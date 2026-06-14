extends "res://scenes/menu/DioramaBase.gd"
## WheelFilesDiorama — Erica Campbell's LAWYER_FILES_INDEX.EXE, 3:47 AM.
##
## The Fortress Menu with its four color-coded files. Each file
## opens to its contents; file 3 (CONTACT BLUE, Alberto's call log)
## is the rich one — eighteen rows of call data, each with Erica's
## red-ink marginalia, several wiring cross-card unlocks for the
## Emperor, Hierophant, Devil, and the 23 Feb unidentified caller.
##
## Lore beat: daemon_archivist.10 at 10 Hz substrate tick. The
## ambient is the night office — a desk lamp's faint 60 Hz hum, a
## monitor's pixel-clock subharmonic at 30 Hz, and the tick.
##
## See pitches/10_wheel_of_fortune.md for the source script.

const _FILES := [
	{
		"id": "file_1_corporate_slate",
		"label": "1 · Indexed Files       (Corporate Slate)",
		"color": Color(0.55, 0.55, 0.58),
		"summary": "Bulk of the PetroTex case — depositions, briefs, exhibits. Erica's bookmark is at exhibit 47 (Mrs. Romero's deposition video timestamps). Nothing here surprises. The bulk is the bulk.",
		"rows": [],
		"unlock": "vol5_wheel_file_corporate_slate_opened"
	},
	{
		"id": "file_2_denied_motion",
		"label": "2 · The Denied Motion   (Denied Red)",
		"color": Color(0.85, 0.30, 0.25),
		"summary": "Erica's first move at trial. Motion to compel production of internal PetroTex correspondence regarding the date-shift in Mrs. Romero's deposition record. DENIED by the bench three days ago. The chapter begins on the down-stroke; the wheel was already turning when Erica sat down.",
		"rows": [],
		"unlock": "vol5_wheel_file_denied_motion_opened"
	},
	{
		"id": "file_3_alberto_log",
		"label": "3 · Alberto's Call Log  (Contact Blue)",
		"color": Color(0.35, 0.55, 0.85),
		"summary": "Call log of Alberto J. Marroquín, dates reordered chronologically. 14 visible rows. Click any row to read Erica's marginalia.",
		"rows": [
			{
				"date": "10 Feb · 19:14:22",
				"io": "IN ",
				"to": "dante.d",
				"duration": "04:18",
				"status": "ANSWERED",
				"marginalia": "Dante called Alberto first. The 19:14 inbound is unprompted — Alberto didn't dial. Dante took it himself, four minutes eighteen seconds. Why does Dante call Alberto unprompted on a Wednesday evening?",
				"unlock": "vol5_wheel_dante_called_first"
			},
			{
				"date": "10 Feb · 19:18-19:20",
				"io": "OUT",
				"to": "dante.d ×3",
				"duration": "0:09 ×3",
				"status": "NO ANSWER",
				"marginalia": "Three callbacks in two minutes after Dante hung up. Alberto wanted to keep talking. Dante didn't. The 0:09 duration means each rang to voicemail-greeting then Alberto hung up — he didn't want to leave a message either.",
				"unlock": ""
			},
			{
				"date": "10 Feb · 19:42:08",
				"io": "IN ",
				"to": "dante.d",
				"duration": "06:51",
				"status": "ANSWERED",
				"marginalia": "Dante calls back at 19:42 — exactly 23m44s after he hung up the first time. That's IN the 22-25 min Dante callback window. Pattern confirmed. Content of the call recorded handwritten in Alberto's notebook p.47: 'wait until the audit clears.' THE AUDIT IS THE PRETROTEX DATE-SHIFT AUDIT. Dante is telling Alberto to wait until the audit clears. The audit cleared the wrong way per Quent (next row).",
				"unlock": "vol5_wheel_dante_audit_window"
			},
			{
				"date": "13 Feb · 09:11-09:14",
				"io": "IN ",
				"to": "q.booth",
				"duration": "00:02 / 0:00 / 03:14",
				"status": "CUT / NO PICKUP / ANSWERED",
				"marginalia": "Q.BOOTH = st. jude's parish phone, the same booth Quent dials antonio from on the morning of the rite. Quent calls Alberto THREE TIMES in three minutes. First call dropped (signal? Alberto in transit?). Second no pickup. Third answers. Content per Alberto p.51: 'the audit's clearing the wrong way. tell him.' Notation in Alberto's hand: 'Q. wouldn't say who him is on the line. I made him say it twice.' \n\nQuent KNEW he was being recorded. Quent is the witness who makes a record by knowing he's on record. That changes the whole shape of Quent's role in the case.",
				"unlock": "vol5_wheel_quent_recorded_himself"
			},
			{
				"date": "19 Feb · 22:00-22:14",
				"io": "OUT",
				"to": "daigle",
				"duration": "00:09 ×19",
				"status": "NO ANSWER ×19",
				"marginalia": "Alberto called Daigle NINETEEN TIMES IN FOURTEEN MINUTES on the night Antonio dies. Daigle did not pick up once. Alberto's notebook for the night reads only 'he wouldn't pick up. it's fine.'\n\nIt was not fine. Antonio died in the scaffolding fall that Alberto was calling about. Daigle knew by call seven and didn't pick up because he didn't want to be the person who knew. Daigle's morning-after note (see Devil XV) confesses this.\n\nFourteen minutes is a long time to keep dialing. Alberto knew before the wreck and tried to warn the only person who could have heard. The chapter's whole bondage is in the silence of the unpicked-up phone.",
				"unlock": "vol5_wheel_alberto_warned_daigle"
			},
			{
				"date": "23 Feb · 05:18:33",
				"io": "IN ",
				"to": "?",
				"duration": "00:04",
				"status": "ANSWERED",
				"marginalia": "Four seconds. Unattributed caller. Alberto answered, listened, hung up. Alberto's notebook for 23 Feb is BLANK — not even 'it's fine.' Just blank.\n\nThe four-second call is the deck's deepest withheld entity. Alberto would not write down who that was. Whoever it was, four seconds was enough for Alberto to know to hang up.\n\nForward seed. Daemon_archivist refuses to assign provenance.",
				"unlock": "vol5_wheel_unidentified_23feb"
			}
		],
		"unlock": "vol5_wheel_file_alberto_log_opened"
	},
	{
		"id": "file_4_settlement",
		"label": "4 · PetroTex Settlement (Settlement Gold)",
		"color": Color(0.90, 0.75, 0.30),
		"summary": "The settlement offer. Dollar amount redacted by Erica with a sharpie. Cover paragraph names Marta Romero as plaintiff and a co-plaintiff initialled only 'A.L.' (Anna Logue). The settlement requires both signatures. Anna has not signed; Marta has not been asked. The settlement is the wheel's exit — refused at Justice (XI), as the wireframe and shattered scales already imply.",
		"rows": [],
		"unlock": "vol5_wheel_file_settlement_opened"
	}
]

