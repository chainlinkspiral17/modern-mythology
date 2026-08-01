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
signal crisis_over(results: Dictionary)
# A route-only reward found by WALKING (town_life.json moments) —
# the year scene applies gives{} without spending the week.
signal town_moment(moment: Dictionary)

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

# ── TOWN LIFE · what walking gives that a list cannot ────────────
# ("walking around versus picking from a list is superficial.")
# Three systems, all data in town_life.json:
#   PRESENCE  people are AT places by month + weather — and away.
#             Approaching a place says who is (or isn't) there
#             before you commit; absence is information.
#   OVERHEARD crossing Main Street catches fragments of the town
#             talking to itself, per season.
#   MOMENTS   route-only encounters at spots BETWEEN places. Only
#             a walker finds them, and they pay (journal lines,
#             bond touches, thread clues) WITHOUT spending a week.
var _life: Dictionary = {}
var _wx: String = "clear"
var _moments_taken: Array = []      # ids spent (run-persistent, from the year)
var _last_near: String = ""         # sight lines fire once per approach
var _street_cd: float = 0.0         # overheard cooldown
var _overheard_n: int = 0           # rotation index within a visit

# ── WAVE C · the night the water comes (2026-07-28) ──────────────
# The same town, played once, against the clock. The bell rings,
# the water goes out, and then it comes back — climbing the map
# from the bay. Who you save is who you physically REACH: each
# rescue roots you in place while the water keeps rising. What
# you built all year (sea-sense, bonds, the bicycle, the night
# off the bar, the thread) is speed, access, and options here.
const CRISIS_LEN := 75.0        # seconds, bell to the last water
const CRISIS_SLACK := 18.0      # the water is OUT · position yourself
const FLOOD_TOP := 392.0        # the highest the water walks
var _crisis: bool = false
var _crisis_t: float = 0.0
var _crisis_state: Dictionary = {}
var _flood_y: float = 580.0
var _rescues: Array = []        # completed target ids
var _rescue_busy: String = ""   # target mid-rescue
var _rescue_left: float = 0.0
var _crisis_speed: float = 190.0
var _crisis_done: bool = false

# target id -> availability + the work it takes
const RESCUES := {
	"dock":    {"label": "CAST OFF THE FLEET", "work": 6.0,
		"line": "You and Del get lines off cleat after cleat, shouting boats out to deep water."},
	"cannery": {"label": "THE ONES THE FLEET FORGOT", "work": 5.0,
		"line": "The night crew is still on the finger pier. You take the skiff out for them the way you did once before."},
	"estelle": {"label": "THE GRAY HOUSE", "work": 5.0,
		"line": "She will not leave the window. You say what only someone who has sat with her could say."},
}


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_to_group("ui")
	_walker.load_from(WALKER_SPRITE)
	var lf := FileAccess.open("res://resources/games/vol7/salmonberry/town_life.json", FileAccess.READ)
	if lf != null:
		var parsed: Variant = JSON.parse_string(lf.get_as_text())
		lf.close()
		if parsed is Dictionary:
			_life = parsed
	_build_ui()
	set_process(true)


func boot_crisis(state: Dictionary) -> void:
	_crisis = true
	_crisis_state = state
	_month = 6
	_season = SEASONS["winter"]
	_bonds = state.get("bonds", {})
	_acts_by_loc = {}
	_pos = Vector2(160, 470)
	_crisis_t = 0.0
	_flood_y = 640.0
	_rescues = []
	_rescue_busy = ""
	_crisis_done = false
	_crisis_speed = 240.0 if (state.get("gear", []) as Array).has("bicycle") else 190.0
	_hdr_lbl.text = "SALMONBERRY · MARCH 1964 · GOOD FRIDAY"
	_hint_lbl.text = "arrows run · E where it matters"
	_msg("The bell. The water has gone out — too far out. It is coming back. Vovo is at the house; E there ends the night, up the hill.")
	_sfx("harbor_bell", 1.0)
	queue_redraw()


