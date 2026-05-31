extends Node
## Audio manager — three buses (BGM, SFX, Voice), BGM cross-fade, music queue.
## Autoloaded as "AudioMgr".

const FADE_DURATION  := 0.6
const DUCK_RATIO     := 0.32   # BGM ducks to 32% when dialogue is showing
const DUCK_FADE      := 0.35
const UNDUCK_FADE    := 0.70

signal track_changed(src: String)

var _bgm:   AudioStreamPlayer
var _sfx:   AudioStreamPlayer
var _voice: AudioStreamPlayer

var _fade_timer:  float  = 0.0
var _fade_from:   float  = 1.0
var _fade_target: float  = 1.0
var _pending_src: String = ""
var _current_src: String = ""
var _paused:      bool   = false
var _shuffle:     bool   = true

var _duck_tween: Tween    = null
var _is_ducked:  bool     = false

var _music_heard: Dictionary = {}

# Spectrum analyzer on BGM bus, for visualizer windows.
var _bgm_spectrum: AudioEffectSpectrumAnalyzerInstance = null

const HEARD_PATH := "user://progress/music_heard.cfg"


func _ready() -> void:
	_setup_buses()
	_setup_players()
	_load_heard()


func _setup_buses() -> void:
	for bus_name in ["BGM", "SFX", "Voice"]:
		if AudioServer.get_bus_index(bus_name) == -1:
			AudioServer.add_bus()
			var idx := AudioServer.get_bus_count() - 1
			AudioServer.set_bus_name(idx, bus_name)
			AudioServer.set_bus_send(idx, "Master")
	set_bus_volume("BGM",   Settings.bgm_vol)
	set_bus_volume("SFX",   Settings.sfx_vol)
	set_bus_volume("Voice", Settings.voice_vol)
	# Add panner to SFX bus for positional dialogue audio
	var sfx_idx := AudioServer.get_bus_index("SFX")
	if sfx_idx != -1 and AudioServer.get_bus_effect_count(sfx_idx) == 0:
		var panner := AudioEffectPanner.new()
		panner.pan = 0.0
		AudioServer.add_bus_effect(sfx_idx, panner)

	# Add spectrum analyzer to BGM bus so visualizers can read magnitudes
	var bgm_idx := AudioServer.get_bus_index("BGM")
	if bgm_idx != -1:
		var has_spec := false
		for i in range(AudioServer.get_bus_effect_count(bgm_idx)):
			if AudioServer.get_bus_effect(bgm_idx, i) is AudioEffectSpectrumAnalyzer:
				_bgm_spectrum = AudioServer.get_bus_effect_instance(bgm_idx, i) as AudioEffectSpectrumAnalyzerInstance
				has_spec = true
				break
		if not has_spec:
			var spec := AudioEffectSpectrumAnalyzer.new()
			spec.fft_size = AudioEffectSpectrumAnalyzer.FFT_SIZE_2048
			AudioServer.add_bus_effect(bgm_idx, spec)
			var spec_idx := AudioServer.get_bus_effect_count(bgm_idx) - 1
			_bgm_spectrum = AudioServer.get_bus_effect_instance(bgm_idx, spec_idx) as AudioEffectSpectrumAnalyzerInstance


# Returns BGM magnitude in [0..~1] for the given frequency range, or 0 if
# the analyzer isn't initialized.
func get_bgm_magnitude(freq_low: float, freq_high: float) -> float:
	if _bgm_spectrum == null:
		return 0.0
	return _bgm_spectrum.get_magnitude_for_frequency_range(freq_low, freq_high).length()


func _setup_players() -> void:
	_bgm = AudioStreamPlayer.new()
	_bgm.bus = "BGM"
	_bgm.finished.connect(_on_bgm_finished)
	add_child(_bgm)

	_sfx = AudioStreamPlayer.new()
	_sfx.bus = "SFX"
	add_child(_sfx)

	_voice = AudioStreamPlayer.new()
	_voice.bus = "Voice"
	add_child(_voice)


