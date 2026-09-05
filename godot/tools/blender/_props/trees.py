# _props/trees.py — real tree silhouettes (2026-08-04)
# ════════════════════════════════════════════════════════════════
# "Lighting won't fix the minecraft, blender will." The worst
# offenders were the trees: cabin_road's conifers were three stacked
# CUBES on a pole; cypress crowns were layer-cake discs. These build
# actual silhouettes from the de-Minecraft vocabulary: tapered
# trunks, stacked cones, noise-displaced blob canopies. Deterministic
# per (prefix-hash) seed — same tree, forever.
import math
from .geometry import (make_taper_cyl, make_blob, make_cyl, make_box)


def _seed_of(prefix):
    h = 0
    for ch in prefix:
        h = (h * 131 + ord(ch)) & 0x7FFFFFFF
    return h


def make_conifer(prefix, px, py, h, foliage_col, trunk_col,
                 skirt=0.30):
    """Spruce/Sitka: tapered trunk + three stacked CONES, each a
    touch off-axis so the tree isn't a lathe object. `skirt` is the
    bottom cone's radius as a fraction of height."""
    s = _seed_of(prefix)
    make_taper_cyl(f"{prefix}_Trunk", (px, py, h * 0.22),
                   0.10 * h * 0.14 + 0.10, 0.05, h * 0.44,
                   trunk_col, segments=7)
    tiers = ((0.34, 1.00, 0.42), (0.58, 0.72, 0.36), (0.80, 0.45, 0.34))
    for ti, (base_f, r_f, h_f) in enumerate(tiers):
        jx = ((s >> (ti * 3)) % 5 - 2) * 0.04
        jy = ((s >> (ti * 3 + 7)) % 5 - 2) * 0.04
        make_taper_cyl(f"{prefix}_C{ti}",
                       (px + jx, py + jy,
                        h * base_f + h * h_f * 0.5),
                       h * skirt * r_f, 0.0, h * h_f,
                       foliage_col, segments=8 + (ti == 0) * 2)


def make_broadleaf(prefix, px, py, h, foliage_col, trunk_col,
                   crown=0.34):
    """Alder / oak / park tree: tapered trunk + two or three blob
    lobes. The blob facets ARE the foliage at our art scale."""
    s = _seed_of(prefix)
    make_taper_cyl(f"{prefix}_Trunk", (px, py, h * 0.28),
                   h * 0.035 + 0.08, h * 0.02 + 0.04, h * 0.56,
                   trunk_col, segments=7)
    lobes = [(0.0, 0.0, 0.72, 1.00)]
    if s % 3:
        lobes.append((0.55, 0.15, 0.60, 0.62))
    if (s >> 4) % 3:
        lobes.append((-0.5, -0.2, 0.62, 0.58))
    for li, (ox, oy, oz, r_f) in enumerate(lobes):
        r = h * crown * r_f
        make_blob(f"{prefix}_L{li}",
                  (px + ox * r, py + oy * r, h * oz),
                  r, foliage_col, noise=0.20,
                  seed=s + li * 17, squash=0.85)


def make_cypress(prefix, px, py, h, foliage_col, trunk_col,
                 moss_col=None):
    """Bald cypress: buttressed base, tall taper trunk, one wide
    squashed blob crown, moss strands."""
    s = _seed_of(prefix)
    make_taper_cyl(f"{prefix}_Butt", (px, py, 0.5),
                   0.62, 0.30, 1.0, trunk_col, segments=9)
    make_taper_cyl(f"{prefix}_Trunk", (px, py, 1.0 + h * 0.5),
                   0.30, 0.14, h, trunk_col, segments=8)
    make_blob(f"{prefix}_Crown", (px, py, h + 1.3),
              h * 0.30 + 0.9, foliage_col, noise=0.24,
              seed=s, squash=0.55)
    if moss_col is not None:
        for mi in range(3):
            mx = px + (mi - 1) * 0.35
            make_box(f"{prefix}_Moss_{mi}",
                     (mx, py + ((s >> mi) % 3 - 1) * 0.2,
                      h + 0.4 - mi * 0.1),
                     (0.05, 0.05, 1.1 + (s >> (mi + 2)) % 3 * 0.2),
                     moss_col)


# ════════════════════════════════════════════════════════════════
# DETAIL DRAFT 1 (2026-09-05): trees that are not a cone on a stick.
# ════════════════════════════════════════════════════════════════

def make_bare_tree(prefix, px, py, h, bark=(0.34, 0.28, 0.22, 1.0), seed=0, limbs=5):
    """A leafless tree: a lathed trunk with a root flare, tube limbs
    that fork once — the winter tree, the dead snag by the fallen
    house, the alder by the crick."""
    import math
    from .geometry import make_lathe, make_tube
    def hsh(a, b):
        n = (a * 374761393 + b * 668265263 + seed * 1442695041) & 0xFFFFFFFF
        n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
        return ((n ^ (n >> 16)) & 0xFFFF) / 65536.0
    r0 = 0.05 * h ** 0.55
    make_lathe(f"{prefix}_Trunk", (px, py, 0.0),
               [(r0 * 1.6, 0.0), (r0 * 1.1, 0.25), (r0, h * 0.15), (r0 * 0.75, h * 0.5), (r0 * 0.45, h * 0.78), (r0 * 0.2, h), (0.0, h * 1.02)],
               bark, segments=8)
    for li in range(limbs):
        a = 2.0 * math.pi * (li / limbs + 0.13 * hsh(li, 1))
        z0 = h * (0.42 + 0.42 * hsh(li, 2))
        reach = h * (0.28 + 0.22 * hsh(li, 3))
        rise = h * (0.18 + 0.20 * hsh(li, 4))
        base = (px, py, z0)
        mid = (px + math.cos(a) * reach * 0.55, py + math.sin(a) * reach * 0.55, z0 + rise * 0.5)
        tip = (px + math.cos(a) * reach, py + math.sin(a) * reach, z0 + rise)
        make_tube(f"{prefix}_Limb_{li}", [base, mid, tip], r0 * 0.35, bark, segments=5)
        a2 = a + (0.6 if hsh(li, 5) > 0.5 else -0.6)
        tip2 = (mid[0] + math.cos(a2) * reach * 0.45, mid[1] + math.sin(a2) * reach * 0.45, mid[2] + rise * 0.55)
        make_tube(f"{prefix}_Twig_{li}", [mid, tip2], r0 * 0.18, bark, segments=4)


def make_shrub(prefix, px, py, h=0.9, r=0.55, col=(0.26, 0.40, 0.24, 1.0), segments=8):
    """A lathed shrub silhouette (waist, belly, crown) — reads as a
    clipped bush, not a ball."""
    from .geometry import make_lathe
    make_lathe(prefix, (px, py, 0.0),
               [(0.0, 0.0), (r * 0.55, h * 0.08), (r, h * 0.42), (r * 0.82, h * 0.78), (r * 0.35, h * 0.96), (0.0, h)],
               col, segments=segments)
