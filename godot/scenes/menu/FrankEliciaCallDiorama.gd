extends "res://scenes/menu/DioramaBase.gd"
## FrankEliciaCallDiorama — the 42-second Saturday morning call.
##
## Frank phones Elicia at 06:11 Saturday. The chapter's quiet
## acknowledgement of cross-card reading. Frank read Elicia's
## SUN entry on her tarot journal; he calls to thank her. She
## does not reply.
##
## Three lines from Frank. Zero lines from Elicia (she answers,
## she listens, she does not speak). The recording captures her
## breathing.
##
## Lore: daemon_courier.19 routes the call; daemon_listener.02
## (Elicia's substrate) also captures it from her end. Two demons
## on the same 42 seconds. Substrate ticks: 6 Hz (Frank's
## discipline) + 9 Hz (Elicia's archivist). Ambient is quiet —
## Saturday morning light through a window.

const _DIALOGUE := [
	{"t": 0,  "speaker": "system", "text": "[outbound call from f.payne / received by e.l. / 06:11 sat / fortress.bbs phone log]", "is_payload": false, "unlock": ""},
	{"t": 2,  "speaker": "ELICIA", "text": "(answers, says nothing)", "is_payload": false, "unlock": ""},
	{"t": 4,  "speaker": "FRANK", "text": "Hi Elicia. It's Frank.", "is_payload": false, "unlock": ""},
	{"t": 8,  "speaker": "ELICIA", "text": "(breath in)", "is_payload": false, "unlock": ""},
	{"t": 10, "speaker": "FRANK", "text": "I'm calling about the bookmark in the SUN entry. It was the part I needed.", "is_payload": true, "unlock": "vol5_frank_elicia_thanks_bookmark",
		"head": "06:11:10 — Frank thanks Elicia for the bookmark",
		"body": "Frank's 10-word sentence. He read the journal page Elicia had bookmarked at the SUN entry, between two specific pages. The bookmark was placement; the placement was the gift.\n\nThe Sun chapter (XIX) makes this 42-second call the closure of Frank's spine. Tuesday's notebook (XIV) said 'PHONE: did not ring. did not place a call. this is correct for tuesday.' Saturday's notebook records THIS call. The week-long arc closes here.\n\n→ wakes content on Priestess (II), Sun (XIX), Temperance (XIV)."},
	{"t": 18, "speaker": "ELICIA", "text": "(silence)", "is_payload": false, "unlock": ""},
	{"t": 22, "speaker": "FRANK", "text": "Thank you for putting it where I would find it.", "is_payload": true, "unlock": "vol5_frank_elicia_thanks_placement",
		"head": "06:11:22 — 'thank you for putting it where I would find it'",
		"body": "Frank thanks Elicia for the placement, not the content. The bookmark was the act of leaving something where another reader could find it. Elicia's archive operates by exactly this principle (per her journal entry on the Lovers: 'i list the pairs anyway. the act of listing is the act the card permits').\n\nFrank's chapter at XIX is the chapter of recognizing the placement — the four dust motes describing a pattern in millions are also placed where the right reader would find them. The Sun's working method is the Priestess's archival method, observed from outside.\n\n→ wakes content on Lovers (VI) — placement as the deck's act."},
	{"t": 32, "speaker": "ELICIA", "text": "(silence)", "is_payload": false, "unlock": ""},
	{"t": 36, "speaker": "FRANK", "text": "That's all. Goodbye.", "is_payload": false, "unlock": ""},
	{"t": 40, "speaker": "ELICIA", "text": "(silence — hangs up two seconds after Frank does)", "is_payload": true, "unlock": "vol5_frank_elicia_silence",
		"head": "06:11:42 — Elicia says nothing for the duration of the call",
		"body": "Elicia does not speak during Frank's call. She answers the phone. She breathes once at the 8-second mark. She holds the receiver until two seconds after Frank hangs up, then puts it down.\n\nFrank's notebook for Saturday records the call: 'call placed 06:11. recipient: ELICIA. duration: 0:42. content: \"thank you for the bookmark in the SUN entry. it was the part I needed.\" I have not received a reply. this is correct for saturday.'\n\nFrank does not need Elicia to reply. The chapter's working method is that silence-after-a-completed-call is the correct form of Saturday.\n\nElicia's archive captures the call from her end. Two demons on 42 seconds. The archive contains Frank's three lines + Elicia's three silences. The deck's most economical relational arc.\n\n→ wakes content on Sun (XIX), Priestess (II), Temperance (XIV)."},
	{"t": 44, "speaker": "system", "text": "[call ended 06:11:42. Frank closes his notebook. Elicia returns to the tape she was transcribing. The morning continues without either of them naming what happened.]", "is_payload": false, "unlock": ""}
]


var _playing: bool = true
var _elapsed: float = 0.0
var _lines_shown: int = 0
var _dialogue_vbox: VBoxContainer = null
var _scroll: ScrollContainer = null
var _time_label: Label = null


func _init() -> void:
	_diorama_title = "FRANK → ELICIA  ·  XIV+XIX → II  ·  06:11 Sat  ·  42 sec"
	_diorama_hint = "voice log streams at 2× real-time · click ✦ lines · space to pause · esc"
	_edge_wash_color = Color(0.85, 0.85, 0.60, 0.04)