# UI state
var _active_file: int = -1
var _file_panel: PanelContainer = null
var _rows_vbox: VBoxContainer = null

# Ambient state
var _tick_phase: float = 0.0
var _lamp_phase: float = 0.0
var _monitor_phase: float = 0.0


func _init() -> void:
	_diorama_title = "LAWYER_FILES_INDEX.EXE  ·  X THE WHEEL OF FORTUNE  ·  Houston, 3:47 AM"
	_diorama_hint = "click a file row · click a call-log row to read marginalia · esc to leave"
	_edge_wash_color = Color(0.20, 0.40, 0.55, 0.03)  # corporate-monitor blue


func _build_content() -> void:
	# Fortress Menu — left side, fixed
	var menu := PanelContainer.new()
	menu.set_anchors_preset(Control.PRESET_CENTER_LEFT)
	menu.offset_left = 40
	menu.offset_right = 480
	menu.offset_top = -260
	menu.offset_bottom = 280
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.020, 0.026, 0.034, 0.96)
	sb.border_color = C_GOLD
	sb.set_border_width_all(1)
	menu.add_theme_stylebox_override("panel", sb)
	add_child(menu)

	var mpad := MarginContainer.new()
	mpad.add_theme_constant_override("margin_left", 16)
	mpad.add_theme_constant_override("margin_right", 16)
	mpad.add_theme_constant_override("margin_top", 14)
	mpad.add_theme_constant_override("margin_bottom", 14)
	menu.add_child(mpad)
	var mvb := VBoxContainer.new()
	mvb.add_theme_constant_override("separation", 12)
	mpad.add_child(mvb)

	var head := Label.new()
	head.text = "LAWYER_FILES_INDEX.EXE"
	head.add_theme_color_override("font_color", C_GOLD_HI)
	head.add_theme_font_size_override("font_size", 12)
	mvb.add_child(head)
	var status := Label.new()
	status.text = "POV: ERICA CAMPBELL  ·  STATUS: ARGUING AGAINST CHAOS\nWALLS: SLIGHTLY TRANSPARENT  ·  TIME: 03:47 AM"
	status.add_theme_color_override("font_color", C_TEXT_DIM)
	status.add_theme_font_size_override("font_size", 9)
	mvb.add_child(status)
	var rule := ColorRect.new()
	rule.color = C_GOLD
	rule.custom_minimum_size = Vector2(0, 1)
	mvb.add_child(rule)

	for i in _FILES.size():
		var f: Dictionary = _FILES[i]
		var btn := Button.new()
		btn.flat = false
		btn.text = "  " + str(f["label"])
		btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		btn.custom_minimum_size = Vector2(0, 36)
		btn.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
		btn.add_theme_color_override("font_color", f["color"])
		btn.add_theme_font_size_override("font_size", 11)
		var fbg := StyleBoxFlat.new()
		fbg.bg_color = Color(f["color"].r, f["color"].g, f["color"].b, 0.10)
		fbg.border_color = f["color"]
		fbg.border_width_left = 2
		btn.add_theme_stylebox_override("normal", fbg)
		var fbh := fbg.duplicate() as StyleBoxFlat
		fbh.bg_color = Color(f["color"].r, f["color"].g, f["color"].b, 0.25)
		fbh.border_width_left = 4
		btn.add_theme_stylebox_override("hover", fbh)
		var captured := i
		btn.pressed.connect(func() -> void: _open_file(captured))
		mvb.add_child(btn)

	# Floorplan inset
	var fp := Label.new()
	fp.text = "\nHOUSTON_OFFICE_FLOORPLAN:\n  · Erica's Desk    · Conference Room\n  · File Archives\n  · Painter's Space (EMPTY — Anna hasn't arrived)\n  · Office\n  · Glass Walls"
	fp.add_theme_color_override("font_color", C_TEXT_DIM)
	fp.add_theme_font_size_override("font_size", 9)
	mvb.add_child(fp)

	# Daemon-fetch banner
	var fetch := Label.new()
	fetch.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	fetch.offset_top = -28
	fetch.offset_bottom = -10
	fetch.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	fetch.text = "[demon_archivist.10 // fortress.bbs // 4 files indexed // integrity 0.99 (1 row redacted)]"
	fetch.add_theme_color_override("font_color", C_TEXT_DIM)
	fetch.add_theme_font_size_override("font_size", 9)
	fetch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(fetch)


