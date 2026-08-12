"""Living things — the small recurring animals the prose keeps
pointing a camera at.

2026-08-12: `shot_marker_audit.py --props` (the "bowls hunt") found
that **the crow is cued 12+ times across four locales and has never
been modeled anywhere.** It flies ahead of Finn along the bluff
trail, it sits on the rusted I-beam in Graustark that the builder's
own comment calls "the crow's perch," it waits on the cabin's
window ledge and the Millers' porch rail. Twelve inserts framing a
bird that did not exist.

DESIGN NOTES — reading at couch distance, in a vertex-color
pipeline, with no rig:

  · A crow is a SILHOUETTE: a heavy head, a thick neck that runs
    into the body without a step, a long wedge tail, and a beak
    deep enough to see against sky. Get those four and the bird
    reads even at 20m. Round it out and it becomes a pigeon.
  · Corvid black is NOT black. It is a warm charcoal with a blue-
    violet sheen on the wing coverts and a browner cast on the
    flight feathers. Flat black reads as a hole in the frame.
  · One eye highlight sells "alive" more than any other detail.
  · Perched, a crow leans slightly FORWARD off vertical and its
    tail angles down. Standing plumb makes it a decoy.

Two poses, because the prose uses two: perched (on a rail, ledge,
beam) and gliding (ahead along a trail, over a field). No walking
pose — a walking crow needs legs mid-stride and we cannot pose them.
"""
from .geometry import make_box, make_cyl, make_taper_cyl, make_blob

CROW_BODY = (0.10, 0.10, 0.12, 1.0)      # warm charcoal, faint blue
CROW_SHEEN = (0.14, 0.15, 0.21, 1.0)     # blue-violet covert sheen
CROW_FLIGHT = (0.13, 0.12, 0.11, 1.0)    # browner primaries
CROW_BEAK = (0.09, 0.08, 0.08, 1.0)
CROW_EYE = (0.86, 0.84, 0.76, 1.0)       # the one bright note
CROW_LEG = (0.16, 0.15, 0.14, 1.0)


