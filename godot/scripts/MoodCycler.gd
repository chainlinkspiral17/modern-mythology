# MoodCycler.gd
# ════════════════════════════════════════════════════════════════
# Attach to the PostProcess CanvasLayer. Cycles through the
# demoscene_post shader's mood presets when F3 is pressed.
#
# Lets you see how the warehouse looks under each named mood —
# lunch / dusk / night / 3:47 AM / precipice / substrate.
# ════════════════════════════════════════════════════════════════

extends CanvasLayer

const MOODS: Array = [
    { "name": "lunch",      "palette": 16.0, "dither": 0.10, "scanline": 0.25, "aberration": 0.0012, "ascii": 0.00 },
    { "name": "dusk",       "palette": 12.0, "dither": 0.18, "scanline": 0.35, "aberration": 0.0018, "ascii": 0.00 },
    { "name": "night",      "palette": 10.0, "dither": 0.22, "scanline": 0.45, "aberration": 0.0020, "ascii": 0.05 },
    { "name": "3_47_am",    "palette":  9.0, "dither": 0.28, "scanline": 0.55, "aberration": 0.0024, "ascii": 0.30 },
    { "name": "precipice",  "palette":  6.0, "dither": 0.45, "scanline": 0.70, "aberration": 0.0030, "ascii": 0.60 },
    { "name": "substrate",  "palette":  4.0, "dither": 0.60, "scanline": 0.80, "aberration": 0.0035, "ascii": 1.00 },
    { "name": "raw",        "palette": 32.0, "dither": 0.00, "scanline": 0.00, "aberration": 0.0000, "ascii": 0.00 },
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
    var quad: Node = get_node_or_null("Quad")
    if quad == null or not (quad is CanvasItem):
        return
    var mat: Material = (quad as CanvasItem).material
    if not (mat is ShaderMaterial):
        return
    var sm: ShaderMaterial = mat as ShaderMaterial
    sm.set_shader_parameter("palette_size", preset["palette"])
    sm.set_shader_parameter("dither_strength", preset["dither"])
    sm.set_shader_parameter("scanline_strength", preset["scanline"])
    sm.set_shader_parameter("chromatic_aberration", preset["aberration"])
    sm.set_shader_parameter("ascii_strength", preset["ascii"])
