| profile | 44.1 vs 48 max err before (dB) | after (dB) | max pole radius | written |
|---|---|---|---|---|
| iem-hd | 0.14 | 0.01 | 0.9602 | no (already within 0.3 dB) |
| iem-v4 | 0.92 | 0.03 | 0.9689 | yes |
| iem-v10 | 1.36 | 0.01 | 0.9705 | yes |
| spk-v6 | 0.02 | 0.00 | 0.9924 | no (already within 0.3 dB) |
| spk-v8 | 1.59 | 0.02 | 0.9890 | yes |
| spk-v10 | 1.57 | 0.20 | 0.9899 | yes |

Verified offline by `src/dsp/refit44.py`: it compares each 44.1 kHz bank's computed response with the same file's 48 kHz bank on a 600-point 20 Hz to 20 kHz grid. Only the 44.1 kHz line of four VDCs changes; the 48 kHz bank, section counts and file format are untouched. Candidates are in `candidates/v6/` and are not part of any release until promoted.
