"""VI · LOVERS — Roadside Chapel. Tiny limestone chapel on a raised
mound in the cane fields. Single altar, two short kneelers, statue
niche on the east wall, arched stained-glass window N, bell pull
in the SW corner. Stone-cool interior, votive-warm pools at the
altar — sanctuary on cursed ground.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster
from _props.safety import make_smoke_detector, make_sprinkler

PAL = {"wall": (0.84, 0.80, 0.72, 1.0), "baseboard": (0.62, 0.56, 0.46, 1.0)}
COL_FLOOR_STONE = (0.66, 0.60, 0.52, 1.0); COL_SEAM = (0.46, 0.40, 0.34, 1.0)
COL_ALTAR = (0.92, 0.88, 0.78, 1.0); COL_ALTAR_CLOTH = (0.88, 0.72, 0.32, 1.0)
COL_PEW_WOOD = (0.36, 0.24, 0.16, 1.0); COL_STAINED_R = (0.74, 0.22, 0.20, 0.65)
COL_STAINED_B = (0.20, 0.34, 0.62, 0.65); COL_STAINED_G = (0.30, 0.48, 0.34, 0.65)
COL_VOTIVE = (0.96, 0.62, 0.28, 1.0); COL_STATUE = (0.86, 0.84, 0.78, 1.0)
COL_BELL_BRONZE = (0.62, 0.46, 0.26, 1.0)

ROOM_W = 5.0; ROOM_D = 7.0; CEIL = 3.40


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR_STONE, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL, baseboard_face_sign=bb)
    make_wall("Wall_S", (0.0, 0.0, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=+1)
    make_wall("Wall_N_W", (-1.40, ROOM_D, 0), length=1.80, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_N_E", (+1.40, ROOM_D, 0), length=1.80, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=-1)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    # Crown moldings — limestone wash
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),
                                    ("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),
                                    ("Crown_S",'X',ROOM_W,0.0,+0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_BELL_BRONZE})


def build_stained_glass_window():
    # Tall arched window centered on the N wall (above altar). Three vertical panels.
    make_box("Window_Frame", (0.0, ROOM_D-0.04, 2.20), (1.60, 0.04, 1.40), COL_BELL_BRONZE)
    panels = [(-0.50, COL_STAINED_R), (0.0, COL_STAINED_B), (+0.50, COL_STAINED_G)]
    for i, (px, pc) in enumerate(panels):
        make_box(f"Stained_{i}", (px, ROOM_D-0.06, 2.20), (0.42, 0.005, 1.20), pc)
    # Arched top — three small half-discs
    for i, px in enumerate([-0.50, 0.0, +0.50]):
        make_cyl(f"Stained_Arch_{i}", (px, ROOM_D-0.06, 2.96), 0.21, 0.005,
                 (0.96, 0.84, 0.62, 0.65), axis='Y', segments=10)


def build_altar():
    ax, ay = 0.0, ROOM_D - 1.20
    make_box("Altar_Base", (ax, ay, 0.50), (1.30, 0.50, 1.00), COL_ALTAR)
    make_box("Altar_Top",  (ax, ay, 1.04), (1.40, 0.56, 0.04), COL_ALTAR)
    # Altar cloth front
    make_box("Altar_Cloth", (ax, ay-0.30, 0.50), (1.34, 0.005, 1.00), COL_ALTAR_CLOTH)
    # Candle pair + crucifix
    for sgn in (-1, +1):
        make_cyl(f"Altar_Candle_{sgn:+d}", (ax + sgn*0.40, ay, 1.18), 0.04, 0.24, P.PAPER)
        make_cyl(f"Altar_Candle_Flame_{sgn:+d}", (ax + sgn*0.40, ay, 1.34), 0.025, 0.04, COL_VOTIVE)
    make_box("Altar_Crucifix_V", (ax, ay, 1.40), (0.04, 0.04, 0.40), COL_PEW_WOOD)
    make_box("Altar_Crucifix_H", (ax, ay, 1.50), (0.20, 0.04, 0.04), COL_PEW_WOOD)
    # Votive rack to the right of the altar
    vx, vy = +1.40, ay - 0.20
    make_box("Votive_Rack", (vx, vy, 0.42), (0.30, 0.30, 0.10), COL_BELL_BRONZE)
    for i in range(6):
        cx = vx - 0.20 + (i % 3) * 0.20
        cy = vy - 0.10 + (i // 3) * 0.20
        make_cyl(f"Votive_{i}", (cx, cy, 0.50), 0.025, 0.06, COL_VOTIVE)
        make_cyl(f"Votive_Flame_{i}", (cx, cy, 0.58), 0.018, 0.03, COL_VOTIVE)


def build_pews():
    # Two short kneelers in the center, oriented to face the altar.
    for pi, py in enumerate([2.00, 3.80]):
        make_box(f"Pew_{pi}_Seat",   (0.0, py, 0.46), (2.20, 0.40, 0.06), COL_PEW_WOOD)
        make_box(f"Pew_{pi}_Back",   (0.0, py-0.20, 0.80), (2.20, 0.06, 0.68), COL_PEW_WOOD)
        make_box(f"Pew_{pi}_Kneeler", (0.0, py+0.32, 0.12), (2.20, 0.16, 0.06), COL_PEW_WOOD)
        for sgn in (-1, +1):
            make_box(f"Pew_{pi}_End_{sgn:+d}", (sgn*1.12, py, 0.46), (0.04, 0.40, 0.80), COL_PEW_WOOD)


def build_statue_niche():
    # Recessed niche on the E wall with a small Madonna figure.
    nx, ny = ROOM_W/2.0 - 0.14, 3.40
    make_box("Niche_Recess", (nx-0.04, ny, 1.80), (0.20, 0.80, 1.20), (0.78, 0.74, 0.66, 1.0))
    # Statue (stylised: pedestal + body + head)
    make_box("Statue_Pedestal", (nx-0.20, ny, 1.30), (0.16, 0.20, 0.10), COL_STATUE)
    make_cyl("Statue_Body", (nx-0.20, ny, 1.62), 0.10, 0.50, COL_STATUE, segments=10)
    make_cyl("Statue_Head", (nx-0.20, ny, 1.96), 0.07, 0.16, COL_STATUE, segments=10)


def build_bell_pull():
    # Rope dangling from ceiling in SW corner.
    bx, by = -ROOM_W/2.0 + 0.40, 0.60
    make_box("BellPull_Rope", (bx, by, 1.70), (0.04, 0.04, 1.60), COL_BELL_BRONZE)
    make_cyl("BellPull_Knot", (bx, by, 0.94), 0.08, 0.10, COL_BELL_BRONZE)


def build_ceiling_infra():
    make_smoke_detector("Smoke", (0.0, 3.5, CEIL))
    make_sprinkler("Spr", (0.0, 1.5, CEIL))
    # Hanging brass pendant over the altar
    make_cyl("Pendant_Cord", (0.0, ROOM_D-1.20, CEIL-0.40), 0.012, 0.80, P.METAL_BLACK)
    make_cyl("Pendant_Bowl", (0.0, ROOM_D-1.20, CEIL-0.96), 0.16, 0.08, COL_BELL_BRONZE)


def build_decor():
    make_wall_clock("Clock", (-ROOM_W/2.0+0.05, 5.5, 2.20), frozen_hour=4, frozen_min=15)
    make_floor_plant("Plant_SE", (ROOM_W/2.0-0.60, 0.60, 0.0), palette={"leaf": (0.42, 0.52, 0.36, 1.0)})
    make_faded_poster("Poster", (-ROOM_W/2.0+0.05, 1.8, 1.50))


def build_lovers_exterior():
    """Scene-description specifics from setup_sanctuary_on_cursed_ground:
    "The chapel sits on the only raised ground for half a mile of
    cane field." The interior was already covered by the existing
    builders — this adds the EXTERIOR that anchors the scenario:
    the raised mound under the chapel, a sparse cane-field around it
    on three sides, and a gravel access path from the south.
    """
    import random as _r
    _r.seed(17)
    # ── Raised mound under the chapel ──
    # Footprint extends ~3m beyond the interior on all sides
    mound_extent = 3.0
    mound_cx = 0.0
    mound_cy = ROOM_D / 2.0
    mound_w = ROOM_W + 0.4 + 2 * mound_extent
    mound_d = ROOM_D + 0.4 + 2 * mound_extent
    make_box("Exterior_Mound",
             (mound_cx, mound_cy, -0.30),
             (mound_w, mound_d, 0.60),
             (0.38, 0.30, 0.18, 1.0))   # mound dirt

    # ── Cane field surrounding the mound ──
    field_extent = 12.0
    field_w = mound_w + 2 * field_extent
    field_d = mound_d + 2 * field_extent
    make_box("Exterior_CaneField_Ground",
             (mound_cx, mound_cy, -1.10),
             (field_w, field_d, 0.10),
             (0.32, 0.46, 0.22, 1.0))   # green ground

    # ── Sparse cane stalks ──
    # 80 stalks placed randomly outside the mound. Each is a thin
    # vertical cylinder with a leaf clump on top. "The cane breathes"
    # is sold at runtime by wind shaders + lighting; the geometry
    # just needs to read as a cane field, not a lawn.
    stalk_count = 80
    placed = 0
    attempts = 0
    while placed < stalk_count and attempts < stalk_count * 8:
        attempts += 1
        sx = _r.uniform(mound_cx - field_w / 2.0 + 1.0, mound_cx + field_w / 2.0 - 1.0)
        sy = _r.uniform(mound_cy - field_d / 2.0 + 1.0, mound_cy + field_d / 2.0 - 1.0)
        # Skip if within the mound footprint
        if abs(sx - mound_cx) <= mound_w / 2.0 + 0.5 and abs(sy - mound_cy) <= mound_d / 2.0 + 0.5:
            continue
        stalk_h = _r.uniform(1.40, 2.20)
        make_cyl("CaneStalk_%d" % placed,
                 (sx, sy, -1.05 + stalk_h / 2.0),
                 0.018, stalk_h,
                 (0.42, 0.40, 0.22, 1.0), segments=4, axis='Z')
        make_box("CaneLeaf_%d" % placed,
                 (sx, sy, -1.05 + stalk_h + 0.10),
                 (0.10, 0.10, 0.16),
                 (0.32, 0.46, 0.22, 1.0))
        placed += 1

    # ── Gravel access path from the south ──
    make_box("Exterior_GravelPath",
             (0.0, -4.0, -0.18),
             (1.40, 8.0, 0.06),
             (0.60, 0.56, 0.50, 1.0))   # gravel
    # Three stone steps up the mound's south face
    for s in range(3):
        make_box("MoundStep_%d" % s,
                 (0.0, -0.40 - s * 0.40, -0.25 + s * 0.10),
                 (1.10, 0.36, 0.10),
                 (0.46, 0.40, 0.34, 1.0))   # limestone-darker


def build_facade_2026_08():
    """2026-08-03 tail pass: the chapel_exterior preset photographs
    the front — which never existed. Portico + steps + door +
    steeple + the asphalt apron, the idling black car, the trash
    can from the lemonade beat."""
    wood = (0.82, 0.80, 0.74, 1.0)      # white clapboard
    trim = (0.62, 0.60, 0.55, 1.0)
    # Steps + portico
    for si, (sy, sz) in enumerate(((-0.45, 0.15), (-0.75, 0.30), (-1.05, 0.45))):
        make_box(f"Church_Step_{si}", (0.0, sy, sz - 0.075), (2.4, 0.32, 0.15), trim)
    for px in (-1.0, 1.0):
        make_cyl(f"Portico_Col_{px:+.0f}", (px, -0.9, 1.55), 0.09, 2.6, wood, segments=8)
    make_box("Portico_Roof", (0.0, -0.7, 3.05), (2.8, 1.8, 0.22), (0.42, 0.36, 0.30, 1.0))
    make_box("Portico_Pediment", (0.0, -0.55, 3.35), (2.4, 1.2, 0.4), wood)
    # Door + facade face + steeple
    make_box("Church_Door", (0.0, -0.02, 1.30), (1.10, 0.08, 2.30), (0.36, 0.26, 0.16, 1.0))
    make_box("Facade_Face", (0.0, -0.05, 1.85), (5.2, 0.06, 3.7), wood)
    make_box("Facade_Gable", (0.0, -0.05, 4.2), (3.4, 0.06, 1.2), wood)
    make_box("Steeple_Base", (0.0, 0.8, 4.6), (1.2, 1.2, 1.6), wood)
    make_box("Steeple_Spire_0", (0.0, 0.8, 5.9), (0.85, 0.85, 1.2), trim)
    make_box("Steeple_Spire_1", (0.0, 0.8, 7.1), (0.5, 0.5, 1.4), trim)
    make_box("Steeple_Cross_V", (0.0, 0.8, 8.2), (0.06, 0.06, 0.8), (0.74, 0.58, 0.28, 1.0))
    make_box("Steeple_Cross_H", (0.0, 0.8, 8.4), (0.4, 0.06, 0.06), (0.74, 0.58, 0.28, 1.0))
    # The shimmering asphalt apron + curb
    make_box("Asphalt_Apron", (0.0, -6.5, -0.01), (14.0, 10.0, 0.04), (0.22, 0.22, 0.24, 1.0))
    make_box("Curb", (0.0, -9.0, 0.05), (14.0, 0.25, 0.12), (0.55, 0.53, 0.48, 1.0))
    # The long black car idling by the curb
    make_box("Black_Car_Body", (4.5, -8.0, 0.55), (4.6, 1.75, 0.55), (0.08, 0.08, 0.10, 1.0))
    make_box("Black_Car_Cabin", (4.2, -8.0, 1.02), (2.4, 1.6, 0.45), (0.08, 0.08, 0.10, 1.0))
    make_box("Black_Car_Glass", (4.2, -8.0, 1.04), (2.2, 1.45, 0.36), (0.16, 0.18, 0.22, 1.0))
    for wx in (3.0, 5.9):
        for wy in (-8.75, -7.25):
            make_cyl(f"BC_Wheel_{wx:.0f}_{wy:.2f}", (wx, wy, 0.30), 0.30, 0.22,
                     (0.06, 0.06, 0.07, 1.0), segments=10, axis='Y')
    # The trash can at the foot of the steps (the lemonade cup)
    make_cyl("Trash_Can", (1.8, -2.2, 0.45), 0.28, 0.90, (0.30, 0.34, 0.30, 1.0), segments=10)


def main():
    clear_scene()
    build_shell()
    build_stained_glass_window()
    build_altar()
    build_pews()
    build_statue_niche()
    build_bell_pull()
    build_ceiling_infra()
    build_decor()
    build_lovers_exterior()
    build_facade_2026_08()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/roadside_chapel.glb"))
    print(f"\n[build_roadside_chapel] exporting to {out}")
    build_horizon_2026_08()
    export_glb(out)



def build_horizon_2026_08():
    """STUMP HUNT: view stopped at 32m. Cane fields and hedgerow
    lines running out to the parish section roads."""
    # GROUND under everything out past the last band (2026-08-09,
    # user: "no ground on any of the roads — a flat expanse of
    # nothing"). Locale-colored so exteriors stop sharing a void.
    make_box("Ground_Far", (0.0, 0.0, -0.03), (1080.0, 1080.0, 0.02),
             (0.22, 0.28, 0.16, 1.0))
    from _props.detail import make_far_bands
    make_far_bands("FarHedgerow", (0.30, 0.38, 0.26),
                   [(60.0, 70.0, 5.0, 0.90), (130.0, 120.0, 6.5, 0.72),
                    (260.0, 200.0, 8.0, 0.56), (460.0, 320.0, 10.0, 0.42)],
                   profile="treeline")


if __name__ == "__main__":
    main()
