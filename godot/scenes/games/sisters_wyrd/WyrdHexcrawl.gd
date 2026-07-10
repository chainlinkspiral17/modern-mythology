extends Control
## THE SISTERS WYRD · the crawl · seven nested scales of one territory.
##
## The world is one hex at scale 7.  Every hex contains seven —
## a center and a ring — down to scale 1, the ground.  Your
## ADDRESS is a path of ring digits (0 center · 1–6 ring); the
## address IS the world: terrain, encounters, everything derives
## from it, identically every run.  The territory is not
## generated.  It is WOVEN, and the loom does not change its mind.
##
## RIDE · click a hex (center touches all six; ring hexes touch
## their ring neighbors and the center).  ZOOM IN (X or button) ·
## drop into the hex under you.  ZOOM OUT (Z) · lift to the hex
## that contains you.  Distance is vertical.
##
## GRIT at zero folds the territory back to your porch, which is
## worse than dying.  SILVER is bullets and money, the same
## pouch, on purpose.  LORE is spent on nothing and REQUIRED for
## unweaving.

signal quit
signal crawl_event(kind: String, state: Dictionary)

const ENC_PATH := "res://resources/games/vol7/sisters_wyrd/encounters.json"
# Preload by path — new class_names miss the first editor scan
# after a pull (sprite playbook rule).
const HEX_ART := preload("res://scenes/games/sisters_wyrd/WyrdHexArt.gd")
const FIGURE_ART := preload("res://scenes/games/sisters_wyrd/WyrdFigureArt.gd")

# Paperback inks
const C_DUST   := Color("c8a878")
const C_INK    := Color("201410")
const C_BONE   := Color("e8dcc0")
const C_BLOOD  := Color("7a3020")
const C_SILVER := Color("b8bcc8")
const C_WYRD   := Color("8a58a8")
const C_SCRUB  := Color("4a5a3a")

const TERRAINS := ["dust", "bone", "scrub", "mesa", "salt", "gallows", "township"]
const TERRAIN_COLORS := {
	"dust": Color("c8a878"), "bone": Color("e8dcc0"), "scrub": Color("4a5a3a"),
	"mesa": Color("3a3028"), "salt": Color("d8d8d0"), "gallows": Color("5a4838"),
	"township": Color("a08858")
}
const WITCH_SEATS := {"north": [1,1,1,1,1,1], "east": [2,2,2,2,2,2],
	"south": [4,4,4,4,4,4], "west": [5,5,5,5,5,5]}
const HOME := [0, 0, 0, 0, 0, 0]

const HEX_R := 92.0
const RING_D := 168.0
const CENTER := Vector2(560, 350)

var _state: Dictionary = {}
var _enc: Dictionary = {}
var _addr: Array = []            # ring digits · length = 7 - scale
var _msg: String = ""
var _encounter: Dictionary = {}  # active encounter, if any
var _choice_btns: Array = []
var _hud: Label = null
var _msg_lbl: Label = null
var _zoom_in_btn: Button = null
var _zoom_out_btn: Button = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	var f := FileAccess.open(ENC_PATH, FileAccess.READ)
	if f != null:
		var parsed: Variant = JSON.parse_string(f.get_as_text())
		f.close()
		if parsed is Dictionary:
			_enc = parsed
	_build_ui()


func boot(state: Dictionary) -> void:
	_state = state
	_addr = (_state.get("addr", HOME.duplicate()) as Array).duplicate()
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("play_bgm"):
		am.play_bgm("res://assets/audio/bgm/sw/territory.wav")
	_set_msg("the territory. scale %d. the porch is behind you, six digits deep." % _scale())
	queue_redraw()


func _scale() -> int:
	return 7 - _addr.size()


# ─── The address is the world ────────────────────────────────────

func _hash_addr(addr: Array, salt: int = 0) -> int:
	var h := 5381 + salt
	for d in addr:
		h = ((h << 5) + h + int(d)) & 0x7FFFFFFF
	return h


func _terrain(addr: Array) -> String:
	if addr == HOME.slice(0, addr.size()) and addr.size() == 6:
		return "township"   # home is a porch with a town's manners
	return TERRAINS[_hash_addr(addr) % TERRAINS.size()]


func _seat_here(addr: Array) -> String:
	for w in WITCH_SEATS.keys():
		if addr == WITCH_SEATS[w]:
			return String(w)
	return ""


