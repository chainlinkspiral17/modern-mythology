extends RefCounted
## HERO ART (2026-10-12): the 2D pictures that live on the world's surfaces.
##
## The user: "For 2D images, art, specific textures like the Aria street
## painting, add them to the hero prop as image generations or textures that
## can be imported." Hero Studio's roster has an `art` kind: an image
## generated like any concept, then INSTALLED as the picture itself at
## assets/art/hero/<slug>.<png|jpg|webp> (no Meshy). Each art entry names, in
## `apply`, the surfaces it belongs on:
##
##   {"locale": "salty_tome_interior", "center": [x, y, z], "size": [w, h],
##    "facing": "-y", "hide": ["Face_Band_", ...], "label": "..."}
##
## center is in BLENDER coordinates (the builders' frame), size in metres,
## facing the side the viewer stands on (+x | -x | +y | -y | up). When
## Background3D loads a locale, apply() lays a lit, matte quad with the
## picture at each row of that locale and hides the box stand-in the row
## names. No picture installed (a checkout without the Drive's files) = the
## stand-in stays and nothing else changes.

const ROSTER := "res://tools/meshy_roster.json"
const ART_ROOT := "res://assets/art/hero/"
const EXTS: Array[String] = [".png", ".jpg", ".jpeg", ".webp"]
const LIFT := 0.002          # off the surface, so the quad never fights it
## (2026-11-09) ART CLARITY. The render layer of each picture's white twin,
## seen only by ArtMask's camera (the main cameras drop it): the passes
## after the render step back over the pictures where the mask is white.
const ART_LAYER: int = 1 << 19
## A picture lights itself a little from its own image, so a dim room does
## not turn it to mud ("art is very murky"); a lit room barely changes.
const ART_SELF_LIGHT: float = 0.22

static var _rows_by_locale: Dictionary = {}
static var _loaded: bool = false
## (2026-10-14) what the last apply() did, picture by picture — "placed",
## "no picture installed", "picture did not load", "stand-in not found" —
## for the contact sheet's report (the Deck's renders could not say why a
## picture was missing).
static var last_report: Dictionary = {}
## (2026-10-14) every picture the last apply() laid, for the director's
## art shots and the player's stillness moments:
## {slug, name, inspect, cat, words, quad (MeshInstance3D), size (Vector2)}
static var placed_art: Array = []
static var current_locale: String = ""
## The object words a narration line can name a picture by — nouns only
## ("the calendar Diego stopped updating" answers to "calendar", never to
## "Diego").
const OBJECT_WORDS: Array[String] = [
	"poster", "painting", "portrait", "print", "photo", "photograph", "picture", "mural",
	"canvas", "artwork", "map", "chart", "calendar", "diploma", "certificate", "menu",
	"flyer", "postcard", "drawing", "sketch", "album", "comic", "corkboard",
	"bulletin", "collage", "screen", "monitor", "television", "tv", "sign",
	"billboard", "banner", "marquee", "plaque", "neon", "tapestry", "nebula", "starfish",
	"letter", "notice", "laptop",
]
# (not "face", "table", "frame", "board", "note", "cover", "display": in
# narration they are mostly people, furniture and figures of speech)


static func _load_roster() -> void:
	_loaded = true
	_rows_by_locale.clear()
	if not FileAccess.file_exists(ROSTER):
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(ROSTER))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_warning("[HeroArt] roster did not parse")
		return
	var data: Dictionary = parsed
	var entries: Array = data.get("entries", [])
	for item: Variant in entries:
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var e: Dictionary = item
		if String(e.get("kind", "")) != "art":
			continue
		var stem: String = String(e.get("file", "")).get_basename()
		var rows: Array = e.get("apply", [])
		for rv: Variant in rows:
			if typeof(rv) != TYPE_DICTIONARY:
				continue
			var row: Dictionary = rv
			var loc: String = String(row.get("locale", ""))
			if loc == "":
				continue
			row = row.duplicate()
			row["_name"] = String(e.get("name", ""))
			row["_inspect"] = bool(e.get("inspect", false))
			row["_cat"] = String(e.get("art_cat", ""))
			row["_words"] = _object_words(String(e.get("slug", "")) + " " + String(e.get("name", "")))
			if not _rows_by_locale.has(loc):
				_rows_by_locale[loc] = []
			var lst: Array = _rows_by_locale[loc]
			lst.append({"slug": String(e.get("slug", stem)), "stem": stem, "row": row})


