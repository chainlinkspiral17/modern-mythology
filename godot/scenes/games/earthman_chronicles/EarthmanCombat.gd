extends Control
## Earthman Chronicles · tactical combat · the boss arenas
## chapters.json describes, playable.
##
## Runs as an OVERLAY inside a chapter scene (the chapter
## instantiates it as a child so its own beat position survives).
## Ported from the Fey Faire combat shape, with two Earthman twists:
##
##   · WORKING · completed Workings are castable specials · the
##     ritual ladder the player climbed becomes their moveset
##   · PARTY   · one party action per fight per member · Hel Velli
##     strikes, Sara Nai's Kyrindi tone staggers, Rocha analyzes
##     (reveals the weak point · +50% player damage after)
##
## Outcomes:
##   victory · overlay closes, the chapter beat continues
##   defeat  · non-lethal · "dragged clear" · the chapter continues
##             with a defeat flag the beats can read
##
## Signals:
##   combat_complete(boss_id, outcome)  · "victory" | "defeat"
##
## F4-compliant via add_to_group("ui").

signal combat_complete(boss_id: String, outcome: String)

const C_BG      := Color(0.043, 0.031, 0.055, 1.0)
const C_CORTEX  := Color(0.345, 0.188, 0.376, 1.0)
const C_PANEL   := Color(0.16, 0.10, 0.20, 1.0)
const C_AMBER   := Color(0.784, 0.376, 0.125, 1.0)
const C_STAR    := Color(0.973, 0.784, 0.282, 1.0)
const C_GREEN   := Color(0.0, 0.753, 0.376, 1.0)
const C_RED     := Color(0.753, 0.125, 0.125, 1.0)
const C_CREAM   := Color(0.912, 0.816, 0.565, 1.0)
const C_WHITE   := Color(0.941, 0.941, 0.941, 1.0)
const C_DIM     := Color(0.545, 0.463, 0.302, 1.0)
const C_SP      := Color(0.55, 0.72, 0.94, 1.0)

const BOSSES: Dictionary = {
	"hel_velli_duel": {
		"name": "HEL VELLI · THE DUEL",
		"hp": 40, "strike": 8,
		"flavor": "Four arms, two blades drawn, two open.  He is not trying to kill you.  He is trying to find out what you do when it costs something.",
		"skills": ["upper-left feint", "lower-right sweep", "the patient guard"],
		"nonlethal": true
	},
	"thar_krai_tam": {
		"name": "THAR-KRAI-TAM · OVERSEER OF THE KEL-RETHANI",
		"hp": 70, "strike": 11,
		"flavor": "Seven feet two.  The silvered blade stays sheathed until the third turn · a courtesy, or a habit of a man who has never needed it early.",
		"skills": ["silvered heirloom blade", "the four-arm bind", "overseer's bellow"],
		"nonlethal": false
	},
	"nalat": {
		"name": "NALAT · ORDER SENIOR SECOND CLASS",
		"hp": 90, "strike": 12,
		"flavor": "He holds the ceremonial blade wrong on purpose.  The eight-pointed stars in the floor brighten when he steps on them.  This is his room, and the room is on his side.",
		"skills": ["the room itself", "administrative patience", "a bonus for each"],
		"nonlethal": false
	}
}

# Working id → castable special
const WORKING_MOVES: Dictionary = {
	"star_ruby":              {"label": "Star Ruby · circle of protection", "kind": "shield", "power": 0, "note": "halves incoming damage for 2 turns"},
	"lesser_ritual_pentagram":{"label": "Lesser Pentagram · banish", "kind": "heal", "power": 14, "note": "restores 14 HP"},
	"bornless_one":           {"label": "The Bornless One · invocation", "kind": "attack", "power": 24, "note": "24 ritual damage"},
	"hymn_of_pan":            {"label": "Hymn of Pan · wild vigor", "kind": "buff", "power": 0, "note": "+6 to every attack this fight"},
	"mass_of_the_phoenix":    {"label": "Mass of the Phoenix · fire", "kind": "attack", "power": 30, "note": "30 ritual damage"},
	"liber_reguli":           {"label": "Liber Reguli · the war-god's clarity", "kind": "buff", "power": 0, "note": "+6 to every attack this fight"},
	"the_great_work":         {"label": "The Great Work · presence", "kind": "shield", "power": 0, "note": "halves incoming damage for 2 turns"},
	"star_sapphire":          {"label": "Star Sapphire · ward", "kind": "shield", "power": 0, "note": "halves incoming damage for 2 turns"}
}

