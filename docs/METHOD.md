# Method
Chain order in RootlessJamesDSP: VDC, then Convolver (IRS), then Liveprog (EEL).
- **VDC**: biquad banks at 44.1 and 48 kHz fitted to the same predicted curve.
- **IRS**: convolution (4-ch true-stereo for IEM, 2-ch for speaker).
- **EEL**: input guard, 1.5 ms lookahead limiter, true-peak guard, per-profile controls.
- Each chain is normalised to a maximum gain of -0.5 dB; the limiter protects peaks.
- Curves on the site are **calculated**, not acoustic measurements.
Sources: `src/profiles/<id>/` (artifacts) and `src/profiles.meta.json` (copy, stats, curves).
The fit library, EEL generator, target and raw data are not in the repo yet; see `src/README.md`.
