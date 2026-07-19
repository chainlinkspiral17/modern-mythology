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
    make_cyl("HoseReel", (4.6, 0.25, 0.35), 0.24, 0.18, (0.24, 0.34, 0.24, 1.0),
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
    make_box("Gate_Latch", (3.1, YARD_D - 0.10, 1.05), (0.08, 0.06, 0.12), (0.4, 0.4, 0.42, 1.0))
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
    make_cyl("Tree_Canopy_A", (tx, ty, 3.3), 1.9, 1.4, COL_CANOPY, segments=12)
    make_cyl("Tree_Canopy_B", (tx - 0.9, ty + 0.4, 2.9), 1.2, 1.0, COL_CANOPY_LT, segments=10)
    make_cyl("Tree_Canopy_C", (tx + 0.8, ty - 0.5, 3.0), 1.1, 1.0, COL_CANOPY_LT, segments=10)
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
    make_box("Daisy_Body", (cx, cy + 0.75, 0.26), (0.35, 0.62, 0.30), COL_DAISY)
    make_box("Daisy_Head", (cx, cy + 0.42, 0.22), (0.22, 0.26, 0.20), COL_DAISY)
    make_box("Daisy_Ear_L", (cx - 0.10, cy + 0.38, 0.34), (0.05, 0.10, 0.12), (0.5, 0.4, 0.28, 1.0))
    make_box("Daisy_Ear_R", (cx + 0.10, cy + 0.38, 0.34), (0.05, 0.10, 0.12), (0.5, 0.4, 0.28, 1.0))
    make_box("Daisy_Tail", (cx, cy + 1.1, 0.30), (0.05, 0.24, 0.05), COL_DAISY)
    # Maya's patch — a towel flattened in the grass where she lies
    make_box("Maya_Towel", (-1.6, 5.4, 0.005), (0.9, 1.9, 0.015), (0.75, 0.62, 0.30, 1.0))
    # Gracie's patio corner: small table + chair + sketchbook + pencil cup
    make_box("Gracie_Table", (-3.9, 1.3, 0.42), (0.7, 0.7, 0.04), COL_TABLE)
    make_cyl("Gracie_Table_Leg", (-3.9, 1.3, 0.21), 0.05, 0.42, COL_CHAIR_FRAME, segments=8)
    make_box("Gracie_Chair", (-3.9, 0.7, 0.24), (0.42, 0.42, 0.05), COL_TABLE)
    make_box("Gracie_Chair_Back", (-3.9, 0.5, 0.55), (0.42, 0.05, 0.55), COL_TABLE)
    make_box("Sketchbook", (-3.85, 1.32, 0.455), (0.30, 0.24, 0.02), COL_PAPER)
    make_cyl("Pencil_Cup", (-4.12, 1.45, 0.50), 0.05, 0.12, (0.3, 0.35, 0.4, 1.0), segments=8)
    # Daisy's water bowl by the slider
    make_cyl("Water_Bowl", (-1.6, 0.5, 0.05), 0.14, 0.09, COL_BOWL, segments=12)
    make_cyl("Water", (-1.6, 0.5, 0.085), 0.11, 0.02, (0.35, 0.45, 0.55, 1.0), segments=12)


def main():
    clear_scene()
    build_ground()
    build_house_back()
    build_fence_and_tree()
    build_scene_props()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/kowalski_backyard.glb"))
    print(f"\n[build_kowalski_backyard] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
