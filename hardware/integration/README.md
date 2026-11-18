# Integrated modular prototype — revision 1

This is the detailed successor to the original bench envelope. The configuration is inspired by the owner's canteen project workflow: one catalogue, one placement file, sourcing queries on every BOM row, native CAD references and reproducible export checks. No private reference-project material is included.

**Status: nominal CAD prototype, not a physically validated or procurement-complete product.** Downloadable prototype STLs are in `../../enclosure/integrated/print/`. Do not substitute the historical `enclosure/shell.scad` for this enclosure. The integrated case is 112 × 210 × 50 mm. The Mini uses the actual long PN532 board; Explore omits NFC and uses the 2090 display.

## Sources and exact configuration

- [BOM.csv](BOM.csv): exact manufacturer/order identifiers, per-device quantities, observed supplier price/stock and DigiKey, Mouser and AliExpress search queries for **every** row. Search results are discovery links, not approved substitutes or authenticity guarantees.
- [catalog.json](catalog.json): dimensions, supplier CAD source URLs, Git object identities, source/derived hashes, mounting-hole coordinates, dimensional conflicts, quotes and assumptions.
- [layout.json](layout.json): all module poses, ports and removable-card/wire corridors in mm.
- [status.json](status.json): generated missing-quote/availability gates and minimum purchase-pack subtotals for one Mini plus one Explore.
- [mute-latch](mute-latch): native routed KiCad 9 schematic/PCB and local libraries for the independent insertion-mute latch. Existing controls PCB remains `../controls`.

Selected modules: Espressif ESP32-S3-DevKitC-1-N16R8 **PCB V1.1**; Adafruit 364 PN532 v1.6 (Mini), 2090 ILI9341 capacitive TFT (Explore; touch unused), 4682 microSD, 6309 TLV320DAC3100 headphone DAC, 3006 MAX98357A speaker amplifier, 6091 BQ25185 charger, 328 protected cell, 3351 enclosed speaker, 805 slide switch; Pololu 2873 regulated 3.3 V supply. Small-part MPNs are enumerated separately, rather than hiding them in an allowance.

No substitute board is dimensionally equivalent merely because it uses the same IC. PN532 manufacturer CAD is 120 × 50 mm whereas retail prose differs. The protected cell reservation combines the larger published dimension on each axis. The speaker uses the larger 19.7 mm CAD depth. ESP assembled/header height is a **14.5 mm reservation**, not a measured height. Switch STEP is an undetailed rectangular envelope: actuator location/slot and cradle require actual-part measurements. Neither uncertain item is represented as a detailed exact model.

## Electrical integration contract

Protected battery → BQ25185 BAT; charger LOAD → regulator VIN and MAX98357A VIN. Pololu fixed 3.3 V → MCU 3V3 and all logic modules; common GND. Charger retains factory 4.2 V / 1 A configuration (cell specified max charge 1.2 A). Slide switch pulls regulator EN to GND to sleep; never drive EN high. Raw LOAD remains powered when regulator sleeps; this is not a service isolation switch. Regulator typical near-battery output is 1.5 A, startup around 700 mA until regulation: delay Wi-Fi/heavy loads. Actual concurrent current, startup, thermal and brownout tests remain pending.

**Never connect MCU native USB/5V while it receives external 3V3.** Charging USB-C is charge-only. Service flashing requires disconnecting external power and confirming isolation; EN-off alone is insufficient. Do not attach charger/battery before polarity and short-circuit checks. Use the battery's manufacturer protection; the printed cage does not provide electrical protection.

Integrated wiring target (not yet implemented in firmware): buttons GPIO4/5/6/7/15/16/17/18; I²C SDA1/SCL2; PN532 IRQ8/RESET9; SD CS10/MOSI11/SCK12/MISO13; TFT CS14/DC48, RESET tied to ESP EN; I²S BCLK40/LRCLK41/DATA42; amplifier request47; latch Q21 and active-low CLR39. Reserve GPIO38 for DevKit V1.1 RGB, USB19/20, OPI35/36/37, boot straps0/3/45/46 and UART43/44. The old bench profile uses different GPIOs and lacks the TLV320 codec driver: **do not flash it onto this wiring**. Integrated firmware/codec bring-up is an explicit release gate.

Mute latch: TLV320 IO1 IRQ pulse drives 2N3904 through10k; base100k to GND; collector pulls HC74 PRE_N low (10k pullup). HC74 Q→GPIO21; /Q AND GPIO47 via HC08→amp SD. D/CLK grounded, CLR_N GPIO39 with10k pullup; all unused gate inputs tied, unused outputs NC. GPIO47 and SD each have10k pulldown; add the mandatory extra **local10k at amp SD/GND** so an unplugged harness leaves it muted. Both logic ICs use regulated3V3 and100nF decoupling. See schematic for header pin order; never infer order from this prose.

