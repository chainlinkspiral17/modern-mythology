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


static func _line(img: Image, x0: int, y0: int, x1: int, y1: int, w: int, c: Color) -> void:
	# thick Bresenham — a disk of radius w-1 stamped along the line
	var dx: int = absi(x1 - x0); var dy: int = -absi(y1 - y0)
	var sx: int = 1 if x0 < x1 else -1; var sy: int = 1 if y0 < y1 else -1
	var err: int = dx + dy; var x: int = x0; var y: int = y0
	var rad: int = maxi(0, w - 1)
	while true:
		_disk(img, x, y, rad, c)
		if x == x1 and y == y1: break
		var e2: int = 2 * err
		if e2 >= dy: err += dy; x += sx
		if e2 <= dx: err += dx; y += sy


static func _tri(img: Image, ax: int, ay: int, bx: int, by: int, cx: int, cy: int, c: Color) -> void:
	# filled triangle via barycentric sign test
	var minx: int = mini(ax, mini(bx, cx)); var maxx: int = maxi(ax, maxi(bx, cx))
	var miny: int = mini(ay, mini(by, cy)); var maxy: int = maxi(ay, maxi(by, cy))
	for yy in range(miny, maxy + 1):
		for xx in range(minx, maxx + 1):
			var d1: int = (xx - bx) * (ay - by) - (ax - bx) * (yy - by)
			var d2: int = (xx - cx) * (by - cy) - (bx - cx) * (yy - cy)
			var d3: int = (xx - ax) * (cy - ay) - (cx - ax) * (yy - ay)
			var neg: bool = (d1 < 0) or (d2 < 0) or (d3 < 0)
			var pos: bool = (d1 > 0) or (d2 > 0) or (d3 > 0)
			if not (neg and pos):
				_put(img, xx, yy, c)


# ── Representational pictographs (user: "cards should represent their
# actions — a foot and leg in stride for walk, an eye up close for
# focus"). Drawn in the upper field (~x 6..30, y 6..26), colour `col`
# for line/fill, `bg` for cutouts. Returns true if `cid` mapped to a
# real icon; false → caller falls back to the abstract hash emblem.
static func _pictograph(img: Image, cid: String, col: Color, bg: Color) -> bool:
	var key := _icon_key(cid)
	match key:
		"walk":
			# two legs mid-stride + feet
			_line(img, 18, 7, 14, 15, 2, col)   # back thigh
			_line(img, 14, 15, 11, 22, 2, col)  # back shin
			_rect(img, 8, 22, 6, 2, col)        # back foot
			_line(img, 18, 7, 22, 15, 2, col)   # front thigh
			_line(img, 22, 15, 24, 22, 2, col)  # front shin
			_rect(img, 23, 22, 6, 2, col)       # front foot
			_disk(img, 18, 7, 2, col)           # hip
		"focus":
			# an eye, up close: almond + iris + pupil + catchlight
			_line(img, 7, 15, 18, 9, 1, col); _line(img, 18, 9, 29, 15, 1, col)
			_line(img, 7, 15, 18, 21, 1, col); _line(img, 18, 21, 29, 15, 1, col)
			_disk(img, 18, 15, 5, col)
			_disk(img, 18, 15, 2, bg)
			_put(img, 20, 13, col)  # (leave a highlight speck of bg-ish)
			_disk(img, 20, 13, 0, bg)
		"search":
			_ring(img, 16, 13, 6, col); _ring(img, 16, 13, 5, col)
			_line(img, 20, 17, 27, 25, 2, col)
		"sprint":
			for i in range(3):
				var bx: int = 10 + i * 6
				_line(img, bx, 9, bx + 5, 15, 2, col)
				_line(img, bx + 5, 15, bx, 21, 2, col)
		"rest":
			# coffee mug (a break) + steam
			_rect(img, 12, 13, 11, 10, col); _rect(img, 14, 15, 7, 6, bg)
			_ring(img, 24, 17, 3, col)
			_line(img, 15, 8, 15, 11, 1, col); _line(img, 19, 7, 19, 11, 1, col)
		"sleep":
			# bed: headboard + mattress + pillow
			_rect(img, 7, 11, 2, 12, col)          # headboard
			_rect(img, 7, 19, 22, 4, col)          # mattress
			_rect(img, 9, 15, 6, 4, col)           # pillow
			_line(img, 22, 9, 27, 9, 1, col); _line(img, 27, 9, 22, 13, 1, col)
			_line(img, 22, 13, 27, 13, 1, col)     # a little "Z"
		"burst":
			# distraction: starburst
			for a in range(8):
				var ax2: int = 18 + int(round(cos(a * PI / 4.0) * 10))
				var ay2: int = 15 + int(round(sin(a * PI / 4.0) * 10))
				_line(img, 18, 15, ax2, ay2, 1, col)
			_disk(img, 18, 15, 2, col)
		"shield":
			_tri(img, 10, 9, 26, 9, 18, 12, col)   # top yoke
			_rect(img, 10, 9, 16, 8, col)
			_tri(img, 10, 17, 26, 17, 18, 26, col) # point
			_diamond(img, 18, 15, 3, bg)
		"alert":
			_ring(img, 18, 15, 9, col)
			_rect(img, 16, 9, 4, 8, col)
			_rect(img, 16, 19, 4, 3, col)
		"coin":
			_disk(img, 18, 15, 8, col); _disk(img, 18, 15, 6, bg)
			_rect(img, 17, 9, 2, 12, col)          # $ stem
			_rect(img, 14, 11, 6, 2, col); _rect(img, 16, 17, 6, 2, col)
		"idea":
			_disk(img, 18, 13, 6, col); _disk(img, 18, 13, 4, bg)
			_rect(img, 15, 18, 6, 3, col); _rect(img, 16, 21, 4, 2, col)
			_line(img, 18, 10, 18, 15, 1, col)     # filament
		"ear":
			_ring(img, 17, 14, 7, col); _ring(img, 17, 14, 6, col)
			_disk(img, 22, 18, 5, bg)              # open the right side
			_disk(img, 17, 14, 2, col)
		"broom":
			_line(img, 23, 7, 15, 18, 2, col)      # handle
			_tri(img, 15, 18, 9, 26, 19, 24, col)  # bristle fan
			for i in range(4):
				_line(img, 11 + i * 2, 22, 10 + i * 2, 26, 1, bg)
		"hand":
			_rect(img, 13, 13, 10, 10, col)        # palm
			for i in range(4):
				_rect(img, 13 + i * 3, 8, 2, 6, col)  # fingers
			_rect(img, 10, 14, 3, 5, col)          # thumb
		"plate":
			_disk(img, 18, 17, 9, col); _disk(img, 18, 17, 7, bg)
			_disk(img, 18, 16, 3, col)             # food lump
		"wait":
			# hourglass
			_rect(img, 11, 8, 14, 2, col); _rect(img, 11, 22, 14, 2, col)
			_tri(img, 11, 10, 25, 10, 18, 16, col)
			_tri(img, 11, 22, 25, 22, 18, 16, col)
		"read":
			# open book
			_tri(img, 18, 10, 8, 12, 8, 23, col); _tri(img, 18, 10, 18, 23, 8, 23, col)
			_tri(img, 18, 10, 28, 12, 28, 23, col); _tri(img, 18, 10, 18, 23, 28, 23, col)
			_line(img, 18, 10, 18, 23, 1, bg)
			for i in range(3):
				_line(img, 10, 15 + i * 2, 16, 15 + i * 2, 1, bg)
				_line(img, 20, 15 + i * 2, 26, 15 + i * 2, 1, bg)
		"phone":
			_line(img, 11, 11, 25, 25, 5, col)     # handset body
			_disk(img, 11, 11, 3, col); _disk(img, 25, 25, 3, col)
			_disk(img, 12, 12, 1, bg); _disk(img, 24, 24, 1, bg)
		"speak":
			_rect(img, 8, 9, 20, 12, col); _rect(img, 10, 11, 16, 8, bg)
			_tri(img, 12, 21, 12, 26, 18, 21, col) # tail
		_:
			return false
	return true


