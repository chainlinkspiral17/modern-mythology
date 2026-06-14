extends "res://scenes/menu/DioramaBase.gd"
## EricaAnnaCallDiorama — Erica Campbell + Anna Logue phone call.
##
## Three weeks before the painted Justice chapter. The call where
## Anna asks Erica to take her mother's case. Captured by
## daemon_courier.10 from the fortress.bbs phone log.
##
## Two voices in different colors. Erica (cool blue — courtroom).
## Anna (warm rose — studio). They have been friends since college.
## The call surfaces the friendship that predates the case; the
## Lovers' pair lattice ERICA & ANNA flips here.
##
## Lore: substrate ticks at 10 Hz (daemon_archivist's archive
## tempo from X) and 0 Hz (no second tick — Anna's chapter
## inherits the dual-POV silence from XI). Ambient carries a
## faint phone-line static under the dialogue.

const _DIALOGUE := [
	{"t": 0,    "speaker": "system", "text": "[call from a.logue / received 22:14 / fortress.bbs phone log row 218]", "is_payload": false, "unlock": ""},
	{"t": 2,    "speaker": "ANNA", "text": "Hi.", "is_payload": false, "unlock": ""},
	{"t": 4,    "speaker": "ERICA", "text": "Hey.", "is_payload": false, "unlock": ""},
	{"t": 6,    "speaker": "ANNA", "text": "Are you busy.", "is_payload": false, "unlock": ""},
	{"t": 8,    "speaker": "ERICA", "text": "I'm always busy. You know that. What's up.", "is_payload": false, "unlock": ""},
	{"t": 14,   "speaker": "ANNA", "text": "I need to ask you something. It's not — okay it's a work thing. I know I'm not supposed to call you about work things.", "is_payload": false, "unlock": ""},
	{"t": 22,   "speaker": "ERICA", "text": "(laughs) Anna. You called me at the firm twice last week. The work-thing rule is not a rule.", "is_payload": false, "unlock": ""},
	{"t": 28,   "speaker": "ANNA", "text": "Those were not work things. Those were — those were 'I need someone who is also a person to read this thing and tell me if it is real.' That is a different category.", "is_payload": false, "unlock": ""},
	{"t": 38,   "speaker": "ERICA", "text": "Is what I do. Tell me what you need.", "is_payload": false, "unlock": ""},
	{"t": 44,   "speaker": "ANNA", "text": "My mom.", "is_payload": true, "unlock": "vol5_erica_anna_marta_named",
		"head": "22:14:44 — 'my mom'",
		"body": "Anna names her mother. This is the moment Marta Romero becomes Erica's potential client. The deck's Justice chapter pivots on this two-syllable confidence — Anna trusts Erica with her mother.\n\nThree weeks later Erica will argue Marta's case. Marta will die in Ward C the morning of Walpurgisnacht. Anna's wireframe deconstruction is what survives.\n\n→ wakes content on Justice (XI) and the Lovers' Erica&Anna pair lattice entry (already live)."},
	{"t": 48,   "speaker": "ERICA", "text": "Okay.", "is_payload": false, "unlock": ""},
	{"t": 52,   "speaker": "ANNA", "text": "She — she got named in a deposition. PetroTex. The thing on the river. The — you would know what I mean.", "is_payload": false, "unlock": ""},
	{"t": 60,   "speaker": "ERICA", "text": "I know what you mean. PetroTex v. Romero et al. is on the firm's docket. I haven't read the filing. I will read it tonight.", "is_payload": false, "unlock": ""},
	{"t": 70,   "speaker": "ANNA", "text": "She wants — she said she wants to give the case to someone she trusts. She said she trusts whoever I trust.", "is_payload": true, "unlock": "vol5_erica_anna_trust_chain",
		"head": "22:15:10 — 'she trusts whoever I trust'",
		"body": "Marta's standard for choosing her lawyer is Anna's trust in someone. Anna trusts Erica because they have been friends since college (vol6 references will land here). The case is a triangulation of one woman's trust through two readers.\n\nMarta's letter on the back of the photo (Justice pitch+script doc) confirms this from Marta's side: 'The lawyer is Erica. She is the one I trust because she is your friend. That is the only standard I have. I do not know her otherwise.'\n\nThe friendship that predates the case is the case's foundation. The Lovers' pair lattice ERICA & ANNA flips at the Wheel diorama entry (live) — the friendship is named at the case-prep desk. The diorama renders the night the friendship became professional.\n\n→ wakes content on Justice (XI) and Lovers (VI)."},
	{"t": 80,   "speaker": "ERICA", "text": "(long pause) Anna.", "is_payload": false, "unlock": ""},
	{"t": 84,   "speaker": "ANNA", "text": "I know.", "is_payload": false, "unlock": ""},
	{"t": 86,   "speaker": "ERICA", "text": "I'm not — I'm trying to figure out how to say this. There is a thing about taking a case that involves a friend's mother. There are rules about it.", "is_payload": false, "unlock": ""},
	{"t": 96,   "speaker": "ANNA", "text": "I know there are rules.", "is_payload": false, "unlock": ""},
	{"t": 99,   "speaker": "ERICA", "text": "I have to think about it. I can think about it tonight. I can't say yes tonight.", "is_payload": false, "unlock": ""},
	{"t": 106,  "speaker": "ANNA", "text": "Okay.", "is_payload": false, "unlock": ""},
	{"t": 110,  "speaker": "ERICA", "text": "I'm not saying no.", "is_payload": false, "unlock": ""},
	{"t": 113,  "speaker": "ANNA", "text": "I know.", "is_payload": false, "unlock": ""},
	{"t": 116,  "speaker": "system", "text": "[long silence — 14 seconds. Erica's pen taps once on her desk. Anna breathes.]", "is_payload": false, "unlock": ""},
	{"t": 134,  "speaker": "ANNA", "text": "I'm sorry I asked.", "is_payload": true, "unlock": "vol5_erica_anna_anna_apologizes",
		"head": "22:16:14 — 'I'm sorry I asked'",
		"body": "Anna apologizes after 14 seconds of silence. The apology is not a withdrawal of the ask; it's an acknowledgement that the ask is hard.\n\nThe chapter's emotional weather: Anna does not want to put this on Erica. Erica does not want to refuse. Both want the same thing — for the case to land somewhere it can be argued well. Neither names the wanting.\n\nThe dual-POV mechanic at XI (the centerline split) is rehearsed here at X-minus-three-weeks: two readers looking at each other through a phone, neither able to see the other's room."},
	{"t": 138,  "speaker": "ERICA", "text": "Don't apologize. I'd be angry if you didn't ask. Then I'd be angrier when I heard you'd asked someone else.", "is_payload": false, "unlock": ""},
	{"t": 148,  "speaker": "ANNA", "text": "(quiet laugh) Yeah.", "is_payload": false, "unlock": ""},
	{"t": 152,  "speaker": "ERICA", "text": "I'll read tonight. I'll call you tomorrow. Whatever I decide, I'm telling you first.", "is_payload": false, "unlock": ""},
	{"t": 160,  "speaker": "ANNA", "text": "Okay.", "is_payload": false, "unlock": ""},
	{"t": 162,  "speaker": "ERICA", "text": "Anna — tell your mom — tell her I'm going to think about it. Don't say I said yes.", "is_payload": false, "unlock": ""},
	{"t": 170,  "speaker": "ANNA", "text": "I won't.", "is_payload": false, "unlock": ""},
	{"t": 173,  "speaker": "ANNA", "text": "Thank you.", "is_payload": false, "unlock": ""},
	{"t": 176,  "speaker": "ERICA", "text": "I haven't done anything.", "is_payload": false, "unlock": ""},
	{"t": 180,  "speaker": "ANNA", "text": "You're going to read it tonight. That is something.", "is_payload": true, "unlock": "vol5_erica_anna_thanks_for_reading",
		"head": "22:17:00 — 'you're going to read it tonight. that is something.'",
		"body": "Anna's closing line. Erica has not committed; Erica has agreed only to read. Anna names the reading as the something. This is the chapter's working method: attention is the gift, not the verdict.\n\nThe Justice card's whole register is set here — both readings are correct; the shattered scales are the verdict carried forward. The chapter does not pretend to resolve. The friendship continues; the case proceeds; both are correct, neither is consummated. The Lovers' refusal is acknowledged at X-minus-three-weeks before it's ever framed at VI.\n\n→ wakes content on Justice (XI), Lovers (VI)."},
	{"t": 188,  "speaker": "ERICA", "text": "Yeah. Okay. Get some sleep.", "is_payload": false, "unlock": ""},
	{"t": 193,  "speaker": "ANNA", "text": "You too.", "is_payload": false, "unlock": ""},
	{"t": 196,  "speaker": "ANNA", "text": "Goodnight.", "is_payload": false, "unlock": ""},
	{"t": 199,  "speaker": "ERICA", "text": "Goodnight.", "is_payload": false, "unlock": ""},
	{"t": 202,  "speaker": "system", "text": "[call ends 22:17:22 — duration 3:08. Erica's pen taps three times after the line goes dead. The recording continues for ten seconds, captures nothing more, then closes.]", "is_payload": false, "unlock": "vol5_erica_anna_call_complete"}
]

