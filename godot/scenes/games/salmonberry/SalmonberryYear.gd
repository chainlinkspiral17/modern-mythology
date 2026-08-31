extends Control
class_name SalmonberryYear
## SALMONBERRY · the year loop · v2 · DEPTH PASS 2026-07-27.
##
## Ten months, September 1963 to June 1964 — and every month is FOUR
## WEEKS now, each week a real decision inside interlocking systems:
##
##   · ENERGY — a body budget. Hard work costs more than you have and
##     the town notices when you're worn thin. Rest is a choice with a
##     price (the week) and a payoff (Vovo).
##   · WEATHER — rolled per week from the month's climate. Storms
##     close the bay. Minus tides open the flats. A forecast lets you
##     plan one week ahead.
##   · MONEY — board is owed to the household every month. Gear from
##     the general store changes what your weeks can do.
##   · CHECKS — every activity rolls your aptitude against the work,
##     with the roll SHOWN. Strong weeks pay extra; rough weeks teach
##     grit and pay less.
##   · OPPORTUNITIES — nine dated events (events.json) that exist for
##     one week each and never come back. The fall run's biggest day.
##     A boat in trouble off the bar. The travelling show.
##   · BONDS — decay if you let a friendship sit for two months.
##
## March is still the night the water comes, and what you built all
## year — bonds, sea-sense, what you know about the boat — is what
## you can save.
##
## Emits (host contract): quit · month_complete(state) · year_over(result)
## F4-compliant via add_to_group("ui").

signal quit
signal month_complete(state: Dictionary)
signal year_over(result: Dictionary)

const ACTS_PATH := "res://resources/games/vol7/salmonberry/activities.json"
const ERRANDS_PATH := "res://resources/games/vol7/salmonberry/errands.json"
const NPCS_PATH := "res://resources/games/vol7/salmonberry/npcs.json"
const EVENTS_PATH := "res://resources/games/vol7/salmonberry/events.json"

const MONTHS := ["September", "October", "November", "December", "January",
	"February", "March", "April", "May", "June"]
# Season keys for outcome_by_season variants (see _pick_outcome).
const SEASON_OF := ["autumn", "autumn", "autumn", "winter", "winter",
	"winter", "spring", "spring", "spring", "summer"]
const SEASON_LINE := [
	"The fog does not lift until noon. The whole town smells of fish and cut cedar. You are the new kid.",
	"The fall run is on. The cannery runs day and night and the gulls never sleep.",
	"On the twenty-second the radio said the President was shot. The line stopped for the afternoon. Nobody knew what to do with their hands.",
	"Rain like the sky forgot how to stop. The town pulls in close. Vovo bakes.",
	"The lowest tides of the year come at first light, in the cold. The flats belong to whoever will get up.",
	"Gray on gray. The storms line up off the point and come in one after another.",
	"",
	"The first green. The alders leaf out. The town is quieter than it was; the water took some of it.",
	"The salmonberry blooms pink along every draw. The days get long.",
	"School lets out. A little travelling show sets up on the cannery lot — a Ferris wheel, a fortune tent. The last month, and you know the town now.",
]

const C_SEA  := Color("3b5a6b")
const C_SAND := Color("b8a882")
const C_FOG  := Color("c8cec4")
const C_FIR  := Color("33452f")
const C_RUST := Color("9c5a3a")
# Text variants · the paint hues fail WCAG on the dark panel
# (rust 3.2:1, sea 2.3:1 measured) · type uses these, fills
# keep the originals. contrast_audit.py is the enforcement.
const C_RUST_TXT := Color("d08a5e")
const C_SEA_TXT  := Color("8fb8c8")
const C_GOLD := Color("d8b048")
const C_INK  := Color("23282a")
const C_DIM  := Color("6a7068")
const C_PANEL := Color(0.10, 0.11, 0.10, 0.90)

const WEEKS_PER_MONTH := 4
const ENERGY_MAX := 10
const ENERGY_WEEKLY := 2        # what a week of sleep gives back
const REST_ENERGY := 5          # what a week of keeping to the house gives
const BOARD_DUE := 2            # owed to the household each month
const DECAY_AFTER_WEEKS := 8    # bonds untouched this long slip

# ── weather ──────────────────────────────────────────────────────
# Per-month climate: weighted kinds rolled per week, deterministic
# from the save's seed (reloading a save does not reroll the sky).
const WEATHER_TABLE := {
	0: [["clear", 4], ["fog", 4], ["rain", 2]],
	1: [["clear", 3], ["rain", 4], ["fog", 2], ["storm", 1]],
	2: [["rain", 5], ["storm", 3], ["fog", 2]],
	3: [["rain", 5], ["storm", 3], ["clear", 2]],
	4: [["minus", 3], ["clear", 2], ["rain", 3], ["storm", 2]],
	5: [["storm", 4], ["rain", 4], ["fog", 2]],
	7: [["rain", 3], ["clear", 4], ["fog", 3]],
	8: [["clear", 6], ["rain", 2], ["fog", 2]],
	9: [["clear", 7], ["fog", 3]],
}
const WEATHER_LINE := {
	"clear": "Clear over the water. The kind of week you can spend anywhere.",
	"fog":   "Fog to noon, silver after. The foghorn keeps its own time.",
	"rain":  "Rain most days. Outdoor work costs more than it says.",
	"storm": "Storms stacked up off the point. The bar is breaking — nothing crosses. Nobody works the bay this week.",
	"minus": "A minus tide, first light. The flats are open wider than they will be all season.",
}
const WEATHER_TAG := {
	"clear": "· clear ·", "fog": "· fog ·", "rain": "· rain ·",
	"storm": "· STORM ·", "minus": "· MINUS TIDE ·",
}

# ── the general store ────────────────────────────────────────────
const GEAR := [
	{"id": "clam_gun", "label": "a clam gun of your own", "cost": 4,
	 "hint": "digging goes twice as well (+2 on the flats, +$1)"},
	{"id": "rain_slicker", "label": "a real rain slicker", "cost": 5,
	 "hint": "rain stops costing you extra effort outdoors"},
	{"id": "bicycle", "label": "the used bicycle in Tuck's shed", "cost": 8,
	 "hint": "the town gets smaller — +1 energy back every week"},
	{"id": "guitar_strings", "label": "new strings for the guitar", "cost": 3,
	 "hint": "songs with Vovo count double"},
	{"id": "field_glasses", "label": "army-surplus field glasses", "cost": 6,
	 "hint": "you see more from the beach and the bluff (+1 outdoors)"},
]

var _s: Dictionary = {}
var _acts: Array = []
var _errands: Array = []       # errands.json entries · WAVE D
var _journal_total: int = 12
var _npcs: Dictionary = {}     # id -> npc dict
var _events: Array = []        # events.json entries


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	_load_data()


