#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python3 -m unittest discover -s tests -v
python3 -m conteuse examples/first-adventure/manifest.json
python3 -m conteuse.demo
python3 scripts/check_cad.py

python3 scripts/check_atlas.py

python3 scripts/check_compact.py
