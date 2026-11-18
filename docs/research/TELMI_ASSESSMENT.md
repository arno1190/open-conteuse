# Telmi console stream assessment

Updated 18 November 2026. **Yes, Telmi is a credible base for a low-cost console conteuse. Start by evaluating stock TelmiOS and an Open Conteuse export target, then make a small GPL fork only for device features that actually need one.** Podcast feed import is already present in Telmi Sync; it should not be reinvented as the reason to fork the player.

This track is separate from the compact ESP32 hardware study. Telmi is an ARM Linux/SDL application with Miyoo-specific firmware integration, not firmware that can run on the proposed ESP32 board. A stock console also does not provide the original screenless NFC Mini interaction.

## Reviewed upstream snapshot

| Project | Reviewed source | Release observed |
| --- | --- | --- |
|[TelmiOS](https://github.com/DantSu/Telmi-story-teller) |[465fdb41bc83d628266e3e349ca2686ff0d301a6](https://github.com/DantSu/Telmi-story-teller/tree/465fdb41bc83d628266e3e349ca2686ff0d301a6)|1.10.4,29September2026|
|[Telmi Sync](https://github.com/DantSu/Telmi-Sync) |[2efd1afe716d5a2a1474f750b6ba39e434f21681](https://github.com/DantSu/Telmi-Sync/tree/2efd1afe716d5a2a1474f750b6ba39e434f21681)|0.19.0,23October2026|
|[Podcast catalogue](https://github.com/DantSu/telmi-rss-feed-podcasts)|[92f2ecfadef42df5e5c1e91eb223cfb83b96ca92](https://github.com/DantSu/telmi-rss-feed-podcasts/tree/92f2ecfadef42df5e5c1e91eb223cfb83b96ca92)|Catalogue, not a player implementation|

No remote fork or upstream messages were created. Source inspection is not a device playback test. Build evidence, where available, is recorded separately below.

## What is already implemented

TelmiOS has offline branching story playback, music playback and saved sessions. Telmi Sync supplies a desktop editor/import workflow, recording and Piper narration. Its RSS workflow parses publisher feeds, lets a parent select episodes, downloads audio and builds story packs. Persisting a feed as a store is useful, but is not evidence of unattended polling, retention or automatic safe device updates.

Primary source evidence: [RSS parser](https://github.com/DantSu/Telmi-Sync/blob/2efd1afe716d5a2a1474f750b6ba39e434f21681/public/MainEvents/Stores.js#L140), [saved feed modal](https://github.com/DantSu/Telmi-Sync/blob/2efd1afe716d5a2a1474f750b6ba39e434f21681/src/App/Modules/RSSFeed/ModalRSSFeedInfo.js#L20), [audio pack build](https://github.com/DantSu/Telmi-Sync/blob/2efd1afe716d5a2a1474f750b6ba39e434f21681/public/MainEvents/Processes/Store/StoreBuild.js), [story reader](https://github.com/DantSu/Telmi-story-teller/blob/465fdb41bc83d628266e3e349ca2686ff0d301a6/src/storyTeller/stories_reader.h).

## Original brief feature mapping

| Requirement | Current Telmi ecosystem | Work needed for our brief |
| --- | --- | --- |
|Offline stories and choices |Native graph and inventory behaviour; STUdio-compatible import |Export our supported graph subset and validate edge/choice semantics against fixtures|
|Family recordings and music |Desktop import/record/edit and music player |Preserve rights, attribution, approval and stable asset identity|
|Publisher podcasts |RSS import, saved feed stores, episode selection/download |Scheduled polling, GUID deduplication, quotas/retention and approval of exact final audio bytes|
|Bookmarks |Story session and music position saving |Stable episode/revision mapping and crash-safe writes; do not silently carry bookmarks into changed audio|
|Bedtime use |Night playlist, inactivity sleep and volume settings |Validate explicit bedtime deadline behaviour and measure actual sound limits|
|Parent studio |Desktop Electron/React editor and Piper TTS |Our responsive local web UI, optional background service, citations/editorial stages, multi-device pairing and final-audio approval|
|Wireless admin/sync |Wi-Fi-capable model detection |No authenticated on-device sync workflow found in inspected player source|
|Live radio |No approved-station/streaming workflow found |Wi-Fi setup, station registry, MP3/AAC capability work, bounded reconnects and offline handling; HLS remains separate|
|NFC and screenless Mini |Not present on stock consoles |Additional hardware/interaction work; keep the custom Mini track|
|Interruption-safe library update |Existing desktop transfer |Does not meet our last-good-library acceptance requirement; storage protocol/player integration work required|
|AI stories |Piper narration is useful |Source gathering, factual/editorial review, script approval and final audio approval remain separate host stages|

### The original Mini is not the Wi-Fi model

The 1.10.4 release names **Miyoo Mini, Mini Plus and Mini Flip**. Player device detection grants Wi-Fi capability only to Plus/Flip. Therefore the original approximately65 × 93.5 × 18mm Mini can receive host-downloaded podcasts via microSD, but it does not become a wireless subscription/sync device through software alone. For the Wi-Fi/headphone brief, evaluate **Mini Plus first**. Mini Flip's player headphone code explicitly handles USB-C audio rather than a3.5mm jack; do not assume every Miyoo Flip model is interchangeable.

Sources: [supported release](https://github.com/DantSu/Telmi-story-teller/releases/tag/1.10.4), [model/Wi-Fi detection](https://github.com/DantSu/Telmi-story-teller/blob/465fdb41bc83d628266e3e349ca2686ff0d301a6/src/common/system/device_model.h), [Mini Flip headphone handling](https://github.com/DantSu/Telmi-story-teller/blob/465fdb41bc83d628266e3e349ca2686ff0d301a6/src/storyTeller/headphone.h#L12). The supported-model list is not a mechanical drawing or proof of runtime on a received hardware revision.

## Gaps that affect the integration architecture

**Replacement transfer currently removes the old destination before copying the new files.** An interrupted replacement can therefore remove the previous good story. Player save code also truncates the current session file before writing it. Those behaviours must not inherit our existing recovery guarantees merely because the player works offline. [Transfer implementation](https://github.com/DantSu/Telmi-Sync/blob/2efd1afe716d5a2a1474f750b6ba39e434f21681/public/MainEvents/Processes/Stories/StoryTransfer.js#L17), [session write](https://github.com/DantSu/Telmi-story-teller/blob/465fdb41bc83d628266e3e349ca2686ff0d301a6/src/storyTeller/app_file.h#L7).

The current RSS parser gives episodes an empty UUID and version 0. It does not bind a parent's approval to the downloaded file hash. The inspected HTTPS helper explicitly disables certificate verification. Keep Open Conteuse's own bounded HTTPS ingestion and revision checks as the proposed trusted ingestion boundary; do not copy the upstream download policy. These are specific inspected behaviours, not a complete security audit. [RSS identity fields](https://github.com/DantSu/Telmi-Sync/blob/2efd1afe716d5a2a1474f750b6ba39e434f21681/public/MainEvents/Stores.js#L195), [request helper](https://github.com/DantSu/Telmi-Sync/blob/2efd1afe716d5a2a1474f750b6ba39e434f21681/public/MainEvents/Helpers/Request.js#L20).

The stock reader scans every directory under `/mnt/SDCARD/Stories/` except `.` and `..`. A `.partial` directory inside that folder is **not** a safe staging convention. Stage outside the scanned tree. Versioned directories also affect menu duplication and saved-session identity. Merely using two renames or a FAT directory rename is not proof of power-loss-safe atomic library activation. A journal/active-index or boot/player integration may be needed; verify it on the real SD filesystem before claiming the original acceptance requirement. [Directory scanner](https://github.com/DantSu/Telmi-story-teller/blob/465fdb41bc83d628266e3e349ca2686ff0d301a6/src/storyTeller/stories_reader.h#L1285).

## Recommended implementation sequence

1. **Stock-device baseline:** exact supported Mini Plus revision, clean SD card and original/licensed fixtures only. Test boot, headphone insertion, volume, story choices, resume and sleep. No proprietary stories, keys or bundled games are needed.
2. **File-format bridge:** add a Telmi export target to Open Conteuse. Export stable story/episode IDs, a supported `nodes.json` graph, metadata, title image/audio and approved MP3 assets. Transcoding creates a new audio revision that needs its own approval. Keep unsupported graph features explicit rather than silently changing a story.
3. **Parent subscriptions:** poll approved publisher RSS on the parent host, deduplicate GUIDs, download into bounded staging, enforce storage quotas and retention, hash candidate audio and queue it for parent review. Only the approved immutable revision becomes exportable. This reuses the current host pipeline; a reliable scheduler/retention engine is not yet implemented there either.
4. **Storage acceptance gate:** retain previous versions outside the active tree, validate complete files, and design recovery/activation together with Telmi's scanner and bookmark keys. Initial manual SD experiments are not a release-level atomic-update solution.
5. **Thin GPL device fork or companion integration:** add authenticated wireless pairing/sync, safe active-library handling, stable bookmarks and live radio as separate increments. Prefer small upstreamable changes. Do not start by replacing Telmi's functioning story player or RSS importer.

For a first proof, export a three-node original story and one original podcast fixture, play them on stock Telmi, and compare choices/resume behaviour. Then perform disconnect/power-cut tests during each update phase. These tests are pending; no device was flashed or modified in this assessment.

## Build and licence constraints

TelmiOS root LICENSE is GPLv3. Telmi Sync's root LICENSE is also GPLv3 while its `package.json` declares MIT. Treat the discrepancy conservatively and seek upstream clarification before reusing/distributing Sync code; do not import it into the MIT-only host on the assumption that the package field settles the licence. A file-format adapter can be independently implemented without copying player/Sync source. A derived Telmi player fork should remain a separate GPL project. Bundled vendor libraries/fonts need their own redistribution inventory before publishing binaries. [Player licence](https://github.com/DantSu/Telmi-story-teller/blob/465fdb41bc83d628266e3e349ca2686ff0d301a6/LICENSE), [Sync licence](https://github.com/DantSu/Telmi-Sync/blob/2efd1afe716d5a2a1474f750b6ba39e434f21681/LICENSE), [Sync package declaration](https://github.com/DantSu/Telmi-Sync/blob/2efd1afe716d5a2a1474f750b6ba39e434f21681/package.json).

Upstream Makefile uses the mutable `aemiii91/miyoomini-toolchain:latest` tag and prebuilt libraries. The observed linux/amd64 image manifest resolves to `sha256:a8da1021449c80c0ccb75e263f1dfc75b5a004278fefa8a54151e55698a352f4`; use the digest for a build assessment, not a claim of long-term supply reproducibility. The old test target references absent `src/infoPanel` files, so a successful build is not evidence of meaningful test coverage. [Build definition](https://github.com/DantSu/Telmi-story-teller/blob/465fdb41bc83d628266e3e349ca2686ff0d301a6/Makefile), [test definition](https://github.com/DantSu/Telmi-story-teller/blob/465fdb41bc83d628266e3e349ca2686ff0d301a6/test/Makefile).

The pinned source was actually compiled in a network-disabled container after preparing the cache directory. Make exited 0 and emitted five ARM32 hard-float ELF executables, including `storyTeller`; headers and hashes were verified. The linker warned that `libbz2.so.1.0` needed by SDL_ttf was absent from its search paths, so device dependency closure/runtime remains unverified. The existing unit-test target was not run as meaningful coverage because it references missing sources. No compiled binaries are redistributed here.

Build and verification results are recorded in [verification.json](../../hardware/compact/verification.json). Source assessment is complete; hardware playback, network capabilities, SD recovery and redistribution readiness remain pending. No remote fork, purchase or fabrication order was made.