static func _icon_key(cid: String) -> String:
	# exact framework ids first, then keyword mapping for arc cards
	var exact := {
		"walk": "walk", "focus": "focus", "search": "search",
		"sprint": "sprint", "short_rest": "rest", "long_rest": "sleep",
		"distraction": "burst", "guard": "shield", "close_call": "alert",
		"spend_it": "coin", "improvise": "idea",
	}
	if exact.has(cid):
		return exact[cid]
	var s := cid.to_lower()
	for kw in [
		["listen", "ear"], ["hear", "ear"], ["walk", "walk"], ["step", "walk"],
		["run", "sprint"], ["look", "focus"], ["watch", "focus"], ["eye", "focus"],
		["read", "read"], ["book", "read"], ["ring", "phone"], ["phone", "phone"],
		["call", "phone"], ["clean", "broom"], ["wipe", "broom"], ["sweep", "broom"],
		["rag", "broom"], ["wait", "wait"], ["let_it", "wait"], ["greet", "hand"],
		["wave", "hand"], ["serve", "plate"], ["deliver", "plate"], ["plate", "plate"],
		["coffee", "rest"], ["rest", "rest"], ["sleep", "sleep"], ["say", "speak"],
		["talk", "speak"], ["speak", "speak"], ["shield", "shield"], ["guard", "shield"],
		["coin", "coin"], ["pay", "coin"], ["spend", "coin"], ["search", "search"],
		["find", "search"],
	]:
		if s.find(kw[0]) >= 0:
			return kw[1]
	return ""


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

	# Emblem: a representational pictograph when the card id maps to
	# a known action (walk/focus/search/...); otherwise the abstract
	# hash-derived shape. The pictograph reads as the ACTION, not a
	# generic glyph (user 2026-07-12).
	var cx := 18
	var cy := 15
	if _pictograph(img, cid, emblem, field_b):
		# pictograph drew the emblem; skip the abstract fallback,
		# still draw satellites + pips below.
		pass
	else:
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
