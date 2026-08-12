"""Henderson Kitchen — vol6 placement script."""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import make_blob, clear_scene, make_box, make_chamfer_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots, make_donut_display
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture, make_ceiling_speaker

ROOM_W = 6.5; ROOM_D = 5.5; CEIL = 2.6
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
    # Stove
    make_chamfer_box("Stove_Body", (ROOM_W/4.0, ROOM_D-1.0, 0.45), (0.70, 0.70, 0.92), (0.86, 0.84, 0.80, 1.0))
    make_box("Stove_Top", (ROOM_W/4.0, ROOM_D-1.0, 0.92), (0.70, 0.70, 0.04), P.METAL_BLACK)

def build_table():
    tx, ty = 0.0, ROOM_D/2.0
    make_chamfer_box("Table_Top", (tx, ty, 0.74), (1.20, 0.80, 0.04), COL_WOOD)
    for li in range(4):
        lx = tx + (-0.54, +0.54, -0.54, +0.54)[li]
        ly = ty + (-0.34, -0.34, +0.34, +0.34)[li]
        make_box(f"Table_Leg_{li}", (lx, ly, 0.36), (0.04, 0.04, 0.72), COL_WOOD)
    for ci, (cx, cy) in enumerate([(tx-0.80, ty), (tx+0.80, ty), (tx, ty-0.62), (tx, ty+0.62)]):
        make_box(f"Chair_{ci}_Seat", (cx, cy, 0.44), (0.40, 0.40, 0.04), COL_WOOD)
        ddx, ddy = cx - tx, cy - ty
        if abs(ddx) >= abs(ddy):
            make_box(f"Chair_{ci}_Back", (cx + (0.18 if ddx > 0 else -0.18), cy, 0.70), (0.04, 0.40, 0.48), COL_WOOD)
        else:
            make_box(f"Chair_{ci}_Back", (cx, cy + (0.18 if ddy > 0 else -0.18), 0.70), (0.40, 0.04, 0.48), COL_WOOD)
        for k, (ox, oy) in enumerate([(-0.16, -0.16), (0.16, -0.16), (-0.16, 0.16), (0.16, 0.16)]):
            make_box(f"Chair_{ci}_Leg_{k}", (cx+ox, cy+oy, 0.22), (0.05, 0.05, 0.42), COL_WOOD)

def build_clock():
    make_wall_clock("Clock", (0.0, ROOM_D-0.05, CEIL-0.50), frozen_hour=10, frozen_min=38)

def build_fridge():
    fx, fy = +ROOM_W/2.0 - 0.50, 1.5
    make_chamfer_box("Fridge_Body", (fx, fy, 1.00), (0.70, 0.70, 2.00), (0.86, 0.84, 0.80, 1.0))
    make_chamfer_box("Fridge_DoorTop", (fx-0.34, fy, 1.50), (0.04, 0.66, 0.80), (0.86, 0.84, 0.80, 1.0))
    make_chamfer_box("Fridge_DoorBot", (fx-0.34, fy, 0.40), (0.04, 0.66, 1.00), (0.86, 0.84, 0.80, 1.0))
    make_box("Fridge_Handle", (fx-0.38, fy-0.20, 1.30), (0.04, 0.04, 0.50), P.METAL_STEEL)
    for mi in range(6):
        make_box(f"Magnet_{mi}", (fx-0.36, fy-0.20+mi*0.10, 1.60), (0.005, 0.06, 0.08), P.SNACK_TINTS[mi%len(P.SNACK_TINTS)])

def build_dressing():
    """Counter + table + wall dressing for a working family kitchen."""
    cw_x = -ROOM_W/4.0; cw_y = ROOM_D-1.0
    make_coffee_pots("Coffee", (cw_x-1.0, cw_y, 0.94), pots=1)
    make_box("DishRack_Base", (cw_x+0.9, cw_y, 0.95), (0.34, 0.30, 0.03), P.METAL_STEEL)
    for ti in range(5):
        make_box(f"DishRack_Tine_{ti}", (cw_x+0.74+ti*0.06, cw_y, 1.05), (0.01, 0.24, 0.16), P.METAL_STEEL)
    make_calendar("Calendar", (-ROOM_W/2.0+0.05, 2.0, 1.6))
    tx, ty = 0.0, ROOM_D/2.0
    make_box("NapkinHolder", (tx, ty, 0.82), (0.14, 0.06, 0.12), (0.86, 0.84, 0.80, 1.0))
    make_cyl("Salt", (tx+0.16, ty, 0.80), 0.025, 0.10, (0.92, 0.92, 0.90, 1.0), segments=8)
    make_cyl("Pepper", (tx+0.22, ty, 0.80), 0.025, 0.10, (0.28, 0.24, 0.22, 1.0), segments=8)
    make_floor_plant("Plant", (-ROOM_W/2.0+0.5, 0.7, 0.0), palette={"leaf": (0.36, 0.48, 0.30, 1.0), "pot": (0.60, 0.40, 0.26, 1.0)})

