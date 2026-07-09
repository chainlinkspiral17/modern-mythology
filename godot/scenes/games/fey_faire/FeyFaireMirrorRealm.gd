extends Control
## Fey Faire · mirror sub-realms · six short vignettes accessed from
## the trailer's memory mirrors.
##
## Each mirror opens into a specific sub-realm tied to the boot
## questionnaire slot the mirror occupies.  These are text-forward
## vignettes · 3-4 beats each · one choice · one keepsake OR one
## memory restored on completion.
##
##   Mirror 1 · THE ROSE GARDEN         (bedroom)
##   Mirror 2 · THE STORM-WRACKED COAST (favorite song)
##   Mirror 3 · THE COURT BENEATH       (favorite meal)
##   Mirror 4 · THE GREEN               (holiday) · required for
##                                        BRING BACK THE LOST ending
##   Mirror 5 · THE UNDERTIDE           (parent argument)
##   Mirror 6 · THE DREAM               (first kiss)
##
## Signals:
##   quit · returns to trailer
##   mirror_completed(mirror_id, rewards) · host merges rewards
##
## F4-compliant via add_to_group("ui").

signal quit
signal mirror_completed(mirror_id: String, rewards: Dictionary)

# Rocha palette
const C_BG        := Color(0.098, 0.055, 0.114, 1.0)
const C_PANEL     := Color(0.455, 0.157, 0.282, 1.0)
const C_CREAM     := Color(0.957, 0.878, 0.816, 1.0)
const C_ROSE      := Color(0.878, 0.722, 0.753, 1.0)
const C_MAUVE     := Color(0.784, 0.557, 0.643, 1.0)
const C_GOLD      := Color(0.973, 0.784, 0.282, 1.0)
const C_GOLD_DIM  := Color(0.541, 0.361, 0.157, 1.0)
const C_DIM       := Color(0.42, 0.34, 0.30, 1.0)

