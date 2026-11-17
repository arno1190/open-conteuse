# Roadmap and handoff state

Updated 2026-11-17. This is a source-only bench prototype, not a complete validated handheld. See [VALIDATION.md](VALIDATION.md) for commands/results and [hardware assembly gates](../hardware/ASSEMBLY.md) for pending measurements.

## M1 — host content core and simulator: implemented and host tested

Versioned JSON Schema; canonical immutable revision; bounded asset sizes/hashes and safe paths; duplicate, unreachable and trapped-branch checks. Deterministic play/pause/choice/back/end, bookmarks and Mini/Explore adapters. Staging, revalidation, durable POSIX pointer replacement, retained versions and verified previous-pointer fallback. Text-story and interruption/restart demo runs without hardware or API keys. Device export checks the current firmware's tighter limits and canonical PCM capability.

## M2 — local parent studio: working local slice, host tested

Loopback web UI imports local recording/playlist paths, inspects packs, approves exact revisions, activates a library and assigns cards. CLI provides the same core and direct SD export. Bounded public HTTPS RSS/audio ingestion, GUID handling and changing-byte detection; fixture tests for network boundaries. Parent-approved direct-radio registry and capability decisions (HLS unsupported). One-use physical-presence pairing and authenticated transfer are **simulated on host**, including interruption recovery, not claimed as device onboarding. No public deployment or background subscription service was started.

The local prototype does not yet offer a full graph editor, in-browser waveform/audio preview, multi-pack device index, unattended RSS scheduler, backup UI or network OTA. Those are further product increments; they are not prerequisites for the checked USB/SD bench slice. One process owns private studio state.

## M3 — firmware bench prototype: built, physical tests blocked

Exact target: ESP32-S3-DevKitC-1 / WROOM-1-N16R8. GPIO allocation reserves USB, OPI memory and strapping pins. Original firmware is GPL-3.0-or-later because the selected radio library is GPL; no ESPuino/STUdio code was copied. Adafruit PN532, ILI9341, SD and I2S driver paths compile. Default Mini/Explore builds are muted; explicit audio-opt-in builds compile PCM-WAV local playback and direct HTTP MP3/AAC radio with bounded connection attempts and a 15-minute stop. Firmware verifies exported canonical manifest/asset bytes and story graph before use, with previous-version fallback. Native policy/parser tests pass.

**Pending:** all board flashing, SD/NFC/display/audio measurements, continuous concurrent-load tests, radio buffering/reconnect measurements, hardware headphone insertion mute, acoustic limits, battery/power management and FAT brownout recovery. HTTPS device radio, ICY/HLS, persistent device bookmarks and OTA pairing are not implemented. Review AAC/Helix licence compatibility before any binary distribution; this PR publishes sources only. Host HTTPS fetch and device HTTP streaming are different capabilities.

## M4 — controls PCB and enclosure sources: CAD checked, fit pending

Native KiCad 9 schematic, local symbols and routed 70×65 mm two-layer common controls daughterboard. ERC and DRC include all warnings and schematic parity: zero violations, zero unrouted pads, zero parity issues, no exclusions. This is **not the final audio/power carrier**. BOM identifies actual bench module choices and explicitly unresolved analogue/battery parts. Assembly procedure and pin/polarity contract are documented.

OpenSCAD provides alternate Mini/Explore fronts, common back, captive plunger and fit coupon. All eight variant/part exports render as simple single solids without warnings. Source checks align PCB holes and actuators with the shell. Nominal 100×174×38 mm shell and module/clearance assumptions are recorded in `enclosure/DIMENSIONS.md`. No mesh or PCB order was submitted; nothing was printed or measured.

## M5 — AI editorial boundary: offline provider slice tested

Source citations, script revision/approval, pluggable narration callable, separate final-audio approval and publication metadata. Script/source/audio changes invalidate publication. Deterministic fake provider emits a short tone for tests, not speech or approved facts. Real source gathering/TTS, licensed voices and a finished editorial UI need a separately selected provider and credentials on the studio host. No keys are needed for offline playback and no unrestricted child AI chat exists.

## Next milestone / blocking evidence

Next is **adult bench bring-up**, starting with exact module markings/drawings and switch/header measurements, then coupon fit and USB-only SD/NFC/display tests. The environment has no physical modules, instruments or permission to purchase/order fabrication. Do not bypass these gates by presenting the final battery/headphone carrier or shell as ready.

Before final carrier integration: freeze the headphone DAC/amp/jack and independent insertion-mute circuit; choose a protected cell and review power-path/regulator/USB-C/thermal design; measure board/module/harness/plug dimensions. Then revise exact mounts, connector cutouts, battery retention and fastener lengths, and repeat ERC/DRC/CAD plus physical tests. Record electrical, acoustic, thermal, runtime, NFC, drop and retention results explicitly. Home Lunii/Merlin generations also remain unidentified; no proprietary interoperation was attempted.

Follow AGENTS.md: focused feature branch and reviewable PR; no auto-merge, purchasing, fabrication order or public studio exposure.
