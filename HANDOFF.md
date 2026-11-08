# Handoff

Where the project stands and what is blocking final v6 hardware verification.

## Current state (v6.0.0)

- The live site is stable and running v6.0.0.
- CI/CD is fully optimised (cached) and green.
- All v6 backend logic, documentation and UI features are merged and tested.

## Blockers

Both groups are needed to finish v6 hardware verification and are blocked on external assets or physical instruments.

### Needs the author (source files)

| Missing | Why it matters |
|:--|:--|
| **Generator script** | Creates the +10/+12 dB speaker variants and the Protection V6 build (2.24 IR peak) |
| **Unstable profile EEL** | The script causing instability is missing, so the bug cannot be reproduced |

### Needs hardware

| Missing | Why it matters |
|:--|:--|
| **Acoustic measurements** | A calibrated mic and interface would change the site status from "calculated" to "measured" |
| **Device and CPU tests** | The Redmi 12 and KZ EDX Pro are needed to run the cap tests and the CPU measurement |

## How to resume

1. Drop the generator and EEL into `build/`.
2. Run `python3 build/build.py` to generate the new profiles.
3. Run `tst` (or `python3 tests/check.py`) to verify.
4. Update `VERSION` and commit.

The full item list, with what each one needs, is in [docs/OPEN.md](docs/OPEN.md).
