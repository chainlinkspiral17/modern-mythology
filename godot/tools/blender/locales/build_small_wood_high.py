"""small_wood_high — the school of vols 2 and 4 (draft 1, 2026-10-16).

The user: "Let's move back to background and model work for all the new vol
1-4 stuff." Twelve vols 1-4 scene uses play a school (bg_places.json group
small_wood_high): vol 2's Small Wood Senior High and vol 4's middle school,
one building here with a camera per room.

What the scenes say, and where it is here:
  "I'm in a small town high school gymnasium with a bunch of old men who get
   off on spouting out the rules of parliamentary procedure" … "Pastor Tim
   stands up at the podium in the middle of the gymnasium"
                    → GYM: the board's long table on the court, the podium at
                      centre court, rows of folding chairs, bleachers pulled out
  "Clarrisa cornered me in the hall"  → HALL: lockers both sides, the trophy
                      case, a stairwell at the east end ("near stairwells or
                      traffic intersections", vol 4)
  "Coach Kordowski humbled things down in the locker room"
                    → LOCKER room: benches between locker rows, the coach's
                      office window
  "I was sitting behind Emily and Tara" (art class)
                    → ART room: worktables, easels, the sink, drying rack
  vol 4: "He walks to his classroom … the motley seventh grade morning
   crew"; "the desks are all in a circle, workshop style"
                    → CLASS: rows of desks, the teacher's desk, chalkboard,
                      the reading shelf by the door, windows
  "There are kids … waiting for him outside the computer lab … a sign hung
   up over one of the children that says, 'We see everything as
   inspiration!'"   → LAB: three rows of computers, the sign

Plan (blender x east, y north): the hall runs E-W along y 0..3.2 (x -24..24).
North of it the gym (x -24..4, y 3.2..21.2, 7.5 m high) and the locker room
(x 4..14, y 3.2..11.2). South of it the classroom (x -14..-4), the art room
(x -4..6) and the computer lab (x 6..16), each 9 m deep (y -9..0), 3.0 high,
windows in the S wall onto the grounds.

DRAFT 2 targets: the hearing's banner and flags; the gym's folding partition;
the art room's student work on the walls (HeroArt); the lab's sign as a
HeroArt picture with the slogan; bleacher wear and scuffed court paint; the
"workshop style" circle of desks as its own preset; Deck-verified framing.
"""
import math, os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_chamfer_box, export_glb
from _props.views import make_view
from _props.structure import make_floor, make_wall, make_ceiling, make_window, make_wall_with_openings
from _props.furniture import make_chair, make_table
from _props.safety import make_fluorescent_tube_fixture, make_smoke_detector
from _props.detail import make_traffic_wear, make_wall_outlet, make_light_switch

HALL_X0, HALL_X1, HALL_Y0, HALL_Y1, HALL_H = -24.0, 24.0, 0.0, 3.2, 3.0
GYM_X0, GYM_X1, GYM_Y1, GYM_H = -24.0, 4.0, 21.2, 7.5
LOCK_X0, LOCK_X1, LOCK_Y1 = 4.0, 14.0, 11.2
ROOM_Y0, ROOM_H = -9.0, 3.0
CLASS = (-14.0, -4.0); ART = (-4.0, 6.0); LAB = (6.0, 16.0)
WALL = {"wall": (0.86, 0.84, 0.76, 1.0), "baseboard": (0.30, 0.30, 0.32, 1.0)}
BLOCK = {"wall": (0.80, 0.80, 0.74, 1.0), "baseboard": (0.26, 0.28, 0.30, 1.0)}   # painted block
GYM_WALL = {"wall": (0.74, 0.70, 0.58, 1.0), "baseboard": (0.20, 0.30, 0.46, 1.0)}
VINYL = {"vinyl": (0.78, 0.76, 0.68, 1.0), "seam": (0.62, 0.60, 0.54, 1.0)}
MAPLE = {"vinyl": (0.78, 0.60, 0.36, 1.0), "seam": (0.64, 0.48, 0.28, 1.0)}
LOCKER = (0.22, 0.40, 0.58, 1.0)          # school blue
WOOD = (0.52, 0.38, 0.22, 1.0); WOOD_DK = (0.30, 0.22, 0.14, 1.0)
STEEL = P.METAL_STEEL
DOOR = (2.4, 1.05, 1.0, 2.1)              # template: (centre, z_c, width, height) — centre filled per door


