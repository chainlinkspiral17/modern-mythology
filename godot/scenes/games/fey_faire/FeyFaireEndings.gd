extends Control
## Fey Faire · endings · Night 6 finale + ending selection.
##
## Trigger: entered on Night 6 by explicit finale gate (from midway
## when night_index has passed 6, OR from Big Top after Night 6's
## [YOUR NAME] show completes).
##
## Selects one of seven endings from the accumulated state:
##
##   1. A ROSE               · seelie · Titania LIKED+ · half promises kept
##   2. A RED CAP            · unseelie · Oberon LIKED+ · 2+ unseelie recruits
##   3. A STAG'S ANTLER      · wildfey · Green Man LIKED+
##   4. REFUSED THE FAIRE    · left before night 3 · few recruits
##   5. BECOME THE FAIRE     · Cricket LOVED · courts all under 3 (neutral)
##   6. BRING BACK THE LOST  · wildfey 8+ · Green Man LOVED · mirror 4 done
##   7. YOU FORGET WHY YOU CAME · all 6 memories lost
##
## Structure mirrors Earthman Ch6: Night-6 gather beats → optional
## explicit finale choices → ending beat-sequence playback → return.
##
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal finished(canon_vars: Dictionary, lore_tokens: Array)

# Rocha palette
const C_BG        := Color(0.157, 0.094, 0.173, 1.0)
const C_PANEL     := Color(0.455, 0.157, 0.282, 1.0)
const C_PANEL_DIM := Color(0.28, 0.10, 0.18, 1.0)
const C_CREAM     := Color(0.957, 0.878, 0.816, 1.0)
const C_ROSE      := Color(0.878, 0.722, 0.753, 1.0)
const C_MAUVE     := Color(0.87, 0.68, 0.76, 1.0)
const C_GOLD      := Color(0.973, 0.784, 0.282, 1.0)
const C_GOLD_DIM  := Color(0.72, 0.52, 0.26, 1.0)
const C_DIM       := Color(0.62, 0.53, 0.47, 1.0)
const C_SEELIE    := Color(0.62, 0.82, 0.55, 1.0)
const C_UNSEELIE  := Color(0.55, 0.35, 0.68, 1.0)
const C_WILDFEY   := Color(0.82, 0.62, 0.35, 1.0)

