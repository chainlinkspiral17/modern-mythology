extends Control
## Chapter title plate — the book's chapter opening, finally shown.
##
## Scene JSON has carried `"title"` for 177 of 245 vol5-7 scenes with
## nobody displaying it. GameEngine now presents this card at every
## (vol, chapter) boundary: an opaque plate in the InterludePanel
## register — rule-diamond-rule ornaments, a small-caps kicker
## (VOLUME · CHAPTER), the chapter title in IM Fell — that fades in
## with a rise, holds, and can be advanced early. The card handles its
## own advance input; GameEngine holds its transition lock until the
## dismiss callback fires.
##
## Built procedurally like every other VN component; no .tscn needed
## (GameEngine news it up and adds it above the fade veil).

var _callback: Callable
var _center: VBoxContainer = null
var _kicker: Label = null
var _main: Label = null
var _state: String = "in"        # in | hold | out
var _hold_left: float = 0.0
var _base_top: float = 0.0
var _base_bottom: float = 0.0

const C_GOLD_DIM := Color(0.78, 0.66, 0.29, 0.45)
const HOLD_S := 2.4              # auto-advance after the plate has sat


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	_build()


# The endpaper plate behind the type — one dyed sheet per volume,
# three variants so consecutive chapters never repeat. The flat
# field stays underneath as the fallback (and as the floor the
# plate's deckle edges fall to).
const PLATE_DIR := "res://assets/vn/plates/"
const PLATE_VARIANTS := 3
var _plate: TextureRect = null


func _build() -> void:
	var bg := ColorRect.new()
	bg.color = Color(0.01, 0.008, 0.005, 1.0)
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	_plate = TextureRect.new()
	_plate.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_plate.stretch_mode = TextureRect.STRETCH_SCALE
	_plate.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_plate.visible = false
	add_child(_plate)

	_center = VBoxContainer.new()
	_center.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_center.custom_minimum_size = Vector2(820, 0)
	_center.offset_left = -410
	_center.offset_right = 410
	_center.alignment = BoxContainer.ALIGNMENT_CENTER
	_center.add_theme_constant_override("separation", 22)
	add_child(_center)

	_center.add_child(_ornament())

	_kicker = Label.new()
	_kicker.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		_kicker.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
	_kicker.add_theme_font_size_override("font_size", 15)
	_kicker.add_theme_color_override("font_color", Color(0.65, 0.60, 0.50))
	_center.add_child(_kicker)

	_main = Label.new()
	_main.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_main.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	if ResourceLoader.exists(SkinDB.F_IMFELL_R):
		_main.add_theme_font_override("font", load(SkinDB.F_IMFELL_R) as Font)
	_main.add_theme_font_size_override("font_size", 40)
	_main.add_theme_color_override("font_color", Color(0.93, 0.90, 0.83))
	_center.add_child(_main)

	_center.add_child(_ornament())
	_base_top = _center.offset_top
	_base_bottom = _center.offset_bottom


func _ornament() -> Control:
	# rule — diamond — rule, matching InterludePanel's book-plate divider.
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


# vol/chapter pick the sheet; the plate breathes in a hair slower
# than the type so the page feels laid down, not switched on.
# chapter arrives as whatever the scene JSON holds. Vol 5 numbers its
# chapters in ROMAN NUMERALS ("I".."XXI") and int("I") is 0 — which
# for a month meant 26 of Vol 5's 27 scenes wore plate 0 and plate 2
# had never been displayed. Parse the numeral properly; anything
# unparseable hashes, so every plate still rotates.
func _chapter_ordinal(chapter_v: Variant) -> int:
	if chapter_v is int or chapter_v is float:
		return absi(int(chapter_v))
	var s := String(chapter_v).strip_edges().to_upper()
	if s.is_valid_int():
		return absi(int(s))
	var vals := {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
	var total := 0
	var ok := s.length() > 0
	for i in range(s.length()):
		if not vals.has(s[i]):
			ok = false
			break
		var v: int = vals[s[i]]
		if i + 1 < s.length() and vals.has(s[i + 1]) and int(vals[s[i + 1]]) > v:
			total -= v
		else:
			total += v
	if ok:
		return total
	return absi(s.hash())


func set_plate(vol: int, chapter_v: Variant) -> void:
	if _plate == null:
		return
	var chapter := _chapter_ordinal(chapter_v)
	var path := PLATE_DIR + "chapter_v%d_%d.png" % [vol, chapter % PLATE_VARIANTS]
	if not ResourceLoader.exists(path):
		return
	var tex: Texture2D = load(path) as Texture2D
	if tex == null:
		return
	_plate.texture = tex
	_plate.visible = true
	_plate.modulate.a = 0.0
	var tw := create_tween()
	tw.tween_property(_plate, "modulate:a", 1.0, 1.0)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)


func present(kicker: String, title: String, callback: Callable) -> void:
	_callback = callback
	_kicker.text = kicker
	_kicker.visible = kicker != ""
	_main.text = title
	_state = "in"
	_hold_left = HOLD_S
	_center.modulate.a = 0.0
	_center.offset_top = _base_top + 16.0
	_center.offset_bottom = _base_bottom + 16.0
	var tw := create_tween()
	tw.set_parallel(true)
	tw.tween_property(_center, "modulate:a", 1.0, 0.7)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	tw.tween_property(_center, "offset_top", _base_top, 0.7)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	tw.tween_property(_center, "offset_bottom", _base_bottom, 0.7)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	tw.chain().tween_callback(func() -> void:
		if _state == "in":
			_state = "hold")


func _process(delta: float) -> void:
	if _state == "hold":
		_hold_left -= delta
		if _hold_left <= 0.0:
			_dismiss()


func _input(event: InputEvent) -> void:
	if _state == "out" or not visible:
		return
	if event.is_action_pressed("advance"):
		get_viewport().set_input_as_handled()
		_dismiss()


func _dismiss() -> void:
	if _state == "out":
		return
	_state = "out"
	var tw := create_tween()
	tw.tween_property(self, "modulate:a", 0.0, 0.55)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	tw.tween_callback(func() -> void:
		if _callback.is_valid():
			_callback.call())
