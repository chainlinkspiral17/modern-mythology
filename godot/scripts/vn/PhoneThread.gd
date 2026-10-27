extends Control
## PHONE THREAD (2026-10-27). The user, on the Deck: "if a character is
## talking on the phone, their portrait should look like a phone image/text
## message, not in scene with the character." A line marked
## `"via": "text"` (or `"via": "call"`) is not a person in the room: the
## absent party is shown as the phone in the reader's hand — the thread's
## bubbles (theirs on the left, the reader's on the right) or a call screen
## with their name and the call's running time.
##
## Picture content, like a portrait — it sits between the portraits and the
## dialogue band and is not HUD (F4 leaves portraits up, and this stands in
## for one).

const MAX_BUBBLES := 6
const PHONE_SIZE := Vector2(330, 600)
const C_BODY := Color(0.07, 0.07, 0.08, 0.97)
const C_SCREEN := Color(0.95, 0.95, 0.96, 1.0)
const C_HEADER := Color(0.88, 0.89, 0.91, 1.0)
const C_IN := Color(0.86, 0.86, 0.88, 1.0)
const C_OUT := Color(0.18, 0.47, 0.96, 1.0)
const C_INK := Color(0.08, 0.08, 0.10, 1.0)
const C_INK_OUT := Color(1, 1, 1, 1)
const C_CALL := Color(0.10, 0.12, 0.14, 1.0)

var _frame: Panel
var _screen: Panel
var _title: Label
var _sub: Label
var _list: VBoxContainer
var _call_box: VBoxContainer
var _call_name: Label
var _call_time: Label
var _call_t: float = 0.0
var _mode: String = ""              # "" hidden · "text" · "call"
var _party: String = ""             # the absent party: the thread's title
var _side: String = "right"         # (2026-10-27) the side the reader's portrait doesn't hold


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_frame = Panel.new()
	_frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_frame.add_theme_stylebox_override("panel", _box(C_BODY, 38, 0))
	_frame.size = PHONE_SIZE
	add_child(_frame)
	_screen = Panel.new()
	_screen.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_screen.add_theme_stylebox_override("panel", _box(C_SCREEN, 28, 0))
	_screen.position = Vector2(12, 12)
	_screen.size = PHONE_SIZE - Vector2(24, 24)
	_frame.add_child(_screen)
	var head := Panel.new()
	head.mouse_filter = Control.MOUSE_FILTER_IGNORE
	head.add_theme_stylebox_override("panel", _box(C_HEADER, 28, 0, true))
	head.position = Vector2.ZERO
	head.size = Vector2(_screen.size.x, 74)
	_screen.add_child(head)
	_title = _label(24, C_INK, HORIZONTAL_ALIGNMENT_CENTER)
	_title.position = Vector2(0, 18)
	_title.size = Vector2(_screen.size.x, 28)
	head.add_child(_title)
	_sub = _label(15, Color(0.40, 0.40, 0.44), HORIZONTAL_ALIGNMENT_CENTER)
	_sub.position = Vector2(0, 46)
	_sub.size = Vector2(_screen.size.x, 18)
	head.add_child(_sub)
	_list = VBoxContainer.new()
	_list.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_list.alignment = BoxContainer.ALIGNMENT_END
	_list.add_theme_constant_override("separation", 8)
	_list.position = Vector2(12, 84)
	_list.size = Vector2(_screen.size.x - 24, _screen.size.y - 100)
	_screen.add_child(_list)
	_call_box = VBoxContainer.new()
	_call_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_call_box.alignment = BoxContainer.ALIGNMENT_CENTER
	_call_box.position = Vector2(0, 0)
	_call_box.size = _screen.size
	_call_box.add_theme_constant_override("separation", 12)
	_screen.add_child(_call_box)
	_call_name = _label(30, C_INK_OUT, HORIZONTAL_ALIGNMENT_CENTER)
	_call_time = _label(19, Color(0.75, 0.80, 0.85), HORIZONTAL_ALIGNMENT_CENTER)
	_call_box.add_child(_call_name)
	_call_box.add_child(_call_time)
	visible = false
	resized.connect(_place)
	_place()