func boot(state: Dictionary) -> void:
	_s = state
	# defensive defaults — older (v1 monthly) saves upgrade in place
	if not _s.has("apts"): _s["apts"] = {"hands": 0, "sea": 0, "word": 0, "heart": 0, "wild": 0, "grit": 0}
	if not _s.has("bonds"): _s["bonds"] = {}
	if not _s.has("journal"): _s["journal"] = []
	if not _s.has("thread_clues"): _s["thread_clues"] = []
	if not _s.has("week"): _s["week"] = 1
	if not _s.has("energy"): _s["energy"] = 8
	if not _s.has("gear"): _s["gear"] = []
	if not _s.has("strain"): _s["strain"] = 0
	if not _s.has("bond_touch"):
		# Pre-depth saves never tracked touches.  Seed every existing
		# bond to "touched now" so the upgrade does not fire one
		# spurious decay wave across the whole web.
		var seeded: Dictionary = {}
		var now_week: int = int(_s.get("month", 0)) * WEEKS_PER_MONTH + int(_s.get("week", 1))
		for id_v in (_s.get("bonds", {}) as Dictionary).keys():
			seeded[String(id_v)] = now_week
		_s["bond_touch"] = seeded
	if not _s.has("events_taken"): _s["events_taken"] = []
	if not _s.has("errands_done"): _s["errands_done"] = []
	if not _s.has("board_month"): _s["board_month"] = -1
	if not _s.has("seed"): _s["seed"] = randi() % 100000
	_render()


func _load_data() -> void:
	var a: Dictionary = _read_json(ACTS_PATH)
	_acts = a.get("activities", [])
	_journal_total = int(a.get("journal_total", 12))
	var n: Dictionary = _read_json(NPCS_PATH)
	for npc_v in n.get("npcs", []):
		var npc: Dictionary = npc_v
		_npcs[String(npc.get("id", ""))] = npc
	var e: Dictionary = _read_json(EVENTS_PATH)
	_events = e.get("events", [])
	var er: Dictionary = _read_json(ERRANDS_PATH)
	_errands = er.get("errands", [])


