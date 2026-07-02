"""Taqueria El Rancho — vol6 ch16 locale (hero pass).

Family-run Gulf Coast taqueria on the small parallel side road behind
the Centro Foods access road. The deliberate OPPOSITE register from
NexCorp: worn, warm, personal. Hugo (23-24, community college by day)
runs the night shift; his mom and dad own the place; his mother is
the cook on most nights.

Canon sources — godot/resources/scenes/vol6/vol6_ch16_el_rancho.json
(node text, cited by JSON line number below):
  · L504  "TAQUERIA EL RANCHO in red paint on a yellow building,
          with the small image of a steer's head ... faded by
          twenty-some Texas summers into the small orange that red
          paint becomes" — yellow walls, red accents, the steer head
          (echoed inside on the west wall).
  · L508  "The drive-thru is at the back. The drive-thru has, taped
          to the speaker box, a hand-lettered sign that reads
          SPEAKER BROKE — ORDER AT WINDOW."
  · L534  "Hugo slides the window open" — sliding service window.
  · L538  Hugo registers Diego "at four-oh-six AM" — wall clock
          frozen at 4:06.
  · L553  Diego's custom burrito — steak, guac, sour cream, cheese,
          WHITE onions not the red, potatoes — the steam-table pans.
  · L599  horchata, large + medium — agua-fresca barrel dispensers.
  · L611-617  "Mexican Coke. The one with the actual sugar, in the
          bottle." / "Yeah, in the back." — bottle chest cooler +
          crate at the back.
  · L622  "Hugo writes everything down on a small slip from a
          yellow pad." — the yellow pad at the window.
  · L637  "Hugo doesn't take tips on the slip ... There's a jar at
          the window." — tip jar on the window shelf.
  · L647  "We're hot on the steak right now" — steak on the
          flat-top; "the flautas need a couple" — the fryer.
  · L846  "brown paper bag with the receipt stapled to the top" /
          "styrofoam cups with sealed lids" — bag stack, stapler,
          white cup stacks + lids.
  · L866  the sauce-packet box at Hugo's elbow — green sauce, red
          sauce, orange El Diablito (in-house, two years), pickled
          jalapeño packets.
  · L938  Hugo's mother's salsa roja "done in-house for fifteen
          years" — the stockpot on the range; the potato cubes.

Shell footprint kept from the original scaffold (7 x 6 x 2.8 — the
.tscn camera + lights are tuned to it). Scaffold audit fixes: the
old Table_Top was a floating cylinder with no base; the south wall
had a door gap but no frame/leaf; there were no window openings at
all. Windows here are REAL openings (frame + mullions, NO glass
slab, dark night boxes behind — 4 AM in mid-August) per the
playbook no-transparency rule.

Text is scene-side Label3D per the playbook; this script only bakes
named vertex-colored panels: MenuBoard_Panel_{0..2}, OrderHere_Sign,
PickUp_Sign, DriveThru_SpeakerBrokeSign, HoursPlaque,
Window_{W,E}_LetterBand, TV_Screen, KidDrawing, FirstDollar_Frame.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import (make_floor, make_wall, make_ceiling,
                              make_crown_molding, make_door_hinges)
from _props.store_fixtures import make_register
from _props.food_service import make_paper_cup_stack
from _props.signage import make_hanging_banner
from _props.decor import (make_wall_clock, make_floor_plant,
                          make_calendar, make_fire_extinguisher)
from _props.safety import (make_smoke_detector, make_hvac_vent,
                           make_fluorescent_tube_fixture,
                           make_ceiling_speaker, make_bug_zapper)
from _props.cleaning import (make_broom_mop, make_wet_floor_cone,
                             make_trash_can)

# ── Shell (kept from the scaffold — camera + lights tuned to it) ──
ROOM_W = 7.0; ROOM_D = 6.0; CEIL = 2.8
PAL_WALL = {"wall": (0.96, 0.84, 0.62, 1.0),        # the yellow building (L504)
            "baseboard": (0.62, 0.42, 0.22, 1.0)}
COL_WALL = PAL_WALL["wall"]

# ── Taqueria palette ─────────────────────────────────────────────
COL_TILE      = (0.62, 0.40, 0.26, 1.0)   # saltillo terracotta
COL_TILE_SEAM = (0.38, 0.24, 0.15, 1.0)
COL_RANCHO_RED= (0.72, 0.20, 0.16, 1.0)   # the red paint (L504)
COL_FADED_RED = (0.76, 0.44, 0.26, 1.0)   # 20-summer faded red = orange (L504)
COL_WOOD      = (0.46, 0.31, 0.19, 1.0)   # worn table/trim wood
COL_WOOD_DARK = (0.30, 0.20, 0.13, 1.0)
COL_LAMINATE  = (0.70, 0.26, 0.20, 1.0)   # red table laminate
COL_STAINLESS = (0.70, 0.71, 0.72, 1.0)   # kitchen line steel
COL_STEEL_DK  = (0.44, 0.45, 0.47, 1.0)
COL_STYRO     = (0.94, 0.94, 0.90, 1.0)   # styrofoam cups (L846)
COL_BAG_KRAFT = (0.72, 0.55, 0.34, 1.0)   # brown paper bags (L846)
COL_YELLOWPAD = (0.94, 0.86, 0.44, 1.0)   # the yellow pad (L622)
COL_JAR_GLASS = (0.80, 0.84, 0.82, 1.0)   # tip jar (L637)
COL_BILLS     = (0.52, 0.60, 0.44, 1.0)
COL_NIGHT     = (0.045, 0.045, 0.07, 1.0) # 4 AM outside the openings
# Sauce colors (L866): green / red / El Diablito orange / jalapeño
COL_SALSA_VERDE  = (0.42, 0.56, 0.26, 1.0)
COL_SALSA_ROJA   = (0.60, 0.18, 0.13, 1.0)
COL_DIABLITO     = (0.85, 0.46, 0.14, 1.0)
COL_JALAPENO     = (0.36, 0.48, 0.26, 1.0)
# Steam-table pans (L553)
COL_GUAC       = (0.46, 0.56, 0.28, 1.0)
COL_SOURCREAM  = (0.94, 0.93, 0.87, 1.0)
COL_CHEESE     = (0.92, 0.76, 0.34, 1.0)
COL_ONION_WHITE= (0.91, 0.89, 0.82, 1.0)
COL_ONION_RED  = (0.56, 0.28, 0.40, 1.0)
COL_POTATO     = (0.88, 0.78, 0.54, 1.0)
COL_STEAK      = (0.42, 0.26, 0.16, 1.0)
COL_FLAUTA     = (0.80, 0.60, 0.32, 1.0)
COL_TORTILLA   = (0.90, 0.84, 0.68, 1.0)
COL_LIME       = (0.55, 0.64, 0.30, 1.0)
COL_COKE_RED   = (0.68, 0.16, 0.14, 1.0)
COL_COKE_GLASS = (0.42, 0.52, 0.44, 1.0)  # green glass bottles
COL_AGUA_HORCH = (0.88, 0.82, 0.70, 1.0)  # horchata (L599)
COL_AGUA_JAMAI = (0.52, 0.16, 0.22, 1.0)  # jamaica
COL_AGUA_TAMAR = (0.55, 0.36, 0.18, 1.0)  # tamarindo
# Papel picado string — muted warm-sunset cycle, not candy-bright
PICADO_TINTS = [
    (0.78, 0.36, 0.28, 1.0),   # muted red
    (0.86, 0.62, 0.28, 1.0),   # marigold
    (0.42, 0.55, 0.48, 1.0),   # teal
    (0.62, 0.40, 0.58, 1.0),   # dusty purple
    (0.90, 0.82, 0.55, 1.0),   # cream gold
]

# Key layout lines (Blender frame — +Y north, +Z up)
S_FACE   = 0.10          # interior face of the south wall
E_FACE   = ROOM_W/2.0 - 0.10   # +3.40 east wall interior face
W_FACE   = -ROOM_W/2.0 + 0.10  # -3.40 west wall interior face
N_FACE   = ROOM_D - 0.10       # +5.90 north wall interior face
COUNTER_Y = 4.15         # service counter centerline
COUNTER_TOP = 0.99
DT_Y = 4.95              # drive-thru window center (east wall, at the back — L508)
DT_Z0, DT_Z1 = 0.95, 2.05


# ═════════════════════════════════════════════════════════════════
# Tiny local helpers (taqueria-specific vocabulary)
# ═════════════════════════════════════════════════════════════════
def _napkin_dispenser(prefix, cx, cy, base_z):
    make_box(f"{prefix}_Body", (cx, cy, base_z + 0.075),
             (0.10, 0.15, 0.15), COL_STEEL_DK)
    make_box(f"{prefix}_Napkin", (cx, cy, base_z + 0.075),
             (0.104, 0.10, 0.08), P.PAPER)


def _squeeze_bottle(prefix, cx, cy, base_z, col):
    make_cyl(f"{prefix}_Body", (cx, cy, base_z + 0.085), 0.032, 0.17, col)
    make_cyl(f"{prefix}_Cap", (cx, cy, base_z + 0.19), 0.014, 0.04,
             (0.88, 0.86, 0.80, 1.0))


def _chair(prefix, cx, cy, back_dx, back_dy):
    """Worn wooden cafe chair. (back_dx, back_dy) is the unit-ish
    offset direction from seat center to the backrest."""
    for li, (sx, sy) in enumerate([(-0.16, -0.16), (+0.16, -0.16),
                                   (-0.16, +0.16), (+0.16, +0.16)]):
        make_cyl(f"{prefix}_Leg_{li}", (cx + sx, cy + sy, 0.225),
                 0.016, 0.45, COL_WOOD_DARK)
    make_box(f"{prefix}_Seat", (cx, cy, 0.46), (0.40, 0.40, 0.035), COL_WOOD)
    make_box(f"{prefix}_Back",
             (cx + back_dx * 0.185, cy + back_dy * 0.185, 0.72),
             (0.40 if back_dy != 0 else 0.05,
              0.40 if back_dx != 0 else 0.05, 0.46), COL_WOOD)


def _pedestal_table(prefix, cx, cy):
    """Round pedestal four-top — cylinder geometry at eye level per
    playbook (the scaffold's floating Table_Top bug, fixed)."""
    make_cyl(f"{prefix}_BaseDisc", (cx, cy, 0.025), 0.30, 0.05,
             COL_STEEL_DK, segments=12)
    make_cyl(f"{prefix}_Column", (cx, cy, 0.38), 0.045, 0.66, COL_STEEL_DK)
    make_cyl(f"{prefix}_Top", (cx, cy, 0.735), 0.46, 0.035,
             COL_LAMINATE, segments=16)
    make_cyl(f"{prefix}_EdgeBand", (cx, cy, 0.718), 0.465, 0.018,
             COL_STEEL_DK, segments=16)
    # table set: napkins + the house squeeze-bottle pair + salt
    _napkin_dispenser(f"{prefix}_Napkins", cx + 0.14, cy + 0.10, 0.755)
    _squeeze_bottle(f"{prefix}_Verde", cx - 0.16, cy + 0.12, 0.755, COL_SALSA_VERDE)
    _squeeze_bottle(f"{prefix}_Roja", cx - 0.09, cy + 0.16, 0.755, COL_SALSA_ROJA)
    make_cyl(f"{prefix}_Salt", (cx - 0.13, cy + 0.02, 0.79), 0.018, 0.07,
             (0.92, 0.92, 0.88, 1.0))


def _agua_barrel(prefix, cx, cy, base_z, liquid_col):
    """Clear agua-fresca barrel dispenser with spigot — the horchata
    lives here (L599). Front face is +X (station on the west wall)."""
    make_cyl(f"{prefix}_Barrel", (cx, cy, base_z + 0.26), 0.155, 0.52,
             (0.86, 0.88, 0.86, 1.0), segments=12)
    make_cyl(f"{prefix}_Liquid", (cx, cy, base_z + 0.22), 0.135, 0.38,
             liquid_col, segments=12)
    make_cyl(f"{prefix}_Lid", (cx, cy, base_z + 0.545), 0.165, 0.05,
             COL_STEEL_DK, segments=12)
    make_cyl(f"{prefix}_Knob", (cx, cy, base_z + 0.59), 0.035, 0.04, COL_STEEL_DK)
    make_cyl(f"{prefix}_Spigot", (cx + 0.17, cy, base_z + 0.07), 0.017, 0.09,
             COL_STEEL_DK, axis='X')
    make_box(f"{prefix}_SpigotTap", (cx + 0.21, cy, base_z + 0.115),
             (0.02, 0.04, 0.05), (0.85, 0.83, 0.78, 1.0))


def _photo_frame(prefix, wall_x, wy, wz, w, h, photo_col):
    """Family photo on the west wall — frame + photo + hanger nail."""
    make_box(f"{prefix}_Frame", (wall_x + 0.015, wy, wz), (0.03, w, h), COL_WOOD_DARK)
    make_box(f"{prefix}_Photo", (wall_x + 0.032, wy, wz),
             (0.004, w - 0.05, h - 0.05), photo_col)


# ═════════════════════════════════════════════════════════════════
# SHELL — saltillo floor, yellow walls with REAL openings (south:
# door + two windows; east: the drive-thru window), ceiling, crown.
# ═════════════════════════════════════════════════════════════════
def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_TILE, "seam": COL_TILE_SEAM})
    # West wall — solid
    make_wall("Wall_W", (-ROOM_W/2.0, ROOM_D/2.0, 0), length=ROOM_D+0.4,
              height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    # East wall — split around the drive-thru window opening
    # (y 4.45..5.45, z 0.95..2.05). Real opening, not a buried pane.
    make_wall("Wall_E_S", (+ROOM_W/2.0, 2.125, 0), length=4.65, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_E_N", (+ROOM_W/2.0, 5.825, 0), length=0.75, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Wall_E_DT_Sill", (+ROOM_W/2.0, DT_Y, DT_Z0/2.0),
             (0.20, 1.00, DT_Z0), COL_WALL)
    make_box("Wall_E_DT_Head", (+ROOM_W/2.0, DT_Y, (DT_Z1+CEIL)/2.0),
             (0.20, 1.00, CEIL-DT_Z1), COL_WALL)
    make_box("Wall_E_DT_Base", (E_FACE - 0.03, DT_Y, 0.08),
             (0.06, 1.00, 0.16), PAL_WALL["baseboard"])
    # North wall — solid (the kitchen line backs onto it)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL,
              axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    # South (storefront) wall — door gap x -1..+1, window openings
    # x -3.05..-1.45 and +1.45..+3.05 at z 0.75..2.20 (real openings).
    for nm, cx, w in [("Wall_S_Pier_WW", -3.375, 0.65),
                      ("Wall_S_Pier_WM", -1.225, 0.45),
                      ("Wall_S_Pier_EM", +1.225, 0.45),
                      ("Wall_S_Pier_EE", +3.375, 0.65)]:
        make_box(nm, (cx, 0.0, CEIL/2.0), (w, 0.20, CEIL), COL_WALL)
    for nm, cx in [("Wall_S_Sill_W", -2.25), ("Wall_S_Sill_E", +2.25)]:
        make_box(nm, (cx, 0.0, 0.375), (1.60, 0.20, 0.75), COL_WALL)
    make_box("Wall_S_Header", (0.0, 0.0, (2.20+CEIL)/2.0),
             (ROOM_W+0.4, 0.20, CEIL-2.20), COL_WALL)
    for nm, cx, w in [("Wall_S_Base_W", -2.35, 2.70), ("Wall_S_Base_E", +2.35, 2.70)]:
        make_box(nm, (cx, 0.13, 0.08), (w, 0.06, 0.16), PAL_WALL["baseboard"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_RANCHO_RED})


# ═════════════════════════════════════════════════════════════════
# STOREFRONT — door (frame + leaf, mullions, no glass), two window
# openings with frames + letter bands, night boxes behind (4 AM),
# entry mat, hours plaque, floor plant, trash can by the door.
# ═════════════════════════════════════════════════════════════════
def _storefront_window(tag, wx):
    make_box(f"Window_{tag}_SillCap", (wx, 0.0, 0.79), (1.76, 0.26, 0.08), COL_WOOD)
    make_box(f"Window_{tag}_Head", (wx, 0.0, 2.16), (1.76, 0.24, 0.08), COL_WOOD)
    for sgn in (-1, +1):
        make_box(f"Window_{tag}_Jamb_{sgn:+d}", (wx + sgn * 0.84, 0.0, 1.475),
                 (0.08, 0.24, 1.29), COL_WOOD)
    # Mullions only — opening stays empty per no-glass rule
    make_box(f"Window_{tag}_MullH", (wx, 0.0, 1.45), (1.60, 0.05, 0.05), COL_WOOD)
    make_box(f"Window_{tag}_MullV", (wx, 0.0, 1.475), (0.05, 0.05, 1.29), COL_WOOD)
    # Hand-painted letter band on the top pane area — "TACOS ·
    # BURRITOS · FLAUTAS" lettering is Label3D scene-side
    make_box(f"Window_{tag}_LetterBand", (wx, S_FACE + 0.005, 1.92),
             (1.40, 0.008, 0.26), COL_RANCHO_RED)
    # 4 AM outside: dark night box fills the view through the opening
    make_box(f"Window_{tag}_Night", (wx, -0.55, 1.475), (1.90, 0.85, 1.60), COL_NIGHT)


def build_storefront():
    _storefront_window('W', -2.25)
    _storefront_window('E', +2.25)
    # Door surround in the 2 m gap
    for sgn in (-1, +1):
        make_box(f"DoorPost_{sgn:+d}", (sgn * 0.96, 0.0, 1.10), (0.08, 0.24, 2.20), COL_WOOD)
    make_box("DoorTransom", (0.0, 0.0, 2.16), (2.00, 0.24, 0.09), COL_WOOD)
    # Door leaf (west half) — stiles + rails + kick plate, opening
    # panes left empty. Worn wood, not storefront aluminum.
    make_box("Door_Stile_W", (-0.88, 0.0, 1.08), (0.07, 0.05, 2.10), COL_WOOD_DARK)
    make_box("Door_Stile_E", (-0.12, 0.0, 1.08), (0.07, 0.05, 2.10), COL_WOOD_DARK)
    make_box("Door_Rail_Top", (-0.50, 0.0, 2.09), (0.83, 0.05, 0.08), COL_WOOD_DARK)
    make_box("Door_Rail_Mid", (-0.50, 0.0, 1.02), (0.83, 0.05, 0.08), COL_WOOD_DARK)
    make_box("Door_Panel_Lower", (-0.50, 0.0, 0.55), (0.79, 0.035, 0.86), COL_WOOD)
    make_box("Door_KickPlate", (-0.50, 0.0, 0.16), (0.83, 0.05, 0.24), COL_STEEL_DK)
    make_cyl("Door_PushBar", (-0.50, 0.07, 1.02), 0.020, 0.62, COL_STEEL_DK, axis='X')
    make_door_hinges("Door_Hinge", edge_x=-0.92, edge_y=0.0,
                     edge_z_centers=[0.35, 1.05, 1.80], axis='X')
    # East sidelite — frame only, opening left empty
    make_box("SideLite_Stile_W", (0.12, 0.0, 1.10), (0.06, 0.05, 2.16), COL_WOOD_DARK)
    make_box("SideLite_Stile_E", (0.88, 0.0, 1.10), (0.06, 0.05, 2.16), COL_WOOD_DARK)
    make_box("SideLite_Sill", (0.50, 0.0, 0.30), (0.80, 0.05, 0.06), COL_WOOD_DARK)
    make_box("SideLite_Mull", (0.50, 0.0, 1.52), (0.80, 0.05, 0.05), COL_WOOD_DARK)
    make_box("Door_Night", (0.0, -0.55, 1.20), (2.30, 0.85, 2.30), COL_NIGHT)
    # Hand-lettered hours plaque on the east door post (Label3D)
    make_box("HoursPlaque", (1.06, S_FACE + 0.005, 1.45), (0.16, 0.010, 0.22), P.PAPER_AGED)
    # ABIERTO/OPEN sign hanging in the door's upper pane on twine
    make_cyl("OpenSign_Cord", (-0.50, 0.045, 1.86), 0.004, 0.30, P.TWINE, axis='Z')
    make_box("OpenSign_Board", (-0.50, 0.045, 1.62), (0.32, 0.018, 0.20), COL_RANCHO_RED)
    make_box("OpenSign_TextBand", (-0.50, 0.058, 1.62), (0.24, 0.006, 0.09), P.PAPER)
    make_box("EntryMat_Under", (0.0, 0.80, 0.004), (1.90, 1.05, 0.006), (0.14, 0.13, 0.13, 1.0))
    make_box("EntryMat", (0.0, 0.80, 0.011), (1.76, 0.92, 0.008), P.RUBBER_MAT)
    make_floor_plant("FloorPlant", (-1.65, 0.50, 0.0))
    make_trash_can("DoorTrash", (1.62, 0.55, 0.0),
                   palette={"body": COL_FADED_RED})
    # Bussing tray stack on the trash can lid
    for ti in range(3):
        make_box(f"TrayStack_{ti}", (1.62, 0.55, 1.10 + ti * 0.035),
                 (0.46, 0.34, 0.03), (0.55, 0.30, 0.22, 1.0))


# ═════════════════════════════════════════════════════════════════
# SERVICE COUNTER — worn formica counter across the room's north
# end, register, second yellow pad, dulces bowl, hanging menu board
# (three red panels, Label3D lettering), ORDER HERE / PICK UP signs,
# heat-lamp pass shelf, bag stack + stapler at the pass end (L846).
# ═════════════════════════════════════════════════════════════════
def build_service_counter():
    cx, cy = -0.40, COUNTER_Y      # counter spans x -2.5..+1.7
    L, D, H = 4.20, 0.75, 0.92
    make_box("Counter_Body", (cx, cy, H/2.0), (L, D, H), (0.78, 0.62, 0.40, 1.0))
    make_box("Counter_Top", (cx, cy, H + 0.035), (L + 0.10, D + 0.12, 0.07), COL_LAMINATE)
    make_box("Counter_Kick", (cx, cy - D/2.0 - 0.01, 0.10), (L, 0.02, 0.20), COL_WOOD_DARK)
    # Bullnose along the customer (south) edge — cyl, not box edge
    seg = L / 7.0
    for s in range(7):
        sx = cx - L/2.0 + (s + 0.5) * seg
        make_cyl(f"Counter_Bullnose_{s}", (sx, cy - D/2.0 - 0.06, H + 0.02),
                 0.028, seg, COL_LAMINATE, axis='X')
    # Register — old cash unit; family place, cash + the tip jar
    # house rule (L637), no corporate card terminal cluster
    make_register("RegisterMachine", (-1.75, cy + 0.05, H + 0.07),
                  palette={"body": (0.58, 0.56, 0.50, 1.0)})
    # Front counter's own yellow pad + pen (Hugo's pad twin, L622)
    make_box("CounterPad", (-1.20, cy - 0.18, H + 0.075), (0.15, 0.21, 0.015), COL_YELLOWPAD)
    make_cyl("CounterPad_Pen", (-1.05, cy - 0.14, H + 0.078), 0.006, 0.13,
             (0.20, 0.24, 0.46, 1.0), axis='Y')
    # Dulces bowl — tamarind candies for the kids (family touch)
    make_cyl("DulcesBowl", (-0.45, cy - 0.20, H + 0.10), 0.11, 0.07,
             (0.85, 0.80, 0.70, 1.0), segments=12)
    for di in range(7):
        ddx = ((di * 3 + 1) % 5 - 2) * 0.032
        ddy = ((di * 5 + 2) % 5 - 2) * 0.028
        make_box(f"Dulce_{di}", (-0.45 + ddx, cy - 0.20 + ddy, H + 0.145),
                 (0.030, 0.022, 0.018), PICADO_TINTS[di % len(PICADO_TINTS)])
    _napkin_dispenser("Counter_Napkins", 0.10, cy - 0.18, H + 0.07)
    make_box("CounterMenu_Stand", (0.55, cy - 0.20, H + 0.16),
             (0.015, 0.20, 0.18), P.PAPER_AGED)
    # Ice bin + scoop behind the counter, west of the register —
    # the horchata pours over ice at 4 AM
    make_box("IceBin", (-2.30, cy + 0.08, H + 0.14), (0.30, 0.24, 0.14), COL_STEEL_DK,
             open_faces={'+Z'})
    make_box("IceBin_Ice", (-2.30, cy + 0.08, H + 0.195), (0.26, 0.20, 0.03),
             (0.88, 0.92, 0.94, 1.0))
    make_cyl("IceScoop", (-2.24, cy + 0.14, H + 0.225), 0.030, 0.12,
             (0.80, 0.20, 0.18, 1.0), axis='Y')
    # Pick-up / pass end (east): heat-lamp bar over the landing zone
    for sgn in (-1, +1):
        make_cyl(f"HeatLamp_Post_{sgn:+d}", (1.35 + sgn * 0.28, cy + 0.12, H + 0.27),
                 0.014, 0.40, COL_STEEL_DK)
    make_box("HeatLamp_Bar", (1.35, cy + 0.12, H + 0.48), (0.72, 0.06, 0.05), COL_STEEL_DK)
    for li in range(2):
        make_cyl(f"HeatLamp_Shade_{li}", (1.15 + li * 0.40, cy + 0.12, H + 0.41),
                 0.075, 0.09, COL_RANCHO_RED)
        make_cyl(f"HeatLamp_Glow_{li}", (1.15 + li * 0.40, cy + 0.12, H + 0.355),
                 0.05, 0.02, (1.0, 0.78, 0.36, 1.0))
    # Brown bag stack + stapler — receipt stapled to the top (L846)
    for bi in range(3):
        make_box(f"BagStack_{bi}", (1.62, cy - 0.10, H + 0.085 + bi * 0.032),
                 (0.26, 0.34 - bi * 0.02, 0.03), COL_BAG_KRAFT)
    make_box("Counter_Stapler", (1.30, cy - 0.22, H + 0.085), (0.06, 0.16, 0.05),
             (0.22, 0.22, 0.24, 1.0))
    # Menu board — three red panels hung over the counter; prices
    # like "horchata, three dollars" (L1373) go scene-side Label3D
    for mi in range(3):
        mx = -1.65 + mi * 1.25
        for cs in (-1, +1):
            make_box(f"MenuBoard_Cable_{mi}_{cs:+d}", (mx + cs * 0.45, 4.02, CEIL - 0.115),
                     (0.01, 0.01, 0.23), P.METAL_BLACK)
        make_box(f"MenuBoard_Panel_{mi}", (mx, 4.02, CEIL - 0.50),
                 (1.12, 0.03, 0.56), COL_RANCHO_RED)
        make_box(f"MenuBoard_Rim_{mi}", (mx, 4.035, CEIL - 0.50),
                 (1.16, 0.015, 0.60), COL_WOOD_DARK)
        for r in range(4):
            make_box(f"MenuBoard_Line_{mi}_{r}", (mx, 4.00, CEIL - 0.31 - r * 0.125),
                     (0.94, 0.006, 0.055), P.PAPER)
    make_hanging_banner("OrderHere_Sign", (-1.75, 3.55, CEIL),
                        width=0.85, height=0.26, bg_color=COL_WOOD_DARK,
                        text_color=P.PAPER)
    make_hanging_banner("PickUp_Sign", (1.35, 3.55, CEIL),
                        width=0.85, height=0.26, bg_color=COL_WOOD_DARK,
                        text_color=P.PAPER)


# ═════════════════════════════════════════════════════════════════
# KITCHEN LINE — open line along the north wall, visible over the
# counter (mom's domain, L938): flat-top with the steak that's
# running hot (L647), fryer with flauta baskets, range with the
# fifteen-year salsa roja stockpot + the potato pan, steam table
# with Diego's burrito pans (L553), stainless hood, ticket rail.
# ═════════════════════════════════════════════════════════════════
def build_kitchen_line():
    ky = 5.52                        # equipment centerline
    # Flat-top grill (west end)
    make_box("Grill_Body", (-2.45, ky, 0.45), (1.10, 0.75, 0.90), COL_STAINLESS)
    make_box("Grill_Top", (-2.45, ky, 0.925), (1.06, 0.68, 0.05), (0.24, 0.23, 0.22, 1.0))
    make_box("Grill_Splash", (-2.45, ky + 0.36, 1.12), (1.10, 0.04, 0.34), COL_STAINLESS)
    for si in range(3):   # "we're hot on the steak right now" (L647)
        make_box(f"Grill_Steak_{si}", (-2.72 + si * 0.27, ky - 0.06, 0.965),
                 (0.20, 0.13, 0.030), COL_STEAK)
    make_box("Grill_Spatula_Blade", (-2.10, ky + 0.14, 0.955), (0.09, 0.11, 0.012), COL_STEEL_DK)
    make_cyl("Grill_Spatula_Handle", (-2.10, ky + 0.28, 0.97), 0.012, 0.18,
             COL_WOOD_DARK, axis='Y')
    make_box("Grill_GreaseCup", (-1.95, ky - 0.30, 0.86), (0.10, 0.10, 0.10), COL_STEEL_DK)
    # Fryer — "the flautas need a couple" (L647); rolled fried
    # cylinders (L924) in the near basket
    make_box("Fryer_Body", (-1.45, ky, 0.45), (0.75, 0.75, 0.90), COL_STAINLESS)
    make_box("Fryer_Oil", (-1.45, ky, 0.895), (0.66, 0.58, 0.02), (0.30, 0.22, 0.10, 1.0))
    make_box("Fryer_Splash", (-1.45, ky + 0.36, 1.12), (0.75, 0.04, 0.34), COL_STAINLESS)
    for bi in range(2):
        bx = -1.62 + bi * 0.34
        make_box(f"Fryer_Basket_{bi}", (bx, ky - 0.05, 0.93),
                 (0.26, 0.34, 0.14), COL_STEEL_DK, open_faces={'+Z'})
        make_cyl(f"Fryer_BasketHandle_{bi}", (bx, ky - 0.32, 1.00),
                 0.011, 0.20, P.METAL_BLACK, axis='Y')
    for fi in range(4):
        make_cyl(f"Fryer_Flauta_{fi}", (-1.62, ky - 0.15 + fi * 0.065, 0.975),
                 0.020, 0.22, COL_FLAUTA, axis='X')
    # Range — salsa roja stockpot, in-house fifteen years (L938),
    # and the small potato pan (L553/938)
    make_box("Range_Body", (-0.60, ky, 0.45), (0.85, 0.75, 0.90), COL_STAINLESS)
    make_box("Range_Top", (-0.60, ky, 0.915), (0.81, 0.68, 0.03), (0.24, 0.23, 0.22, 1.0))
    make_box("Range_Splash", (-0.60, ky + 0.36, 1.12), (0.85, 0.04, 0.34), COL_STAINLESS)
    for gi, (gx, gy) in enumerate([(-0.79, ky - 0.16), (-0.41, ky - 0.16),
                                   (-0.79, ky + 0.18), (-0.41, ky + 0.18)]):
        make_cyl(f"Range_Burner_{gi}", (gx, gy, 0.935), 0.085, 0.015, P.METAL_BLACK)
    make_cyl("SalsaRoja_Pot", (-0.79, ky + 0.18, 1.06), 0.14, 0.24, COL_STEEL_DK, segments=12)
    make_cyl("SalsaRoja_Surface", (-0.79, ky + 0.18, 1.175), 0.125, 0.012, COL_SALSA_ROJA)
    make_cyl("SalsaRoja_Lid", (-0.55, ky + 0.34, 0.945), 0.145, 0.015, COL_STAINLESS)
    for sgn in (-1, +1):
        make_box(f"SalsaRoja_Handle_{sgn:+d}", (-0.79 + sgn * 0.155, ky + 0.18, 1.10),
                 (0.03, 0.06, 0.02), P.METAL_BLACK)
    make_cyl("PotatoPan", (-0.41, ky - 0.16, 0.965), 0.11, 0.05, (0.28, 0.27, 0.26, 1.0), segments=12)
    for pi in range(5):
        pdx = ((pi * 3 + 1) % 4 - 1.5) * 0.038
        pdy = ((pi * 5 + 2) % 4 - 1.5) * 0.034
        make_box(f"PotatoCube_{pi}", (-0.41 + pdx, ky - 0.16 + pdy, 0.995),
                 (0.032, 0.032, 0.026), COL_POTATO)
    make_cyl("PotatoPan_Handle", (-0.41, ky - 0.42, 0.975), 0.011, 0.22,
             P.METAL_BLACK, axis='Y')
    # Steam table (east) — Diego's custom-burrito pans: guac, sour
    # cream, cheese, WHITE onions, the red he skips, potatoes (L553)
    make_box("SteamTable_Body", (0.85, ky, 0.45), (1.85, 0.75, 0.90), COL_STAINLESS)
    make_box("SteamTable_Rim", (0.85, ky, 0.925), (1.85, 0.75, 0.05), COL_STEEL_DK)
    pans = [("Guac", COL_GUAC), ("SourCream", COL_SOURCREAM),
            ("Cheese", COL_CHEESE), ("OnionWhite", COL_ONION_WHITE),
            ("OnionRed", COL_ONION_RED), ("SalsaRojaPan", COL_SALSA_ROJA)]
    for pi, (pnm, pcol) in enumerate(pans):
        px = 0.13 + (pi % 3) * 0.50
        py = ky - 0.17 + (pi // 3) * 0.35
        make_box(f"Pan_{pnm}_Insert", (px, py, 0.905), (0.42, 0.28, 0.10),
                 COL_STEEL_DK, open_faces={'+Z'})
        make_box(f"Pan_{pnm}_Fill", (px, py, 0.935), (0.38, 0.24, 0.02), pcol)
    # Tortilla stack + press at the steam table's east end
    for ti in range(6):
        make_cyl(f"Tortilla_{ti}", (1.62, ky - 0.15, 0.955 + ti * 0.012),
                 0.115, 0.010, COL_TORTILLA, segments=12)
    make_box("TortillaPress_Base", (1.62, ky + 0.18, 0.955), (0.26, 0.26, 0.05),
             (0.35, 0.33, 0.32, 1.0))
    make_box("TortillaPress_Plate", (1.62, ky + 0.24, 1.015), (0.26, 0.14, 0.05),
             (0.35, 0.33, 0.32, 1.0))
    make_cyl("TortillaPress_Arm", (1.62, ky + 0.32, 1.10), 0.012, 0.24,
             P.METAL_BLACK, axis='Z')
    # Hood — stainless canopy over the whole line, filters + lights
    make_box("Hood_Canopy", (-0.75, ky + 0.02, 2.38), (3.80, 0.95, 0.44), COL_STAINLESS)
    make_box("Hood_Skirt", (-0.75, ky - 0.44, 2.28), (3.80, 0.04, 0.24), COL_STEEL_DK)
    for hi in range(4):
        make_box(f"Hood_Filter_{hi}", (-2.10 + hi * 0.90, ky + 0.18, 2.155),
                 (0.80, 0.50, 0.02), COL_STEEL_DK)
    for hl in range(2):
        make_cyl(f"Hood_Light_{hl}", (-1.65 + hl * 1.80, ky - 0.28, 2.145),
                 0.05, 0.02, (1.0, 0.86, 0.52, 1.0))
    # Ticket rail on the hood skirt — the night's slips (L622)
    make_box("TicketRail", (-0.75, ky - 0.465, 2.20), (1.60, 0.015, 0.03), COL_STEEL_DK)
    for ti in range(3):
        make_box(f"Ticket_{ti}", (-1.25 + ti * 0.50, ky - 0.475, 2.10),
                 (0.13, 0.006, 0.17), COL_YELLOWPAD)
    # Back-wall shelf: foil rolls (the burrito wrap, L924) + to-go
    # boxes + the flauta boxes
    make_box("KitchenShelf", (-0.75, N_FACE - 0.14, 1.62), (3.20, 0.28, 0.03), COL_WOOD)
    for sgn in (-1, +1):
        make_box(f"KitchenShelf_Bracket_{sgn:+d}", (-0.75 + sgn * 1.45, N_FACE - 0.06, 1.54),
                 (0.04, 0.14, 0.13), P.METAL_BLACK)
    for fi in range(2):
        make_cyl(f"FoilRoll_{fi}", (-2.00 + fi * 0.35, N_FACE - 0.16, 1.68),
                 0.045, 0.30, COL_STAINLESS, axis='X')
    for bi in range(4):
        make_box(f"FlautaBox_{bi}", (-0.90 + bi * 0.30, N_FACE - 0.15, 1.685),
                 (0.24, 0.20, 0.10), COL_STYRO)
    make_box("ToGoBoxStack", (0.55, N_FACE - 0.15, 1.72), (0.28, 0.24, 0.17), COL_BAG_KRAFT)
    # Mexican Coke — "in the back" (L611-617): red chest cooler +
    # wooden crate of green-glass bottles beside the drive-thru
    make_box("CokeChest_Body", (2.55, 5.55, 0.42), (1.10, 0.62, 0.84), COL_COKE_RED)
    make_box("CokeChest_Band", (2.55, 5.235, 0.55), (1.11, 0.015, 0.16), P.PAPER)
    make_box("CokeChest_LidRail", (2.55, 5.55, 0.86), (1.10, 0.62, 0.04), COL_STEEL_DK)
    make_box("CokeChest_Slider", (2.38, 5.55, 0.895), (0.50, 0.56, 0.03), COL_STEEL_DK)
    make_box("CokeCrate", (2.95, 5.68, 0.955), (0.42, 0.32, 0.13), COL_WOOD_DARK,
             open_faces={'+Z'})
    for bi in range(8):
        bxx = 2.82 + (bi % 4) * 0.088
        byy = 5.62 + (bi // 4) * 0.12
        make_cyl(f"CokeBottle_{bi}", (bxx, byy, 1.010), 0.026, 0.19, COL_COKE_GLASS)
        make_cyl(f"CokeBottle_Neck_{bi}", (bxx, byy, 1.135), 0.012, 0.06, COL_COKE_GLASS)
        make_cyl(f"CokeBottle_Cap_{bi}", (bxx, byy, 1.170), 0.014, 0.012, COL_STEEL_DK)
    # First-dollar frame on the east wall over the coke chest —
    # mom and dad's first ticket (family-run touch)
    make_box("FirstDollar_Frame", (E_FACE - 0.015, 5.70, 1.90), (0.03, 0.20, 0.26), COL_WOOD_DARK)
    make_box("FirstDollar_Bill", (E_FACE - 0.032, 5.70, 1.90), (0.004, 0.14, 0.07), COL_BILLS)
    make_fire_extinguisher("FireExt", (W_FACE + 0.10, 5.55, 0.0))


# ═════════════════════════════════════════════════════════════════
# DRIVE-THRU — the back window on the east wall (L508). Sliding
# sash (frame + mullions, one panel slid open), shelf with the tip
# jar (L637), the yellow pad (L622), the sauce-packet box at Hugo's
# elbow (L866), stapler, Hugo's stool. Outside the opening: night,
# the dead speaker box, and the SPEAKER BROKE sign (L508).
# ═════════════════════════════════════════════════════════════════
def build_drive_thru():
    wx = ROOM_W / 2.0     # wall centerline +3.5
    # Frame + track
    make_box("DT_Frame_Head", (wx, DT_Y, DT_Z1 + 0.04), (0.24, 1.08, 0.08), COL_WOOD)
    make_box("DT_Frame_SillCap", (wx, DT_Y, DT_Z0 - 0.04), (0.28, 1.08, 0.08), COL_WOOD)
    for sgn in (-1, +1):
        make_box(f"DT_Frame_Jamb_{sgn:+d}", (wx, DT_Y + sgn * 0.52, (DT_Z0+DT_Z1)/2.0),
                 (0.24, 0.08, DT_Z1 - DT_Z0), COL_WOOD)
    make_box("DT_Track_Top", (wx - 0.04, DT_Y, DT_Z1 - 0.02), (0.05, 0.98, 0.03), COL_STEEL_DK)
    make_box("DT_Track_Bottom", (wx - 0.04, DT_Y, DT_Z0 + 0.02), (0.05, 0.98, 0.03), COL_STEEL_DK)
    # Sliding sash: south panel closed (frame + mullion, no glass);
    # its twin is slid open behind it — the north half is the OPEN
    # hole Hugo leans through (L534)
    for pnm, px_off, py in [("Closed", 0.0, DT_Y - 0.25), ("Slid", -0.07, DT_Y - 0.25)]:
        make_box(f"DT_Sash_{pnm}_Top", (wx - 0.04 + px_off, py, DT_Z1 - 0.075),
                 (0.04, 0.48, 0.05), COL_STEEL_DK)
        make_box(f"DT_Sash_{pnm}_Bottom", (wx - 0.04 + px_off, py, DT_Z0 + 0.075),
                 (0.04, 0.48, 0.05), COL_STEEL_DK)
        for sgn in (-1, +1):
            make_box(f"DT_Sash_{pnm}_Stile_{sgn:+d}",
                     (wx - 0.04 + px_off, py + sgn * 0.22, (DT_Z0+DT_Z1)/2.0),
                     (0.04, 0.05, DT_Z1 - DT_Z0 - 0.10), COL_STEEL_DK)
        make_box(f"DT_Sash_{pnm}_Mull", (wx - 0.04 + px_off, py, (DT_Z0+DT_Z1)/2.0),
                 (0.04, 0.44, 0.04), COL_STEEL_DK)
    make_box("DT_Sash_Handle", (wx - 0.10, DT_Y - 0.04, 1.50), (0.03, 0.03, 0.22), P.METAL_BLACK)
    # Interior shelf — Hugo's station
    make_box("DT_Shelf", (E_FACE - 0.19, DT_Y, 0.91), (0.42, 1.10, 0.04), COL_WOOD)
    for sgn in (-1, +1):
        make_box(f"DT_Shelf_Bracket_{sgn:+d}", (E_FACE - 0.08, DT_Y + sgn * 0.45, 0.82),
                 (0.16, 0.04, 0.14), P.METAL_BLACK)
    # THE TIP JAR (L637) — glass jar, bills leaning in it
    make_cyl("TipJar", (E_FACE - 0.14, DT_Y - 0.42, 1.02), 0.062, 0.18,
             COL_JAR_GLASS, segments=12)
    make_cyl("TipJar_Rim", (E_FACE - 0.14, DT_Y - 0.42, 1.115), 0.066, 0.012, COL_STEEL_DK)
    for bi in range(3):
        make_box(f"TipJar_Bill_{bi}", (E_FACE - 0.155 + bi * 0.018, DT_Y - 0.44 + bi * 0.014,
                 1.075 + bi * 0.012), (0.012, 0.065, 0.10), COL_BILLS)
    make_box("TipJar_Label", (E_FACE - 0.205, DT_Y - 0.42, 1.02), (0.005, 0.09, 0.07), P.PAPER)
    # The yellow pad + pen (L622)
    make_box("DT_YellowPad", (E_FACE - 0.16, DT_Y - 0.10, 0.938), (0.15, 0.21, 0.015), COL_YELLOWPAD)
    make_box("DT_YellowPad_Slip", (E_FACE - 0.14, DT_Y - 0.02, 0.947), (0.11, 0.13, 0.003), COL_YELLOWPAD)
    make_cyl("DT_Pen", (E_FACE - 0.10, DT_Y - 0.20, 0.942), 0.006, 0.13,
             (0.20, 0.24, 0.46, 1.0), axis='Y')
    # Stapler — the receipt goes to the bag top (L846)
    make_box("DT_Stapler", (E_FACE - 0.13, DT_Y + 0.18, 0.945), (0.055, 0.15, 0.045),
             (0.22, 0.22, 0.24, 1.0))
    # The sauce-packet box at Hugo's elbow (L866) — open carton,
    # packets in green / red / Diablito orange / jalapeño rows
    make_box("SaucePacketBox", (E_FACE - 0.17, DT_Y + 0.35, 0.985),
             (0.30, 0.36, 0.13), COL_BAG_KRAFT, open_faces={'+Z'})
    packet_cols = [COL_SALSA_VERDE, COL_SALSA_ROJA, COL_DIABLITO, COL_JALAPENO]
    for pi in range(12):
        pxx = E_FACE - 0.27 + (pi % 3) * 0.095
        pyy = DT_Y + 0.22 + (pi // 3) * 0.083
        make_box(f"SaucePacket_{pi}", (pxx, pyy, 1.035 + (pi % 2) * 0.012),
                 (0.065, 0.055, 0.012), packet_cols[(pi // 3) % 4])
    # Hugo's stool, tucked south of the window
    make_cyl("HugoStool_Seat", (E_FACE - 0.55, DT_Y - 0.73, 0.62), 0.17, 0.04,
             COL_LAMINATE, segments=12)
    make_cyl("HugoStool_Column", (E_FACE - 0.55, DT_Y - 0.73, 0.31), 0.03, 0.58, COL_STEEL_DK)
    make_cyl("HugoStool_Base", (E_FACE - 0.55, DT_Y - 0.73, 0.02), 0.20, 0.04,
             COL_STEEL_DK, segments=12)
    # Kid's crayon drawing taped beside the window (Hugo's little
    # cousin's) — Label-free, pure family texture
    make_box("KidDrawing", (E_FACE - 0.005, DT_Y - 0.80, 1.55), (0.010, 0.22, 0.28), P.PAPER)
    make_box("KidDrawing_Sun", (E_FACE - 0.012, DT_Y - 0.86, 1.63), (0.010, 0.06, 0.06),
             (0.90, 0.74, 0.28, 1.0))
    make_box("KidDrawing_House", (E_FACE - 0.012, DT_Y - 0.75, 1.48), (0.010, 0.09, 0.08),
             COL_RANCHO_RED)
    # Bug zapper on the north wall by the back window — mid-August
    # Gulf Coast night (helper's long axis runs E-W, so it mounts
    # flat only on the N/S walls)
    make_bug_zapper("DT_BugZapper", (2.60, N_FACE - 0.05, 2.35))
    # ── Outside the opening: 4 AM night recess + the drive-thru
    # lane's speaker post with its dead speaker + the hand-lettered
    # SPEAKER BROKE — ORDER AT WINDOW sign taped to it (L508)
    make_box("DT_NightBox", (wx + 0.75, DT_Y, 1.45), (1.30, 2.60, 2.30), COL_NIGHT)
    make_box("DT_LanePad", (wx + 0.70, DT_Y, 0.02), (1.20, 2.40, 0.04),
             (0.16, 0.15, 0.16, 1.0))
    make_cyl("SpeakerPost", (wx + 0.85, DT_Y - 0.85, 0.62), 0.035, 1.20, COL_STEEL_DK)
    make_box("SpeakerBox", (wx + 0.85, DT_Y - 0.85, 1.36), (0.26, 0.20, 0.34),
             (0.30, 0.29, 0.30, 1.0))
    make_box("SpeakerBox_Grille", (wx + 0.70, DT_Y - 0.85, 1.40), (0.02, 0.14, 0.18),
             P.METAL_BLACK)
    make_box("DriveThru_SpeakerBrokeSign", (wx + 0.685, DT_Y - 0.85, 1.28),
             (0.010, 0.17, 0.12), P.PAPER)
    make_box("DT_SignTape_T", (wx + 0.680, DT_Y - 0.85, 1.335), (0.008, 0.06, 0.02),
             (0.86, 0.84, 0.78, 1.0))


# ═════════════════════════════════════════════════════════════════
# DRINK STATION — west wall self-serve: three agua-fresca barrels
# (the horchata, L599), styrofoam cup stacks + sealed lids (L846),
# straw box, ice scoop bin.
# ═════════════════════════════════════════════════════════════════
def build_drink_station():
    sx = W_FACE + 0.30            # cabinet against the west wall
    make_box("Drink_Cabinet", (sx, 2.60, 0.44), (0.58, 1.85, 0.88),
             (0.78, 0.62, 0.40, 1.0))
    make_box("Drink_CabinetTop", (sx, 2.60, 0.915), (0.64, 1.95, 0.07), COL_LAMINATE)
    make_box("Drink_Kick", (sx + 0.30, 2.60, 0.10), (0.02, 1.85, 0.20), COL_WOOD_DARK)
    aguas = [("Horchata", COL_AGUA_HORCH), ("Jamaica", COL_AGUA_JAMAI),
             ("Tamarindo", COL_AGUA_TAMAR)]
    for ai, (anm, acol) in enumerate(aguas):
        _agua_barrel(f"Agua_{anm}", sx - 0.02, 2.25 + ai * 0.53, 0.95, acol)
        make_box(f"Agua_{anm}_Label", (sx + 0.14, 2.25 + ai * 0.53, 1.02),
                 (0.005, 0.20, 0.08), P.PAPER)
    # Styrofoam cups — sealed-lid service (L846)
    make_paper_cup_stack("CupStack_Med", (sx + 0.05, 1.90, 0.95),
                         palette={"col": COL_STYRO}, count=16)
    make_paper_cup_stack("CupStack_Lrg", (sx + 0.16, 1.99, 0.95),
                         palette={"col": COL_STYRO}, count=14)
    make_cyl("LidStack", (sx + 0.05, 1.76, 1.01), 0.052, 0.12, COL_STYRO, segments=12)
    make_box("StrawBox", (sx + 0.20, 1.76, 0.99), (0.16, 0.11, 0.10), COL_RANCHO_RED,
             open_faces={'+Z'})
    for si in range(5):
        make_cyl(f"Straw_{si}", (sx + 0.16 + si * 0.022, 1.76, 1.06), 0.004, 0.14,
                 P.PAPER, axis='Z')
    # Drips happen — wet-floor cone lives by the station at 4 AM
    # (x kept west of the counter's west end at x -2.50)
    make_wet_floor_cone("WetFloorCone", (sx + 0.25, 3.85, 0.0))


# ═════════════════════════════════════════════════════════════════
# DINING — two round pedestal four-tops mid-room, the long family
# table on the west wall, worn wooden chairs, high-chair stack in
# the SW corner. Every table carries napkins + the house bottles.
# ═════════════════════════════════════════════════════════════════
def build_dining():
    _pedestal_table("TableA", -1.55, 2.05)
    for ci, (ccx, ccy, bdx, bdy) in enumerate([(-1.55, 1.40, 0, -1), (-2.20, 2.05, -1, 0),
                                               (-1.55, 2.70, 0, +1)]):
        _chair(f"TableA_Chair_{ci}", ccx, ccy, bdx, bdy)
    _pedestal_table("TableB", 0.85, 2.10)
    for ci, (ccx, ccy, bdx, bdy) in enumerate([(0.85, 1.45, 0, -1), (1.50, 2.10, +1, 0),
                                               (0.85, 2.75, 0, +1), (0.20, 2.10, -1, 0)]):
        _chair(f"TableB_Chair_{ci}", ccx, ccy, bdx, bdy)
    # Family table — rectangular, against the west wall under the
    # steer head; where the family eats at close
    ftx, fty = -2.72, 1.15
    make_box("FamilyTable_Top", (ftx, fty, 0.735), (1.20, 0.75, 0.045), COL_WOOD)
    make_box("FamilyTable_Apron", (ftx, fty, 0.66), (1.05, 0.62, 0.09), COL_WOOD_DARK)
    for li, (lx, ly) in enumerate([(-0.52, -0.30), (+0.52, -0.30),
                                   (-0.52, +0.30), (+0.52, +0.30)]):
        make_cyl(f"FamilyTable_Leg_{li}", (ftx + lx, fty + ly, 0.355),
                 0.028, 0.71, COL_WOOD_DARK)
    _napkin_dispenser("FamilyTable_Napkins", ftx + 0.35, fty + 0.15, 0.758)
    _squeeze_bottle("FamilyTable_Verde", ftx - 0.35, fty + 0.18, 0.758, COL_SALSA_VERDE)
    _squeeze_bottle("FamilyTable_Roja", ftx - 0.26, fty + 0.22, 0.758, COL_SALSA_ROJA)
    for ci, (ccx, ccy, bdx, bdy) in enumerate([(-2.72, 0.62, 0, -1), (-2.72, 1.70, 0, +1),
                                               (-2.10, 1.15, +1, 0)]):
        _chair(f"FamilyTable_Chair_{ci}", ccx, ccy, bdx, bdy)
    # High chairs, stacked two deep in the SW corner — family place
    for hi in range(2):
        hz = hi * 0.28
        for li, (lx, ly) in enumerate([(-0.14, -0.14), (+0.14, -0.14),
                                       (-0.14, +0.14), (+0.14, +0.14)]):
            make_cyl(f"HighChair_{hi}_Leg_{li}", (-3.12 + lx, 0.52 + ly, hz + 0.34),
                     0.015, 0.68, COL_WOOD)
        make_box(f"HighChair_{hi}_Seat", (-3.12, 0.52, hz + 0.70), (0.30, 0.30, 0.03), COL_WOOD)
        make_box(f"HighChair_{hi}_Tray", (-3.12, 0.38, hz + 0.86), (0.32, 0.10, 0.02), COL_WOOD)
        make_box(f"HighChair_{hi}_Back", (-3.12, 0.66, hz + 0.86), (0.30, 0.03, 0.30), COL_WOOD)


# ═════════════════════════════════════════════════════════════════
# SALSA BAR — small stand on the east wall: the house squeeze
# bottles (verde / roja / El Diablito, L866), pickled-jalapeño
# crock, lime bowl, ramekin stacks, napkins.
# ═════════════════════════════════════════════════════════════════
def build_salsa_bar():
    bx = E_FACE - 0.30
    make_box("SalsaBar_Body", (bx, 2.30, 0.44), (0.55, 1.30, 0.88), (0.78, 0.62, 0.40, 1.0))
    make_box("SalsaBar_Top", (bx, 2.30, 0.915), (0.61, 1.40, 0.07), COL_LAMINATE)
    make_box("SalsaBar_Rail", (bx - 0.33, 2.30, 0.90), (0.03, 1.36, 0.03), COL_STEEL_DK)
    trio = [("Verde", COL_SALSA_VERDE), ("Roja", COL_SALSA_ROJA),
            ("Diablito", COL_DIABLITO)]
    for ti, (tnm, tcol) in enumerate(trio):
        for k in range(2):
            _squeeze_bottle(f"SalsaBar_{tnm}_{k}", bx - 0.10 + k * 0.13,
                            1.85 + ti * 0.28, 0.95, tcol)
    make_cyl("JalapenoCrock", (bx - 0.02, 2.72, 1.02), 0.090, 0.14,
             (0.85, 0.82, 0.74, 1.0), segments=12)
    make_cyl("JalapenoCrock_Fill", (bx - 0.02, 2.72, 1.095), 0.078, 0.012, COL_JALAPENO)
    make_cyl("LimeBowl", (bx + 0.14, 2.86, 1.00), 0.085, 0.09,
             (0.85, 0.82, 0.74, 1.0), segments=12)
    for li in range(4):
        ldx = ((li * 3 + 1) % 3 - 1) * 0.040
        ldy = ((li * 5 + 2) % 3 - 1) * 0.036
        make_cyl(f"Lime_{li}", (bx + 0.14 + ldx, 2.86 + ldy, 1.055), 0.025, 0.038, COL_LIME)
    for ri in range(2):
        make_cyl(f"RamekinStack_{ri}", (bx - 0.16, 2.90 + ri * 0.11, 0.99),
                 0.038, 0.10, COL_STYRO, segments=12)
    _napkin_dispenser("SalsaBar_Napkins", bx + 0.12, 1.78, 0.95)


# ═════════════════════════════════════════════════════════════════
# DECOR — the steer head (faded red = orange, L504) big on the west
# wall, family photo wall, calendar, clock frozen at 4:06 (L538),
# CRT TV in the SE corner, papel picado strings.
# ═════════════════════════════════════════════════════════════════
def build_decor():
    # The steer head — same image as the building's exterior sign,
    # repainted small inside years ago; blocky-iconic like the sign
    sx = W_FACE
    make_box("SteerBoard", (sx + 0.02, 1.55, 1.90), (0.03, 1.30, 0.95),
             (0.90, 0.80, 0.56, 1.0))
    make_box("SteerBoard_Rim", (sx + 0.010, 1.55, 1.90), (0.02, 1.36, 1.01), COL_WOOD_DARK)
    make_box("Steer_Head", (sx + 0.040, 1.55, 1.86), (0.012, 0.44, 0.50), COL_FADED_RED)
    make_box("Steer_Muzzle", (sx + 0.048, 1.55, 1.66), (0.012, 0.30, 0.18),
             (0.86, 0.62, 0.42, 1.0))
    for sgn in (-1, +1):
        make_cyl(f"Steer_Horn_{sgn:+d}", (sx + 0.045, 1.55 + sgn * 0.42, 2.13),
                 0.035, 0.40, COL_FADED_RED, axis='Y')
        make_cyl(f"Steer_HornTip_{sgn:+d}", (sx + 0.045, 1.55 + sgn * 0.64, 2.17),
                 0.020, 0.10, (0.88, 0.82, 0.70, 1.0), axis='Y')
        make_box(f"Steer_Ear_{sgn:+d}", (sx + 0.042, 1.55 + sgn * 0.28, 1.98),
                 (0.010, 0.12, 0.10), COL_FADED_RED)
        make_box(f"Steer_Eye_{sgn:+d}", (sx + 0.050, 1.55 + sgn * 0.11, 1.94),
                 (0.008, 0.05, 0.05), COL_WOOD_DARK)
    make_box("Steer_NameBand", (sx + 0.040, 1.55, 1.50), (0.012, 1.10, 0.14), COL_RANCHO_RED)
    # Family photo wall, south of the steer head
    photos = [(0.55, 2.10, 0.24, 0.30, (0.60, 0.55, 0.46, 1.0)),
              (0.90, 2.05, 0.20, 0.26, (0.44, 0.42, 0.40, 1.0)),
              (0.72, 1.72, 0.26, 0.20, (0.66, 0.58, 0.44, 1.0)),
              (0.42, 1.68, 0.18, 0.24, (0.52, 0.48, 0.50, 1.0))]
    for fi, (fy, fz, w, h, pc) in enumerate(photos):
        _photo_frame(f"FamilyPhoto_{fi}", sx, fy, fz, w, h, pc)
    # Grocery calendar on the west wall over the drink station; the
    # clock frozen at 4:06 AM (L538) goes on the NORTH wall — the
    # helper's face details point -Y, so it only mounts north
    make_calendar("Calendar", (sx + 0.015, 4.35, 1.75))
    make_wall_clock("Clock", (-3.00, N_FACE - 0.03, 2.40), frozen_hour=4, frozen_min=6)
    # CRT TV on a wall bracket, SE corner over the salsa bar —
    # late-night futbol replays with the sound off
    make_box("TV_Bracket", (E_FACE, 0.85, 2.02), (0.10, 0.12, 0.30), P.METAL_BLACK)
    make_box("TV_Arm", (E_FACE - 0.14, 0.85, 2.10), (0.24, 0.06, 0.06), P.METAL_BLACK)
    make_box("TV_Body", (E_FACE - 0.42, 0.85, 2.10), (0.36, 0.56, 0.44),
             (0.26, 0.25, 0.26, 1.0))
    make_box("TV_Screen", (E_FACE - 0.605, 0.85, 2.12), (0.010, 0.46, 0.32),
             (0.30, 0.42, 0.38, 1.0))
    make_box("TV_ControlStrip", (E_FACE - 0.605, 0.85, 1.925), (0.008, 0.40, 0.04),
             P.METAL_BLACK)
    # Papel picado — two strings across the dining ceiling, muted
    # warm-sunset tints, deterministic cycle
    for si, py in enumerate((1.45, 2.75)):
        make_cyl(f"Picado_Wire_{si}", (0.0, py, 2.62), 0.005, 6.7,
                 P.METAL_BLACK, axis='X')
        for k in range(13):
            kx = -2.85 + k * 0.475
            col = PICADO_TINTS[(k + si * 2) % len(PICADO_TINTS)]
            make_box(f"Picado_Flag_{si}_{k}", (kx, py, 2.52),
                     (0.24, 0.005, 0.17), col)
            make_box(f"Picado_Cut_{si}_{k}", (kx, py + 0.004, 2.52),
                     (0.10, 0.004, 0.07), COL_WALL)


# ═════════════════════════════════════════════════════════════════
# CEILING INFRA — fluorescents, the dining ceiling fan (cylinders,
# not boxes, per playbook), smoke detector, HVAC, radio speaker.
# No security cameras: this is the opposite register from NexCorp.
# ═════════════════════════════════════════════════════════════════
def build_ceiling_infra():
    for j, (fx, fy) in enumerate([(-1.7, 2.2), (1.7, 2.2), (-0.4, 4.25), (-0.6, 5.55)]):
        make_fluorescent_tube_fixture(f"Fluor_{j}", (fx, fy, CEIL), length=1.30, width=0.32)
    # Ceiling fan over the dining floor
    fanx, fany = -0.35, 2.05
    make_cyl("Fan_Downrod", (fanx, fany, CEIL - 0.12), 0.018, 0.24, COL_STEEL_DK)
    make_cyl("Fan_Motor", (fanx, fany, CEIL - 0.28), 0.09, 0.10, COL_WOOD_DARK, segments=12)
    for bi, (bdx, bdy, bw, bd) in enumerate([(+0.32, 0, 0.52, 0.14), (-0.32, 0, 0.52, 0.14),
                                             (0, +0.32, 0.14, 0.52), (0, -0.32, 0.14, 0.52)]):
        make_box(f"Fan_Blade_{bi}", (fanx + bdx, fany + bdy, CEIL - 0.315),
                 (bw, bd, 0.015), COL_WOOD)
    make_cyl("Fan_Globe", (fanx, fany, CEIL - 0.40), 0.055, 0.10,
             (1.0, 0.90, 0.66, 1.0), segments=12)
    make_smoke_detector("Smoke", (1.6, 4.6, CEIL))
    make_hvac_vent("HVAC", (-2.4, 4.6, CEIL), width=0.80, depth=0.40)
    make_ceiling_speaker("RadioSpeaker", (2.2, 3.2, CEIL))
    # Mop + broom in the NW corner — mom keeps the floor clean
    # (mop hangs 0.16 west of the anchor; keep it proud of the wall)
    make_broom_mop("BroomMop", (-3.18, 5.72, 0.0))


def main():
    clear_scene()
    build_shell()
    build_storefront()
    build_service_counter()
    build_kitchen_line()
    build_drive_thru()
    build_drink_station()
    build_dining()
    build_salsa_bar()
    build_decor()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/el_rancho_taqueria.glb"))
    print(f"\n[build_el_rancho_taqueria] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
