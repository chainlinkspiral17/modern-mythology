# QASnapshot.gd
# ════════════════════════════════════════════════════════════════
# Autoloaded singleton. Listens for Shift+F1 anywhere in the game
# and dumps a complete state snapshot of the current scene to
# user://qa/qa_snapshots.jsonl + a matching PNG screenshot at
# user://qa/qa_<index>.png, AND copies the JSON to clipboard for
# immediate paste into the QA console (godot/tools/qa_console/).
#
# Designed to be silent if systems are missing — every scene gets
# whatever it can. A scene without a MoodCycler still gets a useful
# position + screenshot capture.
#
# The session_id (Unix timestamp at autoload init) is shared across
# every snapshot from one game run, so the HTML console can auto-
# group snapshots into play sessions per day.
# ════════════════════════════════════════════════════════════════
extends Node

const QA_DIR     := "user://qa"
const JSONL_FILE := "user://qa/qa_snapshots.jsonl"
const PNG_FORMAT := "user://qa/qa_%04d.png"

# Distance (m) above which the player is "between" gauntlet spaces;
# we still record the nearest but flag it as approximate.
const GAUNTLET_SPACE_THRESHOLD: float = 2.5

var _session_id: String = ""
var _next_index: int    = 1


func _ready() -> void:
	_session_id = "sess_%d" % int(Time.get_unix_time_from_system())
	DirAccess.make_dir_recursive_absolute(
		ProjectSettings.globalize_path(QA_DIR))
	_next_index = _scan_existing_index()
	set_process_unhandled_input(true)
	print("[QASnapshot] ready · session=%s · next_index=%d"
		% [_session_id, _next_index])


func _scan_existing_index() -> int:
	# Look at the existing JSONL to find the highest snapshot index
	# so restarting Godot doesn't overwrite earlier captures.
	if not FileAccess.file_exists(JSONL_FILE):
		return 1
	var f := FileAccess.open(JSONL_FILE, FileAccess.READ)
	var max_idx := 0
	while not f.eof_reached():
		var line := f.get_line()
		if line == "":
			continue
		var d: Variant = JSON.parse_string(line)
		if typeof(d) == TYPE_DICTIONARY and d.has("index"):
			max_idx = max(max_idx, int(d["index"]))
	f.close()
	return max_idx + 1


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo):
		return
	var k := event as InputEventKey
	# Shift+F1 — the QA snapshot hotkey
	if k.keycode == KEY_F1 and k.shift_pressed and not k.ctrl_pressed and not k.alt_pressed:
		get_viewport().set_input_as_handled()
		capture_snapshot()


# Public API — call this from anywhere (e.g. a future debug-menu
# button) to capture a snapshot without the hotkey.
func capture_snapshot() -> void:
	var snap: Dictionary = _gather_state()
	var idx: int = _next_index
	_next_index += 1
	snap["index"]      = idx
	snap["session_id"] = _session_id
	snap["ts"]         = Time.get_datetime_string_from_system(true)
	var png_path: String = PNG_FORMAT % idx
	snap["screenshot"] = png_path.get_file()
	# Copy JSON to clipboard immediately (single-line for paste)
	var clip_line: String = JSON.stringify(snap)
	DisplayServer.clipboard_set(clip_line)
	print("[QASnapshot] captured #%04d → %s" % [idx, png_path])
	# PNG + JSONL write happen one frame later so the snapshot
	# captures the CURRENT frame (and so the HUD flash below isn't
	# in the picture).
	_save_after_frame(png_path, snap)


func _save_after_frame(png_path: String, snap: Dictionary) -> void:
	await RenderingServer.frame_post_draw
	var img: Image = get_viewport().get_texture().get_image()
	if img != null:
		img.save_png(png_path)
	# Append JSONL line (single-line JSON; the console parses
	# line-by-line)
	var f: FileAccess
	if FileAccess.file_exists(JSONL_FILE):
		f = FileAccess.open(JSONL_FILE, FileAccess.READ_WRITE)
		f.seek_end()
	else:
		f = FileAccess.open(JSONL_FILE, FileAccess.WRITE)
	f.store_line(JSON.stringify(snap))
	f.close()
	_show_flash("QA #%04d" % int(snap["index"]))


