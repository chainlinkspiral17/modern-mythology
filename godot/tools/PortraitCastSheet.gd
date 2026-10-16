extends Control
## PORTRAIT CAST SHEET (2026-10-13): the heroes as the VN shows them —
## two at a time in CharLayer's left / right cut-out slots over a locale,
## the dialogue band drawn in — so a cast pass judges what the player
## sees: do two people in a conversation share an eye line and a face
## size, does the light read the same on both, does either sit under the
## text. The user: "portraits need to be re-evaluated, lots don't line up
## right, lots look plain bad with lighting."
##
##   xvfb-run -a -s "-screen 0 1280x720x24" godot --path godot \
##     --rendering-driver opengl3 res://tools/PortraitCastSheet.tscn -- \
##     --out /abs/dir [--shots mcu,cu] [--lights warm,night,day] [--bg /abs/x.jpg]
##     [--heroes a,b] [--moods neutral,angry] [--guides]
##     [--rig key_yaw=-0.5,key_elev=0.3,fill_energy=0.5]   # Portrait3D.RIG trial values
##     [--look look_bleed=0,look_rim=0]                     # look trial values
##     [--clean]                                            # the painted look off
##     [--amount 0.6]                                       # the painted look's strength
##
## Writes <out>/pair_<shot>_<light>_<a>__<b>.png for consecutive pairs of
## every hero GLB on disk (the last pairs with the first), and
## <out>/_eyes.json: each hero's eye line and face height in screen pixels
## per shot — the numbers a framing fix is checked against.
##
## Not HUD: nothing here joins "ui"; the tool quits when it is done.

const PORTRAIT_SCENE := preload("res://scenes/vn/Portrait3D.tscn")
const P3D := preload("res://scripts/vn/Portrait3D.gd")
const ROOT := "res://assets/3d/characters/heroes/"
# CharLayer.POSITIONS / SPRITE_W / SPRITE_H (the cut-out slots)
const SLOT := {"left": Vector2(-70, 0), "right": Vector2(570, 0)}
const SPRITE := Vector2(780, 900)
# Background3D.get_scene_light-shaped rooms: a warm interior, a cool
# night exterior, an overcast day
const LIGHTS := {
	"warm":  {"key": Color(1.0, 0.82, 0.6), "ambient": Color(0.45, 0.38, 0.32), "level": 1.0},
	"night": {"key": Color(0.55, 0.66, 0.95), "ambient": Color(0.16, 0.18, 0.26), "level": 0.72},
	"day":   {"key": Color(0.96, 0.96, 0.92), "ambient": Color(0.55, 0.58, 0.62), "level": 1.2},
}

var _args: Dictionary = {}


func _ready() -> void:
	var ua: PackedStringArray = OS.get_cmdline_user_args()
	var i: int = 0
	while i < ua.size():
		var a: String = ua[i]
		if a.begins_with("--"):
			if i + 1 < ua.size() and not ua[i + 1].begins_with("--"):
				_args[a.substr(2)] = ua[i + 1]
				i += 2
				continue
			_args[a.substr(2)] = "1"
		i += 1
	_run.call_deferred()


func _heroes() -> Array[String]:
	var out: Array[String] = []
	var only: String = String(_args.get("heroes", ""))
	for f: String in DirAccess.get_files_at(ROOT):
		if not f.ends_with(".glb") or f.get_basename().ends_with("_gnm"):
			continue
		if only != "" and not (f.get_basename() in only.split(",")):
			continue
		out.append(f.get_basename())
	out.sort()
	return out


func _portrait(hero: String, slot: String) -> SubViewportContainer:
	var holder := Control.new()
	holder.position = SLOT[slot]
	holder.size = SPRITE
	holder.clip_contents = true
	add_child(holder)
	var p: SubViewportContainer = PORTRAIT_SCENE.instantiate() as SubViewportContainer
	holder.add_child(p)
	p.position = Vector2.ZERO
	p.size = SPRITE
	var lo: Dictionary = {}
	for pair: String in String(_args.get("look", "")).split(",", false):
		var kv: PackedStringArray = pair.split("=")
		if kv.size() == 2:
			lo[kv[0].strip_edges()] = float(kv[1])
	var so: Dictionary = {}
	if not lo.is_empty():
		var lk: Dictionary = (P3D.SHADING_DEFAULT["look"] as Dictionary).duplicate()
		lk.merge(lo, true)
		so["look"] = lk
	if _args.has("amount"):
		so["look_amount"] = float(String(_args["amount"]))
	if not so.is_empty():
		p.set("shading_override", so)
	if slot == "left":
		# CharLayer mirrors the left slot so both face the centre
		p.scale = Vector2(-1, 1)
		p.position = Vector2(SPRITE.x, 0)
	if _args.has("clean"):
		p.call("set_look_enabled", false)
	if not bool(p.call("load_character", ROOT + hero + ".glb", "neutral")):
		holder.queue_free()
		return null
	return p


