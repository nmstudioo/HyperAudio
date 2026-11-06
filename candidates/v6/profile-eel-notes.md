# Profile EEL (EDX_Profiles.eel), suspects, none confirmed
1. @init overwrites slider variables (profile = 4 vs slider default 1, intensity, trims, ceiling): remove those lines.
2. Crossover states p1L..q2R are not reset on activation or updated while bypassed; reset list names stale variables (xa1L.., sl1..): reset p/q states on activation.
3. Butterworth-4 Q pair with hi = x - lo: band-gain differences ripple at 180 Hz (pumping on Pop/EDM).
Keep out of releases until the symptom is known and a device test passes.