def door_at(c):
    return (c, DOOR[1], DOOR[2], DOOR[3])


# ── the hall ─────────────────────────────────────────────────────────────

def build_hall():
    make_floor("Hall_Floor", ((HALL_X0 + HALL_X1) / 2.0, (HALL_Y0 + HALL_Y1) / 2.0, 0.0),
               size_x=HALL_X1 - HALL_X0 + 0.4, size_y=HALL_Y1 - HALL_Y0 + 0.4, palette=VINYL)
    # north wall: the gym's double doors, the locker room door
    make_wall_with_openings("Hall_Wall_N", ((HALL_X0 + HALL_X1) / 2.0, HALL_Y1, 0), length=HALL_X1 - HALL_X0,
                            height=HALL_H, axis='X', palette=BLOCK, baseboard_face_sign=-1,
                            openings=[(-10.0, 1.15, 2.2, 2.3), (8.0, 1.05, 1.0, 2.1)])
    # south wall: a door into each room, the lab's at its west end
    # (draft 2) borrowed light: a band of high windows over the lockers into
    # each classroom (whose own outside wall is a band of windows), two per
    # room either side of its clock, clear of its door
    borrowed = [(rc + d, 2.575, 1.6, 0.55) for rc in ((CLASS[0] + CLASS[1]) / 2.0, (ART[0] + ART[1]) / 2.0,
                                                    (LAB[0] + LAB[1]) / 2.0) for d in (-1.6, 1.6)]
    make_wall_with_openings("Hall_Wall_S", ((HALL_X0 + HALL_X1) / 2.0, HALL_Y0, 0), length=HALL_X1 - HALL_X0,
                            height=HALL_H, axis='X', palette=BLOCK, baseboard_face_sign=+1,
                            openings=[door_at(-12.5), door_at(-2.5), door_at(7.5)] + borrowed)
    for k, (bx, bz, bw, bh) in enumerate(borrowed):
        make_window(f"Hall_Borrowed_{k}", (bx, HALL_Y0 + 0.10, bz), width=bw, height=bh, room_dir=+1,
                    see_through=True, cross_mullion=False, trim=False)
    # (draft 2) light at both ends of the hall: the W end is a pair of glazed
    # exit doors under a transom, the E end a tall window over the stair landing
    hy = (HALL_Y0 + HALL_Y1) / 2.0
    make_wall_with_openings("Hall_Wall_W", (HALL_X0, hy, 0), length=HALL_Y1 - HALL_Y0 + 0.2, height=HALL_H, axis='Y',
                            palette=BLOCK, baseboard_face_sign=+1, openings=[(hy, 1.40, 2.0, 2.80)])
    for k, dy in enumerate((-0.5, 0.5)):
        make_window(f"Hall_ExitDoor_{k}", (HALL_X0 + 0.10, hy + dy, 1.05), width=0.92, height=2.06, axis='Y', room_dir=+1,
                    see_through=True, cross_mullion=False, trim=False)
        make_box(f"Hall_ExitDoor_{k}_PushBar", (HALL_X0 + 0.19, hy + dy, 1.00), (0.05, 0.86, 0.06), STEEL)   # end to end, into the stiles
    make_window("Hall_ExitTransom", (HALL_X0 + 0.10, hy, 2.45), width=1.90, height=0.62, axis='Y', room_dir=+1,
                see_through=True, cross_mullion=False, trim=False)
    make_wall_with_openings("Hall_Wall_E", (HALL_X1, hy, 0), length=HALL_Y1 - HALL_Y0 + 0.2, height=HALL_H, axis='Y',
                            palette=BLOCK, baseboard_face_sign=-1, openings=[(hy, 1.95, 1.8, 1.6)])
    make_window("Hall_StairWindow", (HALL_X1 - 0.10, hy, 1.95), width=1.8, height=1.6, axis='Y', room_dir=-1, see_through=True)
    # wall face to wall face: past the N wall it ran into the gym's upper wall
    make_ceiling("Hall_Ceil", ((HALL_X0 + HALL_X1) / 2.0, (HALL_Y0 + HALL_Y1) / 2.0, HALL_H),
                 size_x=HALL_X1 - HALL_X0 - 0.2, size_y=HALL_Y1 - HALL_Y0 - 0.2)
    for k in range(12):
        make_fluorescent_tube_fixture(f"Hall_Light_{k}", (HALL_X0 + 2.0 + k * 4.0, 1.6, HALL_H), length=1.2, width=0.30)
    # lockers both sides, broken by the doors
    def locker_run(side, x0, x1):
        y = HALL_Y1 - 0.30 if side == "N" else HALL_Y0 + 0.30
        n = int((x1 - x0) / 0.38)
        for k in range(n):
            x = x0 + 0.19 + k * 0.38
            make_box(f"Hall_Locker_{side}_{x:.2f}", (x, y, 0.92), (0.36, 0.40, 1.84), LOCKER)   # on the floor
            make_box(f"Hall_Locker_{side}_{x:.2f}_Vent", (x, y + (-0.205 if side == "N" else 0.205), 1.62),
                     (0.24, 0.006, 0.10), (0.16, 0.30, 0.44, 1.0))
            make_box(f"Hall_Locker_{side}_{x:.2f}_Latch", (x + 0.12, y + (-0.21 if side == "N" else 0.21), 1.00),
                     (0.03, 0.01, 0.10), STEEL)
    for a, b in ((-23.6, -16.0), (-13.2, -11.4), (-8.6, 7.2), (8.8, 16.0)):   # the trophy case in the gap
        locker_run("N", a, b)
    for a, b in ((-23.6, -13.3), (-11.7, -3.3), (-1.7, 6.7), (8.3, 11.1), (11.9, 15.5)):   # the fountain in the gap
        locker_run("S", a, b)
    # the trophy case beside the gym doors
    make_box("Trophy_Case", (-14.6, HALL_Y1 - 0.30, 1.10), (2.2, 0.40, 2.0), WOOD_DK)
    make_box("Trophy_Case_Glass", (-14.6, HALL_Y1 - 0.51, 1.25), (2.0, 0.01, 1.4), P.GLASS)
    for k in range(5):
        make_cyl(f"Trophy_{k}", (-15.4 + k * 0.4, HALL_Y1 - 0.30, 0.95 + (k % 2) * 0.55), 0.06, 0.26 + (k % 3) * 0.06,
                 (0.86, 0.70, 0.30, 1.0), segments=8)
    # the stairwell at the east end
    sx = 19.0
    for k in range(10):
        make_box(f"Stair_{k}", (sx + k * 0.28, 1.6, 0.09 + k * 0.17), (0.28, 2.6, 0.18 + k * 0.34 * 0 + 0.02), (0.60, 0.60, 0.58, 1.0))
    make_box("Stair_Rail", (sx + 1.3, 0.35, 1.7), (2.9, 0.05, 0.05), STEEL)
    make_box("Hall_Clock", (0.0, HALL_Y1 - 0.12, 2.55), (0.34, 0.04, 0.34), (0.94, 0.94, 0.90, 1.0))
    make_box("Hall_Banner", (-3.0, HALL_Y1 - 0.11, 2.45), (3.0, 0.01, 0.55), (0.18, 0.36, 0.56, 1.0))
    make_box("Hall_Banner_Text", (-3.0, HALL_Y1 - 0.115, 2.45), (2.4, 0.004, 0.22), (0.94, 0.90, 0.76, 1.0))
    make_box("Hall_Wall_Fountain", (11.5, HALL_Y0 + 0.28, 0.85), (0.50, 0.36, 0.14), STEEL)
    make_traffic_wear("Hall_Wear", [(HALL_X0 + 1.0, 1.6), (HALL_X1 - 1.0, 1.6)], width=1.4,
                      tint=(0.68, 0.66, 0.60, 1.0))


