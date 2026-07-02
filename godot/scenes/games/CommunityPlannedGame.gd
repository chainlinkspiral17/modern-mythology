# CommunityPlannedGame.gd
# ════════════════════════════════════════════════════════════════
# COMMUNITY PLANNED — Frasier's grand-strategy gallery game.
# Phase 1 white-box per lore/_COMMUNITY_PLANNED_SPEC.md: three
# regions on a static background, dispatch as a list of buttons,
# problems and agents from JSON. The strategic layer playable as
# a spreadsheet game. The burn-vs-obligation-vs-corruption economy
# proves out here. BBS layer (phase 2) and the hookup (phase 3)
# come later.
#
# Turn = a day. ~100 turns = Memorial Day → Labor Day. Each turn:
#   1. Resolve any returning dispatches.
#   2. Tick problem severities (per-template tick_per_day).
#   3. Tick escalation clocks; spawn new problems when they tick over.
#   4. Player dispatches 0-3 agents.
#   5. Advance day.
# ════════════════════════════════════════════════════════════════
extends Control

const DATA_ROOT := "res://resources/games/community_planned/"
# Three-slot save system. The active slot is persisted in
# user://saves/community_planned_active_slot.txt so the next game
# session resumes where the player left off; the slot picker
# always opens on _ready so the player can switch slots without
# leaving the game.
const SAVE_DIR := "user://saves/"
const ACTIVE_SLOT_PATH := "user://saves/community_planned_active_slot.txt"
const NUM_SAVE_SLOTS := 3
var _current_slot: int = 0


func _save_path_for_slot(slot: int) -> String:
	return SAVE_DIR + "community_planned_slot_%d.json" % slot


# Compatibility shim. Reads the *current* slot's path; older code
# paths that used the const SAVE_PATH still resolve.
var SAVE_PATH: String:
	get:
		return _save_path_for_slot(_current_slot)
# v1: phase 1 schema (strategic layer only)
# v2: phase 2 schema (adds BBS read-state: visited_bbs_ids,
#     read_thread_ids, dialled_numbers, bbs_session_history,
#     readmitted_to_snacks). v1 saves migrate forward with the
#     new fields initialised empty.
const SAVE_VERSION := 2
const TURNS_TOTAL := 100
const MAX_DISPATCHES_PER_DAY := 3
# Spec: "Each region generates 1-3 problems depending on how
# exposed it currently is." Hard cap above keeps any one column
# legible. Weekly spawn pass on Sunday clamps to this.
const MAX_PROBLEMS_PER_REGION := 4
# Day 1 = Memorial Day = Monday (last Monday in May, canonically).
# Sundays therefore land on day 7, 14, 21, ... Spec: "Six 'quiet'
# days where Frasier just runs the board, then one BBS night
# where everything decompresses." The Sunday tick fires the
# weekly problem spawn and (in phase 2) opens the BBS night.
const DAY_NAMES := ["Monday", "Tuesday", "Wednesday", "Thursday",
                    "Friday", "Saturday", "Sunday"]

var _regions: Dictionary = {}    # id → region def
var _agents: Dictionary = {}     # id → agent def
var _problem_templates: Dictionary = {}  # id → template def
var _dean: Dictionary = {}                # full dean.json
var _interludes_def: Dictionary = {}      # full interludes.json
var _vignettes_def: Dictionary = {}       # full daily_vignettes.json
var _regional_events_pool: Array = []     # regional_events.json events[]
var _fired_regional_events: Array = []    # event_ids that have fired (never repeat)
var _active_regional_markers: Array = []  # [{marker_id, region_id, expires_on_day, log_line, expiry_line}]
var _vignettes_fired: Array = []          # ids of one-shots already fired
var _last_vignette_id: String = ""        # avoid back-to-back repeat
var _interlude_meta: Dictionary = {}      # per-interlude metadata (day earned, ...)
# Accumulators read by interlude earn predicates. Bumped on
# resolution / dispatch / day-tick.
var _problem_resolved_counts: Dictionary = {}    # template_id → count
var _problem_resolved_by_region: Dictionary = {} # region_id → count
var _agent_dispatch_counts: Dictionary = {}      # agent_id → int

# Phase 2 · BBS layer state (save_version 2+).
var _bbs_visited_ids: Array = []      # bbses dialled to date
var _bbs_read_thread_ids: Array = []  # threads read across the summer
var _bbs_dialled_numbers: Array = []  # numbers entered in dialer (for hidden-board clues)
var _readmitted_to_snacks: bool = false  # flips W2 via WIRE_MOTHER DM
# DM read pointers: canonical_character_id → last week read.
# Persisted; advanced on each BBS night when the player opens a DM.
var _dm_read_to_week: Dictionary = {}
# DM reply log: list of {canonical, week, option_idx, label, effects}.
# Append-only across the summer; effects already applied at hang_up.
var _dm_reply_log: Array = []
# Hidden-board discovery state: hidden_board_id → true. Persistent
# across the run; passed into BBS.open(), merged from session on
# hang_up.
var _bbs_discovered_hidden_boards: Dictionary = {}
# Generic state buckets that DM reply effects (and later, board
# choices) write into. The strategic engine + reveals.json read
# from these in addition to the per-region state.
var _flags: Dictionary = {}              # flag → bool
var _counters: Dictionary = {}           # counter → int
var _queued_burns: Array = []            # [{trigger_day, reason}]
var _canon_vars: Dictionary = {}         # key → variant (canonized facts)
var _unlocked_artifacts: Array = []      # artifact ids on the shelf
var _tower_brightness: String = "dim"     # dim / warming / bright / white
var _last_brightness_change_day: int = 0
var _anomalies_observed: int = 0
var _fingerprints_observed: int = 0
var _dean_interludes_earned: Array = []   # ids
var _tower_state_revealed_white_once: bool = false

# Reveal state — what the player has been shown so far. The game
# opens narrow and unfolds over the first three weeks per
# reveals.json. Each flag, once on, stays on.
var _reveals_def: Dictionary = {}            # full reveals.json
var _reveals_fired: Dictionary = {}          # id → bool
var _visible_regions: Array = []             # region ids currently on the map
var _visible_agents: Array = []              # agent ids currently in the roster
var _eligible_problem_types: Array = []      # problem types the escalation clock may spawn
var _ui_flags: Dictionary = {}               # ui-reveal flags (tower_visible, show_*_values, ...)

# Runtime state.
var _day: int = 1
var _dispatches_this_day: int = 0
var _active_dispatches: Array = []  # [{agent_id, target_problem, region, days_remaining, ...}]
var _region_state: Dictionary = {}  # region_id → {held_nodes, insight, cover, courier, escalation_progress, active_problems}
var _agent_state: Dictionary = {}   # agent_id → {burn, corruption, complexity, obligation, on_dispatch}
var _log_lines: PackedStringArray = PackedStringArray()
var _interlude_shelf: Array = []  # list of unlocked interlude ids

@onready var _day_label: Label = $VBox/HeaderBar/DayLabel
@onready var _dispatches_label: Label = $VBox/HeaderBar/DispatchesLabel
@onready var _region_panels_box: HBoxContainer = $VBox/RegionsRow
@onready var _agent_list_box: VBoxContainer = $VBox/BottomRow/AgentScroll/AgentList
@onready var _log_label: RichTextLabel = $VBox/BottomRow/LogScroll/LogLabel
@onready var _advance_button: Button = $VBox/BottomRow/Actions/AdvanceDayButton
@onready var _new_game_button: Button = $VBox/BottomRow/Actions/NewGameButton
@onready var _back_button: Button = $VBox/BottomRow/Actions/BackButton
@onready var _save_status_label: Label = $VBox/BottomRow/Actions/SaveStatusLabel
@onready var _shelf_button: Button = $VBox/HeaderBar/ShelfButton
@onready var _today_header: Label = $VBox/BottomRow/Actions/TodayHeader
@onready var _today_box: VBoxContainer = $VBox/BottomRow/Actions/TodayBox


func _ready() -> void:
	_load_data()
	_build_ui()
	# Three-slot save picker fires before any state load. The player
	# picks a slot; the slot's save is loaded (or a new game starts
	# in that slot). The picker remembers the active slot via
	# ACTIVE_SLOT_PATH so reopening the scene defaults to the last-
	# played slot.
	_current_slot = _read_active_slot()
	call_deferred("_show_slot_picker")


func _begin_session_with_slot(slot: int) -> void:
	_current_slot = slot
	_write_active_slot(slot)
	if _try_load_save():
		_log("[color=#a8c0a8]Loaded slot %d — day %d.[/color]" % [slot + 1, _day])
	else:
		_init_state()
		_log("Slot %d · Day %d · Memorial Day. The summer begins." % [slot + 1, _day])
	_render()
	if not bool(_flags.get("summer_intro_shown", false)):
		call_deferred("_show_summer_intro")
	# Kick off the summer's ambient BGM. Uses the strategic-day track
	# so the sound-world matches the day-to-day loop. Ducks under the
	# BBS-night overlay's own BGM when the overlay opens (Sunday nights)
	# and returns to this track when the BBS overlay hangs up.
	_audio_play_bgm_for_current_state()


func _read_active_slot() -> int:
	if not FileAccess.file_exists(ACTIVE_SLOT_PATH):
		return 0
	var f := FileAccess.open(ACTIVE_SLOT_PATH, FileAccess.READ)
	if f == null:
		return 0
	var raw: String = f.get_as_text().strip_edges()
	var v: int = int(raw)
	if v < 0 or v >= NUM_SAVE_SLOTS:
		return 0
	return v


func _write_active_slot(slot: int) -> void:
	DirAccess.make_dir_recursive_absolute(SAVE_DIR)
	var f := FileAccess.open(ACTIVE_SLOT_PATH, FileAccess.WRITE)
	if f == null:
		return
	f.store_string(str(slot))


func _slot_summary(slot: int) -> Dictionary:
	# Returns {empty: bool, day: int, finale_done: bool, season_label: String}.
	var path: String = _save_path_for_slot(slot)
	if not FileAccess.file_exists(path):
		return {"empty": true, "day": 0, "finale_done": false, "season_label": "empty"}
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return {"empty": true, "day": 0, "finale_done": false, "season_label": "empty"}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	if typeof(parsed) != TYPE_DICTIONARY:
		return {"empty": true, "day": 0, "finale_done": false, "season_label": "empty"}
	var d: Dictionary = parsed
	var day_n: int = int(d.get("day", 1))
	var flags: Dictionary = d.get("flags", {})
	var finale_done: bool = bool(flags.get("labor_day_finale_shown", false))
	var label: String
	if finale_done:
		label = "Labor Day · summer complete"
	else:
		label = "day %d · %s" % [day_n, _day_label_short(day_n)]
	return {"empty": false, "day": day_n, "finale_done": finale_done, "season_label": label}


func _day_label_short(day_n: int) -> String:
	if day_n <= 1:
		return "Memorial Day"
	if day_n >= 100:
		return "Labor Day"
	var week: int = int(ceil(float(day_n) / 7.0))
	return "week %d" % week


func _show_slot_picker() -> void:
	var dlg := AcceptDialog.new()
	dlg.title = "COMMUNITY PLANNED · slot"
	dlg.min_size = Vector2(560, 420)
	dlg.get_ok_button().visible = false  # No OK — pick a slot or close window.
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 10)
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	dlg.add_child(col)
	var hdr := Label.new()
	hdr.text = "Pick a slot. Three summers fit on the desk."
	hdr.add_theme_font_size_override("font_size", 13)
	hdr.add_theme_color_override("font_color", Color(0.96, 0.86, 0.62, 1))
	col.add_child(hdr)
	for slot in range(NUM_SAVE_SLOTS):
		var summary: Dictionary = _slot_summary(slot)
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 10)
		col.add_child(row)
		var btn := Button.new()
		btn.text = "Slot %d · %s" % [slot + 1, String(summary["season_label"])]
		btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		btn.add_theme_font_size_override("font_size", 12)
		var slot_capture: int = slot
		btn.pressed.connect(func() -> void:
			dlg.queue_free()
			_begin_session_with_slot(slot_capture))
		row.add_child(btn)
		# Wipe affordance only for non-empty slots.
		if not bool(summary["empty"]):
			var wipe_btn := Button.new()
			wipe_btn.text = "wipe"
			wipe_btn.focus_mode = Control.FOCUS_NONE
			wipe_btn.add_theme_font_size_override("font_size", 10)
			var slot_w: int = slot
			wipe_btn.pressed.connect(func() -> void:
				_confirm_wipe_slot(slot_w, dlg))
			row.add_child(wipe_btn)
	dlg.add_to_group("ui")
	add_child(dlg)
	dlg.popup_centered()


func _confirm_wipe_slot(slot: int, parent_dlg: AcceptDialog) -> void:
	var confirm := ConfirmationDialog.new()
	confirm.title = "Wipe Slot %d?" % (slot + 1)
	confirm.dialog_text = "Erase the save in slot %d. This can't be undone." % (slot + 1)
	confirm.confirmed.connect(func() -> void:
		var path: String = _save_path_for_slot(slot)
		if FileAccess.file_exists(path):
			DirAccess.remove_absolute(path)
		confirm.queue_free()
		# Refresh the picker.
		parent_dlg.queue_free()
		_show_slot_picker())
	confirm.canceled.connect(func() -> void: confirm.queue_free())
	confirm.add_to_group("ui")
	add_child(confirm)
	confirm.popup_centered()


# ── Data loading ─────────────────────────────────────────────────
func _load_data() -> void:
	var regions_json: Dictionary = _load_json(DATA_ROOT + "regions.json")
	for r in regions_json.get("regions", []):
		_regions[r["id"]] = r
	var agents_json: Dictionary = _load_json(DATA_ROOT + "agents.json")
	for a in agents_json.get("demons", []):
		_agents[a["id"]] = a
	for a in agents_json.get("humans", []):
		_agents[a["id"]] = a
	var problems_json: Dictionary = _load_json(DATA_ROOT + "problems.json")
	for t in problems_json.get("templates", []):
		_problem_templates[t["id"]] = t
	_dean = _load_json(DATA_ROOT + "dean.json")
	_tower_brightness = "dim"
	_last_brightness_change_day = 0
	_reveals_def = _load_json(DATA_ROOT + "reveals.json")
	_interludes_def = _load_json(DATA_ROOT + "interludes.json")
	_vignettes_def = _load_json(DATA_ROOT + "daily_vignettes.json")
	# Weekly regional events (2026-07-02) · JSON-driven pool.
	# Replaces the earlier 5-week cycle of hardcoded flavor lines.
	var regional_events_json: Dictionary = _load_json(DATA_ROOT + "regional_events.json")
	_regional_events_pool = regional_events_json.get("events", [])
	_validate_canonical_character_links()


# Soft validation: every agent's canonical_character_id should map
# to an entry in resources/characters/_index.json, and the
# registry's reciprocal pointer (lore_links.community_planned_agent)
# should match this agent's id. Push warnings — never crash — so
# the data layer stays soft. The registry contract: edits to
# canon-affecting biography go in the registry; both consumer
# systems can be trusted to render the local mechanical shape.
func _validate_canonical_character_links() -> void:
	var registry: Dictionary = _load_json("res://resources/characters/_index.json")
	if registry.is_empty():
		return
	var by_id: Dictionary = {}
	for entry in registry.get("characters", []):
		by_id[String(entry["id"])] = entry
	for a_id in _agents:
		var a: Dictionary = _agents[a_id]
		var canon_id: String = String(a.get("canonical_character_id", ""))
		if canon_id == "":
			continue
		if not by_id.has(canon_id):
			push_warning("[CommunityPlanned] agent %s → canonical_character_id %s not in registry" %
				[a_id, canon_id])
			continue
		var canon: Dictionary = by_id[canon_id]
		var back: String = String(canon.get("lore_links", {}).get("community_planned_agent", ""))
		if back != a_id:
			push_warning("[CommunityPlanned] registry %s · lore_links.community_planned_agent is '%s', expected '%s'" %
				[canon_id, back, a_id])


