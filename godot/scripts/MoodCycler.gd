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
		# slow spiral galaxy + twinkling stars + fungal-microchip drift.
		# sky pixels — galaxy spiral, twinkling stars, fungal chip
		# all near their max. sky_thresh widened (0.10 → 0.18) so
		# more "almost-dark" pixels qualify as sky and accept paint.
		# Large diffuse fBM clouds — sparse-dot penetration at edges,
		# cross-hatch & solid glyphs in the dense cores. Drifts slowly
		# horizontally; floor controls how much of sky is "clear".
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
		# SUBSTRATE_PRESS — the reference-close substrate look. Pure
		# black field, white ink lines from neon_edge with red-only
		# bleed, dense monotone-white glyph stipple from
		# ascii_directional. Pushes blueprint_red further: smaller
		# cells (6 px vs 7), higher dir_ascii strength (0.70 vs 0.45),
		# lower input_scale cutoff (0.55 vs 0.40) so more model
		# surfaces qualify and get monotone stipple. Red bleed stays
		# tight so only sign letters and life rings show colour.
		"name": "substrate_press",
		"palette": 16.0, "dither": 0.01, "scanline": 0.08, "aberration": 0.0,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": false,
		"ascii_fg": Color(0.95, 0.92, 0.88, 1), "ascii_bg": Color(0, 0, 0, 1),
		"neon": 1.0, "neon_thresh": 0.005,
		"neon_edge": Color(0.96, 0.94, 0.88, 1),
		"neon_low":  Color(0.0, 0.0, 0.0, 1),
		"neon_high": Color(0.0, 0.0, 0.0, 1),
		"neon_grad": 0.0, "neon_blend": 0.55, "neon_glow": 0.06,
		"neon_bleed_lo": 0.80, "neon_bleed_hi": 0.96,
		"neon_red_only": true,
		"neon_accent": Vector3(1.0, 0.0, 0.0),
		"neon_sat_lo": 0.35, "neon_sat_hi": 0.60,
		"dir_ascii": 0.70, "dir_cell": 6.0, "dir_thresh": 0.05,
		"dir_line": Color(0.95, 0.92, 0.88, 1),
		"dir_fill": Color(0.0, 0.0, 0.0, 1),
		"dir_tint": false,
		"dir_input_scale": 0.55,
		"dir_mono_red": true,
		"dir_mono_white_col": Color(0.95, 0.92, 0.88, 1),
		"dir_mono_red_col":   Color(0.98, 0.18, 0.20, 1),
		"dir_red_thresh": 0.30,
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
		"name": "linework_overlay",
		# INK PRESS · OVERLAY blend — the linework stylization
		# MULTIPLIES into the scene instead of replacing it. The boat
		# geometry / lighting stays visible underneath the ink lines.
		# Use when you want to read the detail of the world while
		# keeping the stylized aesthetic on top.
		"palette": 32.0, "dither": 0.02, "scanline": 0.06, "aberration": 0.0,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
		"ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
		"neon": 1.0, "neon_thresh": 0.020,
		"neon_edge": Color(1.0, 1.0, 1.0, 1),
		"neon_low":  Color(0.0, 0.0, 0.0, 1),
		"neon_high": Color(0.0, 0.0, 0.0, 1),
		"neon_grad": 0.0, "neon_blend": 0.0, "neon_glow": 0.10,
		"neon_bleed_lo": 0.78, "neon_bleed_hi": 0.96,
		"neon_blend_mode": 2,         # OVERLAY — scene detail visible
	},
	{
		"name": "linework_multiply",
		# INK PRESS · MULTIPLY blend — stylization darkens the scene
		# by multiplying. Edges visible as bright streaks; everywhere
		# else the boat shows through tinted.
		"palette": 32.0, "dither": 0.02, "scanline": 0.06, "aberration": 0.0,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
		"ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
		"neon": 1.0, "neon_thresh": 0.020,
		"neon_edge": Color(1.0, 1.0, 1.0, 1),
		"neon_low":  Color(0.0, 0.0, 0.0, 1),
		"neon_high": Color(0.0, 0.0, 0.0, 1),
		"neon_grad": 0.0, "neon_blend": 0.0, "neon_glow": 0.10,
		"neon_bleed_lo": 0.78, "neon_bleed_hi": 0.96,
		"neon_blend_mode": 1,         # MULTIPLY
	},
	{
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
		# slow spiral galaxy + twinkling stars + fungal-microchip drift.
		# sky pixels — galaxy spiral, twinkling stars, fungal chip
		# all near their max. sky_thresh widened (0.10 → 0.18) so
		# more "almost-dark" pixels qualify as sky and accept paint.
		# Large diffuse fBM clouds — sparse-dot penetration at edges,
		# cross-hatch & solid glyphs in the dense cores. Drifts slowly
		# horizontally; floor controls how much of sky is "clear".
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
		# strength gives the parallax-scroll feel demoscenes love.
		"name": "demoscene_ascii",
		"palette": 5.0, "dither": 0.50, "scanline": 0.80, "aberration": 0.0048,
		"ascii": 1.0, "ascii_cell": 7.0, "ascii_gamma": 0.65, "ascii_tint": false,
		"ascii_fg": Color(0.42, 0.92, 1.0, 1),       # demoscene cyan
		"ascii_bg": Color(0.04, 0.0, 0.08, 1),       # deep purple-black
		"neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 0.22, 0.78, 1),
		"neon_low": Color.BLACK, "neon_high": Color.BLACK,
		"neon_grad": 0.0, "neon_blend": 0.0, "neon_glow": 0.0,
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
		"name": "silent_film_24",
		# 24 fps silent-era cinema with shuddery camera judder. The
		# underlying scene still renders at 60 Hz; old_film quantizes
		# TIME at 24 Hz so brightness / grain / scratches / camera
		# offset all step together at 24 ticks/sec. Picture LOOKS
		# cranked even though gameplay is smooth.
		"palette": 32.0, "dither": 0.0, "scanline": 0.06, "aberration": 0.0,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": false,
		"ascii_fg": Color(1, 1, 1, 1), "ascii_bg": Color.BLACK,
		"neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 1, 1, 1),
		"neon_low": Color.BLACK, "neon_high": Color.BLACK,
		"neon_grad": 0.0, "neon_blend": 0.0, "neon_glow": 0.0,
		"oldfilm": 1.0, "oldfilm_fps": 24.0,
		"oldfilm_tint": Color(0.94, 0.88, 0.72, 1),
		"oldfilm_tint_amt": 0.50,
		"oldfilm_grain": 0.22, "oldfilm_flicker": 0.16,
		"oldfilm_vignette": 0.55, "oldfilm_scratch": 0.14,
		"oldfilm_judder": 0.0035,   # ~4.5 px wobble per simulated frame
	},
	{
		"name": "silent_film_18",
		# Slower 18 fps — slightly more dreamlike, stronger flicker.
		# Same shader, lower sim_fps. Heavier scratches.
		"palette": 32.0, "dither": 0.0, "scanline": 0.06, "aberration": 0.0,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": false,
		"ascii_fg": Color(1, 1, 1, 1), "ascii_bg": Color.BLACK,
		"neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 1, 1, 1),
		"neon_low": Color.BLACK, "neon_high": Color.BLACK,
		"neon_grad": 0.0, "neon_blend": 0.0, "neon_glow": 0.0,
		"oldfilm": 1.0, "oldfilm_fps": 18.0,
		"oldfilm_tint": Color(0.96, 0.90, 0.74, 1),
		"oldfilm_tint_amt": 0.60,
		"oldfilm_grain": 0.20, "oldfilm_flicker": 0.24,
		"oldfilm_vignette": 0.60, "oldfilm_scratch": 0.18,
		"oldfilm_judder": 0.0030,
	},
	{
		"name": "silent_film_12",
		# 12 fps — the absolute minimum the user allowed. Strongest
		# flicker + heavy judder. Picture LOOKS stop-motion.
		"palette": 32.0, "dither": 0.0, "scanline": 0.06, "aberration": 0.0,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": false,
		"ascii_fg": Color(1, 1, 1, 1), "ascii_bg": Color.BLACK,
		"neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 1, 1, 1),
		"neon_low": Color.BLACK, "neon_high": Color.BLACK,
		"neon_grad": 0.0, "neon_blend": 0.0, "neon_glow": 0.0,
		"oldfilm": 1.0, "oldfilm_fps": 12.0,
		"oldfilm_tint": Color(0.98, 0.92, 0.76, 1),
		"oldfilm_tint_amt": 0.65,
		"oldfilm_grain": 0.26, "oldfilm_flicker": 0.32,
		"oldfilm_vignette": 0.65, "oldfilm_scratch": 0.22,
		"oldfilm_judder": 0.0045,
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
		# DEBUG_PURPLE · forces neon_edge strength = 1.0 with SOLID
		# bright purple fill (low + high both saturated). If this
		# mood doesn't paint the screen purple, the post-process
		# stack ITSELF isn't running and the bug isn't in subtle
		# mood differences — it's environmental.
		"name": "debug_purple",
		"palette": 32.0, "dither": 0.0, "scanline": 0.0, "aberration": 0.0,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": false,
		"ascii_fg": Color(1, 1, 1, 1), "ascii_bg": Color.BLACK,
		"neon": 1.0, "neon_thresh": 0.50,                          # high thresh → no edges
		"neon_edge": Color(1.0, 0.0, 1.0, 1),
		"neon_low":  Color(0.60, 0.0, 0.95, 1),                    # SOLID PURPLE
		"neon_high": Color(0.85, 0.0, 0.70, 1),
		"neon_grad": 0.0, "neon_blend": 0.0, "neon_glow": 0.0,
		"neon_bleed_lo": 1.0, "neon_bleed_hi": 1.0,                # bleed never triggers
		"neon_sat_bleed": false, "neon_red_only": false,
		"neon_sat_lo": 0.5, "neon_sat_hi": 0.7,
	},
	{
		# HCE · TEXAS BLEACH DAY — grungy pastel, blown-out summer
		# noon. Wide palette so pastels stay smooth; faint dither and
		# sub-pixel aberration for the "summer haze through the screen
		# door" feel; warm cream background bleed via scene_blend at
		# full strength so the whole picture takes on the bleach-and-
		# honey cast. No edge stylization — the lighting + the warm
		# cast do the work.
		"name": "texas_bleach_day",
		"palette": 28.0, "dither": 0.04, "scanline": 0.05, "aberration": 0.0008,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
		"ascii_fg": Color(0.95, 0.86, 0.62, 1), "ascii_bg": Color(0.95, 0.86, 0.62, 1),
		"neon": 1.0, "neon_thresh": 0.20,            # high thresh — almost no edges
		"neon_edge": Color(0.98, 0.88, 0.72, 1),     # warm cream if any do paint
		"neon_low":  Color(0.96, 0.88, 0.74, 1),     # cream fill
		"neon_high": Color(1.0, 0.94, 0.80, 1),
		"neon_grad": 0.4, "neon_blend": 0.85, "neon_glow": 0.10,
		"neon_bleed_lo": 0.20, "neon_bleed_hi": 0.55,  # wide bleed — most of scene
	},
	{
		# HCE · LIMINAL INTERIOR — soft, samey, shadowy night interior.
		# Mild Gaussian blur sands surfaces; warm low-key palette; no
		# edge stylization. Reads like the memory of a room, not the
		# room itself. Pairs with the liminal_night lighting preset.
		"name": "liminal_interior",
		"palette": 18.0, "dither": 0.06, "scanline": 0.10, "aberration": 0.0010,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
		"ascii_fg": Color(0.95, 0.86, 0.62, 1), "ascii_bg": Color(0.10, 0.08, 0.06, 1),
		"neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 1, 1, 1),
		"neon_low": Color.BLACK, "neon_high": Color.BLACK,
		"neon_grad": 0.0, "neon_blend": 0.0, "neon_glow": 0.0,
		"blur": 0.35, "blur_mode": 0, "blur_radius": 3.0,
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
	# ════════════════════════════════════════════════════════════════
	# POLISH-PASS ADDITIONS (2026-06-17)
	# Per-locale + per-scenario moods to cover gaps in the matrix.
	# Each pairs cleanly with one of the new style packs at bottom.
	# ════════════════════════════════════════════════════════════════
	{
		# Diner galley / restaurant kitchen — harsh fluorescent-cool,
		# slight green-cast, hum-in-the-walls grit
		"name": "kitchen_practical",
		"palette": 12.0, "dither": 0.10, "scanline": 0.22, "aberration": 0.0008,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.95, "ascii_tint": true,
		"ascii_fg": Color(0.86, 0.92, 0.88, 1), "ascii_bg": Color(0.06, 0.08, 0.07, 1),
		"neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(0.78, 0.92, 0.86, 1),
		"neon_low": Color(0.20, 0.32, 0.28, 1), "neon_high": Color(0.04, 0.08, 0.07, 1),
		"neon_grad": 1.0, "neon_blend": 0.0, "neon_glow": 0.3,
	},
	{
		# Cocktail bar — single warm pendant, dark everywhere else,
		# the boat's amber down-light at 9pm
		"name": "bar_pendant_amber",
		"palette": 8.0, "dither": 0.22, "scanline": 0.42, "aberration": 0.0014,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
		"ascii_fg": Color(0.98, 0.78, 0.42, 1), "ascii_bg": Color(0.06, 0.04, 0.03, 1),
		"neon": 1.0, "neon_thresh": 0.06,
		"neon_edge": Color(1.0, 0.62, 0.20, 1),
		"neon_low":  Color(0.46, 0.22, 0.08, 1),
		"neon_high": Color(0.04, 0.02, 0.02, 1),
		"neon_grad": 1.0, "neon_blend": 0.18, "neon_glow": 0.55,
	},
	{
		# High-stakes card room — green felt, amber pendant down, room
		# beyond the lamp circle goes dark
		"name": "card_room_pendant",
		"palette": 6.0, "dither": 0.26, "scanline": 0.55, "aberration": 0.0012,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
		"ascii_fg": Color(0.62, 0.92, 0.66, 1), "ascii_bg": Color(0.04, 0.06, 0.04, 1),
		"neon": 1.0, "neon_thresh": 0.05,
		"neon_edge": Color(1.0, 0.62, 0.20, 1),
		"neon_low":  Color(0.16, 0.30, 0.18, 1),   # the felt
		"neon_high": Color(0.02, 0.04, 0.02, 1),
		"neon_grad": 1.0, "neon_blend": 0.22, "neon_glow": 0.45,
	},
	{
		# Staff corridor / lower-deck back hallway — long fluorescent
		# tubes, cold even, the hum you stop hearing
		"name": "fluorescent_corridor",
		"palette": 14.0, "dither": 0.05, "scanline": 0.30, "aberration": 0.0006,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.90, "ascii_tint": true,
		"ascii_fg": Color(0.86, 0.90, 0.96, 1), "ascii_bg": Color(0.06, 0.07, 0.09, 1),
		"neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(0.86, 0.90, 0.96, 1),
		"neon_low": Color(0.20, 0.24, 0.28, 1), "neon_high": Color(0.04, 0.05, 0.07, 1),
		"neon_grad": 1.0, "neon_blend": 0.0, "neon_glow": 0.25,
	},
	{
		# Candlelight — warm low, deep darks. Pairs with candlelight
		# lighting preset for cathedral workbench + private dining
		"name": "candlelight_low",
		"palette": 6.0, "dither": 0.30, "scanline": 0.48, "aberration": 0.0020,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.80, "ascii_tint": true,
		"ascii_fg": Color(1.0, 0.78, 0.42, 1), "ascii_bg": Color(0.04, 0.02, 0.01, 1),
		"neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1.0, 0.78, 0.42, 1),
		"neon_low": Color(0.32, 0.18, 0.10, 1), "neon_high": Color(0.04, 0.02, 0.01, 1),
		"neon_grad": 1.0, "neon_blend": 0.0, "neon_glow": 0.5,
	},
	{
		# TV glow — cool blue from one direction. The screen-watching
		# look (Elicia at the laptop, John at booth 6 watching the
		# silent TV behind the counter)
		"name": "tv_glow_blue",
		"palette": 8.0, "dither": 0.20, "scanline": 0.55, "aberration": 0.0016,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
		"ascii_fg": Color(0.62, 0.78, 0.96, 1), "ascii_bg": Color(0.02, 0.04, 0.08, 1),
		"neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(0.62, 0.78, 0.96, 1),
		"neon_low": Color(0.10, 0.18, 0.32, 1), "neon_high": Color(0.02, 0.03, 0.06, 1),
		"neon_grad": 1.0, "neon_blend": 0.0, "neon_glow": 0.35,
	},
	{
		# Pre-dawn warm windows + cool moonlight bleed. The 4 AM
		# diner with the sodium lot light leaking in
		"name": "dawn_warm",
		"palette": 16.0, "dither": 0.08, "scanline": 0.22, "aberration": 0.0008,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
		"ascii_fg": Color(0.96, 0.82, 0.62, 1), "ascii_bg": Color(0.10, 0.10, 0.14, 1),
		"neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(0.96, 0.82, 0.62, 1),
		"neon_low": Color(0.46, 0.36, 0.28, 1), "neon_high": Color(0.16, 0.18, 0.24, 1),
		"neon_grad": 1.0, "neon_blend": 0.0, "neon_glow": 0.4,
	},
	{
		# Bright morning interior — slight bloom, clean. The bungalow
		# at 9 AM, the riverboat after the breakfast rush
		"name": "morning_bright",
		"palette": 24.0, "dither": 0.04, "scanline": 0.12, "aberration": 0.0005,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 1.0, "ascii_tint": true,
		"ascii_fg": Color(0.96, 0.92, 0.84, 1), "ascii_bg": Color(0.12, 0.14, 0.16, 1),
		"neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 0.22, 0.78, 1),
		"neon_low": Color(0.42, 0.12, 0.50, 1), "neon_high": Color(0.10, 0.05, 0.25, 1),
		"neon_grad": 1.0, "neon_blend": 0.0, "neon_glow": 0.3,
	},
	{
		# Rain interior — looking out through a wet window, cool light,
		# gentle blur. The bungalow porch with the storm coming in
		"name": "rain_interior",
		"palette": 12.0, "dither": 0.12, "scanline": 0.32, "aberration": 0.0010,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.90, "ascii_tint": true,
		"ascii_fg": Color(0.72, 0.82, 0.92, 1), "ascii_bg": Color(0.06, 0.08, 0.10, 1),
		"neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(0.72, 0.82, 0.92, 1),
		"neon_low": Color(0.18, 0.24, 0.30, 1), "neon_high": Color(0.04, 0.06, 0.08, 1),
		"neon_grad": 1.0, "neon_blend": 0.0, "neon_glow": 0.4,
		"blur": 0.28, "blur_mode": 0, "blur_radius": 2.5,
	},
	{
		# Pomegranate Hour cold open — Elicia's B&W chair vibe. Heavy
		# desaturation, dust + grain, low palette. The show's signature
		"name": "pomegranate_hour_open",
		"palette": 4.0, "dither": 0.42, "scanline": 0.66, "aberration": 0.0016,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.78, "ascii_tint": true,
		"ascii_fg": Color(0.92, 0.88, 0.78, 1), "ascii_bg": Color(0.04, 0.03, 0.02, 1),
		"neon": 1.0, "neon_thresh": 0.06,
		"neon_edge": Color(0.95, 0.92, 0.82, 1),
		"neon_low":  Color(0.0, 0.0, 0.0, 1),
		"neon_high": Color(0.0, 0.0, 0.0, 1),
		"neon_grad": 0.0, "neon_blend": 0.05, "neon_glow": 0.4,
		"oldfilm": 0.38, "oldfilm_fps": 18.0,
		"oldfilm_tint": Color(0.96, 0.92, 0.82, 1), "oldfilm_tint_amount": 0.40,
		"oldfilm_grain": 0.22, "oldfilm_flicker": 0.24,
		"oldfilm_vignette": 0.55, "oldfilm_scratch": 0.10,
	},
	{
		# Whispers from the Liminal — Anya's footage's grading. Sepia +
		# heavier film grain + judder. The take Elicia keeps re-cutting
		"name": "whispers_take",
		"palette": 8.0, "dither": 0.32, "scanline": 0.56, "aberration": 0.0024,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.82, "ascii_tint": true,
		"ascii_fg": Color(0.96, 0.86, 0.62, 1), "ascii_bg": Color(0.06, 0.04, 0.02, 1),
		"neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(0.96, 0.86, 0.62, 1),
		"neon_low": Color(0.36, 0.24, 0.14, 1), "neon_high": Color(0.08, 0.04, 0.02, 1),
		"neon_grad": 1.0, "neon_blend": 0.0, "neon_glow": 0.45,
		"oldfilm": 0.48, "oldfilm_fps": 24.0,
		"oldfilm_tint": Color(0.92, 0.78, 0.42, 1), "oldfilm_tint_amount": 0.55,
		"oldfilm_grain": 0.20, "oldfilm_flicker": 0.18,
		"oldfilm_vignette": 0.48, "oldfilm_scratch": 0.15,
		"oldfilm_judder": 0.008,
	},
	{
		# VN clean — minimal style, clean read for dialogue scenes.
		# Pairs with the visual-novel pipeline where character art
		# is the focus, not the postprocess
		"name": "vn_clean",
		"palette": 24.0, "dither": 0.03, "scanline": 0.08, "aberration": 0.0004,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 1.0, "ascii_tint": true,
		"ascii_fg": Color(0.96, 0.92, 0.84, 1), "ascii_bg": Color(0.10, 0.08, 0.10, 1),
		"neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 0.22, 0.78, 1),
		"neon_low": Color(0.42, 0.12, 0.50, 1), "neon_high": Color(0.10, 0.05, 0.25, 1),
		"neon_grad": 1.0, "neon_blend": 0.0, "neon_glow": 0.2,
	},
	{
		# Gauntlet intro — punchy, attention-grabbing, brief. The boot
		# moment when the gauntlet UI lands and the world tightens
		"name": "gauntlet_intro",
		"palette": 5.0, "dither": 0.32, "scanline": 0.58, "aberration": 0.0026,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.80, "ascii_tint": true,
		"ascii_fg": Color(0.98, 0.78, 0.36, 1), "ascii_bg": Color(0.04, 0.03, 0.02, 1),
		"neon": 1.0, "neon_thresh": 0.04,
		"neon_edge": Color(1.0, 0.42, 0.20, 1),
		"neon_low":  Color(0.62, 0.18, 0.18, 1),
		"neon_high": Color(0.04, 0.02, 0.02, 1),
		"neon_grad": 1.0, "neon_blend": 0.30, "neon_glow": 0.7,
	},
	{
		# Sodium streetlamp — orange single source, dark everywhere.
		# The parking lot at 3 AM
		"name": "sodium_streetlamp",
		"palette": 4.0, "dither": 0.28, "scanline": 0.46, "aberration": 0.0022,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.80, "ascii_tint": true,
		"ascii_fg": Color(1.0, 0.66, 0.22, 1), "ascii_bg": Color(0.04, 0.02, 0.01, 1),
		"neon": 1.0, "neon_thresh": 0.06,
		"neon_edge": Color(1.0, 0.72, 0.28, 1),
		"neon_low":  Color(0.42, 0.20, 0.06, 1),
		"neon_high": Color(0.02, 0.01, 0.01, 1),
		"neon_grad": 1.0, "neon_blend": 0.20, "neon_glow": 0.55,
	},
	{
		# Back-room signal — green-tinted, low, the "the door has been
		# closed for forty minutes" feel. Pairs with tv_glow lighting
		# for the cathedral devil station + the riverboat back room
		"name": "back_room_signal",
		"palette": 6.0, "dither": 0.30, "scanline": 0.58, "aberration": 0.0018,
		"ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.82, "ascii_tint": true,
		"ascii_fg": Color(0.62, 0.96, 0.62, 1), "ascii_bg": Color(0.02, 0.04, 0.02, 1),
		"neon": 1.0, "neon_thresh": 0.05,
		"neon_edge": Color(0.42, 0.92, 0.46, 1),
		"neon_low":  Color(0.14, 0.32, 0.18, 1),
		"neon_high": Color(0.02, 0.04, 0.02, 1),
		"neon_grad": 1.0, "neon_blend": 0.22, "neon_glow": 0.5,
	},
]