# ── the gym and the hearing ──────────────────────────────────────────────

def build_gym():
    cx, cy = (GYM_X0 + GYM_X1) / 2.0, (HALL_Y1 + GYM_Y1) / 2.0
    w, d = GYM_X1 - GYM_X0, GYM_Y1 - HALL_Y1
    make_floor("Gym_Floor", (cx, cy, 0.0), size_x=w, size_y=d, palette=MAPLE)
    for nm, x in (("Gym_Wall_W", GYM_X0), ("Gym_Wall_E", GYM_X1)):
        make_wall(nm, (x, cy, 0), length=d, height=GYM_H, axis='Y', palette=GYM_WALL,
                  baseboard_face_sign=+1 if x < 0 else -1)
    make_wall_with_openings("Gym_Wall_N", (cx, GYM_Y1, 0), length=w + 0.2, height=GYM_H, axis='X',
                            palette=GYM_WALL, baseboard_face_sign=-1,
                            openings=[(cx - 8.0, 6.2, 4.0, 1.2), (cx, 6.2, 4.0, 1.2), (cx + 8.0, 6.2, 4.0, 1.2)])
    for k, ox in enumerate((-8.0, 0.0, 8.0)):
        make_window(f"Gym_Clerestory_{k}", (cx + ox, GYM_Y1 - 0.10, 6.2), width=4.0, height=1.2, see_through=True)
    make_wall("Gym_Wall_S_Upper", (cx, HALL_Y1, (HALL_H + GYM_H) / 2.0), length=w, height=GYM_H - HALL_H,
              axis='X', palette=GYM_WALL)
    make_box("Gym_Roof", (cx, cy, GYM_H + 0.10), (w + 0.4, d + 0.4, 0.20), (0.36, 0.36, 0.38, 1.0))
    for k in range(6):                                    # the steel trusses
        make_box(f"Gym_Truss_{k}", (GYM_X0 + 2.0 + k * 4.8, cy, GYM_H - 0.40), (0.20, d, 0.50), (0.46, 0.46, 0.48, 1.0))
    for i in range(4):
        for j in range(3):
            x, y = GYM_X0 + 4.0 + i * 6.7, HALL_Y1 + 3.5 + j * 5.5
            make_cyl(f"Gym_HighBay_Lamp_{i}_{j}", (x, y, GYM_H - 0.90), 0.32, 0.30, (0.96, 0.94, 0.86, 1.0), segments=10)
            # the rod runs from the lamp's top to the roof deck (it stopped 15 cm short)
            make_cyl(f"Gym_HighBay_Lamp_{i}_{j}_Rod", (x, y, (GYM_H - 0.75 + GYM_H) / 2.0), 0.012, 0.75, STEEL, segments=6)
    # the court: centre circle, half-court line, keys, boundary
    paint = (0.20, 0.32, 0.52, 1.0)
    ccx, ccy, half = cx, cy, 13.0                          # 26 m: the court fits the 28 m room
    make_box("Court_Line_Half", (ccx, ccy, 0.003), (0.05, 15.0, 0.004), paint)
    for nm, (x, y, sx, sy) in {"S": (ccx, ccy - 7.5, 2 * half, 0.05), "N": (ccx, ccy + 7.5, 2 * half, 0.05),
                               "W": (ccx - half, ccy, 0.05, 15.0), "E": (ccx + half, ccy, 0.05, 15.0)}.items():
        make_box(f"Court_Line_{nm}", (x, y, 0.003), (sx, sy, 0.004), paint)
    for k in range(24):
        a = k * math.tau / 24
        make_box(f"Court_Circle_{k}", (ccx + 1.8 * math.cos(a), ccy + 1.8 * math.sin(a), 0.003), (0.48, 0.05, 0.004), paint)
    for s in (-1, 1):
        make_box(f"Court_Key_{'W' if s < 0 else 'E'}", (ccx + s * (half - 2.9), ccy, 0.002), (5.8, 4.9, 0.003), (0.66, 0.50, 0.30, 1.0))
        bx = ccx + s * (half - 0.4)
        wall_face = (GYM_X0 + 0.10) if s < 0 else (GYM_X1 - 0.10)
        make_box(f"Hoop_Board_{'W' if s < 0 else 'E'}", (bx, ccy, 3.4), (0.04, 1.8, 1.05), (0.94, 0.94, 0.92, 1.0))
        make_cyl(f"Hoop_Rim_{'W' if s < 0 else 'E'}", (bx - s * 0.25, ccy, 3.05), 0.23, 0.02, (0.86, 0.36, 0.14, 1.0), segments=14)
        make_box(f"Hoop_Arm_{'W' if s < 0 else 'E'}", ((bx + wall_face) / 2.0, ccy, 3.9), (abs(wall_face - bx), 0.10, 0.10), STEEL)   # board to wall
    # bleachers pulled out along the south wall
    for r in range(4):                                     # four rows: the hearing's chairs start beyond them
        y = HALL_Y1 + 0.6 + r * 0.6
        make_box(f"Bleacher_Seat_{r}", (cx - 2.0, y, 0.45 + r * 0.42), (20.0, 0.30, 0.06), (0.72, 0.56, 0.32, 1.0))
        rh = 0.45 + r * 0.42                               # floor to the seat (the upper rows hung in the air)
        make_box(f"Bleacher_Riser_{r}", (cx - 2.0, y + 0.18, rh / 2.0), (20.0, 0.04, rh), (0.30, 0.30, 0.32, 1.0))
    # THE HEARING: the board's long table, the podium at centre court, the chairs
    tx, ty = ccx, ccy + 5.0
    make_table("Board_Table", tx, ty, w=7.0, d=0.9, h=0.75, wood=WOOD_DK, top_col=(0.40, 0.30, 0.20, 1.0))
    make_box("Board_Table_Skirt", (tx, ty - 0.46, 0.45), (7.0, 0.02, 0.60), (0.20, 0.30, 0.46, 1.0))
    for k in range(7):
        make_chair(f"Board_Chair_{k}", tx - 3.0 + k * 1.0, ty + 0.75, yaw=math.pi, wood=WOOD_DK)
        make_box(f"Board_Placard_{k}", (tx - 3.0 + k * 1.0, ty - 0.20, 0.80), (0.26, 0.02, 0.10), (0.94, 0.92, 0.86, 1.0))
        make_cyl(f"Board_Mic_{k}", (tx - 3.0 + k * 1.0 + 0.2, ty - 0.10, 0.86), 0.008, 0.20, P.METAL_BLACK, segments=6)
    make_box("Podium", (ccx, ccy, 0.58), (0.60, 0.50, 1.16), WOOD)
    make_box("Podium_Top", (ccx, ccy - 0.05, 1.18), (0.66, 0.46, 0.04), WOOD_DK)
    make_cyl("Podium_Mic", (ccx, ccy + 0.12, 1.36), 0.008, 0.30, P.METAL_BLACK, segments=6)
    for r in range(5):
        for k in range(12):
            if k in (5, 6):
                continue                                   # the aisle to the podium
            make_chair(f"Gallery_Chair_{r}_{k}", ccx - 6.0 + k * 1.05, ccy - 1.5 - r * 0.95, yaw=0.0,
                       wood=(0.30, 0.30, 0.32, 1.0), seat_col=(0.40, 0.40, 0.42, 1.0))
    make_box("Hearing_Banner", (cx, GYM_Y1 - 0.12, 4.4), (8.0, 0.02, 1.0), (0.18, 0.36, 0.56, 1.0))
    make_box("Hearing_Banner_Text", (cx, GYM_Y1 - 0.135, 4.4), (6.6, 0.004, 0.40), (0.94, 0.90, 0.76, 1.0))
    make_box("Scoreboard", (GYM_X0 + 0.15, cy, 4.8), (0.12, 3.2, 1.4), (0.10, 0.10, 0.12, 1.0))
    make_box("Scoreboard_Face", (GYM_X0 + 0.22, cy, 4.8), (0.004, 2.8, 1.0), (0.80, 0.24, 0.14, 1.0))


