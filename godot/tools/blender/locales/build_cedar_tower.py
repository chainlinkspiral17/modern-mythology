"""cedar_tower — the Oneironautics building off Old Yachats Road
(vol7 ch22). Until now these scenes played over the Texas warehouse
cathedral — a different building entirely.

Canon (vol7_ch22_floors + vol7_ch22_portal):
LOBBY — "polished cedar. The walls were cedar paneling. The ceiling
was twelve feet up. A reception desk — empty, no chair behind it,"
the corporate portrait of Dean at forty-eight (looking at his
daughter at the photographer's left), cedar stairs at the back with
a brass handrail, double doors that open from the inside.
STUDIO (2nd) — server racks at the back wall with green indicator
lights, desk clusters of four, and the walls "covered, floor to
ceiling, in framed posters of every slow-stick Oneironautics Inc.
had ever released" — Estuary 7 half-sized among them; smaller
framed photographs on the east wall.
QUARTERS (3rd) — bunks, a small kitchen at the east end with cedar
cabinets and a wood-stove, a communal dining table that seats
twelve, the open book.
PORTAL (4th) — a landing with a single unmarked cedar door, a
six-by-six-inch translucent window at chest height, and beyond it
the sixty-by-sixty portal room: the smart-glass far wall rendering
the substrate itself, the far cedar door where Aria waves goodbye.
EXTERIOR — the gravel clearing, the wagon, the seven-story tower
with the seventh floor's smart-glass running the garden.

Layout: floors stacked vertically (riverboat precedent) — lobby
z=0, studio z=5, quarters z=10, portal z=15; the exterior stands at
x≈+45 in the same GLB. Blender Z-up, y=0 south (camera side); glTF
export remaps to Godot (x, z, -y). Five CAMERA_PRESETS vantages.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, make_rot_box, export_glb
from _props.structure import make_wall_with_openings, make_window, make_curtains

CEDAR = (0.58, 0.42, 0.28, 1.0)          # polished cedar
CEDAR_PANEL = (0.52, 0.38, 0.25, 1.0)
CEDAR_DK = (0.42, 0.30, 0.20, 1.0)
BRASS = (0.74, 0.58, 0.28, 1.0)
GLASS = (0.50, 0.58, 0.64, 0.4)
SMART_GLASS = (0.36, 0.52, 0.60, 0.85)   # substrate render
SUBSTRATE_BAND = (0.55, 0.75, 0.80, 0.9)
GREEN_LED = (0.30, 0.86, 0.42, 1.0)
POSTER_TINTS = [(0.36, 0.50, 0.58, 1.0), (0.62, 0.48, 0.30, 1.0), (0.34, 0.46, 0.36, 1.0),
                (0.56, 0.36, 0.34, 1.0), (0.44, 0.42, 0.56, 1.0), (0.66, 0.60, 0.44, 1.0)]
FRAME = (0.24, 0.18, 0.13, 1.0)
GRAVEL = (0.52, 0.48, 0.42, 1.0)
SITKA = (0.12, 0.22, 0.16, 1.0)
WIN_PAL = {"frame": (0.36, 0.26, 0.17, 1.0), "casing": (0.62, 0.46, 0.31, 1.0)}

# THE WINDOWS (2026-10-21). Canon: "Smart-glass on the upper six floors"
# (the outside renders the setting onto itself; from inside it is glass),
# and "Dean alone at the studio's south window looking at the ocean". The
# ground floor is cedar paneling with windows cut in it. Windows face N
# and W only: the exterior set (x 45) stands to the east of these rooms in
# the same GLB, and an east window would look at the tower from inside it.
LOBBY_WIN_W = [(2.6, 1.95, 1.50, 2.30), (5.3, 1.95, 1.50, 2.30)]
LOBBY_WIN_N = [(-3.4, 1.95, 1.40, 2.30), (3.6, 2.10, 1.40, 2.00)]
STUDIO_WIN_N = [(-4.2, 2.48, 2.40, 0.62), (-1.4, 2.48, 2.40, 0.62), (1.4, 2.48, 2.40, 0.62), (4.2, 2.48, 2.40, 0.62)]
STUDIO_WIN_S = [(-2.2 - (-3.5), 1.45, 2.10, 1.90)]   # along the S_W wall piece (centre -3.5)
QUARTERS_WIN_N = [(-2.6, 1.50, 1.70, 1.45), (0.0, 1.50, 1.70, 1.45), (2.6, 1.50, 1.70, 1.45)]


def _room(prefix, z0, w, d, ceil, openings=None):
    """Cedar-paneled floor plate: floor, walls (S door gap), ceiling.
    `openings` (2026-10-21, the Deck: "interiors need more windows" /
    "still in the too boxy phase"): {"N"|"W"|"S_W": [(along, z, w, h)]}
    cuts those walls for windows (z from the floor)."""
    openings = openings or {}
    pal = {"wall": CEDAR_PANEL, "baseboard": CEDAR_DK}
    make_box(f"{prefix}_Floor", (0.0, d/2.0, z0 + 0.02), (w + 0.4, d + 0.4, 0.06), CEDAR)
    for side, nm, x in (("W", f"{prefix}_Wall_W", -w/2.0), ("E", f"{prefix}_Wall_E", w/2.0)):
        if side in openings:
            make_wall_with_openings(nm, (x, d/2.0, z0), length=d + 0.4, openings=openings[side],
                                    height=ceil, axis='Y', palette=pal,
                                    baseboard_face_sign=(1 if side == "W" else -1), base_z=z0)
        else:
            make_box(nm, (x, d/2.0, z0 + ceil/2.0), (0.20, d + 0.4, ceil), CEDAR_PANEL)
    if "N" in openings:
        make_wall_with_openings(f"{prefix}_Wall_N", (0.0, d, z0), length=w + 0.4, openings=openings["N"],
                                height=ceil, axis='X', palette=pal, baseboard_face_sign=-1, base_z=z0)
    else:
        make_box(f"{prefix}_Wall_N", (0.0, d, z0 + ceil/2.0), (w + 0.4, 0.20, ceil), CEDAR_PANEL)
    for side, nm, cx, ww in (("S_W", f"{prefix}_Wall_S_W", -(w/4.0 + 0.5), w/2.0 - 1.0),
                             ("S_E", f"{prefix}_Wall_S_E", +(w/4.0 + 0.5), w/2.0 - 1.0)):
        if side in openings:
            make_wall_with_openings(nm, (cx, 0.0, z0), length=ww, openings=openings[side],
                                    height=ceil, axis='X', palette=pal, baseboard_face_sign=1, base_z=z0)
        else:
            make_box(nm, (cx, 0.0, z0 + ceil/2.0), (ww, 0.20, ceil), CEDAR_PANEL)
    make_box(f"{prefix}_Wall_S_Header", (0.0, 0.0, z0 + ceil - 0.30), (2.0, 0.20, 0.60), CEDAR_PANEL)
    make_box(f"{prefix}_Ceil", (0.0, d/2.0, z0 + ceil), (w + 0.4, d + 0.4, 0.06), CEDAR_DK)
    # Panel seams: vertical cedar batten rhythm on the N wall (not
    # across a window)
    for i in range(int(w // 1.0)):
        bx = -w/2.0 + 0.6 + i * 1.0
        if any(abs(bx - oc) < ow / 2.0 + 0.20 for oc, _, ow, _ in openings.get("N", ())):
            continue
        make_box(f"{prefix}_Batten_{i}", (bx, d - 0.11, z0 + ceil/2.0), (0.05, 0.02, ceil - 0.2), CEDAR_DK)


def _windows(prefix, z0, wall, line, cuts, *, trim=True, curtains=None):
    """A cedar-framed window in each cut made by _room. wall 'N' | 'W' |
    'S'; line = the wall's room-side face (y for N/S, x for W)."""
    along_y = wall == "W"
    room_dir = {"N": -1, "S": +1, "W": +1}[wall]
    for k, (oc, oz, ow, oh) in enumerate(cuts):
        anchor = (line, oc, z0 + oz) if along_y else (oc, line, z0 + oz)
        make_window(f"{prefix}_{k}", anchor, width=ow - 0.20, height=oh - 0.10,
                    axis=('Y' if along_y else 'X'), room_dir=room_dir, palette=WIN_PAL, trim=trim,
                    see_through=True)   # the cedars and the sea, not a cream pane
        if curtains:
            make_curtains(f"{prefix}_{k}_Curtain", anchor, width=ow - 0.20, height=oh - 0.10,
                          axis=('Y' if along_y else 'X'), room_dir=room_dir, color=curtains,
                          rod_col=BRASS)


def build_lobby():
    z0 = 0.0; W, D, C = 10.0, 8.0, 3.66   # twelve-foot ceiling
    _room("Lobby", z0, W, D, C, openings={"W": LOBBY_WIN_W, "N": LOBBY_WIN_N})
    _windows("Lobby_Win_W", z0, "W", -W/2.0 + 0.10, LOBBY_WIN_W)
    _windows("Lobby_Win_N", z0, "N", D - 0.10, LOBBY_WIN_N)
    # Double doors, S center (open from the inside — no panel)
    for sgn in (-1, 1):
        make_box(f"Lobby_Door_{sgn:+d}", (sgn * 0.5, 0.06, z0 + 1.25), (0.95, 0.06, 2.50), CEDAR_DK)
        make_cyl(f"Lobby_Door_Bar_{sgn:+d}", (sgn * 0.85, 0.12, z0 + 1.20), 0.025, 0.55, BRASS, segments=8)
    # Reception desk — empty, NO chair behind it
    make_box("Reception_Desk", (0.0, 5.2, z0 + 0.55), (2.8, 0.8, 1.10), CEDAR_DK)
    make_box("Reception_Top", (0.0, 5.2, z0 + 1.12), (2.95, 0.95, 0.06), CEDAR)
    # (2026-11-04) "The photograph of Dean at forty-eight. Tem stopped at the
    # desk. She looked at the photograph": a framed photograph standing on
    # the desk's near corner, tilted back on its easel leg
    make_rot_box("Reception_Photo_Frame", (0.60, 5.0, z0 + 1.15 + 0.13), (0.22, 0.02, 0.27), FRAME, roll=-0.18)
    make_rot_box("Reception_Photo", (0.60, 5.0 - 0.012, z0 + 1.15 + 0.13), (0.18, 0.004, 0.22), (0.58, 0.54, 0.48, 1.0), roll=-0.18)
    make_rot_box("Reception_Photo_Leg", (0.60, 5.0 + 0.09, z0 + 1.15 + 0.08), (0.03, 0.02, 0.18), FRAME, roll=0.45)
    # THE PHOTOGRAPH: Dean at forty-eight, corporate portrait, on
    # the N wall behind the desk — head and shoulders, eye-line to
    # the photographer's left (where Aria stood, at twelve)
    make_box("Dean_Portrait_Frame", (0.0, D - 0.12, z0 + 1.90), (0.72, 0.04, 0.92), FRAME)
    make_box("Dean_Portrait", (0.0, D - 0.135, z0 + 1.90), (0.60, 0.03, 0.80), (0.66, 0.62, 0.56, 1.0))
    make_box("Dean_Portrait_Figure", (0.02, D - 0.145, z0 + 1.78), (0.34, 0.02, 0.46), (0.32, 0.30, 0.32, 1.0))
    make_cyl("Dean_Portrait_Head", (-0.03, D - 0.15, z0 + 2.08), 0.10, 0.02, (0.74, 0.62, 0.52, 1.0), axis='Y', segments=10)
    # Cedar stairs at the back, E side, brass handrail
    for s in range(8):
        make_box(f"Lobby_Stair_{s}", (3.6, 6.9 - s * 0.32, z0 + (0.23 + s * 0.22) / 2.0), (1.5, 0.32, 0.23 + s * 0.22), CEDAR)   # solid to the floor (2026-09-08)
    make_cyl("Lobby_Handrail", (2.85, 5.8, z0 + 1.55), 0.03, 2.6, BRASS, segments=8, axis='Y')
    for hp in (4.8, 6.6):
        make_box(f"Lobby_Handrail_Post_{hp:.1f}", (2.85, hp, z0 + 0.9 + (6.9 - hp) * 0.6), (0.05, 0.05, 0.9), CEDAR_DK)
    # Low cedar bench along the W wall (a lobby, not a void)
    make_box("Lobby_Bench", (-4.4, 3.5, z0 + 0.40), (0.5, 2.4, 0.10), CEDAR)
    make_box("Lobby_Bench_Base", (-4.4, 3.5, z0 + 0.20), (0.42, 2.2, 0.30), CEDAR_DK)


