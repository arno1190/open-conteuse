"""Source-backed editorial state, offline fake narration; no generated facts asserted."""
import copy
import hashlib
from .packages import canonical


class Draft:
    def __init__(self, script, sources):
        if not isinstance(script, str) or not script.strip() or not sources or not all(
                isinstance(s, dict) and s.get("url", "").startswith("https://") and s.get("title") for s in sources):
            raise ValueError("script and source citations required")
        self.script = script
        self.sources = copy.deepcopy(sources)
        self.script_approval = None
        self.audio = None
        self.audio_approval = None

    @property
    def revision(self):
        return hashlib.sha256(canonical({"script": self.script, "sources": self.sources})).hexdigest()

    def approve_script(self):
        self.script_approval = self.revision

    def narrate(self, provider):
        if self.script_approval != self.revision:
            raise ValueError("current script requires editorial/factual approval")
        self.audio = bytes(provider(self.script))
        if not self.audio:
            raise ValueError("empty narration")
        self.audio_approval = None
        self.narrated_revision = self.revision
        return self.audio

    def approve_audio(self):
        if self.audio is None or self.script_approval != self.revision or self.narrated_revision != self.revision:
            raise ValueError("current approved script must be narrated first")
        self.audio_approval = hashlib.sha256(self.audio).hexdigest()

    def publication(self):
        if (self.script_approval != self.revision or self.audio is None
                or self.narrated_revision != self.revision
                or self.audio_approval != hashlib.sha256(self.audio).hexdigest()):
            raise ValueError("script and exact final audio approvals required")
        return {"script_revision": self.revision, "audio_sha256": self.audio_approval,
                "transcript": self.script, "citations": copy.deepcopy(self.sources)}


def fake_narrator(script):
    """Deterministic short PCM tone for pipeline tests; not speech or final content."""
    import io
    import wave
    import math
    import struct
    out = io.BytesIO()
    with wave.open(out, "wb") as wav:
        wav.setparams((1, 2, 8000, 0, "NONE", "not compressed"))
        wav.writeframes(b"".join(struct.pack("<h", int(800 * math.sin(2 * math.pi * 440 * i / 8000))) for i in range(800)))
    return out.getvalue()
