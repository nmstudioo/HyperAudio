#!/usr/bin/env python3
"""Rebuild the v5 VDC/IRS files with build/v7/generator and compare them with the frozen releases/5.0.0 files.
Float rounding can change with numpy/scipy versions, so the versions are printed. Usage: python3 tests/gen_repro.py"""
import hashlib, os, subprocess, sys, tempfile
import numpy, scipy
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = os.path.join(ROOT, 'build', 'v7', 'generator'); REL = os.path.join(ROOT, 'releases', '5.0.0')
MAP = {'iem_hd': 'iem-hd', 'iem_v10': 'iem-v10', 'iem_v4': 'iem-v4', 'spk_v10': 'spk-v10', 'spk_v8': 'spk-v8', 'spk_v6': 'spk-v6'}
h = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
print('numpy %s scipy %s' % (numpy.__version__, scipy.__version__))
bad = n = 0
with tempfile.TemporaryDirectory() as t:
    r = subprocess.run([sys.executable, os.path.join(G, 'build_v5.py'), t], capture_output=True, text=True, cwd=G)
    if r.returncode: print(r.stdout[-400:], r.stderr[-400:]); sys.exit(2)
    for a, b in MAP.items():
        for fn in sorted(os.listdir(os.path.join(t, a))):
            if not fn.endswith(('.vdc', '.irs')): continue
            ref = os.path.join(REL, b, fn); ok = os.path.exists(ref) and h(ref) == h(os.path.join(t, a, fn)); n += 1; bad += not ok
            if not ok: print('DIFF', b, fn)
print('generator reproduction: %d/%d files identical to releases/5.0.0' % (n - bad, n)); sys.exit(1 if bad else 0)
