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
const SAVE_PATH := "user://saves/community_planned_slot_0.json"
const SAVE_VERSION := 1
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
var _interlude_meta: Dictionary = {}      # per-interlude metadata (day earned, ...)
# Accumulators read by interlude earn predicates. Bumped on
# resolution / dispatch / day-tick.
var _problem_resolved_counts: Dictionary = {}    # template_id → count
var _problem_resolved_by_region: Dictionary = {} # region_id → count
var _agent_dispatch_counts: Dictionary = {}      # agent_id → int
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


func _ready() -> void:
	_load_data()
	_build_ui()
	if _try_load_save():
		_log("[color=#a8c0a8]Loaded summer in progress — day %d.[/color]" % _day)
	else:
		_init_state()
		_log("Day %d · Memorial Day. The summer begins." % _day)
	_render()


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


func _write_save() -> void:
	DirAccess.make_dir_recursive_absolute("user://saves")
	var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f == null:
		push_error("[CommunityPlanned] could not write save to %s" % SAVE_PATH)
		return
	f.store_string(JSON.stringify(_collect_state(), "  "))
	if _save_status_label != null:
		_save_status_label.text = "save: day %d (autosaved)" % _day


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
	# Version check (future migrations land here).
	if int(d.get("save_version", 0)) != SAVE_VERSION:
		push_warning("[CommunityPlanned] save_version mismatch — discarding")
		return false
	_apply_state(d)
	return true


func _wipe_save_and_restart() -> void:
	if FileAccess.file_exists(SAVE_PATH):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(SAVE_PATH))
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
	var color := {
		"dim":     Color(0.42, 0.42, 0.50, 1),
		"warming": Color(0.62, 0.52, 0.42, 1),
		"bright":  Color(0.92, 0.78, 0.42, 1),
		"white":   Color(0.96, 0.96, 0.88, 1),
	}.get(_tower_brightness, Color(0.62, 0.62, 0.62, 1))
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
		var lbl := Label.new()
		var sev_dots := ""
		var sev_int: int = int(round(p["severity"]))
		for i in range(min(sev_int, 9)):
			sev_dots += "●"
		lbl.text = "%s  %s  (effort %.1f)" % [p["title"], sev_dots, p["effort_remaining"]]
		lbl.add_theme_font_size_override("font_size", 10)
		lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
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
			var r_id_capture := r_id
			var pi_capture := pi
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
		# button styled to read like a label until hover.
		var btn := Button.new()
		btn.text = "[%s]  %s%s%s" % [
			"D" if a["class"] == "demon" else "H",
			a["name"], econ, status]
		btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		btn.flat = true
		btn.focus_mode = Control.FOCUS_NONE
		btn.add_theme_font_size_override("font_size", 10)
		var ag_capture := a_id
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
	else:
		status_text = "available"
	status_label.text = "STATUS  ·  %s" % status_text
	status_label.add_theme_font_size_override("font_size", 10)
	status_label.add_theme_color_override("font_color", Color(0.86, 0.86, 0.62, 1))
	col.add_child(status_label)

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
	# Corruption (gated)
	if bool(_ui_flags.get("show_corruption_values", false)):
		var corr_lbl := Label.new()
		corr_lbl.text = "corruption  %d  ·  resistance: %s" % [
			int(st.get("corruption", 0)),
			String(a.get("corruption_resistance", "—"))]
		corr_lbl.add_theme_font_size_override("font_size", 10)
		corr_lbl.add_theme_color_override("font_color", Color(0.96, 0.62, 0.42, 1))
		col.add_child(corr_lbl)
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


