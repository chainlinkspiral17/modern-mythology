"""Chief Miller's home office — vol6 — 892-area Harmony Creek Estates.

Canon (vol6 ch4): a FORMAL DINING ROOM he converted in 2018. The dining
table became his desk; the built-in china cabinet became his file
storage; he left the chandelier hanging because his wife wanted it. On
the desk: his NexCorp-monitored service laptop and TWO phones — the
personal one in his pocket, the other face-down on the desk (the one
that buzzes with the transport order). Rain hits the window behind him.

So the room reads as domestic dining-room bones wearing a cop's working
office: dark walnut table-desk, the glass-front china cabinet now full
of binders instead of china, a wall map of the subdivision, framed
commendations, a police scanner — under a kept brass chandelier. The
look is cool-rainy daylight from the N window + warm chandelier/lamp
practicals (miller_office.tscn does the lighting).

Coordinate frame: Blender Z-up. Interior y 0 (S door wall) → +Y (N),
walls x = ±ROOM_W/2, ceiling CEIL. glTF remaps to Godot (x, z, -y).
make_box / make_cyl only.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import (make_floor, make_wall, make_ceiling,
                              make_crown_molding, make_window)

ROOM_W = 4.6      # x ∈ [-2.3, 2.3]
ROOM_D = 5.2      # y ∈ [0, 5.2]  (door/S wall at y=0)
CEIL = 2.7        # dining rooms sit a touch taller

# ── Palette — formal dining bones, cop's working office ──
COL_WALL = (0.50, 0.50, 0.52, 1.0)      # muted slate — a cool room
COL_WAINSCOT = (0.40, 0.34, 0.28, 1.0)  # wood wainscot lower band
COL_BASE = (0.30, 0.24, 0.18, 1.0)
COL_FLOOR = (0.40, 0.28, 0.18, 1.0)     # dark oak
COL_SEAM = (0.26, 0.17, 0.10, 1.0)
COL_WALNUT = (0.30, 0.19, 0.11, 1.0)    # the table-desk
COL_WALNUT_DK = (0.22, 0.13, 0.08, 1.0)
COL_BRASS = (0.66, 0.50, 0.24, 1.0)
COL_GLASS = (0.58, 0.66, 0.72, 0.5)
COL_RAINGLASS = (0.34, 0.40, 0.46, 0.7) # cold wet window
COL_PAPER = (0.90, 0.88, 0.82, 1.0)
COL_BINDER_A = (0.34, 0.24, 0.20, 1.0)
COL_BINDER_B = (0.24, 0.30, 0.34, 1.0)
COL_BINDER_C = (0.40, 0.36, 0.26, 1.0)
COL_LAPTOP = (0.10, 0.10, 0.12, 1.0)
COL_SCREEN = (0.36, 0.52, 0.60, 1.0)    # faint cold screen glow
COL_PHONE = (0.08, 0.08, 0.10, 1.0)
COL_SCANNER = (0.14, 0.14, 0.16, 1.0)
COL_SCANNER_LED = (0.90, 0.30, 0.16, 1.0)
COL_LAMPSHADE = (0.86, 0.78, 0.58, 1.0)
COL_LAMPGLOW = (1.0, 0.86, 0.58, 1.0)
COL_CANDLE = (1.0, 0.86, 0.50, 1.0)     # chandelier bulbs — bloom
COL_RUG = (0.44, 0.26, 0.24, 1.0)
COL_RUG_BORDER = (0.28, 0.16, 0.15, 1.0)
COL_MAP = (0.72, 0.70, 0.60, 1.0)       # subdivision plat map
COL_MAP_INK = (0.30, 0.34, 0.30, 1.0)
COL_FRAME_GOLD = (0.70, 0.56, 0.26, 1.0)
COL_PHOTO = (0.72, 0.70, 0.66, 1.0)
COL_LEATHER = (0.26, 0.18, 0.16, 1.0)   # desk chair


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    pal = {"wall": COL_WALL, "baseboard": COL_BASE}
    for nm, x, bb in [("Wall_W", -ROOM_W / 2.0, +1), ("Wall_E", +ROOM_W / 2.0, -1)]:
        make_wall(nm, (x, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL,
                  axis='Y', palette=pal, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=pal, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W / 4.0 + 0.5), 0.0, 0),
              length=ROOM_W / 2.0 - 1.0, height=CEIL, axis='X', palette=pal)
    make_wall("Wall_S_E", (+(ROOM_W / 4.0 + 0.5), 0.0, 0),
              length=ROOM_W / 2.0 - 1.0, height=CEIL, axis='X', palette=pal)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL - 0.32), (2.0, 0.20, 0.64), COL_WALL)
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, with_grid=False, with_stains=False)
    # Wainscot band on the W and E walls (dining-room bones)
    for nm, x, fs in [("Wainscot_W", -ROOM_W / 2.0 + 0.06, +1), ("Wainscot_E", ROOM_W / 2.0 - 0.06, -1)]:
        make_box(nm, (x, ROOM_D / 2.0, 0.55), (0.03, ROOM_D, 0.86), COL_WAINSCOT)
        make_box(f"{nm}_Rail", (x, ROOM_D / 2.0, 1.00), (0.05, ROOM_D, 0.05), COL_WALNUT_DK)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W / 2.0 + 0.10, ROOM_D / 2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W / 2.0 - 0.10, ROOM_D / 2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D - 0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_WALNUT})
    # Rainy window on the N wall (behind the desk)
    make_window("Window_N", (0.0, ROOM_D - 0.02, 1.55), width=1.60, height=1.30,
                cross_mullion=True,
                palette={"glass": COL_RAINGLASS, "warm": (0.42, 0.48, 0.54, 0.5)})


def build_desk():
    """The former dining table, now the desk — set near the N window so he
    sits with the rain behind him. Service laptop + two phones (one
    face-down), a green banker's lamp, papers, a coffee mug, a landline."""
    dx, dy = 0.0, ROOM_D - 1.5
    top_z = 0.75
    # Big solid table-desk with a thick apron (reads as a dining table)
    make_box("Desk_Top", (dx, dy, top_z), (2.10, 1.05, 0.06), COL_WALNUT)
    make_box("Desk_Apron", (dx, dy, top_z - 0.10), (2.00, 0.95, 0.12), COL_WALNUT_DK)
    for lx in (-0.92, 0.92):
        for ly in (-0.40, 0.40):
            make_box(f"Desk_Leg_{lx}_{ly}", (dx + lx, dy + ly, top_z / 2.0),
                     (0.10, 0.10, top_z), COL_WALNUT_DK)
    # Service laptop (open, faint cold screen)
    make_box("Laptop_Base", (dx - 0.35, dy - 0.05, top_z + 0.04), (0.42, 0.30, 0.03), COL_LAPTOP)
    make_box("Laptop_Lid", (dx - 0.35, dy + 0.14, top_z + 0.20), (0.42, 0.03, 0.28), COL_LAPTOP)
    make_box("Laptop_Screen", (dx - 0.35, dy + 0.125, top_z + 0.20), (0.36, 0.02, 0.22), COL_SCREEN)
    # Two phones — personal (upright) + the other FACE-DOWN
    make_box("Phone_Personal", (dx + 0.30, dy - 0.30, top_z + 0.04), (0.09, 0.17, 0.02), COL_PHONE)
    make_box("Phone_FaceDown", (dx + 0.55, dy + 0.10, top_z + 0.03), (0.09, 0.17, 0.015), COL_PHONE)
    make_box("Phone_FaceDown_Back", (dx + 0.55, dy + 0.10, top_z + 0.038), (0.06, 0.10, 0.004), COL_SCANNER)
    # Green banker's lamp
    make_box("Lamp_Base", (dx + 0.72, dy + 0.20, top_z + 0.04), (0.20, 0.12, 0.03), COL_BRASS)
    make_cyl("Lamp_Stem", (dx + 0.72, dy + 0.20, top_z + 0.18), 0.012, 0.26, COL_BRASS, segments=6)
    make_box("Lamp_Shade", (dx + 0.72, dy + 0.20, top_z + 0.32), (0.26, 0.12, 0.08), (0.14, 0.34, 0.22, 1.0))
    make_box("Lamp_Glow", (dx + 0.72, dy + 0.20, top_z + 0.30), (0.22, 0.09, 0.03), COL_LAMPGLOW)
    # Papers, a manila folder, coffee mug, a black landline
    for pi in range(3):
        make_box(f"Desk_Paper_{pi}", (dx - 0.05 + pi * 0.03, dy - 0.30, top_z + 0.04 + pi * 0.006),
                 (0.30, 0.40, 0.006), COL_PAPER)
    make_box("Desk_Folder", (dx + 0.10, dy + 0.28, top_z + 0.05), (0.34, 0.44, 0.02), COL_BINDER_C)
    make_cyl("Desk_Mug", (dx - 0.62, dy - 0.20, top_z + 0.09), 0.04, 0.10, COL_WALNUT_DK, segments=10)
    make_box("Landline", (dx - 0.70, dy + 0.24, top_z + 0.06), (0.22, 0.28, 0.06), COL_SCANNER)
    make_box("Landline_Handset", (dx - 0.70, dy + 0.12, top_z + 0.09), (0.24, 0.07, 0.05), COL_LAPTOP)
    # Leather desk chair behind (N of) the desk, facing S
    ch_y = dy + 0.85
    make_cyl("Chair_Column", (dx, ch_y, 0.30), 0.03, 0.44, COL_SCANNER, segments=6)
    make_box("Chair_Seat", (dx, ch_y, 0.52), (0.52, 0.50, 0.10), COL_LEATHER)
    make_box("Chair_Back", (dx, ch_y + 0.24, 0.86), (0.52, 0.08, 0.60), COL_LEATHER)


