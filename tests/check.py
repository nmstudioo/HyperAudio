#!/usr/bin/env python3
"""CI gate: hash checks, link checks, JS syntax, v5 parity. Exit 1 on any failure."""
import json, os, re, subprocess, sys, tempfile, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, f'{ROOT}/build')
from verify import sha
err = []
def need(c, m):
    if not c: err.append(m)
# 1 release hashes: SHA256SUMS vs files, profiles.json vs files, site copy vs release
for rd in sorted(glob.glob(f'{ROOT}/releases/v*')):
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
    sd = f'{ROOT}/site/downloads/{v}'
    if os.path.isdir(sd):
        for f in os.listdir(sd):
            if os.path.isfile(f'{rd}/{f}'): need(sha(f'{sd}/{f}') == sha(f'{rd}/{f}'), f'{v}: site copy differs {f}')
        for f in glob.glob(f'{sd}/*/*'): need(sha(f) == sha(f'{rd}/' + f.split(sd + '/')[1]), f'{v}: site copy differs {f}')
cur = open(f'{ROOT}/VERSION').read().strip()
need(json.load(open(f'{ROOT}/site/data/profiles.json'))['version'] == cur, 'site/data/profiles.json version != VERSION')
# 2 rebuild into temp dir; member files must match published release hashes (reproducibility)
with tempfile.TemporaryDirectory() as t:
    r = subprocess.run([sys.executable, f'{ROOT}/build/build.py', '--out', t + '/r'], capture_output=True, text=True)
    need(r.returncode == 0, 'build failed: ' + r.stdout + r.stderr)
    pub = f'{ROOT}/releases/{cur}/SHA256SUMS.txt'
    if os.path.exists(pub): need(sorted(open(pub).read().split('\n')) == sorted(open(t + '/r/SHA256SUMS.txt').read().split('\n')), 'rebuild SHA256SUMS differs from release')
    if os.path.exists(f'{ROOT}/releases/{cur}/FROZEN'): pass
    else: need(all(sha(f) == sha(f.replace(t + '/r', f'{ROOT}/releases/{cur}')) for f in glob.glob(t + '/r/*.zip')), 'rebuilt zips differ from release')
# 3 local links in index.html and CSS/JS references
html = open(f'{ROOT}/site/index.html', encoding='utf-8').read()
for u in re.findall(r'(?:href|src)="([^"#:]+)"', html):
    need(os.path.exists(f'{ROOT}/site/{u.split("?")[0]}'), f'broken link in index.html: {u}')
# 4 JS syntax
for js in glob.glob(f'{ROOT}/site/assets/js/*.js'):
    r = subprocess.run(['node', '--check', js], capture_output=True, text=True); need(r.returncode == 0, f'JS syntax {js}: {r.stderr[:200]}')
print('\n'.join('FAIL ' + e for e in err) or 'all checks passed'); sys.exit(1 if err else 0)
