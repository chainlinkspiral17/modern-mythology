extends Control
## Ending screen · closes the loop for a full Estuary 3 playthrough.
##
## Loads:  res://resources/games/vol7/estuary_3/ending.json
##
## Contract with Estuary3Host:
##   - Host instantiates Estuary3Ending, then calls `boot(host_state)`.
##   - The screen reads canon_vars.estuary_3_act2_final (the final
##     choice made at the end of Act 2) and canon_vars.
##     estuary_3_line_shape (from Act 4) and composes:
##
##         options[<final>].epilogue_base
##       + '\n\n'
##       + options[<final>].line_shape_riders[<line_shape>]
##
##     If either canon-var is missing (e.g. the player quit mid-run
##     and boots straight to the ending for debug), we fall back
##     to "the_question_is_wrong" + "fallback" rider.
##
##   - After the player dismisses the epilogue and the credits
##     screen, the ending emits `estuary_3_completed(canon_vars,
##     lore_tokens)`. Host merges canon_vars into the run state,
##     writes slowsticks_finished += ['estuary_3'] via
##     Estuary3Host.finished() → SlowstockBoot → GauntletState.
##
## F4-compliant via add_to_group("ui").

signal estuary_3_completed(canon_vars: Dictionary, lore_tokens: Array)
signal quit_to_shelf

const ENDING_JSON := "res://resources/games/vol7/estuary_3/ending.json"

const C_BG        := Color(0.024, 0.020, 0.014, 0.98)
const C_ACCENT    := Color(0.78, 0.66, 0.29, 1.00)
const C_TXT       := Color(0.83, 0.79, 0.69, 1.00)
const C_TXT_DIM   := Color(0.50, 0.47, 0.38, 1.00)
const C_QUOTE     := Color(0.86, 0.72, 0.42, 1.00)

# Loaded data
var _def: Dictionary = {}

# Session state
var _canon_vars: Dictionary = {}
var _lore_tokens: Array = []
var _act2_final: String = "the_question_is_wrong"
var _line_shape: String = "fallback"

# View state · 0 = epilogue, 1 = credits, 2 = quiet, then emit
var _view_index: int = 0

# UI refs
var _content_col: VBoxContainer = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	_load_def()
	_build_ui()


func boot(host_state: Dictionary) -> void:
	var cv: Variant = host_state.get("canon_vars", {})
	_canon_vars = cv.duplicate(true) if cv is Dictionary else {}
	AudioMgr.play_bgm("res://assets/audio/bgm/e3/ending_quiet.wav")
	# Extract the two canon-vars that steer the epilogue.
	_act2_final = String(_canon_vars.get("estuary_3_act2_final", ""))
	if _act2_final == "":
		_act2_final = "the_question_is_wrong"
	_line_shape = String(_canon_vars.get("estuary_3_line_shape", ""))
	if _line_shape == "":
		_line_shape = "fallback"
	# Seed lore tokens: the option's lore_token + any pending tokens
	# the host carried across acts.
	_lore_tokens.clear()
	var opt := _find_option(_act2_final)
	if opt.has("lore_token"):
		_lore_tokens.append(String(opt["lore_token"]))
	var pending: Array = host_state.get("lore_tokens_pending", [])
	for t in pending:
		var s := String(t)
		if not _lore_tokens.has(s):
			_lore_tokens.append(s)
	# Always write the top-level completion tokens from the manifest.
	# We defer to the host to append 'estuary_3_played' etc.; this
	# screen only surfaces the ones the run's choices earned.
	_view_index = 0
	_render_current_view()


# ─── Data ────────────────────────────────────────────────────────

func _load_def() -> void:
	if not FileAccess.file_exists(ENDING_JSON):
		push_warning("[Estuary3Ending] missing %s" % ENDING_JSON)
		return
	var f := FileAccess.open(ENDING_JSON, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		_def = parsed


func _find_option(oid: String) -> Dictionary:
	for o_var in _def.get("options", []):
		var o: Dictionary = o_var
		if String(o.get("id", "")) == oid:
			return o
	return {}


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
	hdr.text = "ESTUARY 3 · ENDING"
	hdr.add_theme_font_size_override("font_size", 12)
	hdr.add_theme_color_override("font_color", C_ACCENT)
	top.add_child(hdr)

	var s := Control.new()
	s.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top.add_child(s)

	var quit := Button.new()
	quit.text = "  ✕  BACK TO SHELF  "
	quit.pressed.connect(func() -> void: quit_to_shelf.emit())
	top.add_child(quit)

	# Content column (centered, narrow)
	var wrap := PanelContainer.new()
	wrap.set_anchors_preset(Control.PRESET_CENTER)
	wrap.custom_minimum_size = Vector2(660, 480)
	wrap.size = wrap.custom_minimum_size
	wrap.position = Vector2(-330, -240 + 24)
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.030, 0.026, 0.020, 1.0)
	sb.border_color = C_ACCENT
	sb.set_border_width_all(1)
	sb.content_margin_left = 20
	sb.content_margin_right = 20
	sb.content_margin_top = 16
	sb.content_margin_bottom = 16
	wrap.add_theme_stylebox_override("panel", sb)
	add_child(wrap)

	_content_col = VBoxContainer.new()
	_content_col.add_theme_constant_override("separation", 8)
	wrap.add_child(_content_col)


# ─── Views ───────────────────────────────────────────────────────

