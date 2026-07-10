extends Control
## ESTUARY 2 · one walk on the flat · June to September in twelve.
##
## Top-down walkable soft-sim · one place: the mudflat, a channel,
## a boardwalk, four house-backs on the bluff, the county road.
## Verbs: WALK (arrows/WASD) · LOOK (E, hold near a species) ·
## CRANK (E at the radio) · TALK (E at a neighbor) · GO HOME (E at
## the road).
##
## WITNESSING IS MECHANICAL: LOOK logs an observation.  Observe
## the same species three walks running and its journal page
## ILLUMINATES · the population math becomes visible on the page.
## The player affects NOTHING directly.  E2 removes E1's lever on
## purpose.
##
## Week 6: the stakes.  The most saturated color in the game.

signal quit
signal walk_over(state: Dictionary)

const SPECIES_PATH := "res://resources/games/vol7/estuary_2/species.json"
const WALKS_PATH   := "res://resources/games/vol7/estuary_2/walks.json"
const WALKER_SPRITE := "res://resources/games/vol7/estuary_2/sprites/walker.json"

# Mudflat neutrals · small color events read loud
const C_MUD    := Color("5a6058")
const C_DRY    := Color("8a8878")
const C_CHAN   := Color("3a4a52")
const C_PLANK  := Color("a8a290")
const C_WEED   := Color("708468")
const C_SKY    := Color("b8b4a4")
const C_STAKE  := Color("d87838")
const C_DARK   := Color("2a3038")

const SPEED := 170.0
const REACH := 52.0
const LOOK_HOLD := 1.2

const NEIGHBORS := {
	"ruth": {"pos": Vector2(220, 380), "name": "RUTH", "col": Color("6a4a30")},
	"cole": {"pos": Vector2(880, 150), "name": "COLE", "col": Color("4a5a52")},
	"ames": {"pos": Vector2(620, 300), "name": "MRS. AMES", "col": Color("8a6878")},
	"jules": {"pos": Vector2(760, 330), "name": "JULES", "col": Color("48607a")},
}
const RADIO_POS := Vector2(480, 300)
const ROAD_Y := 90.0
const STAKE_SPOTS := [Vector2(430, 480), Vector2(560, 440), Vector2(690, 500), Vector2(820, 460)]

var _species: Array = []
var _walks: Dictionary = {}
var _walk: Dictionary = {}
var _state: Dictionary = {}
var _n: int = 1
var _pos := Vector2(640, 200)
var _dir := Vector2.ZERO
var _look_target: String = ""
var _look_t: float = 0.0
var _looked_this_walk: Dictionary = {}
var _petition_asked: Dictionary = {}
var _sprites: Dictionary = {}       # species id → SlowstockSprite
var _walker := SlowstockSprite.new()
var _journal_open: bool = false

var _msg_lbl: Label = null
var _hint_lbl: Label = null
var _hdr_lbl: Label = null
var _journal_overlay: Control = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_load_data()
	_build_ui()
	set_process(true)


func boot(state: Dictionary) -> void:
	_state = state
	_n = clampi(int(_state.get("walk_n", 1)), 1, 12)
	_walk = (_walks.get("walks", []))[_n - 1]
	_pos = Vector2(640, 200)
	_looked_this_walk = {}
	_petition_asked = {}
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("play_bgm"):
		am.play_bgm("res://assets/audio/bgm/e2/walk_%02d.wav" % _n)
	_hdr_lbl.text = "%s · WALK %d OF 12 · %s" % [String(_walk.get("month", "")), _n,
			String(_walk.get("weather", "")).replace("_", " ")]
	_msg("the flat at low tide. the radio is on the boardwalk rail. home is the county road.")
	queue_redraw()


func _load_data() -> void:
	for pair in [[SPECIES_PATH, "s"], [WALKS_PATH, "w"]]:
		var f := FileAccess.open(String(pair[0]), FileAccess.READ)
		if f == null: continue
		var parsed: Variant = JSON.parse_string(f.get_as_text())
		f.close()
		if parsed is Dictionary:
			if String(pair[1]) == "s": _species = (parsed as Dictionary).get("species", [])
			else: _walks = parsed
	for sp_v in _species:
		var sp: Dictionary = sp_v
		var spr := SlowstockSprite.new()
		if spr.load(String(sp["sprite"])):
			_sprites[String(sp["id"])] = spr
	_walker.load(WALKER_SPRITE)