func _read_json(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {}
	var f := FileAccess.open(path, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	return parsed if parsed is Dictionary else {}


# ─── deterministic weather ───────────────────────────────────────

var _week_flavor: Dictionary = {}   # "month,week" -> line · lazy-loaded

func _week_flavor_line(month: int, week: int) -> String:
	if _week_flavor.is_empty():
		var f := FileAccess.open(
				"res://resources/games/vol7/salmonberry/week_flavor.json",
				FileAccess.READ)
		if f == null:
			_week_flavor = {"_missing": true}
			return ""
		var parsed: Variant = JSON.parse_string(f.get_as_text())
		f.close()
		if parsed is Dictionary:
			var weeks: Variant = (parsed as Dictionary).get("weeks", {})
			if weeks is Dictionary:
				_week_flavor = weeks
		if _week_flavor.is_empty():
			_week_flavor = {"_missing": true}
	return String(_week_flavor.get("%d,%d" % [month, week], ""))


func _weather_for(month: int, week: int) -> String:
	if month == 6:
		return "storm"
	var table: Array = WEATHER_TABLE.get(month, [["clear", 1]])
	var rng := RandomNumberGenerator.new()
	rng.seed = int(_s.get("seed", 0)) * 100 + month * 10 + week
	var total: int = 0
	for row_v in table:
		var row: Array = row_v
		total += int(row[1])
	var roll: int = rng.randi_range(1, total)
	for row_v in table:
		var row: Array = row_v
		roll -= int(row[1])
		if roll <= 0:
			return String(row[0])
	return "clear"


func _luck_for(month: int, week: int) -> int:
	# The week's fortune die (0..2), fixed per save+week so reloading
	# does not reroll it.
	var rng := RandomNumberGenerator.new()
	rng.seed = int(_s.get("seed", 0)) * 977 + month * 31 + week * 7
	return rng.randi_range(0, 2)


# ─── render dispatch ─────────────────────────────────────────────

func _render() -> void:
	_clear_ui()
	_paint_backdrop()
	var month: int = int(_s.get("month", 0))
	if month >= MONTHS.size():
		_end_year()
	elif month == 6:
		_render_wave()
	else:
		_month_upkeep(month)
		_render_week()


func _clear_ui() -> void:
	for c in get_children():
		c.queue_free()


func _paint_backdrop() -> void:
	# The season picks its painted backdrop: winter months get the
	# storm coast, the rest the fog coast. ColorRects stay as the
	# fallback under a missing PNG (never remove the fallback).
	# month is a 0-based index: Sep 1963 = 0 … Jun 1964 = 9, so
	# winter (Nov–Feb) is indexes 2..5.
	var month: int = int(_s.get("month", 0))
	var art: String = "res://assets/art/salmonberry/winter.png" if (month >= 2 and month <= 5) \
			else "res://assets/art/salmonberry/coast.png"
	if ResourceLoader.exists(art):
		var tr := TextureRect.new()
		tr.texture = load(art)
		tr.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
		tr.modulate = Color(1, 1, 1, 0.92)
		add_child(tr)
		var scrim := ColorRect.new()
		scrim.color = Color(0.06, 0.08, 0.10, 0.30)
		scrim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		add_child(scrim)
		return
	var sky := ColorRect.new()
	sky.color = C_FOG
	sky.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(sky)
	var sea := ColorRect.new()
	sea.color = C_SEA
	sea.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	sea.offset_top = -180
	add_child(sea)


func _panel() -> VBoxContainer:
	var pc := PanelContainer.new()
	pc.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	pc.offset_left = 80
	pc.offset_right = -80
	pc.offset_top = 40
	pc.offset_bottom = -40
	var sb := StyleBoxFlat.new()
	sb.bg_color = C_PANEL
	sb.set_corner_radius_all(4)
	sb.set_content_margin_all(20)
	pc.add_theme_stylebox_override("panel", sb)
	add_child(pc)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 8)
	pc.add_child(v)
	return v


# ─── month upkeep: board owed + bonds slipping ───────────────────

var _upkeep_lines: Array = []

func _month_upkeep(month: int) -> void:
	if int(_s.get("board_month", -1)) >= month:
		return
	_s["board_month"] = month
	_upkeep_lines = []
	# board to the household (Vovo would never ask; you pay anyway)
	if month > 0:
		var money: int = int(_s.get("money", 0))
		if money >= BOARD_DUE:
			_s["money"] = money - BOARD_DUE
			_upkeep_lines.append("You leave $%d in the flour tin for board. Vovo pretends not to see you do it, the way she does every month." % BOARD_DUE)
		else:
			_s["strain"] = int(_s.get("strain", 0)) + 1
			var bonds: Dictionary = _s["bonds"]
			bonds["gran"] = maxi(0, int(bonds.get("gran", 0)) - 1)
			_upkeep_lines.append("The flour tin stays empty this month. Nothing is said. The house is a little heavier for it.")
	# bonds slip when a friendship sits too long
	var abs_week: int = month * WEEKS_PER_MONTH + 1
	var touch: Dictionary = _s["bond_touch"]
	var bonds_d: Dictionary = _s["bonds"]
	for id_v in bonds_d.keys():
		var id := String(id_v)
		if id == "gran":
			continue
		var lvl: int = int(bonds_d[id])
		if lvl <= 0:
			continue
		var last: int = int(touch.get(id, 0))
		if abs_week - last >= DECAY_AFTER_WEEKS:
			bonds_d[id] = lvl - 1
			touch[id] = abs_week   # one slip per lapse, not one per month
			_upkeep_lines.append("You have not knocked on %s's door in a long while. Something small goes quiet between you." % _npc_name(id))


# ─── the week ────────────────────────────────────────────────────

func _render_week() -> void:
	var month: int = int(_s.get("month", 0))
	var week: int = int(_s.get("week", 1))
	var wx: String = _weather_for(month, week)
	var v := _panel()

	var hdr := Label.new()
	hdr.text = "%s %d · week %d of %d   %s" % [MONTHS[month], (1963 if month <= 3 else 1964),
		week, WEEKS_PER_MONTH, String(WEATHER_TAG.get(wx, ""))]
	hdr.add_theme_font_size_override("font_size", 24)
	hdr.add_theme_color_override("font_color", C_RUST_TXT)
	v.add_child(hdr)

	if week == 1 and SEASON_LINE[month] != "":
		var season := Label.new()
		season.text = SEASON_LINE[month]
		season.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		season.add_theme_font_size_override("font_size", 14)
		season.add_theme_color_override("font_color", C_INK if month != 2 else C_RUST)
		v.add_child(season)

	# THE WEEK ITSELF · every one of the 40 weeks has its own line —
	# what the town is doing right now, independent of your choices.
	# From week_flavor.json ("salmonberry is lifeless" fix); missing
	# file or missing week degrades to nothing, silently.
	var wk_line: String = _week_flavor_line(month, week)
	if wk_line != "":
		var fl := Label.new()
		fl.text = wk_line
		fl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		fl.add_theme_font_size_override("font_size", 14)
		fl.add_theme_color_override("font_color", C_INK)
		v.add_child(fl)

	# weather now + the glass for next week (planning information)
	var wline := Label.new()
	wline.text = String(WEATHER_LINE.get(wx, ""))
	wline.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	wline.add_theme_font_size_override("font_size", 13)
	wline.add_theme_color_override("font_color", C_SEA_TXT)
	v.add_child(wline)
	var nxt: String = _forecast_line(month, week)
	if nxt != "":
		var fl := Label.new()
		fl.text = nxt
		fl.add_theme_font_size_override("font_size", 12)
		fl.add_theme_color_override("font_color", C_DIM)
		v.add_child(fl)

	for ln_v in _upkeep_lines:
		var ul := Label.new()
		ul.text = String(ln_v)
		ul.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		ul.add_theme_font_size_override("font_size", 13)
		ul.add_theme_color_override("font_color", C_GOLD)
		v.add_child(ul)
	_upkeep_lines = []

	v.add_child(_rule())
	v.add_child(_status_strip())
	v.add_child(_rule())

	# ── this week's opportunity, if the calendar holds one ──
	var ev: Dictionary = _event_for(month, week)
	if not ev.is_empty():
		var eb := Button.new()
		eb.text = "  ★  %s   %s" % [String(ev.get("label", "")), _cost_tag(int(ev.get("energy", 2)), wx, ev)]
		eb.add_theme_font_size_override("font_size", 15)
		eb.add_theme_color_override("font_color", C_GOLD)
		eb.alignment = HORIZONTAL_ALIGNMENT_LEFT
		eb.tooltip_text = String(ev.get("blurb", "")) + "\n\n(This week only. It will not come again.)"
		eb.pressed.connect(_on_activity.bind(ev, true))
		v.add_child(eb)
		var ebl := Label.new()
		ebl.text = "      " + String(ev.get("blurb", "")) + "  · this week only ·"
		ebl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		ebl.add_theme_font_size_override("font_size", 12)
		ebl.add_theme_color_override("font_color", C_DIM)
		v.add_child(ebl)

	# ── errands · WAVE D · what bonds unlock ─────────────────────
	# One-shot, season-windowed jobs that only exist because somebody
	# trusts you now. At most two offered per week (soonest-closing
	# window first) so the menu stays a menu, not a job board.
	var offered: Array = _errands_for(month)
	for err_v in offered:
		var err: Dictionary = err_v
		var b := Button.new()
		var blocked: String = _blocked_reason(err, wx)
		b.text = "  ✚  %s   %s%s" % [String(err.get("label", "")),
			_cost_tag(int(err.get("energy", 2)), wx, err), _effect_hint(err)]
		b.add_theme_font_size_override("font_size", 14)
		b.add_theme_color_override("font_color", C_SEA_TXT)
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		var wm: Array = err.get("months", [])
		var closing: bool = wm.is_empty() or int(wm[wm.size() - 1]) == month
		b.tooltip_text = String(err.get("blurb", "")) + \
			("\n\n(This is the last month for it.)" if closing else "")
		if blocked != "":
			b.disabled = true
			b.text += "   — " + blocked
		else:
			b.pressed.connect(_on_activity.bind(err, false))
		v.add_child(b)
		var bl := Label.new()
		bl.text = "      " + String(err.get("blurb", "")) + \
			("  · the window is closing ·" if closing else "")
		bl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		bl.add_theme_font_size_override("font_size", 12)
		bl.add_theme_color_override("font_color", C_DIM)
		v.add_child(bl)

	var town_btn := Button.new()
	town_btn.text = "  ·  WALK INTO TOWN  ·  "
	town_btn.add_theme_font_size_override("font_size", 15)
	town_btn.add_theme_color_override("font_color", C_RUST_TXT)
	town_btn.pressed.connect(_open_town)
	v.add_child(town_btn)

	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	v.add_child(scroll)
	var list := VBoxContainer.new()
	list.add_theme_constant_override("separation", 5)
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(list)

	for act_v in _acts:
		var act: Dictionary = act_v
		if not _eligible(act, month):
			continue
		var b := Button.new()
		var blocked: String = _blocked_reason(act, wx)
		b.text = "  %s %s%s" % [String(act.get("label", "?")), _cost_tag(int(act.get("energy", 2)), wx, act), _effect_hint(act)]
		b.add_theme_font_size_override("font_size", 14)
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		if blocked != "":
			b.disabled = true
			b.text += "   — " + blocked
		else:
			b.pressed.connect(_on_activity.bind(act, false))
		list.add_child(b)

	# rest is always a real option — it costs the week and pays the body
	var rest := Button.new()
	rest.text = "  Keep to the house — rest, and give Vovo a hand   (+%d energy)" % REST_ENERGY
	rest.add_theme_font_size_override("font_size", 14)
	rest.alignment = HORIZONTAL_ALIGNMENT_LEFT
	rest.pressed.connect(_on_rest)
	list.add_child(rest)

	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 12)
	v.add_child(row)
	var store := Button.new()
	store.text = "  · the general store ·  "
	store.add_theme_font_size_override("font_size", 12)
	store.add_theme_color_override("font_color", C_SEA_TXT)
	store.pressed.connect(_show_store)
	row.add_child(store)
	var book := Button.new()
	book.text = "  · the book of the coast ·  "
	book.add_theme_font_size_override("font_size", 12)
	book.add_theme_color_override("font_color", C_GOLD)
	book.pressed.connect(_show_book)
	row.add_child(book)
	var back := Button.new()
	back.text = "  · put it down (save & quit) ·  "
	back.add_theme_font_size_override("font_size", 12)
	back.pressed.connect(func() -> void: quit.emit())
	row.add_child(back)

	GamepadMgr.focus_first.call_deferred(scroll)


