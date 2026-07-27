extends Control
## ESTUARY 4 · the campaign · four chapters, beat-sequence.
##
## Ch1 THE ARCHIVE picks the plan emphasis (line / living / lost ·
## or, when the token bus carries the_tideline_finished, the 2003
## notebook — whose filed register is read back from cross-stick
## canon and becomes the plan).  Ch2 THE WATER makes three calls,
## each argued in the chosen file's voice.  Ch3 THE HUNTER walks
## the line with Ashford Cade, back in the spring.  Ch4 THE KING
## TIDE reads the calls against the plan and files the survey.
##
## v2 DEPTH BUILD (2026-07-27): between the calls and the hunter
## sits THE WORKING SEASON — thirteen field weeks, each allocated
## under a budget, crew morale, a seeded tide table (gate and
## channel work needs the water low), and storms the glass warns
## about one week ahead.  The king tide then reads what you
## actually BUILT, not just what you argued.
##
## Emits: quit · chapter_done(state) · campaign_over(state)

signal quit
signal chapter_done(state: Dictionary)
signal campaign_over(state: Dictionary)

const DATA_PATH := "res://resources/games/vol7/estuary_4/estuary_4.json"

const C_WATER := Color("28343c")
const C_FOG   := Color("dce4e0")
const C_REED  := Color("7a8a5e")
const C_GOLD  := Color("c8b070")
const C_DIM   := Color("70807a")

var _state: Dictionary = {}
var _data: Dictionary = {}
var _root: VBoxContainer = null
var _call_index: int = 0


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	var f := FileAccess.open(DATA_PATH, FileAccess.READ)
	if f != null:
		var parsed: Variant = JSON.parse_string(f.get_as_text())
		f.close()
		if parsed is Dictionary:
			_data = parsed


func boot(state: Dictionary) -> void:
	_state = state
	if not _state.has("seed"):
		_state["seed"] = randi() % 100000
	if not _state.has("season"):
		_state["season"] = {"week": 4, "budget": 10, "morale": 3,
			"progress": {"gate": 0, "channel": 0, "plantings": 0},
			"damaged": [], "grant_taken": false, "prepped_week": -1}
	var bg := ColorRect.new()
	bg.color = C_WATER
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	_show_chapter()


func _clear_root() -> void:
	if _root != null and is_instance_valid(_root):
		_root.queue_free()
	_root = null


func _make_root() -> void:
	_clear_root()
	_root = VBoxContainer.new()
	_root.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_root.offset_left = -440
	_root.offset_right = 440
	_root.offset_top = -290
	_root.offset_bottom = 290
	_root.add_theme_constant_override("separation", 10)
	add_child(_root)


func _add_header(text: String) -> void:
	var hdr := Label.new()
	hdr.text = "· %s ·" % text
	hdr.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hdr.add_theme_font_size_override("font_size", 18)
	hdr.add_theme_color_override("font_color", C_REED)
	_root.add_child(hdr)


func _add_body(text: String, size: int = 14, color: Color = C_FOG) -> void:
	var lbl := Label.new()
	lbl.text = text
	lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	lbl.add_theme_font_size_override("font_size", size)
	lbl.add_theme_color_override("font_color", color)
	_root.add_child(lbl)


func _add_choice(label: String, cb: Callable) -> void:
	var b := Button.new()
	b.text = "  %s  " % label
	b.add_theme_font_size_override("font_size", 13)
	b.pressed.connect(cb)
	_root.add_child(b)


func _advance_chapter() -> void:
	_state["chapter"] = int(_state.get("chapter", 1)) + 1
	_call_index = 0
	chapter_done.emit(_state)
	_show_chapter()


func _show_chapter() -> void:
	match int(_state.get("chapter", 1)):
		1: _show_archive()
		2: _show_water()
		3: _show_hunter()
		_: _show_king_tide()


# ─── Ch1 · the archive ───────────────────────────────────────────

