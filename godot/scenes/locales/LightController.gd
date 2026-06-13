# LightController.gd
# ════════════════════════════════════════════════════════════════
# COMMUNITY PLANNED · per-locale mood controller.
#
# Attach to the root Node3D of a locale scene. Manages the named
# light-setup groups under the LightSetups child node, plus the
# demoscene_post shader uniforms on the PostProcess overlay.
#
# A "mood" is a named pairing of:
#   - which Light3D group is visible/active
#   - what post-process uniforms to apply
#
# Call set_mood("3:47_am") from any scene script. The transitions
# are instant by default; tween_to_mood() animates over 1-2s.
# ════════════════════════════════════════════════════════════════

extends Node3D

@export var initial_mood: String = "lunch"

# Standard mood presets · per-mood (palette · dither · scanline · aberration · ascii)
var MOOD_PRESETS: Dictionary = {
    "lunch":          { "palette": 16.0, "dither": 0.00, "scanline": 0.05, "aberration": 0.0008, "ascii": 0.00 },
    "dawn":           { "palette": 14.0, "dither": 0.10, "scanline": 0.20, "aberration": 0.0012, "ascii": 0.00 },
    "dusk":           { "palette": 12.0, "dither": 0.15, "scanline": 0.30, "aberration": 0.0015, "ascii": 0.00 },
    "night":          { "palette": 10.0, "dither": 0.20, "scanline": 0.40, "aberration": 0.0018, "ascii": 0.00 },
    "3_47_am":        { "palette": 10.0, "dither": 0.25, "scanline": 0.50, "aberration": 0.0020, "ascii": 0.30 },
    "precipice":      { "palette":  6.0, "dither": 0.45, "scanline": 0.70, "aberration": 0.0030, "ascii": 0.60 },
    "substrate":      { "palette":  4.0, "dither": 0.60, "scanline": 0.80, "aberration": 0.0035, "ascii": 1.00 },
    "flashback":      { "palette":  8.0, "dither": 0.10, "scanline": 0.15, "aberration": 0.0010, "ascii": 0.00 },
}

var current_mood: String = ""


func _ready() -> void:
    set_mood(initial_mood)


func set_mood(mood: String) -> void:
    if not MOOD_PRESETS.has(mood):
        push_warning("LightController: unknown mood '%s' — falling back to 'lunch'" % mood)
        mood = "lunch"
    current_mood = mood

    _apply_light_group(mood)
    _apply_post_process(MOOD_PRESETS[mood])


func _apply_light_group(mood: String) -> void:
    # The scene's LightSetups child has one Node3D per mood, each
    # containing the Light3D nodes for that mood. Show only the
    # matching group; hide the rest.
    var setups: Node = get_node_or_null("LightSetups")
    if setups == null:
        return
    for child in setups.get_children():
        if child is Node3D:
            (child as Node3D).visible = (child.name == mood)


func _apply_post_process(preset: Dictionary) -> void:
    # The scene's PostProcess child is a CanvasLayer with a ColorRect
    # whose material is a ShaderMaterial bound to demoscene_post.gdshader.
    var post: Node = get_node_or_null("PostProcess/Quad")
    if post == null:
        return
    var mat: Material = (post as CanvasItem).material
    if mat is ShaderMaterial:
        var sm: ShaderMaterial = mat as ShaderMaterial
        sm.set_shader_parameter("palette_size", preset["palette"])
        sm.set_shader_parameter("dither_strength", preset["dither"])
        sm.set_shader_parameter("scanline_strength", preset["scanline"])
        sm.set_shader_parameter("chromatic_aberration", preset["aberration"])
        sm.set_shader_parameter("ascii_strength", preset["ascii"])


func tween_to_mood(mood: String, duration: float = 1.5) -> void:
    if not MOOD_PRESETS.has(mood):
        push_warning("LightController: unknown mood '%s'" % mood)
        return
    current_mood = mood
    _apply_light_group(mood)   # light switching is still instant; tweening lights is per-scene

    var post: Node = get_node_or_null("PostProcess/Quad")
    if post == null:
        return
    var mat: Material = (post as CanvasItem).material
    if not (mat is ShaderMaterial):
        return
    var sm: ShaderMaterial = mat as ShaderMaterial
    var preset: Dictionary = MOOD_PRESETS[mood]
    var tween: Tween = create_tween().set_parallel(true)
    for key in preset.keys():
        var uniform_name: String = key if key != "palette" else "palette_size"
        if key == "palette": uniform_name = "palette_size"
        elif key == "dither": uniform_name = "dither_strength"
        elif key == "scanline": uniform_name = "scanline_strength"
        elif key == "aberration": uniform_name = "chromatic_aberration"
        elif key == "ascii": uniform_name = "ascii_strength"
        var current_val: float = sm.get_shader_parameter(uniform_name)
        tween.tween_method(
            func(v: float) -> void: sm.set_shader_parameter(uniform_name, v),
            current_val,
            preset[key],
            duration
        )
