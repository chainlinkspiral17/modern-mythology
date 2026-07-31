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
const TOWNS_PATH := "res://resources/games/vol7/sisters_wyrd/townships.json"
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
# THE SECOND DECK · the B-side · the same cart read the other way:
# the sisters swap corners (N<->S, E<->W) and the whole territory
# re-weaves under a different salt. Sagebrush shipped nothing
# else; this is not new product, it is the manual's last page
# read in a mirror.
const WITCH_SEATS_B := {"north": [0, 13], "east": [-13, 0],
	"south": [0, -13], "west": [13, 0]}


func _b_side() -> bool:
	return bool(_state.get("b_side", false))


func _seats() -> Dictionary:
	return WITCH_SEATS_B if _b_side() else WITCH_SEATS
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

# Wave 2 · the territory after a DRAW · her quadrant wears black.
const MOURNING_LINES: Dictionary = {
	"dust": "the dust here has settled flat, the way a room goes after news.",
	"bone": "the bone flats have stopped being ironic about it.",
	"scrub": "the scrub has let the wind through without argument. that's new.",
	"mesa": "the mesa's shadow doesn't move all the while you cross it.",
	"salt": "the salt has taken your hoofprints and grieved over every one.",
	"gallows": "the gallows wood is quieter than quiet. even the rope-shade mourns her.",
	"township": "black crepe on two doors. nobody says for whom. everybody knows for whom.",
}
# And after an UNWEAVE · her quadrant, truly calm.
const PEACE_LINES: Dictionary = {
	"dust": "dust, and the wind through it easy, like a held breath let go.",
	"bone": "the bone flats are just old now. old is allowed.",
	"scrub": "quail everywhere, loud, unbothered. the scrub has decided it's spring.",
	"mesa": "the mesa's shade is cool and means nothing by it.",
	"salt": "the salt pan is bright and flat and finally only a place.",
	"gallows": "the trees are growing straighter. give them forty years.",
	"township": "somebody's repainting a door. the town has plans again.",
}

var _state: Dictionary = {}
var _enc: Dictionary = {}
var _towns: Dictionary = {}             # "q,r" → township def
var _town_defs: Array = []
var _bounty_defs: Array = []
var _services: Dictionary = {}
var _pos: Vector2i = Vector2i.ZERO      # axial q, r
var _encounter: Dictionary = {}
var _choice_btns: Array = []
var _hud: Label = null
# Choice buttons live in an ANCHORED row above the log, never at
# hardcoded pixel coordinates. The old code placed them at literal
# y=540 / x=40..860, which collided with the prose panel on any
# viewport that wasn't exactly 1280×720 — the buttons landed on top
# of the text and, because a live encounter blocks _try_step, an
# unreachable button meant the ride simply stopped. (Reported
# 2026-07-30: "I move once, and the game stops?")
var _choice_row: HFlowContainer = null
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
	var tf := FileAccess.open(TOWNS_PATH, FileAccess.READ)
	if tf != null:
		var tparsed: Variant = JSON.parse_string(tf.get_as_text())
		tf.close()
		if tparsed is Dictionary:
			var tdoc: Dictionary = tparsed
			_town_defs = tdoc.get("townships", [])
			_bounty_defs = tdoc.get("bounties", [])
			_services = tdoc.get("services", {})
			for t_v in _town_defs:
				var t: Dictionary = t_v
				var hx: Array = t.get("hex", [0, 0])
				_towns["%d,%d" % [int(hx[0]), int(hx[1])]] = t
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
	# The B-side re-weaves the whole territory · same loom, other side.
	var h := 5381 + salt + (1009 if _b_side() else 0)
	h = ((h << 5) + h + q + 907) & 0x7FFFFFFF
	h = ((h << 5) + h + r + 2029) & 0x7FFFFFFF
	h = ((h << 5) + h + q * 31 + r * 7) & 0x7FFFFFFF
	return h


func _terrain_at(q: int, r: int) -> String:
	if q == 0 and r == 0:
		return "township"   # home is a porch with a town's manners
	if _towns.has("%d,%d" % [q, r]):
		return "township"   # the five authored towns keep hours
	for w in _seats().keys():
		var s: Array = _seats()[w]
		if q == int(s[0]) and r == int(s[1]):
			return "gallows" if w == "west" else ("salt" if w == "north" else ("mesa" if w == "east" else "dust"))
	return TERRAINS[_hash_qr(q, r) % TERRAINS.size()]


