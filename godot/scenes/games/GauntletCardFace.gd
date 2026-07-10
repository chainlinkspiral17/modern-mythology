extends RefCounted
class_name GauntletCardFace
## Procedural card faces for TAROT GAUNTLET — the third tier of the
## project's art discipline (authored PNG > procedural > plain text).
## assets/gallery/cards/ ships empty until the studio generates real
## art; until then every card face derives deterministically from the
## card id: same card = same face, forever (String.hash(), no RNG —
## the FeyPortrait rule).
##
## 36x36 canvas, nearest-upscaled x3 to 108 (the hand-tile size).
## Field is a Bayer-dithered gradient in the deck's colors; the
## emblem shape, its satellites, and the accent shade come from the
## id hash; the pip row at the bottom is the card's time cost.

const _SIZE := 36
const _SCALE := 3

# Per-arcana accent hue — the gold-on-black gauntlet identity with
# one hue of the arcana's own.
const _ARCANA_ACCENT: Dictionary = {
	"fool":       Color(0.85, 0.68, 0.28),
	"magician":   Color(0.78, 0.32, 0.26),
	"priestess":  Color(0.34, 0.52, 0.72),
	"empress":    Color(0.38, 0.62, 0.38),
	"emperor":    Color(0.62, 0.62, 0.68),
	"hierophant": Color(0.76, 0.68, 0.42),
	"lovers":     Color(0.78, 0.46, 0.52),
	"chariot":    Color(0.52, 0.60, 0.68),
}

const _BAYER4: Array = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5]

static var _cache: Dictionary = {}


static func face(cid: String, card: Dictionary, arcana: String) -> ImageTexture:
	var kind := "arcana"
	if card.has("double_success") or card.has("passive_effect"):
		kind = "framework"
	var key := "%s|%s|%s" % [arcana, kind, cid]
	if _cache.has(key):
		return _cache[key]
	var tex := _build(cid, card, arcana, kind)
	_cache[key] = tex
	return tex


# ── internals ────────────────────────────────────────────────────

static func _bayer(x: int, y: int) -> float:
	return (float(_BAYER4[posmod(y, 4) * 4 + posmod(x, 4)]) + 0.5) / 16.0


static func _put(img: Image, x: int, y: int, c: Color) -> void:
	if x >= 0 and x < _SIZE and y >= 0 and y < _SIZE:
		img.set_pixel(x, y, c)


static func _rect(img: Image, x: int, y: int, w: int, h: int, c: Color) -> void:
	for yy in range(y, y + h):
		for xx in range(x, x + w):
			_put(img, xx, yy, c)


static func _disk(img: Image, cx: int, cy: int, r: int, c: Color) -> void:
	for yy in range(cy - r, cy + r + 1):
		for xx in range(cx - r, cx + r + 1):
			var dx: int = xx - cx
			var dy: int = yy - cy
			if dx * dx + dy * dy <= r * r:
				_put(img, xx, yy, c)


static func _ring(img: Image, cx: int, cy: int, r: int, c: Color) -> void:
	for yy in range(cy - r, cy + r + 1):
		for xx in range(cx - r, cx + r + 1):
			var dx: int = xx - cx
			var dy: int = yy - cy
			var d2: int = dx * dx + dy * dy
			if d2 >= r * r - r and d2 <= r * r + r:
				_put(img, xx, yy, c)


static func _diamond(img: Image, cx: int, cy: int, r: int, c: Color) -> void:
	for yy in range(cy - r, cy + r + 1):
		for xx in range(cx - r, cx + r + 1):
			if absi(xx - cx) + absi(yy - cy) <= r:
				_put(img, xx, yy, c)


