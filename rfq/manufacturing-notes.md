# Quote-only manufacturing references

The manufacturing-reference/ Gerber, separate plated/nonplated drill files/maps and filtered assembly-position CSVs are exported from the current native boards. **RFQ reference only: fabrication_release=false. No order or authorization to manufacture.** The native project/BOM and engineering dossier govern; supplier must return DFM changes and an accepted revision before producing anything.

Mainboards:4layers/1.2mm,35µm all copper layers, subject to agreed dielectric/USB impedance/thermal stack. Reader:2layers/1.6mm with notched outline; token:2layers/0.8mm with selective hardgold wear pads. Agree via-in-pad filled/capped process, drill tolerances, mask/paste process and surface finishes. No generic outer ENIG assumption establishes token wear durability. Token hardgold pads have no paste and no via in wipe lanes. Reader pogo pads have paste; manual solder-wire pads do not.

Position files use KiCad native absolute millimetre coordinates, with its exported Y convention; they are not the enclosure's30mm-shifted case datum. Review each MPN's pin1/orientation against the drawing before machine programming. Copper test pads, holes, reader wire termination and token wear-pad pseudo-components are excluded from pick/place. They remain identified in reference BOM/drawings as copper/manual features. Wiring, labels, cells, speakers, LCD and enclosures are separate boxbuild operations.

The current diagnostics remain muted. Resolve the current electrical/thermal/RF/boost/codec and mechanical gates in the RFQ, including the specified standard reader fastener. Clean design-rule checks do not authorize production or establish physical safety.

The current main-board outline includes an asymmetric4.0×1.4mm headphone-neck relief withR0.5inside corners at caseX26.7–30.7,Y90.6–92. This is part of the reviewed Gerber outline, not an optional hand-cut modification. Preserve the MICDET-pad clearance and qualify actual tapered plugs before accepting the finish.
