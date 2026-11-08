# v7 release candidates (v7.0.0-rc.1) — NOT promoted
Nothing in src/profiles is changed. Evidence: calculated only; device and listening: untested.

## 1. Shared limiter core v7 (all six profiles) — candidates/v7/eel/
16-tap Kaiser(4) true-peak detector, centre-aligned, 1.5% guard, latency 79 samples. Worst 8x true-peak overshoot +0.25 dB (v5 +1.7..+1.95 dB); sample peak never above ceiling. See build/v7/ and candidates/v7/docs/V7_REPORT.md.

## 2. IEM HD target candidates — candidates/v7/iem-hd/
Same IRS and fitter; only the target differs. A = Harman IE 2019, B = JM-1 (renormalised at 1 kHz), C = v5 target (byte-identical VDC/IRS to src/profiles/iem-hd).
All three pass tests/gate_candidate.py (IRS peak 0.694, L1 1.071, tail -80 dB; poles <= 0.969; banks 0.03-0.05 dB; chain -0.50 dB; limiter gates).
Level-match for blind listening (calculated, A-weighted 100 Hz-10 kHz): preGain10 A -2, B +21, C 0 (tenths of dB). Verify by ear.

## 3. Promote (after listening)
cp candidates/v7/iem-hd/<winner>/EDX_HD.{irs,vdc,eel} src/profiles/iem-hd/ ; cp candidates/v7/eel/<other profiles>.eel src/profiles/<dir>/ ; run python3 build/stamp.py ; python3 check.py

Docs: docs/V7_SPEC.md (gates and decisions), docs/V7_PLAN.md (audit + method), docs/V7_REPORT.md (results + listening protocol), all under candidates/v7/docs/.
