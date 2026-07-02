extends Node
## Save slot system. Autoloaded as "SaveSystem".

const SAVE_DIR      := "user://saves"
const GALLERY_PATH  := "user://progress/gallery.cfg"
const UNLOCKS_PATH  := "user://progress/unlocks.cfg"
const SEEN_PATH     := "user://progress/seen.cfg"
const MAX_SLOTS     := 8
# Slot 0 is the autosave — written by the engine on every scene
# transition, shown in "continue" pickers, never offered for manual save.
const AUTOSAVE_SLOT := 0

signal save_written(slot: int)
signal save_deleted(slot: int)
signal unlocked_changed(key: String)

var _seen_cgs:  Dictionary = {}
var _unlocked:  Dictionary = {}
# scene_id -> highest node index the player has read (seen-text tracking
# for skip mode). Buffered in memory; flushed every few marks and at
# scene boundaries so we don't hit disk on every line.
var _seen_upto:   Dictionary = {}
var _seen_dirty:  int = 0


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(SAVE_DIR)
	_load_gallery()
	_load_unlocks()
	_load_seen()
	_migrate_substrate_seen_from_saves()


# ── Save slots ────────────────────────────────────────────────────────────────

func list_saves(include_autosave: bool = false) -> Array:
	var out: Array = []
	if include_autosave:
		var auto_path := _slot_path(AUTOSAVE_SLOT)
		if FileAccess.file_exists(auto_path):
			var auto_data := _read_json(auto_path)
			if not auto_data.is_empty():
				out.append(auto_data)
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
	for i in range(0, MAX_SLOTS + 1):
		if FileAccess.file_exists(_slot_path(i)):
			return true
	return false


# ── Seen text (skip-mode support) ─────────────────────────────────────────────

func get_seen_upto(scene_id: String) -> int:
	return int(_seen_upto.get(scene_id, -1))


func mark_seen_upto(scene_id: String, node_idx: int) -> void:
	if scene_id == "" or node_idx <= get_seen_upto(scene_id):
		return
	_seen_upto[scene_id] = node_idx
	_seen_dirty += 1
	if _seen_dirty >= 20:
		flush_seen()


func flush_seen() -> void:
	if _seen_dirty == 0:
		return
	_seen_dirty = 0
	DirAccess.make_dir_recursive_absolute("user://progress")
	var cfg := ConfigFile.new()
	for scene_id in _seen_upto:
		cfg.set_value("seen_upto", scene_id, int(_seen_upto[scene_id]))
	cfg.save(SEEN_PATH)


func _load_seen() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(SEEN_PATH) != OK:
		return
	if cfg.has_section("seen_upto"):
		for key in cfg.get_section_keys("seen_upto"):
			_seen_upto[key] = int(cfg.get_value("seen_upto", key, -1))


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
	unlocked_changed.emit(key)
	return true


func is_unlocked(key: String) -> bool:
	return _unlocked.has(key)


# ── Internal ──────────────────────────────────────────────────────────────────

func _slot_path(slot: int) -> String:
	if slot == AUTOSAVE_SLOT:
		return SAVE_DIR + "/autosave.json"
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


# ── Substrate gallery migration ───────────────────────────────────────────────
# One-shot pass at startup: for every save slot, infer which substrate
# gallery items the player must have already encountered (based on
# vol/chapter ordering vs each item's unlock_pattern) and mark them seen.
# Idempotent — mark_cg_seen short-circuits on repeats. Cheap (≤8 saves ×
# small index), so we run it every boot rather than gating with a flag.

const _SUBSTRATE_INDEX_PATH := "res://resources/substrates/gallery/_index.json"

func _migrate_substrate_seen_from_saves() -> void:
	if not FileAccess.file_exists(_SUBSTRATE_INDEX_PATH):
		return
	var f := FileAccess.open(_SUBSTRATE_INDEX_PATH, FileAccess.READ)
	if f == null:
		return
	var idx_data: Variant = JSON.parse_string(f.get_as_text())
	if typeof(idx_data) != TYPE_DICTIONARY:
		return
	var items_v: Variant = (idx_data as Dictionary).get("items", [])
	if typeof(items_v) != TYPE_ARRAY:
		return

	for slot in range(0, MAX_SLOTS + 1):
		var save_path := _slot_path(slot)
		if not FileAccess.file_exists(save_path):
			continue
		var save := _read_json(save_path)
		if save.is_empty():
			continue
		var save_scene: String = str(save.get("scene", ""))
		var save_vol: int      = int(save.get("vol", 0))
		var sv: Vector2i = _parse_vol_ch(save_scene)
		# If we couldn't parse vol/ch from the scene id, fall back to the
		# `vol` field (chapter unknown → treat as "very late in volume").
		if sv.x == -1:
			sv = Vector2i(save_vol, 9999)
		for item_v in items_v:
			if typeof(item_v) != TYPE_DICTIONARY:
				continue
			var item: Dictionary = item_v
			var pattern: String = str(item.get("unlock_pattern", ""))
			if pattern == "":
				continue
			# Direct match takes precedence (handles non-volN_chM patterns).
			if save_scene.match(pattern):
				mark_cg_seen("substrate:" + str(item.get("id", "")))
				continue
			# Otherwise compare vol/ch ordering.
			var pv: Vector2i = _parse_vol_ch(pattern)
			if pv.x == -1:
				continue
			if sv.x > pv.x or (sv.x == pv.x and sv.y >= pv.y):
				mark_cg_seen("substrate:" + str(item.get("id", "")))


# Parses "vol5_ch0_xxx" / "vol5_ch0_*" → Vector2i(5, 0). Returns (-1, -1)
# if the prefix doesn't fit the volN_chM pattern.
func _parse_vol_ch(s: String) -> Vector2i:
	var re := RegEx.new()
	re.compile("^vol(\\d+)_ch(\\d+)")
	var m: RegExMatch = re.search(s)
	if m == null:
		return Vector2i(-1, -1)
	return Vector2i(m.get_string(1).to_int(), m.get_string(2).to_int())
