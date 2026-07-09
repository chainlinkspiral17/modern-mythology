extends Control
## Earthman Chronicles · Chapter 2 · The Approach · Parsa +
## Hel Velli + tribal duel · scaffold pass.
##
## Follows Chapter 1's beat-sequence pattern.  Player has just
## fallen through the Working; wakes on Parsa.  Beats cover:
## the wasteland arrival, first Delvanni meeting (Hel Velli),
## the tribal circle, and the duel with Murg of the Kel-Karai
## with the specific briefcase joke option.
##
## Ends with Hel Velli joining the party.
##
## Emits `chapter_complete(state)` on end · state now includes
## hel_velli in party_members, disposition scores, and duel
## outcome.
##
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal chapter_complete(state: Dictionary)

# Astro-Cortex palette
const C_BG           := Color(0.486, 0.220, 0.125, 1.0)   # rust red · Parsa daytime
const C_BG_DUSK      := Color(0.235, 0.157, 0.220, 1.0)   # Parsa dusk
const C_CORTEX       := Color(0.345, 0.188, 0.376, 1.0)
const C_AMBER        := Color(0.784, 0.376, 0.125, 1.0)
const C_GREEN        := Color(0.0, 0.753, 0.376, 1.0)
const C_RED          := Color(0.753, 0.125, 0.125, 1.0)
const C_CREAM        := Color(0.912, 0.816, 0.565, 1.0)
const C_WHITE        := Color(0.941, 0.941, 0.941, 1.0)
const C_GRAY         := Color(0.282, 0.282, 0.314, 1.0)
const C_DIM          := Color(0.545, 0.463, 0.302, 1.0)
const C_SAND         := Color(0.784, 0.541, 0.298, 1.0)

var _run_state: Dictionary = {}
var _beat_idx: int = 0
var _content_lbl: RichTextLabel = null
var _speaker_lbl: Label = null
var _choices_root: Control = null

