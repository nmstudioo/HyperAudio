#!/usr/bin/env python3
"""Run from repo root:  python3 nav-patch/apply_nav.py   (idempotent)"""
import os, re, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.getcwd(); S = f'{ROOT}/site'
assert os.path.isdir(S), 'run from the repo root (the folder that contains site/)'
rd = lambda p: open(p, encoding='utf-8').read()
def wr(p, t): open(p, 'w', encoding='utf-8').write(t)
shutil.copy(f'{HERE}/nav.js', f'{S}/assets/js/nav.js'); shutil.copy(f'{HERE}/nav.css', f'{S}/assets/css/nav.css')
shutil.copy(f'{HERE}/overflow.py', f'{ROOT}/tests/overflow.py')
CSS = '<link rel="stylesheet" href="assets/css/nav.css">'; JS = '<script src="assets/js/nav.js"></script>'
def sub(t, pat, rep, label, flags=re.S):
    n, c = re.subn(pat, rep, t, count=1, flags=flags)
    if c == 0: print('  (skip, not found)', label)
    return n
# index.html
t = rd(f'{S}/index.html')
if JS not in t:
    t = sub(t, r'<header class="top">.*?</header>\s*', '', 'header.top')
    t = sub(t, r'<footer class="ft">.*?</footer>\s*', '', 'footer.ft')
    t = sub(t, r'<nav class="tabbar".*?</nav>\s*', '', 'tabbar')
    t = sub(t, r'(<link rel="stylesheet" href="assets/css/site.css">)', r'\1\n' + CSS, 'css link')
    t = sub(t, r'(<script src="assets/js/app.js"></script>)', JS + r'\n\1', 'js link')
    wr(f'{S}/index.html', t)
# secondary pages
for pg in ('compare', 'finder', 'archive', 'changelog'):
    f = f'{S}/{pg}.html'; t = rd(f)
    if JS in t: continue
    t = sub(t, r'<main class="pg">\s*<a class="brand".*?</a>\s*<nav class="pnav".*?</nav>\s*', '<main class="pg" id="main">', pg + ' chrome')
    t = sub(t, r'(<link rel="stylesheet" href="assets/css/site.css">)', r'\1' + CSS, pg + ' css')
    t = t.replace('</main></body>', '</main>' + JS + '</body>')
    wr(f, t)
# app.js
f = f'{S}/assets/js/app.js'; t = rd(f)
t = sub(t, r"/\* -+ theme -+ \*/\n\(function\(\)\{const th=\$\('#themeBtn'\).*?sync\(\)\}\)\(\);\n", '', 'theme IIFE')
t = sub(t, r"\$\('#tabbar'\)\.addEventListener\('click'.*?\}\);\n", '', 'tabbar handler')
t = t.replace("$('#hdrProfile span').textContent=p.name;", "document.querySelectorAll('.n-chip-t').forEach(n=>{n.textContent=p.name});")
wr(f, t)
# tests/check.py
f = f'{ROOT}/tests/check.py'; t = rd(f)
if 'nav.js' not in t:
    add = '''# 5 shared chrome: every page loads nav.js/nav.css and no page carries its own legacy chrome
for pg in ('index', 'compare', 'finder', 'archive', 'changelog'):
    h = open(f'{ROOT}/site/{pg}.html', encoding='utf-8').read()
    need('assets/js/nav.js' in h and 'assets/css/nav.css' in h, f'{pg}.html: nav.js/nav.css missing')
    for bad in ('class="pnav"', 'class="tabbar"', '<header class="top">', 'class="ft"'):
        need(bad not in h, f'{pg}.html: legacy chrome {bad}')
'''
    t = t.replace("print('\\n'.join('FAIL '", add + "print('\\n'.join('FAIL '", 1); wr(f, t)
# CI
f = f'{ROOT}/.github/workflows/ci.yml'; t = rd(f)
if 'overflow.py' not in t:
    t = t.replace('      - name: Build current release', '''      - name: Layout gate (no horizontal overflow, nav a11y)
        run: |
          pip install playwright
          playwright install --with-deps chromium
          python3 tests/overflow.py
      - name: Build current release''', 1); wr(f, t)
print('done. Next: python3 tests/check.py')
