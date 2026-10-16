extends Control
## Full-screen CG illustration viewer. Advance/click to dismiss.

var _callback: Callable

var _bg:      ColorRect   = null
var _img:     TextureRect = null
var _caption: Label       = null


func _ready() -> void:
	_build()
	mouse_filter = Control.MOUSE_FILTER_STOP


func _build() -> void:
	_bg = ColorRect.new()
	_bg.color = Color(0, 0, 0, 1)
	_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_bg)

	_img = TextureRect.new()
	_img.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_img.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_img.offset_bottom = -56
	add_child(_img)

	_caption = Label.new()
	_caption.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	_caption.custom_minimum_size.y = 48
	_caption.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_caption.add_theme_font_size_override("font_size", 16)
	_caption.add_theme_color_override("font_color", Color(0.75, 0.70, 0.60))
	add_child(_caption)


func present(src: String, caption: String, callback: Callable) -> void:
	_callback = callback
	_caption.text = caption
	_caption.visible = caption != ""

	var path := "res://" + src
	if ResourceLoader.exists(path):
		_img.texture = ResourceLoader.load(path) as Texture2D
	else:
		_img.texture = null

	# Fade in — the illustration arrives with a slow reveal and a
	# barely-there settle-zoom instead of popping on.
	_dismissing = false
	modulate.a = 0.0
	_img.pivot_offset = _img.size * 0.5
	_img.scale = Vector2(1.03, 1.03)
	var tw := create_tween()
	tw.set_parallel(true)
	tw.tween_property(self, "modulate:a", 1.0, 0.5)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	tw.tween_property(_img, "scale", Vector2.ONE, 2.2)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)


var _dismissing: bool = false

func _input(event: InputEvent) -> void:
	if not visible or _dismissing:
		return
	if event.is_action_pressed("advance"):
		get_viewport().set_input_as_handled()
		_dismissing = true
		var tw := create_tween()
		tw.tween_property(self, "modulate:a", 0.0, 0.35)\
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
		tw.tween_callback(func() -> void:
			modulate.a = 1.0
			if _callback.is_valid():
				_callback.call())
