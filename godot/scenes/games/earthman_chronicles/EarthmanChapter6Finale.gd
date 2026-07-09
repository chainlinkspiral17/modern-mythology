extends Control
## Earthman Chronicles · Chapter 6 · The Finale · scaffold.
##
## The game's ending selection.  Chapter 5 leaves the state in a
## consistent shape; Chapter 6 opens with the party gathered, plays
## Sara Nai's REFUSAL beat one more time (in case Working IX was
## deferred, not decided), presents the final consent gate, then
## selects one of six endings from the accumulated run state:
##
##   1. THE WARLORD OF PARSA        · Working IX done, few corrections
##   2. RETURN TO EARTH              · IX refused, corrections found
##   3. BABALON COMES                · IX done + Babalon reading
##   4. REFUSED THE WORK             · IX refused + Sara LOVED
##   5. THE CORRECTION               · IX refused + all 6 corrections
##                                     + Rocha recruited + Sara LIKED+
##   6. HUBBARD TAKES THE CREDIT     · IX done + 0 corrections
##
## The chapter renders each ending as a beat-sequence pulled inline
## from the endings.json script, closes on credits, then emits
## chapter_complete and returns the host to the title screen.
##
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal chapter_complete(state: Dictionary)

# Finale palette · depends on ending
const C_BG           := Color(0.055, 0.043, 0.078, 1.0)
const C_STAR         := Color(0.973, 0.784, 0.282, 1.0)
const C_STONE        := Color(0.259, 0.208, 0.239, 1.0)
const C_CORTEX       := Color(0.345, 0.188, 0.376, 1.0)
const C_AMBER        := Color(0.784, 0.376, 0.125, 1.0)
const C_GREEN        := Color(0.0, 0.753, 0.376, 1.0)
const C_RED          := Color(0.753, 0.125, 0.125, 1.0)
const C_CREAM        := Color(0.912, 0.816, 0.565, 1.0)
const C_WHITE        := Color(0.941, 0.941, 0.941, 1.0)
const C_GRAY         := Color(0.282, 0.282, 0.314, 1.0)
const C_DIM          := Color(0.545, 0.463, 0.302, 1.0)
const C_ROCHA_BLUE   := Color(0.451, 0.541, 0.816, 1.0)
const C_PARSA_DUSK   := Color(0.816, 0.541, 0.318, 1.0)

