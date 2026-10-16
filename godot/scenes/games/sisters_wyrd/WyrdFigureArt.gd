extends RefCounted
class_name WyrdFigureArt
## THE SISTERS WYRD · figure art · the drifter and the four sisters.
##
## v2 — human bones (user: "they don't look human").  Every figure
## is now built on real proportions: a rounded head ≈ 1/6 of the
## height with TWO eyes and a mouth, a neck, sloped shoulders about
## two head-widths across, a fitted bodice to a WAIST, skirts that
## flare from the waist (never from the neck), and arms with elbows
## and hands.  Costume drapes over the bones, not instead of them.
##
##   drifter() · 18×28 · hat brim over a shadowed brow with a LIT
##       JAW, blood kerchief at the neck, coat with a belt at the
##       waist and a front split showing the legs, gloved hands,
##       iron glint on the belt.
##   sister(id) · 28×44 · north (hooded, arms out, the net between
##       her hands, snow rising) · east (hair in a knot, arms
##       folded at the waist, three shadows, the face-down mirror)
##       · south (seated in the rocker, one arm on her lap, the
##       other offering the water) · west (loose ink hair, hand on
##       hip, wind in the hem, the violet eighth point).
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
const CLEAR  := Color(0, 0, 0, 0)

static var _cache: Dictionary = {}


static func drifter(size: Vector2i = Vector2i(18, 28)) -> ImageTexture:
	var key := "drifter:%d" % size.x
	if _cache.has(key):
		return _cache[key]
	var img := Image.create(18, 28, false, Image.FORMAT_RGBA8)
	img.fill(CLEAR)
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
	img.fill(CLEAR)
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


# ─── human bones ─────────────────────────────────────────────────
# Head ≈ 1/6 of figure height, neck, sloped shoulders ≈ two head
# widths, fitted bodice to a WAIST, skirts flare from the waist.

## Rounded 5×6 head with two eyes and a mouth hint.
static func _head6(img: Image, cx: int, top: int, skin: Color) -> void:
	for y in range(top, top + 6):
		var x0: int = cx - 2
		var x1: int = cx + 2
		if y == top or y == top + 5:
			x0 = cx - 1
			x1 = cx + 1
		_shaded_row(img, x0, x1, y, skin)
	_put(img, cx - 1, top + 3, INK)
	_put(img, cx + 1, top + 3, INK)
	_put(img, cx, top + 5, skin.darkened(0.25))


## Neck at top..top+1, shoulders sloping out beneath.
static func _neck_shoulders(img: Image, cx: int, top: int, skin: Color, garment: Color) -> void:
	_hspan(img, cx - 1, cx + 1, top, skin.darkened(0.2))
	_shaded_row(img, cx - 3, cx + 3, top + 1, garment)
	_shaded_row(img, cx - 5, cx + 5, top + 2, garment)


## Fitted torso: shoulders half-width 5 tapering to waist 3.
static func _bodice(img: Image, cx: int, y0: int, y1: int, garment: Color) -> void:
	for y in range(y0, y1 + 1):
		var t: float = float(y - y0) / float(maxi(1, y1 - y0))
		var hw: int = 5 - int(t * 2.0)
		_shaded_row(img, cx - hw, cx + hw, y, garment)


## Upper arm 2px from the shoulder, elbow, forearm, hand.
static func _arm(img: Image, sx: int, sy: int, cx: int, skin: Color, garment: Color, bend: int = 0) -> void:
	var side: int = 1 if sx > cx else -1
	for y in range(sy, sy + 5):
		_put(img, sx, y, garment.darkened(0.18) if side < 0 else _warm(garment, 0.1))
	var ex: int = sx + bend * side
	for y2 in range(sy + 5, sy + 9):
		_put(img, ex, y2, garment.darkened(0.25) if side < 0 else garment)
	_put(img, ex, sy + 9, skin)


# ─── the drifter ─────────────────────────────────────────────────

