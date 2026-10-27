extends Node
## VN LINE SHOT (2026-10-27): the visual novel at one line, as the Deck
## shows it — GameEngine started on a scene at a node (the save resume's
## fast-forward: bg, stage, shows, the last shot and mood re-asserted), run
## a moment, captured. For checking a reported frame without playing to it.
##
##   xvfb-run -a -s "-screen 0 1280x720x24" godot --path godot \
##     --rendering-driver opengl3 --resolution 1280x720 res://tools/VnLineShot.tscn -- \
##     --shots vol6_ch12_cosmic:70,vol5_ch6_lovers:12 --out /abs/dir [--wait 90] [--next 0]
##
## Writes <out>/<scene>__<node>.png (and __<node>+<k>.png for --next k: the
## lines after it, advanced as a reader would — auto-play is switched off).
## Not HUD; quits when done.

const ENGINE := preload("res://scenes/game/GameEngine.tscn")
var _args: Dictionary = {}


func _ready() -> void:
	var ua: PackedStringArray = OS.get_cmdline_user_args()
	for i in ua.size():
		if ua[i].begins_with("--"):
			_args[ua[i].trim_prefix("--")] = ua[i + 1] if i + 1 < ua.size() and not ua[i + 1].begins_with("--") else ""
	_run.call_deferred()


func _run() -> void:
	# a reader's pace: auto-play off, so the frame is the asked-for line
	Settings.set("auto_play", false)
	var out: String = String(_args.get("out", "/tmp/vnshot"))
	DirAccess.make_dir_recursive_absolute(out)
	var wait: int = int(String(_args.get("wait", "90")))
	var nxt: int = int(String(_args.get("next", "0")))
	for spec: String in String(_args.get("shots", "")).split(",", false):
		var parts: PackedStringArray = spec.split(":")
		var scene_id: String = parts[0]
		var node_i: int = int(parts[1]) if parts.size() > 1 else 0
		var sc: Dictionary = SceneDataDB.get_scene(scene_id)
		if sc.is_empty():
			push_error("no scene %s" % scene_id)
			continue
		var eng: Node = ENGINE.instantiate()
		get_tree().root.add_child(eng)
		await get_tree().process_frame
		eng.call("start", int(sc.get("vol", 1)), scene_id, -1, max(node_i, 1))
		for i in wait:
			await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s/%s__%d.png" % [out, scene_id, node_i])
		print("[VnLineShot] %s:%d" % [scene_id, node_i])
		for k in nxt:
			eng.call("_advance")
			await get_tree().process_frame
			eng.call("_advance")      # the first press finishes the typing, the second turns the line
			for i in wait:
				await get_tree().process_frame
			await RenderingServer.frame_post_draw
			get_viewport().get_texture().get_image().save_png("%s/%s__%d+%d.png" % [out, scene_id, node_i, k + 1])
		eng.queue_free()
		for i in 10:
			await get_tree().process_frame
	get_tree().quit(0)