def build_studio():
    z0 = 5.0; W, D, C = 12.0, 9.0, 3.0
    _room("Studio", z0, W, D, C, openings={"N": STUDIO_WIN_N, "S_W": STUDIO_WIN_S})
    # the glass band over the racks (no stool: the racks stand under it)
    _windows("Studio_Win_N", z0, "N", D - 0.10, STUDIO_WIN_N, trim=False)
    # the canon south window, in the poster run
    _windows("Studio_Win_S", z0, "S", 0.10, [(-2.2, 1.45, 2.10, 1.90)])
    # Server racks along the N wall, green indicator lights
    for ri in range(5):
        rx = -4.6 + ri * 2.3
        make_box(f"Rack_{ri}", (rx, D - 0.55, z0 + 1.05), (0.70, 0.75, 2.10), (0.24, 0.25, 0.28, 1.0))
        for li in range(5):
            make_box(f"Rack_{ri}_LED_{li}", (rx - 0.20 + li * 0.10, D - 0.92, z0 + 1.65),
                     (0.03, 0.01, 0.03), GREEN_LED)
        make_box(f"Rack_{ri}_Vents", (rx, D - 0.92, z0 + 0.85), (0.55, 0.01, 1.00), (0.16, 0.17, 0.19, 1.0))
    # Two desk clusters of four
    for ci, (cx, cy) in enumerate(((-2.2, 4.2), (2.2, 4.2))):
        for di, (dx, dy) in enumerate(((-0.75, -0.5), (0.75, -0.5), (-0.75, 0.5), (0.75, 0.5))):
            make_box(f"Desk_{ci}_{di}", (cx + dx, cy + dy, z0 + 0.72), (1.30, 0.75, 0.05), CEDAR)
            make_box(f"Desk_{ci}_{di}_Leg", (cx + dx, cy + dy, z0 + 0.36), (0.10, 0.60, 0.70), CEDAR_DK)
            make_box(f"Desk_{ci}_{di}_Monitor", (cx + dx, cy + dy + 0.22, z0 + 0.885),   # on the desk (2026-09-22: 7 cm up)
                     (0.44, 0.03, 0.28), (0.14, 0.15, 0.17, 1.0))
            make_box(f"Chair_{ci}_{di}", (cx + dx, cy + dy - 0.65, z0 + 0.44), (0.42, 0.42, 0.06), CEDAR_DK)
            make_cyl(f"Chair_{ci}_{di}_Post", (cx + dx, cy + dy - 0.65, z0 + 0.225), 0.03, 0.41, CEDAR_DK, segments=6)   # (2026-09-22)
            make_cyl(f"Chair_{ci}_{di}_Base", (cx + dx, cy + dy - 0.65, z0 + 0.04), 0.22, 0.04, CEDAR_DK, segments=8)
    # THE POSTER ARCHIVE: floor-to-ceiling framed slowstick posters,
    # S + W walls
    idx = 0
    # (2026-10-21: -2.8 and -1.6 gave way to the south window)
    for wall, coords in (("S", [(x, 0.13) for x in (-5.2, -4.0, 1.6, 2.8, 4.0, 5.2)]),
                         ("W", [(-5.87, y) for y in (1.2, 2.4, 3.6, 4.8, 6.0, 7.2)])):
        for (px, py) in coords:
            for row, pz in enumerate((z0 + 0.85, z0 + 2.05)):
                tint = POSTER_TINTS[idx % len(POSTER_TINTS)]; idx += 1
                if wall == "S":
                    make_box(f"Poster_S_{idx}_Frame", (px, 0.115, pz), (1.00, 0.03, 1.05), FRAME)
                    make_box(f"Poster_S_{idx}", (px, 0.1225, pz), (0.90, 0.025, 0.95), tint)
                else:
                    make_box(f"Poster_W_{idx}_Frame", (-5.885, py, pz), (0.03, 1.00, 1.05), FRAME)
                    make_box(f"Poster_W_{idx}", (-5.8775, py, pz), (0.025, 0.90, 0.95), tint)
    # ESTUARY 7, half-sized, on the S wall east run — the river
    # coming down to the sea, coastal blues
    # (2026-09-22: it hung at x 0.55 — in the S wall's door gap, on
    # air; now on the E wall between the first two photographs)
    make_box("Estuary7_Frame", (5.8825, 2.55, z0 + 1.55), (0.035, 0.55, 0.60), BRASS)
    make_box("Estuary7_Poster", (5.85, 2.55, z0 + 1.55), (0.03, 0.47, 0.52), (0.40, 0.56, 0.60, 1.0))
    make_box("Estuary7_River", (5.8355, 2.55, z0 + 1.50), (0.028, 0.10, 0.40), (0.62, 0.76, 0.78, 1.0))
    # East wall: the smaller framed photographs (Dean in '14, '19,
    # '41…)
    for pi, py in enumerate((2.0, 3.1, 4.2, 5.3, 6.4)):
        make_box(f"EPhoto_{pi}_Frame", (5.885, py, z0 + 1.60), (0.03, 0.42, 0.34), FRAME)
        make_box(f"EPhoto_{pi}", (5.8775, py, z0 + 1.60), (0.025, 0.34, 0.26), (0.62, 0.58, 0.52, 1.0))


def build_quarters():
    z0 = 10.0; W, D, C = 12.0, 8.0, 2.9
    _room("Quarters", z0, W, D, C, openings={"N": QUARTERS_WIN_N})
    _windows("Quarters_Win_N", z0, "N", D - 0.10, QUARTERS_WIN_N, curtains=(0.56, 0.50, 0.40, 1.0))
    # Bunks along the W wall — three doubles
    for bi, by in enumerate((1.6, 3.8, 6.0)):
        make_box(f"Bunk_{bi}_Frame", (-5.1, by, z0 + 0.85), (1.1, 2.0, 1.70), CEDAR_DK)
        for lvl, lz in enumerate((0.42, 1.30)):
            make_box(f"Bunk_{bi}_Mattress_{lvl}", (-5.1, by, z0 + lz), (1.0, 1.9, 0.14), (0.86, 0.82, 0.74, 1.0))
            make_box(f"Bunk_{bi}_Blanket_{lvl}", (-5.1, by - 0.35, z0 + lz + 0.09), (0.96, 1.0, 0.06), (0.42, 0.46, 0.55, 1.0))
    # Kitchen at the EAST end: cedar cabinets + wood-stove
    make_box("Q_Counter", (5.1, 4.0, z0 + 0.46), (0.9, 3.2, 0.92), CEDAR_DK)
    make_box("Q_Counter_Top", (5.1, 4.0, z0 + 0.94), (0.95, 3.3, 0.05), CEDAR)
    make_box("Q_Cabinets", (5.725, 4.0, z0 + 1.95), (0.35, 3.0, 0.80), CEDAR_PANEL)   # on the E wall (2026-09-22: 18 cm off it)
    make_cyl("Q_Stove_Belly", (5.0, 6.6, z0 + 0.375), 0.32, 0.75, (0.14, 0.14, 0.16, 1.0), segments=12)   # to the floor
    make_cyl("Q_Stove_Pipe", (5.0, 6.6, z0 + 1.9), 0.08, 2.0, (0.20, 0.19, 0.20, 1.0), segments=8)
    # The communal table that seats twelve
    make_box("Q_Table", (-0.4, 4.0, z0 + 0.76), (4.2, 1.10, 0.07), CEDAR)
    for lx in (-2.2, 1.4):
        make_box(f"Q_Table_Leg_{lx:+.1f}", (lx, 4.0, z0 + 0.38), (0.12, 0.95, 0.74), CEDAR_DK)
    def _q_legs(tag, x, y):   # (2026-09-22: twelve seats hung at 0.42)
        for lx_ in (-1, 1):
            for ly_ in (-1, 1):
                make_box(f"{tag}_Leg_{lx_:+d}_{ly_:+d}", (x + lx_ * 0.16, y + ly_ * 0.16, z0 + 0.2125),
                         (0.035, 0.035, 0.425), CEDAR_DK)
    for si in range(5):
        sx = -2.0 + si * 0.85
        for sy in (3.25, 4.75):
            make_box(f"Q_Chair_{si}_{sy:.2f}", (sx, sy, z0 + 0.45), (0.40, 0.40, 0.05), CEDAR_DK)
            _q_legs(f"Q_Chair_{si}_{sy:.2f}", sx, sy)
    for hx in (-2.75, 2.0):
        make_box(f"Q_HeadChair_{hx:+.2f}", (hx, 4.0, z0 + 0.45), (0.40, 0.44, 0.05), CEDAR_DK)
        _q_legs(f"Q_HeadChair_{hx:+.2f}", hx, 4.0)
    # The open book — the same book on Tem's cedar shelf
    make_box("Q_Book_Open_L", (1.2, 4.1, z0 + 0.80), (0.14, 0.20, 0.012), (0.88, 0.86, 0.78, 1.0))
    make_box("Q_Book_Open_R", (1.35, 4.1, z0 + 0.80), (0.14, 0.20, 0.012), (0.88, 0.86, 0.78, 1.0))


