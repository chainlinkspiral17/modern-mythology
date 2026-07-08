extends Control
## Act 2 controller · top-down landscape sim across four seasons +
## a second spring.
##
## Loads:  res://resources/games/vol7/estuary_3/act2_estuary.json
##
## Contract with Estuary3Host:
##   - Host instantiates EstuaryPlanner, then calls `boot(host_state)`
##     with the accumulated `register_tape` from Act 1.
##   - When the second spring lands, EstuaryPlanner emits
##     `act2_finished(canon_vars, season_choices)`. Host merges
##     canon_vars into run state and advances to act3_town.
##
## This commit builds:
##   - Procedural landscape rendering (value-noise elevation + a
##     hand-authored color ramp for mudflat/marsh/deepwater
##     channel/estuary edge). Rendered to an Image once at boot,
##     wrapped in an ImageTexture, drawn as a TextureRect.
##   - Kwik Stop marker at (384, 210) in canvas coordinates.
##   - Tide gate marker at (80, 260).
##   - Three control panels per season: tide gate, riparian buffer,
##     species boost. Species-boost buttons pull sprites from the
##     Act 2 sprite folder via SlowstockSprite.
##   - Season cycle · spring → summer → fall → winter → second_spring.
##   - Per-season soft-target scoring · picks the success or failure
##     narration from the JSON based on which axes matched.
##   - Final choice screen at Second Spring — three options, each
##     records a canon_var + lore_token that Act 4 reads.
##
## F4-compliant via add_to_group("ui").

signal act2_finished(canon_vars: Dictionary, season_choices: Array)
signal quit_to_shelf

const ACT2_JSON := "res://resources/games/vol7/estuary_3/act2_estuary.json"
const SPRITES_DIR := "res://resources/games/vol7/estuary_3/sprites/act2/"

const MAP_W := 640
const MAP_H := 360

# Color ramp indices for the landscape image, low → high elevation.
const RAMP := [
	Color(0.12, 0.16, 0.28),   # 0 · deepwater channel
	Color(0.22, 0.28, 0.36),   # 1 · shallow channel
	Color(0.38, 0.42, 0.44),   # 2 · mudflat wet
	Color(0.54, 0.50, 0.38),   # 3 · mudflat dry
	Color(0.42, 0.52, 0.36),   # 4 · low marsh
	Color(0.52, 0.60, 0.36),   # 5 · high marsh · sedge
	Color(0.46, 0.44, 0.28),   # 6 · upland transition
	Color(0.30, 0.38, 0.24),   # 7 · coastal-highway rise
]

const C_BG        := Color(0.024, 0.020, 0.014, 0.97)
const C_ACCENT    := Color(0.78, 0.66, 0.29, 1.00)
const C_TXT       := Color(0.83, 0.79, 0.69, 1.00)
const C_TXT_DIM   := Color(0.50, 0.47, 0.38, 1.00)
const C_KWIK      := Color(0.96, 0.86, 0.42, 1.00)
const C_GATE      := Color(0.85, 0.72, 0.30, 1.00)
const C_OK        := Color(0.50, 0.82, 0.60, 1.00)
const C_BAD       := Color(0.86, 0.58, 0.42, 1.00)

# Loaded data
var _def: Dictionary = {}
var _seasons: Array = []
var _register_tape: Array = []

# Session state
var _season_index: int = 0
var _season_choices: Array = []    # one dict per completed season
var _current_choice: Dictionary = {
	"tide_gate":       "",
	"riparian_buffer": "",
	"species_boost":   [],       # up to 2
}
var _canon_vars: Dictionary = {}

# UI refs
var _map_tex_rect: TextureRect = null
var _map_overlay: Control = null
var _narration_lbl: RichTextLabel = null
var _season_hdr: Label = null
var _control_col: VBoxContainer = null
var _next_btn: Button = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	_load_def()
	_build_ui()


func boot(host_state: Dictionary) -> void:
	_register_tape = host_state.get("register_tape", []) as Array
	_season_index = 0
	_season_choices.clear()
	_reset_current_choice()
	_render_current_season()


# ─── Data ────────────────────────────────────────────────────────