func _load_json(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		push_error("CommunityPlanned: missing data file " + path)
		return {}
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("CommunityPlanned: bad JSON shape in " + path)
		return {}
	return parsed


# ── State init ───────────────────────────────────────────────────
func _init_state() -> void:
	for r_id in _regions:
		var r: Dictionary = _regions[r_id]
		_region_state[r_id] = {
			"held_nodes": (r.get("starting_nodes", []) as Array).duplicate(),
			"contested_nodes": (r.get("contested_nodes_at_start", []) as Array).duplicate(),
			"target_nodes": (r.get("target_nodes", []) as Array).duplicate(),
			"insight": int(r.get("starting_insight", 0)),
			"cover": int(r.get("starting_cover", 0)),
			"courier_capacity": int(r.get("starting_courier_capacity", 0)),
			"escalation_progress": 0.0,
			"active_problems": [],
			"failed_plants": 0,
		}
	for a_id in _agents:
		_agent_state[a_id] = {
			"burn": 0,
			"corruption": 0,
			"complexity": int(_agents[a_id].get("complexity", 0)),
			"obligation": 0,
			"on_dispatch": false,
			"return_day": 0,
		}
	# Apply reveal-state overrides: only Graustark and four agents
	# visible at the start; only memorial_grief eligible to spawn.
	# The game opens narrow per reveals.json §starting_state_overrides.
	var ov: Dictionary = _reveals_def.get("starting_state_overrides", {})
	_visible_regions = ov.get("regions_visible", _regions.keys()).duplicate()
	_visible_agents = ov.get("agents_visible", _agents.keys()).duplicate()
	_eligible_problem_types = ov.get("problem_types_eligible_at_start", []).duplicate()
	_ui_flags = {
		"tower_visible": bool(ov.get("tower_visible", true)),
		"show_demon_economy_numbers": bool(ov.get("show_demon_economy_numbers", true)),
		"show_resource_economy_numbers": bool(ov.get("show_resource_economy_numbers", true)),
		"show_corruption_values": bool(ov.get("show_corruption_values", true)),
		"show_complexity_values": bool(ov.get("show_complexity_values", true)),
		"show_obligation_values": bool(ov.get("show_obligation_values", true)),
		"dean_interludes_visible": bool(ov.get("dean_interludes_visible", false)),
	}
	_reveals_fired = {}
	# Seed one starter problem in the only visible region.
	_seed_problem("graustark", "memorial_grief")


func _seed_problem(region_id: String, template_id: String) -> void:
	var t: Dictionary = _problem_templates.get(template_id, {})
	if t.is_empty():
		return
	var st: Dictionary = _region_state.get(region_id, {})
	if st.is_empty():
		return
	# Cap: never exceed the per-region active-problem maximum.
	var active: Array = st.get("active_problems", [])
	if active.size() >= MAX_PROBLEMS_PER_REGION:
		return
	# Dedupe: refuse to seed a template that's already active in
	# this region. Lets a different template of the same type stack
	# (e.g. surveillance + missing_kid can coexist), but prevents
	# a 4th identical surveillance row showing up.
	for p in active:
		if String(p.get("template_id", "")) == template_id:
			return
	active.append({
		"template_id": template_id,
		"title": t["title"],
		"severity": float(t.get("base_severity", 1)),
		"effort_remaining": float(t.get("effort_to_resolve", 2)),
		"in_progress_by": "",
		"day_spawned": _day,
	})
	st["active_problems"] = active


# Day 1 = Memorial Day = Monday. Sunday lands on day 7, 14, 21, ...
func _is_sunday(d: int) -> bool:
	return d > 0 and d % 7 == 0


func _day_of_week(d: int) -> String:
	if d <= 0: return ""
	return DAY_NAMES[(d - 1) % 7]


# ── Save / load ──────────────────────────────────────────────────
# Single-slot autosave at the canonical SAVE_PATH. Writes on each
# ADVANCE DAY. Loads automatically on scene open if a save exists.
# The header bar exposes a "NEW GAME" button that wipes the slot
# and re-seeds from data.
func _collect_state() -> Dictionary:
	return {
		"save_version": SAVE_VERSION,
		"day": _day,
		"dispatches_this_day": _dispatches_this_day,
		"active_dispatches": _active_dispatches,
		"region_state": _region_state,
		"agent_state": _agent_state,
		"log_lines": Array(_log_lines),
		"interlude_shelf": _interlude_shelf,
		"tower_brightness": _tower_brightness,
		"last_brightness_change_day": _last_brightness_change_day,
		"anomalies_observed": _anomalies_observed,
		"fingerprints_observed": _fingerprints_observed,
		"dean_interludes_earned": _dean_interludes_earned,
		"tower_state_revealed_white_once": _tower_state_revealed_white_once,
		"reveals_fired": _reveals_fired,
		"visible_regions": _visible_regions,
		"visible_agents": _visible_agents,
		"eligible_problem_types": _eligible_problem_types,
		"ui_flags": _ui_flags,
		"interlude_meta": _interlude_meta,
		"problem_resolved_counts": _problem_resolved_counts,
		"problem_resolved_by_region": _problem_resolved_by_region,
		"agent_dispatch_counts": _agent_dispatch_counts,
		"bbs_visited_ids": _bbs_visited_ids,
		"bbs_read_thread_ids": _bbs_read_thread_ids,
		"bbs_dialled_numbers": _bbs_dialled_numbers,
		"readmitted_to_snacks": _readmitted_to_snacks,
		"dm_read_to_week": _dm_read_to_week,
		"dm_reply_log": _dm_reply_log,
		"bbs_discovered_hidden_boards": _bbs_discovered_hidden_boards,
		"flags": _flags,
		"counters": _counters,
		"queued_burns": _queued_burns,
		"canon_vars": _canon_vars,
		"unlocked_artifacts": _unlocked_artifacts,
		"vignettes_fired": _vignettes_fired,
		"last_vignette_id": _last_vignette_id,
		"fired_regional_events": _fired_regional_events,
		"active_regional_markers": _active_regional_markers,
	}


func _apply_state(d: Dictionary) -> void:
	_day = int(d.get("day", 1))
	_dispatches_this_day = int(d.get("dispatches_this_day", 0))
	_active_dispatches = d.get("active_dispatches", [])
	_region_state = d.get("region_state", {})
	_agent_state = d.get("agent_state", {})
	_log_lines = PackedStringArray(d.get("log_lines", []))
	_interlude_shelf = d.get("interlude_shelf", [])
	_tower_brightness = String(d.get("tower_brightness", "dim"))
	_last_brightness_change_day = int(d.get("last_brightness_change_day", 0))
	_anomalies_observed = int(d.get("anomalies_observed", 0))
	_fingerprints_observed = int(d.get("fingerprints_observed", 0))
	_dean_interludes_earned = d.get("dean_interludes_earned", [])
	_tower_state_revealed_white_once = bool(d.get("tower_state_revealed_white_once", false))
	_reveals_fired = d.get("reveals_fired", {})
	_visible_regions = d.get("visible_regions", ["graustark"])
	_visible_agents = d.get("visible_agents", ["john_frank", "nicola", "vagrant", "moth"])
	_eligible_problem_types = d.get("eligible_problem_types", ["memorial_grief"])
	_ui_flags = d.get("ui_flags", {})
	_interlude_meta = d.get("interlude_meta", {})
	_problem_resolved_counts = d.get("problem_resolved_counts", {})
	_problem_resolved_by_region = d.get("problem_resolved_by_region", {})
	_agent_dispatch_counts = d.get("agent_dispatch_counts", {})
	_bbs_visited_ids = d.get("bbs_visited_ids", [])
	_bbs_read_thread_ids = d.get("bbs_read_thread_ids", [])
	_bbs_dialled_numbers = d.get("bbs_dialled_numbers", [])
	_readmitted_to_snacks = bool(d.get("readmitted_to_snacks", false))
	_dm_read_to_week = d.get("dm_read_to_week", {})
	_dm_reply_log = d.get("dm_reply_log", [])
	_bbs_discovered_hidden_boards = d.get("bbs_discovered_hidden_boards", {})
	_flags = d.get("flags", {})
	_counters = d.get("counters", {})
	_queued_burns = d.get("queued_burns", [])
	_canon_vars = d.get("canon_vars", {})
	_unlocked_artifacts = d.get("unlocked_artifacts", [])
	_vignettes_fired = d.get("vignettes_fired", [])
	_last_vignette_id = String(d.get("last_vignette_id", ""))
	_fired_regional_events = d.get("fired_regional_events", [])
	_active_regional_markers = d.get("active_regional_markers", [])


func _write_save() -> void:
	DirAccess.make_dir_recursive_absolute("user://saves")
	var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f == null:
		push_error("[CommunityPlanned] could not write save to %s" % SAVE_PATH)
		return
	f.store_string(JSON.stringify(_collect_state(), "  "))
	if _save_status_label != null:
		_save_status_label.text = "slot %d · save: day %d (autosaved)" % [_current_slot + 1, _day]


func _try_load_save() -> bool:
	if not FileAccess.file_exists(SAVE_PATH):
		return false
	var f := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if f == null:
		return false
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("[CommunityPlanned] save file unreadable; ignoring")
		return false
	var d: Dictionary = parsed
	var v: int = int(d.get("save_version", 0))
	if v != SAVE_VERSION:
		# Migrate forward. v1 → v2 is additive: BBS fields default
		# to empty arrays / false. The strategic state is unchanged.
		if v == 1:
			d = _migrate_save_v1_to_v2(d)
		else:
			push_warning("[CommunityPlanned] save_version %d not migratable to %d — discarding" % [v, SAVE_VERSION])
			return false
	_apply_state(d)
	return true


# Additive forward migration. v1 saves were phase 1 only; v2
# extends with the BBS layer fields. No v1 data is rewritten;
# we just default the new fields so _apply_state reads cleanly.
# Seeds every v2 field explicitly so the migration is legible vs
# leaning on _apply_state defaults for the rest.
#
# NOTE (2026-07-01): Everything added post-v2 is additive:
#   · Mission stages (stage_index / is_staged / effort_accumulated /
#     next_stage_day on dispatch entries) default via .get() at read
#     time — a v2 save loads cleanly and any un-staged dispatch simply
#     never enters the stages code path.
#   · Three save slots — the slot lives in the file path
#     (_save_path_for_slot), not in the save itself, so slot state
#     doesn't affect the save format.
#   · Mid-summer pressure curve — purely computational, no save state.
# If a future change is NOT additive, bump SAVE_VERSION to 3 and add
# _migrate_save_v2_to_v3() following this template.
func _migrate_save_v1_to_v2(d: Dictionary) -> Dictionary:
	d["save_version"] = 2
	# BBS layer (phase 2 sprint 1)
	d["bbs_visited_ids"] = []
	d["bbs_read_thread_ids"] = []
	d["bbs_dialled_numbers"] = []
	d["readmitted_to_snacks"] = false
	# BBS layer (phase 2 sprint 2 — DMs + effect interpreter buckets)
	d["dm_read_to_week"] = {}
	d["dm_reply_log"] = []
	d["flags"] = {}
	d["counters"] = {}
	d["queued_burns"] = []
	d["canon_vars"] = {}
	d["unlocked_artifacts"] = []
	# BBS layer (phase 2 sprint 4 — hidden boards)
	d["bbs_discovered_hidden_boards"] = {}
	return d


func _wipe_save_and_restart() -> void:
	if FileAccess.file_exists(SAVE_PATH):
		# DirAccess.remove_absolute takes a res://-or-user:// path,
		# not an OS path. Pass SAVE_PATH straight through.
		DirAccess.remove_absolute(SAVE_PATH)
	# Clear in-memory state then re-init.
	_active_dispatches.clear()
	_region_state.clear()
	_agent_state.clear()
	_log_lines = PackedStringArray()
	_interlude_shelf.clear()
	_tower_brightness = "dim"
	_last_brightness_change_day = 0
	_anomalies_observed = 0
	_fingerprints_observed = 0
	_dean_interludes_earned.clear()
	_tower_state_revealed_white_once = false
	_reveals_fired.clear()
	_visible_regions.clear()
	_visible_agents.clear()
	_eligible_problem_types.clear()
	_ui_flags.clear()
	_day = 1
	_dispatches_this_day = 0
	_init_state()
	_log("Day 1 · Memorial Day. The summer begins.")
	_render()


# ── Effect interpreter ──────────────────────────────────────────
# The single dispatch point for the effect-array data declared in
# problems.json (threshold effects) and agents.json (failure
# effects). Every effect runs against a context dict:
#   {region_id: String, agent_id: String, problem: Dictionary}
# Resolves "current" region/problem references against ctx. Unknown
# kinds log a warning rather than crash so a future data field can
# fail soft.
func _exec_effects(effects: Array, ctx: Dictionary) -> void:
	for eff in effects:
		if typeof(eff) == TYPE_DICTIONARY:
			_exec_effect(eff, ctx)


func _exec_effect(eff: Dictionary, ctx: Dictionary) -> void:
	var kind: String = String(eff.get("kind", ""))
	var rng := RandomNumberGenerator.new()
	rng.randomize()
	match kind:
		"log":
			_log(String(eff.get("text", "")))
		"increment_region_state":
			var r_id := _resolve_region(String(eff.get("region", "current")), ctx)
			var key: String = String(eff.get("key", ""))
			var amt: float = float(eff.get("amount", 1))
			if _region_state.has(r_id) and key != "":
				_region_state[r_id][key] = float(_region_state[r_id].get(key, 0)) + amt
		"decrement_region_state":
			var r_id2 := _resolve_region(String(eff.get("region", "current")), ctx)
			var key2: String = String(eff.get("key", ""))
			var amt2: float = float(eff.get("amount", 1))
			if _region_state.has(r_id2) and key2 != "":
				_region_state[r_id2][key2] = float(_region_state[r_id2].get(key2, 0)) - amt2
		"set_global_state":
			# Persisted into region_state under a "_globals" sub-dict so
			# save_state captures it without a new top-level field.
			if not _region_state.has("_globals"):
				_region_state["_globals"] = {}
			(_region_state["_globals"] as Dictionary)[String(eff.get("key", ""))] = eff.get("value", null)
		"spawn_problem_in_region":
			var r_id3 := _resolve_region(String(eff.get("region", "current")), ctx)
			var template: String = String(eff.get("template", eff.get("problem_template", "")))
			if r_id3 != "" and template != "":
				_seed_problem(r_id3, template)
				_log("[i]Cascade:[/i] %s spawned in %s." %
					[_problem_templates.get(template, {}).get("title", template),
					 _regions.get(r_id3, {}).get("name", r_id3)])
		"spawn_problem_in_neighbor":
			# White-box "neighbor" = a random other region.
			var here: String = String(ctx.get("region_id", ""))
			var others: Array = []
			for k in _regions.keys():
				if k != here: others.append(k)
			if others.is_empty(): return
			var pick: String = String(others[rng.randi() % others.size()])
			var tpl: String = String(eff.get("problem_template", eff.get("template", "")))
			if tpl != "":
				_seed_problem(pick, tpl)
				_log("[i]Spillover:[/i] %s in %s." %
					[_problem_templates.get(tpl, {}).get("title", tpl),
					 _regions.get(pick, {}).get("name", pick)])
		"spawn_problem_in_all_regions":
			var tpl2: String = String(eff.get("problem_template", eff.get("template", "")))
			if tpl2 == "": return
			for k in _regions.keys():
				_seed_problem(k, tpl2)
			_log("[i]Wide spillover:[/i] %s landed in all three regions." %
				_problem_templates.get(tpl2, {}).get("title", tpl2))
		"lose_node":
			var r_id4 := _resolve_region(String(eff.get("region", "current")), ctx)
			var node: String = String(eff.get("node", ""))
			var days: int = int(eff.get("days", 7))
			if _region_state.has(r_id4):
				var st: Dictionary = _region_state[r_id4]
				if String(node) == "any_with_problem" and ctx.has("problem"):
					# Use the problem's region as the lose target (still r_id4).
					pass
				if (st["held_nodes"] as Array).has(node):
					(st["held_nodes"] as Array).erase(node)
					if not st.has("dark_nodes"):
						st["dark_nodes"] = []
					(st["dark_nodes"] as Array).append({"node": node, "until_day": _day + days})
					_log("[color=#ff9090]%s went dark in %s for %d days.[/color]" %
						[node, _regions[r_id4]["name"], days])
		"temporarily_lose_node":
			# Like lose_node but picks from a pool when node isn't named.
			var r_id5 := _resolve_region(String(eff.get("region", "current")), ctx)
			var pool: String = String(eff.get("node_pool", ""))
			var days2: int = int(eff.get("days", 7))
			if _region_state.has(r_id5):
				var held: Array = _region_state[r_id5]["held_nodes"]
				if not held.is_empty():
					var pick_node: String = String(held[rng.randi() % held.size()])
					held.erase(pick_node)
					var st2: Dictionary = _region_state[r_id5]
					if not st2.has("dark_nodes"):
						st2["dark_nodes"] = []
					(st2["dark_nodes"] as Array).append({"node": pick_node, "until_day": _day + days2})
					_log("[color=#ff9090]%s (%s pool) dark in %s for %d days.[/color]" %
						[pick_node, pool, _regions[r_id5]["name"], days2])
		"lose_contested_node":
			var r_id6 := _resolve_region(String(eff.get("region", "current")), ctx)
			var node2: String = String(eff.get("node", ""))
			if _region_state.has(r_id6):
				var contested: Array = _region_state[r_id6]["contested_nodes"]
				if contested.has(node2):
					contested.erase(node2)
				if not _region_state[r_id6].has("dean_held_nodes"):
					_region_state[r_id6]["dean_held_nodes"] = []
				(_region_state[r_id6]["dean_held_nodes"] as Array).append(node2)
				_log("[color=#ff9090]%s in %s lost to the resistance.[/color]" %
					[node2, _regions[r_id6]["name"]])
		"remove_target_node":
			var r_id7 := _resolve_region(String(eff.get("region", "current")), ctx)
			var targets: Array = _region_state[r_id7].get("target_nodes", [])
			if not targets.is_empty():
				var idx: int = rng.randi() % targets.size()
				var removed: String = String(targets[idx])
				targets.remove_at(idx)
				_log("[color=#ff9090]The ground refused: %s removed from %s targets.[/color]" %
					[removed, _regions[r_id7]["name"]])
		"set_region_modifier":
			var r_id8 := _resolve_region(String(eff.get("region", "current")), ctx)
			var mkey: String = String(eff.get("key", ""))
			var mval = eff.get("value", 1.0)
			var mdays: int = int(eff.get("days", 7))
			if _region_state.has(r_id8) and mkey != "":
				if not _region_state[r_id8].has("modifiers"):
					_region_state[r_id8]["modifiers"] = {}
				_region_state[r_id8]["modifiers"][mkey] = {
					"value": mval, "until_day": _day + mdays
				}
		"advance_visitor_drift":
			# Logged for the BBS layer to read later (phase 2).
			_log("[i]Drift:[/i] %s moves a step on its arc." %
				String(eff.get("target", "(unspecified)")))
		"leak_carried_item_to_dean_or_resistance":
			_log("[color=#c8a8ff]The carry was intercepted. The item is also in someone else's hand now.[/color]")
		"turn_demon":
			# White-box: pick the demon currently in Small Wood with the
			# highest corruption and mark it locked.
			var best_id: String = ""
			var best_corr: int = -1
			for ag_id in _agent_state:
				if String(_agents[ag_id].get("class", "")) != "demon":
					continue
				if int(_agent_state[ag_id]["corruption"]) > best_corr:
					best_corr = int(_agent_state[ag_id]["corruption"])
					best_id = ag_id
			if best_id != "":
				_agent_state[best_id]["turned"] = true
				_agent_state[best_id]["on_dispatch"] = true
				_agent_state[best_id]["return_day"] = TURNS_TOTAL + 1
				_log("[color=#c8a8ff][b]%s turned.[/b] %s is now on the resistance's side.[/color]" %
					[_agents[best_id]["name"], _agents[best_id]["name"]])
		"lock_husk_for_saga":
			if _agent_state.has("husk"):
				_agent_state["husk"]["locked_for_saga"] = true
				_agent_state["husk"]["on_dispatch"] = true
				_agent_state["husk"]["return_day"] = TURNS_TOTAL + 1
				_log("[color=#c8a8ff][b]Husk locked for the saga.[/b][/color]")
		"lose_contact":
			# Pick a random human contact in the named region.
			var r_id9 := _resolve_region(String(eff.get("region", "current")), ctx)
			var pool2: String = String(eff.get("agent_pool", "human"))
			var candidates: Array = []
			for ag_id in _agents:
				var a: Dictionary = _agents[ag_id]
				if pool2 == "human" and a.get("class", "") != "human": continue
				if String(a.get("home_region", "")) != r_id9: continue
				candidates.append(ag_id)
			if not candidates.is_empty():
				var pick_id: String = String(candidates[rng.randi() % candidates.size()])
				_agent_state[pick_id]["obligation"] = int(_agents[pick_id].get("obligation_cap_before_stops_picking_up", 0))
				_log("[color=#ff9090]%s stops picking up.[/color]" % _agents[pick_id]["name"])
		# ── DM reply effects (phase 2 sprint 2) ──────────────────
		"set_flag":
			var fk: String = String(eff.get("flag", ""))
			if fk != "":
				_flags[fk] = eff.get("value", true)
		"increment_counter":
			var ck: String = String(eff.get("counter", ""))
			var ca: int = int(eff.get("amount", 1))
			if ck != "":
				_counters[ck] = int(_counters.get(ck, 0)) + ca
		"spend_cover":
			var sc_region: String = String(eff.get("region", "graustark"))
			var sc_amt: int = int(eff.get("amount", 1))
			if _region_state.has(sc_region):
				var cur: int = int(_region_state[sc_region].get("cover", 0))
				_region_state[sc_region]["cover"] = max(0, cur - sc_amt)
				_log("[color=#c8a8ff]Cover spent in %s: −%d (%s)[/color]" %
					[_regions.get(sc_region, {}).get("name", sc_region), sc_amt, String(eff.get("reason", ""))])
		"queue_burn":
			var wfn: int = int(eff.get("weeks_from_now", 1))
			_queued_burns.append({
				"trigger_day": _day + wfn * 7,
				"reason": String(eff.get("reason", "")),
			})
		"set_canon_var":
			var cvk: String = String(eff.get("key", ""))
			if cvk != "":
				_canon_vars[cvk] = eff.get("value", null)
		"unlock_artifact":
			var aid: String = String(eff.get("artifact_id", ""))
			if aid != "" and not _unlocked_artifacts.has(aid):
				_unlocked_artifacts.append(aid)
				_log("[color=#e0c862][b]Artifact unlocked:[/b] %s[/color]" % aid)
		"set_regional_marker":
			# Consequence-chain effect: a stage choice can leave a
			# multi-day marker on a region. Markers tick down daily via
			# _tick_active_markers; regional_events with a matching
			# `blocked_by_marker` field are filtered out while the marker
			# is active. Emits an optional entry log_line now and an
			# optional expiry_line when the marker ends.
			var mk_id: String = String(eff.get("marker_id", ""))
			if mk_id == "":
				return
			var mk_region: String = _resolve_region(String(eff.get("region", "current")), ctx)
			var mk_days: int = int(eff.get("days", 7))
			var expires: int = _day + mk_days
			# If a marker with the same id + region already exists, extend
			# rather than duplicate.
			var extended: bool = false
			for existing in _active_regional_markers:
				var e_m: Dictionary = existing
				if String(e_m.get("marker_id", "")) == mk_id and String(e_m.get("region_id", "")) == mk_region:
					e_m["expires_on_day"] = max(int(e_m.get("expires_on_day", 0)), expires)
					extended = true
					break
			if not extended:
				_active_regional_markers.append({
					"marker_id":     mk_id,
					"region_id":     mk_region,
					"expires_on_day": expires,
					"log_line":       String(eff.get("log_line", "")),
					"expiry_line":    String(eff.get("expiry_line", "")),
				})
				var entry_line: String = String(eff.get("log_line", ""))
				if entry_line != "":
					_log(entry_line)
		"unlock_gauntlet_scenario":
			# Community Planned → Gauntlet crossover. This stage choice
			# records a scenario as unlocked in GauntletState.state
			# (persisted across runs). The scrapbook + future scenario-
			# picker UI can read the unlock list to surface a "unlocked
			# via the summer's work" tag. Doesn't gate playability today
			# (all scenarios are launchable from their locale) — the
			# unlock is a canon marker.
			var g_arc: String = String(eff.get("arcana", ""))
			var g_scn: String = String(eff.get("scenario_id", ""))
			if g_arc == "" or g_scn == "":
				return
			var gs: Node = get_node_or_null("/root/GauntletState")
			if gs == null or not gs.has_method("record_cp_scenario_unlock"):
				return
			var newly: bool = gs.call("record_cp_scenario_unlock", g_arc, g_scn)
			if newly:
				var g_name: String = String(eff.get("display_name", "%s/%s" % [g_arc, g_scn]))
				_log("[color=#e0c862][b]Gauntlet unlocked:[/b] %s[/color]" % g_name)
		"demon_tip_off", "ally_goes_silent", "reveal_dial_up_clue":
			# Logged for now; mechanically wired in sprint 3.
			_log("[i]Reply effect (%s): %s[/i]" % [kind, String(eff.get("reason", eff.get("note", "")))])
		# ── Hidden-board strategic effects (sprint 4c) ───────────
		"demon_burn_reduction":
			# The basement's canonical effect: burn -amt on every
			# demon that still carries any. If any of those demons
			# is at hungry+ tier, the rest becomes THE RITE and
			# also drops one corruption point · the room is doing
			# the deeper work now, not just the recovery work.
			var amt: int = int(eff.get("amount", 1))
			var lowered: Array = []
			var rite_lowered: Array = []
			for ag_id in _agent_state:
				if String(_agents.get(ag_id, {}).get("class", "")) != "demon":
					continue
				var cur: int = int(_agent_state[ag_id].get("burn", 0))
				if cur > 0:
					_agent_state[ag_id]["burn"] = max(0, cur - amt)
					lowered.append(String(_agents[ag_id].get("name", ag_id)))
				# The rite: only applies to demons already at hungry+.
				# Reduces corruption by 1 per basement visit. Cannot
				# lower a demon into a lower tier without an entry
				# log · route the decrement through the tier helper
				# so a crossing back into steady announces itself.
				var corr: int = int(_agent_state[ag_id].get("corruption", 0))
				if _demon_corruption_tier(corr) != "steady":
					var new_corr: int = max(0, corr - 1)
					_agent_state[ag_id]["corruption"] = new_corr
					rite_lowered.append(String(_agents[ag_id].get("name", ag_id)))
					if _demon_corruption_tier(new_corr) != _demon_corruption_tier(corr):
						_log("[color=#86d0a8][i]%s dropped a tier · %s → %s.[/i][/color]" %
							[String(_agents[ag_id].get("name", ag_id)),
							 _demon_corruption_tier(corr).replace("_", " "),
							 _demon_corruption_tier(new_corr).replace("_", " ")])
			if lowered.is_empty() and rite_lowered.is_empty():
				_log("[color=#86d0a8][i]the basement: the roster is already rested.[/i][/color]")
			else:
				if not lowered.is_empty():
					_log("[color=#86d0a8][b]the basement:[/b] burn −%d on %s.[/color]" %
						[amt, ", ".join(lowered)])
				if not rite_lowered.is_empty():
					_log("[color=#86d0a8][b]the rite:[/b] corruption −1 on %s.[/color]" %
						", ".join(rite_lowered))
		"the_grove_intel":
			# Reveal one queued substrate-anomaly the engine intended
			# to roll. Soft information; the player gets a sentence
			# of advance notice. The actual mechanical pre-roll
			# would key off _anomalies / weekly_spawn — for now we
			# surface a representative hint based on visible regions.
			var hint: String = "the HOA's roll for next Sunday will land in Small Wood."
			if _visible_regions.has("graustark") and _flags.get("mackenzie_unleashed", false):
				hint = "the HOA is pushing the substrate ratchet a week early."
			_log("[color=#c8a842][b]the grove:[/b] %s[/color]" % hint)
		_:
			push_warning("[CommunityPlanned] unknown effect kind: %s" % kind)


func _resolve_region(spec: String, ctx: Dictionary) -> String:
	if spec == "current":
		return String(ctx.get("region_id", ""))
	return spec


# ── Reveals: the unfolding game ─────────────────────────────────
# Per reveals.json. Each reveal has a day, a kind, and a payload.
# Fired once. Once fired, the reveal's effect is permanent.
func _fire_reveals_for_today() -> void:
	for r in _reveals_def.get("reveals", []):
		var r_id: String = String(r["id"])
		if _reveals_fired.get(r_id, false):
			continue
		if int(r.get("day", 0)) > _day:
			continue
		_reveals_fired[r_id] = true
		_apply_reveal(r)


func _apply_reveal(r: Dictionary) -> void:
	var kind: String = String(r.get("kind", ""))
	var payload: Dictionary = r.get("payload", {})
	match kind:
		"agent_arrives":
			var a_id: String = String(payload.get("agent_id", ""))
			if a_id != "" and not _visible_agents.has(a_id):
				_visible_agents.append(a_id)
		"region_opens":
			var rid: String = String(payload.get("region_id", ""))
			if rid != "" and not _visible_regions.has(rid):
				_visible_regions.append(rid)
				# Build the panel for the newly-opened region.
				if _region_panels_box != null and _region_panels_box.get_node_or_null("Region_" + rid) == null:
					_region_panels_box.add_child(_make_region_panel(rid))
				# Seed the opening problem if one was specified.
				var seed_id: String = String(payload.get("seed_problem", ""))
				if seed_id != "":
					_seed_problem(rid, seed_id)
		"enable_problem_type":
			# Single "type" or "types" array — accept both.
			if payload.has("type"):
				if not _eligible_problem_types.has(payload["type"]):
					_eligible_problem_types.append(payload["type"])
			if payload.has("types"):
				for t in payload["types"]:
					if not _eligible_problem_types.has(t):
						_eligible_problem_types.append(t)
		"show_ui":
			_ui_flags[String(payload.get("flag", ""))] = true
		"narrative_only":
			pass  # just the log line
	if r.has("log"):
		_log(String(r["log"]))


# ── UI build ─────────────────────────────────────────────────────
func _build_ui() -> void:
	# Build a panel only for the currently visible regions. Other
	# region panels are added when their region_opens reveal fires.
	# (After _try_load_save() this gets re-called from _render via
	# _ensure_region_panels.)
	for r_id in _visible_regions:
		if _region_panels_box.get_node_or_null("Region_" + r_id) == null:
			_region_panels_box.add_child(_make_region_panel(r_id))
	_advance_button.pressed.connect(_on_advance_day)
	_new_game_button.pressed.connect(_on_new_game_pressed)
	_back_button.pressed.connect(_on_back_pressed)
	_shelf_button.pressed.connect(_open_interlude_shelf)


func _on_new_game_pressed() -> void:
	var dlg := ConfirmationDialog.new()
	dlg.title = "New Game"
	dlg.dialog_text = "Wipe the current summer and start over from Memorial Day?"
	dlg.confirmed.connect(func() -> void:
		_wipe_save_and_restart()
		dlg.queue_free())
	dlg.canceled.connect(func() -> void: dlg.queue_free())
	dlg.add_to_group("ui")  # F4 sweep catches modals
	add_child(dlg)
	dlg.popup_centered()


func _on_back_pressed() -> void:
	_write_save()
	queue_free()


func _make_region_panel(r_id: String) -> Control:
	var r: Dictionary = _regions[r_id]
	var panel := PanelContainer.new()
	panel.name = "Region_" + r_id
	panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.08, 0.09, 0.12, 0.95)
	sb.border_color = Color(0.42, 0.52, 0.62, 0.6)
	sb.set_border_width_all(1)
	sb.content_margin_left = 8
	sb.content_margin_right = 8
	sb.content_margin_top = 8
	sb.content_margin_bottom = 8
	panel.add_theme_stylebox_override("panel", sb)
	var col := VBoxContainer.new()
	col.name = "Col"
	col.add_theme_constant_override("separation", 4)
	panel.add_child(col)
	var title := Label.new()
	title.name = "Title"
	title.text = r["name"]
	title.add_theme_font_size_override("font_size", 16)
	title.add_theme_color_override("font_color", Color(0.92, 0.86, 0.62, 1))
	col.add_child(title)
	var subtitle := Label.new()
	subtitle.name = "Subtitle"
	subtitle.text = r.get("subtitle", "")
	subtitle.add_theme_font_size_override("font_size", 10)
	subtitle.add_theme_color_override("font_color", Color(0.62, 0.62, 0.62, 1))
	col.add_child(subtitle)
	var stats := Label.new()
	stats.name = "Stats"
	stats.add_theme_font_size_override("font_size", 11)
	col.add_child(stats)
	var nodes_label := Label.new()
	nodes_label.name = "Nodes"
	nodes_label.add_theme_font_size_override("font_size", 10)
	nodes_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	col.add_child(nodes_label)
	var problems_header := Label.new()
	problems_header.text = "PROBLEMS"
	problems_header.add_theme_font_size_override("font_size", 10)
	problems_header.add_theme_color_override("font_color", Color(0.86, 0.34, 0.20, 1))
	col.add_child(problems_header)
	var problems_box := VBoxContainer.new()
	problems_box.name = "ProblemsBox"
	col.add_child(problems_box)
	return panel


# ── Render ───────────────────────────────────────────────────────
func _render() -> void:
	# Day-of-week makes Sunday legible to the player so the weekly
	# spawn beat reads as a beat instead of a surprise.
	var dow: String = _day_of_week(_day)
	if dow != "":
		_day_label.text = "DAY %d / %d  ·  %s" % [_day, TURNS_TOTAL, dow]
	else:
		_day_label.text = "DAY %d / %d" % [_day, TURNS_TOTAL]
	_dispatches_label.text = "Dispatches today: %d / %d" % [_dispatches_this_day, MAX_DISPATCHES_PER_DAY]
	# Shelf button is hidden until the dean_interludes_visible reveal
	# fires at day 60 — the interlude shelf is part of the late-summer
	# legibility, not an ever-present UI element.
	if _shelf_button != null:
		var total_shelf := _interlude_shelf.size() + _dean_interludes_earned.size()
		_shelf_button.visible = bool(_ui_flags.get("dean_interludes_visible", false))
		_shelf_button.text = "Shelf · %d" % total_shelf
	# Ensure panels exist for any region that's become visible since
	# the last build (e.g. after region_opens reveal fired or after
	# loading a save mid-summer).
	for r_id in _visible_regions:
		if _region_panels_box.get_node_or_null("Region_" + r_id) == null:
			_region_panels_box.add_child(_make_region_panel(r_id))
	if bool(_ui_flags.get("tower_visible", false)):
		_render_tower_strip()
	for r_id in _visible_regions:
		_render_region(r_id)
	_render_agent_list()
	_render_todays_dispatches()
	_render_log()


