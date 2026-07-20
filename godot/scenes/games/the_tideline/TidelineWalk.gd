extends Control
## THE TIDELINE · the walk · twelve stations, two ruled lines each.
##
## Original (2004): at each station, RECORD an observation (one
## line, one slot) or WALK ON with slots unspent — the notebook
## keeps your restraint as faithfully as your attention.  Station
## 11 offers the third thing that is not an observation.  Station
## 12 reads the notebook back as a coastline in one of four
## registers.
##
## Remake (remake_mode, 2048): every observation auto-logs
## instantly; the only button is CONTINUE; the walk takes three
## minutes; station 11's manual moment survives per license §4(c).
##
## Emits: quit · station_done(state) · walk_over(state)

signal quit
signal station_done(state: Dictionary)
signal walk_over(state: Dictionary)

const DATA_PATH := "res://resources/games/vol7/the_tideline/tideline.json"

const C_SEA    := Color("2c343a")
const C_FOG    := Color("dfe4e2")
const C_KELP   := Color("6a7a5e")
const C_PENCIL := Color("b8b0a0")
const C_DIM    := Color("74808a")
const C_MER_BG := Color("eef4f4")
const C_MER_TX := Color("30484a")
const C_MER_OK := Color("58a8a0")

var remake_mode: bool = false

var _state: Dictionary = {}
var _data: Dictionary = {}
var _stations: Array = []
var _slots_left: int = 2
var _root: VBoxContainer = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	var f := FileAccess.open(DATA_PATH, FileAccess.READ)
	if f != null:
		var parsed: Variant = JSON.parse_string(f.get_as_text())
		f.close()
		if parsed is Dictionary:
			_data = parsed
			_stations = _data.get("stations", [])


func boot(state: Dictionary) -> void:
	_state = state
	var bg := ColorRect.new()
	bg.color = C_MER_BG if remake_mode else C_SEA
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("stop_scene_bgm"):
		am.stop_scene_bgm()
	_show_station()


func _fg() -> Color:
	return C_MER_TX if remake_mode else C_FOG


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
	_root.offset_top = -280
	_root.offset_bottom = 280
	_root.add_theme_constant_override("separation", 10)
	add_child(_root)


func _add_body(text: String, size: int = 15, color: Color = Color.TRANSPARENT) -> void:
	var lbl := Label.new()
	lbl.text = text
	lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	lbl.add_theme_font_size_override("font_size", size)
	lbl.add_theme_color_override("font_color", _fg() if color == Color.TRANSPARENT else color)
	_root.add_child(lbl)


# ─── Stations ────────────────────────────────────────────────────

func _station_def(idx: int) -> Dictionary:
	if idx >= 0 and idx < _stations.size():
		return _stations[idx]
	return {}


func _recorded_ids() -> Array:
	var out: Array = []
	for l_v in _state.get("lines", []):
		out.append(String((l_v as Dictionary).get("obs_id", "")))
	return out


func _show_station() -> void:
	var idx: int = int(_state.get("station", 0))
	if idx >= _stations.size() - 1:
		_show_report()
		return
	_slots_left = 2
	_make_root()
	var st := _station_def(idx)
	var hdr := Label.new()
	hdr.text = "· STATION %d · %s ·" % [idx + 1, String(st.get("name", "")).to_upper()]
	hdr.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hdr.add_theme_font_size_override("font_size", 18)
	hdr.add_theme_color_override("font_color", C_MER_OK if remake_mode else C_KELP)
	_root.add_child(hdr)

	if remake_mode:
		_add_body(String((_data.get("remake", {}) as Dictionary).get("arrive_prefix", "")), 12, C_MER_OK)
	_add_body(String(st.get("arrive", "")))

	if remake_mode:
		_show_station_remake(idx, st)
	else:
		_show_station_original(idx, st)
	GamepadMgr.focus_first.call_deferred(_root)