func _seat_at(q: int, r: int) -> String:
	for w in _seats().keys():
		var s: Array = _seats()[w]
		if q == int(s[0]) and r == int(s[1]):
			return String(w)
	return ""


func _hex_dist(a: Vector2i, b: Vector2i) -> int:
	var dq: int = a.x - b.x
	var dr: int = a.y - b.y
	@warning_ignore("integer_division")
	return (absi(dq) + absi(dr) + absi(dq + dr)) / 2


# ─── Wave 2 · sister weather with teeth ──────────────────────────

func _seat_vec(w: String) -> Vector2i:
	var s: Array = _seats().get(w, [0, 0])
	return Vector2i(int(s[0]), int(s[1]))


func _dealt_verb(w: String) -> String:
	var dealt: Dictionary = _state.get("witches_dealt", {})
	return String(dealt.get(w, ""))


func _in_aura(w: String, radius: int = 5) -> bool:
	# An UNDEALT sister projects weather around her seat.
	if _dealt_verb(w) != "":
		return false
	return _hex_dist(_pos, _seat_vec(w)) <= radius


func _quadrant_of(p: Vector2i) -> String:
	# A hex belongs to the sister whose seat sits nearest.
	var best := ""
	var best_d := 9999
	for w in _seats().keys():
		var d := _hex_dist(p, _seat_vec(String(w)))
		if d < best_d:
			best_d = d
			best = String(w)
	return best


func _apply_weather_bites() -> void:
	# North cold · her aura takes grit on woven-deterministic hexes.
	# THE OUTFIT · the long coat eats the ride's first cold bite, and
	# the second canteen widens the interval the north bites on.
	var north_mod: int = 3 + StickLoop.effect("sisters_wyrd", "bite_grace")
	if _in_aura("north", 4) and _hash_qr(_pos.x, _pos.y, 11) % north_mod == 0:
		if StickLoop.flag("sisters_wyrd", "warm_coat") \
				and not bool(_state.get("coat_ate_a_bite", false)):
			_state["coat_ate_a_bite"] = true
			_say("· the cold reaches for you and finds oilcloth · the coat earns itself ·")
		else:
			_state["grit"] = maxi(0, int(_state.get("grit", 6)) - 1)
			_say("· the cold takes a bite · GRIT %d ·" % int(_state.get("grit", 0)))
	# The hat you parleyed away · the sun collects on open ground.
	if _dealt_verb("north") == "parley":
		var terrain := _terrain_at(_pos.x, _pos.y)
		if (terrain == "dust" or terrain == "salt") and _hash_qr(_pos.x, _pos.y, 13) % 4 == 0:
			_state["grit"] = maxi(0, int(_state.get("grit", 6)) - 1)
			_say("· the sun finds your bare head, the way she said it would · GRIT %d ·" % int(_state.get("grit", 0)))


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
	log_bg.color = Color(C_INK.r, C_INK.g, C_INK.b, 0.94)
	log_bg.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	log_bg.offset_left = 24
	log_bg.offset_right = -24
	log_bg.offset_top = -132
	log_bg.offset_bottom = -12
	add_child(log_bg)
	var log_edge := ColorRect.new()
	log_edge.color = Color(C_BONE.r, C_BONE.g, C_BONE.b, 0.30)
	log_edge.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	log_edge.offset_left = 24
	log_edge.offset_right = -24
	log_edge.offset_top = -133
	log_edge.offset_bottom = -132
	add_child(log_edge)

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

	# The choice row · anchored to sit directly above the log panel,
	# wrapping when there are more choices than fit. Added last so it
	# draws over the map, never under the prose.
	_choice_row = HFlowContainer.new()
	_choice_row.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_choice_row.offset_left = 40
	_choice_row.offset_right = -40
	_choice_row.offset_top = -216       # room for two wrapped rows
	_choice_row.offset_bottom = -140    # 8px clear of the log edge
	_choice_row.alignment = FlowContainer.ALIGNMENT_CENTER
	_choice_row.add_theme_constant_override("h_separation", 10)
	_choice_row.add_theme_constant_override("v_separation", 6)
	add_child(_choice_row)


func _say(line: String) -> void:
	_log_lines.append(line)
	while _log_lines.size() > 4:
		_log_lines.pop_front()
	if _log_lbl != null:
		_log_lbl.text = "\n".join(PackedStringArray(_log_lines))


