# Design previews

- `enclosure-design.png`: real OpenSCAD front meshes with separately rendered captive plungers positioned at the documented switch centres. Exterior geometry only; no installed screen, NFC card or speaker is claimed.
- `integration-plan.png`: dimensioned explanatory plan. Controls footprint comes from the actual 70×65 PCB; other module outlines are provisional envelopes from `enclosure/DIMENSIONS.md`. The back is shown in common front coordinates. Dashed outlines are not fitted 3D models; the audio/power block has no designed location, mounts or wiring.
- `controls-pcb.png`: actual native KiCad pad/track coordinates on both copper layers; simplified switch bodies are illustrations. This is the controls daughterboard, not the whole electronic carrier.

These previews were generated from merged PR #1 geometry (merge commit `fd07cad78a4981bebfa6c6a24b061669ce7beabe`). They make the current design visible; physical assembly, component fit/collisions, insertion mute, battery safety and acoustic performance remain pending.

Reproduce from repository root:

```sh
sh scripts/cad-check.sh
mkdir -p work/previews
XDG_CONFIG_HOME="$PWD/work/config" /usr/bin/python3 scripts/export_preview_pcb.py
# Install optional preview requirements in a separate environment, not host runtime:
python3 -m venv work/preview-env
work/preview-env/bin/pip install -r scripts/requirements-preview.txt
work/preview-env/bin/python scripts/render_previews.py
```

Source geometry/copper are reused, not replaced by an invented product render. Colours and simplified component boxes are for readability. See [cost revision](../HARDWARE_COST.md) for the full-unit/prototype budget and supplier evidence.
