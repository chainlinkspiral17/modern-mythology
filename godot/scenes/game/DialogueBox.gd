extends Control
## Dialogue box — skinned typewriter display.
## Call setup(skin) once, then show_narrate/show_say/show_think as needed.

var _skin: Dictionary = {}
var _variant: String = SkinDB.DLG_STANDARD

# CharLayer reference, injected by GameEngine._build_layers via
# set_char_layer() so accent/slot lookups don't tree-walk every
# line. find_child stays as the fallback when nothing was injected
# (e.g. the box used outside GameEngine).
var _char_layer_ref: Node = null


func set_char_layer(n: Node) -> void:
	_char_layer_ref = n


func _get_char_layer() -> Node:
	if _char_layer_ref != null and is_instance_valid(_char_layer_ref):
		return _char_layer_ref
	return get_tree().get_root().find_child("CharLayer", true, false)

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
# NO SPEAKER TICK. The dialogue box is SILENT on advance — the
# nameplate pop and the underline wipe carry the handoff on their
# own, which was always the design intent. A per-change blip was
# tried twice (2026-07) and reported both times as "a beeping as I
# progress" / "super annoying": in back-and-forth dialogue EVERY
# line is a speaker change, so any handoff-gated tick fires on
# nearly every advance. Do not re-add a per-line sound here.

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
## (2026-10-27) a side something else holds that CharLayer doesn't know of —
## the phone thread — so the column stays clear of it too
var _extra_occupied: String = ""


func set_extra_occupied(side: String) -> void:
	_extra_occupied = side

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
	get_viewport().size_changed.connect(_on_viewport_resized)


func _on_settings_changed(key: String, _val) -> void:
	if key == "txt_scale" and not _skin.is_empty():
		_rebuild_keeping_line()


## (2026-11-10, the user: "making choices in the menu still breaks the
## game.") TEXT SIZE in the options rebuilt this box from nothing — and the
## line on screen went with it: an empty box under the menu, and an empty
## screen after it until the next page. The rebuilt box takes the line back:
## the same speaker, the same words, as far along as they were.
func _rebuild_keeping_line() -> void:
	var line: String = _full_text
	var who: String = _last_speaker
	var named: bool = _speaker != null and is_instance_valid(_speaker) and _speaker.visible
	var slot: String = _col_slot
	var was_typing: bool = _typing
	var at: int = _char_idx
	setup(_skin)
	if line == "":
		return
	if named and who != "":
		_present_speaker(who)
	_anchor_to(slot)
	_body.add_theme_color_override("default_color", _skin.get("txt_color", Color.WHITE))
	_start_type(line)
	if was_typing:
		_char_idx = at
		_body.visible_characters = at
	else:
		finish_typing()


## The window changed size under a line (SCREEN SIZE in the options, a
## window dragged): the column is placed and the line fitted again.
func _on_viewport_resized() -> void:
	if _body == null or not is_instance_valid(_body) or _skin.is_empty():
		return
	_anchor_to(_col_slot)
	if _full_text != "":
		_fit_body_size(_full_text)
		_plate_snap = true


func setup(skin: Dictionary) -> void:
	_skin    = skin
	_variant = skin.get("variant", SkinDB.DLG_STANDARD)
	for ch in get_children():
		ch.queue_free()
	# The rule node is only rebuilt by the standard skin — clear the
	# reference so terminal/paper don't poke a freed node.
	_spk_rule     = null
	_last_speaker = ""
	_plate = null
	_measure = null
	_band = null
	_tapes.clear()
	_plate_snap = true
	match _variant:
		SkinDB.DLG_PAPER:    _build_paper()
		SkinDB.DLG_TERMINAL: _build_terminal()
		_:                   _build_standard()


# ── Public API ────────────────────────────────────────────────────────────────

# ── the backlog · everything read this session, for the reader who
# tapped once too fast. GameEngine renders it (H / wheel-up).
var backlog: Array = []
const BACKLOG_CAP := 300


func _log_line(char_name: String, text: String, think: bool) -> void:
	backlog.append({"name": char_name, "text": text, "think": think})
	while backlog.size() > BACKLOG_CAP:
		backlog.pop_front()


func show_narrate(text: String) -> void:
	_log_line("", text, false)
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
	_log_line(char_name, text, false)
	_present_speaker(char_name)
	_anchor_to(_slot_for(char_name))
	_body.add_theme_color_override("default_color", _skin.get("txt_color", Color.WHITE))
	_start_type(text)