def build_china_cabinet():
    """The built-in china cabinet on the E wall, now file storage: glass-
    front upper full of binders, a solid lower cabinet, a police scanner
    on top."""
    cx = ROOM_W / 2.0 - 0.26
    cy = 1.7
    make_box("Cabinet_Lower", (cx, cy, 0.44), (0.44, 1.8, 0.88), COL_WALNUT)
    for dz in (0.28, 0.62):
        make_box(f"Cabinet_Door_{dz}", (cx - 0.22, cy - 0.42, dz), (0.02, 0.7, 0.28), COL_WALNUT_DK)
        make_cyl(f"Cabinet_Knob_{dz}", (cx - 0.23, cy - 0.42, dz), 0.02, 0.03, COL_BRASS, segments=6, axis='X')
    # Glass-front upper with shelves of binders
    make_box("Cabinet_Upper_Frame", (cx, cy, 1.72), (0.44, 1.8, 1.04), COL_WALNUT)
    make_box("Cabinet_Upper_Hollow", (cx - 0.04, cy, 1.72), (0.38, 1.68, 0.92), COL_WALNUT_DK)
    make_box("Cabinet_Glass", (cx - 0.22, cy, 1.72), (0.02, 1.7, 0.94), COL_GLASS)
    for si, sz in enumerate((1.34, 1.72, 2.10)):
        make_box(f"Cabinet_Shelf_{si}", (cx - 0.02, cy, sz - 0.20), (0.34, 1.66, 0.03), COL_WALNUT_DK)
        for bi in range(7):
            by = cy - 0.72 + bi * 0.22
            h = 0.30 + 0.03 * (bi % 2)
            col = [COL_BINDER_A, COL_BINDER_B, COL_BINDER_C][(si + bi) % 3]
            make_box(f"Binder_{si}_{bi}", (cx - 0.04, by, sz - 0.20 + h / 2.0 - 0.15),
                     (0.30, 0.18, h), col)
    # Police scanner on top of the cabinet, one red LED
    make_box("Scanner", (cx, cy - 0.4, 2.30), (0.34, 0.24, 0.14), COL_SCANNER)
    make_box("Scanner_Face", (cx - 0.18, cy - 0.4, 2.30), (0.02, 0.18, 0.08), (0.20, 0.24, 0.26, 1.0))
    make_box("Scanner_LED", (cx - 0.19, cy - 0.46, 2.33), (0.01, 0.03, 0.02), COL_SCANNER_LED)
    for ai in range(2):
        make_cyl(f"Scanner_Ant_{ai}", (cx + 0.10 + ai * 0.06, cy - 0.32, 2.48), 0.006, 0.24,
                 COL_SCANNER, segments=4)


