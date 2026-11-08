# HyperAudio v7 — Initial Plan (Harman IE 2019 vs JM-1)

Evidence labels: measured / calculated / reported / untested. No device or acoustic measurement is possible here.

## 1. Audit of HyperAudio_v7_Master_DSP_Suite.zip
| Item | Finding |
|---|---|
| 4 measurement CSVs | Usable. `KZ_EDX_Pro_raw_RikudouGoku.csv` is byte-identical in values to our repo raw. Harman IE 2019 and 5128 DF look genuine (reported source data). |
| JM-1 CSV | Different format (482 pts, `* Freq, SPL` header) and not normalised to 1 kHz (+1.62 dB there). Must be re-normalised before use. |
| 6 profile trios (V4, V10, SPK V6/V8/V10) | Byte-identical to repo v5. Nothing new. |
| iem_hd | EEL swapped for a new limiter; VDC differs ONLY in section 1 b0-b2 (about -4.3 dB scaling, both banks). Not a refit. Gate run: chain max -4.80 dB vs -0.50 target = FAIL. |
| iem_ghd | Same as repo candidate. |
| build/generate_dsp.py | 110-line stub: biquad helpers + `main()` that only prints text. Produces no profile. |
| data/evidence.json | Claims (pole 0.9846, 0.038 dB RMS, 0.0 dB overshoot, "ADB verified", "Hardware Verified", JM-1 profile "PASSED") have no generator or data behind them, and no JM-1 profile exists in dsp/. Treat as unverified. |
| SHA256SUMS | Paths do not match the zip layout (43 lines fail to open). |
Verdict: keep the 4 CSVs and the biquad helper idea. Discard evidence.json and the claimed results.

## 2. Findings that shape the decision
- Our current KZ target is NOT stock Harman. At 100 Hz it is +4.0 (Harman 2019: +2.8, JM-1: +1.9); at 5 kHz it is +5.0 (Harman +7.7, JM-1 +6.5); at 16 kHz -8.5 (Harman -10.2). It is a trimmed Harman: more bass, calmer 4-8 kHz.
- Rig: raw is on an IEC 711 coupler (reported by you, not independently verified). Harman IE 2019 is also 711, so A is like-for-like. JM-1 is defined on B&K 5128; the CSV's rig/conversion is unstated (its 3 kHz and 16 kHz values look 711-like, not 5128-like, but this is unconfirmed). B needs source confirmation before it is a fair comparison.
- Community evidence (reported): 2024 Olive study, Harman IE 2019 ~ SoundGuys (72% each); JM-1 not tested head-to-head. No proof either is better.

## 3. Data to gather (step 0)
1. Rig and calibration of the raw file (RikudouGoku database page / notes). Fallback: Reference Audio Analyzer measurement (different rig) as a cross-check.
2. Second independent KZ EDX Pro measurement; check unit-to-unit spread. Spread above 1.5 dB at some frequency = do not fit that band tightly.
3. JM-1 source file and its stated tilt and normalisation; Harman IE 2019v2 original.
4. Redmi 12 speaker raw: our own measurement only; no standard target exists.
Each file gets: source URL, date, rig, normalisation, SHA256, in `data/SOURCES.md`.

## 4. Build principles
1. Reproducible: one generator in repo; same inputs give byte-identical files; CI check.
2. Target and raw on the same rig and same 1 kHz normalisation, or no fit.
3. Fit to a smoothed target (1/6 oct); correct only minimum-phase-safe features; no boost above a cap; narrow notches only where two measurements agree.
4. Stability: pole radius <= 0.985; 44.1 and 48 kHz banks within 0.1 dB (20 Hz-16 kHz).
5. Chain: max (LL+LR)*VDC = -0.5 dB for IEM; IRS L1 <= 1.25, peak <= 0.95, tail <= -80 dB.
6. One shared limiter core; must pass numpy reference cross-check; overshoot <= 0.5 dB on tones and noise; ceiling -1.5 dBFS.
7. Gates are executable (tests/gate_candidate.py). Nothing is labelled passed without a run.

## 5. Decision method (Harman vs JM-1)
- Build three calculated candidates from one pipeline: A = Harman IE 2019 exact, B = JM-1 (re-normalised, same bass shelf level as A), C = v5 target (control).
- Calculated report: curve differences in dB per band, headroom needed, limiter engagement on a test set.
- Blind A/B/C by you (reported): same track set, level-matched within 0.5 dB using the chain gain, 3 sessions, notes on bass, 3-8 kHz brightness, fatigue.
- Default recommendation before listening: A as HD default (best study support, matches AutoEQ/community EQ), B as an alternate profile. Final choice by your listening.

## 6. Steps
0 Gather and document data (above). 1 Generator + reproduce v5 HD and SPK V6 byte-for-byte. 2 Shared limiter v7 + reference check. 3 Candidates A/B/C. 4 Gates + calculated A/B report. 5 Your listening. 6 Freeze v7.0.0 pair. 7 Other four profiles. 8 UI.

## 7. Answered
- Rig: IEC 711 (per you). Blind A/B/C listening: yes.
- Still open: JM-1 file provenance (which rig/conversion).
