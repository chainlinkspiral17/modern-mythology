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
##   { "op": "vgrad", "y_range": [y0, y1], "stops": [i0, i1, ...] }
##       Vertical gradient through the palette stops, blended with
##       4x4 Bayer ordered dithering (silkscreen banding, not CRT).
##       Optional "x_range" clips horizontally. "from"/"to" is
##       shorthand for two stops.
##
##   { "op": "hgrad", "x_range": [x0, x1], "stops": [...] }
##       Horizontal gradient; optional "y_range" clips vertically.
##
##   { "op": "disk", "xy": [cx, cy], "r": int, "color": int }
##       Filled circle. Lamps, moons, clock faces, jar lids.
##
##   { "op": "ring", "xy": [cx, cy], "r": int, "color": int }
##       Circle outline, ~1px.
##
##   { "op": "noise", "xywh": [x, y, w, h], "color": int,
##     "density": float, "seed": int }
##       Deterministic hash speckle in a region. Paper tooth,
##       floor scuff, product clutter, star fields. Same seed =
##       same speckle, forever.
##
##   { "op": "shade", "xywh": [x, y, w, h], "color": int,
##     "amount": float }
##       Bayer-thresholded partial coverage — lays `color` over
##       the region at the given density. Shadows, glass, light
##       pools over existing art.
##
##   { "op": "checker", "xywh": [x, y, w, h], "colors": [a, b],
##     "cell": int }
##       Two-color checkerboard. Tile floors, table cloths.
##
##   ── HeroImage 2.0 (compositing ops) ──
##   These blend in true colour and SNAP to the nearest palette index,
##   so results stay in the authored ink set (silkscreen, not a filter).
##
##   { "op": "radial", "xy": [cx, cy], "r": int, "stops": [i, ...] }
##       Radial gradient disk, Bayer-dithered. Soft suns, vignettes,
##       lamp falloff.
##
##   { "op": "glow", "xy": [cx, cy], "r": int, "color": int,
##     "strength": float }
##       Additive soft halo (screen blend, quadratic falloff). Light
##       blooming off lamps, windows, suns.
##
##   { "op": "streak", "from": [x, y], "to": [x, y], "color": int,
##     "width": float, "strength": float, "blend": str }
##       Soft directional band. Light shafts, rain, glare, sun-track
##       shimmer. blend: normal|add|screen|mul (default screen).
##
##   { "op": "hatch", "xywh": [x, y, w, h], "color": int,
##     "spacing": float, "angle_deg": float }
##       Parallel printmaker hatching — directional shade that stays ink.
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


