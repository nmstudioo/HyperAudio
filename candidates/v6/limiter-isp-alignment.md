# True-peak alignment `L_N = L_D + 5`

**Rejected.** Measured on the real EEL: it did not improve the limiter, so the limiter is left unchanged.

## Method

`tests/eel` runs the shipped `.eel` through eel2py, an independent subset interpreter. The v5 baseline reproduces the author's figure: +0.20 dB at 997 Hz (48 kHz).

## Result

Worst tone or click true-peak overshoot, v5 against the candidate:

| Sample rate | Builds | v5 | Candidate |
|:--|:--|--:|--:|
| 48 kHz | iem and spk | 0.82 dB | 1.08 dB |
| 44.1 kHz | iem and spk | 0.37 dB | 1.06 dB |

The square wave was included in this early run. Excluding it, since its Gibbs ringing is a test artefact, the candidate still did not improve the 997 Hz or 44.1 kHz cases. The earlier Python-model gain did not carry over.

## Decision

Leave the limiter unchanged. The sample peak never exceeds the ceiling, and the limited-tone THD residual is -47.5 dB.

## Known limit

+6 dB overload noise overshoots by about +1.9 dB (guard 2.5 dB). Re-run after any change:

```bash
python3 tests/eel/limiter_tests.py <file.eel>
```
