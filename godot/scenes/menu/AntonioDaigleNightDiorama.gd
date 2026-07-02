extends "res://scenes/menu/DioramaBase.gd"
## AntonioDaigleNightDiorama — the night Antonio and Daigle invented
## "the chariot's flame" as their private name. Approximately a
## year before the wreck.
##
## Two characters at the bar after closing. Antonio is Dante's
## elder son. Daigle is the friend who keeps the friendship at
## bar-level, not family-level. The conversation drifts; the
## drink gets named; the friendship is recorded.
##
## Lore: demon_listener.15 archived this from the bar's BBS
## post-hoc — the recording was not made deliberately at the
## time. Daigle later requested the archive be preserved.
## Substrate ticks: 14 Hz (the Devil's amber-bulb flicker tempo)
## + occasional bottle clink. The ambient warms over time as the
## bar quiets down further.

const _DIALOGUE := [
	{"t": 0,    "speaker": "system", "text": "[archive recovered from bar BBS post-hoc / approx 14 months before the wreck / recording length 11:38]", "is_payload": false, "unlock": ""},
	{"t": 3,    "speaker": "DAIGLE", "text": "Last call was an hour ago.", "is_payload": false, "unlock": ""},
	{"t": 6,    "speaker": "ANTONIO", "text": "I know. I heard you say it.", "is_payload": false, "unlock": ""},
	{"t": 9,    "speaker": "DAIGLE", "text": "You're still sitting here.", "is_payload": false, "unlock": ""},
	{"t": 12,   "speaker": "ANTONIO", "text": "Yeah.", "is_payload": false, "unlock": ""},
	{"t": 16,   "speaker": "DAIGLE", "text": "(pours something) On the house.", "is_payload": false, "unlock": ""},
	{"t": 20,   "speaker": "ANTONIO", "text": "Thanks.", "is_payload": false, "unlock": ""},
	{"t": 30,   "speaker": "ANTONIO", "text": "My father's having a thing about the boat this week.", "is_payload": true, "unlock": "vol5_antonio_daigle_father_boat",
		"head": "00:30 — 'my father's having a thing about the boat'",
		"body": "Antonio mentions Dante by relation (his father), not by name. The relation IS the name in this bar between these two men. Daigle knows. Daigle doesn't ask.\n\nA year before the wreck, Antonio is already burdened by his father's boat decisions. The Wednesday morning barge walkthrough that opens the deck's later Dante+Quent voicelog has been a pattern for at least a year. Antonio knows he'll get called in eventually.\n\n→ wakes content on Emperor (IV) and Chariot (VII)."},
	{"t": 36,   "speaker": "DAIGLE", "text": "When isn't he.", "is_payload": false, "unlock": ""},
	{"t": 38,   "speaker": "ANTONIO", "text": "True.", "is_payload": false, "unlock": ""},
	{"t": 46,   "speaker": "ANTONIO", "text": "Alberto says he's going to start coming down here. He wants to know what you're like.", "is_payload": true, "unlock": "vol5_antonio_daigle_alberto_mentioned",
		"head": "00:46 — Antonio mentions Alberto by name",
		"body": "Antonio uses his brother's name aloud. He says Alberto is going to start coming down to Daigle's bar — to know what Daigle is like.\n\nAlberto wants to know what Daigle is like because Daigle is Antonio's friend, and Alberto is Antonio's brother, and brothers know each other through the other's friends. The chapter's economy of family-management is in this sentence: Alberto is using a bar to learn his brother.\n\nDaigle does not say whether he wants Alberto to come. Daigle is the friend of Antonio specifically; the relationship with Alberto would be a different friendship. Daigle will not have time to develop it before Antonio dies.\n\nThirteen months from now, Alberto will call Daigle nineteen times in fourteen minutes the night Antonio dies. Daigle will not pick up partly because he never quite learned what Alberto was like.\n\n→ wakes content on Wheel (X), Devil (XV), Chariot (VII)."},
	{"t": 56,   "speaker": "DAIGLE", "text": "What am I like.", "is_payload": false, "unlock": ""},
	{"t": 60,   "speaker": "ANTONIO", "text": "(considers) Patient. Kind. Cheap on bourbon.", "is_payload": false, "unlock": ""},
	{"t": 66,   "speaker": "DAIGLE", "text": "I don't pour bourbon for people I don't like. The price is the affection.", "is_payload": false, "unlock": ""},
	{"t": 74,   "speaker": "ANTONIO", "text": "(laughs) Then tell Alberto that. That's a thing he'll understand.", "is_payload": false, "unlock": ""},
	{"t": 80,   "speaker": "DAIGLE", "text": "He's a numbers man.", "is_payload": false, "unlock": ""},
	{"t": 84,   "speaker": "ANTONIO", "text": "He's a numbers man. Yeah.", "is_payload": false, "unlock": ""},
	{"t": 92,   "speaker": "ANTONIO", "text": "He's not — he's not like me. He's the one my father — never mind.", "is_payload": true, "unlock": "vol5_antonio_daigle_succession_avoided",
		"head": "01:32 — Antonio doesn't finish the sentence",
		"body": "Antonio starts to say something about the succession — 'He's the one my father —' — and stops. He doesn't finish. Daigle doesn't push.\n\nThe sentence Antonio doesn't complete is the chapter's deepest exchange. Antonio knows what their father is doing about the empire. He starts to tell Daigle. He doesn't.\n\nThe Lovers' refusal as a working method: Antonio refuses to consummate a sentence about his brother's place in the inheritance. The Devil's UNCOMFORTABLE INSIDE in retrospective register: Daigle has been holding the half-finished sentence for fourteen months.\n\n→ wakes content on Emperor (IV), Wheel (X), Lovers (VI)."},
	{"t": 102,  "speaker": "DAIGLE", "text": "(quiet) Yeah.", "is_payload": false, "unlock": ""},
	{"t": 108,  "speaker": "system", "text": "[50 second pause. bottle clink. Daigle pouring another for himself.]", "is_payload": false, "unlock": ""},
	{"t": 168,  "speaker": "DAIGLE", "text": "What are you drinking.", "is_payload": false, "unlock": ""},
	{"t": 172,  "speaker": "ANTONIO", "text": "Whatever you put in the glass.", "is_payload": false, "unlock": ""},
	{"t": 176,  "speaker": "DAIGLE", "text": "It's mezcal, lime, chili, splash of orange. I burned the rim.", "is_payload": false, "unlock": ""},
	{"t": 184,  "speaker": "ANTONIO", "text": "It's good.", "is_payload": false, "unlock": ""},
	{"t": 188,  "speaker": "DAIGLE", "text": "Yeah. It needs a name.", "is_payload": false, "unlock": ""},
	{"t": 192,  "speaker": "ANTONIO", "text": "(considers) Call it after me.", "is_payload": false, "unlock": ""},
	{"t": 196,  "speaker": "DAIGLE", "text": "(laughs) The Antonio. Yeah. No.", "is_payload": false, "unlock": ""},
	{"t": 202,  "speaker": "ANTONIO", "text": "(laughs) Why not.", "is_payload": false, "unlock": ""},
	{"t": 206,  "speaker": "DAIGLE", "text": "Because everyone who orders it would have to say your name. They'd say it wrong.", "is_payload": false, "unlock": ""},
	{"t": 214,  "speaker": "ANTONIO", "text": "Hm. Fair.", "is_payload": false, "unlock": ""},
	{"t": 222,  "speaker": "ANTONIO", "text": "What about — okay, the chariot. The thing where you're holding the reins of two horses and they're pulling apart. That's what this drink does. Mezcal pulls one way, lime pulls the other. The chili holds them together.", "is_payload": true, "unlock": "vol5_antonio_daigle_chariot_named",
		"head": "03:42 — 'the chariot'",
		"body": "Antonio names the cocktail concept by invoking the tarot card. He describes the drink as the chariot card's two horses pulling apart, held by the chili.\n\nHe doesn't know he'll be the_charioteer on the BBS that runs his own restaurant's network, dead inside a wreck the deck calls the Chariot card. He's just using a tarot metaphor at the bar after closing.\n\nThe naming is the chapter's deepest dramatic irony: a year before the wreck, Antonio names a cocktail after the card that will become his death certificate. Daigle keeps the name on the menu after Antonio dies as both elegy and refusal of finality — the drink keeps being poured.\n\n→ wakes content on Chariot (VII) and Devil (XV)."},
	{"t": 240,  "speaker": "DAIGLE", "text": "(thinking) The chariot's flame. Because of the burned rim.", "is_payload": false, "unlock": ""},
	{"t": 246,  "speaker": "ANTONIO", "text": "(slowly) Yeah. The chariot's flame. That's good.", "is_payload": false, "unlock": ""},
	{"t": 252,  "speaker": "DAIGLE", "text": "It's ours. Don't tell people.", "is_payload": false, "unlock": ""},
	{"t": 256,  "speaker": "ANTONIO", "text": "I won't.", "is_payload": false, "unlock": ""},
	{"t": 260,  "speaker": "DAIGLE", "text": "(small laugh) When you order it, just say 'the usual.' I'll know.", "is_payload": false, "unlock": ""},
	{"t": 266,  "speaker": "ANTONIO", "text": "The usual.", "is_payload": false, "unlock": ""},
	{"t": 274,  "speaker": "system", "text": "[the conversation continues for another six minutes about lesser things — a baseball score, a cousin's wedding, the bar's leaking faucet. the recording captures all of it; daemon_listener marks it 'low-priority continuation.']", "is_payload": false, "unlock": ""},
	{"t": 670,  "speaker": "ANTONIO", "text": "I should go.", "is_payload": false, "unlock": ""},
	{"t": 674,  "speaker": "DAIGLE", "text": "Where are you going to drive to at this hour.", "is_payload": false, "unlock": ""},
	{"t": 680,  "speaker": "ANTONIO", "text": "Home. The river road.", "is_payload": true, "unlock": "vol5_antonio_daigle_river_road",
		"head": "11:20 — 'the river road'",
		"body": "Antonio names the route he'll take home. The river road. The same route he'll take to the wreck site fourteen months from now (the SMS thread: 'guy in the seat next to me at d'ambrosios this morning was the lawyer i told you about. nicola was there. i dont think she ate' — the breakfast he had on the morning of the wreck was on the river road).\n\nAntonio drives the river road from his bar to his home. He will drive the river road from his breakfast to his wreck. The road is the same. The trip is the same length on different mornings. The chapter is the chapter at the end of the road, every time.\n\n→ wakes content on Chariot (VII)."},
	{"t": 690,  "speaker": "DAIGLE", "text": "Drive slow.", "is_payload": false, "unlock": ""},
	{"t": 694,  "speaker": "ANTONIO", "text": "I always do.", "is_payload": false, "unlock": ""},
	{"t": 698,  "speaker": "system", "text": "[Antonio leaves. Daigle pours one more for himself and writes 'CHARIOT FLAME (priv)' on the small index card he keeps for menu drafts. The card goes in his pocket. The recording ends at 11:38. Fourteen months later he will pull the same card out and write 'pub' next to the entry — public — and put it on the chalkboard above the bar the same week Alberto begins calling.]", "is_payload": true, "unlock": "vol5_antonio_daigle_card_kept",
		"head": "11:38 — Daigle keeps the menu card",
		"body": "Daigle writes 'CHARIOT FLAME (priv)' on the menu draft card and pockets it. The card stays in his pocket for fourteen months. He pulls it out the week of the wreck and adds 'pub' (public) — the drink moves from private to menu in the week his friend dies.\n\nThe Devil chapter's chalkboard with THE CHARIOT'S FLAME chalked in is the chalkboard Daigle wrote a year and a week ago, in private ink, in the company of a man he is now grieving with cocktail signage. The bar serves the drink every night because the bar serves Antonio's absence every night.\n\nAlberto begins calling the same week. Alberto has not yet learned what Daigle is like. The brothers' relationship to Daigle is in the un-finished sentence Antonio refused to complete an hour and a half into this recording. Daigle is the bartender of a friendship he could not extend in time.\n\n→ wakes content on Devil (XV) and Wheel (X)."}
]


