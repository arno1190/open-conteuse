# Bench wiring contract v0.1

Only **ESP32-S3-DevKitC-1 fitted with ESP32-S3-WROOM-1-N16R8**. Board selector `conteuse_s3_n16r8` describes 16 MB QSPI flash and 8 MB OPI PSRAM. Read the module marking; the generic PlatformIO DevKitC default describes an N8 and is not the chosen hardware. USB powers the dev board for the first bench stage. No battery connects to this prototype.

| Function | ESP GPIO | Interface |
| --- | --- | --- |
| SW1 / up | 4 | Controls J1.1 |
| SW2 / play, A | 5 | Controls J1.2 |
| SW3 / down | 6 | Controls J1.3 |
| SW4 / previous, left | 7 | Controls J1.4 |
| SW5 / next, right | 15 | Controls J1.5 |
| SW6 / back, B | 16 | Controls J1.6 |
| SW7 / volume down | 17 | Controls J1.7 |
| SW8 / volume up | 18 | Controls J1.8 |
| Controls common | GND | Controls J1.9 |
| PN532 SDA / SCL | 1 / 2 | 3.3 V I2C; board in I2C mode |
| PN532 IRQ / reset | 8 / 9 | Adafruit constructor IRQ then reset |
| SD CS / MOSI / SCK / MISO | 10 / 11 / 12 / 13 | 3.3 V SPI, initial SD clock 1 MHz |
| ILI9341 CS / DC / reset | 14 / 38 / 39 | Shared SCK=12, MOSI=11, MISO=13; touch unused |
| I2S BCLK / LRCLK / DOUT | 40 / 41 / 42 | DAC and separate amp may share digital bus |
| Headphone-present signal | 21 | Active low, 3.3 V input with pull-up; isolated detection interface still pending |
| Speaker amp enable | 47 | Active high; external 10 kΩ pulldown required |

Reserve GPIO19/20 for native USB; 35/36/37 for OPI PSRAM; 0/3/45/46 for boot/strapping; 43/44 for UART; 48 for onboard RGB LED. Do not silently substitute a WROOM variant or PSRAM mode. These assignments are a desk pin allocation, not a measured signal-integrity result.

The controls PCB contains **switches and a ground harness only**. It does not contain the MCU, SD, NFC, screen, charger, regulator, codec, headphone amp or speaker amp. All GPIOs must remain 3.3 V. J1 carries no positive supply. Pin 1 is the square pad; there is no reverse-insertion protection. Generic unkeyed headers are for adult bench use only. The final carrier must select a keyed locking harness.

Mini populates SW2, SW4, SW5, SW7 and SW8; SW1/SW3/SW6 are DNP. Explore populates all eight. Current firmware uses left/right to choose and A to confirm; up/down and volume events are diagnosed but do not yet implement a finished child-facing UI. Mini text prompts are serial diagnostics unless the pack contains recorded speech; no on-device unrestricted TTS/AI is present.

The line DAC is not a headphone amp. MAX98357A output is bridge tied: neither speaker terminal is ground, and neither goes to a headphone jack. The final analogue headphone path, insertion detection and independent speaker mute circuit must be designed and reviewed before an acoustic bench test. Software mute by itself cannot establish this requirement.
