extends Control
## Camp Sweetgum · overworld · Wave B scaffold.
##
## Loads a zone JSON, renders its tile grid, spawns Sam at a
## named spawn point, and handles four-way tile-grid-locked
## movement with camera follow.  Walking onto a tile marked
## with an `exit` transitions to another zone.
##
## Zone JSON schema (v1):
##   {
##     id, display_name, size: [w,h],
##     tileset: { "<char>": { kind, color, walkable, label?, exit?, interact? } },
##     tiles:   [ "<row_string>", ... ]   // <char> lookups into tileset
##     spawns:  { "<name>": [x, y] }
##   }
##
## Signals up:
##   quit_to_shelf                    — Escape or BACK button
##   zone_changed(zone_id, spawn_id)  — after a transition
##   run_finished(canon_vars, lore_tokens) — Wave B never emits;
##                                     Wave M's ending screen will
##
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal zone_changed(zone_id: String, spawn_id: String)
signal run_finished(canon_vars: Dictionary, lore_tokens: Array)
signal party_changed(party: Array, friendship: Dictionary)
signal day_advanced(day_index: int)
signal facts_discovered(discovered: Array)
signal time_advanced(day_index: int, time_index: int)

# Tag colors for the dialogue-web reactions.
const TAG_COLOR := {
	"knowledge": Color(0.62, 0.82, 0.96, 1.0),   # cool blue
	"curiosity": Color(0.70, 0.94, 0.62, 1.0),   # green
	"insight":   Color(0.94, 0.82, 0.42, 1.0),   # gold
	"aside":     Color(0.62, 0.58, 0.50, 1.0),   # dim gray
}

# Party cap · Sam + 3 others.
const PARTY_CAP := 3
# Wave C-tail dev threshold · design doc says 3, but the anchor
# events that grant friendship land in Waves D+.  Until then the
# friendship gate is lowered so testers can form parties by just
# saying hello.
const INVITE_THRESHOLD := 1

const TILE_PX := 24                # on-screen size of one tile
const CHAR_SPRITE_DIR := "res://resources/games/vol7/pirate_summer/sprites/chars/"
const SAM_SPRITE := CHAR_SPRITE_DIR + "sam.json"
const ZONE_DIR := "res://resources/games/vol7/pirate_summer/zones/"
const CAMPERS_PATH := "res://resources/games/vol7/pirate_summer/campers.json"
const DAYS_PATH := "res://resources/games/vol7/pirate_summer/days.json"
const DIALOGUE_WEB_PATH := "res://resources/games/vol7/pirate_summer/dialogue_web.json"
const PARTY_CHATTER_PATH := "res://resources/games/vol7/pirate_summer/party_chatter.json"
const SCHEDULE_PATH := "res://resources/games/vol7/pirate_summer/schedule.json"

# Chatter fires every CHATTER_STEP_INTERVAL successful moves, rotating
# through the party.  Tuned to feel like natural conversation while
# walking — one line every ~8-12 tiles.
const CHATTER_STEP_INTERVAL := 10
# Chatter balloon fades after CHATTER_LIFETIME seconds.
const CHATTER_LIFETIME := 6.0

# Mood color palette · chatter balloon border tints by the speaker's
# mood.  Matches the dialogue-web tag palette in feel but different
# hues so the two systems don't blur together.
const MOOD_COLOR := {
	"curious":   Color(0.72, 0.94, 0.72, 1.0),  # green
	"wistful":   Color(0.72, 0.86, 0.94, 1.0),  # soft blue
	"restless":  Color(0.96, 0.82, 0.42, 1.0),  # yellow-orange
	"calm":      Color(0.80, 0.78, 0.72, 1.0),  # warm gray
	"teasing":   Color(0.96, 0.70, 0.86, 1.0),  # pink
}

# Movement · one step per tile · with a short slide so it reads
# smoother than a hard cut.
const STEP_SECONDS := 0.14

const C_BG        := Color(0.024, 0.020, 0.014, 1.0)
const C_ACCENT    := Color(0.78, 0.66, 0.29, 1.00)
const C_TXT       := Color(0.83, 0.79, 0.69, 1.00)
const C_TXT_DIM   := Color(0.50, 0.47, 0.38, 1.00)

# Loaded zone.
var _zone: Dictionary = {}
var _tileset: Dictionary = {}
var _grid: Array = []              # Array[Array[String]] of char codes
var _grid_w: int = 0
var _grid_h: int = 0

# Sam state.
var _sam_x: int = 0
var _sam_y: int = 0
var _sam_facing: String = "down"
var _sam_texture_rect: TextureRect = null
var _sam_moving: bool = false
var _sam_move_tween: Tween = null

# NPCs in current zone.  Keyed by camper_id → { pos: Vector2i, node: TextureRect }.
var _npcs: Dictionary = {}
# Campers table (loaded once).
var _campers_by_id: Dictionary = {}
# Days table (loaded once).
var _days: Array = []

# Dialogue-web tables (loaded once).
var _facts_by_id: Dictionary = {}                      # fact_id → def
var _reactions_by_character: Dictionary = {}           # char_id → Array[reaction]
var _hello_grants: Dictionary = {}                     # char_id → fact_id

# Schedule table (loaded once).
var _schedule_blocks: Array = []
var _schedule_day_activities: Dictionary = {}

# Party chatter · full authored pool (loaded once) and per-run
# rotation state.  _chatter_speaker_cursor rotates through the party
# so the same person doesn't dominate the walk.
var _chatter_pool: Array = []
var _chatter_speaker_cursor: int = 0
var _steps_since_chatter: int = 0
var _chatter_balloon: Panel = null
var _chatter_balloon_timer: SceneTreeTimer = null

# Day-intro modal (shown on wake up / sleep interact).
var _day_modal: Panel = null
var _day_modal_open: bool = false

# Dialogue box · null unless open.  While open, movement is blocked.
var _dialogue_panel: Panel = null
var _dialogue_open: bool = false
# Roster panel (TAB).
var _roster_panel: Panel = null
var _roster_open: bool = false
# Which campers Sam has said hello to at least once this run · avoids
# repeatedly farming friendship from the same greeting.
var _greeted: Dictionary = {}

# Camera / render nodes.
var _world_root: Node2D = null     # holds tiles + Sam · we translate this for camera follow
var _hud_layer: CanvasLayer = null
var _zone_label: Label = null
var _day_label: Label = null
var _hover_label: Label = null
var _prompt_label: Label = null

# Run state carried in from host.
var _run_state: Dictionary = {}


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	set_process(true)
	set_process_input(true)
	_load_campers()
	_load_days()
	_load_dialogue_web()
	_load_chatter()
	_load_schedule()
	_build_hud()


