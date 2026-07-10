extends RefCounted
class_name EarthmanPortrait
## Earthman Chronicles · character plates · v4.1 FULL FIGURES, refined.
##
## Per the reference boards: painterly pixel art, silhouette-first.
## At slowstick scale identity is COSTUME + POSE + HEIGHT — faces
## are shadow with a glint.  Each character stands full-figure in a
## dithered Parsan dusk: a 7-stop violet-to-amber sky, two moons,
## distant butte silhouettes, rust dunes with speckle and ridge
## light.  The refinement pass (user: "too blocky and basic"):
##
##   · 5-value material shading with Bayer-dithered transitions
##     (deep shadow / mid / core / half-light / warm rim)
##   · organic silhouettes — sloped shoulders, tapered limbs,
##     rounded crowns, robe hems that jitter
##   · fabric fold lines inside every garment
##
## Species by silhouette: humans mid-height (jacket, boots, holster
## glint) · Kyrindi tall slender robes, silver collar, pale-blue
## backswept head · Delvanni massive, FOUR ARMS visible, greatsword
## hilt over the shoulder · Kelait small hooded cones, cream eyes
## lit in the hood shadow · the Scarlet Woman pale in red, hair
## streaming as light, floating with no contact shadow.
##
## Chrome: corner brackets + the spectral ID stamp.  Deterministic
## per id.  Named specials: jack (goggles up), rocha (glasses
## glint, notebook, blue pen, long coat), yr_kelait_child.
##
## Canvas 36×60 · display at 2x (72×120).
##
## Lockstep mirror: godot/tools/sprites/preview_earthman_portrait.py
## — edit both together, preview before pushing.
##
## Usage (preload by path — new class_names miss the first editor
## scan after a pull):
##   const PORTRAIT := preload("res://scenes/games/earthman_chronicles/EarthmanPortrait.gd")
##   tex_rect.texture = PORTRAIT.texture("sara_nai", "kyrindi", Vector2i(72, 120))

const W := 36
const H := 60

const VOID   := Color("100a16")
const CORTEX := Color("58305f")
const AMBER  := Color("c86020")
const STAR   := Color("f8c848")
const CREAM  := Color("e9d090")
const WHITE  := Color("f0f0f0")
const SILVER := Color("b8bcc8")
const RED    := Color("c02020")

const SKY: Array = [Color("100a16"), Color("1e1022"), Color("331632"),
		Color("58223a"), Color("7e3038"), Color("a85038"), Color("d08448")]
const BUTTE     := Color("2c1220")
const BUTTE2    := Color("451a28")
const GROUND    := Color("6a3024")
const GROUND_DK := Color("3a1a16")
const GROUND_LT := Color("8a4430")

const HORIZON := 44
const BASE := 54

static var _cache: Dictionary = {}


static func texture(pid: String, species: String, size: Vector2i = Vector2i(72, 120)) -> ImageTexture:
	var key := "%s:%s:%d" % [pid, species, size.x]
	if _cache.has(key):
		return _cache[key]
	var seed: int = pid.hash()
	var img := Image.create(W, H, false, Image.FORMAT_RGBA8)
	img.fill(VOID)
	_dusk_bg(img, seed)
	match species:
		"kyrindi":            _paint_kyrindi(img, pid, seed)
		"delvanni":           _paint_delvanni(img, pid, seed)
		"kelait":             _paint_kelait(img, pid, seed)
		"scarlet_ambiguous":  _paint_scarlet(img, pid, seed)
		_:                    _paint_human(img, pid, seed)
	_plate_chrome(img, seed)
	var out := img.duplicate()
	out.resize(size.x, size.y, Image.INTERPOLATE_NEAREST)
	var tex := ImageTexture.create_from_image(out)
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
	if x >= 0 and x < W and y >= 0 and y < H:
		img.set_pixel(x, y, c)


static func _hspan(img: Image, x0: int, x1: int, y: int, c: Color) -> void:
	for x in range(x0, x1 + 1):
		_put(img, x, y, c)


static func _vspan(img: Image, x: int, y0: int, y1: int, c: Color) -> void:
	for y in range(y0, y1 + 1):
		_put(img, x, y, c)


