# v7.0.0-rc.1 report (calculated; no device tests)
1. Generator: build/v7/generator rebuilds all 12 v5 VDC/IRS files byte-identically (numpy 2.5.3, scipy 1.18.1). `python3 build_v5.py out/ && python3 repro_check.py out/ <repo>`.
2. Limiter: see candidates/v7/README.md. Test metric fixed (edge ringing trimmed); tests/eel/limiter_tests.py gate 0.5 dB for tones and noise.
3. Target candidates A/B/C: build/v7/generator/build_cand.py <out> data/measurements; predicted responses in candidates/v7/iem-hd/predicted_response.csv.
   Predicted level vs C (calculated, includes chain gain): 20-100 Hz A -1.1 / B -5.9; 100-500 A -2.2 / B -4.6; 2-5 kHz A +0.5 / B -2.2; 10-16 kHz A -2.1 / B +0.3 dB.
4. Listening protocol (reported evidence once done): level-matched (preGain10 A -2, B +21, C 0), blind, 3 sessions, same tracks; note bass, 3-8 kHz brightness, fatigue; reply with the winner.
5. Not done: speaker V6 candidate, other four profiles, JM-1 source URL, device and phone CPU tests, Harman 250 Hz / 3-8 kHz trim.
