extends Control
## THE LENS · VnContactSheet (Arc 0 of lore/_VISUAL_PROGRAM.md, 2026-09-15)
##
## Every VN framing is math-verified and none has been seen. This rig
## renders the shot list in `res://qa/contact_manifest.json` (written
## by tools/audit/contact_manifest.py) through the SAME nodes the VN
## uses — Background3D for the rooms, Portrait3D for the cast — and
## saves one frame per preset × mood (the establish), one per marker
## the preset owns (under the chapter's primary mood), and one per
## hero GLB × expression. Frames go to `res://qa/contact/<preset>/`
## and `res://qa/contact/_heroes/`; a `_report.json` beside them says
## what was skipped (a GLB not built, a marker not found) and why.
##
## Run on a machine with a GPU and the locale GLBs built (the Deck):
##
##   ./godot/tools/contact_sheet.sh                 # everything
##   ./godot/tools/contact_sheet.sh --only=cabin    # presets whose id starts with
##   ./godot/tools/contact_sheet.sh --png           # lossless (default is JPEG 0.82)
##
## then ./godot/tools/contact_push.sh to hand the frames to Claude.
##
## What a frame contains: the room, its lights, its PostProcess stack
## (the locale's own CanvasLayer inside the SubViewport) — the picture
## as the VN's texture layer receives it. NOT in the frame: THE TRIP,
## the dialogue box, the busts. Those are the window's layers; the
## sheet is the set and the framing.
##
## Not HUD: nothing here joins "ui"; the rig quits when it is done.

const BG_SCENE := preload("res://scenes/vn/Background3D.tscn")
const PORTRAIT_SCENE := preload("res://scenes/vn/Portrait3D.tscn")
const MANIFEST := "res://qa/contact_manifest.json"
const OUT_DIR := "res://qa/contact"

# VnDirector.TYPE_FOV, mirrored: a marker without a `fov` meta takes
# the lens its type implies.
const TYPE_FOV := {"closeup": 45.0, "insert": 35.0}
const DEFAULT_FOV := 50.0

# Frames to wait. A locale's _ready cascade, the PostProcess shaders'
# first compile and the lights' first bounce all need a few frames;
# a camera cut needs one.
const SETTLE_LOAD := 30
const SETTLE_MOOD := 12
const SETTLE_CUT := 6
const SETTLE_EXPR := 24   # the portrait's mood motion has a phase; a third of a second in

var _only: String = ""
var _png: bool = false
var _jpg_quality: float = 0.82
var _report: Dictionary = {
	"captured": 0, "skipped_glb": [], "skipped_marker": [], "skipped_scene": [],
	"presets": 0, "heroes": 0, "seconds": 0.0,
}
var _t0: int = 0


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		var arg := String(a)
		if arg.begins_with("--only="):
			_only = arg.substr(7)
		elif arg == "--png":
			_png = true
	_t0 = Time.get_ticks_msec()
	_run()


func _run() -> void:
	var manifest: Dictionary = _read_manifest()
	if manifest.is_empty():
		push_error("[VnContactSheet] no manifest at %s — run tools/audit/contact_manifest.py" % MANIFEST)
		get_tree().quit(1)
		return
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))
	await _shoot_presets(manifest)
	await _shoot_heroes(manifest)
	_report["seconds"] = float(Time.get_ticks_msec() - _t0) / 1000.0
	_write_report()
	print("[VnContactSheet] %d frame(s) · %d preset(s) · %d hero(es) · %.0f s → %s"
		% [int(_report["captured"]), int(_report["presets"]), int(_report["heroes"]),
		   float(_report["seconds"]), ProjectSettings.globalize_path(OUT_DIR)])
	get_tree().quit()


func _read_manifest() -> Dictionary:
	if not FileAccess.file_exists(MANIFEST):
		return {}
	var f := FileAccess.open(MANIFEST, FileAccess.READ)
	if f == null:
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		return parsed as Dictionary
	return {}


