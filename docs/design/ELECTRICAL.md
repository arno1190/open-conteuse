# Current electrical reference

This is an engineering prototype design. Run native ERC/DRC on each variant and inspect the actual reports in `hardware/<board>/checks`. Geometric/net checks do not establish voltage compliance, signal integrity, thermal performance or successful hardware operation.

## Shared power and audio

USB-C is a5 V sink with independent5.1k CC resistors, USBLC6-2SC6 data protection and 27 Ω data series resistors. No USB-PD controller or high-current Type-C negotiation is assumed. BQ24074 EN1 is tied to VBUS and EN2 to GND for USB500 mode, not a claimed1.5A input source. ISET3.57k gives about 249 mA nominal charge; ITERM3.01k gives about 25.3 mA termination in this mode. TMR is NC for default safety timers. A real Semitec 103AT-2 thermistor is bonded to the pouch and connected at J6; it is not replaced by a fixed “temperature OK” resistor. The input current budget includes the running load, so charge current may reduce under load. Measure thermal regulation, charge termination and source behaviour.

SYS supplies the separate MAX98357A speaker amplifier. A physical slide switch enables the logic regulator and Explore backlight boost. The regulated logic net is named **3V2**, with a TPS63020DSJR and 0.1%1M/187k feedback divider. Nominal output is 0.5×(1+1000/187)=**3.174 V**. PS/SYNC is tied HIGH for forced PWM: power-save mode can raise the output, which conflicts with the panel's3.3 V ceiling. Precision-divider and feedback extremes give approximately 3.137–3.211 V before line/load/ripple effects; a planning envelope including 1% combined line/load allowance and±50mV dynamic excursion is about 3.055–3.293 V. These are calculated limits, not measured regulation. Validate the actual panel's maximum and MCU's3.0 V minimum over startup, Wi-Fi load steps, USB changes and battery discharge. Forced PWM has a standby-efficiency cost. VINA has its dedicated100nF bypass and is **not tied directly to SYS**.

TLV75518 supplies the codec's1.8 V DVDD. Its3.2 V I/O/analogue/headphone supplies and the unused internal speaker supplies remain on legal rails. The TLV320DAC3100 uses the matching TI RHB0032E3.45 mm exposed-pad footprint. Its internal class-D outputs are unconnected and must remain disabled. Stereo HPL/HPR pass through 100µF AC-coupling capacitors to a CTIA jack: SJ-43514 pin2=tip/left, 3=ring1/right, 4=ring2/GND and 1=sleeve/MICDET, with MICBIAS through 2.2k. This follows the codec's headset-detection topology; actual TRS/TRRS insertion, debounce, pops, short-circuit response and output level must be measured.

A codec event on GPIO 1 drives MMBT3904 and asynchronously sets SN74LVC1G74. Its complementary output and speaker request are ANDed by SN74LVC1G08. Correct DCU latch mapping is CLK1,D2,/Q3,GND4,Q5,/CLR6,/PRE7,VCC8. Speaker request has a pulldown. A 10k series/20k local pulldown keeps the MAX98357 SD_MODE control near2 V rather than driving3.2 V into an amplifier on a depleted raw rail. Its internal pulldown also affects the exact value. Gain selection100k to SYS chooses the low3dB setting. The0.7 W speaker still requires a measured limiter; low gain is not a certified sound limit.

Firmware must keep request LOW while clearing the latch, configure/read the codec and verify no headphone before enabling. Codec reset/IRQ configuration and its detection clock must be checked, and I²C failures must force mute. This is independent of main-loop progress **after a configured codec event**; it is not an independent mechanical insertion switch. The current Mini and Explore diagnostic profiles deliberately keep the speaker request LOW and the headphone paths reset/muted; they do not claim completed compact audio playback or a proven mute response.

## Digital pin contract

| MCU GPIO | Function |
|---|---|
|1 /2 |I²C SDA/SCL; codec0x18, TCA9534 controls0x20 |
|4 |Codec reset |
|5 /6 |Mute-latch clear / latched-state readback |
|7 |Spare test pad; no device function assigned |
|8 /9, Explore |Backlight PWM / LCD reset |
|10 /11 /12 /13 |microSD CS / shared MOSI / SCK / MISO |
|14 /38, Explore |LCD CS / data-command |
|19 /20 |Native USB D− / D+ |
|21 |Codec IRQ, active event polarity must match configuration |
|40 /41 /42 |I²S BCLK/LRCLK/data |
|43 /44 |Service UART TX/RX |
|47 |Speaker request, active high, externally pulled down |
|48 |Single status LED; bare module has no onboard DevKit RGB LED |

GPIO 0 remains boot; 3/45/46 strapping and 35/36/37 OPI pins are not assigned. This table concerns module GPIOs, never DevKit header numbers. TCA9534 ports P0..P7 map UP,A,DOWN,LEFT,RIGHT,B,VOL_DOWN,VOL_UP; each has a10k pull-up and a normally-open switch to GND. The I²C expander intentionally frees MCU pins for a robust mute/control contract.

## Display circuit

