extends Node
## Headless QA: the evening-loop driver — one sim for the three
## sticks that share the boot(state) → buttons → <x>_over(state) →
## re-boot contract: Mrs Wu's garden evenings, Hane no Niwa's shrine
## visits, Patient Mister Glass's kitchen evenings. Presses
## continue-ish buttons first, else the first safe button (ending a
## visit IS progress here, so only quit/shelf words are skipped).
##
## Each target asserts PROGRESS on a state counter, not just
## no-crash. Stalls dump the button tree and fail.
##
## Run: godot --headless res://tools/qa/EveningLoopSim.tscn

const STALL_FAIL := 250

var _loops: int = 0
var _presses: int = 0
var _over: bool = false
var _last_state: Dictionary = {}
var _fails: int = 0
var _child: Node = null
var _host_inc: String = ""


func _ready() -> void:
	await _run_target("mrs_wu", "res://scenes/games/mrs_wus_garden/WuGarden.tscn",
		{"evening": 1, "conditions": {}, "missed": {}, "covered": [], "dead": [],
		 "sits": 0, "stories_heard": [], "last_tended": "", "visitor_seen": false,
		 "melody_heard": false, "canon_vars": {}, "lore_tokens_pending": []},
		"evening_done", "garden_over", 40, 2600, "evening", 5)
	await _run_target("hane_no_niwa", "res://scenes/games/hane_no_niwa/ShrineVisit.tscn",
		{"visit_total": 0, "swept": 0, "mended": 5, "satchel": [], "lexicon": [],
		 "lexicon_items": [], "lexicon_prev": [], "season_offered": [], "feathers": 0,
		 "ng_plus": false, "letters_kept": [], "canon_vars": {}, "lore_tokens_pending": []},
		"visit_over", "", 10, 2600, "visit_total", 6)
	await _run_target("mister_glass", "res://scenes/games/patient_mister_glass/GlassKitchen.tscn",
		{"evening_n": 1, "trust": 5, "answers_heard": [], "findings": [],
		 "unlocked_questions": [], "rain_evenings": [3, 7],
		 "canon_vars": {}, "lore_tokens_pending": []},
		"evening_over", "", 8, 2600, "evening_n", 5, "evening_n")
	print("Evening loop sim done · %d failure(s)" % _fails)
	get_tree().quit(1 if _fails > 0 else 0)


func _run_target(tag: String, scene_path: String, fresh: Dictionary,
		loop_sig: String, over_sig: String, max_loops: int, tick_cap: int,
		progress_key: String, progress_min: int, host_inc: String = "") -> void:
	_loops = 0
	_over = false
	_last_state = fresh.duplicate(true)
	# The host contract: a FRESH child per evening/visit. Re-booting
	# one instance stacks duplicate UI (WuGarden's boot appends).
	# NOTE a lambda capturing a local by value cannot re-point it —
	# the child lives in a member var, spawned by a real method.
	var packed: PackedScene = load(scene_path)
	_host_inc = host_inc
	_spawn(packed, fresh, loop_sig, over_sig, max_loops)
	await get_tree().process_frame
	await get_tree().process_frame
	var seen_loops: int = 0

	var last_fp: String = ""
	var stall: int = 0
	for tick in range(tick_cap):
		await get_tree().process_frame
		await get_tree().process_frame
		if _over:
			break
		if _loops != seen_loops:
			seen_loops = _loops
			_spawn(packed, _last_state, loop_sig, over_sig, max_loops)
			await get_tree().process_frame
			continue
		var btns: Array = []
		_collect(_child, btns)
		var fp: String = "%d,%d,%d" % [_loops, _presses, btns.size()]
		if fp == last_fp:
			stall += 1
			if stall >= STALL_FAIL:
				print("EVSIM-STALL %s at loop %d" % [tag, _loops])
				for b_v in btns:
					print("  btn: '%s' dis=%s" % [(b_v as Button).text, (b_v as Button).disabled])
				_fails += 1
				break
		else:
			last_fp = fp
			stall = 0
		var pick: Button = _choose(btns)
		if pick != null:
			_presses += 1
			pick.emit_signal("pressed")

	if not _over:
		var dump: Array = []
		_collect(_child, dump)
		print("EVSIM-CAP %s exhausted · buttons at end:" % tag)
		for b_v in dump:
			print("  btn: '%s' dis=%s" % [(b_v as Button).text, (b_v as Button).disabled])
	var got: int = int(_last_state.get(progress_key, -1))
	if got >= progress_min:
		print("EVSIM-OK   %s · loops=%d · %s=%d" % [tag, _loops, progress_key, got])
	else:
		print("EVSIM-FAIL %s · loops=%d · %s=%d (< %d)" % [tag, _loops, progress_key, got, progress_min])
		_fails += 1
	if _child != null and is_instance_valid(_child):
		_child.queue_free()
	_child = null
	await get_tree().process_frame


func _spawn(packed: PackedScene, st: Dictionary, loop_sig: String,
		over_sig: String, max_loops: int) -> void:
	if _child != null and is_instance_valid(_child):
		_child.queue_free()
	_child = packed.instantiate()
	add_child(_child)
	_child.connect(loop_sig, func(st2: Dictionary) -> void:
		_loops += 1
		_presses = 0
		# some hosts own the counter step (glass increments evening_n
		# in _on_evening_over) — mimic that contract here
		if _host_inc != "":
			st2[_host_inc] = int(st2.get(_host_inc, 1)) + 1
		_last_state = st2
		_over = _loops >= max_loops)
	if over_sig != "" and _child.has_signal(over_sig):
		_child.connect(over_sig, func(st2: Dictionary) -> void:
			_last_state = st2
			_over = true)
	_child.call_deferred("boot", st.duplicate(true))


func _is_ender(t: String) -> bool:
	var low := t.to_lower()
	for w in ["end the", "→", "next", "morning", "go on", "leave", "down the hill",
			"good night", "goodnight", "home", "close up", "get back to his kitchen"]:
		if low.contains(String(w)):
			return true
	return false


func _choose(btns: Array) -> Button:
	# A few real actions per loop, then take the evening's exit —
	# a driver that only tends dahlias never sleeps.
	if _presses >= 3:
		for b_v in btns:
			var b: Button = b_v
			if not b.disabled and _is_ender(b.text):
				return b
	# action pass runs LAST-first: modal overlays (Hane's bring menu)
	# are added after the base UI and block it while open
	for i in range(btns.size() - 1, -1, -1):
		var b: Button = btns[i]
		if b.disabled:
			continue
		var t := b.text
		if t.contains("quit") or t.contains("shelf") or t.contains("put it down"):
			continue
		if _presses < 3 and _is_ender(t):
			continue
		return b
	# nothing but enders left: take one
	for b_v in btns:
		var b: Button = b_v
		if not b.disabled and _is_ender(b.text):
			return b
	return null


func _collect(root: Node, out: Array) -> void:
	if root is Button and (root as Button).is_visible_in_tree():
		out.append(root)
	for c in root.get_children():
		_collect(c, out)
