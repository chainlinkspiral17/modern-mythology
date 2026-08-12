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
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/miller_kitchen.glb"))
    print(f"\n[build_miller_kitchen] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
