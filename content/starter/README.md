# Les petits détours / Little Detours

Three original, fictional listening stories in French and English, each around 300 words, with an optional activity away from the screen. The working collection name is not a cleared trademark. Mallow informed the broad idea of a warm, audio-first family experience; these texts, characters and illustrations are original and do not adapt or reproduce a competitor's catalogue.

- [Read-aloud booklet](collection.pdf): seven A4 pages, including introduction and all six language versions.
- [Printable cards](cards.pdf): one A4 sheet containing three 40 × 60 mm fronts and three matching activity backs; print at 100%, check the 40 mm ruler and have an adult cut and pair them. The sheet does not assume duplex alignment.
- [Electronic cartridge artwork labels](cartridge-labels.pdf): three separate **33.6 × 38.6 mm** adhesive-label designs for the actual cartridge recess; see the fit assumptions below.
- [Structured catalogue](index.json): bilingual titles, scripts, activities, intended audience guidance and review state.
- [Vector artwork](cards): editable, original SVG front/back faces.
- Individual `.fr.md` and `.en.md` files include recording directions and optional pauses.

The paper artwork does **not** activate the contact-ID player. An electronic cartridge needs the specified serial-ID PCB and a parent-created local assignment. Artwork IDs such as `milo-moon-post` are catalogue keys, not DS2401 ROM identifiers. No electronic IDs, executable device packs or child-library assignments are supplied here.

The intended 4–7 age range and roughly four-minute reading time are editorial guidance, not a tested age classification or a measured recording duration. Children may simply listen; answers and movement are optional. No health, learning-outcome or therapeutic claims are made. There has been no child usability test.

**Script approval is pending. Final audio approval is pending.** Six downloadable MP3 demonstrations are included under [audio](audio), generated entirely locally using eSpeak NG. They are robotic synthetic draft voices, not finished performer narration or final approved audio. Downloaded files can be listened to without a screen or network. The showcase may also offer browser speech synthesis as a fallback; its availability and processing depend on the browser or operating system. Review the script first, then review the exact final recording separately before activating a library. A text or audio change invalidates its earlier approval.

All original collection text and artwork are dedicated under [CC0-1.0](LICENSE.txt). The asset-generation utility is covered by the repository's MIT licence. This does not license any competitor's work or third-party voice service. No commercial recordings or music are included.

Rebuild PDFs and SVGs with Python and ReportLab:

```sh
python3 content/starter/generate_assets.py
python3 content/starter/validate.py
```

The utility uses the system DejaVu fonts, embedded under their font licence in the PDFs; see [font notice](FONT-LICENSE.txt). Generated public assets mirror to `site/content/`. The JSON catalogue and Markdown scripts are authoritative text sources; PDFs are reading/printing derivatives. Visual QA on 20 November 2026 checked the card sheet and a complete story page after rasterization; printed scale and real-world readability remain to be checked on paper.

## Electronic cartridge artwork labels

[The separate A4 label sheet](cartridge-labels.pdf) provides original character artwork and short bilingual titles for the electronic cartridge. [SVG label sources](cartridge-labels) and a [dimension record](cartridge-labels.json) are included. [Sheet preview](cartridge-labels-preview.png).

Each rectangular label is **33.6 × 38.6 mm**, centered in the **34 × 39 mm** recess. In the cartridge’s canonical coordinates, the recess is **X3–37, Y4–43 mm** and the label occupies **X3.2–36.8, Y4.2–42.8 mm**, leaving **0.2 mm nominal clearance at each edge**. The paper plus adhesive stack is assumed to be **at most 0.15 mm thick**. These dimensions describe the intended artwork and placement; printed scale, placement tolerance, adhesion, wear and real enclosure fit remain **physically unvalidated**. Print at 100%, verify the 40 mm ruler and have an adult prepare and apply the label.

The artwork keys `MILO-01`, `NORI-02` and `PIPO-03` are visual catalogue labels, **not electronic ROM values**. No DS2401 ROM identifier is supplied. An assembled DS2401 cartridge and a parent-created assignment to approved local audio are still required. Printing or attaching a label does not activate a player. Script and final-audio approvals remain pending.

