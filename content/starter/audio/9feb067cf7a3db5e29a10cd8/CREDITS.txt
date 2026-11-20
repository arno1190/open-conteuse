# Neural narration sources and voice credits

The current six original-script demonstrations use **Kokoro 82M v1.0**, run locally through **kokoro-onnx 0.6.1** on CPU. French preset **ff_siwis** and British English preset **bf_emma** are fixed model voices. No celebrity voice, competitor recording, uploaded reference voice or custom clone is used. These are synthetic interpretations, not recordings by a hired performer.

Kokoro is one of [Voicebox's documented preset engines](https://github.com/jamiepine/voicebox/blob/main/docs/content/docs/overview/preset-voices.mdx). We used the engine directly; we did **not** install or operate the Voicebox desktop application. The [Voicebox site](https://voicebox.sh/) describes its local studio/API/MCP workflow. That separate app is a useful authoring option, not an already connected Galia provider.

| Dependency | Source and terms | Reproduction record |
|---|---|---|
| Kokoro model and voice presets | [hexgrad/Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M), declared Apache-2.0 | ONNX/voice release URLs and full SHA-256 in `tts-engine-lock.json`; [Apache text](tts-notices/Kokoro-model-Apache-2.0.txt) |
| ONNX conversion/runtime wrapper | [thewh1teagle/kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx), MIT | Pinned 0.6.1; [licence](tts-notices/kokoro-onnx-MIT.txt) |
| Text phonemization | [phonemizer](https://github.com/bootphon/phonemizer), GPL-3.0; [eSpeak NG](https://github.com/espeak-ng/espeak-ng), GPL-3.0-or-later | Pinned Python package/loader versions; [phonemizer licence](tts-notices/phonemizer-GPL.txt), [eSpeak licence](tts-notices/espeak-ng-GPL.txt). eSpeak supplies phonemes, **not** the synthesized acoustic voice |
| Encoder | [FFmpeg](https://ffmpeg.org/legal.html), installed build and its configuration | Actual version and audio filter recorded in the generation receipt; encoder binaries are not distributed |
| Numeric/audio libraries | ONNX Runtime, NumPy, SoundFile and transitive packages retain their own licences | Exact install versions in `requirements-narration.txt`; no dependency binaries bundled |

## French voice dataset attribution

Kokoro's [voice table](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md) and [model card](https://huggingface.co/hexgrad/Kokoro-82M) credit **SIWIS**, licensed **CC BY 4.0**, among its training data. Credit: Junichi Yamagishi, Pierre-Edouard Honnet, Philip Garner and Alexandros Lazaridis (2017), *The SIWIS French Speech Synthesis Database, 2016*, University of Edinburgh, Centre for Speech Technology Research. [Dataset and licence record](https://doi.org/10.7488/ds/1705).

The Galia recordings are newly synthesized from revised original scripts, with pacing adjustments and digital loudness processing; they are not copies of the dataset's recordings. No author, speaker or institution endorsement is implied. Preserve this attribution with redistributed French previews. English **bf_emma** is the model's named preset, not a claim to imitate a named performer.

Original story text/card art remains CC0 under `LICENSE.txt`. That dedication does not override model, dataset, font, dependency or voice-service terms. Model weights, phonemizer data, engine and encoder binaries are not included in the public site or RFQ package.

All script and final-audio approvals remain pending. Hashes, decoding, format, loudness and automatic transcript checks are engineering QA, not listening/editorial approval or child-suitability evidence. Digital normalization does not establish safe acoustic output on the hardware.
