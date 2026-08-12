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
from _props.geometry import clear_scene, make_box, make_cyl, export_glb

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


def _room(prefix, z0, w, d, ceil):
    """Cedar-paneled floor plate: floor, walls (S door gap), ceiling."""
    make_box(f"{prefix}_Floor", (0.0, d/2.0, z0 + 0.02), (w + 0.4, d + 0.4, 0.06), CEDAR)
    for nm, x in ((f"{prefix}_Wall_W", -w/2.0), (f"{prefix}_Wall_E", w/2.0)):
        make_box(nm, (x, d/2.0, z0 + ceil/2.0), (0.20, d + 0.4, ceil), CEDAR_PANEL)
    make_box(f"{prefix}_Wall_N", (0.0, d, z0 + ceil/2.0), (w + 0.4, 0.20, ceil), CEDAR_PANEL)
    for nm, cx, ww in ((f"{prefix}_Wall_S_W", -(w/4.0 + 0.5), w/2.0 - 1.0),
                       (f"{prefix}_Wall_S_E", +(w/4.0 + 0.5), w/2.0 - 1.0)):
        make_box(nm, (cx, 0.0, z0 + ceil/2.0), (ww, 0.20, ceil), CEDAR_PANEL)
    make_box(f"{prefix}_Wall_S_Header", (0.0, 0.0, z0 + ceil - 0.30), (2.0, 0.20, 0.60), CEDAR_PANEL)
    make_box(f"{prefix}_Ceil", (0.0, d/2.0, z0 + ceil), (w + 0.4, d + 0.4, 0.06), CEDAR_DK)
    # Panel seams: vertical cedar batten rhythm on the N wall
    for i in range(int(w // 1.0)):
        bx = -w/2.0 + 0.6 + i * 1.0
        make_box(f"{prefix}_Batten_{i}", (bx, d - 0.11, z0 + ceil/2.0), (0.05, 0.02, ceil - 0.2), CEDAR_DK)


def build_lobby():
    z0 = 0.0; W, D, C = 10.0, 8.0, 3.66   # twelve-foot ceiling
    _room("Lobby", z0, W, D, C)
    # Double doors, S center (open from the inside — no panel)
    for sgn in (-1, 1):
        make_box(f"Lobby_Door_{sgn:+d}", (sgn * 0.5, 0.06, z0 + 1.25), (0.95, 0.06, 2.50), CEDAR_DK)
        make_cyl(f"Lobby_Door_Bar_{sgn:+d}", (sgn * 0.85, 0.12, z0 + 1.20), 0.025, 0.55, BRASS, segments=8)
    # Reception desk — empty, NO chair behind it
    make_box("Reception_Desk", (0.0, 5.2, z0 + 0.55), (2.8, 0.8, 1.10), CEDAR_DK)
    make_box("Reception_Top", (0.0, 5.2, z0 + 1.12), (2.95, 0.95, 0.06), CEDAR)
    # THE PHOTOGRAPH: Dean at forty-eight, corporate portrait, on
    # the N wall behind the desk — head and shoulders, eye-line to
    # the photographer's left (where Aria stood, at twelve)
    make_box("Dean_Portrait_Frame", (0.0, D - 0.12, z0 + 1.90), (0.72, 0.04, 0.92), FRAME)
    make_box("Dean_Portrait", (0.0, D - 0.135, z0 + 1.90), (0.60, 0.03, 0.80), (0.66, 0.62, 0.56, 1.0))
    make_box("Dean_Portrait_Figure", (0.02, D - 0.145, z0 + 1.78), (0.34, 0.02, 0.46), (0.32, 0.30, 0.32, 1.0))
    make_cyl("Dean_Portrait_Head", (-0.03, D - 0.15, z0 + 2.08), 0.10, 0.02, (0.74, 0.62, 0.52, 1.0), axis='Y', segments=10)
    # Cedar stairs at the back, E side, brass handrail
    for s in range(8):
        make_box(f"Lobby_Stair_{s}", (3.6, 6.9 - s * 0.32, z0 + 0.18 + s * 0.22), (1.5, 0.32, 0.10), CEDAR)
    make_cyl("Lobby_Handrail", (2.85, 5.8, z0 + 1.55), 0.03, 2.6, BRASS, segments=8, axis='Y')
    for hp in (4.8, 6.6):
        make_box(f"Lobby_Handrail_Post_{hp:.1f}", (2.85, hp, z0 + 0.9 + (6.9 - hp) * 0.6), (0.05, 0.05, 0.9), CEDAR_DK)
    # Low cedar bench along the W wall (a lobby, not a void)
    make_box("Lobby_Bench", (-4.4, 3.5, z0 + 0.40), (0.5, 2.4, 0.10), CEDAR)
    make_box("Lobby_Bench_Base", (-4.4, 3.5, z0 + 0.20), (0.42, 2.2, 0.30), CEDAR_DK)


def build_studio():
    z0 = 5.0; W, D, C = 12.0, 9.0, 3.0
    _room("Studio", z0, W, D, C)
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
            make_box(f"Desk_{ci}_{di}_Monitor", (cx + dx, cy + dy + 0.22, z0 + 0.95),
                     (0.44, 0.03, 0.28), (0.14, 0.15, 0.17, 1.0))
            make_box(f"Chair_{ci}_{di}", (cx + dx, cy + dy - 0.65, z0 + 0.44), (0.42, 0.42, 0.06), CEDAR_DK)
    # THE POSTER ARCHIVE: floor-to-ceiling framed slowstick posters,
    # S + W walls
    idx = 0
    for wall, coords in (("S", [(x, 0.13) for x in (-5.2, -4.0, -2.8, -1.6, 1.6, 2.8, 4.0, 5.2)]),
                         ("W", [(-5.87, y) for y in (1.2, 2.4, 3.6, 4.8, 6.0, 7.2)])):
        for (px, py) in coords:
            for row, pz in enumerate((z0 + 0.85, z0 + 2.05)):
                tint = POSTER_TINTS[idx % len(POSTER_TINTS)]; idx += 1
                if wall == "S":
                    make_box(f"Poster_S_{idx}_Frame", (px, py, pz), (1.00, 0.03, 1.05), FRAME)
                    make_box(f"Poster_S_{idx}", (px, py - 0.005, pz), (0.90, 0.025, 0.95), tint)
                else:
                    make_box(f"Poster_W_{idx}_Frame", (px, py, pz), (0.03, 1.00, 1.05), FRAME)
                    make_box(f"Poster_W_{idx}", (px + 0.005, py, pz), (0.025, 0.90, 0.95), tint)
    # ESTUARY 7, half-sized, on the S wall east run — the river
    # coming down to the sea, coastal blues
    make_box("Estuary7_Frame", (0.55, 0.13, z0 + 1.55), (0.55, 0.035, 0.60), BRASS)
    make_box("Estuary7_Poster", (0.55, 0.125, z0 + 1.55), (0.47, 0.03, 0.52), (0.40, 0.56, 0.60, 1.0))
    make_box("Estuary7_River", (0.55, 0.12, z0 + 1.50), (0.10, 0.028, 0.40), (0.62, 0.76, 0.78, 1.0))
    # East wall: the smaller framed photographs (Dean in '14, '19,
    # '41…)
    for pi, py in enumerate((2.0, 3.1, 4.2, 5.3, 6.4)):
        make_box(f"EPhoto_{pi}_Frame", (5.87, py, z0 + 1.60), (0.03, 0.42, 0.34), FRAME)
        make_box(f"EPhoto_{pi}", (5.865, py, z0 + 1.60), (0.025, 0.34, 0.26), (0.62, 0.58, 0.52, 1.0))


def build_quarters():
    z0 = 10.0; W, D, C = 12.0, 8.0, 2.9
    _room("Quarters", z0, W, D, C)
    # Bunks along the W wall — three doubles
    for bi, by in enumerate((1.6, 3.8, 6.0)):
        make_box(f"Bunk_{bi}_Frame", (-5.1, by, z0 + 0.85), (1.1, 2.0, 1.70), CEDAR_DK)
        for lvl, lz in enumerate((0.42, 1.30)):
            make_box(f"Bunk_{bi}_Mattress_{lvl}", (-5.1, by, z0 + lz), (1.0, 1.9, 0.14), (0.86, 0.82, 0.74, 1.0))
            make_box(f"Bunk_{bi}_Blanket_{lvl}", (-5.1, by - 0.35, z0 + lz + 0.09), (0.96, 1.0, 0.06), (0.42, 0.46, 0.55, 1.0))
    # Kitchen at the EAST end: cedar cabinets + wood-stove
    make_box("Q_Counter", (5.1, 4.0, z0 + 0.46), (0.9, 3.2, 0.92), CEDAR_DK)
    make_box("Q_Counter_Top", (5.1, 4.0, z0 + 0.94), (0.95, 3.3, 0.05), CEDAR)
    make_box("Q_Cabinets", (5.55, 4.0, z0 + 1.95), (0.35, 3.0, 0.80), CEDAR_PANEL)
    make_cyl("Q_Stove_Belly", (5.0, 6.6, z0 + 0.50), 0.32, 0.65, (0.14, 0.14, 0.16, 1.0), segments=12)
    make_cyl("Q_Stove_Pipe", (5.0, 6.6, z0 + 1.9), 0.08, 2.0, (0.20, 0.19, 0.20, 1.0), segments=8)
    # The communal table that seats twelve
    make_box("Q_Table", (-0.4, 4.0, z0 + 0.76), (4.2, 1.10, 0.07), CEDAR)
    for lx in (-2.2, 1.4):
        make_box(f"Q_Table_Leg_{lx:+.1f}", (lx, 4.0, z0 + 0.38), (0.12, 0.95, 0.74), CEDAR_DK)
    for si in range(5):
        sx = -2.0 + si * 0.85
        for sy in (3.25, 4.75):
            make_box(f"Q_Chair_{si}_{sy:.2f}", (sx, sy, z0 + 0.45), (0.40, 0.40, 0.05), CEDAR_DK)
    for hx in (-2.75, 2.0):
        make_box(f"Q_HeadChair_{hx:+.2f}", (hx, 4.0, z0 + 0.45), (0.40, 0.44, 0.05), CEDAR_DK)
    # The open book — the same book on Tem's cedar shelf
    make_box("Q_Book_Open_L", (1.2, 4.1, z0 + 0.80), (0.14, 0.20, 0.012), (0.88, 0.86, 0.78, 1.0))
    make_box("Q_Book_Open_R", (1.35, 4.1, z0 + 0.80), (0.14, 0.20, 0.012), (0.88, 0.86, 0.78, 1.0))


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
    make_box("Portal_Door", (0.0, 2.98, z0 + 1.25), (0.90, 0.08, 2.50), CEDAR_DK)
    make_cyl("Portal_Door_Handle", (0.32, 2.92, z0 + 1.10), 0.025, 0.05, BRASS, axis='Y', segments=8)
    # The six-by-six window, chest height, translucent
    make_box("Portal_Window_Frame", (0.0, 2.96, z0 + 1.40), (0.20, 0.10, 0.20), CEDAR)
    make_box("Portal_Window", (0.0, 2.94, z0 + 1.40), (0.15, 0.06, 0.15), (0.80, 0.85, 0.86, 0.45))
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
    make_box("Far_Door", (0.0, 20.92, z0 + 1.25), (0.90, 0.08, 2.50), CEDAR_DK)
    make_cyl("Far_Door_Handle", (-0.32, 20.86, z0 + 1.10), 0.025, 0.05, BRASS, axis='Y', segments=8)



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
        make_box(f"Lobby_Sconce_{sx:+.1f}_Back", (sx, 7.86, z0 + 2.10), (0.10, 0.04, 0.22), BRASS)
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
    # Task lamps on the two rack-side desks.
    for ti, tx in enumerate((-2.95, 1.45)):
        make_cyl(f"Studio_TaskLamp_{ti}_Arm", (tx, 4.75, z0 + 0.95), 0.012, 0.40, (0.22, 0.22, 0.24, 1.0), segments=6)
        make_cyl(f"Studio_TaskLamp_{ti}_Head", (tx + 0.12, 4.70, z0 + 1.12), 0.06, 0.09, (0.96, 0.90, 0.72, 1.0), segments=8)
    # Cable tray from desk clusters to the racks + floor cable runs
    # (the room is PLUGGED IN — D3 rule at tower scale).
    make_box("Studio_CableTray", (0.0, 6.6, z0 + 2.65), (9.5, 0.25, 0.08), (0.30, 0.31, 0.33, 1.0))
    for ci2, cx2 in enumerate((-2.2, 2.2)):
        make_box(f"Studio_CableDrop_{ci2}", (cx2, 6.6, z0 + 1.70), (0.10, 0.06, 1.90), (0.24, 0.24, 0.26, 1.0))
        make_box(f"Studio_CableFloor_{ci2}", (cx2, 5.6, z0 + 0.045), (0.12, 2.0, 0.025), (0.22, 0.22, 0.24, 1.0))
    # Rack labels + ONE rack door ajar (mid-maintenance).
    for ri in range(5):
        make_box(f"Rack_{ri}_Label", (-4.6 + ri * 2.3, 8.44, z0 + 2.00), (0.30, 0.005, 0.08),
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
        make_box(f"Bunk_{bi}_Footlocker", (-4.4, by - 0.85, z0 + 0.22), (0.85, 0.42, 0.40), CEDAR_DK)
    # Folded clothes on one mattress, a guitar leaning at the last bunk.
    make_box("Q_Folded_Clothes", (-5.1, 1.35, z0 + 1.78), (0.30, 0.40, 0.10), (0.52, 0.46, 0.42, 1.0))
    make_box("Q_Guitar_Body", (-4.35, 6.85, z0 + 0.30), (0.32, 0.10, 0.40), (0.55, 0.38, 0.22, 1.0))
    make_box("Q_Guitar_Neck", (-4.35, 6.88, z0 + 0.75), (0.06, 0.05, 0.55), CEDAR_DK)
    # Kitchen life: kettle on the stove, dish rack, mug pegs, pot rail.
    make_cyl("Q_Kettle", (5.0, 6.6, z0 + 0.92), 0.11, 0.16, (0.74, 0.76, 0.78, 1.0), segments=10)
    make_box("Q_DishRack", (5.05, 2.9, z0 + 0.98), (0.45, 0.32, 0.10), (0.62, 0.64, 0.66, 1.0))
    for di2 in range(4):
        make_box(f"Q_Dish_{di2}", (5.05, 2.80 + di2 * 0.07, z0 + 1.06), (0.30, 0.015, 0.16),
                 (0.88, 0.86, 0.80, 1.0))
    for mi in range(5):
        make_cyl(f"Q_MugPeg_{mi}", (5.62, 2.6 + mi * 0.28, z0 + 1.55), 0.015, 0.06,
                 CEDAR_DK, axis='X', segments=6)
        make_cyl(f"Q_PegMug_{mi}", (5.55, 2.6 + mi * 0.28, z0 + 1.47), 0.04, 0.08,
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
    """The clearing at x≈+45: gravel, the wagon, the tower — seven
    floors of cedar band + glass band, the seventh running the
    garden."""
    X = 45.0
    make_box("Ext_Gravel", (X, 2.0, 0.0), (30.0, 26.0, 0.06), GRAVEL)
    # The tower: 8×8 footprint, seven floors
    for f in range(7):
        fz = f * 3.7
        make_box(f"Tower_Band_{f}", (X, 12.0, fz + 1.1), (8.0, 8.0, 2.2), CEDAR_PANEL)
        glass_col = (0.34, 0.55, 0.40, 0.9) if f == 6 else GLASS
        make_box(f"Tower_Glass_{f}", (X, 12.0, fz + 2.85), (8.15, 8.15, 1.3), glass_col)
    make_box("Tower_Cap", (X, 12.0, 7 * 3.7 + 0.2), (8.4, 8.4, 0.4), CEDAR_DK)
    # Garden silhouettes behind the seventh floor's glass
    for gi, gx in enumerate((-2.4, -0.6, 1.2, 2.8)):
        make_box(f"Garden_Green_{gi}", (X + gx, 7.85, 6 * 3.7 + 2.8), (1.0, 0.10, 0.9 + 0.2 * (gi % 2)),
                 (0.28, 0.48, 0.30, 1.0))
    # Double doors at the base, S face
    for sgn in (-1, 1):
        make_box(f"Tower_Door_{sgn:+d}", (X + sgn * 0.5, 7.94, 1.25), (0.95, 0.06, 2.50), CEDAR_DK)
    # The wagon in the clearing
    wx, wy = X - 6.0, 2.5
    make_box("Wagon_Body", (wx, wy, 0.95), (1.95, 4.4, 1.15), (0.36, 0.40, 0.38, 1.0))
    make_box("Wagon_Glass", (wx, wy - 0.2, 1.35), (1.98, 3.0, 0.45), (0.14, 0.16, 0.20, 1.0))
    for tx in (wx - 0.9, wx + 0.9):
        for ty in (wy - 1.5, wy + 1.5):
            make_cyl(f"Wagon_Wheel_{tx:.0f}_{ty:.0f}", (tx, ty, 0.34), 0.34, 0.24,
                     (0.10, 0.10, 0.11, 1.0), segments=10, axis='X')
    # The Sitka ring around the clearing
    for i in range(10):
        tx = X - 13.0 + (i * 41) % 27
        ty = -3.0 if i % 2 == 0 else 20.0 + (i % 3) * 2.0
        h = 9.0 + (i * 3) % 4
        # 2026-08-04: crowns were BOXES. Real spruce silhouettes.
        from _props.trees import make_conifer
        make_conifer(f"Ext_Sitka_{i}", tx, ty, h, SITKA,
                     (0.30, 0.24, 0.18, 1.0))
    # (Sky wall deleted 2026-08-04 — it stood between the camera
    # and the new far bands, occluding the horizon it faked.
    # The sky is the .tscn environment's job.)


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
    make_drone_dock("DroneDock", X - 11.5, 7.0, 0.06, n=3,
                    occupied=(True, False, True))
    # The late unit on approach — low over the gravel, arm stowed,
    # nose toward the empty cradle.
    make_drone("Drone_Inbound", X - 6.4, 1.2, 3.9)
    # A second working the tower's fourth-floor glass band (they
    # repair the buildings they belong to).
    make_drone("Drone_Glazier", X + 5.2, 7.6, 12.4, arm_down=True,
               yaw_flip=True)


def main():
    clear_scene()
    build_lobby()
    build_studio()
    build_quarters()
    build_portal_floor()
    build_draft2_density_2026_08()
    build_exterior()
    build_drone_dock_2026_08()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/cedar_tower.glb"))
    print(f"\n[build_cedar_tower] exporting to {out}")
    build_horizon_2026_08()
    export_glb(out)



def build_horizon_2026_08():
    """STUMP HUNT: view stopped at 31m. The tower has a town under
    it — rooflines stepping down the hill, then the tree country."""
    # GROUND under everything out past the last band (2026-08-09,
    # user: "no ground on any of the roads — a flat expanse of
    # nothing"). Locale-colored so exteriors stop sharing a void.
    make_box("Ground_Far", (0.0, 0.0, -0.03), (1080.0, 1080.0, 0.02),
             (0.20, 0.24, 0.16, 1.0))
    from _props.detail import make_far_bands
    make_far_bands("FarTown", (0.30, 0.28, 0.27),
                   [(60.0, 70.0, 7.0, 0.90), (130.0, 110.0, 8.5, 0.72)],
                   profile="roofline")
    make_far_bands("FarWood", (0.16, 0.24, 0.15),
                   [(250.0, 200.0, 12.0, 0.56), (460.0, 330.0, 15.0, 0.42)],
                   profile="treeline")


if __name__ == "__main__":
    main()
