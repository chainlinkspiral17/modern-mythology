extends Control
## Dialogue box — skinned typewriter display.
## Call setup(skin) once, then show_narrate/show_say/show_think as needed.

var _skin: Dictionary = {}
var _variant: String = SkinDB.DLG_STANDARD

# UI nodes built in setup()
var _bg:      Panel          = null
var _rule:    TextureRect    = null
var _speaker: Label          = null
var _body:    RichTextLabel  = null
var _cursor:  Label          = null

# Typewriter state
var _full_text:  String = ""
var _char_idx:   int    = 0
var _char_timer: float  = 0.0
var _typing:     bool   = false
var _cursor_t:   float  = 0.0

const CURSOR_CHAR := "▼"


func _ready() -> void:
	Settings.settings_changed.connect(_on_settings_changed)


func _on_settings_changed(key: String, _val) -> void:
	if key == "txt_scale" and not _skin.is_empty():
		setup(_skin)


func setup(skin: Dictionary) -> void:
	_skin    = skin
	_variant = skin.get("variant", SkinDB.DLG_STANDARD)
	for ch in get_children():
		ch.queue_free()
	match _variant:
		SkinDB.DLG_PAPER:    _build_paper()
		SkinDB.DLG_TERMINAL: _build_terminal()
		_:                   _build_standard()


# ── Public API ────────────────────────────────────────────────────────────────

func show_narrate(text: String) -> void:
	_speaker.visible = false
	_body.add_theme_color_override("default_color", _skin.get("txt_color", Color.WHITE))
	_start_type(text)


func show_say(char_name: String, text: String) -> void:
	_speaker.text    = char_name.to_upper()
	_speaker.visible = true
	_apply_speaker_accent(char_name)
	_body.add_theme_color_override("default_color", _skin.get("txt_color", Color.WHITE))
	_start_type(text)


func show_think(char_name: String, text: String) -> void:
	_speaker.text    = char_name.to_upper() if char_name != "" else ""
	_speaker.visible = char_name != ""
	if char_name != "":
		_apply_speaker_accent(char_name)
	_body.add_theme_color_override("default_color", _skin.get("txt_color", Color.WHITE))
	_start_type("[i]" + text + "[/i]")


func _apply_speaker_accent(char_name: String) -> void:
	# Pull the accent from CharLayer's registry so portrait borders,
	# speaker names, and any future char-keyed chrome stay aligned.
	var char_layer := get_tree().get_root().find_child("CharLayer", true, false)
	if char_layer == null or not char_layer.has_method("accent_for"):
		return
	var c: Color = char_layer.call("accent_for", char_name)
	_speaker.add_theme_color_override("font_color", c)


func is_typing() -> bool:
	return _typing


func finish_typing() -> void:
	if not _typing:
		return
	_typing        = false
	_char_timer    = 0.0
	_body.text     = _full_text
	_body.scroll_to_line(_body.get_line_count())
	_cursor.visible = true


# ── Build variants ────────────────────────────────────────────────────────────

func _build_standard() -> void:
	# Modern-VN standard skin (2026-07-12 redesign): no bordered box —
	# a soft bottom scrim only; the outlined text carries legibility so
	# the background art reads full-bleed behind it. Larger type.
	var pad: Array = _skin.get("dlg_pad", [26.0, 60.0, 30.0, 60.0])
	var min_h: float = _skin.get("dlg_min_h", 200.0)
	custom_minimum_size.y = min_h

	# Soft scrim (no border, low alpha) instead of an opaque panel.
	_bg = Panel.new()
	_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var style := StyleBoxFlat.new()
	style.bg_color = _skin.get("dlg_bg", Color(0.02, 0.02, 0.04, 0.42))
	style.set_border_width_all(0)
	style.content_margin_top    = pad[0] + 4
	style.content_margin_right  = pad[1]
	style.content_margin_bottom = pad[2]
	style.content_margin_left   = pad[3]
	_bg.add_theme_stylebox_override("panel", style)
	add_child(_bg)

	# Gradient rule at top
	var rule_stops: Array = _skin.get("rule", [])
	if rule_stops.size() > 0:
		_rule = TextureRect.new()
		_rule.texture = SkinDB.make_rule_tex(rule_stops)
		_rule.stretch_mode = TextureRect.STRETCH_SCALE
		_rule.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
		_rule.custom_minimum_size.y = 2.0
		_rule.size.y = 2.0
		add_child(_rule)
	else:
		_rule = TextureRect.new()
		add_child(_rule)

	# Speaker name (above box)
	_speaker = Label.new()
	_speaker.position = Vector2(pad[3], -36.0)
	var sc: float = Settings.get_text_scale()
	_apply_font(_speaker, _skin.get("spk_font", SkinDB.F_CINZEL),
				int(_skin.get("spk_size", 19) * sc),
				_skin.get("spk_color", Color(0.96, 0.82, 0.42)))
	_speaker.visible = false
	add_child(_speaker)

	# Body text
	_body = RichTextLabel.new()
	_body.bbcode_enabled = true
	_body.fit_content    = false
	_body.scroll_active  = true
	_body.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_body.offset_top    = pad[0] + 6
	_body.offset_bottom = -pad[2] - 24
	_body.offset_left   = pad[3]
	_body.offset_right  = -pad[1]
	_apply_rtl_font(_body, _skin.get("txt_font", SkinDB.F_IMFELL_I),
					int(_skin.get("txt_size", 25) * sc),
					_skin.get("txt_color", Color(0.98, 0.97, 0.94)))
	add_child(_body)

	# Advance cursor
	_cursor = Label.new()
	_cursor.text = CURSOR_CHAR
	_apply_font(_cursor, _skin.get("spk_font", SkinDB.F_CINZEL), int(12 * sc),
				_skin.get("cursor_col", Color(0.78, 0.66, 0.29)))
	_cursor.visible = false
	add_child(_cursor)