def _cedar_door(prefix, yc, z0, *, face=-1, handle_x=0.30, window=False, casing=True):
    """A cedar plank door in a 0.90 x 2.50 opening, its near face toward
    `face` (-1: seen from the south). Parts: <prefix> (the leaf's core),
    _Plank_i, _Casing_*, _Handle, _Handle_Plate and, with `window`,
    _Window_Frame / _Window (named so the old markers and art still find
    Portal_Window)."""
    yf = yc + face * 0.04                       # the leaf's near face
    make_box(prefix, (0.0, yc, z0 + 1.25), (0.90, 0.07, 2.50), FRAME)        # the core: dark in the plank gaps
    tones = (CEDAR, (0.62, 0.45, 0.30, 1.0), (0.55, 0.39, 0.26, 1.0), (0.60, 0.43, 0.28, 1.0), CEDAR)
    for i in range(5):
        make_box(f"{prefix}_Plank_{i}", (-0.36 + i * 0.18, yf, z0 + 1.25), (0.172, 0.012, 2.48), tones[i])
    for nm, rz in (("Rail_Top", 2.28), ("Rail_Bottom", 0.22)):
        make_box(f"{prefix}_{nm}", (0.0, yf + face * 0.009, z0 + rz), (0.88, 0.008, 0.14), CEDAR_DK)
    if casing:
        for sgn in (-1, 1):
            make_box(f"{prefix}_Casing_{sgn:+d}", (sgn * 0.495, yc + face * 0.085, z0 + 1.29), (0.09, 0.05, 2.58), FRAME)
        make_box(f"{prefix}_Casing_Top", (0.0, yc + face * 0.085, z0 + 2.58), (1.08, 0.05, 0.10), FRAME)
        make_box(f"{prefix}_Threshold", (0.0, yc + face * 0.07, z0 + 0.06), (0.90, 0.10, 0.02), BRASS)
    hz = z0 + 1.05
    make_box(f"{prefix}_Handle_Plate", (handle_x, yf + face * 0.010, hz), (0.05, 0.008, 0.18), BRASS)
    make_cyl(f"{prefix}_Handle", (handle_x, yf + face * 0.035, hz), 0.012, 0.05, BRASS, axis='Y', segments=8)
    lever_dx = -0.055 if handle_x > 0 else 0.055
    make_box(f"{prefix}_Handle_Lever", (handle_x + lever_dx, yf + face * 0.055, hz), (0.13, 0.016, 0.020), BRASS)
    if window:
        wz = z0 + 1.42
        base = prefix.replace("_Door", "")
        make_box(f"{base}_Window_Frame", (handle_x, yf + face * 0.012, wz), (0.21, 0.012, 0.21), FRAME)
        make_box(f"{base}_Window", (handle_x, yf + face * 0.020, wz), (0.152, 0.006, 0.152), (0.92, 0.95, 0.93, 1.0))


def build_portal_floor():
    """Fourth floor: landing + the unmarked cedar door with the
    six-inch window, and beyond it the 18×18 portal room — the
    smart-glass far wall rendering the substrate, the far door with
    the handle Aria's hand rests on."""
    z0 = 15.0; C = 3.2
    # Landing, y 0..3
    make_box("Landing_Floor", (0.0, 1.5, z0 + 0.02), (4.4, 3.4, 0.06), CEDAR)
    for nm, x in (("Landing_Wall_W", -2.1), ("Landing_Wall_E", 2.1)):
        make_box(nm, (x, 1.5, z0 + C/2.0), (0.20, 3.4, C), CEDAR_PANEL)
    make_box("Landing_Ceil", (0.0, 1.5, z0 + C), (4.4, 3.4, 0.06), CEDAR_DK)
    # The door wall (N side of the landing) with THE DOOR
    for sgn in (-1, 1):
        make_box(f"Landing_DoorWall_{sgn:+d}", (sgn * 1.55, 3.0, z0 + C/2.0), (1.3, 0.20, C), CEDAR_PANEL)
    make_box("Landing_DoorWall_Header", (0.0, 3.0, z0 + C - 0.35), (0.9, 0.20, 0.70), CEDAR_PANEL)
    # (pass 455) THE DOOR. It was one slab the colour of its wall with a
    # 5 cm knob and a window in its middle: the seven "insert door" lines
    # framed brown. "The door was unmarked. It was cedar. Above the door's
    # handle was a window, six inches by six, set into the cedar at chest
    # height ... The window itself was milky" (ch22). Now a dark casing, a
    # leaf of five cedar planks, a lever on its plate, and the window ABOVE
    # THE HANDLE, its glass the brightest thing on the landing.
    _cedar_door("Portal_Door", 2.98, z0, face=-1, handle_x=0.30, window=True)
    # THE PORTAL ROOM beyond, 18×18 (sixty feet)
    make_box("Portal_Room_Floor", (0.0, 12.0, z0 + 0.02), (18.4, 18.4, 0.06), CEDAR)
    for nm, x in (("Portal_Wall_W", -9.1), ("Portal_Wall_E", 9.1)):
        make_box(nm, (x, 12.0, z0 + C/2.0), (0.20, 18.4, C), CEDAR_PANEL)
    make_box("Portal_Ceil", (0.0, 12.0, z0 + C), (18.4, 18.4, 0.06), CEDAR_DK)
    # The smart-glass far wall: the substrate rendered against it —
    # bands of held light
    make_box("SmartGlass_Wall", (0.0, 21.0, z0 + C/2.0), (18.4, 0.15, C), SMART_GLASS)
    for bi in range(5):
        make_box(f"Substrate_Band_{bi}", (-7.0 + bi * 3.5, 20.9, z0 + 0.7 + (bi % 3) * 0.9),
                 (2.2, 0.05, 0.35), SUBSTRATE_BAND)
    # The air held a half-second longer than ordinary air: faint
    # shimmer volumes
    for si, (sx, sy) in enumerate(((-4.0, 9.0), (3.0, 13.0), (0.0, 17.0))):
        make_box(f"Air_Shimmer_{si}", (sx, sy, z0 + 1.5), (3.5, 3.0, 2.4), (0.78, 0.84, 0.86, 0.10))
    # The FAR DOOR — cedar, unmarked, handle opposite; Aria's exit
    _cedar_door("Far_Door", 20.92, z0, face=-1, handle_x=-0.30, window=False, casing=False)



