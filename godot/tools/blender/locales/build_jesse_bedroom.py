"""Jesse's Bedroom — vol6 — Jesse (the music kid). DARK/WARM palette
(plum-charcoal walls, amber accent) and a musician's prop set: a guitar
on a stand + a practice amp, a record-crate + turntable, headphones,
egg-crate acoustic foam on one wall, a mattress-on-the-floor / futon
vibe, warm string lights, and lyric sheets pinned up — so it reads
unmistakably as Jesse's, not a reskin of Diego's."""
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

ROOM_W = 4.0; ROOM_D = 4.5; CEIL = 2.6
# Plum-charcoal walls, amber accent — dark and warm, a practice-space vibe.
PAL_WALL = {"wall": (0.34, 0.29, 0.33, 1.0), "baseboard": (0.20, 0.16, 0.18, 1.0)}
COL_FLOOR = (0.34, 0.28, 0.24, 1.0); COL_SEAM = (0.20, 0.16, 0.14, 1.0); COL_WOOD = (0.40, 0.30, 0.20, 1.0)
COL_ACCENT = (0.86, 0.56, 0.28, 1.0)     # warm amber
COL_FOAM = (0.22, 0.20, 0.22, 1.0)       # acoustic foam
COL_BLANKET = (0.52, 0.30, 0.28, 1.0)    # warm rust futon blanket

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
    # Mattress on the floor / futon — low, no tall frame.
    bx, by = -ROOM_W/4.0, ROOM_D/2.0
    make_box("Futon_Pallet", (bx, by, 0.08), (1.24, 1.84, 0.16), (0.28, 0.22, 0.18, 1.0))
    make_box("Futon_Mattress", (bx, by, 0.24), (1.16, 1.76, 0.18), (0.72, 0.66, 0.60, 1.0))
    make_box("Futon_Blanket", (bx, by-0.20, 0.34), (1.16, 1.10, 0.10), COL_BLANKET)
    make_box("Futon_Pillow", (bx, by+0.66, 0.34), (1.00, 0.34, 0.12), (0.86, 0.78, 0.66, 1.0))

def build_desk_lamp():
    # Desk doubles as the turntable / gear bench.
    dx, dy = +ROOM_W/4.0, 1.5
    make_box("Desk_Top", (dx, dy, 0.74), (1.00, 0.60, 0.04), COL_WOOD)
    for li in range(4):
        lx, ly = dx+(-0.44,+0.44,-0.44,+0.44)[li], dy+(-0.24,-0.24,+0.24,+0.24)[li]
        make_box(f"Desk_Leg_{li}", (lx, ly, 0.36), (0.04, 0.04, 0.72), COL_WOOD)
    make_box("Lamp_Base", (dx-0.30, dy+0.20, 0.78), (0.10, 0.10, 0.04), P.METAL_BLACK)
    make_cyl("Lamp_Arm", (dx-0.30, dy+0.20, 0.96), 0.012, 0.30, P.METAL_BLACK)
    make_cyl("Lamp_Head", (dx-0.20, dy+0.20, 1.16), 0.06, 0.08, COL_ACCENT)
    # Turntable on the desk + a record on the platter
    make_box("Turntable", (dx+0.14, dy+0.02, 0.79), (0.42, 0.44, 0.08), P.METAL_BLACK)
    make_cyl("Turntable_Platter", (dx+0.14, dy+0.02, 0.85), 0.16, 0.01, (0.14, 0.14, 0.16, 1.0), segments=16)
    make_cyl("Record_Spinning", (dx+0.14, dy+0.02, 0.855), 0.15, 0.006, (0.08, 0.08, 0.09, 1.0), segments=16)
    # Headphones resting on the desk edge (band + two cups)
    make_cyl("Headphone_Band", (dx-0.30, dy-0.14, 0.84), 0.10, 0.02, COL_ACCENT, axis='Y', segments=12)
    for hs in (-1, +1):
        make_cyl(f"Headphone_Cup_{hs:+d}", (dx-0.30, dy-0.14+hs*0.10, 0.80), 0.06, 0.06, P.METAL_BLACK, axis='Y', segments=10)

def build_posters():
    # Band posters along the west wall
    for pi in range(3):
        px = -ROOM_W/2.0+0.05
        py = 0.9 + pi*1.4
        make_faded_poster(f"Poster_Band_{pi}", (px, py, 1.55))

def build_win():
    make_window("Window_N", (0.0, ROOM_D-0.02, 1.50), width=1.20, height=1.00)

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))
    make_hvac_vent("HVAC", (-ROOM_W/4.0, ROOM_D-0.5, CEIL), width=0.80, depth=0.40)

