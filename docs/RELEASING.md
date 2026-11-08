# Releasing

How a version is built, frozen and published. A frozen release is never rebuilt in place.

## Steps

1. Bump `VERSION`; edit `src/profiles.meta.json` (`released`) and `docs/CHANGELOG.md` (a `vX.Y.Z` heading).
2. Run `python3 build/build.py`. It builds `releases/<ver>/`, publishes to `site/`, and stamps the version into `site/index.html`, `site/data/versions.json` and `site/sw.js`.
3. Run `python3 build/docs_site.py && python3 tests/check.py`. It must print `all checks passed`.
4. Review `releases/<ver>/DIFF.md` and `acceptance.json`. There must be 0 failures; `warn` and `not_run` entries stay visible.
5. Run `python3 build/freeze.py`, commit, and merge to `main` (Pages deploys). Then tag and push.
6. The `release` workflow checks the tag against `VERSION`, rebuilds, requires the frozen hashes to match, and publishes a GitHub Release with the zips, `SHA256SUMS.txt`, `acceptance.json` and `DIFF.md`.

## Commands

```
python3 build/build.py
python3 build/docs_site.py && python3 tests/check.py
python3 build/freeze.py
git tag v<ver> && git push --tags
```

## Guards

- `build.py` refuses to rebuild a release that has a `FROZEN` file.
- `tests/check.py` fails if a frozen release's `SHA256SUMS.txt` changes.
- The release notes are the `## v<ver>` section of [the changelog](CHANGELOG.md), so write it before you tag.
