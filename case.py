"""Radxa Cubie A7Z enclosure, generated with CadQuery.

Two pieces: a bottom tray the board drops into and a friction-fit snap lid.
Dimensions come from Radxa's official mechanical data in ./docs/ — the 2D
dimension drawing (65.0 x 30.0 mm outline, 4x2.8 mm holes on a 57.8 x 22.9
grid, 3.6 mm from the edges) and the 3D STEP of the board, which was probed
solid-by-solid for the connector positions below.

Coordinates: x across the board width (0 at the GPIO edge, 30.01 at the
ports edge), y along the length (0 at the fan/antenna end), z = 0 at the
PCB bottom face.

Run:  uv run case.py
Outputs STEP + STLs into ./output/.
"""

import os

import cadquery as cq

# --- board facts (probed from docs/3d/Radxa_Cubie_A7Z_3D_STP_V1.10.stp) ---
PCB_W = 30.01
PCB_L = 65.02
PCB_T = 1.2
HOLE_D = 2.8
HOLES = [(3.56, 3.61), (26.46, 3.61), (3.56, 61.41), (26.46, 61.41)]

GPIO = (0.79, 5.87, 7.07, 57.87)     # x0, x1, y0, y1; pins top out 8.3 above PCB
GPIO_H = 8.3

# ports edge (x = 30.01); all three shells overhang the board edge by 1.0
HDMI_Y = (9.27, 15.77)               # micro HDMI shell, z 0.66..4.10
USB3_Y = (37.01, 45.95)              # USB-C 3.1 / DP alt mode, z 1.24..4.40
PWR_Y = (49.56, 58.50)               # USB-C 2.0 / power + OTG, z 1.24..4.40

# bottom side. Three parts hang under the board, and the STEP models only
# two of them — as truncated blocks, with no names. An earlier revision read
# the wrong one as the card slot, so both are pinned down here:
#   MIPI CSI FPC, at the y=0 short edge — 10.80 wide x 3.25 deep x 1.00 tall
#   is a 0.5 mm-pitch FPC connector, not a card holder. Its ribbon leaves
#   under the board over that edge.
#   PCIe Gen3 FPC, at the ports long edge mid-board — 13.70 long x 4.26 deep,
#   likewise an FPC connector; its ribbon leaves under the board sideways.
# The microSD is absent from the STEP entirely, which is what let the CSI
# connector pass for it: 10.80 wide reads a lot like an 11.0 mm card. It is
# at the *other* short edge (y=65), also on the bottom, and two independent
# sources agree on where. Radxa's interface photo
# (docs.radxa.com/img/cubie/a7z/a7z-interface.webp) puts the holder shell at
# x 9.7..20.6, y 52.1..57.4 when scaled against the known 30.01 x 65.02
# outline; the bottom DXF has the holder's contact row there too — nine pads
# in microSD's 1.10/0.70 mm pitch pattern, x 11.14..18.84, y 57.85..58.93.
# The same photo shows the CSI FPC connector at the y=0 edge, x 9.8..19.1,
# on the bottom face, which is the block the STEP does model.
CSI_X = (9.61, 20.41)                # MIPI CSI FPC, y 1.32..4.57, z -1.00..0
PCIE = (25.05, 29.31, 19.42, 33.12)  # x0, x1, y0, y1; z -1.20..0
SD_X = (9.65, 20.65)                 # microSD holder shell, y 52.1..59.4
SD_DROP = 1.4                        # holder hang below the PCB. Not in the
                                     # STEP; a generic push-pull holder.
# A 15.0 mm card bottoms out with its leading edge at the back of the shell
# (y ~52.2), so its other end lands at y ~67.2 — level with the outer wall
# face at 67.12. Flush is not grippable, hence the scallop around the slot.
# USB BOOT button: bottom side, just behind the micro HDMI port. A 3.00 x
# 2.50 x 1.00 tact switch at x 26.01..29.01, y 16.69..19.19. Confirmed two
# ways, because the board has a second, similar-looking part at y 51.9 that
# an earlier revision used by mistake: the placement map's SW1 designator
# lands at (26.95, 17.95) once the bottom view's mirrored x is undone, and
# the switch is where the hardware says it is.
SW1 = (27.51, 17.94)
BOTTOM_DROP = SD_DROP                # deepest bottom-side part

# The y = 65 edge carries nothing on the top side — everything at that end
# (the microSD holder) is underneath.
# y = 0 edge, top side: fan header (x 18.25..23.00, 3.1 tall) and the
# antenna U.FL (x 13.31..16.31, 2.5 tall); both need a cable path out
ANT_FAN_X = (12.8, 23.5)

# Status LED, in the 2.2 mm gap between the two USB-C ports. The window has
# to thread a needle: at Ø2.0 it overran the lip's inner face (x = 28.96) on
# one side and the power port's notch (y = 48.86) on the other, by about
# 0.05 each, nicking both. Ø1.6 clears everything and still sits over the
# emitter, which spans y 47.27..48.54.
LED = (28.01, 47.91)
LED_D = 1.6
SOC = (10.30, 25.40, 20.65, 35.75)   # Allwinner A733, vent slots go above it

