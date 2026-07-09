extends Control
## Fey Faire · The Trailer · Prospero's Airstream · scaffold pass.
##
## The player's persistent home base.  Six fixtures are
## interactable and open sub-panels:
##   · KEEPSAKE BOOKCASE · 20 active slots + footlocker overflow ·
##     shows collected keepsakes from keepsakes.json with lore +
##     effect · scaffolded read-only for this pass (swap-active
##     UI is a follow-up commit)
##   · COTS · party roster · lists recruited feys · dismiss/invite
##     stubs
##   · WRITING DESK · compendium · met/recruited/hostile feys
##     from feys.json · grouped by court
##   · MEMORY MIRRORS · six mirrors matching the boot questionnaire
##     · cracked when memory lost
##   · HEARTH · HP restore stub (no HP tracking in scaffold)
##   · HELIA THE CAT · per-fey disposition indicator (tail flick
##     description per recruited fey)
##
## Signals:
##   quit · returns to Gate
##
## F4-compliant via add_to_group("ui").

signal quit

const FEYS_PATH      := "res://resources/games/vol7/fey_faire/feys.json"
const KEEPSAKES_PATH := "res://resources/games/vol7/fey_faire/keepsakes.json"

# Trailer palette · warmer, more mundane than the Faire
const C_BG        := Color(0.145, 0.098, 0.075, 1.0)   # inside-a-trailer dark
const C_WOOD      := Color(0.451, 0.294, 0.180, 1.0)   # Craftsman wood
const C_WOOD_HI   := Color(0.671, 0.443, 0.263, 1.0)
const C_CREAM     := Color(0.957, 0.878, 0.816, 1.0)
const C_ROSE      := Color(0.878, 0.722, 0.753, 1.0)
const C_GOLD      := Color(0.973, 0.784, 0.282, 1.0)
const C_GOLD_DIM  := Color(0.541, 0.361, 0.157, 1.0)
const C_LAMP      := Color(0.973, 0.816, 0.518, 1.0)   # warm lamplight
const C_MEMORY    := Color(0.62, 0.55, 0.72, 1.0)      # memory-mirror silvery
const C_CRACKED   := Color(0.42, 0.30, 0.30, 1.0)      # cracked mirror

var _run_state: Dictionary = {}
var _feys_by_id: Dictionary = {}
var _keepsakes_by_id: Dictionary = {}
var _panel_root: Control = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")


func boot(state: Dictionary) -> void:
	_run_state = state
	_load_data()
	_build_frame()
	_render_main_view()


func _load_data() -> void:
	if FileAccess.file_exists(FEYS_PATH):
		var f := FileAccess.open(FEYS_PATH, FileAccess.READ)
		var parsed: Variant = JSON.parse_string(f.get_as_text())
		f.close()
		if parsed is Dictionary:
			for entry_v in (parsed as Dictionary).get("feys", []):
				var entry: Dictionary = entry_v
				_feys_by_id[String(entry.get("id", ""))] = entry
	if FileAccess.file_exists(KEEPSAKES_PATH):
		var f2 := FileAccess.open(KEEPSAKES_PATH, FileAccess.READ)
		var parsed2: Variant = JSON.parse_string(f2.get_as_text())
		f2.close()
		if parsed2 is Dictionary:
			for entry_v in (parsed2 as Dictionary).get("keepsakes", []):
				var entry: Dictionary = entry_v
				_keepsakes_by_id[String(entry.get("id", ""))] = entry


func _build_frame() -> void:
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# Wood-plank floor · horizontal bands
	for y in range(360, 720, 24):
		var plank := ColorRect.new()
		plank.color = C_WOOD if (y / 24) % 2 == 0 else C_WOOD_HI
		plank.set_anchors_preset(Control.PRESET_TOP_WIDE)
		plank.position.y = y
		plank.size = Vector2(2000, 12)
		add_child(plank)

	# Warm lamp glow at center-top · Prospero's bare bulb
	var lamp := ColorRect.new()
	lamp.color = C_LAMP
	lamp.set_anchors_preset(Control.PRESET_TOP_LEFT)
	lamp.position = Vector2(0, 0)
	lamp.size = Vector2(2000, 60)
	# Simulate glow via a specific alpha
	lamp.color.a = 0.25
	add_child(lamp)

	# Header
	var header := Label.new()
	header.text = "· THE TRAILER · PROSPERO'S AIRSTREAM ·"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 14)
	header.add_theme_color_override("font_color", C_LAMP)
	header.set_anchors_preset(Control.PRESET_TOP_WIDE)
	header.offset_top = 20
	header.offset_bottom = 48
	add_child(header)