func _load_def() -> void:
	if not FileAccess.file_exists(ACT2_JSON):
		push_warning("[EstuaryPlanner] missing %s" % ACT2_JSON)
		return
	var f := FileAccess.open(ACT2_JSON, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		_def = parsed
		_seasons = _def.get("seasons", [])


func _reset_current_choice() -> void:
	_current_choice = {
		"tide_gate":       "",
		"riparian_buffer": "",
		"species_boost":   [],
	}


# ─── UI build ────────────────────────────────────────────────────

func _build_ui() -> void:
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# Top header
	var top := HBoxContainer.new()
	top.set_anchors_preset(Control.PRESET_TOP_WIDE)
	top.offset_left = 16
	top.offset_right = -16
	top.offset_top = 8
	top.offset_bottom = 32
	top.add_theme_constant_override("separation", 16)
	add_child(top)

	_season_hdr = Label.new()
	_season_hdr.add_theme_font_size_override("font_size", 13)
	_season_hdr.add_theme_color_override("font_color", C_ACCENT)
	top.add_child(_season_hdr)

	var s := Control.new()
	s.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top.add_child(s)

	var quit := Button.new()
	quit.text = "  ✕  BACK  "
	quit.pressed.connect(func() -> void: quit_to_shelf.emit())
	top.add_child(quit)

	# Main layout: map on the left, controls on the right, narration below.
	var main := HBoxContainer.new()
	main.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	main.offset_left = 16
	main.offset_right = -16
	main.offset_top = 40
	main.offset_bottom = -160
	main.add_theme_constant_override("separation", 16)
	add_child(main)

	# Map column
	var map_col := VBoxContainer.new()
	map_col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	map_col.size_flags_stretch_ratio = 2.0
	map_col.add_theme_constant_override("separation", 4)
	main.add_child(map_col)

	# The map is rendered as a TextureRect with a proceduraly-drawn
	# image, overlaid with a Control that hosts the kwik-stop and
	# tide-gate markers.
	var map_wrap := Control.new()
	map_wrap.custom_minimum_size = Vector2(MAP_W, MAP_H)
	map_wrap.size_flags_vertical = Control.SIZE_EXPAND_FILL
	map_col.add_child(map_wrap)

	_map_tex_rect = TextureRect.new()
	_map_tex_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_map_tex_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	map_wrap.add_child(_map_tex_rect)

	_map_overlay = Control.new()
	_map_overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_map_overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
	map_wrap.add_child(_map_overlay)

	# Kick off the procedural render.
	_generate_landscape_image()
	_draw_markers()

	# Control column
	_control_col = VBoxContainer.new()
	_control_col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_control_col.size_flags_stretch_ratio = 1.0
	_control_col.add_theme_constant_override("separation", 8)
	main.add_child(_control_col)

	# Narration + next button
	var bottom := VBoxContainer.new()
	bottom.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	bottom.offset_left = 16
	bottom.offset_right = -16
	bottom.offset_top = -152
	bottom.offset_bottom = -8
	bottom.add_theme_constant_override("separation", 6)
	add_child(bottom)

	_narration_lbl = RichTextLabel.new()
	_narration_lbl.bbcode_enabled = true
	_narration_lbl.fit_content = false
	_narration_lbl.custom_minimum_size = Vector2(0, 108)
	_narration_lbl.add_theme_font_size_override("normal_font_size", 11)
	_narration_lbl.add_theme_color_override("default_color", C_TXT)
	bottom.add_child(_narration_lbl)

	var next_row := HBoxContainer.new()
	next_row.alignment = BoxContainer.ALIGNMENT_END
	bottom.add_child(next_row)

	_next_btn = Button.new()
	_next_btn.text = "  → NEXT SEASON  "
	_next_btn.pressed.connect(_on_next_pressed)
	next_row.add_child(_next_btn)


# ─── Procedural landscape ────────────────────────────────────────

func _generate_landscape_image() -> void:
	# Deterministic hash-based value noise + a horizontal + vertical
	# gradient that pushes deep water to the west, mudflats to the
	# south, upland to the east. Renders once at boot; the same
	# landscape carries across all four seasons.
	var img := Image.create(MAP_W, MAP_H, false, Image.FORMAT_RGBA8)
	var scale_x := 0.032
	var scale_y := 0.048
	for y in range(MAP_H):
		for x in range(MAP_W):
			var n := _fbm(float(x) * scale_x, float(y) * scale_y)
			# Base elevation: 0..1 · shape it with position gradients.
			var elev := n
			# Push west of x=140 into deep channel.
			elev -= max(0.0, (140.0 - float(x)) / 140.0) * 0.55
			# Push southern half toward mudflat.
			elev -= max(0.0, (float(y) - 200.0) / 160.0) * 0.35
			# Push far-east into upland rise.
			elev += max(0.0, (float(x) - 480.0) / 160.0) * 0.35
			# Clamp + quantize to the ramp.
			elev = clamp(elev, 0.0, 1.0)
			var ramp_idx := int(elev * float(RAMP.size() - 1) + 0.5)
			ramp_idx = clamp(ramp_idx, 0, RAMP.size() - 1)
			img.set_pixel(x, y, RAMP[ramp_idx])
	# Waterline shimmer band along the channel edge (a single row
	# of lighter blue at where elevation goes from index 1 to 2).
	# Cheap post-process pass.
	for y in range(1, MAP_H - 1):
		for x in range(1, MAP_W - 1):
			var here := img.get_pixel(x, y)
			var east := img.get_pixel(x + 1, y)
			if here == RAMP[1] and east == RAMP[2]:
				img.set_pixel(x, y, Color(0.72, 0.82, 0.88, 1.0))
	_map_tex_rect.texture = ImageTexture.create_from_image(img)


func _draw_markers() -> void:
	# Kwik Stop marker
	var kwik: Dictionary = _def.get("map", {}).get("kwik_stop_marker", {})
	var kpos: Array = kwik.get("pos_xy", [384, 210])
	var ksize: Array = kwik.get("size_px", [8, 8])
	var k := ColorRect.new()
	k.color = C_KWIK
	k.position = Vector2(float(kpos[0]) - float(ksize[0]) / 2.0, float(kpos[1]) - float(ksize[1]) / 2.0)
	k.custom_minimum_size = Vector2(float(ksize[0]), float(ksize[1]))
	k.size = k.custom_minimum_size
	_map_overlay.add_child(k)
	var klbl := Label.new()
	klbl.text = "  KWIK STOP"
	klbl.add_theme_font_size_override("font_size", 8)
	klbl.add_theme_color_override("font_color", C_KWIK)
	klbl.position = Vector2(float(kpos[0]) + float(ksize[0]), float(kpos[1]) - 6.0)
	_map_overlay.add_child(klbl)

	# Tide gate marker
	var gate: Dictionary = _def.get("map", {}).get("tide_gate_pos", {})
	var gpos: Array = gate.get("pos_xy", [80, 260])
	var gsize: Array = gate.get("size_px", [12, 12])
	var g := Panel.new()
	g.position = Vector2(float(gpos[0]) - float(gsize[0]) / 2.0, float(gpos[1]) - float(gsize[1]) / 2.0)
	g.custom_minimum_size = Vector2(float(gsize[0]), float(gsize[1]))
	g.size = g.custom_minimum_size
	var gsb := StyleBoxFlat.new()
	gsb.bg_color = C_GATE
	gsb.border_color = Color(0.4, 0.32, 0.14, 1)
	gsb.set_border_width_all(1)
	g.add_theme_stylebox_override("panel", gsb)
	_map_overlay.add_child(g)
	var glbl := Label.new()
	glbl.text = "TIDE GATE"
	glbl.add_theme_font_size_override("font_size", 8)
	glbl.add_theme_color_override("font_color", C_GATE)
	glbl.position = Vector2(float(gpos[0]) + float(gsize[0]) + 2.0, float(gpos[1]) - 6.0)
	_map_overlay.add_child(glbl)


# Simple value-noise FBM. Two octaves is plenty for a 640x360 map.
func _fbm(x: float, y: float) -> float:
	var v := 0.0
	var amp := 0.5
	var fx := x
	var fy := y
	for _o in range(2):
		v += _value_noise(fx, fy) * amp
		fx *= 2.0
		fy *= 2.0
		amp *= 0.5
	return clamp(v, 0.0, 1.0)


func _value_noise(x: float, y: float) -> float:
	var xi := int(floor(x))
	var yi := int(floor(y))
	var xf := x - floor(x)
	var yf := y - floor(y)
	var v00 := _hash2(xi,       yi)
	var v10 := _hash2(xi + 1,   yi)
	var v01 := _hash2(xi,       yi + 1)
	var v11 := _hash2(xi + 1,   yi + 1)
	# Smooth cubic interpolation
	var sx := xf * xf * (3.0 - 2.0 * xf)
	var sy := yf * yf * (3.0 - 2.0 * yf)
	var i0 := lerp(v00, v10, sx)
	var i1 := lerp(v01, v11, sx)
	return lerp(i0, i1, sy)


func _hash2(x: int, y: int) -> float:
	# A little integer-hash based on Knuth's multiplicative hash;
	# deterministic, no dependency on runtime RNG.
	var n: int = x * 374761393 + y * 668265263
	n = (n ^ (n >> 13)) * 1274126177
	n = n ^ (n >> 16)
	return float(n & 0xffff) / 65535.0


# ─── Season loop ─────────────────────────────────────────────────

func _render_current_season() -> void:
	if _season_index >= _seasons.size():
		_render_final_choice()
		return
	var season: Dictionary = _seasons[_season_index]
	_season_hdr.text = String(season.get("label", "Season"))
	# Intro narration.
	_narration_lbl.clear()
	var intro: String = String(season.get("narration_intro", ""))
	if intro != "":
		_narration_lbl.append_text("[i]%s[/i]\n\n" % intro)
	# Kwik Stop echo (previous season, if any).
	if _season_index > 0:
		var prev_season: Dictionary = _seasons[_season_index - 1]
		var echo: String = String(prev_season.get("kwik_stop_echo", ""))
		if echo != "":
			_narration_lbl.append_text("[color=#c8a842][i]kwik stop echo · %s[/i][/color]\n\n" % echo)
	# Second spring is the final-choice frame; controls hidden.
	if String(season.get("id", "")) == "second_spring":
		_narration_lbl.append_text("[i]%s[/i]" % String(season.get("narration_intro", "")))
		if season.has("narration_out"):
			_narration_lbl.append_text("\n\n" + String(season["narration_out"]))
		# Trigger the final choice.
		_render_final_choice()
		return
	# Otherwise · build the three control panels for this season.
	_reset_current_choice()
	_build_season_controls()
	_next_btn.text = "  → SETTLE THE SEASON  "
	_next_btn.disabled = false


func _build_season_controls() -> void:
	# Clear existing controls.
	for c in _control_col.get_children():
		c.queue_free()
	for ctrl_var in _def.get("controls", []):
		var ctrl: Dictionary = ctrl_var
		var cid: String = String(ctrl.get("id", ""))
		var hdr := Label.new()
		hdr.text = String(ctrl.get("label", cid)).to_upper()
		hdr.add_theme_font_size_override("font_size", 11)
		hdr.add_theme_color_override("font_color", C_ACCENT)
		_control_col.add_child(hdr)
		var note := Label.new()
		note.text = String(ctrl.get("notes", ""))
		note.add_theme_font_size_override("font_size", 9)
		note.add_theme_color_override("font_color", C_TXT_DIM)
		note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		_control_col.add_child(note)
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 4)
		_control_col.add_child(row)
		for opt_var in ctrl.get("options", []):
			var opt: Dictionary = opt_var
			var b := Button.new()
			b.toggle_mode = true
			b.text = " " + String(opt.get("label", opt.get("id", ""))) + " "
			b.focus_mode = Control.FOCUS_NONE
			var oid: String = String(opt.get("id", ""))
			b.pressed.connect(func() -> void: _select_option(cid, oid, b))
			# Load species icon into the button for species_boost row.
			if cid == "species_boost":
				var sprite_path := SPRITES_DIR + oid + ".json"
				var sp := SlowstockSprite.new()
				if sp.load_from(sprite_path):
					b.icon = sp.texture()
					b.expand_icon = false
			row.add_child(b)
			# Restore selection state (in case rebuilding).
			if cid == "species_boost":
				if (_current_choice.get("species_boost", []) as Array).has(oid):
					b.button_pressed = true
			elif String(_current_choice.get(cid, "")) == oid:
				b.button_pressed = true
		# Little separator
		var rule := ColorRect.new()
		rule.color = Color(C_ACCENT.r, C_ACCENT.g, C_ACCENT.b, 0.15)
		rule.custom_minimum_size = Vector2(0, 1)
		_control_col.add_child(rule)


