# Open v6 items

Status for v6.0.0. The shipped profile files are byte-identical to v5.0.0; v6 changes tooling, tests, docs and the site.

| # | Item | State | Needs |
|---|------|-------|-------|
| 1 | CI on GitHub | Workflow installs numpy/scipy, runs full acceptance and gates the Pages deploy; green status is not recorded in this repo | Confirm the latest Actions run on `main` is green |
| 2 | EEL compile, limiter ceiling, tail, CPU, NaN tests | DONE offline via tests/eel (eel2py): ceiling, true-peak, THD, tail, NaN soak pass on all six; cpu remains not_run | Optional: confirm on real WDL/ysfx; cpu needs device |
| 3 | Response-error check | DONE: VDC x IRS reproduces stored correction (0.03 dB RMS); checks in build/response.py | Nothing |
| 4 | Speaker boost cap (+8 dB) | Unchanged. Applied boost +7.3 to +8.2 dB vs +10.7 to +11.6 needed; mean shortfall about -2 dB, not 3 to 5 | Generator for +10/+12 variants, then device test |
| 5 | Protection V6 loudness (IR peak 2.24 vs 1.25) | Build not found in v5 files | Name the build or send generator |
| 6 | True-peak overshoot (+0.19 dB) | Measured +0.20 dB confirmed; candidate `L_D + 5` REJECTED (worse on real EEL); limiter unchanged | Nothing, unless clipping is heard |
| 7 | 44.1 kHz bank | Refit done offline, in candidates/v6/ | One listening check on a 44.1 kHz file, then promote |
| 8 | Profile EEL (Pop, EDM...) | Not in repo; no unstable path found by reading | Symptom description; fixes in candidates/v6/profile-eel-notes.md; device test |
| 9 | Device evidence | All six builds `untested` | One pass/fail per build (build, device, date, result) |
| 10 | Acoustic measurements | None | Mic measurement, or site keeps saying "calculated" |
| 11 | Self-hosted fonts | Google Fonts fallback (sandbox could not download) | woff2 files for Plus Jakarta Sans and JetBrains Mono |
| 12 | v1 to v4 history | Archive lists them as "no record in repo" | Old notes or files |
| 13 | Release v6.0.0 | Not cut | VERSION bump, build, freeze, preview branch approval |
| 14 | KZ EDX Pro · GHD candidate | In candidates/v6/iem-ghd, offline gates pass (calculated) | Limiter figures match v5 exactly (unexplained), CPU, init_done in JamesDSP, one listening check |
