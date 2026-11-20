# Current custom-board firmware

Build only `mini` and `explore` with PlatformIO6.1.18 / espressif32 platform6.9.0 and pinned dependencies in platformio.ini. Both are **muted diagnostics**, not finished playback firmware.

```sh
sh scripts/firmware-check.sh
```

Galia Mini reads DS2401P+ on GPIO8 with external4.3k pull-up. ROM family01 + Dallas CRC8 and stable-read insertion/removal filter are host tested. The read slot uses nominal3µs low +5µs until sampling to leave GPIO-call overhead margin within the datasheet15µs read window; only scope measurements can confirm that timing. The bit timing, protection/pull-up budget, partial insertion and removal behaviour need a scope and real hardware. GPIO9 is unconnected and not driven. No PN532 dependency remains.

Galia Explore initializes the SPI panel with limited backlight. Both inspect I2C controls/codec, mount SD, disable Wi-Fi and hold speaker request LOW and mute-latch clear asserted. Codec headphone/speaker playback and event configuration remain a supplier firmware/bench milestone.

Portable content/policy tests remain for the existing host export contract. Default diagnostics do not load/play approved libraries. Do not enable audio until voltage, headphone event, acoustic and power checks pass. Original firmware GPL-3.0-or-later; see THIRD_PARTY.md.

The hardware-free control decoder in include/controls.h now defines25ms debounce, release-to-arm, context actions, nonrepeating navigation, deliberate volume repeat and bounded logical volume steps. Diagnostics log these actions without enabling audio. See docs/design/UX.md for the complete contract and pending physical/playback gates.


Parent card setup is now implemented in the compiled profiles: a parent-only boot chord enables a temporary WPA2 AP, with USB-reported ephemeral credentials, bounded authenticated HTTP, staged encoded-chunk transfers, incremental SHA256 verification and per-ID two-slot assignments. Normal mode keeps Wi-Fi off. Mini resolves and incrementally verifies the inserted card's local content; audio remains muted. See [card workflow/protocol](../docs/design/CARDS.md). Firmware-native fault/decode/deadline tests and host HTTP peer tests are software evidence; real SD/network/power interruption and onboarding qualification remain pending. The legacy active/previous pointer loader remains available but is not the card-selection path.
