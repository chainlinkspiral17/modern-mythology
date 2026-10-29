"""figures.py — stand-in PEOPLE for the sets (2026-10-29).

The sets have always built their figures inline from a torso box and a head
cylinder (build_school_field_evening's fans, its players). This is the same
grammar in one place, a little better: two legs, a torso narrower at the
waist than the shoulders, two arms, a head, hair, and an optional held
thing. They are scale and staging — a line at a door, an old man coming
down a hallway — never a character's face (the VN's portraits are the
faces). heading is the way the figure faces, in radians (0 = +Y, blender).
"""
import math
from _props.geometry import make_box, make_cyl, make_blob, make_rot_box

SKIN = (0.66, 0.52, 0.44, 1.0)


def make_standing_figure(prefix, x, y, *, heading=0.0, h=1.72, coat=(0.30, 0.32, 0.38, 1.0),
                         pants=(0.22, 0.22, 0.26, 1.0), skin=SKIN, hair=(0.20, 0.16, 0.12, 1.0),
                         dress=None, arms="down", z0=0.0, stoop=0.0):
    """One standing person. `dress` (a colour) replaces the legs' trousers
    with a skirt to the knee. arms "down" | "front" (holding something at
    the waist) | "folded". `stoop` (radians) bends the torso forward (an old
    man). Returns the (x, y, z) of the hands' middle, for a held thing."""
    s = h / 1.72
    ch, sh = math.cos(heading), math.sin(heading)

    def at(fx, fy, z):
        # figure-local (fx: right, fy: forward) -> world
        return (x + fx * ch + fy * sh, y - fx * sh + fy * ch, z0 + z)

    leg_h = 0.80 * s
    for side, fx in (("L", -0.09 * s), ("R", 0.09 * s)):
        make_rot_box(f"{prefix}_Leg_{side}", at(fx, 0.0, leg_h / 2.0), (0.13 * s, 0.15 * s, leg_h), pants, yaw=-heading)
        make_rot_box(f"{prefix}_Shoe_{side}", at(fx, 0.05 * s, 0.03 * s), (0.11 * s, 0.26 * s, 0.06 * s), (0.10, 0.09, 0.08, 1.0), yaw=-heading)
    if dress:
        make_rot_box(f"{prefix}_Skirt", at(0.0, 0.0, leg_h - 0.20 * s), (0.40 * s, 0.30 * s, 0.42 * s), dress, yaw=-heading)
    torso_h = 0.56 * s
    tz = leg_h + torso_h / 2.0
    lean = stoop * 0.22 * s
    make_rot_box(f"{prefix}_Waist", at(0.0, lean * 0.3, leg_h + 0.10 * s), (0.32 * s, 0.20 * s, 0.20 * s), dress or coat, yaw=-heading, pitch=stoop)
    make_rot_box(f"{prefix}_Torso", at(0.0, lean, tz + 0.06 * s), (0.42 * s, 0.24 * s, torso_h - 0.10 * s), dress or coat, yaw=-heading, pitch=stoop)
    head_z = leg_h + torso_h + 0.14 * s
    make_cyl(f"{prefix}_Neck", at(0.0, lean * 1.6, head_z - 0.10 * s), 0.05 * s, 0.08 * s, skin, segments=8)
    make_blob(f"{prefix}_Head", at(0.0, lean * 1.8, head_z + 0.03 * s), 0.11 * s, skin, noise=0.05, seed=len(prefix), squash=1.15)
    make_blob(f"{prefix}_Hair", at(0.0, lean * 1.8 - 0.02 * s, head_z + 0.08 * s), 0.115 * s, hair, noise=0.12, seed=len(prefix) + 7, squash=0.8)
    shoulder_z = leg_h + torso_h - 0.04 * s
    if arms == "front":
        for side, fx in (("L", -0.20 * s), ("R", 0.20 * s)):
            make_rot_box(f"{prefix}_UpperArm_{side}", at(fx, lean + 0.04 * s, shoulder_z - 0.15 * s), (0.09 * s, 0.10 * s, 0.30 * s), coat, yaw=-heading, pitch=0.35)
            make_rot_box(f"{prefix}_Forearm_{side}", at(fx * 0.7, lean + 0.20 * s, shoulder_z - 0.32 * s), (0.08 * s, 0.30 * s, 0.08 * s), coat, yaw=-heading)
            make_blob(f"{prefix}_Hand_{side}", at(fx * 0.6, lean + 0.34 * s, shoulder_z - 0.33 * s), 0.045 * s, skin, noise=0.05, seed=3, squash=0.9)
        return at(0.0, lean + 0.36 * s, shoulder_z - 0.36 * s)
    if arms == "folded":
        make_rot_box(f"{prefix}_Arms_Folded", at(0.0, lean + 0.14 * s, shoulder_z - 0.22 * s), (0.40 * s, 0.10 * s, 0.10 * s), coat, yaw=-heading)
        return at(0.0, lean + 0.16 * s, shoulder_z - 0.22 * s)
    for side, fx in (("L", -0.25 * s), ("R", 0.25 * s)):
        make_rot_box(f"{prefix}_Arm_{side}", at(fx, lean, shoulder_z - 0.30 * s), (0.09 * s, 0.10 * s, 0.58 * s), coat, yaw=-heading, pitch=stoop * 0.5)
        make_blob(f"{prefix}_Hand_{side}", at(fx, lean, shoulder_z - 0.62 * s), 0.045 * s, skin, noise=0.05, seed=5, squash=0.9)
    return at(0.0, lean + 0.10 * s, shoulder_z - 0.62 * s)