var current_index: int = 8   # start on linework — pure visible-edges-only render

# ── VN FOCUS MODE ─────────────────────────────────────────────────
# When a dialogue line is active in the visual novel layer, soften
# the noise-y shader params (scanline, aberration, ASCII strength,
# oldfilm grain + judder) so dialogue text reads cleanly without
# breaking the mood's silhouette + colour identity. GameEngine
# calls vn_focus_dialogue(true) at the start of a say/think, and
# vn_focus_dialogue(false) on narrate or scene end.
var _vn_focus_active: bool = false
# Per-param multipliers applied when _vn_focus_active is true.
# Values below 1.0 attenuate; 1.0 leaves the preset alone. Tune
# here to taste — these are the readability-vs-mood trade-offs.
const VN_FOCUS_SOFTEN := {
	"scanline":      0.50,   # halve scanline so text edges read
	"aberration":    0.50,   # reduce chromatic fringe on glyphs
	"ascii":         0.30,   # ASCII obscures text most; pull hard
	"dir_ascii":     0.45,   # same for the linework variant
	"oldfilm":       0.65,   # keep film vibe but settle the grain
	"oldfilm_grain": 0.50,
	"oldfilm_judder":0.20,   # judder is the worst for text
	"motion":        0.30,   # speed lines distract from dialogue
}