static func _paint_drifter(img: Image) -> void:
	var cx := 9
	var base := 24
	var coat := Color("2e1c14")
	var skin := Color("c09068")
	_dust_strip(img, base + 1)
	# legs in the coat split + boots
	_vspan(img, cx - 2, base - 5, base - 2, coat.darkened(0.35))
	_vspan(img, cx + 1, base - 5, base - 2, coat.darkened(0.3))
	for bx in [cx - 3, cx + 1]:
		_hspan(img, bx, bx + 2, base - 1, Color("241a10"))
		_hspan(img, bx, bx + 2, base, Color("241a10"))
		_put(img, bx + 2, base, _warm(Color("241a10"), 0.3))
	# coat skirt — flares from the WAIST, split up the front
	for y in range(17, base - 1):
		var t: float = float(y - 17) / float(base - 18)
		var hw: int = 3 + int(t * 3.0)
		_shaded_row(img, cx - hw, cx + hw, y, coat)
		if y > 18:
			_put(img, cx, y, CLEAR)                     # the split
			_put(img, cx - 1, y, coat.darkened(0.4))
	# torso — shoulders to waist
	_shaded_row(img, cx - 3, cx + 3, 11, coat)          # shoulder slope
	_shaded_row(img, cx - 5, cx + 5, 12, coat)
	for y2 in range(13, 17):
		var t2: float = float(y2 - 13) / 3.0
		var hw2: int = 5 - int(t2 * 2.0)
		_shaded_row(img, cx - hw2, cx + hw2, y2, coat)
	_folds(img, cx - 3, cx + 3, 13, 16, coat, 9, 1)
	_hspan(img, cx - 3, cx + 3, 17, coat.darkened(0.5))   # belt
	_put(img, cx + 3, 17, SILVER)                         # the iron
	# arms — hands at the hips, gloved
	for y3 in range(13, 17):
		_put(img, cx - 5, y3, coat.darkened(0.2))
		_put(img, cx + 5, y3, _warm(coat, 0.12))
	_put(img, cx - 5, 17, coat.darkened(0.35))
	_put(img, cx + 5, 17, coat)
	_put(img, cx - 5, 18, Color("3a2418"))                # gloves
	_put(img, cx + 5, 18, Color("4a2e1c"))
	# neck + kerchief
	_put(img, cx, 10, skin.darkened(0.3))
	_hspan(img, cx - 1, cx + 1, 10, BLOOD)
	# face — jaw lit under the brim shadow
	_hspan(img, cx - 1, cx + 1, 7, skin.darkened(0.55))   # eyes in shadow
	_hspan(img, cx - 1, cx + 1, 8, skin.darkened(0.4))
	_hspan(img, cx - 1, cx + 1, 9, skin.darkened(0.15))   # lit jaw
	_put(img, cx + 1, 9, _warm(skin, 0.1))
	# the hat — wide brim above the shadow
	_hspan(img, cx - 4, cx + 4, 6, INK)
	_put(img, cx - 4, 6, Color("3a2c1c").darkened(0.1))
	_put(img, cx + 4, 6, _warm(Color("3a2c1c"), 0.3))
	_hspan(img, cx - 2, cx + 2, 5, INK)
	_hspan(img, cx - 2, cx + 2, 4, INK)
	_put(img, cx + 2, 4, _warm(Color("3a2c1c"), 0.2))
	_hspan(img, cx - 2, cx + 2, 3, INK)


# ─── the sisters ─────────────────────────────────────────────────

static func _paint_north(img: Image) -> void:
	var cx := 14
	var base := 38
	var shawl := Color("8890a0")
	var dress := Color("5a5a68")
	var skin := Color("d8ccc0")
	_dust_strip(img, base + 1)
	# skirt — flares from the WAIST
	for y in range(22, base + 1):
		var t: float = float(y - 22) / float(base - 22)
		var hw: int = 3 + int(t * 4.0)
		_shaded_row(img, cx - hw, cx + hw, y, dress)
	_folds(img, cx - 4, cx + 4, 24, base - 1, dress, 11, 2)
	_neck_shoulders(img, cx, 14, skin, dress)
	_bodice(img, cx, 16, 21, dress)
	_head6(img, cx, 8, skin)
	for y2 in range(6, 9):                               # hood crown
		_hspan(img, cx - 2, cx + 2, y2, shawl)
	_vspan(img, cx - 3, 8, 15, shawl)                    # hood sides
	_vspan(img, cx + 3, 8, 15, _warm(shawl, 0.1))
	_hspan(img, cx - 4, cx + 4, 15, shawl)               # shawl over shoulders
	_hspan(img, cx - 5, cx + 5, 16, shawl.darkened(0.15))
	# arms out, the net draped between her hands
	for y3 in range(17, 24):
		_put(img, cx - 6, y3, shawl.darkened(0.2))
		_put(img, cx + 6, y3, _warm(shawl, 0.1))
	_put(img, cx - 6, 24, skin)
	_put(img, cx + 6, 24, _warm(skin, 0.1))
	_line(img, cx - 6, 25, cx + 6, 27, SILVER)
	_line(img, cx - 6, 27, cx + 6, 25, SILVER)
	_line(img, cx - 4, 25, cx - 1, 29, SILVER)
	_line(img, cx + 1, 29, cx + 4, 25, SILVER)
	for s in [[3, 30], [5, 18], [23, 24], [25, 12], [2, 8], [24, 36], [7, 38]]:
		_put(img, s[0], s[1], BONE)
		_put(img, s[0], int(s[1]) - 1, Color("f4f0e8"))