func _put(x: int, y: int, idx: int) -> void:
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
					_put(x, y, color)
		"vband":
			var xr: Array = op.get("x_range", [0, 0])
			var x0 := int(xr[0]); var x1 := int(xr[1])
			for x in range(x0, x1):
				for y in range(h):
					_put(x, y, color)
		"rect":
			var xywh: Array = op.get("xywh", [0, 0, 0, 0])
			var rx := int(xywh[0]); var ry := int(xywh[1])
			var rw := int(xywh[2]); var rh := int(xywh[3])
			for yy in range(ry, ry + rh):
				for xx in range(rx, rx + rw):
					_put(xx, yy, color)
		"hline":
			var y := int(op.get("y", 0))
			var xr2: Array = op.get("x_range", [0, w])
			for x in range(int(xr2[0]), int(xr2[1])):
				_put(x, y, color)
		"vline":
			var x2 := int(op.get("x", 0))
			var yr2: Array = op.get("y_range", [0, h])
			for y in range(int(yr2[0]), int(yr2[1])):
				_put(x2, y, color)
		"dot":
			var xy: Array = op.get("xy", [0, 0])
			var s := int(op.get("size", 1))
			var cx := int(xy[0]); var cy := int(xy[1])
			var half: int = maxi(0, s / 2)
			for dy in range(-half, half + (s % 2)):
				for dx in range(-half, half + (s % 2)):
					_put(cx + dx, cy + dy, color)
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
						_put(x, y, color)
					i2 += 2
		"text":
			var xy2: Array = op.get("xy", [0, 0])
			var s2 := String(op.get("s", ""))
			_draw_text(int(xy2[0]), int(xy2[1]), s2, color)
		"vgrad":
			var g_yr: Array = op.get("y_range", [0, h])
			var g_xr: Array = op.get("x_range", [0, w])
			var stops: Array = op.get("stops", [])
			if stops.is_empty():
				stops = [int(op.get("from", color)), int(op.get("to", color))]
			var gy0: int = int(g_yr[0]); var gy1: int = int(g_yr[1])
			var span: float = maxf(1.0, float(gy1 - gy0))
			for y in range(gy0, gy1):
				var t: float = float(y - gy0) / span
				for x in range(int(g_xr[0]), int(g_xr[1])):
					_put(x, y, _grad_pick(stops, t, x, y))
		"hgrad":
			var g_xr2: Array = op.get("x_range", [0, w])
			var g_yr2: Array = op.get("y_range", [0, h])
			var stops2: Array = op.get("stops", [])
			if stops2.is_empty():
				stops2 = [int(op.get("from", color)), int(op.get("to", color))]
			var gx0: int = int(g_xr2[0]); var gx1: int = int(g_xr2[1])
			var span2: float = maxf(1.0, float(gx1 - gx0))
			for x in range(gx0, gx1):
				var t2: float = float(x - gx0) / span2
				for y in range(int(g_yr2[0]), int(g_yr2[1])):
					_put(x, y, _grad_pick(stops2, t2, x, y))
		"disk":
			var d_xy: Array = op.get("xy", [0, 0])
			var d_r: int = int(op.get("r", 2))
			var dcx: int = int(d_xy[0]); var dcy: int = int(d_xy[1])
			for yy in range(dcy - d_r, dcy + d_r + 1):
				for xx in range(dcx - d_r, dcx + d_r + 1):
					var ddx: int = xx - dcx; var ddy: int = yy - dcy
					if ddx * ddx + ddy * ddy <= d_r * d_r:
						_put(xx, yy, color)
		"ring":
			var r_xy: Array = op.get("xy", [0, 0])
			var r_r: int = int(op.get("r", 2))
			var rcx: int = int(r_xy[0]); var rcy: int = int(r_xy[1])
			for yy in range(rcy - r_r, rcy + r_r + 1):
				for xx in range(rcx - r_r, rcx + r_r + 1):
					var rdx: int = xx - rcx; var rdy: int = yy - rcy
					var d2: int = rdx * rdx + rdy * rdy
					if d2 >= r_r * r_r - r_r and d2 <= r_r * r_r + r_r:
						_put(xx, yy, color)
		"noise":
			var n_rect: Array = op.get("xywh", [0, 0, w, h])
			var dens: float = clampf(float(op.get("density", 0.1)), 0.0, 1.0)
			var n_seed: int = int(op.get("seed", 7))
			var nx: int = int(n_rect[0]); var ny: int = int(n_rect[1])
			for yy in range(ny, ny + int(n_rect[3])):
				for xx in range(nx, nx + int(n_rect[2])):
					if _hash01(xx, yy, n_seed) < dens:
						_put(xx, yy, color)
		"shade":
			var s_rect: Array = op.get("xywh", [0, 0, w, h])
			var amt: float = clampf(float(op.get("amount", 0.5)), 0.0, 1.0)
			var sx0: int = int(s_rect[0]); var sy0: int = int(s_rect[1])
			for yy in range(sy0, sy0 + int(s_rect[3])):
				for xx in range(sx0, sx0 + int(s_rect[2])):
					if amt > _bayer(xx, yy):
						_put(xx, yy, color)
		"checker":
			var c_rect: Array = op.get("xywh", [0, 0, w, h])
			var cell: int = maxi(1, int(op.get("cell", 2)))
			var cols: Array = op.get("colors", [color, color])
			var cx0: int = int(c_rect[0]); var cy0: int = int(c_rect[1])
			for yy in range(cy0, cy0 + int(c_rect[3])):
				for xx in range(cx0, cx0 + int(c_rect[2])):
					@warning_ignore("integer_division")
					var pick: int = ((xx / cell) + (yy / cell)) % 2
					_put(xx, yy, int(cols[pick]))
		# ── HeroImage 2.0 ops ────────────────────────────────────
		# All composite WITHIN the palette (blend true-colour, then
		# snap to nearest palette index) so the result still reads as
		# silkscreen ink, never a post filter.
		"radial":
			# Radial gradient disk. { xy, r, stops:[i,...] } — soft
			# suns, vignettes, lamp falloff. Opaque, Bayer-dithered.
			var rd_xy: Array = op.get("xy", [w / 2, h / 2])
			var rd_r: float = maxf(1.0, float(op.get("r", 8)))
			var rd_stops: Array = op.get("stops", [color])
			var rcx: int = int(rd_xy[0]); var rcy: int = int(rd_xy[1])
			var rr: int = int(ceil(rd_r))
			for yy in range(rcy - rr, rcy + rr + 1):
				for xx in range(rcx - rr, rcx + rr + 1):
					var dd: float = sqrt(float((xx - rcx) ** 2 + (yy - rcy) ** 2))
					if dd <= rd_r:
						_put(xx, yy, _grad_pick(rd_stops, dd / rd_r, xx, yy))
		"glow":
			# Additive soft halo. { xy, r, color, strength }. Light
			# blooms off lamps/windows/suns; screen-blends up.
			var g_xy: Array = op.get("xy", [w / 2, h / 2])
			var g_r: float = maxf(1.0, float(op.get("r", 10)))
			var g_str: float = clampf(float(op.get("strength", 0.8)), 0.0, 1.0)
			var gcx: int = int(g_xy[0]); var gcy: int = int(g_xy[1])
			var gr: int = int(ceil(g_r))
			var g_col: Color = _pal(color)
			for yy in range(gcy - gr, gcy + gr + 1):
				for xx in range(gcx - gr, gcx + gr + 1):
					var gd: float = sqrt(float((xx - gcx) ** 2 + (yy - gcy) ** 2))
					if gd <= g_r:
						var fall: float = (1.0 - gd / g_r)
						_composite(xx, yy, g_col, "screen", g_str * fall * fall)
		"streak":
			# Soft directional band — light shafts, rain, glare lines.
			# { from:[x,y], to:[x,y], color, width, strength, blend }
			var s_a: Array = op.get("from", [0, 0])
			var s_b: Array = op.get("to", [w, h])
			var s_w: float = maxf(0.5, float(op.get("width", 2)))
			var s_str: float = clampf(float(op.get("strength", 0.6)), 0.0, 1.0)
			var s_blend: String = String(op.get("blend", "screen"))
			var s_col: Color = _pal(color)
			var ax: float = float(s_a[0]); var ay: float = float(s_a[1])
			var bx: float = float(s_b[0]); var by: float = float(s_b[1])
			var vx: float = bx - ax; var vy: float = by - ay
			var vlen2: float = maxf(1e-4, vx * vx + vy * vy)
			for yy in range(h):
				for xx in range(w):
					var t: float = clampf(((xx - ax) * vx + (yy - ay) * vy) / vlen2, 0.0, 1.0)
					var px: float = ax + t * vx; var py: float = ay + t * vy
					var perp: float = sqrt((xx - px) ** 2 + (yy - py) ** 2)
					if perp <= s_w:
						_composite(xx, yy, s_col, s_blend, s_str * (1.0 - perp / s_w))
		"hatch":
			# Parallel printmaker hatching in a rect. { xywh, color,
			# spacing, angle_deg } — directional shade that stays ink.
			var h_rect: Array = op.get("xywh", [0, 0, w, h])
			var h_sp: float = maxf(1.0, float(op.get("spacing", 3)))
			var h_ang: float = deg_to_rad(float(op.get("angle_deg", 45)))
			var hca: float = cos(h_ang); var hsa: float = sin(h_ang)
			var hx0: int = int(h_rect[0]); var hy0: int = int(h_rect[1])
			for yy in range(hy0, hy0 + int(h_rect[3])):
				for xx in range(hx0, hx0 + int(h_rect[2])):
					var proj: float = float(xx) * hca + float(yy) * hsa
					if fposmod(proj, h_sp) < 1.0:
						_put(xx, yy, color)


