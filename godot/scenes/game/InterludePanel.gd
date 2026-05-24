extends Control
## Full-screen atmospheric interlude — large centered text with optional sub-text.
## duration=0 means wait for player advance; duration>0 auto-dismisses after ms.

var _callback: Callable
var _duration_timer: float = 0.0
var _waiting: bool = false

var _bg:     ColorRect = null
var _main:   Label     = null
var _sub:    Label     = null


func _ready() -> void:
	_build()
	mouse_filter = Control.MOUSE_FILTER_STOP


func _build() -> void:
	_bg = ColorRect.new()
	_bg.color = Color(0.01, 0.008, 0.005, 0.97)
	_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_bg)

	var center := VBoxContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	center.custom_minimum_size = Vector2(800, 0)
	center.offset_left   = -400
	center.offset_right  = 400
	center.alignment = BoxContainer.ALIGNMENT_CENTER
	center.add_theme_constant_override("separation", 24)
	add_child(center)

	_main = Label.new()
	_main.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_main.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_main.add_theme_font_size_override("font_size", 32)
	_main.add_theme_color_override("font_color", Color(0.93, 0.90, 0.83))
	center.add_child(_main)

	_sub = Label.new()
	_sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_sub.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_sub.add_theme_font_size_override("font_size", 18)
	_sub.add_theme_color_override("font_color", Color(0.65, 0.60, 0.50))
	center.add_child(_sub)


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


func _process(delta: float) -> void:
	if _duration_timer > 0.0:
		_duration_timer -= delta
		if _duration_timer <= 0.0:
			_duration_timer = 0.0
			_dismiss()


func try_advance() -> void:
	if _waiting:
		_dismiss()


func _dismiss() -> void:
	_waiting = false
	if _callback.is_valid():
		_callback.call()
