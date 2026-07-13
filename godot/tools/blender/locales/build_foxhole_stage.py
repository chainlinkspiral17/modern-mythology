"""foxhole_stage — vol5-7 locale (auto-generated placement script)."""
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

ROOM_W = 8.0; ROOM_D = 5.0; CEIL = 3.2
PAL_WALL = {"wall":(0.62,0.46,0.32,1.0),"baseboard":(0.32,0.22,0.14,1.0)}
COL_FLOOR = (0.42,0.30,0.20,1.0); COL_SEAM = (0.22,0.14,0.10,1.0); COL_WOOD = (0.42,0.30,0.18,1.0)
COL_ACCENT = (0.96,0.62,0.32,1.0)

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

def build_posters():
    for pi in range(3):
        px = -ROOM_W/2.0+0.05; py = 1.0 + pi*1.5
        make_faded_poster(f"Poster_W_{pi}", (px, py, 1.50))

STAGE_Y = 4.2
STAGE_TOP = 0.30

def build_stage():
    make_box("Stage_Deck", (0.0, STAGE_Y, 0.15), (7.4, 1.6, 0.30), (0.20,0.16,0.14,1.0))
    make_box("Stage_Lip", (0.0, STAGE_Y-0.80, 0.28), (7.4, 0.05, 0.06), COL_ACCENT)
    make_box("Stage_Skirt", (0.0, STAGE_Y-0.80, 0.14), (7.4, 0.03, 0.28), (0.10,0.08,0.08,1.0))

def build_drums():
    dx, dy, dz = 0.0, 4.6, STAGE_TOP
    shell = (0.72,0.32,0.24,1.0); chrome = P.METAL_STEEL; brass = (0.86,0.72,0.30,1.0)
    make_cyl("Drum_Kick", (dx, dy, dz+0.28), 0.28, 0.42, (0.74,0.70,0.66,1.0), axis='Y', segments=16)
    make_cyl("Drum_KickHead", (dx, dy-0.21, dz+0.28), 0.27, 0.02, (0.92,0.90,0.86,1.0), axis='Y', segments=16)
    make_cyl("Drum_Snare", (dx-0.46, dy-0.30, dz+0.55), 0.16, 0.14, (0.86,0.84,0.80,1.0), segments=12)
    make_cyl("Drum_SnarePost", (dx-0.46, dy-0.30, dz+0.28), 0.02, 0.52, chrome)
    make_cyl("Drum_Tom0", (dx-0.16, dy, dz+0.64), 0.13, 0.16, shell, segments=12)
    make_cyl("Drum_Tom1", (dx+0.16, dy, dz+0.66), 0.14, 0.18, shell, segments=12)
    make_cyl("Drum_FloorTom", (dx+0.52, dy+0.10, dz+0.40), 0.18, 0.40, shell, segments=12)
    make_cyl("Drum_CymStandL", (dx-0.58, dy+0.15, dz+0.45), 0.015, 0.90, chrome)
    make_cyl("Drum_CymL", (dx-0.58, dy+0.15, dz+0.90), 0.22, 0.02, brass, segments=16)
    make_cyl("Drum_CymStandR", (dx+0.60, dy-0.05, dz+0.55), 0.015, 1.10, chrome)
    make_cyl("Drum_CymR", (dx+0.60, dy-0.05, dz+1.10), 0.26, 0.02, brass, segments=16)
    make_cyl("Drum_HHStand", (dx-0.52, dy-0.36, dz+0.40), 0.015, 0.80, chrome)
    make_cyl("Drum_HH", (dx-0.52, dy-0.36, dz+0.80), 0.16, 0.03, brass, segments=16)

