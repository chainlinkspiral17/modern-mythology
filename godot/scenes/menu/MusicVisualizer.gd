extends Control
## Music visualizer — drops into MusicPlayerOverlay's reserved host slot.
##
## Six unlock-gated modes, each with its own _draw() pass. Audio is
## sampled either via the BGM bus's peak meter (cheap, always available)
## or via an AudioEffectSpectrumAnalyzer attached on first use.
##
## The visualizer is mode-driven: switch `mode` and the same Control
## renders a different visualization. This avoids a node-per-mode tree
## while keeping the modes textually separate in _draw().

const BUS_NAME := "BGM"
const MIN_DB := -60.0          # silence floor
const FREQ_BINS := 16          # spectrum-bars bin count
const FREQ_LO := 60.0          # spectrum low end (Hz)
const FREQ_HI := 8000.0        # spectrum high end (Hz)
const LOW_BAND_HZ := [60.0, 250.0]    # for low-band-energy modes

# ── Visualizer table — id, display name, unlock clause. Mirrors the
#    skin table's unlock shape so the player overlay can reuse the
#    same MenuButton flow.
const VIZ := [
	{
		"id": "peak_meter",
		"name": "Peak Meter",
		"unlock": {},
	},
	{
		"id": "vu_needle",
		"name": "VU Needle",
		"unlock": {"type": "heard_count", "min": 5},
	},
	{
		"id": "spectrum_bars",
		"name": "Spectrum Bars",
		"unlock": {"type": "heard_count", "min": 15},
	},
	{
		"id": "cassette_reels",
		"name": "Cassette Reels",
		"unlock": {"type": "heard", "src": "assets/audio/bgm/vol5_elicia_theme_solo.ogg"},
	},
	{
		"id": "cathedral_drift",
		"name": "Cathedral Drift",
		"unlock": {"type": "key", "key": "milestone:gauntlet_win"},
	},
	{
		"id": "steamboat_wheel",
		"name": "Steamboat Wheel",
		"unlock": {"type": "key", "key": "milestone:candles_lit"},
	},
]

var mode: String = "peak_meter"
var accent: Color = Color(0.78, 0.66, 0.29)
var dim:    Color = Color(0.45, 0.43, 0.36, 0.6)
var txt:    Color = Color(0.83, 0.79, 0.69)

# Latest sampled signal values, written every _process(dt).
var _peak_l: float = 0.0          # 0..1
var _peak_r: float = 0.0          # 0..1
var _low_energy: float = 0.0      # 0..1, smoothed
var _bands: PackedFloat32Array = PackedFloat32Array()   # FREQ_BINS magnitudes 0..1
var _phase: float = 0.0           # cumulative time for rotation modes

# Particle pool for cathedral_drift — initialized lazily.
var _particles: Array = []
const PARTICLE_COUNT := 28


func _ready() -> void:
	_bands.resize(FREQ_BINS)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_process(true)


# ── Public API ───────────────────────────────────────────────────────
func set_mode(m: String) -> void:
	mode = m
	queue_redraw()


func set_colors(p_accent: Color, p_dim: Color, p_txt: Color) -> void:
	accent = p_accent
	dim    = p_dim
	txt    = p_txt
	queue_redraw()


# ── Unlock resolution (used by the dropdown to filter modes) ─────────
static func viz_unlocked(v: Dictionary) -> bool:
	var u: Dictionary = v.get("unlock", {})
	var t: String = String(u.get("type", ""))
	if t == "":
		return true
	if t == "key":
		return SaveSystem.is_unlocked(String(u.get("key", "")))
	if t == "heard":
		return AudioMgr.is_heard(String(u.get("src", "")))
	if t == "heard_count":
		return AudioMgr.get_heard_set().size() >= int(u.get("min", 0))
	return false


# ── Sampling ─────────────────────────────────────────────────────────
func _process(dt: float) -> void:
	_phase += dt
	var bus_idx: int = AudioServer.get_bus_index(BUS_NAME)
	if bus_idx == -1:
		_peak_l = 0.0
		_peak_r = 0.0
	else:
		_peak_l = _db_to_unit(AudioServer.get_bus_peak_volume_left_db(bus_idx, 0))
		_peak_r = _db_to_unit(AudioServer.get_bus_peak_volume_right_db(bus_idx, 0))

	# Spectrum — only sample when a mode that needs it is active.
	if mode in ["spectrum_bars", "cathedral_drift", "steamboat_wheel"]:
		var inst := _spectrum_instance()
		if inst != null:
			# Logarithmic bin distribution feels better than linear for
			# music — low end is dense, high end stretches.
			var lo_log: float = log(FREQ_LO) / log(10.0)
			var hi_log: float = log(FREQ_HI) / log(10.0)
			for i in FREQ_BINS:
				var a: float = lerpf(lo_log, hi_log, float(i)     / float(FREQ_BINS))
				var b: float = lerpf(lo_log, hi_log, float(i + 1) / float(FREQ_BINS))
				var lo: float = pow(10.0, a)
				var hi: float = pow(10.0, b)
				var mag: float = inst.get_magnitude_for_frequency_range(lo, hi).length()
				# Smooth toward target so bars/particles don't strobe.
				var prev: float = _bands[i]
				_bands[i] = lerpf(prev, clampf(mag * 6.0, 0.0, 1.0), 0.30)
			# Low-band convenience
			var low: float = inst.get_magnitude_for_frequency_range(LOW_BAND_HZ[0], LOW_BAND_HZ[1]).length()
			_low_energy = lerpf(_low_energy, clampf(low * 6.0, 0.0, 1.0), 0.30)
		else:
			_low_energy = lerpf(_low_energy, 0.0, 0.10)
	queue_redraw()