# Ending scripts inline · each ending is a list of beats with a
# specific tint color that flavors the panel header.
const ENDINGS: Dictionary = {
	"a_rose": {
		"name": "· A ROSE ·",
		"subtitle": "the seelie ending",
		"tint": Color(0.62, 0.82, 0.55, 1.0),
		"beats": [
			{"speaker": "· TALIKAN · AT FIRST LIGHT ·",
			 "text": "A specific window opens outward.  You leave the Faire with a rose in your buttonhole."},
			{"speaker": "narrator",
			 "text": "The rose does not wilt.  You keep your name.  You keep your face.  You keep every friend you had.  You no longer remember the specific season that specific loss (from $LOST_PERSON) happened in.  You catch yourself humming a Midsummer song at odd moments."},
			{"speaker": "narrator",
			 "text": "Titania keeps her promise to you.  Ondine watches you leave through the Gate.  The rose blooms in your buttonhole for exactly one year."},
			{"speaker": "· STILL IMAGE ·",
			 "text": "$PLAYER_NAME's front door in $CITY · a specific morning · the rose visible on the coat rack.  Three seconds held."}
		]
	},
	"a_red_cap": {
		"name": "· A RED CAP ·",
		"subtitle": "the unseelie ending",
		"tint": Color(0.55, 0.35, 0.68, 1.0),
		"beats": [
			{"speaker": "· AT DUSK · A SPECIFIC BACK GATE ·",
			 "text": "No other tourist knows this way out.  You leave the Faire wearing a knitted red cap."},
			{"speaker": "narrator",
			 "text": "It fits well.  You keep the seasons.  You keep every friend you had.  Your NAME is different now.  Everyone who calls you the old name gets confused for a moment before you correct them.  You have to relearn to answer to a name you did not choose."},
			{"speaker": "narrator",
			 "text": "Oberon keeps his promise to you · whatever it was · you are trying to remember what it was · it will come back to you eventually · you think.  The Erlking passes your house at night and does not stop."},
			{"speaker": "· STILL IMAGE ·",
			 "text": "You in a specific new coat with a specific red cap · looking in a specific bathroom mirror · adjusting the cap · your reflection is you with a specific new expression.  Three seconds held."}
		]
	},
	"a_stag_antler": {
		"name": "· A STAG'S ANTLER ·",
		"subtitle": "the wildfey ending",
		"tint": Color(0.82, 0.62, 0.35, 1.0),
		"beats": [
			{"speaker": "· AT DAWN · THE FAIRE IS PACKING UP ·",
			 "text": "Trailers being hooked to trucks.  You leave the Faire holding a stag's antler wrapped in oiled paper."},
			{"speaker": "narrator",
			 "text": "You do not know how to explain it.  You keep everything.  But: you do not really leave.  You are AT the Faire when it packs up at dawn.  And you are on one of the trucks.  And you are there when it unpacks in another town seventeen years later."},
			{"speaker": "narrator",
			 "text": "You come back home older, and the town has changed, and everyone you loved has grown up or died.  You are 32 now.  Your mother, if she is alive, is 71."},
			{"speaker": "· STILL IMAGE ·",
			 "text": "You at 32 · standing on the porch of your old childhood house · in a town you barely recognize · holding the antler.  Five seconds held."}
		]
	},
	"refused_the_faire": {
		"name": "· REFUSED THE FAIRE ·",
		"subtitle": "you walked away",
		"tint": Color(0.72, 0.52, 0.26, 1.0),
		"beats": [
			{"speaker": "· PARKING LOT · AT NIGHT · A STREETLIGHT FLICKERS ·",
			 "text": "You walk home under a streetlight that flickers behind you."},
			{"speaker": "narrator",
			 "text": "You never know what you missed."},
			{"speaker": "narrator",
			 "text": "Someone at school asks the next Monday if you went to that carnival that was there over the weekend.\n\n$PLAYER_NAME: 'No.'"},
			{"speaker": "narrator",
			 "text": "You say no honestly.  You do not remember it."},
			{"speaker": "· STILL IMAGE ·",
			 "text": "You at your school desk · Monday morning · looking down at your specific homework.  A specific empty lot where the Faire had been · early morning light · fully mundane."}
		]
	},
	"become_the_faire": {
		"name": "· BECOME THE FAIRE ·",
		"subtitle": "you take Cricket's seat",
		"tint": Color(0.973, 0.784, 0.282, 1.0),
		"beats": [
			{"speaker": "· THE GATE · NIGHT 6 · DAWN APPROACHING ·",
			 "text": "Cricket has been at the Gate a very long time.  She would like to retire."},
			{"speaker": "CRICKET",
			 "text": "'You have understood.  We have nodded at each other for six nights.  I have selected you.  Do you consent?'"},
			{"speaker": "narrator",
			 "text": "You accept.  You take the ticket-taker's stool.  You bite the corner off tickets."},
			{"speaker": "narrator",
			 "text": "Seventeen years pass in one night.\n\nA new teenager walks up."},
			{"speaker": "YOU · to them",
			 "text": "'You get six nights.'\n\nYou mean it."},
			{"speaker": "· STILL IMAGE ·",
			 "text": "You · specifically shrunken to cricket-scale · sitting on a stool on the ticket counter · in a specific new town · watching a specific new teenager approach.  Six seconds held."}
		]
	},
	"bring_back_the_lost": {
		"name": "· BRING BACK THE LOST ·",
		"subtitle": "$LOST_PERSON comes home",
		"tint": Color(0.62, 0.82, 0.55, 1.0),
		"beats": [
			{"speaker": "· THE GREEN · A SPECIFIC CLEARING · DAWN LIGHT ·",
			 "text": "The Green Man does not speak often.  He speaks now."},
			{"speaker": "THE GREEN MAN",
			 "text": "'There is one exchange I will make.'"},
			{"speaker": "narrator",
			 "text": "He asks for your most-recruited fey in trade.  You lose them permanently to Fairyland.  You have already said yes.  You said yes when you walked into his clearing."},
			{"speaker": "narrator",
			 "text": "$LOST_PERSON comes home."},
			{"speaker": "narrator",
			 "text": "The ripple travels forward.  On the drive home from the Faire your father tells you a story about $LOST_PERSON.  Except he doesn't die.  Because you gave a fey back."},
			{"speaker": "· STILL IMAGE ·",
			 "text": "$LOST_PERSON's specific final image · rendered specifically to who they were.  Eight seconds held.\n\nDedication: for the ones we could not save · and the specific one we did."}
		]
	},
	"you_forget_why_you_came": {
		"name": "· YOU FORGET WHY YOU CAME ·",
		"subtitle": "the Faire keeps you",
		"tint": Color(0.62, 0.53, 0.47, 1.0),
		"beats": [
			{"speaker": "· NIGHT 7 · MORNING · THE FAIRE HAS LEFT ·",
			 "text": "You are still at the Faire on Night 7.  The Faire has left already."},
			{"speaker": "narrator",
			 "text": "You are alone in an empty lot.  You do not know why you came.  You do not know your name."},
			{"speaker": "narrator",
			 "text": "(the boot-questionnaire name $PLAYER_NAME still displays in the UI · but the character in the epilogue does not use it)"},
			{"speaker": "narrator",
			 "text": "The screen fades to black."},
			{"speaker": "· SFX · A SPECIFIC CRICKET CHIRPS ONCE ·",
			 "text": "You (the player, not the character) know what that means now."},
			{"speaker": "· STILL IMAGE ·",
			 "text": "The empty lot at Night 7 · a specific single cricket visible on a specific patch of dirt · she is watching.  Five seconds held.\n\nText: THE FAIRE MOVED ON"}
		]
	}
}

