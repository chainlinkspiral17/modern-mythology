"""Sam's Bedroom — vol5-7 — Sam (the kid protagonist; into Cosmic Comics
and video games). Boyish BLUE/GREEN palette and a distinct prop set:
a captain's bed with storage drawers, comic/movie posters, a shelf of
comic longboxes + action figures, a CRT/TV + game console, a desk with
sketches + a lamp, a beanbag, and model kits — so it reads as a
comics-and-games kid's room, not a reskin of Maya's."""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture

ROOM_W = 4.0; ROOM_D = 5.0; CEIL = 2.6
# Denim-blue walls, lime-green accent — boyish, distinct from the girls'/others'.
PAL_WALL = {"wall":(0.56,0.66,0.78,1.0),"baseboard":(0.32,0.40,0.50,1.0)}
COL_FLOOR = (0.60,0.60,0.62,1.0); COL_SEAM = (0.38,0.38,0.42,1.0); COL_WOOD = (0.40,0.46,0.40,1.0)
COL_ACCENT = (0.44,0.66,0.36,1.0)        # lime green
COL_BLUE = (0.24,0.42,0.66,1.0)          # cosmic blue bedding
COL_BLUE_DK = (0.16,0.28,0.46,1.0)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)

def build_bed():
    # Captain's bed: raised frame with a row of storage drawers underneath.
    bx, by = -ROOM_W/4.0, ROOM_D/2.0
    make_box("Bed_Base", (bx, by, 0.24), (1.24, 1.84, 0.48), COL_WOOD)
    for di in range(3):
        make_box(f"Bed_Drawer_{di}", (bx+0.64, by-0.6+di*0.6, 0.24), (0.02, 0.52, 0.36), (0.30, 0.36, 0.30, 1.0))
        make_cyl(f"Bed_DrawerPull_{di}", (bx+0.66, by-0.6+di*0.6, 0.24), 0.03, 0.04, P.METAL_STEEL, axis='X', segments=6)
    make_box("Bed_Mattress", (bx, by, 0.56), (1.10, 1.70, 0.16), (0.90, 0.90, 0.86, 1.0))
    make_box("Bed_Headboard", (bx, by+0.90, 0.86), (1.24, 0.10, 0.68), COL_WOOD)
    make_box("Bed_Pillow", (bx, by+0.58, 0.68), (0.96, 0.36, 0.12), (0.92, 0.92, 0.86, 1.0))
    make_box("Bed_Comforter", (bx, by-0.24, 0.66), (1.14, 1.14, 0.12), COL_BLUE)
    make_box("Bed_ComforterStripe", (bx, by-0.6, 0.68), (1.14, 0.30, 0.13), COL_ACCENT)

def build_desk_lamp():
    dx, dy = +ROOM_W/4.0, 1.5
    make_box("Desk_Top", (dx, dy, 0.74), (1.00, 0.60, 0.04), COL_WOOD)
    for i, (lx, ly) in enumerate([(-0.44, -0.26), (0.44, -0.26), (-0.44, 0.26), (0.44, 0.26)]):
        make_box(f"Desk_Leg_{i}", (dx+lx, dy+ly, 0.37), (0.06, 0.06, 0.72), COL_WOOD)
    # Clip lamp
    make_cyl("Lamp_Base", (dx-0.34, dy+0.18, 0.78), 0.07, 0.03, P.METAL_BLACK)
    make_cyl("Lamp_Col", (dx-0.34, dy+0.18, 0.98), 0.02, 0.40, P.METAL_BLACK)
    make_cyl("Lamp_Head", (dx-0.24, dy+0.20, 1.16), 0.06, 0.10, COL_ACCENT)
    # Chunky CRT monitor + keyboard
    make_box("Monitor_Body", (dx+0.10, dy+0.14, 0.98), (0.42, 0.40, 0.38), (0.24, 0.24, 0.26, 1.0))
    make_box("Monitor_Screen", (dx+0.10, dy-0.06, 0.98), (0.34, 0.02, 0.28), (0.30, 0.52, 0.70, 1.0))
    make_box("Keyboard", (dx+0.10, dy-0.20, 0.77), (0.40, 0.16, 0.03), (0.32, 0.32, 0.34, 1.0))
    # Game console + controller
    make_box("Console", (dx-0.30, dy-0.16, 0.79), (0.26, 0.20, 0.06), P.METAL_BLACK)
    make_box("Controller", (dx+0.02, dy-0.22, 0.77), (0.14, 0.09, 0.03), COL_ACCENT)
    # Comic sketches / drawing pad + pencils spread on the desk
    make_box("SketchPad", (dx-0.20, dy+0.12, 0.765), (0.30, 0.40, 0.01), P.PAPER)
    for si in range(3):
        make_box(f"Sketch_{si}", (dx-0.28+si*0.10, dy+0.24, 0.767), (0.20, 0.26, 0.004), (0.92, 0.90, 0.84, 1.0))
    make_cyl("Pencil", (dx-0.05, dy+0.06, 0.762), 0.01, 0.18, (0.86, 0.72, 0.28, 1.0), axis='Y', segments=6)
    # Desk chair
    make_box("Chair_Seat", (dx, dy-0.55, 0.46), (0.42, 0.42, 0.05), COL_WOOD)
    make_box("Chair_Back", (dx, dy-0.74, 0.74), (0.42, 0.05, 0.46), COL_BLUE)
    for i, (lx, ly) in enumerate([(-0.16, -0.16), (0.16, -0.16), (-0.16, 0.16), (0.16, 0.16)]):
        make_box(f"Chair_Leg_{i}", (dx+lx, dy-0.55+ly, 0.23), (0.05, 0.05, 0.44), P.METAL_BLACK)

