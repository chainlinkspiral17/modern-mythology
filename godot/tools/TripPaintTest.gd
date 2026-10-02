extends Control
## The painted room WITH the register's trip (2026-10-02): Background3D
## on a preset, TripSync attached under the painter (as GameEngine does)
## with a fixed, lively music state, captured. --inked sets the aura's
## paint_under (0 = the raw glow, 0.85 = the game); --paint 0 unpaints.
##
##   godot --path godot --rendering-driver opengl3 res://tools/TripPaintTest.tscn -- \
##     --preset diner_interior --vol 5 --out /tmp/x.png [--inked 0.85] [--paint 0]

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
	var trip: Node = get_node_or_null("/root/TripSync")
	var mat: ShaderMaterial = null
	if trip != null:
		trip.call("push_register", String(trip.call("register_for_volume", vol)), self)
		mat = trip.call("attach", bg)
	for i in 90:
		await get_tree().process_frame     # the register fade completes
	# a lively bar, held still: the aura at its brightest, a beat just landed
	if trip != null and mat != null:
		trip.set_process(false)
		trip.set("energy", 0.7)
		trip.set("bass", 0.6)
		trip.set("mid", 0.5)
		trip.set("high", 0.4)
		trip.set("pulse", 0.6)
		trip.set("ring_t", 0.25)
		trip.call("_push_to", mat)
		trip.call("_push_register_to", mat)
		mat.set_shader_parameter("paint_under", float(String(args.get("inked", "0.85"))))
	for i in 4:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(String(args.get("out", "/tmp/trip.png")))
	get_tree().quit(0)
