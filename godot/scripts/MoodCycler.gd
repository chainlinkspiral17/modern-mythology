# MoodCycler.gd
# ════════════════════════════════════════════════════════════════
# Cycles the post-process moods. F3 advances to the next preset.
# Drives the screen post-process stack (in render order):
#   NeonQuad   · neon_edge — Sobel silhouette outliner.
#   AsciiQuad  · ascii_render — per-cell ASCII renderer.
#   Quad       · demoscene_post — palette quantize, dither, scanlines,
#                chromatic aberration.
#
# Every mood is pushed to have STRONG identity — no two should feel
# like minor variations of the same look. Naturalistic moods (lunch,
# dusk, night) lean on palette quantize. Stylized moods (chillwave,
# sunset, lithograph, noir, ice) lean on the neon-edge shader.
# Substrate states (3:47, precipice, substrate) lean on ASCII render.
# ════════════════════════════════════════════════════════════════

extends CanvasLayer

const MOODS: Array = [
    # ── naturalistic time-of-day ─────────────────────────────────
    {
        "name": "lunch",
        "palette": 22.0, "dither": 0.04, "scanline": 0.10, "aberration": 0.0006,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
        "ascii_fg": Color(0.92, 0.82, 0.55, 1), "ascii_bg": Color(0.04, 0.03, 0.02, 1),
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 0.22, 0.78, 1),
        "neon_low": Color(0.42, 0.12, 0.50, 1), "neon_high": Color(0.10, 0.05, 0.25, 1),
        "neon_grad": 1.0, "neon_blend": 0.0, "neon_glow": 0.4,
    },
    {
        "name": "dusk",
        "palette": 14.0, "dither": 0.18, "scanline": 0.40, "aberration": 0.0016,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
        "ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 0.22, 0.78, 1),
        "neon_low": Color(0.42, 0.12, 0.50, 1), "neon_high": Color(0.10, 0.05, 0.25, 1),
        "neon_grad": 1.0, "neon_blend": 0.0, "neon_glow": 0.4,
    },
    # ── synthwave / chillwave ────────────────────────────────────
    {
        "name": "chillwave",
        "palette": 6.0, "dither": 0.18, "scanline": 0.50, "aberration": 0.0030,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
        "ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
        "neon": 1.0, "neon_thresh": 0.05,
        "neon_edge": Color(1.0, 0.20, 0.85, 1),    # hot magenta
        "neon_low":  Color(0.58, 0.10, 0.65, 1),   # vivid magenta floor
        "neon_high": Color(0.08, 0.02, 0.25, 1),   # deep purple top
        "neon_grad": 1.0, "neon_blend": 0.20, "neon_glow": 0.7,
    },
    {
        "name": "sunset",
        "palette": 8.0, "dither": 0.15, "scanline": 0.35, "aberration": 0.0024,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
        "ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
        "neon": 1.0, "neon_thresh": 0.06,
        "neon_edge": Color(1.0, 0.78, 0.20, 1),    # gold edges
        "neon_low":  Color(0.95, 0.32, 0.18, 1),   # blazing orange
        "neon_high": Color(0.18, 0.06, 0.32, 1),   # twilight purple
        "neon_grad": 1.0, "neon_blend": 0.30, "neon_glow": 0.6,
    },
    # ── concept-art match: pure black + warm red + scene warmth ──
    {
        "name": "lithograph",
        "palette": 3.0, "dither": 0.18, "scanline": 0.60, "aberration": 0.0010,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
        "ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
        "neon": 1.0, "neon_thresh": 0.03,
        "neon_edge": Color(0.95, 0.16, 0.14, 1),
        "neon_low":  Color(0.0,  0.0,  0.0,  1),
        "neon_high": Color(0.0,  0.0,  0.0,  1),
        "neon_grad": 0.0,
        "neon_blend": 0.25,                        # only the brightest spots tint
        "neon_glow": 0.55,                         # tighter bloom — sharper lines
    },
    {
        "name": "noir",
        "palette": 3.0, "dither": 0.28, "scanline": 0.70, "aberration": 0.0008,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
        "ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
        "neon": 1.0, "neon_thresh": 0.07,
        "neon_edge": Color(1.0, 0.98, 0.92, 1),    # bone white
        "neon_low":  Color(0.0, 0.0, 0.0, 1),
        "neon_high": Color(0.0, 0.0, 0.0, 1),
        "neon_grad": 0.0, "neon_blend": 0.10, "neon_glow": 0.5,
    },
    {
        # Architectural / drafting look. The v2 directional ASCII
        # shader samples per cell + 4 neighbors, picks ─ │ ┼ ┌ ┐ └ ┘
        # ╱ ╲ from the local brightness gradient direction. Strokes
        # span full cells so adjacent edge cells form continuous
        # lines. Geometry rendered as architectural line drawing.
        "name": "blueprint",
        "palette": 6.0, "dither": 0.06, "scanline": 0.20, "aberration": 0.0004,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
        "ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 0.22, 0.78, 1),
        "neon_low": Color(0.42, 0.12, 0.50, 1), "neon_high": Color(0.10, 0.05, 0.25, 1),
        "neon_grad": 1.0, "neon_blend": 0.0, "neon_glow": 0.4,
        "dir_ascii": 1.0, "dir_cell": 10.0, "dir_thresh": 0.06,
        "dir_line": Color(0.78, 0.92, 1.0, 1),
        "dir_fill": Color(0.06, 0.10, 0.18, 1),
        "dir_tint": false,
        "dir_input_scale": 0.7,
    },
    {
        # Same v2 directional ASCII but in saturated booth-red on
        # pure black — matching the lithograph palette. The ASCII
        # character set draws the geometry edges as line work.
        "name": "blueprint_red",
        # Lithograph clean-up — same logic as linework. Aberration off
        # so red/blue fringe doesn't paint yellow-green halos on edges.
        # Palette widened to 16 so bleed-through reds aren't banded.
        "palette": 16.0, "dither": 0.01, "scanline": 0.06, "aberration": 0.0,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
        "ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
        # NEW: layer the linework neon_edge UNDERNEATH the ASCII so
        # crisp architectural lines survive even where the ASCII
        # density floods the surface. scene_blend > 0 lets the
        # brightest pixels (red sign letters, white bulb meshes) bleed
        # through the black fill as their actual scene colour — same
        # trick as the linework mood, applied as the foundation here.
        "neon": 1.0, "neon_thresh": 0.006,
        "neon_edge": Color(0.96, 0.94, 0.88, 1),
        "neon_low":  Color(0.0, 0.0, 0.0, 1),
        "neon_high": Color(0.0, 0.0, 0.0, 1),
        "neon_grad": 0.0, "neon_blend": 0.65, "neon_glow": 0.06,
        "neon_bleed_lo": 0.82, "neon_bleed_hi": 0.96,
        # red_only: bleed gate becomes R - max(G,B). Sodium-lit cars
        # (red_dom 0.34) rejected; sign letters (0.78) pass; red-glow
        # lit windows (0.50 if practical is red) pass with subtle weight.
        "neon_sat_bleed": false,
        "neon_red_only": true,
        "neon_sat_lo": 0.40, "neon_sat_hi": 0.65,
        # Animated ASCII starscape layer over the dark sky pixels —
        # slow spiral galaxy + twinkling stars + fungal-microchip drift.
        # Starscape DIALED UP so it's actually visible on the dark
        # sky pixels — galaxy spiral, twinkling stars, fungal chip
        # all near their max. sky_thresh widened (0.10 → 0.18) so
        # more "almost-dark" pixels qualify as sky and accept paint.
        "star": 1.0, "star_cell": 9.0, "star_time": 0.40,
        "star_sky_thresh": 0.18,
        "star_galaxy": 0.95, "star_stars": 1.0, "star_chip": 0.70,
        # Large diffuse fBM clouds — sparse-dot penetration at edges,
        # cross-hatch & solid glyphs in the dense cores. Drifts slowly
        # horizontally; floor controls how much of sky is "clear".
        "star_cloud": 0.85, "star_cloud_scale": 0.011, "star_cloud_floor": 0.50,
        # ASCII halftone tuned for reference-restraint: input_scale
        # 0.6 → 0.40 drops dim cells below the empty cutoff so most
        # surface stays pure black. Density chars now only appear on
        # genuinely lit highlights (lit windows, sign halo). Cells
        # shrunk to 7 for finer-grain halftone that reads as ink
        # stipple rather than blocky char fill.
        "dir_ascii": 0.45, "dir_cell": 7.0, "dir_thresh": 0.06,
        "dir_line": Color(0.95, 0.92, 0.86, 1),
        "dir_fill": Color(0.0, 0.0, 0.0, 1),
        "dir_tint": false,
        "dir_input_scale": 0.40,
        "dir_mono_red": true,
        "dir_mono_white_col": Color(0.96, 0.94, 0.88, 1),
        "dir_mono_red_col":   Color(0.98, 0.16, 0.18, 1),
        "dir_red_thresh": 0.32,
    },
    {
        # Pure linework — answer to "render the scene so only visible
        # edges of geometry are pronounced and visible." Uses
        # neon_edge's Sobel silhouette outliner at strength 1 with a
        # very low edge_threshold so even subtle geometry creases get
        # caught. Fill is pure black so non-edge pixels render as
        # solid nothing. No ASCII layer; no density fill; no halftone.
        # The picture reads as an ink drawing of whatever the camera
        # actually sees.
        "name": "linework",
        # INK PRESS · RED PASS — pure BLACK + BLEACH WHITE + RED.
        # The reference rule made explicit: no colour anywhere except
        # the one chosen accent. neon_edge is pure (1,1,1) bleach
        # white (no warm cast). accent_channel = (1,0,0) makes the
        # bleed gate fire only on red-dominant pixels. Sibling moods
        # ink_blue / ink_green swap accent_channel for the same look
        # at a different accent — the "different colours for different
        # passes" the user described.
        "palette": 16.0, "dither": 0.01, "scanline": 0.06, "aberration": 0.0,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
        "ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
        "neon": 1.0, "neon_thresh": 0.006,
        "neon_edge": Color(1.0, 1.0, 1.0, 1),          # PURE BLEACH WHITE
        "neon_low":  Color(0.0, 0.0, 0.0, 1),
        "neon_high": Color(0.0, 0.0, 0.0, 1),
        "neon_grad": 0.0, "neon_blend": 0.65, "neon_glow": 0.06,
        "neon_bleed_lo": 0.82, "neon_bleed_hi": 0.96,
        "neon_sat_bleed": false,
        "neon_red_only": true,
        "neon_accent": Vector3(1.0, 0.0, 0.0),         # RED PASS
        "neon_sat_lo": 0.40, "neon_sat_hi": 0.65,
        # Animated ASCII starscape layer over the dark sky pixels —
        # slow spiral galaxy + twinkling stars + fungal-microchip drift.
        # Starscape DIALED UP so it's actually visible on the dark
        # sky pixels — galaxy spiral, twinkling stars, fungal chip
        # all near their max. sky_thresh widened (0.10 → 0.18) so
        # more "almost-dark" pixels qualify as sky and accept paint.
        "star": 1.0, "star_cell": 9.0, "star_time": 0.40,
        "star_sky_thresh": 0.18,
        "star_galaxy": 0.95, "star_stars": 1.0, "star_chip": 0.70,
        # Large diffuse fBM clouds — sparse-dot penetration at edges,
        # cross-hatch & solid glyphs in the dense cores. Drifts slowly
        # horizontally; floor controls how much of sky is "clear".
        "star_cloud": 0.85, "star_cloud_scale": 0.011, "star_cloud_floor": 0.50,
    },
    {
        # SKYBOX FILTER — pure preview of the starscape animation
        # without any scene content. All other shader layers off,
        # palette/dither/scanline minimal, demoscene aberration zero.
        # force_full bypasses the sky_mask so the animation paints
        # the whole frame. Use it to inspect the galaxy spiral,
        # twinkling stars, fungal-microchip drift, and diffuse
        # clouds in isolation.
        "name": "skybox",
        "palette": 32.0, "dither": 0.0, "scanline": 0.0, "aberration": 0.0,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": false,
        "ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.0, 0.0, 0.0, 1),
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 0.22, 0.78, 1),
        "neon_low": Color.BLACK, "neon_high": Color.BLACK,
        "neon_grad": 0.0, "neon_blend": 0.0, "neon_glow": 0.0,
        "star": 1.0, "star_cell": 9.0, "star_time": 0.55,
        "star_sky_thresh": 1.0,
        "star_galaxy": 1.0, "star_stars": 1.0, "star_chip": 0.85,
        "star_cloud": 1.0, "star_cloud_scale": 0.011, "star_cloud_floor": 0.50,
        "star_force_full": true,
    },
    # ────────────────────────────────────────────────────────────────
    # CINEMATIC FILTER MOODS — exaggerated stylization presets, each
    # leaning hard into a single visual idiom. Use for hero shots
    # and stylistic variety; not the everyday gameplay mood.
    # ────────────────────────────────────────────────────────────────
    {
        # INK PRESS · BLUE PASS — same architecture as linework but
        # accent_channel = (0, 0, 1) so the dominance test fires on
        # blue-saturated emission instead of red. Future scenes with
        # cool tube lights / blue neon / blueprint blue stamp the
        # accent here without other warm-lit surfaces leaking.
        "name": "ink_blue",
        "palette": 16.0, "dither": 0.01, "scanline": 0.06, "aberration": 0.0,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
        "ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
        "neon": 1.0, "neon_thresh": 0.006,
        "neon_edge": Color(1.0, 1.0, 1.0, 1),
        "neon_low":  Color(0.0, 0.0, 0.0, 1),
        "neon_high": Color(0.0, 0.0, 0.0, 1),
        "neon_grad": 0.0, "neon_blend": 0.65, "neon_glow": 0.06,
        "neon_bleed_lo": 0.82, "neon_bleed_hi": 0.96,
        "neon_sat_bleed": false,
        "neon_red_only": true,
        "neon_accent": Vector3(0.0, 0.0, 1.0),          # BLUE PASS
        "neon_sat_lo": 0.40, "neon_sat_hi": 0.65,
    },
    {
        # INK PRESS · GREEN PASS — same architecture, accent_channel
        # (0, 1, 0). Lit foliage, phosphor screens, neon green signage
        # take the accent.
        "name": "ink_green",
        "palette": 16.0, "dither": 0.01, "scanline": 0.06, "aberration": 0.0,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
        "ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
        "neon": 1.0, "neon_thresh": 0.006,
        "neon_edge": Color(1.0, 1.0, 1.0, 1),
        "neon_low":  Color(0.0, 0.0, 0.0, 1),
        "neon_high": Color(0.0, 0.0, 0.0, 1),
        "neon_grad": 0.0, "neon_blend": 0.65, "neon_glow": 0.06,
        "neon_bleed_lo": 0.82, "neon_bleed_hi": 0.96,
        "neon_sat_bleed": false,
        "neon_red_only": true,
        "neon_accent": Vector3(0.0, 1.0, 0.0),          # GREEN PASS
        "neon_sat_lo": 0.40, "neon_sat_hi": 0.65,
    },
    {
        # HIGH-CONTRAST B&W INK — Sin City / chiaroscuro. Pure white
        # ink lines over pure black fill. No bleed, no gradient, no
        # ASCII. Heavy scanline gives film-grain feel; chromatic
        # aberration zero so the lines stay crisp.
        "name": "high_contrast_bw",
        "palette": 24.0, "dither": 0.04, "scanline": 0.55, "aberration": 0.0,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": false,
        "ascii_fg": Color(1, 1, 1, 1), "ascii_bg": Color(0, 0, 0, 1),
        "neon": 1.0, "neon_thresh": 0.012,
        "neon_edge": Color(1.0, 1.0, 1.0, 1),
        "neon_low":  Color.BLACK, "neon_high": Color.BLACK,
        "neon_grad": 0.0, "neon_blend": 0.0, "neon_glow": 0.20,
        "neon_bleed_lo": 0.99, "neon_bleed_hi": 1.0,
    },
    {
        # CEL-SHADED — Saturday-morning cartoon. Aggressive palette
        # quantize gives flat colour bands; neon_edge at strength 1.0
        # with a low threshold adds the bold black ink outline cels.
        # NO bleed gates (the scene colour is the point). Minimal
        # dither so the colour bands stay flat. Scanline + aberration
        # off — we're going for animation cels, not CRT.
        "name": "cel_shaded",
        "palette": 4.0, "dither": 0.0, "scanline": 0.0, "aberration": 0.0,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
        "ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
        "neon": 1.0, "neon_thresh": 0.025,
        "neon_edge": Color(0.04, 0.02, 0.02, 1),     # near-black ink outline
        "neon_low":  Color(0.0, 0.0, 0.0, 1),        # gradient unused
        "neon_high": Color(0.0, 0.0, 0.0, 1),
        # scene_blend = 1.0 with very-wide bleed range = the fill is
        # essentially the scene colour itself (after palette quantize).
        # The neon_edge gives the cel outline ON TOP of the flat fill.
        "neon_grad": 0.0, "neon_blend": 1.0, "neon_glow": 0.10,
        "neon_bleed_lo": 0.05, "neon_bleed_hi": 0.20,
    },
    {
        # DEMOSCENE ASCII — Amiga / Diskmag intro. Full ASCII coverage
        # like substrate, but cyan/magenta vapor palette + heavy
        # scanlines + chromatic aberration. Starscape on TOP at low
        # strength gives the parallax-scroll feel demoscenes love.
        "name": "demoscene_ascii",
        "palette": 5.0, "dither": 0.50, "scanline": 0.80, "aberration": 0.0048,
        "ascii": 1.0, "ascii_cell": 7.0, "ascii_gamma": 0.65, "ascii_tint": false,
        "ascii_fg": Color(0.42, 0.92, 1.0, 1),       # demoscene cyan
        "ascii_bg": Color(0.04, 0.0, 0.08, 1),       # deep purple-black
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 0.22, 0.78, 1),
        "neon_low": Color.BLACK, "neon_high": Color.BLACK,
        "neon_grad": 0.0, "neon_blend": 0.0, "neon_glow": 0.0,
        "star": 0.6, "star_cell": 8.0, "star_time": 0.85,
        "star_sky_thresh": 0.22,
        "star_galaxy": 0.7, "star_stars": 0.9, "star_chip": 1.0,
        "star_cloud": 0.4,
    },
    {
        "name": "ice",
        "palette": 7.0, "dither": 0.22, "scanline": 0.40, "aberration": 0.0020,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
        "ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
        "neon": 1.0, "neon_thresh": 0.06,
        "neon_edge": Color(0.62, 0.95, 1.0, 1),    # pale cyan
        "neon_low":  Color(0.06, 0.12, 0.28, 1),
        "neon_high": Color(0.0,  0.02, 0.06, 1),
        "neon_grad": 1.0, "neon_blend": 0.25, "neon_glow": 0.6,
    },
    # ── deep moods: code substrate states ────────────────────────
    {
        "name": "night",
        "palette": 9.0, "dither": 0.26, "scanline": 0.50, "aberration": 0.0022,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
        "ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 0.22, 0.78, 1),
        "neon_low": Color(0.42, 0.12, 0.50, 1), "neon_high": Color(0.10, 0.05, 0.25, 1),
        "neon_grad": 1.0, "neon_blend": 0.0, "neon_glow": 0.4,
    },
    {
        "name": "3_47_am",
        "palette": 7.0, "dither": 0.36, "scanline": 0.62, "aberration": 0.0030,
        "ascii": 0.55, "ascii_cell": 9.0, "ascii_gamma": 0.85, "ascii_tint": true,
        "ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 0.22, 0.78, 1),
        "neon_low": Color(0.42, 0.12, 0.50, 1), "neon_high": Color(0.10, 0.05, 0.25, 1),
        "neon_grad": 1.0, "neon_blend": 0.0, "neon_glow": 0.4,
    },
    {
        "name": "precipice",
        "palette": 5.0, "dither": 0.50, "scanline": 0.78, "aberration": 0.0042,
        "ascii": 0.90, "ascii_cell": 7.0, "ascii_gamma": 0.75, "ascii_tint": true,
        "ascii_fg": Color(0.95, 0.32, 0.32, 1),    # red shift
        "ascii_bg": Color(0.02, 0.0, 0.0, 1),
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 0.22, 0.78, 1),
        "neon_low": Color(0.42, 0.12, 0.50, 1), "neon_high": Color(0.10, 0.05, 0.25, 1),
        "neon_grad": 1.0, "neon_blend": 0.0, "neon_glow": 0.4,
    },
    {
        # FULL substrate — every cell on the screen rendered as code.
        # Much more dramatic than before: small cells (dense glyphs),
        # steeper gamma curve so high-density characters dominate,
        # extreme dither + heavy chromatic aberration + tight palette.
        # NOT tinted from the scene — the substrate uses its own
        # bright phosphor green-on-black so the "looking at code"
        # quality reads clearly.
        "name": "substrate",
        "palette": 3.0, "dither": 0.70, "scanline": 0.92, "aberration": 0.0055,
        "ascii": 1.00, "ascii_cell": 6.0, "ascii_gamma": 0.60, "ascii_tint": false,
        "ascii_fg": Color(0.42, 1.0, 0.62, 1),     # phosphor green
        "ascii_bg": Color(0.0, 0.02, 0.0, 1),      # deep black-green
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 0.22, 0.78, 1),
        "neon_low": Color(0.42, 0.12, 0.50, 1), "neon_high": Color(0.10, 0.05, 0.25, 1),
        "neon_grad": 1.0, "neon_blend": 0.0, "neon_glow": 0.4,
    },
    {
        "name": "raw",
        "palette": 32.0, "dither": 0.0, "scanline": 0.0, "aberration": 0.0,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 1.0, "ascii_tint": true,
        "ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 0.22, 0.78, 1),
        "neon_low": Color(0.42, 0.12, 0.50, 1), "neon_high": Color(0.10, 0.05, 0.25, 1),
        "neon_grad": 1.0, "neon_blend": 0.0, "neon_glow": 0.4,
    },
]

