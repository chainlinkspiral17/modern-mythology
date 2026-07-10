extends RefCounted
class_name EarthmanPortrait
## Earthman Chronicles · species-driven NPC portraits · v3 PROFILES.
##
## Fey Faire draws front-facing symmetric busts.  These are SIDE
## PROFILES on instrument plates — anthropological specimen
## drawings, faces turned right into the key light.  The species
## live in the silhouette: the Kyrindi's long backswept cranium,
## the Delvanni's brow shelf and jaw with the tusk jutting past the
## lip, the Kelait's small hooded curve, the human's 1940s haircut
## and straight nose, the Scarlet Woman's hair streaming back as
## light.  Nothing in this house draws profiles but Earthman.
##
## Instrument chrome (kept from v2): graticule + meridian at eye
## height, open registration brackets, calibration ticks, spectral
## ID stamp (six seed-colored code bars — the machine's name for
## the subject).
##
## Deterministic per id.  Named specials: jack (goggles pushed up),
## rocha (lens ring + arm to the ear, the blue pen),
## yr_kelait_child (smaller, bare-headed).
##
## Lockstep mirror: godot/tools/sprites/preview_earthman_portrait.py
## — edit both together, preview before pushing.
##
## Usage (preload by path — new class_names miss the first editor
## scan after a pull):
##   const PORTRAIT := preload("res://scenes/games/earthman_chronicles/EarthmanPortrait.gd")
##   tex_rect.texture = PORTRAIT.texture("sara_nai", "kyrindi", Vector2i(80, 100))

const W := 40
const H := 50

const VOID     := Color("0b080e")
const PANEL    := Color("291a33")
const CORTEX   := Color("58305f")
const AMBER    := Color("c86020")
const STAR     := Color("f8c848")
const CREAM    := Color("e9d090")
const WHITE    := Color("f0f0f0")
const SILVER   := Color("b8bcc8")
const RED      := Color("c02020")
const GRID     := Color("18101f")
const MERIDIAN := Color("241a30")
const TICK     := Color("6a5878")

static var _cache: Dictionary = {}


static func texture(pid: String, species: String, size: Vector2i = Vector2i(80, 100)) -> ImageTexture:
	var key := "%s:%s:%d" % [pid, species, size.x]
	if _cache.has(key):
		return _cache[key]
	var img := Image.create(W, H, false, Image.FORMAT_RGBA8)
	img.fill(VOID)
	_plate_bg(img)
	var seed: int = pid.hash()
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


static func _put(img: Image, x: int, y: int, c: Color) -> void:
	if x >= 1 and x < W - 1 and y >= 1 and y < H - 1:
		img.set_pixel(x, y, c)


static func _hspan(img: Image, x0: int, x1: int, y: int, c: Color) -> void:
	for x in range(x0, x1 + 1):
		_put(img, x, y, c)


## Amber-warmed rim variant of a color — the key light's tint.
static func _lit(c: Color) -> Color:
	var l := c.lightened(0.20)
	return Color(minf(1.0, l.r * 1.08), l.g, l.b * 0.92, 1.0)


# ─── the plate ───────────────────────────────────────────────────

static func _plate_bg(img: Image) -> void:
	for y in range(H):
		for x in range(W):
			if x % 8 == 4 or y % 8 == 4:
				img.set_pixel(x, y, GRID)
	for x2 in range(W):
		img.set_pixel(x2, 17, MERIDIAN)
	@warning_ignore("integer_division")
	var mid: int = W / 2
	for i in range(-2, 3):
		img.set_pixel(mid + i, 10, MERIDIAN)
		img.set_pixel(mid, 10 + i, MERIDIAN)


