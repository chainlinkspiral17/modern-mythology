extends Control
## UnlockToast — small, subtle bottom-right corner notification.
## Slides up from below, holds, fades out. Non-blocking.
##
## Usage: call show_toast({"title": "...", "subtitle": "..."}).
## Queues multiple notifications, plays them in sequence.

const C_GOLD     := Color(0.78, 0.66, 0.29)
const C_BG       := Color(0.039, 0.031, 0.020, 0.92)
const C_BORDER   := Color(0.70, 0.55, 0.24, 0.45)
const C_TXT      := Color(0.83, 0.79, 0.69)
const C_DIM      := Color(0.55, 0.51, 0.42, 0.85)

const HOLD_TIME  := 3.6
const FADE_IN    := 0.32
const FADE_OUT   := 0.45
const SLIDE_PX   := 24.0
const CARD_W     := 320
const CARD_H     := 64
const MARGIN     := 16

var _queue: Array[Dictionary] = []
var _card: Panel = null
var _playing: bool = false


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	z_index = 100


func show_toast(data: Dictionary) -> void:
	_queue.append(data)
	if not _playing:
		_play_next()


func _play_next() -> void:
	if _queue.is_empty():
		_playing = false
		if _card != null:
			_card.queue_free()
			_card = null
		return
	_playing = true
	var data: Dictionary = _queue.pop_front()
	_build_card(data)
	_animate()


func _build_card(data: Dictionary) -> void:
	if _card != null:
		_card.queue_free()
	_card = Panel.new()
	_card.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	_card.offset_right  = -float(MARGIN)
	_card.offset_bottom = -float(MARGIN)
	_card.offset_left   = -float(MARGIN + CARD_W)
	_card.offset_top    = -float(MARGIN + CARD_H)
	_card.mouse_filter  = Control.MOUSE_FILTER_IGNORE
	var st := StyleBoxFlat.new()
	st.bg_color     = C_BG
	st.border_color = C_BORDER
	st.set_border_width_all(1)
	st.content_margin_top    = 8
	st.content_margin_right  = 12
	st.content_margin_bottom = 8
	st.content_margin_left   = 12
	_card.add_theme_stylebox_override("panel", st)
	add_child(_card)

	# Left gold accent bar
	var accent := ColorRect.new()
	accent.color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.85)
	accent.set_anchors_preset(Control.PRESET_LEFT_WIDE)
	accent.offset_right = 3
	accent.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_card.add_child(accent)

	var vbox := VBoxContainer.new()
	vbox.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	vbox.offset_left = 14
	vbox.offset_right = -10
	vbox.offset_top = 8
	vbox.offset_bottom = -8
	vbox.add_theme_constant_override("separation", 2)
	vbox.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_card.add_child(vbox)

	var tag := Label.new()
	tag.text = "✦  UNLOCKED"
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		tag.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
	tag.add_theme_font_size_override("font_size", 12)
	tag.add_theme_color_override("font_color", Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.7))
	vbox.add_child(tag)

	var title := Label.new()
	title.text = str(data.get("title", ""))
	if ResourceLoader.exists(SkinDB.F_IMFELL_R):
		title.add_theme_font_override("font", load(SkinDB.F_IMFELL_R) as Font)
	title.add_theme_font_size_override("font_size", 14)
	title.add_theme_color_override("font_color", C_TXT)
	title.clip_text = true
	vbox.add_child(title)

	var sub_text: String = str(data.get("subtitle", ""))
	if sub_text != "":
		var sub := Label.new()
		sub.text = sub_text
		if ResourceLoader.exists(SkinDB.F_IMFELL_I):
			sub.add_theme_font_override("font", load(SkinDB.F_IMFELL_I) as Font)
		sub.add_theme_font_size_override("font_size", 12)
		sub.add_theme_color_override("font_color", C_DIM)
		sub.clip_text = true
		vbox.add_child(sub)


func _animate() -> void:
	if _card == null:
		return
	_card.modulate.a = 0.0
	_card.position.y += SLIDE_PX
	var tween := create_tween()
	tween.set_parallel(true)
	tween.tween_property(_card, "modulate:a", 1.0, FADE_IN).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	tween.tween_property(_card, "position:y", _card.position.y - SLIDE_PX, FADE_IN).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	tween.chain().tween_interval(HOLD_TIME)
	tween.chain().tween_property(_card, "modulate:a", 0.0, FADE_OUT).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN)
	tween.chain().tween_callback(_play_next)
