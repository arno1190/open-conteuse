# Hardware design and bench gates

Status: requirements and candidates only; no validated schematic, PCB or enclosure.

Candidates: ESP32-S3 module with 16 MB flash/8 MB PSRAM; microSD; PN532 module initially; I2S codec/DAC with real headphone path and separate mono speaker amp; jack detection; protected replaceable 1S battery; USB-C charger with power-path management; 3.3 V regulation; optional SPI TFT. BQ24074 is a charger candidate, not a complete power supply. A MAX98357A speaker amplifier alone is not a headphone solution.

Manufacturer references:
- https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf
- https://www.ti.com/product/BQ24074
- https://www.ti.com/product/TPA6132A2

## Sequence

1. Freeze exact dev modules and measure dimensions; allocate GPIOs avoiding memory/USB/boot conflicts.
2. Play SD audio while serving UI; add Wi-Fi streams; test decoder load, underruns and reconnects.
3. Verify headphone detection/muting and gain with appropriate loads and acoustic measurement.
4. Add NFC with the proposed plastic/card geometry; test card removal and standby consumption.
5. Measure power at boot, Wi-Fi peaks, SD access, speaker output, charging/playback and low battery.
6. Draw carrier PCB with test points and connector/polarity documentation; review ERC/DRC.
7. Print fit coupons and an enclosure prototype before final shell.
8. Record battery temperature, runtime, charging behaviour, drop/retention and serviceability results.

Use screws and enclosed battery/SD access for child use. Battery protection, charge-current selection, USB-C CC/input-current handling, ESD and thermal design need explicit review. No certification or child-product compliance is claimed. Buying or fabricating hardware requires owner authorization.

Targets, not measured results: 2500–3500 mAh battery; 40–50 mm speech-oriented speaker; roughly 2.8-inch 320x240 screen on Explore. Preliminary prototype cost allowance EUR 70–110 Mini / EUR 85–135 Explore, not quotations.