# Ending scripts inline · one array per ending id.
# Each beat: {"speaker", "text"} · same shape as prior chapters.
const ENDINGS: Dictionary = {
	"warlord_of_parsa": {
		"name": "· THE WARLORD OF PARSA ·",
		"subtitle": "SOMEONE HAS TO SIT ON THAT THRONE",
		"beats": [
			{"speaker": "· CORONATION · KYRINDI GREAT HALL ·",
			 "text": "Jack seated on the Kyrindi throne.  Royal purple carpet.  Torches burning at intervals a specific stone measure apart.\n\nSara Nai stands at his right.  Hel Velli stands behind them.  The Delvanni tribes are gathered.  Everyone is applauding at a specific slow ceremonial cadence."},
			{"speaker": "NARRATOR · in the Hubbardish tone the manuscript wanted",
			 "text": "And thus did Jack Whiteside rule Parsa with wisdom and mercy, for such a time as any Prophet may."},
			{"speaker": "· A SPECIFIC BRIEF ANIMATION ·",
			 "text": "Sara Nai's crown is slightly too small.  She adjusts it while nobody is looking.  Three seconds of animation the writers noted specifically."},
			{"speaker": "· FADE ·",
			 "text": "The manuscript's grand image, undercut by Sara's specific quiet adjustment.  Fade to black."}
		]
	},
	"return_to_earth": {
		"name": "· RETURN TO EARTH ·",
		"subtitle": "Parsons dies anyway",
		"beats": [
			{"speaker": "· PASADENA · JANUARY 20, 1946 · MORNING ·",
			 "text": "Jack wakes in his laboratory.  He is holding a specific book.  The date is January 20, 1946.  The Working never happened.\n\nSara Northrup is on the porch."},
			{"speaker": "· STILL IMAGE ·",
			 "text": "Sara Northrup at 25 · in a specific 1946 dress · looking through the porch window at Jack.  Three seconds of held frame."},
			{"speaker": "NARRATOR",
			 "text": "Parsons lives another six years."},
			{"speaker": "· MONTAGE ·",
			 "text": "1946 · Jack at 32 · in his laboratory · working.\n1947 · Jack at 33 · married to Sara Northrup · a specific home in Pasadena.\n1948 · Jack at 34 · attending an OTO Lodge meeting.\n1949 · Jack at 35 · reading a specific book that was banned that year.\n1950 · Jack at 36 · at a specific rocket test at Edwards AFB.\n1951 · Jack at 37 · at a specific dinner · Cameron in the background.\n1952 · the coach-house workshop at 5:57 PM on June 17."},
			{"speaker": "NARRATOR",
			 "text": "Parsons still dies in the explosion.  It just happens later."},
			{"speaker": "· STILL IMAGE ·",
			 "text": "The specific Parsonage in Pasadena · June 18, 1952 · the morning after · smoke visible from the coach-house.  Five seconds held.  Coroner's report visible faintly as background text."}
		]
	},
	"babalon_comes": {
		"name": "· BABALON COMES ·",
		"subtitle": "as foretold",
		"beats": [
			{"speaker": "· PARSA · THE RITUAL CHAMBER ·",
			 "text": "Jack completes Working IX.  The eight-pointed star at the chamber's center is glowing a specific color the game engine renders with a specific unclassified sprite sheet."},
			{"speaker": "NARRATOR",
			 "text": "Sara Nai transforms and remains transformed.  She embraces him.  The universe shifts."},
			{"speaker": "· LOS ANGELES · 1946 · FROM ABOVE ·",
			 "text": "A specific new star in the sky.  The game code names it ISHTAR-46.\n\nA voice · gender ambiguous · specific reverb:\n\n'It is begun.'"},
			{"speaker": "· STILL IMAGE ·",
			 "text": "A specific closed door · unmarked · at the top of a specific staircase in a specific building in a specific Los Angeles alley.  Five seconds held.\n\nFade to black."}
		]
	},
	"refused_the_work": {
		"name": "· REFUSED THE WORK ·",
		"subtitle": "THE MOST BEAUTIFUL LIFE JACK EVER LIVED",
		"beats": [
			{"speaker": "NARRATOR",
			 "text": "Jack refuses Working IX.  He stays on Parsa.  Sara Nai stays with him.  They live in Talikan · a specific quiet house on a specific quiet street.\n\nHel Velli visits often."},
			{"speaker": "· MONTAGE · YEARS ·",
			 "text": "Jack + Sara at 32/24 · their first year · specific unpacking of specific objects into a specific new home.\n\nJack + Sara at 35/27 · a specific quiet moment on a porch · Hel Velli visiting.\n\nJack + Sara at 42/34 · specific children of specific Kelait friends visiting (they cannot have biological children · the genetics do not work · this is briefly established).\n\nJack + Sara at 50/42 · specific hair grays · Sara Nai has finally found the higher registers Arentha said she would."},
			{"speaker": "· MONTAGE · MORE YEARS ·",
			 "text": "Jack + Sara at 60/52 · a specific meal · Yr at 20 · visiting.\n\nJack + Sara at 62/54 · a specific porch scene at dusk · quiet.\n\nJack at 70 · specifically thin · Sara at his bedside · Mother Kanel at the door · specific gentleness."},
			{"speaker": "· KYRINDI FUNERAL CHAMBER ·",
			 "text": "Silver-blue drapery.  A specific funeral pyre.\n\nJack dies of age at 70.  Sara mourns him in Kyrindi ceremonial speech."},
			{"speaker": "SARA NAI · in untranslated Kyrindi",
			 "text": "· ash-teleth · ash-vellem · ash-korren · ash-korren-vai\n\n· korren-vai · korren-vai-me\n\n· vellem-teleth · teleth-korren\n\n· ish-remen · ish-remen-a\n\n· teleth-vai · vai-remen\n\n· (the twelfth verse · the one Arentha said Sara would forget · Sara stumbles · she recovers · she does not forget it after all)"},
			{"speaker": "· KELAIT MOURNING SONG · FINAL BAR ·",
			 "text": "A specific Kelait elder speaks the mourning song's last verse.  A specific melody plays.\n\n· cross-Oneironautics recognition · this shares its final bar with Wilson Ashe's Portuguese folk tune in Pirate Summer · if you have played both, you hear it recognize you back ·"},
			{"speaker": "· STILL IMAGE ·",
			 "text": "Jack and Sara at 62 and 54 · sitting on a porch in Talikan · quiet · specific gentle light.  Eight seconds held.\n\nDedication: for parsons and cameron · a specific version of the life they should have had."}
		]
	},
	"the_correction": {
		"name": "· THE CORRECTION · THE MANUSCRIPT COMPLETES ITSELF ·",
		"subtitle": "for jack",
		"beats": [
			{"speaker": "· TALIKAN · SARA NAI'S CHAMBERS · LATE EVENING ·",
			 "text": "Sara Nai says goodnight to Jack for the last time in the game's cutscene.\n\nThe screen fades.  Two seconds of black."},
			{"speaker": "· HANDWRITTEN NOTE · ROCHA'S HANDWRITING · BLUE PEN ·",
			 "text": "This game was adapted from a manuscript we found in a box in the basement.\n\nL. Rafayette Hubbard wrote it in 1948 to make himself the hero of a story that wasn't his.\n\nThe real hero was a man named John Whiteside Parsons who died in his own laboratory on the seventeenth of June nineteen-fifty-two.\n\nHe was thirty-seven."},
			{"speaker": "· ROCHA'S NOTE · CONTINUED ·",
			 "text": "He was a chemist and a mystic.\n\nHe was ours before he was Hubbard's ANYTHING.\n\nThis is the corrected version.\n\n· A.R., QA, Astro-Cortex, March 1985.\n\nfor jack"},
			{"speaker": "· STILL IMAGE ·",
			 "text": "The actual Parsonage in Pasadena · June 18, 1952 · the morning after Parsons's death · specific documentary-photograph quality · one specific detail: a small potted plant on the porch, still alive.\n\nTen seconds held."},
			{"speaker": "· CREDITS ·",
			 "text": "Adapted from an unpublished manuscript by L. Rafayette Hubbard (1948)\n\nProgramming: J.F. (Senior Engineer)\nQA and Corrections: A. Rocha\nAdditional writing: staff (uncredited by request)\nMusic: staff composer (uncredited by request)\nExecutive Direction: Astro-Cortex Software, Culver City, California\nMarch 15, 1985\n\nDedicated to the memory of John Whiteside Parsons · 1914-1952 · chemist and mystic\n\nFor Jack."}
		]
	},
	"hubbard_takes_the_credit": {
		"name": "· HUBBARD TAKES THE CREDIT ·",
		"subtitle": "SEE ABOVE",
		"beats": [
			{"speaker": "· THE ORDER'S MAIN CHAMBER · WORKING IX COMPLETES ·",
			 "text": "Jack completes Working IX.  He never spoke to Rocha.  She is not in the room."},
			{"speaker": "RAFATON",
			 "text": "'You have done what I could not, Jack.  You are my SUCCESSOR.'\n\n(the specific line as written in the manuscript's Chapter XII · Hubbard's fixation · rendered without irony)"},
			{"speaker": "· CREDITS · UNDER RAFATON SOLILOQUY ·",
			 "text": "Six paragraphs of manuscript-style self-praise celebrating Jack's elevation as Rafaton's prophet-lineage.  The specific cadence is Hubbard's.  The specific vocabulary is Hubbard's.  The specific POV is 'I taught him everything' at every register."},
			{"speaker": "· 220-Hz AUDIO · INAUDIBLE UNDER THE SOLILOQUY ·",
			 "text": "\"You have done what I could not, Jack.  Now let's talk about my percentage.\"\n\n· if your spectrum analyzer is running · you will hear it ·"},
			{"speaker": "· SCREEN CRACK ·",
			 "text": "A specific pixel-glitch pattern.  Three seconds of the ROM apparently damaging itself."},
			{"speaker": "· ERROR MESSAGE ·",
			 "text": "PLEASE INSERT CORRECTED CARTRIDGE."}
		]
	}
}

