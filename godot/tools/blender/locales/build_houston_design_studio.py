"""VOL 5 · ANNA LOGUE'S OFFICE — Houston, the same tower as Erica's (Justice,
Judgement).

DRAFT 3 (2026-10-10) — the wrong REGISTER. Drafts 1-2 built "an open-plan
creative studio: drafting tables, brick wall, exposed duct ... plotter,
mood board" — a loft. The chapters: "Her brand was clean lines, negative
space, ethically sourced typefaces, and the quiet hum of expensive air
purifiers in her meticulously greige Houston high-rise office, three
floors down from a law firm whose name, if she squinted at the building
directory in the lobby, she would recognize" (Justice) — Erica's firm,
Erica's tower; "Anna Logue's third monitor — curated, naturally, for
optimal color fidelity"; "her cold brew (cashew milk ...)"; "her
oversized, architecturally inspired glasses"; the pitch deck, Slide 7;
"She stood up from her desk. She took the stairs, not the elevator, down
nineteen flights to the lobby." (Judgement)

Plan (7 x 6 m, ceiling 2.9, the tower's facade on the N): one glass wall
on mullions over the same city as Erica's (build_houston_office's
build_city run three floors lower through plan.shifted); greige walls
and carpet; her long white-oak desk on the E wall with THREE monitors
(the third showing EMBER & ASH), the pen tablet, the cold brew, the
glasses, her phone; a mesh task chair; the pitch deck pinned in a clean
grid on a white board (Slide 7); two air purifiers; a low credenza with
the colour-calibrated printer and the swatch books squared; a low sofa
and a side table; one sculptural plant; the door to the corridor.

Draft 4 targets: the corridor and the stair door (the nineteen flights);
the screens' content at insert scale; a dusk variant.
"""
import os, sys
import math as _m
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
_LOC = os.path.dirname(os.path.abspath(__file__))
if _LOC not in sys.path: sys.path.insert(0, _LOC)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_chamfer_box, make_lathe, make_tube, make_rot_box, make_blob, export_glb
from _props.structure import make_floor, make_wall, make_wall_with_openings
from _props.detail import make_wall_outlet, make_traffic_wear