func _process(delta: float) -> void:
	if _fade_timer <= 0.0:
		return
	_fade_timer -= delta
	var t: float = clampf(1.0 - (_fade_timer / FADE_DURATION), 0.0, 1.0)
	var vol := lerpf(_fade_from, _fade_target, t)
	_bgm.volume_db = linear_to_db(maxf(vol, 0.0001))
	if _fade_timer <= 0.0:
		_fade_timer = 0.0
		_bgm.volume_db = linear_to_db(maxf(_fade_target, 0.0001))
		if _fade_target == 0.0:
			_bgm.stop()
			if _pending_src != "":
				_start_bgm(_pending_src)
				_pending_src = ""


# ── Public API ────────────────────────────────────────────────────────────────

func set_bus_volume(bus_name: String, vol: float) -> void:
	var idx := AudioServer.get_bus_index(bus_name)
	if idx != -1:
		AudioServer.set_bus_volume_db(idx, linear_to_db(maxf(vol, 0.0001)))


func play_bgm(src: String) -> void:
	if src == _current_src and _bgm.playing and not _paused:
		return
	_mark_heard(src)
	if _bgm.playing or _paused:
		_paused = false
		_bgm.stream_paused = false
		_pending_src = src
		_fade_out()
	else:
		_start_bgm(src)


func stop_bgm() -> void:
	_pending_src = ""
	_paused = false
	if _bgm.playing:
		_fade_out()


func pause_bgm() -> void:
	if _bgm.playing and not _paused:
		_bgm.stream_paused = true
		_paused = true


func resume_bgm() -> void:
	if _paused:
		_bgm.stream_paused = false
		_paused = false


func play_sfx(src: String) -> void:
	var stream := _load_audio(src)
	if stream:
		_sfx.stream = stream
		_sfx.play()


func duck() -> void:
	if _is_ducked:
		return
	_is_ducked = true
	_tween_bgm_bus(Settings.bgm_vol * DUCK_RATIO, DUCK_FADE)


func unduck() -> void:
	if not _is_ducked:
		return
	_is_ducked = false
	_tween_bgm_bus(Settings.bgm_vol, UNDUCK_FADE)


func set_sfx_pan(pan: float) -> void:
	var idx := AudioServer.get_bus_index("SFX")
	if idx == -1 or AudioServer.get_bus_effect_count(idx) == 0:
		return
	var effect = AudioServer.get_bus_effect(idx, 0)
	if effect is AudioEffectPanner:
		(effect as AudioEffectPanner).pan = clampf(pan, -1.0, 1.0)


func play_voice(src: String) -> void:
	if src == "":
		return
	var stream := _load_audio(src)
	if stream:
		_voice.stream = stream
		_voice.play()


func stop_voice() -> void:
	_voice.stop()


func is_voice_playing() -> bool:
	return _voice.playing


func get_current_track() -> String:
	return _current_src


func is_playing() -> bool:
	return _bgm.playing and not _paused


func is_paused() -> bool:
	return _paused


# Current playback head in seconds (0 if nothing is loaded).
func get_playback_position() -> float:
	if _bgm.stream == null:
		return 0.0
	return _bgm.get_playback_position()


# Length of the loaded BGM stream in seconds (0 if unknown/none).
func get_stream_length() -> float:
	if _bgm.stream == null:
		return 0.0
	return _bgm.stream.get_length()


# Seek the loaded BGM stream to an absolute position in seconds.
func seek(pos: float) -> void:
	if _bgm.stream == null:
		return
	var length := _bgm.stream.get_length()
	if length > 0.0:
		pos = clampf(pos, 0.0, length - 0.05)
	_bgm.seek(maxf(pos, 0.0))


func is_shuffle() -> bool:
	return _shuffle


func is_heard(src: String) -> bool:
	return src in _music_heard


func get_heard_set() -> Dictionary:
	return _music_heard.duplicate()


func set_shuffle(enabled: bool) -> void:
	_shuffle = enabled