static func _plate_chrome(img: Image, seed: int) -> void:
	for br in [[1, 1, 1, 1], [W - 2, 1, -1, 1], [1, H - 2, 1, -1], [W - 2, H - 2, -1, -1]]:
		var cx0: int = br[0]
		var cy0: int = br[1]
		for i in range(5):
			img.set_pixel(cx0 + int(br[2]) * i, cy0, CORTEX)
			img.set_pixel(cx0, cy0 + int(br[3]) * i, CORTEX)
	for x in range(4, W - 4, 4):
		var tick_h: int = 2 if x % 8 == 0 else 1
		for t in range(tick_h):
			img.set_pixel(x, H - 2 - t, TICK)
	for y in range(6, H - 6, 4):
		img.set_pixel(1, y, TICK)
		if y % 8 == 6:
			img.set_pixel(2, y, TICK)
	var code_cols: Array = [AMBER, STAR, SILVER, CORTEX, Color("58a068"), RED]
	for i2 in range(6):
		var c: Color = code_cols[(seed >> (i2 * 4)) % code_cols.size()]
		for t2 in range(2):
			img.set_pixel(W - 16 + i2 * 2 + t2, 2, c)
			img.set_pixel(W - 16 + i2 * 2 + t2, 3, c)


# ─── profile machinery ───────────────────────────────────────────
# The face looks RIGHT (into the key light).  spec keys: fx (face
# line) · bx (back of skull) · head_top/head_bot · crown[/crown_slope]
# · brow_rel · eye_rel · nose_rel · nose_len · mouth_rel · chin_rel
# [/chin_slope] · jaw_rel[/jaw_slope].

static func _build_profile(spec: Dictionary) -> Array:
	var face: Dictionary = {}
	var backs: Dictionary = {}
	var ht: int = spec["head_top"]
	var hb: int = spec["head_bot"]
	var fx: int = spec["fx"]
	var bx: int = spec["bx"]
	var crown: int = spec.get("crown", 4)
	for y in range(ht, hb + 1):
		var rel: int = y - ht
		var x: int = fx
		if rel < crown:
			x = fx - (crown - rel) * int(spec.get("crown_slope", 2))
		if rel == int(spec["brow_rel"]):
			x = fx + 1
		if rel > int(spec["brow_rel"]) and rel <= int(spec["eye_rel"]) + 1:
			x = fx - 1
		var nr: int = spec["nose_rel"]
		if rel >= nr and rel < nr + 3:
			var jut: Array = [2, int(spec["nose_len"]), 1]
			x = fx + int(jut[rel - nr])
		if rel == int(spec["mouth_rel"]):
			x = fx
		if rel == int(spec["mouth_rel"]) + 1:
			x = fx - 1
		if rel == int(spec["mouth_rel"]) + 2:
			x = fx
		if rel >= int(spec["chin_rel"]):
			x = fx - (rel - int(spec["chin_rel"])) * int(spec.get("chin_slope", 1))
		face[y] = x
		var b: int = bx
		if rel < 4:
			b = bx + (4 - rel) * 2
		var jr: int = spec.get("jaw_rel", int(spec["chin_rel"]) - 2)
		if rel > jr:
			b = bx + (rel - jr) * int(spec.get("jaw_slope", 2))
		backs[y] = b
	return [face, backs]


static func _fill_profile(img: Image, face: Dictionary, backs: Dictionary,
		skin: Color, skin_sh: Color, skin_lt: Color) -> void:
	for y in face.keys():
		var b: int = backs[y]
		var f: int = face[y]
		if f <= b:
			continue
		for x in range(b, f + 1):
			if x >= f - 1:
				_put(img, x, int(y), skin_lt)
			elif x <= b + 1:
				_put(img, x, int(y), skin_sh)
			else:
				_put(img, x, int(y), skin)


## Eye, nostril, mouth line, ear — shared profile furniture.
static func _profile_features(img: Image, spec: Dictionary, skin: Color,
		skin_sh: Color, eye_c: Color) -> void:
	var ht: int = spec["head_top"]
	var fx: int = spec["fx"]
	var bx: int = spec["bx"]
	var eye_y: int = ht + int(spec["eye_rel"])
	var ex: int = fx - 5
	_put(img, ex, eye_y, eye_c)
	_put(img, ex + 1, eye_y, eye_c)
	_put(img, ex + 1, eye_y - 1, skin_sh)                # lid
	_put(img, ex + 2, eye_y, WHITE)                      # the light in it
	_put(img, fx + 1, ht + int(spec["nose_rel"]) + 2, skin_sh)   # nostril
	var my: int = ht + int(spec["mouth_rel"]) + 1
	_hspan(img, fx - 4, fx - 1, my, skin_sh)             # mouth line
	@warning_ignore("integer_division")
	var ear_x: int = bx + (fx - bx) / 2 - 2
	_put(img, ear_x, eye_y, skin_sh)
	_put(img, ear_x + 1, eye_y, skin_sh)
	_put(img, ear_x, eye_y + 1, skin_sh)
	_put(img, ear_x + 1, eye_y + 1, skin)
	_put(img, ear_x, eye_y + 2, skin_sh)


