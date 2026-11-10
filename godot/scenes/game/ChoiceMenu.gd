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
var _vbox:         GridContainer = null     # the options (one column, or two for a long list)
var _scroll:       ScrollContainer = null   # holds them; scrolls only when nothing else fits
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
	# (2026-11-10, the user: "making choices in the menu still breaks the
	# game.") The column hung from the screen's centre DOWNWARD: its top sat
	# at mid-screen and every option pushed the list toward the bottom edge.
	# Five options reached it; the hubs have 7, 10, 13 — one has 31 — and
	# everything past the edge could not be seen or clicked. The column now
	# grows both ways from the centre, and present() fits the list to the
	# screen (_fit_options).
	_column.grow_vertical = Control.GROW_DIRECTION_BOTH
	_column.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_column.alignment = BoxContainer.ALIGNMENT_CENTER
	_column.add_theme_constant_override("separation", 18)
	add_child(_column)

	_column.add_child(_ornament())

	_prompt_label = Label.new()
	_prompt_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_prompt_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	# (pass 82) the prompt in the reading face's italic, a step above the body
	if ResourceLoader.exists(SkinDB.F_LITERATA_I):
		_prompt_label.add_theme_font_override("font", load(SkinDB.F_LITERATA_I) as Font)
	_prompt_label.add_theme_font_size_override("font_size", 26)
	_prompt_label.add_theme_color_override("font_color", Color(0.93, 0.90, 0.83))
	_column.add_child(_prompt_label)

	_scroll = ScrollContainer.new()
	_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	_scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
	_scroll.follow_focus = true          # a pad walks the list into view
	_column.add_child(_scroll)
	_vbox = GridContainer.new()
	_vbox.columns = 1
	_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_vbox.add_theme_constant_override("v_separation", 6)
	_vbox.add_theme_constant_override("h_separation", 18)
	_scroll.add_child(_vbox)

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


func present(prompt: String, opts: Array, callback: Callable, style: String = "", hotspot: String = "") -> void:
	_callback = callback
	# VERB COIN (SCUMM grammar · milk_honey register · 2026-09-07): the
	# prompt line names the HOTSPOT in small caps and the options are
	# short verbs in caps — LOOK AT · ASK PER · LEAVE IT — instead of
	# numbered sentences. Same buttons, same keys; the grammar is the
	# only difference.
	var coin: bool = style == "verb_coin"
	if coin:
		_prompt_label.text = ("▸  " + hotspot.to_upper()) if hotspot != "" else prompt
		_prompt_label.visible = _prompt_label.text != ""
	else:
		_prompt_label.text    = prompt
		_prompt_label.visible = prompt != ""

	# Remove stale options from the tree BEFORE building. queue_free
	# alone leaves the dying buttons as children until end of frame,
	# so get_child(0) below would grab a corpse for focus, and the
	# stagger loop / number keys would count them too.
	for child in _vbox.get_children():
		_vbox.remove_child(child)
		child.queue_free()
	_scroll.scroll_vertical = 0

	var labels: Array = []
	for i in opts.size():
		labels.append(_label_for(i, opts[i], coin))
	var fit: Dictionary = _fit_options(labels)
	var opt_font: int = int(fit["font"])
	var opt_pad: float = float(fit["pad"])
	_vbox.columns = int(fit["cols"])
	for i in opts.size():
		var opt: Dictionary = opts[i]
		var btn            := Button.new()
		# Numbered like a table of contents — and the number keys
		# choose (see _unhandled_input).
		var label: String = String(labels[i])
		btn.text                  = label
		btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		btn.alignment             = HORIZONTAL_ALIGNMENT_CENTER

		# Chrome-less option lines: no box in rest, a thin gold
		# underline when hovered/focused — the option is TEXT, the
		# way the dialogue itself is.
		var normal_style := StyleBoxEmpty.new()
		normal_style.content_margin_left   = 12.0
		normal_style.content_margin_right  = 12.0
		normal_style.content_margin_top    = opt_pad
		normal_style.content_margin_bottom = opt_pad
		btn.add_theme_stylebox_override("normal", normal_style)

		var hover_style := StyleBoxFlat.new()
		hover_style.bg_color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.05)
		hover_style.border_color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.55)
		hover_style.border_width_bottom = 1
		hover_style.content_margin_left   = 12.0
		hover_style.content_margin_right  = 12.0
		hover_style.content_margin_top    = opt_pad
		hover_style.content_margin_bottom = opt_pad
		btn.add_theme_stylebox_override("hover",   hover_style)
		btn.add_theme_stylebox_override("pressed", hover_style)
		btn.add_theme_stylebox_override("focus",   hover_style)

		# Per-volume type character survives (skin font), but the size
		# floor rises to reading distance — options were 13px under a
		# 34px body.
		var ch_font: String = _skin.get("ch_font", SkinDB.F_LITERATA)
		if ResourceLoader.exists(ch_font):
			btn.add_theme_font_override("font", load(ch_font) as Font)
		# (pass 82) options at reading size; the hover colour is the skin's
		# ch_hcolor so the cream suburban scrim keeps its contrast (gold on
		# cream read as nothing).
		btn.add_theme_font_size_override("font_size", opt_font)
		if _vbox.columns > 1:
			btn.clip_text = true         # two columns: a long option ends in an ellipsis, never under its neighbour
			btn.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
			btn.tooltip_text = label
		else:
			# one column: a long option WRAPS inside the column (it used to
			# set the column's width, and ran off the right of the screen)
			btn.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			btn.custom_minimum_size.x = 780.0 - 8.0
		var hot: Color = _skin.get("ch_hcolor", C_GOLD)
		btn.add_theme_color_override("font_color",         _skin.get("ch_color",  Color(0.80, 0.75, 0.64)))
		btn.add_theme_color_override("font_hover_color",   hot)
		btn.add_theme_color_override("font_focus_color",   hot)
		btn.add_theme_color_override("font_pressed_color", hot)

		var idx := i
		btn.pressed.connect(func() -> void: _on_chosen(idx))
		btn.mouse_entered.connect(func() -> void:
			var sb := get_node_or_null("/root/SFXBank")
			if sb != null and sb.has_method("play"):
				sb.play("tile_hover", 0.5))
		_vbox.add_child(btn)

	_size_list(fit)
	# a wrapped option's height is only known once it has been laid out
	_resize_after_layout(fit)
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