static func _warm(c: Color, f: float = 0.22) -> Color:
	var l := c.lightened(f)
	return Color(minf(1.0, l.r * 1.10), l.g, l.b * 0.90, 1.0)


## One garment row with the 5-value ramp: deep shadow, dithered
## mid, core, dithered half-light, warm rim.
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


## Vertical fabric fold lines with breaks.
static func _folds(img: Image, x0: int, x1: int, y0: int, y1: int,
		core: Color, seed: int, n: int) -> void:
	var fold_c := core.darkened(0.30)
	for k in range(n):
		var fx: int = x0 + 2 + int(_h01(k, 5, seed) * float(maxi(1, x1 - x0 - 3)))
		for y in range(y0 + 1, y1):
			if _h01(fx, y, seed + k) < 0.75:
				_put(img, fx, y, fold_c)


# ─── the dusk plate ──────────────────────────────────────────────

static func _dusk_bg(img: Image, seed: int) -> void:
	for y in range(HORIZON):
		var t: float = float(y) / float(HORIZON)
		var f: float = t * float(SKY.size() - 1)
		var i: int = mini(int(f), SKY.size() - 2)
		for x in range(W):
			img.set_pixel(x, y, SKY[i + 1] if (f - float(i)) > _bayer(x, y) else SKY[i])
	for y2 in range(18):
		for x2 in range(W):
			if _h01(x2, y2, seed) < 0.012:
				img.set_pixel(x2, y2, SILVER)
	for dx in range(-2, 3):
		for dy in range(-2, 3):
			if dx * dx + dy * dy <= 4:
				_put(img, 7 + dx, 7 + dy, CREAM)
	_put(img, 6, 6, WHITE)
	_put(img, 13, 11, SILVER)
	_put(img, 14, 11, SILVER)
	_put(img, 13, 12, SILVER)
	# distant buttes — flat-topped silhouettes on the horizon
	var b1x: int = 2 + int(_h01(1, 9, seed) * 8.0)
	for y3 in range(HORIZON - 7, HORIZON):
		@warning_ignore("integer_division")
		var spread: int = mini(3, (y3 - (HORIZON - 7)) / 2)
		_hspan(img, b1x - spread, b1x + 5 + spread, y3, BUTTE)
	var b2x: int = 24 + int(_h01(9, 1, seed) * 8.0)
	for y4 in range(HORIZON - 4, HORIZON):
		@warning_ignore("integer_division")
		var spread2: int = mini(2, (y4 - (HORIZON - 4)) / 2)
		_hspan(img, b2x - spread2, b2x + 3 + spread2, y4, BUTTE2)
	# ground
	for y5 in range(HORIZON, H):
		var c: Color = GROUND if y5 < BASE else GROUND_DK
		for x3 in range(W):
			img.set_pixel(x3, y5, c)
	for k in range(3):
		var ry: int = HORIZON + 2 + k * 3 + int(_h01(k, 3, seed) * 2.0)
		var rx: int = int(_h01(3, k, seed) * 20.0)
		_hspan(img, rx, rx + 10 + k * 4, ry, GROUND_LT)
		_hspan(img, rx + 2, rx + 8 + k * 4, ry + 1, GROUND_LT.darkened(0.15))
	for y6 in range(HORIZON + 1, H):
		for x4 in range(W):
			if _h01(x4, y6, seed + 31) < 0.05:
				img.set_pixel(x4, y6, GROUND.darkened(0.25))
			elif _h01(x4, y6, seed + 32) < 0.03:
				img.set_pixel(x4, y6, GROUND_LT)
	_hspan(img, 0, W - 1, HORIZON, GROUND.darkened(0.35))
	for x5 in range(W):
		if _bayer(x5, HORIZON - 1) < 0.5:
			img.set_pixel(x5, HORIZON - 1, SKY[6])


