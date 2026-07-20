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
		_advance_chapter()
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
	_add_choice("→ the next call", _show_water)
	GamepadMgr.focus_first.call_deferred(_root)


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
	var eid := "water_decides"
	if aligned_count >= 3:
		eid = "estuary_remembers"
	elif aligned_count <= 1:
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
