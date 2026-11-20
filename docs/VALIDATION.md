# Current release validation

20 November 2026. Digital engineering checks pass; all physical validation remains pending. Reports and hash receipts are part of this source release.

| Check | Current result and practical limit |
|---|---|
| Host | `sh scripts/check.sh`:32 unit tests plus content/demo, library interruption/restart and artifact/content checks. Host behaviour does not prove device playback. |
| Firmware | `sh scripts/firmware-check.sh`:Galia Mini and Galia Explore muted profiles compile with pinned PlatformIO dependencies. Native policy/WAV, content-parser, Dallas CRC/debounce and control-policy executables pass. No board flashed. |
| Electronics | KiCad9 ERC and native DRC with all severities and schematic parity on all4 boards:zero violations, zero unrouted pads, zero parity issues. Actual reports are in each board’s checks/. |
| Mechanical CAD | `sh scripts/cad-check.sh`:54 exports/gates pass, including manifold/positive-volume plastic meshes, shell/body and main-board/peripheral intersections, cap pairs, sampled cap/shell motion, reference plugs against shell/PCB,41-position Galia Mini card sweep and wrong-orientation interference. The compliant detent bump is deliberately excluded from the rigid insertion sweep; its nominal lateral deflection is0.35mm. |
| Views and document |46 current coloured views and the consolidated PDF/gallery/BOM are source-bound by frozen-input receipts. The release checker verifies sources, published outputs and available prepared inputs, plus the full RFQ manifest. Images use nominal component envelopes and proposed finish colours/ink, not measured fit or supplier-certified models. |
| Manufacturing reference |64 quote-only Gerber/drill/map/placement files are bound to the current native board hashes. They carry no fabrication authorization. |
| Original collection |3 bilingual stories,6 scripts and6 local synthetic MP3s; SVG/PDF cards and cartridge labels. All MP3s decode; script/audio hashes and public mirrors match. Scripts, listening suitability and final recording approval remain pending. |
| Showcase | Static checks cover128 translated labels,13 local references and3 bilingual stories; JS syntax passes. An independent Node VM/DOM simulation with mock Audio covers sources/durations/downloads, play/stop, language/close/pageleave cancellation, stale callbacks, errors, path rejection and voice fallback. This is UI logic verification, not visual browser or actual-listening QA. |

Managed browser preview could not start: its relay timed out opening port4173. No alternative browser infrastructure or public parent studio was started. Browser layout, narration quality and the deployed public route need separate observation; release/publication notes record any later checks.

The control tests include release-to-arm, debounce, nonrepeating navigation, pause-priority chords with full-release inhibition, bounded volume repeat/ceiling, choice/prompt context, end/help actions and timer wrap. Diagnostics log readable actions and keep speaker request LOW and mute-latch clear asserted. They do not implement the finished integrated-codec playback or production synchronization flow.

Pending physical/DFM evidence: received component envelopes; standard reader screw fit/thread engagement/pullout; wire bends/strain relief; reader stiffness and spring travel over tolerances; card force, recovery, wear and contamination; cap retention, feel, wobble and mechanical overtravel protection; actual plug compatibility; LCD/FPC fit; cell/charger/power/thermal faults; RF; USB/SD/brownout recovery; codec/headphone event mute and acoustic limits; finish durability; child/adult usability and applicable conformity. The Galia Explore boost layout remains an electrical DFM qualification item before fabrication release.

No purchases, fabrication, supplier acceptance, written quote or physical prototype. Public source/RFQ publication is not a production-ready or child-ready product claim. MCP, provider/TTS and subscription-plan eligibility remain a later assessment; no provider is connected or billed. The public site contains original draft content and no ordering flow.