def build_ceiling_infra():
    # A night kitchen lit warm and low — dome + pendant, no tubes
    make_cyl("Ceiling_Dome", (0.0, 1.6, CEIL-0.10), 0.16, 0.16, (0.96, 0.88, 0.68, 1.0), segments=12)
    make_cyl("Table_Pendant_Cord", (0.0, ROOM_D/2.0, CEIL-0.14), 0.008, 0.28, P.METAL_BLACK)
    make_cyl("Table_Pendant_Shade", (0.0, ROOM_D/2.0, CEIL-0.36), 0.15, 0.15, (0.60, 0.44, 0.28, 1.0), segments=12)
    make_smoke_detector("Smoke", (0.9, ROOM_D/2.0, CEIL))


def build_hero_props():
    """2026-08-03 hero-prop pass: the front kitchen window (the one
    the porch build lights from outside), THE BASEMENT DOOR (the
    ch7 hinge), the stair mouth, the oven face, the microwave, four
    place settings — the fourth, at the head, unset for eight days
    until tonight — and the coffee mugs."""
    wood = (0.48, 0.36, 0.24, 1.0)
    # Front window, S wall east of the doorway — matches the porch
    # build's lit window at x=+2.55
    make_window("Front_Window", (1.45, 0.05, 1.50), width=0.90, height=1.05)
    # The basement door, E wall, dark stair void behind
    make_box("Basement_Doorframe", (ROOM_W/2.0-0.04, 1.6, 1.08), (0.10, 1.00, 2.16), wood)
    make_chamfer_box("Basement_Door", (ROOM_W/2.0-0.07, 1.6, 1.05), (0.05, 0.85, 2.05), (0.42, 0.32, 0.22, 1.0))
    make_box("Basement_Void", (ROOM_W/2.0-0.02, 1.6, 1.00), (0.02, 0.80, 2.00), (0.06, 0.05, 0.05, 1.0))
    # Stair mouth (up), S gap edge
    make_box("Stair_Newel", (0.92, 0.15, 0.60), (0.10, 0.10, 1.20), wood)
    for s in range(3):
        make_box(f"Stair_Tread_{s}", (1.4, 0.20, 0.16 + s * 0.18), (0.80, 0.28, 0.05), wood)
    # Oven face on the stove front (the pot roast on warm)
    sx, sy = ROOM_W/4.0, ROOM_D-1.0
    make_chamfer_box("Oven_Door", (sx, sy-0.36, 0.50), (0.60, 0.03, 0.55), (0.72, 0.70, 0.66, 1.0))
    make_box("Oven_Window", (sx, sy-0.375, 0.55), (0.40, 0.015, 0.26), (0.14, 0.12, 0.10, 1.0))
    make_box("Oven_Handle", (sx, sy-0.39, 0.80), (0.50, 0.03, 0.04), (0.55, 0.57, 0.58, 1.0))
    # Microwave, counter east end
    make_chamfer_box("Microwave", (-0.25, ROOM_D-1.0, 1.14), (0.50, 0.38, 0.30), (0.30, 0.30, 0.32, 1.0))
    # ── THE POT ROAST · the chapter's hero object ──────────────
    # (2026-08-12, shot_marker_audit --props) [shot:insert pot_roast]
    # fires 3x in a MODEL CHAPTER — "Eileen has made a pot roast…
    # the pot roast Eileen has been making on Sunday nights since he
    # was three. She has not made it since April." It was never
    # modeled; the insert framed bare table.
    # It sits at the table's head, still in the enameled dutch oven
    # it was cooked in, lid off and leaning against its own base —
    # which is what "she made it tonight" looks like from the door.
    tx0, ty0 = 0.0, ROOM_D/2.0
    enamel = (0.62, 0.16, 0.14, 1.0)      # the old red enamel
    enamel_dk = (0.46, 0.11, 0.10, 1.0)
    cream = (0.90, 0.88, 0.82, 1.0)       # the chipped interior
    roast = (0.42, 0.24, 0.16, 1.0)
    gravy = (0.34, 0.20, 0.12, 1.0)
    carrot = (0.78, 0.42, 0.16, 1.0)
    tater = (0.80, 0.72, 0.52, 1.0)
    # Dutch oven: body, a proud rolled rim, two lug handles
    make_cyl("PotRoast_Pot", (tx0, ty0 + 0.22, 0.855),
             0.155, 0.19, enamel, segments=16)
    make_cyl("PotRoast_Pot_Rim", (tx0, ty0 + 0.22, 0.948),
             0.166, 0.022, enamel_dk, segments=16)
    make_cyl("PotRoast_Pot_Inner", (tx0, ty0 + 0.22, 0.944),
             0.140, 0.010, cream, segments=16)
    for sgn in (-1, 1):
        make_box("PotRoast_Lug_%d" % sgn,
                 (tx0 + sgn * 0.175, ty0 + 0.22, 0.930),
                 (0.055, 0.085, 0.030), enamel_dk)
    # The roast itself, proud of the rim, with vegetables around it
    make_blob("PotRoast_Meat", (tx0, ty0 + 0.22, 0.975), 0.105,
              roast, noise=0.16, seed=5, squash=0.62)
    make_cyl("PotRoast_Gravy", (tx0, ty0 + 0.22, 0.950),
             0.132, 0.012, gravy, segments=14)
    for vi, (vx, vy) in enumerate(((-0.085, 0.055), (0.080, 0.040),
                                   (-0.050, -0.075), (0.065, -0.065))):
        col = carrot if vi % 2 == 0 else tater
        make_blob("PotRoast_Veg_%d" % vi,
                  (tx0 + vx, ty0 + 0.22 + vy, 0.962), 0.036,
                  col, noise=0.20, seed=11 + vi, squash=0.80)
    # The lid, OFF — leaning against the pot, which is the detail
    # that says it was served just now.
    make_cyl("PotRoast_Lid", (tx0 + 0.245, ty0 + 0.30, 0.815),
             0.150, 0.030, enamel, segments=16)
    make_cyl("PotRoast_Lid_Knob", (tx0 + 0.245, ty0 + 0.30, 0.845),
             0.024, 0.030, enamel_dk, segments=8)
    # A trivet under the pot — nobody puts a hot dutch oven on oak
    make_box("PotRoast_Trivet", (tx0, ty0 + 0.22, 0.768),
             (0.36, 0.36, 0.016), (0.36, 0.28, 0.20, 1.0))

    # Four place settings — the head setting is the shot
    tx, ty = 0.0, ROOM_D/2.0
    for si, (dx, dy) in enumerate(((-0.45, 0.0), (0.0, -0.32), (0.0, 0.32), (0.45, 0.0))):
        make_cyl(f"Setting_{si}_Plate", (tx+dx, ty+dy, 0.77), 0.11, 0.012, (0.90, 0.88, 0.84, 1.0), segments=12)
        make_box(f"Setting_{si}_Fork", (tx+dx-0.15, ty+dy, 0.772), (0.02, 0.12, 0.008), (0.60, 0.62, 0.63, 1.0))
    # Coffee mugs by the pot: three poured, one never drunk
    for mi, (mx, my) in enumerate(((-2.3, ROOM_D-1.15), (-2.15, ROOM_D-0.95), (0.35, ty-0.05))):
        make_cyl(f"Mug_{mi}", (mx, my, 0.99 if mi < 2 else 0.79), 0.04, 0.09,
                 [(0.72, 0.30, 0.22, 1.0), (0.30, 0.40, 0.52, 1.0), (0.86, 0.82, 0.74, 1.0)][mi], segments=10)


def main():
    clear_scene()
    build_shell()
    build_counter()
    build_table()
    build_dressing()
    build_hero_props()
    build_clock()
    build_fridge()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/henderson_kitchen.glb"))
    print(f"\n[build_henderson_kitchen] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