var _boss_id: String = ""
var _boss: Dictionary = {}
var _run_state: Dictionary = {}

var _player_hp: int = 60
var _player_hp_max: int = 60
var _boss_hp: int = 50
var _boss_hp_max: int = 50
var _turn: int = 1
var _shield_turns: int = 0
var _attack_buff: int = 0
var _weakness_revealed: bool = false
# Thar-Krai-Tam arena pattern state · the pattern-setter boss.
# Other bosses run the generic strike loop below.
var _bind_incoming: bool = false     # telegraphed · resolves next boss turn
var _blade_drawn: bool = false       # sheathed through turn 3 · a courtesy
var _counter_open: bool = false      # you slipped the bind · next hit x1.5
var _staggered: bool = false         # the bellow · next hit −4
var _party_used: Dictionary = {}     # member id → true
var _workings_cast: Dictionary = {}  # working id → true (one cast each)
var _log: Array = []
var _combat_over: bool = false
var _outcome: String = ""


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")


func boot(state: Dictionary) -> void:
	_boss_id = String(state.get("boss_id", "hel_velli_duel"))
	_run_state = state.get("run_state", {})
	_boss = BOSSES.get(_boss_id, BOSSES["hel_velli_duel"])
	_boss_hp_max = int(_boss.get("hp", 50))
	_boss_hp = _boss_hp_max
	_player_hp_max = int(_run_state.get("hp_max", 100 if _run_state.has("hp_max") else 60))
	if _player_hp_max <= 0: _player_hp_max = 60
	_player_hp = _player_hp_max
	_log = ["· " + String(_boss.get("flavor", ""))]
	_render()


func _clear_children() -> void:
	for c in get_children():
		c.queue_free()


