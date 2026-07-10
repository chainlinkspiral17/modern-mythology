extends Control
## RIFFMASTER MELODY CLUB · one club meeting.
##
## Upper two-thirds: the clubhouse · four members on a couch,
## whoever is talking sits forward.  Lower third: the Riffmaster
## itself, drawn — eight rubber keys that light as played, two
## chunky OSC sliders, the frog SUB button, the smiling power
## light.  Keys 1–8 play live through the real 3-osc voice
## (PDPRiffmaster.gd); SHIFT is the upper octave.
##
## Call-and-response, graded generously on pitch sequence only ·
## three tries, then BEEBO declares it jazz and the club moves on.
## The only fail state is quitting, and the club says goodbye
## kindly even then.
##
## Meeting 12 is OPEN MIC: the take starts at your first note and
## ends when you stop for a while.  It records to the save and
## becomes the title music of THIS CARTRIDGE forever after.

signal quit
signal meeting_over(state: Dictionary)

const MEETINGS_PATH := "res://resources/games/vol7/riffmaster_melody_club/meetings.json"
const SPRITE_DIR := "res://resources/games/vol7/riffmaster_melody_club/sprites/"
const VOICE_SCRIPT := "res://scripts/PDPRiffmaster.gd"

# Toy palette
const C_WHITE  := Color("f4f4f0")
const C_RED    := Color("e83030")
const C_YELLOW := Color("f8c820")
const C_BLUE   := Color("2870d8")
const C_GREEN  := Color("30a848")
const C_KEY    := Color("282828")

const MEMBER_SEATS := {          # x centers on the couch
	"dot_dot": 340.0, "beebo": 550.0, "marcie": 760.0, "todd": 950.0
}
const OPEN_MIC_MAX_SEC := 16.0
const OPEN_MIC_SILENCE_END := 2.5

var _state: Dictionary = {}
var _meeting: Dictionary = {}
var _voice: Node = null
var _player: RiffmasterLoopPlayer = null
var _active_keys: Dictionary = {}      # semitones → true (for key highlights)

# Meeting flow
var _phase: String = "intro"           # intro · call · echo · open_mic · outro
var _intro_i: int = 0
var _call_i: int = 0
var _tries: int = 0
var _echo_expected: Array = []          # semitone sequence, rests removed
var _echo_heard: Array = []

# Open mic recorder
var _rec_events: Array = []
var _rec_started_ms: int = -1
var _rec_last_note_ms: int = -1
var _rec_open_notes: Dictionary = {}    # semitones → start_ms
var _rec_check_timer: Timer = null

var _speaker_lbl: Label = null
var _line_lbl: Label = null
var _go_btn: Button = null
var _title_lbl: Label = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST

	_voice = load(VOICE_SCRIPT).new()
	_voice.set("input_enabled", false)
	add_child(_voice)
	_voice.connect("note_on", _on_note_on)
	_voice.connect("note_off", _on_note_off)

	_player = RiffmasterLoopPlayer.new()
	add_child(_player)
	# Calls play through OUR voice · the drawn keys light up.
	_player.use_external_voice(_voice)

	_title_lbl = Label.new()
	_title_lbl.position = Vector2(60, 24)
	_title_lbl.add_theme_font_size_override("font_size", 20)
	_title_lbl.add_theme_color_override("font_color", C_BLUE)
	add_child(_title_lbl)

	_speaker_lbl = Label.new()
	_speaker_lbl.position = Vector2(60, 330)
	_speaker_lbl.size = Vector2(1160, 24)
	_speaker_lbl.add_theme_font_size_override("font_size", 13)
	_speaker_lbl.add_theme_color_override("font_color", C_RED)
	add_child(_speaker_lbl)

	_line_lbl = Label.new()
	_line_lbl.position = Vector2(60, 356)
	_line_lbl.size = Vector2(1160, 80)
	_line_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_line_lbl.add_theme_font_size_override("font_size", 16)
	_line_lbl.add_theme_color_override("font_color", C_KEY)
	add_child(_line_lbl)

	_go_btn = Button.new()
	_go_btn.position = Vector2(1020, 400)
	_go_btn.size = Vector2(200, 34)
	_go_btn.add_theme_font_size_override("font_size", 14)
	_go_btn.pressed.connect(_on_go)
	add_child(_go_btn)


