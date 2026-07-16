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
        "identity_sigma": 0.6,
        "head_scale": 1.0,
        "face_width": 0.90,                 # thin face
        "height": 1.78,
        "hair": "bangs",                    # long dark bangs over the brow
        "skin": (0.88, 0.72, 0.60),         # pale
        "hair_color": (0.14, 0.11, 0.10),   # dark
        "iris": (0.28, 0.32, 0.30),
        "shirt": (0.46, 0.24, 0.20),        # diner flannel red-brown
        "shirt_lt": (0.56, 0.32, 0.26),
        "pants": (0.22, 0.20, 0.24),
        "shoes": (0.12, 0.10, 0.09),
    },
    "frasier_temple": {
        "seed_key": "frasier_temple_v2",
        "identity_sigma": 0.65,
        "head_scale": 1.0,
        "face_width": 1.0,
        "height": 1.82,
        "hair": "afro",                     # slightly disheveled
        "skin": (0.42, 0.28, 0.20),         # dark brown
        "hair_color": (0.10, 0.08, 0.07),
        "iris": (0.22, 0.15, 0.10),
        "shirt": (0.16, 0.26, 0.22),        # dark green work jacket
        "shirt_lt": (0.22, 0.34, 0.28),
        "pants": (0.16, 0.16, 0.18),
        "shoes": (0.10, 0.09, 0.08),
    },
    "sam_miller": {
        "seed_key": "sam_miller_v2",
        "identity_sigma": 0.45,
        "head_scale": 0.94,                 # 17 — slighter build
        "height": 1.65,
        "face_width": 1.0,
        "hair": "bob",                      # jaw-length
        "brows": False,                     # soft look — no painted brow band
        "skin": (0.80, 0.62, 0.48),
        "hair_color": (0.28, 0.20, 0.14),   # dark brown
        "iris": (0.30, 0.20, 0.12),
        "shirt": (0.16, 0.42, 0.42),        # Kwik Stop teal polo
        "shirt_lt": (0.20, 0.52, 0.52),
        "pants": (0.24, 0.28, 0.38),        # jeans
        "shoes": (0.70, 0.70, 0.68),        # worn sneakers
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
    # subtle head scale about the neck base
    if cfg["head_scale"] != 1.0:
        base = verts[:, 1].min()
        verts[:, 1] = (verts[:, 1] - base) * cfg["head_scale"] + base
        verts[:, [0, 2]] *= cfg["head_scale"]
    return verts, tris, colors


def vertex_normals(verts, tris):
    fn = np.cross(verts[tris[:, 1]] - verts[tris[:, 0]],
                  verts[tris[:, 2]] - verts[tris[:, 0]])
    vn = np.zeros_like(verts)
    for k in range(3):
        np.add.at(vn, tris[:, k], fn)
    ln = np.linalg.norm(vn, axis=1, keepdims=True)
    ln[ln == 0] = 1.0
    return vn / ln


def decimate_cluster(verts, tris, colors, cell=0.006):
    """Vertex-cluster decimation — snaps vertices to a grid and merges.
    THIS is the stylization step: statistical-smooth → faceted lowpoly."""
    keys = np.floor(verts / cell).astype(np.int64)
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


def hex_prism(acc, y0, y1, r0, r1, color, cx=0.0, cz=0.0, squash=0.78):
    """Tapered hexagonal prism (the project's hull idiom). squash
    flattens front-back so torsos aren't tubes."""
    ang = np.deg2rad(np.arange(6) * 60.0 + 30.0)
    ring0 = np.stack([cx + np.cos(ang) * r0, np.full(6, y0), cz + np.sin(ang) * r0 * squash], 1)
    ring1 = np.stack([cx + np.cos(ang) * r1, np.full(6, y1), cz + np.sin(ang) * r1 * squash], 1)
    v = np.vstack([ring0, ring1])
    t = []
    for i in range(6):
        j = (i + 1) % 6
        # outward-facing winding (ring runs CCW seen from +Y, so the
        # side quads need j-first order to point their normals out)
        t += [[i, j + 6, j], [i, i + 6, j + 6]]
    for i in range(1, 5):          # caps: bottom faces -Y, top faces +Y
        t += [[0, i, i + 1]]
        t += [[6, 6 + i + 1, 6 + i]]
    acc.add(v, t, color)


def build_body(cfg, head_min_y, head_w):
    """Angular body scaled to cfg height. Returns (verts, tris, colors)
    with the collar top at y=0 (head gets translated to sit on it)."""
    H = cfg["height"]
    shirt, shirt_lt = np.array(cfg["shirt"]), np.array(cfg["shirt_lt"])
    pants, shoes = np.array(cfg["pants"]), np.array(cfg["shoes"])
    skin = np.array(cfg["skin"])
    acc = MeshAcc()
    # proportions (fraction of height)
    hip_y = -H * 0.48          # collar(0) → hips
    knee_y = -H * 0.70
    ankle_y = -H * 0.90
    shoulder_w = H * 0.125
    # torso: shoulders → waist → hips (two stacked hex prisms)
    hex_prism(acc, -H * 0.28, -0.010, shoulder_w * 0.72, shoulder_w, shirt)
    hex_prism(acc, hip_y, -H * 0.28, shoulder_w * 0.62, shoulder_w * 0.72, shirt)
    # collar ring (lighter) — hides the neck seam
    hex_prism(acc, -0.012, 0.012, head_w * 0.60, head_w * 0.52, shirt_lt)
    # arms: upper (shirt) + forearm (shirt) + hand (skin), slight A-pose
    for s in (-1, 1):
        sx = s * shoulder_w
        box(acc, (sx, -H * 0.10, 0), (H * 0.052, H * 0.20, H * 0.058), shirt_lt)
        box(acc, (sx + s * H * 0.012, -H * 0.285, 0), (H * 0.046, H * 0.17, H * 0.050), shirt)
        box(acc, (sx + s * H * 0.02, -H * 0.395, 0.004), (H * 0.040, H * 0.052, H * 0.044), skin)
    # legs + shoes
    for s in (-1, 1):
        lx = s * shoulder_w * 0.42
        box(acc, (lx, (hip_y + knee_y) / 2, 0), (H * 0.075, abs(knee_y - hip_y), H * 0.080), pants)
        box(acc, (lx, (knee_y + ankle_y) / 2, 0), (H * 0.065, abs(ankle_y - knee_y), H * 0.070), pants)
        box(acc, (lx, ankle_y - H * 0.028, H * 0.020), (H * 0.070, H * 0.055, H * 0.135), shoes)
    return acc.merged()


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
    col = colors[tris].reshape(-1, 3)
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
        if x1 <= x0 or yy1 <= yy0 or (x1 - x0) * (yy1 - yy0) > 12000:
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
        hv, ht, hc = build_head(gnm, cfg)
        hv, ht, hc = decimate_cluster(hv, ht, hc, cell=0.006)
        print(f"  head after decimation: {len(hv)} verts / {len(ht)} tris")
        head_w = hv[:, 0].max() - hv[:, 0].min()
        bv, bt, bc = build_body(cfg, hv[:, 1].min(), head_w)
        # seat the head: neck base sits just below the collar top (y=0)
        hv = hv - np.array([0.0, hv[:, 1].min() + 0.035, 0.0])
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