func _render_tower_strip() -> void:
	# Dean's tower is the only legible reading of what he's doing.
	# Surface its current brightness state in the small wood panel's
	# header so the player can read it as a weekly forecast. A
	# dispatch button below the label lets the player send an agent
	# at the tower — at the cost of never seeing them again. (Spec
	# §The tower: "agents dispatched to the tower do not return.")
	var panel: Node = _region_panels_box.get_node_or_null("Region_small_wood")
	if panel == null:
		return
	var col: Node = panel.get_node_or_null("Col")
	if col == null:
		return
	var tower_row: HBoxContainer = col.get_node_or_null("TowerRow") as HBoxContainer
	if tower_row == null:
		tower_row = HBoxContainer.new()
		tower_row.name = "TowerRow"
		tower_row.add_theme_constant_override("separation", 6)
		col.add_child(tower_row)
		col.move_child(tower_row, 3)
		var lbl := Label.new()
		lbl.name = "TowerLine"
		lbl.add_theme_font_size_override("font_size", 11)
		lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		tower_row.add_child(lbl)
		var btn := Button.new()
		btn.name = "TowerBtn"
		btn.text = "send to tower"
		btn.focus_mode = Control.FOCUS_NONE
		btn.add_theme_font_size_override("font_size", 9)
		btn.pressed.connect(_open_tower_dispatch)
		tower_row.add_child(btn)
	var tower_label: Label = tower_row.get_node("TowerLine") as Label
	var color_map: Dictionary = {
		"dim":     Color(0.42, 0.42, 0.50, 1),
		"warming": Color(0.62, 0.52, 0.42, 1),
		"bright":  Color(0.92, 0.78, 0.42, 1),
		"white":   Color(0.96, 0.96, 0.88, 1),
	}
	var color: Color = color_map.get(_tower_brightness, Color(0.62, 0.62, 0.62, 1))
	tower_label.add_theme_color_override("font_color", color)
	tower_label.text = "tower: %s" % _tower_brightness


func _render_region(r_id: String) -> void:
	var panel: Node = _region_panels_box.get_node("Region_" + r_id)
	var st: Dictionary = _region_state[r_id]
	var stats_label: Label = panel.get_node("Col/Stats") as Label
	if bool(_ui_flags.get("show_resource_economy_numbers", false)):
		stats_label.text = "insight %d  ·  cover %d  ·  courier %d  ·  esc %.0f%%" % [
			st["insight"], st["cover"], st["courier_capacity"],
			clamp(st["escalation_progress"] * 100.0, 0.0, 100.0)
		]
	else:
		# Pre-reveal: just hint at the rhythm without naming the
		# resource columns. Once the numbers reveal fires at day 5
		# they read in numbers.
		stats_label.text = "running steady  ·  esc %.0f%%" % clamp(st["escalation_progress"] * 100.0, 0.0, 100.0)
	var nodes_label: Label = panel.get_node("Col/Nodes") as Label
	var held: Array = st["held_nodes"]
	var contested: Array = st["contested_nodes"]
	var targets: Array = st["target_nodes"]
	# Memory nodes: read directly off the region definition. They
	# stay on the map as memory but cannot be dispatched into; spec
	# §Graustark mentions the riverboat as the canonical memory.
	var memory: Array = _regions[r_id].get("memory_nodes", [])
	var parts: PackedStringArray = PackedStringArray()
	parts.append("HELD: " + (", ".join(held) if not held.is_empty() else "—"))
	if not memory.is_empty():
		parts.append("MEMORY: " + ", ".join(memory))
	if not contested.is_empty():
		parts.append("CONTESTED: " + ", ".join(contested))
	if not targets.is_empty():
		parts.append("TARGETS: " + ", ".join(targets))
	nodes_label.text = "\n".join(parts)
	var box: VBoxContainer = panel.get_node("Col/ProblemsBox") as VBoxContainer
	for child in box.get_children():
		child.queue_free()
	var probs: Array = st["active_problems"]
	if probs.is_empty():
		var none := Label.new()
		none.text = "(none active)"
		none.add_theme_color_override("font_color", Color(0.55, 0.55, 0.55, 1))
		none.add_theme_font_size_override("font_size", 10)
		box.add_child(none)
	for pi in range(probs.size()):
		var p: Dictionary = probs[pi]
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 4)
		# Problem label is a flat button that opens the dossier. The
		# title + severity dots + effort read the same as before, but
		# clicking now surfaces the template flavor + threshold info
		# + ideal handlers.
		var lbl := Button.new()
		var sev_dots := ""
		var sev_int: int = int(round(p["severity"]))
		for i in range(min(sev_int, 9)):
			sev_dots += "●"
		lbl.text = "%s  %s  (effort %.1f)" % [p["title"], sev_dots, p["effort_remaining"]]
		lbl.alignment = HORIZONTAL_ALIGNMENT_LEFT
		lbl.flat = true
		lbl.focus_mode = Control.FOCUS_NONE
		lbl.add_theme_font_size_override("font_size", 10)
		lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var r_id_d: String = String(r_id)
		var pi_d: int = int(pi)
		lbl.pressed.connect(func() -> void: _open_problem_dossier(r_id_d, pi_d))
		row.add_child(lbl)
		if String(p.get("in_progress_by", "")) != "":
			var ag := Label.new()
			ag.text = "↳ %s" % p["in_progress_by"]
			ag.add_theme_color_override("font_color", Color(0.62, 0.86, 0.62, 1))
			ag.add_theme_font_size_override("font_size", 10)
			row.add_child(ag)
		else:
			var btn := Button.new()
			btn.text = "dispatch"
			btn.focus_mode = Control.FOCUS_NONE
			btn.add_theme_font_size_override("font_size", 10)
			var r_id_capture: String = String(r_id)
			var pi_capture: int = int(pi)
			btn.pressed.connect(func() -> void: _open_dispatch_picker(r_id_capture, pi_capture))
			row.add_child(btn)
		box.add_child(row)


func _render_agent_list() -> void:
	for child in _agent_list_box.get_children():
		child.queue_free()
	var header := Label.new()
	header.text = "AGENT ROSTER"
	header.add_theme_color_override("font_color", Color(0.92, 0.86, 0.62, 1))
	header.add_theme_font_size_override("font_size", 12)
	_agent_list_box.add_child(header)
	# Only show agents the reveal schedule has surfaced.
	var ids: Array = _visible_agents.duplicate()
	ids.sort_custom(func(a, b):
		var ac: String = String(_agents[a].get("class", ""))
		var bc: String = String(_agents[b].get("class", ""))
		if ac != bc: return ac < bc
		return String(_agents[a]["name"]) < String(_agents[b]["name"]))
	var show_demon_econ: bool = bool(_ui_flags.get("show_demon_economy_numbers", false))
	var show_corr: bool = bool(_ui_flags.get("show_corruption_values", false))
	var show_cmplx: bool = bool(_ui_flags.get("show_complexity_values", false))
	var show_oblig: bool = bool(_ui_flags.get("show_obligation_values", false))
	for a_id in ids:
		if not _agents.has(a_id): continue
		var a: Dictionary = _agents[a_id]
		var st: Dictionary = _agent_state[a_id]
		var status := ""
		if bool(st["on_dispatch"]):
			status = "  · ON DISPATCH (returns day %d)" % int(st["return_day"])
		elif _agent_is_resting(a_id):
			status = "  · AT REST (%d/%d)" % [
				int(st.get("home_days_used", 0)),
				int(st.get("home_days_needed", 0))]
		var econ := ""
		if a["class"] == "demon":
			# Demon econ stays hidden until the player has been at it
			# for a week. Once shown, each value is gated by its own
			# reveal flag so corruption/complexity arrive when the
			# narrative is ready for them.
			if show_demon_econ:
				var parts: PackedStringArray = PackedStringArray()
				parts.append("burn=%d" % int(st["burn"]))
				if show_corr:
					parts.append("corr=%d" % int(st["corruption"]))
				if show_cmplx:
					parts.append("cmplx=%d" % int(st["complexity"]))
				econ = "  " + "  ".join(parts)
			elif bool(st["on_dispatch"]):
				econ = ""
			else:
				econ = "  (rested)"
		else:
			if show_oblig:
				econ = "  oblig=%d/%d" % [int(st["obligation"]), int(a.get("obligation_cap_before_stops_picking_up", 0))]
			elif bool(st["on_dispatch"]):
				econ = ""
			else:
				econ = "  (home)"
		# Each agent is a button that opens the dossier modal. Flat
		# button styled to read like a label until hover. The prefix
		# glyph is a fast at-a-glance state read: ○ available, ▶ on
		# dispatch, ● at rest. For demons at corruption>=3 the tier
		# tag rides in the econ column · hungry / restless / close.
		var btn := Button.new()
		var glyph := "○"
		if bool(st["on_dispatch"]):
			glyph = "▶"
		elif _agent_is_resting(a_id):
			glyph = "●"
		var tier_tag := ""
		if a["class"] == "demon" and show_corr:
			var d_tier: String = _demon_corruption_tier(int(st.get("corruption", 0)))
			if d_tier != "steady":
				tier_tag = "  · " + d_tier.replace("_", " ")
		btn.text = "%s [%s]  %s%s%s%s" % [
			glyph,
			"D" if a["class"] == "demon" else "H",
			a["name"], econ, tier_tag, status]
		btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		btn.flat = true
		btn.focus_mode = Control.FOCUS_NONE
		btn.add_theme_font_size_override("font_size", 10)
		var ag_capture: String = String(a_id)
		btn.pressed.connect(func() -> void: _open_agent_dossier(ag_capture))
		_agent_list_box.add_child(btn)


# ── Agent dossier modal ─────────────────────────────────────────
# Clicking an agent in the roster opens this panel. The dossier
# is the rich-context surface for an agent: specialty types,
# competence, evolution traits (locked + earned), and the per-
# agent economy state. Demon dossiers show burn history; human
# dossiers show obligation against cap and the named life-cost
# thresholds with proximity to each. In phase 2 demons will
# accrue BBS opinions surfaced here.
func _open_agent_dossier(agent_id: String) -> void:
	if not _agents.has(agent_id):
		return
	var a: Dictionary = _agents[agent_id]
	var st: Dictionary = _agent_state[agent_id]
	var dlg := AcceptDialog.new()
	dlg.title = "Dossier — %s" % String(a["name"])
	dlg.min_size = Vector2(560, 480)
	var scroll := ScrollContainer.new()
	scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.custom_minimum_size = Vector2(540, 440)
	dlg.add_child(scroll)
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 6)
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(col)

	# Header line
	var hdr := Label.new()
	hdr.text = "%s · %s" % [String(a["name"]), "DEMON" if a["class"] == "demon" else "HUMAN"]
	hdr.add_theme_font_size_override("font_size", 14)
	hdr.add_theme_color_override("font_color", Color(0.92, 0.86, 0.62, 1))
	col.add_child(hdr)

	# Handle + home region
	var sub := Label.new()
	sub.text = "@%s  ·  home: %s" % [
		String(a.get("handle_on_bbs", "—")),
		_regions.get(String(a.get("home_region", "")), {}).get("name", String(a.get("home_region", "—")))
	]
	sub.add_theme_font_size_override("font_size", 10)
	sub.add_theme_color_override("font_color", Color(0.62, 0.62, 0.62, 1))
	col.add_child(sub)

	col.add_child(_dossier_rule())

	# Flavor / origin
	if String(a.get("flavor", "")) != "":
		var flavor := Label.new()
		flavor.text = String(a["flavor"])
		flavor.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		flavor.add_theme_font_size_override("font_size", 11)
		flavor.add_theme_color_override("font_color", Color(0.86, 0.86, 0.86, 1))
		col.add_child(flavor)
		col.add_child(_dossier_rule())

	# Specialty + competence
	var sp_header := Label.new()
	sp_header.text = "SPECIALTY"
	sp_header.add_theme_font_size_override("font_size", 10)
	sp_header.add_theme_color_override("font_color", Color(0.86, 0.34, 0.20, 1))
	col.add_child(sp_header)
	var sp := Label.new()
	var specs: Array = a.get("specialty_problem_types", [])
	sp.text = (", ".join(specs) if not specs.is_empty() else "—")
	sp.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	sp.add_theme_font_size_override("font_size", 10)
	col.add_child(sp)
	var comp := Label.new()
	comp.text = "competence  %.2fx  ·  speed  %.2fx" % [
		float(a.get("competence_modifier", 1.0)),
		float(a.get("dispatch_speed_modifier", 1.0))]
	comp.add_theme_font_size_override("font_size", 10)
	comp.add_theme_color_override("font_color", Color(0.62, 0.62, 0.62, 1))
	col.add_child(comp)

	col.add_child(_dossier_rule())

	# Per-class economy block
	if a["class"] == "demon":
		_render_demon_dossier(col, a, st)
	else:
		_render_human_dossier(col, a, st)

	col.add_child(_dossier_rule())

	# Evolution paths (always visible — what this agent could
	# become; reads as character development). Earned traits get a
	# checkmark; locked traits are dimmed.
	var ev_header := Label.new()
	ev_header.text = "EVOLUTION"
	ev_header.add_theme_font_size_override("font_size", 10)
	ev_header.add_theme_color_override("font_color", Color(0.42, 0.86, 0.62, 1))
	col.add_child(ev_header)
	var paths: Array = a.get("evolution_paths", [])
	var earned: Array = st.get("evolution_traits_earned", [])
	for trait_id in paths:
		var trait_str: String = String(trait_id)
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 6)
		var mark := Label.new()
		var is_earned := earned.has(trait_str)
		mark.text = "✓" if is_earned else "○"
		mark.add_theme_color_override("font_color",
			Color(0.42, 0.86, 0.62, 1) if is_earned else Color(0.42, 0.42, 0.42, 1))
		mark.add_theme_font_size_override("font_size", 12)
		row.add_child(mark)
		var name_lbl := Label.new()
		name_lbl.text = trait_str
		name_lbl.add_theme_font_size_override("font_size", 10)
		name_lbl.add_theme_color_override("font_color",
			Color(0.86, 0.86, 0.86, 1) if is_earned else Color(0.55, 0.55, 0.55, 1))
		name_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(name_lbl)
		col.add_child(row)
		# Trait description from the catalog (lives in agents.json).
		var catalog: Dictionary = {}
		# Look up the agents.json file's catalog dict — we cached
		# only the agent records in _agents, so reload it here lazily.
		# (Fine; this is a one-shot dossier open.)
		var aj: Dictionary = _load_json(DATA_ROOT + "agents.json")
		catalog = aj.get("evolution_traits_catalog", {})
		if catalog.has(trait_str):
			var desc := Label.new()
			desc.text = String(catalog[trait_str])
			desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			desc.add_theme_font_size_override("font_size", 9)
			desc.add_theme_color_override("font_color", Color(0.55, 0.55, 0.55, 1))
			col.add_child(desc)

	# Status / dispatch state
	col.add_child(_dossier_rule())
	var status_label := Label.new()
	var status_text: String
	if bool(st.get("on_dispatch", false)):
		status_text = "ON DISPATCH · returns day %d" % int(st.get("return_day", 0))
	elif bool(st.get("locked_for_saga", false)):
		status_text = "LOCKED FOR THE SAGA"
	elif bool(st.get("turned", false)):
		status_text = "TURNED · on the resistance's side"
	elif _agent_is_resting(a_id):
		status_text = "AT REST · %d/%d days" % [
			int(st.get("home_days_used", 0)),
			int(st.get("home_days_needed", 0))]
	else:
		status_text = "available"
	status_label.text = "STATUS  ·  %s" % status_text
	status_label.add_theme_font_size_override("font_size", 10)
	status_label.add_theme_color_override("font_color", Color(0.86, 0.86, 0.62, 1))
	col.add_child(status_label)

	dlg.add_to_group("ui")  # F4 sweep catches modals
	add_child(dlg)
	dlg.popup_centered()


func _render_demon_dossier(col: VBoxContainer, a: Dictionary, st: Dictionary) -> void:
	var econ_hdr := Label.new()
	econ_hdr.text = "DEMON ECONOMY"
	econ_hdr.add_theme_font_size_override("font_size", 10)
	econ_hdr.add_theme_color_override("font_color", Color(0.86, 0.34, 0.20, 1))
	col.add_child(econ_hdr)
	# Burn line
	var burn_lbl := Label.new()
	burn_lbl.text = "burn  %d  ·  +%d per dispatch  ·  dark at 5, gone at 10" % [
		int(st.get("burn", 0)), int(a.get("burn_per_dispatch", 1))]
	burn_lbl.add_theme_font_size_override("font_size", 10)
	col.add_child(burn_lbl)
	# Corruption (gated) · tier tag makes the number legible, and
	# the spillover-chance line tells the player what they're
	# rolling on every dispatch while this demon carries corruption.
	if bool(_ui_flags.get("show_corruption_values", false)):
		var corr_val: int = int(st.get("corruption", 0))
		var d_tier: String = _demon_corruption_tier(corr_val)
		var d_glyph: String = _demon_tier_glyph(d_tier)
		var d_chance: float = _demon_tier_spillover_chance(d_tier)
		var corr_lbl := Label.new()
		corr_lbl.text = "%s corruption  %d  ·  %s  ·  resistance: %s" % [
			d_glyph, corr_val, d_tier.replace("_", " "),
			String(a.get("corruption_resistance", "—"))]
		corr_lbl.add_theme_font_size_override("font_size", 10)
		corr_lbl.add_theme_color_override("font_color", _demon_tier_color(d_tier))
		col.add_child(corr_lbl)
		if d_chance > 0.0:
			var spill_lbl := Label.new()
			spill_lbl.text = "  signature-spillover chance on dispatch: %d%%" % int(round(d_chance * 100.0))
			spill_lbl.add_theme_font_size_override("font_size", 9)
			spill_lbl.add_theme_color_override("font_color", Color(0.86, 0.62, 0.42, 1))
			col.add_child(spill_lbl)
	# Complexity (gated)
	if bool(_ui_flags.get("show_complexity_values", false)):
		var cmplx_lbl := Label.new()
		cmplx_lbl.text = "complexity  %d  ·  the longer they work, the more they are themselves" % int(st.get("complexity", 0))
		cmplx_lbl.add_theme_font_size_override("font_size", 10)
		cmplx_lbl.add_theme_color_override("font_color", Color(0.86, 0.62, 0.96, 1))
		col.add_child(cmplx_lbl)
	# Signature failure
	if String(a.get("signature_failure", "")) != "":
		var fail := Label.new()
		fail.text = "signature failure: " + String(a["signature_failure"])
		fail.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		fail.add_theme_font_size_override("font_size", 9)
		fail.add_theme_color_override("font_color", Color(0.62, 0.42, 0.42, 1))
		col.add_child(fail)
	# Region restrictions
	var restrictions: Array = a.get("region_restrictions", [])
	if not restrictions.is_empty():
		var rest_lbl := Label.new()
		var names: PackedStringArray = PackedStringArray()
		for rid in restrictions:
			names.append(String(_regions.get(rid, {}).get("name", rid)))
		rest_lbl.text = "region-locked to: " + ", ".join(names)
		rest_lbl.add_theme_font_size_override("font_size", 9)
		rest_lbl.add_theme_color_override("font_color", Color(0.62, 0.62, 0.62, 1))
		col.add_child(rest_lbl)


func _render_human_dossier(col: VBoxContainer, a: Dictionary, st: Dictionary) -> void:
	var econ_hdr := Label.new()
	econ_hdr.text = "HUMAN COSTS"
	econ_hdr.add_theme_font_size_override("font_size", 10)
	econ_hdr.add_theme_color_override("font_color", Color(0.86, 0.34, 0.20, 1))
	col.add_child(econ_hdr)
	if bool(_ui_flags.get("show_obligation_values", false)):
		var obl_lbl := Label.new()
		var cap: int = int(a.get("obligation_cap_before_stops_picking_up", 0))
		var cur: int = int(st.get("obligation", 0))
		obl_lbl.text = "obligation  %d / %d  ·  +%d per dispatch" % [
			cur, cap, int(a.get("obligation_per_dispatch", 1))]
		obl_lbl.add_theme_font_size_override("font_size", 10)
		var col_color := Color(0.86, 0.86, 0.62, 1)
		if cap > 0 and float(cur) / float(cap) >= 0.6:
			col_color = Color(0.96, 0.62, 0.42, 1)
		if cap > 0 and float(cur) / float(cap) >= 0.85:
			col_color = Color(0.96, 0.42, 0.32, 1)
		obl_lbl.add_theme_color_override("font_color", col_color)
		col.add_child(obl_lbl)
	# Time-at-home cost
	var th_lbl := Label.new()
	th_lbl.text = "time-at-home cost  %.1f days per dispatch" % float(a.get("time_at_home_cost_days", 1.0))
	th_lbl.add_theme_font_size_override("font_size", 9)
	th_lbl.add_theme_color_override("font_color", Color(0.62, 0.62, 0.62, 1))
	col.add_child(th_lbl)
	# Life cost thresholds
	var life: Dictionary = a.get("life_cost_thresholds", {})
	if not life.is_empty():
		var life_hdr := Label.new()
		life_hdr.text = "LIFE COSTS"
		life_hdr.add_theme_font_size_override("font_size", 9)
		life_hdr.add_theme_color_override("font_color", Color(0.86, 0.62, 0.42, 1))
		col.add_child(life_hdr)
		var keys: Array = life.keys()
		keys.sort_custom(func(x, y): return int(String(x)) < int(String(y)))
		var cur_obl: int = int(st.get("obligation", 0))
		for k in keys:
			var n: int = int(String(k))
			var crossed: bool = cur_obl >= n
			var line := Label.new()
			line.text = "%s @%d  ·  %s" % [
				("✓" if crossed else "○"),
				n,
				String(life[k])]
			line.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			line.add_theme_font_size_override("font_size", 9)
			line.add_theme_color_override("font_color",
				Color(0.96, 0.62, 0.42, 1) if crossed else Color(0.62, 0.62, 0.62, 1))
			col.add_child(line)


func _open_problem_dossier(region_id: String, problem_index: int) -> void:
	if not _region_state.has(region_id):
		return
	var probs: Array = _region_state[region_id].get("active_problems", [])
	if problem_index < 0 or problem_index >= probs.size():
		return
	var p: Dictionary = probs[problem_index]
	var template_id: String = String(p.get("template_id", ""))
	var template: Dictionary = _problem_templates.get(template_id, {})
	var region_name: String = String(_regions.get(region_id, {}).get("name", region_id))
	var dlg := AcceptDialog.new()
	dlg.title = "Problem — %s" % String(p["title"])
	dlg.min_size = Vector2(560, 440)
	var scroll := ScrollContainer.new()
	scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.custom_minimum_size = Vector2(540, 400)
	dlg.add_child(scroll)
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 6)
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(col)
	var hdr := Label.new()
	hdr.text = String(p["title"])
	hdr.add_theme_font_size_override("font_size", 14)
	hdr.add_theme_color_override("font_color", Color(0.92, 0.86, 0.62, 1))
	col.add_child(hdr)
	var sub := Label.new()
	sub.text = "in %s  ·  age %d days" % [region_name, _day - int(p.get("day_spawned", _day))]
	sub.add_theme_font_size_override("font_size", 10)
	sub.add_theme_color_override("font_color", Color(0.62, 0.62, 0.62, 1))
	col.add_child(sub)
	col.add_child(_dossier_rule())
	if String(template.get("flavor", "")) != "":
		var flavor := Label.new()
		flavor.text = String(template["flavor"])
		flavor.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		flavor.add_theme_font_size_override("font_size", 11)
		flavor.add_theme_color_override("font_color", Color(0.86, 0.86, 0.86, 1))
		col.add_child(flavor)
		col.add_child(_dossier_rule())
	var sev: float = float(p.get("severity", 0))
	var eff: float = float(p.get("effort_remaining", 0))
	var tick: float = float(template.get("tick_per_day", 0.0))
	var econ_header := Label.new()
	econ_header.text = "STATE"
	econ_header.add_theme_font_size_override("font_size", 10)
	econ_header.add_theme_color_override("font_color", Color(0.86, 0.34, 0.20, 1))
	col.add_child(econ_header)
	var econ := Label.new()
	econ.text = "severity %.1f  ·  effort %.1f  ·  tick +%.2f/day" % [sev, eff, tick]
	econ.add_theme_font_size_override("font_size", 10)
	col.add_child(econ)
	if String(p.get("in_progress_by", "")) != "":
		var ip := Label.new()
		ip.text = "in progress by %s" % String(p["in_progress_by"])
		ip.add_theme_color_override("font_color", Color(0.62, 0.86, 0.62, 1))
		ip.add_theme_font_size_override("font_size", 10)
		col.add_child(ip)
	col.add_child(_dossier_rule())
	var thresh: Array = template.get("if_unresolved_at_severity_7", [])
	if not thresh.is_empty():
		var th_header := Label.new()
		th_header.text = "IF IT CROSSES SEVERITY 7"
		th_header.add_theme_font_size_override("font_size", 10)
		th_header.add_theme_color_override("font_color", Color(0.96, 0.62, 0.42, 1))
		col.add_child(th_header)
		for ef in thresh:
			var ed: Dictionary = ef as Dictionary
			var line := Label.new()
			var log_text: String = String(ed.get("text", ""))
			if log_text != "":
				line.text = "· %s" % log_text
			else:
				line.text = "· %s" % String(ed.get("kind", "")).replace("_", " ")
			line.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			line.add_theme_font_size_override("font_size", 10)
			line.add_theme_color_override("font_color", Color(0.86, 0.74, 0.62, 1))
			col.add_child(line)
		col.add_child(_dossier_rule())
	# Generic shape hint — names the *kind* of person this problem
	# wants, not specific agents. The player decides who. Removes
	# the clicker-feel of "pick the recommended name."
	var shape_hint: String = String(template.get("dispatch_shape_hint", ""))
	if shape_hint != "":
		var sh_header := Label.new()
		sh_header.text = "WHAT IT WANTS"
		sh_header.add_theme_font_size_override("font_size", 10)
		sh_header.add_theme_color_override("font_color", Color(0.42, 0.86, 0.62, 1))
		col.add_child(sh_header)
		var sh := Label.new()
		sh.text = shape_hint
		sh.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		sh.add_theme_font_size_override("font_size", 10)
		sh.add_theme_color_override("font_color", Color(0.86, 0.86, 0.86, 1))
		col.add_child(sh)
	dlg.add_to_group("ui")  # F4 sweep catches modals
	add_child(dlg)
	dlg.popup_centered()