# ── the locker room ──────────────────────────────────────────────────────

def build_locker_room():
    cx, cy = (LOCK_X0 + LOCK_X1) / 2.0, (HALL_Y1 + LOCK_Y1) / 2.0
    w, d = LOCK_X1 - LOCK_X0, LOCK_Y1 - HALL_Y1
    make_floor("Lock_Floor", (cx, cy, 0.0), size_x=w, size_y=d, palette={"vinyl": (0.62, 0.60, 0.56, 1.0), "seam": (0.48, 0.46, 0.44, 1.0)})
    make_wall("Lock_Wall_E", (LOCK_X1, cy, 0), length=d, height=ROOM_H, axis='Y', palette=BLOCK, baseboard_face_sign=-1)
    make_wall("Lock_Wall_N", (cx, LOCK_Y1, 0), length=w + 0.2, height=ROOM_H, axis='X', palette=BLOCK, baseboard_face_sign=-1)
    make_ceiling("Lock_Ceil", (cx, cy, ROOM_H), size_x=w, size_y=d)
    for k in range(3):
        make_fluorescent_tube_fixture(f"Lock_Light_{k}", (LOCK_X0 + 2.0 + k * 3.2, cy, ROOM_H), length=1.2, width=0.30)
    for row in range(3):
        y = HALL_Y1 + 1.8 + row * 2.4
        for k in range(18):
            x = LOCK_X0 + 1.4 + k * 0.40
            make_box(f"Lock_Locker_{row}_{k}", (x, y, 0.92), (0.38, 0.46, 1.84), (0.56, 0.20, 0.16, 1.0))   # on the floor
        make_box(f"Lock_Bench_{row}", (LOCK_X0 + 4.8, y - 0.95, 0.43), (7.0, 0.30, 0.05), WOOD)
        for k in range(4):
            make_box(f"Lock_Bench_{row}_Leg_{k}", (LOCK_X0 + 1.8 + k * 2.0, y - 0.95, 0.21), (0.05, 0.24, 0.40), STEEL)
    make_box("Coach_Office_Window", (LOCK_X1 - 0.12, cy + 1.6, 1.6), (0.02, 2.2, 1.0), P.GLASS)
    make_box("Coach_Whiteboard", (LOCK_X0 + 0.12, cy, 1.5), (0.02, 2.4, 1.1), (0.94, 0.94, 0.92, 1.0))
    for k, (a, b) in enumerate([((0.3, 0.2), (1.0, -0.3)), ((-0.6, 0.3), (0.0, -0.2))]):   # the X's and O's
        make_box(f"Coach_Play_{k}", (LOCK_X0 + 0.115, cy + a[0], 1.5 + a[1]), (0.004, 0.22, 0.03), (0.16, 0.20, 0.44, 1.0))