# --- case parameters ---
CLR = 0.3        # board clearance per side
WALL = 1.8
FLOOR = 1.4      # 7 layers at 0.2; plenty over a footprint this small
STANDOFF = 1.6   # board bottom above the tray floor; bottom parts reach 1.27
SHELL_TOP = 4.40  # tallest port shell, measured from the PCB bottom face
FAN_HDR_TOP = 3.10  # tallest part that isn't a port shell

# Cavity height above the PCB top, and the one number that sets how tall the
# case is. Two settings:
#
#   standard — clears the USB-C shells, so the lid closes over the port
#     notches and the ports read as slots in the tray wall alone. Also
#     leaves 1.6 mm above the fan header for a fan cable.
#   slim — clears the fan header and nothing more. The shells now stand
#     proud of the cavity, so the port notches carry on through the lid and
#     open at the top edge; the case loses 1.3 mm. No room for a fan lead,
#     which is the trade.
#
# Below the standard figure the lid would foul the shells; above it, every
# extra millimetre shows up as slop above the ports.
HEADROOM_STD = SHELL_TOP + 0.3 - PCB_T
HEADROOM_SLIM = FAN_HDR_TOP + 0.3 - PCB_T
LID_T = 1.4      # 0.6 of that is engraving depth, leaving 0.8 of skin

CAV_X0, CAV_X1 = -CLR, PCB_W + CLR
CAV_Y0, CAV_Y1 = -CLR, PCB_L + CLR
OUT_X0, OUT_X1 = CAV_X0 - WALL, CAV_X1 + WALL
OUT_Y0, OUT_Y1 = CAV_Y0 - WALL, CAV_Y1 + WALL
Z_FLOOR = -STANDOFF - FLOOR          # outer bottom face
CORNER_R = 4.0
EDGE_CHAMFER = 0.8  # bed-facing outer edges. A fillet there would curve out
                    # to a 90° overhang on the first layers; 45° prints clean.

LIP_T = 1.2
LIP_H = 1.6
LIP_CLR = 0.15   # per side

# Set per variant by use_headroom(); the geometry below reads them as
# globals so both heights share one set of builders.
CAV_TOP = SNAP_Z = None
notches = lip_clears = recesses = sd_slot = aux_notches = None
shell_notches = None
PORTS_THROUGH_LID = False

# Snap geometry copied from the restorekit dongle cases, where this exact
# pairing gives a lock that shuts with a real click and stays shut: a 0.6
# dome on the lip against a 0.75 socket in the wall, the two offset by the
# 0.15 lip clearance. That offset makes them internally tangent when
# seated — the dome drops fully home instead of riding on the socket rim —
# while the dome still has to squeeze 0.45 mm past the wall on the way in,
# which is what you feel as the click.
#
# A 45° rib was tried in between and was the wrong call: symmetric ramps
# cam back out as easily as they go in, so it closed softly and pulled
# apart. The dome's underside is a steep overhang, but it is 0.6 mm across
# and prints without support in practice — as the reference cases have.
SNAP_BUMP_R = 0.6
SNAP_SOCKET_R = 0.75

# two per short wall, two on the ports wall, each clear of that wall's
# openings. None on the GPIO wall — the header opening eats the lip there.
SNAPS = [
    (4.0, CAV_Y0, "y"), (27.0, CAV_Y0, "y"),   # fan/antenna end
    (4.5, CAV_Y1, "y"), (26.5, CAV_Y1, "y"),   # microSD end
    (CAV_X1, 4.0, "x"), (CAV_X1, 26.0, "x"),   # ports wall, between notches
]

# 3 x 0.2 mm layers: the lid prints top-face-down, so the marks double as
# pockets for a two-colour inlay (see README)
TEXT_DEPTH = 0.6

# Arial Black, not Arial Bold: a 0.4 mm nozzle wants two perimeters per
# letter stem, and the free-standing inlay letters get dropped by the slicer
# if they come in under a nozzle width. Arial Black stems are 0.222 x size
# against Arial Bold's 0.145 — see the restorekit dongle cases for the
# full argument.
FONT = "Arial Black"
STEM_RATIO = 0.222
MIN_STROKE = 0.65

WORDMARK_SIZE = 3.2
LABEL_SIZE = 3.0


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY", origin=(x0, y0, z0)).box(
        x1 - x0, y1 - y0, z1 - z0, centered=(False, False, False))


def outer_profile(z0, z1):
    return (
        box(OUT_X0, OUT_X1, OUT_Y0, OUT_Y1, z0, z1)
        .edges("|Z")
        .fillet(CORNER_R)
    )


def snap_dome(x, y, r):
    """Sphere centred on a face: a socket cut into the tray's cavity wall,
    or the mating dome standing off the lid lip."""
    return cq.Workplane("XY").sphere(r).translate((x, y, SNAP_Z))


def lip_face(x, y, axis):
    """Same snap position, moved from the cavity wall to the lip's face."""
    if axis == "x":
        return (x - LIP_CLR if x > PCB_W / 2 else x + LIP_CLR), y
    return x, (y - LIP_CLR if y > PCB_L / 2 else y + LIP_CLR)