func _build_content() -> void:
	var panel := PanelContainer.new()
	panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	panel.offset_top = 60
	panel.offset_left = 80
	panel.offset_right = -80
	panel.offset_bottom = -56
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.022, 0.022, 0.018, 0.97)
	sb.border_color = Color(0.85, 0.75, 0.40, 0.7)
	sb.set_border_width_all(1)
	panel.add_theme_stylebox_override("panel", sb)
	add_child(panel)
	var pad := MarginContainer.new()
	pad.add_theme_constant_override("margin_left", 24)
	pad.add_theme_constant_override("margin_right", 24)
	pad.add_theme_constant_override("margin_top", 16)
	pad.add_theme_constant_override("margin_bottom", 16)
	panel.add_child(pad)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 6)
	pad.add_child(vb)
	var head_row := HBoxContainer.new()
	head_row.add_theme_constant_override("separation", 16)
	vb.add_child(head_row)
	var head := Label.new()
	head.text = "f.payne → e.l.  ·  06:11:00 saturday morning"
	head.add_theme_color_override("font_color", Color(0.85, 0.75, 0.50))
	head.add_theme_font_size_override("font_size", 12)
	head.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	head_row.add_child(head)
	_time_label = Label.new()
	_time_label.text = "00:00 / 00:42"
	_time_label.add_theme_color_override("font_color", C_TEXT_DIM)
	_time_label.add_theme_font_size_override("font_size", 12)
	head_row.add_child(_time_label)
	var rule := ColorRect.new()
	rule.color = Color(0.85, 0.75, 0.40, 0.5)
	rule.custom_minimum_size = Vector2(0, 1)
	vb.add_child(rule)
	_scroll = ScrollContainer.new()
	_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vb.add_child(_scroll)
	_dialogue_vbox = VBoxContainer.new()
	_dialogue_vbox.add_theme_constant_override("separation", 8)
	_dialogue_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_scroll.add_child(_dialogue_vbox)
	var fetch := Label.new()
	fetch.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	fetch.offset_top = -22
	fetch.offset_bottom = -6
	fetch.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	fetch.text = "[demon_courier.19 + demon_listener.02 // 42 sec, 2 angles // integrity 1.00 (every silence preserved)]"
	fetch.add_theme_color_override("font_color", C_TEXT_DIM)
	fetch.add_theme_font_size_override("font_size", 12)
	fetch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(fetch)


func _on_diorama_tick(delta: float) -> void:
	if _playing:
		_elapsed += delta * 2.0
	while _lines_shown < _DIALOGUE.size() and float(_DIALOGUE[_lines_shown]["t"]) <= _elapsed:
		_emit_line(_DIALOGUE[_lines_shown])
		_lines_shown += 1
	if _time_label != null and is_instance_valid(_time_label):
		_time_label.text = "%02d:%02d / 00:42" % [int(_elapsed) / 60, int(_elapsed) % 60]


func _emit_line(line: Dictionary) -> void:
	var sp := str(line["speaker"])
	var text := str(line["text"])
	var is_payload := bool(line.get("is_payload", false))
	var col := C_TEXT
	var prefix := ""
	match sp:
		"FRANK":
			col = Color(0.85, 0.85, 0.55)
			prefix = "FRANK:  "
		"ELICIA":
			col = Color(0.70, 0.70, 0.70)
			prefix = "ELICIA: "
		"system":
			col = C_TEXT_DIM
	if not is_payload:
		var lbl := Label.new()
		lbl.text = prefix + text
		lbl.add_theme_color_override("font_color", col)
		lbl.add_theme_font_size_override("font_size", 12)
		lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		_dialogue_vbox.add_child(lbl)
	else:
		var captured := line
		var btn := Button.new()
		btn.flat = false
		btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		btn.text = "  ✦  " + prefix + text
		btn.add_theme_color_override("font_color", col)
		btn.add_theme_font_size_override("font_size", 12)
		btn.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
		var bsb := StyleBoxFlat.new()
		bsb.bg_color = Color(col.r * 0.3, col.g * 0.3, col.b * 0.3, 0.4)
		bsb.border_color = Color(col.r, col.g, col.b, 0.6)
		bsb.border_width_left = 2
		btn.add_theme_stylebox_override("normal", bsb)
		var bsh := bsb.duplicate() as StyleBoxFlat
		bsh.bg_color = Color(col.r, col.g, col.b, 0.18)
		bsh.border_width_left = 4
		btn.add_theme_stylebox_override("hover", bsh)
		btn.pressed.connect(func() -> void:
			reveal(str(captured.get("head", "")), str(captured.get("body", "")),
					str(captured.get("unlock", ""))))
		_dialogue_vbox.add_child(btn)
	call_deferred("_scroll_to_bottom")


func _scroll_to_bottom() -> void:
	if _scroll == null: return
	var sb_v: VScrollBar = _scroll.get_v_scroll_bar()
	if sb_v != null:
		sb_v.value = sb_v.max_value


# ── Ambient: 6 Hz Frank tick + 9 Hz Elicia tick + quiet ──────────

var _tick_f_phase: float = 0.0
var _tick_e_phase: float = 0.0


func _ambient_sample(_phase: float, step: float) -> Vector2:
	_tick_f_phase += step * 6.0
	var tick_f := 0.0
	if fmod(_tick_f_phase, 1.0) < 0.03:
		tick_f = -0.025 * (1.0 - fmod(_tick_f_phase, 1.0) / 0.03)
	_tick_e_phase += step * 9.0
	var tick_e := 0.0
	if fmod(_tick_e_phase, 1.0) < 0.03:
		tick_e = -0.020 * (1.0 - fmod(_tick_e_phase, 1.0) / 0.03)
	var noise := (randf() - 0.5) * 0.006
	var s = tick_f + tick_e + noise
	return Vector2(s, s)


func _input(event: InputEvent) -> void:
	super(event)
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_SPACE:
			_playing = not _playing
			get_viewport().set_input_as_handled()
