extends Node
## SCREEN PROBE (2026-11-09): the real Main scene, a SCREEN SIZE picked as
## the Settings overlay picks it, then a chapter started as the menu starts
## it — the window, the canvas and the 3D set's render size printed at each
## step. For "the ultrawide setting isn't taking".
##
##   xvfb-run -a -s "-screen 0 3440x1440x24" godot --path godot \
##     res://tools/ScreenProbe.tscn -- --mode ultrawide --scene vol6_ch7_hospital --out /abs/dir

const MAIN := preload("res://scenes/Main.tscn")
var _args: Dictionary = {}


func _ready() -> void:
	var ua: PackedStringArray = OS.get_cmdline_user_args()
	for i in ua.size():
		if ua[i].begins_with("--"):
			_args[ua[i].trim_prefix("--")] = ua[i + 1] if i + 1 < ua.size() and not ua[i + 1].begins_with("--") else ""
	_run.call_deferred()


func _report(tag: String) -> void:
	var root: Window = get_tree().root
	var line: String = "[probe] %-14s window %s mode %d · root.size %s · canvas %s · aspect %d · screen %s" % [
		tag, DisplayServer.window_get_size(), DisplayServer.window_get_mode(), root.size,
		root.get_visible_rect().size, root.content_scale_aspect, DisplayServer.screen_get_size()]
	print(line)
	for n: Node in root.find_children("*", "SubViewportContainer", true, false):
		var c: SubViewportContainer = n as SubViewportContainer
		if not c.is_visible_in_tree():
			continue
		for ch: Node in c.get_children():
			if ch is SubViewport:
				print("[probe]    %s size %s scale %s · viewport %s x%.2f" % [c.name, c.size, c.scale, (ch as SubViewport).size, (ch as SubViewport).scaling_3d_scale])


func _shot(name: String) -> void:
	var out: String = String(_args.get("out", ""))
	if out == "":
		return
	await RenderingServer.frame_post_draw
	# the SCREEN as the player sees it (the X root), not the game's own
	# viewport: a window the game has lost track of shows only here
	if OS.execute("import", ["-window", "root", "%s/%s.png" % [out, name]]) != 0:
		get_viewport().get_texture().get_image().save_png("%s/%s.png" % [out, name])


func _run() -> void:
	Settings.set("auto_play", false)
	var main: Node = MAIN.instantiate()
	get_tree().root.add_child(main)
	for i in 30:
		await get_tree().process_frame
	_report("menu")
	Settings.window_mode = String(_args.get("mode", "ultrawide"))
	for i in 30:
		await get_tree().process_frame
	_report("menu+mode")
	await _shot("menu")
	var scene_id: String = String(_args.get("scene", "vol6_ch7_hospital"))
	var sc: Dictionary = SceneDataDB.get_scene(scene_id)
	main.call("_on_play_requested", int(sc.get("vol", 1)), scene_id, 1)
	for k in 4:
		for i in 40:
			await get_tree().process_frame
		_report("scene+%d" % ((k + 1) * 40))
	await _shot("scene")
	get_tree().quit()