# ── the rooms ─────────────────────────────────────────────────────
func _shoot_presets(manifest: Dictionary) -> void:
	var bg: SubViewportContainer = BG_SCENE.instantiate() as SubViewportContainer
	add_child(bg)
	bg.position = Vector2.ZERO
	var presets: Array = manifest.get("presets", [])
	for pv in presets:
		if not (pv is Dictionary):
			continue
		var p: Dictionary = pv
		var pid: String = String(p.get("id", ""))
		if pid == "" or (_only != "" and not pid.begins_with(_only)):
			continue
		var loaded: bool = bool(bg.call("load_location", pid))
		if not loaded:
			(_report["skipped_glb"] as Array).append(pid)
			var why: String = String(bg.get("last_load_error"))
			if not _report.has("skip_reasons"):
				_report["skip_reasons"] = {}
			(_report["skip_reasons"] as Dictionary)[pid] = why
			print("[VnContactSheet] SKIP %s (%s)" % [pid, why])
			continue
		await _settle(SETTLE_LOAD)
		_report["presets"] = int(_report["presets"]) + 1
		var moods: Array = p.get("moods", [""])
		if moods.is_empty():
			moods = [""]
		var mc: Node = bg.call("get_locale_mood_cycler")
		# The establish under every mood the chapters cue.
		for mv in moods:
			var mood := String(mv)
			bg.call("restore_preset_vantage")
			await _apply_mood(mc, mood)
			await _settle(SETTLE_CUT)
			_save(bg, "%s/%s__establish" % [pid, _mood_tag(mood)])
		# The markers under the primary mood.
		var primary := String(moods[0])
		await _apply_mood(mc, primary)
		var cam: Camera3D = bg.call("get_camera")
		var markers: Array = p.get("markers", [])
		for mkv in markers:
			if not (mkv is Dictionary):
				continue
			var mk: Dictionary = mkv
			var name := String(mk.get("name", ""))
			var kind := String(mk.get("type", ""))
			var node: Node3D = bg.call("find_shot_marker", name)
			if node == null or cam == null:
				(_report["skipped_marker"] as Array).append("%s/%s" % [pid, name])
				continue
			bg.call("set_camera_vantage", cam.position, cam.rotation, cam.fov)  # stops any track
			cam.global_transform = node.global_transform
			var fov: float = float(TYPE_FOV.get(kind, DEFAULT_FOV))
			if node.has_meta("fov"):
				fov = float(node.get_meta("fov"))
			cam.fov = fov
			cam.make_current()
			await _settle(SETTLE_CUT)
			_save(bg, "%s/%s__%s" % [pid, _mood_tag(primary), name])
		bg.call("restore_preset_vantage")
	bg.queue_free()


func _apply_mood(mc: Node, mood: String) -> void:
	if mood == "" or mc == null or not mc.has_method("apply_style_or_mood"):
		return
	var ok: bool = bool(mc.call("apply_style_or_mood", mood))
	if not ok:
		print("[VnContactSheet] mood '%s' unknown to this locale — default look" % mood)
	await _settle(SETTLE_MOOD)


func _mood_tag(mood: String) -> String:
	return "default" if mood == "" else mood