def build_draft2_density_2026_08():
    """DRAFT 2 (drafting-program ledger): per-floor dressing density
    + portal-room staging. Draft 1 was the named hero objects in
    empty cedar rooms; this pass makes each floor read as USED —
    and stages the portal room's sixty-foot walk as a walk.
    Draft 3 targets: vn_shot coverage per floor, D2 wear pass,
    Deck reframe of the five presets."""
    # ── LOBBY (z0=0) · a lobby someone keeps, not a void ──
    z0 = 0.0
    # Ceiling beams — the twelve-foot ceiling earns its height.
    for bi, by in enumerate((2.0, 4.0, 6.0)):
        make_box(f"Lobby_Beam_{bi}", (0.0, by, z0 + 3.42), (10.2, 0.30, 0.28), CEDAR_DK)
    # Pendant lamps hung from the beams.
    for pi, (px, py) in enumerate(((-2.4, 4.0), (2.4, 4.0))):
        make_cyl(f"Lobby_Pendant_{pi}_Cord", (px, py, z0 + 3.15), 0.012, 0.45, (0.20, 0.18, 0.16, 1.0), segments=6)
        make_cyl(f"Lobby_Pendant_{pi}_Shade", (px, py, z0 + 2.85), 0.16, 0.18, BRASS, segments=10)
        make_cyl(f"Lobby_Pendant_{pi}_Bulb", (px, py, z0 + 2.78), 0.05, 0.06, (0.98, 0.92, 0.72, 1.0), segments=8)
    # Runner from the doors to the desk — the walk-in line.
    make_box("Lobby_Runner", (0.0, 2.6, z0 + 0.055), (1.4, 4.4, 0.015), (0.46, 0.30, 0.22, 1.0))
    make_box("Lobby_Runner_Border", (0.0, 2.6, z0 + 0.062), (1.15, 4.15, 0.008), (0.52, 0.36, 0.26, 1.0))
    # Reception desk dress: the visitor ledger OPEN, a pen, the
    # small brass bell (the studio's motif rings here too).
    make_box("Lobby_Ledger_L", (-0.30, 5.05, z0 + 1.155), (0.16, 0.22, 0.012), (0.90, 0.88, 0.80, 1.0))
    make_box("Lobby_Ledger_R", (-0.13, 5.05, z0 + 1.155), (0.16, 0.22, 0.012), (0.90, 0.88, 0.80, 1.0))
    make_cyl("Lobby_Pen", (0.10, 5.00, z0 + 1.16), 0.007, 0.13, (0.16, 0.18, 0.30, 1.0), axis='X', segments=6)
    make_cyl("Lobby_Bell_Base", (0.55, 5.05, z0 + 1.165), 0.05, 0.02, (0.62, 0.64, 0.66, 1.0), segments=10)
    make_cyl("Lobby_Bell_Dome", (0.55, 5.05, z0 + 1.20), 0.045, 0.05, BRASS, segments=10)
    # Coat rack (one coat — somebody IS here) + umbrella stand.
    make_cyl("Lobby_CoatRack_Pole", (-4.5, 6.8, z0 + 0.95), 0.03, 1.90, CEDAR_DK, segments=8)
    make_cyl("Lobby_CoatRack_Base", (-4.5, 6.8, z0 + 0.03), 0.22, 0.05, CEDAR_DK, segments=10)
    make_box("Lobby_Coat", (-4.5, 6.75, z0 + 1.30), (0.34, 0.16, 0.85), (0.30, 0.32, 0.38, 1.0))
    make_cyl("Lobby_Umbrella_Stand", (-4.0, 6.9, z0 + 0.25), 0.11, 0.50, BRASS, segments=10)
    make_cyl("Lobby_Umbrella", (-3.97, 6.87, z0 + 0.55), 0.03, 0.75, (0.20, 0.24, 0.30, 1.0), segments=6)
    # Low table by the bench, brochures fanned.
    make_box("Lobby_SideTable", (-4.35, 2.0, z0 + 0.42), (0.5, 0.6, 0.05), CEDAR)
    make_box("Lobby_SideTable_Leg", (-4.35, 2.0, z0 + 0.20), (0.08, 0.08, 0.40), CEDAR_DK)
    for fi in range(3):
        make_box(f"Lobby_Brochure_{fi}", (-4.38 + fi * 0.05, 2.0 - fi * 0.04, z0 + 0.455 + fi * 0.006),
                 (0.12, 0.20, 0.005), POSTER_TINTS[fi % len(POSTER_TINTS)])
    # Wall sconces flanking the portrait.
    for sx in (-1.4, 1.4):
        make_box(f"Lobby_Sconce_{sx:+.1f}_Back", (sx, 7.88, z0 + 2.10), (0.10, 0.04, 0.22), BRASS)
        make_cyl(f"Lobby_Sconce_{sx:+.1f}_Glow", (sx, 7.80, z0 + 2.16), 0.045, 0.09, (0.98, 0.90, 0.70, 1.0), segments=8)

    # ── STUDIO (z0=5) · people work here mid-shift ──
    z0 = 5.0
    for ci, (cx, cy) in enumerate(((-2.2, 4.2), (2.2, 4.2))):
        for di, (dx, dy) in enumerate(((-0.75, -0.5), (0.75, -0.5), (-0.75, 0.5), (0.75, 0.5))):
            make_box(f"Kbd_{ci}_{di}", (cx + dx, cy + dy - 0.10, z0 + 0.755), (0.36, 0.13, 0.02),
                     (0.22, 0.23, 0.25, 1.0))
        # One mug per cluster, one chair shoved out of true.
        make_cyl(f"Studio_Mug_{ci}", (cx + 0.55, cy - 0.62, z0 + 0.80), 0.04, 0.09,
                 POSTER_TINTS[(ci * 2) % len(POSTER_TINTS)], segments=8)
    make_box("Studio_Chair_Shoved", (-1.85, 3.35, z0 + 0.44), (0.42, 0.42, 0.06), CEDAR_DK)
    make_cyl("Studio_Chair_Shoved_Post", (-1.85, 3.35, z0 + 0.225), 0.03, 0.41, CEDAR_DK, segments=6)
    make_cyl("Studio_Chair_Shoved_Base", (-1.85, 3.35, z0 + 0.04), 0.22, 0.04, CEDAR_DK, segments=8)
    # Task lamps on the two rack-side desks.
    for ti, tx in enumerate((-2.95, 1.45)):
        make_cyl(f"Studio_TaskLamp_{ti}_Arm", (tx, 4.75, z0 + 0.95), 0.012, 0.40, (0.22, 0.22, 0.24, 1.0), segments=6)
        make_cyl(f"Studio_TaskLamp_{ti}_Head", (tx + 0.06, 4.70, z0 + 1.12), 0.06, 0.09, (0.96, 0.90, 0.72, 1.0), segments=8)   # on the arm (2026-09-22)
    # Cable tray from desk clusters to the racks + floor cable runs
    # (the room is PLUGGED IN — D3 rule at tower scale).
    make_box("Studio_CableTray", (0.0, 6.6, z0 + 2.65), (9.5, 0.25, 0.08), (0.30, 0.31, 0.33, 1.0))
    for hi, hx_ in enumerate((-3.5, 3.5)):   # hung from the ceiling (2026-09-22: 31 cm under it)
        make_cyl(f"Studio_CableTray_Hanger_{hi}", (hx_, 6.6, z0 + 2.845), 0.01, 0.31, (0.30, 0.31, 0.33, 1.0), segments=6)
    for ci2, cx2 in enumerate((-2.2, 2.2)):
        make_box(f"Studio_CableDrop_{ci2}", (cx2, 6.6, z0 + 1.35), (0.10, 0.06, 2.60), (0.24, 0.24, 0.26, 1.0))   # to the floor run
        make_box(f"Studio_CableFloor_{ci2}", (cx2, 5.6, z0 + 0.045), (0.12, 2.0, 0.025), (0.22, 0.22, 0.24, 1.0))
    # Rack labels + ONE rack door ajar (mid-maintenance).
    for ri in range(5):
        make_box(f"Rack_{ri}_Label", (-4.6 + ri * 2.3, 8.0715, z0 + 2.00), (0.30, 0.005, 0.08),   # on the rack's front face (2026-09-25: 37 cm inside it)
                 (0.88, 0.86, 0.78, 1.0))
    make_box("Rack_2_Door_Ajar", (0.35, 8.02, z0 + 1.05), (0.55, 0.03, 2.00), (0.28, 0.29, 0.32, 1.0))

    # ── QUARTERS (z0=10) · twelve people live here ──
    z0 = 10.0
    for bi, by in enumerate((1.6, 3.8, 6.0)):
        # Bunk ladders + a footlocker per bunk.
        make_box(f"Bunk_{bi}_Ladder_L", (-4.52, by + 0.80, z0 + 0.85), (0.05, 0.05, 1.60), CEDAR_DK)
        make_box(f"Bunk_{bi}_Ladder_R", (-4.52, by + 1.00, z0 + 0.85), (0.05, 0.05, 1.60), CEDAR_DK)
        for ri2 in range(3):
            make_box(f"Bunk_{bi}_Rung_{ri2}", (-4.52, by + 0.90, z0 + 0.45 + ri2 * 0.45),
                     (0.04, 0.22, 0.04), CEDAR)
        # footlocker on the floor in FRONT of the bunk (the frame's east
        # face is x -4.55; bunks sit 0.2 m apart so nothing fits between)
        make_box(f"Bunk_{bi}_Footlocker", (-4.10, by - 0.55, z0 + 0.20), (0.85, 0.42, 0.40), CEDAR_DK)
    # Folded clothes on one mattress, a guitar leaning at the last bunk.
    # on the upper bunk's blanket (2026-09-22: was 35 cm over it)
    make_box("Q_Folded_Clothes", (-5.1, 1.35, z0 + 1.475), (0.30, 0.40, 0.10), (0.52, 0.46, 0.42, 1.0))
    make_box("Q_Guitar_Body", (-4.35, 6.85, z0 + 0.30), (0.32, 0.10, 0.40), (0.55, 0.38, 0.22, 1.0))
    make_box("Q_Guitar_Neck", (-4.35, 6.88, z0 + 0.75), (0.06, 0.05, 0.55), CEDAR_DK)
    # Kitchen life: kettle on the stove, dish rack, mug pegs, pot rail.
    make_cyl("Q_Kettle", (5.0, 6.6, z0 + 0.92), 0.11, 0.16, (0.74, 0.76, 0.78, 1.0), segments=10)
    make_box("Q_DishRack", (5.05, 2.9, z0 + 1.015), (0.45, 0.32, 0.10), (0.62, 0.64, 0.66, 1.0))
    for di2 in range(4):
        make_box(f"Q_Dish_{di2}", (5.05, 2.80 + di2 * 0.07, z0 + 1.095), (0.30, 0.015, 0.16),
                 (0.88, 0.86, 0.80, 1.0))
    for mi in range(5):
        make_cyl(f"Q_MugPeg_{mi}", (5.52, 2.6 + mi * 0.28, z0 + 1.55), 0.015, 0.06,   # on the cabinets' face (2026-09-22)
                 CEDAR_DK, axis='X', segments=6)
        make_cyl(f"Q_PegMug_{mi}", (5.45, 2.6 + mi * 0.28, z0 + 1.485), 0.04, 0.08,
                 POSTER_TINTS[mi % len(POSTER_TINTS)], segments=8)
    # Table life: three mugs at seats, a dealt card fan mid-game.
    for mi2, (mx, my) in enumerate(((-1.6, 3.6), (0.4, 4.4), (1.0, 3.6))):
        make_cyl(f"Q_TableMug_{mi2}", (mx, my, z0 + 0.84), 0.04, 0.09,
                 POSTER_TINTS[(mi2 + 2) % len(POSTER_TINTS)], segments=8)
    for ci3 in range(5):
        make_box(f"Q_Card_{ci3}", (-0.8 + ci3 * 0.09, 4.32 - (ci3 % 2) * 0.03, z0 + 0.805),
                 (0.06, 0.09, 0.003), (0.92, 0.90, 0.84, 1.0))
    make_box("Q_Card_Deck", (-0.35, 4.05, z0 + 0.815), (0.07, 0.10, 0.02), (0.42, 0.20, 0.18, 1.0))
    # Rug under the communal table.
    make_box("Q_Rug", (-0.4, 4.0, z0 + 0.055), (5.2, 2.4, 0.012), (0.40, 0.34, 0.26, 1.0))

    # ── PORTAL FLOOR (z0=15) · staging the sixty-foot walk ──
    z0 = 15.0
    # Landing: boot mat, coat hooks with ONE coat, the waiting bench.
    make_box("Landing_BootMat", (0.0, 0.7, z0 + 0.055), (1.2, 0.7, 0.02), (0.30, 0.26, 0.22, 1.0))
    for hi, hx in enumerate((-1.7, -1.45, -1.2)):
        make_cyl(f"Landing_Hook_{hi}", (hx, 2.92, z0 + 1.70), 0.015, 0.06, BRASS, axis='Y', segments=6)
    make_box("Landing_Hung_Coat", (-1.45, 2.86, z0 + 1.25), (0.30, 0.12, 0.85), (0.34, 0.30, 0.28, 1.0))
    make_box("Landing_Bench", (1.5, 1.0, z0 + 0.40), (1.2, 0.42, 0.08), CEDAR)
    make_box("Landing_Bench_Base", (1.5, 1.0, z0 + 0.20), (1.1, 0.36, 0.32), CEDAR_DK)
    # THE WALK: a darker cedar path from the door to the smart glass
    # — the leading line of the whole floor; two brass threshold
    # strips at the thirds pace it like held breaths.
    make_box("Portal_Walk", (0.0, 12.0, z0 + 0.055), (1.6, 17.6, 0.015), (0.48, 0.33, 0.22, 1.0))
    for ti2, ty in enumerate((9.0, 15.0)):
        make_box(f"Portal_Threshold_{ti2}", (0.0, ty, z0 + 0.065), (1.7, 0.06, 0.012), BRASS)
    # Light pool under the smart glass — the substrate reaches the
    # floor before you reach it.
    make_box("Portal_GlassPool", (0.0, 20.2, z0 + 0.058), (17.6, 1.4, 0.012),
             (0.46, 0.58, 0.62, 1.0))
    # Low cedar sconces pacing the W/E walls — the walk is LIT.
    for si2, sy2 in enumerate((6.0, 10.5, 15.0, 19.0)):
        for sx2 in (-8.98, 8.98):
            make_box(f"Portal_Sconce_{si2}_{sx2:+.0f}_Back", (sx2, sy2, z0 + 1.9),
                     (0.06, 0.10, 0.22), CEDAR_DK)
            make_cyl(f"Portal_Sconce_{si2}_{sx2:+.0f}_Glow", (sx2 * 0.985, sy2, z0 + 1.96),
                     0.04, 0.08, (0.96, 0.88, 0.66, 1.0), axis='X', segments=8)
    # A second, dimmer rank of substrate bands behind the first —
    # depth in the render, not a flat pattern.
    for bi2 in range(4):
        make_box(f"Substrate_Band_Deep_{bi2}", (-5.5 + bi2 * 3.6, 20.96, z0 + 1.3 + (bi2 % 2) * 0.8),
                 (1.6, 0.03, 0.22), (0.44, 0.60, 0.66, 0.6))
    # Vertical seams in the smart glass — it is PANES, not a void.
    for vi in range(3):
        make_box(f"SmartGlass_Seam_{vi}", (-4.6 + vi * 4.6, 20.98, z0 + 1.6),
                 (0.05, 0.04, 3.0), (0.28, 0.42, 0.50, 1.0))
    # The far door earns a surround: frame + a single step.
    make_box("Far_Door_Frame", (0.0, 20.90, z0 + 2.55), (1.15, 0.10, 0.12), CEDAR)
    make_box("Far_Door_Step", (0.0, 20.55, z0 + 0.06), (1.2, 0.45, 0.08), CEDAR_DK)


