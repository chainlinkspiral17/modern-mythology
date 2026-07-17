#!/usr/bin/env python3
"""GNM → VN hero portrait GLB generator.

Builds stylized full-figure portrait GLBs for the VN's Portrait3D tier
from Google's GNM parametric head model (https://github.com/google/GNM,
Apache 2.0). The GNM head gives each character real, distinct facial
structure; this tool then STYLIZES it to fit the project's no-texture,
vertex-color, faceted-lowpoly look:

  1. identity sampled DETERMINISTICALLY from the character key
     (crc32-seeded — same character = same face, forever), plus
     per-character hand tweaks (head scale, hair mask, palette),
  2. interior anatomy dropped (tongue / gums / teeth / mouth sock /
     eye interiors — never visible in a portrait),
  3. flat vertex-color zones painted from GNM's semantic vertex
     groups (skin, lips, scleras / irises / pupils, core brows) plus
     a computed scalp mask for painted hair and a lowpoly HAIR SHELL
     (scalp faces offset along their normals),
  4. vertex-cluster decimation + flat shading — the faceted diorama
     look, not statistical realism,
  5. welded onto a procedural angular body (hex-prism torso in the
     project's hull idiom) so Portrait3D's auto-scale heuristic
     (1.8 m figure, thigh-to-head framing) sees a normal hero GLB,
  6. exported as a self-contained GLB with COLOR_0 vertex colors
     (Godot's importer applies them as albedo automatically).

USAGE
  python3 gnm_portrait.py --gnm-path /path/to/GNM/checkout \
      [--only john_frank,sam_miller] [--preview]

The GNM checkout (with its bundled gnm_head.npz weights, ~53 MB) is a
BUILD-TIME dependency only — it is not vendored into this repo. Deps:
numpy, absl-py, etils[enp] (pip). --preview writes a software-rendered
PNG next to each GLB for eyeballing without Godot (needs pillow).

Output: godot/assets/3d/characters/heroes/<name>_gnm.glb — committed
(hero GLBs are tracked in git), so portraits ship on pull.
"""
from __future__ import annotations

import argparse
import json
import os
import struct
import sys
import tempfile
import zlib

import numpy as np

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
OUT_DIR = os.path.join(REPO, "godot", "assets", "3d", "characters", "heroes")

# ── Character book ────────────────────────────────────────────────
# seed_key: identity seed (never change once shipped — faces are canon).
# identity_sigma: how far from the mean face to wander (0.6-0.9 sane).
# head_scale: subtle skull resize (teens slightly smaller).
# hair: "short" (scalp shell) | "bob" (down to jaw) | color.
# palette: skin/hair/shirt/pants/shoes/iris colors (linear-ish sRGB).
CHARACTERS = {
    "john_frank": {
        "seed_key": "john_frank_v2",
        "anny": {"gender": 0.0, "age": 0.45, "height": 0.62, "weight": 0.38,
                 "muscle": 0.50, "cupsize": 0.0, "firmness": 1.0},
        "identity_sigma": 0.6,
        "head_scale": 1.0,
        "face_width": 0.90,                 # thin face
        "height": 1.78,
        "hair": "bangs",                    # long dark bangs over the brow
        "skin": (0.88, 0.72, 0.60),         # pale
        "hair_color": (0.14, 0.11, 0.10),   # dark
        "iris": (0.28, 0.32, 0.30),
        "outfit": "waiter",
        "shirt": (0.88, 0.88, 0.85),        # white dress shirt
        "shirt_lt": (0.94, 0.94, 0.91),
        "collar": (0.94, 0.94, 0.91),
        "tie": (0.07, 0.07, 0.09),          # black tie
        "apron": (0.10, 0.10, 0.11),        # waiter's half-apron
        "pants": (0.09, 0.09, 0.10),        # black slacks
        "shoes": (0.05, 0.05, 0.06),        # black shoes
    },
    "frasier_temple": {
        "seed_key": "frasier_temple_v2",
        "anny": {"gender": 0.0, "age": 0.45, "height": 0.68, "weight": 0.50,
                 "muscle": 0.60, "cupsize": 0.0, "firmness": 1.0, "african": 1.0},
        "identity_sigma": 0.65,
        "head_scale": 1.0,
        "face_width": 1.0,
        "height": 1.82,
        "hair": "afro",                     # slightly disheveled
        "skin": (0.42, 0.28, 0.20),         # dark brown
        "hair_color": (0.10, 0.08, 0.07),
        "iris": (0.22, 0.15, 0.10),
        "outfit": "bomber",
        "shirt": (0.30, 0.28, 0.17),        # olive bomber jacket
        "shirt_lt": (0.36, 0.34, 0.22),
        "rib": (0.18, 0.17, 0.11),          # ribbed collar/waist/cuffs
        "tee": (0.13, 0.12, 0.13),          # band tee underneath
        "alien": (0.64, 0.68, 0.64),        # the grey alien head patch
        "pants": (0.28, 0.34, 0.50),        # blue jeans
        "shoes": (0.58, 0.16, 0.18),        # stylish sneakers (crimson)
        "sole": (0.92, 0.92, 0.90),
    },
    "sam_miller": {
        "seed_key": "sam_miller_v2",
        "anny": {"gender": 1.0, "age": 0.40, "height": 0.45, "weight": 0.42,
                 "muscle": 0.40, "cupsize": 0.40},
        "identity_sigma": 0.45,
        "head_scale": 0.94,                 # 17 — slighter build
        "height": 1.65,
        "face_width": 1.0,
        "hair": "bob",                      # jaw-length
        "brows": False,                     # soft look — no painted brow band
        "skin": (0.80, 0.62, 0.48),
        "hair_color": (0.28, 0.20, 0.14),   # dark brown
        "iris": (0.30, 0.20, 0.12),
        "outfit": "kwikstop",
        "build": "female",
        "shirt": (0.16, 0.42, 0.42),        # Kwik Stop teal polo
        "shirt_lt": (0.20, 0.52, 0.52),
        "collar": (0.10, 0.28, 0.28),       # darker uniform collar
        "tag": (0.92, 0.92, 0.88),          # name tag
        "brand": (0.72, 0.20, 0.16),        # Kwik Stop red
        "pants": (0.24, 0.28, 0.38),        # jeans
        "shoes": (0.86, 0.86, 0.84),        # white sneakers
        "sole": (0.72, 0.20, 0.16),         # red soles
    },
}

LIP = lambda skin: (min(1.0, skin[0] * 1.02), skin[1] * 0.72, skin[2] * 0.70)
SCLERA = (0.90, 0.89, 0.86)
PUPIL = (0.06, 0.05, 0.05)
SKIN_SHADOW = 0.86  # multiplier under the jaw shell


# ── GNM head generation ───────────────────────────────────────────

def load_gnm(gnm_path: str):
    sys.path.insert(0, gnm_path)
    from gnm.shape import gnm_numpy                     # noqa: E402
    from gnm.shape.data.versions import gnm_specs       # noqa: E402
    return gnm_numpy.GNM.from_local(
        version=gnm_specs.GNMMajorVersion.V3,
        variant=gnm_specs.GNMVariant.HEAD)


