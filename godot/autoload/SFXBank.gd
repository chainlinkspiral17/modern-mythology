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

const SFX_ROOT := "res://assets/audio/sfx/e3/"
const POOL_SIZE := 8

# Preset → filename (relative to SFX_ROOT). Kept explicit so the
# audit doc doubles as the registry.
const PRESET_MAP := {
	# Original SFX set
	"coin":               "coin.wav",
	"hurt":               "hurt.wav",
	"jump":               "jump.wav",
	"blip":               "blip.wav",
	"pickup":             "pickup.wav",
	"door_open":          "door_open.wav",
	"register_ding":      "register_ding.wav",
	"phone_ring":         "phone_ring.wav",
	"broom_sweep":        "broom_sweep.wav",
	"cooler_whoosh":      "cooler_whoosh.wav",
	"fluorescent_start":  "fluorescent_start.wav",
	"tide_pool_splash":   "tide_pool_splash.wav",
	"stick_scratch":      "stick_scratch.wav",
	# Wave A · UI
	"verb_select":        "verb_select.wav",
	"turn_tick":          "turn_tick.wav",
	"customer_bell":      "customer_bell.wav",
	"control_click":      "control_click.wav",
	"season_settle":      "season_settle.wav",
	"tile_hover":         "tile_hover.wav",
	"tile_enter":         "tile_enter.wav",
	"press_hit":          "press_hit.wav",
	"press_miss":         "press_miss.wav",
	"cartridge_hover":    "cartridge_hover.wav",
	"cartridge_click":    "cartridge_click.wav",
	"boot":               "boot.wav",
}

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
	var fname: String = PRESET_MAP[preset]
	var path := SFX_ROOT + fname
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