var _playing: bool = true
var _elapsed: float = 0.0
var _lines_shown: int = 0
var _dialogue_vbox: VBoxContainer = null
var _scroll: ScrollContainer = null
var _time_label: Label = null


func _init() -> void:
	_diorama_title = "ANTONIO & DAIGLE  ·  VII+XV  ·  the night the drink got named  ·  ~14 months before the wreck"
	_diorama_hint = "voice log streams at 8× real-time · click ✦ lines · space to pause · esc"
	_edge_wash_color = Color(0.95, 0.70, 0.30, 0.04)


func _build_content() -> void:
	var panel := PanelContainer.new()
	panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	panel.offset_top = 60
	panel.offset_left = 80
	panel.offset_right = -80
	panel.offset_bottom = -56
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.024, 0.018, 0.012, 0.97)
	sb.border_color = Color(0.95, 0.65, 0.25, 0.7)
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
	head.text = "DAIGLE'S BAR — after closing"
	head.add_theme_color_override("font_color", Color(0.95, 0.70, 0.30))
	head.add_theme_font_size_override("font_size", 11)
	head.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	head_row.add_child(head)
	_time_label = Label.new()
	_time_label.text = "00:00 / 11:38"
	_time_label.add_theme_color_override("font_color", C_TEXT_DIM)
	_time_label.add_theme_font_size_override("font_size", 10)
	head_row.add_child(_time_label)
	var rule := ColorRect.new()
	rule.color = Color(0.95, 0.65, 0.25, 0.5)
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
	fetch.text = "[demon_listener.15 // daigles_bar.bbs (archived post-hoc by sysop request) // 11:38 // integrity 0.96]"
	fetch.add_theme_color_override("font_color", C_TEXT_DIM)
	fetch.add_theme_font_size_override("font_size", 9)
	fetch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(fetch)


