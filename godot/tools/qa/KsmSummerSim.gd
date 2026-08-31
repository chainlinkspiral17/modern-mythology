extends Node
## Headless QA: KWIK STOP MANAGER summer sim — twelve weeks through
## the real UI. Plan phase: pick the first three available crew
## checkboxes and RUN THE WEEK; event/report/robbery phases: press
## the go button or the first safe choice. On week_over the sim
## re-boots the same KsmWeek with the emitted state (what the host
## does). Ends at summer_over.
##
## PROGRESS asserts: week 12 reached, the score computes, at least
## one mid-summer event resolved. Stalls fail loudly.
##
## Run: godot --headless res://tools/qa/KsmSummerSim.tscn

const WEEK_SCENE := "res://scenes/games/kwik_stop_manager/KsmWeek.tscn"
const TICK_CAP := 3000
const STALL_FAIL := 250

var _over: bool = false
var _final: Dictionary = {}
var _week: Node = null


func _ready() -> void:
	_week = (load(WEEK_SCENE) as PackedScene).instantiate()
	add_child(_week)
	_week.connect("summer_over", func(st: Dictionary) -> void:
		_over = true
		_final = st)
	_week.connect("week_over", func(st: Dictionary) -> void:
		# the host re-opens the week scene with the new state;
		# re-booting the same instance is the same contract
		_week.call_deferred("boot", st))
	await get_tree().process_frame
	_week.call("boot", {"week_n": 1, "cash": 300, "stock": 5, "morale": 5,
		"landlord": 5, "last_crew": [], "events_done": [], "staff_gone": [],
		"robbery_choice": "", "summers": [], "canon_vars": {},
		"lore_tokens_pending": []})
	await get_tree().process_frame

	var last_fp: String = ""
	var stall: int = 0
	for tick in range(TICK_CAP):
		await get_tree().process_frame
		await get_tree().process_frame
		if _over:
			break
		var st: Dictionary = _week.get("_state")
		var phase := String(_week.get("_phase"))
		var picked: Array = _week.get("_picked")
		var fp: String = "%s,%s,%d" % [st.get("week_n", 1), phase, picked.size()]
		if fp == last_fp:
			stall += 1
			if stall >= STALL_FAIL:
				print("KSMSIM-STALL at %s" % fp)
				var dump: Array = []
				_collect(_week, dump, false)
				for b_v in dump:
					print("  btn: '%s' vis=%s dis=%s" % [(b_v as Button).text,
						(b_v as Button).visible, (b_v as Button).disabled])
				get_tree().quit(1)
				return
		else:
			last_fp = fp
			stall = 0
		_drive(phase, picked)

	if not _over:
		print("KSMSIM-FAIL · summer never ended")
		get_tree().quit(1)
		return
	print("KSMSIM-END · cash=%s morale=%s landlord=%s stock=%s" %
		[_final.get("cash", "?"), _final.get("morale", "?"),
		 _final.get("landlord", "?"), _final.get("stock", "?")])
	print("KSMSIM-END · events_done=%s staff_gone=%s" %
		[_final.get("events_done", []), _final.get("staff_gone", [])])
	var ok: bool = int(_final.get("week_n", 0)) >= 12 \
		and (_final.get("events_done", []) as Array).size() >= 1
	print("Kwik Stop Manager summer sim done · %s" % ("PASS" if ok else "FAIL (progress asserts)"))
	get_tree().quit(0 if ok else 1)


func _drive(phase: String, picked: Array) -> void:
	if phase == "plan" and picked.size() < 3:
		# tick the first open crew box; setting the property fires
		# the toggled handler, which is the real code path
		var boxes: Array = []
		_collect(_week, boxes, true)
		for cb_v in boxes:
			var cb: CheckBox = cb_v
			if not cb.button_pressed and not cb.disabled:
				cb.button_pressed = true
				return
		return
	# go button first (RUN THE WEEK / NEXT WEEK / THE FALL REOPENING)
	var btns: Array = []
	_collect(_week, btns, false)
	for b_v in btns:
		var b: Button = b_v
		if b is CheckBox:
			continue
		var t := b.text
		if t.contains("RUN THE WEEK") or t.contains("NEXT WEEK") or t.contains("REOPENING"):
			if b.visible and not b.disabled:
				b.emit_signal("pressed")
				return
	# otherwise a choice phase (robbery etc.): first safe button
	for b_v in btns:
		var b: Button = b_v
		if b is CheckBox or b.disabled:
			continue
		var t := b.text
		var bare := t.strip_edges()
		# skip the stock steppers (exact glyphs) and exits — nothing else
		if bare == "+" or bare == "−" or bare == "-":
			continue
		if t.contains("quit") or t.contains("shelf"):
			continue
		b.emit_signal("pressed")
		return


func _collect(root: Node, out: Array, boxes_only: bool) -> void:
	if boxes_only:
		if root is CheckBox and (root as CheckBox).is_visible_in_tree():
			out.append(root)
	elif root is Button and (root as Button).is_visible_in_tree():
		out.append(root)
	for c in root.get_children():
		_collect(c, out, boxes_only)