# ── BLEND MODE OVERRIDE (F9) ──────────────────────────────────────
# A sub-toggle that overrides the active mood's neon_edge blend mode
# without touching any other parameter. -1 = "use the preset's own
# blend mode" (the default). 0..4 = force the corresponding blend:
# 0 REPLACE, 1 MULTIPLY, 2 OVERLAY, 3 SCREEN, 4 ADD. Persists across
# F3 / RMB cycling so the user can pick a base mood, then layer a
# blend mode that reveals the scene underneath.
const BLEND_MODE_NAMES: Array[String] = [
	"preset", "replace", "multiply", "overlay", "screen", "add",
]
var blend_mode_override: int = -1

# ── BLEND INTENSITY DIAL (F10) ────────────────────────────────────
# Multiplies the neon_edge layer's strength so the raw scene
# dominates and the stylization sits as a subtle overlay on top.
# -1 = preset default (1.0). Otherwise we use BLEND_AMOUNTS[idx].
# Most blend modes (multiply, screen, add) are commutative — there's
# no useful "invert source/target", just less of the stylized layer
# over more of the raw. This is that dial.
const BLEND_AMOUNTS: Array[float] = [1.0, 0.6, 0.3, 0.15]
const BLEND_AMOUNT_LABELS: Array[String] = ["preset", "full", "60%", "30%", "15%"]
var blend_amount_override: int = -1