func _on_diorama_tick(delta: float) -> void:
	if _playing:
		_elapsed += delta * 8.0
	while _lines_shown < _DIALOGUE.size() and float(_DIALOGUE[_lines_shown]["t"]) <= _elapsed:
		_emit_line(_DIALOGUE[_lines_shown])
		_lines_shown += 1
	if _time_label != null and is_instance_valid(_time_label):
		_time_label.text = "%02d:%02d / 11:38" % [int(_elapsed) / 60, int(_elapsed) % 60]


func _emit_line(line: Dictionary) -> void:
	var sp := str(line["speaker"])
	var text := str(line["text"])
	var is_payload := bool(line.get("is_payload", false))
	var col := C_TEXT
	var prefix := ""
	match sp:
		"ANTONIO":
			col = Color(0.95, 0.55, 0.35)
			prefix = "ANTONIO: "
		"DAIGLE":
			col = Color(0.70, 0.55, 0.40)
			prefix = "DAIGLE:  "
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


# ── Ambient: 14 Hz amber flicker + bar quiet ─────────────────────

var _tick_phase: float = 0.0
var _bulb_phase: float = 0.0
var _next_clink_at: float = 8.0


func _on_diorama_tick_audio() -> void:
	pass


func _ambient_sample(phase: float, step: float) -> Vector2:
	_tick_phase += step * 14.0
	var tick := 0.0
	if fmod(_tick_phase, 1.0) < 0.04:
		tick = -0.035 * (1.0 - fmod(_tick_phase, 1.0) / 0.04)
	_bulb_phase += step
	var bulb_amplitude := 0.5 + 0.5 * sin(_bulb_phase * 0.7 * TAU)
	var bulb := sin(_bulb_phase * 110.0 * TAU) * 0.010 * bulb_amplitude
	var clink := 0.0
	if has_meta("clink_t0"):
		var ct: float = phase - get_meta("clink_t0")
		if ct >= 0.0 and ct < 0.12:
			clink = sin(ct * 1840.0 * TAU) * 0.06 * (1.0 - ct / 0.12)
		if ct > 0.12:
			remove_meta("clink_t0")
	if _t >= _next_clink_at:
		set_meta("clink_t0", phase)
		_next_clink_at = _t + randf_range(15.0, 30.0)
	var noise := (randf() - 0.5) * 0.010
	var s = tick + bulb + clink + noise
	return Vector2(s, s)


func _input(event: InputEvent) -> void:
	super(event)
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_SPACE:
			_playing = not _playing
			get_viewport().set_input_as_handled()
