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
const SFX_GAUNTLET_ROOT := "res://assets/audio/sfx/gauntlet/"
const SFX_UI_ROOT := "res://assets/audio/sfx/ui/"
const SFX_FF_ROOT := "res://assets/audio/sfx/ff/"
const SFX_EM_ROOT := "res://assets/audio/sfx/em/"
const SFX_NH_ROOT := "res://assets/audio/sfx/nh/"
const SFX_PMG_ROOT := "res://assets/audio/sfx/pmg/"
const SFX_SD_ROOT := "res://assets/audio/sfx/sd/"
const SFX_SB_ROOT := "res://assets/audio/sfx/sb/"
const POOL_SIZE := 8

# Preset → (root, filename). Kept explicit so the audit doc doubles
# as the registry. Wave A lives under e3/; Wave C under cp/.
const PRESET_MAP := {
	# Patient Mister Glass kitchen foley
	"kettle_hiss":            ["pmg", "kettle_hiss.wav"],
	"knife_board":            ["pmg", "knife_board.wav"],
	# Salmonberry (Oneironautics, 2006) · coastal RPG
	"harbor_bell":            ["sb", "harbor_bell.wav"],
	# Spiderdrops (PDP Toys, 1993) · the storm on the web
	"thread_pluck":           ["sd", "thread_pluck.wav"],
	"thread_snap":            ["sd", "thread_snap.wav"],
	"thread_spin":            ["sd", "thread_spin.wav"],
	"wind_gust":              ["sd", "wind_gust.wav"],
	"spider_step":            ["sd", "spider_step.wav"],
	"silk_cast":              ["sd", "silk_cast.wav"],
	# Northwind Harbor one-shots (1988 · almost no sound, so each counts)
	"boat_horn":              ["nh", "boat_horn.wav"],
	"lamp_buzz":              ["nh", "lamp_buzz.wav"],
	"water_slap":             ["nh", "water_slap.wav"],
	"boot_plank":             ["nh", "boot_plank.wav"],
	# Earthman ambient one-shots
	"parsa_wind":             ["em", "parsa_wind.wav"],
	"mine_drip":              ["em", "mine_drip.wav"],
	"kyrindi_bell":           ["em", "kyrindi_bell.wav"],
	# Fey Faire ambient one-shots
	"calliope_drift":         ["ff", "calliope_drift.wav"],
	"canvas_flap":            ["ff", "canvas_flap.wav"],
	"night_crowd":            ["ff", "night_crowd.wav"],
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
	"radio_889_bed":                        ["e3", "radio_889_bed.wav"],
	"radio_1150_bed":                       ["e3", "radio_1150_bed.wav"],
	"radio_1600_static_voice_night_5":      ["e3", "radio_1600_static_voice_night_5.wav"],
	"radio_1600_static_voice_night_12_sam": ["e3", "radio_1600_static_voice_night_12_sam.wav"],
	"2am_customer_stands_up":               ["e3", "2am_customer_stands_up.wav"],
	"creature_arrival_2am_customer":        ["e3", "creature_arrival_2am_customer.wav"],
	"creature_arrival_kid_on_bike":         ["e3", "creature_arrival_kid_on_bike.wav"],
	# Wave F · closing set
	"radio_static":                ["e3", "radio_static.wav"],
	"season_success":              ["e3", "season_success.wav"],
	"season_failure":              ["e3", "season_failure.wav"],
	"tide_gate_toggle":            ["e3", "tide_gate_toggle.wav"],
	"wave_break":                  ["e3", "wave_break.wav"],
	"gull_cry":                    ["e3", "gull_cry.wav"],
	"heron_wingbeat":              ["e3", "heron_wingbeat.wav"],
	"hotspot_look":                ["e3", "hotspot_look.wav"],
	"hotspot_talk":                ["e3", "hotspot_talk.wav"],
	"hotspot_use":                 ["e3", "hotspot_use.wav"],
	"clock_tick":                  ["e3", "clock_tick.wav"],
	"return_to_shop":              ["e3", "return_to_shop.wav"],
	"creature_arrival_heron":      ["e3", "creature_arrival_heron.wav"],
	"creature_arrival_otter":      ["e3", "creature_arrival_otter.wav"],
	"creature_arrival_crab":       ["e3", "creature_arrival_crab.wav"],
	"creature_arrival_fry":        ["e3", "creature_arrival_fry.wav"],
	"tide_swallow":                ["e3", "tide_swallow.wav"],
	"signing":                     ["e3", "signing.wav"],
	"page_turn":                   ["e3", "page_turn.wav"],
	"unlock_chime":                ["e3", "unlock_chime.wav"],
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
	# Wave D · Gauntlet
	"card_flip":              ["gauntlet", "card_flip.wav"],
	"card_place":             ["gauntlet", "card_place.wav"],
	"hand_deal":              ["gauntlet", "hand_deal.wav"],
	"threshold_cross":        ["gauntlet", "threshold_cross.wav"],
	"visitor_arrive":         ["gauntlet", "visitor_arrive.wav"],
	"lore_token_reveal":      ["gauntlet", "lore_token_reveal.wav"],
	"scrapbook_open":         ["gauntlet", "scrapbook_open.wav"],
	"scenario_unlock":        ["gauntlet", "scenario_unlock.wav"],
	"scenario_picker":        ["gauntlet", "scenario_picker.wav"],
	"win_chord":              ["gauntlet", "win_chord.wav"],
	"loss_thud":              ["gauntlet", "loss_thud.wav"],
	# Wave D · Shared UI
	"menu_open":              ["ui", "menu_open.wav"],
	"menu_close":             ["ui", "menu_close.wav"],
	"button_hover":           ["ui", "button_hover.wav"],
	"button_click":           ["ui", "button_click.wav"],
	"save_confirm":           ["ui", "save_confirm.wav"],
	"load_start":             ["ui", "load_start.wav"],
	"notification":           ["ui", "notification.wav"],
}


