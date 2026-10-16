"""Kowalski back yard — vol6 placement script.

Canon (vol6 ch7 "Daisy and the Butterfly"): Maya lying on her back in
the grass Ben's father has cut every other Saturday for twenty-two
years; Daisy the coward mutt hiding behind a lawn chair from an
aggressive butterfly; Gracie (eleven) sketching on the patio,
pretending to ignore everyone; "your house is just a house."
Saturday, 13:38, high summer — bright, flat, ordinary on purpose.

Hero features: the perfect lawn (mow stripes), the lawn chair with
Daisy's shape crouched behind it, the concrete patio off the back of
the house with Gracie's chair + sketchbook table, the back of the
house itself (siding, sliding glass door, kitchen window), a
back fence line with a gate, one shade tree with a tire swing.

Coordinate frame: Blender Z-up. y=0 is the BACK OF THE HOUSE (south
edge); +Y runs away from the house into the yard; fence at y=YARD_D.
glTF export remaps to Godot (x, z, -y).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb

YARD_W = 11.0     # x ∈ [-5.5, 5.5]
YARD_D = 9.0      # y ∈ [0, 9.0]
HOUSE_H = 3.0

COL_LAWN = (0.30, 0.42, 0.20, 1.0)
COL_LAWN_DK = (0.26, 0.37, 0.17, 1.0)   # alternating mow stripes
COL_PATIO = (0.56, 0.55, 0.52, 1.0)
COL_PATIO_SEAM = (0.44, 0.43, 0.41, 1.0)
COL_SIDING = (0.72, 0.70, 0.62, 1.0)    # pale vinyl siding
COL_SIDING_SHADE = (0.62, 0.60, 0.53, 1.0)
COL_TRIM = (0.85, 0.84, 0.80, 1.0)
COL_GLASS = (0.40, 0.48, 0.52, 0.6)
COL_FENCE = (0.52, 0.40, 0.26, 1.0)     # cedar fence
COL_FENCE_DK = (0.42, 0.32, 0.20, 1.0)
COL_CHAIR = (0.24, 0.42, 0.55, 1.0)     # blue webbed lawn chair
COL_CHAIR_FRAME = (0.70, 0.70, 0.72, 1.0)
COL_DAISY = (0.62, 0.52, 0.38, 1.0)     # tan mutt
COL_TRUNK = (0.34, 0.25, 0.16, 1.0)
COL_CANOPY = (0.22, 0.34, 0.15, 1.0)
COL_CANOPY_LT = (0.28, 0.42, 0.19, 1.0)
COL_TIRE = (0.12, 0.12, 0.13, 1.0)
COL_TABLE = (0.60, 0.58, 0.54, 1.0)
COL_PAPER = (0.88, 0.86, 0.78, 1.0)
COL_BOWL = (0.70, 0.30, 0.20, 1.0)      # Daisy's water bowl


def build_ground():
    """Mow-striped lawn + the patio slab against the house."""
    stripe_w = 1.1
    n = int(YARD_W / stripe_w) + 1
    for i in range(n):
        x0 = -YARD_W / 2.0 + i * stripe_w
        make_box(f"Lawn_Stripe_{i}", (x0 + stripe_w / 2.0, YARD_D / 2.0 + 0.8, -0.02),
                 (stripe_w, YARD_D - 1.6, 0.04),
                 COL_LAWN if i % 2 == 0 else COL_LAWN_DK)
    # Patio slab (west half against the house)
    make_box("Patio", (-2.6, 1.15, 0.0), (4.6, 2.3, 0.06), COL_PATIO)
    for k in range(3):
        make_box(f"Patio_Seam_{k}", (-4.4 + k * 1.55, 1.15, 0.035), (0.04, 2.3, 0.01),
                 COL_PATIO_SEAM)
    # Grass strip continues in front of the patio's east edge
    make_box("Lawn_Front", (2.9, 1.15, -0.02), (5.2, 2.3, 0.04), COL_LAWN)


def build_house_back():
    """The back of the house: siding wall, sliding glass door onto
    the patio, kitchen window, gutter + eave line."""
    make_box("House_Wall", (0.0, -0.15, HOUSE_H / 2.0), (YARD_W, 0.3, HOUSE_H), COL_SIDING)
    # 2026-08-04: the house was a ROOFLESS BILLBOARD — a 0.3m siding
    # slab whose top edge cut raw against the sky. A real gable now
    # rises behind the wall (ridge along X, slight overhang) with an
    # eave fascia where roof meets siding, so the top of frame reads
    # as a house instead of a stage flat.
    from _props.geometry import make_gable
    make_gable("House_Roof", (0.0, -2.6, HOUSE_H + 1.1),
               (YARD_W + 0.8, 5.6, 2.2), (0.30, 0.26, 0.23, 1.0),
               ridge_axis='X')
    make_box("House_Eave", (0.0, -0.02, HOUSE_H + 0.06),
             (YARD_W + 0.6, 0.34, 0.16), (0.24, 0.21, 0.19, 1.0))
    # Siding lap lines
    for k in range(6):
        make_box(f"Siding_Line_{k}", (0.0, 0.02, 0.35 + k * 0.45), (YARD_W - 0.2, 0.02, 0.03),
                 COL_SIDING_SHADE)
    # Sliding glass door (onto the patio, west)
    make_box("Slider_Frame", (-2.6, 0.04, 1.05), (2.0, 0.10, 2.1), COL_TRIM)
    make_box("Slider_Glass_L", (-3.05, 0.06, 1.05), (0.85, 0.03, 1.95), COL_GLASS)
    make_box("Slider_Glass_R", (-2.15, 0.09, 1.05), (0.85, 0.03, 1.95), COL_GLASS)
    # Kitchen window (east half), sill + two panes
    make_box("KWin_Frame", (2.4, 0.04, 1.55), (1.5, 0.10, 1.0), COL_TRIM)
    make_box("KWin_Glass", (2.4, 0.07, 1.55), (1.35, 0.02, 0.88), COL_GLASS)
    make_box("KWin_Mullion", (2.4, 0.08, 1.55), (0.04, 0.02, 0.9), COL_TRIM)
    make_box("KWin_Sill", (2.4, 0.10, 1.02), (1.6, 0.14, 0.05), COL_TRIM)
    # Eave + gutter
    make_box("Eave", (0.0, 0.10, HOUSE_H + 0.05), (YARD_W + 0.3, 0.5, 0.10), COL_TRIM)
    make_cyl("Downspout", (5.2, 0.06, HOUSE_H / 2.0), 0.05, HOUSE_H, COL_TRIM, segments=6)
    # Hose reel by the downspout
    # on the house wall (2026-09-23: 16 cm off it)
    make_cyl("HoseReel", (4.6, 0.09, 0.35), 0.24, 0.18, (0.24, 0.34, 0.24, 1.0),
             segments=12, axis='Y')


def build_fence_and_tree():
    """Cedar fence on three sides + the shade tree with tire swing."""
    panel_w = 1.8
    n = int(YARD_W / panel_w)
    for i in range(n):
        x0 = -YARD_W / 2.0 + (i + 0.5) * panel_w
        make_box(f"Fence_N_{i}", (x0, YARD_D, 0.9), (panel_w - 0.06, 0.08, 1.8), COL_FENCE)
        make_box(f"Fence_N_Post_{i}", (x0 - panel_w / 2.0, YARD_D, 0.95), (0.12, 0.12, 1.9),
                 COL_FENCE_DK)
    make_box("Fence_N_Rail", (0.0, YARD_D - 0.05, 1.55), (YARD_W, 0.06, 0.08), COL_FENCE_DK)
    # Gate — slightly different panel, latch block
    make_box("Fence_Gate", (3.6, YARD_D - 0.02, 0.88), (1.0, 0.07, 1.76), COL_FENCE_DK)
    make_box("Gate_Latch", (3.1, YARD_D - 0.085, 1.05), (0.08, 0.06, 0.12), (0.4, 0.4, 0.42, 1.0))   # on the gate (2026-09-23: 1.5 cm off it)
    for sgn in (-1, 1):
        m = int(YARD_D / panel_w)
        for i in range(m):
            y0 = (i + 0.5) * panel_w
            make_box(f"Fence_{'E' if sgn > 0 else 'W'}_{i}",
                     (sgn * YARD_W / 2.0, y0, 0.9), (0.08, panel_w - 0.06, 1.8), COL_FENCE)
    # The shade tree, NE quadrant, with the tire swing
    tx, ty = 3.4, 6.6
    make_cyl("Tree_Trunk", (tx, ty, 1.3), 0.28, 2.6, COL_TRUNK, segments=10)
    make_cyl("Tree_Branch", (tx - 0.7, ty, 2.45), 0.10, 1.5, COL_TRUNK, segments=7, axis='X')
    # 2026-08-04: canopy was three cylinders. Blob lobes now — the
    # branch and the tire swing keep their exact geometry.
    from _props.geometry import make_blob
    make_blob("Tree_Canopy_A", (tx, ty, 3.4), 1.95, COL_CANOPY,
              noise=0.20, seed=11, squash=0.80)
    make_blob("Tree_Canopy_B", (tx - 0.9, ty + 0.4, 2.9), 1.25,
              COL_CANOPY_LT, noise=0.22, seed=23, squash=0.85)
    make_blob("Tree_Canopy_C", (tx + 0.8, ty - 0.5, 3.0), 1.15,
              COL_CANOPY_LT, noise=0.22, seed=37, squash=0.85)
    # Tire swing on the branch
    make_box("Swing_Rope", (tx - 1.25, ty, 1.75), (0.03, 0.03, 1.4), (0.62, 0.56, 0.42, 1.0))
    make_cyl("Swing_Tire", (tx - 1.25, ty, 1.0), 0.30, 0.16, COL_TIRE, segments=14, axis='Y')


def build_scene_props():
    """The lawn chair + Daisy behind it, Maya's patch of grass,
    Gracie's patio setup, the water bowl."""
    # The lawn chair — mid-lawn, the butterfly standoff
    cx, cy = 0.8, 4.6
    make_box("Chair_Seat", (cx, cy, 0.38), (0.52, 0.5, 0.05), COL_CHAIR)
    make_box("Chair_Back", (cx, cy + 0.26, 0.72), (0.52, 0.05, 0.65), COL_CHAIR)
    for lx in (-0.22, 0.22):
        make_box(f"Chair_Leg_F_{lx:+.2f}", (cx + lx, cy - 0.22, 0.19), (0.04, 0.04, 0.38),
                 COL_CHAIR_FRAME)
        make_box(f"Chair_Leg_B_{lx:+.2f}", (cx + lx, cy + 0.24, 0.19), (0.04, 0.04, 0.38),
                 COL_CHAIR_FRAME)
    make_box("Chair_Arm_L", (cx - 0.28, cy, 0.55), (0.05, 0.5, 0.05), COL_CHAIR_FRAME)
    make_box("Chair_Arm_R", (cx + 0.28, cy, 0.55), (0.05, 0.5, 0.05), COL_CHAIR_FRAME)
    # DAISY — crouched BEHIND the chair (north side), head low
    # belly on the grass (2026-09-23: the crouch hung 11 cm up)
    make_box("Daisy_Body", (cx, cy + 0.75, 0.15), (0.35, 0.62, 0.30), COL_DAISY)
    make_box("Daisy_Head", (cx, cy + 0.42, 0.11), (0.22, 0.26, 0.20), COL_DAISY)
    make_box("Daisy_Ear_L", (cx - 0.10, cy + 0.38, 0.23), (0.05, 0.10, 0.12), (0.5, 0.4, 0.28, 1.0))
    make_box("Daisy_Ear_R", (cx + 0.10, cy + 0.38, 0.23), (0.05, 0.10, 0.12), (0.5, 0.4, 0.28, 1.0))
    make_box("Daisy_Tail", (cx, cy + 1.1, 0.19), (0.05, 0.24, 0.05), COL_DAISY)
    # Maya's patch — a towel flattened in the grass where she lies
    make_box("Maya_Towel", (-1.6, 5.4, 0.005), (0.9, 1.9, 0.015), (0.75, 0.62, 0.30, 1.0))
    # Gracie's patio corner: small table + chair + sketchbook + pencil cup
    make_box("Gracie_Table", (-3.9, 1.3, 0.42), (0.7, 0.7, 0.04), COL_TABLE)
    make_cyl("Gracie_Table_Leg", (-3.9, 1.3, 0.21), 0.05, 0.42, COL_CHAIR_FRAME, segments=8)
    make_box("Gracie_Chair", (-3.9, 0.7, 0.24), (0.42, 0.42, 0.05), COL_TABLE)
    # legs (2026-09-23: the seat was a board at 24 cm on nothing)
    for lx in (-0.18, 0.18):
        for ly in (-0.18, 0.18):
            make_box(f"Gracie_Chair_Leg_{lx:+.2f}_{ly:+.2f}", (-3.9 + lx, 0.7 + ly, 0.1075),
                     (0.04, 0.04, 0.215), COL_CHAIR_FRAME)
    make_box("Gracie_Chair_Back", (-3.9, 0.5, 0.55), (0.42, 0.05, 0.55), COL_TABLE)
    make_box("Sketchbook", (-3.85, 1.32, 0.455), (0.30, 0.24, 0.02), COL_PAPER)
    make_cyl("Pencil_Cup", (-4.12, 1.45, 0.50), 0.05, 0.12, (0.3, 0.35, 0.4, 1.0), segments=8)
    # Daisy's water bowl by the slider
    make_cyl("Water_Bowl", (-1.6, 0.5, 0.05), 0.14, 0.09, COL_BOWL, segments=12)
    make_cyl("Water", (-1.6, 0.5, 0.085), 0.11, 0.02, (0.35, 0.45, 0.55, 1.0), segments=12)


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    THE BUTTERFLY ("The butterfly leaves.") — in the air by the
    lawn chair Daisy hides behind. Daisy exists (marker only)."""
    make_cyl("Butterfly_Body", (1.35, 4.2, 0.55), 0.006, 0.030, (0.16, 0.14, 0.12, 1.0), axis='Y', segments=6)
    make_box("Butterfly_Wing_L", (1.330, 4.2, 0.552), (0.028, 0.020, 0.002), (0.90, 0.62, 0.20, 1.0))
    make_box("Butterfly_Wing_R", (1.372, 4.2, 0.558), (0.028, 0.020, 0.002), (0.90, 0.62, 0.20, 1.0))



def build_front_yard_2026_10():
    """THE FRONT OF THE HOUSE (2026-10-10; vol6 ch19 "The Chains" — the sweep:
    Bill at the front yard played in Ben's truck cab). "He pulls into the
    Kowalski driveway at one fifty-three. Bill is, again, at the front yard.
    Bill is, this Friday afternoon, pulling weeds from the bed beside the
    porch — the small Bill-task that has been, for three weeks, his
    Friday-afternoon ritual." The house gets its sides and its front (the
    door, the windows, the stoop, the attached garage), the flower bed beside
    the stoop with the pulled weeds, the bucket, the trowel and the kneeling
    pad; the front lawn, the driveway with Ben's Civic, the sidewalk, the
    street and the houses across it. Preset `kowalski_front_yard` (its
    markers suffixed); the same bright afternoon light as the back yard."""
    import math
    from _props.vehicles import make_car
    from _props.geometry import make_blob, make_rot_box
    FY = -5.2                                   # the house's front wall line
    # the house's sides and its front
    for e in (-1, 1):
        make_box(f"House_Wall_Side_{e:+d}", (e * (YARD_W / 2.0), FY / 2.0, HOUSE_H / 2.0), (0.3, -FY, HOUSE_H), COL_SIDING_SHADE)
    make_box("House_Wall_Front", (0.0, FY, HOUSE_H / 2.0), (YARD_W, 0.3, HOUSE_H), COL_SIDING)
    make_box("House_Front_Door", (-1.2, FY - 0.16, 1.02), (0.92, 0.04, 2.04), (0.36, 0.22, 0.18, 1.0))
    make_box("House_Front_Door_Knob", (-0.85, FY - 0.20, 1.00), (0.05, 0.04, 0.05), (0.72, 0.62, 0.36, 1.0))
    for k, wx in enumerate((-3.6, 1.4, 3.6)):
        make_box(f"House_Front_Window_{k}", (wx, FY - 0.155, 1.55), (1.20, 0.02, 1.10), (0.40, 0.46, 0.52, 1.0))
        make_box(f"House_Front_Window_{k}_Trim", (wx, FY - 0.152, 1.55), (1.36, 0.01, 1.26), COL_TRIM)
    # the stoop and its little roof on posts
    make_box("Front_Stoop_Slab", (-1.2, FY - 0.85, 0.045), (2.4, 1.4, 0.09), COL_PATIO)   # one low slab the door opens over
    make_box("Front_Stoop_Step", (-1.2, FY - 1.75, 0.03), (1.6, 0.40, 0.06), COL_PATIO)
    for e in (-1, 1):
        make_box(f"Front_Stoop_Post_{e:+d}", (-1.2 + e * 1.10, FY - 1.45, 0.09 + (2.60 - 0.09) / 2.0), (0.10, 0.10, 2.60 - 0.09), COL_TRIM)
    make_box("Front_Stoop_Roof", (-1.2, FY - 0.80, 2.66), (2.6, 1.70, 0.12), COL_TRIM)
    # the bed beside the stoop: mulch, shrubs, the pulled weeds, Bill's things
    bx0, bx1 = -5.2, -2.6
    make_box("Flower_Bed_Mulch", ((bx0 + bx1) / 2.0, FY - 0.70, 0.02), (bx1 - bx0, 1.10, 0.06), (0.36, 0.24, 0.16, 1.0))
    make_box("Flower_Bed_Edging", ((bx0 + bx1) / 2.0, FY - 1.27, 0.06), (bx1 - bx0, 0.04, 0.12), (0.56, 0.54, 0.50, 1.0))
    for k, sx in enumerate((-4.7, -3.9, -3.1)):
        make_blob(f"Flower_Bed_Shrub_{k}", (sx, FY - 0.55, 0.40), 0.40, (0.24, 0.40, 0.20, 1.0), noise=0.22, seed=600 + k, squash=0.8)
    make_blob("Pulled_Weeds_Pile", (-3.4, FY - 1.55, 0.06), 0.22, (0.40, 0.48, 0.24, 1.0), noise=0.35, seed=640, squash=0.35)
    make_cyl("Weed_Bucket", (-2.9, FY - 1.75, 0.16), 0.15, 0.32, (0.86, 0.48, 0.16, 1.0), segments=12)
    make_box("Kneeling_Pad", (-3.95, FY - 1.55, 0.02), (0.44, 0.28, 0.04), (0.20, 0.42, 0.30, 1.0))
    make_rot_box("Garden_Trowel", (-3.65, FY - 1.40, 0.012), (0.06, 0.26, 0.02), (0.60, 0.62, 0.64, 1.0), yaw=0.6)
    make_box("Garden_Gloves", (-4.30, FY - 1.50, 0.015), (0.14, 0.10, 0.03), (0.72, 0.62, 0.38, 1.0))
    # the attached garage on the east, its door to the driveway
    gx0, gx1 = YARD_W / 2.0, YARD_W / 2.0 + 4.0
    make_box("Garage_Wall_Front", ((gx0 + gx1) / 2.0, FY, 1.35), (gx1 - gx0, 0.3, 2.70), COL_SIDING)
    make_box("Garage_Wall_Side", (gx1, FY / 2.0, 1.35), (0.3, -FY, 2.70), COL_SIDING_SHADE)
    make_box("Garage_Door", ((gx0 + gx1) / 2.0, FY - 0.16, 1.05), (3.0, 0.03, 2.10), COL_TRIM)
    for k in range(4):
        make_box(f"Garage_Door_Panel_Line_{k}", ((gx0 + gx1) / 2.0, FY - 0.177, 0.45 + k * 0.52), (3.0, 0.004, 0.03), (0.70, 0.70, 0.66, 1.0))
    make_box("Garage_Roof", ((gx0 + 0.15 + gx1 + 0.15) / 2.0, FY / 2.0 - 0.075, 2.76), (gx1 - gx0, -FY + 0.15, 0.12), (0.36, 0.30, 0.28, 1.0))   # from the house wall's face out
    # the front lawn, the driveway with Ben's Civic, the sidewalk, the curb, the street
    make_box("Front_Lawn", (-2.0, (FY - 13.4) / 2.0, -0.02), (15.0, 13.4 + FY, 0.04), COL_LAWN)
    make_box("Driveway_Concrete", (7.5, (FY - 13.4) / 2.0, -0.015), (3.8, 13.4 + FY, 0.05), COL_PATIO)
    make_car("Driveway_Civic", 7.5, -9.4, 4.4, (0.42, 0.46, 0.52, 1.0), along="Y")
    make_box("Front_Sidewalk", (1.0, -14.0, -0.01), (26.0, 1.2, 0.06), COL_PATIO)
    make_box("Front_Curb", (1.0, -14.66, 0.02), (26.0, 0.12, 0.14), (0.60, 0.59, 0.56, 1.0))
    make_box("Front_Street_Asphalt", (1.0, -17.9, -0.03), (40.0, 6.4, 0.05), (0.28, 0.28, 0.30, 1.0))
    make_box("Front_Lawn_Across", (1.0, -26.0, -0.03), (40.0, 9.8, 0.04), COL_LAWN)
    for k, (hx, col) in enumerate(((-8.0, (0.78, 0.72, 0.60, 1.0)), (3.0, (0.66, 0.70, 0.72, 1.0)), (14.0, (0.84, 0.80, 0.70, 1.0)))):
        make_box(f"Across_House_{k}_Facade", (hx, -28.5, 1.5), (9.0, 7.0, 3.0), col)
        rh = 7.0 / 4.0 + 0.25
        rzz = 3.0 + rh * math.sin(0.42) + 0.08 - 0.02
        make_rot_box(f"Across_House_{k}_Roof_N", (hx, -28.5 + 7.0 / 4.0, rzz), (9.6, 2.0 * rh, 0.16), (0.34, 0.30, 0.28, 1.0), roll=-0.42)
        make_rot_box(f"Across_House_{k}_Roof_S", (hx, -28.5 - 7.0 / 4.0, rzz), (9.6, 2.0 * rh, 0.16), (0.34, 0.30, 0.28, 1.0), roll=0.42)
    for k, (gx, gy) in enumerate(((-7.5, -11.0), (2.5, -12.2), (-12.0, -24.0), (9.0, -24.5))):
        make_cyl(f"Front_Tree_{k}_Trunk", (gx, gy, 1.6), 0.22, 3.2, (0.36, 0.28, 0.22, 1.0), segments=8)
        make_blob(f"Front_Tree_{k}_Crown", (gx, gy, 4.4), 2.2, (0.26, 0.40, 0.20, 1.0), noise=0.22, seed=660 + k, squash=0.7)
    make_box("Mailbox_Post", (5.2, -13.2, 0.55), (0.08, 0.08, 1.10), (0.40, 0.32, 0.24, 1.0))
    make_box("Mailbox", (5.2, -13.2, 1.18), (0.20, 0.46, 0.22), (0.20, 0.20, 0.22, 1.0))

def main():
    clear_scene()
    build_ground()
    build_house_back()
    build_fence_and_tree()
    build_scene_props()
    build_hero_props_2026_09()
    build_front_yard_2026_10()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/kowalski_backyard.glb"))
    print(f"\n[build_kowalski_backyard] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
