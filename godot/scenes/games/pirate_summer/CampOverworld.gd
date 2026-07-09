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
const _SAM_DIRECTIONAL_SPRITE := {
	"down":  CHAR_SPRITE_DIR + "sam_down.json",
	"up":    CHAR_SPRITE_DIR + "sam_up.json",
	"left":  CHAR_SPRITE_DIR + "sam_left.json",
	"right": CHAR_SPRITE_DIR + "sam_right.json",
}
const _SAM_WALK_SPRITE := {
	"down":  CHAR_SPRITE_DIR + "sam_down_walk.json",
	"up":    CHAR_SPRITE_DIR + "sam_up_walk.json",
	"left":  CHAR_SPRITE_DIR + "sam_left_walk.json",
	"right": CHAR_SPRITE_DIR + "sam_right_walk.json",
}
# Alternating-foot walk frame · toggles per step for a two-frame gait.
const _SAM_WALK_B_SPRITE := {
	"down":  CHAR_SPRITE_DIR + "sam_down_walk_b.json",
	"up":    CHAR_SPRITE_DIR + "sam_up_walk_b.json",
	"left":  CHAR_SPRITE_DIR + "sam_left_walk_b.json",
	"right": CHAR_SPRITE_DIR + "sam_right_walk_b.json",
}
# Dig-action frames · plays 3-frame sequence at the cache moment.
const _SAM_DIG_SPRITES := [
	CHAR_SPRITE_DIR + "sam_dig_1.json",
	CHAR_SPRITE_DIR + "sam_dig_2.json",
	CHAR_SPRITE_DIR + "sam_dig_3.json",
]
# Cache of loaded directional textures so we don't re-decode every turn.
var _sam_direction_textures: Dictionary = {}
const ZONE_DIR := "res://resources/games/vol7/pirate_summer/zones/"
const CAMPERS_PATH := "res://resources/games/vol7/pirate_summer/campers.json"
const TILE_SPRITE_DIR := "res://resources/games/vol7/pirate_summer/sprites/tiles/"

# Maps tile.kind → tile sprite id.  When a tile's kind matches, the
# renderer uses that pixelart sprite instead of a flat ColorRect.
# Kinds not in this table fall back to ColorRect (which is fine ·
# some tiles are utility-only, e.g. exit doors, and never authored).
const _TILE_SPRITE_FOR_KIND := {
	"grass":         "grass",
	"path":          "path",
	"sand":          "sand",
	"dune_grass":    "dune_grass",
	"floor":         "wood_floor",
	"wall":          "cabin_wall",
	"bunk":          "bunk",
	"tree":          "tree_top",
	"spruce":        "tree_top",
	"pine":          "tree_top",
	"brush":         "brush",
	"boulder":       "boulder",
	"rock":          "rock_wall",
	"dock":          "dock",
	"dock_edge":     "dock_edge",
	"shallow":       "water_shallow",
	"deep":          "water_deep",
	"water":         "water_deep",
	"ocean":         "water_deep",
	"sea":           "water_deep",
	"wet_wood":      "dock",
	"fire":          "fire",
	"fire_pit":      "fire",
	"deck":          "deck_wood",
	"rail":          "cabin_wall",
	"mast":          "cabin_wall",
	"cabin_ext":     "cabin_wall",
	"beaver_ext":    "cabin_wall",
	"osprey_ext":    "cabin_wall",
	"kestrel_ext":   "cabin_wall",
	"mess_ext":      "cabin_wall",
	"boathouse":     "cabin_wall",
	"rug":           "wood_floor",
	"stones":        "rock_wall",
	"window":        "window",
	"sign":          "sign",
	"chest":         "chest",
	"board":         "bulletin_board",
	"kitchen":       "kitchen_range",
	"table":         "wood_floor",
	"bench":         "wood_floor",
	"canoe_rack":    "chest",
	"life_jackets":  "sign",
	"lantern":       "fire",
	"lantern_big":   "fire",
	"lantern_hung":  "fire",
	"shelf":         "cabin_wall",
	"cross":         "cabin_wall",
	"grave":         "boulder",
	"hunter_cab":    "cabin_wall",
	"cabin_door":    "cabin_wall",
	"door":          "cabin_wall",
	"duff":          "grass",
	"back_path":     "path",
	"back_boat":     "deck_wood",
	"back_down":     "path",
	"back_up":       "rock_wall",
	"passage":       "rock_wall",
	"passage_up":    "rock_wall",
	"underwater":    "water_deep",
	# Variant tiles · zones opt in by using these kinds instead of
	# the base kind for texture variety across large tile areas.
	"grass_flower":    "grass_flower",
	"grass_thick":     "grass_thick",
	"sand_shell":      "sand_shell",
	"path_pebble":     "path_pebble",
	"brush_berry":     "brush_berry",
	"rock_wall_moss":  "rock_wall_moss",
	"tree_short":      "tree_short",
	"dune_grass_wind": "dune_grass_wind",
	# East-forest deep clearing (Wave X-forest-deep · 1976 cache)
	"fallen_log":      "fallen_log",
	"disturbed":       "disturbed_earth",
	"tent_peg":        "tent_peg",
	"cairn":           "cairn",
	"hollow":          "hollow_tree",
	"hollow_log":      "hollow_log",
}
# Sprite cache · keyed by sprite id.  Loaded once per zone-load
# (cleared when the world root is rebuilt).
var _tile_sprite_cache: Dictionary = {}
const DAYS_PATH := "res://resources/games/vol7/pirate_summer/days.json"
const DIALOGUE_WEB_PATH := "res://resources/games/vol7/pirate_summer/dialogue_web.json"
const PARTY_CHATTER_PATH := "res://resources/games/vol7/pirate_summer/party_chatter.json"
const IDLE_CHATTER_PATH := "res://resources/games/vol7/pirate_summer/idle_chatter.json"
const PIRATE_RADIO_PATH := "res://resources/games/vol7/pirate_summer/pirate_radio.json"

# Idle chatter · when Sam stands close to an NPC for a while, the
# NPC mutters something.  Different tint than party chatter.
const IDLE_PROXIMITY_TILES := 3
const IDLE_TRIGGER_SECONDS := 12.0
const IDLE_COOLDOWN_SECONDS := 20.0    # per-npc cooldown after firing
const SCHEDULE_PATH := "res://resources/games/vol7/pirate_summer/schedule.json"
const ITEMS_PATH := "res://resources/games/vol7/pirate_summer/items.json"
const COUNSELORS_PATH := "res://resources/games/vol7/pirate_summer/counselors.json"

const DUFFEL_CAP := 16

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

# Items catalog (loaded once).
var _items_by_id: Dictionary = {}
# Set of pickup tile positions Sam has already collected · prevents
# a pickup from re-fireing after zone reload.  Keys are "zone:x,y".
var _picked_up_positions: Dictionary = {}

# Duffel panel (key I).
var _duffel_panel: Panel = null
var _duffel_open: bool = false
# Journal panel (key J).
var _journal_panel: Panel = null
var _journal_open: bool = false

# Party chatter · full authored pool (loaded once) and per-run
# rotation state.  _chatter_speaker_cursor rotates through the party
# so the same person doesn't dominate the walk.
var _chatter_pool: Array = []
var _chatter_speaker_cursor: int = 0
var _steps_since_chatter: int = 0
var _chatter_balloon: Panel = null
var _chatter_balloon_timer: SceneTreeTimer = null

# Idle chatter · loaded pool + per-NPC dwell timer + cooldown timers.
var _idle_pool: Array = []
var _idle_current_target: String = ""
var _idle_dwell: float = 0.0
var _idle_cooldown_per_npc: Dictionary = {}

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
	_load_items()
	_build_hud()


