"""Oneironautics work-drones — the futuristic-Oregon design language.

2026-08-12, user: "the drones in land of milk and honey factor in
heavily, need a good futuristic oregon design for those."

WHAT THE PROSE ESTABLISHES (vol 7, the canon these must match):
  · They WORK. They prune salal back from trail edges, weld a
    downspout that came off in the wind, repair the frame around a
    painted window. Tools, not weapons; maintenance, not menace.
  · They keep hours. "The drones came in off the bluff in the last
    hour before dawn… by six-thirty they were all docked and the
    sky over Smolvud was empty."
  · Nobody looks up. Lena "registered the drone the way she
    registered drones, which was as a thing that was always
    somewhere in the sky." They are infrastructure, like a bus.
  · The Foundation owns them; a single unit is placeable in the
    planner's-view as a "drone-unit."

THE DESIGN, therefore — futuristic OREGON, not futuristic anywhere:

  1. WEATHER-SEALED, NOT SLEEK. This coast is rain nine months a
     year and salt air all twelve. A flush bone-gray composite
     shell with visible gasket seams and a slightly domed back so
     water sheets off. Corners radiused, no vents facing up.
  2. DUCTED FANS, NOT EXPOSED ROTORS. Four shrouded ducts on stub
     arms — quieter (they fly over sleeping towns at 1:35am), and
     safe to work near a person on a ladder. The duct rings read
     as four soft circles in silhouette: the drone's signature.
  3. IT CARRIES A TOOL. A stowed work-arm folded under the belly
     with a small effector head (the welder / the pruning shear).
     A drone with no arm is a camera; this world's drones fix
     things.
  4. ONE AMBER EYE. A single sensor lens on the nose, amber like
     every practical lamp in the game's night palette, so a drone
     reads at 40m as one warm point above a roofline.
  5. WEATHERED, MAINTAINED, MISMATCHED. Salt haze on the lower
     shell, one replacement panel in a slightly-off gray, a
     stenciled unit number. These are ten years into service and
     repaired by people who repair things.
  6. NO CHROME, NO GLOW SEAMS, NO NEON. The future here is damp
     plywood-and-composite civic competence — the opposite of the
     Basilica's chrome. If it looks like a spaceship, it's wrong.

Palette lives in DRONE_* below so every locale's drones match.

All parts share the caller's prefix (assembly rule for the overlap
audit). Callers give the drone's CENTER position — for a docked
unit that is cradle height, for a flier it is its altitude.
"""
from .geometry import make_box, make_chamfer_box, make_cyl, make_taper_cyl

# ── Palette ────────────────────────────────────────────────────
DRONE_SHELL = (0.80, 0.79, 0.75, 1.0)      # bone composite
DRONE_SHELL_PATCH = (0.71, 0.72, 0.70, 1.0)  # replacement panel
DRONE_SHELL_LO = (0.62, 0.62, 0.60, 1.0)   # salt-hazed underside
DRONE_SEAM = (0.44, 0.45, 0.46, 1.0)       # gasket seams / ducts
DRONE_TRIM = (0.30, 0.42, 0.34, 1.0)       # Oneironautics moss-green
DRONE_EYE = (0.98, 0.72, 0.30, 1.0)        # amber sensor
DRONE_ARM = (0.36, 0.36, 0.38, 1.0)        # work arm
DRONE_TOOL = (0.52, 0.50, 0.48, 1.0)       # effector head


