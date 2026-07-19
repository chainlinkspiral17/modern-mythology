extends Node
## GamepadMgr — the global controller translation layer.
## Baseline device: the 2026 Steam Controller (Steam Input presents
## it as a standard SDL gamepad; its HD haptic motors render SDL
## rumble, which SFXBank drives). Full design + mapping table:
## lore/_CONTROLLER_STEAM_PLAYBOOK.md.
##
## The package is ~60 surfaces of keyboard+mouse UI. Rather than
## rewrite them, this autoload translates pad input into the events
## those surfaces already understand — one path per input, never two:
##
##   · B → ESC, X → E, Y → J, View/Select → F4 · synthesized
##     InputEventKey. Synthesis happens in _unhandled_input, so a
##     Control that consumed the button (an AcceptDialog closing on
##     ui_cancel's built-in B binding) suppresses the synth and
##     nothing double-fires. menu_back's direct joypad binding was
##     removed from project.godot for the same reason.
##   · d-pad + left stick → arrow-key synth with keyboard-accurate
##     hold-repeat (echo events), ONLY while no Control has UI
##     focus — focus-based menus are already driven by Godot's
##     default ui_* joypad bindings, and synthesizing arrows there
##     would double-move focus.
##   · right stick → a drawn virtual mouse cursor · RB or R3
##     clicks. Every mouse-only surface (the CP board, gallery
##     tiles, dioramas, region panels) becomes pad-playable with
##     zero per-surface work. Fades after 3s idle; hides the
##     moment a real mouse moves.
##
## A (advance/accept) and Start (skip) ride the real input map —
## they were already bound there. Synthesized events carry
## device == SYNTH_DEVICE so this script never reacts to itself.

const SYNTH_DEVICE := 97            # sentinel · never a real device id
const CURSOR_SPEED := 950.0         # px/s at full deflection
const CURSOR_ACCEL_POW := 1.7      # response curve · fine control near center
const CURSOR_HIDE_AFTER := 3.0
const STICK_DEADZONE := 0.30
const REPEAT_DELAY := 0.28          # s before a held direction repeats
const REPEAT_RATE := 0.12           # s between repeats

# Face/utility buttons → synthesized keys (tap semantics).
const BUTTON_KEYS := {
	JOY_BUTTON_B: KEY_ESCAPE,       # back / close · everything checks ESC
	JOY_BUTTON_X: KEY_E,            # interact (Pirate Summer et al)
	JOY_BUTTON_Y: KEY_J,            # journal (Pirate Summer)
	JOY_BUTTON_BACK: KEY_F4,        # View button · clean-screenshot HUD toggle
}

# Directions → arrow keys. D-pad buttons and left-stick axes feed
# the same four channels.
const DIR_KEYS := {
	"up": KEY_UP, "down": KEY_DOWN, "left": KEY_LEFT, "right": KEY_RIGHT,
}

var _dir_state: Dictionary = {}     # "up" → {held: bool, t: float}

var _cursor_layer: CanvasLayer = null
var _cursor_dot: Control = null
var _cursor_pos: Vector2 = Vector2(640, 360)
var _cursor_idle: float = 999.0
var _cursor_active: bool = false    # has the right stick been touched


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for d in DIR_KEYS:
		_dir_state[d] = {"held": false, "t": 0.0}
	_build_cursor()


func _build_cursor() -> void:
	_cursor_layer = CanvasLayer.new()
	_cursor_layer.layer = 120
	add_child(_cursor_layer)
	_cursor_dot = Control.new()
	_cursor_dot.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_cursor_dot.visible = false
	_cursor_dot.draw.connect(_draw_cursor)
	_cursor_layer.add_child(_cursor_dot)


func _draw_cursor() -> void:
	# Small gold pointer · readable on every surface in the package.
	var gold := Color(0.92, 0.78, 0.40, 0.95)
	var ink := Color(0.02, 0.02, 0.01, 0.9)
	var pts := PackedVector2Array([
		Vector2(0, 0), Vector2(0, 15), Vector2(4, 11), Vector2(7, 17),
		Vector2(9, 16), Vector2(6, 10), Vector2(11, 10),
	])
	_cursor_dot.draw_colored_polygon(pts, gold)
	_cursor_dot.draw_polyline(pts, ink, 1.0)


# ── Button-tap synthesis (in unhandled so consumed input wins) ────

func _unhandled_input(event: InputEvent) -> void:
	if event.device == SYNTH_DEVICE:
		return
	if event is InputEventJoypadButton:
		var jb := event as InputEventJoypadButton
		if BUTTON_KEYS.has(jb.button_index):
			_synth_key(int(BUTTON_KEYS[jb.button_index]), jb.pressed, false)
			get_viewport().set_input_as_handled()
		elif jb.button_index == JOY_BUTTON_RIGHT_SHOULDER \
				or jb.button_index == JOY_BUTTON_RIGHT_STICK:
			if _cursor_active:
				_synth_click(jb.pressed)
				get_viewport().set_input_as_handled()


