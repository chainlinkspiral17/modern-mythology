extends "res://scenes/menu/DioramaBase.gd"
## FrasierDantePaintingDiorama — the conversation that decided
## which word.
##
## Dante's office at D'Ambrosio Industrial, seven years before
## the painted vol5 chapters. Frasier is thirty-three; Dante is
## sixty-three. The painting is on the desk between them, wrapped
## in butcher paper. Inside: John Frank rendered as cosmic being
## in a white button-up, tie, and apron, holding a round drink
## tray. The painting will be unwrapped twice across the day —
## once now, once after Frasier leaves.
##
## The conversation is the moment Dante and Frasier each decide
## which word to use for what is happening. Dante decides on
## 'fired.' Frasier decides on 'quit.' Both decisions are honest;
## the words are not the same word but they describe the same
## boundary. Both people preserve their own version for the rest
## of their lives. The painting is preserved by both.
##
## Lore: demon_archivist.01 (Frasier's substrate at the spire.bbs)
## and demon_archivist.04 (Dante's office endpoint, dormant since
## the wreck) co-hold the recording. The substrate has waited
## seven years for someone to retrieve it; the un-named eventual
## listener is Alberto, after Dante is in Bed 6. Substrate: 6 Hz
## (Frasier's working rhythm) + 4 Hz (Dante's office) + the
## slight rustle of butcher paper across the desk.

