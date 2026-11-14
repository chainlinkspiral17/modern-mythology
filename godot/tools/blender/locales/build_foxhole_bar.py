"""foxhole_bar — THE FOXHOLE, the whole venue (vol 1 ch 3/4, vol 6 ch 20/22).

REBUILT 2026-10-09 (the overnight run). The Foxhole was two template
rooms: `foxhole_bar`, an 8 x 6 m bar with a stage crammed against its
west wall, and `foxhole_stage`, an auto-generated 8 x 5 m shell with a
deck in it. The prose plays ONE room, and a big one:

    "a hundred and ten people in front of him" · "The stage at the front
    is lit, in slow rotation, by six programmable LED fixtures mounted on
    two vertical truss towers at the lip of the stage" · "At the small DJ
    booth at the side of the stage" · "There is one work light at the
    back of the room" · "Walk to the back. Stand against the back wall"
    · "the bass is hitting the back wall" · "Jesse, at the bar in the
    back" · "a high-top to the left of the stage" · "At the front of the
    stage against the lip is one kid" / "the kid at the rail" ·
    "Backstage Jesse drinks half a bottle of water" · "He goes out the
    back" · Ricky at the board with his Topo Chico · "The set list ...
    taped to the floor with masking tape Ricky put down at six".

So: a 12 x 16 m black box, ceiling 4.6. The stage across the north end
(0.6 m deck, 9 m wide, a drum riser, two amps, three mics, wedges, the
PA flanking it on the floor, the two truss towers at the lip with three
fixtures each, a lighting pipe over the lip); the rail in front of it;
the DJ booth on the floor at the stage's east side; the FOH desk mid-
room with its cooler; high-tops down the west wall; the bar across the
back (south) wall's west half with its back bar, neon, taps and stools;
the entrance at the south wall's east end; the work light in the back
corner; restroom doors on the east wall; the backstage door off the
stage's west wing.

TWO PRESETS, one set (the cabin-porch pattern): `foxhole_bar` looks
from the back of the room at the stage; `foxhole_stage` stands at the
rail. The stage preset's own markers are suffixed __foxhole_stage.
The old build_foxhole_stage.py / foxhole_stage.tscn are retired.

Frame: Blender Z-up, y=0 the south (back) wall, +Y toward the stage,
x = +-6. glTF export remaps to Godot (x, z, -y).

DRAFT 2 targets: crowd silhouettes for the gig states (a hundred and ten
people is not an empty floor — staged figures on the floor for ch22);
cable runs from the stage to the FOH snake; the bar's beer-tap handles
told apart; flyers layered by date; the mirror ball? (no — not this
room); Deck framing of both presets with the stage rig lit.

PASS 342 (2026-11-11, read by render): the entrance glass hid behind its
own leaves from inside (now through the leaf, sodium); the scene lights all
six tower fixtures and two backdrop cans, the FOH board has its glow; the
door insert looks at the doors and a new `insert stage` stands just inside
them looking up the room (ch20 106 / 108).
NEXT-PASS TARGETS: the gig crowd for ch22 ("a hundred and ten people" — the
floor is empty at ten o'clock); the vestibule past the glass (a street, the
Tacoma and the Civic in the lot, not a black box); the booth insert shoots
past the east truss tower (a reverse from the restroom wall needs the PA
moved); the stage reads purple-dark at the back-wall wide — a hazer and the
white spike ("a single white spike at the end of the cycle") as a cue.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import (clear_scene, make_box, make_cyl, make_lathe, make_chamfer_box, make_tube,
                             make_rot_box, export_glb)
from _props.structure import make_floor, make_wall, make_ceiling, make_wall_with_openings, make_frame_ring
from _props.decor import make_faded_poster
from _props.safety import make_smoke_detector
from _props.objects import make_liquor_bottle
from _props.furniture import make_stool

ROOM_W = 12.0; ROOM_D = 16.0; CEIL = 4.6
PAL_WALL = {"wall": (0.16, 0.14, 0.15, 1.0), "baseboard": (0.10, 0.09, 0.09, 1.0)}
COL_FLOOR = (0.24, 0.22, 0.22, 1.0); COL_SEAM = (0.14, 0.13, 0.13, 1.0)
COL_BAR = (0.34, 0.22, 0.14, 1.0); COL_BAR_TOP = (0.20, 0.13, 0.09, 1.0)
COL_BRASS = (0.82, 0.62, 0.28, 1.0); COL_STEEL = P.METAL_STEEL; COL_BLACK = P.METAL_BLACK
COL_WOOD = (0.42, 0.30, 0.18, 1.0)
COL_DECK = (0.16, 0.14, 0.13, 1.0)
COL_TRUSS = (0.62, 0.64, 0.66, 1.0)
COL_CAB = (0.11, 0.10, 0.10, 1.0)
COL_NEON_MAGENTA = (0.98, 0.24, 0.72, 1.0); COL_NEON_CYAN = (0.30, 0.82, 0.96, 1.0)
COL_NEON_AMBER = (0.98, 0.72, 0.28, 1.0)
COL_BOTTLE_AMBER = (0.78, 0.42, 0.16, 1.0); COL_BOTTLE_GREEN = (0.24, 0.42, 0.22, 1.0)
COL_BOTTLE_CLEAR = (0.74, 0.82, 0.84, 0.55)

STAGE_Y0, STAGE_Y1, STAGE_X = 12.0, ROOM_D - 0.1, 4.5
STAGE_TOP = 0.60
BAR_X0, BAR_X1, BAR_Y = -5.6, -0.6, 2.40          # the bar's front face (the bartender's lane behind it 1.1 m)
DOOR_X, DOOR_W = 3.8, 1.80                         # the entrance, south wall east


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    # W wall: the backstage door off the stage's west wing (y 13.4)
    make_wall_with_openings("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y',
                            palette=PAL_WALL, baseboard_face_sign=+1, openings=[(13.4, STAGE_TOP + 1.05, 0.95, 2.10)])
    # E wall: the restrooms (y 3.2 / 4.6)
    make_wall_with_openings("Wall_E", (+ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y',
                            palette=PAL_WALL, baseboard_face_sign=-1, openings=[(3.2, 1.05, 0.90, 2.10), (4.6, 1.05, 0.90, 2.10)])
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    # S (back) wall: the entrance's double doors at its east end
    make_wall_with_openings("Wall_S", (0.0, 0.0, 0), length=ROOM_W + 0.4, height=CEIL, axis='X', palette=PAL_WALL,
                            baseboard_face_sign=+1, openings=[(DOOR_X, 1.20, DOOR_W, 2.40)])
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
                 with_grid=False, with_stains=False, palette={"tile": (0.08, 0.08, 0.09, 1.0)})
    # what is behind the openings: dark vestibules a lens will not reach
    for nm, (cx, cy, sx, sy) in (("Vestibule_S", (DOOR_X, -0.9, DOOR_W + 0.4, 1.6)),
                                 ("Backstage_W", (-ROOM_W / 2.0 - 1.0, 13.4, 1.8, 2.4)),
                                 ("Restroom_Hall_E", (ROOM_W / 2.0 + 0.9, 3.9, 1.6, 3.4))):
        make_box(f"{nm}_Floor", (cx, cy, -0.01 + (STAGE_TOP if nm.startswith("Backstage") else 0.0)), (sx, sy, 0.02), (0.18, 0.17, 0.17, 1.0))
        make_box(f"{nm}_Back", (cx + (-sx / 2.0 if nm == "Backstage_W" else sx / 2.0 if nm == "Restroom_Hall_E" else 0.0),
                                cy + (-sy / 2.0 if nm == "Vestibule_S" else 0.0), CEIL / 2.0),
                 (0.10 if nm != "Vestibule_S" else sx, 0.10 if nm == "Vestibule_S" else sy, CEIL), (0.12, 0.11, 0.11, 1.0))
    # the doors: the entrance's two leaves (glass to the street, the street's
    # sodium light in it), the restrooms' leaves shut with their signs, the
    # backstage door propped open a hand
    for li, lx in enumerate((DOOR_X - DOOR_W / 4.0, DOOR_X + DOOR_W / 4.0)):
        make_box(f"Entrance_Door_Leaf_{li}", (lx, 0.06, 1.18), (DOOR_W / 2.0 - 0.04, 0.05, 2.34), (0.20, 0.20, 0.22, 1.0))
        # the glass runs through the leaf, proud of both faces: at y 0.03 it hid
        # behind its own leaf from inside, and the door insert read as two black
        # slabs (pass 342); the street's sodium in it
        make_box(f"Entrance_Door_Leaf_{li}_Glass", (lx, 0.06, 1.50), (DOOR_W / 2.0 - 0.30, 0.058, 1.10), (0.88, 0.66, 0.36, 1.0))
        make_tube(f"Entrance_Door_Leaf_{li}_Bar", [(lx - 0.30, 0.11, 1.05), (lx + 0.30, 0.11, 1.05)], 0.016, COL_STEEL, segments=6)
    make_box("Entrance_Exit_Sign", (DOOR_X, 0.12, 2.62), (0.42, 0.06, 0.16), (0.24, 0.84, 0.36, 1.0))
    for ri, ry in enumerate((3.2, 4.6)):
        make_box(f"Restroom_Door_{ri}", (ROOM_W / 2.0 - 0.06, ry, 1.05), (0.05, 0.86, 2.08), (0.30, 0.26, 0.24, 1.0))
        make_box(f"Restroom_Door_{ri}_Sign", (ROOM_W / 2.0 - 0.09, ry, 1.62), (0.01, 0.16, 0.16), (0.86, 0.84, 0.78, 1.0))
    make_box("Backstage_Door_Leaf", (-ROOM_W / 2.0 - 0.10 - 0.45, 13.4 - 0.47 + 0.03, STAGE_TOP + 1.05), (0.86, 0.05, 2.08), (0.24, 0.22, 0.22, 1.0))


def build_stage():
    """The stage across the north end: the deck on its skirt, the drum
    riser, the side steps to the backstage door's landing."""
    sw = 2 * STAGE_X
    make_box("Stage_Deck", (0.0, (STAGE_Y0 + STAGE_Y1) / 2.0, STAGE_TOP / 2.0), (sw, STAGE_Y1 - STAGE_Y0, STAGE_TOP), COL_DECK)
    make_box("Stage_Lip", (0.0, STAGE_Y0 + 0.03, STAGE_TOP - 0.03), (sw, 0.06, 0.06), (0.32, 0.30, 0.28, 1.0))
    make_box("Stage_Skirt", (0.0, STAGE_Y0 - 0.015, STAGE_TOP / 2.0), (sw, 0.03, STAGE_TOP - 0.02), (0.08, 0.07, 0.07, 1.0))
    # the west wing: a landing from the stage to the backstage door, and its steps to the floor
    make_box("Stage_Wing_W", (-(STAGE_X + ROOM_W / 2.0 - 0.1) / 2.0, 13.4, STAGE_TOP / 2.0), (ROOM_W / 2.0 - 0.1 - STAGE_X, 1.6, STAGE_TOP), COL_DECK)
    for si in range(3):
        sh = STAGE_TOP * (si + 1) / 4.0
        make_box(f"Stage_Step_{si}", (-5.6, 12.6 - 0.14 - 0.28 * (2 - si), sh / 2.0), (0.50, 0.28, sh), COL_DECK)   # a service stair, clear of the PA
    # the backdrop: a black drape on the N wall, its pleats
    make_box("Backdrop", (0.0, ROOM_D - 0.14, CEIL / 2.0 + 0.2), (sw + 0.4, 0.04, CEIL - 0.4), (0.07, 0.06, 0.07, 1.0))
    for pi in range(18):
        make_box(f"Backdrop_Pleat_{pi}", (-STAGE_X + 0.25 + pi * (sw / 18.0), ROOM_D - 0.165, CEIL / 2.0 + 0.2), (0.04, 0.02, CEIL - 0.45), (0.10, 0.09, 0.10, 1.0))
    # the drum riser, centre back
    make_box("Drum_Riser", (0.0, 14.6, STAGE_TOP + 0.15), (2.6, 2.0, 0.30), (0.20, 0.18, 0.17, 1.0))
    make_box("Drum_Riser_Carpet", (0.0, 14.6, STAGE_TOP + 0.305), (2.4, 1.8, 0.01), (0.36, 0.14, 0.12, 1.0))