# Per-percent override: -1 means use blend_amount_override (above);
# 0..100 means use this exact percent as the blend scale.
# Adjusted via action_blend_pct_tens() / action_blend_pct_ones() —
# two-button incremental tuner (one button bumps the tens place,
# the other bumps the ones place; both wrap at 100).
var blend_amount_pct: int = -1

# ── TIME-OF-DAY LIGHTING TOGGLE (F11) ─────────────────────────────
# A proper time-of-day cycle, not just a brightness scalar. Per
# preset:
#   dir_mult       · multiplier on each DirectionalLight3D's base
#                    energy. Use BIG numbers (8-15) to push the
#                    night-scale 0.3 keys into real daylight.
#   practical_mult · scales OmniLight3D / SpotLight3D. 0.0 turns the
#                    sodium lamps off for midday; 1.0 leaves them at
#                    their night base.
#   dir_tint       · colour the directionals lerp toward.
#   tint_mix       · how strongly to apply dir_tint (0 = keep base
#                    colour, 1 = fully replace).
#   sun_pitch_deg  · X rotation of the key directional (0 = horizon,
#                    -90 = straight down). Drives shadow angle.
#   sun_yaw_deg    · Y rotation (east / west).
#   ambient_color  · absolute WorldEnvironment ambient colour.
#   ambient_energy · absolute ambient energy (not a multiplier).
# Defers to lightshow_extreme which already drives lights from audio.
const LIGHTING_PRESETS: Array = [
	{"name": "scene_default", "dir_mult": 1.0, "practical_mult": 1.0,
	"dir_tint": Color.WHITE, "tint_mix": 0.0,
	"sun_pitch_deg": NAN, "sun_yaw_deg": NAN,
	"ambient_color": Color.WHITE, "ambient_energy": -1.0,
	"sky_top": Color(0.04, 0.05, 0.10, 1), "sky_horizon": Color(0.10, 0.12, 0.18, 1),
	"sky_energy": 1.0, "fog_color": Color(0.05, 0.06, 0.08, 1)},
	{"name": "midday",        "dir_mult": 14.0, "practical_mult": 0.0,
	"dir_tint": Color(1.0, 0.97, 0.92, 1), "tint_mix": 0.95,
	"sun_pitch_deg": -78.0, "sun_yaw_deg": 18.0,
	"ambient_color": Color(0.62, 0.70, 0.82, 1), "ambient_energy": 1.8,
	"sky_top": Color(0.22, 0.42, 0.78, 1), "sky_horizon": Color(0.72, 0.84, 0.95, 1),
	"sky_energy": 1.6, "fog_color": Color(0.72, 0.82, 0.92, 1)},
	{"name": "golden_hour",   "dir_mult": 8.0, "practical_mult": 0.25,
	"dir_tint": Color(1.0, 0.60, 0.28, 1), "tint_mix": 0.85,
	"sun_pitch_deg": -12.0, "sun_yaw_deg": -75.0,
	"ambient_color": Color(0.95, 0.55, 0.35, 1), "ambient_energy": 1.2,
	"sky_top": Color(0.32, 0.28, 0.42, 1), "sky_horizon": Color(1.0, 0.55, 0.22, 1),
	"sky_energy": 1.3, "fog_color": Color(0.95, 0.62, 0.40, 1)},
	{"name": "blue_hour",     "dir_mult": 3.0, "practical_mult": 0.75,
	"dir_tint": Color(0.45, 0.62, 1.0, 1), "tint_mix": 0.80,
	"sun_pitch_deg": -3.0, "sun_yaw_deg": -92.0,
	"ambient_color": Color(0.32, 0.42, 0.68, 1), "ambient_energy": 0.85,
	"sky_top": Color(0.10, 0.14, 0.32, 1), "sky_horizon": Color(0.42, 0.38, 0.55, 1),
	"sky_energy": 0.85, "fog_color": Color(0.28, 0.32, 0.42, 1)},
	{"name": "dawn",          "dir_mult": 5.0, "practical_mult": 0.45,
	"dir_tint": Color(1.0, 0.78, 0.62, 1), "tint_mix": 0.75,
	"sun_pitch_deg": -8.0, "sun_yaw_deg": 85.0,
	"ambient_color": Color(0.78, 0.62, 0.55, 1), "ambient_energy": 1.0,
	"sky_top": Color(0.28, 0.32, 0.55, 1), "sky_horizon": Color(0.98, 0.70, 0.62, 1),
	"sky_energy": 1.1, "fog_color": Color(0.82, 0.68, 0.62, 1)},
	{"name": "storm_front",   "dir_mult": 4.0, "practical_mult": 0.85,
	"dir_tint": Color(0.72, 0.78, 0.88, 1), "tint_mix": 0.65,
	"sun_pitch_deg": -55.0, "sun_yaw_deg": 0.0,
	"ambient_color": Color(0.48, 0.52, 0.60, 1), "ambient_energy": 0.9,
	"sky_top": Color(0.18, 0.22, 0.28, 1), "sky_horizon": Color(0.42, 0.46, 0.52, 1),
	"sky_energy": 0.8, "fog_color": Color(0.42, 0.46, 0.52, 1)},
	{"name": "overcast_day",  "dir_mult": 9.0, "practical_mult": 0.10,
	"dir_tint": Color(0.92, 0.95, 1.0, 1), "tint_mix": 0.70,
	"sun_pitch_deg": -65.0, "sun_yaw_deg": 0.0,
	"ambient_color": Color(0.72, 0.76, 0.82, 1), "ambient_energy": 1.5,
	"sky_top": Color(0.65, 0.68, 0.72, 1), "sky_horizon": Color(0.80, 0.82, 0.85, 1),
	"sky_energy": 1.2, "fog_color": Color(0.75, 0.78, 0.82, 1)},
	{"name": "midnight",      "dir_mult": 0.6, "practical_mult": 1.0,
	"dir_tint": Color(0.50, 0.60, 0.95, 1), "tint_mix": 0.65,
	"sun_pitch_deg": -28.0, "sun_yaw_deg": 12.0,
	"ambient_color": Color(0.18, 0.22, 0.32, 1), "ambient_energy": 0.32,
	"sky_top": Color(0.02, 0.03, 0.08, 1), "sky_horizon": Color(0.06, 0.08, 0.14, 1),
	"sky_energy": 0.6, "fog_color": Color(0.04, 0.05, 0.08, 1)},
	# HCE-flavoured lighting
	{"name": "texas_noon",    "dir_mult": 18.0, "practical_mult": 0.0,
	"dir_tint": Color(1.0, 0.92, 0.76, 1), "tint_mix": 0.85,
	"sun_pitch_deg": -82.0, "sun_yaw_deg": 10.0,
	"ambient_color": Color(1.0, 0.88, 0.70, 1), "ambient_energy": 2.4,
	"sky_top": Color(0.42, 0.62, 0.88, 1), "sky_horizon": Color(0.95, 0.92, 0.82, 1),
	"sky_energy": 1.9, "fog_color": Color(0.92, 0.88, 0.78, 1)},
	{"name": "liminal_night", "dir_mult": 0.3, "practical_mult": 1.4,
	"dir_tint": Color(0.62, 0.66, 0.85, 1), "tint_mix": 0.50,
	"sun_pitch_deg": -25.0, "sun_yaw_deg": 0.0,
	"ambient_color": Color(0.32, 0.28, 0.25, 1), "ambient_energy": 0.40,
	"sky_top": Color(0.06, 0.05, 0.04, 1), "sky_horizon": Color(0.18, 0.12, 0.10, 1),
	"sky_energy": 0.5, "fog_color": Color(0.16, 0.12, 0.10, 1)},
	# ── POLISH-PASS ADDITIONS (2026-06-17) ───────────────────────────
	# Kitchen overhead — white fluorescent, slight cool cast.
	# Practicals dominate; sun barely registers.
	{"name": "kitchen_overhead", "dir_mult": 0.4, "practical_mult": 1.3,
	"dir_tint": Color(0.92, 0.96, 1.0, 1), "tint_mix": 0.55,
	"sun_pitch_deg": -78.0, "sun_yaw_deg": 0.0,
	"ambient_color": Color(0.78, 0.82, 0.88, 1), "ambient_energy": 0.85,
	"sky_top": Color(0.04, 0.05, 0.08, 1), "sky_horizon": Color(0.10, 0.12, 0.16, 1),
	"sky_energy": 0.5, "fog_color": Color(0.10, 0.12, 0.14, 1)},
	# Sodium streetlamp — single orange point, deep dark elsewhere.
	# For parking lots, back walkways, the gangway at night.
	{"name": "sodium_streetlamp", "dir_mult": 0.4, "practical_mult": 1.6,
	"dir_tint": Color(1.0, 0.72, 0.32, 1), "tint_mix": 0.88,
	"sun_pitch_deg": -10.0, "sun_yaw_deg": -85.0,
	"ambient_color": Color(0.42, 0.28, 0.16, 1), "ambient_energy": 0.32,
	"sky_top": Color(0.02, 0.02, 0.04, 1), "sky_horizon": Color(0.10, 0.06, 0.04, 1),
	"sky_energy": 0.4, "fog_color": Color(0.18, 0.12, 0.08, 1)},
	# Candlelight — warm low, deep darks, practicals lifted.
	# For the cathedral workbench / private-dining table at 9 PM.
	{"name": "candlelight", "dir_mult": 0.15, "practical_mult": 1.5,
	"dir_tint": Color(1.0, 0.78, 0.42, 1), "tint_mix": 0.92,
	"sun_pitch_deg": -20.0, "sun_yaw_deg": 0.0,
	"ambient_color": Color(0.36, 0.22, 0.12, 1), "ambient_energy": 0.28,
	"sky_top": Color(0.02, 0.02, 0.03, 1), "sky_horizon": Color(0.06, 0.04, 0.03, 1),
	"sky_energy": 0.4, "fog_color": Color(0.10, 0.06, 0.04, 1)},
	# TV glow — cool blue from one direction, dim ambient.
	# For the cathedral demon stool, the riverboat back room.
	{"name": "tv_glow", "dir_mult": 0.35, "practical_mult": 0.55,
	"dir_tint": Color(0.42, 0.62, 0.92, 1), "tint_mix": 0.86,
	"sun_pitch_deg": -15.0, "sun_yaw_deg": -90.0,
	"ambient_color": Color(0.14, 0.18, 0.28, 1), "ambient_energy": 0.30,
	"sky_top": Color(0.02, 0.02, 0.04, 1), "sky_horizon": Color(0.04, 0.06, 0.10, 1),
	"sky_energy": 0.4, "fog_color": Color(0.06, 0.08, 0.12, 1)},
	# Bar pendant amber — single warm down, room beyond goes dark.
	# Pairs with bar_pendant_amber mood for cathedral private rooms
	# + Sammy's bar at 9 PM.
	{"name": "bar_pendant_amber", "dir_mult": 0.25, "practical_mult": 1.35,
	"dir_tint": Color(1.0, 0.66, 0.32, 1), "tint_mix": 0.90,
	"sun_pitch_deg": -22.0, "sun_yaw_deg": 0.0,
	"ambient_color": Color(0.32, 0.22, 0.16, 1), "ambient_energy": 0.32,
	"sky_top": Color(0.02, 0.02, 0.03, 1), "sky_horizon": Color(0.08, 0.05, 0.03, 1),
	"sky_energy": 0.4, "fog_color": Color(0.10, 0.07, 0.05, 1)},
	# Dawn diner — warm windows + cool moonlight bleed.
	# The 4 AM D'Ambrosio's with the sodium lot light coming in.
	{"name": "dawn_diner", "dir_mult": 3.0, "practical_mult": 1.15,
	"dir_tint": Color(1.0, 0.78, 0.55, 1), "tint_mix": 0.58,
	"sun_pitch_deg": -10.0, "sun_yaw_deg": 95.0,
	"ambient_color": Color(0.62, 0.55, 0.62, 1), "ambient_energy": 0.78,
	"sky_top": Color(0.18, 0.20, 0.32, 1), "sky_horizon": Color(0.78, 0.55, 0.42, 1),
	"sky_energy": 0.85, "fog_color": Color(0.48, 0.42, 0.42, 1)},
]
var lighting_index: int = 0   # 0 = scene_default

