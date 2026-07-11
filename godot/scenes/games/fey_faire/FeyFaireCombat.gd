extends Control
## Fey Faire · combat · text-forward turn-based scaffold.
##
## Combat is NOT the default resolution path in Fey Faire · dialogue
## and RECITE are.  Combat is what happens when the player has
## chosen "attack" from a negotiation OR when a fey specifically
## initiates combat as a narrative beat.
##
## Turn order:
##   1. Player picks an action (ATTACK · DEFEND · RECITE · PARLEY)
##   2. Fey responds (uses one of its skills OR attacks)
##   3. Turn counter increments · log advances
##
## Weakness/resistance:
##   damage_type WEAK vs fey.weakness → ×1.5 damage
##   damage_type MATCHES fey.resistance → ×0.5 damage
##
## Ending states:
##   VICTORY · fey_hp <= 0 · fey is subdued (recruit-forced OR
##            defeated depending on Court alignment; scaffold
##            treats it as a defeat that opens the checkpoint)
##   LOSS    · player_hp <= 0 · one memory lost · back to Gate
##   PARLEY  · player converted combat back to negotiation · returns
##            with dispositional penalty
##
## Signals:
##   combat_complete(fey_id, outcome, mutations)
##   quit
##
## F4-compliant via add_to_group("ui").

signal combat_complete(fey_id: String, outcome: String, mutations: Dictionary)
signal quit

const FEYS_PATH   := "res://resources/games/vol7/fey_faire/feys.json"
const QUOTES_PATH := "res://resources/games/vol7/fey_faire/quotes.json"

# Quotes granted by Big Top shows / mirrors · not in quotes.json ·
# display text lives here so RECITE never prints a raw id.
const EXTRA_QUOTES: Dictionary = {
	"midsummer_shadows": {"text": "If we shadows have offended, think but this, and all is mended.", "source": "midsummer"},
	"tempest_seachange": {"text": "Doth suffer a sea-change into something rich and strange.", "source": "tempest"},
	"hamlet_remember":   {"text": "Remember me.", "source": "hamlet"},
	"macbeth_thumbs":    {"text": "By the pricking of my thumbs, something wicked this way comes.", "source": "macbeth"},
	"lear_never":        {"text": "Never, never, never, never, never.", "source": "lear"},
	"your_name_seventh": {"text": "Six nights we have given you.  The seventh is yours.", "source": "your_name"},
	"kelpie_verse":      {"text": "Full fathom five thy father lies · a verse nobody else has heard.", "source": "tempest"}
}

# Rocha palette · combat is cooler + high-contrast
const C_BG        := Color(0.098, 0.055, 0.114, 1.0)   # deeper black-plum
const C_PANEL     := Color(0.455, 0.157, 0.282, 1.0)
const C_PANEL_DIM := Color(0.24, 0.09, 0.16, 1.0)
const C_CREAM     := Color(0.957, 0.878, 0.816, 1.0)
const C_ROSE      := Color(0.878, 0.722, 0.753, 1.0)
const C_MAUVE     := Color(0.87, 0.68, 0.76, 1.0)
const C_GOLD      := Color(0.973, 0.784, 0.282, 1.0)
const C_GOLD_DIM  := Color(0.72, 0.52, 0.26, 1.0)
const C_DIM       := Color(0.62, 0.53, 0.47, 1.0)
const C_HP_GOOD   := Color(0.62, 0.82, 0.55, 1.0)
const C_HP_MID    := Color(0.973, 0.784, 0.282, 1.0)
const C_HP_LOW    := Color(0.878, 0.361, 0.361, 1.0)
const C_SP        := Color(0.55, 0.72, 0.94, 1.0)

var _fey_id: String = ""
var _fey: Dictionary = {}
var _run_state: Dictionary = {}
var _quotes_by_id: Dictionary = {}

# Combat state
var _player_hp: int = 60
var _player_hp_max: int = 60
var _player_sp: int = 20
var _player_sp_max: int = 20
var _player_defending: bool = false
var _fey_hp: int = 40
var _fey_hp_max: int = 40
var _turn: int = 1
var _log: Array = []       # array of Strings
var _combat_over: bool = false


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")


