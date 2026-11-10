#!/usr/bin/env python3
"""CI scope: which job groups a change needs. Fails safe to everything."""
import os, subprocess
DSP = ('src/profiles', 'releases/', 'VERSION', 'build/build.py', 'build/response.py', 'build/verify.py', 'build/generator/', 'tests/eel/', 'tests/gen_repro.py', 'requirements.txt')
GEN = ('build/generator/', 'tests/gen_repro.py', 'releases/5.0.0/')
SITE = ('site/', 'docs/', 'VERSION', 'build/docs_site.py', 'build/seo.py', 'build/stamp.py', 'build/evidence_data.py', 'tests/overflow.js', 'tests/footer.js', 'tests/links.js', 'tests/a11y.js', 'tests/budget.js', 'tests/ui-behavior.js', 'tests/screenshots.js', 'tests/seo_audit.py')
ALL = ('.github/workflows/ci.yml', 'tools/ci_scope.py', 'package.json', 'package-lock.json')
def changed():
    ev, b = os.environ.get('EVENT', ''), os.environ.get('BEFORE', '')
    if ev == 'pull_request': rng = 'origin/%s...HEAD' % os.environ.get('BASE_REF', 'main')
    elif ev == 'push' and b.strip('0'): rng = b + '..HEAD'
    else: return None
    r = subprocess.run(['git', 'diff', '--name-only', rng], capture_output=True, text=True)
    return r.stdout.split() if r.returncode == 0 else None
f = changed()
if f is None or any(x.startswith(ALL) for x in f): dsp = gen = site = True
else:
    dsp = any(x.startswith(DSP) for x in f); gen = any(x.startswith(GEN) for x in f); site = any(x.startswith(SITE) for x in f)
print('files:', 'ALL (fail-safe)' if f is None else len(f))
out = {'dsp': dsp, 'gen': gen, 'site': site}
for k, v in out.items(): print('%s=%s' % (k, str(v).lower()))
if os.environ.get('GITHUB_OUTPUT'):
    open(os.environ['GITHUB_OUTPUT'], 'a').write(''.join('%s=%s\n' % (k, str(v).lower()) for k, v in out.items()))
