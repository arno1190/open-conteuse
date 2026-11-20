# Source and model attribution

Original compact circuits, pin contracts, enclosure geometry, BOM arithmetic, scripts and documentation follow the repository licence; firmware source retains its GPL-3.0-or-later notices.

Embedded standard footprints come from the installed KiCad9 footprint libraries, licensed CC-BY-SA4.0 with the KiCad library exception. The local ESP32-S3-WROOM-1-R1 footprint is derived from KiCad's ESP32-S3-WROOM-1: antenna silkscreen is omitted, the rule area is placed on the board, and thermal drills/pads use0.3/0.5mm. Preserve the original KiCad library attribution/exception when reusing the standalone footprint library. Local TPS63020 and SJ43514 footprints were drawn from dimensional facts in the manufacturers' drawings and require supplier DFM/incoming checks.

Manufacturer datasheets, product pages and reference diagrams are linked in component data; they are not bundled or relicensed here. No Adafruit/ELECHOUSE firmware, Eagle design, commercial story library or proprietary console firmware is redistributed. The coloured component renderings are simplified nominal bodies, not copied proprietary supplier meshes.

Freerouting1.9.0 is an external GPL tool used to calculate routes; its JAR/runtime is not committed. Native KiCad DRC validates the resulting board copper. The versioned native CAD/artifacts do not require a cloud routing service to inspect them.
