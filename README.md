# HyperAudio

Browser tool that builds QA-checked convolver impulse responses, EEL2 Liveprog scripts and Viper DDC files for RootlessJamesDSP. Targets: KZ EDX Pro (IEM) and Xiaomi Redmi 12 (loudspeaker). All processing runs locally in the browser.

**Live:** `https://<username>.github.io/<repo>/`

## Layout

```
index.html          markup
css/style.css       styles
js/engine.js        DSP engine, fitter, WAV audit, self-tests
js/ui.js            workspace UI and event binding
assets/eel/         4 Liveprog scripts
assets/ddc/         2 Viper DDC files
tests/              Node checks run in CI (jsdom)
.github/workflows/  test, then deploy to Pages
```

## Setup per device

| Part | IEM | Speaker |
| --- | --- | --- |
| Convolver impulse (generated) | KZ Edx Pro profiles | Redmi 12 Speaker |
| Liveprog, after the convolver | IEM HyperAudio™ Master v2.0.eel | Speaker HyperAudio™ Master v2.0.eel |
| DDC | IEM HyperAudio™ DDC.vdc | Speaker HyperAudio™ DDC.vdc |

Chain order is convolver, then Liveprog: the impulse does the EQ, the script does dynamics and safety. Limiter ceilings are fixed in `CEIL` (`js/engine.js`): -1.0 dBFS IEM, -0.5 dBFS speaker. The page checks that the Master v2.0 scripts carry those values on load.

`S+ IEM HyperAudio™ Master.eel` and `S+ Speaker HyperAudio™ Master.eel` are standalone, for use outside the setup above.

## Run locally

Assets are fetched, so opening `index.html` by double-click will not work. Serve the folder:

```
python3 -m http.server 8000
```

## Tests

```
cd tests
npm ci
npm test
```

Checks: self-tests, asset files and ceilings, unique IDs, all 6 profiles at 44.1 and 48 kHz, fitter, and the exact download names.

## Publish

Settings → Pages → Source: **GitHub Actions**. Every push to `main` runs the tests and deploys only if they pass.

## Scope

QA is browser-side math on the exact exported file. It does not test native RootlessJamesDSP behavior. Headroom is the peak sine-wave gain, not a bound for arbitrary broadband peaks. Device evidence in the page is operator-reported, not independent certification.

## Licence

See `LICENSE` (placeholder, all rights reserved until replaced).
