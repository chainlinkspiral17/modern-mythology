extends Node
## TarotAudioManipulator
##
## Dynamic interpolation of the BGM bus effects driven by gauntlet
## pressure stats. Attaches a LowPass filter + Distortion to the BGM
## bus on _ready (idempotently — if the effects are already present
## from a prior instance, those are reused). Two update entry points:
##
##   update_stagnation(t: float)   — t in 0..1. The room dulls as the
##                                   maker forgets the make. LowPass
##                                   cutoff sweeps from BRIGHT_HZ down
##                                   to MUFFLED_HZ as t → 1.
##
##   update_doubt(t: float)        — t in 0..1. The world distorts
##                                   under the host's hands. Distortion
##                                   drive (and mix) ramp up as t → 1.
##
## reset() restores neutral state (full brightness, no distortion)
## immediately, useful when a scenario ends or the player leaves.
##
## All transitions use a Tween so the effect change is smooth (the
## audience feels the room dimming, not a jump). FADE_SEC controls
## how long each interpolation takes.

const BUS_NAME    := "BGM"
const FADE_SEC    := 0.6

# LowPass cutoff range — BRIGHT_HZ is essentially transparent (the bus
# sounds normal), MUFFLED_HZ pulls the high end out so the room reads
# as deadened. The lower the value the more "the maker is asleep on
# the workbench" it sounds.
const BRIGHT_HZ   := 18000.0
const MUFFLED_HZ  := 800.0

# Distortion drive — DRIVE_MIN is effectively off (still ~5% mix so
# the effect isn't bypassed by Godot), DRIVE_MAX is "the world is
# folding in on him." Mode is OVERDRIVE for a tube-warmth bite rather
# than a digital clip.
const DRIVE_MIN   := 0.0
const DRIVE_MAX   := 0.55
const MIX_MIN     := 0.0
const MIX_MAX     := 0.70

var _lpf:    AudioEffectLowPassFilter = null
var _dist:   AudioEffectDistortion    = null
var _tween:  Tween = null

var _stagnation_t: float = 0.0
var _doubt_t:      float = 0.0


func _ready() -> void:
	_ensure_effects()
	# Initialize to neutral so a fresh scenario starts transparent.
	_apply_stagnation(0.0)
	_apply_doubt(0.0)


func _exit_tree() -> void:
	# Don't tear the effects off the bus — other scenes / a later
	# instance of this manipulator can reuse them. Just kill any
	# pending tween so it doesn't fire on a freed node.
	if _tween != null and _tween.is_valid():
		_tween.kill()


# ── Public API ───────────────────────────────────────────────────────

# t in 0..1. Smoothly interpolate the LowPass cutoff toward the
# muffled end. Safe to call every frame — the tween de-duplicates
# repeated identical targets.
func update_stagnation(t: float) -> void:
	t = clampf(t, 0.0, 1.0)
	if is_equal_approx(t, _stagnation_t):
		return
	_stagnation_t = t
	_tween_stagnation_to(t)


# t in 0..1. Smoothly interpolate distortion drive + mix toward the
# distorted end.
func update_doubt(t: float) -> void:
	t = clampf(t, 0.0, 1.0)
	if is_equal_approx(t, _doubt_t):
		return
	_doubt_t = t
	_tween_doubt_to(t)


# Snap both stats back to neutral. Useful at scenario end / leave.
func reset() -> void:
	_stagnation_t = 0.0
	_doubt_t      = 0.0
	_apply_stagnation(0.0)
	_apply_doubt(0.0)


# ── Effect attachment ────────────────────────────────────────────────

func _ensure_effects() -> void:
	var bus_idx: int = AudioServer.get_bus_index(BUS_NAME)
	if bus_idx == -1:
		push_warning("TarotAudioManipulator: BGM bus not found.")
		return
	# Reuse existing effects of the right type if present.
	for i in AudioServer.get_bus_effect_count(bus_idx):
		var fx := AudioServer.get_bus_effect(bus_idx, i)
		if fx is AudioEffectLowPassFilter and _lpf == null:
			_lpf = fx
		elif fx is AudioEffectDistortion and _dist == null:
			_dist = fx
	if _lpf == null:
		_lpf = AudioEffectLowPassFilter.new()
		AudioServer.add_bus_effect(bus_idx, _lpf)
	if _dist == null:
		_dist = AudioEffectDistortion.new()
		_dist.mode = AudioEffectDistortion.MODE_OVERDRIVE
		AudioServer.add_bus_effect(bus_idx, _dist)


# ── Tween helpers ────────────────────────────────────────────────────

func _ensure_tween() -> void:
	if _tween != null and _tween.is_valid():
		return
	_tween = create_tween()
	_tween.set_parallel(true)
	_tween.set_trans(Tween.TRANS_QUAD)
	_tween.set_ease(Tween.EASE_OUT)


func _tween_stagnation_to(t: float) -> void:
	if _lpf == null:
		return
	_ensure_tween()
	var target_hz: float = lerpf(BRIGHT_HZ, MUFFLED_HZ, t)
	_tween.tween_method(_set_lpf_cutoff, _lpf.cutoff_hz, target_hz, FADE_SEC)


func _tween_doubt_to(t: float) -> void:
	if _dist == null:
		return
	_ensure_tween()
	# Single tween_method drives both drive + post_gain via _apply_doubt.
	# This keeps the two parameters in lockstep and avoids a second
	# state variable for the mix value.
	_tween.tween_method(_apply_doubt, _doubt_current(), t, FADE_SEC)


# Read the effective current doubt-t back out of the distortion's
# drive setting. Used so the next tween starts from where the previous
# one landed instead of snapping.
func _doubt_current() -> float:
	if _dist == null:
		return 0.0
	return clampf(inverse_lerp(DRIVE_MIN, DRIVE_MAX, _dist.drive), 0.0, 1.0)


# Setter routed through method so Tween.tween_method can drive it.
func _set_lpf_cutoff(hz: float) -> void:
	if _lpf != null:
		_lpf.cutoff_hz = hz


# Direct apply (no tween) — used at init and on reset() for snap.
func _apply_stagnation(t: float) -> void:
	if _lpf != null:
		_lpf.cutoff_hz = lerpf(BRIGHT_HZ, MUFFLED_HZ, t)


func _apply_doubt(t: float) -> void:
	if _dist != null:
		_dist.drive     = lerpf(DRIVE_MIN, DRIVE_MAX, t)
		_dist.post_gain = lerpf(-10.0, 4.0, lerpf(MIX_MIN, MIX_MAX, t))
