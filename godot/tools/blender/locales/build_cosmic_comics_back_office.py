"""Cosmic Comics — back office — vol6 placement script."""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_chamfer_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots, make_donut_display
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture, make_ceiling_speaker

ROOM_W = 4.0; ROOM_D = 5.0; CEIL = 2.6
PAL_WALL = {"wall": (0.78, 0.70, 0.58, 1.0), "baseboard": (0.42, 0.32, 0.22, 1.0)}
COL_FLOOR = (0.62, 0.52, 0.42, 1.0); COL_SEAM = (0.32, 0.22, 0.14, 1.0); COL_WOOD = (0.42, 0.30, 0.20, 1.0)
COL_ACCENT = (0.78, 0.42, 0.22, 1.0)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})

def build_desk():
    dx, dy = 0.0, ROOM_D-1.5
    make_box("Desk_Top", (dx, dy, 0.74), (1.80, 0.80, 0.04), COL_WOOD)
    for li in range(4):
        lx, ly = dx+(-0.84,+0.84,-0.84,+0.84)[li], dy+(-0.34,-0.34,+0.34,+0.34)[li]
        make_box(f"Desk_Leg_{li}", (lx, ly, 0.36), (0.04, 0.04, 0.72), COL_WOOD)
    # Papers stacked
    for pi in range(3):
        make_box(f"Papers_{pi}", (dx-0.30+pi*0.18, dy, 0.78+pi*0.02), (0.20, 0.26, 0.03), P.PAPER)
    # Monitor + keyboard
    make_box("Monitor", (dx, dy+0.20, 1.05), (0.50, 0.04, 0.30), (0.06, 0.08, 0.10, 1.0))
    make_box("Keyboard", (dx, dy-0.10, 0.76), (0.42, 0.16, 0.02), (0.32, 0.30, 0.32, 1.0))

def build_filing():
    for ci in range(2):
        cx = -ROOM_W/2.0+0.30+ci*0.50
        make_chamfer_box(f"Filing_{ci}", (cx, 1.0, 0.65), (0.50, 0.60, 1.30), (0.62, 0.62, 0.58, 1.0))
        for di in range(4):
            make_box(f"Filing_{ci}_Drawer_{di}", (cx, 0.70, 1.20-di*0.30), (0.46, 0.04, 0.26), (0.78, 0.78, 0.74, 1.0))

def build_cal():
    make_calendar("Calendar", (+ROOM_W/2.0-0.05, ROOM_D/2.0, 1.70))

def build_bulb():
    # "lit by a single overhead with a pull chain" — the bulb is the
    # room's only light (fluorescents removed, hero-prop pass)
    make_cyl("Bulb_Cord", (0.0, ROOM_D/2.0, CEIL-0.30), 0.005, 0.60, P.METAL_BLACK)
    make_cyl("Bulb_Glass", (0.0, ROOM_D/2.0, CEIL-0.86), 0.06, 0.14, (0.96, 0.86, 0.46, 1.0))
    make_box("Bulb_PullChain", (0.06, ROOM_D/2.0, CEIL-0.98), (0.008, 0.008, 0.22), P.METAL_BLACK)

def build_ceiling_infra():
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))
    make_hvac_vent("HVAC", (-ROOM_W/4.0, ROOM_D-0.5, CEIL), width=0.80, depth=0.40)



