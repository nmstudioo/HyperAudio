#!/usr/bin/env python3
"""Refit each VDC's 44.1 kHz bank so its response matches the same VDC's 48 kHz bank.
Usage: python3 src/dsp/refit44.py [OUT_DIR]   (default candidates/v6). Inputs are never modified."""
import json, os, re, sys, numpy as np
from scipy.optimize import least_squares
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
out = sys.argv[1] if len(sys.argv) > 1 else f'{ROOT}/candidates/v6'
F = np.geomspace(20, 20000, 600)
def H(c, fs, f=F):
    w = np.exp(-1j*2*np.pi*f/fs); h = np.ones_like(w)
    for i in range(0, len(c), 5):
        b0, b1, b2, a1, a2 = c[i:i+5]; h = h*(b0+b1*w+b2*w**2)/(1-a1*w-a2*w**2)
    return 20*np.log10(np.abs(h)+1e-12)
def to_p(c):
    p = []
    for i in range(0, len(c), 5):
        b0, b1, b2, a1, a2 = c[i:i+5]; r = np.sqrt(max(-a2, 1e-6)); p += [b0, b1, b2, min(r, .9995), np.arccos(np.clip(a1/(2*r), -1, 1))]
    return np.array(p)
def to_c(p):
    c = []
    for i in range(0, len(p), 5):
        b0, b1, b2, r, t = p[i:i+5]; c += [b0, b1, b2, 2*r*np.cos(t), -r*r]
    return np.array(c)
meta = json.load(open(f'{ROOT}/src/profiles.meta.json')); rows = []
for pr in meta['profiles']:
    fn = [n for n in pr['file_order'] if n.endswith('.vdc')][0]; src = f'{ROOT}/src/profiles/{pr["id"]}/{fn}'
    txt = open(src, encoding='ascii').read(); b = {int(m[1]): np.array([float(x) for x in m[2].split(',') if x]) for m in re.finditer(r'SR_(\d+):([^\n]*)', txt)}
    tgt = H(b[48000], 48000); before = np.abs(H(b[44100], 44100) - tgt).max()
    p0 = to_p(b[44100]); n = len(p0)
    lo = np.tile([-8, -8, -8, 0.0, 0.0], n//5); hi = np.tile([8, 8, 8, 0.9995, np.pi], n//5)
    best = None
    for s in range(6):  # multi-start; start 0 is the existing bank
        x0 = p0 if s == 0 else np.clip(p0*(1+0.02*np.random.default_rng(s).standard_normal(n)), lo, hi)
        r = least_squares(lambda p: H(to_c(p), 44100) - tgt, x0, bounds=(lo, hi), method='trf', max_nfev=400)
        if best is None or r.cost < best.cost: best = r
    c = to_c(best.x); after = np.abs(H(c, 44100) - tgt).max()
    stable = all(best.x[i+3] < 1 for i in range(0, n, 5))
    ok = after < before and stable and np.isfinite(c).all()
    rows.append((pr['id'], before, after if ok else before, ok, max(best.x[3::5])))
    if ok and before > 0.3:  # only touch banks that were off by more than 0.3 dB
        line = 'SR_44100:' + ','.join('%.9f' % v for v in c)
        os.makedirs(f'{out}/{pr["id"]}', exist_ok=True)
        open(f'{out}/{pr["id"]}/{fn}', 'w', encoding='ascii').write(re.sub(r'SR_44100:[^\n]*', line, txt))
print('| profile | 44.1 vs 48 max err before (dB) | after (dB) | max pole radius | written |\n|---|---|---|---|---|')
for i, b_, a_, ok, pr_ in rows: print(f'| {i} | {b_:.2f} | {a_:.2f} | {pr_:.4f} | {"yes" if ok and b_ > .3 else "no (already within 0.3 dB)" if b_ <= .3 else "no (fit not better)"} |')