## Lay every installed picture for `locale` on its surface under `root`.
## Returns how many pictures went up.
static func _object_words(text: String) -> PackedStringArray:
	var out := PackedStringArray()
	for raw: String in text.to_lower().replace("_", " ").replace("'", " ").split(" ", false):
		var w: String = raw.strip_edges().trim_suffix(",").trim_suffix(".")
		if w.ends_with("s") and not w.ends_with("ss"):
			w = w.substr(0, w.length() - 1)
		if w in OBJECT_WORDS and not w in out:
			out.append(w)
	return out


## The pictures laid in the current room that still exist.
static func placements() -> Array:
	var live: Array = []
	for pv: Variant in placed_art:
		var p: Dictionary = pv
		var q: Variant = p.get("quad")
		if q != null and is_instance_valid(q) and (q as Node3D).is_inside_tree():
			live.append(p)
	return live


static func apply(root: Node, locale: String, preset_id: String = "") -> int:
	last_report = {}
	placed_art = []
	current_locale = locale
	if root == null:
		return 0
	if not _loaded:
		_load_roster()
	if not _rows_by_locale.has(locale):
		return 0
	var placed: int = 0
	# (2026-11-08) larger pictures first, so a smaller one laid over it on the
	# same plane — a sign's text strip on its panel, one letter on the brand
	# board, comics fanned over each other — STACKS on top (see _stack)
	# instead of z-fighting with it
	var items: Array = (_rows_by_locale[locale] as Array).duplicate()
	items.sort_custom(func(a: Variant, b: Variant) -> bool: return _area(a) > _area(b))
	for iv: Variant in items:
		var it: Dictionary = iv
		var slug: String = String(it["slug"])
		var tex: Texture2D = _texture(String(it["stem"]))
		if tex == null:
			last_report[slug] = _why_missing(String(it["stem"]))
			continue
		var row: Dictionary = it["row"]
		# (2026-11-08) a slug that NAMES views — `…__street_rain`, `…__suite_4am`
		# — is a picture for those views only, like a builder part named
		# `<Name>__<preset>`. Background3D strips such parts before the
		# pictures are laid, so the quads were never stripped: every view of
		# the editing suite showed the tide AND the 4 a.m. monitors, Pasadena
		# its day street and its rain street on one plane.
		var owners: PackedStringArray = slug.split("__").slice(1)
		if preset_id != "" and not owners.is_empty() and not owners.has(preset_id) \
				and _names_presets(owners):
			continue
		# (2026-10-27) a picture that belongs to some views of a set and not
		# others: `not_presets` skips it there (vol 6's NexCorp logos are not
		# on the same station in 2003)
		var skip_v: Variant = row.get("not_presets", [])
		if preset_id != "" and typeof(skip_v) == TYPE_ARRAY and (skip_v as Array).has(preset_id):
			continue
		# (2026-10-28, the Deck: "The Aria face should be a generation. That
		# looks bad.") a picture PAINTED on a surface — a mural on brick — laid
		# as a hard-edged card read as a poster taped up. `feather` (a fraction
		# of the picture's size) fades its edges to clear, so only the paint
		# sits on the wall.
		var feather: float = float(row.get("feather", 0.0))
		if feather > 0.0:
			tex = _feathered(tex, feather)
		var quad: MeshInstance3D = _quad(tex, row)
		quad.name = "HeroArt_" + slug
		var lvl: int = _stack(quad)
		root.add_child(quad)
		var hid: int = 0
		var hide_v: Variant = row.get("hide", [])
		if typeof(hide_v) == TYPE_ARRAY:
			hid = _hide(root, hide_v as Array, quad)
		placed_art.append({"slug": slug, "name": String(row.get("_name", slug)), "inspect": bool(row.get("_inspect", false)),
			"cat": String(row.get("_cat", "")), "words": row.get("_words", PackedStringArray()),
			"quad": quad, "size": (quad.mesh as QuadMesh).size, "lvl": lvl})
		last_report[slug] = "placed (%dx%d px), %d stand-in piece(s) hidden" % [tex.get_width(), tex.get_height(), hid] \
			if hid > 0 or (hide_v as Array).is_empty() else "placed, but its stand-in was NOT found (it may cover the picture)"
		placed += 1
	if placed > 0:
		print("[HeroArt] %s: %d picture(s) laid on their surfaces" % [locale, placed])
	return placed


## Whether `parts` (a slug's `__` suffixes) name Background3D presets — a
## numbered copy (`__2`) does not.
static func _names_presets(parts: PackedStringArray) -> bool:
	var bg: GDScript = load("res://scripts/vn/Background3D.gd") as GDScript
	if bg == null:
		return true
	var cm: Dictionary = bg.get_script_constant_map()
	var presets_v: Variant = cm.get("CAMERA_PRESETS", {})
	if typeof(presets_v) != TYPE_DICTIONARY:
		return true
	var presets: Dictionary = presets_v
	for p: String in parts:
		if presets.has(p):
			return true
	return false


