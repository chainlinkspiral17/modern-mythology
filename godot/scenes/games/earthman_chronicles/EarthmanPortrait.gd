extends RefCounted
class_name EarthmanPortrait
## Earthman Chronicles · species-driven NPC portraits.
##
## Astro-Cortex instrument-plate style: void ground, faint panel
## wash, hairline violet frame with amber corner ticks, the figure
## lit like a specimen plate.  Species body plans per species.json
## and the design doc:
##   human_earth       · 1940s Pasadena · side-parted hair, collar+tie
##   kyrindi           · tall-and-blue · high silver collar, song-sigil
##   delvanni          · four-armed rust-red · heavy brow, tusks,
##                       second shoulder line (the four-arm read)
##   kelait            · small, children-shaped, ancient eyes, hooded
##   scarlet_ambiguous · clothed in a light not of Parsa
##
## Deterministic per id — same person, same face, forever.  Named
## specials: jack (goggles up), rocha (glasses + the blue pen),
## yr_kelait_child (smaller still, bare-headed).
##
## Design mirror: scratchpad design_earthman_portraits.py — iterate
## there, port function-by-function.
##
## Usage (preload by path — new class_names miss the first editor
## scan after a pull):
##   const PORTRAIT := preload("res://scenes/games/earthman_chronicles/EarthmanPortrait.gd")
##   tex_rect.texture = PORTRAIT.texture("sara_nai", "kyrindi", Vector2i(80, 100))

const W := 40
const H := 50

const VOID   := Color("0b080e")
const PANEL  := Color("291a33")
const CORTEX := Color("58305f")
const AMBER  := Color("c86020")
const STAR   := Color("f8c848")
const CREAM  := Color("e9d090")
const WHITE  := Color("f0f0f0")
const SILVER := Color("b8bcc8")
const RED    := Color("c02020")

static var _cache: Dictionary = {}


static func texture(pid: String, species: String, size: Vector2i = Vector2i(80, 100)) -> ImageTexture:
	var key := "%s:%s:%d" % [pid, species, size.x]
	if _cache.has(key):
		return _cache[key]
	var img := Image.create(W, H, false, Image.FORMAT_RGBA8)
	img.fill(VOID)
	_plate_wash(img)
	var seed: int = pid.hash()
	match species:
		"kyrindi":            _paint_kyrindi(img, pid, seed)
		"delvanni":           _paint_delvanni(img, pid, seed)
		"kelait":             _paint_kelait(img, pid, seed)
		"scarlet_ambiguous":  _paint_scarlet(img, pid, seed)
		_:                    _paint_human(img, pid, seed)
	_frame(img)
	var out := img.duplicate()
	out.resize(size.x, size.y, Image.INTERPOLATE_NEAREST)
	var tex := ImageTexture.create_from_image(out)
	_cache[key] = tex
	return tex


# ─── plumbing ────────────────────────────────────────────────────

const _BAYER4: Array = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5]


static func _bayer(x: int, y: int) -> float:
	return (float(_BAYER4[posmod(y, 4) * 4 + posmod(x, 4)]) + 0.5) / 16.0


static func _put(img: Image, x: int, y: int, c: Color) -> void:
	if x >= 1 and x < W - 1 and y >= 1 and y < H - 1:
		img.set_pixel(x, y, c)


static func _hspan(img: Image, x0: int, x1: int, y: int, c: Color) -> void:
	for x in range(x0, x1 + 1):
		_put(img, x, y, c)


static func _frame(img: Image) -> void:
	for x in range(W):
		img.set_pixel(x, 0, CORTEX)
		img.set_pixel(x, H - 1, CORTEX)
	for y in range(H):
		img.set_pixel(0, y, CORTEX)
		img.set_pixel(W - 1, y, CORTEX)
	for tick in [[2, 2, 1, 1], [W - 3, 2, -1, 1], [2, H - 3, 1, -1], [W - 3, H - 3, -1, -1]]:
		var tx: int = tick[0]
		var ty: int = tick[1]
		_put(img, tx, ty, AMBER)
		_put(img, tx + tick[2], ty, AMBER)
		_put(img, tx, ty + tick[3], AMBER)


static func _plate_wash(img: Image) -> void:
	for y in range(1, H - 1):
		var t: float = 1.0 - absf(float(y) - float(H) * 0.40) / (float(H) * 0.55)
		for x in range(1, W - 1):
			var tx: float = 1.0 - absf(float(x) - float(W) / 2.0) / (float(W) * 0.60)
			if t * tx * 0.8 > _bayer(x, y):
				img.set_pixel(x, y, PANEL)