def build_backline():
    """Carl's kit on the riser, Jesse's amp and Nate's bass rig, the mics,
    the wedges at the lip, the PA flanking the stage on the floor."""
    rz = STAGE_TOP + 0.31
    # (pass 375) the kit a quarter metre toward the lip, the throne where it was: seated on it,
    # a drummer's shins stood in the kick drum
    dx, dy = 0.0, 14.45
    ty = 15.32
    shell = (0.62, 0.20, 0.16, 1.0); chrome = COL_STEEL; brass = (0.86, 0.72, 0.30, 1.0)
    make_cyl("Drum_Kick", (dx, dy, rz + 0.28), 0.28, 0.42, (0.74, 0.70, 0.66, 1.0), axis='Y', segments=16)
    make_cyl("Drum_Kick_Head", (dx, dy - 0.215, rz + 0.28), 0.27, 0.01, (0.92, 0.90, 0.86, 1.0), axis='Y', segments=16)
    make_cyl("Drum_Snare", (dx - 0.48, dy - 0.32, rz + 0.58), 0.16, 0.14, (0.86, 0.84, 0.80, 1.0), segments=12)
    make_cyl("Drum_Snare_Stand", (dx - 0.48, dy - 0.32, rz + 0.255), 0.015, 0.51, chrome, segments=6)
    make_cyl("Drum_Tom_Mount", (dx, dy + 0.05, rz + 0.585), 0.018, 0.05, chrome, segments=6)   # the rack mount on the kick's shell
    make_cyl("Drum_Tom_0", (dx - 0.16, dy, rz + 0.64), 0.13, 0.16, shell, segments=12)
    make_cyl("Drum_Tom_1", (dx + 0.16, dy, rz + 0.65), 0.14, 0.18, shell, segments=12)
    make_cyl("Drum_FloorTom", (dx + 0.56, dy + 0.10, rz + 0.22), 0.18, 0.44, shell, segments=12)
    for ci, (cx, cy, ch, cr) in enumerate(((-0.62, 0.06, 0.95, 0.22), (0.64, -0.06, 1.15, 0.26), (-0.82, -0.46, 0.82, 0.16))):
        make_cyl(f"Drum_Cym_Stand_{ci}", (dx + cx, dy + cy, rz + ch / 2.0), 0.014, ch, chrome, segments=6)
        make_cyl(f"Drum_Cym_{ci}", (dx + cx, dy + cy, rz + ch + 0.01), cr, 0.02, brass, segments=16)
    make_cyl("Drum_Throne_Post", (dx, ty, rz + 0.25), 0.02, 0.50, chrome, segments=6)
    make_lathe("Drum_Throne_Seat", (dx, ty, rz + 0.50), [(0.0, 0.0), (0.17, 0.0), (0.18, 0.03), (0.15, 0.08), (0.0, 0.09)], (0.12, 0.12, 0.12, 1.0), segments=12)
    make_lathe("Drum_Throne_Foot", (dx, ty, rz), [(0.26, 0.0), (0.26, 0.02), (0.03, 0.05), (0.0, 0.05)], chrome, segments=10)
    # amps on the stage deck (Jesse stage-left of centre, Nate stage-right)
    for prefix, ax in (("Stage_Amp", -2.4), ("Bass_Amp", 2.4)):
        make_box(f"{prefix}_Cab", (ax, 14.3, STAGE_TOP + 0.40), (0.74, 0.46, 0.80), COL_CAB)
        make_box(f"{prefix}_Grille", (ax, 14.3 - 0.235, STAGE_TOP + 0.40), (0.62, 0.01, 0.66), (0.42, 0.38, 0.30, 1.0))
        make_box(f"{prefix}_Head", (ax, 14.3, STAGE_TOP + 0.91), (0.74, 0.40, 0.22), (0.18, 0.16, 0.15, 1.0))
        for k in range(4):
            make_cyl(f"{prefix}_Knob_{k}", (ax - 0.24 + k * 0.16, 14.3 - 0.205, STAGE_TOP + 0.95), 0.018, 0.02, (0.86, 0.80, 0.62, 1.0), axis='Y', segments=6)
    # the bridge lyrics on the back of last week's flyer, flat by Jesse's amp
    make_box("Bridge_Lyrics", (-1.95, 13.75, STAGE_TOP + 0.002), (0.21, 0.28, 0.003), (0.92, 0.90, 0.84, 1.0))
    make_box("Bridge_Lyrics_Lines", (-1.95, 13.77, STAGE_TOP + 0.0045), (0.15, 0.18, 0.001), (0.32, 0.32, 0.36, 1.0))
    # THE SET LIST, taped to the floor at Jesse's feet (masking tape at the corners)
    make_box("Setlist", (-1.6, 12.55, STAGE_TOP + 0.002), (0.21, 0.28, 0.003), (0.94, 0.92, 0.86, 1.0))
    make_box("Setlist_Lines", (-1.6, 12.56, STAGE_TOP + 0.0045), (0.15, 0.20, 0.001), (0.20, 0.20, 0.24, 1.0))
    for ti, (tx, ty) in enumerate(((-1.70, 12.68), (-1.50, 12.68), (-1.70, 12.42), (-1.50, 12.42))):
        make_box(f"Setlist_Tape_{ti}", (tx, ty, STAGE_TOP + 0.005), (0.06, 0.03, 0.002), (0.86, 0.80, 0.58, 1.0))
    # three mic stands: Em centre, Jesse and Nate either side
    for mi, (mx, my) in enumerate(((0.0, 12.75), (-1.9, 12.85), (1.9, 12.85))):
        make_lathe(f"Mic_{mi}_Base", (mx, my, STAGE_TOP), [(0.15, 0.0), (0.15, 0.02), (0.03, 0.04), (0.0, 0.04)], COL_BLACK, segments=12)
        make_cyl(f"Mic_{mi}_Pole", (mx, my, STAGE_TOP + 0.74), 0.012, 1.40, COL_STEEL, segments=6)
        make_tube(f"Mic_{mi}_Clip", [(mx, my, STAGE_TOP + 1.44), (mx, my - 0.08, STAGE_TOP + 1.48)], 0.012, COL_BLACK, segments=5)
        make_cyl(f"Mic_{mi}_Mic", (mx, my - 0.13, STAGE_TOP + 1.50), 0.024, 0.12, (0.12, 0.12, 0.13, 1.0), axis='Y', segments=8)
        # (pass 375) down the stand, then away along the deck in its own run: one tube from the mic
        # to the back of the stage boxed in the place a singer stands
        make_tube(f"Mic_{mi}_Cord", [(mx, my - 0.17, STAGE_TOP + 1.50), (mx + 0.02, my - 0.10, STAGE_TOP + 0.9),
                                     (mx + 0.03, my + 0.0, STAGE_TOP + 0.02)], 0.006, COL_BLACK, segments=4)
        make_tube(f"Mic_{mi}_Cord_Run", [(mx + 0.03, my + 0.0, STAGE_TOP + 0.008), (mx + 0.45, my + 0.05, STAGE_TOP + 0.008),
                                         (mx + 0.75, my + 0.9, STAGE_TOP + 0.008)], 0.006, COL_BLACK, segments=4)
    # wedges at the lip, angled up at the players
    for wi, wx in enumerate((-1.9, 0.0, 1.9)):
        make_rot_box(f"Wedge_{wi}", (wx, 12.35, STAGE_TOP + 0.215), (0.56, 0.42, 0.30), COL_CAB, pitch=0.35)
    # the PA: a sub and a top on each side, on the floor off the stage's corners
    for si, sx in enumerate((-4.95, 4.95)):
        py = 11.0
        make_box(f"PA_{si}_Sub", (sx, py, 0.35), (0.70, 0.70, 0.70), COL_CAB)
        make_box(f"PA_{si}_Sub_Grille", (sx, py - 0.355, 0.35), (0.60, 0.01, 0.60), (0.20, 0.19, 0.19, 1.0))
        make_box(f"PA_{si}_Top", (sx, py, 1.32), (0.56, 0.56, 1.24), COL_CAB)
        make_cyl(f"PA_{si}_Woofer", (sx, py - 0.285, 1.10), 0.20, 0.02, (0.06, 0.06, 0.06, 1.0), axis='Y', segments=14)
        make_box(f"PA_{si}_Horn", (sx, py - 0.285, 1.66), (0.32, 0.02, 0.18), (0.20, 0.18, 0.16, 1.0))


