# Compact R1 dimensions and mechanical assumptions

Coordinates are millimetres: X left-to-right, Y top-to-bottom in the front view, Z rear-to-front. These are canonical KiCad-style source coordinates. Physical mesh exports use the right-handed mapping **Xout=X, Yout=H−Y, Zout=Z**, so that a manufactured KiCad board and printed housing have the same handedness. The front print mesh additionally rotates the physical front face onto the build plate; do not mirror STL files in the slicer. All dimensions below are nominal case-body dimensions; the captive keys protrude another0.6 mm (assembled depth22.6/24.6 mm). The original modular model is not rescaled or reused as a fitted compact shell.

| Feature | Mini | Explore |
|---|---:|---:|
|Outer width ×height ×depth |65 ×95 ×22 |67 ×100 ×24 |
|Bounding volume |135.85cm³ |160.8cm³ |
|Reduction from original1176cm³ |88.45% |86.33% |
|Main PCB |60 ×83 ×1.2, 1 mm corner chamfers |same outline, different placement/population |
|PCB case origin |X2.5,Y9,Z10.5 |same |
|Nominal walls/front/back |1.8 |1.8 |
|Back rim / front seam |Z12.8 /12.95 |same |
|Mount holes |(6, 56),(59, 56),(6, 88),(59, 88),Ø2.2 |same |
|Back PCB-support face |Z10.5 |same |
|Front PCB-support face |Z11.7 |same |
|Protected cell body |34 ×62 ×5, at(15.5, 24, 3) |same |
|Cell service reserve |36 ×64 ×7 at(14.5, 23, 2.5) |same |
|Speaker body |15 ×11 ×3 at(34, 78.9, 16.4) |at(34, 78.9, 18.4) |
|NFC reader |25 ×16.4 ×4.4 at(30, 32, 15.5) |absent |
|Ferrite antenna |25 ×10, assembled0.6 thickness assumption at(20, 19, 19.6) |absent |
|LCD body |absent |60.26 ×42.72 ×2.55, at(3.37, 7, 19.45) |
|Lens |absent |55 ×40 ×0.5, at(6, 8.5, 22.5) |

The display drawing says2.55 mm, while the manufacturer's product summary says2.3 mm. The larger drawing value drives this design. The exact received FPC contact face, tail length, bend radius, tolerance and panel revision must be confirmed. The folded tail has a reserved corridor on the right; its proposed centreline is illustrated, not certified as a flex fatigue or assembly result. A 67 mm body leaves 1.57 mm between the nominal panel edge and the inside of the right wall; this is why the 65 mm comparison target was relaxed.

The battery envelope comes from the identified Adafruit258 product, not an arbitrary capacity-only box. The stock connector, lead exit and protection board must be checked against the received pack. The reserve adds XY room and Z allowance; it does not establish a permissible swelling limit or continuous discharge rating. Soft retention and an insulating strap are used, with no screw or hard post passing over the pouch. Confirm the supplied cell's discharge/charge limits and protection cutoffs before energizing.

The Wi-Fi antenna overhangs the main PCB's top edge. The native board has an all-layer rule area, and the case lip is relieved around the physical module. Battery metal, speaker magnet and metal fasteners remain outside the reserved top region. NFC uses a separate ferrite-backed antenna; its nominal separation from the MCU shield is about 4.8 mm. Actual NFC range and Wi-Fi coexistence still require a populated, closed-case test. The copper rule area is not a full three-dimensional RF clearance proof: Explore’s panel envelope begins at Y=7 mm and approaches the module antenna region; Mini’s separate NFC antenna begins at Y=19 mm. Confirm the received display’s metallic backing and the ferrite/lead arrangement, review them against Espressif’s antenna-placement guidance, and measure closed-case Wi-Fi/NFC performance before claiming RF qualification.

## Interface and tolerance assumptions

- Captive keys: 7.0 mm face in7.4 mm opening; 9 mm keeper; 3 mm actuator stem. Nominal 0.1 mm rest gap to the 1.9 mm switch actuator. Print variation and switch travel must be measured; adjust the stem, never preload every key by tightening the case.
- Inserts: RuthexRX-M2x3x3.2, 3 mm pilot is a **coupon starting point**. Verify the manufacturer's recommended process and actual PETG hole result. Four M2×14 screws have relief beyond the 3 mm insert; confirm engagement and that no screw bottoms in plastic before clamping.
- Main-board thickness is 1.2 mm. A 1.6 mm substitution changes Z stack and key travel and requires a CAD revision.
- USB and headphone noses are recessed. The headphone tunnel reserves 14 mm width and 8 mm height; the USB tunnel is 11 mm wide and 8 mm high to preserve the adjacent insert boss. Select a USB plug overmold no wider than 10.5 mm; test the actual intended plug overmolds. A drawn opening does not prove that every commercial cable fits.
- Battery and NTC wires return around the top-left PCB edge, outside the antenna rule area; do not force them through the 0.7 mm left wall/PCB gap. The illustrated paths and 100 mm service leads require a physical cable trial.
- NFC module attachment uses printed corner retainers with clearance. Verify its actual headers/antenna socket height; remove unwanted tall headers as a controlled assembly operation, not by forcing the shell closed.
- Lens is a drawing-defined cut part, not an identified stock lens. Speaker gasket is a drawing-defined consumable. Their material/adhesive and supplier qualification remain pending.

Nominal digital checks distinguish body-envelope overlap, case penetration and intentional PCB support-face contact. They do not prove tolerance stack, service access, heat, acoustic seal, impact strength, RF compliance or battery suitability.

The speaker keeper is a separate ribbed print with front post centres (36, 77.3) and(41.5, 91.5)mm in canonical XY. Two M1.6×4 pan-head screws (head envelope 3.2×1.3 mm) enter1.25 mm tapped PETG pilots. Mini keeper/J4 clearance is only0.2 mm nominal; print warping, screw-head tolerances, driver-back geometry and pullout strength must be checked. The keeper shoulder defines the nominal 0.8 mm compressed-gasket gap. Interference checking separates only the intended keeper/driver contact face by 1 µm; positive penetrations remain failures.

The lower keeper screw head has only **0.1 mm nominal clearance** to the Mini inner wall, and the blind pilot leaves 0.2 mm nominal screw-tip clearance. The keeper posts have0.1 mm nominal clearance to the speaker ends. Verify actual screw heads, driver dimensions and PETG shrinkage before assembly; these small margins are prototype assumptions.
