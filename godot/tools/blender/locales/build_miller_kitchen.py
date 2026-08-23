"""Miller (Sam's) Kitchen — vol6 Planned Community — vol6 placement script."""
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

ROOM_W = 7.0; ROOM_D = 6.0; CEIL = 2.6
PAL_WALL = {"wall": (0.92, 0.86, 0.74, 1.0), "baseboard": (0.42, 0.32, 0.22, 1.0)}
COL_FLOOR = (0.74, 0.58, 0.38, 1.0); COL_SEAM = (0.42, 0.30, 0.18, 1.0); COL_WOOD = (0.46, 0.34, 0.22, 1.0)
COL_ACCENT = (0.62, 0.42, 0.22, 1.0)

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

def build_counter():
    # make_counter's `depth` is the X extent, `length` the Y —
    # so length>depth built this counter ROTATED 90 DEGREES:
    # a narrow face against the wall and the run jutting into
    # the room. Swapped 2026-08-12 (same bug as the New
    # Orleans bar and the pit stop's lunch counter).
    top_z = make_counter("Counter", (-ROOM_W/4.0, ROOM_D-1.0, 0.0), length=0.70, depth=2.40, height=0.92,
                         palette={"formica": (0.78, 0.66, 0.42, 1.0), "top": (0.32, 0.22, 0.14, 1.0), "kick": (0.32, 0.22, 0.14, 1.0)})
    make_counter_bullnose("Counter", (-ROOM_W/4.0, ROOM_D-1.0 - 0.35, top_z), length=2.40, axis='X')
    # Sink
    make_box("Sink_Bowl", (-ROOM_W/4.0, ROOM_D-1.0, 0.86), (0.50, 0.40, 0.12), (0.86, 0.86, 0.84, 1.0))
    make_cyl("Sink_Faucet", (-ROOM_W/4.0, ROOM_D-1.10, top_z+0.04), 0.015, 0.30, P.METAL_STEEL)
    # Stove, with the cast-iron roasting pan on it ("roast something
    # — tonight, a chicken — in the cast-iron")
    make_chamfer_box("Stove_Body", (ROOM_W/4.0, ROOM_D-1.0, 0.45), (0.70, 0.70, 0.92), (0.86, 0.84, 0.80, 1.0))
    make_box("Stove_Top", (ROOM_W/4.0, ROOM_D-1.0, 0.92), (0.70, 0.70, 0.04), P.METAL_BLACK)
    make_box("CastIron_Pan", (ROOM_W/4.0, ROOM_D-1.0, 0.99), (0.42, 0.30, 0.10), (0.16, 0.16, 0.17, 1.0))
    # Dishwasher under-counter beside the sink (three scenes end on it)
    make_chamfer_box("Dishwasher_Face", (-ROOM_W/4.0+0.90, ROOM_D-0.68, 0.44), (0.60, 0.04, 0.82), (0.80, 0.78, 0.74, 1.0))
    make_box("Dishwasher_Handle", (-ROOM_W/4.0+0.90, ROOM_D-0.70, 0.80), (0.44, 0.03, 0.04), P.METAL_STEEL)
    # Microwave on the counter
    make_chamfer_box("Microwave", (-ROOM_W/4.0-0.85, ROOM_D-1.0, 1.10), (0.48, 0.36, 0.28), (0.30, 0.30, 0.32, 1.0))
    make_chamfer_box("Microwave_Door", (-ROOM_W/4.0-0.85, ROOM_D-1.19, 1.10), (0.36, 0.02, 0.20), (0.14, 0.14, 0.16, 1.0))
    # Upper cabinets + the under-cabinet light over the sink ("She
    # does not turn on the overhead. She turns on, instead, the
    # small under-cabinet light over the sink")
    make_chamfer_box("Upper_Cabinets", (-ROOM_W/4.0, ROOM_D-0.55, 1.95), (2.40, 0.34, 0.75), (0.72, 0.60, 0.40, 1.0))
    for di, dx in enumerate((-0.85, -0.28, 0.28, 0.85)):
        make_box(f"Upper_Cab_Door_{di}", (-ROOM_W/4.0+dx, ROOM_D-0.72, 1.95), (0.52, 0.02, 0.68), (0.78, 0.66, 0.42, 1.0))
    make_box("UnderCab_Light", (-ROOM_W/4.0, ROOM_D-0.74, 1.56), (1.10, 0.05, 0.04), (0.98, 0.92, 0.74, 1.0))
    # The pantry — tall door on the W wall
    make_box("Pantry_Door", (-ROOM_W/2.0+0.06, 4.20, 1.05), (0.05, 0.80, 2.10), (0.78, 0.66, 0.42, 1.0))
    make_cyl("Pantry_Knob", (-ROOM_W/2.0+0.12, 3.90, 1.02), 0.025, 0.03, (0.66, 0.52, 0.24, 1.0), axis='X', segments=8)
    # The kitchen landline ("The landline never rings")
    make_box("Landline_Base", (-ROOM_W/2.0+0.07, 1.20, 1.40), (0.06, 0.12, 0.24), (0.86, 0.84, 0.78, 1.0))
    make_box("Landline_Handset", (-ROOM_W/2.0+0.10, 1.20, 1.52), (0.05, 0.08, 0.22), (0.80, 0.78, 0.72, 1.0))
    make_box("Landline_Cord", (-ROOM_W/2.0+0.07, 1.28, 1.22), (0.02, 0.02, 0.20), (0.44, 0.42, 0.40, 1.0))

