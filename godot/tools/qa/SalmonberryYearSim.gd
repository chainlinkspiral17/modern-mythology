extends Node
## Headless QA: SALMONBERRY year sim — WAVE D's day-one driver.
## Plays the whole Sept→June year through the real UI: an errand
## when one is offered (the new system under test), else the week's
## event, else the first activity; rests when worn thin; skips the
## March realtime crisis via _resolve_crisis({}) (the legitimate
## nobody-saved path — the walkable crisis is MonkeySweep territory).
##
## PROGRESS asserts: the year ends, ≥3 errands completed, ≥1 event
## taken, bonds grew. A stalled screen fails loudly.
##
## Run: godot --headless res://tools/qa/SalmonberryYearSim.tscn

const YEAR_SCENE := "res://scenes/games/salmonberry/SalmonberryYear.tscn"
const TICK_CAP := 4000
const STALL_FAIL := 300

var _year_over: bool = false
var _result: Dictionary = {}


func _ready() -> void:
	var year: Control = (load(YEAR_SCENE) as PackedScene).instantiate()
	add_child(year)
	year.connect("year_over", func(r: Dictionary) -> void:
		_year_over = true
		_result = r)
	await get_tree().process_frame
	year.call("boot", {"month": 0, "money": 0, "bonds": {}, "seed": 4242})
	await get_tree().process_frame

	var last_fp: String = ""
	var stall: int = 0
	for tick in range(TICK_CAP):
		await get_tree().process_frame
		await get_tree().process_frame
		if _year_over:
			break
		var s: Dictionary = year.get("_s")
		# March: the realtime crisis is out of a button-sim's reach —
		# resolve it directly down the no-rescue path and move on.
		if int(s.get("month", 0)) == 6:
			year.call("_resolve_crisis", {})
			await get_tree().process_frame
			continue
		var btns: Array = []
		_collect_buttons(year, btns)
		var fp: String = "%d,%d,%d" % [int(s.get("month", 0)), int(s.get("week", 1)), btns.size()]
		if fp == last_fp:
			stall += 1
			if stall >= STALL_FAIL:
				print("SBSIM-STALL at %s" % fp)
				get_tree().quit(1)
				return
		else:
			last_fp = fp
			stall = 0
		var pick: Button = _choose(btns, int(s.get("energy", 8)))
		if pick != null:
			pick.emit_signal("pressed")

	if not _year_over:
		print("SBSIM-FAIL · year never ended")
		get_tree().quit(1)
		return
	# year_over emits {state, register, coda} — the year lives inside.
	var s2: Dictionary = _result.get("state", {})
	var errs: Array = s2.get("errands_done", [])
	var evs: Array = s2.get("events_taken", [])
	var bonds: Dictionary = s2.get("bonds", {})
	print("SBSIM-END · errands=%s" % [errs])
	print("SBSIM-END · events=%s" % [evs])
	print("SBSIM-END · bonds=%s · register=%s" % [bonds, _result.get("register", "?")])
	print("SBSIM-END · apts=%s · money=%s · journal=%d" %
		[s2.get("apts", {}), s2.get("money", 0), (s2.get("journal", []) as Array).size()])
	var ok: bool = errs.size() >= 3 and evs.size() >= 1 and bonds.size() >= 3
	print("Salmonberry year sim done · %s" % ("PASS" if ok else "FAIL (progress asserts)"))
	get_tree().quit(0 if ok else 1)


func _choose(btns: Array, energy: int) -> Button:
	# Priority: the continue button → an errand (✚) → the event (★)
	# → rest when worn → the first plain activity.
	for b_v in btns:
		var b: Button = b_v
		if b.text.contains("week passes") or b.text.contains("year ends") \
				or b.text.contains("go on") or b.text.contains("morning comes"):
			return b
	for b_v in btns:
		var b: Button = b_v
		if b.text.strip_edges().begins_with("✚") and not b.disabled:
			return b
	for b_v in btns:
		var b: Button = b_v
		if b.text.strip_edges().begins_with("★") and not b.disabled:
			return b
	if energy <= 2:
		for b_v in btns:
			var b: Button = b_v
			if b.text.contains("Keep to the house"):
				return b
	for b_v in btns:
		var b: Button = b_v
		if b.disabled:
			continue
		var t: String = b.text
		if t.contains("put it down") or t.contains("WALK INTO TOWN") \
				or t.contains("general store") or t.contains("book of the coast") \
				or t.contains("RUN"):
			continue
		return b
	return null


func _collect_buttons(root: Node, out: Array) -> void:
	if root is Button and (root as Button).is_visible_in_tree():
		out.append(root)
	for c in root.get_children():
		_collect_buttons(c, out)
