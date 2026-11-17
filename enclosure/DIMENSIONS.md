# Dimensional assumptions and fit gates

All dimensions are millimetres. These are desk assumptions made on 2026-11-17, **not measurements of physical modules**. Sources are editable OpenSCAD; exported meshes are check intermediates in `work/cad`, not a fabrication release.

| Item | Nominal assumption | Validation needed |
| --- | --- | --- |
| Common outside shell | 100 W × 174 H × 38 D, corner R8 | Hand size, weight, edge finish, retention and drop study |
| Shell wall / split | 2.4 wall; 19 front + 19 back | Material, print orientation, warping, strength |
| Controls PCB | 70 × 65 × 1.6; origin (15,98) from front top left in CAD xy | Actual board/footprint tolerances |
| PCB mounting | Four 2.7 holes at (4,4), (66,4), (4,61), (66,61), relative to PCB | M2.5 fit and fastener length |
| Board front surface | z=8.9; posts 6.5 above inner front face | Switch height, solder tails, wire access |
| Switch centre positions | `controls.json`, checked against `shell.scad` | Button hand feel and reach |
| Button opening / stem | 5.85 opening, 5.2 stem; nominal 0.325 radial gap | Printed fit, lateral play, sticking, wear |
| Plunger | 8 head × 1.2 thick, 4.4 stem, 7 retaining flange | Actual actuator height/free travel; flange retention |
| PCB/case screw pilot | 2.1, case clearance 2.8, head recess 5.2 × 1.3 | Screw selection/thread fit; pilots are not final threads |
| Explore active window | 58 × 44 at (21,17), landscape | LCD active area, bezel, carrier PCB and cable bend |
| Explore display module keepout | Approx. 86 × 50 × 6, landscape, pending exact drawing | Verify exact product 1770 revision; redesign mounting |
| Mini card guides | Inner width 55.2; front pocket 54 × 50; guides end near y=72 | Portrait ID-1 card ~53.98 × 85.60 × 0.76; upper part protrudes; retention/read tests |
| NFC module keepout | Approx. 43 × 40 × 6 | Exact PN532 revision, antenna, stand-offs and metal clearance |
| Speaker keepout | 40 diameter, assumed <=5.5 depth near centre (50,83) | Actual driver basket, excursion and grille/acoustic test |
| Battery placeholder | 38 × 60 × 8; not a selected cell | Protected pack drawing, swelling allowance, connector strain relief |
| Dev board placeholder | Approx. 26 × 63 × 12 | Actual USB plug, headers, board and harness |

The enclosure is a **controls-aligned fit study**. It includes PCB bosses, captive actuator sources, card guides, speaker openings and a screw-retained back. Display/NFC/speaker/MCU mounts, USB/headphone cutouts, sealing lip and final battery retention are deliberately not frozen from guessed module drawings. Battery rails are space reservations, not a qualified cell restraint. Check the back's viewing direction before assigning connector positions; front/back sources are oriented for editing, and assembly mirrors the back in Z.

`part="coupon"` exercises button holes and pilot fits. `part="plunger"` generates one actuator; Mini needs five and Explore eight. Export front/back separately. `part="assembly"` displays translucent placeholders for inspection and is not a printable union. Generated STLs passing manifold checks do not prove the two halves fit, seal or survive use.

The wider 100 mm shell reserves space for an approximately 86 mm display module. The active display window alone cannot determine the PCB size. `scripts/check_cad.py` checks duplicated controls and hole coordinates and basic nominal PCB containment; it is not a full collision/tolerance solver. Print coupons only after fabrication authorization, then record measured allowances before a final shell.