func _load_items() -> void:
	if not FileAccess.file_exists(ITEMS_PATH): return
	var f := FileAccess.open(ITEMS_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		for it_v in (parsed as Dictionary).get("items", []):
			var it: Dictionary = it_v
			_items_by_id[String(it.get("id", ""))] = it


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
	if FileAccess.file_exists(PARTY_CHATTER_PATH):
		var f := FileAccess.open(PARTY_CHATTER_PATH, FileAccess.READ)
		var parsed: Variant = JSON.parse_string(f.get_as_text())
		f.close()
		if parsed is Dictionary:
			_chatter_pool = (parsed as Dictionary).get("chatter", [])
	if FileAccess.file_exists(IDLE_CHATTER_PATH):
		var f2 := FileAccess.open(IDLE_CHATTER_PATH, FileAccess.READ)
		var parsed2: Variant = JSON.parse_string(f2.get_as_text())
		f2.close()
		if parsed2 is Dictionary:
			_idle_pool = (parsed2 as Dictionary).get("chatter", [])


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
	# Counselors ride in the same _campers_by_id table with kind:"counselor"
	# · schedule resolver + dialogue box treat them uniformly.
	if FileAccess.file_exists(COUNSELORS_PATH):
		var f2 := FileAccess.open(COUNSELORS_PATH, FileAccess.READ)
		var parsed2: Variant = JSON.parse_string(f2.get_as_text())
		f2.close()
		if parsed2 is Dictionary:
			for c_var in (parsed2 as Dictionary).get("counselors", []):
				var c: Dictionary = c_var
				_campers_by_id[String(c.get("id", ""))] = c


func boot(host_state: Dictionary) -> void:
	_run_state = host_state
	_restore_picked_up_positions()
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
	_ensure_transition_layer()
	# On subsequent loads, fade to black, do the swap, fade back in.
	# On the very first load, start opaque and fade in only.
	if _first_zone_loaded:
		_in_transition = true
		_transition_rect.color.a = 0.0
		await _fade_to(1.0)
	else:
		_transition_rect.color.a = 1.0
	var path := ZONE_DIR + zone_id + ".json"
	if not FileAccess.file_exists(path):
		push_warning("[CampOverworld] missing zone %s" % path)
		_in_transition = false
		if _transition_rect != null: _transition_rect.color.a = 0.0
		return
	var f := FileAccess.open(path, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if not (parsed is Dictionary):
		push_warning("[CampOverworld] zone parse failed %s" % path)
		_in_transition = false
		if _transition_rect != null: _transition_rect.color.a = 0.0
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
	_play_zone_bgm(zone_id)
	_apply_world_tint()
	_first_zone_loaded = true
	# Give the world one frame to render before we fade in, so the
	# player never sees a partially-populated map through the alpha.
	await get_tree().process_frame
	await _fade_to(0.0)
	_in_transition = false
	# First-time zone-entry moment cards.
	if zone_id == "caves_level_1" and not _has_fact("caves_entered_first_time"):
		_discover_fact("caves_entered_first_time")
		_show_hero("moment_caves_entrance", "  the caves · Ana Faustina · 1873")
	elif zone_id == "north_bluff" and not _has_fact("north_bluff_first_view"):
		_discover_fact("north_bluff_first_view")
		_show_hero("moment_north_bluff_view", "  north bluff · you can see for miles")


const _BGM_FOR_ZONE := {
	"cabin_sturgeon":  "res://assets/audio/bgm/ps/cabin_warmth.wav",
	"cabin_beaver":    "res://assets/audio/bgm/ps/cabin_warmth.wav",
	"cabin_osprey":    "res://assets/audio/bgm/ps/cabin_warmth.wav",
	"cabin_kestrel":   "res://assets/audio/bgm/ps/cabin_warmth.wav",
	"mess_hall":       "res://assets/audio/bgm/ps/cabin_warmth.wav",
	"camp_path":       "res://assets/audio/bgm/ps/camp_daytime.wav",
	"archery_range":   "res://assets/audio/bgm/ps/camp_daytime.wav",
	"east_forest":     "res://assets/audio/bgm/ps/camp_daytime.wav",
	"north_bluff":     "res://assets/audio/bgm/ps/camp_daytime.wav",
	"alder_pond":      "res://assets/audio/bgm/ps/alder_pond_water.wav",
	"boathouse":       "res://assets/audio/bgm/ps/alder_pond_water.wav",
	"caves_level_1":   "res://assets/audio/bgm/ps/caves_echo.wav",
	"caves_level_2":   "res://assets/audio/bgm/ps/caves_echo.wav",
	"caves_level_3":   "res://assets/audio/bgm/ps/caves_echo.wav",
	"campfire_ring":   "res://assets/audio/bgm/ps/campfire_evening.wav",
	"ghost_ship":      "res://assets/audio/bgm/ps/ghost_ship_forever.wav",
}
var _current_bgm_path: String = ""

# Zone-specific ambient one-shot loops.  A single AudioStreamPlayer
# plays these on a period matched to the sound · waves every 30s,
# spruce wind every 40s, campfire crackle every 15s in evenings, etc.
const _AMBIENT_FOR_ZONE := {
	"alder_pond":      { "path": "res://assets/audio/sfx/ps/waves_lap.wav",       "interval": 30.0, "vol_db": -14.0 },
	"boathouse":       { "path": "res://assets/audio/sfx/ps/waves_lap.wav",       "interval": 40.0, "vol_db": -12.0 },
	"east_forest":     { "path": "res://assets/audio/sfx/ps/spruce_wind.wav",     "interval": 42.0, "vol_db": -12.0 },
	"north_bluff":     { "path": "res://assets/audio/sfx/ps/spruce_wind.wav",     "interval": 45.0, "vol_db": -14.0 },
	"campfire_ring":   { "path": "res://assets/audio/sfx/ps/campfire_crackle.wav","interval": 15.0, "vol_db": -10.0 },
	"ghost_ship":      { "path": "res://assets/audio/sfx/ps/ghost_moan.wav",      "interval": 20.0, "vol_db": -10.0 },
}
var _ambient_player: AudioStreamPlayer = null
var _ambient_timer: SceneTreeTimer = null
var _current_ambient_path: String = ""


func _play_zone_bgm(zone_id: String) -> void:
	var path := String(_BGM_FOR_ZONE.get(zone_id, ""))
	if path == "" or path == _current_bgm_path:
		return
	_current_bgm_path = path
	# AudioMgr is the game-wide bgm autoload · has_method guard for
	# scene-tests that boot without it.
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("play_bgm"):
		am.call("play_bgm", path)
	_start_zone_ambient(zone_id)


func _start_zone_ambient(zone_id: String) -> void:
	# Ambient one-shot pattern · load a stream, play it every `interval`
	# seconds while Sam is in this zone.  A subsequent zone-change
	# swaps or clears the ambient.
	var entry: Variant = _AMBIENT_FOR_ZONE.get(zone_id, null)
	if not (entry is Dictionary):
		_current_ambient_path = ""
		return
	var e: Dictionary = entry
	var path: String = String(e.get("path", ""))
	if path == _current_ambient_path: return
	_current_ambient_path = path
	if _ambient_player == null:
		_ambient_player = AudioStreamPlayer.new()
		add_child(_ambient_player)
	var stream: AudioStream = load(path)
	if stream == null:
		_current_ambient_path = ""
		return
	_ambient_player.stream = stream
	_ambient_player.volume_db = float(e.get("vol_db", -12.0))
	# Schedule the first play immediately, then loop on interval.
	_ambient_player.play()
	_schedule_next_ambient(float(e.get("interval", 30.0)))


func _schedule_next_ambient(interval: float) -> void:
	if _ambient_timer != null and _ambient_timer.is_connected("timeout", _on_ambient_tick):
		return  # already ticking
	_ambient_timer = get_tree().create_timer(interval)
	_ambient_timer.timeout.connect(_on_ambient_tick.bind(interval))


func _on_ambient_tick(interval: float) -> void:
	# Only fire if we're still in the same zone and the ambient
	# player is still valid.
	if _ambient_player == null or not is_instance_valid(_ambient_player):
		_ambient_timer = null
		return
	if _current_ambient_path == "":
		_ambient_timer = null
		return
	_ambient_player.play()
	# Reschedule.
	_ambient_timer = get_tree().create_timer(interval)
	_ambient_timer.timeout.connect(_on_ambient_tick.bind(interval))


func _get_sam_facing_texture(facing: String) -> ImageTexture:
	if _sam_direction_textures.has(facing):
		return _sam_direction_textures[facing]
	var path := String(_SAM_DIRECTIONAL_SPRITE.get(facing, SAM_SPRITE))
	var s := SlowstockSprite.new()
	if not s.load_from(path):
		# Fall back to the base sam.json · if that also fails, null.
		if not s.load_from(SAM_SPRITE):
			return null
	var tex := s.texture()
	_sam_direction_textures[facing] = tex
	return tex


func _get_sam_walk_texture(facing: String) -> ImageTexture:
	# Alternates between the primary walk frame (A) and the opposite-
	# foot mirror (B) per step, driven by _step_parity.
	var use_b: bool = (_step_parity % 2) == 1
	var dict: Dictionary = _SAM_WALK_B_SPRITE if use_b else _SAM_WALK_SPRITE
	var cache_key := facing + ("_walk_b" if use_b else "_walk")
	if _sam_direction_textures.has(cache_key):
		return _sam_direction_textures[cache_key]
	var path := String(dict.get(facing, ""))
	if path == "": return null
	var s := SlowstockSprite.new()
	if not s.load_from(path):
		return null
	var tex := s.texture()
	_sam_direction_textures[cache_key] = tex
	return tex


func _get_sam_dig_texture(frame: int) -> ImageTexture:
	var idx: int = clamp(frame, 0, _SAM_DIG_SPRITES.size() - 1)
	var cache_key := "dig_%d" % idx
	if _sam_direction_textures.has(cache_key):
		return _sam_direction_textures[cache_key]
	var s := SlowstockSprite.new()
	if not s.load_from(_SAM_DIG_SPRITES[idx]):
		return null
	var tex := s.texture()
	_sam_direction_textures[cache_key] = tex
	return tex


# Toggled every time Sam takes a step · used by _get_sam_walk_texture
# to alternate between the A and B walk frames.
var _step_parity: int = 0


func _update_sam_facing_sprite() -> void:
	if _sam_texture_rect == null: return
	var tex := _get_sam_facing_texture(_sam_facing)
	if tex != null:
		_sam_texture_rect.texture = tex


func _spawn_npcs() -> void:
	_npcs.clear()
	# Resolve who belongs in this zone at the current (day, time).
	# The zone JSON may still declare static npcs as fallbacks · used
	# when a character has no schedule entry that matches (e.g. Sam's
	# non-schedule guest characters in later waves).
	var resolved: Array = _resolve_scheduled_npcs_for_zone()
	# Static fallbacks · only spawn a character from zone.npcs if
	# they aren't already resolved by schedule.
	var already: Dictionary = {}
	for r_v in resolved:
		already[String((r_v as Dictionary).get("camper", ""))] = true
	for entry_v in _zone.get("npcs", []):
		var entry: Dictionary = entry_v
		if not already.has(String(entry.get("camper", ""))):
			resolved.append(entry)
	# Skip anyone currently in Sam's party · they're with Sam, not
	# standing in a room.
	var party: Array = _party()
	for entry_v in resolved:
		var entry: Dictionary = entry_v
		var cid := String(entry.get("camper", ""))
		if cid == "" or party.has(cid): continue
		var pos_a: Array = entry.get("pos", [0, 0])
		if pos_a.size() < 2: continue
		var sprite := SlowstockSprite.new()
		# Prefer the new "_down" directional sprite (facing camera by
		# default); fall back to the bare {cid}.json (legacy path);
		# fall back to Sam so a missing sprite never breaks the zone.
		var down_path := CHAR_SPRITE_DIR + cid + "_down.json"
		var base_path := CHAR_SPRITE_DIR + cid + ".json"
		var loaded := false
		if FileAccess.file_exists(down_path):
			loaded = sprite.load_from(down_path)
		if not loaded and FileAccess.file_exists(base_path):
			loaded = sprite.load_from(base_path)
		if not loaded:
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
		_npcs[cid] = { "pos": Vector2i(nx, ny), "node": tr, "facing": "down" }


func _resolve_scheduled_npcs_for_zone() -> Array:
	# For each camper with a schedule, decide whether they're in the
	# current zone at the current (day, time) block, and if so, at
	# what tile position.  Returns a list of {camper, pos} entries.
	var zone_id := String(_zone.get("id", ""))
	var block_id := _current_block_id()
	var day_name := String(_current_day().get("name", ""))
	var out: Array = []
	for cid_v in _campers_by_id.keys():
		var cid: String = String(cid_v)
		if cid == "sam": continue
		var c: Dictionary = _campers_by_id[cid]
		var sched: Dictionary = c.get("schedule", {})
		var placed := _resolve_camper_position(cid, c, sched, zone_id, block_id, day_name)
		if not placed.is_empty():
			out.append(placed)
	return out


func _resolve_camper_position(cid: String, c: Dictionary, sched: Dictionary,
	zone_id: String, block_id: String, day_name: String) -> Dictionary:
	# Priority · meals in mess hall · activities in activity zones ·
	# cabin/quiet/lights_out at bunk · free time at bunk (Wave G-tail
	# keeps free-time at cabin · a future wave scatters campers).
	var is_counselor: bool = String(c.get("kind", "")) == "counselor"
	match block_id:
		"breakfast", "lunch", "dinner":
			if zone_id == "mess_hall":
				var seat: Array = sched.get("mess_hall_seat", [])
				if seat.size() >= 2:
					return { "camper": cid, "pos": seat }
			return {}
		"morning_activity", "afternoon_activity":
			var per_day: Dictionary = _schedule_day_activities.get(day_name, {})
			var target_zone: Variant = per_day.get(block_id, null)
			if target_zone is String and String(target_zone) == zone_id:
				var pos: Array = (sched.get("activity_positions", {}) as Dictionary).get(zone_id, [])
				if pos.size() >= 2:
					return { "camper": cid, "pos": pos }
			return {}
		"free_time":
			# Counselors stand by their oversight posts during free time.
			if is_counselor:
				var cp_pos: Array = sched.get("camp_path_position", [])
				if cp_pos.size() >= 2 and zone_id == "camp_path":
					return { "camper": cid, "pos": cp_pos }
				return {}
			# Campers scatter · each has an authored free_time_zone +
			# free_time_pos.  Sturgeon-mates who don't scatter default
			# to the cabin.
			var ftz := String(sched.get("free_time_zone", ""))
			var ftp: Array = sched.get("free_time_pos", [])
			if ftz != "" and ftp.size() >= 2:
				if ftz == zone_id:
					return { "camper": cid, "pos": ftp }
				return {}
			var cabin_ft := String(c.get("cabin", ""))
			if cabin_ft == "sturgeon" and zone_id == "cabin_sturgeon":
				var bunk_ft: Variant = c.get("bunk_pos", null)
				if bunk_ft is Array and (bunk_ft as Array).size() >= 2:
					return { "camper": cid, "pos": bunk_ft }
			return {}
		"evening_event":
			if zone_id == "campfire_ring":
				var cfr: Array = sched.get("campfire_ring_position", [])
				if cfr.size() >= 2:
					return { "camper": cid, "pos": cfr }
			return {}
		_:
			# wake · quiet_time · lights_out → campers in the cabin at
			# their bunk.  Counselors stay quiet · they're off-duty.
			if is_counselor: return {}
			var cabin := String(c.get("cabin", ""))
			var expected_zone := "cabin_" + cabin
			if cabin != "" and zone_id == expected_zone:
				var bunk: Variant = c.get("bunk_pos", null)
				if bunk is Array and (bunk as Array).size() >= 2:
					return { "camper": cid, "pos": bunk }
			return {}


func _render_grid() -> void:
	var zone_id := String(_zone.get("id", ""))
	_tile_sprite_cache.clear()
	_animated_tile_rects.clear()
	for y in range(_grid_h):
		for x in range(_grid_w):
			var ch: String = _grid[y][x] if y < _grid.size() and x < _grid[y].size() else "."
			var def: Dictionary = _tileset.get(ch, {})
			# If this tile was a pickup Sam already collected, render
			# the underlying walkable base instead (grass/floor).
			if String(def.get("interact", "")) == "pickup":
				var key := "%s:%d,%d" % [zone_id, x, y]
				if _picked_up_positions.has(key):
					def = _tileset.get(_default_walkable_char_for_zone(), {})
			# Try a tile-art sprite first · authored per-kind lookup.
			var kind := String(def.get("kind", ""))
			var sprite_id := String(_TILE_SPRITE_FOR_KIND.get(kind, ""))
			if sprite_id != "":
				var tex: ImageTexture = _get_tile_texture(sprite_id)
				if tex != null:
					var tr := TextureRect.new()
					tr.texture = tex
					tr.size = Vector2(TILE_PX, TILE_PX)
					tr.position = Vector2(x * TILE_PX, y * TILE_PX)
					tr.stretch_mode = TextureRect.STRETCH_SCALE
					tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
					_world_root.add_child(tr)
					# If this tile kind has an animation cycle, track it so
					# _tick_env_animation can rotate the frame.
					if _ENV_ANIM_CYCLES.has(sprite_id):
						_animated_tile_rects.append({"node": tr, "cycle_id": sprite_id})
					continue
			# Fallback · flat ColorRect from the tile's color hex.
			var color := Color(0.2, 0.2, 0.2, 1.0)
			if def.has("color"):
				color = Color(String(def["color"]))
			var r := ColorRect.new()
			r.color = color
			r.size = Vector2(TILE_PX, TILE_PX)
			r.position = Vector2(x * TILE_PX, y * TILE_PX)
			r.mouse_filter = Control.MOUSE_FILTER_IGNORE
			_world_root.add_child(r)


func _get_tile_texture(sprite_id: String) -> ImageTexture:
	if _tile_sprite_cache.has(sprite_id):
		return _tile_sprite_cache[sprite_id]
	var path := TILE_SPRITE_DIR + sprite_id + ".json"
	var s := SlowstockSprite.new()
	if not s.load_from(path):
		return null
	var tex := s.texture()
	_tile_sprite_cache[sprite_id] = tex
	return tex


func _default_walkable_char_for_zone() -> String:
	# Best-effort choose a "background" tile to fill picked-up spots.
	# Prefer '.' (grass or floor in all current zones); fall back to
	# the first walkable tile in the tileset.
	if _tileset.has(".") and bool((_tileset["."] as Dictionary).get("walkable", false)):
		return "."
	for ch_v in _tileset.keys():
		var ch: String = String(ch_v)
		var d: Dictionary = _tileset[ch]
		if bool(d.get("walkable", false)):
			return ch
	return "."


func _spawn_sam(spawn_id: String) -> void:
	var sp: Array = _zone.get("spawns", {}).get(spawn_id, [0, 0])
	_sam_x = int(sp[0]) if sp.size() >= 2 else 0
	_sam_y = int(sp[1]) if sp.size() >= 2 else 0
	# Sprite · load the current facing direction.
	var tex: ImageTexture = _get_sam_facing_texture(_sam_facing)
	if tex == null:
		return
	_sam_texture_rect = TextureRect.new()
	_sam_texture_rect.texture = tex
	# Upscale 1.5× so the 16×24 native reads well against 24-px tiles.
	var upscale := 1.5
	_sam_texture_rect.size = Vector2(16 * upscale, 24 * upscale)
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
	_prompt_label.text = "  WASD · move  ·  space · interact  ·  tab · roster  ·  i · duffel  ·  j · journal  ·  esc · back  "
	_prompt_label.add_theme_font_size_override("font_size", 9)
	_prompt_label.add_theme_color_override("font_color", C_TXT_DIM)
	_prompt_label.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	_prompt_label.offset_left = -560
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
	_respawn_npcs_for_current_block()
	_apply_world_tint()
	_maybe_fire_evening_beat()
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


func _maybe_fire_evening_beat() -> void:
	# When time advances into evening_event AND Sam is at the campfire
	# ring, fire the day's scripted beat.  Tuesday and Wednesday carry
	# Wilson clues 2 and 3.
	if _current_block_id() != "evening_event": return
	if String(_zone.get("id", "")) != "campfire_ring": return
	var day_name := String(_current_day().get("name", ""))
	match day_name:
		"sunday":
			if not _has_fact("first_campfire_sunday"):
				_discover_fact("first_campfire_sunday")
				_show_hero("moment_first_campfire_night", "  sunday · you got eleven of fourteen")
			else:
				_show_transient("  · opening campfire · Jenny leads the name game.  Everyone learns fourteen names in one pass.  You get eleven of them.")
		"monday":
			_show_transient("  · the reptile skit · Cabin Beaver performs.  Wilson narrates in a voice that is trying very hard to be a narrator's voice.")
		"tuesday":
			_show_transient("  · homesick songs · Danny cries on the bench.  Wilson gets up and disappears for twenty minutes.  He returns with a wet jacket.  The lake is a mile away.")
			_discover_fact("wilson_disappeared_twenty_minutes_tuesday")
		"wednesday":
			_show_transient("  · the ghost pirate play · Wilson wrote the script.  The play describes a pirate who buried something at 44° 45' N, 124° 03' W.  Those are the coordinates of this camp.")
			_discover_fact("wilson_ghost_pirate_coordinates_match")
		"thursday":
			_show_transient("  · the talent show · ten acts.  Sylvie sings.  Xavier does a magic trick that 'goes wrong.'  Nika does not participate · she leaves during act six.")
		"friday":
			_show_transient("  · the closing bonfire · every cabin performs.  Wilson stands up at the end and sings a sea shanty in Portuguese.")
			# Clue 5 · fires only if Sam has enough Amelie context to
			# translate the shanty (Amelie in party OR friendship >= 3).
			var amelie_close: bool = _party().has("amelie_rocha") or _friendship_of("amelie_rocha") >= 3
			if amelie_close:
				_discover_fact("wilson_sings_portuguese_volta_return")
			else:
				_show_transient("  You didn't catch a word of the shanty.  Amelie would have known one.  You didn't have Amelie close.")
		_:
			pass


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
	var def: Dictionary = _tileset.get(ch, {})
	var zone_id := String(_zone.get("id", ""))
	# Picked-up pickup tiles collapse to the base walkable so Sam can
	# walk over the spot and the label goes away.
	if String(def.get("interact", "")) == "pickup":
		var key := "%s:%d,%d" % [zone_id, x, y]
		if _picked_up_positions.has(key):
			return _tileset.get(_default_walkable_char_for_zone(), {})
	# Boathouse: once unlocked, 'b' tiles become the door-def (which
	# has an exit).  Sam walks through the front b to enter.
	if zone_id == "alder_pond" and ch == "b" and _has_fact("boathouse_unlocked"):
		return _tileset.get("B", def)
	# Caves level 1 barrel: 'b' becomes 'B' (open) after the puzzle
	# solves.  The passage 'P' east of the barrel stays walkable but
	# labelless unless the barrel is open.
	if zone_id == "caves_level_1" and ch == "b" and _has_fact("caves_barrel_opened"):
		return _tileset.get("B", def)
	if zone_id == "caves_level_1" and ch == "P" and not _has_fact("caves_barrel_opened"):
		# Passage blocked by the sealed barrel · label reflects it.
		return { "kind": "blocked_passage", "color": "#241814", "walkable": false,
			"label": "the passage is blocked by the sealed barrel · open it first" }
	if zone_id == "caves_level_2" and ch == "P" and not _has_fact("caves_underwater_passed"):
		# Passage to level 3 requires clearing the underwater section.
		return { "kind": "blocked_passage", "color": "#241814", "walkable": false,
			"label": "the passage climbs up but you can't reach it without going through the water first" }
	return def


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
			elif _duffel_open:
				_close_duffel()
			elif _journal_open:
				_close_journal()
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
		if kev.keycode == KEY_I:
			_toggle_duffel()
			get_viewport().set_input_as_handled()
			return
		if kev.keycode == KEY_J:
			_toggle_journal()
			get_viewport().set_input_as_handled()
			return
		if _dialogue_open or _roster_open or _duffel_open or _journal_open: return
		if _sam_moving: return
		if _in_transition: return
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
	# Face the direction the player pressed, even if the move is
	# blocked · Sam still turns to look.
	_update_sam_facing_sprite()
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
	# Alternate the walk frame each step · this is the two-frame gait.
	_step_parity = (_step_parity + 1) % 2
	# Swap to walk-frame at the start of the step, back to idle at
	# the end.  The finished handler restores the idle sprite.
	var walk_tex: ImageTexture = _get_sam_walk_texture(_sam_facing)
	if walk_tex != null and _sam_texture_rect != null:
		_sam_texture_rect.texture = walk_tex


func _tween_camera(_t: float) -> void:
	_recenter_camera()


func _on_move_finished() -> void:
	_sam_moving = false
	# Back to the idle-frame for the current facing.
	_update_sam_facing_sprite()
	# Remember Sam's resting Y at this tile so the idle-bob can
	# oscillate around it in _process.
	if _sam_texture_rect != null:
		_sam_idle_base_y = _sam_texture_rect.position.y
	# Trigger an exit if the tile we landed on has one.
	var def := _tile_def_at(_sam_x, _sam_y)
	var exit_v: Variant = def.get("exit", null)
	if exit_v is Dictionary:
		var ex: Dictionary = exit_v
		var zid := String(ex.get("zone", ""))
		var sid := String(ex.get("spawn", ""))
		if zid != "":
			var sfx := get_node_or_null("/root/SFXBank")
			if sfx: sfx.play("door_open", 0.5)
			zone_changed.emit(zid, sid)
			_load_zone(zid, sid)
			return
	_update_hover_label()
	_tick_party_chatter()


# ── Party chatter ─────────────────────────────────────────────

func _maybe_schedule_reply(primary_id: String) -> void:
	# Find an authored reply that responds to primary_id, whose
	# speaker is in the party, and hasn't been used yet.
	var party: Array = _party()
	var used: Array = _used_chatter_ids()
	var candidates: Array = []
	for e_v in _chatter_pool:
		var e: Dictionary = e_v
		if String(e.get("replies_to", "")) != primary_id: continue
		var speaker := String(e.get("character", ""))
		if not party.has(speaker): continue
		if used.has(String(e.get("id", ""))): continue
		candidates.append(e)
	if candidates.is_empty(): return
	var pick: Dictionary = candidates[randi() % candidates.size()]
	# Fire the reply 4.0 seconds after the primary, once the primary
	# balloon has been visible long enough to read.
	get_tree().create_timer(4.0).timeout.connect(func() -> void:
		# Suppress if a modal is now open · deferred replies shouldn't
		# ambush the player in a menu.
		if _dialogue_open or _roster_open or _duffel_open \
			or _journal_open or _day_modal_open: return
		_show_chatter(String(pick.get("character", "")), pick)
		_mark_chatter_used(String(pick.get("id", ""))))


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
		# Reply lines · these fire scheduled after their target, not
		# on their own · exclude from the primary picker.
		if e.has("replies_to"): continue
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
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("tile_hover", 0.32)
	# Schedule a reply · scan for any authored reply that responds
	# to this line and whose speaker is currently in the party.
	_maybe_schedule_reply(String(entry.get("id", "")))
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
	elif interact == "shoot_arrow":
		_do_activity("shoot arrows", "LUCK")
	elif interact == "bulletin_board":
		_read_bulletin_board()
	elif interact == "pickup":
		_do_pickup(fx, fy, def)
	elif interact == "examine_wilson_bottle":
		if _has_fact("wilson_has_anchor_decal"):
			_show_transient("  Wilson's bottle is still on the table.  The anchor decal is still chipped.")
		else:
			_discover_fact("wilson_has_anchor_decal")
	elif interact == "dig_old_man":
		_try_dig_old_man()
	elif interact == "boathouse_door":
		_try_boathouse_door()
	elif interact == "boathouse_chest":
		_try_boathouse_chest()
	elif interact == "tune_shortwave":
		_tune_shortwave()
	elif interact == "boot_slowstick_console":
		_open_console_menu()
	elif interact == "cave_barrel":
		_try_cave_barrel()
	elif interact == "underwater_passage":
		_try_underwater_passage()
	elif interact == "pickup_satchel":
		_pickup_leather_satchel()
	elif interact == "examine_wall_scratch":
		if not _has_fact("caves_wall_scratch_message"):
			_discover_fact("caves_wall_scratch_message")
		else:
			_show_transient("  The words on the wall.  You read them again anyway.")
	elif interact == "examine_graffiti_1976":
		if not _has_fact("caves_1976_graffiti"):
			_discover_fact("caves_1976_graffiti")
		else:
			_show_transient("  'A.J. · JULY 22 · 1976.'  You've read this too.  The wall keeps the year.")
		# Third source triggers the umbrella fact if the newspaper + Jenny's
		# testimony are both known.  Not the case yet · this is the seed.
		_maybe_reveal_1976_incident()
	elif interact == "examine_1976_newspaper":
		if not _has_fact("boathouse_newspaper_1976"):
			_discover_fact("boathouse_newspaper_1976")
			_discover_fact("the_counselor_that_summer")
		else:
			_show_transient("  The clipping is still under the coffee tin.  Peter Halstrom quoted twice.  His silence louder than the quotes.")
		_maybe_reveal_1976_incident()
	elif interact == "examine_watched_island":
		if not _has_fact("watched_island_offshore"):
			_discover_fact("watched_island_offshore")
			_show_hero("moment_watched_island_delisle", "  the Delisle place · four miles out")
		else:
			_show_transient("  The island is still there · one lit dock, one cabin, smoke.  Same as yesterday.")
	elif interact == "examine_fed_boat":
		if not _has_fact("federal_boats_offshore"):
			_discover_fact("federal_boats_offshore")
			_show_hero("moment_federal_boat_pass", "  every ninety minutes · unmarked")
		else:
			_show_transient("  The gray twin-hull comes back around every ninety minutes.  You could set your watch.")
	elif interact == "ghost_ship_approach":
		_try_ghost_ship_approach()
	elif interact == "speak_captain":
		_speak_ghost_captain()
	elif interact == "leave_camp_early":
		_try_leave_camp_early()
	elif interact == "east_forest_gate":
		_try_east_forest_gate()
	elif interact == "examine_hunter_note":
		if not _has_fact("hunter_note_dated_2016"):
			_discover_fact("hunter_note_dated_2016")
			_show_hero("moment_hunter_note_2016", "  a year that hasn't happened yet")
		else:
			_show_transient("  The note is still on the door.  You reread it.")
	elif interact == "examine_grave":
		if not _has_fact("east_forest_ana_faustina_grave"):
			_discover_fact("east_forest_ana_faustina_grave")
		else:
			_show_transient("  The grave is here.  The moss keeps growing on the stone.")
	elif interact == "examine_graffiti_ship":
		if not _has_fact("caves_ship_ana_faustina"):
			_discover_fact("caves_ship_ana_faustina")
		else:
			_show_transient("  'Ana Faustina · 1873.'  Still there.")
	elif interact == "examine_graffiti_date":
		if not _has_fact("caves_march_1873_lost"):
			_discover_fact("caves_march_1873_lost")
		else:
			_show_transient("  'PERDIDA · MARÇO 1873.'  Lost.  March 1873.")
	elif interact == "try_hollow_log":
		_try_hollow_log()
	elif interact == "dig_1976_cache":
		_dig_1976_cache()
	elif interact == "examine_hollow_tree":
		_examine_hollow_tree()
	elif label != "":
		_show_transient("  " + label)


func _try_dig_old_man() -> void:
	# Success requires either Bea Hallowell (ROCKS FOR CLIMBING) in
	# the party, or three party members total to lift together.
	var party: Array = _party()
	var has_bea: bool = party.has("bea_hallowell")
	var enough_hands: bool = party.size() >= 3
	# Clue 6 · returning to the Old Man on Friday+ with the map in
	# the duffel and Wilson in nominal reach is the direct-question
	# moment.  It fires once.
	var day_idx: int = int(_run_state.get("day_index", 0))
	if _has_fact("wilson_signed_treasure_map_1987") and _duffel_contains("the_treasure_map") \
		and day_idx >= 5 and not _has_fact("wilson_is_the_pirate"):
		_discover_fact("wilson_is_the_pirate")
		_show_hero("moment_wilson_is_the_pirate", "  he says yes · before you finish asking")
		return
	if _has_fact("wilson_signed_treasure_map_1987"):
		_show_transient("  The Old Man is where you left it.  The empty tin is still under it.  You've got the map already.")
		return
	if not (has_bea or enough_hands):
		_show_transient("  The Old Man is too heavy for you alone.  You need Bea (rocks for climbing) or three of you together.")
		return
	# Add the map to the duffel · discovers clue 4.  If the duffel is
	# full we still give the map · plot item, always accepted.
	var duf: Array = _duffel()
	if not _duffel_contains("the_treasure_map"):
		duf.append("the_treasure_map")
		_run_state["duffel"] = duf
	_discover_fact("wilson_signed_treasure_map_1987")
	_show_hero("moment_treasure_map_found", "  signed W.A. · 1987")


func _duffel_contains(item_id: String) -> bool:
	for it in _duffel():
		if String(it) == item_id: return true
	return false


# ── Boathouse ─────────────────────────────────────────────────

func _try_boathouse_door() -> void:
	if _has_fact("boathouse_unlocked"):
		# Should be walkable now via the tile-def transform · this
		# path is a safety net if the player walks into an unlocked
		# b tile from the wrong angle.
		_show_transient("  The boathouse is already unlocked · walk into the front and it opens.")
		return
	var party: Array = _party()
	if party.has("reggie_vandermeer"):
		_discover_fact("boathouse_unlocked")
		_show_transient("  Reggie tries three of the four keys on his dad's ring.  The third works.  The boathouse door opens.")
		return
	if party.has("nika_voss"):
		_discover_fact("boathouse_unlocked")
		_show_transient("  Nika opens the padlock in under fifteen seconds and does not explain how.  The boathouse door opens.")
		return
	_show_transient("  The boathouse is padlocked.  You'd need Reggie's key or Nika's sneak to open it.")


func _try_cave_barrel() -> void:
	if _has_fact("caves_barrel_opened"):
		_show_transient("  The barrel is already open · the passage past it is clear.")
		return
	# Wu Kai's READ THE SIGN translates the shanty's second verse
	# scratched into the barrel · which is the barrel's release
	# combination.  Or three party members can force it.
	var party: Array = _party()
	var has_wu_kai: bool = party.has("wu_kai")
	var enough_hands: bool = party.size() >= 3
	if not (has_wu_kai or enough_hands):
		_show_transient("  The barrel has old Portuguese scratched into it.  Wu Kai could read it.  Three of you could just force the barrel · brute-force is a strategy.")
		return
	_discover_fact("caves_barrel_opened")
	_discover_fact("caves_passage_to_level_2")
	if has_wu_kai:
		_show_transient("  Wu Kai reads the shanty's second verse.  The barrel is a puzzle · reciting the verse in order releases the lid.  Inside · dry rope, a rusted lantern, a folded oilcloth.  Behind the barrel · a passage opens.")
	else:
		_show_transient("  Three of you lean on the barrel and it gives.  The lid rolls off.  Inside · dry rope, a rusted lantern, a folded oilcloth.  Behind the barrel · a passage opens.")


func _maybe_reveal_1976_incident() -> void:
	# The umbrella fact reveals once Sam has both the graffiti and the
	# newspaper.  Jenny's sister-1976 fact is optional (revealed via
	# a Jenny-in-mess-hall interact, deferred to a later commit).
	if _has_fact("camp_1976_incident"): return
	if _has_fact("caves_1976_graffiti") and _has_fact("boathouse_newspaper_1976"):
		_discover_fact("camp_1976_incident")


func _try_east_forest_gate() -> void:
	# Nika's SNEAK gets the party through without being spotted.
	# Anyone else · Bear catches them and turns them back.
	if _party().has("nika_voss"):
		zone_changed.emit("east_forest", "from_camp_path")
		_load_zone("east_forest", "from_camp_path")
		return
	_show_transient("  You take three steps into the deer trail.  Bear appears out of the pines with the specific patient expression of a man who has caught six campers this summer.  He walks you back.  Nika could get you past him.")


func _try_hollow_log() -> void:
	# Nika's SNEAK · she notices the disturbed moss where someone
	# else recently crawled through.  Without her, the log looks
	# like any other fallen tree.
	if not _party().has("nika_voss"):
		_show_transient("  A hollow log.  You'd crawl in and get scraped up and nothing would come of it.  Nika would probably notice something you're not noticing.")
		return
	if not _has_fact("east_forest_deep_clearing"):
		_discover_fact("east_forest_deep_clearing")
	zone_changed.emit("east_forest_deep", "from_east_forest")
	_load_zone("east_forest_deep", "from_east_forest")


func _dig_1976_cache() -> void:
	if _has_fact("dig_1976_cache"):
		_show_transient("  The tin is empty now.  You took what was in it.")
		return
	# Plot items · always accepted, no duffel-slot check.
	var duf: Array = _duffel()
	for it_id in ["photograph_1976", "journal_page_nika_v"]:
		if not _duffel_contains(it_id):
			duf.append(it_id)
	_run_state["duffel"] = duf
	_discover_fact("dig_1976_cache")
	_discover_fact("photograph_1976_counselors")
	_discover_fact("journal_page_shows_love_triangle")
	# Play the 3-frame dig animation, then the reveal HeroImage.
	_play_dig_animation(func() -> void:
		_show_hero("moment_1976_cache_reveal", "  summer 1976 · someone kept coming back"))


func _play_dig_animation(on_done: Callable) -> void:
	# Show sam_dig_1 → 2 → 3, 300ms each, then run on_done.  During the
	# sequence Sam's texture is overridden; when done, restore the
	# facing sprite.  Suppress idle-bob by pretending we're moving.
	if _sam_texture_rect == null:
		on_done.call()
		return
	_sam_moving = true
	var t := create_tween()
	for i in [0, 1, 2, 1, 0, 1, 2]:
		var frame_i: int = i
		t.tween_callback(func() -> void:
			if _sam_texture_rect == null: return
			var tex := _get_sam_dig_texture(frame_i)
			if tex != null:
				_sam_texture_rect.texture = tex)
		t.tween_interval(0.22)
	t.tween_callback(func() -> void:
		_sam_moving = false
		_update_sam_facing_sprite()
		on_done.call())


func _examine_hollow_tree() -> void:
	if _has_fact("examined_hollow_tree"):
		_show_transient("  You already took the bag.  The nail is bare.")
		return
	var duf: Array = _duffel()
	if not _duffel_contains("cassette_summer_1976"):
		duf.append("cassette_summer_1976")
	_run_state["duffel"] = duf
	_discover_fact("examined_hollow_tree")
	_show_hero("moment_hollow_spruce", "  she kept it in the tree")


func _try_leave_camp_early() -> void:
	# Only Friday (day_index 5) can take the bus.  Ends the run
	# immediately with the left_camp_early flag set · Saturday
	# transition skipped, ending picks the early_exit epilogue.
	var day_idx: int = int(_run_state.get("day_index", 0))
	if day_idx < 5:
		_show_transient("  The bus sign says the 3:41 bus stops here.  It's not Friday yet.  Nothing to catch today.")
		return
	if day_idx >= 6:
		_show_transient("  It's Saturday.  The bus you would have taken has come and gone.")
		return
	# Confirm-adjacent: fire directly · the message frames the choice.
	_run_state["left_camp_early_friday"] = true
	_show_transient("  You walk to the bus stop.  The bus comes at 3:41.  You pay the driver.  You do not look back.")
	get_tree().create_timer(2.0).timeout.connect(func() -> void:
		run_finished.emit({}, []))


func _try_ghost_ship_approach() -> void:
	# Thursday+ · Ford in party · satchel in duffel · then Sam sees
	# the ship offshore and Ford tide-times a canoe.  Any missing
	# requirement produces a specific refusal so the player knows
	# what's blocking.
	var day_idx: int = int(_run_state.get("day_index", 0))
	if day_idx < 4:
		_show_transient("  You look at the horizon.  Nothing unusual · yet.  The sea takes on a different shape after Wednesday.")
		return
	if not _duffel_contains("the_leather_satchel"):
		_show_transient("  You look at the horizon.  There's · something · out there in the shape of a ship.  You don't know what to do about it.  You'd need the satchel from the caves to have any reason to go.")
		return
	if not _party().has("ford_mears"):
		_show_transient("  You see the ship.  Riding low.  Not moving.  You don't know when the tide would let a canoe reach it.  Ford would know.")
		return
	# All conditions met · transport to the ghost ship.
	zone_changed.emit("ghost_ship", "from_alder_pond")
	_load_zone("ghost_ship", "from_alder_pond")


func _speak_ghost_captain() -> void:
	if _has_fact("wilson_ancestors_ghost_absolution"):
		_show_transient("  The captain looks at Sam.  He nods.  The nod is enough · you already heard what he had to say.")
		return
	# Sam presents the satchel and asks for absolution.  Wilson does
	# not need to be in the party · Sam is speaking for him.
	if not _duffel_contains("the_leather_satchel"):
		_show_transient("  The captain sees Sam empty-handed and shakes his head, gently.  'You have brought me nothing, child.  Go back for what my second mate carried away from me.'")
		return
	_discover_fact("wilson_ancestors_ghost_absolution")
	_show_hero("moment_ghost_captain_absolution", "  tell him I have been waiting to say so")


func _pickup_leather_satchel() -> void:
	if _has_fact("picked_up_leather_satchel"):
		_show_transient("  The satchel is already in your duffel.  You put it there earlier.")
		return
	var duf: Array = _duffel()
	if not _duffel_contains("the_leather_satchel"):
		duf.append("the_leather_satchel")
		_run_state["duffel"] = duf
	_discover_fact("picked_up_leather_satchel")
	_discover_fact("caves_captains_letter_1873")
	_discover_fact("caves_chart_center_is_camp")
	_show_hero("moment_leather_satchel_open", "  the center of the chart is this camp")


func _try_underwater_passage() -> void:
	if _has_fact("caves_underwater_passed"):
		_show_transient("  You've done this before.  The passage is where it was.")
		return
	var party: Array = _party()
	var has_ollie: bool = party.has("ollie_fisk")
	var has_ford: bool = party.has("ford_mears")
	if not (has_ollie or has_ford):
		_show_transient("  The water is too deep to hold breath through, and you don't know when the tide drops.  Ollie could swim you through.  Ford could time it.")
		return
	_discover_fact("caves_underwater_passed")
	if has_ollie:
		_show_transient("  Ollie takes Sam's hand.  'Two breaths in, then hold.'  Sam holds.  Ollie leads them under.  Nine seconds later they're up on sand on the other side.  Ollie is grinning.  Ollie was NOT lying about advanced swim, it turns out.")
	else:
		_show_transient("  Ford watches the water for eleven minutes.  'Now.'  The tide drops for ninety seconds · long enough to wade through.  Sam wades.  Ford follows.  The water comes back behind them.")


const CONSOLE_CARTS_PATH := "res://resources/games/vol7/pirate_summer/console_carts.json"
var _console_carts: Array = []
var _console_panel: Panel = null

func _open_console_menu() -> void:
	if _console_carts.is_empty() and FileAccess.file_exists(CONSOLE_CARTS_PATH):
		var f := FileAccess.open(CONSOLE_CARTS_PATH, FileAccess.READ)
		var parsed: Variant = JSON.parse_string(f.get_as_text())
		f.close()
		if parsed is Dictionary:
			_console_carts = (parsed as Dictionary).get("carts", [])
	if _console_carts.is_empty():
		_show_transient("  The console is off.  No carts on the shelf.")
		return
	if _console_panel != null and is_instance_valid(_console_panel):
		_console_panel.queue_free()
	var panel := Panel.new()
	panel.custom_minimum_size = Vector2(620, 400)
	panel.size = panel.custom_minimum_size
	panel.set_anchors_preset(Control.PRESET_CENTER)
	panel.position = -panel.size / 2.0
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.028, 0.024, 0.020, 0.98)
	sb.border_color = C_ACCENT
	sb.set_border_width_all(1)
	sb.content_margin_left = 20
	sb.content_margin_right = 20
	sb.content_margin_top = 14
	sb.content_margin_bottom = 14
	panel.add_theme_stylebox_override("panel", sb)
	_hud_layer.add_child(panel)
	_console_panel = panel
	_dialogue_open = true
	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.add_theme_constant_override("separation", 8)
	panel.add_child(v)
	var hdr := Label.new()
	hdr.text = "SLOWSTICK REV 2 · pick a cart to boot"
	hdr.add_theme_font_size_override("font_size", 13)
	hdr.add_theme_color_override("font_color", C_ACCENT)
	v.add_child(hdr)
	for cart_v in _console_carts:
		var cart: Dictionary = cart_v
		var row := VBoxContainer.new()
		row.add_theme_constant_override("separation", 2)
		v.add_child(row)
		var btn := Button.new()
		btn.text = "  ▸  " + String(cart.get("title", "?")) + "  ·  " + String(cart.get("publisher", "?")) + "  ·  " + str(cart.get("release_year", "?"))
		btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		btn.add_theme_font_size_override("font_size", 11)
		btn.pressed.connect(func() -> void: _boot_console_cart(cart))
		row.add_child(btn)
		var blurb := Label.new()
		blurb.text = "    " + String(cart.get("blurb", ""))
		blurb.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		blurb.custom_minimum_size = Vector2(560, 0)
		blurb.add_theme_font_size_override("font_size", 9)
		blurb.add_theme_color_override("font_color", C_TXT_DIM)
		row.add_child(blurb)
	var actions := HBoxContainer.new()
	actions.alignment = BoxContainer.ALIGNMENT_END
	v.add_child(actions)
	var close := Button.new()
	close.text = "  ✕  power off  "
	close.pressed.connect(_close_console_menu)
	actions.add_child(close)


func _boot_console_cart(cart: Dictionary) -> void:
	_close_console_menu()
	_show_transient("  " + String(cart.get("on_boot_line", "")))
	var fid := String(cart.get("fact", ""))
	if fid != "" and not _has_fact(fid):
		_discover_fact(fid)
	# Umbrella if all three cart facts discovered.
	var all_carts := ["sam_played_northwind_harbor_chapter_one",
		"sam_booted_earthman_chronicles", "sam_booted_fey_faire"]
	var have_all := true
	for f in all_carts:
		if not _has_fact(f):
			have_all = false; break
	if have_all and not _has_fact("console_all_three_carts"):
		_discover_fact("console_all_three_carts")


func _close_console_menu() -> void:
	if _console_panel != null and is_instance_valid(_console_panel):
		_console_panel.queue_free()
	_console_panel = null
	_dialogue_open = false


var _pirate_radio_fragments: Array = []

func _tune_shortwave() -> void:
	# If the player has the 1976 cassette in the duffel and hasn't
	# yet heard it, the tape deck plays it before the shortwave
	# fragments · the payoff for the deep-forest cache.
	if _duffel_contains("cassette_summer_1976") and not _has_fact("cassette_has_nika_voss_voice"):
		_discover_fact("cassette_has_nika_voss_voice")
		_show_hero("moment_1976_cassette_playback", "  the same voice · eighteen years younger · same frequency")
		return
	# Lazy-load the radio fragment file.
	if _pirate_radio_fragments.is_empty() and FileAccess.file_exists(PIRATE_RADIO_PATH):
		var f := FileAccess.open(PIRATE_RADIO_PATH, FileAccess.READ)
		var parsed: Variant = JSON.parse_string(f.get_as_text())
		f.close()
		if parsed is Dictionary:
			_pirate_radio_fragments = (parsed as Dictionary).get("fragments", [])
	if _pirate_radio_fragments.is_empty():
		_show_transient("  Static.  Just static.")
		return
	var day: int = int(_run_state.get("day_index", 0))
	var picked: Dictionary = {}
	for frag_v in _pirate_radio_fragments:
		var frag: Dictionary = frag_v
		if int(frag.get("day", -1)) == day:
			picked = frag
			break
	if picked.is_empty():
		_show_transient("  Static.  The band is quiet today.  Try again tomorrow.")
		return
	# Show the fragment as a transient · long lifetime.
	_show_transient("  " + String(picked.get("line", "")))
	# Register the fragment fact.
	var fact_id := String(picked.get("fact", ""))
	if fact_id != "" and not _has_fact(fact_id):
		_discover_fact(fact_id)
	# After 3+ fragments discovered, reveal the umbrella cross-lore fact.
	var count: int = 0
	for frag_v in _pirate_radio_fragments:
		if _has_fact(String((frag_v as Dictionary).get("fact", ""))):
			count += 1
	if count >= 3 and not _has_fact("pirate_radio_is_1600_am"):
		_discover_fact("pirate_radio_is_1600_am")


func _try_boathouse_chest() -> void:
	if _has_fact("read_wilsons_1988_logbook"):
		_show_transient("  Wilson's logbook is where you left it.  You've read it.")
		return
	# Chest opens with Priya's ALLERGY WARNING (noticing the padlock
	# is worn), Nika's SNEAK, or a rope+hook improvised lockpick.
	var party: Array = _party()
	var can_open: bool = party.has("nika_voss") or party.has("priya_sundar")
	if not can_open:
		_show_transient("  The chest is locked.  Nika's fingers or Priya's eye for worn hardware would help.")
		return
	_discover_fact("read_wilsons_1988_logbook")
	_discover_fact("wilson_captained_a_ship_out_of_astoria")
	_discover_fact("wilson_burial_july_1988")
	_show_hero("moment_boathouse_1988_logbook", "  W. Ashe · first mate, later master · july 1988")


func _do_pickup(x: int, y: int, def: Dictionary) -> void:
	var key := "%s:%d,%d" % [String(_zone.get("id", "")), x, y]
	if _picked_up_positions.has(key):
		_show_transient("  You already picked this up.")
		return
	var item_id := String(def.get("item_id", ""))
	if item_id == "" or not _items_by_id.has(item_id):
		return
	var duf: Array = _duffel()
	if duf.size() >= DUFFEL_CAP:
		_show_transient("  Your duffel is full · drop something before picking up more.")
		return
	duf.append(item_id)
	_run_state["duffel"] = duf
	_picked_up_positions[key] = true
	_run_state["picked_up_positions"] = _picked_up_positions.keys()
	facts_discovered.emit(_discovered_facts())    # piggyback save
	var it: Dictionary = _items_by_id[item_id]
	_show_transient("  ✻  picked up · " + String(it.get("display", item_id)))
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("pickup", 0.65)


func _duffel() -> Array:
	var v: Variant = _run_state.get("duffel", [])
	return v if v is Array else []


func _restore_picked_up_positions() -> void:
	# Hydrate _picked_up_positions from the saved list on boot.
	var arr: Variant = _run_state.get("picked_up_positions", [])
	if not (arr is Array): return
	for k in arr:
		_picked_up_positions[String(k)] = true


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
	# The bulletin board is a slow discovery · each read pulls out one
	# fact you haven't seen yet, in a fixed order, so the reader
	# unfolds it over multiple readings rather than dumping everything.
	var order := [
		"the_tide_chart_this_week",
		"camp_founded_by_andersson_1952",
		"mrs_wu_garden_open_house_1995",
	]
	for fid in order:
		if not _has_fact(fid):
			_discover_fact(fid)
			return
	_show_transient("  · you've read all the pinned fliers.  Nothing new today.")


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
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("season_settle", 0.5)
	day_advanced.emit(cur + 1)
	time_advanced.emit(cur + 1, 0)
	_update_zone_label()
	_respawn_npcs_for_current_block()
	_apply_world_tint()
	_show_day_intro_modal()
	# Saturday morning · Sam's summer resolves.  A beat after the
	# intro modal appears, fire run_finished so the host transitions
	# to the ending screen.  The intro reads first; the ending arrives
	# when Sam dismisses it (a Wave M-tail future refinement would
	# wait for modal-dismissed rather than firing on a timer).
	if (cur + 1) == 6:
		_show_hero("moment_saturday_bus_home", "  saturday · you know fourteen names")
		get_tree().create_timer(3.0).timeout.connect(func() -> void:
			run_finished.emit({}, []))


var _sam_idle_base_y: float = 0.0
var _sam_idle_bob_t: float = 0.0
# Cache: "{cid}:{facing}" -> ImageTexture
var _npc_directional_textures: Dictionary = {}

# ─── Zone transition fade ──────────────────────────────────────────
# Full-screen black overlay tweens 0↔1 across zone loads.  Uses a
# dedicated CanvasLayer at layer 128 so it draws above the HUD.
const _TRANSITION_FADE_SECS := 0.28
var _transition_layer: CanvasLayer = null
var _transition_rect: ColorRect = null
var _first_zone_loaded: bool = false
var _in_transition: bool = false

func _ensure_transition_layer() -> void:
	if _transition_layer != null and is_instance_valid(_transition_layer):
		return
	_transition_layer = CanvasLayer.new()
	_transition_layer.layer = 128
	add_child(_transition_layer)
	_transition_rect = ColorRect.new()
	_transition_rect.color = Color(0, 0, 0, 1)
	_transition_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_transition_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_transition_layer.add_child(_transition_rect)


func _fade_to(a: float) -> void:
	_ensure_transition_layer()
	var t := create_tween()
	t.tween_property(_transition_rect, "color:a", a, _TRANSITION_FADE_SECS)
	await t.finished


# ─── Time-of-day tint ──────────────────────────────────────────────
# Per-block Color tinting the world subtree (not the HUD).  Uses a
# CanvasModulate under _world_root so tiles / Sam / NPCs all darken
# and warm at once, while the HUD CanvasLayer stays bright.
const _BLOCK_TINT := {
	"wake":              Color(1.00, 1.00, 1.00, 1.0),
	"breakfast":         Color(1.00, 0.98, 0.94, 1.0),
	"morning_activity":  Color(1.00, 0.98, 0.94, 1.0),
	"lunch":             Color(1.00, 0.96, 0.90, 1.0),
	"afternoon_activity":Color(1.00, 0.94, 0.86, 1.0),
	"free_time":         Color(1.00, 0.92, 0.80, 1.0),
	"dinner":            Color(1.00, 0.86, 0.72, 1.0),   # sunset warming
	"evening_event":     Color(0.96, 0.72, 0.60, 1.0),   # sunset amber
	"lights_out":        Color(0.42, 0.48, 0.72, 1.0),   # twilight blue
	"quiet_time":        Color(0.62, 0.66, 0.82, 1.0),
}
# Zones that stay dark regardless of time-of-day (cave, ghost ship).
const _ZONE_TINT_OVERRIDE := {
	"caves_level_1": Color(0.40, 0.44, 0.60, 1.0),
	"caves_level_2": Color(0.34, 0.40, 0.56, 1.0),
	"caves_level_3": Color(0.30, 0.36, 0.52, 1.0),
	"ghost_ship":    Color(0.44, 0.52, 0.72, 1.0),
	"east_forest":       Color(0.72, 0.82, 0.68, 1.0),
	"east_forest_deep":  Color(0.60, 0.72, 0.60, 1.0),
	"boathouse":     Color(0.86, 0.78, 0.62, 1.0),
}
var _tint_modulate: CanvasModulate = null

func _apply_world_tint() -> void:
	if _world_root == null: return
	if _tint_modulate == null or not is_instance_valid(_tint_modulate):
		_tint_modulate = CanvasModulate.new()
		_world_root.add_child(_tint_modulate)
	var zone_id := String(_zone.get("id", ""))
	if _ZONE_TINT_OVERRIDE.has(zone_id):
		_tint_modulate.color = _ZONE_TINT_OVERRIDE[zone_id]
		return
	var block_id := _current_block_id()
	var c: Color = _BLOCK_TINT.get(block_id, Color(1, 1, 1, 1))
	_tint_modulate.color = c


# ─── Interaction indicator ─────────────────────────────────────────
# A small "!" bubble that hovers above any interactable/exit tile
# adjacent to Sam.  Reuses a single TextureRect that we move around
# rather than spawning/despawning nodes.  Two frame textures for a
# subtle bob (toggled by _tick_env_animation's frame counter).
var _interact_hint_rect: TextureRect = null
var _interact_hint_target: Vector2i = Vector2i(-99, -99)

func _tick_interact_hint(_dt: float) -> void:
	# Suppress while modals are open, Sam is mid-step, or the HUD is
	# toggled off (F4) · this is UI, not world state.
	if _sam_moving or _dialogue_open or _duffel_open \
		or _journal_open or _day_modal_open or _roster_open \
		or not FirstPersonController.hud_visible:
		_hide_interact_hint()
		return
	# Find the first interactable/exit tile adjacent to Sam (including
	# the tile Sam is standing on).
	var target: Vector2i = Vector2i(-99, -99)
	var candidates: Array = [
		Vector2i(_sam_x, _sam_y),
		Vector2i(_sam_x, _sam_y - 1),
		Vector2i(_sam_x, _sam_y + 1),
		Vector2i(_sam_x - 1, _sam_y),
		Vector2i(_sam_x + 1, _sam_y),
	]
	for c_v in candidates:
		var c: Vector2i = c_v
		var d: Dictionary = _tile_def_at(c.x, c.y)
		if d.is_empty(): continue
		if String(d.get("interact", "")) != "" or d.has("exit"):
			target = c
			break
	if target == Vector2i(-99, -99):
		_hide_interact_hint()
		return
	# Lazy-create the indicator rect · lives in _world_root so it
	# scrolls with the map.  Joins "ui" group so F4 hides it in
	# screenshots (per the debug-hud master rule).
	if _interact_hint_rect == null or not is_instance_valid(_interact_hint_rect):
		_interact_hint_rect = TextureRect.new()
		var upscale := 1.0
		_interact_hint_rect.size = Vector2(16 * upscale, 16 * upscale)
		_interact_hint_rect.stretch_mode = TextureRect.STRETCH_KEEP
		_interact_hint_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_interact_hint_rect.add_to_group("ui")
		_interact_hint_rect.visible = FirstPersonController.hud_visible
		_world_root.add_child(_interact_hint_rect)
	# Position 12 pixels above the tile center.
	var px_x: float = target.x * TILE_PX + TILE_PX / 2.0 - 8.0
	var px_y: float = target.y * TILE_PX - 10.0
	_interact_hint_rect.position = Vector2(px_x, px_y)
	_interact_hint_rect.visible = true
	# Alternate frame based on shared env-anim counter (2-frame bob).
	var frame_id := "interact_indicator" if (_env_anim_frame % 2) == 0 \
		else "interact_indicator_b"
	var tex := _get_tile_texture(frame_id)
	if tex != null:
		_interact_hint_rect.texture = tex
	_interact_hint_target = target


func _hide_interact_hint() -> void:
	if _interact_hint_rect != null and is_instance_valid(_interact_hint_rect):
		_interact_hint_rect.visible = false
	_interact_hint_target = Vector2i(-99, -99)


# ─── Environmental animation ───────────────────────────────────────
# Per-kind cycle definitions.  Each entry: base_sprite_id → array of
# sprite_ids to cycle through.  The renderer registers tiles with a
# base cycle id when rendered; _tick_env_animation swaps their texture
# at the shared frame interval.
const _ENV_ANIM_CYCLES := {
	"fire":          ["fire", "fire_alt", "fire_alt2"],
	"water_deep":    ["water_deep", "water_deep_alt"],
	"water_shallow": ["water_shallow", "water_shallow_alt"],
}
const _ENV_ANIM_INTERVAL := 0.4  # seconds per frame
var _animated_tile_rects: Array = []   # [{node, cycle_id}, ...]
var _env_anim_t: float = 0.0
var _env_anim_frame: int = 0

func _tick_env_animation(dt: float) -> void:
	_env_anim_t += dt
	if _env_anim_t < _ENV_ANIM_INTERVAL:
		return
	_env_anim_t = 0.0
	_env_anim_frame += 1
	for entry_v in _animated_tile_rects:
		var entry: Dictionary = entry_v
		var cycle_id: String = entry.get("cycle_id", "")
		var cycle: Array = _ENV_ANIM_CYCLES.get(cycle_id, [])
		if cycle.is_empty(): continue
		var idx: int = _env_anim_frame % cycle.size()
		var sprite_id: String = String(cycle[idx])
		var tex := _get_tile_texture(sprite_id)
		var node = entry.get("node", null)
		if tex != null and node is TextureRect:
			(node as TextureRect).texture = tex

func _get_npc_directional_texture(cid: String, facing: String) -> ImageTexture:
	var key := "%s:%s" % [cid, facing]
	if _npc_directional_textures.has(key):
		return _npc_directional_textures[key]
	var s := SlowstockSprite.new()
	# Prefer "{cid}_{facing}.json"; fall back to base sprite.
	var dir_path := CHAR_SPRITE_DIR + cid + "_" + facing + ".json"
	var base_path := CHAR_SPRITE_DIR + cid + ".json"
	var loaded := false
	if FileAccess.file_exists(dir_path):
		loaded = s.load_from(dir_path)
	if not loaded and FileAccess.file_exists(base_path):
		loaded = s.load_from(base_path)
	if not loaded:
		return null
	var tex := s.texture()
	_npc_directional_textures[key] = tex
	return tex


func _tick_npcs_face_sam() -> void:
	# For each NPC, if Sam is adjacent (Chebyshev distance == 1),
	# turn to face him.  Otherwise keep the current facing.  Doing
	# this only when Sam actually moves would be more efficient, but
	# it's cheap enough per-frame for the ~10 NPCs in view.
	for cid_v in _npcs.keys():
		var cid: String = String(cid_v)
		var entry: Dictionary = _npcs[cid]
		var p: Vector2i = entry.get("pos", Vector2i(-99, -99))
		if p == Vector2i(-99, -99): continue
		var dx: int = _sam_x - p.x
		var dy: int = _sam_y - p.y
		# Only face Sam when he's within a 2-tile radius.  Beyond that,
		# keep the current facing so idle NPCs don't spin every step.
		if abs(dx) > 2 or abs(dy) > 2: continue
		var want: String
		if abs(dx) >= abs(dy):
			want = "right" if dx > 0 else "left"
		else:
			want = "down" if dy > 0 else "up"
		if String(entry.get("facing", "down")) == want: continue
		var tex := _get_npc_directional_texture(cid, want)
		if tex == null: continue
		entry["facing"] = want
		var node: Node = entry.get("node", null)
		if node is TextureRect:
			(node as TextureRect).texture = tex


func _process(dt: float) -> void:
	# Environmental animation · flickering fire, rippling water.
	# Runs regardless of modals · this is world-state, not HUD.
	if not _animated_tile_rects.is_empty():
		_tick_env_animation(dt)
	# NPCs face Sam when he's within 2 tiles.  Uses the new directional
	# sprites (falls back to bare sprite for any missing variant).
	if not _npcs.is_empty() and not _sam_moving:
		_tick_npcs_face_sam()
	# Interaction indicator · "!" bubble above adjacent interactable
	# tiles.  Cheap · one adjacency scan per frame.
	_tick_interact_hint(dt)
	# Idle bob · when Sam is standing still, oscillate the sprite Y
	# by 1 pixel every ~700ms.  Movement tween overrides this by
	# writing position each step; we only nudge while _sam_moving is
	# false and no modal is up.
	if not _sam_moving and _sam_texture_rect != null \
		and not _dialogue_open and not _duffel_open \
		and not _journal_open and not _day_modal_open \
		and not _roster_open:
		_sam_idle_bob_t += dt
		var phase: int = int(_sam_idle_bob_t / 0.7) % 2
		var target_y: float = _sam_idle_base_y - (1.0 if phase == 1 else 0.0)
		# Only touch position if we've captured a base y (post-first-move).
		if _sam_idle_base_y != 0.0:
			_sam_texture_rect.position.y = target_y
	# Idle chatter · when Sam stands close to an NPC for
	# IDLE_TRIGGER_SECONDS, the NPC mutters an idle line.
	# Suppressed while any modal / moving is happening.
	# Also decrement per-NPC cooldowns.
	if not _idle_pool.is_empty():
		_tick_idle_chatter(dt)
	# Countdown cooldowns.
	for cid in _idle_cooldown_per_npc.keys():
		var v: float = float(_idle_cooldown_per_npc[cid]) - dt
		if v <= 0.0:
			_idle_cooldown_per_npc.erase(cid)
		else:
			_idle_cooldown_per_npc[cid] = v


func _tick_idle_chatter(dt: float) -> void:
	if _sam_moving or _dialogue_open or _roster_open or _duffel_open \
		or _journal_open or _day_modal_open:
		_idle_current_target = ""
		_idle_dwell = 0.0
		return
	# Find closest NPC within IDLE_PROXIMITY_TILES.
	var nearest_id := ""
	var nearest_dist: int = IDLE_PROXIMITY_TILES + 1
	for cid_v in _npcs.keys():
		var cid: String = String(cid_v)
		if _idle_cooldown_per_npc.has(cid): continue
		var p: Vector2i = _npcs[cid].get("pos", Vector2i(-99, -99))
		var d: int = abs(p.x - _sam_x) + abs(p.y - _sam_y)
		if d <= IDLE_PROXIMITY_TILES and d < nearest_dist:
			nearest_dist = d
			nearest_id = cid
	if nearest_id == "":
		_idle_current_target = ""
		_idle_dwell = 0.0
		return
	if nearest_id != _idle_current_target:
		_idle_current_target = nearest_id
		_idle_dwell = 0.0
		return
	_idle_dwell += dt
	if _idle_dwell >= IDLE_TRIGGER_SECONDS:
		_fire_idle_chatter(nearest_id)
		_idle_dwell = 0.0
		_idle_cooldown_per_npc[nearest_id] = IDLE_COOLDOWN_SECONDS


func _fire_idle_chatter(cid: String) -> void:
	var used: Array = _run_state.get("used_idle_ids", [])
	var eligible: Array = []
	for e_v in _idle_pool:
		var e: Dictionary = e_v
		if String(e.get("character", "")) != cid: continue
		if used.has(String(e.get("id", ""))): continue
		eligible.append(e)
	if eligible.is_empty(): return
	var pick: Dictionary = eligible[randi() % eligible.size()]
	# Reuse the party-chatter balloon renderer but with an ' [idle]'
	# suffix on the name label so the two are distinguishable.
	var entry := pick.duplicate()
	entry["_is_idle"] = true
	_show_idle_balloon(cid, entry)
	# Mark used.
	used.append(String(entry.get("id", "")))
	_run_state["used_idle_ids"] = used
	facts_discovered.emit(_discovered_facts())    # piggyback save


func _show_idle_balloon(cid: String, entry: Dictionary) -> void:
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
	sb.bg_color = Color(0.014, 0.020, 0.020, 0.92)
	sb.border_color = color.darkened(0.20)   # slightly darker border · idle marker
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
	name_lbl.text = String(c.get("display_name", cid)) + "  ·  " + mood + "  ·  [thinking aloud]"
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

	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("tile_hover", 0.28)
	_chatter_balloon_timer = get_tree().create_timer(CHATTER_LIFETIME)
	_chatter_balloon_timer.timeout.connect(func() -> void:
		if _chatter_balloon == panel and is_instance_valid(panel):
			panel.queue_free()
			_chatter_balloon = null)


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
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("customer_bell", 0.4)
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

	# Two-column layout · portrait on the left, text on the right.
	var row := HBoxContainer.new()
	row.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	row.add_theme_constant_override("separation", 14)
	panel.add_child(row)

	# Portrait · use the character's SlowstockSprite upscaled 3x.
	var portrait := SlowstockSprite.new()
	if portrait.load_from(CHAR_SPRITE_DIR + camper_id + ".json"):
		var portrait_wrap := PanelContainer.new()
		portrait_wrap.custom_minimum_size = Vector2(60, 84)
		var psb := StyleBoxFlat.new()
		psb.bg_color = Color(0.02, 0.02, 0.02, 1.0)
		psb.border_color = C_ACCENT
		psb.set_border_width_all(1)
		psb.content_margin_left = 4
		psb.content_margin_right = 4
		psb.content_margin_top = 4
		psb.content_margin_bottom = 4
		portrait_wrap.add_theme_stylebox_override("panel", psb)
		var portrait_rect := TextureRect.new()
		portrait_rect.texture = portrait.texture()
		portrait_rect.custom_minimum_size = Vector2(48, 72)
		portrait_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		portrait_wrap.add_child(portrait_rect)
		row.add_child(portrait_wrap)

	var v := VBoxContainer.new()
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	v.add_theme_constant_override("separation", 6)
	row.add_child(v)

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
	var is_counselor: bool = String(c.get("kind", "")) == "counselor"
	if is_counselor:
		# Counselors don't join camper parties · they're staff.
		pass
	elif in_party:
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

	# STORY BEAT button · appears only when this camper's story-beat
	# trigger conditions match the current (day, zone, block) tuple
	# AND the beat hasn't fired yet this run.  Grants +N friendship
	# and marks the beat consumed.
	if _story_beat_available(camper_id, c):
		var beat: Dictionary = c.get("story_beat_trigger", {})
		var story := Button.new()
		story.text = "  ✧  " + String(beat.get("prompt", "story beat"))
		story.pressed.connect(func() -> void:
			_fire_story_beat(camper_id, beat)
			_close_dialogue())
		actions.add_child(story)

	# GIVE A GIFT button · appears whenever Sam has any giftable
	# items in the duffel.  Opens the duffel in gift-mode.
	if _has_giftable_items():
		var gift := Button.new()
		gift.text = "  🎁  give a gift  "
		gift.pressed.connect(func() -> void:
			_close_dialogue()
			_open_duffel(camper_id))
		actions.add_child(gift)

	var close := Button.new()
	close.text = "  ✕  close  (esc)  "
	close.pressed.connect(_close_dialogue)
	actions.add_child(close)


func _story_beat_available(camper_id: String, c: Dictionary) -> bool:
	var beat: Dictionary = c.get("story_beat_trigger", {})
	if beat.is_empty(): return false
	# Already fired · one-shot.
	if _has_fact("story_beat_" + camper_id): return false
	var need_day: int = int(beat.get("day", -1))
	if need_day >= 0 and int(_run_state.get("day_index", 0)) != need_day: return false
	var need_zone := String(beat.get("zone", ""))
	if need_zone != "" and need_zone != String(_zone.get("id", "")): return false
	var need_block := String(beat.get("block", ""))
	if need_block != "" and need_block != _current_block_id(): return false
	return true


func _fire_story_beat(camper_id: String, beat: Dictionary) -> void:
	var delta: int = int(beat.get("friendship_delta", 1))
	_bump_friendship(camper_id, delta)
	_discover_fact("story_beat_" + camper_id)
	_show_transient("  " + String(beat.get("response", "")))
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("boot", 0.55)


func _has_giftable_items() -> bool:
	for id_v in _duffel():
		var it: Dictionary = _items_by_id.get(String(id_v), {})
		if bool(it.get("giftable", true)):
			return true
	return false


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

	# Two-column layout · portrait on the left, reaction on the right.
	var row := HBoxContainer.new()
	row.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	row.add_theme_constant_override("separation", 14)
	_dialogue_panel.add_child(row)

	# Portrait · matches the dialogue-open view.
	var portrait := SlowstockSprite.new()
	if portrait.load_from(CHAR_SPRITE_DIR + camper_id + ".json"):
		var portrait_wrap := PanelContainer.new()
		portrait_wrap.custom_minimum_size = Vector2(60, 84)
		var psb := StyleBoxFlat.new()
		psb.bg_color = Color(0.02, 0.02, 0.02, 1.0)
		psb.border_color = C_ACCENT
		psb.set_border_width_all(1)
		psb.content_margin_left = 4
		psb.content_margin_right = 4
		psb.content_margin_top = 4
		psb.content_margin_bottom = 4
		portrait_wrap.add_theme_stylebox_override("panel", psb)
		var portrait_rect := TextureRect.new()
		portrait_rect.texture = portrait.texture()
		portrait_rect.custom_minimum_size = Vector2(48, 72)
		portrait_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		portrait_wrap.add_child(portrait_rect)
		row.add_child(portrait_wrap)

	var v := VBoxContainer.new()
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	v.add_theme_constant_override("separation", 6)
	row.add_child(v)

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
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("register_ding", 0.55)
	# Scan for chain-facts whose all-preconditions are now satisfied.
	# Deferred one frame so the transient banner ordering reads.
	call_deferred("_scan_chain_facts")


func _scan_chain_facts() -> void:
	# Chain facts have an `unlocks_when_all_of` array in their def.
	# When every fact in that array is discovered, the chain fact
	# fires automatically.  Recurses via _discover_fact if the
	# chain fact itself unlocks further chains.
	var newly: Array = []
	for fid_v in _facts_by_id.keys():
		var fid: String = String(fid_v)
		if _has_fact(fid): continue
		var f: Dictionary = _facts_by_id[fid]
		var reqs: Variant = f.get("unlocks_when_all_of", null)
		if not (reqs is Array): continue
		var have_all: bool = true
		for r in reqs:
			if not _has_fact(String(r)):
				have_all = false; break
		if have_all:
			newly.append(fid)
	for fid in newly:
		_discover_fact(fid)


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
	_respawn_npcs_for_current_block()


func _remove_from_party(cid: String) -> void:
	var p: Array = _party()
	if not p.has(cid): return
	p.erase(cid)
	_run_state["party"] = p
	party_changed.emit(p, _friendship())
	_show_transient("  " + String(_campers_by_id.get(cid, {}).get("display_name", cid)) + " left the party.")
	_respawn_npcs_for_current_block()


func _respawn_npcs_for_current_block() -> void:
	# Free existing NPC nodes and rebuild from the current schedule.
	# Called when time advances, day changes, or party composition
	# shifts (someone joined / left).  Kept cheap · Cabin Sturgeon
	# never has more than ~5 NPCs.
	for cid_v in _npcs.keys():
		var entry: Dictionary = _npcs[cid_v]
		var node: Variant = entry.get("node", null)
		if node is TextureRect and is_instance_valid(node):
			(node as TextureRect).queue_free()
	_npcs.clear()
	if _world_root == null: return
	_spawn_npcs()


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


# ── Duffel panel (key I) ──────────────────────────────────────

func _toggle_duffel() -> void:
	if _duffel_open:
		_close_duffel()
	else:
		_open_duffel()


func _open_duffel(for_gift_to: String = "") -> void:
	if _duffel_panel != null and is_instance_valid(_duffel_panel):
		_duffel_panel.queue_free()
	_duffel_open = true
	var panel := Panel.new()
	panel.custom_minimum_size = Vector2(520, 440)
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
	_duffel_panel = panel

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.add_theme_constant_override("separation", 6)
	panel.add_child(v)

	var hdr := Label.new()
	if for_gift_to == "":
		hdr.text = "DUFFEL BAG · %d / %d" % [_duffel().size(), DUFFEL_CAP]
	else:
		var c: Dictionary = _campers_by_id.get(for_gift_to, {})
		hdr.text = "GIVE A GIFT TO %s" % String(c.get("display_name", for_gift_to)).to_upper()
	hdr.add_theme_font_size_override("font_size", 13)
	hdr.add_theme_color_override("font_color", C_ACCENT)
	v.add_child(hdr)

	var scroll := ScrollContainer.new()
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(scroll)

	var list := VBoxContainer.new()
	list.add_theme_constant_override("separation", 3)
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(list)

	var duf: Array = _duffel()
	if duf.is_empty():
		var empty := Label.new()
		empty.text = "  empty · your duffel has a slowstick, some clothes, a toothbrush, and a lot of unfilled slots"
		empty.add_theme_font_size_override("font_size", 10)
		empty.add_theme_color_override("font_color", C_TXT_DIM)
		list.add_child(empty)
	else:
		for i in range(duf.size()):
			var item_id: String = String(duf[i])
			var it: Dictionary = _items_by_id.get(item_id, {})
			var row := HBoxContainer.new()
			row.add_theme_constant_override("separation", 8)
			list.add_child(row)
			# Item sprite · pixelart icon on the left, falls through
			# to a small chip if the JSON is missing.
			var icon_sprite := SlowstockSprite.new()
			var icon_path := "res://resources/games/vol7/pirate_summer/sprites/items/" + item_id + ".json"
			if icon_sprite.load_from(icon_path):
				var icon_rect := TextureRect.new()
				icon_rect.texture = icon_sprite.texture()
				icon_rect.custom_minimum_size = Vector2(32, 32)
				icon_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
				row.add_child(icon_rect)
			else:
				var chip := ColorRect.new()
				chip.color = Color(0.5, 0.4, 0.3, 1.0)
				chip.custom_minimum_size = Vector2(32, 32)
				row.add_child(chip)
			var label := Label.new()
			label.text = "  · " + String(it.get("display", item_id))
			label.custom_minimum_size = Vector2(200, 0)
			label.add_theme_font_size_override("font_size", 10)
			label.add_theme_color_override("font_color", C_TXT)
			row.add_child(label)
			var notes := Label.new()
			notes.text = String(it.get("notes", ""))
			notes.add_theme_font_size_override("font_size", 9)
			notes.add_theme_color_override("font_color", C_TXT_DIM)
			notes.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			notes.custom_minimum_size = Vector2(220, 0)
			row.add_child(notes)
			if for_gift_to != "":
				var giftable: bool = bool(it.get("giftable", true))
				var give_btn := Button.new()
				give_btn.text = "  give  "
				give_btn.disabled = not giftable
				var target_id: String = for_gift_to
				var slot: int = i
				give_btn.pressed.connect(func() -> void:
					_give_gift(target_id, slot))
				row.add_child(give_btn)

	var actions := HBoxContainer.new()
	actions.alignment = BoxContainer.ALIGNMENT_END
	v.add_child(actions)

	if for_gift_to != "":
		var cancel := Button.new()
		cancel.text = "  ← never mind  "
		cancel.pressed.connect(func() -> void:
			_close_duffel()
			_open_dialogue(for_gift_to))
		actions.add_child(cancel)
	else:
		var close := Button.new()
		close.text = "  ✕  close  (i / esc)  "
		close.pressed.connect(_close_duffel)
		actions.add_child(close)


func _close_duffel() -> void:
	if _duffel_panel != null and is_instance_valid(_duffel_panel):
		_duffel_panel.queue_free()
	_duffel_panel = null
	_duffel_open = false


# ── Journal panel (key J) ─────────────────────────────────────

func _toggle_journal() -> void:
	if _journal_open:
		_close_journal()
	else:
		_open_journal()


func _open_journal() -> void:
	if _journal_panel != null and is_instance_valid(_journal_panel):
		_journal_panel.queue_free()
	_journal_open = true
	var panel := Panel.new()
	panel.custom_minimum_size = Vector2(720, 520)
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
	_journal_panel = panel

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.add_theme_constant_override("separation", 6)
	panel.add_child(v)

	var hdr := Label.new()
	hdr.text = "SAM'S JOURNAL · %s · %s" % [_current_day_display_name(), _current_block_label()]
	hdr.add_theme_font_size_override("font_size", 13)
	hdr.add_theme_color_override("font_color", C_ACCENT)
	v.add_child(hdr)

	var discovered: Array = _discovered_facts()
	var total: int = _facts_by_id.size()
	var progress := Label.new()
	progress.text = "  facts known · %d of %d  ·  press J or esc to close" % [discovered.size(), total]
	progress.add_theme_font_size_override("font_size", 10)
	progress.add_theme_color_override("font_color", C_TXT_DIM)
	v.add_child(progress)

	var scroll := ScrollContainer.new()
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(scroll)

	var list := VBoxContainer.new()
	list.add_theme_constant_override("separation", 4)
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(list)

	# Two-group render · what Sam knows, followed by silhouettes for
	# what's still out there.  Order within each group by fact
	# authored-order (dict preserves it) so the reveal chain reads.
	_journal_add_section(list, "· KNOWN ·", true, discovered)
	_journal_add_section(list, "· STILL UNKNOWN ·", false, discovered)

	var actions := HBoxContainer.new()
	actions.alignment = BoxContainer.ALIGNMENT_END
	v.add_child(actions)

	var close := Button.new()
	close.text = "  ✕  close  (j / esc)  "
	close.pressed.connect(_close_journal)
	actions.add_child(close)


func _journal_add_section(parent: VBoxContainer, title: String, want_known: bool, discovered: Array) -> void:
	var section_had_any: bool = false
	var section_hdr := Label.new()
	section_hdr.text = title
	section_hdr.add_theme_font_size_override("font_size", 11)
	section_hdr.add_theme_color_override("font_color", C_ACCENT if want_known else C_TXT_DIM)
	parent.add_child(section_hdr)
	for fid_v in _facts_by_id.keys():
		var fid: String = String(fid_v)
		var is_known: bool = discovered.has(fid)
		if is_known != want_known: continue
		section_had_any = true
		var f: Dictionary = _facts_by_id[fid]
		var row := VBoxContainer.new()
		row.add_theme_constant_override("separation", 1)
		parent.add_child(row)
		var line := Label.new()
		if is_known:
			line.text = "  · " + String(f.get("display", fid))
			line.add_theme_color_override("font_color", C_TXT)
		else:
			line.text = "  · · · · · · · · · · · · · · · · ·"
			line.add_theme_color_override("font_color", C_TXT_DIM)
		line.add_theme_font_size_override("font_size", 10)
		row.add_child(line)
	if not section_had_any:
		var empty := Label.new()
		empty.text = "  (nothing here yet)"
		empty.add_theme_font_size_override("font_size", 9)
		empty.add_theme_color_override("font_color", C_TXT_DIM)
		parent.add_child(empty)


func _close_journal() -> void:
	if _journal_panel != null and is_instance_valid(_journal_panel):
		_journal_panel.queue_free()
	_journal_panel = null
	_journal_open = false


func _give_gift(target_id: String, slot: int) -> void:
	var duf: Array = _duffel()
	if slot < 0 or slot >= duf.size(): return
	var item_id: String = String(duf[slot])
	var it: Dictionary = _items_by_id.get(item_id, {})
	if not bool(it.get("giftable", true)): return
	var c: Dictionary = _campers_by_id.get(target_id, {})
	# +2 if preferred, +2 if wildcard, else +1.
	var bump := 1
	if bool(it.get("wildcard", false)):
		bump = 1
	else:
		var prefs: Array = c.get("preferred_items", [])
		var aliases: Array = it.get("aliases", [])
		for a in aliases:
			for p in prefs:
				if String(a).to_lower() == String(p).to_lower():
					bump = 2
					break
			if bump == 2: break
	# Remove from duffel.
	duf.remove_at(slot)
	_run_state["duffel"] = duf
	_bump_friendship(target_id, bump)
	_close_duffel()
	# Show the response.
	var name := String(c.get("display_name", target_id))
	var line := "  You gave " + name + " the " + String(it.get("display", item_id)) + "."
	if bump >= 2:
		line += "  They light up · they had been hoping for exactly that."
	else:
		line += "  They thank you · they'll remember it."
	_show_transient(line)


var _transient_lbl: Label = null

var _hero_overlay: Control = null

func _show_hero(hero_id: String, caption: String = "") -> void:
	# Centered pixel-art moment card · lives in the HUD CanvasLayer
	# so F4 hides it.  Auto-dismisses after ~6s.
	if _hero_overlay != null and is_instance_valid(_hero_overlay):
		_hero_overlay.queue_free()
	var hero_path := "res://resources/games/vol7/pirate_summer/sprites/scenes/" + hero_id + ".json"
	if not FileAccess.file_exists(hero_path):
		push_warning("[hero] missing " + hero_path)
		return
	var h := HeroImage.new()
	if not h.load_from(hero_path):
		push_warning("[hero] load failed " + hero_id)
		return
	var overlay := Control.new()
	overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	overlay.mouse_filter = Control.MOUSE_FILTER_STOP
	var bg := ColorRect.new()
	bg.color = Color(0.0, 0.0, 0.0, 0.86)
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	overlay.add_child(bg)
	var img := TextureRect.new()
	img.texture = h.texture(Vector2i(640, 360))
	img.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	img.set_anchors_preset(Control.PRESET_FULL_RECT)
	img.offset_top = 30
	img.offset_bottom = -60
	img.offset_left = 60
	img.offset_right = -60
	overlay.add_child(img)
	if caption != "":
		var cap := Label.new()
		cap.text = caption
		cap.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		cap.add_theme_font_size_override("font_size", 12)
		cap.add_theme_color_override("font_color", C_ACCENT)
		cap.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
		cap.offset_top = -40
		cap.offset_bottom = -8
		overlay.add_child(cap)
	_hud_layer.add_child(overlay)
	_hero_overlay = overlay
	get_tree().create_timer(6.0).timeout.connect(func() -> void:
		if _hero_overlay != null and is_instance_valid(_hero_overlay):
			_hero_overlay.queue_free()
			_hero_overlay = null)


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