func show_think(char_name: String, text: String) -> void:
	_log_line(char_name, text, true)
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
	# Underline bar sized to the rendered name — sits just under the
	# speaker label on every skin (each build places _speaker itself).
	if _spk_rule != null:
		_speaker.reset_size()
		_spk_rule.visible    = true
		_spk_rule.position   = Vector2(_speaker.position.x,
				_speaker.position.y + _speaker.get_minimum_size().y + 1.0)
		_spk_rule.size       = Vector2(maxf(_speaker.get_minimum_size().x, 40.0), 2.0)
		_spk_rule.pivot_offset = Vector2.ZERO
	var changed := char_name != _last_speaker
	_last_speaker = char_name
	if not changed:
		return
	# Speaker handoff, silently: the name pops from slightly oversized
	# and the underline wipes in from the left. No sound (see above).
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
	var char_layer: Node = _get_char_layer()
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
	var char_layer: Node = _get_char_layer()
	if char_layer != null and char_layer.has_method("slot_of"):
		var s: String = char_layer.call("slot_of", char_name)
		if s != "":
			return s
	return "center"


# Slide the body text + speaker name into a narrower column biased
# toward the speaker's cutout: left slot → hug the left third, right
# slot → hug the right third, centre/narration → centred. Every skin
# (terminal and paper too, since 2026-10-17).
func _anchor_to(slot: String) -> void:
	_col_slot = slot
	if _body == null:
		return
	var pad: Array = _skin.get("dlg_pad", [22.0, 48.0, 28.0, 48.0])
	var left_pad: float  = float(pad[3])
	var right_pad: float = float(pad[1])
	# THE MEASURE (pass 82): the column is centred and capped at
	# READ_MAX_COL (~75 characters) — an ereader's line, not the screen's
	# — and leans gently toward the speaker's portrait slot, never past
	# the pads. On a narrow viewport the cap never bites and there is no
	# room to lean, so the column simply fills the box.
	# (2026-10-27, the Deck: "text over portraits is wrong ... keep it off to
	# the side for each speaker/narration") the column no longer leans toward
	# the speaker: when a portrait stands on one side, the text takes the
	# OTHER side (~58 % of the width); with none, or both, it is centred.
	var vp_w: float = 1280.0
	var vpr := get_viewport_rect()
	if vpr.size.x > 1.0:
		vp_w = vpr.size.x
	# WIDE SCREENS (2026-11-08): the text lives in the centre 16:9 band;
	# the width past it belongs to the panoramic background
	var band_x: float = 0.0
	var sm: Node = get_node_or_null("/root/ScreenMgr")
	if sm != null and sm.has_method("center_band"):
		var band: Rect2 = sm.call("center_band")
		band_x = maxf(band.position.x, 0.0)
		vp_w = minf(vp_w, band.size.x)
	left_pad += band_x
	right_pad += band_x
	var usable: float = maxf(vp_w - (left_pad - band_x) - (right_pad - band_x), 1.0)
	var occ: Array = []
	var char_layer: Node = _get_char_layer()
	if char_layer != null and char_layer.has_method("occupied_slots"):
		occ = char_layer.call("occupied_slots")
	if _extra_occupied != "" and not occ.has(_extra_occupied):
		occ = occ.duplicate()
		occ.append(_extra_occupied)
	var side: String = ""
	if occ.has("right") and not occ.has("left"):
		side = "left"
	elif occ.has("left") and not occ.has("right"):
		side = "right"
	elif occ.is_empty():
		side = ""
	elif slot == "right" and not occ.has("left"):
		side = "left"
	elif slot == "left" and not occ.has("right"):
		side = "right"
	var col_w: float = minf(READ_MAX_COL, usable * (0.58 if side != "" else 1.0))
	var spare: float = maxf(usable - col_w, 0.0)
	var target_l: float = left_pad + spare * 0.5
	var target_r: float = -(right_pad + spare * 0.5)
	if side == "left":
		target_l = left_pad
		target_r = -(right_pad + spare)
	elif side == "right":
		target_l = left_pad + spare
		target_r = -right_pad
	# (2026-11-10, the user: "text is partially rendering outside the
	# background box on the right before it continues to the next line" /
	# "make the text work. don't break it on screen like this.") The column
	# used to SLIDE to its place over a quarter second while the line was
	# already being fitted and typed: the font was fitted at the old, wider
	# column, the column then narrowed, the passage wrapped to a line more
	# than the box holds and its last line was cut off at the screen edge.
	# The column is in its place before the first character; only the plate
	# glides (_update_plate).
	var moved: bool = absf(_body.offset_left - target_l) > 0.5 \
			or absf(_body.offset_right - target_r) > 0.5
	_body.offset_left = target_l
	_body.offset_right = target_r
	if _speaker != null:
		_speaker.position.x = target_l
	if _spk_rule != null:
		_spk_rule.position.x = target_l
	# a column that changes under a line already up: fit that line again
	if moved and _full_text != "" and visible:
		_fit_body_size(_full_text)


