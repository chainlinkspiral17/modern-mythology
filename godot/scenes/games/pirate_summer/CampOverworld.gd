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

const TILE_PX := 24                # on-screen size of one tile
const CHAR_SPRITE_PATH := "res://resources/games/vol7/pirate_summer/sprites/chars/sam.json"
const ZONE_DIR := "res://resources/games/vol7/pirate_summer/zones/"

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

# Camera / render nodes.
var _world_root: Node2D = null     # holds tiles + Sam · we translate this for camera follow
var _hud_layer: CanvasLayer = null
var _zone_label: Label = null
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
	_build_hud()


func boot(host_state: Dictionary) -> void:
	_run_state = host_state
	var zone_id := String(host_state.get("zone", "cabin_sturgeon"))
	var spawn_id := String(host_state.get("spawn", "start"))
	_load_zone(zone_id, spawn_id)


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
	_update_zone_label()
	_recenter_camera()


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
	if _zone_label == null: return
	_zone_label.text = "PIRATE SUMMER · " + String(_zone.get("display_name", _zone.get("id", ""))).to_upper()


func _update_hover_label() -> void:
	if _hover_label == null: return
	var face_delta := _facing_delta()
	var tx: int = _sam_x + int(face_delta.x)
	var ty: int = _sam_y + int(face_delta.y)
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
			quit_to_shelf.emit()
			get_viewport().set_input_as_handled()
			return
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
	var nx := _sam_x + dx
	var ny := _sam_y + dy
	var def := _tile_def_at(nx, ny)
	if def.is_empty():
		_update_hover_label()
		return
	if not bool(def.get("walkable", false)):
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


func _interact_forward() -> void:
	var d := _facing_delta()
	var def := _tile_def_at(_sam_x + int(d.x), _sam_y + int(d.y))
	if def.is_empty(): return
	var interact := String(def.get("interact", ""))
	var label := String(def.get("label", ""))
	if interact == "duffel":
		_show_transient("  Sam's duffel · a slowstick called NORTHWIND HARBOR is inside · Wave C authors it.")
	elif label != "":
		_show_transient("  " + label)


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
