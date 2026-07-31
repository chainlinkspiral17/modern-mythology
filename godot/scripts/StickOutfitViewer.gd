extends Control
## THE OUTFIT · the shared SPEND screen for the StickLoop contract.
##
## One screen, reused by every slowstick that ships a loadout.json.
## It is opened from the shelf's info card (the OUTFIT button appears
## on any cartridge that has a loadout) and it is where a run's
## earnings visibly become the next run's options — the middle link
## of earn → spend → carry.
##
## Deliberately not a stat sheet. Each row leads with the object's
## NAME and the sentence about what it changes in play; the cost is
## the small print. A locked row says exactly what unlocks it, so the
## screen doubles as the roadmap for the stick.
##
## Layout is containers only, top to bottom — no hand-placed pixels
## (see the 2026-07-30 sweep; that mistake broke five screens).
##
## Usage:
##   var v = preload("res://scripts/StickOutfitViewer.gd").new()
##   add_child(v)
##   v.boot("sisters_wyrd", "THE SISTERS WYRD")
##   v.closed.connect(...)

signal closed

const C_INK    := Color(0.043, 0.039, 0.031, 0.97)
const C_PANEL  := Color(0.106, 0.094, 0.075, 1.0)
const C_BONE   := Color(0.910, 0.867, 0.769, 1.0)
const C_DIM    := Color(0.549, 0.518, 0.443, 1.0)
const C_GOLD   := Color(0.859, 0.729, 0.365, 1.0)
const C_LOCK   := Color(0.412, 0.384, 0.337, 1.0)
const C_OWNED  := Color(0.545, 0.769, 0.588, 1.0)

var _stick_id: String = ""
var _title: String = ""
var _rows_box: VBoxContainer = null
var _purse: Label = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")          # F4 master-toggle sweep (CLAUDE.md)
	z_index = 180


func boot(stick_id: String, display_title: String = "") -> void:
	_stick_id = stick_id
	_title = display_title if display_title != "" else stick_id.to_upper()
	_build()


func _build() -> void:
	for c in get_children():
		c.queue_free()

	var dim := ColorRect.new()
	dim.color = C_INK
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(dim)

	var panel := PanelContainer.new()
	var st := StyleBoxFlat.new()
	st.bg_color = C_PANEL
	st.border_color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.55)
	st.set_border_width_all(1)
	st.set_corner_radius_all(3)
	st.set_content_margin_all(20)
	panel.add_theme_stylebox_override("panel", st)
	panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	panel.offset_left = 90
	panel.offset_right = -90
	panel.offset_top = 48
	panel.offset_bottom = -48
	add_child(panel)

	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 10)
	panel.add_child(col)

	var head := Label.new()
	head.text = "· THE OUTFIT · %s ·" % _title
	head.add_theme_font_size_override("font_size", 19)
	head.add_theme_color_override("font_color", C_GOLD)
	col.add_child(head)

	_purse = Label.new()
	_purse.add_theme_font_size_override("font_size", 14)
	_purse.add_theme_color_override("font_color", C_BONE)
	col.add_child(_purse)

	var earn := Label.new()
	earn.text = StickLoop.earn_line(_stick_id)
	earn.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	earn.add_theme_font_size_override("font_size", 12)
	earn.add_theme_color_override("font_color", C_DIM)
	col.add_child(earn)

	var rule := ColorRect.new()
	rule.color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.28)
	rule.custom_minimum_size = Vector2(0, 1)
	col.add_child(rule)

	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	col.add_child(scroll)
	_rows_box = VBoxContainer.new()
	_rows_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_rows_box.add_theme_constant_override("separation", 8)
	scroll.add_child(_rows_box)

	var back := Button.new()
	back.text = "  · back to the shelf ·  "
	back.add_theme_font_size_override("font_size", 14)
	back.focus_mode = Control.FOCUS_ALL
	back.pressed.connect(_close)
	col.add_child(back)

	_refresh()


