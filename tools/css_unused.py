#!/usr/bin/env python3
"""Static report of CSS class selectors that no HTML, JS or build script mentions. Report only; it never edits CSS.
Classes assembled at runtime (for example "dot " + status) can look unused, so review before deleting."""
import glob, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = ''
for pat in ('site/*.html', 'site/docs/*.html', 'site/assets/js/*.js', 'build/*.py'):
    for f in glob.glob(f'{ROOT}/{pat}'): src += open(f, encoding='utf-8', errors='ignore').read() + '\n'
for css in sorted(glob.glob(f'{ROOT}/site/assets/css/*.css')):
    t = re.sub(r'/\*.*?\*/', '', open(css, encoding='utf-8').read(), flags=re.S)
    cls = set(re.findall(r'\.([a-zA-Z_][\w-]*)', t))
    dead = sorted(c for c in cls if not re.search(r'(?<![\w-])' + re.escape(c) + r'(?![\w-])', src))
    print(f'{os.path.basename(css):12} {os.path.getsize(css)//1024:4} KB  {len(cls):4} classes  {len(dead):4} not found in html/js/build')
    if '--list' in __import__('sys').argv: print('   ' + ' '.join(dead))
