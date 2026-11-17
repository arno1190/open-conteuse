"""Deterministic playback policy independent of audio hardware."""
from .manifest import validate
from .packages import revision


class Player:
    def __init__(self, pack):
        errors = validate(pack)
        if errors:
            raise ValueError("; ".join(errors))
        # Own immutable-by-convention snapshot, not the caller's mutable graph.
        import copy
        self.pack = copy.deepcopy(pack)
        self.nodes = {node["id"]: node for node in self.pack["nodes"]}
        self.node = pack["start"]
        self.state = "paused"
        self.history = []
        self.headphones = False
        self.wifi = False
        self.radio = False
        self.retries = 0

    def toggle(self):
        self.state = "paused" if self.state == "playing" else "playing"

    def ended(self):
        self.state = "choice" if self.nodes[self.node].get("choices") else "ended"

    def choose(self, index):
        choices = self.nodes[self.node].get("choices", [])
        if self.state != "choice" or type(index) is not int or not 0 <= index < len(choices):
            raise ValueError("choice unavailable")
        self.history.append(self.node)
        self.node = choices[index]["target"]
        self.state = "playing"

    def back(self):
        if self.history:
            self.node = self.history.pop()
        self.state = "paused"

    @property
    def speaker_enabled(self):
        return self.state == "playing" and not self.headphones

    def select_local(self, offline=True):
        self.radio = False
        self.wifi = not offline
        self.state = "paused"

    def start_radio(self, approved, online):
        if not approved:
            raise ValueError("station not approved")
        self.radio, self.wifi, self.retries = True, True, 0
        self.state = "buffering" if online else "offline"

    def stream_failed(self):
        self.retries += 1
        self.state = "offline" if self.retries >= 3 else "buffering"

    def bookmark(self):
        return {"revision": revision(self.pack), "node": self.node, "history": list(self.history)}

    def restore(self, bookmark):
        if (bookmark.get("revision") != revision(self.pack)
                or not isinstance(bookmark.get("node"), str)
                or bookmark.get("node") not in self.nodes
                or not isinstance(bookmark.get("history"), list)
                or len(bookmark["history"]) > 1000
                or any(not isinstance(n, str) or n not in self.nodes for n in bookmark["history"])):
            raise ValueError("stale or invalid bookmark")
        self.node, self.history = bookmark["node"], list(bookmark["history"])
        self.state = "paused"

    def view(self, variant):
        choices = [c["label"] for c in self.nodes[self.node].get("choices", [])]
        if variant == "mini":
            return {"spoken": self.nodes[self.node]["text"], "spoken_choices": choices}
        if variant == "explore":
            return {"title": self.pack["title"], "text": self.nodes[self.node]["text"], "menu": choices}
        raise ValueError("unknown variant")
