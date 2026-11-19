# Open Conteuse

An open-source, self-buildable audio handheld project: one platform, two Game Boy inspired variants.

- **Mini (approximately 3–5):** no screen, illustrated NFC cards, spoken navigation and a few buttons.
- **Explore (approximately 6–15):** colour screen, D-pad and A/B, chapters, bookmarks and optional cards.
- **Target for both:** offline audio, battery, Wi-Fi administration, speaker/headphones, USB-C, microSD, downloaded podcasts, branching stories and parent-approved live radio.
- **Parent studio:** local imports, approvals, cards, device sync and a separate AI drafting/review workflow.

## Current state

Working host content/player/studio prototypes, four baseline firmware builds and two compact bring-up builds. The new [compact R1 dossier](docs/compact-r1/README.md) brings together **Mini65×95×22mm** and **Explore67×100×24mm** custom four-layer PCBs, schematics, printable enclosure sources, coloured integration/cutaway views, exact-identity BOMs, cost assumptions and assembly instructions. **Physical hardware, audio limits, battery circuits and mechanical fit remain unvalidated.** Compact diagnostics are muted; the finished integrated-codec playback driver remains a bench milestone. Read the [roadmap](docs/ROADMAP.md) and [compact validation record](docs/compact-r1/VALIDATION.md) for limits.

## Run locally

Python 3.11+, no runtime dependencies for the host foundation:

```sh
sh scripts/check.sh
python3 -m conteuse.demo
python3 -m conteuse.studio --root .studio
```

The studio prints a loopback address and a per-launch token. It imports local audio paths, inspects packs, records exact final-content approval, assigns cards and activates a local library. See [content workflow](docs/CONTENT.md) for CLI import/export, RSS, simulated pairing and editorial approval. The example includes original text only, no audio. A valid draft graph alone never authorizes publication.

[Build firmware](firmware/README.md) and [run CAD checks](hardware/controls/README.md) separately. Default firmware is muted. No board was flashed, no parts ordered and no fabrication submitted.

## Project map

- [Requirements](docs/REQUIREMENTS.md) · [Architecture](docs/ARCHITECTURE.md) · [Research](docs/RESEARCH.md)
- [Content schema](schemas/pack-v1.schema.json) · [Content/studio workflow](docs/CONTENT.md)
- [Firmware and limits](firmware/README.md) · [Firmware licences](firmware/THIRD_PARTY.md)
- [Complete coloured CAD atlas and PDF](docs/visual-atlas) · [Early PNG previews](docs/previews) · [Revised hardware cost](docs/HARDWARE_COST.md)
- [Controls schematic/layout](hardware/controls) · [BOM](hardware/BOM.csv) · [Pinout](hardware/PINOUT.md)
- [Assembly and physical validation](hardware/ASSEMBLY.md) · [Enclosure assumptions](enclosure/DIMENSIONS.md)
- [Roadmap](docs/ROADMAP.md) · [Validation](docs/VALIDATION.md) · [Cloud handoff](docs/CLOUD.md) · [Agent instructions](AGENTS.md)

Original host Python, original CAD and documentation: MIT. Original firmware: GPL-3.0-or-later; dependencies retain their own licences and codec terms. KiCad library footprints retain the upstream library licence/exception. Original example content: CC0-1.0. No commercial story catalogues, proprietary firmware or keys are included.

### Detailed component integration

The [integrated modular design](hardware/integration/README.md) includes exact component identifiers and supplier/search links for every [BOM row](hardware/integration/BOM.csv), native mute-latch KiCad sources, [parametric SCAD and prototype STL files](enclosure/integrated/), and [source-derived integration/exploded PNGs](docs/previews/integrated/). [Updated cost evidence](docs/HARDWARE_COST.md) separates known supplier subtotals from missing quotes and shipping. Physical fit, integrated codec firmware and procurement availability remain explicit release gates.

### Compact successor and console software study

The [compact hardware assessment](docs/research/COMPACT_HARDWARE.md) compares the first design with Miyoo-sized targets and a much cheaper integrated-board direction. The separate [Telmi assessment](docs/research/TELMI_ASSESSMENT.md) maps existing RSS/story features and the remaining sync, radio, approval and recovery work. The [compact R1 implementation](docs/compact-r1/README.md) now develops the custom hardware direction; the prior modular files and atlas remain available as historical prototypes. The Telmi stream remains a separate assessment.
