# Releasing

1. Bump `VERSION`; edit `src/profiles.meta.json` (`released`) and `docs/CHANGELOG.md` (a `vX.Y.Z` heading).
2. `python3 build/build.py` builds `releases/<ver>/`, publishes to `site/`, and stamps the version into `site/index.html`, `site/data/versions.json` and `site/sw.js`.
3. `python3 build/docs_site.py && python3 tests/check.py` must print `all checks passed`.
4. Review `releases/<ver>/DIFF.md` and `acceptance.json` (0 failures; `warn` and `not_run` entries stay visible).
5. `python3 build/freeze.py`, commit, merge to `main` (Pages deploys), then `git tag v<ver> && git push --tags`.
6. The `release` workflow checks the tag against `VERSION`, rebuilds, requires the frozen hashes to match, and publishes a GitHub Release with the zips, `SHA256SUMS.txt`, `acceptance.json` and `DIFF.md`.

A frozen release is never rebuilt in place: `build.py` refuses, and `tests/check.py` fails if its `SHA256SUMS.txt` changes.
