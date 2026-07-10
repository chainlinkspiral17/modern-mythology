extends Control
## SWEETGUM · the watch · one night, 9 PM to 6 AM, real-time-ish
## (~forty minutes).  You are the night watchman.  The date is on
## the log header.  The game never mentions it again.
##
## Three colors.  No sprites.  No hero images.  The camp is an
## ASCII-adjacent line diagram · eight stations, paths, the
## waterline · traced from somewhere real.  Players of Pirate
## Summer will recognize the geography and feel the floor tilt.
##
## ROUNDS: walk the diagram, CHECK each padlock.  Rounds are due
## hourly; the game does not enforce this; the log simply shows
## the gaps.
##
## THE LOG: typed, free text, timestamped.  It persists across
## every run of the cartridge (user://sweetgum_log.json, seeded
## from nineteen years of authored entries).
##
## Around 3 AM: three sounds on the water, and a light on the
## island the log template HAS NO FIELD FOR.  `NOT A STATION.`
##
## 06:00 · ALL · QUIET.  Whether that is the game being kind or
## the game lying is the whole aftertaste.
##
## Second playthrough: cabin 3 is unlocked.  A made bed.  The log
## gains a field it didn't have: NAMES.  It is never filled.
## There is no third variation.  The author said what she had.

signal quit
signal watch_over(state: Dictionary)

const PALIMPSEST_RES := "res://resources/games/vol7/sweetgum/palimpsest.json"
const LOG_PATH := "user://sweetgum_log.json"

const C_DARK := Color("041104")
const C_INK  := Color("46d84a")
const C_THIN := Color("1c5a20")

# 9 PM (1260) → 6 AM (1800, wrapping) · 540 game-minutes in ~40
# real minutes · 4.444 s per game-minute.
const SECONDS_PER_GAME_MIN := 4.444
const START_MIN := 21 * 60
const END_MIN   := 30 * 60          # 6 AM next day, unwrapped

# The diagram · traced from somewhere real (Pirate Summer's camp)
const STATIONS := {
	"gate":      {"pos": Vector2(160, 520), "label": "GATE"},
	"mess":      {"pos": Vector2(420, 380), "label": "MESS"},
	"boathouse": {"pos": Vector2(760, 560), "label": "BOATHOUSE"},
	"cabin_1":   {"pos": Vector2(300, 220), "label": "CABIN 1"},
	"cabin_2":   {"pos": Vector2(460, 180), "label": "CABIN 2"},
	"cabin_3":   {"pos": Vector2(620, 200), "label": "CABIN 3"},
	"cabin_4":   {"pos": Vector2(760, 260), "label": "CABIN 4"},
	"waterline": {"pos": Vector2(560, 600), "label": "WATERLINE"},
}
const PATHS := [
	["gate", "mess"], ["mess", "cabin_1"], ["cabin_1", "cabin_2"],
	["cabin_2", "cabin_3"], ["cabin_3", "cabin_4"],
	["mess", "waterline"], ["waterline", "boathouse"],
	["cabin_4", "boathouse"], ["gate", "waterline"],
]
const ISLAND_POS := Vector2(1000, 650)

var _state: Dictionary = {}
var _game_min: float = float(START_MIN)
var _at: String = "gate"
var _walking_to: String = ""
var _walk_t: float = 0.0
var _checked: Dictionary = {}        # "hour:station" → true
var _light_on: bool = false
var _water_sounds_played: int = 0
var _crickets: bool = true
var _over: bool = false
var _second_night: bool = false
var _run_entries: Array = []         # this night's typed entries

var _clock_lbl: Label = null
var _cond_edit: LineEdit = null
var _names_edit: LineEdit = null
var _file_btn: Button = null
var _check_btn: Button = null
var _log_view: RichTextLabel = null
var _msg_lbl: Label = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	_build_ui()
	set_process(true)


func boot(state: Dictionary) -> void:
	_state = state
	_second_night = int(_state.get("nights_stood", 0)) >= 1
	_game_min = float(START_MIN)
	_ensure_log_file()
	_names_edit.visible = _second_night
	_play_bed("res://assets/audio/bgm/sg/room_crickets.wav")
	_refresh_log_view()
	_msg("21:00. the watch is yours. rounds are hourly. nobody said by whom.")
	queue_redraw()


# ─── The palimpsest ──────────────────────────────────────────────

