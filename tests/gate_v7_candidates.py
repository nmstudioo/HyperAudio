#!/usr/bin/env python3
"""Gate every v7 candidate (IRS + VDC + EEL) with tests/gate_candidate.py and verify candidates/v7/SHA256SUMS.
Usage: python3 tests/gate_v7_candidates.py"""
import hashlib, os, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V7 = os.path.join(ROOT, 'candidates', 'v7')

def trios():
    for d, _, fs in sorted(os.walk(V7)):
        k = {e: [f for f in fs if f.endswith(e)] for e in ('.irs', '.vdc', '.eel')}
        if all(len(v) == 1 for v in k.values()):
            yield d, [k[e][0] for e in ('.irs', '.vdc', '.eel')]

def gate(item):
    d, names = item
    with tempfile.TemporaryDirectory() as t:
        for n, e in zip(names, ('.irs', '.vdc', '.eel')): shutil.copy(os.path.join(d, n), os.path.join(t, 'X' + e))
        r = subprocess.run([sys.executable, os.path.join(ROOT, 'tests', 'gate_candidate.py'), os.path.join(t, 'X')], capture_output=True, text=True, cwd=ROOT)
    return os.path.relpath(d, V7), r.returncode == 0, (r.stdout + r.stderr).strip().splitlines()[-1:]

bad = 0
sums = os.path.join(V7, 'SHA256SUMS')
for line in open(sums):
    h, p = line.split(None, 1); p = p.strip().lstrip('*')
    if hashlib.sha256(open(os.path.join(V7, p), 'rb').read()).hexdigest() != h: print('SHA256 MISMATCH', p); bad += 1
items = list(trios())
with ThreadPoolExecutor() as ex:
    for name, ok, last in ex.map(gate, items):
        print('%-4s %-24s %s' % ('PASS' if ok else 'FAIL', name, ' '.join(last))); bad += not ok
print('v7 candidates: %d pairs, %s' % (len(items), 'FAILED' if bad else 'all gates pass (calculated only)')); sys.exit(1 if bad else 0)
