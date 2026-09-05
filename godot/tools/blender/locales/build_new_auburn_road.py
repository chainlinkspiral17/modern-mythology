"""new_auburn_road — the Texas back road, New Auburn (vol6). Split off
louisiana_road 2026-09-03 (user: "the stretches of highway across all
the volumes look identical, same geometry, same camera").

Every vol6 exterior that was not a real room — the subdivision
street at night, the water tower and the gas station, the Foxhole
strip mall on Old San Antonio Road with its back-lot unit, Live Oak
(Jesse's Civic, the door open two inches), the Cypress motel — had
been built onto a LOUISIANA swamp road with cypress and Spanish moss.
This is the same dressing on a Texas road: flat, wide, cracked
two-lane blacktop with gravel shoulders and bar ditches, live oaks
and cedar scrub instead of cypress, power lines down one side, the
NAPD substation off the bypass, a divided stretch to the north for
the highway chapters, and the bypass's own traffic signal.

Presets (Background3D), each a different place, height and lens:
  new_auburn_strip_mall  night · from the Civic's nose in the back
                          lot, NNE at the unit's door · eye 1.35, 58°
  new_auburn_lot         day · the front lot, the white sedan · 1.6, 56°
  new_auburn_two_lane    night storm · low behind the Chronicle sedan
                          tailing the van up the open road · 1.1, 50°
  new_auburn_bypass      dawn · the substation lot off the bypass,
                          Ramirez at the side door · 1.7, 60°
  new_auburn_cedar_route dusk · handlebar height on the cedar route
                          south of town, cicadas · 1.1, 66°

Coordinate frame: Blender Z-up. Road runs N-S along y (x 0), the
subdivision at y -6..18, the strip mall east at y 36..58, the motel
west at y 60..96, the substation west at y 100..124, the divided
stretch north of y 200, the cedar route south of y -40. glTF export
remaps to Godot (x, z, -y).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
import math
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_blob, make_wedge, export_glb
from _props.detail import make_far_bands
from _props.trees import make_broadleaf, make_cypress
from _props.vehicles import make_car
from _props.buildings import make_ranch_house
from _props.detail import make_utility_pole, make_wire_run

COL_ASPHALT = (0.30, 0.29, 0.28, 1.0); COL_LANE_LINE = (0.92, 0.86, 0.52, 1.0)
COL_GRASS = (0.50, 0.48, 0.30, 1.0); COL_DIRT_SHOULDER = (0.58, 0.50, 0.38, 1.0)
COL_CYPRESS_TRUNK = (0.32, 0.22, 0.16, 1.0); COL_CYPRESS_FOLIAGE = (0.32, 0.42, 0.30, 1.0)
COL_SPANISH_MOSS = (0.62, 0.58, 0.42, 1.0)
COL_OAK_TRUNK = (0.30, 0.24, 0.18, 1.0); COL_OAK_FOLIAGE = (0.26, 0.34, 0.20, 1.0)
COL_CEDAR_SCRUB = (0.24, 0.30, 0.20, 1.0)
COL_MILE_MARKER = (0.78, 0.84, 0.62, 1.0); COL_SIGN_RED = (0.74, 0.28, 0.20, 1.0)
COL_SKY = (0.10, 0.13, 0.22, 1.0)
# ── Suburban dressing palette (Harmony Creek Estates night street) ──
COL_SIDEWALK  = (0.54, 0.54, 0.52, 1.0)   # pale concrete
COL_CURB      = (0.42, 0.42, 0.42, 1.0)
COL_DRIVEWAY  = (0.48, 0.48, 0.50, 1.0)
COL_LAWN      = (0.30, 0.44, 0.24, 1.0)   # mowed front lawn, darker at night
COL_HOUSE_TAN = (0.52, 0.44, 0.34, 1.0)   # tan siding ranch
COL_HOUSE_GRY = (0.42, 0.42, 0.46, 1.0)   # gray two-story
COL_HOUSE_BRK = (0.46, 0.34, 0.30, 1.0)   # brick
COL_ROOF      = (0.18, 0.16, 0.18, 1.0)
COL_ROOF_WARM = (0.24, 0.19, 0.17, 1.0)
COL_TRIM      = (0.72, 0.70, 0.64, 1.0)
COL_WIN_WARM  = (0.98, 0.88, 0.58, 1.0)   # lit window (bright — reads as glowing)
COL_WIN_TV    = (0.56, 0.68, 0.94, 1.0)   # cool TV-glow window
COL_WIN_DARK  = (0.10, 0.12, 0.16, 1.0)   # unlit window
COL_DOOR      = (0.36, 0.24, 0.20, 1.0)
COL_LAMP_POLE = (0.22, 0.22, 0.24, 1.0)
COL_LAMP_HEAD = (1.0, 0.80, 0.42, 1.0)    # sodium fixture glass (bright warm)
COL_MAILBOX   = (0.30, 0.34, 0.40, 1.0)
COL_MAIL_POST = (0.40, 0.30, 0.20, 1.0)
COL_SHRUB     = (0.26, 0.40, 0.24, 1.0)
COL_SPRINK    = (0.30, 0.32, 0.30, 1.0)
COL_SPRAY     = (0.70, 0.80, 0.88, 0.35)  # faint sprinkler arc droplets
COL_STREETSIGN_G = (0.20, 0.46, 0.32, 1.0)

# Streetlamp fixtures. Each entry is (pole_x, y, head_x) in BLENDER frame;
# lamp head sits at z=5.0. The louisiana_road.tscn Sodium_* practicals are
# co-located: godot(x,y,z) = (head_x, 5.0, -y). This outdoor set legitimately
# spans +/-Y (godot +/-Z), so the practicals sit at both +Z and -Z (not a bug).
LAMP_FIXTURES = [
    (-3.7, -2.0, -2.8), (-3.7, 6.0, -2.8), (-3.7, 14.0, -2.8),  # west verge
    (+5.4, 2.0, 3.0), (+5.4, 10.0, 3.0),                        # east verge
]
ROAD_FAR = 1200.0
ROAD_NEAR = -1200.0


def _make_house(prefix, cx, cy, face, style, wall_col):
    """Suburban house massing set back off the road. `face` = +1 for a
    west-side house (road at +X) or -1 for east (road at -X). `style` is
    'ranch' (low + wide, optional garage wing) or 'two_story'. Compound
    silhouette: body + eave + ridge cap + a row of lit/dark windows on the
    road-facing wall + door + chimney, plus a garage wing for ranches. Lit
    windows use bright emissive-reading vertex colour so the frame isn't a
    black void behind the dialogue."""
    import math as _m
    if style == 'two_story':
        bd, bw, bh, rows = 5.0, 6.0, 5.4, 2
    else:                              # ranch
        bd, bw, bh, rows = 5.2, 7.2, 3.0, 1
    # main body
    make_box(f"{prefix}_Body", (cx, cy, bh / 2.0), (bd, bw, bh), wall_col)
    # wide eave slab + ridge cap (hip-roof massing)
    make_box(f"{prefix}_Eave", (cx, cy, bh + 0.12), (bd + 0.7, bw + 0.7, 0.24), COL_ROOF)
    make_box(f"{prefix}_Ridge", (cx, cy, bh + 0.5), (bd * 0.55, bw * 0.7, 0.6), COL_ROOF_WARM)
    # chimney
    make_box(f"{prefix}_Chimney", (cx - bd * 0.28, cy + bw * 0.3, bh + 0.7),
             (0.4, 0.4, 1.0), COL_HOUSE_BRK)
    # road-facing wall + its windows
    wall_x = cx + face * (bd / 2.0 + 0.02)
    lit_cycle = [COL_WIN_WARM, COL_WIN_DARK, COL_WIN_WARM, COL_WIN_TV, COL_WIN_DARK]
    for r in range(rows):
        wz = 1.5 + r * 2.0
        for c in range(3):
            wy = cy - bw * 0.28 + c * (bw * 0.28)
            wc = lit_cycle[(r * 3 + c + (0 if face > 0 else 2)) % len(lit_cycle)]
            make_box(f"{prefix}_Win_{r}_{c}", (wall_x, wy, wz), (0.05, 1.0, 1.0), wc)
            make_box(f"{prefix}_WinTrim_{r}_{c}", (wall_x - face * 0.02, wy, wz),
                     (0.03, 1.16, 1.16), COL_TRIM)
    # front door
    make_box(f"{prefix}_Door", (wall_x, cy - bw * 0.28, 1.05), (0.06, 0.9, 2.1), COL_DOOR)
    # porch: slab + two posts under an awning
    px = wall_x + face * 0.9
    make_box(f"{prefix}_Porch", (px, cy - bw * 0.28, 0.1), (1.8, 2.2, 0.2), COL_SIDEWALK)
    for ps in (-1, +1):
        make_cyl(f"{prefix}_PorchPost_{ps:+d}", (wall_x + face * 1.7, cy - bw * 0.28 + ps * 1.0, 1.2),
                 0.08, 2.4, COL_TRIM, segments=6)
    make_box(f"{prefix}_Awning", (wall_x + face * 1.0, cy - bw * 0.28, 2.45), (2.0, 2.3, 0.14), COL_ROOF)
    # ranch garage wing
    if style == 'ranch':
        gy = cy + bw * 0.5 + 1.6
        make_box(f"{prefix}_Garage", (cx + face * 0.4, gy, 1.3), (bd * 0.7, 3.0, 2.6), wall_col)
        make_box(f"{prefix}_GarageRoof", (cx + face * 0.4, gy, 2.7), (bd * 0.7 + 0.4, 3.2, 0.2), COL_ROOF)
        make_box(f"{prefix}_GarageDoor", (cx + face * (bd * 0.35 + 0.03), gy, 1.1),
                 (0.05, 2.4, 2.0), COL_TRIM)
    # a couple of foundation shrubs against the facing wall
    for si in range(3):
        make_cyl(f"{prefix}_Shrub_{si}", (wall_x + face * 0.5, cy - bw * 0.3 + si * bw * 0.3, 0.4),
                 0.45, 0.8, COL_SHRUB, segments=8)

def _make_streetlamp(prefix, pole_x, y, head_x):
    """Cobra-head sodium streetlamp: pole + arm reaching over the verge +
    a glowing lamp head at z=5.0. The head is co-located with a Sodium_*
    OmniLight practical in louisiana_road.tscn."""
    make_cyl(f"{prefix}_Pole", (pole_x, y, 2.6), 0.09, 5.2, COL_LAMP_POLE, segments=8)
    # horizontal arm from pole toward the road
    arm_len = abs(head_x - pole_x)
    make_cyl(f"{prefix}_Arm", ((pole_x + head_x) / 2.0, y, 5.05), 0.05, arm_len,
             COL_LAMP_POLE, segments=6, axis='X')
    # cobra-head housing + bright glass lens (reads as the lit fixture)
    make_box(f"{prefix}_Housing", (head_x, y, 5.12), (0.5, 0.28, 0.16), COL_LAMP_POLE)
    make_box(f"{prefix}_Lens", (head_x, y, 4.98), (0.42, 0.22, 0.06), COL_LAMP_HEAD)

def build_suburban_street():
    """Populate the black frame: Harmony Creek Estates comes right up to
    this two-lane road. West side is fully developed (sidewalk, lawns with
    sprinklers, driveways, houses, mailboxes, a parked car); the east side
    backs onto the bayou but still carries set-back houses + a sidewalk, so
    the road reads as a lit suburban street from any angle instead of a
    strip of asphalt in a void. Blender frame; road runs N-S along +Y."""
    import math as _m
    y0, y1 = -6.0, 18.0
    y_mid, y_len = (y0 + y1) / 2.0, (y1 - y0)
    # ── Sidewalks + curbs both sides (public right-of-way) ──
    for sgn, sw_x in ((-1, -4.0), (+1, 4.6)):
        make_box(f"Sidewalk_{sgn:+d}", (sw_x, y_mid, 0.03), (1.2, y_len, 0.06), COL_SIDEWALK)
        make_box(f"Curb_{sgn:+d}", (sw_x - sgn * 0.7, y_mid, 0.05), (0.12, y_len, 0.12), COL_CURB)
    # ── West front lawns (mowed, raised slightly off the street) ──
    make_box("Lawn_W", (-8.0, y_mid, 0.035), (7.0, y_len, 0.05), COL_LAWN)
    # ── Houses set back on BOTH sides, varied silhouettes ──
    west_houses = [(-1.5, 'ranch', COL_HOUSE_TAN), (6.5, 'two_story', COL_HOUSE_GRY),
                   (14.0, 'ranch', COL_HOUSE_BRK)]
    for i, (hy, style, col) in enumerate(west_houses):
        make_ranch_house(f"HouseW_{i}", -12.5, hy, "+X", col, COL_ROOF, w=7.2 if style == 'ranch' else 6.0, d=5.2 if style == 'ranch' else 5.0,
                         garage=(style == 'ranch'), two_story=(style == 'two_story'), lit=(True, False, True) if i % 2 else (False, True, False))
    east_houses = [(1.0, 'two_story', COL_HOUSE_BRK), (9.0, 'ranch', COL_HOUSE_TAN),
                   (29.5, 'two_story', COL_HOUSE_GRY)]  # north of the gas station — at 16.5 it stood inside the store
    for i, (hy, style, col) in enumerate(east_houses):
        make_ranch_house(f"HouseE_{i}", 14.5, hy, "-X", col, COL_ROOF, w=7.2 if style == 'ranch' else 6.0, d=5.2 if style == 'ranch' else 5.0,
                         garage=(style == 'ranch'), two_story=(style == 'two_story'), lit=(False, True, True) if i % 2 else (True, False, False))
    # ── Driveways (curb-cut apron to each west house) + one parked car ──
    for i, (hy, _s, _c) in enumerate(west_houses):
        make_box(f"DriveW_{i}", (-6.8, hy, 0.032), (6.0, 2.6, 0.05), COL_DRIVEWAY)
        make_box(f"DriveApron_W_{i}", (-3.2, hy, 0.031), (1.6, 2.2, 0.04), COL_DRIVEWAY)
    # parked sedan on the middle west driveway (nosed toward the house)
    # On house 0's driveway, along it (E-W), nosed west at the
    # house. It was authored crosswise on drive 1: nose inside the
    # porch posts, tail across the cypress buttresses, and drive 1's
    # mouth is where the sedan stalled anyway.
    cxp, cyp = -6.0, -1.3
    make_box("Parked_Body", (cxp, cyp, 0.5), (3.8, 2.0, 0.6), (0.20, 0.28, 0.40, 1.0))
    make_box("Parked_Cabin", (cxp + 0.2, cyp, 1.05), (2.0, 1.7, 0.5), (0.16, 0.22, 0.32, 1.0))
    make_box("Parked_Windshield", (cxp - 0.75, cyp, 1.06), (0.05, 1.5, 0.42), (0.30, 0.36, 0.42, 1.0))
    for wx in (-1.35, 1.35):
        for wy in (-0.8, 0.8):
            make_cyl(f"Parked_Wheel_{wx:+.0f}_{wy:+.0f}", (cxp + wx, cyp + wy, 0.32),
                     0.34, 0.28, (0.08, 0.08, 0.09, 1.0), segments=8, axis='Y')
    # ── Mailboxes on posts at each west driveway mouth ──
    for i, (hy, _s, _c) in enumerate(west_houses):
        # house 1's box sits SOUTH of its drive: the stalled sedan
        # stands exactly where hy+1.4 lands
        mb_y = hy - 1.4 if i == 1 else hy + 1.4
        make_cyl(f"Mailbox_Post_{i}", (-3.1, mb_y, 0.55), 0.05, 1.1, COL_MAIL_POST, segments=6)
        make_box(f"Mailbox_Box_{i}", (-3.1, mb_y, 1.15), (0.24, 0.42, 0.24), COL_MAILBOX)
        make_box(f"Mailbox_Flag_{i}", (-2.95, mb_y - 0.2, 1.2), (0.02, 0.04, 0.14), COL_SIGN_RED)
    # ── Sprinklers on the west lawns: heads + faint arcing spray ──
    for i, (sx, sy) in enumerate([(-6.8, 0.5), (-6.4, 7.6), (-9.6, 16.8)]):
        make_cyl(f"Sprinkler_{i}", (sx, sy, 0.08), 0.05, 0.16, COL_SPRINK, segments=6)
        # parabolic arc of droplets rising and falling from the head
        for d in range(6):
            t = d / 5.0
            ax = sx + t * 2.4
            az = 0.15 + _m.sin(_m.pi * t) * 1.1
            make_cyl(f"Spray_{i}_{d}", (ax, sy, az), 0.03, 0.06, COL_SPRAY, segments=5)
    # ── West telephone poles w/ crossarms (overhead lines both sides) ──
    for i, py in enumerate([-4.0, 6.0, 16.0]):
        make_cyl(f"WPole_{i}", (-4.6, py, 2.7), 0.09, 5.4, (0.34, 0.26, 0.20, 1.0), segments=6)
        make_box(f"WPole_{i}_Arm", (-4.6, py, 5.0), (0.06, 0.9, 0.08), (0.34, 0.26, 0.20, 1.0))
        for sgn in (-1, +1):
            make_cyl(f"WPole_{i}_Insul_{sgn:+d}", (-4.6, py + sgn * 0.35, 5.12),
                     0.04, 0.10, (0.30, 0.44, 0.42, 1.0), segments=5)
    # ── Streetlamps (co-located with tscn Sodium_* practicals) ──
    for i, (pole_x, y, head_x) in enumerate(LAMP_FIXTURES):
        _make_streetlamp(f"Streetlamp_{i}", pole_x, y, head_x)
    # ── Street-name blade sign at the south intersection ──
    make_cyl("StreetSign_Pole", (-3.0, -5.0, 1.2), 0.04, 2.4, P.METAL_STEEL, segments=6)
    make_box("StreetSign_Blade", (-3.0, -5.0, 2.3), (0.05, 1.2, 0.28), COL_STREETSIGN_G)
    make_box("StreetSign_Text", (-3.03, -5.0, 2.3), (0.005, 0.9, 0.12), P.PAPER)

def build_vol6_landmarks():
    """2026-08-03 hero-prop pass: the civic reads the vol6 prose
    keeps naming — the Harmony Creek water tower (62 ft), the gas
    station the sign already advertised (canopy + pumps + store),
    the traffic light over its exit, the NAPD SUBSTATION B sign."""
    steel = (0.55, 0.57, 0.58, 1.0)
    # Water tower, SW skyline (62 ft ~ 18.9 m)
    for li, (dx, dy) in enumerate(((-2.2, -2.2), (2.2, -2.2), (-2.2, 2.2), (2.2, 2.2))):
        make_cyl(f"WTower_Leg_{li}", (-18.0 + dx, 21.0 + dy, 7.0), 0.20, 14.0, steel, segments=8)
    make_cyl("WTower_Tank", (-18.0, 21.0, 16.2), 3.0, 4.6, (0.72, 0.74, 0.76, 1.0), segments=14)
    make_cyl("WTower_Cap", (-18.0, 21.0, 18.8), 2.2, 0.8, (0.62, 0.64, 0.66, 1.0), segments=14)
    make_box("WTower_Band", (-18.0, 20.9, 16.2), (6.2, 0.05, 1.0), (0.30, 0.44, 0.62, 1.0))
    # The gas station behind its sign (canopy, two islands, store)
    make_box("Gas_Canopy", (7.5, 20.0, 4.85), (10.0, 8.0, 0.5), (0.90, 0.90, 0.92, 1.0))
    for ci, (cx, cy) in enumerate(((4.0, 17.0), (11.0, 17.0), (4.0, 23.0), (11.0, 23.0))):
        make_cyl(f"Gas_Canopy_Post_{ci}", (cx, cy, 2.3), 0.16, 4.6, steel, segments=8)
    for ii, (ix, iy) in enumerate(((5.8, 18.8), (9.2, 18.8), (5.8, 21.2), (9.2, 21.2))):
        make_box(f"Gas_Pump_{ii}", (ix, iy, 0.85), (0.45, 0.55, 1.40), (0.18, 0.32, 0.50, 1.0))
    make_box("Gas_Store", (13.5, 20.0, 1.8), (6.0, 8.0, 3.6), (0.66, 0.62, 0.55, 1.0))
    make_box("Gas_Store_Glow", (10.55, 20.0, 1.4), (0.06, 5.0, 1.6), (0.98, 0.84, 0.55, 1.0))
    # Traffic light over the gas-station exit (the crow's perch)
    # mast west of the canopy edge, head raised above the slab —
    # the pole used to pass through the canopy, the head hung in it
    make_cyl("Signal_Mast", (1.9, 17.0, 3.3), 0.10, 6.6, steel, segments=8)
    make_box("Signal_Arm", (4.05, 17.0, 6.2), (4.2, 0.09, 0.09), steel)
    make_box("Signal_Head", (6.3, 17.0, 5.75), (0.30, 0.30, 0.90), (0.16, 0.16, 0.18, 1.0))
    for si, (sz, col) in enumerate(((6.02, (0.72, 0.20, 0.16, 1.0)), (5.75, (0.86, 0.64, 0.20, 1.0)),
                                    (5.48, (0.26, 0.62, 0.30, 1.0)))):
        make_cyl(f"Signal_Lamp_{si}", (6.16, 17.0, sz), 0.08, 0.03, col, axis='X', segments=8)
    # NAPD SUBSTATION B — hand-touched-up dark-blue enamel
    make_box("NAPD_Base", (-4.35, 12.0, 0.25), (0.30, 1.9, 0.50), (0.52, 0.50, 0.46, 1.0))
    make_box("NAPD_Sign", (-4.35, 12.0, 0.95), (0.15, 1.8, 0.90), (0.12, 0.18, 0.38, 1.0))
    make_box("NAPD_Text", (-4.26, 12.0, 1.05), (0.02, 1.4, 0.30), (0.86, 0.86, 0.82, 1.0))

def build_foxhole_strip_mall_2026_08():
    """THE FOXHOLE STRIP MALL (--props hunt, 2026-08).

    Jesse's whole vol6 surveillance thread runs through geometry
    that did not exist: "The unit at the back of the Foxhole's
    section of the strip mall is the unit Jesse has been tracking"
    · "the papered-over front window" · "His own band's name, in
    chalk, on the front of a venue, in his town." Five cues across
    three chapters looked at nothing.

    Sited east of the road, north of the gas station, with the
    BACK of the mall toward the road — because that is the view
    the chapters use: Jesse in a parked Civic, looking across the
    lot at a dark unit. The white panel van and the dark sedan are
    NOT modeled; the prose keeps noting their absence.
    """
    stucco = (0.72, 0.68, 0.60, 1.0)
    stucco_dk = (0.62, 0.58, 0.50, 1.0)
    roofline = (0.38, 0.35, 0.30, 1.0)
    door_steel = (0.45, 0.46, 0.48, 1.0)
    paper = (0.86, 0.83, 0.76, 1.0)
    chalk = (0.92, 0.92, 0.88, 1.0)
    board = (0.14, 0.14, 0.15, 1.0)
    # y=33 stood inside HouseE_2 (14.5, 29.5) and clipped the
    # gas store — the east side is full through y~35. North of
    # all of it: the mall anchors the road's far end.
    mx, my = 17.0, 47.0            # mall center
    # The mall block: one long bar, back face toward the road (west).
    make_box("StripMall_Block", (mx, my, 2.1), (10.0, 22.0, 4.2), stucco)
    make_box("StripMall_Parapet", (mx, my, 4.35), (10.4, 22.4, 0.35), roofline)
    # Service lot between road and mall back.
    make_box("StripMall_Lot", (10.0, my, 0.015), (7.6, 22.0, 0.03), (0.24, 0.24, 0.25, 1.0))
    for si, sy in enumerate(range(-8, 9, 4)):
        make_box("StripMall_LotStripe_%d" % si, (8.2, my + sy, 0.032),
                 (2.6, 0.10, 0.004), (0.55, 0.54, 0.50, 1.0))
    # Back doors of the row: four plain units...
    for di, dy in enumerate((-8.0, -3.5, 5.5, 9.0)):
        make_box("StripMall_BackDoor_%d" % di, (mx - 5.02, my + dy, 1.05),
                 (0.06, 0.95, 2.10), door_steel)
    # ...the Foxhole's section (rear door + one caged bulb + kegs).
    make_box("Foxhole_BackDoor", (mx - 5.02, my + 1.5, 1.05), (0.06, 0.95, 2.10),
             (0.30, 0.24, 0.20, 1.0))
    make_box("Foxhole_DoorLamp", (mx - 5.10, my + 1.5, 2.45), (0.10, 0.16, 0.16),
             (0.90, 0.78, 0.50, 1.0))
    for ki, ky in enumerate((2.6, 3.1)):
        make_cyl("Foxhole_Keg_%d" % ki, (mx - 5.55, my + ky, 0.30), 0.20, 0.60,
                 (0.60, 0.62, 0.64, 1.0), segments=10)
    # THE UNIT · the tracked one, between the Foxhole and the rest:
    # a rear window PAPERED OVER (paper sheets slightly askew), the
    # door repainted darker than its neighbors, no lamp.
    ux = mx - 5.02
    make_box("Unit_BackDoor", (ux, my - 1.0, 1.05), (0.06, 0.95, 2.10),
             (0.24, 0.23, 0.24, 1.0))
    make_box("Unit_Window_Frame", (ux, my - 2.3, 1.60), (0.05, 1.30, 1.00), stucco_dk)
    for pi2, (poy, poz, w, h) in enumerate((
            (-0.30, 0.18, 0.62, 0.55), (0.28, -0.12, 0.66, 0.60),
            (0.02, 0.30, 0.55, 0.38))):
        make_box("Unit_Window_Paper_%d" % pi2,
                 (ux - 0.035, my - 2.3 + poy, 1.60 + poz), (0.012, w, h), paper)
    # The lot's one working floodlight aims at the OTHER end — the
    # unit sits in the dark on purpose.
    make_cyl("StripMall_FloodPole", (10.5, my + 9.5, 2.6), 0.09, 5.2, door_steel, segments=8)
    make_box("StripMall_FloodHead", (10.7, my + 9.2, 5.1), (0.35, 0.30, 0.22),
             (0.92, 0.88, 0.72, 1.0))
    # THE MARQUEE · front corner, visible from the road past the
    # mall's south end: a black reader board on two posts, chalk
    # lines where the band name is (the name itself is one long
    # chalk stroke and two short ones — legible as writing, not as
    # letters, which is how chalk reads at distance).
    qx, qy = 11.5, 35.5
    for pi3, py3 in enumerate((qy - 0.8, qy + 0.8)):
        make_cyl("Marquee_Post_%d" % pi3, (qx, py3, 1.4), 0.07, 2.8, door_steel, segments=8)
    make_box("Marquee_Board", (qx, qy, 3.1), (0.14, 2.4, 1.30), board)
    make_box("Marquee_Trim", (qx, qy, 3.80), (0.18, 2.5, 0.10), (0.70, 0.20, 0.16, 1.0))
    make_box("Marquee_Chalk_Line1", (qx - 0.08, qy, 3.38), (0.01, 1.9, 0.16), chalk)
    make_box("Marquee_Chalk_Line2", (qx - 0.08, qy - 0.35, 3.05), (0.01, 1.2, 0.12), chalk)
    make_box("Marquee_Chalk_Line3", (qx - 0.08, qy + 0.42, 3.02), (0.01, 0.9, 0.10), chalk)

def build_live_oak_2026_09():
    """LIVE OAK (vol6 ch14, re-homed 2026-09-03 — the beat that stays on
    this set because this set IS the strip mall). "Tonight the door is
    open. Two inches. A faint light is visible through the gap." Jesse
    "stops the car at the corner of the lot, in the small position
    where the sodium lamp does not directly illuminate the Civic's
    silhouette." "At ten twenty-three, Jesse takes out his phone."
    """
    from _props.vehicles import make_car
    mx, my = 17.0, 47.0
    ux = mx - 5.02
    # the two-inch gap: a blade of light on the latch side of the unit's back door, and its spill on the lot
    make_box("Unit_Door_Gap_Light", (ux - 0.035, my - 1.0 + 0.45, 1.05), (0.01, 0.05, 2.02), (0.98, 0.90, 0.66, 1.0))
    make_box("Unit_Door_Light_Spill", (ux - 0.40, my - 0.55, 0.033), (0.70, 0.60, 0.002), (0.46, 0.40, 0.28, 1.0))
    # Jesse's Civic at the south-west corner of the lot, nose north, lights off
    make_car("Civic", 7.2, 38.0, 4.3, (0.34, 0.36, 0.40, 1.0), hatch=True, along="Y", z0=0.03)
    # the phone, lit, in the gap between the dash and the windshield, driver's side
    make_box("Civic_Phone", (6.85, 38.0 - 0.40 + 1.30 + 0.015, 0.03 + 1.08), (0.07, 0.012, 0.14), (0.08, 0.08, 0.09, 1.0))
    make_box("Civic_Phone_Screen", (6.85, 38.0 - 0.40 + 1.30 + 0.0225, 0.03 + 1.08), (0.062, 0.001, 0.126), (0.66, 0.80, 0.96, 1.0))

def build_cypress_motel_2026_09():
    """THE CYPRESS (vol6 ch15, Room 7 — re-homed 2026-09-03). "A motel
    from the 1970s, single-story, twelve rooms in a long L around a
    small empty parking lot. There are three cars in the lot." Sam
    drives past it slowly on the way home; she does not stop. West of
    the road, north of the houses: the long wing runs N-S at x -26
    with its doors toward the lot, the short wing closes the north end,
    the office and the pole sign at the south end nearest the road.
    Room 7 has its light on and its AC running.
    """
    from _props.vehicles import make_car
    wall = (0.74, 0.66, 0.52, 1.0)
    wall_dk = (0.62, 0.54, 0.42, 1.0)
    trim = (0.40, 0.24, 0.18, 1.0)
    roof = (0.30, 0.28, 0.26, 1.0)
    door = (0.36, 0.26, 0.18, 1.0)
    glass = (0.22, 0.26, 0.32, 1.0)
    glass_lit = (0.96, 0.84, 0.54, 1.0)
    lot = (0.26, 0.26, 0.27, 1.0)
    walk = (0.58, 0.56, 0.52, 1.0)
    rw = 3.4
    y0 = 60.0
    # long wing: rooms 1-8, x -30..-22, doors on the east face
    make_box("Cypress_Motel_Long_Wing", (-26.0, y0 + 4 * rw, 1.45), (8.0, 8 * rw, 2.90), wall)
    make_box("Cypress_Motel_Long_Roof", (-26.0, y0 + 4 * rw, 3.02), (8.4, 8 * rw + 0.4, 0.24), roof)
    make_box("Cypress_Motel_Long_Fascia", (-21.85, y0 + 4 * rw, 3.02), (0.10, 8 * rw + 0.4, 0.30), trim)
    # short wing: rooms 9-12 along the north end, x -22..-8.4, doors on the south face
    make_box("Cypress_Motel_Short_Wing", (-15.2, y0 + 8 * rw + 4.0, 1.45), (13.6, 8.0, 2.90), wall)
    make_box("Cypress_Motel_Short_Roof", (-15.2, y0 + 8 * rw + 4.0, 3.02), (14.0, 8.4, 0.24), roof)
    make_box("Cypress_Motel_Short_Fascia", (-15.2, y0 + 8 * rw - 0.15, 3.02), (14.0, 0.10, 0.30), trim)
    # the office at the south end, its window lit, the ice machine and the soda machine beside it
    make_box("Cypress_Motel_Office", (-26.0, y0 - 2.5, 1.45), (8.0, 5.0, 2.90), wall_dk)
    make_box("Cypress_Motel_Office_Roof", (-26.0, y0 - 2.5, 3.02), (8.4, 5.4, 0.24), roof)
    make_box("Cypress_Motel_Office_Window", (-21.98, y0 - 2.5, 1.55), (0.04, 2.60, 1.20), glass_lit)
    make_box("Cypress_Motel_Office_Door", (-21.98, y0 - 0.2, 1.05), (0.04, 0.90, 2.10), glass)
    make_box("Motel_Ice_Machine", (-21.5, y0 + 0.6, 0.85), (0.80, 0.70, 1.70), (0.80, 0.80, 0.78, 1.0))
    make_box("Motel_Soda_Machine", (-21.5, y0 + 1.5, 0.90), (0.80, 0.80, 1.80), (0.72, 0.16, 0.14, 1.0))
    make_box("Motel_Soda_Machine_Face", (-21.09, y0 + 1.5, 1.10), (0.01, 0.60, 1.10), (0.96, 0.92, 0.80, 1.0))
    # the walkway under the overhang, the posts
    make_box("Cypress_Motel_Walk_Long", (-21.2, y0 + 4 * rw, 0.05), (1.6, 8 * rw, 0.10), walk)
    make_box("Cypress_Motel_Walk_Short", (-15.2, y0 + 8 * rw - 0.8, 0.05), (13.6, 1.6, 0.10), walk)
    make_box("Cypress_Motel_Overhang_Long", (-20.9, y0 + 4 * rw, 2.86), (2.2, 8 * rw, 0.08), roof)
    make_box("Cypress_Motel_Overhang_Short", (-15.2, y0 + 8 * rw - 1.1, 2.86), (13.6, 2.2, 0.08), roof)
    for pi in range(9):
        make_box("Motel_Post_%d" % pi, (-19.85, y0 + pi * rw, 1.41), (0.10, 0.10, 2.82), trim)
    for pi in range(5):
        make_box("Motel_Post_N_%d" % pi, (-21.5 + pi * rw, y0 + 8 * rw - 2.15, 1.41), (0.10, 0.10, 2.82), trim)
    # rooms 1-8: door, window, AC unit under the window, room number, one wall lamp each
    for ri in range(8):
        ry = y0 + ri * rw + rw / 2.0
        lit = (ri == 6)      # Room 7
        make_box("Motel_Room_%d_Door" % (ri + 1), (-21.98, ry - 0.9, 1.05), (0.04, 0.90, 2.10), door)
        make_box("Motel_Room_%d_Number" % (ri + 1), (-21.955, ry - 0.9, 1.75), (0.01, 0.12, 0.14), (0.86, 0.80, 0.60, 1.0))
        make_box("Motel_Room_%d_Window" % (ri + 1), (-21.98, ry + 0.75, 1.60), (0.04, 1.30, 1.00), glass_lit if lit else glass)
        make_box("Motel_Room_%d_Curtain" % (ri + 1), (-21.955, ry + 0.75, 1.60), (0.01, 1.20, 0.90), (0.76, 0.68, 0.50, 1.0) if not lit else (0.92, 0.82, 0.58, 1.0))
        make_box("Motel_Room_%d_AC" % (ri + 1), (-21.65, ry + 0.75, 0.62), (0.70, 0.70, 0.50), (0.68, 0.66, 0.62, 1.0))
        make_box("Motel_Room_%d_Lamp" % (ri + 1), (-21.93, ry - 0.2, 2.30), (0.06, 0.14, 0.14), (0.92, 0.82, 0.50, 1.0))
    make_box("Motel_Room_7_AC_Drip", (-21.65, y0 + 6 * rw + rw / 2.0 + 0.75, 0.101), (0.30, 0.24, 0.002), (0.30, 0.30, 0.32, 1.0))
    # rooms 9-12 on the short wing, plainer
    for ri in range(4):
        rx = -21.5 + ri * rw + rw / 2.0
        make_box("Motel_Room_%d_Door" % (ri + 9), (rx - 0.9, y0 + 8 * rw + 0.02, 1.05), (0.90, 0.04, 2.10), door)
        make_box("Motel_Room_%d_Window" % (ri + 9), (rx + 0.75, y0 + 8 * rw + 0.02, 1.60), (1.30, 0.04, 1.00), glass)
        make_box("Motel_Room_%d_AC" % (ri + 9), (rx + 0.75, y0 + 8 * rw - 0.35, 0.62), (0.70, 0.70, 0.50), (0.68, 0.66, 0.62, 1.0))
    # the small empty parking lot, three cars in it
    make_box("Cypress_Motel_Lot", (-13.0, y0 + 4 * rw - 1.0, 0.015), (14.0, 8 * rw + 4.0, 0.03), lot)
    for si in range(7):
        make_box("Motel_Lot_Stripe_%d" % si, (-17.0, y0 + 2.0 + si * rw, 0.032), (4.6, 0.10, 0.004), (0.50, 0.50, 0.46, 1.0))
    make_car("Motel_Car_0", -15.5, y0 + 2 * rw + 0.4, 4.4, (0.62, 0.62, 0.60, 1.0), along="Y", z0=0.03)
    make_car("Motel_Car_1", -15.5, y0 + 6 * rw + 0.4, 4.2, (0.40, 0.26, 0.20, 1.0), along="Y", z0=0.03)
    make_car("Motel_Car_2", -9.0, y0 + 7 * rw - 1.6, 4.6, (0.20, 0.22, 0.30, 1.0), along="X", z0=0.03)
    # the pole sign by the road: CYPRESS · MOTEL · VACANCY
    make_cyl("Cypress_Motel_Sign_Pole", (-5.5, y0 - 2.0, 3.5), 0.14, 7.0, (0.36, 0.36, 0.38, 1.0), segments=8)
    make_box("Cypress_Motel_Sign", (-5.5, y0 - 2.0, 7.8), (0.30, 3.2, 1.60), (0.18, 0.40, 0.36, 1.0))
    make_box("Cypress_Motel_Sign_Text", (-5.34, y0 - 2.0, 8.1), (0.02, 2.6, 0.50), (0.96, 0.92, 0.72, 1.0))
    make_box("Cypress_Motel_Sign_Motel", (-5.34, y0 - 2.0, 7.5), (0.02, 1.6, 0.26), (0.92, 0.60, 0.30, 1.0))
    make_box("Cypress_Motel_Vacancy", (-5.5, y0 - 2.0, 6.7), (0.26, 2.0, 0.44), (0.16, 0.16, 0.18, 1.0))
    make_box("Cypress_Motel_Vacancy_Neon", (-5.35, y0 - 2.0, 6.7), (0.02, 1.6, 0.18), (0.94, 0.30, 0.30, 1.0))
    # the access road from the highway into the lot
    make_box("Cypress_Motel_Access", (-4.3, y0 + 4.0, 0.012), (3.0, 6.0, 0.024), lot)
    # a cypress or two behind the wings, for the name
    from _props.trees import make_cypress
    make_cypress("Cypress_Motel_Tree_0", -33.5, y0 + 10.0, 7.5, COL_CYPRESS_FOLIAGE, COL_CYPRESS_TRUNK, COL_SPANISH_MOSS)
    make_cypress("Cypress_Motel_Tree_1", -34.0, y0 + 26.0, 6.8, COL_CYPRESS_FOLIAGE, COL_CYPRESS_TRUNK, COL_SPANISH_MOSS)


def build_road():
    """Texas two-lane: paler asphalt than the Louisiana blacktop, a
    crack seam, gravel shoulders, bar ditches, no swamp. Runs the
    full ±1200 so the lines still converge."""
    span = (ROAD_FAR - ROAD_NEAR) / 2.0
    mid = (ROAD_FAR + ROAD_NEAR) / 2.0
    make_box("Ground_Far", (0.0, 0.0, -0.06), (2600.0, 2600.0, 0.02), (0.46, 0.44, 0.28, 1.0))
    make_box("Asphalt", (0.0, mid, 0.0), (4.4, span, 0.04), COL_ASPHALT)
    di = 0
    dy = ROAD_NEAR
    while dy < ROAD_FAR:
        make_box(f"CenterLine_{di}", (0.0, dy, 0.022), (0.10, 1.50, 0.005), COL_LANE_LINE)
        dy += 12.0
        di += 1
    for sgn in (-1, +1):
        make_box(f"EdgeLine_{sgn:+d}", (sgn * 2.05, mid, 0.022), (0.06, span, 0.005), (0.92, 0.92, 0.86, 1.0))
        make_box(f"Shoulder_{sgn:+d}", (sgn * 2.95, mid, 0.02), (1.50, span, 0.04), COL_DIRT_SHOULDER)
        make_wedge(f"Ditch_{sgn:+d}", (sgn * 4.6, mid, -0.20), (1.8, span, 0.40), COL_GRASS, high_end=("+X" if sgn < 0 else "-X"))
    for ci in range(40):
        make_box(f"Crack_Seam_{ci}", (0.0 + (ci % 3 - 1) * 0.6, -600.0 + ci * 30.0 + 7.0, 0.021), (0.03, 4.0, 0.002), (0.20, 0.20, 0.20, 1.0))
    # power lines down the east verge, the whole run: real poles with
    # crossarms and insulators, wires that sag between them
    poles = [(6.4, i * 75.0) for i in range(-16, 17)]
    for i, (px, py) in enumerate(poles):
        make_utility_pole(f"Power_Pole_{i}", px, py, h=9.0, transformer=(i % 5 == 2))
    make_wire_run("Power", poles, h=9.0, sag=0.9)


def build_texas_trees():
    """Live oaks near the subdivision, cedar scrub everywhere else."""
    for i, (x, y, h) in enumerate(((-9.5, -12.0, 6.5), (-9.5, 25.0, 6.8), (+9.5, -20.0, 7.0), (+9.7, -32.0, 6.0), (-10.0, 33.0, 7.2))):
        make_broadleaf(f"LiveOak_{i}", x, y, h, COL_OAK_FOLIAGE, COL_OAK_TRUNK)
    for i, (x, y, r, s) in enumerate(((-9.0, -14.0, 1.6, 1), (-11.0, -22.0, 2.0, 2), (9.5, -18.0, 1.8, 3), (10.5, -30.0, 2.2, 4),
                                      (-9.0, 130.0, 1.8, 5), (9.5, 140.0, 2.0, 6), (-10.0, 160.0, 2.2, 7), (10.0, 180.0, 1.9, 8))):
        make_blob(f"Cedar_Scrub_{i}", (x, y, r * 0.75), r, COL_CEDAR_SCRUB, noise=0.26, seed=s, squash=0.75)


def build_front_lot():
    """The strip mall's FRONT lot, east of the block (ch3_parking_lot:
    "The white sedan is parked in the lot when Sam comes out" — the
    Chronicle reporter, alone, reading a tablet; ch20: the Tacoma and
    the RAMÓN VARGAS LIGHTING van in front of the Foxhole's door)."""
    make_box("Front_Lot", (28.0, 47.0, 0.015), (12.0, 22.0, 0.03), (0.28, 0.28, 0.29, 1.0))
    for si in range(5):
        make_box("Front_Lot_Stripe_%d" % si, (25.0, 39.0 + si * 4.0, 0.032), (4.6, 0.10, 0.004), (0.58, 0.58, 0.54, 1.0))
    make_box("Front_Walk", (22.8, 47.0, 0.06), (1.6, 22.0, 0.12), (0.56, 0.56, 0.54, 1.0))
    make_box("Foxhole_Front_Door", (22.03, 49.0, 1.05), (0.06, 1.0, 2.10), (0.30, 0.24, 0.20, 1.0))
    make_box("Foxhole_Front_Sign", (22.06, 49.0, 3.2), (0.06, 3.0, 0.7), (0.14, 0.14, 0.15, 1.0))
    make_car("Lot_Sedan", 28.0, 44.0, 4.4, (0.92, 0.92, 0.90, 1.0), along="Y", z0=0.03)
    make_box("Lot_Sedan_Tablet_Glow", (27.65, 44.0 + 0.9 + 0.012, 1.05), (0.20, 0.006, 0.14), (0.62, 0.78, 0.94, 1.0))
    make_car("Tacoma", 28.0, 52.0, 5.4, (0.72, 0.30, 0.20, 1.0), pickup=True, along="Y", z0=0.03)
    make_car("Lighting_Van", 32.5, 48.0, 5.6, (0.88, 0.88, 0.86, 1.0), along="Y", z0=0.03)
    make_box("Lighting_Van_Logo", (31.575, 48.0, 1.0), (0.01, 2.6, 0.5), (0.20, 0.30, 0.56, 1.0))


