#!/usr/bin/env python3
"""CI gate: hash checks, link checks, JS syntax, v5 parity. Exit 1 on any failure."""
import json, os, re, subprocess, sys, tempfile, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, f'{ROOT}/build')
from verify import sha
err = []
def need(c, m):
    if not c: err.append(m)
cur_v = open(f'{ROOT}/VERSION').read().strip()
subprocess.run([sys.executable, f'{ROOT}/build/build.py', '--publish'], check=True)  # site/downloads is generated, never committed
# 1 release hashes: SHA256SUMS vs files, profiles.json vs files, site copy vs release
for rd in sorted(d for d in glob.glob(f'{ROOT}/releases/*') if os.path.isfile(f'{d}/SHA256SUMS.txt')):
    v = os.path.basename(rd)
    for ln in open(f'{rd}/SHA256SUMS.txt').read().split('\n'):
        if ln:
            h, p = ln.split('  '); f = f'{rd}/{p.split("/", 1)[1]}'
            need(os.path.exists(f) and sha(f) == h, f'{v}: hash mismatch {p}')
    pj = json.load(open(f'{rd}/profiles.json'))
    for p in pj['profiles']:
        for f in p['files'] + [p['bundle']]:
            fp = f'{rd}/' + f['path'].split(v + '/', 1)[1]
            need(os.path.exists(fp) and sha(fp) == f['sha256'] and os.path.getsize(fp) == f['bytes'], f'{v}: profiles.json mismatch {f["name"]}')
cur = open(f'{ROOT}/VERSION').read().strip()
need(json.load(open(f'{ROOT}/site/data/profiles.json'))['version'] == cur, 'site/data/profiles.json version != VERSION')
# 2 rebuild into temp dir; member files must match published release hashes (reproducibility)
if os.environ.get('HA_SKIP_REBUILD') != '1':
    with tempfile.TemporaryDirectory() as t:
        r = subprocess.run([sys.executable, f'{ROOT}/build/build.py', '--out', t + '/r', '--no-runtime'], capture_output=True, text=True)
        need(r.returncode == 0, 'build failed: ' + r.stdout + r.stderr)
        pub = f'{ROOT}/releases/{cur}/SHA256SUMS.txt'
        if os.path.exists(pub): need(sorted(open(pub).read().split('\n')) == sorted(open(t + '/r/SHA256SUMS.txt').read().split('\n')), 'rebuild SHA256SUMS differs from release')
        if os.path.exists(f'{ROOT}/releases/{cur}/FROZEN'): pass
        else: need(all(sha(f) == sha(f.replace(t + '/r', f'{ROOT}/releases/{cur}')) for f in glob.glob(t + '/r/*.zip')), 'rebuilt zips differ from release')
r = subprocess.run([sys.executable, f'{ROOT}/build/stamp.py', '--check'], capture_output=True, text=True); need(r.returncode == 0, r.stdout.strip() or r.stderr[:200])
r = subprocess.run([sys.executable, f'{ROOT}/build/evidence_data.py', '--check'], capture_output=True, text=True); need(r.returncode == 0, r.stdout.strip() or r.stderr[:200])
fz = f'{ROOT}/releases/{cur}/FROZEN'
if os.path.exists(fz) and 'sha256sums' in open(fz).read():
    import hashlib; need(hashlib.sha256(open(f'{ROOT}/releases/{cur}/SHA256SUMS.txt', 'rb').read()).hexdigest() in open(fz).read(), f'{cur}: FROZEN release changed (SHA256SUMS differs from the frozen hash)')
# 3 local links in index.html and CSS/JS references
html = open(f'{ROOT}/site/index.html', encoding='utf-8').read()
for u in re.findall(r'(?:href|src)="([^"#:]+)"', html):
    need(os.path.exists(f'{ROOT}/site/{u.split("?")[0]}'), f'broken link in index.html: {u}')
