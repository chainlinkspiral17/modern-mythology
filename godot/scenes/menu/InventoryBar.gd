extends Control
## InventoryBar — thin bottom-edge strip that surfaces the player's
## carried items. Added by TarotVisualizerBase to each visualizer.
##
## Visibility rule: collapsed (offscreen) when no items are carried,
## slides up the first time Inventory.item_added fires. Click a slot
## to show its blurb in a small popup. The cursor flips to CURSOR_USE
## (the "drag" / closed-hand) while an item is "armed" (held above a
## hotspot with a matching `requires_item`).
##
## The bar is intentionally small — 56 px tall, 32 px icons.

const BAR_HEIGHT := 56.0
const ICON_SIZE := 32.0
const COLLAPSE_OFFSET := BAR_HEIGHT + 12.0   # how far we sit offscreen
const C_BG := Color(0.020, 0.012, 0.018, 0.92)
const C_GOLD := Color(0.85, 0.66, 0.29)
const C_GOLD_HI := Color(1.0, 0.85, 0.40)
const C_INK := Color(0.06, 0.04, 0.06)

var _slots: Dictionary = {}    # item_id -> {btn, icon_rect}
var _row: HBoxContainer
var _frame: PanelContainer
var _label: Label
var _armed_item_id: String = ""
var _blurb_popup: PanelContainer = null
var _blurb_label: Label = null

signal item_armed(id: String)        # player clicked an item to use it
signal item_disarmed(id: String)


func _ready() -> void:
	set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	offset_top = -BAR_HEIGHT
	custom_minimum_size = Vector2(0, BAR_HEIGHT)
	mouse_filter = Control.MOUSE_FILTER_PASS

	_frame = PanelContainer.new()
	_frame.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var sb := StyleBoxFlat.new()
	sb.bg_color = C_BG
	sb.border_color = C_GOLD
	sb.border_width_top = 1
	_frame.add_theme_stylebox_override("panel", sb)
	_frame.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_frame)

	var pad := MarginContainer.new()
	pad.add_theme_constant_override("margin_left", 14)
	pad.add_theme_constant_override("margin_right", 14)
	pad.add_theme_constant_override("margin_top", 8)
	pad.add_theme_constant_override("margin_bottom", 8)
	_frame.add_child(pad)

	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 14)
	pad.add_child(hb)

	_label = Label.new()
	_label.text = "INVENTORY"
	_label.add_theme_color_override("font_color", C_GOLD)
	_label.add_theme_font_size_override("font_size", 12)
	_label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	hb.add_child(_label)

	_row = HBoxContainer.new()
	_row.add_theme_constant_override("separation", 6)
	_row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hb.add_child(_row)

	# Start collapsed offscreen — slide in on first add.
	position.y = COLLAPSE_OFFSET
	visible = (Inventory.count() > 0)
	if visible:
		position.y = 0
	Inventory.item_added.connect(_on_item_added)
	Inventory.item_removed.connect(_on_item_removed)
	# Populate any items already in the bag from prior sessions.
	for id_v in Inventory.all():
		_add_slot(str(id_v))


func _on_item_added(id: String) -> void:
	_add_slot(id)
	if not visible:
		visible = true
		position.y = COLLAPSE_OFFSET
		var tw := create_tween()
		tw.tween_property(self, "position:y", 0.0, 0.35) \
		.set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)


func _on_item_removed(id: String) -> void:
	if _slots.has(id):
		var btn: Button = _slots[id].btn
		if is_instance_valid(btn):
			btn.queue_free()
		_slots.erase(id)
	if _slots.is_empty():
		var tw := create_tween()
		tw.tween_property(self, "position:y", COLLAPSE_OFFSET, 0.25) \
		.set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN)
		tw.tween_callback(func() -> void: visible = false)


func _add_slot(id: String) -> void:
	if _slots.has(id):
		return
	var entry := Inventory.describe(id)
	var btn := Button.new()
	btn.flat = true
	btn.custom_minimum_size = Vector2(ICON_SIZE + 6, ICON_SIZE + 6)
	btn.tooltip_text = str(entry.get("name", id))
	btn.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0, 0, 0, 0)
	sb.border_color = C_GOLD
	sb.border_width_bottom = 1
	btn.add_theme_stylebox_override("normal", sb)
	var sbh := sb.duplicate() as StyleBoxFlat
	sbh.bg_color = Color(1.0, 0.85, 0.40, 0.10)
	sbh.border_color = C_GOLD_HI
	sbh.set_border_width_all(1)
	btn.add_theme_stylebox_override("hover", sbh)
	var sbp := sb.duplicate() as StyleBoxFlat
	sbp.bg_color = Color(1.0, 0.85, 0.40, 0.24)
	sbp.border_color = C_GOLD_HI
	sbp.set_border_width_all(2)
	btn.add_theme_stylebox_override("pressed", sbp)

	var icon_path: String = str(entry.get("icon", ""))
	if icon_path != "" and ResourceLoader.exists(icon_path):
		var tex: Texture2D = load(icon_path)
		if tex != null:
			btn.icon = tex
			btn.expand_icon = false
	if btn.icon == null:
		btn.text = str(entry.get("name", id)).substr(0, 2).to_upper()

	btn.pressed.connect(func() -> void: _on_slot_pressed(id))
	_row.add_child(btn)
	_slots[id] = {"btn": btn}


func _on_slot_pressed(id: String) -> void:
	# Toggle arm: clicking the slot arms the item (cursor flips to use
	# when over compatible hotspots); clicking it again disarms.
	if _armed_item_id == id:
		_armed_item_id = ""
		item_disarmed.emit(id)
		_show_blurb(id, " · DISARMED · ")
	else:
		var prior := _armed_item_id
		_armed_item_id = id
		if prior != "":
			item_disarmed.emit(prior)
		item_armed.emit(id)
		var entry := Inventory.describe(id)
		_show_blurb(id, str(entry.get("blurb", "")))


func armed_item() -> String:
	return _armed_item_id


# ── Blurb popup ────────────────────────────────────────────────────

func _show_blurb(_id: String, text: String) -> void:
	_ensure_blurb_popup()
	_blurb_label.text = text
	_blurb_popup.visible = true
	_blurb_popup.modulate.a = 0.0
	var tw := create_tween()
	tw.tween_property(_blurb_popup, "modulate:a", 1.0, 0.18)


func _ensure_blurb_popup() -> void:
	if _blurb_popup != null and is_instance_valid(_blurb_popup):
		return
	_blurb_popup = PanelContainer.new()
	_blurb_popup.set_anchors_preset(Control.PRESET_TOP_WIDE)
	_blurb_popup.offset_top = -56
	_blurb_popup.offset_left = 14
	_blurb_popup.offset_right = -14
	_blurb_popup.custom_minimum_size = Vector2(0, 48)
	var sb := StyleBoxFlat.new()
	sb.bg_color = C_INK
	sb.border_color = C_GOLD
	sb.set_border_width_all(1)
	_blurb_popup.add_theme_stylebox_override("panel", sb)
	var m := MarginContainer.new()
	m.add_theme_constant_override("margin_left", 10)
	m.add_theme_constant_override("margin_right", 10)
	m.add_theme_constant_override("margin_top", 6)
	m.add_theme_constant_override("margin_bottom", 6)
	_blurb_popup.add_child(m)
	_blurb_label = Label.new()
	_blurb_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_blurb_label.add_theme_color_override("font_color", Color(0.85, 0.72, 0.50))
	_blurb_label.add_theme_font_size_override("font_size", 12)
	m.add_child(_blurb_label)
	_blurb_popup.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_blurb_popup)
	_blurb_popup.visible = false
