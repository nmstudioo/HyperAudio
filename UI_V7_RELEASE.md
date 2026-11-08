# HyperAudio v7 UI update

This package is a frontend-only enhancement for the repository state at commit
`83ba68f2df87b32325c699f648ea948c4047e7ea` (8 November 2026). It does not
promote candidate DSP files, change VDC/IRS/EEL artifacts, or alter the stable
release number.

## What changes

- Makes the homepage device/profile selection the primary interaction and
  places predicted-response analysis after profile selection.
- Presents calculated per-profile metrics alongside each profile option.
- Adds a direct `Use this profile` link to the profile finder result.
- Constrains profile comparison to profiles for the same output device.
- Removes unqualified device-tested wording from the homepage evidence area and
  shared footer. Historical author reports remain distinct from per-build tests.
- Reads displayed release versions from generated profile metadata.
- Adds a coordinated responsive styling layer without replacing the existing
  vanilla-JavaScript stack or design tokens.
- Pre-caches the new CSS and JavaScript in the existing service worker so the
  enhancement remains available when the site is used offline.

## Safety boundaries

- `VERSION` remains `6.1.0` until a new DSP release is formally promoted.
- `src/profiles/`, `releases/`, and `site/downloads/` are not modified by this UI
  package.
- Candidate builds remain experimental and are not linked as stable downloads.
- Calculated response, device-reported listening, device measurement and
  acoustic measurement are separate evidence classes.

## Install

Run `python3 install_v7.py /path/to/HyperAudio` from this package. The installer
checks the exact base commit and each edited file's Git blob SHA before making
changes. It creates a timestamped backup before writing. It refuses to apply to
an unexpected repository state rather than guessing at replacement locations.

## Validation

Run the checks listed in `INSTALL.md`. The included GitHub Actions workflow
adds a dedicated UI validation and repository ZIP artifact job when the update
is committed to a branch. The normal DSP acceptance workflow remains the final
release gate; this UI package cannot resolve or override the current v6.1.0
limiter acceptance failures.