func _build_ui() -> void:
	_hdr_lbl = Label.new()
	_hdr_lbl.position = Vector2(24, 12)
	_hdr_lbl.add_theme_font_size_override("font_size", 15)
	_hdr_lbl.add_theme_color_override("font_color", C_DARK)
	add_child(_hdr_lbl)

	_msg_lbl = Label.new()
	_msg_lbl.position = Vector2(24, 648)
	_msg_lbl.size = Vector2(1000, 60)
	_msg_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_msg_lbl.add_theme_font_size_override("font_size", 15)
	_msg_lbl.add_theme_color_override("font_color", C_DARK)
	add_child(_msg_lbl)

	_hint_lbl = Label.new()
	_hint_lbl.position = Vector2(1040, 12)
	_hint_lbl.add_theme_font_size_override("font_size", 12)
	_hint_lbl.add_theme_color_override("font_color", C_MUD)
	_hint_lbl.text = "arrows · E interact · J journal"
	add_child(_hint_lbl)


# ─── Movement + verbs ────────────────────────────────────────────

func _process(delta: float) -> void:
	if _journal_open:
		return
	_dir = Vector2.ZERO
	if Input.is_key_pressed(KEY_LEFT) or Input.is_key_pressed(KEY_A): _dir.x -= 1
	if Input.is_key_pressed(KEY_RIGHT) or Input.is_key_pressed(KEY_D): _dir.x += 1
	if Input.is_key_pressed(KEY_UP) or Input.is_key_pressed(KEY_W): _dir.y -= 1
	if Input.is_key_pressed(KEY_DOWN) or Input.is_key_pressed(KEY_S): _dir.y += 1
	if _dir != Vector2.ZERO:
		_pos += _dir.normalized() * SPEED * delta
		_pos.x = clampf(_pos.x, 40, 1240)
		_pos.y = clampf(_pos.y, 70, 630)
		queue_redraw()

	# LOOK · hold E near a species
	if Input.is_key_pressed(KEY_E):
		var near := _species_near()
		if near != "":
			if _look_target != near:
				_look_target = near
				_look_t = 0.0
			_look_t += delta
			if _look_t >= LOOK_HOLD and not _looked_this_walk.has(near):
				_register_observation(near)
			queue_redraw()
	else:
		_look_target = ""
		_look_t = 0.0


func _species_near() -> String:
	for sp_v in _species:
		var sp: Dictionary = sp_v
		if _pop(sp) <= 0:
			continue
		var spot := Vector2(sp["spot"][0], sp["spot"][1])
		if _pos.distance_to(spot) < REACH:
			return String(sp["id"])
	return ""


func _pop(sp: Dictionary) -> int:
	return int((sp.get("pop", []))[_n - 1]) if _n - 1 < (sp.get("pop", []) as Array).size() else 0


func _register_observation(sid: String) -> void:
	_looked_this_walk[sid] = true
	var obs: Dictionary = _state.get("observations", {})
	var walks_seen: Array = obs.get(sid, [])
	if not walks_seen.has(_n):
		walks_seen.append(_n)
	obs[sid] = walks_seen
	_state["observations"] = obs
	var sp := _find_species(sid)
	# Three walks RUNNING illuminates the page.
	var illuminated: Array = _state.get("illuminated", [])
	var streak := _streak(walks_seen)
	if streak >= 3 and not illuminated.has(sid):
		illuminated.append(sid)
		_state["illuminated"] = illuminated
		OneironauticsTokens.add("e2_journal_" + sid)
		_sfx("unlock_chime", 0.5)
		_msg("the journal page for %s ILLUMINATES. the math is visible now. its voice joins the walk." % String(sp.get("name", sid)))
	else:
		_sfx("page_turn", 0.4)
		_msg("observed · %s (%d walk%s running). %s" % [String(sp.get("name", sid)), streak,
				"s" if streak != 1 else "", String(sp.get("keystone", ""))])


