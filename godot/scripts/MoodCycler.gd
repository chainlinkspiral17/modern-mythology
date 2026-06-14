# MoodCycler.gd
# ════════════════════════════════════════════════════════════════
# Cycles the post-process moods. F3 advances to the next preset.
#
# Drives the screen post-process stack:
#   AsciiQuad · ascii_render — full-screen ASCII renderer. The whole
#               scene gets sampled per-cell and each cell becomes a
#               glyph chosen by luminance. strength=0 passes the
#               scene through, strength=1 renders entirely as code.
#   Quad      · demoscene_post — palette quantize, Bayer dither,
#               scanlines, chromatic aberration. Stylization on top
#               of whatever the ASCII pass produced.
#
# Each mood is a state of how loud the substrate is. Lunch is the
# raw world. Substrate is the world rendered ENTIRELY as code.
# ════════════════════════════════════════════════════════════════

extends CanvasLayer

const MOODS: Array = [
    {
        "name": "lunch",
        "palette": 16.0, "dither": 0.08, "scanline": 0.20,
        "aberration": 0.0008, "ascii_post": 0.0,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85,
    },
    {
        "name": "dusk",
        "palette": 12.0, "dither": 0.16, "scanline": 0.32,
        "aberration": 0.0014, "ascii_post": 0.0,
        "ascii": 0.12, "ascii_cell": 10.0, "ascii_gamma": 0.85,
    },
    {
        "name": "night",
        "palette": 10.0, "dither": 0.22, "scanline": 0.45,
        "aberration": 0.0020, "ascii_post": 0.0,
        "ascii": 0.25, "ascii_cell": 10.0, "ascii_gamma": 0.85,
    },
    {
        "name": "3_47_am",
        "palette":  9.0, "dither": 0.28, "scanline": 0.55,
        "aberration": 0.0024, "ascii_post": 0.0,
        "ascii": 0.50, "ascii_cell": 9.0, "ascii_gamma": 0.85,
    },
    {
        "name": "precipice",
        "palette":  6.0, "dither": 0.42, "scanline": 0.68,
        "aberration": 0.0030, "ascii_post": 0.0,
        "ascii": 0.80, "ascii_cell": 8.0, "ascii_gamma": 0.80,
    },
    {
        "name": "substrate",
        "palette":  4.0, "dither": 0.55, "scanline": 0.80,
        "aberration": 0.0035, "ascii_post": 0.0,
        "ascii": 1.00, "ascii_cell": 8.0, "ascii_gamma": 0.75,
    },
    {
        "name": "raw",
        "palette": 32.0, "dither": 0.00, "scanline": 0.00,
        "aberration": 0.0000, "ascii_post": 0.0,
        "ascii": 0.00, "ascii_cell": 10.0, "ascii_gamma": 1.0,
    },
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
    _set_params("AsciiQuad", {
        "strength":  preset["ascii"],
        "cell_size": preset["ascii_cell"],
        "gamma":     preset["ascii_gamma"],
    })
    _set_params("Quad", {
        "palette_size":         preset["palette"],
        "dither_strength":      preset["dither"],
        "scanline_strength":    preset["scanline"],
        "chromatic_aberration": preset["aberration"],
        "ascii_strength":       preset["ascii_post"],
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