func is_typing() -> bool:
	return _typing


func finish_typing() -> void:
	if not _typing:
		return
	_typing        = false
	_char_timer    = 0.0
	_body.visible_characters = -1
	# No scroll_to_line — box auto-fits the whole passage; jumping to the
	# last line was hiding the opening lines on click.
	_cursor.visible = true


# ── Build variants ────────────────────────────────────────────────────────────

# ── THE READING BAND (2026-10-11, pass 82) ────────────────────────────
# User: "clean, elegant ereader type fonts for the visual novel … the whole
# visual novel UI needs more passes, it's still a bit ugly." The 2026-07
# modern-VN standard skin set 34 px type with an 11 px outline straight on
# the art. This reads like an ereader instead: Literata at 28 px, 1.45
# leading, a measure capped near 75 characters, NO outline — the words sit
# on a soft reading band that fades up from the skin's dlg_bg (near-black
# for the literary skins, cream paper for suburban) so the art stays
# full-bleed above and the text has a calm ground. Draft 2 targets: the
# band's top edge as a real gradient mask over the art (not a flat fade),
# a hanging-punctuation / optical-margin pass, the backlog in the same face.
const READ_BODY_PX := 28
const READ_LEADING := 0.18        # extra line separation (Literata already carries ~1.44 em of line height)
const READ_MAX_COL := 980.0       # the measure: ~75 characters of Literata at 28 px
const READ_SPK_PX  := 21
const READ_BAND_RISE := 36.0      # how far above the box the band begins its fade

var _band: TextureRect = null


func _band_texture(ground: Color) -> GradientTexture2D:
	var g := Gradient.new()
	g.offsets = PackedFloat32Array([0.0, 0.22, 0.52, 1.0])
	g.colors = PackedColorArray([
		Color(ground.r, ground.g, ground.b, 0.0),
		Color(ground.r, ground.g, ground.b, ground.a * 0.58),
		Color(ground.r, ground.g, ground.b, ground.a * 0.90),
		Color(ground.r, ground.g, ground.b, ground.a * 0.96),
	])
	var t := GradientTexture2D.new()
	t.gradient = g
	t.fill_from = Vector2(0.0, 0.0)
	t.fill_to = Vector2(0.0, 1.0)
	t.width = 4
	t.height = 256
	return t


# ── THE PLATE ─────────────────────────────────────────────────────────
# The text's ground hugs the text. `_measure` is the body's twin holding
# the WHOLE line (the body itself holds only what has been typed so far),
# so the plate is the line's final size from its first character and does
# not grow as the words appear.
const PLATE_ALPHA := 0.88
const PLATE_PAD_X := 26.0
const PLATE_PAD_TOP := 14.0
const PLATE_PAD_BOT := 18.0

var _plate: Control = null
var _plate_snap: bool = true
var _measure: RichTextLabel = null
var _tapes: Array[ColorRect] = []


func _make_measure() -> void:
	_measure = RichTextLabel.new()
	_measure.bbcode_enabled = true
	_measure.fit_content = false
	_measure.scroll_active = false
	_measure.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_measure.modulate = Color(1, 1, 1, 0)       # laid out, never seen
	_measure.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_measure)


## The rect the plate should have now (this box's coordinates): the whole
## line's text, the speaker's name when one is up, and the buffer.
func _plate_target() -> Rect2:
	_sync_measure()
	var cw: float = float(_measure.get_content_width())
	var ch: float = float(_measure.get_content_height())
	if cw < 2.0 or ch < 2.0:
		return Rect2()
	var r := Rect2(Vector2(_body.offset_left, _body.offset_top), Vector2(cw, ch))
	if _speaker != null and _speaker.visible and _speaker.text != "":
		var ss: Vector2 = _speaker.get_minimum_size()
		r = r.merge(Rect2(_speaker.position, Vector2(ss.x, ss.y + 4.0)))
	return r.grow_individual(PLATE_PAD_X, PLATE_PAD_TOP, PLATE_PAD_X, PLATE_PAD_BOT)


