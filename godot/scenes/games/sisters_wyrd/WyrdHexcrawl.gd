extends Control
## THE SISTERS WYRD · the crawl · v2 · a RIDE, not a diagram.
##
## Rebuilt per playtest ("unplayable · needs an abundance of tiles
## and a text engine moving around and having an adventure"). The
## territory is now a dense field of terrain-inked hexes you ride
## across, one hex per step, with the adventure narrating itself in
## the message log on every move: travel prose in the paperback
## voice, sister-weather as you near a corner, encounters from the
## deck. The seven-scales weave survives as THEOLOGY — terrain is
## still hashed from the address (here: axial coords), identical
## every run, and the manual still calls it woven — but navigation
## is now plain riding.
##
## RIDE · click an adjacent hex, or arrows/WASD.
## The FOUR SISTERS keep the far corners: N · E · S · W.
## HOME is the dead center. Ride home with sisters dealt to end the
## ride; deal with all four by UNWEAVING to find the loom.
##
## GRIT at zero folds the territory back to your porch. SILVER is
## bullets and money, the same pouch. LORE is spent on nothing and
## REQUIRED for unweaving.

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

# The map · axial hex coords (q, r) · pointy-top.
const MAP_R := 15                       # rideable radius from home
const WITCH_SEATS := {"north": [0, -13], "east": [13, 0],
	"south": [0, 13], "west": [-13, 0]}
const HOME := [0, 0]

# Tile geometry · native WyrdHexArt tiles (40×46) laid as a field.
const TILE_W := 40.0
const TILE_H := 46.0
const COL_X := 40.0                     # x per q
const ROW_X := 20.0                     # x per r (axial shear)
const ROW_Y := 34.0                     # y per r
const VIEW_CENTER := Vector2(640, 330)

# axial neighbors · E, W, NE, NW, SE, SW
const DIRS := [[1, 0], [-1, 0], [1, -1], [0, -1], [0, 1], [-1, 1]]

# The text engine · travel lines per terrain, hash-picked per hex.
const TRAVEL_LINES: Dictionary = {
	"dust": [
		"dust, and more of it. the horse doesn't comment.",
		"the trail is a rumor here. you follow it anyway.",
		"wind out of the west, carrying somebody's topsoil."],
	"bone": [
		"bone flats. whatever died here did it thoroughly.",
		"the ground crunches, polite, underfoot.",
		"ribs to the left, ribs to the right. you don't count them."],
	"scrub": [
		"sage and scrub, arguing with the wind.",
		"green, in the stubborn sense of the word.",
		"quail somewhere close. the horse's ears say so."],
	"mesa": [
		"the mesa keeps its own counsel, and its own shadow.",
		"red rock overhead. cool, for one hex.",
		"you ride the butte's long shade a while."],
	"salt": [
		"salt pan. your shadow is the only honest thing on it.",
		"white to every horizon that matters.",
		"the crust takes hoofprints and keeps them."],
	"gallows": [
		"gallows wood. the trees grew wrong on purpose.",
		"a rope's worth of shade in every tree.",
		"you don't whistle here. nobody taught you that. you just know."],
	"township": [
		"a township. lamps lit, nobody about.",
		"the boards of the walk remember boots.",
		"somewhere a door closes, courteous about it."],
}
const WEATHER_CUES: Dictionary = {
	"north": "snow on the wind, faint. she is close, to the north.",
	"east": "the light has gone red at the edges. east.",
	"south": "the air has gone dry as a sermon. south.",
	"west": "sunset is coming early on that side. west.",
}

var _state: Dictionary = {}
var _enc: Dictionary = {}
var _pos: Vector2i = Vector2i.ZERO      # axial q, r
var _encounter: Dictionary = {}
var _choice_btns: Array = []
var _hud: Label = null
var _log_lbl: RichTextLabel = null
var _log_lines: Array = []
var _last_cue: String = ""


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
	var saved_v: Variant = _state.get("addr", HOME.duplicate())
	var saved: Array = saved_v if saved_v is Array else HOME.duplicate()
	# v1 saves carried a 6-digit weave address — fold those riders
	# gently back to the porch.
	if saved.size() == 2:
		_pos = Vector2i(int(saved[0]), int(saved[1]))
	else:
		_pos = Vector2i.ZERO
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("request_scene_bgm"):
		am.request_scene_bgm("res://assets/audio/bgm/sw/territory.wav")
	_say("the porch. the territory runs %d hexes to every horizon that matters." % MAP_R)
	_say("the sisters keep the four corners · N · E · S · W · ride out, deal with them, ride home. click a touching hex, or use the arrows.")
	queue_redraw()


# ─── The address is still the world ──────────────────────────────

