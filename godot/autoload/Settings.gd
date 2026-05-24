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

var window_mode: String:
	get: return _window_mode
	set(val):
		_window_mode = val
		_apply_window_mode(val)
		settings_changed.emit("window_mode", val)
		_save()


func _ready() -> void:
	_load()


func get_char_delay_ms() -> float:
	return float(TEXT_SPEED_MS.get(_text_speed, 28))


func get_text_scale() -> float:
	return _txt_scale


func _apply_window_mode(mode: String) -> void:
	match mode:
		"720p":
			call_deferred("_resize_window", 1280, 720)
		"900p":
			call_deferred("_resize_window", 1600, 900)
		"1080p":
			call_deferred("_resize_window", 1920, 1080)
		"fullscreen":
			call_deferred("_set_fullscreen")


func _set_fullscreen() -> void:
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)


func _resize_window(w: int, h: int) -> void:
	var screen_size: Vector2i = DisplayServer.screen_get_size()
	var clamped_w: int = mini(w, screen_size.x)
	var clamped_h: int = mini(h, screen_size.y)
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	DisplayServer.window_set_size(Vector2i(clamped_w, clamped_h))
	DisplayServer.window_set_position((screen_size - Vector2i(clamped_w, clamped_h)) / 2)


func _load() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(SAVE_PATH) != OK:
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
	cfg.save(SAVE_PATH)
