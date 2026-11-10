extends Node
## OPTIONS PROBE (2026-11-10): the options menu opened over a line of the
## story and EVERY choice in it pressed. The user: "making choices in the
## menu still breaks the game."
##
##   godot --headless --path godot res://tools/VnOptionsProbe.tscn -- \
##     [--scene vol5_ch1_magician --node 19]
##
## After each press it checks the story under the menu: the same line, still
## whole on screen in a live text box, the game still paused, the menu still
## up. Then it closes the menu, resumes and turns the page, and the next line
## must appear. Restores the settings it found. Exit 1 on any ✗. Not HUD.

const ENGINE := preload("res://scenes/game/GameEngine.tscn")
var _args: Dictionary = {}
var _bad: int = 0


func _ready() -> void:
	var ua: PackedStringArray = OS.get_cmdline_user_args()
	for i in ua.size():
		if ua[i].begins_with("--"):
			_args[ua[i].trim_prefix("--")] = ua[i + 1] if i + 1 < ua.size() and not ua[i + 1].begins_with("--") else ""
	_run.call_deferred()


func _flag(what: String) -> void:
	_bad += 1
	print("  ✗ %s" % what)


func _walk(n: Node, out: Array) -> void:
	for c in n.get_children():
		if c is Button or c is Slider:
			out.append(c)
		_walk(c, out)


func _label_of(c: Control) -> String:
	# the row label above a button row / slider
	var row: Node = c.get_parent()
	var holder: Node = row.get_parent() if row != null else null
	var name_s: String = ""
	if holder != null:
		var idx: int = row.get_index()
		for j in range(idx - 1, -1, -1):
			var prev: Node = holder.get_child(j)
			if prev is Label:
				name_s = (prev as Label).text
				break
	if name_s == "" and row != null:
		for sib in row.get_children():
			if sib is Label:
				name_s = (sib as Label).text
				break
	return name_s.left(34)


func _check(eng: Node, what: String, line: String, node_idx: int) -> void:
	var dlg: Control = eng.get("_dlg")
	var body: RichTextLabel = dlg.get("_body")
	var ov: Control = eng.get("_settings_ov")
	if body == null or not is_instance_valid(body) or body.is_queued_for_deletion():
		_flag("%s → the text box has no body" % what)
		return
	if String(dlg.get("_full_text")) != line:
		_flag("%s → the line changed under the menu" % what)
	elif body.text != line or (body.visible_characters != -1 and not bool(dlg.call("is_typing"))):
		_flag("%s → the line is gone from the screen (body holds %d of %d characters, %d shown)" % [
			what, body.text.length(), line.length(), body.visible_characters])
	elif float(body.get_content_height()) > body.size.y + 1.5:
		_flag("%s → the line no longer fits its box (%.0f px of text in %.0f)" % [
			what, float(body.get_content_height()), body.size.y])
	if int(eng.get("_node_idx")) != node_idx:
		_flag("%s → the story moved under the menu (node %d → %d)" % [what, node_idx, int(eng.get("_node_idx"))])
	if not bool(eng.get("_paused")):
		_flag("%s → the game is no longer paused" % what)
	if not ov.visible:
		_flag("%s → the options closed themselves" % what)


func _run() -> void:
	var cfg_path: String = "user://settings.cfg"
	var saved: PackedByteArray = FileAccess.get_file_as_bytes(cfg_path)
	Settings.set("auto_play", false)
	Settings.set("auto_advance_ms", 0)
	var scene_id: String = String(_args.get("scene", "vol5_ch1_magician"))
	var node_i: int = int(String(_args.get("node", "19")))
	var sc: Dictionary = SceneDataDB.get_scene(scene_id)
	var eng: Node = ENGINE.instantiate()
	get_tree().root.add_child(eng)
	await get_tree().process_frame
	eng.call("start", int(sc.get("vol", 1)), scene_id, -1, max(node_i, 1))
	var dlg: Control = eng.get("_dlg")
	for i in 600:
		await get_tree().process_frame
		if bool(eng.get("_waiting")) and dlg.visible and String(dlg.get("_full_text")) != "":
			break
	dlg.call("finish_typing")
	await get_tree().process_frame
	var line: String = String(dlg.get("_full_text"))
	var node_idx: int = int(eng.get("_node_idx"))
	print("  the line: '%s…' (node %d)" % [line.left(48), node_idx - 1])
	eng.call("_open_in_game_menu")
	eng.call("_open_settings")
	for i in 5:
		await get_tree().process_frame
	var ov: Control = eng.get("_settings_ov")
	var ctrls: Array = []
	_walk(ov, ctrls)
	var pressed: int = 0
	for i in ctrls.size():
		# the overlay may rebuild itself: walk it again and take the i-th
		var now: Array = []
		_walk(ov, now)
		if i >= now.size():
			break
		var c: Control = now[i]
		var what: String = ""
		if c is Button:
			var b: Button = c
			if b.text == "✕" or b.text.to_upper() == "CLOSE":
				continue
			what = "%s · %s" % [_label_of(b), b.text]
			b.pressed.emit()
		else:
			var s: Slider = c
			what = "%s · slider" % _label_of(s)
			var keep: float = s.value
			s.value = s.min_value + (s.max_value - s.min_value) * 0.37
			await get_tree().process_frame
			s.value = keep
		pressed += 1
		for f in 6:
			await get_tree().process_frame
		_check(eng, what, line, node_idx)
	# back to the story
	ov.visible = false
	eng.call("_resume_from_menu")
	for i in 5:
		await get_tree().process_frame
	eng.call("_advance")
	for i in 30:
		await get_tree().process_frame
	var next_line: String = String(dlg.get("_full_text"))
	var body: RichTextLabel = dlg.get("_body")
	if next_line == line or next_line == "" or body.text != next_line:
		_flag("after the menu the page did not turn to a new line (line '%s', body '%s')" % [next_line.left(30), body.text.left(30)])
	# put the settings back as they were
	var f: FileAccess = FileAccess.open(cfg_path, FileAccess.WRITE)
	if f != null and saved.size() > 0:
		f.store_buffer(saved)
		f.close()
	print("[VnOptionsProbe] %d option(s) pressed · %d finding(s)" % [pressed, _bad])
	get_tree().quit(1 if _bad > 0 else 0)
