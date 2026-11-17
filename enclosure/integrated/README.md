# Integrated prototype enclosure

Use `integrated.scad`, generated catalogue data, and the manufacturer-reference meshes in `models/`. This replaces the original placeholder shell for this modular configuration. `print/` contains versioned prototype STL exports and a SHA256/bounds manifest. Purchased-part meshes under `models/` must never be printed as case parts.

Set `variant="mini"` or `"explore"`, and `part` to front/lid/carrier/battery_cover/mcu_retainer/regulator_retainer/switch_retainer/button/coupon/speaker_spacer. Assembly mode includes the purchased parts, carrier, retainers, battery cover and lid; `exploded=55` separates layers for inspection. The [printed-parts BOM](print/assembly_BOM.csv) identifies every file, quantity, bounds and hash. Print two MCU retainers and5Mini/8Explore buttons; other listed pieces one each. The fit coupon is additional. Shared-part exports are duplicated by variant for simple complete downloads.

Start with the coupon. Review the slicer and support placement before printing a full shell. The exports are digitally closed meshes with nonnegative print Z, not printer-calibrated G-code or guaranteed physical fits. Dimensions, assembly sequence, screw stackups, supplier conflicts and pending MCU/switch measurements are documented in [hardware integration](../../hardware/integration/README.md). All physical validation remains pending.

Rebuild: `python3 scripts/integrated_hardware.py && python3 scripts/export_integrated.py`. OpenSCAD2021.01 is the checked renderer. Model hashes are verified before host/CAD checks. Do not hand edit generated_data.scad.

The largest flat part is112×210mm before a brim. Confirm your printer's usable bed area (and support/brim margin), material profile and calibration; no printer model has been specified. A210mm axis leaves no brim margin on a210mm bed. The enclosure's deep front is47.6mm tall; internal cantilevers need explicit slicer support review.