var current_index: int = 8   # start on linework — pure visible-edges-only render
# Optional in-game label that displays the current mood name. If the
# scene's HUD doesn't provide one we just skip updating it.
@export var mood_label_path: NodePath = NodePath("../HUD/MoodLabel")

# ── PER-AREA MOOD STRATA ──────────────────────────────────────────
# Each scene defines its OWN curated subset of moods that fit the
# area's vibe ("strata"). Hold the right mouse button + look
# horizontally → smooth-cycle through the strata. F3 still steps
# through ONLY the strata, not the global mood list. Empty strata
# falls back to every mood.
@export var mood_strata: Array[String] = []
var _strata_indices: Array[int] = []

# Right-mouse vibe wheel state
var _right_mouse_held: bool = false
var _yaw_accum: float = 0.0
const STRATA_YAW_PER_STEP: float = 0.18    # radians of horizontal mouse motion per mood swap

# ── ELASTIC TRANSITION · WARBLE · MUSIC INPUT ─────────────────────
# Strata swaps don't snap — they fade through a ~0.35 s elastic
# transition with a sin-warble on aberration / scanline / dither
# that decays to zero. Gives the wheel a "this reality is bending"
# feel rather than a hard cut. The warble also folds in a pulse
# from the master audio bus peak, so playing music makes the visuals
# react — louder = more warble, louder reality bends harder.
const WARBLE_DURATION: float = 0.35       # seconds
var _warble_t: float = 999.0              # seconds since last strata swap
var _audio_level: float = 0.0             # 0..1, smoothed master bus peak
const AUDIO_DECAY: float = 0.92           # exponential smoothing on the level

