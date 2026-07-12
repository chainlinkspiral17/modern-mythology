"""school_field_evening — vol6 EXTERIOR: the school football/practice
field at dusk. Friday-night-lights energy: open striped turf with yard
+ side lines, a set of bleachers, two goalposts, four floodlight poles
with lamp banks, and a low chain-link fence along the far end.

Was the generic room template (four walls + ceiling + fluorescent
tubes + a porch railing) — an indoor box labelled 'field evening'.
Rebuilt as an actual outdoor field; no room shell.

Coords: x = sideline-to-sideline, y = downfield (0 = near/south end),
z = up. The Background3D camera sits just off the south end looking
downfield."""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb

FIELD_W = 20.0   # x extent (a partial width of the field)
FIELD_D = 14.0   # y extent (toward the far end zone)
COL_TURF  = (0.18, 0.32, 0.16, 1.0)
COL_TURF2 = (0.22, 0.38, 0.20, 1.0)   # alternate mow stripe
COL_LINE  = (0.86, 0.88, 0.82, 1.0)
COL_METAL = (0.60, 0.62, 0.66, 1.0)
COL_POLE  = (0.28, 0.28, 0.30, 1.0)
COL_GOAL  = (0.94, 0.82, 0.28, 1.0)   # yellow uprights
COL_LAMP  = (1.0, 0.98, 0.90, 1.0)


def build_ground():
    # Turf in alternating mow-stripe bands running downfield
    bands = 7
    for i in range(bands):
        c = COL_TURF if i % 2 == 0 else COL_TURF2
        make_box(f"Turf_{i}", (0.0, i*(FIELD_D/bands)+(FIELD_D/bands)/2.0, -0.02),
                 (FIELD_W, FIELD_D/bands, 0.04), c)
    # Yard lines across the field
    for i in range(6):
        make_box(f"YardLine_{i}", (0.0, 1.2+i*2.4, 0.001), (FIELD_W-2.0, 0.10, 0.02), COL_LINE)
    # Sidelines
    for sx in [-(FIELD_W/2.0-1.0), +(FIELD_W/2.0-1.0)]:
        make_box(f"Sideline_{'L' if sx < 0 else 'R'}", (sx, FIELD_D/2.0, 0.001),
                 (0.12, FIELD_D, 0.02), COL_LINE)


def build_bleachers():
    # Stepped aluminium stands along the west sideline, facing the field
    bx = -(FIELD_W/2.0 + 1.2)
    for step in range(6):
        h = 0.4 + step*0.42
        make_box(f"Bleach_Riser_{step}", (bx - step*0.55, FIELD_D/2.0, h*0.5), (0.55, 8.0, h), COL_METAL)
        make_box(f"Bleach_Bench_{step}", (bx - step*0.55, FIELD_D/2.0, h+0.05), (0.50, 8.0, 0.06), (0.44, 0.36, 0.26, 1.0))
    # End rails
    for ry in [FIELD_D/2.0-4.0, FIELD_D/2.0+4.0]:
        make_box(f"Bleach_Rail_{ry:.0f}", (bx-1.6, ry, 1.5), (3.4, 0.06, 0.06), COL_METAL)


def build_goalposts():
    for gy in [1.2, FIELD_D-1.2]:
        tag = f"{gy:.0f}"
        make_cyl(f"Goal_{tag}_Post", (0.0, gy, 1.5), 0.07, 3.0, COL_GOAL, segments=8)
        make_box(f"Goal_{tag}_Cross", (0.0, gy, 3.0), (2.4, 0.07, 0.07), COL_GOAL)
        for ux in [-1.15, 1.15]:
            make_cyl(f"Goal_{tag}_Up_{'L' if ux < 0 else 'R'}", (ux, gy, 4.3), 0.05, 2.6, COL_GOAL, segments=8)


def build_floodlights():
    corners = [(-(FIELD_W/2.0-1.0), 0.5), (+(FIELD_W/2.0-1.0), 0.5),
               (-(FIELD_W/2.0-1.0), FIELD_D-0.5), (+(FIELD_W/2.0-1.0), FIELD_D-0.5)]
    for pi, (px, py) in enumerate(corners):
        make_cyl(f"Pole_{pi}", (px, py, 4.0), 0.10, 8.0, COL_POLE, segments=8)
        make_box(f"Bank_{pi}", (px, py, 7.8), (1.3, 0.30, 0.75), P.METAL_BLACK)
        for li in range(9):
            lx = -0.85 + (li % 3)*0.85
            lz = -0.24 + (li // 3)*0.42
            make_cyl(f"Lamp_{pi}_{li}", (px+lx, py-0.20, 7.8+lz), 0.10, 0.10, COL_LAMP, axis='Y', segments=8)


def build_fence():
    # Low chain-link along the far (north) end
    n = 20
    for i in range(n):
        fx = -FIELD_W/2.0 + i*(FIELD_W/(n-1))
        make_cyl(f"FencePost_{i}", (fx, FIELD_D+0.6, 0.6), 0.03, 1.2, COL_METAL, segments=6)
    make_box("FenceRail_Top", (0.0, FIELD_D+0.6, 1.15), (FIELD_W, 0.03, 0.04), COL_METAL)
    make_box("FenceRail_Mid", (0.0, FIELD_D+0.6, 0.60), (FIELD_W, 0.03, 0.04), COL_METAL)


def main():
    clear_scene()
    build_ground()
    build_bleachers()
    build_goalposts()
    build_floodlights()
    build_fence()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/school_field_evening.glb"))
    print(f"\n[build_school_field_evening] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
