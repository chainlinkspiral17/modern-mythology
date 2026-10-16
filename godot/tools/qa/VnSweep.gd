extends Node
## Headless QA: VN chapter traversal — the runtime twin of
## vn_story_audit.py. Boots GameEngine and PLAYS every scene of
## every volume: advances each line, auto-picks the first choice,
## taps through interludes, and watches for stalls (a scene that
## stops progressing is a broken scene, whatever the static audit
## says). Catches handler crashes, bad node payloads the schema
## audit can't see, and dead-end flows.
##
## Traversal order is BACK TO FRONT — per the user's 2026-08-30
## direction, the START of each volume has absorbed the most
## iteration, so the tail chapters get checked (and later,
## polished) first. Vol 7 tail is the first thing this sweep runs.
##
## Run: godot --headless res://tools/qa/VnSweep.tscn

const ENGINE_SCENE := "res://scenes/game/GameEngine.tscn"
const VOLS := [7, 6, 5, 4, 3, 2, 1]
const TICK_FRAMES := 2
const SCENE_TICK_CAP := 2400      # ~4800 frames · a scene longer than
                                  # this isn't advancing, it's looping
const STALL_TAP_AT := 120         # ticks with no progress → start tapping
const STALL_FAIL_AT := 420        # ticks with no progress → STALL

var _stalls: int = 0
var _errors: int = 0


func _ready() -> void:
	for vol in VOLS:
		await _sweep_volume(vol)
	print("VN sweep done · %d stall(s) · %d error(s)" % [_stalls, _errors])
	get_tree().quit(1 if (_stalls > 0 or _errors > 0) else 0)


func _sweep_volume(vol: int) -> void:
	var scene_ids: Array = SceneDataDB.get_volume_scenes(vol)
	if scene_ids.is_empty():
		print("VN-SKIP vol%d · no scenes" % vol)
		return
	print("VN-VOL %d · %d scene(s), traversing back to front" % [vol, scene_ids.size()])
	var engine: Node = (load(ENGINE_SCENE) as PackedScene).instantiate()
	add_child(engine)
	if engine.has_signal("game_ended"):
		engine.connect("game_ended", func() -> void: _flow_ended = true)
	for f in range(4):
		await get_tree().process_frame
	# get_volume_scenes returns full scene DICTS (id inside), not ids.
	var reversed_scenes: Array = scene_ids.duplicate()
	reversed_scenes.reverse()
	# Targeted runs: VN_SWEEP_ONLY="sid1,sid2" plays just those scenes
	# (any volume). For verifying a fix without the hour-long full run.
	var only_raw := OS.get_environment("VN_SWEEP_ONLY")
	var only: PackedStringArray = only_raw.split(",", false) if only_raw != "" else PackedStringArray()
	var played: int = 0
	for sc_v in reversed_scenes:
		var sid: String = String((sc_v as Dictionary).get("id", ""))
		if sid == "":
			continue
		if only.size() > 0 and not (sid in only):
			continue
		await _play_scene(engine, vol, sid)
		played += 1
	if only.size() > 0:
		if played > 0:
			print("VN-VOL %d filtered · %d scene(s) played" % [vol, played])
		engine.queue_free()
		await get_tree().process_frame
		return
	# PROGRESS assertion (QA README rule): a volume that played zero
	# scenes means the sweep itself broke — never report that as clean.
	if played == 0:
		print("VN-ERR  vol%d · sweep played ZERO scenes" % vol)
		_errors += 1
	engine.queue_free()
	await get_tree().process_frame


var _flow_ended: bool = false


func _play_scene(engine: Node, vol: int, sid: String) -> void:
	_flow_ended = false
	engine.call("start", vol, sid)
	await get_tree().process_frame
	var last_fp: String = ""
	var stall_ticks: int = 0
	var nodes_walked: int = 0
	for tick in range(SCENE_TICK_CAP):
		for f in range(TICK_FRAMES):
			await get_tree().process_frame
		var cur_scene := String(engine.get("_scene_id"))
		# The engine chained past our target (vols 5-7 flow) or a
		# jump moved it — this scene traversed clean.
		if cur_scene != sid:
			print("VN-OK   vol%d %-38s %d node(s) walked → %s" %
				[vol, sid, nodes_walked, cur_scene])
			return
		# The scene's `end` node closed the whole flow (last scene of
		# a reading order): that's a clean traversal, not a stall.
		if _flow_ended:
			print("VN-OK   vol%d %-38s %d node(s) walked → (flow end)" %
				[vol, sid, nodes_walked])
			return
		var fp := "%s#%s" % [cur_scene, str(engine.get("_node_idx"))]
		if fp != last_fp:
			last_fp = fp
			stall_ticks = 0
			nodes_walked += 1
		else:
			stall_ticks += 1
		_drive(engine, stall_ticks)
		if stall_ticks >= STALL_FAIL_AT:
			print("VN-STALL vol%d %-38s stuck at %s after %d node(s)" %
				[vol, sid, fp, nodes_walked])
			_stalls += 1
			return
	# Never left the scene and never stalled: either a very long
	# scene (raise the cap) or a same-scene loop.
	var ended: bool = not engine.get("_waiting")
	if nodes_walked > 1:
		print("VN-OK   vol%d %-38s %d node(s) walked (end of flow · ended=%s)" %
			[vol, sid, nodes_walked, str(ended)])
	else:
		print("VN-STALL vol%d %-38s no progress at all" % [vol, sid])
		_stalls += 1


func _drive(engine: Node, stall_ticks: int) -> void:
	# A visible choice menu: resolve option 0 directly. (Emitting the
	# button's `pressed` proved flaky under stagger; _on_chosen is the
	# same code path a click reaches.)
	var choices: Node = engine.get("_choices")
	if choices != null and bool(choices.get("visible")):
		choices.call("_on_chosen", 0)
		return
	# CG panels, interludes, and chapter cards all dismiss on the
	# "advance" ACTION. The input map binds it by PHYSICAL keycode, so
	# a plain InputEventKey with only `keycode` set never matches —
	# the first sweep stalled on every cg node because of exactly
	# that. InputEventAction sidesteps the keyboard entirely.
	var cg: Node = engine.get("_cg")
	if cg != null and bool(cg.get("visible")):
		_tap_advance()
		return
	var interlude: Node = engine.get("_interlude")
	if interlude != null and bool(interlude.get("visible")):
		_tap_advance()
	# Normal advance. When stalled a while, add action taps too.
	engine.call("_advance")
	if stall_ticks > STALL_TAP_AT:
		_tap_advance()


func _tap_advance() -> void:
	var down := InputEventAction.new()
	down.action = "advance"
	down.pressed = true
	Input.parse_input_event(down)
	var up := InputEventAction.new()
	up.action = "advance"
	up.pressed = false
	Input.parse_input_event(up)
