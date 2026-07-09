extends Control
## Earthman Chronicles · Chapter 3 · Talikan · Sara Nai · scaffold.
##
## Party arrives at the Kyrindi capital.  Jack meets King Vessel,
## High Scribe Arentha (Correction 3 available here), and Sara Nai
## (who has been reading about Jack for four years and summoned him
## deliberately as an academic collaborator).  First Working (Star
## Ruby) becomes performable.
##
## Ends with Sara Nai joining the party and the party preparing to
## descend to the Mines of Delvan.
##
## Follows the Chapter 1 / Chapter 2 beat-sequence pattern.
##
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal chapter_complete(state: Dictionary)

# Kyrindi Talikan palette · silver-blue, cream, green-tinted glass
const C_BG           := Color(0.157, 0.220, 0.290, 1.0)   # Kyrindi twilight
const C_STONE        := Color(0.910, 0.878, 0.816, 1.0)   # white marble
const C_STONE_HI     := Color(0.784, 0.808, 0.816, 1.0)   # green-tinted glass
const C_CORTEX       := Color(0.345, 0.188, 0.376, 1.0)
const C_AMBER        := Color(0.784, 0.376, 0.125, 1.0)
const C_GREEN        := Color(0.0, 0.753, 0.376, 1.0)
const C_RED          := Color(0.753, 0.125, 0.125, 1.0)
const C_CREAM        := Color(0.912, 0.816, 0.565, 1.0)
const C_WHITE        := Color(0.941, 0.941, 0.941, 1.0)
const C_GRAY         := Color(0.282, 0.282, 0.314, 1.0)
const C_DIM          := Color(0.545, 0.463, 0.302, 1.0)
const C_KYRINDI      := Color(0.678, 0.780, 0.859, 1.0)

var _run_state: Dictionary = {}
var _beat_idx: int = 0
var _content_lbl: RichTextLabel = null
var _speaker_lbl: Label = null
var _choices_root: Control = null

