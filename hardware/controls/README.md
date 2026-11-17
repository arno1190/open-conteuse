# Controls PCB v0.1

Native KiCad 9 schematic, project, local symbols and **fully routed** two-layer PCB. Scope: eight normally-open GPIO-to-ground switches, 1×9 harness and four mounting holes. This is the common Mini/Explore control daughterboard, **not a complete power/audio carrier**. Mini leaves three switches unpopulated. See ../PINOUT.md, ../BOM.csv and ../ASSEMBLY.md.

The schematic and PCB share deterministic symbol identities and net assignments. `scripts/generate_controls.py` generates the design using Debian `/usr/bin/python3` with pcbnew/KiCad 9; the routing algorithm is deterministic in geometry, while KiCad may assign fresh object UUIDs. The committed native sources are the review baseline. No copper fill is needed: ground is an explicit routed tree, and traces/vias obey project minima. Do not treat the switch net name RIGHT_B as a second B button; J1.5 is right/next and J1.6 is back/B (variant labels are listed in PINOUT.md).

```sh
# Optional regeneration; no need to regenerate simply to check the files.
XDG_CONFIG_HOME="$PWD/work/config" XDG_CACHE_HOME="$PWD/work/cache" XDG_DATA_HOME="$PWD/work/data" /usr/bin/python3 scripts/generate_controls.py
sh scripts/cad-check.sh
```

The check includes all warnings, no exclusions, and schematic/PCB parity. Reports saved in `work/cad`; the checked release snapshot is in `hardware/reports`. No Gerber/fabrication order is generated or submitted.

Footprints are embedded from KiCad 9 libraries (https://www.kicad.org/libraries/license/, CC-BY-SA-4.0 with the KiCad library exception). Original circuit, symbols, layout generation and documentation are MIT. Preserve upstream footprint/library notices and exception when reusing library data; the exception permits ordinary PCB design distribution.
