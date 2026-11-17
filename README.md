# Open Conteuse

An open-source, self-buildable audio handheld: one electronics platform, two Game Boy inspired versions.

- **Mini (approximately 3–5):** no screen, illustrated NFC cards, spoken navigation and a few buttons.
- **Explore (approximately 6–15):** colour screen, D-pad and A/B buttons, chapters, bookmarks and optional cards.
- **Both:** battery, Wi-Fi administration, speaker, 3.5 mm headphones, USB-C, microSD, downloaded podcasts, personal audio, branching stories and parent-approved live radio.
- **Parent studio:** imports, RSS subscriptions, device sync, card assignments and an AI drafting/review/publishing workflow.

## Status

Early software foundation and design brief. No PCB, enclosure, firmware or physical performance has been validated. This repository currently contains a working story-pack validator and tests; the studio and player remain to be built.

## Quick start

Python 3.11 or newer; no external dependencies for the current foundation.

```sh
python3 -m unittest discover -s tests -v
python3 -m conteuse examples/first-adventure/manifest.json
```

The example contains original text only. Audio assets will be generated or recorded later. Validation checks graph and publication metadata, not audio existence or factual accuracy.

## Project map

- [Requirements](docs/REQUIREMENTS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Research and sources](docs/RESEARCH.md)
- [Hardware and bench validation](hardware/README.md)
- [Roadmap and current state](docs/ROADMAP.md)
- [Codex cloud handoff](docs/CLOUD.md)
- [Agent instructions](AGENTS.md)

Code and documentation: MIT. Original example content: CC0-1.0 (see examples/LICENSE). Third-party content and upstream software retain their own licences. No commercial audio catalogues are included.