# 3b docs pages up to date, links resolve, 404 exists
r = subprocess.run([sys.executable, f'{ROOT}/build/docs_site.py', '--check'], capture_output=True, text=True); need(r.returncode == 0, r.stdout.strip() or r.stderr[:200])
r = subprocess.run([sys.executable, f'{ROOT}/build/seo.py', '--check'], capture_output=True, text=True); need(r.returncode == 0, r.stdout.strip() or r.stderr[:200])
r = subprocess.run([sys.executable, f'{ROOT}/tests/seo_audit.py'], capture_output=True, text=True); need(r.returncode == 0, r.stdout.strip()[:300])
r = subprocess.run(['node', f'{ROOT}/tests/links.js'], capture_output=True, text=True); need(r.returncode == 0, r.stdout.strip() or r.stderr[:200])
# 3c service worker precache list must exist on disk
sw = open(f'{ROOT}/site/sw.js', encoding='utf-8').read(); m = re.search(r'const SHELL = \[(.*?)\];', sw, re.S)
for u in re.findall(r"'([^']+)'", m[1] if m else ''): need(os.path.exists(f'{ROOT}/site/{u}') or u == './', f'sw.js SHELL entry missing on disk: {u}')
need(bool(m), 'sw.js SHELL list not found')
need(len(re.findall(r"(?m)^const VERSION =", sw)) == 1, 'sw.js must contain exactly one VERSION declaration')
r = subprocess.run(['node', '--check', f'{ROOT}/site/sw.js'], capture_output=True, text=True)
need(r.returncode == 0, f'sw.js syntax: {r.stderr[:200]}')
# 4 JS syntax
for js in glob.glob(f'{ROOT}/site/assets/js/*.js'):
    r = subprocess.run(['node', '--check', js], capture_output=True, text=True); need(r.returncode == 0, f'JS syntax {js}: {r.stderr[:200]}')
# 5 static site invariants (moved from tests/ui-v7-contract.js)
import math
S = f'{ROOT}/site'; rd = lambda q: open(f'{S}/{q}', encoding='utf-8').read()
FONTS = ['plus-jakarta-sans-latin-400-normal', 'plus-jakarta-sans-latin-600-normal', 'plus-jakarta-sans-latin-800-normal', 'jetbrains-mono-latin-400-normal', 'jetbrains-mono-latin-700-normal']
def fin(v):
    try: return math.isfinite(float(v))
    except (TypeError, ValueError): return False
for n in ('index', 'compare', 'finder', 'archive', 'changelog', '404'):
    s = rd(f'{n}.html')
    need('Content-Security-Policy' in s, f'{n}.html has no CSP meta')
    need(not re.search(r'fonts\.g(oogleapis|static)\.com', s), f'{n}.html loads Google Fonts')
    need('assets/css/fonts.css' in s, f'{n}.html does not load fonts.css')
for f in FONTS:
    need(os.path.exists(f'{S}/assets/fonts/{f}.woff2'), f'font file missing: {f}.woff2')
    need(f in rd('assets/css/fonts.css'), f'fonts.css does not reference {f}')
need('assets/css/fonts.css' in rd('sw.js'), 'sw.js SHELL lacks fonts.css')
pd = json.load(open(f'{S}/data/profiles.json'))
need(len(pd['profiles']) == 6, 'stable profile set changed unexpectedly')
need(all(len(p['files']) == 3 for p in pd['profiles']), 'a profile no longer has its matched three-file set')
need(all(fin(p.get('stats', {}).get(k)) for p in pd['profiles'] for k in ('rms', 'chainMax', 'sections', 'irsPeak')), 'profile metric fields missing or non-finite')
need('Offline + author device test' not in rd('index.html'), 'stale evidence badge on index.html')
need("Tested on the author's phone" not in rd('index.html'), 'unqualified device-test claim on index.html')
need('no acoustic measurement recorded' in rd('assets/js/nav.js').lower(), 'footer evidence copy is not qualified (nav.js)')
print('\n'.join('FAIL ' + e for e in err) or 'all checks passed'); sys.exit(1 if err else 0)
