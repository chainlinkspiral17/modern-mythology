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
		enqueue_music(src)
	return newly_unlocked


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
	var next := _pick_next(_current_src)
	_start_bgm(next if next != "" else _current_src)


func _pick_next(current_src: String) -> String:
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


func _load_audio(src: String) -> AudioStream:
	# Short-circuit known-bad sources so a corrupt entry in the
	# catalog (or a missing .ogg that still has an .import sidecar)
	# doesn't re-emit decode errors every time the queue lands on it.
	if src in _failed_srcs:
		return null
	var path := "res://" + src
	if ResourceLoader.exists(path):
		var s := ResourceLoader.load(path) as AudioStream
		if s == null:
			_failed_srcs[src] = true
			push_warning("AudioMgr: failed to load BGM (marking as skip): " + src)
		return s
	# Fallback when the .import sidecar isn't generated yet (e.g.
	# audio dropped in but the editor hasn't reimported). Without
	# this, freshly-dropped voicelines silently fail to play.
	var abs_path := ProjectSettings.globalize_path(path)
	if not FileAccess.file_exists(abs_path):
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
			return AudioStreamOggVorbis.load_from_buffer(bytes)
		"wav":
			var w := AudioStreamWAV.new()
			w.data = bytes
			return w
	push_warning("AudioMgr: unsupported audio extension '%s' for %s" % [ext, src])
	return null
