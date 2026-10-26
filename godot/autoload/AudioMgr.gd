extends Node
## Audio manager — three buses (BGM, SFX, Voice), BGM cross-fade, music queue.
## Autoloaded as "AudioMgr".

const FADE_DURATION  := 0.6
const DUCK_RATIO     := 0.32   # BGM ducks to 32% when dialogue is showing
const DUCK_FADE      := 0.35
const UNDUCK_FADE    := 0.70

# ── Per-locale ambient bed ("the world hum") ──────────────────────
# When a 3D locale that owns an ambient bed loads, the dominant
# Music Player track ducks WAY down (to AMBIENT_DUCK) and an
# inverted ambient soundtrack — a looping room-tone/drone on its
# own Ambient bus — rises to take the room. Leaving the locale
# crossfades back: ambient falls, BGM returns. The two are
# inversely coupled, driven from the same enter/exit calls.
const AMBIENT_DUCK   := 0.14   # BGM sinks to 14% under an active locale bed
const AMBIENT_FADE   := 1.4    # slow, atmospheric crossfade (s)
const AMBIENT_CFG    := "res://resources/audio/locale_ambient.json"

# ── Signatures (2026-09-12) ───────────────────────────────────────
# A catalog entry that names a character in `chars` and carries
# "theme" in its id is that character's SIGNATURE: a 12-20 s figure
# ("Sharp's signature, played whenever Sharp shows up"). GameEngine
# cues it once per scene on the character's first show or line; it
# plays as a one-shot on the Music Player and hands back whatever was
# playing. While it plays under a world hum the duck INVERTS — the
# hum sinks to SIGNATURE_HUM of its gain and the signature rises to
# full — then both return when it ends. "Full" is still under the
# dialogue duck (DUCK_RATIO, always on in the VN), so the hum has to
# go well below that for the signature to read as foreground: 0.20
# puts it ~5 dB above the room.
const SIGNATURE_HUM  := 0.20
const SIGNATURE_FADE := 0.5

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

# ── Jukebox mode ──────────────────────────────────────────────────
# ON (default): the Music Player owns playback. The FULL catalog
# rotates continuously; scene BGM requests only mark the track heard
# (or seed the rotation when nothing is playing yet). Looping is
# defeated so no track plays twice in a row.
# OFF: classic behavior — scenes set their own looping BGM and the
# VN queue/chapter logic drives track changes.
# Toggled from the Music Player overlay; persisted in Settings.
var jukebox_on: bool = true
var _scene_src:  String = ""    # last BGM a scene asked for
var _scene_loop: bool   = true  # whether that scene bed should loop

var _duck_tween: Tween    = null
var _is_ducked:  bool     = false

# Per-locale ambient bed state.
var _ambient:         AudioStreamPlayer = null
var _ambient_tween:   Tween             = null
var _ambient_active:  bool              = false
var _ambient_locale:  String            = ""
var _ambient_bed: String = ""      # the hum's src, un-prefixed — compared with _current_src
var _ambient_gain: float = 1.0     # the locale's configured hum gain (locale_ambient.json)
var _signature_srcs: Dictionary = {}   # src -> true, built lazily from the catalog
var _signature_srcs_built: bool = false
var _ambient_cfg:     Dictionary        = {}
var _ambient_cfg_loaded: bool           = false

var _music_heard: Dictionary = {}

# ── Stillness (2026-10-14) ────────────────────────────────────────
# The player's quiet moment (GameEngine · J / pad Y): the text goes, the
# camera settles on a picture in the room, and the sound settles too. A
# catalog track tagged `"moments": ["stillness"]` (the audio director's
# ambient pieces) fades in on its own player — this room's piece first
# (`"locales": [...]`), then this volume's, then any — while the Music
# Player track and the room hum sink under it. Nothing tagged yet: the
# music simply dips. Leaving reverses it.
const STILL_FADE_IN  := 2.4    # slow — the moment arrives
const STILL_FADE_OUT := 1.2
const STILL_BGM_MULT := 0.18   # the scene's music under the stillness bed
const STILL_HUM_MULT := 0.45   # the room hum under it
const STILL_GAIN     := 0.85
var _still: AudioStreamPlayer = null
var _still_tween: Tween = null
var _still_active: bool = false
var _still_src: String = ""
var _still_rot: int = 0

# Sources that have failed to load (file missing, corrupt, undecodable).
# Each src only logs once per session — subsequent attempts short-circuit
# silently so the queue can advance to the next track without spam.
var _failed_srcs: Dictionary = {}

# Spectrum analyzer on BGM bus, for visualizer windows.
var _bgm_spectrum: AudioEffectSpectrumAnalyzerInstance = null

# Oneshot-then-resume support. When a caller plays a BGM via
# `play_oneshot_bgm`, the previous BGM src is captured here so the
# `finished` handler can fall back to it instead of looping the
# oneshot or picking the next queued track. Cleared as soon as the
# resume kicks in.
var _oneshot_resume_src: String = ""

const HEARD_PATH := "user://progress/music_heard.cfg"

