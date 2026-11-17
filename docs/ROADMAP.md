# Roadmap and handoff state

## Completed

- Product brief, radio requirement, architecture, research register and physical validation gates.
- Dependency-free draft story graph validator, CLI, original example and regression tests.
- GitHub Actions validation workflow.

## Next: M1 — host content core and player simulator

Implement an explicit versioned JSON Schema and immutable content revision/hash model. Validate asset references and file paths, bounded file sizes, missing/duplicate nodes, unreachable branches and trapped cycles. Add deterministic playback simulation (select, play/pause, choose, back, end, bookmarks) with Mini spoken-choice and Explore menu adapters. Add fixtures and tests for invalid packs and interruption/restart. Deliver a runnable CLI demo and document limitations. No hardware or AI API key required.

## M2 — local parent studio

Local web UI: import audio, create playlists/cards, inspect packs, approve final content revisions. RSS fetch with fixtures, episode GUID handling, changing-byte detection and bounded downloads. Radio registry and stream capability checks. Establish authenticated device pairing and staging/activation sync simulator. Do not expose the studio to the Internet by default.

## M3 — firmware bench prototype

Freeze exact board/codec/reader and upstream licensing decision. Firmware build CI, SD playback, NFC/buttons, headphone mute, radio and power management. Keep bench checks explicitly pending until measured.

## M4 — Explore display and industrial design

Shared player state machine with colour-screen UI. KiCad carrier, OpenSCAD shell, dimensional assumptions, BOM and assembly guide. ERC/DRC and CAD checks are not physical validation.

## M5 — AI studio

Source-backed outline, draft, script approval, pluggable licensed TTS, final audio approval and immutable publication. Offline fake providers in tests. User-supplied credentials only; never required for ordinary playback.

## Blocking evidence

Exact home Lunii/Merlin generations, measured module dimensions, battery/audio/thermal/drop results. Continue software work independently.