func _dossier_rule() -> Control:
	var hr := ColorRect.new()
	hr.color = Color(0.32, 0.32, 0.32, 0.6)
	hr.custom_minimum_size = Vector2(0, 1)
	return hr


# Today's-dispatches panel: each dispatch the player committed
# this turn (before ADVANCE DAY) shows up here with a revoke
# button. Revoking restores agent state, frees the problem, and
# decrements _dispatches_this_day so the player gets the slot back.
# Lock: once committed_at_day < _day (after ADVANCE DAY), the
# dispatch no longer appears here.
func _render_todays_dispatches() -> void:
	for child in _today_box.get_children():
		child.queue_free()
	var todays: Array = []
	for d in _active_dispatches:
		if int(d.get("committed_at_day", -1)) == _day:
			todays.append(d)
	_today_header.visible = not todays.is_empty()
	for d in todays:
		var a_id: String = String(d.get("agent_id", ""))
		if not _agents.has(a_id):
			continue
		var a: Dictionary = _agents[a_id]
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 4)
		var lbl := Label.new()
		lbl.text = "%s → %s" % [String(a["name"]),
			String(_regions.get(String(d.get("region_id", "")), {}).get("name", "?"))]
		lbl.add_theme_font_size_override("font_size", 9)
		lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(lbl)
		var btn := Button.new()
		btn.text = "↩"
		btn.tooltip_text = "Revoke this dispatch"
		btn.focus_mode = Control.FOCUS_NONE
		btn.custom_minimum_size = Vector2(28, 22)
		btn.add_theme_font_size_override("font_size", 10)
		var d_capture: Dictionary = d
		btn.pressed.connect(func() -> void: _revoke_dispatch(d_capture))
		row.add_child(btn)
		_today_box.add_child(row)


func _revoke_dispatch(d: Dictionary) -> void:
	if int(d.get("committed_at_day", -1)) != _day:
		return
	var a_id: String = String(d.get("agent_id", ""))
	var region_id: String = String(d.get("region_id", ""))
	var pi: int = int(d.get("problem_index", -1))
	if not _agents.has(a_id):
		return
	var a: Dictionary = _agents[a_id]
	var st: Dictionary = _agent_state[a_id]
	# Restore the agent state from the snapshot we took at dispatch.
	var snap: Dictionary = d.get("undo_snapshot", {})
	if a["class"] == "demon":
		st["burn"] = int(snap.get("burn", st.get("burn", 0)))
	else:
		st["obligation"] = int(snap.get("obligation", st.get("obligation", 0)))
	st["on_dispatch"] = false
	st["return_day"] = 0
	st["days_away_since_dispatch"] = 0
	st["home_node_strained_this_dispatch"] = false
	# Free the target problem (if it still exists at that index).
	if _region_state.has(region_id):
		var probs: Array = _region_state[region_id].get("active_problems", [])
		if pi >= 0 and pi < probs.size():
			var p_ref: Dictionary = probs[pi]
			if String(p_ref.get("dispatch_agent_id", "")) == a_id:
				p_ref["in_progress_by"] = ""
				p_ref["dispatch_agent_id"] = ""
				p_ref["dispatch_resolution_day"] = 0
	# Decrement counters.
	_active_dispatches.erase(d)
	_dispatches_this_day = max(0, _dispatches_this_day - 1)
	_agent_dispatch_counts[a_id] = max(0, int(_agent_dispatch_counts.get(a_id, 1)) - 1)
	_log("[i]Revoked.[/i] %s came back from the road. The problem is unhandled again." % String(a["name"]))
	_render()


func _render_log() -> void:
	_log_label.clear()
	for line in _log_lines:
		_log_label.append_text(line + "\n")


# ── Dispatch flow ────────────────────────────────────────────────
# Tower dispatch: a special target inside the Small Wood column.
# Spec §The tower: "agents dispatched to the tower do not return."
# The player can do it — the brightness state is the only legible
# reading they have of what Dean is doing, and a fingerprint, a
# sacrifice, or a Dean-shelf interlude might be worth one agent.
# But it always costs the agent for the rest of the summer.
func _open_tower_dispatch() -> void:
	if _dispatches_this_day >= MAX_DISPATCHES_PER_DAY:
		_log("[color=#ff9090]Already dispatched %d agents today.[/color]" % MAX_DISPATCHES_PER_DAY)
		return
	var dlg := ConfirmationDialog.new()
	dlg.title = "Send to the tower"
	dlg.dialog_text = ("The tower in Small Wood. Brightness: %s.\n\n"
		+ "Agents dispatched to the tower do not return.\n"
		+ "Choose an agent. They will be gone for the rest of the summer.")  % _tower_brightness
	var picker := VBoxContainer.new()
	picker.add_theme_constant_override("separation", 4)
	dlg.add_child(picker)
	var has_any := false
	for a_id in _visible_agents:
		if not _agents.has(a_id): continue
		var a: Dictionary = _agents[a_id]
		var st: Dictionary = _agent_state[a_id]
		if bool(st["on_dispatch"]): continue
		if _agent_is_resting(a_id): continue   # respect the home-return breather
		var btn := Button.new()
		btn.text = "send %s" % String(a["name"])
		btn.focus_mode = Control.FOCUS_NONE
		var ag_capture: String = String(a_id)
		btn.pressed.connect(func() -> void:
			_dispatch_to_tower(ag_capture)
			dlg.hide()
			dlg.queue_free())
		picker.add_child(btn)
		has_any = true
	if not has_any:
		var none := Label.new()
		none.text = "No agents available to send."
		picker.add_child(none)
	dlg.add_to_group("ui")  # F4 sweep catches modals
	add_child(dlg)
	dlg.popup_centered()


func _dispatch_to_tower(agent_id: String) -> void:
	if not _agents.has(agent_id): return
	var a: Dictionary = _agents[agent_id]
	var st: Dictionary = _agent_state[agent_id]
	st["on_dispatch"] = true
	st["return_day"] = TURNS_TOTAL + 1
	st["sent_to_tower"] = true
	if a["class"] == "demon":
		st["burn"] = int(st["burn"]) + int(a.get("burn_per_dispatch", 1))
	else:
		var prev_obl: int = int(st["obligation"])
		var new_obl: int = prev_obl + int(a.get("obligation_per_dispatch", 1))
		st["obligation"] = new_obl
		var life: Dictionary = a.get("life_cost_thresholds", {})
		for k in life:
			var n: int = int(String(k))
			if prev_obl < n and new_obl >= n:
				_log("[color=#c8a8ff][b]%s[/b] · obligation %d → %s[/color]" %
					[String(a["name"]), n, String(life[k])])
	_dispatches_this_day += 1
	_log("[color=#c8a8ff]%s went to the tower. They do not return.[/color]" % String(a["name"]))
	_render()


# ── Evolution earning ───────────────────────────────────────────
# Per spec §Demon evolution + the trait catalog at the bottom of
# agents.json. Each trait has an earn condition; we simplify to
# countable predicates against the per-agent state counters that
# the engine ticks on each resolution. Earned traits surface in
# the dossier as ✓ instead of ○.
func _check_evolution_traits(agent_id: String) -> void:
	if not _agents.has(agent_id): return
	var a: Dictionary = _agents[agent_id]
	var st: Dictionary = _agent_state[agent_id]
	var earned: Array = st.get("evolution_traits_earned", [])
	var paths: Array = a.get("evolution_paths", [])
	for trait_v in paths:
		var t: String = String(trait_v)
		if earned.has(t):
			continue
		if _is_trait_earned(t, st, a):
			earned.append(t)
			_log("[color=#62ff9c][b]%s[/b] earned: %s[/color]" %
				[String(a["name"]), t.replace("_", " ")])
	st["evolution_traits_earned"] = earned


func _is_trait_earned(trait_id: String, st: Dictionary, a: Dictionary) -> bool:
	# Catalog simplifications:
	#   cold_terrain_resistance: 3 small_wood returns without turning
	#   press_invisibility: total successful >= 5
	#   policy_intuition: successful in harmony_creek >= 8
	#   embedded_permanence: complexity >= 5
	#   controlled_burn: total successful >= 4
	#   wake_management: complexity >= 6
	#   bayou_native: successful in graustark >= 3
	#   dead_drop_specialist: complexity >= 3
	#   coordinated_flock: successful in harmony_creek >= 4
	#   controlled_husk: complexity >= 4 + small_wood returns >= 1
	#   community_organizer: successful >= 3
	#   press_voice: successful >= 5
	#   restaurant_anchor: successful >= 3
	#   small_wood_native: successful >= 2
	var by_region: Dictionary = st.get("successful_dispatches_by_region", {})
	var sw_returns: int = int(st.get("small_wood_returns_without_turning", 0))
	var complexity: int = int(st.get("complexity", 0))
	var total_success: int = 0
	for k in by_region:
		total_success += int(by_region[k])
	match trait_id:
		"cold_terrain_resistance":  return sw_returns >= 3
		"press_invisibility":       return total_success >= 5
		"policy_intuition":         return int(by_region.get("harmony_creek", 0)) >= 8
		"embedded_permanence":      return complexity >= 5
		"controlled_burn":          return total_success >= 4
		"wake_management":          return complexity >= 6
		"bayou_native":             return int(by_region.get("graustark", 0)) >= 3
		"dead_drop_specialist":     return complexity >= 3
		"coordinated_flock":        return int(by_region.get("harmony_creek", 0)) >= 4
		"controlled_husk":          return complexity >= 4 and sw_returns >= 1
		"community_organizer":      return total_success >= 3
		"press_voice":              return total_success >= 5
		"restaurant_anchor":        return total_success >= 3
		"small_wood_native":        return total_success >= 2
	return false


func _open_dispatch_picker(region_id: String, problem_index: int) -> void:
	if _dispatches_this_day >= MAX_DISPATCHES_PER_DAY:
		_log("[color=#ff9090]Already dispatched %d agents today.[/color]" % MAX_DISPATCHES_PER_DAY)
		_render_log()
		return
	var p: Dictionary = (_region_state[region_id]["active_problems"] as Array)[problem_index]
	var dlg := AcceptDialog.new()
	dlg.title = "Dispatch — %s" % p["title"]
	dlg.min_size = Vector2(560, 420)
	var scroll := ScrollContainer.new()
	scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.custom_minimum_size = Vector2(540, 380)
	dlg.add_child(scroll)
	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 6)
	vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(vbox)
	var hint := Label.new()
	hint.text = "%s (%s) · severity %.1f · effort %.1f" % [
		p["title"], _regions[region_id]["name"],
		float(p["severity"]), float(p["effort_remaining"])]
	hint.add_theme_color_override("font_color", Color(0.92, 0.86, 0.62, 1))
	hint.add_theme_font_size_override("font_size", 11)
	vbox.add_child(hint)
	# Ideal handlers listed by the template — small caption that
	# hints which agents the writer expected to land this problem.
	var ideal: Array = _problem_templates.get(String(p["template_id"]), {}).get("ideal_handlers", [])
	if not ideal.is_empty():
		var hint2 := Label.new()
		hint2.text = "ideal handlers: " + ", ".join(ideal)
		hint2.add_theme_font_size_override("font_size", 9)
		hint2.add_theme_color_override("font_color", Color(0.62, 0.62, 0.62, 1))
		vbox.add_child(hint2)
	var any_eligible := false
	for a_id in _visible_agents:
		if not _agents.has(a_id): continue
		var a: Dictionary = _agents[a_id]
		var st: Dictionary = _agent_state[a_id]
		if bool(st["on_dispatch"]):
			continue
		if a["class"] == "human" and int(st["obligation"]) >= int(a.get("obligation_cap_before_stops_picking_up", 999)):
			continue
		var restrictions: Array = a.get("region_restrictions", [])
		if not restrictions.is_empty() and not restrictions.has(region_id):
			continue
		vbox.add_child(_make_dispatch_preview_row(a_id, region_id, problem_index, p, dlg))
		any_eligible = true
	if not any_eligible:
		var none := Label.new()
		none.text = "No agents available."
		none.add_theme_color_override("font_color", Color(0.62, 0.62, 0.62, 1))
		vbox.add_child(none)
	dlg.add_to_group("ui")  # F4 sweep catches modals
	add_child(dlg)
	dlg.popup_centered()


# Single agent preview row in the dispatch picker. Shows specialty,
# competence + speed, predicted ETA day, and predicted dispatch
# cost (burn for demons, obligation increment + life-cost crossings
# for humans, corruption risk for demons sent to Small Wood).
func _make_dispatch_preview_row(agent_id: String, region_id: String,
		problem_index: int, p: Dictionary, dlg: AcceptDialog) -> Control:
	var a: Dictionary = _agents[agent_id]
	var st: Dictionary = _agent_state[agent_id]
	var r: Dictionary = _regions[region_id]
	var specialty: bool = bool((a.get("specialty_problem_types", []) as Array).has(p["template_id"]))
	# Predict days exactly the way _dispatch_agent calculates.
	var base_days: float = float(p["effort_remaining"]) / max(0.1, float(a.get("competence_modifier", 1.0)))
	var speed_mod: float = float(r.get(
		"demon_travel_speed_modifier" if a["class"] == "demon" else "human_travel_speed_modifier",
		1.0))
	var days: int = int(ceil(base_days / max(0.1, speed_mod)))
	if String(a.get("home_region", "")) != region_id:
		days = int(ceil(float(days) * 1.5))
	if region_id == "small_wood" and String(a.get("home_region", "")) != "small_wood":
		days = int(ceil(float(days) * 1.5))
	# Build a row.
	var panel := PanelContainer.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.06, 0.07, 0.10, 0.6)
	sb.border_color = Color(0.32, 0.42, 0.52, 0.65)
	sb.set_border_width_all(1)
	sb.content_margin_left = 6
	sb.content_margin_right = 6
	sb.content_margin_top = 4
	sb.content_margin_bottom = 4
	panel.add_theme_stylebox_override("panel", sb)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 8)
	panel.add_child(row)
	# Left: name + class tag + specialty star
	var lcol := VBoxContainer.new()
	lcol.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(lcol)
	var name_lbl := Label.new()
	name_lbl.text = "[%s]  %s%s" % [
		"D" if a["class"] == "demon" else "H",
		String(a["name"]),
		"  ★ specialty" if specialty else ""]
	name_lbl.add_theme_font_size_override("font_size", 11)
	if specialty:
		name_lbl.add_theme_color_override("font_color", Color(0.96, 0.86, 0.42, 1))
	lcol.add_child(name_lbl)
	# Detail line
	var detail_parts: PackedStringArray = PackedStringArray()
	detail_parts.append("comp %.2fx" % float(a.get("competence_modifier", 1.0)))
	detail_parts.append("ETA day %d" % (_day + days))
	if a["class"] == "demon":
		detail_parts.append("burn +%d → %d" % [
			int(a.get("burn_per_dispatch", 1)),
			int(st.get("burn", 0)) + int(a.get("burn_per_dispatch", 1))])
		if region_id == "small_wood":
			var per_day: float = float(r.get("demon_corruption_per_day_in_region", 0.0))
			var corr_risk: int = int(ceil(per_day * float(days)))
			detail_parts.append("[corr +~%d]" % corr_risk)
	else:
		var prev: int = int(st.get("obligation", 0))
		var bump: int = int(a.get("obligation_per_dispatch", 1))
		var cap: int = int(a.get("obligation_cap_before_stops_picking_up", 0))
		detail_parts.append("oblig +%d → %d/%d" % [bump, prev + bump, cap])
		# Warn about any threshold this dispatch would cross.
		var life: Dictionary = a.get("life_cost_thresholds", {})
		for k in life:
			var n: int = int(String(k))
			if prev < n and (prev + bump) >= n:
				detail_parts.append("crosses %d: %s" % [n, String(life[k])])
	var detail_lbl := Label.new()
	detail_lbl.text = "  " + "  ·  ".join(detail_parts)
	detail_lbl.add_theme_font_size_override("font_size", 9)
	detail_lbl.add_theme_color_override("font_color", Color(0.72, 0.72, 0.72, 1))
	detail_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	lcol.add_child(detail_lbl)
	# Pair-preview: if this row is a demon and another demon is
	# already on-dispatch to the same region, surface the pair
	# entry inline so the player sees the consequence before
	# they commit. Tone drives color: warm green, cold slate,
	# loud amber.
	if a["class"] == "demon":
		var pair_hint: Dictionary = _preview_demon_pair(agent_id, region_id)
		if not pair_hint.is_empty():
			var p_lbl := Label.new()
			var p_tone: String = String(pair_hint.get("tone", "warm"))
			var p_color := Color(0.53, 0.82, 0.66, 1)
			if p_tone == "loud":
				p_color = Color(0.86, 0.62, 0.42, 1)
			elif p_tone == "cold":
				p_color = Color(0.66, 0.68, 0.78, 1)
			var mods: PackedStringArray = PackedStringArray()
			var pc: int = int(pair_hint.get("cover", 0))
			var pa: int = int(pair_hint.get("attention", 0))
			if pc != 0: mods.append("cover %+d" % pc)
			if pa != 0: mods.append("attention %+d" % pa)
			var mod_tag := ""
			if not mods.is_empty():
				mod_tag = "  [" + "  ".join(mods) + "]"
			p_lbl.text = "  pair with %s%s · %s" % [
				String(pair_hint.get("partner_name", "")),
				mod_tag,
				String(pair_hint.get("log", ""))]
			p_lbl.add_theme_font_size_override("font_size", 9)
			p_lbl.add_theme_color_override("font_color", p_color)
			p_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			lcol.add_child(p_lbl)
	# Right: dispatch button
	var btn := Button.new()
	btn.text = "Dispatch"
	btn.focus_mode = Control.FOCUS_NONE
	btn.custom_minimum_size = Vector2(96, 32)
	var ag_capture: String = agent_id
	var rg_capture: String = region_id
	var pi_capture: int = problem_index
	btn.pressed.connect(func() -> void:
		_dispatch_agent(ag_capture, rg_capture, pi_capture)
		dlg.hide()
		dlg.queue_free())
	row.add_child(btn)
	return panel


func _dispatch_agent(agent_id: String, region_id: String, problem_index: int) -> void:
	var a: Dictionary = _agents[agent_id]
	var st: Dictionary = _agent_state[agent_id]
	var r: Dictionary = _regions[region_id]
	var p_ref: Dictionary = (_region_state[region_id]["active_problems"] as Array)[problem_index]
	# Compute travel + execute days. Effort_to_resolve weighted by
	# region travel-speed and agent competence.
	var base_days: float = float(p_ref["effort_remaining"]) / max(0.1, float(a.get("competence_modifier", 1.0)))
	var speed_mod: float = float(r.get("demon_travel_speed_modifier" if a["class"] == "demon" else "human_travel_speed_modifier", 1.0))
	var days: int = int(ceil(base_days / max(0.1, speed_mod)))
	# Cross-region cost: if agent's home_region != target, multiplier
	# from the target region's cross_region_dispatch_cost_modifier
	# (defaults to 1.5 if not specified).
	if String(a.get("home_region", "")) != region_id:
		var x_mod: float = float(r.get("cross_region_dispatch_cost_modifier", 1.5))
		days = int(ceil(float(days) * x_mod))
	if region_id == "small_wood" and String(a.get("home_region", "")) != "small_wood":
		days = int(ceil(float(days) * 1.5))
	st["on_dispatch"] = true
	st["return_day"] = _day + days
	if a["class"] == "demon":
		st["burn"] = int(st["burn"]) + int(a.get("burn_per_dispatch", 1))
		if region_id == "small_wood":
			# Corruption accrues per day in small wood.
			var per_day: float = float(r.get("demon_corruption_per_day_in_region", 0.0))
			var add_corr: int = int(ceil(per_day * float(days)))
			if add_corr > 0:
				_apply_corruption_to_demon(agent_id, add_corr)
		# Demon-pair interaction: if another demon is already on
		# dispatch to this same region, fire the pair effect (if any)
		# from the pair table. Ordered pairs so "moth+starling" and
		# "starling+moth" collapse to a single entry. Effects here
		# are flavor + a small mechanical bump (cover, attention).
		_maybe_fire_demon_pair(agent_id, region_id)
	else:
		var prev_obl: int = int(st["obligation"])
		var new_obl: int = prev_obl + int(a.get("obligation_per_dispatch", 1))
		st["obligation"] = new_obl
		# Reset the time-at-home strain flag for this new dispatch.
		st["days_away_since_dispatch"] = 0
		st["home_node_strained_this_dispatch"] = false
		# Fire any life_cost_thresholds the human just crossed.
		# The threshold dict keys are stringified obligation levels
		# ("3", "5"); values are the in-voice consequence.
		var life: Dictionary = a.get("life_cost_thresholds", {})
		for k in life:
			var n: int = int(String(k))
			if prev_obl < n and new_obl >= n:
				_log("[color=#c8a8ff][b]%s[/b] · obligation %d → %s[/color]" %
					[String(a["name"]), n, String(life[k])])
	p_ref["in_progress_by"] = String(a["name"])
	p_ref["dispatch_agent_id"] = agent_id
	p_ref["dispatch_resolution_day"] = _day + days
	# Stamp the dispatch's commit day. While committed_at_day == _day
	# the player can revoke this dispatch via the Today's Dispatches
	# panel. ADVANCE DAY commits — once committed_at_day < _day, the
	# dispatch is locked in.
	# Build the undo snapshot — pre-dispatch values, derived by
	# subtracting the bumps we just applied above.
	var snap_burn: int = 0
	var snap_obl: int = 0
	if a["class"] == "demon":
		snap_burn = int(st.get("burn", 0)) - int(a.get("burn_per_dispatch", 1))
	else:
		snap_obl = int(st.get("obligation", 0)) - int(a.get("obligation_per_dispatch", 1))
	_active_dispatches.append({
		"agent_id": agent_id,
		"region_id": region_id,
		"problem_index": problem_index,
		"return_day": _day + days,
		"competence_modifier": float(a.get("competence_modifier", 1.0)),
		"committed_at_day": _day,
		"undo_snapshot": {
			"burn": snap_burn,
			"obligation": snap_obl,
			"corruption": int(st.get("corruption", 0)),
		},
	})
	# Mission stages — if the template declares a stages[] array,
	# this dispatch is staged: the agent doesn't auto-resolve when
	# return_day arrives. Instead each stage fires a choice modal
	# on _on_advance_day; the player's choices apply effort + effects
	# through the existing _exec_effect interpreter. The dispatch
	# resolves deterministically after the final stage. Templates
	# without stages[] keep the existing auto-resolve flow.
	var template: Dictionary = _problem_templates.get(String(p_ref.get("template_id", "")), {})
	var stages: Array = template.get("stages", [])
	if not stages.is_empty():
		var d_entry: Dictionary = _active_dispatches[_active_dispatches.size() - 1]
		d_entry["is_staged"] = true
		d_entry["stage_index"] = 0
		d_entry["effort_accumulated"] = 0.0
		var first_stage: Dictionary = stages[0] as Dictionary
		d_entry["next_stage_day"] = _day + int(first_stage.get("fires_after_days", 1))
		# Move the return_day FAR into the future so the existing
		# auto-resolve path never triggers for a staged dispatch.
		# The dispatch resolves explicitly after the last stage
		# choice via _resolve_dispatch.
		d_entry["return_day"] = _day + 999
	_dispatches_this_day += 1
	_agent_dispatch_counts[agent_id] = int(_agent_dispatch_counts.get(agent_id, 0)) + 1
	_log("Day %d · [b]%s[/b] dispatched to [b]%s[/b] in %s. ETA day %d." %
		[_day, a["name"], p_ref["title"], r["name"], _day + days])
	_render()


