extends Control
## Fey Faire · The Big Top · nightly Shakespeare show.
##
## The Big Top runs one show per night.  The cast is fey (Titania
## plays Titania · Puck plays Puck · Bottom is a specific unnamed
## goblin) and the play rotates by night_index:
##
##   Night 1 · A MIDSUMMER NIGHT'S DREAM (Titania soliloquy)
##   Night 2 · THE TEMPEST                (Ariel · Prospero absent)
##   Night 3 · HAMLET                     (the play-within-the-play)
##   Night 4 · MACBETH                    (Hecate · three witches)
##   Night 5 · KING LEAR                  (Fool · storm scene)
##   Night 6 · [YOUR NAME]                (the play written for you)
##
## The show is a text-forward vignette · 5-6 beats · closes with a
## playbill keepsake grant + one new quote unlocked for negotiation
## RECITE moves.  Attending advances no state on its own · REST at
## a recruited booth is what advances the night.
##
## Signals:
##   finished(rewards: Dictionary) · host merges rewards into state
##   quit · returns to midway
##
## F4-compliant via add_to_group("ui").

signal finished(rewards: Dictionary)
signal quit

# Rocha palette
const C_BG        := Color(0.157, 0.094, 0.173, 1.0)
const C_PANEL     := Color(0.455, 0.157, 0.282, 1.0)
const C_PANEL_DIM := Color(0.28, 0.10, 0.18, 1.0)
const C_CREAM     := Color(0.957, 0.878, 0.816, 1.0)
const C_ROSE      := Color(0.878, 0.722, 0.753, 1.0)
const C_MAUVE     := Color(0.784, 0.557, 0.643, 1.0)
const C_GOLD      := Color(0.973, 0.784, 0.282, 1.0)
const C_GOLD_DIM  := Color(0.541, 0.361, 0.157, 1.0)
const C_DIM       := Color(0.42, 0.34, 0.30, 1.0)

