extends Node
## Scene + music catalog database. Autoloaded as "SceneDataDB".
## Reads JSON from res://resources/scenes/; user:// overrides take precedence.

const SCENES_BASE  := "res://resources/scenes/"
const SCENES_USER  := "user://scenes/"
const MUSIC_PATH   := "res://resources/music_catalog.json"

var _cache:     Dictionary = {}
var _vol_index: Dictionary = {}
var _music:     Array      = []


func _ready() -> void:
	_load_index()
	_load_music_catalog()


# ── Scene API ─────────────────────────────────────────────────────────────────

func get_scene(scene_id: String) -> Dictionary:
	if _cache.has(scene_id):
		return _cache[scene_id]
	for vol_key: String in _vol_index:
		var list: Array = _vol_index[vol_key]
		if scene_id in list:
			return _load_scene_file(vol_key, scene_id)
	push_warning("SceneDataDB: scene not found: " + scene_id)
	return {}


func get_volume_scenes(vol_num: int) -> Array:
	var key := str(vol_num)
	if not _vol_index.has(key):
		return []
	var out: Array = []
	for scene_id: String in _vol_index[key]:
		var s := get_scene(scene_id)
		if not s.is_empty():
			out.append(s)
	return out


func get_volume_chapters(vol_num: int) -> Array:
	# One entry per unique chapter number, in index.json order.
	# Prefers type="chapter" over type="interlude" so that proper chapter
	# entry points are shown even when interlude subscenes appear first.
	var key := str(vol_num)
	if not _vol_index.has(key):
		return []
	var first_any:     Dictionary = {}
	var first_chapter: Dictionary = {}
	var ch_order:      Array      = []
	for scene_id: String in _vol_index[key]:
		var s := get_scene(scene_id)
		if s.is_empty():
			continue
		var ch_val = s.get("chapter")
		if ch_val == null:
			continue
		var ch_key: String = str(ch_val)
		if not first_any.has(ch_key):
			first_any[ch_key] = s
			ch_order.append(ch_key)
		if s.get("type", "") == "chapter" and not first_chapter.has(ch_key):
			first_chapter[ch_key] = s
	var chapters: Array = []
	for ch_key in ch_order:
		chapters.append(first_chapter.get(ch_key, first_any[ch_key]))
	return chapters


func get_first_scene(vol_num: int) -> Dictionary:
	var chapters := get_volume_chapters(vol_num)
	if chapters.is_empty():
		return {}
	return chapters[0]


func get_next_scene_id(scene_id: String) -> String:
	var flow_vols := ["5", "6", "7"]
	for vi in range(flow_vols.size()):
		var vk := flow_vols[vi]
		if not _vol_index.has(vk):
			continue
		var list: Array = _vol_index[vk]
		var idx: int = list.find(scene_id)
		if idx < 0:
			continue
		if idx < list.size() - 1:
			return list[idx + 1]
		if vi + 1 < flow_vols.size():
			var nk := flow_vols[vi + 1]
			if _vol_index.has(nk) and not _vol_index[nk].is_empty():
				return _vol_index[nk][0]
		return ""
	return ""


func get_all_volumes() -> Array:
	var vols: Array = []
	for key: String in _vol_index:
		vols.append(int(key))
	vols.sort()
	return vols


func get_all_cg_ids() -> Array:
	var cgs: Array = []
	for vol_key: String in _vol_index:
		for scene_id: String in _vol_index[vol_key]:
			var scene := get_scene(scene_id)
			for node: Dictionary in scene.get("nodes", []):
				if node.get("t", "") == "cg":
					var src: String = node.get("src", "")
					if src != "" and src not in cgs:
						cgs.append(src)
	return cgs


# ── Save override (scene editor writes here) ──────────────────────────────────

func save_scene_override(scene_id: String, data: Dictionary) -> bool:
	var vol_key := str(int(data.get("vol", 1)))
	var dir_path := SCENES_USER + "vol" + vol_key + "/"
	DirAccess.make_dir_recursive_absolute(dir_path)
	var path := dir_path + scene_id + ".json"
	var f := FileAccess.open(path, FileAccess.WRITE)
	if not f:
		push_error("SceneDataDB: cannot write override: " + path)
		return false
	f.store_string(JSON.stringify(data, "\t"))
	f.close()
	_cache[scene_id] = data
	return true


func export_scene_to_project(scene_id: String, data: Dictionary) -> bool:
	var vol_key := str(int(data.get("vol", 1)))
	var res_dir := "res://resources/scenes/vol" + vol_key + "/"
	var res_path := res_dir + scene_id + ".json"
	var abs_path := ProjectSettings.globalize_path(res_path)
	var abs_dir  := ProjectSettings.globalize_path(res_dir)
	DirAccess.make_dir_recursive_absolute(abs_dir)
	var f := FileAccess.open(abs_path, FileAccess.WRITE)
	if not f:
		push_error("SceneDataDB: cannot export to project: " + abs_path)
		return false
	f.store_string(JSON.stringify(data, "\t"))
	f.close()
	_cache[scene_id] = data
	return true


# ── Music API ─────────────────────────────────────────────────────────────────

func get_music_catalog() -> Array:
	return _music


func get_music_entry(src: String) -> Dictionary:
	for entry: Dictionary in _music:
		if entry.get("src", "") == src:
			return entry
	return {}


# ── Internal ──────────────────────────────────────────────────────────────────

func _load_index() -> void:
	var path := SCENES_BASE + "index.json"
	var text := _read_file(path)
	if text == "":
		push_warning("SceneDataDB: index.json not found — run tools/import_scenes.py first")
		return
	var parsed = JSON.parse_string(text)
	if parsed is Dictionary:
		_vol_index = parsed as Dictionary
	else:
		push_error("SceneDataDB: failed to parse index.json")


func _load_scene_file(vol_key: String, scene_id: String) -> Dictionary:
	var user_path := SCENES_USER + "vol" + vol_key + "/" + scene_id + ".json"
	var res_path  := SCENES_BASE + "vol" + vol_key + "/" + scene_id + ".json"
	var path := user_path if FileAccess.file_exists(user_path) else res_path
	var text := _read_file(path)
	if text == "":
		push_warning("SceneDataDB: scene file missing: " + res_path)
		return {}
	var parsed = JSON.parse_string(text)
	if parsed is Dictionary:
		var d: Dictionary = parsed as Dictionary
		_cache[scene_id] = d
		return d
	push_error("SceneDataDB: JSON parse error: " + path)
	return {}


func _load_music_catalog() -> void:
	var text := _read_file(MUSIC_PATH)
	if text == "":
		return
	var parsed = JSON.parse_string(text)
	if parsed is Array:
		_music = parsed as Array


func _read_file(path: String) -> String:
	var f := FileAccess.open(path, FileAccess.READ)
	if not f:
		return ""
	var text := f.get_as_text()
	f.close()
	return text