def build_head(gnm, cfg):
    """Returns (verts (N,3), tris (T,3), colors (N,3)) — the colored,
    interior-stripped, hair-shelled GNM head at native metric scale."""
    d = gnm.to_numpy_data_dict()
    gnames = [str(x) for x in d["vertex_group_names"]]
    groups = np.asarray(d["vertex_groups"], dtype=np.float32)  # (46, N)

    def g(name):
        return groups[gnames.index(name)]

    rng = np.random.default_rng(zlib.crc32(cfg["seed_key"].encode()))
    identity = rng.normal(size=gnm.identity_dim) * cfg["identity_sigma"]
    expression = np.zeros(gnm.expression_dim)
    rotations = np.zeros((gnm.num_joints, 3))
    verts = np.asarray(gnm(identity, expression, rotations, np.zeros(3)), dtype=np.float64)
    tris = np.asarray(gnm.triangles, dtype=np.int64)
    n = verts.shape[0]

    # ── Drop interior anatomy (never visible in a VN portrait) ──
    interior = (g("tongue") + g("gums") + g("teeth") + g("mouth_sock")
                + g("eye_interiors")) > 0.5
    keep_tri = ~interior[tris].any(axis=1)
    tris = tris[keep_tri]

    # ── Paint flat color zones ──
    skin = np.array(cfg["skin"])
    colors = np.tile(skin, (n, 1))
    face_mask = np.zeros(n, dtype=bool)
    for nm in ("forehead_region", "left_brow_region", "middle_brow_region",
               "right_brow_region", "left_orbital_region", "right_orbital_region",
               "left_zygomatic_region", "right_zygomatic_region", "nose_region",
               "left_infraorbital_region", "right_infraorbital_region",
               "left_cheek_region", "right_cheek_region", "upper_lip_region",
               "lower_lip_region", "chin_region"):
        face_mask |= g(nm) > 0.35
    ears = g("ears") > 0.5
    lips = (g("upper_lip") + g("lower_lip")) > 0.5
    scleras = g("scleras") > 0.5
    irises = g("irises") > 0.5
    pupils = g("pupils") > 0.5
    brows_core = (g("left_brow_region") + g("right_brow_region")) > 0.92
    if not cfg.get("brows", True):
        brows_core &= False

    eye_y = verts[scleras, 1].mean() if scleras.any() else verts[:, 1].mean()
    scalp_floor = eye_y + (0.020 if cfg["hair"] == "afro" else 0.035)
    scalp = (g("skin_exterior") > 0.5) & (verts[:, 1] > scalp_floor) \
        & ~face_mask & ~ears
    hair_zone = scalp.copy()
    if cfg["hair"] == "bangs":
        # long bangs: the forehead (above the brows) reads as hair too
        bangs = (g("forehead_region") > 0.3) & (verts[:, 1] > eye_y + 0.026)
        hair_zone |= bangs
    if cfg["hair"] == "bob":
        # hair falls down the sides + back to jaw level
        chin_y = verts[g("chin_region") > 0.5, 1].mean()
        sides_back = (g("skin_exterior") > 0.5) & ~face_mask \
            & (verts[:, 1] > chin_y + 0.005) & (verts[:, 2] < 0.055)
        # side curtains framing the face: anything far enough off-centre
        # counts as hair even inside the temple/cheek regions
        side_x = np.abs(verts[:, 0] - verts[:, 0].mean())
        curtains = (g("skin_exterior") > 0.5) & ~ears \
            & (side_x > 0.058) & (verts[:, 1] > chin_y + 0.005) \
            & (verts[:, 1] < eye_y + 0.09) & (verts[:, 2] < 0.09)
        hair_zone |= sides_back | curtains

    hair_col = np.array(cfg["hair_color"])
    colors[hair_zone] = hair_col
    colors[lips] = np.array(LIP(cfg["skin"]))
    colors[scleras] = np.array(SCLERA)
    colors[irises] = np.array(cfg["iris"])
    colors[pupils] = np.array(PUPIL)
    colors[brows_core & ~hair_zone] = hair_col * 0.9

    # ── Hair shell: offset hair-zone faces along vertex normals ──
    vnorm = vertex_normals(verts, tris)
    hair_tris = tris[hair_zone[tris].all(axis=1)]
    used = np.unique(hair_tris)
    remap = -np.ones(n, dtype=np.int64)
    remap[used] = np.arange(used.size)
    shell_off = {"bob": 0.018, "afro": 0.034, "bangs": 0.016}.get(cfg["hair"], 0.013)
    off = np.full(used.size, shell_off)
    if cfg["hair"] == "afro":
        # deterministic per-vertex jitter — the "slightly disheveled" read
        jit = ((used * 2654435761) % 1000) / 1000.0
        off = shell_off + (jit - 0.5) * 0.016
    shell_v = verts[used] + vnorm[used] * off[:, None]
    shell_t = remap[hair_tris] + n
    shell_c = np.tile(hair_col, (used.size, 1))
    # darken the skin under the shell slightly so gaps read as depth
    colors[hair_zone] = hair_col * SKIN_SHADOW

    verts = np.vstack([verts, shell_v])
    tris = np.vstack([tris, shell_t])
    colors = np.vstack([colors, shell_c])

    # thin/widen the face about the head's x-centre
    fw = float(cfg.get("face_width", 1.0))
    if fw != 1.0:
        cx = verts[:, 0].mean()
        verts[:, 0] = (verts[:, 0] - cx) * fw + cx
    # fine-detail mask: the face (incl. eyes/lips/brows) keeps fine
    # decimation; scalp/shell/neck can go coarse
    fine = face_mask | scleras | irises | pupils | lips
    fine = np.concatenate([fine, np.zeros(len(verts) - n, dtype=bool)])

    # subtle facial shading zones — flat single-tone skin reads as a
    # mannequin; a few % of baked warmth/shadow makes it read as a face
    rosy = (g("left_zygomatic_region") + g("right_zygomatic_region")
            + g("left_cheek_region") + g("right_cheek_region")) > 0.5
    socket = (g("left_orbital_region") + g("right_orbital_region")) > 0.6
    nose = g("nose_region") > 0.55
    for mask, mult in ((rosy, (1.04, 0.95, 0.93)), (socket, (0.92, 0.90, 0.91)),
                       (nose, (1.03, 1.00, 0.98))):
        mm = mask & ~lips & ~scleras & ~irises & ~pupils & ~hair_zone
        colors[:n][mm] *= np.array(mult)
    colors = np.clip(colors, 0.0, 1.0)

    # subtle head scale about the neck base
    if cfg["head_scale"] != 1.0:
        base = verts[:, 1].min()
        verts[:, 1] = (verts[:, 1] - base) * cfg["head_scale"] + base
        verts[:, [0, 2]] *= cfg["head_scale"]

    # ── CUT the head at mid-neck. The GNM head model includes a
    # clavicle/shoulder skirt (~19cm radial extent — wider than any
    # shirt we put under it); everything below chin-5cm goes, and the
    # true neck cross-section is measured AT the cut so the body can
    # weld to it exactly. ──
    chin_mask = g("chin_region") > 0.5
    chin_y = float(verts[:n][chin_mask, 1].min())
    cut_y = chin_y - 0.032
    keep = verts[tris][:, :, 1].max(axis=1) > cut_y
    tris = tris[keep]
    band = (verts[:, 1] > cut_y + 0.004) & (verts[:, 1] < cut_y + 0.018)
    bx, bz = verts[band, 0].mean(), verts[band, 2].mean()
    rim = {
        "y": cut_y,
        "cx": float(bx),
        "cz": float(bz),
        "r": float(np.percentile(
            np.sqrt((verts[band, 0] - bx) ** 2 + (verts[band, 2] - bz) ** 2), 75)),
    }
    return verts, tris, colors, fine, rim