func boot(state: Dictionary) -> void:
	_state = state
	var meetings: Array = _load_json(MEETINGS_PATH).get("meetings", [])
	var n: int = clampi(int(_state.get("meeting_n", 1)), 1, meetings.size())
	_meeting = meetings[n - 1]
	_title_lbl.text = String(_meeting.get("title", ""))
	_phase = "intro"
	_intro_i = 0
	_call_i = 0
	_show_intro_line()
	queue_redraw()


func _load_json(path: String) -> Dictionary:
	if not FileAccess.file_exists(path): return {}
	var f := FileAccess.open(path, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	return parsed if parsed is Dictionary else {}


# ─── Meeting flow ────────────────────────────────────────────────

func _show_intro_line() -> void:
	var intro: Array = _meeting.get("intro", [])
	if _intro_i >= intro.size():
		if bool(_meeting.get("open_mic", false)):
			_begin_open_mic()
		else:
			_begin_call()
		return
	_set_line(String(intro[_intro_i]))
	_go_btn.text = "  · okay ·  "
	_go_btn.visible = true
	_phase = "intro"


func _on_go() -> void:
	match _phase:
		"intro":
			_intro_i += 1
			_show_intro_line()
		"call_ready":
			_play_call()
		"echo":
			_finish_echo()
		"praise":
			_begin_call()
		"open_mic_wait":
			pass
		"outro":
			meeting_over.emit(_state)


func _begin_call() -> void:
	var calls: Array = _meeting.get("calls", [])
	if _call_i >= calls.size():
		_begin_outro()
		return
	_tries = 0
	var call: Dictionary = calls[_call_i]
	_set_line("%s · '%s' · listen —" % [_host_name(), String(call.get("name", ""))])
	_phase = "call_ready"
	_go_btn.text = "  · play it ·  "
	_go_btn.visible = true


func _play_call() -> void:
	_phase = "listening"
	_go_btn.visible = false
	_voice.set("input_enabled", false)
	var call: Dictionary = (_meeting.get("calls", []))[_call_i]
	var loop := _call_to_loop(call)
	_player.play_loop(loop)
	_echo_expected = []
	for ev in loop.get("events", []):
		_echo_expected.append(int((ev as Dictionary)["s"]))
	var wait := _player.loop_length(loop) + 0.6
	get_tree().create_timer(wait).timeout.connect(_begin_echo)


func _call_to_loop(call: Dictionary) -> Dictionary:
	# Rests (s < 0) shape the call's timing but are not notes.
	var bpm: float = float(call.get("bpm", 84))
	var beat := 60.0 / bpm
	var t := 0.0
	var events: Array = []
	for n_v in call.get("notes", []):
		var n: Dictionary = n_v
		var beats: float = float(n.get("beats", 1.0))
		var s: int = int(n.get("s", 0))
		if s >= 0:
			events.append({"s": s, "t": t, "d": beat * beats * 0.82})
		t += beat * beats
	return {"events": events}


func _begin_echo() -> void:
	_phase = "echo"
	_echo_heard = []
	_voice.set("input_enabled", true)
	_set_line("your turn.  (keys 1–8 · SHIFT for the high octave · press DONE when you're done)")
	_go_btn.text = "  · done ·  "
	_go_btn.visible = true


func _finish_echo() -> void:
	_voice.set("input_enabled", false)
	if _echo_heard == _echo_expected:
		_call_i += 1
		var praise := ["DOT-DOT · 'bwam! that was IT!'",
			"BEEBO · 'yes!! exactly and also wonderfully!!'",
			"MARCIE · 'correct.' · from marcie that is a parade.",
			"TODD · (thumbs up)"]
		_set_line(String(praise[_call_i % praise.size()]))
		_phase = "praise"
		_go_btn.text = "  · next ·  "
		_go_btn.visible = true
	elif _tries < 2:
		_tries += 1
		var nudges := ["MARCIE · 'close. the shape was right. the notes can join it. again —'",
			"DOT-DOT · 'you got the spirit! now get the keys! one more time —'"]
		_set_line(String(nudges[_tries % nudges.size()]))
		_phase = "call_ready"
		_go_btn.text = "  · hear it again ·  "
		_go_btn.visible = true
	else:
		_call_i += 1
		_set_line("BEEBO · 'that was JAZZ!! jazz is when it is different on purpose!!' · the club applauds. the club means it.")
		_phase = "praise"
		_go_btn.text = "  · next ·  "
		_go_btn.visible = true


func _begin_outro() -> void:
	_phase = "outro"
	_voice.set("input_enabled", true)   # the machine stays on · always
	_set_line(String(_meeting.get("outro", "the meeting is over. the couch stays warm.")))
	_go_btn.text = "  · end the meeting ·  "
	_go_btn.visible = true


func _host_name() -> String:
	return String(_meeting.get("host", "dot_dot")).to_upper().replace("_", "-")


# The praise phase reuses the okay button · route it.
func _gui_input(_event: InputEvent) -> void:
	pass


func _set_line(text: String) -> void:
	var idx := text.find(" · ")
	if text.begins_with("DOT-DOT") or text.begins_with("BEEBO") \
			or text.begins_with("MARCIE") or text.begins_with("TODD"):
		_speaker_lbl.text = text.substr(0, idx) if idx > 0 else ""
		_line_lbl.text = text.substr(idx + 3) if idx > 0 else text
	else:
		_speaker_lbl.text = ""
		_line_lbl.text = text
	queue_redraw()


# ─── OPEN MIC ────────────────────────────────────────────────────

func _begin_open_mic() -> void:
	_phase = "open_mic_wait"
	_voice.set("input_enabled", true)
	_rec_events = []
	_rec_started_ms = -1
	_rec_last_note_ms = -1
	_rec_open_notes = {}
	_set_line("the club is quiet. the tape is ready. your first note starts it.")
	_go_btn.visible = false
	_rec_check_timer = Timer.new()
	_rec_check_timer.wait_time = 0.25
	_rec_check_timer.timeout.connect(_check_open_mic_end)
	add_child(_rec_check_timer)
	_rec_check_timer.start()


func _check_open_mic_end() -> void:
	if _rec_started_ms < 0:
		return
	var now := Time.get_ticks_msec()
	var elapsed := float(now - _rec_started_ms) / 1000.0
	var silence := float(now - _rec_last_note_ms) / 1000.0
	if elapsed >= OPEN_MIC_MAX_SEC or (silence >= OPEN_MIC_SILENCE_END and _rec_open_notes.is_empty() and _rec_events.size() > 0):
		_end_open_mic()


func _end_open_mic() -> void:
	if _rec_check_timer != null:
		_rec_check_timer.stop()
		_rec_check_timer.queue_free()
		_rec_check_timer = null
	_voice.set("input_enabled", false)
	# Close any hanging notes.
	var now := Time.get_ticks_msec()
	for s in _rec_open_notes.keys():
		_rec_events.append({"s": int(s),
			"t": float(_rec_open_notes[s] - _rec_started_ms) / 1000.0,
			"d": float(now - _rec_open_notes[s]) / 1000.0})
	_rec_open_notes.clear()
	_rec_events.sort_custom(func(a, b) -> bool: return float(a["t"]) < float(b["t"]))
	_state["open_mic_loop"] = {"recorded_by": "you", "events": _rec_events}
	_set_line("the tape clicks off. the club looks at each other. DOT-DOT starts the applause and BEEBO makes it a weather event.")
	_phase = "playback_wait"
	_go_btn.text = "  · hear it back ·  "
	_go_btn.visible = true
	_go_btn.pressed.disconnect(_on_go)
	_go_btn.pressed.connect(_playback_open_mic, CONNECT_ONE_SHOT)


func _playback_open_mic() -> void:
	_go_btn.visible = false
	var loop: Dictionary = _state.get("open_mic_loop", {})
	_player.play_loop(loop)
	var wait := _player.loop_length(loop) + 1.0
	get_tree().create_timer(wait).timeout.connect(func() -> void:
		_go_btn.pressed.connect(_on_go)
		_begin_outro())


# ─── The voice, watched ──────────────────────────────────────────

func _on_note_on(semitones: int) -> void:
	_active_keys[semitones] = true
	if _phase == "echo":
		_echo_heard.append(semitones)
	elif _phase == "open_mic_wait":
		var now := Time.get_ticks_msec()
		if _rec_started_ms < 0:
			_rec_started_ms = now
			_set_line("· recording ·")
		_rec_last_note_ms = now
		_rec_open_notes[semitones] = now
	queue_redraw()


func _on_note_off(semitones: int) -> void:
	_active_keys.erase(semitones)
	if _phase == "open_mic_wait" and _rec_started_ms >= 0 and _rec_open_notes.has(semitones):
		var start: int = _rec_open_notes[semitones]
		_rec_open_notes.erase(semitones)
		_rec_events.append({"s": semitones,
			"t": float(start - _rec_started_ms) / 1000.0,
			"d": maxf(0.08, float(Time.get_ticks_msec() - start) / 1000.0)})
		_rec_last_note_ms = Time.get_ticks_msec()
	queue_redraw()


# ─── The picture ─────────────────────────────────────────────────

func _draw() -> void:
	# The one stick in the catalog with a white background.
	draw_rect(Rect2(0, 0, 1280, 720), C_WHITE)

	# Clubhouse · the couch
	draw_rect(Rect2(200, 250, 880, 60), C_RED)            # seat
	draw_rect(Rect2(220, 190, 840, 70), C_RED)            # backrest
	draw_rect(Rect2(180, 220, 40, 90), C_RED)             # arms
	draw_rect(Rect2(1060, 220, 40, 90), C_RED)
	draw_rect(Rect2(160, 306, 960, 10), C_KEY)            # shadow line

	# A window and the banner make it a clubhouse
	draw_rect(Rect2(80, 60, 140, 100), C_BLUE)
	draw_rect(Rect2(88, 68, 124, 84), C_WHITE)
	draw_rect(Rect2(146, 68, 4, 84), C_BLUE)
	draw_rect(Rect2(88, 106, 124, 4), C_BLUE)

	# Members on the couch · the speaker sits forward (drawn lower + bigger)
	var speaker := _speaker_lbl.text.to_lower().replace("-", "_")
	var spr := SlowstockSprite.new()
	for member in MEMBER_SEATS.keys():
		if not spr.load(SPRITE_DIR + String(member) + ".json"):
			continue
		var tex: Texture2D = spr.texture()
		if tex == null:
			continue
		var is_speaking := String(member) == speaker
		var scale := 9.0 if is_speaking else 8.0
		var w := 12.0 * scale
		var h := 14.0 * scale
		var x: float = MEMBER_SEATS[member] - w * 0.5
		var y := (268.0 if is_speaking else 258.0) - h
		draw_texture_rect(tex, Rect2(Vector2(x, y), Vector2(w, h)), false)

	_draw_riffmaster()


func _draw_riffmaster() -> void:
	# The machine fills the lower third.
	draw_rect(Rect2(0, 470, 1280, 250), C_WHITE)
	draw_rect(Rect2(60, 480, 1160, 220), Color("e4e4de"))     # molded body
	draw_rect(Rect2(60, 480, 1160, 8), C_KEY)                 # seam

	# Eight rubber keys · lit when played (either octave)
	for i in range(8):
		var kx := 120.0 + i * 96.0
		var semis := [0, 2, 4, 5, 7, 9, 11, 12][i]
		var lit: bool = _active_keys.has(semis) or _active_keys.has(semis + 12)
		var key_col := [C_RED, C_YELLOW, C_BLUE, C_GREEN][i % 4] if lit else C_KEY
		draw_rect(Rect2(kx, 540, 80, 120), key_col)
		draw_rect(Rect2(kx + 6, 546, 68, 20), Color(1, 1, 1, 0.25) if lit else Color(1, 1, 1, 0.08))
		var font := get_theme_default_font()
		draw_string(font, Vector2(kx + 32, 700), str(i + 1), HORIZONTAL_ALIGNMENT_LEFT, -1, 14, C_KEY)

	# Two chunky OSC sliders
	draw_rect(Rect2(920, 500, 10, 30), C_KEY)
	draw_rect(Rect2(908, 508, 34, 12), C_RED)
	draw_rect(Rect2(970, 500, 10, 30), C_KEY)
	draw_rect(Rect2(958, 514, 34, 12), C_BLUE)
	# The SUB button · shaped like a frog · always a frog
	draw_rect(Rect2(1030, 496, 44, 34), C_GREEN)
	draw_rect(Rect2(1034, 490, 10, 10), C_GREEN)
	draw_rect(Rect2(1060, 490, 10, 10), C_GREEN)
	# The famous smiling power light
	var lit_now := not _active_keys.is_empty()
	draw_circle(Vector2(1150, 512), 16.0, C_YELLOW if lit_now else Color("d8c890"))
	draw_circle(Vector2(1144, 508), 2.0, C_KEY)
	draw_circle(Vector2(1156, 508), 2.0, C_KEY)
	draw_arc(Vector2(1150, 514), 7.0, 0.3, PI - 0.3, 10, C_KEY, 2.0)


func _input(event: InputEvent) -> void:
	if not is_visible_in_tree():
		return
	if event is InputEventKey and event.pressed and not event.echo:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			quit.emit()
			get_viewport().set_input_as_handled()