func _render() -> void:
	_clear_children()

	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	var header := Label.new()
	header.text = "· " + String(_boss.get("name", "?")) + " ·"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 18)
	header.add_theme_color_override("font_color", C_STAR)
	header.set_anchors_preset(Control.PRESET_TOP_WIDE)
	header.offset_top = 30
	header.offset_bottom = 54
	add_child(header)

	# HP bars
	var boss_lbl := Label.new()
	boss_lbl.text = String(_boss.get("name", "?")).split(" ·")[0] + "  " + str(_boss_hp) + "/" + str(_boss_hp_max) + ("   · weak point known ·" if _weakness_revealed else "") + ("   · BIND INCOMING · brace ·" if _bind_incoming else "") + ("   · blade drawn ·" if _blade_drawn else "")
	boss_lbl.set_anchors_preset(Control.PRESET_TOP_LEFT)
	boss_lbl.position = Vector2(60, 66)
	boss_lbl.add_theme_font_size_override("font_size", 15)
	boss_lbl.add_theme_color_override("font_color", C_RED)
	add_child(boss_lbl)

	var jack_lbl := Label.new()
	jack_lbl.text = "JACK  " + str(_player_hp) + "/" + str(_player_hp_max) + ("   · warded ·" if _shield_turns > 0 else "") + ("   · +%d ·" % _attack_buff if _attack_buff > 0 else "") + ("   · opening ·" if _counter_open else "") + ("   · staggered ·" if _staggered else "")
	jack_lbl.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	jack_lbl.position = Vector2(-320, 66)
	jack_lbl.add_theme_font_size_override("font_size", 15)
	jack_lbl.add_theme_color_override("font_color", C_GREEN)
	add_child(jack_lbl)

	# Boss plate · the arena as a picture, above the log
	var plate := HeroImage.new()
	if plate.load_from("res://resources/games/vol7/earthman_chronicles/hero_images/boss_%s.json" % _boss_id):
		var plate_rect := TextureRect.new()
		plate_rect.texture = plate.texture(Vector2i(480, 120))
		plate_rect.set_anchors_preset(Control.PRESET_CENTER_TOP)
		plate_rect.offset_left = -240
		plate_rect.offset_right = 240
		plate_rect.offset_top = 92
		plate_rect.offset_bottom = 212
		plate_rect.stretch_mode = TextureRect.STRETCH_KEEP
		add_child(plate_rect)

	# Log panel
	var log_panel := ColorRect.new()
	log_panel.color = C_PANEL
	log_panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	log_panel.offset_left = -420
	log_panel.offset_right = 420
	log_panel.offset_top = -140
	log_panel.offset_bottom = 60
	add_child(log_panel)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -400
	v.offset_right = 400
	v.offset_top = -130
	v.offset_bottom = 50
	v.add_theme_constant_override("separation", 3)
	add_child(v)

	var turn_lbl := Label.new()
	turn_lbl.text = "· TURN " + str(_turn) + " ·"
	turn_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	turn_lbl.add_theme_font_size_override("font_size", 14)
	turn_lbl.add_theme_color_override("font_color", C_DIM)
	v.add_child(turn_lbl)

	var start: int = max(0, _log.size() - 6)
	for i in range(start, _log.size()):
		var entry := RichTextLabel.new()
		entry.bbcode_enabled = false
		entry.fit_content = true
		entry.text = String(_log[i])
		entry.add_theme_font_size_override("normal_font_size", 14)
		entry.add_theme_color_override("default_color", C_CREAM)
		entry.custom_minimum_size = Vector2(760, 14)
		v.add_child(entry)

	if _combat_over:
		_render_outcome()
	else:
		_render_actions()


func _render_actions() -> void:
	var menu := HBoxContainer.new()
	menu.name = "BottomMenu"
	menu.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	menu.offset_left = 40
	menu.offset_right = -40
	menu.offset_top = -180
	menu.offset_bottom = -110
	menu.alignment = BoxContainer.ALIGNMENT_CENTER
	menu.add_theme_constant_override("separation", 10)
	add_child(menu)

	var atk := Button.new()
	atk.text = "  ATTACK  \n  propellant pistol  "
	atk.custom_minimum_size = Vector2(150, 60)
	atk.add_theme_font_size_override("font_size", 15)
	atk.add_theme_color_override("font_color", C_AMBER)
	atk.pressed.connect(_on_attack)
	menu.add_child(atk)

	var def := Button.new()
	def.text = "  DEFEND  \n  cover + breathe  "
	def.custom_minimum_size = Vector2(150, 60)
	def.add_theme_font_size_override("font_size", 15)
	def.pressed.connect(_on_defend)
	menu.add_child(def)

	# WORKING · one cast each per fight
	var completed: Array = _run_state.get("workings_completed", [])
	var castable: Array = []
	for w_id in completed:
		if WORKING_MOVES.has(String(w_id)) and not _workings_cast.has(String(w_id)):
			castable.append(String(w_id))
	var wk := Button.new()
	if castable.is_empty():
		wk.text = "  WORKING  \n  none ready  "
		wk.disabled = true
	else:
		wk.text = "  WORKING  \n  " + str(castable.size()) + " ready  "
		wk.pressed.connect(func() -> void: _render_working_menu(castable))
	wk.custom_minimum_size = Vector2(150, 60)
	wk.add_theme_font_size_override("font_size", 15)
	wk.add_theme_color_override("font_color", C_STAR)
	menu.add_child(wk)

	# PARTY · one action per member per fight
	var party: Array = _run_state.get("party_members", ["jack"])
	var avail: Array = []
	for m in ["hel_velli", "sara_nai", "rocha"]:
		if party.has(m) and not _party_used.has(m) and _boss_id != "hel_velli_duel":
			avail.append(m)
	if _boss_id == "hel_velli_duel":
		pass  # a duel is a duel · nobody helps
	var pt := Button.new()
	if avail.is_empty():
		pt.text = "  PARTY  \n  " + ("a duel is a duel" if _boss_id == "hel_velli_duel" else "spent") + "  "
		pt.disabled = true
	else:
		pt.text = "  PARTY  \n  " + str(avail.size()) + " can act  "
		pt.pressed.connect(func() -> void: _render_party_menu(avail))
	pt.custom_minimum_size = Vector2(150, 60)
	pt.add_theme_font_size_override("font_size", 15)
	pt.add_theme_color_override("font_color", C_SP)
	menu.add_child(pt)


