#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p work/config/kicad/9.0 work/cache work/data work/current
export XDG_CONFIG_HOME="$PWD/work/config" XDG_CACHE_HOME="$PWD/work/cache" XDG_DATA_HOME="$PWD/work/data"
export KICAD9_FOOTPRINT_DIR=/usr/share/kicad/footprints KICAD9_SYMBOL_DIR=/usr/share/kicad/symbols
cp /usr/share/kicad/template/fp-lib-table work/config/kicad/9.0/fp-lib-table
cp /usr/share/kicad/template/sym-lib-table work/config/kicad/9.0/sym-lib-table
for board in mini explore card-reader story-card; do
 mkdir -p "hardware/$board/checks"
 kicad-cli sch erc "hardware/$board/$board.kicad_sch" --exit-code-violations --severity-all -o "hardware/$board/checks/erc.rpt"
 kicad-cli pcb drc "hardware/$board/$board.kicad_pcb" --schematic-parity --exit-code-violations --severity-all -o "hardware/$board/checks/drc.rpt"
done
python3 scripts/export_enclosure.py
