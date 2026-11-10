# Open items

Status after v7.0.0. Everything shipped is calculated or offline-checked; nothing in v7.0.0 is device-tested.

## At a glance

- **Waiting on a device or instrument:** 5, 6, 9, 10 and the `cpu` check in 2.
- **Waiting on the author:** 4, 8, 12.
- **Waiting on tooling:** 13, 14, 15.
- **Closed:** 1, 3, 7, 11 and the JM-1 source question (permanently unconfirmed, see `data/measurements/SOURCES.md`).

## All items

| # | Item | State | Needs |
|---|---|---|---|
| 1 | CI on GitHub | Done: one test workflow and one release workflow, green on `main` | Nothing |
| 2 | EEL compile, limiter ceiling, tail, CPU, NaN tests | Done offline via `tests/eel` (eel2py): ceiling, true-peak, THD, tail and NaN soak pass on all six; `cpu` stays `not_run` | Optional: confirm on real WDL or ysfx; `cpu` needs a device |
| 3 | Response-error check | Done: VDC times IRS reproduces the stored correction (0.03 dB RMS); checks live in `build/response.py` | Nothing |
| 4 | Speaker boost cap (+8 dB) | Unchanged; +10/+12 variants not built | Decide whether to build them, then a device test |
| 5 | Protection V6 level path | The 110 Hz high-pass and low shelf now sit in the IRS (L1 1.20). Assumes the effect chain is floating point with no clamp between VDC and convolver | Device check of the VDC-to-convolver level path and loud-input clipping |
| 6 | Limiter true-peak | Shared v7 core shipped: worst 8x overshoot +0.25 dB, latency 79 samples (calculated). One gate, <= 0.5 dB | Device and CPU test; automate the EEL-vs-reference cross-check |
| 7 | 44.1 kHz bank | Refit shipped in 6.1.0; v7 speaker banks refit to the 48 kHz response; listening check reported by the author | None; there is no instrument measurement |
| 8 | Profile EEL (Pop, EDM and others) | Not shipped; suspects are listed in [Method](METHOD.md) | A symptom description, then a device test |
| 9 | Device evidence | v7.0.0 `iem-hd` and `spk-v6` have a reported listening pass (the author's own test, not an instrument measurement); the other four builds have no entry | One pass or fail per remaining build (build, device, date, result) |
| 10 | Acoustic measurements | None | A mic measurement, or the site keeps saying "calculated" |
| 11 | Self-hosted fonts | Done: Plus Jakarta Sans and JetBrains Mono, latin subset, via `tools/fetch_fonts.sh` | Nothing |
| 12 | v1 to v4 history | The archive lists them as "no record in repo" | Old notes or files |
| 13 | v7 byte reproducibility | `build/generator/build_v5.py` reproduces v5 byte for byte. Nothing in CI regenerates the v7 files (`build_cand.py`, `build_spk_fold.py`, `gen_eel.py`) | A CI step that regenerates and compares |
| 14 | Stored profile stats | `stats.derived` check warns when stored stats drift from the files (fine grid); `build.py --write-stats` refreshes them for new versions. v7.0.0 stored values are frozen as shipped | Run `--write-stats` before the next release |
| 15 | Release links | Done: the archive drops download links for versions with no `releases/` folder | Nothing |
