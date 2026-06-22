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
const TURNS_TOTAL := 100
const MAX_DISPATCHES_PER_DAY := 3

var _regions: Dictionary = {}    # id → region def
var _agents: Dictionary = {}     # id → agent def
var _problem_templates: Dictionary = {}  # id → template def

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


func _ready() -> void:
	_load_data()
	_init_state()
	_build_ui()
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
	# Seed one starter problem per region so the player has something
	# to look at on day 1.
	_seed_problem("graustark", "memorial_grief")
	_seed_problem("harmony_creek", "surveillance")
	_seed_problem("small_wood", "seed_dying")


func _seed_problem(region_id: String, template_id: String) -> void:
	var t: Dictionary = _problem_templates.get(template_id, {})
	if t.is_empty():
		return
	var st: Dictionary = _region_state[region_id]
	st["active_problems"].append({
		"template_id": template_id,
		"title": t["title"],
		"severity": float(t.get("base_severity", 1)),
		"effort_remaining": float(t.get("effort_to_resolve", 2)),
		"in_progress_by": "",
		"day_spawned": _day,
	})


# ── UI build ─────────────────────────────────────────────────────
func _build_ui() -> void:
	# Three region panels in the regions row.
	for r_id in ["graustark", "harmony_creek", "small_wood"]:
		var panel := _make_region_panel(r_id)
		_region_panels_box.add_child(panel)
	_advance_button.pressed.connect(_on_advance_day)


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
	_day_label.text = "DAY %d / %d" % [_day, TURNS_TOTAL]
	_dispatches_label.text = "Dispatches today: %d / %d" % [_dispatches_this_day, MAX_DISPATCHES_PER_DAY]
	for r_id in ["graustark", "harmony_creek", "small_wood"]:
		_render_region(r_id)
	_render_agent_list()
	_render_log()


func _render_region(r_id: String) -> void:
	var panel: Node = _region_panels_box.get_node("Region_" + r_id)
	var st: Dictionary = _region_state[r_id]
	var stats_label: Label = panel.get_node("Col/Stats") as Label
	stats_label.text = "insight %d  ·  cover %d  ·  courier %d  ·  esc %.0f%%" % [
		st["insight"], st["cover"], st["courier_capacity"],
		clamp(st["escalation_progress"] * 100.0, 0.0, 100.0)
	]
	var nodes_label: Label = panel.get_node("Col/Nodes") as Label
	var held: Array = st["held_nodes"]
	var contested: Array = st["contested_nodes"]
	var targets: Array = st["target_nodes"]
	var parts: PackedStringArray = PackedStringArray()
	parts.append("HELD: " + (", ".join(held) if not held.is_empty() else "—"))
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
	var ids: Array = _agents.keys()
	ids.sort_custom(func(a, b):
		var ac: String = String(_agents[a].get("class", ""))
		var bc: String = String(_agents[b].get("class", ""))
		if ac != bc: return ac < bc
		return String(_agents[a]["name"]) < String(_agents[b]["name"]))
	for a_id in ids:
		var a: Dictionary = _agents[a_id]
		var st: Dictionary = _agent_state[a_id]
		var lbl := Label.new()
		var status := ""
		if bool(st["on_dispatch"]):
			status = "  · ON DISPATCH (returns day %d)" % int(st["return_day"])
		var econ := ""
		if a["class"] == "demon":
			econ = " burn=%d  corr=%d  cmplx=%d" % [int(st["burn"]), int(st["corruption"]), int(st["complexity"])]
		else:
			econ = " oblig=%d/%d" % [int(st["obligation"]), int(a.get("obligation_cap_before_stops_picking_up", 0))]
		lbl.text = "[%s]  %s%s%s" % [
			"D" if a["class"] == "demon" else "H",
			a["name"], econ, status]
		lbl.add_theme_font_size_override("font_size", 10)
		_agent_list_box.add_child(lbl)


