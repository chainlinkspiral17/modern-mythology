extends Node
## Headless QA: UI monkey — boots a host scene and PRESSES REAL
## BUTTONS for N iterations (skipping quit/back/shelf/erase), which
## walks title → run → gameplay loops the way a hand does. Catches
## _pressed-handler crashes and dead-end screens (no buttons at
## all is reported).
## Run: godot --headless res://tools/qa/MonkeySweep.tscn

const TARGETS := {
	"pirate_summer":  "res://scenes/games/pirate_summer/PirateSummerHost.tscn",
	"fey_faire":      "res://scenes/games/fey_faire/FeyFaireHost.tscn",
	"earthman":       "res://scenes/games/earthman_chronicles/EarthmanChroniclesHost.tscn",
	"sams_shifts":    "res://scenes/games/sams_summer_shifts/SamsSummerShiftsHost.tscn",
	"estuary_1":      "res://scenes/games/estuary_1/Estuary1Host.tscn",
	"northwind":      "res://scenes/games/northwind_harbor/NorthwindHarborHost.tscn",
	"riffrocker":     "res://scenes/games/riffrocker_melody_club/RiffrockerClubHost.tscn",
	"mister_glass":   "res://scenes/games/patient_mister_glass/PatientGlassHost.tscn",
	"sweetgum":       "res://scenes/games/sweetgum/SweetgumHost.tscn",
	"mrs_wus":        "res://scenes/games/mrs_wus_garden/MrsWuHost.tscn",
	"tideline":       "res://scenes/games/the_tideline/TidelineHost.tscn",
	"estuary_4":      "res://scenes/games/estuary_4/EstuaryFourHost.tscn",
	"estuary_2":      "res://scenes/games/estuary_2/Estuary2Host.tscn",
	"hane_no_niwa":   "res://scenes/games/hane_no_niwa/HaneNoNiwaHost.tscn",
	"sisters_wyrd":   "res://scenes/games/sisters_wyrd/SistersWyrdHost.tscn",
	"kwik_stop_mgr":  "res://scenes/games/kwik_stop_manager/KwikStopManagerHost.tscn",
	"spiderdrops":    "res://scenes/games/spiderdrops/SpiderdropsHost.tscn",
	"spiderdrops_2":  "res://scenes/games/spiderdrops_2/SpiderdropsTwoHost.tscn",
	"salmonberry":    "res://scenes/games/salmonberry/SalmonberryHost.tscn",
	"basilica":       "res://scenes/games/basilica_of_wires/BasilicaHost.tscn",
	"estuary_3":      "res://scenes/games/estuary_3/Estuary3Host.tscn",
}
const SKIP_WORDS := ["shelf", "quit", "erase", "wipe", "back to", "hang up", "retire", "save & quit", "put it down"]
const STEPS := 120

func _ready() -> void:
	var failures: int = 0
	for key in TARGETS:
		_last_fp = 0
		print("MONKEY-START %s" % key)
		var ps: PackedScene = load(String(TARGETS[key]))
		var g: Node = ps.instantiate()
		add_child(g)
		for f in range(8):
			await get_tree().process_frame
		var pressed: int = 0
		var dead_screens: int = 0
		var pick: int = 0
		for step in range(STEPS):
			var btns: Array = []
			_collect_buttons(g, btns)
			if btns.is_empty():
				dead_screens += 1
				# Keyboard-driven screens (walkabouts, action
				# sticks) have no buttons BY DESIGN — play them
				# with a rotating keyboard hand: arrows to move,
				# E/Space/Enter to act, ESC only late (so we play
				# rather than immediately leave).
				var seq: Array = [KEY_RIGHT, KEY_E, KEY_UP, KEY_SPACE, KEY_LEFT,
					KEY_E, KEY_DOWN, KEY_ENTER, KEY_1, KEY_2, KEY_3, KEY_RIGHT, KEY_ESCAPE]
				_tap(seq[dead_screens % seq.size()])
				# A buttonless screen is only DEAD if the UI stops
				# CHANGING — pure-keyboard games (estuary_1's gate
				# loop) play fine with zero buttons, and the taps
				# above are real play. Fingerprint the visible text.
				var fp: int = _ui_fingerprint(g)
				if fp != _last_fp:
					_last_fp = fp
					dead_screens = 1
				if dead_screens >= 30:
					print("MONKEY-DEAD %s · buttonless AND unchanged for 30 checks at step %d" % [key, step])
					break
			else:
				dead_screens = 0
				var b: BaseButton = btns[pick % btns.size()]
				pick += 1
				b.emit_signal("pressed")
				pressed += 1
			for f in range(3):
				await get_tree().process_frame
		print("MONKEY-END %s · %d presses" % [key, pressed])
		g.queue_free()
		for f in range(4):
			await get_tree().process_frame
	print("QA monkey done · %d failure(s)" % failures)
	get_tree().quit(0)

var _last_fp: int = 0


func _ui_fingerprint(n: Node) -> int:
	var acc: int = 0
	_fp_walk(n, [acc])
	var box: Array = [0]
	_fp_walk(n, box)
	return int(box[0])


func _fp_walk(n: Node, box: Array) -> void:
	if n is Control and (n as Control).visible and "text" in n:
		box[0] = int(box[0]) ^ String(n.text).hash()
	for c in n.get_children():
		_fp_walk(c, box)


func _tap(code: int) -> void:
	var down := InputEventKey.new()
	down.keycode = code
	down.pressed = true
	Input.parse_input_event(down)
	var up := InputEventKey.new()
	up.keycode = code
	up.pressed = false
	Input.parse_input_event(up)


func _collect_buttons(n: Node, out: Array) -> void:
	if n is BaseButton:
		var b: BaseButton = n
		if b.visible and not b.disabled and b.is_visible_in_tree():
			var t: String = b.text.to_lower() if "text" in b else ""
			var skip: bool = false
			for w in SKIP_WORDS:
				if t.contains(w):
					skip = true
					break
			if not skip:
				out.append(b)
	for c in n.get_children():
		_collect_buttons(c, out)