func _clear_panel() -> void:
	if _panel_root != null and is_instance_valid(_panel_root):
		_panel_root.queue_free()
	_panel_root = null


func _render_main_view() -> void:
	_clear_panel()
	_panel_root = Control.new()
	_panel_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_panel_root.offset_top = 60
	_panel_root.offset_bottom = -20
	_panel_root.offset_left = 40
	_panel_root.offset_right = -40
	add_child(_panel_root)

	# 3x2 fixture grid
	var grid := GridContainer.new()
	grid.columns = 3
	grid.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	grid.add_theme_constant_override("h_separation", 16)
	grid.add_theme_constant_override("v_separation", 16)
	_panel_root.add_child(grid)

	_add_fixture_button(grid, "KEEPSAKE BOOKCASE",
		"twenty active slots · footlocker overflow",
		_active_keepsake_count_string(),
		_render_bookcase_view)

	_add_fixture_button(grid, "COTS · PARTY ROSTER",
		"four beds · one for you, three for recruited feys",
		_party_summary_string(),
		_render_cots_view)

	_add_fixture_button(grid, "WRITING DESK · COMPENDIUM",
		"met · recruited · defeated · dismissed",
		_compendium_summary_string(),
		_render_compendium_view)

	_add_fixture_button(grid, "MEMORY MIRRORS",
		"six · one per boot question · crack on death",
		_memory_summary_string(),
		_render_memory_view)

	_add_fixture_button(grid, "HEARTH",
		"kitchen · restore HP without advancing the night",
		"pending · no HP tracking yet",
		null)

	_add_fixture_button(grid, "HELIA · THE CAT",
		"Prospero's cat · shows how each recruited fey feels",
		_helia_summary_string(),
		_render_helia_view)

	# Back button
	var back := Button.new()
	back.text = "  ← back to the Gate  "
	back.add_theme_font_size_override("font_size", 11)
	back.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	back.offset_top = -40
	back.offset_bottom = -8
	back.pressed.connect(_on_back)
	_panel_root.add_child(back)


func _add_fixture_button(parent: Node, title: String, subtitle: String, status: String, callback: Variant) -> void:
	var cell := ColorRect.new()
	cell.color = C_WOOD
	cell.custom_minimum_size = Vector2(320, 120)
	parent.add_child(cell)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.offset_left = 12
	v.offset_right = -12
	v.offset_top = 10
	v.offset_bottom = -10
	v.add_theme_constant_override("separation", 4)
	cell.add_child(v)

	var title_lbl := Label.new()
	title_lbl.text = title
	title_lbl.add_theme_font_size_override("font_size", 12)
	title_lbl.add_theme_color_override("font_color", C_LAMP)
	v.add_child(title_lbl)

	var subtitle_lbl := Label.new()
	subtitle_lbl.text = "· " + subtitle
	subtitle_lbl.add_theme_font_size_override("font_size", 9)
	subtitle_lbl.add_theme_color_override("font_color", C_GOLD_DIM)
	v.add_child(subtitle_lbl)

	var status_lbl := Label.new()
	status_lbl.text = status
	status_lbl.add_theme_font_size_override("font_size", 10)
	status_lbl.add_theme_color_override("font_color", C_CREAM)
	status_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(status_lbl)

	var btn := Button.new()
	btn.text = "  open  " if callback != null else "  pending  "
	btn.add_theme_font_size_override("font_size", 10)
	btn.disabled = (callback == null)
	if callback != null:
		btn.pressed.connect(callback)
	v.add_child(btn)


func _active_keepsake_count_string() -> String:
	var kp: Array = _run_state.get("keepsakes", [])
	return "%d keepsake%s · 20 slots" % [kp.size(), "" if kp.size() == 1 else "s"]


func _party_summary_string() -> String:
	var recruited: Array = _run_state.get("recruited_feys", [])
	if recruited.is_empty(): return "· no recruits yet ·"
	var names: Array = []
	for id in recruited:
		var fey: Dictionary = _feys_by_id.get(String(id), {})
		if not fey.is_empty():
			names.append(String(fey.get("name", id)))
	return "recruited · " + ", ".join(names)