def build_rig():
    """The two vertical truss towers at the lip with three fixtures each,
    and the lighting pipe across the lip with its cans."""
    led = [(0.72, 0.26, 0.60, 1.0), (0.26, 0.55, 0.80, 1.0), (0.86, 0.62, 0.22, 1.0)]
    for ti, tx in enumerate((-STAGE_X + 0.35, STAGE_X - 0.35)):
        make_box(f"Truss_{ti}_Base", (tx, STAGE_Y0 + 0.40, STAGE_TOP + 0.02), (0.60, 0.60, 0.04), COL_BLACK)
        h = CEIL - STAGE_TOP - 0.62
        for ci, (ox, oy) in enumerate(((-0.13, -0.13), (0.13, -0.13), (-0.13, 0.13), (0.13, 0.13))):
            make_cyl(f"Truss_{ti}_Chord_{ci}", (tx + ox, STAGE_Y0 + 0.40 + oy, STAGE_TOP + 0.04 + h / 2.0), 0.024, h, COL_TRUSS, segments=6)
        for li in range(int(h / 0.5)):
            z = STAGE_TOP + 0.30 + li * 0.5
            make_tube(f"Truss_{ti}_Lace_{li}", [(tx - 0.13, STAGE_Y0 + 0.27, z), (tx + 0.13, STAGE_Y0 + 0.27, z + 0.25),
                                                (tx + 0.13, STAGE_Y0 + 0.53, z + 0.5)], 0.010, COL_TRUSS, segments=4)
        # three fixtures up each tower, yoked off the audience-side chords
        for li, lz in enumerate((1.4, 2.4, 3.2)):
            make_box(f"Truss_{ti}_LED_{li}_Yoke", (tx, STAGE_Y0 + 0.40 - 0.18, STAGE_TOP + lz), (0.26, 0.10, 0.04), COL_BLACK)
            make_rot_box(f"Truss_{ti}_LED_{li}", (tx, STAGE_Y0 + 0.40 - 0.30, STAGE_TOP + lz - 0.10), (0.20, 0.22, 0.24), (0.14, 0.14, 0.15, 1.0), pitch=0.35)
            make_rot_box(f"Truss_{ti}_LED_{li}_Lens", (tx, STAGE_Y0 + 0.40 - 0.42, STAGE_TOP + lz - 0.06), (0.16, 0.01, 0.16), led[li], pitch=0.35)
    # the pipe over the lip on its two drop rods, six cans on it
    py, pz = STAGE_Y0 + 0.30, CEIL - 0.70
    make_cyl("Lighting_Pipe", (0.0, py, pz), 0.025, 2 * STAGE_X - 1.4, COL_BLACK, axis='X', segments=8)
    for ri, rx in enumerate((-2.8, 2.8)):
        make_cyl(f"Lighting_Pipe_Rod_{ri}", (rx, py, (pz + CEIL) / 2.0), 0.012, CEIL - pz, COL_BLACK, segments=6)
    for ci in range(6):
        cx = -2.75 + ci * 1.1
        make_box(f"Par_Light_{ci}_Clamp", (cx, py, pz - 0.05), (0.06, 0.06, 0.08), COL_BLACK)
        make_rot_box(f"Par_Light_{ci}", (cx, py - 0.10, pz - 0.20), (0.18, 0.30, 0.18), (0.12, 0.12, 0.13, 1.0), pitch=-0.6)