func _render_working_menu(castable: Array) -> void:
	_clear_bottom_menu()
	var v := VBoxContainer.new()
	v.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	v.offset_left = 60
	v.offset_right = -60
	v.offset_top = -200
	v.offset_bottom = -20
	v.add_theme_constant_override("separation", 3)
	v.name = "BottomMenu"
	add_child(v)
	for w_id in castable:
		var mv: Dictionary = WORKING_MOVES[String(w_id)]
		var btn := Button.new()
		btn.text = "  " + String(mv.get("label", w_id)) + " · " + String(mv.get("note", "")) + "  "
		btn.add_theme_font_size_override("font_size", 14)
		btn.add_theme_color_override("font_color", C_STAR)
		var wid: String = String(w_id)
		btn.pressed.connect(func() -> void: _on_cast_working(wid))
		v.add_child(btn)
	var back := Button.new()
	back.text = "  ← back  "
	back.add_theme_font_size_override("font_size", 14)
	back.pressed.connect(_render)
	v.add_child(back)


func _render_party_menu(avail: Array) -> void:
	_clear_bottom_menu()
	var v := VBoxContainer.new()
	v.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	v.offset_left = 60
	v.offset_right = -60
	v.offset_top = -200
	v.offset_bottom = -20
	v.add_theme_constant_override("separation", 3)
	v.name = "BottomMenu"
	add_child(v)
	var moves := {
		"hel_velli": "Hel Velli · four-armed strike · 18 damage",
		"sara_nai":  "Sara Nai · Kyrindi tone · the boss loses its next turn",
		"rocha":     "Rocha · analyze · reveals the weak point · +50% damage after"
	}
	for m in avail:
		var btn := Button.new()
		btn.text = "  " + String(moves.get(String(m), m)) + "  "
		btn.add_theme_font_size_override("font_size", 14)
		btn.add_theme_color_override("font_color", C_SP)
		var mid: String = String(m)
		btn.pressed.connect(func() -> void: _on_party_act(mid))
		v.add_child(btn)
	var back := Button.new()
	back.text = "  ← back  "
	back.add_theme_font_size_override("font_size", 14)
	back.pressed.connect(_render)
	v.add_child(back)


func _clear_bottom_menu() -> void:
	var bm := get_node_or_null("BottomMenu")
	if bm != null:
		bm.queue_free()


# ─── Actions ────────────────────────────────────────────────────

func _player_damage(base: int) -> int:
	var dmg: int = base + _attack_buff + (_turn % 4)
	if _weakness_revealed:
		dmg = int(round(dmg * 1.5))
	if _counter_open:
		dmg = int(round(dmg * 1.5))
		_counter_open = false
	if _staggered:
		dmg = maxi(1, dmg - 4)
		_staggered = false
	return max(1, dmg)


func _on_attack() -> void:
	var dmg: int = _player_damage(11)
	_boss_hp = max(0, _boss_hp - dmg)
	_log.append("· the pistol answers · " + str(dmg) + " damage")
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("press_hit", 0.7)
	_end_player_turn()


func _on_defend() -> void:
	_shield_turns = max(_shield_turns, 1)
	_player_hp = min(_player_hp_max, _player_hp + 5)
	_log.append("· you find cover and breathe · +5 HP · braced")
	_end_player_turn()


