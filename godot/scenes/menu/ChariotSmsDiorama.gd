extends "res://scenes/menu/DioramaBase.gd"
## ChariotSmsDiorama — Antonio's outbound SMS thread, 06:42-07:11.
##
## The 29 minutes between Father Quent's booth call (V) and the
## Chariot wreck (VII). The thread is recovered by daemon_courier
## from ember.ash.rest.bbs after Antonio's device went dark at the
## scaffolding. Messages animate in at their real timestamps; the
## player can let the chapter run in real time, scrub forward, or
## click individual messages to surface cross-card payloads.
##
## Lore beat: daemon_courier is fast and brief but its tick rate
## ramps from 22 Hz at 06:42 toward 60 Hz at 07:11 — the substrate
## senses the impending crash and accelerates. The mid-frame ambient
## adds a faint engine drone that warms as the timestamp approaches
## the wreck minute.
##
## See pitches/07_chariot.md for the source script.

# Each message: timestamp (sec offset from 06:42:00), text body,
# optional unlock_key, optional cross_card payload.
const _MSGS := [
	{"ts": 0,    "from": "antonio", "text": "on my way", "unlock": ""},
	{"ts": 12,   "from": "antonio", "text": "daigle doesnt take ur calls anymore?", "unlock": ""},
	{"ts": 140,  "from": "antonio", "text": "ok ok im going. but i need to be back for the eleven. prep at nine. cant miss.", "unlock": ""},
	{"ts": 570,  "from": "antonio", "text": "hey. its dark on the river road. is the bridge open", "unlock": ""},
	{"ts": 575,  "from": "antonio", "text": "scratch that, bridge open", "unlock": ""},
	{"ts": 810,  "from": "antonio",
		"text": "guy in the seat next to me at d'ambrosios this morning was the lawyer i told you about. nicola was there. i dont think she ate",
		"unlock": "vol5_chariot_breakfast_witness_seen"},
	{"ts": 815,  "from": "antonio",
		"text": "what does it mean if a lawyer eats and the empress doesnt",
		"unlock": ""},
	{"ts": 880,  "from": "antonio", "text": "not your problem. nm", "unlock": ""},
	{"ts": 1200, "from": "antonio",
		"text": "daigle says fine. he says hes been waiting for u to change ur mind. he says u shouldnt have made up ur mind in the first place",
		"unlock": "vol5_chariot_daigle_relay_seen"},
	{"ts": 1208, "from": "antonio", "text": "his words not mine", "unlock": ""},
	{"ts": 1280, "from": "antonio",
		"text": "he wants u to come by tonight. he wants to talk about the boat",
		"unlock": ""},
	{"ts": 1390, "from": "antonio",
		"text": "the chariots flame. that's what we used to call the drink. its on the menu now. did u know that",
		"unlock": "vol5_chariot_flame_private_name"},
	{"ts": 1400, "from": "antonio", "text": "daigle put it on the menu", "unlock": ""},
	{"ts": 1530, "from": "antonio", "text": "bridge fog. cant see. driving slow", "unlock": ""},
	{"ts": 1610, "from": "antonio",
		"text": "scaffolding looks weird from here. its not — i dont know. its leaning. or its the fog",
		"unlock": ""},
	{"ts": 1700, "from": "antonio",
		"text": "q the scaffolding is leaning",
		"unlock": "vol5_chariot_scaffold_warned"},
	{"ts": 1735, "from": "antonio", "text": "q", "unlock": ""},
	{"ts": 1740, "from": "system", "text": "— device unresponsive —", "unlock": "vol5_chariot_device_offline"},
]

