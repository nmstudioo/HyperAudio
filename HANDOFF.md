# Handoff

Where the project stands.

## Current state

- Live site and shipped profiles: v6.1.0 (44.1 kHz bank refit). UI 7.0.0 is site-only.
- v7 DSP candidates are in `candidates/v7` (IEM HD A/B/C, iem-v4, iem-v10, spk-v6, spk-v8, spk-v10). Offline gates pass (calculated). Nothing is device-tested.
- The generator is in `build/generator`. It reproduces the v5.0.0 files byte for byte (`tests/gen_repro.py`).
- The Protection V6 IR peak of 2.24 is fixed in the v7 candidate: the 110 Hz high-pass and low shelf are folded into the IRS, which is scaled to L1 1.20.
- CI caches the v7 pair gates and the limiter gate; a push without DSP changes stays near 3.5 min.

## Blockers (hardware or listening only)

| Needed | Why |
|:--|:--|
| IEM blind A/B/C listening | Picks the HD target (Harman IE 2019, JM-1, or v5 control) |
| Redmi 12 check | V6 level path from VDC to convolver (assumes no clamp; fallback `--keep-v6-structure`), loud-input clipping, limiter CPU |
| JM-1 source URL | Provenance of candidate B is reported, not confirmed |
| Acoustic measurements | Would move "calculated" to "measured" |

## How to resume

1. Pick the HD target, then run `python3 tools/promote_v7.py --hd A|B|C --dry-run`.
2. Without `--dry-run`, then `python3 build/build.py`, `python3 build/docs_site.py && python3 tools/ship.py`, `python3 build/freeze.py`, commit, tag.
3. Run `python3 tests/gate_v7_candidates.py` and `python3 tests/gen_repro.py` after any generator or candidate change.