def build_posters():
    # Comic / movie posters along the west wall
    for pi in range(3):
        px = -ROOM_W/2.0+0.05; py = 1.0 + pi*1.5
        make_faded_poster(f"Poster_W_{pi}", (px, py, 1.55))

def build_rug():
    make_cyl("Rug", (0.0, ROOM_D/2.0, 0.012), 1.20, 0.005, COL_BLUE_DK)

def build_win():
    make_window("Window_N", (0.0, ROOM_D-0.02, 1.50), width=1.20, height=1.00)

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))

def build_dressing():
    """Comics-and-games clutter: a nightstand + clock, a shelf of comic
    longboxes + action figures, a stack of model kits, a beanbag, a
    skateboard, and a laundry pile. make_floor_plant is imported but this
    kid keeps no plants — wired here as a single small windowsill sprout."""
    bx, by = -ROOM_W/4.0, ROOM_D/2.0
    TINTS = P.SNACK_TINTS
    nsx = bx + 0.95
    make_box("Nightstand", (nsx, by+0.7, 0.28), (0.40, 0.40, 0.56), COL_WOOD)
    make_box("Clock", (nsx, by+0.7, 0.62), (0.16, 0.10, 0.10), P.METAL_BLACK)
    # Shelf on the east wall: comic longboxes on the bottom, figures on top
    shx = ROOM_W/2.0 - 0.18
    make_box("Shelf_Body", (shx, ROOM_D-1.4, 0.80), (0.34, 1.20, 1.60), COL_WOOD)
    # comic longboxes (long white boxes) on the lowest shelf
    for c in range(3):
        make_box(f"Longbox_{c}", (shx-0.02, ROOM_D-1.9+c*0.36, 0.34), (0.28, 0.32, 0.20), (0.88, 0.86, 0.80, 1.0))
    # action figures / statues on the middle + upper shelves
    for r in range(2):
        for c in range(4):
            fc = TINTS[(r*4+c) % len(TINTS)]
            make_cyl(f"Figure_{r}_{c}", (shx-0.04, ROOM_D-1.85+c*0.30, 0.78+r*0.42), 0.06, 0.26, fc, segments=8)
            make_cyl(f"FigureHead_{r}_{c}", (shx-0.04, ROOM_D-1.85+c*0.30, 0.95+r*0.42), 0.05, 0.10, (0.86, 0.70, 0.54, 1.0), segments=8)
    # Stack of model kit boxes in the SE corner
    for mi in range(3):
        make_box(f"ModelKit_{mi}", (ROOM_W/2.0-0.4, 0.7, 0.12+mi*0.16), (0.42-mi*0.04, 0.30, 0.14), TINTS[(mi*2) % len(TINTS)])
    # Beanbag chair (squashed stack of discs)
    for di in range(3):
        make_cyl(f"Beanbag_{di}", (0.3, 1.1, 0.14+di*0.10), 0.42-di*0.08, 0.12, COL_ACCENT, segments=14)
    # Skateboard leaning against the south wall
    make_box("Skateboard", (0.9, 0.15, 0.42), (0.20, 0.06, 0.80), COL_BLUE)
    for wi, wz in enumerate([0.10, 0.74]):
        make_cyl(f"Skate_Wheel_{wi}", (0.9, 0.10, wz), 0.05, 0.10, (0.86, 0.82, 0.30, 1.0), axis='X', segments=8)
    # Laundry pile in the corner
    for li, (lc, lz) in enumerate([((0.30, 0.44, 0.62, 1.0), 0.06), ((0.46, 0.60, 0.36, 1.0), 0.14), ((0.24, 0.36, 0.52, 1.0), 0.20)]):
        make_cyl(f"Laundry_{li}", (-ROOM_W/2.0+0.5, 0.6, lz), 0.24-li*0.04, 0.10, lc, segments=10)
    # Single small sprout on the windowsill (wires the imported helper)
    make_floor_plant("Sill_Sprout", (0.5, ROOM_D-0.4, 0.0), palette={"leaf": (0.40, 0.58, 0.34, 1.0), "pot": (0.30, 0.42, 0.30, 1.0)})

def main():
    clear_scene()
    build_shell()
    build_bed()
    build_desk_lamp()
    build_posters()
    build_rug()
    build_win()
    build_ceiling_infra()
    build_dressing()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/sam_bedroom.glb"))
    print(f"\n[build_sam_bedroom] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
