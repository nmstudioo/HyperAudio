# Changelog

What changed in each version, newest first. Profile files are frozen per release; v6.0.0 changed tooling, tests, docs and the site, not the profiles.

## Unreleased (v7 work)

### Added

- Single version source: `build/stamp.py` stamps `VERSION` into `index.html`, `versions.json` and `sw.js`; CI fails on stale stamps.
- Release automation: a `vX.Y.Z` tag runs `.github/workflows/release.yml` (GitHub Release with zips, checksums, acceptance and diff); `build/freeze.py` and a FROZEN hash guard.
- Offline support: a service worker (network first, cache fallback).
- Accessibility gate: `tests/a11y.js` (built-in checks plus axe-core in CI).
- Evidence panel: a per-profile check matrix generated from `acceptance.json` into `site/data/evidence.json`.

### Changed

- Docs pages redesigned: shared navigation, section tabs, table of contents, code blocks with copy buttons, previous and next links.

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