func _seat_direction_hint() -> String:
	# at high scales, the corners announce themselves
	if _addr.is_empty():
		return "four corners hum · N · E · S · W · and the compass card in your pocket has eight points."
	return ""


# ─── UI ──────────────────────────────────────────────────────────

func _build_ui() -> void:
	_hud = Label.new()
	_hud.position = Vector2(40, 20)
	_hud.add_theme_font_size_override("font_size", 15)
	_hud.add_theme_color_override("font_color", C_INK)
	add_child(_hud)

	_msg_lbl = Label.new()
	_msg_lbl.position = Vector2(40, 620)
	_msg_lbl.size = Vector2(1200, 90)
	_msg_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_msg_lbl.add_theme_font_size_override("font_size", 15)
	_msg_lbl.add_theme_color_override("font_color", C_INK)
	add_child(_msg_lbl)

	_zoom_in_btn = Button.new()
	_zoom_in_btn.text = "  ZOOM IN (X)  "
	_zoom_in_btn.position = Vector2(1060, 300)
	_zoom_in_btn.add_theme_font_size_override("font_size", 14)
	_zoom_in_btn.pressed.connect(_zoom_in)
	add_child(_zoom_in_btn)

	_zoom_out_btn = Button.new()
	_zoom_out_btn.text = "  ZOOM OUT (Z)  "
	_zoom_out_btn.position = Vector2(1060, 344)
	_zoom_out_btn.add_theme_font_size_override("font_size", 14)
	_zoom_out_btn.pressed.connect(_zoom_out)
	add_child(_zoom_out_btn)


func _refresh_hud() -> void:
	var addr_s := ""
	for d in _addr:
		addr_s += str(int(d)) + "·"
	if addr_s == "":
		addr_s = "the world"
	else:
		addr_s = addr_s.trim_suffix("·")
	_hud.text = "SCALE %d · [%s] · %s      GRIT %d · SILVER %d · LORE %d      sisters dealt · %d of 4" % [
		_scale(), addr_s, _terrain(_addr).to_upper(),
		int(_state.get("grit", 6)), int(_state.get("silver", 3)), int(_state.get("lore", 0)),
		(_state.get("witches_dealt", {}) as Dictionary).size()]


# ─── Movement ────────────────────────────────────────────────────

func _ring_center(i: int) -> Vector2:
	# i = 1..6 · pointy compass-ish: 1 N · 2 NE · 3 SE · 4 S · 5 SW · 6 NW
	var ang := deg_to_rad(-90.0 + (i - 1) * 60.0)
	return CENTER + Vector2(cos(ang), sin(ang)) * RING_D


func _gui_input(event: InputEvent) -> void:
	if not _encounter.is_empty():
		return
	if event is InputEventMouseButton and event.pressed \
			and event.button_index == MOUSE_BUTTON_LEFT:
		var pos: Vector2 = (event as InputEventMouseButton).position
		var cur: int = int(_addr[-1]) if _addr.size() > 0 else -1
		for i in range(7):
			var c := CENTER if i == 0 else _ring_center(i)
			if pos.distance_to(c) < HEX_R * 0.9:
				if _addr.is_empty():
					return   # the world hex has no siblings
				if i == cur:
					return
				if _adjacent(cur, i):
					_ride(i)
				else:
					_set_msg("no trail between those hexes at this scale. the center touches all six; the ring touches its neighbors.")
				accept_event()
				return


func _adjacent(a: int, b: int) -> bool:
	if a == 0 or b == 0:
		return true
	var diff: int = absi(a - b)
	return diff == 1 or diff == 5


func _ride(i: int) -> void:
	# The south sister's parley price · you gave the southwest away.
	if i == 5 and bool(_state.get("no_southwest", false)):
		_set_msg("you turn the horse southwest and the horse declines, courteous about it. you traded that direction. the territory keeps receipts.")
		return
	_addr[-1] = i
	var seat := _seat_here(_addr)
	if seat != "":
		crawl_event.emit("witch", _pack(seat))
		return
	if _addr == HOME:
		var dealt: int = (_state.get("witches_dealt", {}) as Dictionary).size()
		if dealt > 0:
			crawl_event.emit("home", _pack(""))
			return
		_set_msg("the porch. it holds your shape. the territory is out there being itself in six directions.")
		queue_redraw()
		return
	_maybe_encounter()
	queue_redraw()