# ── F5 STROBE FLICKER ─────────────────────────────────────────────
# Press F5 to rapid-cycle through a curated sequence of dramatic
# moods over ~1.5 s, then return to the mood that was active when
# the strobe started. "A solid in-between flicker in the substrate"
# — glimpses of alternate realities glitching through the current
# one. Names are resolved to MOODS indices at startup so a future
# reorder of MOODS doesn't break the strobe.
const STROBE_NAMES: Array = [
    "substrate", "linework", "demoscene_ascii", "high_contrast_bw",
    "ink_blue", "blueprint_red", "cel_shaded", "ink_green",
    "noir", "precipice", "linework", "substrate",
]
const STROBE_FRAMES_PER_STEP: int = 5     # one mood swap every ~5 frames @ 60fps
var strobe_active: bool = false
var strobe_step: int = 0
var strobe_frame: int = 0
var strobe_return_index: int = 0
var _strobe_indices: Array[int] = []


func _ready() -> void:
    _apply(MOODS[current_index])
    print("[Mood] %s · F3 cycle · F5 strobe · RMB+look strata wheel" % MOODS[current_index]["name"])
    var by_name: Dictionary = {}
    for i in range(MOODS.size()):
        by_name[MOODS[i]["name"]] = i
    for name in STROBE_NAMES:
        if by_name.has(name):
            _strobe_indices.append(by_name[name])
    # Resolve the scene-configured mood_strata to indices. Empty
    # strata falls back to the full mood list so F3 / RMB still work.
    for name in mood_strata:
        if by_name.has(name):
            _strata_indices.append(by_name[name])
    if _strata_indices.is_empty():
        for i in range(MOODS.size()):
            _strata_indices.append(i)
    if current_index in _strata_indices:
        pass
    else:
        # If the configured start mood isn't in the strata, jump to
        # the first strata mood so RMB cycling makes sense.
        current_index = _strata_indices[0]
        _apply(MOODS[current_index])


