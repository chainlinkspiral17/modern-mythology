extends Control
## HANE NO NIWA · one visit to the shrine · 4 seasons × 9 visits.
##
## Composed vertically like a hanging scroll: a tall center panel
## with wide paper margins, and the margins are USED · season
## title, visit count, and the feather tally live there in
## vertical text.
##
## Verbs: SWEEP · MEND · OFFER · SIT.  Maintenance has visible
## memory (the steps stay swept a few visits; the rope frays back
## slowly).  The shrine keeps a quiet UPKEEP state it never shows
## as a number · the fox statues' expressions read differently at
## high upkeep, and players argue about whether that's real.
## (It is.)
##
## OFFER is the language.  The town at the hill's foot is one
## menu, not a location · you bring one thing per visit, or
## gather what the season leaves on the hill.

signal quit
signal visit_over(state: Dictionary)

const OFFERINGS_PATH := "res://resources/games/vol7/hane_no_niwa/offerings.json"

const SEASON_PAL := {
	"spring": ["f4ece0", "d88a98", "8aa878", "5a6a8a", "38302a"],
	"summer": ["ecf0e4", "4a8a58", "f0c848", "7a98b8", "38302a"],
	"autumn": ["f0e8d8", "c85830", "b89038", "6a5a48", "38302a"],
	"winter": ["f0f0ec", "b8c4d0", "d8dce0", "4a4a52", "38302a"],
}
const SEASONS := ["spring", "summer", "autumn", "winter"]
const SEASON_JP := {"spring": "春", "summer": "夏", "autumn": "秋", "winter": "冬"}

# Eight spots · panel coordinates (the panel is x 420..860)
const SPOTS := {
	"torii":         {"pos": Vector2(640, 620), "name": "the torii"},
	"steps":         {"pos": Vector2(640, 520), "name": "the steps (23)"},
	"cistern":       {"pos": Vector2(520, 420), "name": "the cistern"},
	"offering_shelf":{"pos": Vector2(640, 360), "name": "the offering shelf"},
	"honden_door":   {"pos": Vector2(640, 250), "name": "the honden door"},
	"camphor_tree":  {"pos": Vector2(790, 300), "name": "the camphor tree"},
	"fox_statues":   {"pos": Vector2(540, 300), "name": "the fox statues"},
	"brazier":       {"pos": Vector2(760, 450), "name": "the brazier"},
}
const ACTIONS_PER_VISIT := 4

var _state: Dictionary = {}
var _offerings: Array = []
var _season: String = "spring"
var _visit: int = 1              # 1..9 within the season
var _at: String = "torii"
var _actions_left: int = ACTIONS_PER_VISIT
var _pal: Array = []
var _visit_done: bool = false

var _margin_msg: Label = null
var _verb_row: HBoxContainer = null
var _satchel_lbl: Label = null
var _bring_overlay: Control = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	_load_data()
	_build_ui()


func boot(state: Dictionary) -> void:
	_state = state
	var total: int = int(_state.get("visit_total", 0))
	_season = SEASONS[clampi(total / 9, 0, 3)]
	_visit = (total % 9) + 1
	_pal = SEASON_PAL[_season]
	_at = "torii"
	_actions_left = ACTIONS_PER_VISIT
	_visit_done = false
	# decay · the steps stay swept a few visits · the rope frays slowly
	_state["swept"] = maxi(0, int(_state.get("swept", 0)) - 1)
	if _visit % 3 == 0:
		_state["mended"] = maxi(0, int(_state.get("mended", 5)) - 1)
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("request_scene_bgm"):
		am.request_scene_bgm("res://assets/audio/bgm/hnn/%s.wav" % _season)
	if _visit == 1 and _season == "summer":
		_msg("the cicadas are very loud. louder than they need to be. the hill does not apologize.")
	elif _visit == 1 and _season == "autumn":
		_msg("the cicadas are gone. you notice the exact shape of the quiet they leave.")
	else:
		_msg("you climb the twenty-three steps. the shrine is where you left it, minus what the weather took.")
	_show_bring_menu()
	queue_redraw()


