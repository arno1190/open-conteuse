"""Run an offline Mini/Explore choice, bookmark and transfer-recovery demo."""
import json
from pathlib import Path
import tempfile
from .packages import activate, active_pack, revision
from .player import Player


def main():
    source = Path(__file__).resolve().parents[1] / "examples/first-adventure"
    with tempfile.TemporaryDirectory() as library:
        pack = json.loads((source / "manifest.json").read_text())
        activate(source, library, revision(pack))
        try:
            activate(source, library, revision(pack), interrupt=True)
        except InterruptedError:
            print("Interrupted transfer: previous library retained")
        player = Player(active_pack(library))
        player.toggle()
        player.ended()
        print(json.dumps(player.view("mini")))
        player.choose(0)
        bookmark = player.bookmark()
        restored = Player(pack)
        restored.restore(bookmark)
        print(json.dumps(restored.view("explore")))
        print("Restart restored", restored.node, "with Wi-Fi off:", not restored.wifi)


if __name__ == "__main__":
    main()
