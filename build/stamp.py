#!/usr/bin/env python3
"""Single version source. Stamps VERSION into site files. `--check` fails (exit 1) if anything is stale.
Run automatically by build/build.py; CI runs `python3 build/stamp.py --check` via tests/check.py."""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ver = open(f'{ROOT}/VERSION').read().strip()
rel = json.load(open(f'{ROOT}/src/profiles.meta.json'))['released']

def index(s):
    s = re.sub(r'HyperAudio v\d+\.\d+\.\d+(?: \(v\d+ in progress\))?', f'HyperAudio v{ver}', s)
    s = re.sub(r'downloads/v?\d+\.\d+\.\d+/', f'downloads/{ver}/', s)
    s = re.sub(r'RootlessJamesDSP v\d+ Profiles', f'RootlessJamesDSP v{ver.split(".")[0]} Profiles', s)
    return re.sub(r'(release <b>)v\d+\.\d+\.\d+(</b>)', rf'\g<1>v{ver}\g<2>', s)

def versions(s):
    d = json.loads(s); found = False
    for e in d:
        if e['v'] == f'v{ver}':
            found = True; e['status'] = 'current'; e['date'] = rel; e['dl'] = f'downloads/{ver}/SHA256SUMS.txt'
        elif e.get('status') in ('current', 'in progress'):
            e['status'] = 'previous'
    if not found: d.insert(0, dict(v=f'v{ver}', date=rel, status='current', notes=['See docs/CHANGELOG.md'], dl=f'downloads/{ver}/SHA256SUMS.txt'))
    return json.dumps(d, indent=1, ensure_ascii=False) + '\n'

def sw(s): return re.sub(r"(const VERSION = ')[^']*(')", rf'\g<1>{ver}\g<2>', s)

T = {'site/index.html': index, 'site/data/versions.json': versions, 'site/sw.js': sw}
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
