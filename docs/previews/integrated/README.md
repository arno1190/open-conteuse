# Source-derived integration previews

These PNGs project the supplier STL meshes and the exported OpenSCAD carrier at the placements in `hardware/integration/layout.json`. The front and lid are omitted so parts remain visible. The exploded view lifts the carrier layer55mm. PCB-only/MCU/regulator envelopes are identified in the legend; no unverified detailed component model is implied.

- [Mini internal view](mini-integration.png)
- [Mini exploded view](mini-exploded.png)
- [Explore internal view](explore-integration.png)
- [Explore exploded view](explore-exploded.png)

Reproduce with `python3 scripts/render_integrated.py` after exporting the STL files. Physical fit and functional validation remain pending; these are digital prototype views.
- [Mini bare front shell](mini-front.png)
- [Explore bare front shell](explore-front.png)