func _load_data() -> void:
	var f := FileAccess.open(OFFERINGS_PATH, FileAccess.READ)
	if f == null: return
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		_offerings = (parsed as Dictionary).get("items", [])


func _build_ui() -> void:
	_margin_msg = Label.new()
	_margin_msg.position = Vector2(60, 560)
	_margin_msg.size = Vector2(330, 140)
	_margin_msg.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_margin_msg.add_theme_font_size_override("font_size", 14)
	add_child(_margin_msg)

	_verb_row = HBoxContainer.new()
	_verb_row.position = Vector2(430, 676)
	_verb_row.size = Vector2(440, 30)
	_verb_row.add_theme_constant_override("separation", 14)
	add_child(_verb_row)
	for verb in ["SWEEP", "MEND", "OFFER", "SIT", "GATHER", "LEAVE"]:
		var b := Button.new()
		b.text = verb
		b.flat = true
		b.add_theme_font_size_override("font_size", 14)
		b.pressed.connect(_do_verb.bind(verb))
		_verb_row.add_child(b)

	_satchel_lbl = Label.new()
	_satchel_lbl.position = Vector2(890, 560)
	_satchel_lbl.size = Vector2(340, 140)
	_satchel_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_satchel_lbl.add_theme_font_size_override("font_size", 13)
	add_child(_satchel_lbl)


# ─── The town · one menu, not a location ─────────────────────────

func _show_bring_menu() -> void:
	_bring_overlay = Panel.new()
	_bring_overlay.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_bring_overlay.offset_left = -300
	_bring_overlay.offset_right = 300
	_bring_overlay.offset_top = -240
	_bring_overlay.offset_bottom = 240
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color("#" + String(_pal[0]))
	sb.border_color = Color("#" + String(_pal[4]))
	sb.set_border_width_all(1)
	_bring_overlay.add_theme_stylebox_override("panel", sb)
	add_child(_bring_overlay)

	var col := VBoxContainer.new()
	col.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	col.offset_left = 20
	col.offset_right = -20
	col.offset_top = 14
	col.offset_bottom = -14
	col.add_theme_constant_override("separation", 6)
	_bring_overlay.add_child(col)

	var hdr := Label.new()
	hdr.text = "· the town at the hill's foot · bring one thing up, or nothing ·"
	hdr.add_theme_font_size_override("font_size", 13)
	hdr.add_theme_color_override("font_color", Color("#" + String(_pal[4])))
	col.add_child(hdr)

	for item_v in _offerings:
		var item: Dictionary = item_v
		if String(item.get("found", "")) != "town":
			continue
		var b := Button.new()
		b.text = String(item.get("name", ""))
		b.flat = true
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.add_theme_font_size_override("font_size", 13)
		b.pressed.connect(_bring.bind(String(item["id"])))
		col.add_child(b)

	var skip := Button.new()
	skip.text = "· bring nothing ·"
	skip.flat = true
	skip.add_theme_font_size_override("font_size", 13)
	skip.pressed.connect(_bring.bind(""))
	col.add_child(skip)


func _bring(item_id: String) -> void:
	if _bring_overlay != null and is_instance_valid(_bring_overlay):
		_bring_overlay.queue_free()
		_bring_overlay = null
	if item_id != "":
		var satchel: Array = _state.get("satchel", [])
		satchel.append(item_id)
		_state["satchel"] = satchel
	_refresh_satchel()


# ─── Verbs ───────────────────────────────────────────────────────

