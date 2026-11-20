# Product UX contract · current design and qualification targets

20 November 2026. The sources now implement distinct cap sizes, tactile symbols and testable button-event policy. The full player/audio experience remains a target until codec, device playback and physical usability validation are complete. This document is the contract for implementation and RFQ review, not a claim of a finished commercial product.

Case-body dimensions are Mini 65×95×24mm and Explore 67×95×24mm; caps add0.6mm depth. The Mini’s inserted cartridge adds20mm height. These are nominal CAD dimensions, not measured received assemblies.

## Child’s first minute

An adult prepares approved audio. The child chooses an illustrated cartridge, slides it into the only keyed orientation and hears that selection. Inserting an assigned cartridge should start/resume its approved local selection; removing it should fade/pause and retain position. Timing/retention are acceptance targets, not measured capabilities. No microphone, child account, subscription login or network conversation is required on the Mini.

The recognition badge is deliberately in the exposed handle: character icon and MILO/NORI/PIPO names fit within cartridgeY5.4–18.2mm, inside the20mm that remains visible after insertion. The remainder of the label adds detail when the cartridge is held. Paper play cards are separate from these electronic selectors.

## Mini: five controls, three clear jobs

| Control | Physical identification | Intended action |
|---|---|---|
| Play/pause | Largest10.5mm cap, warm yellow, debossed play triangle and pause bars | Pause immediately; press again to resume. Confirm a choice only when its prompt has finished; while a prompt is playing or paused, this remains pause/resume. |
| Previous/next | Two8.5mm teal caps on either side of play, tactile bar-and-triangle symbols | Move between items/chapters within this cartridge’s assigned selection. |
| Volume−/+ | Two smaller6.5mm sage caps below, tactile minus/plus | One bounded level per press; deliberate holding repeats slowly. |

Colour is redundant: size, position and tactile symbols carry the meaning. No essential action depends on a long press or button combination. Play during silent loading cancels/pauses the pending start; an Explore back press also cancels loading and returns to the library. A delayed file load must never start unexpectedly after the child has paused it. Background transfer must preserve the active playing context and its pause action. Navigation never repeats on a hold. There is no hidden child gesture for raising the parent’s volume ceiling or activating unreviewed content.

Previous always selects the previous item; at the first/single item it restarts that item. There is no hidden elapsed-time rule. Next at the final item does not wrap into unrelated content: keep the selection and give a quiet end cue if an approved cue exists. Play at the end restarts the selected item. With no assigned selection, play requests a help cue/status and never falls through to other audio. Track boundaries and actual playback/bookmark behaviour still need integration tests on hardware.

During a spoken branch, left/right change the spoken option and play confirms it. The narration must explain this when offering choices. When a choice prompt/option is speaking, play pauses it; another fresh press resumes it. Confirm is available when the spoken option is waiting silently. Choice navigation remains choice navigation while its announcement is playing or paused; the implementation must retain that context. No voice recognition is implied. The three starter stories currently invite imagination and optional activity; they do not claim interactive voice handling.

## Explore: the same primary action, plus visible navigation

Explore retains8physical switches: four directional caps in a cross,10.5mm primary play/confirm,7.5mm back with a tactile return symbol, and6.5mm volume−/+. It has four separate directional caps, not an unimplemented single-piece rocker.

In the library, up/down move through items, left/right move between pages, play confirms, and back returns one level. On the playback page, play pauses/resumes, left/right move tracks, back returns to the approved library; up/down do not silently become volume controls. On a choice page, directions move through choices and play confirms. Screen labels must match the current context and selected item. The displayed library contains approved content only.

## Input policy already implemented and host tested

`firmware/include/controls.h` defines the TCA9534 bit contract, context routing and a hardware-free decoder.25ms stable debounce; a boot-held key must be released before arming; navigation/play never auto-repeat; volume repeats only after600ms, at most once every200ms. Unsigned timer arithmetic handles clock wrap. A play press while playing wins over accidental simultaneous keys and means **pause**, never an ambiguous toggle. A combination cannot resume. Other multi-key combinations are ignored and remain inhibited until all keys are released, preventing release of part of a chord from resuming or starting repeat.

Logical volume steps respect the supplied parent ceiling and an absolute20-step software bound. Missing/zero ceiling stays muted. Steps are not decibels: headphone/speaker acoustic calibration and hardware mute qualification remain mandatory. The current diagnostic firmware logs actions only and keeps audio locked LOW. Host policy tests do not establish physical switch feel or sound behaviour.