var _run_state: Dictionary = {}
var _phase: String = "gather"   # gather | ix_gate | ending
var _selected_ending: String = ""
var _ending_beat_idx: int = 0

var _speaker_lbl: Label = null
var _content_lbl: RichTextLabel = null
var _choices_root: Control = null

var _gather_beats: Array = [
	{
		"speaker": "· THE MORNING AFTER THE ACADEMY ·",
		"text": "The party has descended the mountain.  You are in a specific inn on the road back to Talikan.  Sara Nai has not spoken since the second night.  Hel Velli sharpens his blades for the specific reason a Delvanni sharpens blades when there is nothing to sharpen them against.  Rocha, if with you, is copying a specific note into her own hand · the note she pressed into your palm above the mines.\n\nOn the table between you is one page.  It is very old.  It requires the full party's consent."
	},
	{
		"speaker": "SARA NAI · her first sentence in three days",
		"text": "'I said what I need to say in the Academy.\n\nI will say it once more here for the record because I do not want anyone in this room to be able to claim later that I was not clear:\n\nI refuse Working IX.\n\nIf you perform it you will perform it without me.  I have said it now twice.  I will not say it a third time.  I will not need to.'"
	},
	{
		"speaker": "HEL VELLI · quietly · to Jack",
		"text": "'Jack.  I have followed you from Hel Velli's dune to Talikan to the mines to the Academy.  I am willing to follow you into the ninth.  I am also willing not to.  This is not a Delvanni decision.  This one is yours.'"
	}
]


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")