def vertex_normals(verts, tris):
    fn = np.cross(verts[tris[:, 1]] - verts[tris[:, 0]],
                  verts[tris[:, 2]] - verts[tris[:, 0]])
    vn = np.zeros_like(verts)
    for k in range(3):
        np.add.at(vn, tris[:, k], fn)
    ln = np.linalg.norm(vn, axis=1, keepdims=True)
    ln[ln == 0] = 1.0
    return vn / ln


def decimate_cluster(verts, tris, colors, cell=0.006, fine=None, fine_cell=0.0035):
    """Vertex-cluster decimation — snaps vertices to a grid and merges.
    THIS is the stylization step: statistical-smooth → faceted lowpoly.
    `fine` (bool per vertex) marks the face region, which clusters on
    a finer grid so eyes/lips/nose survive stylization."""
    if fine is None:
        keys = np.floor(verts / cell).astype(np.int64)
    else:
        keys = np.floor(verts / cell).astype(np.int64)
        keys_f = np.floor(verts / fine_cell).astype(np.int64)
        keys = np.where(fine[:, None], keys_f * 2 + 1, keys * 2)
    _, first_idx, inv = np.unique(keys, axis=0, return_index=True, return_inverse=True)
    # cluster position = mean of members; color = first member's zone color
    new_n = first_idx.size
    nv = np.zeros((new_n, 3))
    cnt = np.zeros((new_n, 1))
    np.add.at(nv, inv, verts)
    np.add.at(cnt, inv, 1.0)
    nv /= cnt
    nc = colors[first_idx]
    nt = inv[tris]
    good = (nt[:, 0] != nt[:, 1]) & (nt[:, 1] != nt[:, 2]) & (nt[:, 0] != nt[:, 2])
    return nv, nt[good], nc


# ── Procedural angular body (numpy make_box / hex prism idiom) ────

class MeshAcc:
    def __init__(self):
        self.v, self.t, self.c = [], [], []
        self.n = 0

    def add(self, verts, tris, color):
        self.v.append(np.asarray(verts, dtype=np.float64))
        self.t.append(np.asarray(tris, dtype=np.int64) + self.n)
        col = np.asarray(color, dtype=np.float64)
        if col.ndim == 1:
            col = np.tile(col, (len(verts), 1))
        self.c.append(col)
        self.n += len(verts)

    def merged(self):
        return np.vstack(self.v), np.vstack(self.t), np.vstack(self.c)


def box(acc, center, size, color):
    cx, cy, cz = center
    hx, hy, hz = size[0] / 2, size[1] / 2, size[2] / 2
    v = np.array([[cx - hx, cy - hy, cz - hz], [cx + hx, cy - hy, cz - hz],
                  [cx + hx, cy + hy, cz - hz], [cx - hx, cy + hy, cz - hz],
                  [cx - hx, cy - hy, cz + hz], [cx + hx, cy - hy, cz + hz],
                  [cx + hx, cy + hy, cz + hz], [cx - hx, cy + hy, cz + hz]])
    q = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (3, 0, 4, 7), (1, 2, 6, 5)]
    t = []
    for a, b, c_, d_ in q:
        t += [[a, b, c_], [a, c_, d_]]
    acc.add(v, t, color)


def loft(acc, rings):
    """Lofted octagonal cross-sections — the anatomical replacement for
    the old hex-prism slabs. rings = [(y, half_w, squash, color, cx)]
    TOP-FIRST. Each band between two rings is emitted as its own
    16-vertex group colored by the LOWER ring's color, so garment
    boundaries are crisp bands, not gradients. Octagon is rotated so a
    flat face points +Z (the camera side)."""
    ang = np.deg2rad(22.5 + np.arange(8) * 45.0)

    def ring_pts(y, hw, sq, cx):
        return np.stack([cx + np.cos(ang) * hw, np.full(8, y),
                         np.sin(ang) * hw * sq], 1)

    pts = [ring_pts(y, hw, sq, cx) for (y, hw, sq, _c, cx) in rings]
    for r in range(len(rings) - 1):
        v = np.vstack([pts[r], pts[r + 1]])         # 0-7 upper, 8-15 lower
        t = []
        for i in range(8):
            j = (i + 1) % 8
            t += [[8 + i, j, 8 + j], [8 + i, i, j]]
        acc.add(v, t, np.array(rings[r + 1][3]))
    # caps: top faces +Y (first ring), bottom faces -Y (last ring)
    t_top = [[0, i + 1, i] for i in range(1, 7)]
    acc.add(pts[0], t_top, np.array(rings[0][3]))
    t_bot = [[0, i, i + 1] for i in range(1, 7)]
    acc.add(pts[-1], t_bot, np.array(rings[-1][3]))


# Anthropometric tables (fractions of height H). Real proportions:
# shoulders ~1/4 H wide, waist narrower than chest, hips ~shoulder-
# width on men and wider-than-waist on women, arms reach mid-thigh.
_BODY_M = {
    "traps":    (-0.018, 0.056, 0.85),
    "shoulder": (-0.058, 0.110, 0.58),
    "chest":    (-0.115, 0.102, 0.62),
    "waist":    (-0.265, 0.082, 0.66),
    "hip":      (-0.480, 0.092, 0.70),
    "arm_r": 1.0, "leg_x": 0.050, "thigh": 0.050, "knee": 0.033, "ankle": 0.022,
}
_BODY_F = {
    "traps":    (-0.016, 0.048, 0.85),
    "shoulder": (-0.055, 0.096, 0.60),
    "chest":    (-0.108, 0.088, 0.66),
    "waist":    (-0.255, 0.066, 0.68),
    "hip":      (-0.480, 0.097, 0.74),
    "arm_r": 0.82, "leg_x": 0.048, "thigh": 0.052, "knee": 0.032, "ankle": 0.020,
}