func _forecast_line(month: int, week: int) -> String:
	var nm: int = month
	var nw: int = week + 1
	if nw > WEEKS_PER_MONTH:
		nm += 1
		nw = 1
	if nm >= MONTHS.size() or nm == 6:
		return ""
	var wx: String = _weather_for(nm, nw)
	match wx:
		"storm": return "Del taps the glass and frowns — it is dropping hard. Next week the bar will be breaking."
		"minus": return "The tide book says next week the sea pulls back farther than it has all season."
		"rain":  return "The glass says more rain coming."
		_:       return "The glass holds steady — fair week coming."


func _errands_for(month: int) -> Array:
	# Eligible = bond earned + inside the window + not yet done.
	# Sorted so the soonest-to-vanish errand is offered first.
	var done: Array = _s.get("errands_done", [])
	var out: Array = []
	for err_v in _errands:
		var err: Dictionary = err_v
		if done.has(String(err.get("id", ""))):
			continue
		if not _eligible(err, month):
			continue
		out.append(err)
	out.sort_custom(func(a, b) -> bool:
		var am: Array = (a as Dictionary).get("months", [])
		var bm: Array = (b as Dictionary).get("months", [])
		var ae: int = int(am[am.size() - 1]) if not am.is_empty() else 99
		var be: int = int(bm[bm.size() - 1]) if not bm.is_empty() else 99
		return ae < be)
	return out.slice(0, 2)


func _event_for(month: int, week: int) -> Dictionary:
	var taken: Array = _s.get("events_taken", [])
	for ev_v in _events:
		var ev: Dictionary = ev_v
		if int(ev.get("month", -1)) == month and int(ev.get("week", -1)) == week \
				and not taken.has(String(ev.get("id", ""))):
			return ev
	return {}


# ─── eligibility + weather gating (with visible reasons) ─────────

func _eligible(act: Dictionary, month: int) -> bool:
	if act.has("months"):
		# JSON numbers parse as FLOATS and Array.has(int) compares
		# typed — [0.0, 1.0].has(1) is false. This silently hid every
		# month-gated activity (clamming, the fall cannery line, berry
		# picking, row the bay, storm watch) from the menu since v2
		# shipped; the errand system's sim exposed it. Compare as ints.
		var ms: Array = act["months"]
		var in_window: bool = false
		for m_v in ms:
			if int(m_v) == month:
				in_window = true
				break
		if not in_window:
			return false
	if act.has("require") and not _req_met(act["require"]):
		return false
	if act.has("require_any"):
		var ok: bool = false
		for r_v in act["require_any"]:
			if _req_met(r_v):
				ok = true
				break
		if not ok:
			return false
	return true


func _blocked_reason(act: Dictionary, wx: String) -> String:
	if bool(act.get("bay", false)) and wx == "storm":
		return "the bar is breaking"
	return ""


func _req_met(req: Dictionary) -> bool:
	if req.has("apt") and _apt(String(req["apt"])) < int(req.get("min", 0)):
		return false
	if req.has("bond") and _bond(String(req["bond"])) < int(req.get("min", 0)):
		return false
	if req.has("money") and int(_s.get("money", 0)) < int(req.get("min", 0)):
		return false
	return true


func _energy_cost(act: Dictionary, wx: String) -> int:
	var cost: int = int(act.get("energy", 2))
	if bool(act.get("outdoor", false)) and (wx == "rain" or wx == "storm") \
			and not _has_gear("rain_slicker"):
		cost += 1
	return cost


func _cost_tag(base: int, wx: String, act: Dictionary) -> String:
	return "[%d en]" % _energy_cost(act, wx) if act.has("energy") else "[%d en]" % base


func _effect_hint(act: Dictionary) -> String:
	var parts: PackedStringArray = PackedStringArray()
	var apts_d: Dictionary = act.get("apts", {})
	for k in apts_d.keys():
		parts.append("+%d %s" % [int(apts_d[k]), String(k)])
	if act.has("bond"):
		parts.append("+ " + _npc_name(String(act["bond"])))
	if int(act.get("money", 0)) > 0:
		parts.append("+$%d" % int(act["money"]))
	if act.has("journal"):
		parts.append("book")
	if bool(act.get("song", false)):
		parts.append("a song")
	if parts.is_empty():
		return ""
	return "   (" + ", ".join(parts) + ")"


func _has_gear(id: String) -> bool:
	return (_s.get("gear", []) as Array).has(id)


# ─── resolve a week ──────────────────────────────────────────────

