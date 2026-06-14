# DebugMenu.gd
# ════════════════════════════════════════════════════════════════
# Mouse-only debug menu. Visible whenever the mouse is released
# (Input.MOUSE_MODE_VISIBLE — toggle with ESC). Replicates every
# F-key command as a clickable button so the keyboard isn't needed
# during controller / gamepad testing.
#
# Buttons call public action_*() methods on FPC and MoodCycler
# directly — no synthetic input event injection. The F-key handlers
# in those scripts ALSO call the same methods, so keyboard + mouse
# stay in sync without duplicate logic.
# ════════════════════════════════════════════════════════════════
extends VBoxContainer

@export var fpc_path: NodePath = NodePath("../../Player")
@export var mood_path: NodePath = NodePath("../../PostProcess")

var _fpc: Node = null
var _mood: Node = null


func _ready() -> void:
    _fpc = get_node_or_null(fpc_path)
    _mood = get_node_or_null(mood_path)
    # Build buttons — label them with the matching F-key for muscle-
    # memory continuity. Buttons stack top-to-bottom.
    _add_btn("F1 · Toggle Collision",       Callable(self, "_btn_collide"))
    _add_btn("F2 · Teleport (0, 3, 0)",     Callable(self, "_btn_teleport"))
    _add_btn("F3 · Cycle Mood →",           Callable(self, "_btn_mood_next"))
    _add_btn("(prev) ← Cycle Mood",          Callable(self, "_btn_mood_prev"))
    _add_btn("F4 · Toggle HUD",              Callable(self, "_btn_hud"))
    _add_btn("F5 · Shimmer Strobe",          Callable(self, "_btn_shimmer"))
    _add_btn("F6 · Rift Strobe",             Callable(self, "_btn_rift"))
    _add_btn("F7 · ← Prev Track",            Callable(self, "_btn_prev_track"))
    _add_btn("F8 · Next Track →",            Callable(self, "_btn_next_track"))
    _add_btn("Capture Mouse (in-game)",      Callable(self, "_btn_capture"))


func _process(_delta: float) -> void:
    # Only show when the mouse is released — clicking buttons while
    # mouse is captured would be hidden anyway, and we want the panel
    # out of the way during normal gameplay.
    visible = Input.mouse_mode == Input.MOUSE_MODE_VISIBLE


func _add_btn(label: String, on_pressed: Callable) -> void:
    var b: Button = Button.new()
    b.text = label
    b.focus_mode = Control.FOCUS_NONE
    b.pressed.connect(on_pressed)
    add_child(b)


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

func _btn_prev_track() -> void:
    var m: Node = get_node_or_null("/root/InGameMusic")
    if m and m.has_method("prev_track"):
        m.prev_track()

func _btn_next_track() -> void:
    var m: Node = get_node_or_null("/root/InGameMusic")
    if m and m.has_method("next_track"):
        m.next_track()