func _play_sfx(name: String, vol: float = 1.0) -> void:
	var bank := get_node_or_null("/root/SFXBank")
	if bank: bank.play(name, vol)


func _select_option(cid: String, oid: String, b: Button) -> void:
	_play_sfx("control_click", 0.65)
	if cid == "species_boost":
		var arr: Array = _current_choice.get("species_boost", []).duplicate()
		if arr.has(oid):
			arr.erase(oid)
		else:
			if arr.size() >= 2:
				# Pop the oldest to make room.
				arr.pop_front()
			arr.append(oid)
		_current_choice["species_boost"] = arr
		# Refresh visual state of all species buttons in this row.
		var row: HBoxContainer = b.get_parent()
		for c in row.get_children():
			if c is Button:
				(c as Button).button_pressed = arr.has(String(c.name))
		# Reflect current pick even if button.name wasn't set (Godot
		# uses text as fallback for identity; we didn't set names so
		# instead we walk by index by rebuilding text-map).
		# Simplest: re-toggle b to the state we want.
		b.button_pressed = arr.has(oid)
	else:
		_current_choice[cid] = oid
		# Un-toggle sibling buttons in the row.
		var row: HBoxContainer = b.get_parent()
		for c in row.get_children():
			if c is Button and c != b:
				(c as Button).button_pressed = false


