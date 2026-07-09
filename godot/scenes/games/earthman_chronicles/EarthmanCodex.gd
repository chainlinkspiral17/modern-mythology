extends Control
## Earthman Chronicles · Jack's Codex · title-screen notebook.
##
## A read-only view of everything the current save has accumulated:
##
##   TAB · WORKINGS      · nine ritual entries · marks ones performed
##   TAB · CORRECTIONS   · six document entries · marks ones found
##                         (found ones show their actual text)
##   TAB · NPCS          · people met + their current disposition
##   TAB · ENDINGS       · endings seen · TRUE ending hidden until got
##
## The Codex is title-screen-accessible so a player can flip through
## Jack's notebook between runs to see what they collected and what
## paths are still ahead.  Also emits back-to-title on close.
##
## F4-compliant via add_to_group("ui").

signal quit

const WORKINGS_PATH   := "res://resources/games/vol7/earthman_chronicles/workings.json"
const CORRECTIONS_PATH := "res://resources/games/vol7/earthman_chronicles/corrections.json"
const NPCS_PATH       := "res://resources/games/vol7/earthman_chronicles/npcs.json"
const MANUSCRIPT_PATH := "res://resources/games/vol7/earthman_chronicles/manuscript.json"

# Astro-Cortex palette · matches the title screen's tone
const C_BG           := Color(0.094, 0.094, 0.157, 1.0)
const C_CORTEX       := Color(0.345, 0.188, 0.376, 1.0)
const C_PAPER        := Color(0.851, 0.788, 0.702, 1.0)   # aged notebook page
const C_PAPER_DIM    := Color(0.545, 0.502, 0.451, 1.0)
const C_INK          := Color(0.196, 0.137, 0.098, 1.0)   # brown notebook ink
const C_INK_FADED    := Color(0.451, 0.373, 0.294, 1.0)
const C_AMBER        := Color(0.784, 0.376, 0.125, 1.0)
const C_GREEN        := Color(0.0, 0.753, 0.376, 1.0)
const C_RED          := Color(0.753, 0.125, 0.125, 1.0)
const C_STAR         := Color(0.973, 0.784, 0.282, 1.0)
const C_WHITE        := Color(0.941, 0.941, 0.941, 1.0)
const C_GRAY         := Color(0.282, 0.282, 0.314, 1.0)
const C_DIM          := Color(0.545, 0.463, 0.302, 1.0)

# Endings authored in Ch6 · id → display metadata
const ENDING_META: Dictionary = {
	"warlord_of_parsa":         {"n": 1, "name": "THE WARLORD OF PARSA",         "subtitle": "someone has to sit on that throne", "hidden": false},
	"return_to_earth":          {"n": 2, "name": "RETURN TO EARTH",              "subtitle": "Parsons dies anyway",              "hidden": false},
	"babalon_comes":            {"n": 3, "name": "BABALON COMES",                "subtitle": "as foretold",                       "hidden": false},
	"refused_the_work":         {"n": 4, "name": "REFUSED THE WORK",             "subtitle": "the most beautiful life he ever lived", "hidden": false},
	"the_correction":           {"n": 5, "name": "THE CORRECTION",               "subtitle": "the manuscript completes itself",  "hidden": true},
	"hubbard_takes_the_credit": {"n": 6, "name": "HUBBARD TAKES THE CREDIT",     "subtitle": "see above",                         "hidden": false}
}