var _run_state: Dictionary = {}
var _phase: String = "gather"   # gather | choice | ending
var _selected_ending: String = ""
var _beat_idx: int = 0

var _speaker_lbl: Label = null
var _content_lbl: RichTextLabel = null
var _choices_root: Control = null

# Night-6 gather beats · one Cricket line + one Ondine line + a status
var _gather_beats: Array = [
	{
		"speaker": "· NIGHT 6 · THE LAST NIGHT ·",
		"text": "The Faire begins packing.  Trailer roofs fold.  The Edison bulbs come down one string at a time.  The mauve and cream stripes of the tents lose their voltage; without it they are just fabric.\n\nYou stand at the Gate.  Cricket is at her ticket-counter.  Ondine is behind the ring-toss booth.  Neither of them is smiling.  Both are watching you.\n\nWhat you carry now is what you will carry out."
	},
	{
		"speaker": "CRICKET",
		"text": "'Six nights.  We agreed.  You have chosen every step whether you thought you were choosing or not.  Six nights.  Your ticket is expiring at first light.\n\nWhat you take home is decided.'"
	},
	{
		"speaker": "ONDINE",
		"text": "'I gave you three rings on your first night.  You still have · [$RING_COUNT] · of them.  The rings do not matter.  The choices you made in the last six nights matter.  Titania sends her regards.  Puck sends his laughter.  Oberon sends his careful nothing.'"
	}
]


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")


func boot(state: Dictionary) -> void:
	_run_state = state
	_build_frame()
	_beat_idx = 0
	# A forced ending (set by the Host when the sixth memory is lost on
	# death) skips the Night-6 gather beats and plays straight through.
	var forced: String = String(_run_state.get("forced_ending", ""))
	if forced != "" and ENDINGS.has(forced.trim_prefix("ending_")):
		_run_state.erase("forced_ending")
		_choose(forced.trim_prefix("ending_"))
		return
	_render_gather_beat()


func _build_frame() -> void:
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	for x in range(60, 1280, 90):
		var stripe := ColorRect.new()
		stripe.color = C_MAUVE
		stripe.set_anchors_preset(Control.PRESET_TOP_LEFT)
		stripe.position = Vector2(x, 0)
		stripe.size = Vector2(6, 40)
		add_child(stripe)

	var header := Label.new()
	header.text = "· NIGHT 6 · THE LAST NIGHT ·"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 18)
	header.add_theme_color_override("font_color", C_GOLD)
	header.set_anchors_preset(Control.PRESET_TOP_WIDE)
	header.offset_top = 50
	header.offset_bottom = 78
	add_child(header)

	var panel := ColorRect.new()
	panel.color = C_PANEL
	panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	panel.offset_left = -420
	panel.offset_right = 420
	panel.offset_top = -240
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


