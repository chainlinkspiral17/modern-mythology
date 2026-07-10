extends RefCounted
class_name EarthmanPortrait
## Earthman Chronicles · character plates · v4 FULL FIGURES.
##
## Per the reference boards: painterly pixel art, silhouette-first.
## At slowstick scale identity is COSTUME + POSE + HEIGHT, not
## facial features — faces are mostly shadow with a glint.  Each
## character stands full-figure in a dithered Parsan dusk (violet
## banding down to an amber horizon, two moons, rust dunes), and
## the species read from across the room:
##
##   human    · mid-height · jacket, boots, holster glint · 1940s
##   kyrindi  · tall slender robe, high silver collar, pale blue
##   delvanni · massive · four arms VISIBLE (two crossed, two
##              hanging) · greatsword hilt over the shoulder
##   kelait   · a small hooded cone · lit eyes inside the hood
##   scarlet  · pale glow in red, hair streaming as light, feet
##              not quite touching the dust
##
## Chrome: corner registration brackets + the spectral ID stamp
## (the machine's name for the subject).  Deterministic per id.
## Named specials: jack (goggles up), rocha (glasses glint, the
## notebook, the blue pen, a longer coat), yr_kelait_child
## (smaller, looking up).
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

const SKY: Array = [Color("100a16"), Color("2a1428"), Color("58223a"),
		Color("9a4838"), Color("d08448")]
const GROUND    := Color("6a3024")
const GROUND_DK := Color("3a1a16")
const GROUND_LT := Color("8a4430")

const HORIZON := 44
const BASE := 54          # where boots touch dust

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


static func _rect(img: Image, x0: int, y0: int, rw: int, rh: int, c: Color) -> void:
	for y in range(y0, y0 + rh):
		for x in range(x0, x0 + rw):
			_put(img, x, y, c)


## Amber-warmed rim variant — the horizon light's tint.
static func _warm(c: Color, f: float = 0.22) -> Color:
	var l := c.lightened(f)
	return Color(minf(1.0, l.r * 1.10), l.g, l.b * 0.90, 1.0)


## A garment/limb block: shadow left column, lit right column.
static func _part(img: Image, x0: int, x1: int, y0: int, y1: int, core: Color) -> void:
	var sh := core.darkened(0.35)
	var lt := _warm(core)
	for y in range(y0, y1 + 1):
		for x in range(x0, x1 + 1):
			if x == x1:
				_put(img, x, y, lt)
			elif x == x0:
				_put(img, x, y, sh)
			else:
				_put(img, x, y, core)


# ─── the dusk plate ──────────────────────────────────────────────

static func _dusk_bg(img: Image, seed: int) -> void:
	# banded dusk down to the amber horizon
	for y in range(HORIZON):
		var t: float = float(y) / float(HORIZON)
		var f: float = t * float(SKY.size() - 1)
		var i: int = mini(int(f), SKY.size() - 2)
		for x in range(W):
			img.set_pixel(x, y, SKY[i + 1] if (f - float(i)) > _bayer(x, y) else SKY[i])
	# stars in the high dusk
	for y2 in range(16):
		for x2 in range(W):
			if _h01(x2, y2, seed) < 0.012:
				img.set_pixel(x2, y2, SILVER)
	# the two moons
	for dx in range(-2, 3):
		for dy in range(-2, 3):
			if dx * dx + dy * dy <= 4:
				_put(img, 7 + dx, 7 + dy, CREAM)
	_put(img, 6, 6, WHITE)
	_put(img, 13, 11, SILVER)
	_put(img, 14, 11, SILVER)
	_put(img, 13, 12, SILVER)
	# ground — rust dunes
	for y3 in range(HORIZON, H):
		var c: Color = GROUND if y3 < BASE else GROUND_DK
		for x3 in range(W):
			img.set_pixel(x3, y3, c)
	for k in range(3):
		var ry: int = HORIZON + 2 + k * 3 + int(_h01(k, 3, seed) * 2.0)
		var rx: int = int(_h01(3, k, seed) * 20.0)
		_hspan(img, rx, rx + 10 + k * 4, ry, GROUND_LT)
	_hspan(img, 0, W - 1, HORIZON, GROUND.darkened(0.35))
	for x4 in range(W):
		if _bayer(x4, HORIZON - 1) < 0.5:
			img.set_pixel(x4, HORIZON - 1, SKY[4])


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
	for x in range(cx - half_w, cx + half_w + 1):
		if _bayer(x, BASE + 1) < 0.7:
			_put(img, x, BASE + 1, GROUND_DK)
	for x2 in range(cx - half_w + 2, cx + half_w - 1):
		_put(img, x2, BASE + 2, GROUND_DK)


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
	_contact_shadow(img, cx, 6)
	_part(img, cx - 4, cx - 2, BASE - 3, BASE, Color("241a14"))    # boots
	_part(img, cx + 1, cx + 3, BASE - 3, BASE, Color("241a14"))
	_part(img, cx - 4, cx - 2, top + 20, BASE - 4, pants)          # legs
	_part(img, cx + 1, cx + 3, top + 20, BASE - 4, pants)
	_part(img, cx - 5, cx + 4, top + 9, top + 20, coat)            # jacket
	_hspan(img, cx - 4, cx + 3, top + 19, coat.darkened(0.45))     # belt
	_part(img, cx - 6, cx - 5, top + 10, top + 18, coat.darkened(0.12))  # arms
	_part(img, cx + 5, cx + 6, top + 10, top + 18, coat)
	_put(img, cx - 6, top + 19, skin)                              # hands
	_put(img, cx + 6, top + 19, _warm(skin))
	_put(img, cx + 4, top + 21, SILVER)                            # holster glint
	# head — small, face mostly shade, lit on the key side
	_part(img, cx - 2, cx + 2, top, top + 6, skin)
	_rect(img, cx - 2, top, 5, 2, hair)
	_put(img, cx - 2, top + 2, skin.darkened(0.4))
	_put(img, cx - 1, top + 3, skin.darkened(0.3))
	_put(img, cx + 1, top + 3, Color("241a14"))                    # eye shadow
	_hspan(img, cx - 2, cx + 2, top + 8, CREAM)                    # collar
	if pid == "jack":
		_put(img, cx, top, STAR)                                   # goggles up
		_put(img, cx + 1, top, Color("6a5a30"))
	if pid == "rocha":
		_put(img, cx + 1, top + 3, WHITE)                          # glasses glint
		_rect(img, cx - 8, top + 14, 3, 4, CREAM)                  # the notebook
		_put(img, cx - 8, top + 15, Color("3868c8"))               # blue pen line
		_part(img, cx - 5, cx + 4, top + 20, BASE - 6, coat)       # her coat runs long


