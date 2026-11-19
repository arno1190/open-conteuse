# Compact R1 cost assumptions

The identified R1 parts supersede the earlier generic €34–63 Mini / €36–66 Explore targets. The selected documented NFC module alone is about €34–40 in this planning model. These are **engineering allowances, not binding supplier, PCB assembly or print-service quotes**. The table is per assembled unit before yield loss, tax, delivery or manual assembly labour.

| Quantity | Mini | Explore |
|---|---:|---:|
|1|€100.81–178.50|€71.91–156.06|
|5|€87.81–153.50|€58.91–131.06|
|25|€80.81–138.50|€51.91–116.06|

The ranges include the protected cell, microSD, speaker, PCB components, front-end module/panel, PCB assembly allowance, printed case/buttons and fasteners/harness materials. A single prototype also carries a project setup/rework/spares reserve of €100–250. One assembled Mini plus that reserve is about €200.81–428.50 before delivery/tax; Explore is €171.91–406.06. This is why a custom one-off is not automatically cheaper than an already-manufactured console.

| First batch of five | Mini | Explore |
|---|---:|---:|
|Parts/PCBA/print plus €100–250 setup reserve|€539.05–1017.50|€394.55–905.30|
|Illustrative France total, with €40–90 shipping and 20% VAT|€694.86–1329.00|€521.46–1194.36|

These are scenario totals, not landed quotes. Delivery, battery shipping eligibility, import fees/duty, seller tax handling, actual country and supplier consolidation remain unresolved. A 20% VAT illustration is not a tax invoice. Engineering labour, manual harness/enclosure assembly and debug labour, tools, certification and extra PCB spins are excluded. Failed boards and rework can increase the cost per usable unit. No purchases or fabrication orders were placed.

## Evidence versus allowance

Observed 18 November 2026: ELECHOUSE lists NFC_EX_MINI at US$35.50 for 1–9 and US$29.90 for 10–99; Adafruit258 lists US$9.95; RONBO lists the chosen panel at US$2.80, but a current sample/revision/contact specification and delivery quote is still required. The NFC low estimate uses a **planning** exchange rate of €0.95/US$, not a live currency quote. Component allowances conservatively retain the same material range across quantities; only the PCB/assembly allowance changes. Applying the advertised NFC quantity discount would save approximately €5.32 per Mini at 25 units before supplier/FX/tax effects.

Sources: [NFC module](https://www.elechouse.com/product/pn532-mini/), [protected cell](https://www.adafruit.com/product/258), [panel](https://www.ronboe.com/shop/rb024d18n01b1/). Every stock component has an MPN/query in the [searchable BOM](BOM.html); cut lens/gasket and standardized consumables are explicitly drawing-defined or unqualified supplier items, not invented manufacturer parts.

## Cost-reduction decision

This version removes DevKit headers, separate controls/latch boards, the large NFC breakout and extensive module harnesses. It keeps a traceable NFC module for the first compact build, instead of assigning an unsupported bare-reader price to an unfinished RF design. Integrating the NFC IC/antenna matching on a later board could remove much of that premium, but needs a new schematic, antenna/driver/layout work and validation; no cost saving from that unbuilt board is booked here.

Mini Plus/Telmi remains the cheaper immediate software-prototyping route. The custom Mini is justified by its screenless NFC interaction, size and control of the hardware, not by claiming it beats a mass-produced console at one-off quantity.

The printable shell material estimate comes from watertight CAD volume and is a budgeting upper bound for dense material plus waste, not a slicer time/cost quote. Prototype PETG material is budgeted at €25/kg; the table includes a wider €2.50–5 allowance for print wear/setup/material. A paid print service can cost more. See the print manifest for model-derived volume/mass assumptions.

The layout uses small via-in-pad source/decoupling/thermal connections. Filled/capped or otherwise qualified assembly processing and its quote remain pending. PCB/assembly allowances may be exceeded by the chosen supplier’s technology minima; do not treat the budget endpoints as a guaranteed maximum.

The PCB planning request is four layers, 1.2 mm nominal thickness and 35 µm copper on every copper layer. Do not substitute a common18 µm inner stack without revisiting the 3V2 drop budget. Supplier process minima and via filling/capping may exceed the listed allowances.