func _write_narrative(speaker: String, text: String, tint: Color = C_GOLD) -> void:
	_clear_narrative()
	_speaker_lbl = Label.new()
	_speaker_lbl.text = "· " + speaker.strip_edges().to_upper() + " ·"
	_speaker_lbl.set_anchors_preset(Control.PRESET_CENTER)
	_speaker_lbl.offset_left = -400
	_speaker_lbl.offset_right = 400
	_speaker_lbl.offset_top = -220
	_speaker_lbl.offset_bottom = -196
	_speaker_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_speaker_lbl.add_theme_font_size_override("font_size", 15)
	_speaker_lbl.add_theme_color_override("font_color", tint)
	add_child(_speaker_lbl)

	_content_lbl = RichTextLabel.new()
	_content_lbl.bbcode_enabled = false
	_content_lbl.fit_content = true
	_content_lbl.set_anchors_preset(Control.PRESET_CENTER)
	_content_lbl.offset_left = -400
	_content_lbl.offset_right = 400
	_content_lbl.offset_top = -186
	_content_lbl.offset_bottom = 180
	_content_lbl.text = _substitute(text)
	_content_lbl.add_theme_font_size_override("normal_font_size", 16)
	_content_lbl.add_theme_color_override("default_color", C_CREAM)
	add_child(_content_lbl)


func _substitute(text: String) -> String:
	var q: Dictionary = _run_state.get("questionnaire", {})
	var s := text
	s = s.replace("$PLAYER_NAME", String(q.get("player_name", "you")))
	s = s.replace("$LOST_PERSON", String(q.get("lost_person_name", "someone")))
	s = s.replace("$CITY", String(q.get("city_you_live_in", "your town")))
	s = s.replace("$FAVORITE_SONG", String(q.get("favorite_song", "a song")))
	s = s.replace("$RING_COUNT", str(int(_run_state.get("rings_kept", 3))))
	return s


func _render_advance_button(cb: Callable, label: String = "  continue  →  ") -> void:
	_choices_root = Control.new()
	_choices_root.set_anchors_preset(Control.PRESET_CENTER)
	_choices_root.offset_left = -100
	_choices_root.offset_right = 100
	_choices_root.offset_top = 190
	_choices_root.offset_bottom = 250
	add_child(_choices_root)

	var btn := Button.new()
	btn.text = label
	btn.add_theme_font_size_override("font_size", 16)
	btn.add_theme_color_override("font_color", C_GOLD)
	btn.pressed.connect(cb)
	btn.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_choices_root.add_child(btn)


# ─── Gather phase ───────────────────────────────────────────────────

func _render_gather_beat() -> void:
	if _beat_idx >= _gather_beats.size():
		_render_promise_reckoning(0)
		return
	var beat: Dictionary = _gather_beats[_beat_idx]
	_write_narrative(String(beat.get("speaker", "")), String(beat.get("text", "")), C_GOLD_DIM)
	_render_advance_button(func() -> void:
		_beat_idx += 1
		_render_gather_beat()
	)


# ─── Finale-choice phase ────────────────────────────────────────────

# ─── Promise reckoning · Ondine's ledger, opened ────────────────
# Every promise made this run is read back on the last night.  The
# fey asks whether you kept it · the game does not verify, because
# the promise binds the PLAYER, not the character.  The Faire
# trusts you.  That is the trap.

