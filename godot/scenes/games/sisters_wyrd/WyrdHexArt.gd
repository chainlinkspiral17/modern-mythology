extends RefCounted
class_name WyrdHexArt
## THE SISTERS WYRD · terrain-inked hex tiles.
##
## The design doc promises hexes "big as playing cards, terrain-
## inked like cover art, not like a wargame."  This paints them: a
## deterministic 40×46 pixel tile per (terrain, address hash),
## masked to a pointy-top hexagon, upscaled nearest-neighbor to the
## crawl's on-screen hex size.  Paperback inks only — the sister's
## trade.
##
## No RNG anywhere: placement reads _h01(x, y, seed), so the same
## hex is inked the same way forever.  The territory is not
## generated.  It is WOVEN, and the loom does not change its mind.
##
## Design mirror: scratchpad design_wyrd_hexes.py (session tool) —
## visuals were iterated there and ported function-by-function.
##
## Usage (preload by path — new class_names miss the first editor
## scan after a pull):
##   const HEX_ART := preload("res://scenes/games/sisters_wyrd/WyrdHexArt.gd")
##   draw_texture(HEX_ART.tile(terrain, hash), pos)

const TW := 40
const TH := 46

const INK    := Color("201410")
const DUST   := Color("c8a878")
const BONE   := Color("e8dcc0")
const BLOOD  := Color("7a3020")
const SILVER := Color("b8bcc8")
const WYRD   := Color("8a58a8")
const SCRUB  := Color("4a5a3a")

static var _cache: Dictionary = {}


static func tile(terrain: String, seed: int, out_size: Vector2i = Vector2i(160, 184)) -> ImageTexture:
	var key := "%s:%d:%d" % [terrain, seed, out_size.x]
	if _cache.has(key):
		return _cache[key]
	var img := Image.create(TW, TH, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	match terrain:
		"dust":     _paint_dust(img, seed)
		"bone":     _paint_bone(img, seed)
		"scrub":    _paint_scrub(img, seed)
		"mesa":     _paint_mesa(img, seed)
		"salt":     _paint_salt(img, seed)
		"gallows":  _paint_gallows(img, seed)
		"township": _paint_township(img, seed)
		_:          _paint_dust(img, seed)
	_mask_hex(img)
	img.resize(out_size.x, out_size.y, Image.INTERPOLATE_NEAREST)
	var tex := ImageTexture.create_from_image(img)
	_cache[key] = tex
	return tex


# ─── plumbing ────────────────────────────────────────────────────

const _BAYER4: Array = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5]


static func _bayer(x: int, y: int) -> float:
	return (float(_BAYER4[posmod(y, 4) * 4 + posmod(x, 4)]) + 0.5) / 16.0


static func _h01(x: int, y: int, s: int) -> float:
	var n: int = x * 374761393 + y * 668265263 + s * 1442695041
	n = (n ^ (n >> 13)) * 1274126177
	n = n ^ (n >> 16)
	return float(n & 0xFFFF) / 65536.0


static func _put(img: Image, x: int, y: int, c: Color) -> void:
	if x >= 0 and x < TW and y >= 0 and y < TH:
		img.set_pixel(x, y, c)


static func _hspan(img: Image, x0: int, x1: int, y: int, c: Color) -> void:
	for x in range(x0, x1 + 1):
		_put(img, x, y, c)


static func _vspan(img: Image, x: int, y0: int, y1: int, c: Color) -> void:
	for y in range(y0, y1 + 1):
		_put(img, x, y, c)


static func _rect(img: Image, x: int, y: int, rw: int, rh: int, c: Color) -> void:
	for yy in range(y, y + rh):
		for xx in range(x, x + rw):
			_put(img, xx, yy, c)


static func _fill(img: Image, c: Color) -> void:
	for y in range(TH):
		for x in range(TW):
			img.set_pixel(x, y, c)


static func _in_hex(x: int, y: int) -> bool:
	var half_w := float(TW) / 2.0
	var r := float(TH) / 2.0
	var dx: float = absf(float(x) + 0.5 - half_w)
	var dy: float = absf(float(y) + 0.5 - r)
	if dx > half_w:
		return false
	return dy <= r - (r * 0.5) * (dx / half_w)


static func _mask_hex(img: Image) -> void:
	for y in range(TH):
		for x in range(TW):
			if not _in_hex(x, y):
				img.set_pixel(x, y, Color(0, 0, 0, 0))


# ─── terrains ────────────────────────────────────────────────────

