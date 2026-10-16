extends Control
## THE CATALOG — the slowstick collector's shelf.
##
## The alternate-universe catalog lattice made visible: every cart on
## Olaf's shelf grouped by the STUDIO that (in-fiction) made it, with
## liner notes — year, genre, credits, a blurb — and a ✓ where the
## shelf has actually seen it. Cross-cart achievements at the foot.
## Deepens the Almanac's THE SHELF chapter (design direction #3).
##
## Read-only: play-detection + achievements reuse AlmanacState's
## predicate engine over OneironauticsTokens. Data: catalog.json.
## Pattern: Almanac/ProfilePanel — static build, ui group, Esc close.

const DATA_PATH := "res://resources/almanac/catalog.json"

const C_BG     := Color(0.024, 0.020, 0.014, 0.98)
const C_ACCENT := Color(0.95, 0.78, 0.40)
const C_TEXT   := Color(0.86, 0.80, 0.66)
const C_DIM    := Color(0.48, 0.45, 0.38)
const C_DONE   := Color(0.62, 0.90, 0.68)
const C_STUDIO := Color(0.80, 0.66, 0.92)

var _data: Dictionary = {}


static func build(parent: Node) -> Control:
	var panel := Control.new()
	panel.set_script(load("res://scenes/menu/CatalogShelf.gd"))
	panel.name = "CatalogShelf"
	return panel


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	var bank := get_node_or_null("/root/SFXBank")
	if bank: bank.play("menu_open", 0.7)
	if FileAccess.file_exists(DATA_PATH):
		var f := FileAccess.open(DATA_PATH, FileAccess.READ)
		var parsed: Variant = JSON.parse_string(f.get_as_text())
		f.close()
		if parsed is Dictionary:
			_data = parsed
	_build()


func _input(event: InputEvent) -> void:
	if event.is_action_pressed("menu_back") or \
			(event is InputEventKey and (event as InputEventKey).keycode == KEY_ESCAPE and event.pressed):
		queue_free()
		get_viewport().set_input_as_handled()


func _played(cart: Dictionary) -> bool:
	var pred: Variant = cart.get("played", null)
	if pred is Dictionary:
		return AlmanacState.predicate_met(pred)
	return false


func _build() -> void:
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 60)
	margin.add_theme_constant_override("margin_right", 60)
	margin.add_theme_constant_override("margin_top", 26)
	margin.add_theme_constant_override("margin_bottom", 22)
	add_child(margin)

	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 6)
	margin.add_child(col)

	var carts: Array = _data.get("carts", [])
	var played_n := 0
	for c in carts:
		if _played(c): played_n += 1

	var header := Label.new()
	header.text = "· THE CATALOG · Olaf's shelf, 1983–2048 ·"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 22)
	header.add_theme_color_override("font_color", C_ACCENT)
	col.add_child(header)

	var sub := Label.new()
	sub.text = "%d of %d carts booted   ·   eight studios, one shelf" % [played_n, carts.size()]
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub.add_theme_font_size_override("font_size", 12)
	sub.add_theme_color_override("font_color", C_DIM)
	col.add_child(sub)

	var rule := ColorRect.new()
	rule.color = Color(C_ACCENT.r, C_ACCENT.g, C_ACCENT.b, 0.3)
	rule.custom_minimum_size.y = 1
	col.add_child(rule)

	var scroll := ScrollContainer.new()
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	col.add_child(scroll)
	var body := VBoxContainer.new()
	body.add_theme_constant_override("separation", 12)
	body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(body)

	var studios: Dictionary = _data.get("studios", {})
	for sid_v in _data.get("studios_order", []):
		var sid := String(sid_v)
		var mine: Array = []
		for c_v in carts:
			if String((c_v as Dictionary).get("studio", "")) == sid:
				mine.append(c_v)
		if mine.is_empty(): continue
		mine.sort_custom(func(a, b): return int(a.get("year", 0)) < int(b.get("year", 0)))

		var st: Dictionary = studios.get(sid, {})
		var sh := Label.new()
		sh.text = "%s  ·  %s" % [String(st.get("name", sid)), String(st.get("city", ""))]
		sh.add_theme_font_size_override("font_size", 16)
		sh.add_theme_color_override("font_color", C_STUDIO)
		body.add_child(sh)
		var snote := Label.new()
		snote.text = "  " + String(st.get("note", ""))
		snote.add_theme_font_size_override("font_size", 11)
		snote.add_theme_color_override("font_color", C_DIM)
		snote.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		body.add_child(snote)

		for c_v in mine:
			_add_cart(body, c_v)

	# ── achievements ──
	var achs: Array = _data.get("achievements", [])
	if not achs.is_empty():
		var arule := ColorRect.new()
		arule.color = Color(C_ACCENT.r, C_ACCENT.g, C_ACCENT.b, 0.3)
		arule.custom_minimum_size.y = 1
		body.add_child(arule)
		var ah := Label.new()
		ah.text = "· CROSS-CART ·"
		ah.add_theme_font_size_override("font_size", 14)
		ah.add_theme_color_override("font_color", C_ACCENT)
		body.add_child(ah)
		for a_v in achs:
			var a: Dictionary = a_v
			var got: bool = AlmanacState.predicate_met(a.get("when", {})) if (a.get("when", null) is Dictionary) else false
			var al := Label.new()
			al.text = ("✦ " if got else "· ") + String(a.get("title", "")) + " — " + String(a.get("blurb", ""))
			al.add_theme_font_size_override("font_size", 12)
			al.add_theme_color_override("font_color", C_DONE if got else C_DIM)
			al.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			body.add_child(al)

	var close := Button.new()
	close.text = "  · close the drawer ·  "
	close.add_theme_font_size_override("font_size", 14)
	close.pressed.connect(func() -> void: queue_free())
	col.add_child(close)


func _add_cart(parent: Node, cart: Dictionary) -> void:
	var played := _played(cart)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 0)
	parent.add_child(box)

	var line := Label.new()
	line.text = "    %s %s  ·  %s  ·  %s" % [
		("✓" if played else "·"),
		String(cart.get("title", "?")),
		str(int(cart.get("year", 0))),
		String(cart.get("genre", "")),
	]
	line.add_theme_font_size_override("font_size", 14)
	line.add_theme_color_override("font_color", C_DONE if played else C_TEXT)
	box.add_child(line)

	var notes := Label.new()
	notes.text = "        " + String(cart.get("blurb", "")) + "   ( " + String(cart.get("credits", "")) + " )"
	notes.add_theme_font_size_override("font_size", 11)
	notes.add_theme_color_override("font_color", C_DIM)
	notes.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	box.add_child(notes)