# ── the south rooms ──────────────────────────────────────────────────────

def south_room(prefix, x0, x1, door_c, palette=WALL):
    cx, cy = (x0 + x1) / 2.0, (ROOM_Y0 + HALL_Y0) / 2.0
    w, d = x1 - x0, HALL_Y0 - ROOM_Y0
    make_floor(f"{prefix}_Floor", (cx, cy, 0.0), size_x=w, size_y=d, palette=VINYL)
    make_wall(f"{prefix}_Wall_W", (x0, cy, 0), length=d, height=ROOM_H, axis='Y', palette=palette, baseboard_face_sign=+1)
    make_wall(f"{prefix}_Wall_E", (x1, cy, 0), length=d, height=ROOM_H, axis='Y', palette=palette, baseboard_face_sign=-1)
    # (draft 2, 2026-10-20, the Deck: "interiors need more windows") a school's
    # outside wall is a BAND of tall windows, not three holes: four 2.1 m bays
    # on 2.4 m centres, sill at ~0.75 m, head at ~2.65 m
    wins = [(cx + (k - 1.5) * 2.4, 1.70, 2.1, 1.9) for k in range(4)]
    make_wall_with_openings(f"{prefix}_Wall_S", (cx, ROOM_Y0, 0), length=w + 0.2, height=ROOM_H, axis='X',
                            palette=palette, baseboard_face_sign=+1, openings=wins)
    for k, (wx, wz, ww, wh) in enumerate(wins):
        make_window(f"{prefix}_Window_{k}", (wx, ROOM_Y0 + 0.10, wz), width=ww, height=wh, see_through=True, room_dir=+1)
    make_ceiling(f"{prefix}_Ceil", (cx, cy, ROOM_H), size_x=w, size_y=d)
    for i in range(2):
        for j in range(3):
            make_fluorescent_tube_fixture(f"{prefix}_Light_{i}_{j}", (x0 + w * (0.3 + 0.4 * i), ROOM_Y0 + 1.6 + j * 2.8, ROOM_H),
                                          length=1.2, width=0.30)
    make_smoke_detector(f"{prefix}_Smoke", (cx, cy, ROOM_H))
    make_box(f"{prefix}_Clock", (cx, HALL_Y0 - 0.12, 2.45), (0.30, 0.04, 0.30), (0.94, 0.94, 0.90, 1.0))
    make_light_switch(f"{prefix}_Switch", (door_c + 0.7, HALL_Y0), axis='X', face_sign=-1, aged=True)
    make_wall_outlet(f"{prefix}_Outlet", (x0, cy), axis='Y', face_sign=1, aged=True)
    return cx, cy, w, d