static func _paint_east(img: Image) -> void:
	var cx := 14
	var base := 38
	var dress := Color("7a3020")
	var skin := Color("d8b8a0")
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
	for y2 in range(22, base + 1):
		var t2: float = float(y2 - 22) / float(base - 22)
		var hw: int = 3 + int(t2 * 3.0)
		_shaded_row(img, cx - hw, cx + hw, y2, dress)
	_folds(img, cx - 3, cx + 3, 24, base - 1, dress, 13, 2)
	_neck_shoulders(img, cx, 14, skin, dress)
	_bodice(img, cx, 16, 21, dress)
	_hspan(img, cx - 4, cx + 4, 20, dress.darkened(0.3))   # arms folded
	_hspan(img, cx - 4, cx + 4, 21, dress.lightened(0.1))
	_put(img, cx - 4, 20, skin)                            # a hand at each elbow
	_put(img, cx + 4, 21, _warm(skin, 0.1))
	_head6(img, cx, 8, skin)
	_hspan(img, cx - 2, cx + 2, 7, INK)                    # hair pulled tight
	_hspan(img, cx - 1, cx + 1, 8, INK)
	_put(img, cx - 2, 9, INK)
	_put(img, cx + 3, 9, INK)                              # the knot
	_hspan(img, cx + 6, cx + 9, base, SILVER)              # the face-down mirror
	_hspan(img, cx + 6, cx + 9, base - 1, SILVER.darkened(0.35))


static func _paint_south(img: Image) -> void:
	var cx := 12
	var base := 38
	var dress := Color("8a6838")
	var chair := Color("4a3018")
	var skin := Color("d0b898")
	_dust_strip(img, base + 1)
	_line(img, 4, base, 24, base - 3, chair)               # the rocker
	_line(img, 4, base - 3, 24, base, chair)
	_vspan(img, 5, 12, base - 2, chair)                    # chair back
	_vspan(img, 6, 11, base - 2, chair.darkened(0.2))
	_vspan(img, 21, 27, base - 2, chair)                   # front leg
	_head6(img, cx, 10, skin)
	_hspan(img, cx - 1, cx + 1, 9, SILVER)                 # the bun
	_put(img, cx - 2, 10, SILVER)
	_put(img, cx, 8, SILVER)
	_hspan(img, cx - 1, cx + 1, 16, skin.darkened(0.2))    # neck
	_shaded_row(img, cx - 3, cx + 3, 17, dress)            # shoulders
	_shaded_row(img, cx - 4, cx + 4, 18, dress)
	for y in range(19, 27):                                # torso to the lap
		var t: float = float(y - 19) / 8.0
		var hw: int = 4 - int(t)
		_shaded_row(img, cx - hw, cx + hw + int(t * 2.0), y, dress)
	for y2 in range(27, 33):                               # lap, forward
		_shaded_row(img, cx - 3, cx + 7, y2, dress)
	_folds(img, cx - 2, cx + 6, 27, 32, dress, 15, 2)
	_vspan(img, cx + 7, 33, base - 1, dress.darkened(0.25))  # shin
	_put(img, cx + 7, base, Color("241a10"))               # shoe
	_hspan(img, cx - 3, cx + 2, 26, dress.darkened(0.3))   # resting arm
	_put(img, cx - 3, 26, skin)
	_hspan(img, cx + 4, cx + 8, 23, dress.darkened(0.2))   # forearm out
	_put(img, cx + 9, 23, skin)                            # her hand
	_put(img, cx + 10, 23, SILVER)                         # the cup
	_put(img, cx + 10, 22, Color("f4f0e8"))                # the water's light


static func _paint_west(img: Image) -> void:
	var cx := 14
	var base := 38
	var dress := Color("a08858")
	var hair := Color("241814")
	var skin := Color("e0c0a0")
	_dust_strip(img, base + 1)
	# skirt from the waist — wind drifts the hem west
	for y in range(22, base + 1):
		var t: float = float(y - 22) / float(base - 22)
		var hw: int = 3 + int(t * 4.0)
		var lean: int = int(t * 2.0)
		@warning_ignore("integer_division")
		_shaded_row(img, cx - hw - lean, cx + hw - lean / 2, y, dress)
	_folds(img, cx - 5, cx + 3, 24, base - 1, dress, 17, 3)
	_neck_shoulders(img, cx, 14, skin, dress)
	_bodice(img, cx, 16, 21, dress)
	_head6(img, cx, 8, skin)
	_hspan(img, cx - 2, cx + 2, 7, hair)                   # crown
	_hspan(img, cx - 2, cx + 1, 8, hair)                   # swept fringe
	for y2 in range(8, 20):                                # the fall of it
		_put(img, cx - 3, y2, hair)
		if y2 > 10:
			if _h01(4, y2, 3) < 0.7:
				_put(img, cx - 4, y2, hair)
			else:
				_put(img, cx - 4, y2, hair)
	_put(img, cx + 3, 9, hair)                             # a strand past the ear
	_put(img, cx + 3, 10, hair)
	_arm(img, cx - 5, 17, cx, skin, dress, 0)              # left arm hangs
	_put(img, cx + 5, 17, _warm(dress, 0.1))               # right: elbow out
	_put(img, cx + 6, 18, _warm(dress, 0.1))
	_put(img, cx + 6, 19, dress)
	_put(img, cx + 5, 20, skin)                            # hand at the hip
	# the eighth point at her collar — the only violet in the figure
	_put(img, cx, 16, WYRD)
	_put(img, cx - 1, 15, WYRD)
	_put(img, cx + 1, 15, WYRD)
	_put(img, cx, 14, WYRD.lightened(0.3))
