# Repository Report: HyperAudio
Generated on: Sat Nov  7 03:11:07 +06 2026

## 1. Git Status
```text
Branch: main
Latest Commit: 2f95cea - ci: run tests/footer.js in the layout gate step (18 minutes ago)

?? REPO_REPORT.md
?? generate_report.sh
```

## 2. Recent Commits
```text
2f95cea - ci: run tests/footer.js in the layout gate step (18 minutes ago)
6a1c4c2 - feat(ui): apply complete footer patch from AKMODS (19 minutes ago)
71df973 - ci: fix layout gate by starting local server and add numpy/scipy for acceptance tests (36 minutes ago)
fee85e9 - feat(ui): sync frontend with v6 backend (evidence links, status text, meta titles) (41 minutes ago)
d5e7036 - feat(v6): merge backend acceptance suite, EEL2 interpreter, and updated docs while preserving frontend layout (55 minutes ago)
```

## 3. CI/CD Status (Latest 3 Runs)
```text
completed	success	ci: run tests/footer.js in the layout gate step	ci	main	push	42292166116	4m38s	2026-11-06T20:53:37Z
completed	success	ci: run tests/footer.js in the layout gate step	pages	main	push	42292166010	28s	2026-11-06T20:53:37Z
completed	success	feat(ui): apply complete footer patch from AKMODS	pages	main	push	42291958565	23s	2026-11-06T20:52:06Z
```

## 4. File Structure (Depth 3)
```text
.
  .nojekyll
  README.md
  REPO_REPORT.md
  VERSION
  build
    __pycache__
    build.py
    response.py
    verify.py
  candidates
    v6
      iem-v10
      iem-v4
      limiter-isp-alignment.md
      profile-eel-notes.md
      spk-v10
      spk-v8
  docs
    CHANGELOG.md
    EVIDENCE.md
    LIMITS.md
    METHOD.md
    OPEN.md
    REPRODUCING.md
    evidence
      acceptance-src-v5.0.0.json
      device-tests.json
    refit44_report.md
  generate_report.sh
  index.html
  releases
    v5.0.0
      FROZEN
      HyperAudio_v5.0.0_all.zip
      HyperAudio_v5.0.0_iem-hd.zip
      HyperAudio_v5.0.0_iem-v10.zip
      HyperAudio_v5.0.0_iem-v4.zip
      HyperAudio_v5.0.0_spk-v10.zip
      HyperAudio_v5.0.0_spk-v6.zip
      HyperAudio_v5.0.0_spk-v8.zip
      SHA256SUMS.txt
      iem-hd
      iem-v10
      iem-v4
      profiles.json
      spk-v10
      spk-v6
      spk-v8
  site
    .nojekyll
    README.md
    archive.html
    assets
      brand
      css
      icons
      img
      js
    changelog.html
    compare.html
    data
      choose.json
      profiles.json
      versions.json
    downloads
      v5.0.0
    favicon.ico
    finder.html
    index.html
    manifest.webmanifest
    robots.txt
    tools
      make_brand.py
  src
    README.md
    dsp
      refit44.py
    profiles
    profiles.meta.json
      iem-hd
      iem-v10
      iem-v4
      spk-v10
      spk-v6
      spk-v8
  tests
    check.py
    eel
      eel2py.py
      limiter_tests.py
    footer.js
    overflow.js
```

## 5. Core Tests Status
```text
all checks passed
```

## 6. Release Blockers (from HANDOFF.md)
HANDOFF.md not found.
