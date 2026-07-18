extends RefCounted
class_name VnBustPortrait
## Procedural VN portrait busts v2 — the last tier of CharLayer's
## portrait chain (3D GLB > composition > PNG > THIS), also drawn
## directly by the Community Planned board.
##
## v2 (2026-07-16): 60x64 canvas (was 30x32) at 5x upscale into the
## same 300x320 slot. Real eyes (sclera / iris / pupil / catchlight),
## two-shade skin+hair ramps with a rim-light column, brow+mouth
## expression shapes, blush / sweat-drop accents, and a BLINK frame
## (frame="blink") that CharLayer swaps in on a timer. Layout was
## prototyped and eyeballed in tools' bust_v2.py before porting.
##
## Same determinism contract as v1: hash bits pick skin tone, hair
## style + color, iris, glasses, beard; the accent color dresses the
## shirt; _OVERRIDES pins named characters. Same character = same
## face, forever (String.hash(), no RNG — the FeyPortrait rule).

const _W := 60
const _H := 64
const _SCALE := 5

const _SKIN_TONES: Array = [
	Color("#8a5a3c"), Color("#a06848"), Color("#b87c50"),
	Color("#c89060"), Color("#d8a878"), Color("#e8c098"),
	Color("#f0d2b4"),   # 6 fair (append-only — see hash freeze below)
]
const _HAIR_COLORS: Array = [
	Color("#181410"), Color("#30241a"), Color("#4a3020"),
	Color("#6a4a28"), Color("#8a6a38"), Color("#4a4a52"),
	Color("#7a4838"), Color("#c8b090"),
	Color("#b25422"),   # 8 ginger (append-only — see hash freeze below)
]
const _IRIS_COLORS: Array = [
	Color("#2e2014"), Color("#24382a"), Color("#283448"),
	Color("#50361e"), Color("#3a3a40"),
]
const _INK := Color("#100c0a")
const _SCLERA := Color("#eae8e2")
const _BLUSH := Color("#d8746a")
const _SWEAT := Color("#9cc8e0")
const _CATCH := Color("#ffffff")
const _GOLD := Color("#d8b050")

