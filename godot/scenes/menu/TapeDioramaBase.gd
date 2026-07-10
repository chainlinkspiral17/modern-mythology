extends "res://scenes/menu/DioramaBase.gd"
## TapeDioramaBase — shared chrome for Elicia's archive tapes.
##
## The three Priestess-fetched cassette transcripts (ANYA_03,
## HERMIT_01, ENSEMBLE_01) share the same UI:
##   · top: cassette header card (label, side, duration, archivist
##     annotation)
##   · centre: waveform strip — events plotted at their timestamps,
##     with the player's playhead scrubbing across
##   · right: events list — each event is a clickable row; click
##     to seek the playhead AND reveal the event's content (the
##     transcribed line + Elicia's annotation, with optional
##     cross-card unlock)
##   · bottom: play / pause / restart controls (also SPACE)
##
## Subclasses override _init() to set the tape metadata, then
## populate _events. The base handles all rendering + scrubbing.
##
## Lore: daemon_listener.02 fetches all three. Substrate tick rate
## per-card (set in _init via _tape_tick_hz):
##   · Priestess (II) at 9 Hz — the archivist's metronome
##   · Hermit (IX) at 1 Hz — lantern fuel-tick
##   · Judgement (XX) at 0 Hz — held silence; the gesture is silent

# Subclass override fields
var _tape_id: String = "tape"
var _tape_header_label: String = "TAPE"
var _tape_side: String = "A"
var _tape_duration_sec: int = 1200
var _tape_archivist_note: String = ""
var _tape_tick_hz: float = 9.0
var _tape_fetch_banner: String = "[demon_listener.02 // priestess.bbs // 1 tape recovered]"
# Each event: { ts: int (seconds), label: String, body: String,
#               unlock: String, is_speech: bool }
var _events: Array = []

# UI state
var _playing: bool = false
var _elapsed: float = 0.0
var _playhead_marker: ColorRect = null
var _waveform_panel: PanelContainer = null
var _time_label: Label = null
var _events_vbox: VBoxContainer = null

# Ambient state
var _tick_phase: float = 0.0
var _hiss_phase: float = 0.0


