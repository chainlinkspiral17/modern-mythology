extends Node
## MENU FLOW PROBE (2026-11-10): the pause menu and the options, worked with
## a REAL mouse over a line of the story. The user: "making choices in the
## menu still breaks the game." (VnOptionsProbe called the open functions
## and emitted `pressed` itself: it could not see a panel that opens behind
## another, or a click that lands on the wrong one.)
##
##   godot --headless --path godot res://tools/VnMenuFlowProbe.tscn -- [--scene S --node N] [--out /abs/dir]
##
## MENU (the HUD's button) → SETTINGS → an option → ✕ → RESUME → a page turn.
## At each step: what is under the pointer is the thing being clicked, the
## panel on top is drawn on top, the story does not move under a menu, the
## game is paused while a menu is up and running after RESUME, and one click
## then turns exactly one page. Also: MENU → SETTINGS → Escape must not leave
## the options over a running story. Exit 1 on any ✗. Not HUD.

const ENGINE := preload("res://scenes/game/GameEngine.tscn")
var _args: Dictionary = {}
var _bad: int = 0
var _eng: Node = null
var _shot: int = 0


func _ready() -> void:
	var ua: PackedStringArray = OS.get_cmdline_user_args()
	for i in ua.size():
		if ua[i].begins_with("--"):
			_args[ua[i].trim_prefix("--")] = ua[i + 1] if i + 1 < ua.size() and not ua[i + 1].begins_with("--") else ""
	_run.call_deferred()


func _flag(what: String) -> void:
	_bad += 1
	print("  ✗ %s" % what)


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _snap(label: String) -> void:
	var out: String = String(_args.get("out", ""))
	if out == "":
		return
	DirAccess.make_dir_recursive_absolute(out)
	await RenderingServer.frame_post_draw
	_shot += 1
	get_viewport().get_texture().get_image().save_png("%s/%02d_%s.png" % [out, _shot, label])


func _find_button(root: Node, text: String) -> Button:
	for c in root.get_children():
		if c is Button and (c as Button).is_visible_in_tree() and (c as Button).text.strip_edges().to_upper() == text:
			return c
		var deeper: Button = _find_button(c, text)
		if deeper != null:
			return deeper
	return null


func _key(code: Key) -> void:
	for down: bool in [true, false]:
		var ev := InputEventKey.new()
		ev.keycode = code
		ev.physical_keycode = code
		ev.pressed = down
		Input.parse_input_event(ev)
		await _frames(2)


## Move the pointer onto `c` and click. Flags when something else is under it.
func _click(c: Control, what: String) -> void:
	var at: Vector2 = c.get_global_rect().get_center()
	var mv := InputEventMouseMotion.new()
	mv.position = at
	mv.global_position = at
	get_viewport().push_input(mv, true)
	await _frames(2)
	var hov: Control = get_viewport().gui_get_hovered_control()
	if hov != c and (hov == null or not c.is_ancestor_of(hov)):
		_flag("%s: under the pointer is %s, not the button" % [what, hov.get_path() if hov != null else NodePath("nothing")])
	for down: bool in [true, false]:
		var ev := InputEventMouseButton.new()
		ev.button_index = MOUSE_BUTTON_LEFT
		ev.pressed = down
		ev.position = at
		ev.global_position = at
		get_viewport().push_input(ev, true)
		await _frames(2)
	await _frames(4)


func _z(c: CanvasItem) -> int:
	var z: int = 0
	var n: Node = c
	while n != null and n is CanvasItem:
		z += (n as CanvasItem).z_index
		if not (n as CanvasItem).z_as_relative:
			break
		n = n.get_parent()
	return z


func _story() -> String:
	return "%s#%d" % [String(_eng.get("_scene_id")), int(_eng.get("_node_idx"))]


func _to_line() -> void:
	var dlg: Control = _eng.get("_dlg")
	for i in 600:
		await get_tree().process_frame
		if bool(_eng.get("_waiting")) and dlg.visible and String(dlg.get("_full_text")) != "":
			break
	dlg.call("finish_typing")
	await _frames(3)


