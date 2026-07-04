"""Cosmic Comics — back office / back room — vol6 placement script.

The second-most-used VN background in the game (43 scenes). Rick's
L-shaped storage-and-office area behind the front room's curtained
EMPLOYEES-ONLY doorway, compressed into the 4 x 5 shell the .tscn
camera preset is tuned to (Background3D.gd "cosmic_comics_back_office":
establishing shot from the south doorway end at 2.30 m, fov 58 —
the north wall is the backdrop; the south opening must stay clear).

Canon sources:
  · vol6_ch3_back_room.json — the definitive prose: "smaller than
    she imagined — an L-shaped storage and office area, lit by a
    single overhead with a pull chain, stacked with long boxes and
    cardboard cartons of new releases still in shrink. There is a
    small desk in one corner, a mini-fridge, a calendar of cats
    from 2022 nobody has taken down." Sam sits on an overturned
    milk crate opposite the desk; the back door has "a bolt Sam
    did not realize was there."
  · vol6_ch12_cosmic.json — Rick's spiral notebook on the desk
    (top drawer), the green folder with the Diamond invoice, the
    Mr. Coffee on the file cabinet (since 2008), the Speak & Spell
    "on the shelf above the file cabinet, dim", the safe in the
    back office (key ring), back door deadbolt.
  · vol6_ch21_cosmic.json — "She turns on the back-office
    computer"; the wanderer looks through the doorway straight at
    "the shelf above the file cabinet" (so that shelf must face
    the south doorway → it lives on the north wall).
  · vol6_ch4_speak_spell.json — the Speak & Spell: 1978 original,
    red housing, crack in the lower-left corner, red speaker
    grille (dim by default), on the shelf behind Rick's desk.
  · lore/planned_community/cosmic_comics.md ("the back room") —
    concrete floor, grey metal shelving banks on the side walls,
    long-box dolly at the back, photocopier in the corner (Konica
    Minolta Bizhub C284e), the desk under the small high window
    facing the alley, THE BACK DOOR WITH ITS THREE LOCKS, the zine
    archive (~11,000 zines sorted by year), the 1985–1991 shelf
    with THE NINE-WAY POTLATCH OF AUGUST in an acid-free sleeve at
    the front, the seven Henderson Donation boxes on the lowest
    shelf at the back (three opened by mid-August).
  · lore/planned_community/rick_cosmic.md — Item III: PHILIP
    DAIGLE'S BOX ("FOR M.D. · FROM HER FATHER · DO NOT OPEN UNTIL
    SHE ASKS"), a wooden box ~18x12x6 in. on the BOTTOM shelf of
    the storage rack, BEHIND a stack of unsold GENERAL STORE
    zines — modeled present but occluded, per Philip's "don't
    tell her about it." Item V: the green velvet couch with the
    band detritus in its cushions (lyrics page, picks, the
    pinch-zine between the cushions).
  · lore/planned_community/maya_daigle.md — the IBM Wheelwriter 3
    on the desk (the Glitch Report drafts).

Register: the shop's unglamorous service side — same decades-old
oak, white long-box corrugate, kraft, brass and velvet constants as
build_cosmic_comics_interior.py so the two rooms read as one shop,
but on a concrete floor with grey steel shelving instead of retail
fixtures. The GLB also stands in for several generic small offices
across vol6 (ch0 Pit Stop office, ch17 home office), so no baked
lettering anywhere — every sign/label panel is a named mesh for
scene-side Label3D: ZineArchive_Sign, ZineYearTab_{i},
Potlatch_SleeveLabel, PhilipBox_TapeLabel, HendersonBox_Label_{i},
Calendar_Cats2022_*, DoorNotice_Paper.

No transparency: the alley window is frame + mullion + an OPAQUE
near-black "night glass" pane (same treatment as the front room's
painted mural glass); the doorway curtain is tied back in opaque
velvet bunches; nothing translucent anywhere.

Scaffold audit (per playbook 2026-07-02 lesson — openings and
intersections first):
  · Kwik Stop fixture vocabulary imported but unused (snack aisle,
    endcap, coffee pots, donut display) — removed.
  · Filing cabinets were embedded 5 cm into the west wall — gone
    (canon has ONE small file cabinet, north wall).
  · Monitor floated 14 cm above the desk — rebuilt seated.
  · Bare bulb cord hung 30 cm BELOW the ceiling, attached to
    nothing — cord now runs from a ceiling rose to the bulb, and
    the canon pull chain exists.
  · Fluorescent fixtures contradicted ch3's "a single overhead
    with a pull chain" — removed.
  · Calendar floated 4.5 cm proud of the east wall — reseated.
  · No window, no back door, bare south gap — all three built.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_door_hinges
from _props.decor import make_calendar, make_faded_poster
from _props.safety import make_smoke_detector, make_hvac_vent
from _props.signage import make_paper_notices_wall

# ── Shell (kept from the original scaffold — .tscn camera + lights
#    are tuned to this footprint; south doorway gap x -1..+1) ─────
ROOM_W = 4.0; ROOM_D = 5.0; CEIL = 2.6
PAL_WALL = {"wall": (0.78, 0.70, 0.58, 1.0), "baseboard": (0.42, 0.32, 0.22, 1.0)}

# Concrete floor (canon: "Concrete floor", cosmic_comics.md)
COL_CONCRETE   = (0.56, 0.54, 0.51, 1.0)
COL_CONC_SEAM  = (0.45, 0.43, 0.41, 1.0)
COL_CONC_STAIN = (0.42, 0.40, 0.37, 1.0)

# ── Shared constants — VERBATIM from build_cosmic_comics_interior.py
#    so the two rooms read as one shop ─────────────────────────────
COL_SHELF_WOOD = (0.40, 0.29, 0.20, 1.0)     # decades-old oak fixtures
COL_SHELF_DARK = (0.26, 0.18, 0.14, 1.0)
COL_LONGBOX    = (0.90, 0.87, 0.80, 1.0)     # white corrugate
COL_LONGBOX_IN = (0.32, 0.28, 0.24, 1.0)
COL_KRAFT      = (0.74, 0.56, 0.34, 1.0)     # cardboard
COL_DIVIDER    = (0.94, 0.92, 0.86, 1.0)     # white divider tab
COL_BRASS      = (0.72, 0.58, 0.28, 1.0)
COL_VELVET_A   = (0.24, 0.14, 0.30, 1.0)     # the doorway curtain
COL_VELVET_B   = (0.19, 0.11, 0.25, 1.0)
COMIC_TINTS = [
    (0.72, 0.24, 0.20, 1.0), (0.24, 0.36, 0.62, 1.0),
    (0.86, 0.70, 0.28, 1.0), (0.46, 0.28, 0.54, 1.0),
    (0.30, 0.52, 0.46, 1.0), (0.80, 0.48, 0.24, 1.0),
    (0.88, 0.84, 0.74, 1.0), (0.22, 0.20, 0.24, 1.0),
]

# ── Back-room-only palette ───────────────────────────────────────
COL_STEEL_SHELF   = (0.58, 0.60, 0.58, 1.0)  # grey metal shelving (canon)
COL_STEEL_DARK    = (0.42, 0.44, 0.42, 1.0)
COL_SERVICE_DOOR  = (0.52, 0.54, 0.55, 1.0)  # institutional gray (ch14 register)
COL_DOOR_FRAME    = (0.38, 0.40, 0.41, 1.0)
COL_NIGHT_GLASS   = (0.09, 0.10, 0.13, 1.0)  # opaque alley-window pane
COL_GREEN_VELVET  = (0.22, 0.36, 0.26, 1.0)  # the 2014 estate-sale couch
COL_GREEN_VELVET2 = (0.17, 0.29, 0.21, 1.0)
COL_SS_BODY       = (0.80, 0.30, 0.16, 1.0)  # 1978 Speak & Spell red
COL_SS_KEYS       = (0.86, 0.80, 0.66, 1.0)
COL_SS_GRILLE     = (0.30, 0.08, 0.06, 1.0)  # dim (canon default state)
COL_WHEELWRITER   = (0.82, 0.78, 0.68, 1.0)  # IBM beige
COL_CRT           = (0.72, 0.70, 0.62, 1.0)  # 2000s office beige
COL_CRT_SCREEN    = (0.10, 0.12, 0.11, 1.0)
COL_MRCOFFEE      = (0.90, 0.88, 0.82, 1.0)
COL_COFFEE        = (0.20, 0.15, 0.11, 1.0)
COL_BASKET_STAIN  = (0.78, 0.68, 0.44, 1.0)  # 17 years of residue (canon)
COL_GREEN_FOLDER  = (0.30, 0.52, 0.34, 1.0)  # the Diamond invoice (ch12)
COL_MILK_CRATE    = (0.70, 0.26, 0.22, 1.0)  # Sam's seat (ch3)
COL_FILE_CAB      = (0.62, 0.62, 0.58, 1.0)
COL_SAFE          = (0.24, 0.25, 0.27, 1.0)
COL_FRIDGE        = (0.88, 0.88, 0.84, 1.0)
COL_SLEEVE        = (0.90, 0.91, 0.90, 1.0)  # acid-free archival sleeve
COL_MASKING_TAPE  = (0.88, 0.80, 0.60, 1.0)  # Philip's box label
COL_SHRINK        = (0.86, 0.88, 0.90, 1.0)  # shrink-wrap band highlight


# ═════════════════════════════════════════════════════════════════
# SHELL — concrete floor, aged service-side walls, drop ceiling.
# Footprint unchanged from the scaffold (camera-tuned). Crown
# molding removed — a concrete-floored stockroom doesn't get the
# front room's purple-stained crown.
# ═════════════════════════════════════════════════════════════════
def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_CONCRETE, "seam": COL_CONC_SEAM})
    # Wear: dolly-track scuffs + an old spill shadow (deterministic)
    for si, (sx, sy, sw, sd) in enumerate([
            (0.55, 2.30, 0.50, 1.60),    # dolly track toward the door
            (-0.90, 3.90, 0.70, 0.55),   # under the desk chair
            (1.30, 3.60, 0.55, 0.45)]):  # photocopier drag marks
        make_box(f"Floor_Wear_{si}", (sx, sy, 0.008), (sw, sd, 0.002), COL_CONC_STAIN)
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)


# ═════════════════════════════════════════════════════════════════
# SOUTH DOORWAY — the seam to build_cosmic_comics_interior (its
# north-wall curtained EMPLOYEES-ONLY doorway, seen from the back).
# Oak posts + the brass rod + the velvet curtain TIED BACK in
# bunches at both jambs — the 2 m opening itself stays clear
# because the establishing camera shoots from/through it.
# ═════════════════════════════════════════════════════════════════
def build_south_doorway():
    for sgn in (-1, +1):
        make_box(f"Doorway_Post_{sgn:+d}", (sgn * 1.04, 0.0, 1.00),
                 (0.08, 0.24, 2.00), COL_SHELF_WOOD)
    make_box("Doorway_Head", (0.0, 0.0, 2.06), (2.16, 0.24, 0.12), COL_SHELF_WOOD)
    # Brass rod on the room-side face, matching the front room's
    make_cyl("Doorway_CurtainRod", (0.0, 0.16, 1.95), 0.015, 2.10, COL_BRASS, axis='X')
    for sgn in (-1, +1):
        tag = 'W' if sgn < 0 else 'E'
        # Two layered velvet bunches per side, gathered off the opening
        make_box(f"Doorway_CurtainBunch_{tag}_A", (sgn * 0.87, 0.16, 1.02),
                 (0.20, 0.055, 1.82), COL_VELVET_A)
        make_box(f"Doorway_CurtainBunch_{tag}_B", (sgn * 0.80, 0.185, 1.10),
                 (0.10, 0.045, 1.62), COL_VELVET_B)
        make_box(f"Doorway_TieBand_{tag}", (sgn * 0.87, 0.155, 1.10),
                 (0.22, 0.075, 0.06), COL_BRASS)


# ═════════════════════════════════════════════════════════════════
# SERVICE DOOR — north wall, east side. "The back door with its
# three locks" (cosmic_comics.md): knob lock (the "bottom lock"),
# deadbolt (the one Maya tests twice, ch12/ch21), and the surface
# slide bolt "Sam did not realize was there" (ch3). Institutional
# gray metal service door (register per ch14's service doors).
# ═════════════════════════════════════════════════════════════════
def build_service_door():
    dx = 1.15                       # door centerline
    wall_face = ROOM_D - 0.10       # 4.90 interior face
    # Steel frame — jambs + head, proud of the wall face (never
    # buried past it — the wall is solid, this door never opens)
    for sgn in (-1, +1):
        make_box(f"BackDoor_Jamb_{sgn:+d}", (dx + sgn * 0.505, wall_face - 0.045, 1.04),
                 (0.06, 0.07, 2.08), COL_DOOR_FRAME)
    make_box("BackDoor_Head", (dx, wall_face - 0.045, 2.10), (1.07, 0.07, 0.08), COL_DOOR_FRAME)
    # Leaf — flush steel, sits just inside the frame
    make_box("BackDoor_Leaf", (dx, wall_face - 0.035, 1.02), (0.95, 0.05, 2.04), COL_SERVICE_DOOR)
    make_box("BackDoor_KickPlate", (dx, wall_face - 0.065, 0.18), (0.88, 0.012, 0.30), P.METAL_STEEL)
    # THE THREE LOCKS, stacked up the west (latch) edge:
    lx = dx - 0.36
    #  1 · knob with round rose — the "bottom lock" (ch21)
    make_cyl("BackDoor_KnobRose", (lx, wall_face - 0.07, 0.95), 0.045, 0.015, P.METAL_STEEL, axis='Y')
    make_cyl("BackDoor_Knob", (lx, wall_face - 0.115, 0.95), 0.032, 0.075, P.METAL_STEEL, axis='Y')
    #  2 · deadbolt — the one Maya tests, then tests again (ch12)
    make_box("BackDoor_DeadboltPlate", (lx, wall_face - 0.072, 1.18), (0.07, 0.012, 0.11), COL_BRASS)
    make_cyl("BackDoor_DeadboltThumb", (lx, wall_face - 0.090, 1.18), 0.018, 0.028, COL_BRASS, axis='Y')
    #  3 · surface-mounted slide bolt — the bolt Sam didn't see (ch3)
    make_box("BackDoor_SlideBoltBody", (lx + 0.05, wall_face - 0.075, 1.52), (0.20, 0.018, 0.05), P.METAL_STEEL)
    make_cyl("BackDoor_SlideBoltRod", (lx + 0.05, wall_face - 0.082, 1.52), 0.011, 0.26, P.METAL_BLACK, axis='X')
    make_cyl("BackDoor_SlideBoltHandle", (lx + 0.11, wall_face - 0.105, 1.52), 0.008, 0.05, P.METAL_BLACK, axis='Y')
    make_box("BackDoor_SlideBoltKeep", (lx - 0.145, wall_face - 0.072, 1.52), (0.05, 0.014, 0.05), P.METAL_STEEL)
    # Hinges on the east edge + overhead closer arm
    make_door_hinges("BackDoor_Hinge", edge_x=dx + 0.46, edge_y=wall_face - 0.04,
                     edge_z_centers=[0.30, 1.02, 1.78], axis='X')
    make_box("BackDoor_CloserBody", (dx + 0.22, wall_face - 0.075, 2.00), (0.26, 0.05, 0.07), P.METAL_BLACK)
    make_box("BackDoor_CloserArm", (dx + 0.10, wall_face - 0.13, 2.04), (0.34, 0.06, 0.02), P.METAL_BLACK)
    # Rubber mat inside the door + a taped delivery notice beside it
    make_box("BackDoor_Mat", (dx, 4.55, 0.008), (0.90, 0.55, 0.012), P.RUBBER_MAT)
    make_box("DoorNotice_Paper", (1.76, wall_face - 0.015, 1.60), (0.22, 0.012, 0.28), P.PAPER_AGED)


# ═════════════════════════════════════════════════════════════════
# DESK ZONE — NW corner, "the back-office desk under the small high
# window that faces the alley" (cosmic_comics.md). On it: the IBM
# Wheelwriter 3 (Maya's Glitch Report drafts), the back-office
# computer (ch21), Rick's spiral notebook (ch12, lives in the top
# drawer), the green folder with the Friday Diamond invoice (ch12).
# Under it: the safe from the key-ring list (ch12) and the tower.
# ═════════════════════════════════════════════════════════════════
def build_desk_zone():
    wall_face = ROOM_D - 0.10   # 4.90
    dx, dy = -1.05, 4.52        # desk center; top 1.60 x 0.72
    make_box("Desk_Top", (dx, dy, 0.74), (1.60, 0.72, 0.045), COL_SHELF_WOOD)
    for li, (lox, loy) in enumerate([(-0.74, -0.30), (+0.74, -0.30), (-0.74, +0.30), (+0.74, +0.30)]):
        make_box(f"Desk_Leg_{li}", (dx + lox, dy + loy, 0.36), (0.05, 0.05, 0.72), COL_SHELF_DARK)
    make_box("Desk_Apron", (dx, dy + 0.30, 0.62), (1.48, 0.04, 0.16), COL_SHELF_DARK)
    # Top drawer (where the spiral notebook goes at close, ch12)
    make_box("Desk_DrawerFront", (dx + 0.35, dy - 0.345, 0.63), (0.62, 0.025, 0.14), COL_SHELF_WOOD)
    make_box("Desk_DrawerKnob", (dx + 0.35, dy - 0.370, 0.63), (0.05, 0.025, 0.03), COL_BRASS)
    # IBM Wheelwriter 3 — on this desk since 1991 (cosmic_comics.md);
    # Maya pays for the ribbons out of her tip jar
    wx = dx - 0.48
    make_box("Wheelwriter_Body", (wx, dy + 0.02, 0.815), (0.44, 0.40, 0.11), COL_WHEELWRITER)
    make_box("Wheelwriter_KeyBank", (wx, dy - 0.09, 0.878), (0.38, 0.20, 0.022), (0.62, 0.58, 0.50, 1.0))
    make_cyl("Wheelwriter_Platen", (wx, dy + 0.13, 0.895), 0.028, 0.40, P.METAL_BLACK, axis='X')
    make_cyl("Wheelwriter_PlatenKnob", (wx + 0.22, dy + 0.13, 0.895), 0.016, 0.03, P.METAL_BLACK, axis='X')
    make_box("Wheelwriter_Page", (wx, dy + 0.155, 1.00), (0.21, 0.006, 0.21), P.PAPER)
    # Back-office computer (ch21: "She turns on the back-office
    # computer") — small beige CRT + keyboard, tower under the desk
    make_box("Crt_Body", (dx + 0.50, dy + 0.10, 0.93), (0.36, 0.34, 0.31), COL_CRT)
    make_box("Crt_Screen", (dx + 0.50, dy - 0.075, 0.945), (0.28, 0.012, 0.22), COL_CRT_SCREEN)
    make_box("Crt_Foot", (dx + 0.50, dy + 0.08, 0.775), (0.26, 0.24, 0.025), COL_CRT)
    make_box("Keyboard", (dx + 0.48, dy - 0.22, 0.775), (0.36, 0.13, 0.022), (0.68, 0.66, 0.58, 1.0))
    make_box("Pc_Tower", (dx + 0.52, dy + 0.05, 0.20), (0.18, 0.42, 0.40), COL_CRT)
    # Rick's spiral notebook — open on the desk since Sunday (ch12/ch21)
    make_box("SpiralNotebook", (dx - 0.02, dy - 0.18, 0.775), (0.24, 0.18, 0.015), P.PAPER)
    make_cyl("SpiralNotebook_Coil", (dx - 0.02, dy - 0.085, 0.782), 0.008, 0.23, P.METAL_STEEL, axis='X')
    # The green folder — the Friday Diamond invoice Curtis runs (ch12)
    make_box("GreenFolder", (dx + 0.24, dy - 0.13, 0.772), (0.26, 0.20, 0.012), COL_GREEN_FOLDER)
    make_box("GreenFolder_Sheet", (dx + 0.26, dy - 0.12, 0.780), (0.21, 0.16, 0.004), P.PAPER)
    # Loose paper strata + pen cup
    for pi in range(3):
        make_box(f"Desk_Papers_{pi}", (dx - 0.30 + pi * 0.09, dy + 0.24 - pi * 0.03, 0.772 + pi * 0.008),
                 (0.20, 0.26, 0.008), (P.PAPER, P.PAPER_AGED, P.NEWSPRINT)[pi])
    make_cyl("PenCup", (dx + 0.73, dy + 0.26, 0.795), 0.032, 0.09, COL_SHELF_DARK)
    make_cyl("PenCup_Pen", (dx + 0.72, dy + 0.26, 0.865), 0.005, 0.09, COMIC_TINTS[1])
    # Desk chair, pushed half-in (Rick's / Curtis's / Maya's seat)
    chx, chy = -1.00, 3.86
    make_box("DeskChair_Seat", (chx, chy, 0.45), (0.42, 0.42, 0.04), COL_SHELF_WOOD)
    make_box("DeskChair_Back", (chx, chy + 0.19, 0.78), (0.40, 0.04, 0.42), COL_SHELF_WOOD)
    for li, (lox, loy) in enumerate([(-0.17, -0.17), (+0.17, -0.17), (-0.17, +0.17), (+0.17, +0.17)]):
        make_box(f"DeskChair_Leg_{li}", (chx + lox, chy + loy, 0.22), (0.04, 0.04, 0.44), COL_SHELF_DARK)
    # The safe (ch12 key ring: "safe in the back office") — squat
    # steel box under the desk's east end
    make_box("Safe_Body", (dx + 0.45, dy + 0.12, 0.19), (0.36, 0.38, 0.38), COL_SAFE)
    make_cyl("Safe_Dial", (dx + 0.45, dy - 0.085, 0.22), 0.035, 0.02, P.METAL_STEEL, axis='Y')
    make_box("Safe_Handle", (dx + 0.34, dy - 0.082, 0.13), (0.03, 0.015, 0.09), P.METAL_STEEL)
    # The small high window facing the alley (cosmic_comics.md) —
    # frame + mullion + OPAQUE night-dark pane (no-transparency rule;
    # same opaque-glass treatment as the front room's mural windows)
    # (all pieces sit SOUTH of the wall face at y=4.90 — the pane
    # must be in front of the solid wall or it renders invisible)
    wz = 2.12
    make_box("AlleyWindow_Pane", (dx, wall_face - 0.015, wz), (0.86, 0.012, 0.46), COL_NIGHT_GLASS)
    make_box("AlleyWindow_Sill", (dx, wall_face - 0.045, wz - 0.26), (1.00, 0.07, 0.06), COL_SHELF_WOOD)
    make_box("AlleyWindow_Head", (dx, wall_face - 0.045, wz + 0.26), (1.00, 0.07, 0.06), COL_SHELF_WOOD)
    for sgn in (-1, +1):
        make_box(f"AlleyWindow_Jamb_{sgn:+d}", (dx + sgn * 0.47, wall_face - 0.045, wz),
                 (0.06, 0.07, 0.46), COL_SHELF_WOOD)
    make_box("AlleyWindow_Mull", (dx, wall_face - 0.032, wz), (0.04, 0.03, 0.46), COL_SHELF_DARK)


# ═════════════════════════════════════════════════════════════════
# FILE-CABINET ZONE — north wall between desk and door, dead in the
# doorway sightline (ch21: the wanderer, from the shop floor, looks
# straight at "the shelf above the file cabinet"). The small file
# cabinet, the Mr. Coffee (since 2008; carafe replaced twice, both
# times by Curtis dropping it), the shelf, THE SPEAK & SPELL (dim),
# and the specific outlet it can be unplugged from (ch12).
# ═════════════════════════════════════════════════════════════════
def build_file_cabinet_zone():
    wall_face = ROOM_D - 0.10
    cx, cy = 0.25, 4.64
    # Small two-drawer file cabinet ("The file cabinet is small.")
    make_box("FileCab_Body", (cx, cy, 0.36), (0.45, 0.48, 0.72), COL_FILE_CAB)
    for di in range(2):
        make_box(f"FileCab_Drawer_{di}", (cx, cy - 0.245, 0.54 - di * 0.33),
                 (0.40, 0.015, 0.27), (0.72, 0.72, 0.68, 1.0))
        make_box(f"FileCab_Handle_{di}", (cx, cy - 0.262, 0.58 - di * 0.33),
                 (0.12, 0.015, 0.025), P.METAL_BLACK)
    # Mr. Coffee — brewed by Rick at morning, Curtis at noon, Maya
    # at three, Wren at five (cosmic_comics.md)
    mx = cx - 0.08
    make_box("MrCoffee_Base", (mx, cy + 0.02, 0.735), (0.20, 0.24, 0.03), COL_MRCOFFEE)
    make_box("MrCoffee_Tower", (mx, cy + 0.10, 0.87), (0.20, 0.10, 0.30), COL_MRCOFFEE)
    make_box("MrCoffee_Basket", (mx, cy + 0.015, 0.955), (0.16, 0.14, 0.055), COL_BASKET_STAIN)
    make_cyl("MrCoffee_Carafe", (mx, cy - 0.005, 0.815), 0.062, 0.13, COL_COFFEE)
    make_box("MrCoffee_CarafeHandle", (mx - 0.075, cy - 0.005, 0.82), (0.015, 0.03, 0.10), P.METAL_BLACK)
    make_box("MrCoffee_Mug", (cx + 0.145, cy - 0.06, 0.765), (0.07, 0.07, 0.075), COMIC_TINTS[4])
    make_box("MrCoffee_Filters", (cx + 0.145, cy + 0.12, 0.75), (0.11, 0.11, 0.035), P.PAPER)
    # The shelf above the file cabinet (ch12/ch21)
    make_box("HighShelf_Plank", (cx + 0.05, cy + 0.06, 1.50), (0.62, 0.26, 0.035), COL_SHELF_WOOD)
    for sgn in (-1, +1):
        make_box(f"HighShelf_Bracket_{sgn:+d}", (cx + 0.05 + sgn * 0.24, cy + 0.15, 1.42),
                 (0.04, 0.14, 0.13), P.METAL_BLACK)
    # THE SPEAK & SPELL — 1978 original, red housing, dim red grille,
    # crack in the lower-left corner since 2014 (ch4/ch12/ch21).
    # Face-out toward the doorway sightline.
    sx = cx + 0.02
    make_box("SpeakAndSpell_Body", (sx, cy + 0.10, 1.625), (0.27, 0.05, 0.21), COL_SS_BODY)
    make_box("SpeakAndSpell_KeyPanel", (sx - 0.025, cy + 0.072, 1.60), (0.15, 0.008, 0.11), COL_SS_KEYS)
    make_cyl("SpeakAndSpell_Grille", (sx + 0.085, cy + 0.070, 1.655), 0.036, 0.010, COL_SS_GRILLE, axis='Y')
    make_box("SpeakAndSpell_Display", (sx - 0.02, cy + 0.070, 1.685), (0.14, 0.006, 0.028), (0.16, 0.20, 0.16, 1.0))
    make_cyl("SpeakAndSpell_Handle", (sx, cy + 0.10, 1.745), 0.012, 0.16, COL_SS_BODY, axis='X')
    make_box("SpeakAndSpell_Crack", (sx - 0.115, cy + 0.072, 1.545), (0.035, 0.004, 0.006), P.METAL_BLACK)
    # The outlet ("walk to the back and unplug it. You know which
    # outlet." — ch12) + the cord dropping to it
    make_box("Outlet_Plate", (cx + 0.42, wall_face - 0.012, 0.38), (0.08, 0.012, 0.12), P.PVC_WHITE)
    make_cyl("SpeakAndSpell_Cord_V", (cx + 0.36, wall_face - 0.05, 0.96), 0.006, 1.06, P.METAL_BLACK)
    make_cyl("SpeakAndSpell_Cord_Top", (cx + 0.25, wall_face - 0.09, 1.49), 0.006, 0.22, P.METAL_BLACK, axis='X')


# ═════════════════════════════════════════════════════════════════
# ZINE ARCHIVE — west wall, north run. "A six-foot row of shelving
# ... forty years of regional zines, sorted by year and labeled in
# Rick's hand" — ~11,000 issues (rick_cosmic.md I). Grey metal
# shelving per cosmic_comics.md. On the 1985–1991 shelf, in an
# acid-free sleeve AT THE FRONT, separate from the year sorting:
# THE NINE-WAY POTLATCH OF AUGUST. On the bottom shelf, BEHIND a
# stack of unsold GENERAL STORE zines: Philip Daigle's box —
# "FOR M.D. · FROM HER FATHER · DO NOT OPEN UNTIL SHE ASKS"
# (rick_cosmic.md III). Present, occluded from the camera by the
# zine stack, never announced: Rick's nine-year secret.
# ═════════════════════════════════════════════════════════════════
def build_zine_archive():
    wx = -1.70                 # bank centerline; wall face at -1.90
    y0, y1 = 2.30, 4.10        # six-foot run (1.80 m)
    yc = (y0 + y1) / 2.0
    for pi, (px, py) in enumerate([(-1.88, y0 + 0.03), (-1.52, y0 + 0.03),
                                   (-1.88, y1 - 0.03), (-1.52, y1 - 0.03)]):
        make_box(f"ZineBank_Post_{pi}", (px, py, 1.20), (0.045, 0.045, 2.40), COL_STEEL_DARK)
    shelf_zs = (0.15, 0.65, 1.15, 1.65, 2.15)
    for si, sz in enumerate(shelf_zs):
        make_box(f"ZineBank_Shelf_{si}", (wx, yc, sz), (0.40, 1.80, 0.04), COL_STEEL_SHELF)
    # Zine mass — vertical spine runs + flat stacks, muted paper
    # stock with the occasional comic tint; deterministic variation
    for si, sz in enumerate(shelf_zs[1:], start=1):
        for k in range(11):
            ky = y0 + 0.14 + k * 0.145
            h = (0.24, 0.28, 0.21, 0.26)[(si * 3 + k) % 4]
            tint = (P.NEWSPRINT, P.PAPER_AGED, P.PAPER,
                    COMIC_TINTS[(si * 5 + k) % 8])[(si + k) % 4]
            make_box(f"ZineRun_{si}_{k}", (wx - 0.02, ky, sz + 0.02 + h / 2.0),
                     (0.24, 0.115, h), tint)
        # Flat overflow stack at the north end of each shelf
        make_box(f"ZineStack_{si}", (wx - 0.02, y1 - 0.17, sz + 0.085),
                 (0.26, 0.22, 0.13), (P.PAPER_AGED, P.NEWSPRINT)[si % 2])
        # Rick's hand-lettered year tab on the shelf edge (Label3D
        # scene-side; 1985–1991 is shelf index 2)
        make_box(f"ZineYearTab_{si}", (wx + 0.205, y0 + 0.28 + si * 0.30, sz + 0.005),
                 (0.012, 0.14, 0.07), COL_DIVIDER)
    # THE NINE-WAY POTLATCH OF AUGUST — acid-free sleeve propped
    # face-out at the front of the 1985–1991 shelf (z 1.15)
    make_box("Potlatch_Sleeve", (wx + 0.13, 3.16, 1.335), (0.022, 0.24, 0.31), COL_SLEEVE)
    make_box("Potlatch_Booklet", (wx + 0.145, 3.16, 1.325), (0.010, 0.19, 0.26), P.PAPER_AGED)
    make_box("Potlatch_SleeveLabel", (wx + 0.155, 3.16, 1.22), (0.006, 0.12, 0.045), P.PAPER)
    # BOTTOM SHELF — the unsold GENERAL STORE stack (Maya's
    # grandfather's minicomics, though she doesn't know that yet)…
    make_box("GeneralStore_Stack_A", (wx, 3.42, 0.275), (0.26, 0.24, 0.21), P.NEWSPRINT)
    make_box("GeneralStore_Stack_B", (wx - 0.01, 3.44, 0.395), (0.23, 0.21, 0.03), COMIC_TINTS[6])
    # …and BEHIND it (north of it, hidden from the doorway camera),
    # pushed against the wall: PHILIP'S BOX. Wooden, ~46x30x15 cm,
    # masking-tape label on the lid in Rick's hand.
    make_box("PhilipBox_Body", (-1.74, 3.86, 0.245), (0.28, 0.44, 0.13), COL_SHELF_WOOD)
    make_box("PhilipBox_Lid", (-1.74, 3.86, 0.320), (0.30, 0.46, 0.025), COL_SHELF_DARK)
    make_box("PhilipBox_TapeLabel", (-1.74, 3.86, 0.336), (0.20, 0.09, 0.006), COL_MASKING_TAPE)
    # Small paper sign above the bank (Label3D scene-side —
    # "THE ARCHIVE · ASK RICK")
    make_box("ZineArchive_Sign", (-1.885, yc, 2.44), (0.012, 0.56, 0.14), P.PAPER_AGED)


# ═════════════════════════════════════════════════════════════════
# COUCH ZONE — west wall, south run. The green velvet couch Rick
# salvaged from an estate sale in 2014; the band's break couch,
# with the accumulated cushion detritus: Diego's lyrics page, a
# guitar pick or two, the bassist's pinch-zine slid between the
# cushions (rick_cosmic.md V). Above it, a sun-faded regional tour
# poster + taped band flyers (Suburban Blight's world).
# ═════════════════════════════════════════════════════════════════
def build_couch_zone():
    cx, cy = -1.48, 1.15   # body center; couch backs onto the west wall
    make_box("Couch_Base", (cx, cy, 0.20), (0.78, 1.90, 0.24), COL_GREEN_VELVET2)
    make_box("Couch_Back", (cx - 0.315, cy, 0.55), (0.16, 1.90, 0.50), COL_GREEN_VELVET)
    for sgn in (-1, +1):
        make_box(f"Couch_Arm_{sgn:+d}", (cx + 0.02, cy + sgn * 0.87, 0.44),
                 (0.72, 0.16, 0.26), COL_GREEN_VELVET)
    for ci in range(2):
        sy = cy - 0.395 + ci * 0.79
        make_box(f"Couch_SeatCushion_{ci}", (cx + 0.06, sy, 0.375),
                 (0.56, 0.74, 0.11), (COL_GREEN_VELVET, COL_GREEN_VELVET2)[ci])
        make_box(f"Couch_BackCushion_{ci}", (cx - 0.20, sy, 0.62),
                 (0.14, 0.72, 0.36), (COL_GREEN_VELVET2, COL_GREEN_VELVET)[ci])
    for fi, (fy,) in enumerate([(cy - 0.80,), (cy + 0.80,)]):
        make_box(f"Couch_Foot_F_{fi}", (cx + 0.32, fy, 0.04), (0.06, 0.06, 0.08), COL_SHELF_DARK)
        make_box(f"Couch_Foot_B_{fi}", (cx - 0.32, fy, 0.04), (0.06, 0.06, 0.08), COL_SHELF_DARK)
    # Cushion detritus (rick_cosmic.md V)
    make_box("Couch_LyricsPage", (cx + 0.10, cy - 0.30, 0.436), (0.20, 0.15, 0.004), P.PAPER)
    make_box("Couch_GuitarPick_0", (cx + 0.16, cy + 0.22, 0.434), (0.028, 0.024, 0.004), COMIC_TINTS[0])
    make_box("Couch_GuitarPick_1", (cx - 0.02, cy + 0.55, 0.434), (0.028, 0.024, 0.004), COMIC_TINTS[2])
    # The pinch-zine, corner proud between the two seat cushions
    make_box("Couch_PinchZine", (cx + 0.08, cy, 0.445), (0.14, 0.020, 0.055), P.PAPER_AGED)
    # Wall above: faded tour poster + taped band flyers
    make_faded_poster("Couch_TourPoster", (-1.895, 1.55, 1.80))
    make_paper_notices_wall("Couch_Flyer", wall_x=-1.88, wall_face_sign=+1,
                            run_center_y=0.62, base_z=0.0, notices=[
        (-0.12, 1.85, 0.22, 0.30, P.PAPER),
        (+0.20, 1.72, 0.18, 0.24, (0.86, 0.46, 0.22, 1.0)),
    ])


# ═════════════════════════════════════════════════════════════════
# EAST STORAGE — the overflow bank: long boxes, new-release cartons
# still in shrink (ch3), bags-and-boards. Bottom shelf at the back:
# the HENDERSON DONATION BOXES — seven; three opened by mid-August
# (cosmic_comics.md). Plus the photocopier in the corner (Konica
# Minolta Bizhub C284e — prints the Glitch Report), the long-box
# dolly at the back, the mini-fridge, the 2022 cat calendar nobody
# has taken down, and the breaker panel.
# ═════════════════════════════════════════════════════════════════
def build_east_storage():
    wallf = ROOM_W / 2.0 - 0.10   # +1.90 interior face
    # ── Shelving bank, y 1.20..2.90 ──────────────────────────────
    bx = 1.68
    for pi, (px, py) in enumerate([(1.50, 1.23), (1.86, 1.23), (1.50, 2.87), (1.86, 2.87)]):
        make_box(f"StoreBank_Post_{pi}", (px, py, 1.20), (0.045, 0.045, 2.40), COL_STEEL_DARK)
    for si, sz in enumerate((0.15, 0.75, 1.35, 1.95)):
        make_box(f"StoreBank_Shelf_{si}", (bx, 2.05, sz), (0.40, 1.70, 0.04), COL_STEEL_SHELF)
    # Long boxes on shelf 2 (lids on, white corrugate — same boxes
    # as the front room's browsing tables)
    for li in range(2):
        ly = 1.62 + li * 0.82
        make_box(f"StoreBank_LongBox_{li}", (bx, ly, 1.51), (0.34, 0.74, 0.28), COL_LONGBOX)
        make_box(f"StoreBank_LongBoxLid_{li}", (bx, ly, 1.665), (0.38, 0.78, 0.03), COL_LONGBOX)
    # New-release cartons still in shrink on shelf 3 (ch3) — kraft
    # with a pale shrink-band highlight
    for ki in range(3):
        ky = 1.50 + ki * 0.56
        make_box(f"ShrinkCarton_{ki}", (bx, ky, 2.155), (0.34, 0.44, 0.32), COL_KRAFT)
        make_box(f"ShrinkCarton_{ki}_Band", (bx, ky, 2.16), (0.36, 0.12, 0.30), COL_SHRINK)
    # Bags-and-boards supply box on shelf 1
    make_box("BagsBoards_Box", (bx, 1.52, 0.90), (0.32, 0.40, 0.24), COL_LONGBOX)
    make_box("BagsBoards_Boards", (bx, 2.10, 0.86), (0.28, 0.34, 0.14), COL_DIVIDER)
    # ── HENDERSON DONATION BOXES — 4 on the bottom shelf… ────────
    for hi in range(4):
        hy = 1.44 + hi * 0.44
        opened = hi < 2   # three opened total (2 here + 1 on floor)
        make_box(f"HendersonBox_{hi}", (bx, hy, 0.335), (0.36, 0.40, 0.29), COL_KRAFT,
                 open_faces={'+Z'} if opened else None)
        if opened:
            make_box(f"HendersonBox_{hi}_Inner", (bx, hy, 0.345), (0.32, 0.36, 0.02), COL_LONGBOX_IN)
            make_box(f"HendersonBox_{hi}_Zines", (bx - 0.03, hy, 0.42), (0.22, 0.28, 0.13),
                     (P.NEWSPRINT, P.PAPER_AGED)[hi % 2])
            make_box(f"HendersonBox_{hi}_LidOff", (bx - 0.185, hy + 0.05, 0.30),
                     (0.025, 0.40, 0.30), COL_KRAFT)
        else:
            make_box(f"HendersonBox_{hi}_Lid", (bx, hy, 0.495), (0.40, 0.44, 0.035), COL_KRAFT)
        make_box(f"HendersonBox_Label_{hi}", (bx - 0.185 - (0.03 if opened else 0.0),
                 hy - 0.10, 0.30 if not opened else 0.24), (0.012, 0.16, 0.10), P.PAPER)
    # …and the remaining 3 stacked on the floor south of the bank
    make_box("HendersonBox_4", (1.60, 0.96, 0.20), (0.42, 0.36, 0.40), COL_KRAFT,
             open_faces={'+Z'})
    make_box("HendersonBox_4_Zines", (1.58, 0.96, 0.30), (0.30, 0.26, 0.16), P.NEWSPRINT)
    make_box("HendersonBox_5", (1.10, 0.92, 0.19), (0.40, 0.34, 0.38), COL_KRAFT)
    make_box("HendersonBox_5_Lid", (1.10, 0.92, 0.40), (0.44, 0.38, 0.035), COL_KRAFT)
    make_box("HendersonBox_6", (1.10, 0.92, 0.60), (0.38, 0.32, 0.34), COL_KRAFT)
    make_box("HendersonBox_Label_4", (1.60, 0.77, 0.22), (0.16, 0.012, 0.10), P.PAPER)
    make_box("HendersonBox_Label_5", (1.10, 0.74, 0.19), (0.16, 0.012, 0.10), P.PAPER)
    # ── Long-box dolly "at the back" (cosmic_comics.md) ──────────
    dyy = 3.22
    for sgn in (-1, +1):
        make_cyl(f"Dolly_Wheel_{sgn:+d}", (1.62 + sgn * 0.20, dyy + 0.16, 0.09),
                 0.09, 0.05, P.RUBBER_MAT, axis='X')
    make_box("Dolly_ToePlate", (1.60, dyy - 0.06, 0.035), (0.46, 0.34, 0.02), P.METAL_STEEL)
    for sgn in (-1, +1):
        make_box(f"Dolly_Rail_{sgn:+d}", (1.60 + sgn * 0.18, dyy + 0.17, 0.70),
                 (0.035, 0.035, 1.40), P.METAL_STEEL)
    for ci in range(3):
        make_box(f"Dolly_Crossbar_{ci}", (1.60, dyy + 0.17, 0.40 + ci * 0.42),
                 (0.36, 0.03, 0.035), P.METAL_STEEL)
    make_box("Dolly_LongBox_0", (1.60, dyy - 0.04, 0.20), (0.34, 0.30, 0.30), COL_LONGBOX)
    make_box("Dolly_LongBox_1", (1.60, dyy - 0.02, 0.50), (0.32, 0.28, 0.28), COL_LONGBOX)
    # ── Photocopier — Konica Minolta Bizhub C284e (2018, refurb) ─
    px, py = 1.52, 3.92
    make_box("Photocopier_Base", (px, py, 0.30), (0.60, 0.58, 0.60), (0.78, 0.78, 0.74, 1.0))
    make_box("Photocopier_Drawer_0", (px - 0.315, py, 0.22), (0.02, 0.50, 0.14), (0.62, 0.62, 0.60, 1.0))
    make_box("Photocopier_Drawer_1", (px - 0.315, py, 0.40), (0.02, 0.50, 0.14), (0.62, 0.62, 0.60, 1.0))
    make_box("Photocopier_Body", (px, py, 0.75), (0.56, 0.54, 0.30), (0.84, 0.84, 0.80, 1.0))
    make_box("Photocopier_TrayGap", (px - 0.29, py, 0.68), (0.02, 0.40, 0.09), (0.20, 0.20, 0.20, 1.0))
    make_box("Photocopier_OutSheet", (px - 0.27, py, 0.645), (0.06, 0.28, 0.004), P.PAPER)
    make_box("Photocopier_Lid", (px + 0.04, py, 0.925), (0.46, 0.50, 0.05), (0.62, 0.62, 0.60, 1.0))
    make_box("Photocopier_Panel", (px - 0.20, py - 0.20, 0.925), (0.16, 0.12, 0.03), (0.30, 0.32, 0.32, 1.0))
    make_box("Photocopier_GoLight", (px - 0.17, py - 0.24, 0.945), (0.03, 0.03, 0.008), (0.34, 0.72, 0.38, 1.0))
    # Paper reams stacked beside it (Rick over-orders a ream a
    # quarter so Maya's General Store supply never runs out)
    for ri in range(3):
        make_box(f"PaperReam_{ri}", (1.62, 3.44, 0.045 + ri * 0.075),
                 (0.24, 0.30, 0.07), (P.PAPER, COL_DIVIDER)[ri % 2])
    # ── Mini-fridge (ch3) + the 2022 cat calendar above it ───────
    fx, fy = 1.62, 0.50
    make_box("MiniFridge_Body", (fx, fy, 0.425), (0.50, 0.48, 0.85), COL_FRIDGE)
    make_box("MiniFridge_DoorSeam", (fx - 0.255, fy, 0.42), (0.012, 0.44, 0.76), (0.66, 0.66, 0.62, 1.0))
    make_box("MiniFridge_Handle", (fx - 0.27, fy - 0.19, 0.60), (0.02, 0.03, 0.24), P.METAL_BLACK)
    make_box("MiniFridge_TopMug", (fx - 0.06, fy + 0.08, 0.885), (0.07, 0.07, 0.07), COMIC_TINTS[3])
    # "a calendar of cats from 2022 nobody has taken down" (ch3)
    make_calendar("Calendar_Cats2022", (wallf - 0.005, 0.52, 1.72))
    make_box("Calendar_Cats2022_CatPhoto", (wallf - 0.012, 0.52, 1.85),
             (0.004, 0.32, 0.20), (0.72, 0.58, 0.40, 1.0))
    # ── Breaker panel, east wall north end ───────────────────────
    make_box("BreakerPanel_Box", (wallf - 0.025, 4.42, 1.65), (0.05, 0.30, 0.44), COL_STEEL_SHELF)
    make_box("BreakerPanel_Door", (wallf - 0.055, 4.42, 1.65), (0.012, 0.26, 0.40), COL_STEEL_DARK)
    make_box("BreakerPanel_Conduit", (wallf - 0.035, 4.42, 2.28), (0.035, 0.035, 0.82), P.PVC_WHITE)


# ═════════════════════════════════════════════════════════════════
# CENTER FLOOR — the overturned milk crate opposite the desk (ch3:
# Sam's seat), and the mid-room long-box stack ("stacked with long
# boxes", ch3). The camera lane down the middle stays walkable.
# ═════════════════════════════════════════════════════════════════
def build_center_floor():
    # Overturned milk crate — open side down
    mx, my = 0.10, 3.50
    make_box("MilkCrate_Body", (mx, my, 0.145), (0.33, 0.33, 0.29), COL_MILK_CRATE,
             open_faces={'-Z'})
    for gi in range(2):
        make_box(f"MilkCrate_TopGroove_{gi}", (mx, my - 0.08 + gi * 0.16, 0.292),
                 (0.29, 0.03, 0.004), (0.52, 0.18, 0.15, 1.0))
    for sgn in (-1, +1):
        make_box(f"MilkCrate_Slot_{sgn:+d}", (mx + sgn * 0.167, my, 0.23),
                 (0.004, 0.14, 0.05), (0.30, 0.10, 0.09, 1.0))
    # Long-box stack, two crossed + one open on top with comics
    make_box("FloorStack_LongBox_0", (0.95, 2.42, 0.15), (0.74, 0.32, 0.30), COL_LONGBOX)
    make_box("FloorStack_LongBox_1", (0.95, 2.40, 0.45), (0.70, 0.30, 0.30), COL_LONGBOX)
    make_box("FloorStack_Open", (0.95, 2.40, 0.72), (0.66, 0.28, 0.24), COL_LONGBOX,
             open_faces={'+Z'})
    make_box("FloorStack_Open_Inner", (0.95, 2.40, 0.66), (0.62, 0.24, 0.02), COL_LONGBOX_IN)
    for ci in range(6):
        cxx = 0.95 - 0.22 + ci * 0.085
        make_box(f"FloorStack_Comic_{ci}", (cxx, 2.40, 0.77),
                 (0.020, 0.24, 0.24), COMIC_TINTS[(ci * 3 + 1) % 8])
    make_box("FloorStack_DividerTab", (0.95 + 0.09, 2.40, 0.80),
             (0.010, 0.25, 0.27), COL_DIVIDER)


# ═════════════════════════════════════════════════════════════════
# CEILING — "lit by a single overhead with a pull chain" (ch3).
# Ceiling rose → cord → bare bulb → pull chain; the .tscn's
# Key_BareBulb light color (0.96, 0.86, 0.46) matches the glass.
# Fluorescents removed (they contradicted the canon single bulb).
# ═════════════════════════════════════════════════════════════════
def build_ceiling_infra():
    bxy = (0.0, ROOM_D / 2.0)
    make_cyl("Bulb_CeilingRose", (bxy[0], bxy[1], CEIL - 0.02), 0.06, 0.04, P.PVC_WHITE)
    make_cyl("Bulb_Cord", (bxy[0], bxy[1], CEIL - 0.40), 0.006, 0.76, P.METAL_BLACK)
    make_cyl("Bulb_Socket", (bxy[0], bxy[1], CEIL - 0.80), 0.022, 0.06, P.METAL_BLACK)
    make_cyl("Bulb_Glass", (bxy[0], bxy[1], CEIL - 0.90), 0.06, 0.14, (0.96, 0.86, 0.46, 1.0))
    # The pull chain, hanging beside the socket (ch3)
    make_cyl("Bulb_PullChain", (bxy[0] + 0.06, bxy[1], CEIL - 0.99), 0.004, 0.34, P.METAL_STEEL)
    make_cyl("Bulb_PullChainBall", (bxy[0] + 0.06, bxy[1], CEIL - 1.17), 0.012, 0.02, COL_BRASS)
    make_smoke_detector("Smoke", (-0.9, 1.4, CEIL))
    make_hvac_vent("HVAC", (-1.0, 4.45, CEIL), width=0.80, depth=0.40)


def main():
    clear_scene()
    build_shell()
    build_south_doorway()
    build_service_door()
    build_desk_zone()
    build_file_cabinet_zone()
    build_zine_archive()
    build_couch_zone()
    build_east_storage()
    build_center_floor()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/cosmic_comics_back_office.glb"))
    print(f"\n[build_cosmic_comics_back_office] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
