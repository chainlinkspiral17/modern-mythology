extends Control
## NORTHWIND HARBOR · one morning, 5:47 to the horns.
##
## Twelve tableaux, one held wide shot each.  Navigation is
## Fey-Faire-midway cell movement across the harbor graph.  The
## core mechanic is LISTENING: working people talk AT you, one or
## two lines, while doing their jobs; every puzzle's hint was said
## aloud once by someone two screens away.  Overheard lines land
## in the HEARD list.  POCKETS: five slots, an open coat lining.
##
## BOSUN is always on screen.  What he noses is live.  He has more
## animation frames than the boy.  This is correct.
##
## No fail states.  The horn ends the morning whether or not the
## chain closed; unfinished chains carry over, and the town
## notices.  Chapter 6 is fog: navigation labels become what each
## place SOUNDS like.  Chapter 7, nothing is wrong; you walk the
## dog.

signal quit
signal morning_over(state: Dictionary)

const LOCS_PATH := "res://resources/games/vol7/northwind_harbor/locations.json"
const CHAP_PATH := "res://resources/games/vol7/northwind_harbor/chapters.json"
const HERO_DIR  := "res://resources/games/vol7/northwind_harbor/hero_images/"
const SPRITE_DIR := "res://resources/games/vol7/northwind_harbor/sprites/"

# The dawn palette
const C_DARK  := Color("16202e")
const C_FOG   := Color("7a8894")
const C_PILE  := Color("4a5a52")
const C_WOOD  := Color("30281e")
const C_LAMP  := Color("d88a30")
const C_GULL  := Color("c8ccd4")

const START_MIN := 347      # 5:47
const HORN_MIN  := 420      # 7:00
const MOVE_COST := 4
const ACT_COST  := 1
const POCKET_SLOTS := 5

var _locs: Dictionary = {}      # id → location dict
var _chapters: Array = []
var _state: Dictionary = {}
var _chapter: Dictionary = {}
var _loc_id: String = ""
var _minutes: int = START_MIN
var _morning_done: bool = false
var _ambient_flip: int = 0

var _tableau: TextureRect = null
var _loc_lbl: Label = null
var _clock_lbl: Label = null
var _text_lbl: Label = null
var _nav_row: HBoxContainer = null
var _act_btn: Button = null
var _pocket_lbl: Label = null
var _heard_btn: Button = null
var _heard_overlay: Control = null
var _bosun_rect: TextureRect = null
var _bosun_note: Label = null
var _sprite := SlowstockSprite.new()


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_load_data()
	_build_ui()


func boot(state: Dictionary) -> void:
	_state = state
	var n: int = clampi(int(_state.get("chapter_n", 1)), 1, 7)
	_chapter = _chapters[n - 1]
	_minutes = START_MIN
	_loc_id = "maddox_porch"
	_morning_done = false
	_enter_location(_loc_id, true)
	if n == 1:
		_add_heard(_opening_line())
		_text_lbl.text = _opening_line()


func _opening_line() -> String:
	# Canon · the line Sam backed out before hearing again.
	return "you ask bosun if he's ready to walk. he was ready before you asked. he is always ready before you ask."


# ─── Data ────────────────────────────────────────────────────────

func _load_data() -> void:
	var l: Dictionary = _load_json(LOCS_PATH)
	for loc in l.get("locations", []):
		_locs[String(loc["id"])] = loc
	var c: Dictionary = _load_json(CHAP_PATH)
	_chapters = c.get("chapters", [])


