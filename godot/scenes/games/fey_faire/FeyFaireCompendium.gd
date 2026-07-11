extends Control
## Fey Faire · title-screen Compendium · Prospero's inventory ledger.
##
## Between-runs viewer accessible from the title.  Four tabs:
##
##   ENDINGS   · 7 endings · hidden endings shown as silhouettes
##               until seen (BRING BACK THE LOST + YOU FORGET WHY
##               YOU CAME)
##   FEYS      · 101 roster · grouped by court · marks
##               recruited/vanquished/met · else silhouette
##   KEEPSAKES · collected keepsakes from keepsakes.json with lore
##   MIRRORS   · six mirrors · walked/cracked marks · matches
##               the trailer's memory-mirror view but title-side
##
## Parallel to Earthman's Codex.  The Trailer is in-run; the
## Compendium is between-runs, so seen-endings + lifetime-recruited
## carry across multiple playthroughs when the save persists.
##
## F4-compliant via add_to_group("ui").

signal quit

const FEYS_PATH      := "res://resources/games/vol7/fey_faire/feys.json"
const KEEPSAKES_PATH := "res://resources/games/vol7/fey_faire/keepsakes.json"

# Rocha palette · muted for the ledger look
const C_BG        := Color(0.157, 0.094, 0.173, 1.0)
const C_PAPER     := Color(0.957, 0.878, 0.816, 1.0)
const C_PAPER_DIM := Color(0.72, 0.65, 0.60, 1.0)
const C_INK       := Color(0.196, 0.098, 0.157, 1.0)
const C_INK_FADED := Color(0.63, 0.45, 0.54, 1.0)
const C_ROSE      := Color(0.878, 0.361, 0.451, 1.0)
const C_MAUVE     := Color(0.87, 0.68, 0.76, 1.0)
const C_GOLD      := Color(0.973, 0.784, 0.282, 1.0)
const C_GOLD_DIM  := Color(0.72, 0.52, 0.26, 1.0)
const C_SEELIE    := Color(0.42, 0.62, 0.35, 1.0)
const C_UNSEELIE  := Color(0.55, 0.35, 0.68, 1.0)
const C_WILDFEY   := Color(0.82, 0.62, 0.35, 1.0)
const C_DIM       := Color(0.62, 0.53, 0.47, 1.0)

# Endings display metadata · order + hidden flag
const ENDING_META: Dictionary = {
	"a_rose":                 {"n": 1, "name": "A ROSE",              "subtitle": "the seelie ending",   "hidden": false},
	"a_red_cap":              {"n": 2, "name": "A RED CAP",           "subtitle": "the unseelie ending", "hidden": false},
	"a_stag_antler":          {"n": 3, "name": "A STAG'S ANTLER",     "subtitle": "the wildfey ending",  "hidden": false},
	"refused_the_faire":      {"n": 4, "name": "REFUSED THE FAIRE",   "subtitle": "you walked away",     "hidden": false},
	"become_the_faire":       {"n": 5, "name": "BECOME THE FAIRE",    "subtitle": "you take Cricket's seat", "hidden": true},
	"bring_back_the_lost":    {"n": 6, "name": "BRING BACK THE LOST", "subtitle": "$LOST_PERSON comes home", "hidden": true},
	"you_forget_why_you_came":{"n": 7, "name": "YOU FORGET WHY YOU CAME", "subtitle": "the Faire keeps you", "hidden": true}
}

const MIRROR_META: Array = [
	{"id": "mirror_1_rose_garden",  "n": 1, "name": "THE ROSE GARDEN",         "slot": "bedroom_description"},
	{"id": "mirror_2_storm_coast",  "n": 2, "name": "THE STORM-WRACKED COAST", "slot": "favorite_song"},
	{"id": "mirror_3_court_beneath","n": 3, "name": "THE COURT BENEATH",       "slot": "favorite_meal"},
	{"id": "mirror_4_the_green",    "n": 4, "name": "THE GREEN",               "slot": "holiday"},
	{"id": "mirror_5_undertide",    "n": 5, "name": "THE UNDERTIDE",           "slot": "parent_argument"},
	{"id": "mirror_6_dream",        "n": 6, "name": "THE DREAM",               "slot": "first_kiss"}
]

var _run_state: Dictionary = {}
var _feys: Array = []
var _keepsakes: Array = []
var _tab: String = "endings"
var _content_root: Control = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")


func boot(state: Dictionary) -> void:
	_run_state = state
	_load_data()
	_build_frame()
	_render_tab_content()