# ── Day advance ──────────────────────────────────────────────────
func _on_advance_day() -> void:
	_day += 1
	_dispatches_this_day = 0
	# Fire any reveals scheduled for this day BEFORE other ticks, so
	# new regions / agents land in time for the day's processing.
	_fire_reveals_for_today()
	# Fire staged-mission stage modals BEFORE the auto-resolve pass.
	# A staged dispatch never auto-resolves; its stages drive the
	# resolution. Only one stage modal per advance is opened; if
	# multiple are due, the others queue and surface on subsequent
	# advances.
	for d in _active_dispatches.duplicate():
		if not bool(d.get("is_staged", false)):
			continue
		if bool(d.get("staged_done", false)):
			continue
		if int(d.get("next_stage_day", 999999)) <= _day:
			_open_stage_modal(d)
			break
	# Resolve returning dispatches.
	for d in _active_dispatches.duplicate():
		if int(d["return_day"]) <= _day:
			_resolve_dispatch(d)
			_active_dispatches.erase(d)
	# Per-day economy ticks: held-node resource production, the
	# withdrawal-pressure escalation, and the time-at-home cost
	# accruing on each human's home node while they're away.
	_tick_resource_yields()
	_tick_withdrawal_pressure()
	_tick_time_at_home()
	_tick_queued_burns()
	_tick_active_markers()
	_tick_agent_home_rest()
	_tick_roster_is_loud()
	_fire_daily_vignette()
	# Tick problems + accumulate per-region escalation. The actual
	# weekly spawn pass fires only on Sunday nights (day 7, 14, 21,
	# ...) per spec §Problems.
	for r_id in _region_state:
		_tick_region_problems(r_id)
		_tick_region_escalation(r_id)
	if _is_sunday(_day):
		_log("[i]Sunday night. The week ends.[/i]")
		_run_weekly_spawn()
		_fire_weekly_region_flavor()
		# BBS night. Open the BBS overlay; pause _on_advance_day
		# until the player hangs up. The overlay is a child Control
		# created lazily — exits and cleans itself up on hang_up.
		# Frasier is readmitted to SNACKS on W2.
		if _day >= 14 and not _readmitted_to_snacks:
			_readmitted_to_snacks = true
			_log("[color=#a8e0a8]WIRE_MOTHER's DM: 'you're back.'  SNACKS is reachable.[/color]")
		# W14 storm watch fires on the Sunday at the start of week 14.
		# Branches on whether the player has been reading the
		# BACKCHANNEL all summer — see _fire_w14_storm_watch.
		if _day >= 91 and not bool(_flags.get("w14_storm_watch_fired", false)):
			_fire_w14_storm_watch()
		await _open_bbs_night()
	# Dean's tower: re-roll brightness on the cadence; fire anomalies
	# when bright/white.
	_tick_dean_tower()
	# Check Dean interlude unlock conditions.
	_check_dean_interludes()
	# Check the (non-Dean) interlude shelf earn conditions.
	_check_interlude_earnings()
	# Win/loss check.
	if _day >= TURNS_TOTAL and not bool(_flags.get("labor_day_finale_shown", false)):
		_flags["labor_day_finale_shown"] = true
		_log("[b]Labor Day arrived.[/b] The summer's end. Interlude shelf: %d items (incl. %d from Dean)." %
			[_interlude_shelf.size(), _dean_interludes_earned.size()])
		_show_labor_day_finale()
	# Autosave at end of each day.
	_write_save()
	_render()


# ── Dean's network: the third faction ───────────────────────────
# Per _COMMUNITY_PLANNED_SPEC.md §Dean's network. Tower brightness
# re-rolls weekly. Bright / white weeks fire anomalies that bend
# the strategic rules — sometimes for, sometimes against. Player
# never sees Dean directly; only the effects + the occasional
# fingerprint in BBS thread flavor text.
func _tick_dean_tower() -> void:
	if _dean.is_empty():
		return
	var tower_cfg: Dictionary = _dean.get("tower", {})
	var cadence: int = int(tower_cfg.get("brightness_change_cadence_days", 7))
	if _day - _last_brightness_change_day < cadence:
		# Mid-week: anomalies might still fire if tower is bright/white.
		_maybe_fire_anomaly()
		return
	_last_brightness_change_day = _day
	# Weighted brightness reroll.
	var states: Array = tower_cfg.get("brightness_states", [])
	var total: float = 0.0
	for s in states:
		total += float(s.get("weight", 0.0))
	var rng := RandomNumberGenerator.new()
	rng.randomize()
	var pick: float = rng.randf() * total
	var running: float = 0.0
	for s in states:
		running += float(s.get("weight", 0.0))
		if pick <= running:
			_tower_brightness = String(s["state"])
			_log("[color=#a8a8c0]Day %d · The tower in Small Wood is %s.[/color]" %
				[_day, String(s["label"])])
			break
	if _tower_brightness == "white":
		_tower_state_revealed_white_once = true
	_maybe_fire_anomaly()


func _maybe_fire_anomaly() -> void:
	if _dean.is_empty():
		return
	if _tower_brightness == "dim":
		return  # No anomalies while tower is dim.
	var palette: Array = _dean.get("substrate_anomaly_palette", [])
	# Filter to anomalies eligible at this brightness.
	var eligible: Array = []
	for a in palette:
		var states_ok: Array = a.get("applies_when_tower", [])
		if states_ok.has(_tower_brightness):
			eligible.append(a)
	if eligible.is_empty():
		return
	# Fire chance scales with brightness: warming 0.20 / bright 0.45 / white 0.75.
	var fire_chance: float = {"warming": 0.20, "bright": 0.45, "white": 0.75}.get(_tower_brightness, 0.0)
	var rng := RandomNumberGenerator.new()
	rng.randomize()
	if rng.randf() > fire_chance:
		return
	# Pick weighted anomaly.
	var total: float = 0.0
	for a in eligible:
		total += float(a.get("weight", 1.0))
	var pick: float = rng.randf() * total
	var running: float = 0.0
	var chosen: Dictionary = {}
	for a in eligible:
		running += float(a.get("weight", 1.0))
		if pick <= running:
			chosen = a
			break
	if chosen.is_empty():
		return
	_anomalies_observed += 1
	_apply_anomaly(chosen)
	# Maybe leak a fingerprint into the log too.
	if rng.randf() < float(chosen.get("fingerprint_chance", 0.0)):
		_fingerprints_observed += 1
		_log("[color=#88c0ff][i]Fingerprint.[/i] %s[/color]" %
			String(chosen.get("fingerprint_text", "")))


func _apply_anomaly(a: Dictionary) -> void:
	var eff: Dictionary = a.get("engine_effect", {})
	var kind: String = String(eff.get("kind", ""))
	var rng := RandomNumberGenerator.new()
	rng.randomize()
	# All anomaly effects log their flavor.
	var log_str: String = String(eff.get("log", String(a.get("description", ""))))
	match kind:
		"freeze_problem_severity":
			var r_id: String = String(eff.get("region", "small_wood"))
			var st: Dictionary = _region_state.get(r_id, {})
			st["substrate_freeze_until_day"] = _day + int(eff.get("duration_days", 7))
			_log("[color=#a8a8c0][b]%s[/b] [i]Anomaly: severities in %s frozen for the week.[/i][/color]" %
				[String(a["title"]), _regions[r_id]["name"]])
		"resolve_random_problem":
			var r_id2: String = String(eff.get("region", "harmony_creek"))
			var probs: Array = _region_state[r_id2]["active_problems"]
			# Skip indices an active dispatch is bound to — removing
			# one shifts indices and breaks the dispatch's binding.
			var bound_indices: Dictionary = {}
			for ad in _active_dispatches:
				if String((ad as Dictionary).get("region_id", "")) == r_id2:
					bound_indices[int((ad as Dictionary).get("problem_index", -1))] = true
			var free_indices: Array = []
			for i in range(probs.size()):
				if not bound_indices.has(i):
					free_indices.append(i)
			if not free_indices.is_empty():
				var idx: int = int(free_indices[rng.randi() % free_indices.size()])
				_log("[color=#a8a8c0][b]%s[/b] [i]%s[/i][/color]" % [String(a["title"]), log_str])
				probs.remove_at(idx)
				# Shift each later-than-idx dispatch's problem_index down 1.
				for ad in _active_dispatches:
					var ad_d: Dictionary = ad
					if String(ad_d.get("region_id", "")) == r_id2 and int(ad_d.get("problem_index", -1)) > idx:
						ad_d["problem_index"] = int(ad_d["problem_index"]) - 1
		"wipe_corruption_on_demon_in_small_wood":
			var amount: int = int(eff.get("amount", 4))
			# The name says "in small wood" — honor it. Find demons
			# currently on dispatch to Small Wood via _active_dispatches.
			var demons_in_sw: Dictionary = {}
			for ad in _active_dispatches:
				if String((ad as Dictionary).get("region", "")) == "small_wood":
					demons_in_sw[String((ad as Dictionary).get("agent_id", ""))] = true
			for ag_id in _agent_state:
				if String(_agents[ag_id].get("class", "")) != "demon":
					continue
				if not demons_in_sw.has(ag_id):
					continue
				if int(_agent_state[ag_id]["corruption"]) > 0:
					_agent_state[ag_id]["corruption"] = max(0, int(_agent_state[ag_id]["corruption"]) - amount)
					_log("[color=#a8a8c0][b]%s[/b] [i]%s[/i] (%s, −%d corruption)[/color]" %
						[String(a["title"]), log_str, String(_agents[ag_id]["name"]), amount])
					break
		"downgrade_random_held_node_to_contested":
			var r_id3: String = String(eff.get("region", "graustark"))
			var held: Array = _region_state[r_id3]["held_nodes"]
			if not held.is_empty():
				var idx2: int = rng.randi() % held.size()
				var node: String = String(held[idx2])
				held.remove_at(idx2)
				_region_state[r_id3]["contested_nodes"].append(node)
				_log("[color=#a8a8c0][b]%s[/b] [i]%s (%s)[/i][/color]" %
					[String(a["title"]), log_str, node])
		"redirect_dispatch", "set_region_escalation_modifier":
			# Logged but not mechanically wired in phase 1.
			_log("[color=#a8a8c0][b]%s[/b] [i]%s[/i][/color]" % [String(a["title"]), log_str])
		_:
			_log("[color=#a8a8c0][b]%s[/b] [i]%s[/i][/color]" % [String(a["title"]), log_str])


# ── Interlude shelf ─────────────────────────────────────────────
# Per _COMMUNITY_PLANNED_SPEC.md §The interlude economy. Each
# interlude has an earn predicate over the run's state. Once
# earned, it's on the shelf permanently. Spec success criteria:
# at least 8 items, at least 3 Small Wood seeds, at least one
# canon-human friendship that changed. interludes.json authors
# ~20 candidates so any reasonable play style earns 8+.
func _check_interlude_earnings() -> void:
	for section in ["small_wood_seed_interludes", "canon_friendship_interludes",
	                "summer_milestone_interludes", "cross_cutting_interludes",
	                "aria_summer_w11_interludes"]:
		for entry in _interludes_def.get(section, []):
			var i_id: String = String(entry["id"])
			if _interlude_shelf.has(i_id):
				continue
			if _interlude_earn_predicate(String(entry.get("earn_condition", "")), entry):
				_interlude_shelf.append(i_id)
				_interlude_meta[i_id] = {
					"day_earned": _day,
					"section": String(entry.get("shelf_section", section)),
					"title": String(entry["title"]),
				}
				_log("[color=#a8c0a8][b]Interlude:[/b] %s[/color]" % String(entry["title"]))


func _interlude_earn_predicate(cond: String, entry: Dictionary) -> bool:
	# Predicates simplify the spec descriptions into countable
	# checks over the run state. Anything unknown returns false.
	match cond:
		"always":
			return true
		"reached_day_7":
			return _day >= 7
		"reached_day_100":
			return _day >= TURNS_TOTAL
		# ─── Small Wood seeds ─────────────────────────────────────
		"small_wood_held_at_labor_day":
			if _day < TURNS_TOTAL: return false
			var sw: Dictionary = _region_state.get("small_wood", {})
			return (sw.get("held_nodes", []) as Array).size() >= 1
		"small_wood_resolved_problem_count_min_3":
			return int(_problem_resolved_by_region.get("small_wood", 0)) >= 3
		"small_wood_seed_dying_resolved_min_2":
			return int(_problem_resolved_counts.get("seed_dying", 0)) >= 2
		"small_wood_lost_target_node":
			var sw2: Dictionary = _region_state.get("small_wood", {})
			# The spec scaffold has 3 target_nodes at start; if any
			# disappeared by Labor Day the seed-that-didnt interlude
			# fires. Only fires AT labor day so it reads as the
			# summer's tally, not a mid-game scold.
			if _day < TURNS_TOTAL: return false
			return (sw2.get("target_nodes", []) as Array).size() < 3
		"jules_resolved_problem_count_min_2_obligation_under_cap":
			var st: Dictionary = _agent_state.get("the_small_wood_contact_jules", {})
			var cap: int = int(_agents.get("the_small_wood_contact_jules", {}).get("obligation_cap_before_stops_picking_up", 0))
			return (int(st.get("successful_dispatches_by_region", {}).get("small_wood", 0)) >= 2
				and int(st.get("obligation", 0)) < cap)
		# ─── Canon humans · friendship arcs ───────────────────────
		"mackenzie_dispatched_min_5_obligation_under_4_at_labor_day":
			if _day < TURNS_TOTAL: return false
			var disp: int = int(_agent_dispatch_counts.get("mackenzie", 0))
			var obl: int = int(_agent_state.get("mackenzie", {}).get("obligation", 0))
			return disp >= 5 and obl < 4
		"mackenzie_obligation_hit_cap":
			var cap2: int = int(_agents.get("mackenzie", {}).get("obligation_cap_before_stops_picking_up", 0))
			return int(_agent_state.get("mackenzie", {}).get("obligation", 0)) >= cap2
		"surviving_son_dispatched_min_3_obligation_under_3_at_labor_day":
			if _day < TURNS_TOTAL: return false
			return (int(_agent_dispatch_counts.get("the_surviving_son", 0)) >= 3
				and int(_agent_state.get("the_surviving_son", {}).get("obligation", 0)) < 3)
		"surviving_son_obligation_hit_cap":
			var cap3: int = int(_agents.get("the_surviving_son", {}).get("obligation_cap_before_stops_picking_up", 0))
			return int(_agent_state.get("the_surviving_son", {}).get("obligation", 0)) >= cap3
		"john_frank_dispatched_min_4_obligation_under_6_at_labor_day":
			if _day < TURNS_TOTAL: return false
			return (int(_agent_dispatch_counts.get("john_frank", 0)) >= 4
				and int(_agent_state.get("john_frank", {}).get("obligation", 0)) < 6)
		"john_frank_obligation_hit_cap":
			var cap4: int = int(_agents.get("john_frank", {}).get("obligation_cap_before_stops_picking_up", 0))
			return int(_agent_state.get("john_frank", {}).get("obligation", 0)) >= cap4
		"elicia_dispatched_min_3_obligation_under_4_at_labor_day":
			if _day < TURNS_TOTAL: return false
			return (int(_agent_dispatch_counts.get("elicia", 0)) >= 3
				and int(_agent_state.get("elicia", {}).get("obligation", 0)) < 4)
		"nicola_dispatched_min_2_obligation_under_3_at_labor_day":
			if _day < TURNS_TOTAL: return false
			return (int(_agent_dispatch_counts.get("nicola", 0)) >= 2
				and int(_agent_state.get("nicola", {}).get("obligation", 0)) < 3)
		# ─── Summer milestones ────────────────────────────────────
		"memorial_grief_resolved_min_2_by_day_55":
			return _day >= 55 and int(_problem_resolved_counts.get("memorial_grief", 0)) >= 2
		"graustark_low_pressure_at_day_85":
			if _day < 85: return false
			var gp: Array = _region_state.get("graustark", {}).get("active_problems", [])
			return gp.size() <= 2
		# ─── Cross-cutting ────────────────────────────────────────
		"cathedral_visitor_resolved_min_2":
			return int(_problem_resolved_counts.get("cathedral_visitor", 0)) >= 2
		"any_demon_complexity_min_5":
			for ag_id in _agent_state:
				if _agents.get(ag_id, {}).get("class", "") != "demon": continue
				if int(_agent_state[ag_id].get("complexity", 0)) >= 5: return true
			return false
		"family_succession_resolved_min_2":
			return int(_problem_resolved_counts.get("family_succession", 0)) >= 2
		"diner_threshold_resolved_min_2":
			return int(_problem_resolved_counts.get("diner_threshold", 0)) >= 2
		"summer_with_tower_dim_majority":
			# Approximation: tower was dim if we never saw it warm/bright/white >2 weeks.
			if _day < TURNS_TOTAL: return false
			return not _tower_state_revealed_white_once
		"any_agent_sent_to_tower":
			for ag_id in _agent_state:
				if bool(_agent_state[ag_id].get("sent_to_tower", false)): return true
			return false
		# ─── Aria W11 branches (phase 3 sprint 1) ────────────────
		"aria_w11_choice_rebind":
			return String(_canon_vars.get("aria_w11_choice", "")) == "rebind"
		"aria_w11_choice_rebind_and_storm_hard":
			return String(_canon_vars.get("aria_w11_choice", "")) == "rebind" \
				and bool(_flags.get("w14_storm_hard_branch", false))
		"aria_w11_choice_let_her_hold_it":
			return String(_canon_vars.get("aria_w11_choice", "")) == "let_her_hold_it"
		"aria_w11_choice_let_her_hold_it_and_burns_landed":
			return String(_canon_vars.get("aria_w11_choice", "")) == "let_her_hold_it" \
				and _day >= 91
		"aria_w11_choice_send_her_away":
			return String(_canon_vars.get("aria_w11_choice", "")) == "send_her_away"
		"aria_w11_choice_send_her_away_and_reached_labor_day":
			return String(_canon_vars.get("aria_w11_choice", "")) == "send_her_away" \
				and _day >= TURNS_TOTAL
	return false


# Returns combined shelf entries (Dean + the other four sections)
# in the order they were earned, with their full text. Used by the
# shelf modal.
func _all_earned_interludes() -> Array:
	var out: Array = []
	# Dean first (the rarer / sparer section).
	for s in _dean.get("dean_interlude_seeds", []):
		if _dean_interludes_earned.has(String(s["id"])):
			out.append({
				"id": s["id"], "title": s["title"], "flavor": s["flavor"],
				"section": String(s.get("shelf_section", "dean"))
			})
	# The rest from interludes.json — pick up by id from the shelf.
	var by_id: Dictionary = {}
	for section in ["small_wood_seed_interludes", "canon_friendship_interludes",
	                "summer_milestone_interludes", "cross_cutting_interludes",
	                "aria_summer_w11_interludes"]:
		for entry in _interludes_def.get(section, []):
			by_id[String(entry["id"])] = entry
	for i_id in _interlude_shelf:
		var ent: Dictionary = by_id.get(String(i_id), {})
		if ent.is_empty(): continue
		out.append({
			"id": ent["id"], "title": ent["title"], "flavor": ent["flavor"],
			"section": String(ent.get("shelf_section", ""))
		})
	return out


func _open_interlude_shelf() -> void:
	var dlg := AcceptDialog.new()
	dlg.title = "Interlude Shelf"
	dlg.min_size = Vector2(680, 540)
	var scroll := ScrollContainer.new()
	scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.custom_minimum_size = Vector2(660, 500)
	dlg.add_child(scroll)
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 14)
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(col)
	var entries: Array = _all_earned_interludes()
	if entries.is_empty():
		var none := Label.new()
		none.text = "The shelf is empty. Stay with the summer. Things land."
		none.add_theme_color_override("font_color", Color(0.62, 0.62, 0.62, 1))
		col.add_child(none)
	else:
		var summary := Label.new()
		summary.text = "%d entries on the shelf." % entries.size()
		summary.add_theme_color_override("font_color", Color(0.92, 0.86, 0.62, 1))
		summary.add_theme_font_size_override("font_size", 12)
		col.add_child(summary)
		for entry in entries:
			var rule := ColorRect.new()
			rule.color = Color(0.32, 0.32, 0.32, 0.6)
			rule.custom_minimum_size = Vector2(0, 1)
			col.add_child(rule)
			var title := Label.new()
			title.text = String(entry["title"])
			title.add_theme_font_size_override("font_size", 13)
			var section: String = String(entry.get("section", ""))
			var title_color := Color(0.92, 0.86, 0.62, 1)
			if section == "dean": title_color = Color(0.78, 0.62, 0.96, 1)
			elif section == "small_wood_seeds": title_color = Color(0.62, 0.96, 0.74, 1)
			elif section == "canon_humans": title_color = Color(0.96, 0.86, 0.62, 1)
			elif section == "milestones": title_color = Color(0.86, 0.96, 0.62, 1)
			elif section == "cross_cutting": title_color = Color(0.74, 0.84, 0.96, 1)
			elif section == "aria_w11": title_color = Color(0.96, 0.74, 0.62, 1)
			title.add_theme_color_override("font_color", title_color)
			col.add_child(title)
			var body := Label.new()
			body.text = String(entry["flavor"])
			body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			body.add_theme_font_size_override("font_size", 11)
			body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			col.add_child(body)
	# BBS artifact section. Folded in below the interludes; the
	# artifacts unlocked via THE_LIBRARY / THE_ART_WALL / THE_ATTIC
	# read-throughs surface here, plus anything DM reply effects
	# placed via unlock_artifact.
	if not _unlocked_artifacts.is_empty():
		var spacer := ColorRect.new()
		spacer.color = Color(0.32, 0.62, 0.32, 0.6)
		spacer.custom_minimum_size = Vector2(0, 2)
		col.add_child(spacer)
		var heading := Label.new()
		heading.text = "BBS · UNLOCKED ARTIFACTS"
		heading.add_theme_font_size_override("font_size", 12)
		heading.add_theme_color_override("font_color", Color(0.86, 0.78, 0.42, 1))
		col.add_child(heading)
		for aid in _unlocked_artifacts:
			var arule := ColorRect.new()
			arule.color = Color(0.32, 0.32, 0.32, 0.4)
			arule.custom_minimum_size = Vector2(0, 1)
			col.add_child(arule)
			var atitle := Label.new()
			atitle.text = String(aid)
			atitle.add_theme_font_size_override("font_size", 12)
			atitle.add_theme_color_override("font_color", Color(0.86, 0.78, 0.42, 1))
			col.add_child(atitle)
	dlg.add_to_group("ui")  # F4 sweep catches modals
	add_child(dlg)
	dlg.popup_centered()


# ── Mission stages ──────────────────────────────────────────────
# Multi-stage dispatch system. A problem template that declares a
# stages[] array makes its dispatches multi-decision instead of
# fire-and-forget. Each stage fires a choice modal; the player's
# choice applies effort + effects through the existing _exec_effect
# interpreter. After the final stage choice the dispatch resolves
# deterministically based on accumulated effort vs effort_to_resolve.
func _open_stage_modal(d: Dictionary) -> void:
	var agent_id: String = String(d["agent_id"])
	var region_id: String = String(d["region_id"])
	var pi: int = int(d.get("problem_index", -1))
	var probs: Array = (_region_state.get(region_id, {}) as Dictionary).get("active_problems", [])
	if pi < 0 or pi >= probs.size():
		# Problem disappeared underneath the dispatch — close it out.
		d["staged_done"] = true
		d["return_day"] = _day
		return
	var p_ref: Dictionary = probs[pi]
	var template: Dictionary = _problem_templates.get(String(p_ref.get("template_id", "")), {})
	var stages: Array = template.get("stages", [])
	var stage_index: int = int(d.get("stage_index", 0))
	if stage_index >= stages.size():
		d["staged_done"] = true
		d["return_day"] = _day
		return
	var stage: Dictionary = stages[stage_index] as Dictionary
	var agent_name: String = String(_agents.get(agent_id, {}).get("name", agent_id))
	var dlg := AcceptDialog.new()
	dlg.title = "%s · %s · stage %d/%d" % [
		String(p_ref["title"]), agent_name, stage_index + 1, stages.size()]
	dlg.min_size = Vector2(640, 480)
	dlg.get_ok_button().visible = false
	var scroll := ScrollContainer.new()
	scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.custom_minimum_size = Vector2(620, 440)
	dlg.add_child(scroll)
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 10)
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(col)
	var hdr := Label.new()
	hdr.text = String(stage.get("title", "stage"))
	hdr.add_theme_font_size_override("font_size", 14)
	hdr.add_theme_color_override("font_color", Color(0.96, 0.86, 0.62, 1))
	col.add_child(hdr)
	var sub := Label.new()
	sub.text = "%s is at %s · day %d" % [agent_name,
		String(_regions.get(region_id, {}).get("name", region_id)), _day]
	sub.add_theme_font_size_override("font_size", 10)
	sub.add_theme_color_override("font_color", Color(0.62, 0.62, 0.62, 1))
	col.add_child(sub)
	col.add_child(_dossier_rule())
	var body_text: String = String(stage.get("body", "")).replace("{agent}", agent_name)
	var body := Label.new()
	body.text = body_text
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.add_theme_font_size_override("font_size", 11)
	body.add_theme_color_override("font_color", Color(0.86, 0.86, 0.86, 1))
	col.add_child(body)
	col.add_child(_dossier_rule())
	var choices: Array = stage.get("choices", [])
	for choice_v in choices:
		var choice: Dictionary = choice_v as Dictionary
		# BBS-lookup gate: a choice that requires the player to have
		# read a specific BBS thread is shown LOCKED if the thread
		# isn't in _bbs_read_thread_ids. The label still renders so
		# the player knows the option exists; the button is disabled
		# and the summary names the required thread + board.
		var requires_thread: String = String(choice.get("requires_bbs_thread", ""))
		var locked: bool = (requires_thread != "" and not _bbs_read_thread_ids.has(requires_thread))
		var btn := Button.new()
		btn.text = String(choice.get("label", "(choice)"))
		if locked:
			btn.text = "  🔒  " + btn.text
		btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		btn.add_theme_font_size_override("font_size", 11)
		btn.add_theme_color_override("font_color",
			Color(0.42, 0.48, 0.42, 1) if locked else Color(0.86, 0.96, 0.74, 1))
		btn.disabled = locked
		col.add_child(btn)
		if locked:
			var lock_lbl := Label.new()
			lock_lbl.text = "        locked · needs to have read thread %s on the BBS" % requires_thread
			lock_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			lock_lbl.add_theme_font_size_override("font_size", 10)
			lock_lbl.add_theme_color_override("font_color", Color(0.62, 0.50, 0.32, 1))
			col.add_child(lock_lbl)
		var summary: String = String(choice.get("summary", ""))
		if summary != "":
			var sm := Label.new()
			sm.text = "        " + summary
			sm.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			sm.add_theme_font_size_override("font_size", 10)
			sm.add_theme_color_override("font_color", Color(0.62, 0.78, 0.62, 1))
			col.add_child(sm)
		var d_capture: Dictionary = d
		var choice_capture: Dictionary = choice
		btn.pressed.connect(func() -> void:
			dlg.queue_free()
			_apply_stage_choice(d_capture, choice_capture))
	dlg.add_to_group("ui")
	add_child(dlg)
	dlg.popup_centered()