func _build_terminal() -> void:
	var pad: Array = _skin.get("dlg_pad", [20.0, 40.0, 20.0, 40.0])
	var min_h: float = _skin.get("dlg_min_h", 220.0)
	custom_minimum_size.y = min_h

	_bg = Panel.new()
	_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var style := StyleBoxFlat.new()
	style.bg_color     = _skin.get("dlg_bg", Color(0.02, 0.03, 0.06, 0.97))
	style.border_color = _skin.get("dlg_border", Color(0.0, 0.7, 1.0, 0.25))
	style.set_border_width_all(1)
	style.content_margin_top    = pad[0] + 4
	style.content_margin_right  = pad[1]
	style.content_margin_bottom = pad[2]
	style.content_margin_left   = pad[3]
	_bg.add_theme_stylebox_override("panel", style)
	add_child(_bg)

	var rule_stops: Array = _skin.get("rule", [])
	if rule_stops.size() > 0:
		_rule = TextureRect.new()
		_rule.texture = SkinDB.make_rule_tex(rule_stops)
		_rule.stretch_mode = TextureRect.STRETCH_SCALE
		_rule.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
		_rule.custom_minimum_size.y = 2.0
		add_child(_rule)
	else:
		_rule = TextureRect.new()
		add_child(_rule)

	var sc: float = Settings.get_text_scale()
	_speaker = Label.new()
	_speaker.position = Vector2(pad[3], -26.0)
	_apply_font(_speaker, _skin.get("spk_font", SkinDB.F_SPACEMONO),
				int(_skin.get("spk_size", 11) * sc),
				_skin.get("spk_color", Color(0.0, 0.78, 1.0)))
	_speaker.visible = false
	add_child(_speaker)

	_body = RichTextLabel.new()
	_body.bbcode_enabled = true
	_body.fit_content    = false
	_body.scroll_active  = true
	_body.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_body.offset_top    = pad[0] + 6
	_body.offset_bottom = -pad[2] - 20
	_body.offset_left   = pad[3]
	_body.offset_right  = -pad[1]
	_apply_rtl_font(_body, _skin.get("txt_font", SkinDB.F_SPACEMONO),
					int(_skin.get("txt_size", 13) * sc),
					_skin.get("txt_color", Color(0.78, 0.84, 0.94)))
	add_child(_body)

	_cursor = Label.new()
	_cursor.text = CURSOR_CHAR
	_apply_font(_cursor, _skin.get("spk_font", SkinDB.F_SPACEMONO), int(11 * sc),
				_skin.get("cursor_col", Color(0.0, 0.78, 1.0)))
	_cursor.visible = false
	add_child(_cursor)


func _build_paper() -> void:
	var pad: Array  = _skin.get("dlg_pad", [24.0, 36.0, 24.0, 36.0])
	var min_h: float = _skin.get("dlg_min_h", 240.0)
	custom_minimum_size.y = min_h

	_bg = Panel.new()
	_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var style := StyleBoxFlat.new()
	style.bg_color     = _skin.get("dlg_bg", Color(0.94, 0.92, 0.88))
	style.border_color = _skin.get("dlg_border", Color(0.0, 0.0, 0.0, 0.08))
	style.set_border_width_all(1)
	style.content_margin_top    = pad[0] + 20
	style.content_margin_right  = pad[1]
	style.content_margin_bottom = pad[2]
	style.content_margin_left   = pad[3]
	_bg.add_theme_stylebox_override("panel", style)
	add_child(_bg)

	# Tape strips
	var tape_col: Color = _skin.get("tape_color", Color(1.0, 0.86, 0.39, 0.5))
	_add_tape_strip(Vector2(pad[3] + 20, 0), 76, 22, -1.5, tape_col)
	_add_tape_strip(Vector2(pad[3] + 120, -2), 76, 22, 2.0, tape_col)

	_rule = TextureRect.new()  # unused for paper but keep reference valid
	add_child(_rule)

	var sc: float = Settings.get_text_scale()
	_speaker = Label.new()
	_speaker.position = Vector2(pad[3], 24.0)
	_apply_font(_speaker, _skin.get("spk_font", SkinDB.F_BEBAS),
				int(_skin.get("spk_size", 28) * sc),
				_skin.get("spk_color", Color(0.04, 0.04, 0.04)))
	_speaker.visible = false
	add_child(_speaker)

	_body = RichTextLabel.new()
	_body.bbcode_enabled = true
	_body.fit_content    = false
	_body.scroll_active  = true
	_body.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_body.offset_top    = pad[0] + 22
	_body.offset_bottom = -pad[2] - 20
	_body.offset_left   = pad[3]
	_body.offset_right  = -pad[1]
	_apply_rtl_font(_body, _skin.get("txt_font", SkinDB.F_ELITE),
					int(_skin.get("txt_size", 15) * sc),
					_skin.get("txt_color", Color(0.10, 0.10, 0.10)))
	add_child(_body)

	_cursor = Label.new()
	_cursor.text = CURSOR_CHAR
	_apply_font(_cursor, _skin.get("txt_font", SkinDB.F_ELITE), int(14 * sc),
				_skin.get("cursor_col", Color(0.04, 0.04, 0.04)))
	_cursor.visible = false
	add_child(_cursor)


