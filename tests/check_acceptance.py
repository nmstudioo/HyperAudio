#!/usr/bin/env python3
"""Validate an acceptance.json, fresh or restored from cache. Usage: check_acceptance.py PATH"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQ = ('vdc.banks', 'vdc.sections', 'vdc.finite', 'irs.valid', 'irs.peak_matches_meta', 'eel.lint',
       'response.correction_match', 'irs.peak_limit', 'irs.l1', 'irs.tail', 'vdc.pole_radius',
       'eel.compile', 'limiter.ceiling', 'limiter.true_peak', 'tail', 'nan_soak')
d = json.load(open(sys.argv[1]))
ver = open(f'{ROOT}/VERSION').read().strip()
ids = [p['id'] for p in json.load(open(f'{ROOT}/src/profiles.meta.json'))['profiles']]
errs = []
if d.get('version') != ver: errs.append(f'version {d.get("version")} != VERSION {ver}')
res = d.get('results', {})
if sorted(res) != sorted(ids): errs.append(f'profiles {sorted(res)} != {sorted(ids)}')
for pid in ids:
    cs = {c['check']: c for c in res.get(pid, [])}
    for n in REQ:
        if n not in cs: errs.append(f'{pid}: missing {n}')
        elif cs[n]['status'] != 'pass': errs.append(f'{pid}: {n} is {cs[n]["status"]}')
    for c in res.get(pid, []):
        if c['status'] == 'fail' or (c['status'] == 'not_run' and c['check'] != 'cpu'):
            errs.append(f'{pid}: {c["check"]} is {c["status"]}')
print('\n'.join(sorted(set(errs))) or f'acceptance ok: {len(ids)} profiles, version {ver}')
sys.exit(1 if errs else 0)