func _update_plate(delta: float) -> void:
	if _plate == null or _measure == null or _body == null:
		return
	var want: Rect2 = _plate_target()
	if want.size.x < 2.0:
		_plate.visible = false
		_plate_snap = true
		return
	_plate.visible = true
	if _plate_snap:
		_plate_snap = false
		_plate.position = want.position
		_plate.size = want.size
	else:
		var k: float = 1.0 - exp(-delta * 16.0)
		_plate.position = _plate.position.lerp(want.position, k)
		_plate.size = _plate.size.lerp(want.size, k)
	# the paper's tape rides its top-left corner; the terminal's rule its top edge
	for i in _tapes.size():
		if is_instance_valid(_tapes[i]):
			_tapes[i].position = _plate.position + Vector2(20.0 + 100.0 * i, -11.0 - 2.0 * i)
	if _rule != null and _variant == SkinDB.DLG_TERMINAL and _rule.texture != null:
		_rule.position = _plate.position
		_rule.size = Vector2(_plate.size.x, 2.0)


func _build_standard() -> void:
	var pad: Array = _skin.get("dlg_pad", [22.0, 48.0, 28.0, 48.0])
	# Box height is viewport-relative so the column reaches from just
	# below mid-screen down to the bottom on any resolution/letterbox.
	var vp_h: float = 720.0
	var vpr := get_viewport_rect()
	if vpr.size.y > 1.0:
		vp_h = vpr.size.y
	# (2026-10-27, the Deck: "text over portraits is wrong. bring text lower")
	# the eyes sit ~44 % down now, so the box starts below the chin: ~31 %
	_std_box_h = clampf(vp_h * 0.31, 230.0, 340.0)
	offset_top = -_std_box_h
	offset_bottom = 0.0
	custom_minimum_size.y = _std_box_h
	_std_inner_top = float(pad[0]) + 6.0
	_std_inner_bot = float(pad[2]) + 18.0

	# THE PLATE (2026-11-09) replaces the reading band. The band was the
	# skin's ground as a fade across the WHOLE width of the bottom third —
	# over the set, over the portrait's shoulders. The user: "the white box
	# is obscuring too much, it should just be behind the text with a bit of
	# edge buffer. i keep saying this, I want to feature the assets and art,
	# the text is important, but everything is important." So the ground is
	# a soft-edged plate the size of THIS line's text (and the speaker's
	# name), plus a buffer — _update_plate sizes it every frame.
	var ground: Color = _skin.get("dlg_bg", Color(0.03, 0.025, 0.02, 0.96))
	var plate := Panel.new()
	plate.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var pst := StyleBoxFlat.new()
	pst.bg_color = Color(ground.r, ground.g, ground.b, ground.a * PLATE_ALPHA)
	pst.set_corner_radius_all(12)
	pst.shadow_color = Color(ground.r, ground.g, ground.b, ground.a * 0.34)
	pst.shadow_size = 16                      # the feathered edge
	pst.anti_aliasing = true
	plate.add_theme_stylebox_override("panel", pst)
	add_child(plate)
	_plate = plate
	_plate_snap = true

	# The panel stays transparent; it only carries the content margins.
	_bg = Panel.new()
	_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.0, 0.0, 0.0, 0.0)
	style.set_border_width_all(0)
	style.content_margin_top    = pad[0] + 4
	style.content_margin_right  = pad[1]
	style.content_margin_bottom = pad[2]
	style.content_margin_left   = pad[3]
	_bg.add_theme_stylebox_override("panel", style)
	add_child(_bg)

	# No rule bar; keep the node so the reference stays valid.
	_rule = TextureRect.new()
	add_child(_rule)

	# Speaker name: small tracked caps above the body (Cinzel on the
	# literary skins, Inter on suburban), a 2 px edge instead of the old
	# third-of-the-size outline.
	_speaker = Label.new()
	_speaker.position = Vector2(pad[3], -37.0)
	var sc: float = Settings.get_text_scale()
	_apply_font(_speaker, _skin.get("spk_font", SkinDB.F_CINZEL),
				int(READ_SPK_PX * sc),
				_skin.get("spk_color", Color(0.96, 0.82, 0.42)), true)
	_speaker.visible = false
	add_child(_speaker)

	_spk_rule = ColorRect.new()
	_spk_rule.visible = false
	_spk_rule.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_spk_rule)

	# Body: top-aligned, no scrollbar; auto-fit (_fit_body_size) steps the
	# size down for long passages so nothing scrolls or clips.
	_body_font_path = _skin.get("txt_font", SkinDB.F_LITERATA)
	_body_base_size = int(READ_BODY_PX * sc)
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
					_skin.get("txt_color", Color(0.98, 0.97, 0.94)), true)
	add_child(_body)
	_make_measure()

	# Advance cursor
	_cursor = Label.new()
	_cursor.text = CURSOR_CHAR
	_apply_font(_cursor, _skin.get("spk_font", SkinDB.F_CINZEL), int(12 * sc),
				_skin.get("cursor_col", Color(0.78, 0.66, 0.29)), true)
	_cursor.visible = false
	add_child(_cursor)
	_anchor_to("center")


