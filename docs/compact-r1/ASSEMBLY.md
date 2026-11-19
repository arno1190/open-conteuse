# Assembly and staged bring-up — compact R1

This procedure is for an adult engineering prototype. The files are not a child-ready product release. No board or enclosure has been manufactured or physically tested. Ordering remains outside this task; establish the release gates in VALIDATION before ordering. Source-only checks cannot establish safe charging, sound pressure, RF performance or drop resistance.

## Files, materials and tools

For each variant, the manufacturing identities and quantities are in its CSV BOM and searchable BOM page. Mainboard, front and back are variant-specific. Use a1.2 mm four-layer board, not an unreviewed1.6 mm substitute. Prototype print set: one `*-print_front.stl`, one `*-back.stl`, and five Mini/eight Explore `*-button.stl` copies. `*-buttons.stl` is the alternative prearranged key plate, not an additional set. `*-front.stl` retains assembly coordinates for viewing. Print the fit coupon first.

Planning print settings: PETG, 0.4 mm nozzle, 0.2 mm layers, four perimeters, five top/bottom layers, 15–20% infill where there is an interior. The speaker keeper prints with its flat contact face on the bed and its reinforcing rib upward. Back prints rear-face down. The normalized front prints exterior-face down. Buttons print face down with the keeper's tapered shoulder upward. Small bridges, bed adhesion, dimensional compensation and any support required by the actual slicer must be inspected; no specific printer profile or G-code has been validated. Do not scale the STL to fit a purchased component. Update its source dimension instead.

Use a suitable reflow process/microscope for the SMD PCB; this is not a hand-wired breakout assembly. Stencil/thermal-via treatment must be reviewed with an assembler. For bring-up: current-limited bench supply, multimeter, oscilloscope, USB meter, thermometer/thermocouple, headphone dummy loads, acoustic measurement equipment and original/licensed content fixtures. No child should be the first acoustic tester.

## 1. Incoming inspection and fit coupon

1. Check every semiconductor suffix and marking against the BOM; record substitutions as design changes. Preserve N16R8 and OPI pin reservations. Check both large IC exposed-pad footprints against current manufacturer drawings.
2. Measure the actual board thickness, switch actuator/travel, jack/USB/SD nose locations, cell/protection/lead envelope, NFC sockets and FPC contact face. Update the mechanical JSON before declaring fit.
3. Print the coupon. Test key clearance, the 3 mm insert pilot and insert heating process on a scrap coupon. Confirm the plastic does not split or the insert rotate under modest screw load. Tune the source pilot/clearance, then re-export and recheck.
4. Heat-install four inserts in the empty front shell, entering from the inside. Keep the cell and electronics away from this operation. Check their axes against PCB holes and inspect the screw-tip relief. Do not use a screw to pull a crooked insert into alignment.

## 2. Unpowered PCB and supply bring-up

1. Inspect paste bridges, polarity, exposed-pad solder, USB tabs, connector pins and solder balls. Check resistance between VBUS/SYS/BAT/3V2/1V8 and GND with capacitors allowed to charge. Investigate a suspicious low resistance rather than repeatedly applying power.
2. Leave the pouch, speaker, headphones, NFC and LCD disconnected initially. Test the power path with current-limited laboratory sources and a controlled load/simulator; do not use a normal bench supply as a rechargeable battery sink.
3. With the logic switch off, verify speaker shutdown remains LOW. Apply a current-limited5 V USB source; verify input-current limiting and that SYS behaves as the BQ24074 reference specifies. A zero-volt battery absence is not a successful charger test.
4. Enable logic and verify3V2 nominal 3.174 V and codec1V8. Check startup/turn-off, input changes, load transients and ripple at the IC pins. The planned logic envelope must keep the panel below3.3 V and MCU above3.0 V; tighten the design if the observed excursion exceeds the assumptions.
5. Record regulator/charger temperatures and quiescent current. Test with USB changes and simulated battery conditions before fitting a real cell. Review thermal-via filling/tenting and any assembly voiding. Do not infer thermal success from ERC/DRC.

## 3. Firmware and digital interfaces, still muted

1. Use the dedicated `compact-mini-bringup` or `compact-explore-bringup` PlatformIO environment. The old DevKit environments use direct GPIO controls and a different NFC/display contract; do not flash them as if interchangeable.
2. Confirm the compact profile holds GPIO 47 LOW. It resets/mutes the codec and reports TCA9534 keys, SD status and PSRAM, with Wi-Fi off. These are diagnostic profiles; completed compact audio playback/detection configuration is still a separate integration gate.
3. Check each button's TCA bit. A bad I²C read must not turn into an apparent press. Verify USB flashing/reset/boot recovery and UART service pads. Use only3.2 V-compatible external logic; VBUS is never a GPIO supply.
4. Fit an original-content SD card. Test insertion, removal, file reads and the actual socket/card extraction clearance. The socket is exposed through the side opening; it is not a battery connector.
5. Mini: set the PN532 module to SPI. J7 order is 3V2,GND,SCK,MOSI,MISO,CS,RESET; terminate the other end by the manufacturer's labels and continuity-check it. Connect only the small included antenna. Keep its100 mm lead/service loop out of controls and the Wi-Fi antenna region. Test known NTAG cards before mounting the antenna.
6. Explore: verify FPC pin1 and contact side before closing the ZIF latch. Confirm the selected connector mates the exact tail thickness and conductor face; reverse-contact substitution is not automatic. First test at low backlight PWM, measure all four LED currents and check that no GPIO directly supplies the LEDs. The profile uses a low initial duty cycle, not a calibrated brightness or sound limit.

