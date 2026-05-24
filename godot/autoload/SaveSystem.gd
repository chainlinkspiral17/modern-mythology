extends Node
## Save slot system. Autoloaded as "SaveSystem".

const SAVE_DIR      := "user://saves"
const GALLERY_PATH  := "user://progress/gallery.cfg"
const UNLOCKS_PATH  := "user://progress/unlocks.cfg"
const MAX_SLOTS     := 8

signal save_written(slot: int)
signal save_deleted(slot: int)

var _seen_cgs:  Dictionary = {}
var _unlocked:  Dictionary = {}


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(SAVE_DIR)
	_load_gallery()
	_load_unlocks()


# ── Save slots ────────────────────────────────────────────────────────────────

func list_saves() -> Array:
	var out: Array = []
	for i in range(1, MAX_SLOTS + 1):
		var path := _slot_path(i)
		if FileAccess.file_exists(path):
			var data := _read_json(path)
			if not data.is_empty():
				out.append(data)
				continue
		out.append({"slot": i, "empty": true})
	return out


func write_save(slot: int, vol: int, scene_id: String, node_idx: int,
				flags: Dictionary, skills: Dictionary, log: Array) -> void:
	var data := {
		"slot":      slot,
		"vol":       vol,
		"ts":        Time.get_unix_time_from_system(),
		"scene":     scene_id,
		"nodeIndex": node_idx,
		"flags":     flags,
		"skills":    skills,
		"log":       log.slice(maxi(0, log.size() - 50)),
	}
	_write_json(_slot_path(slot), data)
	save_written.emit(slot)


func read_save(slot: int) -> Dictionary:
	var path := _slot_path(slot)
	if not FileAccess.file_exists(path):
		return {}
	return _read_json(path)


func delete_save(slot: int) -> void:
	var path := _slot_path(slot)
	if FileAccess.file_exists(path):
		DirAccess.remove_absolute(path)
		save_deleted.emit(slot)


func has_any_save() -> bool:
	for i in range(1, MAX_SLOTS + 1):
		if FileAccess.file_exists(_slot_path(i)):
			return true
	return false


# ── Gallery ───────────────────────────────────────────────────────────────────

func mark_cg_seen(cg_id: String) -> void:
	if cg_id == "" or _seen_cgs.has(cg_id):
		return
	_seen_cgs[cg_id] = true
	_save_gallery()


func is_cg_seen(cg_id: String) -> bool:
	return _seen_cgs.has(cg_id)


func get_seen_cgs() -> Dictionary:
	return _seen_cgs.duplicate()


# ── Unlocks ───────────────────────────────────────────────────────────────────

## Returns true only on the first call for this key (new unlock).
func mark_unlocked(key: String) -> bool:
	if _unlocked.has(key):
		return false
	_unlocked[key] = true
	_save_unlocks()
	return true


func is_unlocked(key: String) -> bool:
	return _unlocked.has(key)


# ── Internal ──────────────────────────────────────────────────────────────────

func _slot_path(slot: int) -> String:
	return SAVE_DIR + "/slot_%d.json" % slot


func _read_json(path: String) -> Dictionary:
	var f := FileAccess.open(path, FileAccess.READ)
	if not f:
		return {}
	var text := f.get_as_text()
	f.close()
	var parsed = JSON.parse_string(text)
	if parsed is Dictionary:
		return parsed as Dictionary
	return {}


func _write_json(path: String, data: Dictionary) -> void:
	var f := FileAccess.open(path, FileAccess.WRITE)
	if not f:
		push_error("SaveSystem: cannot write " + path)
		return
	f.store_string(JSON.stringify(data, "\t"))
	f.close()


func _load_unlocks() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(UNLOCKS_PATH) != OK:
		return
	if cfg.has_section("unlocked"):
		for key in cfg.get_section_keys("unlocked"):
			_unlocked[key] = true


func _save_unlocks() -> void:
	DirAccess.make_dir_recursive_absolute("user://progress")
	var cfg := ConfigFile.new()
	for key in _unlocked:
		cfg.set_value("unlocked", key, true)
	cfg.save(UNLOCKS_PATH)


func _load_gallery() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(GALLERY_PATH) != OK:
		return
	if cfg.has_section("seen"):
		for key in cfg.get_section_keys("seen"):
			_seen_cgs[key] = true


func _save_gallery() -> void:
	DirAccess.make_dir_recursive_absolute("user://progress")
	var cfg := ConfigFile.new()
	for cg_id in _seen_cgs:
		cfg.set_value("seen", cg_id, true)
	cfg.save(GALLERY_PATH)