# Per-character art overrides. The hash gives everyone a deterministic
# but arbitrary face; named characters we want to READ a specific way
# get pinned here. Keys are the slugified char id (lowercase, spaces →
# "_"). Fields (all optional): hair_style (0-6), hair_color (index into
# _HAIR_COLORS), glasses ("none"/"regular"/"round"), beard (bool),
# skin_tone (index into _SKIN_TONES, 0 darkest → 5 lightest),
# face ("oval"/"narrow"/"wide"/"round"), age ("adult"/"elder" — elder
# adds forehead creases, crow's feet, nasolabial + under-eye lines),
# collar ("v"/"shirt"/"tee"/"hoodie"), earrings (bool), freckles (bool).
# hair_style: 0 short crop · 1 side part (long fringe) · 2 long-past-
# jaw · 3 curly/afro · 4 bald · 5 cap · 6 feminine long · 7 ponytail ·
# 8 buzz · 9 middle-part curtains · 10 bun · 11 slicked back.
const _OVERRIDES: Dictionary = {
	# Maya Miller — teenage girl: feminine long hair + big round CLEAR
	# glasses (not the dark rings that read as sunglasses).
	"maya":        {"hair_style": 6, "glasses": "round", "beard": false, "freckles": true},
	"maya_daigle": {"hair_style": 6, "glasses": "round", "beard": false, "freckles": true},
	"maya_miller": {"hair_style": 6, "glasses": "round", "beard": false, "freckles": true},
	# Samantha Miller — 17, back on the pixel bust.
	"sam":         {"hair_style": 6, "hair_color": 8, "skin_tone": 6,
					"beard": false, "collar": "tee", "face": "round"},
	"sam_miller":  {"hair_style": 6, "hair_color": 8, "skin_tone": 6,
					"beard": false, "collar": "tee", "face": "round"},
	# John Frank — thin young white man, long dark bangs.
	"john":        {"hair_style": 1, "hair_color": 0, "skin_tone": 5,
					"beard": false, "glasses": "none", "collar": "shirt",
					"face": "narrow"},
	"john_frank":  {"hair_style": 1, "hair_color": 0, "skin_tone": 5,
					"beard": false, "glasses": "none", "collar": "shirt",
					"face": "narrow"},
	# Frasier Temple — young Black man, slightly disheveled afro.
	"frasier":        {"hair_style": 3, "hair_color": 0, "skin_tone": 0,
					   "beard": false, "glasses": "none"},
	"frasier_temple": {"hair_style": 3, "hair_color": 0, "skin_tone": 0,
					   "beard": false, "glasses": "none"},
	# Graciela Ramos — 71, Diego's abuela: long grey hair + reading
	# glasses (the hash was rendering her bald and bearded).
	"graciela":       {"hair_style": 10, "hair_color": 5, "beard": false,
					   "glasses": "regular", "age": "elder", "earrings": true},
	"graciela_ramos": {"hair_style": 10, "hair_color": 5, "beard": false,
					   "glasses": "regular", "age": "elder", "earrings": true},

	# ── COMMUNITY PLANNED roster ──────────────────────────────────
	"vagrant":       {"hair_style": 0, "hair_color": 1, "beard": true},
	"cicada":        {"hair_style": 4, "hair_color": 0, "beard": false},
	"moth":          {"hair_style": 3, "hair_color": 5, "beard": false},
	"steamboat":     {"hair_style": 2, "hair_color": 5, "beard": true, "age": "elder"},
	"weir":          {"hair_style": 1, "hair_color": 1, "beard": false},
	"filly":         {"hair_style": 6, "hair_color": 6, "beard": false},
	"starling":      {"hair_style": 3, "hair_color": 0, "beard": false},
	"husk":          {"hair_style": 4, "hair_color": 0, "beard": true},
	"mackenzie":     {"hair_style": 2, "glasses": "regular", "beard": false},
	"the_surviving_son": {"hair_style": 0, "hair_color": 1, "beard": true},
	"elicia":        {"hair_style": 6, "glasses": "none", "beard": false},
	"nicola":        {"hair_style": 6, "beard": false},
	"the_small_wood_contact_jules": {"hair_style": 0, "beard": true},

	# ── LAND OF MILK & HONEY (vol7 / Smolvud) ─────────────────────
	"tem":     {"hair_style": 6, "beard": false, "earrings": true},
	"kai":     {"hair_style": 9, "beard": false, "collar": "hoodie"},
	"lena":    {"hair_style": 6, "hair_color": 1, "skin_tone": 2, "beard": false},
	"finn":    {"hair_style": 1, "beard": false},
	"per":     {"hair_style": 8, "hair_color": 5, "beard": true, "age": "elder"},
	"cale":    {"hair_style": 1, "beard": false},
	"hans":    {"hair_style": 0, "hair_color": 5, "beard": true, "age": "elder"},
	"roy":     {"hair_style": 0, "beard": false},
	"marina":  {"hair_style": 2, "beard": false},
	"marit":   {"hair_style": 6, "hair_color": 7, "beard": false},
	"aud":     {"hair_style": 6, "beard": false},
	"nate":    {"hair_style": 1, "beard": false},
	"petra":   {"hair_style": 2, "glasses": "regular", "beard": false},
	"wren":    {"hair_style": 6, "beard": false},
}

static var _cache: Dictionary = {}


static func texture(key: String, expr: String, accent: Color,
		frame: String = "open") -> ImageTexture:
	var fam := _expr_family(expr)
	var cache_key := "%s|%s|%s|%s" % [key, fam, accent.to_html(false), frame]
	if _cache.has(cache_key):
		return _cache[cache_key]
	var tex := _build(key, fam, accent, frame)
	_cache[cache_key] = tex
	return tex


# Collapse the scene-JSON expression vocabulary into the families
# the face can actually draw. Mirrors the EXPR_TINTS groupings.
static func _expr_family(expr: String) -> String:
	match expr:
		"happy", "excited", "pleased", "warm":
			return "happy"
		"sad", "melancholy", "upset":
			return "sad"
		"angry", "furious", "frustrated":
			return "angry"
		"surprised", "shocked", "wide":
			return "surprised"
		"tired":
			return "tired"
		"nervous", "scared", "uneasy":
			return "nervous"
		_:
			return "neutral"