func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_F3:
            # F3 now steps WITHIN the strata so each area's cycle stays curated.
            _strata_step(1)
        elif event.keycode == KEY_F5:
            strobe_active = true
            strobe_step = 0
            strobe_frame = 0
            strobe_return_index = current_index
            print("[Mood] STROBE · return to %s in %d steps" %
                  [MOODS[strobe_return_index]["name"], _strobe_indices.size()])
    elif event is InputEventMouseButton:
        if event.button_index == MOUSE_BUTTON_RIGHT:
            _right_mouse_held = event.pressed
            _yaw_accum = 0.0
    elif event is InputEventMouseMotion and _right_mouse_held:
        # Use the captured horizontal motion as a yaw accumulator.
        # Sensitivity 0.0015 matches FPC's mouse sensitivity scale.
        _yaw_accum += event.relative.x * 0.0015
        while abs(_yaw_accum) >= STRATA_YAW_PER_STEP:
            var step: int = 1 if _yaw_accum > 0.0 else -1
            _yaw_accum -= float(step) * STRATA_YAW_PER_STEP
            _strata_step(step)


func _strata_step(direction: int) -> void:
    """Cycle within the resolved strata. Triggers the warble transition."""
    var n: int = _strata_indices.size()
    if n == 0:
        return
    var pos: int = _strata_indices.find(current_index)
    if pos < 0:
        pos = 0
    var next_pos: int = ((pos + direction) % n + n) % n
    current_index = _strata_indices[next_pos]
    _apply(MOODS[current_index])
    _warble_t = 0.0
    print("[Mood] strata → %s" % MOODS[current_index]["name"])