func _band() -> Control:
	# DialogueBox's box: the lower 44 % of the screen (its band fades in above)
	var c := ColorRect.new()
	c.color = Color(0.03, 0.03, 0.05, 0.55)
	c.position = Vector2(0, 403)
	c.size = Vector2(1280, 317)
	return c


func _rig_override() -> Dictionary:
	var o: Dictionary = {}
	for pair: String in String(_args.get("rig", "")).split(",", false):
		var kv: PackedStringArray = pair.split("=")
		if kv.size() == 2:
			o[kv[0].strip_edges()] = float(kv[1])
	return o


## --guides: the box's top (where the reading band starts) and each
## figure's measured eye line, so a framing pass reads in pixels.
func _guides(pa: SubViewportContainer, pb: SubViewportContainer) -> Control:
	var g := Control.new()
	g.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var box := ColorRect.new()
	box.color = Color(1, 0.3, 0.3, 0.8)
	box.position = Vector2(0, 403)
	box.size = Vector2(1280, 2)
	g.add_child(box)
	for pair: Array in [[pa, "left"], [pb, "right"]]:
		var pv: SubViewportContainer = pair[0]
		if pv == null or not pv.has_method("frame_report"):
			continue
		var rep: Dictionary = pv.call("frame_report")
		if rep.is_empty():
			continue
		var y: float = float(rep["eye"]) * SPRITE.y
		var ln := ColorRect.new()
		ln.color = Color(0.3, 1, 0.5, 0.8)
		var x0: float = 0.0 if String(pair[1]) == "left" else 640.0
		ln.position = Vector2(x0 + 60.0, y)
		ln.size = Vector2(520, 2)
		g.add_child(ln)
	return g


func _run() -> void:
	var out: String = String(_args.get("out", "/tmp/castsheet"))
	var ro: Dictionary = _rig_override()
	if not ro.is_empty():
		P3D.rig_override = ro
	DirAccess.make_dir_recursive_absolute(out)
	var shots: PackedStringArray = String(_args.get("shots", "mcu,cu")).split(",")
	var lights: PackedStringArray = String(_args.get("lights", "warm")).split(",")
	var moods: PackedStringArray = String(_args.get("moods", "neutral")).split(",")
	var bg := TextureRect.new()
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	bg.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	var bg_path: String = String(_args.get("bg", ""))
	if bg_path != "" and FileAccess.file_exists(bg_path):
		var img := Image.load_from_file(bg_path)
		if img != null:
			bg.texture = ImageTexture.create_from_image(img)
	else:
		var solid := ColorRect.new()
		solid.color = Color(0.30, 0.27, 0.24)
		solid.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		add_child(solid)
	add_child(bg)
	# As the engine does (VNTypeSpecimen): the trip runs on the background
	# texture only and the global screen layer steps aside — without this
	# every figure wore the trip's edge glow (a yellow-green halo that is
	# not in the game)
	add_to_group("trip_local")
	var trip: Node = get_node_or_null("/root/TripSync")
	if trip != null and trip.has_method("attach") and bg.texture != null:
		trip.call("attach", bg)
	var heroes: Array[String] = _heroes()
	var eyes: Dictionary = {}
	for k in heroes.size():
		var a: String = heroes[k]
		var b: String = heroes[(k + 1) % heroes.size()]
		var pa: SubViewportContainer = _portrait(a, "left")
		var pb: SubViewportContainer = _portrait(b, "right")
		var band: Control = _band()
		add_child(band)
		for shot: String in shots:
			for ln: String in lights:
				for md: String in moods:
					var light: Dictionary = LIGHTS.get(ln, LIGHTS["warm"])
					for pv: SubViewportContainer in [pa, pb]:
						if pv == null:
							continue
						pv.call("set_scene_light", light)
						pv.call("set_shot", shot, "eye", 7)
						pv.call("set_expression", md)
					for f in 40:
						await get_tree().process_frame
					for pv: SubViewportContainer in [pa, pb]:
						if pv != null:
							pv.call("snap_look")
					var gd: Control = null
					if _args.has("guides"):
						gd = _guides(pa, pb)
						add_child(gd)
					await get_tree().process_frame
					await RenderingServer.frame_post_draw
					var shot_img: Image = get_viewport().get_texture().get_image()
					var tag: String = ln if md == "neutral" else ln + "_" + md
					shot_img.save_png("%s/pair_%s_%s_%s__%s.png" % [out, shot, tag, a, b])
					print("[PortraitCastSheet] %s %s %s + %s" % [shot, tag, a, b])
					if gd != null:
						gd.queue_free()
			if pa != null and pa.has_method("frame_report"):
				var rep: Dictionary = pa.call("frame_report")
				if not eyes.has(a):
					eyes[a] = {}
				var ea: Dictionary = eyes[a]
				ea[shot] = rep
		for pv: SubViewportContainer in [pa, pb]:
			if pv != null:
				pv.get_parent().queue_free()
		band.queue_free()
		await get_tree().process_frame
	var fa := FileAccess.open(out + "/_eyes.json", FileAccess.WRITE)
	if fa != null:
		fa.store_string(JSON.stringify(eyes, "  "))
		fa.close()
	get_tree().quit(0)