def build_table():
    """RECTANGULAR table — the seating-position motif can't be
    staged on a round one: "Her old chair had been at the long side
    of the table, with Mike across from her and Sammy at the head.
    Since June she has been sitting in Mike's chair, which is on the
    short side near the window." Short side toward the E window."""
    tx, ty = 0.5, ROOM_D/2.0
    make_chamfer_box("Table_Top", (tx, ty, 0.74), (1.60, 0.95, 0.05), COL_WOOD)
    for li, (lx, ly) in enumerate([(-0.70, -0.38), (0.70, -0.38), (-0.70, 0.38), (0.70, 0.38)]):
        make_box(f"Table_Leg_{li}", (tx+lx, ty+ly, 0.36), (0.06, 0.06, 0.72), COL_WOOD)
    # Sammy's chair — the HEAD (west end)
    # Bianca's old chair — LONG side (south)
    # Mike's chair — SHORT side near the window (east end) — where
    # Bianca sits since June
    chairs = [("Chair_Head_Sammy", tx-1.15, ty, -0.18, 0.0),
              ("Chair_Long_Bianca", tx, ty-0.95, 0.0, -0.18),
              ("Chair_Short_Mike", tx+1.15, ty, 0.18, 0.0),
              ("Chair_Long_Guest", tx, ty+0.95, 0.0, 0.18)]
    for nm, cx, cy, bdx, bdy in chairs:
        make_box(f"{nm}_Seat", (cx, cy, 0.44), (0.42, 0.42, 0.04), COL_WOOD)
        make_box(f"{nm}_Back", (cx+bdx, cy+bdy, 0.72),
                 (0.05 if bdx else 0.42, 0.42 if bdx else 0.05, 0.56), COL_WOOD)
        for li, (lx, ly) in enumerate([(-0.17, -0.17), (0.17, -0.17), (-0.17, 0.17), (0.17, 0.17)]):
            make_box(f"{nm}_Leg_{li}", (cx+lx, cy+ly, 0.22), (0.05, 0.05, 0.42), COL_WOOD)
    # Fruit bowl centrepiece — shallow bowl + a few rounds of fruit
    make_cyl("Fruitbowl", (tx, ty, 0.81), 0.18, 0.08, (0.72, 0.66, 0.52, 1.0), segments=14)
    for fi, (fx2, fy2, fc) in enumerate([(-0.06, 0.0, (0.86, 0.62, 0.22, 1.0)),
                                         (0.06, 0.05, (0.72, 0.24, 0.20, 1.0)),
                                         (0.0, -0.07, (0.56, 0.62, 0.28, 1.0))]):
        make_cyl(f"Fruit_{fi}", (tx+fx2, ty+fy2, 0.86), 0.05, 0.09, fc, segments=8)

