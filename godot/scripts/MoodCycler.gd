# MoodCycler.gd
# ════════════════════════════════════════════════════════════════
# Attach to the PostProcess CanvasLayer. Cycles through the
# demoscene post stack's mood presets when F3 is pressed.
#
# Drives THREE shader layers in order:
#   Quad       · demoscene_post (palette / dither / scanlines /
#                 chromatic aberration / ascii blocks)
#   EdgeQuad   · ascii_edges (depth-edge detection painted with
#                 scrolling ASCII glyphs — "the chassis breathes")
#   GlyphQuad  · glyph_field (drifting ASCII glyph overlay across
#                 the whole frame, luma-biased — "substrate hum")
#
# Each preset names a state of the substrate's audibility:
#   lunch / dusk / night — substrate quiet, mostly invisible
#   3:47 AM — substrate audible
#   precipice — substrate loud
#   substrate — full bleed-through
#   raw — debug, no post-process
# ════════════════════════════════════════════════════════════════

extends CanvasLayer

const MOODS: Array = [
    { "name": "lunch",     "palette": 16.0, "dither": 0.10, "scanline": 0.25, "aberration": 0.0012, "ascii": 0.00, "edge": 0.00, "glyph": 0.00 },
    { "name": "dusk",      "palette": 12.0, "dither": 0.18, "scanline": 0.35, "aberration": 0.0018, "ascii": 0.00, "edge": 0.05, "glyph": 0.00 },
    { "name": "night",     "palette": 10.0, "dither": 0.22, "scanline": 0.45, "aberration": 0.0020, "ascii": 0.05, "edge": 0.15, "glyph": 0.05 },
    { "name": "3_47_am",   "palette":  9.0, "dither": 0.28, "scanline": 0.55, "aberration": 0.0024, "ascii": 0.30, "edge": 0.35, "glyph": 0.18 },
    { "name": "precipice", "palette":  6.0, "dither": 0.45, "scanline": 0.70, "aberration": 0.0030, "ascii": 0.60, "edge": 0.60, "glyph": 0.35 },
    { "name": "substrate", "palette":  4.0, "dither": 0.60, "scanline": 0.80, "aberration": 0.0035, "ascii": 1.00, "edge": 0.85, "glyph": 0.55 },
    { "name": "raw",       "palette": 32.0, "dither": 0.00, "scanline": 0.00, "aberration": 0.0000, "ascii": 0.00, "edge": 0.00, "glyph": 0.00 },
]

var current_index: int = 0


func _ready() -> void:
    _apply(MOODS[current_index])
    print("[Mood] %s · F3 to cycle" % MOODS[current_index]["name"])


func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_F3:
            current_index = (current_index + 1) % MOODS.size()
            _apply(MOODS[current_index])
            print("[Mood] → %s" % MOODS[current_index]["name"])


func _apply(preset: Dictionary) -> void:
    _set_params("Quad", {
        "palette_size":         preset["palette"],
        "dither_strength":      preset["dither"],
        "scanline_strength":    preset["scanline"],
        "chromatic_aberration": preset["aberration"],
        "ascii_strength":       preset["ascii"],
    })
    _set_params("EdgeQuad", {
        "edge_strength": preset["edge"],
    })
    _set_params("GlyphQuad", {
        "glyph_alpha": preset["glyph"],
    })


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