func _on_cast_working(w_id: String) -> void:
	_workings_cast[w_id] = true
	var mv: Dictionary = WORKING_MOVES[w_id]
	var kind: String = String(mv.get("kind", "attack"))
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("basement_rite", 0.7)
	match kind:
		"attack":
			var dmg: int = _player_damage(int(mv.get("power", 20)))
			_boss_hp = max(0, _boss_hp - dmg)
			_log.append("· " + String(mv.get("label", w_id)) + " · " + str(dmg) + " ritual damage")
		"heal":
			_player_hp = min(_player_hp_max, _player_hp + int(mv.get("power", 14)))
			_log.append("· " + String(mv.get("label", w_id)) + " · the hostile weight lifts · +" + str(int(mv.get("power", 14))) + " HP")
		"shield":
			_shield_turns = 2
			_log.append("· " + String(mv.get("label", w_id)) + " · the circle holds around you")
		"buff":
			_attack_buff += 6
			_log.append("· " + String(mv.get("label", w_id)) + " · your hands stop being only hands")
	_end_player_turn()


var _boss_stunned: bool = false

func _on_party_act(member: String) -> void:
	_party_used[member] = true
	match member:
		"hel_velli":
			var dmg: int = 18 + (3 if _weakness_revealed else 0)
			_boss_hp = max(0, _boss_hp - dmg)
			_log.append("· Hel Velli closes · four arms · " + str(dmg) + " damage · he steps back exactly when he said he would")
		"sara_nai":
			_boss_stunned = true
			_log.append("· Sara Nai sings one Kyrindi tone · the room forgets what it was doing · the next turn is yours alone")
		"rocha":
			_weakness_revealed = true
			_log.append("· Rocha, from the doorway, flatly: 'left knee, third rib, and he telegraphs the bind.' · weak point revealed")
	_end_player_turn()


func _end_player_turn() -> void:
	if _boss_hp <= 0:
		_combat_over = true
		_outcome = "victory"
		var nonlethal: bool = bool(_boss.get("nonlethal", false))
		_log.append("· " + ("he lowers all four arms and nods · the duel is answered" if nonlethal else "it is over") + " ·")
		var sfx := get_node_or_null("/root/SFXBank")
		if sfx: sfx.play("win_chord", 0.7)
		_render()
		return
	# Boss turn
	if _boss_stunned:
		_boss_stunned = false
		_log.append("· the tone still hangs · " + String(_boss.get("name", "?")).split(" ·")[0] + " does nothing ·")
	elif _boss_id == "thar_krai_tam":
		_boss_turn_thar()
	else:
		_boss_turn_generic()
	if _player_hp <= 0:
		_combat_over = true
		_outcome = "defeat"
		_log.append("· the floor arrives · hands drag you clear before anything final ·")
		var sfx2 := get_node_or_null("/root/SFXBank")
		if sfx2: sfx2.play("loss_thud", 0.7)
		_render()
		return
	_turn += 1
	_render()


