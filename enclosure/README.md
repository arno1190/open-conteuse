# Current enclosure and cartridge sources

Millimetres. `design.scad` selects Mini or Explore with `variant="mini"` / `"explore"`; `card.scad` defines the shared Mini serial-ID cartridge. Generated `*-data.scad` inputs come from current native KiCad component/pad coordinates through `scripts/export_mechanical.py`.

Mini65×95×24mm, Explore67×95×24mm; nominal walls1.8mm. Current source datum is case front-view left/topXY and rear exteriorZ0. Export mirrorsY to retain physical PCB handedness. No production shrink, paint allowance, mould draft or material qualification is established.

Run `sh scripts/cad-check.sh` for all native checks and current mesh exports. `mesh-checks.json` records source hashes, manifold/volume checks and intersections. The rigid insertion sweep deliberately excludes only the compliant0.35mm detent bump; force/recovery/fatigue need physical tests.

[Print-file map](print/README.md), [full assembly/clearance dossier](../docs/design/README.md), [RFQ](../rfq/README.md). Source geometry and exported STLs support prototype trials. They do not establish received-component fit, safety or suitability for children.