func _refresh_hud() -> void:
	var dealt: Dictionary = _state.get("witches_dealt", {})
	# The reckoning home · the east can take it from you two ways:
	# her parley price removes it, her red aura makes it lie.
	var home_txt := "%d hexes" % _hex_dist(_pos, Vector2i.ZERO)
	# THE OUTFIT · brass doesn't lie. The east sister can take the
	# memory of home or make the light misreport it; the compass
	# answers anyway.
	var brass := StickLoop.flag("sisters_wyrd", "dead_reckoning")
	if _dealt_verb("east") == "parley" and not brass:
		home_txt = "you'd have to ask"
	elif _in_aura("east") and not brass:
		var lie: int = maxi(0, _hex_dist(_pos, Vector2i.ZERO) + (_hash_qr(_pos.x, _pos.y, 19) % 7) - 3)
		home_txt = "%d hexes, says the light" % lie
	_hud.text = "GRIT %d · SILVER %d · LORE %d      sisters dealt · %d of 4      home · %s" % [
		int(_state.get("grit", 6)), int(_state.get("silver", 3)),
		int(_state.get("lore", 0)), dealt.size(), home_txt]


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
		# THE OUTFIT · THE EIGHTH POINT · you have crossed once and
		# kept the memory, so the edge stops making you ask three
		# times. Buying it turns a one-time ritual into a route.
		if StickLoop.flag("sisters_wyrd", "open_road") \
				and not bool(_state.get("shimmer_crossed", false)):
			_state["shimmer_crossed"] = true
			_say("you ride at the shimmer the way you would ride at a gate, and it opens, sullen about it. the eighth point knew the way.")
			_sfx("radio_static", 0.25)
			OneironauticsTokens.add("wyrd_shimmer_crossed")
			return
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
	# Authored townships · the trading post opens.
	var town_key := "%d,%d" % [_pos.x, _pos.y]
	if _towns.has(town_key):
		_arrive_township(_towns[town_key])
		return
	# An active notice, and this is the marked hex.
	var bounty: Dictionary = _state.get("bounty", {})
	if not bounty.is_empty() and String(bounty.get("stage", "")) == "posted":
		var bdef := _find_bounty(String(bounty.get("id", "")))
		if not bdef.is_empty():
			var tgt: Array = bdef.get("target", [99, 99])
			if _pos.x == int(tgt[0]) and _pos.y == int(tgt[1]):
				_show_encounter({"id": "bounty_%s" % String(bdef["id"]),
					"text": String(bdef.get("arrive", "")),
					"choices": bdef.get("choices", [])})
				return
	# The wrong hex · the previous owner's map is wrong in exactly
	# one hex. Olaf checked. The cart agrees.
	var wrong: Dictionary = (_enc.get("special", {}) as Dictionary).get("wrong_hex", {})
	if not wrong.is_empty():
		var wh: Array = wrong.get("hex", [99, 99])
		if _pos.x == int(wh[0]) and _pos.y == int(wh[1]) \
				and not (_state.get("flags", {}) as Dictionary).has("wrong_hex_done"):
			_show_encounter(wrong)
			return
	# Weather with teeth · the cold, the bare head.
	_apply_weather_bites()
	if int(_state.get("grit", 6)) <= 0:
		_fold_home()
		queue_redraw()
		return
	# The text engine · every hex says something. After a dealing,
	# the quadrant says it differently.
	var terrain := _terrain_at(_pos.x, _pos.y)
	var quad_verb := _dealt_verb(_quadrant_of(_pos))
	var line := ""
	if quad_verb == "draw" and _hash_qr(_pos.x, _pos.y, 17) % 2 == 0:
		line = String(MOURNING_LINES.get(terrain, ""))
	elif quad_verb == "unweave" and _hash_qr(_pos.x, _pos.y, 17) % 3 == 0:
		line = String(PEACE_LINES.get(terrain, ""))
	if line == "":
		var lines: Array = TRAVEL_LINES.get(terrain, [])
		if not lines.is_empty():
			line = String(lines[_hash_qr(_pos.x, _pos.y, 3) % lines.size()])
	if line != "":
		_say(line)
	_maybe_whisper_trail()
	# Sister weather when her corner is near.
	var dealt2: Dictionary = _state.get("witches_dealt", {})
	var cue := ""
	for w in _seats().keys():
		if dealt2.has(w):
			continue
		var s: Array = _seats()[w]
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
		# Number keys pick the Nth choice while an encounter or a town
		# menu is up — a keyboard/pad path that never depends on
		# finding a small button with the pointer.
		if not _choice_btns.is_empty() \
				and kev.keycode >= KEY_1 and kev.keycode <= KEY_9:
			var pick: int = int(kev.keycode) - int(KEY_1)
			if pick < _choice_btns.size():
				var pb: Button = _choice_btns[pick] as Button
				if pb != null and is_instance_valid(pb) and not pb.disabled:
					pb.emit_signal("pressed")
					get_viewport().set_input_as_handled()
			return
		match kev.keycode:
			KEY_ESCAPE:
				if _encounter.has("_town"):
					_close_town()
					get_viewport().set_input_as_handled()
				elif _encounter.is_empty():
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
	# Base ~18% of hexes carry a beat · the west's early dark doubles
	# it in her aura · an unwoven quadrant, truly calm, halves it.
	var chance := 18
	if _in_aura("west"):
		chance = 36
	elif _dealt_verb(_quadrant_of(_pos)) == "unweave":
		chance = 9
	if h % 100 >= chance:
		return
	var seen: Array = _state.get("encounters_seen", [])
	var flags: Dictionary = _state.get("flags", {})
	var pool_all: Array = (_enc.get("by_terrain", {}) as Dictionary).get(terrain, [])
	if pool_all.is_empty():
		return
	# Flag-gated deck · chain beats only surface once their thread is
	# live, and one-shot beats spend themselves globally.
	var pool: Array = []
	var priority: Array = []
	for e_v in pool_all:
		var cand: Dictionary = e_v
		var nf := String(cand.get("need_flag", ""))
		if nf != "" and not flags.has(nf):
			continue
		var bf := String(cand.get("block_flag", ""))
		if bf != "" and flags.has(bf):
			continue
		if bool(cand.get("once", false)) and seen.has(String(cand["id"])):
			continue
		pool.append(cand)
		if bool(cand.get("priority", false)):
			priority.append(cand)
	if not priority.is_empty():
		pool = priority
	if pool.is_empty():
		return
	var e: Dictionary = pool[h % pool.size()]
	var key := "%s@%d,%d" % [String(e["id"]), _pos.x, _pos.y]
	if bool(e.get("once", false)):
		key = String(e["id"])
	if seen.has(key):
		return
	seen.append(key)
	_state["encounters_seen"] = seen
	_show_encounter(e)