# Shows keyed by night.  Each show: title, playbill, cast, beats,
# quote_unlocked (one Shakespeare line the player can then RECITE
# in negotiations), keepsake_id.
const SHOWS: Dictionary = {
	1: {
		"title": "A MIDSUMMER NIGHT'S DREAM",
		"playbill": "Titania · playing herself · with Puck as chorus",
		"director": "OBERON (uncredited)",
		"beats": [
			{"speaker": "PUCK, prologue",
			 "line": "If we shadows have offended,\nThink but this, and all is mended · That you have but slumbered here\nWhile these visions did appear."},
			{"speaker": "TITANIA, on stage as herself",
			 "line": "Set your heart at rest ·\nThe fairy land buys not the child of me."},
			{"speaker": "TITANIA, still",
			 "line": "The human mortals want their winter here.\nNo night is now with hymn or carol blest."},
			{"speaker": "narrator",
			 "line": "A mortal in the audience recognizes the child she means.  A mortal in the audience is you.\nThe recognition is a hook that goes in easy and comes out slow."},
			{"speaker": "PUCK, epilogue",
			 "line": "Give me your hands, if we be friends,\nAnd Robin shall restore amends."}
		],
		"quote_unlocked": {"id": "midsummer_shadows", "text": "If we shadows have offended, think but this, and all is mended."},
		"keepsake_id": "playbill_midsummer"
	},
	2: {
		"title": "THE TEMPEST",
		"playbill": "Ariel · playing herself · Prospero's role read by a folding chair",
		"director": "PROSPERO (absent · offstage · the cat)",
		"beats": [
			{"speaker": "ARIEL, from the wire above the stage",
			 "line": "Full fathom five thy father lies ·\nOf his bones are coral made ·\nThose are pearls that were his eyes ·"},
			{"speaker": "ARIEL, alighting",
			 "line": "Nothing of him that doth fade,\nBut doth suffer a sea-change\nInto something rich and strange."},
			{"speaker": "narrator",
			 "line": "The folding chair says nothing.  The audience treats the chair with a specific respect.\nTheir respect is not for the chair."},
			{"speaker": "ARIEL, to the chair",
			 "line": "Where the bee sucks, there suck I ·\nIn a cowslip's bell I lie ·\nMerrily merrily shall I live now\nUnder the blossom that hangs on the bough."},
			{"speaker": "narrator",
			 "line": "The bough grows through the tent's canvas.  The blossom is in your hair when you leave."}
		],
		"quote_unlocked": {"id": "tempest_seachange", "text": "Doth suffer a sea-change into something rich and strange."},
		"keepsake_id": "playbill_tempest"
	},
	3: {
		"title": "HAMLET",
		"playbill": "The Mousetrap · a play within a play · cast entirely of fey playing mortals playing fey",
		"director": "the ghost",
		"beats": [
			{"speaker": "HAMLET, on stage",
			 "line": "The play's the thing\nWherein I'll catch the conscience of the king."},
			{"speaker": "narrator",
			 "line": "The play within the play is about the Fair Folk stealing a child.\nThe audience is quiet in a specific way."},
			{"speaker": "GHOST, from the wing",
			 "line": "Remember me."},
			{"speaker": "narrator",
			 "line": "Someone in row three stands up and walks out.  Cricket at the door does not stop them.  They did not have a ticket.\nThey did not need one."},
			{"speaker": "HAMLET, closing",
			 "line": "The rest is silence."}
		],
		"quote_unlocked": {"id": "hamlet_remember", "text": "Remember me."},
		"keepsake_id": "playbill_hamlet"
	},
	4: {
		"title": "MACBETH",
		"playbill": "Hecate presiding · three witches played by three witches",
		"director": "the moon (waning)",
		"beats": [
			{"speaker": "WITCH ONE",
			 "line": "When shall we three meet again\nIn thunder, lightning, or in rain?"},
			{"speaker": "WITCH TWO",
			 "line": "When the hurlyburly's done,\nWhen the battle's lost and won."},
			{"speaker": "HECATE, entering",
			 "line": "By the pricking of my thumbs,\nSomething wicked this way comes."},
			{"speaker": "narrator",
			 "line": "The something-wicked is you.  The witches turn their heads.  You are seated in row seven.\nThey nod at you like they have been expecting you.  Which they have."},
			{"speaker": "MACBETH, offstage",
			 "line": "Life's but a walking shadow, a poor player\nThat struts and frets his hour upon the stage\nAnd then is heard no more."}
		],
		"quote_unlocked": {"id": "macbeth_thumbs", "text": "By the pricking of my thumbs, something wicked this way comes."},
		"keepsake_id": "playbill_macbeth"
	},
	5: {
		"title": "KING LEAR",
		"playbill": "The Fool · in a rabbit costume that is not a costume",
		"director": "the storm",
		"beats": [
			{"speaker": "LEAR, on the heath",
			 "line": "Blow, winds, and crack your cheeks!  Rage!  Blow!\nYou cataracts and hurricanoes, spout\nTill you have drenched our steeples."},
			{"speaker": "FOOL, in rabbit ears",
			 "line": "He that has and a little tiny wit ·\nWith heigh-ho, the wind and the rain ·\nMust make content with his fortunes fit,\nThough the rain it raineth every day."},
			{"speaker": "narrator",
			 "line": "The storm inside the tent is a specific real storm.  The canvas holds.  Your hair is not wet.\nWhen you look at your palm it is wet."},
			{"speaker": "LEAR, holding nothing",
			 "line": "Never, never, never, never, never."},
			{"speaker": "FOOL, gentle",
			 "line": "I'll go to bed at noon."}
		],
		"quote_unlocked": {"id": "lear_never", "text": "Never, never, never, never, never."},
		"keepsake_id": "playbill_lear"
	},
	6: {
		"title": "[YOUR NAME] · A NEW PLAY",
		"playbill": "A play in one act · written for tonight · one performance only",
		"director": "(you)",
		"beats": [
			{"speaker": "narrator",
			 "line": "The playbill has your name on it in Ondine's handwriting.  The cast list is every fey you recruited.\nThe empty roles are the ones you did not."},
			{"speaker": "OPENING LINE, whoever leads your party",
			 "line": "This is the story of a mortal who came to Fey Faire looking for something.\nWhether they found it depends on which of us stands with them at the end."},
			{"speaker": "narrator",
			 "line": "The play is short.  It rhymes when it wants to.  It ends with a specific question."},
			{"speaker": "CHORUS · your recruited feys, together",
			 "line": "Will you stay?  Or will you go?\nSix nights we have given you.  The seventh is yours."},
			{"speaker": "narrator",
			 "line": "The audience does not applaud.  They wait for your answer.\nYou do not have to answer tonight."}
		],
		"quote_unlocked": {"id": "your_name_seventh", "text": "Six nights we have given you.  The seventh is yours."},
		"keepsake_id": "playbill_your_name"
	}
}