static func _paint_dust(img: Image, seed: int) -> void:
	_fill(img, DUST)
	var streak := DUST.darkened(0.14)
	var streak2 := DUST.darkened(0.07)
	for k in range(4):
		var base_y: int = 7 + k * 10 + int(_h01(k, 0, seed) * 5.0)
		for x in range(TW):
			var y: int = base_y + int(sin(float(x) * 0.30 + float(k) * 2.1 + float(seed % 7)) * 1.8)
			_put(img, x, y, streak if k % 2 == 0 else streak2)
			if _h01(x, k, seed + 3) < 0.5:
				_put(img, x, y + 1, streak2)
	for y2 in range(TH):
		for x2 in range(TW):
			if _h01(x2, y2, seed + 9) < 0.02:
				_put(img, x2, y2, DUST.darkened(0.3))
	if seed % 3 == 0:
		var cx: int = 10 + int(_h01(1, 2, seed) * 20.0)
		var cy: int = 30 + int(_h01(2, 1, seed) * 8.0)
		for a in range(10):
			var ang: float = float(a) * 0.63
			_put(img, cx + int(cos(ang) * 2.5), cy + int(sin(ang) * 2.5), DUST.darkened(0.35))


static func _paint_bone(img: Image, seed: int) -> void:
	_fill(img, BONE)
	for y in range(TH):
		for x in range(TW):
			@warning_ignore("integer_division")
			if _h01(x / 3, y / 3, seed + 1) < 0.25:
				_put(img, x, y, BONE.darkened(0.08))
	for k in range(2 + seed % 2):
		var cx: int = 8 + int(_h01(k, 5, seed) * 24.0)
		var cy: int = 16 + int(_h01(5, k, seed) * 18.0)
		var rr: int = 4 + int(_h01(k, k, seed) * 3.0)
		for t in range(18):
			var a: float = PI + float(t) * PI / 17.0
			_put(img, cx + int(cos(a) * float(rr)), cy + int(sin(a) * float(rr) * 0.8), INK)
		_hspan(img, cx - rr, cx + rr, cy + 1, BONE.darkened(0.18))
	if seed % 4 == 1:
		var sx: int = 12 + int(_h01(3, 3, seed) * 14.0)
		var sy: int = 26 + int(_h01(4, 4, seed) * 8.0)
		_rect(img, sx, sy, 5, 4, BONE.lightened(0.3))
		_put(img, sx + 1, sy + 1, INK)
		_put(img, sx + 3, sy + 1, INK)
		_hspan(img, sx + 1, sx + 3, sy + 3, BONE.darkened(0.3))


static func _paint_scrub(img: Image, seed: int) -> void:
	_fill(img, DUST.darkened(0.06))
	var sc_lt := SCRUB.lightened(0.15)
	var sc_dk := SCRUB.darkened(0.25)
	for k in range(9):
		var cx: int = 4 + int(_h01(k, 11, seed) * 32.0)
		var cy: int = 6 + int(_h01(11, k, seed) * 34.0)
		if not _in_hex(cx, cy):
			continue
		_hspan(img, cx - 1, cx + 1, cy, SCRUB)
		_hspan(img, cx - 2, cx + 2, cy + 1, SCRUB)
		_put(img, cx, cy - 1, sc_lt)
		_put(img, cx - 1 + int(_h01(k, 1, seed) * 3.0), cy - 1, sc_lt)
		_hspan(img, cx - 1, cx + 1, cy + 2, sc_dk)
	for y in range(TH):
		for x in range(TW):
			if _h01(x, y, seed + 17) < 0.015:
				_put(img, x, y, DUST.darkened(0.3))


static func _paint_mesa(img: Image, seed: int) -> void:
	var dark := Color("2c2018")
	var ground := Color("443626")
	_fill(img, dark)
	for y in range(30):
		var t: float = float(y) / 30.0
		for x in range(TW):
			if 1.0 - t > _bayer(x, y):
				_put(img, x, y, BLOOD)
	for y2 in range(31, TH):
		_hspan(img, 0, TW - 1, y2, ground)
	_hspan(img, 0, TW - 1, 31, ground.darkened(0.3))
	var butte := Color("181008")
	var top: int = 12 + int(_h01(0, 1, seed) * 5.0)
	var bl: int = 10 + int(_h01(1, 0, seed) * 10.0)
	var bw: int = 8 + int(_h01(2, 2, seed) * 8.0)
	var br: int = bl + bw
	for y3 in range(top, 32):
		@warning_ignore("integer_division")
		var spread: int = mini(5, (y3 - top) / 2)
		_hspan(img, maxi(1, bl - spread), mini(TW - 2, br + spread), y3, butte)
	if seed % 3 != 0:
		var b2l: int = (bl + 18) % 30 + 2
		var b2t: int = top + 6
		for y4 in range(b2t, 32):
			@warning_ignore("integer_division")
			var spread2: int = mini(3, (y4 - b2t) / 2)
			_hspan(img, maxi(1, b2l - spread2), mini(TW - 2, b2l + 5 + spread2), y4,
					ground.darkened(0.45))
	_put(img, 4 + int(_h01(6, 6, seed) * 30.0), 3 + int(_h01(7, 7, seed) * 5.0), BONE)


