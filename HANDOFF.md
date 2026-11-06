
Project Handoff & Blockers

Current State (v6.0.0)

· The live site is stable and running on v6.0.0.
· CI/CD is fully optimized (cached) and green.
· All v6 backend logic, documentation, and UI features are merged and tested.

Remaining Verification Blockers

The following items are required to finalize the v6 hardware verification, but are currently blocked due to missing external assets or physical instruments.

1. Missing Source Files (Requires Author)

· Generator Script: Needed to create the +10/+12 dB speaker variants and the Protection V6 build (2.24 IR peak).
· Unstable Profile EEL: The script causing instability is missing, preventing bug reproduction.
· Fonts (.woff2): The actual font files are missing, preventing self-hosting (site currently uses Google Fonts).

2. Missing Physical Instruments (Requires Hardware)

· Acoustic Measurements: Need calibrated mic/interface to change site status from "calculated" to "measured".
· Device & CPU Tests: Need the actual Redmi 12 / KZ EDX Pro hardware to run the cap tests and CPU measurement.

How to Resume

When the assets/instruments are available:

1. Drop the generator/EEL/fonts into the build/ or site/assets/fonts/ directories.
2. Run python3 build/build.py to generate the new profiles.
3. Run tst (or python3 tests/check.py) to verify.
4. Update VERSION and commit.
   MD_EOF

echo "Markdown files updated to premium v6 standard."