# 4x4 Bayer matrix for ordered-dither gradients and shading.
# Reads as silkscreen banding at HeroImage scale — deliberately a
# printmaker's tool, not a hardware artifact.
const _BAYER4: Array = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5]


func _bayer(x: int, y: int) -> float:
	return (float(_BAYER4[(posmod(y, 4)) * 4 + posmod(x, 4)]) + 0.5) / 16.0


func _pal(idx: int) -> Color:
	return _palette[idx] if idx >= 0 and idx < _palette.size() else Color(0, 0, 0, 1)


# Nearest palette index to an arbitrary colour, by squared RGB distance.
# Keeps composited results inside the authored ink set (silkscreen look).
var _near_cache: Dictionary = {}
func _nearest_palette(c: Color) -> int:
	var key: int = (int(c.r * 31) << 10) | (int(c.g * 31) << 5) | int(c.b * 31)
	if _near_cache.has(key):
		return _near_cache[key]
	var best: int = 0
	var best_d: float = 1e9
	for i in range(_palette.size()):
		var p: Color = _palette[i]
		var d: float = (p.r - c.r) ** 2 + (p.g - c.g) ** 2 + (p.b - c.b) ** 2
		if d < best_d:
			best_d = d
			best = i
	_near_cache[key] = best
	return best


