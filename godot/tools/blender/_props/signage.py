# _props/signage.py
# ════════════════════════════════════════════════════════════════
# Wall + ceiling + door + outdoor signage — banners, paper notices,
# neon, brand pole signs, aisle-end signs, door decals. Reusable
# across any retail interior.
# ════════════════════════════════════════════════════════════════
from . import palette as P
from .geometry import make_box


def make_hanging_banner(prefix, anchor, *, width=1.60, height=0.36,
                        text_color=None, bg_color=None, palette=None):
    """Hanging promo banner on two thin steel cables.
    anchor=(center_x, center_y, ceiling_z) — banner drops 42cm below."""
    palette = palette or {}
    bg = bg_color if bg_color is not None else palette.get("bg", P.BRAND_RED_KWIK)
    fg = text_color if text_color is not None else palette.get("fg", P.PAPER)
    cx, cy, ceil_z = anchor
    for cs in (-1, +1):
        make_box(f"{prefix}_Cable_{cs:+d}",
                 (cx + cs * (width * 0.40), cy, ceil_z - 0.20),
                 (0.01, 0.01, 0.40), P.METAL_STEEL)
    make_box(f"{prefix}_BG", (cx, cy, ceil_z - 0.42),
             (width, 0.02, height), bg)
    make_box(f"{prefix}_TextStrip", (cx, cy + 0.012, ceil_z - 0.42),
             (width * 0.80, 0.005, height * 0.50), fg)


def make_brand_banner_wall(prefix, anchor, *, width=4.80, height=0.42,
                           palette=None):
    """Long brand banner mounted on a back wall (above coolers, etc).
    anchor=(center_x, wall_y, center_z)."""
    palette = palette or {}
    bg = palette.get("bg", P.BRAND_NAVY_HCE)
    frame = palette.get("frame", P.BRAND_NAVY_TXT)
    text = palette.get("text", P.BRAND_NAVY_TXT)
    cx, cy, cz = anchor
    make_box(f"{prefix}_BG", (cx, cy, cz),
             (width, 0.02, height), bg)
    for sgn_x in (-1, +1):
        make_box(f"{prefix}_FrameX_{sgn_x:+d}",
                 (cx + sgn_x * (width / 2.0), cy - 0.005, cz),
                 (0.02, 0.02, height), frame)
    for sgn_z in (-1, +1):
        make_box(f"{prefix}_FrameZ_{sgn_z:+d}",
                 (cx, cy - 0.005, cz + sgn_z * (height / 2.0)),
                 (width, 0.02, 0.02), frame)
    make_box(f"{prefix}_LetterBand", (cx, cy - 0.012, cz),
             (width * 0.75, 0.005, height * 0.45), text)


def make_paper_notices_wall(prefix, *, wall_x, wall_face_sign,
                            run_center_y, base_z, notices=None,
                            palette=None):
    """Wall of taped-up paper notices — small varied rectangles.
    wall_face_sign: +1 (notices face +X) or -1 (face -X)."""
    palette = palette or {}
    if notices is None:
        # Default canon: 11-notice set across two rows (employment /
        # lottery odds / we card / tallboys yellow / no loitering /
        # security cam / shift schedule / food stamps + lower row)
        notices = [
            # (dy, dz, w, h, tint)
            (-1.4, 2.00, 0.28, 0.36, P.PAPER),
            (-1.0, 2.00, 0.30, 0.40, P.PAPER),
            (-0.6, 2.00, 0.18, 0.20, P.PAPER_AGED),
            (-0.2, 2.00, 0.22, 0.28, (0.96, 0.96, 0.62, 1.0)),
            (+0.2, 2.00, 0.16, 0.22, P.PAPER_AGED),
            (+0.6, 2.00, 0.20, 0.26, (0.86, 0.46, 0.22, 1.0)),
            (+1.0, 2.00, 0.30, 0.42, P.PAPER),
            (+1.4, 2.00, 0.24, 0.30, P.PAPER),
            (-1.0, 1.60, 0.22, 0.18, P.PAPER_AGED),
            (+0.0, 1.60, 0.18, 0.16, P.PAPER),
            (+0.8, 1.60, 0.20, 0.20, (0.92, 0.74, 0.42, 1.0)),
        ]
    for i, (dy, dz, w, h, tint) in enumerate(notices):
        make_box(f"{prefix}_{i}_Bg",
                 (wall_x + wall_face_sign * 0.02,
                  run_center_y + dy, dz),
                 (0.02, w, h), tint)
        make_box(f"{prefix}_{i}_Print",
                 (wall_x + wall_face_sign * 0.025,
                  run_center_y + dy, dz - 0.04),
                 (0.001, w * 0.7, h * 0.45), P.METAL_BLACK)
        make_box(f"{prefix}_{i}_TapeTop",
                 (wall_x + wall_face_sign * 0.023,
                  run_center_y + dy, dz + h * 0.5 - 0.01),
                 (0.001, 0.06, 0.02), (0.86, 0.84, 0.78, 0.7))


def make_door_decals(prefix, *, door_x_center, door_y_face,
                     decals=None, palette=None):
    """Hours / payment / OPEN / ATM decals on a glass door.
    door_y_face: the wall_y of the door's outside face."""
    palette = palette or {}
    if decals is None:
        decals = [
            # (cx_offset, cz, w, h, tint, name)
            (-1.20, 1.40, 0.28, 0.20, P.PAPER,           "Hours"),
            (-1.20, 1.18, 0.28, 0.10, P.BRAND_NAVY_HCE,  "VisaMC"),
            (+1.20, 1.40, 0.28, 0.18, P.LOTTERY_RED,     "OPEN"),
            (+1.20, 1.18, 0.28, 0.10, P.BRAND_NAVY_HCE,  "ATM"),
            (0.00, 0.40, 0.36, 0.14, P.PAPER_AGED,       "Delivery"),
        ]
    for (xo, zo, w, h, col, nm) in decals:
        make_box(f"{prefix}_{nm}",
                 (door_x_center + xo, door_y_face, zo),
                 (w, 0.005, h), col)


def make_pole_sign(prefix, anchor, *, palette=None):
    """Tall outdoor brand pole sign with red KWIK STOP-style logo +
    price LED panel. anchor=(pole_x, pole_y, pole_center_z)."""
    palette = palette or {}
    brand = palette.get("brand", P.BRAND_RED_KWIK)
    letters = palette.get("letters", P.PAPER)
    led_red = palette.get("led", (0.96, 0.18, 0.10, 1.0))
    px, py, pole_z = anchor
    make_cyl_local(f"{prefix}_Pole", (px, py, pole_z), 0.10, 5.00,
                   P.METAL_STEEL)
    make_box(f"{prefix}_Sign_BG", (px, py, pole_z + 2.40),
             (1.40, 0.10, 0.80), brand)
    make_box(f"{prefix}_Sign_Letters", (px - 0.06, py, pole_z + 2.40),
             (0.005, 1.20, 0.30), letters)
    make_box(f"{prefix}_PriceBG", (px, py, pole_z + 1.60),
             (1.20, 0.10, 0.50), P.METAL_BLACK)
    for di in range(3):
        make_box(f"{prefix}_PriceDigit_{di}",
                 (px - 0.05, py, pole_z + 1.60),
                 (0.005, 0.30, 0.20), led_red)


# Local import to avoid circular — make_cyl is in geometry.py
def make_cyl_local(*args, **kwargs):
    from .geometry import make_cyl
    return make_cyl(*args, **kwargs)
