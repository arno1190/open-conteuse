#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p work/config/kicad/9.0 work/cache work/data work/cad
export XDG_CONFIG_HOME="$PWD/work/config"
export XDG_CACHE_HOME="$PWD/work/cache"
export XDG_DATA_HOME="$PWD/work/data"
export KICAD9_FOOTPRINT_DIR=/usr/share/kicad/footprints
export KICAD9_SYMBOL_DIR=/usr/share/kicad/symbols
cp /usr/share/kicad/template/fp-lib-table work/config/kicad/9.0/fp-lib-table
cp /usr/share/kicad/template/sym-lib-table work/config/kicad/9.0/sym-lib-table
kicad-cli sch erc hardware/controls/controls.kicad_sch --exit-code-violations --severity-all -o work/cad/erc.rpt
kicad-cli pcb drc hardware/controls/controls.kicad_pcb --schematic-parity --exit-code-violations --severity-all -o work/cad/drc.rpt
python3 scripts/check_cad.py
for variant in mini explore; do
  for part in front back coupon plunger; do
    openscad --hardwarnings -D "variant=\"$variant\"" -D "part=\"$part\"" -o "work/cad/$variant-$part.stl" enclosure/shell.scad > "work/cad/$variant-$part.log" 2>&1
    cat "work/cad/$variant-$part.log"
    if rg -q 'WARNING|ERROR|Simple: *no' "work/cad/$variant-$part.log"; then
      exit 1
    fi
    rg -q '^ *Simple: *yes$' "work/cad/$variant-$part.log"
    rg -q '^ *Volumes: *2$' "work/cad/$variant-$part.log"
  done
done