# Cross-card payloads — extended commentary attached to specific
# messages. Clicking the message after it lands surfaces the
# corresponding payload in the reveal panel.
const _PAYLOADS := {
	"vol5_chariot_breakfast_witness_seen": {
		"head": "06:55 — D'Ambrosio's, the morning of",
		"body": "Antonio sat next to Erica Campbell at breakfast. Nicola was at the same table. Nicola did not eat. Three POVs at the same diner at the same hour: the Chariot, the Wheel, the Empress. The deck's only triple-overlap meal. None of the three knew the other two were at the table.\n\n→ wakes content on Empress (III) and Wheel (X)."
	},
	"vol5_chariot_daigle_relay_seen": {
		"head": "07:02 — Daigle's relay",
		"body": "Daigle, who would not pick up Alberto's 19 calls thirteen days from now, picks up Antonio. 'Hes been waiting for u to change ur mind.' Father Quent had made up his mind about Thursday's scaffolding. Daigle was waiting for him to unmake it. The decision Antonio is delivering is the unmaking. The wreck is the late delivery.\n\n→ wakes content on Devil (XV)."
	},
	"vol5_chariot_flame_private_name": {
		"head": "07:05 — The Chariot's Flame",
		"body": "Daigle and Antonio had a private name for the cocktail. Daigle put it on the menu. The deck's signature drink on the Devil card is a private name surrendered to a menu. The middle barstool at Daigle's still serves it.\n\n→ wakes content on Devil (XV) and Chariot (VII)."
	},
	"vol5_chariot_scaffold_warned": {
		"head": "07:10 — Antonio saw it",
		"body": "Antonio sees the scaffolding leaning one minute before it falls. He texts Q. The text is delivered. Quent is in the rite at this minute; the phone is in his cassock pocket on vibrate.\n\nThe BBS diagnostic at the wreck site logs this as 'scaffolding check in progress.' The check was Antonio's eyes. The progress was Antonio's last text."
	},
	"vol5_chariot_device_offline": {
		"head": "07:11:40 — daemon_courier sign-off",
		"body": "the device fell with the scaffolding. daemon_courier was relaying texts via the cell tower mounted on the east scaffolding post. the cell tower fell with the device.\n\nintegrity of subsequent records degraded. daemon_courier requests re-fetch via alternate node. ember.ash.rest.bbs picks up the slack. the wreck site BBS sysop is no longer the_charioteer; it is whoever inherits the sysop key, which is — per ember.ash.rest.bbs ops manual — the first person to log in after a sysop-DOA event.\n\nthe key has not been claimed."
	},
}

# Playback state
var _playback_speed: float = 8.0  # 8x real time by default → 29 min in ~3:38
var _playing: bool = true
var _elapsed: float = 0.0
var _delivered_idx: int = -1     # last delivered message index

# UI refs
var _chat_vbox: VBoxContainer = null
var _scroll: ScrollContainer = null
var _time_label: Label = null
var _msg_buttons: Array = []     # parallel to _MSGS — null until delivered

# Ambient state
var _tick_phase: float = 0.0
var _engine_phase: float = 0.0
var _next_chime_at: float = -1.0   # set per-delivery


func _init() -> void:
	_diorama_title = "ANTONIO → QUENTIN  ·  VII THE CHARIOT  ·  06:42-07:11 CT"
	_diorama_hint = "messages animate in real time at 8× · click any delivered message · space to pause · esc to leave"
	_edge_wash_color = Color(0.95, 0.45, 0.20, 0.03)  # rust-orange


