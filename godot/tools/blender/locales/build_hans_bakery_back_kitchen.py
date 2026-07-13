"""hans_bakery_back_kitchen — vol5-7 bakery back-of-house kitchen.

Was well-lit but sparse (a counter, a deck oven, a speed rack, a prep
table, flour sacks, a bowl shelf; ~35 calls). Enriched to a working
bakery kitchen: a taller PROOFER cabinet beside the oven, a planetary
STAND MIXER, a rolling FLOUR BIN, a platform SCALE, a wire COOLING
RACK of loaves, a wall UTENSIL RAIL of hanging tools, a subway-TILE
backsplash band, and a PASS WINDOW to the front counter with a ticket
rail. Room: door/S wall at blender y=0, extends +Y; interior lands at
godot -Z. Props kept inside the 6.0 x 5.0 footprint.
"""
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

ROOM_W = 6.0; ROOM_D = 5.0; CEIL = 2.8
PAL_WALL = {"wall":(0.96,0.84,0.62,1.0),"baseboard":(0.62,0.42,0.22,1.0)}
COL_FLOOR = (0.62,0.46,0.30,1.0); COL_SEAM = (0.32,0.22,0.14,1.0); COL_WOOD = (0.42,0.30,0.18,1.0)
COL_ACCENT = (0.78,0.42,0.22,1.0)

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
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})

def build_tile():
    # White subway-tile backsplash band behind the north work wall +
    # a tiled wainscot along the east wall, with darker grout seams.
    tile = (0.90, 0.90, 0.86, 1.0); grout = (0.66, 0.64, 0.58, 1.0)
    make_box("Backsplash_N", (0.0, ROOM_D-0.11, 1.35), (ROOM_W-0.4, 0.02, 0.90), tile)
    for gi in range(6):
        make_box(f"Grout_N_H_{gi}", (0.0, ROOM_D-0.10, 0.95+gi*0.15), (ROOM_W-0.4, 0.005, 0.01), grout)
    for gi in range(11):
        make_box(f"Grout_N_V_{gi}", (-2.6+gi*0.52, ROOM_D-0.10, 1.35), (0.01, 0.005, 0.90), grout)
    make_box("Wainscot_E", (ROOM_W/2.0-0.11, ROOM_D/2.0, 0.70), (0.02, ROOM_D-0.4, 1.20), tile)

def build_counter():
    top_z = make_counter("Counter", (-ROOM_W/4.0, ROOM_D-1.0, 0.0), length=2.40, depth=0.70, height=0.92,
                         palette={"formica": (0.78, 0.66, 0.42, 1.0), "top": (0.32, 0.22, 0.14, 1.0), "kick": (0.32, 0.22, 0.14, 1.0)})
    make_counter_bullnose("Counter", (-ROOM_W/4.0-0.35, ROOM_D-1.0, top_z), length=2.40)

def build_stove():
    # Commercial deck oven: stainless body, two glass doors with warm
    # interiors + bar handles, a vent hood above.
    sx, sy = +ROOM_W/4.0, ROOM_D-1.0
    make_box("Oven_Body", (sx, sy, 0.75), (1.00, 0.80, 1.50), (0.80, 0.82, 0.86, 1.0))
    for di, dz in enumerate([0.55, 1.05]):
        make_box(f"Oven_Door_{di}", (sx-0.42, sy, dz), (0.06, 0.66, 0.40), (0.28, 0.24, 0.22, 1.0))
        make_box(f"Oven_Window_{di}", (sx-0.46, sy, dz), (0.02, 0.46, 0.24), (1.0, 0.62, 0.26, 0.8))
        make_cyl(f"Oven_Handle_{di}", (sx-0.50, sy, dz-0.24), 0.02, 0.60, P.METAL_STEEL, axis='Y', segments=8)
    make_box("Oven_Hood", (sx, sy, 1.70), (1.10, 0.90, 0.30), P.METAL_STEEL)