def build_chandelier():
    """The kept brass chandelier over where the table used to center — a
    domestic thing left in place. Six candle-arms; the bulbs bloom warm
    (chandelier is the warm practical in miller_office.tscn)."""
    cx, cy = 0.0, ROOM_D / 2.0 + 0.2
    import math as _m
    make_cyl("Chand_Chain", (cx, cy, CEIL - 0.20), 0.01, 0.40, COL_WALNUT_DK, segments=4)
    make_cyl("Chand_Hub", (cx, cy, CEIL - 0.44), 0.06, 0.10, COL_BRASS, segments=8)
    make_cyl("Chand_Stem", (cx, cy, CEIL - 0.58), 0.02, 0.20, COL_BRASS, segments=6)
    for k in range(6):
        a = k * (2 * _m.pi / 6)
        ax_, ay_ = cx + _m.cos(a) * 0.34, cy + _m.sin(a) * 0.34
        make_cyl(f"Chand_Arm_{k}", (cx + _m.cos(a) * 0.17, cy + _m.sin(a) * 0.17, CEIL - 0.52),
                 0.012, 0.40, COL_BRASS, segments=5, axis='X' if abs(_m.cos(a)) > abs(_m.sin(a)) else 'Y')
        make_cyl(f"Chand_Cup_{k}", (ax_, ay_, CEIL - 0.50), 0.03, 0.03, COL_BRASS, segments=6)
        make_cyl(f"Chand_Candle_{k}", (ax_, ay_, CEIL - 0.44), 0.015, 0.08, (0.90, 0.86, 0.78, 1.0), segments=6)
        make_box(f"Chand_Flame_{k}", (ax_, ay_, CEIL - 0.38), (0.03, 0.03, 0.05), COL_CANDLE)


