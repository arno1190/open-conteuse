# Product requirements

User brief accepted 2026-11-17; live Internet radio explicitly added.

## Variants

Mini: approximately 3–5 years, no display, NFC card slot in the upper front, previous/play/next buttons, volume rocker, spoken choices and status LED. Explore: approximately 6–15 years, roughly 2.8-inch 320x240 colour TFT, D-pad/A/B, volume rocker, optional NFC. Both use a rounded portrait Game Boy inspired form, shared electronics, replaceable battery, Wi-Fi, mono speaker, headphone jack, USB-C and microSD. Dimensions remain provisional until components are measured.

## Content

Support imported audio and family recordings, publisher RSS podcast downloads, linear playlists, offline branching stories, bookmarks and bedtime timers. Apple/Spotify links are discovery inputs: resolve public publisher RSS where available with parent confirmation. They do not grant audio export or access to exclusives. No DRM bypass is part of this project.

Live radio: parent-approved configurable station registry; card selection on Mini, menu on Explore. Direct MP3/AAC first; HLS requires a separate capability decision and tests. Bounded reconnects, buffering, clear offline indication, separate volume limits and sleep timers. Radio station approval cannot guarantee the suitability of every live programme. No radio recording in the initial scope.

## Parent studio

Local responsive web UI; optional self-hosted service for background RSS, transcoding and AI. Direct player upload must remain possible without the service. Device pairing requires physical presence and a per-device secret; no default shared admin credential. Manage multiple devices, library revisions, cards, offline readiness, quotas, backups and updates.

AI: choose age/topic/length/objective, gather sources, draft, editorial/factual review, explicit script approval, narration, audio preview, explicit publication approval. Keep transcript, citations, attribution and revision. Learn from the accessible explanations of Petit/ Mini Vulgaire and narrative history of Les Odyssées; use original writing and licensed voices. No child-facing unrestricted AI chat.

## Acceptance priorities

1. Playback survives missing Wi-Fi and unavailable studio.
2. Interrupted download or power loss cannot replace a good library with a partial one.
3. Content revisions require renewed approval; only approved final assets sync.
4. Unknown cards and dead stations fail understandably.
5. Headphone insertion mutes the speaker; output limits require physical measurement.
6. Every deliverable distinguishes host tests, firmware builds and bench results.
