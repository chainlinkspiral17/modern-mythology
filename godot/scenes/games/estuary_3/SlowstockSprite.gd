extends RefCounted
class_name SlowstockSprite
## Palette-indexed sprite loader for the Vol 7 slowstock library.
##
## A "slowstock sprite" is one of:
##   1. A JSON file describing an indexed image:
##        { "palette": ["#rgb"|"#rgba", ...],
##          "w": int, "h": int,
##          "data": [int, int, ...],           // flat row-major, w*h ints
##          "origin": [int, int]?,              // optional pivot
##          "hotspots": {name: [x, y]}?,        // optional named anchors
##          "attribution"?, "notes"? }
##      Palette index 0 is always transparent; use 1+ for opaque colors.
##      A hex color of "" or the string "transparent" also renders transparent.
##
##   2. A PNG file at the same path with a .png extension. If both exist,
##      the PNG wins. This is the escape hatch that lets a hand-drawn
##      sprite override an authored-JSON placeholder without any other
##      wiring change.
##
## Usage:
##
##     var s := SlowstockSprite.new()
##     s.load_from("res://resources/games/vol7/estuary_3/sprites/act2/heron.json")
##     var tex: ImageTexture = s.texture()
##     var pivot: Vector2 = s.origin
##     var eye_pos: Vector2 = s.hotspot("eye")
##
## The class is a plain RefCounted — no Node overhead. Multiple sprites
## can share the same palette by referencing a `palette_ref` string that
## resolves against a project-wide palette registry (deferred; not yet
## implemented — palettes are inline per file for now).

var w: int = 0
var h: int = 0
var origin: Vector2 = Vector2.ZERO
var hotspots: Dictionary = {}
var _image: Image = null
var _texture: ImageTexture = null
var _source_path: String = ""
var _notes: String = ""


func load_from(path: String) -> bool:
	## Load a slowstock sprite from `path`. If a PNG exists at the same
	## stem, the PNG wins; otherwise falls back to the JSON at `path`.
	## Returns true on success. Prints a push_warning on failure.
	_source_path = path
	var png_path := path.get_basename() + ".png"
	if FileAccess.file_exists(png_path):
		return _load_png(png_path)
	if FileAccess.file_exists(path):
		return _load_json(path)
	push_warning("[SlowstockSprite] no file at %s or %s" % [path, png_path])
	return false


func texture() -> ImageTexture:
	## Returns an ImageTexture wrapping the loaded image. Created lazily
	## and cached across calls.
	if _texture != null:
		return _texture
	if _image == null:
		push_warning("[SlowstockSprite] texture() called before load")
		return null
	_texture = ImageTexture.create_from_image(_image)
	return _texture


func image() -> Image:
	return _image


func hotspot(name: String) -> Vector2:
	## Returns the named hotspot in sprite-local pixel coordinates, or
	## `origin` if the name is not defined. Never returns null.
	if hotspots.has(name):
		var v: Variant = hotspots[name]
		if v is Vector2:
			return v
		if v is Array and (v as Array).size() >= 2:
			return Vector2(float(v[0]), float(v[1]))
	return origin


func notes() -> String:
	return _notes


# ─── internal ────────────────────────────────────────────────────

func _load_json(path: String) -> bool:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_warning("[SlowstockSprite] failed to open %s" % path)
		return false
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if not (parsed is Dictionary):
		push_warning("[SlowstockSprite] %s not a JSON object" % path)
		return false
	var d: Dictionary = parsed
	w = int(d.get("w", 0))
	h = int(d.get("h", 0))
	if w <= 0 or h <= 0:
		push_warning("[SlowstockSprite] %s missing w/h" % path)
		return false
	var palette: Array = d.get("palette", [])
	var colors: PackedColorArray = PackedColorArray()
	for p_var in palette:
		colors.append(_parse_color(String(p_var)))
	if colors.is_empty():
		push_warning("[SlowstockSprite] %s missing palette" % path)
		return false
	var data: Array = d.get("data", [])
	if data.size() != w * h:
		push_warning("[SlowstockSprite] %s data size %d != w*h %d" % [path, data.size(), w * h])
		return false
	_image = Image.create(w, h, false, Image.FORMAT_RGBA8)
	for y in range(h):
		for x in range(w):
			var idx: int = int(data[y * w + x])
			if idx < 0 or idx >= colors.size():
				idx = 0
			_image.set_pixel(x, y, colors[idx])
	# Optional origin (pivot) and hotspots.
	var orig: Variant = d.get("origin", null)
	if orig is Array and (orig as Array).size() >= 2:
		origin = Vector2(float(orig[0]), float(orig[1]))
	elif orig is Vector2:
		origin = orig
	else:
		origin = Vector2(float(w) / 2.0, float(h) / 2.0)
	hotspots = {}
	var hs: Variant = d.get("hotspots", {})
	if hs is Dictionary:
		for k in (hs as Dictionary).keys():
			var v: Variant = (hs as Dictionary)[k]
			if v is Array and (v as Array).size() >= 2:
				hotspots[String(k)] = Vector2(float(v[0]), float(v[1]))
	_notes = String(d.get("notes", ""))
	_texture = null
	return true


func _load_png(path: String) -> bool:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_warning("[SlowstockSprite] failed to open %s" % path)
		return false
	var bytes := f.get_buffer(f.get_length())
	f.close()
	var img := Image.new()
	var err := img.load_png_from_buffer(bytes)
	if err != OK:
		push_warning("[SlowstockSprite] failed to decode PNG at %s (err %d)" % [path, err])
		return false
	_image = img
	w = _image.get_width()
	h = _image.get_height()
	origin = Vector2(float(w) / 2.0, float(h) / 2.0)
	hotspots = {}
	_notes = ""
	_texture = null
	return true


func _parse_color(s: String) -> Color:
	# Accept: "", "transparent", "#rgb", "#rgba", "#rrggbb", "#rrggbbaa"
	if s == "" or s.to_lower() == "transparent":
		return Color(0, 0, 0, 0)
	var t: String = s
	if not t.begins_with("#"):
		t = "#" + t
	# Godot's Color("#hex") supports 3/4/6/8-hex forms.
	return Color(t)
