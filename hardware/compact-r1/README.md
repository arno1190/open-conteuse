# Compact R1 native hardware

Start with the [combined design dossier](../../docs/compact-r1/README.md), [assembly guide](../../docs/compact-r1/ASSEMBLY.md) and [electrical contract](../../docs/compact-r1/ELECTRICAL.md).

- `mini/mini.kicad_pro` and `explore/explore.kicad_pro`: independent complete four-layer 1.2 mm boards and corresponding schematics, with local custom libraries.
- `*-BOM.csv`: all references, exact candidate identifiers, footprint/source/query and price assumptions. External cut/standard parts are distinguished from manufacturer catalogue parts.
- `*-mechanical.json`: placed native component envelopes, peripheral coordinates, clearance reserves and dimensional evidence/assumptions.
- `*-copper.json`: native pads/tracks/vias exported for the coloured views.
- `checks/`: final native all-severity ERC/DRC reports, including schematic parity.
- `verification.json` and `manifest.json`: check results and frozen source/artifact integrity.

Run `sh scripts/compact-check.sh` with KiCad9, its standard libraries, Python pcbnew and OpenSCAD installed. `sh scripts/check.sh` also verifies host behaviour and frozen design artefacts. `sh scripts/firmware-check.sh` builds all six firmware profiles.

Native routed boards are the reviewable layout source. `scripts/compact_design.py` / `generate_compact_pcb.py` regenerate the initial schematic/placement, **overwriting routing**; they are not a harmless final-artifact refresh. Routing used Freerouting1.9.0 with the regulator's local copper constrained, followed by native KiCad plane fill and DRC. Final routed native boards are the layout source; optional `finish_compact_pcb.py --work-stage ... mini explore` development imports require operator-supplied routing sessions in `work/`. `import_compact_routes.py` requires the matching input DSN because SES sessions omit unchanged protected copper. No fabrication files were uploaded or ordered.

After an intentional board change, export mechanical/copper data with `/usr/bin/python3 scripts/compact_mechanical.py` and `/usr/bin/python3 scripts/export_compact_geometry.py`, regenerate SCAD data, rerun CAD/mesh checks, render both variants using Blender4.3, rebuild the dossier and regenerate the integrity manifest. Any changed source invalidates existing image receipts and requires review again.

Physical fit, electrical/audio/RF/thermal behaviour and battery integration remain pending. The files are engineering prototypes, not an authorized production release.
