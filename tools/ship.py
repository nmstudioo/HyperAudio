#!/usr/bin/env python3
"""The only orchestrator.  python3 tools/ship.py [--no-check] | --release
Default: regenerate every derived file in order, then run the gate once.
--release: full build with runtime acceptance, regenerate, pass the gate, then freeze releases/<VERSION>/."""
import datetime, hashlib, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def run(*a):
    r = subprocess.run([sys.executable, *a], cwd=ROOT, capture_output=True, text=True); return r.returncode, (r.stdout + r.stderr).strip()
def gen():
    c, o = run('build/build.py', '--publish')
    print('%-24s %s' % ('build/build.py --publish', 'ok' if c == 0 else 'FAILED\n' + o))
    if c: sys.exit(c)
    for s in ('build/evidence_data.py', 'build/docs_site.py', 'tools/fmt.py', 'build/seo.py', 'build/stamp.py'):
        c, o = run(s)
        print('%-24s %s' % (s, 'ok' if c == 0 else 'FAILED\n' + o))
        if c: sys.exit(c)
def freeze():
    v = open(f'{ROOT}/VERSION').read().strip(); d = f'{ROOT}/releases/{v}'
    h = hashlib.sha256(open(f'{d}/SHA256SUMS.txt', 'rb').read()).hexdigest()
    open(f'{d}/FROZEN', 'w').write(f'frozen {datetime.date.today()}\nsha256sums {h}\n'); print('frozen', v, h)
def gate():
    c, o = run('tests/check.py')
    print(o or ('gate passed' if c == 0 else 'gate failed'))
    return c
if '--release' in sys.argv:
    c, o = run('build/build.py'); print(o)
    if c: sys.exit(c)
    gen()
    if gate(): sys.exit(1)
    freeze()
    sys.exit(0)
gen()
if '--no-check' in sys.argv: sys.exit(0)
sys.exit(gate())
