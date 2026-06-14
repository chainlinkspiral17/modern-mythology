extends "res://scenes/menu/DioramaBase.gd"
## HierophantBoothDiorama — Father Quent's three booth calls.
##
## Sunday morning, 06:35-06:42. The vestibule booth of St. Jude's,
## three rows back from the rose window. Father Quent dials three
## numbers in succession; daemon_observer is patient enough to
## capture all three.
##
## Lore beat: daemon_observer's substrate signature is a 7 Hz tick
## — the rite's tempo. The ambient also carries a sustained low
## church-bell tone (~110 Hz, very faint) — the chapter's
## diegetic-but-pre-mass atmosphere. Each picked-up handset plays
## that call's synth-rhythm transcript scroll; clicking the
## transcript surfaces the cross-card payload.
##
## See pitches/05_hierophant.md for the source script.

const _CALLS := [
	{
		"id": "call_1_antonio",
		"label": "06:35 — Call 1: Antonio",
		"rect": [0.10, 0.46, 0.22, 0.34],
		"recipient": "Antonio",
		"duration_sec": 70,
		"transcript": [
			"[four rings before pickup]",
			"ANTONIO:  Yeah.",
			"QUENT:    Antonio. It's Quent.",
			"ANTONIO:  Father. It's — what time is it.",
			"QUENT:    Quarter to seven. I need you to do me a favor I'm not going to remember asking you for.",
			"ANTONIO:  Okay.",
			"QUENT:    Drive to Ember and Ash and tell Daigle I changed my mind about Thursday. Do not call. Drive. He doesn't take the call from this number anymore.",
			"ANTONIO:  Thursday is —",
			"QUENT:    Thursday is the scaffolding. I changed my mind.",
			"ANTONIO:  Okay. I'll go after the eleven.",
			"QUENT:    Go before the seven.",
			"ANTONIO:  Father. The seven is in twenty minutes.",
			"QUENT:    I know what time the seven is.",
			"ANTONIO:  Yeah okay. I'll go.",
			"QUENT:    Thank you.",
			"[Quent hangs up]"
		],
		"payload_head": "Call 1 — V → VII the booth dispatches the wreck",
		"payload_body": "Father Quent sends Antonio to Daigle to unmake a decision Quent had already made. The decision concerned the scaffolding. The scaffolding fell. Antonio drove to Daigle. The Chariot card's status panel reads 'quentin call complete'; this is the call.\n\nThe rite is twenty minutes away when Quent dials; the rite begins as Antonio is driving; the scaffolding falls during the rite. Three events in the same forty minutes. Father Quent does not know — or chooses not to know — that they are the same event.\n\n→ wakes content on Chariot (VII).",
		"unlock": "vol5_hierophant_call_1_played"
	},
	{
		"id": "call_2_natalie",
		"label": "06:38 — Call 2: unknown number (no answer)",
		"rect": [0.40, 0.46, 0.22, 0.34],
		"recipient": "(no answer)",
		"duration_sec": 32,
		"transcript": [
			"[six rings, no answer]",
			"[time-zone log: dial originated 06:38 CT; the recipient's device — Natalie's, in LA — registered the call as 23:47 PT incoming-decline, because PT was four hours behind CT on this day and the call shifted across the zone change]",
			"[Quent hangs up before voicemail]",
			"[no audio captured]"
		],
		"payload_head": "Call 2 — V → XII the call Natalie didn't pick up",
		"payload_body": "Natalie's phone log on the Hanged Man card shows an incoming-unknown decline at 23:47 PT. This is that call. Father Quent dialed; the device shifted across time zones in transit; Natalie was in someone else's apartment at the receiving end and saw the number, did not recognize it, did not answer.\n\nQuent does not leave a voicemail because the rite is fifteen minutes away. He moves on.\n\n→ wakes content on Hanged Man (XII).",
		"unlock": "vol5_hierophant_call_2_played"
	},
	{
		"id": "call_3_carlie",
		"label": "06:42 — Call 3: unidentified (Carlie?)",
		"rect": [0.70, 0.46, 0.22, 0.34],
		"recipient": "Carlie (probably)",
		"duration_sec": 22,
		"transcript": [
			"[one ring before pickup]",
			"VOICE-3:  — yes Father.",
			"QUENT:    Bring the car around at six fifty. Don't take Carlie.",
			"VOICE-3:  Yes Father.",
			"QUENT:    [hangs up]",
			"[Quent puts the receiver down. He stands. He walks toward the rose window. The painted scene begins where this call ends.]"
		],
		"payload_head": "Call 3 — V → vol6 the third recipient is held",
		"payload_body": "Quent does not name the third recipient. He instructs them not to take Carlie. Carlie is therefore both:\n  · someone in the third recipient's care, and\n  · someone Quent does not want at the car at 06:50.\n\nThe third recipient is on staff. The recipient says 'yes Father' twice. Quent trusts them with the car and the morning and the not-taking-of-Carlie. The recipient is the parish housekeeper, almost certainly.\n\nCarlie is the deck's deepest withheld name through vol5 — only known to be A) named, B) someone the housekeeper would otherwise bring along, C) someone Quent wants kept away from the car on Sunday morning, D) someone whose presence at the rite is conditional on the housekeeper's compliance.\n\n→ forward seed for vol6.",
		"unlock": "vol5_hierophant_call_3_played"
	}
]

