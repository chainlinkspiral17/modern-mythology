extends Control
## Fey Faire · Morgan le Fey's fortune reading · specific mini-scene.
##
## Not a negotiation.  When the player enters the fortune-teller's
## tent, Morgan reads back specific facts from the boot
## questionnaire, then draws three specific cards from a specific
## deck of a specific 22-card Major Arcana.
##
## The cards are chosen deterministically from questionnaire answers
## (so each character gets THEIR reading), and each card unlocks a
## specific hook: a keepsake, a court alignment, a hint about the
## finale, or a warning about a specific fey the player has already
## met.
##
## Signals:
##   quit · returns to midway
##   reading_complete(rewards) · host merges rewards
##
## F4-compliant via add_to_group("ui").

signal quit
signal reading_complete(rewards: Dictionary)

# Rocha palette · velvet-dim, candlelit
const C_BG        := Color(0.11, 0.055, 0.098, 1.0)
const C_PANEL     := Color(0.455, 0.157, 0.282, 1.0)
const C_CREAM     := Color(0.957, 0.878, 0.816, 1.0)
const C_ROSE      := Color(0.878, 0.722, 0.753, 1.0)
const C_MAUVE     := Color(0.784, 0.557, 0.643, 1.0)
const C_GOLD      := Color(0.973, 0.784, 0.282, 1.0)
const C_GOLD_DIM  := Color(0.541, 0.361, 0.157, 1.0)
const C_DIM       := Color(0.42, 0.34, 0.30, 1.0)
const C_CANDLE    := Color(0.973, 0.816, 0.518, 1.0)