# ── the cast ──────────────────────────────────────────────────────
func _shoot_heroes(manifest: Dictionary) -> void:
	if _only != "" and not "_heroes".begins_with(_only):
		return
	var heroes: Array = manifest.get("heroes", [])
	var exprs: Array = manifest.get("expressions", ["neutral"])
	# The heroes ON DISK, not the manifest's list (2026-10-01: the manifest
	# is written where the repo is, which held 10 models, while the Deck
	# holds every model Hero Studio made — they live on Google Drive, not
	# in git). The GNM experiment files are left out.
	var disk: Array = _heroes_on_disk()
	if not disk.is_empty():
		heroes = disk
	if heroes.is_empty():
		return
	# THE LOOK (2026-10-02): the raw viewport (_save) never shows the
	# portrait's painted pass — it is a material on the container. The
	# container now sits inside its own SubViewport over a neutral paper
	# grey, and `__look_*` frames capture that composite, so the sheet
	# shows the real heroes the way the game draws them.
	var look_vp := SubViewport.new()
	look_vp.size = Vector2i(600, 640)
	look_vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(look_vp)
	var paper := ColorRect.new()
	paper.color = Color(0.56, 0.54, 0.50)
	paper.size = Vector2(600, 640)
	look_vp.add_child(paper)
	var portrait: SubViewportContainer = PORTRAIT_SCENE.instantiate() as SubViewportContainer
	look_vp.add_child(portrait)
	portrait.position = Vector2.ZERO
	portrait.size = Vector2(600, 640)
	for hv in heroes:
		if not (hv is Dictionary):
			continue
		var h: Dictionary = hv
		var path := String(h.get("path", ""))
		var file := String(h.get("file", ""))
		if path == "" or not ResourceLoader.exists(path):
			(_report["skipped_glb"] as Array).append(file)
			continue
		var ok: bool = bool(portrait.call("load_character", path, "neutral"))
		if not ok:
			(_report["skipped_glb"] as Array).append(file)
			continue
		_report["heroes"] = int(_report["heroes"]) + 1
		for ev in exprs:
			var expr := String(ev)
			portrait.call("set_expression", expr)
			await _settle(SETTLE_EXPR)
			_save(portrait, "_heroes/%s__%s" % [file.get_basename(), expr], true)
		# the director's dialogue sizes at eye level, neutral, a fixed take
		# (portrait direction, 2026-10-01) — so a sheet shows whether the
		# close-ups land on each model's face
		if portrait.has_method("set_shot"):
			portrait.call("set_expression", "neutral")
			for sz in ["mcu", "cu", "ecu"]:
				portrait.call("set_shot", sz, "eye", 7)
				await _settle(SETTLE_EXPR)
				_save(portrait, "_heroes/%s__shot_%s" % [file.get_basename(), sz], true)
			# the painted look, composited: the three sizes, then two moods
			for lk: Array in [["mcu", "neutral"], ["cu", "neutral"], ["ecu", "neutral"], ["cu", "sad"], ["cu", "angry"]]:
				portrait.call("set_shot", String(lk[0]), "eye", 7)
				portrait.call("set_expression", String(lk[1]))
				if portrait.has_method("snap_look"):
					portrait.call("snap_look")
				await _settle(SETTLE_EXPR)
				_save_texture(look_vp.get_texture(), "_heroes/%s__look_%s_%s" % [file.get_basename(), lk[0], lk[1]])
			portrait.call("set_expression", "neutral")
			portrait.call("set_shot", "medium", "eye", 7)
	look_vp.queue_free()


func _heroes_on_disk() -> Array:
	var out: Array = []
	var root := "res://assets/3d/characters/heroes"
	var d := DirAccess.open(root)
	if d == null:
		return out
	for f: String in d.get_files():
		if not f.ends_with(".glb") or f.ends_with("_gnm.glb"):
			continue
		out.append({"path": root + "/" + f, "file": f})
	out.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return String(a["file"]) < String(b["file"]))
	return out


# ── capture ───────────────────────────────────────────────────────
func _settle(frames: int) -> void:
	for i in frames:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw


func _save_texture(tex: Texture2D, rel: String) -> void:
	if tex == null:
		return
	var img: Image = tex.get_image()
	if img == null:
		return
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR + "/" + rel.get_base_dir()))
	img.convert(Image.FORMAT_RGB8)
	img.save_jpg(ProjectSettings.globalize_path(OUT_DIR + "/" + rel) + ".jpg", 0.9)
	_report["captured"] = int(_report.get("captured", 0)) + 1


func _save(container: SubViewportContainer, rel: String, force_png: bool = false) -> void:
	var tex: Texture2D = container.call("get_viewport_texture")
	if tex == null:
		return
	var img: Image = tex.get_image()
	if img == null:
		return
	var dir := OUT_DIR + "/" + rel.get_base_dir()
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(dir))
	var base := ProjectSettings.globalize_path(OUT_DIR + "/" + rel)
	var err: Error
	if _png or force_png:
		err = img.save_png(base + ".png")
	else:
		# A transparent portrait needs PNG; a room is opaque and a
		# thousand of them at 1280×720 want JPEG.
		img.convert(Image.FORMAT_RGB8)
		err = img.save_jpg(base + ".jpg", _jpg_quality)
	if err == OK:
		_report["captured"] = int(_report["captured"]) + 1
	else:
		push_warning("[VnContactSheet] could not write %s (%d)" % [base, err])


func _write_report() -> void:
	var f := FileAccess.open(OUT_DIR + "/_report.json", FileAccess.WRITE)
	if f == null:
		return
	_report["when"] = Time.get_datetime_string_from_system()
	_report["only"] = _only
	f.store_string(JSON.stringify(_report, "\t") + "\n")
	f.close()