func _streak(walks_seen: Array) -> int:
	var streak := 0
	var w := _n
	while walks_seen.has(w) and w >= 1:
		streak += 1
		w -= 1
	return streak


func _find_species(sid: String) -> Dictionary:
	for sp in _species:
		if String((sp as Dictionary)["id"]) == sid:
			return sp
	return {}


func _input(event: InputEvent) -> void:
	if not is_visible_in_tree():
		return
	if event is InputEventKey and event.pressed and not event.echo:
		var kev: InputEventKey = event
		match kev.keycode:
			KEY_ESCAPE:
				if _journal_open:
					_toggle_journal()
				else:
					quit.emit()
				get_viewport().set_input_as_handled()
			KEY_J:
				_toggle_journal()
			KEY_E:
				_try_interact()


func _try_interact() -> void:
	if _journal_open:
		return
	# The road · go home
	if _pos.y <= ROAD_Y + 30:
		_msg("you go home. the flat keeps working without you, which is the point.")
		var tw := create_tween()
		tw.tween_interval(1.2)
		tw.tween_callback(func() -> void: walk_over.emit(_state))
		set_process(false)
		return
	# The radio
	if _pos.distance_to(RADIO_POS) < REACH:
		_sfx("radio_static", 0.5)
		_msg("· crank · crank · " + String(_walk.get("radio", "")))
		return
	# Neighbors
	for nid in NEIGHBORS.keys():
		if _pos.distance_to(NEIGHBORS[nid]["pos"]) < REACH:
			_talk(String(nid))
			return


func _talk(nid: String) -> void:
	var scenes: Dictionary = _walk.get("scenes", {})
	if scenes.has(nid) and not bool(_state.get("scene_seen_%d_%s" % [_n, nid], false)):
		_state["scene_seen_%d_%s" % [_n, nid]] = true
		_msg(String(scenes[nid]))
		return
	# Petition · walkable door to door from week 6
	if _n >= 6 and not _petition_asked.has(nid):
		_petition_asked[nid] = true
		var sigs: Array = _state.get("petition", [])
		match nid:
			"ruth":
				_msg("ruth reads the whole petition, both sides. 'no.' she hands it back with respect.")
			"cole":
				if bool(_state.get("scene_seen_8_cole", false)) and not sigs.has("cole"):
					sigs.append("cole")
					_msg("cole signs with his county pen, slowly, like the signature costs. 'i owe an old flat upcoast this one.'")
				else:
					_msg("cole looks at the petition and away. 'ask me after the weather turns.' he means something else.")
			"ames":
				if (_state.get("illuminated", []) as Array).size() >= 6 and not sigs.has("ames"):
					sigs.append("ames")
					_msg("mrs. ames flips through your journal pages first. counts them. 'you've done the looking. all right.' she signs above the line, neatly.")
				else:
					_msg("mrs. ames: 'show me a summer of looking and we'll talk.' she is counting your journal pages.")
			"jules":
				if not sigs.has("jules"):
					sigs.append("jules")
					_msg("jules signs before you finish the sentence. 'somebody's got to be first. it's never me. today it's me.'")
		_state["petition"] = sigs
		return
	var lines := {"ruth": "ruth nods at the water. the water nods back, per their arrangement.",
		"cole": "cole is measuring something by eye. he will tell you what if you have an hour.",
		"ames": "mrs. ames sweeps. counts. sweeps.",
		"jules": "jules watches the flat like it's television. 'shh. it's a good part.'"}
	_msg(String(lines.get(nid, "")))


func _msg(t: String) -> void:
	_msg_lbl.text = t


# ─── Journal (key J) · the direct ancestor of PS's J-panel ──────

