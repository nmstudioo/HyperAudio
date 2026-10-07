# RootlessJamesDSP EEL2 UI Control Reference

> **Purpose:** A practical, device-verified reference for generating Liveprog EEL2 scripts with reliable RootlessJamesDSP controls.
>
> **Scope:** UI parameter grammar, parser behavior, script structure, known pitfalls, and a reusable authoring checklist.
>
> **Verification status:** The behaviors documented here were observed from working `.eel` scripts loaded in RootlessJamesDSP on Android, including bundled and HyperAudio-authored scripts. Host-version and device-specific differences may still exist.

---

## Contents

1. [Quick-start rules](#quick-start-rules)
2. [Verified script examples](#verified-script-examples)
3. [How the parser behaves](#how-the-parser-behaves)
4. [Supported controls](#supported-controls)
5. [Parameter grammar](#parameter-grammar)
6. [Integer-step requirement](#integer-step-requirement)
7. [Label safety](#label-safety)
8. [Script structure](#script-structure)
9. [EEL2 execution model](#eel2-execution-model)
10. [UI grouping](#ui-grouping)
11. [Latency documentation](#latency-documentation)
12. [Universal template](#universal-template)
13. [Publishing checklist](#publishing-checklist)
14. [Performance guidance](#performance-guidance)
15. [Scope and limitations](#scope-and-limitations)

---

## Quick-start rules

For a reliable RootlessJamesDSP Liveprog script:

- Save the file with the exact `.eel` extension.
- Make the first line `desc: Script Title`.
- Put optional metadata on the second line as `//tags: ...`.
- Declare parameters before the first `@` section marker.
- Use integer step values for every parameter.
- Reassign every declared parameter in `@init`.
- Use only `@init` and `@sample` section markers.
- Do not use `@slider`, `@block`, or `@serialize`.
- Avoid `@` in comments before `@init`.
- Keep labels free of `:`, `(`, `)`, and `%`.
- Guard `srate` with a fallback value.
- Guard non-finite or extreme input samples.
- Clamp the final output to the intended ceiling.
- Keep per-sample processing bounded and inexpensive on low-power Android devices.

A compact valid skeleton is:

```eel
desc: HyperAudio Example
//tags: hyperaudio example liveprog

level10:0<-120,60,1>Master level 0.1 dB

@init
level10 = 0;
level = level10 / 10;
fs = srate > 0 ? srate : 48000;

@sample
!(abs(spl0) < 1e6) ? spl0 = 0;
!(abs(spl1) < 1e6) ? spl1 = 0;

spl0 = min(max(spl0, -1), 1);
spl1 = min(max(spl1, -1), 1);
```

---

## Verified script examples

The following scripts were loaded and observed on-device:

| Script | Source | Controls observed | Notes |
|---|---|---:|---|
| Viper Dynamic Bass | Bundled in RootlessJamesDSP | 2 sliders + 1 dropdown | A 19-option enum was confirmed working. |
| Joe0Bloggs DRX10K Compander | Bundled in RootlessJamesDSP | 6 sliders | Labels containing units and hyphens worked. |
| HyperAudio Test Bass | HyperAudio-authored | 4 sliders | Integer steps only. |
| HyperAudio Core IEM | HyperAudio-authored | 14 sliders | Used scaled-integer parameters. |
| HyperAudio Core Speaker | HyperAudio-authored | 17 sliders | The working version used integer steps throughout. |
| HyperAudio HAmaster Speaker | HyperAudio-authored | 22 sliders | Confirmed working previously. |

These observations support the parser and UI rules in this document.

---

## How the parser behaves

RootlessJamesDSP processes a Liveprog file in roughly this order:

```text
1. Discover files with the .eel extension.
2. Read the first line for the desc title.
3. Read optional //tags metadata.
4. Scan parameter declarations before the first @ section.
5. Build controls from valid parameter declarations.
6. Run @init once.
7. Run @sample once per audio frame.
```

### 1. File discovery

- The file must end in `.eel`.
- A `.txt` file is ignored by the Liveprog scanner.
- Be careful with operating systems that hide extensions. A file saved as `script.eel.txt` is not a valid Liveprog file.

### 2. Header parsing

The first line should be:

```eel
desc: HyperAudio Script Title
```

The title becomes the displayed script name.

Optional metadata can follow:

```eel
//tags: limiter iem safety
```

Tags are metadata and are not normally shown as UI controls.

### 3. Parameter scanning

Parameters are scanned before the first section marker. A declaration generally follows:

```eel
name:default<min,max,step>Label
```

Enum parameters use:

```eel
mode:0<0,2,1{Off,On,Auto}>Mode
```

### 4. Transactional control construction

A critical observed behavior is that an invalid parameter can prevent the complete parameter set from rendering. In particular, a non-integer step may cause the parameter construction process to fail and result in no visible sliders.

Treat the entire declaration block as transactional: validate every parameter before loading the script.

---

## Supported controls

RootlessJamesDSP exposes two observed control types.

### Slider

```eel
bass10:0<-60,60,1>Bass level 0.1 dB
```

The value is quantized by the integer step.

### Dropdown

```eel
mode:0<0,2,1{Off,On,Auto}>Processing mode
```

Dropdowns are triggered by enum options inside the angle-bracket range.

There is no verified built-in syntax for:

- Checkboxes
- Radio groups
- Group panels
- Read-only information rows
- Separate headings
- Rich layout widgets

To create visual grouping, use label prefixes and comments.

---

## Parameter grammar

The safest observed grammar is:

```text
name:default<min,max,step>Label text
```

Or:

```text
name:default<min,max,step{Option A,Option B,Option C}>Label text
```

### Parameter fields

| Field | Requirement |
|---|---|
| `name` | Identifier using letters, digits, and underscores; do not begin with a digit. |
| `default` | Integer inside the declared range. |
| `min` | Integer lower bound. |
| `max` | Integer upper bound greater than `min`. |
| `step` | Positive integer. |
| Options | Optional comma-separated enum labels inside `{}`. |
| Label | Plain text after `>`, using safe characters. |

### Valid examples

```eel
toneBass10:0<-20,20,1>Tone bass 0.1 dB
width10:10<0,20,1>Stereo width 0.1 ratio
mode:0<0,2,1{Off,On,Auto}>Processing mode
```

### Invalid or risky examples

```eel
// Decimal step. Avoid.
toneBass:0<-2,2,0.1>Tone bass

// Colon in label. Avoid.
mode:0<0,1,1>Universal: On off

// Parentheses in label. Avoid.
amount:0<0,100,1>Mix (percent)

// Percent symbol in label. Avoid.
amount:0<0,100,1>Mix %
```

---

## Integer-step requirement

The most important UI rule is:

> Use integer parameter steps.

A decimal step such as `0.1` may be accepted by the declaration scanner but rejected when the control is constructed. The observed symptom is that the complete parameter set may disappear, leaving no customizable parameters.

### Use scaled integers for precision

Instead of:

```eel
toneBass:0<-2,2,0.1>Tone bass
```

Use:

```eel
toneBass10:0<-20,20,1>Tone bass 0.1 dB
```

Then convert it in `@init` or during processing:

```eel
toneBass = toneBass10 / 10;
```

For hundredths:

```eel
mix100:25<0,100,1>Mix 0.01
mix = mix100 / 100;
```

This preserves fine control while keeping the UI step integer.

---

## Label safety

The label is everything after `>` on a parameter declaration. It is sanitized before display.

### Avoid these characters

| Character | Observed risk | Safer replacement |
|---|---|---|
| `:` | Can break label parsing. | Use a space or hyphen. |
| `(` | May drop the label or parameter. | Remove it. |
| `)` | May drop the label or parameter. | Remove it. |
| `%` | May be stripped or cause rejection. | Write `pct`. |
| `@` | Can be misread as a section marker in comments. | Write `at-sign`. |

### Safe label style

Prefer plain labels such as:

```eel
Tone bass 105 Hz 0.1 dB
Tone treble 6 kHz 0.1 dB
Space stereo width pct
Dynamics deesser amount pct
Dynamics compressor threshold dB
```

Hyphens, periods, commas, and slashes were tolerated, but simpler labels are safer.

### Label grouping

Because the UI is flat, use prefixes:

```text
Tone ...
Space ...
Dynamics ...
Safety ...
```

This creates a readable mental grouping without relying on unsupported layout widgets.

---

## Script structure

Use this order:

```text
[1]  desc: line
[2]  optional //tags: line
[3]  comments and parameter declarations
[4]  @init
[5]  parameter reassignments
[6]  derived values and constants
[7]  memory allocation
[8]  state initialization
[9]  @sample
[10] input guard
[11] processing
[12] output write and clamp
```

### Header

```eel
desc: HyperAudio KZ EDX Pro Limiter
//tags: hyperaudio iem limiter safety
```

Avoid an `author:` line unless you have verified that your target host uses it. It is unnecessary for reliable UI rendering.

### Parameter declarations

Declare all UI parameters before `@init`:

```eel
master10:0<-120,60,1>Master level 0.1 dB
toneBass10:0<-20,20,1>Tone bass 0.1 dB
mode:0<0,2,1{Off,On,Auto}>Processing mode
```

### `@init`

Reassign every declared parameter to its declared default:

```eel
master10 = 0;
toneBass10 = 0;
mode = 0;
```

Then calculate derived values, allocate arrays, and initialize states.

### `@sample`

Process one audio frame:

```eel
peak = max(abs(spl0), abs(spl1));
```

Read from `spl0` and `spl1`, process them, and write the final values back.

---

## EEL2 execution model

### Recognized sections

Use only:

```eel
@init
@sample
```

Observed guidance indicates that `@init` runs once at script load and `@sample` runs once per audio frame.

Do not use:

```eel
@slider
@block
@serialize
```

Avoid lines beginning with `@` in comments before the recognized sections.

### Functions

Functions use space-separated arguments:

```eel
function clampValue x lo hi (
  min(max(x, lo), hi);
)
```

Do not assume comma-separated function arguments.

### Conditionals

Use the observed ternary-style form:

```eel
condition ? (
  value = 1;
) : (
  value = 0;
);
```

### Loops

Examples:

```eel
loop(count,
  i += 1;
);
```

```eel
while (condition) (
  i += 1;
);
```

Use loops carefully inside `@sample`. A full sliding-window scan for every audio sample can consume substantial CPU on lower-power Android devices.

### Arrays and memory

Use numeric memory bases and explicit pointer allocation:

```eel
ptr = 0;
bufL = ptr;
ptr += bufferSize;
bufR = ptr;
ptr += bufferSize;
```

Access values by index:

```eel
bufL[index] = spl0;
value = bufL[index];
```

### Sample-rate guard

Always guard the host sample rate:

```eel
fs = srate > 0 ? srate : 48000;
```

### Input guard

Guard input samples before processing:

```eel
!(abs(spl0) < 1e6) ? spl0 = 0;
!(abs(spl1) < 1e6) ? spl1 = 0;
```

### Output clamp

Use a final safety clamp appropriate to the script:

```eel
spl0 = min(max(spl0, -ceilingLin), ceilingLin);
spl1 = min(max(spl1, -ceilingLin), ceilingLin);
```

---

## UI grouping

The UI is flat: there is no verified group-panel control. Use label prefixes instead.

```eel
Tone bass 105 Hz 0.1 dB
Tone treble 6 kHz 0.1 dB
Tone air 9.5 kHz 0.1 dB
Space stereo width pct
Space mono bass below Hz
Dynamics deesser amount pct
Dynamics compressor threshold dB
Safety ceiling dBFS
```

The prefix communicates the functional group while keeping the parameter parser simple.

### Fixed information

There is no verified read-only information row. Put fixed constants in comments:

```eel
// Fixed safety constants
// CEIL_DB -1.0
// LOOK_MS 1.5
// RELEASE_MS 120
```

Only the following are generally visible in the Liveprog UI:

1. The `desc:` title.
2. Parameter labels.
3. Interactive controls.

Comments are visible when the source is opened, not as controls.

---

## Latency documentation

Calculate latency from the host sample rate rather than hardcoding a sample count:

```eel
// Lookahead is 1.5 ms and follows the host sample rate.
LOOK_MS = 1.5;
limN = floor(LOOK_MS * 0.001 * fs + 0.5);
limN < 1 ? limN = 1;
```

Document fixed latency constants in comments. Do not try to display latency as a read-only UI row unless it is also intended to be an interactive parameter.

---

## Universal template

The following template demonstrates the supported parameter patterns and safe script structure.

```eel
desc: Universal EEL Template
//tags: template reference universal ui

// ============================================================
// UNIVERSAL EEL TEMPLATE
// Demonstrates supported controls and script structure.
// ============================================================

// ---------- BASIC SLIDER ----------
plainSlider:0<-100,100,1>Basic slider full range
steppedSlider:0<0,1000,50>Basic stepped slider step 50
narrowSlider:50<50,50,1>Basic fixed single value
wideSlider:0<-10000,10000,100>Basic wide step 100

// ---------- TOGGLE ----------
switchOn:1<0,1,1>Toggle on off default on
switchOff:0<0,1,1>Toggle on off default off

// ---------- ENUM DROPDOWN ----------
modeSmall:0<0,2,1{Off,On,Auto}>Dropdown three options
modeLarge:0<0,4,1{Very Low,Low,Medium,High,Very High}>Dropdown five options
modeDescriptive:0<0,3,1{Extreme Headphone,Common Earphone,Unknown Type}>Dropdown descriptive options

// ---------- GROUPED SLIDERS ----------
gainMaster10:0<-120,60,1>Master volume 0.1 dB
gainBass10:0<-60,60,1>Bass shelf 105 Hz 0.1 dB
gainMid10:0<-60,60,1>Mid shelf 1 kHz 0.1 dB
gainTreble10:0<-60,60,1>Treble shelf 6 kHz 0.1 dB
gainAir10:0<0,60,1>Air shelf 9.5 kHz 0.1 dB
freqLow:100<20,500,5>Frequency low Hz
freqHigh:5000<2000,20000,100>Frequency high Hz
compAmount:0<0,100,1>Compressor amount pct
compThreshold:-20<-60,0,1>Compressor threshold dB

// ---------- FIXED SAFETY CONSTANTS ----------
// CEIL_DB -1.0
// LOOK_MS 1.5
// RELEASE_MS 120

@init
// Reassign every parameter to its declared default
plainSlider = 0;
steppedSlider = 0;
narrowSlider = 50;
wideSlider = 0;
switchOn = 1;
switchOff = 0;
modeSmall = 0;
modeLarge = 0;
modeDescriptive = 0;
gainMaster10 = 0;
gainBass10 = 0;
gainMid10 = 0;
gainTreble10 = 0;
gainAir10 = 0;
freqLow = 100;
freqHigh = 5000;
compAmount = 0;
compThreshold = -20;

// Convert scaled integer values to real units
gainMaster = gainMaster10 / 10;
gainBass = gainBass10 / 10;
gainMid = gainMid10 / 10;
gainTreble = gainTreble10 / 10;
gainAir = gainAir10 / 10;

// Runtime sample rate
fs = srate > 0 ? srate : 48000;
PI2 = 2 * $PI;

@sample
// Input guard
!(abs(spl0) < 1e6) ? spl0 = 0;
!(abs(spl1) < 1e6) ? spl1 = 0;

// Pass-through demonstration
switchOn ? (
  gainLin = pow(10, gainMaster / 20);
  spl0 *= gainLin;
  spl1 *= gainLin;
);

// Final sample-peak clamp
spl0 = min(max(spl0, -1), 1);
spl1 = min(max(spl1, -1), 1);
```

### Template feature map

| Template item | Demonstrates |
|---|---|
| `plainSlider` | Basic slider with symmetric range |
| `steppedSlider` | Integer step larger than one |
| `narrowSlider` | Fixed-value declaration pattern |
| `wideSlider` | Wide range with a larger integer step |
| `switchOn` and `switchOff` | 0/1 toggle patterns |
| `modeSmall` | Three-option dropdown |
| `modeLarge` | Five-option dropdown |
| `modeDescriptive` | Multi-word enum labels |
| `gain*10` parameters | Prefix grouping and scaled integer precision |
| `freq*` parameters | Frequency controls using integer steps |
| `comp*` parameters | Dynamics controls |
| Comment block | Fixed-constant documentation |
| `@init` assignments | Required default reassignment pattern |
| Scale division | Integer-to-real conversion |
| `srate` guard | Host sample-rate fallback |
| Input guard | Non-finite/extreme input protection |
| Final clamp | Sample-peak output safety |

---

## Publishing checklist

Before publishing a script, verify every item:

### File and header

- [ ] File extension is exactly `.eel`.
- [ ] The first line is `desc: <title>`.
- [ ] The second line is `//tags: ...` or a safe comment/blank line.
- [ ] No accidental `.eel.txt` extension exists.

### Parameters

- [ ] Every parameter is declared before `@init`.
- [ ] Every step value is an integer.
- [ ] Every default is inside its range.
- [ ] Every range has `min < max`, unless the target host has verified fixed-value support.
- [ ] No parameter is duplicated.
- [ ] Every declared parameter is reassigned to its default in `@init`.
- [ ] Decimal precision uses scaled integers such as `gain10` or `mix100`.
- [ ] Enum options use safe comma-separated labels.

### Labels and sections

- [ ] Labels contain no colon `:`.
- [ ] Labels contain no parentheses `(` or `)`.
- [ ] Labels contain no percent sign `%`.
- [ ] Units are written safely, such as `dB`, `Hz`, and `pct`.
- [ ] Only `@init` and `@sample` are used.
- [ ] No comment before `@init` begins with an accidental `@` section marker.

### Runtime safety

- [ ] `srate` has a fallback.
- [ ] Inputs are guarded against non-finite or extreme values.
- [ ] Outputs are clamped to the intended safety ceiling.
- [ ] All persistent states are initialized.
- [ ] Array memory is allocated deliberately.
- [ ] Per-sample loops are bounded and performance-tested.
- [ ] No untested built-in is required for the core signal path.

### Performance

- [ ] The script is tested on the target Android device.
- [ ] CPU load is acceptable during continuous playback.
- [ ] The device does not become excessively hot during normal use.
- [ ] Audio remains free of crackles, dropouts, and buffer underruns.
- [ ] Optional high-cost processing is clearly separated from the low-CPU path.

---

## Performance guidance

A script can parse correctly and still be unsuitable for a low-power Android device.

### Avoid repeated full-window scans

This pattern is expensive inside `@sample`:

```eel
loop(L,
  // scan a complete history window
);
```

If it runs more than once per sample, CPU cost grows quickly as `L` increases. Prefer:

- One-pole envelope followers.
- Running sums.
- Ring buffers with incremental updates.
- Bounded state updates.
- Efficient moving-min/max helpers only after verifying them on the target host.
- Optional processing modes that can be disabled.

### Quality does not require redundant work

A high-quality limiter can use:

```text
linked stereo detection
+ peak hold
+ lookahead delay
+ attack/release gain smoothing
+ final safety clamp
```

without repeatedly rescanning the entire audio history for every sample.

### Target-device validation

Always test the complete chain on the intended device. Confirm:

- No audio crackle.
- No dropouts.
- No thermal runaway.
- No unacceptable battery drain.
- No audible zipper noise.
- No channel imbalance.
- No excessive limiter pumping.
- No unexpected delay.

---

## Scope and limitations

This reference documents observed UI parsing and script-structure behavior. It does not replace host-specific testing.

### Host versions

Behavior was observed against RootlessJamesDSP on Android during early 2026. Future versions may change parser behavior.

### Device-specific CPU

A script can load successfully and still be too heavy for a particular phone. Real-time CPU cost depends on sample rate, effect-chain complexity, buffer size, Android version, and device thermal state.

### DSP correctness

This document focuses on:

- UI controls
- Parameter grammar
- Script structure
- Parser pitfalls
- Basic runtime safety
- Performance considerations

It does not prove that a filter, limiter, crossover, or nonlinear processor is mathematically correct. Those require separate DSP analysis and target-device listening/measurement tests.

### Untested built-ins

The following built-ins were not directly exercised as part of these observations:

- `movingMinMaxProcess`
- `stftInit`
- `stftForward`
- `stftBackward`
- Other undocumented or host-version-specific functions

Refer to the relevant EEL VM documentation and bundled RootlessJamesDSP Liveprog scripts before using them in a release-critical path.

---

## Release principle

Use the smallest script that meets the audible and safety requirement.

A reliable HyperAudio script should be:

```text
parseable
+ controllable
+ numerically bounded
+ CPU-conscious
+ testable on the target device
+ easy for a user to understand
```

That combination is more valuable than a script that is merely complex.

## Credits

Research, device verification, script authoring, and documentation by Noushad Mostafa.

This reference was developed through hands-on testing with RootlessJamesDSP on Android and HyperAudio-authored Liveprog scripts.

**Reference version:** 1.0  
**Last verified:** October 2026
