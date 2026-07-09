extends Control
## Fey Faire · midway navigation · text-forward booth graph.
##
## A hand-authored subset of the 48-cell midway map from
## _FEY_FAIRE_ROUTES.md · ~18 booth cells with adjacency edges.
## The player is always AT a specific cell.  Interact with the
## cell's booth-fey (opens the negotiation scene), OR move to an
## adjacent cell.
##
## First-person grid rendering is a follow-up commit; this is the
## text-forward version that surfaces the same content and adjacency
## structure so we can validate the map and playtest the content.
##
## Signals:
##   negotiate_with_fey(fey_id) · host opens negotiation scene
##   quit · returns to Gate
##
## F4-compliant via add_to_group("ui").

signal negotiate_with_fey(fey_id: String)
signal quit

const FEYS_PATH := "res://resources/games/vol7/fey_faire/feys.json"

# Rocha palette
const C_BG        := Color(0.157, 0.094, 0.173, 1.0)
const C_PANEL     := Color(0.455, 0.157, 0.282, 1.0)
const C_PANEL_DIM := Color(0.28, 0.10, 0.18, 1.0)
const C_CREAM     := Color(0.957, 0.878, 0.816, 1.0)
const C_ROSE      := Color(0.878, 0.722, 0.753, 1.0)
const C_MAUVE     := Color(0.784, 0.557, 0.643, 1.0)
const C_GOLD      := Color(0.973, 0.784, 0.282, 1.0)
const C_GOLD_DIM  := Color(0.541, 0.361, 0.157, 1.0)
const C_RECRUITED := Color(0.62, 0.82, 0.55, 1.0)

# Midway map · subset of the 48-cell layout · ~18 cells.
# Each cell: id, name, description, fey (or null if no booth),
# neighbors (adjacency).
const MIDWAY: Dictionary = {
	"gate": {
		"name": "THE GATE",
		"description": "Cricket's ticket-counter · cream and mauve striped canvas · Edison bulbs on strings overhead.",
		"fey": "cricket_the_cricket",
		"neighbors": ["midway_south", "parking_lot"]
	},
	"parking_lot": {
		"name": "THE PARKING LOT",
		"description": "Gravel · rows of parked cars · past the last row, past the generator shack, a specific Airstream trailer.",
		"fey": null,
		"neighbors": ["gate", "trailer_area"]
	},
	"trailer_area": {
		"name": "TRAILER GROUNDS",
		"description": "Prospero's Airstream sits on cinderblocks.  A specific cat watches you from the window.",
		"fey": null,
		"neighbors": ["parking_lot"],
		"leads_to_trailer": true
	},
	"midway_south": {
		"name": "MIDWAY · SOUTH END",
		"description": "The main promenade begins here.  Booths line either side.  A specific Boggart-run lost-and-found is at your right.",
		"fey": "boggart",
		"neighbors": ["gate", "midway_center", "ring_toss"]
	},
	"ring_toss": {
		"name": "RING TOSS BOOTH",
		"description": "The FIRST booth you noticed on your first night.  Cream and mauve stripes.  Behind the counter · Ondine.  Plush prizes hanging in a row that nobody has won in living memory.",
		"fey": "ondine",
		"neighbors": ["midway_south", "fountain_jump"]
	},
	"fountain_jump": {
		"name": "FOUNTAIN-JUMP BOOTH",
		"description": "A shallow pool of pennies · a wooden frog cutout painted green · nixies swimming in it.  Every third jump the water speaks your name back.",
		"fey": "nixie",
		"neighbors": ["ring_toss", "midway_center"]
	},
	"midway_center": {
		"name": "MIDWAY · CENTER",
		"description": "The heart of the promenade.  A specific Edison-bulb archway.  A carousel to the north, a coin-in-glass booth to the east, the cotton-candy wagon to the west.",
		"fey": null,
		"neighbors": ["midway_south", "carousel", "coin_glass", "cotton_candy", "midway_north"]
	},
	"carousel": {
		"name": "THE CAROUSEL",
		"description": "A specific hand-crank music-box tune plays as the wooden horses go round.  You do not know where you have heard the tune before.",
		"fey": null,
		"neighbors": ["midway_center", "funhouse"]
	},
	"coin_glass": {
		"name": "COIN-IN-A-GLASS BOOTH",
		"description": "An old man behind the counter demonstrates that if you slide the quarter down the ramp JUST SO it lands in the shot glass.  Two dollars for three tries.  Nobody wins.  He asks your name twice.",
		"fey": "puck",
		"neighbors": ["midway_center", "bookstall"]
	},
	"cotton_candy": {
		"name": "COTTON CANDY WAGON",
		"description": "A wagoneer in a paper hat.  Green overalls.  The wagon is not hooked to any truck.  Cotton candy stays with you longer than cotton candy should.",
		"fey": "green_man",
		"neighbors": ["midway_center", "popcorn"]
	},
	"popcorn": {
		"name": "POPCORN WAGON",
		"description": "A small hairy fellow in overalls pops corn in a tall glass box.  A dollar a bag.  Every bag has one popped kernel that's the color of blood.  It is not blood.",
		"fey": "hob_of_the_hedgerow",
		"neighbors": ["cotton_candy"]
	},
	"funhouse": {
		"name": "FUNHOUSE MIRROR MAZE",
		"description": "Nine mirrors that don't show what they should.  The attendant is in a rabbit costume.  You suspect the rabbit costume is not a costume.",
		"fey": "pooka",
		"neighbors": ["carousel", "sleep_tent"]
	},
	"sleep_tent": {
		"name": "MOTH'S QUIET · SLEEP TENT",
		"description": "Two adjacent tents.  MOTH'S QUIET is candlelit · Moth is inside, silent · she puts a moth on your palm.  The SLEEP TENT next door is darker · a specific fine linen bed · someone else is in it, in a dream.",
		"fey": "moth",
		"neighbors": ["funhouse", "midway_north"]
	},
	"bookstall": {
		"name": "THE BOOKSTALL",
		"description": "Used paperbacks stacked on wooden crates.  Two gold each.  A specific slim volume on the top shelf has your name on the cover.  It is not your name yet.",
		"fey": null,
		"neighbors": ["coin_glass", "midway_north"]
	},
	"midway_north": {
		"name": "MIDWAY · NORTH END",
		"description": "The Big Top rises here · striped in mauve and cream.  Nightly Shakespeare shows.  Backstage is locked (Night 4+).  To the east: the kissing booth and the wheel of fortune.",
		"fey": null,
		"neighbors": ["midway_center", "bookstall", "sleep_tent", "kissing_booth", "wheel_fortune", "big_top"]
	},
	"kissing_booth": {
		"name": "KISSING BOOTH",
		"description": "Deliberately old-fashioned.  Deliberately gothic.  She is in a long dark dress that touches the floor.  Sign: ONE DOLLAR · ONE KISS · ONE QUESTION.",
		"fey": "baobhan_sith",
		"neighbors": ["midway_north", "wheel_fortune"]
	},
	"wheel_fortune": {
		"name": "WHEEL OF FORTUNE",
		"description": "A tall painted wheel with sixteen sectors.  A gaunt man in a long grey coat spins it.  His crown is antler.  Sector 16 says CHILD.  Nobody has landed on Sector 16 in living memory.",
		"fey": "erlking",
		"neighbors": ["midway_north", "kissing_booth"]
	},
	"big_top": {
		"name": "THE BIG TOP · MAIN TENT",
		"description": "The nightly show is starting.  Cast varies · tonight's playbill reads A MIDSUMMER NIGHT'S DREAM.  Titania is playing herself.  Backstage locked.",
		"fey": null,
		"neighbors": ["midway_north"],
		"needs_night_4_for_backstage": true
	}
}

