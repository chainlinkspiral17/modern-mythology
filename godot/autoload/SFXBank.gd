extends Node
## SFXBank · autoloaded as "SFXBank".
##
## Named-preset SFX playback. A companion to AudioMgr's single-slot
## `play_sfx()` that supports OVERLAPPING short SFX (e.g. tile hover +
## verb select + turn tick all firing within the same second). Uses
## a small pool of AudioStreamPlayer nodes cycled round-robin.
##
## Preset names map to files under `res://assets/audio/sfx/e3/`
## rendered by godot/tools/audio/slowstick_synth.py. Missing files
## print a push_warning once and silently no-op thereafter.
##
## Usage:
##
##     SFXBank.play("verb_select")
##     SFXBank.play("cartridge_click", 0.6)   # 0.6 volume ratio
##
## The bank respects Settings.sfx_vol (if the autoload is present).

const SFX_E3_ROOT := "res://assets/audio/sfx/e3/"
const SFX_CP_ROOT := "res://assets/audio/sfx/cp/"
const POOL_SIZE := 8

# Preset → (root, filename). Kept explicit so the audit doc doubles
# as the registry. Wave A lives under e3/; Wave C under cp/.
const PRESET_MAP := {
	# Original SFX set + Wave A · UI (all under e3/)
	"coin":               ["e3", "coin.wav"],
	"hurt":               ["e3", "hurt.wav"],
	"jump":               ["e3", "jump.wav"],
	"blip":               ["e3", "blip.wav"],
	"pickup":             ["e3", "pickup.wav"],
	"door_open":          ["e3", "door_open.wav"],
	"register_ding":      ["e3", "register_ding.wav"],
	"phone_ring":         ["e3", "phone_ring.wav"],
	"broom_sweep":        ["e3", "broom_sweep.wav"],
	"cooler_whoosh":      ["e3", "cooler_whoosh.wav"],
	"fluorescent_start":  ["e3", "fluorescent_start.wav"],
	"tide_pool_splash":   ["e3", "tide_pool_splash.wav"],
	"stick_scratch":      ["e3", "stick_scratch.wav"],
	"verb_select":        ["e3", "verb_select.wav"],
	"turn_tick":          ["e3", "turn_tick.wav"],
	"customer_bell":      ["e3", "customer_bell.wav"],
	"control_click":      ["e3", "control_click.wav"],
	"season_settle":      ["e3", "season_settle.wav"],
	"tile_hover":         ["e3", "tile_hover.wav"],
	"tile_enter":         ["e3", "tile_enter.wav"],
	"press_hit":          ["e3", "press_hit.wav"],
	"press_miss":         ["e3", "press_miss.wav"],
	"cartridge_hover":    ["e3", "cartridge_hover.wav"],
	"cartridge_click":    ["e3", "cartridge_click.wav"],
	"boot":               ["e3", "boot.wav"],
	# Wave C · CP demon-depth
	"tier_crossing_hungry":   ["cp", "tier_crossing_hungry.wav"],
	"tier_crossing_restless": ["cp", "tier_crossing_restless.wav"],
	"tier_crossing_close":    ["cp", "tier_crossing_close.wav"],
	"tier_crossing_turned":   ["cp", "tier_crossing_turned.wav"],
	"basement_rite":          ["cp", "basement_rite.wav"],
	"pair_warm":              ["cp", "pair_warm.wav"],
	"pair_loud":              ["cp", "pair_loud.wav"],
	"pair_cold":              ["cp", "pair_cold.wav"],
	"marker_set":             ["cp", "marker_set.wav"],
	"marker_expire":          ["cp", "marker_expire.wav"],
	"quiet_week":             ["cp", "quiet_week.wav"],
	"roster_loud":            ["cp", "roster_loud.wav"],
	"interlude_earned":       ["cp", "interlude_earned.wav"],
	"labor_day_arrival":      ["cp", "labor_day_arrival.wav"],
}


func _preset_path(preset: String) -> String:
	var entry: Array = PRESET_MAP[preset]
	var root: String = SFX_CP_ROOT if String(entry[0]) == "cp" else SFX_E3_ROOT
	return root + String(entry[1])