func _on_activity(act: Dictionary, is_event: bool) -> void:
	_sfx(String(ACT_SFX.get(String(act.get("id", "")), "tile_enter")))
	var month: int = int(_s.get("month", 0))
	var week: int = int(_s.get("week", 1))
	var wx: String = _weather_for(month, week)
	var lines: Array = []

	# ── energy ──
	var cost: int = _energy_cost(act, wx)
	var energy: int = int(_s.get("energy", 8))
	var worn: bool = energy < cost
	_s["energy"] = maxi(0, energy - cost)
	if worn:
		lines.append("· you went into the week already worn thin, and the week knew it. (−2 on the work)")

	# ── the check: aptitude vs the work, roll shown ──
	var tier: int = 1        # 0 rough · 1 fair · 2 strong
	var breakdown: String = ""
	var check: Dictionary = act.get("check", act.get("check_stakes", {}))
	if not check.is_empty():
		var apt_name := String(check.get("apt", "grit"))
		var diff: int = int(check.get("diff", 2))
		var luck: int = _luck_for(month, week)
		var mod: int = 0
		var mod_bits: PackedStringArray = PackedStringArray()
		if bool(act.get("outdoor", false)) and wx == "clear":
			mod += 1; mod_bits.append("+1 fair sky")
		if String(act.get("id", "")) == "clamming" and wx == "minus":
			mod += 2; mod_bits.append("+2 minus tide")
		if String(act.get("id", "")) == "storm_watch" and wx == "storm":
			mod += 2; mod_bits.append("+2 the real thing")
		if String(act.get("id", "")) == "clamming" and _has_gear("clam_gun"):
			mod += 2; mod_bits.append("+2 clam gun")
		if bool(act.get("outdoor", false)) and _has_gear("field_glasses"):
			mod += 1; mod_bits.append("+1 field glasses")
		if worn:
			mod -= 2
		var score: int = _apt(apt_name) + luck + mod - diff
		tier = 2 if score >= 3 else (1 if score >= 1 else 0)
		var tier_word: String = ["a rough week", "a fair week", "a strong week"][tier]
		breakdown = "%s %d + luck %d %s vs. the work %d — %s" % [
			apt_name, _apt(apt_name), luck,
			(" ".join(mod_bits) if not mod_bits.is_empty() else ""), diff, tier_word]

	# ── stakes events branch on the check ──
	var outcome: String = _pick_outcome(act, tier)
	var apply_full: bool = true
	if act.has("check_stakes") and tier == 0:
		outcome = String(act.get("fail_outcome", outcome))
		apply_full = false

	# ── rewards, scaled by tier ──
	var apts_d: Dictionary = act.get("apts", {})
	var apts: Dictionary = _s["apts"]
	for k in apts_d.keys():
		var amt: int = int(apts_d[k])
		if tier == 0:
			amt = maxi(1, amt - 1) if apply_full else 1
		elif tier == 2:
			amt += 0
		apts[String(k)] = int(apts.get(String(k), 0)) + amt
	if tier == 2 and not check.is_empty():
		var bonus_apt := String(check.get("apt", "grit"))
		apts[bonus_apt] = int(apts.get(bonus_apt, 0)) + 1
		lines.append("· the strong week leaves something behind: +1 %s" % bonus_apt)

	var pay: int = int(act.get("money", 0))
	if pay != 0:
		if tier == 0:
			pay = int(floor(pay / 2.0))
		elif tier == 2 and pay > 0:
			pay += 2
			lines.append("· good work is worth more: +$2 on top")
		_s["money"] = int(_s.get("money", 0)) + pay

	if apply_full:
		if act.has("bond"):
			lines.append_array(_raise_bond(String(act["bond"]), int(act.get("bond_amt", 1))))
		if act.has("bond2"):
			lines.append_array(_raise_bond(String(act["bond2"]), int(act.get("bond2_amt", 1))))
		if bool(act.get("song", false)):
			var n: int = 2 if _has_gear("guitar_strings") else 1
			_s["songs"] = int(_s.get("songs", 0)) + n
		if act.has("clue"):
			lines.append_array(_grant_clue(String(act["clue"])))
		if act.has("flag"):
			_s[String(act["flag"])] = true
		if act.has("journal") and tier >= 1:
			var j: Array = _s["journal"]
			var entry: String = String(act["journal"])
			if not j.has(entry):
				j.append(entry)
				lines.append("· your book of the coast: \"%s\"" % entry)
				_sfx("page_turn")
	else:
		# went out and came back with less: the sea still teaches
		lines.append_array(_raise_bond(String(act.get("bond", "del")), 1))
		apts["grit"] = int(apts.get("grit", 0)) + 1
		lines.append("· +1 grit. Some lessons only the rough weeks give.")

	if is_event:
		var taken: Array = _s.get("events_taken", [])
		taken.append(String(act.get("id", "")))
		_s["events_taken"] = taken
	if bool(act.get("errand", false)):
		var done_e: Array = _s.get("errands_done", [])
		done_e.append(String(act.get("id", "")))
		_s["errands_done"] = done_e

	if breakdown != "":
		lines.push_front("· " + breakdown)
	_advance_after(outcome, lines)


# FLAVOR · which line the week actually says.
#
# Reported 2026-07-31: "salmonberry is lifeless. add flavor text for
# every week, and every choice." Measured cause: every activity had
# ONE outcome string, reused across all 40 weeks. The data now
# carries variants and this picks between them:
#
#   outcome            · the base line (always present · fallback)
#   outcome_by_season  · {"summer": "...", "autumn": ...} overrides
#                        the base for that season
#   outcome_rough      · replaces on a rough week (tier 0)
#   outcome_strong     · replaces on a strong week (tier 2)
#   outcome_alt        · [..] extra variants rotated by visit count,
#                        so the third net-haul doesn't read like the
#                        first even inside one season
#
# Priority: tier line > season line > alt rotation > base. Tier wins
# because the tier is the news; season is scenery.
func _pick_outcome(act: Dictionary, tier: int) -> String:
	var base: String = String(act.get("outcome", ""))
	if tier == 0 and act.has("outcome_rough"):
		return String(act["outcome_rough"])
	if tier == 2 and act.has("outcome_strong"):
		return String(act["outcome_strong"])
	var month: int = int(_s.get("month", 0))
	var season: String = SEASON_OF[month]
	var by_season: Dictionary = act.get("outcome_by_season", {})
	if by_season.has(season):
		return String(by_season[season])
	var alts: Array = act.get("outcome_alt", [])
	if not alts.is_empty():
		# visit count per activity id · persists in the run state
		var visits: Dictionary = _s.get("act_visits", {})
		var aid: String = String(act.get("id", ""))
		var n: int = int(visits.get(aid, 0))
		visits[aid] = n + 1
		_s["act_visits"] = visits
		if n > 0:   # first visit keeps the authored base line
			return String(alts[(n - 1) % alts.size()])
	return base


func _on_rest() -> void:
	_sfx("season_settle")
	_s["energy"] = mini(ENERGY_MAX, int(_s.get("energy", 8)) + REST_ENERGY)
	var lines: Array = _raise_bond("gran", 1)
	_advance_after("You sleep past the foghorn. You split kindling, you dry dishes, you sit on the porch while Vovo names the boats coming in. The week is quiet and it gives you your body back.", lines)


# ─── bonds + the thread (unchanged machinery, now touch-tracked) ──

