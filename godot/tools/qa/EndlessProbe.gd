extends Node
func _ready() -> void:
	var ps: PackedScene = load("res://scenes/games/CommunityPlannedGame.tscn")
	var g: Node = ps.instantiate()
	add_child(g)
	await get_tree().process_frame
	await get_tree().process_frame
	var epath: String = g.call("_endless_path_for_slot", 2)
	if FileAccess.file_exists(epath):
		var abs_e: String = ProjectSettings.globalize_path(epath)
		DirAccess.remove_absolute(abs_e)
	print("PROBE epath_exists_after_delete=%s" % str(FileAccess.file_exists(epath)))
	g.call("_begin_endless_with_slot", 2)
	await get_tree().process_frame
	print("PROBE endless=%s day=%s flags.endless_mode=%s" %
		[str(g.get("_endless")), str(g.get("_day")),
		 str((g.get("_flags") as Dictionary).get("endless_mode"))])
	for i in range(70):
		g.call("_on_advance_day")
		for f in range(3):
			await get_tree().process_frame
		for c in g.get_children():
			if c is Node and c.has_signal("hung_up") and c.has_method("_hang_up"):
				c.call("_hang_up")
		await get_tree().process_frame
		if i % 10 == 0:
			var day: int = int(g.get("_day"))
			var week: int = int(ceil(float(day) / 7.0))
			print("PROBE i=%d day=%d week=%d ew=%d endless=%s fired=%s" %
				[i, day, week, week - 15, str(g.get("_endless")),
				 str((g.get("_flags") as Dictionary).get("endless_milestones_fired", "unset"))])
	get_tree().quit(0)