def build_floor():
    """The floor in front of the stage: the rail, the DJ booth at the
    stage's side, the FOH desk with Ricky's cooler, high-tops down the
    west wall, the tape marks."""
    # the barricade rail, a hand off the lip (the kid at the rail)
    for pi, px in enumerate((-4.0, -2.0, 0.0, 2.0, 4.0)):
        make_lathe(f"Rail_Post_{pi}", (px, 11.35, 0.0), [(0.10, 0.0), (0.10, 0.02), (0.03, 0.04), (0.03, 1.06), (0.0, 1.06)], COL_TRUSS, segments=8)
    make_cyl("Rail_Top", (0.0, 11.35, 1.07), 0.03, 8.06, COL_TRUSS, axis='X', segments=8)
    make_cyl("Rail_Mid", (0.0, 11.35, 0.55), 0.02, 8.06, COL_TRUSS, axis='X', segments=6)
    # the DJ booth on the floor at the stage's east side: a skirted table,
    # Chess's laptop, the controller, the lamp
    bx, by = 5.15, 12.9
    make_chamfer_box("DJ_Booth", (bx, by, 0.55), (1.20, 0.70, 1.10), (0.12, 0.11, 0.12, 1.0), chamfer=0.01)
    make_box("DJ_Booth_Top", (bx, by, 1.115), (1.26, 0.76, 0.03), (0.20, 0.19, 0.20, 1.0))
    make_box("DJ_Laptop_Base", (bx - 0.18, by - 0.05, 1.14), (0.32, 0.22, 0.02), (0.55, 0.57, 0.58, 1.0))
    make_rot_box("DJ_Laptop_Screen", (bx - 0.18, by + 0.07, 1.26), (0.32, 0.01, 0.22), (0.20, 0.26, 0.34, 1.0), pitch=0.25)
    make_box("DJ_Controller", (bx + 0.30, by - 0.05, 1.15), (0.40, 0.26, 0.04), (0.10, 0.10, 0.11, 1.0))
    for ki in range(4):
        make_cyl(f"DJ_Controller_Platter_{ki % 2}_{ki}", (bx + 0.20 + (ki % 2) * 0.20, by - 0.05, 1.172), 0.06 if ki < 2 else 0.012, 0.006, (0.30, 0.30, 0.32, 1.0), segments=12)
    make_tube("DJ_Lamp", [(bx + 0.55, by + 0.30, 1.13), (bx + 0.55, by + 0.30, 1.40), (bx + 0.45, by + 0.15, 1.50)], 0.008, COL_BLACK, segments=5)
    make_cyl("DJ_Lamp_Base", (bx + 0.55, by + 0.30, 1.14), 0.05, 0.02, COL_BLACK, segments=10)
    make_rot_box("DJ_Lamp_Head", (bx + 0.42, by + 0.11, 1.50), (0.07, 0.11, 0.05), COL_BLACK, pitch=0.6)   # the shade, turned down at the console (2026-11-04)
    # FOH: the desk mid-room on a low platform, the console, Ricky's cooler under it
    fx, fy = 2.6, 6.4
    make_box("FOH_Platform", (fx, fy, 0.10), (2.4, 1.8, 0.20), (0.20, 0.19, 0.19, 1.0))
    make_box("FOH_Desk", (fx, fy + 0.25, 1.02), (1.80, 0.80, 0.05), (0.24, 0.22, 0.20, 1.0))
    for lx in (fx - 0.85, fx + 0.85):
        make_box(f"FOH_Desk_Leg_{lx:.2f}", (lx, fy + 0.25, 0.60), (0.05, 0.75, 0.80), (0.20, 0.19, 0.20, 1.0))
    make_rot_box("FOH_Console", (fx, fy + 0.30, 1.10), (1.40, 0.62, 0.10), (0.14, 0.14, 0.16, 1.0), pitch=-0.12)
    for fi in range(16):
        make_box(f"FOH_Fader_{fi}", (fx - 0.60 + fi * 0.08, fy + 0.10, 1.165), (0.012, 0.10, 0.012), (0.80, 0.78, 0.74, 1.0))
    make_box("FOH_Cooler", (fx + 0.40, fy + 0.30, 0.42), (0.50, 0.40, 0.44), (0.72, 0.20, 0.18, 1.0))
    make_box("FOH_Cooler_Lid", (fx + 0.40, fy + 0.30, 0.65), (0.52, 0.42, 0.03), (0.92, 0.90, 0.86, 1.0))
    make_lathe("FOH_Topo_Chico", (fx + 0.70, fy + 0.45, 1.045), [(0.03, 0.0), (0.03, 0.14), (0.012, 0.20), (0.012, 0.23), (0.0, 0.23)], (0.42, 0.62, 0.48, 0.8), segments=10)
    make_cyl("FOH_Stool_Post", (fx - 0.30, fy - 0.45, 0.20 + 0.33), 0.02, 0.66, COL_STEEL, segments=6)
    make_lathe("FOH_Stool_Seat", (fx - 0.30, fy - 0.45, 0.86), [(0.0, 0.0), (0.17, 0.0), (0.18, 0.02), (0.16, 0.05), (0.0, 0.055)], (0.14, 0.14, 0.15, 1.0), segments=12)
    make_lathe("FOH_Stool_Foot", (fx - 0.30, fy - 0.45, 0.20), [(0.24, 0.0), (0.24, 0.02), (0.03, 0.04), (0.0, 0.04)], COL_STEEL, segments=10)
    # the snake: the cable run from the stage to the desk, taped down
    make_tube("Snake_Cable", [(-0.6, 12.0, 0.02), (0.6, 10.0, 0.02), (1.6, 8.0, 0.02), (fx - 0.3, fy + 0.9, 0.02)], 0.03, COL_BLACK, segments=6)
    for ti, (tx, ty) in enumerate(((0.6, 10.0), (1.6, 8.0))):
        make_box(f"Snake_Tape_{ti}", (tx, ty, 0.047), (0.30, 0.08, 0.004), (0.60, 0.58, 0.20, 1.0))
    # high-tops down the west wall ("a high-top to the left of the stage")
    for hi, hy in enumerate((5.0, 7.4, 9.8)):
        hx = -5.2
        make_lathe(f"HighTop_{hi}_Base", (hx, hy, 0.0), [(0.26, 0.0), (0.26, 0.02), (0.05, 0.04), (0.04, 1.02), (0.0, 1.02)], COL_BLACK, segments=12)
        make_cyl(f"HighTop_{hi}_Top", (hx, hy, 1.05), 0.36, 0.04, (0.26, 0.20, 0.16, 1.0), segments=16)
    # (pass 375) a beer sign's neon on the west wall over the high-tops: that side of the room had no
    # light of its own, and "the two of them are at a high-top to the left of the stage" played in the dark
    make_box("West_Wall_Neon", (-5.92, 8.60, 2.35), (0.04, 1.10, 0.30), (0.98, 0.46, 0.24, 1.0))
    make_box("West_Wall_Neon_Back", (-5.945, 8.60, 2.35), (0.01, 1.24, 0.44), (0.10, 0.09, 0.09, 1.0))
    make_lathe("HighTop_1_Bottle", (-5.1, 7.45, 1.07), [(0.03, 0.0), (0.03, 0.15), (0.012, 0.21), (0.012, 0.24), (0.0, 0.24)], COL_BOTTLE_AMBER, segments=8)
    # the one work light at the back of the room, the floor's tape marks
    make_lathe("Work_Light_Stand", (5.3, 0.8, 0.0), [(0.25, 0.0), (0.03, 0.04), (0.02, 1.90), (0.0, 1.90)], COL_TRUSS, segments=8)
    make_rot_box("Work_Light_Head", (5.2, 0.9, 1.98), (0.26, 0.14, 0.20), (0.96, 0.88, 0.66, 1.0), yaw=0.6, pitch=-0.2)
    for ti, (tx, ty, ta) in enumerate(((-1.2, 9.4, 0.1), (1.8, 10.2, -0.3), (-3.4, 8.2, 0.7))):
        make_rot_box(f"Floor_Tape_{ti}", (tx, ty, 0.003), (0.30, 0.05, 0.004), (0.70, 0.66, 0.24, 1.0), yaw=ta)