var _run_state: Dictionary = {}
var _workings: Array = []
var _corrections: Array = []
var _npcs: Array = []
var _manuscript: Dictionary = {}
var _tab: String = "workings"
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
	_workings = _load_array(WORKINGS_PATH, "workings")
	_corrections = _load_array(CORRECTIONS_PATH, "corrections")
	_npcs = _load_array(NPCS_PATH, "npcs")
	if FileAccess.file_exists(MANUSCRIPT_PATH):
		var mf := FileAccess.open(MANUSCRIPT_PATH, FileAccess.READ)
		var mparsed: Variant = JSON.parse_string(mf.get_as_text())
		mf.close()
		if mparsed is Dictionary:
			_manuscript = mparsed


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


	# HUD bands
	var hud_top := ColorRect.new()
	hud_top.color = C_GRAY
	hud_top.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	hud_top.offset_top = 0
	hud_top.offset_bottom = 24
	add_child(hud_top)

	var hud_top_text := Label.new()
	hud_top_text.text = "JACK'S CODEX · notebook, pasadena, 1946+"
	hud_top_text.set_anchors_preset(Control.PRESET_TOP_LEFT)
	hud_top_text.position = Vector2(12, 6)
	hud_top_text.add_theme_font_size_override("font_size", 14)
	hud_top_text.add_theme_color_override("font_color", C_AMBER)
	add_child(hud_top_text)

	var chapter_lbl := Label.new()
	chapter_lbl.text = "CHAPTER " + str(int(_run_state.get("chapter", 1))) + " · save loaded"
	chapter_lbl.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	chapter_lbl.position = Vector2(-220, 6)
	chapter_lbl.add_theme_font_size_override("font_size", 14)
	chapter_lbl.add_theme_color_override("font_color", C_STAR)
	add_child(chapter_lbl)

	# Notebook-paper panel
	var paper := ColorRect.new()
	paper.color = C_PAPER
	paper.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	paper.offset_left = 40
	paper.offset_right = -40
	paper.offset_top = 40
	paper.offset_bottom = -64
	add_child(paper)

	# Ruled lines · faded amber
	for y in range(120, 680, 24):
		var rule := ColorRect.new()
		rule.color = Color(C_AMBER.r, C_AMBER.g, C_AMBER.b, 0.15)
		rule.set_anchors_preset(Control.PRESET_TOP_LEFT)
		rule.position = Vector2(60, y)
		rule.size = Vector2(1200, 1)
		add_child(rule)

	# Left margin line
	var margin := ColorRect.new()
	margin.color = Color(C_RED.r, C_RED.g, C_RED.b, 0.35)
	margin.set_anchors_preset(Control.PRESET_TOP_LEFT)
	margin.position = Vector2(120, 60)
	margin.size = Vector2(1, 600)
	add_child(margin)

	# Tab bar
	var tab_row := HBoxContainer.new()
	tab_row.set_anchors_preset(Control.PRESET_TOP_WIDE)
	tab_row.offset_left = 60
	tab_row.offset_right = -60
	tab_row.offset_top = 60
	tab_row.offset_bottom = 96
	tab_row.alignment = BoxContainer.ALIGNMENT_CENTER
	tab_row.add_theme_constant_override("separation", 4)
	add_child(tab_row)

	for tab_id in ["workings", "corrections", "npcs", "endings", "manuscript"]:
		var btn := Button.new()
		var count_str: String = _tab_count_string(String(tab_id))
		btn.text = "  " + String(tab_id).to_upper() + count_str + "  "
		btn.add_theme_font_size_override("font_size", 16)
		if _tab == String(tab_id):
			btn.add_theme_color_override("font_color", C_STAR)
		else:
			btn.add_theme_color_override("font_color", C_INK_FADED)
		var t: String = String(tab_id)
		btn.pressed.connect(func() -> void: _set_tab(t))
		tab_row.add_child(btn)

	# Back button
	var back_btn := Button.new()
	back_btn.text = "  ← back to title  "
	back_btn.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	back_btn.position = Vector2(60, -50)
	back_btn.size = Vector2(180, 34)
	back_btn.add_theme_font_size_override("font_size", 16)
	back_btn.pressed.connect(_on_back_pressed)
	add_child(back_btn)


func _tab_count_string(tab_id: String) -> String:
	match tab_id:
		"workings":
			var wc: Array = _run_state.get("workings_completed", [])
			return " (" + str(wc.size()) + "/" + str(_workings.size()) + ")"
		"corrections":
			var cf: Array = _run_state.get("corrections_found", [])
			return " (" + str(cf.size()) + "/6)"
		"npcs":
			var met: Array = _run_state.get("npcs_met", [])
			return " (" + str(met.size()) + ")"
		"endings":
			var seen: Array = _run_state.get("endings_seen", [])
			return " (" + str(seen.size()) + "/6)"
		"manuscript":
			var ch: int = int(_run_state.get("chapter", 1))
			return " (" + str(clampi(ch, 0, 6)) + "/6)"
	return ""


