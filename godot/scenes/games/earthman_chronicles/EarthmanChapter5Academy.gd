extends Control
## Earthman Chronicles · Chapter 5 · The Academy · scaffold.
##
## The pivot chapter.  Rocha's team labeled it "THE PIVOT" in
## production docs.  Rafaton reveals himself as Nalat.  Ronson (the
## Hubbard-analog) delivers his soliloquy.  The Scarlet Woman is met
## with three canonical readings.  Working VI and Working VII are
## offered; Working IX is offered but Sara defaults REFUSAL.  The
## chapter closes on a boss encounter with three routes.
##
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal chapter_complete(state: Dictionary)

# Academy palette · mountain-stone + Cortex-purple + gold accents
const C_BG           := Color(0.075, 0.055, 0.098, 1.0)   # deep indigo
const C_STONE        := Color(0.259, 0.208, 0.239, 1.0)   # cool stone
const C_INLAY        := Color(0.851, 0.702, 0.353, 1.0)   # gold inlay
const C_STAR         := Color(0.973, 0.784, 0.282, 1.0)   # eight-pointed star gold
const C_CORTEX       := Color(0.345, 0.188, 0.376, 1.0)
const C_VELVET       := Color(0.518, 0.098, 0.161, 1.0)   # Scarlet Woman red
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