# Convert a peak dB reading (negative; -60..0) into a unit 0..1.
func _db_to_unit(v_db: float) -> float:
	if is_inf(v_db) or is_nan(v_db):
		return 0.0
	var t: float = (v_db - MIN_DB) / -MIN_DB    # MIN_DB is negative
	return clampf(t, 0.0, 1.0)


# Locate the spectrum analyzer instance on the BGM bus, attaching one
# on first call. Returns null if the bus doesn't exist.
func _spectrum_instance() -> AudioEffectSpectrumAnalyzerInstance:
	var bus_idx: int = AudioServer.get_bus_index(BUS_NAME)
	if bus_idx == -1:
		return null
	# Search existing effects.
	var n: int = AudioServer.get_bus_effect_count(bus_idx)
	for i in n:
		var fx := AudioServer.get_bus_effect(bus_idx, i)
		if fx is AudioEffectSpectrumAnalyzer:
			return AudioServer.get_bus_effect_instance(bus_idx, i) as AudioEffectSpectrumAnalyzerInstance
	# Attach one.
	var analyzer := AudioEffectSpectrumAnalyzer.new()
	analyzer.buffer_length = 0.1
	analyzer.fft_size = AudioEffectSpectrumAnalyzer.FFT_SIZE_1024
	AudioServer.add_bus_effect(bus_idx, analyzer)
	var new_idx: int = AudioServer.get_bus_effect_count(bus_idx) - 1
	return AudioServer.get_bus_effect_instance(bus_idx, new_idx) as AudioEffectSpectrumAnalyzerInstance


# ── Drawing ──────────────────────────────────────────────────────────
func _draw() -> void:
	var s: Vector2 = size
	if s.x <= 0 or s.y <= 0:
		return
	match mode:
		"peak_meter":      _draw_peak_meter(s)
		"vu_needle":       _draw_vu_needle(s)
		"spectrum_bars":   _draw_spectrum_bars(s)
		"cassette_reels":  _draw_cassette_reels(s)
		"cathedral_drift": _draw_cathedral_drift(s)
		"steamboat_wheel": _draw_steamboat_wheel(s)
		_:                 _draw_peak_meter(s)


# Two horizontal bars, L over R, animating to peak.
func _draw_peak_meter(s: Vector2) -> void:
	var bar_h: float = 8.0
	var gap: float = 6.0
	var w: float = s.x
	var y_l: float = s.y * 0.5 - bar_h - gap * 0.5
	var y_r: float = s.y * 0.5 + gap * 0.5
	# Backing
	draw_rect(Rect2(0, y_l, w, bar_h), Color(dim.r, dim.g, dim.b, 0.18), true)
	draw_rect(Rect2(0, y_r, w, bar_h), Color(dim.r, dim.g, dim.b, 0.18), true)
	# Levels
	draw_rect(Rect2(0, y_l, w * _peak_l, bar_h), accent, true)
	draw_rect(Rect2(0, y_r, w * _peak_r, bar_h), accent, true)
	# Tick marks at quarter intervals
	for i in range(1, 4):
		var x: float = w * (float(i) / 4.0)
		draw_line(Vector2(x, y_l - 2), Vector2(x, y_l + bar_h + 2), Color(accent.r, accent.g, accent.b, 0.35), 1.0)


# Single needle sweeping 0..180° based on peak.
func _draw_vu_needle(s: Vector2) -> void:
	var c: Vector2 = Vector2(s.x * 0.5, s.y * 0.95)
	var r: float = s.y * 0.85
	# Arc backing
	draw_arc(c, r, PI, TAU, 64, Color(dim.r, dim.g, dim.b, 0.35), 2.0, false)
	# Tick marks
	for i in range(0, 11):
		var t: float = float(i) / 10.0
		var ang: float = lerpf(PI, TAU, t)
		var p1: Vector2 = c + Vector2(cos(ang), sin(ang)) * (r - 6)
		var p2: Vector2 = c + Vector2(cos(ang), sin(ang)) * r
		var col: Color = accent if t > 0.7 else Color(accent.r, accent.g, accent.b, 0.6)
		draw_line(p1, p2, col, 1.0)
	# Needle — peak of L/R, with a tiny lag so it feels mechanical.
	var pk: float = maxf(_peak_l, _peak_r)
	var ang2: float = lerpf(PI, TAU, pk)
	var tip: Vector2 = c + Vector2(cos(ang2), sin(ang2)) * (r - 8)
	draw_line(c, tip, accent, 2.0)
	draw_circle(c, 4.0, accent)