func _do_verb(verb: String) -> void:
	if _visit_done or (_bring_overlay != null and is_instance_valid(_bring_overlay)):
		return
	match verb:
		"LEAVE":
			_end_visit()
			return
		"SWEEP":
			if _actions_left <= 0: return _no_time()
			_actions_left -= 1
			_state["swept"] = mini(9, int(_state.get("swept", 0)) + 3)
			_sfx("broom_sweep", 0.5)
			_msg("you sweep the steps, all twenty-three. the broom knows them by now. the sweeping will hold a few visits.")
		"MEND":
			if _actions_left <= 0: return _no_time()
			_actions_left -= 1
			_state["mended"] = mini(9, int(_state.get("mended", 5)) + 4)
			_sfx("stick_scratch", 0.4)
			_msg("you re-twist the shimenawa where it frays and set the chipped fox's pebble back. small repairs. the shrine notices small.")
		"SIT":
			if _actions_left <= 0: return _no_time()
			_actions_left -= 1
			# The ninth sit · having sat at all eight spots across
			# the run, the shrine offers the seat it never names.
			var sat: Array = _state.get("sat_spots", [])
			if not sat.has(_at):
				sat.append(_at)
				_state["sat_spots"] = sat
			if sat.size() >= SPOTS.size() and not bool(_state.get("ninth_sit_done", false)):
				_state["ninth_sit_done"] = true
				_msg("you have sat everywhere there is to sit, and so the shrine offers the ninth seat: the top step, facing DOWN the hill, the way the foxes face. the town below. the season doing what it does to it. you understand, briefly, what the shrine is for. it is not for the shrine.")
				_sfx("kyrindi_bell", 0.3)
				OneironauticsTokens.add("hnn_ninth_sit")
			else:
				_msg(_sit_line())
		"OFFER":
			_offer_menu()
			return
		"GATHER":
			if _actions_left <= 0: return _no_time()
			var found := _gather_here()
			if found == "":
				_msg("nothing here the season wants to give, at this spot, today.")
			else:
				_actions_left -= 1
				var satchel: Array = _state.get("satchel", [])
				satchel.append(found)
				_state["satchel"] = satchel
				var item := _find_item(found)
				_sfx("pickup", 0.4)
				_msg("you pick up %s." % String(item.get("name", found)))
	_refresh_satchel()
	queue_redraw()


func _no_time() -> void:
	_msg("the light is going. one more look, then the steps.")


func _sit_line() -> String:
	var upkeep := (int(_state.get("swept", 0)) + int(_state.get("mended", 5))) / 2
	if _at == "fox_statues":
		if upkeep >= 6:
			return "you sit with the foxes. the chipped one's expression · you would swear it has changed. something around the mouth. approving. people argue about whether that's real."
		return "you sit with the foxes. the chipped one looks past you, down the steps, the way it has for years."
	if _at == "honden_door":
		return "you sit by the honden. the door does not open. the door has a way of not opening that feels like attention."
	if _at == "camphor_tree" and _season == "summer":
		return "you sit under the camphor. the cicadas are a wall. somewhere behind the wall, the hill is listening."
	return "you sit. the %s does what it does. the wind takes roll." % SPOTS[_at]["name"]


func _gather_here() -> String:
	var satchel: Array = _state.get("satchel", [])
	var lexicon: Array = _state.get("lexicon_items", [])
	for item_v in _offerings:
		var item: Dictionary = item_v
		var found := String(item.get("found", ""))
		if found == "town":
			continue
		var parts := found.split(" · ")
		if parts.size() == 2 and parts[0] == _at and parts[1] == _season:
			var iid := String(item["id"])
			if not satchel.has(iid) and not lexicon.has(iid):
				return iid
	return ""