const _DIALOGUE := [
	{"t": 0,    "speaker": "system", "text": "[recovered record / spire.bbs ↔ d'ambrosio_office.bbs / 7 years prior / dante's office, ground floor / butcher paper on the desk / two cups of cold coffee / no third party present]", "is_payload": false, "unlock": ""},
	{"t": 4,    "speaker": "DANTE",   "text": "Sit, Frasier.", "is_payload": false, "unlock": ""},
	{"t": 7,    "speaker": "FRASIER", "text": "Thank you.", "is_payload": false, "unlock": ""},
	{"t": 11,   "speaker": "DANTE",   "text": "You brought it.", "is_payload": false, "unlock": ""},
	{"t": 14,   "speaker": "FRASIER", "text": "I brought it.", "is_payload": false, "unlock": ""},
	{"t": 17,   "speaker": "DANTE",   "text": "May I.", "is_payload": false, "unlock": ""},
	{"t": 19,   "speaker": "FRASIER", "text": "Please.", "is_payload": true, "unlock": "vol5_painting_handed_over",
		"head": "the painting is handed across",
		"body": "Frasier slides the butcher-paper-wrapped canvas across the desk. The painting is the same size as the original sketch he made on a diner napkin three months earlier — about 18 by 24 inches.\n\nDante does not unwrap it yet. He places one hand flat on top of the paper and leaves it there for the length of the conversation. He will unwrap it after Frasier leaves.\n\nThe deck's most preserved object passes here from maker to keeper. Neither party calls it a gift; neither party calls it a payment.\n\n→ wakes content on Magician (I) and Emperor (IV)."},
	{"t": 28,   "speaker": "DANTE",   "text": "I will not ask you to explain it. I see what you saw.", "is_payload": false, "unlock": ""},
	{"t": 34,   "speaker": "FRASIER", "text": "Thank you.", "is_payload": false, "unlock": ""},
	{"t": 38,   "speaker": "DANTE",   "text": "John is — he is a good waiter.", "is_payload": true, "unlock": "vol5_dante_says_good_waiter",
		"head": "'a good waiter'",
		"body": "Dante calls John Frank 'a good waiter.' The phrase is the deck's quietest classification — Dante has just seen John rendered as cosmic being and his response is a labor description.\n\nThe deck's complicated villainy: Dante is not insulting John. He means it. He thinks John is a good waiter. He also thinks the painting is correct. He holds both readings simultaneously without registering the contradiction. The Emperor's chapter at IV is partly the chapter of a man who can see a cosmic being and call him by his position on the schedule.\n\nFrasier hears the phrase and does not correct it. He chose to give Dante the painting; the painting can say what it says without commentary.\n\n→ wakes content on Emperor (IV) and the John Frank thread."},
	{"t": 50,   "speaker": "FRASIER", "text": "He is.", "is_payload": false, "unlock": ""},
	{"t": 54,   "speaker": "DANTE",   "text": "I understand we will not continue.", "is_payload": true, "unlock": "vol5_dante_chooses_fired",
		"head": "Dante chooses 'fired'",
		"body": "Dante's phrase is carefully constructed: 'We will not continue.' He does not say 'I am letting you go.' He does not say 'I am terminating the contract.' But in his own working memory of this conversation, he will record it later — and tell Marta the next morning — as 'I had to let Frasier go.' He decides, in this moment, that he is the one ending the arrangement.\n\nThe deck's truth is reserved. The Frog at XXI does not say which of them ended the arrangement first. Both versions are honest within their own ledgers. Dante's ledger reads 'fired'; Frasier's ledger reads 'quit.' Neither ledger is the document of record.\n\n→ wakes content on Tower (XVI) and the Sinkhole Nexus thread (the firing/quitting ambiguity began at the Nexus, which the painting will not name)."},
	{"t": 70,   "speaker": "FRASIER", "text": "We will not.", "is_payload": true, "unlock": "vol5_frasier_chooses_quit",
		"head": "Frasier chooses 'quit'",
		"body": "Frasier's two words match Dante's — 'we will not.' But Frasier records the conversation internally as 'I quit on Tuesday.' He will tell his then-partner that night that he quit; he will tell his then-partner's housemate three years later that he quit; he will tell Elicia, when she asks for the archive, that he quit.\n\nThe gentleness of this exchange is that both men chose the same syntax and assigned themselves opposite roles within it. Neither corrects the other. Neither asks for the other's version. The conversation closes the arrangement without resolving the question.\n\nThe Magician chapter at I is partly the chapter of a man who learned, here, that the operative verb of a closing can be left undecided indefinitely.\n\n→ wakes content on Magician (I) and the painting-as-keepsake thread."},
	{"t": 88,   "speaker": "DANTE",   "text": "I would like to keep this.", "is_payload": false, "unlock": ""},
	{"t": 93,   "speaker": "FRASIER", "text": "Yes.", "is_payload": false, "unlock": ""},
	{"t": 97,   "speaker": "DANTE",   "text": "May I hang it in this room.", "is_payload": false, "unlock": ""},
	{"t": 101,  "speaker": "FRASIER", "text": "You may hang it anywhere you would like.", "is_payload": false, "unlock": ""},
	{"t": 106,  "speaker": "DANTE",   "text": "It will hang here.", "is_payload": true, "unlock": "vol5_painting_hangs_here",
		"head": "'it will hang here'",
		"body": "Dante commits to hanging the painting in this specific room — the office at D'Ambrosio Industrial, ground floor. He keeps the commitment. The painting hangs on the same wall for seven years. He moves it once, when the office is repainted, and then back to the same nail.\n\nAfter the Tower's collapse and the wreck and Dante's hospitalization, the painting will be removed from this wall by Alberto, in his role as next of kin. Alberto will not destroy it. Alberto will not sell it. Alberto will move it to the storage unit that contains the family's reserved objects, where it will hang on the inside of the unit's door, lit by the bare bulb, for as long as the unit is paid.\n\nThe Frog's reading at XXI on the painting: 'preserved by both.' The Frog does not specify whether the preservation is dignified.\n\n→ wakes content on Emperor (IV), Tower (XVI), and the redemption arc thread on Alberto."},
	{"t": 130,  "speaker": "DANTE",   "text": "I have an envelope for you. I asked Marta to prepare it.", "is_payload": false, "unlock": ""},
	{"t": 138,  "speaker": "FRASIER", "text": "Thank you. I will accept it.", "is_payload": false, "unlock": ""},
	{"t": 144,  "speaker": "DANTE",   "text": "It is not — I am not paying you for the painting.", "is_payload": true, "unlock": "vol5_envelope_not_for_painting",
		"head": "the envelope is not for the painting",
		"body": "Dante is explicit: the envelope is not payment for the painting. The envelope is severance. The painting is something else.\n\nThe distinction matters to Dante. He would rather the painting be a gift than a transaction. He has decided to receive it as a gift. He is therefore not willing to let the envelope blur the ledger.\n\nFrasier accepts the distinction. He takes the envelope. He does not open it in front of Dante. He will open it in his car, find that it contains six months of his usual contract fee, and put it in his account that evening. He will record the deposit in his ledger as 'severance, D'Ambrosio.' He will not record the painting in his ledger at all.\n\n→ wakes content on Emperor (IV) and Justice (XI)."},
	{"t": 168,  "speaker": "FRASIER", "text": "I understand.", "is_payload": false, "unlock": ""},
	{"t": 172,  "speaker": "DANTE",   "text": "Will you tell me what it is for.", "is_payload": false, "unlock": ""},
	{"t": 177,  "speaker": "FRASIER", "text": "(pause) I painted it because I saw him. That is all.", "is_payload": true, "unlock": "vol5_frasier_just_saw_him",
		"head": "'I painted it because I saw him'",
		"body": "Frasier offers Dante the only answer he is willing to give: the act of painting was not a statement, not a gift, not a critique. He saw John Frank. He painted what he saw.\n\nThe Magician chapter at I is partly the chapter of a man who has decided that seeing is its own act and does not require a thesis. Frasier's lemniscate at I is the figure-eight of attention; the painting is one of its loops.\n\nDante registers the answer as sufficient. He does not press. He has the painting. He has decided to hang it here. He does not need a paragraph from Frasier about meaning.\n\nThe deck's gentlest chapter-close: two men who do not agree on the verb of their parting agree to leave the painting unparaphrased.\n\n→ wakes content on Magician (I) and World (XXI)."},
	{"t": 200,  "speaker": "DANTE",   "text": "All right. Thank you, Frasier.", "is_payload": false, "unlock": ""},
	{"t": 206,  "speaker": "FRASIER", "text": "Thank you, Dante.", "is_payload": false, "unlock": ""},
	{"t": 211,  "speaker": "DANTE",   "text": "Will you take the back stairs out. I would prefer the floor not see you go.", "is_payload": true, "unlock": "vol5_back_stairs_out",
		"head": "'take the back stairs out'",
		"body": "Dante asks Frasier to leave by the back stairs so the office floor does not witness his departure. The request is the chapter's quietest dishonesty: if the floor does not see Frasier go, the floor will not know whether he was fired or quit. The ambiguity Dante wanted to preserve in language he now preserves in choreography.\n\nFrasier agrees. He takes the back stairs. He will tell two people in the next month — his then-partner and his accountant — that he 'took the back stairs.' Neither of them asks what he means.\n\nThe Magician card's later painted scene of Frasier walking the spire perimeter is partly the long form of this exit. Frasier became, after this Tuesday, a man who leaves rooms by the path that does not require explanation.\n\n→ wakes content on Magician (I) and Tower (XVI)."},
	{"t": 240,  "speaker": "FRASIER", "text": "I will.", "is_payload": false, "unlock": ""},
	{"t": 245,  "speaker": "DANTE",   "text": "Goodbye.", "is_payload": false, "unlock": ""},
	{"t": 249,  "speaker": "FRASIER", "text": "Goodbye, Dante.", "is_payload": false, "unlock": ""},
	{"t": 254,  "speaker": "system", "text": "[recording continues 8 minutes after frasier leaves. dante does not speak. paper rustles at 02:11 (the painting unwrapped). a chair scrapes at 04:48 (dante stands). picture hardware contacts the wall at 07:22 (the nail). dante sits again at 07:55. silence resumes. recording closes 10:18 / dante locks the office.]", "is_payload": true, "unlock": "vol5_painting_hung_alone",
		"head": "Dante hangs it alone",
		"body": "The recording continues for eight minutes after Frasier leaves. Dante unwraps the painting, finds the nail, hangs it, sits back down. He does not speak the entire time. demon_archivist.04 records the silence with the same fidelity as the conversation.\n\nThe deck's most preserved object is preserved by both parties because both parties needed it preserved. Dante hangs it because the painting tells him a truth about John Frank that Dante is grateful to know and unwilling to articulate. Frasier gave it because the painting tells him a truth about his own attention that he is grateful to have made and unwilling to caption.\n\nThe Frog's reading at XXI on this Tuesday: 'both kept it. both were right to keep it. the painting did not require any of the words around it.'\n\nVol6 forward seed: Alberto will eventually retrieve the recording — demon_archivist.04 was waiting for an authorized listener from the family side; Alberto becomes the only authorized listener after the wreck. He listens to it once. He decides not to ask his father which word was true. He moves the painting to the storage unit. He does not transcribe the recording.\n\n→ wakes content on Magician (I), Emperor (IV), and the redemption arc thread on Alberto."}
]

