# Open Conteuse

An open-source, self-buildable audio handheld project: one platform, two Game Boy inspired variants.

- **Mini (approximately 3–5):** no screen, illustrated NFC cards, spoken navigation and a few buttons.
- **Explore (approximately 6–15):** colour screen, D-pad and A/B, chapters, bookmarks and optional cards.
- **Target for both:** offline audio, battery, Wi-Fi administration, speaker/headphones, USB-C, microSD, downloaded podcasts, branching stories and parent-approved live radio.
- **Parent studio:** local imports, approvals, cards, device sync and a separate AI drafting/review workflow.

## Current state

Working host content/player/studio prototypes, four compiling ESP32-S3 firmware configurations, a routed/checkable KiCad controls PCB and two OpenSCAD enclosure variants. **No physical hardware, audio limits, battery circuit or mechanical fit has been validated.** The controls board is not a complete audio/power carrier; the shell is a dimensional fit study. Read the [roadmap](docs/ROADMAP.md) and [actual validation record](docs/VALIDATION.md) for implemented behaviour and limits.

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
- [PNG design/integration previews](docs/previews) · [Revised hardware cost](docs/HARDWARE_COST.md)
- [Controls schematic/layout](hardware/controls) · [BOM](hardware/BOM.csv) · [Pinout](hardware/PINOUT.md)
- [Assembly and physical validation](hardware/ASSEMBLY.md) · [Enclosure assumptions](enclosure/DIMENSIONS.md)
- [Roadmap](docs/ROADMAP.md) · [Validation](docs/VALIDATION.md) · [Cloud handoff](docs/CLOUD.md) · [Agent instructions](AGENTS.md)

Original host Python, original CAD and documentation: MIT. Original firmware: GPL-3.0-or-later; dependencies retain their own licences and codec terms. KiCad library footprints retain the upstream library licence/exception. Original example content: CC0-1.0. No commercial story catalogues, proprietary firmware or keys are included.