def build_body(cfg, head_rim_y, head_w):
    """Anatomical lofted body scaled to cfg height, dressed per
    cfg["outfit"] ("waiter" | "kwikstop" | "bomber" | plain). Returns
    (verts, tris, colors) with the collar top at y=0. Sloped trapezius
    shoulders, chest->waist->hip taper (female table for
    build:"female"), visible neck, tapered limbs."""
    H = cfg["height"]
    outfit = cfg.get("outfit", "plain")
    B = _BODY_F if cfg.get("build") == "female" else _BODY_M
    shirt, shirt_lt = np.array(cfg["shirt"]), np.array(cfg["shirt_lt"])
    pants, shoes = np.array(cfg["pants"]), np.array(cfg["shoes"])
    skin = np.array(cfg["skin"])
    acc = MeshAcc()
    ankle_y = -H * 0.915

    def R(name, color, y=None, hw=None, sq=None):
        ry, rhw, rsq = B[name]
        return ((y if y is not None else ry) * H,
                (hw if hw is not None else rhw) * H,
                sq if sq is not None else rsq, color, 0.0)

    # ── torso loft (top-first rings; band takes lower ring's color) ──
    if outfit == "waiter":
        torso = [R("traps", shirt), R("shoulder", shirt), R("chest", shirt),
                 R("waist", shirt), (-H * 0.295, H * 0.080, 0.66, shirt, 0.0),
                 R("hip", pants)]
    elif outfit == "kwikstop":
        torso = [R("traps", shirt), R("shoulder", shirt), R("chest", shirt),
                 R("waist", shirt), (-H * 0.310, H * 0.086, 0.68, shirt, 0.0),
                 R("hip", pants)]
    elif outfit == "bomber":
        rib = np.array(cfg.get("rib", (shirt * 0.62).tolist()))
        torso = [R("traps", shirt), R("shoulder", shirt, hw=B["shoulder"][1] + 0.008, sq=0.60),
                 R("chest", shirt, hw=B["chest"][1] + 0.010, sq=0.64),
                 (-H * 0.320, H * 0.096, 0.68, shirt, 0.0),
                 (-H * 0.345, H * 0.076, 0.68, rib, 0.0),
                 R("hip", pants)]
    else:
        torso = [R("traps", shirt), R("shoulder", shirt), R("chest", shirt),
                 R("waist", shirt), R("hip", pants)]
    loft(acc, torso)
    torso_prof = [(y, hw * sq) for (y, hw, sq, _c, _cx) in torso]

    def front_z(y):
        ys = [a for (a, _b) in torso_prof]
        zs = [b for (_a, b) in torso_prof]
        return float(np.interp(y, ys[::-1], zs[::-1]))

    # ── neck: welded to the head's open rim (rim sits at y=-0.05
    # after seating). The tube starts INSIDE the head above the rim
    # and runs down into the torso, so the open rim is always backed
    # by neck geometry — no see-through, no floating head. ──
    nr = cfg.get("_neck_r", H * 0.034)
    loft(acc, [(0.012, nr * 0.96, 0.98, skin, 0.0),
               (-0.090, nr * 1.04, 0.98, skin, 0.0)])
    # collar ring around the junction (rib for bombers, collar/shirt
    # otherwise) — hides the head/body weld completely
    if outfit == "bomber":
        cring = np.array(cfg.get("rib", (shirt * 0.62).tolist()))
    else:
        cring = np.array(cfg.get("collar", shirt_lt.tolist()))
    # tight band hugging the neck, ending exactly at the torso's top
    # cap — a crew/polo collar, not a flared ruff
    traps_top = B["traps"][0] * H
    loft(acc, [(0.004, nr * 1.16, 0.97, cring, 0.0),
               (traps_top, nr * 1.26, 0.97, cring, 0.0)])

    # ── arms: shoulder -> elbow -> wrist, tapered, slight outward drift ──
    ar = B["arm_r"]
    shx = B["shoulder"][1] * 0.94
    for sgn in (-1, 1):
        jx = lambda off: sgn * (shx + off) * H
        if outfit == "kwikstop":       # short sleeves — bare forearms
            arm = [(-H * 0.062, H * 0.031 * ar, 1.0, shirt_lt, jx(0.0)),
                   (-H * 0.150, H * 0.028 * ar, 1.0, shirt_lt, jx(0.006)),
                   (-H * 0.160, H * 0.026 * ar, 1.0, skin, jx(0.007)),
                   (-H * 0.250, H * 0.024 * ar, 1.0, skin, jx(0.014)),
                   (-H * 0.410, H * 0.017 * ar, 1.0, skin, jx(0.026))]
        elif outfit == "bomber":       # jacket sleeves + rib cuffs
            rib = np.array(cfg.get("rib", (shirt * 0.62).tolist()))
            arm = [(-H * 0.062, H * 0.036 * ar, 1.0, shirt, jx(0.0)),
                   (-H * 0.250, H * 0.030 * ar, 1.0, shirt, jx(0.014)),
                   (-H * 0.385, H * 0.024 * ar, 1.0, shirt, jx(0.024)),
                   (-H * 0.408, H * 0.019 * ar, 1.0, rib, jx(0.026))]
        else:                          # long sleeves to the wrist
            arm = [(-H * 0.062, H * 0.031 * ar, 1.0, shirt_lt, jx(0.0)),
                   (-H * 0.250, H * 0.025 * ar, 1.0, shirt, jx(0.014)),
                   (-H * 0.410, H * 0.018 * ar, 1.0, shirt, jx(0.026))]
        loft(acc, arm)
        # hand
        hx = jx(0.028)
        box(acc, (hx, -H * 0.443, 0.004), (H * 0.030, H * 0.052, H * 0.036), skin)

    # ── legs: hip -> knee -> ankle, thigh thicker than calf ──
    for sgn in (-1, 1):
        lx = sgn * B["leg_x"] * H
        loft(acc, [(-H * 0.465, H * B["thigh"], 0.92, pants, lx),
                   (-H * 0.715, H * B["knee"], 0.95, pants, lx),
                   (ankle_y, H * B["ankle"], 0.95, pants, lx)])

    # ── shoes ──
    for sgn in (-1, 1):
        lx = sgn * B["leg_x"] * H
        if outfit in ("kwikstop", "bomber"):
            sole = np.array(cfg.get("sole", (0.92, 0.92, 0.90)))
            box(acc, (lx, ankle_y - H * 0.040, H * 0.018), (H * 0.058, H * 0.014, H * 0.115), sole)
            box(acc, (lx, ankle_y - H * 0.018, H * 0.018), (H * 0.054, H * 0.032, H * 0.105), shoes)
            box(acc, (lx, ankle_y - H * 0.016, H * 0.062), (H * 0.042, H * 0.022, H * 0.026), sole)
        else:
            box(acc, (lx, ankle_y - H * 0.026, H * 0.016), (H * 0.056, H * 0.048, H * 0.110), shoes)

    # ── outfit dressing (front pieces follow the torso taper) ──
    if outfit == "waiter":
        tie = np.array(cfg.get("tie", (0.08, 0.08, 0.10)))
        apron = np.array(cfg.get("apron", (0.10, 0.10, 0.11)))
        box(acc, (0, -H * 0.045, front_z(-H * 0.045) + 0.006), (H * 0.018, H * 0.016, 0.010), tie)
        for (ya, yb, w) in ((-0.055, -0.105, 0.012), (-0.105, -0.155, 0.015), (-0.155, -0.205, 0.018)):
            ym = H * (ya + yb) / 2
            box(acc, (0, ym, front_z(ym) + 0.005), (H * w, H * (ya - yb), 0.007), tie)
        wb_y = -H * 0.292
        box(acc, (0, wb_y, front_z(wb_y) + 0.005), (H * 0.165, H * 0.018, 0.009), apron)
        box(acc, (0, -H * 0.44, front_z(-H * 0.31) + 0.008), (H * 0.150, H * 0.30, 0.007), apron)
    elif outfit == "kwikstop":
        tag = np.array(cfg.get("tag", (0.92, 0.92, 0.88)))
        brand = np.array(cfg.get("brand", (0.72, 0.20, 0.16)))
        box(acc, (-H * 0.040, -H * 0.095, front_z(-H * 0.095) + 0.005), (H * 0.028, H * 0.014, 0.007), tag)
        box(acc, (-H * 0.040, -H * 0.091, front_z(-H * 0.091) + 0.009), (H * 0.024, H * 0.0035, 0.005), brand)
        box(acc, (0, -H * 0.062, front_z(-H * 0.062) + 0.004), (H * 0.11, H * 0.009, 0.007), brand)
    elif outfit == "bomber":
        tee = np.array(cfg.get("tee", (0.13, 0.12, 0.13)))
        zipp = np.array(cfg.get("zip", (0.70, 0.70, 0.72)))
        box(acc, (0, -H * 0.052, front_z(-H * 0.052) + 0.004), (H * 0.046, H * 0.052, 0.008), tee)
        box(acc, (0, -H * 0.058, front_z(-H * 0.058) + 0.009), (H * 0.026, H * 0.011, 0.004), zipp)
        for (ya, yb) in ((-0.080, -0.19), (-0.19, -0.315)):
            ym = H * (ya + yb) / 2
            box(acc, (0, ym, front_z(ym) + 0.004), (H * 0.007, H * (ya - yb), 0.006), zipp)
        grey = np.array(cfg.get("alien", (0.64, 0.68, 0.64)))
        ink = np.array((0.06, 0.07, 0.06))
        ax, ay = H * 0.048, -H * 0.110
        az = front_z(ay) + 0.006
        box(acc, (ax, ay + H * 0.011, az), (H * 0.036, H * 0.020, 0.006), grey)
        box(acc, (ax, ay - H * 0.005, az), (H * 0.025, H * 0.013, 0.006), grey)
        box(acc, (ax, ay - H * 0.014, az), (H * 0.012, H * 0.007, 0.006), grey)
        for e in (-1, 1):
            box(acc, (ax + e * H * 0.009, ay + H * 0.009, az + 0.004), (H * 0.010, H * 0.005, 0.004), ink)
        box(acc, (-H * 0.048, -H * 0.100, front_z(-H * 0.100) + 0.006), (H * 0.027, H * 0.016, 0.006),
            np.array((0.62, 0.14, 0.14)))
        box(acc, (-H * 0.048, -H * 0.128, front_z(-H * 0.128) + 0.006), (H * 0.023, H * 0.012, 0.006),
            np.array((0.88, 0.82, 0.30)))
        arm_out = (shx + 0.006) * H + H * 0.036 * ar
        box(acc, (-arm_out, -H * 0.10, 0.008), (0.006, H * 0.024, H * 0.024), np.array((0.24, 0.62, 0.66)))
        box(acc, (arm_out, -H * 0.11, 0.008), (0.006, H * 0.020, H * 0.028), np.array((0.86, 0.60, 0.18)))
        box(acc, (arm_out, -H * 0.11, 0.008), (0.008, H * 0.007, H * 0.011), ink)
    return acc.merged()