## Mechanical changes in the current CAD

Caps have0.25mm softened face edges and debossed0.5mm symbols with minimum0.8mm strokes, avoiding first-layer embossed islands when printed face-down. A flat retaining collar sits0.1mm below the nominal front inner roof, reducing upward float; front apertures give0.2mm nominal clearance per side. Caps retain the original switch centres and nominal13.7mm stem tip,0.1mm above the nominal13.6mm actuator top. The switch footprints and pin mapping do not move. The separate headphone-neck relief is included in the current PCB outline.

`cap_0.stl` onward follow the listed switch order; `buttons.stl` contains the whole set. Print primary/navigation/volume/back groups in different colours if desired, while preserving symbols. `button.stl` is only the first navigation-cap reference, not a universal replacement. The revised coupon checks10.9/8.9/6.9mm apertures and stem/pilot dimensions. Actual print shrink and switch dimensions can alter clearance. Rendered dark glyph floors represent proposed nonmetallic contrast ink filling; the STL supplies the tactile recess, not ink. Supplier must qualify ink adhesion/wear and keep paint off fit surfaces.

CAD gates include cap-to-cap separation and cap-to-shell motion at nominalZ offsets−0.35,0,+0.09mm. These are geometric samples, not a validated switch stroke or an overtravel-stop specification. Factory must measure mounted actuator height, force/travel/overtravel limits, cap retention, wobble, simultaneous presses and repeated use; adjust stem/stops before physical release. An explicit robust mechanical travel limit remains a physical DFM/qualification item. Do not infer switch protection from the sampled collision test.

## Enclosure finish and everyday access

The current case adds0.4mm exterior face-edge bevels. USB-C now has an11.4×6.4mm rounded plug tunnel (cornerR1.7) centred on the native receptacle, instead of a square oversize cut. The3.5mm jack has an8.8mm round approach bore. Both main PCBs also include a4.0×1.4mm asymmetric headphone-neck relief atX26.7–30.7,Y90.6–92 withR0.5inside corners, preserving at least the native copper-edge rule around the adjacent MICDET pad. The reference headphone envelope is a5mm neck atY91.05 tapering to8mm over4mm; the USB reference overmould is10.5×5.8mm. Separate CAD tests check each reference envelope against shell and PCB. These are compatibility targets, not identification of a bundled cable or support for every plug. The port coupon checks those opening profiles; actual insertion depth, cable/overmould and headphone-barrel compatibility remain physical gates, not universal plug-fit claims. The recessed physical power slider must have a visible power mark and verified I/O direction in the supplier finish artwork; do not assign ON/OFF direction without checking the actual switch contact drawing and sample.

Only one function changes when a child chooses another story: the selected approved content. Power remains physical; pause is always prominent; volume remains the same two controls. Missing/unknown cards must never fall through to other audio. Give a quiet, parent-approved help cue and a status indication when those assets exist; current diagnostics only log the condition.

## Parent experience and the differentiator

The proposition is **personal audio a parent can prepare with tools and subscriptions they already choose**: a lesson about a current interest, a story with familiar themes, or reviewed episodes. It is not a promise that any subscription includes API access, downloadable speech or catalogue redistribution rights.

The intended flow is a parent brief → draft/script review → narration → exact final-audio review → approved local library → cartridge assignment. The existing local tools cover import, approval and export foundations; assisted creation, provider connections and on-device playback are separate implementation gates. See [personalization assessment](../PERSONALIZATION.md). No MCP or TTS provider is currently connected or provisioned.

## Acceptance before describing it as a finished product

Test with adults and intended-age children under an appropriate usability plan: identify play and volume without prompting; pause while holding either hand; distinguish all cap symbols without colour; insert/remove/identify the cartridge; recover from missing/unknown cards and end-of-selection without losing place. Measure actuation/retention forces, travel, accidental presses, worn/dirty cards, headphone behaviour, audible level limits and battery/power interruptions. Observe accessibility/hand-size needs and revise the source. There are no test participants or pass results yet.

The RFQ must quote enclosure finishing, clean seams/port access, legible durable markings, colour consistency, hardware/firmware completion and the test evidence above. Public previews remain engineering and editorial demonstrations; no orders are open.