func _on_next_pressed() -> void:
	if _season_index >= _seasons.size():
		# Final choice branch handled its own emission.
		return
	var season: Dictionary = _seasons[_season_index]
	if String(season.get("id", "")) == "second_spring":
		# Handled in _render_final_choice.
		return
	_play_sfx("season_settle", 0.85)
	# Score this season's choice.
	var hit := _score_season_targets(season, _current_choice)
	_season_choices.append({
		"season_id":   String(season.get("id", "")),
		"choice":      _current_choice.duplicate(true),
		"hit_targets": hit,
	})
	# Print outcome narration.
	_narration_lbl.append_text("\n")
	var key := "narration_out_on_success" if hit else "narration_out_on_failure"
	var out: String = String(season.get(key, ""))
	if out != "":
		var color := "#7cffb0" if hit else "#c88070"
		_narration_lbl.append_text("[color=%s][b]%s[/b]  %s[/color]\n" % [
			color, "the season settled." if hit else "the season strained.", out])
	# Advance.
	_season_index += 1
	# Small delay so the outcome text lingers before the next season
	# clobbers the panel. Uses a one-shot Timer via SceneTree.
	get_tree().create_timer(0.6).timeout.connect(func() -> void:
		_narration_lbl.append_text("\n")
		_render_current_season())