# ── Typewriter ────────────────────────────────────────────────────────────────

func _start_type(text: String) -> void:
	_full_text  = text
	_char_idx   = 0
	_typing     = true
	_char_timer = 0.0
	_cursor.visible = false
	_body.text = ""


func _process(delta: float) -> void:
	if _typing:
		_char_timer -= delta
		if _char_timer <= 0.0:
			_char_timer = Settings.get_char_delay_ms() / 1000.0
			_char_idx += 1
			_body.text  = _substr_visible(_full_text, _char_idx)
			_body.scroll_to_line(_body.get_line_count())
			if _char_idx >= _count_visible(_full_text):
				_typing     = false
				_cursor.visible = true
	elif _cursor != null and _cursor.visible:
		_cursor_t += delta
		var a: float = 0.4 + 0.6 * (0.5 + 0.5 * sin(_cursor_t * TAU / 1.5))
		_cursor.modulate.a = a
		_place_cursor()


func _substr_visible(text: String, n: int) -> String:
	var count := 0
	var i     := 0
	while i < text.length() and count < n:
		if text[i] == "[":
			var end: int = text.find("]", i)
			if end != -1:
				i = end + 1
				continue
		count += 1
		i     += 1
	return text.substr(0, i)


func _count_visible(text: String) -> int:
	var count := 0
	var i     := 0
	while i < text.length():
		if text[i] == "[":
			var end: int = text.find("]", i)
			if end != -1:
				i = end + 1
				continue
		count += 1
		i     += 1
	return count


func _place_cursor() -> void:
	if _body == null or _cursor == null:
		return
	var r: Rect2 = _body.get_rect()
	_cursor.position = Vector2(r.end.x - 24, r.end.y - 26)


# ── Helpers ───────────────────────────────────────────────────────────────────

# Modern-VN legibility: a heavy contrast outline so text reads over
# ANY background regardless of the scene's colours. Light fill →
# black outline; dark fill (paper skin) → white outline. Outline
# scales with the font so big text gets a proportionally bold edge.
static func _outline_for(col: Color) -> Color:
	return Color(0, 0, 0, 0.92) if col.get_luminance() > 0.5 else Color(1, 1, 1, 0.92)


func _apply_font(lbl: Label, font_path: String, size: int, col: Color) -> void:
	if ResourceLoader.exists(font_path):
		var ff: FontFile = load(font_path)
		lbl.add_theme_font_override("font", ff)
	lbl.add_theme_font_size_override("font_size", size)
	lbl.add_theme_color_override("font_color", col)
	lbl.add_theme_color_override("font_outline_color", _outline_for(col))
	lbl.add_theme_constant_override("outline_size", maxi(4, int(size * 0.34)))


func _apply_rtl_font(rtl: RichTextLabel, font_path: String, size: int, col: Color) -> void:
	if ResourceLoader.exists(font_path):
		var ff: FontFile = load(font_path)
		rtl.add_theme_font_override("normal_font",  ff)
		rtl.add_theme_font_override("bold_font",    ff)
		rtl.add_theme_font_override("italics_font", ff)
	rtl.add_theme_font_size_override("normal_font_size",  size)
	rtl.add_theme_font_size_override("bold_font_size",    size)
	rtl.add_theme_font_size_override("italics_font_size", size)
	rtl.add_theme_color_override("default_color", col)
	# RichTextLabel outline: color override + outline_size constant.
	rtl.add_theme_color_override("font_outline_color", _outline_for(col))
	rtl.add_theme_constant_override("outline_size", maxi(4, int(size * 0.34)))


func _add_tape_strip(pos: Vector2, w: int, h: int, angle_deg: float, col: Color) -> void:
	var strip := ColorRect.new()
	strip.color              = col
	strip.size               = Vector2(w, h)
	strip.position           = pos
	strip.pivot_offset       = Vector2(w * 0.5, h * 0.5)
	strip.rotation_degrees   = angle_deg
	add_child(strip)
