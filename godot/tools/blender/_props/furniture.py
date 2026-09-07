"""Furniture with silhouettes — DETAIL DRAFT 2 kit (2026-09-05).

Every chair in the project was a seat box on four stick cylinders;
every table a slab on posts. These read as furniture at a glance:
turned legs (lathed), aprons and stretchers, a chair back with
spindles, a chamfered seat, a lamp with a shade, a stool with a
footring. All parts share the prefix so the overlap gate treats
each piece as one assembly.

    make_chair(prefix, x, y, yaw=0.0, wood=..., seat_col=None)
    make_table(prefix, x, y, w=1.2, d=0.8, h=0.75, wood=...)
    make_stool(prefix, x, y, h=0.70, wood=...)
    make_lamp(prefix, x, y, base_z=0.0, h=0.55, shade_col=...)
    make_bench(prefix, x, y, length=1.6, yaw=0.0, wood=...)
    make_bed(prefix, x, y, head="+Y", w=1.4, d=2.0, style="frame", ...)
"""
import math
from .geometry import make_box, make_cyl, make_chamfer_box, make_lathe, make_rot_box, make_tube

WOOD = (0.50, 0.40, 0.28, 1.0)
WOOD_DK = (0.40, 0.31, 0.22, 1.0)
BRASS = (0.72, 0.60, 0.32, 1.0)


def _leg(name, x, y, z0, h, r=0.025, wood=WOOD):
    """A turned leg: foot, a swell, a neck, the block under the seat."""
    make_lathe(name, (x, y, z0), [(r * 0.8, 0.0), (r * 1.15, 0.05), (r * 0.7, 0.10), (r, 0.30 * h), (r * 1.25, 0.42 * h),
                                  (r * 0.85, 0.58 * h), (r * 0.85, 0.90 * h), (r * 1.1, 0.94 * h), (r * 1.1, h)], wood, segments=8)


def make_chair(prefix, x, y, yaw=0.0, wood=WOOD, seat_col=None, seat_h=0.45, w=0.42, z0=0.0):
    seat_col = seat_col or wood
    c, s = math.cos(yaw), math.sin(yaw)
    def P(u, v, z):
        return (x + u * c - v * s, y + u * s + v * c, z0 + z)
    hw = w / 2.0
    for li, (u, v) in enumerate(((-hw + 0.03, -hw + 0.03), (hw - 0.03, -hw + 0.03), (-hw + 0.03, hw - 0.03), (hw - 0.03, hw - 0.03))):
        _leg(f"{prefix}_Leg_{li}", *P(u, v, 0.0)[:2], z0, seat_h - 0.04, wood=wood)
    # stretchers between the legs
    for si, (a, b) in enumerate((((-hw + 0.03, -hw + 0.03), (hw - 0.03, -hw + 0.03)), ((-hw + 0.03, hw - 0.03), (hw - 0.03, hw - 0.03)),
                                 ((-hw + 0.03, -hw + 0.03), (-hw + 0.03, hw - 0.03)), ((hw - 0.03, -hw + 0.03), (hw - 0.03, hw - 0.03)))):
        make_tube(f"{prefix}_Stretcher_{si}", [P(a[0], a[1], 0.18), P(b[0], b[1], 0.18)], 0.012, wood, segments=5)
    make_chamfer_box(f"{prefix}_Seat", P(0.0, 0.0, seat_h - 0.02), (w, w, 0.04), seat_col, chamfer=0.012, yaw=yaw)
    # the back: two posts, a top rail, spindles
    for sgn in (-1, 1):
        make_rot_box(f"{prefix}_Back_Post_{sgn:+d}", P(sgn * (hw - 0.03), -hw + 0.03, seat_h + 0.22), (0.035, 0.035, 0.48), wood, yaw=yaw, roll=-0.10)
    make_rot_box(f"{prefix}_Back_Rail", P(0.0, -hw + 0.03 - 0.05, seat_h + 0.44), (w, 0.03, 0.07), wood, yaw=yaw, roll=-0.10)
    for si, u in enumerate((-0.12, -0.04, 0.04, 0.12)):
        make_rot_box(f"{prefix}_Spindle_{si}", P(u, -hw + 0.03 - 0.03, seat_h + 0.21), (0.016, 0.016, 0.38), wood, yaw=yaw, roll=-0.10)