static func _neck_and_shoulders(img: Image, spec: Dictionary, _skin: Color,
		skin_sh: Color, garment: Color) -> int:
	var hb: int = spec["head_bot"]
	var bx: int = spec["bx"]
	var fx: int = spec["fx"]
	@warning_ignore("integer_division")
	var ncx: int = bx + (fx - bx) / 2
	for y in range(hb - 3, hb + 4):
		_hspan(img, ncx - 2, ncx + 3, y, skin_sh)
	for y2 in range(hb + 3, H - 3):
		var widen: int = mini(17, 6 + (y2 - hb - 3) * 3)
		_hspan(img, ncx - widen, ncx + widen, y2, garment)
		_hspan(img, ncx + maxi(3, widen - 4), ncx + widen, y2, garment.lightened(0.14))
		_hspan(img, ncx - widen, ncx - widen + 2, y2, garment.darkened(0.25))
	return ncx


# ─── species painters ────────────────────────────────────────────

static func _paint_human(img: Image, pid: String, seed: int) -> void:
	var skins: Array = [Color("e8c8a0"), Color("d4a878"), Color("c09068")]
	var skin: Color = skins[(seed >> 15) % 3]
	var skin_sh := skin.darkened(0.22)
	var skin_lt := _lit(skin)
	var hairs: Array = [Color("3a2a1c"), Color("6a4a2c"), Color("222020"), Color("8a8078")]
	var hair: Color = hairs[(seed >> 17) % 4]
	var garment := Color("4a3c30") if (seed >> 5) % 2 == 0 else Color("3a4250")
	var spec: Dictionary = {
		"fx": 30 + (seed & 0x1), "bx": 10 - ((seed >> 1) & 0x1),
		"head_top": 6, "head_bot": 31, "crown": 4,
		"brow_rel": 9, "eye_rel": 11,
		"nose_rel": 13, "nose_len": 3 + ((seed >> 3) & 0x1),
		"mouth_rel": 18, "chin_rel": 21, "chin_slope": 1,
		"jaw_rel": 19, "jaw_slope": 2,
	}
	var prof := _build_profile(spec)
	var face: Dictionary = prof[0]
	var backs: Dictionary = prof[1]
	_fill_profile(img, face, backs, skin, skin_sh, skin_lt)
	var ncx := _neck_and_shoulders(img, spec, skin, skin_sh, garment)
	# 1940s cut in profile — slick top, short back, sideburn
	var ht: int = spec["head_top"]
	for y in range(ht - 1, ht + 4):
		var b: int = backs.get(y, spec["bx"])
		_hspan(img, b - 1, int(face.get(y, spec["fx"])) - 2, y, hair)
	for y2 in range(ht + 4, ht + 12):
		_hspan(img, int(backs[y2]) - 1, int(backs[y2]) + 2, y2, hair)
	_hspan(img, int(backs[ht + 12]), int(backs[ht + 12]) + 1, ht + 12, hair)  # sideburn
	_profile_features(img, spec, skin, skin_sh, Color("2a2420"))
	# collar + tie knot at the throat
	_hspan(img, ncx - 4, ncx + 4, int(spec["head_bot"]) + 4, CREAM)
	var tie: Color = RED if (seed >> 13) % 2 == 0 else garment.darkened(0.3)
	_put(img, ncx + 1, int(spec["head_bot"]) + 5, tie)
	_put(img, ncx + 1, int(spec["head_bot"]) + 6, tie)
	if pid == "rocha":
		# glasses in profile — one lens ring + arm back to the ear
		var eye_y: int = ht + int(spec["eye_rel"])
		var ex: int = int(spec["fx"]) - 5
		var lens := Color("222020")
		for d in [[-1, -1], [0, -1], [1, -1], [2, 0], [-2, 0], [-1, 1], [0, 1], [1, 1]]:
			_put(img, ex + int(d[0]), eye_y + int(d[1]), lens)
		_hspan(img, int(spec["bx"]) + 6, ex - 2, eye_y - 1, lens)
		_put(img, ncx + 5, int(spec["head_bot"]) + 5, Color("3868c8"))   # the blue pen
	if pid == "jack":
		# goggles pushed up — band across the crown, one lens up top
		_hspan(img, int(backs[ht + 2]) - 1, int(face[ht + 2]) - 1, ht + 2, Color("6a5a30"))
		_put(img, int(face[ht + 2]) - 3, ht + 1, STAR)