def build_cedar_route():
    """South of town: the cedar route (ch21's bike ride home in the
    lavender dusk, ch18's drive home into the morning sun). Scrub
    close on both sides, a cattle guard, a ranch gate."""
    for i in range(18):
        for sgn in (-1, 1):
            r = 1.4 + (i * 7 + (0 if sgn > 0 else 3)) % 5 * 0.12
            make_blob(f"Route_Cedar_{i}_{sgn:+d}", (sgn * (8.4 + (i % 3) * 1.2), -48.0 - i * 6.5, r * 0.75), r, COL_CEDAR_SCRUB,
                      noise=0.26, seed=40 + i * 2 + (sgn > 0), squash=0.75)
    make_box("Cattle_Guard", (0.0, -70.0, 0.025), (4.4, 2.4, 0.01), (0.40, 0.40, 0.42, 1.0))
    for gi in range(9):
        make_box(f"Cattle_Guard_Bar_{gi}", (0.0, -71.0 + gi * 0.25, 0.031), (4.4, 0.06, 0.006), (0.60, 0.60, 0.62, 1.0))
    make_cyl("Ranch_Gate_Post_0", (7.0, -84.0, 1.2), 0.14, 2.4, (0.34, 0.26, 0.18, 1.0), segments=6)
    make_cyl("Ranch_Gate_Post_1", (12.0, -84.0, 1.2), 0.14, 2.4, (0.34, 0.26, 0.18, 1.0), segments=6)
    make_box("Ranch_Gate_Bar", (9.5, -84.0, 1.05), (5.0, 0.06, 0.06), (0.50, 0.50, 0.52, 1.0))
    make_box("Ranch_Gate_Sign", (9.5, -83.96, 2.1), (2.0, 0.02, 0.5), (0.72, 0.60, 0.40, 1.0))


