extends Control
## Act 3 controller · Labor Day walkabout across nine town locations.
##
## Loads:  res://resources/games/vol7/estuary_3/act3_town.json
##
## Contract with Estuary3Host:
##   - Host instantiates TownWalkabout, then calls `boot(host_state)`
##     with the accumulated canon_vars (esp. estuary_3_act2_final).
##   - When the walkabout ends (return to Kwik Stop OR clock hits
##     19:30), TownWalkabout resolves the three-branch Jules
##     ending and emits `act3_finished(canon_vars, locations_visited)`.
##     Host merges canon_vars and advances to act4_fifth.
##
## This commit builds:
##   - Two views · Hub (nine-location grid + clock + opening
##     narration) and Location (procedural hero-image placeholder
##     + hotspot list + verb sub-actions).
##   - Clock cost of 15 minutes per visited location, from 08:32
##     to hard-stop 19:30. Location revisits allowed.
##   - Hotspot gates on prerequisite flags (e.g. the bookstore's
##     back-door-key needs the side-alley visited first).
##   - Return-to-Kwik-Stop button surfaces after clock passes
##     18:00 OR after any location is visited (whichever), lands
##     the three-branch Jules ending based on
##     canon_vars.estuary_3_act2_final.
##
## Per the per-act visual-language design (Act 3 = vector-style
## hero images), the hero-image panel is a procedural composition
## of flat-color rects that suggest each location. Real hero-image
## art can override any location by dropping a PNG at
## `sprites/act3/<location_id>.png`. Not yet implemented — this
## commit ships the procedural placeholder.
##
## F4-compliant via add_to_group("ui").

signal act3_finished(canon_vars: Dictionary, locations_visited: Array)
signal quit_to_shelf

const ACT3_JSON := "res://resources/games/vol7/estuary_3/act3_town.json"

const HERO_W := 640
const HERO_H := 360
const HUB_TILE_W := 200
const HUB_TILE_H := 96

const C_BG        := Color(0.024, 0.020, 0.014, 0.97)
const C_ACCENT    := Color(0.78, 0.66, 0.29, 1.00)
const C_TXT       := Color(0.83, 0.79, 0.69, 1.00)
const C_TXT_DIM   := Color(0.50, 0.47, 0.38, 1.00)
const C_TILE      := Color(0.14, 0.18, 0.22, 1.00)
const C_TILE_VIS  := Color(0.22, 0.24, 0.20, 1.00)
const C_TILE_HOV  := Color(0.24, 0.22, 0.16, 1.00)
const C_HOTSPOT   := Color(0.62, 0.55, 0.42, 0.95)

# Per-location hero palettes (rough compositional tints). Each
# location's hero panel uses three color bands for a chunky flat-
# color line-art look. Deliberately abstract; real art overrides
# via `sprites/act3/<id>.png` in the follow-up commit.
const HERO_PALETTES := {
	"kwik_stop_revisit":  [Color(0.34, 0.36, 0.32), Color(0.66, 0.60, 0.44), Color(0.92, 0.84, 0.42)],
	"shell_station":      [Color(0.20, 0.20, 0.24), Color(0.55, 0.32, 0.22), Color(0.85, 0.78, 0.28)],
	"pier":               [Color(0.34, 0.44, 0.52), Color(0.60, 0.66, 0.68), Color(0.88, 0.86, 0.72)],
	"mill_office":        [Color(0.16, 0.14, 0.10), Color(0.42, 0.36, 0.24), Color(0.72, 0.60, 0.34)],
	"bookstore":          [Color(0.28, 0.20, 0.16), Color(0.72, 0.58, 0.42), Color(0.94, 0.88, 0.72)],
	"aandahl_house":      [Color(0.55, 0.62, 0.66), Color(0.62, 0.72, 0.62), Color(0.90, 0.82, 0.62)],
	"elementary_school":  [Color(0.42, 0.44, 0.36), Color(0.62, 0.66, 0.48), Color(0.86, 0.84, 0.66)],
	"tide_gate":          [Color(0.24, 0.30, 0.36), Color(0.42, 0.48, 0.50), Color(0.66, 0.70, 0.68)],
	"cabin_road":         [Color(0.16, 0.20, 0.14), Color(0.30, 0.36, 0.24), Color(0.58, 0.52, 0.36)],
}