var _run_state: Dictionary = {}
var _feys_by_id: Dictionary = {}
var _current_cell: String = "midway_south"


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")


func boot(state: Dictionary) -> void:
	_run_state = state
	# Restore last cell if saved
	var saved_cell := String(_run_state.get("midway_cell", "midway_south"))
	if MIDWAY.has(saved_cell):
		_current_cell = saved_cell
	_load_feys()
	_render_current_cell()


func _load_feys() -> void:
	if not FileAccess.file_exists(FEYS_PATH): return
	var f := FileAccess.open(FEYS_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		for entry_v in (parsed as Dictionary).get("feys", []):
			var entry: Dictionary = entry_v
			_feys_by_id[String(entry.get("id", ""))] = entry


func _clear_children() -> void:
	for c in get_children():
		c.queue_free()


func _render_current_cell() -> void:
	_clear_children()
	_run_state["midway_cell"] = _current_cell

	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# Mauve tent-stripe hint · top
	for x in range(60, 1280, 90):
		var stripe := ColorRect.new()
		stripe.color = C_MAUVE
		stripe.set_anchors_preset(Control.PRESET_TOP_LEFT)
		stripe.position = Vector2(x, 0)
		stripe.size = Vector2(6, 30)
		add_child(stripe)

	var cell: Dictionary = MIDWAY[_current_cell]

	# Top: cell name
	var header := Label.new()
	header.text = "· " + String(cell.get("name", "?")) + " ·"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 16)
	header.add_theme_color_override("font_color", C_GOLD)
	header.set_anchors_preset(Control.PRESET_TOP_WIDE)
	header.offset_top = 46
	header.offset_bottom = 74
	add_child(header)

	# Central panel
	var panel := ColorRect.new()
	panel.color = C_PANEL
	panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	panel.offset_left = -420
	panel.offset_right = 420
	panel.offset_top = -240
	panel.offset_bottom = 240
	add_child(panel)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -400
	v.offset_right = 400
	v.offset_top = -220
	v.offset_bottom = 220
	v.add_theme_constant_override("separation", 10)
	add_child(v)

	# Description
	var desc := RichTextLabel.new()
	desc.bbcode_enabled = false
	desc.fit_content = true
	desc.text = String(cell.get("description", ""))
	desc.add_theme_font_size_override("normal_font_size", 12)
	desc.add_theme_color_override("default_color", C_CREAM)
	desc.custom_minimum_size = Vector2(0, 80)
	v.add_child(desc)

	# Booth-fey (if any)
	var fey_id: Variant = cell.get("fey", null)
	if fey_id != null and fey_id != "":
		var fey: Dictionary = _feys_by_id.get(String(fey_id), {})
		if not fey.is_empty():
			var recruited: Array = _run_state.get("recruited_feys", [])
			var is_recruited: bool = recruited.has(String(fey_id))
			var booth_row := HBoxContainer.new()
			booth_row.add_theme_constant_override("separation", 12)
			v.add_child(booth_row)

			var booth_lbl := Label.new()
			if is_recruited:
				booth_lbl.text = "✓ " + String(fey.get("name", fey_id)) + " · recruited · their booth is unattended"
				booth_lbl.add_theme_color_override("font_color", C_RECRUITED)
			else:
				booth_lbl.text = "· " + String(fey.get("name", fey_id)) + " · " + String(fey.get("court", "?")) + " · tier " + str(int(fey.get("tier", 1))) + " ·"
				booth_lbl.add_theme_color_override("font_color", C_ROSE)
			booth_lbl.add_theme_font_size_override("font_size", 11)
			booth_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			booth_row.add_child(booth_lbl)

			if not is_recruited:
				var interact_btn := Button.new()
				interact_btn.text = "  approach the booth  "
				interact_btn.add_theme_font_size_override("font_size", 11)
				interact_btn.add_theme_color_override("font_color", C_GOLD)
				interact_btn.pressed.connect(func() -> void: negotiate_with_fey.emit(String(fey_id)))
				booth_row.add_child(interact_btn)

	# Special-case: trailer link
	if bool(cell.get("leads_to_trailer", false)):
		var trailer_btn := Button.new()
		trailer_btn.text = "  ⌂  walk up to the trailer door  "
		trailer_btn.add_theme_font_size_override("font_size", 11)
		trailer_btn.add_theme_color_override("font_color", C_GOLD)
		trailer_btn.pressed.connect(_on_visit_trailer_pressed)
		v.add_child(trailer_btn)

	# Big Top backstage lock message
	if bool(cell.get("needs_night_4_for_backstage", false)):
		var night: int = int(_run_state.get("night", 1))
		var lock_lbl := Label.new()
		if night < 4:
			lock_lbl.text = "· backstage is locked · night " + str(night) + "/6 · Oberon holds court there from night 4 ·"
			lock_lbl.add_theme_color_override("font_color", C_GOLD_DIM)
		else:
			lock_lbl.text = "· backstage is open · Oberon is here ·"
			lock_lbl.add_theme_color_override("font_color", C_GOLD)
		lock_lbl.add_theme_font_size_override("font_size", 10)
		v.add_child(lock_lbl)

	var sep := Control.new()
	sep.custom_minimum_size = Vector2(0, 12)
	v.add_child(sep)

	# Directions
	var dir_header := Label.new()
	dir_header.text = "· FROM HERE ·"
	dir_header.add_theme_font_size_override("font_size", 10)
	dir_header.add_theme_color_override("font_color", C_GOLD_DIM)
	v.add_child(dir_header)

	var neighbors: Array = cell.get("neighbors", [])
	for n_id_v in neighbors:
		var n_id: String = String(n_id_v)
		if not MIDWAY.has(n_id): continue
		var n: Dictionary = MIDWAY[n_id]
		var btn := Button.new()
		var fey_hint: String = ""
		var n_fey: Variant = n.get("fey", null)
		if n_fey != null and n_fey != "":
			var f: Dictionary = _feys_by_id.get(String(n_fey), {})
			var r: Array = _run_state.get("recruited_feys", [])
			var checked: String = "✓" if r.has(String(n_fey)) else "·"
			fey_hint = "  (" + checked + " " + String(f.get("name", "?")) + ")"
		btn.text = "  →  " + String(n.get("name", n_id)) + fey_hint + "  "
		btn.add_theme_font_size_override("font_size", 11)
		btn.pressed.connect(func() -> void: _on_move_to(n_id))
		v.add_child(btn)

	var sep2 := Control.new()
	sep2.custom_minimum_size = Vector2(0, 12)
	v.add_child(sep2)

	# Back to gate
	var back_btn := Button.new()
	back_btn.text = "  ← return to the Gate  "
	back_btn.add_theme_font_size_override("font_size", 11)
	back_btn.pressed.connect(_on_back)
	v.add_child(back_btn)


func _on_move_to(cell_id: String) -> void:
	if not MIDWAY.has(cell_id): return
	_current_cell = cell_id
	_render_current_cell()


func _on_visit_trailer_pressed() -> void:
	# Emit a specific quit + set flag so host routes to trailer
	_run_state["_route_to_trailer"] = true
	quit.emit()


func _on_back() -> void:
	quit.emit()


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			_on_back()
			get_viewport().set_input_as_handled()