def build_two_lane_north():
    """The open two-lane eighty miles west (ch4_kitchen 83): the white
    unmarked van with the Houston Chronicle sedan three cars back,
    through a storm just easing. Far up the road so nothing of town
    is in the frame."""
    make_car("Transport_Van", 1.1, 322.0, 5.4, (0.90, 0.90, 0.88, 1.0), along="Y")
    make_box("Transport_Van_Roof", (1.1, 321.6, 1.72), (1.7, 3.6, 0.40), (0.86, 0.86, 0.84, 1.0))
    make_car("Chronicle_Sedan", 1.0, 300.0, 4.4, (0.92, 0.92, 0.90, 1.0), along="Y")
    for sgn, nm in ((1, "R"), (-1, "L")):
        make_box(f"Chronicle_Sedan_Taillight_{nm}", (1.0 + sgn * 0.62, 297.78, 0.80), (0.24, 0.02, 0.12), (0.86, 0.14, 0.10, 1.0))
        make_box(f"Transport_Van_Taillight_{nm}", (1.1 + sgn * 0.70, 319.28, 0.80), (0.22, 0.02, 0.14), (0.78, 0.12, 0.10, 1.0))
    make_box("Wet_Sheen", (0.0, 305.0, 0.0205), (4.2, 60.0, 0.001), (0.36, 0.36, 0.38, 1.0))
    for i in range(6):
        make_box(f"Puddle_{i}", (-1.0 + (i % 2) * 2.0, 280.0 + i * 9.0, 0.0215), (1.2, 2.0, 0.001), (0.42, 0.44, 0.48, 1.0))