func _raise_bond(id: String, amt: int) -> Array:
	var bonds: Dictionary = _s["bonds"]
	var before: int = int(bonds.get(id, 0))
	var after: int = before + amt
	bonds[id] = after
	var touch: Dictionary = _s["bond_touch"]
	touch[id] = int(_s.get("month", 0)) * WEEKS_PER_MONTH + int(_s.get("week", 1))
	var out: Array = []
	var npc: Dictionary = _npcs.get(id, {})
	for i in range(3):
		var thresh: int = 2 + i * 2
		if before < thresh and after >= thresh:
			var bl: Array = npc.get("bond_lines", [])
			if i < bl.size():
				out.append("%s — %s" % [_npc_name(id), String(bl[i])])
	for c_v in npc.get("clues", []):
		var c: Dictionary = c_v
		var at: int = int(c.get("at", 99))
		if before < at and after >= at:
			out.append_array(_grant_clue(String(c.get("id", ""))))
	return out


const CLUE_TEXT := {
	"estelle_grave": "the boat · a grave behind the church, flowers fresh against the rain, nineteen years on this month. Somebody still comes.",
	"estelle_light": "the boat · Estelle keeps a light in the window that faces the bar. Someone she loved went out on it, and did not come back.",
	"del_saw": "the boat · Del told you what he saw the morning it did not come in. He has never told anyone else.",
	"iris_record": "the boat · the county register has the crew, and a date, and after the date nothing at all.",
	"estelle_name": "the boat · Estelle said his name to you. Once. You are the only one she has told.",
}


func _grant_clue(id: String) -> Array:
	if id == "":
		return []
	var clues: Array = _s.get("thread_clues", [])
	if clues.has(id):
		return []
	clues.append(id)
	_s["thread_clues"] = clues
	_sfx("page_turn")
	return ["· " + String(CLUE_TEXT.get(id, "you learn something the town does not say."))]


func _thread_depth() -> int:
	return (_s.get("thread_clues", []) as Array).size()


# ─── week's end ──────────────────────────────────────────────────

func _advance_after(outcome: String, extra: Array) -> void:
	_clear_ui()
	_paint_backdrop()
	var v := _panel()
	var month: int = int(_s.get("month", 0))
	var week: int = int(_s.get("week", 1))
	var h := Label.new()
	h.text = "%s %d · week %d" % [MONTHS[month], (1963 if month <= 3 else 1964), week]
	h.add_theme_font_size_override("font_size", 20)
	h.add_theme_color_override("font_color", C_FIR)
	v.add_child(h)

	var o := Label.new()
	o.text = outcome
	o.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	o.add_theme_font_size_override("font_size", 16)
	o.add_theme_color_override("font_color", C_INK)
	v.add_child(o)

	for ln_v in extra:
		var ln := Label.new()
		ln.text = String(ln_v)
		ln.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		ln.add_theme_font_size_override("font_size", 14)
		ln.add_theme_color_override("font_color", C_GOLD)
		v.add_child(ln)

	v.add_child(_rule())
	v.add_child(_status_strip())

	# advance the week (persist), sleep restores a little
	week += 1
	if week > WEEKS_PER_MONTH:
		week = 1
		_s["month"] = month + 1
	_s["week"] = week
	var regen: int = ENERGY_WEEKLY + (1 if _has_gear("bicycle") else 0)
	_s["energy"] = mini(ENERGY_MAX, int(_s.get("energy", 8)) + regen)
	month_complete.emit(_s)
	_sfx("season_settle")

	var done: bool = int(_s["month"]) >= MONTHS.size()
	var cont := Button.new()
	cont.text = "  the week passes  →  " if not done else "  the year ends  →  "
	cont.add_theme_font_size_override("font_size", 15)
	cont.pressed.connect(_render)
	v.add_child(cont)
	GamepadMgr.focus_first.call_deferred(v)


# ─── the general store ───────────────────────────────────────────

func _show_store() -> void:
	_sfx("door_open")
	_clear_ui()
	_paint_backdrop()
	var v := _panel()
	var hdr := Label.new()
	hdr.text = "The General Store"
	hdr.add_theme_font_size_override("font_size", 24)
	hdr.add_theme_color_override("font_color", C_RUST_TXT)
	v.add_child(hdr)
	var sub := Label.new()
	sub.text = "Wanting a thing is free. You have $%d." % int(_s.get("money", 0))
	sub.add_theme_font_size_override("font_size", 13)
	sub.add_theme_color_override("font_color", C_DIM)
	v.add_child(sub)
	v.add_child(_rule())
	for g_v in GEAR:
		var g: Dictionary = g_v
		var gid := String(g["id"])
		var b := Button.new()
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.add_theme_font_size_override("font_size", 14)
		if _has_gear(gid):
			b.text = "  ✓ %s — yours" % String(g["label"])
			b.disabled = true
		else:
			var cost: int = int(g["cost"])
			b.text = "  %s — $%d   (%s)" % [String(g["label"]), cost, String(g["hint"])]
			if int(_s.get("money", 0)) < cost:
				b.disabled = true
			else:
				b.pressed.connect(func() -> void:
					_s["money"] = int(_s.get("money", 0)) - cost
					(_s["gear"] as Array).append(gid)
					_sfx("customer_bell")
					_show_store())
		v.add_child(b)
	var note := Label.new()
	note.text = "(Buying does not spend the week — the store is on the way to everything.)"
	note.add_theme_font_size_override("font_size", 12)
	note.add_theme_color_override("font_color", C_DIM)
	v.add_child(note)
	var back := Button.new()
	back.text = "  · back out into the weather ·  "
	back.add_theme_font_size_override("font_size", 14)
	back.pressed.connect(_render)
	v.add_child(back)
	GamepadMgr.focus_first.call_deferred(v)


# ── the walkable town · unchanged contract with SalmonberryTown ──

const TOWN_SCRIPT := preload("res://scenes/games/salmonberry/SalmonberryTown.gd")
var _town: Control = null