func _render_promise_reckoning(idx: int) -> void:
	var promises: Array = _run_state.get("promises", [])
	# Skip already-resolved entries
	while idx < promises.size() and bool((promises[idx] as Dictionary).get("resolved", false)):
		idx += 1
	if idx >= promises.size():
		_render_finale_choice()
		return
	var pr: Dictionary = promises[idx]
	var fey_id: String = String(pr.get("fey_id", ""))
	var fey_name: String = fey_id.capitalize()
	_write_narrative(
		"ONDINE'S LEDGER · " + str(idx + 1) + " of " + str(promises.size()),
		"Ondine opens the ledger to a specific page and reads without looking up:\n\n\"" + String(pr.get("promise", "")) + "\"\n\n" + fey_name + " is somewhere on the grounds, listening.  Everyone at the Faire can hear a promise being weighed.\n\nDid you keep it?",
		C_GOLD
	)
	if _choices_root != null and is_instance_valid(_choices_root):
		_choices_root.queue_free()
	_choices_root = Control.new()
	_choices_root.set_anchors_preset(Control.PRESET_CENTER)
	_choices_root.offset_left = -400
	_choices_root.offset_right = 400
	_choices_root.offset_top = 150
	_choices_root.offset_bottom = 270
	add_child(_choices_root)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.add_theme_constant_override("separation", 4)
	_choices_root.add_child(v)

	var kept_btn := Button.new()
	kept_btn.text = "  · I kept it. ·  "
	kept_btn.add_theme_font_size_override("font_size", 16)
	kept_btn.add_theme_color_override("font_color", C_GOLD)
	kept_btn.pressed.connect(func() -> void: _resolve_promise(idx, true))
	v.add_child(kept_btn)

	var kept_note := Label.new()
	kept_note.text = "     the ledger takes your word · " + fey_name + "'s regard rises · nobody checks · that is the point"
	kept_note.add_theme_font_size_override("font_size", 12)
	kept_note.add_theme_color_override("font_color", C_DIM)
	v.add_child(kept_note)

	var not_btn := Button.new()
	not_btn.text = "  · Not yet. ·  "
	not_btn.add_theme_font_size_override("font_size", 16)
	not_btn.pressed.connect(func() -> void: _resolve_promise(idx, false))
	v.add_child(not_btn)

	var not_note := Label.new()
	not_note.text = "     honest · the promise stays open past the summer · fey respect an unkept truth over a kept lie"
	not_note.add_theme_font_size_override("font_size", 12)
	not_note.add_theme_color_override("font_color", C_DIM)
	v.add_child(not_note)


func _resolve_promise(idx: int, kept: bool) -> void:
	var promises: Array = _run_state.get("promises", [])
	if idx < promises.size():
		var pr: Dictionary = promises[idx]
		pr["resolved"] = true
		pr["fulfilled"] = kept
		promises[idx] = pr
		var fey_id: String = String(pr.get("fey_id", ""))
		if kept and fey_id != "":
			var cur: int = int(_run_state.get(fey_id + "_disposition", 0))
			_run_state[fey_id + "_disposition"] = cur + 2
		elif not kept:
			# Honesty is its own small credit · seelie notices
			_run_state["court_seelie"] = int(_run_state.get("court_seelie", 0)) + 1
	_run_state["promises"] = promises
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("page_turn", 0.6)
	_render_promise_reckoning(idx + 1)