# ── Adaptive music: stems layered by intensity ───────────────────────────────
# A catalog track with a sibling "<basename>.stems.json" (written by the DAW's
# STEMS + MIX export, godot/tools/daw.html) plays as an AudioStreamSynchronized
# of its stems instead of the stereo mix. Each stem has a `layer` threshold
# (pad 0 · chords 0 · bass 0.25 · drums 0.5 · lead 0.75); set_music_intensity()
# fades in every stem whose threshold is at or below the level. Missing or
# unreadable stems fall back to the mix, so a half-written export never breaks
# playback. Intensity 1.0 = the full mix, which is the default.
#
# Temp tracks (the DAW / AUDIO DIRECTOR) are Ogg Vorbis: "<basename>.temp.ogg" +
# "<basename>.stems/<part>.ogg", with a manifest marked `temp: true`. The lookup
# order is the catalog src (real audio) → "<basename>.wav" (FIELD RECORDER /
# TAPE STUDIO, or a temp from before Ogg) → "<basename>.temp.ogg", and a temp
# manifest's stems never play over real audio. Ogg has no loop chunk: the
# manifest's `loop` / `loop_offset` (seconds; the loop end is the stream end)
# are set on every Ogg stream it names — its mix and its stems.
const STEM_FADE := 1.5
var adaptive_music: bool = true
var _intensity: float = 1.0
var _stem_stream: AudioStreamSynchronized = null
var _stem_layers: Array = []      # [{index, layer, name}]
var _stem_gain: PackedFloat32Array = PackedFloat32Array()
var _stem_target: PackedFloat32Array = PackedFloat32Array()
var _stem_rate: float = 1.0 / STEM_FADE


func _ready() -> void:
	_setup_buses()
	_setup_players()
	_load_heard()
	jukebox_on = Settings.music_jukebox


func _setup_buses() -> void:
	for bus_name in ["BGM", "SFX", "Voice", "Ambient"]:
		if AudioServer.get_bus_index(bus_name) == -1:
			AudioServer.add_bus()
			var idx := AudioServer.get_bus_count() - 1
			AudioServer.set_bus_name(idx, bus_name)
			AudioServer.set_bus_send(idx, "Master")
	set_bus_volume("BGM",   Settings.bgm_vol)
	set_bus_volume("SFX",   Settings.sfx_vol)
	set_bus_volume("Voice", Settings.voice_vol)
	# Ambient starts silent — a locale bed fades it up when it takes
	# the room, and back to silence on exit.
	set_bus_volume("Ambient", 0.0001)
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

	_ambient = AudioStreamPlayer.new()
	_ambient.bus = "Ambient"
	add_child(_ambient)

	# the stillness bed: its own player (and its own fades, on the
	# player, so the locale hum's bus tweens never touch it)
	_still = AudioStreamPlayer.new()
	# Master, not Ambient (silent in a room with no hum) or BGM (ducked
	# for the moment); the music-volume setting scales it in _tween_still
	_still.bus = "Master"
	_still.volume_db = linear_to_db(0.0001)
	add_child(_still)


func _process(delta: float) -> void:
	_step_stems(delta)
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
	# Normalize: callers pass both "assets/audio/…" (catalog srcs)
	# and "res://assets/audio/…" (host literals). Everything internal
	# — heard-marking, catalog matching, _load_audio — expects the
	# un-prefixed form. Without this, res://-prefixed requests got
	# double-prefixed in _load_audio and silently never played.
	src = src.trim_prefix("res://")
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


# Scene-driven BGM. Gameplay scenes (slowstick hosts, the VN, the
# gauntlet) call THIS instead of play_bgm. With the jukebox off it
# behaves exactly like play_bgm (plus looping the bed when `loop`).
# With the jukebox on, the request is remembered + marked heard but
# playback stays with the rotating catalog — the player said who
# controls the music.
func request_scene_bgm(src: String, loop: bool = true) -> void:
	src = src.trim_prefix("res://")
	_scene_src  = src
	_scene_loop = loop
	if not jukebox_on:
		play_bgm(src)
		return
	_mark_heard(src)
	# Seed the rotation if we're sitting in silence.
	if not _bgm.playing and not _paused and _pending_src == "" and _fade_timer <= 0.0:
		play_bgm(src)


# Scene-driven stop (VN scene end, host quit). A no-op while the
# jukebox owns playback — the rotation keeps rolling.
func stop_scene_bgm() -> void:
	_scene_src = ""
	if not jukebox_on:
		stop_bgm()


func set_jukebox(on: bool) -> void:
	if jukebox_on == on:
		return
	jukebox_on = on
	Settings.music_jukebox = on
	if on:
		# Player takes over: keep whatever is playing (rotation picks
		# up at track end), or start rolling from silence.
		if not is_playing() and not _paused:
			play_next()
	else:
		# Hand control back to the scene: return to its bed if the
		# rotation had wandered off it.
		if _scene_src != "" and _scene_src != _current_src:
			play_bgm(_scene_src)


# Play `src` once, then snap back to `resume_src` when it ends.
# Used by the gauntlet jukebox: a B-side plays one full revolution,
# then the diner ambient returns. If a resume isn't supplied, the
# currently-playing BGM is captured automatically.
func play_oneshot_bgm(src: String, resume_src: String = "") -> void:
	if src == "":
		return
	if resume_src == "":
		resume_src = _current_src
	_oneshot_resume_src = resume_src
	play_bgm(src)


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
	_retarget_bgm_bus(DUCK_FADE)


func unduck() -> void:
	if not _is_ducked:
		return
	_is_ducked = false
	_retarget_bgm_bus(UNDUCK_FADE)


