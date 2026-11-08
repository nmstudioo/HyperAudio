# v7 step 2 — shared limiter core (calculated; nothing run on a device)

## Findings
1. Measurement artifact: tests measured true peak on a hard-truncated signal; resampling edge ringing inflated tone overshoot (v5 "+0.20 dB" was mostly that). With edges trimmed, v5 tones are +0.01..+0.03 dB. Noise overshoot is real: v5 +1.88 dB.
2. Cause of noise overshoot: 8-tap Hann-sinc detector truncation error (not phase count). 8x phases with 8 taps still +1.7 dB.
3. Detector timing: the interpolated peak lies ~3.5 samples before the newest sample; v5 attributed it to the newest sample.
4. Real runtime available: /home/claude/w/vm/harness is an NSEEL VM; used alongside eel2py and numpy.

## v7 core
16-tap Kaiser(beta 4) windowed-sinc, 4x (3 phases), centre-aligned (+7 samples audio delay, total latency 79 samples = 1.65 ms), gate hold 16 samples, 1.5% detector guard (-0.13 dB on tones). Same ceilings, sliders, defaults as v5.

## Results (8x reference; ceil per profile)
| profile | v5 worst TP | v7 worst TP | sample peak / ceil |
|---|---|---|---|
| IEM HD / V4 / V10 | +1.88 | +0.25 | 1.0000 (never above) |
| SPK V6 / V8 | +1.95 / +1.89 | +0.25 | 1.0000 |
| SPK V10 | +1.70 | +0.20 | 1.0000 |
Extra: 3 more noise seeds and a 50 Hz-20 kHz hot sweep worst +0.40 dB (numpy; no EEL run). Gate: <= 0.5 dB.
- Cross-check, real VM vs numpy: max diff 2.2e-5 (float32 output rounding). eel2py suite: THD -47.5 dB, tail 0.84 s, soak pass, same as v5.
- NaN/Inf injection (VM): 0 non-finite outputs, tail identical to clean run.
- CPU (harness wall incl. IO, relative only): loud noise 1.17 s -> 1.55 s (+32%), quiet 0.70 -> 0.80 s (+14%). Phone CPU unmeasured.

## Not verified
Device behaviour, audible effect of +0.13 dB guard and +0.8 ms extra latency, phone CPU. Gate test in repo needs run in CI (patched tests/eel/limiter_tests.py: trimmed metric, 0.5 dB limits).
