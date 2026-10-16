extends Control
## DiscoveriesPanel — small "wait, there's more" affordance.
##
## Three states:
##   1. invisible (no cipher reveals yet — preserves the gallery's
##      "innocuous" first impression),
##   2. pill (lit gold pill in the Gallery header showing the live
##      count of discoveries — appears the moment the first cipher
##      reveals),
##   3. expanded (clicking the pill drops a small scrollable list of
##      what's been found, grouped by card).
##
## Walks every res://resources/puzzle_hooks/*.json on demand to
## enumerate which ciphers the SaveSystem has marked as unlocked,
## so it surfaces content without each card needing to register.

const HOOKS_DIR := "res://resources/puzzle_hooks/"
const C_BG := Color(0.020, 0.012, 0.018, 0.96)
const C_GOLD := Color(0.85, 0.66, 0.29)
const C_GOLD_HI := Color(1.0, 0.85, 0.40)
const C_TEXT := Color(0.85, 0.72, 0.50)
const C_TEXT_DIM := Color(0.52, 0.40, 0.22)

var _pill_btn: Button
var _list_panel: PanelContainer = null
var _list_vbox: VBoxContainer = null
var _expanded: bool = false
var _count_cache: int = 0


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_PASS
	# The pill is the visible footprint for the HBoxContainer layout.
	custom_minimum_size = Vector2(160, 24)
	_build_pill()
	_refresh_count()
	if not SaveSystem.unlocked_changed.is_connected(_on_unlock):
		SaveSystem.unlocked_changed.connect(_on_unlock)


func _build_pill() -> void:
	_pill_btn = Button.new()
	_pill_btn.flat = false
	_pill_btn.text = "+0  DISCOVERIES"
	_pill_btn.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_pill_btn.add_theme_color_override("font_color", C_GOLD_HI)
	_pill_btn.add_theme_font_size_override("font_size", 12)
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(C_GOLD.r * 0.35, C_GOLD.g * 0.25, C_GOLD.b * 0.18, 0.50)
	sb.border_color = C_GOLD
	sb.set_border_width_all(1)
	sb.corner_radius_top_left = 11
	sb.corner_radius_top_right = 11
	sb.corner_radius_bottom_left = 11
	sb.corner_radius_bottom_right = 11
	_pill_btn.add_theme_stylebox_override("normal", sb)
	var sbh := sb.duplicate() as StyleBoxFlat
	sbh.bg_color = Color(C_GOLD.r * 0.55, C_GOLD.g * 0.40, C_GOLD.b * 0.28, 0.70)
	sbh.border_color = C_GOLD_HI
	_pill_btn.add_theme_stylebox_override("hover", sbh)
	_pill_btn.pressed.connect(_toggle_expanded)
	_pill_btn.visible = false
	_pill_btn.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	add_child(_pill_btn)


func _on_unlock(_key: String) -> void:
	_refresh_count()
	if _expanded:
		_populate_list()


func _refresh_count() -> void:
	var entries := _enumerate_discoveries()
	_count_cache = entries.size()
	if _count_cache <= 0:
		_pill_btn.visible = false
		return
	if not _pill_btn.visible:
		# First-time reveal — slide in with a soft fade.
		_pill_btn.visible = true
		_pill_btn.modulate.a = 0.0
		var tw := create_tween()
		tw.tween_property(_pill_btn, "modulate:a", 1.0, 0.5)
	_pill_btn.text = "+%d  DISCOVERIES" % _count_cache


func _toggle_expanded() -> void:
	_expanded = not _expanded
	if _expanded:
		_ensure_list_panel()
		_populate_list()
		_list_panel.visible = true
		_list_panel.modulate.a = 0.0
		var tw := create_tween()
		tw.tween_property(_list_panel, "modulate:a", 1.0, 0.18)
	elif _list_panel != null:
		_list_panel.visible = false


