# v7 release candidates (v7.0.0-rc.1) — NOT promoted
Nothing in src/profiles is changed. Evidence: calculated only; device and listening: untested.

## 1. Shared limiter core v7 (all six profiles) — candidates/v7/eel/
16-tap Kaiser(4) true-peak detector, centre-aligned, 1.5% guard, latency 79 samples. Worst 8x true-peak overshoot +0.25 dB (v5 +1.7..+1.95 dB); sample peak never above ceiling. See build/dsp/ and candidates/v7/docs/V7_REPORT.md.

## 2. IEM HD target candidates — candidates/v7/iem-hd/
Same IRS and fitter; only the target differs. A = Harman IE 2019, B = JM-1 (renormalised at 1 kHz), C = v5 target (byte-identical VDC/IRS to src/profiles/iem-hd).
All three pass tests/gate_candidate.py (IRS peak 0.694, L1 1.071, tail -80 dB; poles <= 0.969; banks 0.03-0.05 dB; chain -0.50 dB; limiter gates).
Level-match for blind listening (calculated, A-weighted 100 Hz-10 kHz): preGain10 A -2, B +21, C 0 (tenths of dB). Verify by ear.

## 3. Promote (after listening)
cp candidates/v7/iem-hd/<winner>/EDX_HD.{irs,vdc,eel} src/profiles/iem-hd/ ; cp candidates/v7/eel/<other profiles>.eel src/profiles/<dir>/ ; run python3 build/stamp.py ; python3 check.py

Docs: docs/V7_SPEC.md (gates and decisions), docs/V7_PLAN.md (audit + method), docs/V7_REPORT.md (results + listening protocol), all under candidates/v7/docs/.

## 4. Speaker candidates V6 / V8 / V10 — candidates/v7/spk-v6, spk-v8, spk-v10 (calculated only)
Method (build/generator/build_spk_fold.py): VDC sections 0 (110 Hz protection high-pass) and 1 (low shelf) hold the 0.990 poles. They are folded into the IRS by convolution (exact LTI reordering); the VDC keeps its remaining sections; the 44.1 kHz bank is refitted to the 48 kHz response.
Result: 48 kHz chain identical to the shipped profile (0.0 dB deviation; time-domain residual -150 dB on coloured noise); max pole 0.971 / 0.980 / 0.979 (shipped 0.993 / 0.990 / 0.990); bank 44.1 vs 48 kHz 0.017 / 0.000 / 0.000 dB; tuning, +8 dB boost cap and chain gain unchanged.
V6 only: IRS L1 2.24 -> 1.20 by scaling the IRS by 0.496 and making up +6.1 dB in the VDC (documented L1 exception removed). V8 and V10 IRS L1 stay about 1.0.
Replaces the rc.2 V6 candidate (a refit with 0.37 dB maximum deviation).
Untested assumption: the effect chain is floating point with no clamp between VDC and convolver (V6 intermediate peak is 2.0x the input peak, calculated).

## 5. IEM V4 / V10 — candidates/v7/iem-v4, iem-v10
Shipped 6.1.0 IRS and VDC, unchanged, plus the v7 limiter. They already pass every gate (bank 0.004 / 0.005 dB after the 6.1.0 refit). Promotion = copy the .eel.

Gate results for all six: GATES.md.
