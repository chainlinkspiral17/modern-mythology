extends "res://scenes/menu/DioramaBase.gd"
## AlbertoMartaCallDiorama — the first redemption-arc call.
##
## Alberto calls Marta Romero at Ward C Bed 5. The week after
## Antonio dies. The week before Walpurgisnacht. Marta is
## comfortable, lucid, on the family's contracted hospital
## account. Alberto is on his office line at the firm.
##
## He has not called Marta in twenty years. He does not have a
## script. He has a list of things he needs to say. He gets
## through about half of them.
##
## Lore: two demons cover this conversation — demon_archivist.10
## (Alberto's substrate at the fortress.bbs) and demon_listener.13
## (Marta's substrate at ward_c.bbs). The recording is preserved
## by Alberto's request; he asks demon_archivist to keep it so he
## can listen back later. Substrate ticks: 10 Hz (Alberto's
## working rhythm) + 12 Hz (Ward C's daemon_archivist). The
## ambient also carries faint hospital sounds — IV beeps in the
## background, footsteps in the hall.

const _DIALOGUE := [
	{"t": 0,    "speaker": "system", "text": "[outbound call from a.marroquin / received at ward_c.bbs bed 5 / 14:18 / approx 8 days after the wreck / 6 days before walpurgisnacht]", "is_payload": false, "unlock": ""},
	{"t": 3,    "speaker": "MARTA",  "text": "Hello.", "is_payload": false, "unlock": ""},
	{"t": 6,    "speaker": "ALBERTO", "text": "Hi. Mrs. Romero. This is — this is Alberto. Marroquín. D'Ambrosio.", "is_payload": false, "unlock": ""},
	{"t": 14,   "speaker": "MARTA",  "text": "(small pause) Yes. I know who you are.", "is_payload": false, "unlock": ""},
	{"t": 18,   "speaker": "ALBERTO", "text": "I — yes. Okay. I'm sorry. I'm calling — I — okay.", "is_payload": true, "unlock": "vol5_alberto_marta_first_words",
		"head": "14:18:18 — Alberto stumbles",
		"body": "Alberto has not made a personal call to Marta in twenty years. The last time he spoke to her he was fourteen and she helped him with a button on a shirt his mother could not put on him because his mother was already gone.\n\nThe stumble is not anxiety; it is the absence of a script. Alberto has been making calls his whole adult life. None of them prepared him for this one. He has prepared a list; he forgets the first line of it.\n\n→ wakes content on Justice (XI) and Wheel (X)."},
	{"t": 28,   "speaker": "MARTA",  "text": "Take your time, Alberto.", "is_payload": false, "unlock": ""},
	{"t": 32,   "speaker": "ALBERTO", "text": "Thank you. I — okay. I'm calling because I want to tell you a few things. I don't expect you to — I'm not asking for anything. I just want to tell you them. Is that all right.", "is_payload": false, "unlock": ""},
	{"t": 46,   "speaker": "MARTA",  "text": "It's all right.", "is_payload": false, "unlock": ""},
	{"t": 50,   "speaker": "ALBERTO", "text": "Okay. The first thing is I know about the deposition. The dates were correct when you gave them. The dates were moved after. I have the original timestamps. I will give them to your lawyer.", "is_payload": true, "unlock": "vol5_alberto_marta_timestamps",
		"head": "14:18:50 — Alberto offers the timestamps",
		"body": "Alberto tells Marta he has the original deposition timestamps and will give them to Erica.\n\nThis is the first concrete act of the redemption arc. Alberto is admitting to the document fraud his family arranged and offering the evidence that would unwind it. He is doing this on his own initiative. He has not cleared it with anyone (his father is fading; his brother is dead).\n\nThe Justice chapter's shattered scales now have a different gravity: Alberto handed Erica the evidence she could not have obtained legally. The verdict the painted chapter renders as shattered may be a verdict the shatter was engineered to permit.\n\n→ wakes content on Justice (XI) and Wheel (X)."},
	{"t": 66,   "speaker": "MARTA",  "text": "(quiet) That's a thing you can do.", "is_payload": false, "unlock": ""},
	{"t": 70,   "speaker": "ALBERTO", "text": "Yes.", "is_payload": false, "unlock": ""},
	{"t": 74,   "speaker": "ALBERTO", "text": "The second thing is that I know what my family did to you. I don't mean the deposition. I mean the whole — the whole arrangement. The hours. The way you were paid. The years you weren't paid what you should have been.", "is_payload": false, "unlock": ""},
	{"t": 88,   "speaker": "MARTA",  "text": "(silence — 12 seconds)", "is_payload": false, "unlock": ""},
	{"t": 102,  "speaker": "MARTA",  "text": "Yes.", "is_payload": false, "unlock": ""},
	{"t": 106,  "speaker": "ALBERTO", "text": "I have run a calculation. I have a number. I am going to put the number in an account in your name. I am going to do this whether you want it or not, so that part isn't — that isn't a request. It will be there. I am telling you because if I didn't tell you you'd find out from a letter and that would be worse.", "is_payload": true, "unlock": "vol5_alberto_marta_calculation",
		"head": "14:19:46 — the calculation",
		"body": "Alberto has calculated what Marta should have been paid across her twenty years and is putting the number in an account in her name. He is doing this whether she wants it or not.\n\nThe gesture is awkward. Alberto knows it is awkward. He does it anyway because the alternative — discussing it, asking permission, granting Marta the burden of being grateful — would be worse. He chooses to be a person who acts on the calculation rather than a person who waits to be authorized to act.\n\nThe deck's complicated villainy: the family that underpaid her is the family that now overpays her. Neither cancels the other. Marta is not obligated to accept; she also is not obligated to refuse. The calculation is in the account.\n\n→ wakes content on Wheel (X), Justice (XI), Empress (III)."},
	{"t": 130,  "speaker": "MARTA",  "text": "(longer silence — 28 seconds)", "is_payload": false, "unlock": ""},
	{"t": 162,  "speaker": "MARTA",  "text": "Alberto.", "is_payload": false, "unlock": ""},
	{"t": 165,  "speaker": "ALBERTO", "text": "Yes.", "is_payload": false, "unlock": ""},
	{"t": 168,  "speaker": "MARTA",  "text": "How is your father.", "is_payload": true, "unlock": "vol5_alberto_marta_dante",
		"head": "14:21:08 — Marta asks after Dante",
		"body": "Marta asks after Dante. The question is not deference; it is information-gathering. She knows the family's chapter is closing; she wants to know how the closing is going for the head of household.\n\nThis is the chapter's most difficult moment for Alberto. The man Marta cleaned for twenty years is in Bed 6 of the same ward, six beds away, on the same floor. Alberto knows. Marta knows. Neither of them name the geometry.\n\n→ wakes content on Emperor (IV) and Death (XIII)."},
	{"t": 174,  "speaker": "ALBERTO", "text": "(small breath) He's in the ward. He's — he's not well. He doesn't always know where he is. He asked me about Antonio this morning and I had to tell him again.", "is_payload": false, "unlock": ""},
	{"t": 190,  "speaker": "MARTA",  "text": "I'm sorry.", "is_payload": false, "unlock": ""},
	{"t": 194,  "speaker": "ALBERTO", "text": "Thank you.", "is_payload": false, "unlock": ""},
	{"t": 198,  "speaker": "MARTA",  "text": "I'm sorry for him and I'm sorry for you.", "is_payload": false, "unlock": ""},
	{"t": 204,  "speaker": "ALBERTO", "text": "(small breath in) Yes. Thank you.", "is_payload": false, "unlock": ""},
	{"t": 212,  "speaker": "system", "text": "[40 second pause. footstep echoes in the hall on Marta's side. the IV pump cycles. Alberto's pen scratches against his desk on his side. neither party speaks.]", "is_payload": false, "unlock": ""},
	{"t": 256,  "speaker": "ALBERTO", "text": "I have one more thing. Then I'm going to let you rest. The third thing is that I was wrong to not call you sooner. I should have called when my mother — when I — I should have called you when I was sixteen. I didn't. I am calling you now. I am sorry that I am calling you now and not when I should have.", "is_payload": true, "unlock": "vol5_alberto_marta_should_have_called",
		"head": "14:22:16 — 'I should have called you when I was sixteen'",
		"body": "Alberto names his second failure: not calling Marta when his mother died at the Sinkhole. He was fourteen at the event; sixteen when he could have started reaching out. He did not.\n\nMarta helped his mother in the household until his mother was gone; Marta was one of the last people to see his mother alive. Marta would have had things to tell him. He did not call to ask. He calls now, twenty-some years later, with a worse reason.\n\nThe Sinkhole Nexus thread surfaces here in the redemption arc: Alberto is not just paying for the case; he is paying for the silence after the event. The redemption is partly a reckoning with the years he did not ask Marta what she knew about his mother's last days.\n\n→ wakes content on Empress (III)'s void-mother thread, the Sinkhole Nexus (across the deck), and the Lovers' pair lattice (a new line: ALBERTO & MARTA, post-hoc, asymmetric, not romance — accountability)."},
	{"t": 286,  "speaker": "MARTA",  "text": "(very quiet) Yes.", "is_payload": false, "unlock": ""},
	{"t": 290,  "speaker": "ALBERTO", "text": "I'm not asking you to forgive me. I'm telling you I know.", "is_payload": false, "unlock": ""},
	{"t": 298,  "speaker": "MARTA",  "text": "That is a kind of forgiveness I can give.", "is_payload": true, "unlock": "vol5_alberto_marta_kind_of_forgiveness",
		"head": "14:22:58 — 'a kind of forgiveness I can give'",
		"body": "Marta names what she can give: the acknowledgement of his knowing. She does not absolve him; she does not pretend to. She tells him that his knowing is a thing she can receive.\n\nThis is the deck's most precise act of grace. Marta is not exonerating; she is recognizing the difference between people who don't know what they did and people who do. Alberto has done the difficult work of telling her he knows. She can hold that.\n\nThe Lovers card's pair lattice gains a new entry: ALBERTO & MARTA — accountability acknowledged. Not romance, not friendship, not closure. A category the chapter at VI did not list because the chapter at VI did not yet contain it.\n\n→ wakes content on Lovers (VI)."},
	{"t": 318,  "speaker": "ALBERTO", "text": "Thank you.", "is_payload": false, "unlock": ""},
	{"t": 322,  "speaker": "MARTA",  "text": "You're welcome.", "is_payload": false, "unlock": ""},
	{"t": 326,  "speaker": "MARTA",  "text": "Alberto.", "is_payload": false, "unlock": ""},
	{"t": 329,  "speaker": "ALBERTO", "text": "Yes.", "is_payload": false, "unlock": ""},
	{"t": 332,  "speaker": "MARTA",  "text": "Tell my daughter I am proud of her. Tell her I said you said it. Don't make her wonder.", "is_payload": false, "unlock": ""},
	{"t": 344,  "speaker": "ALBERTO", "text": "I will. (small breath) I will tell her exactly that.", "is_payload": false, "unlock": ""},
	{"t": 352,  "speaker": "MARTA",  "text": "Thank you.", "is_payload": false, "unlock": ""},
	{"t": 356,  "speaker": "MARTA",  "text": "Get some rest.", "is_payload": false, "unlock": ""},
	{"t": 360,  "speaker": "ALBERTO", "text": "You too.", "is_payload": false, "unlock": ""},
	{"t": 364,  "speaker": "ALBERTO", "text": "Goodbye, Mrs. Romero.", "is_payload": false, "unlock": ""},
	{"t": 368,  "speaker": "MARTA",  "text": "Goodbye, Alberto.", "is_payload": false, "unlock": ""},
	{"t": 374,  "speaker": "system", "text": "[call ends 14:24:14 — duration 5:56. demon_archivist.10 holds the recording per Alberto's standing request. Marta's recording on the ward side is held by demon_listener.13. neither demon transcribes; both archive. Alberto does not listen back. he writes one line in his notebook: 'tell Anna.' then he files the timestamps for Erica.]", "is_payload": true, "unlock": "vol5_alberto_marta_call_closes",
		"head": "14:24:14 — Alberto files the timestamps",
		"body": "The call ends. Alberto does one administrative act before leaving his desk: he files the original deposition timestamps in a folder addressed to Erica Campbell's office, attaching no cover note.\n\nThe redemption arc continues from this call. Within a week, Marta will die in Ward C — the Death chapter's Bed 5 walkout. Alberto will attend the funeral. Anna will receive the message Marta asked him to pass. Erica will use the timestamps; the case will move. Dante will not know any of this; Dante is in Bed 6 looking at the ceiling.\n\nThe Frog's reading at XXI on Alberto: 'he began.' The Frog says (mostly) that the beginning is the chapter; the chapter is not the verdict; the verdict is reserved.\n\n→ wakes content on Justice (XI), Lovers (VI), World (XXI), Death (XIII)."}
]

