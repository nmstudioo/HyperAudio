<p align="center">
<img src="assets/brand/github-cover.png" alt="HyperAudio: calibrated DSP profiles for RootlessJamesDSP" width="100%">
</p>

# HyperAudio site

Static site and downloads for six DSP profiles. The chain order in RootlessJamesDSP is VDC, then Convolver, then Liveprog.

Profiles: **iem-hd, iem-v4, iem-v10** (KZ EDX Pro) and **spk-v6, spk-v8, spk-v10** (Redmi 12).

## Run it

Serve over HTTP, because `file://` blocks the JSON fetch.

```bash
python3 -m http.server
```

## Layout

```text
index.html, finder.html, compare.html, changelog.html, archive.html, 404.html
manifest.webmanifest       installable web app
sw.js                      service worker (network first, cache fallback)
assets/brand/              logo, logo-light, logo-mark, github-cover, og-image (SVG and PNG)
assets/icons/              favicon, apple-touch, 192/512 and maskable icons
assets/img/                app-layout.webp
assets/css/                fonts, main, site, nav and docs styles
assets/fonts/              self-hosted woff2 (tools/fetch_fonts.sh)
assets/js/                 app, chart, nav, pages, docs, theme-init
data/profiles.json         single source of truth: profiles, files, SHA-256, curves
data/                      versions, evidence and choose data
docs/                      rendered from ../docs/*.md by build/docs_site.py
downloads/<version>/       VDC, IRS and EEL per profile, per-profile zips, all-in-one, SHA256SUMS.txt
tools/make_brand.py        regenerates every brand asset
```

## Releasing

Replace the files, then update `data/profiles.json` and `SHA256SUMS.txt`. The full procedure is in [Releasing](../docs/RELEASING.md).

## Evidence and limits

- **Offline-verified:** file validity, VDC and IRS fit, EEL compile and limiter tests in a VM.
- **Device-reported:** no crackle on the speaker profiles; the IEM passed; True Peak Detect on.
- **Speaker boost** is capped at +8 dB and high-passed below 110 Hz, so speaker curves sit below the uncapped target at 100 to 2000 Hz by design.
- **Predicted-response curves** are calculated, not acoustic measurements.

## Brand assets

Set `assets/brand/github-cover.png` (1280 x 640) as the repository social preview in Settings > General.

`tools/make_brand.py` rebuilds every asset. Text is outlined and the curve comes from `profiles.json`. It needs fontTools, Pillow, Playwright and the Inter font.
