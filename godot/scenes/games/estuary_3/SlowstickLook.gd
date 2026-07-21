extends RefCounted
class_name SlowstickLook
## The Slowstick look layer · one call per host.
##
## The slowsticks are tech from an alternate universe.  They never
## had our timeline's hardware limits, so they must never cosplay
## them: no hand-drawn scanline ColorRects, no phosphor-mono
## "authenticity."  Instead every slowstick renders MODERN and
## passes through the same post-process language TAROT GAUNTLET and
## COMMUNITY PLANNED use — demoscene_post.gdshader — tuned to a
## per-studio preset.  Palette discipline stays (it is each
## studio's house STYLE, not a limitation); the rendering is
## smooth, full-res, Steam Deck native.
##
## Usage (host _ready, after add_to_group):
##   SlowstickLook.apply(self, "oneironautics")
##
## The layer joins the "world_render" group per the F4 rule's
## escape hatch — it is the picture, not HUD.

const SHADER_PATH := "res://assets/shaders/demoscene_post.gdshader"

# Per-studio look presets · the fictional design cultures.
# Values are demoscene_post uniforms.  Subtle on purpose · the
# treatment should read as material, not as filter.
const PRESETS: Dictionary = {
	# Oneironautics · Portland · soft field-guide gouache · gentle
	# grain like paper tooth, barely-there line cadence
	"oneironautics": {
		"look_mode": 1, "grain_amount": 0.6, "paper_tint": Color(0.92, 0.88, 0.76),
		"palette_size": 24.0, "dither_strength": 0.10,
		"scanline_strength": 0.06, "chromatic_aberration": 0.0008,
		"ascii_strength": 0.0
	},
	# Fey Faire · Rocha 1990 · hand-inked cel over cream stock ·
	# slightly deeper quantize so the mauves band like silkscreen
	"rocha_faire": {
		"look_mode": 2,
		"palette_size": 20.0, "dither_strength": 0.14,
		"scanline_strength": 0.05, "chromatic_aberration": 0.0012,
		"ascii_strength": 0.0
	},
	# Astro-Cortex · Culver City · precision-instrument glass ·
	# deeper palette crush, a breath of aberration at the edges ·
	# the closest any slowstick gets to feeling like a machine
	"astro_cortex": {
		"look_mode": 3, "ink_amount": 0.5,
		"palette_size": 14.0, "dither_strength": 0.22,
		"scanline_strength": 0.10, "chromatic_aberration": 0.0018,
		"ascii_strength": 0.0
	},
	# PDP Toys · Beaverton · injection-molded toy-bright · white
	# background, primary colors, no grain worth mentioning · a
	# children's product photographed in a catalog
	"pdp_toys": {
		"look_mode": 0,
		"palette_size": 32.0, "dither_strength": 0.03,
		"scanline_strength": 0.0, "chromatic_aberration": 0.0006,
		"ascii_strength": 0.0
	},
	# RANCH · San Francisco · laminate-and-signage commercial
	# graphics · nearly clean · the crispest image in the catalog
	"ranch": {
		"look_mode": 0,
		"palette_size": 28.0, "dither_strength": 0.05,
		"scanline_strength": 0.0, "chromatic_aberration": 0.0004,
		"ascii_strength": 0.0
	},
	# Meridian Heritage Interactive · New Portland Arcology · 2048
	# heritage-product rendering · perfectly, wrongly clean — no
	# grain, no quantize, no texture at all. The sterility IS the
	# period look; the wrongness is the point.
	"meridian": {
		"look_mode": 0,
		"palette_size": 48.0, "dither_strength": 0.0,
		"scanline_strength": 0.0, "chromatic_aberration": 0.0,
		"ascii_strength": 0.0
	},
	# Sagebrush Engineworks · Amarillo · pulp-paperback cover inks ·
	# warm dust field, heavy linework, one violet held in reserve
	"sagebrush": {
		"look_mode": 3, "ink_amount": 0.8, "paper_tint": Color(0.90, 0.82, 0.66),
		"palette_size": 22.0, "dither_strength": 0.12,
		"scanline_strength": 0.0, "chromatic_aberration": 0.0010,
		"ascii_strength": 0.0
	},
	# Yumemi Denshi · Kyoto · inked line on paper tones · a hanging
	# scroll's patience · the gentlest treatment in the catalog
	"yumemi": {
		"look_mode": 1, "grain_amount": 0.4, "paper_tint": Color(0.90, 0.90, 0.82),
		"palette_size": 26.0, "dither_strength": 0.06,
		"scanline_strength": 0.0, "chromatic_aberration": 0.0006,
		"ascii_strength": 0.0
	},
	# No-publisher homebrew (Sweetgum) · one ink, one duplicator ·
	# dialed to near-nothing · the crudeness is in the DRAWING,
	# not the display
	"homebrew": {
		"look_mode": 4, "grain_amount": 0.7,
		"palette_size": 30.0, "dither_strength": 0.04,
		"scanline_strength": 0.0, "chromatic_aberration": 0.0,
		"ascii_strength": 0.0
	},
	# The shelf itself · Olaf's cabin · warm neutral
	"shelf": {
		"look_mode": 1, "grain_amount": 0.5, "paper_tint": Color(0.92, 0.88, 0.76),
		"palette_size": 24.0, "dither_strength": 0.08,
		"scanline_strength": 0.04, "chromatic_aberration": 0.0008,
		"ascii_strength": 0.0
	}
}


static func apply(host: Node, preset_name: String) -> CanvasLayer:
	var preset: Dictionary = PRESETS.get(preset_name, PRESETS["oneironautics"])
	var layer := CanvasLayer.new()
	layer.name = "SlowstickLook"
	layer.layer = 80
	layer.add_to_group("world_render")

	# Nested boot support: Pirate Summer's console launches a host
	# inside a layer-90 CanvasLayer.  CanvasLayer.layer is global
	# (nesting does not compose), so a layer-80 look under there
	# would shade the CAMP and leave the nested game untreated.
	# Render above the enclosing layer instead.
	var anc: Node = host.get_parent()
	while anc != null:
		if anc is CanvasLayer:
			layer.layer = maxi(layer.layer, (anc as CanvasLayer).layer + 5)
			break
		anc = anc.get_parent()

	var rect := ColorRect.new()
	rect.name = "LookRect"
	rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	# The picture must never eat input.
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE

	var shader: Shader = load(SHADER_PATH)
	if shader != null:
		var mat := ShaderMaterial.new()
		mat.shader = shader
		for k in preset.keys():
			mat.set_shader_parameter(String(k), preset[k])
		rect.material = mat

	layer.add_child(rect)
	host.add_child(layer)
	# CanvasLayer ignores its parent Control's `visible` — a hidden
	# shelf would keep post-processing whatever plays over it, and
	# two look layers would stack. Track the host's visibility.
	if host is CanvasItem:
		layer.visible = (host as CanvasItem).visible
		(host as CanvasItem).visibility_changed.connect(func() -> void:
			if is_instance_valid(layer):
				layer.visible = (host as CanvasItem).visible)
	return layer