func _show_encounter(e: Dictionary) -> void:
	_clear_town_buttons()
	_encounter = e
	_say("— " + String(e.get("text", "")))
	var idx := 1
	for ch_v in e.get("choices", []):
		var ch: Dictionary = ch_v
		var label := "  %d · %s  " % [idx, String(ch.get("label", ""))]
		var blocked := false
		# Choices with a price on them · silver spends, lore gates.
		var need_ag: int = int(ch.get("need_silver", 0))
		var need_lo: int = int(ch.get("need_lore", 0))
		if need_ag > 0:
			label = "  %d · %s · %d ag  " % [idx, String(ch.get("label", "")), need_ag]
			blocked = int(_state.get("silver", 0)) < need_ag
		if need_lo > 0:
			label = "  %d · %s · needs %d lore  " % [idx, String(ch.get("label", "")), need_lo]
			blocked = blocked or int(_state.get("lore", 0)) < need_lo
		_add_choice_button(label, blocked, _resolve_encounter.bind(ch))
		idx += 1
	# NEVER leave the rider with a live encounter and no way out of
	# it — that is precisely how the ride "stops". An encounter whose
	# every choice is priced out of reach, or which shipped with no
	# choices at all, still gets a way to ride on.
	var any_live := false
	for b_v in _choice_btns:
		var b: Button = b_v as Button
		if b != null and is_instance_valid(b) and not b.disabled:
			any_live = true
			break
	if not any_live:
		_add_choice_button("  · ride on ·  ", false,
				_resolve_encounter.bind({"text": "you leave it where it lies."}))
	queue_redraw()