func _ensure_list_panel() -> void:
	if _list_panel != null and is_instance_valid(_list_panel):
		return
	_list_panel = PanelContainer.new()
	# Float as a popup-style overlay (top_level decouples from the
	# HBoxContainer layout the pill lives inside).
	_list_panel.top_level = true
	_list_panel.custom_minimum_size = Vector2(340, 0)
	var sb := StyleBoxFlat.new()
	sb.bg_color = C_BG
	sb.border_color = C_GOLD
	sb.set_border_width_all(1)
	_list_panel.add_theme_stylebox_override("panel", sb)
	add_child(_list_panel)
	# Position it just below the pill, biased toward the right edge.
	var pill_global := _pill_btn.global_position + Vector2(_pill_btn.size.x, _pill_btn.size.y)
	_list_panel.global_position = pill_global - Vector2(340, 0) + Vector2(0, 6)
	var scroll := ScrollContainer.new()
	scroll.custom_minimum_size = Vector2(340, 360)
	_list_panel.add_child(scroll)
	_list_vbox = VBoxContainer.new()
	_list_vbox.add_theme_constant_override("separation", 8)
	_list_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(_list_vbox)


func _populate_list() -> void:
	if _list_vbox == null:
		return
	for c in _list_vbox.get_children():
		c.queue_free()
	var entries := _enumerate_discoveries()
	# Group by card.
	var by_card: Dictionary = {}
	for e in entries:
		var card_id: String = e.card_id
		if not by_card.has(card_id):
			by_card[card_id] = []
		by_card[card_id].append(e)
	var cards := by_card.keys()
	cards.sort()
	for card_id in cards:
		var head := Label.new()
		head.text = card_id.to_upper()
		head.add_theme_color_override("font_color", C_GOLD_HI)
		head.add_theme_font_size_override("font_size", 12)
		_list_vbox.add_child(head)
		for entry in by_card[card_id]:
			var row := VBoxContainer.new()
			row.add_theme_constant_override("separation", 2)
			var title := Label.new()
			title.text = "  ▷ " + str(entry.title)
			title.add_theme_color_override("font_color", C_TEXT)
			title.add_theme_font_size_override("font_size", 12)
			title.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			title.custom_minimum_size.x = 300
			row.add_child(title)
			if entry.text != "":
				var t := Label.new()
				t.text = "      " + entry.text
				t.add_theme_color_override("font_color", C_TEXT_DIM)
				t.add_theme_font_size_override("font_size", 12)
				t.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
				t.custom_minimum_size.x = 300
				row.add_child(t)
			_list_vbox.add_child(row)


# Walk all hooks JSONs and return one Dictionary per revealed cipher.
# Entry shape: {card_id, cipher_id, title, text, key}.
func _enumerate_discoveries() -> Array:
	var out: Array = []
	var dir := DirAccess.open(HOOKS_DIR)
	if dir == null:
		return out
	dir.list_dir_begin()
	var fname := dir.get_next()
	while fname != "":
		if not dir.current_is_dir() and fname.ends_with(".json"):
			var card_id: String = fname.get_basename()
			var path := HOOKS_DIR + fname
			var f := FileAccess.open(path, FileAccess.READ)
			if f != null:
				var data: Variant = JSON.parse_string(f.get_as_text())
				f.close()
				if typeof(data) == TYPE_DICTIONARY and data.has("ciphers"):
					for c_v in data["ciphers"]:
						var c: Dictionary = c_v
						var reveals := str(c.get("reveals", ""))
						if reveals == "":
							continue
						if not SaveSystem.is_unlocked(reveals):
							continue
						var text := str(c.get("text", ""))
						if text == "" and c.has("text_lines"):
							var lines := PackedStringArray()
							for line_v in c["text_lines"]:
								lines.append(str(line_v))
							text = " / ".join(lines)
						# Truncate long text to keep the panel scannable.
						if text.length() > 110:
							text = text.substr(0, 107) + "…"
						out.append({
							"card_id": card_id,
							"cipher_id": str(c.get("id", "")),
							"title": str(c.get("kind", c.get("id", ""))),
							"text": text,
							"key": reveals,
						})
		fname = dir.get_next()
	return out