# Per-mirror content · each has: name, tint (Vector3-ish RGB), beats,
# choice (offered on last beat), reward (keepsake or memory restore),
# questionnaire slot key.
const REALMS: Dictionary = {
	"mirror_1_rose_garden": {
		"name": "· MIRROR 1 · THE ROSE GARDEN ·",
		"slot": "bedroom_description",
		"tint": Color(0.62, 0.82, 0.55, 1.0),
		"beats": [
			{"speaker": "· YOU STEP THROUGH ·",
			 "text": "You put your hand flat on the silvered glass.  It gives.  You step through.\n\nThe far side is a specific garden.  Roses at every stage · buds, half-open, full, dropping petals, dry-brown, gone.  A wooden bench in the middle of the beds.  On the bench is a specific object you left in your bedroom the day you went to the Faire."},
			{"speaker": "narrator",
			 "text": "The object is: · $BEDROOM_DETAIL ·\n\nA rose-thorn Fey the size of a hummingbird lands on your knee.  It watches you.  It is waiting for you to say what the object means."},
			{"speaker": "THE ROSE-THORN FEY",
			 "text": "'Everyone who comes here brings a specific object with them.  Some know what it means.  Some don't.  Some come to find out.  Which are you?'"}
		],
		"choice": {
			"prompt": "· speak to the Rose-Thorn Fey ·",
			"options": [
				{
					"label": "  'I know what it means.  I brought it on purpose.'  ",
					"note": "The Fey nods once.  You are given a rose keepsake · your bedroom-mirror stays uncracked.",
					"rewards": {"keepsake": "rose_from_the_mirror", "seelie_delta": 2}
				},
				{
					"label": "  'I don't know.  I want to.'  ",
					"note": "The Fey sits with you.  It tells you what it thinks the object means.  You listen.  Memory 1 (bedroom) is protected from cracking for this run.",
					"rewards": {"keepsake": "rose_thorn_confidant", "memory_protected": "bedroom_description", "seelie_delta": 1, "wildfey_delta": 1}
				},
				{
					"label": "  'I do not want to say aloud what it means.'  ",
					"note": "The Fey nods.  It takes off.  You keep the object.  No keepsake this time.  You leave lighter than you came in.",
					"rewards": {"seelie_delta": 1}
				}
			]
		}
	},
	"mirror_2_storm_coast": {
		"name": "· MIRROR 2 · THE STORM-WRACKED COAST ·",
		"slot": "favorite_song",
		"tint": Color(0.55, 0.72, 0.94, 1.0),
		"beats": [
			{"speaker": "· YOU STEP THROUGH ·",
			 "text": "A specific coast.  The rain has just stopped; the wind has not.  On the tide line is a specific radio.  It has salt-corrosion on the dial but it is playing.\n\nThe song playing is: · $FAVORITE_SONG ·"},
			{"speaker": "narrator",
			 "text": "The song plays through once.  A specific Kelpie-shaped fey walks up out of the surf.  Her mane is heavy with water.  She is beautiful in a way that makes you feel your bones."},
			{"speaker": "THE KELPIE",
			 "text": "'The radio has been playing your song for six years without stopping.  I have been listening.  I like it.\n\nI can give you two things.  I cannot give you three.  Choose.'"}
		],
		"choice": {
			"prompt": "· choose two ·",
			"options": [
				{
					"label": "  · A verse to the song nobody else has heard, and the memory of hearing it here.  ",
					"note": "You gain a specific Shakespeare-flavored quote unlocked for RECITE · a hidden verse of your song is added to the trailer bookcase.",
					"rewards": {"quote_unlocked": "kelpie_verse", "keepsake": "hidden_verse_of_your_song", "unseelie_delta": 1}
				},
				{
					"label": "  · The radio, taken out of this mirror and into your pocket.  It will play the song forever.  ",
					"note": "The radio is yours.  It plays the song on repeat.  You lose the memory of ever having a favorite song outside it (Mirror 2 cracks).",
					"rewards": {"keepsake": "kelpie_radio", "memories_lost_delta": 1}
				},
				{
					"label": "  · The Kelpie's true name, whispered in your ear.  Everything else stays here.  ",
					"note": "You learn the Kelpie's true name.  You may recruit her via RECITE at negotiation later.  She swims off.",
					"rewards": {"true_name_learned": "kelpie", "wildfey_delta": 2}
				}
			]
		}
	},
	"mirror_3_court_beneath": {
		"name": "· MIRROR 3 · THE COURT BENEATH ·",
		"slot": "favorite_meal",
		"tint": Color(0.55, 0.35, 0.68, 1.0),
		"beats": [
			{"speaker": "· YOU STEP THROUGH ·",
			 "text": "A long table.  Set for a banquet.  Every place is filled by a fey you have never seen before · Unseelie, formal, wearing black.  At the head of the table is a plate with your name on it.  On the plate is: · $FAVORITE_MEAL ·\n\nOberon is at the far end.  He nods to you specifically."},
			{"speaker": "narrator",
			 "text": "The rule of the Court Beneath is well known: eat their food, stay forever.  Refuse the meal, offer nothing, they take offense.  You know both these rules from bedtime stories."},
			{"speaker": "OBERON",
			 "text": "'Sit.  Take one bite · a specific one bite · that is the compromise.  My court accepts one-bite guests.  What do you do?'"}
		],
		"choice": {
			"prompt": "· sit or don't ·",
			"options": [
				{
					"label": "  Take one bite.  Only one.  ",
					"note": "You take one bite.  The meal is exactly as good as you remember.  Oberon nods once.  Your Unseelie alignment climbs.",
					"rewards": {"unseelie_delta": 3, "keepsake": "bite_of_the_court", "oberon_disposition_delta": 1}
				},
				{
					"label": "  Take no bite.  Bow instead.  Say you cannot accept.  ",
					"note": "Oberon respects the bow.  He does not respect the refusal.  Neutral outcome.  You get an Unseelie recognition token but no keepsake.",
					"rewards": {"unseelie_delta": 1}
				},
				{
					"label": "  Offer them something in return.  A memory of the meal at your grandmother's table.  ",
					"note": "You give up Mirror 3 (favorite_meal cracks).  In exchange Oberon promises one favor.  Specific, uncashed, on-file.",
					"rewards": {"memories_lost_delta": 1, "oberon_promise_on_file": true, "unseelie_delta": 2}
				}
			]
		}
	},
	"mirror_4_the_green": {
		"name": "· MIRROR 4 · THE GREEN ·",
		"slot": "holiday",
		"tint": Color(0.35, 0.68, 0.35, 1.0),
		"beats": [
			{"speaker": "· YOU STEP THROUGH ·",
			 "text": "A clearing in a forest that is not a forest you have been in.  Dawn light through the canopy.  A specific holiday from your life plays out in miniature at the center of the clearing · a specific tabletop-sized diorama of it, complete with figures.\n\nThe figures are moving.  The holiday you chose is: · $HOLIDAY ·"},
			{"speaker": "narrator",
			 "text": "One figure is missing.  You know which one.  You have known which one for a long time.\n\nThe Green Man stands at the edge of the clearing.  He has been there the whole time.  He is very still.  He is very old."},
			{"speaker": "THE GREEN MAN",
			 "text": "'You have found me.  The mirror opens for people who are looking for a specific person.  You are looking for a specific person.  What do you offer?'"}
		],
		"choice": {
			"prompt": "· offer to the Green Man ·",
			"options": [
				{
					"label": "  A promise.  On the Faire's next return, you will find him and give what he asks.  ",
					"note": "The Green Man accepts the promise.  Mirror 4 is COMPLETED · this is required for BRING BACK THE LOST.  His disposition rises.",
					"rewards": {"mirror_4_the_green_completed": true, "green_man_disposition_delta": 3, "wildfey_delta": 2}
				},
				{
					"label": "  A memory.  Take the holiday itself.  Give it up.  ",
					"note": "Mirror 4 completes AND cracks · rare.  The Green Man is impressed by the offer.  He may recruit you into his court later.",
					"rewards": {"mirror_4_the_green_completed": true, "memories_lost_delta": 1, "green_man_disposition_delta": 4, "wildfey_delta": 3}
				},
				{
					"label": "  Nothing.  Just look at the diorama for a specific length of time.  Walk out.  ",
					"note": "You walked away.  Mirror 4 not completed.  You can come back.  The Green Man waits with the patience of a tree.",
					"rewards": {}
				}
			]
		}
	},
	"mirror_5_undertide": {
		"name": "· MIRROR 5 · THE UNDERTIDE ·",
		"slot": "parent_argument",
		"tint": Color(0.35, 0.42, 0.68, 1.0),
		"beats": [
			{"speaker": "· YOU STEP THROUGH ·",
			 "text": "A specific hallway of your childhood house.  You are outside a specific closed door.  On the other side of the door is the specific argument you had with a parent · the one you recorded on the questionnaire · playing out again.  You can hear it.  You cannot see it.\n\nThe fey here is not visible either.  Its voice is under the water in the house's pipes."},
			{"speaker": "THE UNDERTIDE (a specific voice in the pipes)",
			 "text": "'This argument does not end here.  It ends specifically later, in a specific way, when you are older.  Would you like to see how?'"}
		],
		"choice": {
			"prompt": "· see the ending? ·",
			"options": [
				{
					"label": "  Yes.  Show me.  ",
					"note": "The Undertide shows you the argument's actual future ending.  Whether it is good or bad depends on your $PARENT_ARGUMENT text.  You gain the 'undertide postcard' keepsake describing what happens.",
					"rewards": {"keepsake": "undertide_postcard", "unseelie_delta": 1, "wildfey_delta": 1}
				},
				{
					"label": "  No.  I don't want to know.  ",
					"note": "The Undertide is not offended.  It has been asked no many times.  You leave the mirror with an unopened envelope keepsake instead.",
					"rewards": {"keepsake": "undertide_unopened_envelope", "seelie_delta": 1}
				},
				{
					"label": "  Open the door.  Speak.  Interrupt yourself at the age you were.  ",
					"note": "Rare · you speak to your younger self.  You give up Mirror 5 (parent_argument cracks) in exchange for a specific different memory of the same night.  A rare thing.",
					"rewards": {"memories_lost_delta": 1, "keepsake": "undertide_rewritten_night", "unseelie_delta": 2}
				}
			]
		}
	},
	"mirror_6_dream": {
		"name": "· MIRROR 6 · THE DREAM ·",
		"slot": "first_kiss",
		"tint": Color(0.878, 0.722, 0.753, 1.0),
		"beats": [
			{"speaker": "· YOU STEP THROUGH ·",
			 "text": "A specific corner of your life you did not choose to remember.  The first-kiss moment.  It is playing out in slow motion.  A specific detail is different from how you remember it.\n\nMoth stands at the edge of the scene.  She has been walking specific slow circles around this scene for as long as it has existed inside you."},
			{"speaker": "MOTH",
			 "text": "'This is the mirror I take care of.  I have made small changes to the memory over the years.  I have not asked permission.  I am asking now.  Do you want the changes reverted?'"}
		],
		"choice": {
			"prompt": "· speak to Moth ·",
			"options": [
				{
					"label": "  Yes.  Revert the changes.  I want the memory as it actually was.  ",
					"note": "Moth reverts.  You now remember the first kiss more accurately.  It is slightly less romantic and slightly more honest.  You gain the 'restored kiss' keepsake.  Seelie alignment falls.  Wildfey rises.",
					"rewards": {"keepsake": "restored_first_kiss", "seelie_delta": -1, "wildfey_delta": 2}
				},
				{
					"label": "  No.  Keep the changes.  I like the version she made.  ",
					"note": "Moth nods.  You may return to this mirror later to change your mind.  She gives you the 'moth's edit' keepsake acknowledging the arrangement.",
					"rewards": {"keepsake": "moths_edit", "seelie_delta": 2}
				},
				{
					"label": "  Recruit Moth.  Ask her to take her time to keep editing the whole rest of your life.  ",
					"note": "Very rare.  Moth accepts.  She joins the party permanently.  All future memories will be gently edited by her.  Wildfey +3.  Seelie -3.  Moth is now recruited without a booth negotiation.",
					"rewards": {"fey_recruited": "moth", "wildfey_delta": 3, "seelie_delta": -3, "keepsake": "moths_permanent_arrangement"}
				}
			]
		}
	}
}