static func _plate_chrome(img: Image, seed: int) -> void:
	for br in [[1, 1, 1, 1], [W - 2, 1, -1, 1], [1, H - 2, 1, -1], [W - 2, H - 2, -1, -1]]:
		var cx0: int = br[0]
		var cy0: int = br[1]
		for i in range(4):
			img.set_pixel(cx0 + int(br[2]) * i, cy0, CORTEX)
			img.set_pixel(cx0, cy0 + int(br[3]) * i, CORTEX)
	var code_cols: Array = [AMBER, STAR, SILVER, CORTEX, Color("58a068"), RED]
	for i2 in range(6):
		var c: Color = code_cols[(seed >> (i2 * 4)) % code_cols.size()]
		for t in range(2):
			img.set_pixel(W - 15 + i2 * 2 + t, 2, c)


static func _contact_shadow(img: Image, cx: int, half_w: int) -> void:
	for pair in [[1, half_w], [2, half_w - 2]]:
		var r: int = pair[0]
		var hw: int = pair[1]
		for x in range(cx - hw, cx + hw + 1):
			if _bayer(x, BASE + r) < (0.75 - float(r) * 0.2):
				_put(img, x, BASE + r, GROUND_DK)


# ─── figures ─────────────────────────────────────────────────────

static func _paint_human(img: Image, pid: String, seed: int) -> void:
	var cx := 18
	var coats: Array = [Color("2c2233"), Color("332a24"), Color("22282e")]
	var coat: Color = coats[(seed >> 7) % 3]
	var pants := coat.darkened(0.25)
	var skins: Array = [Color("e8c8a0"), Color("d4a878"), Color("c09068")]
	var skin: Color = skins[(seed >> 15) % 3]
	var hairs: Array = [Color("2a1e14"), Color("4a3420"), Color("1a1818"), Color("6a6058")]
	var hair: Color = hairs[(seed >> 17) % 4]
	var top := 20
	var long_coat: bool = pid == "rocha"
	_contact_shadow(img, cx, 6)
	# boots — with a lit toe
	for bx in [cx - 4, cx + 1]:
		for y in range(BASE - 2, BASE + 1):
			_shaded_row(img, bx, bx + 2, y, Color("241a14"))
		_put(img, bx + 3, BASE, _warm(Color("241a14"), 0.35))
	# legs — tapering
	if not long_coat:
		for y2 in range(top + 20, BASE - 2):
			var t: float = float(y2 - top - 20) / float(BASE - 2 - top - 20)
			var wdt: int = 2 if t < 0.6 else 1
			_shaded_row(img, cx - 3 - (wdt - 1), cx - 2, y2, pants)
			_shaded_row(img, cx + 2, cx + 3 + (wdt - 1), y2, pants)
	# torso — shoulders slope in over two rows
	for y3 in range(top + 9, top + 21):
		var rel: int = y3 - (top + 9)
		var wdt2: int = 3 + mini(2, rel)
		_shaded_row(img, cx - wdt2, cx + wdt2 - 1, y3, coat)
	_folds(img, cx - 4, cx + 3, top + 11, top + 19, coat, seed, 2)
	_hspan(img, cx - 4, cx + 3, top + 19, coat.darkened(0.5))       # belt
	_put(img, cx, top + 19, STAR)                                   # buckle
	if long_coat:
		for y4 in range(top + 20, BASE - 4):
			var wdt3: int = 4 + (1 if _h01(2, y4, seed) < 0.3 else 0)
			_shaded_row(img, cx - wdt3, cx + wdt3 - 1, y4, coat)
		_folds(img, cx - 4, cx + 3, top + 20, BASE - 5, coat, seed + 1, 2)
	# arms
	for y5 in range(top + 10, top + 19):
		_put(img, cx - 6, y5, coat.darkened(0.3) if y5 > top + 12 else coat.darkened(0.15))
		_put(img, cx + 5, y5, _warm(coat) if y5 < top + 14 else coat.lightened(0.1))
	_put(img, cx - 6, top + 19, skin)
	_put(img, cx + 5, top + 19, _warm(skin))
	_put(img, cx + 4, top + 21, SILVER)                             # holster glint
	# head — rounded, TWO eyes, a mouth, a neck
	for y6 in range(top, top + 7):
		var hx0: int = cx - 2
		var hx1: int = cx + 2
		if y6 == top or y6 == top + 6:
			hx0 += 1; hx1 -= 1
		_shaded_row(img, hx0, hx1, y6, skin)
	_hspan(img, cx - 1, cx + 1, top, hair)
	_hspan(img, cx - 2, cx + 2, top + 1, hair)
	_put(img, cx - 2, top + 2, hair.darkened(0.2))
	_put(img, cx - 1, top + 3, Color("241a14"))                     # eyes — both of them
	_put(img, cx + 1, top + 3, Color("241a14"))
	_put(img, cx, top + 5, skin.darkened(0.3))                      # mouth
	_hspan(img, cx - 1, cx + 1, top + 7, skin.darkened(0.25))       # neck
	_hspan(img, cx - 2, cx + 2, top + 8, CREAM)                     # collar
	if pid == "jack":
		_put(img, cx, top, STAR)
		_put(img, cx + 1, top, Color("6a5a30"))
	if pid == "rocha":
		_put(img, cx + 1, top + 3, WHITE)
		for dy in range(4):
			_hspan(img, cx - 8, cx - 6, top + 14 + dy,
					CREAM if dy % 2 == 0 else CREAM.darkened(0.12))
		_put(img, cx - 8, top + 15, Color("3868c8"))


