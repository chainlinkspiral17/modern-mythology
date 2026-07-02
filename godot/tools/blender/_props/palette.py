# _props/palette.py
# ════════════════════════════════════════════════════════════════
# Shared color constants. Two layers:
#
#   1. NEUTRALS — palette pieces every locale uses: walls, floor,
#      ceiling, paper, metal, glass. Each locale can override but
#      the defaults match the "warm sunset 1990s vernacular" the
#      kwik stop dialled in.
#
#   2. CANON BRANDS — colors tied to fictional in-game brands.
#      KWIK STOP red, HCE banner navy, NexCorp orange, etc. Don't
#      retune these per locale — keep canon visual consistency
#      across the franchise.
#
# When you need a one-off color for a specific prop, define it
# locally in that prop's builder function. Promote to this file
# only when ≥2 locales reach for the same shade.
# ════════════════════════════════════════════════════════════════

# ── NEUTRALS ──────────────────────────────────────────────────────
FLOOR_VINYL     = (0.84, 0.78, 0.66, 1.0)
FLOOR_SEAM      = (0.62, 0.55, 0.44, 1.0)
FLOOR_SCUFF     = (0.46, 0.40, 0.32, 1.0)
WALL_CREAM      = (0.92, 0.86, 0.74, 1.0)
WALL_BASEBOARD  = (0.62, 0.52, 0.40, 1.0)
CEILING_TILE    = (0.94, 0.92, 0.84, 1.0)
CEILING_GRID    = (0.58, 0.54, 0.46, 1.0)
CEILING_STAIN   = (0.72, 0.62, 0.42, 1.0)
GLASS           = (0.78, 0.84, 0.86, 0.45)
GLASS_WARM      = (0.96, 0.84, 0.62, 0.70)
METAL_STEEL     = (0.66, 0.68, 0.70, 1.0)
METAL_BLACK     = (0.18, 0.16, 0.14, 1.0)
PAPER           = (0.96, 0.92, 0.82, 1.0)
PAPER_AGED      = (0.86, 0.78, 0.62, 1.0)
NEWSPRINT       = (0.78, 0.74, 0.66, 1.0)
TWINE           = (0.62, 0.46, 0.30, 1.0)
RUBBER_MAT      = (0.22, 0.20, 0.20, 1.0)
COUNTER_FORMICA = (0.74, 0.64, 0.42, 1.0)
COUNTER_DARK    = (0.30, 0.22, 0.14, 1.0)
COUNTER_TOP     = (0.18, 0.14, 0.12, 1.0)
COOLER_GLASS    = (0.42, 0.66, 0.84, 0.55)
COOLER_INTERIOR = (0.08, 0.16, 0.26, 1.0)
CROWN_MOLD      = (0.74, 0.62, 0.42, 1.0)
PVC_WHITE       = (0.86, 0.84, 0.78, 1.0)

# ── CANON BRANDS ──────────────────────────────────────────────────
BRAND_RED_KWIK  = (0.78, 0.18, 0.16, 1.0)   # KWIK STOP signage
BRAND_NAVY_HCE  = (0.18, 0.32, 0.50, 1.0)   # Harmony Creek Estates
BRAND_NAVY_TXT  = (0.86, 0.84, 0.74, 1.0)   # cream text on HCE
BRAND_AMBER_NEX = (0.84, 0.64, 0.28, 1.0)   # NexCorp gas-station

# Lottery / convenience accents — used across multiple stores.
LOTTERY_YEL     = (0.98, 0.84, 0.32, 1.0)
LOTTERY_RED     = (0.86, 0.42, 0.32, 1.0)   # muted from raw

# ── PRODUCT TINTS (warm-sunset palette, not rainbow-bright) ──────
# Snack bags / soda cans / six-packs cycle this. Saturations are
# pulled to ~40-65% so the aisles read coloured-but-cohesive
# instead of candy-aisle clown.
SNACK_TINTS = [
    (0.92, 0.62, 0.28, 1.0),   # warm amber (dominant)
    (0.78, 0.42, 0.22, 1.0),   # rust orange
    (0.68, 0.32, 0.20, 1.0),   # terracotta
    (0.94, 0.82, 0.52, 1.0),   # cream wheat
    (0.86, 0.66, 0.34, 1.0),   # gold honey
    (0.52, 0.40, 0.26, 1.0),   # warm brown jerky
    (0.42, 0.52, 0.56, 1.0),   # muted teal accent
    (0.56, 0.58, 0.42, 1.0),   # sage olive accent
    (0.34, 0.42, 0.54, 1.0),   # dusty blue accent
]
