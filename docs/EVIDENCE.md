# Evidence
Three tiers, never mixed on the site:
1. **Offline, automated** (`releases/<v>/acceptance.json`, produced by `build/build.py`): file validity, VDC banks/sections, IRS format and peak vs metadata, EEL static lint. Status is `pass`, `fail` or `not_run`.
   `not_run` today: eel.compile, limiter.ceiling, response_error, tail, cpu, nan_soak. They need an EEL runtime and the test harness, which are not in the repo yet. They are listed, not faked.
2. **Device-reported** (`docs/evidence/device-tests.json`): one entry per build, device, date, result.
3. **Acoustic measurement**: none yet. Site keeps saying "calculated".

Entry schema: `{"release","build","device","date","test","result":"pass|fail|untested","notes"}`.
Legacy v5 claims ("IEM passed") are recorded as `untested` per build until re-run individually.

## v6 prep results (docs/evidence/acceptance-src-v5.0.0.json, generated from src/, v5.0.0 unchanged)
- `response.*` now run (build/response.py): shipped VDC x IRS reproduces each stored `correction` curve to 0.03 dB RMS on all six builds, so the earlier "files do not reproduce curves" finding is closed. Convention in the module docstring. `predicted` = raw + correction + a constant level alignment.
- `eel.compile`, `limiter.*`, `tail`, `nan_soak` now run through tests/eel (eel2py). Tier note: this is an independent interpreter, not the WDL/JSFX runtime; assumptions are listed in eel2py.py. Treat as strong offline evidence, not device proof.
- `vdc.sr_consistency` is `warn` for iem-v4, iem-v10, spk-v8, spk-v10 (44.1 vs 48 kHz bank 0.9 to 1.6 dB at 20 kHz). `cpu` stays `not_run` (needs a device).
- Speaker cap: applied peak boost is +7.3 to +8.2 dB vs +10.7 to +11.6 dB needed. Mean shortfall over 100-2000 Hz is about -2.0 dB (the "3 to 5 dB" figure is not reproduced); worst single point is -11 to -12 dB.

## True-peak limits (eel2py, 8x oversampled)
Tones, clicks and square waves overshoot the ceiling by about +0.20 dB. Broadband noise driven 6 dB over the ceiling overshoots by about +1.9 dB (test guard 2.5 dB). Sample peaks never exceed the ceiling (hard clamp). These come from a subset interpreter, not the WDL runtime; the device check is the final authority.
