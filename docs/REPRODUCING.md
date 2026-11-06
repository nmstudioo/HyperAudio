# Rebuild and verify
```
python3 build/build.py        # writes releases/<VERSION>/ and publishes to site/
python3 tests/check.py        # hashes, links, JS syntax, rebuild parity
cd site && sha256sum -c ../releases/v5.0.0/SHA256SUMS.txt   # from a dir where v5.0.0/ resolves
```
Frozen releases (`FROZEN` file) are never rebuilt in place. Zip bytes depend on the zip tool, so the check compares member-file hashes for frozen releases.
