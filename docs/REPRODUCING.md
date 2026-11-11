# Reproduce

Rebuild every release artifact from source and verify it against the published checksums.

## Rebuild

```
python3 build/build.py --out /tmp/rel        # rebuild into a scratch directory; never overwrites a frozen release
version=$(cat VERSION)
diff "/tmp/rel/SHA256SUMS.txt" "releases/$version/SHA256SUMS.txt" && echo identical
python3 build/build.py --publish             # copy releases/ into site/downloads/ for local serving
python3 tests/check.py        # hashes, links, JS syntax, rebuild parity
```

## Verify

```
cd releases && sha256sum -c 7.0.0/SHA256SUMS.txt
```

Run it from `releases/` so the `7.0.0/` paths in the checksum file resolve. It covers each profile file; the zips are not listed.

## Frozen releases

Releases with a `FROZEN` file are never rebuilt in place. Zip bytes depend on the zip tool, so the check compares member-file hashes for frozen releases instead of the zip hashes.
