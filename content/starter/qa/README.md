# Automatic transcript screen

`transcript-qa.json` binds each approximate transcript to the exact script and MP3 bytes, records the local ASR model/runtime and reports normalized word edit distance and measured editorial words/minute. These transcripts are machine output, not corrected scripts or approval evidence. Names, homophones, punctuation and number spellings can inflate error rates; inspect differences rather than treating the score as a voice-quality rating. No fixed score automatically approves a recording.

The QA tool uses local **faster-whisper base** (`Systran/faster-whisper-base`, converted from OpenAI Whisper) with CPU int8 and a fixed French/English language. Model weight hash and package versions are recorded. These are separate QA dependencies; they are not shipped to the website or required by ordinary host checks. [faster-whisper](https://github.com/SYSTRAN/faster-whisper) and [Whisper](https://github.com/openai/whisper) retain their MIT licences. No audio is uploaded to a recognition service.

```sh
work/narration-venv/bin/pip install -r content/starter/requirements-audio-qa.txt
HF_HOME="$PWD/work/current/huggingface" XDG_CACHE_HOME="$PWD/work/cache" \
  work/narration-venv/bin/python scripts/check_narration_transcripts.py --fetch-model
python3 content/starter/validate.py --media
```

FFmpeg decodes to mono16kHz float PCM before transcription, avoiding dependence on the recognition wrapper's container-decoding API. Whole-file decode/format/loudness checks are separately recorded in `../audio-quality.json`.

Before final audio approval, listen to **every complete file** against the authoritative script: missing/repeated words, names, dialogue, optional pause, rhythm and ending; assess voice/pacing with the intended audience and playback chain. Script and final-audio approvals remain separate and pending.

Current screen: English normalized word error is approximately 0.2–2.9%; French is 13.3% (Milo), 14.8% (Nori) and 25.1% (Pipo). These values include homophones, inflections and invented names/sound effects. Prioritize a complete French Pipo audition, especially “la rouge sauta si haut qu’elle coiffa la cuillère” and the “Tap” rhythm. Some machine phrases are garbled; this report cannot establish whether the synthesizer or recognizer caused them. No recording has passed final listening approval.