func _apply_stage_choice(d: Dictionary, choice: Dictionary) -> void:
	var agent_id: String = String(d["agent_id"])
	var region_id: String = String(d["region_id"])
	var pi: int = int(d.get("problem_index", -1))
	var probs: Array = (_region_state.get(region_id, {}) as Dictionary).get("active_problems", [])
	if pi < 0 or pi >= probs.size():
		d["staged_done"] = true
		d["return_day"] = _day
		return
	var p_ref: Dictionary = probs[pi]
	var template: Dictionary = _problem_templates.get(String(p_ref.get("template_id", "")), {})
	var stages: Array = template.get("stages", [])
	var stage_index: int = int(d.get("stage_index", 0))
	# Apply the choice's effort and effects.
	var effort_applied: float = float(choice.get("effort_applied", 0.0))
	d["effort_accumulated"] = float(d.get("effort_accumulated", 0.0)) + effort_applied
	p_ref["effort_remaining"] = max(0.0, float(p_ref.get("effort_remaining", 0.0)) - effort_applied)
	var ctx: Dictionary = {"region_id": region_id, "agent_id": agent_id, "problem": p_ref}
	for ef in choice.get("effects", []):
		if typeof(ef) == TYPE_DICTIONARY:
			_exec_effect(ef, ctx)
	_log("[color=#c8e896]Day %d · [b]%s[/b] · %s[/color]" % [
		_day, String(_agents.get(agent_id, {}).get("name", agent_id)),
		String(choice.get("label", ""))])
	# Advance to the next stage (or close out).
	var next_index: int = stage_index + 1
	d["stage_index"] = next_index
	if next_index >= stages.size():
		# Last stage done. Resolve immediately — deterministic
		# success because the choices were the resolution.
		d["staged_done"] = true
		d["return_day"] = _day
		_resolve_dispatch(d)
		_active_dispatches.erase(d)
	else:
		var next_stage: Dictionary = stages[next_index] as Dictionary
		d["next_stage_day"] = _day + int(next_stage.get("fires_after_days", 1))
	_render()


# ── Summer intro ────────────────────────────────────────────────
# Fires once per save on first day. Frasier's letter to himself at
# the cathedral desk on Memorial Day morning, '96. Sets the season
# up + hints at the gameplay rhythm in voice — Sundays are the
# circle's night, weekdays are the dispatch work, the shelf at the
# end is what the summer leaves you. Diegetic, not a tutorial popup.
func _show_summer_intro() -> void:
	if bool(_flags.get("summer_intro_shown", false)):
		return
	_flags["summer_intro_shown"] = true
	var dlg := AcceptDialog.new()
	dlg.title = "Memorial Day · 1996"
	dlg.min_size = Vector2(640, 520)
	dlg.get_ok_button().text = "begin the summer"
	var scroll := ScrollContainer.new()
	scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.custom_minimum_size = Vector2(620, 480)
	dlg.add_child(scroll)
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 10)
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(col)

	var hdr := Label.new()
	hdr.text = "the cathedral office · Monday, May 27"
	hdr.add_theme_font_size_override("font_size", 11)
	hdr.add_theme_color_override("font_color", Color(0.62, 0.62, 0.62, 1))
	col.add_child(hdr)

	var title := Label.new()
	title.text = "what's on the desk this summer"
	title.add_theme_font_size_override("font_size", 16)
	title.add_theme_color_override("font_color", Color(0.96, 0.86, 0.62, 1))
	col.add_child(title)

	col.add_child(_dossier_rule())

	var paragraphs := [
		"Pop's ledger is on the desk. The Klein lineman's pliers are in the toolbox. The Pliny is on the shelf above the modem and the modem is humming the way the modem hums in May.",
		"A hundred days between Memorial Day and Labor Day. We've done this before. The rhythm holds.",
		"[color=#a8e0a8]Weekdays — the dispatch work.[/color] Problems land in Graustark, in the regions at the edges, in the rooms we don't always see. Look at them. Send the right people. The agent list is on the left. Click a problem to read what it actually is; click a name to see who the person is. Cover is the resource you spend to be elsewhere visibly; burn is what the demons carry home from a long week.",
		"[color=#a8e0a8]Sunday night — the modem.[/color] The cathedral office goes dark around 9 and the dial-up wakes up around 10. The circle is on the line. STEEPLE in Mobile. WIRE_MOTHER in Lubbock. PALOMINO in Santa Fe. THE_QUARRY in Pennsylvania. SNACKS, once the matriarch lets us back in. There is reading to do and a DM panel for the canon humans — pick a number to open a board, M for mail, B back, Q to hang up. Pace yourself; the circle doesn't reward speed.",
		"[color=#a8e0a8]The shelf — what the summer leaves.[/color] Every choice that matters lands on a shelf at Labor Day. Interludes, artifacts, the canon facts the family will carry into the fall. The summer is the choice-making; the shelf is the record.",
		"Three beats to mark on the calendar without circling them: W11, when the question that has been forming for fifteen years gets asked out loud; W14, when the gulf decides which way to come; Labor Day, when the cookout in the back lot of the storefront either happens or doesn't, depending on who is at booth four.",
		"There will be days that read quiet. Read the quiet too. The boiler hums two semitones flat. Faith II brings coffee at 11:14. The cathedral bell pulls at 11 and three of the regulars are inside before the second pull. That's all the work too.",
		"  — F."
	]
	for p_text in paragraphs:
		var p := RichTextLabel.new()
		p.bbcode_enabled = true
		p.fit_content = true
		p.text = p_text
		p.add_theme_font_size_override("normal_font_size", 12)
		p.add_theme_color_override("default_color", Color(0.86, 0.86, 0.86, 1))
		p.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		col.add_child(p)

	col.add_child(_dossier_rule())

	var coda := Label.new()
	coda.text = "press [begin the summer] to open the office."
	coda.add_theme_font_size_override("font_size", 10)
	coda.add_theme_color_override("font_color", Color(0.62, 0.78, 0.62, 1))
	col.add_child(coda)

	dlg.add_to_group("ui")  # F4 sweep catches modals
	add_child(dlg)
	dlg.popup_centered()


# ── Labor Day finale ────────────────────────────────────────────
# Per _COMMUNITY_PLANNED_PHASE3_SCOPE.md §Sprint 3. Day 100 fires
# this once. Purely declarative — the summer was the choice-making;
# the finale shows the player what they carried.
func _compute_labor_day_branch_id() -> String:
	var aria: String = String(_canon_vars.get("aria_w11_choice", "none"))
	var storm: String = "soft" if bool(_flags.get("w14_storm_hard_branch", false)) == false else "hard"
	if not bool(_flags.get("w14_storm_watch_fired", false)):
		storm = "none"
	var tower: String = _tower_brightness
	var shelf: int = _interlude_shelf.size() + _dean_interludes_earned.size()
	var density: String = "sparse"
	if shelf >= 14: density = "dense"
	elif shelf >= 8: density = "full"
	return "%s.%s.%s.%s" % [aria, storm, tower, density]


func _labor_day_cookout_vignette() -> String:
	var aria: String = String(_canon_vars.get("aria_w11_choice", "none"))
	match aria:
		"rebind":
			return "Sunday, September 1, 1996. The back lot of the storefront, 4 PM into the long blue dusk. Hector brought the brisket from Baton Rouge and the boy carried the second pan. Mom is at the picnic table Pop's father built in '64. Nicola is at the picnic table next to her. Aria is between them, fourteen, leaning against her mother's shoulder, eating a piece of cornbread with both hands."
		"let_her_hold_it":
			return "Sunday, September 1, 1996. The back lot of the storefront. The cookout took the shape it took. Aria came with the wooden box JF made her in '94. She set it under her seat. Nobody asked. Hector's brisket sold out at 7. Mom said the gumbo was the gumbo Pop liked. Aria stayed until 8 and then walked home with Nicola the long way."
		"send_her_away":
			return "Sunday, September 1, 1996. The back lot of the storefront. The seat next to Mom was empty. Mom kept looking up at the back door as if Aria were going to come through it. Elicia drove down from the bungalow with a print of the cottonwood and stayed through dinner; she sat in the seat next to Mom and the seat was less empty than it had been."
		_:
			return "Sunday, September 1, 1996. The back lot of the storefront. The cookout was the cookout. The brisket was the brisket. Hector's boy was at the picnic table with his college acceptance folded in his pocket and he showed it to anyone who asked. The summer ended in the kind of dusk it ended in every year."


func _closing_line_for(canonical: String) -> String:
	var aria: String = String(_canon_vars.get("aria_w11_choice", "none"))
	match canonical:
		"john_frank":
			match aria:
				"rebind":           return "The conduit held. The room held. I'll be at booth four Friday. — JF"
				"let_her_hold_it":  return "She's a person. Whatever the year takes, the room takes too. — JF"
				"send_her_away":    return "I'll drive up to the bungalow with the cradle I made for her in '82. The bungalow has the right wood for it. — JF"
				_:                  return "I'll be at booth four Friday. — JF"
		"the_surviving_son":
			match aria:
				"rebind":           return "Mom said the gumbo was the gumbo Pop liked. The booth was full. — T."
				"let_her_hold_it":  return "Aria came with the wooden box. Mom didn't ask what was in it. The box stayed under her seat. — T."
				"send_her_away":    return "We saved the seat for her anyway. Mom kept looking up. Elicia took the seat instead. — T."
				_:                  return "The kitchen held. — T."
		"mackenzie":
			match aria:
				"rebind":           return "I'm writing the piece I came down to write, finally. It's not the one I started in May. — mac"
				"let_her_hold_it":  return "I'm staying through fall. There's a draft I want to read again before I print it. — mac"
				"send_her_away":    return "I drove up to the bungalow Sunday afternoon. Elicia made coffee. Aria showed me the list. — mac"
				_:                  return "I'm staying through fall. — mac"
		"elicia_duchane":
			match aria:
				"send_her_away":    return "The bungalow is busier than it's been since the spring. Aria is reading the kind of book my mother used to read. — E."
				_:                  return "The cottonwood came in three weeks early. The piece runs in October. — E."
		"frasier_temple":
			return "The office is locked. The cathedral is the cathedral. I'll be in Tuesday at 9. — F."
	return ""


func _show_labor_day_finale() -> void:
	var dlg := AcceptDialog.new()
	dlg.title = "Labor Day · September 1, 1996"
	dlg.min_size = Vector2(820, 720)
	var scroll := ScrollContainer.new()
	scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.custom_minimum_size = Vector2(800, 680)
	dlg.add_child(scroll)
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 12)
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(col)
	# Header
	var title := Label.new()
	title.text = "The summer's end."
	title.add_theme_font_size_override("font_size", 18)
	title.add_theme_color_override("font_color", Color(0.96, 0.86, 0.62, 1))
	col.add_child(title)
	# The cookout vignette
	var vignette := Label.new()
	vignette.text = _labor_day_cookout_vignette()
	vignette.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	vignette.add_theme_font_size_override("font_size", 12)
	vignette.add_theme_color_override("font_color", Color(0.86, 0.86, 0.86, 1))
	col.add_child(vignette)
	# Rule
	var rule := ColorRect.new()
	rule.color = Color(0.32, 0.62, 0.32, 0.6)
	rule.custom_minimum_size = Vector2(0, 2)
	col.add_child(rule)
	# Closing lines from each canon human
	var lines_heading := Label.new()
	lines_heading.text = "Closing lines"
	lines_heading.add_theme_font_size_override("font_size", 14)
	lines_heading.add_theme_color_override("font_color", Color(0.86, 0.96, 0.62, 1))
	col.add_child(lines_heading)
	for canonical in ["frasier_temple", "the_surviving_son", "john_frank", "mackenzie", "elicia_duchane"]:
		var line := Label.new()
		line.text = _closing_line_for(canonical)
		if line.text == "":
			continue
		line.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		line.add_theme_font_size_override("font_size", 12)
		line.add_theme_color_override("font_color", Color(0.74, 0.84, 0.96, 1))
		col.add_child(line)
	# Rule
	var rule2 := ColorRect.new()
	rule2.color = Color(0.32, 0.62, 0.32, 0.6)
	rule2.custom_minimum_size = Vector2(0, 2)
	col.add_child(rule2)
	# Shelf summary
	var shelf_heading := Label.new()
	shelf_heading.text = "On the shelf · %d entries" % (_interlude_shelf.size() + _dean_interludes_earned.size())
	shelf_heading.add_theme_font_size_override("font_size", 14)
	shelf_heading.add_theme_color_override("font_color", Color(0.86, 0.96, 0.62, 1))
	col.add_child(shelf_heading)
	for entry in _all_earned_interludes():
		var ent_lbl := Label.new()
		ent_lbl.text = "  · %s" % String(entry["title"])
		ent_lbl.add_theme_font_size_override("font_size", 11)
		ent_lbl.add_theme_color_override("font_color", Color(0.92, 0.86, 0.62, 1))
		col.add_child(ent_lbl)
	# Artifacts
	if not _unlocked_artifacts.is_empty():
		var art_heading := Label.new()
		art_heading.text = "Artifacts · %d unlocked" % _unlocked_artifacts.size()
		art_heading.add_theme_font_size_override("font_size", 13)
		art_heading.add_theme_color_override("font_color", Color(0.86, 0.78, 0.42, 1))
		col.add_child(art_heading)
		for aid in _unlocked_artifacts:
			var alabel := Label.new()
			alabel.text = "  · %s" % String(aid)
			alabel.add_theme_font_size_override("font_size", 11)
			alabel.add_theme_color_override("font_color", Color(0.86, 0.78, 0.42, 1))
			col.add_child(alabel)
	# Branch id (small, at the bottom — for the record)
	var rule3 := ColorRect.new()
	rule3.color = Color(0.32, 0.32, 0.32, 0.4)
	rule3.custom_minimum_size = Vector2(0, 1)
	col.add_child(rule3)
	var branch_lbl := Label.new()
	branch_lbl.text = "branch: %s" % _compute_labor_day_branch_id()
	branch_lbl.add_theme_font_size_override("font_size", 10)
	branch_lbl.add_theme_color_override("font_color", Color(0.42, 0.42, 0.42, 1))
	col.add_child(branch_lbl)
	# Wire close → show outro
	dlg.confirmed.connect(_show_post_summer_outro)
	dlg.add_to_group("ui")  # F4 sweep catches modals
	add_child(dlg)
	dlg.popup_centered()


func _show_post_summer_outro() -> void:
	var dlg := AcceptDialog.new()
	dlg.title = "After the summer"
	dlg.min_size = Vector2(620, 420)
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 10)
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	dlg.add_child(col)
	var heading := Label.new()
	heading.text = "What you carried out of the summer"
	heading.add_theme_font_size_override("font_size", 14)
	heading.add_theme_color_override("font_color", Color(0.96, 0.86, 0.62, 1))
	col.add_child(heading)
	var items: Array = []
	items.append("· %d interludes on the shelf" % (_interlude_shelf.size() + _dean_interludes_earned.size()))
	items.append("· %d artifacts unlocked from the BBS" % _unlocked_artifacts.size())
	items.append("· %d hidden boards discovered" % _bbs_discovered_hidden_boards.size())
	items.append("· %d threads read across the summer" % _bbs_read_thread_ids.size())
	items.append("· %d DM replies on record" % _dm_reply_log.size())
	# Regional-events fired · texture-per-week metric
	items.append("· %d weekly regional events lived through" % _fired_regional_events.size())
	# Top handlers by dispatch count · reads back on the summer's rhythm
	var dispatch_by_agent: Dictionary = {}
	for a_id in _agent_state:
		var st: Dictionary = _agent_state[a_id]
		var per_region: Dictionary = st.get("successful_dispatches_by_region", {})
		var total: int = 0
		for k in per_region:
			total += int(per_region[k])
		if total > 0:
			dispatch_by_agent[a_id] = total
	if not dispatch_by_agent.is_empty():
		var sorted_ids: Array = dispatch_by_agent.keys()
		sorted_ids.sort_custom(func(a, b) -> bool:
			return int(dispatch_by_agent[a]) > int(dispatch_by_agent[b]))
		var top_line := "· Handlers who carried the summer:"
		var top_n: int = min(3, sorted_ids.size())
		for i in range(top_n):
			var a_id: String = String(sorted_ids[i])
			var name: String = String(_agents.get(a_id, {}).get("name", a_id))
			var count: int = int(dispatch_by_agent[a_id])
			top_line += "  %s (%d)" % [name, count]
		items.append(top_line)
	# Region reputation snapshot · cover at summer's end
	var reg_line := "· Cover left at Labor Day: "
	var reg_parts: Array = []
	for r_id in _visible_regions:
		if not _region_state.has(r_id): continue
		var reg_name: String = String(_regions.get(r_id, {}).get("name", r_id))
		var cover: int = int(_region_state[r_id].get("cover", 0))
		reg_parts.append("%s %d" % [reg_name.split(" ")[0], cover])
	items.append(reg_line + " · ".join(reg_parts))
	# Gauntlet crossover · lore tokens carried out of the summer
	var gs: Node = get_node_or_null("/root/GauntletState")
	if gs != null:
		var g_state: Dictionary = gs.get("state") if gs.get("state") is Dictionary else {}
		var g_lore: Array = g_state.get("lore_tokens_revealed", [])
		var g_cp_unlocks: Array = g_state.get("cp_scenario_unlocks", [])
		if not g_lore.is_empty():
			items.append("· %d gauntlet lore tokens carried across from the arcana runs" % g_lore.size())
		if not g_cp_unlocks.is_empty():
			items.append("· %d gauntlet scenarios unlocked by your CP choices this summer" % g_cp_unlocks.size())
	# Any active regional markers that are still on the map at Labor Day
	if not _active_regional_markers.is_empty():
		items.append("· %d regional markers still on the map at summer's end" % _active_regional_markers.size())
	var aria: String = String(_canon_vars.get("aria_w11_choice", "none"))
	if aria != "none":
		items.append("· Aria · the W11 choice was: %s" % aria.replace("_", " "))
	if bool(_flags.get("w14_storm_hard_branch", false)):
		items.append("· The cathedral basement relay held through Bertha.")
	elif bool(_flags.get("w14_storm_soft_branch", false)):
		items.append("· Bertha turned east. The keel-keeper called it right.")
	for s in items:
		var lbl := Label.new()
		lbl.text = s
		lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		lbl.add_theme_font_size_override("font_size", 12)
		lbl.add_theme_color_override("font_color", Color(0.86, 0.86, 0.86, 1))
		col.add_child(lbl)
	var spacer := Control.new()
	spacer.custom_minimum_size = Vector2(0, 12)
	col.add_child(spacer)
	var coda := Label.new()
	coda.text = "The cathedral office is locked. The river is the river. The summer was the summer."
	coda.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	coda.add_theme_font_size_override("font_size", 12)
	coda.add_theme_color_override("font_color", Color(0.62, 0.78, 0.62, 1))
	col.add_child(coda)
	dlg.add_to_group("ui")  # F4 sweep catches modals
	add_child(dlg)
	dlg.popup_centered()


func _check_dean_interludes() -> void:
	if _dean.is_empty():
		return
	for seed in _dean.get("dean_interlude_seeds", []):
		var s_id: String = String(seed["id"])
		if _dean_interludes_earned.has(s_id):
			continue
		var cond: String = String(seed.get("earn_condition", ""))
		var earned: bool = false
		match cond:
			"observe_3_fingerprints":
				earned = _fingerprints_observed >= 3
			"see_tower_at_white_once":
				earned = _tower_state_revealed_white_once
			"summer_end_anomalies_observed_min_8":
				earned = (_day >= TURNS_TOTAL and _anomalies_observed >= 8)
		if earned:
			_dean_interludes_earned.append(s_id)
			_interlude_shelf.append(s_id)
			_log("[color=#c8a8ff][b]Dean interlude unlocked:[/b] %s[/color]" % String(seed["title"]))


# Pick a resolution flavor line from the template's pool. Prefers
# per-agent lines (resolution_flavor_success_by_agent[agent_id]) when
# they exist; falls back to the generic pool. Tokens in the picked
# string: {agent}, {region} — substituted at log time.
func _pick_resolution_flavor(template: Dictionary, key: String, agent_id: String) -> String:
	var rng := RandomNumberGenerator.new()
	rng.randomize()
	# Per-agent pool first.
	var by_agent_key: String = key + "_by_agent"
	var by_agent: Dictionary = template.get(by_agent_key, {})
	var lines: Array = []
	if by_agent.has(agent_id):
		lines = by_agent[agent_id]
	if lines.is_empty():
		lines = template.get(key, [])
	if lines.is_empty():
		return ""
	var line: String = String(lines[rng.randi() % lines.size()])
	var agent_name: String = String(_agents.get(agent_id, {}).get("name", agent_id))
	line = line.replace("{agent}", agent_name)
	return line


func _resolve_dispatch(d: Dictionary) -> void:
	var a_id: String = String(d["agent_id"])
	var r_id: String = String(d["region_id"])
	var pi: int = int(d["problem_index"])
	var st: Dictionary = _agent_state[a_id]
	var a: Dictionary = _agents[a_id]
	var probs: Array = _region_state[r_id]["active_problems"]
	if pi >= probs.size():
		_finish_dispatch_and_set_breather(a_id)
		return
	var p_ref: Dictionary = probs[pi]
	# Staged dispatches resolve deterministically — the choices the
	# player made through the stage modals already shaped the outcome.
	# Success vs failure keys off accumulated effort vs the
	# template's effort_to_resolve.
	if bool(d.get("is_staged", false)):
		var template_for_staged: Dictionary = _problem_templates.get(String(p_ref.get("template_id", "")), {})
		var target_effort: float = float(template_for_staged.get("effort_to_resolve", 3.0))
		var effort_accum: float = float(d.get("effort_accumulated", 0.0))
		if effort_accum >= target_effort * 0.95:
			_log("[color=#7cffb0]Day %d · [b]%s[/b] resolved [b]%s[/b] in %s.[/color]" %
				[_day, a["name"], p_ref["title"], _regions[r_id]["name"]])
			var sf: String = _pick_resolution_flavor(template_for_staged, "resolution_flavor_success", a_id)
			if sf != "":
				_log("[color=#86c896][i]%s[/i][/color]" % sf)
			probs.remove_at(pi)
			_problem_resolved_by_region[r_id] = int(_problem_resolved_by_region.get(r_id, 0)) + 1
			var template_id: String = String(p_ref.get("template_id", ""))
			if template_id != "":
				_problem_resolved_counts[template_id] = int(_problem_resolved_counts.get(template_id, 0)) + 1
		else:
			_log("[color=#c8a842]Day %d · [b]%s[/b] left [b]%s[/b] partly handled (effort %.1f/%.1f).[/color]" %
				[_day, a["name"], p_ref["title"], effort_accum, target_effort])
			p_ref["in_progress_by"] = ""
		_finish_dispatch_and_set_breather(a_id)
		return
	# Roll for success. Specialty doubles base chance; competence
	# scales linearly. Failure fires the agent's signature failure
	# (effects elided in this whitebox — just log).
	var specialty := bool((a.get("specialty_problem_types", []) as Array).has(p_ref["template_id"]))
	var base_chance: float = 0.55
	if specialty:
		base_chance += 0.25
	base_chance *= float(a.get("competence_modifier", 1.0))
	var rng := RandomNumberGenerator.new()
	rng.randomize()
	var roll: float = rng.randf()
	var template: Dictionary = _problem_templates.get(String(p_ref.get("template_id", "")), {})
	if roll < base_chance:
		_log("[color=#7cffb0]Day %d · [b]%s[/b] resolved [b]%s[/b] in %s.[/color]" %
			[_day, a["name"], p_ref["title"], _regions[r_id]["name"]])
		var sf: String = _pick_resolution_flavor(template, "resolution_flavor_success", a_id)
		if sf != "":
			_log("[color=#86c896][i]%s[/i][/color]" % sf)
		probs.remove_at(pi)
		if a["class"] == "demon":
			st["complexity"] = int(st["complexity"]) + 1
			# Corruption-tier spillover · a demon at hungry+ rolls a
			# chance to still fire its signature failure even on a
			# successful dispatch. Husk brings the body back with the
			# win; Steamboat's wake reaches Harmony Creek by morning.
			# This is the decision-friction moment · the player who
			# leans too hard on a demon starts paying the signature
			# in the middle of clean weeks.
			var s_tier: String = _demon_corruption_tier(int(st.get("corruption", 0)))
			var s_chance: float = _demon_tier_spillover_chance(s_tier)
			if s_chance > 0.0:
				var s_rng := RandomNumberGenerator.new()
				s_rng.randomize()
				if s_rng.randf() < s_chance:
					_log("[color=#c88070]…but %s came back [i]%s[/i]. %s[/color]" %
						[a["name"], s_tier.replace("_", " "), String(a.get("signature_failure", ""))])
					var s_ctx: Dictionary = {
						"region_id": r_id, "agent_id": a_id, "problem": p_ref,
					}
					_exec_effects(a.get("failure_effects", []), s_ctx)
		# Per-region success counter — drives several evolution
		# traits (policy_intuition needs 8 in HC; bayou_native
		# needs 3 in Graustark; coordinated_flock 4 in HC).
		var by_region: Dictionary = st.get("successful_dispatches_by_region", {})
		by_region[r_id] = int(by_region.get(r_id, 0)) + 1
		st["successful_dispatches_by_region"] = by_region
		# Small Wood returns without turning — cold_terrain_
		# resistance / controlled_husk earn predicates.
		if r_id == "small_wood" and a["class"] == "demon" and not bool(st.get("turned", false)):
			st["small_wood_returns_without_turning"] = int(st.get("small_wood_returns_without_turning", 0)) + 1
		_check_evolution_traits(a_id)
		# Per-template + per-region resolution counters for the
		# interlude earn predicates.
		var template_id: String = String(p_ref.get("template_id", ""))
		if template_id != "":
			_problem_resolved_counts[template_id] = int(_problem_resolved_counts.get(template_id, 0)) + 1
		_problem_resolved_by_region[r_id] = int(_problem_resolved_by_region.get(r_id, 0)) + 1
	else:
		_log("[color=#ff9090]Day %d · [b]%s[/b] failed at [b]%s[/b]. %s[/color]" %
			[_day, a["name"], p_ref["title"], String(a.get("signature_failure", ""))])
		var ff: String = _pick_resolution_flavor(template, "resolution_flavor_failure", a_id)
		if ff != "":
			_log("[color=#c89a8a][i]%s[/i][/color]" % ff)
		p_ref["in_progress_by"] = ""
		p_ref["severity"] = float(p_ref["severity"]) + 1.5
		if a["class"] == "demon":
			st["burn"] = int(st["burn"]) + 1
		# Run the agent's signature failure_effects with context.
		var fctx: Dictionary = {
			"region_id": r_id, "agent_id": a_id, "problem": p_ref,
		}
		_exec_effects(a.get("failure_effects", []), fctx)
	_finish_dispatch_and_set_breather(a_id)