func _load_schedule() -> void:
	if not FileAccess.file_exists(SCHEDULE_PATH): return
	var f := FileAccess.open(SCHEDULE_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		_schedule_blocks = (parsed as Dictionary).get("blocks", [])
		var d: Variant = (parsed as Dictionary).get("day_activity_zones", {})
		_schedule_day_activities = d if d is Dictionary else {}


func _load_chatter() -> void:
	if not FileAccess.file_exists(PARTY_CHATTER_PATH): return
	var f := FileAccess.open(PARTY_CHATTER_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		_chatter_pool = (parsed as Dictionary).get("chatter", [])


func _load_dialogue_web() -> void:
	if not FileAccess.file_exists(DIALOGUE_WEB_PATH): return
	var f := FileAccess.open(DIALOGUE_WEB_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if not (parsed is Dictionary): return
	var w: Dictionary = parsed
	for fact_v in w.get("facts", []):
		var fact: Dictionary = fact_v
		_facts_by_id[String(fact.get("id", ""))] = fact
	for r_v in w.get("reactions", []):
		var r: Dictionary = r_v
		var cid := String(r.get("character", ""))
		if not _reactions_by_character.has(cid):
			_reactions_by_character[cid] = []
		(_reactions_by_character[cid] as Array).append(r)
	var hg: Variant = w.get("hello_grants", {})
	_hello_grants = hg if hg is Dictionary else {}


func _load_days() -> void:
	if not FileAccess.file_exists(DAYS_PATH): return
	var f := FileAccess.open(DAYS_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		_days = (parsed as Dictionary).get("days", [])


func _load_campers() -> void:
	if not FileAccess.file_exists(CAMPERS_PATH): return
	var f := FileAccess.open(CAMPERS_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if not (parsed is Dictionary): return
	for c_var in (parsed as Dictionary).get("campers", []):
		var c: Dictionary = c_var
		_campers_by_id[String(c.get("id", ""))] = c


func boot(host_state: Dictionary) -> void:
	_run_state = host_state
	var zone_id := String(host_state.get("zone", "cabin_sturgeon"))
	var spawn_id := String(host_state.get("spawn", "start"))
	_load_zone(zone_id, spawn_id)
	# On very first boot of a fresh run (day 0 and no zone changes
	# recorded), show the Sunday intro narration so the player lands
	# in the fiction, not just the tile grid.
	if int(_run_state.get("day_index", 0)) == 0 and not bool(_run_state.get("sunday_intro_shown", false)):
		_run_state["sunday_intro_shown"] = true
		# Sunday seed facts · the umbrella facts every character can
		# comment on from turn one.
		_discover_fact("sam_at_camp_sweetgum")
		_discover_fact("wilson_ashe_is_the_new_counselor")
		_discover_fact("wilson_has_a_bag_he_doesnt_put_down")
		_discover_fact("something_about_wilson_is_off")
		call_deferred("_show_day_intro_modal")


# ─── Zone load + render ──────────────────────────────────────────

func _load_zone(zone_id: String, spawn_id: String) -> void:
	var path := ZONE_DIR + zone_id + ".json"
	if not FileAccess.file_exists(path):
		push_warning("[CampOverworld] missing zone %s" % path)
		return
	var f := FileAccess.open(path, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if not (parsed is Dictionary):
		push_warning("[CampOverworld] zone parse failed %s" % path)
		return
	_zone = parsed
	_tileset = _zone.get("tileset", {})
	var size_v: Array = _zone.get("size", [0, 0])
	_grid_w = int(size_v[0]) if size_v.size() >= 2 else 0
	_grid_h = int(size_v[1]) if size_v.size() >= 2 else 0
	_grid = []
	for row_v in _zone.get("tiles", []):
		var s := String(row_v)
		var row_chars: Array = []
		for i in range(s.length()):
			row_chars.append(s.substr(i, 1))
		_grid.append(row_chars)
	# Rebuild the world root.
	if _world_root != null and is_instance_valid(_world_root):
		_world_root.queue_free()
	_world_root = Node2D.new()
	add_child(_world_root)
	move_child(_world_root, 0)   # under the HUD
	_render_grid()
	_spawn_sam(spawn_id)
	_spawn_npcs()
	_update_zone_label()
	_recenter_camera()


func _spawn_npcs() -> void:
	_npcs.clear()
	for entry_v in _zone.get("npcs", []):
		var entry: Dictionary = entry_v
		var cid := String(entry.get("camper", ""))
		var pos_a: Array = entry.get("pos", [0, 0])
		if cid == "" or pos_a.size() < 2: continue
		var sprite := SlowstockSprite.new()
		var sprite_path := CHAR_SPRITE_DIR + cid + ".json"
		if not sprite.load_from(sprite_path):
			# Fall back to Sam's sprite so a missing NPC sprite doesn't
			# break the zone · they'll just look wrong.
			if not sprite.load_from(SAM_SPRITE):
				continue
		var tr := TextureRect.new()
		tr.texture = sprite.texture()
		var upscale := 1.5
		tr.size = Vector2(sprite.w * upscale, sprite.h * upscale)
		tr.stretch_mode = TextureRect.STRETCH_KEEP
		tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var nx: int = int(pos_a[0])
		var ny: int = int(pos_a[1])
		var tile_center := Vector2(nx * TILE_PX + TILE_PX / 2.0,
		                           ny * TILE_PX + TILE_PX / 2.0)
		tr.position = Vector2(tile_center.x - tr.size.x / 2.0,
		                      tile_center.y - tr.size.y + TILE_PX / 2.0 + 2)
		_world_root.add_child(tr)
		_npcs[cid] = { "pos": Vector2i(nx, ny), "node": tr }


func _render_grid() -> void:
	for y in range(_grid_h):
		for x in range(_grid_w):
			var ch: String = _grid[y][x] if y < _grid.size() and x < _grid[y].size() else "."
			var def: Dictionary = _tileset.get(ch, {})
			var color := Color(0.2, 0.2, 0.2, 1.0)
			if def.has("color"):
				color = Color(String(def["color"]))
			var r := ColorRect.new()
			r.color = color
			r.size = Vector2(TILE_PX, TILE_PX)
			r.position = Vector2(x * TILE_PX, y * TILE_PX)
			r.mouse_filter = Control.MOUSE_FILTER_IGNORE
			_world_root.add_child(r)


func _spawn_sam(spawn_id: String) -> void:
	var sp: Array = _zone.get("spawns", {}).get(spawn_id, [0, 0])
	_sam_x = int(sp[0]) if sp.size() >= 2 else 0
	_sam_y = int(sp[1]) if sp.size() >= 2 else 0
	# Sprite.
	var sprite := SlowstockSprite.new()
	if not sprite.load_from(CHAR_SPRITE_PATH):
		return
	_sam_texture_rect = TextureRect.new()
	_sam_texture_rect.texture = sprite.texture()
	# Upscale 1.5× so the 16×24 native reads well against 24-px tiles.
	var upscale := 1.5
	_sam_texture_rect.size = Vector2(sprite.w * upscale, sprite.h * upscale)
	_sam_texture_rect.stretch_mode = TextureRect.STRETCH_KEEP
	_sam_texture_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_place_sam()
	_world_root.add_child(_sam_texture_rect)


func _place_sam() -> void:
	if _sam_texture_rect == null: return
	# Position so Sam's feet land in the tile center.
	var tile_center := Vector2(_sam_x * TILE_PX + TILE_PX / 2.0,
	                           _sam_y * TILE_PX + TILE_PX / 2.0)
	_sam_texture_rect.position = Vector2(
		tile_center.x - _sam_texture_rect.size.x / 2.0,
		tile_center.y - _sam_texture_rect.size.y + TILE_PX / 2.0 + 2)


func _recenter_camera() -> void:
	# Pin the world root so Sam sits at screen center.
	if _sam_texture_rect == null or _world_root == null: return
	var sam_center := _sam_texture_rect.position + Vector2(
		_sam_texture_rect.size.x / 2.0, _sam_texture_rect.size.y / 2.0)
	var screen := get_viewport_rect().size
	_world_root.position = screen / 2.0 - sam_center


# ─── HUD (F4-compliant · lives in a CanvasLayer) ─────────────────

func _build_hud() -> void:
	_hud_layer = CanvasLayer.new()
	add_child(_hud_layer)
	_hud_layer.visible = FirstPersonController.hud_visible

	var top := HBoxContainer.new()
	top.offset_left = 16
	top.offset_top = 8
	top.offset_right = 800
	top.offset_bottom = 32
	top.add_theme_constant_override("separation", 16)
	_hud_layer.add_child(top)

	_zone_label = Label.new()
	_zone_label.add_theme_font_size_override("font_size", 12)
	_zone_label.add_theme_color_override("font_color", C_ACCENT)
	top.add_child(_zone_label)

	_day_label = Label.new()
	_day_label.add_theme_font_size_override("font_size", 11)
	_day_label.add_theme_color_override("font_color", C_TXT_DIM)
	top.add_child(_day_label)

	# Right-side back button in its own container.
	var right_wrap := Control.new()
	right_wrap.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	right_wrap.offset_left = -140
	right_wrap.offset_right = -16
	right_wrap.offset_top = 8
	right_wrap.offset_bottom = 32
	_hud_layer.add_child(right_wrap)

	var back := Button.new()
	back.text = "  ✕  BACK  "
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	back.pressed.connect(func() -> void: quit_to_shelf.emit())
	right_wrap.add_child(back)

	# Bottom hover-label · shows the label of the tile Sam is facing.
	var bot := Control.new()
	bot.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	bot.offset_top = -48
	bot.offset_bottom = -12
	bot.offset_left = 16
	bot.offset_right = -16
	_hud_layer.add_child(bot)

	_hover_label = Label.new()
	_hover_label.add_theme_font_size_override("font_size", 11)
	_hover_label.add_theme_color_override("font_color", C_TXT_DIM)
	_hover_label.set_anchors_preset(Control.PRESET_FULL_RECT)
	bot.add_child(_hover_label)

	_prompt_label = Label.new()
	_prompt_label.text = "  arrows / WASD · move  ·  space · interact  ·  esc · back  "
	_prompt_label.add_theme_font_size_override("font_size", 9)
	_prompt_label.add_theme_color_override("font_color", C_TXT_DIM)
	_prompt_label.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	_prompt_label.offset_left = -320
	_prompt_label.offset_right = -160
	_prompt_label.offset_top = 8
	_prompt_label.offset_bottom = 24
	_hud_layer.add_child(_prompt_label)


func _update_zone_label() -> void:
	if _zone_label != null:
		_zone_label.text = "PIRATE SUMMER · " + String(_zone.get("display_name", _zone.get("id", ""))).to_upper()
	if _day_label != null:
		_day_label.text = "  ·  " + _current_day_display_name() + "  ·  " + _current_block_label()


func _current_block() -> Dictionary:
	var i: int = int(_run_state.get("time_index", 0))
	if i < 0 or i >= _schedule_blocks.size(): return {}
	return _schedule_blocks[i]


func _current_block_label() -> String:
	var b := _current_block()
	if b.is_empty(): return ""
	return String(b.get("start", "?")) + " · " + String(b.get("label", "?"))


func _current_block_id() -> String:
	var b := _current_block()
	return String(b.get("id", ""))


func _advance_time_block() -> void:
	var i: int = int(_run_state.get("time_index", 0))
	if i >= _schedule_blocks.size() - 1:
		# End of the day arrived · nudge the player to sleep in the
		# cabin.  Sleeping is the day-advance, not a time-block one.
		_show_transient("  It's lights-out.  Head back to your bunk to sleep.")
		return
	_run_state["time_index"] = i + 1
	time_advanced.emit(int(_run_state.get("day_index", 0)), i + 1)
	_update_zone_label()
	# When the new block is a meal / activity, nudge the player.
	var block := _current_block()
	var loc := String(block.get("location_hint", ""))
	match loc:
		"mess_hall":
			_show_transient("  · " + String(block.get("label", "")) + " · everyone is heading to the mess hall.")
		"activity_zone_am", "activity_zone_pm":
			var zone_target := _activity_zone_for_current_block()
			if zone_target != "":
				_show_transient("  · " + String(block.get("label", "")) + " · today's activity is at " + zone_target.replace("_", " ") + ".")
			else:
				_show_transient("  · " + String(block.get("label", "")) + " · free · nothing scheduled.")
		"scatter":
			_show_transient("  · free time · everyone is doing their own thing.")
		"campfire_ring":
			_show_transient("  · " + String(block.get("label", "")) + " · " + _current_day().get("anchor_event_summary", ""))
		_:
			_show_transient("  · " + String(block.get("label", "")))


func _activity_zone_for_current_block() -> String:
	var day := _current_day()
	if day.is_empty(): return ""
	var day_name := String(day.get("name", ""))
	var per_day: Dictionary = _schedule_day_activities.get(day_name, {})
	var block_id := _current_block_id()
	var target: Variant = per_day.get(block_id, null)
	if target is String: return target
	return ""


func _current_day() -> Dictionary:
	var i: int = int(_run_state.get("day_index", 0))
	if i < 0 or i >= _days.size(): return {}
	return _days[i]


func _current_day_display_name() -> String:
	var d := _current_day()
	if d.is_empty(): return "DAY ?"
	return String(d.get("display_name", "day " + str(d.get("index", 0))))


func _update_hover_label() -> void:
	if _hover_label == null: return
	var face_delta := _facing_delta()
	var tx: int = _sam_x + int(face_delta.x)
	var ty: int = _sam_y + int(face_delta.y)
	# NPC in front takes label priority.
	var cid := _npc_at(tx, ty)
	if cid != "":
		var c: Dictionary = _campers_by_id.get(cid, {})
		_hover_label.text = "  " + String(c.get("display_name", cid)) + "  ·  press space to talk"
		return
	var def := _tile_def_at(tx, ty)
	var label := String(def.get("label", ""))
	if label == "":
		_hover_label.text = ""
	else:
		_hover_label.text = "  " + label


func _facing_delta() -> Vector2i:
	match _sam_facing:
		"up":    return Vector2i(0, -1)
		"down":  return Vector2i(0, 1)
		"left":  return Vector2i(-1, 0)
		"right": return Vector2i(1, 0)
	return Vector2i.ZERO


func _tile_def_at(x: int, y: int) -> Dictionary:
	if x < 0 or y < 0 or y >= _grid.size() or x >= _grid[y].size():
		return {}
	var ch: String = _grid[y][x]
	return _tileset.get(ch, {})


# ─── Input · four-way movement + interact ────────────────────────

func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			if _day_modal_open:
				_close_day_modal()
			elif _dialogue_open:
				_close_dialogue()
			elif _roster_open:
				_close_roster()
			else:
				quit_to_shelf.emit()
			get_viewport().set_input_as_handled()
			return
		if _day_modal_open:
			if kev.keycode == KEY_SPACE or kev.keycode == KEY_ENTER:
				_close_day_modal()
				get_viewport().set_input_as_handled()
			return
		if kev.keycode == KEY_TAB:
			_toggle_roster()
			get_viewport().set_input_as_handled()
			return
		if _dialogue_open or _roster_open: return
		if _sam_moving: return
		var dx := 0
		var dy := 0
		if kev.keycode == KEY_UP or kev.keycode == KEY_W:
			dy = -1; _sam_facing = "up"
		elif kev.keycode == KEY_DOWN or kev.keycode == KEY_S:
			dy = 1; _sam_facing = "down"
		elif kev.keycode == KEY_LEFT or kev.keycode == KEY_A:
			dx = -1; _sam_facing = "left"
		elif kev.keycode == KEY_RIGHT or kev.keycode == KEY_D:
			dx = 1; _sam_facing = "right"
		elif kev.keycode == KEY_SPACE or kev.keycode == KEY_E:
			_interact_forward()
			return
		if dx == 0 and dy == 0:
			_update_hover_label()
			return
		_try_move(dx, dy)


func _try_move(dx: int, dy: int) -> void:
	if _dialogue_open: return
	var nx := _sam_x + dx
	var ny := _sam_y + dy
	var def := _tile_def_at(nx, ny)
	if def.is_empty():
		_update_hover_label()
		return
	if not bool(def.get("walkable", false)):
		_update_hover_label()
		return
	# Blocked by any NPC standing on the target tile.
	if _npc_at(nx, ny) != "":
		_update_hover_label()
		return
	_sam_x = nx
	_sam_y = ny
	_sam_moving = true
	# Kill any prior tween to avoid stacking.
	if _sam_move_tween != null and _sam_move_tween.is_valid():
		_sam_move_tween.kill()
	_sam_move_tween = create_tween()
	var target_pos := Vector2(_sam_x * TILE_PX + TILE_PX / 2.0 - _sam_texture_rect.size.x / 2.0,
		_sam_y * TILE_PX + TILE_PX / 2.0 - _sam_texture_rect.size.y + TILE_PX / 2.0 + 2)
	_sam_move_tween.tween_property(_sam_texture_rect, "position", target_pos, STEP_SECONDS)
	_sam_move_tween.parallel().tween_method(_tween_camera, 0.0, 1.0, STEP_SECONDS)
	_sam_move_tween.finished.connect(_on_move_finished)


func _tween_camera(_t: float) -> void:
	_recenter_camera()


func _on_move_finished() -> void:
	_sam_moving = false
	# Trigger an exit if the tile we landed on has one.
	var def := _tile_def_at(_sam_x, _sam_y)
	var exit_v: Variant = def.get("exit", null)
	if exit_v is Dictionary:
		var ex: Dictionary = exit_v
		var zid := String(ex.get("zone", ""))
		var sid := String(ex.get("spawn", ""))
		if zid != "":
			zone_changed.emit(zid, sid)
			_load_zone(zid, sid)
			return
	_update_hover_label()
	_tick_party_chatter()


# ── Party chatter ─────────────────────────────────────────────

func _tick_party_chatter() -> void:
	_steps_since_chatter += 1
	if _steps_since_chatter < CHATTER_STEP_INTERVAL: return
	# Modals suppress chatter · party stays quiet during dialogue,
	# roster, or day-intro views.
	if _dialogue_open or _roster_open or _day_modal_open: return
	var party: Array = _party()
	if party.is_empty(): return
	# Round-robin through the party, up to N attempts so we don't
	# spin if nobody has anything eligible left.
	var attempts: int = party.size()
	while attempts > 0:
		attempts -= 1
		var cid: String = String(party[_chatter_speaker_cursor % party.size()])
		_chatter_speaker_cursor += 1
		var line := _pick_chatter_for(cid)
		if not line.is_empty():
			_steps_since_chatter = 0
			_show_chatter(cid, line)
			return


func _pick_chatter_for(cid: String) -> Dictionary:
	var used: Array = _used_chatter_ids()
	var party: Array = _party()
	var eligible: Array = []
	var zone_id := String(_zone.get("id", ""))
	var day_idx: int = int(_run_state.get("day_index", 0))
	for entry_v in _chatter_pool:
		var e: Dictionary = entry_v
		if String(e.get("character", "")) != cid: continue
		var eid := String(e.get("id", ""))
		if used.has(eid): continue
		# Gossip auto-gate · don't gossip about someone in the party.
		var subject := String(e.get("subject", ""))
		if subject != "" and party.has(subject): continue
		# Conditions.
		var cond: Dictionary = e.get("conditions", {})
		if not cond.is_empty():
			var zone_req := String(cond.get("zone_id", ""))
			if zone_req != "" and zone_req != zone_id: continue
			var iwp := String(cond.get("in_party_with", ""))
			if iwp != "" and not party.has(iwp): continue
			var fact_req := String(cond.get("requires_fact", ""))
			if fact_req != "" and not _has_fact(fact_req): continue
			var dmin: int = int(cond.get("day_min", -1))
			if dmin >= 0 and day_idx < dmin: continue
			var dmax: int = int(cond.get("day_max", -1))
			if dmax >= 0 and day_idx > dmax: continue
		eligible.append(e)
	if eligible.is_empty(): return {}
	return eligible[randi() % eligible.size()]


func _used_chatter_ids() -> Array:
	var v: Variant = _run_state.get("used_chatter_ids", [])
	return v if v is Array else []


func _mark_chatter_used(eid: String) -> void:
	var arr: Array = _used_chatter_ids()
	if arr.has(eid): return
	arr.append(eid)
	_run_state["used_chatter_ids"] = arr
	facts_discovered.emit(_discovered_facts())    # piggyback the save · chatter state rides the same signal


func _show_chatter(cid: String, entry: Dictionary) -> void:
	if _chatter_balloon != null and is_instance_valid(_chatter_balloon):
		_chatter_balloon.queue_free()
	var c: Dictionary = _campers_by_id.get(cid, {})
	var mood := String(entry.get("mood", "calm"))
	var color: Color = MOOD_COLOR.get(mood, C_TXT)
	var panel := Panel.new()
	panel.custom_minimum_size = Vector2(560, 60)
	panel.size = panel.custom_minimum_size
	panel.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	panel.offset_left = 40
	panel.offset_right = -40
	panel.offset_top = -108
	panel.offset_bottom = -48
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.020, 0.018, 0.014, 0.92)
	sb.border_color = color
	sb.set_border_width_all(1)
	sb.content_margin_left = 14
	sb.content_margin_right = 14
	sb.content_margin_top = 6
	sb.content_margin_bottom = 6
	panel.add_theme_stylebox_override("panel", sb)
	_hud_layer.add_child(panel)
	_chatter_balloon = panel

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.add_theme_constant_override("separation", 2)
	panel.add_child(v)

	var name_lbl := Label.new()
	name_lbl.text = String(c.get("display_name", cid)) + "  ·  " + mood
	name_lbl.add_theme_font_size_override("font_size", 10)
	name_lbl.add_theme_color_override("font_color", color)
	v.add_child(name_lbl)

	var line_lbl := RichTextLabel.new()
	line_lbl.bbcode_enabled = true
	line_lbl.fit_content = true
	line_lbl.custom_minimum_size = Vector2(520, 24)
	line_lbl.add_theme_font_size_override("normal_font_size", 11)
	line_lbl.add_theme_color_override("default_color", C_TXT)
	line_lbl.append_text(String(entry.get("line", "")))
	v.add_child(line_lbl)

	_mark_chatter_used(String(entry.get("id", "")))
	_chatter_balloon_timer = get_tree().create_timer(CHATTER_LIFETIME)
	_chatter_balloon_timer.timeout.connect(func() -> void:
		if _chatter_balloon == panel and is_instance_valid(panel):
			panel.queue_free()
			_chatter_balloon = null)


func _interact_forward() -> void:
	if _dialogue_open: return
	var d := _facing_delta()
	var fx: int = _sam_x + int(d.x)
	var fy: int = _sam_y + int(d.y)
	# NPC first · they take priority over a tile beneath them.
	var cid := _npc_at(fx, fy)
	if cid != "":
		_open_dialogue(cid)
		return
	var def := _tile_def_at(fx, fy)
	if def.is_empty(): return
	var interact := String(def.get("interact", ""))
	var label := String(def.get("label", ""))
	if interact == "sleep":
		_sleep_and_advance_day()
	elif interact == "duffel":
		if _has_fact("sam_has_northwind_harbor_cart"):
			_show_transient("  Your duffel · Northwind Harbor is still in there.  You'll boot it after dinner.")
		else:
			_discover_fact("sam_has_northwind_harbor_cart")
	elif interact == "eat":
		_do_meal()
	elif interact == "swim":
		_do_activity("swim", "BODY")
	elif interact == "canoe":
		_do_activity("canoe", "BODY")
	elif interact == "bulletin_board":
		_read_bulletin_board()
	elif label != "":
		_show_transient("  " + label)


func _do_meal() -> void:
	var block_id := _current_block_id()
	var block := _current_block()
	# Only meals during meal blocks count.
	if block_id in ["breakfast", "lunch", "dinner"]:
		_show_transient("  You ate " + String(block.get("label", "a meal")) + " with the campers who showed up.")
		# Meal advances time.  Bump friendship with each party member
		# for shared meals · shared bench, shared plate.
		for cid in _party():
			_bump_friendship(String(cid), 1)
		_advance_time_block()
	else:
		_show_transient("  Nothing to eat here right now.  Kitchen opens at the next meal.")


func _do_activity(kind: String, stat: String) -> void:
	var block_id := _current_block_id()
	var block := _current_block()
	if not (block_id in ["morning_activity", "afternoon_activity", "free_time"]):
		_show_transient("  You can't do that right now · " + String(block.get("label", "not activity time")) + ".")
		return
	# Party members with a matching stat_spike get +1 friendship for
	# doing it with Sam.
	for cid in _party():
		var c: Dictionary = _campers_by_id.get(String(cid), {})
		if String(c.get("stat_spike", "")) == stat:
			_bump_friendship(String(cid), 1)
	# Sam's own stat bump.
	var stats: Dictionary = _run_state.get("stats", {})
	var key := stat.to_lower()
	stats[key] = int(stats.get(key, 2)) + 1
	_run_state["stats"] = stats
	_show_transient("  You " + kind + "ed with the group.  " + stat + " up.")
	_advance_time_block()


func _read_bulletin_board() -> void:
	# Wave G ships a static read.  Wave N will populate this with
	# cross-Oneironautics lore fliers (Mrs. Wu's Garden open house,
	# tide chart, camp yearbook table of contents, etc.).
	_show_transient("  · bulletin board · pinned: today's schedule, the tide chart, a flier for a Mrs. Wu's Garden open house in Corvallis (Fall '95)")
	if not _has_fact("mrs_wu_garden_flier_on_bulletin_board"):
		# Announce the fact only if we've authored it in dialogue_web ·
		# for Wave G scaffold we don't · Wave N adds it.
		pass


func _sleep_and_advance_day() -> void:
	var cur: int = int(_run_state.get("day_index", 0))
	if cur >= _days.size() - 1:
		_show_transient("  It's Saturday.  You're going home today.  You don't sleep in on the last day.")
		return
	_run_state["day_index"] = cur + 1
	_run_state["time_index"] = 0
	# Clear the greet-once cache each morning so hellos can register
	# a friendship tick on each new day (design doc: talking every
	# day nudges).
	_greeted.clear()
	day_advanced.emit(cur + 1)
	time_advanced.emit(cur + 1, 0)
	_update_zone_label()
	_show_day_intro_modal()


func _npc_at(x: int, y: int) -> String:
	for cid_v in _npcs.keys():
		var cid: String = String(cid_v)
		var p: Vector2i = _npcs[cid].get("pos", Vector2i(-1, -1))
		if p.x == x and p.y == y:
			return cid
	return ""


func _open_dialogue(camper_id: String) -> void:
	var c: Dictionary = _campers_by_id.get(camper_id, {})
	if c.is_empty(): return
	_dialogue_open = true
	# First-time greeting grants +1 friendship AND discovers this
	# camper's signature fact (their hello line contains it).
	if not _greeted.get(camper_id, false):
		_greeted[camper_id] = true
		_bump_friendship(camper_id, 1)
		var hg: String = String(_hello_grants.get(camper_id, ""))
		if hg != "":
			_discover_fact(hg)
	# Face Sam toward the NPC (helpful when they came at the NPC from
	# a diagonal in a later movement scheme; today it's always forward).
	if _dialogue_panel != null and is_instance_valid(_dialogue_panel):
		_dialogue_panel.queue_free()
	var panel := Panel.new()
	panel.custom_minimum_size = Vector2(680, 360)
	panel.size = panel.custom_minimum_size
	panel.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	panel.offset_left = 40
	panel.offset_right = -40
	panel.offset_top = -380
	panel.offset_bottom = -20
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.030, 0.026, 0.020, 0.98)
	sb.border_color = C_ACCENT
	sb.set_border_width_all(1)
	sb.content_margin_left = 20
	sb.content_margin_right = 20
	sb.content_margin_top = 12
	sb.content_margin_bottom = 12
	panel.add_theme_stylebox_override("panel", sb)
	_hud_layer.add_child(panel)
	_dialogue_panel = panel

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.add_theme_constant_override("separation", 6)
	panel.add_child(v)

	var name_lbl := Label.new()
	name_lbl.text = String(c.get("display_name", camper_id)).to_upper() + "  ·  age " + str(int(c.get("age", 0)))
	name_lbl.add_theme_font_size_override("font_size", 13)
	name_lbl.add_theme_color_override("font_color", C_ACCENT)
	v.add_child(name_lbl)

	var knack: String = String(c.get("knack", ""))
	if knack != "":
		var knack_lbl := Label.new()
		knack_lbl.text = "  KNACK · " + knack
		knack_lbl.add_theme_font_size_override("font_size", 10)
		knack_lbl.add_theme_color_override("font_color", C_TXT_DIM)
		v.add_child(knack_lbl)

	var body := RichTextLabel.new()
	body.bbcode_enabled = true
	body.fit_content = true
	body.custom_minimum_size = Vector2(500, 60)
	body.add_theme_font_size_override("normal_font_size", 11)
	body.add_theme_color_override("default_color", C_TXT)
	body.append_text("\"" + String(c.get("hello_line", "...")) + "\"")
	v.add_child(body)

	# Friendship line.
	var meter := Label.new()
	meter.text = "  friendship · " + _meter_bar(_friendship_of(camper_id))
	meter.add_theme_font_size_override("font_size", 10)
	meter.add_theme_color_override("font_color", C_TXT_DIM)
	v.add_child(meter)

	# Topics · list of facts this character has a reaction to that
	# Sam has discovered.  Empty when no reactions are yet available.
	var topics: Array = _reactions_for(camper_id)
	if not topics.is_empty():
		var topics_hdr := Label.new()
		topics_hdr.text = "  · TALK ABOUT ·"
		topics_hdr.add_theme_font_size_override("font_size", 10)
		topics_hdr.add_theme_color_override("font_color", C_ACCENT)
		v.add_child(topics_hdr)
		var scroll := ScrollContainer.new()
		scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
		scroll.custom_minimum_size = Vector2(640, 120)
		v.add_child(scroll)
		var list := VBoxContainer.new()
		list.add_theme_constant_override("separation", 2)
		scroll.add_child(list)
		for r_v in topics:
			var r: Dictionary = r_v
			var fid := String(r.get("fact", ""))
			var fdef: Dictionary = _facts_by_id.get(fid, {})
			var row := HBoxContainer.new()
			row.add_theme_constant_override("separation", 8)
			list.add_child(row)
			var tag := String(r.get("tag", "aside"))
			var tag_chip := Label.new()
			tag_chip.text = "  " + tag.substr(0, 1).to_upper() + "  "
			tag_chip.add_theme_font_size_override("font_size", 9)
			tag_chip.add_theme_color_override("font_color", TAG_COLOR.get(tag, C_TXT_DIM))
			tag_chip.custom_minimum_size = Vector2(28, 0)
			row.add_child(tag_chip)
			var btn := Button.new()
			btn.text = "  " + String(fdef.get("display", fid))
			btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			btn.add_theme_font_size_override("font_size", 10)
			btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
			var reaction_copy: Dictionary = r.duplicate()
			btn.pressed.connect(func() -> void: _show_reaction(camper_id, reaction_copy))
			row.add_child(btn)

	var actions := HBoxContainer.new()
	actions.alignment = BoxContainer.ALIGNMENT_END
	actions.add_theme_constant_override("separation", 8)
	v.add_child(actions)

	var party: Array = _party()
	var in_party: bool = party.has(camper_id)
	if in_party:
		var leave := Button.new()
		leave.text = "  ← leave party  "
		leave.pressed.connect(func() -> void:
			_remove_from_party(camper_id)
			_close_dialogue())
		actions.add_child(leave)
	else:
		var can_invite: bool = _friendship_of(camper_id) >= INVITE_THRESHOLD and party.size() < PARTY_CAP
		var invite := Button.new()
		invite.text = "  + invite to party  "
		invite.disabled = not can_invite
		if not can_invite:
			if party.size() >= PARTY_CAP:
				invite.text = "  · party full ·  "
			elif _friendship_of(camper_id) < INVITE_THRESHOLD:
				invite.text = "  · not close enough yet ·  "
		invite.pressed.connect(func() -> void:
			_add_to_party(camper_id)
			_close_dialogue())
		actions.add_child(invite)

	var close := Button.new()
	close.text = "  ✕  close  (esc)  "
	close.pressed.connect(_close_dialogue)
	actions.add_child(close)


func _close_dialogue() -> void:
	if _dialogue_panel != null and is_instance_valid(_dialogue_panel):
		_dialogue_panel.queue_free()
	_dialogue_panel = null
	_dialogue_open = false


func _show_reaction(camper_id: String, r: Dictionary) -> void:
	var c: Dictionary = _campers_by_id.get(camper_id, {})
	var fid := String(r.get("fact", ""))
	var fdef: Dictionary = _facts_by_id.get(fid, {})
	# Reuse the dialogue panel · replace its contents.
	if _dialogue_panel == null or not is_instance_valid(_dialogue_panel):
		return
	for child in _dialogue_panel.get_children():
		child.queue_free()

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.add_theme_constant_override("separation", 6)
	_dialogue_panel.add_child(v)

	var hdr := Label.new()
	hdr.text = String(c.get("display_name", camper_id)).to_upper() + "  on  " + String(fdef.get("display", fid))
	hdr.add_theme_font_size_override("font_size", 11)
	hdr.add_theme_color_override("font_color", C_ACCENT)
	hdr.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(hdr)

	var tag := String(r.get("tag", "aside"))
	var tag_lbl := Label.new()
	tag_lbl.text = "  · " + tag + " ·"
	tag_lbl.add_theme_font_size_override("font_size", 10)
	tag_lbl.add_theme_color_override("font_color", TAG_COLOR.get(tag, C_TXT_DIM))
	v.add_child(tag_lbl)

	var body := RichTextLabel.new()
	body.bbcode_enabled = true
	body.fit_content = true
	body.custom_minimum_size = Vector2(620, 180)
	body.add_theme_font_size_override("normal_font_size", 11)
	body.add_theme_color_override("default_color", C_TXT)
	body.append_text("\"" + String(r.get("line", "...")) + "\"")
	v.add_child(body)

	# Fire any unlocks · this is what makes the web grow.
	for uid in r.get("unlocks_fact_ids", []):
		_discover_fact(String(uid))

	var actions := HBoxContainer.new()
	actions.alignment = BoxContainer.ALIGNMENT_END
	actions.add_theme_constant_override("separation", 8)
	v.add_child(actions)

	var back := Button.new()
	back.text = "  ←  back  "
	back.pressed.connect(func() -> void:
		_close_dialogue()
		_open_dialogue(camper_id))
	actions.add_child(back)

	var close := Button.new()
	close.text = "  ✕  close  "
	close.pressed.connect(_close_dialogue)
	actions.add_child(close)


# ── Friendship + party helpers ────────────────────────────────

# ── Dialogue-web state ────────────────────────────────────────

func _discovered_facts() -> Array:
	var d: Variant = _run_state.get("discovered_facts", [])
	return d if d is Array else []


func _has_fact(fid: String) -> bool:
	return _discovered_facts().has(fid)


func _discover_fact(fid: String) -> void:
	if fid == "" or _has_fact(fid): return
	if not _facts_by_id.has(fid): return
	var arr: Array = _discovered_facts()
	arr.append(fid)
	_run_state["discovered_facts"] = arr
	facts_discovered.emit(arr)
	# Transient nudge so the player sees the world's shape grow.
	var f: Dictionary = _facts_by_id[fid]
	_show_transient("  ✻  learned · " + String(f.get("display", fid)))


func _reactions_for(cid: String) -> Array:
	# Return this character's authored reactions filtered by currently-
	# discovered facts (they only speak on things Sam already knows).
	var out: Array = []
	var seen: Dictionary = {}
	for r_v in _reactions_by_character.get(cid, []):
		var r: Dictionary = r_v
		var fid := String(r.get("fact", ""))
		if fid == "" or seen.has(fid): continue
		if not _has_fact(fid): continue
		seen[fid] = true
		out.append(r)
	return out


func _friendship() -> Dictionary:
	var f: Variant = _run_state.get("friendship", {})
	return f if f is Dictionary else {}


func _friendship_of(cid: String) -> int:
	return int(_friendship().get(cid, 0))


func _bump_friendship(cid: String, delta: int) -> void:
	var f: Dictionary = _friendship()
	var cur: int = int(f.get(cid, 0))
	f[cid] = clampi(cur + delta, 0, 5)
	_run_state["friendship"] = f
	party_changed.emit(_party(), f)


func _party() -> Array:
	var p: Variant = _run_state.get("party", [])
	return p if p is Array else []


func _add_to_party(cid: String) -> void:
	var p: Array = _party()
	if p.has(cid) or p.size() >= PARTY_CAP: return
	p.append(cid)
	_run_state["party"] = p
	party_changed.emit(p, _friendship())
	_show_transient("  " + String(_campers_by_id.get(cid, {}).get("display_name", cid)) + " joined the party.")


func _remove_from_party(cid: String) -> void:
	var p: Array = _party()
	if not p.has(cid): return
	p.erase(cid)
	_run_state["party"] = p
	party_changed.emit(p, _friendship())
	_show_transient("  " + String(_campers_by_id.get(cid, {}).get("display_name", cid)) + " left the party.")


func _meter_bar(n: int) -> String:
	# 0..5 → "●●○○○" style bar with colored HTML span, plus /5.
	var full := ""
	var empty := ""
	for i in range(n): full += "●"
	for i in range(5 - n): empty += "○"
	return "%s%s   %d / 5" % [full, empty, n]


# ── Roster panel (TAB) ────────────────────────────────────────

func _toggle_roster() -> void:
	if _roster_open:
		_close_roster()
	else:
		_open_roster()


func _open_roster() -> void:
	if _dialogue_open: return
	if _roster_panel != null and is_instance_valid(_roster_panel):
		_roster_panel.queue_free()
	_roster_open = true
	var panel := Panel.new()
	panel.custom_minimum_size = Vector2(560, 480)
	panel.size = panel.custom_minimum_size
	panel.set_anchors_preset(Control.PRESET_CENTER)
	panel.position = -panel.size / 2.0
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.030, 0.026, 0.020, 0.98)
	sb.border_color = C_ACCENT
	sb.set_border_width_all(1)
	sb.content_margin_left = 20
	sb.content_margin_right = 20
	sb.content_margin_top = 14
	sb.content_margin_bottom = 14
	panel.add_theme_stylebox_override("panel", sb)
	_hud_layer.add_child(panel)
	_roster_panel = panel

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.add_theme_constant_override("separation", 4)
	panel.add_child(v)

	var hdr := Label.new()
	hdr.text = "ROSTER · CAMP SWEETGUM · SUMMER '94"
	hdr.add_theme_font_size_override("font_size", 13)
	hdr.add_theme_color_override("font_color", C_ACCENT)
	v.add_child(hdr)

	var party: Array = _party()
	var party_line := Label.new()
	if party.is_empty():
		party_line.text = "  party · just Sam · walk up to a camper and press space to say hello"
	else:
		var names := PackedStringArray()
		for cid in party:
			names.append(String(_campers_by_id.get(String(cid), {}).get("display_name", cid)))
		party_line.text = "  party · Sam + " + ", ".join(names) + " (%d/%d)" % [party.size(), PARTY_CAP]
	party_line.add_theme_font_size_override("font_size", 10)
	party_line.add_theme_color_override("font_color", C_TXT)
	v.add_child(party_line)

	var facts_line := Label.new()
	facts_line.text = "  facts discovered · %d of %d" % [_discovered_facts().size(), _facts_by_id.size()]
	facts_line.add_theme_font_size_override("font_size", 10)
	facts_line.add_theme_color_override("font_color", C_TXT_DIM)
	v.add_child(facts_line)

	var scroll := ScrollContainer.new()
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(scroll)

	var list := VBoxContainer.new()
	list.add_theme_constant_override("separation", 2)
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(list)

	# Order · Sam skipped, cabin-mates first, others by cabin.
	var order: Array = []
	for cabin in ["sturgeon", "beaver", "osprey", "kestrel"]:
		for cid in _campers_by_id.keys():
			var c: Dictionary = _campers_by_id[cid]
			if String(c.get("id", "")) == "sam": continue
			if String(c.get("cabin", "")) == cabin:
				order.append(cid)

	for cid_v in order:
		var cid: String = String(cid_v)
		var c: Dictionary = _campers_by_id[cid]
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 8)
		list.add_child(row)

		var name_lbl := Label.new()
		var star: String = "★ " if party.has(cid) else "  "
		name_lbl.text = star + String(c.get("display_name", cid))
		name_lbl.custom_minimum_size = Vector2(180, 0)
		name_lbl.add_theme_font_size_override("font_size", 10)
		name_lbl.add_theme_color_override("font_color", C_ACCENT if party.has(cid) else C_TXT)
		row.add_child(name_lbl)

		var knack_lbl := Label.new()
		knack_lbl.text = String(c.get("knack", "·"))
		knack_lbl.custom_minimum_size = Vector2(200, 0)
		knack_lbl.add_theme_font_size_override("font_size", 9)
		knack_lbl.add_theme_color_override("font_color", C_TXT_DIM)
		row.add_child(knack_lbl)

		var meter_lbl := Label.new()
		meter_lbl.text = _meter_bar(_friendship_of(cid))
		meter_lbl.add_theme_font_size_override("font_size", 10)
		meter_lbl.add_theme_color_override("font_color", C_TXT)
		row.add_child(meter_lbl)

	var actions := HBoxContainer.new()
	actions.alignment = BoxContainer.ALIGNMENT_END
	v.add_child(actions)

	var close := Button.new()
	close.text = "  ✕  close  (tab)  "
	close.pressed.connect(_close_roster)
	actions.add_child(close)


func _close_roster() -> void:
	if _roster_panel != null and is_instance_valid(_roster_panel):
		_roster_panel.queue_free()
	_roster_panel = null
	_roster_open = false


# ── Day-intro modal ────────────────────────────────────────────

func _show_day_intro_modal() -> void:
	var d := _current_day()
	if d.is_empty(): return
	if _day_modal != null and is_instance_valid(_day_modal):
		_day_modal.queue_free()
	_day_modal_open = true
	var panel := Panel.new()
	panel.custom_minimum_size = Vector2(620, 340)
	panel.size = panel.custom_minimum_size
	panel.set_anchors_preset(Control.PRESET_CENTER)
	panel.position = -panel.size / 2.0
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.028, 0.024, 0.018, 0.98)
	sb.border_color = C_ACCENT
	sb.set_border_width_all(1)
	sb.content_margin_left = 22
	sb.content_margin_right = 22
	sb.content_margin_top = 16
	sb.content_margin_bottom = 16
	panel.add_theme_stylebox_override("panel", sb)
	_hud_layer.add_child(panel)
	_day_modal = panel

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.add_theme_constant_override("separation", 8)
	panel.add_child(v)

	var hdr := Label.new()
	hdr.text = String(d.get("display_name", "day"))
	hdr.add_theme_font_size_override("font_size", 13)
	hdr.add_theme_color_override("font_color", C_ACCENT)
	hdr.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(hdr)

	var body := RichTextLabel.new()
	body.bbcode_enabled = true
	body.fit_content = true
	body.custom_minimum_size = Vector2(560, 200)
	body.add_theme_font_size_override("normal_font_size", 11)
	body.add_theme_color_override("default_color", C_TXT)
	for line_v in d.get("intro_narration", []):
		body.append_text(String(line_v) + "\n\n")
	var anchor: String = String(d.get("anchor_event_summary", ""))
	if anchor != "":
		body.append_text("[color=#c8a842][i]  · anchor · %s[/i][/color]" % anchor)
	v.add_child(body)

	var actions := HBoxContainer.new()
	actions.alignment = BoxContainer.ALIGNMENT_END
	v.add_child(actions)

	var close := Button.new()
	close.text = "  →  begin the day  (esc / space)  "
	close.pressed.connect(_close_day_modal)
	actions.add_child(close)


func _close_day_modal() -> void:
	if _day_modal != null and is_instance_valid(_day_modal):
		_day_modal.queue_free()
	_day_modal = null
	_day_modal_open = false


var _transient_lbl: Label = null

func _show_transient(text: String) -> void:
	if _transient_lbl != null and is_instance_valid(_transient_lbl):
		_transient_lbl.queue_free()
	_transient_lbl = Label.new()
	_transient_lbl.text = text
	_transient_lbl.add_theme_font_size_override("font_size", 11)
	_transient_lbl.add_theme_color_override("font_color", C_ACCENT)
	_transient_lbl.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_transient_lbl.offset_top = -74
	_transient_lbl.offset_bottom = -50
	_transient_lbl.offset_left = 16
	_transient_lbl.offset_right = -16
	_hud_layer.add_child(_transient_lbl)
	get_tree().create_timer(3.0).timeout.connect(func() -> void:
		if _transient_lbl != null and is_instance_valid(_transient_lbl):
			_transient_lbl.queue_free()
			_transient_lbl = null)