func _load_data() -> void:
	_feys = _load_array(FEYS_PATH, "feys")
	_keepsakes = _load_array(KEEPSAKES_PATH, "keepsakes")


func _load_array(path: String, key: String) -> Array:
	if not FileAccess.file_exists(path): return []
	var f := FileAccess.open(path, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		var arr: Variant = (parsed as Dictionary).get(key, [])
		if arr is Array:
			return arr
	return []


func _build_frame() -> void:
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# Tent-stripe hint · dim in compendium
	for x in range(60, 1280, 90):
		var stripe := ColorRect.new()
		stripe.color = Color(C_MAUVE.r, C_MAUVE.g, C_MAUVE.b, 0.35)
		stripe.set_anchors_preset(Control.PRESET_TOP_LEFT)
		stripe.position = Vector2(x, 0)
		stripe.size = Vector2(6, 40)
		add_child(stripe)

	# Paper ledger panel
	var paper := ColorRect.new()
	paper.color = C_PAPER
	paper.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	paper.offset_left = 40
	paper.offset_right = -40
	paper.offset_top = 60
	paper.offset_bottom = -60
	add_child(paper)

	var header := Label.new()
	header.text = "PROSPERO'S INVENTORY LEDGER · lifetime record"
	header.set_anchors_preset(Control.PRESET_TOP_WIDE)
	header.offset_left = 60
	header.offset_right = -60
	header.offset_top = 76
	header.offset_bottom = 100
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	header.add_theme_font_size_override("font_size", 16)
	header.add_theme_color_override("font_color", C_INK)
	add_child(header)

	# Tabs
	var tab_row := HBoxContainer.new()
	tab_row.set_anchors_preset(Control.PRESET_TOP_WIDE)
	tab_row.offset_left = 60
	tab_row.offset_right = -60
	tab_row.offset_top = 100
	tab_row.offset_bottom = 132
	tab_row.alignment = BoxContainer.ALIGNMENT_CENTER
	tab_row.add_theme_constant_override("separation", 4)
	add_child(tab_row)

	for tab_id in ["endings", "feys", "keepsakes", "mirrors"]:
		var btn := Button.new()
		btn.text = "  " + String(tab_id).to_upper() + _tab_count_string(String(tab_id)) + "  "
		btn.add_theme_font_size_override("font_size", 16)
		if _tab == String(tab_id):
			btn.add_theme_color_override("font_color", C_ROSE)
		else:
			btn.add_theme_color_override("font_color", C_INK_FADED)
		var t: String = String(tab_id)
		btn.pressed.connect(func() -> void: _set_tab(t))
		tab_row.add_child(btn)

	# Back button
	var back_btn := Button.new()
	back_btn.text = "  ← back to title  "
	back_btn.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	back_btn.position = Vector2(60, -46)
	back_btn.size = Vector2(180, 32)
	back_btn.add_theme_font_size_override("font_size", 16)
	back_btn.pressed.connect(_on_back_pressed)
	add_child(back_btn)


func _tab_count_string(tab_id: String) -> String:
	match tab_id:
		"endings":
			var seen: Array = _run_state.get("endings_seen", [])
			return " (" + str(seen.size()) + "/7)"
		"feys":
			var r: Array = _run_state.get("recruited_feys", [])
			return " (" + str(r.size()) + "/" + str(_feys.size()) + ")"
		"keepsakes":
			var k: Array = _run_state.get("keepsakes", [])
			return " (" + str(k.size()) + "/" + str(_keepsakes.size()) + ")"
		"mirrors":
			var m: Array = _run_state.get("mirrors_completed", [])
			return " (" + str(m.size()) + "/6)"
	return ""


func _set_tab(tab_id: String) -> void:
	_tab = tab_id
	for c in get_children():
		c.queue_free()
	_content_root = null
	_build_frame()
	_render_tab_content()


func _render_tab_content() -> void:
	if _content_root != null and is_instance_valid(_content_root):
		_content_root.queue_free()
	_content_root = Control.new()
	_content_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_content_root.offset_left = 80
	_content_root.offset_right = -80
	_content_root.offset_top = 140
	_content_root.offset_bottom = -76
	add_child(_content_root)

	var scroll := ScrollContainer.new()
	scroll.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	_content_root.add_child(scroll)

	var v := VBoxContainer.new()
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	v.add_theme_constant_override("separation", 8)
	scroll.add_child(v)

	match _tab:
		"endings":   _render_endings_tab(v)
		"feys":      _render_feys_tab(v)
		"keepsakes": _render_keepsakes_tab(v)
		"mirrors":   _render_mirrors_tab(v)


# ── Endings tab ─────────────────────────────────────────────────

func _render_endings_tab(v: VBoxContainer) -> void:
	var seen: Array = _run_state.get("endings_seen", [])

	var header := Label.new()
	header.text = "ENDINGS · " + str(seen.size()) + " of 7 seen"
	header.add_theme_font_size_override("font_size", 17)
	header.add_theme_color_override("font_color", C_INK)
	v.add_child(header)

	var order: Array = ["a_rose", "a_red_cap", "a_stag_antler", "refused_the_faire", "become_the_faire", "bring_back_the_lost", "you_forget_why_you_came"]
	for eid in order:
		var meta: Dictionary = ENDING_META.get(eid, {})
		var got: bool = seen.has(String(eid))
		var hidden: bool = bool(meta.get("hidden", false)) and not got

		var entry := VBoxContainer.new()
		entry.add_theme_constant_override("separation", 1)
		v.add_child(entry)

		var name_lbl := Label.new()
		var mark: String = "✓  " if got else "·  "
		if hidden:
			name_lbl.text = "·  #" + str(int(meta.get("n", 0))) + " · ? · ? · ?"
			name_lbl.add_theme_color_override("font_color", C_PAPER_DIM)
		else:
			name_lbl.text = mark + "#" + str(int(meta.get("n", 0))) + " · " + String(meta.get("name", ""))
			name_lbl.add_theme_color_override("font_color", C_INK if got else C_INK_FADED)
		name_lbl.add_theme_font_size_override("font_size", 16)
		entry.add_child(name_lbl)

		if not hidden:
			var sub := Label.new()
			sub.text = "    · " + String(meta.get("subtitle", "")) + " ·"
			sub.add_theme_font_size_override("font_size", 13)
			sub.add_theme_color_override("font_color", C_INK_FADED)
			entry.add_child(sub)


# ── Feys tab ────────────────────────────────────────────────────

func _render_feys_tab(v: VBoxContainer) -> void:
	var recruited: Array = _run_state.get("recruited_feys", [])
	var vanquished: Array = _run_state.get("vanquished_feys", [])
	var met: Array = _run_state.get("feys_met", [])

	# Group by court
	var by_court: Dictionary = {"seelie": [], "unseelie": [], "wildfey": [], "other": []}
	for f_v in _feys:
		var f: Dictionary = f_v
		var court: String = String(f.get("court", "other"))
		if not by_court.has(court):
			by_court["other"].append(f)
		else:
			by_court[court].append(f)

	for court_id in ["seelie", "unseelie", "wildfey", "other"]:
		var arr: Array = by_court[court_id]
		if arr.is_empty(): continue
		var section := Label.new()
		section.text = "· " + String(court_id).to_upper() + " · " + str(arr.size()) + " known"
		section.add_theme_font_size_override("font_size", 16)
		section.add_theme_color_override("font_color", _court_color(String(court_id)))
		v.add_child(section)

		for f_v2 in arr:
			var f: Dictionary = f_v2
			var f_id: String = String(f.get("id", ""))
			var got_recruit: bool = recruited.has(f_id)
			var got_vanq: bool = vanquished.has(f_id)
			var got_met: bool = met.has(f_id)
			var known: bool = got_recruit or got_vanq or got_met

			var line := Label.new()
			var mark: String
			if got_recruit: mark = "✦"
			elif got_vanq:  mark = "✕"
			elif got_met:   mark = "·"
			else:           mark = " "
			var name_text: String
			if known:
				name_text = "  " + mark + " " + String(f.get("name", f_id)) + " · tier " + str(int(f.get("tier", 1)))
			else:
				name_text = "     · not yet met ·"
			line.text = name_text
			line.add_theme_font_size_override("font_size", 14)
			if got_recruit: line.add_theme_color_override("font_color", C_GOLD)
			elif got_vanq:  line.add_theme_color_override("font_color", C_ROSE)
			elif got_met:   line.add_theme_color_override("font_color", C_INK)
			else:           line.add_theme_color_override("font_color", C_PAPER_DIM)
			v.add_child(line)


func _court_color(c: String) -> Color:
	match c:
		"seelie":   return C_SEELIE
		"unseelie": return C_UNSEELIE
		"wildfey":  return C_WILDFEY
	return C_INK_FADED


# ── Keepsakes tab ───────────────────────────────────────────────

func _render_keepsakes_tab(v: VBoxContainer) -> void:
	var collected: Array = _run_state.get("keepsakes", [])

	var header := Label.new()
	header.text = "KEEPSAKES · " + str(collected.size()) + " of " + str(_keepsakes.size()) + " in the bookcase"
	header.add_theme_font_size_override("font_size", 17)
	header.add_theme_color_override("font_color", C_INK)
	v.add_child(header)

	# Only show collected ones · unseen would spoil
	for kp_v in _keepsakes:
		var kp: Dictionary = kp_v
		var kp_id: String = String(kp.get("id", ""))
		var got: bool = collected.has(kp_id)
		if not got: continue

		var entry := VBoxContainer.new()
		entry.add_theme_constant_override("separation", 1)
		v.add_child(entry)

		var name_lbl := Label.new()
		name_lbl.text = "✓  " + String(kp.get("name", kp_id))
		name_lbl.add_theme_font_size_override("font_size", 16)
		name_lbl.add_theme_color_override("font_color", C_INK)
		entry.add_child(name_lbl)

		var lore: String = String(kp.get("lore", kp.get("description", "")))
		if lore != "":
			var lore_lbl := Label.new()
			lore_lbl.text = "    " + lore.left(160) + (" ..." if lore.length() > 160 else "")
			lore_lbl.add_theme_font_size_override("font_size", 13)
			lore_lbl.add_theme_color_override("font_color", C_INK_FADED)
			lore_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			entry.add_child(lore_lbl)

		var effect: String = String(kp.get("effect", ""))
		if effect != "":
			var eff_lbl := Label.new()
			eff_lbl.text = "    · " + effect + " ·"
			eff_lbl.add_theme_font_size_override("font_size", 13)
			eff_lbl.add_theme_color_override("font_color", C_ROSE)
			eff_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			entry.add_child(eff_lbl)

	if collected.is_empty():
		var empty := Label.new()
		empty.text = "· no keepsakes yet · every recruit and every mirror leaves one ·"
		empty.add_theme_font_size_override("font_size", 14)
		empty.add_theme_color_override("font_color", C_INK_FADED)
		v.add_child(empty)


# ── Mirrors tab ─────────────────────────────────────────────────

func _render_mirrors_tab(v: VBoxContainer) -> void:
	var completed: Array = _run_state.get("mirrors_completed", [])
	var lost: int = int(_run_state.get("memories_lost", 0))

	var header := Label.new()
	header.text = "MEMORY MIRRORS · " + str(completed.size()) + " of 6 walked"
	header.add_theme_font_size_override("font_size", 17)
	header.add_theme_color_override("font_color", C_INK)
	v.add_child(header)

	for i in range(MIRROR_META.size()):
		var mm: Dictionary = MIRROR_META[i]
		var mid: String = String(mm.get("id", ""))
		var done: bool = completed.has(mid)
		var cracked: bool = i < lost

		var entry := VBoxContainer.new()
		entry.add_theme_constant_override("separation", 1)
		v.add_child(entry)

		var name_lbl := Label.new()
		var mark: String
		if cracked: mark = "✕"
		elif done:  mark = "✓"
		else:       mark = "·"
		name_lbl.text = mark + "  #" + str(int(mm.get("n", 0))) + " · " + String(mm.get("name", "")) + (" · CRACKED" if cracked else "")
		name_lbl.add_theme_font_size_override("font_size", 16)
		if cracked: name_lbl.add_theme_color_override("font_color", C_ROSE)
		elif done:  name_lbl.add_theme_color_override("font_color", C_INK)
		else:       name_lbl.add_theme_color_override("font_color", C_INK_FADED)
		entry.add_child(name_lbl)

		var sub := Label.new()
		sub.text = "    · slot: " + String(mm.get("slot", "")) + " ·"
		sub.add_theme_font_size_override("font_size", 13)
		sub.add_theme_color_override("font_color", C_INK_FADED)
		entry.add_child(sub)

	if bool(_run_state.get("mirror_4_the_green_completed", false)):
		var note := Label.new()
		note.text = "· mirror 4 completed · BRING BACK THE LOST is available at the final gate ·"
		note.add_theme_font_size_override("font_size", 14)
		note.add_theme_color_override("font_color", C_GOLD)
		note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		v.add_child(note)


func _on_back_pressed() -> void:
	quit.emit()


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			_on_back_pressed()
			get_viewport().set_input_as_handled()