func boot(state: Dictionary) -> void:
	var payload: Dictionary = state
	_fey_id = String(payload.get("fey_id", ""))
	_run_state = payload.get("run_state", {})
	_load_fey()
	# Scale player HP based on lost memories (harder as they wear thin)
	var lost: int = int(_run_state.get("memories_lost", 0))
	_player_hp_max = max(20, 60 - lost * 6)
	_player_hp = _player_hp_max
	_player_sp = _player_sp_max
	# Enemy stats from fey
	var stats: Dictionary = _fey.get("stats", {})
	_fey_hp_max = int(stats.get("hp", 40))
	_fey_hp = _fey_hp_max
	_log = ["· " + _fey_str("name", "fey").to_upper() + " will not be reasoned with.  They have chosen a specific shape."]
	_render()


func _load_fey() -> void:
	if not FileAccess.file_exists(FEYS_PATH): return
	var f := FileAccess.open(FEYS_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		for entry_v in (parsed as Dictionary).get("feys", []):
			var entry: Dictionary = entry_v
			if String(entry.get("id", "")) == _fey_id:
				_fey = entry
				break
	# Quote catalog · for RECITE text + affinity matching
	if not FileAccess.file_exists(QUOTES_PATH): return
	var qf := FileAccess.open(QUOTES_PATH, FileAccess.READ)
	var qparsed: Variant = JSON.parse_string(qf.get_as_text())
	qf.close()
	if qparsed is Dictionary:
		for q_v in (qparsed as Dictionary).get("quotes", []):
			var q: Dictionary = q_v
			_quotes_by_id[String(q.get("id", ""))] = q


func _clear_children() -> void:
	for c in get_children():
		c.queue_free()


func _render() -> void:
	_clear_children()

	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# Tent-stripe top edge · dim in combat
	for x in range(60, 1280, 90):
		var stripe := ColorRect.new()
		stripe.color = C_PANEL_DIM
		stripe.set_anchors_preset(Control.PRESET_TOP_LEFT)
		stripe.position = Vector2(x, 0)
		stripe.size = Vector2(6, 40)
		add_child(stripe)

	# Header
	var header := Label.new()
	header.text = "· COMBAT · " + _fey_str("name", "?").to_upper() + " ·"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 18)
	header.add_theme_color_override("font_color", C_GOLD)
	header.set_anchors_preset(Control.PRESET_TOP_WIDE)
	header.offset_top = 44
	header.offset_bottom = 66
	add_child(header)

	# Left half · fey status
	_render_fey_status()

	# Right half · player status
	_render_player_status()

	# Center · log
	_render_log()

	# Bottom · actions or outcome
	if _combat_over:
		_render_outcome_buttons()
	else:
		_render_action_menu()