def build_bar():
    """The bar across the back wall's west half: the counter, the back
    bar with its shelves of bottles and mirror and neon, taps, stools."""
    top_z = 1.10
    cx, L = (BAR_X0 + BAR_X1) / 2.0, BAR_X1 - BAR_X0
    make_box("Bar_Front", (cx, BAR_Y - 0.30, 0.53), (L, 0.60, 1.06), COL_BAR)
    make_box("Bar_Top", (cx, BAR_Y - 0.28, top_z - 0.025), (L + 0.10, 0.70, 0.05), COL_BAR_TOP)
    make_cyl("Bar_Rail", (cx, BAR_Y + 0.04, 0.18), 0.025, L - 0.1, COL_BRASS, axis='X', segments=8)
    for pi in range(int(L / 0.8)):
        make_box(f"Bar_Panel_{pi}", (BAR_X0 + 0.4 + pi * 0.8, BAR_Y + 0.003, 0.55), (0.70, 0.006, 0.80), (0.38, 0.25, 0.16, 1.0))
    # taps on the bar's back edge
    for ti in range(6):
        tx = cx - 1.0 + ti * 0.4
        make_box(f"Tap_{ti}_Tower", (tx, BAR_Y - 0.50, top_z + 0.18), (0.10, 0.10, 0.36), COL_STEEL)
        make_box(f"Tap_{ti}_Handle", (tx, BAR_Y - 0.44, top_z + 0.42), (0.04, 0.04, 0.16), [COL_NEON_AMBER, (0.20, 0.20, 0.22, 1.0), (0.62, 0.20, 0.16, 1.0)][ti % 3])
    # the back bar against the S wall: a low cabinet, three shelves of bottles, the mirror
    make_box("BackBar_Cabinet", (cx, 0.38, 0.48), (L, 0.56, 0.96), (0.26, 0.17, 0.11, 1.0))
    for si2, sx2 in enumerate((BAR_X0 + 0.18, BAR_X1 - 0.18)):
        make_box(f"BackBar_Side_{si2}", (sx2, 0.29, 1.63), (0.04, 0.30, 1.34), (0.30, 0.20, 0.13, 1.0))
    make_box("BackBar_Mirror", (cx, 0.115, 1.80), (L - 0.6, 0.02, 1.00), (0.42, 0.44, 0.46, 1.0))
    for si, sz in enumerate((1.20, 1.62, 2.04)):
        make_box(f"BackBar_Shelf_{si}", (cx, 0.29, sz), (L - 0.40, 0.30, 0.03), (0.30, 0.20, 0.13, 1.0))
        for bi in range(int((L - 0.8) / 0.22)):
            col = (COL_BOTTLE_AMBER, COL_BOTTLE_GREEN, COL_BOTTLE_CLEAR)[(bi + si) % 3]
            make_liquor_bottle(f"BackBar_Bottle_{si}_{bi}", BAR_X0 + 0.45 + bi * 0.22, 0.29, sz + 0.015, col)
    # neon over the back bar
    for ni, (nx, col) in enumerate(((cx - 1.4, COL_NEON_MAGENTA), (cx + 1.4, COL_NEON_CYAN))):
        make_box(f"BackBar_Neon_{ni}", (nx, 0.13, 2.80), (1.30, 0.04, 0.34), col)
    make_box("BackBar_Neon_2", (cx, 0.13, 3.25), (2.20, 0.04, 0.26), COL_NEON_AMBER)
    # stools along the bar's front
    for si in range(6):
        make_stool(f"Bar_Stool_{si}", BAR_X0 + 0.45 + si * 0.82, BAR_Y + 0.48, h=0.78, wood=(0.18, 0.12, 0.10, 1.0))
    # Jesse's bottle at the bar's east end, the bartender's rag
    make_lathe("Bar_Beer_Jesse", (BAR_X1 - 0.35, BAR_Y - 0.15, top_z), [(0.03, 0.0), (0.03, 0.15), (0.012, 0.21), (0.012, 0.24), (0.0, 0.24)], COL_BOTTLE_AMBER, segments=8)
    make_box("Bar_Rag", (BAR_X1 - 1.10, BAR_Y - 0.40, top_z + 0.006), (0.30, 0.20, 0.012), (0.82, 0.80, 0.74, 1.0))


