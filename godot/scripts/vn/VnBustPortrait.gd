extends RefCounted
class_name VnBustPortrait
## Procedural VN portrait busts — the last tier of CharLayer's
## portrait chain (3D GLB > composition > PNG > THIS). Replaces the
## old oval-and-rectangle placeholder with a readable chunky-pixel
## bust derived deterministically from the character key, in the
## FeyPortrait manner: hash bits pick skin tone, hair style + color,
## glasses, beard; the accent color dresses the shirt; the current
## expression drives brows, eyes, and mouth. Same character = same
## face, forever (String.hash(), no RNG).
##
## Canvas 30x32, nearest-upscaled x10 to the 300x320 slot.

const _W := 30
const _H := 32
const _SCALE := 10

const _SKIN_TONES: Array = [
	Color("#8a5a3c"), Color("#a06848"), Color("#b87c50"),
	Color("#c89060"), Color("#d8a878"), Color("#e8c098"),
]
const _HAIR_COLORS: Array = [
	Color("#181410"), Color("#30241a"), Color("#4a3020"),
	Color("#6a4a28"), Color("#8a6a38"), Color("#4a4a52"),
	Color("#7a4838"), Color("#c8b090"),
]
const _INK := Color("#100c0a")

static var _cache: Dictionary = {}


static func texture(key: String, expr: String, accent: Color) -> ImageTexture:
	var fam := _expr_family(expr)
	var cache_key := "%s|%s|%s" % [key, fam, accent.to_html(false)]
	if _cache.has(cache_key):
		return _cache[cache_key]
	var tex := _build(key, fam, accent)
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