func _hash_qr(q: int, r: int, salt: int = 0) -> int:
	var h := 5381 + salt
	h = ((h << 5) + h + q + 907) & 0x7FFFFFFF
	h = ((h << 5) + h + r + 2029) & 0x7FFFFFFF
	h = ((h << 5) + h + q * 31 + r * 7) & 0x7FFFFFFF
	return h


func _terrain_at(q: int, r: int) -> String:
	if q == 0 and r == 0:
		return "township"   # home is a porch with a town's manners
	for w in WITCH_SEATS.keys():
		var s: Array = WITCH_SEATS[w]
		if q == int(s[0]) and r == int(s[1]):
			return "gallows" if w == "west" else ("salt" if w == "north" else ("mesa" if w == "east" else "dust"))
	return TERRAINS[_hash_qr(q, r) % TERRAINS.size()]


func _seat_at(q: int, r: int) -> String:
	for w in WITCH_SEATS.keys():
		var s: Array = WITCH_SEATS[w]
		if q == int(s[0]) and r == int(s[1]):
			return String(w)
	return ""


func _hex_dist(a: Vector2i, b: Vector2i) -> int:
	var dq: int = a.x - b.x
	var dr: int = a.y - b.y
	@warning_ignore("integer_division")
	return (absi(dq) + absi(dr) + absi(dq + dr)) / 2


# ─── UI ──────────────────────────────────────────────────────────

func _build_ui() -> void:
	_hud = Label.new()
	_hud.position = Vector2(40, 16)
	_hud.add_theme_font_size_override("font_size", 15)
	_hud.add_theme_color_override("font_color", C_BONE)
	_hud.add_theme_color_override("font_outline_color", C_INK)
	_hud.add_theme_constant_override("outline_size", 6)
	add_child(_hud)

	# The text engine — the ride narrating itself.
	var log_bg := ColorRect.new()
	log_bg.color = Color(C_INK.r, C_INK.g, C_INK.b, 0.82)
	log_bg.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	log_bg.offset_left = 24
	log_bg.offset_right = -24
	log_bg.offset_top = -132
	log_bg.offset_bottom = -12
	add_child(log_bg)

	_log_lbl = RichTextLabel.new()
	_log_lbl.bbcode_enabled = false
	_log_lbl.scroll_active = false
	_log_lbl.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_log_lbl.offset_left = 40
	_log_lbl.offset_right = -40
	_log_lbl.offset_top = -124
	_log_lbl.offset_bottom = -18
	_log_lbl.add_theme_font_size_override("normal_font_size", 15)
	_log_lbl.add_theme_color_override("default_color", C_BONE)
	_log_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_log_lbl)


func _say(line: String) -> void:
	_log_lines.append(line)
	while _log_lines.size() > 5:
		_log_lines.pop_front()
	if _log_lbl != null:
		_log_lbl.text = "\n".join(PackedStringArray(_log_lines))


func _refresh_hud() -> void:
	var dealt: Dictionary = _state.get("witches_dealt", {})
	_hud.text = "GRIT %d · SILVER %d · LORE %d      sisters dealt · %d of 4      home · %d hexes" % [
		int(_state.get("grit", 6)), int(_state.get("silver", 3)),
		int(_state.get("lore", 0)), dealt.size(),
		_hex_dist(_pos, Vector2i.ZERO)]


# ─── Movement · the ride ─────────────────────────────────────────

func _axial_to_px(q: int, r: int) -> Vector2:
	var rel_q: float = float(q - _pos.x)
	var rel_r: float = float(r - _pos.y)
	return VIEW_CENTER + Vector2(rel_q * COL_X + rel_r * ROW_X, rel_r * ROW_Y)


func _try_step(dq: int, dr: int) -> void:
	if not _encounter.is_empty():
		return
	var nq: int = _pos.x + dq
	var nr: int = _pos.y + dr
	if _hex_dist(Vector2i(nq, nr), Vector2i.ZERO) > MAP_R:
		# The hidden hex · push into the shimmer three times from the
		# same edge hex, once ever, and the repeat shows itself.
		if not bool(_state.get("shimmer_crossed", false)):
			var pos_key := "%d,%d" % [_pos.x, _pos.y]
			var pushes: int = int(_state.get("shimmer_pushes", 0))
			if String(_state.get("shimmer_push_pos", "")) == pos_key:
				pushes += 1
			else:
				pushes = 1
			_state["shimmer_pushes"] = pushes
			_state["shimmer_push_pos"] = pos_key
			if pushes >= 3:
				_state["shimmer_crossed"] = true
				_say("you push a third time and the shimmer stops pretending. one hex past the edge: this hex, again, exactly · your own hoofprints already in it, a version of your campfire, cold. the territory repeats. it is not a figure of speech. you turn the horse, and the horse was already turning.")
				_sfx("radio_static", 0.25)
				OneironauticsTokens.add("wyrd_shimmer_crossed")
				return
		_say("the shimmer. the territory repeats past here, and the manual says not to look at that too long. you turn the horse.")
		return
	# The south sister's parley price · you gave the southwest away.
	if dq == -1 and dr == 1 and bool(_state.get("no_southwest", false)):
		_say("you turn the horse southwest and the horse declines, courteous about it. you traded that direction. the territory keeps receipts.")
		return
	_pos = Vector2i(nq, nr)
	_sfx("boot_plank", 0.2)
	_on_arrive()
	queue_redraw()