func _render_current_view() -> void:
	for c in _content_col.get_children():
		c.queue_free()
	# Page turn when the view index actually advances (not on the
	# initial 0 render, which lands as the epilogue on boot).
	if _view_index > 0:
		var sfx := get_node_or_null("/root/SFXBank")
		if sfx: sfx.play("page_turn", 0.65)
	match _view_index:
		0: _render_epilogue()
		1: _render_credits()
		_: _render_quiet()


func _render_epilogue() -> void:
	var opt := _find_option(_act2_final)
	var chosen_label := String(opt.get("label", _act2_final))

	var hdr := Label.new()
	hdr.text = "· %s ·" % chosen_label.to_upper().rstrip(".")
	hdr.add_theme_font_size_override("font_size", 13)
	hdr.add_theme_color_override("font_color", C_ACCENT)
	hdr.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_content_col.add_child(hdr)

	# Composed epilogue: base + rider.
	var body := RichTextLabel.new()
	body.bbcode_enabled = true
	body.fit_content = true
	body.custom_minimum_size = Vector2(600, 340)
	body.add_theme_color_override("default_color", C_TXT)
	body.add_theme_font_size_override("normal_font_size", 11)
	var epilogue_base := String(opt.get("epilogue_base", opt.get("epilogue", "")))
	body.append_text(epilogue_base)
	var riders: Dictionary = opt.get("line_shape_riders", {})
	var rider := ""
	if riders.has(_line_shape):
		rider = String(riders[_line_shape])
	elif riders.has("fallback"):
		rider = String(riders["fallback"])
	if rider != "":
		body.append_text("\n\n")
		body.append_text("[color=#c8a842]%s[/color]" % rider)
	_content_col.add_child(body)

	# Meta line · line shape + option ids (small, dim).
	var meta := Label.new()
	meta.text = "  line: %s  ·  choice: %s" % [_line_shape.replace("_", " "), _act2_final.replace("_", " ")]
	meta.add_theme_font_size_override("font_size", 9)
	meta.add_theme_color_override("font_color", C_TXT_DIM)
	_content_col.add_child(meta)

	var actions := HBoxContainer.new()
	actions.alignment = BoxContainer.ALIGNMENT_END
	_content_col.add_child(actions)

	var next := Button.new()
	next.text = "  → credits  "
	next.pressed.connect(func() -> void:
		_view_index = 1
		_render_current_view())
	actions.add_child(next)


func _render_credits() -> void:
	var post: Dictionary = _def.get("post_ending_screen", {})
	var hdr := Label.new()
	hdr.text = String(post.get("title", "ESTUARY 3 · CREDITS"))
	hdr.add_theme_font_size_override("font_size", 13)
	hdr.add_theme_color_override("font_color", C_ACCENT)
	hdr.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_content_col.add_child(hdr)

	var body := RichTextLabel.new()
	body.bbcode_enabled = true
	body.fit_content = true
	body.custom_minimum_size = Vector2(600, 340)
	body.add_theme_color_override("default_color", C_TXT)
	body.add_theme_font_size_override("normal_font_size", 11)
	var credits: Array = post.get("credits", [])
	for line_v in credits:
		var line := String(line_v)
		if line == "":
			body.append_text("\n")
			continue
		# Lines that start with "'" are the Rocha epigraph — style them.
		if line.begins_with("'"):
			body.append_text("[color=#c8a842][i]%s[/i][/color]\n" % line)
		elif line.begins_with("IN MEMORY OF"):
			body.append_text("[color=#a89860][i]%s[/i][/color]\n" % line)
		else:
			body.append_text("%s\n" % line)
	_content_col.add_child(body)

	var actions := HBoxContainer.new()
	actions.alignment = BoxContainer.ALIGNMENT_END
	_content_col.add_child(actions)

	var next := Button.new()
	next.text = "  → hang up the modem  "
	next.pressed.connect(func() -> void:
		_view_index = 2
		_render_current_view())
	actions.add_child(next)


func _render_quiet() -> void:
	var hdr := Label.new()
	hdr.text = ""
	_content_col.add_child(hdr)

	var body := RichTextLabel.new()
	body.bbcode_enabled = true
	body.fit_content = true
	body.custom_minimum_size = Vector2(600, 200)
	body.add_theme_color_override("default_color", C_TXT)
	body.add_theme_font_size_override("normal_font_size", 12)
	body.append_text("\n\n\n")
	body.append_text("[color=#c8a842]You have finished ESTUARY 3.[/color]\n\n")
	body.append_text("[i]The cartridge sleeve remembers what you did.[/i]")
	_content_col.add_child(body)

	var actions := HBoxContainer.new()
	actions.alignment = BoxContainer.ALIGNMENT_END
	_content_col.add_child(actions)

	var back := Button.new()
	back.text = "  →  back to the shelf  "
	back.pressed.connect(_finish_and_return)
	actions.add_child(back)


func _finish_and_return() -> void:
	# Assemble the final canon_vars set (option choice, line shape,
	# any prior canon_vars from Acts 2/4).
	_canon_vars["estuary_3_act2_final"] = _act2_final
	_canon_vars["estuary_3_line_shape"] = _line_shape
	# Manifest also authors completion tokens (estuary_3_played,
	# sam_shift_finished_this_particular_summer). We append those
	# alongside the option's chosen lore_token so the scrapbook
	# has both a completion signal and a choice-specific signal.
	var manifest_tokens := [
		"estuary_3_played",
		"sam_shift_finished_this_particular_summer",
	]
	for t in manifest_tokens:
		if not _lore_tokens.has(String(t)):
			_lore_tokens.append(String(t))
	estuary_3_completed.emit(_canon_vars, _lore_tokens)