func _boss_turn_generic() -> void:
	# Every foe now shares the telegraph -> DEFEND -> counter rhythm the
	# Thar arena introduced: a wind-up you can read, a heavy blow you can
	# fully SLIP by bracing (DEFEND), and a one-breath opening (x1.5) if
	# you do. DEFEND stops being just +5 HP; on the telegraphed turn it is
	# the whole exchange. Reuses _bind_incoming / _counter_open.
	var sfx := get_node_or_null("/root/SFXBank")
	# Resolve a telegraphed heavy blow.
	if _bind_incoming:
		_bind_incoming = false
		if _shield_turns > 0:
			_shield_turns -= 1
			_counter_open = true
			_log.append("· the heavy blow breaks on your cover, not on you · you slip it · for one breath it is wide open")
			return
		var heavy: int = int(_boss.get("strike", 10)) + 7
		_player_hp = max(0, _player_hp - heavy)
		_log.append("· the blow you didn't brace lands full · " + str(heavy) + " damage · that was the one to read")
		if sfx: sfx.play("hurt", 0.6)
		return
	# Telegraph a heavy blow every third turn.
	if _turn % 3 == 2:
		_bind_incoming = true
		_log.append("· it winds up wide · the big one is coming · brace for it or pay for it")
		var bank := get_node_or_null("/root/SFXBank")
		if bank != null and bank.has_method("rumble"):
			bank.call("rumble", 0.12, 0.22, 0.3)
		return
	# Ordinary strike (DEFEND still halves these).
	var skills: Array = _boss.get("skills", [])
	var raw: int = int(_boss.get("strike", 10)) + (_turn % 3)
	if _shield_turns > 0:
		raw = int(round(raw * 0.5))
		_shield_turns -= 1
	raw = max(1, raw)
	_player_hp = max(0, _player_hp - raw)
	var skill_name: String = String(skills[_turn % max(1, skills.size())]) if not skills.is_empty() else "a strike"
	_log.append("· " + skill_name + " · " + str(raw) + " damage to you")
	if sfx: sfx.play("hurt", 0.5)


func _boss_turn_thar() -> void:
	# The scripted arena · turn 1 open-hand, turn 2 telegraph, turn 3
	# the bind, turn 4 the blade, then a bind cycle with the bellow
	# between.  DEFEND on the telegraph turn slips the bind and opens
	# him up · Rocha's analyze line ("he telegraphs the bind") is a
	# tutorial for this fight, not flavor.
	if _bind_incoming:
		_bind_incoming = false
		if _shield_turns > 0:
			_shield_turns -= 1
			_counter_open = true
			_log.append("· the four-arm bind closes on your cover, not on you · you slip it · for one breath he is wide open")
		else:
			var raw: int = int(_boss.get("strike", 11)) + 6
			_player_hp = max(0, _player_hp - raw)
			_log.append("· the four-arm bind · " + str(raw) + " damage · lifted, held, set down like a point being made")
			var sfx := get_node_or_null("/root/SFXBank")
			if sfx: sfx.play("hurt", 0.6)
		return
	if _turn == 2 or (_blade_drawn and _turn % 3 == 0):
		_bind_incoming = true
		_log.append("· the four lower arms spread wide · the bind is coming · brace for it or pay for it")
		# Telegraph judder · the warning you feel before you read it.
		var bank := get_node_or_null("/root/SFXBank")
		if bank != null and bank.has_method("rumble"):
			bank.call("rumble", 0.12, 0.22, 0.3)
		return
	if not _blade_drawn and _turn >= 3:
		_blade_drawn = true
		_log.append("· the silvered heirloom blade leaves the sheath · unhurried · the courtesy is over")
		return
	if _blade_drawn and _turn % 4 == 0:
		_staggered = true
		_log.append("· overseer's bellow · the gallery rings off the stone · your next strike wavers")
		return
	var raw2: int = int(_boss.get("strike", 11)) + (_turn % 3) + (2 if _blade_drawn else -5)
	if _shield_turns > 0:
		raw2 = int(round(raw2 * 0.5))
		_shield_turns -= 1
	raw2 = max(1, raw2)
	_player_hp = max(0, _player_hp - raw2)
	_log.append("· " + ("one clean silvered arc" if _blade_drawn else "an open-hand cuff · the blade stays sheathed") + " · " + str(raw2) + " damage to you")
	var sfx2 := get_node_or_null("/root/SFXBank")
	if sfx2: sfx2.play("hurt", 0.5)


func _render_outcome() -> void:
	var btn := Button.new()
	btn.text = "  · continue ·  "
	btn.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	btn.offset_left = 500
	btn.offset_right = -500
	btn.offset_top = -160
	btn.offset_bottom = -110
	btn.add_theme_font_size_override("font_size", 16)
	btn.add_theme_color_override("font_color", C_STAR)
	btn.pressed.connect(func() -> void: combat_complete.emit(_boss_id, _outcome))
	add_child(btn)