## Shared bust: shoulders, neck, rounded head.  Returns geometry.
static func _base_figure(img: Image, skin: Color, skin_sh: Color, garment: Color,
		head_w: int, head_top: int, head_h: int, narrow_jaw: bool = true) -> Dictionary:
	@warning_ignore("integer_division")
	var cx: int = W / 2
	@warning_ignore("integer_division")
	var head_left: int = cx - head_w / 2
	var head_right: int = head_left + head_w
	var head_bot: int = mini(head_top + head_h, H - 10)
	for y in range(head_bot + 2, H - 2):
		var widen: int = mini(15, 6 + (y - head_bot - 2) * 2)
		_hspan(img, cx - widen, cx + widen, y, garment)
	for y2 in range(head_bot - 1, head_bot + 3):
		_hspan(img, cx - 3, cx + 3, y2, skin_sh)
	for y3 in range(head_top, head_bot):
		var x0: int = head_left
		var x1: int = head_right
		if y3 == head_top:
			x0 += 3; x1 -= 3
		elif y3 == head_top + 1:
			x0 += 1; x1 -= 1
		var fb: int = head_bot - 1 - y3
		if narrow_jaw:
			if fb == 0:
				x0 += 4; x1 -= 4
			elif fb == 1:
				x0 += 2; x1 -= 2
			elif fb == 2:
				x0 += 1; x1 -= 1
		else:
			if fb == 0:
				x0 += 2; x1 -= 2
			elif fb == 1:
				x0 += 1; x1 -= 1
		for x in range(x0, x1):
			if x >= x1 - 3 and fb > 2:
				_put(img, x, y3, skin_sh)
			else:
				_put(img, x, y3, skin)
	return {"cx": cx, "hl": head_left, "hr": head_right, "hb": head_bot}


static func _eyes(img: Image, cx: int, eye_y: int, eye_dx: int,
		eye_c: Color, hi_c: Color, brow_c: Color, wide: bool = false) -> void:
	for side in [-1, 1]:
		var ex: int = cx + side * eye_dx - 1
		_hspan(img, ex, ex + (2 if wide else 1) + 1, eye_y, eye_c)
		_put(img, ex + 1, eye_y, hi_c)
		_hspan(img, ex, ex + 2, eye_y - 2, brow_c)


# ─── species painters ────────────────────────────────────────────

static func _paint_human(img: Image, pid: String, seed: int) -> void:
	var skins: Array = [Color("e8c8a0"), Color("d4a878"), Color("c09068")]
	var skin: Color = skins[(seed >> 15) % 3]
	var skin_sh := skin.darkened(0.22)
	var hairs: Array = [Color("3a2a1c"), Color("6a4a2c"), Color("222020"), Color("8a8078")]
	var hair: Color = hairs[(seed >> 17) % 4]
	var garment := Color("4a3c30") if (seed >> 5) % 2 == 0 else Color("3a4250")
	var head_w: int = 15 + (seed & 0x3)
	var head_top := 9
	var head_h: int = 19 + ((seed >> 3) & 0x3)
	var g := _base_figure(img, skin, skin_sh, garment, head_w, head_top, head_h)
	var cx: int = g["cx"]
	var hl: int = g["hl"]
	var hr: int = g["hr"]
	var hb: int = g["hb"]
	var part: int = cx - 2 if (seed >> 9) % 2 == 0 else cx + 2
	for y in range(head_top - 1, head_top + 4):
		_hspan(img, hl, hr - 1, y, hair)
	_hspan(img, hl, hr - 1, head_top + 4, hair.darkened(0.3))
	for x in range(part, part + 2):
		_put(img, x, head_top + 1, skin_sh)
	var eye_y: int = head_top + 8
	var eye_dx: int = 3 + ((seed >> 6) & 0x1)
	_eyes(img, cx, eye_y, eye_dx, Color("2a2420"), WHITE, skin_sh)
	_put(img, cx, eye_y + 4, skin_sh)
	_hspan(img, cx - 2, cx + 2, hb - 5, skin_sh)
	if (seed >> 11) % 4 == 0:
		_hspan(img, cx - 2, cx + 2, hb - 7, hair.darkened(0.1))
	_hspan(img, cx - 6, cx + 6, hb + 3, CREAM)
	var tie: Color = RED if (seed >> 13) % 2 == 0 else garment.darkened(0.3)
	_put(img, cx, hb + 4, tie)
	_put(img, cx, hb + 5, tie)
	if pid == "rocha":
		var lens := Color("222020")
		for side in [-1, 1]:
			var ex: int = cx + side * eye_dx
			for d in [[-1, -1], [0, -1], [1, -1], [-2, 0], [2, 0], [-1, 1], [0, 1], [1, 1]]:
				_put(img, ex + int(d[0]), eye_y + int(d[1]), lens)
		_hspan(img, cx - 1, cx + 1, eye_y - 1, lens)
		_put(img, cx + 5, hb + 4, Color("3868c8"))   # the blue pen
	if pid == "jack":
		# goggles pushed up on the forehead
		_hspan(img, hl + 3, hr - 4, head_top + 3, Color("6a5a30"))
		_put(img, cx - 3, head_top + 3, STAR)
		_put(img, cx + 3, head_top + 3, STAR)


