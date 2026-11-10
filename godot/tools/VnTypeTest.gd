extends Node
## DIALOGUE TYPE TEST (2026-11-10): the text box while a line TYPES, which
## VnLineShot (a rested line) never sees. The user: "text is partially
## rendering outside the background box on the right before it continues to
## the next line" / "make the text work. don't break it on screen like this."
##
##   xvfb-run -a -s "-screen 0 1720x720x24" godot --path godot \
##     --rendering-driver opengl3 --resolution 1720x720 res://tools/VnTypeTest.tscn -- \
##     --shots vol5_ch1_magician:19,vol3_ch1_x:4 --lines 6 [--out /abs/dir] [--size 1720x720]
##   (or `godot --headless …` for the checks alone, no pictures: fast)
##
## For each shot it reads --lines lines as a reader would and, on EVERY frame
## of the typing, checks: the whole line is laid out from the first character
## (revealed, not re-set), its line count never changes, the laid-out text is
## no taller than the body, the body and the plate are inside the screen, and
## the plate covers the text. With --out it saves a frame a third of the way
## through each line's typing. Exit 1 on any finding. Not HUD; quits when done.

const ENGINE := preload("res://scenes/game/GameEngine.tscn")
var _args: Dictionary = {}
var _bad: int = 0
var _lines: int = 0


func _ready() -> void:
	var ua: PackedStringArray = OS.get_cmdline_user_args()
	for i in ua.size():
		if ua[i].begins_with("--"):
			_args[ua[i].trim_prefix("--")] = ua[i + 1] if i + 1 < ua.size() and not ua[i + 1].begins_with("--") else ""
	_run.call_deferred()


func _flag(where: String, what: String) -> void:
	_bad += 1
	print("  ✗ %s · %s" % [where, what])


func _check_frame(dlg: Control, where: String, state: Dictionary) -> void:
	var body: RichTextLabel = dlg.get("_body")
	var plate: Control = dlg.get("_plate")
	var full: String = String(dlg.get("_full_text"))
	if body == null or full == "":
		return
	var screen: Rect2 = Rect2(Vector2.ZERO, get_viewport().get_visible_rect().size)
	if body.text != full:
		_flag(where, "the body holds %d characters of a %d-character line (re-set as it types)" % [body.text.length(), full.length()])
	var lc: int = body.get_line_count()
	if int(state.get("lines", lc)) != lc:
		_flag(where, "the line count changed while typing: %d → %d" % [int(state.get("lines", lc)), lc])
	state["lines"] = lc
	var ch: float = float(body.get_content_height())
	if ch > body.size.y + 1.5:
		_flag(where, "the text is %.0f px tall in a %.0f px body (its last line is cut off)" % [ch, body.size.y])
	var br: Rect2 = Rect2(body.global_position, Vector2(float(body.get_content_width()), ch))
	if not screen.grow(0.5).encloses(br):
		_flag(where, "the text %s is not inside the screen %s" % [br, screen])
	if plate != null and plate.visible and int(state.get("frame", 0)) > 30:
		var pr: Rect2 = plate.get_global_rect()
		if not screen.grow(20.0).encloses(pr):
			_flag(where, "the plate %s runs off the screen" % pr)
		if not pr.grow(2.0).encloses(br):
			_flag(where, "the text %s is outside its plate %s" % [br, pr])
	state["frame"] = int(state.get("frame", 0)) + 1


func _run() -> void:
	Settings.set("auto_play", false)
	var out: String = String(_args.get("out", ""))
	if out != "":
		DirAccess.make_dir_recursive_absolute(out)
	var n_lines: int = int(String(_args.get("lines", "4")))
	var size_s: String = String(_args.get("size", ""))
	if size_s != "":
		var wh: PackedStringArray = size_s.split("x")
		get_tree().root.size = Vector2i(int(wh[0]), int(wh[1]))
		for i in 4:
			await get_tree().process_frame
	print("  canvas %s" % get_viewport().get_visible_rect().size)
	for spec: String in String(_args.get("shots", "")).split(",", false):
		var parts: PackedStringArray = spec.split(":")
		var scene_id: String = parts[0]
		var node_i: int = int(parts[1]) if parts.size() > 1 else 0
		var sc: Dictionary = SceneDataDB.get_scene(scene_id)
		if sc.is_empty():
			push_error("no scene %s" % scene_id)
			_bad += 1
			continue
		var eng: Node = ENGINE.instantiate()
		get_tree().root.add_child(eng)
		await get_tree().process_frame
		eng.call("start", int(sc.get("vol", 1)), scene_id, -1, max(node_i, 1))
		var dlg: Control = eng.get("_dlg")
		for k in n_lines:
			var where: String = "%s:%d+%d" % [scene_id, node_i, k]
			var state: Dictionary = {}
			var shot: bool = false
			var total: int = 0
			# through the typing, then a rested half second
			var rest: int = 0
			for f in 1500:
				await get_tree().process_frame
				if not dlg.visible or String(dlg.get("_full_text")) == "":
					continue
				if total == 0:
					total = int(dlg.call("_count_visible", String(dlg.get("_full_text"))))
					_lines += 1
				state["text"] = String(dlg.get("_full_text"))
				_check_frame(dlg, where, state)
				var typing: bool = bool(dlg.call("is_typing"))
				if out != "" and not shot and typing and int(dlg.get("_char_idx")) * 3 >= total:
					shot = true
					await RenderingServer.frame_post_draw
					get_viewport().get_texture().get_image().save_png("%s/%s__%d+%d_typing.png" % [out, scene_id, node_i, k])
				if not typing:
					rest += 1
					if rest > 30:
						break
			if out != "":
				await RenderingServer.frame_post_draw
				get_viewport().get_texture().get_image().save_png("%s/%s__%d+%d.png" % [out, scene_id, node_i, k])
			for tries in 40:
				var card: Control = eng.get("_interlude")
				if card != null and card.visible:
					card.call("try_advance")
				elif (eng.get("_choices") as Control).visible:
					(eng.get("_choices") as Control).call("_on_chosen", 0)
				else:
					eng.call("_advance")
				for i in 6:
					await get_tree().process_frame
				if String(dlg.get("_full_text")) != state.get("text", "") and dlg.visible and bool(dlg.call("is_typing")):
					break
		eng.queue_free()
		for i in 10:
			await get_tree().process_frame
	print("[VnTypeTest] %d line(s) · %d finding(s)" % [_lines, _bad])
	get_tree().quit(1 if _bad > 0 else 0)