func _open_town() -> void:
	_clear_ui()
	var month: int = int(_s.get("month", 0))
	var wx: String = _weather_for(month, int(_s.get("week", 1)))
	var by_loc: Dictionary = {}
	for act_v in _acts:
		var act: Dictionary = act_v
		if not _eligible(act, month):
			continue
		if _blocked_reason(act, wx) != "":
			continue
		var loc := String(act.get("loc", ""))
		if loc == "":
			continue
		var arr: Array = by_loc.get(loc, [])
		arr.append(act)
		by_loc[loc] = arr
	_town = TOWN_SCRIPT.new()
	add_child(_town)
	_town.connect("activity_chosen", func(act: Dictionary) -> void:
		if _town != null and is_instance_valid(_town):
			_town.queue_free()
		_town = null
		_on_activity(act, false))
	_town.connect("quit", func() -> void:
		if _town != null and is_instance_valid(_town):
			_town.queue_free()
		_town = null
		_render())
	# Route-only finds (town_life.json moments) pay WITHOUT spending
	# the week — the walk itself is the price. Applied here so the
	# rewards live in the run state like any other.
	_town.connect("town_moment", func(m: Dictionary) -> void:
		var taken: Array = _s.get("town_moments", [])
		var mid := String(m.get("id", ""))
		if taken.has(mid):
			return
		taken.append(mid)
		_s["town_moments"] = taken
		var gives: Dictionary = m.get("gives", {})
		if gives.has("journal"):
			var j: Array = _s["journal"]
			var entry := String(gives["journal"])
			if not j.has(entry):
				j.append(entry)
		if gives.has("clue"):
			_grant_clue(String(gives["clue"]))
		if gives.has("bond"):
			_raise_bond(String(gives["bond"]), int(gives.get("bond_amt", 1))))
	_town.call("boot", month, by_loc, _s.get("bonds", {}), {
		"wx": wx,
		"moments_taken": _s.get("town_moments", []),
		"seed": int(_s.get("seed", 0)),
	})


# ── the book of the coast · the collectible, read back ──

func _show_book() -> void:
	_sfx("page_turn")
	_clear_ui()
	_paint_backdrop()
	var v := _panel()
	var hdr := Label.new()
	hdr.text = "The Book of the Coast"
	hdr.add_theme_font_size_override("font_size", 24)
	hdr.add_theme_color_override("font_color", C_RUST_TXT)
	v.add_child(hdr)

	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	v.add_child(scroll)
	var list := VBoxContainer.new()
	list.add_theme_constant_override("separation", 8)
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(list)

	var journal: Array = _s.get("journal", [])
	var jh := Label.new()
	jh.text = "· what you noticed (%d of %d) ·" % [journal.size(), _journal_total]
	jh.add_theme_font_size_override("font_size", 14)
	jh.add_theme_color_override("font_color", C_GOLD)
	list.add_child(jh)
	if journal.is_empty():
		list.add_child(_book_line("The pages are still blank. Go and look at something.", C_FIR))
	for e in journal:
		list.add_child(_book_line("— " + String(e), C_INK))

	var clues: Array = _s.get("thread_clues", [])
	if not clues.is_empty():
		var ch := Label.new()
		ch.text = "· what you know ·"
		ch.add_theme_font_size_override("font_size", 14)
		ch.add_theme_color_override("font_color", C_GOLD)
		list.add_child(ch)
		for cid in clues:
			list.add_child(_book_line("— " + String(CLUE_TEXT.get(String(cid), "")), C_INK))

	var gear: Array = _s.get("gear", [])
	if not gear.is_empty():
		var gh := Label.new()
		gh.text = "· what you carry ·"
		gh.add_theme_font_size_override("font_size", 14)
		gh.add_theme_color_override("font_color", C_GOLD)
		list.add_child(gh)
		for gid_v in gear:
			for g_v in GEAR:
				var g: Dictionary = g_v
				if String(g["id"]) == String(gid_v):
					list.add_child(_book_line("— " + String(g["label"]), C_INK))

	var back := Button.new()
	back.text = "  · close the book ·  "
	back.add_theme_font_size_override("font_size", 14)
	back.pressed.connect(_render)
	v.add_child(back)
	GamepadMgr.focus_first.call_deferred(scroll)


func _book_line(text: String, col: Color) -> Label:
	var l := Label.new()
	l.text = text
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.add_theme_font_size_override("font_size", 14)
	l.add_theme_color_override("font_color", col)
	return l


# ─── March · the water comes ─────────────────────────────────────

func _render_wave() -> void:
	_sfx("harbor_bell")
	var v := _panel()
	var hdr := Label.new()
	hdr.text = "March 1964 · Good Friday"
	hdr.add_theme_font_size_override("font_size", 26)
	hdr.add_theme_color_override("font_color", C_RUST_TXT)
	v.add_child(hdr)

	var body := Label.new()
	body.text = "At dinner the ground moves — a long slow roll, not a jolt — and does not stop. Del is out the door before it ends, yelling to bring the boats in. Then the harbormaster's bell, and the word goes house to house faster than the phone: the water has gone out. Too far out. It is coming back."
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.add_theme_font_size_override("font_size", 15)
	body.add_theme_color_override("font_color", C_INK)
	v.add_child(body)

	v.add_child(_rule())
	var prompt := Label.new()
	prompt.text = "You have a few minutes, and legs. What you built this year is who you can reach."
	prompt.add_theme_font_size_override("font_size", 14)
	prompt.add_theme_color_override("font_color", C_GOLD)
	v.add_child(prompt)

	var run_btn := Button.new()
	run_btn.text = "  ·  RUN  ·  "
	run_btn.add_theme_font_size_override("font_size", 18)
	run_btn.add_theme_color_override("font_color", C_RUST_TXT)
	run_btn.pressed.connect(_open_crisis)
	v.add_child(run_btn)
	GamepadMgr.focus_first.call_deferred(v)


# ── WAVE C · the night, played ───────────────────────────────────
# The walkable town runs the crisis (timer, rising water, rescues
# gated on the year's build); the results come back here and write
# through the SAME reward paths the old choice menu used.
func _open_crisis() -> void:
	_clear_ui()
	_town = TOWN_SCRIPT.new()
	add_child(_town)
	_town.connect("crisis_over", func(results: Dictionary) -> void:
		if _town != null and is_instance_valid(_town):
			_town.queue_free()
		_town = null
		_resolve_crisis(results))
	_town.call("boot_crisis", _s)


func _resolve_crisis(results: Dictionary) -> void:
	var saved: Array = results.get("saved", [])
	var told: bool = bool(results.get("told_estelle", false))
	var forced: bool = bool(results.get("forced", false))
	var apts: Dictionary = _s["apts"]
	var lines: Array = []
	var parts := PackedStringArray()

	if saved.has("dock"):
		lines.append_array(_raise_bond("del", 2))
		apts["sea"] = int(apts.get("sea", 0)) + 2
		_s["helped_wave"] = true
		parts.append("You got lines cast off with Del and the fleet stood off the bar in deep water, and it rides the surge instead of splintering on the pilings. Half the town's living, saved.")
	if saved.has("cannery"):
		lines.append_array(_raise_bond("manny", 2))
		apts["sea"] = int(apts.get("sea", 0)) + 2
		_s["helped_wave"] = true
		parts.append("The skiff again, like the night off the bar — the cannery's night crew off the finger pier, and a dog nobody owns off a swamped float.")
	if saved.has("estelle"):
		if told:
			lines.append_array(_raise_bond("estelle", 3))
			apts["heart"] = int(apts.get("heart", 0)) + 2
			_s["told_estelle"] = true
			parts.append("You were already running to the gray house before the bell finished, because you knew. She lets you take her up the hill, and she does not look back at the water — she looks at you.")
		else:
			lines.append_array(_raise_bond("estelle", 2))
			apts["heart"] = int(apts.get("heart", 0)) + 2
			parts.append("Estelle would not leave the window that faces the bar, and then, for you, she did.")
		_s["helped_wave"] = true

	# Vovo, always — the night ends on the hill either way
	lines.append_array(_raise_bond("gran", 1))
	apts["grit"] = int(apts.get("grit", 0)) + 1

	if parts.is_empty():
		parts.append("You take Vovo's arm and you climb, and you watch from the top as the river walks up into the town and back out again, taking pieces. You are safe. That is also a choice, and not a small one.")
	elif forced:
		parts.append("The water reached the porch before you meant it to. You take Vovo up the hill at a run, her hand weighing nothing, the town going dark below by streets.")
	else:
		parts.append("Then Vovo, and the hill, and the watching — the river walking up into the town and back out, taking pieces, but fewer than it wanted.")

	var outcome := "  ".join(parts)
	if not lines.is_empty():
		var extra := PackedStringArray()
		for ln_v in lines:
			extra.append(String(ln_v))
		outcome += "\n\n" + "\n".join(extra)
	_advance_wave(outcome)