# Composite `src` over the existing pixel with a blend mode at `amount`,
# then snap the result to the nearest palette index.
func _composite(x: int, y: int, src: Color, mode: String, amount: float) -> void:
	if x < 0 or x >= w or y < 0 or y >= h or amount <= 0.0:
		return
	var dst: Color = _pal(_pixels[y * w + x])
	var m: Color
	match mode:
		"add":
			m = Color(dst.r + src.r, dst.g + src.g, dst.b + src.b)
		"screen":
			m = Color(1.0 - (1.0 - dst.r) * (1.0 - src.r),
				1.0 - (1.0 - dst.g) * (1.0 - src.g),
				1.0 - (1.0 - dst.b) * (1.0 - src.b))
		"mul":
			m = Color(dst.r * src.r, dst.g * src.g, dst.b * src.b)
		_:
			m = src
	var out := dst.lerp(m, clampf(amount, 0.0, 1.0))
	out = Color(clampf(out.r, 0, 1), clampf(out.g, 0, 1), clampf(out.b, 0, 1))
	_pixels[y * w + x] = _nearest_palette(out)


# Pick a palette index along a multi-stop gradient at t in 0..1,
# dithering between the two neighboring stops.
func _grad_pick(stops: Array, t: float, x: int, y: int) -> int:
	if stops.size() == 1:
		return int(stops[0])
	var seg_f: float = t * float(stops.size() - 1)
	var seg: int = clampi(int(seg_f), 0, stops.size() - 2)
	var local_t: float = seg_f - float(seg)
	return int(stops[seg + 1]) if local_t > _bayer(x, y) else int(stops[seg])


# Deterministic per-pixel hash in 0..1. No RNG — the same speckle
# every load, every platform (see _SPRITE_PLAYBOOK: hash, don't seed).
func _hash01(x: int, y: int, s: int) -> float:
	var n: int = x * 374761393 + y * 668265263 + s * 1442695041
	n = (n ^ (n >> 13)) * 1274126177
	n = n ^ (n >> 16)
	return float(n & 0xFFFF) / 65536.0


func _bresenham(x0: int, y0: int, x1: int, y1: int, color: int) -> void:
	var dx: int = absi(x1 - x0); var sx: int = 1 if x0 < x1 else -1
	var dy: int = -absi(y1 - y0); var sy: int = 1 if y0 < y1 else -1
	var err: int = dx + dy
	while true:
		_put(x0, y0, color)
		if x0 == x1 and y0 == y1: break
		var e2: int = 2 * err
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
					_put(cx + col, y + row, color)
		cx += 4


func _parse_color(s: String) -> Color:
	if s == "" or s.to_lower() == "transparent":
		return Color(0, 0, 0, 0)
	var t: String = s
	if not t.begins_with("#"): t = "#" + t
	return Color(t)