func _ensure_log_file() -> void:
	if FileAccess.file_exists(LOG_PATH):
		return
	# First boot of this copy · seed nineteen years of entries.
	var f := FileAccess.open(PALIMPSEST_RES, FileAccess.READ)
	if f == null: return
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if not (parsed is Dictionary): return
	var out := {"nights": []}
	for block in (parsed as Dictionary).get("seeded", []):
		out["nights"].append(block)
	var w := FileAccess.open(LOG_PATH, FileAccess.WRITE)
	if w != null:
		w.store_string(JSON.stringify(out, "  "))
		w.close()


func _read_log() -> Dictionary:
	if not FileAccess.file_exists(LOG_PATH):
		return {"nights": []}
	var f := FileAccess.open(LOG_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	return parsed if parsed is Dictionary else {"nights": []}


func _append_entry(entry: Dictionary) -> void:
	_run_entries.append(entry)
	var log := _read_log()
	var nights: Array = log.get("nights", [])
	# This run's block · undated · "the log continues."
	if nights.is_empty() or String((nights[-1] as Dictionary).get("who", "")) != "this watch":
		nights.append({"year": "", "who": "this watch", "entries": []})
	(nights[-1] as Dictionary)["entries"].append(entry)
	log["nights"] = nights
	var w := FileAccess.open(LOG_PATH, FileAccess.WRITE)
	if w != null:
		w.store_string(JSON.stringify(log, "  "))
		w.close()
	_refresh_log_view()


# ─── UI ──────────────────────────────────────────────────────────

func _build_ui() -> void:
	var bg := ColorRect.new()
	bg.color = C_DARK
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	_clock_lbl = Label.new()
	_clock_lbl.position = Vector2(60, 24)
	_clock_lbl.add_theme_font_size_override("font_size", 18)
	_clock_lbl.add_theme_color_override("font_color", C_INK)
	add_child(_clock_lbl)

	# The log header · the date, said once, never again
	var hdr := Label.new()
	hdr.text = "WATCH LOG · CAMP SWEETGUM · AUG 14 1976"
	hdr.position = Vector2(860, 24)
	hdr.add_theme_font_size_override("font_size", 13)
	hdr.add_theme_color_override("font_color", C_THIN)
	add_child(hdr)

	_msg_lbl = Label.new()
	_msg_lbl.position = Vector2(60, 660)
	_msg_lbl.size = Vector2(700, 48)
	_msg_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_msg_lbl.add_theme_font_size_override("font_size", 14)
	_msg_lbl.add_theme_color_override("font_color", C_INK)
	add_child(_msg_lbl)

	_check_btn = Button.new()
	_check_btn.flat = true
	_check_btn.text = "[ CHECK PADLOCK ]"
	_check_btn.position = Vector2(60, 570)
	_check_btn.add_theme_font_size_override("font_size", 14)
	_check_btn.add_theme_color_override("font_color", C_INK)
	_check_btn.pressed.connect(_check_station)
	add_child(_check_btn)

	# The log panel · one character-width too narrow · do not fix
	var panel := ColorRect.new()
	panel.color = Color(C_DARK.r + 0.01, C_DARK.g + 0.03, C_DARK.b + 0.01)
	panel.position = Vector2(860, 52)
	panel.size = Vector2(360, 520)
	add_child(panel)

	_log_view = RichTextLabel.new()
	_log_view.bbcode_enabled = false
	_log_view.scroll_following = true
	_log_view.position = Vector2(868, 58)
	_log_view.size = Vector2(338, 430)
	_log_view.add_theme_font_size_override("normal_font_size", 12)
	_log_view.add_theme_color_override("default_color", C_THIN)
	add_child(_log_view)

	var form_lbl := Label.new()
	form_lbl.text = "TIME · auto   STATION · auto   CONDITION:"
	form_lbl.position = Vector2(868, 494)
	form_lbl.add_theme_font_size_override("font_size", 12)
	form_lbl.add_theme_color_override("font_color", C_THIN)
	add_child(form_lbl)

	_cond_edit = LineEdit.new()
	_cond_edit.position = Vector2(868, 514)
	_cond_edit.size = Vector2(260, 28)
	_cond_edit.max_length = 80
	_cond_edit.add_theme_font_size_override("font_size", 13)
	_cond_edit.add_theme_color_override("font_color", C_INK)
	_cond_edit.text_submitted.connect(func(_t: String) -> void: _file_entry())
	add_child(_cond_edit)

	_file_btn = Button.new()
	_file_btn.flat = true
	_file_btn.text = "[FILE]"
	_file_btn.position = Vector2(1136, 514)
	_file_btn.add_theme_font_size_override("font_size", 13)
	_file_btn.add_theme_color_override("font_color", C_INK)
	_file_btn.pressed.connect(_file_entry)
	add_child(_file_btn)

	# NAMES · second playthrough only · never filled
	_names_edit = LineEdit.new()
	_names_edit.position = Vector2(868, 548)
	_names_edit.size = Vector2(338, 26)
	_names_edit.placeholder_text = "NAMES:"
	_names_edit.editable = false
	_names_edit.visible = false
	_names_edit.add_theme_font_size_override("font_size", 12)
	_names_edit.add_theme_color_override("font_color", C_THIN)
	add_child(_names_edit)


func _refresh_log_view() -> void:
	var log := _read_log()
	var txt := ""
	var glass := OneironauticsTokens.has("glass_second_ledger_seen")
	var nights: Array = log.get("nights", [])
	# The A.G. 1979 entry is injected at read time, in year order.
	var render: Array = []
	for n in nights:
		render.append(n)
		if glass and String((n as Dictionary).get("year", "")) == "1977":
			var f := FileAccess.open(PALIMPSEST_RES, FileAccess.READ)
			if f != null:
				var p: Variant = JSON.parse_string(f.get_as_text())
				f.close()
				if p is Dictionary and (p as Dictionary).has("glass_entry"):
					render.append((p as Dictionary)["glass_entry"])
	for n_v in render:
		var n: Dictionary = n_v
		var year := String(n.get("year", ""))
		var who := String(n.get("who", ""))
		txt += "\n— %s —\n" % (year + " · " + who if year != "" else "the log continues.")
		for e_v in n.get("entries", []):
			var e: Dictionary = e_v
			txt += "%s · %s · %s\n" % [String(e.get("t", "")),
				String(e.get("station", "")).to_upper(), String(e.get("text", ""))]
	_log_view.text = txt


# ─── Time ────────────────────────────────────────────────────────

func _process(delta: float) -> void:
	if _over:
		return
	_game_min += delta / SECONDS_PER_GAME_MIN
	if _walking_to != "":
		_walk_t += delta
		queue_redraw()
		if _walk_t >= 2.5:
			_at = _walking_to
			_walking_to = ""
			_sfx("boot_plank", 0.22)
	var h := int(_game_min / 60.0) % 24
	var m := int(_game_min) % 60
	_clock_lbl.text = "%02d:%02d" % [h, m]

	# 2 AM · the crickets stop being audible · nobody notices when
	if _crickets and _game_min >= 26 * 60:
		_crickets = false
		_play_bed("res://assets/audio/bgm/sg/room_tone.wav")

	# ~2:55–3:10 · three sounds on the water · quieter than the clock
	if _game_min >= 26 * 60 + 55 and _water_sounds_played < 3:
		var due := 26 * 60 + 55 + _water_sounds_played * 5
		if _game_min >= due:
			_water_sounds_played += 1
			_sfx("water_slap", 0.18)

	# the light
	if not _light_on and _game_min >= 27 * 60 and _game_min < 28 * 60 + 30:
		_light_on = true
		queue_redraw()
	elif _light_on and _game_min >= 28 * 60 + 30:
		_light_on = false
		queue_redraw()

	# 6 AM
	if _game_min >= END_MIN:
		_six_am()


func _six_am() -> void:
	_over = true
	_play_bed("res://assets/audio/bgm/sg/four_notes.wav")
	_append_entry({"t": "06:00", "station": "all", "text": "QUIET"})
	_msg("the sky line brightens. the log closes itself with an entry you didn't type.")
	_cond_edit.editable = false
	_check_btn.visible = false
	queue_redraw()
	var tw := create_tween()
	tw.tween_interval(8.0)
	tw.tween_callback(func() -> void: watch_over.emit(_state))


# ─── Actions ─────────────────────────────────────────────────────

func _check_station() -> void:
	if _over or _walking_to != "":
		return
	var hour := int(_game_min / 60.0)
	_checked["%d:%s" % [hour, _at]] = true
	if _second_night and _at == "cabin_3":
		_msg("the padlock hangs open. inside: nothing but a made bed.")
		_sfx("door_open", 0.3)
		return
	_msg("%s · padlock holds." % STATIONS[_at]["label"])
	_sfx("stick_scratch", 0.25)


func _file_entry() -> void:
	if _over:
		return
	var text := _cond_edit.text.strip_edges()
	if text == "":
		return
	# The light has no field.  Everyone tries.
	if _light_on:
		var lower := text.to_lower()
		for w in ["light", "island", "glow", "out there", "water", "lamp"]:
			if lower.contains(w):
				_msg("NOT A STATION.")
				_sfx("hurt", 0.3)
				OneironauticsTokens.add("sweetgum_island_light_logged_attempt")
				_state["island_attempted"] = true
				_cond_edit.text = ""
				return
	var h := int(_game_min / 60.0) % 24
	var m := int(_game_min) % 60
	_append_entry({"t": "%02d:%02d" % [h, m], "station": _at, "text": text})
	_cond_edit.text = ""
	_msg("filed.")


func _msg(t: String) -> void:
	_msg_lbl.text = t


# ─── The diagram ─────────────────────────────────────────────────

func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed \
			and event.button_index == MOUSE_BUTTON_LEFT and not _over:
		var pos: Vector2 = (event as InputEventMouseButton).position
		for sid in STATIONS.keys():
			if pos.distance_to(STATIONS[sid]["pos"]) < 40.0 and sid != _at:
				if _adjacent(_at, String(sid)) and _walking_to == "":
					_walking_to = String(sid)
					_walk_t = 0.0
					_sfx("boot_plank", 0.18)
					accept_event()
				return


func _adjacent(a: String, b: String) -> bool:
	for p in PATHS:
		if (p[0] == a and p[1] == b) or (p[0] == b and p[1] == a):
			return true
	return false


func _draw() -> void:
	var font := get_theme_default_font()
	# paths · thinned ink
	for p in PATHS:
		draw_line(STATIONS[p[0]]["pos"], STATIONS[p[1]]["pos"], C_THIN, 1.5)
	# the waterline · a long uneven line past the camp
	var wl: Array = []
	for i in range(0, 900, 60):
		wl.append(Vector2(80 + i, 622 + (i % 120) / 30.0))
	for i in range(wl.size() - 1):
		draw_line(wl[i], wl[i + 1], C_THIN, 1.5)
	# stations
	for sid in STATIONS.keys():
		var s: Dictionary = STATIONS[sid]
		var pos: Vector2 = s["pos"]
		var here := sid == _at
		draw_rect(Rect2(pos - Vector2(24, 14), Vector2(48, 28)), C_INK if here else C_THIN, false, 2.0)
		draw_string(font, pos + Vector2(-22, -20), String(s["label"]),
			HORIZONTAL_ALIGNMENT_LEFT, -1, 12, C_INK if here else C_THIN)
		# station 6's data-fault band · the author's unit wrote it
		# into the master · present in every copy · do not fix
		if sid == "cabin_4":
			for row in range(3):
				draw_rect(Rect2(pos.x - 30 + (row * 7) % 13, pos.y - 2 + row * 4, 60, 2), C_DARK)
				draw_rect(Rect2(pos.x - 26 + (row * 11) % 17, pos.y - 1 + row * 4, 18, 1), C_INK)
	# the watchman
	var wpos: Vector2 = STATIONS[_at]["pos"]
	if _walking_to != "":
		wpos = wpos.lerp(STATIONS[_walking_to]["pos"], clampf(_walk_t / 2.5, 0.0, 1.0))
	draw_circle(wpos + Vector2(0, 20), 4.0, C_INK)
	# the light · the log has no field for it
	if _light_on:
		draw_circle(ISLAND_POS, 3.0, C_INK)
		draw_circle(ISLAND_POS, 7.0, Color(C_INK.r, C_INK.g, C_INK.b, 0.25))
	# 6 AM · the sky line brightens
	if _over:
		draw_rect(Rect2(0, 0, 1280, 3), C_INK)
		draw_rect(Rect2(0, 3, 1280, 6), C_THIN)


func _play_bed(path: String) -> void:
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("play_bgm"):
		am.play_bgm(path)


func _sfx(preset: String, vol: float = 1.0) -> void:
	var sb := get_node_or_null("/root/SFXBank")
	if sb != null and sb.has_method("play"):
		sb.play(preset, vol)


func _input(event: InputEvent) -> void:
	if not is_visible_in_tree():
		return
	if event is InputEventKey and event.pressed and not event.echo:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE and not _cond_edit.has_focus():
			quit.emit()
			get_viewport().set_input_as_handled()
