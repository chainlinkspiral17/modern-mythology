extends Control
## Full-screen atmospheric interlude — large centered text with optional sub-text.
## duration=0 means wait for player advance; duration>0 auto-dismisses after ms.
##
## 2026-07 presentation pass: serif type (IM Fell main, Cinzel sub),
## rule-diamond-rule ornaments, text fades in with a small rise, and
## a "continue" hint breathes in after a beat on player-advance cards.

var _callback: Callable
var _duration_timer: float = 0.0
var _waiting: bool = false

var _bg:     ColorRect     = null
var _center: VBoxContainer = null
var _main:   Label         = null
var _sub:    Label         = null
var _hint:   Label         = null
var _rise_tw: Tween        = null
var _base_top: float       = 0.0
var _base_bottom: float    = 0.0

const C_GOLD_DIM := Color(0.78, 0.66, 0.29, 0.45)


func _ready() -> void:
	_build()
	mouse_filter = Control.MOUSE_FILTER_STOP


func _build() -> void:
	_bg = ColorRect.new()
	_bg.color = Color(0.01, 0.008, 0.005, 0.97)
	_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_bg)

	_center = VBoxContainer.new()
	_center.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_center.custom_minimum_size = Vector2(800, 0)
	_center.offset_left   = -400
	_center.offset_right  = 400
	_center.alignment = BoxContainer.ALIGNMENT_CENTER
	_center.add_theme_constant_override("separation", 24)
	add_child(_center)

	_center.add_child(_make_ornament())

	_main = Label.new()
	_main.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_main.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	if ResourceLoader.exists(SkinDB.F_IMFELL_R):
		_main.add_theme_font_override("font", load(SkinDB.F_IMFELL_R) as Font)
	_main.add_theme_font_size_override("font_size", 34)
	_main.add_theme_color_override("font_color", Color(0.93, 0.90, 0.83))
	_center.add_child(_main)

	_sub = Label.new()
	_sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_sub.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		_sub.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
	_sub.add_theme_font_size_override("font_size", 16)
	_sub.add_theme_color_override("font_color", Color(0.65, 0.60, 0.50))
	_center.add_child(_sub)

	_center.add_child(_make_ornament())

	# Continue hint — invisible until a player-advance card has sat
	# for a beat; never shown on timed cards.
	_hint = Label.new()
	_hint.text = "·  continue  ·"
	_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		_hint.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
	_hint.add_theme_font_size_override("font_size", 12)
	_hint.add_theme_color_override("font_color", C_GOLD_DIM)
	_hint.modulate.a = 0.0
	_center.add_child(_hint)
	_base_top = _center.offset_top
	_base_bottom = _center.offset_bottom


func _make_ornament() -> Control:
	# rule — diamond — rule, the book plate's divider.
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	var r1 := ColorRect.new()
	r1.color = Color(C_GOLD_DIM.r, C_GOLD_DIM.g, C_GOLD_DIM.b, 0.25)
	r1.custom_minimum_size = Vector2(0, 1)
	r1.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	r1.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(r1)
	var d := Label.new()
	d.text = "◆"
	d.add_theme_font_size_override("font_size", 12)
	d.add_theme_color_override("font_color", C_GOLD_DIM)
	row.add_child(d)
	var r2 := ColorRect.new()
	r2.color = Color(C_GOLD_DIM.r, C_GOLD_DIM.g, C_GOLD_DIM.b, 0.25)
	r2.custom_minimum_size = Vector2(0, 1)
	r2.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	r2.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(r2)
	return row


func present(text: String, sub: String, duration_ms: int, callback: Callable) -> void:
	_callback = callback
	_main.text = text
	_sub.text  = sub
	_sub.visible = sub != ""
	_waiting = true

	if duration_ms > 0:
		_duration_timer = duration_ms / 1000.0
	else:
		_duration_timer = 0.0

	# Text fades in with a small rise — the card breathes instead of
	# popping. Offsets always animate from base+14 back to base so
	# rapid re-presents can't drift the block.
	if _rise_tw != null and _rise_tw.is_valid():
		_rise_tw.kill()
	_center.modulate.a = 0.0
	_center.offset_top = _base_top + 14.0
	_center.offset_bottom = _base_bottom + 14.0
	_hint.modulate.a = 0.0
	_rise_tw = create_tween()
	_rise_tw.set_parallel(true)
	_rise_tw.tween_property(_center, "modulate:a", 1.0, 0.6)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	_rise_tw.tween_property(_center, "offset_top", _base_top, 0.6)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	_rise_tw.tween_property(_center, "offset_bottom", _base_bottom, 0.6)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	if duration_ms == 0:
		_rise_tw.tween_property(_hint, "modulate:a", 0.7, 0.5).set_delay(1.4)


func _process(delta: float) -> void:
	if _duration_timer > 0.0:
		_duration_timer -= delta
		if _duration_timer <= 0.0:
			_duration_timer = 0.0
			_dismiss()
	elif _waiting and _hint.modulate.a > 0.0:
		# Breathe the continue hint.
		_hint.modulate.a = 0.45 + 0.25 * (0.5 + 0.5 * sin(Time.get_ticks_msec() / 500.0))


func try_advance() -> void:
	if _waiting:
		_dismiss()


func _dismiss() -> void:
	_waiting = false
	if _callback.is_valid():
		_callback.call()