def build_substation():
    """The NAPD substation off the New Auburn Bypass (ch6_miller_truck):
    "a flat-roofed beige building in a strip-mall configuration ...
    sharing a parking lot with a payday loan." Dawn. Ramirez's car in
    the lot, two coffees at the side door."""
    bx, by = -20.0, 112.0
    make_box("Substation_Lot", (-11.0, by, 0.015), (18.0, 30.0, 0.03), (0.30, 0.30, 0.31, 1.0))
    for si in range(6):
        make_box(f"Substation_Lot_Stripe_{si}", (-14.0, by - 10.0 + si * 4.0, 0.032), (4.6, 0.10, 0.004), (0.60, 0.60, 0.56, 1.0))
    make_box("Substation_Block", (bx, by - 4.0, 2.0), (10.0, 20.0, 4.0), (0.74, 0.68, 0.56, 1.0))
    make_box("Substation_Parapet", (bx, by - 4.0, 4.15), (10.4, 20.4, 0.30), (0.50, 0.46, 0.40, 1.0))
    make_box("Substation_Sign", (bx + 5.02, by - 8.0, 3.2), (0.04, 3.0, 0.60), (0.20, 0.28, 0.44, 1.0))
    make_box("Substation_Sign_Text", (bx + 5.05, by - 8.0, 3.2), (0.01, 2.4, 0.20), (0.92, 0.92, 0.88, 1.0))
    make_box("Substation_Front_Door", (bx + 5.02, by - 8.0, 1.05), (0.04, 1.0, 2.10), (0.28, 0.32, 0.40, 1.0))
    make_box("Substation_Front_Glass", (bx + 5.02, by - 5.0, 1.60), (0.04, 3.0, 1.60), (0.34, 0.42, 0.52, 1.0))
    make_box("Substation_Side_Door", (bx + 5.02, by + 3.5, 1.05), (0.04, 0.95, 2.10), (0.44, 0.44, 0.46, 1.0))
    make_box("Substation_Side_Lamp", (bx + 5.10, by + 3.5, 2.45), (0.10, 0.16, 0.16), (0.96, 0.90, 0.70, 1.0))
    make_box("Substation_Side_Step", (bx + 5.5, by + 3.5, 0.10), (0.9, 1.4, 0.20), (0.56, 0.56, 0.54, 1.0))
    make_box("Payday_Loan_Block", (bx, by + 12.0, 1.8), (10.0, 10.0, 3.6), (0.80, 0.74, 0.62, 1.0))
    make_box("Payday_Loan_Sign", (bx + 5.02, by + 12.0, 3.0), (0.04, 4.0, 0.70), (0.92, 0.72, 0.20, 1.0))
    make_box("Payday_Loan_Sign_Text", (bx + 5.05, by + 12.0, 3.0), (0.01, 3.2, 0.24), (0.16, 0.16, 0.18, 1.0))
    make_box("Payday_Loan_Glass", (bx + 5.02, by + 12.0, 1.5), (0.04, 6.0, 1.6), (0.22, 0.26, 0.32, 1.0))
    make_car("Ramirez_Car", -13.5, by + 1.0, 4.6, (0.24, 0.26, 0.30, 1.0), along="Y", z0=0.03)
    make_car("Miller_Truck", -13.5, by - 7.0, 5.6, (0.20, 0.26, 0.38, 1.0), pickup=True, along="Y", z0=0.03)
    make_cyl("Coffee_Cup_0", (bx + 5.4, by + 2.9, 0.26), 0.04, 0.12, (0.94, 0.92, 0.88, 1.0), segments=8)
    make_cyl("Coffee_Cup_1", (bx + 5.4, by + 4.1, 0.26), 0.04, 0.12, (0.94, 0.92, 0.88, 1.0), segments=8)
    make_cyl("Bypass_Signal_Pole", (5.4, 100.0, 3.2), 0.12, 6.4, (0.30, 0.30, 0.32, 1.0), segments=8)
    make_box("Bypass_Signal_Arm", (2.6, 100.0, 6.3), (5.6, 0.10, 0.10), (0.30, 0.30, 0.32, 1.0))
    make_box("Bypass_Signal_Head", (0.0, 100.0, 5.85), (0.30, 0.30, 0.90), (0.16, 0.16, 0.18, 1.0))
    make_box("Bypass_Signal_Red", (0.0, 99.84, 6.15), (0.20, 0.02, 0.20), (0.90, 0.16, 0.12, 1.0))
    make_box("Bypass_Sign", (5.4, 96.0, 2.4), (0.04, 1.6, 0.60), (0.16, 0.42, 0.24, 1.0))


def build_horizon():
    make_far_bands("FarScrub", (0.30, 0.34, 0.24),
                   [(140.0, 220.0, 5.0, 0.90), (300.0, 340.0, 7.0, 0.72), (600.0, 520.0, 9.0, 0.55)],
                   sides="EW", cx=0.0, cy=0.0, profile="treeline")


def main():
    clear_scene()
    build_road()
    build_texas_trees()
    build_suburban_street()
    build_vol6_landmarks()
    build_foxhole_strip_mall_2026_08()
    build_live_oak_2026_09()
    build_cypress_motel_2026_09()
    build_front_lot()
    build_cedar_route()
    build_two_lane_north()
    build_substation()
    build_horizon()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/new_auburn_road.glb"))
    print(f"\n[build_new_auburn_road] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