# --- shared wall cutters ---
# The port openings are notches through the tray wall, open to the top of
# the wall. Windows with a closed top would be nicer-looking, but the shells
# overhang the board edge by 1.0 mm, so the board can only drop in
# vertically if the wall is open above each shell. At standard height the
# lid closes over them; on the slim variant they carry on through the lid.
NOTCH_X0 = CAV_X1 - LIP_CLR - LIP_T - 0.1  # inboard of the lip band
SHELL_X0 = 23.4   # just inboard of the port shells (they start at 23.66)
PORT_SPANS = [  # y0, y1, sill z — sills sit just under each shell
    (HDMI_Y[0] - 0.5, HDMI_Y[1] + 0.5, 0.5),   # micro HDMI: shell z 0.66..4.10
    (USB3_Y[0] - 0.7, USB3_Y[1] + 0.7, 1.0),   # USB-C x2: shells z 1.24..4.40
    (PWR_Y[0] - 0.7, PWR_Y[1] + 0.7, 1.0),
]


def use_headroom(headroom):
    """Point the builders at one of the two cavity heights."""
    global CAV_TOP, SNAP_Z, notches, lip_clears, recesses, sd_slot
    global aux_notches, PORTS_THROUGH_LID, shell_notches

    CAV_TOP = PCB_T + headroom
    SNAP_Z = CAV_TOP - LIP_H + 0.5
    PORTS_THROUGH_LID = CAV_TOP < SHELL_TOP + 0.25

    notches = None
    shell_notches = None
    for y0, y1, sill in PORT_SPANS:
        top = (max(CAV_TOP, SHELL_TOP + 0.3) + LID_T + 0.5
               if PORTS_THROUGH_LID else CAV_TOP + 0.1)
        n = (box(NOTCH_X0, OUT_X1 + 0.5, y0, y1, sill, top)
             .edges("|Z").fillet(0.6))
        notches = n if notches is None else notches.union(n)
        # A slim lid sits below the shells, so its notch has to clear their
        # whole 7.35 mm depth inboard of the wall, not just the wall band.
        s = (box(SHELL_X0, OUT_X1 + 0.5, y0, y1, CAV_TOP - LIP_H - 0.1, top)
             .edges("|Z").fillet(0.6))
        shell_notches = s if shell_notches is None else shell_notches.union(s)
    # where the lid does clear the shells it still needs its lip relieved
    # over each port span (the shells reach x = 31.0, z 4.4 — into the
    # lip's territory, not the slab's)
    lip_clears = None
    for y0, y1, _ in PORT_SPANS:
        c = box(NOTCH_X0, CAV_X1 + 0.2, y0, y1, CAV_TOP - LIP_H - 0.1,
                CAV_TOP + 0.05)
        lip_clears = c if lip_clears is None else lip_clears.union(c)
    # shallow outer recesses so plug overmolds can seat against the shells:
    # micro HDMI overmolds run ~11 x 6.5, USB-C ~12 x 6.5. One shared recess
    # spans both USB-C ports — separate ones would leave a 0.8 mm fin. These
    # stop at the seam and cut the tray only: running them up into the lid
    # rim is what made the ports read as a tall slot from outside.
    recesses = (
        box(OUT_X1 - 1.0, OUT_X1 + 0.5, (HDMI_Y[0] + HDMI_Y[1]) / 2 - 5.5,
            (HDMI_Y[0] + HDMI_Y[1]) / 2 + 5.5, 0.0, CAV_TOP + 0.1)
        .edges("|Z").fillet(0.6)
        .union(box(OUT_X1 - 1.0, OUT_X1 + 0.5, USB3_Y[0] - 1.4,
                   PWR_Y[1] + 1.4, 0.0, CAV_TOP + 0.1)
               .edges("|Z").fillet(0.6))
    )
    # microSD slot through the y=65 short wall, under the board — the card
    # rides in the holder's hang below the PCB. Every tray gets this: card
    # access isn't optional.
    #
    # The card's outer end sits level with the wall's outer face, so a plain
    # slot would leave nothing to pull on. The slot is therefore cut wide
    # (1.6 clear of the holder each side, as much as the y=65 snaps allow)
    # and the outer 1.0 mm of wall is scalloped away over it, which puts the
    # card 1.0 mm proud of the surface a fingertip can reach.
    sd_slot = (
        box(SD_X[0] - 1.6, SD_X[1] + 1.6, CAV_Y1 - 1.0, OUT_Y1 + 0.5,
            -STANDOFF, 0.05).edges("|Z").fillet(1.0)
        .union(box(SD_X[0] - 3.0, SD_X[1] + 3.0, OUT_Y1 - 1.0, OUT_Y1 + 0.5,
                   -STANDOFF - 0.4, 0.05).edges("|Z").fillet(0.7))
    )
    # cable exits, skipped by the sealed tray. Lids get cut by these too: on
    # a lid they only trim the hidden lip, so either lid fits either tray of
    # the same height.
    aux_notches = (
        # antenna pigtail + fan cable path over the y=0 wall. Normally it
        # stops 0.6 short of the cavity top so some lip survives, but on the
        # slim variant the 3.1 mm fan header would then foul that lip, so
        # the band loses its lip entirely.
        box(ANT_FAN_X[0], ANT_FAN_X[1], OUT_Y0 - 0.5, CAV_Y0 + 1.4, PCB_T,
            CAV_TOP - 0.6 if CAV_TOP - 0.6 >= FAN_HDR_TOP + 0.25
            else CAV_TOP + 0.05)
        # MIPI CSI ribbon exit under the y=0 wall. The connector is on the
        # board's bottom face at that edge, so the ribbon leaves below the
        # board, not over it — same band the card slot used to occupy.
        .union(box(CSI_X[0] - 1.2, CSI_X[1] + 1.2, OUT_Y0 - 0.5,
                   CAV_Y0 + 1.0, -STANDOFF, 0.05).edges("|Z").fillet(1.0))
        # PCIe FPC ribbon exit: the connector sits on the board bottom at
        # the ports edge, so its ribbon leaves under the board between the
        # HDMI and USB-C notches
        .union(box(CAV_X1 - 1.0, OUT_X1 + 0.5, PCIE[2] - 0.6, PCIE[3] + 0.6,
                   -1.6, 0.05))
    )

