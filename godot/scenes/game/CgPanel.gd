extends Control
## Full-screen CG illustration viewer. Advance/click to dismiss.
## READER ZOOM (2026-10-16): dense pages (the weep (FOR THE FUTURE!)
## zine scans) are unreadable fitted whole to a Deck screen. Wheel or
## double-click/tap zooms at the pointer, drag pans while zoomed.
## Advance resets the zoom first, then a second advance dismisses, so
## a reader deep in a page never loses it to one stray keypress.

const ZOOM_MIN := 1.0
const ZOOM_MAX := 4.0
const ZOOM_STEP := 1.18
const DBLCLICK_ZOOM := 2.5

var _callback: Callable

var _bg:      ColorRect   = null
var _img:     TextureRect = null
var _caption: Label       = null

var _zoom: float = 1.0
var _pan: Vector2 = Vector2.ZERO
var _dragging: bool = false
var _drag_moved: bool = false
var _settle_tw: Tween = null


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
	# a picture larger than the canvas must not grow the rect past the
	# screen (ChapterCard, 2026-10-19: the same bug cut the title plates)
	_img.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
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

	_reset_view()
	# Fade in — the illustration arrives with a slow reveal and a
	# barely-there settle-zoom instead of popping on.
	_dismissing = false
	modulate.a = 0.0
	_img.pivot_offset = _img.size * 0.5
	_img.scale = Vector2(1.03, 1.03)
	_settle_tw = create_tween()
	_settle_tw.set_parallel(true)
	_settle_tw.tween_property(self, "modulate:a", 1.0, 0.5)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	_settle_tw.tween_property(_img, "scale", Vector2.ONE, 2.2)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)


func _reset_view() -> void:
	_zoom = 1.0
	_pan = Vector2.ZERO
	_dragging = false
	_drag_moved = false
	_apply_view()


func _kill_settle() -> void:
	if _settle_tw != null and _settle_tw.is_valid():
		_settle_tw.kill()
		_settle_tw = null
		modulate.a = 1.0


func _apply_view() -> void:
	_img.pivot_offset = _img.size * 0.5
	_img.scale = Vector2(_zoom, _zoom)
	# Clamp the pan so the page can't be dragged fully off screen.
	var slack: Vector2 = _img.size * (_zoom - 1.0) * 0.5
	_pan.x = clampf(_pan.x, -slack.x, slack.x)
	_pan.y = clampf(_pan.y, -slack.y, slack.y)
	_img.position = _pan


func _zoom_at(point: Vector2, new_zoom: float) -> void:
	_kill_settle()
	new_zoom = clampf(new_zoom, ZOOM_MIN, ZOOM_MAX)
	if is_equal_approx(new_zoom, _zoom):
		return
	# Keep the content under `point` (viewer coords) fixed while the
	# scale changes: pan' = (pan - d) * (z'/z) + d, d = point - center.
	var center: Vector2 = _img.size * 0.5
	var d: Vector2 = point - center
	_pan = (_pan - d) * (new_zoom / _zoom) + d
	_zoom = new_zoom
	if is_equal_approx(_zoom, 1.0):
		_pan = Vector2.ZERO
	_apply_view()


var _dismissing: bool = false

func _dismiss() -> void:
	_dismissing = true
	var tw := create_tween()
	tw.tween_property(self, "modulate:a", 0.0, 0.35)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	tw.tween_callback(func() -> void:
		modulate.a = 1.0
		_reset_view()
		if _callback.is_valid():
			_callback.call())


func _input(event: InputEvent) -> void:
	if not visible or _dismissing:
		return
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if mb.button_index == MOUSE_BUTTON_WHEEL_UP and mb.pressed:
			get_viewport().set_input_as_handled()
			_zoom_at(mb.position, _zoom * ZOOM_STEP)
			return
		if mb.button_index == MOUSE_BUTTON_WHEEL_DOWN and mb.pressed:
			get_viewport().set_input_as_handled()
			_zoom_at(mb.position, _zoom / ZOOM_STEP)
			return
		if mb.button_index == MOUSE_BUTTON_LEFT:
			if mb.pressed:
				if mb.double_click:
					get_viewport().set_input_as_handled()
					_zoom_at(mb.position, DBLCLICK_ZOOM if _zoom <= 1.001 else 1.0)
					return
				if _zoom > 1.001:
					get_viewport().set_input_as_handled()
					_dragging = true
					_drag_moved = false
					return
			else:
				if _dragging:
					get_viewport().set_input_as_handled()
					var was_drag := _drag_moved
					_dragging = false
					_drag_moved = false
					if was_drag:
						return
					# a clean click while zoomed: nothing — reading mode
					return
	if event is InputEventMouseMotion and _dragging:
		var mm := event as InputEventMouseMotion
		get_viewport().set_input_as_handled()
		_kill_settle()
		_drag_moved = true
		_pan += mm.relative
		_apply_view()
		return
	if event is InputEventKey and (event as InputEventKey).pressed:
		var k := event as InputEventKey
		if k.keycode == KEY_EQUAL or k.keycode == KEY_KP_ADD:
			get_viewport().set_input_as_handled()
			_zoom_at(_img.size * 0.5, _zoom * ZOOM_STEP)
			return
		if k.keycode == KEY_MINUS or k.keycode == KEY_KP_SUBTRACT:
			get_viewport().set_input_as_handled()
			_zoom_at(_img.size * 0.5, _zoom / ZOOM_STEP)
			return
	if event.is_action_pressed("advance"):
		get_viewport().set_input_as_handled()
		if _zoom > 1.001:
			# first advance backs out to the fitted page; the reader
			# sees where they are before the page goes away.
			_zoom_at(_img.size * 0.5, 1.0)
			return
		_dismiss()