# The BGM bus target is the product of every active attenuation:
# the dialogue duck and the locale-ambient duck compose so that,
# e.g., dialogue shown inside a locale bed doesn't fight over the
# bus (both pull it down, we take the combined target).
func _bgm_bus_target() -> float:
	var duck_mult: float = DUCK_RATIO if _is_ducked else 1.0
	if _still_active:
		duck_mult *= STILL_BGM_MULT
	var amb_mult:  float = AMBIENT_DUCK if _ambient_active else 1.0
	# The hum and the Music Player track are, since 2026-09-12, usually
	# the SAME bed (one locale→bed table feeds both layers). A 14% ghost
	# of the file playing under itself, out of phase, is a chorus effect
	# nobody asked for: when they coincide the Music Player goes to the
	# floor and the hum carries the room alone.
	if _ambient_active and _ambient_bed != "" and _current_src == _ambient_bed:
		amb_mult = 0.0
	# A signature is the one Music Player track that OUTRANKS the hum:
	# it comes up to full and the hum sinks instead (see _ambient_target).
	if _ambient_active and _is_signature(_current_src):
		amb_mult = 1.0
	return Settings.bgm_vol * duck_mult * amb_mult


func _retarget_bgm_bus(duration: float) -> void:
	_tween_bgm_bus(_bgm_bus_target(), duration)


# The Ambient bus target while a hum is active: the locale's gain,
# pulled down to SIGNATURE_HUM of itself for as long as a signature
# is the Music Player track.
func _ambient_target() -> float:
	var sig_mult: float = SIGNATURE_HUM if _is_signature(_current_src) else 1.0
	var still_mult: float = STILL_HUM_MULT if _still_active else 1.0
	return Settings.bgm_vol * _ambient_gain * sig_mult * still_mult


func _retarget_ambient_bus(duration: float) -> void:
	if _ambient_active:
		_tween_ambient_bus(_ambient_target(), duration)


func _is_signature(src: String) -> bool:
	if src == "":
		return false
	if not _signature_srcs_built:
		_signature_srcs_built = true
		for entry: Dictionary in SceneDataDB.get_music_catalog():
			var chars: Array = entry.get("chars", [])
			var id: String = String(entry.get("id", ""))
			if not chars.is_empty() and id.contains("theme"):
				_signature_srcs[String(entry.get("src", ""))] = true
	return _signature_srcs.has(src)


# Play `char_key`'s signature now, once, then return to whatever was
# playing. Returns the src cued, or "" when the character has no
# signature in the current volume, its file is missing, or one is
# already on its way (a queued unlock still catches it later).
# `any_volume` lifts the volume scope — the gauntlet board cues its
# visitors' themes from vol 5 and the Stranger's is vol 1's.
func cue_signature(char_key: String, any_volume: bool = false) -> String:
	if char_key == "":
		return ""
	if _pending_src != "" or _is_signature(_current_src):
		return ""
	for entry: Dictionary in SceneDataDB.get_music_catalog():
		var chars: Array = entry.get("chars", [])
		var id: String = String(entry.get("id", ""))
		if not (char_key in chars) or not id.contains("theme"):
			continue
		if not any_volume and not _entry_in_current_volume(entry):
			continue
		var src: String = String(entry.get("src", ""))
		if src == "" or src in _failed_srcs:
			continue
		var p := "res://" + src
		if not ResourceLoader.exists(p) and not FileAccess.file_exists(ProjectSettings.globalize_path(p)):
			_failed_srcs[src] = true
			continue
		# unlock_tracks_for_character queued it as well — one hearing, not two.
		if src in _queue:
			_queue.erase(src)
			queue_changed.emit()
		play_oneshot_bgm(src)
		return src
	return ""


# ── Per-locale ambient bed ────────────────────────────────────────

# Called by GameEngine when a 3D locale background loads. If the
# locale has an ambient bed configured, duck the dominant BGM way
# down and raise the inverted ambient soundtrack; otherwise ensure
# any previous locale's bed is retired.
func enter_locale_ambient(locale_id: String) -> void:
	_ensure_ambient_cfg()
	if locale_id == "":
		exit_locale_ambient()
		return
	var entry: Variant = _ambient_cfg.get(locale_id, null)
	if not (entry is Dictionary):
		# No bed for this locale — retire any prior one.
		exit_locale_ambient()
		return
	var cfg := entry as Dictionary
	var bed: String = String(cfg.get("bed", ""))
	if bed == "":
		exit_locale_ambient()
		return
	if _ambient_active and _ambient_locale == locale_id:
		return   # already humming this room
	var stream := _load_audio(bed)
	if stream == null:
		exit_locale_ambient()
		return
	_set_stream_loop(stream, true)
	_ambient.stream = stream
	_ambient.volume_db = linear_to_db(0.0001)
	_ambient.play()
	_ambient_active = true
	_ambient_locale = locale_id
	_ambient_bed = bed.trim_prefix("res://")
	_ambient_gain = float(cfg.get("gain", 1.0))
	_tween_ambient_bus(_ambient_target(), AMBIENT_FADE)
	_retarget_bgm_bus(AMBIENT_FADE)


# Crossfade back to the Music Player: ambient falls to silence and
# stops, BGM returns to its (possibly dialogue-ducked) level.
func exit_locale_ambient() -> void:
	if not _ambient_active:
		return
	_ambient_active = false
	_ambient_locale = ""
	_ambient_bed = ""
	_tween_ambient_bus(0.0, AMBIENT_FADE, true)
	_retarget_bgm_bus(UNDUCK_FADE)


## Begin a stillness moment. Returns the bed's src ("" = the music only
## dips — nothing in the catalog is tagged for stillness yet).
func enter_stillness(locale_id: String, vol: int) -> String:
	if _still_active:
		return _still_src
	_still_active = true
	var src: String = _pick_stillness_bed(locale_id, vol)
	_still_src = src
	if src != "":
		var stream := _load_audio(src)
		if stream != null:
			_set_stream_loop(stream, true)
			_still.stream = stream
			_still.volume_db = linear_to_db(0.0001)
			_still.play()
			_tween_still(Settings.bgm_vol * STILL_GAIN, STILL_FADE_IN, false)
		else:
			_still_src = ""
	_retarget_bgm_bus(STILL_FADE_IN)
	_retarget_ambient_bus(STILL_FADE_IN)
	return _still_src