def make_drone(prefix, x, y, z, yaw_flip=False, arm_down=False,
               scale=1.0, eye_color=DRONE_EYE):
    """One work-drone. Body 0.62m across the shell, 0.98m across
    the duct ring — a thing two people could carry.

    yaw_flip: mirror the stub arms (variety in a flight/dock row).
    arm_down: deploy the work arm below the belly (a working unit;
              default stows it flush).
    """
    s = float(scale)
    sh_w, sh_d, sh_h = 0.62 * s, 0.44 * s, 0.15 * s

    # ── Shell: chamfered body + domed back so rain sheets off ──
    make_chamfer_box("%s_Shell" % prefix, (x, y, z),
                     (sh_w, sh_d, sh_h), DRONE_SHELL)
    make_chamfer_box("%s_Shell_Crown" % prefix, (x, y, z + sh_h * 0.62),
                     (sh_w * 0.72, sh_d * 0.70, sh_h * 0.55), DRONE_SHELL)
    # Salt-hazed belly plate
    make_box("%s_Shell_Belly" % prefix, (x, y, z - sh_h * 0.52),
             (sh_w * 0.86, sh_d * 0.84, 0.02 * s), DRONE_SHELL_LO)
    # Gasket seam around the shell's waist — the sealed look
    make_box("%s_Shell_Seam" % prefix, (x, y, z + sh_h * 0.10),
             (sh_w * 1.02, sh_d * 1.02, 0.012 * s), DRONE_SEAM)
    # ONE mismatched replacement panel (top, off-center) + stencil
    make_box("%s_Shell_Patch" % prefix,
             (x + sh_w * 0.16, y - sh_d * 0.12, z + sh_h * 0.86),
             (sh_w * 0.30, sh_d * 0.34, 0.010 * s), DRONE_SHELL_PATCH)
    make_box("%s_Shell_Stencil" % prefix,
             (x - sh_w * 0.22, y - sh_d * 0.10, z + sh_h * 0.86),
             (sh_w * 0.22, sh_d * 0.12, 0.008 * s), DRONE_SEAM)
    # Foundation moss-green stripe down the spine
    make_box("%s_Shell_Stripe" % prefix, (x, y, z + sh_h * 0.87),
             (sh_w * 0.10, sh_d * 0.92, 0.009 * s), DRONE_TRIM)

    # ── Four ducted fans on stub arms ──────────────────────────
    duct_r = 0.17 * s
    ax = sh_w * 0.52 + duct_r * 0.55
    ay = sh_d * 0.62 + duct_r * 0.55
    for sgn_x in (-1, 1):
        for sgn_y in (-1, 1):
            dx, dy = x + sgn_x * ax, y + sgn_y * ay
            if yaw_flip:
                dx, dy = x + sgn_y * ax, y + sgn_x * ay
            tag = "%s%s" % ("E" if sgn_x > 0 else "W",
                            "N" if sgn_y > 0 else "S")
            # Stub arm from shell to duct
            make_box("%s_Arm_%s" % (prefix, tag),
                     ((x + dx) / 2.0, (y + dy) / 2.0, z),
                     (abs(dx - x) * 1.05, 0.07 * s, 0.055 * s),
                     DRONE_SEAM)
            # Duct ring (the silhouette signature) + hub + blade disc
            make_cyl("%s_Duct_%s" % (prefix, tag), (dx, dy, z + 0.02 * s),
                     duct_r, 0.085 * s, DRONE_SEAM, segments=12)
            make_cyl("%s_DuctLip_%s" % (prefix, tag),
                     (dx, dy, z + 0.065 * s),
                     duct_r * 1.04, 0.016 * s, DRONE_SHELL, segments=12)
            make_cyl("%s_Blades_%s" % (prefix, tag), (dx, dy, z + 0.02 * s),
                     duct_r * 0.80, 0.012 * s, DRONE_SHELL_LO, segments=10)
            make_cyl("%s_Hub_%s" % (prefix, tag), (dx, dy, z + 0.03 * s),
                     0.032 * s, 0.05 * s, DRONE_ARM, segments=8)

    # ── Amber sensor eye on the nose (front = -Y) ──────────────
    nose_y = y - sh_d * 0.52
    make_taper_cyl("%s_EyePod" % prefix, (x, nose_y - 0.02 * s, z),
                   0.055 * s, 0.045 * s, 0.09 * s, DRONE_SEAM,
                   segments=10, axis='Y')
    make_cyl("%s_Eye" % prefix, (x, nose_y - 0.07 * s, z),
             0.038 * s, 0.018 * s, eye_color, segments=10, axis='Y')

    # ── Stowed (or deployed) work arm under the belly ──────────
    belly = z - sh_h * 0.55
    if arm_down:
        make_box("%s_WorkArm_Upper" % prefix,
                 (x, y + sh_d * 0.06, belly - 0.12 * s),
                 (0.06 * s, 0.06 * s, 0.26 * s), DRONE_ARM)
        make_box("%s_WorkArm_Fore" % prefix,
                 (x, y - sh_d * 0.10, belly - 0.28 * s),
                 (0.05 * s, 0.34 * s, 0.05 * s), DRONE_ARM)
        make_box("%s_WorkArm_Head" % prefix,
                 (x, y - sh_d * 0.34, belly - 0.30 * s),
                 (0.07 * s, 0.10 * s, 0.08 * s), DRONE_TOOL)
    else:
        # Folded flush fore-aft along the belly
        make_box("%s_WorkArm_Stowed" % prefix, (x, y, belly - 0.045 * s),
                 (0.07 * s, sh_d * 0.86, 0.06 * s), DRONE_ARM)
        make_box("%s_WorkArm_Head" % prefix,
                 (x, y - sh_d * 0.40, belly - 0.045 * s),
                 (0.075 * s, 0.10 * s, 0.075 * s), DRONE_TOOL)
    # Two skids — they land on gravel and wet dock plates
    for sgn in (-1, 1):
        make_box("%s_Skid_%d" % (prefix, sgn),
                 (x + sgn * sh_w * 0.30, y, belly - 0.07 * s),
                 (0.045 * s, sh_d * 0.78, 0.035 * s), DRONE_ARM)