def build_bakery():
    """Back-of-house bakery: a rolling speed rack of sheet trays + loaves,
    a flour-dusted prep table with dough balls + a rolling pin, stacked
    flour sacks, and a wall shelf of mixing bowls."""
    # Speed rack (rolling tray rack) near the centre
    rx, ry = -0.3, ROOM_D/2.0 - 0.3
    make_box("Rack_Frame", (rx, ry, 0.90), (0.70, 0.60, 1.80), P.METAL_STEEL)
    for ti, tz in enumerate([0.4, 0.7, 1.0, 1.3, 1.6]):
        make_box(f"Rack_Tray_{ti}", (rx, ry, tz), (0.64, 0.54, 0.03), (0.72, 0.72, 0.74, 1.0))
        for li in range(3):
            make_cyl(f"Rack_Loaf_{ti}_{li}", (rx-0.2+li*0.2, ry, tz+0.06), 0.06, 0.26, (0.72, 0.52, 0.30, 1.0), axis='X', segments=8)
    for wi, wx in enumerate([-0.36, 0.36]):
        make_cyl(f"Rack_Wheel_{wi}", (rx+wx, ry, 0.04), 0.05, 0.05, P.METAL_BLACK, axis='X', segments=8)
    # Flour-dusted prep table with dough balls + rolling pin
    tx, ty = -ROOM_W/4.0, ROOM_D/2.0 - 0.8
    make_box("Prep_Top", (tx, ty, 0.90), (1.20, 0.70, 0.06), (0.86, 0.84, 0.80, 1.0))
    for i, (lx, ly) in enumerate([(-0.54, -0.3), (0.54, -0.3), (-0.54, 0.3), (0.54, 0.3)]):
        make_box(f"Prep_Leg_{i}", (tx+lx, ty+ly, 0.45), (0.06, 0.06, 0.90), P.METAL_STEEL)
    for di in range(4):
        make_cyl(f"Dough_{di}", (tx-0.35+di*0.24, ty-0.1, 0.96), 0.07, 0.08, (0.90, 0.86, 0.74, 1.0), segments=10)
    make_cyl("RollingPin", (tx+0.2, ty+0.22, 0.95), 0.04, 0.44, COL_WOOD, axis='X', segments=8)
    # Stacked flour sacks in the SW corner
    for si, (sx2, sz) in enumerate([(-ROOM_W/2.0+0.6, 0.22), (-ROOM_W/2.0+0.55, 0.62), (-ROOM_W/2.0+0.85, 0.22)]):
        make_box(f"FlourSack_{si}", (sx2, 0.7, sz), (0.34, 0.30, 0.42), (0.88, 0.84, 0.76, 1.0))
    # Wall shelf of mixing bowls, west wall
    make_box("BowlShelf", (-ROOM_W/2.0+0.14, ROOM_D-1.4, 1.7), (0.10, 1.20, 0.06), COL_WOOD)
    for bi in range(3):
        make_cyl(f"Bowl_{bi}", (-ROOM_W/2.0+0.30, ROOM_D-1.9+bi*0.5, 1.80), 0.14, 0.16, P.METAL_STEEL, segments=12)

def build_proofer():
    # Roll-in proofing cabinet on casters, east of the oven: stainless
    # body, a full glass door showing racked trays, a warm proof glow.
    px, py = ROOM_W/2.0 - 0.55, ROOM_D - 1.4
    make_box("Proofer_Body", (px, py, 1.00), (0.66, 0.80, 1.90), (0.78, 0.80, 0.84, 1.0))
    make_box("Proofer_Door", (px-0.30, py, 1.05), (0.06, 0.66, 1.60), (0.30, 0.30, 0.32, 1.0))
    make_box("Proofer_Glass", (px-0.34, py, 1.05), (0.02, 0.54, 1.44), (0.72, 0.82, 0.86, 0.4))
    make_cyl("Proofer_Handle", (px-0.38, py+0.24, 1.05), 0.02, 0.70, P.METAL_STEEL, axis='Z', segments=8)
    for ti, tz in enumerate([0.55, 0.85, 1.15, 1.45, 1.75]):
        make_box(f"Proofer_Tray_{ti}", (px-0.02, py, tz), (0.56, 0.60, 0.03), (0.72, 0.72, 0.74, 1.0))
        make_box(f"Proofer_Glow_{ti}", (px-0.30, py, tz), (0.02, 0.50, 0.10), (1.0, 0.78, 0.42, 0.7))
    for wi, wo in enumerate([-0.26, 0.26]):
        make_cyl(f"Proofer_Wheel_{wi}", (px+wo, py, 0.05), 0.05, 0.05, P.METAL_BLACK, axis='X', segments=8)