func exit_stillness() -> void:
	if not _still_active:
		return
	_still_active = false
	_tween_still(0.0, STILL_FADE_OUT, true)
	_retarget_bgm_bus(STILL_FADE_OUT)
	_retarget_ambient_bus(STILL_FADE_OUT)


func is_stillness_active() -> bool:
	return _still_active


## The catalog's stillness pieces, best fit first: this room's, then this
## volume's, then any; rotated so the same moment does not always get the
## same piece.
func _pick_stillness_bed(locale_id: String, vol: int) -> String:
	var room: Array[String] = []
	var same_vol: Array[String] = []
	var any: Array[String] = []
	for entry: Dictionary in SceneDataDB.get_music_catalog():
		var moments: Array = entry.get("moments", [])
		var tags: Array = entry.get("tags", [])
		if not ("stillness" in moments or "stillness" in tags):
			continue
		var src: String = String(entry.get("src", ""))
		if src == "":
			continue
		var locs: Array = entry.get("locales", [])
		if locale_id != "" and locale_id in locs:
			room.append(src)
		elif int(entry.get("vol", -1)) == vol:
			same_vol.append(src)
		else:
			any.append(src)
	for pool: Array[String] in [room, same_vol, any]:
		if not pool.is_empty():
			_still_rot += 1
			return pool[_still_rot % pool.size()]
	return ""


func _tween_still(target_linear: float, duration: float, stop_at_end: bool) -> void:
	if _still_tween and _still_tween.is_valid():
		_still_tween.kill()
	_still_tween = create_tween()
	_still_tween.tween_method(
		func(v: float) -> void:
			_still.volume_db = linear_to_db(maxf(v, 0.0001)),
		db_to_linear(_still.volume_db), target_linear, duration
	)
	if stop_at_end:
		_still_tween.tween_callback(func() -> void:
			if not _still_active:
				_still.stop())


func _tween_ambient_bus(target_linear: float, duration: float, stop_at_end: bool = false) -> void:
	var idx := AudioServer.get_bus_index("Ambient")
	if idx == -1:
		return
	var current := db_to_linear(AudioServer.get_bus_volume_db(idx))
	if _ambient_tween and _ambient_tween.is_valid():
		_ambient_tween.kill()
	_ambient_tween = create_tween()
	_ambient_tween.tween_method(
		func(v: float) -> void:
			AudioServer.set_bus_volume_db(idx, linear_to_db(maxf(v, 0.0001))),
		current, target_linear, duration
	)
	if stop_at_end:
		_ambient_tween.tween_callback(func() -> void:
			if not _ambient_active:
				_ambient.stop())


func _set_stream_loop(stream: AudioStream, on: bool) -> void:
	if stream is AudioStreamOggVorbis:
		(stream as AudioStreamOggVorbis).loop = on
	elif stream is AudioStreamMP3:
		(stream as AudioStreamMP3).loop = on
	elif stream is AudioStreamWAV:
		var w: AudioStreamWAV = stream as AudioStreamWAV
		w.loop_mode = AudioStreamWAV.LOOP_FORWARD if on else AudioStreamWAV.LOOP_DISABLED
		# A runtime-set loop needs a loop REGION: loop_end is 0 unless the
		# importer wrote one, and an empty region does not loop. The
		# world-hum beds are WAVs now (2026-09-12) and must loop.
		if on and w.loop_end <= w.loop_begin:
			w.loop_begin = 0
			w.loop_end = _last_audible_frame(w)


# The loop end for a WAV that was rendered as a one-shot: the last
# frame above the noise floor, not the file's end. Every legacy bed
# ends in a second of digital silence — the release tail's padding —
# and looping the whole file put that silence in every room every
# 40-70 s. Beds rendered with the synth's `loop` fold have no such
# tail and come back unchanged. Scans at most the last four seconds.
func _last_audible_frame(w: AudioStreamWAV) -> int:
	var frames: int = int(w.get_length() * float(w.mix_rate))
	if w.format != AudioStreamWAV.FORMAT_16_BITS:
		return frames
	var channels: int = 2 if w.stereo else 1
	var bytes_per_frame: int = 2 * channels
	var data: PackedByteArray = w.data
	var total: int = data.size() / bytes_per_frame
	if total <= 0:
		return frames
	var floor_frame: int = maxi(0, total - int(4.0 * float(w.mix_rate)))
	var f: int = total - 1
	while f > floor_frame:
		var off: int = f * bytes_per_frame
		var loud := false
		for c in channels:
			if absi(data.decode_s16(off + 2 * c)) > 16:
				loud = true
				break
		if loud:
			break
		f -= 1
	if f <= floor_frame:
		return frames
	return f + 1


func _ensure_ambient_cfg() -> void:
	if _ambient_cfg_loaded:
		return
	_ambient_cfg_loaded = true
	if not FileAccess.file_exists(AMBIENT_CFG):
		return
	var f := FileAccess.open(AMBIENT_CFG, FileAccess.READ)
	if f == null:
		return
	var txt := f.get_as_text()
	f.close()
	var parsed: Variant = JSON.parse_string(txt)
	if not (parsed is Dictionary):
		return
	var root := parsed as Dictionary
	# Support both a bare {locale: {...}} map and a wrapped
	# {"locales": {...}} form (leaving room for future globals).
	if root.has("locales") and root["locales"] is Dictionary:
		_ambient_cfg = root["locales"] as Dictionary
	else:
		_ambient_cfg = root


func is_ambient_active() -> bool:
	return _ambient_active


