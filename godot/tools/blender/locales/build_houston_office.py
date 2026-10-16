"""VOL 5 · HOUSTON OFFICE — Erica Campbell's office (Wheel of Fortune,
Justice, Judgement).

DRAFT 4 (2026-10-09) — the wrong REGISTER. Drafts 1-3 built "a generic
corporate office: glass partition, cubicle row, fluorescents" with Erica
in a glass box in its corner under a drop ceiling. The chapters say who
she is and where: a law partner of fourteen years, "high in her sterile
tower", "Outside her window, Houston in late afternoon: the freeway
traffic doing its slow desperate ballet, the heat-shimmer rising off
the asphalt twelve stories below ... a hawk" (the freeway was 12 m down,
not twelve stories), "Her office was a temple to control. Glass walls.
Chrome accents. Files indexed with obsessive precision", "the Italian
marble floor beneath Erica Campbell's expensive shoes", "The desk was
teak, custom-built, paid for in 2014", the eyedrops in "the third drawer
of her desk", her "ergonomic chair", "the second monitor", "the small
framed photograph on the corner of the desk, the only personal item in
the office — her mother, age fifty-one, in a sun hat in Galveston", and
her assistant Marcus, who "knocked on her door and pushed it open
carrying two coffees ... set the coffee on the desk ... stepped back to
the doorway and waited".

Plan (9 x 7 m, ceiling 3.0, the twelfth floor): the corner office — the
N and W walls floor-to-ceiling glass on mullions, the city and the
freeway 42 m down, the hawk on its thermal below the sill line; marble
underfoot, a charcoal rug; the teak desk mid-room facing the door, her
back to the N glass, two monitors, the photograph on its corner, the
phone, the chrome lamp, the eleven-page draft, Marcus's coffee and card;
the low credenza against the N glass; two chrome-and-leather guest
chairs; the seating group in the SW by the W glass; the E wall of
lateral files (every drawer labelled) under the law reporters; the door
in the S wall, ajar, a frosted sidelight; through it the hall and
Marcus's desk. No diplomas — the photograph is "the only personal item".

Coordinates: Blender Z-up, x -4.5..4.5, y 0 (the S wall, the door) ..
7.0 (the N glass); the hall is y -3.6..0. glTF export -> Godot (x, z, -y).

Draft 5 targets: the city at dusk (lit windows, the freeway's lights)
as a per-preset variant for Wheel's end; the files' label holders
legible at insert scale; Marcus as a presence (his jacket on his chair).
"""
import os, sys
import math as _m
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_chamfer_box, make_lathe, make_tube, make_rot_box, export_glb
from _props.furniture import make_chair, make_lamp
from _props.structure import make_floor, make_wall, make_wall_with_openings
from _props.detail import make_wall_outlet, make_traffic_wear
from _props.objects import make_mug

ROOM_W = 9.0; ROOM_D = 7.0; CEIL = 3.0
XW, XE, YS, YN = -ROOM_W / 2.0, ROOM_W / 2.0, 0.0, ROOM_D
HALL_Y0 = -3.6
DOOR_X, DOOR_W, DOOR_H = 2.7, 1.0, 2.30
SIDE_X, SIDE_W = 3.55, 0.45
GROUND_Z = -42.0                     # the street, twelve stories down

PAL_WALL = {"wall": (0.90, 0.89, 0.86, 1.0), "baseboard": (0.30, 0.30, 0.31, 1.0)}
MARBLE = (0.88, 0.86, 0.82, 1.0); MARBLE_SEAM = (0.72, 0.70, 0.66, 1.0)
TEAK = (0.52, 0.34, 0.20, 1.0); TEAK_DK = (0.40, 0.26, 0.15, 1.0)
CHROME = (0.78, 0.80, 0.82, 1.0); LEATHER = (0.12, 0.11, 0.12, 1.0)
GLASS = (0.62, 0.72, 0.78, 0.14); MULLION = (0.36, 0.38, 0.40, 1.0)
SCREEN = (0.20, 0.34, 0.46, 1.0); PAPER = (0.94, 0.93, 0.89, 1.0)
FILE_GREY = (0.62, 0.62, 0.60, 1.0)
REPORTERS = [(0.46, 0.16, 0.14, 1.0), (0.62, 0.50, 0.34, 1.0), (0.14, 0.18, 0.28, 1.0)]


