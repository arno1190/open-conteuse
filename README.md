# Open Conteuse · Les Petits Détours

Two current custom handheld designs and an original bilingual listening collection. **Engineering RFQ release: physical validation and integrated audio firmware remain pending. No hardware is offered for sale.**

- **Mini contact ID:** 65 × 95 × 24 mm; a keyed cartridge selects audio stored inside the player. Passive DS2401 serial ID, two wear contacts, no NFC or audio on the card. Cartridge protrudes 20 mm when seated.
- **Explore:** 67 × 95 × 24 mm, 2.4-inch display and button navigation. USB-C charging/data and 3.5 mm headphones on both.
- **Parent studio:** existing local import, exact-revision approval, card assignment and export foundation. Never deployed publicly.

[French showcase](https://arno1190.github.io/open-conteuse/?lang=fr) · [English showcase](https://arno1190.github.io/open-conteuse/?lang=en) · [RFQ](rfq/README.md) · [Design/assembly dossier](docs/design/README.md)

The intended differentiator is parent-controlled, highly personal listening made with their chosen tools and authorised sources. [MCP and provider/TTS connections remain under assessment](docs/PERSONALIZATION.md); no subscription/API compatibility is claimed. [Control UX and tactile-cap design](docs/design/UX.md) define the current refinement.

## Stories and cards

[Three original bilingual adventures](content/starter/README.md), [printable cards](content/starter/cards.pdf), [read-aloud booklet](content/starter/collection.pdf). Paper artwork does not activate the electronic reader. Scripts are editorial drafts; downloadable synthetic recordings and browser fallback are demonstrations, not approved final audio.

## Sources and checks

[Native KiCad](hardware/) · [OpenSCAD and prototype print meshes](enclosure/) · [BOM/cost assumptions](rfq/costs.json) · [Firmware](firmware/README.md) · [Validation](docs/VALIDATION.md) · [Roadmap](docs/ROADMAP.md)

```sh
sh scripts/check.sh
sh scripts/cad-check.sh
PIO=pio sh scripts/firmware-check.sh
python3 -m conteuse.studio --root .studio
```

Python host has no runtime dependencies. KiCad 9, OpenSCAD and PlatformIO are separate CAD/build requirements. The studio binds loopback and prints a per-launch token. Current firmware diagnostics keep audio muted; codec playback, hardware transfer and physical validation are unfinished.

Only the current designs are kept on main; earlier iterations remain in Git history. Original host/CAD/docs MIT; firmware GPL-3.0-or-later; original starter stories/art CC0-1.0. Dependencies retain upstream licences. No proprietary story libraries are included.
