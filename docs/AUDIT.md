# Independent release audit · Galia

20 November 2026. Baseline reviewed: `507b540` (Galia naming release). Four bounded reviews covered firmware/electrical contracts, host/web behaviour, mechanical/RFQ tooling and editorial/narration quality. Root implemented the corrections; reviewers made no implementation changes. The original content author's baseline critique is identified as self-audit; new scripts and the final combined revision receive separate review. Exact-head review and CI authorization are recorded on the release PR.

This is an engineering-source/RFQ audit, **not a declaration of a finished child-ready product**. Compilation, nominal CAD and digital audio QA do not qualify physical devices or listening suitability.

## Corrected findings

| ID / severity | Reproduced issue | Correction and regression evidence |
|---|---|---|
| A01 / P1 | Specified10mm battery band could not fit6×1mm slots |13mm anchors,11×2mm slots,10×1.5mm source gauges for both back shells;56 export/check contract. Supplier band dimensions/strength still pending |
| A02 / P2 | Two zero-cost manual/copper BOM features linked prose as nonexistent drawing paths | Actual footprint drawing paths; not-purchased classification; all local BOM sources must resolve |
| A03 / P2 | Stored ERC/DRC reports were not tied to current sources | Native source/report hashes, tool version, all-four physical pad-net checks and shared firmware GPIO/key contract |
| A04 / P2 | Mechanical receipt could omit critical gates; empty-export branch could accept errors | Exact56-entry contract, all shell/internal/cap/plug/card/band gates, cap/plug component counts; reject unexpected error/warning/exit |
| A05 / P2 | A→B→B activation discarded rollback A | Preserve last different verified revision; corruption recovery regression |
| A06 / P2 | Embedded NULs changed approved content on device; deep metadata exceeded firmware parser limit | Host and firmware reject NUL strings; export bounds nesting to12; shared Python/C++ fixtures |
| A07 / P2 | I²C outage preserved stale held/repeating input | Invalidate input state; first valid recovery sample starts a new observed25ms release boundary; hold/chord/recovery/wrap tests |
| A08 / P2 | Long playlist graph validation repeatedly scanned every node | Reverse-edge terminal traversal, O(V+E);6,000-node chain, optional cycle and trapped-cycle regressions |
| A09 / P2 | Engineering-only edits did not redeploy the public downloads | Pages watches RFQ/design/content/build/test inputs; generated hero assets come from current CAD views |
| A10 / P3 | Malformed authenticated HTTP fields could disconnect instead of returning JSON | Typed route fields/import arguments; invalid-object/title/card/source regressions return400 |
| A11 / P3 | Failed recording never reached the advertised fallback | Explicit opt-in browser voice after failure/missing audio; no automatic network voice; maintained real-UI DOM regressions |
| A12 / P2 | Audio generation could publish mixed versions or trust corrupt existing MP3s | Complete staged immutable batches, exact existing-byte verification, explicit approval reset, failure/reuse regressions, build preflight |
| A13 / P2 | Stories lacked causal payoff; robotic formant narration was unsuitable as showcase audio | Three rewritten bilingual plots, local neural presets, connected dialogue and revised pacing; text review plus digital/automatic transcript QA; human listening still pending |
| A14 / P3 | Obsolete carrier/lid/retainer logs remained on main |20 stale generated logs removed; earlier versions remain in Git history |
| A15 / P2 | SD/hash helper was not even compiled by current profiles | SDK compile coverage now included; helper explicitly remains inactive prototype code, with fail-closed read/seek checks. Real SD fault and playback integration remain pending |
| A16 / P3 | Generated BOM used its previous output as an input; copy and playback logic were mixed | Authoritative `hardware/common-parts.json`; separate FR/EN copy file; pinned minimal DOM test dependency and repeatable artifact builders |

| A17 / P2 | Legacy Mini R25 paralleled the stated4.3k reader pull-up; R26 had an unused terminal | Removed both resistors and private power stubs from native PCB/schematic/BOM; preserve shared bus/power routes. Semantic single-pull-up and no-unused-resistor checks plus fresh ERC/DRC/parity; real bus timing still pending |

| A18 / P2 | Public HTML still referenced old static CAD aliases while the builder copied fresh renders under different names | Bind the two actual CAD image elements to generated current aliases; remove old static copies; source/DOM/build byte checks prevent stale illustration reuse |

## Evidence and verification boundaries

- Four native board projects: all-severity ERC, DRC, schematic parity, complete declared native pad nets (including duplicate-number pads), GPIO/address/key mappings. `hardware/check-receipt.json` binds exact inputs and reports.
- Both firmware profiles build with pinned PlatformIO/platform/framework. Native content/policy/card/control tests and shared export fixtures run. Audio remains locked LOW in diagnostics; no physical board has been flashed/tested here.
- Host regressions cover rollback, type errors, graph escape and firmware export boundaries. Website tests use actual HTML/copy/playback code with controlled DOM/media; live browser QA is recorded after deployment.
- CAD receipts bind sources, export/check algorithms and OpenSCAD version. Manifold/component/volume checks are coarse generated-mesh checks, not full self-intersection/orientation certification or received-part fit evidence.
- Exact model/voice/render/script/audio hashes, embedded/downloadable credits, full decode and measured loudness are recorded. Automatic transcripts can flag omissions; neither those transcripts nor a successful decode are human listening approval.
- The one-source RFQ playbook builds HTML/PDF with a comparison worksheet and byte receipts. Reference cost allowances remain estimates; no supplier acceptance or binding delivered quote exists.

## Gates before calling the product finished

**Hardware/integration:** actual component and mated-plug dimensions, band/insert/screw/card retention, spring working travel/reader deflection, display/lens attachment/FPC folds, switch overtravel, clean seams/markings, charger/current/thermal faults, rail transients, RF, headphone/speaker mute and acoustic limits.

**Firmware/product:** integrated codec and local PCM playback, device library/card/bookmark operation, real SD/USB transfer and recovery, Explore browsing/fonts, volume/fault qualification and intended-user usability. Current host foundations and muted board diagnostics do not implement that finished device experience. These deliverables are explicitly priced in the prototype RFQ.

**Content:** full human listening/editorial review of the six exact recordings, pronunciation/character/performance decisions and intended-audience review. Do not silently auto-approve them into a child library.

**Commercial/conformity:** supplier DFM and substitutions, stage costs/ownership, applicable classification/lab work, battery transport and production validation. MCP/TTS/subscription adapters remain a separate assessed future feature. No paid engineering, procurement or fabrication is authorized by this audit.
