# TripSync.gd · AUTOLOAD
# ════════════════════════════════════════════════════════════════
# THE TRIP · the project-wide psychedelic layer, synced to the music.
#
# "Realism but trippy — I always wanted this running through the
# game at all times, in lines and backgrounds, synced to the music
# currently playing."  (2026-09-07)
#
# One node does three jobs:
#
#   1. LISTEN   · reads the BGM bus spectrum analyzer (AudioMgr owns
#                 one on the BGM bus; we attach one if it is missing)
#                 into eight log-spaced bands with an adaptive gain,
#                 so a quiet drone drives the picture as hard as a
#                 loud track. Detects beats on the low band (onset
#                 over a running average), keeps a tempo estimate
#                 from the median inter-beat interval, and runs the
#                 tempo-locked beat / bar phases the shader uses.
#   2. PAINT    · owns a global layer-60 CanvasLayer (above every
#                 scene's PostProcess stack at 50, below HUD at 100,
#                 below the slowstick look at 80) with one full-rect
#                 ColorRect running trip_sync.gdshader in screen
#                 mode. It is the PICTURE, not HUD: group
#                 "world_render", never "ui", name carries none of
#                 the F4 sweep's HUD substrings.
#   3. DELEGATE · surfaces that must keep their text clean (the VN)
#                 join the "trip_local" group and call attach() on
#                 their background CanvasItems; the same shader runs
#                 in texture mode on those and the global layer hides
#                 while any trip_local node is in the tree.
#
# Every attached material — global and local — receives the same
# music state each frame, so a VN background and a locale walk
# breathe to the same beat.
#
# Dial: Settings.trip_amount (0..1, PSYCHEDELIA in the settings
# overlay). 0 = the layer is an identity and hides itself.
# ════════════════════════════════════════════════════════════════
extends Node

const SHADER_PATH: String = "res://assets/shaders/trip_sync.gdshader"
const LAYER_ORDER: int = 60
const BUS_NAME: String = "BGM"
const BANDS: int = 8
const FREQ_LO: float = 40.0
const FREQ_HI: float = 9000.0

# Beat detector
const BEAT_MIN_GAP: float = 0.22        # s · no two beats closer than this (~270 bpm)
const BEAT_RATIO: float = 1.32          # onset must clear the running average by this
const BEAT_FLOOR: float = 0.07          # ... plus this absolute margin (normalised units)
const INTERVAL_LO: float = 0.28         # s · accepted inter-beat range (215..46 bpm)
const INTERVAL_HI: float = 1.30
const INTERVALS_KEPT: int = 8
const PULSE_DECAY: float = 5.0          # exp decay rate of the beat envelope
const SILENCE_RAW: float = 0.0035       # raw analyzer sum below this = no music
const SILENCE_HOLD: float = 1.5         # s of quiet before the idle breath takes over

var _shader: Shader = null
var _global_layer: CanvasLayer = null
var _global_rect: ColorRect = null
var _materials: Array[ShaderMaterial] = []
var _analyzer: AudioEffectSpectrumAnalyzerInstance = null

# Music state (public read for anything else that wants to dance)
var amount: float = 0.6
var energy: float = 0.0
var bass: float = 0.0
var mid: float = 0.0
var high: float = 0.0
var pulse: float = 0.0
var ring_t: float = 10.0
var beat_phase: float = 0.0
var bar_phase: float = 0.0
var hue_base: float = 0.0
var t_flow: float = 0.0
var bpm: float = 120.0
var music_present: bool = false
# Multipliers on `amount` (draft 1B). mood_scale is pushed by
# MoodCycler._apply — edge/ascii-heavy moods (neon 1.0, ascii ≥ 0.5)
# are already a stylization and the trip is dialled to 0.35 under
# them unless the preset carries its own "trip_scale". surface_scale
# is 0.45 while any node sits in "trip_soft" (the main menu — text-
# heavy surfaces the global layer still covers).
var mood_scale: float = 1.0
var surface_scale: float = 1.0
const SOFT_SURFACE_SCALE: float = 0.45

var _bands: PackedFloat32Array = PackedFloat32Array()
var _band_lo: PackedFloat32Array = PackedFloat32Array()
var _band_hi: PackedFloat32Array = PackedFloat32Array()
var _peak_track: float = 0.05           # slow-tracking loudness ceiling for the auto-gain
var _bass_avg: float = 0.0
var _last_beat_at: float = -10.0
var _beat_interval: float = 0.5
var _intervals: Array[float] = []
var _silence_t: float = 0.0
var _clock: float = 0.0
var _ring_c: Vector2 = Vector2(0.5, 0.5)
var _ring_target: Vector2 = Vector2(0.5, 0.5)
var _rng: RandomNumberGenerator = RandomNumberGenerator.new()


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_rng.seed = 0x7121F
	_bands.resize(BANDS)
	_band_lo.resize(BANDS)
	_band_hi.resize(BANDS)
	var lo_log: float = log(FREQ_LO) / log(10.0)
	var hi_log: float = log(FREQ_HI) / log(10.0)
	for i in range(BANDS):
		_band_lo[i] = pow(10.0, lerpf(lo_log, hi_log, float(i) / float(BANDS)))
		_band_hi[i] = pow(10.0, lerpf(lo_log, hi_log, float(i + 1) / float(BANDS)))
	_shader = load(SHADER_PATH) as Shader
	if _shader == null:
		push_warning("[TripSync] shader missing at %s — layer disabled" % SHADER_PATH)
		return
	amount = clampf(Settings.trip_amount, 0.0, 1.0)
	Settings.settings_changed.connect(_on_setting)
	_spawn_global_layer()
	print("[TripSync] on · amount %.2f · layer %d · PSYCHEDELIA slider in settings" % [amount, LAYER_ORDER])


