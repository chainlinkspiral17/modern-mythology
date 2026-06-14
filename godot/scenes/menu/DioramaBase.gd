extends Control
## DioramaBase — shared chrome for every card's playable diorama.
##
## Subclasses implement _build_content() and (optionally)
## _ambient_sample(delta) to drop in their own audio. The base
## handles:
##   · solid backdrop + edge wash
##   · top strip with title, hint text, close button, ESC handler
##   · right-side reveal panel (shared across all dioramas)
##   · cross-card unlock dispatch via reveal()
##   · procedural ambient audio scaffold (a per-diorama
##     _ambient_sample callback that returns one stereo sample
##     per audio frame; base mixes it onto the BGM bus)
##
## The diorama is intended to be added as a child of a
## TarotVisualizerBase. The base spawns it from a hotspot's
## `opens_diorama` field; on `closed` it queue_frees itself.

signal closed

# Common palette
const C_BG := Color(0.020, 0.012, 0.018, 0.96)
const C_INK := Color(0.06, 0.04, 0.06)
const C_GOLD := Color(0.85, 0.66, 0.29)
const C_GOLD_HI := Color(1.0, 0.85, 0.40)
const C_TEXT := Color(0.85, 0.72, 0.50)
const C_TEXT_DIM := Color(0.52, 0.40, 0.22)

# Subclass override hooks — set in subclass _init()
var _diorama_title: String = "DIORAMA"
var _diorama_hint: String = "click to interact · esc to leave"
var _edge_wash_color: Color = Color(1.0, 1.0, 1.0, 0.04)

# Reveal panel state
var _reveal_panel: PanelContainer = null
var _reveal_head: Label = null
var _reveal_text: RichTextLabel = null

# Ambient audio
var _amb_gen: AudioStreamGenerator
var _amb_player: AudioStreamPlayer
var _amb_playback: AudioStreamGeneratorPlayback
var _t: float = 0.0


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	_build_chrome()
	_build_content()
	_init_ambient()
	set_process(true)
	set_process_input(true)


# ── Chrome ────────────────────────────────────────────────────────

func _build_chrome() -> void:
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(bg)

	# Edge wash — gives each diorama a distinct atmospheric tint
	var wash := ColorRect.new()
	wash.color = _edge_wash_color
	wash.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	wash.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(wash)

	var top := PanelContainer.new()
	top.set_anchors_preset(Control.PRESET_TOP_WIDE)
	top.offset_bottom = 40
	var tps := StyleBoxFlat.new()
	tps.bg_color = Color(0, 0, 0, 0.78)
	tps.border_color = C_GOLD
	tps.border_width_bottom = 1
	top.add_theme_stylebox_override("panel", tps)
	add_child(top)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 12)
	top.add_child(row)
	var lpad := Control.new()
	lpad.custom_minimum_size = Vector2(14, 0)
	row.add_child(lpad)
	var title := Label.new()
	title.text = _diorama_title
	title.add_theme_color_override("font_color", C_GOLD_HI)
	title.add_theme_font_size_override("font_size", 13)
	title.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(title)
	var sp := Control.new()
	sp.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(sp)
	var hint := Label.new()
	hint.text = _diorama_hint
	hint.add_theme_color_override("font_color", C_TEXT_DIM)
	hint.add_theme_font_size_override("font_size", 9)
	hint.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(hint)
	var close := Button.new()
	close.text = "[ × CLOSE ]"
	close.flat = true
	close.add_theme_color_override("font_color", C_GOLD_HI)
	close.pressed.connect(func() -> void: closed.emit())
	row.add_child(close)


## Subclasses override this to build their interactive content.
## The base has already added the backdrop, edge wash, and top
## strip — implementations should add their content as children
## of `self`.
func _build_content() -> void:
	pass


# ── Reveal panel — right-side text + unlock dispatch ──────────────

## Show a reveal panel with `head_text` and `body_text`. If
## `unlock_key` is non-empty, mark it as unlocked (cross-card
## unlocks fire from here).
func reveal(head_text: String, body_text: String, unlock_key: String = "") -> void:
	_ensure_reveal_panel()
	_reveal_head.text = "▷ " + head_text
	_reveal_text.text = body_text
	if unlock_key != "":
		SaveSystem.mark_unlocked(unlock_key)
	_reveal_panel.visible = true
	_reveal_panel.modulate.a = 0.0
	var tw := create_tween()
	tw.tween_property(_reveal_panel, "modulate:a", 1.0, 0.22)