func _set_tab(tab_id: String) -> void:
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("page_turn", 0.5)
	_tab = tab_id
	# Rebuild the frame to refresh tab highlight
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
	_content_root.offset_left = 140
	_content_root.offset_right = -80
	_content_root.offset_top = 108
	_content_root.offset_bottom = -80
	add_child(_content_root)

	var scroll := ScrollContainer.new()
	scroll.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	_content_root.add_child(scroll)

	var v := VBoxContainer.new()
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	v.add_theme_constant_override("separation", 10)
	scroll.add_child(v)

	match _tab:
		"workings":    _render_workings_tab(v)
		"corrections": _render_corrections_tab(v)
		"npcs":        _render_npcs_tab(v)
		"endings":     _render_endings_tab(v)
		"manuscript":  _render_manuscript_tab(v)


# ── Workings tab ────────────────────────────────────────────────

func _render_workings_tab(v: VBoxContainer) -> void:
	var completed: Array = _run_state.get("workings_completed", [])

	var header := Label.new()
	header.text = "TABLE OF WORKINGS · " + str(completed.size()) + " of " + str(_workings.size()) + " performed"
	header.add_theme_font_size_override("font_size", 18)
	header.add_theme_color_override("font_color", C_INK)
	v.add_child(header)

	for w_v in _workings:
		var w: Dictionary = w_v
		var w_id: String = String(w.get("id", ""))
		var done: bool = completed.has(w_id)
		var entry := VBoxContainer.new()
		entry.add_theme_constant_override("separation", 2)
		v.add_child(entry)

		var name_lbl := Label.new()
		var mark: String = "✓  " if done else "·  "
		name_lbl.text = mark + String(w.get("roman", "?")) + " · " + String(w.get("name", ""))
		name_lbl.add_theme_font_size_override("font_size", 16)
		name_lbl.add_theme_color_override("font_color", C_INK if done else C_INK_FADED)
		entry.add_child(name_lbl)

		var desc := RichTextLabel.new()
		desc.bbcode_enabled = false
		desc.fit_content = true
		desc.text = "    " + String(w.get("description", ""))
		desc.add_theme_font_size_override("normal_font_size", 14)
		desc.add_theme_color_override("default_color", C_INK if done else C_INK_FADED)
		desc.custom_minimum_size = Vector2(0, 34)
		entry.add_child(desc)

		if done:
			var effect := Label.new()
			effect.text = "    · effect · " + String(w.get("unlock_effect", ""))
			effect.add_theme_font_size_override("font_size", 13)
			effect.add_theme_color_override("font_color", C_AMBER)
			effect.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			entry.add_child(effect)


# ── Corrections tab ─────────────────────────────────────────────

func _render_corrections_tab(v: VBoxContainer) -> void:
	var found: Array = _run_state.get("corrections_found", [])

	var header := Label.new()
	header.text = "CORRECTIONS · " + str(found.size()) + " of 6 · left in the ROM by A.R. and J.F."
	header.add_theme_font_size_override("font_size", 18)
	header.add_theme_color_override("font_color", C_INK)
	v.add_child(header)

	var sub := Label.new()
	sub.text = "find the five findable · refuse Working IX · the sixth finds you"
	sub.add_theme_font_size_override("font_size", 13)
	sub.add_theme_color_override("font_color", C_INK_FADED)
	v.add_child(sub)

	for c_v in _corrections:
		var c: Dictionary = c_v
		var c_id: String = String(c.get("id", ""))
		var got: bool = found.has(c_id)
		var entry := VBoxContainer.new()
		entry.add_theme_constant_override("separation", 2)
		v.add_child(entry)

		var name_lbl := Label.new()
		var mark: String = "✓  " if got else "·  "
		name_lbl.text = mark + "#" + str(int(c.get("number", 0))) + " · " + String(c.get("name", ""))
		name_lbl.add_theme_font_size_override("font_size", 16)
		name_lbl.add_theme_color_override("font_color", C_INK if got else C_INK_FADED)
		entry.add_child(name_lbl)

		if got:
			var src := Label.new()
			src.text = "    source · " + String(c.get("source", "")).left(90)
			src.add_theme_font_size_override("font_size", 13)
			src.add_theme_color_override("font_color", C_INK_FADED)
			src.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			entry.add_child(src)

			# Show the actual body if the JSON carries a `body` or `document_text` field
			var body_text: String = String(c.get("document_text", c.get("body", c.get("text", ""))))
			if body_text != "":
				var body := RichTextLabel.new()
				body.bbcode_enabled = false
				body.fit_content = true
				var trimmed: String = body_text.substr(0, min(body_text.length(), 500))
				body.text = "    " + trimmed + (" ..." if body_text.length() > 500 else "")
				body.add_theme_font_size_override("normal_font_size", 14)
				body.add_theme_color_override("default_color", C_INK)
				body.custom_minimum_size = Vector2(0, 60)
				entry.add_child(body)
		else:
			var hint := Label.new()
			hint.text = "    · not yet found ·"
			hint.add_theme_font_size_override("font_size", 13)
			hint.add_theme_color_override("font_color", C_PAPER_DIM)
			entry.add_child(hint)