static func _paint_kyrindi(img: Image, _pid: String, seed: int) -> void:
	var skins: Array = [Color("7a94c8"), Color("8ea6d8"), Color("6a82b8")]
	var skin: Color = skins[(seed >> 15) % 3]
	var skin_sh := skin.darkened(0.25)
	var skin_lt := _lit(skin)
	var garment := Color("2a3450")
	# the long backswept cranium — bx runs almost to the plate edge
	var spec: Dictionary = {
		"fx": 31, "bx": 4 + ((seed >> 1) & 0x1),
		"head_top": 7, "head_bot": 32, "crown": 6, "crown_slope": 4,
		"brow_rel": 10, "eye_rel": 12,
		"nose_rel": 14, "nose_len": 3,
		"mouth_rel": 19, "chin_rel": 22, "chin_slope": 1,
		"jaw_rel": 18, "jaw_slope": 3,
	}
	var prof := _build_profile(spec)
	var face: Dictionary = prof[0]
	var backs: Dictionary = prof[1]
	_fill_profile(img, face, backs, skin, skin_sh, skin_lt)
	var ncx := _neck_and_shoulders(img, spec, skin, skin_sh, garment)
	var ht: int = spec["head_top"]
	# crest ridge along the swept skull, or a braid off the back
	var crest := skin.darkened(0.4)
	if (seed >> 9) % 2 == 0:
		for x in range(int(backs[ht + 1]) - 1, int(face[ht + 1]) - 6):
			_put(img, x, ht - 1, crest)
			if x % 3 == 0:
				_put(img, x, ht - 2, crest)
	else:
		var bx0: int = int(spec["bx"]) + 2
		for y in range(ht + 4, int(spec["head_bot"]) + 6):
			_put(img, bx0 - 2, y, crest)
			if y % 3 == 0:
				_put(img, bx0 - 3, y, crest)
	# court markings — paired lines down the visible cheek
	var eye_y: int = ht + int(spec["eye_rel"])
	var mark := Color("2a3450").darkened(0.1)
	for dy in range(3):
		_put(img, int(spec["fx"]) - 6, eye_y + 3 + dy, mark)
		_put(img, int(spec["fx"]) - 8, eye_y + 4 + dy, mark)
	_profile_features(img, spec, skin, skin_sh, Color("18203a"))
	# high silver collar + the song-sigil at the throat
	_hspan(img, ncx - 5, ncx + 5, int(spec["head_bot"]) + 3, SILVER)
	_hspan(img, ncx - 6, ncx + 6, int(spec["head_bot"]) + 4, SILVER)
	_hspan(img, ncx - 7, ncx + 7, int(spec["head_bot"]) + 5, SILVER.darkened(0.3))
	_put(img, ncx + 2, int(spec["head_bot"]) + 2, STAR)


