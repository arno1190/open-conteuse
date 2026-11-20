# Current release state

Updated 20 November 2026.

Implemented: local parent studio/content validation and staged export; two current native four-layer main PCBs; Mini reader and passive token native two-layer PCBs; parametric cases, keyed cartridge, source-derived views; exact-identity BOM with drawing-defined manufactured items; machine-assembly RFQ; original FR/EN starter collection and public showcase.

Checked: host behaviour, two muted diagnostic firmware builds, passive-ID CRC/debounce native tests, native ERC/DRC and schematic parity on four boards. Enclosure geometry checks and their actual outcomes are recorded in [validation](VALIDATION.md). These are engineering checks, not evidence of physical safety or production readiness.

Next hardware gates: independent DFM, RF/boost/power review; confirm standard reader screw fit/pullout; dimensional coupons and received-part measurement; spring travel and reader stiffness; staged power/charger/thermal tests; codec and headphone mute driver; acoustic limits; USB/card/SD/brownout behaviour; finished-enclosure qualification; applicable conformity and battery shipping documentation. No supplier quote, order, physical prototype or compliance evidence exists.

Content: three original bilingual scripts and card artworks are drafts. Six downloadable local synthetic MP3 recordings and optional browser speech are demonstrations only; exact script and final recording approvals are separate and pending. Local studio never auto-approves them.

Public release means source, documentation and showcase publication. It does not mean a shippable child-ready product.

UX refinement: distinct tactile cap sizes/symbols at existing PCB switch centres, clear5/8-control hierarchy, no essential long presses, and host-tested context/debounce/repeat/volume policy. Diagnostic firmware logs actions only. Parent-owned personalization is the product target; MCP/provider/TTS/subscription eligibility remains a later assessment per PERSONALIZATION.md, with no connected service or implicit API entitlement.