func _on_setting(key: String, value: Variant) -> void:
	if key == "trip_amount":
		amount = clampf(float(value), 0.0, 1.0)


# ── Layer ─────────────────────────────────────────────────────────
func _spawn_global_layer() -> void:
	_global_layer = CanvasLayer.new()
	_global_layer.name = "TripSync"
	_global_layer.layer = LAYER_ORDER
	_global_layer.add_to_group("world_render")   # the picture, not HUD — F4 leaves it
	add_child(_global_layer)
	_global_rect = ColorRect.new()
	_global_rect.name = "TripRect"
	_global_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_global_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE   # never eat input
	var mat: ShaderMaterial = ShaderMaterial.new()
	mat.shader = _shader
	mat.set_shader_parameter("use_screen", true)
	_global_rect.material = mat
	_global_layer.add_child(_global_rect)
	_materials.append(mat)


# Run the trip on a CanvasItem's own texture (a TextureRect or a
# SubViewportContainer) instead of the screen. The caller's root
# should also join "trip_local" so the global layer steps aside.
func attach(item: CanvasItem) -> ShaderMaterial:
	if _shader == null or item == null:
		return null
	var existing: Material = item.material
	if existing is ShaderMaterial and (existing as ShaderMaterial).shader == _shader:
		return existing as ShaderMaterial
	var mat: ShaderMaterial = ShaderMaterial.new()
	mat.shader = _shader
	mat.set_shader_parameter("use_screen", false)
	item.material = mat
	_materials.append(mat)
	item.tree_exiting.connect(func() -> void: _materials.erase(mat))
	_push_to(mat)
	return mat


func detach(item: CanvasItem) -> void:
	if item == null:
		return
	var existing: Material = item.material
	if existing is ShaderMaterial and (existing as ShaderMaterial).shader == _shader:
		_materials.erase(existing as ShaderMaterial)
		item.material = null


# ── Listen ────────────────────────────────────────────────────────
func _find_analyzer() -> AudioEffectSpectrumAnalyzerInstance:
	if _analyzer != null:
		return _analyzer
	var bus_idx: int = AudioServer.get_bus_index(BUS_NAME)
	if bus_idx == -1:
		return null
	for i in range(AudioServer.get_bus_effect_count(bus_idx)):
		if AudioServer.get_bus_effect(bus_idx, i) is AudioEffectSpectrumAnalyzer:
			_analyzer = AudioServer.get_bus_effect_instance(bus_idx, i) as AudioEffectSpectrumAnalyzerInstance
			return _analyzer
	var spec: AudioEffectSpectrumAnalyzer = AudioEffectSpectrumAnalyzer.new()
	spec.fft_size = AudioEffectSpectrumAnalyzer.FFT_SIZE_2048
	AudioServer.add_bus_effect(bus_idx, spec)
	var new_idx: int = AudioServer.get_bus_effect_count(bus_idx) - 1
	_analyzer = AudioServer.get_bus_effect_instance(bus_idx, new_idx) as AudioEffectSpectrumAnalyzerInstance
	return _analyzer


