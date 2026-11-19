#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p work/config/kicad/9.0 work/cache work/data work/compact-check
export XDG_CONFIG_HOME="$PWD/work/config"
export XDG_CACHE_HOME="$PWD/work/cache"
export XDG_DATA_HOME="$PWD/work/data"
export KICAD9_FOOTPRINT_DIR=/usr/share/kicad/footprints
export KICAD9_SYMBOL_DIR=/usr/share/kicad/symbols
cp /usr/share/kicad/template/fp-lib-table work/config/kicad/9.0/fp-lib-table
cp /usr/share/kicad/template/sym-lib-table work/config/kicad/9.0/sym-lib-table
for v in mini explore; do
 kicad-cli sch erc "hardware/compact-r1/$v/$v.kicad_sch" --exit-code-violations --severity-all -o "work/compact-check/$v-erc.rpt"
 kicad-cli pcb drc "hardware/compact-r1/$v/$v.kicad_pcb" --schematic-parity --all-track-errors --exit-code-violations --severity-all -o "work/compact-check/$v-drc.rpt"

done
python3 scripts/export_compact_meshes.py
/usr/bin/python3 scripts/check_compact_native.py
python3 scripts/check_compact.py