func _input(event: InputEvent) -> void:
	# A real mouse taking over hides the virtual cursor instantly.
	if event is InputEventMouseMotion and event.device != SYNTH_DEVICE:
		if (event as InputEventMouseMotion).relative.length_squared() > 4.0:
			_cursor_active = false
			if _cursor_dot != null:
				_cursor_dot.visible = false


# ── Per-frame · stick/d-pad polling ──────────────────────────────

func _process(delta: float) -> void:
	if Input.get_connected_joypads().is_empty():
		return
	_tick_dirs(delta)
	_tick_cursor(delta)


func _dir_intent() -> Dictionary:
	var lx := Input.get_joy_axis(0, JOY_AXIS_LEFT_X)
	var ly := Input.get_joy_axis(0, JOY_AXIS_LEFT_Y)
	return {
		"up": ly < -STICK_DEADZONE or Input.is_joy_button_pressed(0, JOY_BUTTON_DPAD_UP),
		"down": ly > STICK_DEADZONE or Input.is_joy_button_pressed(0, JOY_BUTTON_DPAD_DOWN),
		"left": lx < -STICK_DEADZONE or Input.is_joy_button_pressed(0, JOY_BUTTON_DPAD_LEFT),
		"right": lx > STICK_DEADZONE or Input.is_joy_button_pressed(0, JOY_BUTTON_DPAD_RIGHT),
	}


func _tick_dirs(delta: float) -> void:
	# While a Control has UI focus, Godot's default ui_* joypad
	# bindings drive focus navigation — synthesizing arrows on top
	# would double-move. Release anything held and stand down.
	var vp := get_viewport()
	var focus_owner: Control = vp.gui_get_focus_owner() if vp != null else null
	var intent: Dictionary = _dir_intent()
	for d in DIR_KEYS:
		var st: Dictionary = _dir_state[d]
		var want: bool = bool(intent[d]) and focus_owner == null
		var key: int = int(DIR_KEYS[d])
		if want and not bool(st["held"]):
			st["held"] = true
			st["t"] = -REPEAT_DELAY
			_synth_key(key, true, false)
		elif want and bool(st["held"]):
			st["t"] = float(st["t"]) + delta
			if float(st["t"]) >= REPEAT_RATE:
				st["t"] = 0.0
				_synth_key(key, true, true)    # keyboard-accurate echo
		elif not want and bool(st["held"]):
			st["held"] = false
			_synth_key(key, false, false)
		_dir_state[d] = st


func _tick_cursor(delta: float) -> void:
	var rx := Input.get_joy_axis(0, JOY_AXIS_RIGHT_X)
	var ry := Input.get_joy_axis(0, JOY_AXIS_RIGHT_Y)
	var v := Vector2(rx, ry)
	if v.length() < STICK_DEADZONE:
		_cursor_idle += delta
		if _cursor_idle > CURSOR_HIDE_AFTER and _cursor_dot != null:
			_cursor_dot.visible = false
		return
	_cursor_idle = 0.0
	_cursor_active = true
	# Response curve · slow near center for precise picks, fast at
	# full deflection for crossing the screen.
	var mag: float = clampf((v.length() - STICK_DEADZONE) / (1.0 - STICK_DEADZONE), 0.0, 1.0)
	var speed: float = CURSOR_SPEED * pow(mag, CURSOR_ACCEL_POW)
	_cursor_pos += v.normalized() * speed * delta
	var vp := get_viewport()
	if vp != null:
		var r: Rect2 = vp.get_visible_rect()
		_cursor_pos = _cursor_pos.clamp(r.position, r.position + r.size)
	if _cursor_dot != null:
		_cursor_dot.visible = true
		_cursor_dot.position = _cursor_pos
		_cursor_dot.queue_redraw()
	var mm := InputEventMouseMotion.new()
	mm.device = SYNTH_DEVICE
	mm.position = _cursor_pos
	mm.global_position = _cursor_pos
	mm.relative = v.normalized() * speed * delta
	Input.parse_input_event(mm)


# ── Synthesis helpers ────────────────────────────────────────────

func _synth_key(keycode: int, pressed: bool, echo: bool) -> void:
	var ev := InputEventKey.new()
	ev.device = SYNTH_DEVICE
	ev.keycode = keycode
	ev.physical_keycode = keycode
	ev.pressed = pressed
	ev.echo = echo
	Input.parse_input_event(ev)


func _synth_click(pressed: bool) -> void:
	var ev := InputEventMouseButton.new()
	ev.device = SYNTH_DEVICE
	ev.button_index = MOUSE_BUTTON_LEFT
	ev.pressed = pressed
	ev.position = _cursor_pos
	ev.global_position = _cursor_pos
	if pressed:
		ev.button_mask = MOUSE_BUTTON_MASK_LEFT
	Input.parse_input_event(ev)
	if _cursor_dot != null:
		_cursor_dot.visible = true
	_cursor_idle = 0.0
