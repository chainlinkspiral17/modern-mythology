extends Control
## Portrait look check (2026-10-01): a hero over a locale frame, the
## shot sizes and moods, captured from the WINDOW (the container's look
## shader included — the contact sheet saves the raw viewport, which
## never shows it). Needs a display (xvfb-run on a server):
##
##   godot --path godot --rendering-driver opengl3 res://tools/PortraitLookTest.tscn -- \
##     --hero john_frank --bg qa/contact/diner_interior/x.jpg --out /tmp/look
##
## Writes <out>/<hero>__<shot>__<mood>__<look|clean>.png.

const PORTRAIT_SCENE := preload("res://scenes/vn/Portrait3D.tscn")

var _args: Dictionary = {}


func _ready() -> void:
	for a: String in OS.get_cmdline_user_args():
		if a.begins_with("--"):
			_args[a.trim_prefix("--")] = ""
	var ua: PackedStringArray = OS.get_cmdline_user_args()
	for i in ua.size() - 1:
		if ua[i].begins_with("--"):
			_args[ua[i].trim_prefix("--")] = ua[i + 1]
	_run.call_deferred()


func _run() -> void:
	var hero: String = String(_args.get("hero", "john_frank"))
	var out: String = String(_args.get("out", "/tmp/look"))
	DirAccess.make_dir_recursive_absolute(out)
	var bg := TextureRect.new()
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	bg.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	var bg_path: String = String(_args.get("bg", ""))
	if bg_path != "":
		var img := Image.load_from_file(bg_path)
		if img != null:
			bg.texture = ImageTexture.create_from_image(img)
	add_child(bg)
	var p: SubViewportContainer = PORTRAIT_SCENE.instantiate() as SubViewportContainer
	add_child(p)
	# CharLayer's right slot, cut-out size (780 × 900 from x 570)
	p.position = Vector2(570, 0)
	p.size = Vector2(780, 900)
	var ok: bool = bool(p.call("load_character", "res://assets/3d/characters/heroes/%s.glb" % hero, "neutral"))
	if not ok:
		push_error("could not load %s" % hero)
		get_tree().quit(1)
		return
	# a warm diner key, as Background3D.get_scene_light would give
	p.call("set_scene_light", {"key": Color(1.0, 0.82, 0.6), "ambient": Color(0.45, 0.38, 0.32), "level": 1.0})
	for shot: String in ["mcu", "cu", "ecu"]:
		for mood: String in ["neutral", "sad", "angry"]:
			p.call("set_shot", shot, "eye", 7)
			p.call("set_expression", mood)
			for look: bool in [true, false]:
				p.call("set_look_enabled", look)
				for i in 40:
					await get_tree().process_frame
				await RenderingServer.frame_post_draw
				var img: Image = get_viewport().get_texture().get_image()
				img.save_png("%s/%s__%s__%s__%s.png" % [out, hero, shot, mood, "look" if look else "clean"])
	get_tree().quit(0)
