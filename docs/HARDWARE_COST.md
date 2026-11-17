# Hardware budget revision — 17 November 2026

The original EUR 70–110 Mini / EUR 85–135 Explore targets are too low for the currently selected branded breakout modules plus a complete battery/headphone/power path. This estimate prices **one complete unit**, including a printed shell, rather than only the USB-powered bench electronics. Unselected circuitry receives an explicit allowance; it is not a frozen or purchasable final BOM.

## Current supplier evidence

Public Adafruit product pages checked on 17 November 2026:

| Selected module | Listed USD, before tax/shipping | Source |
| --- | ---: | --- |
| PN532 v1.6 reader | $39.95 | https://www.adafruit.com/product/364 |
| 2.8-inch ILI9341 display | $29.95 | https://www.adafruit.com/product/1770 |
| UDA1334A line DAC | $6.95 | https://www.adafruit.com/product/3678 |
| MAX98357A speaker amp | $5.95 | https://www.adafruit.com/product/3006 |
| 3 V microSD breakout | $3.50 | https://www.adafruit.com/product/4682 |

ECB daily reference dated 2026-11-17: **EUR 1 = USD 1.0989** ([ECB XML](https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml)). For the indicative VAT-inclusive equivalent, use `USD / 1.0989 × 1.20`, assuming French 20% VAT. Product amounts below are rounded allowances for small-quantity European sourcing/markup; they are not distributor quotes or guaranteed landed prices. Shipping/minimum batches are budgeted separately. Tools, labour, instruments, certification and development time are excluded.

## Per-unit parts/material allowances, EUR including assumed VAT

| Item | Mini | Explore, without optional NFC |
| --- | ---: | ---: |
| Exact N16R8 dev board | 18–28 | 18–28 |
| microSD memory card | 8–14 | 8–14 |
| microSD breakout | 5–7 | 5–7 |
| Selected PN532 reader | 44–55 | — |
| Selected display | — | 33–45 |
| UDA1334A line DAC | 8–11 | 8–11 |
| MAX98357A speaker amp | 7–10 | 7–10 |
| Headphone amplifier/mute components — unselected | 8–18 | 8–18 |
| Speaker | 4–9 | 4–9 |
| Protected battery pack | 15–25 | 15–25 |
| USB-C, charger/power path, regulator/protection — unselected | 12–22 | 12–22 |
| Controls PCB, switches, harness/header | 12–25 | 13–28 |
| Printed shell/plungers, material and print allowance | 6–15 | 6–15 |
| Jack, wiring and fasteners | 6–12 | 6–12 |
| **Arithmetic total** | **153–251** | **143–244** |

Explore adds an allowance of EUR 1–3 for the three additional switches. Add EUR 44–55 for Explore's optional selected NFC reader: **EUR 187–299** total. This breakout display also includes a microSD socket; later validated integration could remove the separate SD breakout and save roughly EUR 5–7 per Explore. That saving is not assumed above.

The headphone line uses an allowance for a small final circuit, **not the TI evaluation board** mentioned as a bench candidate in the BOM. No EVM price is included. Buying an EVM, outsourcing printing, or fabricating a separate custom audio/power carrier during development can add materially to prototype spending. Exact audio/power parts must be selected before a final procurement total can be quoted.

## Practical first-prototype budget

| Build | Rounded complete-unit parts/materials | First-prototype cash allowance |
| --- | ---: | ---: |
| Mini | 155–250 | **185–315** |
| Explore without NFC | 145–245 | **175–310** |
| Explore with NFC | 190–300 | **220–365** |
| Mini + Explore without Explore NFC | 300–500 | **340–590 combined** |
| Mini + Explore both with NFC | 340–550 | **380–640 combined** |

The single-unit prototype column adds roughly EUR 30–65 for shipping, minimum PCB quantity, fit coupons and basic spares; the combined builds share an approximate EUR 40–90 allowance. These are planning ranges, not assurances of available inventory, exact import fees or iteration count. A redesign/reprint, evaluation board or additional carrier fabrication can exceed them. No purchases or fabrication orders were made.

The largest obvious cost reduction is replacing the USD 39.95 Adafruit PN532 with a cheaper PN532 module. That is **not** a drop-in cost revision: exact supply/logic levels, antenna, firmware interface, dimensions and mounting would need to be selected and rechecked. A future consolidated PCB might reduce recurring module cost but increases development/fabrication work. Do not silently substitute those savings into the current branded-module BOM.

## Integrated component revision — observed 2026-11-17

The detailed successor BOM is [hardware/integration/BOM.csv](../hardware/integration/BOM.csv), with exact MPNs, supplier offers and search links on every row. Its [machine-readable status](../hardware/integration/status.json) supersedes the earlier modular allowances for this revision.

For **one Mini plus one Explore**, the known minimum purchase-pack amounts are **US$242.76 + £37.07 + €21.99**, excluding tax and shipping. Keep currencies separate: no unverified exchange rate or fictitious landed total is implied. The USD amount includes two sets of electronics, the exact latch/controls components, one shared22AWG wire kit, two shared26AWG spools and four cage ties. GBP purchases are one100-pack of M2.5×6 screws (£25.81) and one250-pack of plain M2.5 nuts (£11.26), rather than charging fractional pack usage. EUR is one shared1kg PETG spool, subject to actual slicer consumption (not yet known). The PETG observed French gross price was€26.39/€21.99exVAT; destination may change tax.

**This is a known subtotal, not an exact complete quote.** Two custom controls PCBs, two mute-latch PCBs and two exact SanDisk8GB cards remain unquoted. Delivery country/postcode, destination tax, shipping, battery freight and any supplier minimum surcharges are unknown. For budgeting only, retain an additional **US$40–100 allowance** for those unquoted PCB/card items and prototype waste; this allowance is not supplier evidence. Assembly labour, printer time/electricity, instruments and tools are excluded. Shipping/tax can be substantial across these suppliers.

Adafruit364 and the exact EspressifN16R8 MCU were unavailable at the observed suppliers. Their published prices remain in the subtotal for comparability, but are not currently executable offers. Other identified offers are dated snapshots; availability, discount and price can change. Do not buy an apparently similar board without reviewing its dimensions, power behavior and pinout.

Final landed quote requires delivery details, available authorized sellers for the unavailable exact modules, current fabrication quotes and exact memory-card offer, followed by supplier basket totals. No purchase, basket checkout or fabrication submission was performed.