func _process(delta: float) -> void:
	if _shader == null:
		return
	_clock += delta
	var dt: float = minf(delta, 0.1)

	# ── bands · raw magnitudes → adaptive gain → asymmetric smoothing
	var raw_sum: float = 0.0
	var raw: PackedFloat32Array = PackedFloat32Array()
	raw.resize(BANDS)
	var inst: AudioEffectSpectrumAnalyzerInstance = _find_analyzer()
	if inst != null:
		for i in range(BANDS):
			var m: float = inst.get_magnitude_for_frequency_range(_band_lo[i], _band_hi[i]).length()
			# the high bands carry far less amplitude than the lows; tilt them up
			m *= 1.0 + 0.55 * float(i)
			raw[i] = m
			raw_sum += m
	if raw_sum < SILENCE_RAW:
		_silence_t += dt
	else:
		_silence_t = 0.0
	music_present = _silence_t < SILENCE_HOLD

	# auto-gain: the ceiling follows the loudest recent moment and sinks slowly
	_peak_track = maxf(_peak_track * (1.0 - 0.10 * dt), raw_sum * 0.5)
	_peak_track = maxf(_peak_track, 0.02)
	var gain: float = 1.0 / _peak_track
	for i in range(BANDS):
		var target: float = clampf(raw[i] * gain * 2.6, 0.0, 1.0)
		var prev: float = _bands[i]
		var k: float = 0.55 if target > prev else 0.14
		_bands[i] = lerpf(prev, target, k)

	var bass_now: float = clampf((raw[0] + raw[1]) * gain * 1.4, 0.0, 1.5)
	var t_bass: float = (_bands[0] + _bands[1]) * 0.5
	var t_mid: float = (_bands[2] + _bands[3] + _bands[4]) / 3.0
	var t_high: float = (_bands[5] + _bands[6] + _bands[7]) / 3.0
	var t_energy: float = clampf(t_bass * 0.45 + t_mid * 0.35 + t_high * 0.20, 0.0, 1.0)

	if not music_present:
		# Idle breath: no music, the picture still lives, gently.
		var lfo: float = 0.5 + 0.5 * sin(_clock * 0.45)
		t_energy = 0.14 + 0.10 * lfo
		t_bass = 0.10 + 0.08 * lfo
		t_mid = 0.10
		t_high = 0.06
		bass_now = 0.0
		_bass_avg = 0.0
	bass = lerpf(bass, t_bass, 0.25)
	mid = lerpf(mid, t_mid, 0.25)
	high = lerpf(high, t_high, 0.25)
	energy = lerpf(energy, t_energy, 0.18)

	# ── beats · onset on the low band over its ~1 s running average
	_bass_avg = lerpf(_bass_avg, bass_now, clampf(dt * 1.6, 0.0, 1.0))
	if music_present and bass_now > _bass_avg * BEAT_RATIO + BEAT_FLOOR and _clock - _last_beat_at > BEAT_MIN_GAP:
		var interval: float = _clock - _last_beat_at
		_last_beat_at = _clock
		if interval > INTERVAL_LO and interval < INTERVAL_HI:
			_intervals.append(interval)
			while _intervals.size() > INTERVALS_KEPT:
				_intervals.pop_front()
			var sorted: Array[float] = []
			sorted.assign(_intervals)
			sorted.sort()
			_beat_interval = sorted[sorted.size() >> 1]
			bpm = 60.0 / _beat_interval
		pulse = 1.0
		ring_t = 0.0
		beat_phase = 0.0
		_ring_target = Vector2(0.5 + _rng.randf_range(-0.22, 0.22), 0.5 + _rng.randf_range(-0.16, 0.16))

	# ── clocks
	pulse *= exp(-dt * PULSE_DECAY)
	ring_t += dt
	beat_phase = fposmod(beat_phase + dt / _beat_interval, 1.0)
	bar_phase = fposmod(bar_phase + dt / (_beat_interval * 4.0), 1.0)
	hue_base = fposmod(hue_base + dt * (0.008 + 0.045 * energy), 1.0)
	t_flow += dt * (0.30 + 0.90 * energy + 0.60 * pulse)
	_ring_c = _ring_c.lerp(_ring_target, clampf(dt * 2.5, 0.0, 1.0))

	# ── paint · the global layer steps aside for trip_local surfaces
	var local_active: bool = not get_tree().get_nodes_in_group("trip_local").is_empty()
	var soft_active: bool = not get_tree().get_nodes_in_group("trip_soft").is_empty()
	surface_scale = SOFT_SURFACE_SCALE if soft_active else 1.0
	if _global_layer != null:
		_global_layer.visible = effective_amount() > 0.001 and not local_active
	for mat in _materials:
		_push_to(mat)


func _push_to(mat: ShaderMaterial) -> void:
	if mat == null:
		return
	mat.set_shader_parameter("amount", effective_amount())
	mat.set_shader_parameter("energy", energy)
	mat.set_shader_parameter("bass", bass)
	mat.set_shader_parameter("mid", mid)
	mat.set_shader_parameter("high", high)
	mat.set_shader_parameter("pulse", pulse)
	mat.set_shader_parameter("ring_t", ring_t)
	mat.set_shader_parameter("beat_phase", beat_phase)
	mat.set_shader_parameter("bar_phase", bar_phase)
	mat.set_shader_parameter("hue_base", hue_base)
	mat.set_shader_parameter("t_flow", t_flow)
	mat.set_shader_parameter("ring_cx", _ring_c.x)
	mat.set_shader_parameter("ring_cy", _ring_c.y)


# ── Public helpers ────────────────────────────────────────────────
func effective_amount() -> float:
	return clampf(amount * mood_scale * surface_scale, 0.0, 1.0)


func set_amount(v: float) -> void:
	Settings.trip_amount = clampf(v, 0.0, 1.0)


# MoodCycler._apply pushes this on every mood change.
func set_mood_scale(v: float) -> void:
	mood_scale = clampf(v, 0.0, 1.0)


func status_line() -> String:
	return "TRIP %d%% (dial %d%% · mood ×%.2f · surface ×%.2f) · %s · %.0f bpm · e%.2f b%.2f p%.2f" % [
		int(effective_amount() * 100.0), int(amount * 100.0), mood_scale, surface_scale,
		"music" if music_present else "idle", bpm, energy, bass, pulse]
