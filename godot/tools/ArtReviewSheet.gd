extends SceneTree
## ART REVIEW SHEET (2026-10-14): every installed hero-art picture as small
## contact sheets + a per-picture report, for Claude to judge without the
## 1.3 GB of originals. The user: "the 2D art from the hero has been sent
## over. Take a look and see how well it works with the existing 3D assets."
##
##   godot --headless --path godot --script res://tools/ArtReviewSheet.gd
##   (bash godot/tools/art_review.sh does this, then contact_push.sh)
##
## Writes godot/qa/contact/_art/:
##   sheet_NN.jpg   — 6 x 4 cells of 256 px, roster order (most-played first)
##   index.json     — sheet → [slug per cell]
##   report.json    — per picture: pixels, its aspect vs the surface's, mean
##                    luminance / saturation, alpha in use, a border band that
##                    differs from the inside (a painted frame the prompt asked
##                    not to have), the fit (tile / crop / exact)
## Headless: image work only, nothing is rendered.

const ROSTER := "res://tools/meshy_roster.json"
const ART := "res://assets/art/hero/"
const OUT := "res://qa/contact/_art/"
const EXTS: Array[String] = [".png", ".jpg", ".jpeg", ".webp"]
const CELL := 256
const COLS := 6
const ROWS := 4


func _initialize() -> void:
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(ROSTER))
	if typeof(data) != TYPE_DICTIONARY:
		push_error("roster did not parse")
		quit(1)
		return
	var roster: Dictionary = data
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	var items: Array = []
	var entries: Array = roster.get("entries", [])
	for ev: Variant in entries:
		var e: Dictionary = ev
		if String(e.get("kind", "")) != "art":
			continue
		var stem: String = String(e.get("file", "")).get_basename()
		var path: String = ""
		for x: String in EXTS:
			if FileAccess.file_exists(ART + stem + x):
				path = ART + stem + x
				break
		if path != "":
			items.append({"e": e, "path": path})
	var report: Dictionary = {}
	var index: Dictionary = {}
	var per: int = COLS * ROWS
	var sheet: Image = null
	var sheet_n: int = 0
	var cells: Array = []
	for i in items.size():
		var it: Dictionary = items[i]
		var e: Dictionary = it["e"]
		var slug: String = String(e.get("slug", ""))
		var img: Image = Image.load_from_file(ProjectSettings.globalize_path(String(it["path"])))
		if img == null or img.is_empty():
			report[slug] = {"error": "could not load"}
			continue
		if img.is_compressed():
			img.decompress()
		img.convert(Image.FORMAT_RGBA8)
		report[slug] = _stats(img, e)
		if i % per == 0:
			if sheet != null:
				_save(sheet, sheet_n, cells, index)
				sheet_n += 1
			sheet = Image.create(COLS * CELL, ROWS * CELL, false, Image.FORMAT_RGB8)
			sheet.fill(Color(0.12, 0.12, 0.13))
			cells = []
		var slot: int = i % per
		var th: Image = img.duplicate() as Image
		var w: int = th.get_width()
		var h: int = th.get_height()
		var sc: float = float(CELL - 8) / float(maxi(w, h))
		th.resize(maxi(1, int(w * sc)), maxi(1, int(h * sc)), Image.INTERPOLATE_LANCZOS)
		th.convert(Image.FORMAT_RGB8)
		var ox: int = (slot % COLS) * CELL + (CELL - th.get_width()) / 2
		var oy: int = (slot / COLS) * CELL + (CELL - th.get_height()) / 2
		sheet.blit_rect(th, Rect2i(0, 0, th.get_width(), th.get_height()), Vector2i(ox, oy))
		cells.append(slug)
	if sheet != null:
		_save(sheet, sheet_n, cells, index)
	_write(OUT + "index.json", index)
	_write(OUT + "report.json", report)
	print("[ArtReviewSheet] %d picture(s) on %d sheet(s) → %s" % [items.size(), sheet_n + (1 if sheet != null else 0), OUT])
	quit(0)


func _save(sheet: Image, n: int, cells: Array, index: Dictionary) -> void:
	var name: String = "sheet_%02d.jpg" % n
	sheet.save_jpg(ProjectSettings.globalize_path(OUT + name), 0.82)
	index[name] = cells.duplicate()


func _write(path: String, d: Dictionary) -> void:
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify(d, " ", true))
		f.close()


func _stats(img: Image, e: Dictionary) -> Dictionary:
	var w: int = img.get_width()
	var h: int = img.get_height()
	var size_v: Variant = e.get("size", [])
	var sw: float = 0.0
	var sh: float = 0.0
	if typeof(size_v) == TYPE_ARRAY and (size_v as Array).size() == 2:
		sw = float((size_v as Array)[0])
		sh = float((size_v as Array)[1])
	if sw <= 0.0:
		var apply_v: Variant = e.get("apply", [])
		if typeof(apply_v) == TYPE_ARRAY and not (apply_v as Array).is_empty():
			var row: Dictionary = (apply_v as Array)[0]
			var sz: Array = row.get("size", [1.0, 1.0])
			sw = float(sz[0])
			sh = float(sz[1])
	var lum := 0.0
	var sat := 0.0
	var alpha_used := false
	var inner := Vector3.ZERO
	var border := Vector3.ZERO
	var ni: int = 0
	var nb: int = 0
	var nall: int = 0
	var step: int = maxi(1, mini(w, h) / 64)
	var band: int = maxi(2, mini(w, h) / 40)
	var y: int = 0
	while y < h:
		var x: int = 0
		while x < w:
			var c: Color = img.get_pixel(x, y)
			lum += c.get_luminance()
			sat += c.s
			nall += 1
			if c.a < 0.98:
				alpha_used = true
			var v := Vector3(c.r, c.g, c.b)
			if x < band or y < band or x >= w - band or y >= h - band:
				border += v
				nb += 1
			elif x > w / 6 and x < w * 5 / 6 and y > h / 6 and y < h * 5 / 6:
				inner += v
				ni += 1
			x += step
		y += step
	var n: float = float(maxi(1, nall))
	var bmean: Vector3 = border / float(maxi(1, nb))
	var imean: Vector3 = inner / float(maxi(1, ni))
	var img_aspect: float = float(w) / float(maxi(1, h))
	var surf_aspect: float = sw / maxf(sh, 0.001)
	var fit: String = String(e.get("fit", ""))
	if fit == "":
		fit = "exact" if absf(log(img_aspect / maxf(surf_aspect, 0.001))) < 0.14 else "crop"
	return {
		"px": [w, h], "img_aspect": snappedf(img_aspect, 0.01), "surface_m": [sw, sh],
		"surface_aspect": snappedf(surf_aspect, 0.01), "fit": fit,
		"mean_lum": snappedf(lum / n, 0.01), "mean_sat": snappedf(sat / n, 0.01),
		"alpha": alpha_used, "border_vs_inner": snappedf(bmean.distance_to(imean), 0.01),
		"cat": String(e.get("art_cat", "")), "locale": _locale(e),
	}


func _locale(e: Dictionary) -> String:
	var apply_v: Variant = e.get("apply", [])
	if typeof(apply_v) == TYPE_ARRAY and not (apply_v as Array).is_empty():
		var row: Dictionary = (apply_v as Array)[0]
		return String(row.get("locale", ""))
	return ""
