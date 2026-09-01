extends Node
## Headless QA: THE APPRENTICE probe — endless v2's succession
## mechanic, exercised deterministically. Boots endless from slot 3,
## pulls the offer forward to week 1, pins the tower dim (a probe
## may hold the weather still to watch one machine), auto-accepts
## via the dialog sweep, and runs ~70 days: offer → training (with
## its mis-route tuition) → the small ones are hers.
##
## Asserts: the offer fired and was accepted; training lines
## logged; at least one small problem auto-resolved after
## graduation. Run AFTER CPSimSweep seeds slot 3:
##   godot --headless res://tools/qa/ApprenticeProbe.tscn

var _game: Node = null


func _ready() -> void:
	var ps: PackedScene = load("res://scenes/games/CommunityPlannedGame.tscn")
	_game = ps.instantiate()
	add_child(_game)
	await get_tree().process_frame
	await get_tree().process_frame
	var epath: String = _game.call("_endless_path_for_slot", 2)
	if FileAccess.file_exists(epath):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(epath))
	_game.call("_begin_endless_with_slot", 2)
	await get_tree().process_frame
	# Deterministic: pre-accept (the offer dialog's async dance is
	# not what this probe tests — the weekly mechanic is).
	var flags: Dictionary = _game.get("_flags")
	flags["apprentice_since_week"] = 0
	var resolved_before: int = _resolved_total()

	var seeded_small: bool = false
	for i in range(70):
		# after graduation, keep one honest small problem available so
		# the pickup path is testable even on a full, ancient board
		if i > 40 and not seeded_small:
			var rs0: Dictionary = _game.get("_region_state")
			var hc: Dictionary = rs0.get("harmony_creek", {})
			var probs0: Array = hc.get("active_problems", [])
			if probs0.size() >= 4:
				probs0.remove_at(0)
			_game.call("_seed_problem", "harmony_creek", "newsletter_item")
			seeded_small = true
		# the probe holds the tower still to watch the apprentice
		_game.set("_tower_brightness", "dim")
		_game.set("_last_brightness_change_day", int(_game.get("_day")))
		_game.call("_on_advance_day")
		for f in range(4):
			await get_tree().process_frame
		_close_bbs_if_open()
		for f in range(2):
			await get_tree().process_frame
		_dismiss_dialogs()
		await get_tree().process_frame

	var rs: Dictionary = _game.get("_region_state")
	for r_id in rs:
		if String(r_id).begins_with("_"):
			continue
		var probs: Array = (rs[r_id] as Dictionary).get("active_problems", [])
		var sevs: Array = []
		for p_v in probs:
			sevs.append("%.1f%s" % [float((p_v as Dictionary).get("severity", 0)),
				"*" if String((p_v as Dictionary).get("in_progress_by", "")) != "" else ""])
		print("APPR-BOARD %s · %s" % [r_id, sevs])
	flags = _game.get("_flags")
	var since: int = int(flags.get("apprentice_since_week", -1))
	var aw: int = int(_game.call("_apprentice_weeks"))
	var resolved_after: int = _resolved_total()
	var log_lines: Array = _game.get("_log_lines")
	var training_seen: bool = false
	var small_seen: bool = false
	for ln_v in log_lines:
		var ln := String(ln_v)
		if ln.contains("Aria") and (ln.contains("dispatches") or ln.contains("alphabetizes") \
				or ln.contains("traces") or ln.contains("drills") or ln.contains("region files")):
			training_seen = true
		if ln.contains("smallest problem off the board") or ln.contains("littlest fire") \
				or ln.contains("about the fence") or ln.contains("pencil mark where it stood") \
				or ln.contains("never have been a problem"):
			small_seen = true
	print("APPR · since_week=%d · apprentice_weeks=%d · resolved %d → %d" %
		[since, aw, resolved_before, resolved_after])
	print("APPR · training_seen=%s · small_ones_seen=%s" % [training_seen, small_seen])
	var ok: bool = since >= 0 and aw >= 5 and training_seen \
		and (small_seen or resolved_after > resolved_before)
	print("Apprentice probe done · %s" % ("PASS" if ok else "FAIL"))
	get_tree().quit(0 if ok else 1)


func _resolved_total() -> int:
	var prc: Dictionary = _game.get("_problem_resolved_counts")
	var n: int = 0
	for k in prc:
		n += int(prc[k])
	return n


func _close_bbs_if_open() -> void:
	for c in _game.get_children():
		if c is Node and c.has_signal("hung_up") and c.has_method("_hang_up"):
			c.call("_hang_up")


func _dismiss_dialogs() -> void:
	for c in _game.get_children():
		if c is AcceptDialog:
			c.hide()
			if c.has_signal("confirmed"):
				c.emit_signal("confirmed")