func _refresh() -> void:
	if _purse != null:
		_purse.text = "%s %d   ·   rides finished: %d" % [
			StickLoop.currency_name(_stick_id),
			StickLoop.credit(_stick_id),
			StickLoop.mastery(_stick_id)]
	if _rows_box == null:
		return
	for c in _rows_box.get_children():
		_rows_box.remove_child(c)
		c.queue_free()
	var rows: Array = StickLoop.catalog(_stick_id)
	if rows.is_empty():
		var none := Label.new()
		none.text = "nothing to outfit yet."
		none.add_theme_color_override("font_color", C_DIM)
		_rows_box.add_child(none)
		return
	var last_tier := -1
	for r_v in rows:
		var r: Dictionary = r_v
		var tier: int = int(r.get("tier", 1))
		if tier != last_tier:
			last_tier = tier
			var band := Label.new()
			band.text = "· tier %d ·" % tier
			band.add_theme_font_size_override("font_size", 12)
			band.add_theme_color_override("font_color", C_DIM)
			_rows_box.add_child(band)
		_rows_box.add_child(_make_row(r))


func _make_row(r: Dictionary) -> Control:
	var owned: bool = bool(r.get("owned", false))
	var buyable: bool = bool(r.get("buyable", false))

	var box := PanelContainer.new()
	var st := StyleBoxFlat.new()
	st.bg_color = Color(0.0, 0.0, 0.0, 0.28)
	st.border_color = C_OWNED if owned else (
			Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.4) if buyable
			else Color(C_LOCK.r, C_LOCK.g, C_LOCK.b, 0.5))
	st.set_border_width_all(1)
	st.set_corner_radius_all(2)
	st.set_content_margin_all(10)
	box.add_theme_stylebox_override("panel", st)

	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 14)
	box.add_child(row)

	var text_col := VBoxContainer.new()
	text_col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	text_col.add_theme_constant_override("separation", 3)
	row.add_child(text_col)

	var name_lbl := Label.new()
	name_lbl.text = String(r.get("name", ""))
	name_lbl.add_theme_font_size_override("font_size", 15)
	name_lbl.add_theme_color_override("font_color",
			C_OWNED if owned else (C_BONE if buyable else C_LOCK))
	text_col.add_child(name_lbl)

	var blurb := Label.new()
	blurb.text = String(r.get("blurb", ""))
	blurb.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	blurb.add_theme_font_size_override("font_size", 13)
	blurb.add_theme_color_override("font_color", C_DIM if not owned else C_BONE)
	text_col.add_child(blurb)

	# The reason a row is closed is the roadmap — always say it.
	var reason := String(r.get("reason", ""))
	if not owned and reason != "":
		var why := Label.new()
		why.text = "· " + reason + " ·"
		why.add_theme_font_size_override("font_size", 12)
		why.add_theme_color_override("font_color", C_LOCK)
		text_col.add_child(why)

	var act := Button.new()
	act.custom_minimum_size = Vector2(150, 36)
	act.focus_mode = Control.FOCUS_ALL
	act.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	if owned:
		act.text = "  CARRIED  "
		act.disabled = true
	else:
		act.text = "  %d %s  " % [int(r.get("cost", 0)),
				StickLoop.currency_name(_stick_id)]
		act.disabled = not buyable
		var uid := String(r.get("id", ""))
		act.pressed.connect(func() -> void: _buy(uid))
	row.add_child(act)
	return box


func _buy(upgrade_id: String) -> void:
	if not StickLoop.buy(_stick_id, upgrade_id):
		return
	var sb := get_node_or_null("/root/SFXBank")
	if sb != null and sb.has_method("play"):
		sb.play("coin", 0.8)
	_refresh()


func _close() -> void:
	closed.emit()
	queue_free()


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed \
			and (event as InputEventKey).keycode == KEY_ESCAPE:
		get_viewport().set_input_as_handled()
		_close()
