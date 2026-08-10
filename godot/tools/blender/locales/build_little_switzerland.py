"""Little Switzerland — vol2 ch1's history-montage stop. An
alpine-kitsch roadside village: chalet fronts with dark timber
half-framing, steep roofs, flower boxes, the painted village sign,
mountains behind.

Hero features: three chalet facades of varied width along the north
side of the road (white stucco + timber X-braces + stepped steep
roofs + balconies + flower boxes), the LITTLE SWITZERLAND sign on
two posts, a gravel pull-off, split-rail fence, pines between the
buildings, and a two-ridge mountain backdrop with snow caps.

Coordinate frame: Blender Z-up. y=0 is the road's south edge (the
camera side); +Y runs north: road → pull-off → chalet fronts at
y≈7 → pines → ridges. glTF export remaps to Godot (x, z, -y).

Vantage wired in Background3D.CAMERA_PRESETS:
  little_switzerland — across the road from the chalets, sign
  frame-left, ridges above the rooflines.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, export_glb

COL_ROAD = (0.24, 0.24, 0.26, 1.0)
COL_GRAVEL = (0.48, 0.44, 0.38, 1.0)
COL_GRASS = (0.40, 0.50, 0.30, 1.0)
COL_STUCCO = (0.80, 0.77, 0.70, 1.0)
COL_TIMBER = (0.24, 0.17, 0.12, 1.0)
COL_ROOF = (0.34, 0.24, 0.18, 1.0)
COL_ROOF_LT = (0.42, 0.30, 0.22, 1.0)
COL_WIN = (0.34, 0.40, 0.48, 1.0)
COL_WIN_WARM = (0.92, 0.76, 0.46, 1.0)
COL_FLOWER_BOX = (0.30, 0.22, 0.15, 1.0)
COL_FLOWER_R = (0.66, 0.28, 0.26, 1.0)
COL_FLOWER_P = (0.68, 0.48, 0.60, 1.0)
COL_SIGN = (0.84, 0.80, 0.68, 1.0)
COL_SIGN_TRIM = (0.50, 0.20, 0.18, 1.0)
COL_FENCE = (0.38, 0.29, 0.20, 1.0)
COL_TRUNK = (0.28, 0.21, 0.14, 1.0)
COL_PINE = (0.17, 0.31, 0.21, 1.0)
COL_RIDGE_NEAR = (0.36, 0.44, 0.42, 1.0)
COL_RIDGE_FAR = (0.48, 0.56, 0.60, 1.0)
COL_SNOW = (0.88, 0.90, 0.92, 1.0)
COL_SKY = (0.64, 0.74, 0.84, 1.0)


def build_ground():
    make_box("Grass_Base", (0.0, 8.0, 0.0), (36.0, 20.0, 0.05), COL_GRASS)
    make_box("Road", (0.0, 1.5, 0.02), (36.0, 3.0, 0.05), COL_ROAD)
    make_box("Road_Line", (0.0, 1.5, 0.055), (36.0, 0.10, 0.01), (0.70, 0.66, 0.50, 1.0))
    make_box("Pulloff", (0.0, 4.6, 0.02), (30.0, 3.2, 0.05), COL_GRAVEL)


def chalet(prefix, cx, width, depth, floors):
    """One chalet facade: stucco body, timber grid, stepped steep
    roof, warm ground-floor windows, balcony + flower boxes."""
    face_y = 7.0
    h = 2.6 * floors
    make_box(f"{prefix}_Body", (cx, face_y + depth / 2.0, h / 2.0),
             (width, depth, h), COL_STUCCO)
    # Timber grid on the face: sill line, corner posts, X suggestion
    for tx in (cx - width / 2.0 + 0.10, cx + width / 2.0 - 0.10):
        make_box(f"{prefix}_Post_{tx:.1f}", (tx, face_y - 0.04, h / 2.0),
                 (0.18, 0.10, h), COL_TIMBER)
    for fl in range(1, floors + 1):
        make_box(f"{prefix}_Band_{fl}", (cx, face_y - 0.04, fl * 2.6 - 0.05),
                 (width, 0.08, 0.16), COL_TIMBER)
    make_box(f"{prefix}_Brace_A", (cx - width * 0.22, face_y - 0.05, h - 1.3),
             (0.12, 0.06, 2.0), COL_TIMBER)
    make_box(f"{prefix}_Brace_B", (cx + width * 0.22, face_y - 0.05, h - 1.3),
             (0.12, 0.06, 2.0), COL_TIMBER)
    # Steep roof: three stepped slabs with deep eaves
    for ri in range(3):
        make_box(f"{prefix}_Roof_{ri}", (cx, face_y + depth / 2.0, h + 0.35 + ri * 0.55),
                 (width + 1.4 - ri * (width * 0.30 + 0.4), depth + 1.2 - ri * 0.8, 0.55),
                 COL_ROOF if ri % 2 == 0 else COL_ROOF_LT)
    # Ground-floor warm windows + door; upper cool windows
    n_win = max(2, int(width / 1.7))
    for wi in range(n_win):
        wx = cx - width / 2.0 + width * (wi + 0.5) / n_win
        make_box(f"{prefix}_GWin_{wi}", (wx, face_y - 0.06, 1.30), (0.85, 0.05, 1.0),
                 COL_WIN_WARM)
        make_box(f"{prefix}_GBox_{wi}", (wx, face_y - 0.16, 0.72), (0.95, 0.22, 0.20),
                 COL_FLOWER_BOX)
        fcol = COL_FLOWER_R if (wi + int(cx)) % 2 == 0 else COL_FLOWER_P
        make_box(f"{prefix}_GFlower_{wi}", (wx, face_y - 0.18, 0.86), (0.85, 0.20, 0.10), fcol)
        if floors > 1:
            make_box(f"{prefix}_UWin_{wi}", (wx, face_y - 0.06, 3.75), (0.75, 0.05, 0.9),
                     COL_WIN)
    if floors > 1:
        # Balcony rail across the upper floor
        make_box(f"{prefix}_Balc_Deck", (cx, face_y - 0.30, 2.85), (width - 0.5, 0.5, 0.10),
                 COL_TIMBER)
        make_box(f"{prefix}_Balc_Rail", (cx, face_y - 0.52, 3.25), (width - 0.5, 0.06, 0.08),
                 COL_TIMBER)
        for bi in range(int(width * 2)):
            bx = cx - width / 2.0 + 0.35 + bi * 0.5
            if bx > cx + width / 2.0 - 0.3:
                break
            make_box(f"{prefix}_Baluster_{bi}", (bx, face_y - 0.52, 3.02),
                     (0.05, 0.05, 0.40), COL_TIMBER)


def build_village():
    chalet("Chalet_W", -7.0, 4.6, 4.0, 2)
    chalet("Chalet_M", -0.5, 5.8, 4.6, 2)
    chalet("Chalet_E", 6.0, 3.8, 3.6, 1)
    # The sign, on two posts at the pull-off's west end
    for px in (-11.6, -9.8):
        make_box(f"Sign_Post_{px:.1f}", (px, 5.4, 1.15), (0.14, 0.14, 2.3), COL_TIMBER)
    make_box("Sign_Panel", (-10.7, 5.42, 2.05), (2.2, 0.08, 0.85), COL_SIGN)
    make_box("Sign_Trim", (-10.7, 5.40, 2.05), (2.35, 0.06, 1.0), COL_SIGN_TRIM)
    make_box("Sign_Peak", (-10.7, 5.42, 2.70), (1.4, 0.10, 0.30), COL_ROOF)
    # Split-rail fence along the pull-off
    for i in range(8):
        fx = -8.0 + i * 2.6
        make_box(f"Fence_Post_{i}", (fx, 6.2, 0.45), (0.12, 0.12, 0.9), COL_FENCE)
    for rz in (0.42, 0.72):
        make_cyl(f"Fence_Rail_{rz:.2f}", (1.0, 6.2, rz), 0.05, 20.0, COL_FENCE,
                 segments=6, axis='X')
    # Pines between and beyond the buildings
    spots = [(-10.5, 9.5), (-3.8, 8.8), (2.8, 9.2), (9.5, 8.5), (12.0, 10.5), (-13.5, 8.0)]
    for i, (px, py) in enumerate(spots):
        h = 4.5 + 1.2 * ((i * 5) % 3)
        make_cyl(f"Pine_{i}_Trunk", (px, py, h * 0.2), 0.16, h * 0.4, COL_TRUNK, segments=6)
        make_box(f"Pine_{i}_T0", (px, py, h * 0.45), (2.2, 2.2, h * 0.32), COL_PINE)
        make_box(f"Pine_{i}_T1", (px, py, h * 0.70), (1.5, 1.5, h * 0.28), COL_PINE)
        make_box(f"Pine_{i}_T2", (px, py, h * 0.92), (0.8, 0.8, h * 0.22), COL_PINE)


def build_mountains():
    # (cardboard ridge slab deleted 2026-08-04 — a 0.06m-thick
    # 'mountain' occluding the real banded ridges behind it)
    # (occluder slab deleted 2026-08-04 — a paper-thin wall 20m out
    # hiding the real receding bands built behind it)
    # Snow caps: light bands along the far ridge tops
    make_box("Snow_Far_A", (-12.0, 19.95, 12.0), (10.0, 0.05, 2.0), COL_SNOW)
    make_box("Snow_Far_B", (4.0, 19.95, 12.6), (8.0, 0.05, 1.6), COL_SNOW)
    make_box("Snow_Near", (10.0, 15.95, 8.4), (7.0, 0.05, 1.2), COL_SNOW)
    # (Sky wall deleted 2026-08-04 — it stood between the camera
    # and the new far bands, occluding the horizon it faked.
    # The sky is the .tscn environment's job.)


def main():
    clear_scene()
    build_ground()
    build_village()
    build_mountains()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/little_switzerland.glb"))
    print(f"\n[build_little_switzerland] exporting to {out}")
    build_horizon_2026_08()
    export_glb(out)



def build_horizon_2026_08():
    """STUMP HUNT: view stopped at 41m. It is called Little
    Switzerland — it owes the view mountains: conifer bands, then
    blue-grey ridgelines stacking back."""
    # GROUND under everything out past the last band (2026-08-09,
    # user: "no ground on any of the roads — a flat expanse of
    # nothing"). Locale-colored so exteriors stop sharing a void.
    make_box("Ground_Far", (0.0, 0.0, -0.03), (1800.0, 1800.0, 0.02),
             (0.22, 0.30, 0.18, 1.0))
    from _props.detail import make_far_bands
    make_far_bands("FarConifer", (0.14, 0.22, 0.14),
                   [(60.0, 70.0, 9.0, 0.90), (130.0, 120.0, 12.0, 0.72)],
                   profile="treeline")
    make_far_bands("FarRidge", (0.34, 0.37, 0.42),
                   [(260.0, 220.0, 22.0, 0.62), (480.0, 380.0, 34.0, 0.46),
                    (820.0, 600.0, 48.0, 0.34)], profile="ridge")


if __name__ == "__main__":
    main()
