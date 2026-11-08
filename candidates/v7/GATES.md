# v7 candidate gates (calculated; tests/gate_candidate.py; eel2py runtime, not WDL; no device tests)

| Profile | IRS L1 | IRS peak | max pole 48k | bank 44.1/48 (dB) | chain max (dB) | limiter TP (dB) | result |
|---|---|---|---|---|---|---|---|
| IEM HD (C = v5 target) | 1.071 | 0.694 | 0.9690 | 0.054 | -0.50 | +0.23 | PASS |
| IEM Spatial V4 | 0.682 | 0.603 | 0.9714 | 0.004 | -0.48 | +0.23 | PASS |
| IEM Reference V10 | 0.993 | 0.842 | 0.9732 | 0.005 | -0.50 | +0.23 | PASS |
| Speaker Protection V6 | 1.200 | 0.203 | 0.9710 | 0.017 | -0.50 | +0.23 | PASS |
| Speaker Cinema V8 | 1.020 | 0.348 | 0.9796 | 0.000 | -0.50 | +0.23 | PASS |
| Speaker Dynamic V10 | 0.976 | 0.339 | 0.9794 | 0.000 | -0.50 | +0.05 | PASS |

Gates: L1 <= 1.25, peak <= 0.95, tail <= -80 dB, pole <= 0.985, bank <= 0.3 dB (spec target 0.1), chain -0.50 dB, limiter overshoot <= 0.5 dB (tones and +6 dB noise).