def build_exterior():
    """The clearing at x≈+45 and the tower on it (pass 476, draft 3 of the
    exterior, by the text, vol7 ch22_drive n52-92):
      "seventy feet on a side at the ground floor. Square. Seven stories.
       Smart-glass on the upper six floors." / "The ground floor was cedar
       siding above a stone foundation, with a single set of double-doors at
       the center facing the clearing." / "the seaward face showing the
       ocean, the inland face showing the cedars. The tower was rendering its
       own setting onto itself." / "The seventh floor was glass-walled
       including the roof ... what looked like vegetation. The indoor
       garden." / "The doors were cedar, hand-built — ... the kind of doors a
       fishing-cabin had, scaled up ... There was no handle. No doorknob. A
       small black panel beside the right-hand door at chest height" / "The
       gravel had been raked ... The grass at the edge of the gravel was cut."
    It was seven stripes of cedar and grey glass (a parking garage), two flat
    door slabs, a box van, ten small spruce and a town's rooflines beside an
    undeveloped headland. Now: a stone plinth and steps; the ground floor in
    cedar siding with corner boards; ledged-and-braced plank doors on iron
    strap hinges, an open-door variant (__cedar_tower_exterior_open, "The
    double-doors eased open"); floors 2-6 one smart-glass skin, its seams the
    mullions and floor lines, rendering the setting — ocean on the seaward
    (W) face, cedars and sky on the S and E; the seventh floor real glass
    (the engine's glass pass) round a garden of beds and small trees, its
    roof glass on a grid; raked gravel, a mown edge, rough grass to a ring
    of tall cedars; Old Yachats Road arriving from the south-west; Tem's
    wagon at the clearing's edge.
    NEXT (draft 4): the rendering's sky to follow the scene's hour; moss on
    the plinth's north side; the drone that rakes caught mid-row; the lobby
    beyond the open doors (now a lit cedar vestibule)."""
    from _props.geometry import make_prism, make_blob, make_tube, join_prefix
    from _props.trees import make_conifer
    from _props.vehicles import make_car
    import math, random
    rnd = random.Random(476)
    X = 45.0
    TY, TS = 18.0, 21.3
    H = TS / 2.0
    YS, XW, XE, YN = TY - H, X - H, X + H, TY + H          # the four faces: S 7.35, W 34.35, E 55.65, N 28.65
    STONE, STONE_DK, MORTAR = (0.50, 0.48, 0.44, 1.0), (0.40, 0.38, 0.35, 1.0), (0.33, 0.31, 0.29, 1.0)
    SIDING, SIDING_DK = (0.56, 0.40, 0.26, 1.0), (0.40, 0.28, 0.18, 1.0)
    IRON = (0.10, 0.10, 0.11, 1.0)
    FD = 0.6                                           # the plinth's exposed height; the ground floor stands on it
    G1 = FD + 4.0                                      # top of the ground floor (cedar) / foot of the glass
    FLOOR_H = 3.7
    G7 = G1 + 5 * FLOOR_H                              # foot of the seventh floor
    TOP = G7 + FLOOR_H
    # ── the clearing ──
    make_box("Ext_Grass_Mown", (X, 3.0, -0.012), (40.0, 68.0, 0.024), (0.36, 0.46, 0.26, 1.0))
    make_box("Ext_Gravel", (X, 3.0, 0.0), (34.0, 58.0, 0.06), GRAVEL)          # x 28..62, y -26..32
    # "The gravel had been raked": the tines' rows, east-west across the front
    for k in range(60):
        yy = -25.4 + k * 0.55
        if yy > YS - 0.4:
            break
        make_box(f"Ext_Gravel_Rake_{k}", (X, yy, 0.032), (33.2, 0.04, 0.004), (0.50, 0.46, 0.405, 1.0))   # the tines' shadow, not stripes
    # rough grass beyond the mown edge, to the trees
    for i in range(70):
        ang = rnd.uniform(0.0, 2.0 * math.pi)
        rx, ry = 21.5 + rnd.uniform(0.0, 4.0), 35.5 + rnd.uniform(0.0, 4.0)
        gx, gy = X + rx * math.cos(ang), 3.0 + ry * math.sin(ang)
        if gy < -30.0 and 26.0 < gx < 36.0:
            continue                                   # the road's mouth
        r = rnd.uniform(0.3, 0.7)
        make_blob(f"Ext_Rough_Grass_{i}", (gx, gy, r * 0.3 - 0.04), r, ((0.40, 0.44, 0.26, 1.0), (0.32, 0.40, 0.24, 1.0), (0.46, 0.46, 0.30, 1.0))[i % 3],
                  noise=0.35, seed=4760 + i, rings=3, segments=6, squash=0.45)
    # Old Yachats Road arrives from the south-west ("The road ended in a
    # clearing on top of the bluff"), the aged asphalt of the highway set
    OLD = (0.31, 0.31, 0.30, 1.0)
    ra, rb = (31.5, -25.8), (12.0, -52.0)
    rl = math.hypot(rb[0] - ra[0], rb[1] - ra[1])
    ryaw = math.atan2(rb[1] - ra[1], rb[0] - ra[0])
    make_rot_box("Ext_Old_Road_Asphalt", ((ra[0] + rb[0]) / 2.0, (ra[1] + rb[1]) / 2.0, 0.01), (rl, 4.8, 0.03), OLD, yaw=ryaw)
    for k in range(12):
        t = (k + 0.5) / 12.0
        make_rot_box(f"Ext_Old_Road_Crack_{k}", (ra[0] + (rb[0] - ra[0]) * t + rnd.uniform(-1.5, 1.5) * math.sin(ryaw),
                                                 ra[1] + (rb[1] - ra[1]) * t - rnd.uniform(-1.5, 1.5) * math.cos(ryaw), 0.0265),
                     (rnd.uniform(0.8, 2.4), 0.05, 0.004), (0.18, 0.18, 0.18, 1.0), yaw=ryaw + rnd.uniform(-0.3, 0.3))
    # ── the cedars round the clearing ("Trees on either side had not been cut
    # back"; "the inland face showing the cedars"): a ring of tall trees,
    # thick to the north, east and south, the old road's cut through them
    trees = []
    for i in range(46):
        ang = 2.0 * math.pi * i / 46.0 + rnd.uniform(-0.05, 0.05)
        rx, ry = 27.5 + rnd.uniform(0.0, 6.0), 41.0 + rnd.uniform(0.0, 6.0)
        tx, ty = X + rx * math.cos(ang), 3.0 + ry * math.sin(ang)
        # the road's line out to the south-west stays open
        d_road = abs((rb[0] - ra[0]) * (ra[1] - ty) - (ra[0] - tx) * (rb[1] - ra[1])) / rl
        if d_road < 5.0 and ty < -20.0:
            continue
        trees.append((tx, ty, rnd.uniform(22.0, 32.0)))
    for i in range(30):                                # a second row behind
        ang = 2.0 * math.pi * (i + 0.5) / 30.0
        tx, ty = X + 38.0 * math.cos(ang), 3.0 + 52.0 * math.sin(ang)
        d_road = abs((rb[0] - ra[0]) * (ra[1] - ty) - (ra[0] - tx) * (rb[1] - ra[1])) / rl
        if d_road < 6.0 and ty < -20.0:
            continue
        trees.append((tx, ty, rnd.uniform(26.0, 36.0)))
    for k in range(9):                                 # along the old road, both sides
        t = 0.18 + k * 0.1
        for side in (-1, 1):
            off = side * rnd.uniform(4.4, 6.0)
            trees.append((ra[0] + (rb[0] - ra[0]) * t - off * math.sin(ryaw), ra[1] + (rb[1] - ra[1]) * t + off * math.cos(ryaw),
                          rnd.uniform(18.0, 26.0)))
    # depth: a forest is rows deep — through one ring the low sun showed
    # between every trunk (bright slots round the clearing). A third row,
    # young trees in the gaps (crowns from 2 m), salal and huckleberry under
    for i in range(44):
        ang = 2.0 * math.pi * (i + 0.25) / 44.0
        tx, ty = X + (45.0 + rnd.uniform(-3.0, 3.0)) * math.cos(ang), 3.0 + (60.0 + rnd.uniform(-3.0, 3.0)) * math.sin(ang)
        d_road = abs((rb[0] - ra[0]) * (ra[1] - ty) - (ra[0] - tx) * (rb[1] - ra[1])) / rl
        if d_road < 6.0 and ty < -20.0:
            continue
        trees.append((tx, ty, rnd.uniform(26.0, 36.0)))
    young = []
    for i in range(52):
        ang = 2.0 * math.pi * (i + 0.6) / 52.0
        tx, ty = X + (30.5 + rnd.uniform(-1.5, 3.5)) * math.cos(ang), 3.0 + (44.0 + rnd.uniform(-1.5, 3.5)) * math.sin(ang)
        d_road = abs((rb[0] - ra[0]) * (ra[1] - ty) - (ra[0] - tx) * (rb[1] - ra[1])) / rl
        if d_road < 4.5 and ty < -20.0:
            continue
        young.append((tx, ty, rnd.uniform(6.5, 11.0)))
    young = [t for t in young if not (t[0] - 0.4 * t[2] < 10.5 and -4.0 - 0.4 * t[2] < t[1] < 16.0 + 0.4 * t[2])
             and not any(math.hypot(t[0] - bx_, t[1] - by_) < 9.0 for bx_, by_ in ((10.5, 30.0), (15.0, 38.0), (3.5, 35.0)))]
    # the west of the ring stays low (the interior floors stand there in this
    # GLB): young trees only, so the low sun over the sea does not show through
    for i in range(10):
        young.append((13.2 + (i % 2) * 1.6, -3.0 + i * 2.0, 6.0 + (i % 3) * 0.6))
    for i in range(14):                                # and the south-west arc, where the low sun came through
        ang = math.radians(196.0 + i * 4.6)
        young.append((X + (29.0 + (i % 3) * 1.4) * math.cos(ang), 3.0 + (42.5 + (i % 2) * 1.6) * math.sin(ang), 7.0 + (i % 4) * 0.9))
    for i, (tx, ty, th) in enumerate(young):
        make_conifer(f"Ext_Forest_Young_{i}", tx, ty, th, (0.17, 0.28, 0.19, 1.0), (0.30, 0.24, 0.18, 1.0), skirt=0.36, z0=-0.9)
    for i in range(64):
        ang = 2.0 * math.pi * (i + 0.3) / 64.0
        bx_, by_ = X + (28.5 + rnd.uniform(0.0, 4.0)) * math.cos(ang), 3.0 + (42.0 + rnd.uniform(0.0, 4.0)) * math.sin(ang)
        d_road = abs((rb[0] - ra[0]) * (ra[1] - by_) - (ra[0] - bx_) * (rb[1] - ra[1])) / rl
        if (d_road < 4.0 and by_ < -20.0) or (bx_ < 11.0 and -4.0 < by_ < 16.0):
            continue
        r = rnd.uniform(1.2, 2.3)
        make_blob(f"Ext_Forest_Salal_{i}", (bx_, by_, r * 0.45 - 0.1), r, ((0.20, 0.32, 0.20, 1.0), (0.24, 0.36, 0.22, 1.0), (0.17, 0.27, 0.18, 1.0))[i % 3],
                  noise=0.3, seed=4950 + i, rings=4, segments=8, squash=0.6)
    # tall cedars at the clearing's west edge, set where their crowns stay
    # clear of the interior floors: they hide that block from the clearing
    for i, (tx, ty, th) in enumerate(((21.4, -3.0, 30.0), (20.8, 3.0, 31.0), (21.8, 9.0, 29.0), (21.0, 14.5, 30.0))):
        if tx - 0.29 * th >= 11.0:
            make_conifer(f"Ext_Forest_West_{i}", tx, ty, th, SITKA if i % 2 else (0.14, 0.24, 0.17, 1.0), (0.30, 0.24, 0.18, 1.0), skirt=0.24)
    # behind the rows, the forest going on: a treeline wall all round but
    # the sea side, so no slot of sky shows between trunks
    from _props.detail import make_far_bands
    make_far_bands("Ext_Forest_Backdrop", (0.12, 0.20, 0.14), [(72.0, 80.0, 24.0, 1.0)], profile="treeline", sides="NSE", cx=X, cy=3.0)
    # (the interior floors stand at x 0 in this GLB, the portal floor 18 m
    # wide: no crown may reach them)
    # (nor crowd build_horizon's bluff cedars at (10.5, 30) and (15, 38))
    near_bluff = lambda t, r: any(math.hypot(t[0] - bx_, t[1] - by_) < r for bx_, by_ in ((10.5, 30.0), (15.0, 38.0), (3.5, 35.0)))
    trees = [t for t in trees if not (t[0] - 0.29 * t[2] < 11.0 and -4.0 - 0.29 * t[2] < t[1] < 16.0 + 0.29 * t[2]) and not near_bluff(t, 9.0)]
    for i, (tx, ty, th) in enumerate(trees):
        make_conifer(f"Ext_Forest_Tree_{i}", tx, ty, th, SITKA if i % 2 else (0.14, 0.24, 0.17, 1.0), (0.30, 0.24, 0.18, 1.0), skirt=0.24)
    # ── THE TOWER ──
    # the stone foundation: a plinth proud of the siding by 25 cm, its courses
    make_box("Tower_Foundation", (X, TY, (FD - 0.4) / 2.0), (TS + 0.5, TS + 0.5, FD + 0.4), STONE)
    for zc in (0.20, 0.40):
        for nm, c, sz in (("S", (X, YS - 0.25 - 0.004, zc), (TS + 0.5, 0.008, 0.025)),
                          ("W", (XW - 0.25 - 0.004, TY, zc), (0.008, TS + 0.5, 0.025)),
                          ("E", (XE + 0.25 + 0.004, TY, zc), (0.008, TS + 0.5, 0.025))):
            make_box(f"Tower_Foundation_Course_{nm}_{int(zc * 100)}", c, sz, MORTAR)
    for k in range(36):                                # the head joints, staggered course to course
        u = -H - 0.25 + 0.3 + k * 0.6
        for row, (z0, z1) in enumerate(((0.0, 0.20), (0.20, 0.40), (0.40, FD))):
            uu = u + (0.3 if row % 2 else 0.0)
            if uu > H + 0.2 or abs(uu) < 2.2:
                continue                               # (behind the steps)
            make_box(f"Tower_Foundation_Joint_{row}_{k}", (X + uu, YS - 0.25 - 0.004, (z0 + z1) / 2.0), (0.025, 0.008, z1 - z0 - 0.03), MORTAR)
    # the stone steps up to the doors, the top one the landing
    for k, (y0, y1) in enumerate(((YS - 2.05, YS - 1.65), (YS - 1.65, YS - 1.25), (YS - 1.25, YS - 0.25))):   # the top one a 1 m landing
        make_box(f"Tower_Step_{k}", (X, (y0 + y1) / 2.0, (0.2 * (k + 1) - 0.1) / 2.0), (4.4 - 0.3 * k, y1 - y0, 0.2 * (k + 1) + 0.1),
                 STONE if k % 2 else STONE_DK)
    # the ground floor: cedar siding, the doorway cut through it (a cedar
    # vestibule behind, lit, for the open doors)
    DW, DH = 2.7, 3.1                                   # the doorway: 2.7 x 3.1 m, "scaled up"
    DX0, DX1 = X - DW / 2.0, X + DW / 2.0
    VD = 3.2                                            # the vestibule's depth
    make_box("Tower_Siding_W", ((XW + DX0) / 2.0, YS + VD / 2.0, (FD + G1) / 2.0), (DX0 - XW, VD, G1 - FD), SIDING)
    make_box("Tower_Siding_E", ((DX1 + XE) / 2.0, YS + VD / 2.0, (FD + G1) / 2.0), (XE - DX1, VD, G1 - FD), SIDING)
    make_box("Tower_Siding_Head", (X, YS + VD / 2.0, (FD + DH + G1) / 2.0), (DW, VD, G1 - FD - DH), SIDING)
    make_box("Tower_Siding_Core", (X, (YS + VD + YN) / 2.0, (FD + G1) / 2.0), (TS, YN - YS - VD, G1 - FD), SIDING)
    VEST = (0.66, 0.50, 0.33, 1.0)                     # polished cedar, lit
    make_box("Tower_Vestibule_Floor", (X, YS + VD / 2.0, FD + 0.01), (DW, VD, 0.02), (0.60, 0.44, 0.29, 1.0))
    make_box("Tower_Vestibule_Back", (X, YS + VD - 0.01, FD + DH / 2.0), (DW, 0.02, DH), VEST)
    # the courses of the siding (S, W and E faces) and the corner boards
    nz = int((G1 - FD - 0.2) / 0.22)
    for k in range(nz):
        zc = FD + 0.22 + k * 0.22
        segs = [(XW + 0.1, DX0 - 0.2), (DX1 + 0.2, XE - 0.1)] if zc < FD + DH + 0.2 else [(XW + 0.1, XE - 0.1)]
        for si, (a0, a1) in enumerate(segs):
            make_box(f"Tower_Siding_Course_S_{k}_{si}", ((a0 + a1) / 2.0, YS - 0.006, zc), (a1 - a0, 0.012, 0.022), SIDING_DK)
        for nm, xx in (("W", XW - 0.006), ("E", XE + 0.006)):
            make_box(f"Tower_Siding_Course_{nm}_{k}", (xx, TY, zc), (0.012, TS - 0.2, 0.022), SIDING_DK)
    for nm, (cx, cy) in (("SW", (XW, YS)), ("SE", (XE, YS)), ("NW", (XW, YN)), ("NE", (XE, YN))):
        make_box(f"Tower_Corner_Board_{nm}", (cx, cy, (FD + G1) / 2.0), (0.22, 0.22, G1 - FD), SIDING_DK)
    make_box("Tower_Belt", (X, TY, G1 + 0.12), (TS + 0.24, TS + 0.24, 0.24), CEDAR_DK)
    # the doorway's casing
    for nm, c, sz in (("L", (DX0 - 0.10, YS - 0.03, FD + DH / 2.0), (0.20, 0.06, DH)),     # the head caps them (they met coplanar)
                      ("R", (DX1 + 0.10, YS - 0.03, FD + DH / 2.0), (0.20, 0.06, DH)),
                      ("Head", (X, YS - 0.035, FD + DH + 0.12), (DW + 0.6, 0.07, 0.24))):
        make_box(f"Tower_Door_Casing_{nm}", c, sz, SIDING_DK)
    # THE DOORS: two leaves of vertical planks, three ledges, a brace between
    # each pair, black iron strap hinges, no handle. Closed in the exterior,
    # swung in against the vestibule's sides in the _open view.
    LW, LH = DW / 2.0 - 0.01, DH - 0.02

    def leaf(tag, side, opened):
        sfx = "__cedar_tower_exterior_open" if opened else "__cedar_tower_exterior"
        hinge_x = DX0 if side < 0 else DX1
        if opened:
            # swung in: its face along the vestibule's side, hinge at the front
            cx, cy = hinge_x - side * 0.04, YS + 0.06 + LW / 2.0
            make_box(f"Tower_Door_Leaf_{tag}{sfx}", (cx, cy, FD + LH / 2.0 + 0.01), (0.07, LW, LH), CEDAR)
            for k, zz in enumerate((0.40, LH / 2.0, LH - 0.40)):
                make_box(f"Tower_Door_Ledge_{tag}_{k}{sfx}", (cx - side * 0.05, cy, FD + zz), (0.035, LW - 0.10, 0.16), CEDAR_DK)
            return
        cx = hinge_x - side * LW / 2.0
        fy = YS - 0.035                                # the leaf's face, set 3.5 cm proud of the siding
        make_box(f"Tower_Door_Leaf_{tag}{sfx}", (cx, YS - 0.0, FD + LH / 2.0 + 0.01), (LW, 0.07, LH), CEDAR)
        for g in range(1, 5):                           # the plank joints
            make_box(f"Tower_Door_Groove_{tag}_{g}{sfx}", (cx - LW / 2.0 + g * LW / 5.0, fy - 0.002, FD + LH / 2.0 + 0.01), (0.012, 0.004, LH - 0.02), SIDING_DK)
        lz = (0.40, LH / 2.0, LH - 0.40)
        for k, zz in enumerate(lz):
            make_box(f"Tower_Door_Ledge_{tag}_{k}{sfx}", (cx, fy - 0.0175, FD + zz), (LW - 0.10, 0.035, 0.16), CEDAR_DK)
            # the strap hinge across the ledge from the hinge side, its knuckle at the edge
            make_box(f"Tower_Door_Strap_{tag}_{k}{sfx}", (hinge_x - side * 0.40, fy - 0.040, FD + zz), (0.78, 0.010, 0.055), IRON)
            make_cyl(f"Tower_Door_Pintle_{tag}_{k}{sfx}", (hinge_x - side * 0.02, fy - 0.030, FD + zz), 0.022, 0.10, IRON, segments=8)
        for k in range(2):                              # the braces, rising toward the hinge side
            z0_, z1_ = FD + lz[k] + 0.10, FD + lz[k + 1] - 0.10
            run = LW - 0.30
            ln = math.hypot(run, z1_ - z0_)
            ang = math.atan2(z1_ - z0_, run)
            make_rot_box(f"Tower_Door_Brace_{tag}_{k}{sfx}", (cx, fy - 0.0175, (z0_ + z1_) / 2.0), (ln, 0.035, 0.14), CEDAR_DK,
                         pitch=(ang if side < 0 else -ang))
    for opened in (False, True):
        leaf("L", -1, opened)
        leaf("R", 1, opened)
    # (pass 366) "A small black panel beside the right-hand door at chest
    # height — the size of a deck of cards ... A small green LED at the
    # panel's corner lit up." Chest height over the landing (FD).
    PX = DX1 + 0.55
    make_box("Palm_Panel", (PX, YS - 0.012, FD + 1.30), (0.065, 0.024, 0.09), (0.05, 0.05, 0.06, 1.0))
    make_box("Palm_Panel_LED", (PX + 0.022, YS - 0.026, FD + 1.30 + 0.034), (0.012, 0.006, 0.012), GREEN_LED)
    # FLOORS 2-6: one smart-glass skin. Its seams — the mullions every 3 m
    # and the floor lines — are "what gives the rendering away up close".
    GLASS_DK = (0.16, 0.21, 0.25, 1.0)
    make_box("Tower_Glass_Core", (X, TY, (G1 + G7) / 2.0), (TS, TS, G7 - G1), GLASS_DK)
    SKY, SKY_HI = (0.66, 0.72, 0.76, 1.0), (0.74, 0.79, 0.82, 1.0)
    # S face: the setting behind it — the cedars north of the tower against the sky
    make_box("Tower_Render_S_Sky", (X, YS - 0.006, (G1 + G7) / 2.0), (TS - 0.02, 0.008, G7 - G1 - 0.02), SKY)
    make_box("Tower_Render_S_SkyHi", (X, YS - 0.011, G7 - 3.0), (TS - 0.02, 0.004, 5.9), SKY_HI)
    make_box("Tower_Render_E_Sky", (XE + 0.006, TY, (G1 + G7) / 2.0), (0.008, TS - 0.02, G7 - G1 - 0.02), SKY)

    def render_cedars(face, n, seed):
        rr = random.Random(seed)
        us = sorted(rr.uniform(-H + 0.6, H - 0.6) for _ in range(n))
        for i, u in enumerate(us):
            top = rr.uniform(G1 + 7.0, G7 - 1.2)
            w = rr.uniform(2.8, 4.8)
            off = 0.015 + 0.002 * i
            h_ = top - G1
            # a cedar's tiers, not a spike: the outline steps in at each tier
            right = [(w / 2.0, 0.08 * h_), (w * 0.16, 0.24 * h_), (w * 0.40, 0.27 * h_), (w * 0.12, 0.47 * h_), (w * 0.32, 0.50 * h_),
                     (w * 0.09, 0.68 * h_), (w * 0.22, 0.71 * h_), (w * 0.05, 0.88 * h_)]
            poly = [(-w * 0.06, 0.0), (w * 0.06, 0.0)] + right + [(0.0, h_)] + [(-u, v) for (u, v) in reversed(right)]
            col = ((0.16, 0.27, 0.19, 1.0), (0.12, 0.22, 0.16, 1.0), (0.20, 0.31, 0.22, 1.0))[i % 3]
            if face == "S":
                make_prism(f"Tower_Render_S_Cedar_{i}", (X + u, YS - off, G1 + 0.01), poly, 0.004, col, axis="Y")
            else:
                make_prism(f"Tower_Render_E_Cedar_{i}", (XE + off, TY - u, G1 + 0.01), poly, 0.004, col, axis="X")
        floor_col = (0.12, 0.18, 0.13, 1.0)
        if face == "S":
            make_box("Tower_Render_S_Understory", (X, YS - 0.052, G1 + 1.6), (TS - 0.02, 0.004, 3.2), floor_col)
        else:
            make_box("Tower_Render_E_Understory", (XE + 0.054, TY, G1 + 1.6), (0.004, TS - 0.02, 3.2), floor_col)
    render_cedars("S", 16, 4761)
    render_cedars("E", 18, 4762)
    # W face (seaward): the ocean — the sea to a horizon, the swells closing
    # toward it, the sky (whose wave period, up close, is not the sea's)
    HZ = G1 + 8.6
    make_box("Tower_Render_W_Sea", (XW - 0.006, TY, (G1 + HZ) / 2.0), (0.008, TS - 0.02, HZ - G1), (0.30, 0.42, 0.48, 1.0))
    make_box("Tower_Render_W_Sky", (XW - 0.006, TY, (HZ + G7) / 2.0), (0.008, TS - 0.02, G7 - HZ - 0.01), SKY)
    make_box("Tower_Render_W_Horizon", (XW - 0.012, TY, HZ), (0.004, TS - 0.02, 0.10), (0.80, 0.82, 0.80, 1.0))
    for k, zz in enumerate((G1 + 0.8, G1 + 2.6, G1 + 4.1, G1 + 5.4, G1 + 6.4, G1 + 7.2, G1 + 7.8, G1 + 8.2)):
        make_box(f"Tower_Render_W_Swell_{k}", (XW - 0.012, TY + rnd.uniform(-1.5, 1.5), zz), (0.004, TS - 1.5 - k * 0.6, 0.06 + 0.10 * (1.0 - k / 8.0)),
                 (0.78, 0.84, 0.84, 1.0))
    # the seams: mullions on S, W, E, the floor lines all round
    for k in range(1, 7):
        u = -H + k * TS / 7.0
        for nm, c, sz in (("S", (X + u, YS - 0.06, (G1 + TOP) / 2.0), (0.10, 0.08, TOP - G1)),
                          ("W", (XW - 0.06, TY + u, (G1 + TOP) / 2.0), (0.08, 0.10, TOP - G1)),
                          ("E", (XE + 0.06, TY + u, (G1 + TOP) / 2.0), (0.08, 0.10, TOP - G1)),
                          ("N", (X + u, YN + 0.06, (G1 + TOP) / 2.0), (0.10, 0.08, TOP - G1))):
            make_box(f"Tower_Mullion_{nm}{k}", c, sz, (0.12, 0.12, 0.13, 1.0))
    for f in range(1, 6):
        zz = G1 + f * FLOOR_H
        for nm, c, sz in (("S", (X, YS - 0.05, zz), (TS + 0.2, 0.10, 0.20)), ("N", (X, YN + 0.05, zz), (TS + 0.2, 0.10, 0.20)),
                          ("W", (XW - 0.05, TY, zz), (0.10, TS, 0.20)), ("E", (XE + 0.05, TY, zz), (0.10, TS, 0.20))):
            make_box(f"Tower_FloorLine_{f}_{nm}", c, sz, (0.12, 0.12, 0.13, 1.0))
    for nm, c, sz in (("S", (X, YS - 0.06, G1 + 0.05), (TS + 0.24, 0.12, 0.10)),):
        make_box(f"Tower_FloorLine_0_{nm}", c, sz, (0.12, 0.12, 0.13, 1.0))
    # THE SEVENTH FLOOR: glass-walled, glass-roofed, the garden inside
    GL = (0.72, 0.80, 0.84, 0.20)                      # the engine's glass pass draws it see-through
    make_box("Tower_Seventh_Slab", (X, TY, G7 + 0.10), (TS, TS, 0.20), (0.30, 0.26, 0.22, 1.0))
    for nm, c, sz in (("S", (X, YS + 0.02, G7 + FLOOR_H / 2.0 + 0.1), (TS - 0.04, 0.03, FLOOR_H - 0.2)),
                      ("N", (X, YN - 0.02, G7 + FLOOR_H / 2.0 + 0.1), (TS - 0.04, 0.03, FLOOR_H - 0.2)),
                      ("W", (XW + 0.02, TY, G7 + FLOOR_H / 2.0 + 0.1), (0.03, TS - 0.04, FLOOR_H - 0.2)),
                      ("E", (XE - 0.02, TY, G7 + FLOOR_H / 2.0 + 0.1), (0.03, TS - 0.04, FLOOR_H - 0.2))):
        make_box(f"Tower_Seventh_Glass_{nm}", c, sz, GL)
    make_box("Tower_Seventh_Sill", (X, YS - 0.04, G7 + 0.20), (TS + 0.2, 0.12, 0.20), (0.12, 0.12, 0.13, 1.0))
    make_box("Tower_Roof_Glass", (X, TY, TOP - 0.02), (TS - 0.04, TS - 0.04, 0.03), GL)
    for k in range(1, 7):                              # the roof's grid
        u = -H + k * TS / 7.0
        make_box(f"Tower_Roof_Rib_X{k}", (X + u, TY, TOP + 0.03), (0.10, TS, 0.10), (0.12, 0.12, 0.13, 1.0))
        make_box(f"Tower_Roof_Rib_Y{k}", (X, TY + u, TOP + 0.03), (TS, 0.10, 0.10), (0.12, 0.12, 0.13, 1.0))
    for nm, c, sz in (("S", (X, YS, TOP + 0.08), (TS + 0.3, 0.30, 0.22)), ("N", (X, YN, TOP + 0.08), (TS + 0.3, 0.30, 0.22)),
                      ("W", (XW, TY, TOP + 0.08), (0.30, TS - 0.3, 0.22)), ("E", (XE, TY, TOP + 0.08), (0.30, TS - 0.3, 0.22))):
        make_box(f"Tower_Roof_Rim_{nm}", c, sz, CEDAR_DK)
    # "The vegetation moved gently against the glass": a planting strip
    # right inside the S, W and E glass, leaf to the glass from the sill up,
    # so from the clearing the garden is IN the top floor's walls
    for side, (ax, ay, dx_, dy_) in (("S", (X - H + 1.0, YS + 0.85, 1.0, 0.0)), ("W", (XW + 0.85, TY - H + 1.0, 0.0, 1.0)),
                                     ("E", (XE - 0.85, TY - H + 1.0, 0.0, 1.0))):
        n_ = 19
        for j in range(n_):
            t = j * (TS - 2.0) / (n_ - 1)
            px, py = ax + dx_ * t, ay + dy_ * t
            for lvl, (lz, lr) in enumerate(((0.75, 0.55), (1.55, 0.50), (2.35, 0.42))):
                if lvl == 2 and j % 2:
                    continue
                r = lr * rnd.uniform(0.85, 1.15)
                make_blob(f"Garden_Glass_Leaf_{side}_{j}_{lvl}", (px + rnd.uniform(-0.15, 0.15) * dy_, py + rnd.uniform(-0.15, 0.15) * dx_, G7 + 0.2 + lz), r,
                          ((0.26, 0.48, 0.28, 1.0), (0.34, 0.54, 0.30, 1.0), (0.22, 0.42, 0.25, 1.0))[(j + lvl) % 3],
                          noise=0.32, seed=5100 + j * 3 + lvl + {"S": 0, "W": 200, "E": 400}[side], rings=4, segments=7, squash=0.85)
    # the garden: raised cedar beds, low planting, small trees under the glass
    gz = G7 + 0.20
    for i, (bx_, by_, bw, bd) in enumerate(((-6.5, -6.0, 5.0, 1.6), (0.0, -6.5, 4.0, 1.6), (6.5, -6.0, 5.0, 1.6),
                                            (-6.0, 1.0, 1.6, 6.0), (6.0, 1.0, 1.6, 6.0), (0.0, 6.0, 9.0, 1.6))):
        make_box(f"Garden_Bed_{i}", (X + bx_, TY + by_, gz + 0.25), (bw, bd, 0.50), CEDAR)
        for j in range(int(max(bw, bd) / 0.9)):
            t = (j + 0.5) / int(max(bw, bd) / 0.9)
            px = X + bx_ + ((t - 0.5) * bw if bw >= bd else 0.0)
            py = TY + by_ + ((t - 0.5) * bd if bd > bw else 0.0)
            r = rnd.uniform(0.35, 0.6)
            make_blob(f"Garden_Plant_{i}_{j}", (px, py, gz + 0.5 + r * 0.45), r,
                      ((0.26, 0.48, 0.28, 1.0), (0.34, 0.54, 0.30, 1.0), (0.22, 0.40, 0.26, 1.0))[(i + j) % 3],
                      noise=0.3, seed=4800 + i * 20 + j, rings=4, segments=7, squash=0.8)
    for i, (tx, ty) in enumerate(((-3.0, -2.0), (3.2, -1.5), (-1.0, 3.0), (7.5, -3.0), (-8.0, 3.5))):
        th = 2.6 + (i % 3) * 0.35                       # small trees on the slab (make_broadleaf stands on z 0)
        make_cyl(f"Garden_Tree_{i}_Trunk", (X + tx, TY + ty, gz + th * 0.30), 0.07, th * 0.60, (0.36, 0.28, 0.20, 1.0), segments=7)
        for li, (lx, ly, lz, lr) in enumerate(((0.0, 0.0, 0.72, 0.62), (0.35, 0.15, 0.62, 0.45), (-0.30, -0.20, 0.64, 0.48), (0.05, -0.30, 0.86, 0.40))):
            make_blob(f"Garden_Tree_{i}_Crown_{li}", (X + tx + lx, TY + ty + ly, gz + th * lz), th * lr / 1.6,
                      ((0.28, 0.46, 0.26, 1.0), (0.24, 0.40, 0.23, 1.0))[(i + li) % 2], noise=0.28, seed=4900 + i * 4 + li, rings=4, segments=7, squash=0.85)
    # ── Tem's wagon, stopped at the edge of the clearing where the road comes in
    make_car("Tem_Wagon", 34.2, -20.5, 4.6, (0.48, 0.36, 0.26, 1.0), wagon=True, along="Y", z0=0.03)
    for pfx in ("Ext_Gravel_Rake", "Ext_Rough_Grass", "Ext_Old_Road_Crack", "Ext_Forest_Tree", "Tower_Foundation_Joint",
                "Tower_Foundation_Course", "Tower_Siding_Course", "Tower_Render_S_Cedar", "Tower_Render_E_Cedar",
                "Tower_Render_W_Swell", "Tower_Mullion", "Tower_FloorLine", "Tower_Roof_Rib", "Garden_Plant", "Garden_Tree",
                "Ext_Forest_Young", "Ext_Forest_Salal", "Ext_Forest_West", "Garden_Glass_Leaf"):
        join_prefix(pfx)


