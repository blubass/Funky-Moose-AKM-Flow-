# v1.0.1 — Workflow Radar, more flow, more love

Funky Moose Release Forge `v1.0.1` delivers a broad UI and workflow polish pass: clearer orientation, more consistent interaction, and more robust behavior across the whole app.

## Highlights

- Unified radar/cockpit look across all major areas
- Much clearer status communication and empty states
- Smoother flow between Overview, Details, Cover, Loudness, and Release
- Stronger batch, import, and export workflows
- Expanded regression coverage and successful macOS build

## New & improved

### Global

- New consistent header with visible system state
- Better visual hierarchy and clearer action zones
- More of a single cohesive product, less scattered UI

### Dashboard

- New `Operations Radar`
- Focus hints and meta metrics for the current work state
- Faster guidance toward the next sensible step

### Overview

- New `Catalog Radar`
- Better filter, search, and empty-state communication
- More direct actions for Details, audio preview, and Loudness
- Double-click now reliably opens Details

### Work Details

- New `Work Radar`
- Live context for title, audio, status, and instrumental flag
- Clearer hints depending on record state
- Much easier-to-read editing workspace overall

### Cover Forge

- Consistent preview/export rendering
- Improved preset layouts including `Top Left`
- Better artwork flow with Release handoff, Finder access, and live radar state
- New render parameters are persisted and restored correctly

### Release

- Clearer release assembly workflow
- Smarter file matching and duplicate handling
- Cleaner export flow
- Old generated export artifacts are cleaned before rebuild

### Loudness

- Improved status and hint communication
- More consistent handoff from Overview and file selection
- Better visibility into workflow state

### Assistant & Batch

- Both areas now have proper radar-style guidance instead of bare controls
- Clearer queue and input communication
- Separate input fields instead of overwriting each other
- Batch flow is more robust and better guided

## Stability & quality

- Regression suite modernized and expanded
- `45/45` tests passing
- GUI smoke test passing
- PyInstaller macOS build successful

## Build artifacts

- `Funky Moose Release Forge.app`
- `Funky Moose Release Forge.app.zip`

## macOS note

Because the build is currently not codesigned/notarized, macOS may still show a security dialog on first launch.

Thanks for testing, refining, and shaping this project. This release feels much more cohesive, clearer, and more pleasant to use in day-to-day work.