# Loaded data
var _def: Dictionary = {}
var _locations: Array = []

# Session state
var _canon_vars: Dictionary = {}
var _visited: Array = []                # location ids in visit order
var _clock_minutes: int = 512           # 08:32 default
var _clock_cost_per_visit: int = 15
var _clock_end_minutes: int = 1170      # 19:30 hard-stop
var _pending_view: String = "hub"       # "hub" | "location:<id>"
var _flags: Dictionary = {}             # gate flags for hotspot prerequisites

# UI refs
var _view_container: Control = null
var _clock_label: Label = null
var _ended: bool = false


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	_load_def()
	_build_ui()


func boot(host_state: Dictionary) -> void:
	# Read the Act 2 final canon-var so the ending can branch.
	var cv: Variant = host_state.get("canon_vars", {})
	_canon_vars = cv.duplicate(true) if cv is Dictionary else {}
	_visited.clear()
	_flags.clear()
	_ended = false
	var clock: Dictionary = _def.get("clock", {})
	_clock_minutes = _hhmm_to_minutes(String(clock.get("starts_at", "08:32")))
	_clock_cost_per_visit = int(clock.get("location_visit_costs_minutes", 15))
	_clock_end_minutes = _hhmm_to_minutes(String(clock.get("ends_at", "19:30")))
	AudioMgr.play_bgm("res://assets/audio/bgm/e3/act3_town_morning.wav")
	_show_hub()


# ─── Data ────────────────────────────────────────────────────────

