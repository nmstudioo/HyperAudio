#!/usr/bin/env python3
"""Record a user-reported device test: appends to docs/evidence/device-tests.json and sets the build's meta evidence.
  python3 tools/record_device.py BUILD pass|fail|untested "device" "notes" [--test "listening pass"]
Evidence stays 'reported' (author's own test); nothing here is an instrument measurement."""
import argparse, datetime, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser(); ap.add_argument('build'); ap.add_argument('result', choices=['pass', 'fail', 'untested']); ap.add_argument('device'); ap.add_argument('notes'); ap.add_argument('--test', default='listening pass'); a = ap.parse_args()
mp = f'{ROOT}/src/profiles.meta.json'; meta = json.load(open(mp, encoding='utf-8')); ver = meta['version']
dp = f'{ROOT}/docs/evidence/device-tests.json'; d = json.load(open(dp, encoding='utf-8'))
d['entries'] = [e for e in d['entries'] if not (e['release'] == ver and e['build'] == a.build and e['test'] == a.test)]
d['entries'].append(dict(release=ver, build=a.build, device=a.device, date=datetime.date.today().isoformat(), test=a.test, result=a.result, notes=a.notes))
open(dp, 'w', encoding='utf-8').write(json.dumps(d, indent=1, ensure_ascii=False) + '\n')
for p in meta['profiles']:
    if p['id'] == a.build: p['evidence'] = {'offline': True, 'device': 'reported' if a.result != 'untested' else 'untested', 'deviceNote': a.notes}
open(mp, 'w', encoding='utf-8').write(json.dumps(meta, separators=(',', ':')))
print('recorded', a.build, a.result)
