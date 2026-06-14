# DebugMenu.gd
# ════════════════════════════════════════════════════════════════
# Mouse-only debug menu. Appears whenever the mouse is released
# (Input.MOUSE_MODE_VISIBLE — toggle with ESC). Replicates every
# F-key command as a clickable button so the keyboard isn't needed
# during controller / gamepad testing.
#
# Buttons call public action_*() methods on FPC and MoodCycler
# directly — no synthetic input event injection. The F-key handlers
# in those scripts ALSO call the same methods, so keyboard + mouse
# paths stay in sync without duplicate logic.
#
# Built as a PanelContainer with a visible background + header so
# the menu reads clearly against the dark 3D scene underneath.
# ════════════════════════════════════════════════════════════════
extends PanelContainer

@export var fpc_path: NodePath = NodePath("../../Player")
@export var mood_path: NodePath = NodePath("../../PostProcess")

var _fpc: Node = null
var _mood: Node = null


func _ready() -> void:
    _fpc = get_node_or_null(fpc_path)
    _mood = get_node_or_null(mood_path)

    # Background tint so the menu is unmissable against the scene.
    var style := StyleBoxFlat.new()
    style.bg_color = Color(0.06, 0.05, 0.07, 0.92)
    style.border_color = Color(0.95, 0.78, 0.36, 1.0)
    style.border_width_left = 2
    style.border_width_right = 2
    style.border_width_top = 2
    style.border_width_bottom = 2
    style.content_margin_left = 12.0
    style.content_margin_right = 12.0
    style.content_margin_top = 10.0
    style.content_margin_bottom = 10.0
    add_theme_stylebox_override("panel", style)

    var vb := VBoxContainer.new()
    vb.add_theme_constant_override("separation", 6)
    add_child(vb)

    # Header so the player IMMEDIATELY clocks what they're looking at.
    var header := Label.new()
    header.text = "DEBUG MENU · click to fire"
    header.add_theme_font_size_override("font_size", 18)
    header.add_theme_color_override("font_color", Color(1.0, 0.86, 0.42, 1.0))
    vb.add_child(header)

    var sub := Label.new()
    sub.text = "Mouse-release mode (ESC to toggle)"
    sub.add_theme_font_size_override("font_size", 12)
    sub.add_theme_color_override("font_color", Color(0.85, 0.78, 0.62, 1.0))
    vb.add_child(sub)

    var spacer := Control.new()
    spacer.custom_minimum_size = Vector2(0, 8)
    vb.add_child(spacer)

    _add_btn(vb, "F1 · Toggle Collision",   Callable(self, "_btn_collide"))
    _add_btn(vb, "F2 · Teleport (0,3,0)",   Callable(self, "_btn_teleport"))
    _add_btn(vb, "F3 · Cycle Mood →",       Callable(self, "_btn_mood_next"))
    _add_btn(vb, "←  Cycle Mood (prev)",    Callable(self, "_btn_mood_prev"))
    _add_btn(vb, "F4 · Toggle HUD",         Callable(self, "_btn_hud"))
    _add_btn(vb, "F5 · Shimmer Strobe",     Callable(self, "_btn_shimmer"))
    _add_btn(vb, "F6 · Rift Strobe",        Callable(self, "_btn_rift"))
    _add_btn(vb, "Capture Mouse (resume)",  Callable(self, "_btn_capture"))


func _process(_delta: float) -> void:
    # Only show when the mouse is released. Hidden during normal
    # gameplay so it doesn't get in the way.
    visible = Input.mouse_mode == Input.MOUSE_MODE_VISIBLE


func _add_btn(parent: Container, label: String, on_pressed: Callable) -> void:
    var b := Button.new()
    b.text = label
    b.focus_mode = Control.FOCUS_NONE
    b.add_theme_font_size_override("font_size", 14)
    b.custom_minimum_size = Vector2(240, 32)
    b.pressed.connect(on_pressed)
    parent.add_child(b)


# ── Button handlers ──────────────────────────────────────────────
func _btn_collide() -> void:
    if _fpc and _fpc.has_method("action_toggle_collide"):
        _fpc.action_toggle_collide()

func _btn_teleport() -> void:
    if _fpc and _fpc.has_method("action_teleport_origin"):
        _fpc.action_teleport_origin()

func _btn_mood_next() -> void:
    if _mood and _mood.has_method("action_cycle_mood"):
        _mood.action_cycle_mood(1)

func _btn_mood_prev() -> void:
    if _mood and _mood.has_method("action_cycle_mood"):
        _mood.action_cycle_mood(-1)

func _btn_hud() -> void:
    if _fpc and _fpc.has_method("action_toggle_hud"):
        _fpc.action_toggle_hud()

func _btn_shimmer() -> void:
    if _mood and _mood.has_method("action_strobe_shimmer"):
        _mood.action_strobe_shimmer()

func _btn_rift() -> void:
    if _mood and _mood.has_method("action_strobe_rift"):
        _mood.action_strobe_rift()

func _btn_capture() -> void:
    if _fpc and _fpc.has_method("action_mouse_capture"):
        _fpc.action_mouse_capture()
