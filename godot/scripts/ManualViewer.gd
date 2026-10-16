extends Control
class_name ManualViewer
## Renders a game manual (res://resources/manuals/<id>.md) as an
## in-game overlay — the box copy readable from the couch.
##
## Small markdown subset, converted to BBCode: #/##/### headings,
## ---- rules, - lists, **bold**, *italic*, `code`, [text](link)
## flattened to text, and | tables via RichTextLabel's [table].
## Headings containing "spoiler" get a warning band so nobody
## scrolls into an ending by accident.
##
## ESC or the close button dismisses. Pad: stick/d-pad scrolls,
## B closes (ui_cancel). F4-compliant via add_to_group("ui").

signal closed

const C_PAPER := Color("ece4d0")
const C_INK   := Color("23282a")
const C_ACCENT := Color("c8a048")
const C_DIM   := Color("8a8478")
const C_WARN  := Color("b85c48")

var _scroll: ScrollContainer = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")


func boot(manual_path: String) -> void:
	var dim := ColorRect.new()
	dim.color = Color(0.02, 0.02, 0.02, 0.88)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)

	var panel := PanelContainer.new()
	panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	panel.offset_left = -470
	panel.offset_right = 470
	panel.offset_top = -330
	panel.offset_bottom = 330
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.10, 0.095, 0.085, 0.99)
	sb.border_color = C_ACCENT
	sb.set_border_width_all(1)
	sb.set_corner_radius_all(4)
	sb.set_content_margin_all(18)
	panel.add_theme_stylebox_override("panel", sb)
	add_child(panel)

	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 8)
	panel.add_child(col)

	_scroll = ScrollContainer.new()
	_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	col.add_child(_scroll)

	var body := RichTextLabel.new()
	body.bbcode_enabled = true
	body.fit_content = true
	body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body.custom_minimum_size = Vector2(880, 0)
	body.add_theme_color_override("default_color", C_PAPER)
	body.add_theme_font_size_override("normal_font_size", 14)
	body.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_scroll.add_child(body)

	var close := Button.new()
	close.text = "  · close the manual ·  "
	close.add_theme_font_size_override("font_size", 14)
	close.pressed.connect(_close)
	col.add_child(close)

	var f := FileAccess.open(manual_path, FileAccess.READ)
	if f == null:
		body.text = "the manual for this cartridge has gone missing from the box."
	else:
		body.text = _md_to_bbcode(f.get_as_text())
		f.close()
	var gm := get_node_or_null("/root/GamepadMgr")
	if gm != null and gm.has_method("focus_first"):
		gm.call_deferred("focus_first", col)


func _close() -> void:
	closed.emit()
	queue_free()


func _process(delta: float) -> void:
	# pad / key scroll while the manual is open
	if _scroll == null:
		return
	var dy: float = 0.0
	if Input.is_action_pressed("ui_down"):
		dy += 520.0 * delta
	if Input.is_action_pressed("ui_up"):
		dy -= 520.0 * delta
	if dy != 0.0:
		_scroll.scroll_vertical = int(_scroll.scroll_vertical + dy)


func _input(event: InputEvent) -> void:
	if not is_visible_in_tree():
		return
	if event.is_action_pressed("ui_cancel"):
		_close()
		get_viewport().set_input_as_handled()


# ─── markdown → bbcode ───────────────────────────────────────────

func _inline(t: String) -> String:
	t = t.replace("[", "[lb]")
	# links → just the text: [lb]text[lb-close](target) — after the
	# escape above, the original "[x](y)" reads "[lb]x](y)".
	var rx_link := RegEx.new()
	rx_link.compile("\\[lb\\]([^\\]]*)\\]\\([^)]*\\)")
	t = rx_link.sub(t, "$1", true)
	var rx_b := RegEx.new()
	rx_b.compile("\\*\\*([^*]+)\\*\\*")
	t = rx_b.sub(t, "[b]$1[/b]", true)
	var rx_i := RegEx.new()
	rx_i.compile("\\*([^*]+)\\*")
	t = rx_i.sub(t, "[i]$1[/i]", true)
	var rx_c := RegEx.new()
	rx_c.compile("`([^`]+)`")
	t = rx_c.sub(t, "[code]$1[/code]", true)
	return t


func _md_to_bbcode(md: String) -> String:
	var out := PackedStringArray()
	var table_rows: Array = []

	for raw_v in md.split("\n"):
		var line := String(raw_v)
		var stripped := line.strip_edges()

		# table collection — runs of "| ... |" rows become [table]
		if stripped.begins_with("|"):
			var cells := PackedStringArray()
			for c in stripped.split("|"):
				var cs := String(c).strip_edges()
				if cs != "":
					cells.append(cs)
			# skip the |---|---| separator row
			var is_sep := true
			for c2 in cells:
				if String(c2).lstrip("-: ").rstrip("-: ") != "":
					is_sep = false
					break
			if not is_sep and cells.size() > 0:
				table_rows.append(cells)
			continue
		elif not table_rows.is_empty():
			out.append(_flush_table(table_rows))
			table_rows = []

		if stripped.begins_with("### "):
			out.append("[color=%s]%s[/color]" % [C_DIM.to_html(false), _inline(stripped.substr(4))])
		elif stripped.begins_with("## "):
			var h := stripped.substr(3)
			if h.to_lower().find("spoiler") >= 0:
				out.append("\n[color=%s]────────  SPOILERS BELOW THIS LINE  ────────[/color]" % C_WARN.to_html(false))
			out.append("\n[font_size=19][color=%s]%s[/color][/font_size]" % [C_ACCENT.to_html(false), _inline(h)])
		elif stripped.begins_with("# "):
			out.append("[font_size=26][color=%s]%s[/color][/font_size]" % [C_ACCENT.to_html(false), _inline(stripped.substr(2))])
		elif stripped.begins_with("---"):
			out.append("[color=%s]────────────────────────────────[/color]" % C_DIM.to_html(false))
		elif stripped.begins_with("- "):
			out.append("   •  " + _inline(stripped.substr(2)))
		else:
			out.append(_inline(line))

	if not table_rows.is_empty():
		out.append(_flush_table(table_rows))
	return "\n".join(out)


func _flush_table(rows: Array) -> String:
	var cols: int = (rows[0] as PackedStringArray).size()
	var t := "[table=%d]" % cols
	var first := true
	for r_v in rows:
		var r: PackedStringArray = r_v
		for i in range(cols):
			var cell := _inline(String(r[i]) if i < r.size() else "")
			if first:
				cell = "[b]%s[/b]" % cell
			t += "[cell]%s   [/cell]" % cell
		first = false
	t += "[/table]"
	return t