static func _build(key: String, fam: String, accent: Color, frame: String) -> ImageTexture:
	var img := Image.create(_W, _H, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))

	var h: int = absi(key.hash())
	# Hash rolls stay on the ORIGINAL palette ranges (6 skins, 8 hairs)
	# so appending override-only colors never reshuffles hash faces.
	var skin: Color = _SKIN_TONES[(h >> 2) % 6]
	var hair: Color = _HAIR_COLORS[(h >> 8) % 8]
	var iris: Color = _IRIS_COLORS[(h >> 16) % _IRIS_COLORS.size()]
	var style: int = (h >> 5) % 6
	var has_glasses: bool = (h >> 11) % 4 == 0
	var gkind: String = "regular"
	var has_beard: bool = (h >> 13) % 3 == 0 and style != 5

	var faces: Array = ["oval", "narrow", "wide", "round"]
	var face: String = faces[(h >> 18) % 4]
	var freckles: bool = (h >> 21) % 6 == 0
	var age: String = "adult"
	var earrings: bool = false
	var collar: String = "v"

	var ov: Dictionary = _OVERRIDES.get(key, {})
	if ov.has("face"):
		face = String(ov["face"])
	if ov.has("age"):
		age = String(ov["age"])
	if ov.has("earrings"):
		earrings = bool(ov["earrings"])
	if ov.has("freckles"):
		freckles = bool(ov["freckles"])
	if ov.has("collar"):
		collar = String(ov["collar"])
	if ov.has("skin_tone"):
		skin = _SKIN_TONES[int(ov["skin_tone"]) % _SKIN_TONES.size()]
	if ov.has("hair_color"):
		hair = _HAIR_COLORS[int(ov["hair_color"]) % _HAIR_COLORS.size()]
	if ov.has("hair_style"):
		style = int(ov["hair_style"])
	if ov.has("beard"):
		has_beard = bool(ov["beard"])
	if ov.has("glasses"):
		var g: String = String(ov["glasses"])
		has_glasses = g != "none"
		if has_glasses:
			gkind = g

	var skin_dk: Color = skin.darkened(0.20)
	var skin_dk2: Color = skin.darkened(0.34)
	var skin_lt: Color = skin.lightened(0.14)
	var hair_dk: Color = hair.darkened(0.28)
	var hair_lt: Color = hair.lightened(0.25)
	var shirt := Color(accent.r * 0.55, accent.g * 0.55, accent.b * 0.55, 1.0)
	var shirt_lt := Color(accent.r * 0.75, accent.g * 0.75, accent.b * 0.75, 1.0)
	var shirt_dk := Color(shirt.r * 0.7, shirt.g * 0.7, shirt.b * 0.7, 1.0)
	var lip: Color = skin.lerp(Color("#a8504a"), 0.45)
	var cheek: int = 1 if face == "narrow" else 0
	var widen: int = 1 if face == "wide" else 0
	var jaw_extra: int = 1 if face == "narrow" or face == "oval" else 2 if face == "round" else 0
	var x_lo: int = 20 + cheek - widen
	var x_hi: int = 40 - cheek + widen

	# ── torso: shoulders widening to frame bottom, two-tone ──────
	for y in range(47, _H):
		var half: int = mini(27, 11 + (y - 47) * 3)
		_hspan(img, 30 - half, 30 + half, y, shirt)
	_hspan(img, 18, 42, 47, shirt_lt)                   # shoulder seam light
	match collar:
		"hoodie":
			for y in range(41, 47):                     # hood bulk behind the neck
				_hspan(img, 22, 25, y, shirt_dk)
				_hspan(img, 35, 38, y, shirt_dk)
			_hspan(img, 20, 40, 47, shirt_dk)
			_hspan(img, 19, 41, 48, shirt_dk)
			for dy in range(50, 53):                    # drawstrings
				_put(img, 28, dy, shirt_lt)
				_put(img, 32, dy, shirt_lt)
		"shirt":
			for i in range(4):                          # pointed collar flaps
				_hspan(img, 25 - i, 26, 48 + i, shirt_lt)
				_hspan(img, 34, 35 + i, 48 + i, shirt_lt)
			_hspan(img, 27, 33, 48, skin_dk)            # open throat
			_hspan(img, 28, 32, 49, skin_dk)
		"tee":
			_hspan(img, 24, 36, 48, shirt_lt)           # round neck band
			_hspan(img, 26, 34, 49, shirt_lt)
		_:
			for y in range(48, 54):                     # default v-notch
				var wdt: int = maxi(0, 5 - (y - 48))
				_hspan(img, 30 - wdt / 2 - 1, 30 + wdt / 2 + 1, y, skin_dk)
	# ── neck ─────────────────────────────────────────────────────
	for y in range(40, 48):
		_hspan(img, 26, 34, y, skin_dk)
	# ── head block: face shape + stepped corners + baked ramp ────
	for y in range(10, 40):
		var inset: int = 0
		if y == 10 or y == 39: inset = 3
		elif y == 11 or y == 38: inset = 2
		elif y == 12 or y == 37: inset = 1
		if y >= 37:
			inset += jaw_extra                          # face-shape jaw taper
		elif y >= 34 and jaw_extra >= 2:
			inset += 1
		for x in range(x_lo + inset, x_hi + 1 - inset):
			var c: Color = skin
			if x <= x_lo + 1: c = skin_dk               # shadow side
			elif x >= x_hi - 2: c = skin_lt             # rim-light side
			_put(img, x, y, c)
	_hspan(img, 23, 37, 38, skin_dk)                    # jaw shade
	for y in range(24, 29):                             # ears
		_hspan(img, x_lo - 2, x_lo - 1, y, skin)
		_hspan(img, x_hi + 1, x_hi + 2, y, skin)
	_put(img, x_lo - 1, 26, skin_dk)
	_put(img, x_hi + 1, 26, skin_dk)
	if earrings:
		for ey in [29, 30]:
			_put(img, x_lo - 2, ey, _GOLD)
			_put(img, x_hi + 2, ey, _GOLD)

	# ── brows ────────────────────────────────────────────────────
	var by := 21
	if fam == "surprised": by = 19
	if fam == "tired": by = 22
	if fam == "angry":
		for i in range(5):
			_put(img, 23 + i, by + 1 + i / 3, _INK)
			_put(img, 37 - i, by + 1 + i / 3, _INK)
	elif fam == "sad":
		for i in range(5):
			_put(img, 23 + i, by + 2 - i / 3, _INK)
			_put(img, 37 - i, by + 2 - i / 3, _INK)
	else:
		_hspan(img, 23, 27, by, hair_dk)
		_hspan(img, 33, 37, by, hair_dk)
		_hspan(img, 23, 27, by + 1, _INK)
		_hspan(img, 33, 37, by + 1, _INK)

	# ── eyes (open or the blink frame) ───────────────────────────
	if frame == "blink" or fam == "tired":
		_hspan(img, 23, 27, 26, _INK)
		_hspan(img, 33, 37, 26, _INK)
		_hspan(img, 24, 26, 27, skin_dk)
		_hspan(img, 34, 36, 27, skin_dk)
	else:
		for x0 in [23, 33]:
			_hspan(img, x0, x0 + 4, 24, _INK)           # upper lash line
			_hspan(img, x0, x0 + 4, 25, _SCLERA)
			_hspan(img, x0, x0 + 4, 26, _SCLERA)
			_hspan(img, x0 + 1, x0 + 3, 27, skin_dk)    # lower lid
		var big: bool = fam == "surprised"
		for ix in [25, 35]:
			_put(img, ix, 25, iris)
			_put(img, ix + 1, 25, iris)
			_put(img, ix, 26, iris)
			_put(img, ix + 1, 26, iris)
			_put(img, ix + 1, 26, _INK)                 # pupil
			if big:
				_put(img, ix - 1, 25, iris)
				_put(img, ix + 2, 26, iris)
			_put(img, ix, 25, _CATCH)                   # catchlight
	# ── nose ─────────────────────────────────────────────────────
	for y in range(28, 32):
		_put(img, 31, y, skin_dk)
	_hspan(img, 29, 31, 32, skin_dk)
	_put(img, 28, 32, skin_dk2)
	_put(img, 32, 32, skin_dk2)
	# ── age set (elder): forehead creases, crow's feet, nasolabial
	# folds, under-eye lines ─────────────────────────────────────
	if age == "elder":
		_hspan(img, 25, 35, 17, skin_dk)
		_hspan(img, 27, 33, 15, skin_dk)
		_put(img, 22, 25, skin_dk2)
		_put(img, 38, 25, skin_dk2)
		_put(img, 22, 27, skin_dk2)
		_put(img, 38, 27, skin_dk2)
		_hspan(img, 24, 25, 29, skin_dk)
		_hspan(img, 35, 36, 29, skin_dk)
		_put(img, 27, 33, skin_dk2)
		_put(img, 26, 34, skin_dk2)
		_put(img, 33, 33, skin_dk2)
		_put(img, 34, 34, skin_dk2)
	if freckles:
		for fp in [Vector2i(24, 30), Vector2i(26, 31), Vector2i(23, 32),
				Vector2i(36, 30), Vector2i(34, 31), Vector2i(37, 32)]:
			_put(img, fp.x, fp.y, skin_dk2)
	# ── mouth by family ──────────────────────────────────────────
	match fam:
		"happy":
			_put(img, 26, 34, _INK)
			_put(img, 34, 34, _INK)
			_hspan(img, 27, 33, 35, _INK)
			_hspan(img, 28, 32, 36, lip)
		"sad":
			_put(img, 26, 36, _INK)
			_put(img, 34, 36, _INK)
			_hspan(img, 27, 33, 35, _INK)
		"surprised":
			for y in [34, 35, 36]:
				_hspan(img, 28, 31, y, _INK)
			_hspan(img, 29, 30, 35, lip.darkened(0.3))
		"angry":
			_hspan(img, 26, 34, 35, _INK)
			_hspan(img, 27, 33, 36, skin_dk2)
		"nervous":
			for i in range(8):
				_put(img, 26 + i, 35 + (i % 2), _INK)
		_:
			_hspan(img, 27, 33, 35, _INK)
			_hspan(img, 28, 32, 36, lip)
	# ── expression accents ───────────────────────────────────────
	if fam == "happy" or fam == "nervous":
		for bx0 in [22, 35]:
			_hspan(img, bx0, bx0 + 2, 31, _BLUSH)
			_hspan(img, bx0, bx0 + 2, 32, _BLUSH)
	if fam == "nervous":
		_put(img, 41, 17, _SWEAT)
		_put(img, 41, 18, _SWEAT)
		_put(img, 40, 19, _SWEAT)
		_put(img, 41, 19, _SWEAT)

	# ── hair (textured strands + rim light via _hair_px) ─────────
	match style:
		0:  # short crop
			for y in range(5, 14):
				var inset: int = 3 if y == 5 else 2 if y == 6 else 1 if y == 7 else 0
				for x in range(20 + inset, 41 - inset):
					_hair_px(img, x, y, h, style, hair, hair_dk, hair_lt)
			for y in range(14, 17):
				for x in [20, 21, 39, 40]:
					_hair_px(img, x, y, h, style, hair, hair_dk, hair_lt)
		1:  # side part — long fringe falls left
			for y in range(5, 14):
				var inset: int = 3 if y == 5 else 1 if y == 6 else 0
				for x in range(20 + inset, 41 - inset):
					_hair_px(img, x, y, h, style, hair, hair_dk, hair_lt)
			for y in range(14, 18):
				for x in range(20, 30 - (y - 14) * 2):
					_hair_px(img, x, y, h, style, hair, hair_dk, hair_lt)
			for x in range(20, 23):
				for y in range(18, 21):
					_hair_px(img, x, y, h, style, hair, hair_dk, hair_lt)
		2:  # long past the jaw
			for y in range(5, 14):
				var inset: int = 3 if y == 5 else 1 if y == 6 else 0
				for x in range(20 + inset, 41 - inset):
					_hair_px(img, x, y, h, style, hair, hair_dk, hair_lt)
			for y in range(14, 40):
				for x in [18, 19, 20, 40, 41, 42]:
					_hair_px(img, x, y, h, style, hair, hair_dk, hair_lt)
			for x in range(18, 23):
				_hair_px(img, x, 40, h, style, hair, hair_dk, hair_lt)
			for x in range(38, 43):
				_hair_px(img, x, 40, h, style, hair, hair_dk, hair_lt)
		3:  # curly / afro — dense halo
			for y in range(3, 16):
				for x in range(17, 44):
					var dx: float = float(x - 30)
					var dy: float = float(y - 9)
					if dx * dx * 0.55 + dy * dy * 1.3 < 64.0 and _hash01(x, y, h) > 0.04:
						_hair_px(img, x, y, h, style, hair, hair_dk, hair_lt)
			for y in range(16, 22):
				if _hash01(3, y, h) > 0.4:
					_hair_px(img, 18, y, h, style, hair, hair_dk, hair_lt)
					_hair_px(img, 19, y, h, style, hair, hair_dk, hair_lt)
				if _hash01(43, y, h) > 0.4:
					_hair_px(img, 41, y, h, style, hair, hair_dk, hair_lt)
					_hair_px(img, 42, y, h, style, hair, hair_dk, hair_lt)
		4:  # bald / shaved
			_hspan(img, 22, 38, 10, skin_dk)
			_hspan(img, 23, 37, 11, skin_dk)
		5:  # cap in the shirt color
			for y in range(5, 13):
				var inset: int = 3 if y == 5 else 1 if y == 6 else 0
				_hspan(img, 20 + inset, 40 - inset, y, shirt)
			_hspan(img, 17, 45, 13, shirt_lt)
			_hspan(img, 17, 45, 14, shirt.darkened(0.3))
			_put(img, 30, 5, shirt_lt)
		6:  # feminine long — crown + bangs sweep + curtains to shoulders
			for y in range(4, 14):
				var inset: int = 3 if y == 4 else 1 if y == 5 else 0
				for x in range(19 + inset, 42 - inset):
					_hair_px(img, x, y, h, style, hair, hair_dk, hair_lt)
			for x in range(20, 41):
				var fy: int = 16 if x >= 27 and x <= 33 else 17
				for y in range(14, fy + 1):
					if not (x >= 28 and x <= 32 and y > 14):
						_hair_px(img, x, y, h, style, hair, hair_dk, hair_lt)
			for y in range(14, 45):
				for x in [17, 18, 19, 41, 42, 43]:
					_hair_px(img, x, y, h, style, hair, hair_dk, hair_lt)
			for y in range(20, 45):
				_hair_px(img, 20, y, h, style, hair, hair_dk, hair_lt)
				_hair_px(img, 40, y, h, style, hair, hair_dk, hair_lt)
			for x in range(17, 22):
				_hair_px(img, x, 45, h, style, hair, hair_dk, hair_lt)
			for x in range(39, 44):
				_hair_px(img, x, 45, h, style, hair, hair_dk, hair_lt)
		7:  # ponytail — crown swept back, tail over one shoulder
			for y in range(5, 14):
				var inset: int = 3 if y == 5 else 1 if y == 6 else 0
				for x in range(20 + inset, 41 - inset):
					_hair_px(img, x, y, h, style, hair, hair_dk, hair_lt)
			for y in range(14, 20):
				for x in [20, 21, 39, 40]:
					_hair_px(img, x, y, h, style, hair, hair_dk, hair_lt)
			for y in range(12, 18):                     # gathered knot
				for x in range(41, 44):
					_hair_px(img, x, y, h, style, hair, hair_dk, hair_lt)
			_hspan(img, 41, 43, 18, _GOLD.darkened(0.1))
			for y in range(19, 40):                     # the tail
				var wob: int = 1 if _hash01(2, y, h) > 0.5 else 0
				for x in range(42 + wob, 45 + wob):
					_hair_px(img, x, y, h, style, hair, hair_dk, hair_lt)
			for x in range(42, 46):
				_hair_px(img, x, 40, h, style, hair, hair_dk, hair_lt)
		8:  # buzz cut — sparse stubble over the scalp
			for y in range(6, 14):
				var inset: int = 3 if y == 6 else 1 if y == 7 else 0
				for x in range(20 + inset, 41 - inset):
					if _hash01(x, y, h) > 0.35:
						_put(img, x, y, hair_dk)
					else:
						_put(img, x, y, skin_dk)
			_hspan(img, 20, 40, 14, skin_dk)
		9:  # middle part — curtains framing the forehead
			for y in range(4, 13):
				var inset: int = 3 if y == 4 else 1 if y == 5 else 0
				for x in range(20 + inset, 41 - inset):
					_hair_px(img, x, y, h, style, hair, hair_dk, hair_lt)
			for x in range(20, 41):
				if x >= 29 and x <= 31:
					continue
				var depth: int = 19 - absi(x - 30) / 2
				for y in range(13, depth):
					_hair_px(img, x, y, h, style, hair, hair_dk, hair_lt)
			for y in range(13, 24):
				for x in [20, 21, 39, 40]:
					_hair_px(img, x, y, h, style, hair, hair_dk, hair_lt)
		10: # bun — pulled back tight + a bun on top
			for y in range(6, 14):
				var inset: int = 3 if y == 6 else 1 if y == 7 else 0
				for x in range(20 + inset, 41 - inset):
					_hair_px(img, x, y, h, style, hair, hair_dk, hair_lt)
			for y in range(1, 6):                       # the bun
				var wdt: int = 4 if y >= 2 and y <= 4 else 2
				for x in range(30 - wdt, 31 + wdt):
					_hair_px(img, x, y, h, style, hair, hair_dk, hair_lt)
			_hspan(img, 27, 33, 6, hair_dk)             # gathered ring
			for y in range(14, 18):
				_hair_px(img, 20, y, h, style, hair, hair_dk, hair_lt)
				_hair_px(img, 39, y, h, style, hair, hair_dk, hair_lt)
		11: # slicked back — streaked crown, no fringe
			for y in range(5, 14):
				var inset: int = 3 if y == 5 else 1 if y == 6 else 0
				for x in range(20 + inset, 41 - inset):
					if y % 3 == 0 and _hash01(x, y, h) > 0.4:
						_put(img, x, y, hair_lt)
					elif _hash01(x * 3, y, h) < 0.2:
						_put(img, x, y, hair_dk)
					else:
						_put(img, x, y, hair)
			for y in range(14, 16):
				for x in [20, 21, 39, 40]:
					_hair_px(img, x, y, h, style, hair, hair_dk, hair_lt)

	# ── glasses ──────────────────────────────────────────────────
	if has_glasses:
		if gkind == "round":
			for cx0 in [25, 35]:
				for off in [Vector2i(-2, -1), Vector2i(-2, 0), Vector2i(-2, 1),
						Vector2i(2, -1), Vector2i(2, 0), Vector2i(2, 1),
						Vector2i(-1, -2), Vector2i(0, -2), Vector2i(1, -2),
						Vector2i(-1, 2), Vector2i(0, 2), Vector2i(1, 2)]:
					_put(img, cx0 + off.x, 26 + off.y, _INK)
			_put(img, 30, 26, _INK)
			_hspan(img, 19, 21, 26, _INK)
			_hspan(img, 39, 41, 26, _INK)
		else:
			for x0 in [22, 32]:
				_hspan(img, x0, x0 + 6, 23, _INK)
				_hspan(img, x0, x0 + 6, 28, _INK)
				for y in range(24, 28):
					_put(img, x0, y, _INK)
					_put(img, x0 + 6, y, _INK)
			_hspan(img, 29, 31, 25, _INK)
			_hspan(img, 19, 21, 25, _INK)
			_hspan(img, 39, 41, 25, _INK)

	# ── beard — textured jaw + chin block + moustache ────────────
	if has_beard:
		for y in range(33, 40):
			for x in range(22, 39):
				var edge: bool = x < 24 or x > 36 or y > 36
				if edge and _is_skin(img, x, y, skin, skin_dk, skin_lt, skin_dk2):
					_put(img, x, y, hair if _hash01(x, y, h) > 0.12 else hair_dk)
		_hspan(img, 26, 34, 33, hair_dk)

	img.resize(_W * _SCALE, _H * _SCALE, Image.INTERPOLATE_NEAREST)
	return ImageTexture.create_from_image(img)