def build_show_2026_11():
    """THE SHOW (pass 375, vol 6 ch22). The venue had no one in it:

      "Em is on the stage with her mic in her hand checking the cord. Carl
      is at the kit ... Nate is plugging the bass into the house DI. Chess
      is at the small DJ booth at the side of the stage with her laptop
      open and Ramón at her elbow." · "Ricky has white hair pulled back in
      a small tail."
      "a room of about a hundred and ten people" · "Most of the room is
      standing and bobbing and listening ... About a third of the room is
      moving more" · "At the front of the stage against the lip is one
      kid. The kid is twenty-five, six-two, in a black T-shirt ... with
      hair down to his shoulders. The kid is at the rail. By the second
      verse the kid is fully headbanging."
      "By ten Chess is up and the room is hers." · "Carl is at the front
      by the rail with two girls from Selma ... Nate is at the door of the
      venue with his phone" · "Em is at the booth talking to Chess" · "The
      two of them are at a high-top to the left of the stage."

    Three views by the clock (the plain foxhole_bar / foxhole_stage stay the
    empty room of the other chapters); a part's letters say which it is in:
      k  foxhole_check   5:45  sound check: the band at their places, Chess
                               and Ramón at the booth, Ricky at the board
      s  foxhole_show    9:00  the set: about a hundred on the floor, the kid at the
                               rail, the band on stage (Jesse's place is
                               the lens), the bartender
      t  foxhole_after  10:00  Chess's set: most of the room still there;
                               Carl at the rail with the two girls, Nate at
                               the door, Em at the booth, the kid and his
                               friend at the high-top
    The figures are _props.figures (the portraits are the faces). Lanes are
    left where the lens stands: the bar's east end, the line from the back
    wall, the pit between the rail and the lip.

    NEXT (draft 2): drinks in hands and on the high-tops; phones held up;
    the two girls and the friend are the crowd's own figures recoloured;
    Nate's phone; a hazer in the stage light ("a single white spike at the
    end of the cycle"); the vestibule past the glass; ch20's visit and vol 1's
    nights have no one either."""
    import random
    import _props.figures as FIG
    from _props.view_tags import Views
    V = Views("fx", {"k": "foxhole_check", "s": "foxhole_show", "t": "foxhole_after"})
    rnd = random.Random(22)
    black, brown, blond, red = (0.10, 0.09, 0.09, 1.0), (0.24, 0.17, 0.12, 1.0), (0.66, 0.54, 0.32, 1.0), (0.48, 0.22, 0.12, 1.0)
    white, grey = (0.86, 0.85, 0.82, 1.0), (0.56, 0.55, 0.55, 1.0)
    hairs = (black, brown, brown, blond, red, (0.32, 0.22, 0.14, 1.0), black, (0.30, 0.46, 0.62, 1.0), (0.66, 0.28, 0.46, 1.0), grey)
    tees = ((0.10, 0.10, 0.11, 1.0), (0.14, 0.14, 0.18, 1.0), (0.20, 0.24, 0.34, 1.0), (0.42, 0.16, 0.16, 1.0), (0.24, 0.34, 0.26, 1.0),
            (0.50, 0.46, 0.40, 1.0), (0.60, 0.28, 0.44, 1.0), (0.72, 0.70, 0.66, 1.0), (0.30, 0.20, 0.36, 1.0), (0.68, 0.52, 0.20, 1.0),
            (0.12, 0.12, 0.13, 1.0), (0.16, 0.30, 0.36, 1.0))
    jeans = ((0.14, 0.16, 0.24, 1.0), (0.10, 0.10, 0.11, 1.0), (0.30, 0.34, 0.44, 1.0), (0.36, 0.30, 0.24, 1.0))
    skins = ((0.66, 0.52, 0.44, 1.0), (0.78, 0.64, 0.56, 1.0), (0.50, 0.36, 0.28, 1.0), (0.36, 0.25, 0.20, 1.0), (0.70, 0.56, 0.46, 1.0), (0.60, 0.44, 0.34, 1.0))

    people = []

    def stand(prefix, x, y, h, coat, hair, views, heading, **kw):
        people.append(prefix)
        with V.tagged(views, FIG):
            return FIG.make_standing_figure(prefix, x, y, heading=heading, h=h, coat=coat, hair=hair, **kw)

    S, N = math.pi, 0.0            # facing the room (south) / the stage (north)
    # ── the band (Jesse's place, stage-left of centre, is the lens) ──
    stand("Fx_Em", 0.0, 12.98, 1.60, (0.14, 0.12, 0.14, 1.0), black, "ks", S, z0=STAGE_TOP, arms="front", pants=jeans[1])
    people.append("Fx_Carl")
    with V.tagged("ks", FIG):
        FIG.make_seated_figure("Fx_Carl", 0.0, 15.40, heading=S, seat_h=0.59, z0=STAGE_TOP + 0.31, h=1.78,
                               coat=(0.30, 0.30, 0.34, 1.0), hair=brown, arms="table")
    stand("Fx_Nate", 2.00, 13.40, 1.82, (0.20, 0.26, 0.22, 1.0), black, "ks", S, z0=STAGE_TOP, arms="front", pants=jeans[0])
    # ── the house: Chess and Ramón at the booth, Ricky at the board, the bartender ──
    # (named for the job: a part called Chess is the subject of every `closeup chess` in the set)
    stand("Fx_Deejay", 5.05, 13.62, 1.66, (0.52, 0.20, 0.30, 1.0), black, "kst", S, arms="front", skin=skins[2])
    stand("Fx_Ramon", 5.62, 13.60, 1.74, (0.20, 0.22, 0.28, 1.0), black, "kst", S - 0.5, skin=skins[2])
    stand("Fx_Ricky", 2.85, 5.92, 1.76, (0.26, 0.26, 0.28, 1.0), white, "kst", N, z0=0.20, arms="front")
    stand("Fx_Bartender", -3.20, 1.25, 1.75, (0.12, 0.12, 0.13, 1.0), brown, "st", N, arms="front")
    # ── 9:00 · the kid at the rail ──
    stand("Fx_Kid", -0.50, 10.95, 1.88, (0.08, 0.08, 0.09, 1.0), brown, "s", N, arms="front", stoop=0.42, pants=jeans[1])
    # ── 10:00 · where they have gone ──
    after = (("Fx_KidT", -4.55, 9.95, 1.88, (0.08, 0.08, 0.09, 1.0), brown, -1.9, {"pants": jeans[1]}),
             ("Fx_KidFriend", -5.35, 9.12, 1.76, (0.36, 0.20, 0.16, 1.0), black, 0.3, {}),
             ("Fx_CarlT", -1.55, 10.95, 1.78, (0.30, 0.30, 0.34, 1.0), brown, 1.2, {}),
             ("Fx_Selma_A", -0.92, 10.94, 1.64, (0.62, 0.30, 0.46, 1.0), blond, -1.3, {}),
             ("Fx_Selma_B", -1.20, 10.36, 1.60, (0.70, 0.62, 0.30, 1.0), black, 0.2, {}),
             ("Fx_EmT", 5.10, 11.95, 1.60, (0.14, 0.12, 0.14, 1.0), black, N, {"pants": jeans[1]}),
             ("Fx_NateT", 3.55, 0.95, 1.82, (0.20, 0.26, 0.22, 1.0), black, S + 0.6, {"arms": "front", "pants": jeans[0]}))
    for nm, x, y, h, coat, hair, hd, kw in after:
        stand(nm, x, y, h, coat, hair, "t", hd, **kw)
    # ── the room: five rows packed behind the rail, a looser middle, the bar and the door ──
    spots = []
    for r, y in enumerate((10.92, 10.34, 9.76, 9.18, 8.60)):
        n = 15 - (r % 2)
        for k in range(n):
            spots.append((-4.20 + (k + 0.5 * (r % 2)) * 0.60 + rnd.uniform(-0.06, 0.06), y + rnd.uniform(-0.07, 0.07), r))
    for r, y in enumerate((7.65, 6.75, 5.85, 4.95, 4.05)):
        for k in range(9):
            spots.append((-4.30 + k * 1.06 + (0.4 if r % 2 else 0.0) + rnd.uniform(-0.18, 0.18), y + rnd.uniform(-0.15, 0.15), 5 + r))
    spots += [(-5.02, 3.02, 10), (-4.20, 3.08, 10), (-3.42, 2.98, 10), (3.05, 2.70, 10), (4.70, 2.55, 10), (5.05, 3.70, 10)]
    # no one where a thing stands, or where a lens does
    solids = ((2.6, 6.4, 1.75, 1.45),       # the FOH platform and Ricky
              (-5.2, 5.0, 0.75, 0.75), (-5.2, 7.4, 0.75, 0.75), (-5.2, 9.8, 0.75, 0.75),   # the high-tops
              (4.95, 11.0, 0.70, 0.70), (-4.95, 11.0, 0.70, 0.70))                          # the PA
    lenses = ((1.4, 2.4, 1.05, 2.2),        # the line from the back wall (the 10:00 vantage, the door insert)
              (3.9, 10.4, 0.60, 0.75),      # the booth frame, and its line past the PA
              (-3.9, 9.3, 1.00, 0.60))      # the high-top frame and its lane to the table
    gone_at_ten = [(a[1], a[2]) for a in after]
    k_n = 0
    for x, y, row in spots:
        if any(abs(x - cx) < hx and abs(y - cy) < hy for cx, cy, hx, hy in solids + lenses):
            continue
        if row == 0 and abs(x + 0.50) < 0.34:
            continue                         # the kid's place on the rail
        views = "st" if rnd.random() < 0.78 else "s"
        if any(math.hypot(x - ax, y - ay) < 0.62 for ax, ay in gone_at_ten):
            views = "s"
        arms = "down"
        if row <= 2 and rnd.random() < 0.34:
            arms = "up_r" if rnd.random() < 0.7 else "up"
        stand(f"Fx_C{k_n:03d}", x, y, rnd.uniform(1.56, 1.90), tees[rnd.randrange(len(tees))], hairs[rnd.randrange(len(hairs))],
              views, math.atan2(-x, 15.0 - y) * 0.5 + rnd.uniform(-0.16, 0.16), arms=arms,
              pants=jeans[rnd.randrange(len(jeans))], skin=skins[rnd.randrange(len(skins))])
        k_n += 1
    print(f"[build_foxhole_bar] the room: {k_n} on the floor")
    V.check()
    # one mesh a person (the stage and the floor are reached by more lamps than a load-time
    # merge may fold: thirteen parts a figure were 2,650 draw calls)
    from _props.geometry import join_prefix
    folded = sum(int(join_prefix(pfx) or 0) for pfx in people)
    print(f"[build_foxhole_bar] {len(people)} figures, {folded} parts folded into them")


def build_walls_dressing():
    """Flyers on the walls (the show posters of a venue that books every
    week), the PA hang points, the smoke detectors."""
    for pi in range(5):
        make_faded_poster(f"Flyer_E_{pi}", (ROOM_W / 2.0 - 0.05 - 0.0535, 6.2 + pi * 0.85, 1.60 + (pi % 2) * 0.35), into_room=-1, kind="band")
    for pi in range(4):
        make_faded_poster(f"Flyer_W_{pi}", (-ROOM_W / 2.0 + 0.05 + 0.0535, 3.6 + pi * 0.9, 1.70 + (pi % 2) * 0.30), into_room=+1, kind="band")
    for di, (dx, dy) in enumerate(((0.0, 4.0), (0.0, 9.0))):
        make_smoke_detector(f"Smoke_{di}", (dx, dy, CEIL))


def main():
    clear_scene()
    build_shell()
    build_stage()
    build_backline()
    build_rig()
    build_floor()
    build_bar()
    build_show_2026_11()
    build_walls_dressing()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/foxhole_bar.glb"))
    print(f"\n[build_foxhole_bar] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
