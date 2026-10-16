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
		"skins":   [Color("#f0d8b0"), Color("#e8c890"), Color("#f2ccc0")],
		"eye":     Color("#3a5a2a"),
		"eye_hi":  Color("#f8f4e0"),
		"feature": Color("#e8a0b0"),
		"hairs":   [Color("#e8d090"), Color("#c88848"), Color("#f0f0e0"), Color("#a86840")],
		"garment": Color("#8a7440")
	},
	"unseelie": {
		"bg":      Color("#1c1024"),
		"aura":    Color("#32204a"),
		"frame":   Color("#8a5aa8"),
		"skins":   [Color("#d8c8e0"), Color("#e8e4e0"), Color("#a8b0c8")],
		"eye":     Color("#601830"),
		"eye_hi":  Color("#f0d8e8"),
		"feature": Color("#503060"),
		"hairs":   [Color("#302040"), Color("#141020"), Color("#684a78"), Color("#8890a0")],
		"garment": Color("#3a2a50")
	},
	"wildfey": {
		"bg":      Color("#1c2014"),
		"aura":    Color("#32381e"),
		"frame":   Color("#c8983a"),
		"skins":   [Color("#c8b088"), Color("#a88860"), Color("#a8b080")],
		"eye":     Color("#c87828"),
		"eye_hi":  Color("#f4e8c8"),
		"feature": Color("#587038"),
		"hairs":   [Color("#6a4a28"), Color("#3a4a28"), Color("#8a6838"), Color("#484030")],
		"garment": Color("#4a5230")
	}
}

# ── Species ──────────────────────────────────────────────────────
# Body plan per fey, resolved from the catalog's true_form. The
# explicit map covers the canon strange ones; the keyword fallback
# classifies the rest; everything else is humanoid.
#
# Fully custom plans (nothing human about them):
#   wisp · formless · swarm · abomination · insect · triad
# Humanoid modifiers:
#   beast · treefolk · aquatic · winged · wraith · bullhead
const SPECIES_OVERRIDES: Dictionary = {
	"will_o_wisp":        "wisp",
	"brollachan":         "formless",
	"sluagh":             "swarm",
	"nuckelavee":         "abomination",
	"cricket_the_cricket": "insect",
	"salt_sisters":       "triad",
	"hecate":             "triad",
	"setebos":            "bullhead",
	"kelpie":             "beast",
	"pooka":              "beast",
	"cu_sith":            "beast",
	"black_dog":          "beast",
	"cluricaunes_cat":    "beast",
	"ossory_wolf":        "beast",
	"selkie":             "beast",
	"boggart":            "beast",
	"green_man":          "treefolk",
	"ghillie_dhu":        "treefolk",
	"huldra":             "treefolk",
	"skogsra":            "treefolk",
	"ondine":             "aquatic",
	"nixie":              "aquatic",
	"merrow":             "aquatic",
	"ceasg":              "aquatic",
	"nokken":             "aquatic",
	"fossegrim":          "aquatic",
	"bean_nighe":         "aquatic",
	"blue_man_minch":     "aquatic",
	"moth":               "winged",
	"queen_mab":          "winged",
	"cobweb":             "winged",
	"ariel":              "wraith",
	"hamlets_ghost":      "wraith",
	"ophelia_ghost":      "wraith",
	"sycorax":            "wraith",
	"banshee":            "wraith",
	"fear_gorta":         "wraith",
	"draugr":             "wraith",
}