static func _paint_kyrindi(img: Image, _pid: String, seed: int) -> void:
	var cx := 18
	var robes: Array = [Color("2a3450"), Color("28304a"), Color("323a58")]
	var robe: Color = robes[(seed >> 7) % 3]
	var skins: Array = [Color("7a94c8"), Color("8ea6d8"), Color("6a82b8")]
	var skin: Color = skins[(seed >> 15) % 3]
	var top := 12
	_contact_shadow(img, cx, 5)
	for y in range(top + 10, BASE + 1):
		var t: float = float(y - (top + 10)) / float(BASE - top - 10)
		var hw: int = 3 + int(t * 3.0)
		if y > BASE - 3 and _h01(1, y, seed) < 0.4:
			hw += 1
		_shaded_row(img, cx - hw, cx + hw, y, robe)
	_folds(img, cx - 3, cx + 3, top + 12, BASE - 2, robe, seed, 3)
	_vspan(img, cx + 2, top + 14, BASE - 6, robe.lightened(0.18))   # sheen
	for y2 in range(top + 12, top + 23):
		_put(img, cx - 5, y2, robe.darkened(0.35))
		_put(img, cx + 5, y2, _warm(robe))
	_put(img, cx + 5, top + 23, skin)
	_hspan(img, cx - 3, cx + 3, top + 9, SILVER)
	_hspan(img, cx - 2, cx + 2, top + 8, SILVER)
	_put(img, cx + 3, top + 9, WHITE)
	for y3 in range(top, top + 8):
		var hx0: int = cx - 2
		if y3 == top:
			hx0 += 1
		_shaded_row(img, hx0, cx + 1, y3, skin)
	_vspan(img, cx - 3, top + 2, top + 6, skin.darkened(0.3))
	_put(img, cx - 3, top + 1, skin.darkened(0.4))
	_put(img, cx - 1, top + 4, Color("18203a"))       # both eyes
	_put(img, cx + 1, top + 4, Color("18203a"))
	_put(img, cx + 1, top + 3, WHITE)                 # their light
	_put(img, cx, top + 6, skin.darkened(0.3))        # mouth
	_put(img, cx, top + 9, STAR)
	if (seed >> 9) % 2 == 0:
		for dy in range(5):
			_hspan(img, cx - 8, cx - 6, top + 18 + dy,
					CREAM if dy % 2 == 0 else CREAM.darkened(0.12))
		_vspan(img, cx - 8, top + 18, top + 22, CREAM.darkened(0.4))