var _beats: Array = [
	{
		"speaker": "· PARSA · UNKNOWN HOUR · TWO MOONS ·",
		"text": "You wake on rust-red sand.  You are lying on your back.  Two moons are overhead · one bright, one visibly dying.  The light between them casts everything a specific violet-red.\n\nYou do not know how long you have been unconscious.  You do not know how far you have fallen.  You have specific bruises on your left elbow and your right shoulder."
	},
	{
		"speaker": "· BEAT ·",
		"text": "You stand up.  Slowly.\n\nAround you: a dune-field stretching to a specific low ridge in the west.  In the east, a specific rock formation you would call an 'inselberg' if you had time to name things.  You do not have time to name things.  You have specific concerns:\n\n· you do not know where Rafaton is (or if he came through with you)\n· you do not have water\n· you do not have your notebook\n· you do have your rocket-fuel pistol\n\nThe last one surprises you.  You do not remember taking it into the ritual."
	},
	{
		"speaker": "· BEAT ·",
		"text": "You walk toward the ridge.  It seems like the best available choice."
	},
	{
		"speaker": "· ONE HOUR LATER · THE RIDGE ·",
		"text": "At the top of the ridge you see, in the near distance, a specific tall figure walking toward you.\n\nHe is · not a person shape you know.\n\nHe is tall.  Very tall.  He has four arms."
	},
	{
		"speaker": "HEL VELLI",
		"text": "The four-armed figure stops at a specific respectful distance and raises his upper hands, palms out.  His lower hands remain at his sides.\n\n'Small.  Four-limbed.  Not from here.'\n\nHis voice is a specific low tenor.  The words are not English but you understand them.  You will realize later that you did not understand them at the time · you inferred them.  You are correctly inferring."
	},
	{
		"speaker": "· CHOICE · how do you greet him? ·",
		"type": "choice",
		"choices": [
			{
				"id": "greet_respectful",
				"label": "  Raise both your hands to match his.  ",
				"note": "Match his salute-of-tribal-inquiry as best a two-armed being can · earns respect gradually",
				"sets": {"hel_velli_disposition_delta": 1}
			},
			{
				"id": "greet_confident",
				"label": "  Speak first.  'I mean no harm.  Where am I?'  ",
				"note": "Presumptuous by Delvanni standards · asks a question before returning the salute",
				"sets": {"hel_velli_disposition_delta": -1}
			},
			{
				"id": "greet_reach_pistol",
				"label": "  Keep your hand near your pistol.  Do not raise your hands.  ",
				"note": "Cautious · a specific insult · Hel Velli will remember",
				"sets": {"hel_velli_disposition_delta": -3, "started_hostile_with_hel_velli": true}
			}
		]
	},
	{
		"speaker": "HEL VELLI",
		"text": "He considers you for a specific length of time.  Then he speaks a specific phrase that translates (approximately) to:\n\n'Come.  My tribe is one hour east.  We will feed you.  Sit at the fire.  Do not touch the salt with your left hand.'"
	},
	{
		"speaker": "· THE KEL-DANARI TRIBAL CIRCLE ·",
		"text": "Fifteen Delvanni sit in a specific ring around a fire pit.  Hel Velli introduces you with a specific ceremonial phrase you do not catch fully.\n\nOne Delvanni · larger than the rest, upper-arm decorated with braided combat honors · stands up.  Hel Velli whispers to you:\n\n'This is MURG.  He is from the Kel-Karai · a neighboring tribe · visiting for a specific trade meeting.  You have arrived at an awkward time.  He will want to duel.  It is · a tradition.'"
	},
	{
		"speaker": "MURG OF THE KEL-KARAI",
		"text": "Murg approaches.  Seven feet tall.  Rust-red skin.  A specific braided upper-right arm decoration.  A specific stain on his lower-left palm that Hel Velli's earlier tone about him suggests you should not ask about.\n\n'I have heard the outworlder is small.  I did not expect four-limbed.'  He pauses.  'What is that in your hand?'"
	},
	{
		"speaker": "· CHOICE · how do you engage Murg? ·",
		"type": "choice",
		"choices": [
			{
				"id": "duel_traditional",
				"label": "  Choose a traditional weapon from the rack.  A Delvanni spear.  ",
				"note": "Fight the duel as a Delvanni would · combat introduced properly · Murg respects you if you win, thinks less of you if you lose",
				"sets": {"duel_choice": "traditional", "combat_pending": true}
			},
			{
				"id": "duel_briefcase",
				"label": "  Pull out your Caltech lab briefcase.  'I have brought my work.'  ",
				"note": "The briefcase joke option · Murg laughs · duel becomes friendly · specific reconciliation dialogue",
				"sets": {"duel_choice": "briefcase", "murg_reconciled": true, "hel_velli_disposition_delta": 2}
			},
			{
				"id": "duel_pistol",
				"label": "  Draw your rocket-fuel pistol.  'I do not intend to duel.'  ",
				"note": "Presume the duel need not happen · Murg's face does a specific thing · Hel Velli's face does a specific thing",
				"sets": {"duel_choice": "pistol_drawn", "hel_velli_disposition_delta": -4, "murg_hostile": true}
			}
		]
	},
	{
		"speaker": "· BEAT ·",
		"text": "The tribal circle reacts."
	},
	{
		"speaker": "· BEAT ·",
		"text": "· specific beat · what happens next depends on your specific choice · full scene authoring is a follow-up commit · scaffold advances toward the reconciled path for narrative continuity ·"
	},
	{
		"speaker": "HEL VELLI",
		"text": "Later, at the fire, Murg has returned to his own tribe with (specific outcome dependent on your choice above).  Hel Velli sits next to you and passes you a specific piece of dried meat.\n\n'You will need transportation.  I have a specific mount.  I have a specific reason to travel west to Talikan.  If you would like to travel with me · I will not object.  Your presence is · specifically interesting to me.'"
	},
	{
		"speaker": "· BEAT ·",
		"text": "You accept.  Hel Velli nods once.\n\nHel Velli · Kel-Danari warrior · four-armed · loyal once respect is earned · 22 years of combat memory · specifically loyal to his mother who lives on a coastal Delvanni settlement · joins your party."
	},
	{
		"speaker": "· END CHAPTER 2 ·",
		"text": "Hel Velli points north with his upper-left blade.  'Talikan,' he says.  'Three days.  The Kyrindi will want to look at you.  Everyone wants to look at you.  You are the only one of you.'\n\nYou ride.\n\n· CHAPTER 3 · TALIKAN · the silver-blue city ·"
	}
]


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")


func boot(state: Dictionary) -> void:
	_run_state = state
	_build_frame()
	_render_current_beat()


