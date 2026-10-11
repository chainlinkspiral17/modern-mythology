# stub autoload for the AudioMgr test project (tests/godot_audiomgr.test.js)
extends Node
func get_music_catalog() -> Array:
	# fixture catalog when a test writes one
	var p := "res://resources/music_catalog.json"
	if FileAccess.file_exists(p):
		var d = JSON.parse_string(FileAccess.get_file_as_string(p))
		if d is Array:
			return d
	return []