var _beats: Array = [
	{
		"speaker": "· TALIKAN · APPROACH ·",
		"text": "The Kyrindi capital sits on a specific mesa · two rivers meet at its base, both fresh, both cold, both drinkable.  The city is white marble and green-tinted glass in the specific way that Kyrindi architecture is.\n\nHel Velli rides a specific Parsan mount with an unusual number of legs (six).  You are on foot beside him.  He has offered you the mount several times.  You have declined for reasons of pride you cannot fully articulate."
	},
	{
		"speaker": "· TALIKAN GATE ·",
		"text": "Four Kyrindi guards stand at the main gate.  They are seven feet tall.  Their skin is silver-blue.  Their fingertips fluoresce faintly.\n\nHel Velli speaks a specific ceremonial phrase to them.  They accept his tribal-ID token.  They wave you both through.\n\nAbove the gate: a specific inscription you cannot yet read.  Hel Velli says quietly, 'it says something specifically welcoming.  I will not translate more than that.'"
	},
	{
		"speaker": "· TALIKAN MARKET ·",
		"text": "The main market of Talikan.  Kyrindi merchants sell specific crafts you have not seen in any Earth market · woven silks that change color under moonlight, small carved figures that keep time, glass jars containing water from specific springs on Parsa.\n\nA specific Kelait musician plays reed pipes at a specific booth.  His playing is quiet, competent, sad.  A tune fragment catches your ear · you do not know why.  Something about the ending bar."
	},
	{
		"speaker": "· CHOICE · do you drop a coin in the Kelait musician's bowl? ·",
		"type": "choice",
		"choices": [
			{
				"id": "coin_drop",
				"label": "  Drop a coin.  Listen to a specific verse of his tune.  ",
				"note": "The musician is Yr's paternal grandfather · specific cross-Oneironautics tie · fragment shares its final bar with a song from Pirate Summer",
				"sets": {"met_kelait_musician": true, "heard_musician_fragment": true}
			},
			{
				"id": "coin_skip",
				"label": "  Walk on.  You are here for the palace audience.  ",
				"note": "You will pass this booth again in a later chapter · you can drop a coin then · but a specific realization is delayed",
				"sets": {"met_kelait_musician": false}
			}
		]
	},
	{
		"speaker": "· TALIKAN PALACE · KING VESSEL ·",
		"text": "The Kyrindi throne room is smaller than you expected.  Twelve pillars, a single throne of pale wood, six standing courtiers.\n\nKING VESSEL is 6'8\" · his silver hair is cropped unusually short for a Kyrindi noble · his six fingertips fluoresce more when he is tired · he is often tired.\n\nHe stands when you enter.  Kyrindi royalty do not stand for foreigners.  You will realize this later."
	},
	{
		"speaker": "KING VESSEL",
		"text": "'You are Jack Whiteside.  My daughter has been reading about you for four years.'\n\nHe pauses.  A specific length of pause · not for effect · thinking specifically.\n\n'She wants me to say I do not offer her to you.  She has made her own decision.  I honor it.'"
	},
	{
		"speaker": "· TALIKAN LIBRARY · THAT NIGHT ·",
		"text": "You are at the library because Vessel invited you to read a specific document about the Kelait people.  You are alone in a reading room at what you would call 'ten pm' if this world had pm.\n\nThe door opens.  A specific tall Kyrindi woman with silver-black hair in a single braid enters carrying a lamp.  She is · seven feet one · unusually tall for a Kyrindi · wearing scholar's white with green trim.\n\nBehind her, standing quietly, is a second Kyrindi woman.  Younger.  Six-foot-four.  Green-eyed in torchlight.  Silver hair worn loose.\n\nSARA NAI."
	},
	{
		"speaker": "HIGH SCRIBE ARENTHA",
		"text": "The taller woman is ARENTHA · High Scribe · Sara Nai's academic mentor.  She sets the lamp on the table and studies you through a specific pair of reading spectacles.  Kyrindi rarely need corrective lenses · she is genetically anomalous.\n\n'You are Sara's alleged summoning.  Sit.  You will find our chairs uncomfortable.  We do this on purpose.'"
	},
	{
		"speaker": "· CHOICE · which specific thing do you ask Arentha about? ·",
		"type": "choice",
		"choices": [
			{
				"id": "ask_star",
				"label": "  'I have seen an eight-pointed star three times since arriving.'  ",
				"note": "Arentha shows you the OTO Contract · CORRECTION 3 unlockable · specific plot advancement",
				"sets": {"asked_arentha_star": true, "found_correction_oto": true, "corrections_found_delta": 1}
			},
			{
				"id": "ask_kelait",
				"label": "  'Tell me about the Kelait.  I have heard specific things.'  ",
				"note": "Arentha refers you to Mother Kanel · sets up Chapter 4 arrival · +1 disposition Arentha",
				"sets": {"asked_arentha_kelait": true, "arentha_disposition_delta": 1}
			},
			{
				"id": "ask_sara",
				"label": "  'Tell me about Sara.  Your student.'  ",
				"note": "Arentha talks about Sara as scholar · unlocks Sara's academic-collaboration dialogue · +1 disposition Sara",
				"sets": {"asked_arentha_sara": true, "sara_nai_disposition_delta": 1}
			}
		]
	},
	{
		"speaker": "SARA NAI",
		"text": "Arentha leaves you both with a specific 'if you break anything I will know.'\n\nSara Nai sits opposite you.  She does not lean forward.  She does not smile.  She looks at you the way you would look at a chart you had been reading about for a very long time and were finally seeing in person.\n\n'You did not fall in love with me on first sight.  You looked at me like I was a chart.  I summoned you as an academic collaborator four years ago.  I want you to know that.  I want you to acknowledge that.  Then we can proceed.'"
	},
	{
		"speaker": "· CHOICE · what do you say to Sara Nai? ·",
		"type": "choice",
		"choices": [
			{
				"id": "recognize_setup",
				"label": "  'I acknowledge you summoned me.  You have my attention.'  ",
				"note": "Recognize the setup · Sara Nai +3 disposition · unlocks her deeper dialogue tree · the game's most respectful path",
				"sets": {"acknowledged_summoning": true, "sara_nai_disposition_delta": 3}
			},
			{
				"id": "manuscript_frame",
				"label": "  'The Working brought me here.  I did not know you existed until tonight.'  ",
				"note": "Play along with Hubbard's fate-narrative · Sara Nai -1 disposition · specific Chapter 5 dialogue changes",
				"sets": {"acknowledged_summoning": false, "sara_nai_disposition_delta": -1}
			}
		]
	},
	{
		"speaker": "SARA NAI",
		"text": "She nods once.  The nod is not celebration.  It is acknowledgment.\n\n'Good.  I have specific documents you should read.  I have a specific ritual you should perform · the Star Ruby · Working I · you know the shape of it, I have read your Rafaton's notes.  I have a specific alternative to what Rafaton would have you do.  The Kelait version is more accurate.  You may choose.'"
	},
	{
		"speaker": "· CHOICE · Working I · which version? ·",
		"type": "choice",
		"choices": [
			{
				"id": "working_i_rafaton",
				"label": "  Perform Rafaton's version · the manuscript-canonical Star Ruby.  ",
				"note": "The manuscript version · Rafaton would approve · sets up his Chapter 5 reveal · Sara Nai's disappointment specific",
				"sets": {"working_i_completed": true, "working_i_version": "rafaton", "sara_nai_disposition_delta": -1}
			},
			{
				"id": "working_i_kelait",
				"label": "  Perform Sara Nai's Kelait version.  ",
				"note": "The Kelait version · more accurate · Sara Nai +1 disposition · sets up specific Chapter 4 rapport with Mother Kanel",
				"sets": {"working_i_completed": true, "working_i_version": "kelait", "sara_nai_disposition_delta": 1}
			}
		]
	},
	{
		"speaker": "· THE STAR RUBY ·",
		"text": "You perform Working I.  The specific candles.  The specific chalk.  The specific spoken words.  Rafaton is not present · Sara Nai is · her hand is steady on the specific brass censer she is holding.\n\nAfter, the party is protected from panic effects for the next specific combat encounter.  You are also, and this is not in Rafaton's notes, quieter than you were before you began.  You do not know what to do with this."
	},
	{
		"speaker": "· NEWS ARRIVES ·",
		"text": "A specific Kyrindi courier enters the library at what would be one in the morning.  She hands Arentha a specific letter.  Arentha reads it silently.  Then she says, and her voice is entirely level:\n\n'The Kel-Rethani have staged a Delvanni tribal conflict as cover for a specific raid on a Kelait settlement.  The settlement is on the Delvan mining land.  If you were planning to descend to the mines, it is now more urgent than it was.'"
	},
	{
		"speaker": "· BEAT ·",
		"text": "Sara Nai stands.  She looks at you.\n\n'I am coming with you.'"
	},
	{
		"speaker": "· END CHAPTER 3 ·",
		"text": "Sara Nai · Kyrindi noblewoman · scholar of Kelait rituals · joins the party.\n\nThat night she spreads a map on the library table and puts one finger on a specific plateau fifteen hours south.  'The mines,' she says.  'The Kelait are there.  My books end where the mines begin.  I want to see what the books were not allowed to say.'\n\n· CHAPTER 4 · THE MINES OF DELVAN ·"
	}
]


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	_schedule_ambient()