func _on_arrive() -> void:
	var seat := _seat_at(_pos.x, _pos.y)
	if seat != "":
		crawl_event.emit("witch", _pack(seat))
		return
	if _pos == Vector2i.ZERO:
		var dealt: Dictionary = _state.get("witches_dealt", {})
		if dealt.size() > 0:
			crawl_event.emit("home", _pack(""))
			return
		_say("the porch. it holds your shape. the territory is out there being itself in six directions.")
		return
	# The text engine · every hex says something.
	var terrain := _terrain_at(_pos.x, _pos.y)
	var lines: Array = TRAVEL_LINES.get(terrain, [])
	if not lines.is_empty():
		_say(String(lines[_hash_qr(_pos.x, _pos.y, 3) % lines.size()]))
	# Sister weather when her corner is near.
	var dealt2: Dictionary = _state.get("witches_dealt", {})
	var cue := ""
	for w in WITCH_SEATS.keys():
		if dealt2.has(w):
			continue
		var s: Array = WITCH_SEATS[w]
		if _hex_dist(_pos, Vector2i(int(s[0]), int(s[1]))) <= 4:
			cue = String(w)
			break
	if cue != "" and cue != _last_cue:
		_say(String(WEATHER_CUES[cue]))
	_last_cue = cue
	_maybe_encounter(terrain)


func _gui_input(event: InputEvent) -> void:
	if not _encounter.is_empty():
		return
	if event is InputEventMouseButton and event.pressed \
			and event.button_index == MOUSE_BUTTON_LEFT:
		var pos: Vector2 = (event as InputEventMouseButton).position
		for d in DIRS:
			var c := _axial_to_px(_pos.x + int(d[0]), _pos.y + int(d[1]))
			if pos.distance_to(c) < TILE_W * 0.62:
				_try_step(int(d[0]), int(d[1]))
				accept_event()
				return


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
			KEY_RIGHT, KEY_D: _try_step(1, 0)
			KEY_LEFT, KEY_A: _try_step(-1, 0)
			KEY_UP, KEY_W: _try_step(1, -1) if Input.is_key_pressed(KEY_SHIFT) else _try_step(0, -1)
			KEY_DOWN, KEY_S: _try_step(-1, 1) if Input.is_key_pressed(KEY_SHIFT) else _try_step(0, 1)
			KEY_Q: _try_step(0, -1)
			KEY_E: _try_step(1, -1)
			KEY_Z: _try_step(-1, 1)
			KEY_C: _try_step(0, 1)


# ─── Encounters · the deck is the address ────────────────────────

func _maybe_encounter(terrain: String) -> void:
	var h := _hash_qr(_pos.x, _pos.y, 7)
	if h % 100 >= 18:   # ~18% of hexes carry a beat
		return
	var seen: Array = _state.get("encounters_seen", [])
	var pool: Array = (_enc.get("by_terrain", {}) as Dictionary).get(terrain, [])
	if pool.is_empty():
		return
	var e: Dictionary = pool[h % pool.size()]
	var key := "%s@%d,%d" % [String(e["id"]), _pos.x, _pos.y]
	if seen.has(key):
		return
	seen.append(key)
	_state["encounters_seen"] = seen
	_show_encounter(e)


func _show_encounter(e: Dictionary) -> void:
	_encounter = e
	_say("— " + String(e.get("text", "")))
	var y := 560.0
	var idx := 0
	for ch_v in e.get("choices", []):
		var ch: Dictionary = ch_v
		var b := Button.new()
		b.text = "  · %s ·  " % String(ch.get("label", ""))
		b.position = Vector2(60.0 + float(idx) * 320.0, y)
		b.add_theme_font_size_override("font_size", 14)
		b.pressed.connect(_resolve_encounter.bind(ch))
		add_child(b)
		_choice_btns.append(b)
		idx += 1
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
	_say(String(ch.get("text", "")))
	if int(ch.get("lore", 0)) > 0:
		_sfx("page_turn", 0.5)
		_say("· that is LORE, and you can hold it · LORE %d ·" % int(_state.get("lore", 0)))
	if int(_state.get("grit", 6)) <= 0:
		_fold_home()
	queue_redraw()


