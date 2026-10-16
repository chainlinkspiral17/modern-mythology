extends Node
## One-off probe: replay the monkey's path into Salmonberry and
## DUMP the UI tree when the dead screen appears.
func _ready() -> void:
	var ps: PackedScene = load("res://scenes/games/salmonberry/SalmonberryHost.tscn")
	var g: Node = ps.instantiate()
	add_child(g)
	for f in range(8):
		await get_tree().process_frame
	var pick: int = 0
	for step in range(40):
		var btns: Array = []
		_collect(g, btns)
		var labels: Array = []
		for b in btns:
			labels.append(String(b.text).strip_edges().left(28))
		print("STEP %02d · %d buttons · %s" % [step, btns.size(), str(labels)])
		if btns.is_empty():
			print("── DEAD SCREEN · dumping visible controls:")
			_dump(g, 0)
			break
		var b2: BaseButton = btns[pick % btns.size()]
		pick += 1
		print("   pressing: '%s'" % String(b2.text).strip_edges().left(40))
		b2.emit_signal("pressed")
		for f in range(3):
			await get_tree().process_frame
	get_tree().quit(0)

func _collect(n: Node, out: Array) -> void:
	if n is BaseButton and n.visible and not n.disabled and n.is_visible_in_tree():
		var t: String = String(n.text).to_lower()
		for w in ["shelf", "quit", "erase", "wipe", "back to", "hang up", "retire", "put it down"]:
			if t.contains(w):
				return
		out.append(n)
	for c in n.get_children():
		_collect(c, out)

func _dump(n: Node, depth: int) -> void:
	if depth > 6: return
	if n is Control and n.visible:
		var txt: String = ""
		if "text" in n:
			txt = " '" + String(n.text).strip_edges().left(40) + "'"
		print("%s%s%s" % ["  ".repeat(depth), n.get_class(), txt])
	for c in n.get_children():
		_dump(c, depth + 1)
