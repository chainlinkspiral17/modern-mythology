extends Node
## Settings singleton — persists player preferences via ConfigFile.
## Autoloaded as "Settings".

signal settings_changed(key: String, value)

const SAVE_PATH := "user://settings.cfg"
const TEXT_SPEED_MS := {"slow": 60, "normal": 28, "fast": 10}
const LEGACY_SIZE   := {"small": 0.82, "normal": 1.0, "large": 1.30}

var _txt_scale:      float  = 1.0
var _text_speed:     String = "normal"
var _bgm_vol:        float  = 0.65
var _sfx_vol:        float  = 0.80
var _voice_vol:      float  = 0.80
var _skip_unread:    bool   = false
var _auto_advance_ms: int   = 0
var _window_mode:    String = "720p"
var _haptics:        float  = 1.0
var _music_skin:     String = "diner_booth"
var _music_viz:      String = "peak_meter"
var _music_jukebox:  bool   = true
var _trip_amount:    float  = 0.75   # THE TRIP · psychedelic layer strength (TripSync)
var _trip_flow:      float  = 1.0    # THE TRIP mix · the liquid drift (the one dial that moves pixels)
var _trip_lines:     float  = 1.0    # THE TRIP mix · aura on the lines
var _trip_colour:    float  = 1.0    # THE TRIP mix · hue drift + wash in the flats
var _trip_beat:      float  = 1.0    # THE TRIP mix · how much the beat shows
var _trip_trails:    float  = 1.0    # THE TRIP mix · the feedback buffer (Minter light trails)
var _auto_play:      bool   = false  # AUTO-PLAY: every chapter reads itself, choices picked
var _hud_bar:        String = "auto" # TOP BAR: "auto" (shows on an update / at the top edge) | "always"
var _wide_screens:   String = "fill" # WIDE SCREENS (2026-11-08): "fill" (wide-ready surfaces use the whole screen) | "pillarbox"
var _detail_3d:      String = "native" # 3D DETAIL: "native" (every pixel) | "balanced" (0.75) | "fast" (0.5)


var txt_scale: float:
	get: return _txt_scale
	set(val):
		_txt_scale = clampf(val, 0.5, 3.0)
		settings_changed.emit("txt_scale", _txt_scale)
		_save()

var text_speed: String:
	get: return _text_speed
	set(val):
		_text_speed = val
		settings_changed.emit("text_speed", val)
		_save()

var bgm_vol: float:
	get: return _bgm_vol
	set(val):
		_bgm_vol = val
		if is_node_ready() and has_node("/root/AudioMgr"):
			AudioMgr.set_bus_volume("BGM", val)
		settings_changed.emit("bgm_vol", val)
		_save()

var sfx_vol: float:
	get: return _sfx_vol
	set(val):
		_sfx_vol = val
		if is_node_ready() and has_node("/root/AudioMgr"):
			AudioMgr.set_bus_volume("SFX", val)
		settings_changed.emit("sfx_vol", val)
		_save()

var voice_vol: float:
	get: return _voice_vol
	set(val):
		_voice_vol = val
		if is_node_ready() and has_node("/root/AudioMgr"):
			AudioMgr.set_bus_volume("Voice", val)
		settings_changed.emit("voice_vol", val)
		_save()

var skip_unread: bool:
	get: return _skip_unread
	set(val):
		_skip_unread = val
		settings_changed.emit("skip_unread", val)
		_save()

var auto_advance_ms: int:
	get: return _auto_advance_ms
	set(val):
		_auto_advance_ms = val
		settings_changed.emit("auto_advance_ms", val)
		_save()

# AUTO-PLAY (2026-10-19, the user: "there needs to be an auto-read/play
# setting that just automatically plays a chapter and picks options as
# needed"). On: every scene starts in AUTO (the A key's hands-free mode),
# voiced lines finish before the page turns, choices are picked.
var auto_play: bool:
	get: return _auto_play
	set(val):
		_auto_play = val
		settings_changed.emit("auto_play", val)
		_save()

# TOP BAR (2026-10-19, the user: "the top bar shouldn't be there unless it
# shows an update or it's turned on"). "auto": hidden, it shows for a few
# seconds when a skill, an item or the chapter changes, and while the
# pointer is at the top edge; "always": on.
var hud_bar: String:
	get: return _hud_bar
	set(val):
		_hud_bar = val
		settings_changed.emit("hud_bar", val)
		_save()