var _pool: Array = []           # AudioStreamPlayer[]
var _next_pool_idx: int = 0
var _cache: Dictionary = {}     # preset → AudioStream (loaded once, reused)
var _missing_warned: Dictionary = {}   # preset → true (warn once)


func _ready() -> void:
	# Build the pool.
	for i in range(POOL_SIZE):
		var p := AudioStreamPlayer.new()
		p.bus = "SFX"
		add_child(p)
		_pool.append(p)


func play(preset: String, volume_ratio: float = 1.0) -> void:
	if not PRESET_MAP.has(preset):
		if not _missing_warned.get(preset, false):
			_missing_warned[preset] = true
			push_warning("[SFXBank] unknown preset: %s" % preset)
		return
	var stream: AudioStream = _load_stream(preset)
	if stream == null:
		return
	var p: AudioStreamPlayer = _pool[_next_pool_idx]
	_next_pool_idx = (_next_pool_idx + 1) % POOL_SIZE
	p.stream = stream
	# Compose volume from settings * clamped ratio. Settings uses
	# 0..1 linear; convert to dB (rough).
	var settings := get_node_or_null("/root/Settings")
	var settings_vol: float = 1.0
	if settings != null and settings.get("sfx_vol") != null:
		settings_vol = float(settings.get("sfx_vol"))
	var effective := max(0.0, settings_vol * volume_ratio)
	if effective <= 0.0:
		return
	p.volume_db = linear_to_db(effective)
	p.play()


func has_preset(preset: String) -> bool:
	return PRESET_MAP.has(preset)


func stop_all() -> void:
	for p in _pool:
		var pp: AudioStreamPlayer = p
		if pp.playing:
			pp.stop()


# ─── internal ────────────────────────────────────────────────────

func _load_stream(preset: String) -> AudioStream:
	if _cache.has(preset):
		return _cache[preset]
	var path := _preset_path(preset)
	if not FileAccess.file_exists(path):
		if not _missing_warned.get(preset, false):
			_missing_warned[preset] = true
			push_warning("[SFXBank] missing %s (rendered? see godot/tools/audio/slowstick_synth.py sfx %s)" % [path, preset])
		return null
	# WAV loader.
	var stream := AudioStreamWAV.new()
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return null
	var bytes := f.get_buffer(f.get_length())
	f.close()
	# Parse minimal WAV header to configure the stream. All our
	# authored WAVs are 16-bit mono 44.1 kHz per slowstick_synth's
	# defaults, so this is straightforward.
	var sr := 44100
	var bit_depth := 16
	var channels := 1
	var data_offset := 44
	if bytes.size() >= 44 and bytes[0] == 0x52 and bytes[1] == 0x49 and bytes[2] == 0x46 and bytes[3] == 0x46:
		sr = int(bytes[24]) | (int(bytes[25]) << 8) | (int(bytes[26]) << 16) | (int(bytes[27]) << 24)
		channels = int(bytes[22]) | (int(bytes[23]) << 8)
		bit_depth = int(bytes[34]) | (int(bytes[35]) << 8)
		# Find "data" chunk offset (some WAVs have a fmt chunk with
		# extra bytes before data). Search from offset 12 for "data".
		var i := 12
		while i < bytes.size() - 8:
			if bytes[i] == 0x64 and bytes[i+1] == 0x61 and bytes[i+2] == 0x74 and bytes[i+3] == 0x61:
				data_offset = i + 8
				break
			var chunk_size := int(bytes[i+4]) | (int(bytes[i+5]) << 8) | (int(bytes[i+6]) << 16) | (int(bytes[i+7]) << 24)
			i += 8 + chunk_size
	stream.mix_rate = sr
	stream.stereo = (channels == 2)
	stream.format = AudioStreamWAV.FORMAT_16_BITS if bit_depth == 16 else AudioStreamWAV.FORMAT_8_BITS
	stream.data = bytes.slice(data_offset)
	_cache[preset] = stream
	return stream
