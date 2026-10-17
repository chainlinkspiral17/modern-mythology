"""sleep_lab — vol 3's sleep study at Caltech, and the four-screen room in
Portland (draft 1, 2026-10-17).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
Two places in one GLB, as the vol 2 ranch keeps its second house: they are
years and states apart and share nothing but this file.

THE SLEEP LAB (origin) — "in the new building, Moore, in the Koch lab", in
"the basement's basement": no windows, no outside.
  "The sleep study room is a small office with two beds."
                                       → Bed_A / Bed_B, heads to the N wall
  "There is a bookshelf between two beds, stacked full of good reads."
  "The spines are cracked white from reading, read and reread."
                                       → Bookshelf, its books' white creases
  "A portable CD player occupies part of one shelf."      → CD_Player
  "Between the Wittgenstein and the Powers a white binder, no label on the
   spine."                             → Binder_IRIS
  "a deathly heavy black curtain is pulled around the computer"
                                       → Curtain_* round the NE corner; the
                                         Sun box, its CRT and the
  "The chair is intentionally uncomfortable"              → Chair_Hard
  "The machinery under the curtain looks simple but expensive. It hums."
                                       → Machine_Rack (a plain box: the text
                                         gives it no form; no electrodes)
  "A Kermit doll sits on top a computer monitor his eyes painted bloodshot
   red holding a real joint in his green felt hand."      → Kermit_* on the
                                         test computer's CRT (E wall desk)
  "Altered States with William Hurt, the David Lynch film Lost Highway."
                                       → Poster_AlteredStates (W wall),
                                         Poster_LostHighway (N wall)
  "They play with blocks" / "her note-pad" / "She takes his blood pressure"
                                       → Blocks_*, Notepad, BP_Cuff
  "She shows Andy the bathroom, shower."                  → the bathroom
                                         through the W door
  "so the researcher can watch real time from the next room"
                                       → Door_NextRoom (E wall, shut)
  "The hallways leading to the lab are lined by long empty aquariums once
   housing intricate families of electric eels."          → the corridor
                                         past the entry door, Aquarium_*
The entry door is open in the work views and shut at night (`__<preset>`
meshes): after lights-out the light is the curtain's glow.

THE FOUR-SCREEN ROOM (x 31..49) — the back room of a vacant Portland gallery.
  "We are locked in a large room, each wall taller than normal. White."
                                       → 18 x 18 m, walls 7 m
  "I saw an island of leather executive swivel chairs, maybe eighty in
   total." / "They were securely bolted down"
                                       → Island_Stock: 81 chairs, each on a
                                         bolted plate, each turned its own way
  "There are four projectors that must be on the other side of the walls."
                                       → none in the room; in the show view
                                         each wall carries its picture
                                         (Screen_*__four_screens_show)
  "Then a beam came down out of the dark at a slant, from very high up, from
   a machine on a long jointed stalk, covered in tiny lights like little
   eyes."  (meld_seam_2_3 only)        → Stalk_*__four_screens_beam, hidden in
                                         the ch4 views

Blender: x east, y north, z up; Godot (x, z, -y).

DRAFT 2 targets: the observation room behind Door_NextRoom (Jane "just out
of sight on the other side of the curtain, watching her numbers"); the tunnel
run from Dabney to Moore as its own set (graffiti, rails, radiation doors,
the racquetball room's lanterns) — the corridor here is its last 9 m; the
gallery's front lobby (vol3_vacant_gallery_lobby: glass doors, the unswept
floor, the ice-and-beer trashcan) through the double doors; the beam as a
visible shaft (a volumetric fog pass) rather than a pool; book spines
lettered as the text spells them ("Deridan", "Vollman"); Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_lathe, make_rot_box, make_blob, make_tube,
                             join_stock, export_glb)
from _props.structure import make_floor, make_wall, make_ceiling, make_wall_with_openings
from _props.furniture import make_bed, make_chair, make_lamp
from _props.safety import make_fluorescent_tube_fixture
from _props.detail import make_wall_outlet, make_light_switch

# ── the sleep lab ──────────────────────────────────────────────────────
W, D, CEIL, T = 6.0, 5.0, 2.75, 0.20
X0, X1 = -W / 2.0, W / 2.0
PAL = {"wall": (0.80, 0.78, 0.72, 1.0), "baseboard": (0.30, 0.28, 0.26, 1.0)}
CARPET = (0.36, 0.34, 0.38, 1.0); CARPET_SEAM = (0.30, 0.28, 0.32, 1.0)
OAK = (0.56, 0.42, 0.28, 1.0); OAK_DARK = (0.38, 0.28, 0.18, 1.0)
LAB_GREY = (0.62, 0.62, 0.60, 1.0); BEIGE = (0.80, 0.76, 0.66, 1.0)
CURTAIN = (0.06, 0.06, 0.07, 1.0)
FELT = (0.30, 0.62, 0.24, 1.0)
DOOR = (0.58, 0.48, 0.36, 1.0)

ENTRY_X, NEXT_Y, BATH_Y = -1.30, 0.62, 1.40
CUR_X, CUR_Y = 1.70, 3.20               # the curtain's corner (it runs N to the wall, E to the wall)
WORK = "__sleep_lab_entry__sleep_lab_desk"

# ── the four-screen room ──────────────────────────────────────────────
GX0, GX1, GD, GH = 31.0, 49.0, 18.0, 7.0
GCX, GCY = (GX0 + GX1) / 2.0, GD / 2.0
WHITE = (0.90, 0.90, 0.88, 1.0)
LEATHER = [(0.26, 0.16, 0.11, 1.0), (0.36, 0.22, 0.14, 1.0), (0.16, 0.15, 0.15, 1.0), (0.44, 0.28, 0.18, 1.0)]


def crt(prefix, x, y, z, face="-X", body=BEIGE, glow=(0.46, 0.56, 0.62, 1.0)):
    """A 17-inch CRT on its own base, its screen toward `face`."""
    sx = -1.0 if face == "-X" else 1.0
    make_chamfer_box(f"{prefix}_Body", (x, y, z + 0.215), (0.42, 0.40, 0.37), body, chamfer=0.03)
    make_box(f"{prefix}_Bezel", (x + sx * 0.214, y, z + 0.225), (0.008, 0.36, 0.31), (body[0] * 0.9, body[1] * 0.9, body[2] * 0.9, 1.0))
    make_box(f"{prefix}_Screen", (x + sx * 0.219, y, z + 0.228), (0.004, 0.30, 0.24), glow)
    make_box(f"{prefix}_Base", (x, y, z + 0.015), (0.24, 0.24, 0.03), body)


def build_lab_shell():
    make_floor("Floor", (0.0, D / 2.0, 0.0), size_x=W + 0.4, size_y=D + 0.4, palette={"vinyl": CARPET, "seam": CARPET_SEAM})
    make_ceiling("Ceil", (0.0, D / 2.0, CEIL), size_x=W + 0.4, size_y=D + 0.4, with_grid=True, with_stains=True,
                 palette={"tile": (0.84, 0.82, 0.78, 1.0)})
    make_wall("Wall_N", (0.0, D, 0), length=W + 0.4, height=CEIL, thickness=T, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_wall_with_openings("Wall_W", (X0, D / 2.0, 0), length=D + 0.4, height=CEIL, thickness=T, axis='Y', palette=PAL,
                            baseboard_face_sign=+1, openings=[(BATH_Y, 1.0, 0.80, 2.0)])
    make_wall_with_openings("Wall_E", (X1, D / 2.0, 0), length=D + 0.4, height=CEIL, thickness=T, axis='Y', palette=PAL,
                            baseboard_face_sign=-1, openings=[(NEXT_Y, 1.0, 0.86, 2.0)])
    # the S wall runs on west past the bathroom: the corridor's north side
    make_wall_with_openings("Wall_S", (-1.0, 0.0, 0), length=8.4, height=CEIL, thickness=T, axis='X', palette=PAL,
                            baseboard_face_sign=+1, openings=[(ENTRY_X, 1.0, 0.90, 2.0)])
    make_fluorescent_tube_fixture("Fluor_Lab", (0.0, 2.2, CEIL), length=1.20, width=0.60)
    # the entry door: open into the room in the work views, shut at night
    make_box("Door_Entry_Open" + WORK, (ENTRY_X - 0.43, 0.10 + 0.44, 1.0), (0.04, 0.86, 2.0), DOOR)
    make_cyl("Door_Entry_Open_Knob" + WORK, (ENTRY_X - 0.39, 0.86, 0.98), 0.026, 0.05, (0.70, 0.66, 0.56, 1.0), axis='X', segments=10)
    make_box("Door_Entry_Shut__sleep_lab_night", (ENTRY_X, 0.0, 1.0), (0.86, 0.05, 2.0), DOOR)
    make_cyl("Door_Entry_Shut_Knob__sleep_lab_night", (ENTRY_X + 0.34, 0.045, 0.98), 0.026, 0.04, (0.70, 0.66, 0.56, 1.0),
             axis='Y', segments=10)
    # the next room's door (E wall), shut: the researcher watches from there
    make_box("Door_NextRoom", (X1, NEXT_Y, 1.0), (0.05, 0.82, 2.0), DOOR)
    make_cyl("Door_NextRoom_Knob", (X1 - 0.045, NEXT_Y + 0.32, 0.98), 0.026, 0.04, (0.70, 0.66, 0.56, 1.0), axis='X', segments=10)
    make_light_switch("Switch_Entry", (ENTRY_X - 0.65, 0.0), axis='X', face_sign=1)
    make_wall_outlet("Outlet_Beds", (-1.40, D), axis='X', face_sign=-1)
    make_wall_outlet("Outlet_Desk", (X1, 2.70), axis='Y', face_sign=-1)


def build_beds_and_shelf():
    # two beds, heads to the N wall, the bookshelf between them
    make_bed("Bed_A", -1.35, D - 0.10 - 0.98, head="+Y", w=0.99, d=1.95, blanket_col=(0.34, 0.36, 0.48, 1.0),
             sheet_col=(0.90, 0.88, 0.82, 1.0))
    make_bed("Bed_B", 0.55, D - 0.10 - 0.98, head="+Y", w=0.99, d=1.95, blanket_col=(0.50, 0.30, 0.26, 1.0),
             sheet_col=(0.90, 0.88, 0.82, 1.0))
    sx, sy, sw, sd, sh = -0.40, D - 0.10 - 0.16, 0.80, 0.30, 1.50
    make_box("Bookshelf_Side_L", (sx - sw / 2.0 + 0.01, sy, sh / 2.0), (0.02, sd, sh), OAK_DARK)
    make_box("Bookshelf_Side_R", (sx + sw / 2.0 - 0.01, sy, sh / 2.0), (0.02, sd, sh), OAK_DARK)
    make_box("Bookshelf_Back", (sx, sy + sd / 2.0 - 0.005, sh / 2.0), (sw, 0.01, sh), OAK_DARK)
    shelves = (0.06, 0.42, 0.78, 1.14, 1.49)
    for k, z in enumerate(shelves):
        make_box(f"Bookshelf_Board_{k}", (sx, sy, z), (sw - 0.04, sd, 0.02), OAK)
    spines = [(0.20, 0.22, 0.30), (0.46, 0.18, 0.16), (0.16, 0.28, 0.24), (0.62, 0.56, 0.40), (0.12, 0.12, 0.14),
              (0.36, 0.30, 0.42), (0.70, 0.66, 0.58), (0.28, 0.34, 0.44)]
    for k in range(4):
        z0 = shelves[k] + 0.01
        x = sx - sw / 2.0 + 0.04
        n = 0
        while x < sx + sw / 2.0 - 0.05:
            # the CD player takes the right of the second shelf; the binder
            # stands in the third, between the Wittgenstein and the Powers
            if k == 1 and x > sx + 0.06:
                break
            t = 0.022 + ((k * 7 + n * 3) % 4) * 0.008
            h = 0.20 + ((k * 5 + n * 11) % 5) * 0.022
            col = spines[(k * 3 + n) % len(spines)]
            if k == 2 and n == 7:
                make_box("Binder_IRIS", (x + 0.022, sy - 0.01, z0 + 0.15), (0.044, 0.26, 0.30), (0.94, 0.94, 0.92, 1.0))
                x += 0.050
                n += 1
                continue
            make_box(f"Bookshelf_Stock_Book_{k}_{n}", (x + t / 2.0, sy - 0.01, z0 + h / 2.0), (t, 0.20, h), (*col, 1.0))
            # "cracked white from reading": pale creases down the spine
            for c in range(2):
                make_box(f"Bookshelf_Stock_Crease_{k}_{n}_{c}", (x + t / 2.0, sy - 0.111, z0 + h * (0.30 + 0.35 * c)),
                         (t * 0.8, 0.002, 0.006), (0.90, 0.88, 0.82, 1.0))
            x += t + 0.003
            n += 1
    # the portable CD player, its lid, a few jewel cases
    make_cyl("CD_Player", (sx + 0.22, sy - 0.02, shelves[1] + 0.025), 0.068, 0.03, (0.70, 0.72, 0.74, 1.0), segments=16)
    make_cyl("CD_Player_Lid", (sx + 0.22, sy - 0.02, shelves[1] + 0.042), 0.058, 0.004, (0.40, 0.42, 0.46, 1.0), segments=16)
    for k in range(3):
        make_box(f"Jewel_Case_{k}", (sx + 0.22, sy + 0.08, shelves[1] + 0.017 + k * 0.011), (0.14, 0.12, 0.010),
                 (0.66, 0.70, 0.74, 1.0))
    make_box("Rug_Beds", (-0.40, 3.30, 0.006), (1.20, 1.60, 0.012), (0.52, 0.36, 0.28, 1.0))
    # the floor lamp in the W corner by Bed_A: the room's warm light at work
    make_lamp("Lamp_Floor", X0 + 0.45, D - 0.45, base_z=0.0, h=1.45)
    # posters: Altered States on the W wall, Lost Highway above Bed_B
    px = X0 + 0.104
    make_box("Poster_AlteredStates", (px, 3.40, 1.62), (0.006, 0.68, 1.02), (0.94, 0.92, 0.86, 1.0))
    make_box("Poster_AlteredStates_Field", (px + 0.004, 3.40, 1.66), (0.004, 0.62, 0.86), (0.10, 0.06, 0.08, 1.0))
    make_box("Poster_AlteredStates_Figure", (px + 0.007, 3.40, 1.72), (0.004, 0.16, 0.50), (0.90, 0.52, 0.20, 1.0))
    make_box("Poster_AlteredStates_Halo", (px + 0.006, 3.40, 1.76), (0.004, 0.40, 0.56), (0.56, 0.20, 0.14, 1.0))
    make_box("Poster_AlteredStates_Title", (px + 0.007, 3.40, 1.25), (0.004, 0.50, 0.06), (0.92, 0.88, 0.80, 1.0))
    py = D - 0.104
    make_box("Poster_LostHighway", (0.55, py, 1.86), (0.68, 0.006, 1.00), (0.08, 0.08, 0.09, 1.0))
    for k in range(5):
        w = 0.03 + k * 0.012
        make_box(f"Poster_LostHighway_Line_{k}", (0.55, py - 0.004, 1.50 + k * 0.10), (w, 0.004, 0.05 - k * 0.006),
                 (0.92, 0.80, 0.30, 1.0))
    make_box("Poster_LostHighway_Title", (0.55, py - 0.004, 2.24), (0.52, 0.004, 0.07), (0.78, 0.16, 0.12, 1.0))


def build_curtain_station():
    """The NE corner behind the black curtain: the Sun box, its monitor, the
    humming machine, the hard chair. The curtain hangs from a ceiling track
    and stands a hand's width open at its corner."""
    make_box("Curtain_Track_W", (CUR_X, (CUR_Y + D) / 2.0, CEIL - 0.02), (0.03, D - CUR_Y, 0.03), (0.30, 0.30, 0.32, 1.0))
    make_box("Curtain_Track_S", ((CUR_X + X1) / 2.0, CUR_Y, CEIL - 0.02), (X1 - CUR_X, 0.03, 0.03), (0.30, 0.30, 0.32, 1.0))
    h = CEIL - 0.06
    # folds: panels turned alternately a little, so the cloth reads heavy
    y = D - 0.12
    k = 0
    while y > CUR_Y + 0.30:
        make_rot_box(f"Curtain_W_{k}", (CUR_X + (0.03 if k % 2 else -0.03), y - 0.09, h / 2.0 + 0.02), (0.04, 0.20, h),
                     CURTAIN, yaw=(0.30 if k % 2 else -0.30))
        y -= 0.17
        k += 1
    x = X1 - 0.12
    k = 0
    while x > CUR_X + 0.22:
        make_rot_box(f"Curtain_S_{k}", (x - 0.09, CUR_Y + (0.03 if k % 2 else -0.03), h / 2.0 + 0.02), (0.20, 0.04, h),
                     CURTAIN, yaw=(0.30 if k % 2 else -0.30))
        x -= 0.17
        k += 1
    # inside: the researcher's desk against the N wall, the Sun box and its
    # CRT, the rack of the machinery, the chair
    dx, dy = (CUR_X + X1) / 2.0 + 0.10, D - 0.10 - 0.36
    make_box("Station_Desk_Top", (dx, dy, 0.73), (1.00, 0.70, 0.03), LAB_GREY)
    for s in (-1, 1):
        make_box(f"Station_Desk_Leg_{s:+d}", (dx + s * 0.47, dy, 0.36), (0.04, 0.66, 0.72), LAB_GREY)
    make_box("Sun_Box", (dx - 0.14, dy + 0.10, 0.775), (0.42, 0.40, 0.06), (0.28, 0.28, 0.30, 1.0))
    crt("Sun_CRT", dx - 0.14, dy + 0.10, 0.805, face="-X", body=(0.30, 0.30, 0.32, 1.0), glow=(0.50, 0.62, 0.78, 1.0))
    make_box("Sun_Keyboard", (dx - 0.06, dy - 0.24, 0.755), (0.16, 0.44, 0.02), (0.24, 0.24, 0.26, 1.0))
    make_box("Machine_Rack", (X1 - 0.10 - 0.30, CUR_Y + 0.55, 0.60), (0.56, 0.60, 1.20), (0.18, 0.18, 0.20, 1.0))
    for k in range(6):
        make_box(f"Machine_Rack_LED_{k}", (X1 - 0.10 - 0.585, CUR_Y + 0.35 + k * 0.08, 1.02), (0.004, 0.02, 0.012),
                 ((0.40, 0.96, 0.46, 1.0) if k % 3 else (0.98, 0.56, 0.20, 1.0)))
    for k in range(4):
        make_box(f"Machine_Rack_Vent_{k}", (X1 - 0.10 - 0.585, CUR_Y + 0.55, 0.30 + k * 0.10), (0.004, 0.44, 0.03),
                 (0.10, 0.10, 0.11, 1.0))
    # "intentionally uncomfortable": a hard steel-and-plywood stool-chair
    make_chair("Chair_Hard", dx - 0.62, dy - 0.10, yaw=-math.pi / 2.0, wood=(0.46, 0.44, 0.40, 1.0),
               seat_col=(0.54, 0.46, 0.34, 1.0), seat_h=0.46, w=0.38)