func _resolve_encounter(ch: Dictionary) -> void:
	_clear_town_buttons()
	var was_bounty := String(_encounter.get("id", "")).begins_with("bounty_")
	_encounter = {}
	# Up-front prices · silver spends on the choosing.
	if int(ch.get("need_silver", 0)) > 0:
		_state["silver"] = maxi(0, int(_state.get("silver", 0)) - int(ch.get("need_silver", 0)))
	# Chain flags + tokens the deck can set.
	if String(ch.get("set_flag", "")) != "":
		var flags: Dictionary = _state.get("flags", {})
		flags[String(ch["set_flag"])] = true
		_state["flags"] = flags
	if String(ch.get("token", "")) != "":
		OneironauticsTokens.add(String(ch["token"]))
	# The south's thirst · in her aura, what costs grit costs deeper.
	var grit_delta: int = int(ch.get("grit", 0))
	if grit_delta < 0 and _in_aura("south"):
		grit_delta -= 1
		_say("· the dry air takes its share on top ·")
	_state["grit"] = clampi(int(_state.get("grit", 6)) + grit_delta, 0, 9)
	_state["silver"] = maxi(0, int(_state.get("silver", 3)) + int(ch.get("silver", 0)))
	# The west's parley price · you gave the question away, and lore
	# is what questions carry. Bought novels still work; asking doesn't.
	var lore_delta: int = int(ch.get("lore", 0))
	if lore_delta > 0 and _dealt_verb("west") == "parley":
		lore_delta = 0
		_say("· you reach for the question that would hold it, and the question isn't there. it runs through like water ·")
	_state["lore"] = maxi(0, int(_state.get("lore", 0)) + lore_delta)
	_say(String(ch.get("text", "")))
	if lore_delta > 0:
		_sfx("page_turn", 0.5)
		_say("· that is LORE, and you can hold it · LORE %d ·" % int(_state.get("lore", 0)))
	# Bounty dealings · capture rides with you, mercy spends the notice.
	if was_bounty:
		var bounty: Dictionary = _state.get("bounty", {})
		if bool(ch.get("capture", false)):
			bounty["stage"] = "captive"
			_state["bounty"] = bounty
			_say("· the notice is satisfied · deliver to any township board ·")
		else:
			var done: Array = _state.get("bounties_done", [])
			done.append(String(bounty.get("id", "")))
			_state["bounties_done"] = done
			_state["bounty"] = {}
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


# ─── Townships · the trading post keeps hours ────────────────────

func _find_bounty(bid: String) -> Dictionary:
	for b_v in _bounty_defs:
		var b: Dictionary = b_v
		if String(b.get("id", "")) == bid:
			return b
	return {}


func _town_surcharge() -> int:
	# Widow-weather · a town in a DRAWn sister's quadrant charges
	# for its grief. THE OUTFIT · the mourning veil says you are
	# grieving too, and the surcharge is quietly not mentioned.
	if StickLoop.flag("sisters_wyrd", "mourning_veil"):
		return 0
	return 1 if _dealt_verb(_quadrant_of(_pos)) == "draw" else 0


func _arrive_township(t: Dictionary) -> void:
	_say(String(t.get("arrive", "")))
	if _town_surcharge() > 0:
		_say("the town is wearing black for her. prices are up · grief has overheads.")
	# A captive in tow · any board pays.
	var bounty: Dictionary = _state.get("bounty", {})
	if not bounty.is_empty() and String(bounty.get("stage", "")) == "captive":
		var bdef := _find_bounty(String(bounty.get("id", "")))
		var reward: int = int(bdef.get("reward", 3))
		_state["silver"] = int(_state.get("silver", 0)) + reward
		var done: Array = _state.get("bounties_done", [])
		done.append(String(bounty.get("id", "")))
		_state["bounties_done"] = done
		var paid: int = int(_state.get("bounties_paid", 0)) + 1
		_state["bounties_paid"] = paid
		_state["bounty"] = {}
		_sfx("coin", 0.7)
		_say("the board pays out · %d SILVER · the clerk does not ask questions, which is what the silver is partly for." % reward)
		if paid >= 3 and not bool(_state.get("board_cleared_told", false)):
			_state["board_cleared_told"] = true
			OneironauticsTokens.add("wyrd_notice_board_cleared")
			_say("· three notices ridden down in one ride · the territory has started describing YOU to strangers ·")
	_open_town_menu(t)


