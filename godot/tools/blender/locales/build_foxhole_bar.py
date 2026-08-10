"""foxhole_bar — the bar side of the Foxhole music venue (sibling of
foxhole_stage). Long bar counter + back-bar bottle shelves + taps +
stools; neon beer signs; a couple of high-tops; band flyers. Moody
warm venue lighting with a saturated neon accent (see .tscn).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling
from _props.decor import make_faded_poster
from _props.safety import make_smoke_detector
from _props.objects import make_liquor_bottle

ROOM_W = 8.0; ROOM_D = 6.0; CEIL = 3.0
PAL_WALL = {"wall":(0.36,0.26,0.20,1.0),"baseboard":(0.20,0.14,0.10,1.0)}
COL_FLOOR = (0.28,0.20,0.14,1.0); COL_SEAM = (0.16,0.10,0.08,1.0)
COL_BAR = (0.34,0.22,0.14,1.0); COL_BAR_TOP = (0.20,0.13,0.09,1.0)
COL_BRASS = (0.82,0.62,0.28,1.0); COL_STEEL = P.METAL_STEEL; COL_BLACK = P.METAL_BLACK
COL_LEATHER = (0.30,0.16,0.12,1.0); COL_WOOD = (0.42,0.30,0.18,1.0)
COL_BOTTLE_AMBER = (0.78,0.42,0.16,1.0); COL_BOTTLE_GREEN = (0.24,0.42,0.22,1.0)
COL_BOTTLE_CLEAR = (0.74,0.82,0.84,0.55)
COL_NEON_MAGENTA = (0.98,0.24,0.72,1.0); COL_NEON_CYAN = (0.30,0.82,0.96,1.0)
COL_NEON_AMBER = (0.98,0.72,0.28,1.0)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)

def build_bar():
    # Bar counter along the north wall — EAST side only. At 6m
    # centered on x=0 it ran straight into the stage zone (the
    # stage's front rail post and the deck itself stood inside the
    # bar body).
    top_z = 1.14
    make_box("Bar_Front", (0.7, 5.0, 0.55), (4.6, 0.60, 1.10), COL_BAR)
    make_box("Bar_Top",   (0.7, 4.94, top_z), (4.8, 0.80, 0.06), COL_BAR_TOP)
    make_box("Bar_Kick",  (0.7, 4.70, 0.10), (4.6, 0.05, 0.20), COL_BLACK)
    # Brass foot rail along the customer (south) side.
    make_cyl("Bar_FootRail", (0.7, 4.62, 0.16), 0.03, 4.6, COL_BRASS, axis='X', segments=8)
    for si, sx in enumerate([-0.8, 0.7, 2.2]):
        make_cyl(f"Bar_RailPost_{si}", (sx, 4.62, 0.08), 0.02, 0.16, COL_STEEL)
    # Back-bar bottle shelves against the north wall.
    for shf in range(3):
        sz = 1.30 + shf * 0.40
        make_box(f"BackBar_Shelf_{shf}", (0.7, 5.78, sz), (4.2, 0.24, 0.03), COL_WOOD)
        for bi in range(14):
            bx = -1.25 + bi * 0.30
            tint = [COL_BOTTLE_AMBER, COL_BOTTLE_CLEAR, COL_BOTTLE_GREEN][(shf + bi) % 3]
            make_liquor_bottle(f"BackBar_Bottle_{shf}_{bi}", bx, 5.85,
                               sz + 0.02, tint,
                               h=0.23 + ((shf + bi) % 3) * 0.03, r=0.031)
    # Long back mirror behind the bottles.
    make_box("BackBar_Mirror", (0.7, 5.87, 2.05), (4.2, 0.02, 1.50), (0.30, 0.32, 0.36, 0.85))
    # Draft-beer tap tower on the bar top.
    _make_tap_tower("Taps", -0.9, 5.05, top_z)

def _make_tap_tower(prefix, cx, cy, top_z):
    make_cyl(f"{prefix}_Base",   (cx, cy, top_z + 0.03), 0.06, 0.06, COL_STEEL, segments=12)
    make_cyl(f"{prefix}_Column", (cx, cy, top_z + 0.24), 0.045, 0.38, COL_STEEL, segments=12)
    for ti in range(4):
        hx = cx - 0.18 + ti * 0.12
        make_box(f"{prefix}_Handle_{ti}", (hx, cy - 0.12, top_z + 0.20), (0.03, 0.10, 0.14),
                 [COL_NEON_AMBER, (0.86,0.24,0.20,1.0), (0.24,0.42,0.68,1.0), (0.30,0.52,0.30,1.0)][ti])
        make_cyl(f"{prefix}_Spout_{ti}", (hx, cy - 0.16, top_z + 0.06), 0.012, 0.08, COL_STEEL)

def _make_bar_stool(prefix, cx, cy, seat_r=0.19):
    make_cyl(f"{prefix}_Seat",   (cx, cy, 0.78), seat_r, 0.06, COL_LEATHER, segments=12)
    make_cyl(f"{prefix}_Pillar", (cx, cy, 0.40), 0.035, 0.72, COL_STEEL)
    make_cyl(f"{prefix}_FootRing",(cx, cy, 0.22), seat_r*0.9, 0.02, COL_STEEL, segments=12)
    make_cyl(f"{prefix}_Base",   (cx, cy, 0.03), seat_r, 0.04, COL_BLACK, segments=12)

def build_stools():
    # Recentered on the shortened bar — the westmost stool used to
    # stand on the stage deck.
    for si, sx in enumerate([-1.3, -0.3, 0.7, 1.7, 2.7]):
        _make_bar_stool(f"Stool_{si}", sx, 4.1)

def _make_high_top(prefix, tx, ty):
    make_cyl(f"{prefix}_Top",      (tx, ty, 1.06), 0.40, 0.05, COL_BAR, segments=16)
    make_cyl(f"{prefix}_Pedestal", (tx, ty, 0.54), 0.05, 1.00, COL_STEEL)
    make_cyl(f"{prefix}_Foot",     (tx, ty, 0.04), 0.30, 0.05, COL_BLACK, segments=12)
    for ci, (ox, oy) in enumerate([(-0.55, 0.0), (0.55, 0.0)]):
        _make_bar_stool(f"{prefix}_Stool_{ci}", tx + ox, ty + oy)

def build_high_tops():
    _make_high_top("HighTop_0", 0.3, 1.9)
    _make_high_top("HighTop_1", 2.3, 2.2)

def _make_neon_sign(prefix, cx, cz, w, h, col):
    y = 5.855
    make_box(f"{prefix}_Top",   (cx, y, cz + h/2.0), (w, 0.03, 0.05), col)
    make_box(f"{prefix}_Bottom",(cx, y, cz - h/2.0), (w, 0.03, 0.05), col)
    make_box(f"{prefix}_Left",  (cx - w/2.0, y, cz), (0.05, 0.03, h), col)
    make_box(f"{prefix}_Right", (cx + w/2.0, y, cz), (0.05, 0.03, h), col)
    make_box(f"{prefix}_TubeA", (cx, y, cz + h*0.12), (w*0.7, 0.02, 0.04), col)
    make_box(f"{prefix}_TubeB", (cx, y, cz - h*0.14), (w*0.5, 0.02, 0.04), col)

def build_neon_signs():
    _make_neon_sign("Neon_Magenta", -2.1, 2.60, 1.30, 0.60, COL_NEON_MAGENTA)
    _make_neon_sign("Neon_Cyan",     2.1, 2.72, 1.10, 0.55, COL_NEON_CYAN)
    _make_neon_sign("Neon_Amber",    0.0, 2.66, 0.90, 0.45, COL_NEON_AMBER)

def build_pendants():
    # Warm hanging pendant lamps over the bar (motivate the .tscn practicals).
    for pi, px in enumerate([-1.5, 1.5]):
        make_cyl(f"Pendant_{pi}_Cord", (px, 5.0, CEIL - 0.30), 0.006, 0.40, COL_BLACK)
        make_cyl(f"Pendant_{pi}_Shade", (px, 5.0, CEIL - 0.62), 0.16, 0.18, (0.28,0.20,0.14,1.0), segments=12)
        make_cyl(f"Pendant_{pi}_Bulb", (px, 5.0, CEIL - 0.70), 0.05, 0.06, (0.98,0.86,0.60,1.0))

def build_flyers():
    # Band flyers taped to the west wall.
    flyer_inks = [(0.86,0.24,0.20,1.0), (0.24,0.42,0.68,1.0), (0.86,0.72,0.24,1.0)]
    for pi in range(3):
        make_faded_poster(f"Flyer_W_{pi}", (-ROOM_W/2.0 + 0.05, 1.2 + pi * 1.6, 1.70),
                          palette={"body": (0.82,0.78,0.70,1.0), "ink": flyer_inks[pi]})
    # A couple more taped to the wall by the door.
    make_faded_poster("Flyer_S", (-(ROOM_W/4.0+0.5), 0.05, 1.60),
                      palette={"body": (0.80,0.76,0.68,1.0), "ink": (0.30,0.52,0.30,1.0)})

def build_ceiling_infra():
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))

def build_venue_side():
    """2026-08-03 hero-prop pass: vol6_ch20 plays the WHOLE venue on
    this preset — it needs the stage side. Stage along the W wall
    with truss towers + six LEDs, front rail, FOH board + the
    Topo Chico cooler, DJ booth, work light, PA."""
    deckcol = (0.20, 0.16, 0.14, 1.0)
    truss = (0.40, 0.42, 0.46, 1.0)
    # Stage deck + lip along the W wall
    make_box("Stage_Deck", (-3.15, 3.0, 0.15), (1.7, 5.0, 0.30), deckcol)
    make_box("Stage_Lip", (-2.28, 3.0, 0.16), (0.06, 5.0, 0.32), (0.28, 0.22, 0.18, 1.0))
    # Two truss towers with three LED fixtures each — standing ON
    # the deck (they used to straddle the deck edge and pass through
    # its body).
    for ti, ty in enumerate((1.9, 4.1)):
        make_box(f"Truss_{ti}", (-2.7, ty, 1.45), (0.25, 0.25, 2.30), truss)
        for li, lz in enumerate((1.2, 1.8, 2.4)):
            make_box(f"Truss_{ti}_LED_{li}", (-2.55, ty, lz), (0.14, 0.16, 0.12),
                     [(0.72, 0.26, 0.60, 1.0), (0.26, 0.55, 0.80, 1.0), (0.86, 0.62, 0.22, 1.0)][li])
    # Front-of-stage rail (Carl's spot)
    for py in (1.0, 2.3, 3.7, 5.0):
        make_box(f"Rail_Post_{py:.1f}", (-2.02, py, 0.52), (0.06, 0.06, 1.05), truss)
    make_cyl("Stage_Rail", (-2.02, 3.0, 1.05), 0.035, 4.4, truss, segments=8, axis='Y')
    # FOH board + the cooler under it (Ricky's Topo Chico)
    make_box("FOH_Desk", (2.9, 2.0, 0.92), (0.7, 1.4, 0.06), (0.24, 0.22, 0.20, 1.0))
    make_box("FOH_Console", (2.82, 2.0, 1.02), (0.40, 1.20, 0.12), (0.14, 0.14, 0.16, 1.0))
    for lx in (2.62, 3.18):
        make_box(f"FOH_Leg_{lx:.2f}", (lx, 2.0, 0.45), (0.06, 1.3, 0.90), (0.20, 0.19, 0.20, 1.0))
    make_box("FOH_Cooler", (2.9, 2.0, 0.24), (0.45, 0.60, 0.44), (0.72, 0.20, 0.18, 1.0))
    # DJ booth beside the stage + laptop — east of the lip, clear of
    # PA_0 (they used to occupy the same corner, booth 0.55m inside
    # the sub).
    make_box("DJ_Booth", (-1.7, 0.48, 0.55), (1.1, 0.6, 1.10), (0.18, 0.17, 0.19, 1.0))
    make_box("DJ_Laptop_Base", (-1.7, 0.48, 1.12), (0.30, 0.22, 0.02), (0.55, 0.57, 0.58, 1.0))
    make_box("DJ_Laptop_Screen", (-1.7, 0.59, 1.24), (0.30, 0.02, 0.20), (0.16, 0.20, 0.26, 1.0))
    # The one work light at the back
    make_cyl("Work_Light_Stand", (3.4, 5.3, 0.90), 0.03, 1.80, truss, segments=6)
    make_cyl("Work_Light_Head", (3.35, 5.25, 1.85), 0.10, 0.14, (0.96, 0.88, 0.66, 1.0), segments=8)
    # PA flanking the stage — fully on the deck, stacked on its
    # surface (z base 0.30), not embedded through it.
    for si, sy in enumerate((0.9, 5.1)):
        make_box(f"PA_{si}_Sub", (-2.9, sy, 0.65), (0.60, 0.60, 0.70), (0.12, 0.11, 0.10, 1.0))
        make_box(f"PA_{si}_Top", (-2.9, sy, 1.60), (0.52, 0.52, 1.10), (0.14, 0.12, 0.11, 1.0))


def main():
    clear_scene()
    build_shell()
    build_bar()
    build_stools()
    build_high_tops()
    build_neon_signs()
    build_pendants()
    build_flyers()
    build_ceiling_infra()
    build_venue_side()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/foxhole_bar.glb"))
    print(f"\n[build_foxhole_bar] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