func _toggle_journal() -> void:
	if _journal_overlay != null and is_instance_valid(_journal_overlay):
		_journal_overlay.queue_free()
		_journal_overlay = null
		_journal_open = false
		return
	_journal_open = true
	_journal_overlay = Panel.new()
	_journal_overlay.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_journal_overlay.offset_left = -440
	_journal_overlay.offset_right = 440
	_journal_overlay.offset_top = -290
	_journal_overlay.offset_bottom = 290
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(C_PLANK.r, C_PLANK.g, C_PLANK.b, 0.98)
	sb.border_color = C_DARK
	sb.set_border_width_all(1)
	_journal_overlay.add_theme_stylebox_override("panel", sb)
	add_child(_journal_overlay)

	var scroll := ScrollContainer.new()
	scroll.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scroll.offset_left = 18
	scroll.offset_right = -18
	scroll.offset_top = 14
	scroll.offset_bottom = -14
	_journal_overlay.add_child(scroll)
	var col := VBoxContainer.new()
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	col.add_theme_constant_override("separation", 8)
	scroll.add_child(col)

	var hdr := Label.new()
	var illuminated: Array = _state.get("illuminated", [])
	hdr.text = "· FIELD JOURNAL · %d of 12 pages illuminated ·" % illuminated.size()
	hdr.add_theme_font_size_override("font_size", 15)
	hdr.add_theme_color_override("font_color", C_DARK)
	col.add_child(hdr)

	var obs: Dictionary = _state.get("observations", {})
	for sp_v in _species:
		var sp: Dictionary = sp_v
		var sid := String(sp["id"])
		var lit: bool = illuminated.has(sid)
		var seen: Array = obs.get(sid, [])
		var l := Label.new()
		if lit:
			var curve := ""
			for v in sp.get("pop", []):
				curve += str(int(v))
			l.text = "★ %s · %s\n    twelve weeks · %s" % [String(sp["name"]), String(sp.get("keystone", "")), curve]
		elif seen.size() > 0:
			l.text = "· %s · observed %d walk(s) · the page is pencil, waiting for ink" % [String(sp["name"]), seen.size()]
		else:
			l.text = "· (a ruled page, blank · something lives here you haven't looked at)"
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.custom_minimum_size = Vector2(800, 0)
		l.add_theme_font_size_override("font_size", 13)
		l.add_theme_color_override("font_color", C_DARK if lit else C_MUD)
		col.add_child(l)

	var sigs: Array = _state.get("petition", [])
	if _n >= 6:
		var p := Label.new()
		p.text = "· PETITION · %d signature(s) · %s" % [sigs.size(), ", ".join(sigs) if sigs.size() > 0 else "walk it door to door"]
		p.add_theme_font_size_override("font_size", 13)
		p.add_theme_color_override("font_color", C_STAKE)
		col.add_child(p)


# ─── The flat ────────────────────────────────────────────────────

func _hash(n: int) -> float:
	var x: int = (n * 2654435761) & 0x7FFFFFFF
	x = (x ^ (x >> 13)) * 1274126177 & 0x7FFFFFFF
	return float(x % 1000) / 1000.0