# Playback state
var _playing: bool = true
var _elapsed: float = 0.0
var _lines_shown: int = 0
var _dialogue_vbox: VBoxContainer = null
var _scroll: ScrollContainer = null
var _time_label: Label = null


func _init() -> void:
	_diorama_title = "ALBERTO → MARTA  ·  X → XIII  ·  the first redemption call  ·  ~6 days before Walpurgisnacht"
	_diorama_hint = "voice log streams at 8× real-time · click ✦ lines · space to pause · esc"
	_edge_wash_color = Color(0.35, 0.50, 0.55, 0.04)


func _build_content() -> void:
	var panel := PanelContainer.new()
	panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	panel.offset_top = 60
	panel.offset_left = 80
	panel.offset_right = -80
	panel.offset_bottom = -56
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.020, 0.020, 0.022, 0.97)
	sb.border_color = Color(0.55, 0.65, 0.65, 0.7)
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
	head.text = "FORTRESS.BBS  →  WARD_C.BBS bed 5  ·  14:18 PT"
	head.add_theme_color_override("font_color", Color(0.75, 0.80, 0.80))
	head.add_theme_font_size_override("font_size", 12)
	head.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	head_row.add_child(head)
	_time_label = Label.new()
	_time_label.text = "00:00 / 05:56"
	_time_label.add_theme_color_override("font_color", C_TEXT_DIM)
	_time_label.add_theme_font_size_override("font_size", 12)
	head_row.add_child(_time_label)
	var rule := ColorRect.new()
	rule.color = Color(0.55, 0.65, 0.65, 0.5)
	rule.custom_minimum_size = Vector2(0, 1)
	vb.add_child(rule)
	_scroll = ScrollContainer.new()
	_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vb.add_child(_scroll)
	_dialogue_vbox = VBoxContainer.new()
	_dialogue_vbox.add_theme_constant_override("separation", 5)
	_dialogue_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_scroll.add_child(_dialogue_vbox)
	var fetch := Label.new()
	fetch.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	fetch.offset_top = -22
	fetch.offset_bottom = -6
	fetch.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	fetch.text = "[demon_archivist.10 + demon_listener.13 // 5:56 across two BBS endpoints // integrity 0.99 // recording preserved by sysop request: a.marroquin]"
	fetch.add_theme_color_override("font_color", C_TEXT_DIM)
	fetch.add_theme_font_size_override("font_size", 12)
	fetch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(fetch)