# ── Anny full-body base (github.com/naver/anny — Apache 2.0 code,
# CC0 MakeHuman-derived assets in the native topology) ─────────────
# The realistic parametric body under the wardrobe. Bone skinning
# weights double as garment segmentation: a vertex belongs to a
# garment zone when the summed weight of that zone's bones wins.

_ANNY_MODEL = None


def _anny_model():
    global _ANNY_MODEL
    if _ANNY_MODEL is None:
        import anny as _anny
        _ANNY_MODEL = _anny.create_fullbody_model(topology="default",
                                                  triangulate_faces=True,
                                                  all_phenotypes=True)
    return _ANNY_MODEL


def _zone_weights(model, bone_substrings):
    """Per-vertex summed skinning weight over bones whose label contains
    any of the given substrings."""
    import numpy as _np
    labels = [str(b) for b in model.bone_labels]
    idx = [i for i, b in enumerate(labels)
           if any(ss in b for ss in bone_substrings)]
    vbi = model.vertex_bone_indices.detach().numpy()
    vbw = model.vertex_bone_weights.detach().numpy()
    sel = _np.isin(vbi, _np.array(idx, dtype=vbi.dtype))
    return (vbw * sel).sum(axis=1)


def build_body_anny(cfg):
    """Anny body: forward the phenotype, convert to Godot frame (Y-up,
    face +Z), CUT the head at the head-bone base (the GNM head replaces
    everything above the neck), paint wardrobe zones by ARGMAX bone
    weights with clean horizontal hem/ankle lines, decimate. Returns
    (verts, tris, colors, neck) with neck = the weld-plane ring."""
    import torch
    model = _anny_model()
    with torch.no_grad():
        out = model.forward(phenotype_kwargs=dict(cfg["anny"]))
    v = out["vertices"][0].detach().numpy().astype(np.float64)
    tris = model.faces.detach().numpy().astype(np.int64)
    bone_heads = out["rest_bone_heads"][0].detach().numpy().astype(np.float64)
    # anny frame: height along +Z, depth along Y → godot (x, z, -y)
    v = np.stack([v[:, 0], v[:, 2], -v[:, 1]], axis=1)
    bh = np.stack([bone_heads[:, 0], bone_heads[:, 2], -bone_heads[:, 1]], axis=1)
    floor = v[:, 1].min()
    v[:, 1] -= floor
    bh[:, 1] -= floor
    Hb = float(v[:, 1].max())

    # ── find the neck GEOMETRICALLY: the narrowest cross-section
    # between the shoulders and the skull (bone origins proved
    # unreliable — the "head" bone sits at eye level in this rig) ──
    def width_at(yy):
        band_m = np.abs(v[:, 1] - yy) < 0.008
        if not band_m.any():
            return 1e9
        return float(np.sqrt(v[band_m, 0] ** 2
                             + (v[band_m, 2] - v[band_m, 2].mean()) ** 2).max())
    Hb0 = float(v[:, 1].max())
    ys = np.arange(0.80 * Hb0, 0.93 * Hb0, 0.005)
    widths = np.array([width_at(yy) for yy in ys])
    y_neck_min = float(ys[widths.argmin()])
    y_cut = y_neck_min + 0.012                      # just above the narrowest point

    outfit = cfg.get("outfit", "plain")
    skin = np.array(cfg["skin"])
    shirt, shirt_lt = np.array(cfg["shirt"]), np.array(cfg["shirt_lt"])
    pants, shoes = np.array(cfg["pants"]), np.array(cfg["shoes"])
    rib = np.array(cfg.get("rib", (shirt * 0.62).tolist()))
    sole = np.array(cfg.get("sole", shoes.tolist()))

    # ── argmax zoning: every vertex gets exactly ONE zone, so garment
    # boundaries are smooth weight-crossover curves, not 0.5-threshold
    # spikes ──
    zone_w = np.stack([
        _zone_weights(model, ["spine", "chest", "breast", "root", "pelvis",
                              "clavicle", "shoulder"]),          # 0 torso
        _zone_weights(model, ["upperarm"]),                       # 1 upper arm
        _zone_weights(model, ["lowerarm"]),                       # 2 forearm
        _zone_weights(model, ["wrist", "finger", "metacarpal", "thumb"]),  # 3 hand
        _zone_weights(model, ["upperleg", "lowerleg"]),           # 4 legs
        _zone_weights(model, ["foot", "toe"]),                    # 5 feet
        _zone_weights(model, ["neck", "head", "special", "jaw", "eye",
                              "tongue", "oris", "orbicularis", "levator",
                              "risorius", "temporalis", "oculi"]),  # 6 neck/head
    ])
    zone = zone_w.argmax(axis=0)

    short_sleeves = outfit == "kwikstop"
    zone_cols = {
        0: shirt,
        1: shirt_lt if short_sleeves else shirt,
        2: skin if short_sleeves else shirt,
        3: skin,
        4: pants,
        5: shoes,
        6: skin,
    }
    colors = np.stack([zone_cols[z] for z in zone])

    # ── horizontal garment lines (clean hems, no zigzag) ──
    hem_y = Hb * (0.60 if outfit == "bomber" else 0.565)
    body_zone = np.isin(zone, (0, 4))
    colors[body_zone & (v[:, 1] > hem_y)] = shirt      # shirt down TO the hem…
    colors[(zone == 0) & (v[:, 1] <= hem_y)] = pants   # …and pants below it
    if outfit == "bomber":
        rib_band = body_zone & (v[:, 1] > hem_y) & (v[:, 1] < hem_y + 0.032)
        colors[rib_band] = rib
        cuffs = (zone == 2) & (zone_w[3] > 0.10)
        colors[cuffs] = rib
    # crew-neck line: a clean horizontal collar boundary (the argmax
    # neck/torso crossover is ragged at 9mm decimation)
    collar_y = float(v[:, 1].max())  # placeholder, refined below
    ankle_y = Hb * 0.062
    low = v[:, 1] < ankle_y
    colors[low] = shoes                                # shoe below the line…
    colors[(zone == 5) & ~low] = pants                 # …pants above it
    colors[low & (v[:, 1] < Hb * 0.018)] = sole        # sole tone at the ground

    # ── GARMENT VOLUME: clothes are not skin — displace every clothed
    # vertex outward along its normal so shirts/jackets/pants read as
    # cloth tubes around the body (sewing-pattern ease, not paint).
    # Cuffs/hems/collars get a natural cloth step where offsets end. ──
    vn_all = vertex_normals(v, tris)

    def col_mask(col):
        return (np.abs(colors - np.asarray(col)) < 1e-6).all(axis=1)

    ease = np.zeros(len(v))
    if outfit == "bomber":
        ease[col_mask(shirt)] = 0.026      # jacket built up around the torso
        ease[col_mask(rib)] = 0.016
    elif outfit == "waiter":
        ease[col_mask(shirt)] = 0.012      # dress shirt drape
        ease[col_mask(shirt_lt)] = 0.012
    else:
        ease[col_mask(shirt)] = 0.009      # polo
        ease[col_mask(shirt_lt)] = 0.009
    ease[col_mask(pants)] = 0.007          # denim/slacks over the legs
    ease[col_mask(shoes)] = 0.005
    # arms in sleeves: sleeves hang looser than the torso knit
    sleeve = np.isin(zone, (1, 2)) & (ease > 0)
    ease[sleeve] = np.maximum(ease[sleeve], 0.013 if outfit != "kwikstop" else 0.010)
    v = v + vn_all * ease[:, None]

    # dilate garment color one ring into the skin at every opening
    # (neckline / cuffs / shoe tops): boundary triangles otherwise
    # stretch skin-colored flaps from the body out to the inflated
    # cloth — dilated, the step reads as the garment edge overlapping
    gm = ease > 0.0
    tri_g = gm[tris]
    mixed = tri_g.any(axis=1) & (~tri_g).any(axis=1)
    for t in tris[mixed]:
        g_corner = t[gm[t]][0]
        for vi in t[~gm[t]]:
            colors[vi] = colors[g_corner]

    # ── cut the head at the skull base ──
    above = v[:, 1] > y_cut
    tris = tris[~above[tris].any(axis=1)]

    # ── weld-plane ring (for the bridge + collar) ──
    band = (v[:, 1] > y_cut - 0.030) & (v[:, 1] < y_cut - 0.004)
    bx, bz = float(v[band, 0].mean()), float(v[band, 2].mean())
    # shoulder/collar anchors as fixed anatomical drops below the neck
    # cut (a widest-band scan catches the spread A-pose arms instead
    # of the shoulders)
    sh_y = y_cut - 0.075                    # ~sternal notch
    neck_line = y_cut - 0.050               # crew-collar line
    ccol = rib if outfit == "bomber" else shirt
    colors[(zone == 6) & (v[:, 1] < neck_line)] = ccol
    near_axis = np.abs(v[:, 0]) < 0.10
    colors[(zone == 0) & (v[:, 1] > neck_line) & near_axis] = skin
    neck = {
        "y": y_cut,
        "cx": bx,
        "cz": bz,
        "r": float(np.percentile(
            np.sqrt((v[band, 0] - bx) ** 2 + (v[band, 2] - bz) ** 2), 80)),
        "shoulder_y": sh_y,
    }

    v2, t2, c2 = decimate_cluster(v, tris, colors, cell=0.009)

    # snap vertices near each garment line ONTO the line — creates a
    # real edge loop so boundary triangles end exactly at the hem
    for line_y in (hem_y, ankle_y, y_cut - 0.050):
        snap = np.abs(v2[:, 1] - line_y) < 0.0095
        v2[snap, 1] = line_y
    # ── re-cut the garment lines AFTER decimation (clustering bleeds
    # colors across the boundary; re-painting on the decimated verts
    # makes hem / ankle / crew lines crisp) ──
    def m_is(col):
        return (np.abs(c2 - np.asarray(col)) < 1e-6).all(axis=1)

    trunk = np.abs(v2[:, 0]) < 0.22
    sh_m, pa_m, sk_m, ho_m = m_is(shirt), m_is(pants), m_is(skin), m_is(shoes)
    c2[sh_m & (v2[:, 1] <= hem_y) & trunk] = pants
    c2[pa_m & (v2[:, 1] > hem_y) & trunk & (v2[:, 1] < y_cut - 0.10)] = shirt
    if outfit == "bomber":
        band2 = trunk & (v2[:, 1] > hem_y) & (v2[:, 1] < hem_y + 0.032) \
            & (m_is(shirt) | m_is(pants))
        c2[band2] = rib
    pa_m, ho_m = m_is(pants), m_is(shoes)
    c2[pa_m & (v2[:, 1] < ankle_y)] = shoes
    c2[ho_m & (v2[:, 1] > ankle_y)] = pants
    c2[m_is(shoes) & (v2[:, 1] < Hb * 0.018)] = sole
    # crew line: garment above it (near the axis) becomes skin; stray
    # skin below it AWAY from the neck becomes collar color
    r_xz = np.sqrt((v2[:, 0] - bx) ** 2 + (v2[:, 2] - bz) ** 2)
    near = np.abs(v2[:, 0]) < 0.16
    c2[m_is(ccol) & (v2[:, 1] > neck_line) & near] = skin
    c2[m_is(skin) & (v2[:, 1] < neck_line) & (v2[:, 1] > hem_y)
       & (r_xz > neck["r"] * 1.6) & trunk & (v2[:, 1] < y_cut - 0.02)] = ccol
    return v2, t2, c2, neck