func _load_def() -> void:
	if not FileAccess.file_exists(ACT3_JSON):
		push_warning("[TownWalkabout] missing %s" % ACT3_JSON)
		return
	var f := FileAccess.open(ACT3_JSON, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		_def = parsed
		_locations = _def.get("locations", [])


func _hhmm_to_minutes(hhmm: String) -> int:
	var parts := hhmm.split(":")
	if parts.size() < 2:
		return 512
	return int(parts[0]) * 60 + int(parts[1])


func _minutes_to_hhmm(m: int) -> String:
	var hh := int(m / 60)
	var mm := int(m % 60)
	return "%02d:%02d" % [hh, mm]


# ─── UI build ────────────────────────────────────────────────────

func _build_ui() -> void:
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# Top status bar
	var top := HBoxContainer.new()
	top.set_anchors_preset(Control.PRESET_TOP_WIDE)
	top.offset_left = 16
	top.offset_right = -16
	top.offset_top = 8
	top.offset_bottom = 32
	top.add_theme_constant_override("separation", 16)
	add_child(top)

	var hdr := Label.new()
	hdr.text = "ACT 3 · THE TOWN · LABOR DAY 1998"
	hdr.add_theme_font_size_override("font_size", 12)
	hdr.add_theme_color_override("font_color", C_ACCENT)
	top.add_child(hdr)

	_clock_label = Label.new()
	_clock_label.add_theme_font_size_override("font_size", 11)
	_clock_label.add_theme_color_override("font_color", C_TXT)
	top.add_child(_clock_label)

	var s := Control.new()
	s.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top.add_child(s)

	var quit := Button.new()
	quit.text = "  ✕  BACK  "
	quit.pressed.connect(func() -> void: quit_to_shelf.emit())
	top.add_child(quit)

	# View container
	_view_container = Control.new()
	_view_container.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_view_container.offset_top = 44
	_view_container.offset_left = 16
	_view_container.offset_right = -16
	_view_container.offset_bottom = -8
	add_child(_view_container)


# ─── Hub view ────────────────────────────────────────────────────

func _show_hub() -> void:
	_pending_view = "hub"
	_clear_view()
	_update_clock_label()

	var col := VBoxContainer.new()
	col.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	col.add_theme_constant_override("separation", 8)
	_view_container.add_child(col)

	# Opening narration (only on first hub render — after first visit,
	# skip so the panel is more compact).
	if _visited.is_empty():
		var intro := RichTextLabel.new()
		intro.bbcode_enabled = true
		intro.fit_content = true
		intro.add_theme_color_override("default_color", C_TXT)
		intro.add_theme_font_size_override("normal_font_size", 11)
		intro.custom_minimum_size = Vector2(0, 120)
		var opening: Array = _def.get("opening_narration", [])
		for line in opening:
			intro.append_text("[i]%s[/i]\n\n" % String(line))
		col.add_child(intro)
	else:
		var back := Label.new()
		back.text = "· back at the map ·"
		back.add_theme_font_size_override("font_size", 10)
		back.add_theme_color_override("font_color", C_TXT_DIM)
		col.add_child(back)

	# Grid of nine locations.
	var grid := GridContainer.new()
	grid.columns = 3
	grid.add_theme_constant_override("h_separation", 8)
	grid.add_theme_constant_override("v_separation", 8)
	col.add_child(grid)

	for loc_var in _locations:
		var loc: Dictionary = loc_var
		grid.add_child(_make_hub_tile(loc))

	# End-of-day / return-early buttons
	var actions := HBoxContainer.new()
	actions.alignment = BoxContainer.ALIGNMENT_END
	actions.add_theme_constant_override("separation", 8)
	col.add_child(actions)

	# Show the "return to Kwik Stop" option only after at least one
	# visit or after the clock has passed 18:00 (soft nudge).
	if _visited.size() >= 1 or _clock_minutes >= 1080:
		var ret := Button.new()
		ret.text = "  RETURN TO THE KWIK STOP  "
		ret.pressed.connect(_show_return_to_kwik_stop)
		actions.add_child(ret)


func _make_hub_tile(loc: Dictionary) -> Control:
	var loc_id := String(loc.get("id", ""))
	var visited := _visited.has(loc_id)
	var panel := Panel.new()
	panel.custom_minimum_size = Vector2(HUB_TILE_W, HUB_TILE_H)
	panel.mouse_filter = Control.MOUSE_FILTER_STOP
	var sb := StyleBoxFlat.new()
	sb.bg_color = C_TILE_VIS if visited else C_TILE
	sb.border_color = C_ACCENT if visited else C_TXT_DIM
	sb.set_border_width_all(1)
	sb.set_corner_radius_all(3)
	sb.content_margin_left = 8
	sb.content_margin_right = 8
	sb.content_margin_top = 6
	sb.content_margin_bottom = 6
	panel.add_theme_stylebox_override("panel", sb)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.offset_left = 8
	v.offset_right = -8
	v.offset_top = 6
	v.offset_bottom = -6
	v.add_theme_constant_override("separation", 2)
	panel.add_child(v)

	var name_lbl := Label.new()
	name_lbl.text = String(loc.get("name", loc_id))
	name_lbl.add_theme_font_size_override("font_size", 11)
	name_lbl.add_theme_color_override("font_color", C_ACCENT if visited else C_TXT)
	v.add_child(name_lbl)

	# Tiny compositional preview using the hero palette.
	var preview := HBoxContainer.new()
	preview.add_theme_constant_override("separation", 2)
	preview.custom_minimum_size = Vector2(0, 32)
	v.add_child(preview)
	var palette: Array = HERO_PALETTES.get(loc_id, [C_TILE, C_TILE_VIS, C_TXT_DIM])
	for c in palette:
		var band := ColorRect.new()
		band.color = c if not visited else Color(c.r, c.g, c.b, 0.65)
		band.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		preview.add_child(band)

	var status := Label.new()
	status.text = "  ✓ visited" if visited else "  · unvisited"
	status.add_theme_font_size_override("font_size", 9)
	status.add_theme_color_override("font_color", C_TXT_DIM)
	v.add_child(status)

	panel.mouse_entered.connect(func() -> void:
		sb.bg_color = C_TILE_HOV
		var b := get_node_or_null("/root/SFXBank")
		if b: b.play("tile_hover", 0.5))
	panel.mouse_exited.connect(func() -> void: sb.bg_color = C_TILE_VIS if visited else C_TILE)
	panel.gui_input.connect(func(ev: InputEvent) -> void:
		if ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed:
			var b := get_node_or_null("/root/SFXBank")
			if b: b.play("tile_enter", 0.8)
			_enter_location(loc_id))
	return panel


# ─── Location view ───────────────────────────────────────────────

func _enter_location(loc_id: String) -> void:
	# Advance the clock.
	_advance_clock(_clock_cost_per_visit)
	if not _visited.has(loc_id):
		_visited.append(loc_id)
	_pending_view = "location:" + loc_id
	_render_location(loc_id)


func _render_location(loc_id: String) -> void:
	_clear_view()
	_update_clock_label()

	var loc: Dictionary = _find_location(loc_id)
	if loc.is_empty():
		return

	var col := VBoxContainer.new()
	col.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	col.add_theme_constant_override("separation", 6)
	_view_container.add_child(col)

	# Location header
	var name_lbl := Label.new()
	name_lbl.text = String(loc.get("name", loc_id)).to_upper()
	name_lbl.add_theme_font_size_override("font_size", 13)
	name_lbl.add_theme_color_override("font_color", C_ACCENT)
	col.add_child(name_lbl)

	# Hero image panel (procedural placeholder).
	col.add_child(_make_hero_image(loc_id))

	# Intro narration
	var intro := RichTextLabel.new()
	intro.bbcode_enabled = true
	intro.fit_content = true
	intro.custom_minimum_size = Vector2(0, 60)
	intro.add_theme_color_override("default_color", C_TXT)
	intro.add_theme_font_size_override("normal_font_size", 11)
	intro.append_text("[i]%s[/i]\n" % String(loc.get("narration_intro", "")))
	col.add_child(intro)

	# Hotspot list + interaction log
	var hs_wrap := HBoxContainer.new()
	hs_wrap.add_theme_constant_override("separation", 12)
	hs_wrap.size_flags_vertical = Control.SIZE_EXPAND_FILL
	col.add_child(hs_wrap)

	# Left · hotspot buttons
	var hs_col := VBoxContainer.new()
	hs_col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hs_col.size_flags_stretch_ratio = 1.0
	hs_col.add_theme_constant_override("separation", 4)
	hs_wrap.add_child(hs_col)

	var response_log := RichTextLabel.new()
	response_log.bbcode_enabled = true
	response_log.scroll_following = true
	response_log.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	response_log.size_flags_stretch_ratio = 1.5
	response_log.add_theme_color_override("default_color", C_TXT)
	response_log.add_theme_font_size_override("normal_font_size", 11)
	hs_wrap.add_child(response_log)

	for hs_var in loc.get("hotspots", []):
		var hs: Dictionary = hs_var
		hs_col.add_child(_make_hotspot_row(hs, response_log, loc))

	# Leave-location button
	var actions := HBoxContainer.new()
	actions.alignment = BoxContainer.ALIGNMENT_END
	actions.add_theme_constant_override("separation", 8)
	col.add_child(actions)

	var leave := Button.new()
	leave.text = "  ← back to the map  "
	leave.pressed.connect(func() -> void:
		var outro: String = String(loc.get("on_leave_narration", ""))
		if outro != "":
			response_log.append_text("\n[i]%s[/i]\n" % outro)
			# Small delay so the outro reads before returning.
			get_tree().create_timer(0.6).timeout.connect(func() -> void: _show_hub())
		else:
			_show_hub())
	actions.add_child(leave)

	# If this is the Kwik Stop revisit and the clock is late, add
	# the return-to-shelf-for-ending affordance inline.
	if loc_id == "kwik_stop_revisit" and _clock_minutes >= 1080:
		var ret := Button.new()
		ret.text = "  wait for Jules · end the day  "
		ret.pressed.connect(_show_return_to_kwik_stop)
		actions.add_child(ret)


func _make_hero_image(loc_id: String) -> Control:
	# Wrap panel with the accent-bordered frame.
	var wrap := Panel.new()
	wrap.custom_minimum_size = Vector2(HERO_W, HERO_H)
	var sb := StyleBoxFlat.new()
	sb.bg_color = C_TILE
	sb.border_color = C_ACCENT
	sb.set_border_width_all(1)
	wrap.add_theme_stylebox_override("panel", sb)

	# Prefer an authored HeroImage from sprites/act3/<loc_id>.json.
	# Falls back to the palette-band placeholder if the file is
	# missing or malformed.
	var hero_path := "res://resources/games/vol7/estuary_3/sprites/act3/%s.json" % loc_id
	var hero := HeroImage.new()
	if hero.load_from(hero_path):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(HERO_W, HERO_H))
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		tex_rect.position = Vector2(0, 0)
		tex_rect.size = Vector2(HERO_W, HERO_H)
		wrap.add_child(tex_rect)
	else:
		var palette: Array = HERO_PALETTES.get(loc_id, [C_TILE, C_TILE_VIS, C_TXT_DIM])
		var band_h: int = int(float(HERO_H) / float(palette.size()))
		for i in range(palette.size()):
			var band := ColorRect.new()
			band.color = palette[i]
			band.position = Vector2(0, band_h * i)
			band.custom_minimum_size = Vector2(HERO_W, band_h)
			band.size = band.custom_minimum_size
			wrap.add_child(band)
		var horizon := ColorRect.new()
		horizon.color = Color(0.10, 0.09, 0.06, 0.60)
		horizon.position = Vector2(0, band_h + int(band_h * 0.5))
		horizon.custom_minimum_size = Vector2(HERO_W, 2)
		horizon.size = horizon.custom_minimum_size
		wrap.add_child(horizon)
	# Location caption in the lower-left corner of the hero.
	var cap := Label.new()
	cap.text = "  " + loc_id.replace("_", " ") + "  "
	cap.add_theme_font_size_override("font_size", 9)
	cap.add_theme_color_override("font_color", Color(0.10, 0.09, 0.06, 0.85))
	cap.position = Vector2(8, HERO_H - 20)
	wrap.add_child(cap)
	return wrap


