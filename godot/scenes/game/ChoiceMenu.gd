extends Control
## Choice menu — the book's turning points, presented as a plate.
## Call setup(skin) once after instantiation, then present() per use.
##
## 2026-07 presentation wave 2: choices are the most important eight
## moments in vols 5-7 and looked like a stock button list at 13px on
## a near-opaque slab. Now: the scene dims but stays visible beneath a
## translucent scrim, and a centered column in the chapter-plate
## register (rule-diamond-rule ornaments, serif prompt, large centered
## options with a gold underline on hover/focus) carries the decision.
## Number keys still choose; pad focus still works; the staggered
## entrance remains. Public API unchanged.

var _skin:         Dictionary    = {}
var _callback:     Callable
var _vbox:         VBoxContainer = null
var _prompt_label: Label         = null
var _scrim:        ColorRect     = null
var _column:       VBoxContainer = null

const C_GOLD     := Color(0.85, 0.72, 0.35)
const C_GOLD_DIM := Color(0.78, 0.66, 0.29, 0.45)


func _ready() -> void:
	_build()


func setup(skin: Dictionary) -> void:
	_skin = skin
	if _scrim != null:
		# The scene stays visible under the decision — dimmed, not
		# blacked out. Skin's overlay color, alpha capped.
		var c: Color = skin.get("ov_bg", Color(0.04, 0.03, 0.02, 0.95))
		_scrim.color = Color(c.r, c.g, c.b, minf(c.a, 0.78))
	if _prompt_label != null:
		_prompt_label.add_theme_color_override("font_color",
			skin.get("hud_color", Color(0.93, 0.90, 0.83)))


func _build() -> void:
	_scrim = ColorRect.new()
	_scrim.color = Color(0.04, 0.03, 0.02, 0.78)
	_scrim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_scrim)

	_column = VBoxContainer.new()
	_column.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_column.custom_minimum_size = Vector2(780, 0)
	_column.offset_left = -390
	_column.offset_right = 390
	_column.alignment = BoxContainer.ALIGNMENT_CENTER
	_column.add_theme_constant_override("separation", 18)
	add_child(_column)

	_column.add_child(_ornament())

	_prompt_label = Label.new()
	_prompt_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_prompt_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	if ResourceLoader.exists(SkinDB.F_IMFELL_I):
		_prompt_label.add_theme_font_override("font", load(SkinDB.F_IMFELL_I) as Font)
	_prompt_label.add_theme_font_size_override("font_size", 22)
	_prompt_label.add_theme_color_override("font_color", Color(0.93, 0.90, 0.83))
	_column.add_child(_prompt_label)

	_vbox = VBoxContainer.new()
	_vbox.add_theme_constant_override("separation", 6)
	_column.add_child(_vbox)

	_column.add_child(_ornament())


func _ornament() -> Control:
	# rule — diamond — rule · the plate divider (InterludePanel register).
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	row.add_child(_rule())
	var d := Label.new()
	d.text = "◆"
	d.add_theme_font_size_override("font_size", 12)
	d.add_theme_color_override("font_color", C_GOLD_DIM)
	row.add_child(d)
	row.add_child(_rule())
	return row


func _rule() -> ColorRect:
	var r := ColorRect.new()
	r.color = Color(C_GOLD_DIM.r, C_GOLD_DIM.g, C_GOLD_DIM.b, 0.25)
	r.custom_minimum_size = Vector2(0, 1)
	r.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	r.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	return r