static func _resolve_species(fey: Dictionary) -> String:
	var fid := String(fey.get("id", ""))
	if SPECIES_OVERRIDES.has(fid):
		return SPECIES_OVERRIDES[fid]
	var tf := String(fey.get("true_form", "")).to_lower()
	if tf.contains("wing"):
		return "winged"
	if tf.contains("dog") or tf.contains("wolf") or tf.contains("hound") \
			or tf.contains(" cat") or tf.contains("horse") or tf.contains("seal"):
		return "beast"
	if tf.contains("moss") or tf.contains("leaves") or tf.contains("tree-") \
			or tf.contains("pine-trunk") or tf.contains("bramble"):
		return "treefolk"
	if tf.contains("mermaid") or tf.contains("fish-tail") or tf.contains("water-fey") \
			or tf.contains("seawater"):
		return "aquatic"
	if tf.contains("ghost") or tf.contains("shade") or tf.contains("revenant") \
			or tf.contains("translucent"):
		return "wraith"
	return "humanoid"


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

	# Court aura — dithered glow behind the figure, shaped per court:
	# seelie round as a sun, unseelie a tall narrow shard, wildfey
	# broad and low like canopy light.
	var aura: Color = pal["aura"]
	var aura_w: float = float(W) * (0.50 if court == "unseelie" else 0.62)
	var aura_h: float = float(H) * (0.62 if court == "wildfey" else 0.55)
	if court == "unseelie":
		aura_h = float(H) * 0.70
	for y in range(1, H - 1):
		for x in range(1, W - 1):
			var dx: float = (float(x) - float(W) / 2.0) / aura_w
			var dy: float = (float(y) - float(H) * 0.42) / aura_h
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

	# Non-humanoid body plans branch here — they share the aura,
	# frame, and tier pips, but nothing of the face pipeline.
	var species := _resolve_species(fey)
	if species == "wisp" or species == "formless" or species == "swarm" \
			or species == "abomination" or species == "insect" or species == "triad":
		_paint_custom_species(img, species, pal, seed)
		for t0 in range(tier):
			_put(img, 5 + t0 * 5, H - 3, frame)
			_put(img, 6 + t0 * 5, H - 3, frame)
		var out0 := img.duplicate()
		out0.resize(size.x, size.y, Image.INTERPOLATE_NEAREST)
		return ImageTexture.create_from_image(out0)

	# Hash-derived geometry · SAME bit layout as v1 (stable faces).
	var head_w: int = 14 + (seed & 0x7)                 # 14..21
	var head_h: int = 17 + ((seed >> 3) & 0x7)          # 17..24
	var eye_dx: int = 3 + ((seed >> 6) & 0x3)           # eye spread
	var eye_size: int = 1 + ((seed >> 8) & 0x1)         # 1..2
	var mouth_style: int = (seed >> 9) & 0x3
	var feature_kind: int = (seed >> 11) & 0x3
	var hair_style: int = (seed >> 13) & 0x3
	# v3 traits — read from previously UNUSED seed bits, so every
	# v2 identity (head, eyes, mouth, hair style) is untouched.
	var skins: Array = pal["skins"]
	var skin: Color = skins[((seed >> 15) & 0x3) % skins.size()]
	var skin_sh: Color = skin.darkened(0.22)
	var hairs: Array = pal["hairs"]
	var hair: Color = hairs[((seed >> 17) & 0x3) % hairs.size()]
	var hair_sh: Color = hair.darkened(0.28)
	var eye_style: int = (seed >> 19) & 0x1
	var marking: int = (seed >> 20) & 0x3
	var adornment: int = (seed >> 22) & 0x3

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
	_hspan(img, cx - 6, cx + 6, head_bot + 2, skin_sh)   # collar skin
	# Neck.
	for y in range(head_bot - 1, head_bot + 3):
		_hspan(img, cx - 3, cx + 3, y, skin_sh)

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
				_put(img, x, y, skin_sh)
			else:
				_put(img, x, y, skin)

	# Hair — four styles, all with a shadow row where hair meets skin.
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

	# Pointed fey ears on everyone — court features layer over them.
	var ear_base: int = head_top + 8
	for side_e in [-1, 1]:
		var ear_x: int = (head_left - 1) if side_e < 0 else head_right
		_put(img, ear_x, ear_base, skin)
		_put(img, ear_x, ear_base + 1, skin_sh)
		_put(img, ear_x + side_e, ear_base - 1, skin)

	# Eyes — almond or rounded (eye_style), with a highlight pixel.
	# Unseelie get vertical slit pupils instead of the corner light.
	var eye_y: int = head_top + 7
	var eye: Color = pal["eye"]
	var eye_hi: Color = pal["eye_hi"]
	for side in [-1, 1]:
		var ex0: int = cx + side * eye_dx - 1
		for ey in range(eye_size + 1):
			_hspan(img, ex0, ex0 + eye_size + 1, eye_y + ey, eye)
		if eye_style == 1:
			_hspan(img, ex0 + 1, ex0 + eye_size, eye_y - 1, eye)
		if court == "unseelie":
			for ey2 in range(eye_size + 1):
				_put(img, ex0 + 1, eye_y + ey2, eye_hi)
		else:
			_put(img, ex0 + (0 if side < 0 else eye_size), eye_y, eye_hi)
	# Brow shadow above each eye.
	for side2 in [-1, 1]:
		var bx0: int = cx + side2 * eye_dx - 1
		_hspan(img, bx0, bx0 + eye_size + 1, eye_y - 2, skin_sh)

	# Nose hint.
	_put(img, cx, eye_y + 4, skin_sh)

	# Face marking — a quarter of feys carry one.
	match marking:
		1:  # freckles across the cheeks
			_put(img, cx - eye_dx - 1, eye_y + 4, skin_sh)
			_put(img, cx + eye_dx, eye_y + 5, skin_sh)
			_put(img, cx + eye_dx + 2, eye_y + 4, skin_sh)
		2:  # tear-mark under the left eye
			_put(img, cx - eye_dx, eye_y + 3, pal["feature"])
			_put(img, cx - eye_dx, eye_y + 4, pal["feature"])
		3:  # third-eye brow dot
			_put(img, cx, eye_y - 4, pal["feature"])

	# Mouth.
	var mouth_y: int = head_bot - 5
	match mouth_style:
		0:
			_hspan(img, cx - 2, cx + 2, mouth_y, skin_sh)
		1:  # smile
			_put(img, cx - 3, mouth_y - 1, skin_sh)
			_hspan(img, cx - 2, cx + 2, mouth_y, skin_sh)
			_put(img, cx + 3, mouth_y - 1, skin_sh)
		2:  # small o
			_put(img, cx, mouth_y, eye)
			_put(img, cx, mouth_y - 1, skin_sh)
		3:  # downturn
			_put(img, cx - 3, mouth_y, skin_sh)
			_hspan(img, cx - 2, cx + 2, mouth_y - 1, skin_sh)
			_put(img, cx + 3, mouth_y, skin_sh)

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

	# Adornment — drawn last so it sits over hair and features.
	match adornment:
		1:  # earrings at the ear points
			_put(img, head_left - 1, ear_base + 2, frame)
			_put(img, head_right, ear_base + 2, frame)
		2:  # circlet across the brow
			_hspan(img, head_left + 2, head_right - 3, head_top + 5, frame)
		3:  # collar gem
			_put(img, cx, head_bot + 4, frame)
			_put(img, cx, head_bot + 5, inset)

	# Garment shading + collar trim — cheap cloth read.
	var garment_sh: Color = garment.darkened(0.25)
	for y3 in range(head_bot + 3, H - 3):
		var widen2: int = mini(14, 5 + (y3 - head_bot - 2) * 2)
		for x3 in range(cx + widen2 - 4, cx + widen2 + 1):
			if img.get_pixel(clampi(x3, 1, W - 2), y3) == garment:
				_put(img, x3, y3, garment_sh)
	_hspan(img, cx - 7, cx + 7, head_bot + 3, garment_sh)

	# Humanoid-variant species — paints the body-plan differences
	# over the base (wings test for bg/aura so they sit BEHIND).
	if species != "humanoid":
		_apply_species_modifier(img, species, pal, {
			"seed": seed, "head_left": head_left, "head_right": head_right,
			"head_top": head_top, "head_bot": head_bot, "cx": cx,
			"eye_y": eye_y, "eye_dx": eye_dx, "eye_size": eye_size,
			"skin": skin, "skin_sh": skin_sh, "hair": hair, "hair_sh": hair_sh,
			"garment": garment,
		})

	# Tier pips along the bottom frame.
	for t in range(tier):
		_put(img, 5 + t * 5, H - 3, frame)
		_put(img, 6 + t * 5, H - 3, frame)

	# Upscale nearest-neighbor.
	var out := img.duplicate()
	out.resize(size.x, size.y, Image.INTERPOLATE_NEAREST)
	return ImageTexture.create_from_image(out)