func _load_json(path: String) -> Dictionary:
	if not FileAccess.file_exists(path): return {}
	var f := FileAccess.open(path, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	return parsed if parsed is Dictionary else {}


func _steps_done() -> Array:
	return _state.get("steps_done", [])


func _pockets() -> Array:
	return _state.get("pockets", [])


func _heard() -> Array:
	return _state.get("heard", [])


func _add_heard(line: String) -> void:
	var h: Array = _heard()
	if not h.has(line):
		h.append(line)
	_state["heard"] = h


func _mark_done(step_id: String) -> void:
	var d: Array = _steps_done()
	if not d.has(step_id):
		d.append(step_id)
	_state["steps_done"] = d


# A step is live: in a chapter ≤ current, requirements met, not done.
func _live_steps() -> Array:
	var out: Array = []
	var n: int = int(_chapter.get("n", 1))
	for ch in _chapters:
		if int(ch.get("n", 1)) > n:
			break
		for step in ch.get("steps", []):
			var s: Dictionary = step
			if _steps_done().has(String(s["id"])):
				continue
			var ok := true
			for req in s.get("requires", []):
				if not _steps_done().has(String(req)):
					ok = false
					break
			if ok:
				out.append(s)
	return out


func _live_step_here() -> Dictionary:
	for s in _live_steps():
		if String(s["loc"]) == _loc_id:
			return s
	return {}


func _next_step_loc() -> String:
	var here: Dictionary = _live_step_here()
	if not here.is_empty():
		return _loc_id
	var live: Array = _live_steps()
	if live.is_empty():
		return ""
	return String(live[0]["loc"])


# ─── UI build ────────────────────────────────────────────────────

func _build_ui() -> void:
	var bg := ColorRect.new()
	bg.color = C_DARK
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	_tableau = TextureRect.new()
	_tableau.stretch_mode = TextureRect.STRETCH_KEEP
	_tableau.position = Vector2(112, 10)
	_tableau.size = Vector2(1056, 594)
	add_child(_tableau)

	_bosun_rect = TextureRect.new()
	_bosun_rect.stretch_mode = TextureRect.STRETCH_KEEP
	add_child(_bosun_rect)

	_loc_lbl = Label.new()
	_loc_lbl.position = Vector2(126, 20)
	_loc_lbl.add_theme_font_size_override("font_size", 16)
	_loc_lbl.add_theme_color_override("font_color", C_FOG)
	add_child(_loc_lbl)

	_clock_lbl = Label.new()
	_clock_lbl.position = Vector2(1090, 20)
	_clock_lbl.add_theme_font_size_override("font_size", 16)
	_clock_lbl.add_theme_color_override("font_color", C_GULL)
	add_child(_clock_lbl)

	_text_lbl = Label.new()
	_text_lbl.position = Vector2(120, 608)
	_text_lbl.size = Vector2(880, 58)
	_text_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_text_lbl.add_theme_font_size_override("font_size", 15)
	_text_lbl.add_theme_color_override("font_color", C_GULL)
	add_child(_text_lbl)

	_bosun_note = Label.new()
	_bosun_note.position = Vector2(120, 668)
	_bosun_note.size = Vector2(600, 24)
	_bosun_note.add_theme_font_size_override("font_size", 13)
	_bosun_note.add_theme_color_override("font_color", C_FOG)
	add_child(_bosun_note)

	_nav_row = HBoxContainer.new()
	_nav_row.position = Vector2(120, 694)
	_nav_row.size = Vector2(1040, 26)
	_nav_row.add_theme_constant_override("separation", 10)
	add_child(_nav_row)

	_act_btn = Button.new()
	_act_btn.flat = true
	_act_btn.position = Vector2(1010, 608)
	_act_btn.size = Vector2(200, 30)
	_act_btn.add_theme_font_size_override("font_size", 14)
	_act_btn.add_theme_color_override("font_color", C_LAMP)
	_act_btn.pressed.connect(_do_step)
	add_child(_act_btn)

	_pocket_lbl = Label.new()
	_pocket_lbl.position = Vector2(730, 668)
	_pocket_lbl.size = Vector2(340, 24)
	_pocket_lbl.add_theme_font_size_override("font_size", 13)
	_pocket_lbl.add_theme_color_override("font_color", C_PILE)
	add_child(_pocket_lbl)

	_heard_btn = Button.new()
	_heard_btn.flat = true
	_heard_btn.text = "· HEARD ·"
	_heard_btn.position = Vector2(1080, 668)
	_heard_btn.add_theme_font_size_override("font_size", 13)
	_heard_btn.add_theme_color_override("font_color", C_FOG)
	_heard_btn.pressed.connect(_toggle_heard)
	add_child(_heard_btn)


# ─── Movement + rendering ────────────────────────────────────────

func _enter_location(loc_id: String, first: bool = false) -> void:
	_loc_id = loc_id
	if not first:
		_minutes += MOVE_COST
		_sfx("boot_plank", 0.5)
		if loc_id in ["jetty", "breakwater", "clara_b"]:
			_sfx("water_slap", 0.5)
		elif loc_id in ["fish_station", "cannery_wall"]:
			_sfx("gull_cry", 0.4)
	if _minutes >= HORN_MIN and not _morning_done:
		_end_morning()
		return
	_render()
	# The town talks AT you · a step line if one is live and it is a
	# heard/look type (those fire on arrival · listening is passive).
	var step: Dictionary = _live_step_here()
	if not step.is_empty() and String(step.get("type", "")) in ["heard", "look"]:
		_do_step()


func _render() -> void:
	var loc: Dictionary = _locs.get(_loc_id, {})
	var fog: bool = bool(_chapter.get("fog", false))
	var n: int = int(_chapter.get("n", 1))

	# Tableau
	var hero := HeroImage.new()
	if hero.load_from(HERO_DIR + "loc_" + _loc_id + ".json"):
		_tableau.texture = hero.texture(Vector2i(1056, 594))
	_tableau.modulate = Color(0.62, 0.66, 0.72) if fog else Color.WHITE

	_loc_lbl.text = String(loc.get("name", _loc_id)) + ("  · fog ·" if fog else "")
	_clock_lbl.text = "%d:%02d" % [_minutes / 60, _minutes % 60]

	# Ambient line unless a step already spoke
	if _live_step_here().is_empty():
		var lines: Array = loc.get("ambient_lines", [])
		if lines.size() > 0:
			_ambient_flip += 1
			var carry := _carryover_line_here()
			_text_lbl.text = carry if carry != "" else String(lines[_ambient_flip % lines.size()])

	_render_nav(fog, n)
	_render_action()
	_render_pockets()
	_render_bosun(n)


func _carryover_line_here() -> String:
	# The town notices unfinished chains from PREVIOUS mornings.
	var n: int = int(_chapter.get("n", 1))
	for ch in _chapters:
		if int(ch.get("n", 1)) >= n:
			break
		for step in ch.get("steps", []):
			var s: Dictionary = step
			if bool(s.get("optional", false)):
				continue
			if _steps_done().has(String(s["id"])):
				continue
			if s.has("carryover_line") and String(s["loc"]) == _loc_id:
				return String(s["carryover_line"])
	return ""


func _render_nav(fog: bool, n: int) -> void:
	for c in _nav_row.get_children():
		c.queue_free()
	var loc: Dictionary = _locs.get(_loc_id, {})
	var locked: Array = _chapter.get("locked_locations", []) if n == 1 else []
	for adj_v in loc.get("adjacent", []):
		var adj := String(adj_v)
		if locked.has(adj):
			var lock_lbl := Label.new()
			lock_lbl.text = "· the breakwater gate is chained ·"
			lock_lbl.add_theme_font_size_override("font_size", 13)
			lock_lbl.add_theme_color_override("font_color", C_WOOD)
			_nav_row.add_child(lock_lbl)
			continue
		var b := Button.new()
		var target: Dictionary = _locs.get(adj, {})
		if fog:
			b.text = "→ (" + String(target.get("sound_cue", "something out there")) + ")"
		else:
			b.text = "→ " + String(target.get("name", adj))
		b.flat = true
		b.add_theme_font_size_override("font_size", 14)
		b.add_theme_color_override("font_color", C_GULL)
		b.add_theme_color_override("font_hover_color", C_LAMP)
		b.pressed.connect(_enter_location.bind(adj))
		_nav_row.add_child(b)


func _render_action() -> void:
	var step: Dictionary = _live_step_here()
	if step.is_empty():
		_act_btn.visible = false
		return
	var t := String(step.get("type", ""))
	match t:
		"pickup": _act_btn.text = "· pick up: %s ·" % String(step.get("item", ""))
		"give":   _act_btn.text = "· give: %s ·" % String(step.get("item", ""))
		"use":    _act_btn.text = "· use: %s ·" % String(step.get("item", ""))
		"look":   _act_btn.text = "· look ·"
		_:        _act_btn.text = "· listen ·"
	_act_btn.visible = true


func _render_pockets() -> void:
	var p: Array = _pockets()
	var chips: Array = []
	for i in range(POCKET_SLOTS):
		chips.append(String(p[i]) if i < p.size() else "—")
	_pocket_lbl.text = "pockets · " + " | ".join(chips)


func _render_bosun(n: int) -> void:
	var loc: Dictionary = _locs.get(_loc_id, {})
	var anchor: Array = loc.get("bosun_anchor", [640, 500])
	var stance := "stand"
	var note := ""
	var here: Dictionary = _live_step_here()
	var next_loc := _next_step_loc()
	if n == 7 and _loc_id == "cannery_wall":
		stance = "refuse"
		note = "bosun will not come closer."
	elif not here.is_empty():
		stance = "point" if bool(here.get("bosun_marks", false)) else "sniff"
		note = "bosun noses at something here."
	elif next_loc != "" and next_loc != _loc_id:
		stance = "trot"
		var target: Dictionary = _locs.get(next_loc, {})
		note = "bosun keeps looking toward %s." % String(target.get("name", next_loc)).to_lower()
	else:
		stance = "sit"
		note = "bosun sits. the morning is doing what mornings do."
	if _sprite.load(SPRITE_DIR + "bosun_" + stance + ".json"):
		_bosun_rect.texture = _sprite.texture()
		var scale := 6.0
		_bosun_rect.size = Vector2(16 * scale, 12 * scale)
		# Anchor is in tableau 1056×594 space offset by the tableau origin
		var ax := 112.0 + float(anchor[0]) * (1056.0 / 1280.0)
		var ay := 10.0 + float(anchor[1]) * (594.0 / 720.0)
		_bosun_rect.position = Vector2(ax - 48, ay - 72)
	_bosun_note.text = note


# ─── Steps ───────────────────────────────────────────────────────

func _do_step() -> void:
	var step: Dictionary = _live_step_here()
	if step.is_empty() or _morning_done:
		return
	var t := String(step.get("type", ""))
	var sid := String(step["id"])
	match t:
		"heard":
			_add_heard(String(step.get("line", "")))
			_text_lbl.text = String(step.get("line", ""))
			_mark_done(sid)
		"look":
			_text_lbl.text = String(step.get("line", ""))
			if step.has("heard_as"):
				_add_heard(String(step["heard_as"]))
			_mark_done(sid)
			if bool(step.get("poster", false)):
				_show_poster()
				return
		"pickup":
			if _pockets().size() >= POCKET_SLOTS:
				_text_lbl.text = "your pockets are full. five is five."
				return
			var p: Array = _pockets()
			p.append(String(step.get("item", "")))
			_state["pockets"] = p
			_text_lbl.text = String(step.get("text", ""))
			_mark_done(sid)
			_sfx("pickup", 0.6)
		"give", "use":
			var item := String(step.get("item", ""))
			var p2: Array = _pockets()
			if not p2.has(item):
				_text_lbl.text = "you pat your pockets. not there."
				return
			p2.erase(item)
			if step.has("makes_item"):
				p2.append(String(step["makes_item"]))
			_state["pockets"] = p2
			_text_lbl.text = String(step.get("text", ""))
			_mark_done(sid)
			if sid == "fix_lamp":
				_sfx("lamp_buzz", 0.8)
	_minutes += ACT_COST
	if _minutes >= HORN_MIN:
		_end_morning()
		return
	_render()


func _show_poster() -> void:
	# Chapter 7 · the wall. No UI. No explanation, then or ever.
	var hero := HeroImage.new()
	if hero.load_from(HERO_DIR + "carnival_poster.json"):
		_tableau.texture = hero.texture(Vector2i(1056, 594))
	_loc_lbl.text = ""
	_nav_row.visible = false
	_act_btn.visible = false
	_heard_btn.visible = false
	_pocket_lbl.visible = false
	_add_heard("the poster on the cannery wall · CARNIVAL · SEVEN YEARS · 1976 · half torn · bosun would not come near it")
	_render_bosun(7)
	_state["poster_seen"] = true
	var tw := create_tween()
	tw.tween_interval(6.0)
	tw.tween_callback(_end_morning)


func _end_morning() -> void:
	if _morning_done:
		return
	_morning_done = true
	_sfx("boat_horn", 1.0)
	_text_lbl.text = "the horns blow across the water. the morning is over, however it went."
	_act_btn.visible = false
	_nav_row.visible = false
	var home := Button.new()
	home.text = "  · walk home ·  "
	home.add_theme_font_size_override("font_size", 14)
	home.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	home.position = Vector2(1020, 690)
	home.pressed.connect(func() -> void: morning_over.emit(_state))
	add_child(home)


# ─── HEARD overlay ───────────────────────────────────────────────

func _toggle_heard() -> void:
	if _heard_overlay != null and is_instance_valid(_heard_overlay):
		_heard_overlay.queue_free()
		_heard_overlay = null
		return
	_heard_overlay = Panel.new()
	_heard_overlay.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_heard_overlay.offset_left = -420
	_heard_overlay.offset_right = 420
	_heard_overlay.offset_top = -280
	_heard_overlay.offset_bottom = 280
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(C_DARK.r, C_DARK.g, C_DARK.b, 0.96)
	sb.border_color = C_FOG
	sb.set_border_width_all(1)
	_heard_overlay.add_theme_stylebox_override("panel", sb)
	add_child(_heard_overlay)

	var scroll := ScrollContainer.new()
	scroll.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scroll.offset_left = 16
	scroll.offset_right = -16
	scroll.offset_top = 16
	scroll.offset_bottom = -16
	_heard_overlay.add_child(scroll)

	var col := VBoxContainer.new()
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	col.add_theme_constant_override("separation", 10)
	scroll.add_child(col)

	var hdr := Label.new()
	hdr.text = "· HEARD · everything anyone said, you keep ·"
	hdr.add_theme_font_size_override("font_size", 14)
	hdr.add_theme_color_override("font_color", C_LAMP)
	col.add_child(hdr)

	for line in _heard():
		var l := Label.new()
		l.text = "· " + String(line)
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.custom_minimum_size = Vector2(800, 0)
		l.add_theme_font_size_override("font_size", 14)
		l.add_theme_color_override("font_color", C_GULL)
		col.add_child(l)


# ─── Plumbing ────────────────────────────────────────────────────

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
			if _heard_overlay != null and is_instance_valid(_heard_overlay):
				_toggle_heard()
			else:
				quit.emit()
			get_viewport().set_input_as_handled()
		elif kev.keycode == KEY_H:
			_toggle_heard()
