#!/usr/bin/env python3
"""Single version source. Stamps VERSION into site files. `--check` fails (exit 1) if anything is stale.
Run by tools/ship.py; CI runs `python3 build/stamp.py --check` via tests/check.py."""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ver = open(f'{ROOT}/VERSION').read().strip()
rel = json.load(open(f'{ROOT}/src/profiles.meta.json'))['released']

def index(s):
    s = re.sub(r'HyperAudio v\d+\.\d+\.\d+(?: \(v\d+ in progress\))?', f'HyperAudio v{ver}', s)
    s = re.sub(r'downloads/v?\d+\.\d+\.\d+/', f'downloads/{ver}/', s)
    s = re.sub(r'RootlessJamesDSP v\d+ Profiles', f'RootlessJamesDSP v{ver.split(".")[0]} Profiles', s)
    s = re.sub(r'(<span class="tag"><i aria-hidden="true"></i>)v\d+\.\d+\.\d+( · Stable release)', rf'\g<1>v{ver}\g<2>', s)
    return re.sub(r'(release <b>)v\d+\.\d+\.\d+(</b>)', rf'\g<1>v{ver}\g<2>', s)

def versions(s):
    d = json.loads(s); found = False
    for e in d:
        if e['v'] == f'v{ver}':
            found = True; e['status'] = 'current'; e['date'] = rel; e['dl'] = f'downloads/{ver}/SHA256SUMS.txt'
        elif e.get('status') in ('current', 'in progress'):
            e['status'] = 'previous'
    if not found: d.insert(0, dict(v=f'v{ver}', date=rel, status='current', notes=['See docs/CHANGELOG.md'], dl=f'downloads/{ver}/SHA256SUMS.txt'))
    for e in d:
        if e.get('dl') and not os.path.isdir(f"{ROOT}/releases/{e['dl'].split('/')[1]}"): e.pop('dl')
    cur = d[0]
    if cur['v'] == f'v{ver}' and cur.get('notes') == ['See docs/CHANGELOG.md']:
        m = re.search(r'^## v' + re.escape(ver) + r'\b(.*?)(?=^## |\Z)', open(f'{ROOT}/docs/CHANGELOG.md', encoding='utf-8').read(), re.S | re.M)
        b = [l[2:].strip().replace('`', '') for l in (m[1] if m else '').splitlines() if l.startswith('- ')][:4]
        if b: cur['notes'] = b
    return json.dumps(d, indent=1, ensure_ascii=False) + '\n'

from siteconfig import REPO, OWNER_SITE
def nav(s):
    s = re.sub(r'(var GH = ")[^"]*(")', lambda m: m[1] + REPO + m[2], s)
    return re.sub(r'(<p class="sf-l"><a href=")[^"]*(")', lambda m: m[1] + OWNER_SITE + m[2], s)

import hashlib, posixpath
PAGES = ['index.html', 'compare.html', 'finder.html', 'archive.html', 'changelog.html', 'docs/index.html']
EXTRA = ['data/evidence.json', 'data/profiles.json', 'data/versions.json', 'data/choose.json', 'manifest.webmanifest']
ASSET = ('.css', '.js', '.woff2', '.svg', '.webmanifest')
def shell():
    S = f'{ROOT}/site'; out = set(EXTRA)
    def add(base, u):
        u = u.split('?')[0].split('#')[0]
        if not u or re.match(r'^(https?:|mailto:|tel:|data:|javascript:|/)', u): return
        q = posixpath.normpath(posixpath.join(posixpath.dirname(base), u))
        if q.startswith('..') or q.startswith('downloads/') or not q.endswith(ASSET): return
        if os.path.isfile(f'{S}/{q}'): out.add(q)
    for pg in PAGES:
        if not os.path.exists(f'{S}/{pg}'): continue
        out.add(pg)
        for u in re.findall(r'(?:href|src)="([^"]+)"', open(f'{S}/{pg}', encoding='utf-8').read()): add(pg, u)
    for f in list(out):
        if f.endswith('.css'):
            for u in re.findall(r'url\(\s*["\']?([^)"\']+)', open(f'{S}/{f}', encoding='utf-8').read()): add(f, u)
    return ['./'] + sorted(out)
