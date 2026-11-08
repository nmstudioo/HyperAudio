# src

Source profiles and metadata. `build/build.py` reads from here.

| Path | Holds |
|:--|:--|
| `profiles/<id>/` | The current VDC, IRS, EEL and `SETUP.txt` (`{{VERSION}}` is substituted) |
| `profiles.meta.json` | The copy, stats and curves for every profile |
| `dsp/refit44.py` | The 44.1 kHz refit tool; see the [refit report](../docs/refit44_report.md) |

## Missing

The DSP sources were not in the v5 site archive: the fit library, the EEL generator, the target and the raw data. Add them under `src/dsp/` and have them write into `src/profiles/` before `build/build.py`, so the build stays one command.

See [Open items](../docs/OPEN.md) for what each missing piece blocks.
