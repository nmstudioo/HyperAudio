# Open v6 items

Status as of this package. Nothing here is released; v5.0.0 files are unchanged.

| # | Item | State | Needs |
|---|------|-------|-------|
| 1 | CI on GitHub | Not run (only run locally) | Push repo, confirm Actions green |
| 2 | EEL compile, limiter ceiling, tail, CPU, NaN tests | `not_run` in acceptance.json | EEL2 runtime in CI (ysfx, untried) |
| 3 | Response-error check | `not_run`: files do not reproduce stored curves | Generator or its convention |
| 4 | Speaker boost cap (+8 dB) | Unchanged | Device listening test of higher-cap variants (needs generator) |
| 5 | Protection V6 loudness (IR peak 2.24 vs 1.25) | Build not found in v5 files | Name the build or send generator |
| 6 | True-peak overshoot (+0.19 dB) | Candidate fix `L_N = L_D + 5` (see candidates/v6/limiter-isp-alignment.md); Python model only | Harness run on real EEL, then device check |
| 7 | 44.1 kHz bank | Refit done offline, in candidates/v6/ | One listening check on a 44.1 kHz file, then promote |
| 8 | Profile EEL (Pop, EDM...) | Not in repo; no unstable path found by reading | Symptom description; fixes in candidates/v6/profile-eel-notes.md; device test |
| 9 | Device evidence | All six builds `untested` | One pass/fail per build (build, device, date, result) |
| 10 | Acoustic measurements | None | Mic measurement, or site keeps saying "calculated" |
| 11 | Self-hosted fonts | Google Fonts fallback (sandbox could not download) | woff2 files for Plus Jakarta Sans and JetBrains Mono |
| 12 | v1 to v4 history | Archive lists them as "no record in repo" | Old notes or files |
| 13 | Release v6.0.0 | Not cut | VERSION bump, build, freeze, replace hardcoded "v5.0.0" in index.html, preview branch approval |
