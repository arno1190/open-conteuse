"""Validate one local draft manifest."""
import argparse
import json
import sys
from pathlib import Path
from .manifest import validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        pack = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError, RecursionError) as exc:
        print(f"Cannot read manifest: {exc}", file=sys.stderr)
        return 2
    errors = validate(pack)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Valid draft story graph (audio and publication approval not checked).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