var wide_screens: String:
	get: return _wide_screens
	set(val):
		_wide_screens = val if val in ["fill", "pillarbox"] else "fill"
		settings_changed.emit("wide_screens", _wide_screens)
		_save()

var detail_3d: String:
	get: return _detail_3d
	set(val):
		_detail_3d = val if val in ["native", "balanced", "fast"] else "native"
		settings_changed.emit("detail_3d", _detail_3d)
		_save()


## the 3D sets' render scale for the chosen detail (Viewport.scaling_3d_scale)
func get_3d_scale() -> float:
	match _detail_3d:
		"balanced": return 0.75
		"fast": return 0.5
	return 1.0


var window_mode: String:
	get: return _window_mode
	set(val):
		_window_mode = val
		_apply_window_mode(val)
		settings_changed.emit("window_mode", val)
		_save()

# Haptic rumble strength · 0.0 = off, 1.0 = full. Driven by
# SFXBank's rumble grammar; baseline device is the 2026 Steam
# Controller (SDL rumble rendered by its HD haptic motors).
var haptics: float:
	get: return _haptics
	set(val):
		_haptics = clampf(val, 0.0, 1.0)
		settings_changed.emit("haptics", _haptics)
		_save()

var music_skin: String:
	get: return _music_skin
	set(val):
		_music_skin = val
		settings_changed.emit("music_skin", val)
		_save()

var music_viz: String:
	get: return _music_viz
	set(val):
		_music_viz = val
		settings_changed.emit("music_viz", val)
		_save()

# Jukebox mode: the Music Player owns playback — the full catalog
# rotates continuously and per-scene BGM requests are ignored.
# OFF = classic behavior: scene / queue music.
var music_jukebox: bool:
	get: return _music_jukebox
	set(val):
		_music_jukebox = val
		settings_changed.emit("music_jukebox", val)
		_save()

# THE TRIP (2026-09-07): strength of the project-wide music-synced
# psychedelic layer. 0 turns it off; TripSync reads this live.
var trip_amount: float:
	get: return _trip_amount
	set(val):
		_trip_amount = clampf(val, 0.0, 1.0)
		settings_changed.emit("trip_amount", _trip_amount)
		_save()

var trip_flow: float:
	get: return _trip_flow
	set(val):
		_trip_flow = clampf(val, 0.0, 1.0)
		settings_changed.emit("trip_flow", _trip_flow)
		_save()

var trip_lines: float:
	get: return _trip_lines
	set(val):
		_trip_lines = clampf(val, 0.0, 1.0)
		settings_changed.emit("trip_lines", _trip_lines)
		_save()

var trip_colour: float:
	get: return _trip_colour
	set(val):
		_trip_colour = clampf(val, 0.0, 1.0)
		settings_changed.emit("trip_colour", _trip_colour)
		_save()

var trip_beat: float:
	get: return _trip_beat
	set(val):
		_trip_beat = clampf(val, 0.0, 1.0)
		settings_changed.emit("trip_beat", _trip_beat)
		_save()

var trip_trails: float:
	get: return _trip_trails
	set(val):
		_trip_trails = clampf(val, 0.0, 1.0)
		settings_changed.emit("trip_trails", _trip_trails)
		_save()


func _ready() -> void:
	_load()


func get_char_delay_ms() -> float:
	return float(TEXT_SPEED_MS.get(_text_speed, 28))


func get_text_scale() -> float:
	return _txt_scale


## (2026-11-08) Run from the Godot editor, the game plays EMBEDDED in the
## editor's Game tab (Godot 4.4+), and Godot ignores window size and
## fullscreen requests there — SCREEN SIZE seemed to do nothing. The wide
## layout still follows the tab's own size. To test window sizes: the Game
## tab's menu → turn off "Embed Game on Next Play", or run the game on its
## own (tools/play.sh).
func window_sizes_available() -> bool:
	return not Engine.is_embedded_in_editor()


func _apply_window_mode(mode: String) -> void:
	if not window_sizes_available():
		push_warning("[Settings] window size '%s' not applied: the game is embedded in the editor's Game tab" % mode)
		return
	match mode:
		"720p":
			call_deferred("_resize_window", 1280, 720)
		"900p":
			call_deferred("_resize_window", 1600, 900)
		"1080p":
			call_deferred("_resize_window", 1920, 1080)
		"1440p":
			call_deferred("_resize_window", 2560, 1440)
		"ultrawide":
			call_deferred("_resize_window", 3440, 1440)
		"fullscreen":
			call_deferred("_set_fullscreen")


