## CharLayerStageTest (2026-11-09): the stage's moves, without hero models.
## Drives CharLayer alone over a 3D set with special-2D stand-ins: a hidden
## or displaced portrait comes back SLIDING (same node) within 2 lines; `hide
## center` finds the portrait a 3D set put at an edge; a three-shot's centre
## slides home when its edge's owner arrives; a re-shown portrait's slot
## forgets "center". Exit code = failures.
##
##   godot --headless --path godot --script res://tools/CharLayerStageTest.gd
extends SceneTree
var cl: Control
var fails: int = 0
func _ok(c: bool, what: String) -> void:
	print(("PASS  " if c else "FAIL  ") + what)
	if not c: fails += 1
func _node_of(k: String) -> Control:
	for p: String in cl._slots:
		var s = cl._slots[p]
		if s != null and s["name"] == k: return s["node"]
	return null
func _slot_of(k: String) -> String:
	for p: String in cl._slots:
		var s = cl._slots[p]
		if s != null and s["name"] == k: return p
	return ""
func _initialize() -> void:
	cl = load("res://scenes/game/CharLayer.gd").new()
	root.add_child(cl)
	cl.bg_is_3d = true
	for c in ["diego", "maya", "sam", "linda", "anita", "bill"]:
		cl.allow_special_2d(c, "res://assets/gallery/portrait_dante_1.png")
	await process_frame
	# vol6_ch9_safehouse 59..66: diego center (-> an edge), hide center, maya right, diego left
	cl.show_character("diego", "neutral", "center")
	var d0: Control = _node_of("diego")
	var d0_slot: String = _slot_of("diego")
	_ok(d0 != null, "diego shown (at %s)" % d0_slot)
	cl.direct_line("", "line", "", "narrate")
	cl.hide_at("center")
	_ok(_node_of("diego") == null, "hide center hides the centre-shown portrait on a 3D set")
	cl.show_character("maya", "neutral", "right")
	cl.show_character("diego", "neutral", "left")
	_ok(_node_of("diego") == d0, "diego's SAME portrait comes back (no new node)")
	_ok(_slot_of("diego") == "left" and d0.has_meta("slide_x"), "and slides to left (slide_x %s)" % str(d0.get_meta("slide_x", 0.0)))
	_ok(not d0.has_meta("fading"), "no longer fading")
	# a solo->two-shot move while visible
	cl.show_character("maya", "neutral", "left")
	_ok(_slot_of("maya") == "left" and _slot_of("diego") == "", "maya moves into diego's slot; diego displaced")
	# held for 2 lines then freed
	cl.direct_line("", "a", "", "narrate"); cl.direct_line("", "b", "", "narrate")
	_ok(cl._displaced.has("diego"), "displaced diego still held after 2 lines")
	cl.direct_line("", "c", "", "narrate")
	_ok(not cl._displaced.has("diego"), "freed after the 3rd line")
	cl.show_character("diego", "neutral", "right")
	_ok(_node_of("diego") != null and _node_of("diego") != d0, "after the window, a fresh portrait")
	cl.hide_all(false)
	_ok(cl._displaced.is_empty() and _node_of("maya") == null, "scene change clears all")
	# three-shot on a 3D set: left / center / right keeps all three
	cl.show_character("linda", "neutral", "left")
	cl.show_character("anita", "neutral", "center")
	var a0: Control = _node_of("anita")
	_ok(_slot_of("anita") == "right", "anita's center stands at the free right edge")
	cl.show_character("bill", "neutral", "right")
	_ok(_node_of("anita") == a0 and _slot_of("anita") == "center", "bill takes right; anita SLIDES to center, same portrait")
	_ok(_slot_of("bill") == "right" and _slot_of("linda") == "left", "all three on stage")
	# the centre SPEAKER faces who they are talking to (2026-11-09)
	var want_r: float = -1.0 if cl._compute_flip("anita", "center", "right") else 1.0
	var want_l: float = -1.0 if cl._compute_flip("anita", "center", "left") else 1.0
	var want_f: float = -1.0 if cl._compute_flip("anita", "center", "forward") else 1.0
	_ok(want_r != want_l, "left and right are different facings for the centre")
	cl.activate_speaker("anita"); cl.direct_line("anita", "Well, here we are.", "", "say")
	_ok(float(a0.get_meta("flip_x")) == want_f, "nobody has spoken: the centre speaker faces forward")
	cl.activate_speaker("bill"); cl.direct_line("bill", "It is late.", "", "say")
	_ok(float(a0.get_meta("flip_x")) == want_r, "bill (right) speaks: the centre listener turns to him")
	cl.activate_speaker("anita"); cl.direct_line("anita", "It is always late.", "", "say")
	_ok(float(a0.get_meta("flip_x")) == want_r, "the centre answers bill: she FACES him (was forward)")
	cl.activate_speaker("anita"); cl.direct_line("anita", "Linda, hand me the plates.", "", "say")
	_ok(float(a0.get_meta("flip_x")) == want_l, "a line that names linda (left): the centre turns to her")
	cl.activate_speaker(""); cl.direct_line("", "The plates go round.", "", "narrate")
	_ok(float(a0.get_meta("flip_x")) == want_f, "narration: the centre faces forward again")
	cl.hide_all(false)
	# re-shown at its own slot: a later hide center is not about it (vol 7 ch5)
	cl.show_character("diego", "neutral", "center")
	cl.show_character("maya", "neutral", "left")
	cl.show_character("diego", "neutral", "right")
	cl.hide_at("center")
	_ok(_slot_of("diego") == "right", "re-shown at right, a hide of the empty centre leaves diego up")
	cl.hide_all(false)
	for i in 30: await process_frame
	print("RESULT fails=%d" % fails)
	quit(fails)