def build_dressing():
    """Musician's dressing: a guitar on a stand + a practice amp, a crate
    of records, warm string lights along the north wall, egg-crate foam on
    the east wall, lyric sheets pinned to the west wall, a dresser, and a
    corner plant (wires the imported make_floor_plant)."""
    bx, by = -ROOM_W/4.0, ROOM_D/2.0
    make_box("Nightstand", (bx+0.95, by+0.7, 0.24), (0.40, 0.40, 0.48), COL_WOOD)
    make_box("Clock", (bx+0.95, by+0.7, 0.54), (0.15, 0.10, 0.10), P.METAL_BLACK)
    # Guitar on an A-frame stand, SE corner
    gx, gy = ROOM_W/2.0-0.5, 0.9
    for ss in (-1, +1):
        make_cyl(f"GuitarStand_Leg_{ss:+d}", (gx+ss*0.12, gy, 0.30), 0.02, 0.60, P.METAL_BLACK, segments=6)
    make_cyl("GuitarStand_Cross", (gx, gy, 0.20), 0.02, 0.24, P.METAL_BLACK, axis='X', segments=6)
    make_cyl("Guitar_Body", (gx, gy-0.04, 0.55), 0.20, 0.10, COL_ACCENT, axis='Y', segments=14)
    make_box("Guitar_Neck", (gx, gy-0.04, 1.05), (0.07, 0.06, 0.90), COL_WOOD)
    make_box("Guitar_Head", (gx, gy-0.04, 1.54), (0.10, 0.05, 0.18), P.METAL_BLACK)
    # Practice amp next to the guitar
    ax, ay = ROOM_W/2.0-0.35, 1.7
    make_box("Amp_Cab", (ax, ay, 0.28), (0.44, 0.36, 0.56), (0.16, 0.14, 0.14, 1.0))
    make_cyl("Amp_Speaker", (ax-0.20, ay, 0.28), 0.14, 0.02, (0.28, 0.26, 0.26, 1.0), axis='X', segments=14)
    make_box("Amp_Panel", (ax, ay, 0.54), (0.44, 0.36, 0.06), COL_ACCENT)
    for ki in range(3):
        make_cyl(f"Amp_Knob_{ki}", (ax-0.14+ki*0.14, ay-0.20, 0.56), 0.02, 0.03, P.METAL_STEEL, segments=6)
    # Crate of records on the floor
    make_box("Record_Crate", (0.5, 0.6, 0.20), (0.46, 0.46, 0.40), COL_WOOD)
    for ri in range(5):
        make_box(f"Record_{ri}", (0.5, 0.42+ri*0.07, 0.24), (0.42, 0.02, 0.34), P.SNACK_TINTS[ri % len(P.SNACK_TINTS)])
    # Egg-crate acoustic foam grid on the east wall
    ex = ROOM_W/2.0 - 0.04
    for r in range(4):
        for c in range(5):
            make_box(f"Foam_{r}_{c}", (ex, ROOM_D-1.9+c*0.34, 1.1+r*0.34), (0.02, 0.28, 0.28), COL_FOAM)
    # Lyric sheets pinned to the west wall
    for li in range(4):
        make_box(f"Lyric_{li}", (-ROOM_W/2.0+0.06, 0.7+(li%2)*0.5, 2.05-(li//2)*0.5), (0.02, 0.24, 0.30), (0.88, 0.84, 0.76, 1.0))
    # Dresser against the north-east wall
    make_box("Dresser", (ROOM_W/2.0-0.30, ROOM_D-0.5, 0.45), (0.44, 0.9, 0.90), COL_WOOD)
    for di in range(3):
        make_box(f"Dresser_Drawer_{di}", (ROOM_W/2.0-0.52, ROOM_D-0.5, 0.24+di*0.24), (0.02, 0.78, 0.16), (0.28, 0.20, 0.14, 1.0))
    # Warm string lights along the north wall
    for i in range(8):
        make_cyl(f"String_{i}", (-1.4+i*0.4, ROOM_D-0.08, 2.05), 0.028, 0.028, COL_ACCENT, segments=6)
    # Corner plant (wires the imported helper)
    make_floor_plant("Plant", (-ROOM_W/2.0+0.5, ROOM_D-0.6, 0.0), palette={"leaf": (0.34, 0.42, 0.28, 1.0), "pot": (0.50, 0.34, 0.22, 1.0)})

def main():
    clear_scene()
    build_shell()
    build_bed()
    build_desk_lamp()
    build_dressing()
    build_posters()
    build_win()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/jesse_bedroom.glb"))
    print(f"\n[build_jesse_bedroom] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