static func _paint_kyrindi(img: Image, _pid: String, seed: int) -> void:
	var cx := 18
	var robes: Array = [Color("2a3450"), Color("28304a"), Color("323a58")]
	var robe: Color = robes[(seed >> 7) % 3]
	var skins: Array = [Color("7a94c8"), Color("8ea6d8"), Color("6a82b8")]
	var skin: Color = skins[(seed >> 15) % 3]
	var top := 12
	_contact_shadow(img, cx, 5)
	# the long robe — a slender column flaring at the hem
	for y in range(top + 10, BASE + 1):
		var t: float = float(y - (top + 10)) / float(BASE - top - 10)
		var hw: int = 3 + int(t * 3.0)
		_hspan(img, cx - hw, cx + hw, y, robe)
		_put(img, cx + hw, y, _warm(robe))
		_put(img, cx - hw, y, robe.darkened(0.35))
	_part(img, cx - 5, cx - 4, top + 12, top + 22, robe.darkened(0.15))  # sleeves
	_part(img, cx + 4, cx + 5, top + 12, top + 22, robe)
	_put(img, cx + 5, top + 23, skin)                              # one visible hand
	_hspan(img, cx - 3, cx + 3, top + 9, SILVER)                   # high collar
	_hspan(img, cx - 2, cx + 2, top + 8, SILVER)
	# elongated head — pale blue, backswept
	_part(img, cx - 2, cx + 1, top, top + 7, skin)
	_vspan(img, cx - 3, top + 1, top + 5, skin.darkened(0.3))
	_put(img, cx + 1, top + 3, Color("18203a"))                    # eye, front
	_put(img, cx + 2, top + 3, WHITE)                              # its light
	_put(img, cx, top + 9, STAR)                                   # the song-sigil
	if (seed >> 9) % 2 == 0:                                       # the scholar's folio
		_rect(img, cx - 8, top + 18, 3, 5, CREAM)
		_vspan(img, cx - 8, top + 18, top + 22, CREAM.darkened(0.4))