ROOM_W = 7.0; ROOM_D = 6.0; CEIL = 2.9
XW, XE, YS, YN = -ROOM_W / 2.0, ROOM_W / 2.0, 0.0, ROOM_D
DOOR_X, DOOR_W, DOOR_H = -2.4, 0.95, 2.25
GREIGE = (0.78, 0.75, 0.70, 1.0); GREIGE_DK = (0.62, 0.60, 0.56, 1.0)
CARPET = (0.58, 0.56, 0.52, 1.0); CARPET_SEAM = (0.52, 0.50, 0.47, 1.0)
OAK = (0.80, 0.70, 0.56, 1.0); WHITE = (0.94, 0.94, 0.92, 1.0)
STEEL = (0.62, 0.64, 0.66, 1.0); BLACK = (0.10, 0.10, 0.11, 1.0)
GLASS = (0.62, 0.72, 0.78, 0.14); MULLION = (0.36, 0.38, 0.40, 1.0)
PAL = {"wall": GREIGE, "baseboard": GREIGE_DK}


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4, palette={"vinyl": CARPET, "seam": CARPET_SEAM})
    make_wall("Wall_W", (XW, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=+1)
    make_wall("Wall_E", (XE, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=-1)
    make_wall_with_openings("Wall_S", (0.0, YS, 0), length=ROOM_W + 0.4, height=CEIL, axis='X', palette=PAL,
                            baseboard_face_sign=+1, openings=[(DOOR_X, DOOR_H / 2.0, DOOR_W, DOOR_H)])
    make_box("Ceil", (0.0, ROOM_D / 2.0, CEIL + 0.05), (ROOM_W + 0.4, ROOM_D + 0.4, 0.10), (0.95, 0.95, 0.93, 1.0))
    make_box("Ceil_Slot_N", (0.0, YN - 0.35, CEIL - 0.002), (ROOM_W - 0.8, 0.05, 0.004), (0.30, 0.30, 0.32, 1.0))
    for i, (x, y) in enumerate(((-1.8, 1.6), (0.0, 1.6), (1.8, 1.6), (-1.8, 4.0), (0.0, 4.0), (1.8, 4.0))):
        make_cyl(f"Downlight_{i}", (x, y, CEIL - 0.004), 0.08, 0.008, (0.98, 0.97, 0.92, 1.0), segments=12)
    # the N glass: panes between mullions every 1.4 m, base and head rails
    z0, z1 = 0.10, CEIL - 0.12
    zc, zh = (z0 + z1) / 2.0, z1 - z0
    make_box("Glass_N_Base", (0.0, YN, 0.05), (ROOM_W - 0.2, 0.10, 0.10), MULLION)
    make_box("Glass_N_Head", (0.0, YN, CEIL - 0.06), (ROOM_W - 0.2, 0.10, 0.12), MULLION)
    xs = [XW + 0.10] + [XW + i * 1.4 for i in range(1, 5)] + [XE - 0.10]
    for i in range(len(xs) - 1):
        a, b = xs[i] + (0.03 if i else 0.0), xs[i + 1] - (0.03 if i < len(xs) - 2 else 0.0)
        make_box(f"Glass_N_{i}", ((a + b) / 2.0, YN, zc), (b - a, 0.02, zh), GLASS)
    for i in range(1, 5):
        make_box(f"Curtain_Wall_Mullion_N_{i}", (XW + i * 1.4, YN, zc), (0.06, 0.12, zh), MULLION)
    make_box("Slab_Edge_N", (0.0, YN + 0.25, -0.15), (ROOM_W + 0.4, 0.50, 0.30), (0.50, 0.52, 0.54, 1.0))
    # the door to the corridor, closed
    make_box("Office_Door", (DOOR_X, YS + 0.06, DOOR_H / 2.0 - 0.01), (DOOR_W - 0.04, 0.04, DOOR_H - 0.02), OAK)
    make_box("Office_Door_Pull", (DOOR_X + 0.34, YS + 0.10, 1.05), (0.02, 0.03, 0.36), STEEL)


def build_desk():
    """The long white-oak desk on the E wall, three monitors, her things."""
    dx, dy0, dy1 = XE - 0.10 - 0.40, 1.9, 4.5
    dy = (dy0 + dy1) / 2.0
    make_box("Oak_Desk_Top", (dx, dy, 0.74), (0.80, dy1 - dy0, 0.04), OAK)
    for i, y in enumerate((dy0 + 0.10, dy1 - 0.10)):
        make_box(f"Oak_Desk_Leg_{i}", (dx, y, 0.36), (0.70, 0.05, 0.72), BLACK)
    top = 0.76
    for i, (my, yaw) in enumerate(((dy - 0.62, 0.30), (dy, 0.0), (dy + 0.62, -0.30))):
        nm = ("Monitor", "Monitor_2", "Third_Monitor")[i]
        make_rot_box(nm, (dx + 0.20, my, top + 0.34), (0.03, 0.60, 0.36), BLACK, yaw=yaw)
        make_rot_box(f"{nm}_Screen", (dx + 0.18, my, top + 0.34), (0.004, 0.55, 0.31),
                     [(0.88, 0.88, 0.86, 1.0), (0.84, 0.86, 0.88, 1.0), (0.14, 0.12, 0.12, 1.0)][i], yaw=yaw)
        make_box(f"{nm}_Neck", (dx + 0.24, my, top + 0.10), (0.04, 0.05, 0.18), STEEL)
        make_box(f"{nm}_Foot", (dx + 0.24, my, top + 0.005), (0.16, 0.20, 0.01), STEEL)
    # EMBER & ASH on the third screen, the flame mark
    make_rot_box("Third_Monitor_Wordmark", (dx + 0.175, dy + 0.62, top + 0.30), (0.002, 0.30, 0.05), (0.92, 0.56, 0.22, 1.0), yaw=-0.30)
    make_rot_box("Third_Monitor_Flame", (dx + 0.175, dy + 0.62, top + 0.40), (0.002, 0.07, 0.10), (0.90, 0.36, 0.16, 1.0), yaw=-0.30)
    make_box("Keyboard", (dx - 0.08, dy, top + 0.008), (0.14, 0.42, 0.016), WHITE)
    make_box("Pen_Tablet", (dx - 0.10, dy + 0.50, top + 0.005), (0.24, 0.36, 0.01), BLACK)
    make_cyl("Pen_Tablet_Stylus", (dx - 0.04, dy + 0.50, top + 0.016), 0.005, 0.16, BLACK, axis='Y', segments=6)
    make_lathe("Cold_Brew", (dx - 0.20, dy - 0.50, top), [(0.0, 0.0), (0.035, 0.0), (0.04, 0.15), (0.0, 0.15)], (0.70, 0.56, 0.42, 0.7), segments=10)
    make_cyl("Cold_Brew_Straw", (dx - 0.19, dy - 0.50, top + 0.19), 0.004, 0.14, WHITE, segments=6)
    make_box("Anna_Glasses", (dx - 0.22, dy - 0.20, top + 0.008), (0.05, 0.15, 0.016), BLACK)
    make_box("Anna_Phone", (dx - 0.24, dy + 0.18, top + 0.005), (0.07, 0.14, 0.01), (0.86, 0.84, 0.82, 1.0))
    make_box("Desk_Notepad", (dx - 0.20, dy + 0.85, top + 0.004), (0.15, 0.21, 0.008), WHITE)
    # the mesh task chair, facing the screens (east)
    cx, cy = dx - 0.72, dy
    make_chamfer_box("Task_Chair_Seat", (cx, cy, 0.50), (0.48, 0.48, 0.06), (0.24, 0.24, 0.26, 1.0), chamfer=0.02)
    make_chamfer_box("Task_Chair_Back", (cx - 0.24, cy, 0.85), (0.05, 0.46, 0.64), (0.30, 0.30, 0.32, 0.85), chamfer=0.02)
    make_lathe("Task_Chair_Pillar", (cx, cy, 0.06), [(0.03, 0.0), (0.03, 0.34), (0.05, 0.38), (0.05, 0.40), (0.0, 0.40)], STEEL, segments=8)
    for si in range(5):
        a = si * 2.0 * _m.pi / 5.0 + 0.3
        make_rot_box(f"Task_Chair_Star_{si}", (cx + 0.14 * _m.cos(a), cy + 0.14 * _m.sin(a), 0.055), (0.28, 0.035, 0.03), STEEL, yaw=a)
        make_cyl(f"Task_Chair_Caster_{si}", (cx + 0.27 * _m.cos(a), cy + 0.27 * _m.sin(a), 0.025), 0.025, 0.035, BLACK, axis='Y', segments=6)


def build_room():
    """The pitch board, the purifiers, the credenza, the sofa, the plant."""
    # the pitch deck pinned in a clean grid on a white board, W wall — Slide 7 at the centre
    bx = XW + 0.10 + 0.015
    make_box("Pitch_Board", (bx, 3.0, 1.55), (0.02, 2.40, 1.20), WHITE)
    for r in range(3):
        for c in range(4):
            i = r * 4 + c
            make_box(f"Pitch_Slide_{i}", (bx + 0.012, 2.22 + c * 0.52, 1.95 - r * 0.38), (0.003, 0.42, 0.26),
                     (0.16, 0.14, 0.14, 1.0) if i == 6 else (0.90, 0.88, 0.84, 1.0))
            if i == 6:
                make_box("Pitch_Slide_7_Line", (bx + 0.0145, 2.22 + c * 0.52, 1.95 - r * 0.38), (0.002, 0.30, 0.03), (0.92, 0.56, 0.22, 1.0))
    # the two air purifiers, white towers, humming
    for i, (x, y) in enumerate(((XE - 0.35, 1.10), (XW + 0.35, 5.35))):
        make_lathe(f"Air_Purifier_{i}", (x, y, 0.0), [(0.0, 0.0), (0.15, 0.0), (0.16, 0.05), (0.16, 0.66), (0.14, 0.70), (0.0, 0.70)], WHITE, segments=16)
        make_cyl(f"Air_Purifier_{i}_Grille", (x, y, 0.71), 0.12, 0.012, (0.70, 0.70, 0.70, 1.0), segments=16)
        make_cyl(f"Air_Purifier_{i}_Light", (x + 0.155, y, 0.55), 0.012, 0.004, (0.50, 0.86, 0.96, 1.0), axis='X', segments=8)
    # the credenza on the S wall: the calibrated printer, the swatch books squared
    cx = 0.9
    make_box("Credenza_Body", (cx, YS + 0.10 + 0.24, 0.32), (2.0, 0.46, 0.64), WHITE)
    make_box("Credenza_Top", (cx, YS + 0.10 + 0.24, 0.655), (2.04, 0.50, 0.03), OAK)
    make_box("Printer", (cx + 0.55, YS + 0.34, 0.83), (0.56, 0.42, 0.32), (0.86, 0.86, 0.84, 1.0))
    make_box("Printer_Tray", (cx + 0.55, YS + 0.57, 0.78), (0.36, 0.06, 0.03), (0.70, 0.70, 0.68, 1.0))
    for i in range(5):
        make_box(f"Swatch_Book_{i}", (cx - 0.55 + i * 0.07, YS + 0.34, 0.67 + 0.13), (0.05, 0.24, 0.26),
                 [(0.86, 0.36, 0.30, 1.0), (0.30, 0.46, 0.66, 1.0), (0.94, 0.82, 0.30, 1.0), (0.36, 0.56, 0.40, 1.0), (0.46, 0.36, 0.56, 1.0)][i])
    # the low sofa under the window's W end, its side table
    sx, sy = -1.6, YN - 0.55
    make_chamfer_box("Sofa_Base", (sx, sy, 0.20), (1.90, 0.80, 0.24), (0.66, 0.64, 0.60, 1.0), chamfer=0.03)
    make_chamfer_box("Sofa_Back", (sx, sy + 0.32, 0.55), (1.90, 0.16, 0.46), (0.66, 0.64, 0.60, 1.0), chamfer=0.03)
    make_chamfer_box("Sofa_Cushion", (sx, sy - 0.06, 0.37), (1.80, 0.64, 0.10), (0.72, 0.70, 0.66, 1.0), chamfer=0.03)
    for i, (lx, ly) in enumerate(((-0.86, -0.32), (0.86, -0.32), (-0.86, 0.32), (0.86, 0.32))):
        make_box(f"Sofa_Leg_{i}", (sx + lx, sy + ly, 0.04), (0.04, 0.04, 0.08), BLACK)
    make_cyl("Side_Table_Top", (sx + 1.35, sy, 0.50), 0.25, 0.03, OAK, segments=16)
    make_cyl("Side_Table_Stem", (sx + 1.35, sy, 0.25), 0.03, 0.48, BLACK, segments=8)
    make_cyl("Side_Table_Foot", (sx + 1.35, sy, 0.01), 0.18, 0.02, BLACK, segments=12)
    make_box("Side_Table_Book", (sx + 1.35, sy, 0.53), (0.22, 0.28, 0.03), (0.86, 0.84, 0.80, 1.0))
    # one sculptural plant in a white pot, the SE corner
    px, py = XE - 0.45, YN - 0.55
    make_lathe("Plant_Pot", (px, py, 0.0), [(0.0, 0.0), (0.16, 0.0), (0.20, 0.40), (0.0, 0.40)], WHITE, segments=14)
    make_cyl("Plant_Stem", (px, py, 0.80), 0.02, 0.80, (0.36, 0.30, 0.20, 1.0), segments=6)
    for i in range(5):
        a = i * 1.26
        make_blob(f"Plant_Leaf_{i}", (px + 0.16 * _m.cos(a), py + 0.16 * _m.sin(a), 0.95 + i * 0.12), 0.12, (0.24, 0.40, 0.24, 1.0), noise=0.2, seed=3 + i, squash=0.4)
    make_wall_outlet("Outlet_E", (XE, 3.2), axis='Y', face_sign=-1, aged=False)
    make_traffic_wear("Wear_Door_Desk", [(DOOR_X, 0.4), (1.6, 2.4)], width=0.6, tint=(0.0, 0.0, 0.0, 1.0))


def build_city_lower():
    """The same city as Erica's, three floors lower (her office is
    "three floors down from a law firm"): build_houston_office's city run
    through plan.shifted with dz +10.5 and the facade line moved to this
    room's glass. That tower's own facade (sized to reach Erica's slab)
    and Erica's hawk are dropped; this floor's facade goes down from
    here."""
    import build_houston_office as HO
    from _props.plan import shifted
    skip = ("Out_Facade", "Hawk_")
    with shifted(vars(HO), 0.0, YN - HO.YN, dz=10.5):
        saved = {n: getattr(HO, n) for n in ("make_box", "make_rot_box")}
        for n, f in saved.items():
            setattr(HO, n, (lambda f: lambda name, *a, **k: None if name.startswith(skip) else f(name, *a, **k))(f))
        try:
            HO.build_city()
        finally:
            for n, f in saved.items():
                setattr(HO, n, f)
    gz = HO.GROUND_Z + 10.5
    make_box("Out_Facade_N", (0.0, YN + 0.55, gz / 2.0 - 0.3), (ROOM_W + 30.0, 0.2, -gz - 0.6), (0.28, 0.34, 0.40, 1.0))
    for f in range(1, 9):
        make_box(f"Out_Facade_N_Floor_{f}", (0.0, YN + 0.66, -f * 3.5), (ROOM_W + 30.0, 0.02, 0.35), (0.50, 0.52, 0.54, 1.0))


def main():
    clear_scene()
    build_shell(); build_desk(); build_room(); build_city_lower()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/houston_design_studio.glb"))
    print(f"\n[build_houston_design_studio] exporting to {out}")
    export_glb(out)


if __name__ == "__main__": main()
