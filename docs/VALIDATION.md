# Validation record — 2026-11-17

Executed in the managed Linux workspace. No board, battery, transducer, printer or instruments were attached. Results below are host/build/CAD evidence only. No purchasing/fabrication, flashing or physical safety validation occurred.

| Check | Actual result |
| --- | --- |
| `sh scripts/check.sh` | 32 standard-library unit tests passed; draft example, recovery/player demo and CAD coordinate assertions passed |
| `sh scripts/firmware-check.sh` (PlatformIO 6.1.18, see environment below) | Mini, Explore, Mini bench-audio and Explore bench-audio all compiled/linked successfully; native C++ policy/WAV and content-parser tests passed with `-Wall -Wextra -Werror` |
| `sh scripts/cad-check.sh` — KiCad 9.0.2 ERC | Zero errors/warnings; all severities, no exclusions |
| Same — KiCad DRC with `--schematic-parity` | Zero violations, zero unconnected pads, zero parity issues; all severities, no exclusions |
| Same — OpenSCAD 2021.01 | Eight STL renders: Mini/Explore × front/back/coupon/plunger; all `Simple: yes`, `Volumes: 2` (one bounded solid plus exterior), no warning/error |
| Live HTTPS smoke check to the owned public repository example | Connection refused by this environment network path; no live fetch/stream validation claimed |
| Studio UI inline JavaScript `node --check` | Syntax check passed; HTTP mutation auth/Host/Origin and approval workflow exercised by host tests |
| Python `compileall`, Draft 2020-12 schema/example validation, `git diff --check` | Passed |

Build reproduction used:

```sh
PLATFORMIO_CORE_DIR="$PWD/work/pio" PIO="$PWD/work/toolenv/bin/pio" sh scripts/firmware-check.sh
```

Framework 2.0.17 (PlatformIO package 3.20017.241212+sha.dcc1105b), Espressif32 platform 6.9.0, exact direct libraries in `firmware/platformio.ini`. The final local build reported at most 46,220 bytes static RAM and approximately 1.07 MB flash for Explore bench-audio. Linker size is not runtime free heap, decoder load, performance or battery consumption. Runtime codec allocations still need board measurements.

The committed `hardware/reports/controls-erc.rpt` and `controls-drc.rpt` are actual clean check snapshots, not hand-edited summaries. Intermediate meshes/logs, dependencies, tokens and binaries remain ignored under `work`/`.pio`. No built firmware binary is published. CI workflows repeat host checks, the four firmware configurations/native tests, and CAD checks using Debian trixie packages; remote CI results are separate from this local record.

Coverage includes invalid paths/symlinks, truncated/changed/oversized assets, graph traps, stale approval, interrupted staging, corrupt-active fallback, pairing expiry/reuse/authentication, dynamic episode bytes, hostile URL/redirect/response boundaries, editorial invalidation, canonical WAV export limits and debounce timer wraparound. Fixture network tests make no external requests. No live station availability or content suitability is claimed.

Pending physical evidence is listed in `hardware/ASSEMBLY.md`; dimensions/fit assumptions are in `enclosure/DIMENSIONS.md`. CAD correctness cannot establish electrical/acoustic/mechanical/battery safety or child-product compliance.

## Integrated modular sources, 2026-11-17

39 host tests pass, including collision detection, corrupt supplier-model hashes, exact identity requirements, missing quotes and purchase-pack rounding. Existing Mini/Explore/default-muted and both bench-audio firmware builds pass with native policy/content tests; these are the historical bench wiring, **not a TLV320 integrated driver build**. The integrated firmware profile remains unimplemented.

The new mute-latch schematic/PCB passes KiCad9 ERC and full DRC including schematic parity with0violations/0unconnected items/0parity issues using configured stock/local libraries. Reports are in `hardware/integration/checks`. The controls PCB remains checked by the same command. New prototype exports are checked for OpenSCAD simple single solid, two-manifold STL edges, nonnegative printZ and recorded bounds/hashes. Digital geometry and supplier files do not establish physicalfit, electrical/acoustic/thermal/drop safety or print strength. MCU assembledheight, switchactuator, slicer review and all physicaltests remain pending. Source-derived PNGs show reference geometry, with simplified envelopes explicitly labelled.

## Visual atlas 2026-11-18

The visual atlas uses the existing manufacturing sources and adds rendering/documentation tools. Its coverage/integrity check verifies72 PNG views,16 sections, complete orthographic coverage for both variants, source/image hashes and the PDF page count. A complete render receipt records every finished figure against frozen renderer inputs. Blender regression checks verify positive native-board transform determinants, front/back orientation, alignment of all eight actuator centres and a hollow case section (about1957.33mm² of actual cut faces rather than a disk filling the enclosure). Opaque material/Boolean comparisons also confirmed that the display-only mirrored lid/button meshes produce the same rendered result as corrected winding; they are not exported manufacturing geometry. All physical fit, electrical, acoustic, thermal and retention gates remain pending.