static func _paint_delvanni(img: Image, _pid: String, seed: int) -> void:
	var cx := 18
	var armors: Array = [Color("4a3424"), Color("3a3a2c"), Color("55402a")]
	var armor: Color = armors[(seed >> 7) % 3]
	var skins: Array = [Color("b06038"), Color("a05430"), Color("c07048")]
	var skin: Color = skins[(seed >> 15) % 3]
	var top := 10
	_contact_shadow(img, cx, 9)
	# the greatsword on the back — only hilt and tip show past the mass
	_put(img, cx - 6, top + 8, SILVER)
	_put(img, cx - 7, top + 7, SILVER)
	_hspan(img, cx - 9, cx - 5, top + 6, Color("6a4a2c").darkened(0.1))
	_put(img, cx - 7, top + 5, CREAM)
	_put(img, cx + 8, top + 30, SILVER)
	_put(img, cx + 9, top + 32, SILVER)
	_part(img, cx - 6, cx - 3, top + 28, BASE, armor.darkened(0.2))   # legs
	_part(img, cx + 3, cx + 6, top + 28, BASE, armor.darkened(0.2))
	_part(img, cx - 7, cx + 7, top + 12, top + 27, armor)             # torso
	_hspan(img, cx - 6, cx + 6, top + 26, armor.darkened(0.45))       # belt
	# LOWER arm pair — hanging, bare rust skin
	_part(img, cx - 9, cx - 8, top + 16, top + 26, skin)
	_part(img, cx + 8, cx + 9, top + 16, top + 26, skin)
	# UPPER arm pair — crossed over the chest, bare skin
	_hspan(img, cx - 6, cx + 1, top + 15, skin)
	_hspan(img, cx - 1, cx + 6, top + 17, _warm(skin))
	_hspan(img, cx - 6, cx + 6, top + 16, skin.darkened(0.15))
	_hspan(img, cx - 8, cx - 5, top + 12, _warm(armor))               # shoulders
	_hspan(img, cx + 5, cx + 8, top + 12, _warm(armor))
	# head — small on the mass, heavy brow, tusk
	_part(img, cx - 2, cx + 2, top + 4, top + 11, skin)
	_hspan(img, cx - 2, cx + 2, top + 6, skin.darkened(0.4))
	_put(img, cx + 1, top + 7, Color("301810"))
	_put(img, cx + 3, top + 9, Color("e8dcc0"))                       # the tusk
	_put(img, cx + 3, top + 8, Color("e8dcc0"))
	if (seed >> 10) % 2 == 0:                                         # topknot
		_put(img, cx, top + 3, Color("2a1a10"))
		_put(img, cx, top + 2, Color("2a1a10"))
	if (seed >> 12) % 3 == 0:                                         # war-paint
		_hspan(img, cx - 2, cx + 2, top + 8, Color("7a3020").darkened(0.1))


static func _paint_kelait(img: Image, pid: String, seed: int) -> void:
	var cx := 18
	var robes: Array = [Color("5a5048"), Color("4c5248"), Color("605444")]
	var robe: Color = robes[(seed >> 7) % 3]
	var child: bool = pid == "yr_kelait_child"
	var top: int = 40 if child else 33
	_contact_shadow(img, cx, 4)
	# the hooded cone — small, quiet
	for y in range(top, BASE + 1):
		var t: float = float(y - top) / float(BASE - top)
		var hw: int = 1 + int(t * 4.0)
		_hspan(img, cx - hw, cx + hw, y, robe)
		_put(img, cx + hw, y, _warm(robe))
		_put(img, cx - hw, y, robe.darkened(0.35))
	# the hood shadow, and the eyes lit inside it
	var hood_dk := robe.darkened(0.55)
	_hspan(img, cx - 1, cx + 1, top + 1, hood_dk)
	_hspan(img, cx - 1, cx + 1, top + 2, hood_dk)
	_put(img, cx - 1, top + 2, CREAM)
	_put(img, cx + 1, top + 2, CREAM)
	# a staff taller than they are, on some elders
	if not child and (seed >> 9) % 2 == 0:
		_vspan(img, cx + 6, top - 8, BASE, Color("6a4a2c"))
		_put(img, cx + 6, top - 9, AMBER)                             # lantern ember
	if child:
		_put(img, cx, top, Color("c8b498"))                           # looking up


static func _paint_scarlet(img: Image, _pid: String, _seed: int) -> void:
	var cx := 18
	var gown := Color("c03048")
	var skin := Color("f4ead8")
	var top := 18
	# she casts light DOWN onto the dust, and no contact shadow
	for x in range(cx - 5, cx + 6):
		if _bayer(x, BASE + 1) < 0.5:
			_put(img, x, BASE + 1, _warm(GROUND_LT, 0.3))
	# the gown — floating a pixel off the dust
	for y in range(top + 9, BASE):
		var t: float = float(y - (top + 9)) / float(BASE - top - 9)
		var hw: int = 2 + int(t * 4.0)
		_hspan(img, cx - hw, cx + hw, y, gown)
		_put(img, cx + hw, y, gown.lightened(0.3))
		_put(img, cx - hw, y, gown.darkened(0.3))
	# hair streaming back as light — tapering ribbons, not a block
	for y2 in range(top - 2, top + 12):
		var rel: int = y2 - (top - 2)
		@warning_ignore("integer_division")
		var stream: int = maxi(1, 5 - rel / 3) + (1 if _h01(3, y2, 77) < 0.5 else 0)
		@warning_ignore("integer_division")
		var x1: int = cx - 3 - rel / 4
		_hspan(img, x1 - stream, x1, y2, CREAM)
	# head and shoulders — pale, lit from within
	_part(img, cx - 2, cx + 2, top, top + 6, skin)
	_put(img, cx + 1, top + 3, Color("6a1828"))                       # her eye
	_hspan(img, cx - 3, cx + 3, top + 7, gown.lightened(0.2))
	_vspan(img, cx - 4, top + 9, top + 16, skin)                      # arms open
	_vspan(img, cx + 4, top + 9, top + 16, WHITE)
	for s in [[cx + 8, top - 4], [cx + 10, top], [cx + 9, top + 4]]:
		_put(img, s[0], s[1], STAR)