static func _build(cid: String, card: Dictionary, arcana: String, kind: String) -> ImageTexture:
	var img := Image.create(_SIZE, _SIZE, false, Image.FORMAT_RGBA8)
	var accent: Color = _ARCANA_ACCENT.get(arcana, Color(0.85, 0.68, 0.28))
	var field_a: Color
	var field_b: Color
	var emblem: Color
	var line: Color
	if kind == "framework":
		# Shared framework cards: parchment stock, charcoal mark.
		field_a = Color(0.83, 0.78, 0.64)
		field_b = Color(0.70, 0.65, 0.52)
		emblem = Color(0.20, 0.18, 0.15)
		line = Color(0.38, 0.33, 0.24)
	else:
		# Arcana cards: the deck's black-and-gold, hue per arcana.
		field_a = Color(0.115, 0.10, 0.075)
		field_b = Color(0.06, 0.05, 0.045)
		emblem = accent
		line = Color(accent.r, accent.g, accent.b, 1.0).darkened(0.25)

	var h: int = absi(cid.hash())
	# Small deterministic shade variation so two cards of the same
	# arcana don't look like the same card.
	emblem = emblem.lightened(float((h >> 8) % 5) * 0.04)

	# Field: dithered vertical gradient.
	for y in range(_SIZE):
		var t: float = float(y) / float(_SIZE - 1)
		for x in range(_SIZE):
			img.set_pixel(x, y, field_b if t > _bayer(x, y) else field_a)
	# Double border: outer dark, inner accent line.
	for x in range(_SIZE):
		_put(img, x, 0, Color(0, 0, 0, 1))
		_put(img, x, _SIZE - 1, Color(0, 0, 0, 1))
	for y in range(_SIZE):
		_put(img, 0, y, Color(0, 0, 0, 1))
		_put(img, _SIZE - 1, y, Color(0, 0, 0, 1))
	for x in range(2, _SIZE - 2):
		_put(img, x, 2, line)
		_put(img, x, _SIZE - 3, line)
	for y in range(2, _SIZE - 2):
		_put(img, 2, y, line)
		_put(img, _SIZE - 3, y, line)

	# Emblem: eight variants by hash, centered in the upper field.
	var cx := 18
	var cy := 15
	match h % 8:
		0:
			_diamond(img, cx, cy, 7, emblem)
			_diamond(img, cx, cy, 3, field_b)
		1:
			_disk(img, cx, cy, 6, emblem)
			_ring(img, cx, cy, 9, emblem)
		2:
			for i in range(3):
				_rect(img, cx - 7 + i * 6, cy - 7, 3, 15, emblem)
		3:
			for i in range(7):
				_rect(img, cx - 1 - i, cy - 3 + i, 2, 2, emblem)
				_rect(img, cx + i, cy - 3 + i, 2, 2, emblem)
			_rect(img, cx - 1, cy - 7, 2, 2, emblem)
		4:
			_rect(img, cx - 8, cy - 2, 17, 4, emblem)
			_rect(img, cx - 2, cy - 8, 4, 17, emblem)
			_disk(img, cx, cy, 2, field_b)
		5:
			for row in range(3):
				var yy: int = cy - 5 + row * 5
				for x in range(cx - 8, cx + 9):
					var lift: int = 1 if posmod(x + row, 6) < 3 else 0
					_put(img, x, yy - lift, emblem)
					_put(img, x, yy - lift + 1, emblem)
		6:
			for row in range(9):
				_rect(img, cx - row, cy - 6 + row, row * 2 + 1, 1, emblem)
		7:
			for row in range(6):
				_rect(img, cx - 5 + row, cy - 7 + row, 11 - row * 2, 1, emblem)
				_rect(img, cx - 5 + row, cy + 7 - row, 11 - row * 2, 1, emblem)

	# Satellites by a second hash slice.
	match (h >> 4) % 3:
		0:
			for ang in range(4):
				var sx: int = cx + [0, 11, 0, -11][ang]
				var sy: int = cy + [-11, 0, 11, 0][ang]
				_disk(img, sx, sy, 1, emblem)
		1:
			_rect(img, cx - 6, cy + 11, 13, 1, emblem)
		2:
			_put(img, 4, 4, emblem)
			_put(img, _SIZE - 5, 4, emblem)

	# Pip row: time cost, bottom center.
	var cost: int = clampi(int(card.get("time_cost", 1)), 0, 5)
	if cost > 0:
		var total_w: int = cost * 3 + (cost - 1) * 2
		@warning_ignore("integer_division")
		var px: int = cx - total_w / 2
		for i in range(cost):
			_rect(img, px + i * 5, _SIZE - 7, 3, 3, emblem)

	img.resize(_SIZE * _SCALE, _SIZE * _SCALE, Image.INTERPOLATE_NEAREST)
	return ImageTexture.create_from_image(img)