func _fold_home() -> void:
	_pos = Vector2i.ZERO
	_state["grit"] = 3
	_state["silver"] = maxi(0, int(_state.get("silver", 0)) - 1)
	_say("— the territory folds. no distance happens, and yet: the porch. your boots are dusty from hexes you don't remember. this is worse than dying, and it knows it.")
	_sfx("loss_thud", 0.6)


func _pack(extra: String) -> Dictionary:
	_state["addr"] = [_pos.x, _pos.y]
	if extra != "":
		_state["_witch"] = extra
	return _state


# ─── The field · an abundance of tiles ───────────────────────────

func _draw() -> void:
	draw_rect(Rect2(0, 0, 1280, 720), C_INK)
	if _hud != null:
		_refresh_hud()
	var font := get_theme_default_font()

	# visible window of the field, centered on the drifter
	var r0: int = _pos.y - 11
	var r1: int = _pos.y + 11
	for r in range(r0, r1 + 1):
		var q_mid: int = _pos.x - int(round(float(r - _pos.y) * 0.5))
		for q in range(q_mid - 18, q_mid + 19):
			var c := _axial_to_px(q, r)
			if c.x < -TILE_W or c.x > 1280.0 + TILE_W or c.y < -TILE_H or c.y > 720.0 + TILE_H:
				continue
			var inside: bool = _hex_dist(Vector2i(q, r), Vector2i.ZERO) <= MAP_R
			var tex: ImageTexture = HEX_ART.tile(_terrain_at(q, r), _hash_qr(q, r),
					Vector2i(int(TILE_W), int(TILE_H)))
			if inside:
				draw_texture(tex, c - Vector2(TILE_W / 2.0, TILE_H / 2.0))
			else:
				# past the rim, the weave shows — dimmed, violet-shot
				draw_texture(tex, c - Vector2(TILE_W / 2.0, TILE_H / 2.0),
						Color(0.5, 0.42, 0.6, 0.55))

	# marks · home + seats
	var home_c := _axial_to_px(0, 0)
	draw_string(font, home_c + Vector2(-18, -26), "HOME",
			HORIZONTAL_ALIGNMENT_LEFT, -1, 13, C_BLOOD)
	var dealt: Dictionary = _state.get("witches_dealt", {})
	for w in WITCH_SEATS.keys():
		var s: Array = WITCH_SEATS[w]
		var sc := _axial_to_px(int(s[0]), int(s[1]))
		if sc.x > -60.0 and sc.x < 1340.0 and sc.y > -60.0 and sc.y < 780.0:
			draw_string(font, sc + Vector2(-30, -28), "HER SEAT",
					HORIZONTAL_ALIGNMENT_LEFT, -1, 13, C_WYRD)
			if dealt.has(w):
				draw_line(sc + Vector2(-10, -6), sc + Vector2(10, 6), C_WYRD, 2.0)
	# seat direction arrows at the screen edge for undealt sisters
	for w2 in WITCH_SEATS.keys():
		if dealt.has(w2):
			continue
		var s2: Array = WITCH_SEATS[w2]
		var sc2 := _axial_to_px(int(s2[0]), int(s2[1]))
		if sc2.x < 0.0 or sc2.x > 1280.0 or sc2.y < 0.0 or sc2.y > 720.0:
			var dir := (sc2 - VIEW_CENTER).normalized()
			var edge := VIEW_CENTER + dir * 300.0
			draw_line(edge, edge + dir * 16.0, C_WYRD, 2.0)
			draw_string(font, edge + dir * 24.0 + Vector2(-8, 4), String(w2[0]).to_upper(),
					HORIZONTAL_ALIGNMENT_LEFT, -1, 14, C_WYRD)

	# the drifter, on the hex
	draw_texture(FIGURE_ART.drifter(), VIEW_CENTER - Vector2(9.0, 26.0))

	# the eight-pointed compass card corner · always · uncommented
	var cc := Vector2(1200, 70)
	for i in range(8):
		var a := float(i) * PI / 4.0
		draw_line(cc, cc + Vector2(cos(a), sin(a)) * 24.0, C_BONE if i % 2 == 0 else C_WYRD, 1.5)
	draw_circle(cc, 3.0, C_BLOOD)


func _sfx(preset: String, vol: float = 1.0) -> void:
	var sb := get_node_or_null("/root/SFXBank")
	if sb != null and sb.has_method("play"):
		sb.play(preset, vol)