var _playing: bool = true
var _elapsed: float = 0.0
var _lines_shown: int = 0
var _dialogue_vbox: VBoxContainer = null
var _scroll: ScrollContainer = null
var _time_label: Label = null


func _init() -> void:
	_diorama_title = "ERICA → ANNA  ·  X+XI  ·  3 weeks before the Justice chapter  ·  22:14 PT"
	_diorama_hint = "voice log streams at 4× real-time · click ✦ lines for payload · space to pause · esc"
	_edge_wash_color = Color(0.40, 0.35, 0.50, 0.04)


func _build_content() -> void:
	var panel := PanelContainer.new()
	panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	panel.offset_top = 60
	panel.offset_left = 80
	panel.offset_right = -80
	panel.offset_bottom = -56
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.018, 0.018, 0.024, 0.97)
	sb.border_color = Color(0.55, 0.55, 0.65, 0.7)
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
	head.text = "FORTRESS.BBS — incoming call: a.logue"
	head.add_theme_color_override("font_color", Color(0.85, 0.70, 0.75))
	head.add_theme_font_size_override("font_size", 11)
	head.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	head_row.add_child(head)
	_time_label = Label.new()
	_time_label.text = "00:00 / 03:22"
	_time_label.add_theme_color_override("font_color", C_TEXT_DIM)
	_time_label.add_theme_font_size_override("font_size", 10)
	head_row.add_child(_time_label)
	var rule := ColorRect.new()
	rule.color = Color(0.55, 0.55, 0.65, 0.5)
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
	fetch.text = "[demon_courier.10 // fortress.bbs phone log row 218 // duration 3:22 // integrity 0.98]"
	fetch.add_theme_color_override("font_color", C_TEXT_DIM)
	fetch.add_theme_font_size_override("font_size", 9)
	fetch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(fetch)