func _process(delta: float) -> void:
    # ── audio-reactive sampling: exponential-smoothed master bus peak
    # (linear 0..1). Quiet game → ~0; loud music → ~0.8-1.0. Fed to
    # shaders as a uniform so any layer can react.
    var bus_peak_db: float = AudioServer.get_bus_peak_volume_left_db(0, 0)
    var bus_peak_lin: float = db_to_linear(bus_peak_db)
    _audio_level = _audio_level * AUDIO_DECAY + bus_peak_lin * (1.0 - AUDIO_DECAY)

    # ── elastic warble after a strata swap: decays to 0 over WARBLE_DURATION
    if _warble_t < WARBLE_DURATION:
        _warble_t += delta
        var w: float = 1.0 - clamp(_warble_t / WARBLE_DURATION, 0.0, 1.0)
        # Sin oscillation gives the "bending" reality feel
        var osc: float = sin(_warble_t * 60.0)
        # Music-pulse adds on top so loud audio extends the warble
        var pulse: float = _audio_level * 0.6
        _apply_warble(w, osc, pulse)
    elif _audio_level > 0.02:
        # Quiet baseline warble driven by music only
        _apply_warble(0.0, 0.0, _audio_level * 0.4)

    # ── strobe handling (unchanged)
    if not strobe_active:
        return
    strobe_frame += 1
    if strobe_frame < STROBE_FRAMES_PER_STEP:
        return
    strobe_frame = 0
    if strobe_step >= _strobe_indices.size():
        strobe_active = false
        current_index = strobe_return_index
        _apply(MOODS[current_index])
        print("[Mood] strobe end → %s" % MOODS[current_index]["name"])
        return
    var idx: int = _strobe_indices[strobe_step]
    _apply(MOODS[idx])
    strobe_step += 1