func _tideline_register() -> String:
	# Cross-stick canon read · the first stick to consume another
	# stick's canon var, not just a token.
	if not OneironauticsTokens.has("the_tideline_finished"):
		return ""
	var reg := String(OneironauticsTokens.canon("tideline_report", ""))
	return reg if reg != "" else "THE WHOLE BEACH"


func _show_archive() -> void:
	_make_root()
	var ch: Dictionary = _data.get("ch1", {})
	_add_header(String(ch.get("title", "")))
	_add_body(String(ch.get("intro", "")))
	for f_v in ch.get("folders", []):
		var folder: Dictionary = f_v
		_add_choice(String(folder.get("label", "")), _on_pick_folder.bind(folder))
	# The fourth folder · your own notebook, thirteen years on.
	var reg := _tideline_register()
	if reg != "":
		var nb: Dictionary = ch.get("notebook_folder", {})
		_add_choice(String(nb.get("label", "")), _on_pick_notebook.bind(nb, reg))
	GamepadMgr.focus_first.call_deferred(_root)


func _on_pick_folder(folder: Dictionary) -> void:
	_state["plan"] = String(folder.get("plan", "line"))
	_make_root()
	_add_body(String(folder.get("body", "")))
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("page_turn", 0.5)
	_add_choice("→ take the plan to the water", _advance_chapter)
	GamepadMgr.focus_first.call_deferred(_root)


func _on_pick_notebook(nb: Dictionary, reg: String) -> void:
	var plans: Dictionary = nb.get("register_plans", {})
	_state["plan"] = String(plans.get(reg, "whole"))
	_state["read_notebook"] = true
	_make_root()
	_add_body("%s%s%s" % [String(nb.get("body_prefix", "")), reg, String(nb.get("body_suffix", ""))])
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("season_settle", 0.5)
	_add_choice("→ take the plan to the water", _advance_chapter)
	GamepadMgr.focus_first.call_deferred(_root)


# ─── Ch2 · the water ─────────────────────────────────────────────

func _show_water() -> void:
	var ch: Dictionary = _data.get("ch2", {})
	var calls: Array = ch.get("calls", [])
	if _call_index >= calls.size():
		_show_season_week()
		return
	_make_root()
	if _call_index == 0:
		_add_header(String(ch.get("title", "")))
		_add_body(String(ch.get("intro", "")), 13, C_DIM)
	var call: Dictionary = calls[_call_index]
	_add_header(String(call.get("title", "")).to_upper())
	_add_body(String(call.get("body", "")))
	var plan := String(_state.get("plan", "line"))
	var arg := String((call.get("arguments", {}) as Dictionary).get(plan, ""))
	if arg != "":
		_add_body("the file argues: %s" % arg, 13, C_GOLD)
	for o_v in call.get("options", []):
		var o: Dictionary = o_v
		_add_choice(String(o.get("label", "")), _on_pick_call.bind(call, o))
	GamepadMgr.focus_first.call_deferred(_root)


func _on_pick_call(call: Dictionary, o: Dictionary) -> void:
	var calls_made: Dictionary = _state.get("calls", {})
	calls_made[String(call.get("id", ""))] = {
		"option": String(o.get("id", "")),
		"aligned": (o.get("aligned", []) as Array).duplicate(),
	}
	_state["calls"] = calls_made
	_make_root()
	_add_body(String(o.get("result", "")))
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("card_place", 0.5)
	_call_index += 1
	chapter_done.emit(_state)
	if _call_index >= (call.get("_total", 3) if call.has("_total") else 3):
		_add_choice("→ to the water · the season starts", _show_water)
	else:
		_add_choice("→ the next call", _show_water)
	GamepadMgr.focus_first.call_deferred(_root)


# ─── Ch2b · THE WORKING SEASON · thirteen field weeks ────────────
# Budget, morale, tide windows, storms.  The three calls are plans;
# the season is where plans meet water.

