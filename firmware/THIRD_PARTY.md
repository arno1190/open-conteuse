# Dependency and distribution register

Versions are pinned in `platformio.ini`; PlatformIO is pinned in `requirements-build.txt`. Dependency code is fetched into ignored `.pio`/`work` directories and retains upstream notices. No built firmware binaries are committed or attached to the PR.

| Dependency | Selected version | Licence/source |
| --- | --- | --- |
| PlatformIO Espressif32 platform | 6.9.0 | Apache-2.0 platform scripts; https://github.com/platformio/platform-espressif32 |
| Arduino ESP32 framework | 2.0.17, packaged 3.20017.241212+sha.dcc1105b | LGPL-2.1 and component-specific notices; https://github.com/espressif/arduino-esp32 |
| ESP8266Audio | 1.9.7 | GPL-3.0-or-later wrapper/MP3 integration; https://github.com/earlephilhower/ESP8266Audio/tree/1.9.7 |
| libmad in ESP8266Audio | dependency-bundled | GPL; retain its COPYING/author notices |
| Helix AAC in ESP8266Audio | dependency-bundled | RealNetworks source notices in each source file/readme; **do not assume GPL-only licensing** |
| ArduinoJson | 6.21.5 | MIT; https://github.com/bblanchon/ArduinoJson |
| Adafruit PN532 | 1.3.4 | BSD; https://github.com/adafruit/Adafruit-PN532 |
| Adafruit ILI9341 | 1.6.1 | BSD; https://github.com/adafruit/Adafruit_ILI9341 |
| Adafruit GFX | 1.11.11 | BSD and bundled font/component notices; https://github.com/adafruit/Adafruit-GFX-Library |
| Adafruit BusIO | 1.16.2 | MIT; https://github.com/adafruit/Adafruit_BusIO |

The MP3/radio choice makes the original firmware a GPL-3.0-or-later work; the root MIT licence is not a licence for a linked firmware image. `firmware/LICENSE` contains GPLv3. Firmware headers/source explicitly state GPL-3.0-or-later. Original Python and CAD are separate MIT works, not copied upstream firmware.

**Source-only prototype release:** before distributing any binary, audit the exact linked components and AAC/Helix licence compatibility, retain all notices, and supply complete corresponding source/build information for the distributed image. If AAC terms are unsuitable, remove that decoder and select a compatible alternative; do not relabel upstream source. Source references and local compilation here do not settle every upstream codec's redistribution terms. No proprietary firmware, keys or commercial audio are included.