def build_drone_dock_2026_08():
    """THE FOUNDATION'S DRONE DOCK (user 2026-08-12). Oneironautics
    owns the drones; this is where they come home. Canon: "by
    six-thirty they were all docked and the sky over Smolvud was
    empty" — so the rack sits in the tower clearing, cedar-framed
    like everything else Oneironautics builds, with one cradle
    empty because that unit is still out over the town.
    """
    from _props.drones import make_drone_dock, make_drone
    X = 45.0
    # Rack on the clearing's north edge, beside the tower's base.
    make_drone_dock("DroneDock", X - 14.0, 5.0, 0.06, n=3,   # clear of the 21 m tower (2026-10-21)
                    occupied=(True, False, True))
    # The late unit on approach — low over the gravel, arm stowed,
    # nose toward the empty cradle.
    make_drone("Drone_Inbound", X - 6.4, 1.2, 3.9)
    # A second working the tower's fourth-floor glass band (they
    # repair the buildings they belong to).
    make_drone("Drone_Glazier", X + 5.2, 6.3, 12.4, arm_down=True,
               yaw_flip=True)


def build_wear_personality_2026_08():
    """D2 WEAR — draft 4 (queued in the ledger). Whose feet: a
    small crew that CROSSES the lobby, WORKS the studio, LIVES in
    the quarters, and WAITS at the portal door.

    The building's personality is kept-but-lived-in: the lobby is
    polished cedar with exactly one line of traffic through it
    (nobody lingers — the reception desk has no chair); the studio
    wears at the chairs and along the rack wall; the quarters seat
    twelve and wear at five; and on the portal landing the wear
    STOPS at the unmarked door — a polished waiting crescent in
    front of it, and a hand-smudge under the little window, and
    nothing past that.
    """
    from _props.detail import make_traffic_wear, make_floor_stain
    cedar_dk = (0.44, 0.31, 0.20, 1.0)   # traffic on cedar
    cedar_pale = (0.62, 0.48, 0.33, 1.0) # polish/scrape
    # ── LOBBY (z 0) · one line, door to stairs ──
    make_traffic_wear("Wear_Lobby_Line",
                      [(0.0, 0.8), (1.2, 3.0), (2.5, 5.2)],
                      width=0.5, floor_z=0.05, tint=cedar_dk)   # (pass 386) the floor's TOP: 0.02 is inside the slab
    # Dust band on the empty reception desk — no chair, no hands.
    make_box("Wear_Reception_Dust", (0.0, 5.2, 1.155), (2.6, 0.7, 0.004),
             (0.58, 0.45, 0.32, 1.0))
    # The brass handrail worn BRIGHT at the grab points (bottom +
    # top), duller mid-run.
    for gz, gy in ((1.55, 4.9), (1.55, 6.7)):   # on the rail (z 1.55; 2026-09-22: one hung 0.8 m over it)
        make_cyl("Wear_Handrail_Bright_%d" % int(gy * 10), (2.85, gy, gz),
                 0.032, 0.30, (0.85, 0.72, 0.42, 1.0), segments=8, axis='Y')
    # ── STUDIO (z 5) · chairs and the rack line ──
    for ci, (cx2, cy2) in enumerate(((-2.2, 4.2), (2.2, 4.2))):
        for di, (dx2, dy2) in enumerate(((-0.75, -0.5), (0.75, -0.5),
                                         (-0.75, 0.5), (0.75, 0.5))):
            make_floor_stain("Wear_Studio_Chair_%d_%d" % (ci, di),
                             (cx2 + dx2, cy2 + dy2 - 0.65), radius=0.24,
                             floor_z=5.05, tint=cedar_dk, segments=8)
    # One desk carries coffee rings; the others don't — one person
    # on the crew drinks at their desk, and everyone knows who.
    for ri2, (rx2, ry2) in enumerate(((-2.95, 3.55), (-2.88, 3.75), (-3.05, 3.68))):
        make_cyl("Wear_Desk_Ring_%d" % ri2, (rx2, ry2, 5.7465), 0.042, 0.003,
                 (0.38, 0.26, 0.16, 1.0), segments=8)
    # The service line along the racks — feet that tend machines.
    make_traffic_wear("Wear_Rack_Line",
                      [(-4.6, 7.9), (0.0, 7.9), (4.6, 7.9)],
                      width=0.4, floor_z=5.05, tint=cedar_dk)
    # ── QUARTERS (z 10) · a table for twelve, a crew of five ──
    # Five seats worn, seven clean: the table was built for the
    # company they hoped for.
    for si2, (sx2, sy2) in enumerate(((-1.4, 3.2), (-0.7, 3.2), (0.0, 3.2),
                                      (0.7, 3.2), (-1.4, 4.4))):
        make_floor_stain("Wear_Seat_%d" % si2, (sx2, sy2), radius=0.17,
                         floor_z=10.05, tint=cedar_dk, segments=8)
    # Kettle ring on the wood-stove top (a different household's
    # kettle than the cabin's, same physics).
    make_cyl("Wear_QStove_Ring", (5.0, 6.6, 10.8374), 0.095, 0.004,
             (0.10, 0.10, 0.11, 1.0), segments=10)
    # ── PORTAL LANDING (z 15) · the wear STOPS at the door ──
    make_traffic_wear("Wear_Landing_Line",
                      [(0.0, 0.4), (0.0, 1.6)],
                      width=0.42, floor_z=15.04, tint=cedar_dk)
    # The waiting crescent: feet polish a half-round in front of
    # the unmarked door. Nothing continues past it.
    make_floor_stain("Wear_Portal_Wait", (0.0, 2.45), radius=0.34,
                     floor_z=15.045, tint=cedar_pale, segments=10)
    # The hand-smudge below the six-inch window (chest height).
    make_box("Wear_Portal_Smudge", (0.0, 2.955, 16.05), (0.20, 0.008, 0.10),
             (0.40, 0.28, 0.18, 1.0))


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    THE CREDIT ("Kai pointed at the Tideline Survey poster's
    lower-right corner. The credit read:") — a credit line on the
    lower-right of the studio's S poster at x 1.6 (lower row). Photograph (Dean's
    portrait), estuary_7, the portal door and window exist —
    markers only."""
    # ON the poster's face, printed pale (2026-09-24: at y 0.105 it sat inside
    # the frame, behind the poster's face at 0.135 — the insert filmed a
    # dark poster and no credit)
    # (pass 473) the credit line READS: "Brandon T., with the Oneironautics
    # Inc. team, after a template submitted in 2046." (ch22_floors n44) — the
    # strip widened for its two lines of small print, a Label3D in
    # cedar_tower.tscn (Tideline_Credit_Words) printed on it
    make_box("Tideline_Credit", (1.84, 0.136, 5.425), (0.36, 0.002, 0.05), (0.88, 0.86, 0.80, 1.0))


def main():
    clear_scene()
    build_lobby()
    build_studio()
    build_quarters()
    build_portal_floor()
    build_draft2_density_2026_08()
    build_exterior()
    build_drone_dock_2026_08()
    build_wear_personality_2026_08()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/cedar_tower.glb"))
    print(f"\n[build_cedar_tower] exporting to {out}")
    build_horizon_2026_08()
    build_hero_props_2026_09()
    export_glb(out)



def build_horizon_2026_08():
    """STUMP HUNT: view stopped at 31m. The tower has a town under
    it — rooflines stepping down the hill, then the tree country."""
    # GROUND under everything out past the last band (2026-08-09,
    # user: "no ground on any of the roads — a flat expanse of
    # nothing"). Locale-colored so exteriors stop sharing a void.
    # The ground stops at the bluff's edge west of the floors (2026-10-21):
    # the tower is "on top of the bluff" with the ocean seaward, and the
    # new west windows look out at it — so the land runs to x -34, a rock
    # face drops 24 m, and the September ocean runs to the horizon.
    BLUFF_X, SEA_Z = -34.0, -24.0
    make_box("Ground_Far", ((BLUFF_X + 540.0) / 2.0, 0.0, -0.03), (540.0 - BLUFF_X, 1080.0, 0.02),
             (0.20, 0.24, 0.16, 1.0))
    make_box("Bluff_Face", (BLUFF_X - 0.6, 0.0, SEA_Z / 2.0 - 0.02), (1.2, 1080.0, -SEA_Z), (0.34, 0.31, 0.27, 1.0))
    for k, (by, bw) in enumerate(((-30.0, 9.0), (-8.0, 6.0), (14.0, 11.0), (38.0, 7.0))):
        # spurs of the bluff stepping out into the surf, so the edge is not
        # a ruled line
        make_box(f"Bluff_Spur_{k}", (BLUFF_X - 2.4 - (k % 2) * 1.2, by, SEA_Z / 2.0 - 1.5 - (k % 2) * 2.0),
                 (3.6 + (k % 2) * 2.4, bw, -SEA_Z - 3.0 - (k % 2) * 4.0), (0.30, 0.28, 0.25, 1.0))
    make_box("Sea", (BLUFF_X - 500.0, 0.0, SEA_Z), (1000.0, 1080.0, 0.04), (0.30, 0.40, 0.46, 1.0))
    make_box("Sea_Surf", (BLUFF_X - 6.0, 0.0, SEA_Z + 0.03), (5.0, 1080.0, 0.02), (0.74, 0.78, 0.78, 1.0))
    from _props.detail import make_far_bands
    # the horizon bands stop at the bluff's edge: N and S bands run from
    # x -33.9 east, the E bands as before; nothing hangs over the sea
    # (pass 476) no town: "a small unincorporated headland ... undeveloped land
    # for forty years" — the near band is the cedar forest too, not rooflines
    for nm, col, bands, prof in (("FarWoodNear", (0.15, 0.23, 0.16), [(80.0, 90.0, 22.0, 0.80), (150.0, 130.0, 26.0, 0.66)], "treeline"),
                                 ("FarWood", (0.16, 0.24, 0.15), [(250.0, 200.0, 12.0, 0.56), (460.0, 330.0, 15.0, 0.42)], "treeline")):
        # the E bands are measured from the exterior set (x 45), not from the
        # floors: at x 60 the first one stood 13 m off the establish's lens,
        # a dark wall down the frame's right side (2026-10-21)
        make_far_bands(nm, col, bands, profile=prof, sides="E", cx=45.0)
        for k, (dist, half, h, shade) in enumerate(bands):
            half_ns = (half - BLUFF_X - 0.1) / 2.0
            make_far_bands(f"{nm}_NS{k}", col, [(dist, half_ns, h, shade)], profile=prof, sides="NS",
                           cx=BLUFF_X + 0.1 + half_ns)
    # The cedars round the tower's own floors, seen from the new N and W
    # windows ("the inland face showing the cedars"): tall Sitka and
    # cedar between the floors and the bluff's edge, and a stand north.
    from _props.trees import make_conifer
    for i, (tx, ty, th) in enumerate(((-15.0, -4.0, 24.0), (-21.0, 6.5, 30.0), (-17.5, 15.0, 27.0),
                                      (-26.0, 21.0, 22.0), (-13.5, 27.0, 31.0), (-6.0, 32.0, 26.0),
                                      (3.5, 35.0, 29.0), (10.5, 30.0, 24.0), (15.0, 38.0, 30.0),
                                      (-24.0, -14.0, 26.0))):
        make_conifer(f"Bluff_Cedar_{i}", tx, ty, th, SITKA if i % 2 else (0.14, 0.24, 0.17, 1.0),
                     (0.30, 0.24, 0.18, 1.0), skirt=0.22)


if __name__ == "__main__":
    main()
