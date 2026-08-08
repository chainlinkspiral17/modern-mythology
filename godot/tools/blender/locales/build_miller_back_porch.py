"""Miller Back Porch — vol6's screened Texas porch (Bianca's), also
reused as Tem's cabin porch in vol7. Rebuilt 2026-08-03 hero-prop
pass: the prose specifies a SCREENED porch, her mother's wicker
chair from Lubbock, the crepe myrtle in the yard corner, the door
to the house, steps down to the browning yard, and (vol7) the
smokers' tin + Eddvard's thumb-sized carved cedar on the rail.

Coordinate frame: Blender Z-up, y=0 yard side (railing/steps), +Y
toward the house wall at y=4.0, x=±3.0, ceiling 2.8. glTF export
remaps to Godot (x, z, -y).
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling
from _props.decor import make_floor_plant

ROOM_W = 6.0; ROOM_D = 4.0; CEIL = 2.8
PAL_WALL = {"wall": (0.62, 0.46, 0.32, 1.0), "baseboard": (0.32, 0.22, 0.14, 1.0)}
COL_FLOOR = (0.42, 0.30, 0.20, 1.0); COL_SEAM = (0.22, 0.14, 0.10, 1.0)
COL_WOOD = (0.42, 0.30, 0.18, 1.0)
COL_ACCENT = (0.96, 0.62, 0.32, 1.0)
COL_SCREEN = (0.42, 0.42, 0.40, 0.30)   # the screen the dust motes hang in
COL_WICKER = (0.82, 0.70, 0.48, 1.0)    # her mother's chair, pale wicker
COL_GRASS = (0.42, 0.50, 0.30, 1.0)
COL_GRASS_DRY = (0.58, 0.54, 0.32, 1.0)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    # House wall (north) stays solid — it's the side of the house
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    # The other three sides are SCREENED: knee wall to z=1.0, screen
    # panels above, corner posts. ("It is screened in… the light
    # catches the small motes of dust in the screen of the porch.")
    for nm, x in (("Knee_W", -ROOM_W/2.0), ("Knee_E", +ROOM_W/2.0)):
        make_box(nm, (x, ROOM_D/2.0, 0.50), (0.16, ROOM_D+0.4, 1.00), PAL_WALL["wall"])
        make_box(nm+"_Screen", (x, ROOM_D/2.0, 1.80), (0.01, ROOM_D+0.2, 1.60), COL_SCREEN)
    for nm, cx, w in (("Knee_S_W", -(ROOM_W/4.0+0.5), ROOM_W/2.0-1.0),
                      ("Knee_S_E", +(ROOM_W/4.0+0.5), ROOM_W/2.0-1.0)):
        make_box(nm, (cx, 0.0, 0.50), (w, 0.16, 1.00), PAL_WALL["wall"])
        make_box(nm+"_Screen", (cx, 0.0, 1.80), (w, 0.01, 1.60), COL_SCREEN)
    make_box("Screen_AboveDoor", (0.0, 0.0, CEIL-0.15), (2.0, 0.01, 0.30), COL_SCREEN)
    for px, py in ((-ROOM_W/2.0, 0.0), (ROOM_W/2.0, 0.0),
                   (-ROOM_W/2.0, ROOM_D), (ROOM_W/2.0, ROOM_D)):
        make_box(f"Post_{px:.0f}_{py:.0f}", (px, py, CEIL/2.0), (0.16, 0.16, CEIL), COL_WOOD)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
                 with_grid=False, with_stains=False,
                 palette={"tile": (0.56, 0.44, 0.32, 1.0)})


def build_railing():
    make_box("Rail_Top", (0.0, 0.10, 1.00), (ROOM_W-1.0, 0.06, 0.06), COL_WOOD)
    for vi in range(10):
        vx = -(ROOM_W-1.0)/2.0+vi*0.6
        make_box(f"Rail_Bal_{vi}", (vx, 0.10, 0.50), (0.04, 0.04, 0.90), COL_WOOD)
    # vol7's rail-corner props: the small tin Tem keeps for the
    # people who smoke, and the thumb-sized carved cedar Eddvard left
    make_cyl("Smokers_Tin", (-2.20, 0.10, 1.05), 0.05, 0.03, (0.62, 0.62, 0.60, 1.0), segments=10)
    make_box("Carved_Cedar", (2.30, 0.10, 1.06), (0.03, 0.02, 0.05), (0.52, 0.34, 0.22, 1.0))


def build_chairs():
    """One rocker + HER MOTHER'S WICKER CHAIR (down from Lubbock in
    1989, against the back wall, with arms wide enough to set a
    coffee cup on)."""
    # The rocker keeps its spot west of center
    cx, cy = -1.5, ROOM_D/2.0
    make_box("Rocker_0_Seat", (cx, cy, 0.46), (0.50, 0.46, 0.04), COL_WOOD)
    make_box("Rocker_0_Back", (cx, cy+0.20, 0.78), (0.50, 0.04, 0.66), COL_WOOD)
    for si in range(4):
        sx = cx - 0.18 + si * 0.12
        make_cyl(f"Rocker_0_Spindle_{si}", (sx, cy+0.20, 0.72), 0.015, 0.44, COL_WOOD, segments=6)
    for ai, ax in enumerate([cx-0.24, cx+0.24]):
        make_box(f"Rocker_0_Arm_{ai}", (ax, cy, 0.62), (0.04, 0.44, 0.04), COL_WOOD)
        make_cyl(f"Rocker_0_ArmPost_{ai}", (ax, cy-0.18, 0.54), 0.02, 0.16, COL_WOOD, segments=6)
    for ri, ry in enumerate([cy-0.20, cy+0.20]):
        make_cyl(f"Rocker_0_Rocker_{ri}", (cx, ry, 0.10), 0.04, 0.50, COL_WOOD, axis='X', segments=8)
    # The wicker chair, against the house wall
    wx, wy = 1.20, ROOM_D - 0.65
    make_box("Wicker_Seat", (wx, wy, 0.42), (0.52, 0.48, 0.10), COL_WICKER)
    make_box("Wicker_Back", (wx, wy+0.24, 0.80), (0.54, 0.08, 0.70), COL_WICKER)
    make_box("Wicker_Back_Weave", (wx, wy+0.21, 0.80), (0.44, 0.02, 0.58), (0.74, 0.62, 0.42, 1.0))
    # Wide flat arms — "She puts the coffee cup down on the wicker
    # chair's arm"
    for ai, ax in enumerate((wx-0.34, wx+0.34)):
        make_box(f"Wicker_Arm_{ai}", (ax, wy, 0.60), (0.14, 0.52, 0.05), COL_WICKER)
        make_box(f"Wicker_ArmSide_{ai}", (ax, wy, 0.42), (0.10, 0.46, 0.32), COL_WICKER)
    for li, (lx, ly) in enumerate(((-0.20, -0.18), (0.20, -0.18), (-0.20, 0.20), (0.20, 0.20))):
        make_box(f"Wicker_Leg_{li}", (wx+lx, wy+ly, 0.18), (0.05, 0.05, 0.36), COL_WICKER)
    # The coffee cup on the arm
    make_cyl("Wicker_Cup", (wx-0.34, wy-0.08, 0.665), 0.04, 0.08, (0.86, 0.82, 0.74, 1.0), segments=10)


def build_doors():
    # Screen door to the YARD (south)
    make_box("ScreenDoor_Frame", (0.0, 0.0, 1.05), (1.00, 0.04, 2.10), COL_WOOD)
    make_box("ScreenDoor_Mesh", (0.0, 0.0, 1.05), (0.96, 0.005, 2.00), COL_SCREEN)
    # The door to the HOUSE (north) — Sam knocks on this frame
    make_box("HouseDoor_Frame", (-0.9, ROOM_D-0.06, 1.08), (1.04, 0.10, 2.16), COL_WOOD)
    make_box("HouseDoor", (-0.9, ROOM_D-0.04, 1.05), (0.90, 0.05, 2.05), (0.50, 0.38, 0.26, 1.0))
    make_cyl("HouseDoor_Knob", (-0.55, ROOM_D-0.10, 1.02), 0.03, 0.04, (0.66, 0.52, 0.24, 1.0), axis='Y', segments=8)
    # The house's lit window onto the porch (vol7: "The porch was lit
    # by the cabin's south window")
    make_box("HouseWin_Frame", (1.60, ROOM_D-0.05, 1.60), (1.10, 0.08, 1.10), COL_WOOD)
    make_box("HouseWin_Glow", (1.60, ROOM_D-0.08, 1.60), (0.94, 0.05, 0.94), (0.98, 0.82, 0.52, 1.0))


def build_yard():
    """Beyond the screens: the browning yard, the steps down, the
    crepe myrtle in the corner, the neighbor's oak."""
    make_box("Yard", (0.0, -4.5, -0.44), (16.0, 9.0, 0.05), COL_GRASS)
    for i, (px, py, pw, pd) in enumerate(((-3.5, -2.5, 2.2, 1.6), (2.0, -4.0, 1.8, 1.4),
                                          (5.0, -2.0, 1.5, 1.2), (-1.0, -6.0, 2.5, 1.8))):
        make_box(f"Yard_Brown_{i}", (px, py, -0.435), (pw, pd, 0.045), COL_GRASS_DRY)
    # Three treads from the screen door down to grade
    for si in range(3):
        make_box(f"Step_{si}", (0.0, -0.35 - si*0.32, -0.075 - si*0.15),
                 (1.3, 0.32, 0.15), COL_WOOD)
    # The crepe myrtle, late bloom, in the corner of the back yard
    mx, my = 2.6, -2.2
    for ti, (dx, dy) in enumerate(((0.0, 0.0), (0.14, 0.10), (-0.12, 0.08))):
        make_cyl(f"Myrtle_Trunk_{ti}", (mx+dx, my+dy, 1.0-0.44), 0.05, 2.0,
                 (0.55, 0.46, 0.40, 1.0), segments=6)
    for bi, (dx, dy, dz, r) in enumerate(((0.0, 0.0, 2.3, 0.75), (0.45, 0.2, 2.0, 0.55),
                                          (-0.4, 0.15, 2.1, 0.5), (0.1, -0.3, 2.55, 0.45))):
        # 2026-08-04: the crepe myrtle's bloom clusters were flat
        # cylinders. Blobs now — flowering mass, not pink pucks.
        from _props.geometry import make_blob
        make_blob(f"Myrtle_Canopy_{bi}", (mx+dx, my+dy, dz-0.40),
                  r * 1.05, (0.86, 0.52, 0.62, 1.0), noise=0.24,
                  seed=61 + bi, squash=0.75)
    # The neighbor's oak, farther off (the mockingbird's)
    make_cyl("Oak_Trunk", (-6.5, -5.5, 1.6-0.44), 0.22, 3.2, (0.36, 0.28, 0.20, 1.0), segments=8)
    from _props.geometry import make_blob as _mb_oak
    _mb_oak("Oak_Canopy", (-6.5, -5.5, 3.9-0.44), 2.35,
            (0.30, 0.40, 0.24, 1.0), noise=0.20, seed=83, squash=0.80)


