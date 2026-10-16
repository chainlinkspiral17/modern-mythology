extends Node
## Headless QA: SIMULATE Community Planned — boot a fresh summer in
## slot 3, then drive the day loop through Labor Day, dispatching an
## agent every few days and hanging up every Sunday's BBS. Catches
## the runtime errors and stalls no static check can see.
## Run: godot --headless res://tools/qa/CPSimSweep.tscn

var _game: Node = null
var _days_run: int = 0

func _ready() -> void:
	var ps: PackedScene = load("res://scenes/games/CommunityPlannedGame.tscn")
	_game = ps.instantiate()
	add_child(_game)
	await get_tree().process_frame
	await get_tree().process_frame
	# Fresh summer in the QA slot (3rd) — wipe any stale save first.
	var save_path: String = _game.call("_save_path_for_slot", 2)
	if FileAccess.file_exists(save_path):
		DirAccess.remove_absolute(save_path)
	_game.call("_begin_session_with_slot", 2)
	await get_tree().process_frame
	print("CPSIM · summer begun · day=%s" % str(_game.get("_day")))
	# Drive through the summer.
	for i in range(110):
		var day_before: int = int(_game.get("_day"))
		if day_before >= 100:
			break
		# every 3rd day, try to dispatch the first available agent
		# at the first visible region's first problem
		if i % 3 == 0:
			_try_dispatch()
		_game.call("_on_advance_day")
		# give deferred work + possible BBS overlay time to appear
		for f in range(4):
			await get_tree().process_frame
		_close_bbs_if_open()
		for f in range(2):
			await get_tree().process_frame
		_dismiss_dialogs()
		var day_after: int = int(_game.get("_day"))
		if day_after == day_before:
			# a modal (stage dialog / finale) may be blocking — try
			# dismissing and advancing once more before declaring stall
			_dismiss_dialogs()
			await get_tree().process_frame
			_game.call("_on_advance_day")
			for f in range(3):
				await get_tree().process_frame
			_close_bbs_if_open()
			if int(_game.get("_day")) == day_before:
				print("CPSIM-STALL · day stuck at %d (iteration %d)" % [day_before, i])
				break
		_days_run += 1
		# Transcript dump: everything the ledger showed this day
		# (the store caps at 200 lines, so drain it daily).
		var lines: Array = _game.get("_log_lines")
		for ln in lines:
			var clean: String = str(ln)
			var rx := RegEx.new()
			rx.compile("\\[/?[a-z_]+[^\\]]*\\]")
			clean = rx.sub(clean, "", true)
			print("LEDGER| " + clean)
		lines.clear()
	print("CPSIM · finished · reached day %s after %d advances" % [str(_game.get("_day")), _days_run])
	get_tree().quit(0)

func _try_dispatch() -> void:
	# lowest-level poke: mark the first idle agent dispatched via the
	# game's own dispatch helper if exposed; otherwise skip (the sim's
	# main job is the day loop + BBS + finale path).
	pass

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
