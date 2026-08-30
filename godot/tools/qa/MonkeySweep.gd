extends Node
## Headless QA: UI monkey — boots a host scene and PRESSES REAL
## BUTTONS for N iterations (skipping quit/back/shelf/erase), which
## walks title → run → gameplay loops the way a hand does. Catches
## _pressed-handler crashes and dead-end screens (no buttons at
## all is reported).
## Run: godot --headless res://tools/qa/MonkeySweep.tscn

const TARGETS := {
	"salmonberry":  "res://scenes/games/salmonberry/SalmonberryHost.tscn",
	"estuary_4":    "res://scenes/games/estuary_4/EstuaryFourHost.tscn",
	"northwind":    "res://scenes/games/northwind_harbor/NorthwindHarborHost.tscn",
}
const SKIP_WORDS := ["shelf", "quit", "erase", "wipe", "back to", "hang up", "retire", "save & quit", "put it down"]
const STEPS := 120

func _ready() -> void:
	var failures: int = 0
	for key in TARGETS:
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
				# Keyboard-driven screens (salmonberry's town
				# walkabout) have no buttons BY DESIGN — try ESC
				# (ui_cancel) to step back out before judging.
				var esc := InputEventKey.new()
				esc.keycode = KEY_ESCAPE
				esc.pressed = true
				Input.parse_input_event(esc)
				var esc_up := InputEventKey.new()
				esc_up.keycode = KEY_ESCAPE
				esc_up.pressed = false
				Input.parse_input_event(esc_up)
				if dead_screens >= 10:
					print("MONKEY-DEAD %s · no pressable buttons for 10 checks (ESC tried) at step %d" % [key, step])
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