func current_ambient_locale() -> String:
	return _ambient_locale


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
	if _bgm.stream is AudioStreamSynchronized:
		var sync := _bgm.stream as AudioStreamSynchronized
		var longest := 0.0
		for i in sync.stream_count:
			var sub := sync.get_sync_stream(i)
			if sub:
				longest = maxf(longest, sub.get_length())
		return longest
	return _bgm.stream.get_length()


## 0.0 … 1.0. With layered (stems) music, fades stems in or out over `fade`
## seconds: 0 = pad / chords only, 0.25 + bass, 0.5 + drums, 0.75+ everything.
## Remembered across tracks; plain stereo tracks ignore it.
func set_music_intensity(level: float, fade: float = STEM_FADE) -> void:
	_intensity = clampf(level, 0.0, 1.0)
	_stem_rate = 1.0 / maxf(fade, 0.01)
	for l in _stem_layers:
		_stem_target[l.index] = 1.0 if _intensity + 0.0001 >= float(l.layer) else 0.0


## True when `src` (a catalog path) has something playable on disk: the file,
## the .wav sibling, the .temp.ogg temp, or a stems manifest. The MusicDirector
## only picks tracks that pass this, so missing catalog audio never silences
## a scene that already has music playing.
func can_play(src: String) -> bool:
	if src == "" or src in _failed_srcs:
		return false
	var base := src.get_basename()
	for p in [src, base + ".wav", base + ".temp.ogg", base + ".stems.json"]:
		if _exists(p):
			# a third-party temp (a cover / sample made from imported audio) is never playable in a release build
			if (p == base + ".temp.ogg" or p == base + ".stems.json") and _third_party_blocked(base):
				continue
			return true
	return false


## Temps made from imported third-party audio (the AUDIO DIRECTOR's REMIX of an import: covers, samples) carry
## "third_party" in their manifest. They are sketches: a release build never plays them (nor their stems), and
## the project setting audio/block_third_party_temps (default false) blocks them in the editor too, to hear the
## game as it would ship. godot/tools/music_release_check.py lists / strips them before an export.
func _third_party_blocked(base: String) -> bool:
	var block := not OS.is_debug_build() or bool(ProjectSettings.get_setting("audio/block_third_party_temps", false))
	if not block:
		return false
	var man = _manifest(base)
	return man != null and man.has("third_party") and man["third_party"] != null


func _exists(path: String) -> bool:
	var p := "res://" + path
	return ResourceLoader.exists(p) or FileAccess.file_exists(p)


# A track's manifest (<basename>.stems.json) as a Dictionary, or null.
func _manifest(base: String) -> Variant:
	var path := "res://" + base + ".stems.json"
	if not FileAccess.file_exists(path):
		return null
	var man = JSON.parse_string(FileAccess.get_file_as_string(path))
	return man if typeof(man) == TYPE_DICTIONARY else null


# Ogg loop points come from the manifest that names the file (as its mix or a
# stem): loop + loop_offset. Any other Ogg (sfx, voice, a real track with no
# manifest) is left as imported / loaded.
func _apply_ogg_loop(src: String, s: AudioStream) -> void:
	if not (s is AudioStreamOggVorbis):
		return
	var base := src.get_basename()
	if base.get_base_dir().ends_with(".stems"):
		base = base.get_base_dir().get_basename()
	elif base.ends_with(".temp"):
		base = base.get_basename()
	var man = _manifest(base)
	if man == null:
		return
	var named: bool = String(man.get("mix", "")) == src
	var stems = man.get("stems", [])
	if typeof(stems) == TYPE_ARRAY:
		for st in stems:
			if typeof(st) == TYPE_DICTIONARY and String(st.get("file", "")) == src:
				named = true
	if not named:
		return
	var ogg := s as AudioStreamOggVorbis
	ogg.loop = bool(man.get("loop", false))
	ogg.loop_offset = float(man.get("loop_offset", 0.0))


func get_music_intensity() -> float:
	return _intensity


## The stems of the playing track: [{name, layer, gain}] (empty for a stereo track).
func get_music_layers() -> Array:
	var out := []
	for l in _stem_layers:
		out.append({"name": l.name, "layer": l.layer, "gain": _stem_gain[l.index]})
	return out


func _load_stems(src: String) -> AudioStream:
	var base := src.get_basename()
	var man_path := "res://" + base + ".stems.json"
	if not FileAccess.file_exists(man_path):
		return null
	var man = JSON.parse_string(FileAccess.get_file_as_string(man_path))
	if typeof(man) != TYPE_DICTIONARY or not man.has("stems"):
		push_warning("AudioMgr: unreadable stems manifest, playing the mix: " + man_path)
		return null
	# a temp's stems never layer over real audio (the src itself, or a recorded .wav)
	if bool(man.get("temp", false)) and (_exists(src) or _exists(base + ".wav")):
		return null
	if _third_party_blocked(base):
		return null
	var stems: Array = man["stems"]
	if stems.is_empty() or stems.size() > AudioStreamSynchronized.MAX_STREAMS:
		return null
	var sync := AudioStreamSynchronized.new()
	sync.stream_count = stems.size()
	var layers := []
	var gain := PackedFloat32Array()
	for i in stems.size():
		var st: Dictionary = stems[i]
		var sub := _load_audio(String(st.get("file", "")))
		if sub == null:
			push_warning("AudioMgr: stem missing, playing the mix instead: " + String(st.get("file", "")))
			return null
		var layer := float(st.get("layer", 0.0))
		var g := 1.0 if _intensity + 0.0001 >= layer else 0.0
		sync.set_sync_stream(i, sub)
		sync.set_sync_stream_volume(i, linear_to_db(maxf(g, 0.0001)))
		layers.append({"index": i, "layer": layer, "name": String(st.get("name", "stem %d" % i))})
		gain.append(g)
	_stem_stream = sync
	_stem_layers = layers
	_stem_gain = gain
	_stem_target = gain.duplicate()
	return sync