func db_to_linear(db: float) -> float:
    if db <= -60.0:
        return 0.0
    return pow(10.0, db / 20.0)


func _apply_warble(strata_warble: float, osc: float, pulse: float) -> void:
    """Overlay a transient sin-warble onto the demoscene_post params
    AND amplify chromatic aberration + dither during the transition.
    This is destructive of the base preset's values for the duration —
    the elastic feel comes from the picture briefly mis-aligning
    before snapping back."""
    var aberration_boost: float = strata_warble * 0.0020 + pulse * 0.0010
    var dither_boost: float = strata_warble * 0.20 + pulse * 0.10
    var scanline_boost: float = strata_warble * 0.15 * (0.5 + 0.5 * osc) + pulse * 0.05
    var base: Dictionary = MOODS[current_index]
    _set_params("Quad", {
        "chromatic_aberration": base["aberration"] + aberration_boost,
        "dither_strength":      clamp(base["dither"] + dither_boost, 0.0, 1.0),
        "scanline_strength":    clamp(base["scanline"] + scanline_boost, 0.0, 1.0),
        "palette_size":         base["palette"],
    })


func _apply(preset: Dictionary) -> void:
    _set_params("NeonQuad", {
        "strength":       preset["neon"],
        "edge_threshold": preset["neon_thresh"],
        "edge_color":     preset["neon_edge"],
        "fill_low":       preset["neon_low"],
        "fill_high":      preset["neon_high"],
        "fill_gradient":  preset["neon_grad"],
        "scene_blend":    preset.get("neon_blend", 0.0),
        "edge_glow":      preset.get("neon_glow", 0.4),
        "bleed_lo":       preset.get("neon_bleed_lo", 0.78),
        "bleed_hi":       preset.get("neon_bleed_hi", 0.96),
        "sat_bleed":      preset.get("neon_sat_bleed", false),
        "sat_lo":         preset.get("neon_sat_lo", 0.40),
        "sat_hi":         preset.get("neon_sat_hi", 0.60),
        "red_only":       preset.get("neon_red_only", false),
        "accent_channel": preset.get("neon_accent", Vector3(1.0, 0.0, 0.0)),
    })
    _set_params("DirAsciiQuad", {
        "strength":       preset.get("dir_ascii", 0.0),
        "cell_size":      preset.get("dir_cell", 10.0),
        "edge_threshold": preset.get("dir_thresh", 0.10),
        "line_color":     preset.get("dir_line", Color(0.92, 0.20, 0.20, 1)),
        "fill_color":     preset.get("dir_fill", Color(0.02, 0.02, 0.03, 1)),
        "tint_from_scene": preset.get("dir_tint", false),
        "input_scale":    preset.get("dir_input_scale", 1.0),
        "mono_with_red":  preset.get("dir_mono_red", false),
        "mono_white":     preset.get("dir_mono_white_col", Color(0.95, 0.92, 0.86, 1)),
        "mono_red":       preset.get("dir_mono_red_col",   Color(0.98, 0.16, 0.18, 1)),
        "red_threshold":  preset.get("dir_red_thresh", 0.20),
    })
    _set_params("StarscapeQuad", {
        "strength":        preset.get("star", 0.0),
        "cell_size":       preset.get("star_cell", 10.0),
        "time_scale":      preset.get("star_time", 0.40),
        "sky_thresh":      preset.get("star_sky_thresh", 0.10),
        "galaxy_strength": preset.get("star_galaxy", 0.6),
        "star_strength":   preset.get("star_stars", 0.85),
        "chip_strength":   preset.get("star_chip", 0.45),
        "cloud_strength":  preset.get("star_cloud", 0.0),
        "cloud_scale":     preset.get("star_cloud_scale", 0.012),
        "cloud_floor":     preset.get("star_cloud_floor", 0.55),
        "force_full":      preset.get("star_force_full", false),
    })
    _set_params("AsciiQuad", {
        "strength":        preset["ascii"],
        "cell_size":       preset["ascii_cell"],
        "gamma":           preset["ascii_gamma"],
        "tint_from_scene": preset.get("ascii_tint", true),
        "fg_color":        preset.get("ascii_fg", Color(0.92, 0.82, 0.55, 1)),
        "bg_color":        preset.get("ascii_bg", Color(0.04, 0.03, 0.02, 1)),
    })
    _set_params("Quad", {
        "palette_size":         preset["palette"],
        "dither_strength":      preset["dither"],
        "scanline_strength":    preset["scanline"],
        "chromatic_aberration": preset["aberration"],
    })
    var label: Node = get_node_or_null(mood_label_path)
    if label is Label:
        (label as Label).text = "MOOD · %s   (F3)" % preset["name"]


func _set_params(node_name: String, params: Dictionary) -> void:
    var node: Node = get_node_or_null(node_name)
    if node == null or not (node is CanvasItem):
        return
    var mat: Material = (node as CanvasItem).material
    if not (mat is ShaderMaterial):
        return
    var sm: ShaderMaterial = mat as ShaderMaterial
    for key in params.keys():
        sm.set_shader_parameter(key, params[key])