func _on_diorama_tick(delta: float) -> void:
	if _playing:
		_elapsed += delta * 4.0
	while _lines_shown < _DIALOGUE.size() and float(_DIALOGUE[_lines_shown]["t"]) <= _elapsed:
		_emit_line(_DIALOGUE[_lines_shown])
		_lines_shown += 1
	if _time_label != null and is_instance_valid(_time_label):
		_time_label.text = "%02d:%02d / 03:22" % [int(_elapsed) / 60, int(_elapsed) % 60]


func _emit_line(line: Dictionary) -> void:
	var sp := str(line["speaker"])
	var text := str(line["text"])
	var is_payload := bool(line.get("is_payload", false))
	var col := C_TEXT
	var prefix := ""
	match sp:
		"ERICA":
			col = Color(0.55, 0.75, 0.90)
			prefix = "ERICA: "
		"ANNA":
			col = Color(0.95, 0.65, 0.70)
			prefix = "ANNA:  "
		"system":
			col = C_TEXT_DIM
	if not is_payload:
		var lbl := Label.new()
		lbl.text = prefix + text
		lbl.add_theme_color_override("font_color", col)
		lbl.add_theme_font_size_override("font_size", 10)
		lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		_dialogue_vbox.add_child(lbl)
	else:
		var captured := line
		var btn := Button.new()
		btn.flat = false
		btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		btn.text = "  ✦  " + prefix + text
		btn.add_theme_color_override("font_color", col)
		btn.add_theme_font_size_override("font_size", 10)
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


# ── Ambient: 10 Hz archivist tick + phone-line static ────────────

var _tick_phase: float = 0.0


func _ambient_sample(phase: float, step: float) -> Vector2:
	_tick_phase += step * 10.0
	var tick := 0.0
	if fmod(_tick_phase, 1.0) < 0.03:
		tick = -0.04 * (1.0 - fmod(_tick_phase, 1.0) / 0.03)
	var static_hum := sin(phase * 60.0 * TAU) * 0.008
	var noise := (randf() - 0.5) * 0.016
	var s = tick + static_hum + noise
	return Vector2(s, s)


func _input(event: InputEvent) -> void:
	super(event)
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_SPACE:
			_playing = not _playing
			get_viewport().set_input_as_handled()