static func _paint_delvanni(img: Image, _pid: String, seed: int) -> void:
	var skins: Array = [Color("b06038"), Color("a05430"), Color("c07048")]
	var skin: Color = skins[(seed >> 15) % 3]
	var skin_sh := skin.darkened(0.25)
	var skin_lt := _lit(skin)
	var garments: Array = [Color("4a3424"), Color("3a3a2c"), Color("55402a")]
	var garment: Color = garments[(seed >> 7) % 3]
	# massive skull, heavier brow, jaw that barely recedes
	var spec: Dictionary = {
		"fx": 32, "bx": 7 - ((seed >> 1) & 0x1),
		"head_top": 5, "head_bot": 32, "crown": 4,
		"brow_rel": 10, "eye_rel": 12,
		"nose_rel": 14, "nose_len": 3,
		"mouth_rel": 19, "chin_rel": 24, "chin_slope": 1,
		"jaw_rel": 26, "jaw_slope": 2,
	}
	var prof := _build_profile(spec)
	var face: Dictionary = prof[0]
	var backs: Dictionary = prof[1]
	# the brow SHELF — two extra rows jutting at brow height
	var ht: int = spec["head_top"]
	face[ht + int(spec["brow_rel"])] = int(spec["fx"]) + 2
	face[ht + int(spec["brow_rel"]) - 1] = int(spec["fx"]) + 1
	_fill_profile(img, face, backs, skin, skin_sh, skin_lt)
	var ncx := _neck_and_shoulders(img, spec, skin, skin_sh, garment)
	if (seed >> 10) % 2 == 0:   # topknot
		var knot := Color("2a1a10")
		var kx: int = int(backs[ht + 1]) + 3
		_hspan(img, kx, kx + 2, ht - 1, knot)
		_hspan(img, kx, kx + 2, ht - 2, knot)
		_put(img, kx + 1, ht - 3, knot)
	# the tusk — up past the lip, IN SILHOUETTE
	var tusk := Color("e8dcc0")
	var my: int = ht + int(spec["mouth_rel"])
	var tlen: int = 2 + ((seed >> 22) & 0x1)
	for t in range(tlen):
		_put(img, int(spec["fx"]) + 1 + (1 if t >= 2 else 0), my - 1 - t, tusk)
	_put(img, int(spec["fx"]), my, tusk)
	# war-paint band across the visible cheek, on some
	var eye_y: int = ht + int(spec["eye_rel"])
	if (seed >> 12) % 3 == 0:
		_hspan(img, int(spec["fx"]) - 9, int(spec["fx"]) - 2, eye_y + 2,
				Color("7a3020").darkened(0.15))
	# a kept scar, on some
	if (seed >> 20) % 3 == 1:
		for i in range(4):
			_put(img, int(spec["fx"]) - 10 + i, eye_y + 3 + i, skin.darkened(0.45))
	_profile_features(img, spec, skin, skin_sh, Color("301810"))
	# second shoulder pair + chest strap
	var sh_y: int = int(spec["head_bot"]) + 8
	_hspan(img, ncx - 17, ncx - 11, sh_y, skin)
	_hspan(img, ncx + 11, ncx + 17, sh_y, skin)
	_hspan(img, ncx - 17, ncx - 12, sh_y + 1, skin_sh)
	_hspan(img, ncx + 12, ncx + 17, sh_y + 1, skin_lt)
	for i2 in range(14):
		@warning_ignore("integer_division")
		_put(img, ncx - 7 + i2, int(spec["head_bot"]) + 5 + i2 / 3, garment.darkened(0.4))