def build_classroom():
    x0, x1 = CLASS
    cx, cy, w, d = south_room("Class", x0, x1, -12.5)
    make_box("Class_Chalkboard", (x0 + 0.12, cy, 1.45), (0.03, 4.8, 1.2), (0.16, 0.24, 0.20, 1.0))
    make_box("Class_Chalk_Tray", (x0 + 0.17, cy, 0.84), (0.08, 4.8, 0.03), (0.60, 0.58, 0.54, 1.0))
    make_box("Class_Chalk_Words", (x0 + 0.138, cy - 0.6, 1.70), (0.002, 2.2, 0.06), (0.86, 0.86, 0.82, 1.0))
    make_box("Class_Chalk_Words_2", (x0 + 0.138, cy - 0.2, 1.55), (0.002, 2.8, 0.05), (0.86, 0.86, 0.82, 1.0))
    make_table("Teacher_Desk", x0 + 1.4, cy - 2.6, w=1.5, d=0.75, h=0.76, wood=WOOD_DK)
    make_box("Teacher_Desk_Papers", (x0 + 1.3, cy - 2.6, 0.78), (0.30, 0.24, 0.04), P.PAPER)
    make_box("Teacher_Pink_Handouts", (x0 + 1.7, cy - 2.5, 0.775), (0.22, 0.28, 0.03), (0.94, 0.66, 0.70, 1.0))   # "Character Suitcase"
    for r in range(5):
        for k in range(6):
            sx, sy = x0 + 3.0 + r * 1.35, cy - 3.2 + k * 1.15
            make_box(f"Class_Desk_{r}_{k}_Top", (sx, sy, 0.72), (0.60, 0.46, 0.03), (0.70, 0.60, 0.44, 1.0))
            make_box(f"Class_Desk_{r}_{k}_Leg", (sx, sy, 0.355), (0.04, 0.04, 0.71), STEEL)
            make_box(f"Class_Desk_{r}_{k}_Seat", (sx + 0.42, sy, 0.44), (0.36, 0.36, 0.03), (0.30, 0.40, 0.56, 1.0))
            make_box(f"Class_Desk_{r}_{k}_Seat_Post", (sx + 0.42, sy, 0.212), (0.04, 0.04, 0.425), STEEL)
            make_box(f"Class_Desk_{r}_{k}_Back", (sx + 0.60, sy, 0.60), (0.03, 0.36, 0.30), (0.30, 0.40, 0.56, 1.0))
    # the reading shelf by the door ("hungry reader types huddled close to the door looking for a fix off the shelf")
    for sd in (-1, 1):                                     # the shelf's sides, floor to top, on the wall
        make_box(f"Class_Shelf_Side_{sd:+d}", (x1 - 1.2 + sd * 0.91, HALL_Y0 - 0.25, 0.70), (0.02, 0.30, 1.40), WOOD)
    for b in range(4):
        make_box(f"Class_Shelf_{b}", (x1 - 1.2, HALL_Y0 - 0.25, 0.20 + b * 0.36), (1.8, 0.30, 0.02), WOOD)
        for k in range(14):
            make_box(f"Class_Shelf_{b}_Book_{k}", (x1 - 2.0 + k * 0.11, HALL_Y0 - 0.32, 0.31 + b * 0.36), (0.07, 0.20, 0.20),
                     P.SNACK_TINTS[(k + b) % len(P.SNACK_TINTS)])
    make_box("Class_Flag", (x1 - 0.11, cy + 2.6, 2.2), (0.02, 0.50, 0.30), (0.70, 0.20, 0.18, 1.0))