static func _paint_salt(img: Image, seed: int) -> void:
	var pan := Color("d8d8d0")
	_fill(img, pan)
	var crack := pan.darkened(0.35)
	for k in range(5):
		var x: int = 4 + int(_h01(k, 21, seed) * 32.0)
		var y: int = 2 + int(_h01(21, k, seed) * 10.0)
		for step in range(16):
			_put(img, x, y, crack)
			x += int(_h01(x, y, seed + k) * 3.0) - 1
			y += 1 if _h01(y, x, seed + k) < 0.75 else 0
			if x < 1 or x > TW - 2 or y > TH - 2:
				break
	for k2 in range(4):
		var x2: int = 6 + int(_h01(k2, 31, seed) * 28.0)
		var y2: int = 14 + int(_h01(31, k2, seed) * 24.0)
		for step2 in range(6):
			_put(img, x2, y2, crack)
			x2 += 1 if _h01(x2, y2, seed + 40 + k2) < 0.5 else -1
			y2 += int(_h01(y2, x2, seed + 41 + k2) * 2.0)
	for y3 in range(TH):
		for x3 in range(TW):
			@warning_ignore("integer_division")
			if _h01(x3 / 4, y3 / 4, seed + 5) < 0.2 and 0.5 > _bayer(x3, y3):
				_put(img, x3, y3, pan.lightened(0.35))


static func _paint_gallows(img: Image, seed: int) -> void:
	var base := Color("5a4838")
	_fill(img, base.darkened(0.15))
	for y in range(10):
		for x in range(TW):
			if (1.0 - float(y) / 10.0) * 0.5 > _bayer(x, y):
				_put(img, x, y, base.darkened(0.4))
	for k in range(4):
		var tx: int = 6 + int(_h01(k, 51, seed) * 29.0)
		var ty: int = 10 + int(_h01(51, k, seed) * 9.0)
		var th_: int = 16 + int(_h01(k, 52, seed) * 10.0)
		_vspan(img, tx, ty, mini(TH - 4, ty + th_), INK)
		@warning_ignore("integer_division")
		_vspan(img, tx + 1, ty + th_ / 2, mini(TH - 4, ty + th_), base.darkened(0.5))
		for b in range(4):
			var by: int = ty + 1 + b * 3
			var side: int = 1 if _h01(b, tx, seed) < 0.5 else -1
			var blen: int = 3 + int(_h01(b, tx + 1, seed) * 3.0)
			for i in range(blen):
				@warning_ignore("integer_division")
				_put(img, tx + side * i, by - (i + 1) / 2, INK)
	var gx: int = 6 + int(_h01(0, 51, seed) * 29.0)
	var gy: int = 10 + int(_h01(51, 0, seed) * 9.0)
	var rope := BONE.darkened(0.2)
	_hspan(img, gx, gx + 7, gy, INK)
	_put(img, gx + 2, gy + 1, INK)
	_vspan(img, gx + 7, gy + 1, gy + 5, rope)
	_put(img, gx + 6, gy + 6, rope)
	_put(img, gx + 8, gy + 6, rope)
	_put(img, gx + 7, gy + 7, rope)
	for y2 in range(TH - 12, TH):
		for x2 in range(TW):
			if _h01(x2, y2, seed + 61) < 0.05:
				_put(img, x2, y2, base.darkened(0.45))


static func _paint_township(img: Image, seed: int) -> void:
	_fill(img, DUST)
	var street := DUST.darkened(0.22)
	var sy: int = 27 + int(_h01(7, 7, seed) * 4.0)
	for y in range(sy, sy + 4):
		_hspan(img, 0, TW - 1, y, street)
	_hspan(img, 0, TW - 1, sy + 4, DUST.darkened(0.12))
	var n: int = 3 + seed % 2
	for k in range(n):
		@warning_ignore("integer_division")
		var hx: int = 4 + k * (30 / n) + int(_h01(k, 71, seed) * 3.0)
		var hw: int = 5 + int(_h01(71, k, seed) * 3.0)
		var hh: int = 5 + int(_h01(k, 72, seed) * 3.0)
		var hy: int = sy - hh
		_rect(img, hx, hy, hw, hh, BONE)
		_hspan(img, hx - 1, hx + hw, hy - 1, INK)
		_hspan(img, hx, hx + hw - 1, hy - 2, INK)
		_vspan(img, hx + 1, sy - 3, sy - 1, INK)
		var wlit: bool = _h01(k, 73, seed) < 0.4
		_put(img, hx + hw - 2, hy + 2, BLOOD if wlit else BONE.darkened(0.4))
	if seed % 3 == 2:
		var wx: int = 30 + int(_h01(9, 9, seed) * 5.0)
		_rect(img, wx, sy - 12, 4, 4, BONE.darkened(0.15))
		_hspan(img, wx, wx + 3, sy - 13, INK)
		_vspan(img, wx, sy - 8, sy - 1, INK)
		_vspan(img, wx + 3, sy - 8, sy - 1, INK)
	for y2 in range(sy + 5, TH):
		for x2 in range(TW):
			if _h01(x2, y2, seed + 81) < 0.03:
				_put(img, x2, y2, street)
