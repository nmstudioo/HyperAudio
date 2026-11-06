# src/
`profiles/<id>/` holds the current VDC, IRS, EEL and SETUP.txt (`{{VERSION}}` is substituted), `profiles.meta.json` the copy, stats and curves.
**Missing:** DSP sources (fit library, EEL generator, target and raw data) were not in the v5 site archive. Add them under `src/dsp/` and have them write into `src/profiles/` before `build/build.py`; the build then stays one command.