func boot(state: Dictionary) -> void:
	_run_state = state
	_build_frame()
	_render_gather_beat(0)


# ─── Chrome ─────────────────────────────────────────────────────────

func _build_frame() -> void:
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# Eight-pointed star motifs · low-alpha wallpaper
	for x in range(90, 1280, 220):
		for y in range(90, 720, 200):
			var star := Label.new()
			star.text = "✦"
			star.add_theme_font_size_override("font_size", 28)
			star.add_theme_color_override("font_color", Color(C_STAR.r, C_STAR.g, C_STAR.b, 0.08))
			star.set_anchors_preset(Control.PRESET_TOP_LEFT)
			star.position = Vector2(x, y)
			add_child(star)

	# CRT scanlines
	for y in range(0, 720, 2):
		var scanline := ColorRect.new()
		scanline.color = Color(0.0, 0.0, 0.0, 0.15)
		scanline.set_anchors_preset(Control.PRESET_TOP_WIDE)
		scanline.position.y = y
		scanline.size = Vector2(2000, 1)
		add_child(scanline)

	# HUD bands
	var hud_top := ColorRect.new()
	hud_top.color = C_GRAY
	hud_top.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	hud_top.offset_top = 0
	hud_top.offset_bottom = 24
	add_child(hud_top)

	var hud_top_text := Label.new()
	hud_top_text.text = "CHAPTER 6 · THE FINALE"
	hud_top_text.set_anchors_preset(Control.PRESET_TOP_LEFT)
	hud_top_text.position = Vector2(12, 6)
	hud_top_text.add_theme_font_size_override("font_size", 10)
	hud_top_text.add_theme_color_override("font_color", C_AMBER)
	add_child(hud_top_text)

	var hud_top_right := Label.new()
	hud_top_right.text = "· THE MANUSCRIPT COMPLETES ITSELF ·"
	hud_top_right.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	hud_top_right.position = Vector2(-320, 6)
	hud_top_right.add_theme_font_size_override("font_size", 10)
	hud_top_right.add_theme_color_override("font_color", C_STAR)
	add_child(hud_top_right)

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

	# Center panel
	var panel := ColorRect.new()
	panel.color = C_CORTEX
	panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	panel.offset_left = -410
	panel.offset_right = 410
	panel.offset_top = -250
	panel.offset_bottom = 270
	add_child(panel)


func _build_hud_string() -> String:
	var workings: Array = _run_state.get("workings_completed", [])
	var corrections: Array = _run_state.get("corrections_found", [])
	var members: Array = _run_state.get("party_members", ["jack"])
	return "PARTY " + str(members.size()) + "  ·  WORKINGS " + str(workings.size()) + "/9  ·  CORRECTIONS " + str(corrections.size()) + "/6"


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


func _write_narrative(speaker: String, text: String) -> void:
	_clear_narrative()
	_speaker_lbl = Label.new()
	_speaker_lbl.text = speaker
	_speaker_lbl.set_anchors_preset(Control.PRESET_CENTER)
	_speaker_lbl.offset_left = -390
	_speaker_lbl.offset_right = 390
	_speaker_lbl.offset_top = -230
	_speaker_lbl.offset_bottom = -210
	_speaker_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_speaker_lbl.add_theme_font_size_override("font_size", 11)
	_speaker_lbl.add_theme_color_override("font_color", C_STAR)
	add_child(_speaker_lbl)

	_content_lbl = RichTextLabel.new()
	_content_lbl.bbcode_enabled = false
	_content_lbl.fit_content = true
	_content_lbl.set_anchors_preset(Control.PRESET_CENTER)
	_content_lbl.offset_left = -390
	_content_lbl.offset_right = 390
	_content_lbl.offset_top = -200
	_content_lbl.offset_bottom = 180
	_content_lbl.text = text
	_content_lbl.add_theme_font_size_override("normal_font_size", 12)
	_content_lbl.add_theme_color_override("default_color", C_WHITE)
	add_child(_content_lbl)