# 16 vertical bars driven by FFT.
func _draw_spectrum_bars(s: Vector2) -> void:
	var n: int = _bands.size()
	var gap: float = 3.0
	var w: float = (s.x - gap * float(n - 1)) / float(n)
	var floor_y: float = s.y - 4
	for i in n:
		var h: float = _bands[i] * (s.y - 12)
		var x: float = float(i) * (w + gap)
		var y: float = floor_y - h
		draw_rect(Rect2(x, y, w, h), accent, true)
		# 1px backing line at the floor
		draw_line(Vector2(x, floor_y + 1), Vector2(x + w, floor_y + 1), Color(dim.r, dim.g, dim.b, 0.4), 1.0)


# Two cassette hubs rotating to amplitude. The faster the music
# (proxied by peak), the faster the reels spin.
func _draw_cassette_reels(s: Vector2) -> void:
	var hub_r: float = minf(s.y * 0.45, 28.0)
	var cy: float = s.y * 0.5
	var c_l: Vector2 = Vector2(s.x * 0.30, cy)
	var c_r: Vector2 = Vector2(s.x * 0.70, cy)
	# Background hubs
	for c in [c_l, c_r]:
		draw_circle(c, hub_r, Color(dim.r, dim.g, dim.b, 0.18))
		draw_arc(c, hub_r, 0.0, TAU, 48, Color(accent.r, accent.g, accent.b, 0.5), 1.5, false)
	# Spoke phase — left and right rotate at slightly different rates.
	var rot_l: float = _phase * (0.6 + _peak_l * 3.0)
	var rot_r: float = _phase * (0.6 + _peak_r * 3.0)
	for c_and_rot in [[c_l, rot_l], [c_r, rot_r]]:
		var c: Vector2 = c_and_rot[0]
		var rot: float = c_and_rot[1]
		for k in 6:
			var a: float = rot + float(k) * PI / 3.0
			var p1: Vector2 = c + Vector2(cos(a), sin(a)) * (hub_r * 0.25)
			var p2: Vector2 = c + Vector2(cos(a), sin(a)) * (hub_r * 0.90)
			draw_line(p1, p2, accent, 1.5)
		draw_circle(c, hub_r * 0.18, Color(accent.r, accent.g, accent.b, 0.7))


# Drifting rust-particle field. Particles get a vertical kick from
# the low-band energy; otherwise they drift sideways slowly.
func _draw_cathedral_drift(s: Vector2) -> void:
	if _particles.is_empty():
		_init_particles(s)
	# Step + draw
	for p in _particles:
		p.x += p.vx
		p.y += p.vy
		# Low-band gives an upward push (rust rising)
		p.vy -= _low_energy * 0.30
		# Gravity-ish recover
		p.vy = lerpf(p.vy, 0.06, 0.04)
		# Wrap
		if p.x < -4: p.x = s.x + 4
		if p.x > s.x + 4: p.x = -4
		if p.y < -4: p.y = s.y + 4
		if p.y > s.y + 4: p.y = -4
		var a: float = 0.4 + 0.6 * _low_energy
		draw_circle(Vector2(p.x, p.y), p.r, Color(accent.r, accent.g, accent.b, a))


func _init_particles(s: Vector2) -> void:
	_particles.clear()
	var rng := RandomNumberGenerator.new()
	rng.seed = 0xCA7HEDRAL
	for _i in PARTICLE_COUNT:
		_particles.append({
			"x":  rng.randf_range(0, s.x),
			"y":  rng.randf_range(0, s.y),
			"vx": rng.randf_range(-0.20, 0.20),
			"vy": rng.randf_range(0.04, 0.18),
			"r":  rng.randf_range(0.8, 2.4),
		})


# A paddle wheel rotating; bass kicks scale the splash arc.
func _draw_steamboat_wheel(s: Vector2) -> void:
	var c: Vector2 = Vector2(s.x * 0.5, s.y * 0.55)
	var r: float = minf(s.y * 0.45, 28.0)
	var rot: float = _phase * (0.4 + _low_energy * 2.5)
	# Hub outline
	draw_arc(c, r, 0.0, TAU, 64, Color(accent.r, accent.g, accent.b, 0.55), 1.5, false)
	# 8 paddle blades
	for k in 8:
		var a: float = rot + float(k) * PI / 4.0
		var p1: Vector2 = c + Vector2(cos(a), sin(a)) * (r * 0.20)
		var p2: Vector2 = c + Vector2(cos(a), sin(a)) * r
		draw_line(p1, p2, accent, 2.0)
	# Splash arc — only the lower hemisphere, modulated by low-band.
	var splash_r: float = r + 4 + _low_energy * 10
	var splash_alpha: float = 0.25 + 0.55 * _low_energy
	draw_arc(c, splash_r, 0.0, PI, 24, Color(accent.r, accent.g, accent.b, splash_alpha), 1.5, false)
	# Waterline tick
	draw_line(Vector2(0, c.y + r + 2), Vector2(s.x, c.y + r + 2), Color(dim.r, dim.g, dim.b, 0.45), 1.0)