Boot holds GPIO47 LOW. Configure codec headset detection/internal oscillator and repeating IRQ, clear checked codec flags, clear latch with amplifier held LOW, release CLR, then perform checked no-headset/status and Q-low reads before enabling. I²C failure means muted. PRE and CLR simultaneous LOW can make both Q and /Q HIGH: never enable while clearing. This circuit latches insertion IRQ even if the loop stalls, but is not protection against codec reset, lost AVDD or broken IRQ. No physical headphone-mute safety result is claimed.

## Adult assembly and validation

1. Confirm every received PCB revision/MPN, battery polarity, exact connector and fastener geometry. Measure MCU assembled height, switch actuator, solder/header protrusions and actual plug barrels. Update catalogue/poses and rerun exports before a full case print.
2. Print the coupon first. Confirm M2.5 screw clearance, plain DIN934 nut capture and connector opening clearances. Nyloc nuts are taller and are not substitutes.
3. PETG baseline: 0.4 mm nozzle, 0.2 mm layers, ≥3 perimeters, 20–30% infill. These are starting settings, not validated strength. Slicer/orientation/support review is required; no printer-specific G-code is supplied. Front exterior faces the bed; all STL exports have nonnegative Z. Wide flat parts may need a brim; tall wall ledges may need support.
4. Install nuts into front pockets. Insert button stems **from inside**: the large internal head retains each cap. Fit controls PCB over them, then test free travel before wiring. Fit variant PCB and sealed speaker using the rigid4 mm PETG spacer; it is not an acoustic gasket.
5. Assemble removable carrier, modules, battery cage and cover. Use two MCU bars, one regulator bar and one switch bar. Route trimmed soldered harnesses with strain relief; avoid exposed plug-in jumpers. Leave SD extraction corridor clear. Do not overtighten against PCBs or pouch cell. Tie tension must close on the rigid cage, not compress the cell.
6. Verify service access and that lid/retainers cannot touch components or wires. Use M2.5×6 socket screws and plain2 mm-high nuts; selected mounting count43 pairs/device includes4 case,4 carrier,12 front,15 rear module,4 MCU,2 regulator,2 switch pairs. Verify screw engagement before tightening: supplier PCB stack variations require rechecking length.
7. Bench test isolated USB logic first with current limiting; then power rail startup/load, SD/NFC/TFT, codec/I²S and insertion mute. Finally battery/charge thermal, sound level, runtime, acoustic seal, NFC range, drop/retention and repeated assembly tests. Record results; all remain pending.

The render/export/mesh checks prove only properties of digital geometry. They do not establish electrical safety, child suitability, battery containment, mechanical strength or that every actual part fits. No purchases or fabrication orders were made.

## Reproduce

```sh
python3 scripts/integrated_hardware.py
python3 scripts/export_integrated.py
sh scripts/check.sh
sh scripts/cad-check.sh
sh scripts/firmware-check.sh
```

KiCad9 and OpenSCAD2021.01 are the checked CAD tool versions. Generator `scripts/generate_mute_latch.py` requires system Python with pcbnew. Preview rendering additionally uses the pinned numpy/matplotlib packages in `scripts/requirements-preview.txt`. The catalogue and geometric host checks need only Python standard library.

### Screw and solder clearance assumptions

M2.5×6 is measured under its head. For1.57/1.6mm modulePCBs, the tip lies4.43/4.4mm below the PCB support plane; global blind bores preserve a nominal0.6mm floor skin instead of being refilled by the case/carrier union. Speaker body is raised to6.4mm with a4mm spacer. Native CAD flange bearing surfaces are localZ1.0–2.7mm (1.7mm thick), so posts end at globalZ7.4 and screw tips atZ3.1. Verify the actual flange before assembly. Its post bores remain blind and nut cavities are open from the PCB side. Screw heads and tool approach still require received-part verification. Trim through-hole solder leads to≤2mm under every3mm PCB standoff; do not leave long header tails to touch the carrier. Bare standoffs do not provide insulation for unknown protruding components.

CAD poses use bare module assemblies without optional tall pin headers or the MAX98357A screw-terminal block. Solder the strain-relieved speaker lead directly to the amplifier output pads; do not add an unmodelled terminal block. Battery's included matching JST-PH lead connects to charger BAT; retain its protection and verify polarity. Any added plug/socket, terminal block or replacement speaker lead requires an exact BOM row, envelope and revised fit check. Latch's specified Samtec headers are included in its10mm upper reservation and still require received-part/lead-trim checks.


## Full visual atlas

The [combined visual design document](../../docs/visual-atlas) includes exterior/orthographic, exploded, sectional, module and service views for Mini and Explore, with a downloadable PDF. Its orange faces show sections of the supplied CAD solids; they do not reveal hidden speaker/cell construction. Shared-module close-ups are grouped with Mini; Explore adds its display and eight-switch controls view. Visual proxies and generic component bodies are labelled and do not replace received-part measurements.