def body_front_z(verts, y, half_band=0.02):
    """Front-face z of the (welded) figure at height y — sampled from
    the actual mesh so accessories sit ON the body."""
    band = np.abs(verts[:, 1] - y) < half_band
    band &= np.abs(verts[:, 0]) < 0.09
    if not band.any():
        return 0.10
    return float(verts[band, 2].max())


def dress_accessories(acc, cfg, verts, neck):
    """Proud accessory geometry on the painted anny body — collar ring
    at the weld, then per-outfit dressing anchored to the SHOULDER line
    (bone-derived), positioned by sampling the real body profile."""
    outfit = cfg.get("outfit", "plain")
    Hb = float(verts[:, 1].max())
    shirt_lt = np.array(cfg["shirt_lt"])
    ny = neck["y"]
    sh = neck["shoulder_y"]
    nr = neck["r"]

    def fz(y):
        return body_front_z(verts, y)

    # collar at the ACTUAL head/body junction (the dropped seat): a
    # stand collar sized to the head's neck stub — most shirts have
    # collars, jackets a built-up one
    cring = np.array(cfg.get("rib", (np.array(cfg["shirt"]) * 0.62).tolist())) \
        if outfit == "bomber" else np.array(cfg.get("collar", shirt_lt.tolist()))
    sy = cfg.get("_seat_y", ny)
    rr = cfg.get("_rim_r", nr)
    c_h = 0.055 if outfit == "bomber" else 0.042   # jacket collar taller
    loft(acc, [(sy + 0.026, rr * 1.05, 0.97, cring, neck["cx"]),
               (sy - c_h + 0.026, rr * (1.30 if outfit == "bomber" else 1.20),
                0.97, cring, neck["cx"])])

    if outfit == "waiter":
        tie = np.array(cfg.get("tie", (0.08, 0.08, 0.10)))
        apron = np.array(cfg.get("apron", (0.10, 0.10, 0.11)))
        knot_y = sh + 0.005
        box(acc, (0, knot_y, fz(knot_y) + 0.006), (0.030, 0.026, 0.012), tie)
        for (d0, d1, w) in ((0.015, 0.09, 0.020), (0.09, 0.165, 0.025), (0.165, 0.235, 0.030)):
            ym = knot_y - (d0 + d1) / 2
            box(acc, (0, ym, fz(ym) + 0.005), (w, d1 - d0, 0.008), tie)
        wb_y = Hb * 0.575
        box(acc, (0, wb_y, fz(wb_y) + 0.006), (0.30, 0.028, 0.010), apron)
        box(acc, (0, wb_y - 0.27, fz(wb_y) + 0.010), (0.27, 0.50, 0.008), apron)
    elif outfit == "kwikstop":
        tag = np.array(cfg.get("tag", (0.92, 0.92, 0.88)))
        brand = np.array(cfg.get("brand", (0.72, 0.20, 0.16)))
        ty = sh - 0.075
        box(acc, (-0.068, ty, fz(ty) + 0.006), (0.048, 0.025, 0.008), tag)
        box(acc, (-0.068, ty + 0.007, fz(ty) + 0.010), (0.042, 0.006, 0.006), brand)
        sy = sh - 0.035
        box(acc, (0, sy, fz(sy) + 0.005), (0.18, 0.013, 0.008), brand)
    elif outfit == "bomber":
        tee = np.array(cfg.get("tee", (0.13, 0.12, 0.13)))
        zipp = np.array(cfg.get("zip", (0.70, 0.70, 0.72)))
        tv = sh - 0.015
        box(acc, (0, tv, fz(tv) + 0.005), (0.080, 0.070, 0.010), tee)
        hem_y = Hb * 0.60
        zm = (sh - 0.05 + hem_y) / 2
        box(acc, (0, zm, fz(zm) + 0.005), (0.012, (sh - 0.05) - hem_y, 0.008), zipp)
        grey = np.array(cfg.get("alien", (0.64, 0.68, 0.64)))
        ink = np.array((0.06, 0.07, 0.06))
        ax, ay = 0.082, sh - 0.105
        az = fz(ay) + 0.008
        box(acc, (ax, ay + 0.020, az), (0.060, 0.034, 0.007), grey)
        box(acc, (ax, ay - 0.006, az), (0.042, 0.020, 0.007), grey)
        box(acc, (ax, ay - 0.021, az), (0.021, 0.011, 0.007), grey)
        for e in (-1, 1):
            box(acc, (ax + e * 0.015, ay + 0.017, az + 0.005), (0.016, 0.008, 0.005), ink)
        py = sh - 0.095
        box(acc, (-0.082, py, fz(py) + 0.008), (0.046, 0.027, 0.007), np.array((0.62, 0.14, 0.14)))
        box(acc, (-0.082, py - 0.043, fz(py - 0.043) + 0.008), (0.038, 0.021, 0.007),
            np.array((0.88, 0.82, 0.30)))
        ay2 = sh - 0.075
        band = np.abs(verts[:, 1] - ay2) < 0.03
        if band.any():
            arm_x = float(np.abs(verts[band, 0]).max())
            box(acc, (-arm_x - 0.002, ay2, 0.0), (0.008, 0.038, 0.038), np.array((0.24, 0.62, 0.66)))
            box(acc, (arm_x + 0.002, ay2 - 0.01, 0.0), (0.008, 0.032, 0.044), np.array((0.86, 0.60, 0.18)))
            box(acc, (arm_x + 0.004, ay2 - 0.01, 0.0), (0.010, 0.011, 0.017), ink)