func play_next() -> void:
	var next := _pick_next(_current_src)
	if next != "":
		play_bgm(next)


func play_prev() -> void:
	var catalog: Array = SceneDataDB.get_music_catalog()
	if catalog.is_empty():
		return
	var cur_idx := -1
	for i in catalog.size():
		if (catalog[i] as Dictionary).get("src", "") == _current_src:
			cur_idx = i
			break
	if cur_idx > 0:
		play_bgm((catalog[cur_idx - 1] as Dictionary).get("src", ""))
	elif not catalog.is_empty():
		play_bgm((catalog[catalog.size() - 1] as Dictionary).get("src", ""))


# ── Internal ──────────────────────────────────────────────────────────────────

func _tween_bgm_bus(target_linear: float, duration: float) -> void:
	var idx := AudioServer.get_bus_index("BGM")
	if idx == -1:
		return
	var current := db_to_linear(AudioServer.get_bus_volume_db(idx))
	if _duck_tween and _duck_tween.is_valid():
		_duck_tween.kill()
	_duck_tween = create_tween()
	_duck_tween.tween_method(
		func(v: float) -> void:
			AudioServer.set_bus_volume_db(idx, linear_to_db(maxf(v, 0.0001))),
		current, target_linear, duration
	)


func _start_bgm(src: String) -> void:
	var stream := _load_audio(src)
	if not stream:
		push_warning("AudioMgr: BGM not found: " + src)
		return
	_current_src = src
	_bgm.stream = stream
	_bgm.volume_db = linear_to_db(0.0001)
	_bgm.play()
	_fade_in()
	track_changed.emit(src)


func _fade_in() -> void:
	_fade_from   = 0.0
	_fade_target = 1.0
	_fade_timer  = FADE_DURATION


func _fade_out() -> void:
	_fade_from   = db_to_linear(_bgm.volume_db)
	_fade_target = 0.0
	_fade_timer  = FADE_DURATION


func _on_bgm_finished() -> void:
	var next := _pick_next(_current_src)
	_start_bgm(next if next != "" else _current_src)


func _pick_next(current_src: String) -> String:
	var catalog: Array = SceneDataDB.get_music_catalog()
	if catalog.is_empty():
		return ""
	if not _shuffle:
		var cur_idx := -1
		for i in catalog.size():
			if (catalog[i] as Dictionary).get("src", "") == current_src:
				cur_idx = i
				break
		if cur_idx >= 0 and cur_idx + 1 < catalog.size():
			return (catalog[cur_idx + 1] as Dictionary).get("src", "")
		return (catalog[0] as Dictionary).get("src", "")

	var current_vol := 0
	for track: Dictionary in catalog:
		if track.get("src", "") == current_src:
			current_vol = track.get("vol", 0)
			break

	var same_vol: Array = []
	var other_vol: Array = []
	for track: Dictionary in catalog:
		var src: String = track.get("src", "")
		if src != current_src and _music_heard.has(src):
			if track.get("vol", 0) == current_vol:
				same_vol.append(src)
			else:
				other_vol.append(src)

	if not same_vol.is_empty():
		return same_vol[0]
	if not other_vol.is_empty():
		return other_vol[0]
	return ""


func _mark_heard(src: String) -> void:
	if src == "":
		return
	_music_heard[src] = true
	_save_heard()


func _load_heard() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(HEARD_PATH) != OK:
		return
	if cfg.has_section("heard"):
		for key in cfg.get_section_keys("heard"):
			_music_heard[key] = true


func _save_heard() -> void:
	DirAccess.make_dir_recursive_absolute("user://progress")
	var cfg := ConfigFile.new()
	for src in _music_heard:
		cfg.set_value("heard", src, true)
	cfg.save(HEARD_PATH)


func _load_audio(src: String) -> AudioStream:
	var path := "res://" + src
	if ResourceLoader.exists(path):
		return ResourceLoader.load(path) as AudioStream
	return null