func _crisis_available(tid: String) -> bool:
	if _rescues.has(tid):
		return false
	var apts: Dictionary = _crisis_state.get("apts", {})
	match tid:
		"dock":
			return int(apts.get("sea", 0)) >= 3 or int(_bonds.get("del", 0)) >= 2
		"cannery":
			return bool(_crisis_state.get("helped_boat", false))
		"estelle":
			return int(_bonds.get("estelle", 0)) >= 2 or int(apts.get("heart", 0)) >= 3 				or _crisis_thread_ready()
	return false


func _crisis_thread_ready() -> bool:
	var clues: Array = _crisis_state.get("thread_clues", [])
	return clues.size() >= 2 and (clues.has("estelle_light") or clues.has("estelle_name"))


func _crisis_flooded(tid: String) -> bool:
	return _flood_y < float((PLACES[tid]["pos"] as Vector2).y) - 14.0


func _crisis_tick(delta: float) -> void:
	if _crisis_done:
		return
	_crisis_t += delta
	# the water: out for the slack, then walking up the town
	if _crisis_t > CRISIS_SLACK:
		var k: float = clampf((_crisis_t - CRISIS_SLACK) / (CRISIS_LEN - CRISIS_SLACK), 0.0, 1.0)
		_flood_y = 640.0 - (640.0 - FLOOD_TOP) * pow(k, 1.25)
	# mid-rescue: rooted in place while the work happens
	if _rescue_busy != "":
		_rescue_left -= delta
		if _rescue_left <= 0.0:
			_rescues.append(_rescue_busy)
			_msg(String((RESCUES[_rescue_busy] as Dictionary)["line"]))
			_sfx("wave_break", 0.6)
			_rescue_busy = ""
		queue_redraw()
		return
	# movement (faster with the bicycle year)
	_dir = Vector2.ZERO
	if Input.is_key_pressed(KEY_LEFT) or Input.is_key_pressed(KEY_A): _dir.x -= 1
	if Input.is_key_pressed(KEY_RIGHT) or Input.is_key_pressed(KEY_D): _dir.x += 1
	if Input.is_key_pressed(KEY_UP) or Input.is_key_pressed(KEY_W): _dir.y -= 1
	if Input.is_key_pressed(KEY_DOWN) or Input.is_key_pressed(KEY_S): _dir.y += 1
	if _dir != Vector2.ZERO:
		_pos += _dir.normalized() * _crisis_speed * delta
		_pos.x = clampf(_pos.x, 40, 1240)
		_pos.y = clampf(_pos.y, 60, minf(640.0, _flood_y - 18.0))
	# the water reaches Vovo's porch → the night takes itself
	if _flood_y < float((PLACES["home"]["pos"] as Vector2).y) + 20.0:
		_end_crisis(true)
		return
	queue_redraw()


func _crisis_interact() -> void:
	var pid := _place_near()
	if pid == "":
		return
	if pid == "home":
		_end_crisis(false)
		return
	if not RESCUES.has(pid):
		_msg("Nothing here the water wants tonight. Vovo. The hill.")
		return
	if _crisis_flooded(pid):
		_msg("Too late — the water is already through here. It does not renegotiate.")
		return
	if not _crisis_available(pid):
		match pid:
			"dock":
				_msg("Del is already shouting men to lines. You don't know the bar well enough to be more than in the way.")
			"cannery":
				_msg("The night crew is being seen to. Nobody here knows to listen for you.")
			"estelle":
				_msg("The curtain does not move. You have not sat with her enough for the door to open tonight.")
		return
	_rescue_busy = pid
	_rescue_left = float((RESCUES[pid] as Dictionary)["work"])
	_msg("(" + String((RESCUES[pid] as Dictionary)["label"]) + " — hold on. This takes what it takes.)")


func _end_crisis(forced: bool) -> void:
	if _crisis_done:
		return
	_crisis_done = true
	crisis_over.emit({
		"saved": _rescues.duplicate(),
		"told_estelle": _rescues.has("estelle") and _crisis_thread_ready(),
		"forced": forced,
	})


