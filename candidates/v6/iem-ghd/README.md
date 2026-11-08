# KZ EDX Pro · GHD

A candidate in-ear profile, not released.

| Status | Evidence | Device test | Acoustic measurement |
|:--|:--|:--|:--|
| **Candidate** | **Calculated** | **Untested** | **None** |

Re-run the gates:

```bash
python3 tests/gate_candidate.py candidates/v6/iem-ghd/EDX_GHD
```

## What it is

| Part | Detail |
|:--|:--|
| **VDC** | 10 biquads per bank, 44.1 and 48 kHz. A calculated correction toward the Harman 2019 in-ear target. Notches and shelves are **targets, not measurements**. Max pole radius 0.980 and 0.979. |
| **IRS** | 4-channel true-stereo, 2100 frames, minimum phase, 270 µs interaural delay (an average head; real heads vary). Bass and air shelving lives here, not in the VDC. |
| **EEL** | Limiter with a continuous 8-tap 4x sinc true-peak detector, no `while` and no `&`. Default ceiling -1.5 dBFS, which trades 1.5 dB of headroom for inter-sample safety. |
| **Chain gain** | max (LL+LR) x VDC = -0.50 dB, the same convention as every other profile. |

## Measured offline

Numpy and scipy, with the limiter on eel2py rather than the WDL runtime. See the `tests/gate_candidate.py` output.

The VDC notches measure -3.6 dB at 4.8 kHz and -3.8 dB at 8.1 kHz, not the -4.6 and -5.2 dB first specified; the notches were widened afterwards.

## Open before promotion

1. The limiter suite figures (+0.20 dB tones, +1.89 dB noise, clamp 0.0068, THD -47.5 dB) are identical to the v5 core's despite a different detector. With `tpDetect` off the sample peak of an fs/4 45-degree tone is 0.841; on, it is 0.589, so the detector acts, but the suite may not separate the two. Unexplained.
2. The CPU cost of the per-sample `loop(N)` minimum scan is not measured.
3. `!init_done` slider preservation is untested in real JamesDSP.
4. One listening check on the IEM; no frequency-response measurement exists.
5. A fix was applied to the supplied file: line 31 had a missing `$PI`, a syntax error.