const SEASON_END := 17            # weeks 4..16 inclusive
const PROJ := {
	"gate":      {"label": "the tide gate", "need": 5, "diff": 2, "cost": 1, "tidal": true},
	"channel":   {"label": "the channel",   "need": 5, "diff": 3, "cost": 2, "tidal": true},
	"plantings": {"label": "the plantings", "need": 4, "diff": 1, "cost": 1, "tidal": false},
}
const WEEK_DATES := ["", "", "", "", "late april", "early may", "mid-may",
	"late may", "early june", "mid-june", "late june", "july", "late july",
	"september", "early october", "late october", "november"]


func _season() -> Dictionary:
	return _state.get("season", {})


func _tide_for(week: int) -> String:
	var rng := RandomNumberGenerator.new()
	rng.seed = int(_state.get("seed", 0)) * 37 + week
	var roll: int = rng.randi_range(0, 9)
	return "low" if roll < 4 else ("neutral" if roll < 8 else "high")


func _storm_for(week: int) -> bool:
	var rng := RandomNumberGenerator.new()
	rng.seed = int(_state.get("seed", 0)) * 53 + week * 11
	return week >= 6 and rng.randi_range(0, 9) < 3


func _luck_for(week: int) -> int:
	var rng := RandomNumberGenerator.new()
	rng.seed = int(_state.get("seed", 0)) * 71 + week * 13
	return rng.randi_range(0, 2)


func _show_season_week() -> void:
	var se: Dictionary = _season()
	var week: int = int(se.get("week", 4))
	if week >= SEASON_END:
		_advance_chapter()
		return
	_make_root()
	var tide := _tide_for(week)
	var storm_now := _storm_for(week)
	var storm_next := _storm_for(week + 1)
	_add_header("THE WORKING SEASON · %s · week %d of 13" % [WEEK_DATES[week], week - 3])
	var tide_line := {"low": "the tide book gives you the flats — gate and channel are workable, and gladly.",
		"neutral": "middling water. the tidal work is possible, not generous.",
		"high": "the water sits high on the pilings all week. no gate, no channel — the estuary is closed for business."}[tide]
	_add_body(tide_line, 13, C_DIM)
	if storm_now:
		_add_body("a storm is ON the water this week. unprepped work will pay for it.", 13, C_GOLD)
	elif storm_next:
		_add_body("the glass is dropping hard. cade would say: whatever you love out there, lash it down this week.", 13, C_GOLD)
	var prog: Dictionary = se.get("progress", {})
	var damaged: Array = se.get("damaged", [])
	var status := "budget $%d · crew morale %d/5" % [int(se.get("budget", 0)), int(se.get("morale", 3))]
	_add_body(status, 13, C_REED)
	for pid in ["gate", "channel", "plantings"]:
		var pd: Dictionary = PROJ[pid]
		var bar := ""
		for i in range(int(pd["need"])):
			bar += "■" if i < int(prog.get(pid, 0)) else "□"
		var flag := "  · STORM-DAMAGED" if damaged.has(pid) else ""
		_add_body("%s  %s%s" % [String(pd["label"]), bar, flag], 13, C_FOG)
	# ── the week's allocation ──
	for pid2 in ["gate", "channel", "plantings"]:
		var pd2: Dictionary = PROJ[pid2]
		if int(prog.get(pid2, 0)) >= int(pd2["need"]):
			continue
		if bool(pd2["tidal"]) and tide == "high":
			continue
		if int(se.get("budget", 0)) < int(pd2["cost"]):
			continue
		_add_choice("work %s · careful  (-$%d)" % [String(pd2["label"]), int(pd2["cost"])],
			_season_work.bind(pid2, false))
		_add_choice("work %s · hard push  (-$%d, -1 morale)" % [String(pd2["label"]), int(pd2["cost"])],
			_season_work.bind(pid2, true))
	if not damaged.is_empty():
		_add_choice("repair the storm damage", _season_repair)
	if storm_next:
		_add_choice("spend the week lashing down · storm prep", _season_prep)
	if week == 6 and not bool(se.get("grant_taken", false)):
		_add_choice("write the county grant · deadline is THIS week  (+$6)", _season_grant)
	_add_choice("rest the crew  (+2 morale)", _season_rest)
	GamepadMgr.focus_first.call_deferred(_root)


