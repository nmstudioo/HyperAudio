#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
from ci_scope import classify
ALL3 = {'dsp': True, 'gen': True, 'site': True}
def t(files, dsp, gen, site, why):
    got = classify(files)
    assert got == {'dsp': dsp, 'gen': gen, 'site': site}, f'{why}: {files} -> {got}'
t(None, 1, 1, 1, 'git diff failed or unknown event fails safe')
t(['src/profiles/iem-hd/EDX_HD.eel'], 1, 0, 0, 'EEL change')
t(['src/profiles/spk-v8/a.vdc', 'src/profiles/spk-v8/a.irs'], 1, 0, 0, 'VDC and IRS')
t(['src/profiles.meta.json'], 1, 0, 0, 'profile metadata')
t(['build/verify.py'], 1, 0, 0, 'verifier')
t(['build/derive_stats.py'], 1, 0, 0, 'derive_stats feeds acceptance')
t(['VERSION'], 1, 0, 1, 'version bump')
t(['tests/check_acceptance.py'], 1, 0, 0, 'acceptance validator')
t(['build/generator/build_v5.py'], 1, 1, 0, 'generator')
t(['releases/5.0.0/SHA256SUMS.txt'], 1, 1, 0, 'frozen v5 release')
t(['releases/7.0.0/SHA256SUMS.txt'], 1, 0, 0, 'current release files')
t(['docs/CHANGELOG.md'], 0, 0, 1, 'docs only')
t(['site/assets/css/base.css'], 0, 0, 1, 'site only')
t(['README.md'], 0, 0, 0, 'root readme needs no jobs')
t(['.github/workflows/ci.yml'], 1, 1, 1, 'ci.yml')
t(['.github/workflows/release.yml'], 1, 1, 1, 'any workflow')
t(['package-lock.json'], 1, 1, 1, 'browser tool lockfile')
t(['tools/ci_scope.py', 'README.md'], 1, 1, 1, 'scope script itself')
t([], 0, 0, 0, 'empty diff')
print('ci_scope tests ok')
