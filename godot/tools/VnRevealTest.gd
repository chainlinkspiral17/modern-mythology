extends Node
## REVEAL TEST (2026-11-10): the typing compared PIXEL BY PIXEL with the
## finished line. The user, after a first fix: "That wasn't what caused my
## glitch. Keep digging. It types outside the box and then moved the too
## long word to the next line."
##
##   xvfb-run -a -s "-screen 0 1720x720x24" godot --path godot \
##     --rendering-driver opengl3 res://tools/VnRevealTest.tscn -- [--out /abs/dir]
##
## The text box alone on black, each test line typed at every column the
## game uses (centred, text on the left, text on the right). On EVERY frame:
## every lit pixel of the typing must be a lit pixel of the finished line (a
## word that sits on one line and later moves to the next lights pixels the
## finished line does not have), and every lit pixel must be inside the
## plate once the plate has settled. Exit 1 on any finding. Not HUD.

const DLG := preload("res://scenes/game/DialogueBox.tscn")
const LINES := [
	"Frasier moved through it — lanky silhouette against the gloom. His bomber jacket draped over a t-shirt bearing the faded logo of some defunct tech collective the rest of the world had forgotten.",
	"His steps echoed — a chaotic rhythm on the stained concrete. The controlled stumble that was his signature. Architect of decay and possibility. The mad scientist in his Southern Gothic laboratory, cobbling life together from discarded bits.",
	"The city hummed back — a low thrum of potential and decay, indistinguishable from the warehouse's own electrical complaints. And Frasier had long ago stopped trying to tell the difference.",
	"\"Subject proximate. John Frank. Probability of existential navel-gazing: ninety-three point seven percent.\"",
]
var _args: Dictionary = {}
var _bad: int = 0


func _ready() -> void:
	var ua: PackedStringArray = OS.get_cmdline_user_args()
	for i in ua.size():
		if ua[i].begins_with("--"):
			_args[ua[i].trim_prefix("--")] = ua[i + 1] if i + 1 < ua.size() and not ua[i + 1].begins_with("--") else ""
	_run.call_deferred()


func _lit(img: Image) -> PackedByteArray:
	# 1 where the frame is lit like text (the plate over black is dark)
	var w: int = img.get_width()
	var h: int = img.get_height()
	var out := PackedByteArray()
	out.resize(w * h)
	var data: PackedByteArray = img.get_data()      # RGBA8
	for i in w * h:
		var o: int = i * 4
		out[i] = 1 if (int(data[o]) + int(data[o + 1]) + int(data[o + 2])) > 330 else 0
	return out


func _grab() -> Image:
	await RenderingServer.frame_post_draw
	var img: Image = get_viewport().get_texture().get_image()
	img.convert(Image.FORMAT_RGBA8)
	return img


