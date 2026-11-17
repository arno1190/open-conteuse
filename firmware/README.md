# ESP32-S3 bench firmware

Two build-time variants share input, library validation and playback policy. Exact target: **ESP32-S3-DevKitC-1 with ESP32-S3-WROOM-1-N16R8**, 16 MB flash / 8 MB OPI PSRAM. No device was flashed or physically tested in this task. The project-local board definition records the selected memory configuration rather than silently using the generic N8 default.

```sh
python3 -m venv work/toolenv
work/toolenv/bin/pip install -r firmware/requirements-build.txt
PLATFORMIO_CORE_DIR="$PWD/work/pio" work/toolenv/bin/pio run -d firmware
# Compile explicit audio opt-ins too; do not flash without hardware review:
PLATFORMIO_CORE_DIR="$PWD/work/pio" work/toolenv/bin/pio run -d firmware -e mini-bench-audio -e explore-bench-audio
```

`mini` and `explore` leave audio disabled. All four configurations are buildable; a build proves compilation/linking only. Neither the muted build nor the opt-in build establishes safe electrical/acoustic output. See `hardware/PINOUT.md` and `hardware/ASSEMBLY.md` before wiring. GPIO47 starts low. An external shutdown pulldown and an independent hardware headphone insertion mute are still required.

## What runs

- Debounced eight-button diagnostics; local selection disables Wi-Fi. PN532 I2C UID reading and unknown-card reporting. Explore ILI9341 landscape text/choice diagnostic on shared SPI. No touch controller is used.
- Boot checks `/library/active.json`, canonical manifest SHA-256 and all declared asset sizes/hashes before accepting any story. If current validation fails, try `/library/previous.json`. Reject unsafe paths, missing references, duplicate/unreachable nodes and branches trapped without an exit. Both invalid means no library; the separate `/bench.wav` fixture remains an explicitly opt-in bench diagnostic.
- Select choices using left/right and confirm with A; back returns through up to 128 history entries. Text-only packs exercise the graph but produce serial/display text, not spoken narration. Recorded node audio can be canonical PCM WAV. Pausing a WAV stops it; the next play restarts the node. Persistent firmware bookmarks and a finished Mini spoken-choice adapter remain integration work.
- WAV reader deliberately supports a canonical 44-byte PCM header, 16-bit mono/stereo at 16,000 / 22,050 / 44,100 Hz. Extra metadata chunks and other formats fail visibly. PCM samples are attenuated by 1/16 for bench tracing. This is not an acoustic volume limit. Output begins only in an audio opt-in build.
- Optional direct HTTP MP3/AAC radio via ESP8266Audio. Physical USB serial configures volatile Wi-Fi credentials; no provider secrets, password echo, default admin credential, captive portal or public server. Parent-exported station registry required. Three connection attempts, five-second retry interval, 8 KiB source buffer, 15-minute stop. Selection of local audio or `stop` turns Wi-Fi off. NFC polling is suspended during playback to avoid its synchronous transactions interrupting audio.

## Export a library

On the parent computer, import/inspect/review the actual audio first:

```sh
python3 -m conteuse.tools import work/recording-pack path/to/recording.wav --title "My recording"
python3 -m conteuse.tools inspect work/recording-pack
python3 -m conteuse.tools approve work/recording-pack
python3 -m conteuse.tools export work/recording-pack /path/to/mounted-sd/library
```

The export writes sorted-key UTF-8 canonical manifest bytes. Their raw SHA-256 equals the revision. Hand-editing whitespace makes device verification fail; re-export instead. Parent approval covers the exact manifest and every asset hash. Approval is a trusted local studio record, not a signature; physical SD access is a trust boundary. No unauthenticated network activation endpoint exists on this firmware.

Device capability limits are **16 KiB manifest, 128 nodes, 16 choices per node, 64 assets, 32 MiB per asset, 128 MiB total**. These are tighter than host limits. The CLI export enforces these limits and checks referenced audio against the canonical PCM header; unsupported media must be transcoded and approved again. A host-valid MP3 playlist cannot be exported to this WAV-only local player yet. The package parser also runs in a native C++ test, but SD/NFC/display/decoder drivers need a board.

For the text demonstration, export `examples/first-adventure` after approval. Put optional card mappings in `/library/cards.json` as `{ "lowercasehexuid": "approved-revision-sha256" }`; the CLI export writes the parent's current assignments. This prototype has one active story pack; a card selects it only when its mapping matches the verified active revision. A multi-pack device index and asset reuse are not implemented.

## Radio bench interface

`/library/stations.json` example (use an actual parent-reviewed direct stream URL):

```json
{"station-id":{"url":"http://example.invalid/direct.mp3","mime":"audio/mpeg","approved":true}}
```

`example.invalid` is intentionally non-working. MIME choices are `audio/mpeg` and `audio/aac`. This bench transport supports **direct HTTP only**; HTTPS stations fail closed pending an explicit verified-TLS adapter. HLS, redirects on ESP32, ICY metadata handling and station content suitability are not established. The parent host fetch adapter separately uses checked public HTTPS destinations; it is not this device stream transport.

In an audio opt-in build, send `wifi SSID<TAB>PASSWORD` and newline over the physically attached USB serial port; wait for connection, then `radio station-id` and newline. Send `stop` to mute and turn Wi-Fi off. Credentials live only in RAM in this implementation. The firmware never prints the command. Do not commit or attach real credentials/logs to an issue. Test with dummy loads before any transducer.

## Deliberate limits and next hardware gate

No battery monitor, charger/power-path controller, verified headphone DAC/amp/jack circuit, finished volume UI or measured sleep current. The default build logs volume and up/down inputs but does not promise a finished UI. No over-the-air transfer/pairing or persistent device bookmark store; authenticated pairing/transfer recovery is exercised in the host simulator. Host POSIX `fsync`/rename tests cannot establish SD FAT brownout behaviour. Wi-Fi/decoder contention, buffering, reconnect timing and insertion mute latency must be measured. Do not interpret compiler success as a completed child-facing player.

Original firmware source: GPL-3.0-or-later, see `LICENSE` and `THIRD_PARTY.md`. Host Python and original CAD remain MIT. No ESPuino or STUdio source was copied.
