"""THE WOOD THE CROW BROUGHT FINN (vol 7) — one look in every room.

The text builds it a piece at a time: "a small piece of charred wood … about
three inches long, irregular, the edges burnt black, the grain visible in
the unburnt parts. The grain was yellow" (ch1); three pieces that fit (ch5);
five, "a rough irregular hexagon about ten inches across … open at three
corners" (ch9); eight — "six in a ring, one in the center, and one extra"
(ch12): the six smaller pieces each one side of the ring, the eighth, bigger,
in the hole ("The hole was the size and shape of the eighth piece"), cedar,
"The face filled the unburnt portion of the wood … The hair on the face was
curling. The eyes were closed", and the extra with A R I A scratched on its
underside, set "on the cloth next to the hexagon".

(pass 400) The hexagon was drawn five ways in five rooms — cedar squares
round a disc in four of them, a ninth "Eighth_Piece" beside the centre one
at Lena's. Every room builds it here now. Each part carries the room's view
tag (`<Name>__<tag>`), so it stands only in the views whose chapters hold it.
Names keep the close-ups' subject words: Hexagon_* (shot_insert_hexagon),
Hexagon_Eighth_Piece (shot_insert_eighth_piece), Charred_Wood* (_charred_wood).
"""
import math

from .geometry import make_box, make_cyl, make_rot_box

CHAR = (0.075, 0.065, 0.058, 1.0)        # burnt black
GRAIN = (0.74, 0.60, 0.30, 1.0)          # the yellow grain in the unburnt part
CEDAR_FACE = (0.72, 0.52, 0.34, 1.0)     # the eighth piece's carved face
FACE_INK = (0.54, 0.37, 0.24, 1.0)       # the carving's cuts
RING_A = 0.105                           # the ring's apothem: ~25 cm across ("about ten inches")
PIECE = (0.100, 0.036, 0.022)            # a ring piece: one side of the hexagon


def _t(name, tag):
    return "%s__%s" % (name, tag) if tag else name


def ring_piece(base, tag, cx, cy, top, k, gap=0.0, turn=0.0):
    """Ring piece k (0..5) of the hexagon centred at (cx, cy), standing on a
    surface whose top is `top`: char, its unburnt grain face up. `gap` moves
    it out from the centre, `turn` twists it — a piece not yet fitted."""
    d = math.radians(30.0 + 60.0 * k)
    px, py = cx + (RING_A + gap) * math.cos(d), cy + (RING_A + gap) * math.sin(d)
    yaw = d + math.pi / 2.0 + turn
    make_rot_box(_t(base, tag), (px, py, top + PIECE[2] / 2.0), PIECE, CHAR, yaw=yaw)
    make_rot_box(_t(base + "_Grain", tag), (px, py, top + PIECE[2] + 0.0005),
                 (0.066, 0.016, 0.001), GRAIN, yaw=yaw)


def make_charred_pieces(base, tag, cx, cy, top, pieces):
    """A stage before the hexagon: `pieces` is ((k, gap, turn), …)."""
    for i, (k, gap, turn) in enumerate(pieces):
        ring_piece("%s_%d" % (base, i), tag, cx, cy, top, k, gap, turn)


def make_hexagon(cx, cy, top, tag="", aria=(0.17, -0.12), aria_yaw=0.35, eighth=True):
    """The assembled hexagon (ch12 on): the ring, the eighth piece in the
    hole with Aria's face, and the AR I A piece beside it. eighth=False
    leaves the hole open (the piece in a hand or a pocket)."""
    for k in range(6):
        ring_piece("Hexagon_Ring_%d" % k, tag, cx, cy, top, k)
    if eighth:
        h = 0.024
        make_cyl(_t("Hexagon_Eighth_Piece", tag), (cx, cy, top + h / 2.0), 0.096, h, CHAR, segments=6)
        ft = top + h
        make_cyl(_t("Hexagon_Eighth_Piece_Face", tag), (cx, cy, ft + 0.0005), 0.056, 0.001, CEDAR_FACE, segments=12)
        for side, ex in (("L", -0.016), ("R", 0.016)):
            make_box(_t("Hexagon_Face_Eye_" + side, tag), (cx + ex, cy + 0.008, ft + 0.0012), (0.014, 0.002, 0.0004), FACE_INK)
        make_box(_t("Hexagon_Face_Mouth", tag), (cx, cy - 0.020, ft + 0.0012), (0.012, 0.002, 0.0004), FACE_INK)
        for hk, (hx, hy) in enumerate(((-0.034, 0.026), (-0.040, 0.004), (0.034, 0.026), (0.040, 0.004))):
            make_cyl(_t("Hexagon_Face_Curl_%d" % hk, tag), (cx + hx, cy + hy, ft + 0.0012), 0.006, 0.0004, FACE_INK, segments=6)
    if aria is not None:
        ax, ay = cx + aria[0], cy + aria[1]
        make_rot_box(_t("Hexagon_Aria", tag), (ax, ay, top + 0.011), (0.078, 0.048, 0.022), CHAR, yaw=aria_yaw)
        make_rot_box(_t("Hexagon_Aria_Grain", tag), (ax, ay, top + 0.0225), (0.044, 0.022, 0.001), GRAIN, yaw=aria_yaw)