func _render_fey_status() -> void:
	var panel := ColorRect.new()
	panel.color = C_PANEL
	panel.set_anchors_preset(Control.PRESET_TOP_LEFT)
	panel.position = Vector2(60, 90)
	panel.size = Vector2(360, 140)
	add_child(panel)

	# Portrait · the glamour is thinner in combat but they keep the face
	var portrait_rect := TextureRect.new()
	portrait_rect.texture = FeyPortrait.texture(_fey, Vector2i(80, 100))
	portrait_rect.set_anchors_preset(Control.PRESET_TOP_LEFT)
	portrait_rect.position = Vector2(340, 100)
	portrait_rect.size = Vector2(80, 100)
	portrait_rect.stretch_mode = TextureRect.STRETCH_KEEP
	add_child(portrait_rect)

	var name_lbl := Label.new()
	name_lbl.text = _fey_str("name", "?")
	name_lbl.add_theme_font_size_override("font_size", 17)
	name_lbl.add_theme_color_override("font_color", C_GOLD)
	name_lbl.set_anchors_preset(Control.PRESET_TOP_LEFT)
	name_lbl.position = Vector2(80, 100)
	add_child(name_lbl)

	var court_lbl := Label.new()
	court_lbl.text = "· " + _fey_str("court", "?") + " · tier " + str(int(_fey.get("tier", 1))) + " ·"
	court_lbl.add_theme_font_size_override("font_size", 14)
	court_lbl.add_theme_color_override("font_color", C_ROSE)
	court_lbl.set_anchors_preset(Control.PRESET_TOP_LEFT)
	court_lbl.position = Vector2(80, 118)
	add_child(court_lbl)

	var hp_lbl := Label.new()
	hp_lbl.text = "HP  " + str(_fey_hp) + " / " + str(_fey_hp_max)
	hp_lbl.add_theme_font_size_override("font_size", 15)
	hp_lbl.add_theme_color_override("font_color", _hp_color(_fey_hp, _fey_hp_max))
	hp_lbl.set_anchors_preset(Control.PRESET_TOP_LEFT)
	hp_lbl.position = Vector2(80, 140)
	add_child(hp_lbl)

	# HP bar
	var bar_bg := ColorRect.new()
	bar_bg.color = C_PANEL_DIM
	bar_bg.set_anchors_preset(Control.PRESET_TOP_LEFT)
	bar_bg.position = Vector2(80, 160)
	bar_bg.size = Vector2(320, 8)
	add_child(bar_bg)

	var bar := ColorRect.new()
	bar.color = _hp_color(_fey_hp, _fey_hp_max)
	bar.set_anchors_preset(Control.PRESET_TOP_LEFT)
	bar.position = Vector2(80, 160)
	var frac_e: float = 0.0
	if _fey_hp_max > 0:
		frac_e = float(_fey_hp) / float(_fey_hp_max)
	bar.size = Vector2(320.0 * clamp(frac_e, 0.0, 1.0), 8)
	add_child(bar)

	var elem_lbl := Label.new()
	var weak_str: String = _fey_str("weakness", "?")
	var res_str: String  = _fey_str("resistance", "?")
	elem_lbl.text = "damage " + _fey_str("damage_type", "?") + " · weak " + weak_str + " · resists " + res_str
	elem_lbl.add_theme_font_size_override("font_size", 13)
	elem_lbl.add_theme_color_override("font_color", C_GOLD_DIM)
	elem_lbl.set_anchors_preset(Control.PRESET_TOP_LEFT)
	elem_lbl.position = Vector2(80, 178)
	add_child(elem_lbl)

	var true_name_known: bool = _player_knows_true_name()
	var tn_lbl := Label.new()
	if true_name_known:
		tn_lbl.text = "· you know their true name · combat harder for them ·"
		tn_lbl.add_theme_color_override("font_color", C_GOLD)
	else:
		tn_lbl.text = "· true name unknown ·"
		tn_lbl.add_theme_color_override("font_color", C_DIM)
	tn_lbl.add_theme_font_size_override("font_size", 13)
	tn_lbl.set_anchors_preset(Control.PRESET_TOP_LEFT)
	tn_lbl.position = Vector2(80, 198)
	add_child(tn_lbl)


func _render_player_status() -> void:
	var panel := ColorRect.new()
	panel.color = C_PANEL
	panel.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	panel.position = Vector2(-420, 90)
	panel.size = Vector2(360, 140)
	add_child(panel)

	var name_lbl := Label.new()
	name_lbl.text = String(_run_state.get("questionnaire", {}).get("player_name", "You"))
	name_lbl.add_theme_font_size_override("font_size", 17)
	name_lbl.add_theme_color_override("font_color", C_GOLD)
	name_lbl.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	name_lbl.position = Vector2(-400, 100)
	add_child(name_lbl)

	var alignment_lbl := Label.new()
	var seelie: int = int(_run_state.get("court_seelie", 0))
	var unseelie: int = int(_run_state.get("court_unseelie", 0))
	var wildfey: int = int(_run_state.get("court_wildfey", 0))
	alignment_lbl.text = "S:" + str(seelie) + " · U:" + str(unseelie) + " · W:" + str(wildfey)
	alignment_lbl.add_theme_font_size_override("font_size", 14)
	alignment_lbl.add_theme_color_override("font_color", C_ROSE)
	alignment_lbl.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	alignment_lbl.position = Vector2(-400, 118)
	add_child(alignment_lbl)

	var hp_lbl := Label.new()
	hp_lbl.text = "HP  " + str(_player_hp) + " / " + str(_player_hp_max)
	hp_lbl.add_theme_font_size_override("font_size", 15)
	hp_lbl.add_theme_color_override("font_color", _hp_color(_player_hp, _player_hp_max))
	hp_lbl.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	hp_lbl.position = Vector2(-400, 140)
	add_child(hp_lbl)

	# HP bar
	var bar_bg := ColorRect.new()
	bar_bg.color = C_PANEL_DIM
	bar_bg.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	bar_bg.position = Vector2(-400, 160)
	bar_bg.size = Vector2(320, 8)
	add_child(bar_bg)

	var bar := ColorRect.new()
	bar.color = _hp_color(_player_hp, _player_hp_max)
	bar.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	bar.position = Vector2(-400, 160)
	var frac_p: float = 0.0
	if _player_hp_max > 0:
		frac_p = float(_player_hp) / float(_player_hp_max)
	bar.size = Vector2(320.0 * clamp(frac_p, 0.0, 1.0), 8)
	add_child(bar)

	var sp_lbl := Label.new()
	sp_lbl.text = "SP  " + str(_player_sp) + " / " + str(_player_sp_max)
	sp_lbl.add_theme_font_size_override("font_size", 14)
	sp_lbl.add_theme_color_override("font_color", C_SP)
	sp_lbl.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	sp_lbl.position = Vector2(-400, 178)
	add_child(sp_lbl)

	var mem_lbl := Label.new()
	var lost: int = int(_run_state.get("memories_lost", 0))
	mem_lbl.text = "· memories lost: " + str(lost) + " / 6 ·"
	mem_lbl.add_theme_font_size_override("font_size", 13)
	mem_lbl.add_theme_color_override("font_color", C_DIM)
	mem_lbl.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	mem_lbl.position = Vector2(-400, 198)
	add_child(mem_lbl)