static func _area(item: Variant) -> float:
	var it: Dictionary = item
	var row: Dictionary = it["row"]
	var sz: Array = row.get("size", [1.0, 1.0])
	return float(sz[0]) * float(sz[1])


## (2026-11-08) a picture laid on the same plane as pictures already placed,
## over them: lifted STACK_STEP above the highest it covers, so the two never
## z-fight (hero_art_placement_audit's OVERLAP). Returns its stack level.
const STACK_STEP := 0.002

static func _stack(quad: MeshInstance3D) -> int:
	var xf: Transform3D = quad.transform
	var n: Vector3 = xf.basis.z.normalized()
	var ax: Vector3 = xf.basis.x.normalized()
	var ay: Vector3 = xf.basis.y.normalized()
	var sz: Vector2 = (quad.mesh as QuadMesh).size
	var top: int = -1
	for pv: Variant in placed_art:
		var p: Dictionary = pv
		var other: MeshInstance3D = p.get("quad") as MeshInstance3D
		if other == null or not is_instance_valid(other):
			continue
		var oxf: Transform3D = other.transform
		if oxf.basis.z.normalized().dot(n) < 0.99:
			continue
		var d: Vector3 = oxf.origin - xf.origin
		if absf(d.dot(n)) > 0.004 + STACK_STEP * float(int(p.get("lvl", 0))):
			continue
		var osz: Vector2 = p.get("size", Vector2.ONE)
		var ox: float = maxf(0.0, (sz.x + osz.x) * 0.5 - absf(d.dot(ax)))
		var oy: float = maxf(0.0, (sz.y + osz.y) * 0.5 - absf(d.dot(ay)))
		if ox * oy >= 0.02 * minf(sz.x * sz.y, osz.x * osz.y):
			top = maxi(top, int(p.get("lvl", 0)))
	var lvl: int = top + 1
	if lvl > 0:
		quad.transform = Transform3D(xf.basis, xf.origin + n * STACK_STEP * float(lvl))
	return lvl


static func _why_missing(stem: String) -> String:
	for ext: String in EXTS:
		var path: String = ART_ROOT + stem + ext
		if FileAccess.file_exists(path) or ResourceLoader.exists(path):
			return "picture did not load (%s)" % path.get_file()
	return "no picture installed"


static func _texture(stem: String) -> Texture2D:
	for ext: String in EXTS:
		var path: String = ART_ROOT + stem + ext
		if ResourceLoader.exists(path):
			var res: Resource = load(path)
			var t: Texture2D = res as Texture2D
			if t != null:
				return t
		if FileAccess.file_exists(path):
			# pulled from the Drive but not yet imported by the editor
			var img: Image = Image.load_from_file(path)
			if img != null and not img.is_empty():
				img.generate_mipmaps()
				return ImageTexture.create_from_image(img)
	return null


static func _feathered(tex: Texture2D, feather: float) -> Texture2D:
	var src: Image = tex.get_image()
	if src == null or src.is_empty():
		return tex
	var img: Image = src.duplicate() as Image
	if img.is_compressed():
		if img.decompress() != OK:
			return tex
	img.convert(Image.FORMAT_RGBA8)
	var longest: int = maxi(img.get_width(), img.get_height())
	if longest > 768:
		var k: float = 768.0 / float(longest)
		img.resize(maxi(1, int(img.get_width() * k)), maxi(1, int(img.get_height() * k)), Image.INTERPOLATE_BILINEAR)
	var w: int = img.get_width()
	var h: int = img.get_height()
	var f: float = clampf(feather, 0.01, 0.5)
	for y: int in h:
		var v: float = float(y) / float(maxi(h - 1, 1))
		var dv: float = minf(v, 1.0 - v)
		for x: int in w:
			var u: float = float(x) / float(maxi(w - 1, 1))
			var d: float = minf(minf(u, 1.0 - u), dv)
			if d >= f:
				continue
			var px: Color = img.get_pixel(x, y)
			px.a *= smoothstep(0.0, f, d)
			img.set_pixel(x, y, px)
	img.generate_mipmaps()
	return ImageTexture.create_from_image(img)