def build_test_desk():
    """The E wall, south of the curtain: the test computer with Kermit on
    its monitor, the blocks, the note-pad, the blood-pressure cuff."""
    dx, dy, dl = X1 - 0.10 - 0.36, 1.90, 1.40
    make_box("Test_Desk_Top", (dx, dy, 0.74), (0.72, dl, 0.03), OAK)
    for s in (-1, 1):
        make_box(f"Test_Desk_Panel_{s:+d}", (dx, dy + s * (dl / 2.0 - 0.02), 0.365), (0.68, 0.03, 0.725), OAK_DARK)
    make_box("Test_Desk_Modesty", (dx + 0.32, dy, 0.48), (0.02, dl - 0.08, 0.50), OAK_DARK)
    crt("Test_CRT", dx + 0.10, dy + 0.30, 0.755)
    make_box("Test_Tower", (dx + 0.06, dy + 0.62, 0.975), (0.42, 0.18, 0.44), BEIGE)
    make_box("Test_Keyboard", (dx - 0.16, dy + 0.30, 0.765), (0.16, 0.46, 0.025), BEIGE)
    make_box("Test_Mouse", (dx - 0.16, dy + 0.02, 0.765), (0.10, 0.06, 0.03), BEIGE)
    # Kermit on the monitor: felt body, legs over the front edge, the head,
    # the eyes painted bloodshot, the joint in his hand
    kx, ky, kz = dx + 0.10, dy + 0.30, 0.755 + 0.40
    make_chamfer_box("Kermit_Body", (kx + 0.02, ky, kz + 0.07), (0.07, 0.10, 0.14), FELT, chamfer=0.02)
    for s in (-1, 1):
        make_rot_box(f"Kermit_Leg_{s:+d}", (kx - 0.12, ky + s * 0.03, kz + 0.01), (0.20, 0.025, 0.025), FELT, pitch=0.35)
        make_rot_box(f"Kermit_Arm_{s:+d}", (kx - 0.03, ky + s * 0.065, kz + 0.10), (0.11, 0.022, 0.022), FELT, pitch=0.5)
    make_blob("Kermit_Head", (kx + 0.01, ky, kz + 0.19), 0.06, FELT, noise=0.05, seed=3)
    for s in (-1, 1):
        make_blob(f"Kermit_Eye_{s:+d}", (kx - 0.025, ky + s * 0.026, kz + 0.235), 0.022, (0.96, 0.82, 0.80, 1.0), noise=0.0, seed=s + 5)
        make_box(f"Kermit_Eye_Red_{s:+d}", (kx - 0.046, ky + s * 0.026, kz + 0.236), (0.003, 0.016, 0.012), (0.86, 0.12, 0.10, 1.0))
    make_rot_box("Kermit_Collar", (kx + 0.01, ky, kz + 0.145), (0.10, 0.13, 0.015), FELT, yaw=0.785)
    make_cyl("Kermit_Joint", (kx - 0.10, ky + 0.085, kz + 0.07), 0.004, 0.06, (0.94, 0.92, 0.86, 1.0), axis='X', segments=6)
    # the blocks, the note-pad and pen, the cuff
    for k in range(6):
        stacked = k == 5       # one block up on another: the timed assembly half done
        make_box(f"Blocks_{k}", (dx - 0.18 + ((1 if stacked else k) % 3) * 0.06, dy - 0.42 + (0 if stacked else k // 3) * 0.07,
                                 0.775 + (0.04 if stacked else 0.0)),
                 (0.04, 0.04, 0.04), ((0.84, 0.24, 0.20, 1.0), (0.94, 0.94, 0.90, 1.0))[k % 2])
    make_box("Notepad", (dx - 0.20, dy - 0.10, 0.759), (0.16, 0.22, 0.008), (0.96, 0.92, 0.62, 1.0))
    make_cyl("Notepad_Pen", (dx - 0.20, dy - 0.02, 0.766), 0.004, 0.14, (0.16, 0.20, 0.50, 1.0), axis='Y', segments=6)
    make_box("BP_Cuff", (dx + 0.05, dy - 0.48, 0.770), (0.16, 0.24, 0.03), (0.22, 0.30, 0.44, 1.0))
    make_cyl("BP_Bulb", (dx - 0.02, dy - 0.62, 0.775), 0.022, 0.06, (0.10, 0.10, 0.10, 1.0), axis='X', segments=8)
    make_lamp("Lamp_Desk", dx + 0.20, dy - 0.58, base_z=0.755, h=0.42)
    # Andy's chair at the desk, Jane's by its south end
    make_chair("Chair_Test", dx - 0.62, dy + 0.10, yaw=-math.pi / 2.0, wood=OAK_DARK)
    make_chair("Chair_Jane", dx - 0.70, dy - 0.62, yaw=-math.pi * 0.80, wood=OAK_DARK)


def build_bathroom():
    """Through the W door: a small tiled bathroom with a shower."""
    bx0, bx1, bd = -5.0, X0, 2.8
    cx = (bx0 + bx1) / 2.0
    tile = {"vinyl": (0.84, 0.86, 0.84, 1.0), "seam": (0.62, 0.64, 0.62, 1.0)}
    make_floor("Bath_Floor", (cx, bd / 2.0, 0.0), size_x=bx1 - bx0, size_y=bd, palette=tile)
    make_box("Bath_Ceil", (cx, bd / 2.0, CEIL + 0.03), (bx1 - bx0, bd, 0.06), (0.86, 0.86, 0.84, 1.0))
    bpal = {"wall": (0.86, 0.88, 0.86, 1.0), "baseboard": (0.60, 0.62, 0.60, 1.0)}
    make_wall("Bath_Wall_W", (bx0, bd / 2.0, 0), length=bd + 0.2, height=CEIL, thickness=T, axis='Y', palette=bpal, baseboard_face_sign=+1)
    make_wall("Bath_Wall_N", (cx, bd, 0), length=(bx1 - bx0) + 0.2, height=CEIL, thickness=T, axis='X', palette=bpal, baseboard_face_sign=-1)
    make_box("Shower_Base", (bx0 + 0.55, bd - 0.55, 0.05), (0.90, 0.90, 0.10), (0.92, 0.92, 0.90, 1.0))
    make_box("Shower_Curtain", (bx0 + 0.55, bd - 1.02, 1.12), (0.90, 0.02, 1.80), (0.70, 0.78, 0.82, 1.0))
    make_box("Shower_Rod", (bx0 + 0.55, bd - 1.02, 2.04), (0.92, 0.02, 0.02), (0.74, 0.74, 0.76, 1.0))
    make_box("Shower_Arm", (bx0 + 0.13, bd - 0.55, 1.95), (0.08, 0.025, 0.025), (0.74, 0.74, 0.76, 1.0))
    make_cyl("Shower_Head", (bx0 + 0.18, bd - 0.55, 1.90), 0.05, 0.04, (0.74, 0.74, 0.76, 1.0), axis='X', segments=10)
    make_box("Toilet_Bowl", (bx0 + 0.32, 0.70, 0.20), (0.50, 0.38, 0.40), (0.94, 0.94, 0.92, 1.0))
    make_box("Toilet_Tank", (bx0 + 0.18, 0.70, 0.58), (0.20, 0.44, 0.36), (0.94, 0.94, 0.92, 1.0))
    make_box("Bath_Door", (X0 - 0.05, BATH_Y - 0.36, 1.0), (0.04, 0.10, 2.0), DOOR)        # swung back, edge-on
    make_box("Bath_Sink", (bx1 - 0.10 - 0.25, 2.30, 0.80), (0.46, 0.40, 0.14), (0.94, 0.94, 0.92, 1.0))
    make_box("Bath_Sink_Pedestal", (bx1 - 0.10 - 0.25, 2.30, 0.37), (0.16, 0.16, 0.72), (0.94, 0.94, 0.92, 1.0))


def build_corridor():
    """Past the entry door: the corridor of long empty aquariums."""
    cy0, cy1, cx0, cx1, ch = -2.6, -0.1, -6.0, 4.0, 2.6
    cx, cy = (cx0 + cx1) / 2.0, (cy0 + cy1) / 2.0
    make_floor("Corr_Floor", (cx, cy, 0.0), size_x=cx1 - cx0, size_y=cy1 - cy0,
               palette={"vinyl": (0.56, 0.56, 0.54, 1.0), "seam": (0.46, 0.46, 0.44, 1.0)})
    make_box("Corr_Ceil", (cx, cy, ch + 0.03), (cx1 - cx0, cy1 - cy0, 0.06), (0.70, 0.70, 0.68, 1.0))
    make_wall("Corr_Wall_S", (cx, cy0, 0), length=cx1 - cx0, height=ch, thickness=T, axis='X',
              palette={"wall": (0.74, 0.74, 0.70, 1.0), "baseboard": (0.40, 0.40, 0.38, 1.0)}, baseboard_face_sign=+1)
    for k, x in enumerate((-4.0, -1.0, 2.0)):
        make_fluorescent_tube_fixture(f"Fluor_Corr_{k}", (x, cy, ch), length=1.20, width=0.30)
    for k, x in enumerate((-4.4, -1.6, 1.2)):
        ay = cy0 + 0.10 + 0.28
        make_box(f"Aquarium_Stand_{k}", (x, ay, 0.40), (2.40, 0.50, 0.80), (0.20, 0.20, 0.22, 1.0))
        make_box(f"Aquarium_Back_{k}", (x, ay + 0.24, 1.10), (2.36, 0.01, 0.58), (0.50, 0.58, 0.56, 1.0))
        make_box(f"Aquarium_Floor_{k}", (x, ay, 0.815), (2.36, 0.46, 0.03), (0.62, 0.62, 0.58, 1.0))
        make_box(f"Aquarium_Rim_{k}", (x, ay, 1.39), (2.40, 0.50, 0.02), (0.10, 0.10, 0.12, 1.0))
        for s in (-1, 1):
            make_box(f"Aquarium_Post_{k}_{s:+d}", (x + s * 1.19, ay - 0.24, 1.10), (0.02, 0.02, 0.58), (0.10, 0.10, 0.12, 1.0))
        make_box(f"Aquarium_Glass_{k}", (x, ay - 0.24, 1.10), (2.36, 0.006, 0.56), (0.66, 0.74, 0.72, 0.35))


def build_four_screens():
    make_floor("G_Floor", (GCX, GCY, 0.0), size_x=GX1 - GX0 + 0.4, size_y=GD + 0.4,
               palette={"vinyl": (0.40, 0.40, 0.40, 1.0), "seam": (0.34, 0.34, 0.34, 1.0)})
    make_box("G_Ceil", (GCX, GCY, GH + 0.05), (GX1 - GX0 + 0.4, GD + 0.4, 0.10), (0.10, 0.10, 0.11, 1.0))
    gpal = {"wall": WHITE, "baseboard": WHITE}
    make_wall("G_Wall_N", (GCX, GD, 0), length=GX1 - GX0 + 0.4, height=GH, thickness=0.3, axis='X', palette=gpal, baseboard_face_sign=-1)
    make_wall("G_Wall_W", (GX0, GCY, 0), length=GD + 0.4, height=GH, thickness=0.3, axis='Y', palette=gpal, baseboard_face_sign=+1)
    make_wall("G_Wall_E", (GX1, GCY, 0), length=GD + 0.4, height=GH, thickness=0.3, axis='Y', palette=gpal, baseboard_face_sign=-1)
    make_wall_with_openings("G_Wall_S", (GCX, 0.0, 0), length=GX1 - GX0 + 0.4, height=GH, thickness=0.3, axis='X', palette=gpal,
                            baseboard_face_sign=+1, openings=[(GCX, 1.2, 1.80, 2.4)])
    # the doors: flush, white, shut ("The doors close.")
    for s in (-1, 1):
        make_box(f"G_Door_{s:+d}", (GCX + s * 0.45, 0.0, 1.2), (0.88, 0.06, 2.38), (0.86, 0.86, 0.84, 1.0))
    make_box("G_Door_Seam", (GCX, 0.035, 1.2), (0.01, 0.01, 2.38), (0.50, 0.50, 0.50, 1.0))
    # the house lights: a row of small cans in the dark ceiling
    for k in range(4):
        for j in range(4):
            make_cyl(f"G_Can_{k}_{j}", (GX0 + 3.0 + k * 4.0, 3.0 + j * 4.0, GH - 0.03), 0.10, 0.06, (0.30, 0.30, 0.30, 1.0), segments=10)
    # the island: 81 leather executive swivel chairs on bolted plates, 1.2 m
    # apart, each turned its own way (they spin)
    n, pitch = 9, 1.2
    for r in range(n):
        for q in range(n):
            x = GCX + (q - (n - 1) / 2.0) * pitch
            y = GCY + (r - (n - 1) / 2.0) * pitch
            yaw = ((r * 37 + q * 53) % 41) / 41.0 * 1.4 - 0.7 + (math.pi if (r * 3 + q) % 7 == 0 else 0.0)
            col = LEATHER[(r * 5 + q * 3) % len(LEATHER)]
            p = f"Island_Stock_{r}_{q}"
            c, s = math.cos(yaw), math.sin(yaw)

            def at(u, v):
                # u across the chair, v toward its front
                return (x + u * c - v * s, y + u * s + v * c)
            make_cyl(p + "_Plate", (x, y, 0.006), 0.24, 0.012, (0.30, 0.30, 0.32, 1.0), segments=10)
            make_cyl(p + "_Column", (x, y, 0.24), 0.035, 0.44, (0.20, 0.20, 0.22, 1.0), segments=8)
            make_rot_box(p + "_Seat", (x, y, 0.50), (0.60, 0.58, 0.14), col, yaw=yaw)
            make_rot_box(p + "_Back", (*at(0.0, -0.27), 0.92), (0.58, 0.14, 0.78), col, yaw=yaw, roll=0.0)
            for side in (-1, 1):
                make_rot_box(p + f"_Arm_{side:+d}", (*at(side * 0.30, -0.02), 0.68), (0.08, 0.46, 0.08), col, yaw=yaw)


def build_screens():
    """Show view: each wall carries its picture (the rear projection). From
    the text: the desert from a helicopter; the van with four passengers on
    the highway; the road signs ("Ticonderoga", "Promontory Point"); the
    fourth wall's own film, the girl's."""
    show = "__four_screens_show"
    inset = 0.16
    # N: the desert from the air — sky band, the long tan land, a road across it
    make_box("Screen_N_Land" + show, (GCX, GD - inset, 2.6), (GX1 - GX0 - 0.4, 0.02, 5.2), (0.86, 0.68, 0.46, 1.0))
    make_box("Screen_N_Sky" + show, (GCX, GD - inset, 6.1), (GX1 - GX0 - 0.4, 0.02, 1.8), (0.62, 0.78, 0.94, 1.0))
    make_box("Screen_N_Road" + show, (GCX - 1.0, GD - inset - 0.01, 2.6), (0.30, 0.02, 5.0), (0.30, 0.28, 0.28, 1.0))
    # E: the van on the highway, dusk
    make_box("Screen_E_Dusk" + show, (GX1 - inset, GCY, 3.5), (0.02, GD - 0.4, 7.0 - 0.4), (0.82, 0.48, 0.34, 1.0))
    make_box("Screen_E_Road" + show, (GX1 - inset - 0.01, GCY, 1.3), (0.02, GD - 0.4, 1.4), (0.26, 0.24, 0.26, 1.0))
    make_box("Screen_E_Van" + show, (GX1 - inset - 0.02, GCY + 1.0, 2.1), (0.02, 4.6, 2.2), (0.84, 0.84, 0.80, 1.0))
    for k in range(4):
        make_box(f"Screen_E_Window_{k}" + show, (GX1 - inset - 0.03, GCY - 0.6 + k * 1.05, 2.6), (0.02, 0.80, 0.70), (0.18, 0.20, 0.26, 1.0))
    # W: the road signs going by, green on a blur of road
    make_box("Screen_W_Blur" + show, (GX0 + inset, GCY, 3.5), (0.02, GD - 0.4, 7.0 - 0.4), (0.44, 0.50, 0.48, 1.0))
    for k, (y, z) in enumerate(((GCY - 4.0, 4.4), (GCY + 3.0, 3.6))):
        make_box(f"Screen_W_Sign_{k}" + show, (GX0 + inset + 0.01, y, z), (0.02, 4.4, 1.6), (0.10, 0.46, 0.26, 1.0))
        make_box(f"Screen_W_Sign_{k}_Text" + show, (GX0 + inset + 0.02, y, z), (0.02, 3.4, 0.30), (0.92, 0.94, 0.90, 1.0))
    # S: the girl's film, around the doors
    make_box("Screen_S_Upper" + show, (GCX, inset, 4.85), (GX1 - GX0 - 0.4, 0.02, 4.1), (0.30, 0.42, 0.64, 1.0))
    for s in (-1, 1):
        make_box(f"Screen_S_Side_{s:+d}" + show, (GCX + s * 5.0, inset, 1.4), (7.6, 0.02, 2.8), (0.24, 0.34, 0.54, 1.0))
    make_box("Screen_S_Figure" + show, (GCX - 3.4, inset + 0.01, 3.6), (1.2, 0.02, 3.4), (0.86, 0.66, 0.58, 1.0))


def build_stalk():
    """meld_seam_2_3 only: the machine on a long jointed stalk, high in the
    dark, covered in tiny lights like little eyes."""
    beam = "__four_screens_beam"
    # hung from the ceiling NE of the island, its head over the open floor
    pts = [(46.0, 15.5, GH), (45.6, 14.6, GH - 0.6), (44.4, 13.9, GH - 1.0), (43.6, 13.5, GH - 1.3)]
    make_tube("Stalk_Arm" + beam, pts, 0.06, (0.16, 0.16, 0.18, 1.0), segments=8)
    for k, pt in enumerate(pts[1:]):
        make_blob(f"Stalk_Joint_{k}" + beam, pt, 0.11, (0.20, 0.20, 0.22, 1.0), noise=0.0, seed=k)
    hx, hy, hz = pts[-1]
    make_chamfer_box("Stalk_Head" + beam, (hx, hy, hz - 0.2), (0.6, 0.5, 0.4), (0.12, 0.12, 0.14, 1.0), chamfer=0.06)
    for k in range(22):
        a = k * 0.9
        make_box(f"Stalk_Eye_{k}" + beam, (hx + 0.31 * math.cos(a) * (1 if k % 2 else 0.8), hy + 0.26 * math.sin(a), hz - 0.05 - (k % 4) * 0.09),
                 (0.06, 0.06, 0.06), (1.0, 0.92, 0.70, 1.0))
    make_box("Stalk_Lens" + beam, (hx - 0.1, hy + 0.1, hz - 0.42), (0.22, 0.22, 0.04), (1.0, 0.96, 0.86, 1.0))


def main():
    clear_scene()
    build_lab_shell()
    build_beds_and_shelf()
    build_curtain_station()
    build_test_desk()
    build_bathroom()
    build_corridor()
    build_four_screens()
    build_screens()
    build_stalk()
    try:    # one mesh for the shelf's books, one for the chair island (_props.geometry.join_stock)
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/sleep_lab.glb"))
    print(f"\n[build_sleep_lab] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
