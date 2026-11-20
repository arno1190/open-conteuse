# Current STL file map

Print only the named plastic parts below. Nominal geometry; slicer/material/shrink/support settings and finished fits require coupons and measurement.

| File in mini/ or explore/ | Use / quantity per player |
|---|---|
| print_front.stl | One front, already face-down oriented |
| back.stl | One rear shell |
| buttons.stl | One layout containing all caps:5Mini /8Explore |
| cap_0.stl onward | Individual cap types in native switch order; use these for different colours |
| button.stl | First navigation cap only, assembly/reference; not a universal replacement |
| bridge.stl | One speaker keeper, print-oriented |
| coupon.stl | Actuator/aperture/pilot setup test; not fitted in product |
| port_coupon.stl | Rounded USB and headphone approach-opening test; not fitted in product |
| front.stl | Canonical assembly/reference orientation; use print_front for printing |

| File in story-card/ | Use / quantity per cartridge |
|---|---|
| print_front.stl | One front, print-oriented |
| back.stl | One rear |
| front.stl | Assembly/reference orientation |
| pcb.stl | **PCB envelope reference only, not a plastic part**; order electronics only after DFM approval |

Do not count the two front orientations as two physical parts. Native KiCad files define actual PCBs. Cartridge artwork labels are33.6×38.6mm, intended for a34×39mm recess; total paper/adhesive≤0.15mm is an unvalidated assumption. Ordinary nonmetallic artwork only; confirm fit and RF behaviour on a prototype.

PrimaryA is10.5mm, Mini previous/next8.5mm, volumes6.5mm; Explore directions7mm and back7.5mm. Symbols are debossed and the top rim is chamfered. Full batch and individual cap files are alternatives, not cumulative print quantities. See the UX contract for switch order, colours, tactile meaning and physical travel qualification.