# ── Flat shading + GLB writer ─────────────────────────────────────

def flat_shade(verts, tris, colors):
    """Split every triangle to unique vertices with the face normal —
    the faceted look. Returns (pos, nrm, col) float32, no index reuse."""
    p = verts[tris].reshape(-1, 3)
    fn = np.cross(verts[tris[:, 1]] - verts[tris[:, 0]],
                  verts[tris[:, 2]] - verts[tris[:, 0]])
    ln = np.linalg.norm(fn, axis=1, keepdims=True)
    ln[ln == 0] = 1.0
    fn = fn / ln
    nrm = np.repeat(fn, 3, axis=0)
    # ONE color per triangle (first corner's) — per-corner colors
    # interpolate across boundary triangles and fringe every garment
    # line; single-color triangles keep the lowpoly zones crisp
    col = np.repeat(colors[tris[:, 0]], 3, axis=0)
    return p.astype(np.float32), nrm.astype(np.float32), col.astype(np.float32)


def write_glb(path, pos, nrm, col, mesh_name):
    pos_b = pos.tobytes()
    nrm_b = nrm.tobytes()
    col_rgba = np.concatenate([col, np.ones((col.shape[0], 1), np.float32)], axis=1)
    col_b = col_rgba.astype(np.float32).tobytes()
    bin_chunk = pos_b + nrm_b + col_b
    while len(bin_chunk) % 4:
        bin_chunk += b"\x00"
    nverts = pos.shape[0]
    gltf = {
        "asset": {"version": "2.0", "generator": "gnm_portrait.py (GNM Apache-2.0)"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": mesh_name}],
        "meshes": [{"name": mesh_name, "primitives": [{
            "attributes": {"POSITION": 0, "NORMAL": 1, "COLOR_0": 2},
            "material": 0, "mode": 4}]}],
        "materials": [{"name": "VertexColor", "pbrMetallicRoughness": {
            "baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0.0,
            "roughnessFactor": 1.0}}],
        "buffers": [{"byteLength": len(bin_chunk)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": len(pos_b), "target": 34962},
            {"buffer": 0, "byteOffset": len(pos_b), "byteLength": len(nrm_b), "target": 34962},
            {"buffer": 0, "byteOffset": len(pos_b) + len(nrm_b), "byteLength": len(col_b), "target": 34962},
        ],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": nverts, "type": "VEC3",
             "min": pos.min(0).tolist(), "max": pos.max(0).tolist()},
            {"bufferView": 1, "componentType": 5126, "count": nverts, "type": "VEC3"},
            {"bufferView": 2, "componentType": 5126, "count": nverts, "type": "VEC4"},
        ],
    }
    js = json.dumps(gltf, separators=(",", ":")).encode()
    while len(js) % 4:
        js += b" "
    total = 12 + 8 + len(js) + 8 + len(bin_chunk)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(js), 0x4E4F534A))
        f.write(js)
        f.write(struct.pack("<II", len(bin_chunk), 0x004E4942))
        f.write(bin_chunk)


