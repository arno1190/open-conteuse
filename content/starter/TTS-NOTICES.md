# Local synthetic demonstration generation

The six draft recordings use the original scripts in this collection. They do not sample competitor stories, music or a named performer's voice. They are generated with the built-in eSpeak NG formant voices `fr-fr` and `en-gb`.

The generation environment downloaded and extracted these official Debian packages locally, without installing them system-wide:

| Component | Version | Source / notice |
| --- | --- | --- |
| eSpeak NG binary | 1.52.0+dfsg-5 | [Upstream](https://github.com/espeak-ng/espeak-ng), [Debian copyright](tts-notices/espeak-ng-copyright.txt) |
| eSpeak NG shared library | 1.52.0+dfsg-5 | [Debian copyright](tts-notices/libespeak-ng1-copyright.txt) |
| eSpeak NG voice data | 1.52.0+dfsg-5 | [Debian copyright](tts-notices/espeak-ng-data-copyright.txt) |
| pcaudiolib | 1.3-1 | [Debian copyright](tts-notices/libpcaudio0-copyright.txt) |
| Sonic library | 0.2.0-13+b1 | [Debian copyright](tts-notices/libsonic0-copyright.txt) |
| FFmpeg, local encoder | 7.1.5-0+deb13u1 | [FFmpeg licensing](https://ffmpeg.org/legal.html); installed build enables GPL and libmp3lame |

The exact package download URLs and SHA-256 values are preserved in [tts-engine-lock.json](tts-engine-lock.json). eSpeak NG's main upstream licence is GPL-3.0-or-later; individual files retain their notices. The Debian pcaudiolib notice has per-file GPL/BSD terms. Sonic is Apache-2.0. These notices remain separate from this collection's CC0 dedication. None of these engine binaries, library binaries or voice-data files are bundled in `content/starter` or the published website; only the generated draft MP3 recordings and reproduction utilities are included.

The repository's MIT licence covers the original generation utility, not the engine. The original story text and illustrations have the separate CC0 dedication. No endorsement, voice-service licence or competitor licence is implied. The generated recordings remain labelled synthetic drafts; exact script review and final-audio review are separate and still pending.