func _show_station_original(idx: int, st: Dictionary) -> void:
	var slots_lbl := Label.new()
	slots_lbl.text = "ruled lines left at this station · %d" % _slots_left
	slots_lbl.add_theme_font_size_override("font_size", 12)
	slots_lbl.add_theme_color_override("font_color", C_PENCIL)
	_root.add_child(slots_lbl)
	var recorded := _recorded_ids()
	for o_v in st.get("obs", []):
		var o: Dictionary = o_v
		var oid := String(o.get("id", ""))
		var b := Button.new()
		b.text = "  record · %s  " % String(o.get("line", ""))
		b.add_theme_font_size_override("font_size", 13)
		b.disabled = recorded.has(oid)
		b.pressed.connect(_on_record.bind(idx, o, slots_lbl))
		_root.add_child(b)
	# Station 11's third thing, which is not an observation.
	var watch: Dictionary = st.get("special_watch", {})
	if not watch.is_empty() and not bool(_state.get("watched_the_seal", false)):
		var wb := Button.new()
		wb.text = "  · %s ·  " % String(watch.get("label", ""))
		wb.add_theme_font_size_override("font_size", 13)
		wb.pressed.connect(_on_watch.bind(watch))
		_root.add_child(wb)
	var walk_btn := Button.new()
	walk_btn.text = "  → walk on  "
	walk_btn.add_theme_font_size_override("font_size", 14)
	walk_btn.pressed.connect(_advance_station)
	_root.add_child(walk_btn)


func _show_station_remake(idx: int, st: Dictionary) -> void:
	# Everything logs itself. The only button is CONTINUE.
	var obs: Array = st.get("obs", [])
	for o_v in obs:
		var o: Dictionary = o_v
		var lines: Array = _state.get("lines", [])
		lines.append({"station": idx, "obs_id": String(o.get("id", "")),
			"line": String(o.get("line", "")), "cat": String(o.get("cat", "line"))})
		_state["lines"] = lines
		var lbl := Label.new()
		lbl.text = "  ✓ %s" % String(o.get("line", ""))
		lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		lbl.add_theme_font_size_override("font_size", 12)
		lbl.add_theme_color_override("font_color", C_MER_OK)
		_root.add_child(lbl)
	var rk: Dictionary = _data.get("remake", {})
	var auto_lbl := Label.new()
	auto_lbl.text = String(rk.get("auto_line", "%d · %s · %s")) % [obs.size(), "0.3", "99.2"]
	auto_lbl.add_theme_font_size_override("font_size", 12)
	auto_lbl.add_theme_color_override("font_color", C_MER_TX)
	_root.add_child(auto_lbl)
	# License §4(c) · the one surviving manual moment.
	var watch: Dictionary = st.get("special_watch", {})
	if not watch.is_empty() and not bool(_state.get("watched_the_seal", false)):
		_add_body(String(rk.get("compliance_note", "")), 12, C_MER_OK)
		var wb := Button.new()
		wb.text = "  · %s ·  " % String(watch.get("label", ""))
		wb.add_theme_font_size_override("font_size", 13)
		wb.pressed.connect(_on_watch_remake.bind(rk))
		_root.add_child(wb)
	var cont := Button.new()
	cont.text = "  %s  " % String(rk.get("continue_label", "CONTINUE"))
	cont.add_theme_font_size_override("font_size", 14)
	cont.pressed.connect(_advance_station)
	_root.add_child(cont)


func _on_record(idx: int, o: Dictionary, slots_lbl: Label) -> void:
	if _slots_left <= 0:
		return
	var lines: Array = _state.get("lines", [])
	lines.append({"station": idx, "obs_id": String(o.get("id", "")),
		"line": String(o.get("line", "")), "cat": String(o.get("cat", "line"))})
	_state["lines"] = lines
	_slots_left -= 1
	slots_lbl.text = "ruled lines left at this station · %d" % _slots_left
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("page_turn", 0.4)
	# Disable the chosen row; lock all rows when the page is full.
	for c in _root.get_children():
		if c is Button and String((c as Button).text).begins_with("  record"):
			if String((c as Button).text).find(String(o.get("line", ""))) >= 0:
				(c as Button).disabled = true
			elif _slots_left <= 0:
				(c as Button).disabled = true


