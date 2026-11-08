# Candidates

Experiments that are not part of any release. Nothing here ships until it passes its gates and a device test.

## v6

| Candidate | Where | State |
|:--|:--|:--|
| **KZ EDX Pro · GHD** | [`v6/iem-ghd/`](v6/iem-ghd/README.md) | Candidate; offline gates pass, `untested` on a device |
| **44.1 kHz refits** | `v6/iem-v4/`, `v6/iem-v10/`, `v6/spk-v8/`, `v6/spk-v10/` | Refit done offline (0.01 to 0.20 dB); needs one listening check, then promotion |
| **True-peak alignment `L_N = L_D + 5`** | [`v6/limiter-isp-alignment.md`](v6/limiter-isp-alignment.md) | Rejected; limiter unchanged |
| **Profile EEL (Pop, EDM)** | [`v6/profile-eel-notes.md`](v6/profile-eel-notes.md) | Suspects only, none confirmed |

The refit numbers are in the [44.1 kHz refit report](../docs/refit44_report.md); the full list of open work is in [Open items](../docs/OPEN.md).

## Promotion

1. Re-run the gates: `python3 tests/gate_candidate.py <candidate path>`.
2. Pass a device test and record it in `docs/evidence/device-tests.json`.
3. Move the files into `src/profiles/` and cut a release; see [Releasing](../docs/RELEASING.md).