def build_equipment():
    # Planetary stand mixer on the north counter's west end.
    mx, my = -ROOM_W/4.0-0.9, ROOM_D-1.0
    top = 0.96
    make_box("Mixer_Base", (mx, my, top+0.06), (0.28, 0.34, 0.12), (0.86, 0.84, 0.82, 1.0))
    make_box("Mixer_Column", (mx+0.10, my, top+0.34), (0.14, 0.24, 0.44), (0.86, 0.84, 0.82, 1.0))
    make_box("Mixer_Head", (mx-0.06, my, top+0.52), (0.34, 0.22, 0.16), (0.86, 0.84, 0.82, 1.0))
    make_cyl("Mixer_Whisk", (mx-0.10, my, top+0.30), 0.05, 0.20, P.METAL_STEEL, segments=8)
    make_cyl("Mixer_Bowl", (mx-0.10, my, top+0.14), 0.13, 0.18, P.METAL_STEEL, segments=12)
    # Rolling flour ingredient bin in the SW.
    fx, fy = -ROOM_W/2.0+0.55, ROOM_D/2.0+0.5
    make_box("FlourBin_Body", (fx, fy, 0.40), (0.50, 0.60, 0.72), (0.72, 0.60, 0.42, 1.0))
    make_box("FlourBin_Lid", (fx, fy, 0.78), (0.52, 0.62, 0.06), (0.56, 0.46, 0.32, 1.0))
    make_cyl("FlourBin_Scoop", (fx, fy-0.10, 0.86), 0.05, 0.14, P.METAL_STEEL, segments=8)
    for wi, wo in enumerate([-0.20, 0.20]):
        make_cyl(f"FlourBin_Wheel_{wi}", (fx+wo, fy, 0.05), 0.05, 0.05, P.METAL_BLACK, axis='X', segments=8)
    # Platform baker's scale on the prep table's edge.
    sx, sy = -ROOM_W/4.0+0.5, ROOM_D/2.0-0.9
    make_box("Scale_Base", (sx, sy, 0.98), (0.24, 0.24, 0.06), (0.30, 0.30, 0.32, 1.0))
    make_box("Scale_Platform", (sx, sy, 1.04), (0.20, 0.20, 0.02), P.METAL_STEEL)
    make_box("Scale_Column", (sx+0.09, sy, 1.14), (0.03, 0.03, 0.18), (0.30, 0.30, 0.32, 1.0))
    make_cyl("Scale_Dial", (sx+0.09, sy, 1.26), 0.07, 0.03, (0.94, 0.92, 0.86, 1.0), axis='Y', segments=12)

def build_cooling_rack():
    # Wire cooling rack of finished loaves, center-east floor.
    rx, ry = 0.9, ROOM_D/2.0 - 0.9
    make_box("Cool_Frame", (rx, ry, 0.85), (0.66, 0.50, 1.70), P.METAL_STEEL)
    for si, sz in enumerate([0.5, 0.85, 1.2, 1.55]):
        make_box(f"Cool_Shelf_{si}", (rx, ry, sz), (0.62, 0.46, 0.02), P.METAL_STEEL)
        for li in range(3):
            make_cyl(f"Cool_Loaf_{si}_{li}", (rx-0.18+li*0.18, ry, sz+0.07), 0.05, 0.24,
                     (0.74, 0.52, 0.30, 1.0), axis='Y', segments=8)
    for wi, wo in enumerate([-0.28, 0.28]):
        make_cyl(f"Cool_Wheel_{wi}", (rx+wo, ry, 0.04), 0.04, 0.05, P.METAL_BLACK, axis='X', segments=8)