var _run_state: Dictionary = {}
var _mirror_id: String = ""
var _realm: Dictionary = {}
var _beat_idx: int = 0

var _speaker_lbl: Label = null
var _content_lbl: RichTextLabel = null
var _choices_root: Control = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")


func boot(state: Dictionary) -> void:
	_run_state = state.get("run_state", state)
	_mirror_id = String(state.get("mirror_id", ""))
	_realm = REALMS.get(_mirror_id, REALMS["mirror_1_rose_garden"])
	_beat_idx = 0
	_build_frame()
	_render_current_beat()


func _build_frame() -> void:
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# Tint-flavored ripple stripes at top matching the mirror's realm
	var tint: Color = _realm.get("tint", C_GOLD)
	for x in range(60, 1280, 90):
		var stripe := ColorRect.new()
		stripe.color = Color(tint.r, tint.g, tint.b, 0.35)
		stripe.set_anchors_preset(Control.PRESET_TOP_LEFT)
		stripe.position = Vector2(x, 0)
		stripe.size = Vector2(6, 60)
		add_child(stripe)

	var header := Label.new()
	header.text = String(_realm.get("name", "· MIRROR ·"))
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 14)
	header.add_theme_color_override("font_color", tint)
	header.set_anchors_preset(Control.PRESET_TOP_WIDE)
	header.offset_top = 68
	header.offset_bottom = 96
	add_child(header)

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
	_speaker_lbl.text = "· " + speaker.strip_edges().to_upper() + " ·"
	_speaker_lbl.set_anchors_preset(Control.PRESET_CENTER)
	_speaker_lbl.offset_left = -400
	_speaker_lbl.offset_right = 400
	_speaker_lbl.offset_top = -200
	_speaker_lbl.offset_bottom = -178
	_speaker_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_speaker_lbl.add_theme_font_size_override("font_size", 11)
	_speaker_lbl.add_theme_color_override("font_color", _realm.get("tint", C_GOLD))
	add_child(_speaker_lbl)

	_content_lbl = RichTextLabel.new()
	_content_lbl.bbcode_enabled = false
	_content_lbl.fit_content = true
	_content_lbl.set_anchors_preset(Control.PRESET_CENTER)
	_content_lbl.offset_left = -400
	_content_lbl.offset_right = 400
	_content_lbl.offset_top = -168
	_content_lbl.offset_bottom = 140
	_content_lbl.text = _substitute(text)
	_content_lbl.add_theme_font_size_override("normal_font_size", 12)
	_content_lbl.add_theme_color_override("default_color", C_CREAM)
	add_child(_content_lbl)