func _season_outcome(lines: Array) -> void:
	var se: Dictionary = _season()
	var week: int = int(se.get("week", 4))
	# a storm lands on whatever is half-built and unprepped
	if _storm_for(week) and int(se.get("prepped_week", -1)) != week:
		var worst := ""
		var worst_p := 999
		var prog: Dictionary = se.get("progress", {})
		for pid in ["gate", "channel", "plantings"]:
			var p: int = int(prog.get(pid, 0))
			if p > 0 and p < int((PROJ[pid] as Dictionary)["need"]) and p < worst_p:
				worst = pid
				worst_p = p
		if worst != "":
			prog[worst] = maxi(0, int(prog[worst]) - 1)
			var dmg: Array = se.get("damaged", [])
			if not dmg.has(worst):
				dmg.append(worst)
			se["damaged"] = dmg
			lines.append("the storm finds %s half-finished and takes a week of it back. the estuary does not grade on effort." % String((PROJ[worst] as Dictionary)["label"]))
	se["week"] = week + 1
	chapter_done.emit(_state)
	_make_root()
	for ln in lines:
		_add_body(String(ln))
	_add_choice("→ the next week", _show_season_week)
	GamepadMgr.focus_first.call_deferred(_root)


func _season_work(pid: String, push: bool) -> void:
	var se: Dictionary = _season()
	var week: int = int(se.get("week", 4))
	var pd: Dictionary = PROJ[pid]
	se["budget"] = int(se.get("budget", 0)) - int(pd["cost"])
	var morale: int = int(se.get("morale", 3))
	if push:
		se["morale"] = maxi(0, morale - 1)
	var luck := _luck_for(week)
	var mod: int = 0
	var bits: PackedStringArray = PackedStringArray()
	if bool(pd["tidal"]) and _tide_for(week) == "low":
		mod += 1; bits.append("+1 low water")
	if morale >= 4:
		mod += 1; bits.append("+1 crew in good heart")
	elif morale <= 1:
		mod -= 1; bits.append("-1 crew worn out")
	var score: int = luck + mod - int(pd["diff"]) + 2
	var tier: int = 2 if score >= 3 else (1 if score >= 1 else 0)
	var gain: int = [0, 1, 2][tier] + (1 if push else 0)
	var prog: Dictionary = se.get("progress", {})
	prog[pid] = mini(int(pd["need"]), int(prog.get(pid, 0)) + gain)
	var tier_word: String = ["a week the water wins", "a fair week's work", "a strong week's work"][tier]
	var lines: Array = ["%s · luck %d %s vs. the job %d — %s. progress +%d." % [
		String(pd["label"]), luck, " ".join(bits), int(pd["diff"]), tier_word, gain]]
	if tier == 0:
		lines.append("nothing to show but what the crew learned about the site, which is not nothing, but it is not progress either.")
	_season_outcome(lines)


func _season_repair() -> void:
	var se: Dictionary = _season()
	se["damaged"] = []
	_season_outcome(["you give the week to the damage. it is slower than building — it always is — but the work stands whole again."])


func _season_prep() -> void:
	var se: Dictionary = _season()
	# protects the week the glass warned about (the one now arriving)
	se["prepped_week"] = int(se.get("week", 4)) + 1
	_season_outcome(["you lash down the season's work · stakes doubled, silt fence trenched, the gate blocked open the way the old logbook says. whatever the storm wants, it will have to argue for."])


func _season_grant() -> void:
	var se: Dictionary = _season()
	se["grant_taken"] = true
	se["budget"] = int(se.get("budget", 0)) + 6
	_season_outcome(["you spend the week at a desk writing the county's own language back at it. it works. it always works, and nobody in the field ever believes it was a real week's work. it was."])


func _season_rest() -> void:
	var se: Dictionary = _season()
	se["morale"] = mini(5, int(se.get("morale", 3)) + 2)
	_season_outcome(["you stand the crew down. somebody's kid graduates, somebody's boat gets painted, and on monday the shovels come back sharper."])