def sw(s):
    sh = shell(); h = hashlib.sha256()
    for f in sh[1:]:
        if os.path.exists(f'{ROOT}/site/{f}'): h.update(open(f'{ROOT}/site/{f}', 'rb').read())
    s = re.sub(r"^const VERSION = .*$", f"const VERSION = '{ver}', CACHE = 'hyperaudio-' + VERSION + '-{h.hexdigest()[:8]}';", s, count=1, flags=re.M)
    return re.sub(r"const SHELL = \[.*?\];", lambda m: 'const SHELL = [' + ', '.join("'%s'" % u for u in sh) + '];', s, count=1, flags=re.S)

def readme(s):
    pj = json.load(open(f'{ROOT}/releases/{ver}/profiles.json')); sz = {'all': pj['all']['bytes']}
    sz.update({q['id']: q['bundle']['bytes'] for q in pj['profiles']})
    acc = json.load(open(f'{ROOT}/releases/{ver}/acceptance.json'))['results']; c = {}
    for v in acc.values():
        for x in v: c[x['status']] = c.get(x['status'], 0) + 1
    n = len(next(iter(acc.values())))
    s = re.sub(r'VERSION-\d+\.\d+\.\d+-', f'VERSION-{ver}-', s)
    s = re.sub(r'alt="Version \d+\.\d+\.\d+"', f'alt="Version {ver}"', s)
    s = re.sub(r'releases/\d+\.\d+\.\d+/', f'releases/{ver}/', s)
    s = re.sub(r'HyperAudio_\d+\.\d+\.\d+_', f'HyperAudio_{ver}_', s)
    s = re.sub(r'sha256sum -c \d+\.\d+\.\d+/', f'sha256sum -c {ver}/', s)
    s = re.sub(r'(HyperAudio_[\d.]+_([\w-]+)\.zip\)) \| [\d.]+ KB \|', lambda m: f'{m[1]} | {sz[m[2]] / 1024:.1f} KB |' if m[2] in sz else m[0], s)
    line = f"**Offline, automated.** {n} checks on each of {len(acc)} builds in [`acceptance.json`](releases/{ver}/acceptance.json): {c.get('pass', 0)} pass, {c.get('warn', 0)} warn, {c.get('not_run', 0)} not run (`cpu`)."
    s = re.sub(r'\*\*Offline, automated\.\*\* [^\n]*', lambda m: line, s)
    ds = sorted((d for d in os.listdir(f'{ROOT}/releases') if os.path.isfile(f'{ROOT}/releases/{d}/SHA256SUMS.txt')), key=lambda x: tuple(int(i) for i in x.split('.')), reverse=True)
    return re.sub(r'(Frozen, versioned releases with checksums \()[^)]*(\))', lambda m: m[1] + ', '.join(ds) + m[2], s)

T = {'site/index.html': index, 'site/data/versions.json': versions, 'site/sw.js': sw, 'site/assets/js/nav.js': nav, 'README.md': readme}
check = '--check' in sys.argv; bad = []
for p, f in T.items():
    fp = f'{ROOT}/{p}'
    if not os.path.exists(fp): continue
    old = open(fp, encoding='utf-8').read(); new = f(old)
    if new != old:
        bad.append(p)
        if not check: open(fp, 'w', encoding='utf-8').write(new)
if check: print('\n'.join(f'STALE version text: {p} (run python3 build/stamp.py)' for p in bad) or 'version stamps ok'); sys.exit(1 if bad else 0)
print('stamped', ', '.join(bad) or 'nothing to change', f'-> v{ver}')