# ── STYLE PACKS (F12) ─────────────────────────────────────────────
# A pack snaps mood + lighting + blend overrides in one tap. Each
# location has a handful of named looks that nail its identity;
# F12 cycles the full list so the user can also jump between
# locations' styles freely. F3 / F9 / F10 / F11 keep working
# independently for mix-and-match after the pack is applied.
# blend_mode / blend_amt of -1 mean "use mood preset's own value".
const STYLE_PACKS: Array = [
	# ── RIVERFRONT (vol5) — ink press, night, river haze ──
	{"name": "rf_substrate",       "mood": "substrate_press",   "lighting": "scene_default",
	"blend_mode": -1, "blend_amt": -1},
	{"name": "rf_linework_night",  "mood": "linework",          "lighting": "scene_default",
	"blend_mode": -1, "blend_amt": -1},
	{"name": "rf_linework_subtle", "mood": "linework_multiply", "lighting": "scene_default",
	"blend_mode": -1, "blend_amt": 1},   # 60% — raw shows through
	{"name": "rf_blue_hour",       "mood": "linework",          "lighting": "blue_hour",
	"blend_mode": -1, "blend_amt": -1},
	# ── HARMONY CREEK ESTATES — bleach Texas day, liminal night ──
	{"name": "hce_texas_day",      "mood": "texas_bleach_day",  "lighting": "texas_noon",
	"blend_mode": -1, "blend_amt": -1},
	{"name": "hce_golden_porch",   "mood": "studio",            "lighting": "golden_hour",
	"blend_mode": -1, "blend_amt": -1},
	{"name": "hce_overcast",       "mood": "day_bright",        "lighting": "overcast_day",
	"blend_mode": -1, "blend_amt": -1},
	{"name": "hce_liminal_night",  "mood": "liminal_interior",  "lighting": "liminal_night",
	"blend_mode": -1, "blend_amt": -1},
	# ── SMALL WOOD (placeholder slot — vol5 future area) ──
	{"name": "smallwood_dawn",     "mood": "macro_haze",        "lighting": "dawn",
	"blend_mode": -1, "blend_amt": -1},
	{"name": "smallwood_storm",    "mood": "dream_blur",        "lighting": "storm_front",
	"blend_mode": -1, "blend_amt": -1},
	# ── UTILITY ──
	{"name": "raw_observation",    "mood": "raw",               "lighting": "scene_default",
	"blend_mode": 0, "blend_amt": 0},   # forces neon off completely
	# ── POLISH-PASS ADDITIONS (2026-06-17) ────────────────────────
	# Per-locale + per-scenario one-tap snaps. Each combines a mood +
	# lighting preset that matches the canonical scenario state.
	# ── D'AMBROSIO'S — Fool (3:47 AM) + Empress (Friday 8 PM) ──
	{"name": "dambrosios_3am",     "mood": "raw",               "lighting": "midnight",
	"blend_mode": -1, "blend_amt": -1},
	{"name": "dambrosios_brunch",  "mood": "studio",            "lighting": "dawn_diner",
	"blend_mode": -1, "blend_amt": -1},
	# ── CATHEDRAL — Magician work-mode + devil-station threat ──
	{"name": "cathedral_workbench","mood": "substrate_press",   "lighting": "candlelight",
	"blend_mode": -1, "blend_amt": -1},
	{"name": "cathedral_devil",    "mood": "back_room_signal",  "lighting": "tv_glow",
	"blend_mode": -1, "blend_amt": -1},
	# ── BUNGALOW — Priestess packing dusk + comforting-void late ──
	{"name": "bungalow_dusk",      "mood": "linework",          "lighting": "blue_hour",
	"blend_mode": -1, "blend_amt": -1},
	{"name": "bungalow_late",      "mood": "noir",              "lighting": "midnight",
	"blend_mode": -1, "blend_amt": -1},
	# ── RIVERBOAT — Emperor at helm (10 PM Friday) ──
	{"name": "riverboat_helm",     "mood": "lithograph",        "lighting": "midnight",
	"blend_mode": -1, "blend_amt": -1},
	# ── POMEGRANATE HOUR — Elicia's show cold open ──
	{"name": "pomegranate_hour",   "mood": "silent_film_18",    "lighting": "midnight",
	"blend_mode": -1, "blend_amt": -1},
	# ── NEW SHADER STYLE PACKS (2026-06-18) — vibe presets the
	#    portrait shader has analogues for, so bg + portrait can be
	#    style-matched with one tap on each. Generic names so any
	#    locale can use them. ───────────────────────────────────
	{"name": "vaporwave_dream",    "mood": "psychedelic_substrate", "lighting": "scene_default",
	"blend_mode": -1, "blend_amt": -1},
	{"name": "glitch_art_chaos",   "mood": "back_room_signal",  "lighting": "tv_glow",
	"blend_mode": -1, "blend_amt": -1},
	{"name": "cyberpunk_neon",     "mood": "noir",              "lighting": "neon_signage",
	"blend_mode": -1, "blend_amt": -1},
	{"name": "film_noir_extreme",  "mood": "high_contrast_bw",  "lighting": "midnight",
	"blend_mode": -1, "blend_amt": -1},
	{"name": "night_vision_green", "mood": "ink_blue",          "lighting": "candlelight_low",
	"blend_mode": -1, "blend_amt": -1},
	{"name": "thermal_heatmap",    "mood": "blueprint_red",     "lighting": "tv_glow",
	"blend_mode": -1, "blend_amt": -1},
	{"name": "comic_book_halftone","mood": "lithograph",        "lighting": "scene_default",
	"blend_mode": -1, "blend_amt": -1},
	{"name": "watercolor_soft",    "mood": "macro_haze",        "lighting": "dawn",
	"blend_mode": -1, "blend_amt": -1},
	{"name": "analog_tape_warp",   "mood": "silent_film_24",    "lighting": "tv_glow_blue",
	"blend_mode": -1, "blend_amt": -1},
	{"name": "broken_signal_tv",   "mood": "back_room_signal",  "lighting": "tv_glow",
	"blend_mode": -1, "blend_amt": -1},
	{"name": "convenience_night",  "mood": "fluorescent_corridor", "lighting": "sodium_streetlamp",
	"blend_mode": -1, "blend_amt": -1},
	{"name": "smoky_bar",          "mood": "macro_haze",        "lighting": "bar_pendant_amber",
	"blend_mode": -1, "blend_amt": -1},
	{"name": "rainy_window",       "mood": "dream_blur",        "lighting": "rain_interior",
	"blend_mode": -1, "blend_amt": -1},
	{"name": "memory_warm",        "mood": "silent_film_12",    "lighting": "candlelight",
	"blend_mode": -1, "blend_amt": -1},
	{"name": "fluorescent_panic",  "mood": "anime_motion",      "lighting": "fluorescent_corridor",
	"blend_mode": -1, "blend_amt": -1},
]
var style_pack_index: int = -1   # -1 = none applied (manual mode)

