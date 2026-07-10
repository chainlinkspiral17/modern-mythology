extends Node
class_name RiffmasterLoopPlayer
## Replays a recorded Riffmaster loop through the real voice.
##
## A loop is {"events": [{"s": semitones, "t": start_sec, "d": dur_sec}]}
## — the shape the OPEN MIC recorder writes and the heirloom JSON
## uses.  Owns a PDPRiffmaster child with input_enabled = false, so
## it can live anywhere (the club title screen, the Estuary 3
## cabin radio) without eating the key row.

const VOICE_SCRIPT := "res://scripts/PDPRiffmaster.gd"

var _voice: Node = null
var _generation: int = 0


func _ready() -> void:
	_voice = load(VOICE_SCRIPT).new()
	_voice.set("input_enabled", false)
	add_child(_voice)


func set_gain_db(db: float) -> void:
	if _voice != null and _voice.has_method("set_gain_db"):
		_voice.call("set_gain_db", db)


## Drive someone else's voice instead of our own · the club
## meeting routes call playback through ITS synth so the drawn
## keys light up while the call plays.
func use_external_voice(voice: Node) -> void:
	if _voice != null and _voice.get_parent() == self:
		_voice.queue_free()
	_voice = voice


## Play the loop once, or repeat with a breath between passes.
func play_loop(loop: Dictionary, repeat: bool = false, gap_sec: float = 1.6) -> void:
	stop()
	_generation += 1
	_run_pass(loop, repeat, gap_sec, _generation)


func stop() -> void:
	_generation += 1


func loop_length(loop: Dictionary) -> float:
	var end := 0.0
	for ev in loop.get("events", []):
		var e: Dictionary = ev
		end = maxf(end, float(e.get("t", 0.0)) + float(e.get("d", 0.5)))
	return end


func _run_pass(loop: Dictionary, repeat: bool, gap_sec: float, gen: int) -> void:
	var events: Array = loop.get("events", [])
	if events.is_empty():
		return
	for ev in events:
		var e: Dictionary = ev
		var s: int = int(e.get("s", 0))
		var t: float = float(e.get("t", 0.0))
		var d: float = maxf(0.08, float(e.get("d", 0.5)))
		_schedule(t, func() -> void:
			if gen == _generation and _voice != null:
				_voice.call("play_note", s))
		_schedule(t + d, func() -> void:
			if gen == _generation and _voice != null:
				_voice.call("release_note", s))
	if repeat:
		_schedule(loop_length(loop) + gap_sec, func() -> void:
			if gen == _generation:
				_run_pass(loop, repeat, gap_sec, gen))


func _schedule(delay: float, callable: Callable) -> void:
	if delay <= 0.0:
		callable.call()
		return
	var timer := get_tree().create_timer(delay)
	timer.timeout.connect(callable)