# Playback state
var _playing: bool = true
var _elapsed: float = 0.0
var _lines_shown: int = 0
var _dialogue_vbox: VBoxContainer = null
var _scroll: ScrollContainer = null
var _time_label: Label = null


func _init() -> void:
	_diorama_title = "FRASIER ↔ DANTE  ·  the painting handed across  ·  7 years before vol5"
	_diorama_hint = "recovered substrate · streams at 8× real-time · click ✦ moments · space to pause · esc"
	_edge_wash_color = Color(0.30, 0.22, 0.15, 0.04)


func _build_content() -> void:
	var panel := PanelContainer.new()
	panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	panel.offset_top = 60
	panel.offset_left = 80
	panel.offset_right = -80
	panel.offset_bottom = -56
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.024, 0.020, 0.018, 0.97)
	sb.border_color = Color(0.70, 0.55, 0.40, 0.7)
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
	head.text = "SPIRE.BBS  ↔  D'AMBROSIO_OFFICE.BBS  ·  Tuesday afternoon  ·  7y prior"
	head.add_theme_color_override("font_color", Color(0.82, 0.72, 0.60))
	head.add_theme_font_size_override("font_size", 12)
	head.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	head_row.add_child(head)
	_time_label = Label.new()
	_time_label.text = "00:00 / 10:18"
	_time_label.add_theme_color_override("font_color", C_TEXT_DIM)
	_time_label.add_theme_font_size_override("font_size", 12)
	head_row.add_child(_time_label)
	var rule := ColorRect.new()
	rule.color = Color(0.70, 0.55, 0.40, 0.5)
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
	fetch.text = "[demon_archivist.01 + demon_archivist.04 // 10:18 recovered // integrity 0.92 // retrieved by: reserved (a.marroquin)]"
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
		_time_label.text = "%02d:%02d / 10:18" % [int(_elapsed) / 60, int(_elapsed) % 60]


