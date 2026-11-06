# Evidence
Three tiers, never mixed on the site:
1. **Offline, automated** (`releases/<v>/acceptance.json`, produced by `build/build.py`): file validity, VDC banks/sections, IRS format and peak vs metadata, EEL static lint. Status is `pass`, `fail` or `not_run`.
   `not_run` today: eel.compile, limiter.ceiling, response_error, tail, cpu, nan_soak. They need an EEL runtime and the test harness, which are not in the repo yet. They are listed, not faked.
2. **Device-reported** (`docs/evidence/device-tests.json`): one entry per build, device, date, result.
3. **Acoustic measurement**: none yet. Site keeps saying "calculated".

Entry schema: `{"release","build","device","date","test","result":"pass|fail|untested","notes"}`.
Legacy v5 claims ("IEM passed") are recorded as `untested` per build until re-run individually.
