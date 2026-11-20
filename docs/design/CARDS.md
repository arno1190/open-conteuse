# Galia Mini · cards, pictures and parent Wi-Fi setup

A card contains a DS2401P+ factory ROM identifier, a20×12×0.8mm two-layer PCB and two hard-gold wear contacts. It has no battery, antenna, NFC electronics or audio memory. Only its identifier is stored permanently in the chip. The player stores audio and the assignment. There is no licensed card-count restriction; storage, filesystem and practical administration are finite. IDs are selectors, not authentication.

## Replaceable picture and dedicated views

[Exploded card](images/card-exploded.png) · [Front](images/card-front.png) · [Rear](images/card-rear.png) · [Section](images/card-section.png) · [Printable inserts](../../content/starter/cartridge-labels.pdf) · [Window cutting outline](../../enclosure/card-window.svg).

The external insertion envelope remains40mm body width,60mm length,4.3mm thickness with44mm-wide handle. Contacts, key, ramps and stop stay at their existing positions. Adult access uses the existing two M1.6×3 screws; there is no loose outside clip.

| Layer | Nominal specification |
|---|---|
| Front frame | PETG shell; visible aperture32×37mm atX4,Y8; internal pocket34.4×39.4mm atX2.8,Y6.8 |
| Clear window | OC-ID-WINDOW-R1: cut/deburred clear PETG sheet34×39×0.50mm, nominal edge tolerance±0.10mm and thickness±0.05mm; exact drawing in enclosure/card-window.svg |
| Picture | Paper33.6×38.6mm, maximum0.15mm thick, no adhesive; X3.2,Y7.2 |
| Rear picture support | TopZ2.80mm; paper endsZ2.95, window endsZ3.45; front retaining shoulderZ3.55 |
| Electronics | Existing DS2401 PCB located by rear pegs and retained on bare margins |
| Closure | Two M1.6×3 screws through the exposed handle |

The window overlaps the visible aperture by1mm nominal per edge. Its lateral allowance is0.2mm per side; nominal roof clearance is0.10mm, reduced to0.05mm at maximum specified sheet thickness before printed tolerances. The pocket leaves0.8mm to the screw bosses and0.65mm to the PCB seat. These are source assumptions, not measured manufacturing capability. Print the coupon/shell and measure the received sheet before accepting the fit. Do not use real glass. Inspect cut edges, screw retention, frame strength, trapped-sheet retention and repeated opening before child use.

To change the picture: remove the card from the player; an adult opens the two screws, separates the halves, lifts the board only if needed without touching wear surfaces, places the clear sheet against the inside front shoulder, then the paper image facing outward, and closes the rear support. Keep contacts, ramps, key and stop bare. Do not glue the picture. Print at100% with browser headers/footers disabled and check the reference ruler. The inserted handle exposes only the first12.8mm of the shifted insert: essential icon/name remain visible; the lower header background is partly hidden.

The local parent studio also accepts a PNG/JPEG/WebP and prints a correctly sized picture. The chosen file stays in the browser; the tool does not upload the image. Printing artwork does not create an electronic ID card.

## Parent workflow implemented for engineering tests

1. On power-up, hold play/A plus volume-up for3seconds within the first15seconds after diagnostics become ready. Normal operation keeps Wi-Fi off. This is an adult setup gesture, separate from normal playback controls.
2. For this EVT version, connect USB and read the temporary SSID, WPA2 password and64-character setup token on the serial monitor. Final credentials are freshly generated after RF startup, checked for expected lengths and never committed or stored in studio state. No default shared password exists. The USB credential step is an engineering setup limitation, not a finished phone-only onboarding experience.
3. Connect the parent computer to the Galia setup Wi-Fi. Start the private studio with `python3 -m conteuse.studio --root .studio`, open its localhost URL and enter its separate session token. Never expose this studio to the Internet.
4. Inspect and explicitly approve the exact final pack revision. Current device transfer accepts canonical16-bit PCM WAV at16/22.05/44.1kHz; it does not silently transcode MP3 or auto-approve content.
5. In Wi-Fi setup, enter the player's temporary token and select **Read inserted card**. The CRC-valid stable ID fills the card field. Choose the approved pack directory and select **Transfer approved pack and assign card**. Reassigning the same ID does not alter the card itself.
6. Keep the computer on the setup network until confirmation. Files are staged, hashed incrementally and published before the assignment changes. Inserted-card selection resolves the mapping against verified local content. The current diagnostic firmware still keeps physical audio outputs muted; integrated codec playback remains a separate bench milestone.

