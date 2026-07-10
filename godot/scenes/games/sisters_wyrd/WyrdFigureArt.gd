extends RefCounted
class_name WyrdFigureArt
## THE SISTERS WYRD · figure art · the drifter and the four sisters.
##
## Same render language as the Earthman character plates (5-value
## ramps with Bayer-dithered transitions, folds, organic
## silhouettes), in the paperback inks.  Transparent backgrounds —
## these composite over existing screens — each figure standing on
## a small dust strip that carries her motif.
##
##   drifter() · 18×28 · wide-brim hat, face in shadow beneath it,
##       flared duster with folds, blood kerchief, iron glint at
##       the hip.  Drawn native on the crawl map (the player marker
##       IS the drifter now) and 3× on the title screen.
##   sister(id) · 28×44 · north (the net between her hands, snow
##       rising) · east (straight-backed in blood red, three
##       shadows on the dust, the face-down mirror) · south (the
##       rocker, the offered water glinting real) · west (young,
##       long ink hair, wind in the hem, the violet eighth point
##       at her collar — the only violet in the figure).
##
## Design mirror: godot/tools/sprites/preview_wyrd_figures.py —
## edit both together, preview before pushing.
##
## Usage (preload by path — new class_names miss the first editor
## scan after a pull):
##   const FIGURE_ART := preload("res://scenes/games/sisters_wyrd/WyrdFigureArt.gd")
##   draw_texture(FIGURE_ART.drifter(), pos)
##   tex_rect.texture = FIGURE_ART.sister("north", Vector2i(84, 132))

const INK    := Color("201410")
const DUST   := Color("c8a878")
const BONE   := Color("e8dcc0")
const BLOOD  := Color("7a3020")
const SILVER := Color("b8bcc8")
const WYRD   := Color("8a58a8")

static var _cache: Dictionary = {}


