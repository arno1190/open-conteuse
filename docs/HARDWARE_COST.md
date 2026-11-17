# Integrated hardware cost — 17 November 2026

The detailed successor BOM is [hardware/integration/BOM.csv](../hardware/integration/BOM.csv), with exact MPNs, supplier offers and search links on every row. Its [machine-readable status](../hardware/integration/status.json) supersedes the earlier modular allowances for this revision.

The current modular design replaces the earlier UDA1334A/headphone and power allowances with exact TLV320DAC3100, latch, charger and regulator selections. Explore uses Adafruit2090 and omits NFC. Historical figures remain in Git history.

| Build | Known USD purchase | Known GBP purchase | Known EUR purchase |
| --- | ---: | ---: | ---: |
| One Mini, first purchase |140.78|37.07|21.99|
| One Explore, first purchase |131.83|37.07|21.99|
| One Mini + one Explore, shared packs |242.76|37.07|21.99|

Do not add the single-device rows to price a combined build: shared wire, fastener and filament packs would be counted twice.

For **one Mini plus one Explore**,  the known minimum purchase-pack amounts are **US$242.76 + £37.07 + €21.99**, excluding tax and shipping. Keep currencies separate: no unverified exchange rate or fictitious landed total is implied. The USD amount includes two sets of electronics, the exact latch/controls components, one shared22AWG wire kit, two shared26AWG spools and four cage ties. GBP purchases are one100-pack of M2.5×6 screws (£25.81) and one250-pack of plain M2.5 nuts (£11.26), rather than charging fractional pack usage. EUR is one shared1kg PETG spool, subject to actual slicer consumption (not yet known). The PETG observed French gross price was€26.39/€21.99exVAT; destination may change tax.

**This is a known subtotal, not an exact complete quote.** Two custom controls PCBs, two mute-latch PCBs and two exact SanDisk8GB cards remain unquoted. Delivery country/postcode, destination tax, shipping, battery freight and any supplier minimum surcharges are unknown. For budgeting only, retain an additional **US$40–100 allowance** for those unquoted PCB/card items and prototype waste; this allowance is not supplier evidence. Assembly labour, printer time/electricity, instruments and tools are excluded. Shipping/tax can be substantial across these suppliers.

Adafruit364 and the exact EspressifN16R8 MCU were unavailable at the observed suppliers. Their published prices remain in the subtotal for comparability, but are not currently executable offers. Other identified offers are dated snapshots; availability, discount and price can change. Do not buy an apparently similar board without reviewing its dimensions, power behavior and pinout.

Final landed quote requires delivery details, available authorized sellers for the unavailable exact modules, current fabrication quotes and exact memory-card offer, followed by supplier basket totals. No purchase, basket checkout or fabrication submission was performed.

## Indicative complete prototype budget

For planning only, assume USD1=EUR0.91, GBP1=EUR1.18,20%VAT on parts, USD20–50 perdevice for unquoted PCBs/cards/waste, and EUR30–65 shipping perindividualbuild or EUR40–90 for the combinedbuild. These are **explicit budget assumptions, not current FX evidence or supplier quotes**. Rounded first-purchase budgets are:

| Build | Indicative cash budget, EUR |
| --- | ---: |
| Mini |285–355|
| Explore, no NFC |275–345|
| One Mini + one Explore, shared packs |430–550|

This includes minimum packs rather than fractional consumed material. It excludes labour, printer/tools/instruments, certification and additional redesign iterations. Different delivery taxes, exchange rates, battery freight or unavailable-item substitutions can exceed the range. The original EUR70–110/EUR85–135 targets are not credible for this branded-module prototype. A cheaper PN532 or consolidated PCB would require a separate electrical/mechanical redesign before savings can be counted.