func _render_log() -> void:
	_log_label.clear()
	for line in _log_lines:
		_log_label.append_text(line + "\n")


# ── Dispatch flow ────────────────────────────────────────────────
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
	for a_id in _agents:
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
		st["obligation"] = int(st["obligation"]) + int(a.get("obligation_per_dispatch", 1))
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
	_log("Day %d · [b]%s[/b] dispatched to [b]%s[/b] in %s. ETA day %d." %
		[_day, a["name"], p_ref["title"], r["name"], _day + days])
	_render()


# ── Day advance ──────────────────────────────────────────────────
func _on_advance_day() -> void:
	_day += 1
	_dispatches_this_day = 0
	# Resolve returning dispatches.
	for d in _active_dispatches.duplicate():
		if int(d["return_day"]) <= _day:
			_resolve_dispatch(d)
			_active_dispatches.erase(d)
	# Tick problems.
	for r_id in _region_state:
		_tick_region_problems(r_id)
		_tick_region_escalation(r_id)
	# Win/loss check.
	if _day >= TURNS_TOTAL:
		_log("[b]Labor Day arrived.[/b] The summer's end. Interlude shelf: %d items." % _interlude_shelf.size())
	_render()


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
		if a["class"] == "human":
			st["complexity"] = int(st["complexity"]) + 0  # humans don't gain complexity; demons do
		else:
			st["complexity"] = int(st["complexity"]) + 1
	else:
		_log("[color=#ff9090]Day %d · [b]%s[/b] failed at [b]%s[/b]. %s[/color]" %
			[_day, a["name"], p_ref["title"], String(a.get("signature_failure", ""))])
		p_ref["in_progress_by"] = ""
		p_ref["severity"] = float(p_ref["severity"]) + 1.5
		if a["class"] == "demon":
			st["burn"] = int(st["burn"]) + 1
	st["on_dispatch"] = false


func _tick_region_problems(r_id: String) -> void:
	var probs: Array = _region_state[r_id]["active_problems"]
	for p in probs:
		if String(p.get("in_progress_by", "")) != "":
			continue  # in-progress problems don't tick
		var t: Dictionary = _problem_templates.get(p["template_id"], {})
		var tick: float = float(t.get("tick_per_day", 0.3))
		p["severity"] = float(p["severity"]) + tick


func _tick_region_escalation(r_id: String) -> void:
	var r: Dictionary = _regions[r_id]
	var st: Dictionary = _region_state[r_id]
	var clock: float = float(r.get("escalation_clock_days", 6))
	st["escalation_progress"] = float(st["escalation_progress"]) + (1.0 / clock)
	if float(st["escalation_progress"]) >= 1.0:
		st["escalation_progress"] = 0.0
		# Spawn a problem weighted by palette.
		var weights: Dictionary = r.get("problem_palette_weights", {})
		if weights.is_empty():
			return
		# Weighted pick.
		var total: float = 0.0
		for k in weights:
			total += float(weights[k])
		var rng := RandomNumberGenerator.new()
		rng.randomize()
		var pick: float = rng.randf() * total
		var running: float = 0.0
		var chosen_type: String = ""
		for k in weights:
			running += float(weights[k])
			if pick <= running:
				chosen_type = k
				break
		# Find a template matching that type, eligible to this region.
		for t_id in _problem_templates:
			var t: Dictionary = _problem_templates[t_id]
			if String(t.get("problem_type", "")) == chosen_type:
				if (t.get("regions_eligible", []) as Array).has(r_id):
					if String(t.get("spawn_only_by", "")) == "":
						_seed_problem(r_id, t_id)
						_log("Day %d · [b]%s[/b] in %s." % [_day, t["title"], r["name"]])
						break


# ── Logging ──────────────────────────────────────────────────────
func _log(line: String) -> void:
	_log_lines.append(line)
	if _log_lines.size() > 200:
		_log_lines = _log_lines.slice(_log_lines.size() - 200, _log_lines.size())
