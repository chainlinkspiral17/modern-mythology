extends Node
## Save slot system. Autoloaded as "SaveSystem".

const SAVE_DIR      := "user://saves"
const GALLERY_PATH  := "user://progress/gallery.cfg"
const UNLOCKS_PATH  := "user://progress/unlocks.cfg"
const MAX_SLOTS     := 8

signal save_written(slot: int)
signal save_deleted(slot: int)
signal unlocked_changed(key: String)

var _seen_cgs:  Dictionary = {}
var _unlocked:  Dictionary = {}

# ── Save-slot thumbnails + notes (2026-10-01) ─────────────────────────
# The user: "The save state should be a thumbnail with a notes section.
# Players can input these notes at any time." Each slot keeps a PNG of
# the scene at the moment it was saved (slot_N.png beside slot_N.json)
# and a free-text "notes" field the player edits from the pause menu
# or the save/load screen whenever they like. Overwriting a slot keeps
# its notes; notes typed before the first save wait in pending_notes
# and land on the first slot written.
const THUMB_W := 384
const THUMB_H := 216
const NOTES_MAX := 2000
var pending_notes: String = ""


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(SAVE_DIR)
	_load_gallery()
	_load_unlocks()
	_migrate_substrate_seen_from_saves()


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
				flags: Dictionary, skills: Dictionary, log: Array,
				thumb: Image = null) -> void:
	# notes belong to the slot, not to one write of it: keep them
	var prev: Dictionary = read_save(slot)
	var notes: String = String(prev.get("notes", ""))
	if notes == "" and pending_notes != "":
		notes = pending_notes
		pending_notes = ""
	var data := {
		"slot":      slot,
		"vol":       vol,
		"ts":        Time.get_unix_time_from_system(),
		"scene":     scene_id,
		"nodeIndex": node_idx,
		"flags":     flags,
		"skills":    skills,
		"log":       log.slice(maxi(0, log.size() - 50)),
		"notes":     notes,
	}
	if thumb != null and not thumb.is_empty():
		var small: Image = thumb.duplicate() as Image
		if small.is_compressed():
			small.decompress()
		small.convert(Image.FORMAT_RGB8)
		small.resize(THUMB_W, THUMB_H, Image.INTERPOLATE_BILINEAR)
		if small.save_png(_thumb_path(slot)) == OK:
			data["thumb"] = _thumb_path(slot).get_file()
	elif bool(prev.has("thumb")) and FileAccess.file_exists(_thumb_path(slot)):
		data["thumb"] = String(prev.get("thumb", ""))
	_write_json(_slot_path(slot), data)
	save_written.emit(slot)


## The player's notes for a slot. slot < 1 (no save yet) holds them in
## pending_notes until the first write.
func get_notes(slot: int) -> String:
	if slot < 1:
		return pending_notes
	var data: Dictionary = read_save(slot)
	return String(data.get("notes", ""))


func set_notes(slot: int, text: String) -> void:
	var t: String = text.substr(0, NOTES_MAX)
	if slot < 1:
		pending_notes = t
		return
	var path := _slot_path(slot)
	if not FileAccess.file_exists(path):
		pending_notes = t
		return
	var data: Dictionary = _read_json(path)
	if data.is_empty():
		return
	data["notes"] = t
	data["notes_ts"] = Time.get_unix_time_from_system()
	_write_json(path, data)


## The slot's thumbnail as a texture, or null when it has none (saves
## from before 2026-10-01, or a write whose capture failed).
func get_thumb(slot: int) -> Texture2D:
	var path := _thumb_path(slot)
	if not FileAccess.file_exists(path):
		return null
	var img: Image = Image.load_from_file(path)
	if img == null or img.is_empty():
		return null
	return ImageTexture.create_from_image(img)


func read_save(slot: int) -> Dictionary:
	var path := _slot_path(slot)
	if not FileAccess.file_exists(path):
		return {}
	return _read_json(path)


func delete_save(slot: int) -> void:
	var path := _slot_path(slot)
	if FileAccess.file_exists(_thumb_path(slot)):
		DirAccess.remove_absolute(_thumb_path(slot))
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
	unlocked_changed.emit(key)
	return true


func is_unlocked(key: String) -> bool:
	return _unlocked.has(key)


# ── Records (2026-09-19) ─────────────────────────────────────────────────────
# Small per-key dictionaries that outlive a run: the gauntlet's
# per-arcana card (runs, wins, best turns). One JSON file beside the
# unlocks; loaded on first use, written on every set.
const RECORDS_PATH := "user://progress/records.json"
var _records: Dictionary = {}
var _records_loaded: bool = false


func get_record(key: String) -> Dictionary:
	_ensure_records()
	var rv: Variant = _records.get(key, {})
	return (rv as Dictionary).duplicate() if rv is Dictionary else {}


func set_record(key: String, data: Dictionary) -> void:
	_ensure_records()
	_records[key] = data.duplicate()
	DirAccess.make_dir_recursive_absolute("user://progress")
	_write_json(RECORDS_PATH, _records)


func _ensure_records() -> void:
	if _records_loaded:
		return
	_records_loaded = true
	_records = _read_json(RECORDS_PATH)


# ── Internal ──────────────────────────────────────────────────────────────────

func _slot_path(slot: int) -> String:
	return SAVE_DIR + "/slot_%d.json" % slot


func _thumb_path(slot: int) -> String:
	return SAVE_DIR + "/slot_%d.png" % slot


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

	for slot in range(1, MAX_SLOTS + 1):
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


## True if any save slot has reached at least (vol, min_chapter). Used
## by the slowstock shelf to gate sticks Tem only acquires late in a
## given volume (e.g. the Tideline Survey 2048, bought in Vol 7 ch 22).
## Scene ids that don't parse fall back to the save's `vol` field at a
## very-late chapter, matching the substrate-migration heuristic above.
func reached_vol_chapter(vol: int, min_chapter: int) -> bool:
	for i in range(1, MAX_SLOTS + 1):
		var save := read_save(i)
		if save.is_empty():
			continue
		var sv: Vector2i = _parse_vol_ch(str(save.get("scene", "")))
		if sv.x == -1:
			sv = Vector2i(int(save.get("vol", 0)), 9999)
		if sv.x > vol or (sv.x == vol and sv.y >= min_chapter):
			return true
	return false
