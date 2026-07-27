extends Control
class_name SalmonberryTown
## SALMONBERRY · the walkable town · Wave A.
##
## The adventure half arrives: instead of picking the month from a
## menu, you WALK Salmonberry — Vovo's house at the river mouth, Main
## Street (store · cafe · library · church), the dock and the cannery
## on the bay, the school, Estelle's gray house, the woods above, the
## beach path below. Walk anywhere free of charge; press E at a place
## to see what this month offers THERE (the same activities.json data
## the menu used — the town is an interface, not a second economy).
## Choosing an activity spends the month and returns to the year loop.
##
## Painted in _draw on the E2 MudflatWalk pattern (one Control, no
## tiles to manage), with the season repainting the palette as the
## year turns. The kid is a SlowstockSprite (the coat Vovo had
## waiting).
##
## Emits: activity_chosen(act: Dictionary) · quit (back to the month
## menu). Owned as a child overlay by SalmonberryYear (the overlay-
## combat pattern — the year scene never loses its place).

signal activity_chosen(act: Dictionary)
signal quit

const WALKER_SPRITE := "res://resources/games/vol7/salmonberry/sprites/walker.json"

const SPEED := 190.0
const REACH := 62.0

# ── the town plan (design space 1280x720) ──
# One screen, the whole town — Salmonberry is small on purpose.
const PLACES := {
	"home":    {"pos": Vector2(120, 430), "name": "VOVO'S HOUSE", "who": "Vovo",
		"empty": "The kitchen smells of bread. Vovo is out back. The house holds you either way."},
	"store":   {"pos": Vector2(300, 250), "name": "TUCK'S STORE", "who": "Tuck",
		"empty": "Tuck nods from behind the register. Nothing needs running today."},
	"cafe":    {"pos": Vector2(500, 250), "name": "THE CAFE", "who": "Ruth",
		"empty": "Ruth waves you in for a warm-up. The town's news washes over you and out."},
	"library": {"pos": Vector2(700, 250), "name": "THE LIBRARY", "who": "Iris",
		"empty": "Iris looks up, marks her page, nods. The one warm room on Main is open."},
	"church":  {"pos": Vector2(900, 250), "name": "THE CHURCH", "who": "",
		"empty": "The church is quiet. The notice board lists the supper, when there is one."},
	"estelle": {"pos": Vector2(1110, 300), "name": "THE GRAY HOUSE", "who": "Estelle",
		"empty": "The curtain moves. The light in the window that faces the bar is off, in daylight."},
	"school":  {"pos": Vector2(1050, 130), "name": "THE SCHOOL", "who": "",
		"empty": "Chalk dust and the flag line clinking. School keeps its own hours."},
	"woods":   {"pos": Vector2(620, 90),  "name": "THE WOODS", "who": "Boyd",
		"empty": "The treeline stands there being the treeline. Boyd is not up a spruce today. Probably."},
	"dock":    {"pos": Vector2(430, 560), "name": "THE DOCK", "who": "Del",
		"empty": "Del is out on the water. The nets hang. The bar, beyond, lies flat and lies."},
	"cannery": {"pos": Vector2(760, 545), "name": "THE CANNERY", "who": "Manny",
		"empty": "The line is between runs. The gulls wait anyway. Gulls are optimists."},
	"beach":   {"pos": Vector2(150, 620), "name": "THE BEACH PATH", "who": "",
		"empty": "The beach goes both ways for miles. It will still be there when you have a month to spend on it."},
}

# ── seasonal palettes · the year repaints the town ──
# buckets: 0-1 fall gold · 2-5 winter gray · 7 early spring · 8-9 summer
const SEASONS := {
	"fall":   {"sky": Color("c8b890"), "ground": Color("8a8060"), "sea": Color("4a6070"), "fir": Color("3a4a34")},
	"winter": {"sky": Color("b0b4b0"), "ground": Color("787a72"), "sea": Color("3a4a52"), "fir": Color("2e3a30")},
	"spring": {"sky": Color("b8c4b0"), "ground": Color("7a8a62"), "sea": Color("44606c"), "fir": Color("34503a")},
	"summer": {"sky": Color("c0d0c8"), "ground": Color("88985e"), "sea": Color("48687a"), "fir": Color("3a5a3c")},
}

const C_ROAD  := Color("9a9482")
const C_WOOD  := Color("8a6a48")
const C_ROOF  := Color("6a4a38")
const C_GRAY  := Color("8a8e90")
const C_RUST  := Color("9c5a3a")
const C_INK   := Color("23282a")
const C_GOLD  := Color("d8b048")
const C_FOAM  := Color("e8ece8")
const C_RIVER := Color("52707c")

