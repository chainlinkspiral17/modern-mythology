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
	# F4 sweep compliance per CLAUDE.md hard rule. The implicit
	# MOUSE_MODE_VISIBLE hide already removes the menu during
	# captured-mouse play, but the F4 toggle should also nuke it
	# during screenshots. Explicit group membership makes the
	# behavior legible.
	add_to_group("ui")
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
	_add_btn("F9 · Cycle Blend Mode",        Callable(self, "_btn_blend_mode"))
	_add_btn("F10 · Cycle Blend Amount",     Callable(self, "_btn_blend_amount"))
	# Per-percent shader-intensity tuner — two buttons, one bumps the
	# tens digit, one bumps the ones digit. Both wrap (90→0 / 9→0).
	# Press repeatedly to dial in any 0-100% value.
	_add_btn("Blend % · +10 (tens)",         Callable(self, "_btn_blend_pct_tens"))
	_add_btn("Blend % · +1  (ones)",         Callable(self, "_btn_blend_pct_ones"))
	_add_btn("Blend % · reset → preset",     Callable(self, "_btn_blend_pct_reset"))
	_add_btn("F11 · Cycle Lighting",         Callable(self, "_btn_lighting"))
	_add_btn("F12 · Cycle Style Pack",       Callable(self, "_btn_style_pack"))
	_add_btn("Capture Mouse (in-game)",      Callable(self, "_btn_capture"))


const FPC_SCRIPT := preload("res://scripts/FirstPersonController.gd")


func _process(_delta: float) -> void:
	# Show when the mouse is released AND F4 hasn't nuked the HUD.
	# The F4 sweep sets visible=false; without this hud_visible AND
	# the next _process frame would set visible back to true and
	# screenshots would still get the menu in frame.
	visible = (Input.mouse_mode == Input.MOUSE_MODE_VISIBLE) and FPC_SCRIPT.hud_visible


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

func _btn_blend_mode() -> void:
	if _mood and _mood.has_method("action_cycle_blend_mode"):
		_mood.action_cycle_blend_mode()

func _btn_blend_amount() -> void:
	if _mood and _mood.has_method("action_cycle_blend_amount"):
		_mood.action_cycle_blend_amount()

func _btn_blend_pct_tens() -> void:
	if _mood and _mood.has_method("action_blend_pct_tens"):
		_mood.action_blend_pct_tens()

func _btn_blend_pct_ones() -> void:
	if _mood and _mood.has_method("action_blend_pct_ones"):
		_mood.action_blend_pct_ones()

func _btn_blend_pct_reset() -> void:
	if _mood and _mood.has_method("action_blend_pct_reset"):
		_mood.action_blend_pct_reset()

func _btn_lighting() -> void:
	if _mood and _mood.has_method("action_cycle_lighting"):
		_mood.action_cycle_lighting()

func _btn_style_pack() -> void:
	if _mood and _mood.has_method("action_cycle_style_pack"):
		_mood.action_cycle_style_pack()