func _build_frame() -> void:
	# Rust-red Parsa background
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# A specific sand-band gradient across the bottom two thirds
	var sand_band := ColorRect.new()
	sand_band.color = C_SAND
	sand_band.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	sand_band.offset_top = -240
	sand_band.offset_bottom = 0
	add_child(sand_band)

	# CRT scanline overlay
	for y in range(0, 720, 2):
		var scanline := ColorRect.new()
		scanline.color = Color(0.0, 0.0, 0.0, 0.15)
		scanline.set_anchors_preset(Control.PRESET_TOP_WIDE)
		scanline.position.y = y
		scanline.size = Vector2(2000, 1)
		add_child(scanline)

	# Top HUD band
	var hud_top := ColorRect.new()
	hud_top.color = C_GRAY
	hud_top.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	hud_top.offset_top = 0
	hud_top.offset_bottom = 24
	add_child(hud_top)

	var hud_top_text := Label.new()
	hud_top_text.text = "CHAPTER 2 · THE APPROACH · PARSA"
	hud_top_text.set_anchors_preset(Control.PRESET_TOP_LEFT)
	hud_top_text.position = Vector2(12, 6)
	hud_top_text.add_theme_font_size_override("font_size", 10)
	hud_top_text.add_theme_color_override("font_color", C_AMBER)
	add_child(hud_top_text)

	var hud_top_right := Label.new()
	hud_top_right.text = "TWO MOONS"
	hud_top_right.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	hud_top_right.position = Vector2(-100, 6)
	hud_top_right.add_theme_font_size_override("font_size", 10)
	hud_top_right.add_theme_color_override("font_color", C_AMBER)
	add_child(hud_top_right)

	# Bottom HUD status line · updates as party grows
	var hud_bot := ColorRect.new()
	hud_bot.color = C_GRAY
	hud_bot.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	hud_bot.offset_top = -24
	hud_bot.offset_bottom = 0
	add_child(hud_bot)

	var hud_bot_text := Label.new()
	hud_bot_text.text = _build_hud_string()
	hud_bot_text.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	hud_bot_text.position = Vector2(12, -18)
	hud_bot_text.add_theme_font_size_override("font_size", 10)
	hud_bot_text.add_theme_color_override("font_color", C_GREEN)
	add_child(hud_bot_text)

	# Central Cortex-purple panel
	# HeroImage · two moons over the dunes · top-right
	var hero := HeroImage.new()
	if hero.load_from("res://resources/games/vol7/earthman_chronicles/hero_images/parsa_awakening.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(220, 124))
		tex_rect.set_anchors_preset(Control.PRESET_TOP_RIGHT)
		tex_rect.position = Vector2(-240, 28)
		tex_rect.size = Vector2(220, 124)
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		add_child(tex_rect)

	var panel := ColorRect.new()
	panel.color = C_CORTEX
	panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	panel.offset_left = -400
	panel.offset_right = 400
	panel.offset_top = -220
	panel.offset_bottom = 240
	add_child(panel)


func _build_hud_string() -> String:
	var members: Array = _run_state.get("party_members", ["jack"])
	var names: Array = []
	for m in members:
		match String(m):
			"jack": names.append("JACK")
			"hel_velli": names.append("HEL VELLI")
			"sara_nai": names.append("SARA NAI")
			"scarlet_woman": names.append("SCARLET")
			"rocha": names.append("ROCHA")
			_: names.append(String(m).to_upper())
	return "PARTY: " + " · ".join(names) + "  ·  HP 100/100  ·  SP 40/40"


func _clear_choices() -> void:
	if _choices_root != null and is_instance_valid(_choices_root):
		_choices_root.queue_free()
	_choices_root = null


func _render_current_beat() -> void:
	_clear_choices()
	if _beat_idx >= _beats.size():
		_end_chapter()
		return

	if _speaker_lbl != null and is_instance_valid(_speaker_lbl):
		_speaker_lbl.queue_free()
	if _content_lbl != null and is_instance_valid(_content_lbl):
		_content_lbl.queue_free()

	var beat: Dictionary = _beats[_beat_idx]

	_speaker_lbl = Label.new()
	_speaker_lbl.text = String(beat.get("speaker", ""))
	_speaker_lbl.set_anchors_preset(Control.PRESET_CENTER)
	_speaker_lbl.offset_left = -380
	_speaker_lbl.offset_right = 380
	_speaker_lbl.offset_top = -200
	_speaker_lbl.offset_bottom = -180
	_speaker_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_speaker_lbl.add_theme_font_size_override("font_size", 11)
	_speaker_lbl.add_theme_color_override("font_color", C_AMBER)
	add_child(_speaker_lbl)

	_content_lbl = RichTextLabel.new()
	_content_lbl.bbcode_enabled = false
	_content_lbl.fit_content = true
	_content_lbl.set_anchors_preset(Control.PRESET_CENTER)
	_content_lbl.offset_left = -380
	_content_lbl.offset_right = 380
	_content_lbl.offset_top = -170
	_content_lbl.offset_bottom = 100
	_content_lbl.text = String(beat.get("text", ""))
	_content_lbl.add_theme_font_size_override("normal_font_size", 12)
	_content_lbl.add_theme_color_override("default_color", C_WHITE)
	add_child(_content_lbl)

	if String(beat.get("type", "")) == "choice":
		_render_choices(beat)
	else:
		_render_advance_button()


func _render_choices(beat: Dictionary) -> void:
	_choices_root = Control.new()
	_choices_root.set_anchors_preset(Control.PRESET_CENTER)
	_choices_root.offset_left = -380
	_choices_root.offset_right = 380
	_choices_root.offset_top = 100
	_choices_root.offset_bottom = 240
	add_child(_choices_root)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.add_theme_constant_override("separation", 6)
	_choices_root.add_child(v)

	for choice_v in beat.get("choices", []):
		var choice: Dictionary = choice_v
		var vh := VBoxContainer.new()
		vh.add_theme_constant_override("separation", 2)
		v.add_child(vh)

		var btn := Button.new()
		btn.text = String(choice.get("label", ""))
		btn.add_theme_font_size_override("font_size", 11)
		btn.pressed.connect(func() -> void: _on_choice_selected(choice))
		vh.add_child(btn)

		var note := Label.new()
		note.text = "     " + String(choice.get("note", ""))
		note.add_theme_font_size_override("font_size", 9)
		note.add_theme_color_override("font_color", C_DIM)
		vh.add_child(note)


func _render_advance_button() -> void:
	_choices_root = Control.new()
	_choices_root.set_anchors_preset(Control.PRESET_CENTER)
	_choices_root.offset_left = -80
	_choices_root.offset_right = 80
	_choices_root.offset_top = 160
	_choices_root.offset_bottom = 220
	add_child(_choices_root)

	var btn := Button.new()
	btn.text = "  continue  →  "
	btn.add_theme_font_size_override("font_size", 12)
	btn.pressed.connect(_on_advance)
	btn.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_choices_root.add_child(btn)


func _on_choice_selected(choice: Dictionary) -> void:
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("verb_select", 0.5)
	var sets: Dictionary = choice.get("sets", {})
	for k in sets.keys():
		var key: String = String(k)
		if key.ends_with("_delta"):
			var base_key: String = key.substr(0, key.length() - 6)
			var cur: int = int(_run_state.get(base_key, 0))
			_run_state[base_key] = cur + int(sets[k])
		else:
			_run_state[key] = sets[k]
	var choices_log: Array = _run_state.get("choices_log", [])
	choices_log.append({"chapter": 2, "beat": _beat_idx, "choice_id": String(choice.get("id", ""))})
	_run_state["choices_log"] = choices_log
	_on_advance()


func _on_advance() -> void:
	_beat_idx += 1
	_render_current_beat()


func _end_chapter() -> void:
	# Officially add Hel Velli to the party
	var party: Array = _run_state.get("party_members", ["jack"])
	if not party.has("hel_velli"):
		party.append("hel_velli")
	_run_state["party_members"] = party
	var alive: Dictionary = _run_state.get("party_alive", {"jack": true})
	alive["hel_velli"] = true
	_run_state["party_alive"] = alive
	_run_state["chapter"] = 3

	_clear_choices()
	# Refresh HUD to show Hel Velli
	# (crude · full HUD rebuild would be a specific method call)

	var end_root := Control.new()
	end_root.set_anchors_preset(Control.PRESET_CENTER)
	end_root.offset_left = -180
	end_root.offset_right = 180
	end_root.offset_top = 100
	end_root.offset_bottom = 200
	add_child(end_root)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.add_theme_constant_override("separation", 12)
	end_root.add_child(v)

	var back_btn := Button.new()
	back_btn.text = "  ← back to title  "
	back_btn.pressed.connect(_on_back_pressed)
	v.add_child(back_btn)

	chapter_complete.emit(_run_state)


func _on_back_pressed() -> void:
	quit_to_shelf.emit()


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			_on_back_pressed()
			get_viewport().set_input_as_handled()
			return
		if kev.keycode == KEY_SPACE or kev.keycode == KEY_ENTER or kev.keycode == KEY_KP_ENTER:
			if _beat_idx < _beats.size():
				var beat: Dictionary = _beats[_beat_idx]
				if String(beat.get("type", "")) != "choice":
					_on_advance()
					get_viewport().set_input_as_handled()
