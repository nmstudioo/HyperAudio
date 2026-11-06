
Changelog

v6.0.0 (Current)

Added

· Responsive UI: Complete redesign with desktop sidebar, tablet icon-rail, and mobile bottom sheet.
· Documentation Site: Automated Markdown-to-HTML rendering (site/docs/) for seamless reading.
· Custom 404: Theme-aware error page that preserves the /HyperAudio/ base path.
· Backend Integration: Merged EEL2 runtime tests and response acceptance suites.
· CI Enhancements: Caching for pip/npm/Playwright, concurrency cancellation, and local link checking (links.js).
· Formatting Tooling: Custom AST-verified formatter (tools/fmt.py) enforcing zero-indentation style.

Changed

· Bumped all UI badges, meta tags, and footer text to v6.0.0.
· Reorganized the repository structure to separate backend testing from the frontend UI.
· Consolidated navigation into a shared nav.js component.

v5.0.0

· Initial stable release with six RootlessJamesDSP profiles for KZ EDX Pro and Redmi 12.
  MD_EOF

4. Update docs/EVIDENCE.md

cat << 'MD_EOF' > docs/EVIDENCE.md

Evidence & Validation

<div align="center">
  <img src="https://img.shields.io/badge/Status-Offline%20%2B%20Author%20Device%20Test-f2b13a?style=flat-square" alt="Status">
</div>

v6 Backend Acceptance Suite

As of v6.0.0, the repository includes a comprehensive automated acceptance suite.

· Response Error: Closed. The shipped VDC × IRS reproduces each stored correction curve to 0.03 dB RMS.
· EEL Compilation: Validated via an independent EEL2 interpreter (tests/eel/eel2py.py). Sample peak never exceeds the ceiling, THD residual is -47.5 dB.
· True Peak: Confirmed +0.19 dB overshoot (documented as a known limit).

Tested by the Author

The profiles have been tested on the target hardware (Redmi 12 speaker and KZ EDX Pro IEMs) for stability and subjective audio quality. No crackle or distortion was reported.

Note: Acoustic measurements (using a calibrated microphone) have not yet been performed. The responses are calculated based on the provided DSP math, not measured in an anechoic chamber.