def make_crow(prefix, x, y, z, facing=1.0, scale=1.0, perched=True):
    """A crow. `z` is the FOOT for a perched bird (give it the top of
    the rail/beam it stands on) and the BODY CENTER for a glider.
    `facing`: +1 looks toward -Y (the usual camera side), -1 flips.
    Body length ~0.46m, wingspan ~0.95m — a real American crow.
    """
    s = float(scale)
    f = 1.0 if facing >= 0 else -1.0
    # Perched birds sit a beak-height above their perch; gliders are
    # already given their altitude.
    cz = z + (0.13 * s if perched else 0.0)

    # ── Body: two masses, no step between them ─────────────────
    make_blob("%s_Body" % prefix, (x, y, cz), 0.115 * s, CROW_BODY,
              noise=0.10, seed=7, squash=0.82)
    make_blob("%s_Breast" % prefix,
              (x, y - f * 0.085 * s, cz + 0.012 * s), 0.088 * s,
              CROW_BODY, noise=0.08, seed=11, squash=0.90)
    # Nape running into the head — the corvid's heavy shoulder line
    make_taper_cyl("%s_Nape" % prefix,
                   (x, y - f * 0.135 * s, cz + 0.055 * s),
                   0.070 * s, 0.052 * s, 0.075 * s, CROW_BODY,
                   segments=8, axis='Y')
    # ── Head + beak ────────────────────────────────────────────
    hy = y - f * 0.185 * s
    make_blob("%s_Head" % prefix, (x, hy, cz + 0.085 * s),
              0.058 * s, CROW_BODY, noise=0.07, seed=3, squash=0.92)
    make_taper_cyl("%s_Beak" % prefix,
                   (x, hy - f * 0.055 * s, cz + 0.082 * s),
                   0.026 * s, 0.007 * s, 0.075 * s, CROW_BEAK,
                   segments=6, axis='Y')
    # The eye — one small bright disc per side, the "alive" detail
    for sgn in (-1, 1):
        make_cyl("%s_Eye_%d" % (prefix, sgn),
                 (x + sgn * 0.038 * s, hy - f * 0.012 * s,
                  cz + 0.098 * s),
                 0.010 * s, 0.006 * s, CROW_EYE, segments=6, axis='X')

    # ── Wings ──────────────────────────────────────────────────
    if perched:
        # Folded: two long covert plates lying along the flanks,
        # tips crossing over the tail base.
        for sgn in (-1, 1):
            make_box("%s_Wing_%d" % (prefix, sgn),
                     (x + sgn * 0.098 * s, y + f * 0.010 * s,
                      cz + 0.010 * s),
                     (0.038 * s, 0.230 * s, 0.105 * s), CROW_SHEEN)
            make_box("%s_WingTip_%d" % (prefix, sgn),
                     (x + sgn * 0.070 * s, y + f * 0.150 * s,
                      cz - 0.020 * s),
                     (0.030 * s, 0.130 * s, 0.045 * s), CROW_FLIGHT)
    else:
        # Gliding: wings OUT and slightly swept back, flat — a
        # gliding crow holds them almost level with a shallow bend.
        for sgn in (-1, 1):
            make_box("%s_Wing_%d_In" % (prefix, sgn),
                     (x + sgn * 0.170 * s, y + f * 0.020 * s,
                      cz + 0.015 * s),
                     (0.240 * s, 0.150 * s, 0.030 * s), CROW_SHEEN)
            make_box("%s_Wing_%d_Out" % (prefix, sgn),
                     (x + sgn * 0.375 * s, y + f * 0.075 * s,
                      cz + 0.005 * s),
                     (0.215 * s, 0.115 * s, 0.024 * s), CROW_FLIGHT)
            # Splayed primaries — the fingered trailing edge
            for k in range(3):
                make_box("%s_Primary_%d_%d" % (prefix, sgn, k),
                         (x + sgn * (0.455 + k * 0.035) * s,
                          y + f * (0.115 + k * 0.030) * s,
                          cz - 0.002 * s),
                         (0.075 * s, 0.058 * s, 0.014 * s), CROW_FLIGHT)

    # ── Tail: a long wedge, angled down when perched ───────────
    t_dz = -0.055 * s if perched else -0.010 * s
    make_box("%s_Tail" % prefix,
             (x, y + f * 0.255 * s, cz + t_dz),
             (0.105 * s, 0.230 * s, 0.026 * s), CROW_FLIGHT)
    make_box("%s_TailTip" % prefix,
             (x, y + f * 0.375 * s, cz + t_dz * 1.5),
             (0.078 * s, 0.090 * s, 0.020 * s), CROW_FLIGHT)

    # ── Legs (perched only — a glider tucks them) ──────────────
    if perched:
        for sgn in (-1, 1):
            make_cyl("%s_Leg_%d" % (prefix, sgn),
                     (x + sgn * 0.035 * s, y - f * 0.020 * s,
                      z + 0.062 * s),
                     0.010 * s, 0.125 * s, CROW_LEG, segments=6)
            # Toes gripping the perch — three forward, one back
            for t in range(3):
                make_box("%s_Toe_%d_%d" % (prefix, sgn, t),
                         (x + sgn * (0.035 + (t - 1) * 0.018) * s,
                          y - f * 0.048 * s, z + 0.008 * s),
                         (0.010 * s, 0.048 * s, 0.010 * s), CROW_LEG)
            make_box("%s_Hallux_%d" % (prefix, sgn),
                     (x + sgn * 0.035 * s, y + f * 0.030 * s,
                      z + 0.008 * s),
                     (0.010 * s, 0.036 * s, 0.010 * s), CROW_LEG)


def make_crow_pair(prefix, x, y, z, gap=0.34, facing=1.0, scale=1.0):
    """Two crows on the same perch, one turned away. Crows are
    rarely alone, and the second bird's different angle is what
    makes the pair read as birds rather than ornaments.
    """
    make_crow("%s_A" % prefix, x - gap * 0.5, y, z,
              facing=facing, scale=scale, perched=True)
    make_crow("%s_B" % prefix, x + gap * 0.5, y + 0.05, z,
              facing=-facing, scale=scale * 0.95, perched=True)
