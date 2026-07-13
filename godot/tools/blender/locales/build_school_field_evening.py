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


def build_hashmarks():
    # Two inboard rows of short hash marks — one per yard, at 1/3 and 2/3
    # width — the detail that makes turf read as a real gridiron.
    for hx in [-(FIELD_W/2.0)*0.30, +(FIELD_W/2.0)*0.30]:
        for i in range(13):
            make_box(f"Hash_{'L' if hx < 0 else 'R'}_{i}", (hx, 0.6+i*1.05, 0.0015),
                     (0.30, 0.06, 0.02), COL_LINE)
    # End-zone corner pylons (soft orange foam markers)
    for cx, cy in [(-(FIELD_W/2.0-1.0), 0.6), (+(FIELD_W/2.0-1.0), 0.6),
                   (-(FIELD_W/2.0-1.0), FIELD_D-0.6), (+(FIELD_W/2.0-1.0), FIELD_D-0.6)]:
        make_box(f"Pylon_{cx:.0f}_{cy:.0f}", (cx, cy, 0.14), (0.10, 0.10, 0.28), (0.94, 0.44, 0.16, 1.0))
    # A football teed up near midfield
    make_cyl("Tee", (0.0, FIELD_D/2.0, 0.03), 0.06, 0.06, (0.92, 0.72, 0.20, 1.0), segments=10)
    make_cyl("Ball", (0.0, FIELD_D/2.0, 0.14), 0.055, 0.20, (0.42, 0.24, 0.14, 1.0), axis='X', segments=8)


def build_bleachers():
    # Stepped aluminium stands along the west sideline, facing the field
    bx = -(FIELD_W/2.0 + 1.2)
    for step in range(9):
        h = 0.4 + step*0.42
        make_box(f"Bleach_Riser_{step}", (bx - step*0.55, FIELD_D/2.0, h*0.5), (0.55, 8.0, h), COL_METAL)
        make_box(f"Bleach_Bench_{step}", (bx - step*0.55, FIELD_D/2.0, h+0.05), (0.50, 8.0, 0.06), (0.44, 0.36, 0.26, 1.0))
    # Vertical support legs + a hand rail up the near aisle
    for ly in [FIELD_D/2.0-3.6, FIELD_D/2.0+3.6]:
        make_box(f"Bleach_Leg_{ly:.0f}", (bx-2.4, ly, 1.7), (5.0, 0.10, 0.10), COL_METAL)
    # End rails
    for ry in [FIELD_D/2.0-4.0, FIELD_D/2.0+4.0]:
        make_box(f"Bleach_Rail_{ry:.0f}", (bx-1.6, ry, 1.5), (3.4, 0.06, 0.06), COL_METAL)


def build_spectators():
    # A scattering of seated silhouettes on the stands (torso + head),
    # muted dusk-crowd colours — suggests a Friday-night crowd.
    bx = -(FIELD_W/2.0 + 1.2)
    coats = [(0.42,0.30,0.34,1.0),(0.30,0.36,0.44,1.0),(0.46,0.42,0.30,1.0),
             (0.36,0.44,0.38,1.0),(0.52,0.40,0.36,1.0),(0.34,0.34,0.40,1.0)]
    skin = (0.62, 0.48, 0.40, 1.0)
    seats = [(2,-3.2),(2,-1.0),(3,1.4),(4,-2.2),(4,2.6),(5,0.2),(6,-1.6),(6,3.0),(7,1.0)]
    for si, (step, yo) in enumerate(seats):
        h = 0.4 + step*0.42
        seat_top = h + 0.08
        px = bx - step*0.55
        py = FIELD_D/2.0 + yo
        col = coats[si % len(coats)]
        make_box(f"Fan_{si}_Torso", (px, py, seat_top+0.24), (0.34, 0.34, 0.46), col)
        make_cyl(f"Fan_{si}_Head", (px, py, seat_top+0.58), 0.10, 0.16, skin, segments=8)


def build_benches():
    # Team sideline area on the EAST side (opposite the stands): two
    # players' benches, water coolers, and a ball/helmet rack.
    ex = +(FIELD_W/2.0 + 1.0)
    for bi, by in enumerate([FIELD_D/2.0-3.0, FIELD_D/2.0+3.0]):
        col = (0.30, 0.36, 0.52, 1.0) if bi == 0 else (0.52, 0.30, 0.30, 1.0)
        make_box(f"Bench_{bi}_Seat", (ex, by, 0.46), (0.50, 4.4, 0.08), (0.42, 0.34, 0.26, 1.0))
        make_box(f"Bench_{bi}_Back", (ex+0.24, by, 0.70), (0.06, 4.4, 0.40), col)
        for lo in (-2.0, 2.0):
            make_box(f"Bench_{bi}_Leg_{'S' if lo<0 else 'N'}", (ex, by+lo, 0.22), (0.46, 0.08, 0.44), COL_METAL)
    # Two orange water coolers with white lids + spigots
    for wi, wy in enumerate([FIELD_D/2.0-5.4, FIELD_D/2.0+5.4]):
        make_cyl(f"Cooler_{wi}_Body", (ex, wy, 0.34), 0.24, 0.60, (0.92, 0.48, 0.18, 1.0), segments=12)
        make_cyl(f"Cooler_{wi}_Lid", (ex, wy, 0.66), 0.25, 0.06, (0.92, 0.90, 0.86, 1.0), segments=12)
        make_box(f"Cooler_{wi}_Spigot", (ex-0.26, wy, 0.24), (0.06, 0.05, 0.05), P.METAL_BLACK)
    # Ball / helmet rack behind the benches
    rx = ex + 0.9
    make_box("Rack_Bar_T", (rx, FIELD_D/2.0, 1.10), (0.06, 3.0, 0.06), COL_METAL)
    make_box("Rack_Bar_B", (rx, FIELD_D/2.0, 0.60), (0.06, 3.0, 0.06), COL_METAL)
    for hi in range(5):
        hy = FIELD_D/2.0 - 1.2 + hi*0.6
        make_cyl(f"Rack_Helmet_{hi}", (rx, hy, 0.84), 0.11, 0.14, (0.30, 0.36, 0.52, 1.0), axis='Y', segments=10)