func _emit_line(line: Dictionary) -> void:
	var sp := str(line["speaker"])
	var text := str(line["text"])
	var is_payload := bool(line.get("is_payload", false))
	var col := C_TEXT
	var prefix := ""
	match sp:
		"FRASIER":
			col = Color(0.78, 0.68, 0.55)
			prefix = "FRASIER: "
		"DANTE":
			col = Color(0.85, 0.60, 0.50)
			prefix = "DANTE:   "
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


# ── Ambient: 6 Hz Frasier + 4 Hz Dante's office + paper rustle ──

var _tick_f_phase: float = 0.0
var _tick_d_phase: float = 0.0
var _next_rustle_at: float = 9.0


func _on_diorama_tick_audio() -> void:
	pass


func _ambient_sample(phase: float, step: float) -> Vector2:
	_tick_f_phase += step * 6.0
	var tick_f := 0.0
	if fmod(_tick_f_phase, 1.0) < 0.025:
		tick_f = -0.020 * (1.0 - fmod(_tick_f_phase, 1.0) / 0.025)
	_tick_d_phase += step * 4.0
	var tick_d := 0.0
	if fmod(_tick_d_phase, 1.0) < 0.025:
		tick_d = -0.018 * (1.0 - fmod(_tick_d_phase, 1.0) / 0.025)
	var rustle := 0.0
	if has_meta("rustle_t0"):
		var rt: float = phase - get_meta("rustle_t0")
		if rt >= 0.0 and rt < 0.20:
			rustle = (randf() - 0.5) * 0.04 * (1.0 - rt / 0.20)
		if rt > 0.20:
			remove_meta("rustle_t0")
	if _t >= _next_rustle_at:
		set_meta("rustle_t0", phase)
		_next_rustle_at = _t + randf_range(8.0, 18.0)
	var noise := (randf() - 0.5) * 0.008
	var s = tick_f + tick_d + rustle + noise
	return Vector2(s, s)


func _input(event: InputEvent) -> void:
	super(event)
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_SPACE:
			_playing = not _playing
			get_viewport().set_input_as_handled()
