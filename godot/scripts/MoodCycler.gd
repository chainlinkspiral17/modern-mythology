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
        "palette": 4.0, "dither": 0.04, "scanline": 0.20, "aberration": 0.0004,
        "ascii": 0.0, "ascii_cell": 10.0, "ascii_gamma": 0.85, "ascii_tint": true,
        "ascii_fg": Color(0.92, 0.78, 0.45, 1), "ascii_bg": Color(0.05, 0.04, 0.02, 1),
        "neon": 0.0, "neon_thresh": 0.10, "neon_edge": Color(1, 0.22, 0.78, 1),
        "neon_low": Color(0.42, 0.12, 0.50, 1), "neon_high": Color(0.10, 0.05, 0.25, 1),
        "neon_grad": 1.0, "neon_blend": 0.0, "neon_glow": 0.4,
        "dir_ascii": 1.0, "dir_cell": 10.0, "dir_thresh": 0.06,
        "dir_line": Color(0.95, 0.16, 0.14, 1),
        "dir_fill": Color(0.0, 0.0, 0.0, 1),
        "dir_tint": false,
        "dir_input_scale": 0.6,
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

var current_index: int = 0
# Optional in-game label that displays the current mood name. If the
# scene's HUD doesn't provide one we just skip updating it.
@export var mood_label_path: NodePath = NodePath("../HUD/MoodLabel")


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
        "edge_glow":      preset.get("neon_glow", 0.4),
    })
    _set_params("DirAsciiQuad", {
        "strength":       preset.get("dir_ascii", 0.0),
        "cell_size":      preset.get("dir_cell", 10.0),
        "edge_threshold": preset.get("dir_thresh", 0.10),
        "line_color":     preset.get("dir_line", Color(0.92, 0.20, 0.20, 1)),
        "fill_color":     preset.get("dir_fill", Color(0.02, 0.02, 0.03, 1)),
        "tint_from_scene": preset.get("dir_tint", false),
        "input_scale":    preset.get("dir_input_scale", 1.0),
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