func _build_content() -> void:
	# Cassette header card — top centre
	var card := PanelContainer.new()
	card.set_anchors_preset(Control.PRESET_TOP_WIDE)
	card.offset_top = 56
	card.offset_left = 60
	card.offset_right = -60
	card.offset_bottom = 56 + 80
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.030, 0.022, 0.018, 0.96)
	sb.border_color = C_GOLD
	sb.set_border_width_all(1)
	card.add_theme_stylebox_override("panel", sb)
	add_child(card)
	var cpad := MarginContainer.new()
	cpad.add_theme_constant_override("margin_left", 18)
	cpad.add_theme_constant_override("margin_right", 18)
	cpad.add_theme_constant_override("margin_top", 10)
	cpad.add_theme_constant_override("margin_bottom", 10)
	card.add_child(cpad)
	var cvb := VBoxContainer.new()
	cvb.add_theme_constant_override("separation", 4)
	cpad.add_child(cvb)
	var hd := Label.new()
	hd.text = "%s  ·  side %s  ·  duration %02d:%02d" % [_tape_header_label,
		_tape_side, _tape_duration_sec / 60, _tape_duration_sec % 60]
	hd.add_theme_color_override("font_color", C_GOLD_HI)
	hd.add_theme_font_size_override("font_size", 12)
	cvb.add_child(hd)
	if _tape_archivist_note != "":
		var note := Label.new()
		note.text = "annotation, e.l.: " + _tape_archivist_note
		note.add_theme_color_override("font_color", C_TEXT_DIM)
		note.add_theme_font_size_override("font_size", 12)
		note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		cvb.add_child(note)

	# Waveform strip — middle of screen
	_waveform_panel = PanelContainer.new()
	_waveform_panel.set_anchors_preset(Control.PRESET_CENTER_LEFT)
	_waveform_panel.offset_left = 60
	_waveform_panel.offset_right = -440
	_waveform_panel.offset_top = -80
	_waveform_panel.offset_bottom = 80
	var wsb := StyleBoxFlat.new()
	wsb.bg_color = Color(0.014, 0.012, 0.018, 0.94)
	wsb.border_color = C_GOLD
	wsb.set_border_width_all(1)
	_waveform_panel.add_theme_stylebox_override("panel", wsb)
	add_child(_waveform_panel)

	# Draw the waveform — flat for silence, spikes at events.
	# We render this as Control children: a row of small ColorRect
	# spikes at event timestamps, plus a playhead marker.
	var wfm := Control.new()
	wfm.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	wfm.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_waveform_panel.add_child(wfm)

	# Silence baseline — faint horizontal line
	var baseline := ColorRect.new()
	baseline.color = Color(C_TEXT_DIM.r, C_TEXT_DIM.g, C_TEXT_DIM.b, 0.4)
	baseline.set_anchors_preset(Control.PRESET_LEFT_WIDE)
	baseline.offset_top = -1
	baseline.offset_bottom = 1
	baseline.anchor_top = 0.5
	baseline.anchor_bottom = 0.5
	wfm.add_child(baseline)

	# Event spikes — sized by whether the event is speech or
	# ambient. Speech = tall spike; non-speech = short notch.
	for ev_v in _events:
		var ev: Dictionary = ev_v
		var frac: float = float(ev["ts"]) / float(_tape_duration_sec)
		var spike := ColorRect.new()
		var is_speech: bool = bool(ev.get("is_speech", true))
		spike.color = C_GOLD_HI if is_speech else C_GOLD
		spike.color.a = 0.85
		spike.anchor_left = frac
		spike.anchor_right = frac
		spike.offset_left = -1
		spike.offset_right = 1
		if is_speech:
			spike.anchor_top = 0.1
			spike.anchor_bottom = 0.9
		else:
			spike.anchor_top = 0.4
			spike.anchor_bottom = 0.6
		wfm.add_child(spike)

	# Playhead — animated vertical line tracking _elapsed
	_playhead_marker = ColorRect.new()
	_playhead_marker.color = Color(1, 0.4, 0.4, 0.85)
	_playhead_marker.anchor_left = 0
	_playhead_marker.anchor_right = 0
	_playhead_marker.offset_left = -1
	_playhead_marker.offset_right = 1
	_playhead_marker.anchor_top = 0
	_playhead_marker.anchor_bottom = 1
	wfm.add_child(_playhead_marker)

	# Time label, below the waveform
	_time_label = Label.new()
	_time_label.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_time_label.offset_top = -22
	_time_label.offset_bottom = -4
	_time_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_time_label.add_theme_color_override("font_color", C_TEXT_DIM)
	_time_label.add_theme_font_size_override("font_size", 12)
	_time_label.text = _format_ts(0)
	_waveform_panel.add_child(_time_label)

	# Events list — right side
	var elist := PanelContainer.new()
	elist.set_anchors_preset(Control.PRESET_RIGHT_WIDE)
	elist.offset_left = -380
	elist.offset_right = -40
	elist.offset_top = 160
	elist.offset_bottom = -100
	var ebg := StyleBoxFlat.new()
	ebg.bg_color = Color(0.024, 0.020, 0.026, 0.94)
	ebg.border_color = C_GOLD
	ebg.set_border_width_all(1)
	elist.add_theme_stylebox_override("panel", ebg)
	add_child(elist)
	var epad := MarginContainer.new()
	epad.add_theme_constant_override("margin_left", 12)
	epad.add_theme_constant_override("margin_right", 12)
	epad.add_theme_constant_override("margin_top", 10)
	epad.add_theme_constant_override("margin_bottom", 10)
	elist.add_child(epad)
	var evb := VBoxContainer.new()
	evb.add_theme_constant_override("separation", 6)
	epad.add_child(evb)
	var eh := Label.new()
	eh.text = "EVENTS (click to seek + reveal)"
	eh.add_theme_color_override("font_color", C_GOLD_HI)
	eh.add_theme_font_size_override("font_size", 12)
	evb.add_child(eh)
	var escroll := ScrollContainer.new()
	escroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	evb.add_child(escroll)
	_events_vbox = VBoxContainer.new()
	_events_vbox.add_theme_constant_override("separation", 2)
	_events_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	escroll.add_child(_events_vbox)
	for ev_v in _events:
		var ev: Dictionary = ev_v
		var captured := ev
		var rb := Button.new()
		rb.flat = false
		rb.alignment = HORIZONTAL_ALIGNMENT_LEFT
		rb.text = "  %s  %s" % [_format_ts(int(ev["ts"])), str(ev["label"])]
		rb.add_theme_color_override("font_color", C_TEXT)
		rb.add_theme_font_size_override("font_size", 12)
		rb.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
		var rsb := StyleBoxFlat.new()
		rsb.bg_color = Color(0, 0, 0, 0.25)
		rsb.border_color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.3)
		rsb.border_width_bottom = 1
		rb.add_theme_stylebox_override("normal", rsb)
		var rsh := rsb.duplicate() as StyleBoxFlat
		rsh.bg_color = Color(1, 0.85, 0.40, 0.12)
		rb.add_theme_stylebox_override("hover", rsh)
		rb.pressed.connect(func() -> void: _seek_and_reveal(captured))
		_events_vbox.add_child(rb)

	# Playback controls — bottom left
	var ctrls := HBoxContainer.new()
	ctrls.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	ctrls.offset_left = 60
	ctrls.offset_right = 400
	ctrls.offset_top = -56
	ctrls.offset_bottom = -20
	ctrls.add_theme_constant_override("separation", 8)
	add_child(ctrls)
	var play_btn := Button.new()
	play_btn.text = "[ ▸ play / pause ]"
	play_btn.flat = true
	play_btn.add_theme_color_override("font_color", C_GOLD)
	play_btn.pressed.connect(func() -> void: _playing = not _playing)
	ctrls.add_child(play_btn)
	var restart_btn := Button.new()
	restart_btn.text = "[ ⟲ restart ]"
	restart_btn.flat = true
	restart_btn.add_theme_color_override("font_color", C_TEXT)
	restart_btn.pressed.connect(func() -> void:
		_elapsed = 0.0
		_playing = true)
	ctrls.add_child(restart_btn)
	var speed_lbl := Label.new()
	speed_lbl.text = "speed: 60× real"
	speed_lbl.add_theme_color_override("font_color", C_TEXT_DIM)
	speed_lbl.add_theme_font_size_override("font_size", 12)
	speed_lbl.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	ctrls.add_child(speed_lbl)

	# Daemon-fetch banner
	var fetch := Label.new()
	fetch.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	fetch.offset_top = -22
	fetch.offset_bottom = -6
	fetch.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	fetch.text = _tape_fetch_banner
	fetch.add_theme_color_override("font_color", C_TEXT_DIM)
	fetch.add_theme_font_size_override("font_size", 12)
	fetch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(fetch)