# --- bottom trays ---
# Two variants: the full tray has exits for the PCIe FPC, CSI FPC and the
# antenna/fan cables; the sealed tray omits all three for a cleaner box
# when nothing hangs off those connectors.
def build_tray(sealed):
    bottom = outer_profile(Z_FLOOR, CAV_TOP)
    # chamfer, not fillet: this face is on the bed
    bottom = bottom.edges("<Z").chamfer(EDGE_CHAMFER)

    cutters = box(CAV_X0, CAV_X1, CAV_Y0, CAV_Y1, -STANDOFF, CAV_TOP + 0.1)
    cutters = cutters.union(sd_slot)
    # USB BOOT button poke hole, in the floor under the power port
    cutters = cutters.union(
        cq.Workplane("XY", origin=(SW1[0], SW1[1], Z_FLOOR - 0.5))
        .circle(1.6).extrude(FLOOR + 0.6))
    # pry notch: a scallop in the GPIO-side wall top so a fingernail can get
    # under the lid edge. Open upward, so nothing overhangs. It lands where
    # the lid has no lip anyway (the header opening already clears it).
    cutters = cutters.union(
        box(OUT_X0 - 0.5, OUT_X0 + 1.0, PCB_L / 2 - 5.0, PCB_L / 2 + 5.0,
            CAV_TOP - 1.5, CAV_TOP + 0.5).edges("|Z").fillet(0.7))
    # snap sockets in the cavity walls
    for sx, sy, axis in SNAPS:
        cutters = cutters.union(snap_dome(sx, sy, SNAP_SOCKET_R))
    bottom = (bottom.cut(cutters, clean=False).cut(notches, clean=False)
              .cut(recesses, clean=False))
    if not sealed:
        bottom = bottom.cut(aux_notches, clean=False)

    # standoffs: bosses under the four mounting pads, pins into the 2.8 mm
    # holes. Pins stop 0.1 under the board top so the lid posts land on the
    # pads alone.
    for hx, hy in HOLES:
        bottom = bottom.union(
            cq.Workplane("XY", origin=(hx, hy, -STANDOFF)).circle(2.7)
            .extrude(STANDOFF))
        pin = (cq.Workplane("XY", origin=(hx, hy, 0)).circle(1.2)
               .extrude(PCB_T - 0.1).edges(">Z").chamfer(0.3))
        bottom = bottom.union(pin)

    # "BOOT" on the underside beside the poke hole, mirrored to read from
    # below. It goes on the +y side of the hole, running along the case
    # rather than squeezed against the HDMI notch. Anchored off SW1 so it
    # cannot drift away from the hole again — it spent a revision stranded
    # at y = 54, left behind when the switch moved to its real position.
    t = (cq.Workplane("XY", origin=(0, 0, Z_FLOOR)).text(
        "BOOT", LABEL_SIZE, TEXT_DEPTH, font=FONT, kind="regular")
        .rotate((0, 0, 0), (0, 0, 1), 90))
    b = t.val().BoundingBox()
    t = t.mirror("YZ", ((b.xmin + b.xmax) / 2, 0, 0))
    b = t.val().BoundingBox()
    # ink starts 0.7 clear of the poke hole's edge (the hole is Ø3.2)
    t = t.translate((SW1[0] - (b.xmin + b.xmax) / 2,
                     SW1[1] + 1.6 + 0.7 - b.ymin, 0))
    return bottom.cut(t, clean=False)


use_headroom(HEADROOM_STD)
bottom = build_tray(sealed=False)
bottom_s = build_tray(sealed=True)

# --- lids ---
# Two variants. The open lid has a slot the GPIO header pokes through: the
# header is 8.3 mm tall, 4.3 more than the cavity. The closed lid caps it
# instead, raising the whole top by LID_RAISE — a flat raised top still
# prints face-down with no supports, where a local blister over the header
# would hover 4.6 mm above the bed once flipped.
# A closed lid's ceiling is absolute — it is set by the header, not by the
# cavity below it — so a closed lid over the slim tray ends up the same
# height overall as one over the standard tray. Computed here rather than
# once at import, because the cavity height changes between variants.
GPIO_CEIL = PCB_T + GPIO_H + 0.3