# ── State gathering ─────────────────────────────────────────────
func _gather_state() -> Dictionary:
	var scene: Node = get_tree().current_scene
	var out: Dictionary = {
		"scene_path": scene.scene_file_path if scene else "",
		"scene_name": scene.name if scene else "",
	}
	# Player position + camera orientation
	var player := _find_player(scene)
	if player != null:
		var pos: Vector3 = player.global_transform.origin
		out["player_pos_godot"]    = [pos.x, pos.y, pos.z]
		# Blender frame for cross-ref with build scripts
		out["player_pos_blender"]  = [pos.x, -pos.z, pos.y]
		out["player_yaw_rad"]      = player.rotation.y
		out["player_yaw_deg"]      = rad_to_deg(player.rotation.y)
		var cam := player.get_node_or_null("Camera3D") as Camera3D
		if cam != null:
			out["camera_fov"]         = cam.fov
			out["camera_pitch_rad"]   = cam.rotation.x
			out["camera_pitch_deg"]   = rad_to_deg(cam.rotation.x)
			out["camera_global_pos"]  = [
				cam.global_transform.origin.x,
				cam.global_transform.origin.y,
				cam.global_transform.origin.z]
			out["camera_basis_z"]     = [
				cam.global_transform.basis.z.x,
				cam.global_transform.basis.z.y,
				cam.global_transform.basis.z.z]
	# MoodCycler + shader strengths (PostProcess CanvasLayer)
	var post: Node = scene.get_node_or_null("PostProcess") if scene else null
	if post != null:
		if "current_index" in post:
			out["mood_index"] = post.current_index
		if "mood_strata" in post and post.mood_strata is Array:
			var strata: Array = post.mood_strata
			var idx: int = int(out.get("mood_index", -1))
			if idx >= 0 and idx < strata.size():
				out["mood_stratum"] = String(strata[idx])
		if "blend_amount_pct" in post:
			out["blend_amount_pct"] = post.blend_amount_pct
		if "lighting_index" in post:
			out["lighting_index"] = post.lighting_index
		if "style_pack_index" in post:
			out["style_pack_index"] = post.style_pack_index
		# Iterate shader quads
		var shaders: Dictionary = {}
		for child in post.get_children():
			if child is ColorRect and child.material is ShaderMaterial:
				var mat: ShaderMaterial = child.material as ShaderMaterial
				var s: Variant = mat.get_shader_parameter("strength")
				if s != null:
					shaders[child.name] = s
		out["shader_strengths"] = shaders
	# Nearest liminal station (from LiminalProximityController)
	var lim: Node = scene.get_node_or_null("LiminalProximityController") if scene else null
	if lim != null:
		if "_strength" in lim:
			out["liminal_strength"] = lim._strength
		if "_target_type" in lim:
			out["liminal_target_type"] = lim._target_type
	# Current gauntlet space — match player position against the
	# active gauntlet host's SPACE_MAP
	var host: Node = _find_gauntlet_host(scene)
	if host != null and player != null:
		out["gauntlet_host"] = host.name
		var sp_pair := _player_to_space(host, player.global_transform.origin)
		if sp_pair["id"] != "":
			out["gauntlet_space"]            = sp_pair["id"]
			out["gauntlet_space_distance_m"] = sp_pair["distance"]
			out["gauntlet_space_exact"]      = sp_pair["distance"] < GAUNTLET_SPACE_THRESHOLD
	# HUD visible — read directly from the HUD CanvasLayer
	var hud: Node = scene.get_node_or_null("HUD") if scene else null
	if hud != null and "visible" in hud:
		out["hud_visible"] = hud.visible
	return out


func _find_player(scene: Node) -> CharacterBody3D:
	if scene == null:
		return null
	var p := scene.get_node_or_null("Player") as CharacterBody3D
	if p != null:
		return p
	var arr := scene.get_tree().get_nodes_in_group("player")
	if arr.size() > 0 and arr[0] is CharacterBody3D:
		return arr[0] as CharacterBody3D
	return null


func _find_gauntlet_host(scene: Node) -> Node:
	if scene == null:
		return null
	for n in ["DinerGauntletHost", "CathedralGauntletHost",
			  "BungalowGauntletHost", "RiverboatGauntletHost"]:
		var node := scene.get_node_or_null(n)
		if node != null:
			return node
	return null


func _player_to_space(host: Node, ppos: Vector3) -> Dictionary:
	# Use the host's SPACE_MAP to find the closest space id.
	# Entries are [bx, by, yaw_deg] OR [bx, by, bz, yaw_deg] (riverboat).
	if not "SPACE_MAP" in host:
		return {"id": "", "distance": INF}
	var map: Dictionary = host.SPACE_MAP
	if map.is_empty():
		return {"id": "", "distance": INF}
	var best_id := ""
	var best_d: float = INF
	for sid in map.keys():
		var entry: Array = map[sid]
		var bx: float = entry[0]
		var by: float = entry[1]
		var bz: float = 0.0
		if entry.size() >= 4:
			bz = entry[2]
		var spos := Vector3(bx, bz, -by)
		var d: float = (spos - ppos).length()
		if d < best_d:
			best_d = d
			best_id = sid
	return {"id": best_id, "distance": best_d}


# ── HUD flash (post-capture) ────────────────────────────────────
func _show_flash(msg: String) -> void:
	var cl := CanvasLayer.new()
	cl.layer = 200
	var lbl := Label.new()
	lbl.text = msg
	lbl.add_theme_font_size_override("font_size", 22)
	lbl.add_theme_color_override("font_color",
		Color(0.96, 0.92, 0.78, 1))
	lbl.add_theme_color_override("font_outline_color",
		Color(0, 0, 0, 1))
	lbl.add_theme_constant_override("outline_size", 4)
	lbl.position = Vector2(40, 80)
	cl.add_child(lbl)
	get_tree().root.add_child(cl)
	var tw := lbl.create_tween()
	tw.tween_interval(0.9)
	tw.tween_property(lbl, "modulate:a", 0.0, 0.35)
	tw.tween_callback(cl.queue_free)