var _run_state: Dictionary = {}
var _night: int = 1
var _beat_index: int = 0
var _show: Dictionary = {}


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")


func boot(state: Dictionary) -> void:
	_run_state = state
	_night = int(_run_state.get("night", 1))
	_night = clamp(_night, 1, 6)
	_show = SHOWS.get(_night, SHOWS[1])
	_beat_index = 0
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

	# Mauve tent-stripe wall · full-height on this scene
	for x in range(60, 1280, 90):
		var stripe := ColorRect.new()
		stripe.color = C_MAUVE
		stripe.set_anchors_preset(Control.PRESET_TOP_LEFT)
		stripe.position = Vector2(x, 0)
		stripe.size = Vector2(6, 60)
		add_child(stripe)

	# Header · playbill
	var header := Label.new()
	header.text = "· THE BIG TOP · NIGHT " + str(_night) + " OF 6 ·"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 12)
	header.add_theme_color_override("font_color", C_GOLD_DIM)
	header.set_anchors_preset(Control.PRESET_TOP_WIDE)
	header.offset_top = 60
	header.offset_bottom = 82
	add_child(header)

	var title_lbl := Label.new()
	title_lbl.text = String(_show.get("title", ""))
	title_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title_lbl.add_theme_font_size_override("font_size", 22)
	title_lbl.add_theme_color_override("font_color", C_GOLD)
	title_lbl.set_anchors_preset(Control.PRESET_TOP_WIDE)
	title_lbl.offset_top = 90
	title_lbl.offset_bottom = 124
	add_child(title_lbl)

	var playbill := Label.new()
	playbill.text = String(_show.get("playbill", ""))
	playbill.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	playbill.add_theme_font_size_override("font_size", 10)
	playbill.add_theme_color_override("font_color", C_ROSE)
	playbill.set_anchors_preset(Control.PRESET_TOP_WIDE)
	playbill.offset_top = 130
	playbill.offset_bottom = 148
	add_child(playbill)

	var director := Label.new()
	director.text = "directed by " + String(_show.get("director", ""))
	director.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	director.add_theme_font_size_override("font_size", 9)
	director.add_theme_color_override("font_color", C_GOLD_DIM)
	director.set_anchors_preset(Control.PRESET_TOP_WIDE)
	director.offset_top = 150
	director.offset_bottom = 166
	add_child(director)

	# HeroImage · big top interior · right side, out of the way of the panel
	var hero := HeroImage.new()
	if hero.load_from("res://resources/games/vol7/fey_faire/hero_images/big_top_interior.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(220, 124))
		tex_rect.set_anchors_preset(Control.PRESET_TOP_RIGHT)
		tex_rect.position = Vector2(-240, 60)
		tex_rect.size = Vector2(220, 124)
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		add_child(tex_rect)

	# Central panel
	var panel := ColorRect.new()
	panel.color = C_PANEL
	panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	panel.offset_left = -420
	panel.offset_right = 420
	panel.offset_top = -180
	panel.offset_bottom = 200
	add_child(panel)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -400
	v.offset_right = 400
	v.offset_top = -160
	v.offset_bottom = 180
	v.add_theme_constant_override("separation", 14)
	add_child(v)

	var beats: Array = _show.get("beats", [])
	if _beat_index < beats.size():
		var beat: Dictionary = beats[_beat_index]

		var speaker := Label.new()
		speaker.text = "· " + String(beat.get("speaker", "")).to_upper() + " ·"
		speaker.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		speaker.add_theme_font_size_override("font_size", 10)
		speaker.add_theme_color_override("font_color", C_GOLD_DIM)
		v.add_child(speaker)

		var line := RichTextLabel.new()
		line.bbcode_enabled = false
		line.fit_content = true
		line.custom_minimum_size = Vector2(760, 120)
		line.text = String(beat.get("line", ""))
		line.add_theme_font_size_override("normal_font_size", 13)
		line.add_theme_color_override("default_color", C_CREAM)
		v.add_child(line)

		var spacer := Control.new()
		spacer.custom_minimum_size = Vector2(0, 18)
		v.add_child(spacer)

		var progress := Label.new()
		progress.text = "· " + str(_beat_index + 1) + " / " + str(beats.size()) + " ·"
		progress.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		progress.add_theme_font_size_override("font_size", 9)
		progress.add_theme_color_override("font_color", C_DIM)
		v.add_child(progress)

		var next_btn := Button.new()
		if _beat_index + 1 < beats.size():
			next_btn.text = "  ▸ continue  "
		else:
			next_btn.text = "  · curtain ·  "
		next_btn.add_theme_font_size_override("font_size", 12)
		next_btn.add_theme_color_override("font_color", C_GOLD)
		next_btn.pressed.connect(_on_next_beat_pressed)
		v.add_child(next_btn)

		var leave_btn := Button.new()
		leave_btn.text = "  · leave early ·  "
		leave_btn.add_theme_font_size_override("font_size", 10)
		leave_btn.pressed.connect(_on_leave_pressed)
		v.add_child(leave_btn)
	else:
		# Show complete · rewards + exit
		_render_curtain(v)


func _render_curtain(v: VBoxContainer) -> void:
	var quote_data: Dictionary = _show.get("quote_unlocked", {})
	var keepsake_id: String = String(_show.get("keepsake_id", ""))

	var already_have_kp := false
	var already_have_q := false
	var kp_list: Array = _run_state.get("keepsakes", [])
	if kp_list.has(keepsake_id): already_have_kp = true
	var q_list: Array = _run_state.get("unlocked_quotes", [])
	if q_list.has(String(quote_data.get("id", ""))): already_have_q = true

	var applause := Label.new()
	applause.text = "· CURTAIN ·"
	applause.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	applause.add_theme_font_size_override("font_size", 18)
	applause.add_theme_color_override("font_color", C_GOLD)
	v.add_child(applause)

	var kp_lbl := Label.new()
	if already_have_kp:
		kp_lbl.text = "· you already have tonight's playbill ·"
		kp_lbl.add_theme_color_override("font_color", C_GOLD_DIM)
	else:
		kp_lbl.text = "· keepsake added to trailer · " + keepsake_id + " ·"
		kp_lbl.add_theme_color_override("font_color", C_ROSE)
	kp_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	kp_lbl.add_theme_font_size_override("font_size", 11)
	v.add_child(kp_lbl)

	var q_lbl := Label.new()
	if already_have_q:
		q_lbl.text = "· you already know this line by heart ·"
		q_lbl.add_theme_color_override("font_color", C_GOLD_DIM)
	else:
		q_lbl.text = "· new line learned for RECITE · \"" + String(quote_data.get("text", "")) + "\""
		q_lbl.add_theme_color_override("font_color", C_ROSE)
	q_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	q_lbl.add_theme_font_size_override("font_size", 10)
	q_lbl.custom_minimum_size = Vector2(760, 40)
	v.add_child(q_lbl)

	var sep := Control.new()
	sep.custom_minimum_size = Vector2(0, 16)
	v.add_child(sep)

	var exit_btn := Button.new()
	exit_btn.text = "  · leave the tent · return to the midway ·  "
	exit_btn.add_theme_font_size_override("font_size", 12)
	exit_btn.add_theme_color_override("font_color", C_GOLD)
	exit_btn.pressed.connect(_on_finish_pressed)
	v.add_child(exit_btn)


func _on_next_beat_pressed() -> void:
	_beat_index += 1
	_render()


func _on_leave_pressed() -> void:
	# Leaving early forfeits the rewards
	quit.emit()


func _on_finish_pressed() -> void:
	var rewards: Dictionary = {
		"keepsake_id": String(_show.get("keepsake_id", "")),
		"quote_id": String(_show.get("quote_unlocked", {}).get("id", "")),
		"quote_text": String(_show.get("quote_unlocked", {}).get("text", "")),
		"night_attended": _night
	}
	finished.emit(rewards)


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			quit.emit()
			get_viewport().set_input_as_handled()