# 22-card Major Arcana · each has: name, reading, effect
# Cards are pulled deterministically based on questionnaire answers.
const ARCANA: Dictionary = {
	"fool": {
		"name": "THE FOOL",
		"reading": "You are at the beginning.  You already knew that.  The dog barking at your heel is Ondine · she will not stop.  Do not stop for her.",
		"effect": {"seelie_delta": 1}
	},
	"magician": {
		"name": "THE MAGICIAN",
		"reading": "Every tool is already on your table.  The bookstall knows this.  The old woman inside is your reflection at seventy.  She has been waiting to meet you.",
		"effect": {"keepsake": "arcana_magician_card", "seelie_delta": 1}
	},
	"high_priestess": {
		"name": "THE HIGH PRIESTESS",
		"reading": "Titania keeps a specific secret about you.  She knows the name you have not told anyone.  On the night you learn what she keeps, remember: she is on your side.  Everyone here is · in specific ways.",
		"effect": {"seelie_delta": 2, "titania_disposition_delta": 1}
	},
	"empress": {
		"name": "THE EMPRESS",
		"reading": "$LOST_PERSON is closer than you think.  The Green Man knows their name.  You have not asked.  You will.",
		"effect": {"wildfey_delta": 2, "green_man_disposition_delta": 1}
	},
	"emperor": {
		"name": "THE EMPEROR",
		"reading": "Oberon considers your case.  His court will take you if you let it.  You will look good in a dark coat.  You may not be able to take it off after.",
		"effect": {"unseelie_delta": 2, "oberon_disposition_delta": 1}
	},
	"hierophant": {
		"name": "THE HIEROPHANT",
		"reading": "Cricket has selected you for something.  She has not told you what.  If you sit at her counter on Night 6 she will tell you specifically.  Or she will not, and you will still know.",
		"effect": {"cricket_disposition_delta": 2}
	},
	"lovers": {
		"name": "THE LOVERS",
		"reading": "Not what you think.  The first-kiss mirror in your Trailer is the specific one Moth has been editing for three years.  Ask her before you assume.",
		"effect": {"moth_disposition_delta": 1, "keepsake": "arcana_lovers_card"}
	},
	"chariot": {
		"name": "THE CHARIOT",
		"reading": "You will leave the Faire on wheels · a specific truck · seventeen years from your last night.  The specific ending you want does not require this.  The specific ending waiting for you does.",
		"effect": {"wildfey_delta": 2, "warns_stag_antler": true}
	},
	"strength": {
		"name": "STRENGTH",
		"reading": "The Pooka in his rabbit-costume is watching you from the funhouse.  He is not testing you.  He is testing himself against a specific memory.  Be gentle.",
		"effect": {"pooka_disposition_delta": 1}
	},
	"hermit": {
		"name": "THE HERMIT",
		"reading": "Prospero is asleep in the trailer.  He has not woken because he does not need to yet.  When you find his book, put it back on the shelf.  Do not take it out of the trailer.  You will forget why later if you do.",
		"effect": {"prospero_warning": true}
	},
	"wheel_of_fortune": {
		"name": "WHEEL OF FORTUNE",
		"reading": "The wheel at the north end of the midway has a specific sector marked CHILD.  Nobody has landed on it in living memory.  You could.  Do not.",
		"effect": {"erlking_warning": true, "unseelie_delta": 1}
	},
	"justice": {
		"name": "JUSTICE",
		"reading": "Every promise you made will be checked.  Not by them · by you.  Ondine keeps a specific ledger.  Look at it before you leave.",
		"effect": {"ondine_disposition_delta": 1}
	},
	"hanged_man": {
		"name": "THE HANGED MAN",
		"reading": "Between Night 3 and Night 4 there is a specific hour when the Faire is upside down.  If you are in the sleep tent, you will feel it.  You will not remember what you saw.  You will remember that you saw.",
		"effect": {"moth_disposition_delta": 2, "hanged_man_hour_known": true}
	},
	"death": {
		"name": "DEATH",
		"reading": "Not death.  The end of a specific version of yourself.  The version you leave behind is the one that came for a specific reason.  That reason will not survive the Faire.  You will.",
		"effect": {"unseelie_delta": 2}
	},
	"temperance": {
		"name": "TEMPERANCE",
		"reading": "Do not drink Oberon's wine on Night 5.  Or do.  There is a specific consequence for both.  I recommend the wine.  I am not being ironic.",
		"effect": {"unseelie_delta": 1, "oberon_wine_hint": true}
	},
	"devil": {
		"name": "THE DEVIL",
		"reading": "Not the Devil.  Caliban.  He is in a cage because he agreed to be.  He will explain why if you sit for the specific length of time.  Sit.  It is not that long.",
		"effect": {"caliban_hint_known": true, "unseelie_delta": 1}
	},
	"tower": {
		"name": "THE TOWER",
		"reading": "The Big Top will come down on Night 7 whether or not you are inside.  Do not be inside on Night 7.  Or · specifically · do.",
		"effect": {"tower_warning": true, "wildfey_delta": 1}
	},
	"star": {
		"name": "THE STAR",
		"reading": "There is a specific eight-pointed star painted on the underside of the ring-toss booth's roof.  You will not have looked up.  Look up when you are next there.  You are not the first.",
		"effect": {"seelie_delta": 1, "eight_star_visible": true}
	},
	"moon": {
		"name": "THE MOON",
		"reading": "Two moons rise on Night 4.  I know.  There should be one.  There has been one for as long as anyone remembers.  On Night 4 there are two.  Nobody will comment.  Comment.",
		"effect": {"wildfey_delta": 2, "two_moons_night_4": true}
	},
	"sun": {
		"name": "THE SUN",
		"reading": "You will leave the Faire.  You will keep the rose.  Titania will keep her promise.  This is the safest ending I can offer you.  You may not want it.  I understand.",
		"effect": {"seelie_delta": 3, "safest_ending_offered": true}
	},
	"judgement": {
		"name": "JUDGEMENT",
		"reading": "The dead you brought here without meaning to are waking up.  Hamlet's Ghost has been waiting to speak to you specifically.  Visit the grave.  You will not have known there was a grave.",
		"effect": {"hamlets_ghost_warning": true, "unseelie_delta": 1}
	},
	"world": {
		"name": "THE WORLD",
		"reading": "Every fey you have negotiated with, whether you recruited them or not, is watching this reading.  I am not showing off.  I am reminding you: the Faire is one thing.  You have been walking through one large fey for six nights.  Be kind to it.",
		"effect": {"world_awareness": true, "wildfey_delta": 2}
	}
}

var _run_state: Dictionary = {}
var _phase: String = "intro"    # intro | draw1 | draw2 | draw3 | close
var _drawn: Array = []           # 3 card IDs
var _speaker_lbl: Label = null
var _content_lbl: RichTextLabel = null
var _choices_root: Control = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")


func boot(state: Dictionary) -> void:
	_run_state = state.get("run_state", state)
	_drawn = _select_three_cards()
	_build_frame()
	_render_intro()