func _compendium_summary_string() -> String:
	var met: Array = _run_state.get("met_feys", [])
	var recruited: Array = _run_state.get("recruited_feys", [])
	var total: int = _feys_by_id.size()
	return "%d recruited · %d encountered · %d unmet" % [recruited.size(), met.size(), max(0, total - recruited.size() - met.size())]


func _memory_summary_string() -> String:
	var lost: int = int(_run_state.get("memories_lost", 0))
	return "%d of 6 memories intact" % [6 - lost]


func _helia_summary_string() -> String:
	var recruited: Array = _run_state.get("recruited_feys", [])
	if recruited.is_empty(): return "· no recruits to indicate ·"
	return "%d fey%s to observe" % [recruited.size(), "" if recruited.size() == 1 else "s"]


# ── Bookcase view ─────────────────────────────────────────────
func _render_bookcase_view() -> void:
	_render_sub_view("KEEPSAKE BOOKCASE", func(v: VBoxContainer) -> void:
		var kp: Array = _run_state.get("keepsakes", [])
		if kp.is_empty():
			var empty := Label.new()
			empty.text = "· the bookcase is empty ·"
			empty.add_theme_color_override("font_color", C_GOLD_DIM)
			empty.add_theme_font_size_override("font_size", 11)
			v.add_child(empty)
			var hint := Label.new()
			hint.text = "keepsakes are earned by choosing them at boot, gifted by feys, or found across the Faire."
			hint.add_theme_color_override("font_color", C_CREAM)
			hint.add_theme_font_size_override("font_size", 10)
			hint.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			v.add_child(hint)
			return
		for kp_id in kp:
			var entry: Dictionary = _keepsakes_by_id.get(String(kp_id), {})
			if entry.is_empty(): continue
			_add_keepsake_row(v, entry))


func _add_keepsake_row(parent: Node, entry: Dictionary) -> void:
	var row := ColorRect.new()
	row.color = C_WOOD_HI
	row.custom_minimum_size = Vector2(0, 80)
	parent.add_child(row)

	var vh := VBoxContainer.new()
	vh.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	vh.offset_left = 10
	vh.offset_right = -10
	vh.offset_top = 6
	vh.offset_bottom = -6
	vh.add_theme_constant_override("separation", 2)
	row.add_child(vh)

	var name_lbl := Label.new()
	name_lbl.text = String(entry.get("name", ""))
	name_lbl.add_theme_font_size_override("font_size", 11)
	name_lbl.add_theme_color_override("font_color", C_LAMP)
	vh.add_child(name_lbl)

	var lore_lbl := RichTextLabel.new()
	lore_lbl.bbcode_enabled = false
	lore_lbl.fit_content = true
	lore_lbl.text = String(entry.get("lore", ""))
	lore_lbl.add_theme_font_size_override("normal_font_size", 9)
	lore_lbl.add_theme_color_override("default_color", C_CREAM)
	vh.add_child(lore_lbl)

	var effect_lbl := Label.new()
	effect_lbl.text = "· " + String(entry.get("effect", "no effect authored"))
	effect_lbl.add_theme_font_size_override("font_size", 9)
	effect_lbl.add_theme_color_override("font_color", C_ROSE)
	effect_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	vh.add_child(effect_lbl)


# ── Cots view ─────────────────────────────────────────────────
func _render_cots_view() -> void:
	_render_sub_view("COTS · PARTY ROSTER", func(v: VBoxContainer) -> void:
		var protagonist := Label.new()
		var player_name: String = String(_run_state.get("questionnaire", {}).get("player_name", "you"))
		protagonist.text = "COT 1 · " + player_name + " · always here"
		protagonist.add_theme_font_size_override("font_size", 11)
		protagonist.add_theme_color_override("font_color", C_LAMP)
		v.add_child(protagonist)

		var recruited: Array = _run_state.get("recruited_feys", [])
		var slot_idx: int = 2
		for id in recruited:
			if slot_idx > 4:
				break
			var fey: Dictionary = _feys_by_id.get(String(id), {})
			if fey.is_empty(): continue
			var cot := Label.new()
			cot.text = "COT " + str(slot_idx) + " · " + String(fey.get("name", id)) + " · " + String(fey.get("court", "?")) + " · sleeping"
			cot.add_theme_font_size_override("font_size", 11)
			cot.add_theme_color_override("font_color", C_CREAM)
			v.add_child(cot)
			slot_idx += 1
		while slot_idx <= 4:
			var empty := Label.new()
			empty.text = "COT " + str(slot_idx) + " · empty"
			empty.add_theme_font_size_override("font_size", 11)
			empty.add_theme_color_override("font_color", C_GOLD_DIM)
			v.add_child(empty)
			slot_idx += 1

		var note := Label.new()
		note.text = "\n· recruits can be INVITED and DISMISSED here in a later commit · roster is currently read-only ·"
		note.add_theme_font_size_override("font_size", 9)
		note.add_theme_color_override("font_color", C_ROSE)
		note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		v.add_child(note))