func _substitute(text: String) -> String:
	var q: Dictionary = _run_state.get("questionnaire", {})
	var s := text
	s = s.replace("$PLAYER_NAME", String(q.get("player_name", "you")))
	s = s.replace("$LOST_PERSON", String(q.get("lost_person_name", "someone")))
	s = s.replace("$BEDROOM_DETAIL", String(q.get("bedroom_description", "an object you left there")))
	s = s.replace("$FAVORITE_SONG", String(q.get("favorite_song", "a song you like")))
	s = s.replace("$FAVORITE_MEAL", String(q.get("favorite_meal", "a meal you know")))
	s = s.replace("$HOLIDAY", String(q.get("holiday", "a holiday that matters")))
	s = s.replace("$PARENT_ARGUMENT", String(q.get("parent_argument", "an argument")))
	s = s.replace("$FIRST_KISS", String(q.get("first_kiss", "a first kiss")))
	return s


func _render_current_beat() -> void:
	var beats: Array = _realm.get("beats", [])
	if _beat_idx < beats.size():
		var beat: Dictionary = beats[_beat_idx]
		_write(String(beat.get("speaker", "")), String(beat.get("text", "")))
		_render_continue()
	else:
		_render_choice()


func _render_continue() -> void:
	_choices_root = Control.new()
	_choices_root.set_anchors_preset(Control.PRESET_CENTER)
	_choices_root.offset_left = -100
	_choices_root.offset_right = 100
	_choices_root.offset_top = 160
	_choices_root.offset_bottom = 220
	add_child(_choices_root)

	var btn := Button.new()
	btn.text = "  continue  →  "
	btn.add_theme_font_size_override("font_size", 12)
	btn.add_theme_color_override("font_color", _realm.get("tint", C_GOLD))
	btn.pressed.connect(func() -> void:
		_beat_idx += 1
		_render_current_beat()
	)
	btn.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_choices_root.add_child(btn)