static func _paint_delvanni(img: Image, _pid: String, seed: int) -> void:
	var cx := 18
	var armors: Array = [Color("4a3424"), Color("3a3a2c"), Color("55402a")]
	var armor: Color = armors[(seed >> 7) % 3]
	var skins: Array = [Color("b06038"), Color("a05430"), Color("c07048")]
	var skin: Color = skins[(seed >> 15) % 3]
	var top := 10
	_contact_shadow(img, cx, 9)
	_put(img, cx - 6, top + 8, SILVER)
	_put(img, cx - 7, top + 7, SILVER)
	_hspan(img, cx - 9, cx - 5, top + 6, Color("6a4a2c").darkened(0.1))
	_put(img, cx - 7, top + 5, CREAM)
	_put(img, cx + 8, top + 30, SILVER)
	_put(img, cx + 9, top + 32, SILVER)
	for y in range(top + 28, BASE + 1):
		var t: float = float(y - top - 28) / float(BASE - top - 28)
		var wdt: int = 2 if t < 0.7 else 1
		_shaded_row(img, cx - 5 - (wdt - 1), cx - 3, y, armor.darkened(0.2))
		_shaded_row(img, cx + 3, cx + 5 + (wdt - 1), y, armor.darkened(0.2))
	for y2 in range(top + 12, top + 28):
		var rel: int = y2 - (top + 12)
		@warning_ignore("integer_division")
		var wdt2: int = 8 - mini(2, rel / 6)
		_shaded_row(img, cx - wdt2 + 1, cx + wdt2 - 1, y2, armor)
	_hspan(img, cx - 6, cx + 6, top + 20, armor.darkened(0.35))
	_hspan(img, cx - 5, cx + 5, top + 23, armor.darkened(0.3))
	_hspan(img, cx - 6, cx + 6, top + 26, armor.darkened(0.5))
	_put(img, cx, top + 26, STAR)
	_hspan(img, cx - 8, cx - 5, top + 12, _warm(armor))
	_hspan(img, cx + 5, cx + 8, top + 12, _warm(armor))
	_hspan(img, cx - 7, cx - 5, top + 11, _warm(armor, 0.1))
	_hspan(img, cx + 5, cx + 7, top + 11, _warm(armor, 0.1))
	for y3 in range(top + 16, top + 27):
		_put(img, cx - 9, y3, skin.darkened(0.3))
		_put(img, cx - 8, y3, skin)
		_put(img, cx + 8, y3, skin)
		_put(img, cx + 9, y3, _warm(skin))
	_put(img, cx - 8, top + 27, skin.darkened(0.2))
	_put(img, cx + 9, top + 27, _warm(skin, 0.1))
	_hspan(img, cx - 6, cx + 1, top + 15, skin)
	_hspan(img, cx - 6, cx + 6, top + 16, skin.darkened(0.15))
	_hspan(img, cx - 1, cx + 6, top + 17, _warm(skin))
	_put(img, cx - 7, top + 16, skin.darkened(0.3))
	_put(img, cx + 7, top + 16, _warm(skin, 0.1))
	for y4 in range(top + 4, top + 12):
		var hx0: int = cx - 2
		var hx1: int = cx + 2
		if y4 == top + 4:
			hx0 += 1; hx1 -= 1
		_shaded_row(img, hx0, hx1, y4, skin)
	_hspan(img, cx - 2, cx + 2, top + 6, skin.darkened(0.45))
	_put(img, cx - 1, top + 7, Color("301810"))       # both deep-set eyes
	_put(img, cx + 1, top + 7, Color("301810"))
	_hspan(img, cx - 1, cx + 1, top + 10, skin.darkened(0.35))   # the hard mouth
	_put(img, cx + 3, top + 9, Color("e8dcc0"))
	_put(img, cx + 3, top + 8, Color("e8dcc0"))
	_put(img, cx - 3, top + 9, Color("e8dcc0"))       # matched tusks
	_put(img, cx - 3, top + 8, Color("e8dcc0"))
	if (seed >> 10) % 2 == 0:
		_put(img, cx, top + 3, Color("2a1a10"))
		_put(img, cx, top + 2, Color("2a1a10"))
	if (seed >> 12) % 3 == 0:
		_hspan(img, cx - 2, cx + 2, top + 8, Color("7a3020").darkened(0.1))