No Internet or cloud service is needed. The setup AP uses192.168.4.1 and accepts only authenticated parent operations. Three minutes without an authenticated request ends the session; a two-hour overall deadline permits conservative-clock SD transfers and verification. An in-flight body read is bounded by10seconds plus the1second socket timeout; response timeout is2seconds. Normal radio shutdown follows that bounded operation. Timeouts and SD failures do not authorize an unverified assignment.

## Transfer and recovery contract

The local studio contacts only192.168.4.1, without redirects or an arbitrary device-URL proxy. The firmware uses esp_http_server with pre-allocation request limits:40,000-byte JSON envelopes and8,192-byte chunk envelopes. Audio travels as strict base64 JSON with at most4,096 decoded bytes per chunk, preserving NUL and every byte value. Paths are bounded ASCII, case-distinct on FAT and free from traversal/file-directory collisions. Packs retain32MiB per-asset and128MiB total bounds; those are capacity bounds, not measured throughput promises. The1MHz SD clock can make large transfers very slow.

`POST /api/begin` stages the exact manifest; `/api/chunk` appends only a declared asset at the expected offset. `/api/commit` starts incremental asset verification, polled through `GET /api/job`, and only then renames the complete directory into immutable versions. Reusing an existing version still requires verification during assignment. `POST /api/assign` verifies the target and writes the inactive one of two per-ID mapping slots. Each record binds ID, revision and generation with SHA256; a torn/corrupt slot is ignored and the previous valid slot remains. Temporary files never win selection. Stale incoming files are removed at the next parent session. Lost confirmation requires reading device status before assuming which assignment is active.

The IDs and integrity hashes are not authentication credentials. Parent authentication is the independent ephemeral setup token carried inside the WPA2-protected private AP. No TLS/cloud endpoint or public studio is provided. Transfer/parser limits and software recovery tests do not prove SD power-loss behaviour, radio reliability, throughput or physical safety.

## Mounted-SD export uses the same mapping records

Power the player off before removing its SD card. The existing `python3 -m conteuse.tools --root .studio export SOURCE MOUNTED_SD/library` command now writes the same per-ROM two-slot records consumed by firmware, as well as legacy host snapshots in cards.json/stations.json. Only CRC-valid DS2401 IDs pointing to an approved, device-compatible revision actually verified on that SD are emitted. Missing/unapproved content, legacy non-DS2401 IDs and conflicting case aliases are reported as skipped rather than silently becoming physical assignments. Physical ID spelling is normalized on new assignments. The export preserves the previous mapping slot and confirms the new record; failed writes do not deliberately overwrite the active slot.

The firmware test job runs the actual CLI export and feeds its generated record into the shared firmware mapping decoder. This verifies the producer/consumer format, not physical SD power-loss behaviour. Wi-Fi assignment and powered-off SD export use the same ID/revision/generation/checksum contract.

## Qualification still pending

Real-board upload/CRC/SD fault tests; reset/removal/brownout during commit and mapping writes; timeout/radio shutdown measurements; finished parent onboarding; received window/paper tolerances; screw/peg/frame strength, contact wear and repeated opening; and integrated playback/acoustic validation. No purchases, supplier outreach or fabrication orders are authorized by these sources.