def make_table(prefix, x, y, w=1.2, d=0.8, h=0.75, wood=WOOD, top_col=None, z0=0.0):
    top_col = top_col or wood
    x, y, h0 = x, y, h
    h = z0 + h
    make_chamfer_box(f"{prefix}_Top", (x, y, h - 0.02), (w, d, 0.04), top_col, chamfer=0.01)
    make_box(f"{prefix}_Apron_F", (x, y - d / 2.0 + 0.06, h - 0.09), (w - 0.16, 0.025, 0.10), WOOD_DK)
    make_box(f"{prefix}_Apron_B", (x, y + d / 2.0 - 0.06, h - 0.09), (w - 0.16, 0.025, 0.10), WOOD_DK)
    make_box(f"{prefix}_Apron_L", (x - w / 2.0 + 0.06, y, h - 0.09), (0.025, d - 0.16, 0.10), WOOD_DK)
    make_box(f"{prefix}_Apron_R", (x + w / 2.0 - 0.06, y, h - 0.09), (0.025, d - 0.16, 0.10), WOOD_DK)
    for li, (u, v) in enumerate(((-w / 2.0 + 0.06, -d / 2.0 + 0.06), (w / 2.0 - 0.06, -d / 2.0 + 0.06), (-w / 2.0 + 0.06, d / 2.0 - 0.06), (w / 2.0 - 0.06, d / 2.0 - 0.06))):
        _leg(f"{prefix}_Leg_{li}", x + u, y + v, z0, h0 - 0.14, r=0.032, wood=wood)
    make_tube(f"{prefix}_Stretcher", [(x - w / 2.0 + 0.06, y, z0 + 0.16), (x + w / 2.0 - 0.06, y, z0 + 0.16)], 0.014, wood, segments=5)


def make_stool(prefix, x, y, h=0.70, wood=WOOD):
    make_lathe(f"{prefix}_Seat", (x, y, h - 0.04), [(0.0, 0.0), (0.17, 0.0), (0.18, 0.02), (0.16, 0.04), (0.0, 0.045)], wood, segments=12)
    for li in range(3):
        a = li * 2.0 * math.pi / 3.0 + 0.5
        _leg(f"{prefix}_Leg_{li}", x + 0.13 * math.cos(a), y + 0.13 * math.sin(a), 0.0, h - 0.045, r=0.02, wood=wood)
    make_lathe(f"{prefix}_Footring", (x, y, 0.22), [(0.15, 0.0), (0.16, 0.01), (0.15, 0.02)], WOOD_DK, segments=12, loop=True)


def make_lamp(prefix, x, y, base_z=0.0, h=0.55, shade_col=(0.92, 0.86, 0.68, 1.0), body_col=BRASS):
    make_lathe(f"{prefix}_Base", (x, y, base_z), [(0.0, 0.0), (0.09, 0.0), (0.08, 0.02), (0.05, 0.03), (0.03, 0.05), (0.014, 0.06), (0.014, h * 0.55),
                                                  (0.025, h * 0.58), (0.014, h * 0.61), (0.014, h * 0.72), (0.0, h * 0.72)], body_col, segments=10)
    make_lathe(f"{prefix}_Shade", (x, y, base_z + h * 0.62), [(0.11, 0.0), (0.16, h * 0.30), (0.0, h * 0.30)], shade_col, segments=12)
    make_lathe(f"{prefix}_Bulb", (x, y, base_z + h * 0.72), [(0.0, 0.0), (0.025, 0.01), (0.03, 0.04), (0.0, 0.07)], (0.98, 0.94, 0.80, 1.0), segments=8)


def make_bench(prefix, x, y, length=1.6, yaw=0.0, wood=WOOD, h=0.45):
    c, s = math.cos(yaw), math.sin(yaw)
    def P(u, v, z):
        return (x + u * c - v * s, y + u * s + v * c, z)
    make_chamfer_box(f"{prefix}_Seat", P(0.0, 0.0, h - 0.025), (length, 0.36, 0.05), wood, chamfer=0.012, yaw=yaw)
    for sgn in (-1, 1):
        make_rot_box(f"{prefix}_Leg_{sgn:+d}", P(sgn * (length / 2.0 - 0.18), 0.0, (h - 0.05) / 2.0), (0.06, 0.30, h - 0.05), WOOD_DK, yaw=yaw)
    make_rot_box(f"{prefix}_Stretcher", P(0.0, 0.0, 0.14), (length - 0.42, 0.05, 0.06), WOOD_DK, yaw=yaw)


