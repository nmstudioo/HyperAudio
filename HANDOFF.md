# Project Handoff & Blockers

## Current State

- The live site is stable and running on v5.0.0.
- CI/CD is fully green (Layout gates + Runtime acceptance).
- All v6 backend logic (EEL2 interpreter, response checks) is merged and tested.

## Remaining v6 Release Blockers

The following items are required to finalize and freeze v6, but are currently blocked due to missing external assets or physical instruments.

### 1. Missing Source Files (Requires Author)

- **Generator Script:** Needed to create the +10/+12 dB speaker variants and the Protection V6 build (2.24 IR peak).
- **Unstable Profile EEL:** The script causing instability is missing, preventing bug reproduction.
- **Fonts (.woff2):** The actual font files are missing, preventing self-hosting (site currently uses fallbacks).

### 2. Missing Physical Instruments (Requires Hardware)

- **Acoustic Measurements:** Need calibrated mic/interface to change site status from "calculated" to "measured".
- **Device & CPU Tests:** Need the actual Redmi 12 / KZ EDX Pro hardware to run the cap tests and CPU measurement.

### 3. Release Steps (Requires Sign-off)

- Once the above are resolved, the `VERSION` file must be bumped to `v6.0.0`, and the UI text must be updated from "Stable" to the new release status.

## How to Resume

When the assets/instruments are available:

1. Drop the generator/EEL/fonts into the `build/` or `site/assets/fonts/` directories.
2. Run `python3 build/build.py` to generate the new profiles.
3. Run `python3 tests/check.py` and `node tests/overflow.js` to verify.
4. Update `VERSION` and commit.