## (2026-10-17, the user: "vol 1-4 visual novel UIs need to be brought up
## to 5-7 standard") The terminal (vol 3) and paper (vol 4) boxes keep their
## look but read like the standard one: the same viewport-relative height,
## reading-size type, the measured column and auto-fit instead of a 13-15 px
## face in a scrolling 220 px strip.
func _size_reading_box(inner_top: float, inner_bot: float) -> void:
	var vp_h: float = 720.0
	var vpr := get_viewport_rect()
	if vpr.size.y > 1.0:
		vp_h = vpr.size.y
	# (2026-10-27, the Deck: "text over portraits is wrong. bring text lower")
	# the eyes sit ~44 % down now, so the box starts below the chin: ~31 %
	_std_box_h = clampf(vp_h * 0.31, 230.0, 340.0)
	offset_top = -_std_box_h
	offset_bottom = 0.0
	custom_minimum_size.y = _std_box_h
	_std_inner_top = inner_top
	_std_inner_bot = inner_bot


func _build_terminal() -> void:
	var pad: Array = _skin.get("dlg_pad", [20.0, 40.0, 20.0, 40.0])
	_size_reading_box(float(pad[0]) + 6.0, float(pad[2]) + 20.0)

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
	_bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_bg)
	# (2026-11-09) the terminal's panel hugs the text too (THE PLATE)
	_bg.set_anchors_preset(Control.PRESET_TOP_LEFT)
	_plate = _bg
	_plate_snap = true

	var rule_stops: Array = _skin.get("rule", [])
	if rule_stops.size() > 0:
		_rule = TextureRect.new()
		_rule.texture = SkinDB.make_rule_tex(rule_stops)
		_rule.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		_rule.stretch_mode = TextureRect.STRETCH_SCALE
		_rule.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(_rule)
	else:
		_rule = TextureRect.new()
		add_child(_rule)

	var sc: float = Settings.get_text_scale()
	_speaker = Label.new()
	_speaker.position = Vector2(pad[3], -34.0)
	_apply_font(_speaker, _skin.get("spk_font", SkinDB.F_SPACEMONO),
				int(maxf(float(_skin.get("spk_size", 11)), float(READ_SPK_PX)) * sc),
				_skin.get("spk_color", Color(0.0, 0.78, 1.0)), true)
	_speaker.visible = false
	add_child(_speaker)

	_spk_rule = ColorRect.new()
	_spk_rule.visible = false
	_spk_rule.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_spk_rule)

	# a monospace face sets wide: 0.86 of the reading size holds the measure
	_body_font_path = _skin.get("txt_font", SkinDB.F_SPACEMONO)
	_body_base_size = int(maxf(float(_skin.get("txt_size", 13)), READ_BODY_PX * 0.86) * sc)
	_body = RichTextLabel.new()
	_body.bbcode_enabled = true
	_body.fit_content    = false
	_body.scroll_active  = false
	_body.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_body.offset_top    = pad[0] + 6
	_body.offset_bottom = -pad[2] - 20
	_body.offset_left   = pad[3]
	_body.offset_right  = -pad[1]
	_apply_rtl_font(_body, _body_font_path, _body_base_size,
					_skin.get("txt_color", Color(0.78, 0.84, 0.94)), true)
	add_child(_body)
	_make_measure()

	_cursor = Label.new()
	_cursor.text = CURSOR_CHAR
	_apply_font(_cursor, _skin.get("spk_font", SkinDB.F_SPACEMONO), int(14 * sc),
				_skin.get("cursor_col", Color(0.0, 0.78, 1.0)))
	_cursor.visible = false
	add_child(_cursor)
	_anchor_to("center")


