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

# Nameplate chrome (standard skin only): a short accent-colored
# underline bar beneath the speaker name, plus a pop/slide animation
# when the speaker CHANGES — the eye catches the handoff in
# back-and-forth dialogue without reading the name every line.
var _spk_rule:     ColorRect = null
var _last_speaker: String    = ""

# Typewriter state
var _full_text:  String = ""
var _char_idx:   int    = 0
var _char_timer: float  = 0.0
var _typing:     bool   = false
var _cursor_t:   float  = 0.0

const CURSOR_CHAR := "▼"

# Which cutout slot the current line's speaker occupies — the text
# column shifts toward them so the words sit under whoever is talking.
# "" / "center" both centre the column (narration, unknown speaker).
var _col_slot: String = "center"

# Body font, cached so _fit_body_size can re-apply a smaller size for
# long passages (auto-fit) without re-reading the skin each time.
var _body_font_path: String = ""
var _body_base_size: int    = 34
# Standard-skin box geometry, cached so _fit_body_size can measure the
# available inner height and shrink the font until the whole passage
# fits top-to-bottom (no scroll, no clip at the screen edge).
var _std_box_h:      float  = 340.0
var _std_inner_top:  float  = 0.0
var _std_inner_bot:  float  = 0.0


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
	# The rule node is only rebuilt by the standard skin — clear the
	# reference so terminal/paper don't poke a freed node.
	_spk_rule     = null
	_last_speaker = ""
	match _variant:
		SkinDB.DLG_PAPER:    _build_paper()
		SkinDB.DLG_TERMINAL: _build_terminal()
		_:                   _build_standard()


# ── Public API ────────────────────────────────────────────────────────────────

func show_narrate(text: String) -> void:
	_speaker.visible = false
	if _spk_rule != null:
		_spk_rule.visible = false
	# Reset the change-tracker so the same speaker still pops when they
	# come back after a narration beat — the handoff reads either way.
	_last_speaker = ""
	_anchor_to("center")
	_body.add_theme_color_override("default_color", _skin.get("txt_color", Color.WHITE))
	_start_type(text)


func show_say(char_name: String, text: String) -> void:
	_present_speaker(char_name)
	_anchor_to(_slot_for(char_name))
	_body.add_theme_color_override("default_color", _skin.get("txt_color", Color.WHITE))
	_start_type(text)


func show_think(char_name: String, text: String) -> void:
	if char_name != "":
		_present_speaker(char_name)
	else:
		_speaker.text    = ""
		_speaker.visible = false
		if _spk_rule != null:
			_spk_rule.visible = false
		_last_speaker = ""
	_anchor_to(_slot_for(char_name) if char_name != "" else "center")
	_body.add_theme_color_override("default_color", _skin.get("txt_color", Color.WHITE))
	_start_type("[i]" + text + "[/i]")


# Set + style the nameplate for this line's speaker, and animate the
# handoff when the speaker changed since the previous line.
func _present_speaker(char_name: String) -> void:
	_speaker.text    = char_name.to_upper()
	_speaker.visible = true
	_apply_speaker_accent(char_name)
	# Underline bar sized to the rendered name (standard skin only —
	# terminal/paper keep their own diegetic chrome).
	if _spk_rule != null:
		_speaker.reset_size()
		_spk_rule.visible    = true
		_spk_rule.position   = Vector2(_speaker.position.x, -6.0)
		_spk_rule.size       = Vector2(maxf(_speaker.get_minimum_size().x, 40.0), 3.0)
		_spk_rule.pivot_offset = Vector2.ZERO
	var changed := char_name != _last_speaker
	_last_speaker = char_name
	if not changed or _variant != SkinDB.DLG_STANDARD:
		return
	# Speaker handoff: name pops from slightly oversized, underline
	# wipes in from the left. One beat (~0.2s), no layout shift.
	_speaker.pivot_offset = Vector2(0.0, _speaker.size.y)
	_speaker.scale = Vector2(1.14, 1.14)
	var tw := _speaker.create_tween()
	tw.tween_property(_speaker, "scale", Vector2.ONE, 0.16)\
		.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	if _spk_rule != null:
		_spk_rule.scale = Vector2(0.0, 1.0)
		var tw2 := _spk_rule.create_tween()
		tw2.tween_property(_spk_rule, "scale", Vector2.ONE, 0.22)\
			.set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)


