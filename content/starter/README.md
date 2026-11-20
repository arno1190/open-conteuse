# Galia listening collection

Three original fictional stories, each in French and English, with matching illustrated play cards and electronic-cartridge labels. **Editorial revision2** replaces the earlier vignettes with a playful puzzle (Milo), a gentle rescue (Nori) and a comic rhythm adventure (Pipo). Each has a clear goal, failed attempts, a protagonist-led resolution and one optional imaginative invitation. Children can simply listen; no answer is recorded or interpreted.

[Read-aloud booklet](collection.pdf) · [paper cards](cards.pdf) · [cartridge labels](cartridge-labels.pdf) · [catalogue](index.json) · [voice credits](TTS-NOTICES.md).

## Narration

The current six MP3 previews use **Kokoro 82M v1.0**, a neural preset engine also supported by [Voicebox](https://github.com/jamiepine/voicebox/blob/main/docs/content/docs/overview/preset-voices.mdx). We run the engine locally through pinned **kokoro-onnx 0.6.1**, rather than operating the Voicebox app. French uses **ff_siwis**; English uses **bf_emma**. These are fixed model presets, not custom or celebrity voice clones. There is no paid service, API key or account.

Dialogue stays connected in phrase groups rather than receiving a fixed pause after every line. There is one 3-second reflection pause per story. Model speed and pitch-preserving pacing/loudness processing are recorded exactly in the render plans. Actual durations appear on the website and in the catalogue; the files are mono 22,050 Hz MP3 at 96 kbit/s. Digital targets are−23 LUFS/−3 dBTP; measured results are in [audio-quality.json](audio-quality.json), and do not establish safe hardware acoustic levels.

**Script and final-audio approval remain separate and pending.** Independent text review and automatic media/transcript checks do not replace a full listening review for pronunciation, expression, completeness and suitability. The suggested 4–7 age range is editorial guidance, not a tested classification. No developmental, learning or therapeutic outcomes are claimed.

Every recording is in the current immutable [audio batch](audio), with its generation receipt and `CREDITS.txt`. French files embed SIWIS attribution; all files embed a voice-source reference. [Full notices](TTS-NOTICES.md) explain model/runtime terms and the SIWIS CC BY 4.0 dataset credit. Original scripts and card artwork are CC0 under [LICENSE.txt](LICENSE.txt); that dedication does not override fonts, models, datasets or third-party terms.

## Reproduce and verify

```sh
python3 -m venv work/narration-venv
work/narration-venv/bin/pip install -r content/starter/requirements-narration.txt
work/narration-venv/bin/python content/starter/generate_audio.py --fetch-engine
python3 content/starter/validate.py --media
python3 content/starter/generate_assets.py
```

`--fetch-engine` downloads model/voice files only into ignored `work/current/neural-tts/` and checks full SHA-256 against [tts-engine-lock.json](tts-engine-lock.json). No model or runtime binaries are distributed. FFmpeg/FFprobe are required for generation and media QA; ReportLab/Pillow/Poppler are separate print-artifact tools.

All six recordings must render and decode successfully before the catalogue can select the complete immutable batch. Existing batches are checked against their exact MP3 and credit hashes before reuse. A failed generation leaves the prior catalogue usable. A crash between metadata/mirror updates makes validation fail; the public build runs that preflight and refuses an inconsistent package. No generation approves or activates a child library. These MP3 listening previews are not firmware export packs: the current device profile requires supported PCM conversion and exact-revision parent approval.

The ordinary stdlib validation checks exact scripts/render plans, model/voice provenance, audio hashes, recorded media QA, credits and public mirrors. `--media` additionally probes/fully decodes the actual files and remeasures digital loudness/peak. Automated transcript QA is described in `qa/`; it is a screen for omissions, not a listening-quality approval.

## Voicebox authoring option

Voicebox offers local preset voices and a stories editor. For a comparable manual workflow: select Kokoro and the matching preset, import one revised script, generate a short audition, then render and export lossless audio. Review the whole recording before making the delivery MP3. Its Qwen and other engines are separate candidates for expressive narration; hardware and licence requirements differ. A supported preset engine here does not mean Galia already has a Voicebox/MCP or subscription adapter. Parent-studio provider integration remains a future milestone.

## Paper cards and electronic labels

The printable paper cards are40 × 60 mm fronts/activity backs. They **do not** trigger the electronic reader. Inserts are33.6×38.6mm paper, maximum0.15mm thick without adhesive, behind a34×39×0.50mm clear PETG window. The internal pocket is34.4×39.4mm; paper is inset0.2mm from the window edges and0.4mm from the pocket edges. An adult opens the two card screws to replace it. Print at100%, check the40mm ruler and have an adult prepare them. Fit, placement, window retention, wear and child readability remain physically unvalidated.

Electronic-cartridge keys MILO-01/NORI-02/PIPO-03 are artwork identifiers, not DS2401 ROMs. A specified assembled serial-ID PCB and a parent-created local assignment are required. The recognition icon/name occupies cartridgeY5.4–18.2mm, inside the nominal exposed20mm handle; it remains a layout assumption, not measured recognition evidence.

PDF/SVG artwork comes from `generate_assets.py`; deterministic PDF metadata avoids timestamp-only changes. Embedded DejaVu fonts retain [their licence](FONT-LICENSE.txt). `--labels-only` regenerates only cartridge labels; the default command also rebuilds paper cards and the read-aloud booklet. The catalogue/Markdown scripts are authoritative text; print files are derivatives.