def build_lid(closed, header=True):
    """header=False assumes the 40-pin header is not fitted, which lets a
    flat lid stay down at cavity height with no opening in it at all."""
    ceil = max(CAV_TOP, GPIO_CEIL) if closed and header else CAV_TOP
    top_z = ceil + LID_T
    # chamfer, not fillet: this face is on the bed (the lid prints inverted)
    lid = outer_profile(CAV_TOP, top_z).edges(">Z").chamfer(EDGE_CHAMFER)
    if closed:
        # Hollow the cap only inside the lip's inner face, not to the full
        # cavity footprint. Cutting the wider footprint would take away the
        # material directly above the lip and leave the lip — and the four
        # snaps riding on it — as islands floating under the cap with
        # nothing joining them to it. What remains is a ledge the lip hangs
        # from, which also seats on the tray's wall top.
        inset = LIP_CLR + LIP_T
        lid = lid.cut(
            box(CAV_X0 + inset, CAV_X1 - inset, CAV_Y0 + inset,
                CAV_Y1 - inset, CAV_TOP - 0.1, ceil),
            clean=False)
    lip = (
        cq.Workplane("XY", origin=((CAV_X0 + CAV_X1) / 2,
                                   (CAV_Y0 + CAV_Y1) / 2, CAV_TOP - LIP_H))
        .rect(CAV_X1 - CAV_X0 - 2 * LIP_CLR, CAV_Y1 - CAV_Y0 - 2 * LIP_CLR)
        .rect(CAV_X1 - CAV_X0 - 2 * LIP_CLR - 2 * LIP_T,
              CAV_Y1 - CAV_Y0 - 2 * LIP_CLR - 2 * LIP_T)
        .extrude(LIP_H)
    )
    lid = lid.union(lip)
    if not closed and header:
        # GPIO slot, sized for 2.54 mm female headers (5.08 x 50.8 housings)
        lid = lid.cut(
            box(GPIO[0] - 0.5, GPIO[1] + 0.5, GPIO[2] - 0.5, GPIO[3] + 0.5,
                CAV_TOP - 0.1, top_z + 0.5).edges("|Z").fillet(1.5),
            clean=False)
    if header:
        # both variants lose the lip band beside the header: its inner face
        # (x = 1.05) overlaps the header body (x from 0.79), and beside the
        # open lid's slot only a 0.4 mm sliver would survive anyway. On the
        # closed lid the cut runs the full height, because the seating ledge
        # above the lip would foul the header too. With no header fitted the
        # lip survives all the way round, which grips a little better.
        lid = lid.cut(
            box(CAV_X0 - 0.1, CAV_X0 + LIP_CLR + LIP_T + 0.1, GPIO[2] - 0.5,
                GPIO[3] + 0.5, CAV_TOP - LIP_H - 0.1,
                (ceil + 0.1) if closed else (CAV_TOP + 0.1)), clean=False)
    # On the slim variant the shells stand above the cavity, so the port
    # notches run right through the lid; otherwise the lid keeps its rim and
    # only needs the lip relieved. Cable-path cuts match the full tray (on a
    # lid they only trim the lip, so they're harmless over the sealed tray's
    # solid walls). The overmold recesses stop at the seam, so the lid's
    # outer face stays unbroken.
    lid = lid.cut(shell_notches if PORTS_THROUGH_LID else lip_clears,
                  clean=False)
    lid = lid.cut(aux_notches, clean=False)
    # hold-down posts onto the four mounting-hole pads (the only bare spots
    # on the board top), pressing the board onto the standoffs
    for hx, hy in HOLES:
        lid = lid.union(
            cq.Workplane("XY", origin=(hx, hy, PCB_T)).circle(1.6)
            .extrude(ceil - PCB_T))
    # snap domes on the lip
    for sx, sy, axis in SNAPS:
        lid = lid.union(snap_dome(*lip_face(sx, sy, axis), SNAP_BUMP_R))
    # vent slots over the SoC, rounded ends
    for vx in (11.0, 13.8, 16.6, 19.4, 22.2, 25.0):
        lid = lid.cut(box(vx - 0.9, vx + 0.9, 21.5, 34.5, ceil - 0.1,
                          top_z + 0.5).edges("|Z").fillet(0.85), clean=False)
    return lid, ceil, top_z

# --- lid graphics ---
# Built in absolute coordinates and cut in one pass; re-selecting
# faces(">Z") between engravings picks up the coplanar islands inside
# letter counters and sends later marks astray (see the dongle-probe case).
#
# The GPIO opening owns x < 6.4 and the vents own x 10..26 over the SoC, so
# the wordmark runs lengthwise in the strip between them, and the port
# labels run lengthwise above their ports at x ~27.


def place(shape, cx=None, cy=None, ymin=None):
    """Anchor a mark by its ink bounding box, not cadquery's font metrics."""
    b = shape.val().BoundingBox()
    dx = 0.0 if cx is None else cx - (b.xmin + b.xmax) / 2
    if ymin is not None:
        dy = ymin - b.ymin
    elif cy is not None:
        dy = cy - (b.ymin + b.ymax) / 2
    else:
        dy = 0.0
    return shape.translate((dx, dy, 0))


def engrave(label, size, top_z, rot=90):
    t = cq.Workplane("XY", origin=(0, 0, top_z - TEXT_DEPTH)).text(
        label, size, TEXT_DEPTH, font=FONT, kind="regular")
    return t.rotate((0, 0, 0), (0, 0, 1), rot) if rot else t


def thru_hole(x, y, d, ceil):
    """Window through the lid slab only — starting at its underside keeps
    the cutter out of the lip's z range (the LED sits 1 mm from the lip)."""
    return (cq.Workplane("XY", origin=(x, y, ceil))
            .circle(d / 2).extrude(LID_T + 1))


