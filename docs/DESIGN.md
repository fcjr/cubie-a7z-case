# Design notes

How the case is dimensioned, why the geometry is the way it is, and what to
know before modifying `case.py`. For printing and everyday use, see the
[README](../README.md).

## Source data

Everything is dimensioned from Radxa's official mechanical releases, kept
in this directory:

- [product brief](https://dl.radxa.com/cubie/a7z/docs/radxa_cubie_a7z_product_brief.pdf)
  (rev 1.1) — interface list, 65 × 30 mm outline, Ø2.8 holes on a
  57.8 × 22.9 grid
- [2D DXF + dimension drawing](https://dl.radxa.com/cubie/a7z/docs/hw/Radxa_Cubie_A7Z_2D_DXF_V1.10.zip)
  (V1.10) in `2d/`
- [3D STEP of the board](https://dl.radxa.com/cubie/a7z/docs/hw/Radxa_Cubie_A7Z_3D_STP_V1.10.zip)
  (V1.10) in `3d/`
- [components placement map](https://dl.radxa.com/cubie/a7z/docs/hw/radxa_cubie_a7z_components_placement_map_v1.11.pdf)
  and [schematic](https://dl.radxa.com/cubie/a7z/docs/hw/radxa_cubie_a7z_schematic_v1.11.pdf)
  (v1.11)

The connector positions in `case.py` were probed solid-by-solid from the 3D
STEP (573 solids; each bounding box measured in board coordinates), not
transcribed from marketing drawings. Board coordinates: x across the width
(0 at the GPIO edge), y along the length (0 at the fan/antenna end), z = 0
at the PCB bottom face.

Two caveats found the hard way, both from the STEP modelling connectors as
unnamed truncated blocks rather than full bodies:

- **The STEP has no microSD holder in it at all**, and the block that looks
  most like one isn't. Two revisions were lost to this. The block at the
  y = 0 short edge, on the bottom, measures 10.80 × 3.25 × 1.00 — and
  10.80 mm reads convincingly like an 11.0 mm card, which is how it became
  the card slot. It is the MIPI CSI FPC connector. So is the 13.70 × 4.26
  block at the ports edge (PCIe). Neither is a card holder; both are FPC
  connectors whose ribbons leave under the board.

  The real microSD is at the **other** short edge, y = 65, on the bottom —
  the end with the power USB-C. Two sources outside the STEP agree, and
  they are what the model is dimensioned from now:

  - Radxa's interface photo (`docs.radxa.com/img/cubie/a7z/a7z-interface.webp`),
    scaled against the known 30.01 × 65.02 outline, puts the holder shell at
    x 9.7–20.6, y 52.1–57.4. The same photo, cross-checked on the three port
    shells down the right-hand edge (they land on HDMI 9.27–15.77,
    USB3 37.01–45.95, PWR 49.56–58.50 to within a few tenths), also shows
    the CSI FPC connector sitting at the y = 0 edge on the bottom face.
  - The bottom DXF carries the holder's contact row at x 11.14–18.84,
    y 57.85–58.93 — nine pads in microSD's 1.10 / 0.70 mm pitch pattern.

- Modelled depths are meaningless, so only footprint and hang below the
  board are used. The microSD holder's hang is not in the STEP either;
  1.4 mm is taken as a generic push-pull holder, which is what sets
  `BOTTOM_DROP` and has to fit inside the 1.6 mm standoff gap.

## Geometry decisions

- **Port notches, open to the top.** The HDMI and USB-C shells overhang the
  board edge by 1.0 mm, so the board can only drop vertically into the tray
  if the wall is open above each shell. The tray gets notches; the lid
  keeps its rim and closes them. The lid is only relieved where it must be:
  the friction lip is cleared over each port span (shells reach x = 31.0,
  z = 4.4 — the lip's territory).
- **Port opening height** is set by the cavity, not by choice: a notch runs
  from just under its shell to the top of the wall, so every millimetre of
  headroom above the tallest part shows up as a taller-looking port. The
  cavity is therefore pinned to the USB-C shells at 4.40 plus 0.3, and the
  plug-overmold recesses stop at the seam instead of running up into the
  lid rim — that band above the seam was what made the ports read as a
  slot from outside.
- **Two cavity heights**, both driven from `use_headroom()`:
  *standard* clears the USB-C shells (case 9.1 mm), so the lid closes over
  the port notches; *slim* clears only the 3.10 mm fan header (case
  7.8 mm). Nothing in between is available, and the reason is the plug, not
  the shell: a plug has to reach a connector whose mouth spans z 1.24–4.40,
  so any lid sitting below 4.40 must be cut away over the ports rather than
  roofing them. On the slim lid the notches therefore run through the slab
  and clear the shells' full 7.35 mm depth inboard of the wall, which is
  why its top edge is bitten into at each port. The remaining stack —
  1.4 floor, 1.6 standoff, 1.2 board, 1.4 lid — is already at the thin end
  of what prints well.
- **Standoffs and hold-downs.** The board rests on four Ø5.4 bosses with
  Ø2.4 pins through its mounting holes; pins stop 0.1 mm below the board
  top. The lid presses down with four Ø3.2 posts landing on the bare
  mounting-hole pads — the only reliably clear spots on a board this
  dense. Bottom-side parts hang at most 1.4 mm — the microSD holder — into
  the 1.6 mm standoff gap.
- **GPIO.** The header comes populated and is 8.3 mm tall — 4.3 mm more
  than the cavity. The open lid slots it (sized for 5.08 × 50.8 mm female
  header housings; IDC ribbon sockets are wider and won't fit). The closed
  lid raises its whole top by 4.6 mm instead: a flat raised top still
  prints face-down with no supports, where a local blister over the header
  would hover above the bed once flipped.
- **microSD.** A 14 mm-wide slot through the y = 65 short wall, under board
  level — the card rides in the holder's hang below the PCB — running the
  full standoff gap. Both trays have it; card access isn't optional.

  A 15.0 mm card bottoms out with its leading edge at the back of the shell
  (y ≈ 52.2), which puts its other end at y ≈ 67.2 — level with the outer
  wall face at 67.12. Flush is nothing to pull on, so the outer 1.0 mm of
  wall is scalloped away over a 20 mm span around the slot, and the card
  stands that much proud of the surface a fingertip reaches. The scallop
  stays below board level and clear of the two snaps on that wall.
- **Snap closure.** Friction lip (1.2 × 1.6 mm, 0.15 clearance per side)
  with six rib/groove pairs: two per short wall, two on the ports wall
  between the notches, each placed clear of that wall's openings. The GPIO
  side gets none — the header opening eats the lip along that edge on the
  open lid, and even the closed lid trims it there because the lip's inner
  face (x = 1.05) would overlap the header body (x from 0.79).

  The geometry is lifted from the restorekit dongle cases, which lock
  well in the hand: a 0.6 dome on the lip against a 0.75 socket in the
  wall. Offset by the 0.15 lip clearance, the two are internally tangent
  when seated — the dome drops fully home rather than riding the socket
  rim — while still having to squeeze 0.45 mm past the wall going in,
  which is the click you feel.

  A 45° diamond rib was tried in between, on the theory that a sphere's
  underside is an unprintable overhang and 0.45 mm was more flex than a
  closed 1.2 mm lip loop could give. Both worries were wrong in practice:
  the dome is 0.6 mm across and prints without support, and the loop
  closes fine. What the rib got wrong is retention — symmetric 45° ramps
  cam out as easily as they cam in, so it shut softly and pulled apart.
  Retention wants a face perpendicular to the pull; printability wants one
  at 45°; the dome splits the difference by being steep only near its
  equator.
- **Fillets and chamfers** follow the print orientation. Vertical-axis
  fillets (the 4 mm body corners, the vent ends, the GPIO slot, the port
  openings) are free — they never overhang. The two bed-facing edges get
  45° chamfers instead of fillets: a fillet there curves out to a 90°
  overhang on the first layers, a chamfer doesn't.
- **Pry notch.** A scallop in the GPIO-side wall top, open upward so it
  needs no support, positioned where the lid has no lip anyway.
- **Cable exits** (full tray only), all at the y = 0 end or the ports wall:
  an antenna/fan notch over the y = 0 wall, a CSI ribbon opening under the
  same wall (that connector is on the board's bottom face, so its ribbon
  leaves below the board rather than over it), and a PCIe FPC slot in the
  ports wall between the HDMI and USB-C notches, also below board level.
  The lids are cut by the same solids — on a lid they only trim the hidden
  lip, which is why either lid also fits the sealed tray.
- **Status LED window.** A Ø1.6 pinhole through the lid slab over the
  emitter, which sits in the 2.2 mm gap between the two USB-C ports. It has
  to thread a needle — at Ø2.0 it nicked both the lip's inner face and the
  power port's notch by about 0.05 — so a build-time check reports its three
  clearances and fails if any drops below 0.1 mm.

  Standard lids only. On a slim lid the port notches run through the slab,
  which turns the material the window would pass through into a 0.95 mm fin
  between two openings, so the slim lids don't get one.
- **Boot button.** A 3.00 × 2.50 × 1.00 tact switch on the board underside
  at (27.51, 17.94) — just behind the micro HDMI port, not under the power
  port, where an earlier revision put it after picking a similar-looking
  3.70 × 1.60 part at y ≈ 52. Two independent checks agree: the placement
  map's `SW1` designator lands at (26.95, 17.95) once the bottom view's
  mirrored x is undone, and the hardware confirms the HDMI end. The floor
  gets a Ø3.2 poke hole with a mirrored `BOOT` engraving that reads
  correctly from below, its ink stopping 0.7 mm clear of the hole. The
  engraving is placed off `SW1` rather than off a literal: when the switch
  moved to its real position the label didn't follow, and sat 36 mm away at
  the wrong end of the case for a revision.

## Self-checks

`case.py` refuses to export if anything is wrong, so a bad edit fails the
build instead of failing the print:

- **Fit**: a mock board rebuilt from the probed STEP solids must have zero
  intersection with every tray and lid, both seated and swept vertically
  (the drop-in path), and each lid must clear each tray.
- **Stroke width**: the fonts are measured, not trusted — a stem of the
  actual rendered face must come out ≥ 0.65 mm, so a missing Arial Black
  silently falling back to something lighter can't produce unprintable
  text.
- **Piece width**: the stem check misses sub-stem features (a lowercase
  i's dot is narrower than its stem — the reason the wordmark is
  uppercase), so the narrowest loose inlay piece is also gated at 0.6 mm.
- **Snap engagement**: the interference each rib asks the lip to flex over
  must land between 0.12 and 0.30 mm, and the part of the rib that reaches
  into the wall must sit entirely inside its groove — a rib that bottoms
  out jams instead of clicking.
- **Printability**: every part must be a **single connected solid**, and no
  face may point downward more steeply than 45° in print orientation. The
  connectivity half of this is not theoretical: it caught the closed lid
  shipping as five separate solids, its whole lip — and four of the six
  snaps — floating under the cap with nothing joining them to it, because
  hollowing the cap to the full cavity footprint had removed the material
  directly above the lip. Ceilings over an opening (the microSD slot, the
  cable notches, the engraved letters) are bridges anchored on both sides
  and print fine, so they are reported as an area rather than failed.

## Engraving

Arial Black, 0.6 mm deep with flat bottoms. The font is picked for stroke
width, not looks: a 0.4 mm nozzle wants ~0.8 mm strokes so each letter stem
gets two perimeters, and free-standing inlay letters get dropped by the
slicer if they come in under a nozzle width. Arial Black stems measure
0.222 × size against Arial Bold's 0.145 — 53% more stroke for 9% more
width (the scheme comes from the restorekit dongle cases).

The lid layout is set by the two big openings: the GPIO slot owns one side
and the vent field owns the middle, so the wordmark runs lengthwise in the
strip between them and the port labels run lengthwise above their ports.
All marks are built in absolute coordinates and cut in a single pass —
re-selecting `faces(">Z")` between engravings starts matching the coplanar
islands inside letter counters and sends later marks astray. Each mark is
snapped to its ink bounding box before placement because CadQuery centres
text on font metrics, not on the ink it draws.

## White text inlay

Each `*-inlay.stl` is exactly the volume of its lid's engraved pockets,
exported in the same orientation — union the two and you get a flat-topped
lid with no interference and no gap (verified: 0.000 mm³ intersection and
0.000 mm³ residual).

With a multi-material printer: load the lid, add the inlay to it as a
second *part* of the same object (not a separate object, so it isn't
re-centred), assign a colour, print top-face-down. Single extruder: print
the inlay on its own and glue the letters in — but note the fit is
zero-clearance by construction, so give the inlay a little slicer XY
compensation (or a light sand) or the letters won't drop in.

A plain filament swap does *not* work: the lid prints top-face-down with
the text recessed, so the letters are voids in the first layers — swapping
colours the top face and leaves the letters in the body colour, the inverse
of what you want.

## Working on the model

- `uv run case.py` — rebuilds `output/`. All dimensions live in the
  parameter block at the top of `case.py`, with the probed board facts
  separated from the case design choices.
- `uv run render_images.py` — regenerates the README images in `images/`
  (runs the full build first; rasterising uses macOS `qlmanage`).
- The checks print their interference volumes on every run; keep them at
  zero. If you move or resize a mark, the stroke/piece gates re-verify it
  automatically.