def build_fridge():
    fx, fy = +ROOM_W/2.0 - 0.50, ROOM_D - 1.0
    make_chamfer_box("Fridge_Body", (fx, fy, 1.00), (0.70, 0.70, 2.00), (0.86, 0.84, 0.80, 1.0))
    make_chamfer_box("Fridge_DoorTop", (fx-0.34, fy, 1.50), (0.04, 0.66, 0.80), (0.86, 0.84, 0.80, 1.0))
    make_chamfer_box("Fridge_DoorBot", (fx-0.34, fy, 0.40), (0.04, 0.66, 1.00), (0.86, 0.84, 0.80, 1.0))
    make_box("Fridge_Handle", (fx-0.38, fy-0.20, 1.30), (0.04, 0.04, 0.50), P.METAL_STEEL)
    for mi in range(6):
        make_box(f"Magnet_{mi}", (fx-0.36, fy-0.20+mi*0.10, 1.60), (0.005, 0.06, 0.08), P.SNACK_TINTS[mi%len(P.SNACK_TINTS)])

def build_clock():
    make_wall_clock("Clock", (0.0, ROOM_D-0.05, CEIL-0.50), frozen_hour=8, frozen_min=15)

def build_window():
    """The E window is the FRONT elevation (Don Geller's porch light
    at 5:02 across the cul-de-sac) — Mike's chair sits beside it.
    Sheer curtain per vol6_ch5 ("watching him through the sheer
    curtain")."""
    make_box("Window_E_Frame", (ROOM_W/2.0-0.04, ROOM_D/2.0+0.5, 1.55), (0.04, 1.60, 1.20), P.METAL_STEEL)
    make_box("Window_E_Glass", (ROOM_W/2.0-0.06, ROOM_D/2.0+0.5, 1.55), (0.005, 1.50, 1.10), (0.78, 0.84, 0.86, 0.55))
    make_box("Window_E_Sheer", (ROOM_W/2.0-0.10, ROOM_D/2.0+0.5, 1.55), (0.01, 1.44, 1.06), (0.94, 0.92, 0.88, 0.35))
    # Back door on the E wall, south end (Anita's door — "comes in
    # through the back door because she has walked over")
    make_box("Back_Door", (ROOM_W/2.0-0.05, 1.20, 1.05), (0.05, 0.90, 2.10), (0.70, 0.58, 0.40, 1.0))
    make_cyl("Back_Door_Knob", (ROOM_W/2.0-0.12, 0.85, 1.02), 0.03, 0.04, (0.66, 0.52, 0.24, 1.0), axis='X', segments=8)
    # Small flat-screen above the breakfast nook corner, volume low
    make_chamfer_box("Nook_TV", (2.60, ROOM_D-0.10, 1.85), (0.68, 0.05, 0.40), (0.10, 0.10, 0.12, 1.0))
    make_box("Nook_TV_Screen", (2.60, ROOM_D-0.135, 1.85), (0.60, 0.01, 0.34), (0.30, 0.36, 0.42, 1.0))

def build_ceiling_infra():
    # "She does not turn on the overhead" — but it exists: a single
    # nook pendant + two recessed cans, not shop fluorescents.
    make_cyl("Nook_Pendant_Cord", (2.0, ROOM_D-1.0, CEIL-0.18), 0.008, 0.36, P.METAL_BLACK)
    make_cyl("Nook_Pendant_Shade", (2.0, ROOM_D-1.0, CEIL-0.44), 0.16, 0.16, (0.62, 0.50, 0.34, 1.0), segments=12)
    for ci, (cx, cy) in enumerate(((-1.5, 2.0), (1.0, 2.0))):
        make_cyl(f"Recessed_Can_{ci}", (cx, cy, CEIL-0.02), 0.10, 0.03, (0.92, 0.90, 0.84, 1.0), segments=10)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))
    make_hvac_vent("HVAC", (-ROOM_W/4.0, ROOM_D-0.5, CEIL), width=0.80, depth=0.40)

