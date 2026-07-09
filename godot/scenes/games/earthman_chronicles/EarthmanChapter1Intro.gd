extends Control
## Earthman Chronicles · Chapter 1 · Pasadena · 1946 · opening
## vignette · scaffold pass.
##
## The player is Jack Whiteside on the evening of January 17,
## 1946.  Two hours before the ritual.  Rafaton has just arrived.
##
## This scaffold renders the opening as a text-forward beat
## sequence (like a specific pulp-novel first chapter) with
## specific choices the player makes.  Full first-person grid
## rendering of the coach-house workshop / library / kitchen /
## bedroom / ritual chamber is a later commit.
##
## Emits `quit_to_shelf` on Back.  Emits `chapter_complete(state)`
## when the ritual is performed (currently: after the player
## clicks through the beats and picks the ritual variant).
##
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal chapter_complete(state: Dictionary)

# Astro-Cortex palette
const C_BG           := Color(0.094, 0.094, 0.157, 1.0)
const C_CORTEX       := Color(0.345, 0.188, 0.376, 1.0)
const C_AMBER        := Color(0.784, 0.376, 0.125, 1.0)
const C_GREEN        := Color(0.0, 0.753, 0.376, 1.0)
const C_RED          := Color(0.753, 0.125, 0.125, 1.0)
const C_CREAM        := Color(0.912, 0.816, 0.565, 1.0)
const C_WHITE        := Color(0.941, 0.941, 0.941, 1.0)
const C_GRAY         := Color(0.282, 0.282, 0.314, 1.0)
const C_DIM          := Color(0.545, 0.463, 0.302, 1.0)

var _run_state: Dictionary = {}
var _beat_idx: int = 0
var _content_lbl: RichTextLabel = null
var _speaker_lbl: Label = null
var _choices_root: Control = null

