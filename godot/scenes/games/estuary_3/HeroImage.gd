extends RefCounted
class_name HeroImage
## Simple JSON-authored vector-style hero image rasterizer.
##
## Schema:
##   {
##     "id": str,
##     "w": int,  "h": int,               // low-res canvas
##     "palette": ["#rgb"|"#rgba", ...],  // color indexes
##     "layers": [ { "op": str, ... }, ... ]
##   }
##
## Operations:
##   { "op": "fill",  "color": int }
##       Fill the whole canvas with a palette-indexed color.
##
##   { "op": "hband", "y_range": [y0, y1], "color": int }
##       Horizontal band from y0 to y1 (inclusive-exclusive).
##
##   { "op": "vband", "x_range": [x0, x1], "color": int }
##       Vertical band.
##
##   { "op": "rect",  "xywh": [x, y, w, h], "color": int }
##       Filled rectangle.
##
##   { "op": "hline", "y": int, "x_range": [x0, x1], "color": int }
##       Single horizontal line row.
##
##   { "op": "vline", "x": int, "y_range": [y0, y1], "color": int }
##       Single vertical column.
##
##   { "op": "dot",   "xy": [x, y], "size": int, "color": int }
##       Filled square centered at xy.
##
##   { "op": "polyline", "points": [[x, y], ...], "color": int }
##       Connect the dots. Uses Bresenham for each segment.
##
##   { "op": "poly", "points": [[x, y], ...], "color": int }
##       Simple filled convex polygon (scanline fill).
##
##   { "op": "text", "xy": [x, y], "s": str, "color": int }
##       Draw ASCII text using a tiny built-in 3x5 font. Chunky
##       enough to be legible when the hero is upscaled 4x.
##
## Rendered image is palette-indexed rgba, upscaled to the target
## size with NEAREST-NEIGHBOR so the chunky "vector-style" look
## survives.
##
## Usage:
##   var h := HeroImage.new()
##   if h.load_from("res://.../hero.json"):
##       var tex := h.texture(Vector2i(640, 360))

var w: int = 0
var h: int = 0
var _palette: PackedColorArray = PackedColorArray()
var _pixels: PackedInt32Array = PackedInt32Array()
var _tex_cache: Dictionary = {}       # size_key -> ImageTexture


func load_from(path: String) -> bool:
	if not FileAccess.file_exists(path):
		push_warning("[HeroImage] missing %s" % path)
		return false
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return false
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if not (parsed is Dictionary):
		return false
	var d: Dictionary = parsed
	w = int(d.get("w", 0))
	h = int(d.get("h", 0))
	if w <= 0 or h <= 0:
		return false
	_palette.clear()
	for c in d.get("palette", []):
		_palette.append(_parse_color(String(c)))
	if _palette.is_empty():
		_palette.append(Color(0, 0, 0, 1))
	_pixels.resize(w * h)
	# Rasterize.
	for layer_var in d.get("layers", []):
		if typeof(layer_var) == TYPE_DICTIONARY:
			_apply(layer_var)
	_tex_cache.clear()
	return true


func texture(target_size: Vector2i = Vector2i.ZERO) -> ImageTexture:
	# If target_size is zero, return native-size texture.  Otherwise
	# nearest-neighbor upscale to target.
	if target_size == Vector2i.ZERO:
		target_size = Vector2i(w, h)
	var key := "%d_%d" % [target_size.x, target_size.y]
	if _tex_cache.has(key):
		return _tex_cache[key]
	var native := _to_image()
	var out_img: Image = native
	if target_size != Vector2i(w, h):
		out_img = Image.create(target_size.x, target_size.y, false, Image.FORMAT_RGBA8)
		# Nearest-neighbor sample.
		for y in range(target_size.y):
			var sy := int(float(y) / float(target_size.y) * float(h))
			sy = clamp(sy, 0, h - 1)
			for x in range(target_size.x):
				var sx := int(float(x) / float(target_size.x) * float(w))
				sx = clamp(sx, 0, w - 1)
				out_img.set_pixel(x, y, _palette[_pixels[sy * w + sx]])
	var tex := ImageTexture.create_from_image(out_img)
	_tex_cache[key] = tex
	return tex


# ─── internal ────────────────────────────────────────────────────

func _to_image() -> Image:
	var img := Image.create(w, h, false, Image.FORMAT_RGBA8)
	for y in range(h):
		for x in range(w):
			img.set_pixel(x, y, _palette[_pixels[y * w + x]])
	return img


func _set(x: int, y: int, idx: int) -> void:
	if x < 0 or x >= w or y < 0 or y >= h: return
	if idx < 0 or idx >= _palette.size(): return
	_pixels[y * w + x] = idx