func _make_hotspot_row(hs: Dictionary, log_box: RichTextLabel, loc: Dictionary) -> Control:
	var wrap := VBoxContainer.new()
	wrap.add_theme_constant_override("separation", 2)

	var hs_id: String = String(hs.get("id", ""))
	var label: String = String(hs.get("label", hs_id))

	# Prerequisite gating · JSON convention: keys like
	# `gated_on_shell_visited`, `gated_on_bookstore_side_alley_visited`.
	# We flip those to positive checks on `_flags`/`_visited`.
	var gated_note := ""
	for k in hs.keys():
		var ks := String(k)
		if not ks.begins_with("gated_on_"):
			continue
		var value := bool(hs[k])
		if not value: continue
		var gate := ks.substr(9)   # after "gated_on_"
		if not _gate_satisfied(gate):
			gated_note = gate.replace("_", " ")
			break

	var hdr := Label.new()
	hdr.text = ("· " if gated_note == "" else "· [locked] ") + label
	hdr.add_theme_font_size_override("font_size", 11)
	hdr.add_theme_color_override("font_color", C_TXT if gated_note == "" else C_TXT_DIM)
	wrap.add_child(hdr)

	if gated_note != "":
		var note := Label.new()
		note.text = "    (needs · %s)" % gated_note
		note.add_theme_font_size_override("font_size", 9)
		note.add_theme_color_override("font_color", C_TXT_DIM)
		wrap.add_child(note)
		return wrap

	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 4)
	wrap.add_child(row)
	for verb in ["look", "talk", "use", "take", "open"]:
		if not hs.has(verb):
			continue
		var b := Button.new()
		b.text = "  " + verb + "  "
		b.focus_mode = Control.FOCUS_NONE
		var hs_capture := hs
		var verb_capture := verb
		var loc_capture := loc
		b.pressed.connect(func() -> void: _fire_hotspot(hs_capture, verb_capture, loc_capture, log_box))
		row.add_child(b)
	return wrap