func _label_for(i: int, opt: Dictionary, coin: bool) -> String:
	var num_prefix: String = "%d  ·  " % (i + 1) if i < 9 else ""
	var label: String = num_prefix + str(opt.get("text", "???"))
	if coin:
		label = "  " + str(opt.get("text", "???")).to_upper() + "  "
	if opt.has("check"):
		var check: Dictionary = opt["check"]
		label += "    ·  %s %d  ·" % [str(check.get("skill", "?")), int(check.get("diff", 0))]
	elif opt.has("skill"):
		# The skill an option exercises, named the way a check names
		# what it asks for — minus the number. The face of the five
		# skills on the plate (2026-09-17).
		label += "    ·  %s  ·" % str(opt.get("skill", ""))
	return label


# ── the list is fitted to the screen ──────────────────────────────────
# Tried in order until the options fit the height there is: the reading
# size in one column; a tighter one; two columns (the column widens); two
# tight columns; and past that the list scrolls. A hub with thirty-one
# doors is still a list every door of which can be reached.
const FIT_STEPS := [
	{"cols": 1, "font": 22, "pad": 8.0},
	{"cols": 1, "font": 19, "pad": 5.0},
	{"cols": 2, "font": 20, "pad": 6.0},
	{"cols": 2, "font": 17, "pad": 4.0},
	{"cols": 2, "font": 15, "pad": 3.0},
]


func _screen() -> Vector2:
	var r := get_viewport_rect().size
	return r if r.y > 1.0 else Vector2(1280.0, 720.0)


## The height the options may take: the screen, less a margin, the prompt
## and the two ornaments.
func _list_room() -> float:
	var prompt_h: float = 0.0
	if _prompt_label != null and _prompt_label.visible:
		prompt_h = _prompt_label.get_combined_minimum_size().y + 18.0
	return maxf(_screen().y * 0.84 - prompt_h - 2.0 * (16.0 + 18.0), 120.0)


func _fit_options(labels: Array) -> Dictionary:
	var room: float = _list_room()
	var base: int = maxi(22, int(_skin.get("ch_size", 22)))
	var font: Font = null
	var ch_font: String = _skin.get("ch_font", SkinDB.F_LITERATA)
	if ResourceLoader.exists(ch_font):
		font = load(ch_font) as Font
	for step_v in FIT_STEPS:
		var step: Dictionary = (step_v as Dictionary).duplicate()
		if int(step["font"]) == 22:
			step["font"] = base
		var px: int = int(step["font"])
		var line_h: float = float(px) * 1.42
		var extra: float = 2.0 * float(step["pad"]) + 6.0
		var need: float = 0.0
		if int(step["cols"]) == 1:
			# a long option wraps: count its lines at this size
			for lab_v in labels:
				var lines: float = 1.0
				if font != null:
					var w: float = font.get_string_size(String(lab_v), HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
					lines = maxf(ceil(w / (780.0 - 8.0 - 24.0)), 1.0)
				need += lines * line_h + extra
		else:
			need = ceil(float(labels.size()) / float(int(step["cols"]))) * (line_h + extra)
		if need <= room:
			return step
	return (FIT_STEPS[FIT_STEPS.size() - 1] as Dictionary).duplicate()


func _size_list(fit: Dictionary) -> void:
	var scr: Vector2 = _screen()
	var wide: bool = int(fit["cols"]) > 1
	var col_w: float = minf(1180.0, scr.x * 0.9) if wide else 780.0
	_column.custom_minimum_size.x = col_w
	_column.offset_left = -col_w * 0.5
	_column.offset_right = col_w * 0.5
	var need: float = _vbox.get_combined_minimum_size().y
	_scroll.custom_minimum_size = Vector2(col_w, minf(need, _list_room()))
	# re-centre on the new height (the column grows both ways from here)
	_column.offset_top = 0.0
	_column.offset_bottom = 0.0
	_column.reset_size()


func _resize_after_layout(fit: Dictionary) -> void:
	for i in 2:
		await get_tree().process_frame
		if not is_inside_tree() or not visible:
			return
		_size_list(fit)


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