const ASCII_VESTIBULE := """\

					   ST. JUDE'S VESTIBULE  ·  06:35 SUNDAY

   ╭─────────────────────────────────────────────────────────────────╮
   │                                                                 │
   │      [stained glass overhead — pre-mass light blue-grey]        │
   │                                                                 │
   │                                                                 │
   │     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐          │
   │     │ ┌────┐       │ │ ┌────┐       │ │ ┌────┐       │          │
   │     │ │ ☎  │       │ │ │ ☎  │       │ │ │ ☎  │       │          │
   │     │ └────┘       │ │ └────┘       │ │ └────┘       │          │
   │     │              │ │              │ │              │          │
   │     │ [CALL 1]     │ │ [CALL 2]     │ │ [CALL 3]     │          │
   │     │ 06:35 Antonio│ │ 06:38 no ans │ │ 06:42 Carlie?│          │
   │     │              │ │              │ │              │          │
   │     │ click to     │ │ click to     │ │ click to     │          │
   │     │  pick up     │ │  pick up     │ │  pick up     │          │
   │     └──────────────┘ └──────────────┘ └──────────────┘          │
   │                                                                 │
   │                                                                 │
   │     ─────  parish booth — the only working phones in St. Jude's │
   │     ─────  the housekeeper is on the rectory line; not these    │
   │                                                                 │
   │                                                                 │
   │     vestibule clock: 06:42  ·  rose window glints at 06:58      │
   │                                                                 │
   ╰─────────────────────────────────────────────────────────────────╯

					   daemon_observer.05 // st_judes.bbs // 3 calls
							  integrity 0.94 (call 2 audio absent)
"""

# Playback for the active call (the one the player picked up)
var _active_call: int = -1
var _call_elapsed: float = 0.0
var _line_idx: int = -1
var _transcript_vbox: VBoxContainer = null
var _call_panel: PanelContainer = null

# Ambient state — 7 Hz tick + low sustained church-bell tone
var _tick_phase: float = 0.0
var _bell_phase: float = 0.0


func _init() -> void:
	_diorama_title = "ST. JUDE'S VESTIBULE  ·  V THE HIEROPHANT  ·  three booth calls"
	_diorama_hint = "click a handset to pick up · esc to leave"
	_edge_wash_color = Color(0.30, 0.40, 0.70, 0.03)  # cool stained-glass blue


func _build_content() -> void:
	# Main vestibule panel — left side
	var vestibule := PanelContainer.new()
	vestibule.set_anchors_preset(Control.PRESET_CENTER_LEFT)
	vestibule.offset_left = 40
	vestibule.offset_right = 700
	vestibule.offset_top = -260
	vestibule.offset_bottom = 260
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.012, 0.014, 0.022, 0.94)
	sb.border_color = C_GOLD
	sb.set_border_width_all(1)
	vestibule.add_theme_stylebox_override("panel", sb)
	add_child(vestibule)
	var lbl := Label.new()
	lbl.text = ASCII_VESTIBULE
	lbl.add_theme_color_override("font_color", C_TEXT)
	lbl.add_theme_font_size_override("font_size", 12)
	lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	vestibule.add_child(lbl)

	for i in _CALLS.size():
		var c: Dictionary = _CALLS[i]
		var captured := i
		make_hotspot(vestibule, c["rect"], str(c["label"]),
			func() -> void: _pick_up(captured))

	# Daemon-fetch banner (the ASCII layout already carries the role
	# line at the bottom — but a small reinforcement footer for
	# consistency with other dioramas)
	var fetch := Label.new()
	fetch.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	fetch.offset_top = -28
	fetch.offset_bottom = -10
	fetch.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	fetch.text = "[demon_observer.05 // st_judes.bbs // 3 calls recovered // integrity 0.94]"
	fetch.add_theme_color_override("font_color", C_TEXT_DIM)
	fetch.add_theme_font_size_override("font_size", 9)
	fetch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(fetch)


# ── Pick up a handset → scroll the transcript ────────────────────

func _pick_up(idx: int) -> void:
	_active_call = idx
	_call_elapsed = 0.0
	_line_idx = -1
	_build_call_panel(_CALLS[idx])