func _fire_hotspot(hs: Dictionary, verb: String, loc: Dictionary, log_box: RichTextLabel) -> void:
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx:
		match verb:
			"look":  sfx.play("hotspot_look", 0.65)
			"talk":  sfx.play("hotspot_talk", 0.65)
			"use":   sfx.play("hotspot_use", 0.65)
			"open":  sfx.play("hotspot_use", 0.65)
			"take":  sfx.play("hotspot_use", 0.55)
			_:       sfx.play("hotspot_look", 0.55)
	var response_var: Variant = hs.get(verb, "")
	# Some responses are dictionaries with gated dialogue variants.
	if response_var is Dictionary:
		var d: Dictionary = response_var
		# Gated dialogue keys look like:
		# "gated_on_<flag_expr>": {flag, line}, "default_line": "..."
		var found := false
		for k in d.keys():
			var ks := String(k)
			if not ks.begins_with("gated_on_"):
				continue
			var g: Dictionary = d[k]
			var expr := String(g.get("flag", ""))
			if _flag_expr_satisfied(expr):
				log_box.append_text("[color=#c8a842]> %s the %s[/color]\n%s\n" % [verb, String(hs.get("label", "")), String(g.get("line", ""))])
				found = true
				break
		if not found:
			log_box.append_text("[color=#c8a842]> %s the %s[/color]\n%s\n" % [verb, String(hs.get("label", "")), String(d.get("default_line", ""))])
	elif response_var is String and String(response_var) != "":
		log_box.append_text("[color=#c8a842]> %s the %s[/color]\n%s\n" % [verb, String(hs.get("label", "")), String(response_var)])
	# Bookkeeping · flags set implicitly when we visit a hotspot with
	# a specific id. We map "<location_id>_<hotspot_id>_visited" to
	# true. Cheap and adequate for the JSON's gate style.
	var loc_id := String(loc.get("id", ""))
	var hs_id := String(hs.get("id", ""))
	_flags[loc_id + "_" + hs_id + "_visited"] = true
	# Also set generic per-location visited (already tracked in _visited)
	# and the specific alias the JSON uses when it says
	# `gated_on_bookstore_side_alley_visited`.
	if loc_id == "bookstore" and hs_id == "side_alley":
		_flags["bookstore_side_alley_visited"] = true
	if loc_id == "bookstore" and hs_id == "back_door_key":
		_flags["key_taken"] = true
	if loc_id == "bookstore" and hs_id == "the_shop_inside":
		_flags["shop_inside_visited"] = true
	if loc_id == "shell_station":
		_flags["shell_visited"] = true