def build_wall_dressing():
    """W wall: a framed plat map of the subdivision + framed commendations
    + a family photo (the small domestic thing). A short bookshelf of
    binders under the map. A rug centering the room."""
    wx = -ROOM_W / 2.0 + 0.05
    # Framed subdivision plat map
    make_box("Map_Frame", (wx, 3.4, 1.70), (0.03, 1.30, 0.90), COL_WALNUT_DK)
    make_box("Map_Paper", (wx + 0.012, 3.4, 1.70), (0.01, 1.16, 0.78), COL_MAP)
    for gi in range(5):
        make_box(f"Map_Road_{gi}", (wx + 0.016, 3.0 + gi * 0.18, 1.70), (0.005, 0.02, 0.72), COL_MAP_INK)
    for gi in range(4):
        make_box(f"Map_RoadH_{gi}", (wx + 0.016, 3.4, 1.42 + gi * 0.18), (0.005, 1.10, 0.02), COL_MAP_INK)
    make_box("Map_Zone_G", (wx + 0.02, 3.7, 1.55), (0.004, 0.16, 0.16), COL_SCANNER_LED)  # the flagged zone
    # Framed commendations (two)
    make_box("Commend_1_Frame", (wx, 1.7, 1.9), (0.03, 0.34, 0.44), COL_FRAME_GOLD)
    make_box("Commend_1_Cert", (wx + 0.012, 1.7, 1.9), (0.01, 0.26, 0.34), COL_PAPER)
    make_box("Commend_2_Frame", (wx, 1.7, 1.36), (0.03, 0.30, 0.38), COL_FRAME_GOLD)
    make_box("Commend_2_Cert", (wx + 0.012, 1.7, 1.36), (0.01, 0.22, 0.28), COL_PAPER)
    # Family photo on a short bookshelf under the map
    make_box("LowShelf", (wx + 0.16, 3.4, 0.90), (0.30, 1.10, 0.04), COL_WALNUT)
    make_box("LowShelf_Body", (wx + 0.16, 3.4, 0.44), (0.30, 1.10, 0.86), COL_WALNUT_DK)
    for bi in range(8):
        by = 2.95 + bi * 0.12
        make_box(f"LowBinder_{bi}", (wx + 0.16, by, 0.66), (0.24, 0.10, 0.34),
                 [COL_BINDER_A, COL_BINDER_B, COL_BINDER_C][bi % 3])
    make_box("FamilyPhoto_Frame", (wx + 0.10, 3.9, 0.98), (0.16, 0.20, 0.14), COL_FRAME_GOLD)
    make_box("FamilyPhoto_Img", (wx + 0.10, 3.9, 0.98), (0.10, 0.14, 0.10), COL_PHOTO)
    # Rug centering the room
    make_box("Rug", (0.0, ROOM_D / 2.0 - 0.3, 0.02), (2.8, 3.2, 0.02), COL_RUG)
    make_box("Rug_Border", (0.0, ROOM_D / 2.0 - 0.3, 0.025), (2.6, 3.0, 0.015), COL_RUG_BORDER)
    make_box("Rug_Field", (0.0, ROOM_D / 2.0 - 0.3, 0.03), (2.3, 2.7, 0.012), COL_RUG)


def main():
    clear_scene()
    build_shell()
    build_desk()
    build_china_cabinet()
    build_chandelier()
    build_wall_dressing()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/miller_office.glb"))
    print(f"\n[build_miller_office] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
