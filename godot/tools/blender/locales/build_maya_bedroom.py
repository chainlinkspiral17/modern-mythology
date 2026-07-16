"""Maya's Bedroom — vol6 — Maya Miller (Chief Miller's daughter, a
sharp, observant teenage girl). Distinct LAVENDER + teal palette and a
teen-girl prop set (vanity + round mirror + string lights, a bulletin
board of photos & concert tickets, a bookshelf of paperbacks, a record
player, plants, a patterned duvet + throw pillows, a hamper, a rug) so
the room reads unmistakably as HERS — not a reskin of Sam's."""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots, make_donut_display
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture, make_ceiling_speaker

ROOM_W = 4.0; ROOM_D = 5.0; CEIL = 2.6
# Lavender walls, teal accent — cool, distinct from the boys' tan rooms.
PAL_WALL = {"wall": (0.74, 0.68, 0.86, 1.0), "baseboard": (0.50, 0.44, 0.62, 1.0)}
COL_FLOOR = (0.70, 0.60, 0.50, 1.0); COL_SEAM = (0.44, 0.34, 0.26, 1.0); COL_WOOD = (0.56, 0.42, 0.52, 1.0)
COL_ACCENT = (0.36, 0.72, 0.70, 1.0)     # teal
COL_DUVET = (0.60, 0.42, 0.72, 1.0)      # violet duvet
COL_DUVET2 = (0.42, 0.70, 0.68, 1.0)     # teal patterned band
COL_PILLOW = (0.94, 0.80, 0.86, 1.0)     # blush throw pillows

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

def build_bed():
    # Re-arranged (2026-07-15): bed pushed under the N window, headboard
    # against the N wall — frees the W wall for the vanity and reads
    # distinct from the shared -ROOM_W/4 side-wall twin. Keeps her
    # violet/teal duvet + throw pillows.
    bx, by = 0.0, ROOM_D - 1.15
    make_box("Bed_Frame", (bx, by, 0.20), (1.24, 1.86, 0.20), (0.52, 0.40, 0.50, 1.0))
    make_box("Bed_Mattress", (bx, by, 0.40), (1.14, 1.76, 0.16), (0.92, 0.86, 0.84, 1.0))
    make_box("Bed_Headboard", (bx, by+0.94, 0.66), (1.28, 0.10, 0.72), (0.50, 0.36, 0.48, 1.0))
    # Patterned duvet: violet body + a teal cross-band
    make_box("Bed_Duvet", (bx, by-0.10, 0.50), (1.20, 1.10, 0.12), COL_DUVET)
    make_box("Bed_DuvetBand", (bx, by-0.55, 0.52), (1.20, 0.34, 0.13), COL_DUVET2)
    # Throw pillows in front of the sleeping pillow
    make_box("Bed_Pillow", (bx, by+0.66, 0.50), (1.04, 0.34, 0.12), P.PAPER)
    make_box("Bed_ThrowPillow_A", (bx-0.30, by+0.44, 0.56), (0.34, 0.34, 0.16), COL_PILLOW)
    make_box("Bed_ThrowPillow_B", (bx+0.30, by+0.44, 0.56), (0.34, 0.34, 0.16), COL_ACCENT)

def build_desk_lamp():
    dx, dy = +ROOM_W/4.0, 1.5
    make_box("Desk_Top", (dx, dy, 0.74), (1.00, 0.60, 0.04), COL_WOOD)
    for li in range(4):
        lx, ly = dx+(-0.44,+0.44,-0.44,+0.44)[li], dy+(-0.24,-0.24,+0.24,+0.24)[li]
        make_box(f"Desk_Leg_{li}", (lx, ly, 0.36), (0.04, 0.04, 0.72), COL_WOOD)
    make_box("Lamp_Base", (dx-0.30, dy+0.20, 0.78), (0.10, 0.10, 0.04), P.METAL_BLACK)
    make_cyl("Lamp_Arm", (dx-0.30, dy+0.20, 0.96), 0.012, 0.30, P.METAL_BLACK)
    make_cyl("Lamp_Head", (dx-0.20, dy+0.20, 1.16), 0.06, 0.08, COL_ACCENT)
    # A laptop, open, on the desk
    make_box("Laptop_Base", (dx+0.16, dy+0.06, 0.77), (0.34, 0.24, 0.03), P.METAL_STEEL)
    make_box("Laptop_Screen", (dx+0.16, dy+0.18, 0.90), (0.34, 0.02, 0.24), (0.62, 0.80, 0.92, 1.0))
    # A little stack of paperbacks
    for bi in range(3):
        make_box(f"Desk_Book_{bi}", (dx-0.36, dy-0.14+bi*0.05, 0.79+bi*0.05), (0.16, 0.24, 0.05),
                 P.SNACK_TINTS[bi%len(P.SNACK_TINTS)])

def build_posters():
    # Band / art posters along the west wall
    for pi in range(3):
        px = -ROOM_W/2.0+0.05
        py = 1.0 + pi*1.5
        make_faded_poster(f"Poster_W_{pi}", (px, py, 1.60))