Regenerate just these labels without rewriting existing story/card derivatives:

```sh
python3 content/starter/generate_assets.py --labels-only
```

The default asset-generation command also regenerates the labels. If `pdftoppm` is available, it updates the PNG label-sheet preview as well.

## Downloadable synthetic listening demonstrations

All six scripts have a local MP3 demonstration recording: French voice `fr-fr` and English voice `en-gb`, generated with **eSpeak NG 1.52.0** at 105 words/minute, pitch 45 and amplitude 70. Generation inserts two-second paragraph pauses and eight-second pauses after listener invitations. Actual measured file durations range from about **3:01 to 3:40**; the approximate four-minute editorial label was not a measured runtime promise.

These are deliberately labelled **synthetic draft demonstrations**, with robotic pronunciation and phrasing. They have **not** received listening/editorial approval or child testing. Audio decoding, duration, format and exact-byte checks are complete; a human listening pass and final narration remain pending. The files are mono MP3, 22,050 Hz, 64 kbit/s, normalized digitally to a target −23 LUFS and −3 dBTP. This does not establish a safe acoustic output level on any speaker or headphones.

The exact UTF-8 script string and exact MP3 bytes are SHA-256 recorded in [audio-generation.json](audio-generation.json) and the catalogue. **All six final-audio approval states remain pending.** No player pack is activated. These listening MP3s are not device export packs; the current PCM-only device path requires supported conversion and parent approval.

Reproduce with FFmpeg and the pinned local engine:

```sh
python3 content/starter/generate_audio.py --fetch-engine
python3 content/starter/validate.py
```

`--fetch-engine` downloads the five SHA-256-pinned official Debian packages listed in [tts-engine-lock.json](tts-engine-lock.json), extracts only into ignored `work/current/tts/`, and makes no system installation. This bundle is for Debian amd64. With the engine already extracted, omit the flag. Alternate local locations can be provided with `ESPEAK_NG_BIN` and `ESPEAK_NG_DATA_ROOT`; generation checks version 1.52.0. No external TTS provider, paid service, credentials, music or commercial recordings are used.

See [TTS dependency notices](TTS-NOTICES.md). Engine binaries and voice-data files are not distributed in the public content or site.

Direct listening downloads (synthetic drafts, final-audio approval pending):

| Story | Français | English |
| --- | --- | --- |
| Milo / Moon Post | [MP3 · 3:01](audio/milo-moon-post.fr.mp3) | [MP3 · 3:15](audio/milo-moon-post.en.mp3) |
| Nori / Pocket Cloud | [MP3 · 3:07](audio/nori-cloud-pocket.fr.mp3) | [MP3 · 3:21](audio/nori-cloud-pocket.en.mp3) |
| Pipo / Sock Orchestra | [MP3 · 3:21](audio/pipo-sock-orchestra.fr.mp3) | [MP3 · 3:40](audio/pipo-sock-orchestra.en.mp3) |

### Recognition while the cartridge is inserted

The electronic-cartridge labels reserve a **12.8 mm-high recognition header**, located **1.2–14.0 mm down from the label's top edge**, containing both a distinct character icon and the large short name **MILO**, **NORI** or **PIPO**. The label top is placed toward the exposed handle at canonical cartridge **Y4.2 mm**. This header therefore occupies cartridge **Y5.4–18.2 mm**, wholly within the nominal exposed **Y0–20 mm** handle region when inserted. The first **15.8 mm** of the label is nominally visible; the header leaves **1.8 mm** before the insertion boundary. The lower illustration and bilingual story title are additional detail visible before insertion, rather than the only means of recognition.

These are layout assumptions for the nominal cartridge geometry, not a verified child-recognition result. Real print placement, enclosure occlusion, installed-label orientation, wear and readability remain pending physical review. Install the label with its short-name header toward the handle. Label dimensions, paper/adhesive thickness allowance, pending editorial approval and the requirement for an assigned electronic DS2401 cartridge are unchanged.
