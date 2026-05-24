extends Control
## Choice menu — vertical list of option buttons, skin-aware.
## Call setup(skin) once after instantiation, then present() per use.

var _skin:         Dictionary    = {}
var _callback:     Callable
var _vbox:         VBoxContainer = null
var _prompt_label: Label         = null
var _panel_style:  StyleBoxFlat  = null


func _ready() -> void:
	_build()


func setup(skin: Dictionary) -> void:
	_skin = skin
	if _panel_style != null:
		_panel_style.bg_color     = skin.get("ov_bg",     Color(0.04, 0.03, 0.02, 0.95))
		_panel_style.border_color = skin.get("ov_border", Color(0.85, 0.72, 0.35, 0.4))
	if _prompt_label != null:
		_prompt_label.add_theme_color_override("font_color", skin.get("hud_color", Color(0.75, 0.65, 0.30)))
		var font_path: String = skin.get("ch_font", SkinDB.F_CINZEL)
		if ResourceLoader.exists(font_path):
			_prompt_label.add_theme_font_override("font", load(font_path) as Font)
		_prompt_label.add_theme_font_size_override("font_size", skin.get("ch_size", 13))


func _build() -> void:
	var panel := Panel.new()
	panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_panel_style = StyleBoxFlat.new()
	_panel_style.bg_color = Color(0.04, 0.03, 0.02, 0.95)
	_panel_style.border_color = Color(0.85, 0.72, 0.35, 0.4)
	_panel_style.set_border_width_all(1)
	_panel_style.content_margin_left   = 16.0
	_panel_style.content_margin_right  = 16.0
	_panel_style.content_margin_top    = 16.0
	_panel_style.content_margin_bottom = 16.0
	panel.add_theme_stylebox_override("panel", _panel_style)
	add_child(panel)

	var outer := VBoxContainer.new()
	outer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	outer.offset_left   = 16
	outer.offset_right  = -16
	outer.offset_top    = 16
	outer.offset_bottom = -16
	outer.add_theme_constant_override("separation", 10)
	add_child(outer)

	_prompt_label = Label.new()
	_prompt_label.add_theme_font_size_override("font_size", 16)
	_prompt_label.add_theme_color_override("font_color", Color(0.75, 0.65, 0.30))
	_prompt_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	outer.add_child(_prompt_label)

	_vbox = VBoxContainer.new()
	_vbox.add_theme_constant_override("separation", 8)
	outer.add_child(_vbox)


func present(prompt: String, opts: Array, callback: Callable) -> void:
	_callback = callback
	_prompt_label.text    = prompt
	_prompt_label.visible = prompt != ""

	for child in _vbox.get_children():
		child.queue_free()

	for i in opts.size():
		var opt: Dictionary = opts[i]
		var btn            := Button.new()
		btn.text                  = opt.get("text", "???")
		btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		btn.alignment             = HORIZONTAL_ALIGNMENT_LEFT

		var normal_style := StyleBoxFlat.new()
		normal_style.bg_color     = _skin.get("ch_bg",     Color(0.04, 0.03, 0.02, 0.7))
		normal_style.border_color = _skin.get("ch_border", Color(0.85, 0.72, 0.35, 0.3))
		normal_style.set_border_width_all(1)
		normal_style.content_margin_left   = 12.0
		normal_style.content_margin_right  = 12.0
		normal_style.content_margin_top    = 10.0
		normal_style.content_margin_bottom = 10.0
		btn.add_theme_stylebox_override("normal", normal_style)

		var hover_style: StyleBoxFlat = normal_style.duplicate() as StyleBoxFlat
		hover_style.bg_color     = _skin.get("ch_hbg",     Color(0.10, 0.08, 0.04, 0.9))
		hover_style.border_color = _skin.get("ch_hborder", Color(0.85, 0.72, 0.35, 0.7))
		btn.add_theme_stylebox_override("hover",   hover_style)
		btn.add_theme_stylebox_override("pressed", hover_style)
		btn.add_theme_stylebox_override("focus",   hover_style)

		var ch_font: String = _skin.get("ch_font", SkinDB.F_CINZEL)
		if ResourceLoader.exists(ch_font):
			btn.add_theme_font_override("font", load(ch_font) as Font)
		btn.add_theme_font_size_override("font_size",              _skin.get("ch_size",   13))
		btn.add_theme_color_override("font_color",                 _skin.get("ch_color",  Color(0.72, 0.66, 0.53)))
		btn.add_theme_color_override("font_hover_color",           _skin.get("ch_hcolor", Color(0.83, 0.79, 0.69)))
		btn.add_theme_color_override("font_focus_color",           _skin.get("ch_hcolor", Color(0.83, 0.79, 0.69)))
		btn.add_theme_color_override("font_pressed_color",         _skin.get("ch_hcolor", Color(0.83, 0.79, 0.69)))

		if opt.has("check"):
			var check: Dictionary = opt["check"]
			btn.text += "  [%s %d]" % [check.get("skill", "?"), int(check.get("diff", 0))]
		var idx := i
		btn.pressed.connect(func() -> void: _on_chosen(idx))
		_vbox.add_child(btn)

	if _vbox.get_child_count() > 0:
		_vbox.get_child(0).grab_focus()


func _on_chosen(idx: int) -> void:
	if _callback.is_valid():
		_callback.call(idx)
