# Local content and parent workflow

Python 3.11+, standard library only for runtime/host tests. JSON Schema is in `schemas/pack-v1.schema.json`; semantic graph, quota, path and asset checks supplement it. The schema is not an approval signature. Canonical JSON is UTF-8, sorted keys, no whitespace separators and no NaN; revision is SHA-256 of those bytes. Declared asset hashes/sizes bind actual audio bytes into that revision. Manifest approval fields are not trusted for publication.

```sh
python3 -m conteuse.demo
python3 -m conteuse.studio --root .studio
```

Open the printed **127.0.0.1** address and enter the launch token. The UI imports local recording/playlist paths, assigns cards and inspects a pack (including its text/asset manifest), explicitly approves final content, then activates that revision. It binds loopback only, rejects foreign Host/Origin and requires a per-launch token for every mutation. No shared admin password, Internet exposure, AI key or commercial audio is needed. Keep `.studio` private and outside Git.

For parent recordings and playlists:

```sh
python3 -m conteuse.tools import work/my-pack /path/to/first.wav /path/to/second.wav --title "Family recordings"
python3 -m conteuse.tools inspect work/my-pack
# After reviewing text AND listening to these exact audio files:
python3 -m conteuse.tools approve work/my-pack
python3 -m conteuse.tools publish work/my-pack
```

Import bounds each file and total pack size; creates safe generated asset paths; hashes copied bytes; creates a linear next-track graph. It does not transcode, verify audio suitability or infer a licence. Existing destinations are rejected. The device export profile permits only canonical PCM WAV; the current custom-board diagnostics do not play audio yet. The host core can preserve approved MP3/AAC assets for future decoders. A text-only example is original CC0 and carries no supplied audio.

The CLI also provides `download FEED_URL EPISODE_GUID NEW_FILE`: bounded parent-invoked HTTPS RSS/audio download. No automatic subscription scheduler is started. Network fetch validates public addresses, pins checked DNS to the connection while verifying TLS hostname, rechecks redirects, rejects credentials/compression and bounds transfer bytes. It uses operation timeouts and checks a transfer deadline between reads; DNS and HTTP header parsing remain OS/library operations, not a hard real-time deadline. Default tests use fixtures. RSS GUID identity and audio byte identity are separate: `Studio.observe_episode` flags changing bytes, including dynamic advertisements. Never approve just a feed title. Apple/Spotify URLs do not grant export rights.

`Studio.begin_pair(physical_presence=True)` / `claim_pair` model a 120-second one-use physical pairing event. A unique per-device secret is returned once; only its SHA-256 is stored in mode-0600 state. `Studio.sync` rejects incorrect credentials and unapproved revisions, copies to staging, verifies, then atomically switches the active pointer. This is a **host simulator**, not device onboarding. It retains old revisions and a verified previous pointer, and does not replace cards/bookmarks. One writer owns each library; do not run simultaneous studio/CLI mutations against the same root. Back up private state separately. No default fleet secret exists.

`card UID REVISION` assigns a parent-approved revision. `station ID URL --mime audio/mpeg` records an explicitly reviewed direct station; registry approval never guarantees live programme suitability. Export uses `export SOURCE MOUNTED_SD/library` and emits the current per-ROM two-slot card records for approved, verified content present on that SD. Skipped legacy IDs or unavailable revisions are reported; cards.json remains a host snapshot. The portable firmware content contract handles one active pack; physical audio playback and Explore library browsing remain pending. Mini now resolves per-ID revisions across stored packs with incremental verification; parent Wi-Fi transfer/assignment is implemented for engineering tests per design/CARDS.md. Content hashes are not authentication credentials. Offline card playback must not enable Wi-Fi.

`conteuse.editorial.Draft` implements the offline editorial boundary: source citations → draft → script approval → provider narration → separate audio approval → immutable publication metadata. Script/citation or audio-byte changes invalidate publication. `fake_narrator` generates an 0.1-second WAV tone for pipeline testing, **not speech or a reviewed final recording**. The standalone starter-collection generator now renders local neural example narration with pinned Kokoro presets, immutable batches, media QA and attribution. It is separate from this parent studio. Research/TTS provider connections and parent audio preview inside the studio remain future adapters; secrets stay on the studio host outside Git and off the player. Tests demonstrate invalidation; no AI draft is asserted factual merely because a hash or approval state exists.

This is a local prototype workflow. It does not yet provide waveform preview, a full graphical graph editor, automatic backups/RSS scheduling, signed packages, OTA firmware updates or a production HTTP server. These are explicit follow-on scope, not hidden completed features.

The current original [bilingual collection](../content/starter/README.md) includes scripts, activities, paper cards and electronic-cartridge artwork labels. None is automatically approved or activated; artwork catalogue IDs are not the DS2401 ROM IDs printed by the muted Galia Mini diagnostics.