func _select_three_cards() -> Array:
	# Deterministic pull from questionnaire hashes so the same
	# character gets the same reading across replays of this scene
	# (but different characters get different readings).
	var q: Dictionary = _run_state.get("questionnaire", {})
	var keys: Array = ARCANA.keys()
	var seed_str: String = String(q.get("player_name", "?")) + "|" + String(q.get("lost_person_name", "?")) + "|" + String(q.get("favorite_song", "?"))
	var seed: int = seed_str.hash()
	var picks: Array = []
	# Simple LCG over the seed to pick 3 distinct cards
	var s: int = seed
	while picks.size() < 3:
		s = (s * 1103515245 + 12345) & 0x7fffffff
		var idx: int = int(s % keys.size())
		var card: String = String(keys[idx])
		if not picks.has(card):
			picks.append(card)
	return picks


func _build_frame() -> void:
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# Candlelit velvet-drape stripes on both sides
	for y in range(0, 720, 40):
		var drape_l := ColorRect.new()
		drape_l.color = Color(C_PANEL.r, C_PANEL.g, C_PANEL.b, 0.55)
		drape_l.set_anchors_preset(Control.PRESET_TOP_LEFT)
		drape_l.position = Vector2(20, y)
		drape_l.size = Vector2(30, 20)
		add_child(drape_l)

		var drape_r := ColorRect.new()
		drape_r.color = Color(C_PANEL.r, C_PANEL.g, C_PANEL.b, 0.55)
		drape_r.set_anchors_preset(Control.PRESET_TOP_RIGHT)
		drape_r.position = Vector2(-50, y)
		drape_r.size = Vector2(30, 20)
		add_child(drape_r)

	# Candle flames · top corners
	for cpos in [Vector2(90, 60), Vector2(1170, 60)]:
		var flame := ColorRect.new()
		flame.color = C_CANDLE
		flame.color.a = 0.65
		flame.set_anchors_preset(Control.PRESET_TOP_LEFT)
		flame.position = cpos
		flame.size = Vector2(14, 32)
		add_child(flame)

	# Header
	var header := Label.new()
	header.text = "· MORGAN LE FEY · FORTUNE-TELLER ·"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 14)
	header.add_theme_color_override("font_color", C_GOLD)
	header.set_anchors_preset(Control.PRESET_TOP_WIDE)
	header.offset_top = 40
	header.offset_bottom = 68
	add_child(header)

	# HeroImage · Morgan at her table with three cards, top-right of the tent
	var hero := HeroImage.new()
	if hero.load_from("res://resources/games/vol7/fey_faire/hero_images/fortune_teller.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(220, 124))
		tex_rect.set_anchors_preset(Control.PRESET_TOP_RIGHT)
		tex_rect.position = Vector2(-240, 76)
		tex_rect.size = Vector2(220, 124)
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		add_child(tex_rect)

	# Panel
	var panel := ColorRect.new()
	panel.color = C_PANEL
	panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	panel.offset_left = -420
	panel.offset_right = 420
	panel.offset_top = -220
	panel.offset_bottom = 260
	add_child(panel)


func _clear_narrative() -> void:
	if _speaker_lbl != null and is_instance_valid(_speaker_lbl):
		_speaker_lbl.queue_free()
	if _content_lbl != null and is_instance_valid(_content_lbl):
		_content_lbl.queue_free()
	if _choices_root != null and is_instance_valid(_choices_root):
		_choices_root.queue_free()
	_speaker_lbl = null
	_content_lbl = null
	_choices_root = null


func _write(speaker: String, text: String) -> void:
	_clear_narrative()
	_speaker_lbl = Label.new()
	_speaker_lbl.text = "· " + speaker.to_upper() + " ·"
	_speaker_lbl.set_anchors_preset(Control.PRESET_CENTER)
	_speaker_lbl.offset_left = -400
	_speaker_lbl.offset_right = 400
	_speaker_lbl.offset_top = -200
	_speaker_lbl.offset_bottom = -178
	_speaker_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_speaker_lbl.add_theme_font_size_override("font_size", 11)
	_speaker_lbl.add_theme_color_override("font_color", C_GOLD_DIM)
	add_child(_speaker_lbl)

	_content_lbl = RichTextLabel.new()
	_content_lbl.bbcode_enabled = false
	_content_lbl.fit_content = true
	_content_lbl.set_anchors_preset(Control.PRESET_CENTER)
	_content_lbl.offset_left = -400
	_content_lbl.offset_right = 400
	_content_lbl.offset_top = -170
	_content_lbl.offset_bottom = 180
	_content_lbl.text = _substitute(text)
	_content_lbl.add_theme_font_size_override("normal_font_size", 12)
	_content_lbl.add_theme_color_override("default_color", C_CREAM)
	add_child(_content_lbl)


func _substitute(text: String) -> String:
	var q: Dictionary = _run_state.get("questionnaire", {})
	var s := text
	s = s.replace("$PLAYER_NAME", String(q.get("player_name", "you")))
	s = s.replace("$LOST_PERSON", String(q.get("lost_person_name", "someone")))
	s = s.replace("$CITY", String(q.get("city_you_live_in", "your town")))
	s = s.replace("$FAVORITE_SONG", String(q.get("favorite_song", "a song")))
	return s


func _render_advance(label: String, cb: Callable) -> void:
	_choices_root = Control.new()
	_choices_root.set_anchors_preset(Control.PRESET_CENTER)
	_choices_root.offset_left = -140
	_choices_root.offset_right = 140
	_choices_root.offset_top = 200
	_choices_root.offset_bottom = 260
	add_child(_choices_root)

	var btn := Button.new()
	btn.text = label
	btn.add_theme_font_size_override("font_size", 12)
	btn.add_theme_color_override("font_color", C_GOLD)
	btn.pressed.connect(cb)
	btn.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_choices_root.add_child(btn)


func _render_intro() -> void:
	_phase = "intro"
	var q: Dictionary = _run_state.get("questionnaire", {})
	var name: String = String(q.get("player_name", "friend"))
	var song: String = String(q.get("favorite_song", "a song you have not told anyone about"))
	var seen: Array = _run_state.get("endings_seen", [])
	var recall: String = ""
	if not seen.is_empty():
		var last: String = String(seen[seen.size() - 1]).replace("_", " ").to_upper()
		recall = "\n\nAlso: last time, you left with " + last + ".  I am not supposed to remember across summers.  Neither are you.  Here we are."
	_write(
		"morgan le fey",
		"'Sit.  I don't need your palm.  I already know your name is $PLAYER_NAME.  I already know the song stuck in your head is · " + song + " · and I already know it will be stuck there for two more days.\n\nThere is a specific deck between us.  I have already shuffled it.  I have already selected your three cards.  You are not choosing.  You are looking." + recall + "\n\nMay I turn the first?'"
	)
	_render_advance("  · yes · turn the first card ·  ", func() -> void: _render_card(0))


func _render_card(idx: int) -> void:
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("card_flip", 0.7)
	if idx >= _drawn.size():
		_render_close()
		return
	_phase = "draw" + str(idx + 1)
	var card_id: String = String(_drawn[idx])
	var card: Dictionary = ARCANA.get(card_id, {})
	var position_word: String
	match idx:
		0: position_word = "past"
		1: position_word = "present"
		_: position_word = "future"
	_write(
		"card " + str(idx + 1) + " · " + position_word,
		"· " + String(card.get("name", "?")) + " ·\n\n" + String(card.get("reading", ""))
	)
	if idx < _drawn.size() - 1:
		_render_advance("  · turn the next card ·  ", func() -> void: _render_card(idx + 1))
	else:
		_render_advance("  · thank her ·  ", func() -> void: _render_close())


func _render_close() -> void:
	_phase = "close"
	_write(
		"morgan le fey · closing",
		"'Go.  Do not tip me · Ondine handles the counting.  Come back before Night 6 and I will tell you which of these three was the specific true one.  If you cannot come back before Night 6 · they were all three specifically true.  This is how the cards work.  This is how the Faire works.  Both are true.'"
	)
	_render_advance("  · walk out ·  ", func() -> void: _apply_and_finish())


func _apply_and_finish() -> void:
	var rewards: Dictionary = {"cards_drawn": _drawn}
	for card_id in _drawn:
		var card: Dictionary = ARCANA.get(String(card_id), {})
		var effect: Dictionary = card.get("effect", {})
		for k in effect.keys():
			# Merge into rewards; host applies deltas
			if String(k).ends_with("_delta"):
				var cur_delta: int = int(rewards.get(k, 0))
				rewards[k] = cur_delta + int(effect[k])
			else:
				rewards[String(k)] = effect[k]
	# Record that this run has had its fortune read
	rewards["fortune_read"] = true
	rewards["cards_shown"] = _drawn
	reading_complete.emit(rewards)


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			quit.emit()
			get_viewport().set_input_as_handled()