# ── NPCs tab ────────────────────────────────────────────────────

func _render_npcs_tab(v: VBoxContainer) -> void:
	var met: Array = _run_state.get("npcs_met", [])
	# Fall back: if npcs_met is empty, infer from party_members + chapter progress.
	var party: Array = _run_state.get("party_members", ["jack"])

	var header := Label.new()
	header.text = "PEOPLE · met so far"
	header.add_theme_font_size_override("font_size", 18)
	header.add_theme_color_override("font_color", C_INK)
	v.add_child(header)

	for n_v in _npcs:
		var n: Dictionary = n_v
		var n_id: String = String(n.get("id", ""))
		var is_met: bool = met.has(n_id) or party.has(n_id) or _implicitly_met(n_id)
		if not is_met: continue
		var entry := VBoxContainer.new()
		entry.add_theme_constant_override("separation", 1)
		v.add_child(entry)

		var name_lbl := Label.new()
		var in_party: bool = party.has(n_id)
		var mark: String = "✦ " if in_party else "· "
		name_lbl.text = mark + String(n.get("name", n_id))
		name_lbl.add_theme_font_size_override("font_size", 16)
		name_lbl.add_theme_color_override("font_color", C_STAR if in_party else C_INK)
		entry.add_child(name_lbl)

		var role: String = String(n.get("role", n.get("species", "")))
		if role != "":
			var role_lbl := Label.new()
			role_lbl.text = "    " + role
			role_lbl.add_theme_font_size_override("font_size", 13)
			role_lbl.add_theme_color_override("font_color", C_INK_FADED)
			entry.add_child(role_lbl)

		var disp: int = int(_run_state.get(n_id + "_disposition", 0))
		if disp != 0:
			var disp_lbl := Label.new()
			var word: String = _disposition_word(disp)
			disp_lbl.text = "    · " + word + " (" + ("+" if disp > 0 else "") + str(disp) + ") ·"
			disp_lbl.add_theme_font_size_override("font_size", 13)
			disp_lbl.add_theme_color_override("font_color", C_AMBER if disp > 0 else C_RED)
			entry.add_child(disp_lbl)


func _implicitly_met(npc_id: String) -> bool:
	# Chapter-progress-derived implicit meets · saves us needing every scene
	# to record npcs_met explicitly.
	var ch: int = int(_run_state.get("chapter", 1))
	match npc_id:
		"jack": return true
		"rafaton", "cameron", "helen_parsons": return true      # Ch1
		"hel_velli": return ch >= 2
		"sara_nai": return ch >= 3
		"mother_kanel", "yr", "thar_krai_tam", "dalev": return ch >= 4
		"rocha": return ch >= 4 and bool(_run_state.get("rocha_recruited", false))
		"nalat", "ronson", "scarlet_woman": return ch >= 5
	return false


func _disposition_word(v: int) -> String:
	if v >= 5: return "LOVED"
	if v >= 3: return "LIKED"
	if v >= 1: return "friendly"
	if v == 0: return "neutral"
	if v >= -2: return "distant"
	if v >= -4: return "wary"
	return "HOSTILE"


# ── Endings tab ─────────────────────────────────────────────────

func _render_endings_tab(v: VBoxContainer) -> void:
	var seen: Array = _run_state.get("endings_seen", [])

	var header := Label.new()
	header.text = "ENDINGS · " + str(seen.size()) + " of 6 seen"
	header.add_theme_font_size_override("font_size", 18)
	header.add_theme_color_override("font_color", C_INK)
	v.add_child(header)

	var sub := Label.new()
	sub.text = "the TRUE ending is hidden until achieved"
	sub.add_theme_font_size_override("font_size", 13)
	sub.add_theme_color_override("font_color", C_INK_FADED)
	v.add_child(sub)

	# Iterate in canonical order (1-6)
	var order: Array = ["warlord_of_parsa", "return_to_earth", "babalon_comes", "refused_the_work", "the_correction", "hubbard_takes_the_credit"]
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
			var sub_lbl := Label.new()
			sub_lbl.text = "    · " + String(meta.get("subtitle", "")) + " ·"
			sub_lbl.add_theme_font_size_override("font_size", 13)
			sub_lbl.add_theme_color_override("font_color", C_INK_FADED)
			entry.add_child(sub_lbl)


