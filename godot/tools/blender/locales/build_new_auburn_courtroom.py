"""new_auburn_courtroom — the New Auburn County courtroom, vol6 ch8 (2026-10-10).

"Sam looks around the courtroom. The room is — Sam registers ... bigger
than she had expected. The wood is darker. There are — Sam counts —
twelve other people in the gallery besides her group." "Sam is in the
third row, with her mother on her left and Detective Ramirez on her
right." "In the second row, behind the prosecution table, there is a man
in a charcoal suit." "The judge is a woman ... Judge Patricia Halverson
... NAUC bench since 2006." "The clerk, beside the judge, looks at her
screen." "Sam's father is brought in from the side door ... He sits at
the defense table." "The bailiff at the door of the gallery ..." "the
press in the back row" "the third row of the gallery directly across the
aisle from her own row".

It played on `courthouse_chamber`: the Graustark parish small-claims room
(Louisiana, a third the size), which stays the Tarot Gauntlet's Justice
board. This is the Texas county criminal courtroom: 16 x 22 m under a
6 m coffered ceiling; dark wood wainscot to 2.4 m; the gallery's two
banks of pews either side of the centre aisle, eight rows each, the
bar rail and its gate; the prosecution table (the gallery's left as you
face the bench) and the defense table, their chairs, the lectern
between; the judge's bench up on its dais, the clerk's station beside
it with her screen, the witness box; the empty jury box along the E wall
(an arraignment); the Texas seal over the bench between the flags; the
side door by the defense table; the double doors at the back where the
bailiff stands; tall windows with blinds on the W wall; the clock.

Coordinates: Blender Z-up, the back doors at y 0, the bench at the N end.
x -8..8. glTF export -> Godot (x, z, -y).

Draft 2 targets: the twelve and Sam's group as figures; the hallway
outside the doors; a dusk variant for the 15:04 exit.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, make_chamfer_box, make_lathe, make_tube, make_rot_box, export_glb
from _props.structure import make_floor, make_wall, make_wall_with_openings
from _props.furniture import make_chair, make_lamp
from _props.decor import make_wall_clock

W, D, H = 16.0, 22.0, 6.0
XW, XE, YS, YN = -W / 2.0, W / 2.0, 0.0, D
FW, FE, FS, FN = XW + 0.10, XE - 0.10, YS + 0.10, YN - 0.10
PAL = {"wall": (0.80, 0.76, 0.66, 1.0), "baseboard": (0.22, 0.14, 0.10, 1.0)}
DARK = (0.26, 0.17, 0.11, 1.0); DARK2 = (0.32, 0.21, 0.13, 1.0); BRASS = (0.74, 0.58, 0.30, 1.0)
LEATHER = (0.20, 0.16, 0.14, 1.0); CARPET = (0.30, 0.20, 0.22, 1.0)
BAR_Y = 12.0                       # the bar rail between the gallery and the well
WIN_YS = (5.0, 9.5, 14.0)


def build_shell():
    make_floor("Floor", (0.0, D / 2.0, 0.0), size_x=W + 0.4, size_y=D + 0.4, palette={"vinyl": (0.42, 0.34, 0.28, 1.0), "seam": (0.30, 0.24, 0.20, 1.0)})
    make_box("Aisle_Carpet", (0.0, BAR_Y / 2.0, 0.005), (1.8, BAR_Y - 0.4, 0.01), CARPET)
    make_box("Well_Carpet", (0.0, (BAR_Y + FN) / 2.0, 0.005), (W - 1.0, FN - BAR_Y - 0.6, 0.01), (0.26, 0.22, 0.30, 1.0))
    make_wall_with_openings("Wall_W", (XW, D / 2.0, 0), length=D + 0.4, height=H, axis='Y', palette=PAL, baseboard_face_sign=+1,
                            openings=[(y, 3.2, 1.6, 3.4) for y in WIN_YS])
    make_wall_with_openings("Wall_E", (XE, D / 2.0, 0), length=D + 0.4, height=H, axis='Y', palette=PAL, baseboard_face_sign=-1,
                            openings=[(12.7, 1.10, 1.0, 2.2)])
    make_wall("Wall_N", (0.0, YN, 0), length=W + 0.4, height=H, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_wall_with_openings("Wall_S", (0.0, YS, 0), length=W + 0.4, height=H, axis='X', palette=PAL, baseboard_face_sign=+1,
                            openings=[(0.0, 1.30, 2.0, 2.6)])
    make_box("Ceil", (0.0, D / 2.0, H + 0.05), (W + 0.4, D + 0.4, 0.10), (0.86, 0.84, 0.78, 1.0))
    for i in range(1, 4):
        make_box(f"Ceil_Beam_X_{i}", (0.0, i * D / 4.0, H - 0.12), (W, 0.30, 0.24), (0.78, 0.74, 0.66, 1.0))
    for i, x in enumerate((-W / 6.0, W / 6.0)):
        make_box(f"Ceil_Beam_Y_{i}", (x, D / 2.0, H - 0.12), (0.30, D, 0.24), (0.78, 0.74, 0.66, 1.0))
    # the dark wood wainscot to 2.4 m round the room, its cap
    for tag, ax, line, a0, a1, sgn in (("W", 'Y', FW, 0.1, D - 0.1, 1), ("E", 'Y', FE, 0.1, D - 0.1, -1), ("N", 'X', FN, XW + 0.1, XE - 0.1, -1),
                                       ("S0", 'X', FS, XW + 0.1, -1.0, 1), ("S1", 'X', FS, 1.0, XE - 0.1, 1)):
        mid, ln = (a0 + a1) / 2.0, a1 - a0
        c = (line + sgn * 0.015, mid, 1.28) if ax == 'Y' else (mid, line + sgn * 0.015, 1.28)
        s = (0.03, ln, 2.24) if ax == 'Y' else (ln, 0.03, 2.24)
        make_box(f"Wainscot_{tag}", c, s, DARK)
        cc = (line + sgn * 0.03, mid, 2.42) if ax == 'Y' else (mid, line + sgn * 0.03, 2.42)
        cs = (0.06, ln, 0.06) if ax == 'Y' else (ln, 0.06, 0.06)
        make_box(f"Wainscot_Cap_{tag}", cc, cs, DARK2)
    # tall windows with blinds on the W wall
    for i, y in enumerate(WIN_YS):
        make_box(f"Window_W_{i}_Glass", (XW, y, 3.2), (0.01, 1.6, 3.4), (0.72, 0.80, 0.84, 0.25))
        for k in range(14):
            make_box(f"Window_W_{i}_Blind_{k}", (XW + 0.05, y, 1.70 + k * 0.22), (0.01, 1.60, 0.05), (0.86, 0.84, 0.78, 1.0))
    # the back double doors and the side door by the defense table
    for i, s in enumerate((-1, 1)):
        make_box(f"Back_Door_{i}", (s * 0.5, FS - 0.02, 1.30), (0.96, 0.05, 2.58), DARK2)
        make_box(f"Back_Door_{i}_Window", (s * 0.5, FS + 0.005, 1.75), (0.30, 0.01, 0.50), (0.66, 0.72, 0.76, 0.4))
    make_box("Side_Door", (FE - 0.02, 12.7, 1.10), (0.05, 0.96, 2.18), DARK2)
    make_cyl("Side_Door_Knob", (FE - 0.07, 12.35, 1.00), 0.03, 0.05, BRASS, axis='X', segments=8)
    make_wall_clock("Clock", (0.0, FS, 4.6), frozen_hour=1, frozen_min=54, facing='+Y')
    # pendant fixtures down the room
    for i, y in enumerate((4.0, 9.0, 14.0, 19.0)):
        for j, x in enumerate((-4.0, 4.0)):
            make_cyl(f"Pendant_{i}_{j}_Rod", (x, y, H - 0.6), 0.012, 1.20, BRASS, segments=6)
            make_lathe(f"Pendant_{i}_{j}_Globe", (x, y, H - 1.55), [(0.0, 0.0), (0.18, 0.08), (0.24, 0.24), (0.18, 0.36), (0.0, 0.40)], (0.96, 0.92, 0.80, 1.0), segments=12)


def build_gallery():
    """Two banks of pews, eight rows, either side of the centre aisle; the
    bar rail with its gate."""
    for side, sgn in (("L", -1), ("R", 1)):
        for r in range(8):
            y = BAR_Y - 1.4 - r * 1.15
            x = sgn * (0.9 + 3.05)
            make_box(f"Pew_{side}_{r}_Seat", (x, y, 0.45), (6.0, 0.48, 0.06), DARK2)
            make_box(f"Pew_{side}_{r}_Back", (x, y - 0.27, 0.80), (6.0, 0.06, 0.70), DARK)
            for e, ex in enumerate((x - 2.98, x + 2.98)):
                make_box(f"Pew_{side}_{r}_End_{e}", (ex, y - 0.05, 0.50), (0.06, 0.62, 1.00), DARK)
            make_box(f"Pew_{side}_{r}_Kick", (x, y + 0.20, 0.21), (5.9, 0.03, 0.42), DARK)
    # the bar rail and its swinging gate at the aisle
    for side, sgn in (("L", -1), ("R", 1)):
        x0, x1 = sgn * 0.6, sgn * (W / 2.0 - 0.15)
        cx, ln = (x0 + x1) / 2.0, abs(x1 - x0)
        make_box(f"Bar_Rail_{side}_Top", (cx, BAR_Y, 0.95), (ln, 0.10, 0.06), DARK2)
        make_box(f"Bar_Rail_{side}_Panel", (cx, BAR_Y, 0.47), (ln, 0.05, 0.94), DARK)
    make_box("Bar_Gate_L", (-0.30, BAR_Y, 0.50), (0.60, 0.05, 0.80), DARK2)
    make_box("Bar_Gate_R", (0.30, BAR_Y, 0.50), (0.60, 0.05, 0.80), DARK2)


def build_well():
    """The counsel tables, the lectern, the bench, the clerk, the witness
    box, the jury box, the seal and the flags."""
    for side, sgn, nm in (("L", -1, "Prosecution"), ("R", 1, "Defense")):
        tx, ty = sgn * 3.2, BAR_Y + 2.0
        make_box(f"{nm}_Table_Top", (tx, ty, 0.76), (2.8, 1.0, 0.05), DARK2)
        make_box(f"{nm}_Table_Modesty", (tx, ty - 0.46, 0.40), (2.7, 0.04, 0.70), DARK)
        for e, ex in enumerate((tx - 1.32, tx + 1.32)):
            make_box(f"{nm}_Table_End_{e}", (ex, ty, 0.37), (0.06, 0.90, 0.74), DARK)
        for c, cx in enumerate((tx - 0.8, tx, tx + 0.8)):
            make_chair(f"{nm}_Chair_{c}", cx, ty - 0.85, yaw=0.0, wood=DARK, seat_col=LEATHER, w=0.48)
        make_box(f"{nm}_Folder_Stack", (tx - 0.4, ty, 0.80), (0.24, 0.32, 0.04), (0.86, 0.74, 0.46, 1.0))
        make_lathe(f"{nm}_Water_Pitcher", (tx + 0.9, ty + 0.2, 0.785), [(0.0, 0.0), (0.06, 0.0), (0.07, 0.16), (0.05, 0.22), (0.0, 0.22)], (0.82, 0.86, 0.88, 0.5), segments=10)
    make_box("Lectern", (0.0, BAR_Y + 2.6, 0.55), (0.60, 0.46, 1.10), DARK2)
    make_rot_box("Lectern_Top", (0.0, BAR_Y + 2.6, 1.13), (0.66, 0.52, 0.04), DARK, pitch=0.0)
    # the bench: a raised dais, the high front, the judge's chair, the clerk's station beside it
    by = FN - 1.6
    make_box("Bench_Dais", (0.0, by, 0.30), (6.4, 3.0, 0.60), DARK)
    make_box("Bench_Front", (0.0, by - 0.9, 1.25), (4.2, 0.12, 1.30), DARK2)
    make_box("Bench_Top", (0.0, by - 0.6, 1.93), (4.4, 0.80, 0.06), DARK)
    make_box("Bench_Back_Panel", (0.0, FN - 0.03, 2.4), (5.0, 0.04, 3.4), DARK2)
    make_chamfer_box("Judge_Chair_Back", (0.0, by + 0.45, 1.73), (0.70, 0.12, 1.10), LEATHER, chamfer=0.04)
    make_chamfer_box("Judge_Chair_Seat", (0.0, by + 0.15, 1.12), (0.64, 0.58, 0.12), LEATHER, chamfer=0.04)
    make_box("Judge_Chair_Base", (0.0, by + 0.15, 0.83), (0.30, 0.30, 0.46), DARK)
    make_box("Judge_Nameplate", (0.0, by - 0.97, 1.65), (0.70, 0.02, 0.12), BRASS)
    make_lathe("Gavel_Block", (0.45, by - 0.55, 1.96), [(0.0, 0.0), (0.06, 0.0), (0.06, 0.02), (0.0, 0.02)], DARK2, segments=10)
    make_box("Bench_Folder", (-0.4, by - 0.55, 1.975), (0.24, 0.32, 0.03), (0.86, 0.74, 0.46, 1.0))
    # the clerk beside the judge, lower, her screen
    cx = 4.15
    make_box("Clerk_Station", (cx, by - 0.3, 0.60), (1.8, 0.80, 1.20), DARK2)
    make_box("Clerk_Station_Top", (cx, by - 0.3, 1.215), (1.9, 0.86, 0.03), DARK)
    make_box("Clerk_Screen", (cx, by - 0.2, 1.40), (0.56, 0.04, 0.34), (0.10, 0.10, 0.12, 1.0))
    make_box("Clerk_Screen_Face", (cx, by - 0.222, 1.40), (0.50, 0.004, 0.28), (0.40, 0.62, 0.86, 1.0))
    # the witness box on the bench's W side
    wx = -4.3
    make_box("Witness_Box", (wx, by - 0.5, 0.55), (1.4, 1.2, 1.10), DARK2)
    make_box("Witness_Box_Floor", (wx, by - 0.2, 0.32), (1.2, 1.0, 0.04), DARK)
    make_cyl("Witness_Mic", (wx + 0.3, by - 1.0, 1.25), 0.008, 0.30, (0.20, 0.20, 0.22, 1.0), segments=5)
    # the jury box along the E wall: two tiers of six, empty (an arraignment)
    jx = FE - 1.4
    make_box("Jury_Box_Rail", (jx - 1.0, 16.3, 0.55), (0.06, 5.2, 1.10), DARK2)
    make_box("Jury_Tier_1", (jx + 0.55, 16.3, 0.15), (0.90, 5.2, 0.30), DARK)
    for t, (tx_, tz) in enumerate(((jx - 0.35, 0.0), (jx + 0.55, 0.30))):
        for k in range(6):
            yy = 14.0 + k * 0.92
            make_chamfer_box(f"Jury_{t}_{k}_Seat", (tx_, yy, tz + 0.46), (0.50, 0.50, 0.10), LEATHER, chamfer=0.03)
            make_chamfer_box(f"Jury_{t}_{k}_Back", (tx_ + 0.24, yy, tz + 0.82), (0.08, 0.48, 0.62), LEATHER, chamfer=0.03)
            make_box(f"Jury_{t}_{k}_Post", (tx_, yy, tz + 0.205), (0.08, 0.08, 0.41), DARK)
    # the Texas seal over the bench between the flags
    make_cyl("Texas_Seal_Frame", (0.0, FN - 0.03, 4.2), 0.80, 0.06, (0.80, 0.66, 0.32, 1.0), axis='Y', segments=24)
    make_cyl("Texas_Seal_Field", (0.0, FN - 0.065, 4.2), 0.62, 0.01, (0.20, 0.30, 0.52, 1.0), axis='Y', segments=24)
    make_box("Texas_Seal_Star", (0.0, FN - 0.072, 4.2), (0.36, 0.004, 0.36), (0.92, 0.90, 0.84, 1.0))
    for i, (x, cols) in enumerate(((-2.8, ((0.20, 0.30, 0.52, 1.0), (0.74, 0.22, 0.20, 1.0))), (2.8, ((0.20, 0.30, 0.52, 1.0), (0.92, 0.90, 0.84, 1.0))))):
        make_box(f"Flag_{i}_Base", (x, FN - 0.5, 0.65), (0.40, 0.40, 0.10), DARK)
        make_cyl(f"Flag_{i}_Pole", (x, FN - 0.5, 2.0), 0.02, 2.70, BRASS, segments=6)
        make_rot_box(f"Flag_{i}_Cloth", (x + 0.25, FN - 0.5, 2.70), (0.50, 0.04, 0.90), cols[0], roll=0.0, pitch=0.12)
        make_rot_box(f"Flag_{i}_Cloth_Stripe", (x + 0.27, FN - 0.52, 2.55), (0.44, 0.004, 0.40), cols[1], pitch=0.12)


def build_outside():
    make_box("Out_Ground", (XW - 30.0, D / 2.0, -0.05), (60.0, 80.0, 0.10), (0.46, 0.50, 0.34, 1.0))
    make_box("Out_Building_W", (XW - 26.0, D / 2.0, 7.0), (4.0, 40.0, 14.0), (0.70, 0.66, 0.58, 1.0))
    from _props.trees import make_broadleaf
    for i in range(4):
        make_broadleaf(f"Out_Live_Oak_{i}", XW - 9.0, 2.0 + i * 6.0, 7.0, (0.28, 0.40, 0.24, 1.0), (0.32, 0.26, 0.20, 1.0), crown=0.42)


def build_curb():
    """Outside the back doors: the courthouse steps down to the curb, and
    at the curb Miriam's car — "a 2009 Subaru wagon, dark green,
    immaculate", its passenger door open toward the steps, and on the
    seat "a single faint outline of a quilt" (Sam: "Twilight-colored").
    Hollow-bodied (pan, sides, hood, tailgate, roof) so the seat reads
    through the open door — after courthouse_chamber's 2026-09 build."""
    green = (0.16, 0.30, 0.20, 1.0); green_dk = (0.12, 0.24, 0.16, 1.0)
    make_box("Steps_Landing", (0.0, -1.2, -0.10), (6.0, 2.4, 0.20), (0.70, 0.68, 0.62, 1.0))
    for k in range(4):
        make_box(f"Steps_{k}", (0.0, -2.6 - k * 0.36, -0.30 - k * 0.18), (6.0, 0.36, 0.18), (0.70, 0.68, 0.62, 1.0))
    gz = -0.95
    make_box("Curb_Sidewalk", (0.0, -5.5, gz + 0.06), (24.0, 2.6, 0.12), (0.62, 0.60, 0.56, 1.0))
    make_box("Curb_Kerb", (0.0, -6.9, gz + 0.06), (24.0, 0.20, 0.14), (0.66, 0.64, 0.60, 1.0))
    make_box("Curb_Street", (0.0, -10.5, gz - 0.02), (40.0, 7.0, 0.06), (0.30, 0.30, 0.32, 1.0))
    cy, z0 = -8.6, gz + 0.01
    make_box("Green_Subaru_Pan", (0.0, cy, z0 + 0.40), (4.60, 1.80, 0.10), green_dk)
    make_box("Green_Subaru_Side_S", (0.0, cy - 0.87, z0 + 0.72), (4.60, 0.06, 0.55), green)
    make_box("Green_Subaru_Side_N_Rear", (-1.2, cy + 0.87, z0 + 0.72), (2.20, 0.06, 0.55), green)
    make_box("Green_Subaru_Hood", (1.75, cy, z0 + 0.75), (1.10, 1.70, 0.60), green)
    make_box("Green_Subaru_Tailgate", (-2.05, cy, z0 + 0.85), (0.50, 1.70, 0.80), green)
    make_box("Green_Subaru_Roof", (-0.4, cy, z0 + 1.43), (3.20, 1.80, 0.06), green)
    for i, x in enumerate((1.15, -1.95)):
        for s in (-1, 1):
            make_box(f"Green_Subaru_Pillar_{i}_{s:+d}", (x, cy + s * 0.85, z0 + 1.15), (0.06, 0.06, 0.50), green_dk)
    make_box("Green_Subaru_Windshield", (1.15, cy, z0 + 1.22), (0.04, 1.60, 0.36), (0.60, 0.70, 0.76, 0.35))
    make_box("Green_Subaru_Door_Open", (0.85, cy + 1.35, z0 + 0.72), (0.06, 0.90, 0.55), green)
    for wi, (wx, wy) in enumerate(((-1.5, cy - 0.995), (1.5, cy - 0.995), (-1.5, cy + 0.995), (1.5, cy + 0.995))):
        make_cyl(f"Green_Subaru_Wheel_{wi}", (wx, wy, z0 + 0.32), 0.32, 0.25, (0.12, 0.12, 0.13, 1.0), axis='Y', segments=10)
    make_box("Subaru_Seat", (0.35, cy + 0.42, z0 + 0.675), (0.50, 0.50, 0.45), (0.34, 0.32, 0.30, 1.0))
    make_box("Subaru_Seat_Back", (0.05, cy + 0.42, z0 + 1.10), (0.10, 0.50, 0.40), (0.34, 0.32, 0.30, 1.0))
    make_box("Quilt_Outline", (0.38, cy + 0.42, z0 + 0.9015), (0.30, 0.30, 0.003), (0.46, 0.44, 0.48, 1.0))


def main():
    clear_scene()
    build_shell(); build_gallery(); build_well(); build_outside(); build_curb()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/new_auburn_courtroom.glb"))
    print(f"\n[build_new_auburn_courtroom] exporting to {out}")
    export_glb(out)


if __name__ == "__main__": main()