func _exit_tree() -> void:
	_ambient_alive = false


var _ambient_alive: bool = true

func _schedule_ambient() -> void:
	if not _ambient_alive or not is_inside_tree():
		return
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("kyrindi_bell", 0.35)
	get_tree().create_timer(26.0).timeout.connect(_schedule_ambient)



func boot(state: Dictionary) -> void:
	_run_state = state
	_build_frame()
	_render_current_beat()


func _build_frame() -> void:
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# White-marble accent band at the top
	var marble_band := ColorRect.new()
	marble_band.color = C_STONE
	marble_band.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	marble_band.offset_top = 24
	marble_band.offset_bottom = 60
	marble_band.color.a = 0.5
	add_child(marble_band)

	# CRT scanlines
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
	hud_top_text.text = "CHAPTER 3 · TALIKAN · KYRINDI CAPITAL"
	hud_top_text.set_anchors_preset(Control.PRESET_TOP_LEFT)
	hud_top_text.position = Vector2(12, 6)
	hud_top_text.add_theme_font_size_override("font_size", 10)
	hud_top_text.add_theme_color_override("font_color", C_AMBER)
	add_child(hud_top_text)

	var hud_top_right := Label.new()
	hud_top_right.text = "WORKING I · AVAILABLE"
	hud_top_right.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	hud_top_right.position = Vector2(-180, 6)
	hud_top_right.add_theme_font_size_override("font_size", 10)
	hud_top_right.add_theme_color_override("font_color", C_KYRINDI)
	add_child(hud_top_right)

	# Bottom HUD status
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

	# Center Cortex-purple panel
	# HeroImage · the Kyrindi library · top-right
	var hero := HeroImage.new()
	if hero.load_from("res://resources/games/vol7/earthman_chronicles/hero_images/kyrindi_library.json"):
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
	_speaker_lbl.add_theme_color_override("font_color", C_KYRINDI)
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
	# Track Working I completion as a proper array entry
	if String(choice.get("id", "")).begins_with("working_i_"):
		var wc: Array = _run_state.get("workings_completed", [])
		if not wc.has("star_ruby"): wc.append("star_ruby")
		_run_state["workings_completed"] = wc
	# Track OTO Contract as a Correction
	if bool(sets.get("found_correction_oto", false)):
		var cf: Array = _run_state.get("corrections_found", [])
		if not cf.has("correction_oto_contract"): cf.append("correction_oto_contract")
		_run_state["corrections_found"] = cf
	var choices_log: Array = _run_state.get("choices_log", [])
	choices_log.append({"chapter": 3, "beat": _beat_idx, "choice_id": String(choice.get("id", ""))})
	_run_state["choices_log"] = choices_log
	_on_advance()


func _on_advance() -> void:
	_beat_idx += 1
	_render_current_beat()


func _end_chapter() -> void:
	var party: Array = _run_state.get("party_members", ["jack"])
	if not party.has("sara_nai"):
		party.append("sara_nai")
	_run_state["party_members"] = party
	var alive: Dictionary = _run_state.get("party_alive", {"jack": true})
	alive["sara_nai"] = true
	_run_state["party_alive"] = alive
	_run_state["chapter"] = 4

	_clear_choices()

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
