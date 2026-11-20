#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p work/config/kicad/9.0 work/cache work/data work/current
export XDG_CONFIG_HOME="$PWD/work/config" XDG_CACHE_HOME="$PWD/work/cache" XDG_DATA_HOME="$PWD/work/data"
export KICAD9_FOOTPRINT_DIR=/usr/share/kicad/footprints KICAD9_SYMBOL_DIR=/usr/share/kicad/symbols
cp /usr/share/kicad/template/fp-lib-table work/config/kicad/9.0/fp-lib-table
cp /usr/share/kicad/template/sym-lib-table work/config/kicad/9.0/sym-lib-table
python3 scripts/check_native.py
python3 scripts/export_enclosure.py