def build_art_room():
    x0, x1 = ART
    cx, cy, w, d = south_room("Art", x0, x1, -2.5, palette={"wall": (0.88, 0.84, 0.72, 1.0), "baseboard": (0.30, 0.30, 0.32, 1.0)})
    for r in range(3):
        for k in range(2):
            tx, ty = x0 + 2.2 + k * 4.0, cy - 2.6 + r * 2.4
            make_table(f"Art_Table_{r}_{k}", tx, ty, w=2.4, d=1.0, h=0.80, wood=WOOD, top_col=(0.62, 0.56, 0.48, 1.0))
            for s in range(4):
                make_box(f"Art_Stool_{r}_{k}_{s}", (tx - 0.9 + s * 0.6, ty - 0.75, 0.33), (0.32, 0.32, 0.66), (0.40, 0.40, 0.42, 1.0))
            for s, col in enumerate([(0.86, 0.30, 0.20, 1.0), (0.26, 0.46, 0.70, 1.0), (0.92, 0.80, 0.30, 1.0)]):
                make_box(f"Art_Paint_{r}_{k}_{s}", (tx - 0.6 + s * 0.5, ty + 0.1, 0.82), (0.08, 0.08, 0.04), col)
    for k in range(4):                                     # easels along the E wall
        ex, ey = x1 - 0.9, cy - 3.0 + k * 1.8
        make_box(f"Art_Easel_{k}_Leg_F", (ex - 0.25, ey, 0.85), (0.04, 0.04, 1.70), WOOD)
        make_box(f"Art_Easel_{k}_Leg_B", (ex + 0.30, ey, 0.80), (0.04, 0.04, 1.60), WOOD)
        make_box(f"Art_Easel_{k}_Canvas", (ex - 0.22, ey, 1.25), (0.03, 0.60, 0.75), (0.94, 0.92, 0.86, 1.0))
    make_box("Art_Sink_Counter", (x0 + 0.40, cy + 2.0, 0.45), (0.60, 2.2, 0.90), (0.62, 0.58, 0.52, 1.0))
    make_box("Art_Sink", (x0 + 0.40, cy + 2.0, 0.89), (0.40, 0.60, 0.04), STEEL)
    make_box("Art_Drying_Rack", (x0 + 0.40, cy - 1.0, 0.70), (0.50, 1.10, 1.40), (0.34, 0.34, 0.36, 1.0))
    for k in range(8):                                     # student work pinned up (HeroArt in draft 2)
        make_box(f"Art_Work_{k}", (x0 + 1.0 + k * 1.0, HALL_Y0 - 0.102, 1.75 + (k % 2) * 0.25), (0.60, 0.004, 0.45),
                 P.SNACK_TINTS[k % len(P.SNACK_TINTS)])