# Choice buttons float over map art — a solid dark box with a bone
# border keeps them legible on any terrain.
func _style_choice_btn(b: Button) -> void:
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(C_INK.r, C_INK.g, C_INK.b, 0.92)
	sb.border_color = Color(C_BONE.r, C_BONE.g, C_BONE.b, 0.55)
	sb.set_border_width_all(1)
	sb.set_corner_radius_all(3)
	sb.set_content_margin_all(6)
	b.add_theme_stylebox_override("normal", sb)
	var sbh := sb.duplicate()
	sbh.border_color = C_BONE
	b.add_theme_stylebox_override("hover", sbh)
	b.add_theme_color_override("font_color", C_BONE)


func _clear_town_buttons() -> void:
	# remove_child BEFORE queue_free: queue_free is deferred, so a
	# clear-then-rebuild in the same frame would otherwise leave the
	# old buttons sitting in the row beside the new ones.
	for b_v in _choice_btns:
		var b: Node = b_v as Node
		if b != null and is_instance_valid(b):
			if b.get_parent() != null:
				b.get_parent().remove_child(b)
			b.queue_free()
	_choice_btns.clear()


func _town_button(label: String, disabled: bool, cb: Callable) -> void:
	_add_choice_button(label, disabled, cb, 13)


# The one place a choice button gets made. Everything lands in the
# anchored row — no caller may pass pixel coordinates.
func _add_choice_button(label: String, disabled: bool, cb: Callable,
		font_size: int = 14) -> Button:
	var b := Button.new()
	b.text = label
	b.add_theme_font_size_override("font_size", font_size)
	b.disabled = disabled
	b.focus_mode = Control.FOCUS_ALL
	_style_choice_btn(b)
	b.pressed.connect(cb)
	if _choice_row != null:
		_choice_row.add_child(b)
	else:
		add_child(b)
	_choice_btns.append(b)
	# First enabled button takes focus so the pad/keyboard can act
	# without hunting for the pointer.
	if not disabled and _choice_btns.size() == 1:
		b.grab_focus.call_deferred()
	return b


func _open_town_menu(t: Dictionary) -> void:
	_clear_town_buttons()
	_encounter = {"_town": String(t.get("id", ""))}
	var silver: int = int(_state.get("silver", 0))
	var grit: int = int(_state.get("grit", 6))
	var surcharge := _town_surcharge()
	var hotel_cost: int = int(_services.get("hotel_cost", 2)) + surcharge
	var saloon_cost: int = int(_services.get("saloon_cost", 1)) + surcharge
	var book_cost: int = int(_services.get("bookstall_cost", 2)) + surcharge
	var book_cap: int = int(_services.get("bookstall_cap", 2))
	var bought: Dictionary = _state.get("bookstall_bought", {})
	var here: int = int(bought.get(String(t.get("id", "")), 0))
	# THE OUTFIT · CREDIT AT THE BOARDS · five townships, one name in
	# five ledgers. Two silver of slack, once per ride, so a bad
	# stretch doesn't hard-lock you out of every service in town.
	var slack := 0
	if StickLoop.flag("sisters_wyrd", "town_credit") \
			and not bool(_state.get("credit_spent", false)):
		slack = 2
	var purse: int = silver + slack
	_town_button("  HOTEL · %d ag  " % hotel_cost,
			purse < hotel_cost or grit >= 6, _town_hotel.bind(t))
	_town_button("  SALOON · %d ag  " % saloon_cost,
			purse < saloon_cost, _town_saloon.bind(t))
	_town_button("  BOOKSTALL · %d ag  " % book_cost,
			purse < book_cost or here >= book_cap, _town_bookstall.bind(t))
	_town_button("  NOTICE BOARD  ", false, _open_notice_board.bind(t))
	_town_button("  · ride on ·  ", false, _close_town)
	queue_redraw()


func _close_town() -> void:
	_clear_town_buttons()
	_encounter = {}
	_say("the town lets you go the way towns do · without comment.")
	queue_redraw()


## Pay for a service. When the purse can't cover it, the boards'
## credit does — once per ride, and the clerk says so out loud.
func _pay(cost: int) -> void:
	var have: int = int(_state.get("silver", 0))
	if cost > have and StickLoop.flag("sisters_wyrd", "town_credit") \
			and not bool(_state.get("credit_spent", false)):
		_state["credit_spent"] = true
		_say("· the clerk writes your name down instead of taking coin · that was the once ·")
	_state["silver"] = maxi(0, have - cost)


func _town_hotel(t: Dictionary) -> void:
	_pay(int(_services.get("hotel_cost", 2)) + _town_surcharge())
	_state["grit"] = maxi(int(_state.get("grit", 0)), 6)
	_sfx("coin", 0.5)
	_say(String(_services.get("hotel_text", "")))
	_open_town_menu(t)