# ── Manuscript tab · Hubbard's version beside Rocha's ──────────

func _render_manuscript_tab(v: VBoxContainer) -> void:
	var ch: int = int(_run_state.get("chapter", 1))

	var header := Label.new()
	header.text = "THE PROPHET OF THE RED WORLD · Hubbard, 1948, unsent · Rocha's copy"
	header.add_theme_font_size_override("font_size", 17)
	header.add_theme_color_override("font_color", C_INK)
	v.add_child(header)

	var sub := Label.new()
	sub.text = "typescript in ink · marginalia in blue · pages unlock as the game adapts them"
	sub.add_theme_font_size_override("font_size", 13)
	sub.add_theme_color_override("font_color", C_INK_FADED)
	v.add_child(sub)

	var rocha_blue := Color(0.35, 0.42, 0.72, 1.0)

	# Front matter · visible from chapter 2 (once Jack is on Parsa)
	if ch >= 2:
		for fm_v in _manuscript.get("front_matter", []):
			var fm: Dictionary = fm_v
			_add_manuscript_page(v, String(fm.get("heading", "")), String(fm.get("typescript", "")), String(fm.get("marginalia", "")), rocha_blue)

	# Chapter excerpts · entry N unlocks when game chapter > N (adapted)
	for c_v in _manuscript.get("chapters", []):
		var c: Dictionary = c_v
		var gc: int = int(c.get("game_chapter", 1))
		if ch > gc or (ch == 6 and gc == 6):
			_add_manuscript_page(v, "MS. " + String(c.get("covers", "")), String(c.get("typescript", "")), String(c.get("marginalia", "")), rocha_blue)
		else:
			var locked := Label.new()
			locked.text = "·  [MS. " + String(c.get("covers", "")) + " · the game has not adapted this yet]"
			locked.add_theme_font_size_override("font_size", 14)
			locked.add_theme_color_override("font_color", C_PAPER_DIM)
			v.add_child(locked)

	# Endpaper · only after THE CORRECTION
	var ep: Dictionary = _manuscript.get("endpaper", {})
	if OneironauticsTokens.has(String(ep.get("requires_token", "earthman_correction_ending_seen"))):
		_add_manuscript_page(v, String(ep.get("heading", "ENDPAPER")), "", String(ep.get("marginalia", "for jack")), rocha_blue)
	else:
		var ep_locked := Label.new()
		ep_locked.text = "·  [the endpaper is blank.  for now.]"
		ep_locked.add_theme_font_size_override("font_size", 14)
		ep_locked.add_theme_color_override("font_color", C_PAPER_DIM)
		v.add_child(ep_locked)


func _add_manuscript_page(v: VBoxContainer, heading: String, typescript: String, marginalia: String, blue: Color) -> void:
	var hdr := Label.new()
	hdr.text = "— " + heading + " —"
	hdr.add_theme_font_size_override("font_size", 15)
	hdr.add_theme_color_override("font_color", C_INK)
	v.add_child(hdr)

	if typescript != "":
		var ts := RichTextLabel.new()
		ts.bbcode_enabled = false
		ts.fit_content = true
		ts.text = typescript
		ts.add_theme_font_size_override("normal_font_size", 14)
		ts.add_theme_color_override("default_color", C_INK)
		ts.custom_minimum_size = Vector2(0, 40)
		v.add_child(ts)

	if marginalia != "":
		var mg := RichTextLabel.new()
		mg.bbcode_enabled = false
		mg.fit_content = true
		mg.text = "✎ " + marginalia
		mg.add_theme_font_size_override("normal_font_size", 14)
		mg.add_theme_color_override("default_color", blue)
		mg.custom_minimum_size = Vector2(0, 30)
		v.add_child(mg)

	var gap := Control.new()
	gap.custom_minimum_size = Vector2(0, 8)
	v.add_child(gap)


func _on_back_pressed() -> void:
	quit.emit()


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			_on_back_pressed()
			get_viewport().set_input_as_handled()