def build_scoreboard():
    # Freestanding scoreboard beyond the far (north) end.
    sx, sy = 0.0, FIELD_D + 3.2
    for po in (-2.2, 2.2):
        make_cyl(f"Score_Post_{'L' if po<0 else 'R'}", (sx+po, sy, 2.4), 0.12, 4.8, COL_POLE, segments=8)
    make_box("Score_Panel", (sx, sy, 5.0), (5.2, 0.30, 2.6), (0.10, 0.12, 0.16, 1.0))
    make_box("Score_Header", (sx, sy-0.16, 6.1), (5.4, 0.10, 0.6), (0.30, 0.36, 0.52, 1.0))
    # HOME / GUEST score blocks + clock + quarter — amber LED digits
    amber = (0.98, 0.66, 0.18, 1.0)
    labels = [(-1.6, 5.4), (+1.6, 5.4)]   # HOME / GUEST scores
    for li, (lx, lz) in enumerate(labels):
        make_box(f"Score_LabelBG_{li}", (sx+lx, sy-0.16, lz+0.7), (1.4, 0.06, 0.34), (0.62,0.66,0.72,1.0))
        for di in range(2):
            make_box(f"Score_Digit_{li}_{di}", (sx+lx-0.4+di*0.8, sy-0.18, lz), (0.5, 0.05, 0.8), amber)
    # Game clock (centre) + quarter box
    for di in range(4):
        make_box(f"Score_Clock_{di}", (sx-0.9+di*0.6, sy-0.18, 4.3), (0.34, 0.05, 0.5), amber)
    make_box("Score_QtrBox", (sx, sy-0.18, 3.5), (0.5, 0.05, 0.5), (0.94, 0.30, 0.22, 1.0))


def build_first_down_chain():
    # Chain crew on the near sideline (east side, south of midfield):
    # two down markers connected by a segmented chain, plus a numbered
    # down box.
    cx = +(FIELD_W/2.0 - 0.6)
    y0, y1 = 3.2, 6.4
    for pi, py in enumerate([y0, y1]):
        make_cyl(f"Chain_Pole_{pi}", (cx, py, 0.9, ), 0.03, 1.8, COL_METAL, segments=6)
        make_box(f"Chain_Cap_{pi}", (cx, py, 1.9), (0.14, 0.14, 0.20), (0.94, 0.62, 0.16, 1.0))
    # Segmented chain link between the two poles (short alternating boxes)
    links = 10
    for li in range(links):
        ly = y0 + (li+0.5)*(y1-y0)/links
        make_box(f"Chain_Link_{li}", (cx, ly, 0.16), (0.03, (y1-y0)/links*0.6, 0.03), P.METAL_STEEL)
    # Numbered DOWN box on its own pole a little inboard
    dx = cx - 0.5
    make_cyl("Down_Pole", (dx, y0-1.4, 1.0), 0.03, 2.0, COL_METAL, segments=6)
    make_box("Down_Box", (dx, y0-1.4, 2.1), (0.40, 0.10, 0.40), (0.94, 0.82, 0.28, 1.0))
    make_box("Down_Num", (dx-0.06, y0-1.4, 2.1), (0.005, 0.20, 0.24), P.METAL_BLACK)


def build_banners():
    # Booster / sponsor banners zip-tied to the far chain-link fence.
    cols = [(0.52, 0.20, 0.22, 1.0), (0.20, 0.34, 0.52, 1.0), (0.24, 0.42, 0.30, 1.0),
            (0.58, 0.46, 0.20, 1.0)]
    for bi in range(4):
        bxc = -FIELD_W/2.0 + 2.5 + bi*4.6
        make_box(f"Banner_{bi}", (bxc, FIELD_D+0.55, 0.85), (3.6, 0.04, 0.70), cols[bi % len(cols)])
        make_box(f"Banner_{bi}_Text", (bxc, FIELD_D+0.52, 0.85), (2.6, 0.02, 0.24), (0.92, 0.90, 0.84, 1.0))


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
    build_hashmarks()
    build_bleachers()
    build_spectators()
    build_benches()
    build_scoreboard()
    build_first_down_chain()
    build_goalposts()
    build_floodlights()
    build_fence()
    build_banners()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/school_field_evening.glb"))
    print(f"\n[build_school_field_evening] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
