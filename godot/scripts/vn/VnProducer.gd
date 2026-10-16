extends Node
## VN PRODUCER — the department coordinator.
##
## The VnDirector stages individual shots; nobody was making the
## departments deliver TOGETHER. Before this: the first line typed
## away under the chapter card (the typewriter moment spent before
## the curtain was up), BGM hard-cut while the picture faded, and the
## camera reset mid-fade. The producer owns the production clock:
##
##   · THE CURTAIN GATE — story dispatch (`_run_next`) is deferred
##     through `when_curtain_up()` while a transition holds the
##     curtain. Nothing plays to a black house.
##   · AUDIO IN SYNC WITH PICTURE — the scene's music ducks WITH the
##     fade-out, stops at black, and returns as the veil lifts
##     (riding AudioMgr's existing duck/unduck machinery — no new
##     audio paths). The chapter plate sits in hush.
##   · THE SETTLE BEAT — after the reveal, a short breath before the
##     first line, so the establishing shot lands as a picture
##     before it becomes a page.
##
## Future departments hook here: painted art plates, portrait
## relighting on mood, per-scene ambience choreography. One clock.
##
## Owned by GameEngine (created in _ready, like VnDirector). All
## calls are safe with no scene loaded. NOT a mood authority — mood
## stays with VnDirector→MoodCycler (LightController is CP-only and
## appears in no VN locale; bridging it would drive nothing).

const SETTLE_S := 0.25

var _held: bool = false
var _pending: Array[Callable] = []


# ── The curtain gate ─────────────────────────────────────────────

func hold_curtain() -> void:
	_held = true


## Runs `cb` immediately when the curtain is up, otherwise queues it
## for the settle beat after `curtain_up()`. Mid-story jumps (choice
## targets, gotos) never hold the curtain, so they pass straight
## through — the gate only exists across real transitions.
func when_curtain_up(cb: Callable) -> void:
	if _held:
		_pending.append(cb)
	else:
		cb.call()


func curtain_up() -> void:
	if not _held:
		_flush()
		return
	_held = false
	# The settle beat — the establishing shot breathes before the
	# first line starts to type.
	var tw := create_tween()
	tw.tween_interval(SETTLE_S)
	tw.tween_callback(_flush)


func _flush() -> void:
	var cbs := _pending.duplicate()
	_pending.clear()
	for cb in cbs:
		if cb.is_valid():
			cb.call()


# ── Audio, synced to picture ─────────────────────────────────────
# Order is guaranteed by the curtain gate: no new say-node can duck
# for dialogue until after reveal_begin() has unducked, so the one
# duck flag never fights itself.

func scene_out_begin() -> void:
	# The music dips with the fade-out.
	AudioMgr.duck()


func scene_out_black() -> void:
	# At full black: the old scene's bed actually stops.
	AudioMgr.stop_scene_bgm()


func reveal_begin() -> void:
	# Light returns, and the (new) music rises with it.
	AudioMgr.unduck()
