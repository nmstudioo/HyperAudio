# Profile EEL (`EDX_Profiles.eel`)

**Suspects only; none confirmed.** Keep it out of releases until the symptom is known and a device test passes.

## Suspects

1. **Slider variables are overwritten.** `@init` overwrites slider variables (profile = 4 against a slider default of 1, intensity, trims, ceiling). Remove those lines.
2. **Crossover states are stale.** States `p1L..q2R` are not reset on activation and are not updated while bypassed, and the reset list names stale variables (`xa1L..`, `sl1..`). Reset the p/q states on activation.
3. **Band-gain ripple at 180 Hz.** A Butterworth-4 Q pair with `hi = x - lo` ripples when band gains differ, which would pump on Pop and EDM.
