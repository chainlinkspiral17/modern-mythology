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


func _run() -> void:
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