func _draw() -> void:
	var weather := String(_walk.get("weather", "overcast"))
	# ground
	draw_rect(Rect2(0, 0, 1280, 720), C_DRY)
	# bluff + house-backs + county road
	draw_rect(Rect2(0, 0, 1280, 60), C_WEED)
	draw_rect(Rect2(0, 60, 1280, 30), C_PLANK)     # the county road
	for i in range(4):
		var hx := 180.0 + i * 280.0
		draw_rect(Rect2(hx, 8, 90, 44), Color("6a5a48"))
		draw_rect(Rect2(hx + 8, 16, 16, 14), C_DARK)
	# the wet flat
	draw_rect(Rect2(0, 400, 1280, 320), C_MUD)
	for i in range(120):
		var px := _hash(i * 3) * 1280.0
		var py := 410.0 + _hash(i * 7 + 1) * 300.0
		draw_rect(Rect2(px, py, 3, 2), C_DRY if int(_hash(i)) == 0 else Color(C_MUD.r * 0.9, C_MUD.g * 0.9, C_MUD.b * 0.9))
	# pickleweed fringe
	for i in range(40):
		var wx := _hash(i * 11 + 5) * 1280.0
		draw_rect(Rect2(wx, 392.0 + _hash(i) * 20.0, 5, 4), C_WEED)
	# the channel · meandering
	var ch: Array = [Vector2(80, 720), Vector2(180, 600), Vector2(300, 520), Vector2(420, 470),
		Vector2(560, 450), Vector2(720, 470), Vector2(900, 440), Vector2(1100, 470), Vector2(1280, 450)]
	for i in range(ch.size() - 1):
		draw_line(ch[i], ch[i + 1], C_CHAN, 26.0)
	# the boardwalk
	draw_rect(Rect2(120, 290, 780, 26), C_PLANK)
	for x in range(120, 900, 20):
		draw_line(Vector2(x, 290), Vector2(x, 316), C_DRY, 1.0)
	# the radio · a 9-pixel prop on the rail
	draw_rect(Rect2(RADIO_POS.x - 5, RADIO_POS.y - 12, 10, 8), C_DARK)
	draw_line(RADIO_POS + Vector2(0, -12), RADIO_POS + Vector2(4, -18), C_DARK, 1.0)
	# ruth's boat
	draw_rect(Rect2(150, 400, 70, 18), Color("6a4a30"))
	draw_rect(Rect2(170, 388, 24, 12), C_PLANK)
	# the stakes · week 6 on · the most saturated color in the game
	if _n >= 6:
		for s in STAKE_SPOTS:
			draw_rect(Rect2(s.x - 2, s.y - 18, 4, 18), C_STAKE)
			draw_rect(Rect2(s.x - 5, s.y - 18, 10, 4), C_STAKE)
	# species markers · population as cluster size
	for sp_v in _species:
		var sp: Dictionary = sp_v
		var sid := String(sp["id"])
		var pop := _pop(sp)
		if pop <= 0:
			continue
		var spot := Vector2(sp["spot"][0], sp["spot"][1])
		if _sprites.has(sid):
			var tex: Texture2D = _sprites[sid].texture()
			if tex != null:
				draw_texture_rect(tex, Rect2(spot - Vector2(18, 18), Vector2(36, 36)), false)
		for i in range(mini(pop, 6)):
			draw_circle(spot + Vector2(24 + _hash(i * 13) * 20.0, -10 + _hash(i * 17) * 24.0), 2.0, C_CHAN)
		# LOOK progress ring
		if _look_target == sid and _look_t > 0.05:
			draw_arc(spot, 26.0, -PI / 2, -PI / 2 + TAU * clampf(_look_t / LOOK_HOLD, 0.0, 1.0), 20, C_DARK, 2.0)
	# neighbors
	var font := get_theme_default_font()
	for nid in NEIGHBORS.keys():
		var nb: Dictionary = NEIGHBORS[nid]
		var np: Vector2 = nb["pos"]
		draw_rect(Rect2(np - Vector2(7, 20), Vector2(14, 20)), nb["col"])
		draw_circle(np + Vector2(0, -24), 6.0, Color("c8b8a0"))
		draw_string(font, np + Vector2(-20, -34), String(nb["name"]), HORIZONTAL_ALIGNMENT_LEFT, -1, 12, C_DARK)
	# the walker
	var wtex: Texture2D = _walker.texture()
	if wtex != null:
		draw_texture_rect(wtex, Rect2(_pos - Vector2(24, 56), Vector2(48, 64)), false)
	# weather tint over everything
	match weather:
		"fog":         draw_rect(Rect2(0, 0, 1280, 720), Color(C_SKY.r, C_SKY.g, C_SKY.b, 0.32))
		"rare_sun":    draw_rect(Rect2(0, 0, 1280, 720), Color(1.0, 0.96, 0.82, 0.10))
		"first_storm": draw_rect(Rect2(0, 0, 1280, 720), Color(0.2, 0.24, 0.3, 0.25))
		_:             draw_rect(Rect2(0, 0, 1280, 720), Color(C_SKY.r, C_SKY.g, C_SKY.b, 0.14))


func _sfx(preset: String, vol: float = 1.0) -> void:
	var sb := get_node_or_null("/root/SFXBank")
	if sb != null and sb.has_method("play"):
		sb.play(preset, vol)