const MONTHS := ["September", "October", "November", "December", "January",
	"February", "March", "April", "May", "June"]

var _pos := Vector2(160, 470)
var _dir := Vector2.ZERO
var _walker := SlowstockSprite.new()
var _month: int = 0
var _acts_by_loc: Dictionary = {}   # loc -> Array[act]
var _bonds: Dictionary = {}
var _season: Dictionary = {}
var _panel: Control = null
var _t: float = 0.0

var _hdr_lbl: Label = null
var _msg_lbl: Label = null
var _hint_lbl: Label = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_to_group("ui")
	_walker.load_from(WALKER_SPRITE)
	_build_ui()
	set_process(true)


func boot(month: int, acts_by_loc: Dictionary, bonds: Dictionary) -> void:
	_month = clampi(month, 0, 9)
	_acts_by_loc = acts_by_loc
	_bonds = bonds
	_season = SEASONS[_season_key()]
	_pos = Vector2(160, 470)
	_hdr_lbl.text = "SALMONBERRY · %s %d" % [MONTHS[_month].to_upper(), (1963 if _month <= 3 else 1964)]
	_msg("the town is one walk wide. E at a place to spend the month there. ESC for the list.")
	queue_redraw()


func _season_key() -> String:
	if _month <= 1: return "fall"
	if _month <= 5: return "winter"
	if _month <= 7: return "spring"
	return "summer"


func _build_ui() -> void:
	_hdr_lbl = Label.new()
	_hdr_lbl.position = Vector2(24, 12)
	_hdr_lbl.add_theme_font_size_override("font_size", 15)
	_hdr_lbl.add_theme_color_override("font_color", C_INK)
	add_child(_hdr_lbl)

	_hint_lbl = Label.new()
	_hint_lbl.position = Vector2(1010, 12)
	_hint_lbl.add_theme_font_size_override("font_size", 12)
	_hint_lbl.add_theme_color_override("font_color", C_INK)
	_hint_lbl.text = "arrows walk · E spend the month · ESC list"
	add_child(_hint_lbl)

	_msg_lbl = Label.new()
	_msg_lbl.position = Vector2(24, 660)
	_msg_lbl.size = Vector2(1100, 50)
	_msg_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_msg_lbl.add_theme_font_size_override("font_size", 15)
	_msg_lbl.add_theme_color_override("font_color", C_INK)
	add_child(_msg_lbl)


func _msg(t: String) -> void:
	_msg_lbl.text = t


# ─── walking ─────────────────────────────────────────────────────

func _process(delta: float) -> void:
	_t += delta
	if _panel != null:
		return
	_dir = Vector2.ZERO
	if Input.is_key_pressed(KEY_LEFT) or Input.is_key_pressed(KEY_A): _dir.x -= 1
	if Input.is_key_pressed(KEY_RIGHT) or Input.is_key_pressed(KEY_D): _dir.x += 1
	if Input.is_key_pressed(KEY_UP) or Input.is_key_pressed(KEY_W): _dir.y -= 1
	if Input.is_key_pressed(KEY_DOWN) or Input.is_key_pressed(KEY_S): _dir.y += 1
	if _dir != Vector2.ZERO:
		_pos += _dir.normalized() * SPEED * delta
		_pos.x = clampf(_pos.x, 40, 1240)
		_pos.y = clampf(_pos.y, 60, 640)
	queue_redraw()


func _place_near() -> String:
	var best := ""
	var best_d := REACH
	for pid in PLACES.keys():
		var d: float = _pos.distance_to(PLACES[pid]["pos"])
		if d < best_d:
			best_d = d
			best = String(pid)
	return best


func _input(event: InputEvent) -> void:
	if not is_visible_in_tree():
		return
	if event is InputEventKey and event.pressed and not event.echo:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			get_viewport().set_input_as_handled()
			if _panel != null:
				_close_panel()
			else:
				quit.emit()
		elif kev.keycode == KEY_E and _panel == null:
			var pid := _place_near()
			if pid != "":
				get_viewport().set_input_as_handled()
				_open_offers(pid)


# ─── the offers panel · what this month can be, here ─────────────