def preview_png(path, pos, nrm, col, yaw_deg=18.0):
    """Tiny software rasterizer — orthographic 3/4 view, lambert lit."""
    try:
        from PIL import Image
    except ImportError:
        print("  (pillow not installed — skipping preview)")
        return
    W, Hh = 460, 640
    yaw = np.deg2rad(yaw_deg)
    rot = np.array([[np.cos(yaw), 0, np.sin(yaw)], [0, 1, 0], [-np.sin(yaw), 0, np.cos(yaw)]])
    p = pos @ rot.T
    n = nrm @ rot.T
    y0, y1 = p[:, 1].min(), p[:, 1].max()
    scale = (Hh - 40) / (y1 - y0)
    sx = (p[:, 0] - p[:, 0].mean()) * scale + W / 2
    sy = (y1 - p[:, 1]) * scale + 20
    depth = p[:, 2]
    light = np.array([0.45, 0.35, 0.82])
    light = light / np.linalg.norm(light)
    lam = np.clip(n @ light, 0, 1) * 0.75 + 0.35
    img = np.zeros((Hh, W, 3), np.float32)
    zbuf = np.full((Hh, W), -1e9, np.float32)
    tri_n = pos.shape[0] // 3
    order = np.argsort(depth.reshape(tri_n, 3).mean(1))
    for ti in order:
        i = ti * 3
        xs, ys = sx[i:i + 3], sy[i:i + 3]
        z = depth[i:i + 3].mean()
        c = (col[i] * lam[i:i + 3].mean())
        x0, x1 = int(max(0, xs.min())), int(min(W - 1, xs.max()) + 1)
        yy0, yy1 = int(max(0, ys.min())), int(min(Hh - 1, ys.max()) + 1)
        if x1 <= x0 or yy1 <= yy0 or (x1 - x0) * (yy1 - yy0) > 60000:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(yy0, yy1) + 0.5)
        d = np.stack([(xs[1] - xs[0]) * (gy - ys[0]) - (ys[1] - ys[0]) * (gx - xs[0]),
                      (xs[2] - xs[1]) * (gy - ys[1]) - (ys[2] - ys[1]) * (gx - xs[1]),
                      (xs[0] - xs[2]) * (gy - ys[2]) - (ys[0] - ys[2]) * (gx - xs[2])])
        inside = (d >= 0).all(0) | (d <= 0).all(0)
        zwin = zbuf[yy0:yy1, x0:x1]
        m = inside & (z > zwin)
        zwin[m] = z
        img[yy0:yy1, x0:x1][m] = np.clip(c, 0, 1)
    Image.fromarray((img * 255).astype(np.uint8)).save(path)
    print(f"  preview → {path}")


# ── main ──────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gnm-path", required=True, help="path to a google/GNM checkout")
    ap.add_argument("--only", default="", help="comma list of character keys")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--preview-dir", default="", help="where preview PNGs go (default: system temp — NEVER the assets dir, Godot would import them)")
    args = ap.parse_args()

    gnm = load_gnm(args.gnm_path)
    wanted = [k.strip() for k in args.only.split(",") if k.strip()] or list(CHARACTERS)
    os.makedirs(args.out_dir, exist_ok=True)
    for key in wanted:
        cfg = CHARACTERS[key]
        print(f"[{key}] generating head…")
        hv, ht, hc, fine, rim = build_head(gnm, cfg)
        hv, ht, hc = decimate_cluster(hv, ht, hc, cell=0.0065, fine=fine, fine_cell=0.0035)
        print(f"  head after decimation: {len(hv)} verts / {len(ht)} tris")
        if "anny" in cfg:
            # ── Anny full-body base: weld the GNM head onto the anny
            # neck. Scale the head so its neck cross-section matches,
            # centre it on the neck ring, overlap 20mm down INTO it. ──
            bv, bt, bc, neck = build_body_anny(cfg)
            # seat the head DOWN INTO the body: the rim lands head_drop
            # below the anny weld plane (default ~3.3in — heads read
            # perched without it; tune per character if needed)
            drop = float(cfg.get("head_drop", 0.085))
            seat_y = neck["y"] - drop
            hv = hv - np.array([rim["cx"], 0.0, rim["cz"]])
            hv[:, 1] += seat_y - rim["y"]
            hv[:, 0] += neck["cx"]
            hv[:, 2] += neck["cz"]
            cfg["_neck_top_y"] = neck["y"]
            cfg["_seat_y"] = seat_y
            cfg["_rim_r"] = rim["r"]
            acc = MeshAcc()
            acc.add(hv, ht, hc)
            acc.add(bv, bt, bc)
            # skin bridge: tapered loft from below the anny cut up into
            # the (now lower) GNM head interior
            skin_c = np.array(cfg["skin"]) * 0.97
            loft(acc, [(seat_y + 0.040, rim["r"] * 0.88, 0.95, skin_c, neck["cx"]),
                       (seat_y - 0.025, neck["r"] * 1.04, 0.95, skin_c, neck["cx"])])
            dress_accessories(acc, cfg, bv, neck)
            mv, mt, mc = acc.merged()
        else:
            head_w = hv[:, 0].max() - hv[:, 0].min()
            cfg["_neck_r"] = rim["r"]
            bv, bt, bc = build_body(cfg, rim["y"], head_w)
            hv = hv - np.array([rim["cx"], rim["y"] + 0.050, rim["cz"]])
            acc = MeshAcc()
            acc.add(hv, ht, hc)
            acc.add(bv, bt, bc)
            mv, mt, mc = acc.merged()
        pos, nrm, col = flat_shade(mv, mt, mc)
        out = os.path.join(args.out_dir, f"{key}_gnm.glb")
        write_glb(out, pos, nrm, col, f"{key}_portrait")
        print(f"  GLB → {out} ({os.path.getsize(out) / 1e6:.2f} MB, {pos.shape[0] // 3} tris)")
        if args.preview:
            pdir = args.preview_dir or tempfile.gettempdir()
            preview_png(os.path.join(pdir, f"_{key}_gnm_preview.png"), pos, nrm, col)


if __name__ == "__main__":
    main()
