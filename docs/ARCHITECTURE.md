# Current architecture

The common ESP32-S3-WROOM-1-N16R8 custom main board contains USB-C, BQ24074 charger/power path, TPS63020 nominal3.174V logic rail, TLV75518 codec supply, TLV320DAC3100 headphones, separate MAX98357A speaker amp, hardware event mute latch, microSD and TCA9534 eight-button controls.

Galia Mini exposes GPIO8 through a 330ohm protected reader with 4.3k pull-up, primary TVS and secondary Schottky clamps. A passive DS2401P+ in the cartridge answers with factory ROM serial/family/CRC. The firmware accepts three matching CRC-valid reads, removes after two misses and clears a changed selection before new debounce. One card only; no audio storage/authentication on the token. Galia Explore uses GPIO8/9 for LCD backlight/reset instead.

The card is keyed mechanically and has longer ground wear pad. Its leading ramp avoids sweeping full rear plastic thickness over spring contacts. Received-part tolerances and repeated insertion require physical qualification.

Host modules remain split into immutable content validation, playback state, staging/library activation, import/feed policy and local parent studio. Firmware diagnostics prove compilation and interfaces only, keep speaker request LOW, and do not implement finished integrated-codec playback. No public parent studio is deployed.

The proposed parent-personalization/MCP boundary is specified in PERSONALIZATION.md. It is not a live provider integration. The current UX contract separates button/input policy already implemented from device playback/transfer and physical qualification still pending.
