# True-peak alignment (candidate, unreleased)
The 8-tap true-peak window is centred 3.5 samples behind the newest sample, so its request reaches the sliding minimum about 4 samples late.
Change in the shared limiter core: `L_N = L_D + 1;` -> `L_N = L_D + 5;` (moving-average length `L_D` unchanged; +0.08 ms latency at 48 kHz).
Python model of the core, ceiling -1 dB: 12 kHz tone +0.09 -> +0.05 dB over; fs/4 at 45 deg +0.05 -> +0.01 dB over; 997 Hz unchanged.
Not verified on the real EEL or device.