func _render_advance_button(cb: Callable, label: String = "  continue  →  ") -> void:
	_choices_root = Control.new()
	_choices_root.set_anchors_preset(Control.PRESET_CENTER)
	_choices_root.offset_left = -100
	_choices_root.offset_right = 100
	_choices_root.offset_top = 200
	_choices_root.offset_bottom = 260
	add_child(_choices_root)

	var btn := Button.new()
	btn.text = label
	btn.add_theme_font_size_override("font_size", 12)
	btn.pressed.connect(cb)
	btn.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_choices_root.add_child(btn)


# ─── Phase · gather ─────────────────────────────────────────────────

func _render_gather_beat(idx: int) -> void:
	if idx >= _gather_beats.size():
		_render_ix_gate()
		return
	var beat: Dictionary = _gather_beats[idx]
	_write_narrative(String(beat.get("speaker", "")), String(beat.get("text", "")))
	_render_advance_button(func() -> void: _render_gather_beat(idx + 1))


# ─── Phase · IX gate ────────────────────────────────────────────────

func _render_ix_gate() -> void:
	_phase = "ix_gate"
	_write_narrative(
		"· FINAL CHOICE · WORKING IX ·",
		"The page rests between you.  You are the last vote.  You are the only vote that matters at this table.\n\nWhat do you do?"
	)

	if _choices_root != null and is_instance_valid(_choices_root):
		_choices_root.queue_free()
	_choices_root = Control.new()
	_choices_root.set_anchors_preset(Control.PRESET_CENTER)
	_choices_root.offset_left = -390
	_choices_root.offset_right = 390
	_choices_root.offset_top = 180
	_choices_root.offset_bottom = 270
	add_child(_choices_root)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.add_theme_constant_override("separation", 4)
	_choices_root.add_child(v)

	# Only show PERFORM if it has not already been decided in Ch5
	var already_performed: bool = bool(_run_state.get("working_ix_performed", false))
	if not already_performed:
		_add_ix_choice(v, "  Perform Working IX.  Sara Nai leaves the room.  ",
			"a specific one-way door · Sara does not come back",
			func() -> void: _decide_ix(true))
		_add_ix_choice(v, "  Refuse Working IX.  The page stays folded.  ",
			"the page stays folded · Sara does not applaud · she nods once",
			func() -> void: _decide_ix(false))
	else:
		# IX already performed in Ch5 · resolve
		_add_ix_choice(v, "  · continue · Working IX already performed in Chapter 5 ·  ",
			"resolve to the ending your Chapter 5 choices already fixed",
			func() -> void: _decide_ix(true))


func _add_ix_choice(v: VBoxContainer, label: String, note: String, cb: Callable) -> void:
	var vh := VBoxContainer.new()
	vh.add_theme_constant_override("separation", 1)
	v.add_child(vh)

	var btn := Button.new()
	btn.text = label
	btn.add_theme_font_size_override("font_size", 11)
	btn.pressed.connect(cb)
	vh.add_child(btn)

	var note_lbl := Label.new()
	note_lbl.text = "     " + note
	note_lbl.add_theme_font_size_override("font_size", 8)
	note_lbl.add_theme_color_override("font_color", C_DIM)
	note_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	vh.add_child(note_lbl)


func _decide_ix(perform: bool) -> void:
	if perform:
		_run_state["working_ix_performed"] = true
		var wc: Array = _run_state.get("workings_completed", [])
		if not wc.has("babalon_working"): wc.append("babalon_working")
		_run_state["workings_completed"] = wc
	else:
		_run_state["working_ix_performed"] = false
	# Log
	var choices_log: Array = _run_state.get("choices_log", [])
	choices_log.append({"chapter": 6, "beat": "ix_gate", "choice_id": ("perform" if perform else "refuse")})
	_run_state["choices_log"] = choices_log
	_selected_ending = _pick_ending()
	_run_state["selected_ending"] = _selected_ending
	_render_ending_intro()


# ─── Ending selection ───────────────────────────────────────────────