func _on_watch(watch: Dictionary) -> void:
	# Spends both remaining lines. Writes nothing.
	_slots_left = 0
	_state["watched_the_seal"] = true
	_make_root()
	_add_body(String(watch.get("text", "")))
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("season_settle", 0.5)
	var go := Button.new()
	go.text = "  → walk on  "
	go.add_theme_font_size_override("font_size", 14)
	go.pressed.connect(_advance_station)
	_root.add_child(go)
	GamepadMgr.focus_first.call_deferred(_root)


func _on_watch_remake(rk: Dictionary) -> void:
	_state["watched_the_seal"] = true
	_make_root()
	_add_body(String(rk.get("watch_text", "")))
	var go := Button.new()
	go.text = "  %s  " % String(rk.get("continue_label", "CONTINUE"))
	go.add_theme_font_size_override("font_size", 14)
	go.pressed.connect(_advance_station)
	_root.add_child(go)
	GamepadMgr.focus_first.call_deferred(_root)


func _advance_station() -> void:
	_state["station"] = int(_state.get("station", 0)) + 1
	station_done.emit(_state)
	_show_station()


# ─── Station 12 · the report ─────────────────────────────────────

func _show_report() -> void:
	_make_root()
	var last := _station_def(_stations.size() - 1)
	var hdr := Label.new()
	hdr.text = "· STATION 12 · THE POINT ·"
	hdr.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hdr.add_theme_font_size_override("font_size", 18)
	hdr.add_theme_color_override("font_color", C_MER_OK if remake_mode else C_KELP)
	_root.add_child(hdr)
	_add_body(String(last.get("arrive", "")))

	var scroll := ScrollContainer.new()
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_root.add_child(scroll)
	var body := Label.new()
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.custom_minimum_size = Vector2(860, 0)
	body.add_theme_font_size_override("font_size", 13)
	body.add_theme_color_override("font_color", _fg())
	scroll.add_child(body)

	var lines: Array = _state.get("lines", [])
	if remake_mode:
		var rk: Dictionary = _data.get("remake", {})
		body.text = "%s\n\n%s" % [String(rk.get("report_title", "")), String(rk.get("report_body", ""))]
	else:
		# Register from what you attended to.
		var counts := {"living": 0, "lost": 0, "line": 0}
		var read_back := PackedStringArray()
		for l_v in lines:
			var l: Dictionary = l_v
			counts[String(l.get("cat", "line"))] = int(counts.get(String(l.get("cat", "line")), 0)) + 1
			read_back.append("· " + String(l.get("line", "")))
		var reports: Dictionary = _data.get("reports", {})
		var top := "line"
		var top_n: int = -1
		for k in ["living", "lost", "line"]:
			if int(counts[k]) > top_n:
				top_n = int(counts[k])
				top = k
		var spread: int = top_n - mini(mini(int(counts["living"]), int(counts["lost"])), int(counts["line"]))
		var pick: Dictionary = reports.get("whole", {}) if spread <= 2 and lines.size() >= 6 else reports.get(top, {})
		var canon: Dictionary = _state.get("canon_vars", {})
		canon["tideline_report"] = String(pick.get("title", ""))
		_state["canon_vars"] = canon
		body.text = "THE REPORT · %s\n\n%s\n\n%s\n\n%s" % [
			String(pick.get("title", "")),
			"\n".join(read_back) if not read_back.is_empty() else "(the notebook went home blank, which is also a reading of the beach)",
			String(pick.get("coda", "")),
			String(reports.get("footer", ""))]

	var done := Button.new()
	done.text = "  · hand in the notebook ·  " if not remake_mode else "  ARCHIVE AND EXIT  "
	done.add_theme_font_size_override("font_size", 14)
	done.pressed.connect(func() -> void: walk_over.emit(_state))
	_root.add_child(done)
	GamepadMgr.focus_first.call_deferred(_root)


func _input(event: InputEvent) -> void:
	if not is_visible_in_tree():
		return
	if event is InputEventKey and event.pressed and not event.echo:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			quit.emit()
			get_viewport().set_input_as_handled()
