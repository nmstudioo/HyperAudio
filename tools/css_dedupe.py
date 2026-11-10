#!/usr/bin/env python3
"""Drop declarations that a later identical-selector rule in the same context always overrides. Dry run unless --write."""
import os, re, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from csslib import *
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RISKY = re.compile(r'(dvh|svh|lvh|dvw|env\(|color-mix|clamp\(|min\(|max\(|oklch|oklab|lab\(|lch\(|image-set|subgrid|aspect-ratio|inset|gap|backdrop-filter|scrollbar|accent-color|text-wrap|container|-webkit-|-moz-)')
def collect(s, a, b, ctx, out):
    for st, en, pre, body in scan(s, a, b):
        if body is None: continue
        p = ' '.join(clean(pre).split())
        if p.startswith('@'):
            if AT_NEST.match(p): collect(s, body[0], body[1], ctx + (p,), out)
            continue
        out.append(dict(ctx=ctx, sel=p, st=st, en=en, bs=body[0], be=body[1]))
def parse(s, r):
    ds = []
    for a, b in decls(s, r['bs'], r['be']):
        t = clean(s[a:b]).rstrip(';').strip()
        if ':' not in t: ds.append(dict(a=a, b=b, prop=None)); continue
        pr, v = t.split(':', 1)
        ds.append(dict(a=a, b=b, prop=pr.strip().lower(), val=v.strip(), imp='!important' in v.lower()))
    r['d'] = ds
write = '--write' in sys.argv
for f in ('base', 'nav', 'docs'):
    p = f'{ROOT}/site/assets/css/{f}.css'; s = open(p, encoding='utf-8').read(); assert balanced(s)
    rules = []; collect(s, 0, len(s), (), rules)
    g = defaultdict(list)
    for r in rules: parse(s, r); g[(r['ctx'], r['sel'])].append(r)
    edits = []; nd = 0; nr = 0
    for grp in g.values():
        for i in range(len(grp) - 1):
            drop = []
            for d in grp[i]['d']:
                if d['prop'] is None: continue
                for j in range(i + 1, len(grp)):
                    if any(e['prop'] == d['prop'] and (e['imp'] or not d['imp']) and not RISKY.search(e['prop'] + ':' + e['val']) for e in grp[j]['d'] if e['prop']):
                        drop.append(d); break
            if not drop: continue
            if len(drop) == len(grp[i]['d']): edits.append((grp[i]['st'], grp[i]['en'])); nr += 1
            else: edits += [(d['a'], d['b']) for d in drop]; nd += len(drop)
    n = s
    for a, b in sorted(edits, reverse=True): n = n[:a] + n[b:]
    n = re.sub(r'\n{3,}', '\n\n', n); assert balanced(n)
    print(f'{f}.css: {nd} declarations and {nr} whole rules dropped, {len(s)} -> {len(n)} bytes')
    if write: open(p, 'w', encoding='utf-8').write(n)
print('written' if write else 'dry run (add --write)')