def make_drone_dock(prefix, x, y, base_z, n=3, spacing=1.35,
                    post_h=2.4, occupied=(True, False, True)):
    """A dock rack — the thing they come home to before six-thirty.
    A cedar post-and-beam frame (this coast builds in wood) with
    steel cradle plates, some cradles empty because those units are
    still out. `occupied` is per-cradle; extend/trim to n.
    """
    cedar = (0.44, 0.33, 0.24, 1.0)
    cedar_dk = (0.34, 0.25, 0.18, 1.0)
    steel = (0.52, 0.53, 0.55, 1.0)
    span = spacing * (n - 1) + 1.1
    # Posts + head beam
    for sgn in (-1, 1):
        make_box("%s_Post_%d" % (prefix, sgn),
                 (x + sgn * span / 2.0, y, base_z + post_h / 2.0),
                 (0.14, 0.14, post_h), cedar)
    make_box("%s_Beam" % prefix, (x, y, base_z + post_h + 0.08),
             (span + 0.30, 0.16, 0.16), cedar_dk)
    # Rain hood over the cradles (weather-sealed drones still get a roof)
    make_box("%s_Hood" % prefix, (x, y - 0.10, base_z + post_h + 0.22),
             (span + 0.50, 0.90, 0.06), cedar_dk)
    for i in range(n):
        cx = x - spacing * (n - 1) / 2.0 + i * spacing
        cz = base_z + post_h - 0.55
        make_box("%s_Cradle_%d" % (prefix, i), (cx, y, cz),
                 (0.72, 0.52, 0.05), steel)
        make_box("%s_CradleArm_%d" % (prefix, i), (cx, y, cz + 0.14),
                 (0.06, 0.50, 0.24), steel)
        # Charge umbilical hanging from the beam
        make_box("%s_Umbilical_%d" % (prefix, i),
                 (cx + 0.26, y, cz + 0.42),
                 (0.03, 0.03, 0.60), (0.22, 0.22, 0.24, 1.0))
        if i < len(occupied) and occupied[i]:
            make_drone("%s_Unit_%d" % (prefix, i), cx, y, cz + 0.20,
                       yaw_flip=(i % 2 == 1))


def make_drone_flight(prefix, x, y, z, n=3, spread=9.0, climb=1.6):
    """A loose skein of drones coming in off the bluff — spaced,
    staggered in altitude, all facing the same way. Read at
    distance as three amber points in echelon, not a formation.
    """
    for i in range(n):
        t = i / float(max(1, n - 1))
        make_drone("%s_%d" % (prefix, i),
                   x + (t - 0.5) * spread,
                   y + (0.5 - abs(t - 0.5)) * spread * 0.35,
                   z + t * climb,
                   yaw_flip=(i % 2 == 1), scale=1.0)