static func _paint_kyrindi(img: Image, _pid: String, seed: int) -> void:
	var skins: Array = [Color("7a94c8"), Color("8ea6d8"), Color("6a82b8")]
	var skin: Color = skins[(seed >> 15) % 3]
	var skin_sh := skin.darkened(0.25)
	var garment := Color("2a3450")
	var head_w: int = 12 + (seed & 0x3)
	var head_top := 6
	var head_h: int = 24 + ((seed >> 3) & 0x3)
	var g := _base_figure(img, skin, skin_sh, garment, head_w, head_top, head_h)
	var cx: int = g["cx"]
	var hr: int = g["hr"]
	var hb: int = g["hb"]
	var crest := skin.darkened(0.4)
	if (seed >> 9) % 2 == 0:
		for i in range(6):
			@warning_ignore("integer_division")
			_put(img, cx - 2 + i / 2, head_top - 2 - i / 3, crest)
			@warning_ignore("integer_division")
			_put(img, cx + 1 + i / 2, head_top - 1 - i / 3, crest)
	else:
		for y in range(head_top + 2, hb + 6):
			_put(img, hr, y, crest)
			if y % 3 == 0:
				_put(img, hr + 1, y, crest)
	var eye_y: int = head_top + 10
	_eyes(img, cx, eye_y, 3, Color("18203a"), SILVER, skin_sh)
	_put(img, cx, eye_y + 5, skin_sh)
	_hspan(img, cx - 1, cx + 1, hb - 5, skin_sh)
	_hspan(img, cx - 5, cx + 5, hb + 2, SILVER)
	_hspan(img, cx - 6, cx + 6, hb + 3, SILVER)
	_hspan(img, cx - 7, cx + 7, hb + 4, SILVER.darkened(0.3))
	_put(img, cx, hb + 1, STAR)   # the song-sigil at the throat


static func _paint_delvanni(img: Image, _pid: String, seed: int) -> void:
	var skins: Array = [Color("b06038"), Color("a05430"), Color("c07048")]
	var skin: Color = skins[(seed >> 15) % 3]
	var skin_sh := skin.darkened(0.25)
	var garments: Array = [Color("4a3424"), Color("3a3a2c"), Color("55402a")]
	var garment: Color = garments[(seed >> 7) % 3]
	var head_w: int = 18 + (seed & 0x3)
	var head_top := 10
	var head_h: int = 18 + ((seed >> 3) & 0x3)
	var g := _base_figure(img, skin, skin_sh, garment, head_w, head_top, head_h, false)
	var cx: int = g["cx"]
	var hl: int = g["hl"]
	var hr: int = g["hr"]
	var hb: int = g["hb"]
	if (seed >> 10) % 2 == 0:   # topknot
		var knot := Color("2a1a10")
		_hspan(img, cx - 1, cx + 1, head_top - 1, knot)
		_hspan(img, cx - 1, cx + 1, head_top - 2, knot)
		_put(img, cx, head_top - 3, knot)
	var eye_y: int = head_top + 8
	_hspan(img, hl + 2, hr - 3, eye_y - 3, skin_sh)
	_hspan(img, hl + 2, hr - 3, eye_y - 2, skin.darkened(0.35))
	if (seed >> 12) % 3 == 0:   # war-paint band
		_hspan(img, hl + 2, hr - 3, eye_y + 1, Color("7a3020").darkened(0.15))
	_eyes(img, cx, eye_y, 4, Color("301810"), AMBER, skin.darkened(0.35))
	_put(img, cx, eye_y + 4, skin_sh)
	_hspan(img, cx - 2, cx + 2, hb - 4, skin.darkened(0.35))
	if (seed >> 20) % 3 == 1:   # a kept scar
		for i in range(4):
			_put(img, hl + 4 + i, eye_y + 2 + i, skin.darkened(0.45))
	var tusk := Color("e8dcc0")
	var tlen: int = 2 + ((seed >> 22) & 0x1)
	for t in range(tlen):
		_put(img, cx - 4, hb - 4 - t, tusk)
		_put(img, cx + 4, hb - 4 - t, tusk)
	# the second pair of shoulders — the four-arm read
	var sh_y: int = hb + 6
	_hspan(img, cx - 15, cx - 9, sh_y, skin)
	_hspan(img, cx + 9, cx + 15, sh_y, skin)
	_hspan(img, cx - 15, cx - 10, sh_y + 1, skin_sh)
	_hspan(img, cx + 10, cx + 15, sh_y + 1, skin_sh)
	for i2 in range(12):   # chest strap
		@warning_ignore("integer_division")
		_put(img, cx - 6 + i2, hb + 3 + i2 / 3, garment.darkened(0.4))