func _clear_stems() -> void:
	_stem_stream = null
	_stem_layers = []
	_stem_gain = PackedFloat32Array()
	_stem_target = PackedFloat32Array()


func _step_stems(delta: float) -> void:
	if _stem_stream == null:
		return
	for i in _stem_gain.size():
		var g := _stem_gain[i]
		var t := _stem_target[i]
		if g == t:
			continue
		g = move_toward(g, t, _stem_rate * delta)
		_stem_gain[i] = g
		_stem_stream.set_sync_stream_volume(i, linear_to_db(maxf(g, 0.0001)))


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


# ── Queue API ─────────────────────────────────────────────────────────────────
# Explicit FIFO queue that GameEngine pushes to whenever a character with
# an associated music track is shown. When BGM finishes naturally, the
# head of the queue plays next. When the queue empties, _pick_next falls
# back to the current chapter's first associated track.

var _queue:          Array = []      # Array[String] of src paths
var _chapter_id:     String = ""     # set by GameEngine on scene load
var _chapter_tracks: Array = []      # Array[String] for empty-queue refill

signal queue_changed
signal track_unlocked(src: String, title: String)


func get_queue() -> Array:
	return _queue.duplicate()


func enqueue_music(src: String) -> bool:
	# Strict dedupe — already queued or currently playing → drop.
	if src == "" or src == _current_src or src in _queue:
		return false
	_queue.append(src)
	queue_changed.emit()
	# If nothing is playing right now, the queue would just sit until
	# some other track finishes — but nothing's going to finish. Kick
	# off the head immediately so character-show actually produces
	# music. Skip while we're mid-fade or have a pending switch; the
	# queue head will be picked up by _pick_next when those settle.
	if not _bgm.playing and not _paused and _pending_src == "" and _fade_timer <= 0.0:
		play_next()
	return true


func clear_queue() -> void:
	if _queue.is_empty():
		return
	_queue.clear()
	queue_changed.emit()


func set_chapter(chapter_id: String, tracks: Array) -> void:
	# GameEngine calls this on every scene load. tracks is the ordered
	# list of catalog srcs that should refill the queue when it empties.
	_chapter_id = chapter_id
	_chapter_tracks = tracks.duplicate()


# Enqueue + unlock all catalog tracks whose "chars" field includes the
# given character key. Called by GameEngine on every "show" directive.
# Returns the number of tracks newly unlocked (0 = nothing new).
func unlock_tracks_for_character(char_key: String) -> int:
	return _unlock_tracks_matching(func(entry: Dictionary) -> bool:
		return char_key != "" and (char_key in entry.get("chars", [])))


# Same shape, but matches a scene/chapter id against the entry's
# `chapters` field. Called from GameEngine when a scene loads —
# the music player picks up the scene's track unlocks even if no
# `show` directive on the page lists a character. Returns count
# newly unlocked.
func unlock_tracks_for_chapter(chapter_id: String) -> int:
	return _unlock_tracks_matching(func(entry: Dictionary) -> bool:
		return chapter_id != "" and (chapter_id in entry.get("chapters", [])))


# Unlocks every track in the given volume (1-22). Called when the
# player picks a volume in the main menu — opening a volume unlocks
# all of its music for the Music Player, with new entries appended
# to the playback queue so progression naturally pulls them in.
# Title theme (vol 0) is always unlocked at boot via MainMenu.
func unlock_volume(vol_n: int) -> int:
	return _unlock_tracks_matching(func(entry: Dictionary) -> bool:
		return int(entry.get("vol", -1)) == vol_n)


# Shared core: iterate the catalog, mark heard + unlocked + enqueue
# every entry that the predicate matches. Returns count newly
# unlocked (first-time only).
func _unlock_tracks_matching(predicate: Callable) -> int:
	var catalog: Array = SceneDataDB.get_music_catalog()
	var newly_unlocked := 0
	for entry: Dictionary in catalog:
		if not predicate.call(entry):
			continue
		var src: String = entry.get("src", "")
		var id:  String = entry.get("id",  "")
		if src == "" or id == "":
			continue
		var key := "music:" + id
		if SaveSystem.mark_unlocked(key):
			newly_unlocked += 1
			# Mark heard at the moment of unlock so MusicPlayerOverlay
			# shows the track with a filled ● dot immediately, even
			# before the queue gets around to playing it. Treats
			# "the character that owns this track has appeared" as
			# equivalent to having heard the track for catalog purposes.
			_mark_heard(src)
			track_unlocked.emit(src, entry.get("title", id))
		# ENQUEUE ONLY WITHIN THE CURRENT VOLUME (2026-09-12). A character
		# carries every entry that names them: Lena is on vol2_ambient
		# (Small Wood Variations) and vol7_apartment_rain, Nicola and
		# Dante on vol4_standoff_strings and vol5_riverboat_drone. While
		# those files did not exist the failed load advanced past them
		# and nobody noticed; now that they do, a `show` of Lena in
		# Smolvud put vol 2's bed at the head of the queue and it played
		# next, over the cabin. The unlock (the Music Player's dot) is
		# still volume-blind; what plays next is not.
		if _entry_in_current_volume(entry):
			enqueue_music(src)
	return newly_unlocked