func _ensure_reveal_panel() -> void:
	if _reveal_panel != null and is_instance_valid(_reveal_panel):
		return
	_reveal_panel = PanelContainer.new()
	_reveal_panel.set_anchors_preset(Control.PRESET_RIGHT_WIDE)
	_reveal_panel.offset_left = -380
	_reveal_panel.offset_right = -18
	_reveal_panel.offset_top = 56
	_reveal_panel.offset_bottom = -18
	_reveal_panel.mouse_filter = Control.MOUSE_FILTER_STOP
	_reveal_panel.z_index = 12
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.03, 0.02, 0.04, 0.96)
	sb.border_color = C_GOLD_HI
	sb.set_border_width_all(1)
	_reveal_panel.add_theme_stylebox_override("panel", sb)
	add_child(_reveal_panel)
	var m := MarginContainer.new()
	m.add_theme_constant_override("margin_left", 12)
	m.add_theme_constant_override("margin_right", 12)
	m.add_theme_constant_override("margin_top", 10)
	m.add_theme_constant_override("margin_bottom", 10)
	_reveal_panel.add_child(m)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 6)
	m.add_child(vb)
	_reveal_head = Label.new()
	_reveal_head.add_theme_color_override("font_color", C_GOLD_HI)
	_reveal_head.add_theme_font_size_override("font_size", 11)
	vb.add_child(_reveal_head)
	_reveal_text = RichTextLabel.new()
	_reveal_text.fit_content = true
	_reveal_text.bbcode_enabled = false
	_reveal_text.add_theme_color_override("default_color", C_TEXT)
	_reveal_text.add_theme_font_size_override("normal_font_size", 10)
	_reveal_text.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vb.add_child(_reveal_text)
	var dismiss := Button.new()
	dismiss.text = "[ × dismiss ]"
	dismiss.flat = true
	dismiss.alignment = HORIZONTAL_ALIGNMENT_RIGHT
	dismiss.add_theme_color_override("font_color", C_GOLD)
	dismiss.pressed.connect(func() -> void: _reveal_panel.visible = false)
	vb.add_child(dismiss)
	_reveal_panel.visible = false


## Quick helper for subclasses building hotspot buttons over their
## content. `parent` is the container the button is added to; `rect`
## is normalised (x, y, w, h); `tooltip` shows on hover. The press
## callback receives no args.
func make_hotspot(parent: Control, rect: Array, tooltip: String,
				   on_press: Callable) -> Button:
	var btn := Button.new()
	btn.flat = true
	btn.tooltip_text = tooltip
	btn.anchor_left = float(rect[0])
	btn.anchor_top = float(rect[1])
	btn.anchor_right = float(rect[0]) + float(rect[2])
	btn.anchor_bottom = float(rect[1]) + float(rect[3])
	btn.mouse_default_cursor_shape = Control.CURSOR_HELP
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(1, 0.85, 0.40, 0.0)
	sb.border_color = Color(1, 0.85, 0.40, 0.0)
	sb.set_border_width_all(1)
	btn.add_theme_stylebox_override("normal", sb)
	var sbh := sb.duplicate() as StyleBoxFlat
	sbh.bg_color = Color(1, 0.85, 0.40, 0.30)
	sbh.border_color = Color(1, 0.85, 0.40, 0.85)
	btn.add_theme_stylebox_override("hover", sbh)
	btn.add_theme_stylebox_override("focus", sbh)
	btn.pressed.connect(on_press)
	parent.add_child(btn)
	return btn


# ── Procedural ambient audio scaffold ─────────────────────────────
# The base wires up an AudioStreamGenerator on the BGM bus. Each
# audio frame, the base calls _ambient_sample(t, delta_phase) on
# the subclass to get a stereo sample. Subclasses override this
# method to produce their own diorama-specific ambient.

var _aud_step: float = 0.0


func _init_ambient() -> void:
	_amb_gen = AudioStreamGenerator.new()
	_amb_gen.mix_rate = 44100
	_amb_gen.buffer_length = 0.05
	_amb_player = AudioStreamPlayer.new()
	_amb_player.bus = "BGM"
	_amb_player.stream = _amb_gen
	_amb_player.volume_db = -16.0
	add_child(_amb_player)
	_amb_player.play()
	_amb_playback = _amb_player.get_stream_playback()


func _process(delta: float) -> void:
	_t += delta
	_on_diorama_tick(delta)
	if _amb_playback == null:
		return
	var frames := _amb_playback.get_frames_available()
	if frames <= 0:
		return
	var step := 1.0 / 44100.0
	for _i in frames:
		_aud_step += step
		var s: Vector2 = _ambient_sample(_aud_step, step)
		s.x = clamp(s.x, -0.95, 0.95)
		s.y = clamp(s.y, -0.95, 0.95)
		_amb_playback.push_frame(s)


## Subclasses override this for per-frame logic (animations,
## scheduled events, etc.). Base does nothing.
func _on_diorama_tick(_delta: float) -> void:
	pass


## Subclasses override this to produce one stereo audio sample per
## frame. Default: silence. `phase` is the running audio time in
## seconds since the diorama opened; `step` is 1/44100.
func _ambient_sample(_phase: float, _step: float) -> Vector2:
	return Vector2.ZERO


# ── Input ─────────────────────────────────────────────────────────

func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE:
			closed.emit()
			get_viewport().set_input_as_handled()
