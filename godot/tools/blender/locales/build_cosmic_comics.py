"""VOL 6 · Cosmic Comics — Rick Cosmic's back-issue shop.

PLACEMENT SCRIPT (uses _props/* library, no embedded prop factory)

A demonstration of the library pattern. Compare line count to
build_kwik_stop.py — most of the geometry is now in shared modules,
this script just calls them with specific anchors + palettes.

Footprint:
  Interior X ∈ [-5, +5], Y ∈ [0, +8], ceiling Z=2.80
  Door at south centre (Y=0)
  Long-box bin shelves running E-W in middle
  Back-issue browse boxes along walls
  Register counter at NE corner (X=+4, Y=+6)
  CRT TV + VCR playing 1980s comic-store loop near register
  Faded movie posters on west wall

Run:
    blender --background --python build_cosmic_comics.py

Output:
    godot/assets/3d/locales/cosmic_comics.glb
"""
import os
import sys

# Ensure the parent tools/blender/ dir is on sys.path so _props
# imports work both when invoked directly and via run_cathedral.sh
_BLENDER_TOOLS = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BLENDER_TOOLS not in sys.path:
    sys.path.insert(0, _BLENDER_TOOLS)

from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import (
    make_floor, make_wall, make_ceiling, make_window,
    make_crown_molding, make_door_hinges,
)
from _props.store_fixtures import (
    make_counter, make_counter_bullnose, make_register,
    make_credit_card_terminal,
)
from _props.decor import (
    make_wall_clock, make_payphone, make_faded_poster, make_floor_plant,
)
from _props.safety import (
    make_security_camera, make_smoke_detector, make_sprinkler,
    make_hvac_vent, make_fluorescent_tube_fixture, make_ceiling_speaker,
)


# ── Cosmic Comics palette overrides ────────────────────────────
# Rick Cosmic is a back-issue purist — incandescent shop-lamps,
# wood-stain counter (NOT formica), purple comic-rack accents.
# Override the default warm-sunset neutrals where the canon look
# diverges from kwik stop's.
PAL_COUNTER = {
    "formica": (0.46, 0.32, 0.20, 1.0),    # wood-stain counter
    "top":     (0.32, 0.22, 0.14, 1.0),
    "kick":    (0.20, 0.14, 0.08, 1.0),
}
PAL_PURPLE_ACCENT = (0.42, 0.30, 0.52, 1.0)  # comic-rack purple
PAL_COSMIC_BLUE = (0.20, 0.30, 0.46, 1.0)

# Footprint constants (interior bounds)
ROOM_W = 10.0   # X range
ROOM_D = 8.0    # Y range
CEIL_Z = 2.80


# ════════════════════════════════════════════════════════════════
# SHELL
# ════════════════════════════════════════════════════════════════
def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0),
               size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4)
    # Walls
    make_wall("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0),
              length=ROOM_D + 0.4, height=CEIL_Z, axis='Y',
              baseboard_face_sign=+1)
    make_wall("Wall_E", (+ROOM_W / 2.0, ROOM_D / 2.0, 0),
              length=ROOM_D + 0.4, height=CEIL_Z, axis='Y',
              baseboard_face_sign=-1)
    make_wall("Wall_N", (0.0, ROOM_D, 0),
              length=ROOM_W + 0.4, height=CEIL_Z, axis='X',
              baseboard_face_sign=-1)
    # South wall split around door (door at X∈[-1.5, 1.5])
    make_wall("Wall_S_W", (-3.25, 0.0, 0),
              length=3.50, height=CEIL_Z, axis='X')
    make_wall("Wall_S_E", (+3.25, 0.0, 0),
              length=3.50, height=CEIL_Z, axis='X')
    # Door header
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL_Z - 0.30),
             (3.20, 0.20, 0.60), P.WALL_CREAM)
    # Ceiling
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL_Z),
                 size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4)
    # Crown molding
    for nm, anchor, axis, length in [
            ("Crown_W", (-ROOM_W / 2.0 + 0.10, ROOM_D / 2.0, 0), 'Y', ROOM_D),
            ("Crown_E", (+ROOM_W / 2.0 - 0.10, ROOM_D / 2.0, 0), 'Y', ROOM_D),
            ("Crown_N", (0.0, ROOM_D - 0.10, 0), 'X', ROOM_W),
            ("Crown_S", (0.0, +0.10, 0), 'X', ROOM_W)]:
        make_crown_molding(nm, wall_x=anchor[0], wall_y=anchor[1],
                           length=length, axis=axis, ceil_z=CEIL_Z)
    # Front window (south, west side of door)
    make_window("Window_SW", (-3.20, 0.0, 1.40),
                width=2.40, height=1.40)
    make_window("Window_SE", (+3.20, 0.0, 1.40),
                width=2.40, height=1.40)
    # Door hinges
    make_door_hinges("FrontDoor_Hinge", edge_x=-1.50, edge_y=0.0,
                     edge_z_centers=[0.30, 1.05, 1.80], axis='X')


