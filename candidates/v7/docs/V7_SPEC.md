# HyperAudio v7 DSP: release specification (draft for agreement)

Status: **draft, nothing built yet.** Evidence class for everything below: **calculated** (numpy/scipy, `eel2py` subset interpreter). Device tests: **untested**. Acoustic measurement: **none**.

## 1. Scope (agreed)
- First v7 pair: **KZ EDX Pro · HD** (IEM, current recommended default) and **Redmi 12 · Protection V6** (speaker, current safe default).
- The other four profiles follow the same recipe only after the pair is frozen.
- Speaker boost cap stays **+8 dB**. One shared limiter core for every profile. File names unchanged; the version lives in bundle, docs and release.

## 2. Definition of "release grade"
A profile is release grade when **all** of these hold, with the numbers recorded in `data/evidence.json`:

| Area | Gate |
|---|---|
| Reproducibility | `generator/` rebuilds every shipped file byte-for-byte from pinned inputs; hashes checked in CI |
| IRS format | 4 ch, finite, 32-bit float, 48 kHz, sample peak <= 0.95 |
| IRS size | L1 per channel <= 1.25, no exceptions (Protection V6's 2.24 is either removed or renormalised) |
| IRS tail | below -80 dB with margin; file trimmed to the needed length |
| Chain gain | max (LL+LR) x VDC = -0.50 dB for IEM; speaker per its +8 dB cap rule |
| VDC | 10 sections per bank, both 44.1 and 48 kHz, max pole radius <= 0.985 |
| 44.1 vs 48 kHz | responses agree within 0.1 dB over 20 Hz to 16 kHz |
| Coefficients | 9-decimal rounding changes the response < 0.05 dB |
| Limiter | one shared core; sample peak never above ceiling; true-peak overshoot <= 0.5 dB on tones and on broadband noise; no NaN/Inf soak failures |
| Limiter cross-check | numpy reference of the same algorithm agrees with the EEL on `eel2py` output |
| EEL | no `while`/`&`; lint clean; slider defaults documented; per-sample cost estimate stated as an estimate |
| Docs | every claim in the docs maps to a gate above; unmeasured items stay listed in LIMITS/OPEN |

Not part of the gate (cannot be done here): acoustic measurement, device CPU, speaker excursion and thermal limits. Listening notes from the author are recorded as **reported**, never as measured.

## 3. Work order
1. Agree this spec.
2. Put the generator in the repo and reproduce v5 HD and SPK V6 byte-for-byte (baseline).
3. Shared limiter core v7 + its tests (reference implementation first).
4. VDC refit with joint 44.1/48 kHz design.
5. IRS rebuild/renorm under the single gate.
6. Candidate bundles + calculated A/B report against v5 (frequency response, gain, limiter behaviour).
7. Author listening; fixes; freeze v7.0.0 for the pair.
8. Repeat the recipe for the other four profiles.

## 4. Decisions (settled by research; evidence label: reported, not measured)
1. Overshoot gate: true-peak overshoot <= 0.5 dB on tones AND noise (v5 noise +1.9 dB fails; design target ~0.2 dB). Sample peak never above ceiling.
2. Default ceiling: keep -1.5 dBFS (ceilDb10 -15). Common guidance is -1 dBTP (EBU R128 / streaming); -1.5 adds margin for codec and DAC overshoot, and v5 already ships it, so no loudness change.
3. Target curves: keep v5 targets; v7 changes engineering only.
   - IEM target is already Harman-IE-family: +7 dB bass shelf, +9 dB at 3 kHz, -8.5 dB at 16 kHz (re 1 kHz).
   - Community evidence: Harman IE 2019v2 and SoundGuys preferred equally (72%) in a 2024 Olive study (B&K 5128); New Meta/JM-1 not tested head-to-head. No curve is proven best; bass/treble are trade-offs.
   - Known caveats of Harman 2019: ~250 Hz dip, 3-8 kHz can sound bright. Offer as a future optional trim (not in v7.0.0).
   - Speaker: no standard target exists; keep custom target and +8 dB cap.