func _flag_expr_satisfied(expr: String) -> bool:
	# Very simple AND expression parser. Handles "a AND b" and "a".
	# Anything more complex we don't need for Act 3's authored
	# gates. The JSON's phrase style ("kwik_stop_revisited_in_daylight
	# AND shell_visited") is caught here.
	if expr == "":
		return true
	var terms := expr.split(" AND ")
	for t_var in terms:
		var t := String(t_var).strip_edges()
		if t == "":
			continue
		if not _flag_satisfied(t):
			return false
	return true


func _flag_satisfied(name: String) -> bool:
	# Also match a small alias set defined below and _visited.
	if _flags.get(name, false):
		return true
	if name == "kwik_stop_revisited_in_daylight" and _visited.has("kwik_stop_revisit"):
		return true
	if name == "shell_visited" and _visited.has("shell_station"):
		return true
	return false


func _gate_satisfied(gate_expr: String) -> bool:
	# Convert JSON's `gated_on_<stuff>` shorthand → boolean check.
	# The stuff after `gated_on_` is a flag name.
	return _flag_satisfied(gate_expr)


func _find_location(loc_id: String) -> Dictionary:
	for l_var in _locations:
		var l: Dictionary = l_var
		if String(l.get("id", "")) == loc_id:
			return l
	return {}


