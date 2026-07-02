class_name RefOverlay
extends CanvasLayer
## On-screen reference / storyboard image. Toggle between hidden, fullscreen and
## the four corners. Loads images from res:// or any absolute / user:// path
## (drop reference frames anywhere and point at them). Driven manually (keys) or
## from the timeline via ref-image cues.

enum Place { HIDDEN, FULL, TL, TR, BL, BR }
const PLACE_NAMES := ["hidden", "fullscreen", "top-left", "top-right", "bottom-left", "bottom-right"]

var place: int = Place.HIDDEN
var current_path := ""
var _rect: TextureRect


func _ready() -> void:
	layer = 11
	_rect = TextureRect.new()
	_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_rect)
	_apply_layout()


func load_image(path: String) -> bool:
	var tex := _load_texture(path)
	if tex == null:
		return false
	_rect.texture = tex
	current_path = path
	if place == Place.HIDDEN:
		place = Place.FULL
	_apply_layout()
	return true


func _load_texture(path: String) -> Texture2D:
	if path == "":
		return null
	if ResourceLoader.exists(path):
		var r: Resource = load(path)
		if r is Texture2D:
			return r
	var img := Image.new()
	if img.load(path) == OK:
		return ImageTexture.create_from_image(img)
	return null


func cycle_place() -> void:
	place = (place + 1) % PLACE_NAMES.size()
	_apply_layout()


func set_place(p: int) -> void:
	place = clampi(p, 0, PLACE_NAMES.size() - 1)
	_apply_layout()


func place_name() -> String:
	return PLACE_NAMES[place]


func _apply_layout() -> void:
	if _rect == null:
		return
	_rect.visible = place != Place.HIDDEN and _rect.texture != null
	var vp := get_viewport().get_visible_rect().size
	var w := vp.x * 0.32
	var h := vp.y * 0.32
	var m := 16.0
	match place:
		Place.FULL:
			_rect.position = Vector2.ZERO
			_rect.size = vp
		Place.TL:
			_rect.position = Vector2(m, m)
			_rect.size = Vector2(w, h)
		Place.TR:
			_rect.position = Vector2(vp.x - w - m, m)
			_rect.size = Vector2(w, h)
		Place.BL:
			_rect.position = Vector2(m, vp.y - h - m)
			_rect.size = Vector2(w, h)
		Place.BR:
			_rect.position = Vector2(vp.x - w - m, vp.y - h - m)
			_rect.size = Vector2(w, h)
		_:
			pass
