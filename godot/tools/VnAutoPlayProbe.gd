extends Node
## AUTO-PLAY PROBE (2026-11-10): a scene read hands-free, on the clock. The
## user: "auto-play isn't working ... it's taking a long time between
## continuing" and "making choices in the menu still breaks the game."
##
##   godot --headless --path godot res://tools/VnAutoPlayProbe.tscn -- \
##     --scene vol5_ch1_magician --node 19 --seconds 90 [--auto 1] [--aa 0] \
##     [--click 1] [--stall 12]
##
## --auto 1  AUTO-PLAY on (default); --aa N  AUTO ADVANCE in ms (default 0).
## --click 1 AUTO-PLAY off: the probe turns the pages itself and, at a choice,
##           CLICKS the first option with a real mouse event.
## Prints every page turn with the seconds since the last one, and a ✗ for a
## wait over --stall seconds, a choice that did not take, or a line with no
## text after a choice. Exit 1 on any ✗. Not HUD; quits when done.

const ENGINE := preload("res://scenes/game/GameEngine.tscn")
var _args: Dictionary = {}
var _bad: int = 0


func _ready() -> void:
	var ua: PackedStringArray = OS.get_cmdline_user_args()
	for i in ua.size():
		if ua[i].begins_with("--"):
			_args[ua[i].trim_prefix("--")] = ua[i + 1] if i + 1 < ua.size() and not ua[i + 1].begins_with("--") else ""
	_run.call_deferred()


func _flag(what: String) -> void:
	_bad += 1
	print("  ✗ %s" % what)


func _click(at: Vector2) -> void:
	for down: bool in [true, false]:
		var ev := InputEventMouseButton.new()
		ev.button_index = MOUSE_BUTTON_LEFT
		ev.pressed = down
		ev.position = at
		ev.global_position = at
		get_viewport().push_input(ev, true)      # the canvas's own coordinates
		await get_tree().process_frame
		await get_tree().process_frame


func _run() -> void:
	var click: bool = String(_args.get("click", "0")) == "1"
	Settings.set("auto_play", (not click) and String(_args.get("auto", "1")) == "1")
	Settings.set("auto_advance_ms", int(String(_args.get("aa", "0"))))
	var scene_id: String = String(_args.get("scene", ""))
	var node_i: int = int(String(_args.get("node", "1")))
	var seconds: float = float(String(_args.get("seconds", "90")))
	var stall: float = float(String(_args.get("stall", "12")))
	var sc: Dictionary = SceneDataDB.get_scene(scene_id)
	if sc.is_empty():
		push_error("no scene %s" % scene_id)
		get_tree().quit(1)
		return
	var eng: Node = ENGINE.instantiate()
	get_tree().root.add_child(eng)
	await get_tree().process_frame
	eng.call("start", int(sc.get("vol", 1)), scene_id, -1, max(node_i, 1))
	var dlg: Control = eng.get("_dlg")
	var choices: Control = eng.get("_choices")
	var t: float = 0.0
	var since: float = 0.0
	var last_key: String = ""
	var turns: int = 0
	var rested: float = 0.0
	while t < seconds:
		await get_tree().process_frame
		# the game's own clock (Godot caps a slow frame's delta, so a software
		# renderer at 1 fps is not 1 s a frame to the game)
		var dt: float = get_process_delta_time()
		t += dt
		since += dt
		var key: String = "%s#%d" % [String(eng.get("_scene_id")), int(eng.get("_node_idx"))]
		if key != last_key:
			var nodes: Array = (eng.get("_scene_data") as Dictionary).get("nodes", [])
			var idx: int = int(eng.get("_node_idx")) - 1
			var kind: String = ""
			var chars: int = 0
			if idx >= 0 and idx < nodes.size() and nodes[idx] is Dictionary:
				kind = String((nodes[idx] as Dictionary).get("t", ""))
				chars = String((nodes[idx] as Dictionary).get("text", "")).length()
			if last_key != "":
				print("  %6.1fs  +%5.1fs  %s  %s (%d chars)" % [t, since, key, kind, chars])
				turns += 1
			last_key = key
			since = 0.0
			rested = 0.0
		if since > stall:
			_flag("%s has waited %.0f s (choices %s · card %s · typing %s · line '%s')" % [
				key, since, choices.visible, (eng.get("_interlude") as Control).visible,
				dlg.call("is_typing"), String(dlg.get("_full_text")).left(40)])
			print("    auto %s · waiting %s · lock %s · photo %s · blocker %s · read_t %.1f · hold %.1f · voice %s · dlg %s" % [
				eng.get("_auto_mode"), eng.get("_waiting"), eng.get("_transition_lock"), eng.get("_photo_on"),
				get_tree().get_first_node_in_group("vn_input_blocker"), float(eng.get("_auto_read_t")),
				float(eng.call("_auto_hold")), AudioMgr.is_voice_playing(), dlg.visible])
			print("    char %d of %d · text shown %s · lock %s · paused %s · dlg processing %s · fps %.1f" % [
				int(dlg.get("_char_idx")), int(dlg.call("_count_visible", String(dlg.get("_full_text")))),
				dlg.visible, eng.get("_transition_lock"), eng.get("_paused"), dlg.is_processing(),
				Engine.get_frames_per_second()])
			break
		if click:
			if choices.visible:
				rested += dt
				if rested > 1.2:
					var vb: VBoxContainer = choices.get("_vbox")
					var btn: Control = vb.get_child(0) as Control
					var want: String = (btn as Button).text
					await _click(btn.get_global_rect().get_center())
					for i in 30:
						await get_tree().process_frame
					if choices.visible:
						_flag("%s: clicked '%s' and the choice is still up" % [key, want.left(40)])
						var mv := InputEventMouseMotion.new()
						mv.position = btn.get_global_rect().get_center()
						mv.global_position = mv.position
						get_viewport().push_input(mv, true)
						await get_tree().process_frame
						await get_tree().process_frame
						var hov: Control = get_viewport().gui_get_hovered_control()
						var colc: Control = choices.get("_column")
						print("    screen %s · choice menu %s · its column %s (grow v %d)" % [
							get_viewport().get_visible_rect().size, choices.get_global_rect(),
							colc.get_global_rect(), colc.grow_vertical])
						print("    under the pointer at %s: %s · button rect %s · alpha %.2f · disabled %s" % [
							mv.position, (hov.get_path() if hov != null else NodePath("(nothing)")),
							btn.get_global_rect(), btn.modulate.a, (btn as Button).disabled])
						break
					print("  %6.1fs  chose '%s' → %s#%d · text up: %s · line '%s'" % [t, want.left(36),
						String(eng.get("_scene_id")), int(eng.get("_node_idx")), dlg.visible,
						String(dlg.get("_full_text")).left(40)])
					rested = 0.0
			elif (eng.get("_interlude") as Control).visible:
				rested += dt
				if rested > 1.0:
					(eng.get("_interlude") as Control).call("try_advance")
					rested = 0.0
			elif dlg.visible and bool(eng.get("_waiting")) and not bool(dlg.call("is_typing")):
				rested += dt
				if rested > 0.3:
					await _click(Vector2(200, 200))
					rested = 0.0
			elif dlg.visible and bool(dlg.call("is_typing")):
				dlg.call("finish_typing")
	print("[VnAutoPlayProbe] %s · %d page turn(s) in %.0f s · %d finding(s)" % [scene_id, turns, t, _bad])
	get_tree().quit(1 if _bad > 0 else 0)
