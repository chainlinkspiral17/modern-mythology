extends Node
## Boot node for the slowstock library flow.
##
## Launches SlowstockShelf; on `picked(stick_id)` swaps the shelf
## for the Estuary3Host (for estuary_3) or a placeholder-boot
## screen (for authored stubs). On host `quit_to_shelf` or
## `finished` returns to the shelf.
##
## Testable as a top-level scene · double-click SlowstockBoot.tscn
## in the Godot editor to run just the shelf → host loop without
## going through the main menu.

const SHELF_SCENE := "res://scenes/games/estuary_3/SlowstockShelf.tscn"
const HOST_SCENE  := "res://scenes/games/estuary_3/Estuary3Host.tscn"

var _shelf: Node = null
var _host: Node = null
var _stub_screen: Node = null


func _ready() -> void:
	_open_shelf()


func _open_shelf() -> void:
	if _host != null:
		_host.queue_free()
		_host = null
	if _stub_screen != null:
		_stub_screen.queue_free()
		_stub_screen = null
	_shelf = load(SHELF_SCENE).instantiate()
	_shelf.picked.connect(_on_picked)
	_shelf.closed.connect(_on_closed)
	add_child(_shelf)


func _open_host_estuary_3() -> void:
	if _shelf != null:
		_shelf.queue_free()
		_shelf = null
	_host = load(HOST_SCENE).instantiate()
	_host.quit_to_shelf.connect(_open_shelf)
	_host.finished.connect(_on_host_finished)
	add_child(_host)
	# Fresh run for the scaffold; a later commit will surface
	# "continue" vs "new run" on the shelf itself.
	_host.call_deferred("start_new_run")


func _open_stub_screen(stick_id: String) -> void:
	# For authored-stub sticks (Estuary 2, Pirate Summer, Mrs Wu's
	# Garden, Kwik Stop Manager, Estuary 1), show a small "authored
	# but not yet playable" acknowledgment screen with a BACK button.
	if _shelf != null:
		_shelf.queue_free()
		_shelf = null
	_stub_screen = Control.new()
	_stub_screen.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_stub_screen.add_to_group("ui")

	var bg := ColorRect.new()
	bg.color = Color(0.024, 0.020, 0.014, 0.97)
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_stub_screen.add_child(bg)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -220
	v.offset_right = 220
	v.offset_top = -80
	v.offset_bottom = 80
	v.add_theme_constant_override("separation", 12)
	_stub_screen.add_child(v)

	var title := Label.new()
	title.text = "%s · AUTHORED · NOT YET PLAYABLE" % stick_id.to_upper().replace("_", " ")
	title.add_theme_font_size_override("font_size", 12)
	title.add_theme_color_override("font_color", Color(0.78, 0.66, 0.29, 1))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(title)

	var body := Label.new()
	body.text = "This stick is on the shelf. Its manifest is authored — cover blurb, back-of-case, prior-owner note. Playable acts are a follow-up commit.\n\nUnlock it, know it exists, come back when it's live."
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.add_theme_font_size_override("font_size", 10)
	body.add_theme_color_override("font_color", Color(0.83, 0.79, 0.69, 1))
	body.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(body)

	var back := Button.new()
	back.text = "  ← back to shelf  "
	back.pressed.connect(_open_shelf)
	v.add_child(back)

	add_child(_stub_screen)


# ─── Signals from children ───────────────────────────────────────

func _on_picked(stick_id: String) -> void:
	if stick_id == "estuary_3":
		_open_host_estuary_3()
	else:
		_open_stub_screen(stick_id)


func _on_closed() -> void:
	# From the shelf's dim-click or Escape. In the standalone
	# SlowstockBoot flow there is no parent to return to, so we
	# just re-open the shelf.
	_open_shelf()


func _on_host_finished(canon_vars: Dictionary, lore_tokens: Array) -> void:
	# Merge into GauntletState if it's present (the autoload might
	# not be registered in every test-scene setup).
	var gs := get_node_or_null("/root/GauntletState")
	if gs != null:
		var st: Variant = gs.get("state")
		if st is Dictionary:
			var d: Dictionary = st
			var cv: Dictionary = d.get("canon_vars", {})
			for k in canon_vars.keys():
				cv[String(k)] = canon_vars[k]
			d["canon_vars"] = cv
			var lt: Array = d.get("lore_tokens_revealed", [])
			for t in lore_tokens:
				if not lt.has(String(t)):
					lt.append(String(t))
			d["lore_tokens_revealed"] = lt
			var sf: Array = d.get("slowsticks_finished", [])
			if not sf.has("estuary_3"):
				sf.append("estuary_3")
			d["slowsticks_finished"] = sf
			if gs.has_method("_save"):
				gs.call("_save")
	_open_shelf()