var _beats: Array = [
	{
		"speaker": "· THE APPROACH · MOUNTAIN ROAD ·",
		"text": "The invitation arrived in Talikan a week after the Mines: a specific Delvanni courier, a specific folded parchment, the seal a specific eight-pointed star pressed in dark wax.  Rafaton has requested your presence at the Academy for your \"graduation.\"\n\nThe road climbs.  The party is quiet.  Sara Nai has been quiet since the seal.  She rides a specific length behind you now.  She has not explained.\n\nWhen the Academy comes into view, she stops her mount without meaning to."
	},
	{
		"speaker": "SARA NAI",
		"text": "'I have · I have been to a place like this.  Not this place.  A place LIKE this.  In a book my grandmother did not let me finish.  The book was old.  The place in it was older.\n\nJack.  I do not think this is graduation.'"
	},
	{
		"speaker": "· THE GRAND HALL ·",
		"text": "The great entrance opens on you like a mouth trying to smile.  Everything is comfortable.  Everything is warm.  There is a specific ceremonial meal laid out, a specific wine that smells correct.  Rafaton is at the head of the table.  He rises when you enter.  His arms are open.\n\nHis warmth is uncanny.  You know it is uncanny because you have felt it before and have not remembered where.\n\nHe embraces you.  He calls you SON."
	},
	{
		"speaker": "RAFATON",
		"text": "'Jack.  Jack.  You have done everything I hoped, and things I did not know to hope for.  Six Workings.  Six.  Sit.  Eat.  Tonight we begin the seventh.  Tomorrow, the ninth if you are ready.  I think you are.  I think you have been ready since your first fire in Pasadena.'\n\nEight-pointed stars are inlaid in the floor · in the ceiling · in the trim of Rafaton's collar.  You did not notice the collar until now.  You notice it now."
	},
	{
		"speaker": "· CHOICE · Working VI · Liber Reguli ·",
		"type": "choice",
		"choices": [
			{
				"id": "working_vi_yes",
				"label": "  Perform Liber Reguli tonight.  It is the invocation of Horus · warlike, direct, clarifying.  Rafaton will guide you.  ",
				"note": "Working VI performed.  +2 SP max.  Rafaton_disposition +1.  Sara Nai's face does not move.  Locks certain refusal endings later.",
				"sets": {"working_vi_completed": true, "sp_max_delta": 2, "rafaton_disposition_delta": 1}
			},
			{
				"id": "working_vi_defer",
				"label": "  Defer.  You want to meet Rafaton's Scarlet Woman first.  You want to see the room he is not showing you.  ",
				"note": "Rafaton is disappointed but hides it.  Rafaton_disposition -1.  You may still perform Working VI later.  Sara Nai looks at you for the first time since the road.",
				"sets": {"working_vi_completed": false, "rafaton_disposition_delta": -1, "sara_nai_disposition_delta": 1}
			},
			{
				"id": "working_vi_refuse",
				"label": "  Refuse.  You are here to graduate on your own terms.  You have not consented to a war-god.  ",
				"note": "Rafaton is quiet.  Rafaton_disposition -2.  A specific eight-pointed star on the wall behind him begins to look painted, not carved.  Sara Nai exhales.",
				"sets": {"working_vi_completed": false, "rafaton_disposition_delta": -2, "sara_nai_disposition_delta": 2}
			}
		]
	},
	{
		"speaker": "· THE SCARLET WOMAN'S CHAMBER ·",
		"text": "Velvet drapes.  Photoluminescent moss in specific alcoves, giving the room the quality of a specific California evening you cannot quite place.  A tea service on a low table.  A woman sits behind it.\n\nShe is not Parsan.  She is not Kyrindi.  She is a specific composite the game engine renders with a specific unclassified sprite sheet.  Her eyes are your mother's eyes.  You have not told anyone what your mother's eyes looked like.  Not even Sara."
	},
	{
		"speaker": "THE SCARLET WOMAN",
		"text": "'Sit.  Drink.  Do not lie to me · I will know it and I will not care.\n\nYou have come here because you were told to.  I have been here forever because I chose to be.  Both things can be true.  Both things must be, tonight.  Read me, Jack.  Say aloud what you think I am.'"
	},
	{
		"speaker": "· CHOICE · three readings ·",
		"type": "choice",
		"choices": [
			{
				"id": "reading_literal_babalon",
				"label": "  'You are Babalon.  You are the Scarlet Woman of the manuscript.  I have read the passage.'  ",
				"note": "Manuscript-canonical.  She nods gravely.  Locks certain Sara-dialogue trees in Chapter 6.  Opens BABALON COMES ending.",
				"sets": {"scarlet_reading": "babalon_literal", "canon_babalon_read": true}
			},
			{
				"id": "reading_priestess_ghyra",
				"label": "  'You are a Kelait priestess named Ghyra playing a role for tourists.  Sara has read about you.'  ",
				"note": "Alternative reading.  Sara Nai_disposition +2.  Opens the specific Sara-Kelait scholarship dialogue in Chapter 6.  Kelait mourning song plays under this beat.",
				"sets": {"scarlet_reading": "priestess_ghyra", "sara_nai_disposition_delta": 2}
			},
			{
				"id": "reading_jack_projecting",
				"label": "  'You are my mother.  Or you are what I am afraid my mother was.  I do not know if there is a difference.'  ",
				"note": "The meta reading.  Deepest Sara dialogue in Chapter 6.  Reframes the whole relationship.  The Scarlet Woman does not answer.  She hands you tea.  The tea is exactly the temperature you like.",
				"sets": {"scarlet_reading": "jack_projecting", "sara_nai_disposition_delta": 3, "reframe_flag": true}
			}
		]
	},
	{
		"speaker": "· THE MEETING OF THE ORDER ·",
		"text": "The Order's central chamber.  Nine seats.  Eight are filled with Rafaton-adjacent figures · dignitaries whose species you cannot quite place, whose eight-pointed stars are stitched into every hem.\n\nThe ninth seat holds a Human man.  Broad-faced.  Red-haired going gray.  Wearing a modified naval jacket that has aged badly.  His posture is bad.  He is drinking from a specific chipped ceramic mug.\n\nHe smiles at you when you enter.  His smile is the worst thing you have seen since Pasadena.\n\nRAFATON stands.  He speaks."
	},
	{
		"speaker": "RAFATON",
		"text": "'Jack.  You have completed six Workings on my instruction.  Do you not wonder why?\n\nWell.  I get a specific bonus for each.  My name is not Rafaton.  My name is NALAT.  I am Order Senior Second Class.  I have been Order Senior Second Class for a hundred and forty years.  When you complete Working IX, I become Order Senior First Class.  This is my career.\n\nI do like you, Jack.  That was not a lie.  I like a lot of people.  I have delivered a lot of them.  The liking is real.  The delivery is the job.'"
	},
	{
		"speaker": "· BEAT ·",
		"text": "Sara Nai's face is a specific animation the writers noted as the most quiet 8 frames in the game.  She does not speak.  She reaches out and puts her hand on your forearm.  She has not touched you before.\n\nHel Velli, if with you, has drawn his upper-left blade halfway out of its sheath.  He has not moved otherwise.  He is waiting for you.\n\nRocha, if with you, is already at the door · not fleeing · counting exits."
	},
	{
		"speaker": "· RONSON'S ROOM ·",
		"text": "You are led (or you go anyway) past a specific side hall into RONSON's private study.  It is small.  It has the objects of a specific man who has been away from Earth for fourteen years:\n\n· a specific California postcard (Santa Monica pier, 1932, faded)\n· a specific 1930s book of pulp adventure stories, the spine cracked at a specific page\n· a specific ashtray from a specific Los Angeles restaurant (SIMON'S DRIVE-IN, MAY 1935)\n· a specific glass, empty, with a specific brown ring at the bottom of it\n\nRonson is already sitting.  He has been waiting for you.  He starts the soliloquy the second you sit down."
	},
	{
		"speaker": "RONSON (the Hubbard-analog)",
		"text": "'Kid.  Kid.  Let me talk.  Nalat gave me twelve minutes.\n\nI came here in '32.  I did a Working I found in a used-bookstore in San Bernardino.  I woke up here.  I have been building this Order for FOURTEEN YEARS.  You think you are the first Earthman on Parsa?  No.  I was.  I am.  I will be.\n\nWhat I have built here is a RELIGION, Jack.  A RELIGION.  Which is a specific product I have specifically not been able to sell on Earth.  On Parsa it works.  On Parsa the marks are already ninety percent to the point of sale before you say hello.  On Parsa I am the SECOND COMING of a MAN nobody has heard of, which is the specific best kind of second coming to be.\n\nDo you understand what I have accomplished, Jack?  I have made ONE HUNDRED AND SIXTY THOUSAND SOULS believe a story I made up in a specific one-room apartment in San Bernardino in 1931.  You are welcome to join.  You would be quite good at this, Jack.  You have the specific charisma.\n\nYou have twelve minutes to think.  Talk.'"
	},
	{
		"speaker": "· CHOICE · Ronson's soliloquy ·",
		"type": "choice",
		"choices": [
			{
				"id": "ronson_join",
				"label": "  '· · · yes.  Yes, actually.  This is my calling.  I have known it since I was nine.'  ",
				"note": "You side with Ronson.  Locks the LIBERATOR/CORRECTION endings.  Opens HUBBARD TAKES THE CREDIT.  Sara Nai will not speak to you for the rest of the chapter.",
				"sets": {"ronson_alliance": true, "sara_nai_disposition_delta": -4, "hubbard_takes_credit_open": true}
			},
			{
				"id": "ronson_nine_words",
				"label": "  'You wrote it in a one-room apartment.  That's not enough.'  (the nine-word deflation)  ",
				"note": "The manuscript's own line, uncut by Astro-Cortex.  Ronson is silent for a specific 4 seconds.  Then he laughs.  Then he asks you to leave.  Sara Nai_disposition +2.  Correction 4 (OTO Contract) becomes usable in the boss encounter.",
				"sets": {"ronson_deflated": true, "sara_nai_disposition_delta": 2, "oto_contract_usable": true, "nine_word_deflation": true}
			},
			{
				"id": "ronson_silence",
				"label": "  Say nothing.  Let the twelve minutes pass.  Watch him.  ",
				"note": "Ronson dislikes silence.  He fills it with three more paragraphs you do not need.  Rafaton comes to collect you.  Neutral outcome.  Ronson_disposition -1.",
				"sets": {"ronson_endured_silence": true}
			}
		]
	},
	{
		"speaker": "· HIDDEN CORRECTION · PASADENA FIRE ·",
		"text": "On your way out of Ronson's study, your specific spectrum analyzer (kept in Jack's inventory since Chapter 1) pings.  A 220-Hz reading behind a specific bookcase.\n\nYou nudge the bookcase.  It swings.  Behind it is a specific narrow closet.  Inside the closet is a specific manila folder.  In the folder is a specific police report from Pasadena, June 1946, and a specific handwritten note in Ronson's hand:\n\n\"Fire started 03:14.  Not accidental.  Necessary.  P. suspicions confirmed · left them living, took the girl.  The Order will call it Parsons's own carelessness, per Nalat.  A useful loss.  R.\"\n\nYour hands are cold now.  The specific hands of your character sprite are drawn in a specific different color for the rest of the chapter."
	},
	{
		"speaker": "· CHOICE · what to do with the Pasadena Fire correction ·",
		"type": "choice",
		"choices": [
			{
				"id": "correction_pocket",
				"label": "  Pocket it.  Say nothing yet.  You may need it in the arena.  ",
				"note": "Correction 1 (Pasadena Fire) added.  Opens THE CORRECTION ending path.  Ronson's fate in the boss depends on this later.",
				"sets": {"correction_pasadena_fire": true}
			},
			{
				"id": "correction_show_sara",
				"label": "  Show Sara Nai.  She should know what we are inside of.  ",
				"note": "Sara reads it.  Says nothing.  Puts a specific Kyrindi mourning-bead in your palm.  You will find out what it is for in Chapter 6.  Sara Nai_disposition +3.  Correction added.",
				"sets": {"correction_pasadena_fire": true, "sara_mourning_bead": true, "sara_nai_disposition_delta": 3}
			},
			{
				"id": "correction_burn",
				"label": "  Burn it in the specific oil lamp on Ronson's desk.  You are done being managed.  ",
				"note": "You destroy the evidence.  Correction NOT added.  You feel lighter.  You are lying to yourself.  Ronson will notice the smell and thank you specifically.",
				"sets": {"correction_pasadena_fire": false, "burned_the_evidence": true}
			}
		]
	},
	{
		"speaker": "· WORKING VII · THE GREAT WORK · SARA'S TRANSFORMATION ·",
		"text": "Nalat convenes the Working before you have processed the Correction.  The chamber is prepared.  Sara Nai stands in the center of a specific circle drawn in a specific pigment (the pigment is Kelait blood; Nalat does not mention this; you notice it; you know it).\n\nShe looks at you.  She is calm.  She has decided something.  She wants you to choose the reading, so that she knows which version of herself she has just agreed to.\n\nRafaton-Nalat holds the invocation script.  He is waiting.  What poem is spoken over her?"
	},
	{
		"speaker": "· CHOICE · Working VII · the poem ·",
		"type": "choice",
		"choices": [
			{
				"id": "poem_ishra_elemental",
				"label": "  Speak Sara Nai's own Kyrindi passage · the Ishra elemental hymn she has been studying.  ",
				"note": "Sara transforms into ISHRA (a real historical Kyrindi figure Sara has been researching).  The transformation is empathic, not possessive.  Sara remains Sara underneath.  Opens the REFUSED THE WORK ending Ch6.",
				"sets": {"working_vii_completed": true, "sara_transformation": "ishra_elemental", "sara_still_sara": true}
			},
			{
				"id": "poem_babalon_manuscript",
				"label": "  Speak the manuscript's Babalon passage · Hubbard's canonical text, uncut.  ",
				"note": "Sara transforms as Hubbard wrote.  Reverent, remote, no longer the woman who put her hand on your arm.  Nalat is pleased.  Opens BABALON COMES.  Sara-as-Sara is functionally gone for the rest of the game (specific line in Ch6 endings).",
				"sets": {"working_vii_completed": true, "sara_transformation": "babalon_canonical", "sara_still_sara": false}
			},
			{
				"id": "poem_refuse",
				"label": "  Speak no poem.  Take Sara's hand.  Walk her out of the circle.  ",
				"note": "Working VII NOT performed.  Nalat is genuinely surprised for the first time.  The pigment circle stays drawn.  Sara Nai_disposition +5.  Opens THE CORRECTION and REFUSED THE WORK endings.",
				"sets": {"working_vii_completed": false, "sara_transformation": "none", "walked_her_out": true, "sara_nai_disposition_delta": 5}
			}
		]
	},
	{
		"speaker": "· WORKING IX · BABALON WORKING · OFFERED ·",
		"text": "Immediately after Working VII (or its refusal), Nalat produces the ninth ritual.  It is one page.  It is very old.  It requires the full party's consent.\n\nHe explains the mechanics with a specific administrative patience.  A specific voice.  A specific accountant's cadence.\n\nHe finishes.  He looks at Sara Nai.  He waits.\n\nSARA NAI SPEAKS FIRST · she has been prepared to speak first since the road:"
	},
	{
		"speaker": "SARA NAI",
		"text": "'I refuse.\n\nJack.  Look at me.  I refuse.  If you wish to perform this, you will perform it without me in the room and without my hand.  I will love you across the whole rest of your life · I will · but I will not consent to this.  You may still choose it.  I have said what I need to say.'"
	},
	{
		"speaker": "· CHOICE · Working IX consent ·",
		"type": "choice",
		"choices": [
			{
				"id": "working_ix_yes_despite_sara",
				"label": "  Perform Working IX anyway.  Sara leaves the room.  You proceed without her.  ",
				"note": "Working IX performed WITHOUT full consent.  Locks BABALON COMES (Nalat's preferred ending).  Sara Nai_disposition -8.  She will not return in Ch6.",
				"sets": {"working_ix_performed": true, "sara_consent": false, "sara_nai_disposition_delta": -8}
			},
			{
				"id": "working_ix_refuse",
				"label": "  Refuse.  You have heard Sara Nai.  You have heard her before Nalat.  ",
				"note": "Working IX NOT performed.  Nalat sighs specifically.  Opens THE CORRECTION, REFUSED THE WORK, LIBERATOR endings.  Sara Nai_disposition +3.",
				"sets": {"working_ix_performed": false, "sara_consent": true, "sara_nai_disposition_delta": 3}
			},
			{
				"id": "working_ix_defer",
				"label": "  Defer.  Ask Nalat for a night.  You want to walk the Academy first.  ",
				"note": "Nalat grants the night.  You may still perform Working IX in the finale (Ch6).  He is confident you will.  Sara Nai_disposition +1.",
				"sets": {"working_ix_performed": false, "working_ix_deferred": true, "sara_nai_disposition_delta": 1}
			}
		]
	},
	{
		"speaker": "· THE BOSS ARENA · NALAT ·",
		"text": "You return to the meeting chamber.  The Order has thinned.  Nalat has kept only two lesser members and Ronson (if you deflated him with the nine-word line, Ronson stays seated and does not fight).\n\nHe is not angry.  Anger is not the tone.  He is CHECKING IN.  Like a shift manager.\n\nHe unsheathes a specific ceremonial blade.  He is holding it wrong on purpose.  He wants you to see he is not a fighter.  He wants you to see he does not need to be."
	},
	{
		"speaker": "· CHOICE · Nalat confrontation ·",
		"type": "choice",
		"choices": [
			{
				"id": "nalat_combat",
				"label": "  Combat.  Draw the propellant pistol.  This is what has to happen.  ",
				"note": "Boss fight.  Nalat falls at critical HP if any Workings were performed.  Order weakened.  Specific consequences roll into Ch6.  If Working V and Working VI both done, Hel Velli takes a serious wound here.",
				"sets": {"nalat_outcome": "combat", "nalat_defeated": true, "order_weakened": true}
			},
			{
				"id": "nalat_negotiation_correction",
				"label": "  Produce the OTO Contract Correction from Chapter 3.  Read it aloud.  ",
				"note": "Requires OTO Contract (correction 3).  Nalat's face goes still.  He admits the entire scheme in specific detail.  The Order's plans exposed to the party.  Opens the specific LIBERATOR ending.  No blood shed.",
				"sets": {"nalat_outcome": "negotiation", "nalat_exposed": true, "liberator_ending_open": true}
			},
			{
				"id": "nalat_empathy",
				"label": "  'You are Kelait.  Your name is Nalat.  You have been Order Senior Second Class for a hundred and forty years.  You know what you are helping continue in those mines.'  ",
				"note": "Empathy path.  Requires Kanel LIKED + Working V refused + Rocha recruited.  Nalat sits down.  He is quiet for a specific long time.  He defects.  The rarest outcome.  Opens the specific dual-Kelait Ch6 finale.",
				"sets": {"nalat_outcome": "empathy_defected", "nalat_defected": true, "dual_kelait_finale_open": true}
			}
		]
	},
	{
		"speaker": "· AFTERMATH ·",
		"text": "The Academy is quiet.  A specific stone of the entrance hall has cracked.  The gold inlay of a specific eight-pointed star has come loose and lies on the floor.  Sara Nai picks it up.  She does not put it in her satchel.  She holds it flat in her palm and looks at it for a specific length of time.\n\nHel Velli, if with you, sheathes.  Rocha, if with you, has already found the exit.\n\nRonson, whatever his fate, is quiet.  His California postcard is still on his desk."
	},
	{
		"speaker": "· END CHAPTER 5 ·",
		"text": "The party descends the mountain in the dark.  Nobody proposes stopping.  Nobody proposes talking.  The one page that matters is folded in your breast pocket, and everyone in the party knows it is there, and nobody looks at it.\n\nBy morning you can see Talikan's rooftops.  By evening you will have to decide.\n\n· CHAPTER 6 · THE FINALE ·"
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

	# Eight-pointed star motifs · low-alpha wallpaper
	for x in range(90, 1280, 220):
		for y in range(90, 720, 200):
			var star := Label.new()
			star.text = "✦"
			star.add_theme_font_size_override("font_size", 28)
			star.add_theme_color_override("font_color", Color(C_STAR.r, C_STAR.g, C_STAR.b, 0.10))
			star.set_anchors_preset(Control.PRESET_TOP_LEFT)
			star.position = Vector2(x, y)
			add_child(star)

	# Stone bands
	for y in range(80, 720, 100):
		var band := ColorRect.new()
		band.color = C_STONE
		band.set_anchors_preset(Control.PRESET_TOP_WIDE)
		band.position.y = y
		band.size = Vector2(2000, 30)
		band.color.a = 0.25
		add_child(band)

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
	hud_top_text.text = "CHAPTER 5 · THE ACADEMY"
	hud_top_text.set_anchors_preset(Control.PRESET_TOP_LEFT)
	hud_top_text.position = Vector2(12, 6)
	hud_top_text.add_theme_font_size_override("font_size", 10)
	hud_top_text.add_theme_color_override("font_color", C_AMBER)
	add_child(hud_top_text)

	var hud_top_right := Label.new()
	hud_top_right.text = "ORDER OF THE PROPHET · MOUNTAIN COMPLEX"
	hud_top_right.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	hud_top_right.position = Vector2(-280, 6)
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

	# HeroImage · Academy gate · top-right of the pivot chapter
	var hero := HeroImage.new()
	if hero.load_from("res://resources/games/vol7/earthman_chronicles/hero_images/academy_gate.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(220, 124))
		tex_rect.set_anchors_preset(Control.PRESET_TOP_RIGHT)
		tex_rect.position = Vector2(-240, 28)
		tex_rect.size = Vector2(220, 124)
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		add_child(tex_rect)

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
	var workings: Array = _run_state.get("workings_completed", [])
	var corrections: Array = _run_state.get("corrections_found", [])
	return "PARTY: " + " · ".join(names) + "  ·  WORKINGS " + str(workings.size()) + "/9  ·  CORRECTIONS " + str(corrections.size()) + "/6"


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
	_content_lbl.offset_bottom = 130
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
	_choices_root.offset_left = -390
	_choices_root.offset_right = 390
	_choices_root.offset_top = 130
	_choices_root.offset_bottom = 270
	add_child(_choices_root)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.add_theme_constant_override("separation", 4)
	_choices_root.add_child(v)

	for choice_v in beat.get("choices", []):
		var choice: Dictionary = choice_v
		var vh := VBoxContainer.new()
		vh.add_theme_constant_override("separation", 1)
		v.add_child(vh)

		var btn := Button.new()
		btn.text = String(choice.get("label", ""))
		btn.add_theme_font_size_override("font_size", 10)
		btn.pressed.connect(func() -> void: _on_choice_selected(choice))
		vh.add_child(btn)

		var note := Label.new()
		note.text = "     " + String(choice.get("note", ""))
		note.add_theme_font_size_override("font_size", 8)
		note.add_theme_color_override("font_color", C_DIM)
		note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		vh.add_child(note)


func _render_advance_button() -> void:
	_choices_root = Control.new()
	_choices_root.set_anchors_preset(Control.PRESET_CENTER)
	_choices_root.offset_left = -80
	_choices_root.offset_right = 80
	_choices_root.offset_top = 200
	_choices_root.offset_bottom = 260
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
			var base_key: String = key.substr(0, key.length() - 6)
			var cur: int = int(_run_state.get(base_key, 0))
			_run_state[base_key] = cur + int(sets[k])
		else:
			_run_state[key] = sets[k]
	# Track Workings
	if bool(sets.get("working_vi_completed", false)):
		var wc: Array = _run_state.get("workings_completed", [])
		if not wc.has("liber_reguli"): wc.append("liber_reguli")
		_run_state["workings_completed"] = wc
	if bool(sets.get("working_vii_completed", false)):
		var wc: Array = _run_state.get("workings_completed", [])
		if not wc.has("the_great_work"): wc.append("the_great_work")
		_run_state["workings_completed"] = wc
	if bool(sets.get("working_ix_performed", false)):
		var wc: Array = _run_state.get("workings_completed", [])
		if not wc.has("babalon_working"): wc.append("babalon_working")
		_run_state["workings_completed"] = wc
	# Track Corrections
	if bool(sets.get("correction_pasadena_fire", false)):
		var cf: Array = _run_state.get("corrections_found", [])
		if not cf.has("correction_pasadena_fire"): cf.append("correction_pasadena_fire")
		_run_state["corrections_found"] = cf
	var choices_log: Array = _run_state.get("choices_log", [])
	choices_log.append({"chapter": 5, "beat": _beat_idx, "choice_id": String(choice.get("id", ""))})
	_run_state["choices_log"] = choices_log
	_on_advance()


func _on_advance() -> void:
	_beat_idx += 1
	_render_current_beat()


func _end_chapter() -> void:
	# Nalat outcome may kill Ronson silently if the empathy path with correction fired
	_run_state["chapter"] = 6

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
