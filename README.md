<div align="center">
  <img src="site/assets/brand/github-cover.svg" alt="HyperAudio Cover" width="100%">
  
  <br>
  
  <h1>HyperAudio</h1>
  
  <p><strong>Calibrated DSP profiles for RootlessJamesDSP.</strong></p>
  
  <p>
    <a href="https://nmstudioo.github.io/HyperAudio/">Live Site</a> &nbsp;·&nbsp;
    <a href="docs/METHOD.md">Method</a> &nbsp;·&nbsp;
    <a href="docs/EVIDENCE.md">Evidence</a> &nbsp;·&nbsp;
    <a href="docs/LIMITS.md">Limits</a>
  </p>
  
  <p>
    <img src="https://img.shields.io/badge/Version-5.0.0-amber?style=flat-square" alt="Version">
    <img src="https://img.shields.io/badge/Status-Stable%20·%20Device--Tested-success?style=flat-square" alt="Status">
  </p>
</div>

---

## Repository Structure

```text
HyperAudio/
├── .github/workflows/   # CI (layout gates) and Pages deployment
├── build/               # Build scripts (build.py, verify.py)
├── candidates/          # Experimental profiles (v6)
├── docs/                # Method, Limits, Evidence, Reproducing
├── releases/            # Frozen, versioned releases (v5.0.0)
├── site/                # The live web interface (HTML/CSS/JS)
├── src/                 # Source DSP profiles and metadata
├── tests/               # Validation (check.py, overflow.py)
├── index.html           # Root redirect to /site/
├── VERSION              # Current version string
└── README.md            # This file
```

Rebuild & Test

```bash
# 1. Rebuild the site and artifacts
python3 build/build.py

# 2. Run static checks (syntax, structure, chrome)
python3 tests/check.py

# 3. Run layout gates (requires Playwright)
pip install playwright
playwright install chromium
python3 tests/overflow.py
```

See docs/REPRODUCING.md for full details.

Web Interface Features

The live site features a fully responsive, accessibility-first design:

Context Layout
Desktop (≥1100px) Fixed left sidebar with scroll-spy navigation
Tablet (768–1099px) Collapsible 72px icon rail
Phone (<768px) Bottom navigation bar with a slide-up "More" sheet

Navigation and footer are injected via site/assets/js/nav.js so styling remains unified across all pages.

Evidence & Testing

· Device tests: See docs/evidence/device-tests.json.
· CI Gate: Every push to main runs tests/overflow.py to ensure no horizontal overflow at 320px, 375px, 768px, 1024px, and 1440px in both dark and light themes.

---

<div align="center">
<sub>Tested by Noushad Mostafa · Built with a focus on calibrated, measured audio.</sub>
<br><br>
<img src="site/assets/brand/logo.svg" alt="HyperAudio Logo" width="90" height="90">
<br>
</div>