func _preset_path(preset: String) -> String:
	var entry: Array = PRESET_MAP[preset]
	var kind: String = String(entry[0])
	var root: String
	match kind:
		"cp":       root = SFX_CP_ROOT
		"gauntlet": root = SFX_GAUNTLET_ROOT
		"ui":       root = SFX_UI_ROOT
		"ff":       root = SFX_FF_ROOT
		"em":       root = SFX_EM_ROOT
		"nh":       root = SFX_NH_ROOT
		"pmg":      root = SFX_PMG_ROOT
		"sd":       root = SFX_SD_ROOT
		"sb":       root = SFX_SB_ROOT
		_:          root = SFX_E3_ROOT
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
	var effective: float = maxf(0.0, settings_vol * volume_ratio)
	if effective <= 0.0:
		return
	p.volume_db = linear_to_db(effective)
	p.play()
	_rumble_for_preset(preset, clampf(volume_ratio, 0.0, 1.0))


func has_preset(preset: String) -> bool:
	return PRESET_MAP.has(preset)


# ─── Haptic rumble grammar ───────────────────────────────────────
# SFXBank is the package's sound grammar, so it is also the haptics
# grammar: every play() looks up the preset here and drives SDL
# rumble on all connected pads. Baseline device: the 2026 Steam
# Controller — its HD haptic motors render SDL rumble, so this one
# table covers Steam Deck, Steam Controller, and ordinary XInput
# pads alike. Unmapped presets are silent by design (ambient beds,
# hover ticks — rumble spam is worse than none).
# Values: [weak_motor 0-1, strong_motor 0-1, duration_s].
const RUMBLE_MAP := {
	# UI paper + cards
	"blip":              [0.08, 0.00, 0.04],
	"button_click":      [0.06, 0.00, 0.04],
	"menu_open":         [0.10, 0.00, 0.06],
	"menu_close":        [0.10, 0.00, 0.06],
	"page_turn":         [0.14, 0.00, 0.09],
	"card_flip":         [0.12, 0.00, 0.06],
	"card_place":        [0.16, 0.06, 0.09],
	"hand_deal":         [0.12, 0.00, 0.08],
	"scenario_picker":   [0.12, 0.00, 0.08],
	"verb_select":       [0.08, 0.00, 0.05],
	"control_click":     [0.08, 0.00, 0.05],
	"cartridge_click":   [0.14, 0.05, 0.08],
	"boot":              [0.15, 0.20, 0.35],
	"load_start":        [0.12, 0.10, 0.25],
	# Rewards + confirmations
	"register_ding":     [0.16, 0.00, 0.08],
	"coin":              [0.10, 0.00, 0.05],
	"pickup":            [0.12, 0.00, 0.07],
	"save_confirm":      [0.10, 0.00, 0.06],
	"unlock_chime":      [0.22, 0.10, 0.18],
	"lore_token_reveal": [0.20, 0.08, 0.15],
	"scenario_unlock":   [0.22, 0.10, 0.20],
	"interlude_earned":  [0.18, 0.08, 0.15],
	"scrapbook_open":    [0.12, 0.00, 0.08],
	"season_success":    [0.25, 0.20, 0.30],
	"win_chord":         [0.30, 0.50, 0.45],
	"signing":           [0.12, 0.00, 0.10],
	# Impacts + losses
	"loss_thud":         [0.00, 0.85, 0.40],
	"press_hit":         [0.20, 0.45, 0.12],
	"press_miss":        [0.10, 0.00, 0.08],
	"hurt":              [0.15, 0.55, 0.18],
	"season_failure":    [0.20, 0.40, 0.30],
	"tide_swallow":      [0.20, 0.50, 0.35],
	"threshold_cross":   [0.20, 0.30, 0.20],
	"labor_day_arrival": [0.30, 0.40, 0.60],
	"basement_rite":     [0.10, 0.35, 0.80],
	"jump":              [0.12, 0.08, 0.08],
	# World + creatures
	"door_open":         [0.08, 0.00, 0.06],
	"boot_plank":        [0.10, 0.15, 0.08],
	"boat_horn":         [0.25, 0.35, 0.70],
	"customer_bell":     [0.12, 0.00, 0.08],
	"phone_ring":        [0.15, 0.10, 0.25],
	"visitor_arrive":    [0.12, 0.00, 0.10],
	"wave_break":        [0.15, 0.10, 0.25],
	"tide_gate_toggle":  [0.20, 0.25, 0.15],
	# Spiderdrops · a snap you feel, a gust that rolls. Step/spin are
	# too frequent/soft to rumble (spam is worse than none).
	"thread_snap":       [0.18, 0.30, 0.12],
	"thread_pluck":      [0.10, 0.00, 0.06],
	"wind_gust":         [0.12, 0.22, 0.55],
	"harbor_bell":       [0.10, 0.28, 0.45],
	"marker_set":        [0.10, 0.00, 0.06],
	"2am_customer_stands_up":       [0.15, 0.30, 0.30],
	"creature_arrival_2am_customer": [0.20, 0.25, 0.30],
	"creature_arrival_kid_on_bike":  [0.15, 0.15, 0.25],
	"creature_arrival_heron":        [0.15, 0.10, 0.25],
	"creature_arrival_otter":        [0.15, 0.10, 0.25],
	"creature_arrival_crab":         [0.12, 0.10, 0.20],
	"creature_arrival_fry":          [0.10, 0.08, 0.18],
	"tier_crossing_restless":        [0.15, 0.25, 0.25],
	"tier_crossing_hungry":          [0.18, 0.30, 0.28],
	"tier_crossing_close":           [0.20, 0.35, 0.30],
	"tier_crossing_turned":          [0.25, 0.45, 0.40],
	"pair_loud":         [0.15, 0.20, 0.20],
	"roster_loud":       [0.15, 0.20, 0.20],
}


func _rumble_for_preset(preset: String, ratio: float) -> void:
	if not RUMBLE_MAP.has(preset):
		return
	var r: Array = RUMBLE_MAP[preset]
	rumble(float(r[0]) * ratio, float(r[1]) * ratio, float(r[2]))


## Public · explicit rumble for beats with no SFX (or beats that
## deserve more than their sound). Respects Settings.haptics.
func rumble(weak: float, strong: float, duration_s: float) -> void:
	var settings := get_node_or_null("/root/Settings")
	var strength: float = 1.0
	if settings != null and settings.get("haptics") != null:
		strength = float(settings.get("haptics"))
	if strength <= 0.01:
		return
	for dev in Input.get_connected_joypads():
		Input.start_joy_vibration(int(dev),
				clampf(weak * strength, 0.0, 1.0),
				clampf(strong * strength, 0.0, 1.0),
				maxf(0.02, duration_s))


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