static func _quad(tex: Texture2D, row: Dictionary) -> MeshInstance3D:
	var c: Array = row.get("center", [0.0, 0.0, 0.0])
	var sz: Array = row.get("size", [1.0, 1.0])
	var facing: String = String(row.get("facing", "-y"))
	var mesh := QuadMesh.new()
	mesh.size = Vector2(float(sz[0]), float(sz[1]))
	var mat := StandardMaterial3D.new()
	mat.albedo_texture = tex
	mat.roughness = 1.0
	mat.metallic = 0.0
	mat.metallic_specular = 0.12
	# (2026-10-27, the Deck: a carved sign read "yadoT tisiV emoC") a picture
	# is one-sided: seen from behind it showed its art MIRRORED — the back of
	# a sign, a poster, a window view. The back is a plain board (below); a
	# row may still ask for "two_sided": true.
	var two_sided: bool = bool(row.get("two_sided", false))
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED if two_sided else BaseMaterial3D.CULL_BACK
	mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	if float(row.get("feather", 0.0)) > 0.0:
		mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	# (2026-10-14) a screen or a neon sign makes its own light — painted
	# like a poster it went dead in every night room. `glow` (roster row) is
	# the emission energy: the picture itself lights, on top of the room's
	var glow: float = float(row.get("glow", 0.0))
	mat.emission_enabled = true
	mat.emission_texture = tex
	mat.emission = Color(1, 1, 1)
	mat.emission_energy_multiplier = glow if glow > 0.0 else ART_SELF_LIGHT
	# (2026-10-13) never stretch: a backdrop card (`fit: tile`) far wider
	# than any generator's widest frame (21:9) — a 150 m bluff, an 18 m
	# treeline — repeats the picture across its width; any other surface
	# of a shape no generator makes (a 5:1 shop sign) shows the image's
	# middle band, which the prompt told the generator to compose into
	var img_aspect: float = float(tex.get_width()) / maxf(float(tex.get_height()), 1.0)
	var quad_aspect: float = float(sz[0]) / maxf(float(sz[1]), 0.001)
	var fit: String = String(row.get("fit", ""))
	if fit == "tile" and quad_aspect > img_aspect * 1.5:
		mat.texture_repeat = true
		mat.uv1_scale = Vector3(roundf(quad_aspect / img_aspect), 1.0, 1.0)
	elif fit != "tile" and quad_aspect > img_aspect * 1.15:
		# a sign far wider than the generator's frame: show its middle band
		var sy: float = img_aspect / quad_aspect
		mat.uv1_scale = Vector3(1.0, sy, 1.0)
		mat.uv1_offset = Vector3(0.0, (1.0 - sy) * 0.5, 0.0)
	elif fit != "tile" and quad_aspect < img_aspect / 1.15:
		var sx: float = quad_aspect / img_aspect
		mat.uv1_scale = Vector3(sx, 1.0, 1.0)
		mat.uv1_offset = Vector3((1.0 - sx) * 0.5, 0.0, 0.0)
	mesh.material = mat
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	# blender (x, y, z) → godot (x, z, -y); a QuadMesh faces +Z
	var pos := Vector3(float(c[0]), float(c[2]), -float(c[1]))
	var normal := Vector3(0, 0, 1)
	var basis := Basis()
	match facing:
		"+y":
			basis = Basis(Vector3.UP, PI)
			normal = Vector3(0, 0, -1)
		"-y":
			basis = Basis()
			normal = Vector3(0, 0, 1)
		"+x":
			basis = Basis(Vector3.UP, PI / 2.0)
			normal = Vector3(1, 0, 0)
		"-x":
			basis = Basis(Vector3.UP, -PI / 2.0)
			normal = Vector3(-1, 0, 0)
		"up":
			basis = Basis(Vector3.RIGHT, -PI / 2.0)
			normal = Vector3(0, 1, 0)
	mi.transform = Transform3D(basis, pos + normal * LIFT)
	mi.layers = 1
	# the picture's twin for the art mask: the same quad, unshaded white,
	# on ART_LAYER only (ArtMask's camera sees it; the main cameras do not)
	var twin := MeshInstance3D.new()
	twin.name = "ArtMaskTwin"
	twin.mesh = mesh
	var tw_mat := StandardMaterial3D.new()
	tw_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	tw_mat.albedo_color = Color(1, 1, 1, 1)
	tw_mat.cull_mode = mat.cull_mode
	twin.material_override = tw_mat
	twin.layers = ART_LAYER
	twin.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mi.add_child(twin)
	if not two_sided:
		# the back: the picture's own average colour, darkened — the bare
		# board or paper behind it, not a black hole and not the art reversed
		var back := MeshInstance3D.new()
		var bq := QuadMesh.new()
		bq.size = mesh.size
		var bm := StandardMaterial3D.new()
		bm.albedo_color = _back_colour(tex)
		bm.roughness = 1.0
		bm.cull_mode = BaseMaterial3D.CULL_BACK
		bq.material = bm
		back.mesh = bq
		back.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		back.transform = Transform3D(Basis(Vector3.UP, PI), Vector3(0, 0, -0.001))
		mi.add_child(back)
	return mi


