#!/usr/bin/env python3
"""Builds site/data/evidence.json from releases/<VERSION>/acceptance.json + docs/evidence/device-tests.json.
`--check` fails if the committed file is stale. Run by build/build.py (publish step) and tests/check.py."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ver = open(f'{ROOT}/VERSION').read().strip()
GROUPS = [
 ('files', 'Files valid', 'IRS format and peak, VDC banks and sections, script lint', ['irs.valid', 'irs.peak_matches_meta', 'vdc.banks', 'vdc.sections', 'vdc.finite', 'eel.lint', 'irs.peak_limit', 'irs.l1', 'irs.tail']),
 ('response', 'Response matches curves', 'VDC x IRS reproduces the stored correction (self-consistency, not a measurement)', ['response.correction_match', 'response.gain1k', 'response.chain_max', 'response.error_vs_target']),
 ('stable', 'VDC filters stable', 'All poles inside the unit circle', ['vdc.stable', 'vdc.pole_radius']),
 ('compile', 'Script compiles', 'Runs on eel2py, a subset interpreter, not the WDL runtime', ['eel.compile']),
 ('limiter', 'Limiter holds the ceiling', 'Sample peak, true peak, hard-clamp engagement', ['limiter.ceiling', 'limiter.clamp_engaged', 'limiter.true_peak']),
 ('soak', 'Tail and NaN soak', 'Silence after a burst, no non-finite output', ['tail', 'nan_soak']),
 ('banks', '44.1 and 48 kHz banks agree', 'Within 0.3 dB over 20 Hz to 20 kHz', ['vdc.sr_consistency']),
 ('cpu', 'CPU load', 'Needs an on-device measurement', ['cpu']),
]
RANK = {'fail': 4, 'warn': 3, 'not_run': 2, 'pass': 1}
def build():
    acc = json.load(open(f'{ROOT}/releases/{ver}/acceptance.json'))['results']
    meta = json.load(open(f'{ROOT}/src/profiles.meta.json'))['profiles']
    ids = [p['id'] for p in meta]; dev = json.load(open(f'{ROOT}/docs/evidence/device-tests.json'))['entries']
    rows = []; tot = {'pass': 0, 'warn': 0, 'fail': 0, 'not_run': 0}
    for pid in ids:
        for c in acc[pid]: tot[c['status']] = tot.get(c['status'], 0) + 1
    for gid, label, sub, checks in GROUPS:
        cells = {}
        for pid in ids:
            rs = [c for c in acc[pid] if c['check'] in checks]
            st = max((c['status'] for c in rs), key=lambda s: RANK[s]) if rs else 'not_run'
            bad = [c for c in rs if c['status'] != 'pass']
            cells[pid] = dict(status=st, detail='; '.join(f"{c['check']}: {c['detail']}" for c in (bad or rs))[:420])
        rows.append(dict(id=gid, label=label, sub=sub, cells=cells))
    d = {}
    for e in dev: d[e['build']] = dict(result=e['result'], device=e['device'], date=e['date'], notes=e['notes'])
    rows.append(dict(id='device', label='Device listening test', sub='Recorded per build by the author', cells={pid: dict(status={'pass': 'pass', 'fail': 'fail'}.get(d.get(pid, {}).get('result'), 'untested'), detail=d.get(pid, {}).get('notes', 'No record')) for pid in ids}))
    return dict(version=ver, totals=tot, profiles=ids, rows=rows, tiers=dict(device_recorded=sum(1 for v in d.values() if v['result'] in ('pass', 'fail')), device_total=len(ids), measured=False))
if __name__ == '__main__':
    out = json.dumps(build(), indent=1, ensure_ascii=False) + '\n'; fp = f'{ROOT}/site/data/evidence.json'
    if '--check' in sys.argv:
        ok = os.path.exists(fp) and open(fp, encoding='utf-8').read() == out
        print('evidence.json up to date' if ok else 'STALE site/data/evidence.json (run python3 build/evidence_data.py)'); sys.exit(0 if ok else 1)
    open(fp, 'w', encoding='utf-8').write(out); print('wrote site/data/evidence.json', build()['totals'])