def build_rug():
    make_cyl("Rug", (0.0, ROOM_D/2.0, 0.012), 1.20, 0.005, COL_ACCENT)

def build_win():
    make_window("Window_N", (0.0, ROOM_D-0.02, 1.50), width=1.20, height=1.00)

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))
    make_hvac_vent("HVAC", (-ROOM_W/4.0, ROOM_D-0.5, CEIL), width=0.80, depth=0.40)

def build_dressing():
    """Teen-girl dressing: a vanity with a ROUND mirror + trinket bottles,
    warm string lights along the north wall, a bulletin board of photos &
    concert tickets, a bookshelf of paperbacks, a record player on a
    crate, a hamper, and a floor plant."""
    bx, by = 0.0, ROOM_D - 1.15
    # Nightstand + alarm clock beside the bed
    nsx = bx + 0.95
    make_box("Nightstand", (nsx, by+0.7, 0.28), (0.40, 0.40, 0.56), COL_WOOD)
    make_box("Clock", (nsx, by+0.7, 0.62), (0.15, 0.10, 0.10), P.METAL_BLACK)
    # Vanity dresser against the east wall: body, three drawers, ROUND mirror
    vx = ROOM_W/2.0 - 0.30
    make_box("Vanity_Body", (vx, ROOM_D-1.2, 0.42), (0.50, 0.90, 0.84), COL_WOOD)
    for di in range(3):
        make_box(f"Vanity_Drawer_{di}", (vx-0.26, ROOM_D-1.2, 0.24+di*0.24), (0.02, 0.80, 0.18), (0.44, 0.32, 0.42, 1.0))
    make_cyl("Vanity_Mirror", (vx-0.02, ROOM_D-1.2, 1.34), 0.34, 0.03, (0.80, 0.86, 0.92, 0.6), axis='X', segments=16)
    make_cyl("Vanity_MirrorFrame", (vx+0.005, ROOM_D-1.2, 1.34), 0.38, 0.03, COL_ACCENT, axis='X', segments=16)
    # Perfume/trinket bottles on the vanity top
    for ti, tc in enumerate([(0.86, 0.62, 0.72, 1.0), (0.62, 0.78, 0.86, 1.0), (0.92, 0.82, 0.42, 1.0)]):
        make_cyl(f"Trinket_{ti}", (vx-0.1, ROOM_D-1.5+ti*0.2, 0.90), 0.03, 0.10, tc, segments=8)
    # Bulletin board (cork) with a scatter of photos + concert tickets, west wall
    bbx = -ROOM_W/2.0 + 0.06
    make_box("Corkboard", (bbx, ROOM_D-1.0, 1.55), (0.04, 1.10, 0.80), (0.62, 0.46, 0.30, 1.0))
    for pi in range(6):
        col = (0.90, 0.88, 0.82, 1.0) if pi % 2 == 0 else P.SNACK_TINTS[pi % len(P.SNACK_TINTS)]
        oy = ROOM_D-1.4 + (pi % 3) * 0.34
        oz = 1.30 + (pi // 3) * 0.36
        make_box(f"Pin_{pi}", (bbx+0.03, oy, oz), (0.01, 0.24, 0.18), col)
    # Bookshelf of paperbacks against the north wall
    shx = ROOM_W/2.0 - 0.9
    make_box("Bookshelf_Body", (shx, ROOM_D-0.20, 0.90), (0.90, 0.26, 1.80), COL_WOOD)
    for r in range(3):
        for c in range(7):
            make_box(f"Book_{r}_{c}", (shx-0.42+c*0.12, ROOM_D-0.22, 0.42+r*0.52),
                     (0.10, 0.20, 0.30), P.SNACK_TINTS[(r*7+c) % len(P.SNACK_TINTS)])
    # Record player on a milk crate, SE
    rcx, rcy = ROOM_W/2.0-0.4, 0.8
    make_box("Crate", (rcx, rcy, 0.24), (0.44, 0.44, 0.48), (0.42, 0.52, 0.62, 1.0))
    make_box("RecordPlayer", (rcx, rcy, 0.52), (0.42, 0.42, 0.10), P.METAL_BLACK)
    make_cyl("RecordPlatter", (rcx, rcy, 0.58), 0.16, 0.01, (0.14, 0.14, 0.16, 1.0), segments=16)
    # Wicker hamper, corner
    make_cyl("Hamper", (-ROOM_W/2.0+0.5, 0.6, 0.34), 0.26, 0.68, (0.74, 0.62, 0.44, 1.0), segments=12)
    # Floor plant, SE corner
    make_floor_plant("Plant", (ROOM_W/2.0-0.5, 0.7, 0.0), palette={"leaf": (0.40, 0.60, 0.42, 1.0), "pot": (0.42, 0.72, 0.70, 1.0)})
    # Warm string / fairy lights along the north wall
    for i in range(8):
        make_cyl(f"Fairy_{i}", (-1.4+i*0.4, ROOM_D-0.08, 2.05), 0.028, 0.028, (1.0, 0.84, 0.6, 1.0), segments=6)

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
        "../../../assets/3d/locales/maya_bedroom.glb"))
    print(f"\n[build_maya_bedroom] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