## --engine scene:node --lines N: the same comparison on the REAL flow — the
## engine reading a scene (its speakers, portraits' slots, shots and page
## turns), with the set and the portraits hidden so a lit pixel is text.
func _run_engine(spec: String, n_lines: int, out: String) -> void:
	var parts: PackedStringArray = spec.split(":")
	var scene_id: String = parts[0]
	var node_i: int = int(parts[1]) if parts.size() > 1 else 1
	var sc: Dictionary = SceneDataDB.get_scene(scene_id)
	var eng: Node = load("res://scenes/game/GameEngine.tscn").instantiate()
	get_tree().root.add_child(eng)
	await get_tree().process_frame
	eng.call("start", int(sc.get("vol", 1)), scene_id, -1, max(node_i, 1))
	var dlg: Control = eng.get("_dlg")
	# the window settles (fullscreen is granted a few frames in) before anything is measured
	for i in 90:
		await get_tree().process_frame
	var size: Vector2i = get_viewport().get_texture().get_size()
	var w: int = size.x
	var sx: float = float(size.x) / get_viewport().get_visible_rect().size.x
	print("  frame %s · canvas %s · Godot %s" % [size, get_viewport().get_visible_rect().size, Engine.get_version_info()["string"]])
	var done: int = 0
	var last_text: String = ""
	var guard: int = 0
	while done < n_lines and guard < 20000:
		guard += 1
		await get_tree().process_frame
		# a black stage: the set, the cast and the HUD out of the picture
		for nm: String in ["_bg_3d_node", "_bg", "_chars", "_hud", "_bg_composition", "_substrate"]:
			var nd: Variant = eng.get(nm)
			if nd != null and is_instance_valid(nd) and nd is CanvasItem:
				(nd as CanvasItem).modulate.a = 0.0
				if nm == "_chars":
					(nd as CanvasItem).visible = false      # its own tweens write modulate (the insert step-back)
		var card: Control = eng.get("_interlude")
		if card != null and card.visible:
			card.call("try_advance")
			continue
		if (eng.get("_choices") as Control).visible:
			(eng.get("_choices") as Control).call("_on_chosen", 0)
			continue
		var text: String = String(dlg.get("_full_text"))
		if not dlg.visible or text == "" or text == last_text or not bool(dlg.call("is_typing")):
			if bool(eng.get("_waiting")) and not bool(dlg.call("is_typing")):
				last_text = text          # a line already at rest: turn the page
				eng.call("_advance")
			continue
		last_text = text
		var frames: Array = []
		var plates: Array = []
		while bool(dlg.call("is_typing")) and frames.size() < 3000:
			var gi: Image = await _grab()
			frames.append(_lit(gi))
			plates.append((dlg.get("_plate") as Control).get_global_rect())
			if out != "" and done == int(String(_args.get("dump", "0"))) and frames.size() % 5 == 0:
				gi.save_png("%s/eng_%03d.png" % [out, frames.size()])
		for i in 25:
			await get_tree().process_frame
		var fin_img: Image = await _grab()
		var fin: PackedByteArray = _lit(fin_img)
		if fin_img.get_width() != w or (frames.size() > 0 and (frames[0] as PackedByteArray).size() != fin.size()):
			print("  -- %s: the window changed size during this line; not compared" % text.left(28))
			size = get_viewport().get_texture().get_size()
			w = size.x
			sx = float(size.x) / get_viewport().get_visible_rect().size.x
			done += 1
			continue
		if out != "" and done == int(String(_args.get("dump", "0"))):
			fin_img.save_png("%s/eng_final.png" % out)
		var moved: int = 0
		var outside_n: int = 0
		var first_bad: int = -1
		for fi in range(2, frames.size() - 1):          # frame 0-1: the name plate pops; the last: the cursor
			var f: PackedByteArray = frames[fi]
			var stray: int = 0
			var outside: int = 0
			var pr: Rect2 = plates[fi]
			for i in f.size():
				if f[i] == 1:
					if fin[i] == 0:
						stray += 1
					if fi > 20:
						var x: float = float(i % w) / sx
						var y: float = float(i / w) / sx
						if x < pr.position.x - 1.0 or x > pr.end.x + 1.0 or y < pr.position.y - 1.0 or y > pr.end.y + 1.0:
							outside += 1
			if stray > 12:
				moved += 1
				if first_bad < 0:
					first_bad = fi
			if outside > 12:
				outside_n += 1
		done += 1
		var where: String = "%s#%d '%s…'" % [String(eng.get("_scene_id")), int(eng.get("_node_idx")) - 1, text.left(28)]
		if moved > 0 or outside_n > 0:
			_bad += 1
			print("  ✗ %s: %d of %d typing frames differ from the finished line (first at %d), %d with text outside the plate" % [where, moved, frames.size(), first_bad, outside_n])
		else:
			print("  ok %s: %d typing frames" % [where, frames.size()])
	eng.queue_free()