func _render_choice() -> void:
	var choice: Dictionary = _realm.get("choice", {})
	_write("· CHOICE ·", String(choice.get("prompt", "· choose ·")))

	_choices_root = Control.new()
	_choices_root.set_anchors_preset(Control.PRESET_CENTER)
	_choices_root.offset_left = -400
	_choices_root.offset_right = 400
	_choices_root.offset_top = 100
	_choices_root.offset_bottom = 270
	add_child(_choices_root)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.add_theme_constant_override("separation", 4)
	_choices_root.add_child(v)

	for opt_v in choice.get("options", []):
		var opt: Dictionary = opt_v
		var vh := VBoxContainer.new()
		vh.add_theme_constant_override("separation", 1)
		v.add_child(vh)

		var btn := Button.new()
		btn.text = String(opt.get("label", ""))
		btn.add_theme_font_size_override("font_size", 10)
		btn.pressed.connect(func() -> void: _resolve(opt))
		vh.add_child(btn)

		var note := Label.new()
		note.text = "     " + String(opt.get("note", ""))
		note.add_theme_font_size_override("font_size", 8)
		note.add_theme_color_override("font_color", C_DIM)
		note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		vh.add_child(note)


func _resolve(opt: Dictionary) -> void:
	var rewards: Dictionary = opt.get("rewards", {})
	# Mark realm completed (whichever the id is) unless the option
	# is an explicit "walked out" no-completion.
	if not rewards.is_empty():
		var completed: Array = _run_state.get("mirrors_completed", [])
		if not completed.has(_mirror_id):
			completed.append(_mirror_id)
		_run_state["mirrors_completed"] = completed
	# Emit up · host applies deltas and keepsakes
	_write(
		"· THE MIRROR RELEASES YOU ·",
		"The reflection settles back into silver.\n\nYou are standing in front of the mirror again.  The trailer is quiet.  Helia has not moved from the desk.\n\n· press continue to return ·"
	)
	if _choices_root != null and is_instance_valid(_choices_root):
		_choices_root.queue_free()
	_choices_root = Control.new()
	_choices_root.set_anchors_preset(Control.PRESET_CENTER)
	_choices_root.offset_left = -140
	_choices_root.offset_right = 140
	_choices_root.offset_top = 160
	_choices_root.offset_bottom = 220
	add_child(_choices_root)

	var back_btn := Button.new()
	back_btn.text = "  · return to the trailer ·  "
	back_btn.add_theme_font_size_override("font_size", 12)
	back_btn.add_theme_color_override("font_color", C_GOLD)
	back_btn.pressed.connect(func() -> void: mirror_completed.emit(_mirror_id, rewards))
	back_btn.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_choices_root.add_child(back_btn)


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			quit.emit()
			get_viewport().set_input_as_handled()