func _render_log() -> void:
	var log_panel := ColorRect.new()
	log_panel.color = C_PANEL_DIM
	log_panel.set_anchors_preset(Control.PRESET_CENTER)
	log_panel.offset_left = -420
	log_panel.offset_right = 420
	log_panel.offset_top = -20
	log_panel.offset_bottom = 140
	add_child(log_panel)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -400
	v.offset_right = 400
	v.offset_top = -10
	v.offset_bottom = 130
	v.add_theme_constant_override("separation", 2)
	add_child(v)

	var turn_lbl := Label.new()
	turn_lbl.text = "· TURN " + str(_turn) + " ·"
	turn_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	turn_lbl.add_theme_font_size_override("font_size", 14)
	turn_lbl.add_theme_color_override("font_color", C_GOLD_DIM)
	v.add_child(turn_lbl)

	# Print last 6 log entries
	var start: int = max(0, _log.size() - 6)
	for i in range(start, _log.size()):
		var entry_lbl := RichTextLabel.new()
		entry_lbl.bbcode_enabled = false
		entry_lbl.fit_content = true
		entry_lbl.text = String(_log[i])
		entry_lbl.add_theme_font_size_override("normal_font_size", 14)
		entry_lbl.add_theme_color_override("default_color", C_CREAM)
		entry_lbl.custom_minimum_size = Vector2(760, 14)
		v.add_child(entry_lbl)


func _render_action_menu() -> void:
	var menu := HBoxContainer.new()
	menu.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	menu.offset_left = 60
	menu.offset_right = -60
	menu.offset_top = -100
	menu.offset_bottom = -20
	menu.alignment = BoxContainer.ALIGNMENT_CENTER
	menu.add_theme_constant_override("separation", 12)
	add_child(menu)

	var atk_btn := Button.new()
	atk_btn.text = "  ATTACK  "
	atk_btn.custom_minimum_size = Vector2(140, 60)
	atk_btn.add_theme_font_size_override("font_size", 16)
	atk_btn.add_theme_color_override("font_color", C_GOLD)
	atk_btn.pressed.connect(_on_attack_pressed)
	menu.add_child(atk_btn)

	var def_btn := Button.new()
	def_btn.text = "  DEFEND  "
	def_btn.custom_minimum_size = Vector2(140, 60)
	def_btn.add_theme_font_size_override("font_size", 16)
	def_btn.add_theme_color_override("font_color", C_ROSE)
	def_btn.pressed.connect(_on_defend_pressed)
	menu.add_child(def_btn)

	var recite_btn := Button.new()
	var quotes: Array = _run_state.get("unlocked_quotes", [])
	if quotes.size() > 0:
		recite_btn.text = "  RECITE  \n  (" + str(quotes.size()) + " known)  "
		recite_btn.pressed.connect(_on_recite_pressed)
	else:
		recite_btn.text = "  RECITE  \n  (no lines yet · attend a show)  "
		recite_btn.disabled = true
	recite_btn.custom_minimum_size = Vector2(180, 60)
	recite_btn.add_theme_font_size_override("font_size", 15)
	recite_btn.add_theme_color_override("font_color", C_MAUVE)
	menu.add_child(recite_btn)

	var parley_btn := Button.new()
	if _fey_hp * 2 < _fey_hp_max:
		parley_btn.text = "  PARLEY  \n  (they might listen)  "
		parley_btn.pressed.connect(_on_parley_pressed)
	else:
		parley_btn.text = "  PARLEY  \n  (they are not yet listening)  "
		parley_btn.disabled = true
	parley_btn.custom_minimum_size = Vector2(180, 60)
	parley_btn.add_theme_font_size_override("font_size", 15)
	parley_btn.add_theme_color_override("font_color", C_GOLD_DIM)
	menu.add_child(parley_btn)