static func _paint_kelait(img: Image, pid: String, seed: int) -> void:
	var skins: Array = [Color("c8b498"), Color("b8a488"), Color("d0c0a8")]
	var skin: Color = skins[(seed >> 15) % 3]
	var skin_sh := skin.darkened(0.2)
	var skin_lt := _lit(skin)
	var garments: Array = [Color("5a5048"), Color("4c5248"), Color("605444")]
	var garment: Color = garments[(seed >> 7) % 3]
	var child: bool = pid == "yr_kelait_child"
	var ht: int = 21 if child else 17
	var hb: int = (ht + 11) if child else (ht + 14)
	var spec: Dictionary = {
		"fx": 28, "bx": 14 if child else 12,
		"head_top": ht, "head_bot": hb, "crown": 3,
		"brow_rel": 4, "eye_rel": 5,
		"nose_rel": 7, "nose_len": 2,
		"mouth_rel": 10, "chin_rel": 12, "chin_slope": 1,
		"jaw_rel": 11, "jaw_slope": 2,
	}
	var prof := _build_profile(spec)
	var face: Dictionary = prof[0]
	var backs: Dictionary = prof[1]
	_fill_profile(img, face, backs, skin, skin_sh, skin_lt)
	var ncx := _neck_and_shoulders(img, spec, skin, skin_sh, garment)
	# the hood — arcs over crown and down the back (elders)
	var hood := garment.darkened(0.15)
	if not child:
		for y in range(ht - 3, hb + 3):
			var b: int = backs.get(y, spec["bx"])
			@warning_ignore("integer_division")
			var reach: int = 3 + mini(3, (y - (ht - 3)) / 4)
			_hspan(img, b - reach, b - 1, y, hood)
		for y2 in range(ht - 3, ht - 1):
			_hspan(img, int(backs.get(ht, spec["bx"])) - 3,
					int(face.get(ht, spec["fx"])) - 2, y2, hood)
		_hspan(img, int(backs[ht]) - 1, int(face[ht]) - 3, ht - 1, hood.darkened(0.25))
	# the ancient eye — larger than the face wants
	var eye_y: int = ht + int(spec["eye_rel"])
	var ex: int = int(spec["fx"]) - 5
	var dark := Color("2a2018")
	_put(img, ex, eye_y, dark)
	_put(img, ex + 1, eye_y, dark)
	_put(img, ex, eye_y + 1, dark)
	_put(img, ex + 1, eye_y + 1, dark)
	_put(img, ex + 1, eye_y, CREAM)
	_put(img, int(spec["fx"]) + 1, ht + int(spec["nose_rel"]) + 2, skin_sh)
	_hspan(img, int(spec["fx"]) - 4, int(spec["fx"]) - 1, ht + int(spec["mouth_rel"]) + 1, skin_sh)
	# folded hands at the hem
	_hspan(img, ncx - 2, ncx + 2, H - 6, skin)
	_hspan(img, ncx - 2, ncx + 2, H - 5, skin_sh)


static func _paint_scarlet(img: Image, _pid: String, _seed: int) -> void:
	# the shaft of light, and her profile within it — hair streaming
	# BACK as light
	for y in range(1, H - 1):
		for x in range(1, W - 1):
			if x >= 10 and x <= 30:
				var edge: int = mini(x - 10, 30 - x)
				var c: Color
				var a: float
				if edge >= 6:
					c = Color("9a3448"); a = 0.85
				elif edge >= 3:
					c = Color("7a2438"); a = 0.6
				else:
					c = Color("58182a"); a = 0.3
				if a > _bayer(x, y):
					img.set_pixel(x, y, c)
	var skin := Color("f4ead8")
	var skin_sh := skin.darkened(0.12)
	var garment := Color("c03048")
	var spec: Dictionary = {
		"fx": 29, "bx": 12,
		"head_top": 7, "head_bot": 30, "crown": 4,
		"brow_rel": 9, "eye_rel": 11,
		"nose_rel": 13, "nose_len": 3,
		"mouth_rel": 17, "chin_rel": 20, "chin_slope": 1,
		"jaw_rel": 18, "jaw_slope": 2,
	}
	var prof := _build_profile(spec)
	var face: Dictionary = prof[0]
	var backs: Dictionary = prof[1]
	_fill_profile(img, face, backs, skin, skin_sh, WHITE)
	_neck_and_shoulders(img, spec, skin, skin_sh, garment)
	var ht: int = spec["head_top"]
	# hair as light, streaming back off the skull to the plate edge
	for y2 in range(ht - 1, ht + 16):
		var b: int = backs.get(y2, spec["bx"])
		var stream: int = 2 + (y2 - ht + 2) % 3
		_hspan(img, b - stream - 2, b - 1, y2, CREAM)
		if y2 < ht + 4:
			_hspan(img, b - 1, int(face.get(y2, spec["fx"])) - 3, y2, CREAM)
	var eye_y: int = ht + int(spec["eye_rel"])
	_put(img, int(spec["fx"]) - 5, eye_y, Color("6a1828"))
	_put(img, int(spec["fx"]) - 4, eye_y, Color("6a1828"))
	_hspan(img, int(spec["fx"]) - 4, int(spec["fx"]) - 1, ht + int(spec["mouth_rel"]) + 1, skin_sh)
	# three points of light leading her gaze
	for s in [[34, 8], [36, 12], [35, 16]]:
		_put(img, s[0], s[1], STAR)