def build_backoffice_detail():
    """Scene-standard deep pass (2026-07-12). The comic-shop back
    room (43 instances, vol6) was walls + a desk + filing cabinets.
    Adds the working clutter of a comics back office: stacked
    cardboard long-boxes of back issues, a glowing light table for
    inking, an articulated desk lamp, a rolling office chair, a
    corkboard of pinned pages on the north wall, a coffee maker on
    the filing cabinets, taped wall shelving with trade spines, and
    desk clutter (art boards, mug, pen cup). Room interior x -1.9..
    1.9, y 0..4.9; desk top z 0.8 at y 3.5; filing top z 1.3 at
    y ~1.0. make_box/make_cyl only."""
    import math as _m
    card = (0.62, 0.48, 0.30, 1.0)
    card_dk = (0.48, 0.36, 0.22, 1.0)
    steel = (0.40, 0.42, 0.45, 1.0)
    # ── Long-box stacks of comics down the EAST wall ──
    for s_i, (bx, by, n) in enumerate([(1.55, 1.45, 3), (1.55, 2.3, 2), (1.6, 3.75, 3)]):
        for k in range(n):
            bz = 0.12 + k * 0.24
            skew = 0.03 * ((s_i + k) % 2)
            make_box(f"LongBox_{s_i}_{k}", (bx + skew, by, bz),
                     (0.5, 0.72, 0.22), card if (s_i + k) % 2 else card_dk)
            make_box(f"LongBox_{s_i}_{k}_Lid", (bx + skew, by, bz + 0.115),
                     (0.53, 0.75, 0.02), card_dk)
            # a few comic tops poking above the open box
            make_box(f"LongBox_{s_i}_{k}_Tops", (bx + skew, by - 0.1, bz + 0.14),
                     (0.42, 0.4, 0.05), (0.72, 0.36, 0.30, 1.0))
    # ── Light table (glowing inking surface) on the WEST wall ──
    ltx, lty = -1.5, 2.6
    make_box("LightTable_Top", (ltx, lty, 0.78), (0.55, 0.8, 0.05), (0.30, 0.32, 0.36, 1.0))
    make_box("LightTable_Glass", (ltx, lty, 0.81), (0.48, 0.72, 0.02), (0.92, 0.94, 0.86, 1.0))
    make_box("LightTable_Page", (ltx + 0.05, lty + 0.05, 0.825),
             (0.30, 0.40, 0.004), (0.96, 0.95, 0.92, 1.0))
    for sgn in (-1, +1):
        make_box(f"LightTable_Leg_{sgn:+d}", (ltx + sgn * 0.22, lty, 0.38),
                 (0.05, 0.7, 0.76), steel)
    # ── Articulated desk lamp on the desk (base+arm+arm+head) ──
    lx, ly = -0.65, 3.75
    make_cyl("DeskLamp_Base", (lx, ly, 0.82), 0.07, 0.03, (0.18, 0.20, 0.24, 1.0), segments=8)
    make_cyl("DeskLamp_Arm1", (lx + 0.06, ly, 0.98), 0.014, 0.34, (0.24, 0.26, 0.30, 1.0), segments=5)
    make_cyl("DeskLamp_Arm2", (lx + 0.20, ly, 1.14), 0.014, 0.30, (0.24, 0.26, 0.30, 1.0), segments=5, axis='X')
    make_cyl("DeskLamp_Head", (lx + 0.33, ly, 1.10), 0.06, 0.10, (0.20, 0.22, 0.26, 1.0), segments=8)
    make_cyl("DeskLamp_Bulb", (lx + 0.35, ly, 1.06), 0.03, 0.03, (0.98, 0.92, 0.72, 1.0), segments=6)
    # ── Rolling office chair south of the desk ──
    ch_x, ch_y = 0.0, 2.7
    make_cyl("Chair_Column", (ch_x, ch_y, 0.28), 0.03, 0.42, (0.12, 0.12, 0.14, 1.0), segments=6)
    make_cyl("Chair_Seat", (ch_x, ch_y, 0.50), 0.24, 0.08, (0.16, 0.16, 0.18, 1.0), segments=10)
    make_box("Chair_Back", (ch_x, ch_y + 0.22, 0.78), (0.42, 0.06, 0.44), (0.16, 0.16, 0.18, 1.0))
    for k in range(5):
        a = k * (2 * _m.pi / 5)
        make_box(f"Chair_Star_{k}",
                 (ch_x + _m.cos(a) * 0.14, ch_y + _m.sin(a) * 0.14, 0.06),
                 (0.10, 0.10, 0.05), (0.10, 0.10, 0.12, 1.0))
        make_cyl(f"Chair_Caster_{k}",
                 (ch_x + _m.cos(a) * 0.26, ch_y + _m.sin(a) * 0.26, 0.04),
                 0.035, 0.05, (0.06, 0.06, 0.07, 1.0), segments=6, axis='X')
    # ── Corkboard of pinned pages on the NORTH wall ──
    make_box("Corkboard", (0.0, 4.82, 1.6), (1.4, 0.03, 0.9), (0.56, 0.42, 0.26, 1.0))
    make_box("Corkboard_Frame", (0.0, 4.80, 1.6), (1.48, 0.02, 0.98), (0.30, 0.22, 0.14, 1.0))
    for i, (px, pz, col) in enumerate([(-0.45, 1.8, (0.94, 0.92, 0.86)), (0.1, 1.9, (0.72, 0.78, 0.86)),
                                       (0.5, 1.7, (0.94, 0.92, 0.86)), (-0.2, 1.4, (0.90, 0.82, 0.72)),
                                       (0.4, 1.35, (0.94, 0.92, 0.86))]):
        make_box(f"Cork_Page_{i}", (px, 4.79, pz), (0.24, 0.01, 0.30), (*col, 1.0))
        make_cyl(f"Cork_Pin_{i}", (px, 4.77, pz + 0.12), 0.012, 0.02,
                 [(0.8,0.2,0.2,1),(0.2,0.4,0.8,1),(0.9,0.8,0.2,1)][i%3], segments=5, axis='Y')
    # ── Coffee maker on the filing cabinets (top z 1.3) ──
    cmx, cmy = -1.2, 1.0
    make_chamfer_box("CoffeeMaker_Body", (cmx, cmy, 1.48), (0.22, 0.28, 0.34), (0.16, 0.16, 0.18, 1.0))
    make_cyl("CoffeeMaker_Carafe", (cmx, cmy - 0.02, 1.40), 0.07, 0.14, (0.40, 0.28, 0.20, 0.9), segments=8)
    make_box("CoffeeMaker_Warmer", (cmx, cmy - 0.02, 1.33), (0.18, 0.20, 0.02), (0.10, 0.10, 0.11, 1.0))
    # ── Taped wall shelf with trade spines (west wall over table) ──
    make_box("WallShelf_Plank", (-1.82, 2.6, 1.7), (0.22, 1.2, 0.03), (0.44, 0.34, 0.24, 1.0))
    for i in range(9):
        sy = 2.05 + i * 0.13
        h = 0.24 + 0.03 * (i % 3)
        make_box(f"WallShelf_Book_{i}", (-1.82, sy, 1.72 + (h - 0.24) / 2),
                 (0.18, 0.11, h),
                 [(0.66,0.24,0.22,1),(0.24,0.42,0.52,1),(0.72,0.60,0.28,1),
                  (0.32,0.46,0.34,1)][i % 4])
    # ── Desk clutter: art boards + mug + pen cup ──
    make_box("Desk_ArtBoard_0", (0.35, 3.5, 0.815), (0.34, 0.44, 0.006), (0.94, 0.93, 0.88, 1.0))
    make_box("Desk_ArtBoard_1", (0.42, 3.55, 0.822), (0.34, 0.44, 0.006), (0.90, 0.90, 0.84, 1.0))
    make_cyl("Desk_Mug", (0.7, 3.2, 0.86), 0.04, 0.10, (0.30, 0.44, 0.52, 1.0), segments=8)
    make_cyl("Desk_PenCup", (-0.75, 3.3, 0.87), 0.045, 0.11, (0.20, 0.20, 0.24, 1.0), segments=8)
    for k in range(4):
        make_cyl(f"Desk_Pen_{k}", (-0.75 + (k - 1.5) * 0.012, 3.3, 0.95), 0.006, 0.14,
                 [(0.1,0.1,0.1,1),(0.2,0.3,0.7,1),(0.7,0.2,0.2,1),(0.1,0.5,0.3,1)][k], segments=4)