var _world_env: WorldEnvironment = null
var _world_env_base_energy: float = 0.50
var _world_env_base_color: Color = Color.WHITE
var _sky_material: ProceduralSkyMaterial = null

# ── LIGHTING TRANSITION STATE ─────────────────────────────────────
# Natural day → night transitions: when the user cycles F11 or
# F12, we lerp from the currently-applied preset to the new one
# over LIGHT_LERP_DUR seconds. Same for the sky colour cross-fade.
const LIGHT_LERP_DUR: float = 1.2
var _light_lerp_t: float = 1.0
var _light_lerp_source: Dictionary = {}   # the "from" preset snapshot
var _light_lerp_target: Dictionary = {}   # the "to" preset
# Two parallel arrays so we can scale directional vs practical
# differently — sodium lamps off at midday, key sun pumped up.
var _directional_lights: Array = []     # Array[DirectionalLight3D]
var _directional_base_energy: Array[float] = []
var _directional_base_color: Array[Color] = []
var _directional_base_rotation: Array[Vector3] = []  # euler degrees, original
var _practical_lights: Array = []       # Array[Light3D] (omni/spot)
var _practical_base_energy: Array[float] = []
var _practical_base_color: Array[Color] = []
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
# Per-scene starting style pack. If non-empty AND a STYLE_PACKS
# entry exists with this name, the scene applies it on _ready
# instead of defaulting to current_index's mood. This is how each
# locale opens on its appropriate look (diner → dambrosios_3am,
# bungalow → bungalow_dusk, etc.) without forcing a global default.
# Leave empty to keep the default current_index startup behaviour.
@export var default_style_pack: String = ""
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
	print("[Mood] %s · F3 mood · F5/F6 strobe · F9 blend · F10 amt · F11 light · F12 style · RMB+look strata" % MOODS[current_index]["name"])
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

	# Per-scene starting style pack — applied AFTER strata + lights are
	# resolved so the lighting transition has somewhere to lerp from.
	# If the named pack doesn't exist (typo, etc.) just log and move on
	# without crashing; the scene starts on whatever the default mood is.
	if default_style_pack != "":
		for i in range(STYLE_PACKS.size()):
			if STYLE_PACKS[i]["name"] == default_style_pack:
				style_pack_index = i
				_apply_style_pack(STYLE_PACKS[i])
				print("[Mood] applied default style pack '%s'"
					% default_style_pack)
				break
		if style_pack_index < 0:
			push_warning("[Mood] default_style_pack '%s' not found in STYLE_PACKS" % default_style_pack)


func _collect_lights(node: Node) -> void:
	if node is DirectionalLight3D:
		_directional_lights.append(node)
		_directional_base_energy.append((node as Light3D).light_energy)
		_directional_base_color.append((node as Light3D).light_color)
		_directional_base_rotation.append((node as Node3D).rotation_degrees)
		# Keep legacy combined array for lightshow_extreme's per-light pulse.
		_scene_lights.append(node)
		_scene_light_base_energy.append((node as Light3D).light_energy)
		_scene_light_base_color.append((node as Light3D).light_color)
	elif node is Light3D:
		_practical_lights.append(node)
		_practical_base_energy.append((node as Light3D).light_energy)
		_practical_base_color.append((node as Light3D).light_color)
		_scene_lights.append(node)
		_scene_light_base_energy.append((node as Light3D).light_energy)
		_scene_light_base_color.append((node as Light3D).light_color)
	elif node is WorldEnvironment:
		_world_env = node as WorldEnvironment
		if _world_env.environment:
			_world_env_base_energy = _world_env.environment.ambient_light_energy
			_world_env_base_color = _world_env.environment.ambient_light_color
			var sky: Sky = _world_env.environment.sky
			if sky and sky.sky_material is ProceduralSkyMaterial:
				_sky_material = sky.sky_material as ProceduralSkyMaterial
	for child in node.get_children():
		_collect_lights(child)


func action_cycle_lighting() -> void:
	lighting_index = (lighting_index + 1) % LIGHTING_PRESETS.size()
	_begin_lighting_transition(LIGHTING_PRESETS[lighting_index])
	_apply(MOODS[current_index])  # refresh HUD label with new lighting tag
	print("[Mood] lighting → %s (transitioning)" % LIGHTING_PRESETS[lighting_index]["name"])