func _build_paper() -> void:
	var pad: Array  = _skin.get("dlg_pad", [24.0, 36.0, 24.0, 36.0])
	# the name sits on the paper's first line; the body starts under it
	var name_drop: float = 40.0 * Settings.get_text_scale()
	_size_reading_box(float(pad[0]) + 22.0 + name_drop, float(pad[2]) + 20.0)

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
	_bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_bg)
	# (2026-11-09) the sheet of paper is the size of what is typed on it
	# (THE PLATE); the tape rides its top-left corner
	_bg.set_anchors_preset(Control.PRESET_TOP_LEFT)
	_plate = _bg
	_plate_snap = true

	# Tape strips
	var tape_col: Color = _skin.get("tape_color", Color(1.0, 0.86, 0.39, 0.5))
	_tapes.clear()
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

	_spk_rule = ColorRect.new()
	_spk_rule.visible = false
	_spk_rule.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_spk_rule)

	_body_font_path = _skin.get("txt_font", SkinDB.F_ELITE)
	_body_base_size = int(maxf(float(_skin.get("txt_size", 15)), READ_BODY_PX * 0.92) * sc)
	_body = RichTextLabel.new()
	_body.bbcode_enabled = true
	_body.fit_content    = false
	_body.scroll_active  = false
	_body.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_body.offset_top    = pad[0] + 22 + name_drop
	_body.offset_bottom = -pad[2] - 20
	_body.offset_left   = pad[3]
	_body.offset_right  = -pad[1]
	_apply_rtl_font(_body, _body_font_path, _body_base_size,
					_skin.get("txt_color", Color(0.10, 0.10, 0.10)), true)
	add_child(_body)
	_make_measure()

	_cursor = Label.new()
	_cursor.text = CURSOR_CHAR
	_apply_font(_cursor, _skin.get("txt_font", SkinDB.F_ELITE), int(14 * sc),
				_skin.get("cursor_col", Color(0.04, 0.04, 0.04)))
	_cursor.visible = false
	add_child(_cursor)
	_anchor_to("center")


# ── Typewriter ────────────────────────────────────────────────────────────────

func _start_type(text: String) -> void:
	_full_text  = text
	_char_idx   = 0
	_typing     = true
	_char_timer = 0.0
	_cursor.visible = false
	# THE REVEAL (2026-11-10): the body holds the WHOLE line from the first
	# character and shows it a character at a time (visible_characters,
	# counted AFTER the line is shaped), so every word is on its final line
	# from its first letter. Before, the body held only the typed part: a
	# half-typed word fitted on the upper line, ran past the plate's edge,
	# then jumped down a line when its last letters arrived.
	_body.visible_characters_behavior = TextServer.VC_CHARS_AFTER_SHAPING
	_body.visible_characters = 0
	_body.text = text
	_fit_body_size(text)
	# (pass 82) The first line after a setup() measures before the label
	# has a layout and falls back to the character-count guess, which
	# clipped a five-line passage's last line. Measure again one frame
	# later, when get_content_height() is real.
	_refit_pending = true
	call_deferred("_refit_once")


var _refit_pending: bool = false


func _refit_once() -> void:
	if not _refit_pending or _body == null or _full_text == "":
		return
	_refit_pending = false
	_fit_body_size(_full_text)
	_body.visible_characters = _char_idx if _typing else -1