def build_porchlamp():
    make_cyl("PorchLamp_Cord", (-1.5, 0.30, CEIL-0.20), 0.005, 0.40, P.METAL_BLACK)
    make_cyl("PorchLamp_Bulb", (-1.5, 0.30, CEIL-0.66), 0.08, 0.16, COL_ACCENT)
    # A porch, not an office: ceiling fan instead of tube fixtures
    fx, fy = 0.0, ROOM_D/2.0
    make_cyl("Fan_Downrod", (fx, fy, CEIL-0.12), 0.025, 0.24, P.METAL_BLACK, segments=6)
    make_cyl("Fan_Hub", (fx, fy, CEIL-0.28), 0.10, 0.10, P.METAL_BLACK, segments=10)
    for bi, (dx, dy) in enumerate([(0.55, 0.0), (-0.55, 0.0), (0.0, 0.55), (0.0, -0.55)]):
        make_box(f"Fan_Blade_{bi}", (fx+dx, fy+dy, CEIL-0.30),
                 (0.72 if dy == 0.0 else 0.20, 0.20 if dy == 0.0 else 0.72, 0.025),
                 (0.40, 0.30, 0.22, 1.0))


def build_dressing():
    """Side table by the rocker, doormat, potted plant, firewood,
    hanging planter (EAST side — the old comment said SW and lied)."""
    cy = ROOM_D/2.0
    COL_TERRA = (0.66, 0.40, 0.26, 1.0); COL_LEAF = (0.36, 0.48, 0.30, 1.0)
    make_cyl("SideTbl_Top", (0.0, cy, 0.44), 0.28, 0.04, COL_WOOD, segments=16)
    make_cyl("SideTbl_Col", (0.0, cy, 0.24), 0.05, 0.40, COL_WOOD, segments=8)
    for li in range(3):
        ang = li * (2.0 * math.pi / 3.0)
        make_box(f"SideTbl_Leg_{li}", (math.cos(ang) * 0.18, cy + math.sin(ang) * 0.18, 0.10),
                 (0.05, 0.05, 0.20), COL_WOOD)
    make_cyl("Mug_Body", (0.10, cy - 0.05, 0.52), 0.045, 0.09, (0.82, 0.36, 0.24, 1.0), segments=12)
    make_cyl("Mug_Handle", (0.16, cy - 0.05, 0.55), 0.02, 0.03, (0.82, 0.36, 0.24, 1.0), axis='X', segments=8)
    make_box("Newspaper", (-0.13, cy + 0.02, 0.475), (0.20, 0.14, 0.02), (0.80, 0.78, 0.72, 1.0))
    make_box("Doormat", (0.0, 0.55, 0.012), (0.90, 0.55, 0.02), (0.34, 0.26, 0.18, 1.0))
    make_floor_plant("Plant", (ROOM_W/2.0 - 0.55, ROOM_D - 0.6, 0.0),
                     palette={"leaf": COL_LEAF, "pot": COL_TERRA})
    for row in range(3):
        for col in range(4):
            make_cyl(f"Firewood_{row}_{col}",
                     (ROOM_W/2.0 - 0.38, 0.7 + col * 0.16, 0.12 + row * 0.15),
                     0.072, 0.5, (0.40, 0.28, 0.18, 1.0), axis='X', segments=8)
    make_cyl("Hanger_Cord", (1.5, cy - 0.5, CEIL - 0.35), 0.004, 0.70, P.METAL_BLACK)
    make_cyl("Hanger_Pot", (1.5, cy - 0.5, CEIL - 0.78), 0.14, 0.14, COL_TERRA, segments=12)
    for li in range(6):
        ang = li * (2.0 * math.pi / 6.0)
        make_cyl(f"Hanger_Leaf_{li}", (1.5 + math.cos(ang) * 0.17, cy - 0.5 + math.sin(ang) * 0.17, CEIL - 0.66),
                 0.03, 0.12, COL_LEAF)


def main():
    clear_scene()
    build_shell()
    build_railing()
    build_chairs()
    build_doors()
    build_yard()
    build_porchlamp()
    build_dressing()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/miller_back_porch.glb"))
    print(f"\n[build_miller_back_porch] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