func _open_file(idx: int) -> void:
	_active_file = idx
	if _file_panel != null and is_instance_valid(_file_panel):
		_file_panel.queue_free()
	var f: Dictionary = _FILES[idx]
	SaveSystem.mark_unlocked(str(f["unlock"]))

	_file_panel = PanelContainer.new()
	_file_panel.set_anchors_preset(Control.PRESET_CENTER_RIGHT)
	_file_panel.offset_left = -540
	_file_panel.offset_right = -40
	_file_panel.offset_top = -300
	_file_panel.offset_bottom = 300
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.024, 0.024, 0.034, 0.96)
	sb.border_color = f["color"]
	sb.set_border_width_all(1)
	sb.border_width_left = 4
	_file_panel.add_theme_stylebox_override("panel", sb)
	add_child(_file_panel)

	var m := MarginContainer.new()
	m.add_theme_constant_override("margin_left", 14)
	m.add_theme_constant_override("margin_right", 14)
	m.add_theme_constant_override("margin_top", 12)
	m.add_theme_constant_override("margin_bottom", 12)
	_file_panel.add_child(m)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 8)
	m.add_child(vb)

	var head := Label.new()
	head.text = "▷ " + str(f["label"])
	head.add_theme_color_override("font_color", f["color"])
	head.add_theme_font_size_override("font_size", 12)
	vb.add_child(head)
	var summary := RichTextLabel.new()
	summary.fit_content = true
	summary.bbcode_enabled = false
	summary.text = str(f["summary"])
	summary.add_theme_color_override("default_color", C_TEXT)
	summary.add_theme_font_size_override("normal_font_size", 10)
	vb.add_child(summary)

	var rows: Array = f.get("rows", [])
	if rows.size() > 0:
		var rule := ColorRect.new()
		rule.color = Color(f["color"].r, f["color"].g, f["color"].b, 0.5)
		rule.custom_minimum_size = Vector2(0, 1)
		vb.add_child(rule)
		var rows_head := Label.new()
		rows_head.text = "CALL LOG (chronological — click any row for Erica's marginalia)"
		rows_head.add_theme_color_override("font_color", C_GOLD)
		rows_head.add_theme_font_size_override("font_size", 9)
		vb.add_child(rows_head)
		var scroll := ScrollContainer.new()
		scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
		scroll.custom_minimum_size = Vector2(0, 360)
		vb.add_child(scroll)
		_rows_vbox = VBoxContainer.new()
		_rows_vbox.add_theme_constant_override("separation", 2)
		_rows_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		scroll.add_child(_rows_vbox)
		for row_v in rows:
			var row: Dictionary = row_v
			var captured := row
			var rb := Button.new()
			rb.flat = false
			rb.alignment = HORIZONTAL_ALIGNMENT_LEFT
			rb.text = "  %s  %s  %s  %s  %s" % [
				str(row.get("date","")),
				str(row.get("io","")),
				str(row.get("to","")),
				str(row.get("duration","")),
				str(row.get("status",""))
			]
			rb.add_theme_color_override("font_color", C_TEXT)
			rb.add_theme_font_size_override("font_size", 10)
			rb.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
			var rbsb := StyleBoxFlat.new()
			rbsb.bg_color = Color(0, 0, 0, 0.3)
			rbsb.border_color = Color(f["color"].r, f["color"].g, f["color"].b, 0.3)
			rbsb.border_width_bottom = 1
			rb.add_theme_stylebox_override("normal", rbsb)
			var rbsh := rbsb.duplicate() as StyleBoxFlat
			rbsh.bg_color = Color(f["color"].r, f["color"].g, f["color"].b, 0.15)
			rb.add_theme_stylebox_override("hover", rbsh)
			rb.pressed.connect(func() -> void:
				reveal(str(captured.get("date", "")) + "  " + str(captured.get("to", "")),
						"[Erica's red-ink marginalia]\n\n" + str(captured.get("marginalia", "")),
						str(captured.get("unlock", ""))))
			_rows_vbox.add_child(rb)

	var dismiss := Button.new()
	dismiss.text = "[ × close file ]"
	dismiss.flat = true
	dismiss.alignment = HORIZONTAL_ALIGNMENT_RIGHT
	dismiss.add_theme_color_override("font_color", C_TEXT_DIM)
	dismiss.pressed.connect(func() -> void:
		_active_file = -1
		if is_instance_valid(_file_panel):
			_file_panel.queue_free())
	vb.add_child(dismiss)


# ── Ambient: 10 Hz daemon_archivist + 60 Hz lamp + 30 Hz monitor ──

func _ambient_sample(_phase: float, step: float) -> Vector2:
	_tick_phase += step * 10.0
	var tick := 0.0
	if fmod(_tick_phase, 1.0) < 0.02:
		tick = -0.04 * (1.0 - fmod(_tick_phase, 1.0) / 0.02)
	_lamp_phase += step * 60.0
	var lamp := (-0.025 if fmod(_lamp_phase, 1.0) < 0.5 else 0.025)
	_monitor_phase += step * 30.0
	var monitor := sin(_monitor_phase * TAU) * 0.012
	var noise := (randf() - 0.5) * 0.010
	var s = tick + lamp + monitor + noise
	return Vector2(s, s)