func _render_finale_choice() -> void:
	_phase = "choice"
	_write_narrative(
		"· WHERE DO YOU WALK OUT? ·",
		"You have four visible paths out of the Faire on this last night.  The one you choose matches what you have already become.\n\n(Some paths only fire if the state supports them.)"
	)

	if _choices_root != null and is_instance_valid(_choices_root):
		_choices_root.queue_free()
	_choices_root = Control.new()
	_choices_root.set_anchors_preset(Control.PRESET_CENTER)
	_choices_root.offset_left = -400
	_choices_root.offset_right = 400
	_choices_root.offset_top = 130
	_choices_root.offset_bottom = 270
	add_child(_choices_root)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.add_theme_constant_override("separation", 4)
	_choices_root.add_child(v)

	_add_walk_choice(v, "  Walk out through the Gate.  Cricket watches you leave.  ",
		"the standard exit · picks the ending your court alignment and dispositions have already earned",
		func() -> void: _resolve_ending_from_state())

	# Cricket's offer · only if Cricket LOVED
	var cricket_disp: int = int(_run_state.get("cricket_disposition", 0))
	if cricket_disp >= 3:
		_add_walk_choice(v, "  · Take Cricket's seat.  She has been asking with her eyes for three nights.  ",
			"BECOME THE FAIRE · you take the ticket-taker's stool · a specific new teenager approaches",
			func() -> void: _choose("become_the_faire"))

	# Green Man's exchange
	var green_disp: int = int(_run_state.get("green_man_disposition", 0))
	var mirror_4: bool = bool(_run_state.get("mirror_4_the_green_completed", false))
	var wildfey: int = int(_run_state.get("court_wildfey", 0))
	if green_disp >= 4 and wildfey >= 8 and mirror_4:
		_add_walk_choice(v, "  · Take the Green Man's exchange.  Give up your most-recruited fey.  ",
			"BRING BACK THE LOST · a fey for a mortal · Fairyland keeps the fey · you get $LOST_PERSON back",
			func() -> void: _choose("bring_back_the_lost"))

	# Walk-away-early is state-detected, not a button — but if the player got here with almost nothing:
	if int(_run_state.get("recruited_feys", []).size()) < 3 and int(_run_state.get("night", 6)) <= 3:
		_add_walk_choice(v, "  · Walk out through the Parking Lot without looking back.  ",
			"REFUSED THE FAIRE · the Faire will forget you · you will forget it back",
			func() -> void: _choose("refused_the_faire"))

	# Faire-keeps-you check (all 6 memories lost)
	if int(_run_state.get("memories_lost", 0)) >= 6:
		_add_walk_choice(v, "  · Sit down in the empty lot.  You do not know where to go.  ",
			"YOU FORGET WHY YOU CAME · the Faire keeps you · a cricket chirps once",
			func() -> void: _choose("you_forget_why_you_came"))


func _add_walk_choice(v: VBoxContainer, label: String, note: String, cb: Callable) -> void:
	var vh := VBoxContainer.new()
	vh.add_theme_constant_override("separation", 1)
	v.add_child(vh)

	var btn := Button.new()
	btn.text = label
	btn.add_theme_font_size_override("font_size", 14)
	btn.pressed.connect(cb)
	vh.add_child(btn)

	var note_lbl := Label.new()
	note_lbl.text = "     " + note
	note_lbl.add_theme_font_size_override("font_size", 12)
	note_lbl.add_theme_color_override("font_color", C_DIM)
	note_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	vh.add_child(note_lbl)


func _resolve_ending_from_state() -> void:
	# The three court endings choose by alignment; ties break Seelie > Unseelie > Wildfey.
	var seelie: int = int(_run_state.get("court_seelie", 0))
	var unseelie: int = int(_run_state.get("court_unseelie", 0))
	var wildfey: int = int(_run_state.get("court_wildfey", 0))
	var recruited: Array = _run_state.get("recruited_feys", [])
	var promises: Array = _run_state.get("promises", [])
	var promises_kept: int = 0
	for p_v in promises:
		var p: Dictionary = p_v
		if bool(p.get("fulfilled", false)):
			promises_kept += 1

	var titania_liked: bool = int(_run_state.get("titania_disposition", 0)) >= 2
	var oberon_liked: bool  = int(_run_state.get("oberon_disposition", 0)) >= 2
	var green_liked: bool   = int(_run_state.get("green_man_disposition", 0)) >= 2
	var unseelie_recruits: int = 0
	for r_v in recruited:
		# Look up the fey · this scaffold assumes recruited feys carry their court in state cache.
		var court_tag: String = String(_run_state.get("fey_court_" + String(r_v), ""))
		if court_tag == "unseelie":
			unseelie_recruits += 1

	if seelie >= 10 and titania_liked and promises_kept * 2 >= max(1, promises.size()):
		_choose("a_rose")
		return
	if unseelie >= 10 and oberon_liked and unseelie_recruits >= 2:
		_choose("a_red_cap")
		return
	if wildfey >= 10 and green_liked:
		_choose("a_stag_antler")
		return
	# Very-low-recruit path
	if recruited.size() < 3 and int(_run_state.get("night", 6)) <= 3:
		_choose("refused_the_faire")
		return
	# Nothing else matches · default to whichever court is highest
	if seelie >= unseelie and seelie >= wildfey:
		_choose("a_rose")
	elif unseelie >= wildfey:
		_choose("a_red_cap")
	else:
		_choose("a_stag_antler")


