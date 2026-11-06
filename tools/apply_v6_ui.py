#!/usr/bin/env python3
import re, subprocess, sys, os
IDX, CSS = 'site/index.html', 'site/assets/css/site.css'
BEGIN, END = '<!-- v6-evidence:start -->', '<!-- v6-evidence:end -->'
BLOCK = BEGIN + '''
            <div class="v6ev" id="v6-evidence">
              <h3>v6 backend evidence</h3>
              <p>The v6 acceptance suite and EEL2 runtime tests are included in the repository.</p>
              <ul>
                <li><a href="docs/EVIDENCE.html">Method &amp; evidence</a></li>
                <li><a href="docs/OPEN.html">Open issues</a></li>
                <li><a href="docs/LIMITS.html">Known limits</a></li>
                <li><a href="docs/REPRODUCING.html">Reproduce the build</a></li>
                <li><a href="docs/evidence/acceptance-src-v5.0.0.json">Acceptance test data (JSON)</a></li>
              </ul>
            </div>
            ''' + END
CSS_ADD = '''
/* v6-evidence */
.v6ev{margin-top:20px;padding:16px 18px;border:1px solid var(--bd);border-radius:16px}
.v6ev h3{margin:0 0 6px;font:700 17px var(--sans)}.v6ev p{margin:0 0 10px;color:var(--tx2);font-size:14px}
.v6ev ul{margin:0;padding-left:18px;display:grid;gap:6px}.v6ev a{color:var(--acc);font-weight:600}
'''
s = open(IDX, encoding='utf-8').read()
s = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END) + r'\s*', '', s, flags=re.S)
def enclosing(s, pos):
    for m in reversed([m for m in re.finditer(r'<(section|div|article|aside)\b[^>]*>', s[:pos])]):
        tag, depth = m[1], 0
        for t in re.finditer(r'<(/?)%s\b[^>]*>' % tag, s[m.start():]):
            depth += -1 if t[1] else 1
            if depth == 0:
                end = m.start() + t.end(); break
        else: continue
        if end > pos and 'docs/' in s[m.start():end] and 'id="evidence"' not in s[m.start():end] and len(s[m.start():end]) < 6000:
            return m.start(), end
    return None
h = re.search(r'backend\s+evidence', s, re.I)
if h:
    r = enclosing(s, h.start())
    if not r: sys.exit('Found "Backend Evidence" but could not isolate its container; delete that block by hand, then rerun.')
    s = s[:r[0]] + s[r[1]:]; print('removed misplaced block (%d chars)' % (r[1] - r[0]))
m = re.search(r'<section\b[^>]*id="evidence"', s)
if not m: sys.exit('#evidence section not found in ' + IDX)
close = s.index('</section>', m.end())
s = s[:close] + '  ' + BLOCK + '\n          ' + s[close:]
open(IDX, 'w', encoding='utf-8').write(s)
c = open(CSS, encoding='utf-8').read()
if '/* v6-evidence */' not in c: open(CSS, 'a', encoding='utf-8').write(CSS_ADD)
if os.path.exists('build/docs_site.py'): subprocess.run([sys.executable, 'build/docs_site.py'], check=True)
print('ok: evidence block is inside #evidence')