# Auto-fit: keep the big size for short/medium lines; step the font
# down toward a floor for long passages so the whole block fits the
# box top-to-bottom without needing a scrollbar. Every skin.
func _fit_body_size(text: String) -> void:
	if _body == null or _body_font_path == "":
		return
	var col: Color = _skin.get("txt_color", Color(0.98, 0.97, 0.94))
	var vis: String = _substr_visible(text, _count_visible(text))
	var floor_size: int = maxi(16, int(_body_base_size * 0.5))
	var size: int = _body_base_size
	# (2026-11-10) Measured on the hidden twin at the body's own column, so
	# the body's text is never touched while it types. A long passage first
	# gets a TALLER box (the text rises, up to BOX_MAX_FRAC of the screen);
	# only a passage too long for that has its type stepped down.
	var box_h: float = _std_box_h
	if _measure != null and vis != "":
		_sync_measure()
		_apply_rtl_font(_measure, _body_font_path, size, col, true)
		_measure.text = text
		var ch: float = float(_measure.get_content_height())
		if ch <= 1.0:
			# Layout not ready (first frame): the character-count guess;
			# _refit_once measures for real a frame later.
			size = _fit_size_by_count(text)
		else:
			var max_h: float = maxf(_std_box_h, _viewport_h() * BOX_MAX_FRAC)
			box_h = clampf(ch + _std_inner_top + _std_inner_bot, _std_box_h, max_h)
			var avail: float = box_h - _std_inner_top - _std_inner_bot
			while ch > avail and size > floor_size:
				size -= 2
				_apply_rtl_font(_measure, _body_font_path, size, col, true)
				ch = float(_measure.get_content_height())
	else:
		size = _fit_size_by_count(text)
	_set_box_h(box_h)
	_apply_rtl_font(_body, _body_font_path, size, col, true)
	if _measure != null:
		_sync_measure()
		_apply_rtl_font(_measure, _body_font_path, size, col, true)
		_measure.text = text


## How much of the screen's height a long passage's box may take.
const BOX_MAX_FRAC := 0.46


func _viewport_h() -> float:
	var vpr := get_viewport_rect()
	return vpr.size.y if vpr.size.y > 1.0 else 720.0


func _set_box_h(h: float) -> void:
	if absf(offset_top + h) < 0.5:
		return
	offset_top = -h
	custom_minimum_size.y = h


func _sync_measure() -> void:
	_measure.offset_left = _body.offset_left
	_measure.offset_right = _body.offset_right
	_measure.offset_top = _body.offset_top
	_measure.offset_bottom = _body.offset_bottom


# Fallback shrink when we can't measure (layout not ready): scale the
# font down by visible-character count toward the floor.
func _fit_size_by_count(text: String) -> int:
	var n: int = _count_visible(text)
	if n <= 260:
		return _body_base_size
	var t: float = clampf(float(n - 260) / 340.0, 0.0, 1.0)
	return int(round(lerp(float(_body_base_size), float(_body_base_size) * 0.55, t)))


func _process(delta: float) -> void:
	_update_plate(delta)
	if _typing:
		_char_timer -= delta
		# (2026-11-10) As many characters as the frame's time covers. It was
		# one character a frame at most, so the type's speed was the frame
		# rate's: FAST (10 ms) could not beat 16.7 ms at 60 fps, and a heavy
		# set at 30 fps typed every speed at 33 ms.
		var base := Settings.get_char_delay_ms() / 1000.0
		var total: int = _count_visible(_full_text)
		var steps: int = 0
		while _char_timer <= 0.0 and _char_idx < total:
			steps += 1
			_char_idx += 1
			# Punctuation-aware pacing (2026-07 presentation wave): the
			# reveal breathes with the prose instead of ticking flatly.
			# Sentence stops hold longest, clause marks hold a little;
			# everything scales off the user's char-delay setting.
			_char_timer += base * _pause_mult_after(_substr_visible(_full_text, _char_idx))
		if steps > 0:
			_char_timer = maxf(_char_timer, -base)      # a hitch does not bank a burst
			_body.visible_characters = _char_idx
			if _char_idx >= total:
				_typing     = false
				_body.visible_characters = -1
				_cursor.visible = true
	elif _cursor != null and _cursor.visible:
		_cursor_t += delta
		var a: float = 0.4 + 0.6 * (0.5 + 0.5 * sin(_cursor_t * TAU / 1.5))
		_cursor.modulate.a = a
		_place_cursor()


# Multiplier for the delay AFTER the character just revealed (the
# last visible char of `shown`). Ellipses read as the middle dot of
# "..." so the hold lands once, on the final dot.
func _pause_mult_after(shown: String) -> float:
	if shown.is_empty():
		return 1.0
	var c: String = shown[shown.length() - 1]
	match c:
		".", "!", "?":
			return 7.0
		"—", "…":
			return 5.0
		";", ":":
			return 4.0
		",":
			return 2.6
		"\n":
			return 3.0
		_:
			return 1.0


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
	# in the plate's bottom-right corner, past the text's right edge (it sat
	# at the corner of the whole column box, far from a short line)
	if _plate != null and _plate.visible:
		_cursor.position = _plate.position + _plate.size - Vector2(21.0, 25.0)
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


