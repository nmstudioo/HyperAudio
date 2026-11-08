# generator (step 1 of v7)

Rebuilds the v5 VDC/IRS files from inputs/. Result (numpy 2.5.3, scipy 1.18.1, Python 3): 12 of 12 files byte-identical to src/profiles (calculated, reproducible; two runs identical).

    python3 build_v5.py out/            # writes out/<profile>/*.vdc|*.irs + report.json
    python3 repro_check.py out/ <repo>  # SHA-256 compare against <repo>/src/profiles

Inputs: inputs/v4/* (v4 IRS/VDC bases, 10 files; the IRS bases are inputs, not derived from raw HRIR here), inputs/data/{Raw,target} (KZ EDX Pro and Redmi 12 raw + target).
Limits: byte equality depends on numpy/scipy versions (floating point). EEL limiter is not generated here yet (step 2).
