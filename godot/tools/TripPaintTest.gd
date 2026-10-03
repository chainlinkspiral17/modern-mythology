extends Control
## The painted room WITH the register's trip (2026-10-02): Background3D
## on a preset, TripSync attached under the painter (as GameEngine does)
## with a fixed, lively music state, captured. --inked sets the aura's
## paint_under (0 = the raw glow, 0.85 = the game); --paint 0 unpaints.
##
##   godot --path godot --rendering-driver opengl3 res://tools/TripPaintTest.tscn -- \
##     --preset diner_interior --vol 5 --out /tmp/x.png [--inked 0.85] [--paint 0]
##     [--trip 0 : no trip at all] [--energy 0.22 : a quiet verse instead of a loud beat]
##     [--marker shot_insert_door : shoot from that [shot:] marker instead of the preset]

const BG_SCENE := preload("res://scenes/vn/Background3D.tscn")

func _ready() -> void:
	var args: Dictionary = {}
	var ua: PackedStringArray = OS.get_cmdline_user_args()
	for i in ua.size() - 1:
		if ua[i].begins_with("--"):
			args[ua[i].trim_prefix("--")] = ua[i + 1]
	var bg: SubViewportContainer = BG_SCENE.instantiate() as SubViewportContainer
	add_child(bg)
	bg.position = Vector2.ZERO
	bg.size = Vector2(1280, 720)
	var vol: int = int(String(args.get("vol", "5")))
	bg.call("set_paper_for_volume", vol)
	bg.call("set_paint", float(String(args.get("paint", "1"))))
	var ok: bool = bool(bg.call("load_location", String(args.get("preset", "diner_interior"))))
	if not ok:
		push_error("preset did not load")
		get_tree().quit(1)
		return
	# --mood night: the scene's [mood:] directive, as GameEngine would apply it
	var mood: String = String(args.get("mood", ""))
	if mood != "":
		for i in 3:
			await get_tree().process_frame     # the locale's PostProcess _ready first
		var mc: Node = bg.call("get_locale_mood_cycler")
		if mc != null and mc.has_method("apply_style_or_mood"):
			mc.call("apply_style_or_mood", mood)
	# --marker shot_insert_door: shoot from one of the locale's [shot:] markers
	var mk: String = String(args.get("marker", ""))
	if mk != "":
		var m: Node3D = bg.call("find_shot_marker", mk)
		var cam: Camera3D = bg.get_node("SubViewport/Camera3D") as Camera3D
		if m == null:
			push_error("no marker " + mk)
			get_tree().quit(1)
			return
		cam.global_transform = m.global_transform
		if m.has_meta("fov"):
			cam.fov = float(m.get_meta("fov"))
	# --yaw_deg 3: turn the view a little (does the paper travel with the room?)
	var yaw: float = float(String(args.get("yaw_deg", "0")))
	if yaw != 0.0:
		var cam: Camera3D = bg.get_node("SubViewport/Camera3D") as Camera3D
		cam.rotation.y += deg_to_rad(yaw)
	var trip: Node = get_node_or_null("/root/TripSync")
	var mat: ShaderMaterial = null
	if String(args.get("trip", "1")) == "0":
		trip = null                      # --trip 0: the painted room alone
	var inked: float = float(String(args.get("inked", "0.85")))
	if trip != null:
		trip.call("push_register", String(trip.call("register_for_volume", vol)), self)
		mat = trip.call("attach", bg)
		mat.set_shader_parameter("paint_under", inked)
		# the TRAIL rig, mounted as GameEngine mounts it (2026-10-02: the
		# stills without it "looked to fix this; in action, still terrible")
		# --trails 0 leaves it off; --trails_paint 0 runs it as before the
		# painted scale (the game as the Deck saw it)
		if String(args.get("trails", "1")) != "0" and trip.has_method("attach_feedback"):
			var fb: Control = trip.call("attach_feedback", bg) as Control
			if fb != null:
				fb.z_index = 10
				add_child(fb)
				trip.call("add_feedback_source", fb, bg)
			if String(args.get("trails_paint", "1")) != "0":
				trip.set("paint_under_3d", inked)
	for i in 90:
		await get_tree().process_frame     # the register fade completes, the trail accumulates
	# a lively bar, held still: the aura at its brightest, a beat just landed
	if trip != null and mat != null:
		trip.set_process(false)
		# --energy 0.7 (default): a loud bar with a beat just landed;
		# --energy 0.22: a quiet verse, the usual moment
		var en: float = float(String(args.get("energy", "0.7")))
		trip.set("energy", en)
		trip.set("bass", en * 0.85)
		trip.set("mid", en * 0.7)
		trip.set("high", en * 0.55)
		trip.set("pulse", 0.6 if en > 0.5 else 0.0)
		trip.set("ring_t", 0.25 if en > 0.5 else 10.0)
		trip.call("_push_to", mat)
		trip.call("_push_register_to", mat)
		mat.set_shader_parameter("paint_under", inked)
	for i in 4:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(String(args.get("out", "/tmp/trip.png")))
	get_tree().quit(0)
