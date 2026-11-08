# Evidence

Evidence comes in three tiers that are never mixed on the site: offline automated checks, device reports and acoustic measurement.

## Tiers

| Tier | Today |
|---|---|
| 1. Offline, automated | `releases/<v>/acceptance.json`, produced by `build/build.py`. Runs on every build; 6.1.0 has 108 `pass`, 0 `warn` and 6 `not_run`. |
| 2. Device-reported | `docs/evidence/device-tests.json`. Every build is `untested` until a result is recorded. |
| 3. Acoustic measurement | None yet; the site keeps saying "calculated". |

Legacy v5 claims such as "IEM passed" are recorded as `untested` per build until each one is re-run individually.

## Tier 1: offline checks

Each build is checked for file validity, VDC banks and sections, IRS format and peak against metadata, EEL static lint, response, limiter and runtime behaviour. Status is `pass`, `warn`, `fail` or `not_run`.

| Check | Result |
|---|---|
| `response.*` | `pass`. The shipped VDC times IRS reproduces each stored `correction` curve to 0.03 dB RMS on all six builds. |
| `eel.compile`, `limiter.*`, `tail`, `nan_soak` | `pass`. Run through `tests/eel` (eel2py). |
| `vdc.sr_consistency` | `pass` on all six builds in 6.1.0: the 44.1 kHz bank is within 0.01 to 0.20 dB of the 48 kHz bank (limit 0.3). In 6.0.x it was `warn` on four builds (0.9 to 1.6 dB). |
| `cpu` | `not_run`. Needs a device. |

The response convention is documented in the `build/response.py` docstring: `predicted` is raw plus correction plus a constant level alignment.

eel2py is an independent interpreter, not the WDL/JSFX runtime. Its assumptions are listed in `tests/eel/eel2py.py`. Treat it as strong offline evidence, not device proof.

## Tier 2: device reports

One entry per build, device, date and result, in `docs/evidence/device-tests.json`.

```
{"release","build","device","date","test","result":"pass|fail|untested","notes"}
```

## Tier 3: acoustic measurement

There are no acoustic measurements. Every curve on the site is calculated.

## Speaker cap

- Applied peak boost is +7.3 to +8.2 dB, against +10.7 to +11.6 dB needed.
- The mean shortfall over 100 to 2000 Hz is about -2.0 dB. The earlier "3 to 5 dB" figure is not reproduced.
- The worst single point is -11 to -12 dB.

## True-peak limits

Measured with eel2py at 8x oversampling, as overshoot above the ceiling:

- Tones, clicks and square waves: about +0.20 dB.
- Broadband noise driven 6 dB over the ceiling: about +1.9 dB (test guard 2.5 dB).

Sample peaks never exceed the ceiling because of a hard clamp. These figures come from a subset interpreter, not the WDL runtime; the device check is the final authority.

## Raw data

- [`docs/evidence/acceptance-src-v5.0.0.json`](evidence/acceptance-src-v5.0.0.json): acceptance results generated from `src/` for v5.0.0
- [`docs/evidence/device-tests.json`](evidence/device-tests.json): device entries