def build_lab():
    x0, x1 = LAB
    cx, cy, w, d = south_room("Lab", x0, x1, 7.5)
    for r in range(3):
        y = cy - 2.8 + r * 2.4
        make_box(f"Lab_Bench_{r}", (cx, y, 0.73), (7.6, 0.80, 0.04), (0.84, 0.82, 0.76, 1.0))
        for k in range(8):
            x = x0 + 1.4 + k * 0.95
            make_box(f"Lab_Bench_{r}_Leg_{k}", (x, y + 0.30, 0.36), (0.04, 0.04, 0.70), STEEL)
            make_chamfer_box(f"Lab_PC_{r}_{k}", (x, y + 0.18, 0.91), (0.40, 0.08, 0.32), (0.86, 0.84, 0.78, 1.0), chamfer=0.01)   # on the bench
            make_box(f"Lab_PC_{r}_{k}_Screen", (x, y + 0.138, 0.92), (0.34, 0.004, 0.25), (0.22, 0.38, 0.62, 1.0))
            make_box(f"Lab_PC_{r}_{k}_Keys", (x, y - 0.15, 0.76), (0.40, 0.14, 0.02), (0.84, 0.82, 0.76, 1.0))
            make_chair(f"Lab_Chair_{r}_{k}", x, y - 0.65, yaw=0.0, wood=(0.26, 0.26, 0.28, 1.0), seat_col=(0.30, 0.40, 0.56, 1.0))
    # "a sign hung up over one of the children that says, 'We see everything as inspiration!'"
    make_box("Lab_Sign", (cx, cy + 0.6, 2.35), (2.4, 0.02, 0.50), (0.96, 0.92, 0.40, 1.0))
    make_box("Lab_Sign_Text", (cx, cy + 0.585, 2.35), (2.0, 0.004, 0.18), (0.18, 0.24, 0.50, 1.0))
    make_cyl("Lab_Sign_Wire_W", (cx - 1.1, cy + 0.6, 2.80), 0.004, 0.42, STEEL, segments=4)   # sign to ceiling
    make_cyl("Lab_Sign_Wire_E", (cx + 1.1, cy + 0.6, 2.80), 0.004, 0.42, STEEL, segments=4)


def main():
    clear_scene()
    build_hall()
    build_gym()
    build_locker_room()
    build_classroom()
    build_art_room()
    build_lab()
    # the grounds beyond the south windows, the lot beyond the gym's clerestory
    make_view("View_S", "S", ROOM_Y0, 1.0, kind="front", ground_z=0.0, span=48.0, seed=5)
    make_view("View_N", "N", GYM_Y1, -10.0, kind="back", ground_z=0.0, span=40.0, seed=9)
    make_view("View_W", "W", HALL_X0, (HALL_Y0 + HALL_Y1) / 2.0, kind="side", ground_z=0.0, span=20.0, seed=3)    # (draft 2)
    make_view("View_E", "E", HALL_X1, (HALL_Y0 + HALL_Y1) / 2.0, kind="side", ground_z=0.0, span=20.0, seed=6)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/small_wood_high.glb"))
    print(f"\n[build_small_wood_high] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