## 4. Audio/mute acceptance before connection to a listener

1. Keep the speaker request LOW. Bring up codec PLL/I²S/BCLK-derived clocks, headphone power/pop settings, detection oscillator, MICBIAS, TRS/TRRS detection and interrupt polarity with dummy loads. The compact diagnostic profile does not configure these finished paths.
2. Verify the latch's actual DCU pinout and logic: positive codec event sets MUTED asynchronously; LOW request blocks the amp regardless of latch state. Keep request LOW through latch clearing, read current headset status, verify latch state and only then permit an explicit adult bench enable.
3. Insert/remove TRS and CTIA TRRS plugs at startup, during playback and while deliberately stalling the main loop. Check the latched speaker block with a scope and repeat I²C/codec-reset fault cases. Codec-event mute is not an independent mechanical switch. Establish acceptable latency rather than claiming zero-delay insertion.
4. Verify MAX98357 SD_MODE voltage over raw-SYS range and partial-power conditions. Neither speaker terminal is GND; never connect its BTL outputs to the headphone jack. Check output shorts and recovery with appropriate loads.
5. Measure headphone/speaker level, clipping, noise, pop, temperature and volume limits with known fixtures. The tiny0.7 W speaker is not protected merely by selecting low amplifier gain. Publish no child-use audio or battery claim until these measurements pass.

## 5. Mechanical integration

1. Protect the PCB underside/pouch from sharp leads. Fit the cell into the reserved cradle with a soft insulating pad and retention band; do not compress it with the PCB or screws. Route battery/NTC leads around the top-left PCB edge, not the narrow straight side gap. Bond the external thermistor securely to the pouch with electrical insulation and strain relief.
2. Place the PCB on the four back supports. Confirm component/connector heights and the intended power-switch travel. Check board-to-pouch space with the strap fitted and with the lead/protection reserve included.
3. Mini: trial-fit the NFC board in the front corner retainers without forcing them. Attach the ferrite-backed antenna to the inner face at the marked tap area; its assembled envelope includes adhesive. Test read range in the closed assembly, with battery/USB/Wi-Fi present. Do not shorten the antenna lead or retune its matching by guesswork.
4. Explore: seat the panel on its ledges without glass preload. Fit the cut lens into its inside recess using an appropriate qualified thin adhesive. Fold the FPC within the reserved corridor using the actual manufacturer's allowed bend radius; do not crease it against the shell or trap it in a screw boss.
5. Fit the wired speaker and perimeter gasket facing the grille. Install the printed diagonal keeper with two ISO7045 M1.6×4 A 2 pan-head screws in the front’s1.25 mm tapped pilots; trial the PETG tapping/pullout process on scrap first. Seat against the post shoulders, preserving the nominal 0.8 mm gasket gap (20% compression of 1 mm foam). The driver is retained by the keeper, not by its cable. Confirm the Mini keeper clears J4 by 0.2 mm nominal, the lower screw head clears the wall by 0.1 mm, and the screw tip retains0.2 mm blind clearance; verify actual screw heads, driver-back shape and printed rib before closing. Keep the sound chamber/cable clear of key stems and the jack. Gasket compression, fastener pullout and acoustic behaviour require physical trials.
6. Place the captive keycaps from inside the front. Confirm every key has rest clearance and returns freely with the shell loosely assembled. Adjust stem dimensions if needed; tight screws must not become an actuator-height adjustment.
7. Close the upper seam/hooks, checking that no wire or FPC is pinched. Tighten four M2×14 screws gently and evenly. Confirm insert engagement, screw-tip clearance, unobstructed ports and free key travel again. Use a USB overmold≤10.5 mm for the 11 mm tunnel; qualify the actual intended cable.

## 6. Cell/charge and final prototype checks

After the supply, thermal and mute work is accepted, confirm the actual pack's polarity, protection, continuous/peak discharge and permitted charge conditions. The identified cell has protection but no built-in thermistor; that is why this design adds an external NTC. Test real charging/termination/temperature response with monitoring. Record runtime at defined volume/network use, enclosure temperatures, NFC/Wi-Fi performance, sleep current, retention, plug access, screw cycling and drop/impact behaviour.

Keep a per-unit build record: board revision, component substitutions, cell revision, print/slicer settings, measured voltages/currents/temperatures, acoustic settings, firmware SHA and results. A failed test revises the engineering design; it does not become a footnote to a production-ready badge.

BOM tape and retention-band prices allocate only the length consumed by one unit. A first purchase requires full packs; the first-batch setup reserve allows for consumable pack minima, assembly setup and shipping uncertainty. This is a budget assumption, not a supplier commitment.