def make_office_chair(prefix, x, y, seat_z=0.50, w=0.50, face=-1, col=LEATHER):
    """A five-star ergonomic chair; `face` -1 looks toward -Y (back on +Y)."""
    bdy = -face * 0.22
    make_chamfer_box(f"{prefix}_Seat", (x, y, seat_z), (w, w, 0.07), col, chamfer=0.025)
    make_chamfer_box(f"{prefix}_Back", (x, y + bdy, seat_z + 0.37), (w - 0.02, 0.06, 0.68), col, chamfer=0.025)
    make_cyl(f"{prefix}_Headroll", (x, y + bdy, seat_z + 0.74), 0.05, w - 0.06, col, axis='X', segments=8)
    make_lathe(f"{prefix}_Pillar", (x, y, 0.06), [(0.03, 0.0), (0.03, seat_z - 0.14), (0.05, seat_z - 0.11), (0.05, seat_z - 0.09), (0.0, seat_z - 0.09)], CHROME, segments=8)
    for si in range(5):
        a = si * 2.0 * _m.pi / 5.0 + 0.3
        make_rot_box(f"{prefix}_Star_{si}", (x + 0.14 * _m.cos(a), y + 0.14 * _m.sin(a), 0.055), (0.28, 0.035, 0.03), CHROME, yaw=a)
        make_cyl(f"{prefix}_Caster_{si}", (x + 0.27 * _m.cos(a), y + 0.27 * _m.sin(a), 0.025), 0.025, 0.035, P.METAL_BLACK, axis='Y', segments=6)
    for ai, ax in enumerate((-w / 2.0 - 0.02, w / 2.0 + 0.02)):
        make_tube(f"{prefix}_Arm_{ai}", [(x + ax, y - face * 0.12, seat_z + 0.035), (x + ax, y - face * 0.12, seat_z + 0.24), (x + ax, y + face * 0.16, seat_z + 0.24)],
                  0.016, CHROME, segments=6)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": MARBLE, "seam": MARBLE_SEAM})
    make_wall("Wall_E", (XE, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall_with_openings("Wall_S", (0.0, YS, 0), length=ROOM_W + 0.4, height=CEIL, axis='X', palette=PAL_WALL,
                            baseboard_face_sign=+1, openings=[(DOOR_X, DOOR_H / 2.0, DOOR_W, DOOR_H), (SIDE_X, DOOR_H / 2.0, SIDE_W, DOOR_H)])
    # the ceiling: one smooth plane, the slot diffuser along the glass
    make_box("Ceil", (0.0, ROOM_D / 2.0, CEIL + 0.05), (ROOM_W + 0.4, ROOM_D + 0.4, 0.10), (0.94, 0.94, 0.92, 1.0))
    make_box("Ceil_Slot_N", (0.0, YN - 0.35, CEIL - 0.002), (ROOM_W - 0.8, 0.05, 0.004), (0.30, 0.30, 0.32, 1.0))
    make_box("Ceil_Slot_W", (XW + 0.35, ROOM_D / 2.0, CEIL - 0.002), (0.05, ROOM_D - 0.8, 0.004), (0.30, 0.30, 0.32, 1.0))
    for i, (x, y) in enumerate(((-2.4, 2.0), (0.0, 2.0), (2.4, 2.0), (-2.4, 4.6), (0.0, 4.6), (2.4, 4.6), (3.6, 1.0), (3.6, 6.0))):
        make_cyl(f"Downlight_{i}", (x, y, CEIL - 0.004), 0.08, 0.008, (0.98, 0.96, 0.90, 1.0), segments=12)
        make_cyl(f"Downlight_{i}_Trim", (x, y, CEIL - 0.003), 0.10, 0.006, CHROME, segments=12)
    # the floor slab and ceiling run out past the glass to the building's edge
    make_box("Slab_Edge_N", (-0.2, YN + 0.25, -0.15), (ROOM_W + 1.0, 0.50, 0.30), (0.50, 0.52, 0.54, 1.0))
    make_box("Slab_Edge_W", (XW - 0.25, ROOM_D / 2.0 - 0.0, -0.15), (0.50, ROOM_D + 0.4, 0.30), (0.50, 0.52, 0.54, 1.0))


def build_glass_walls():
    """Floor-to-ceiling glass on the N and W: panes between mullions every
    1.5 m (N) / 1.4 m (W), a base rail and a head rail, the corner post.
    The mullions are named as the curtain WALL they are (the credenza
    stands against them)."""
    z0, z1 = 0.10, CEIL - 0.12
    zc, zh = (z0 + z1) / 2.0, z1 - z0
    make_box("Glass_N_Base", (0.0, YN, 0.05), (ROOM_W - 0.2, 0.10, 0.10), MULLION)
    make_box("Glass_N_Head", (0.0, YN, CEIL - 0.06), (ROOM_W - 0.2, 0.10, 0.12), MULLION)
    xs = [XW + 0.07] + [XW + i * 1.5 for i in range(1, 6)] + [XE - 0.10]
    for i in range(len(xs) - 1):
        a, b = xs[i] + (0.03 if i else 0.0), xs[i + 1] - (0.03 if i < len(xs) - 2 else 0.0)
        make_box(f"Glass_N_{i}", ((a + b) / 2.0, YN, zc), (b - a, 0.02, zh), GLASS)
    for i in range(1, 6):
        make_box(f"Curtain_Wall_Mullion_N_{i}", (XW + i * 1.5, YN, zc), (0.06, 0.12, zh), MULLION)
    make_box("Glass_W_Base", (XW, (YS + YN) / 2.0 + 0.0, 0.05), (0.10, ROOM_D - 0.27, 0.10), MULLION)
    make_box("Glass_W_Head", (XW, (YS + YN) / 2.0 + 0.0, CEIL - 0.06), (0.10, ROOM_D - 0.27, 0.12), MULLION)
    ys = [YS + 0.10] + [i * 1.4 for i in range(1, 5)] + [YN - 0.07]
    for i in range(len(ys) - 1):
        a, b = ys[i] + (0.03 if i else 0.0), ys[i + 1] - (0.03 if i < len(ys) - 2 else 0.0)
        make_box(f"Glass_W_{i}", (XW, (a + b) / 2.0, zc), (0.02, b - a, zh), GLASS)
    for i in range(1, 5):
        make_box(f"Curtain_Wall_Mullion_W_{i}", (XW, i * 1.4, zc), (0.12, 0.06, zh), MULLION)
    make_box("Curtain_Wall_Corner", (XW, YN, CEIL / 2.0), (0.14, 0.14, CEIL), MULLION)
    make_box("Wall_S_Return_W", (XW - 0.05, YS, CEIL / 2.0), (0.10, 0.20, CEIL), PAL_WALL["wall"])


def build_desk():
    """The custom teak desk mid-room: she sits N of it, facing the door,
    her back to the glass. Two pedestals, a modesty panel to the room,
    the third drawer, a chrome edge."""
    dx, dy = 0.0, 4.9
    make_box("Teak_Desk_Top", (dx, dy, 0.76), (2.10, 0.95, 0.04), TEAK)
    make_box("Teak_Desk_Edge", (dx, dy - 0.48, 0.76), (2.10, 0.012, 0.04), CHROME)
    for i, px in enumerate((-0.80, 0.80)):
        make_box(f"Teak_Desk_Pedestal_{i}", (dx + px, dy + 0.02, 0.37), (0.48, 0.86, 0.74), TEAK_DK)
    make_box("Teak_Desk_Modesty", (dx, dy - 0.40, 0.46), (1.12, 0.03, 0.56), TEAK_DK)
    for di in range(3):
        make_box(f"Desk_Drawer_{di}", (dx + 0.80, dy + 0.46, 0.60 - di * 0.20), (0.42, 0.02, 0.16), TEAK)
        make_box(f"Desk_Drawer_{di}_Pull", (dx + 0.80, dy + 0.475, 0.60 - di * 0.20), (0.14, 0.012, 0.015), CHROME)
    top = 0.78
    # two monitors facing her (+Y), the second angled
    for i, (mx, yaw) in enumerate(((-0.34, 0.0), (0.36, -0.22))):
        nm = "Monitor" if i == 0 else "Second_Monitor"
        make_rot_box(nm, (dx + mx, dy - 0.18, top + 0.30), (0.62, 0.03, 0.36), (0.10, 0.11, 0.12, 1.0), yaw=yaw)
        make_rot_box(f"{nm}_Screen", (dx + mx + 0.016 * _m.sin(-yaw), dy - 0.18 + 0.016 * _m.cos(yaw), top + 0.30), (0.56, 0.004, 0.30),
                     SCREEN if i == 0 else (0.86, 0.86, 0.82, 1.0), yaw=yaw)
        make_box(f"{nm}_Neck", (dx + mx, dy - 0.20, top + 0.09), (0.05, 0.04, 0.16), CHROME)
        make_box(f"{nm}_Foot", (dx + mx, dy - 0.20, top + 0.005), (0.22, 0.16, 0.01), CHROME)
    make_box("Keyboard", (dx - 0.20, dy + 0.18, top + 0.008), (0.42, 0.14, 0.016), (0.20, 0.20, 0.22, 1.0))
    make_box("Desk_Pad", (dx - 0.05, dy + 0.18, top + 0.002), (0.90, 0.42, 0.004), (0.18, 0.18, 0.20, 1.0))
    # the phone, the chrome lamp, the photograph on the corner
    make_chamfer_box("Desk_Phone_Base", (dx - 0.82, dy + 0.05, top + 0.025), (0.20, 0.24, 0.05), P.METAL_BLACK, chamfer=0.012)
    make_tube("Desk_Phone_Handset", [(dx - 0.90, dy + 0.12, top + 0.065), (dx - 0.82, dy + 0.12, top + 0.095), (dx - 0.74, dy + 0.12, top + 0.065)], 0.016, (0.12, 0.12, 0.14, 1.0), segments=8)
    make_box("Desk_Phone_Cell", (dx + 0.55, dy + 0.30, top + 0.005), (0.075, 0.15, 0.01), (0.10, 0.10, 0.12, 1.0))
    make_lamp("Erica_Lamp", dx + 0.88, dy - 0.25, base_z=top, h=0.52, shade_col=CHROME, body_col=CHROME)
    make_rot_box("Mother_Photo_Galveston", (dx + 0.92, dy + 0.30, top + 0.075), (0.16, 0.025, 0.14), CHROME, yaw=0.35, roll=0.0)
    make_rot_box("Mother_Photo_Galveston_Print", (dx + 0.915, dy + 0.316, top + 0.075), (0.12, 0.004, 0.10), (0.74, 0.66, 0.50, 1.0), yaw=0.35)
    make_rot_box("Mother_Photo_Galveston_Hat", (dx + 0.915, dy + 0.318, top + 0.10), (0.06, 0.002, 0.025), (0.92, 0.86, 0.66, 1.0), yaw=0.35)
    # the eleven-page draft, squared; Marcus's coffee and his card
    make_box("DAmbrosio_Contract", (dx - 0.50, dy + 0.30, top + 0.006), (0.216, 0.279, 0.012), PAPER)
    make_box("Contract_Top_Sheet", (dx - 0.50, dy + 0.30, top + 0.0125), (0.200, 0.262, 0.001), (0.98, 0.98, 0.96, 1.0))
    for i, (cx, cy) in enumerate(((dx + 0.32, dy - 0.02), (dx + 0.20, dy + 0.06))):
        make_lathe(f"Coffee_{i}", (cx, cy, top), [(0.0, 0.0), (0.03, 0.0), (0.042, 0.13), (0.0, 0.13)], (0.94, 0.92, 0.88, 1.0), segments=10)
        make_lathe(f"Coffee_{i}_Lid", (cx, cy, top + 0.13), [(0.0, 0.0), (0.044, 0.0), (0.044, 0.01), (0.0, 0.016)], (0.16, 0.16, 0.18, 1.0), segments=10)
    make_box("Marcus_Card", (dx + 0.40, dy + 0.20, top + 0.002), (0.10, 0.07, 0.004), (0.96, 0.95, 0.90, 1.0))
    make_office_chair("Erica_Chair", dx, dy + 0.85, seat_z=0.52, face=-1)
    # the guest chairs: chrome frames, black leather
    for gi, gx in enumerate((-0.55, 0.55)):
        make_chair(f"Guest_{gi}", dx + gx, dy - 1.20, yaw=0.0, wood=CHROME, seat_col=LEATHER, w=0.50)
    # the credenza against the N glass behind her
    make_box("Credenza_Body", (dx, YN - 0.34, 0.33), (2.60, 0.48, 0.56), TEAK_DK)
    make_box("Credenza_Top", (dx, YN - 0.34, 0.63), (2.66, 0.52, 0.04), TEAK)
    make_box("Credenza_Plinth", (dx, YN - 0.34, 0.025), (2.50, 0.42, 0.05), CHROME)
    for i in range(4):
        make_box(f"Credenza_Door_{i}", (dx - 0.975 + i * 0.65, YN - 0.585, 0.33), (0.62, 0.012, 0.50), TEAK)
    make_box("Bankers_Box", (dx + 0.85, YN - 0.34, 0.80), (0.40, 0.30, 0.30), (0.62, 0.50, 0.36, 1.0))
    make_box("Bankers_Box_Label", (dx + 0.85, YN - 0.492, 0.80), (0.16, 0.004, 0.06), PAPER)
    make_rug = make_box
    make_rug("Rug", (0.4, 3.9, 0.006), (5.2, 4.2, 0.012), (0.20, 0.20, 0.22, 1.0))


def build_files():
    """The E wall: lateral files every drawer labelled, chrome top edge;
    the law reporters in their runs above."""
    fx = XE - 0.10 - 0.25
    y0, y1 = 1.30, 5.70
    make_box("Lateral_Files", (fx, (y0 + y1) / 2.0, 0.55), (0.50, y1 - y0, 1.10), FILE_GREY)
    make_box("Lateral_Files_Top", (fx - 0.01, (y0 + y1) / 2.0, 1.115), (0.52, y1 - y0 + 0.02, 0.03), CHROME)
    n = 5
    for c in range(n):
        cy = y0 + (c + 0.5) * (y1 - y0) / n
        for d in range(3):
            dz = 0.20 + d * 0.34
            make_box(f"File_Drawer_{c}_{d}", (fx - 0.255, cy, dz), (0.012, (y1 - y0) / n - 0.04, 0.30), (0.68, 0.68, 0.66, 1.0))
            make_box(f"File_Label_{c}_{d}", (fx - 0.263, cy - 0.20, dz + 0.08), (0.004, 0.14, 0.05), PAPER)
            make_box(f"File_Pull_{c}_{d}", (fx - 0.266, cy + 0.10, dz + 0.02), (0.012, 0.24, 0.02), CHROME)
    # the reporters on three floating shelves
    for s, sz in enumerate((1.55, 1.95, 2.35)):
        make_box(f"Reporter_Shelf_{s}", (XE - 0.10 - 0.15, (y0 + y1) / 2.0, sz), (0.30, y1 - y0, 0.03), TEAK)
        for b in range(28):
            col = REPORTERS[(b // 7 + s) % len(REPORTERS)]
            make_box(f"Reporter_{s}_{b}", (XE - 0.10 - 0.16, y0 + 0.12 + b * 0.155, sz + 0.015 + 0.14), (0.24, 0.13, 0.28), col)


def build_seating():
    """The SW seating group by the W glass: the low leather sofa on the S
    wall, the glass-and-chrome table, an armchair facing the sofa."""
    sx, sy = -2.8, 0.62
    make_chamfer_box("Sofa_Base", (sx, sy, 0.22), (2.10, 0.86, 0.30), LEATHER, chamfer=0.03)
    make_chamfer_box("Sofa_Back", (sx, YS + 0.20, 0.58), (2.10, 0.20, 0.46), LEATHER, chamfer=0.04)
    for i, cx in enumerate((-0.52, 0.52)):
        make_chamfer_box(f"Sofa_Cushion_{i}", (sx + cx, sy + 0.06, 0.42), (1.00, 0.68, 0.10), LEATHER, chamfer=0.03)
    for i, cx in enumerate((-1.10, 1.10)):
        make_chamfer_box(f"Sofa_Arm_{i}", (sx + cx, sy, 0.40), (0.12, 0.86, 0.36), LEATHER, chamfer=0.02)
    for i, (lx, ly) in enumerate(((-0.95, -0.36), (0.95, -0.36), (-0.95, 0.30), (0.95, 0.30))):
        make_box(f"Sofa_Leg_{i}", (sx + lx, sy + ly, 0.035), (0.04, 0.04, 0.07), CHROME)
    tx, ty = -2.8, 1.85
    make_box("Coffee_Table_Glass", (tx, ty, 0.40), (1.20, 0.65, 0.02), (0.70, 0.80, 0.84, 0.35))
    for i, (lx, ly) in enumerate(((-0.56, -0.29), (0.56, -0.29), (-0.56, 0.29), (0.56, 0.29))):
        make_box(f"Coffee_Table_Leg_{i}", (tx + lx, ty + ly, 0.195), (0.03, 0.03, 0.39), CHROME)
    make_box("Coffee_Table_Book", (tx - 0.25, ty, 0.42), (0.32, 0.24, 0.02), (0.30, 0.32, 0.36, 1.0))
    ax, ay = -2.8, 3.05
    make_chamfer_box("Armchair_Seat", (ax, ay, 0.21), (0.78, 0.72, 0.42), LEATHER, chamfer=0.03)
    make_chamfer_box("Armchair_Back", (ax, ay + 0.31, 0.68), (0.78, 0.12, 0.40), LEATHER, chamfer=0.03)
    for i, cx in enumerate((-0.36, 0.36)):
        make_chamfer_box(f"Armchair_Arm_{i}", (ax + cx, ay, 0.48), (0.08, 0.70, 0.14), LEATHER, chamfer=0.015)


def build_door_and_hall():
    """The door in the S wall, ajar into the office (Marcus 'stepped back
    to the doorway and waited'), the frosted sidelight; the hall and
    Marcus's desk facing her door."""
    hx, hy = DOOR_X - DOOR_W / 2.0, YS + 0.10
    ang = _m.radians(68.0)
    L = DOOR_W - 0.04
    make_rot_box("Office_Door", (hx + 0.02 + _m.cos(ang) * L / 2.0, hy + _m.sin(ang) * L / 2.0 + 0.0, 1.14), (L, 0.045, 2.28), TEAK, yaw=ang)
    make_rot_box("Office_Door_Pull", (hx + 0.02 + _m.cos(ang) * (L - 0.10) + _m.sin(ang) * 0.04, hy + _m.sin(ang) * (L - 0.10) - _m.cos(ang) * 0.04, 1.05),
                 (0.02, 0.02, 0.40), CHROME, yaw=ang)
    make_box("Office_Door_Hinge", (hx + 0.01, hy, 1.14), (0.02, 0.03, 2.20), CHROME)
    make_box("Sidelight_Glass", (SIDE_X, YS, DOOR_H / 2.0), (SIDE_W, 0.02, DOOR_H), (0.84, 0.86, 0.86, 0.55))
    make_box("Name_Plate", (SIDE_X + 0.42, YS - 0.105, 1.55), (0.22, 0.008, 0.07), CHROME)
    # the hall
    hall_x0, hall_x1 = -1.6, 6.6
    make_box("Hall_Floor", ((hall_x0 + hall_x1) / 2.0, (HALL_Y0 + YS) / 2.0, -0.05), (hall_x1 - hall_x0, -HALL_Y0, 0.10), (0.36, 0.36, 0.38, 1.0))
    make_box("Hall_Ceil", ((hall_x0 + hall_x1) / 2.0, (HALL_Y0 + YS) / 2.0, CEIL - 0.25 + 0.05), (hall_x1 - hall_x0, -HALL_Y0, 0.10), (0.94, 0.94, 0.92, 1.0))
    make_wall("Hall_Wall_S", ((hall_x0 + hall_x1) / 2.0, HALL_Y0 - 0.10, 0), length=hall_x1 - hall_x0 + 0.2, height=CEIL - 0.25, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Hall_Wall_W", (hall_x0 - 0.10, (HALL_Y0 + YS) / 2.0, 0), length=-HALL_Y0, height=CEIL - 0.25, axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Hall_Wall_E", (hall_x1 + 0.10, (HALL_Y0 + YS) / 2.0, 0), length=-HALL_Y0, height=CEIL - 0.25, axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Hall_Art", (0.6, HALL_Y0 + 0.012, 1.55), (1.40, 0.025, 0.95), (0.70, 0.58, 0.42, 1.0))
    make_box("Hall_Art_Field", (0.6, HALL_Y0 + 0.027, 1.55), (1.20, 0.006, 0.75), (0.30, 0.40, 0.52, 1.0))
    for i in range(2):
        make_cyl(f"Hall_Downlight_{i}", (1.0 + i * 3.0, -1.8, CEIL - 0.25 - 0.004), 0.08, 0.008, (0.98, 0.96, 0.90, 1.0), segments=12)
    # Marcus's desk facing her door, his chair behind it
    mx, my = DOOR_X + 0.6, -2.30
    make_box("Marcus_Desk_Top", (mx, my, 0.74), (1.70, 0.78, 0.04), (0.86, 0.85, 0.82, 1.0))
    make_box("Marcus_Desk_Front", (mx, my + 0.37, 0.37), (1.70, 0.03, 0.70), (0.30, 0.30, 0.32, 1.0))
    for i, px in enumerate((-0.82, 0.82)):
        make_box(f"Marcus_Desk_Side_{i}", (mx + px, my, 0.36), (0.04, 0.74, 0.72), (0.30, 0.30, 0.32, 1.0))
    make_box("Marcus_Monitor", (mx - 0.20, my + 0.20, 1.06), (0.56, 0.03, 0.34), (0.10, 0.11, 0.12, 1.0))
    make_box("Marcus_Monitor_Neck", (mx - 0.20, my + 0.22, 0.85), (0.05, 0.04, 0.18), CHROME)
    make_box("Marcus_Monitor_Foot", (mx - 0.20, my + 0.22, 0.765), (0.20, 0.14, 0.01), CHROME)
    make_box("Marcus_Tray", (mx + 0.55, my + 0.05, 0.79), (0.30, 0.36, 0.06), P.METAL_BLACK)
    make_box("Marcus_Tray_Papers", (mx + 0.55, my + 0.05, 0.81), (0.22, 0.30, 0.02), PAPER)
    make_office_chair("Marcus_Chair", mx, my - 0.70, seat_z=0.48, w=0.46, face=+1, col=(0.24, 0.26, 0.30, 1.0))
    make_traffic_wear("Wear_Hall", [(-1.2, -1.2), (DOOR_X, -1.0), (DOOR_X, -0.2)], width=0.8, tint=(0.0, 0.0, 0.0, 1.0))


def build_city():
    """Twelve stories down: the street grid, the elevated freeway deck,
    the towers; the hawk on its thermal well below the sill; the
    building's own glass face going down."""
    gz = GROUND_Z
    make_box("Out_Ground", (0.0, 40.0, gz - 0.1), (500.0, 500.0, 0.2), (0.34, 0.34, 0.34, 1.0))
    for i, y in enumerate((22.0, 70.0, 118.0)):
        make_box(f"Out_Street_EW_{i}", (0.0, y, gz + 0.01), (500.0, 14.0, 0.02), (0.24, 0.24, 0.26, 1.0))
    for i, x in enumerate((-60.0, -18.0, 26.0, 70.0)):
        make_box(f"Out_Street_NS_{i}", (x, 40.0, gz + 0.01), (14.0, 500.0, 0.02), (0.24, 0.24, 0.26, 1.0))
    # the freeway: a deck on piers running E-W, its barriers, the traffic
    fy, fz = 46.0, gz + 9.0
    make_box("Out_Freeway_Deck", (0.0, fy, fz), (500.0, 18.0, 0.8), (0.52, 0.52, 0.50, 1.0))
    for s in (-1, 1):
        make_box(f"Out_Freeway_Barrier_{s:+d}", (0.0, fy + s * 8.9, fz + 0.9), (500.0, 0.3, 1.0), (0.66, 0.66, 0.62, 1.0))
    for i in range(14):
        make_cyl(f"Out_Freeway_Pier_{i}", (-130.0 + i * 20.0, fy, gz + 4.3), 1.0, 8.6, (0.56, 0.56, 0.54, 1.0), segments=10)
    cols = [(0.86, 0.86, 0.84, 1.0), (0.22, 0.24, 0.30, 1.0), (0.66, 0.16, 0.14, 1.0), (0.30, 0.36, 0.44, 1.0), (0.80, 0.76, 0.62, 1.0)]
    for i in range(22):
        lane = (i % 4) - 1.5
        make_box(f"Out_Car_{i}", (-110.0 + i * 10.7 + (i % 3) * 2.0, fy + lane * 3.6, fz + 0.95), (4.4, 1.8, 1.3), cols[i % len(cols)])
    # the towers N and W, the near one with the office where a light comes on
    towers = ((-40.0, 95.0, 30.0, 26.0, 150.0), (12.0, 120.0, 34.0, 30.0, 190.0), (60.0, 96.0, 26.0, 26.0, 120.0),
              (-95.0, 84.0, 28.0, 34.0, 110.0), (-100.0, -20.0, 30.0, 30.0, 90.0), (110.0, 140.0, 30.0, 30.0, 160.0),
              (-24.0, 62.0, 22.0, 18.0, 56.0))
    for i, (tx, ty, tw, td, th) in enumerate(towers):
        make_box(f"Out_Tower_{i}", (tx, ty, gz + th / 2.0), (tw, td, th), [(0.24, 0.32, 0.42, 1.0), (0.46, 0.44, 0.40, 1.0), (0.18, 0.24, 0.30, 1.0)][i % 3])
        for f in range(0, int(th / 3.5), 2):
            make_box(f"Out_Tower_{i}_Band_{f}", (tx, ty - td / 2.0 - 0.02, gz + f * 3.5 + 1.0), (tw + 0.02, 0.02, 0.6), (0.70, 0.74, 0.78, 1.0))
    make_box("Out_Tower_6_LitWin", (-24.0 + 4.0, 62.0 - 9.02, gz + 42.0), (2.6, 0.02, 1.6), (0.98, 0.86, 0.56, 1.0))
    # this building's own glass face, going down from the slab
    make_box("Out_Facade_N", (-0.2, YN + 0.55, gz / 2.0 - 0.3), (ROOM_W + 30.0, 0.2, -gz - 0.6), (0.28, 0.34, 0.40, 1.0))
    make_box("Out_Facade_W", (XW - 0.55, ROOM_D / 2.0 - 10.0, gz / 2.0 - 0.3), (0.2, ROOM_D + 30.0, -gz - 0.6), (0.28, 0.34, 0.40, 1.0))
    for f in range(1, 12):
        make_box(f"Out_Facade_N_Floor_{f}", (-0.2, YN + 0.66, -f * 3.5), (ROOM_W + 30.0, 0.02, 0.35), (0.50, 0.52, 0.54, 1.0))
    # the hawk on its thermal below the sill line
    hx, hy, hz = -6.0, 18.0, -8.0
    make_box("Hawk_Body", (hx, hy, hz), (0.12, 0.40, 0.10), (0.36, 0.26, 0.18, 1.0))
    for s in (-1, 1):
        make_rot_box(f"Hawk_Wing_{s:+d}", (hx + s * 0.48, hy, hz + 0.04), (0.86, 0.30, 0.02), (0.40, 0.30, 0.20, 1.0), roll=s * 0.12)
    make_box("Hawk_Tail", (hx, hy - 0.28, hz), (0.18, 0.14, 0.02), (0.62, 0.30, 0.18, 1.0))


def build_details():
    make_wall_outlet("Outlet_E", (XE, 6.3), axis='Y', face_sign=-1, aged=False)
    make_wall_outlet("Outlet_S", (-0.6, YS), axis='X', face_sign=1, aged=False)
    make_box("Floor_Box", (-0.4, 5.45, 0.003), (0.14, 0.14, 0.006), CHROME)
    make_tube("Desk_Cord", [(-0.40, 5.32, 0.78), (-0.40, 5.40, 0.30), (-0.40, 5.45, 0.006)], 0.008, (0.16, 0.16, 0.18, 1.0), segments=5)
    make_box("Thermostat", (XE - 0.11, 0.70, 1.45), (0.02, 0.10, 0.12), (0.92, 0.92, 0.90, 1.0))


def main():
    clear_scene()
    build_shell(); build_glass_walls(); build_desk(); build_files(); build_seating(); build_door_and_hall(); build_city(); build_details()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/houston_office.glb"))
    print(f"\n[build_houston_office] exporting to {out}")
    export_glb(out)


if __name__ == "__main__": main()