# The opening beat sequence.  Each beat is either a NARRATION
# (auto-advance on click) or a CHOICE (buttons).  Runtime data ·
# player mutations affect later beats.
var _beats: Array = [
	{
		"speaker": "· PASADENA · JANUARY 17, 1946 · 8:47 PM ·",
		"text": "You are Doctor Jack Whiteside.  You are thirty-two.  You have not slept for real in three days.  The propellant you tested at Edwards two weeks ago worked · you have a paper due to a specific journal on Friday.  You have written none of it.\n\nYou are not thinking about the paper.  You are thinking about tonight."
	},
	{
		"speaker": "· THE COACH HOUSE ·",
		"text": "Your home laboratory is behind the main house on Orange Grove Boulevard.  You built it yourself in 1943.  A specific narrow room · two chalk-marked altars, a bench with fifteen kinds of glassware, a smaller bench with three books, one of which is bound in leather older than California statehood.\n\nThe altar to the west has the compound you mixed at four this afternoon.  The altar to the east has three candles you have not yet lit.  The floor is chalked."
	},
	{
		"speaker": "RAFATON, at the door",
		"text": "'Jack.  I hope I am not late.  The 133 was slow.'\n\nHe is Kelait · a small, patient, gray-eyed man in a wool coat that fits him poorly.  He is also, as far as anyone at Caltech knows, a graduate student named ALBERT RATHKE, doing research on Aramaic textual practices.  He is not.  What he is you have not entirely worked out."
	},
	{
		"speaker": "· JACK ·",
		"text": "'You are on time.  I have not lit the candles yet.  I wanted you here for the lighting.'\n\nRafaton nods and takes off his coat, revealing his own working clothes · a plain gray shirt and a specific silver pendant you have never asked him about.  He steps into the chalked circle without breaking any line."
	},
	{
		"speaker": "· CHOICE · what specifically do you tell Rafaton about tonight? ·",
		"type": "choice",
		"choices": [
			{
				"id": "chemistry_focus",
				"label": "  'I want to test the propellant reaction under · specific circumstances.'  ",
				"note": "The chemistry-first framing · Jack's official reason · Working effects will be technical-tuned",
				"sets": {"class_focus": "chemistry", "rafaton_disposition": 0}
			},
			{
				"id": "mysticism_focus",
				"label": "  'You know what I want.  The Working from Book Four.'  ",
				"note": "The mysticism-first framing · Jack's honest reason · Working effects will be mystical-tuned",
				"sets": {"class_focus": "mysticism", "rafaton_disposition": 1}
			},
			{
				"id": "both_focus",
				"label": "  'Both.  I want to see what happens when both are present.'  ",
				"note": "The synthesis framing · Jack's true reason · balanced Working effects · unlocks a specific Chapter 5 dialogue",
				"sets": {"class_focus": "synthesis", "rafaton_disposition": 2, "synthesis_flag": true}
			}
		]
	},
	{
		"speaker": "· BEAT ·",
		"text": "Rafaton considers.  He always does.  The specific length of his considering is one of the reasons you like him."
	},
	{
		"speaker": "RAFATON",
		"text": "'I will scribe.  I have three questions I would like answered afterward.  I will not ask them tonight.  Let us begin.'\n\nHe pulls out a specific fountain pen · the pen is unusually fine for a graduate student, but you have never asked · and opens a leather-bound notebook to a fresh page."
	},
	{
		"speaker": "· CHOICE · a specific practical concern · which candles do you light? ·",
		"type": "choice",
		"choices": [
			{
				"id": "candles_west_first",
				"label": "  West first.  Then east.  Then north.  ",
				"note": "The manuscript-canonical order · Hubbard's version",
				"sets": {"candle_order": "west_first"}
			},
			{
				"id": "candles_east_first",
				"label": "  East first.  Then west.  Then north.  ",
				"note": "The Kelait-canonical order · Rafaton's preferred version if pressed · a specific respect-earning choice",
				"sets": {"candle_order": "east_first", "rafaton_disposition_delta": 1}
			}
		]
	},
	{
		"speaker": "· THE RITUAL ·",
		"text": "You light the candles in the specific order.  Rafaton writes in his notebook · you cannot see what he writes.\n\nYou speak the specific words you have been rehearsing.  You do not know if you are pronouncing them right.  Rafaton does not correct you.\n\nThe compound on the west altar begins, quietly, to burn."
	},
	{
		"speaker": "· BEAT ·",
		"text": "The room · which is nine by fifteen feet, which you built yourself, which you have known for three years · appears briefly, uncomfortably, to expand.\n\nThen something in the room takes a specific interest in you."
	},
	{
		"speaker": "· BEAT ·",
		"text": "Rafaton says, without looking up from his notebook:\n\n'Do you feel it, Jack?'"
	},
	{
		"speaker": "· CHOICE · answer? ·",
		"type": "choice",
		"choices": [
			{
				"id": "answer_honest",
				"label": "  'Not yet.  Should I?'  ",
				"note": "Honest answer · earns Rafaton's specific silent disappointment",
				"sets": {"answered_honestly": true, "rafaton_disposition_delta": -1}
			},
			{
				"id": "answer_canonical",
				"label": "  'I feel the very fabric parting.'  ",
				"note": "The manuscript-canonical answer · Hubbard's line · sets up a specific Chapter 5 manipulation",
				"sets": {"answered_canonically": true, "rafaton_disposition_delta": 1}
			}
		]
	},
	{
		"speaker": "· BEAT ·",
		"text": "The compound has finished burning.  The candles gutter, all three, at once.  A specific silence follows.\n\nThe silence is broken by a specific sound you have not heard in your life before.  It is not audible in any conventional sense.  It is, still, a sound."
	},
	{
		"speaker": "· BEAT ·",
		"text": "You fall."
	},
	{
		"speaker": "· BEAT ·",
		"text": "You fall farther than any man has fallen."
	},
	{
		"speaker": "· END CHAPTER 1 ·",
		"text": "· scaffold pass · Chapter 2 (Parsa · the sand · Hel Velli) authoring pending · content authored in chapters.json · npcs.json · dialogue_web.json ·"
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
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

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
	hud_top_text.text = "CHAPTER 1 · PASADENA · 1946"
	hud_top_text.set_anchors_preset(Control.PRESET_TOP_LEFT)
	hud_top_text.position = Vector2(12, 6)
	hud_top_text.add_theme_font_size_override("font_size", 10)
	hud_top_text.add_theme_color_override("font_color", C_AMBER)
	add_child(hud_top_text)

	var hud_top_right := Label.new()
	hud_top_right.text = "8:47 PM"
	hud_top_right.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	hud_top_right.position = Vector2(-100, 6)
	hud_top_right.add_theme_font_size_override("font_size", 10)
	hud_top_right.add_theme_color_override("font_color", C_AMBER)
	add_child(hud_top_right)

	# Bottom HUD status line
	var hud_bot := ColorRect.new()
	hud_bot.color = C_GRAY
	hud_bot.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	hud_bot.offset_top = -24
	hud_bot.offset_bottom = 0
	add_child(hud_bot)

	var hud_bot_text := Label.new()
	hud_bot_text.text = "PARTY: JACK ·  RAFATON (SCRIBING)  ·  HP 100/100  ·  SP 40/40"
	hud_bot_text.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	hud_bot_text.position = Vector2(12, -18)
	hud_bot_text.add_theme_font_size_override("font_size", 10)
	hud_bot_text.add_theme_color_override("font_color", C_GREEN)
	add_child(hud_bot_text)

	# Central Cortex-purple panel
	var panel := ColorRect.new()
	panel.color = C_CORTEX
	panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	panel.offset_left = -400
	panel.offset_right = 400
	panel.offset_top = -220
	panel.offset_bottom = 240
	add_child(panel)


func _clear_choices() -> void:
	if _choices_root != null and is_instance_valid(_choices_root):
		_choices_root.queue_free()
	_choices_root = null


func _render_current_beat() -> void:
	_clear_choices()
	if _beat_idx >= _beats.size():
		_end_chapter()
		return

	# Clear previous speaker/content labels
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
		# Advance-on-click / space
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
	var sets: Dictionary = choice.get("sets", {})
	for k in sets.keys():
		var key: String = String(k)
		if key.ends_with("_delta"):
			# Additive to existing counter
			var base_key: String = key.substr(0, key.length() - 6)
			var cur: int = int(_run_state.get(base_key, 0))
			_run_state[base_key] = cur + int(sets[k])
		else:
			_run_state[key] = sets[k]
	# Also record the choice id in run_state.choices for later
	var choices_log: Array = _run_state.get("choices_log", [])
	choices_log.append({"beat": _beat_idx, "choice_id": String(choice.get("id", ""))})
	_run_state["choices_log"] = choices_log
	_on_advance()


func _on_advance() -> void:
	_beat_idx += 1
	_render_current_beat()


func _end_chapter() -> void:
	_clear_choices()
	# Final screen: back to title button + status
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
			# Space/Enter advances only if no choice is showing
			if _beat_idx < _beats.size():
				var beat: Dictionary = _beats[_beat_idx]
				if String(beat.get("type", "")) != "choice":
					_on_advance()
					get_viewport().set_input_as_handled()