func _open_offers(pid: String) -> void:
	var place: Dictionary = PLACES[pid]
	var acts: Array = _acts_by_loc.get(pid, [])
	if acts.is_empty():
		_msg(String(place.get("empty", "nothing to do here this month.")))
		_sfx("hotspot_look", 0.5)
		return
	_sfx("door_open", 0.5)
	_panel = PanelContainer.new()
	_panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_panel.custom_minimum_size = Vector2(560, 0)
	_panel.offset_left = -280
	_panel.offset_right = 280
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.10, 0.11, 0.10, 0.96)
	sb.set_corner_radius_all(4)
	sb.set_content_margin_all(18)
	_panel.add_theme_stylebox_override("panel", sb)
	add_child(_panel)

	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 8)
	_panel.add_child(v)

	var hdr := Label.new()
	var who := String(place.get("who", ""))
	hdr.text = String(place["name"]) + ("   ·   %s" % who if who != "" else "")
	hdr.add_theme_font_size_override("font_size", 17)
	hdr.add_theme_color_override("font_color", C_GOLD)
	v.add_child(hdr)

	for act_v in acts:
		var act: Dictionary = act_v
		var b := Button.new()
		b.text = "  " + String(act.get("label", "?"))
		b.add_theme_font_size_override("font_size", 14)
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.pressed.connect(func() -> void:
			var chosen := act
			_close_panel()
			activity_chosen.emit(chosen))
		v.add_child(b)

	var back := Button.new()
	back.text = "  · not this month ·  "
	back.add_theme_font_size_override("font_size", 12)
	back.pressed.connect(_close_panel)
	v.add_child(back)
	GamepadMgr.focus_first.call_deferred(_panel)


func _close_panel() -> void:
	if _panel != null and is_instance_valid(_panel):
		_panel.queue_free()
	_panel = null


# ─── the town, painted ───────────────────────────────────────────

func _draw() -> void:
	var sky: Color = _season["sky"]
	var ground: Color = _season["ground"]
	var sea: Color = _season["sea"]
	var fir: Color = _season["fir"]

	# ground plane + sky suggestion at the very top
	draw_rect(Rect2(0, 0, 1280, 720), ground)
	draw_rect(Rect2(0, 0, 1280, 60), sky)
	# the woods band along the top
	draw_rect(Rect2(0, 40, 1280, 50), fir.darkened(0.15))
	for i in range(40):
		var fx := 16.0 + float(i) * 32.0
		_spruce(Vector2(fx, 88.0 + float((i * 37) % 14)), 26.0 + float((i * 53) % 16), fir)
	# the bay along the bottom
	draw_rect(Rect2(0, 580, 1280, 140), sea)
	draw_line(Vector2(0, 582), Vector2(1280, 582), C_FOAM, 2.0)
	var swell := sin(_t * 1.2) * 3.0
	draw_line(Vector2(0, 610 + swell), Vector2(1280, 612 + swell), Color(C_FOAM.r, C_FOAM.g, C_FOAM.b, 0.25), 1.0)
	# the river down the west edge, mouth at the bay
	draw_rect(Rect2(0, 60, 46, 560), C_RIVER)
	# main street
	draw_rect(Rect2(60, 320, 1160, 44), C_ROAD)
	draw_rect(Rect2(60, 340, 1160, 3), Color(C_ROAD.r * 0.85, C_ROAD.g * 0.85, C_ROAD.b * 0.85))

	# ── buildings ──
	_house(PLACES["home"]["pos"], Vector2(120, 74), C_WOOD, C_RUST, true)       # Vovo's
	_shopfront(PLACES["store"]["pos"], Vector2(120, 80), C_WOOD)
	_shopfront(PLACES["cafe"]["pos"], Vector2(110, 80), Color("a08a5a"))
	_shopfront(PLACES["library"]["pos"], Vector2(130, 80), Color("7a7468"))
	_church(PLACES["church"]["pos"])
	_house(PLACES["estelle"]["pos"], Vector2(96, 66), C_GRAY, C_GRAY.darkened(0.25), false)
	_house(PLACES["school"]["pos"], Vector2(130, 70), Color("9a4a3a"), C_ROOF, false)
	# dock: planks out into the bay
	var dp: Vector2 = PLACES["dock"]["pos"]
	draw_rect(Rect2(dp.x - 16, dp.y - 40, 32, 120), Color("a8a290"))
	for py in range(4):
		draw_rect(Rect2(dp.x - 20, dp.y - 30 + py * 28, 4, 20), C_INK)
		draw_rect(Rect2(dp.x + 16, dp.y - 30 + py * 28, 4, 20), C_INK)
	# cannery: long shed on pilings over the water
	var cp: Vector2 = PLACES["cannery"]["pos"]
	draw_rect(Rect2(cp.x - 110, cp.y - 40, 220, 54), C_RUST)
	draw_rect(Rect2(cp.x - 110, cp.y - 46, 220, 8), C_INK)
	for px in range(6):
		draw_rect(Rect2(cp.x - 96 + px * 38, cp.y + 14, 6, 26), C_INK)
	# beach path: sand wedge SW
	draw_rect(Rect2(60, 596, 190, 30), Color("b8a882"))

	# ── the walk-target glow + names when near ──
	var near := _place_near()
	for pid in PLACES.keys():
		var p: Vector2 = PLACES[pid]["pos"]
		if String(pid) == near:
			draw_arc(p, REACH * 0.55, 0.0, TAU, 24, Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.5 + 0.2 * sin(_t * 4.0)), 2.0)
			_label(p + Vector2(0, -52), String(PLACES[pid]["name"]), C_INK, 14)
			if not (_acts_by_loc.get(pid, []) as Array).is_empty():
				_label(p + Vector2(0, 44), "· E ·", C_GOLD, 13)
		# a small presence dot where a bonded person lives
		var who := String(PLACES[pid].get("who", ""))
		if who != "":
			var key := who.to_lower()
			var lvl: int = int(_bonds.get("gran" if key == "vovo" else key, 0))
			if lvl > 0:
				draw_circle(p + Vector2(26, -26), 3.0 + minf(float(lvl), 6.0) * 0.5, C_GOLD)

	# ── the kid ──
	var tex := _walker.texture()
	if tex != null:
		var scl := 3.0
		var sz := Vector2(tex.get_width() * scl, tex.get_height() * scl)
		draw_texture_rect(tex, Rect2(_pos - sz * 0.5 + Vector2(0, sin(_t * 6.0) * (1.5 if _dir != Vector2.ZERO else 0.0)), sz), false)
	else:
		draw_circle(_pos, 8.0, C_RUST)