func _render_outcome_buttons() -> void:
	var v := VBoxContainer.new()
	v.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	v.offset_left = 60
	v.offset_right = -60
	v.offset_top = -100
	v.offset_bottom = -20
	v.alignment = BoxContainer.ALIGNMENT_CENTER
	v.add_theme_constant_override("separation", 8)
	add_child(v)

	var btn := Button.new()
	btn.text = "  continue  →  "
	btn.custom_minimum_size = Vector2(200, 48)
	btn.add_theme_font_size_override("font_size", 16)
	btn.add_theme_color_override("font_color", C_GOLD)
	btn.pressed.connect(_emit_outcome)
	v.add_child(btn)


# ─── Actions ────────────────────────────────────────────────────────

func _on_attack_pressed() -> void:
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("press_hit", 0.7)
	_player_defending = false
	var base: int = 12 + int(_fey.get("tier", 1)) * 2
	# True name bonus
	if _player_knows_true_name():
		base = int(round(base * 1.4))
	# Random variance ± 3
	var dmg: int = base + (_turn % 5) - 2
	dmg = max(1, dmg)
	_fey_hp = max(0, _fey_hp - dmg)
	_log.append("· you strike · " + str(dmg) + " damage")
	_end_of_player_turn()


func _on_defend_pressed() -> void:
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("card_place", 0.6)
	_player_defending = true
	# Small SP regen
	_player_sp = min(_player_sp_max, _player_sp + 3)
	_log.append("· you set your feet · +3 SP · incoming damage halved next turn")
	_end_of_player_turn()


func _on_recite_pressed() -> void:
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("page_turn", 0.6)
	_player_defending = false
	# Reciting a Shakespeare line: causes wavering.  Text and affinity
	# come from quotes.json; Big Top playbill quotes from EXTRA_QUOTES.
	var quotes: Array = _run_state.get("unlocked_quotes", [])
	var chosen_id: String = String(quotes[_turn % max(1, quotes.size())])
	var display: String = chosen_id.capitalize()
	var affinity_hit := false
	var backfire := false
	if _quotes_by_id.has(chosen_id):
		var q: Dictionary = _quotes_by_id[chosen_id]
		display = String(q.get("text", display))
		var court: String = _fey_str("court", "")
		var aff: Array = q.get("affinities", [])
		var anti: Array = q.get("anti_affinities", [])
		affinity_hit = aff.has(_fey_id) or aff.has(court)
		backfire = anti.has(_fey_id) or anti.has(court)
	elif EXTRA_QUOTES.has(chosen_id):
		var eq: Dictionary = EXTRA_QUOTES[chosen_id]
		display = String(eq.get("text", display))
		var src: String = _fey_str("shakespeare_source", "")
		affinity_hit = src != "" and _source_root(src) == String(eq.get("source", ""))
	var fey_name: String = _fey_str("name", "they")
	if backfire:
		var word_dmg: int = 4
		_player_hp = max(0, _player_hp - word_dmg)
		_log.append("· you recite \"" + display + "\" · " + fey_name + " MISQUOTES it back at you, corrected · " + str(word_dmg) + " Word damage to you")
	elif affinity_hit:
		var wavering: int = 18
		_fey_hp = max(0, _fey_hp - wavering)
		_log.append("· you recite \"" + display + "\" · " + fey_name + " wavers · the line is THEIRS · " + str(wavering) + " to their composure")
	else:
		var wavering: int = 6
		_fey_hp = max(0, _fey_hp - wavering)
		_log.append("· you recite \"" + display + "\" · " + fey_name + " looks at you differently · " + str(wavering) + " to their composure")
	_end_of_player_turn()