func _build_quality(pid: String) -> int:
	var se: Dictionary = _season()
	var prog: Dictionary = se.get("progress", {})
	var pd: Dictionary = PROJ[pid]
	var q: int = int(floor(float(int(prog.get(pid, 0))) * 3.0 / float(int(pd["need"]))))
	if (se.get("damaged", []) as Array).has(pid):
		q -= 1
	return clampi(q, 0, 3)


# ─── Ch3 · the hunter ────────────────────────────────────────────

func _show_hunter() -> void:
	_make_root()
	var ch: Dictionary = _data.get("ch3", {})
	_add_header(String(ch.get("title", "")))
	_add_body(String(ch.get("intro", "")))
	for c_v in ch.get("choices", []):
		var c: Dictionary = c_v
		_add_choice(String(c.get("label", "")), _on_pick_cade.bind(ch, c))
	GamepadMgr.focus_first.call_deferred(_root)


func _on_pick_cade(ch: Dictionary, c: Dictionary) -> void:
	_make_root()
	if String(c.get("id", "")) == "walk_full":
		_state["cade_walked"] = true
		_add_body(String(ch.get("walk", "")))
		var plan := String(_state.get("plan", "line"))
		var pl := String((ch.get("walk_plan_lines", {}) as Dictionary).get(plan, ""))
		if pl != "":
			_add_body(pl, 13, C_GOLD)
		_add_body(String(ch.get("island_nod", "")), 13, C_DIM)
	_add_body(String(c.get("result", "")))
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("page_turn", 0.5)
	_add_choice("→ toward december", _advance_chapter)
	GamepadMgr.focus_first.call_deferred(_root)


# ─── Ch4 · the king tide ─────────────────────────────────────────

func _show_king_tide() -> void:
	_make_root()
	var ch: Dictionary = _data.get("ch4", {})
	_add_header(String(ch.get("title", "")))
	_add_body(String(ch.get("intro", "")))
	# Score the season: calls aligned with the plan you argued.
	var plan := String(_state.get("plan", "line"))
	var aligned_count := 0
	var calls_made: Dictionary = _state.get("calls", {})
	for k in calls_made.keys():
		var entry: Dictionary = calls_made[k]
		var aligned: Array = entry.get("aligned", [])
		if aligned.has(plan) or plan == "whole":
			aligned_count += 1
	var q_total: int = _build_quality("gate") + _build_quality("channel") + _build_quality("plantings")
	for pid in ["gate", "channel", "plantings"]:
		var q: int = _build_quality(pid)
		var pl: String = String((PROJ[pid] as Dictionary)["label"])
		if q >= 2:
			_add_body("%s held." % pl, 14, C_REED)
		elif q == 1:
			_add_body("%s held, mostly. the water edited the margins." % pl, 14, C_DIM)
		else:
			_add_body("%s went. the december water took it back to the survey line." % pl, 14, C_GOLD)
	var eid := "water_decides"
	if aligned_count >= 3 and q_total >= 6:
		eid = "estuary_remembers"
	elif aligned_count <= 1 or q_total <= 2:
		eid = "second_survey"
	var endings: Dictionary = ch.get("endings", {})
	var pick: Dictionary = endings.get(eid, {})
	var canon: Dictionary = _state.get("canon_vars", {})
	canon["e4_ending"] = eid
	_state["canon_vars"] = canon
	_add_header(String(pick.get("title", "")))
	_add_body(String(pick.get("body", "")))
	_add_body(String(ch.get("footer", "")), 13, C_GOLD)
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("win_chord", 0.6)
	_add_choice("· file the survey ·", func() -> void: campaign_over.emit(_state))
	GamepadMgr.focus_first.call_deferred(_root)


func _input(event: InputEvent) -> void:
	if not is_visible_in_tree():
		return
	if event is InputEventKey and event.pressed and not event.echo:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			quit.emit()
			get_viewport().set_input_as_handled()
