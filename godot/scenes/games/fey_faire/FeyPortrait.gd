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

const W := 32
const H := 40

const PALETTES: Dictionary = {
	"seelie": {
		"bg":      Color("#2a2418"),
		"frame":   Color("#f8c848"),
		"skin":    Color("#f0d8b0"),
		"skin_sh": Color("#c8a878"),
		"eye":     Color("#3a5a2a"),
		"feature": Color("#e8a0b0"),
		"hair":    Color("#e8d090")
	},
	"unseelie": {
		"bg":      Color("#1c1024"),
		"frame":   Color("#8a5aa8"),
		"skin":    Color("#d8c8e0"),
		"skin_sh": Color("#a890b8"),
		"eye":     Color("#601830"),
		"feature": Color("#503060"),
		"hair":    Color("#302040")
	},
	"wildfey": {
		"bg":      Color("#1c2014"),
		"frame":   Color("#c8983a"),
		"skin":    Color("#c8b088"),
		"skin_sh": Color("#907850"),
		"eye":     Color("#c87828"),
		"feature": Color("#587038"),
		"hair":    Color("#6a4a28")
	}
}


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
	var fid := String(fey.get("id", "unknown"))
	var court := String(fey.get("court", "wildfey"))
	var tier := clampi(int(fey.get("tier", 1)), 1, 6)
	var pal: Dictionary = PALETTES.get(court, PALETTES["wildfey"])
	var seed: int = fid.hash()

	var img := Image.create(W, H, false, Image.FORMAT_RGBA8)
	img.fill(pal["bg"])

	# Frame
	for x in range(W):
		img.set_pixel(x, 0, pal["frame"])
		img.set_pixel(x, H - 1, pal["frame"])
	for y in range(H):
		img.set_pixel(0, y, pal["frame"])
		img.set_pixel(W - 1, y, pal["frame"])

	# Hash-derived geometry · each byte of the seed feeds one trait
	var head_w: int = 12 + (seed & 0x7)                 # 12..19
	var head_h: int = 14 + ((seed >> 3) & 0x7)          # 14..21
	var eye_dx: int = 2 + ((seed >> 6) & 0x3)           # eye spread from center
	var eye_size: int = 1 + ((seed >> 8) & 0x1)         # 1..2
	var mouth_style: int = (seed >> 9) & 0x3            # 0..3
	var feature_kind: int = (seed >> 11) & 0x3          # variation within court
	var hair_style: int = (seed >> 13) & 0x3

	var cx := W / 2
	var head_top := 8
	var head_left: int = cx - head_w / 2
	var head_right: int = head_left + head_w

	# Head block with shading on the right third
	for y in range(head_top, min(head_top + head_h, H - 4)):
		for x in range(head_left, head_right):
			if x >= head_right - head_w / 4:
				img.set_pixel(x, y, pal["skin_sh"])
			else:
				img.set_pixel(x, y, pal["skin"])

	# Hair · top band over the head, style-varied depth
	var hair_depth: int = 2 + hair_style
	for y in range(head_top, min(head_top + hair_depth, H - 4)):
		for x in range(head_left, head_right):
			img.set_pixel(x, y, pal["hair"])

	# Eyes · enormous by fey standards
	var eye_y := head_top + head_h / 3 + 1
	for ey in range(eye_size + 1):
		for ex in range(eye_size + 1):
			img.set_pixel(clampi(cx - eye_dx - ex, 1, W - 2), clampi(eye_y + ey, 1, H - 2), pal["eye"])
			img.set_pixel(clampi(cx + eye_dx + ex, 1, W - 2), clampi(eye_y + ey, 1, H - 2), pal["eye"])

	# Mouth
	var mouth_y: int = head_top + (head_h * 3) / 4
	match mouth_style:
		0:  # flat line
			for x in range(cx - 2, cx + 3):
				img.set_pixel(clampi(x, 1, W - 2), clampi(mouth_y, 1, H - 2), pal["skin_sh"])
		1:  # small smile
			img.set_pixel(clampi(cx - 2, 1, W - 2), clampi(mouth_y - 1, 1, H - 2), pal["skin_sh"])
			for x in range(cx - 1, cx + 2):
				img.set_pixel(clampi(x, 1, W - 2), clampi(mouth_y, 1, H - 2), pal["skin_sh"])
			img.set_pixel(clampi(cx + 2, 1, W - 2), clampi(mouth_y - 1, 1, H - 2), pal["skin_sh"])
		2:  # small o
			img.set_pixel(clampi(cx, 1, W - 2), clampi(mouth_y, 1, H - 2), pal["eye"])
		3:  # downturn · unseelie-flavored
			img.set_pixel(clampi(cx - 2, 1, W - 2), clampi(mouth_y, 1, H - 2), pal["skin_sh"])
			for x in range(cx - 1, cx + 2):
				img.set_pixel(clampi(x, 1, W - 2), clampi(mouth_y - 1, 1, H - 2), pal["skin_sh"])
			img.set_pixel(clampi(cx + 2, 1, W - 2), clampi(mouth_y, 1, H - 2), pal["skin_sh"])

	# Court feature above/beside the head
	match court:
		"seelie":
			# Petal ears · one pixel-cluster each side, feature_kind sets height
			var ear_y: int = head_top + 3 + feature_kind
			for e in range(2):
				img.set_pixel(clampi(head_left - 1, 1, W - 2), clampi(ear_y + e, 1, H - 2), pal["feature"])
				img.set_pixel(clampi(head_right, 1, W - 2), clampi(ear_y + e, 1, H - 2), pal["feature"])
			# Tiny hovering glow-dot crown for high tiers
			if tier >= 4:
				img.set_pixel(clampi(cx, 1, W - 2), clampi(head_top - 3, 1, H - 2), pal["frame"])
		"unseelie":
			# Horns · angled pixel runs, feature_kind sets length
			var horn_len: int = 2 + feature_kind
			for hnl in range(horn_len):
				img.set_pixel(clampi(head_left + 1 + hnl / 2, 1, W - 2), clampi(head_top - 1 - hnl, 1, H - 2), pal["feature"])
				img.set_pixel(clampi(head_right - 2 - hnl / 2, 1, W - 2), clampi(head_top - 1 - hnl, 1, H - 2), pal["feature"])
		"wildfey":
			# Antlers · branching pixel runs
			var ant_len: int = 3 + feature_kind
			for anl in range(ant_len):
				img.set_pixel(clampi(head_left + 2, 1, W - 2), clampi(head_top - 1 - anl, 1, H - 2), pal["feature"])
				img.set_pixel(clampi(head_right - 3, 1, W - 2), clampi(head_top - 1 - anl, 1, H - 2), pal["feature"])
				if anl == ant_len - 2:
					img.set_pixel(clampi(head_left + 1, 1, W - 2), clampi(head_top - 1 - anl, 1, H - 2), pal["feature"])
					img.set_pixel(clampi(head_right - 2, 1, W - 2), clampi(head_top - 1 - anl, 1, H - 2), pal["feature"])

	# Tier pips along the bottom frame
	for t in range(tier):
		img.set_pixel(clampi(4 + t * 4, 1, W - 2), H - 3, pal["frame"])

	# Upscale nearest-neighbor
	var out := img.duplicate()
	out.resize(size.x, size.y, Image.INTERPOLATE_NEAREST)
	return ImageTexture.create_from_image(out)