static func _build(key: String, fam: String, accent: Color) -> ImageTexture:
	var img := Image.create(_W, _H, false, Image.FORMAT_RGBA8)
	# Transparent ground — the slot's static backdrop shows through.
	img.fill(Color(0, 0, 0, 0))

	var h: int = absi(key.hash())
	var skin: Color = _SKIN_TONES[(h >> 2) % _SKIN_TONES.size()]
	var skin_dk: Color = skin.darkened(0.22)
	var hair: Color = _HAIR_COLORS[(h >> 8) % _HAIR_COLORS.size()]
	var hair_style: int = (h >> 5) % 6
	var has_glasses: bool = (h >> 11) % 4 == 0
	var has_beard: bool = (h >> 13) % 3 == 0 and hair_style != 5
	var shirt: Color = Color(accent.r * 0.55, accent.g * 0.55, accent.b * 0.55, 1.0)
	var shirt_lt: Color = Color(accent.r * 0.75, accent.g * 0.75, accent.b * 0.75, 1.0)

	# ── Torso: shoulders widening to the frame bottom ─────────────
	for y in range(23, _H):
		var half: int = mini(11, 6 + (y - 23))
		_hspan(img, 15 - half, 15 + half, y, shirt)
	_hspan(img, 15 - 6, 15 + 6, 23, shirt_lt)          # shoulder light
	for y in range(24, _H):                             # collar notch
		if y < 27:
			_hspan(img, 14, 16, y, skin_dk)
	# ── Neck ──────────────────────────────────────────────────────
	for y in range(20, 24):
		_hspan(img, 13, 17, y, skin_dk)
	# ── Head: rounded block ───────────────────────────────────────
	for y in range(5, 20):
		var x0: int = 10
		var x1: int = 20
		if y == 5 or y == 19:
			x0 = 12; x1 = 18
		elif y == 6 or y == 18:
			x0 = 11; x1 = 19
		_hspan(img, x0, x1, y, skin)
	# Jaw shading + ears.
	_hspan(img, 11, 19, 18, skin_dk)
	_put(img, 9, 12, skin); _put(img, 9, 13, skin_dk)
	_put(img, 21, 12, skin); _put(img, 21, 13, skin_dk)

	# ── Hair ──────────────────────────────────────────────────────
	match hair_style:
		0:  # short crop
			for y in range(3, 7):
				var pad: int = 1 if y == 3 else 0
				_hspan(img, 10 + pad, 20 - pad, y, hair)
			_hspan(img, 10, 12, 7, hair)
			_hspan(img, 18, 20, 7, hair)
		1:  # side part — fringe falls to one side
			for y in range(3, 7):
				_hspan(img, 10, 20, y, hair)
			_hspan(img, 10, 14, 7, hair)
			_hspan(img, 10, 12, 8, hair)
		2:  # long — down past the jaw
			for y in range(3, 7):
				_hspan(img, 10, 20, y, hair)
			for y in range(7, 19):
				_hspan(img, 9, 10, y, hair)
				_hspan(img, 20, 21, y, hair)
			_hspan(img, 9, 11, 19, hair)
			_hspan(img, 19, 21, 19, hair)
		3:  # curly — dense halo with a ragged edge
			for y in range(2, 8):
				for x in range(9, 22):
					if _hash01(x, y, h) > 0.12:
						_put(img, x, y, hair)
			for y in range(8, 11):
				if _hash01(3, y, h) > 0.4:
					_put(img, 9, y, hair)
				if _hash01(27, y, h) > 0.4:
					_put(img, 21, y, hair)
		4:  # bald / shaved — brow shadow only
			_hspan(img, 11, 19, 4, skin_dk)
		5:  # cap in the shirt color
			for y in range(3, 7):
				_hspan(img, 10, 20, y, shirt)
			_hspan(img, 9, 23, 7, shirt_lt)             # brim
			_put(img, 15, 3, shirt_lt)                  # button

	# ── Brows ─────────────────────────────────────────────────────
	var brow_y := 10
	match fam:
		"surprised":
			brow_y = 9
		"tired":
			brow_y = 11
	if fam == "angry":
		_put(img, 12, 11, _INK); _put(img, 13, 10, _INK)
		_put(img, 18, 11, _INK); _put(img, 17, 10, _INK)
	elif fam == "sad":
		_put(img, 12, 10, _INK); _put(img, 13, 11, _INK)
		_put(img, 18, 10, _INK); _put(img, 17, 11, _INK)
	else:
		_hspan(img, 12, 14, brow_y, _INK)
		_hspan(img, 17, 19, brow_y, _INK)

	# ── Eyes ──────────────────────────────────────────────────────
	if fam == "tired":
		_hspan(img, 12, 14, 13, _INK)
		_hspan(img, 17, 19, 13, _INK)
	elif fam == "surprised":
		for p in [[12, 12], [13, 12], [12, 13], [13, 13],
				[17, 12], [18, 12], [17, 13], [18, 13]]:
			_put(img, p[0], p[1], _INK)
	else:
		_put(img, 12, 13, _INK); _put(img, 13, 13, _INK)
		_put(img, 17, 13, _INK); _put(img, 18, 13, _INK)
	if has_glasses:
		# Full lens rings (not corner dots — those read as mesh).
		for lx in [11, 16]:
			_hspan(img, lx, lx + 3, 12, _INK)
			_hspan(img, lx, lx + 3, 14, _INK)
			_put(img, lx, 13, _INK)
			_put(img, lx + 3, 13, _INK)
		_put(img, 15, 13, _INK)

	# ── Nose ──────────────────────────────────────────────────────
	_put(img, 15, 15, skin_dk)

	# ── Mouth by expression ───────────────────────────────────────
	match fam:
		"happy":
			_put(img, 13, 16, _INK)
			_hspan(img, 14, 16, 17, _INK)
			_put(img, 17, 16, _INK)
		"sad":
			_put(img, 13, 17, _INK)
			_hspan(img, 14, 16, 16, _INK)
			_put(img, 17, 17, _INK)
		"surprised":
			_put(img, 14, 16, _INK); _put(img, 15, 16, _INK)
			_put(img, 14, 17, _INK); _put(img, 15, 17, _INK)
		"angry":
			_hspan(img, 13, 17, 17, _INK)
		"nervous":
			_put(img, 13, 16, _INK); _put(img, 14, 17, _INK)
			_put(img, 15, 16, _INK); _put(img, 16, 17, _INK)
		_:
			_hspan(img, 13, 16, 17, _INK)

	# ── Beard — solid chin block + jaw edges, no speckle ──────────
	if has_beard:
		_hspan(img, 12, 18, 18, hair)
		_hspan(img, 12, 18, 19, hair)
		_put(img, 11, 17, hair); _put(img, 19, 17, hair)
		_put(img, 11, 16, hair); _put(img, 19, 16, hair)

	img.resize(_W * _SCALE, _H * _SCALE, Image.INTERPOLATE_NEAREST)
	return ImageTexture.create_from_image(img)


# ── low-level helpers ────────────────────────────────────────────

static func _put(img: Image, x: int, y: int, c: Color) -> void:
	if x >= 0 and x < _W and y >= 0 and y < _H:
		img.set_pixel(x, y, c)


static func _hspan(img: Image, x0: int, x1: int, y: int, c: Color) -> void:
	for x in range(x0, x1 + 1):
		_put(img, x, y, c)


static func _hash01(x: int, y: int, s: int) -> float:
	var n: int = x * 374761393 + y * 668265263 + s * 1442695041
	n = (n ^ (n >> 13)) * 1274126177
	n = n ^ (n >> 16)
	return float(n & 0xFFFF) / 65536.0