func boot(month: int, acts_by_loc: Dictionary, bonds: Dictionary,
		extra: Dictionary = {}) -> void:
	_month = clampi(month, 0, 9)
	_acts_by_loc = acts_by_loc
	_bonds = bonds
	_wx = String(extra.get("wx", "clear"))
	_moments_taken = extra.get("moments_taken", [])
	_last_near = ""
	_street_cd = 4.0     # let the arrival line breathe before gossip
	_overheard_n = int(extra.get("seed", 0)) + month   # varies per run+month
	_season = SEASONS[_season_key()]
	_pos = Vector2(160, 470)
	_hdr_lbl.text = "SALMONBERRY · %s %d" % [MONTHS[_month].to_upper(), (1963 if _month <= 3 else 1964)]
	_msg("the town is one walk wide. E at a place to spend the month there. ESC for the list.")
	queue_redraw()


# ── PRESENCE · who is actually here, this month, this weather ────

func _presence_for(pid: String) -> Dictionary:
	for e_v in _life.get("presence", []):
		var e: Dictionary = e_v
		if String(e.get("pid", "")) != pid:
			continue
		var months: Array = e.get("months", [])
		if not months.is_empty() and not months.has(float(_month)) and not months.has(_month):
			continue
		var wxs: Array = e.get("wx", [])
		if not wxs.is_empty() and not wxs.has(_wx):
			continue
		return e
	return {}


func _life_tick(delta: float) -> void:
	# sight lines · fire once each time you come near a place
	var near := _place_near()
	if near != _last_near:
		_last_near = near
		if near != "":
			var pr := _presence_for(near)
			var sight := String(pr.get("sight", ""))
			if sight != "":
				_msg(sight)
	# overheard · crossing the Main Street band
	_street_cd = maxf(0.0, _street_cd - delta)
	if _street_cd == 0.0 and _pos.y > 290.0 and _pos.y < 385.0 \
			and _pos.x > 180.0 and _pos.x < 1020.0 and _dir != Vector2.ZERO:
		var pool: Array = (_life.get("overheard", {}) as Dictionary).get(_season_key(), [])
		if not pool.is_empty():
			_msg(String(pool[_overheard_n % pool.size()]))
			_overheard_n += 1
			_street_cd = 22.0
	# moments · route-only finds, at spots between places
	for m_v in _life.get("moments", []):
		var m: Dictionary = m_v
		var mid := String(m.get("id", ""))
		if _moments_taken.has(mid):
			continue
		var months: Array = m.get("months", [])
		if not months.is_empty() and not months.has(float(_month)) and not months.has(_month):
			continue
		var mp: Array = m.get("pos", [0, 0])
		if _pos.distance_to(Vector2(float(mp[0]), float(mp[1]))) < 42.0:
			_moments_taken.append(mid)
			_msg(String(m.get("line", "")))
			_sfx("hotspot_look", 0.6)
			town_moment.emit(m)
			break


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
	if _crisis:
		_crisis_tick(delta)
		return
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
	_life_tick(delta)
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
			if _crisis:
				_msg("There is no putting this night down. Vovo. The hill.")
			elif _panel != null:
				_close_panel()
			else:
				quit.emit()
		elif kev.keycode == KEY_E and _panel == null:
			get_viewport().set_input_as_handled()
			if _crisis:
				if _rescue_busy == "" and not _crisis_done:
					_crisis_interact()
			else:
				var pid := _place_near()
				if pid != "":
					_open_offers(pid)


# ─── the offers panel · what this month can be, here ─────────────