def _make_amp_stack(prefix, cx, cy):
    cz = STAGE_TOP
    make_box(f"{prefix}_Cab", (cx, cy, cz+0.40), (0.70, 0.50, 0.80), (0.14,0.12,0.11,1.0))
    for i,(ox,oz) in enumerate([(-0.16,0.18),(0.16,0.18),(-0.16,-0.16),(0.16,-0.16)]):
        make_cyl(f"{prefix}_Cone_{i}", (cx+ox, cy-0.26, cz+0.40+oz), 0.13, 0.04, (0.08,0.07,0.07,1.0), axis='Y', segments=12)
    make_box(f"{prefix}_Head", (cx, cy, cz+0.92), (0.72, 0.44, 0.22), (0.20,0.18,0.16,1.0))
    make_box(f"{prefix}_Grille", (cx, cy-0.23, cz+0.92), (0.60, 0.02, 0.16), (0.34,0.30,0.22,1.0))
    for k in range(4):
        make_cyl(f"{prefix}_Knob_{k}", (cx-0.24+k*0.16, cy-0.24, cz+1.00), 0.02, 0.03, COL_ACCENT, axis='Y')
    make_box(f"{prefix}_LED", (cx+0.30, cy-0.24, cz+0.92), (0.03,0.02,0.03), (0.96,0.32,0.24,1.0))

def build_amps():
    _make_amp_stack("AmpL", -1.9, 4.6)
    _make_amp_stack("AmpR", 1.9, 4.6)

def _make_mic_stand(prefix, cx, cy):
    cz = STAGE_TOP
    make_cyl(f"{prefix}_Base", (cx, cy, cz+0.02), 0.16, 0.04, P.METAL_BLACK, segments=12)
    make_cyl(f"{prefix}_Pole", (cx, cy, cz+0.72), 0.02, 1.40, P.METAL_STEEL)
    make_box(f"{prefix}_Boom", (cx, cy-0.18, cz+1.40), (0.03, 0.40, 0.03), P.METAL_STEEL)
    make_cyl(f"{prefix}_Mic", (cx, cy-0.36, cz+1.40), 0.03, 0.11, P.METAL_BLACK, axis='Y')

def build_mics():
    _make_mic_stand("Mic0", -1.0, 3.65)
    _make_mic_stand("Mic1", 0.6, 3.60)

def build_monitors():
    for mi, mx in enumerate([-1.0, 0.8]):
        my, mz = 3.55, STAGE_TOP
        make_box(f"Monitor_{mi}_Body", (mx, my, mz+0.14), (0.44, 0.34, 0.28), (0.12,0.11,0.10,1.0))
        make_box(f"Monitor_{mi}_Face", (mx, my+0.14, mz+0.22), (0.36, 0.10, 0.20), (0.24,0.22,0.20,1.0))
        make_cyl(f"Monitor_{mi}_Cone", (mx, my+0.17, mz+0.22), 0.10, 0.03, (0.08,0.07,0.07,1.0), axis='Y', segments=12)

def build_pa():
    for si, sx in enumerate([-3.3, 3.3]):
        sy = 3.4
        make_box(f"PA_{si}_Sub", (sx, sy, 0.35), (0.60, 0.60, 0.70), (0.12,0.11,0.10,1.0))
        make_box(f"PA_{si}_Top", (sx, sy, 1.35), (0.52, 0.52, 1.20), (0.14,0.12,0.11,1.0))
        make_cyl(f"PA_{si}_Woofer", (sx, sy-0.27, 1.15), 0.20, 0.04, (0.08,0.07,0.07,1.0), axis='Y', segments=14)
        make_box(f"PA_{si}_Horn", (sx, sy-0.27, 1.65), (0.30, 0.04, 0.18), (0.20,0.18,0.16,1.0))
        make_box(f"PA_{si}_LED", (sx+0.20, sy-0.27, 0.35), (0.03,0.02,0.03), (0.30,0.86,0.36,1.0))

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))

def main():
    clear_scene()
    build_shell()
    build_posters()
    build_stage()
    build_drums()
    build_amps()
    build_mics()
    build_monitors()
    build_pa()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/foxhole_stage.glb"))
    print(f"\n[build_foxhole_stage] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