func _on_diorama_tick(delta: float) -> void:
	if _playing:
		_elapsed += delta * 8.0
	while _lines_shown < _DIALOGUE.size() and float(_DIALOGUE[_lines_shown]["t"]) <= _elapsed:
		_emit_line(_DIALOGUE[_lines_shown])
		_lines_shown += 1
	if _time_label != null and is_instance_valid(_time_label):
		_time_label.text = "%02d:%02d / 05:56" % [int(_elapsed) / 60, int(_elapsed) % 60]


func _emit_line(line: Dictionary) -> void:
	var sp := str(line["speaker"])
	var text := str(line["text"])
	var is_payload := bool(line.get("is_payload", false))
	var col := C_TEXT
	var prefix := ""
	match sp:
		"ALBERTO":
			col = Color(0.65, 0.75, 0.85)
			prefix = "ALBERTO: "
		"MARTA":
			col = Color(0.85, 0.75, 0.55)
			prefix = "MARTA:   "
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


# ── Ambient: 10 Hz Alberto + 12 Hz Marta-ward + IV beeps ─────────

var _tick_a_phase: float = 0.0
var _tick_m_phase: float = 0.0
var _next_beep_at: float = 6.0


func _on_diorama_tick_audio() -> void:
	pass


func _ambient_sample(phase: float, step: float) -> Vector2:
	_tick_a_phase += step * 10.0
	var tick_a := 0.0
	if fmod(_tick_a_phase, 1.0) < 0.025:
		tick_a = -0.025 * (1.0 - fmod(_tick_a_phase, 1.0) / 0.025)
	_tick_m_phase += step * 12.0
	var tick_m := 0.0
	if fmod(_tick_m_phase, 1.0) < 0.025:
		tick_m = -0.025 * (1.0 - fmod(_tick_m_phase, 1.0) / 0.025)
	var beep := 0.0
	if has_meta("beep_t0"):
		var bt: float = phase - get_meta("beep_t0")
		if bt >= 0.0 and bt < 0.08:
			beep = sin(bt * 800.0 * TAU) * 0.10 * (1.0 - bt / 0.08)
		if bt > 0.08:
			remove_meta("beep_t0")
	if _t >= _next_beep_at:
		set_meta("beep_t0", phase)
		_next_beep_at = _t + randf_range(4.0, 9.0)
	var noise := (randf() - 0.5) * 0.008
	var s = tick_a + tick_m + beep + noise
	return Vector2(s, s)


func _input(event: InputEvent) -> void:
	super(event)
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_SPACE:
			_playing = not _playing
			get_viewport().set_input_as_handled()