func _open_offers(pid: String) -> void:
	var place: Dictionary = PLACES[pid]
	var acts: Array = _acts_by_loc.get(pid, [])
	var pr := _presence_for(pid)
	# When the usual person is AWAY, their activities go with them —
	# the month is different because of who is where. That is what a
	# walk knows and a list doesn't.
	if bool(pr.get("away", false)):
		acts = []
	if acts.is_empty():
		var talk := String(pr.get("talk", ""))
		_msg(talk if talk != "" else String(place.get("empty", "nothing to do here this month.")))
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
	var who := String(pr.get("who", place.get("who", "")))
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
		# PRESENCE, drawn · a small figure by the door when somebody
		# is here; nothing when they are away. Readable at a glance
		# before you cross the map for them.
		if not _crisis:
			var pr := _presence_for(String(pid))
			var here_who := String(pr.get("who", who))
			if not bool(pr.get("away", false)) and here_who != "":
				var fp := p + Vector2(-30, 20)
				draw_circle(fp + Vector2(0, -8), 3.0, C_INK)
				draw_rect(Rect2(fp.x - 3, fp.y - 5, 6, 12), C_INK)

	# MOMENTS · a faint glint where a route-only find waits. Subtle on
	# purpose — a shimmer you notice walking past, not a map marker.
	if not _crisis:
		for m_v in _life.get("moments", []):
			var m: Dictionary = m_v
			if _moments_taken.has(String(m.get("id", ""))):
				continue
			var mm: Array = m.get("months", [])
			if not mm.is_empty() and not mm.has(float(_month)) and not mm.has(_month):
				continue
			var mp: Array = m.get("pos", [0, 0])
			var gp := Vector2(float(mp[0]), float(mp[1]))
			var a: float = 0.18 + 0.14 * sin(_t * 2.4 + gp.x)
			draw_circle(gp, 2.5, Color(C_FOAM.r, C_FOAM.g, C_FOAM.b, a))

	# ── the crisis layer: night, risen water, the work ──
	if _crisis:
		# dusk falls over everything painted so far
		draw_rect(Rect2(0, 0, 1280, 720), Color(0.06, 0.08, 0.12, 0.45))
		# lit windows hold against it
		draw_rect(Rect2(float((PLACES["home"]["pos"] as Vector2).x) - 10.0,
			float((PLACES["home"]["pos"] as Vector2).y) - 6.0, 20.0, 16.0), Color("e8c060"))
		draw_rect(Rect2(float((PLACES["estelle"]["pos"] as Vector2).x) - 10.0,
			float((PLACES["estelle"]["pos"] as Vector2).y) - 6.0, 20.0, 16.0), Color("e8c060"))
		# the water, wherever it has walked to
		if _flood_y < 640.0:
			draw_rect(Rect2(0, _flood_y, 1280, 720.0 - _flood_y), Color(0.16, 0.24, 0.30, 0.88))
			var churn := sin(_t * 5.0) * 3.0
			draw_line(Vector2(0, _flood_y + churn), Vector2(1280, _flood_y - churn), C_FOAM, 3.0)
			draw_line(Vector2(0, _flood_y + 10.0 - churn), Vector2(1280, _flood_y + 12.0 + churn),
				Color(C_FOAM.r, C_FOAM.g, C_FOAM.b, 0.35), 1.5)
		elif _crisis_t < CRISIS_SLACK:
			# the bay GONE — mud where the water should be
			draw_rect(Rect2(0, 580, 1280, 140), Color("6a6252"))
			draw_line(Vector2(0, 582), Vector2(1280, 582), Color("54503f"), 2.0)
		# countdown + targets
		var left: float = maxf(0.0, CRISIS_LEN - _crisis_t)
		_label(Vector2(640, 40), ("the water is out · %d" if _crisis_t < CRISIS_SLACK else "THE WATER · %d") % int(ceil(left)), C_FOAM, 16)
		for tid in RESCUES.keys():
			var tp: Vector2 = PLACES[tid]["pos"]
			if _rescues.has(String(tid)):
				_label(tp + Vector2(0, -60), "· SAFE ·", C_GOLD, 13)
			elif _crisis_flooded(String(tid)):
				_label(tp + Vector2(0, -60), "· gone ·", C_FOAM, 12)
			elif _crisis_available(String(tid)):
				_label(tp + Vector2(0, -60), "· " + String((RESCUES[tid] as Dictionary)["label"]) + " ·",
					Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.7 + 0.3 * sin(_t * 5.0)), 12)
		# mid-rescue progress arc on the kid
		if _rescue_busy != "":
			var frac: float = 1.0 - _rescue_left / float((RESCUES[_rescue_busy] as Dictionary)["work"])
			draw_arc(_pos, 26.0, -PI * 0.5, -PI * 0.5 + TAU * frac, 24, C_GOLD, 3.0)

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
