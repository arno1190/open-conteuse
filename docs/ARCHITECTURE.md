# Architecture decisions (provisional)

## Layers

- Player: ESP32-S3 with PSRAM candidate; C/C++ audio engine, microSD, Wi-Fi sync, buttons/NFC and optional display. Validate upstream compatibility before adopting ESPuino hardware or firmware.
- Parent studio: Python service and responsive web UI, initially local-only. RSS fetching, media preparation, review workflow and device library management.
- Portable content: versioned JSON manifest, assets, checksums, provenance and approval bound to immutable content revisions.
- Host core: deterministic story graph/state machine, manifest checks and sync logic tested without electronics.

The draft CLI validator checks graph structure only. `packages.check_pack` additionally checks actual asset paths/sizes/hashes; canonical SHA-256 binds all manifest fields and declared audio bytes. Parent approval is stored outside the pack by the local studio and must match that revision before publish/export/simulated sync. It is a trusted local decision, not a digital signature. Firmware validates exported canonical bytes and assets before using the current or previous pointer; its capability limits and decoder formats are deliberately narrower than the host core.

The local studio uses the Python standard library HTTP server on loopback, a per-launch parent token, Host/Origin checks and private state. Pairing and authenticated staged transfers are host simulations. Production network onboarding, multi-pack indexes and OTA are separate integrations, not exposed by a default unauthenticated service.

## Implemented host sync contract / device integration pending

Device requests an approved library manifest; downloads into staging; validates sizes, hashes and references; atomically activates only a complete revision. Retain the previous revision until activation succeeds. Local card assignments and bookmarks survive failed sync. Store device pairing credentials separately from content and reject unauthenticated writes.

## Audio and networking

Decode local files from microSD; use bounded stream buffers for live radio. Keep UI tasks independent of decoding. Never put AI provider secrets on the player. Parent studio network fetches need redirect/IP validation, response limits, timeouts and quotas to prevent SSRF and resource exhaustion. Network-dependent tests use fixtures by default.

## Licence strategy

Original foundation is MIT; original demonstration content is CC0. The bench radio selects ESP8266Audio, so original firmware is explicitly GPL-3.0-or-later with component notices and an AAC redistribution review gate. No upstream firmware was copied. If ESPuino is reused later, preserve its GPL obligations in derived firmware. Study STUdio formats or add an adapter with the appropriate notices; do not assume the whole repository can remain MIT after copying upstream code.