static func _back_colour(tex: Texture2D) -> Color:
	var c := Color(0.32, 0.27, 0.22)
	var img: Image = tex.get_image() if tex != null else null
	if img != null and not img.is_empty():
		var small: Image = img.duplicate() as Image
		if small.is_compressed():
			small.decompress()
		# a bilinear shrink to one pixel samples the centre; average a 16 x 16
		small.resize(16, 16, Image.INTERPOLATE_BILINEAR)
		var acc := Color(0, 0, 0)
		for yy in 16:
			for xx in 16:
				acc += small.get_pixel(xx, yy)
		c = Color(acc.r / 256.0, acc.g / 256.0, acc.b / 256.0)
	return Color(c.r * 0.55, c.g * 0.55, c.b * 0.55, 1.0)


## Hide the stand-in under one picture. (2026-10-13) A room can hold
## several surfaces of one family (three Poster_* on three walls), each its
## own picture now: only the prefix-matched nodes UNDER this quad hide — in
## its rectangle (+15 cm) and within 30 cm of its plane. When nothing
## matched there (a builder that parents its pieces at the origin), every
## match in the room hides, as before.
static func _hide(root: Node, prefixes: Array, quad: MeshInstance3D = null) -> int:
	if prefixes.is_empty():
		return 0
	# exact names, `Name_` prefixes, and (2026-10-14) a stand-in's own parts
	# — Donut_Sign's Donut_SignText, Poster_Faded's Poster_Faded_Title, the
	# lettering boxes that sit in front of the sign face and would float over
	# the picture — which are hidden only when they lie under this picture
	var exact: Array[Node3D] = []
	var parts: Array[Node3D] = []
	for n: Node in root.find_children("*", "Node3D", true, false):
		var nm: String = String(n.name)
		if nm.begins_with("HeroArt_"):
			continue
		for pv: Variant in prefixes:
			var h: String = String(pv)
			if nm == h or (h.ends_with("_") and nm.begins_with(h)):
				exact.append(n as Node3D)
				break
			if nm.begins_with(h):
				parts.append(n as Node3D)
				break
	var near: Array[Node3D] = []
	var near_parts: Array[Node3D] = []
	if quad != null:
		var inv: Transform3D = quad.transform.affine_inverse()
		var half: Vector2 = (quad.mesh as QuadMesh).size * 0.5 + Vector2(0.15, 0.15)
		for pair: Array in [[exact, near], [parts, near_parts]]:
			var src: Array[Node3D] = pair[0]
			var dst: Array[Node3D] = pair[1]
			for n3: Node3D in src:
				# (2026-10-14) relative to the room, not the world: apply() runs
				# before the room is in the tree, where global_position errors
				# (2026-11-08) the mesh's own CENTRE: the builders leave every
				# part's origin at the world origin (the GLB nodes carry no
				# translation), so by origin no part was ever "under" a picture
				# — a stand-in's extra pieces (the corkboard's frame, a fourth
				# pinned card) never hid and stood in front of its picture
				var local: Vector3 = inv * _rel_center(root, n3)
				if absf(local.x) <= half.x and absf(local.y) <= half.y and absf(local.z) <= 0.30:
					dst.append(n3)
	var hidden: Array[Node3D] = near if not near.is_empty() else exact
	for n3: Node3D in hidden:
		n3.visible = false
	for n3: Node3D in near_parts:
		n3.visible = false
	return hidden.size() + near_parts.size()


## A node's visual centre in `root`'s space: a mesh's AABB centre, else its
## origin.
static func _rel_center(root: Node, n: Node3D) -> Vector3:
	var mi: MeshInstance3D = n as MeshInstance3D
	if mi == null or mi.mesh == null:
		return _rel_origin(root, n)
	var c: Vector3 = mi.mesh.get_aabb().get_center()
	var xf: Transform3D = n.transform
	var p: Node = n.get_parent()
	while p != null and p != root:
		var p3: Node3D = p as Node3D
		if p3 != null:
			xf = p3.transform * xf
		p = p.get_parent()
	return xf * c


## A node's origin in `root`'s space, by walking up its parents (works
## before the room is added to the scene tree).
static func _rel_origin(root: Node, n: Node3D) -> Vector3:
	var xf: Transform3D = n.transform
	var p: Node = n.get_parent()
	while p != null and p != root:
		var p3: Node3D = p as Node3D
		if p3 != null:
			xf = p3.transform * xf
		p = p.get_parent()
	return xf.origin
