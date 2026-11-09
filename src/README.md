# src

Source profiles and metadata. `build/build.py` reads from here.

| Path | Holds |
|:--|:--|
| `profiles/<id>/` | The current VDC, IRS, EEL and `SETUP.txt` (`{{VERSION}}` is substituted) |
| `profiles.meta.json` | The copy, stats and curves for every profile |
| `dsp/refit44.py` | The 44.1 kHz refit tool; see the [refit report](../docs/refit44_report.md) |

## Generators

The fit library and generators live in `build/generator/` (see its README). They are not yet wired into CI for the v7 files.

See [Open items](../docs/OPEN.md) for what is still unfinished.