def build_dressing():
    """Counter + wall dressing: a drip coffee maker, a dish rack, a
    paper-towel stand, and a wall calendar — the small stuff that
    reads as a family's working kitchen."""
    cw_x = -ROOM_W/4.0; cw_y = ROOM_D-1.0
    # Drip coffee maker at the left end of the west counter
    make_coffee_pots("Coffee", (cw_x-1.0, cw_y, 0.94), pots=1)
    # Dish rack (frame + upright tines) at the right end
    make_box("DishRack_Base", (cw_x+0.9, cw_y, 0.95), (0.34, 0.30, 0.03), P.METAL_STEEL)
    for ti in range(6):
        make_box(f"DishRack_Tine_{ti}", (cw_x+0.72+ti*0.06, cw_y, 1.06), (0.01, 0.24, 0.18), P.METAL_STEEL)
    # Paper-towel stand
    make_cyl("PaperTowel_Rod", (cw_x+0.4, cw_y+0.18, 1.06), 0.012, 0.30, P.METAL_STEEL)
    make_cyl("PaperTowel_Roll", (cw_x+0.4, cw_y+0.18, 1.05), 0.06, 0.24, (0.96, 0.94, 0.90, 1.0), segments=12)
    # Wall calendar on the west wall
    make_calendar("Calendar", (-ROOM_W/2.0+0.05, 2.0, 1.6))

def build_phone_and_toast_2026_08():
    """THE LANDLINE AND THE FRENCH TOAST (--props hunt, 2026-08).

    [shot:insert phone] fires 5x against this kitchen and there was
    no phone: "At seven oh-three the phone in the kitchen rings. It
    is the landline. The landline never rings." — a wall-mount
    landline Sam's father kept active since 2014. And [shot:insert
    french_toast] (vol6 ch11): "She slices the challah, two slices
    thick, the way Mike had always cut his French toast."
    """
    # ── The landline, wall-mounted by the doorway end of the north
    # wall — where a kitchen phone lives, cord long enough to reach
    # the table, because those cords always were.
    px, pz = -2.85, 1.42
    beige = (0.82, 0.78, 0.68, 1.0)
    beige_dk = (0.68, 0.63, 0.53, 1.0)
    make_box("Phone_Wall_Base", (px, ROOM_D - 0.10, pz), (0.095, 0.055, 0.22), beige)
    make_box("Phone_Wall_Handset", (px, ROOM_D - 0.145, pz + 0.02), (0.062, 0.045, 0.19), beige_dk)
    make_box("Phone_Wall_Cradle", (px, ROOM_D - 0.125, pz + 0.115), (0.075, 0.03, 0.02), beige_dk)
    make_box("Phone_Wall_Dial", (px, ROOM_D - 0.132, pz - 0.055), (0.05, 0.006, 0.06), (0.30, 0.28, 0.26, 1.0))
    # The coiled cord, sagging to its low point and back up — three
    # segments stand in for the coil.
    for ci, (dx, dz) in enumerate(((0.05, -0.16), (0.11, -0.26), (0.16, -0.18))):
        make_cyl("Phone_Wall_Cord_%d" % ci, (px + dx, ROOM_D - 0.13, pz + dz),
                 0.011, 0.14, beige_dk, segments=6)
    # Eileen's cell, flat on the counter by the bullnose edge.
    make_box("Phone_Cell", (-2.20, ROOM_D - 1.28, 0.955), (0.075, 0.15, 0.012),
             (0.12, 0.12, 0.14, 1.0))

    # ── The french toast, mid-making: skillet with two thick slices,
    # the challah with its cut end showing, the bowl of whisked egg,
    # the cinnamon. It is being MADE, not plated — that is the shot.
    sx, sy = ROOM_W/4.0, ROOM_D - 1.0
    bread = (0.83, 0.68, 0.44, 1.0)
    crust = (0.62, 0.44, 0.24, 1.0)
    make_cyl("FrenchToast_Skillet", (sx - 0.16, sy + 0.10, 0.965), 0.14, 0.035,
             (0.16, 0.15, 0.14, 1.0), segments=14)
    make_box("FrenchToast_Skillet_Handle", (sx - 0.36, sy + 0.10, 0.975),
             (0.16, 0.032, 0.022), (0.16, 0.15, 0.14, 1.0))
    for si, (ox, oy) in enumerate(((-0.055, 0.03), (0.055, -0.035))):
        make_box("FrenchToast_Slice_%d" % si, (sx - 0.16 + ox, sy + 0.10 + oy, 0.995),
                 (0.105, 0.085, 0.028), bread)
        make_box("FrenchToast_Slice_%d_Crust" % si, (sx - 0.16 + ox, sy + 0.10 + oy, 1.012),
                 (0.109, 0.089, 0.006), crust)
    # The challah on the counter beside the stove, cut end toward
    # the skillet; two slices' worth already gone.
    make_box("FrenchToast_Challah", (-1.65, ROOM_D - 1.05, 0.99), (0.30, 0.13, 0.11), crust)
    make_box("FrenchToast_Challah_Cut", (-1.49, ROOM_D - 1.05, 0.99), (0.012, 0.125, 0.105), bread)
    make_cyl("FrenchToast_EggBowl", (-1.95, ROOM_D - 1.10, 0.975), 0.095, 0.055,
             (0.90, 0.88, 0.84, 1.0), segments=12)
    make_cyl("FrenchToast_Egg", (-1.95, ROOM_D - 1.10, 1.015), 0.078, 0.008,
             (0.94, 0.80, 0.42, 1.0), segments=12)
    make_cyl("FrenchToast_Cinnamon", (-1.78, ROOM_D - 1.22, 0.985), 0.028, 0.075,
             (0.55, 0.34, 0.18, 1.0), segments=8)