func _apply_font(lbl: Label, font_path: String, size: int, col: Color, reading: bool = false) -> void:
	if ResourceLoader.exists(font_path):
		var ff: FontFile = load(font_path)
		if reading:
			# Tracked caps for the nameplate: the glyph spacing lives on a
			# FontVariation, the file itself untouched.
			var fv := FontVariation.new()
			fv.base_font = ff
			fv.set_spacing(TextServer.SPACING_GLYPH, 2)
			lbl.add_theme_font_override("font", fv)
		else:
			lbl.add_theme_font_override("font", ff)
	lbl.add_theme_font_size_override("font_size", size)
	lbl.add_theme_color_override("font_color", col)
	if reading:
		# No outline — the band under the text carries the legibility
		# now; a 1 px shadow under light lettering only (a dark edge on
		# gold caps over a dark band just dimmed the name).
		lbl.add_theme_constant_override("outline_size", 0)
		var shadow: Color = Color(0.0, 0.0, 0.0, 0.0)
		if col.get_luminance() > 0.5:
			shadow = Color(0.0, 0.0, 0.0, 0.5)
		lbl.add_theme_color_override("font_shadow_color", shadow)
		lbl.add_theme_constant_override("shadow_offset_x", 0)
		lbl.add_theme_constant_override("shadow_offset_y", 1)
		lbl.add_theme_constant_override("shadow_outline_size", 1)
	else:
		lbl.add_theme_color_override("font_outline_color", _outline_for(col))
		lbl.add_theme_constant_override("outline_size", maxi(4, int(size * 0.34)))


func _apply_rtl_font(rtl: RichTextLabel, font_path: String, size: int, col: Color, reading: bool = false) -> void:
	if ResourceLoader.exists(font_path):
		var ff: FontFile = load(font_path)
		rtl.add_theme_font_override("normal_font",  ff)
		# (pass 85) bold is the face's 600 weight when it has a wght axis
		var fb: Font = SkinDB.weighted(font_path, 600.0)
		rtl.add_theme_font_override("bold_font",    fb if fb != null else ff)
		# The italic face is the real italic when the body is Literata;
		# every other face slants itself (no italic file shipped).
		var it_path: String = _italic_for(font_path)
		if it_path != "" and ResourceLoader.exists(it_path):
			var fi: FontFile = load(it_path)
			rtl.add_theme_font_override("italics_font", fi)
		else:
			rtl.add_theme_font_override("italics_font", ff)
	rtl.add_theme_font_size_override("normal_font_size",  size)
	rtl.add_theme_font_size_override("bold_font_size",    size)
	rtl.add_theme_font_size_override("italics_font_size", size)
	rtl.add_theme_color_override("default_color", col)
	if reading:
		# THE READING BAND: no outline; generous leading; a 1 px shadow
		# under light text only (dark text on the cream band gets none).
		rtl.add_theme_constant_override("outline_size", 0)
		rtl.add_theme_constant_override("line_separation", int(round(size * READ_LEADING)))
		var shadow: Color = Color(0.0, 0.0, 0.0, 0.0)
		if col.get_luminance() > 0.5:
			shadow = Color(0.0, 0.0, 0.0, 0.45)
		rtl.add_theme_color_override("font_shadow_color", shadow)
		rtl.add_theme_constant_override("shadow_offset_x", 0)
		rtl.add_theme_constant_override("shadow_offset_y", 1)
		rtl.add_theme_constant_override("shadow_outline_size", 1)
	else:
		rtl.add_theme_color_override("font_outline_color", _outline_for(col))
		rtl.add_theme_constant_override("outline_size", maxi(4, int(size * 0.34)))


static func _italic_for(font_path: String) -> String:
	if font_path == SkinDB.F_LITERATA:
		return SkinDB.F_LITERATA_I
	return ""


func _add_tape_strip(pos: Vector2, w: int, h: int, angle_deg: float, col: Color) -> void:
	var strip := ColorRect.new()
	strip.color              = col
	strip.size               = Vector2(w, h)
	strip.position           = pos
	strip.pivot_offset       = Vector2(w * 0.5, h * 0.5)
	strip.rotation_degrees   = angle_deg
	add_child(strip)
	_tapes.append(strip)
