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
	# --cam "x,y,z,pitch_deg,yaw_deg,fov" (godot frame): try a vantage before
	# writing it into a preset or a marker (2026-10-31)
	var cam_s: String = String(args.get("cam", ""))
	if cam_s != "":
		var p: PackedFloat64Array = cam_s.split_floats(",")
		if p.size() >= 5:
			var cam: Camera3D = bg.get_node("SubViewport/Camera3D") as Camera3D
			cam.global_position = Vector3(p[0], p[1], p[2])
			cam.global_rotation = Vector3(deg_to_rad(p[3]), deg_to_rad(p[4]), 0.0)
			if p.size() >= 6:
				cam.fov = p[5]
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
	# (2026-11-02) --markers "a,b,c" --outdir /tmp/d: shoot every listed marker
	# in one launch, <outdir>/<marker>.png each (a preset loads once, not once
	# a marker: a survey of 269 inserts took a Godot start each)
	var mks: String = String(args.get("markers", ""))
	if mks != "":
		var outdir: String = String(args.get("outdir", "/tmp"))
		var cam2: Camera3D = bg.get_node("SubViewport/Camera3D") as Camera3D
		for mname: String in mks.split(","):
			var mm: Node3D = bg.call("find_shot_marker", mname)
			if mm == null:
				push_error("no marker " + mname)
				continue
			cam2.global_transform = mm.global_transform
			if mm.has_meta("fov"):
				cam2.fov = float(mm.get_meta("fov"))
			for i in 6:
				await get_tree().process_frame
			await RenderingServer.frame_post_draw
			var shot: Image = get_viewport().get_texture().get_image()
			shot.save_png(outdir.path_join(mname + ".png"))
			# (2026-11-08) --luma 1: the frame's brightness for dark_frame_sweep.py —
			# mean and 90th percentile of the clear top 69% (the text box covers
			# the rest), on a 160x90 copy so the read costs nothing
			if String(args.get("luma", "")) != "":
				print("LUMA %s %s" % [mname, _luma(shot)])
		get_tree().quit(0)
		return
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(String(args.get("out", "/tmp/trip.png")))
	get_tree().quit(0)


## "<mean> <p90>" of the top 69% of a frame's luminance, 0..255, read on
## a 160x90 copy (dark_frame_sweep.py ranks the cue frames by it).
func _luma(src: Image) -> String:
	var img: Image = src.duplicate() as Image
	img.resize(160, 90, Image.INTERPOLATE_BILINEAR)
	var rows: int = int(90.0 * 0.69)
	var hist: PackedInt32Array = PackedInt32Array()
	hist.resize(256)
	var total: float = 0.0
	var n: int = 0
	for y in range(rows):
		for x in range(160):
			var c: Color = img.get_pixel(x, y)
			var l: int = clampi(int(round((0.299 * c.r + 0.587 * c.g + 0.114 * c.b) * 255.0)), 0, 255)
			hist[l] += 1
			total += float(l)
			n += 1
	var acc: int = 0
	var p90: int = 0
	for i in range(256):
		acc += hist[i]
		if float(acc) >= float(n) * 0.9:
			p90 = i
			break
	return "%.1f %d" % [total / float(maxi(n, 1)), p90]