def build_marks(ceil, top_z, led=True):
    # uppercase on purpose: the dot of a lowercase i is a 0.43 mm loose
    # piece in Arial Black — narrower than the stems the stroke check
    # measures — and neither the standalone dot nor its pocket survives a
    # 0.4 mm nozzle
    inlay = place(engrave("CUBIE A7Z", WORDMARK_SIZE, top_z), cx=8.2,
                  cy=PCB_L / 2)
    for label, cy in (("HDMI", (HDMI_Y[0] + HDMI_Y[1]) / 2),
                      ("USB3", (USB3_Y[0] + USB3_Y[1]) / 2),
                      ("PWR", (PWR_Y[0] + PWR_Y[1]) / 2)):
        inlay = inlay.union(place(engrave(label, LABEL_SIZE, top_z),
                                  cx=27.2, cy=cy))
    if not led:
        return inlay, inlay
    return inlay, inlay.union(thru_hole(*LED, LED_D, ceil))


lid, lid_ceil, lid_top = build_lid(closed=False)
inlay, marks = build_marks(lid_ceil, lid_top)
lid = lid.cut(marks, clean=False)

lid_c, lid_c_ceil, lid_c_top = build_lid(closed=True)
inlay_c, marks_c = build_marks(lid_c_ceil, lid_c_top)
lid_cp = lid_c.cut(thru_hole(*LED, LED_D, lid_c_ceil), clean=False)  # plain: LED only
lid_c = lid_c.cut(marks_c, clean=False)

STD_TOP = lid_top

# --- slim variant ---
# A shorter tray and its matching lid, for builds with no fan lead. Only
# the open lid is worth doing slim: a closed one has to clear the 8.3 mm
# GPIO header, which sets its height regardless of the cavity below.
#
# No LED window on any slim lid. The window lives in the 2.2 mm gap between
# the USB3 and power notches, and on a slim lid those notches carry on
# through the slab — so what the standard lid drills through solid material,
# a slim one would drill through the 0.95 mm fin left standing between two
# openings.
use_headroom(HEADROOM_SLIM)
bottom_lo = build_tray(sealed=False)
bottom_lo_s = build_tray(sealed=True)
lid_lo, lid_lo_ceil, lid_lo_top = build_lid(closed=False)
inlay_lo, marks_lo = build_marks(lid_lo_ceil, lid_lo_top, led=False)
lid_lo = lid_lo.cut(marks_lo, clean=False)
SLIM_TOP = lid_lo_top

# Closed, unengraved, on the slim lip — for a slim tray with the header
# covered. It is no shorter than the standard closed lid: the 8.3 mm header
# sets that ceiling whatever the cavity underneath is doing.
lid_lo_cp, lid_lo_cp_ceil, lid_lo_cp_top = build_lid(closed=True)
SLIM_CLOSED_TOP = lid_lo_cp_top

# Slim height, no opening, no engraving — the flat lid, which only works if
# the 40-pin header is not fitted. With one fitted there is nowhere for it
# to go: at 8.3 mm it stands 5 mm above the cavity, so a lid that stays down
# has to either let it through or rise to meet it.
lid_lo_p, lid_lo_p_ceil, lid_lo_p_top = build_lid(closed=False, header=False)
use_headroom(HEADROOM_STD)  # checks below rebuild against the standard height

# --- checks ---
# 1) stroke width: a missing Arial Black falls back silently to something
#    lighter and unprintable, so measure a stem instead of trusting the name
stem = cq.Workplane("XY").text("I", 1.0, 0.1, font=FONT, kind="regular")
stem = stem.val().BoundingBox().xlen
for name, size in (("wordmark", WORDMARK_SIZE), ("labels", LABEL_SIZE)):
    w = stem * size
    flag = "" if w >= MIN_STROKE else f"  <-- under {MIN_STROKE} mm"
    print(f"{name:10} size {size}  stems {w:.2f} mm{flag}")
if stem * min(WORDMARK_SIZE, LABEL_SIZE) < MIN_STROKE:
    raise SystemExit(
        f"stroke too thin: {FONT!r} measured {stem:.3f} per unit size, "
        f"expected ~{STEM_RATIO}. Is the font installed?")
# the stem check misses sub-stem features (a lowercase i's dot is narrower
# than its stem), so also gate on the narrowest loose inlay piece
narrow = min(min(s.BoundingBox().xlen, s.BoundingBox().ylen)
             for s in inlay.val().Solids())
print(f"narrowest inlay piece {narrow:.2f} mm ({len(inlay.val().Solids())} pieces)")
if narrow < 0.6:
    raise SystemExit(f"inlay piece {narrow:.2f} mm wide won't survive a "
                     "0.4 mm nozzle")

