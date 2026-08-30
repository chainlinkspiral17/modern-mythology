extends Node
## Headless QA: in-engine compile of every script, WITH autoloads
## live (running as a scene inside the project, unlike --script
## mode where autoload identifiers fail to resolve).
## Run: godot --headless res://tools/qa/CompileSweep.tscn

func _ready() -> void:
	var bad: int = 0
	var total: int = 0
	var stack: Array = ["res://scenes", "res://scripts", "res://autoload"]
	while not stack.is_empty():
		var dir_path: String = stack.pop_back()
		for sub in DirAccess.get_directories_at(dir_path):
			stack.append(dir_path + "/" + sub)
		for fn in DirAccess.get_files_at(dir_path):
			if String(fn).ends_with(".gd"):
				total += 1
				var s: Variant = load(dir_path + "/" + String(fn))
				if s == null:
					print("COMPILE-FAIL " + dir_path + "/" + String(fn))
					bad += 1
	print("QA compile sweep: %d scripts, %d failures" % [total, bad])
	get_tree().quit(1 if bad > 0 else 0)