def build_hero_props():
    """2026-08-03 hero-prop pass — the props the vol6 office scenes
    revolve around."""
    iron = (0.20, 0.19, 0.20, 1.0)
    # THE SPEAK & SPELL — 1978 original, battered, cracked lower-left
    # corner, on the shelf above the file cabinet. Grille is its own
    # emissive object so the red glow can read (dim ch12, red ch21).
    make_box("SpeakSpell_Shelf", (-1.45, 1.0, 1.62), (0.60, 0.30, 0.035), (0.44, 0.32, 0.20, 1.0))
    make_chamfer_box("SpeakSpell_Body", (-1.45, 1.0, 1.665), (0.26, 0.20, 0.05), (0.72, 0.16, 0.14, 1.0))
    make_box("SpeakSpell_Keys", (-1.48, 0.96, 1.695), (0.16, 0.10, 0.01), (0.92, 0.88, 0.72, 1.0))
    make_box("SpeakSpell_Grille", (-1.36, 1.05, 1.695), (0.06, 0.06, 0.012), (0.94, 0.42, 0.30, 1.0))
    make_box("SpeakSpell_Crack", (-1.57, 0.92, 1.66), (0.03, 0.03, 0.045), (0.44, 0.10, 0.09, 1.0))
    # One-way mirror to the sales floor (installed 1983)
    make_box("OneWay_Mirror_Frame", (1.4, 0.10, 1.70), (1.20, 0.04, 0.95), (0.30, 0.26, 0.22, 1.0))
    make_box("OneWay_Mirror", (1.4, 0.08, 1.70), (1.10, 0.02, 0.85), (0.46, 0.52, 0.56, 1.0))
    # Desk drawer pedestal (top drawer takes the slip; green folder
    # in the second)
    make_chamfer_box("Desk_Pedestal", (0.62, 3.5, 0.38), (0.52, 0.72, 0.70), (0.40, 0.30, 0.20, 1.0))
    for di in range(3):
        make_box(f"Desk_Drawer_{di}", (0.62, 3.13, 0.62 - di * 0.21), (0.44, 0.02, 0.16), (0.34, 0.24, 0.16, 1.0))
        make_box(f"Desk_Drawer_{di}_Pull", (0.62, 3.11, 0.62 - di * 0.21), (0.12, 0.015, 0.03), iron)
    # Desk phone (Rick's long calls)
    make_box("Desk_Phone", (0.55, 3.72, 0.82), (0.22, 0.16, 0.08), (0.16, 0.16, 0.18, 1.0))
    make_box("Desk_Phone_Handset", (0.55, 3.72, 0.90), (0.20, 0.06, 0.04), (0.12, 0.12, 0.14, 1.0))
    # Overturned milk crate — Sam's seat, opposite the desk
    make_chamfer_box("Milk_Crate", (-0.20, 2.40, 0.16), (0.36, 0.36, 0.32), (0.62, 0.28, 0.24, 1.0))
    make_box("Milk_Crate_Rim", (-0.20, 2.40, 0.315), (0.38, 0.38, 0.03), (0.52, 0.22, 0.20, 1.0))
    # Mini-fridge + floor safe (one of the six keys)
    make_chamfer_box("Mini_Fridge", (1.65, 0.75, 0.42), (0.55, 0.55, 0.84), (0.82, 0.80, 0.76, 1.0))
    make_box("Mini_Fridge_Handle", (1.38, 0.55, 0.55), (0.03, 0.03, 0.30), iron)
    make_chamfer_box("Office_Safe", (1.62, 4.4, 0.28), (0.50, 0.50, 0.56), (0.24, 0.25, 0.28, 1.0))
    make_cyl("Safe_Dial", (1.62, 4.14, 0.32), 0.06, 0.03, (0.60, 0.62, 0.64, 1.0), axis='Y', segments=10)
    # The office door + the slide bolt Sam did not realize was there
    make_box("Office_Door", (0.0, 0.05, 1.03), (1.90, 0.05, 2.05), (0.40, 0.30, 0.20, 1.0))
    make_box("Office_Bolt_Plate", (0.85, 0.02, 1.20), (0.16, 0.02, 0.05), iron)
    make_box("Office_Bolt_Barrel", (0.78, 0.015, 1.20), (0.10, 0.025, 0.03), (0.60, 0.62, 0.64, 1.0))
    # Service/back door in the N wall, with its deadbolt
    make_box("Service_Door", (1.2, ROOM_D-0.05, 1.03), (0.90, 0.05, 2.05), (0.34, 0.30, 0.28, 1.0))
    make_box("Service_Deadbolt", (1.55, ROOM_D-0.09, 1.05), (0.06, 0.03, 0.10), (0.74, 0.60, 0.30, 1.0))


def main():
    clear_scene()
    build_shell()
    build_desk()
    build_filing()
    build_cal()
    build_bulb()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/cosmic_comics_back_office.glb"))
    print(f"\n[build_cosmic_comics_back_office] exporting to {out}")
    build_backoffice_detail()
    build_hero_props()
    export_glb(out)

if __name__ == "__main__":
    main()