func _apply_speaker_accent(char_name: String) -> void:
	# Pull the accent from CharLayer's registry so portrait borders,
	# speaker names, and any future char-keyed chrome stay aligned.
	var char_layer := get_tree().get_root().find_child("CharLayer", true, false)
	if char_layer == null or not char_layer.has_method("accent_for"):
		return
	var c: Color = char_layer.call("accent_for", char_name)
	_speaker.add_theme_color_override("font_color", c)
	if _spk_rule != null:
		_spk_rule.color = Color(c.r, c.g, c.b, 0.85)


# Ask CharLayer which slot this speaker's cutout stands in so the
# text column can shift under them. Falls back to centre if CharLayer
# is absent or the speaker has no on-screen portrait.
func _slot_for(char_name: String) -> String:
	var char_layer := get_tree().get_root().find_child("CharLayer", true, false)
	if char_layer != null and char_layer.has_method("slot_of"):
		var s: String = char_layer.call("slot_of", char_name)
		if s != "":
			return s
	return "center"


# Slide the body text + speaker name into a narrower column biased
# toward the speaker's cutout: left slot → hug the left third, right
# slot → hug the right third, centre/narration → centred. Only the
# standard modern-VN skin gets this; terminal/paper keep full width.
func _anchor_to(slot: String) -> void:
	_col_slot = slot
	if _variant != SkinDB.DLG_STANDARD or _body == null:
		return
	var pad: Array = _skin.get("dlg_pad", [22.0, 48.0, 28.0, 48.0])
	var left_pad: float  = float(pad[3])
	var right_pad: float = float(pad[1])
	# Wide box: text spans the full width with only small edge margins —
	# lots of room to work with, and left-anchored so there's more space
	# on the left (the portrait usually sits at the right). The speaker
	# name shares the left margin.
	_body.offset_left  = left_pad
	_body.offset_right = -right_pad
	if _speaker != null:
		_speaker.position.x = left_pad


func is_typing() -> bool:
	return _typing


func finish_typing() -> void:
	if not _typing:
		return
	_typing        = false
	_char_timer    = 0.0
	_body.text     = _full_text
	# No scroll_to_line — box auto-fits the whole passage; jumping to the
	# last line was hiding the opening lines on click.
	_cursor.visible = true


# ── Build variants ────────────────────────────────────────────────────────────