func _offer_menu() -> void:
	if _at != "offering_shelf":
		_msg("offerings go on the shelf. that is what a shelf is.")
		return
	var satchel: Array = _state.get("satchel", [])
	if satchel.is_empty():
		_msg("your hands are empty. the shelf does not mind. the shelf has patience for both of you.")
		return
	if _actions_left <= 0:
		_no_time()
		return
	_actions_left -= 1
	var iid := String(satchel.pop_back())
	_state["satchel"] = satchel
	var item := _find_item(iid)
	var lexicon: Array = _state.get("lexicon", [])
	for tag in item.get("tags", []):
		if not lexicon.has(String(tag)):
			lexicon.append(String(tag))
	_state["lexicon"] = lexicon
	var li: Array = _state.get("lexicon_items", [])
	li.append(iid)
	_state["lexicon_items"] = li
	var so: Array = _state.get("season_offered", [])
	if not so.has(_season):
		so.append(_season)
	_state["season_offered"] = so
	_sfx("kyrindi_bell", 0.4)
	_msg("you set %s on the shelf, straighten it, step back. it is no longer yours. that is the whole ceremony." % String(item.get("name", iid)))
	_refresh_satchel()


func _find_item(iid: String) -> Dictionary:
	for item in _offerings:
		if String((item as Dictionary)["id"]) == iid:
			return item
	return {}


func _refresh_satchel() -> void:
	var satchel: Array = _state.get("satchel", [])
	var names: Array = []
	for iid in satchel:
		names.append(String(_find_item(String(iid)).get("name", iid)))
	_satchel_lbl.text = "in your hands · " + (" · ".join(names) if names.size() > 0 else "nothing")
	_satchel_lbl.add_theme_color_override("font_color", Color("#" + String(_pal[4])))
	_margin_msg.add_theme_color_override("font_color", Color("#" + String(_pal[4])))


func _msg(t: String) -> void:
	_margin_msg.text = t


func _end_visit() -> void:
	if _visit_done:
		return
	_visit_done = true
	_state["visit_total"] = int(_state.get("visit_total", 0)) + 1
	visit_over.emit(_state)


# ─── The scroll ──────────────────────────────────────────────────

func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed \
			and event.button_index == MOUSE_BUTTON_LEFT and not _visit_done:
		var pos: Vector2 = (event as InputEventMouseButton).position
		for sid in SPOTS.keys():
			if pos.distance_to(SPOTS[sid]["pos"]) < 46.0:
				_at = String(sid)
				_sfx("boot_plank", 0.15)
				_msg("you stand at %s." % SPOTS[sid]["name"])
				queue_redraw()
				return


func _vtext(text: String, x: float, y: float, size: int, col: Color) -> void:
	var font := get_theme_default_font()
	var cy := y
	for ch in text:
		draw_string(font, Vector2(x, cy), ch, HORIZONTAL_ALIGNMENT_CENTER, 24, size, col)
		cy += size + 4