# ════════════════════════════════════════════════════════════════
# COUNTER + REGISTER (NE corner)
# ════════════════════════════════════════════════════════════════
def build_counter_setup():
    cx, cy = 4.0, 6.0
    top_z = make_counter("Counter", (cx, cy, 0.0),
                         length=3.20, depth=1.00, height=1.00,
                         palette=PAL_COUNTER)
    make_counter_bullnose("Counter", (cx - 0.50, cy, top_z),
                          length=3.20, palette=PAL_COUNTER)
    make_register("Register", (cx, cy - 0.60, top_z),
                  palette={"screen": (0.46, 0.32, 0.62, 1.0)})  # purple LCD
    make_credit_card_terminal("CCTerm", (cx, cy + 0.40, top_z))
    # Long-boxes of back-issues stacked behind counter
    for li in range(4):
        make_box(f"LongBox_{li}",
                 (cx + 0.50, cy + (li - 1.5) * 0.32, 0.16 + (li % 2) * 0.20),
                 (0.40, 0.30, 0.20), P.PAPER_AGED)


# ════════════════════════════════════════════════════════════════
# BROWSE BINS — long-box rows running E-W down the middle
# ════════════════════════════════════════════════════════════════
def build_browse_bins():
    for j, ay in enumerate([3.0, 4.5]):
        # Long base
        make_box(f"Bin_{j}_Base", (0.0, ay, 0.30),
                 (5.0, 0.50, 0.60), P.COUNTER_DARK)
        # Vertical dividers every 50cm
        for di in range(11):
            dx = -2.50 + di * 0.50
            make_box(f"Bin_{j}_Div_{di}",
                     (dx, ay, 0.66),
                     (0.02, 0.50, 0.12), P.METAL_STEEL)
        # Comic covers (boxes of varied tints peeking out)
        from _props.palette import SNACK_TINTS
        for ci in range(20):
            cx_pos = -2.40 + (ci % 10) * 0.50
            cy_off = -0.20 + (ci // 10) * 0.40
            make_box(f"Bin_{j}_Comic_{ci}",
                     (cx_pos, ay + cy_off, 0.70),
                     (0.40, 0.04, 0.20),
                     SNACK_TINTS[(j + ci) % len(SNACK_TINTS)])


# ════════════════════════════════════════════════════════════════
# WALL FIXTURES + DECOR
# ════════════════════════════════════════════════════════════════
def build_decor():
    # Wall clock above the counter
    make_wall_clock("Clock", (4.0, 7.80, 2.10),
                    frozen_hour=4, frozen_min=22)
    # Faded movie posters on west wall (3)
    for pi, py in enumerate([2.5, 5.0, 7.0]):
        make_faded_poster(f"Poster_W_{pi}", (-4.90, py, 1.70))
    # Payphone east wall by door
    make_payphone("Payphone", (4.85, 1.40, 1.30))
    # Comic-shop staple: floor plant near door
    make_floor_plant("Plant", (-3.80, 1.20, 0.0))
    # Saturated purple comic-rack accent piece (signature canon)
    make_box("ComicRack_Accent",
             (-4.80, 5.20, 1.40),
             (0.10, 1.40, 1.60), PAL_PURPLE_ACCENT)


# ════════════════════════════════════════════════════════════════
# CEILING INFRA
# ════════════════════════════════════════════════════════════════
def build_ceiling_infra():
    # Two rows of fluorescent fixtures
    for j, ypos in enumerate([2.5, 5.5]):
        for i in range(-1, 2):
            make_fluorescent_tube_fixture(
                f"Fluor_{j}_{i}", (i * 2.4, ypos, CEIL_Z))
    # Security camera over counter
    make_security_camera("Cam_Counter", (3.5, 5.5, CEIL_Z))
    # Smoke detector + sprinklers
    make_smoke_detector("Smoke_Mid", (0.0, 4.0, CEIL_Z))
    for sx, sy in [(-2.0, 2.5), (+2.0, 2.5), (-2.0, 6.0), (+2.0, 6.0)]:
        make_sprinkler(f"Spr_{sx:+.0f}_{sy:+.0f}",
                       (sx, sy, CEIL_Z))
    make_hvac_vent("HVAC", (-1.0, 7.0, CEIL_Z))
    make_ceiling_speaker("Speaker", (1.5, 4.5, CEIL_Z))


# ════════════════════════════════════════════════════════════════
# EXPORT
# ════════════════════════════════════════════════════════════════
def main():
    clear_scene()
    build_shell()
    build_counter_setup()
    build_browse_bins()
    build_decor()
    build_ceiling_infra()

    out_path = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/cosmic_comics.glb"))
    print(f"\n[build_cosmic_comics] exporting to {out_path}")
    export_glb(out_path)


if __name__ == "__main__":
    main()