func _run() -> void:
	if String(_args.get("engine", "")) != "":
		Settings.set("auto_play", false)
		var trip0: float = Settings.trip_amount
		Settings.trip_amount = 0.0
		await _run_engine(String(_args.get("engine", "")), int(String(_args.get("lines", "8"))), String(_args.get("out", "")))
		Settings.trip_amount = trip0
		print("[VnRevealTest] engine · %d finding(s)" % _bad)
		get_tree().quit(1 if _bad > 0 else 0)
		return
	Settings.set("auto_play", false)
	# THE TRIP's glow breathes around the letters: off, so a lit pixel is text
	var trip_was: float = Settings.trip_amount
	Settings.trip_amount = 0.0
	var out: String = String(_args.get("out", ""))
	if out != "":
		DirAccess.make_dir_recursive_absolute(out)
	var bg := ColorRect.new()
	bg.color = Color.BLACK
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	var dlg: Control = DLG.instantiate()
	add_child(dlg)
	dlg.call("setup", SkinDB.get_for_vol(5))
	for i in 5:
		await get_tree().process_frame
	var size: Vector2i = get_viewport().get_texture().get_size()
	print("  frame %s · canvas %s · Godot %s" % [size, get_viewport().get_visible_rect().size, Engine.get_version_info()["string"]])
	var cases: int = 0
	for side: String in ["", "right", "left"]:
		for li in LINES.size():
			cases += 1
			var where: String = "line %d, portrait %s" % [li + 1, side if side != "" else "none"]
			dlg.call("set_extra_occupied", side)
			if li == 3:
				dlg.call("show_say", "The Demon", LINES[li])
			else:
				dlg.call("show_narrate", LINES[li])
			var frames: Array = []
			var plates: Array = []
			var guard: int = 0
			while bool(dlg.call("is_typing")) and guard < 4000:
				guard += 1
				var gi: Image = await _grab()
				frames.append(_lit(gi))
				if out != "" and String(_args.get("dump", "")) == "%d%s" % [li + 1, side] :
					gi.save_png("%s/dump_%03d.png" % [out, guard])
				plates.append((dlg.get("_plate") as Control).get_global_rect())
			for i in 20:
				await get_tree().process_frame
			var final_img: Image = await _grab()
			var fin: PackedByteArray = _lit(final_img)
			var plate: Rect2 = (dlg.get("_plate") as Control).get_global_rect()
			var sx: float = float(size.x) / get_viewport().get_visible_rect().size.x
			var w: int = size.x
			var moved_frames: int = 0
			var outside_frames: int = 0
			var worst: int = 0
			for fi in frames.size():
				var f: PackedByteArray = frames[fi]
				var stray: int = 0
				var outside: int = 0
				var pr: Rect2 = plates[fi]
				for i in f.size():
					if f[i] == 1:
						if fin[i] == 0:
							stray += 1
						if fi > 20:
							var x: float = float(i % w) / sx
							var y: float = float(i / w) / sx
							if x < pr.position.x - 1.0 or x > pr.end.x + 1.0 or y < pr.position.y - 1.0 or y > pr.end.y + 1.0:
								outside += 1
				if stray > 12:
					print("      frame %d of %d: %d stray px" % [fi, frames.size(), stray])
					moved_frames += 1
					worst = maxi(worst, stray)
					if out != "" and moved_frames == 1:
						(await _grab()).save_png("%s/moved_%d_%s.png" % [out, li + 1, side if side != "" else "none"])
				if outside > 12:
					print("      frame %d of %d: %d px outside the plate %s" % [fi, frames.size(), outside, pr])
					outside_frames += 1
			if moved_frames > 0:
				_bad += 1
				print("  ✗ %s: %d of %d typing frames show text where the finished line has none (worst %d px) — a word moved" % [where, moved_frames, frames.size(), worst])
			if outside_frames > 0:
				_bad += 1
				print("  ✗ %s: %d of %d typing frames have text outside the plate" % [where, outside_frames, frames.size()])
			if moved_frames == 0 and outside_frames == 0:
				print("  ok %s: %d typing frames, plate %s" % [where, frames.size(), plate])
			if out != "":
				final_img.save_png("%s/final_%d_%s.png" % [out, li + 1, side if side != "" else "none"])
	Settings.trip_amount = trip_was
	print("[VnRevealTest] %d case(s) · %d finding(s)" % [cases, _bad])
	get_tree().quit(1 if _bad > 0 else 0)
