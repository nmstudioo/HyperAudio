# 44.1 kHz refit

Four VDCs had a 44.1 kHz bank that drifted from the 48 kHz one; the refit brings each back to 0.2 dB or less, offline.

## Result

| Profile | Max error before (dB) | After (dB) | Max pole radius | Written |
|---|---|---|---|---|
| iem-hd | 0.14 | 0.01 | 0.9602 | no (already within 0.3 dB) |
| iem-v4 | 0.92 | 0.03 | 0.9689 | yes |
| iem-v10 | 1.36 | 0.01 | 0.9705 | yes |
| spk-v6 | 0.02 | 0.00 | 0.9924 | no (already within 0.3 dB) |
| spk-v8 | 1.59 | 0.02 | 0.9890 | yes |
| spk-v10 | 1.57 | 0.20 | 0.9899 | yes |

Max error is the 44.1 kHz bank against the 48 kHz bank.

## How it was checked

`src/dsp/refit44.py` compares each 44.1 kHz bank's computed response with the same file's 48 kHz bank on a 600-point grid from 20 Hz to 20 kHz.

## What changed

- Only the 44.1 kHz line of four VDCs changes.
- The 48 kHz bank, the section counts and the file format are untouched.
- The refit files are in `candidates/v6/` and were promoted into `src/profiles/` in 6.1.0 after a listening check reported by the author.
