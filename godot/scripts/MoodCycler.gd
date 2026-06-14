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
        # ink lines over pure black fill, with SPARSE RED bleed for
        # truly emissive accents (sign letters, lit windows). The
        # picture is MOSTLY black-and-white, NOT colour-with-some-
        # B&W — accent_channel RED + tight gates so only sat-red
        # emission passes; cream walls / warm cars stay silhouette.
        "name": "high_contrast_bw",
        "palette": 24.0, "dither": 0.04, "scanline": 0.55, "aberration": 0.0,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": false,
        "ascii_fg": Color(1, 1, 1, 1), "ascii_bg": Color(0, 0, 0, 1),
        "neon": 1.0, "neon_thresh": 0.012,
        "neon_edge": Color(1.0, 1.0, 1.0, 1),
        "neon_low":  Color.BLACK, "neon_high": Color.BLACK,
        "neon_grad": 0.0, "neon_blend": 0.45, "neon_glow": 0.18,
        "neon_bleed_lo": 0.88, "neon_bleed_hi": 0.98,
        "neon_red_only": true,
        "neon_accent": Vector3(1.0, 0.0, 0.0),
        "neon_sat_lo": 0.50, "neon_sat_hi": 0.75,
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
        # ANIME MOTION — speed lines + cartoon trails react to player
        # velocity. Standing still = neutral lithograph. Sprinting =
        # parallel ASCII strokes at the frame edges + directional
        # max-blend smear. MoodCycler updates motion_speed every frame.
        "name": "anime_motion",
        "palette": 12.0, "dither": 0.02, "scanline": 0.10, "aberration": 0.0006,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
        "ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
        "neon": 1.0, "neon_thresh": 0.010,
        "neon_edge": Color(1.0, 1.0, 1.0, 1),
        "neon_low":  Color.BLACK, "neon_high": Color.BLACK,
        "neon_grad": 0.0, "neon_blend": 0.55, "neon_glow": 0.10,
        "neon_bleed_lo": 0.82, "neon_bleed_hi": 0.96,
        "neon_red_only": true,
        "neon_accent": Vector3(1.0, 0.0, 0.0),
        "neon_sat_lo": 0.40, "neon_sat_hi": 0.65,
        "motion": 1.0, "motion_cell": 9.0, "motion_density": 0.90,
        "motion_color": Color(1.0, 0.98, 0.92, 1),
        "motion_trail": 0.8,
    },
    {
        # MOTION BLUR — directional smear via gauss_blur. Pairs with
        # anime_motion when speed is high; reads MotionDir from the
        # MoodCycler. Mild scene_blend keeps the boat readable.
        "name": "motion_blur",
        "palette": 14.0, "dither": 0.04, "scanline": 0.10, "aberration": 0.0006,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
        "ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 1, 1, 1),
        "neon_low": Color.BLACK, "neon_high": Color.BLACK,
        "neon_grad": 0.0, "neon_blend": 0.0, "neon_glow": 0.0,
        "blur": 0.65, "blur_mode": 1, "blur_radius": 7.0,
    },
    {
        # DREAM BLUR — Gaussian, omnidirectional. Soft fall-off. Use
        # for memory / dream-state scenes.
        "name": "dream_blur",
        "palette": 20.0, "dither": 0.0, "scanline": 0.0, "aberration": 0.0008,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
        "ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 1, 1, 1),
        "neon_low": Color.BLACK, "neon_high": Color.BLACK,
        "neon_grad": 0.0, "neon_blend": 0.0, "neon_glow": 0.0,
        "blur": 0.50, "blur_mode": 0, "blur_radius": 5.0,
    },
    {
        # MACRO HAZE — radial DOF-mimic. Centre stays crisp; edges
        # bleed outward. Cinematic "subject in focus" preset.
        "name": "macro_haze",
        "palette": 16.0, "dither": 0.02, "scanline": 0.05, "aberration": 0.0004,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
        "ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 1, 1, 1),
        "neon_low": Color.BLACK, "neon_high": Color.BLACK,
        "neon_grad": 0.0, "neon_blend": 0.0, "neon_glow": 0.0,
        "blur": 0.55, "blur_mode": 2, "blur_radius": 4.0,
    },
    {
        # STUDIO SOFTBOX — even, low-contrast, no edge stylization.
        # Wide palette, no dither, no scanline. Reads as a controlled
        # studio shot — useful for portrait-ish camera positions.
        "name": "studio",
        "palette": 32.0, "dither": 0.0, "scanline": 0.0, "aberration": 0.0,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
        "ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 1, 1, 1),
        "neon_low": Color.BLACK, "neon_high": Color.BLACK,
        "neon_grad": 0.0, "neon_blend": 0.0, "neon_glow": 0.0,
    },
    {
        # DAY BRIGHT — high-key, faint scanline, no stylized edges.
        # The "this is morning, nothing weird here" baseline.
        "name": "day_bright",
        "palette": 24.0, "dither": 0.02, "scanline": 0.04, "aberration": 0.0002,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
        "ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 1, 1, 1),
        "neon_low": Color.BLACK, "neon_high": Color.BLACK,
        "neon_grad": 0.0, "neon_blend": 0.0, "neon_glow": 0.0,
    },
    {
        # PSYCHEDELIC SUBSTRATE — smooth-framerate ASCII visualizer
        # ticking through the scene. The ascii_render shader's new
        # TIME-driven uniforms drive every motion: per-cell glyph
        # cycling (tick_rate), full-image hue rotation (hue_shift_rate),
        # and a slow brightness pulse (pulse_rate × pulse_depth) for
        # the light-and-darkness wash. Starscape kept on top at high
        # strength so the sky is alive too. Bright, unsettled, alive.
        "name": "psychedelic_substrate",
        "palette": 8.0, "dither": 0.20, "scanline": 0.30, "aberration": 0.0028,
        "ascii": 1.0, "ascii_cell": 6.0, "ascii_gamma": 0.55, "ascii_tint": false,
        "ascii_fg": Color(0.55, 1.0, 0.65, 1),       # phosphor-green base
        "ascii_bg": Color(0.02, 0.0, 0.04, 1),       # deep violet-black
        # TIME-driven motion knobs:
        "ascii_tick": 1.4,            # ~1.4 Hz glyph cycle per cell
        "ascii_pulse": 0.35,          # 0.35 Hz brightness pulse (~2.9 s)
        "ascii_pulse_depth": 0.45,    # ±45% wash
        "ascii_hue_shift": 0.55,      # 0.55 rad/sec → 11 s full hue rotation
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 1, 1, 1),
        "neon_low": Color.BLACK, "neon_high": Color.BLACK,
        "neon_grad": 0.0, "neon_blend": 0.0, "neon_glow": 0.0,
        "star": 1.0, "star_cell": 8.0, "star_time": 0.60,
        "star_sky_thresh": 0.20,
        "star_galaxy": 0.90, "star_stars": 1.0, "star_chip": 0.80,
        "star_cloud": 0.6, "star_cloud_scale": 0.012, "star_cloud_floor": 0.55,
    },
    {
        # ── LIGHTSHOW EXTREME · MAXIMUM PSYCHEDELIC ─────────────────
        # Everything piled on at once. ASCII visualizer at hue-cycling
        # max, motion-trails always on, neon edges in saturated
        # rotating colour, directional blur for streaks, starscape
        # full strength. Scene Light3Ds get strobed too — physical
        # lights pulse with the audio, so the boat windows and dock
        # lamps light-show along with the post-process. "Arty farty
        # psychedelic visual splendor" requested literally.
        "name": "lightshow_extreme",
        "palette": 5.0, "dither": 0.45, "scanline": 0.30, "aberration": 0.0050,
        "ascii": 1.0, "ascii_cell": 5.0, "ascii_gamma": 0.50, "ascii_tint": false,
        "ascii_fg": Color(1.0, 0.20, 0.85, 1),   # hot pink (will hue-cycle)
        "ascii_bg": Color(0.04, 0.0, 0.10, 1),   # deep violet
        "ascii_tick": 3.2,          # aggressive ripple
        "ascii_pulse": 0.85,        # fast wash
        "ascii_pulse_depth": 0.70,  # near full-amplitude breathing
        "ascii_hue_shift": 1.6,     # rapid spectrum rotation
        "neon": 0.9, "neon_thresh": 0.010,
        "neon_edge": Color(1.0, 0.95, 0.65, 1),  # warm gold edges
        "neon_low":  Color(0.10, 0.0, 0.30, 1),
        "neon_high": Color(0.30, 0.0, 0.45, 1),
        "neon_grad": 1.0, "neon_blend": 0.75, "neon_glow": 0.45,
        "neon_bleed_lo": 0.55, "neon_bleed_hi": 0.90,
        "neon_sat_bleed": true,
        "neon_sat_lo": 0.20, "neon_sat_hi": 0.50,
        "motion": 1.0, "motion_cell": 8.0, "motion_density": 1.0,
        "motion_color": Color(1.0, 0.95, 0.80, 1),
        "motion_trail": 0.9,
        "blur": 0.35, "blur_mode": 2, "blur_radius": 5.5,
        "star": 1.0, "star_cell": 7.0, "star_time": 0.85,
        "star_sky_thresh": 0.30,
        "star_galaxy": 1.0, "star_stars": 1.0, "star_chip": 1.0,
        "star_cloud": 0.7, "star_cloud_scale": 0.014, "star_cloud_floor": 0.45,
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

# ── Motion-reactive state (driven by player velocity → MotionQuad)
var _motion_speed: float = 0.0
var _motion_dir: Vector2 = Vector2(1.0, 0.0)
var _motion_dir_target: Vector2 = Vector2(1.0, 0.0)

# ── Scene Light3D pulse cache · the lightshow_extreme mood drives
# the actual scene lights with audio_level + per-light sine phase
# so the physical light show maps to the visualizer.
var _scene_lights: Array = []         # Array[Light3D]
var _scene_light_base_energy: Array[float] = []
var _scene_light_phase: Array[float] = []
var _scene_light_base_color: Array[Color] = []
var _last_lightshow_active: bool = false

# ── System-music audio capture (MusicIn bus + AudioStreamMicrophone)
# The OS audio (whatever the device's music player is doing) gets
# routed into the MusicIn bus when the user sets their system
# monitor source as Godot's audio input device. _audio_level reads
# from this bus instead of Master so Godot's own SFX don't drive
# the visualizer — the music does.
const MUSIC_BUS_NAME: String = "MusicIn"
var _music_bus_idx: int = -1
var _music_player: AudioStreamPlayer

# ── Weather / cloud state · audio-reactive scroll + storm pressure
# cloud_scroll_speed accelerates with audio peak; cloud_floor drops
# as _storm_pressure builds (sustained loud → more clouds gather).
# When pressure crosses STORM_BREAK_THRESHOLD, it dumps — fast scroll
# pulse, then settles back down.
var _storm_pressure: float = 0.0      # 0..1, accumulator
var _storm_release: float = 0.0       # transient after a break
const STORM_BREAK_THRESHOLD: float = 0.85

# ── Day/night cycle
# Slow 0..1 phase. 0 = midnight, 0.25 = sunrise, 0.5 = noon,
# 0.75 = sunset. Drives WorldEnvironment ambient colour /
# background colour / Moon_Key DirectionalLight energy / star
# strength. Sampled fresh each frame; player can't pause it.
const DAY_CYCLE_PERIOD: float = 720.0   # seconds per full day (12 min real-time)
var _day_phase: float = 0.05            # start in deep night so the starscape sells


func _get_material(node_name: String) -> Material:
    var node: Node = get_node_or_null(node_name)
    if node == null or not (node is CanvasItem):
        return null
    return (node as CanvasItem).material

# ── STROBE FLICKERS ───────────────────────────────────────────────
# TWO strobe modes:
#
#   F5 SHIMMER · eye-friendly · DEFAULT
#     Every entry shares the same baseline brightness (pure-black
#     background, near-white or saturated-accent foreground). The
#     strobe alternates ACCENT COLOUR, never overall luminance.
#     `linework` is the interstitial that resets every other beat
#     so the eye locks to a steady white-on-black baseline and reads
#     the variations as colour shifts rather than brightness flashes.
#     2 frames per step (≈30 Hz at 60 fps) — vibration, not strobe.
#
#   F6 RIFT · dramatic · saved for hero moments
#     The original sequence: substrate / linework / demoscene_ascii
#     / high_contrast_bw / blueprint_red / cel_shaded / etc. Heavy
#     brightness contrast between adjacent frames — eye-straining
#     ON PURPOSE. Use for narrative breaks ("reality tears open").
#     5 frames per step (12 Hz) so individual frames register.
const STROBE_NAMES_SHIMMER: Array = [
    "linework", "ink_blue", "linework", "ink_green",
    "linework", "blueprint_red", "linework", "noir",
    "linework", "ink_blue", "linework", "high_contrast_bw",
    "linework", "ink_green", "linework", "blueprint_red",
    "linework",
]
const STROBE_NAMES_RIFT: Array = [
    "substrate", "linework", "demoscene_ascii", "high_contrast_bw",
    "ink_blue", "blueprint_red", "cel_shaded", "ink_green",
    "noir", "precipice", "linework", "substrate",
]
const STROBE_FRAMES_SHIMMER: int = 2     # ≈30 Hz — vibration
const STROBE_FRAMES_RIFT: int = 5        # ≈12 Hz — perceptible strobe
var strobe_active: bool = false
var strobe_step: int = 0
var strobe_frame: int = 0
var strobe_return_index: int = 0
var _strobe_indices_shimmer: Array[int] = []
var _strobe_indices_rift: Array[int] = []
var _strobe_indices_active: Array[int] = []
var _strobe_frames_active: int = 2


func _ready() -> void:
    _apply(MOODS[current_index])
    print("[Mood] %s · F3 cycle · F5 shimmer · F6 rift · RMB+look strata wheel" % MOODS[current_index]["name"])
    var by_name: Dictionary = {}
    for i in range(MOODS.size()):
        by_name[MOODS[i]["name"]] = i
    for name in STROBE_NAMES_SHIMMER:
        if by_name.has(name):
            _strobe_indices_shimmer.append(by_name[name])
    for name in STROBE_NAMES_RIFT:
        if by_name.has(name):
            _strobe_indices_rift.append(by_name[name])
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
    # Cache scene Light3Ds for the lightshow_extreme pulse system.
    # Walks from this node's parent (scene root) downward.
    var root := get_tree().current_scene
    if root:
        _collect_lights(root)
    for i in range(_scene_lights.size()):
        _scene_light_phase.append(float(i) * 1.273)   # ~irrational so they don't sync
    # Resolve MusicIn bus + spawn the AudioStreamMicrophone player.
    # If audio input isn't available (driver/enable_input off or the
    # device has no input source) the player just stays silent and
    # _audio_level falls back to whatever Godot itself is playing.
    _music_bus_idx = AudioServer.get_bus_index(MUSIC_BUS_NAME)
    if _music_bus_idx >= 0:
        _music_player = AudioStreamPlayer.new()
        _music_player.stream = AudioStreamMicrophone.new()
        _music_player.bus = MUSIC_BUS_NAME
        _music_player.autoplay = true
        add_child(_music_player)
        _music_player.play()
        print("[Mood] MusicIn capture armed · bus %d · set system monitor as Godot audio input" % _music_bus_idx)
    else:
        print("[Mood] MusicIn bus missing — audio reactive falls back to Master")


func _collect_lights(node: Node) -> void:
    if node is Light3D:
        _scene_lights.append(node)
        _scene_light_base_energy.append((node as Light3D).light_energy)
        _scene_light_base_color.append((node as Light3D).light_color)
    for child in node.get_children():
        _collect_lights(child)


func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_F3:
            action_cycle_mood(1)
        elif event.keycode == KEY_F5:
            action_strobe_shimmer()
        elif event.keycode == KEY_F6:
            action_strobe_rift()
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
    # ── audio-reactive sampling: read BOTH MusicIn (system audio
    # capture) AND Master (Godot's own sounds — Riffmaster etc).
    # Take whichever is louder so the visualizer always reacts:
    #   · user sets monitor source as Godot audio input → MusicIn fires
    #   · no system audio set up → Riffmaster keys still drive it
    # No "silent visualizer" failure mode.
    var master_lin: float = db_to_linear(AudioServer.get_bus_peak_volume_left_db(0, 0))
    var music_lin: float = 0.0
    if _music_bus_idx >= 0:
        music_lin = db_to_linear(AudioServer.get_bus_peak_volume_left_db(_music_bus_idx, 0))
    var combined: float = max(master_lin, music_lin)
    _audio_level = _audio_level * AUDIO_DECAY + combined * (1.0 - AUDIO_DECAY)

    # ── Weather state: storm pressure builds with sustained loud
    # music, dumps in a fast "break" when it crosses the threshold.
    if _audio_level > 0.25:
        _storm_pressure += delta * (_audio_level - 0.20) * 0.18
    else:
        _storm_pressure -= delta * 0.05   # slowly dissipate when quiet
    _storm_pressure = clamp(_storm_pressure, 0.0, 1.0)
    if _storm_pressure >= STORM_BREAK_THRESHOLD and _storm_release <= 0.0:
        _storm_release = 1.0
        print("[Mood] storm break · scroll pulse")
    _storm_release = max(0.0, _storm_release - delta * 0.30)

    # ── Day/night cycle advances always — even in menus.
    _day_phase = fposmod(_day_phase + delta / DAY_CYCLE_PERIOD, 1.0)

    # ── Drive starscape cloud scroll & floor.
    var star_mat: Material = _get_material("StarscapeQuad")
    if star_mat is ShaderMaterial:
        var sm: ShaderMaterial = star_mat as ShaderMaterial
        # Scroll: base + audio acceleration + storm-break pulse.
        # Direction stays diagonal (positive u, slight v) so weather
        # appears to come from the west.
        var sx: float = 0.025 + _audio_level * 0.18 + _storm_release * 0.45
        var sy: float = 0.008 + _audio_level * 0.06 + _storm_release * 0.10
        sm.set_shader_parameter("cloud_scroll", Vector2(sx, sy))
        # Floor: more clouds gather as storm pressure builds; the
        # break instant doesn't change floor (clouds break apart by
        # scrolling fast, not by vanishing).
        var floor_val: float = 0.55 - _storm_pressure * 0.20
        sm.set_shader_parameter("cloud_floor", clamp(floor_val, 0.30, 0.70))

    # ── Day/night cycle → ambient + key light energy + background.
    # day_phase mapping: 0 midnight, 0.25 sunrise, 0.5 noon,
    # 0.75 sunset. Use a smoothstep to bias the dawn/dusk windows.
    var sun_factor: float = 0.5 - 0.5 * cos(_day_phase * TAU)   # 0 night, 1 noon
    var moon_key: DirectionalLight3D = get_node_or_null(NodePath("../Moon_Key"))
    if moon_key:
        # Moon is dim at noon, bright at midnight.
        moon_key.light_energy = lerp(0.42, 0.06, sun_factor)
        # Warm-shift colour through the day (cool at night → warm dawn → daylight neutral → warm dusk → cool again)
        var warm: float = sun_factor
        moon_key.light_color = Color(
            lerp(0.62, 0.98, warm),
            lerp(0.72, 0.92, warm),
            lerp(0.95, 0.80, warm),
            1.0
        )
    var fill_bounce: DirectionalLight3D = get_node_or_null(NodePath("../Fill_Bounce"))
    if fill_bounce:
        fill_bounce.light_energy = lerp(0.05, 0.30, sun_factor)
    var env: WorldEnvironment = get_node_or_null(NodePath("../WorldEnvironment"))
    if env and env.environment:
        var e: Environment = env.environment
        e.ambient_light_energy = lerp(0.18, 0.85, sun_factor)
        e.background_color = Color(
            lerp(0.03, 0.42, sun_factor),
            lerp(0.04, 0.58, sun_factor),
            lerp(0.06, 0.78, sun_factor),
            1.0
        )

    # ── lightshow_extreme · drive every scene Light3D from the audio
    # and a per-light sine phase. The actual physical lights pulse
    # with the music, giving the post-process visualizer a real-light
    # counterpart so the boat windows and dock lamps STROBE along.
    var mood_name: String = MOODS[current_index]["name"]
    if mood_name == "lightshow_extreme":
        var t: float = float(Time.get_ticks_msec()) / 1000.0
        for i in range(_scene_lights.size()):
            var light: Light3D = _scene_lights[i]
            if light == null:
                continue
            var phase: float = _scene_light_phase[i]
            var beat: float = 0.5 + 0.5 * sin(t * 4.0 + phase)
            var audio_pump: float = _audio_level * 2.4
            var mult: float = 0.4 + beat * 1.6 + audio_pump
            light.light_energy = _scene_light_base_energy[i] * mult
            # Hue-shift the light colour through the spectrum too —
            # phase-offset per light so they're not all the same hue
            # at the same time.
            var h: float = fposmod(t * 0.15 + phase * 0.08, 1.0)
            light.light_color = Color.from_hsv(h, 0.65, 1.0, 1.0)
    elif _last_lightshow_active:
        # Just LEFT lightshow_extreme — restore every cached light to
        # its base values so other moods don't inherit strobed state.
        for i in range(_scene_lights.size()):
            var light: Light3D = _scene_lights[i]
            if light != null:
                light.light_energy = _scene_light_base_energy[i]
                light.light_color = _scene_light_base_color[i]
    _last_lightshow_active = (mood_name == "lightshow_extreme")

    # ── psychedelic_substrate · continuous-play visualizer.
    # Every parameter has its OWN slow-drift envelope so the picture
    # never repeats exactly. The shader's TIME-driven motion handles
    # the per-frame ripple/pulse/hue cycling; this loop drifts the
    # MOTION RATES themselves so the rhythm of the picture evolves
    # too. fg/bg colours rotate through complementary palettes via a
    # phase-shifted HSV cycle. Audio level folds in as an extra
    # intensity push on tick/pulse.
    if MOODS[current_index]["name"] == "psychedelic_substrate":
        var t: float = float(Time.get_ticks_msec()) / 1000.0
        var ascii_mat: Material = _get_material("AsciiQuad")
        if ascii_mat is ShaderMaterial:
            var sm: ShaderMaterial = ascii_mat as ShaderMaterial
            var tick: float = 1.4 + 0.6 * sin(t * 0.067) + _audio_level * 0.8
            var pulse: float = 0.35 + 0.15 * sin(t * 0.041) + _audio_level * 0.3
            var pulse_depth: float = 0.45 + 0.10 * sin(t * 0.029)
            var hue: float = 0.55 + 0.25 * sin(t * 0.053)
            sm.set_shader_parameter("tick_rate", tick)
            sm.set_shader_parameter("pulse_rate", pulse)
            sm.set_shader_parameter("pulse_depth", clamp(pulse_depth, 0.0, 1.0))
            sm.set_shader_parameter("hue_shift_rate", hue)
            # FG colour slow-cycles through HSV — phase-shifted from
            # the shader's own hue rotation so the two don't lock.
            var fg_h: float = fposmod(t * 0.04, 1.0)
            sm.set_shader_parameter("fg_color", Color.from_hsv(fg_h, 0.55, 1.0, 1.0))
            # BG slow-cycles complementary (opposite hue, near-black)
            var bg_h: float = fposmod(fg_h + 0.5, 1.0)
            sm.set_shader_parameter("bg_color", Color.from_hsv(bg_h, 0.85, 0.10, 1.0))

    # ── motion-reactive sampling: read the player's velocity from the
    # "player" group, project the forward 2D component, smooth, push
    # to the motion_ascii shader. motion_speed is 0..1, motion_dir is
    # a screen-space 2D unit vector.
    var player := get_tree().get_first_node_in_group("player")
    if player and "velocity" in player:
        var vel: Vector3 = player.velocity
        var horiz: Vector2 = Vector2(vel.x, vel.z)
        var raw_speed: float = horiz.length()
        # Normalise — 12 m/s sprint ≈ 1.0
        var target_speed: float = clamp(raw_speed / 12.0, 0.0, 1.0)
        _motion_speed = _motion_speed * 0.85 + target_speed * 0.15
        if raw_speed > 0.1:
            _motion_dir_target = horiz.normalized()
        _motion_dir = _motion_dir.lerp(_motion_dir_target, 0.18)
        var motion_mat: Material = _get_material("MotionQuad")
        if motion_mat is ShaderMaterial:
            (motion_mat as ShaderMaterial).set_shader_parameter("motion_speed", _motion_speed)
            (motion_mat as ShaderMaterial).set_shader_parameter("motion_dir", _motion_dir)
        var blur_mat: Material = _get_material("BlurQuad")
        if blur_mat is ShaderMaterial:
            (blur_mat as ShaderMaterial).set_shader_parameter("motion_dir", _motion_dir)

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
    if strobe_frame < _strobe_frames_active:
        return
    strobe_frame = 0
    if strobe_step >= _strobe_indices_active.size():
        strobe_active = false
        current_index = strobe_return_index
        _apply(MOODS[current_index])
        print("[Mood] strobe end → %s" % MOODS[current_index]["name"])
        return
    var idx: int = _strobe_indices_active[strobe_step]
    _apply(MOODS[idx])
    strobe_step += 1


func action_cycle_mood(direction: int) -> void:
    _strata_step(direction)


func action_strobe_shimmer() -> void:
    _start_strobe(_strobe_indices_shimmer, STROBE_FRAMES_SHIMMER, "shimmer")


func action_strobe_rift() -> void:
    _start_strobe(_strobe_indices_rift, STROBE_FRAMES_RIFT, "rift")


func _start_strobe(indices: Array[int], frames_per_step: int, label: String) -> void:
    if indices.is_empty():
        return
    _strobe_indices_active = indices
    _strobe_frames_active = frames_per_step
    strobe_active = true
    strobe_step = 0
    strobe_frame = 0
    strobe_return_index = current_index
    print("[Mood] %s · return to %s in %d steps" %
          [label, MOODS[strobe_return_index]["name"], indices.size()])


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
    _set_params("MotionQuad", {
        "strength":      preset.get("motion", 0.0),
        "cell_size":     preset.get("motion_cell", 9.0),
        "line_color":    preset.get("motion_color", Color(1.0, 0.98, 0.92, 1)),
        "trail_strength":preset.get("motion_trail", 0.6),
        "line_density":  preset.get("motion_density", 0.85),
    })
    _set_params("BlurQuad", {
        "strength":  preset.get("blur", 0.0),
        "blur_mode": preset.get("blur_mode", 0),
        "radius":    preset.get("blur_radius", 4.0),
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
        "tick_rate":       preset.get("ascii_tick", 0.0),
        "pulse_rate":      preset.get("ascii_pulse", 0.0),
        "pulse_depth":     preset.get("ascii_pulse_depth", 0.0),
        "hue_shift_rate":  preset.get("ascii_hue_shift", 0.0),
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
