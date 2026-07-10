extends "res://scenes/menu/DioramaBase.gd"
## WorldFrogDiorama — the Frog's closing oracle reading.
##
## Twenty-two cards, each with the Frog's brief qualified verdict.
## The reading scrolls in order; the player can click any card row
## to expand the Frog's gloss on that arcana. The last entry is
## XXI THE WORLD itself — the deck closes by reading the chapter
## the reader is in.
##
## Lore: this is the deck's only Frog-led diorama. daemon_observer
## records the croaks; the Frog speaks. The substrate signature is
## variable — the wreath holds all rates — but defaults to a low
## 6 Hz tick (the chapter's quiet metronome) with occasional croak
## events at the bottom of the spectrum.

const _ORACLE := [
	{"n": "0", "name": "THE FOOL",
		"verdict": "He did not move. That is the chapter. (Mostly.) He is moving now. The clock advanced to dawn. The chapter that did not move is the chapter that ended.",
		"unlock": "vol5_frog_reads_fool"},
	{"n": "I", "name": "THE MAGICIAN",
		"verdict": "He built it. He did not realize the gesture would be borrowed. That is fine; gestures are made to be borrowed.",
		"unlock": "vol5_frog_reads_magician"},
	{"n": "II", "name": "THE HIGH PRIESTESS",
		"verdict": "She recorded what was given. She kept the agreements she could keep. She broke one. The breaking is in the archive. The agreement is in the archive too. Both are correct. (Mostly.)",
		"unlock": "vol5_frog_reads_priestess"},
	{"n": "III", "name": "THE EMPRESS",
		"verdict": "Two figures, one body. The split is the chapter. The collapse of the split is the chapter that follows the chapter. The body is fine. (Mostly.)",
		"unlock": "vol5_frog_reads_empress"},
	{"n": "IV", "name": "THE EMPEROR",
		"verdict": "The throne passes. He knows it. He wrote the rule for what not to write.",
		"unlock": "vol5_frog_reads_emperor"},
	{"n": "V", "name": "THE HIEROPHANT",
		"verdict": "The institution speaks. The child hears. The dress bites. The booth dials. The chapter is the chain. (Mostly.)",
		"unlock": "vol5_frog_reads_hierophant"},
	{"n": "VI", "name": "THE LOVERS",
		"verdict": "The card stays face-down. This was correct. The refusal is the reading. The pairs are accounted for. The accounting is not the consummation. (Mostly.)",
		"unlock": "vol5_frog_reads_lovers"},
	{"n": "VII", "name": "THE CHARIOT",
		"verdict": "The wreck is the wreck. The wreck was warned. The warning was not picked up. The chapter is the not-picking-up. (Mostly.)",
		"unlock": "vol5_frog_reads_chariot"},
	{"n": "VIII", "name": "STRENGTH",
		"verdict": "The hand is the hand. The lion is the dog. The crossing is the crossing nobody made into a story. (Mostly.)",
		"unlock": "vol5_frog_reads_strength"},
	{"n": "IX", "name": "THE HERMIT",
		"verdict": "The lantern is small. The tape is one. The agreement was kept on the second attempt. (Mostly.)",
		"unlock": "vol5_frog_reads_hermit"},
	{"n": "X", "name": "THE WHEEL OF FORTUNE",
		"verdict": "The wheel turned at the desk. The fortress had transparent walls. The lawyer worked the night. The night ended.",
		"unlock": "vol5_frog_reads_wheel"},
	{"n": "XI", "name": "JUSTICE",
		"verdict": "Refused. Flipped anyway. Split. The two readings are both correct. The shattered scales are the verdict carried forward. (Mostly.)",
		"unlock": "vol5_frog_reads_justice"},
	{"n": "XII", "name": "THE HANGED MAN",
		"verdict": "She waited. He did not answer. The voicemails were hers. The chapter was hers. (Mostly.)",
		"unlock": "vol5_frog_reads_hanged_man"},
	{"n": "XIII", "name": "DEATH",
		"verdict": "The hand was gloved. The ward had two empty beds. One died. One walked out. Both empties were correct emptings. (Mostly.)",
		"unlock": "vol5_frog_reads_death"},
	{"n": "XIV", "name": "TEMPERANCE",
		"verdict": "He did not write more on Tuesday than he had to. The discipline was the content. (Mostly.)",
		"unlock": "vol5_frog_reads_temperance"},
	{"n": "XV", "name": "THE DEVIL",
		"verdict": "He knew by call seven. He did not pick up. The bar opened again. (Mostly.)",
		"unlock": "vol5_frog_reads_devil"},
	{"n": "XVI", "name": "THE TOWER",
		"verdict": "The engine could not render itself failing. The log truncates itself. The file size increases. (Mostly.)",
		"unlock": "vol5_frog_reads_tower"},
	{"n": "XVII", "name": "THE STAR",
		"verdict": "She poured the water into the river. She included the smoke in inventory. She did not interpret it. (Mostly.)",
		"unlock": "vol5_frog_reads_star"},
	{"n": "XVIII", "name": "THE MOON",
		"verdict": "She read out of the static what she wrote on the page. The verbs came home. The candle was hers. (Mostly.)",
		"unlock": "vol5_frog_reads_moon"},
	{"n": "XIX", "name": "THE SUN",
		"verdict": "The pattern was four motes. The thank-you was 42 seconds long. The reply was correct silence. (Mostly.)",
		"unlock": "vol5_frog_reads_sun"},
	{"n": "XX", "name": "JUDGEMENT",
		"verdict": "Refused. Held. The gathering was rendered. The verdict was not. The gathering was enough. (Mostly.)",
		"unlock": "vol5_frog_reads_judgement"},
	{"n": "XXI", "name": "THE WORLD",
		"verdict": "I am reading this now. The wreath closes. The center is empty by design. The dancer was not coming. The corners are filled. The count is restored to sixty-four. The chapter ends.\n\n(MOSTLY.)\n\nI am the Frog. I know best, mostly. The mostly is the only part I am sure of. The mostly is the honest reading. The deck closes.\n\n                                                    —🐸",
		"unlock": "vol5_frog_reads_world"}
]

