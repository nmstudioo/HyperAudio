# Limits (open in v5.0.0)
| Area | Limit | v6 plan |
|---|---|---|
| Speaker | +8 dB boost cap; curves sit about 2 dB under target on average at 100-2000 Hz (worst about 12 dB near 500 Hz) | Raise cap only if device test passes |
| Protection V6 | IR peak 2.24 vs L1 gate 1.25 | Redesign IR or document exception |
| Limiter | True-peak overshoot ~+0.19 dB | Tighten only if audible/clipping |
| 44.1 kHz bank | ~1.6 dB from 48 kHz bank at 20 kHz | Candidate in candidates/v6 (docs/refit44_report.md); gap 1.4-1.6 dB -> <=0.2 dB |
| Profile EEL (Pop, EDM) | Unstable, not shipped | Root-cause, then device test |
| Evidence | No acoustic measurements; device results unspecific | See EVIDENCE.md |