# ── Fully non-humanoid painters ──────────────────────────────────

static func _paint_custom_species(img: Image, species: String, pal: Dictionary, seed: int) -> void:
	var feat: Color = pal["feature"]
	var frame: Color = pal["frame"]
	var eye_hi: Color = pal["eye_hi"]
	var bg: Color = pal["bg"]
	match species:
		"wisp":
			# A small floating flame the color of stagnant water.
			var fx := 20
			var fy := 24
			for y in range(fy - 9, fy + 8):
				var r: int = 7 - absi(y - fy) if y >= fy - 2 else maxi(1, 5 - (fy - 2 - y) * 2)
				for x in range(fx - r, fx + r + 1):
					_put(img, x, y, feat)
			for y2 in range(fy - 4, fy + 6):
				var r2: int = 4 - absi(y2 - (fy + 1))
				if r2 > 0:
					_hspan(img, fx - r2, fx + r2, y2, eye_hi)
			_hspan(img, fx - 1, fx + 1, fy + 2, frame)          # hot core
			_put(img, fx - 2, fy, bg)                            # two dark eyes
			_put(img, fx + 2, fy, bg)
			for s in [[10, 14], [30, 18], [13, 34], [28, 33], [20, 8]]:
				_put(img, s[0], s[1], feat)                      # drifting sparks
			# Cold reflection beneath — it casts light, not warmth.
			for x3 in range(fx - 6, fx + 7):
				if _bayer(x3, 40) < 0.4:
					_put(img, x3, 40, feat)
		"formless":
			# The brollachan — a mass that has never had a shape.
			for y in range(16, H - 4):
				for x in range(4, W - 4):
					var n: int = x * 374761393 + y * 668265263 + seed
					n = (n ^ (n >> 13)) * 1274126177
					var v: float = float((n ^ (n >> 16)) & 0xFFFF) / 65536.0
					var edge: float = 1.0 - absf(float(x) - float(W) / 2.0) / (float(W) * 0.42)
					var depth: float = clampf((float(y) - 14.0) / 16.0, 0.0, 1.0)
					if v < edge * depth * 0.96:
						_put(img, x, y, Color(0.05, 0.03, 0.08, 1.0))
			# Two lights, uneven — MYSELF and THYSELF.
			_hspan(img, 14, 15, 26, eye_hi)
			_hspan(img, 24, 25, 29, eye_hi)
			# Drips.
			for d in [[9, 45], [21, 46], [33, 44]]:
				_put(img, d[0], d[1], Color(0.05, 0.03, 0.08, 1.0))
		"swarm":
			# Not a single fey — a HOST, flying with the west wind.
			# A dim moon behind them turns the flock into silhouettes.
			var moon := Color(0.55, 0.52, 0.62, 1.0)
			for my0 in range(10, 32):
				for mx0 in range(9, 32):
					var mdx: float = float(mx0) - 20.0
					var mdy: float = float(my0) - 20.0
					if mdx * mdx + mdy * mdy < 90.0 and _bayer(mx0, my0) < 0.8:
						_put(img, mx0, my0, moon)
			var wing := Color(0.62, 0.60, 0.70, 1.0)
			var idx := 0
			for row in range(3):
				for col in range(3 + (row % 2)):
					var sx: int = 7 + col * 9 + (4 if row % 2 == 1 else 0)
					var sy: int = 12 + row * 10 + ((seed >> (idx % 8)) & 0x3)
					_hspan(img, sx - 1, sx + 1, sy, Color(0.08, 0.06, 0.10, 1.0))
					_hspan(img, sx - 1, sx + 1, sy + 1, Color(0.08, 0.06, 0.10, 1.0))
					_put(img, sx, sy - 1, Color(0.08, 0.06, 0.10, 1.0))
					_put(img, sx - 2, sy, wing)                  # wing dashes
					_put(img, sx + 2, sy, wing)
					_put(img, sx, sy, eye_hi)                    # one eye each
					idx += 1
			# The wind itself.
			for wx in range(6, 34, 4):
				_put(img, wx, 42, feat)
		"abomination":
			# The nuckelavee — horse and rider fused, both skinned.
			var red := Color("#7a2018")
			var red_dk := Color("#4a100c")
			# Horse mass.
			for y in range(28, 42):
				var r3: int = 13 - maxi(0, absi(y - 34) - 2)
				_hspan(img, 20 - r3, 20 + r3, y, red)
			# Legs.
			for lx in [10, 16, 24, 30]:
				for ly in range(42, 47):
					_put(img, lx, ly, red_dk)
			# Rider fused at the withers — no seam where a seam should be.
			for y4 in range(12, 30):
				var r4: int = 5 - maxi(0, absi(y4 - 20) - 5)
				if r4 > 0:
					_hspan(img, 26 - r4, 26 + r4, y4, red)
			# Exposed sinew.
			for my in range(30, 41, 3):
				_hspan(img, 12, 28, my, red_dk)
			for my2 in range(14, 27, 3):
				_hspan(img, 23, 29, my2, red_dk)
			# Too many eyes, all white.
			for e in [[26, 15], [28, 17], [12, 31], [17, 30], [25, 32]]:
				_put(img, e[0], e[1], eye_hi)
		"insect":
			# An actual cricket-sized fey · three eyes · very fast.
			var shell := Color("#3a6a30")
			var shell_lt := Color("#58925a")
			# Wing sheen behind.
			for y5 in range(18, 34):
				_put(img, 8, y5, feat)
				_put(img, 32, y5, feat)
			# Head — broad oval.
			for y6 in range(14, 28):
				var r5: int = 9 - maxi(0, absi(y6 - 21) - 4)
				_hspan(img, 20 - r5, 20 + r5, y6, shell)
			_hspan(img, 14, 26, 15, shell_lt)
			# Three eyes.
			for e2 in [[15, 19], [20, 17], [25, 19]]:
				_put(img, e2[0], e2[1], pal["eye"])
				_put(img, e2[0], e2[1] - 1, eye_hi)
			# Mandibles + antennae.
			_put(img, 18, 27, shell_lt)
			_put(img, 22, 27, shell_lt)
			for a in range(6):
				_put(img, 15 - a, 13 - a, shell_lt)
				_put(img, 25 + a, 13 - a, shell_lt)
			# Six legs.
			for i2 in range(3):
				var lx2: int = 14 + i2 * 6
				for ly2 in range(28, 34 + i2):
					_put(img, lx2, ly2, shell)
					_put(img, 40 - lx2, ly2, shell)
		"triad":
			# Three-in-one — maiden, mother, crone, mid-shift.
			var skin3: Color = (pal["skins"] as Array)[0]
			var skin3_sh: Color = skin3.darkened(0.25)
			# Shared shoulders.
			for y7 in range(36, H - 3):
				var widen3: int = mini(16, 8 + (y7 - 36) * 2)
				_hspan(img, 20 - widen3, 20 + widen3, y7, pal["garment"])
			# Side heads, dimmer, slightly lower.
			for side6 in [-1, 1]:
				var hx2: int = 20 + side6 * 10
				for y8 in range(18, 32):
					var r6: int = 4 - maxi(0, absi(y8 - 24) - 4)
					if r6 > 0:
						_hspan(img, hx2 - r6, hx2 + r6, y8, skin3_sh)
				_put(img, hx2 - 1, 23, pal["eye"])
				_put(img, hx2 + 1, 23, pal["eye"])
				_hspan(img, hx2 - 3, hx2 + 3, 18, pal["hairs"][1])
			# Center head, full.
			for y9 in range(14, 30):
				var r7: int = 5 - maxi(0, absi(y9 - 21) - 5)
				if r7 > 0:
					_hspan(img, 20 - r7, 20 + r7, y9, skin3)
			_put(img, 18, 20, pal["eye"])
			_put(img, 22, 20, pal["eye"])
			_put(img, 18, 19, eye_hi)
			_hspan(img, 18, 22, 26, skin3_sh)
			_hspan(img, 16, 24, 14, pal["hairs"][0])
			_hspan(img, 15, 25, 15, pal["hairs"][0])