var _scroll: ScrollContainer = null
var _list_vbox: VBoxContainer = null
var _croak_at: float = 4.0


func _init() -> void:
	_diorama_title = "FROG KNOWS BEST, MOSTLY  ·  XXI THE WORLD  ·  closing oracle"
	_diorama_hint = "click any card row for the Frog's reading · esc to leave"
	_edge_wash_color = Color(0.50, 0.80, 0.50, 0.025)  # wreath green


func _build_content() -> void:
	var panel := PanelContainer.new()
	panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	panel.offset_top = 60
	panel.offset_left = 80
	panel.offset_right = -80
	panel.offset_bottom = -56
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.014, 0.020, 0.014, 0.96)
	sb.border_color = Color(0.50, 0.80, 0.50, 0.6)
	sb.set_border_width_all(1)
	panel.add_theme_stylebox_override("panel", sb)
	add_child(panel)
	var pad := MarginContainer.new()
	pad.add_theme_constant_override("margin_left", 32)
	pad.add_theme_constant_override("margin_right", 32)
	pad.add_theme_constant_override("margin_top", 20)
	pad.add_theme_constant_override("margin_bottom", 20)
	panel.add_child(pad)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 8)
	pad.add_child(vb)
	var head := Label.new()
	head.text = "FROG KNOWS BEST, MOSTLY\nclosing reading, sunset (qualified)"
	head.add_theme_color_override("font_color", Color(0.60, 0.95, 0.60))
	head.add_theme_font_size_override("font_size", 13)
	vb.add_child(head)
	var intro := RichTextLabel.new()
	intro.bbcode_enabled = false
	intro.fit_content = true
	intro.text = "I will read the deck I have been near. I will read it once, in order, with the qualifications I am allowed. The qualifications are mostly. The reading is mostly. The discipline of the reading is that the mostly is not a weakness — the mostly is the part that lets the reading be true."
	intro.add_theme_color_override("default_color", C_TEXT)
	intro.add_theme_font_size_override("normal_font_size", 12)
	vb.add_child(intro)
	_scroll = ScrollContainer.new()
	_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vb.add_child(_scroll)
	_list_vbox = VBoxContainer.new()
	_list_vbox.add_theme_constant_override("separation", 4)
	_list_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_scroll.add_child(_list_vbox)
	for entry_v in _ORACLE:
		var entry: Dictionary = entry_v
		var captured := entry
		var rb := Button.new()
		rb.flat = false
		rb.alignment = HORIZONTAL_ALIGNMENT_LEFT
		rb.text = "  %s — %s    (click to read)" % [str(entry["n"]), str(entry["name"])]
		rb.add_theme_color_override("font_color", Color(0.60, 0.95, 0.60))
		rb.add_theme_font_size_override("font_size", 12)
		rb.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
		var rsb := StyleBoxFlat.new()
		rsb.bg_color = Color(0, 0, 0, 0.25)
		rsb.border_color = Color(0.50, 0.80, 0.50, 0.3)
		rsb.border_width_left = 2
		rb.add_theme_stylebox_override("normal", rsb)
		var rsh := rsb.duplicate() as StyleBoxFlat
		rsh.bg_color = Color(0.50, 0.80, 0.50, 0.15)
		rsh.border_width_left = 4
		rb.add_theme_stylebox_override("hover", rsh)
		rb.pressed.connect(func() -> void: _show_entry(captured))
		_list_vbox.add_child(rb)

	var fetch := Label.new()
	fetch.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	fetch.offset_top = -22
	fetch.offset_bottom = -6
	fetch.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	fetch.text = "[the_frog (no demon role; the frog speaks for itself) // 22 verdicts // integrity MOSTLY]"
	fetch.add_theme_color_override("font_color", C_TEXT_DIM)
	fetch.add_theme_font_size_override("font_size", 12)
	fetch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(fetch)


func _show_entry(entry: Dictionary) -> void:
	var head := "%s — %s" % [str(entry["n"]), str(entry["name"])]
	var body := "the Frog speaks:\n\n" + str(entry["verdict"])
	reveal(head, body, str(entry["unlock"]))


# ── Ambient: 6 Hz tick + occasional croak ────────────────────────

var _tick_phase: float = 0.0
var _croak_phase: float = 0.0
var _croak_active: bool = false


func _on_diorama_tick(_delta: float) -> void:
	if _t >= _croak_at:
		_croak_active = true
		_croak_phase = 0.0
		_croak_at = _t + randf_range(18.0, 32.0)


func _ambient_sample(_phase: float, step: float) -> Vector2:
	_tick_phase += step * 6.0
	var tick := 0.0
	if fmod(_tick_phase, 1.0) < 0.04:
		tick = -0.03 * (1.0 - fmod(_tick_phase, 1.0) / 0.04)
	var noise := (randf() - 0.5) * 0.014
	var croak := 0.0
	if _croak_active:
		_croak_phase += step
		if _croak_phase < 0.42:
			var env: float = clamp(1.0 - _croak_phase / 0.42, 0.0, 1.0)
			croak = sin(_croak_phase * 130.0 * TAU) * env * 0.12 \
				+ sin(_croak_phase * 65.0 * TAU) * env * 0.08
		else:
			_croak_active = false
	var s = tick + noise + croak
	return Vector2(s, s)