# ── Playback ──────────────────────────────────────────────────────

func _seek_and_reveal(ev: Dictionary) -> void:
	_elapsed = float(ev["ts"])
	reveal(str(ev["label"]), str(ev["body"]), str(ev.get("unlock", "")))


func _on_diorama_tick(delta: float) -> void:
	if _playing:
		_elapsed += delta * 60.0  # 60x real-time
		if _elapsed > float(_tape_duration_sec):
			_elapsed = float(_tape_duration_sec)
			_playing = false
	if _playhead_marker != null and is_instance_valid(_playhead_marker):
		var frac: float = clamp(_elapsed / float(_tape_duration_sec), 0.0, 1.0)
		_playhead_marker.anchor_left = frac
		_playhead_marker.anchor_right = frac
	if _time_label != null and is_instance_valid(_time_label):
		_time_label.text = _format_ts(int(_elapsed)) + " / " + _format_ts(_tape_duration_sec)


func _format_ts(sec: int) -> String:
	return "%02d:%02d" % [sec / 60, sec % 60]


# ── Ambient: per-tape tick rate + tape hiss ──────────────────────

func _ambient_sample(_phase: float, step: float) -> Vector2:
	if _tape_tick_hz > 0.0:
		_tick_phase += step * _tape_tick_hz
		var tick := 0.0
		if fmod(_tick_phase, 1.0) < 0.04:
			tick = -0.04 * (1.0 - fmod(_tick_phase, 1.0) / 0.04)
		_hiss_phase += step
		var hiss := (randf() - 0.5) * 0.018
		var s = tick + hiss
		return Vector2(s, s)
	else:
		_hiss_phase += step
		var hiss := (randf() - 0.5) * 0.014
		return Vector2(hiss, hiss)


func _input(event: InputEvent) -> void:
	super(event)
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_SPACE:
			_playing = not _playing
			get_viewport().set_input_as_handled()
