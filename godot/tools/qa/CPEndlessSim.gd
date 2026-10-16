extends Node
## Headless QA: SEPTEMBER AND AFTER — seed endless mode from the
## campaign save the summer sim left in slot 3, then run ~120 more
## days: ratcheting Sunday spawns, the rhythm flavor pools (the
## one-shots are long dead by now), endless milestones every 8
## weeks, tower brightness, and the retire/white endings' plumbing.
## Run AFTER CPSimSweep (it seeds the slot):
##   godot --headless res://tools/qa/CPEndlessSim.tscn

var _game: Node = null

func _ready() -> void:
	var ps: PackedScene = load("res://scenes/games/CommunityPlannedGame.tscn")
	_game = ps.instantiate()
	add_child(_game)
	await get_tree().process_frame
	await get_tree().process_frame
	# Fresh endless seeded from slot 3's finished campaign — remove
	# any stale endless sibling first.
	var epath: String = _game.call("_endless_path_for_slot", 2)
	if FileAccess.file_exists(epath):
		# user:// paths need globalizing for remove_absolute — the
		# bare form fails SILENTLY and the probe resumed a stale
		# endless save because of it.
		DirAccess.remove_absolute(ProjectSettings.globalize_path(epath))
	_game.call("_begin_endless_with_slot", 2)
	await get_tree().process_frame
	var start_day: int = int(_game.get("_day"))
	print("CPENDLESS · begun at day %d" % start_day)
	var advances: int = 0
	for i in range(140):
		var before: int = int(_game.get("_day"))
		_game.call("_on_advance_day")
		for f in range(4):
			await get_tree().process_frame
		_close_bbs_if_open()
		for f in range(2):
			await get_tree().process_frame
		_dismiss_dialogs()
		if int(_game.get("_day")) == before:
			_dismiss_dialogs()
			await get_tree().process_frame
			_game.call("_on_advance_day")
			for f in range(3):
				await get_tree().process_frame
			_close_bbs_if_open()
			if int(_game.get("_day")) == before:
				# tower_white legitimately ends the run — report which
				print("CPENDLESS-STOP · day stuck at %d (iteration %d) · brightness=%s" %
					[before, i, str(_game.get("_tower_brightness"))])
				break
		advances += 1
	var weeks: int = int((int(_game.get("_day")) - 100) / 7.0)
	print("CPENDLESS · finished · day %s (%d endless weeks) after %d advances · milestones_fired=%s" %
		[str(_game.get("_day")), weeks, advances,
		 str((_game.get("_flags") as Dictionary).get("endless_milestones_fired", 0))])
	get_tree().quit(0)

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