def build_wear_personality_2026_08():
    """WHOSE FEET, WHOSE SPILLS (wear-personality pass 3 — a FAMILY).

    Third pass in the set, completing the triptych: Olaf's decades
    alone, Lena's three years alone, and here a HOUSEHOLD. A family
    walks wide where one person walks narrow; and one chair at this
    table is named Chair_Short_Mike, and the prose about Mike runs
    in the past tense ("Mike had insisted on it," "the way Mike had
    always cut his French toast"). His place gets the cabin
    vocabulary: long wear, stopped.
    """
    from _props.detail import make_traffic_wear, make_floor_stain, make_scuff_band
    floor_dk = (0.34, 0.28, 0.21, 1.0)
    floor_pale = (0.48, 0.40, 0.30, 1.0)
    tx, ty = 0.5, 3.0
    # ── The family's WIDE path · door → table → counter ──
    make_traffic_wear("Wear_Family_Path",
                      [(0.4, 0.8), (0.2, 2.2), (-0.6, 3.4), (-1.5, 4.4)],
                      width=0.70, tint=floor_dk)
    # ── The 4:32 spot · her feet at the sink, years of one hour
    # nobody else is awake for. Narrow, worn dark, right where the
    # under-cabinet light falls.
    make_floor_stain("Wear_Sink_Stand", (-1.75, 4.55), radius=0.24,
                     tint=(0.30, 0.24, 0.18, 1.0), segments=9)
    # Coffee-measure dust arc at the counter corner by the sink.
    make_floor_stain("Wear_Coffee_Dust", (-2.15, 4.35), radius=0.10,
                     tint=(0.40, 0.30, 0.20, 1.0), segments=7)
    # ── The landline's wear · a hand patch on the wall where the
    # handset is grabbed, and the cord's drag-trace toward the
    # table (the cord reaches; the wall shows the reaching).
    make_box("Wear_Phone_HandPatch", (-2.85, 5.87, 1.28), (0.16, 0.01, 0.14),
             (0.74, 0.70, 0.62, 1.0))
    make_scuff_band("Wear_Phone_CordArc", (-2.45, 5.82), 0.7, axis='X',
                    height=0.06, band_z=1.02, tint=(0.70, 0.66, 0.58, 1.0))
    # ── Sixteen years of French toast · the cutting board lives by
    # the stove; its center is worn pale with knife lines.
    make_box("Wear_Board", (-1.65, 4.72, 0.955), (0.38, 0.26, 0.018),
             (0.62, 0.50, 0.34, 1.0))
    make_box("Wear_Board_Center", (-1.65, 4.72, 0.966), (0.24, 0.15, 0.004), floor_pale)
    for ki in range(3):
        make_box("Wear_Board_Knifeline_%d" % ki, (-1.70 + ki * 0.05, 4.72, 0.968),
                 (0.005, 0.13, 0.002), (0.44, 0.34, 0.22, 1.0))
    # ── The chairs tell the household ──
    # (Table sits at tx=0.5 — the first draft of this pass put the
    # stains at tx=0.0 and missed every chair by half a meter.)
    # Sammy's and Bianca's places: dark crescents where feet tuck
    # daily. Mike's place carries BOTH ages stacked: the pale patch
    # of his years, and a small new dark crescent inside it —
    # because "since June she has been sitting in Mike's chair."
    # The guest chair: nothing.
    make_floor_stain("Wear_Chair_Sammy", (tx - 1.45, ty), radius=0.20,
                     tint=floor_dk, segments=8)
    make_floor_stain("Wear_Chair_Bianca", (tx, ty - 1.25), radius=0.20,
                     tint=floor_dk, segments=8)
    make_floor_stain("Wear_Chair_Mike_Years", (tx + 1.45, ty), radius=0.22,
                     tint=floor_pale, segments=8)
    make_floor_stain("Wear_Chair_Mike_June", (tx + 1.38, ty + 0.05), radius=0.11,
                     tint=(0.37, 0.30, 0.225, 1.0), segments=8)
    # The Sentinel on the table, folded, at Mike's end — "they
    # still get the Sentinel, Mike had insisted on it."
    make_box("Sentinel_Folded", (tx + 0.55, ty + 0.18, 0.775), (0.30, 0.20, 0.015),
             (0.86, 0.84, 0.78, 1.0))
    make_box("Sentinel_Headline", (tx + 0.55, ty + 0.18, 0.784), (0.22, 0.03, 0.002),
             (0.28, 0.26, 0.24, 1.0))


