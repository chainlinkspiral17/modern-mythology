extends Control
## Fey Faire · The Gate · scaffold pass.
##
## Player has completed the boot questionnaire.  Ondine's ring-toss
## booth is here.  Cricket is at the ticket-counter.  This scene
## renders the arrival as a text-forward vignette · a specific
## welcome from Cricket, a specific offer from Ondine, then a menu
## with the six navigable directions (explore midway is stubbed).
##
## Currently text-only.  First-person grid rendering is a later
## commit.  Answers from the questionnaire (received via boot(state))
## surface in specific ways in Cricket's greeting.
##
## F4-compliant via add_to_group("ui").

signal quit_to_shelf

const C_BG        := Color(0.157, 0.094, 0.173, 1.0)   # black-plum
const C_PANEL     := Color(0.455, 0.157, 0.282, 1.0)   # dark plum
const C_CREAM     := Color(0.957, 0.878, 0.816, 1.0)
const C_ROSE      := Color(0.878, 0.722, 0.753, 1.0)
const C_MAUVE     := Color(0.784, 0.557, 0.643, 1.0)
const C_GOLD      := Color(0.973, 0.784, 0.282, 1.0)
const C_GOLD_DIM  := Color(0.541, 0.361, 0.157, 1.0)
const C_DIM       := Color(0.42, 0.34, 0.30, 1.0)

var _state: Dictionary = {}


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")


func boot(state: Dictionary) -> void:
	_state = state
	_render()


func _render() -> void:
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# Mauve tent-stripe hint at top (evocative · not first-person)
	for x in range(60, 1280, 90):
		var stripe := ColorRect.new()
		stripe.color = C_MAUVE
		stripe.set_anchors_preset(Control.PRESET_TOP_LEFT)
		stripe.position = Vector2(x, 0)
		stripe.size = Vector2(6, 40)
		add_child(stripe)

	var header := Label.new()
	header.text = "· THE GATE ·"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 16)
	header.add_theme_color_override("font_color", C_GOLD)
	header.set_anchors_preset(Control.PRESET_TOP_WIDE)
	header.offset_top = 60
	header.offset_bottom = 88
	add_child(header)

	# Panel · Cricket's greeting
	var panel := ColorRect.new()
	panel.color = C_PANEL
	panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	panel.offset_left = -400
	panel.offset_right = 400
	panel.offset_top = -240
	panel.offset_bottom = 240
	add_child(panel)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -380
	v.offset_right = 380
	v.offset_top = -220
	v.offset_bottom = 220
	v.add_theme_constant_override("separation", 14)
	add_child(v)

	# Cricket greeting
	var cricket_speaker := Label.new()
	cricket_speaker.text = "CRICKET, at the ticket-counter"
	cricket_speaker.add_theme_font_size_override("font_size", 10)
	cricket_speaker.add_theme_color_override("font_color", C_GOLD_DIM)
	v.add_child(cricket_speaker)

	var cricket_line := RichTextLabel.new()
	cricket_line.bbcode_enabled = false
	cricket_line.fit_content = true
	cricket_line.custom_minimum_size = Vector2(720, 40)
	cricket_line.add_theme_font_size_override("normal_font_size", 12)
	cricket_line.add_theme_color_override("default_color", C_CREAM)
	var player_name: String = String(_state.get("player_name", "you"))
	cricket_line.text = "" + player_name + ".  Your ticket."
	v.add_child(cricket_line)

	var beat := Control.new()
	beat.custom_minimum_size = Vector2(0, 4)
	v.add_child(beat)

	# Ondine's offer
	var ondine_speaker := Label.new()
	ondine_speaker.text = "ONDINE, at the ring-toss booth"
	ondine_speaker.add_theme_font_size_override("font_size", 10)
	ondine_speaker.add_theme_color_override("font_color", C_GOLD_DIM)
	v.add_child(ondine_speaker)

	var ondine_line := RichTextLabel.new()
	ondine_line.bbcode_enabled = false
	ondine_line.fit_content = true
	ondine_line.custom_minimum_size = Vector2(720, 60)
	ondine_line.add_theme_font_size_override("normal_font_size", 12)
	ondine_line.add_theme_color_override("default_color", C_CREAM)
	ondine_line.text = "You get six nights.  This is not a metaphor."
	v.add_child(ondine_line)

	var beat2 := Control.new()
	beat2.custom_minimum_size = Vector2(0, 8)
	v.add_child(beat2)

	# What you brought
	var boot_item := String(_state.get("boot_inventory_item", ""))
	if boot_item != "":
		var inv_lbl := Label.new()
		inv_lbl.text = "· In your pocket: " + _boot_item_display(boot_item) + " ·"
		inv_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		inv_lbl.add_theme_font_size_override("font_size", 10)
		inv_lbl.add_theme_color_override("font_color", C_ROSE)
		v.add_child(inv_lbl)

	# Status line
	var status := Label.new()
	status.text = "· first-person midway rendering pending · content authored in feys.json (101 entries) ·"
	status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	status.add_theme_font_size_override("font_size", 9)
	status.add_theme_color_override("font_color", C_DIM)
	v.add_child(status)

	var beat3 := Control.new()
	beat3.custom_minimum_size = Vector2(0, 12)
	v.add_child(beat3)

	# Menu (stub · buttons for later)
	var directions := VBoxContainer.new()
	directions.add_theme_constant_override("separation", 6)
	v.add_child(directions)

	for label in ["enter the midway (pending)", "go to the trailer (pending)", "look at the Big Top (pending)", "leave through the Parking Lot (pending)"]:
		var btn := Button.new()
		btn.text = "  " + label + "  "
		btn.disabled = true
		btn.add_theme_font_size_override("font_size", 11)
		directions.add_child(btn)

	# Back
	var back := Button.new()
	back.text = "  ← back to shelf  "
	back.pressed.connect(_on_back_pressed)
	v.add_child(back)


func _boot_item_display(id: String) -> String:
	match id:
		"smooth_river_stone":  return "a smooth river stone"
		"grandmothers_ring":   return "your grandmother's ring"
		"first_kiss_note":     return "a folded note · nine words · three years old"
		"father_dog_tag":      return "your father's dog tag"
		"bookstore_receipt":   return "a used-bookstore receipt · six books"
		"photograph_home":     return "a photograph of someone you love"
		_: return "something"


func _on_back_pressed() -> void:
	quit_to_shelf.emit()


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			_on_back_pressed()
			get_viewport().set_input_as_handled()
