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
    # DETAIL DRAFT 4 (2026-09-06): five tiers, each a touch off-axis,
    # the radii jittered per tree so a stand is not seven copies; a
    # leader spike above the top tier. Tiers touch, never overlap
    # (the recorder sees each as its own cone).
    dark = (foliage_col[0] * 0.86, foliage_col[1] * 0.88, foliage_col[2] * 0.86, 1.0)
    tiers = ((0.30, 1.00, 0.26), (0.48, 0.86, 0.24), (0.64, 0.70, 0.22), (0.78, 0.52, 0.20), (0.90, 0.32, 0.14))
    for ti, (base_f, r_f, h_f) in enumerate(tiers):
        jx = ((s >> (ti * 3)) % 5 - 2) * 0.035
        jy = ((s >> (ti * 3 + 7)) % 5 - 2) * 0.035
        rj = 1.0 + ((s >> (ti * 2 + 1)) % 3 - 1) * 0.07
        make_taper_cyl(f"{prefix}_C{ti}",
                       (px + jx, py + jy,
                        h * base_f + h * h_f * 0.5),
                       h * skirt * r_f * rj, 0.0, h * h_f,
                       foliage_col if ti % 2 == 0 else dark, segments=8 + (ti == 0) * 2)
    make_taper_cyl(f"{prefix}_Leader", (px, py, h * 1.04 + 0.02), 0.05, 0.0, h * 0.08,
                   dark, segments=5)


def make_broadleaf(prefix, px, py, h, foliage_col, trunk_col,
                   crown=0.34):
    """Alder / oak / park tree: tapered trunk + two or three blob
    lobes. The blob facets ARE the foliage at our art scale."""
    s = _seed_of(prefix)
    make_taper_cyl(f"{prefix}_Trunk", (px, py, h * 0.28),
                   h * 0.035 + 0.08, h * 0.02 + 0.04, h * 0.56,
                   trunk_col, segments=7)
    # DETAIL DRAFT 4 (2026-09-06): three to five lobes in two greens,
    # and two limbs (tubes) climbing from the trunk into the crown so
    # the tree has a structure under the foliage, not a ball on a pole.
    from .geometry import make_tube
    lobes = [(0.0, 0.0, 0.72, 1.00)]
    if s % 3:
        lobes.append((0.55, 0.15, 0.60, 0.62))
    if (s >> 4) % 3:
        lobes.append((-0.5, -0.2, 0.62, 0.58))
    lobes.append((0.15, -0.5, 0.86, 0.48))
    if (s >> 6) % 2:
        lobes.append((-0.2, 0.55, 0.82, 0.44))
    light = (min(1.0, foliage_col[0] * 1.14), min(1.0, foliage_col[1] * 1.12), min(1.0, foliage_col[2] * 1.10), 1.0)
    for li, (ox, oy, oz, r_f) in enumerate(lobes):
        r = h * crown * r_f
        make_blob(f"{prefix}_L{li}",
                  (px + ox * r, py + oy * r, h * oz),
                  r, foliage_col if li % 2 == 0 else light, noise=0.20,
                  seed=s + li * 17, squash=0.85)
    r0 = h * 0.02 + 0.04
    for bi, (ax, ay) in enumerate(((0.42, 0.12), (-0.36, -0.20))):
        base = (px, py, h * 0.50)
        mid = (px + ax * h * 0.10, py + ay * h * 0.10, h * 0.60)
        tip = (px + ax * h * 0.22, py + ay * h * 0.22, h * 0.68)
        make_tube(f"{prefix}_Limb{bi}", [base, mid, tip], r0 * 0.55, trunk_col, segments=5)


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
