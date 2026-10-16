extends Control
## Painted-room check (2026-10-02): a contact-sheet background frame
## through painted_scene.gdshader, a hero's composited __look_ frame
## over it — the two halves of the art style side by side. Needs a
## display (xvfb-run):
##
##   godot --path godot --rendering-driver opengl3 res://tools/PaintedBgTest.tscn -- \
##     --bg <frame.jpg> --hero <hero__look_cu_neutral.jpg> --out <file.png> [--paint 0]

func _ready() -> void:
	var args: Dictionary = {}
	var ua: PackedStringArray = OS.get_cmdline_user_args()
	for i in ua.size() - 1:
		if ua[i].begins_with("--"):
			args[ua[i].trim_prefix("--")] = ua[i + 1]
	var bg := TextureRect.new()
	bg.position = Vector2.ZERO
	bg.size = Vector2(1280, 720)
	bg.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	bg.stretch_mode = TextureRect.STRETCH_SCALE
	var bimg := Image.load_from_file(String(args.get("bg", "")))
	if bimg != null:
		bg.texture = ImageTexture.create_from_image(bimg)
	add_child(bg)
	# the painted pass reads the screen, exactly as in Background3D
	var bb := BackBufferCopy.new()
	bb.copy_mode = BackBufferCopy.COPY_MODE_VIEWPORT
	add_child(bb)
	var rect := ColorRect.new()
	rect.size = Vector2(1280, 720)
	var mat := ShaderMaterial.new()
	mat.shader = load("res://assets/shaders/painted_scene.gdshader")
	mat.set_shader_parameter("paint", float(String(args.get("paint", "1"))))
	# --set_<uniform> <value>: try a setting without editing the shader
	for k: String in args:
		if k.begins_with("set_"):
			mat.set_shader_parameter(k.trim_prefix("set_"), float(String(args[k])))
	rect.material = mat
	add_child(rect)
	var hp: String = String(args.get("hero", ""))
	if hp != "":
		var himg := Image.load_from_file(hp)
		if himg != null:
			var hr := TextureRect.new()
			hr.texture = ImageTexture.create_from_image(himg)
			hr.size = Vector2(675, 720)
			hr.position = Vector2(1280 - 675, 0)
			hr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
			hr.stretch_mode = TextureRect.STRETCH_SCALE
			# a raw (transparent) sheet portrait: give it the hero look live
			var pm := ShaderMaterial.new()
			pm.shader = load("res://assets/shaders/portrait_demon_static.gdshader")
			pm.set_shader_parameter("look", 1.0)
			pm.set_shader_parameter("look_sat", 1.12)
			pm.set_shader_parameter("look_contrast", 1.06)
			hr.material = pm
			add_child(hr)
	for i in 8:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(String(args.get("out", "/tmp/painted.png")))
	get_tree().quit(0)
