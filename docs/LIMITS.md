# Limits

What the shipped profiles do not do. v6.1.0 ships the v5.0.0 profile files with only the 44.1 kHz bank of four VDCs refitted, so every other limit below still applies.

| Area | Limit | Plan |
|---|---|---|
| Speaker | +8 dB boost cap; curves sit about 2 dB under target on average at 100 to 2000 Hz, and about 12 dB under near 500 Hz at worst | Raise the cap only if a device test passes |
| Protection V6 | IR peak 2.24 against the L1 gate of 1.25 | Redesign the IR or document the exception |
| Limiter | True-peak overshoot of about +0.19 dB | Tighten only if it is audible or clips |
| 44.1 kHz bank | 0.01 to 0.20 dB from the 48 kHz bank (calculated) | Refit shipped in 6.1.0, see [the refit report](refit44_report.md); checked by the author by ear on a 44.1 kHz file, not measured. Other sample rates have no bank, and behaviour there is unverified |
| Profile EEL (Pop, EDM) | Unstable, not shipped | Root-cause it, then device-test |
| Evidence | No acoustic measurements; device results are unspecific | See [Evidence](EVIDENCE.md) |

Everything still unfinished, and what each item needs, is in [Open items](OPEN.md).