func _town_saloon(t: Dictionary) -> void:
	_pay(int(_services.get("saloon_cost", 1)) + _town_surcharge())
	_state["grit"] = clampi(int(_state.get("grit", 0)) + 1, 0, 9)
	_sfx("coin", 0.4)
	_say(String(_services.get("saloon_text", "")))
	_say(String(t.get("rumor", "%s")) % _town_rumor_line())
	_open_town_menu(t)


func _town_bookstall(t: Dictionary) -> void:
	_pay(int(_services.get("bookstall_cost", 2)) + _town_surcharge())
	_state["lore"] = int(_state.get("lore", 0)) + 1
	var bought: Dictionary = _state.get("bookstall_bought", {})
	var tid := String(t.get("id", ""))
	bought[tid] = int(bought.get(tid, 0)) + 1
	_state["bookstall_bought"] = bought
	_sfx("page_turn", 0.5)
	_say(String(_services.get("bookstall_text", "")))
	_open_town_menu(t)


func _town_rumor_line() -> String:
	var dealt: Dictionary = _state.get("witches_dealt", {})
	var best := ""
	var best_d := 999
	for w in _seats().keys():
		if dealt.has(w):
			continue
		var s: Array = _seats()[w]
		var d := _hex_dist(_pos, Vector2i(int(s[0]), int(s[1])))
		if d < best_d:
			best_d = d
			best = String(w)
	match best:
		"north": return "snow holds the north road · %d hexes out, they say" % best_d
		"east": return "the dawn's been stuck red past the mission · %d hexes east" % best_d
		"south": return "the south road's gone dry as a sermon · %d hexes" % best_d
		"west": return "sunset keeps coming early out west · %d hexes that way" % best_d
	return "the weather's just weather now, all four roads. nobody trusts it"


func _open_notice_board(t: Dictionary) -> void:
	_clear_town_buttons()
	var bounty: Dictionary = _state.get("bounty", {})
	if not bounty.is_empty():
		var bdef := _find_bounty(String(bounty.get("id", "")))
		if String(bounty.get("stage", "")) == "captive":
			_say("the clerk eyes what you brought in. wrong board? any board pays · but you were just paid here, so: the wall, then.")
		else:
			_say("your notice, again, in the clerk's fair hand: %s" % String(bdef.get("notice", "")))
		_town_button("  · back ·  ", false, _open_town_menu.bind(t))
		return
	var done: Array = _state.get("bounties_done", [])
	var pool: Array = []
	for b_v in _bounty_defs:
		var b: Dictionary = b_v
		if not done.has(String(b.get("id", ""))):
			pool.append(b)
	if pool.is_empty():
		_say("the board is bare · you cleared it. the clerk has taken up whittling.")
		_town_button("  · back ·  ", false, _open_town_menu.bind(t))
		return
	var hx: Array = t.get("hex", [0, 0])
	var pick: Dictionary = pool[_hash_qr(int(hx[0]), int(hx[1]), done.size()) % pool.size()]
	_say(String(pick.get("notice", "")))
	_town_button("  TAKE THE NOTICE  ", false, _take_notice.bind(t, pick))
	_town_button("  · leave it ·  ", false, _open_town_menu.bind(t))


func _take_notice(t: Dictionary, bdef: Dictionary) -> void:
	_state["bounty"] = {"id": String(bdef.get("id", "")), "stage": "posted"}
	_sfx("page_turn", 0.4)
	_say("you fold the notice into your coat. the territory now contains one hex that is expecting you.")
	_open_town_menu(t)


