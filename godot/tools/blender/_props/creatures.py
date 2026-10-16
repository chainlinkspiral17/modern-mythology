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
            # the back toe from the leg (2026-09-24: 2.2 cm behind it, held
            # only by the body's over-tall recorded box)
            make_box("%s_Hallux_%d" % (prefix, sgn),
                     (x + sgn * 0.035 * s, y + f * 0.008 * s,
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


# ── DOG + CAT (2026-10-05) ────────────────────────────────────────
# Joanna's animals are in four vol 5 chapters — "The cat, sensing the
# shift, stopped cleaning its paw. The dog raised its head." "Her dog,
# the one-eyed one, sleeps twitching in a sunbeam." — and were three
# lumps. Same rules as the crow: silhouette first (a dog lying sphinx
# reads by its raised head + forelegs out; a sitting cat by its pointed
# ears + the tail wrapped round its feet), one bright eye, no rig.
#
# Orientation: `heading` is the way the animal FACES — '+X', '-X', '+Y'
# or '-Y' (default '-Y', toward the usual camera side). `z` is the
# ground (or the top of what it lies on).

DOG_TAN = (0.62, 0.50, 0.36, 1.0)
DOG_MUZZLE = (0.78, 0.68, 0.54, 1.0)
DOG_DARK = (0.24, 0.18, 0.14, 1.0)
CAT_GREY = (0.44, 0.42, 0.40, 1.0)
CAT_DARK = (0.26, 0.25, 0.24, 1.0)
PET_EYE = (0.92, 0.86, 0.52, 1.0)


def _frame(x, y, z, heading):
    hx, hy = {'+X': (1, 0), '-X': (-1, 0), '+Y': (0, 1), '-Y': (0, -1)}[heading]
    sx, sy = -hy, hx                    # the animal's left

    def P(fwd, side, up):
        return (x + hx * fwd + sx * side, y + hy * fwd + sy * side, z + up)

    axis_fwd = 'X' if hx else 'Y'
    axis_side = 'Y' if hx else 'X'

    def S(fwd, side, up):               # a box size in the animal's frame
        return (abs(hx) * fwd + abs(sx) * side, abs(hy) * fwd + abs(sy) * side, up)
    return P, S, axis_fwd, axis_side


def make_dog(prefix, x, y, z, heading='-Y', pose='lying', scale=1.0, coat=DOG_TAN,
             muzzle=DOG_MUZZLE, one_eyed=False):
    """A medium mutt. pose: 'lying' (sphinx, head up — "the dog raised
    its head"), 'curled' (asleep, nose to tail), 'sitting'."""
    s = float(scale)
    P, S, AF, AS = _frame(x, y, z, heading)
    if pose == 'curled':
        make_blob(f"{prefix}_Body", P(0.0, 0.0, 0.15 * s), 0.27 * s, coat, noise=0.10, seed=4, squash=0.55)
        make_blob(f"{prefix}_Head", P(0.16 * s, 0.10 * s, 0.20 * s), 0.10 * s, coat, noise=0.06, seed=9, squash=0.8)
        make_box(f"{prefix}_Muzzle", P(0.24 * s, 0.13 * s, 0.17 * s), S(0.10 * s, 0.07 * s, 0.06 * s), muzzle)
        make_box(f"{prefix}_Ear", P(0.13 * s, 0.17 * s, 0.25 * s), S(0.06 * s, 0.04 * s, 0.07 * s), DOG_DARK)
        make_box(f"{prefix}_Tail", P(0.10 * s, -0.20 * s, 0.035 * s), S(0.30 * s, 0.05 * s, 0.05 * s), coat)
        return
    if pose == 'sitting':
        make_blob(f"{prefix}_Haunch", P(-0.12 * s, 0.0, 0.16 * s), 0.18 * s, coat, noise=0.08, seed=3, squash=0.85)
        make_blob(f"{prefix}_Chest", P(0.05 * s, 0.0, 0.36 * s), 0.14 * s, coat, noise=0.06, seed=5, squash=1.15)
        for sd in (-1, 1):
            make_taper_cyl(f"{prefix}_Foreleg_{sd:+d}", P(0.12 * s, sd * 0.06 * s, 0.14 * s),
                           0.03 * s, 0.025 * s, 0.28 * s, coat, segments=6)
        hz, hf = 0.58 * s, 0.12 * s
    else:  # lying, sphinx
        make_blob(f"{prefix}_Chest", P(0.10 * s, 0.0, 0.15 * s), 0.17 * s, coat, noise=0.07, seed=5, squash=0.88)
        make_blob(f"{prefix}_Hips", P(-0.20 * s, 0.0, 0.13 * s), 0.16 * s, coat, noise=0.07, seed=3, squash=0.80)
        for sd in (-1, 1):
            # (boxes: as horizontal tapers the tail and legs recorded a
            # clip with the haberdashery's floor tiles; boxes record clean)
            make_box(f"{prefix}_Foreleg_{sd:+d}", P(0.30 * s, sd * 0.07 * s, 0.035 * s), S(0.24 * s, 0.06 * s, 0.06 * s), coat)
            make_blob(f"{prefix}_Paw_{sd:+d}", P(0.43 * s, sd * 0.07 * s, 0.03 * s), 0.035 * s, muzzle,
                      noise=0.04, seed=7, squash=0.8)
            make_blob(f"{prefix}_Hindleg_{sd:+d}", P(-0.18 * s, sd * 0.13 * s, 0.08 * s), 0.08 * s, coat,
                      noise=0.06, seed=8, squash=0.9)
        hz, hf = 0.38 * s, 0.28 * s
    # neck, head, muzzle, nose, ears, eyes
    make_blob(f"{prefix}_Neck", P(hf - 0.06 * s, 0.0, hz - 0.08 * s), 0.09 * s, coat, noise=0.05, seed=2, squash=1.1)
    make_blob(f"{prefix}_Head", P(hf, 0.0, hz), 0.10 * s, coat, noise=0.06, seed=9, squash=0.9)
    make_box(f"{prefix}_Muzzle", P(hf + 0.11 * s, 0.0, hz - 0.035 * s), S(0.12 * s, 0.08 * s, 0.07 * s), muzzle)
    make_box(f"{prefix}_Nose", P(hf + 0.175 * s, 0.0, hz - 0.015 * s), S(0.02 * s, 0.04 * s, 0.03 * s), DOG_DARK)
    for sd in (-1, 1):
        make_box(f"{prefix}_Ear_{sd:+d}", P(hf - 0.02 * s, sd * 0.085 * s, hz + 0.02 * s),
                 S(0.05 * s, 0.03 * s, 0.10 * s), DOG_DARK)
        if one_eyed and sd > 0:
            make_box(f"{prefix}_Eye_Scar_{sd:+d}", P(hf + 0.07 * s, sd * 0.058 * s, hz + 0.025 * s),
                     S(0.03 * s, 0.006 * s, 0.006 * s), DOG_DARK)
        else:
            make_cyl(f"{prefix}_Eye_{sd:+d}", P(hf + 0.07 * s, sd * 0.06 * s, hz + 0.025 * s),
                     0.012 * s, 0.006 * s, PET_EYE, segments=6, axis=AS)
    make_box(f"{prefix}_Tail", P(-0.42 * s, 0.05 * s, 0.035 * s), S(0.30 * s, 0.05 * s, 0.05 * s), coat)


def make_cat(prefix, x, y, z, heading='-Y', pose='sitting', scale=1.0, coat=CAT_GREY, dark=CAT_DARK):
    """A cat. pose: 'sitting' (upright, tail round its feet) or 'loaf'
    (paws tucked, a cat on a ledge)."""
    s = float(scale)
    P, S, AF, AS = _frame(x, y, z, heading)
    if pose == 'loaf':
        make_blob(f"{prefix}_Body", P(0.0, 0.0, 0.09 * s), 0.13 * s, coat, noise=0.06, seed=4, squash=0.70)
        hz, hf = 0.17 * s, 0.13 * s
    else:
        make_blob(f"{prefix}_Haunch", P(-0.03 * s, 0.0, 0.09 * s), 0.11 * s, coat, noise=0.06, seed=4, squash=0.85)
        make_blob(f"{prefix}_Chest", P(0.04 * s, 0.0, 0.19 * s), 0.075 * s, coat, noise=0.05, seed=6, squash=1.2)
        for sd in (-1, 1):
            make_cyl(f"{prefix}_Foreleg_{sd:+d}", P(0.07 * s, sd * 0.03 * s, 0.07 * s), 0.016 * s, 0.14 * s,
                     coat, segments=6)
        make_box(f"{prefix}_Tail", P(0.02 * s, 0.10 * s, 0.015 * s), S(0.22 * s, 0.03 * s, 0.03 * s), dark)
        hz, hf = 0.30 * s, 0.06 * s
    make_blob(f"{prefix}_Head", P(hf, 0.0, hz), 0.06 * s, coat, noise=0.05, seed=9, squash=0.92)
    make_box(f"{prefix}_Muzzle", P(hf + 0.05 * s, 0.0, hz - 0.018 * s), S(0.03 * s, 0.04 * s, 0.03 * s), coat)
    for sd in (-1, 1):
        make_taper_cyl(f"{prefix}_Ear_{sd:+d}", P(hf - 0.005 * s, sd * 0.032 * s, hz + 0.062 * s),
                       0.022 * s, 0.003 * s, 0.05 * s, dark, segments=5)
        make_cyl(f"{prefix}_Eye_{sd:+d}", P(hf + 0.046 * s, sd * 0.024 * s, hz + 0.012 * s),
                 0.009 * s, 0.005 * s, PET_EYE, segments=6, axis=AS)


# ════════════════════════════════════════════════════════════════
# BIGFOOT (2026-10-09 · the Missing Link is a Bigfoot diner — user).
# The Pacific-northwest roadside Sasquatch: mid-stride-still, long
# arms hanging past the hips, a sagittal crest, big flat feet. Built
# standing on z (the floor or a base), every part overlapping the one
# it hangs from. carved=True is the chainsaw-carved cedar greeter: a
# warmer wood tone on a round-sawn stump base, the "fur" in facets.
# ════════════════════════════════════════════════════════════════
BIGFOOT_FUR = (0.30, 0.21, 0.15, 1.0)
BIGFOOT_FACE = (0.22, 0.16, 0.12, 1.0)
CEDAR_CARVED = (0.58, 0.40, 0.26, 1.0)
CEDAR_STUMP = (0.46, 0.32, 0.22, 1.0)


def make_bigfoot(prefix, x, y, z=0.0, heading='-Y', h=2.1, carved=False, seed=3):
    """A standing Sasquatch `h` tall facing `heading` (its feet at z).
    Returns the top z of the head."""
    if carved:
        make_cyl(f"{prefix}_Stump", (x, y, z + 0.09), 0.36, 0.18, CEDAR_STUMP, segments=14)
        z += 0.18
    fur = CEDAR_CARVED if carved else BIGFOOT_FUR
    face = CEDAR_STUMP if carved else BIGFOOT_FACE
    P, S, ax_f, ax_s = _frame(x, y, z, heading)
    s = h / 2.1
    rough = 0.16 if carved else 0.34          # chainsaw facets vs shag
    for side, tag in ((-1, "L"), (1, "R")):
        # big flat feet, a step apart (one a little forward)
        make_box(f"{prefix}_Foot_{tag}", P(0.06 + (0.05 if side > 0 else 0.0), side * 0.15 * s, 0.035 * s), S(0.36 * s, 0.15 * s, 0.07 * s), face)
        make_taper_cyl(f"{prefix}_Leg_{tag}", P(0.03 + (0.03 if side > 0 else 0.0), side * 0.15 * s, 0.49 * s), 0.10 * s, 0.13 * s, 0.86 * s, fur, segments=8)   # centre-anchored: 0.06..0.92
        make_blob(f"{prefix}_Thigh_{tag}", P(0.03, side * 0.15 * s, 0.72 * s), 0.17 * s, fur, noise=rough, seed=seed + 20 + side, squash=1.5)
        make_blob(f"{prefix}_Calf_{tag}", P(0.0, side * 0.15 * s, 0.32 * s), 0.13 * s, fur, noise=rough, seed=seed + 23 + side, squash=1.6)
        # long arms hanging past the hips from sloped shoulders, a little forward
        make_taper_cyl(f"{prefix}_Arm_{tag}", P(0.08 * s, side * 0.33 * s, 1.08 * s), 0.07 * s, 0.10 * s, 0.82 * s, fur, segments=8)   # shoulder 1.49 to wrist 0.67
        for k, zz in enumerate((1.30, 0.98)):
            make_blob(f"{prefix}_ArmFur_{tag}_{k}", P(0.08 * s, side * 0.34 * s, zz * s), 0.11 * s, fur, noise=rough, seed=seed + 30 + k + side, squash=1.7)
        make_blob(f"{prefix}_Hand_{tag}", P(0.10 * s, side * 0.34 * s, 0.64 * s), 0.09 * s, face, noise=0.18, seed=seed + (1 if side > 0 else 2), squash=1.3)
        make_blob(f"{prefix}_Shoulder_{tag}", P(0.03 * s, side * 0.24 * s, 1.46 * s), 0.16 * s, fur, noise=rough, seed=seed + 5 + side, squash=0.8)
    make_blob(f"{prefix}_Hips", P(0.0, 0.0, 0.92 * s), 0.27 * s, fur, noise=rough, seed=seed + 7, squash=0.8)
    make_blob(f"{prefix}_Belly", P(0.06 * s, 0.0, 1.12 * s), 0.27 * s, fur, noise=rough, seed=seed + 12, squash=1.0)
    make_blob(f"{prefix}_Torso", P(-0.02 * s, 0.0, 1.32 * s), 0.33 * s, fur, noise=rough, seed=seed + 8, squash=1.1)
    # the head hunched forward and down on a thick neck, a crest, the face
    make_blob(f"{prefix}_Neck", P(0.06 * s, 0.0, 1.58 * s), 0.14 * s, fur, noise=rough, seed=seed + 13, squash=1.0)
    make_blob(f"{prefix}_Head", P(0.12 * s, 0.0, 1.72 * s), 0.15 * s, fur, noise=rough * 0.8, seed=seed + 9, squash=1.15)
    make_blob(f"{prefix}_Crest", P(0.08 * s, 0.0, 1.86 * s), 0.08 * s, fur, noise=0.12, seed=seed + 10, squash=1.4)
    make_blob(f"{prefix}_Face", P(0.22 * s, 0.0, 1.70 * s), 0.09 * s, face, noise=0.10, seed=seed + 14, squash=1.1)
    make_box(f"{prefix}_Brow", P(0.25 * s, 0.0, 1.77 * s), S(0.05 * s, 0.17 * s, 0.035 * s), fur)
    return z + 2.0 * s
