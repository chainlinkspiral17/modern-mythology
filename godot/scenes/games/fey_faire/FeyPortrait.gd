extends RefCounted
class_name FeyPortrait
## Procedural fey portrait generator · covers all 101 feys.
##
## Deterministic 32×40 pixel portrait built from the fey's own data:
##   · court    → palette (seelie cream-gold / unseelie plum-violet /
##                wildfey moss-amber)
##   · tier     → frame pips along the bottom edge (1..6)
##   · id hash  → face geometry (head width, eye spacing, eye size,
##                mouth style) + one court-flavored feature
##                (petal ears / horns / antlers)
##
## The same fey always gets the same face.  Different feys get
## visibly different faces.  This is the fallback tier of the
## two-tier sprite system — an authored HeroImage JSON at
## res://resources/games/vol7/fey_faire/portraits/<id>.json
## overrides the procedural face when present (PNG-override
## escape-hatch pattern from the sprite playbook).
##
## Usage:
##   var tex := FeyPortrait.texture(fey_dict, Vector2i(128, 160))

const W := 40
const H := 50

const PALETTES: Dictionary = {
	"seelie": {
		"bg":      Color("#2a2418"),
		"aura":    Color("#4a3e22"),
		"frame":   Color("#f8c848"),
		"skin":    Color("#f0d8b0"),
		"skin_sh": Color("#c8a878"),
		"eye":     Color("#3a5a2a"),
		"eye_hi":  Color("#f8f4e0"),
		"feature": Color("#e8a0b0"),
		"hair":    Color("#e8d090"),
		"hair_sh": Color("#b8a060"),
		"garment": Color("#8a7440")
	},
	"unseelie": {
		"bg":      Color("#1c1024"),
		"aura":    Color("#32204a"),
		"frame":   Color("#8a5aa8"),
		"skin":    Color("#d8c8e0"),
		"skin_sh": Color("#a890b8"),
		"eye":     Color("#601830"),
		"eye_hi":  Color("#f0d8e8"),
		"feature": Color("#503060"),
		"hair":    Color("#302040"),
		"hair_sh": Color("#201430"),
		"garment": Color("#3a2a50")
	},
	"wildfey": {
		"bg":      Color("#1c2014"),
		"aura":    Color("#32381e"),
		"frame":   Color("#c8983a"),
		"skin":    Color("#c8b088"),
		"skin_sh": Color("#907850"),
		"eye":     Color("#c87828"),
		"eye_hi":  Color("#f4e8c8"),
		"feature": Color("#587038"),
		"hair":    Color("#6a4a28"),
		"hair_sh": Color("#4a3218"),
		"garment": Color("#4a5230")
	}
}

const _BAYER4: Array = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5]


static func _bayer(x: int, y: int) -> float:
	return (float(_BAYER4[posmod(y, 4) * 4 + posmod(x, 4)]) + 0.5) / 16.0


static func _put(img: Image, x: int, y: int, c: Color) -> void:
	if x >= 1 and x < W - 1 and y >= 1 and y < H - 1:
		img.set_pixel(x, y, c)


static func _hspan(img: Image, x0: int, x1: int, y: int, c: Color) -> void:
	for x in range(x0, x1 + 1):
		_put(img, x, y, c)


static func texture(fey: Dictionary, size: Vector2i) -> ImageTexture:
	# Authored-portrait override · escape hatch
	var fid := String(fey.get("id", "unknown"))
	var override_path := "res://resources/games/vol7/fey_faire/portraits/" + fid + ".json"
	if FileAccess.file_exists(override_path):
		var hero := HeroImage.new()
		if hero.load_from(override_path):
			return hero.texture(size)
	return _procedural(fey, size)


