"""Regenerate the README images in images/.

Runs case.py in full (checks and all), projects the parts as line art, and
writes tightly-cropped PNGs. Rasterising uses macOS qlmanage; on another
platform swap in any SVG-to-PNG converter.

Run:  uv run render_images.py
"""

import os
import runpy
import subprocess

from PIL import Image, ImageChops

here = os.path.dirname(os.path.abspath(__file__))
imgdir = os.path.join(here, "images")
os.makedirs(imgdir, exist_ok=True)

g = runpy.run_path(os.path.join(here, "case.py"))
cq = g["cq"]

# The SVG exporter builds its 2D basis so that most isometric directions
# come out mirrored — engraved text reads backwards. This one doesn't.
ISO = (-1, -1, 0.85)
PAD = 18          # px of white left around the geometry
TARGET_W = 1200   # px, downsampled for a clean line weight
TARGET_H = 900


def group(*parts):
    """One compound so a scene projects as a single drawing."""
    return cq.Compound.makeCompound(
        [p if isinstance(p, cq.Shape) else p.val() for p in parts])


bottom, bottom_s = g["bottom"], g["bottom_s"]
lid, lid_c, lid_cp = g["lid"], g["lid_c"], g["lid_cp"]
bottom_lo, lid_lo, lid_lo_cp = g["bottom_lo"], g["lid_lo"], g["lid_lo_cp"]

# Parts are drawn one per image rather than lined up in a shared scene: the
# projection turns an x-offset into a diagonal one, so laid-out parts drift
# apart and waste half the frame. Separate images crop tight and sit in a
# table in the README.
# (shape, projection, degrees to turn the finished image, counter-clockwise).
# The exporter picks its own up-vector per projection direction and lands
# straight-on elevations on their side — and not consistently the same
# side, hence the opposite turns for the two below. Check a new elevation
# against a known landmark (the tray/lid seam sits 1.6 mm below the top)
# rather than assuming.
scenes = {
    "case-open": (group(bottom, lid), ISO, 0),
    "case-closed": (group(bottom, lid_c), ISO, 0),
    "board-in-tray": (group(bottom, g["mock"]), ISO, 0),
    "tray-full": (bottom, ISO, 0),
    "tray-sealed": (bottom_s, ISO, 0),
    "tray-slim": (bottom_lo, ISO, 0),
    "lid-open": (lid, ISO, 0),
    "lid-closed": (lid_c, ISO, 0),
    "lid-plain": (lid_cp, ISO, 0),
    "lid-slim": (lid_lo, ISO, 0),
    "lid-slim-closed": (lid_lo_cp, ISO, 0),
    "lid-slim-plain": (g["lid_lo_p"], ISO, 0),
    "case-slim": (group(bottom_lo, lid_lo), ISO, 0),
    "ports-slim": (group(bottom_lo, lid_lo), (1, 0.001, 0.001), 90),
    "lid-top": (lid, (0, 0, 1), 0),
    "ports": (group(bottom, lid), (1, 0.001, 0.001), 90),
    "sd-end": (group(bottom, lid), (0.001, 1, 0.001), 90),
    "cable-end": (group(bottom, lid), (0.001, -1, 0.001), -90),
    "underside": (bottom, (0.001, 0.001, -1), 0),
}

def render(shape, dirn, svg, canvas_w, canvas_h):
    cq.exporters.export(shape, svg, opt={
        "projectionDir": dirn, "width": canvas_w, "height": canvas_h,
        "marginLeft": 60, "marginTop": 60,
        "showAxes": False, "showHidden": False, "strokeWidth": 0.3,
    })
    subprocess.run(["qlmanage", "-t", "-s", str(max(canvas_w, canvas_h)),
                    "-o", imgdir, svg], check=True, capture_output=True)
    im = Image.open(svg + ".png").convert("RGB")
    bbox = ImageChops.difference(
        im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    os.remove(svg + ".png")
    os.remove(svg)
    return im, bbox


for name, (shape, dirn, turn) in scenes.items():
    svg = os.path.join(imgdir, name + ".svg")
    # The exporter scales the drawing to fit the canvas *height* and lets a
    # wide part run off the sides, so widen and retry until the ink stops
    # touching the frame.
    canvas_w, canvas_h = 3000, 2400
    for _ in range(5):
        im, bbox = render(shape, dirn, svg, canvas_w, canvas_h)
        l, t, r, b = bbox
        if l > 1 and t > 1 and r < im.width - 1 and b < im.height - 1:
            break
        canvas_w = round(canvas_w * 1.6)

    im = im.crop((max(l - PAD, 0), max(t - PAD, 0),
                  min(r + PAD, im.width), min(b + PAD, im.height)))
    if turn:
        im = im.rotate(turn, expand=True, fillcolor=(255, 255, 255))
    scale = min(TARGET_W / im.width, TARGET_H / im.height, 1.0)
    if scale < 1.0:
        im = im.resize((round(im.width * scale), round(im.height * scale)),
                       Image.LANCZOS)
    im.save(os.path.join(imgdir, name + ".png"), optimize=True)
    print(f"{name}  {im.width}x{im.height}")