# ════════════════════════════════════════════════════════════════
# BEDS (2026-09-07 · "lots of clipping on beds and weird pillow
# designs"). Twenty-four builders each hand-stacked a bed from boxes
# and most of them interpenetrate: pillows through comforters,
# comforters through mattresses, headboards through pillows. One
# builder, every layer resting ON the one below it.
#
#   make_bed(prefix, x, y, head="+Y", w=1.4, d=2.0, style="frame",
#            frame_col, mattress_col, sheet_col, blanket_col,
#            pillow_col, pillows=2, made=True, headboard=True, z0=0.0)
#
#   head    which way the headboard lies from the bed centre:
#           "+Y" / "-Y" / "+X" / "-X" (the pillows sit at that end).
#   style   "frame"    wooden frame on four legs, mattress in it
#           "platform" low box platform, mattress on top
#           "captain"  raised base with a row of drawers on the +side
#           "futon"    pallet on the floor, thin mattress, no headboard
#           "hospital" steel frame, thin mattress, side rails, one pillow
#   made    True: fitted sheet + blanket folded from the foot to ~60 %
#           of the length with a rolled top edge; False: sheet only,
#           blanket heaped at the foot.
# Every part shares `prefix`; the mattress is inset inside the frame,
# the sheet is a 1 cm skin on the mattress, the blanket drapes 4 cm
# over the sides, the pillows sit on the sheet. Nothing penetrates.
# Returns the height of the made surface (for a book, a phone, a cat).
# ════════════════════════════════════════════════════════════════

_BED_STYLES = ("frame", "platform", "captain", "futon", "hospital")