func _spruce(base: Vector2, h: float, col: Color) -> void:
	var w := h * 0.42
	draw_colored_polygon(PackedVector2Array([
		base + Vector2(0, -h), base + Vector2(w * 0.5, 0), base + Vector2(-w * 0.5, 0)]), col)


func _house(p: Vector2, sz: Vector2, body: Color, roof: Color, lit: bool) -> void:
	draw_rect(Rect2(p.x - sz.x * 0.5, p.y - sz.y * 0.5, sz.x, sz.y), body)
	draw_colored_polygon(PackedVector2Array([
		Vector2(p.x - sz.x * 0.5 - 6, p.y - sz.y * 0.5),
		Vector2(p.x, p.y - sz.y * 0.5 - 26),
		Vector2(p.x + sz.x * 0.5 + 6, p.y - sz.y * 0.5)]), roof)
	if lit:
		draw_rect(Rect2(p.x - 10, p.y - 6, 20, 16), Color("e8c060"))
	else:
		draw_rect(Rect2(p.x - 10, p.y - 6, 20, 16), C_INK.lightened(0.15))


func _shopfront(p: Vector2, sz: Vector2, body: Color) -> void:
	draw_rect(Rect2(p.x - sz.x * 0.5, p.y - sz.y * 0.5, sz.x, sz.y), body)
	draw_rect(Rect2(p.x - sz.x * 0.5, p.y - sz.y * 0.5 - 12, sz.x, 12), C_INK)
	draw_rect(Rect2(p.x - sz.x * 0.35, p.y - 4, sz.x * 0.7, 26), C_INK.lightened(0.2))


func _church(p: Vector2) -> void:
	draw_rect(Rect2(p.x - 44, p.y - 34, 88, 70), Color("d8d4c8"))
	draw_colored_polygon(PackedVector2Array([
		Vector2(p.x - 50, p.y - 34), Vector2(p.x, p.y - 66), Vector2(p.x + 50, p.y - 34)]), C_ROOF)
	draw_rect(Rect2(p.x - 4, p.y - 96, 8, 32), Color("d8d4c8"))
	draw_rect(Rect2(p.x - 1, p.y - 106, 2, 12), C_INK)
	draw_rect(Rect2(p.x - 8, p.y - 102, 16, 2), C_INK)


func _label(p: Vector2, text: String, col: Color, size: int) -> void:
	var f := ThemeDB.fallback_font
	var w := f.get_string_size(text, HORIZONTAL_ALIGNMENT_CENTER, -1, size).x
	draw_string(f, p + Vector2(-w * 0.5, 0), text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, col)


func _sfx(preset: String, vol: float = 1.0) -> void:
	var sb := get_node_or_null("/root/SFXBank")
	if sb != null and sb.has_method("play"):
		sb.play(preset, vol)