## (2026-11-09, the user: "Ultrawide setting isn't taking, still." / "In
## scenes are back to their old resolution.") The size went to the
## DisplayServer directly, behind the root Window's back: the OS window grew
## to 3440x1440 and the game went on believing it was 1280x720 — the picture
## at its old resolution in a corner of the new window (ScreenProbe shows
## it: window (3440, 1440), root.size (1280, 720)). The DisplayServer records
## the size it was asked for, so the "window changed" event that would tell
## the root Window never fires. EVERY size / mode change goes through the
## root Window (its setters call the DisplayServer AND resize the viewport);
## _sync_root_window then checks the two agree and makes them.
func _set_fullscreen() -> void:
	var root: Window = get_tree().root
	root.borderless = false
	root.mode = Window.MODE_FULLSCREEN
	_sync_root_window.call_deferred(true)


func _resize_window(w: int, h: int) -> void:
	# (2026-10-19) Fit the screen's USABLE area (the taskbar and the window's
	# title bar take some of it): a 1080p window on a smaller display ran past
	# its bottom and right. Too big to fit → maximised; else centred inside it.
	var root: Window = get_tree().root
	var screen: int = DisplayServer.window_get_current_screen()
	# (2026-11-09) A size that IS the screen (ULTRAWIDE on a 3440x1440
	# monitor, 1440p on a 1440p one) is that screen's fullscreen: maximised
	# it lost the title bar's and the taskbar's rows and was never the
	# resolution asked for.
	var scr: Vector2i = DisplayServer.screen_get_size(screen)
	if w == scr.x and h == scr.y:
		_set_fullscreen()
		return
	root.borderless = false
	if root.mode != Window.MODE_WINDOWED:
		root.mode = Window.MODE_WINDOWED
	var usable: Rect2i = DisplayServer.screen_get_usable_rect(screen)
	var deco: Vector2i = DisplayServer.window_get_size_with_decorations() - DisplayServer.window_get_size()
	var room: Vector2i = usable.size - deco
	if w > room.x or h > room.y:
		root.mode = Window.MODE_MAXIMIZED
		_sync_root_window.call_deferred(false)
		return
	root.size = Vector2i(w, h)
	root.position = usable.position + (usable.size - Vector2i(w, h) - deco) / 2
	_sync_root_window.call_deferred(false)


## The root Window must be the size the OS window really is. Checked for a
## second after a change (a window manager answers late); a mismatch is
## corrected through the Window, which resizes the viewport.
## `fill_screen`: fullscreen was asked for. A desktop that does not grant it
## (no window manager, a compositor that ignores the request) leaves the
## window at its old size — after 45 frames the window is made a borderless
## one the size of the screen instead, which is the same picture.
var _sync_serial: int = 0


func _sync_root_window(fill_screen: bool) -> void:
	_sync_serial += 1
	var mine: int = _sync_serial
	for i in 60:
		await get_tree().process_frame
		if mine != _sync_serial:
			return                      # a newer change took over
		var root: Window = get_tree().root
		var real: Vector2i = DisplayServer.window_get_size()
		if fill_screen and i == 45:
			var screen: int = DisplayServer.window_get_current_screen()
			var scr: Vector2i = DisplayServer.screen_get_size(screen)
			if real.x < scr.x - 8 or real.y < scr.y - 8:
				push_warning("[Settings] fullscreen was not granted (window %s on a %s screen) — borderless, the screen's size" % [real, scr])
				root.mode = Window.MODE_WINDOWED
				root.borderless = true
				root.position = DisplayServer.screen_get_position(screen)
				root.size = scr
				continue
		if real.x > 0 and real.y > 0 and root.size != real:
			push_warning("[Settings] the game window is %s, the game thought %s — corrected" % [real, root.size])
			root.size = real