func _build_content() -> void:
	# Phone-screen panel — fixed proportions, centred
	var screen := PanelContainer.new()
	screen.set_anchors_preset(Control.PRESET_CENTER)
	screen.offset_left = -260; screen.offset_right = 260
	screen.offset_top = -360; screen.offset_bottom = 320
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.020, 0.018, 0.024, 0.96)
	sb.border_color = C_GOLD
	sb.set_border_width_all(1)
	sb.corner_radius_top_left = 20
	sb.corner_radius_top_right = 20
	sb.corner_radius_bottom_left = 20
	sb.corner_radius_bottom_right = 20
	screen.add_theme_stylebox_override("panel", sb)
	add_child(screen)

	var screen_vb := VBoxContainer.new()
	screen_vb.add_theme_constant_override("separation", 4)
	screen.add_child(screen_vb)

	# Phone header
	var header := PanelContainer.new()
	var hsb := StyleBoxFlat.new()
	hsb.bg_color = Color(0, 0, 0, 0.6)
	hsb.border_color = C_GOLD
	hsb.border_width_bottom = 1
	header.add_theme_stylebox_override("panel", hsb)
	screen_vb.add_child(header)
	var hpad := MarginContainer.new()
	hpad.add_theme_constant_override("margin_left", 12)
	hpad.add_theme_constant_override("margin_right", 12)
	hpad.add_theme_constant_override("margin_top", 8)
	hpad.add_theme_constant_override("margin_bottom", 8)
	header.add_child(hpad)
	var hrow := HBoxContainer.new()
	hpad.add_child(hrow)
	var to := Label.new()
	to.text = "to:  Q (Quentin)"
	to.add_theme_color_override("font_color", C_GOLD_HI)
	to.add_theme_font_size_override("font_size", 10)
	to.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hrow.add_child(to)
	_time_label = Label.new()
	_time_label.text = "06:42:00"
	_time_label.add_theme_color_override("font_color", C_GOLD)
	_time_label.add_theme_font_size_override("font_size", 10)
	hrow.add_child(_time_label)

	# Chat scroll area
	_scroll = ScrollContainer.new()
	_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_scroll.custom_minimum_size = Vector2(0, 580)
	screen_vb.add_child(_scroll)
	_chat_vbox = VBoxContainer.new()
	_chat_vbox.add_theme_constant_override("separation", 8)
	_chat_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var chat_pad := MarginContainer.new()
	chat_pad.add_theme_constant_override("margin_left", 14)
	chat_pad.add_theme_constant_override("margin_right", 14)
	chat_pad.add_theme_constant_override("margin_top", 10)
	chat_pad.add_theme_constant_override("margin_bottom", 10)
	chat_pad.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_scroll.add_child(chat_pad)
	chat_pad.add_child(_chat_vbox)

	# Initialise the parallel button array with nulls
	for _i in _MSGS.size():
		_msg_buttons.append(null)

	# Daemon-fetch banner — daemon_courier is the role for in-transit
	# messages.
	var fetch := Label.new()
	fetch.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	fetch.offset_top = -28
	fetch.offset_bottom = -10
	fetch.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	fetch.text = "[demon_courier.07 // ember.ash.rest.bbs // 18 messages relayed // integrity 0.91]"
	fetch.add_theme_color_override("font_color", C_TEXT_DIM)
	fetch.add_theme_font_size_override("font_size", 9)
	fetch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(fetch)

	# Playback controls — left of the phone
	var ctrls := VBoxContainer.new()
	ctrls.set_anchors_preset(Control.PRESET_CENTER_LEFT)
	ctrls.offset_left = 40
	ctrls.offset_right = 200
	ctrls.add_theme_constant_override("separation", 8)
	add_child(ctrls)
	var ctrl_title := Label.new()
	ctrl_title.text = "PLAYBACK"
	ctrl_title.add_theme_color_override("font_color", C_GOLD)
	ctrl_title.add_theme_font_size_override("font_size", 10)
	ctrls.add_child(ctrl_title)
	var pause_btn := Button.new()
	pause_btn.text = "[ ▸ play / pause ]"
	pause_btn.flat = true
	pause_btn.add_theme_color_override("font_color", C_TEXT)
	pause_btn.pressed.connect(_toggle_playing)
	ctrls.add_child(pause_btn)
	var skip_btn := Button.new()
	skip_btn.text = "[ ⏭ skip to end ]"
	skip_btn.flat = true
	skip_btn.add_theme_color_override("font_color", C_TEXT)
	skip_btn.pressed.connect(_skip_to_end)
	ctrls.add_child(skip_btn)
	var restart_btn := Button.new()
	restart_btn.text = "[ ⟲ restart ]"
	restart_btn.flat = true
	restart_btn.add_theme_color_override("font_color", C_TEXT)
	restart_btn.pressed.connect(_restart)
	ctrls.add_child(restart_btn)
	var speed_lbl := Label.new()
	speed_lbl.text = "speed: 8× real"
	speed_lbl.add_theme_color_override("font_color", C_TEXT_DIM)
	speed_lbl.add_theme_font_size_override("font_size", 9)
	ctrls.add_child(speed_lbl)


# ── Message delivery ──────────────────────────────────────────────

func _deliver_message(idx: int) -> void:
	if idx <= _delivered_idx:
		return
	_delivered_idx = idx
	var msg: Dictionary = _MSGS[idx]
	var from_id := str(msg.get("from", "antonio"))

	var row := PanelContainer.new()
	var rsb := StyleBoxFlat.new()
	if from_id == "system":
		rsb.bg_color = Color(0.20, 0.04, 0.04, 0.6)
		rsb.border_color = Color(1.0, 0.4, 0.4, 0.6)
	else:
		rsb.bg_color = Color(0.04, 0.06, 0.10, 0.7)
		rsb.border_color = Color(0.4, 0.6, 0.85, 0.5)
	rsb.set_border_width_all(1)
	rsb.corner_radius_top_left = 8
	rsb.corner_radius_top_right = 8
	rsb.corner_radius_bottom_left = 8
	rsb.corner_radius_bottom_right = 8
	row.add_theme_stylebox_override("panel", rsb)
	_chat_vbox.add_child(row)

	var rpad := MarginContainer.new()
	rpad.add_theme_constant_override("margin_left", 10)
	rpad.add_theme_constant_override("margin_right", 10)
	rpad.add_theme_constant_override("margin_top", 6)
	rpad.add_theme_constant_override("margin_bottom", 6)
	row.add_child(rpad)
	var rvb := VBoxContainer.new()
	rvb.add_theme_constant_override("separation", 2)
	rpad.add_child(rvb)

	var ts := Label.new()
	ts.text = "%s  ·  %s" % [_format_timestamp(int(msg["ts"])), from_id]
	ts.add_theme_color_override("font_color", C_TEXT_DIM)
	ts.add_theme_font_size_override("font_size", 8)
	rvb.add_child(ts)
	var body := Label.new()
	body.text = str(msg["text"])
	if from_id == "system":
		body.add_theme_color_override("font_color", Color(1.0, 0.6, 0.6))
	else:
		body.add_theme_color_override("font_color", C_TEXT)
	body.add_theme_font_size_override("font_size", 10)
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.custom_minimum_size.x = 460
	rvb.add_child(body)

	# If the message has a cross-card payload, the whole row is a
	# hotspot — clicking surfaces the payload in the reveal panel.
	var unlock_key := str(msg.get("unlock", ""))
	if unlock_key != "" and _PAYLOADS.has(unlock_key):
		var captured_key := unlock_key
		var btn := Button.new()
		btn.flat = true
		btn.text = ""
		btn.mouse_default_cursor_shape = Control.CURSOR_HELP
		btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		btn.tooltip_text = "click to surface payload"
		btn.add_theme_stylebox_override("normal", StyleBoxEmpty.new())
		var btnh := StyleBoxFlat.new()
		btnh.bg_color = Color(1, 0.85, 0.40, 0.10)
		btn.add_theme_stylebox_override("hover", btnh)
		btn.pressed.connect(func() -> void: _show_payload(captured_key))
		rvb.add_child(btn)
		# also fire the unlock immediately on delivery (the demon has
		# surfaced the message; clicking the row surfaces the meta
		# commentary)
		SaveSystem.mark_unlocked(unlock_key)

	# Auto-scroll to the bottom on each delivery
	var sb_v: VScrollBar = _scroll.get_v_scroll_bar()
	if sb_v != null:
		call_deferred("_scroll_to_bottom")

	# Chime
	_schedule_chime()


