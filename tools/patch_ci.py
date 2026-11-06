#!/usr/bin/env python3
"""Idempotent: add dependency caching + run cancellation to .github/workflows/ci.yml, drop repeated identical check steps."""
import re, sys
P = '.github/workflows/ci.yml'
s = open(P).read(); o = s; log = []
CACHE = """      - name: Cache pip, npm and Playwright
        uses: actions/cache@v4
        with:
          path: |
            ~/.cache/pip
            ~/.npm
            ~/.cache/ms-playwright
          key: deps-${{ runner.os }}-${{ hashFiles('.github/workflows/ci.yml') }}
          restore-keys: deps-${{ runner.os }}-
"""
if 'actions/cache@' not in s:
    s, k = re.subn(r'(      - uses: actions/checkout@[^\n]*\n)', lambda m: m[1] + CACHE, s, count=1); log += ['cache step'] * k
if 'concurrency:' not in s:
    s, k = re.subn(r'\njobs:', '\nconcurrency:\n  group: ci-${{ github.ref }}\n  cancel-in-progress: true\n\njobs:', s, count=1); log += ['cancel superseded runs'] * k
pat = re.compile(r'(?ms)^      - name: [^\n]*\n        run: python3 tests/check\.py\n(?=      - |\Z)')
seen = []
def dedupe(m):
    if seen: log.append('dropped duplicate check step'); return ''
    seen.append(1); return m[0]
s = pat.sub(dedupe, s)
if s != o: open(P, 'w').write(s)
print('ci.yml: ' + (', '.join(log) if log else 'already optimised'))