# Mid-summer pressure curve. Multiplies tick_per_day and the
# weekly-spawn floor. W1-W3 stays at 1.0 (the onboarding cadence
# already exists in the spawn-count logic). W6 is the first
# noticeable bump · W13-W14 is the W14-storm window (peak) ·
# W18 onward eases as the Labor Day end-game approaches.
func _week_pressure_tier(week: int) -> float:
	if week <= 3:
		return 1.00
	elif week <= 5:
		return 1.15
	elif week == 6:
		return 1.30
	elif week <= 8:
		return 1.40
	elif week <= 10:
		return 1.55
	elif week <= 12:
		return 1.70
	elif week <= 14:
		return 1.85
	elif week == 15:
		return 1.65
	elif week <= 17:
		return 1.50
	else:
		return 1.35


func _tick_region_problems(r_id: String) -> void:
	# Substrate freeze (Dean's anomaly) suspends severity ticks in
	# this region until the freeze day expires.
	var st: Dictionary = _region_state[r_id]
	if int(st.get("substrate_freeze_until_day", 0)) >= _day:
		return
	# Restore dark nodes whose timer has run out.
	var dark: Array = st.get("dark_nodes", [])
	if not dark.is_empty():
		var still_dark: Array = []
		for entry in dark:
			if int(entry.get("until_day", 0)) <= _day:
				st["held_nodes"].append(entry["node"])
				_log("%s came back online in %s." % [entry["node"], _regions[r_id]["name"]])
			else:
				still_dark.append(entry)
		st["dark_nodes"] = still_dark
	var probs: Array = st["active_problems"]
	var week_now: int = int(ceil(float(_day) / 7.0))
	var pressure: float = _week_pressure_tier(week_now)
	for p in probs:
		if String(p.get("in_progress_by", "")) != "":
			continue  # in-progress problems don't tick
		var t: Dictionary = _problem_templates.get(p["template_id"], {})
		var tick: float = float(t.get("tick_per_day", 0.3)) * pressure
		var prev_sev: float = float(p["severity"])
		p["severity"] = prev_sev + tick
		# Fire any if_unresolved_at_severity_N effects whose threshold
		# was crossed this tick. Keys look like "if_unresolved_at_severity_5".
		# We track the highest threshold fired per-problem so each one
		# only triggers once.
		var last_fired: int = int(p.get("last_threshold_fired", 0))
		for key in t.keys():
			if not String(key).begins_with("if_unresolved_at_severity_"):
				continue
			var n: int = int(String(key).substr("if_unresolved_at_severity_".length()))
			if n <= last_fired:
				continue
			if p["severity"] >= float(n):
				_log("[color=#ff9090][b]%s[/b] crossed severity %d in %s.[/color]" %
					[p["title"], n, _regions[r_id]["name"]])
				var ctx: Dictionary = {"region_id": r_id, "problem": p, "problem_template": t["id"]}
				_exec_effects(t[key], ctx)
				p["last_threshold_fired"] = n


func _tick_region_escalation(r_id: String) -> void:
	# Per-day escalation accumulator. The weekly spawn pass on
	# Sunday reads escalation_progress + active problem load to
	# decide how many problems to spawn for this region (0-2).
	var r: Dictionary = _regions[r_id]
	var st: Dictionary = _region_state[r_id]
	var clock: float = float(r.get("escalation_clock_days", 6))
	st["escalation_progress"] = float(st["escalation_progress"]) + (1.0 / clock)


# Held nodes generate insight / cover / courier-capacity per day
# weighted by region role. The numbers are floats accumulated into
# the region's pool; display rounds. The starting_* values are
# floors; yields top them up over the summer (or drain as cover
# is spent — though spending isn't wired yet; see issue #2 fixes).
# Per spec §Graustark: "supply ... generates the insight and cover
# and courier capacity Frasier spends elsewhere."
func _tick_resource_yields() -> void:
	for r_id in _visible_regions:
		if not _regions.has(r_id) or not _region_state.has(r_id):
			continue
		var r: Dictionary = _regions[r_id]
		var st: Dictionary = _region_state[r_id]
		var yields: Dictionary = r.get("yields_per_held_node_per_day", {})
		if yields.is_empty():
			continue
		var n_held: int = (st.get("held_nodes", []) as Array).size()
		for k in yields.keys():
			st[k] = float(st.get(k, 0)) + float(yields[k]) * float(n_held)


# When the count of dispatches whose home_region != target_region
# exceeds a region's tolerance, that source region accrues extra
# escalation pressure per day. The spec's "strategic spine"
# (pushing Small Wood costs resources from the other two regions)
# lives here. The threshold is per-region: Graustark tolerates 2
# concurrent outbound; Harmony Creek tolerates 1; Small Wood 0.
func _tick_withdrawal_pressure() -> void:
	# Count concurrent outbound dispatches per home region.
	var outbound: Dictionary = {}
	for d in _active_dispatches:
		var a_id: String = String(d.get("agent_id", ""))
		if not _agents.has(a_id):
			continue
		var home: String = String(_agents[a_id].get("home_region", ""))
		var target: String = String(d.get("region_id", ""))
		if home == "" or target == "" or home == target:
			continue
		outbound[home] = int(outbound.get(home, 0)) + 1
	for r_id in outbound:
		if not _regions.has(r_id) or not _region_state.has(r_id):
			continue
		var r: Dictionary = _regions[r_id]
		var threshold: int = int(r.get("concurrent_outbound_dispatch_threshold", 999))
		var count: int = int(outbound[r_id])
		if count <= threshold:
			continue
		# Over threshold — apply penalty proportional to how many
		# excess withdrawals there are.
		var per_day: float = float(r.get("escalation_penalty_per_day_when_over_threshold", 0.10))
		var excess: int = count - threshold
		var st: Dictionary = _region_state[r_id]
		st["escalation_progress"] = float(st.get("escalation_progress", 0.0)) + per_day * float(excess)
		# Log once per day when penalty applies, but only on Sunday
		# to keep the chatter down.
		if _is_sunday(_day):
			_log("[color=#ff9090]Withdrawal pressure on %s: %d outbound (threshold %d). Sunday's spawn primes faster.[/color]" %
				[r["name"], count, threshold])


# Per spec: "the node they normally maintain runs without them
# while they're away." Each human currently on dispatch ticks a
# small-problem accrual on their home_node. After a threshold of
# days_away the home node spawns a problem in its region.
func _tick_active_markers() -> void:
	# Regional markers · consequence chains. Set by stage-choice effects
	# via `set_regional_marker`. Ticks daily; markers whose expires_on_day
	# has arrived are removed and their expiry_line is emitted to the log.
	if _active_regional_markers.is_empty():
		return
	var remaining: Array = []
	for mk in _active_regional_markers:
		var mk_d: Dictionary = mk
		if int(mk_d.get("expires_on_day", 0)) <= _day:
			var exp_line: String = String(mk_d.get("expiry_line", ""))
			if exp_line != "":
				_log(exp_line)
		else:
			remaining.append(mk_d)
	_active_regional_markers = remaining


func _tick_agent_home_rest() -> void:
	# Agent home-return breather. When an agent returns from a dispatch,
	# _resolve_dispatch sets `home_days_needed` based on how long they
	# were away and initializes `home_days_used` to 0. Each day the
	# agent is not on dispatch, home_days_used advances. When
	# home_days_used >= home_days_needed the agent is fully rested and
	# eligible to be dispatched again. The dispatch UI reads this state
	# to show "at rest N/M" and to disable/tag the agent-list button.
	for a_id in _agent_state:
		var st: Dictionary = _agent_state[a_id]
		if bool(st.get("on_dispatch", false)):
			continue
		var needed: int = int(st.get("home_days_needed", 0))
		if needed <= 0:
			continue
		var used: int = int(st.get("home_days_used", 0))
		if used >= needed:
			# Full rest — clear the counters so the agent is
			# indistinguishable from a fresh-start state.
			st["home_days_needed"] = 0
			st["home_days_used"] = 0
			continue
		st["home_days_used"] = used + 1


# Fires a one-shot day interlude the FIRST day the roster has 3+
# demons at hungry+ simultaneously. Records the count and the list;
# does not fire again while the flag is set. Once every one of those
# demons drops back to steady the flag clears so a second wave can
# fire the beat again later in the summer.
func _tick_roster_is_loud() -> void:
	var loud_ids: PackedStringArray = PackedStringArray()
	for a_id in _agent_state:
		var a: Dictionary = _agents.get(a_id, {})
		if String(a.get("class", "")) != "demon":
			continue
		var corr: int = int(_agent_state[a_id].get("corruption", 0))
		if _demon_corruption_tier(corr) != "steady":
			loud_ids.append(String(a.get("name", a_id)))
	if loud_ids.size() >= 3:
		if not bool(_flags.get("roster_is_loud_active", false)):
			_flags["roster_is_loud_active"] = true
			_log("[color=#c88070][b]The roster is loud.[/b]  %d demons carry corruption at once.  Names: %s.  Basement Sunday is not going to be enough this week.[/color]" %
				[loud_ids.size(), ", ".join(Array(loud_ids))])
			_log("[color=#c88070][i]Frasier posted a note on THE_BASEMENT at 4:14 AM.  Subject: 'more than two of you.'  Body: 'read the room · read the second rule · and then read the first one again.  F.'[/i][/color]")
	elif loud_ids.is_empty():
		_flags["roster_is_loud_active"] = false


# ── Demon corruption tiers ──────────────────────────────────────
# The corruption number is more legible as a NAMED tier · steady /
# hungry / restless / close_to_turning / turned. Each tier above
# steady rolls a spillover chance on every dispatch (even successful
# ones): if the roll hits, the demon's signature failure_effects
# fire alongside the win. This is where the "success comes with a
# cost" texture lives · Husk gets the job done but a body is left.
func _demon_corruption_tier(corruption: int) -> String:
	if corruption >= 9:
		return "turned"
	if corruption >= 7:
		return "close_to_turning"
	if corruption >= 5:
		return "restless"
	if corruption >= 3:
		return "hungry"
	return "steady"


func _demon_tier_spillover_chance(tier: String) -> float:
	match tier:
		"hungry":            return 0.15
		"restless":          return 0.30
		"close_to_turning":  return 0.50
		_:                   return 0.00


func _demon_tier_color(tier: String) -> Color:
	match tier:
		"hungry":            return Color(0.86, 0.86, 0.42, 1)
		"restless":          return Color(0.96, 0.62, 0.42, 1)
		"close_to_turning":  return Color(0.96, 0.42, 0.32, 1)
		"turned":            return Color(0.86, 0.20, 0.86, 1)
		_:                   return Color(0.62, 0.86, 0.62, 1)


# Per-demon in-voice line surfaced on tier crossings. Kept inline
# because these are short and only fire on crossing, not on every
# tick. Adds a shade of character on the moment the player sees
# the mechanical warning.
const _DEMON_VOICE_LINES: Dictionary = {
	"vagrant": {
		"hungry": "Vagrant sat too long at the picnic table.",
		"restless": "Vagrant went to a diner they've been to before and did not order water.",
		"close_to_turning": "Vagrant walked the same block three times before it was dark.",
	},
	"cicada": {
		"hungry": "Cicada made a sound they can't take back.",
		"restless": "Cicada surfaced under the parish road bridge and did not go back down.",
		"close_to_turning": "Cicada stopped counting seconds between the sound and the far echo.",
	},
	"moth": {
		"hungry": "Moth stayed at the porch light past the bulb warming up.",
		"restless": "Moth held the match a second longer than it needed the match held.",
		"close_to_turning": "Moth's shape lengthened at dusk and it did not shorten by full dark.",
	},
	"steamboat": {
		"hungry": "Steamboat's wake reached the drainage ditch three counties over.",
		"restless": "Steamboat took the low channel past the parish line and left a groove.",
		"close_to_turning": "Steamboat sounded once at 3 AM and something in Small Wood answered.",
	},
	"weir": {
		"hungry": "Weir felt the river's pull sideways for the first time all summer.",
		"restless": "Weir opened its hands underwater and did not close them.",
		"close_to_turning": "Weir stopped being the shape of the current and started being the current.",
	},
	"filly": {
		"hungry": "Filly took the long road twice.",
		"restless": "Filly's hands stopped remembering which pocket the second envelope was in.",
		"close_to_turning": "Filly said the wrong name at a diner she's been to sixty times.",
	},
	"starling": {
		"hungry": "Starling counted the phone lines and forgot the middle one.",
		"restless": "Starling scattered above the cul-de-sac at 6:47 PM and did not fully reassemble.",
		"close_to_turning": "Starling could not name the neighborhood watch chair for the first time all year.",
	},
	"husk": {
		"hungry": "Husk kept the coat on inside the safehouse.",
		"restless": "Husk drove the back roads at 2 AM without turning the headlights on.",
		"close_to_turning": "Husk closed a door twice as hard as the door needed closed.",
	},
}


# Demon-pair table. Key is two demon ids joined by "+" in
# alphabetical order. Value is {tone, log, cover, attention, region}
# — a small mechanical + flavor beat that fires when the second
# demon arrives in-region while the first is still on-dispatch.
# Tone drives log color. Cover/attention adjust the *region the
# pair is working in*; a negative cover value means the interaction
# is legibly loud.
const _DEMON_PAIR_INTERACTIONS: Dictionary = {
	"moth+steamboat": {
		"tone": "warm",
		"log": "Moth's light held over Steamboat's wake at the parish landing · the wake read as a fisherman's V and the light read as a bulb, and both readings were normal-parish.",
		"cover": 1,
	},
	"steamboat+weir": {
		"tone": "warm",
		"log": "Steamboat's channel and Weir's shape overlapped at the parish dock at 4 AM · Weir dampened the wake · the river stayed the river.",
		"cover": 2,
	},
	"filly+husk": {
		"tone": "warm",
		"log": "Filly carried the letter and Husk carried the road behind her. Neither of them looked back. The state line was quiet.",
		"cover": 1,
	},
	"moth+starling": {
		"tone": "loud",
		"log": "Moth held the porch-light and Starling read the wire above it · the reading and the holding did not match · the neighborhood watched them from three separate windows.",
		"cover": -1,
	},
	"cicada+starling": {
		"tone": "loud",
		"log": "Cicada's hum and Starling's line count arrived at pole 41 in the same three-minute window · the insulator-out registered as a signal · Mrs Salinas wrote it into her log.",
		"cover": -1,
	},
	"husk+steamboat": {
		"tone": "cold",
		"log": "Husk arrived at the parish dock while Steamboat's wake was still moving · the wake ended at the third plank · a jogger noticed but did not stop.",
	},
	"vagrant+cicada": {
		"tone": "warm",
		"log": "Vagrant walked past the parish-road bridge at 3:14 AM while Cicada was under it · neither one of them acknowledged · both routines held.",
		"cover": 1,
	},
	"filly+starling": {
		"tone": "warm",
		"log": "Filly carried and Starling counted · the two of them passed each other on the parish road and did not slow · the count matched the letter's weight to the ounce.",
	},
	"moth+weir": {
		"tone": "warm",
		"log": "Moth held the porch light over the dock while Weir sat under the third plank · the light on the wet cypress read as a fisherman's flashlight to Mrs Aucoin on her walk.",
		"cover": 1,
	},
	"cicada+moth": {
		"tone": "loud",
		"log": "Cicada hummed under the parish-road bridge and Moth held the sodium light above it · the hum registered on Mrs Salinas's baby monitor and she thought the transformer was cycling wrong.",
		"cover": -1,
	},
	"vagrant+starling": {
		"tone": "warm",
		"log": "Vagrant walked the phone-line route Starling had counted · pole 41's missing insulator read as a walking man's shadow twice from a mile away · the count adjusted.",
	},
	"husk+weir": {
		"tone": "cold",
		"log": "Husk stood at the parish dock at 3 AM while Weir was underneath · a boat's engine died at the far bend and its owner rowed back rather than call · Husk did not offer.",
	},
	"husk+moth": {
		"tone": "cold",
		"log": "Moth's porch light held while Husk was in the yard · the light stayed on the coat and did not touch the face · the neighbor's dog barked once and stopped.",
	},
	"filly+moth": {
		"tone": "warm",
		"log": "Moth held the light at the state line rest stop while Filly stopped for coffee · the second envelope moved from the second pocket to the third pocket and stayed there.",
		"cover": 1,
	},
	"vagrant+moth": {
		"tone": "warm",
		"log": "Vagrant took the same porch light Moth had been at the night before · Vagrant nodded at the light · the light was the light · nothing amplified.",
	},
	"cicada+vagrant": {
		"tone": "warm",
		"log": "Cicada under the bridge and Vagrant on the road above it · both routines rolled through their normal beats · the sixty-eight-degree canal water was the sixty-eight-degree canal water.",
	},
	"filly+weir": {
		"tone": "warm",
		"log": "Filly crossed the river on the parish ferry while Weir sat under the ferry's third support · the letter did not get wet · the water did not lift.",
		"cover": 1,
	},
	"cicada+filly": {
		"tone": "warm",
		"log": "Cicada under the bridge as Filly crossed it · a hum long enough to cover Filly's footsteps · nobody at the diner heard either the hum or the walking.",
		"cover": 1,
	},
	"husk+starling": {
		"tone": "cold",
		"log": "Starling counted the wires above Husk's parked car at the state-line rest stop · the count came out fifty-nine · fifty-nine is one under the number the count has been all summer.",
	},
	"cicada+steamboat": {
		"tone": "loud",
		"log": "Cicada under the parish-road bridge as Steamboat's wake ran the drainage ditch beneath it · the two sounds reinforced · a fisherman on the far bank looked up twice.",
		"cover": -1,
	},
}


# Read-only sibling of _maybe_fire_demon_pair: returns the pair
# entry (with partner_name filled in) that WOULD fire if this demon
# dispatched to this region right now, or {} if none. Used by the
# dispatch picker to show the consequence before commit.
func _preview_demon_pair(agent_id: String, region_id: String) -> Dictionary:
	var a: Dictionary = _agents.get(agent_id, {})
	if String(a.get("class", "")) != "demon":
		return {}
	for other_id in _agent_state:
		if String(other_id) == agent_id:
			continue
		var other_a: Dictionary = _agents.get(other_id, {})
		if String(other_a.get("class", "")) != "demon":
			continue
		var other_st: Dictionary = _agent_state[other_id]
		if not bool(other_st.get("on_dispatch", false)):
			continue
		var other_region: String = ""
		for r_id in _region_state:
			for p in _region_state[r_id].get("active_problems", []):
				if String((p as Dictionary).get("dispatch_agent_id", "")) == String(other_id):
					other_region = r_id
					break
			if other_region != "":
				break
		if other_region != region_id:
			continue
		var key1: String = agent_id + "+" + String(other_id)
		var key2: String = String(other_id) + "+" + agent_id
		var entry: Dictionary = _DEMON_PAIR_INTERACTIONS.get(key1,
			_DEMON_PAIR_INTERACTIONS.get(key2, {}))
		if entry.is_empty():
			continue
		var out: Dictionary = entry.duplicate()
		out["partner_name"] = String(other_a.get("name", other_id))
		return out
	return {}


func _maybe_fire_demon_pair(agent_id: String, region_id: String) -> void:
	var a: Dictionary = _agents.get(agent_id, {})
	if String(a.get("class", "")) != "demon":
		return
	# Look for any OTHER demon currently on-dispatch to this same
	# region. Fire the first pair-entry we find, so a single arrival
	# only ever triggers one interaction (deterministic against the
	# iteration order of _agent_state).
	for other_id in _agent_state:
		if String(other_id) == agent_id:
			continue
		var other_a: Dictionary = _agents.get(other_id, {})
		if String(other_a.get("class", "")) != "demon":
			continue
		var other_st: Dictionary = _agent_state[other_id]
		if not bool(other_st.get("on_dispatch", false)):
			continue
		# Match the other demon's current dispatch region by scanning
		# their active dispatch record if we can find it, else fall
		# back to home region. The engine doesn't store return-region
		# on the agent state, so we walk _region_state for the ref.
		var other_region: String = ""
		for r_id in _region_state:
			for p in _region_state[r_id].get("active_problems", []):
				if String((p as Dictionary).get("dispatch_agent_id", "")) == String(other_id):
					other_region = r_id
					break
			if other_region != "":
				break
		if other_region != region_id:
			continue
		var key1: String = agent_id + "+" + String(other_id)
		var key2: String = String(other_id) + "+" + agent_id
		var entry: Dictionary = _DEMON_PAIR_INTERACTIONS.get(key1,
			_DEMON_PAIR_INTERACTIONS.get(key2, {}))
		if entry.is_empty():
			continue
		var tone: String = String(entry.get("tone", "warm"))
		var color: String = "#86d0a8"
		if tone == "loud":
			color = "#c88070"
		elif tone == "cold":
			color = "#a8a8c0"
		_log("[color=%s][b]%s + %s:[/b] %s[/color]" %
			[color, String(a.get("name", agent_id)),
			 String(other_a.get("name", other_id)),
			 String(entry.get("log", ""))])
		var cover_delta: int = int(entry.get("cover", 0))
		if cover_delta != 0 and _region_state.has(region_id):
			var cur: int = int(_region_state[region_id].get("cover", 0))
			_region_state[region_id]["cover"] = max(0, cur + cover_delta)
		var attn: int = int(entry.get("attention", 0))
		if attn != 0 and _region_state.has(region_id):
			var cur2: int = int(_region_state[region_id].get("attention", 0))
			_region_state[region_id]["attention"] = max(0, cur2 + attn)
		return


# The distinct BBS handle each demon uses on THE_BASEMENT. Used
# in the rule-breaking beat when a demon violates Frasier's
# second rule and posts outside the basement.
const _DEMON_BBS_HANDLES: Dictionary = {
	"vagrant":   "the_vagrant",
	"cicada":    "17-year-hum",
	"moth":      "the_moth",
	"steamboat": "brown-water",
	"weir":      "sideways-current",
	"filly":     "long-road-twice",
	"starling":  "line-counter",
	"husk":      "coat-inside",
}


func _demon_bbs_handle(agent_id: String) -> String:
	return String(_DEMON_BBS_HANDLES.get(agent_id, agent_id))


func _demon_voice_line(agent_id: String, tier: String) -> String:
	var by_agent: Dictionary = _DEMON_VOICE_LINES.get(agent_id, {})
	return String(by_agent.get(tier, ""))