func _begin_lighting_transition(target: Dictionary) -> void:
	# Source = whatever the lights currently look like. For the very
	# first call we snapshot the original scene_default; afterwards we
	# carry forward the previous target so chained transitions stay
	# continuous.
	if _light_lerp_target.is_empty():
		_light_lerp_source = LIGHTING_PRESETS[0]
	else:
		_light_lerp_source = _light_lerp_target
	_light_lerp_target = target
	_light_lerp_t = 0.0


func action_cycle_style_pack() -> void:
	# Cycles -1 (manual) → 0 → 1 → ... → N-1 → back to -1.
	style_pack_index = style_pack_index + 1
	if style_pack_index >= STYLE_PACKS.size():
		style_pack_index = -1
		_apply(MOODS[current_index])  # just refresh label
		print("[Mood] style pack → manual")
		return
	var pack: Dictionary = STYLE_PACKS[style_pack_index]
	_apply_style_pack(pack)
	print("[Mood] style pack → %s (mood=%s, lighting=%s)" % [
		pack["name"], pack["mood"], pack["lighting"]
	])


func _apply_style_pack(pack: Dictionary) -> void:
	var mood_idx: int = _mood_index_by_name(pack["mood"])
	var light_idx: int = _lighting_index_by_name(pack["lighting"])
	if mood_idx >= 0:
		current_index = mood_idx
	if light_idx >= 0:
		lighting_index = light_idx
		_begin_lighting_transition(LIGHTING_PRESETS[lighting_index])
	blend_mode_override = pack.get("blend_mode", -1)
	blend_amount_override = pack.get("blend_amt", -1)
	_apply(MOODS[current_index])


func _mood_index_by_name(name: String) -> int:
	for i in range(MOODS.size()):
		if MOODS[i]["name"] == name:
			return i
	return -1


func _lighting_index_by_name(name: String) -> int:
	for i in range(LIGHTING_PRESETS.size()):
		if LIGHTING_PRESETS[i]["name"] == name:
			return i
	return -1


func _apply_lighting(preset: Dictionary) -> void:
	# Public single-shot apply — snaps to target with no transition.
	# Used at startup so the scene boots in the default lighting and
	# by callers that don't want the lerp.
	_light_lerp_source = preset
	_light_lerp_target = preset
	_light_lerp_t = 1.0
	_apply_lighting_blended(preset, preset, 1.0)


func _apply_lighting_blended(src: Dictionary, dst: Dictionary, t: float) -> void:
	# lightshow_extreme already owns the lights — don't fight it.
	if MOODS[current_index]["name"] == "lightshow_extreme":
		return
	var ts: float = smoothstep(0.0, 1.0, t)   # ease in/out
	var dm: float = lerp(float(src["dir_mult"]), float(dst["dir_mult"]), ts)
	var pm: float = lerp(float(src["practical_mult"]), float(dst["practical_mult"]), ts)
	var tm: float = lerp(float(src["tint_mix"]), float(dst["tint_mix"]), ts)
	var dir_tint: Color = (src["dir_tint"] as Color).lerp(dst["dir_tint"], ts)
	# KEY directional gets the sun rotation; fill/back are left at base
	# rotation so they keep their three-light geometry. The user's
	# scene names the key "Moon_Key" — match by suffix "_Key" when
	# present, else fall back to first directional.
	var key_idx: int = -1
	for i in range(_directional_lights.size()):
		var n: String = String((_directional_lights[i] as Node).name)
		if n.ends_with("_Key") or n.ends_with("Key"):
			key_idx = i
			break
	if key_idx < 0 and _directional_lights.size() > 0:
		key_idx = 0
	# Resolve sun rotation. NAN in either endpoint means "keep base."
	# Otherwise we lerp the pitch/yaw smoothly so the sun arcs.
	var sun_pitch_src: float = src["sun_pitch_deg"]
	var sun_yaw_src: float = src["sun_yaw_deg"]
	var sun_pitch_dst: float = dst["sun_pitch_deg"]
	var sun_yaw_dst: float = dst["sun_yaw_deg"]
	var sun_has_rotation: bool = not (is_nan(sun_pitch_src) or is_nan(sun_pitch_dst))
	var sun_pitch: float = 0.0
	var sun_yaw: float = 0.0
	if sun_has_rotation:
		sun_pitch = lerp(sun_pitch_src, sun_pitch_dst, ts)
		sun_yaw = lerp(sun_yaw_src, sun_yaw_dst, ts)
	for i in range(_directional_lights.size()):
		var light: DirectionalLight3D = _directional_lights[i]
		if light == null:
			continue
		light.light_energy = _directional_base_energy[i] * dm
		light.light_color = _directional_base_color[i].lerp(dir_tint, tm)
		if i == key_idx and sun_has_rotation:
			var r: Vector3 = _directional_base_rotation[i]
			r.x = sun_pitch
			r.y = sun_yaw
			light.rotation_degrees = r
		else:
			light.rotation_degrees = _directional_base_rotation[i]
	for i in range(_practical_lights.size()):
		var p: Light3D = _practical_lights[i]
		if p == null:
			continue
		p.light_energy = _practical_base_energy[i] * pm
		p.light_color = _practical_base_color[i]
	if _world_env and _world_env.environment:
		# Ambient blend. -1 sentinel on either endpoint means "keep
		# the scene's cached base" — used by scene_default. We lerp
		# the resolved values so the cross-fade still works.
		var amb_e_src: float = src["ambient_energy"]
		var amb_e_dst: float = dst["ambient_energy"]
		if amb_e_src < 0.0:
			amb_e_src = _world_env_base_energy
		if amb_e_dst < 0.0:
			amb_e_dst = _world_env_base_energy
		var amb_c_src: Color = src["ambient_color"] if src["ambient_energy"] >= 0.0 else _world_env_base_color
		var amb_c_dst: Color = dst["ambient_color"] if dst["ambient_energy"] >= 0.0 else _world_env_base_color
		_world_env.environment.ambient_light_energy = lerp(amb_e_src, amb_e_dst, ts)
		_world_env.environment.ambient_light_color = amb_c_src.lerp(amb_c_dst, ts)
		# Fog tint follows the sky horizon so haze reads consistently.
		if src.has("fog_color") and dst.has("fog_color"):
			_world_env.environment.fog_light_color = (
				(src["fog_color"] as Color).lerp(dst["fog_color"], ts)
			)
	# Sky cross-fade: ProceduralSkyMaterial colours + energy.
	if _sky_material and src.has("sky_top") and dst.has("sky_top"):
		_sky_material.sky_top_color = (src["sky_top"] as Color).lerp(dst["sky_top"], ts)
		_sky_material.sky_horizon_color = (
			(src["sky_horizon"] as Color).lerp(dst["sky_horizon"], ts)
		)
		_sky_material.sky_energy_multiplier = lerp(
			float(src["sky_energy"]), float(dst["sky_energy"]), ts
		)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_F3:
			action_cycle_mood(1)
		elif event.keycode == KEY_F5:
			action_strobe_shimmer()
		elif event.keycode == KEY_F6:
			action_strobe_rift()
		elif event.keycode == KEY_F9:
			action_cycle_blend_mode()
		elif event.keycode == KEY_F10:
			action_cycle_blend_amount()
		elif event.keycode == KEY_F11:
			action_cycle_lighting()
		elif event.keycode == KEY_F12:
			action_cycle_style_pack()
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
	# ── lighting transition: advance toward target, apply blended values
	if _light_lerp_t < 1.0 and not _light_lerp_target.is_empty():
		_light_lerp_t = min(1.0, _light_lerp_t + delta / LIGHT_LERP_DUR)
		_apply_lighting_blended(_light_lerp_source, _light_lerp_target, _light_lerp_t)

	# ── audio-reactive sampling: exponential-smoothed master bus peak
	# (linear 0..1). Quiet game → ~0; loud music → ~0.8-1.0. Fed to
	# shaders as a uniform so any layer can react.
	var bus_peak_db: float = AudioServer.get_bus_peak_volume_left_db(0, 0)
	var bus_peak_lin: float = db_to_linear(bus_peak_db)
	_audio_level = _audio_level * AUDIO_DECAY + bus_peak_lin * (1.0 - AUDIO_DECAY)

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
		# Just LEFT lightshow_extreme — restore every cached light
		# then re-apply the active lighting preset so the user's F11
		# selection isn't lost when stepping out of the visualizer.
		_apply_lighting(LIGHTING_PRESETS[lighting_index])
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
	# Global shader-strength scaler: when the per-percent tuner is
	# active OR the F10 cycle is set, multiply EVERY shader's
	# strength by the same factor — that way the user gets a single
	# "overall intensity" knob across the whole mood stack.
	var scale: float = 1.0
	if blend_amount_pct >= 0 or blend_amount_override >= 0:
		scale = _blend_scale()
	# VN focus mode — per-param softeners for dialogue readability.
	# vn(key) returns the softening factor for that key, or 1.0 when
	# focus is off / no entry exists.
	var vn := func(key: String) -> float:
		if not _vn_focus_active:
			return 1.0
		return VN_FOCUS_SOFTEN.get(key, 1.0)
	_set_params("NeonQuad", {
		"strength":       _resolved_neon_strength(preset),
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
		"accent_r":       preset.get("neon_accent", Vector3(1.0, 0.0, 0.0)).x,
		"accent_g":       preset.get("neon_accent", Vector3(1.0, 0.0, 0.0)).y,
		"accent_b":       preset.get("neon_accent", Vector3(1.0, 0.0, 0.0)).z,
		"blend_mode":     _resolved_blend_mode(preset),
	})
	_set_params("DirAsciiQuad", {
		"strength":       preset.get("dir_ascii", 0.0) * scale * vn.call("dir_ascii"),
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
		"strength":      preset.get("motion", 0.0) * scale * vn.call("motion"),
		"cell_size":     preset.get("motion_cell", 9.0),
		"line_color":    preset.get("motion_color", Color(1.0, 0.98, 0.92, 1)),
		"trail_strength":preset.get("motion_trail", 0.6),
		"line_density":  preset.get("motion_density", 0.85),
	})
	_set_params("BlurQuad", {
		"strength":  preset.get("blur", 0.0) * scale,
		"blur_mode": preset.get("blur_mode", 0),
		"radius":    preset.get("blur_radius", 4.0),
	})
	_set_params("OldFilmQuad", {
		"strength":          preset.get("oldfilm", 0.0) * scale * vn.call("oldfilm"),
		"sim_fps":           preset.get("oldfilm_fps", 18.0),
		"tint_color":        preset.get("oldfilm_tint", Color(0.96, 0.90, 0.74, 1)),
		"tint_amount":       preset.get("oldfilm_tint_amt", 0.55),
		"grain_strength":    preset.get("oldfilm_grain", 0.18) * vn.call("oldfilm_grain"),
		"flicker_strength":  preset.get("oldfilm_flicker", 0.20),
		"vignette_strength": preset.get("oldfilm_vignette", 0.55),
		"scratch_strength":  preset.get("oldfilm_scratch", 0.10),
		"judder_strength":   preset.get("oldfilm_judder", 0.0) * vn.call("oldfilm_judder"),
	})
	_set_params("StarscapeQuad", {
		"strength":        preset.get("star", 0.0) * scale,
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
		"strength":        preset["ascii"] * scale * vn.call("ascii"),
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
		"scanline_strength":    preset["scanline"]   * vn.call("scanline"),
		"chromatic_aberration": preset["aberration"] * vn.call("aberration"),
	})
	var label: Node = get_node_or_null(mood_label_path)
	if label is Label:
		var prefix: String = ""
		if style_pack_index >= 0:
			prefix = "STYLE · %s (F12)\n" % STYLE_PACKS[style_pack_index]["name"]
		var suffix: String = ""
		if blend_mode_override >= 0:
			suffix += "  · blend=%s (F9)" % BLEND_MODE_NAMES[blend_mode_override + 1]
		if blend_amount_pct >= 0:
			suffix += "  · amt=%d%% (tuner)" % blend_amount_pct
		elif blend_amount_override >= 0:
			suffix += "  · amt=%s (F10)" % BLEND_AMOUNT_LABELS[blend_amount_override + 1]
		if lighting_index > 0:
			suffix += "  · light=%s (F11)" % LIGHTING_PRESETS[lighting_index]["name"]
		(label as Label).text = "%sMOOD · %s   (F3)%s" % [prefix, preset["name"], suffix]


