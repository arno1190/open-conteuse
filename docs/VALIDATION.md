# Current release validation

20 November 2026. These are digital engineering checks. Physical validation, finished device playback and final listening approval remain pending. See [the independent audit](AUDIT.md) and [RFQ launch playbook](../rfq/LAUNCH-PLAYBOOK.md).

| Check | Result and practical limit |
|---|---|
| Host | `npm ci --ignore-scripts` then `sh scripts/check.sh`: 52 unit tests, content/demo, rollback/interruption/restart, typed HTTP errors, firmware export boundaries and artifact checks. Host behaviour does not prove device playback. |
| Firmware | Both muted Mini/Explore profiles compile with pinned PlatformIO/platform/framework. Native policy/WAV/content/card/control executables and shared Python/C++ parser fixtures pass. Incremental SD/hash verification and parent Wi-Fi transfer/mapping are active engineering sources; the legacy pointer loader is compile-covered. No board flashed. |
| Electronics | All-severity KiCad ERC/DRC and schematic parity on all four boards: zero violations/unrouted/parity errors. Every numbered native pad, including duplicate-number pads, matches declared contracts. Shared GPIO/address/key definitions are checked. Native source/report hashes and tool version are recorded. |
| Mechanical CAD | 58 exports/checks pass: closed positive-volume meshes, full component counts, shell/body/internal/cap-pair/motion checks, reference USB/headphone plugs, 41-position card sweep, wrong-orientation positive interference and both band-slot gauges. These are nominal/coarse mesh checks, not physical fit or comprehensive self-intersection certification. |
| Views/documents | 50 coloured views, combined dossier, searchable BOM and RFQ playbook outputs bind to exact sources. Printable PDF text bounds are checked separately. Images use nominal envelopes/proposed finishes, not supplier-certified models or received-part measurements. |
| Manufacturing | 64 quote-only Gerber/drill/map/placement references bind current native PCB hashes. No fabrication authorization. |
| Content | Three revised bilingual plots, six scripts and six local Kokoro neural MP3 previews. Complete-batch hashes, model/voice/render settings, embedded/downloadable credits and exact mirrors checked. Full decode, measured digital loudness/peak and local automatic transcripts recorded; neither ASR nor hashes approve narration quality. |
| Website | 137 translated labels, 18 resolved local/derived references and three bilingual stories; JS syntax and maintained actual-UI DOM/media regressions pass. Tests cover source/duration/download, stop/language/close/pagehide cancellation, stale callbacks, invalid paths, recording failure and explicit browser fallback. Node dependencies are development-only. |

The prior published GitHub Pages route was verified in a real browser. This revision's post-deployment UI/download observations are recorded on its release PR. The unavailable managed local preview relay was not replaced with alternate browser infrastructure, and the private parent studio was never deployed publicly.

Control policy covers boot-held/release-to-arm, 25 ms observed stable release after I²C failure, debounce, nonrepeating navigation, pause-priority chords/full-release inhibition, bounded volume repeat/ceiling, prompt contexts and timer wrap. Diagnostics keep speaker request LOW and the mute-latch clear asserted. Finished codec playback, device library/transfer, Explore browsing and acoustic qualification remain explicit RFQ work.

The band slots are nominally 11 × 2 mm for a 10 × maximum 1.5 mm band allowance. This means 1.0 mm total width clearance and 0.5 mm total thickness clearance. Supplier thickness, threading, strength and retention need measurement. Card sweep excludes the compliant detent; its nominal lateral deflection is 0.35 mm and remains unqualified.

Pending physical/DFM evidence includes received parts and mated plugs/wires; screws/inserts/retention and band; reader stiffness/spring travel; card wear/contamination; switch overtravel/feel; LCD/lens/FPC attachment; cell/charger/thermal and rail faults; RF; SD/USB/brownout recovery; headphone/mute/acoustic limits; enclosure finish and intended-user usability. Explore backlight boost layout is an electrical DFM qualification item before fabrication.

No purchase, fabrication, supplier acceptance, binding quote or physical prototype is claimed. Source/RFQ publication is not a child-ready product launch. Provider/MCP/subscription integration remains a separate future adapter; standalone example narration is not a connected parent-studio feature.

Card feature software evidence: native strict-base64 all-byte tests, pre-allocation body bounds and wrap-safe receive deadlines, injected mapping short/corrupt write and remove/rename failures; HTTP peer upload/approval/retry/corrupt-commit/verification polling tests; actual parent-UI decode ordering and local Chromium picture/print-size checks. These do not execute the ESP32 Wi-Fi/SD hardware. See design/CARDS.md for setup and remaining qualification.
