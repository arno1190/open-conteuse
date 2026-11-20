# Galia RFQ launch playbook

**One place to launch and compare quotes.** RFQ ID **GALIA-EVT-001**, revision **v0.2.1-rfq**, 20 November 2026. This requests engineering and prototype quotations. It is not a purchase order or fabrication release. The Mini and Explore sources are engineering baselines; a supplier must quote the unresolved work explicitly.

## 1. Download the controlled package

Use [the release paired with this playbook](https://github.com/arno1190/open-conteuse/releases/tag/v0.2.1-rfq), then download its **Source code ZIP**. Keep the tag and `rfq/manifest.json` with every quote. Do not mix main-branch files with a released revision. [Release source ZIP](https://github.com/arno1190/open-conteuse/archive/refs/tags/v0.2.1-rfq.zip).

The ZIP contains everything below; send the release link with the small playbook/dossier PDFs. The complete source archive is large; do not split it across emails or mix revisions. The locally generated `galia-rfq.zip` is an optional filtered equivalent, with its own manifest. It is not necessary to buy a service or upload to a PCB ordering cart to request this quote.

| Included | Where | What the supplier must use it for |
|---|---|---|
| Combined illustrated dossier | `rfq/engineering-dossier.pdf` | Read the integration, controls, BOM and outstanding engineering work first |
| Scope and engineering blockers | `rfq/README.md`, `rfq/manufacturing-notes.md` | Quote full completion scope, not bare PCB assembly |
| Four native KiCad projects and exact BOMs | `hardware/mini`, `explore`, `card-reader`, `story-card` | Review design; source exact parts; propose documented substitutions |
| Gerber/drill/placement references | `rfq/manufacturing-reference/` | **Cost/DFM reference only**; regenerate from the accepted design after signoff |
| Enclosure and cartridge sources/meshes | `enclosure/`, `enclosure/print/` | Dimensional coupons, appearance prototype, fit/finish and retention qualification |
| Assembly/electrical/UX contract | `docs/design/README.md`, `ELECTRICAL.md`, `UX.md` | Wiring, physical stack, readable controls and required firmware behaviour |
| All coloured views and search BOM | `docs/design/gallery.html`, `bom.html` | View locally in a browser; online gallery/BOM are convenient mirrors |
| Source and build/test instructions | `firmware/`, `scripts/`, `docs/VALIDATION.md` | Quote firmware integration and deliver reproducible source plus evidence |
| Cost assumptions, not quotations | `rfq/costs.json` | Understand reference allowances and excluded costs |
| Independent audit and unresolved gates | `docs/AUDIT.md`, `docs/ROADMAP.md` | Separate corrected source defects from measurements still required |
| Comparison worksheet | `rfq/quote-comparison.csv` | Return the same commercial and technical breakdown |

Before sending: fill your name/company, reply address, delivery country/postcode, desired quote date and whether the Explore option is required. Keep personal contact/shipping details in your outgoing message, outside the public repository. The current delivery assumption is France; a postcode is needed for a delivered quote.

## 2. Ask for the same pilot from everyone

**Base pilot:** one assembled Galia Mini, one spare assembled Mini mainboard plus reader, **three complete DS2401 contact-ID cartridges**, and all firmware/source/test evidence. The Mini enclosure is nominally 65 × 95 × 24 mm; caps add 0.6 mm depth, and a seated cartridge adds 20 mm height.

**Separate option:** one assembled Galia Explore plus one spare Explore mainboard, nominal case 67 × 95 × 24 mm. Include its specified display, lens, battery, speaker and finished enclosure. No NFC alternative or old modular design is in scope.

Ask for separate **5- and 25-unit prototype** prices and **100/1,000-unit feasibility** with MOQ and tooling assumptions. These volume figures are a quotation exercise, not commitments. Do not let a supplier amortize an undisclosed engineering fee into unit prices.

Require one accountable integrator for sourcing, design corrections, programming, wiring, enclosure assembly and testing. A PCBA-only quote is a useful secondary comparison but does not fulfil the base pilot.

## 3. Send this message

**Subject:** GALIA-EVT-001 — Galia Mini / Explore engineering prototype RFQ — quotation only

> Hello,
>
> We are seeking an engineering/box-build partner for a compact children's audio-player development prototype. Please quote against release v0.2.1-rfq and its attached source package/manifest. This is a request for quotation only; do not manufacture, procure chargeable parts or start paid engineering without a separate written authorization.
>
> Base scope: one complete Galia Mini, one spare assembled mainboard plus contact reader, and three complete DS2401 story-selector cartridges. Please quote Galia Explore plus a spare PCBA as a separate option. Also provide 5/25 prototype and 100/1,000 production-feasibility pricing, with explicit MOQ.
>
> Please review `rfq/README.md` and the illustrated engineering dossier before quoting. The project needs engineering/DFM, integrated firmware completion and physical qualification. Existing firmware is muted diagnostics; CAD checks are not physical fit or compliance evidence. Identify which tasks you perform in-house and which require an engineering partner.
>
> Return an itemized quote covering engineering/NRE, exact BOM sourcing, PCB fabrication/assembly, programming/test fixtures, firmware, enclosure/cartridges/finish, harnesses, box-build, QA, packaging and compliant battery shipping. State lead times, currency, Incoterm, taxes/duties, quote validity, substitutions, exclusions, rework responsibility, tooling ownership and complete source handover. Please complete the supplied comparison worksheet or provide an equivalent line-by-line table.
>
> Please list design blockers, proposed changes and verification evidence. No silent substitutions or fabrication from the reference Gerbers. We will agree a corrected native design and acceptance plan before any separate fabrication decision.
>
> Delivery: France, [POSTCODE]. Requested quote date: [DATE]. Contact: [NAME / COMPANY / EMAIL]. Release/package link: [PASTE RELEASE LINK].
>
> Thank you.

## 4. Supplier shortlist and submission route

Public capability pages below were checked for this project; **none has accepted it or given a binding quote**. Use their official enquiry/contact route and request an engineering account manager. Send the same brief to three suppliers first; keep responses private. No outreach has been sent by this project.

| Candidate | Official starting point | Clarification required |
|---|---|---|
| PCBWay | [OEM / box-build](https://www.pcbway.com/helpcenter/placingorders/How_to_Place_an_OEM_Order_.html), [enclosure service](https://www.pcbway.com/pcbdesign/enclosure.html) | Can one team own design review, firmware completion, finished enclosure, wiring and tested delivered sample? |
| Elecrow | [Box-build and final assembly](https://www.elecrow.com/box-build-and-final-assembly-service.html) | Will they support this low quantity and supply engineering/firmware, not just assembly? |
| Seeed Studio | [ODM process](https://www.seeedstudio.com/blog/2025/07/18/understanding-seeed-studios-odm-process-from-concept-to-product/), [testing](https://www.seeedstudio.com/fusion-testing-solutions.html) | Is this scope/quantity eligible, and what engineering/NRE is required? |
| JLCPCB / JLC3DP | [PCB assembly](https://jlcpcb.com/pcb-assembly) | Use as a PCBA/housing cost comparison; confirm final integration, firmware and QA separately rather than assuming inclusion |

If a supplier can only quote PCBA: label the response **partial**, retain its useful costs, and obtain an explicit separate integrator quote before comparing delivered totals. Do not accept an engineering exclusion hidden behind “customer responsibility.”

## 5. Required engineering statement in every reply

Ask the supplier to mark each item **included / excluded / needs investigation**, with a named owner, fixed allowance or capped investigation cost, evidence and timing:

- Power: charger/NTC/current setting, cell protection and lead/polarity envelope, TPS63020 transient margin, USB power paths and fault behaviour.
- Layout/RF: four-layer stack, USB impedance, via-in-pad fill/cap/paste, antenna keepout; Explore backlight boost placement/feedback review.
- Audio/firmware: TLV320DAC3100 and speaker path, headphone detection/mute, fail-mute faults, PCM playback, bookmarks, approved content/card assignment, USB or removable-SD transfer; 5/8 controls and FR/EN text support.
- Mechanical: actual purchased-part measurements; spring travel and reader deflection; ground-first/keyed card insertion; screws/inserts/pullout; band thickness/retention; mated plugs, wire bends/strain relief, display/FPC/lens attachment; switch travel/overtravel, seams, edges, port access and durable markings.
- Content and accessories: supplied original test audio only; no proprietary story catalogue or provider subscriptions are included. MCP, generative creation and cloud subscriptions are outside this initial prototype quotation.
- Applicable conformity and battery transport: provide a reasoned classification/verification roadmap for the intended French/EU use, required lab work and transport documents. Do not treat component certificates or a generic “CE” claim as finished-device evidence.

## 6. Return a quote that can be compared

Use [quote-comparison.csv](quote-comparison.csv). Require **separate totals** for the base pilot, Explore option, each volume tier, and **all one-time engineering/tooling**. Include:

1. Exact manufacturer part numbers and quantities; stock/lead-time date; approved-alternative request list. The 0-cost wire/contact pads are manual/copper features, not purchasable ICs.
2. PCBs, stencil, assembly, setup, inspection and programming fixture; main/reader/token layer/thickness/finish separately.
3. Firmware and engineering completion with deliverables and test scope; distinguish fixed price from time-and-materials, cap and stop conditions.
4. Enclosures, coupons, finishing, cartridge print/assembly, hardware, wiring and test labor.
5. Shipping, packaging, battery compliance handling, currency, tax/duty assumptions and Incoterm. Ask for a delivered total plus a clear tax/duty breakdown.
6. Quote validity, payment stages, calendar lead time from accepted DFM, rework/warranty terms, ownership of native CAD/firmware/tooling and reproducible handover.

**Cost sanity check, not a supplier offer:** current one-card recurring allowances are Mini **€77.99–173.40**, Explore **€71.91–162.06**. One of each with one Mini card is **€149.90–335.46**, plus a shared **€100–250** setup reserve. These omit engineering, firmware, manual finishing/assembly, shipping, tax and conformity. The RFQ's extra two cards and spare PCBAs are additional. **There is no honest delivered pilot total until itemized supplier quotes arrive.** Retail €99/€129 including French VAT are unachieved volume positioning targets, not prototype budgets.

## 7. Evaluate before choosing

Reject an apparently low total if it omits design correction, firmware, fit work, final integration or evidence. Score compliant replies: technical scope/ownership 30%, DFM/test plan 20%, evidence/handover 15%, complete delivered cost 15%, lead time 10%, commercial/rework terms 10%. Record unknowns rather than assigning them zero cost.

Shortlist two replies, then request a written clarification round. Require the supplier to identify the exact package/tag reviewed. Obtain a substitution delta and corrected drawings, not just “equivalent parts.” A general capability claim is not proof that this specific layout or mechanical stack works.

## 8. Hold points and acceptance

| Hold point | Evidence required | Decision |
|---|---|---|
| Quotation | Complete scope, priced exclusions, supplier ownership, delivered breakdown | Owner compares; no spending or fabrication authorized |
| Engineering proposal | Native source changes, DFM findings, exact BOM/substitutions, dimensional stack and test plan | Owner separately authorizes any paid engineering stage |
| Fabrication decision | Accepted corrected native revision; clean ERC/DRC; regenerated manufacturing data; power/fit risks resolved to agreed level | Separate written owner authorization required; this playbook is not that authorization |
| Prototype inspection | Serialized build log, photos, actual dimensional/retention/connector tests, power/charge/thermal and audio fault measurements, firmware tests | Compare to agreed quantitative acceptance criteria; unresolved failures go to rework |
| Source handover | Native KiCad/SCAD/firmware, exact BOM, build instructions, fixture source, measurement data and deviations | Owner verifies reproducibility and completeness before accepting stage |

Agree numeric criteria **before** building: band/insert/card retention forces, switch travel, spring working height/deflection, seam/port clearances, battery/charger thermal conditions, acoustic limits and fault response. The repository records nominal geometry and candidate component limits; it cannot supply measured pass results for a prototype that does not exist.

For the finished-product goal, require additional intended-user usability, applicable conformity testing and production validation. An attractive printed enclosure or successful firmware compilation is not final product qualification.

## 9. Practical launch sequence

- **Day 0:** download the fixed release, fill the five contact/delivery/date fields, send the template and complete package to three official enquiry routes. Save sent package/tag and worksheet privately.
- **After 3–5 business days:** follow up once; ask who owns engineering and whether they reviewed the unresolved gates. Timing is a proposed working schedule, not a supplier commitment.
- **When replies arrive:** normalize currency/Incoterm/scope in the worksheet, request missing lines, shortlist two and hold a technical clarification call.
- **Before any money or fabrication:** approve a concrete corrected design, work statement, stage price and acceptance plan through a separate decision. No purchase, ordering-cart checkout or automatic approval follows from this document.

**Current state:** RFQ material is prepared; no supplier quote, outreach, prototype, physical validation or order is claimed. Keep actual commercial replies and personal data outside this public repository.
