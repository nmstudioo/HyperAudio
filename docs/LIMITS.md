# Limits

What the shipped v7.0.0 profiles do not do. Everything here is calculated or offline-checked; nothing is device-tested.

| Area | Limit | Plan |
|---|---|---|
| Speaker | +8 dB boost cap; curves sit about 2 dB under target on average at 100 to 2000 Hz, and about 12 dB under near 500 Hz at worst | Raise the cap only if a device test passes |
| Limiter | Shared v7 core: worst 8x true-peak overshoot +0.25 dB on tones and +6 dB noise (calculated, eel2py). One gate for everything that ships: <= 0.5 dB on both | Device and CPU validation; EEL-vs-reference cross-check is not automated |
| 44.1 kHz bank | 0.01 to 0.20 dB from the 48 kHz bank (calculated) | Refit shipped in 6.1.0, see [the refit report](refit44_report.md); checked by the author by ear on a 44.1 kHz file, not measured. Other sample rates have no bank, and behaviour there is unverified |
| Profile EEL (Pop, EDM) | Unstable, not shipped | Root-cause it, then device-test |
| Evidence | No acoustic measurements; device results are unspecific | See [Evidence](EVIDENCE.md) |

## Release gates

Every shipped profile must pass these (calculated; `build/verify.py`):

| Gate | Limit |
|---|---|
| IRS L1 norm | <= 1.25 |
| IRS peak | <= 0.95 |
| IRS tail | -80 dB reached before the end |
| VDC pole radius | <= 0.985 (and < 1.0 stable) |
| 44.1 vs 48 kHz bank | <= 0.3 dB |
| Chain max gain | <= 0 dB |
| Limiter true-peak overshoot | <= 0.5 dB, tones and noise |

Everything still unfinished, and what each item needs, is in [Open items](OPEN.md).
