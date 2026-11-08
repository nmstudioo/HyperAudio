# v7 release candidates (v7.0.0-rc.1) — NOT promoted
Nothing in src/profiles is changed. Evidence: calculated only; device and listening: untested.

## 1. Shared limiter core v7 (all six profiles) — candidates/v7/eel/
16-tap Kaiser(4) true-peak detector, centre-aligned, 1.5% guard, latency 79 samples. Worst 8x true-peak overshoot +0.25 dB (v5 +1.7..+1.95 dB); sample peak never above ceiling. See build/v7/ and candidates/v7/docs/V7_REPORT.md.

### Gate scope
The shipped v5 EELs are checked by the release build against their recorded v5 baseline (tones 0.35 dB, broadband noise 2.5 dB). The strict v7 candidate gate remains 0.5 dB for both tones and noise and is run against all six files in `candidates/v7/eel/` by `python3 tests/gate_v7_limiter.py`. This separates generations; it does not relax the v7 candidate requirement.

## 2. IEM HD target candidates — candidates/v7/iem-hd/
Same IRS and fitter; only the target differs. A = Harman IE 2019, B = JM-1 (renormalised at 1 kHz), C = v5 target (byte-identical VDC/IRS to src/profiles/iem-hd).
All three pass tests/gate_candidate.py (IRS peak 0.694, L1 1.071, tail -80 dB; poles <= 0.969; banks 0.03-0.05 dB; chain -0.50 dB; limiter gates).
Level-match for blind listening (calculated, A-weighted 100 Hz-10 kHz): preGain10 A -2, B +21, C 0 (tenths of dB). Verify by ear.

## 3. Promote (after listening)
cp candidates/v7/iem-hd/<winner>/EDX_HD.{irs,vdc,eel} src/profiles/iem-hd/ ; cp candidates/v7/eel/<other profiles>.eel src/profiles/<dir>/ ; run python3 build/stamp.py ; python3 check.py

Docs: docs/V7_SPEC.md (gates and decisions), docs/V7_PLAN.md (audit + method), docs/V7_REPORT.md (results + listening protocol), all under candidates/v7/docs/.

## 4. Speaker Protection V6 candidate — candidates/v7/spk-v6/ (calculated only)
Same tuning as v5 (target = the v5 chain response; deviation 0.11 dB rms, 0.37 dB max, 100 Hz-16 kHz; +8 dB boost cap unchanged). Structure changed so the gates hold:
IRS L1 1.20 (v5 2.24: documented exception removed), max pole 0.976 (v5 0.993), 44.1/48 kHz banks 0.03 dB, chain max -0.50 dB, tail -80 dB at frame 1340. All of tests/gate_candidate.py passes (v5 V6 fails irs.l1 and vdc.stable under the same gates).
Trade-offs: the IRS is 6.7 dB quieter and the VDC makes the level up (+6.2 dB gain, VDC max +8.4 dB), so the signal between VDC and convolver reaches 2.7x the input peak (calculated, coloured noise). This assumes the effect chain is floating point with no clamp between VDC and convolver: UNTESTED on device. Time-domain residual vs v5: -18 dB (magnitude within 0.37 dB; phase differs). Regenerate: build/v7/generator/build_spk_v7.py <out>.