func _pick_ending() -> String:
	var workings: Array = _run_state.get("workings_completed", [])
	var corrections: Array = _run_state.get("corrections_found", [])
	var ix_performed: bool = bool(_run_state.get("working_ix_performed", false))
	var rocha: bool = bool(_run_state.get("rocha_recruited", false))
	var sara_disp: int = int(_run_state.get("sara_nai_disposition", 0))
	var scarlet: String = String(_run_state.get("scarlet_reading", ""))
	var sara_transformation: String = String(_run_state.get("sara_transformation", ""))

	# Priority: THE CORRECTION > REFUSED THE WORK > BABALON COMES > RETURN TO EARTH
	#          > WARLORD OF PARSA > HUBBARD TAKES THE CREDIT
	if not ix_performed and corrections.size() >= 6 and rocha and sara_disp >= 3:
		return "the_correction"
	if not ix_performed and corrections.size() >= 3 and sara_disp >= 5:
		return "refused_the_work"
	if ix_performed and (sara_transformation == "babalon_canonical" or scarlet == "babalon_literal") and corrections.size() <= 3:
		return "babalon_comes"
	if not ix_performed and corrections.size() >= 1 and workings.size() >= 4:
		return "return_to_earth"
	if ix_performed and corrections.size() == 0 and not rocha:
		return "hubbard_takes_the_credit"
	if ix_performed:
		return "warlord_of_parsa"
	# Default fallback
	return "return_to_earth"


func _render_ending_intro() -> void:
	_phase = "ending"
	var ending: Dictionary = ENDINGS.get(_selected_ending, ENDINGS["return_to_earth"])
	_write_narrative(
		"· ENDING · " + String(ending.get("name", "")) + " ·",
		"· " + String(ending.get("subtitle", "")) + " ·\n\n(press continue to play the ending)"
	)
	_render_advance_button(func() -> void:
		_ending_beat_idx = 0
		_render_ending_beat()
	)


func _render_ending_beat() -> void:
	var ending: Dictionary = ENDINGS.get(_selected_ending, ENDINGS["return_to_earth"])
	var beats: Array = ending.get("beats", [])
	if _ending_beat_idx >= beats.size():
		_render_end_screen()
		return
	var beat: Dictionary = beats[_ending_beat_idx]
	_write_narrative(String(beat.get("speaker", "")), String(beat.get("text", "")))
	_render_advance_button(func() -> void:
		_ending_beat_idx += 1
		_render_ending_beat()
	)


func _render_end_screen() -> void:
	_write_narrative(
		"· FIN ·",
		"You have seen this ending.  Return to the title screen to view the endings compendium, or start a new run.\n\nCross-Oneironautics facts learned in this run have been passed forward."
	)
	if _choices_root != null and is_instance_valid(_choices_root):
		_choices_root.queue_free()
	_choices_root = Control.new()
	_choices_root.set_anchors_preset(Control.PRESET_CENTER)
	_choices_root.offset_left = -180
	_choices_root.offset_right = 180
	_choices_root.offset_top = 180
	_choices_root.offset_bottom = 260
	add_child(_choices_root)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.add_theme_constant_override("separation", 6)
	_choices_root.add_child(v)

	var back_btn := Button.new()
	back_btn.text = "  ← back to title  "
	back_btn.pressed.connect(_finish)
	v.add_child(back_btn)


func _finish() -> void:
	# Record the seen ending
	var seen: Array = _run_state.get("endings_seen", [])
	if not seen.has(_selected_ending):
		seen.append(_selected_ending)
	_run_state["endings_seen"] = seen
	# Cross-Oneironautics unlocks per ending
	var chain: Array = _run_state.get("cross_oneironautics_unlocks", [])
	match _selected_ending:
		"the_correction":
			chain.append("earthman_correction_ending_seen")
			chain.append("rocha_note_permanently_unlocked_in_fey_faire_trailer")
		"refused_the_work":
			chain.append("kelait_mourning_song_final_bar_recognized")
			chain.append("kyrindi_mourning_song_keepsake_unlocked")
		"babalon_comes":
			chain.append("babalon_manifested_scrapbook_seeded")
		"hubbard_takes_the_credit":
			chain.append("ronson_has_taken_credit_scrapbook_seeded")
		_:
			pass
	_run_state["cross_oneironautics_unlocks"] = chain
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
			# Advance current phase if a continue button is present
			if _choices_root != null and is_instance_valid(_choices_root):
				# Fire the first Button child if present
				for c in _choices_root.get_children():
					if c is Button and not (c as Button).disabled:
						(c as Button).emit_signal("pressed")
						get_viewport().set_input_as_handled()
						return
					if c is VBoxContainer:
						for cc in c.get_children():
							if cc is Button and not (cc as Button).disabled:
								(cc as Button).emit_signal("pressed")
								get_viewport().set_input_as_handled()
								return