# ── Humanoid-variant modifiers ───────────────────────────────────

static func _apply_species_modifier(img: Image, species: String, pal: Dictionary, ctx: Dictionary) -> void:
	var head_left: int = ctx["head_left"]
	var head_right: int = ctx["head_right"]
	var head_top: int = ctx["head_top"]
	var head_bot: int = ctx["head_bot"]
	var cx: int = ctx["cx"]
	var eye_y: int = ctx["eye_y"]
	var eye_dx: int = ctx["eye_dx"]
	var skin: Color = ctx["skin"]
	var skin_sh: Color = ctx["skin_sh"]
	var hair: Color = ctx["hair"]
	var hair_sh: Color = ctx["hair_sh"]
	var garment: Color = ctx["garment"]
	var seed: int = ctx["seed"]
	var feat: Color = pal["feature"]
	var eye: Color = pal["eye"]
	var eye_hi: Color = pal["eye_hi"]
	var bg: Color = pal["bg"]
	var aura: Color = pal["aura"]
	match species:
		"beast":
			# Fur the whole head, then muzzle, nose, round eyes,
			# triangle ears. The humanoid face vanishes under it.
			for y in range(head_top - 2, head_bot):
				for x in range(head_left, head_right):
					_put(img, x, y, hair if x < head_right - 3 else hair_sh)
			# Muzzle.
			for y2 in range(eye_y + 3, head_bot - 1):
				_hspan(img, cx - 3, cx + 3, y2, skin)
			_hspan(img, cx - 1, cx + 1, eye_y + 4, hair_sh)      # nose
			_put(img, cx, head_bot - 3, hair_sh)                  # mouth line
			# Round eyes.
			for side in [-1, 1]:
				var ex: int = cx + side * eye_dx
				_put(img, ex, eye_y, eye)
				_put(img, ex + 1, eye_y, eye)
				_put(img, ex, eye_y + 1, eye)
				_put(img, ex + 1, eye_y + 1, eye)
				_put(img, ex, eye_y, eye_hi)
			# Ears.
			for side2 in [-1, 1]:
				var ax: int = cx + side2 * 6
				_put(img, ax, head_top - 3, hair)
				_hspan(img, ax - 1, ax + 1, head_top - 2, hair)
				_hspan(img, ax - 2, ax + 2, head_top - 1, hair)
		"treefolk":
			# Bark face with grain, leaf crown, glowing knot eyes.
			var bark := Color(garment.r * 0.8, garment.g * 0.7, garment.b * 0.5, 1.0)
			var bark_dk := bark.darkened(0.35)
			for y3 in range(head_top - 1, head_bot):
				for x2 in range(head_left, head_right):
					_put(img, x2, y3, bark)
			for gx in range(head_left + 2, head_right - 1, 3):
				for gy in range(head_top, head_bot - 1):
					if posmod(gy + gx, 7) < 3:
						_put(img, gx, gy, bark_dk)
			# Leaf crown + shoulder growth.
			for lx in range(head_left - 1, head_right + 1, 2):
				_put(img, lx, head_top - 2, feat)
				_put(img, lx + 1, head_top - 3, feat)
			_put(img, cx - 8, head_bot + 4, feat)
			_put(img, cx + 7, head_bot + 5, feat)
			_put(img, cx + 8, head_bot + 4, feat)
			# Knot eyes, lit.
			for side3 in [-1, 1]:
				var ex2: int = cx + side3 * eye_dx
				_put(img, ex2, eye_y, eye_hi)
				_put(img, ex2 + 1, eye_y, eye_hi)
				_put(img, ex2, eye_y + 1, bark_dk)
			# Mouth seam.
			_hspan(img, cx - 2, cx + 2, head_bot - 4, bark_dk)
		"aquatic":
			# Teal-tinted skin, fan fin ears, gill slits, scale
			# flecks, wet-slick hair line.
			var tint := Color(0.35, 0.62, 0.60, 1.0)
			for ty in range(head_top, head_bot + 3):
				for tx in range(head_left - 1, head_right + 1):
					var c0: Color = img.get_pixel(clampi(tx, 1, W - 2), clampi(ty, 1, H - 2))
					if c0 == skin or c0 == skin_sh:
						_put(img, tx, ty, c0.lerp(tint, 0.30))
			for side4 in [-1, 1]:
				var fx2: int = (head_left - 1) if side4 < 0 else head_right
				for i in range(4):
					for j in range(i + 1):
						_put(img, fx2 + side4 * j, eye_y - 2 + i, feat)
			for side5 in [-1, 1]:
				for g2 in range(3):
					_put(img, cx + side5 * 2, head_bot + g2, skin_sh.darkened(0.2))
			for sc in [[cx - eye_dx - 1, eye_y + 3], [cx + eye_dx + 1, eye_y + 4],
					[cx - eye_dx, eye_y + 5]]:
				_put(img, sc[0], sc[1], feat)
			_hspan(img, head_left + 1, head_right - 2, head_top + 4, hair_sh)
		"winged":
			# Moth wings BEHIND the figure — only paint over bg/aura.
			# Lifted toward the highlight so they read on dark courts.
			var wing_c: Color = feat.lerp(eye_hi, 0.30)
			for side6 in [-1, 1]:
				for wy in range(14, 34):
					@warning_ignore("integer_division")
					var reach: int = 9 - absi(wy - 22) / 2
					for wxi in range(reach):
						var wx: int = (head_left - 3 - wxi) if side6 < 0 else (head_right + 2 + wxi)
						var cur: Color = img.get_pixel(clampi(wx, 1, W - 2), wy)
						if cur == bg or cur == aura:
							_put(img, wx, wy, wing_c)
				# Eye-spot on each wing.
				var sx2: int = (head_left - 6) if side6 < 0 else (head_right + 5)
				_put(img, sx2, 21, eye_hi)
				_put(img, sx2, 22, hair_sh)
			# Antennae.
			for side7 in [-1, 1]:
				for a2 in range(4):
					_put(img, cx + side7 * (2 + a2), head_top - 2 - a2, hair_sh)
		"wraith":
			# Translucent: everything of the figure drifts toward the
			# bg; ragged hem; the eyes burn through.
			for y4 in range(1, H - 1):
				for x3 in range(1, W - 1):
					var c: Color = img.get_pixel(x3, y4)
					if c == skin or c == skin_sh or c == hair or c == hair_sh or c == garment:
						img.set_pixel(x3, y4, c.lerp(bg, 0.45))
			for x4 in range(8, W - 8):
				var n2: int = x4 * 374761393 + seed
				n2 = (n2 ^ (n2 >> 13)) * 1274126177
				var frays: int = 2 + ((n2 ^ (n2 >> 16)) & 0x3)
				for f2 in range(frays):
					_put(img, x4, H - 4 - f2, bg)
			for side8 in [-1, 1]:
				var ex3: int = cx + side8 * eye_dx
				_put(img, ex3, eye_y, eye_hi)
				_put(img, ex3 + 1, eye_y, eye_hi)
				_put(img, ex3, eye_y + 1, eye_hi)
		"bullhead":
			# Setebos — the bull god. Wide muzzle, out-curving horns.
			var bone := Color("#d8d0be")
			for y5 in range(eye_y + 2, head_bot):
				_hspan(img, cx - 5, cx + 5, y5, hair)
			_put(img, cx - 2, eye_y + 5, hair_sh)
			_put(img, cx + 2, eye_y + 5, hair_sh)
			for side9 in [-1, 1]:
				var hx3: int = (head_left) if side9 < 0 else (head_right - 1)
				var hy2: int = head_top + 2
				for i3 in range(5):
					_put(img, hx3 + side9 * i3, hy2 - (i3 if i3 < 3 else 2 + i3 % 2), bone)
					_put(img, hx3 + side9 * i3, hy2 - (i3 if i3 < 3 else 2 + i3 % 2) + 1, bone)