func _maybe_whisper_trail() -> void:
	var bounty: Dictionary = _state.get("bounty", {})
	if bounty.is_empty() or String(bounty.get("stage", "")) != "posted":
		return
	if bool(bounty.get("whispered", false)):
		return
	var bdef := _find_bounty(String(bounty.get("id", "")))
	if bdef.is_empty():
		return
	var tgt: Array = bdef.get("target", [99, 99])
	if _hex_dist(_pos, Vector2i(int(tgt[0]), int(tgt[1]))) <= 3:
		bounty["whispered"] = true
		_state["bounty"] = bounty
		_say("· the trail freshens · hoofprints, a cold fire, a wrongness the hexes pass along like gossip · close now ·")


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
				# Focus falloff: full light where you are, dusk two hexes
				# out, near-dark at the horizon. Without this every hex
				# renders at equal weight and the field reads as soup.
				var d: int = _hex_dist(Vector2i(q, r), _pos)
				var tint := Color(1, 1, 1)
				if d > 6:
					tint = Color(0.40, 0.40, 0.46)
				elif d > 2:
					tint = Color(0.66, 0.66, 0.68)
				draw_texture(tex, c - Vector2(TILE_W / 2.0, TILE_H / 2.0), tint)
			else:
				# past the rim, the weave shows — dimmed, violet-shot
				draw_texture(tex, c - Vector2(TILE_W / 2.0, TILE_H / 2.0),
						Color(0.30, 0.26, 0.38, 0.5))

	# marks · home + seats + the five towns. The east's parley price
	# was a memory of home — the map no longer admits to one.
	var home_c := _axial_to_px(0, 0)
	if _dealt_verb("east") != "parley":
		_label_plate(font, home_c + Vector2(-18, -26), "HOME", 13, C_BONE)
	for t_v in _town_defs:
		var t: Dictionary = t_v
		var thx: Array = t.get("hex", [0, 0])
		var tc := _axial_to_px(int(thx[0]), int(thx[1]))
		if tc.x > -80.0 and tc.x < 1360.0 and tc.y > -60.0 and tc.y < 780.0:
			_label_plate(font, tc + Vector2(-30, -28), String(t.get("name", "")), 11, C_BONE)
	var dealt: Dictionary = _state.get("witches_dealt", {})
	for w in _seats().keys():
		var s: Array = _seats()[w]
		var sc := _axial_to_px(int(s[0]), int(s[1]))
		if sc.x > -60.0 and sc.x < 1340.0 and sc.y > -60.0 and sc.y < 780.0:
			_label_plate(font, sc + Vector2(-30, -28), "HER SEAT", 13, C_WYRD)
			if dealt.has(w):
				draw_line(sc + Vector2(-10, -6), sc + Vector2(10, 6), C_WYRD, 2.0)
	# seat direction arrows at the screen edge for undealt sisters
	for w2 in _seats().keys():
		if dealt.has(w2):
			continue
		var s2: Array = _seats()[w2]
		var sc2 := _axial_to_px(int(s2[0]), int(s2[1]))
		if sc2.x < 0.0 or sc2.x > 1280.0 or sc2.y < 0.0 or sc2.y > 720.0:
			var dir := (sc2 - VIEW_CENTER).normalized()
			var edge := VIEW_CENTER + dir * 300.0
			draw_line(edge, edge + dir * 16.0, C_WYRD, 2.0)
			draw_string(font, edge + dir * 24.0 + Vector2(-8, 4), String(w2[0]).to_upper(),
					HORIZONTAL_ALIGNMENT_LEFT, -1, 14, C_WYRD)

	# the drifter, on the hex — with a ground-ring so the eye can
	# always find them in one glance
	draw_arc(VIEW_CENTER + Vector2(0, 6), 22.0, 0.0, TAU, 24, C_BONE, 2.0)
	draw_arc(VIEW_CENTER + Vector2(0, 6), 25.0, 0.0, TAU, 24, Color(C_INK.r, C_INK.g, C_INK.b, 0.8), 2.0)
	draw_texture(FIGURE_ART.drifter(), VIEW_CENTER - Vector2(9.0, 26.0))

	# the eight-pointed compass card corner · always · uncommented
	var cc := Vector2(1200, 70)
	for i in range(8):
		var a := float(i) * PI / 4.0
		draw_line(cc, cc + Vector2(cos(a), sin(a)) * 24.0, C_BONE if i % 2 == 0 else C_WYRD, 1.5)
	draw_circle(cc, 3.0, C_BLOOD)


# Dark plate behind map text — labels drawn bare on hex art vanish.
func _label_plate(font: Font, at: Vector2, text: String, size: int, col: Color) -> void:
	var w: float = font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	draw_rect(Rect2(at + Vector2(-4, -size - 2), Vector2(w + 8, size + 7)),
			Color(C_INK.r, C_INK.g, C_INK.b, 0.82))
	draw_string(font, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, col)


func _sfx(preset: String, vol: float = 1.0) -> void:
	var sb := get_node_or_null("/root/SFXBank")
	if sb != null and sb.has_method("play"):
		sb.play(preset, vol)