func _zoom_in() -> void:
	if not _encounter.is_empty() or _addr.size() >= 6:
		if _addr.size() >= 6:
			_set_msg("scale 1. the ground. boots and dust. there is no deeper, except the way the shimmer implies.")
		return
	_addr.append(0)
	_sfx("boot_plank", 0.3)
	_set_msg("down a scale. the hex opens into seven. the weave holds.")
	queue_redraw()


func _zoom_out() -> void:
	if not _encounter.is_empty() or _addr.is_empty():
		if _addr.is_empty():
			_set_msg("the world hex. there is no farther out. the shimmer suggests otherwise and the manual says to ignore that.")
		return
	_addr.pop_back()
	_sfx("boot_plank", 0.3)
	_set_msg("up a scale. seven hexes fold into one under you.")
	queue_redraw()


func _input(event: InputEvent) -> void:
	if not is_visible_in_tree():
		return
	if event is InputEventKey and event.pressed and not event.echo:
		var kev: InputEventKey = event
		match kev.keycode:
			KEY_ESCAPE:
				if _encounter.is_empty():
					quit.emit()
					get_viewport().set_input_as_handled()
			KEY_X: _zoom_in()
			KEY_Z: _zoom_out()


# ─── Encounters · the deck is the address ────────────────────────

func _maybe_encounter() -> void:
	if _scale() > 3:
		return
	var h := _hash_addr(_addr, 7)
	if h % 10 >= 4:   # ~40% of low-scale hexes carry a beat
		return
	var seen: Array = _state.get("encounters_seen", [])
	var terrain := _terrain(_addr)
	var pool: Array = (_enc.get("by_terrain", {}) as Dictionary).get(terrain, [])
	if pool.is_empty():
		return
	var e: Dictionary = pool[h % pool.size()]
	var key := "%s@%s" % [String(e["id"]), str(_addr)]
	if seen.has(key):
		return
	seen.append(key)
	_state["encounters_seen"] = seen
	_show_encounter(e)


func _show_encounter(e: Dictionary) -> void:
	_encounter = e
	_set_msg(String(e.get("text", "")))
	var y := 540.0
	for ch_v in e.get("choices", []):
		var ch: Dictionary = ch_v
		var b := Button.new()
		b.text = "  · %s ·  " % String(ch.get("label", ""))
		b.flat = true
		b.position = Vector2(60.0 + _choice_btns.size() * 300.0, y)
		b.add_theme_font_size_override("font_size", 14)
		b.add_theme_color_override("font_color", C_BLOOD)
		b.pressed.connect(_resolve_encounter.bind(ch))
		add_child(b)
		_choice_btns.append(b)
	queue_redraw()


func _resolve_encounter(ch: Dictionary) -> void:
	for b in _choice_btns:
		if is_instance_valid(b):
			b.queue_free()
	_choice_btns.clear()
	_encounter = {}
	_state["grit"] = clampi(int(_state.get("grit", 6)) + int(ch.get("grit", 0)), 0, 9)
	_state["silver"] = maxi(0, int(_state.get("silver", 3)) + int(ch.get("silver", 0)))
	_state["lore"] = maxi(0, int(_state.get("lore", 0)) + int(ch.get("lore", 0)))
	_set_msg(String(ch.get("text", "")))
	if int(ch.get("lore", 0)) > 0:
		_sfx("page_turn", 0.5)
	if int(_state.get("grit", 6)) <= 0:
		_fold_home()
	queue_redraw()


func _fold_home() -> void:
	# GRIT at zero · the territory folds you back to your porch.
	_addr = HOME.duplicate()
	_state["grit"] = 3
	_state["silver"] = maxi(0, int(_state.get("silver", 0)) - 1)
	_set_msg("— the territory folds. no distance happens, and yet: the porch. your boots are dusty from hexes you don't remember. this is worse than dying, and it knows it.")
	_sfx("loss_thud", 0.6)


func _pack(extra: String) -> Dictionary:
	_state["addr"] = _addr.duplicate()
	if extra != "":
		_state["_witch"] = extra
	return _state


func _set_msg(t: String) -> void:
	_msg = t
	_msg_lbl.text = t


# ─── The seven hexes · paperback inks ────────────────────────────

