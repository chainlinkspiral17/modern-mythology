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


func _input(event: InputEvent) -> void:
	if not visible:
		return
	if event.is_action_pressed("advance"):
		get_viewport().set_input_as_handled()
		if _callback.is_valid():
			_callback.call()