# The chapter id is "<scene_id>::<chapter>" and scene ids start with
# "vol<N>_"; an entry with no `vol`, or no chapter context, passes.
func _entry_in_current_volume(entry: Dictionary) -> bool:
	if _chapter_id == "" or not entry.has("vol"):
		return true
	var m: RegExMatch = _VOL_RX.search(_chapter_id)
	if m == null:
		return true
	return int(entry.get("vol", -1)) == int(m.get_string(1))


var _VOL_RX: RegEx = RegEx.create_from_string("^vol(\\d+)_")


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


func _start_bgm(src: String, fade: bool = true) -> void:
	var stream: AudioStream = _load_stems(src) if adaptive_music else null
	if stream == null:
		_clear_stems()
		stream = _load_audio(src)
	if not stream:
		# Don't double-log when _load_audio already warned about a
		# fresh failure. Either way, mark the src failed (idempotent)
		# and try to advance the queue past the bad entry — but only
		# if we have somewhere else to go, to avoid runaway recursion
		# if the whole catalog is broken.
		_failed_srcs[src] = true
		var next := _pick_next(src)
		if next != "" and next != src and not (next in _failed_srcs):
			_start_bgm(next)
		return
	# Jukebox rotation only advances when `finished` fires — a stream
	# that loops at the import level would trap the rotation on one
	# track forever. Defeat the loop on a duplicate so the import
	# settings themselves stay untouched.
	if jukebox_on:
		stream = _with_loop(stream, false)
	elif src == _scene_src and _scene_loop:
		stream = _with_loop(stream, true)
	_current_src = src
	_bgm.stream = stream
	# the bus level depends on which track this is (see _bgm_bus_target),
	# and so does the hum's (a signature pushes it down; its end lets it back)
	_retarget_bgm_bus(SIGNATURE_FADE)
	_retarget_ambient_bus(SIGNATURE_FADE)
	if fade:
		_bgm.volume_db = linear_to_db(0.0001)
		_bgm.play()
		_fade_in()
	else:
		_fade_timer = 0.0
		_bgm.volume_db = 0.0
		_bgm.play()
	track_changed.emit(src)


# Returns a duplicate of `stream` with looping forced on/off, for the
# stream types we ship (ogg / mp3 / wav). Anything else is returned
# unchanged.
func _with_loop(stream: AudioStream, loop: bool) -> AudioStream:
	if stream is AudioStreamOggVorbis:
		var ogg := stream.duplicate() as AudioStreamOggVorbis
		ogg.loop = loop
		return ogg
	if stream is AudioStreamMP3:
		var mp3 := stream.duplicate() as AudioStreamMP3
		mp3.loop = loop
		return mp3
	if stream is AudioStreamWAV:
		var wav := stream.duplicate() as AudioStreamWAV
		if loop:
			wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
			wav.loop_begin = 0
			var bytes_per_frame: int = 1
			if wav.format == AudioStreamWAV.FORMAT_16_BITS:
				bytes_per_frame = 2
			if wav.stereo:
				bytes_per_frame *= 2
			@warning_ignore("integer_division")
			wav.loop_end = wav.data.size() / bytes_per_frame
		else:
			wav.loop_mode = AudioStreamWAV.LOOP_DISABLED
		return wav
	return stream


func _fade_in() -> void:
	_fade_from   = 0.0
	_fade_target = 1.0
	_fade_timer  = FADE_DURATION


func _fade_out() -> void:
	_fade_from   = db_to_linear(_bgm.volume_db)
	_fade_target = 0.0
	_fade_timer  = FADE_DURATION


func _on_bgm_finished() -> void:
	# A track that ends DURING a cross-fade must not swallow the queued one:
	# without this the finished track restarted (or the queue advanced) and
	# _pending_src was never played. Found by tests/godot_audiomgr.test.js.
	if _pending_src != "":
		var queued := _pending_src
		_pending_src = ""
		_fade_timer = 0.0
		_start_bgm(queued)
		return
	# Oneshot resume — a play_oneshot_bgm caller asked us to snap
	# back to a specific src when this track ends. Clears as soon
	# as it fires so subsequent finishes use the normal queue/
	# chapter logic.
	if _oneshot_resume_src != "":
		var resume := _oneshot_resume_src
		_oneshot_resume_src = ""
		if resume != "":
			_start_bgm(resume)
			return
	# Scene mode + looping scene bed: belt-and-braces replay in case
	# the stream's own loop flag couldn't be set (unknown type).
	if not jukebox_on and _scene_src != "" and _scene_src == _current_src and _scene_loop:
		_start_bgm(_scene_src, false)
		return
	var next := _pick_next(_current_src)
	_start_bgm(next if next != "" else _current_src)