func _draw() -> void:
	if _pal.is_empty():
		_pal = SEASON_PAL["spring"]
	var paper := Color("#" + String(_pal[0]))
	var a1 := Color("#" + String(_pal[1]))
	var a2 := Color("#" + String(_pal[2]))
	var a3 := Color("#" + String(_pal[3]))
	var ink := Color("#" + String(_pal[4]))

	# margins · paper
	draw_rect(Rect2(0, 0, 1280, 720), paper)
	# the tall center panel
	draw_rect(Rect2(420, 20, 440, 640), Color(paper.r * 0.97, paper.g * 0.97, paper.b * 0.95))
	draw_rect(Rect2(420, 20, 440, 640), ink, false, 1.5)

	# margin verticals · season · visit · feathers
	_vtext(_season.to_upper(), 120, 60, 20, ink)
	_vtext("VISIT %d OF 9" % _visit, 200, 60, 14, a3)
	var feathers: int = int(_state.get("feathers", 0))
	_vtext("FEATHERS " + "·".repeat(maxi(feathers, 0)) + str(feathers), 1120, 60, 14, a3)
	_vtext("ACTIONS %d" % _actions_left, 1040, 60, 14, a3)

	# ── the shrine, in the panel, top to bottom ──
	var ng: bool = bool(_state.get("ng_plus", false))
	# honden
	draw_line(Vector2(560, 210), Vector2(640, 180), ink, 2.0)
	draw_line(Vector2(640, 180), Vector2(720, 210), ink, 2.0)
	draw_rect(Rect2(566, 210, 148, 80), ink, false, 2.0)
	# the door · never opens · (NG+: open exactly one pixel wider)
	var door_gap := 2.0 if ng else 1.0
	draw_rect(Rect2(640 - door_gap * 0.5, 218, door_gap, 64), ink)
	# offering shelf
	draw_line(Vector2(580, 350), Vector2(700, 350), ink, 3.0)
	draw_line(Vector2(586, 350), Vector2(586, 366), ink, 2.0)
	draw_line(Vector2(694, 350), Vector2(694, 366), ink, 2.0)
	var li: Array = _state.get("lexicon_items", [])
	for i in range(mini(li.size(), 8)):
		draw_rect(Rect2(590 + i * 13, 340, 8, 8), a1 if i % 2 == 0 else a2)
	# fox statues · one is chipped
	draw_rect(Rect2(532, 280, 14, 26), a3)
	draw_rect(Rect2(734, 280, 14, 26), a3)
	draw_rect(Rect2(744, 278, 3, 3), paper)      # the chip
	# camphor tree
	draw_line(Vector2(790, 340), Vector2(790, 240), ink, 3.0)
	draw_circle(Vector2(790, 226), 34.0, a2 if _season != "winter" else a3)
	# cistern
	draw_circle(Vector2(520, 430), 16.0, a3)
	draw_arc(Vector2(520, 430), 16.0, 0, TAU, 24, ink, 1.5)
	# brazier
	draw_rect(Rect2(750, 444, 20, 16), ink, false, 1.5)
	if _season == "autumn":
		draw_circle(Vector2(760, 440), 3.0, a1)
	# the steps · swept state shows
	var swept: int = int(_state.get("swept", 0))
	for i in range(8):
		var y := 480.0 + i * 16.0
		draw_line(Vector2(600 - i * 3, y), Vector2(680 + i * 3, y), ink, 2.0)
		if swept < 4 and i % 2 == 0:
			draw_circle(Vector2(620 + (i * 37) % 60, y - 4), 2.0, a1)   # unswept leaves
	# the torii
	draw_line(Vector2(596, 660), Vector2(596, 596), a1, 5.0)
	draw_line(Vector2(684, 660), Vector2(684, 596), a1, 5.0)
	draw_line(Vector2(584, 600), Vector2(696, 600), a1, 5.0)
	draw_line(Vector2(588, 612), Vector2(692, 612), a1, 3.0)
	# the rope · frays back slowly
	var mended: int = int(_state.get("mended", 5))
	if mended >= 5:
		draw_line(Vector2(600, 618), Vector2(680, 618), a3, 2.0)
	else:
		draw_line(Vector2(600, 618), Vector2(632, 620), a3, 2.0)
		draw_line(Vector2(648, 621), Vector2(680, 618), a3, 2.0)
	# the watcher's position
	var here: Vector2 = SPOTS[_at]["pos"]
	draw_circle(here + Vector2(0, 14), 5.0, ink)
	draw_arc(here, 46.0, 0, TAU, 32, Color(ink.r, ink.g, ink.b, 0.25), 1.0)
	# weather marks
	if _season == "spring":
		for i in range(6):
			draw_circle(Vector2(440.0 + (i * 73) % 400, 40.0 + (i * 51) % 200), 2.0, a1)
	elif _season == "winter":
		for i in range(10):
			draw_circle(Vector2(430.0 + (i * 47) % 420, 30.0 + (i * 67) % 600), 1.5, a2)


func _sfx(preset: String, vol: float = 1.0) -> void:
	var sb := get_node_or_null("/root/SFXBank")
	if sb != null and sb.has_method("play"):
		sb.play(preset, vol)


func _input(event: InputEvent) -> void:
	if not is_visible_in_tree():
		return
	if event is InputEventKey and event.pressed and not event.echo:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			quit.emit()
			get_viewport().set_input_as_handled()