# 2) fit: a mock board built from the probed solids must not touch either
#    part, seated or while dropping straight down into the tray
MOCK = [
    (GPIO[0], GPIO[1], GPIO[2], GPIO[3], PCB_T, PCB_T + GPIO_H),         # header
    (23.5, PCB_W + 1.0, HDMI_Y[0], HDMI_Y[1], 0.66, 4.10),               # hdmi
    (23.6, PCB_W + 1.0, USB3_Y[0], USB3_Y[1], 1.24, 4.40),               # usb3
    (23.6, PCB_W + 1.0, PWR_Y[0], PWR_Y[1], 1.24, 4.40),                 # pwr
    (PCIE[0], PCIE[1], PCIE[2], PCIE[3], -1.20, 0.0),                    # pcie fpc
    (SW1[0] - 1.85, SW1[0] + 1.85, SW1[1] - 0.8, SW1[1] + 0.8, -1.27, 0.0),
    (SD_X[0], SD_X[1], 52.1, 59.4, -SD_DROP, 0.0),                       # microsd
    (8.55, 21.67, 7.25, 18.87, -0.8, 0.0),                               # ufs pad
    (CSI_X[0], CSI_X[1], 0.0, 4.57, -1.0, 0.0),                          # csi fpc
    (18.25, 23.00, 0.94, 3.74, PCB_T, 3.1),                              # fan
    (13.31, 16.31, 0.82, 3.67, PCB_T, 2.45),                             # antenna
    (SOC[0], SOC[1], SOC[2], SOC[3], PCB_T, 2.55),                       # soc
    (6.84, 21.94, 37.89, 47.99, PCB_T, 2.2),                             # lpddr
]
pcb = box(0, PCB_W, 0, PCB_L, 0, PCB_T)
for hx, hy in HOLES:
    pcb = pcb.cut(cq.Workplane("XY", origin=(hx, hy, -1)).circle(HOLE_D / 2).extrude(4))
mock = pcb
drop = pcb.union(box(0, PCB_W, 0, PCB_L, PCB_T, 30))  # pcb swept upward
for x0, x1, y0, y1, z0, z1 in MOCK:
    mock = mock.union(box(x0, x1, y0, y1, z0, z1))
    drop = drop.union(box(x0, x1, y0, y1, z0, 30))    # each part swept upward

# 3) snaps: each ridge must land inside its groove with clearance to spare,
#    and the interference the lip has to flex over must stay modest
grip = SNAP_BUMP_R - LIP_CLR
print(f"snap: {grip:.2f} mm to squeeze past, "
      f"{SNAP_SOCKET_R - SNAP_BUMP_R - LIP_CLR:+.2f} mm slack when seated "
      f"({len(SNAPS)} snaps)")
if grip < 0.4:
    raise SystemExit(f"snap grip {grip:.2f} mm is softer than the reference "
                     "cases' 0.45 — it will not hold shut")
for sx, sy, axis in SNAPS:
    # seated, the dome must sit wholly inside its socket rather than riding
    # on the rim: centres are LIP_CLR apart, so this wants
    # LIP_CLR + SNAP_BUMP_R <= SNAP_SOCKET_R
    dome = snap_dome(*lip_face(sx, sy, axis), SNAP_BUMP_R).val()
    socket = snap_dome(sx, sy, SNAP_SOCKET_R).val()
    left = dome.cut(socket)
    if left.Volume() > 0.005:
        raise SystemExit(f"snap at {sx},{sy}: {left.Volume():.3f} mm^3 of the "
                         "dome misses its socket — it would hold the lid proud")

# the flat slim lid is only claimed to fit a board with no header fitted,
# so it is checked against a mock with the header removed
mock_nh = mock.cut(box(GPIO[0] - 0.05, GPIO[1] + 0.05, GPIO[2] - 0.05,
                       GPIO[3] + 0.05, PCB_T + 0.01, PCB_T + GPIO_H + 1))

# LED window: it lives in a 2.2 mm gap between two port notches and 0.95 mm
# from the lip's inner face, so a change to its size or place can nick
# either without anything else complaining
led_gaps = {
    "lip inner face": (CAV_X1 - LIP_CLR - LIP_T) - (LED[0] + LED_D / 2),
    "USB3 notch": (LED[1] - LED_D / 2) - (USB3_Y[1] + 0.7),
    "power notch": (PWR_Y[0] - 0.7) - (LED[1] + LED_D / 2),
}
print("LED window clearances: " + ", ".join(
    f"{k} {v:+.2f}" for k, v in led_gaps.items()))
for what, gap in led_gaps.items():
    if gap < 0.1:
        raise SystemExit(f"LED window is {gap:.2f} mm from the {what} — "
                         "it clips. Shrink LED_D or move LED.")

for name, a, b in (("board vs tray", mock, bottom),
                   ("board vs sealed tray", mock, bottom_s),
                   ("board vs lid", mock, lid),
                   ("board vs closed lid", mock, lid_c),
                   ("drop-in sweep vs tray", drop, bottom),
                   ("drop sweep vs sealed tray", drop, bottom_s),
                   ("lid vs tray", lid, bottom),
                   ("lid vs sealed tray", lid, bottom_s),
                   ("closed lid vs tray", lid_c, bottom),
                   ("closed lid vs sealed tray", lid_c, bottom_s),
                   ("board vs slim tray", mock, bottom_lo),
                   ("board vs slim sealed", mock, bottom_lo_s),
                   ("board vs slim lid", mock, lid_lo),
                   ("drop sweep vs slim tray", drop, bottom_lo),
                   ("slim lid vs slim tray", lid_lo, bottom_lo),
                   ("slim lid vs slim sealed", lid_lo, bottom_lo_s),
                   ("board vs slim closed lid", mock, lid_lo_cp),
                   ("slim closed vs slim tray", lid_lo_cp, bottom_lo),
                   ("slim closed vs slim sealed", lid_lo_cp, bottom_lo_s),
                   ("headerless board vs flat lid", mock_nh, lid_lo_p),
                   ("flat lid vs slim tray", lid_lo_p, bottom_lo),
                   ("flat lid vs slim sealed", lid_lo_p, bottom_lo_s)):
    inter = a.val().intersect(b.val())
    vol = inter.Volume() if inter else 0.0
    print(f"{name:24} interference {vol:8.4f} mm^3")
    if vol > 0.01:
        raise SystemExit(f"interference: {name} = {vol:.3f} mm^3")