func _apply(op: Dictionary) -> void:
	var kind := String(op.get("op", ""))
	var color := int(op.get("color", 0))
	match kind:
		"fill":
			for i in range(_pixels.size()):
				_pixels[i] = color
		"hband":
			var yr: Array = op.get("y_range", [0, 0])
			var y0 := int(yr[0]); var y1 := int(yr[1])
			for y in range(y0, y1):
				for x in range(w):
					_set(x, y, color)
		"vband":
			var xr: Array = op.get("x_range", [0, 0])
			var x0 := int(xr[0]); var x1 := int(xr[1])
			for x in range(x0, x1):
				for y in range(h):
					_set(x, y, color)
		"rect":
			var xywh: Array = op.get("xywh", [0, 0, 0, 0])
			var rx := int(xywh[0]); var ry := int(xywh[1])
			var rw := int(xywh[2]); var rh := int(xywh[3])
			for yy in range(ry, ry + rh):
				for xx in range(rx, rx + rw):
					_set(xx, yy, color)
		"hline":
			var y := int(op.get("y", 0))
			var xr2: Array = op.get("x_range", [0, w])
			for x in range(int(xr2[0]), int(xr2[1])):
				_set(x, y, color)
		"vline":
			var x2 := int(op.get("x", 0))
			var yr2: Array = op.get("y_range", [0, h])
			for y in range(int(yr2[0]), int(yr2[1])):
				_set(x2, y, color)
		"dot":
			var xy: Array = op.get("xy", [0, 0])
			var s := int(op.get("size", 1))
			var cx := int(xy[0]); var cy := int(xy[1])
			var half := max(0, s / 2)
			for dy in range(-half, half + (s % 2)):
				for dx in range(-half, half + (s % 2)):
					_set(cx + dx, cy + dy, color)
		"polyline":
			var pts: Array = op.get("points", [])
			for i in range(pts.size() - 1):
				var a: Array = pts[i]; var b: Array = pts[i + 1]
				_bresenham(int(a[0]), int(a[1]), int(b[0]), int(b[1]), color)
		"poly":
			# Simple scanline fill for a convex polygon.
			var pts2: Array = op.get("points", [])
			if pts2.size() < 3: return
			var min_y := 999999; var max_y := -999999
			for p in pts2:
				min_y = min(min_y, int(p[1]))
				max_y = max(max_y, int(p[1]))
			min_y = max(0, min_y); max_y = min(h - 1, max_y)
			for y in range(min_y, max_y + 1):
				var xs: Array = []
				for i in range(pts2.size()):
					var a: Array = pts2[i]
					var b: Array = pts2[(i + 1) % pts2.size()]
					var ay := int(a[1]); var by := int(b[1])
					if (ay <= y and by > y) or (by <= y and ay > y):
						var t := float(y - ay) / float(by - ay)
						xs.append(int(a[0]) + t * (int(b[0]) - int(a[0])))
				xs.sort()
				var i2 := 0
				while i2 + 1 < xs.size():
					for x in range(int(xs[i2]), int(xs[i2 + 1]) + 1):
						_set(x, y, color)
					i2 += 2
		"text":
			var xy2: Array = op.get("xy", [0, 0])
			var s2 := String(op.get("s", ""))
			_draw_text(int(xy2[0]), int(xy2[1]), s2, color)


func _bresenham(x0: int, y0: int, x1: int, y1: int, color: int) -> void:
	var dx := abs(x1 - x0); var sx := 1 if x0 < x1 else -1
	var dy := -abs(y1 - y0); var sy := 1 if y0 < y1 else -1
	var err := dx + dy
	while true:
		_set(x0, y0, color)
		if x0 == x1 and y0 == y1: break
		var e2 := 2 * err
		if e2 >= dy: err += dy; x0 += sx
		if e2 <= dx: err += dx; y0 += sy


# 3x5 pixel font · uppercase A-Z, digits 0-9, space, period, comma,
# apostrophe, dash. Row-major bitmask (row 0 = top, MSB = left col).
const _FONT_3X5 := {
	" ": [0, 0, 0, 0, 0],
	".": [0, 0, 0, 0, 2],
	",": [0, 0, 0, 2, 4],
	"'": [2, 2, 0, 0, 0],
	"-": [0, 0, 7, 0, 0],
	"A": [2, 5, 7, 5, 5], "B": [6, 5, 6, 5, 6], "C": [3, 4, 4, 4, 3],
	"D": [6, 5, 5, 5, 6], "E": [7, 4, 6, 4, 7], "F": [7, 4, 6, 4, 4],
	"G": [3, 4, 5, 5, 3], "H": [5, 5, 7, 5, 5], "I": [7, 2, 2, 2, 7],
	"J": [1, 1, 1, 5, 2], "K": [5, 6, 4, 6, 5], "L": [4, 4, 4, 4, 7],
	"M": [5, 7, 7, 5, 5], "N": [5, 7, 7, 7, 5], "O": [2, 5, 5, 5, 2],
	"P": [6, 5, 6, 4, 4], "Q": [2, 5, 5, 7, 3], "R": [6, 5, 6, 5, 5],
	"S": [3, 4, 2, 1, 6], "T": [7, 2, 2, 2, 2], "U": [5, 5, 5, 5, 7],
	"V": [5, 5, 5, 5, 2], "W": [5, 5, 7, 7, 5], "X": [5, 5, 2, 5, 5],
	"Y": [5, 5, 2, 2, 2], "Z": [7, 1, 2, 4, 7],
	"0": [7, 5, 5, 5, 7], "1": [2, 6, 2, 2, 7], "2": [6, 1, 2, 4, 7],
	"3": [6, 1, 2, 1, 6], "4": [5, 5, 7, 1, 1], "5": [7, 4, 6, 1, 6],
	"6": [3, 4, 7, 5, 7], "7": [7, 1, 2, 4, 4], "8": [7, 5, 2, 5, 7],
	"9": [7, 5, 7, 1, 6],
}


func _draw_text(x: int, y: int, s: String, color: int) -> void:
	var cx := x
	for c in s.to_upper():
		if not _FONT_3X5.has(c):
			cx += 4; continue
		var glyph: Array = _FONT_3X5[c]
		for row in range(glyph.size()):
			var bits: int = int(glyph[row])
			# bits are 3-wide, MSB = left col
			for col in range(3):
				if bits & (1 << (2 - col)):
					_set(cx + col, y + row, color)
		cx += 4


func _parse_color(s: String) -> Color:
	if s == "" or s.to_lower() == "transparent":
		return Color(0, 0, 0, 0)
	var t: String = s
	if not t.begins_with("#"): t = "#" + t
	return Color(t)
