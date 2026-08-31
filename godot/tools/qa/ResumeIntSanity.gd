extends Node
## Headless QA: save-resume int sanity — the JSON-float class, tested
## at the boundary it corrupts. JSON.parse_string returns every
## number as a float, so saved int arrays come back unmatchable by
## Array.has(int). This writes a save file the way a real JSON
## round-trip leaves it, boots the host, and asserts the loaded
## arrays are ints again (the normalizers added 2026-08-31).
##
## Covers: Fey Faire shows_attended (gates REST advancement) and
## Riffrocker meetings_attended (attendance dedupe). Add a block
## here whenever a host gains a saved number array that gets .has()
## checks — this is the regression net for the class.
##
## Run: godot --headless res://tools/qa/ResumeIntSanity.tscn

var _fails: int = 0


func _ready() -> void:
	await _check_fey_faire()
	await _check_riffrocker()
	print("Resume int sanity done · %d failure(s)" % _fails)
	get_tree().quit(1 if _fails > 0 else 0)


func _write_json(path: String, data: Dictionary) -> void:
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string(JSON.stringify(data, "  "))
	f.close()


func _all_ints(arr: Array) -> bool:
	for v in arr:
		if typeof(v) != TYPE_INT:
			return false
	return true


func _check_fey_faire() -> void:
	# A save as the round-trip leaves it: attended nights as numbers
	# (they come back floats), night 3 pending.
	_write_json("user://fey_faire.save.json",
		{"night": 3, "shows_attended": [1, 2]})
	var host: Node = (load("res://scenes/games/fey_faire/FeyFaireHost.tscn") as PackedScene).instantiate()
	add_child(host)
	for i in range(4):
		await get_tree().process_frame
	var rs: Dictionary = host.get("_run_state")
	var att: Array = rs.get("shows_attended", [])
	if not _all_ints(att):
		print("RESUME-FAIL fey_faire · shows_attended holds non-ints: %s" % [att])
		_fails += 1
	elif not att.has(2):
		print("RESUME-FAIL fey_faire · attended.has(2) false after load: %s" % [att])
		_fails += 1
	else:
		print("RESUME-OK   fey_faire · shows_attended=%s · has(2)=true" % [att])
	host.queue_free()
	await get_tree().process_frame
	DirAccess.remove_absolute(ProjectSettings.globalize_path("user://fey_faire.save.json"))


func _check_riffrocker() -> void:
	_write_json("user://riffrocker_melody_club.save.json",
		{"meeting_n": 3, "meetings_attended": [1, 2]})
	var host: Node = (load("res://scenes/games/riffrocker_melody_club/RiffrockerClubHost.tscn") as PackedScene).instantiate()
	add_child(host)
	for i in range(4):
		await get_tree().process_frame
	var rs: Dictionary = host.get("_run_state")
	var att: Array = rs.get("meetings_attended", [])
	if not _all_ints(att):
		print("RESUME-FAIL riffrocker · meetings_attended holds non-ints: %s" % [att])
		_fails += 1
	elif not att.has(2):
		print("RESUME-FAIL riffrocker · attended.has(2) false after load: %s" % [att])
		_fails += 1
	else:
		print("RESUME-OK   riffrocker · meetings_attended=%s · has(2)=true" % [att])
	host.queue_free()
	await get_tree().process_frame
	DirAccess.remove_absolute(ProjectSettings.globalize_path("user://riffrocker_melody_club.save.json"))