func _pick_next(current_src: String) -> String:
	# 0) Jukebox mode: rotate the ENTIRE catalog in order, wrapping.
	#    Queue and chapter context are bypassed — the Music Player
	#    owns playback until the user toggles it off.
	if jukebox_on:
		var jcat: Array = SceneDataDB.get_music_catalog()
		if not jcat.is_empty():
			var cur_idx := -1
			for i in jcat.size():
				if String((jcat[i] as Dictionary).get("src", "")) == current_src:
					cur_idx = i
					break
			for step in range(1, jcat.size() + 1):
				var entry: Dictionary = jcat[(cur_idx + step) % jcat.size()]
				var s := String(entry.get("src", ""))
				if s == "" or s in _failed_srcs:
					continue
				# Much of the catalog is registered ahead of its
				# audio — skip file-less entries here so the rotation
				# never has to bounce off a failed load.
				var p := "res://" + s
				if not ResourceLoader.exists(p) and not FileAccess.file_exists(ProjectSettings.globalize_path(p)):
					_failed_srcs[s] = true
					continue
				return s

	# 1) Queue head wins — that's what GameEngine has enqueued via
	#    character shows + scene loads + volume opens.
	if not _queue.is_empty():
		var head: String = _queue.pop_front()
		queue_changed.emit()
		return head

	# 2) Queue empty → refill from the current chapter's tracks. Start
	#    at the first track that isn't what we just played (avoid 1-track
	#    immediate repeat when a chapter has multiple tracks). Falls
	#    through to the very first if all match.
	if not _chapter_tracks.is_empty():
		for src: String in _chapter_tracks:
			if src != current_src:
				return src
		return _chapter_tracks[0]

	# 3) No chapter context → use the player's UNLOCKED PLAYLIST as
	#    the fallback rotation. Every heard/unlocked track in the
	#    catalog is fair game; we pick the first one that isn't what
	#    just played (avoid an immediate repeat) and the playlist
	#    loops naturally as it exhausts. When the player progresses
	#    far enough to hear new tracks, those join the rotation
	#    automatically next time we pick.
	var heard: Array = _heard_playback_order()
	if not heard.is_empty():
		for src: String in heard:
			if src != current_src:
				return src
		return heard[0]

	# 4) Nothing heard yet (very early app start) → loop current.
	return current_src


# Returns all heard tracks in catalog order — the "playlist" that
# AudioMgr.play_next falls through to when no queue/chapter is set.
# Sorted by the catalog's own ordering so the volume progression
# reads naturally.
func _heard_playback_order() -> Array:
	var out: Array = []
	var catalog: Array = SceneDataDB.get_music_catalog()
	for entry: Dictionary in catalog:
		var src: String = String(entry.get("src", ""))
		if src != "" and src in _music_heard:
			out.append(src)
	return out


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


## (2026-10-17) A cue names a file by one extension and the bed was rendered
## in another — the vols 1-4 scenes ask for vol1_club_thump.mp3 and the
## synth wrote vol1_club_thump.wav. Same stem, the first extension that
## exists wins; the name as written when none does.
func _with_existing_extension(src: String) -> String:
	if ResourceLoader.exists("res://" + src) or FileAccess.file_exists("res://" + src):
		return src
	var stem: String = src.get_basename()
	for ext: String in ["ogg", "wav", "mp3"]:
		var alt: String = stem + "." + ext
		if ResourceLoader.exists("res://" + alt) or FileAccess.file_exists("res://" + alt):
			return alt
	return src


func _load_audio(src: String) -> AudioStream:
	# Short-circuit known-bad sources so a corrupt entry in the
	# catalog (or a missing .ogg that still has an .import sidecar)
	# doesn't re-emit decode errors every time the queue lands on it.
	src = src.trim_prefix("res://")
	if src in _failed_srcs:
		return null
	src = _with_existing_extension(src)
	var path := "res://" + src
	if ResourceLoader.exists(path):
		var s := ResourceLoader.load(path) as AudioStream
		if s == null:
			_failed_srcs[src] = true
			push_warning("AudioMgr: failed to load BGM (marking as skip): " + src)
		_apply_ogg_loop(src, s)
		return s
	# Fallback when the .import sidecar isn't generated yet (e.g.
	# audio dropped in but the editor hasn't reimported). Without
	# this, freshly-dropped voicelines silently fail to play.
	var abs_path := ProjectSettings.globalize_path(path)
	if not FileAccess.file_exists(abs_path):
		# Field recordings and tape mixdowns land as a .wav next to the
		# catalog's .ogg / .mp3 path (godot/tools/field_recorder.html,
		# field_ingest.py); temp tracks as <basename>.temp.ogg (the DAW /
		# AUDIO DIRECTOR). Real audio first: the .wav, then the temp.
		var ext0 := src.get_extension().to_lower()
		if not src.ends_with(".temp.ogg"):
			# a .wav src skips only the .wav step (it IS the .wav) — it still
			# falls back to its temp (2026-10-27: twelve locale ambient beds
			# name a .wav whose take exists only as <base>.temp.ogg, and
			# played silence)
			if ext0 != "wav":
				var wav_src := src.get_basename() + ".wav"
				if _exists(wav_src):
					return _load_audio(wav_src)
			var temp_src := src.get_basename() + ".temp.ogg"
			if _exists(temp_src) and not _third_party_blocked(src.get_basename()):
				return _load_audio(temp_src)
		return null
	var bytes := FileAccess.get_file_as_bytes(abs_path)
	if bytes.is_empty():
		return null
	var ext := src.get_extension().to_lower()
	match ext:
		"mp3":
			var s := AudioStreamMP3.new()
			s.data = bytes
			return s
		"ogg":
			var o := AudioStreamOggVorbis.load_from_buffer(bytes)
			if o == null or o.get_length() <= 0.0:
				_failed_srcs[src] = true
				push_warning("AudioMgr: unreadable Ogg (marking as skip): " + src)
				return null
			_apply_ogg_loop(src, o)
			return o
		"wav":
			# load_from_buffer parses the RIFF header (format, rate,
			# channels); assigning .data directly would play the header
			# as audio at the default 8-bit / 44.1 kHz.
			var w := AudioStreamWAV.load_from_buffer(bytes)
			# A truncated / non-WAV file comes back as an empty stream,
			# not null — treat zero length as unreadable too.
			if w == null or w.get_length() <= 0.0:
				w = null
				_failed_srcs[src] = true
				push_warning("AudioMgr: unreadable WAV (marking as skip): " + src)
			return w
	push_warning("AudioMgr: unsupported audio extension '%s' for %s" % [ext, src])
	return null