static func drifter(size: Vector2i = Vector2i(18, 28)) -> ImageTexture:
	var key := "drifter:%d" % size.x
	if _cache.has(key):
		return _cache[key]
	var img := Image.create(18, 28, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	_paint_drifter(img)
	if size != Vector2i(18, 28):
		img.resize(size.x, size.y, Image.INTERPOLATE_NEAREST)
	var tex := ImageTexture.create_from_image(img)
	_cache[key] = tex
	return tex


static func sister(wid: String, size: Vector2i = Vector2i(28, 44)) -> ImageTexture:
	var key := "sister:%s:%d" % [wid, size.x]
	if _cache.has(key):
		return _cache[key]
	var img := Image.create(28, 44, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	match wid:
		"north": _paint_north(img)
		"east":  _paint_east(img)
		"south": _paint_south(img)
		_:       _paint_west(img)
	if size != Vector2i(28, 44):
		img.resize(size.x, size.y, Image.INTERPOLATE_NEAREST)
	var tex := ImageTexture.create_from_image(img)
	_cache[key] = tex
	return tex


# ─── plumbing (shared render language) ───────────────────────────

const _BAYER4: Array = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5]


static func _bayer(x: int, y: int) -> float:
	return (float(_BAYER4[posmod(y, 4) * 4 + posmod(x, 4)]) + 0.5) / 16.0


static func _h01(x: int, y: int, s: int) -> float:
	var n: int = x * 374761393 + y * 668265263 + s * 1442695041
	n = (n ^ (n >> 13)) * 1274126177
	n = n ^ (n >> 16)
	return float(n & 0xFFFF) / 65536.0


static func _put(img: Image, x: int, y: int, c: Color) -> void:
	if x >= 0 and x < img.get_width() and y >= 0 and y < img.get_height():
		img.set_pixel(x, y, c)


static func _hspan(img: Image, x0: int, x1: int, y: int, c: Color) -> void:
	for x in range(x0, x1 + 1):
		_put(img, x, y, c)


static func _vspan(img: Image, x: int, y0: int, y1: int, c: Color) -> void:
	for y in range(y0, y1 + 1):
		_put(img, x, y, c)


static func _warm(c: Color, f: float = 0.22) -> Color:
	var l := c.lightened(f)
	return Color(minf(1.0, l.r * 1.08), l.g, l.b * 0.92, 1.0)


static func _shaded_row(img: Image, x0: int, x1: int, y: int, core: Color) -> void:
	var sh := core.darkened(0.42)
	var mid := core.darkened(0.18)
	var half := core.lightened(0.10)
	var lt := _warm(core)
	var span: int = maxi(1, x1 - x0)
	for x in range(x0, x1 + 1):
		var t: float = float(x - x0) / float(span)
		var c: Color
		if x == x1:
			c = lt
		elif t > 0.70:
			c = half if _bayer(x, y) < 0.45 else core
		elif x == x0:
			c = sh
		elif t < 0.30:
			c = mid if _bayer(x, y) < 0.6 else core
		else:
			c = core
		_put(img, x, y, c)


static func _folds(img: Image, x0: int, x1: int, y0: int, y1: int,
		core: Color, seed: int, n: int) -> void:
	var fold_c := core.darkened(0.30)
	for k in range(n):
		var fx: int = x0 + 2 + int(_h01(k, 5, seed) * float(maxi(1, x1 - x0 - 3)))
		for y in range(y0 + 1, y1):
			if _h01(fx, y, seed + k) < 0.75:
				_put(img, fx, y, fold_c)


static func _dust_strip(img: Image, base_y: int) -> void:
	for y in range(base_y, mini(img.get_height(), base_y + 4)):
		for x in range(img.get_width()):
			if _bayer(x, y) < (0.85 - float(y - base_y) * 0.25):
				_put(img, x, y, DUST if y == base_y else DUST.darkened(0.25))


static func _line(img: Image, x0: int, y0: int, x1: int, y1: int, c: Color) -> void:
	var steps: int = maxi(absi(x1 - x0), absi(y1 - y0))
	for s in range(steps + 1):
		@warning_ignore("integer_division")
		var x: int = x0 + (x1 - x0) * s / maxi(1, steps)
		@warning_ignore("integer_division")
		var y: int = y0 + (y1 - y0) * s / maxi(1, steps)
		_put(img, x, y, c)


# ─── the drifter ─────────────────────────────────────────────────

static func _paint_drifter(img: Image) -> void:
	var cx := 9
	var base := 24
	var coat := Color("2e1c14")
	_dust_strip(img, base + 1)
	for y in range(base - 1, base + 1):
		_shaded_row(img, cx - 3, cx - 2, y, Color("241a10"))
		_shaded_row(img, cx + 1, cx + 2, y, Color("241a10"))
	for y2 in range(11, base - 1):
		var t: float = float(y2 - 11) / float(base - 12)
		var hw: int = 3 + int(t * 3.0)
		if y2 > base - 4 and _h01(1, y2, 9) < 0.4:
			hw += 1
		_shaded_row(img, cx - hw, cx + hw, y2, coat)
	_folds(img, cx - 3, cx + 3, 13, base - 2, coat, 9, 2)
	_vspan(img, cx, base - 6, base - 2, coat.darkened(0.4))       # coat split
	_shaded_row(img, cx - 3, cx + 3, 10, coat)
	_shaded_row(img, cx - 4, cx + 4, 11, coat)
	_put(img, cx + 4, 16, SILVER)                                  # the iron
	_put(img, cx + 4, 17, SILVER.darkened(0.3))
	_hspan(img, cx - 1, cx + 1, 9, BLOOD)                          # kerchief
	_hspan(img, cx - 1, cx + 1, 7, Color("8a6848").darkened(0.45))  # face in shadow
	_hspan(img, cx - 1, cx + 1, 8, Color("8a6848").darkened(0.6))
	_hspan(img, cx - 4, cx + 4, 6, INK)                            # brim
	_hspan(img, cx - 2, cx + 2, 5, INK)                            # crown
	_hspan(img, cx - 2, cx + 2, 4, INK)
	_put(img, cx + 4, 6, _warm(Color("3a2c1c"), 0.3))
	_put(img, cx + 2, 4, _warm(Color("3a2c1c"), 0.2))


# ─── the sisters ─────────────────────────────────────────────────

static func _paint_north(img: Image) -> void:
	var cx := 14
	var base := 38
	var shawl := Color("8890a0")
	var dress := Color("5a5a68")
	_dust_strip(img, base + 1)
	for y in range(18, base + 1):
		var t: float = float(y - 18) / float(base - 18)
		_shaded_row(img, cx - 3 - int(t * 3.0), cx + 3 + int(t * 3.0), y, dress)
	_folds(img, cx - 3, cx + 3, 20, base - 1, dress, 11, 2)
	for y2 in range(8, 18):
		@warning_ignore("integer_division")
		var hw: int = 2 + mini(3, (y2 - 8) / 2)
		_shaded_row(img, cx - hw, cx + hw, y2, shawl)
	_hspan(img, cx - 1, cx + 1, 11, Color("d8ccc0").darkened(0.15))
	_put(img, cx - 1, 12, Color("d8ccc0").darkened(0.4))
	_put(img, cx + 1, 12, INK)                                     # one seen eye
	_vspan(img, cx - 6, 19, 24, shawl.darkened(0.2))               # arms out
	_vspan(img, cx + 6, 19, 24, _warm(shawl, 0.1))
	# the net no water ever saw
	_line(img, cx - 6, 25, cx + 6, 27, SILVER)
	_line(img, cx - 6, 27, cx + 6, 25, SILVER)
	_line(img, cx - 4, 24, cx - 1, 29, SILVER)
	_line(img, cx + 1, 29, cx + 4, 24, SILVER)
	# snow, rising
	for s in [[3, 30], [5, 18], [23, 24], [25, 12], [2, 8], [24, 36], [7, 38]]:
		_put(img, s[0], s[1], BONE)
		_put(img, s[0], int(s[1]) - 1, Color("f4f0e8"))


static func _paint_east(img: Image) -> void:
	var cx := 14
	var base := 38
	var dress := Color("7a3020")
	_dust_strip(img, base + 1)
	# three shadows on the dust, disagreeing
	for pair in [[-11, -4], [-1, 1], [4, 11]]:
		var dx0: int = pair[0]
		var dx1: int = pair[1]
		for t in range(8):
			@warning_ignore("integer_division")
			var x: int = cx + dx0 + (dx1 - dx0) * t / 8
			@warning_ignore("integer_division")
			var y: int = base + 1 + t / 4
			if _bayer(x, y) < 0.6:
				_put(img, x, y, INK)
	for y2 in range(14, base + 1):
		var t2: float = float(y2 - 14) / float(base - 14)
		_shaded_row(img, cx - 2 - int(t2 * 3.0), cx + 2 + int(t2 * 3.0), y2, dress)
	_folds(img, cx - 3, cx + 3, 16, base - 1, dress, 13, 2)
	_hspan(img, cx - 3, cx + 3, 20, dress.darkened(0.3))           # arms folded
	_hspan(img, cx - 3, cx + 3, 21, dress.lightened(0.1))
	var skin := Color("d8b8a0")
	for y3 in range(9, 12):
		_shaded_row(img, cx - 2, cx + 2, y3, skin)
	_hspan(img, cx - 2, cx + 2, 8, INK)                            # hair pulled tight
	_hspan(img, cx - 2, cx + 2, 7, INK)
	_vspan(img, cx - 3, 9, 13, INK)
	_put(img, cx + 1, 10, INK)
	_hspan(img, cx - 1, cx + 1, 12, skin.darkened(0.3))
	_hspan(img, cx + 5, cx + 8, base, SILVER)                      # the face-down mirror
	_hspan(img, cx + 5, cx + 8, base - 1, SILVER.darkened(0.35))


static func _paint_south(img: Image) -> void:
	var cx := 13
	var base := 38
	var dress := Color("8a6838")
	var chair := Color("4a3018")
	_dust_strip(img, base + 1)
	_line(img, 4, base, 24, base - 3, chair)                       # the rocker
	_line(img, 4, base - 3, 24, base, chair)
	_vspan(img, 6, 14, base - 2, chair)                            # chair back
	_vspan(img, 7, 12, base - 2, chair.darkened(0.2))
	_vspan(img, 20, 26, base - 2, chair)                           # front leg
	for y in range(16, 27):                                        # torso, leaning back
		@warning_ignore("integer_division")
		var hw: int = 2 + (y - 16) / 4
		@warning_ignore("integer_division")
		_shaded_row(img, cx - hw + (26 - y) / 6, cx + hw, y, dress)
	for y2 in range(27, 33):                                       # lap, forward
		_shaded_row(img, cx - 2, cx + 6, y2, dress)
	_folds(img, cx - 1, cx + 5, 27, 32, dress, 15, 2)
	_vspan(img, cx + 6, 33, base - 1, dress.darkened(0.25))        # shin
	_put(img, cx + 6, base, Color("241a10"))                       # shoe
	var skin := Color("d0b898")
	for y3 in range(11, 14):
		_shaded_row(img, cx - 1, cx + 3, y3, skin)
	_hspan(img, cx - 1, cx + 3, 10, SILVER)                        # the grey bun
	_put(img, cx - 2, 11, SILVER)
	_put(img, cx + 2, 12, INK)
	_vspan(img, cx + 8, 24, 26, dress.darkened(0.2))               # extended arm
	_put(img, cx + 9, 26, SILVER)                                  # the cup
	_put(img, cx + 9, 25, Color("f4f0e8"))                         # the water's light


static func _paint_west(img: Image) -> void:
	var cx := 14
	var base := 38
	var dress := Color("a08858")
	var hair := Color("241814")
	_dust_strip(img, base + 1)
	for y in range(14, base + 1):
		var t: float = float(y - 14) / float(base - 14)
		var hw: int = 2 + int(t * 4.0)
		var lean: int = int(t * 2.0)
		@warning_ignore("integer_division")
		_shaded_row(img, cx - hw - lean, cx + hw - lean / 2, y, dress)
	_folds(img, cx - 4, cx + 3, 16, base - 1, dress, 17, 3)
	# long ink hair, loose, falling past the shoulders
	for y2 in range(7, 22):
		var w: int = 1 if y2 < 10 else 2
		@warning_ignore("integer_division")
		var hx: int = cx - 3 - (y2 - 7) / 6
		for dx in range(w):
			_put(img, hx - dx, y2, hair)
	_hspan(img, cx - 2, cx + 2, 7, hair)
	_hspan(img, cx - 2, cx + 2, 6, hair)
	var skin := Color("e0c0a0")
	for y3 in range(9, 12):
		_shaded_row(img, cx - 2, cx + 2, y3, skin)
	_put(img, cx + 1, 10, INK)
	_hspan(img, cx - 1, cx + 1, 12, skin.darkened(0.3))
	_vspan(img, cx + 4, 18, 22, dress.darkened(0.2))               # hand on hip
	_put(img, cx + 4, 23, skin)
	# the eighth point at her collar — the only violet in the figure
	_put(img, cx, 14, WYRD)
	_put(img, cx - 1, 13, WYRD)
	_put(img, cx + 1, 13, WYRD)
	_put(img, cx, 12, WYRD.lightened(0.3))
