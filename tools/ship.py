#!/usr/bin/env python3
"""One command: regenerate everything in the right order, then gate. python3 tools/ship.py [--no-check]
Order: evidence data -> docs pages -> formatter -> SEO blocks/sitemap -> version stamps -> gate (repeated once if generators disagree)."""
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def run(*a):
    r = subprocess.run([sys.executable, *a], cwd=ROOT, capture_output=True, text=True); return r.returncode, (r.stdout + r.stderr).strip()
def gen():
    for s in ('build/evidence_data.py', 'build/docs_site.py', 'tools/fmt.py', 'build/seo.py', 'build/stamp.py'):
        c, o = run(s)
        print('%-24s %s' % (s, 'ok' if c == 0 else 'FAILED\n' + o))
        if c: sys.exit(c)
gen()
if '--no-check' in sys.argv: sys.exit(0)
c, o = run('tests/check.py')
if c: print('gate failed once, regenerating and retrying'); gen(); c, o = run('tests/check.py')
print(o); sys.exit(c)