func _load() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(SAVE_PATH) != OK:
		# First run with no settings file. Exported builds (the
		# Steam Machine target) live on a TV — default fullscreen.
		# Editor / source runs keep the windowed dev default.
		if OS.has_feature("template"):
			_window_mode = "fullscreen"
			_apply_window_mode(_window_mode)
		return
	var raw_size = cfg.get_value("settings", "txt_scale", null)
	if raw_size == null:
		var legacy = str(cfg.get_value("settings", "text_size", "normal"))
		if LEGACY_SIZE.has(legacy.to_lower()):
			_txt_scale = LEGACY_SIZE[legacy.to_lower()]
		elif legacy.is_valid_float():
			_txt_scale = clampf(float(legacy), 0.5, 3.0)
	else:
		_txt_scale = clampf(float(raw_size), 0.5, 3.0)
	_text_speed      = str(cfg.get_value("settings", "text_speed",      "normal"))
	_bgm_vol         = float(cfg.get_value("settings", "bgm_vol",        0.65))
	_sfx_vol         = float(cfg.get_value("settings", "sfx_vol",        0.80))
	_voice_vol       = float(cfg.get_value("settings", "voice_vol",      0.80))
	_skip_unread     = bool(cfg.get_value("settings",  "skip_unread",    false))
	_auto_advance_ms = int(cfg.get_value("settings",   "auto_advance_ms", 0))
	_window_mode     = str(cfg.get_value("settings",   "window_mode",    "720p"))
	_haptics         = clampf(float(cfg.get_value("settings", "haptics", 1.0)), 0.0, 1.0)
	_music_skin      = str(cfg.get_value("settings",   "music_skin",     "diner_booth"))
	_music_viz       = str(cfg.get_value("settings",   "music_viz",      "peak_meter"))
	_music_jukebox   = bool(cfg.get_value("settings",  "music_jukebox",  true))
	_trip_amount     = clampf(float(cfg.get_value("settings", "trip_amount", 0.75)), 0.0, 1.0)
	_trip_flow       = clampf(float(cfg.get_value("settings", "trip_flow", 1.0)), 0.0, 1.0)
	_trip_lines      = clampf(float(cfg.get_value("settings", "trip_lines", 1.0)), 0.0, 1.0)
	_trip_colour     = clampf(float(cfg.get_value("settings", "trip_colour", 1.0)), 0.0, 1.0)
	_trip_beat       = clampf(float(cfg.get_value("settings", "trip_beat", 1.0)), 0.0, 1.0)
	_trip_trails     = clampf(float(cfg.get_value("settings", "trip_trails", 1.0)), 0.0, 1.0)
	_auto_play       = bool(cfg.get_value("settings",  "auto_play",      false))
	_hud_bar         = str(cfg.get_value("settings",   "hud_bar",        "auto"))
	_wide_screens    = str(cfg.get_value("settings",   "wide_screens",   "fill"))
	_detail_3d       = str(cfg.get_value("settings",   "detail_3d",      "native"))
	_apply_window_mode(_window_mode)


func _save() -> void:
	var cfg := ConfigFile.new()
	cfg.set_value("settings", "txt_scale",       _txt_scale)
	cfg.set_value("settings", "text_speed",      _text_speed)
	cfg.set_value("settings", "bgm_vol",         _bgm_vol)
	cfg.set_value("settings", "sfx_vol",         _sfx_vol)
	cfg.set_value("settings", "voice_vol",       _voice_vol)
	cfg.set_value("settings", "skip_unread",     _skip_unread)
	cfg.set_value("settings", "auto_advance_ms", _auto_advance_ms)
	cfg.set_value("settings", "window_mode",     _window_mode)
	cfg.set_value("settings", "wide_screens",    _wide_screens)
	cfg.set_value("settings", "detail_3d",       _detail_3d)
	cfg.set_value("settings", "haptics",         _haptics)
	cfg.set_value("settings", "music_skin",      _music_skin)
	cfg.set_value("settings", "music_viz",       _music_viz)
	cfg.set_value("settings", "music_jukebox",   _music_jukebox)
	cfg.set_value("settings", "trip_amount",     _trip_amount)
	cfg.set_value("settings", "trip_flow",       _trip_flow)
	cfg.set_value("settings", "trip_lines",      _trip_lines)
	cfg.set_value("settings", "trip_colour",     _trip_colour)
	cfg.set_value("settings", "trip_beat",       _trip_beat)
	cfg.set_value("settings", "trip_trails",     _trip_trails)
	cfg.set_value("settings", "auto_play",       _auto_play)
	cfg.set_value("settings", "hud_bar",         _hud_bar)
	cfg.save(SAVE_PATH)