static func _procedural(fey: Dictionary, size: Vector2i) -> ImageTexture:
	# 2026-07 quality pass: rounded head with jaw taper, shoulders
	# and garment (a portrait, not a floating block), dithered court
	# aura behind the figure, almond eyes with a highlight, and
	# real court features — leaf ears, curved horns, tined antlers.
	# Trait derivation keeps the ORIGINAL bit layout so every fey
	# keeps a stable identity across the upgrade.
	var fid := String(fey.get("id", "unknown"))
	var court := String(fey.get("court", "wildfey"))
	var tier := clampi(int(fey.get("tier", 1)), 1, 6)
	var pal: Dictionary = PALETTES.get(court, PALETTES["wildfey"])
	var seed: int = fid.hash()

	var img := Image.create(W, H, false, Image.FORMAT_RGBA8)
	img.fill(pal["bg"])

	# Court aura — dithered radial glow behind the figure.
	var aura: Color = pal["aura"]
	for y in range(1, H - 1):
		for x in range(1, W - 1):
			var dx: float = (float(x) - float(W) / 2.0) / (float(W) * 0.62)
			var dy: float = (float(y) - float(H) * 0.42) / (float(H) * 0.55)
			var g: float = clampf(1.0 - sqrt(dx * dx + dy * dy), 0.0, 1.0)
			if g * 0.85 > _bayer(x, y):
				img.set_pixel(x, y, aura)

	# Double frame: outer court line, inner dark inset.
	var frame: Color = pal["frame"]
	for x in range(W):
		img.set_pixel(x, 0, frame)
		img.set_pixel(x, H - 1, frame)
	for y in range(H):
		img.set_pixel(0, y, frame)
		img.set_pixel(W - 1, y, frame)
	var inset: Color = Color(frame.r * 0.4, frame.g * 0.4, frame.b * 0.4, 1.0)
	for x in range(2, W - 2):
		_put(img, x, 2, inset)
		_put(img, x, H - 3, inset)
	for y in range(2, H - 2):
		_put(img, 2, y, inset)
		_put(img, W - 3, y, inset)

	# Hash-derived geometry · SAME bit layout as v1 (stable faces).
	var head_w: int = 14 + (seed & 0x7)                 # 14..21
	var head_h: int = 17 + ((seed >> 3) & 0x7)          # 17..24
	var eye_dx: int = 3 + ((seed >> 6) & 0x3)           # eye spread
	var eye_size: int = 1 + ((seed >> 8) & 0x1)         # 1..2
	var mouth_style: int = (seed >> 9) & 0x3
	var feature_kind: int = (seed >> 11) & 0x3
	var hair_style: int = (seed >> 13) & 0x3

	@warning_ignore("integer_division")
	var cx: int = W / 2
	var head_top := 10
	@warning_ignore("integer_division")
	var head_left: int = cx - head_w / 2
	var head_right: int = head_left + head_w
	var head_bot: int = mini(head_top + head_h, H - 12)

	# Shoulders + garment first (head overlaps them at the neck).
	var garment: Color = pal["garment"]
	for y in range(head_bot + 2, H - 3):
		var widen: int = mini(14, 5 + (y - head_bot - 2) * 2)
		_hspan(img, cx - widen, cx + widen, y, garment)
	_hspan(img, cx - 6, cx + 6, head_bot + 2, pal["skin_sh"])   # collar skin
	# Neck.
	for y in range(head_bot - 1, head_bot + 3):
		_hspan(img, cx - 3, cx + 3, y, pal["skin_sh"])

	# Head — rounded: taper the top two and bottom three rows.
	for y in range(head_top, head_bot):
		var x0: int = head_left
		var x1: int = head_right
		if y == head_top:
			x0 += 3; x1 -= 3
		elif y == head_top + 1:
			x0 += 1; x1 -= 1
		# Jaw taper toward the chin.
		var from_bot: int = head_bot - 1 - y
		if from_bot == 0:
			x0 += 4; x1 -= 4
		elif from_bot == 1:
			x0 += 2; x1 -= 2
		elif from_bot == 2:
			x0 += 1; x1 -= 1
		for x in range(x0, x1):
			if x >= x1 - 3 and from_bot > 2:
				_put(img, x, y, pal["skin_sh"])
			else:
				_put(img, x, y, pal["skin"])

	# Hair — four styles, all with a shadow row where hair meets skin.
	var hair: Color = pal["hair"]
	var hair_sh: Color = pal["hair_sh"]
	match hair_style:
		0:  # crown band
			for y in range(head_top - 1, head_top + 4):
				var pad: int = 2 if y <= head_top else 0
				_hspan(img, head_left + pad, head_right - 1 - pad, y, hair)
			_hspan(img, head_left, head_right - 1, head_top + 4, hair_sh)
		1:  # long falls, both sides to the shoulders
			for y in range(head_top - 1, head_top + 4):
				_hspan(img, head_left, head_right - 1, y, hair)
			for y in range(head_top + 4, head_bot + 4):
				_hspan(img, head_left - 2, head_left, y, hair)
				_hspan(img, head_right - 1, head_right + 1, y, hair_sh)
			_hspan(img, head_left, head_right - 1, head_top + 4, hair_sh)
		2:  # wild halo — dense ragged edge
			for y in range(head_top - 3, head_top + 5):
				for x in range(head_left - 2, head_right + 2):
					var n: int = x * 374761393 + y * 668265263 + seed
					n = (n ^ (n >> 13)) * 1274126177
					if float((n ^ (n >> 16)) & 0xFFFF) / 65536.0 > 0.22:
						_put(img, x, y, hair if y < head_top + 3 else hair_sh)
		3:  # swept asymmetric
			for y in range(head_top - 1, head_top + 3):
				_hspan(img, head_left, head_right - 1, y, hair)
			_hspan(img, head_left, cx + 1, head_top + 3, hair)
			_hspan(img, head_left, cx - 3, head_top + 4, hair)
			_hspan(img, head_left, head_right - 1, head_top + 5, hair_sh)

	# Eyes — almond blocks with a highlight pixel. Large; fey.
	var eye_y: int = head_top + 7
	var eye: Color = pal["eye"]
	var eye_hi: Color = pal["eye_hi"]
	for side in [-1, 1]:
		var ex0: int = cx + side * eye_dx - 1
		for ey in range(eye_size + 1):
			_hspan(img, ex0, ex0 + eye_size + 1, eye_y + ey, eye)
		_put(img, ex0 + (0 if side < 0 else eye_size), eye_y, eye_hi)
	# Brow shadow above each eye.
	for side2 in [-1, 1]:
		var bx0: int = cx + side2 * eye_dx - 1
		_hspan(img, bx0, bx0 + eye_size + 1, eye_y - 2, pal["skin_sh"])

	# Nose hint.
	_put(img, cx, eye_y + 4, pal["skin_sh"])

	# Mouth.
	var mouth_y: int = head_bot - 5
	match mouth_style:
		0:
			_hspan(img, cx - 2, cx + 2, mouth_y, pal["skin_sh"])
		1:  # smile
			_put(img, cx - 3, mouth_y - 1, pal["skin_sh"])
			_hspan(img, cx - 2, cx + 2, mouth_y, pal["skin_sh"])
			_put(img, cx + 3, mouth_y - 1, pal["skin_sh"])
		2:  # small o
			_put(img, cx, mouth_y, eye)
			_put(img, cx, mouth_y - 1, pal["skin_sh"])
		3:  # downturn
			_put(img, cx - 3, mouth_y, pal["skin_sh"])
			_hspan(img, cx - 2, cx + 2, mouth_y - 1, pal["skin_sh"])
			_put(img, cx + 3, mouth_y, pal["skin_sh"])

	# Court features.
	var feat: Color = pal["feature"]
	match court:
		"seelie":
			# Leaf ears — three-pixel petals tapering out and up.
			var ear_y: int = head_top + 6 + feature_kind
			for side3 in [-1, 1]:
				var ex: int = (head_left - 1) if side3 < 0 else head_right
				_put(img, ex, ear_y, feat)
				_put(img, ex, ear_y + 1, feat)
				_put(img, ex + side3, ear_y - 1, feat)
				_put(img, ex + side3, ear_y, feat)
				_put(img, ex + side3 * 2, ear_y - 2, feat)
			# Blush.
			_put(img, cx - eye_dx - 2, eye_y + 3, feat)
			_put(img, cx + eye_dx + 2, eye_y + 3, feat)
			# Floating crown for the high tiers.
			if tier >= 4:
				for cxx in [cx - 3, cx, cx + 3]:
					_put(img, cxx, head_top - 4, frame)
				_put(img, cx, head_top - 5, frame)
		"unseelie":
			# Curved horns — 2px thick arcs sweeping out then up.
			var horn_len: int = 4 + feature_kind
			for side4 in [-1, 1]:
				var hx: int = (head_left + 2) if side4 < 0 else (head_right - 3)
				var hy: int = head_top
				for i in range(horn_len):
					var lean: int = side4 if i * 2 >= horn_len else 0
					hx += lean
					hy -= 1
					_put(img, hx, hy, feat)
					_put(img, hx + side4, hy, feat)
				_put(img, hx, hy - 1, eye_hi)   # lit tip
			# Dark halo arc for high tiers.
			if tier >= 4:
				_hspan(img, cx - 4, cx + 4, head_top - 7, feat)
		"wildfey":
			# Antlers — main beam with two tines each side.
			var ant_len: int = 5 + feature_kind
			for side5 in [-1, 1]:
				var ax: int = (head_left + 3) if side5 < 0 else (head_right - 4)
				for i in range(ant_len):
					var ay: int = head_top - 1 - i
					_put(img, ax, ay, feat)
					if i == 2:
						_put(img, ax + side5, ay, feat)
						_put(img, ax + side5 * 2, ay - 1, feat)
					if i == ant_len - 1:
						_put(img, ax + side5, ay - 1, feat)
			# Moss flecks on the shoulders.
			_put(img, cx - 8, H - 8, feat)
			_put(img, cx + 7, H - 10, feat)

	# Tier pips along the bottom frame.
	for t in range(tier):
		_put(img, 5 + t * 5, H - 3, frame)
		_put(img, 6 + t * 5, H - 3, frame)

	# Upscale nearest-neighbor.
	var out := img.duplicate()
	out.resize(size.x, size.y, Image.INTERPOLATE_NEAREST)
	return ImageTexture.create_from_image(out)