# ── Compendium view ───────────────────────────────────────────
func _render_compendium_view() -> void:
	_render_sub_view("WRITING DESK · COMPENDIUM", func(v: VBoxContainer) -> void:
		var recruited: Array = _run_state.get("recruited_feys", [])
		var met: Array = _run_state.get("met_feys", [])

		var by_court := {"seelie": [], "unseelie": [], "wildfey": []}
		for id in _feys_by_id.keys():
			var f: Dictionary = _feys_by_id[String(id)]
			var court: String = String(f.get("court", "wildfey"))
			if not by_court.has(court): continue
			var status: String = "unmet"
			if recruited.has(String(id)): status = "RECRUITED"
			elif met.has(String(id)): status = "met"
			by_court[court].append({"id": String(id), "name": String(f.get("name", id)), "tier": int(f.get("tier", 1)), "status": status})

		for court in ["seelie", "unseelie", "wildfey"]:
			var header := Label.new()
			header.text = "· " + court.to_upper() + " · " + str(by_court[court].size()) + " feys ·"
			header.add_theme_font_size_override("font_size", 12)
			header.add_theme_color_override("font_color", C_LAMP)
			v.add_child(header)
			for f_v in by_court[court]:
				var f: Dictionary = f_v
				var line := Label.new()
				var status_marker: String = "  "
				if f["status"] == "RECRUITED": status_marker = "✓ "
				elif f["status"] == "met": status_marker = "· "
				else: status_marker = "  "
				line.text = "     " + status_marker + "T" + str(f["tier"]) + " · " + f["name"]
				line.add_theme_font_size_override("font_size", 10)
				var col: Color = C_LAMP if f["status"] == "RECRUITED" else (C_CREAM if f["status"] == "met" else C_GOLD_DIM)
				line.add_theme_color_override("font_color", col)
				v.add_child(line)
			var sep := Control.new()
			sep.custom_minimum_size = Vector2(0, 8)
			v.add_child(sep))


# ── Memory mirror view ────────────────────────────────────────
func _render_memory_view() -> void:
	_render_sub_view("MEMORY MIRRORS · six on the wall", func(v: VBoxContainer) -> void:
		var q: Dictionary = _run_state.get("questionnaire", {})
		var lost: int = int(_run_state.get("memories_lost", 0))
		var slot_map: Array = [
			["bedroom_description", "your bedroom"],
			["favorite_song",       "the song you played"],
			["favorite_meal",       "the meal you enjoyed"],
			["holiday",             "the holiday that matters"],
			["parent_argument",     "the argument with a parent"],
			["first_kiss",          "the first kiss"],
		]
		for i in range(slot_map.size()):
			var key: String = slot_map[i][0]
			var label: String = slot_map[i][1]
			var value: String = String(q.get(key, ""))
			var cracked: bool = i < lost
			var row := ColorRect.new()
			row.color = C_CRACKED if cracked else C_MEMORY
			row.custom_minimum_size = Vector2(0, 60)
			v.add_child(row)
			var vh := VBoxContainer.new()
			vh.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
			vh.offset_left = 10
			vh.offset_right = -10
			vh.offset_top = 4
			vh.offset_bottom = -4
			vh.add_theme_constant_override("separation", 2)
			row.add_child(vh)
			var hdr := Label.new()
			hdr.text = "MIRROR " + str(i + 1) + " · " + label + (" · CRACKED" if cracked else "")
			hdr.add_theme_font_size_override("font_size", 10)
			hdr.add_theme_color_override("font_color", C_BG)
			vh.add_child(hdr)
			var body := Label.new()
			body.text = value if not cracked else "· ... a specific memory that used to be here ..."
			body.add_theme_font_size_override("font_size", 9)
			body.add_theme_color_override("font_color", C_BG)
			body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			vh.add_child(body))