static func _paint_kelait(img: Image, pid: String, seed: int) -> void:
	var skins: Array = [Color("c8b498"), Color("b8a488"), Color("d0c0a8")]
	var skin: Color = skins[(seed >> 15) % 3]
	var skin_sh := skin.darkened(0.2)
	var garments: Array = [Color("5a5048"), Color("4c5248"), Color("605444")]
	var garment: Color = garments[(seed >> 7) % 3]
	# Small — the frame mostly holds quiet.  Children smaller still.
	var child: bool = pid == "yr_kelait_child"
	var head_w: int = (10 if child else 12) + (seed & 0x1)
	var head_top: int = 20 if child else 16
	var head_h: int = 11 if child else 14
	var g := _base_figure(img, skin, skin_sh, garment, head_w, head_top, head_h)
	var cx: int = g["cx"]
	var hl: int = g["hl"]
	var hr: int = g["hr"]
	var hb: int = g["hb"]
	var hood := garment.darkened(0.15)
	if not child:
		for y in range(head_top - 3, hb + 2):
			var t: int = y - (head_top - 3)
			@warning_ignore("integer_division")
			var reach: int = 2 + mini(3, t / 3)
			_hspan(img, hl - reach, hl - 1, y, hood)
			_hspan(img, hr, hr + reach - 1, y, hood)
		for x in range(hl - 2, hr + 2):
			_put(img, x, head_top - 3, hood)
			_put(img, x, head_top - 2, hood)
		_hspan(img, hl, hr - 1, head_top - 1, hood.darkened(0.25))
	else:
		_hspan(img, hl, hr - 1, head_top - 1, skin.darkened(0.35))
	# ancient eyes — large, round, lit
	var eye_y: int = head_top + 6
	for side in [-1, 1]:
		var ex: int = cx + side * 3
		var dark := Color("2a2018")
		_put(img, ex, eye_y, dark)
		_put(img, ex + 1, eye_y, dark)
		_put(img, ex, eye_y + 1, dark)
		_put(img, ex + 1, eye_y + 1, dark)
		_put(img, ex, eye_y, CREAM)
	_hspan(img, cx - 1, cx + 1, hb - 3, skin_sh)
	_hspan(img, cx - 2, cx + 2, H - 6, skin)
	_hspan(img, cx - 2, cx + 2, H - 5, skin_sh)


static func _paint_scarlet(img: Image, _pid: String, _seed: int) -> void:
	# clothed in a light not of Parsa
	for y in range(1, H - 1):
		for x in range(1, W - 1):
			var dx: float = (float(x) - float(W) / 2.0) / (float(W) * 0.55)
			var dy: float = (float(y) - float(H) * 0.42) / (float(H) * 0.50)
			var gl: float = maxf(0.0, 1.0 - sqrt(dx * dx + dy * dy))
			if gl * 0.7 > _bayer(x, y):
				img.set_pixel(x, y, Color("8a2438").darkened((1.0 - gl) * 0.4))
	var skin := Color("f4ead8")
	var skin_sh := skin.darkened(0.12)
	var garment := Color("c03048")
	var g := _base_figure(img, skin, skin_sh, garment, 13, 9, 20)
	var cx: int = g["cx"]
	var hl: int = g["hl"]
	var hr: int = g["hr"]
	var hb: int = g["hb"]
	var head_top := 9
	for y in range(head_top - 2, hb + 8):
		_put(img, hl - 1, y, CREAM)
		_put(img, hr, y, CREAM)
		if y < head_top + 4:
			_hspan(img, hl, hr - 1, y, CREAM)
	var eye_y: int = head_top + 8
	_put(img, cx - 3, eye_y, Color("6a1828"))
	_put(img, cx + 3, eye_y, Color("6a1828"))
	_hspan(img, cx - 1, cx + 1, hb - 5, skin_sh)
	for s in [[cx - 6, head_top - 4], [cx, head_top - 6], [cx + 6, head_top - 4]]:
		_put(img, s[0], s[1], STAR)