func _run() -> void:
	var cfg_path: String = "user://settings.cfg"
	var saved: PackedByteArray = FileAccess.get_file_as_bytes(cfg_path)
	Settings.set("auto_play", false)
	Settings.set("auto_advance_ms", 0)
	var scene_id: String = String(_args.get("scene", "vol5_ch1_magician"))
	var node_i: int = int(String(_args.get("node", "19")))
	var sc: Dictionary = SceneDataDB.get_scene(scene_id)
	_eng = ENGINE.instantiate()
	get_tree().root.add_child(_eng)
	await get_tree().process_frame
	_eng.call("start", int(sc.get("vol", 1)), scene_id, -1, max(node_i, 1))
	await _to_line()
	var at: String = _story()
	var ig: Control = _eng.get("_ig_menu")
	var ov: Control = _eng.get("_settings_ov")
	var hud: Node = _eng.get("_hud")

	# ── 1. MENU → SETTINGS → an option → ✕ → RESUME → one page ──
	var menu_btn: Button = _find_button(hud, "MENU")
	if menu_btn == null:
		_flag("no MENU button on the HUD")
	else:
		await _click(menu_btn, "MENU")
	if not ig.visible or not bool(_eng.get("_paused")):
		_flag("MENU: the pause menu is %s and the game is %s" % ["up" if ig.visible else "not up", "paused" if bool(_eng.get("_paused")) else "running"])
	await _snap("pause_menu")
	var set_btn: Button = _find_button(ig, "SETTINGS")
	if set_btn != null:
		await _click(set_btn, "SETTINGS")
	if not ov.visible:
		_flag("SETTINGS: the options did not open")
	elif ig.visible and _z(ov) <= _z(ig):
		_flag("SETTINGS: the options are drawn UNDER the pause menu (z %d under %d) while taking its clicks" % [_z(ov), _z(ig)])
	await _snap("options")
	var opt: Button = _find_button(ov, "FAST")
	if opt == null:
		_flag("no FAST button in the options")
	else:
		await _click(opt, "TEXT SPEED · FAST")
		if Settings.text_speed != "fast":
			_flag("TEXT SPEED · FAST: the setting is still '%s'" % Settings.text_speed)
	if _story() != at:
		_flag("an option moved the story (%s → %s)" % [at, _story()])
	if not bool(_eng.get("_paused")):
		_flag("the game is running under the options")
	var close: Button = _find_button(ov, "✕")
	if close != null:
		await _click(close, "✕")
	if ov.visible:
		_flag("✕: the options are still up")
	if not ig.visible:
		_flag("✕: the pause menu is gone (nothing left to resume from)")
	var resume: Button = _find_button(ig, "RESUME GAME")
	if resume != null:
		await _click(resume, "RESUME GAME")
	if ig.visible or bool(_eng.get("_paused")):
		_flag("RESUME GAME: menu %s, game %s" % ["still up" if ig.visible else "closed", "still paused" if bool(_eng.get("_paused")) else "running"])
	if _story() != at:
		_flag("leaving the menu moved the story (%s → %s)" % [at, _story()])
	await _snap("resumed")
	var dlg: Control = _eng.get("_dlg")
	_eng.call("_advance")
	await _to_line()
	var after: String = _story()
	if after == at:
		_flag("after the menu the page does not turn")

	# ── 2. MENU → SETTINGS → Escape, Escape: back to the story, nothing left up ──
	at = _story()
	menu_btn = _find_button(hud, "MENU")
	if menu_btn != null:
		await _click(menu_btn, "MENU (2)")
	set_btn = _find_button(ig, "SETTINGS")
	if set_btn != null:
		await _click(set_btn, "SETTINGS (2)")
	await _key(KEY_ESCAPE)
	await _frames(4)
	if ov.visible and not ig.visible:
		_flag("Escape closed the pause menu and left the options up")
	if ov.visible and not bool(_eng.get("_paused")):
		_flag("Escape: the options are up over a RUNNING story")
	await _key(KEY_ESCAPE)
	await _frames(4)
	if ov.visible or ig.visible:
		_flag("after two Escapes a menu is still up (options %s, pause menu %s)" % [ov.visible, ig.visible])
	if bool(_eng.get("_paused")):
		_flag("after two Escapes the game is still paused")
	if _story() != at:
		_flag("Escape moved the story (%s → %s)" % [at, _story()])
	await _snap("after_escape")
	var f: FileAccess = FileAccess.open(cfg_path, FileAccess.WRITE)
	if f != null and saved.size() > 0:
		f.store_buffer(saved)
		f.close()
	print("[VnMenuFlowProbe] %d finding(s)" % _bad)
	get_tree().quit(1 if _bad > 0 else 0)