def make_bed(prefix, x, y, head="+Y", w=1.4, d=2.0, style="frame",
             frame_col=WOOD, mattress_col=(0.90, 0.89, 0.85, 1.0), sheet_col=(0.93, 0.92, 0.88, 1.0),
             blanket_col=(0.38, 0.44, 0.54, 1.0), pillow_col=(0.94, 0.93, 0.90, 1.0),
             pillows=2, made=True, headboard=True, z0=0.0):
    assert style in _BED_STYLES, style
    # local frame: u across the bed (width), v along the bed toward the HEAD
    yaw = {"+Y": 0.0, "-Y": math.pi, "+X": -math.pi / 2.0, "-X": math.pi / 2.0}[head]
    c, s = math.cos(yaw), math.sin(yaw)
    along_x = abs(s) > 0.5          # the bed's length runs along world X
    def P(u, v, z):
        return (x + u * c - v * s, y + u * s + v * c, z0 + z)
    def S(a, b, h):
        return (b, a, h) if along_x else (a, b, h)
    ax_across = "Y" if along_x else "X"     # cylinder axis ACROSS the bed
    ax_along = "X" if along_x else "Y"
    hw, hd = w / 2.0, d / 2.0

    # ── the frame and the deck the mattress rests on
    if style == "frame":
        deck = 0.34
        for li, (u, v) in enumerate(((-hw + 0.04, -hd + 0.04), (hw - 0.04, -hd + 0.04), (-hw + 0.04, hd - 0.04), (hw - 0.04, hd - 0.04))):
            make_box(f"{prefix}_Leg_{li}", P(u, v, deck / 2.0), (0.07, 0.07, deck), frame_col)
        make_box(f"{prefix}_Rail_-1", P(-hw + 0.035, 0.0, deck - 0.09), S(0.05, d - 0.16, 0.18), frame_col)
        make_box(f"{prefix}_Rail_+1", P(hw - 0.035, 0.0, deck - 0.09), S(0.05, d - 0.16, 0.18), frame_col)
        make_box(f"{prefix}_Rail_Foot", P(0.0, -hd + 0.035, deck - 0.09), S(w - 0.16, 0.05, 0.18), frame_col)
        make_box(f"{prefix}_Deck", P(0.0, 0.0, deck - 0.015), S(w - 0.10, d - 0.10, 0.03), frame_col)
        mat_h, mat_w, mat_d = 0.20, w - 0.14, d - 0.14
    elif style == "platform":
        deck = 0.28
        make_chamfer_box(f"{prefix}_Platform", P(0.0, 0.0, deck / 2.0), S(w, d, deck), frame_col)
        mat_h, mat_w, mat_d = 0.20, w - 0.10, d - 0.10
    elif style == "captain":
        deck = 0.48
        make_box(f"{prefix}_Base", P(0.0, 0.0, deck / 2.0), S(w, d, deck), frame_col)
        n_dr = max(2, int(d // 0.62))
        pitch = (d - 0.20) / n_dr
        dr_col = (frame_col[0] * 0.85, frame_col[1] * 0.85, frame_col[2] * 0.85, 1.0)
        for di in range(n_dr):
            v = -hd + 0.10 + pitch * (di + 0.5)
            make_box(f"{prefix}_Drawer_{di}", P(hw + 0.006, v, deck * 0.5), S(0.012, pitch - 0.08, deck - 0.14), dr_col)
            make_cyl(f"{prefix}_DrawerPull_{di}", P(hw + 0.03, v, deck * 0.5), 0.025, 0.035, (0.70, 0.70, 0.72, 1.0), axis=ax_across, segments=6)
        mat_h, mat_w, mat_d = 0.18, w - 0.12, d - 0.12
    elif style == "futon":
        deck = 0.10
        make_box(f"{prefix}_Pallet", P(0.0, 0.0, deck / 2.0), S(w, d, deck), frame_col)
        mat_h, mat_w, mat_d = 0.14, w - 0.08, d - 0.08
        headboard = False
    else:  # hospital
        deck = 0.52
        steel = (0.72, 0.74, 0.76, 1.0)
        for li, (u, v) in enumerate(((-hw + 0.06, -hd + 0.10), (hw - 0.06, -hd + 0.10), (-hw + 0.06, hd - 0.10), (hw - 0.06, hd - 0.10))):
            make_cyl(f"{prefix}_Post_{li}", P(u, v, 0.07 + (deck - 0.07) / 2.0), 0.02, deck - 0.07, steel, segments=6)
            make_cyl(f"{prefix}_Caster_{li}", P(u, v, 0.05), 0.05, 0.04, (0.14, 0.14, 0.15, 1.0), axis=ax_across, segments=8)
        make_box(f"{prefix}_Deck", P(0.0, 0.0, deck - 0.02), S(w - 0.06, d - 0.10, 0.04), steel)
        for sgn in (-1, 1):
            make_cyl(f"{prefix}_SideRail_{sgn:+d}", P(sgn * (hw + 0.02), 0.10, deck + 0.34), 0.015, d * 0.55, steel, axis=ax_along, segments=6)
            for k in range(3):
                make_cyl(f"{prefix}_RailPost_{sgn:+d}_{k}", P(sgn * (hw + 0.02), 0.10 + (k - 1) * d * 0.22, deck + 0.17), 0.012, 0.34, steel, segments=5)
        mat_h, mat_w, mat_d = 0.14, w - 0.10, d - 0.16
        pillows = 1
        made = False
        headboard = False

    # ── mattress ON the deck, a sheet skin ON the mattress
    make_chamfer_box(f"{prefix}_Mattress", P(0.0, 0.0, deck + mat_h / 2.0), S(mat_w, mat_d, mat_h), mattress_col, chamfer=0.03)
    top = deck + mat_h
    make_box(f"{prefix}_Sheet", P(0.0, 0.0, top + 0.005), S(mat_w - 0.02, mat_d - 0.02, 0.01), sheet_col)
    top += 0.01

    # ── pillows at the head, ON the sheet, a touch of yaw each
    pw, pd, ph = min(0.66, mat_w * 0.46), 0.42, 0.11
    if pillows > 0:
        if pillows == 1:
            us = [0.0]
        else:
            span = mat_w / 2.0 - pw / 2.0 - 0.04
            us = [(-1 + 2 * i / (pillows - 1)) * span for i in range(pillows)]
        for pi, u in enumerate(us):
            make_chamfer_box(f"{prefix}_Pillow_{pi}", P(u, hd - 0.07 - pd / 2.0 - 0.06, top + ph / 2.0), S(pw, pd, ph), pillow_col,
                             chamfer=0.03, yaw=yaw + (0.06 if pi % 2 else -0.05))

    # ── blanket: made = folded from the foot to 60 %, a rolled edge; else heaped
    if made:
        bl_len = mat_d * 0.60
        make_chamfer_box(f"{prefix}_Blanket", P(0.0, -hd + 0.07 + bl_len / 2.0 + 0.02, top + 0.02), S(mat_w + 0.08, bl_len, 0.04), blanket_col, chamfer=0.012)
        make_cyl(f"{prefix}_Blanket_Roll", P(0.0, -hd + 0.07 + bl_len + 0.05, top + 0.06), 0.035, mat_w + 0.06, blanket_col, axis=ax_across, segments=8)
    elif style == "hospital":
        # a flat institutional blanket, tucked, over the lower two thirds
        make_box(f"{prefix}_Blanket", P(0.0, -hd + 0.10 + mat_d * 0.33, top + 0.015), S(mat_w + 0.02, mat_d * 0.66, 0.03), blanket_col)
    else:
        make_chamfer_box(f"{prefix}_Blanket_Heap", P(0.10, -hd + 0.45, top + 0.07), S(mat_w * 0.8, 0.62, 0.14), blanket_col, chamfer=0.04, yaw=yaw + 0.12)

    # ── headboard against the head end
    if headboard and style in ("frame", "platform", "captain"):
        hb_h = 0.70 if style != "captain" else 0.60
        make_box(f"{prefix}_Headboard", P(0.0, hd + 0.03, deck + hb_h / 2.0 - 0.06), S(w + 0.04, 0.06, hb_h), frame_col)
    return top
