# Compact R1 mechanical sources

`compact.scad` builds both nominal compact devices from native-PCB-derived data. Mini case65×95×22 mm; Explore 67×100×24 mm. Captive keys add0.6 mm beyond the front face. These are engineering prototype sources; physical validation is pending, and there is no fabrication or child-use release.

For printing, use one variant's `print/*-print_front.stl`, `*-back.stl` `*-bridge.stl` speaker keeper, and five/eight copies of `*-button.stl`. `*-buttons.stl` is an alternative arranged key plate. The other front STL retains assembly coordinates for inspection. Print/insert coupon first. See the [assembly procedure](../../docs/compact-r1/ASSEMBLY.md), [dimensions](../../docs/compact-r1/DIMENSIONS.md) and generated print manifest for orientation, material assumptions, geometry hashes and volume estimates.

OpenSCAD `part` selects assembly, exploded, section_x, section_y, front, back, print_front, pcb, components, peripherals, button, buttons, bridge or coupon. Interference-only modes are verification diagnostics; intentional antenna/keeper mounting contacts is checked separately. `variant` is mini or explore. Neither enclosure is a scaled copy of the old modular shell.

The two SVG outlines define the custom lens and speaker gasket. They are drawing-defined manufactured/cut parts, not qualified stock components or print-service quotes. No model has been physically printed or test-fitted.