# 4) printability. Everything here is meant to print with no supports, so
#    each part must be one connected solid — a detached island would print
#    in mid-air — and no surface may face downward more steeply than 45°
#    once the part is in its print orientation. Ceilings over an opening
#    (the microSD slot, the cable notches) are bridges, anchored on both
#    sides, and print fine; they are reported rather than failed.
def flip_z(shape):
    return shape.val().rotate(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), 180)


for name, shape, inverted in (("tray", bottom, False),
                              ("sealed tray", bottom_s, False),
                              ("lid", lid, True),
                              ("closed lid", lid_c, True),
                              ("plain closed lid", lid_cp, True),
                              ("slim tray", bottom_lo, False),
                              ("slim sealed tray", bottom_lo_s, False),
                              ("slim lid", lid_lo, True),
                              ("slim closed plain lid", lid_lo_cp, True),
                              ("slim flat lid", lid_lo_p, True),
                              ("inlay", inlay, True),
                              ("closed inlay", inlay_c, True),
                              ("slim inlay", inlay_lo, True)):
    solid = flip_z(shape) if inverted else shape.val()
    pieces = solid.Solids()
    loose = len(pieces) - (len(inlay.val().Solids()) if "inlay" in name else 1)
    if loose > 0:
        big = sorted(pieces, key=lambda s: -s.Volume())
        raise SystemExit(
            f"{name}: {len(pieces)} disconnected solids — "
            f"{', '.join(f'{s.Volume():.1f} mm^3' for s in big[:5])}. "
            "Something is floating and would print in mid-air.")
    if "inlay" in name:
        continue
    verts, tris = solid.tessellate(0.06)
    bed = solid.BoundingBox().zmin
    steep = 0.0
    for ia, ib, ic in tris:
        pa, pb, pc = verts[ia], verts[ib], verts[ic]
        n = pb.sub(pa).cross(pc.sub(pa))
        if n.Length < 1e-9:
            continue
        # skip the face lying on the bed; -0.75 leaves exact 45° chamfers
        # and the snap ribs' 45° flanks alone
        if n.z / n.Length < -0.75 and min(pa.z, pb.z, pc.z) > bed + 0.05:
            steep += n.Length / 2
    print(f"{name:18} 1 solid, {steep:6.1f} mm^2 of bridged ceiling")
    if steep > 200:
        raise SystemExit(f"{name}: {steep:.0f} mm^2 of downward faces is more "
                         "than the known bridges — check for a new overhang")

# --- export ---
out = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(out, exist_ok=True)

for suffix, t, l, i in (("", bottom, lid, inlay),
                        ("-closed", bottom, lid_c, inlay_c),
                        ("-slim", bottom_lo, lid_lo, inlay_lo)):
    assembly = (
        cq.Assembly()
        .add(t, name="bottom", color=cq.Color(0.25, 0.25, 0.28))
        .add(l, name="lid", color=cq.Color(0.85, 0.85, 0.87))
        .add(i, name="inlay", color=cq.Color(1.0, 1.0, 1.0))
    )
    assembly.export(os.path.join(out, f"cubie-a7z-case{suffix}.step"))

cq.exporters.export(bottom, os.path.join(out, "bottom.stl"))
cq.exporters.export(bottom_s, os.path.join(out, "bottom-sealed.stl"))
cq.exporters.export(bottom_lo, os.path.join(out, "bottom-slim.stl"))
cq.exporters.export(bottom_lo_s, os.path.join(out, "bottom-slim-sealed.stl"))
# flip the lids so their flat tops sit on the print bed; each inlay gets the
# same transform so it loads straight into its pockets
flip = lambda w: w.rotate((0, 0, 0), (0, 1, 0), 180)
cq.exporters.export(flip(lid), os.path.join(out, "lid.stl"))
cq.exporters.export(flip(inlay), os.path.join(out, "lid-inlay.stl"))
cq.exporters.export(flip(lid_c), os.path.join(out, "lid-closed.stl"))
cq.exporters.export(flip(inlay_c), os.path.join(out, "lid-closed-inlay.stl"))
# closed lid with no engraving at all — just the LED window
cq.exporters.export(flip(lid_cp), os.path.join(out, "lid-closed-plain.stl"))
cq.exporters.export(flip(lid_lo), os.path.join(out, "lid-slim.stl"))
cq.exporters.export(flip(lid_lo_cp),
                    os.path.join(out, "lid-slim-closed-plain.stl"))
cq.exporters.export(flip(lid_lo_p), os.path.join(out, "lid-slim-plain.stl"))
cq.exporters.export(flip(inlay_lo), os.path.join(out, "lid-slim-inlay.stl"))

print("wrote", out)
w, l = OUT_X1 - OUT_X0, OUT_Y1 - OUT_Y0
for name, top in (("open lid", STD_TOP), ("closed lid", lid_c_top),
                  ("slim", SLIM_TOP), ("slim closed", SLIM_CLOSED_TOP)):
    print(f"outer ({name:10}): {w:.1f} x {l:.1f} x {top - Z_FLOOR:.1f} mm")