# ── low-level helpers ────────────────────────────────────────────

static func _put(img: Image, x: int, y: int, c: Color) -> void:
	if x >= 0 and x < _W and y >= 0 and y < _H:
		img.set_pixel(x, y, c)


static func _hspan(img: Image, x0: int, x1: int, y: int, c: Color) -> void:
	for x in range(x0, x1 + 1):
		_put(img, x, y, c)


static func _hair_px(img: Image, x: int, y: int, h: int, style: int,
		hair: Color, hair_dk: Color, hair_lt: Color) -> void:
	var c: Color = hair
	if _hash01(x * 7 + style, y, h) < 0.18:
		c = hair_dk                                     # strand texture
	if x >= 38:
		c = hair_lt if _hash01(x, y, h) < 0.5 else hair # rim-light side
	_put(img, x, y, c)


static func _is_skin(img: Image, x: int, y: int, s0: Color, s1: Color,
		s2: Color, s3: Color) -> bool:
	if x < 0 or x >= _W or y < 0 or y >= _H:
		return false
	var p: Color = img.get_pixel(x, y)
	for s in [s0, s1, s2, s3]:
		if absf(p.r - s.r) < 0.02 and absf(p.g - s.g) < 0.02 and absf(p.b - s.b) < 0.02:
			return true
	return false


static func _hash01(x: int, y: int, s: int) -> float:
	var n: int = (x * 374761393 + y * 668265263 + s * 1442695041) & 0xFFFFFFFF
	n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
	n = n ^ (n >> 16)
	return float(n & 0xFFFF) / 65536.0