# ── Helia view · disposition indicator ────────────────────────
func _render_helia_view() -> void:
	_render_sub_view("HELIA · THE CAT", func(v: VBoxContainer) -> void:
		var recruited: Array = _run_state.get("recruited_feys", [])
		var intro := Label.new()
		intro.text = "Prospero's cat.  She never lets herself be petted.\n\nHer tail-flick indicates how each recruited fey feels about you:"
		intro.add_theme_font_size_override("font_size", 10)
		intro.add_theme_color_override("font_color", C_CREAM)
		intro.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		v.add_child(intro)

		var sep := Control.new()
		sep.custom_minimum_size = Vector2(0, 12)
		v.add_child(sep)

		if recruited.is_empty():
			var empty := Label.new()
			empty.text = "· no recruits to indicate ·  Helia is asleep on the writing desk ·"
			empty.add_theme_font_size_override("font_size", 10)
			empty.add_theme_color_override("font_color", C_GOLD_DIM)
			v.add_child(empty)
			return

		for id in recruited:
			var fey: Dictionary = _feys_by_id.get(String(id), {})
			if fey.is_empty(): continue
			var disp: int = int(_run_state.get("disposition", {}).get(String(id), 0))
			var flick: String = _tail_flick_for(disp)
			var row := Label.new()
			row.text = "· " + String(fey.get("name", id)) + " · " + flick
			row.add_theme_font_size_override("font_size", 11)
			row.add_theme_color_override("font_color", _tail_flick_color(disp))
			v.add_child(row))


func _tail_flick_for(disp: int) -> String:
	if disp >= 4:  return "tail slow left-to-right · fey LOVED"
	elif disp >= 1:return "tail still · fey LIKED"
	elif disp >= -1:return "tail still · fey NEUTRAL"
	elif disp >= -3:return "tail twitching · fey WARY"
	else:          return "cat hisses · fey HATED"


func _tail_flick_color(disp: int) -> Color:
	if disp >= 4:  return C_LAMP
	elif disp >= 1:return C_CREAM
	elif disp >= -1:return C_GOLD_DIM
	elif disp >= -3:return C_ROSE
	else:          return Color(0.75, 0.25, 0.25, 1.0)


# ── Sub-view frame helper ─────────────────────────────────────
func _render_sub_view(title: String, populator: Callable) -> void:
	_clear_panel()
	_panel_root = Control.new()
	_panel_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_panel_root.offset_top = 60
	_panel_root.offset_bottom = -20
	_panel_root.offset_left = 60
	_panel_root.offset_right = -60
	add_child(_panel_root)

	var bg := ColorRect.new()
	bg.color = C_WOOD
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_panel_root.add_child(bg)

	var header_row := HBoxContainer.new()
	header_row.set_anchors_preset(Control.PRESET_TOP_WIDE)
	header_row.offset_left = 12
	header_row.offset_right = -12
	header_row.offset_top = 8
	header_row.offset_bottom = 32
	_panel_root.add_child(header_row)

	var title_lbl := Label.new()
	title_lbl.text = "· " + title + " ·"
	title_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	title_lbl.add_theme_font_size_override("font_size", 13)
	title_lbl.add_theme_color_override("font_color", C_LAMP)
	header_row.add_child(title_lbl)

	var back_btn := Button.new()
	back_btn.text = "  ← back to trailer  "
	back_btn.add_theme_font_size_override("font_size", 10)
	back_btn.pressed.connect(_render_main_view)
	header_row.add_child(back_btn)

	var scroll := ScrollContainer.new()
	scroll.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scroll.offset_top = 40
	scroll.offset_bottom = -12
	scroll.offset_left = 12
	scroll.offset_right = -12
	_panel_root.add_child(scroll)

	var v := VBoxContainer.new()
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	v.add_theme_constant_override("separation", 6)
	scroll.add_child(v)

	populator.call(v)


func _on_back() -> void:
	quit.emit()


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			_on_back()
			get_viewport().set_input_as_handled()
