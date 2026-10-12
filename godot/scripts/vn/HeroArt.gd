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

static var _rows_by_locale: Dictionary = {}
static var _loaded: bool = false


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
			if not _rows_by_locale.has(loc):
				_rows_by_locale[loc] = []
			var lst: Array = _rows_by_locale[loc]
			lst.append({"slug": String(e.get("slug", stem)), "stem": stem, "row": row})


## Lay every installed picture for `locale` on its surface under `root`.
## Returns how many pictures went up.
static func apply(root: Node, locale: String) -> int:
	if root == null:
		return 0
	if not _loaded:
		_load_roster()
	if not _rows_by_locale.has(locale):
		return 0
	var placed: int = 0
	var items: Array = _rows_by_locale[locale]
	for iv: Variant in items:
		var it: Dictionary = iv
		var tex: Texture2D = _texture(String(it["stem"]))
		if tex == null:
			continue
		var row: Dictionary = it["row"]
		var quad: MeshInstance3D = _quad(tex, row)
		quad.name = "HeroArt_" + String(it["slug"])
		root.add_child(quad)
		var hide_v: Variant = row.get("hide", [])
		if typeof(hide_v) == TYPE_ARRAY:
			_hide(root, hide_v as Array)
		placed += 1
	if placed > 0:
		print("[HeroArt] %s: %d picture(s) laid on their surfaces" % [locale, placed])
	return placed


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
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
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
	return mi


static func _hide(root: Node, prefixes: Array) -> void:
	if prefixes.is_empty():
		return
	for n: Node in root.find_children("*", "Node3D", true, false):
		var nm: String = String(n.name)
		if nm.begins_with("HeroArt_"):
			continue
		for pv: Variant in prefixes:
			if nm.begins_with(String(pv)):
				(n as Node3D).visible = false
				break
