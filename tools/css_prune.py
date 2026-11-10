#!/usr/bin/env python3
"""Remove CSS rules whose selectors need a class that no source file mentions. Dry run unless --write."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from csslib import *
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUSPECT = set('t-sun t-moon t-ok good ghost onoff li-on has-view rec-tag chip-live'.split())
SKIPD = {'.git', 'node_modules', 'releases', 'downloads', '__pycache__', 'evidence'}
txt = ''; jstxt = ''
for d, ds, fs in os.walk(ROOT):
    ds[:] = [x for x in ds if x not in SKIPD]
    for f in fs:
        if f.endswith(('.html', '.js', '.py', '.md', '.json', '.yml')):
            try: t = open(os.path.join(d, f), encoding='utf-8').read()
            except Exception: continue
            txt += t + '\n'
            if f.endswith('.js'): jstxt += t + '\n'
tokens = set(re.findall(r'[\w-]+', txt))
prefixes = set(re.findall(r"""([\w-]+-)(?:\$\{|["'`]\s*\+)""", jstxt))
def live(c): return c in tokens or c in SUSPECT or any(c.startswith(p) for p in prefixes)
def is_dead(sel):
    if re.search(r':(not|is|where|has)\(', sel): return False
    cl = re.findall(r'\.(-?[A-Za-z_][\w-]*)', re.sub(r'\[[^\]]*\]', '', sel))
    return any(not live(c) for c in cl)
removed = []
def process(s, a, b):
    rem = []; kept = 0; items = scan(s, a, b)
    for st, en, pre, body in items:
        p = clean(pre)
        if body is None: kept += 1; continue
        if p.startswith('@'):
            if AT_NEST.match(p):
                sub, allrem = process(s, body[0], body[1])
                if allrem: rem.append((st, en)); removed.append('[empty ' + p + ']')
                else: rem += sub; kept += 1
            else: kept += 1
            continue
        sels = split_sel(p)
        if sels and all(is_dead(x) for x in sels): rem.append((st, en)); removed.append(' '.join(p.split()))
        else: kept += 1
    return rem, (kept == 0 and len(items) > 0)
write = '--write' in sys.argv
for f in ('base', 'nav', 'docs'):
    p = f'{ROOT}/site/assets/css/{f}.css'; s = open(p, encoding='utf-8').read(); assert balanced(s)
    removed.clear(); rem, _ = process(s, 0, len(s)); n = s
    for a, b in sorted(rem, reverse=True): n = n[:a] + n[b:]
    n = re.sub(r'\n{3,}', '\n\n', n); assert balanced(n)
    print(f'{f}.css: {len(removed)} rules removed, {len(s)} -> {len(n)} bytes')
    open(os.path.expanduser(f'~/pruned_{f}.txt'), 'w').write('\n'.join(removed) + '\n')
    if write: open(p, 'w', encoding='utf-8').write(n)
print('written' if write else 'dry run (add --write)')
