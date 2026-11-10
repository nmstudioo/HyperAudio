# Evidence

Evidence comes in three tiers that are never mixed on the site: offline automated checks, device reports and acoustic measurement.

## Tiers

| Tier | Today |
|---|---|
| 1. Offline, automated | `releases/<v>/acceptance.json`, produced by `build/build.py`. The frozen 7.0.0 file has 19 checks per build: 108 `pass`, 0 `warn`, 6 `not_run` (`cpu`). CI rebuilds with 24 per build, adding the release gates and `stats.derived`. |
| 2. Device-reported | `docs/evidence/device-tests.json`. All six v7.0.0 builds have an author-reported listening pass. |
| 3. Acoustic measurement | None yet; the site keeps saying "calculated". |

Device results are the author's own listening tests, not instrument measurements.

## Tier 1: offline checks

Each build is checked for file validity, VDC banks and sections, IRS format and limits, EEL static lint, response, limiter and runtime behaviour. Status is `pass`, `warn`, `fail` or `not_run`.

| Check | Result |
|---|---|
| `response.*` | `pass`. The shipped VDC times IRS reproduces each stored `correction` curve to 0.03 dB RMS on all six builds. |
| `irs.peak_limit`, `irs.l1`, `irs.tail`, `vdc.pole_radius` | Release gates, see [Limits](LIMITS.md). Enforced on every build by CI. |
| `eel.compile`, `limiter.*`, `tail`, `nan_soak` | `pass`. Run through `tests/eel` (eel2py). |
| `vdc.sr_consistency` | `pass`: the 44.1 kHz bank is within 0.3 dB of the 48 kHz bank. |
| `stats.derived` | Warns if stored profile stats drift from the files on a fine grid. A warning is not a failure. |
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

The v7 speaker chains have the same response as the earlier builds, so these figures still apply.

- Applied peak boost is +7.3 to +8.2 dB, against +10.7 to +11.6 dB needed.
- The mean shortfall over 100 to 2000 Hz is about -2.0 dB.
- The worst single point is -11 to -12 dB.

## True-peak limits

Measured with eel2py at 8x oversampling, as overshoot above the ceiling. The shared v7 limiter core gives a worst case of about +0.25 dB on tones, clicks and +6 dB broadband noise, against a gate of 0.5 dB. The v5 limiter overshot by +1.7 to +1.95 dB on noise.

Sample peaks never exceed the ceiling because of a hard clamp. These figures come from a subset interpreter, not the WDL runtime; the device check is the final authority.

## Raw data

- [`docs/evidence/acceptance-src-v5.0.0.json`](evidence/acceptance-src-v5.0.0.json): acceptance results generated from `src/` for v5.0.0
- [`docs/evidence/device-tests.json`](evidence/device-tests.json): device entries