func present(prompt: String, opts: Array, callback: Callable) -> void:
	_callback = callback
	_prompt_label.text    = prompt
	_prompt_label.visible = prompt != ""

	# Remove stale options from the tree BEFORE building. queue_free
	# alone leaves the dying buttons as children until end of frame,
	# so get_child(0) below would grab a corpse for focus, and the
	# stagger loop / number keys would count them too.
	for child in _vbox.get_children():
		_vbox.remove_child(child)
		child.queue_free()

	for i in opts.size():
		var opt: Dictionary = opts[i]
		var btn            := Button.new()
		# Numbered like a table of contents — and the number keys
		# choose (see _unhandled_input).
		var num_prefix: String = "%d  ·  " % (i + 1) if i < 9 else ""
		var label: String = num_prefix + str(opt.get("text", "???"))
		if opt.has("check"):
			var check: Dictionary = opt["check"]
			label += "    ·  %s %d  ·" % [str(check.get("skill", "?")), int(check.get("diff", 0))]
		btn.text                  = label
		btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		btn.alignment             = HORIZONTAL_ALIGNMENT_CENTER

		# Chrome-less option lines: no box in rest, a thin gold
		# underline when hovered/focused — the option is TEXT, the
		# way the dialogue itself is.
		var normal_style := StyleBoxEmpty.new()
		normal_style.content_margin_left   = 12.0
		normal_style.content_margin_right  = 12.0
		normal_style.content_margin_top    = 8.0
		normal_style.content_margin_bottom = 8.0
		btn.add_theme_stylebox_override("normal", normal_style)

		var hover_style := StyleBoxFlat.new()
		hover_style.bg_color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.05)
		hover_style.border_color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.55)
		hover_style.border_width_bottom = 1
		hover_style.content_margin_left   = 12.0
		hover_style.content_margin_right  = 12.0
		hover_style.content_margin_top    = 8.0
		hover_style.content_margin_bottom = 8.0
		btn.add_theme_stylebox_override("hover",   hover_style)
		btn.add_theme_stylebox_override("pressed", hover_style)
		btn.add_theme_stylebox_override("focus",   hover_style)

		# Per-volume type character survives (skin font), but the size
		# floor rises to reading distance — options were 13px under a
		# 34px body.
		var ch_font: String = _skin.get("ch_font", SkinDB.F_IMFELL_R)
		if ResourceLoader.exists(ch_font):
			btn.add_theme_font_override("font", load(ch_font) as Font)
		btn.add_theme_font_size_override("font_size", maxi(19, int(_skin.get("ch_size", 13))))
		btn.add_theme_color_override("font_color",         _skin.get("ch_color",  Color(0.80, 0.75, 0.64)))
		btn.add_theme_color_override("font_hover_color",   C_GOLD)
		btn.add_theme_color_override("font_focus_color",   C_GOLD)
		btn.add_theme_color_override("font_pressed_color", C_GOLD)

		var idx := i
		btn.pressed.connect(func() -> void: _on_chosen(idx))
		btn.mouse_entered.connect(func() -> void:
			var sb := get_node_or_null("/root/SFXBank")
			if sb != null and sb.has_method("play"):
				sb.play("tile_hover", 0.5))
		_vbox.add_child(btn)

	if _vbox.get_child_count() > 0:
		(_vbox.get_child(0) as Control).grab_focus()

	# Staggered entrance — options settle in like a dealt hand
	# instead of popping as a block.
	for i2 in _vbox.get_child_count():
		var b: Control = _vbox.get_child(i2) as Control
		b.modulate.a = 0.0
		var tw := b.create_tween()
		tw.tween_interval(0.08 * float(i2))
		tw.tween_property(b, "modulate:a", 1.0, 0.25)
	# The scrim and column breathe in with the first option.
	_scrim.modulate.a = 0.0
	_column.modulate.a = 0.0
	var tw2 := create_tween()
	tw2.set_parallel(true)
	tw2.tween_property(_scrim, "modulate:a", 1.0, 0.30)
	tw2.tween_property(_column, "modulate:a", 1.0, 0.35)


# Number keys choose directly — couch-distance ergonomics.
func _unhandled_input(event: InputEvent) -> void:
	if not visible or not is_visible_in_tree() or _vbox == null:
		return
	if event is InputEventKey and event.pressed and not (event as InputEventKey).echo:
		var k: int = (event as InputEventKey).keycode
		if k >= KEY_1 and k <= KEY_9:
			var idx: int = k - KEY_1
			if idx < _vbox.get_child_count():
				get_viewport().set_input_as_handled()
				_on_chosen(idx)


func _on_chosen(idx: int) -> void:
	var sb := get_node_or_null("/root/SFXBank")
	if sb != null and sb.has_method("play"):
		sb.play("verb_select", 0.7)
	if _callback.is_valid():
		_callback.call(idx)