static func _paint_kelait(img: Image, pid: String, seed: int) -> void:
	var cx := 18
	var robes: Array = [Color("5a5048"), Color("4c5248"), Color("605444")]
	var robe: Color = robes[(seed >> 7) % 3]
	var child: bool = pid == "yr_kelait_child"
	var top: int = 40 if child else 33
	_contact_shadow(img, cx, 4)
	for y in range(top, BASE + 1):
		var t: float = float(y - top) / float(BASE - top)
		var hw: int = 1 + int(t * 4.0)
		if y > BASE - 2 and _h01(1, y, seed) < 0.4:
			hw += 1
		_shaded_row(img, cx - hw, cx + hw, y, robe)
	_folds(img, cx - 2, cx + 2, top + 4, BASE - 1, robe, seed, 2)
	var hood_dk := robe.darkened(0.55)
	_hspan(img, cx - 1, cx + 1, top + 1, hood_dk)
	_hspan(img, cx - 1, cx + 1, top + 2, hood_dk)
	_put(img, cx - 1, top + 2, CREAM)
	_put(img, cx + 1, top + 2, CREAM)
	_put(img, cx, top, _warm(robe))                                 # hood rim light
	if not child and (seed >> 9) % 2 == 0:
		_vspan(img, cx + 6, top - 8, BASE, Color("6a4a2c"))
		_put(img, cx + 5, top - 4, Color("6a4a2c").darkened(0.3))   # hand on staff
		_put(img, cx + 6, top - 9, AMBER)
	if child:
		_put(img, cx, top, Color("c8b498"))


static func _paint_scarlet(img: Image, _pid: String, seed: int) -> void:
	var cx := 18
	var gown := Color("c03048")
	var skin := Color("f4ead8")
	var top := 18
	for x in range(cx - 5, cx + 6):
		if _bayer(x, BASE + 1) < 0.5:
			_put(img, x, BASE + 1, _warm(GROUND_LT, 0.3))
	# a faint glow halo in the air around her
	for y in range(top - 3, BASE):
		for x2 in range(cx - 8, cx + 9):
			@warning_ignore("integer_division")
			var d: int = absi(x2 - cx) + absi(y - (top + 12)) / 3
			if (d == 8 or d == 9) and _bayer(x2, y) < 0.2:
				_put(img, x2, y, Color("7a2438"))
	for y2 in range(top + 9, BASE):
		var t: float = float(y2 - (top + 9)) / float(BASE - top - 9)
		var hw: int = 2 + int(t * 4.0)
		if y2 > BASE - 4 and _h01(1, y2, seed) < 0.4:
			hw += 1
		_shaded_row(img, cx - hw, cx + hw, y2, gown)
	_folds(img, cx - 3, cx + 3, top + 12, BASE - 2, gown, seed, 2)
	for y3 in range(top - 2, top + 12):
		var rel: int = y3 - (top - 2)
		@warning_ignore("integer_division")
		var stream: int = maxi(1, 5 - rel / 3) + (1 if _h01(3, y3, 77) < 0.5 else 0)
		@warning_ignore("integer_division")
		var x1: int = cx - 3 - rel / 4
		_hspan(img, x1 - stream, x1, y3, CREAM)
		if _h01(5, y3, 78) < 0.4:
			_put(img, x1 - stream - 1, y3, CREAM.darkened(0.15))
	for y4 in range(top, top + 7):
		var hx0: int = cx - 2
		var hx1: int = cx + 2
		if y4 == top:
			hx0 += 1; hx1 -= 1
		_shaded_row(img, hx0, hx1, y4, skin)
	_put(img, cx - 1, top + 3, Color("6a1828"))       # both her eyes
	_put(img, cx + 1, top + 3, Color("6a1828"))
	_put(img, cx, top + 5, skin.darkened(0.2))        # her mouth
	_hspan(img, cx - 3, cx + 3, top + 7, gown.lightened(0.2))
	_vspan(img, cx - 4, top + 9, top + 16, skin)
	_vspan(img, cx + 4, top + 9, top + 16, WHITE)
	_put(img, cx - 4, top + 17, skin)                 # open hands
	_put(img, cx + 4, top + 17, WHITE)
	for s in [[cx + 8, top - 4], [cx + 10, top], [cx + 9, top + 4]]:
		_put(img, s[0], s[1], STAR)
