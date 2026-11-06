# Changelog
## v6.0.0 (in progress)
- Step 1 done: repo restructure, one-command build, CI, per-release folders, profiles.json diff, per-build acceptance file. No DSP change; v5 files rebuild with identical hashes.
- 44.1 kHz refit candidates for iem-v4, iem-v10, spk-v8, spk-v10 (candidates/v6/, not yet released).
- Open items tracked in docs/OPEN.md; candidate limiter alignment and profile EEL notes in candidates/v6/.
- Pending: DSP fixes (docs/LIMITS.md), device evidence, site Phase 2.
## v5.0.0 (2026-11-05)
Six profiles (3 IEM, 3 speaker); VDC with matched 44.1/48 kHz banks; limiter with 1.5 ms lookahead and true-peak guard. Earlier versions: history not in this repo.
- Site Phase 2: before/after labels and "Change" readout at the cursor, compare.html, finder.html, changelog.html, archive.html (v1/v2 dashed). Fonts: Google Fonts kept as documented fallback; the build sandbox could not reach fonts.googleapis.com, so self-hosting is pending.
