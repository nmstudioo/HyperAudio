# Releasing

How a version is built, frozen and published. A frozen release is never rebuilt in place.

## Steps

1. Run `python3 build/build.py --write-stats` once to refresh stored stats from the files (numpy; CI-class machine). Bump `VERSION`; edit `src/profiles.meta.json` (`released`) and `docs/CHANGELOG.md` (a `## vX.Y.Z` heading).
2. Run `python3 tools/ship.py --release`. It builds `releases/<ver>/` with runtime acceptance, regenerates the derived site files, freezes the release and runs the gate. It must end with `all checks passed`.
3. Review `releases/<ver>/DIFF.md` and `acceptance.json`. There must be 0 failures; `warn` and `not_run` entries stay visible.
4. Commit and merge to `main` (Pages deploys). Then tag `vX.Y.Z` and push the tag.
5. The `release` workflow checks the tag against `VERSION`, checks the tag is on `main`, rebuilds, requires the frozen hashes to match, and publishes a GitHub Release with the zips, `SHA256SUMS.txt`, `acceptance.json` and `DIFF.md`.

To build on GitHub instead of locally, run the `release` workflow by hand with the version; it runs the same command and pushes a `release/vX.Y.Z` branch. Open the pull request yourself so CI runs on it.

## Commands

python3 tools/ship.py            # regenerate derived files, then gate (before every commit)
python3 tools/ship.py --release  # full build, regenerate, freeze, gate
git tag v<ver> && git push --tags

## Guards

- `build.py` refuses to rebuild a release that has a `FROZEN` file.
- `tests/check.py` fails if a frozen release's `SHA256SUMS.txt` changes.
- The release notes are the `## v<ver>` section of [the changelog](CHANGELOG.md), so write it before you tag.
