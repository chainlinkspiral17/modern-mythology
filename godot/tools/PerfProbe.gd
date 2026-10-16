extends SceneTree
## PERF PROBE (2026-10-14): what each locale costs the renderer, so passes
## that add detail (3D backgrounds, hero art, hero models) are measured
## against a budget instead of guessed. The user: "do a quick assessment how
## well game is handling graphical load … and how much it can be optimized/
## expanded with new content."
##
##   xvfb-run -a godot --rendering-driver opengl3 --resolution 1280x720 \
##     --path godot --script res://tools/PerfProbe.gd -- diner kwik_stop …
##
## Per locale: the scene's MeshInstance3D / light / shadowed-light counts,
## then the WORST of four 90-degree views from its first camera — draw calls,
## primitives, objects — plus video / texture / buffer memory. Counts are
## exact on any GPU; frame TIME on a software renderer means nothing, so
## measure fps on the Deck itself (Steam's performance overlay).
## (2026-10-16) waits for scripts/StaticMerge.gd to finish and reports it;
## MM_STATIC_MERGE=0 measures the unmerged room. PROBE_SHOTS=<dir> saves the
## first view of each room as <dir>/<room>.png (diff merged vs unmerged).
## Draft 2: run inside GameEngine (post stack, hero art, characters), and a
## budget gate (draw calls per view) for run_all_audits.
var rooms: Array = []
var i := -1
var node: Node = null
var cam: Camera3D = null
var frame := 0
var yaw := 0
var best: Dictionary = {}
var t0 := 0

func _initialize() -> void:
	rooms = OS.get_cmdline_user_args()
	_next()

func _count(n: Node, d: Dictionary) -> void:
	if n is MeshInstance3D:
		d["mesh"] = int(d.get("mesh", 0)) + 1
	if n is OmniLight3D or n is SpotLight3D:
		d["lights"] = int(d.get("lights", 0)) + 1
		if (n as Light3D).shadow_enabled and n.visible:
			d["shadow_lights"] = int(d.get("shadow_lights", 0)) + 1
	if n is DirectionalLight3D and (n as Light3D).shadow_enabled:
		d["sun_shadow"] = 1
	if n is GPUParticles3D or n is CPUParticles3D:
		d["particles"] = int(d.get("particles", 0)) + 1
	for c in n.get_children():
		_count(c, d)

func _next() -> void:
	if node != null:
		print("PROBE ", rooms[i], " ", JSON.stringify(best))
		node.queue_free()
		node = null
	i += 1
	if i >= rooms.size():
		quit(0)
		return
	var ps: PackedScene = load("res://scenes/locales/%s.tscn" % rooms[i])
	node = ps.instantiate()
	if OS.get_environment("PROBE_NO_LAMP_SHADOWS") == "1":     # A/B diagnosis
		for l in node.find_children("*", "Light3D", true, false):
			if not (l is DirectionalLight3D):
				(l as Light3D).shadow_enabled = false
	root.add_child(node)
	cam = null
	for c in node.find_children("*", "Camera3D", true, false):
		cam = c
		break
	if cam == null:
		cam = Camera3D.new()
		node.add_child(cam)
		cam.position = Vector3(0, 1.6, 0)
	cam.current = true
	best = {}
	var d := {}
	_count(node, d)
	best["scene"] = d
	frame = -1
	yaw = 0
	t0 = Time.get_ticks_usec()

func _process(_dt: float) -> bool:
	if node == null:
		return false
	if frame < 0:
		# let StaticMerge (two frames after _ready, then a few groups a frame)
		# finish before counting
		var sm: Node = node.get_node_or_null("StaticMerge")
		var busy: bool = sm != null and sm.is_processing()
		if busy and Time.get_ticks_usec() - t0 < 120000000:
			return false
		if sm == null and Time.get_ticks_usec() - t0 < 2000000:
			return false
		var rep: Variant = sm.get("_report") if sm != null else {}
		best["merge"] = rep
		frame = 0
		return false
	frame += 1
	if frame == 5 and yaw == 0 and OS.get_environment("PROBE_SHOTS") != "":
		var img: Image = root.get_viewport().get_texture().get_image()
		img.save_png(OS.get_environment("PROBE_SHOTS").path_join(String(rooms[i]) + ".png"))
	if frame % 6 == 5:
		var dc := RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME)
		var pr := RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_PRIMITIVES_IN_FRAME)
		var ob := RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_OBJECTS_IN_FRAME)
		if dc > int(best.get("draw", 0)):
			best["draw"] = dc
			best["prims"] = pr
			best["objects"] = ob
		best["vram_mb"] = snappedf(RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_VIDEO_MEM_USED) / 1048576.0, 0.1)
		best["tex_mb"] = snappedf(RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TEXTURE_MEM_USED) / 1048576.0, 0.1)
		best["buf_mb"] = snappedf(RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_BUFFER_MEM_USED) / 1048576.0, 0.1)
		cam.rotate_y(PI / 2.0)
		yaw += 1
		if yaw >= 4:
			best["load_and_4views_ms"] = (Time.get_ticks_usec() - t0) / 1000
			_next()
	return false