# Add corruption to a demon and log tier crossings. Crossing into
# hungry / restless / close_to_turning surfaces a warning line that
# makes the invisible economy legible · the player gets one clear
# beat to react before the next dispatch bakes in more spillover
# risk. Crossing INTO `turned` triggers the same lock-and-flip that
# the demon_corruption_event stage uses.
func _apply_corruption_to_demon(agent_id: String, amount: int) -> void:
	if amount <= 0 or not _agent_state.has(agent_id):
		return
	var st: Dictionary = _agent_state[agent_id]
	var a: Dictionary = _agents.get(agent_id, {})
	var prev: int = int(st.get("corruption", 0))
	var new_val: int = prev + amount
	st["corruption"] = new_val
	var prev_tier: String = _demon_corruption_tier(prev)
	var new_tier: String = _demon_corruption_tier(new_val)
	if prev_tier == new_tier:
		return
	var voice_line: String = _demon_voice_line(agent_id, new_tier)
	match new_tier:
		"hungry":
			_log("[color=#c8c862][b]%s crossed into hungry.[/b]  Corruption sits at %d · signature-spillover chance on dispatch: 15%%.[/color]" %
				[String(a.get("name", agent_id)), new_val])
			if voice_line != "":
				_log("[color=#c8c862][i]%s[/i][/color]" % voice_line)
		"restless":
			_log("[color=#c88070][b]%s crossed into restless.[/b]  Corruption %d · 30%% spillover · this is the last quiet tier before the turn is real.[/color]" %
				[String(a.get("name", agent_id)), new_val])
			if voice_line != "":
				_log("[color=#c88070][i]%s[/i][/color]" % voice_line)
		"close_to_turning":
			_log("[color=#c04050][b]%s is close to turning.[/b]  Corruption %d · 50%% spillover · one more dispatch in Small Wood without a rite and %s goes.[/color]" %
				[String(a.get("name", agent_id)), new_val, String(a.get("name", agent_id))])
			if voice_line != "":
				_log("[color=#c04050][i]%s[/i][/color]" % voice_line)
			# Rule-breaking beat: at close_to_turning, the demon
			# violates Frasier's second rule (do not answer another
			# one of you outside the basement). Log the leak; the
			# post is scrubbed by Frasier the same night, but the
			# room saw it. This is texture only · no BBS thread
			# state changes, but the log makes the pressure legible.
			var boards: Array = ["MAINSTREET", "THE_WORKSHOP", "THE_BAR", "THE_RECTORY"]
			var boards_rng := RandomNumberGenerator.new()
			boards_rng.randomize()
			var b_pick: String = String(boards[boards_rng.randi() % boards.size()])
			var handle: String = _demon_bbs_handle(agent_id)
			_log("[color=#a8a8c0][i]%s posted a reply on %s at %02d:%02d AM.  Frasier scrubbed it before 6.  The room saw it.[/i][/color]" %
				[handle, b_pick,
				 boards_rng.randi_range(2, 4),
				 boards_rng.randi_range(0, 59)])
		"turned":
			_log("[color=#c8a8ff][b]%s turned.[/b]  Corruption %d.  Locking · seeding turned_demon_active if Small Wood has the slot.[/color]" %
				[String(a.get("name", agent_id)), new_val])
			st["turned"] = true
			st["on_dispatch"] = true
			st["return_day"] = TURNS_TOTAL + 1
			if _region_state.has("small_wood"):
				_seed_problem("small_wood", "turned_demon_active")


func _demon_tier_glyph(tier: String) -> String:
	match tier:
		"hungry":            return "◐"
		"restless":          return "◑"
		"close_to_turning":  return "◕"
		"turned":            return "●"
		_:                   return "○"


func _finish_dispatch_and_set_breather(a_id: String) -> void:
	# Called at the tail of _resolve_dispatch (both staged + rolled).
	# Sets on_dispatch false and initializes the home-return breather
	# based on how long the agent was away. Formula: max(1, ceil(days
	# * 0.30)). A three-day dispatch → 1 rest day. A ten-day dispatch
	# → 3 rest days. Cap at 4 to keep even a stretched dispatch from
	# sidelining an agent for a full week.
	if not _agent_state.has(a_id):
		return
	var st: Dictionary = _agent_state[a_id]
	var days_away: int = int(st.get("days_away_since_dispatch", 0))
	var needed: int = clamp(int(ceil(float(days_away) * 0.30)), 1, 4)
	st["on_dispatch"] = false
	st["home_days_needed"] = needed
	st["home_days_used"] = 0


func _agent_is_resting(a_id: String) -> bool:
	if not _agent_state.has(a_id):
		return false
	var st: Dictionary = _agent_state[a_id]
	if bool(st.get("on_dispatch", false)):
		return false
	var needed: int = int(st.get("home_days_needed", 0))
	if needed <= 0:
		return false
	var used: int = int(st.get("home_days_used", 0))
	return used < needed


func _tick_time_at_home() -> void:
	for a_id in _agent_state:
		if not _agents.has(a_id):
			continue
		var a: Dictionary = _agents[a_id]
		if a.get("class", "") != "human":
			continue
		var st: Dictionary = _agent_state[a_id]
		if not bool(st.get("on_dispatch", false)):
			# Reset accrual when they're home.
			st["days_away_since_dispatch"] = 0
			continue
		st["days_away_since_dispatch"] = int(st.get("days_away_since_dispatch", 0)) + 1
		var cost_days: float = float(a.get("time_at_home_cost_days", 1.0))
		# When days_away exceeds cost_days * 2, accrue a small
		# problem at the human's home region. Trigger once per
		# dispatch; we set a flag so it doesn't re-fire on the
		# next day. The flag clears in _resolve_dispatch.
		if bool(st.get("home_node_strained_this_dispatch", false)):
			continue
		if float(st["days_away_since_dispatch"]) > cost_days * 2.0:
			st["home_node_strained_this_dispatch"] = true
			var home_region: String = String(a.get("home_region", ""))
			var strain_template: String = _strain_template_for_human(a_id)
			if _region_state.has(home_region) and strain_template != "":
				_seed_problem(home_region, strain_template)
				_log("[color=#ff9090]%s has been away %d days. %s without them.[/color]" %
					[String(a["name"]), int(st["days_away_since_dispatch"]),
					 String(_problem_templates.get(strain_template, {}).get("title", "The home node strains"))])


# Weekly region flavor. Fires on each Sunday boundary. Picks one
# event per visible region from regional_events.json's pool,
# filtered by available_from_week and never-repeat-if-already-fired.
# Each event has an optional effects[] array that routes through
# _exec_effect — the pool can grant +1 cover, unlock artifacts,
# etc. If no events remain in a region's pool (all fired), fall
# back to a small never-repeat evergreen line so the log still
# marks the week.
func _fire_weekly_region_flavor() -> void:
	var week: int = int(ceil(float(_day) / 7.0))
	var rng := RandomNumberGenerator.new()
	rng.randomize()
	for r_id in _visible_regions:
		var picked: Dictionary = _pick_regional_event(r_id, week, rng)
		if picked.is_empty():
			# Every event in this region's pool has fired. Emit a
			# minimal fallback so the week's log has a beat.
			_log("[color=#a8c0a8][i]%s:[/i] the region held its shape this week.[/color]" %
				_regions.get(r_id, {}).get("name", r_id))
			continue
		var event_id: String = String(picked.get("id", ""))
		_fired_regional_events.append(event_id)
		var line: String = String(picked.get("log_line", ""))
		if line != "":
			_log(line)
		# Apply effects (if any) through the existing interpreter.
		var effects: Array = picked.get("effects", [])
		if not effects.is_empty():
			var ctx: Dictionary = {"region_id": r_id, "source": "regional_event", "event_id": event_id}
			for eff: Dictionary in effects:
				_exec_effect(eff, ctx)


func _pick_regional_event(r_id: String, week: int, rng: RandomNumberGenerator) -> Dictionary:
	# Weighted-pick from _regional_events_pool, filtered by:
	#   · event.region == r_id
	#   · event.available_from_week <= week
	#   · event.id not in _fired_regional_events
	var pool: Array = []
	# Collect active-marker ids for this region for the blocked_by check.
	var active_markers_here: Dictionary = {}
	for mk in _active_regional_markers:
		var mk_d: Dictionary = mk
		if String(mk_d.get("region_id", "")) == r_id:
			active_markers_here[String(mk_d.get("marker_id", ""))] = true
	for e_var in _regional_events_pool:
		var e: Dictionary = e_var
		if String(e.get("region", "")) != r_id:
			continue
		if int(e.get("available_from_week", 1)) > week:
			continue
		if String(e.get("id", "")) in _fired_regional_events:
			continue
		# blocked_by_marker · if any listed marker is active in this
		# region, this event is filtered out.
		var blockers: Array = e.get("blocked_by_marker", [])
		var blocked: bool = false
		for b in blockers:
			if active_markers_here.has(String(b)):
				blocked = true
				break
		if blocked:
			continue
		# requires_marker · positive gate. Event fires ONLY if all
		# listed markers are currently active in the region.  Used
		# for follow-up flavor beats ("the relay held clean into
		# the next weekend") that only make sense while the player
		# is still inside the consequence-window from an earlier
		# stage choice.
		var required: Array = e.get("requires_marker", [])
		var missing: bool = false
		for req in required:
			if not active_markers_here.has(String(req)):
				missing = true
				break
		if missing:
			continue
		pool.append(e)
	if pool.is_empty():
		return {}
	var total: float = 0.0
	for e_var in pool:
		var e: Dictionary = e_var
		total += float(e.get("weight", 1.0))
	var pick: float = rng.randf() * total
	var running: float = 0.0
	for e_var in pool:
		var e: Dictionary = e_var
		running += float(e.get("weight", 1.0))
		if pick <= running:
			return e
	return pool[pool.size() - 1]


# W14 storm watch. Fires once on the Sunday of week 14. The hard
# branch (cathedral_basement_relay problem spawns, the line stays
# up only if the player handles it) is gated on the player having
# read at least 3 THE_BACKCHANNEL threads — inverts the usual
# reward, because the reward here is being trusted with the harder
# coordination work. The soft branch is a brief flavor log;
# everyone goes home dry.
func _fire_w14_storm_watch() -> void:
	_flags["w14_storm_watch_fired"] = true
	var backchannel_reads := 0
	for tid in _bbs_read_thread_ids:
		if String(tid).begins_with("TC_"):
			backchannel_reads += 1
	if backchannel_reads >= 3:
		_flags["w14_storm_hard_branch"] = true
		_log("[color=#ff9090][b]STORM WATCH · W14.[/b]  Bertha turned north of the keys. The cathedral basement is the inland relay this weekend.  STEEPLE on the bell-buoy.  WIRE_MOTHER on the panhandle line.  JF is on the boiler.  T. is at the storefront alone.  The line stays up if you keep it up.[/color]")
		if _region_state.has("graustark"):
			_seed_problem("graustark", "cathedral_basement_relay")
	else:
		_flags["w14_storm_soft_branch"] = true
		_log("[color=#a8c0a8][b]STORM WATCH · W14.[/b]  The system south of the keys turned east.  The bell-buoy in Mobile held its winter rope.  The keel-keeper called it right.  The inland circle gets a quiet weekend.[/color]")


# Daily vignettes: small flavor beats from daily_vignettes.json that
# give each non-Sunday day a piece of texture between dispatch
# decisions. Per-day fire pulls a weighted-random eligible vignette
# (region visible + day in [day_min, day_max] + not a fired one-shot
# + not the same as the most recent). Author note: shipped to fix
# the "first 14 days feel light, click-and-proceed" playtest.
func _fire_daily_vignette() -> void:
	# Sunday already gets the weekly region flavor + BBS night; skip
	# the vignette so Sunday doesn't get noisy.
	if _is_sunday(_day):
		return
	var pool: Array = _vignettes_def.get("vignettes", [])
	if pool.is_empty():
		return
	var eligible: Array = []
	for v in pool:
		var vd: Dictionary = v as Dictionary
		var vid: String = String(vd.get("id", ""))
		if vid == "":
			continue
		if vid == _last_vignette_id:
			continue
		if bool(vd.get("one_shot", false)) and _vignettes_fired.has(vid):
			continue
		var d_min: int = int(vd.get("day_min", 1))
		var d_max: int = int(vd.get("day_max", 999))
		if _day < d_min or _day > d_max:
			continue
		var tag: String = String(vd.get("tag", "any"))
		if tag != "any" and not _visible_regions.has(tag):
			continue
		eligible.append(vd)
	if eligible.is_empty():
		return
	var rng := RandomNumberGenerator.new()
	rng.randomize()
	var pick: Dictionary = eligible[rng.randi() % eligible.size()]
	var pick_id: String = String(pick["id"])
	_last_vignette_id = pick_id
	if bool(pick.get("one_shot", false)) and not _vignettes_fired.has(pick_id):
		_vignettes_fired.append(pick_id)
	_log("[color=#86c896][i]%s[/i][/color]" % String(pick.get("body", "")))


# Queued burns: DM choices and other deferred decisions schedule
# burns to land on a future day. When the day rolls around, fire
# the burn (a flavored log entry + a strain bump on Graustark) and
# remove it from the queue. The reason text doubles as the log line.
func _tick_queued_burns() -> void:
	var remaining: Array = []
	for entry in _queued_burns:
		var ed: Dictionary = entry as Dictionary
		var trigger: int = int(ed.get("trigger_day", 0))
		if trigger > _day:
			remaining.append(ed)
			continue
		var reason: String = String(ed.get("reason", "the bill came due"))
		_log("[color=#c89a42][b]burn lands:[/b] %s[/color]" % reason)
		# A queued burn nudges the day's contested cycle in Graustark
		# by a small amount; soft mechanical bite, not a problem
		# spawn (the player already made the choice; we don't double-
		# punish).
		if _region_state.has("graustark"):
			var st: Dictionary = _region_state["graustark"]
			st["escalation_progress"] = float(st.get("escalation_progress", 0.0)) + 0.5
	_queued_burns = remaining


# Choose a problem template appropriate to the kind of strain
# this particular human's absence would produce at home. Per
# spec: "Philip alone with the basil pot dying" (Mackenzie),
# "the surviving son's Friday dinner crew without him on the
# floor" (the_surviving_son), etc.
func _strain_template_for_human(agent_id: String) -> String:
	match agent_id:
		"mackenzie":             return "model_home_feel"
		"the_surviving_son":     return "family_succession"
		"john_frank":            return "diner_threshold"
		"elicia":                return "cathedral_visitor"
		"nicola":                return "memorial_grief"
		"the_small_wood_contact_jules": return "seed_dying"
	return "lease_and_licensing"


# Sunday-night weekly spawn pass. Per spec: "Problems spawn weekly,
# on Sunday nights, before the BBS opens. Each region generates
# 1-3 problems depending on how exposed it currently is."
#
# Exposure model (white-box, tune-by-feel):
#   · 0 problems active in the region  → roll 1-2 new
#   · 1-2 problems active              → roll 1 new
#   · 3+ problems active                → 0 new (region is saturated)
#   · cap absolute at MAX_PROBLEMS_PER_REGION
#   · dedupe: skip any template already active in the region
# Phase 2 sprint 1: open the BBS overlay on Sunday night.
# Instantiates the BBS scene as a child Control, calls open()
# with the current week + readmission flag, awaits hung_up, then
# merges the session state into the persistent BBS state and
# returns control to _on_advance_day.
func _open_bbs_night() -> void:
	var ps: PackedScene = load("res://scenes/games/CommunityPlannedBBS.tscn") as PackedScene
	if ps == null:
		push_warning("[CommunityPlanned] could not load BBS scene; skipping BBS night")
		return
	var overlay := ps.instantiate()
	add_child(overlay)
	# Switch BGM to the night-modem track for the duration of the
	# overlay. The strategic-day BGM resumes after hung_up (see below).
	_audio_play_bgm_track("res://assets/audio/bgm/vol5_cicadas_dusk.ogg")
	var week: int = int(ceil(float(_day) / 7.0))
	# Glossary unlock fires once the player has read >= 6 SNACKS
	# bleached-counter threads and reached the unlock week.
	var snacks_read := 0
	for tid in _bbs_read_thread_ids:
		if String(tid).begins_with("SN_"):
			snacks_read += 1
	var glossary_unlocked: bool = (week >= 11 and snacks_read >= 6)
	overlay.open(week, _readmitted_to_snacks, _dm_read_to_week.duplicate(),
		_bbs_discovered_hidden_boards.duplicate(), _unlocked_artifacts.duplicate(),
		glossary_unlocked, _canon_vars.duplicate())
	var session: Dictionary = await overlay.hung_up
	overlay.queue_free()
	# Merge BBS-night session state into the persistent layer.
	for bbs_id in session.get("visited_bbs_ids", []):
		var s: String = String(bbs_id)
		if not _bbs_visited_ids.has(s):
			_bbs_visited_ids.append(s)
	for tid in session.get("read_thread_ids", []):
		var t: String = String(tid)
		if not _bbs_read_thread_ids.has(t):
			_bbs_read_thread_ids.append(t)
	for num in session.get("dialled_numbers", []):
		var n: String = String(num)
		if not _bbs_dialled_numbers.has(n):
			_bbs_dialled_numbers.append(n)
	# DM read pointers: the overlay's copy is authoritative for any
	# canonical it touched this session; merge in (take max per key).
	var session_dm_read: Dictionary = session.get("dm_read_to_week", {})
	for canonical in session_dm_read.keys():
		var new_w: int = int(session_dm_read[canonical])
		var old_w: int = int(_dm_read_to_week.get(canonical, 0))
		if new_w > old_w:
			_dm_read_to_week[canonical] = new_w
	# DM replies: append to the log and execute their effects against
	# the strategic engine. ctx defaults to graustark since DMs are
	# personal to Frasier; effect kinds that take an explicit region
	# can override.
	var ctx: Dictionary = {"region_id": "graustark"}
	for reply in session.get("dm_replies", []):
		_dm_reply_log.append(reply)
		var label: String = String(reply.get("label", ""))
		var canonical: String = String(reply.get("canonical", ""))
		_log("[color=#86d0a8]DM reply to %s: %s[/color]" % [canonical, label])
		for eff in reply.get("effects", []):
			if typeof(eff) == TYPE_DICTIONARY:
				_exec_effect(eff, ctx)
	# Apply hidden-board strategic effects (cover cost, demon burn
	# reduction, grove intel). Routed through the same interpreter
	# so they participate in the same per-region context.
	for ef in session.get("strategic_effects", []):
		if typeof(ef) == TYPE_DICTIONARY:
			_exec_effect(ef, ctx)
	# Merge hidden-board discoveries.
	var session_hidden: Dictionary = session.get("discovered_hidden_boards", {})
	for hb_id in session_hidden.keys():
		if bool(session_hidden[hb_id]):
			_bbs_discovered_hidden_boards[hb_id] = true
	for hb_id in session.get("newly_discovered_hidden_boards", []):
		_log("[color=#e0c862][b]hidden board unlocked:[/b] %s[/color]" % String(hb_id))
	# Merge new artifact unlocks; emit shelf log entries.
	for unlock in session.get("new_artifact_unlocks", []):
		var aid: String = String((unlock as Dictionary).get("artifact_id", ""))
		if aid == "" or _unlocked_artifacts.has(aid):
			continue
		_unlocked_artifacts.append(aid)
		_log("[color=#e0c862][b]artifact:[/b] %s[/color]  [color=#c8a842](%s · from %s)[/color]" % [
			aid,
			String((unlock as Dictionary).get("kind", "")),
			String((unlock as Dictionary).get("source_thread_id", ""))])
	_log("[color=#a8c0a8]NO CARRIER. Off the modem. %d threads read across the summer; %d BBSes dialled.[/color]" %
		[_bbs_read_thread_ids.size(), _bbs_visited_ids.size()])


func _run_weekly_spawn() -> void:
	for r_id in _visible_regions:
		if not _regions.has(r_id):
			continue
		_spawn_weekly_problems_for_region(r_id)
	# Reset all escalation accumulators after the weekly pass.
	for r_id in _region_state:
		_region_state[r_id]["escalation_progress"] = 0.0
	# Resume strategic-day BGM after Sunday BBS night. Safe to call
	# every week — if the BGM's already this track, it's a no-op.
	_audio_play_bgm_for_current_state()
	# Surface pressure-tier transitions to the player log so the
	# curve is legible. Fires once on entry to each tier.
	var week: int = int(ceil(float(_day) / 7.0))
	var prev_tier: float = _week_pressure_tier(week - 1)
	var curr_tier: float = _week_pressure_tier(week)
	if curr_tier > prev_tier:
		if curr_tier >= 1.80:
			_log("[color=#ff9090][b]Storm window.[/b] W13-W14 is the gulf-coast peak. Tick rates and weekly spawns are at their hardest.[/color]")
		elif curr_tier >= 1.55:
			_log("[color=#ffb86b][b]Mid-summer crest.[/b] The region feels heavier this week. Problems tick faster; Sundays spawn more.[/color]")
		elif curr_tier >= 1.30:
			_log("[color=#ffd86b][b]First mid-summer bump.[/b] The pace is picking up.[/color]")
	elif curr_tier < prev_tier:
		if curr_tier < 1.50 and prev_tier >= 1.80:
			_log("[color=#a8c0a8][b]Storm passed.[/b] Pressure easing back · the gulf-coast circle is regrouping.[/color]")
		elif curr_tier <= 1.40:
			_log("[color=#a8c0a8][b]Labor Day approach.[/b] The summer's hardest weeks are behind you.[/color]")


func _spawn_weekly_problems_for_region(r_id: String) -> void:
	var r: Dictionary = _regions[r_id]
	var st: Dictionary = _region_state[r_id]
	var active: Array = st.get("active_problems", [])
	var room: int = MAX_PROBLEMS_PER_REGION - active.size()
	if room <= 0:
		return
	# Exposure: how many new ones do we want this week? Early-game
	# is cranked — playtest feedback said W1-W2 felt empty. Through
	# week 3 the room wants 3-4 active problems at minimum; mid-summer
	# (W6+) layers a pressure tier on top of the base cadence so the
	# player feels real escalation; W13-W14 is the storm-window peak;
	# W18+ eases for the Labor Day approach.
	var week: int = int(ceil(float(_day) / 7.0))
	var wanted: int
	if week <= 3:
		wanted = max(0, 4 - active.size())
	elif active.size() == 0:
		wanted = 2
	elif active.size() <= 2:
		wanted = 1
	else:
		wanted = 0
	# Mid-summer pressure floor: extra spawns layered on top of the
	# base cadence. The pressure tier scales the floor smoothly.
	var pressure: float = _week_pressure_tier(week)
	if pressure >= 1.80:
		wanted += 2          # W13-W14 storm-window crush
	elif pressure >= 1.55:
		wanted += 1          # W9-W12 mid-summer crest
	elif pressure >= 1.30:
		# W6-W8 first bump: ensure at least 1 spawn if room
		wanted = max(wanted, 1)
	wanted = min(wanted, room)
	if wanted <= 0:
		return
	# Active templates already in the region — dedupe target set.
	var active_template_ids: Dictionary = {}
	for p in active:
		active_template_ids[String(p.get("template_id", ""))] = true
	# Build the spawnable pool: templates whose problem_type is in
	# the region's palette AND eligible to this region AND in the
	# reveal-unlocked set AND not already on the board AND not
	# spawn_only_by-gated.
	var weights: Dictionary = r.get("problem_palette_weights", {})
	if weights.is_empty():
		return
	var pool: Array = []   # list of (template_id, weight)
	for t_id in _problem_templates:
		if active_template_ids.has(t_id):
			continue
		var t: Dictionary = _problem_templates[t_id]
		var t_type: String = String(t.get("problem_type", ""))
		if not weights.has(t_type):
			continue
		if not _eligible_problem_types.has(t_type):
			continue
		if not (t.get("regions_eligible", []) as Array).has(r_id):
			continue
		if String(t.get("spawn_only_by", "")) != "":
			continue
		pool.append([t_id, float(weights[t_type])])
	if pool.is_empty():
		return
	# Weighted-pick `wanted` distinct templates.
	var rng := RandomNumberGenerator.new()
	rng.randomize()
	var spawned: int = 0
	while spawned < wanted and not pool.is_empty():
		var total: float = 0.0
		for p_entry in pool:
			total += float(p_entry[1])
		var pick: float = rng.randf() * total
		var running: float = 0.0
		var chosen_idx: int = -1
		for i in range(pool.size()):
			running += float(pool[i][1])
			if pick <= running:
				chosen_idx = i
				break
		if chosen_idx < 0:
			break
		var chosen_id: String = String(pool[chosen_idx][0])
		_seed_problem(r_id, chosen_id)
		var t_chosen: Dictionary = _problem_templates[chosen_id]
		_log("Sunday · [b]%s[/b] in %s." % [t_chosen["title"], r["name"]])
		pool.remove_at(chosen_idx)
		spawned += 1


# ── Audio ────────────────────────────────────────────────────────
# CP is otherwise silent. These two helpers wire ambient BGM to the
# strategic-day / BBS-night beat via the AudioMgr autoload.

const _CP_BGM_STRATEGIC := "res://assets/audio/bgm/vol5_ambient.ogg"
const _CP_BGM_BBS_NIGHT := "res://assets/audio/bgm/vol5_cicadas_dusk.ogg"
const _CP_BGM_STORM     := "res://assets/audio/bgm/vol5_warehouse_drone.ogg"


func _audio_play_bgm_track(path: String) -> void:
	if path == "" or Engine.get_main_loop() == null:
		return
	var mgr: Node = get_node_or_null("/root/AudioMgr")
	if mgr == null:
		return
	if mgr.has_method("play_bgm"):
		mgr.call("play_bgm", path)


func _audio_play_bgm_for_current_state() -> void:
	# Route BGM by current pressure tier · storm window gets the
	# warehouse-drone track for the W13-W14 crush; everything else
	# gets the standard strategic-day ambient. BBS-night is handled
	# separately by _open_bbs_night's explicit call.
	var week: int = int(ceil(float(_day) / 7.0))
	var pressure: float = _week_pressure_tier(week)
	if pressure >= 1.80:
		_audio_play_bgm_track(_CP_BGM_STORM)
	else:
		_audio_play_bgm_track(_CP_BGM_STRATEGIC)


# ── Logging ──────────────────────────────────────────────────────
func _log(line: String) -> void:
	_log_lines.append(line)
	if _log_lines.size() > 200:
		_log_lines = _log_lines.slice(_log_lines.size() - 200, _log_lines.size())
