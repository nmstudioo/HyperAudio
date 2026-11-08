# Open items

Status of the v6 work. The shipped profile files are byte-identical to v5.0.0; v6 changes tooling, tests, docs and the site.

## At a glance

- **Closed offline:** 3 (response error), 6 (true-peak candidate rejected, limiter unchanged) and 2 (all but `cpu`).
- **Waiting on a device or instrument:** 9, 10, the `cpu` check in 2, and the device test in 4.
- **Waiting on the author:** 5, 8, 11, 12, 13, and the generator in 4.
- **Waiting on one listening check:** 7.
- **Waiting on GitHub:** 1.
- **Candidate:** 14 has its own open list in [candidates/v6/iem-ghd](../candidates/v6/iem-ghd/README.md).

## All items

| # | Item | State | Needs |
|---|---|---|---|
| 1 | CI on GitHub | Workflow updated (installs numpy and scipy, runs the full acceptance suite); not yet run on GitHub | Push the repo and confirm Actions are green |
| 2 | EEL compile, limiter ceiling, tail, CPU, NaN tests | Done offline via `tests/eel` (eel2py): ceiling, true-peak, THD, tail and NaN soak pass on all six; `cpu` stays `not_run` | Optional: confirm on real WDL or ysfx; `cpu` needs a device |
| 3 | Response-error check | Done: VDC times IRS reproduces the stored correction (0.03 dB RMS); checks live in `build/response.py` | Nothing |
| 4 | Speaker boost cap (+8 dB) | Unchanged. Applied boost is +7.3 to +8.2 dB against +10.7 to +11.6 needed; mean shortfall is about -2 dB, not 3 to 5 | Generator for the +10/+12 variants, then a device test |
| 5 | Protection V6 loudness (IR peak 2.24 against 1.25) | Build not found in the v5 files | Name the build or send the generator |
| 6 | True-peak overshoot (+0.19 dB) | Measured +0.20 dB confirmed; candidate `L_D + 5` rejected (worse on the real EEL); limiter unchanged, see [the note](../candidates/v6/limiter-isp-alignment.md) | Nothing, unless clipping is heard |
| 7 | 44.1 kHz bank | Refit done offline, in `candidates/v6/` | One listening check on a 44.1 kHz file, then promote |
| 8 | Profile EEL (Pop, EDM and others) | Not in the repo; no unstable path found by reading | A symptom description; fixes are in [the notes](../candidates/v6/profile-eel-notes.md); then a device test |
| 9 | Device evidence | All six builds `untested` | One pass or fail per build (build, device, date, result) |
| 10 | Acoustic measurements | None | A mic measurement, or the site keeps saying "calculated" |
| 11 | Self-hosted fonts | Google Fonts fallback (the sandbox could not download) | woff2 files for Plus Jakarta Sans and JetBrains Mono |
| 12 | v1 to v4 history | The archive lists them as "no record in repo" | Old notes or files |
| 13 | Release v6.0.0 | Not cut | VERSION bump, build, freeze, replace the hardcoded "v5.0.0" in `index.html`, preview branch approval |
| 14 | KZ EDX Pro · GHD candidate | In `candidates/v6/iem-ghd`; offline gates pass (calculated) | Limiter figures match v5 exactly (unexplained), CPU, `init_done` in JamesDSP, one listening check |