# The wave night skips the week machinery — one night, one month.
func _advance_wave(outcome: String) -> void:
	_clear_ui()
	_paint_backdrop()
	var v := _panel()
	var o := Label.new()
	o.text = outcome
	o.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	o.add_theme_font_size_override("font_size", 16)
	o.add_theme_color_override("font_color", C_INK)
	v.add_child(o)
	v.add_child(_rule())
	v.add_child(_status_strip())
	_s["month"] = int(_s.get("month", 0)) + 1
	_s["week"] = 1
	_s["energy"] = 6   # nobody sleeps much that week
	month_complete.emit(_s)
	_sfx("season_settle")
	var cont := Button.new()
	cont.text = "  the water goes back  →  "
	cont.add_theme_font_size_override("font_size", 15)
	cont.pressed.connect(_render)
	v.add_child(cont)
	GamepadMgr.focus_first.call_deferred(v)


# ─── the year ends ───────────────────────────────────────────────

func _end_year() -> void:
	var register: String = _resolve_register()
	var coda: String = ""
	if bool(_s.get("helped_wave", false)):
		coda = "And the town remembers you were there the night the water came."
	else:
		coda = "The water came and went, and you were up the hill with Vovo, safe. That is a kind of choice too."
	if bool(_s.get("helped_boat", false)):
		coda += " The men of the Ida Rose still buy your coffee at Ruth's, and will for as long as any of them draws breath."
	var depth: int = _thread_depth()
	if bool(_s.get("told_estelle", false)):
		coda += " You got to Estelle before the water did. Whatever the boat took from her, she did not have to face this one alone."
	elif depth >= 3:
		coda += " You know the whole of it now — the boat, the crew, the morning Del cannot forget. The town's quietest grief has one more keeper."
	elif depth >= 1:
		coda += " You know a little of what the town will not say aloud about the boat that did not come back."
	if int(_s.get("strain", 0)) >= 3:
		coda += " The flour tin was empty more months than it was not, and that is in the ledger of the year too."
	year_over.emit({"state": _s, "register": register, "coda": coda})


func _resolve_register() -> String:
	var a: Dictionary = _s["apts"]
	var gran: int = _bond("gran")
	var songs: int = int(_s.get("songs", 0))
	var journal_n: int = (_s["journal"] as Array).size()
	var deep: int = 0
	var town: int = 0
	for id in (_s["bonds"] as Dictionary).keys():
		if String(id) == "gran":
			continue
		var lvl: int = int((_s["bonds"] as Dictionary)[id])
		if lvl >= 2:
			deep += 1
		if lvl >= 4:
			town += 1
	var heart_word: int = int(a.get("heart", 0)) + int(a.get("word", 0))
	var body_sum: int = int(a.get("hands", 0)) + int(a.get("sea", 0)) + int(a.get("grit", 0))
	if gran >= 6 and songs >= 3:
		return "song"
	if journal_n >= 9:
		return "keeper"
	if heart_word >= 10 and deep >= 3:
		return "listener"
	if body_sum >= 12 and town >= 2:
		return "hands"
	return "leaver"


# ─── helpers ─────────────────────────────────────────────────────

func _apt(name: String) -> int:
	return int((_s["apts"] as Dictionary).get(name, 0))


func _bond(id: String) -> int:
	return int((_s["bonds"] as Dictionary).get(id, 0))


func _npc_name(id: String) -> String:
	var npc: Dictionary = _npcs.get(id, {})
	return String(npc.get("name", id.capitalize()))


func _rule() -> ColorRect:
	var r := ColorRect.new()
	r.color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.35)
	r.custom_minimum_size = Vector2(0, 1)
	return r


func _status_strip() -> Label:
	var a: Dictionary = _s["apts"]
	var en: int = int(_s.get("energy", 8))
	var dots: String = ""
	for i in range(ENERGY_MAX):
		dots += "●" if i < en else "○"
	var l := Label.new()
	l.text = "hands %d · sea %d · word %d · heart %d · wild %d · grit %d      $%d · %s · book %d/%d" % [
		int(a.get("hands", 0)), int(a.get("sea", 0)), int(a.get("word", 0)),
		int(a.get("heart", 0)), int(a.get("wild", 0)), int(a.get("grit", 0)),
		int(_s.get("money", 0)), dots,
		(_s["journal"] as Array).size(), _journal_total]
	l.add_theme_font_size_override("font_size", 13)
	l.add_theme_color_override("font_color", C_FIR)
	return l


func _sfx(preset: String) -> void:
	var sb := get_node_or_null("/root/SFXBank")
	if sb != null and sb.has_method("play"):
		sb.play(preset)


# Which ambient one-shot an activity earns, by id. Reuses the shared bank.
const ACT_SFX := {
	"walk_the_beach": "gull_cry",
	"clamming": "water_slap",
	"storm_watch": "wave_break",
	"row_the_bay": "water_slap",
	"cannery_line": "cooler_whoosh",
	"berry_picking": "gull_cry",
	"cafe_dishes": "customer_bell",
	"store_errand": "door_open",
	"fall_run_first_day": "cooler_whoosh",
	"boat_off_the_bar": "wave_break",
	"lowest_tide": "water_slap",
	"grange_dance": "customer_bell",
}


func _input(event: InputEvent) -> void:
	# The town overlay owns input while open (its own ESC goes back to
	# the week menu, not the title).
	if _town != null and is_instance_valid(_town):
		return
	if event.is_action_pressed("ui_cancel"):
		quit.emit()
		get_viewport().set_input_as_handled()