func _build_call_panel(call: Dictionary) -> void:
	if _call_panel != null and is_instance_valid(_call_panel):
		_call_panel.queue_free()
	_call_panel = PanelContainer.new()
	_call_panel.set_anchors_preset(Control.PRESET_CENTER_RIGHT)
	_call_panel.offset_left = -440
	_call_panel.offset_right = -40
	_call_panel.offset_top = -260
	_call_panel.offset_bottom = 260
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.03, 0.02, 0.04, 0.96)
	sb.border_color = C_GOLD_HI
	sb.set_border_width_all(1)
	_call_panel.add_theme_stylebox_override("panel", sb)
	add_child(_call_panel)
	var m := MarginContainer.new()
	m.add_theme_constant_override("margin_left", 14)
	m.add_theme_constant_override("margin_right", 14)
	m.add_theme_constant_override("margin_top", 12)
	m.add_theme_constant_override("margin_bottom", 12)
	_call_panel.add_child(m)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 6)
	m.add_child(vb)
	var head := Label.new()
	head.text = "▷ " + str(call["label"])
	head.add_theme_color_override("font_color", C_GOLD_HI)
	head.add_theme_font_size_override("font_size", 11)
	vb.add_child(head)
	var sub := Label.new()
	sub.text = "recipient: %s  ·  duration: %d s" % [str(call["recipient"]), int(call["duration_sec"])]
	sub.add_theme_color_override("font_color", C_TEXT_DIM)
	sub.add_theme_font_size_override("font_size", 9)
	vb.add_child(sub)
	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vb.add_child(scroll)
	_transcript_vbox = VBoxContainer.new()
	_transcript_vbox.add_theme_constant_override("separation", 4)
	_transcript_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(_transcript_vbox)
	# The "surface payload" button — visible only when transcript
	# finishes scrolling
	var payload_btn := Button.new()
	payload_btn.text = "[ ✦ surface payload ]"
	payload_btn.flat = true
	payload_btn.alignment = HORIZONTAL_ALIGNMENT_RIGHT
	payload_btn.add_theme_color_override("font_color", C_GOLD)
	payload_btn.visible = false
	payload_btn.name = "payload_btn"
	payload_btn.pressed.connect(func() -> void:
		reveal(str(call["payload_head"]), str(call["payload_body"]),
				str(call["unlock"])))
	vb.add_child(payload_btn)
	var dismiss := Button.new()
	dismiss.text = "[ × hang up ]"
	dismiss.flat = true
	dismiss.alignment = HORIZONTAL_ALIGNMENT_RIGHT
	dismiss.add_theme_color_override("font_color", C_TEXT_DIM)
	dismiss.pressed.connect(func() -> void:
		_active_call = -1
		if is_instance_valid(_call_panel):
			_call_panel.queue_free())
	vb.add_child(dismiss)


func _on_diorama_tick(delta: float) -> void:
	if _active_call < 0:
		return
	_call_elapsed += delta * 4.0  # 4x real-time pacing
	var call: Dictionary = _CALLS[_active_call]
	var lines: Array = call["transcript"]
	# Each line takes roughly duration / line_count seconds to appear,
	# but we floor each line to at least 0.7 s for legibility.
	var per_line: float = max(0.7, float(call["duration_sec"]) / float(lines.size()))
	var target_idx := int(_call_elapsed / per_line)
	if target_idx > lines.size() - 1:
		target_idx = lines.size() - 1
	while _line_idx < target_idx:
		_line_idx += 1
		if _transcript_vbox != null and is_instance_valid(_transcript_vbox):
			var l := Label.new()
			l.text = str(lines[_line_idx])
			l.add_theme_color_override("font_color", C_TEXT)
			l.add_theme_font_size_override("font_size", 10)
			l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			l.custom_minimum_size.x = 360
			_transcript_vbox.add_child(l)
	if _line_idx >= lines.size() - 1 and _call_panel != null:
		var pb: Variant = _call_panel.find_child("payload_btn", true, false)
		if pb != null:
			pb.visible = true


# ── Ambient: 7 Hz tick + 110 Hz church-bell sustain ──────────────

func _ambient_sample(_phase: float, step: float) -> Vector2:
	_tick_phase += step * 7.0
	var tick := 0.0
	if fmod(_tick_phase, 1.0) < 0.02:
		tick = -0.04 * (1.0 - fmod(_tick_phase, 1.0) / 0.02)
	_bell_phase += step * 110.0
	var bell := sin(_bell_phase * TAU) * 0.018
	var bell2 := sin(_bell_phase * 2.0 * TAU) * 0.008
	var noise := (randf() - 0.5) * 0.008
	var s = tick + bell + bell2 + noise
	return Vector2(s, s)