# ─── Return-to-Kwik-Stop ending ──────────────────────────────────

func _show_return_to_kwik_stop() -> void:
	if _ended: return
	_ended = true
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("return_to_shop", 0.85)
	AudioMgr.play_bgm("res://assets/audio/bgm/e3/act3_town_dusk.wav")
	_clear_view()
	# Force clock to at least 18:12 so the narration reads right.
	if _clock_minutes < 1092:
		_clock_minutes = 1092
	_update_clock_label()

	var col := VBoxContainer.new()
	col.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	col.add_theme_constant_override("separation", 8)
	_view_container.add_child(col)

	var hdr := Label.new()
	hdr.text = "RETURN TO THE KWIK STOP · 06:12 PM"
	hdr.add_theme_font_size_override("font_size", 13)
	hdr.add_theme_color_override("font_color", C_ACCENT)
	col.add_child(hdr)

	var ret: Dictionary = _def.get("return_to_kwik_stop", {})
	var body := RichTextLabel.new()
	body.bbcode_enabled = true
	body.fit_content = true
	body.custom_minimum_size = Vector2(0, 140)
	body.add_theme_color_override("default_color", C_TXT)
	body.add_theme_font_size_override("normal_font_size", 11)
	body.append_text(String(ret.get("narration", "")))
	col.add_child(body)

	# Branch on Act 2 final choice.
	var final_id := String(_canon_vars.get("estuary_3_act2_final", ""))
	var branches: Dictionary = ret.get("branches", {})
	var branch_key := "if_act2_choice_yes" if final_id == "yes" \
					 else "if_act2_choice_no" if final_id == "no" \
					 else "if_act2_choice_the_question_is_wrong"
	var branch_text: String = String(branches.get(branch_key, ""))
	if branch_text == "":
		branch_text = "Jules is at the counter. She looks at you for a longer moment than usual. The scene ends."
	var branch_lbl := RichTextLabel.new()
	branch_lbl.bbcode_enabled = true
	branch_lbl.fit_content = true
	branch_lbl.custom_minimum_size = Vector2(0, 160)
	branch_lbl.add_theme_color_override("default_color", C_ACCENT)
	branch_lbl.add_theme_font_size_override("normal_font_size", 12)
	branch_lbl.append_text("[i]%s[/i]" % branch_text)
	col.add_child(branch_lbl)

	# Advance to Act 4.
	var actions := HBoxContainer.new()
	actions.alignment = BoxContainer.ALIGNMENT_END
	col.add_child(actions)

	var next := Button.new()
	next.text = "  →  DAWN.  ACT 4.  "
	next.pressed.connect(func() -> void:
		_canon_vars["estuary_3_act3_locations_visited_count"] = _visited.size()
		act3_finished.emit(_canon_vars, _visited))
	actions.add_child(next)


# ─── Clock ───────────────────────────────────────────────────────

func _advance_clock(minutes: int) -> void:
	_clock_minutes = min(_clock_end_minutes, _clock_minutes + minutes)
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("clock_tick", 0.35)


func _update_clock_label() -> void:
	if _clock_label == null: return
	var visits := _visited.size()
	_clock_label.text = "  clock %s  ·  %d location%s visited" % [
		_minutes_to_hhmm(_clock_minutes), visits, "" if visits == 1 else "s"]


# ─── Utility ─────────────────────────────────────────────────────

func _clear_view() -> void:
	if _view_container == null: return
	for c in _view_container.get_children():
		c.queue_free()