func _process(delta: float) -> void:
	if _mode == "call" and visible:
		_call_t += delta
		var s: int = int(_call_t)
		_call_time.text = "%d:%02d" % [s / 60, s % 60]


## A line by phone. `outgoing`: the speaker is the reader on screen (their
## bubble goes right); otherwise the speaker is the absent party.
func push(speaker: String, text: String, outgoing: bool, via: String) -> void:
	if via != "call":
		via = "text"
	if not outgoing:
		if _party != speaker or _mode != via:
			_reset(speaker, via)
	elif _mode != via:
		_reset(_party, via)
	visible = true
	if via == "call":
		return
	var bubble := PanelContainer.new()
	bubble.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bubble.add_theme_stylebox_override("panel", _box(C_OUT if outgoing else C_IN, 16, 10))
	var l := _label(20, C_INK_OUT if outgoing else C_INK, HORIZONTAL_ALIGNMENT_LEFT)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size = Vector2(minf(230.0, 16.0 + 10.5 * float(text.length())), 0)
	l.text = text
	bubble.add_child(l)
	var row := HBoxContainer.new()
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.alignment = BoxContainer.ALIGNMENT_END if outgoing else BoxContainer.ALIGNMENT_BEGIN
	row.add_child(bubble)
	_list.add_child(row)
	while _list.get_child_count() > MAX_BUBBLES:
		var old: Node = _list.get_child(0)
		_list.remove_child(old)
		old.queue_free()


func set_side(side: String) -> void:
	if side != _side:
		_side = side
		_place()


func hide_thread() -> void:
	visible = false
	_mode = ""
	_party = ""
	for c: Node in _list.get_children():
		c.queue_free()


func is_showing() -> bool:
	return visible


func _reset(party: String, via: String) -> void:
	for c: Node in _list.get_children():
		c.queue_free()
	_party = party
	_mode = via
	_call_t = 0.0
	var calling: bool = via == "call"
	_list.visible = not calling
	_call_box.visible = calling
	_title.get_parent().visible = not calling
	(_screen.get_theme_stylebox("panel") as StyleBoxFlat).bg_color = C_CALL if calling else C_SCREEN
	_title.text = party
	_sub.text = "text message"
	_call_name.text = party
	_call_time.text = "0:00"


# Where the absent party's portrait would stand: on the side the reader's
# portrait does NOT hold (set_side), from near the top to above the dialogue
# band — never over a face, never under the text (2026-10-27, the Deck:
# "Text from Diego on top portrait").
func _place() -> void:
	if _frame == null:
		return
	var vs: Vector2 = size
	var sc: float = clampf(vs.y * 0.58 / PHONE_SIZE.y, 0.45, 1.2)
	_frame.scale = Vector2(sc, sc)
	var cx: float = vs.x * (0.27 if _side == "left" else 0.73)
	_frame.position = Vector2(cx - PHONE_SIZE.x * sc * 0.5, vs.y * 0.04)


func _box(c: Color, radius: int, pad: int, top_only: bool = false) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = c
	sb.corner_radius_top_left = radius
	sb.corner_radius_top_right = radius
	sb.corner_radius_bottom_left = 0 if top_only else radius
	sb.corner_radius_bottom_right = 0 if top_only else radius
	sb.content_margin_left = pad
	sb.content_margin_right = pad
	sb.content_margin_top = pad * 0.7
	sb.content_margin_bottom = pad * 0.7
	return sb


func _label(px: int, c: Color, align: HorizontalAlignment) -> Label:
	var l := Label.new()
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.add_theme_font_size_override("font_size", px)
	l.add_theme_color_override("font_color", c)
	l.horizontal_alignment = align
	l.add_theme_constant_override("outline_size", 0)     # the project theme's outline is for text over pictures
	return l