func _build_standard() -> void:
	# Modern-VN standard skin (2026-07-12 redesign): no bordered box —
	# a soft bottom scrim only; the outlined text carries legibility so
	# the background art reads full-bleed behind it. Larger type.
	# Small edge margins (was 60 L/R) so the text has the full width to
	# work with. Taller box so text can rise to just below mid-screen.
	var pad: Array = _skin.get("dlg_pad", [22.0, 48.0, 28.0, 48.0])
	# Box height is viewport-relative so the column reaches from just
	# below mid-screen down to the bottom on any resolution/letterbox —
	# giving long passages the room to fit without clipping. Overrides
	# the skin's dlg_min_h (and the -210 default _apply_skin set on the
	# root before setup ran) for the standard skin specifically.
	var vp_h: float = 720.0
	var vpr := get_viewport_rect()
	if vpr.size.y > 1.0:
		vp_h = vpr.size.y
	_std_box_h = clampf(vp_h * 0.46, 320.0, 480.0)
	offset_top = -_std_box_h
	offset_bottom = 0.0
	custom_minimum_size.y = _std_box_h
	# Inner text band (matches the body offsets set below): top pad+6,
	# bottom pad+18. Cached so _fit_body_size measures against it.
	_std_inner_top = float(pad[0]) + 6.0
	_std_inner_bot = float(pad[2]) + 18.0

	# No scrim, no border (2026-07-12 "no scrim" pass): the panel is
	# fully transparent — the outlined text alone carries legibility so
	# the background art reads uninterrupted. Kept as a node purely to
	# hold the content-margin padding the text column inherits.
	_bg = Panel.new()
	_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var style := StyleBoxFlat.new()
	# FORCED transparent — ignore any skin-supplied dlg_bg. The skin's
	# standard entry still carries an opaque colour, which was painting a
	# ~200px black band under the text. Modern-VN wants the text sitting
	# directly on the full-bleed background art, carried by its outline.
	style.bg_color = Color(0.0, 0.0, 0.0, 0.0)
	style.set_border_width_all(0)
	style.content_margin_top    = pad[0] + 4
	style.content_margin_right  = pad[1]
	style.content_margin_bottom = pad[2]
	style.content_margin_left   = pad[3]
	_bg.add_theme_stylebox_override("panel", style)
	add_child(_bg)

	# No rule bar (2026-07-12): the gradient rule drew a horizontal line
	# across the screen at the box top. Keep an empty node so the _rule
	# reference stays valid, but never render a bar.
	_rule = TextureRect.new()
	add_child(_rule)

	# Speaker name (above box)
	_speaker = Label.new()
	_speaker.position = Vector2(pad[3], -36.0)
	var sc: float = Settings.get_text_scale()
	# Large modern-VN type — fixed big sizes (scaled by the accessibility
	# text-scale), not the skin's smaller defaults.
	_apply_font(_speaker, _skin.get("spk_font", SkinDB.F_CINZEL),
				int(28 * sc),
				_skin.get("spk_color", Color(0.96, 0.82, 0.42)))
	_speaker.visible = false
	add_child(_speaker)

	# Accent underline bar under the speaker name — sized/positioned
	# per line in _present_speaker, colored in _apply_speaker_accent.
	_spk_rule = ColorRect.new()
	_spk_rule.visible = false
	_spk_rule.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_spk_rule)

	# Body text — top-aligned, no scrollbar. It fills the tall box from
	# the top down (text rises to just below mid-screen); auto-fit
	# (_fit_body_size) shrinks the font for long passages so nothing has
	# to scroll. scroll_active=false is what kills the "jump to bottom on
	# click" that was cutting off the opening lines.
	_body_font_path = _skin.get("txt_font", SkinDB.F_IMFELL_I)
	_body_base_size = int(34 * sc)
	_body = RichTextLabel.new()
	_body.bbcode_enabled = true
	_body.fit_content    = false
	_body.scroll_active  = false
	_body.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_body.offset_top    = pad[0] + 6
	_body.offset_bottom = -pad[2] - 18
	_body.offset_left   = pad[3]
	_body.offset_right  = -pad[1]
	_apply_rtl_font(_body, _body_font_path, _body_base_size,
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
	_fit_body_size(text)
	_body.text = ""


# Auto-fit: keep the big size for short/medium lines; step the font
# down toward a floor for long passages so the whole block fits the
# box top-to-bottom without needing a scrollbar. Standard skin only.
func _fit_body_size(text: String) -> void:
	if _variant != SkinDB.DLG_STANDARD or _body == null or _body_font_path == "":
		return
	var col: Color = _skin.get("txt_color", Color(0.98, 0.97, 0.94))
	var vis: String = _substr_visible(text, _count_visible(text))
	# Available inner height of the box (box height minus the top/bottom
	# text padding). The whole passage must fit inside this — no scroll.
	var avail: float = _std_box_h - _std_inner_top - _std_inner_bot
	var floor_size: int = maxi(16, int(_body_base_size * 0.5))
	var size: int = _body_base_size
	if avail > 1.0 and vis != "":
		# Measure at the real render width and step the font down until the
		# rendered content fits the box top-to-bottom. get_content_height()
		# validates the line cache synchronously, so this is accurate in
		# one call (no await needed).
		while size > floor_size:
			_apply_rtl_font(_body, _body_font_path, size, col)
			_body.text = vis
			var ch: float = _body.get_content_height()
			if ch <= 1.0:
				# Layout not ready (e.g. first frame) — fall back to the
				# character-count heuristic below rather than loop forever.
				size = _fit_size_by_count(text)
				break
			if ch <= avail:
				break
			size -= 2
	else:
		size = _fit_size_by_count(text)
	_apply_rtl_font(_body, _body_font_path, size, col)


# Fallback shrink when we can't measure (layout not ready): scale the
# font down by visible-character count toward the floor.
func _fit_size_by_count(text: String) -> int:
	var n: int = _count_visible(text)
	if n <= 260:
		return _body_base_size
	var t: float = clampf(float(n - 260) / 340.0, 0.0, 1.0)
	return int(round(lerp(float(_body_base_size), float(_body_base_size) * 0.55, t)))


func _process(delta: float) -> void:
	if _typing:
		_char_timer -= delta
		if _char_timer <= 0.0:
			_char_timer = Settings.get_char_delay_ms() / 1000.0
			_char_idx += 1
			_body.text  = _substr_visible(_full_text, _char_idx)
			# No scroll_to_line — the box auto-fits the whole passage, and
			# scrolling to the last line was hiding the opening lines.
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