func _hex_points(c: Vector2, r: float) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for i in range(6):
		var a := deg_to_rad(30.0 + i * 60.0)
		pts.append(c + Vector2(cos(a), sin(a)) * r)
	return pts


func _draw_hex(c: Vector2, r: float, fill: Color, line: Color, width: float) -> void:
	var pts := _hex_points(c, r)
	draw_colored_polygon(pts, fill)
	var closed := pts.duplicate()
	closed.append(pts[0])
	draw_polyline(closed, line, width)


func _draw() -> void:
	draw_rect(Rect2(0, 0, 1280, 720), C_DUST)
	if _hud != null:
		_refresh_hud()
	var font := get_theme_default_font()

	for i in range(7):
		var c := CENTER if i == 0 else _ring_center(i)
		var child_addr: Array = _addr.duplicate()
		if child_addr.is_empty():
			# the world hex cluster · show its seven children
			child_addr = [i]
		else:
			child_addr[-1] = i
		var terrain := _terrain(child_addr)
		var here: bool = (not _addr.is_empty() and i == int(_addr[-1]))
		# Terrain-inked tile — "like cover art, not like a wargame".
		var tile_tex: ImageTexture = HEX_ART.tile(terrain, _hash_addr(child_addr))
		draw_texture(tile_tex, c - Vector2(80.0, 92.0))
		var border_pts := _hex_points(c, HEX_R)
		var border := border_pts.duplicate()
		border.append(border_pts[0])
		draw_polyline(border, C_INK, 3.0 if here else 1.5)
		# the shimmer · at scales 5-7, hexes show their children
		if _scale() >= 5:
			for j in range(7):
				var sc := c if j == 0 else c + Vector2(cos(deg_to_rad(-90.0 + (j - 1) * 60.0)), sin(deg_to_rad(-90.0 + (j - 1) * 60.0))) * (HEX_R * 0.52)
				var sub := child_addr.duplicate()
				sub.append(j)
				_draw_hex(sc, HEX_R * 0.24, Color(TERRAIN_COLORS.get(_terrain(sub), C_DUST), 0.5), Color(C_WYRD, 0.35), 1.0)
		# labels · terrain + marks (bone ink on the dark terrains)
		var label_col: Color = C_BONE if (terrain == "mesa" or terrain == "gallows") else C_INK
		draw_string(font, c + Vector2(-34, HEX_R * 0.75), terrain.to_upper(),
				HORIZONTAL_ALIGNMENT_LEFT, -1, 12, label_col)
		var seat := _seat_here(child_addr)
		if seat != "":
			draw_string(font, c + Vector2(-30, -HEX_R * 0.55), "HER SEAT",
					HORIZONTAL_ALIGNMENT_LEFT, -1, 13, C_WYRD)
			var dealt: Dictionary = _state.get("witches_dealt", {})
			if dealt.has(seat):
				draw_line(c + Vector2(-20, -8), c + Vector2(20, 8), C_WYRD, 2.0)
		if child_addr == HOME:
			draw_string(font, c + Vector2(-20, -HEX_R * 0.55), "HOME",
					HORIZONTAL_ALIGNMENT_LEFT, -1, 13, C_BLOOD)
		# the drifter — the marker IS the figure now
		if here or (_addr.is_empty() and i == 0):
			draw_texture(FIGURE_ART.drifter(), c - Vector2(9.0, 26.0))

	# corner hums at the world scale
	if _addr.size() <= 1:
		var hints := {"N": Vector2(560, 60), "E": Vector2(1000, 350), "S": Vector2(560, 648), "W": Vector2(120, 350)}
		for k in hints.keys():
			draw_string(font, hints[k], String(k), HORIZONTAL_ALIGNMENT_LEFT, -1, 18, C_WYRD)

	# the eight-pointed compass card corner · always · uncommented
	var cc := Vector2(1180, 80)
	for i in range(8):
		var a := i * PI / 4.0
		draw_line(cc, cc + Vector2(cos(a), sin(a)) * 26.0, C_INK if i % 2 == 0 else C_WYRD, 1.5)
	draw_circle(cc, 3.0, C_BLOOD)


func _sfx(preset: String, vol: float = 1.0) -> void:
	var sb := get_node_or_null("/root/SFXBank")
	if sb != null and sb.has_method("play"):
		sb.play(preset, vol)
