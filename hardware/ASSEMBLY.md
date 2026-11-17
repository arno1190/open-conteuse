# Assembly and staged bench procedure

Design review prototype, not a fabrication release. Nothing has been purchased, fabricated, soldered, printed or physically tested in this task. Keep children away from open prototypes. Record actual observations in the table below; do not turn build/check results into bench results.

1. Review `BOM.csv`, `PINOUT.md`, the schematic and the PCB together. Confirm the exact ESP module, footprint terminal spacing and switch internal continuity against the parts in hand. Regenerate/check sources with `scripts/cad-check.sh`. Board extent is 70 × 65 mm, 1.6 mm assumed, two copper layers, 0.25 mm tracks, 0.2 mm minimum clearance, 0.5 mm copper-to-edge minimum; no DRC exclusions. The routing is not a current-carrying power distribution design.
2. **Do not order** the PCB or print parts under this authorization. When physical prototypes are separately authorized/available, print the coupon first and measure fit. Check switch actuator height, plunger free travel and retention before trying either complete front. Fastener length must not reach the cell or components.
3. With all power disconnected, populate variant switches and J1. Check each switch closes its J1 signal only to J1.9; check adjacent signals remain isolated. Confirm connector pin order with a continuity meter, not harness colours. Map pins using the square pin-1 pad.
4. With no battery, audio amp or speaker connected, wire controls and SD to the USB-powered dev board. Common ground; no GPIO sees 5 V. Use a current-limited bench setup appropriate to the board. Flash the default variant only after checking N16R8 marking. Verify PSRAM report, SD detection, input debouncing and missing-SD behaviour. This task built firmware but flashed no board.
5. Add PN532 in I2C mode, with the exact reader revision's pull-ups/jumpers verified. Use known UID test cards and try unknown cards. Add the Explore TFT on shared SPI, verify chip-select isolation and screen orientation. Measure current and timing under concurrent traffic. RFID polling is intentionally suspended while audio/radio runs in this prototype.
6. For library tests, approve and export a pack from the parent studio to a new `library` directory on the SD root. See `firmware/README.md` for the device's tighter limits and canonical-manifest requirement. Change one asset byte and confirm rejection/fallback. Remove power at successive transfer stages and verify last-good behaviour on actual FAT media; POSIX host tests do not prove FAT power-loss recovery.
7. Audio stays off in default builds. Review DAC, amplifier, jack interface, gain and supply before enabling a `*-bench-audio` build. Fit the external 10 kΩ shutdown pulldown. Check an **independent hardware insertion mute** before attaching a speaker. Use electrical dummy loads and suitable instruments first. Verify no DC or bridged speaker output can reach headphones. Begin with low-level signals; fixed digital attenuation is not a measured volume limit. The headphone circuit is still a design blocker.
8. Confirm Wi-Fi is off for local playback; radio enables it only after explicit adult bench configuration. Test direct streams, dead servers, buffering, three connection attempts, local selection and 15-minute stop. Do not assume a station title proves live programme suitability. The default firmware never starts a public admin service.
9. Battery integration follows a separate schematic/power review: protected pack, keyed polarity, USB-C CC/input current, power path, regulator peaks, fuse/protection, charging temperature, cell restraint and service access. A BQ24074 part number alone does not close this review. No battery charging instructions are released here.

| Evidence needed | Status | Record later |
| --- | --- | --- |
| Actual module and switch dimensions, harness heights | Pending | Instrument, revision, dimensions, photos |
| Coupon and full shell fit, plunger travel, screw retention | Pending | Printer/material/orientation/tolerance |
| SD/NFC/TFT on N16R8 hardware | Pending | Firmware commit, wiring, logs |
| Headphone insertion mute and headphone/speaker gain | Pending | Loads, instruments, electrical/acoustic readings |
| Wi-Fi/audio/SD peaks, runtime and low battery | Pending | Supply, current traces, pack model |
| Charging/playback thermal behaviour | Pending | Ambient, cell temperature, duration |
| NFC read range with card guides, display and battery | Pending | Cards, orientation, geometry |
| FAT interruption/restart and card removal | Pending | Power-cut sequence, old/new revisions |
| Drop, small-parts retention and serviceability | Pending | Method, photographs, results |

No certification, child-product compliance, acoustic safety or battery safety is established by the sources or checks.