func _on_parley_pressed() -> void:
	# End combat via parley · returns to negotiation with disposition penalty
	_combat_over = true
	_log.append("· you lower your weapon · '" + _fey_str("name", "friend") + " · please · we can still talk'")
	# emit at next continue
	call_deferred("_render")


func _end_of_player_turn() -> void:
	if _fey_hp <= 0:
		_combat_over = true
		_log.append("· " + _fey_str("name", "they") + " goes still · their manifestation dissolves · you have won")
		call_deferred("_render")
		return
	# Fey turn
	_fey_turn()
	if _player_hp <= 0:
		_combat_over = true
		_log.append("· you fall · the tent fades · you have lost a memory")
		call_deferred("_render")
		return
	_turn += 1
	_render()


func _fey_turn() -> void:
	# The fey uses a skill drawn from its list, or a bare strike.
	var skills: Array = _fey.get("skills", [])
	var stats: Dictionary = _fey.get("stats", {})
	var strike_stat: int = int(stats.get("strike", 6))
	var raw: int = 8 + strike_stat + int(_fey.get("tier", 1)) * 2
	# Random variance
	var dmg: int = raw + (_turn % 4) - 1
	if _player_defending:
		dmg = int(round(dmg * 0.5))
	dmg = max(1, dmg)
	_player_hp = max(0, _player_hp - dmg)
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("hurt", 0.5)
	var skill_str: String = ""
	if skills.size() > 0:
		skill_str = String(skills[_turn % skills.size()]).replace("_", " ")
	if skill_str != "":
		_log.append("· " + _fey_str("name", "they") + " · " + skill_str + " · " + str(dmg) + " damage")
	else:
		_log.append("· " + _fey_str("name", "they") + " strikes · " + str(dmg) + " damage")


# ─── Helpers ────────────────────────────────────────────────────────

func _hp_color(cur: int, cur_max: int) -> Color:
	if cur_max <= 0: return C_HP_LOW
	var frac: float = float(cur) / float(cur_max)
	if frac > 0.66: return C_HP_GOOD
	if frac > 0.33: return C_HP_MID
	return C_HP_LOW


func _player_knows_true_name() -> bool:
	var known: Array = _run_state.get("known_true_names", [])
	return known.has(_fey_id)


func _source_root(src: String) -> String:
	# Reduce "midsummer_nights_dream" or "MIDSUMMER" to a lowercase root
	var s := src.to_lower()
	if s.find("midsummer") >= 0: return "midsummer"
	if s.find("tempest") >= 0: return "tempest"
	if s.find("hamlet") >= 0: return "hamlet"
	if s.find("macbeth") >= 0: return "macbeth"
	if s.find("lear") >= 0: return "lear"
	if s.find("cymbeline") >= 0: return "cymbeline"
	return s


func _emit_outcome() -> void:
	var muts: Dictionary = {}
	var outcome := "victory"
	if _fey_hp <= 0:
		outcome = "victory"
		# The vanquished fey opens their checkpoint but does NOT recruit;
		# they will bear a grudge if the player re-approaches.
		muts["forced_recruit"] = false
		muts["fey_vanquished"] = true
		muts["court_unseelie_delta"] = 1
	elif _player_hp <= 0:
		outcome = "loss"
		muts["memories_lost_delta"] = 1
		muts["player_hp_restore"] = true
	else:
		# Parley
		outcome = "parley"
		muts["parley_penalty"] = true
	combat_complete.emit(_fey_id, outcome, muts)


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			# Escape = concede
			_combat_over = true
			_player_hp = 0
			_log.append("· you turn to leave · they do not let you · you fall")
			_render()
			get_viewport().set_input_as_handled()


# Null-safe string field read — feys.json carries explicit nulls
# (favorite_play, shakespeare_source), and Dictionary.get() returns
# the stored null instead of the default when the key exists.
# String(null) is an invalid constructor call and crashed the
# negotiation view on any fey without a favorite play.
func _fey_str(key: String, default: String = "") -> String:
	var v = _fey.get(key, default)
	return v if v is String else default
