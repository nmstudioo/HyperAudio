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
- The fit library, EEL generator, target and raw data are not in the repo yet; see [src/README.md](../src/README.md).
