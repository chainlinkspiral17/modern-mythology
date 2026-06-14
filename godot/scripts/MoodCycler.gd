# MoodCycler.gd
# ════════════════════════════════════════════════════════════════
# Cycles the post-process moods. F3 advances to the next preset.
#
# Drives the screen post-process stack (in render order):
#   NeonQuad   · neon_edge — Sobel silhouette outliner. Edges painted
#                in a hot accent color, fills painted with a vertical
#                gradient (synthwave / chillwave / noir styling).
#   AsciiQuad  · ascii_render — sample-per-cell ASCII renderer. The
#                scene becomes printed code.
#   Quad       · demoscene_post — palette quantize, dither, scanlines,
#                chromatic aberration.
#
# Moods range from raw scene through naturalistic time-of-day variants
# to fully stylized substrate states. Each mood can use any subset of
# the three layers.
# ════════════════════════════════════════════════════════════════

extends CanvasLayer

const MOODS: Array = [
    {
        "name": "lunch",
        "palette": 16.0, "dither": 0.08, "scanline": 0.20, "aberration": 0.0008,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85,
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 0.22, 0.78, 1),
        "neon_low": Color(0.42, 0.12, 0.50, 1), "neon_high": Color(0.10, 0.05, 0.25, 1), "neon_grad": 1.0,
    },
    {
        "name": "dusk",
        "palette": 12.0, "dither": 0.16, "scanline": 0.32, "aberration": 0.0014,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85,
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 0.22, 0.78, 1),
        "neon_low": Color(0.42, 0.12, 0.50, 1), "neon_high": Color(0.10, 0.05, 0.25, 1), "neon_grad": 1.0,
    },
    {
        "name": "chillwave",
        "palette": 8.0, "dither": 0.20, "scanline": 0.40, "aberration": 0.0024,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85,
        "neon": 1.0, "neon_thresh": 0.08, "neon_edge": Color(1.0, 0.22, 0.78, 1),    # hot pink
        "neon_low": Color(0.50, 0.10, 0.55, 1),     # dusk magenta
        "neon_high": Color(0.08, 0.03, 0.22, 1),    # deep purple
        "neon_grad": 1.0,
    },
    {
        "name": "sunset",
        "palette": 10.0, "dither": 0.18, "scanline": 0.30, "aberration": 0.0020,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85,
        "neon": 1.0, "neon_thresh": 0.09, "neon_edge": Color(1.0, 0.80, 0.30, 1),    # gold edges
        "neon_low": Color(0.85, 0.32, 0.22, 1),     # warm orange
        "neon_high": Color(0.22, 0.08, 0.30, 1),    # twilight purple
        "neon_grad": 1.0, "neon_blend": 0.15,
    },
    {
        # The exact reference look from the vol5 D'Ambrosio's exterior
        # concept: pure-black backgrounds, saturated red edges (booth
        # red / hull-trim red), warm yellow lit windows and lamps
        # bleed through via scene_blend. Limited-palette illustrated
        # / lithograph aesthetic.
        "name": "lithograph",
        "palette": 6.0, "dither": 0.20, "scanline": 0.50, "aberration": 0.0014,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85,
        "neon": 1.0, "neon_thresh": 0.06,
        "neon_edge": Color(0.92, 0.22, 0.20, 1),   # warm hull/booth red
        "neon_low":  Color(0.04, 0.03, 0.03, 1),   # near-black
        "neon_high": Color(0.0,  0.0,  0.0,  1),   # pure black
        "neon_grad": 0.3, "neon_blend": 0.55,      # warmth bleeds through
    },
    {
        "name": "noir",
        "palette": 4.0, "dither": 0.30, "scanline": 0.55, "aberration": 0.0010,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85,
        "neon": 1.0, "neon_thresh": 0.10, "neon_edge": Color(1.0, 0.98, 0.92, 1),    # bone-white edges
        "neon_low": Color(0.04, 0.04, 0.04, 1),
        "neon_high": Color(0.0, 0.0, 0.0, 1),
        "neon_grad": 0.4,
    },
    {
        "name": "ice",
        "palette": 8.0, "dither": 0.22, "scanline": 0.35, "aberration": 0.0018,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85,
        "neon": 1.0, "neon_thresh": 0.09, "neon_edge": Color(0.62, 0.92, 1.0, 1),    # pale cyan
        "neon_low": Color(0.10, 0.18, 0.32, 1),
        "neon_high": Color(0.02, 0.04, 0.10, 1),
        "neon_grad": 1.0,
    },
    {
        "name": "night",
        "palette": 10.0, "dither": 0.22, "scanline": 0.45, "aberration": 0.0020,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85,
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 0.22, 0.78, 1),
        "neon_low": Color(0.42, 0.12, 0.50, 1), "neon_high": Color(0.10, 0.05, 0.25, 1), "neon_grad": 1.0,
    },
    {
        "name": "3_47_am",
        "palette":  9.0, "dither": 0.28, "scanline": 0.55, "aberration": 0.0024,
        "ascii": 0.45, "ascii_cell": 9.0, "ascii_gamma": 0.85,
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 0.22, 0.78, 1),
        "neon_low": Color(0.42, 0.12, 0.50, 1), "neon_high": Color(0.10, 0.05, 0.25, 1), "neon_grad": 1.0,
    },
    {
        "name": "precipice",
        "palette":  6.0, "dither": 0.42, "scanline": 0.68, "aberration": 0.0030,
        "ascii": 0.80, "ascii_cell": 8.0, "ascii_gamma": 0.80,
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 0.22, 0.78, 1),
        "neon_low": Color(0.42, 0.12, 0.50, 1), "neon_high": Color(0.10, 0.05, 0.25, 1), "neon_grad": 1.0,
    },
    {
        "name": "substrate",
        "palette":  4.0, "dither": 0.55, "scanline": 0.80, "aberration": 0.0035,
        "ascii": 1.00, "ascii_cell": 8.0, "ascii_gamma": 0.75,
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 0.22, 0.78, 1),
        "neon_low": Color(0.42, 0.12, 0.50, 1), "neon_high": Color(0.10, 0.05, 0.25, 1), "neon_grad": 1.0,
    },
    {
        "name": "raw",
        "palette": 32.0, "dither": 0.00, "scanline": 0.00, "aberration": 0.0000,
        "ascii": 0.00, "ascii_cell": 10.0, "ascii_gamma": 1.0,
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 0.22, 0.78, 1),
        "neon_low": Color(0.42, 0.12, 0.50, 1), "neon_high": Color(0.10, 0.05, 0.25, 1), "neon_grad": 1.0,
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
    _set_params("NeonQuad", {
        "strength":       preset["neon"],
        "edge_threshold": preset["neon_thresh"],
        "edge_color":     preset["neon_edge"],
        "fill_low":       preset["neon_low"],
        "fill_high":      preset["neon_high"],
        "fill_gradient":  preset["neon_grad"],
        "scene_blend":    preset.get("neon_blend", 0.0),
    })
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
