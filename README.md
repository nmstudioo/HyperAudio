# HyperAudio
Calibrated DSP profiles for RootlessJamesDSP. Current: see `VERSION`.

```
src/        profile artifacts + metadata (DSP generators to be added)
build/      build.py (one command) and verify.py
site/       the web page and published downloads
docs/       METHOD, LIMITS, EVIDENCE, REPRODUCING, CHANGELOG, evidence/
releases/   per-version files, SHA256SUMS.txt, profiles.json, acceptance.json, DIFF.md
tests/      check.py (CI gate)
```
Rebuild: `python3 build/build.py && python3 tests/check.py`. See docs/REPRODUCING.md.
Page notes: site/README.md.
Runtime tests: `pip install numpy scipy; python3 tests/eel/limiter_tests.py src/profiles/iem-hd/EDX_HD.eel`.
