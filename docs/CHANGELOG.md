# Changelog

What changed in each version, newest first. Profile files are frozen per release; v6.0.0 changed tooling, tests, docs and the site, not the profiles.

## v7.0.0

Calculated and offline-checked. Author-reported listening passes for all six builds are recorded in `docs/evidence/device-tests.json`; there is no acoustic measurement.

- Shared limiter core v7 in all six scripts: 16-tap Kaiser true-peak detector, centre-aligned lookahead, worst 8x overshoot +0.25 dB (v5: +1.7 to +1.95 dB), +0.15 ms latency.
- IEM HD target: Harman IE 2019 (new fit).
- Speakers: the 110 Hz high-pass and low shelf moved from the VDC into the IRS (chain response unchanged); max pole radius 0.971 to 0.980; Protection V6 IRS L1 2.24 to 1.20.
- IEM Spatial V4 and Reference V10: new limiter only.

### Site

- Folded the first v7 overlay (`v7-ui.js`, `v7-ui.css`) into `app.js` and `base.css`; no MutationObservers, no runtime copy rewrites.
- Response chart: fixed vertical scale per output, high-pass band on speaker profiles, display-only 1/6 and 1/3 octave smoothing, same-output overlay, spoken readout for keyboard users.
- One evidence chip component (calculated, offline checks, device record, acoustic) used in the files step and the evidence cards.
- Sticky download dock on small screens while choosing a profile.
- Self-hosted fonts, a content security policy, a service worker cache keyed to a separate `UI_VERSION`, and behaviour tests (`tests/ui-behavior.js`).

## Unreleased

### Added

- Single version source: `build/stamp.py` stamps `VERSION` into `index.html`, `versions.json` and `sw.js`; CI fails on stale stamps.
- Release automation: a `vX.Y.Z` tag runs `.github/workflows/release.yml` (GitHub Release with zips, checksums, acceptance and diff); `tools/ship.py --release` (freeze) and a FROZEN hash guard.
- Offline support: a service worker (network first, cache fallback).
- Accessibility gate: `tests/a11y.js` (built-in checks plus axe-core in CI).
- Evidence panel: a per-profile check matrix generated from `acceptance.json` into `site/data/evidence.json`.

### Changed

- Docs pages redesigned: shared navigation, section tabs, table of contents, code blocks with copy buttons, previous and next links.

## v6.1.0

Four VDCs ship a refit 44.1 kHz bank: iem-v4, iem-v10, spk-v8 and spk-v10. Nothing else in the profiles changes.

### Changed

- The 44.1 kHz bank now matches the 48 kHz bank within 0.01 to 0.20 dB (calculated), down from 0.9 to 1.6 dB. `vdc.sr_consistency` is `pass` on all six builds; the release has 108 `pass`, 0 `warn`, 6 `not_run`.
- The refit was checked by the author by ear on a 44.1 kHz file. It is not an instrument measurement.
- The 48 kHz banks, section counts, IRS and EEL files are unchanged; see `releases/6.1.0/DIFF.md`.

## v6.0.1

Profile files are unchanged (byte-identical to v5.0.0 and v6.0.0); this release corrects metadata, packaging and tooling.

### Fixed

- Integrity gate now covers every release folder, including `releases/6.0.0`, and the service worker precache list.
- Status text no longer claims "device-tested"; all six builds remain `untested` until each is re-run.
- Light-theme contrast of the Recommended badge (a11y gate).
- Docs renderer: quotes, nested lists, rules, escaped table pipes.
- Service worker: no caching of downloads or `?p=` URLs, capped runtime cache, font caching, honest offline fallback.

### Changed

- Release folders use plain version names (`5.0.0`, `6.0.0`, `6.0.1`); archived file contents are untouched.
- Loose profile folders in `releases/` and `site/downloads/` now include `SETUP.txt`.
- Repository and site URLs come from `site.config.json`.
- CI: current action versions, Dependabot, pinned `ubuntu-24.04`, deploy gated on the full verify job.

## v6.0.0

### Added

- Responsive UI: desktop sidebar, tablet icon rail and mobile bottom sheet.
- Documentation site: Markdown rendered to `site/docs/`.
- Custom 404 page that keeps the `/HyperAudio/` base path.
- EEL2 runtime tests and response acceptance suites.
- CI: caching, concurrency cancellation and local link checking (`links.js`).
- Formatting tool `tools/fmt.py`.

### Changed

- Version badges, meta tags and footer text moved to v6.0.0.
- Repository structure separates backend testing from the frontend.
- Navigation consolidated into a shared `nav.js`.

### Unchanged

- All six profile files are byte-identical to v5.0.0; see `releases/6.0.0/DIFF.md`.

## v5.0.0

### Added

- Initial stable release with six RootlessJamesDSP profiles for the KZ EDX Pro and the Redmi 12.
- VDC with matched 44.1 and 48 kHz banks.
- Limiter with a 1.5 ms lookahead and a true-peak guard.
