# Prototype RFQ · Galia Mini contact ID and Galia Explore

Engineering source release, 20 November 2026. **Request for quotation only; no purchase or fabrication authorization.** Ask suppliers for feasibility, engineering changes and a delivered, tested exploration prototype—not an unqualified production build.

## Scope to quote

Base: one complete Galia Mini 65×95×24mm contact-ID player, one spare assembled mainboard/reader, three completed DS2401 cartridges. Separate option: one Galia Explore 67×95×24mm display player and spare PCBA. Also price 5/25 prototypes and 100/1000 production feasibility with explicit MOQ. Current hardware is the sole baseline; no NFC/modular alternatives are part of this RFQ.

Use [design/assembly dossier](../docs/design/README.md), [electrical notes](../docs/design/ELECTRICAL.md), native KiCad in hardware/, current enclosure/ sources, each board's BOM.csv and [cost assumptions](costs.json). [Quote-only Gerber/drill/placement references](manufacturing-notes.md) are included to support costing, without fabrication authorization. Manufacturing outputs must be regenerated from the accepted engineering revision after DFM signoff. No Gerber/centroid export is an approval to manufacture.

Quote separately: BOM procurement/substitution list; main four-layer 1.2 mm PCBA with 35 µm copper all layers; inner stack/USB impedance; via-in-pad fill/cap/paste process; reader two-layer 1.6 mm; token two-layer 0.8 mm selective hardgold wipe contacts, finish thickness/hardness and wear suitability; stencil/programming/test fixture; firmware integration; enclosure dimensional prototype and finished appearance; cartridge/ramp/detent qualification; harnesses/battery/speaker/LCD; Galia Mini three-wire harness28 AWG / insulation OD ≤ 0.8 mm, provisional 40 ± 5 mm finished wire length, main SH positions 1/2/6 to readerF-side pads 1/2/3, insulated strain relief and no underside wire protrusion; assembly/QA; packaging and compliant battery transport to France. State Incoterm, currency, VAT/duty/shipping, lead time, NRE, rework, yield assumptions, tooling ownership, IP/source handover and validity period.

## Required engineering work before fabrication release

Review charger/thermistor/current mode, TPS63020 rail margin and transient budget, RF antenna keepouts, speaker/headphone noise and fail-mute event path. Galia Explore backlight boost placement/feedback is an explicit unresolved layout qualification item. Implement/test TLV320DAC3100 playback/headphone events; current source diagnostics are deliberately muted. Review 1-Wire ESD/short/parasite power and timing, keyed insertion/ground-first geometry, spring working travel and 1.6 mm reader stiffness. Qualify the selected standard ISO7045-Z M1.6×4 A2 reader screws at the revised mounting ear. Measure actual cell, speaker, FPC and connector envelopes; confirm case fit with coupons. Do not silently substitute parts.

Quote the current [UX contract](../docs/design/UX.md): distinct tactile caps, contrast-marked controls, softened edges, rounded port openings and physical usability/retention/travel validation. MCP and provider/TTS integration is a later software assessment, not a service already included in this hardware build.

Firmware completion must be priced explicitly: integrated local PCM playback, approved-library/card selection and bookmarks, the UX control/state/feedback contract, Galia Explore library browsing and French/English font/text handling, fail-mute faults and a clearly defined USB transfer or removable-SD workflow. Provide source, build instructions and measured device tests. The current diagnostics are not that deliverable. MCP/provider integration is outside this initial hardware prototype scope.

Acceptance proposal must include: incoming inspection, serialised build log, ERC/DRC on revised natives, clean dimensional stack, power/thermal/charge faults, native USB / SD,5 Galia Mini / 8 Galia Explore keys, repeated token insert/removal/CRC behaviour, audio/headphone mute/acoustic tests, connector strain, enclosure seam/finish, battery transport documentation and applicable conformity roadmap. Supply raw measurements/photos and all source changes. Physical validation is pending; certification is not implied.

## Chinese supplier shortlist · public capability evidence only

- [PCBWay OEM/boxbuild](https://www.pcbway.com/helpcenter/placingorders/How_to_Place_an_OEM_Order_.html) and [enclosure services](https://www.pcbway.com/pcbdesign/enclosure.html): request one accountable electronics-to-enclosure prototype quote.
- [Elecrow boxbuild](https://www.elecrow.com/box-build-and-final-assembly-service.html): request sourcing, assembly, programmed/tested enclosure and delivered sample. Capability listing is not project acceptance.
- [Seeed ODM process](https://www.seeedstudio.com/blog/2025/07/18/understanding-seeed-studios-odm-process-from-concept-to-product/) / [test services](https://www.seeedstudio.com/fusion-testing-solutions.html): ask whether this scope/quantity fits service terms.
- [JLCPCB assembly](https://jlcpcb.com/pcb-assembly) / JLC3DP: separate PCBA/housing comparison; final wiring, firmware/debug and boxbuild must be expressly quoted. Do not assume inclusion.

No supplier has accepted this design or supplied a binding quote. No outreach or orders sent. The owner may send this brief with the release bundle to request quotes; sending messages is a separate explicit action.

## Pricing basis

Current [cost worksheet](costs.json) is an allowance model, not an exact supplier quote. Galia Mini q1 recurring€78.01–173.52, Galia Explore€71.91–162.06; add€100–250setup reserve. Engineering/firmware, finishing/manual assembly, taxes, shipping and compliance are unquoted. Three cartridges and spare assemblies are additional to the one-card Galia Mini baseline. Ask for a full delivered RFQ total rather than comparing bare BOM subtotals.

[Commercial positioning](../site/PRICING.md): conditional retail goals€99Mini/€129Explore incl.France20%VAT, production landed/tested COGS goals≤€35/45. Not achieved at q1, no sales or preorder flow. Current public source release does not claim a child-ready product.

For one of each player, including one Galia Mini cartridge, the combined recurring reference allowance is€149.92–335.58, or€249.92–585.58 with one shared€100–250setup reserve. Engineering, manual finishing/boxbuild, shipping/tax, extra RFQ cards and spare assemblies remain additional and unquoted. This is not a delivered prototype quote.
