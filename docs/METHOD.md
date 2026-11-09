# Method

Every profile is a three-stage chain in RootlessJamesDSP: a VDC filter bank, a convolver impulse response and a Liveprog limiter script.

## Chain order

| Stage | File | Job |
|---|---|---|
| 1. VDC | `.vdc` | Biquad banks at 44.1 and 48 kHz, fitted to the same predicted curve |
| 2. Convolver | `.irs` | Convolution: 4-channel true-stereo for IEM, 2-channel for speaker |
| 3. Liveprog | `.eel` | Input guard, 1.5 ms lookahead limiter, true-peak guard, per-profile controls |

## Gain and protection

- Each chain is normalised to a maximum gain of -0.5 dB.
- The limiter protects peaks; its limits are listed in [Limits](LIMITS.md).

## What the curves mean

Curves on the site are **calculated**, not acoustic measurements. A predicted curve is the raw response plus the correction plus a constant level alignment. See [Evidence](EVIDENCE.md) for how far each claim is checked.

## Sources

- `src/profiles/<id>/` holds the artifacts.
- `src/profiles.meta.json` holds the copy, stats and curves.
- `build/generator/` holds the fit library and generators. `build_v5.py` reproduces the v5 VDC/IRS bytes; `build_cand.py` and `build_spk_fold.py` produced the v7 files; `gen_eel.py` is the shared limiter core. CI does not yet regenerate the v7 bytes; see [Open items](OPEN.md).

## Rejected and unconfirmed experiments

- **True-peak alignment `L_N = L_D + 5`: rejected.** Measured on the real EEL through eel2py, worst tone or click overshoot went from 0.82 to 1.08 dB at 48 kHz and from 0.37 to 1.06 dB at 44.1 kHz. It did not improve the limiter, so the v5 limiter was left unchanged. The v7 limiter core later replaced it with a different detector.
- **Profile EEL (Pop, EDM): not shipped, cause unconfirmed.** Suspects: `@init` overwrites slider variables; crossover states are not reset on activation or updated while bypassed; a Butterworth-4 band split with `hi = x - lo` ripples near 180 Hz when band gains differ. Keep it out of releases until a symptom is known and a device test passes.