func _resolved_blend_mode(preset: Dictionary) -> int:
	# F9 override wins when set, otherwise the preset's own value.
	if blend_mode_override >= 0:
		return blend_mode_override
	return preset.get("neon_blend_mode", 0)


func _blend_scale() -> float:
	# Resolve the active blend scale. Per-percent (tens/ones tuner)
	# takes priority; then the F10 preset-step override; then 1.0.
	if blend_amount_pct >= 0:
		return float(blend_amount_pct) / 100.0
	if blend_amount_override >= 0:
		return BLEND_AMOUNTS[blend_amount_override]
	return 1.0


func _resolved_neon_strength(preset: Dictionary) -> float:
	# F10 override / per-percent tuner scales the neon layer's
	# strength. The tuner takes priority — see _blend_scale().
	var base: float = preset["neon"]
	if blend_amount_pct < 0 and blend_amount_override < 0:
		return base
	return base * _blend_scale()


func action_cycle_blend_mode() -> void:
	# -1 (preset) → 0 REPLACE → 1 MULTIPLY → 2 OVERLAY → 3 SCREEN → 4 ADD → back to -1
	blend_mode_override = blend_mode_override + 1
	if blend_mode_override > 4:
		blend_mode_override = -1
	_apply(MOODS[current_index])
	var label_name: String = BLEND_MODE_NAMES[blend_mode_override + 1]
	print("[Mood] blend → %s" % label_name)


func action_cycle_blend_amount() -> void:
	# -1 (preset) → 0 full → 1 60% → 2 30% → 3 15% → back to -1
	blend_amount_override = blend_amount_override + 1
	if blend_amount_override >= BLEND_AMOUNTS.size():
		blend_amount_override = -1
	# Discrete cycle disables the per-percent tuner.
	blend_amount_pct = -1
	_apply(MOODS[current_index])
	var label_name: String = BLEND_AMOUNT_LABELS[blend_amount_override + 1]
	print("[Mood] blend amount → %s" % label_name)


# ── Per-percent tuner (two-button incremental adjuster) ──────────
# Both buttons wrap at 100 and disable the F10 discrete-cycle
# override. Starting from -1 ("preset"), pressing either button
# moves to 0% and from there the tens / ones digits bump up.
func action_blend_pct_tens() -> void:
	# Bumps the tens digit by 10. Wraps 90 → 0 (i.e. 90+10 = 100 → 0).
	if blend_amount_pct < 0:
		blend_amount_pct = 0
	var ones: int = blend_amount_pct % 10
	var tens: int = (blend_amount_pct / 10) + 1
	if tens > 10:
		tens = 0
	blend_amount_pct = clamp(tens * 10 + ones, 0, 100)
	blend_amount_override = -1
	_apply(MOODS[current_index])
	print("[Mood] blend %d%%" % blend_amount_pct)


func action_blend_pct_ones() -> void:
	# Bumps the ones digit by 1. Wraps 9 → 0 (the tens digit stays
	# put — this is per-place adjustment, NOT carry-on overflow).
	if blend_amount_pct < 0:
		blend_amount_pct = 0
	var tens: int = blend_amount_pct / 10
	var ones: int = (blend_amount_pct % 10) + 1
	if ones > 9:
		ones = 0
	blend_amount_pct = clamp(tens * 10 + ones, 0, 100)
	blend_amount_override = -1
	_apply(MOODS[current_index])
	print("[Mood] blend %d%%" % blend_amount_pct)


func action_blend_pct_reset() -> void:
	# Clear the per-percent tuner and go back to the mood preset
	# (so visiting different moods uses each one's tuned default).
	blend_amount_pct = -1
	blend_amount_override = -1
	_apply(MOODS[current_index])
	print("[Mood] blend → preset")


func get_blend_pct_label() -> String:
	# Used by the HUD MoodLabel so it can show the active tuner state.
	if blend_amount_pct >= 0:
		return "%d%%" % blend_amount_pct
	if blend_amount_override >= 0:
		return BLEND_AMOUNT_LABELS[blend_amount_override + 1]
	return "preset"


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


# ── VN focus mode toggle ────────────────────────────────────────
# GameEngine calls this on say/think (true) and narrate (false).
# A scene without a VN layer never calls it; the default false
# state leaves _apply behaviour identical to pre-Phase-3.
func vn_focus_dialogue(active: bool) -> void:
	if _vn_focus_active == active:
		return
	_vn_focus_active = active
	# Re-apply the current preset so the softeners take effect
	# (or restore to full when releasing).
	_apply(MOODS[current_index])
