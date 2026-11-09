#!/usr/bin/env python3
"""WCAG 2.2 check of the v9 OKLCH tokens: text 4.5:1, control borders 3:1."""
import math, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = open(f'{ROOT}/site/assets/css/base.css', encoding='utf-8').read()
blk = S[S.index('/* == v9 theme'):S.index('/* == /v9 theme')]
tok = {n: [tuple(map(float, x.split())) for x in (a, b)] for n, a, b in
       re.findall(r'--([\w-]+):\s*light-dark\(\s*oklch\(([^)]*)\)\s*,\s*oklch\(([^)]*)\)\s*\)', blk)}
def Y(t, i):
    L, C, h = tok[t][i]; a = C * math.cos(math.radians(h)); b = C * math.sin(math.radians(h))
    l, m, s = (L + .3963377774 * a + .2158037573 * b) ** 3, (L - .1055613458 * a - .0638541728 * b) ** 3, (L - .0894841775 * a - 1.291485548 * b) ** 3
    r, g, bl = (max(0, min(1, v)) for v in (4.0767416621 * l - 3.3077115913 * m + .2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - .3413193965 * s, -.0041960863 * l - .7034186147 * m + 1.707614701 * s))
    return .2126 * r + .7152 * g + .0722 * bl
def cr(a, b, i):
    hi, lo = sorted((Y(a, i), Y(b, i)), reverse=True); return (hi + .05) / (lo + .05)
BG = ('bg', 'surface', 'elev', 'deep')
pairs = [(f, b, 4.5) for f in ('tx', 'tx2', 'mut', 'acc', 'err', 'ok', 'warn', 'info') for b in BG]
pairs += [('ctl', b, 3.0) for b in BG] + [('on-acc', 'acc', 4.5)]
bad, n = [], 0
for i, th in enumerate(('light', 'dark')):
    for f, b, need in pairs:
        if f not in tok or b not in tok: bad.append(f'missing token {f}/{b}'); continue
        n += 1; r = cr(f, b, i)
        if r < need: bad.append(f'{th}: {f} on {b} = {r:.2f} (need {need})')
print('\n'.join('FAIL ' + e for e in bad) or f'contrast ok: {n} pairs'); sys.exit(1 if bad else 0)