func _dossier_rule() -> Control:
	var hr := ColorRect.new()
	hr.color = Color(0.32, 0.32, 0.32, 0.6)
	hr.custom_minimum_size = Vector2(0, 1)
	return hr


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
		var btn := Button.new()
		btn.text = "send %s" % String(a["name"])
		btn.focus_mode = Control.FOCUS_NONE
		var ag_capture := a_id
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
	# Open a simple modal listing eligible agents.
	var dlg := AcceptDialog.new()
	dlg.title = "Dispatch — %s" % p["title"]
	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 4)
	dlg.add_child(vbox)
	var hint := Label.new()
	hint.text = "Choose an agent for %s (%s)." % [p["title"], _regions[region_id]["name"]]
	hint.add_theme_color_override("font_color", Color(0.86, 0.86, 0.86, 1))
	vbox.add_child(hint)
	var any_eligible := false
	# Only consider agents the reveal schedule has surfaced — the
	# dispatch picker reads the same roster the dossier panel does.
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
		var btn := Button.new()
		var specialty := bool((a.get("specialty_problem_types", []) as Array).has(p["template_id"]))
		var indicator := " (★ specialty)" if specialty else ""
		btn.text = "%s%s" % [a["name"], indicator]
		btn.focus_mode = Control.FOCUS_NONE
		var ag_capture := a_id
		btn.pressed.connect(func() -> void:
			_dispatch_agent(ag_capture, region_id, problem_index)
			dlg.hide()
			dlg.queue_free())
		vbox.add_child(btn)
		any_eligible = true
	if not any_eligible:
		var none := Label.new()
		none.text = "No agents available."
		vbox.add_child(none)
	add_child(dlg)
	dlg.popup_centered()


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
	# Cross-region cost: if agent's home_region != target, +50%.
	if String(a.get("home_region", "")) != region_id:
		days = int(ceil(float(days) * 1.5))
	if region_id == "small_wood" and String(a.get("home_region", "")) != "small_wood":
		days = int(ceil(float(days) * 1.5))
	st["on_dispatch"] = true
	st["return_day"] = _day + days
	if a["class"] == "demon":
		st["burn"] = int(st["burn"]) + int(a.get("burn_per_dispatch", 1))
		if region_id == "small_wood":
			# Corruption accrues per day in small wood.
			var per_day: float = float(r.get("demon_corruption_per_day_in_region", 0.0))
			st["corruption"] = int(st["corruption"]) + int(ceil(per_day * float(days)))
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
	_active_dispatches.append({
		"agent_id": agent_id,
		"region_id": region_id,
		"problem_index": problem_index,
		"return_day": _day + days,
		"competence_modifier": float(a.get("competence_modifier", 1.0)),
	})
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
	# Tick problems + accumulate per-region escalation. The actual
	# weekly spawn pass fires only on Sunday nights (day 7, 14, 21,
	# ...) per spec §Problems.
	for r_id in _region_state:
		_tick_region_problems(r_id)
		_tick_region_escalation(r_id)
	if _is_sunday(_day):
		_log("[i]Sunday night. The week ends.[/i]")
		_run_weekly_spawn()
	# Dean's tower: re-roll brightness on the cadence; fire anomalies
	# when bright/white.
	_tick_dean_tower()
	# Check Dean interlude unlock conditions.
	_check_dean_interludes()
	# Check the (non-Dean) interlude shelf earn conditions.
	_check_interlude_earnings()
	# Win/loss check.
	if _day >= TURNS_TOTAL:
		_log("[b]Labor Day arrived.[/b] The summer's end. Interlude shelf: %d items (incl. %d from Dean)." %
			[_interlude_shelf.size(), _dean_interludes_earned.size()])
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
			if not probs.is_empty():
				var idx: int = rng.randi() % probs.size()
				var p: Dictionary = probs[idx]
				_log("[color=#a8a8c0][b]%s[/b] [i]%s[/i][/color]" % [String(a["title"]), log_str])
				probs.remove_at(idx)
		"wipe_corruption_on_demon_in_small_wood":
			var amount: int = int(eff.get("amount", 4))
			for ag_id in _agent_state:
				if String(_agents[ag_id].get("class", "")) != "demon":
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
	                "summer_milestone_interludes", "cross_cutting_interludes"]:
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
	                "summer_milestone_interludes", "cross_cutting_interludes"]:
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
			title.add_theme_color_override("font_color", title_color)
			col.add_child(title)
			var body := Label.new()
			body.text = String(entry["flavor"])
			body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			body.add_theme_font_size_override("font_size", 11)
			body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			col.add_child(body)
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


func _resolve_dispatch(d: Dictionary) -> void:
	var a_id: String = String(d["agent_id"])
	var r_id: String = String(d["region_id"])
	var pi: int = int(d["problem_index"])
	var st: Dictionary = _agent_state[a_id]
	var a: Dictionary = _agents[a_id]
	var probs: Array = _region_state[r_id]["active_problems"]
	if pi >= probs.size():
		st["on_dispatch"] = false
		return
	var p_ref: Dictionary = probs[pi]
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
	if roll < base_chance:
		_log("[color=#7cffb0]Day %d · [b]%s[/b] resolved [b]%s[/b] in %s.[/color]" %
			[_day, a["name"], p_ref["title"], _regions[r_id]["name"]])
		probs.remove_at(pi)
		if a["class"] == "demon":
			st["complexity"] = int(st["complexity"]) + 1
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
		p_ref["in_progress_by"] = ""
		p_ref["severity"] = float(p_ref["severity"]) + 1.5
		if a["class"] == "demon":
			st["burn"] = int(st["burn"]) + 1
		# Run the agent's signature failure_effects with context.
		var fctx: Dictionary = {
			"region_id": r_id, "agent_id": a_id, "problem": p_ref,
		}
		_exec_effects(a.get("failure_effects", []), fctx)
	st["on_dispatch"] = false


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
	for p in probs:
		if String(p.get("in_progress_by", "")) != "":
			continue  # in-progress problems don't tick
		var t: Dictionary = _problem_templates.get(p["template_id"], {})
		var tick: float = float(t.get("tick_per_day", 0.3))
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
func _run_weekly_spawn() -> void:
	for r_id in _visible_regions:
		if not _regions.has(r_id):
			continue
		_spawn_weekly_problems_for_region(r_id)
	# Reset all escalation accumulators after the weekly pass.
	for r_id in _region_state:
		_region_state[r_id]["escalation_progress"] = 0.0


func _spawn_weekly_problems_for_region(r_id: String) -> void:
	var r: Dictionary = _regions[r_id]
	var st: Dictionary = _region_state[r_id]
	var active: Array = st.get("active_problems", [])
	var room: int = MAX_PROBLEMS_PER_REGION - active.size()
	if room <= 0:
		return
	# Exposure: how many new ones do we want this week?
	var wanted: int
	if active.size() == 0:
		wanted = 2
	elif active.size() <= 2:
		wanted = 1
	else:
		wanted = 0
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


# ── Logging ──────────────────────────────────────────────────────
func _log(line: String) -> void:
	_log_lines.append(line)
	if _log_lines.size() > 200:
		_log_lines = _log_lines.slice(_log_lines.size() - 200, _log_lines.size())