func _scroll_to_bottom() -> void:
	var sb_v: VScrollBar = _scroll.get_v_scroll_bar()
	if sb_v != null:
		sb_v.value = sb_v.max_value


func _show_payload(key: String) -> void:
	var payload: Dictionary = _PAYLOADS.get(key, {})
	if payload.is_empty():
		return
	reveal(str(payload.get("head", key)), str(payload.get("body", "")), key)


func _format_timestamp(ts_sec: int) -> String:
	var total := 6 * 3600 + 42 * 60 + ts_sec
	var hh := total / 3600
	var mm := (total / 60) % 60
	var ss := total % 60
	return "%02d:%02d:%02d" % [hh, mm, ss]


# ── Playback controls ─────────────────────────────────────────────

func _toggle_playing() -> void:
	_playing = not _playing


func _skip_to_end() -> void:
	_elapsed = float(_MSGS[_MSGS.size() - 1]["ts"]) + 1.0
	_check_deliveries()


func _restart() -> void:
	_playing = true
	_elapsed = 0.0
	_delivered_idx = -1
	for c in _chat_vbox.get_children():
		c.queue_free()


func _check_deliveries() -> void:
	for i in _MSGS.size():
		if i > _delivered_idx and float(_MSGS[i]["ts"]) <= _elapsed:
			_deliver_message(i)
	if _time_label != null:
		_time_label.text = _format_timestamp(int(_elapsed))


# ── Tick ──────────────────────────────────────────────────────────

func _on_diorama_tick(delta: float) -> void:
	if _playing:
		_elapsed += delta * _playback_speed
		_check_deliveries()


# ── Ambient: 22 → 60 Hz tick ramp + engine drone ──────────────────
# daemon_courier's substrate signature ramps as the timestamp
# approaches the wreck. At 06:42 (elapsed=0) the tick is 22 Hz; at
# 07:11 (elapsed=1740) it's 60 Hz. The engine drone warms in
# parallel.

func _ambient_sample(phase: float, step: float) -> Vector2:
	var progress: float = clamp(_elapsed / 1740.0, 0.0, 1.0)
	var tick_hz: float = lerp(22.0, 60.0, progress)
	_tick_phase += step * tick_hz
	var tick := 0.0
	if fmod(_tick_phase, 1.0) < 0.02:
		tick = -0.05 * (1.0 - fmod(_tick_phase, 1.0) / 0.02)
	# Engine drone — low rumble that warms with progress
	_engine_phase += step * 80.0
	var engine: float = sin(_engine_phase * TAU) * 0.04 * progress
	var engine2: float = sin(_engine_phase * 0.5 * TAU) * 0.03 * progress
	var noise: float = (randf() - 0.5) * (0.008 + 0.012 * progress)
	var chime := 0.0
	if _next_chime_at > 0.0 and phase < _next_chime_at + 0.2:
		var ch_t := phase - _next_chime_at
		if ch_t >= 0.0 and ch_t < 0.2:
			var env: float = clamp(1.0 - ch_t / 0.2, 0.0, 1.0)
			chime = sin(1320.0 * ch_t * TAU) * env * 0.12
		if ch_t > 0.2:
			_next_chime_at = -1.0
	var s = tick + engine + engine2 + noise + chime
	return Vector2(s, s)


func _schedule_chime() -> void:
	_next_chime_at = _aud_step + 0.01


# ── Input ─────────────────────────────────────────────────────────

func _input(event: InputEvent) -> void:
	super(event)
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_SPACE:
			_toggle_playing()
			get_viewport().set_input_as_handled()
