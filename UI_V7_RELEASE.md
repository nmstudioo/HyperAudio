# HyperAudio UI 7.0.0

Frontend only. `VERSION` stays at the DSP release (6.1.0); `src/`, `releases/` and `site/downloads/` are untouched. Candidate builds are not linked as downloads.

## What changed

- The first v7 overlay is folded into the sources. `v7-ui.js` and `v7-ui.css` are gone.
- Chart: fixed y-scale per output, high-pass band on the speaker, display-only 1/6 and 1/3 octave smoothing, same-output overlay, spoken readout on arrow keys.
- Evidence chips: calculated, offline checks, device record and acoustic status, from `data/evidence.json`. An `experimental` or `candidate` profile gets an Experimental chip.
- Sticky download dock under 760 px while choosing a profile.
- Fonts are self-hosted, a CSP meta is on every page, and the service worker cache has its own `UI_VERSION`.

## Gates

`python3 tools/ship.py`, `node tests/ui-v7-contract.js`, `node tests/ui-behavior.js` (Chromium and WebKit), plus the existing overflow, footer, a11y and budget tests. CI: `.github/workflows/v7-ui-validation.yml` (also uploads screenshots at 360, 768 and 1280 px).

## Evidence classes stay separate

Calculated response, offline checks, device-reported listening, device test per build and acoustic measurement are different claims. The UI never merges them.
