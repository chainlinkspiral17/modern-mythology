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
		"palette_size": 24.0, "dither_strength": 0.10,
		"scanline_strength": 0.06, "chromatic_aberration": 0.0008,
		"ascii_strength": 0.0
	},
	# Fey Faire · Rocha 1990 · hand-inked cel over cream stock ·
	# slightly deeper quantize so the mauves band like silkscreen
	"rocha_faire": {
		"palette_size": 20.0, "dither_strength": 0.14,
		"scanline_strength": 0.05, "chromatic_aberration": 0.0012,
		"ascii_strength": 0.0
	},
	# Astro-Cortex · Culver City · precision-instrument glass ·
	# deeper palette crush, a breath of aberration at the edges ·
	# the closest any slowstick gets to feeling like a machine
	"astro_cortex": {
		"palette_size": 14.0, "dither_strength": 0.22,
		"scanline_strength": 0.10, "chromatic_aberration": 0.0018,
		"ascii_strength": 0.0
	},
	# RANCH · San Francisco · laminate-and-signage commercial
	# graphics · nearly clean · the crispest image in the catalog
	"ranch": {
		"palette_size": 28.0, "dither_strength": 0.05,
		"scanline_strength": 0.0, "chromatic_aberration": 0.0004,
		"ascii_strength": 0.0
	},
	# The shelf itself · Olaf's cabin · warm neutral
	"shelf": {
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
	return layer
