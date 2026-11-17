# Architecture decisions (provisional)

## Layers

- Player: ESP32-S3 with PSRAM candidate; C/C++ audio engine, microSD, Wi-Fi sync, buttons/NFC and optional display. Validate upstream compatibility before adopting ESPuino hardware or firmware.
- Parent studio: Python service and responsive web UI, initially local-only. RSS fetching, media preparation, review workflow and device library management.
- Portable content: versioned JSON manifest, assets, checksums, provenance and approval bound to immutable content revisions.
- Host core: deterministic story graph/state machine, manifest checks and sync logic tested without electronics.

The initial manifest validator is deliberately a draft graph validator. It does not yet verify asset hashes, audio files or approval signatures; it is not sufficient to authorise device publication.

## Planned sync protocol

Device requests an approved library manifest; downloads into staging; validates sizes, hashes and references; atomically activates only a complete revision. Retain the previous revision until activation succeeds. Local card assignments and bookmarks survive failed sync. Store device pairing credentials separately from content and reject unauthenticated writes.

## Audio and networking

Decode local files from microSD; use bounded stream buffers for live radio. Keep UI tasks independent of decoding. Never put AI provider secrets on the player. Parent studio network fetches need redirect/IP validation, response limits, timeouts and quotas to prevent SSRF and resource exhaustion. Network-dependent tests use fixtures by default.

## Licence strategy

Original foundation is MIT; original demonstration content is CC0. If ESPuino is reused, preserve GPL obligations in the derived firmware. Study STUdio formats or add an adapter with the appropriate notices; do not assume the whole repository can remain MIT after copying upstream code.