def build_utensil_rail():
    # Wall rail of hanging tools above the north counter.
    rx0, rx1 = -ROOM_W/4.0-1.0, -ROOM_W/4.0+1.0
    ry = ROOM_D - 0.14
    make_box("Rail", ((rx0+rx1)/2.0, ry, 1.85), (rx1-rx0, 0.03, 0.03), P.METAL_STEEL)
    tools = [("Whisk", 0.10, 0.22, P.METAL_STEEL), ("Spatula", 0.05, 0.26, (0.42,0.30,0.18,1.0)),
             ("Scraper", 0.08, 0.20, (0.30,0.42,0.52,1.0)), ("Ladle", 0.07, 0.24, P.METAL_STEEL),
             ("Brush", 0.05, 0.22, (0.62,0.46,0.30,1.0)), ("Sieve", 0.10, 0.18, P.METAL_STEEL)]
    n = len(tools)
    for i, (nm, w, h, col) in enumerate(tools):
        tx = rx0 + (i+0.5)*(rx1-rx0)/n
        make_cyl(f"RailHook_{i}", (tx, ry-0.02, 1.80), 0.006, 0.06, P.METAL_STEEL)
        make_box(f"Tool_{nm}", (tx, ry-0.04, 1.80-h/2.0), (w, 0.03, h), col)

def build_pass_window():
    # Pass-through to the front counter, cut in the SE south-wall
    # segment, with a ticket rail + a tray of finished pastries on the
    # sill (handed to the front of house).
    wx = ROOM_W/4.0 + 0.5
    make_box("Pass_SillFrame", (wx, 0.10, 1.05), (1.30, 0.10, 0.10), P.METAL_STEEL)
    make_box("Pass_TopFrame", (wx, 0.10, 1.85), (1.30, 0.10, 0.10), P.METAL_STEEL)
    for so in (-0.65, 0.65):
        make_box(f"Pass_SideFrame_{'L' if so<0 else 'R'}", (wx+so, 0.10, 1.45), (0.08, 0.10, 0.90), P.METAL_STEEL)
    make_box("Pass_Sill", (wx, 0.22, 1.12), (1.20, 0.30, 0.06), (0.72, 0.72, 0.74, 1.0))
    # Ticket rail with a few order chits
    make_box("Pass_TicketRail", (wx, 0.16, 1.78), (1.10, 0.03, 0.03), P.METAL_STEEL)
    for ti in range(4):
        make_box(f"Pass_Ticket_{ti}", (wx-0.5+ti*0.32, 0.18, 1.66), (0.14, 0.005, 0.20), P.PAPER)
    # A tray of finished pastries on the sill
    make_box("Pass_Tray", (wx, 0.30, 1.16), (0.80, 0.24, 0.02), (0.72, 0.72, 0.74, 1.0))
    for pi in range(4):
        make_cyl(f"Pass_Pastry_{pi}", (wx-0.28+pi*0.19, 0.30, 1.20), 0.05, 0.06,
                 (0.86, 0.64, 0.34, 1.0), segments=8)

def build_decor():
    make_calendar("Calendar", (-ROOM_W/2.0+0.13, 1.4, 1.70))
    make_faded_poster("Poster_E", (ROOM_W/2.0-0.05, 1.6, 1.60))
    make_floor_plant("Plant", (-ROOM_W/2.0+0.5, ROOM_D-0.6, 0.0))

def build_clock():
    make_wall_clock("Clock", (0.0, ROOM_D-0.05, CEIL-0.50), frozen_hour=8, frozen_min=15)

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))

def main():
    clear_scene()
    build_shell()
    build_tile()
    build_counter()
    build_stove()
    build_proofer()
    build_bakery()
    build_equipment()
    build_cooling_rack()
    build_utensil_rail()
    build_pass_window()
    build_decor()
    build_clock()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/hans_bakery_back_kitchen.glb"))
    print(f"\n[build_hans_bakery_back_kitchen] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