Explore uses RONBO RB024D18N01B1. J8.1..18: GND,RESET,SCK,DC,CS,MOSI,MISO,GND,VDD,LEDA,K1,K2,K3,K4,NC,NC,NC,NC. The unused four pins are resistive-touch terminals. Confirm contact face and pin1 against the actual FPC. TPS61040 with 1M/332k feedback produces approximately 4.947 V. Four120 Ω branches and AO3400 PWM derate backlight current to approximately 14.6 mA each/58 mA total at 3.2 V LED forward voltage, rather than claiming the 80 mA nominal maximum brightness. The drawing gives separate cathodes, so no unbalanced parallel LED branch is assumed. Measure LED current, boost startup, ripple and PWM audibility. The final native layout has approximately 14.72 mm total front-layer LCD_SW copper and 17.72 mm feedback routing with two vias; U11, L2 and input C28 are spread roughly 10–11 mm. This is a known boost-layout qualification item: TI TPS61040 section7.5 calls for nearby input capacitor/inductor/diode and protected feedback routing. The main TPS63020 local-loop assertions do not qualify this separate boost circuit. Before fabrication release, review this cluster against TI's reference layout and tighten it if required; bench qualification must measure switch ringing, output startup/ripple, backlight PWM noise and coupling into headphones/codec. Clean DRC and the broad-rail corridor check do not close this item.

## Layout/manufacturing limits

The nominal board stack is four layers / 1.2 mm: front components and local routing, In1 GND reference, In2 logic-power pour plus routing, back system-power pour plus routing. Copper thickness, dielectric stack, USB impedance and supplier capabilities require confirmation before fabrication release. Native design constraints are0.15 mm signal clearance/track minimum and 0.3 mm via drill; signal and fine-pad fanouts can be0.15 mm; regulator local paths use0.25 mm necks and 0.6 mm trunks. Broad3V2(In2) and SYS(back) pours support distribution, rather than relying on long narrow traces. Zone connectivity is natively filled and DRC checked, but resistance/neck bottlenecks and dynamic droop need bench verification. Ground thermal vias/reference planes and hot-loop placement require the layout review; software DRC alone cannot prove them. Via-in-pad filling/tenting, paste apertures, thermal resistances and assembly house capability must be reconciled with an actual quote. No fabrication package is released simply because artwork can be exported.

The whole bare board needs staged adult bring-up. ESD on exposed interfaces, charger/regulator transients, analogue noise, speaker shutdown and RF coexistence remain test/review gates, not inherited properties of the older modules.

## Filled supply geometry and stack assumptions

Local source/load stitches feed the MCU, regulator input/output, charger and amplifier through filled copper. In2 carries logic power and the battery spine; the back carries SYS and USB input distribution, with a separate Explore battery-capacitor branch. Front ground fill and the In1 reference meet through local vias. These are mixed power/routing layers, not an assertion that every pour is a single continuous sheet.

Earlier sampled copper-corridor evidence does not replace a current DFM review. Native ERC/DRC checks connectivity and rules, not impedance, current density or temperature rise.

Planning assumes35 µm copper on **all four layers**, not an automatically accepted18 µm inner stack. At20°C, 35 µm copper is about 0.493mΩ per square: an isolated80 mm×0.8 mm path would be about 49mΩ before vias and local necks, or34mV at 0.7A. This example is not an extracted board result. The narrow3V2 voltage margin requires actual supplier stack confirmation and startup/load-step measurements. Reassess the rail and panel supply if measurements do not retain the MCU3.0 V minimum and panel3.3 V maximum.

The fabrication/assembly allowance requires a quote for the requested copper, via-in-pad filling/capping and paste process. Simple tenting is not an approved substitute for qualified via-in-pad processing. No stack, supplier capability or electrical safety is established by these files.

## Mini contact-ID interface

J7 BM07B-SRSS-TB retains its exact7way footprint. Harness populates **1=3V2,2=GND,6=GPIO8**; positions3/4/5/7 must remain empty. MCU GPIO9 and R26.2 are NC. Reader J1 solderwire pads:1=3V2,2=GND,3=IO8. R1=4.3k pull-up to3V2, R2=330ohm series to exposed DQ; primary TPD1E10B06DPYR DQ-to-ground and BAT54S secondary clamps. Reader GND springP1, DQ springP2. DS2401P+ token pin1GND,2DQ,3..6NC; parasitic supply fromDQ, no VCC wear pad. Family01 and8byte ROM CRC are checked. Factory ROM is not writable; assignments are parent-side. Single-drop ReadROM0x33 only. Validate input-high margin, parasitic charge, pulse timing and ESD/short recovery at the actual rail/tolerances.

Sources: [DS2401](https://www.analog.com/media/en/technical-documentation/data-sheets/ds2401.pdf), [Harwin drawing](https://content.harwin.com/asset/41705223-9cb7-4049-8762-809076ae4035/DRG-02618-Technical-Drawing-Datasheet-P70-10X-pdf.pdf), [TI TVS](https://www.ti.com/lit/ds/symlink/tpd1e10b06.pdf), [Nexperia clamps](https://assets.nexperia.com/documents/data-sheet/BAT54_SER.pdf).
