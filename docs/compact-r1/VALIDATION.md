# Verification and release status

These are complete nominal digital prototypes for two custom compact devices. **Physical validation is pending; fabrication release is false.** No purchases, paid quotations or fabrication orders were made.

## Recorded digital results — 19 November 2026

| Check | Result |
|---|---|
| Native KiCad ERC, each variant | 0 violations |
| Native KiCad DRC / unrouted / schematic parity, each variant | 0 / 0 / 0 |
| Routed supply corridors, both boards | All required sampled 0.8 mm cores pass |
| Exported printable meshes | 14 manifold, positive-volume files; expected part counts |
| Nominal shell/shell and electronics/housing intersections | 4 empty intersection checks |
| Host unit tests | 39 pass |
| Existing modular atlas integrity | 72 views / 16 sections preserved |
| Firmware | 6 environments compile; compact images are muted diagnostics |

Native reports are under [hardware/compact-r1/checks](../../hardware/compact-r1/checks); machine-readable results and limitations are in [verification.json](../../hardware/compact-r1/verification.json) and [power-distribution.json](../../hardware/compact-r1/power-distribution.json). Image, mesh and document receipts bind outputs to the recorded source inputs. Physical tests have not been performed.

## Electrical checks

The committed verification record and native KiCad reports record the final ERC/DRC results. Schematic connectivity, footprint parity and manufacturing geometry are checked independently of the renderer. A clean report cannot establish regulator stability, codec configuration, audio quality, RF performance or battery safety.

The PCB uses four layers, 1.2 mm nominal thickness, with a continuous In1 ground reference and three signal layers. The switching-node, input/output capacitor and VINA routing is explicitly placed. Fine IC fanouts meet broad logic/system power pours on In2/back layers; the regulator has local 0.25 mm necks/0.6 mm trunks. Distribution bottlenecks and rail droop still require measurement. Explore’s TPS61040 cluster is an explicit layout/noise qualification item: its14.72 mm switch-node copper and 17.72 mm/two-via feedback route need reference-layout review before fabrication release; the main-regulator loop assertions do not validate this boost circuit. Impedance, temperature rise, acoustic coupling and EMC require measurement on assembled samples.

## Firmware checks

The four existing profiles and both new compact diagnostic profiles compile. Compact diagnostics keep the speaker enable low and the codec muted, and check the shared GPIO expander, card interface and variant peripheral. This is a bring-up image; the integrated codec playback driver and finished compact product firmware remain bench milestones. Host tests cover the existing library approval and recovery behaviour.

## Mechanical and visual checks

Every exported printable part is checked for manifold edges, positive volume and expected connected component count. The button plate intentionally contains five Mini or eight Explore separate keys. Actual mesh coordinates are checked against the native PCB key locations, including the front-shell printing orientation. Shell-to-shell and nominal electronic-body-to-housing intersections are checked with OpenSCAD. The NFC antenna adhesive face intentionally meets the front shell.

The 40 PNG views contain20 views per variant, including six sections each. They combine source-derived shell meshes, the actual PCB outline/pads/routes and documented nominal component bodies. Colours identify boards, shielding, battery and connectors; they are illustrative finishes. Most electronic bodies are dimensioned envelopes rather than supplier STEP models. Exploded offsets and wire curves explain assembly layers; they do not prove cable reach or strain relief.

## Required physical qualification

1. Print the coupon and one unpopulated case; measure shrinkage, insert bores, ports, keys and closure clearance using the actual printer/material.
2. Check actual cell/protection/lead envelope, connector polarity, protected-cell revision, pouch clearance, soft retention and service removal. No pouch compression or screws over the cell.
3. Verify received panel contact face, FPC length/bend/connector latch and optical alignment, or NFC module/antenna dimensions and read range through the assembled shell.
4. Inspect/reflow the fine-pitch and exposed-pad devices; verify supply current, charger programming and external NTC response before connecting the cell.
5. Measure startup, rail ripple/transients, shutdown/mute ordering and headphone/speaker operation at current-limited power before completing playback firmware.
6. Test buttons, microSD extraction, USB plugs within the documented overmold limit, headphone fit, drop/torque, temperatures, charging, RF coexistence, endurance and acoustic output.
7. Obtain supplier stock/lead-time confirmations, fabrication/assembly/printing quotes and a test/yield plan before a production release.

A mesh that slices, a successful firmware build and clean ERC/DRC reports do not certify a safe or production-ready device. The assembly guide states the inspection gates and stop conditions.