func _choose(ending_id: String) -> void:
	_selected_ending = ending_id
	_beat_idx = 0
	_render_ending_intro()


func _render_ending_intro() -> void:
	_phase = "ending"
	var ending: Dictionary = ENDINGS.get(_selected_ending, ENDINGS["refused_the_faire"])
	_write_narrative(
		"ENDING · " + String(ending.get("name", "")),
		"· " + String(ending.get("subtitle", "")) + " ·\n\n(press continue to play the ending)",
		ending.get("tint", C_GOLD)
	)
	# HeroImage for the specific ending, if authored
	var hero_path: String = "res://resources/games/vol7/fey_faire/hero_images/ending_" + _short_ending_id() + ".json"
	var hero := HeroImage.new()
	if hero.load_from(hero_path):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(320, 180))
		tex_rect.set_anchors_preset(Control.PRESET_CENTER)
		tex_rect.position = Vector2(-160, -270)
		tex_rect.size = Vector2(320, 180)
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		add_child(tex_rect)
	_render_advance_button(func() -> void:
		_beat_idx = 0
		_render_ending_beat()
	)


func _short_ending_id() -> String:
	# All seven endings have authored hero images · a_rose's file predates
	# the ending_<full_id>.json convention and keeps its short name.
	match _selected_ending:
		"a_rose": return "rose"
	return _selected_ending


func _render_ending_beat() -> void:
	var ending: Dictionary = ENDINGS.get(_selected_ending, ENDINGS["refused_the_faire"])
	var beats: Array = ending.get("beats", [])
	if _beat_idx >= beats.size():
		_render_end_screen()
		return
	var beat: Dictionary = beats[_beat_idx]
	_write_narrative(String(beat.get("speaker", "")), String(beat.get("text", "")), ending.get("tint", C_GOLD))
	_render_advance_button(func() -> void:
		_beat_idx += 1
		_render_ending_beat()
	)


func _render_end_screen() -> void:
	_write_narrative(
		"· FIN ·",
		"You have seen this ending.  Return to the shelf to view the compendium or start a new run.\n\nCross-Oneironautics facts have been passed forward.",
		C_ROSE
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

	var shelf_btn := Button.new()
	shelf_btn.text = "  ← back to shelf  "
	shelf_btn.pressed.connect(_finish)
	v.add_child(shelf_btn)


func _finish() -> void:
	# Record seen ending
	var seen: Array = _run_state.get("endings_seen", [])
	if not seen.has(_selected_ending):
		seen.append(_selected_ending)
	_run_state["endings_seen"] = seen

	# Cross-Oneironautics unlocks + canon vars
	var canon: Dictionary = _run_state.get("canon_vars", {})
	canon["fey_faire_ending"] = _selected_ending
	_run_state["canon_vars"] = canon
	var tokens: Array = _run_state.get("lore_tokens_pending", [])
	match _selected_ending:
		"a_rose":
			tokens.append("fey_faire_titania_blessing_keepsake")
		"a_red_cap":
			tokens.append("fey_faire_oberon_promise_keepsake")
		"a_stag_antler":
			tokens.append("fey_faire_wildfey_stag_antler_keepsake")
			tokens.append("fey_faire_next_town_bgm")
		"become_the_faire":
			tokens.append("fey_faire_cricket_retired_keepsake")
		"bring_back_the_lost":
			tokens.append("fey_faire_lost_person_returned")
		"you_forget_why_you_came":
			tokens.append("fey_faire_forgotten_ending")
		"refused_the_faire":
			pass
	_run_state["lore_tokens_pending"] = tokens
	finished.emit(canon, tokens)


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			quit_to_shelf.emit()
			get_viewport().set_input_as_handled()
			return
		if kev.keycode == KEY_SPACE or kev.keycode == KEY_ENTER or kev.keycode == KEY_KP_ENTER:
			if _choices_root != null and is_instance_valid(_choices_root):
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