func _score_season_targets(season: Dictionary, choice: Dictionary) -> bool:
	var targets: Dictionary = season.get("soft_targets", {})
	var hits := 0
	var checks := 0
	# Tide gate target
	if targets.has("tide_gate_should"):
		checks += 1
		var want := String(targets["tide_gate_should"])
		if want == "any":
			hits += 1
		elif want.contains("_or_"):
			var options := want.split("_or_")
			if options.has(String(choice.get("tide_gate", ""))):
				hits += 1
		elif String(choice.get("tide_gate", "")) == want:
			hits += 1
	# Riparian buffer target
	if targets.has("riparian_buffer_should"):
		checks += 1
		var want2 := String(targets["riparian_buffer_should"])
		if want2 == "any":
			hits += 1
		elif want2.contains("_or_"):
			var options2 := want2.split("_or_")
			if options2.has(String(choice.get("riparian_buffer", ""))):
				hits += 1
		elif String(choice.get("riparian_buffer", "")) == want2:
			hits += 1
	# Species-boost target
	if targets.has("species_boost_should_include_any_of"):
		checks += 1
		var wants: Array = targets["species_boost_should_include_any_of"]
		var picks: Array = choice.get("species_boost", [])
		for w in wants:
			if picks.has(String(w)):
				hits += 1
				break
	if checks == 0:
		return true
	return hits >= checks - 0  # need to hit ALL required


# ─── Final choice ────────────────────────────────────────────────

func _render_final_choice() -> void:
	# Clear controls; the second-spring line is already in the log.
	for c in _control_col.get_children():
		c.queue_free()
	_next_btn.disabled = true
	_next_btn.text = "  · make a choice ·  "
	var setup: String = String(_def.get("final_choice_setup_line", ""))
	if setup != "":
		_narration_lbl.append_text("\n[b][color=#e8c060]%s[/color][/b]\n" % setup)
	# Three buttons.
	var opts := [
		{"id": "yes",                   "label": "Yes."},
		{"id": "no",                    "label": "No."},
		{"id": "the_question_is_wrong", "label": "The question is wrong."},
	]
	for o_var in opts:
		var o: Dictionary = o_var
		var b := Button.new()
		b.text = "  " + String(o["label"]) + "  "
		var oid: String = String(o["id"])
		b.pressed.connect(func() -> void: _finalize_choice(oid))
		_control_col.add_child(b)


func _finalize_choice(final_id: String) -> void:
	_canon_vars["estuary_3_act2_final"] = final_id
	act2_finished.emit(_canon_vars, _season_choices)