def build_infrastructure_2026_08():
    """D3 INFRASTRUCTURE — rooms are plugged in (one pass deep,
    per the set-detail playbook). A 2010s family kitchen runs on
    outlets and cords, and every electric thing in the room now
    has both. The landline keeps its own 2014 story: its jack is
    the old four-pin kind, lower on the wall than code would put
    it today, because the wire predates the remodel.
    """
    from _props.detail import (make_wall_outlet, make_light_switch,
                               make_cord_run)
    # Door wall (south): the light switch where a hand finds it in
    # the dark, at the door's latch side.
    make_light_switch("Switch_Door", (1.15, 0.10), axis='X', face_sign=1, z=1.20)
    # Counter-run outlets on the north wall at backsplash height —
    # the code pair, one per work zone.
    make_wall_outlet("Outlet_Counter_W", (-2.35, 5.92), axis='X', face_sign=-1, z=1.05)
    make_wall_outlet("Outlet_Counter_E", (0.65, 5.92), axis='X', face_sign=-1, z=1.05)
    # Floor-level outlet on the east wall behind the table (the
    # vacuum outlet every dining room has).
    make_wall_outlet("Outlet_East", (2.92, 2.4), axis='Y', face_sign=-1, z=0.30)
    # The under-cabinet light's cord drops behind the counter lip
    # to the west counter outlet.
    make_cord_run("Cord_UnderCab", (-1.20, 5.90, 1.54), (-2.30, 5.90, 1.08),
                  sag=0.06)
    # Microwave cord to the same duplex — two plugs, one plate,
    # the quiet crowding of a real counter.
    make_cord_run("Cord_Microwave", (-2.35, 5.62, 1.10), (-2.36, 5.90, 1.05),
                  sag=0.04)
    # The LANDLINE's jack: old four-pin plate at 0.42 on the north
    # wall below the phone, wire predating the remodel, and the
    # flat line cord up to the base.
    make_box("PhoneJack_Plate", (-2.85, 5.925, 0.42), (0.07, 0.012, 0.11),
             (0.82, 0.79, 0.72, 1.0))
    make_cord_run("Cord_PhoneLine", (-2.85, 5.90, 0.46), (-2.85, 5.89, 1.30),
                  sag=0.03)
    # HVAC: a floor register under the east window — the vent every
    # kitchen argument gets carried through.
    make_box("Vent_Register", (2.55, 3.30, 0.045), (0.36, 0.14, 0.09),
             (0.72, 0.70, 0.66, 1.0))
    for vi in range(5):
        make_box("Vent_Register_Slat_%d" % vi, (2.45 + vi * 0.05, 3.30, 0.095),
                 (0.012, 0.11, 0.008), (0.55, 0.53, 0.50, 1.0))


def main():
    clear_scene()
    build_shell()
    build_counter()
    build_table()
    build_fridge()
    build_clock()
    build_window()
    build_ceiling_infra()
    build_dressing()
    build_phone_and_toast_2026_08()
    build_wear_personality_2026_08()
    build_infrastructure_2026_08()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/miller_kitchen.glb"))
    print(f"\n[build_miller_kitchen] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
