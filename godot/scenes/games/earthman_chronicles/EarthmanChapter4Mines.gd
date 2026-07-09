extends Control
## Earthman Chronicles · Chapter 4 · The Mines of Delvan · scaffold.
##
## The game's emotional heart per the design docs.  Party descends
## into the Kel-Rethani mines, meets Mother Kanel and Yr, confronts
## Thar-Krai-Tam via combat OR empathy path, potentially recruits
## Rocha, and (in the success paths) frees the enslaved Kelait
## community.
##
## Beat count is deliberately larger than earlier chapters · this is
## where the game means the most.
##
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal chapter_complete(state: Dictionary)

# Mine palette · underground · claustrophobic
const C_BG           := Color(0.055, 0.043, 0.031, 1.0)   # near-black
const C_STONE        := Color(0.196, 0.137, 0.098, 1.0)   # basalt
const C_LAMP         := Color(0.973, 0.816, 0.518, 1.0)   # warm oil-lantern
const C_KELAIT_GOLD  := Color(0.898, 0.788, 0.478, 1.0)   # Kelait pale-gold skin
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

var _beats: Array = [
	{
		"speaker": "· THE APPROACH · KEL-RETHANI OUTER MINE ·",
		"text": "The Kel-Rethani mine sits on a specific plateau · fifteen hours' ride south of Talikan.  Hel Velli rides ahead.  Sara Nai has learned to ride a Parsan mount over the past three days (she is unsteady but competent).  You are on the last mount.  It is a specific stubborn one Hel Velli warned you about.\n\nThe mine entrance is a specific limestone arch, guarded by two Delvanni sentries and one small tired figure with a specific stain on his lower-left palm.\n\nDALEV.  The bribable overseer."
	},
	{
		"speaker": "DALEV",
		"text": "'You are not authorized.  I do not care.  What are you offering?'\n\nHe does not look up.  He is chewing something.  The stain on his palm is not blood; it is dye.  He has been dyeing wool.  You did not expect this."
	},
	{
		"speaker": "· CHOICE · handle Dalev ·",
		"type": "choice",
		"choices": [
			{
				"id": "dalev_bribe",
				"label": "  Pay him twelve shenin.  ",
				"note": "Dalev looks the other way for twelve minutes · he did not see you · standard route",
				"requires_shenin": 12,
				"sets": {"dalev_bribed": true, "shenin_delta": -12}
			},
			{
				"id": "dalev_full_hour",
				"label": "  Offer twenty-four shenin and ask him to look away for a full hour.  ",
				"note": "Dalev accepts · he will not report anything · specifically retires to his quarters to nap · the rescue path opens",
				"requires_shenin": 24,
				"sets": {"dalev_bribed_long": true, "shenin_delta": -24, "rescue_path_open": true}
			},
			{
				"id": "dalev_sneak",
				"label": "  Try to sneak past.  Sara Nai's Kyrindi vocal magic can distract him.  ",
				"note": "Sara Nai casts a specific low hum · Dalev looks the other way · costs Sara 4 SP · you pass",
				"sets": {"dalev_snuck_past": true, "sara_sp_delta": -4}
			}
		]
	},
	{
		"speaker": "· MINE LEVEL 1 · WITNESSING ·",
		"text": "You descend a specific narrow stair for fifteen minutes.  The temperature rises.  The air thickens.  You reach the first working level.\n\nKelait are here.  Approximately sixty of them.  They are wearing specific harnesses that pass loads to their small frames.  A Delvanni overseer stands at the far end with a specific whip he does not use casually.\n\nHel Velli's face is a specific animation the writers noted.  Sara Nai's is quieter · she has read about this · she did not want to be right.  You have never seen this before."
	},
	{
		"speaker": "· BEAT ·",
		"text": "You pass through.  You do not stop.  You cannot stop.  Not yet."
	},
	{
		"speaker": "· KANEL'S KITCHEN · MINE LEVEL 2 ·",
		"text": "A specific hidden cavern behind a specific loose panel of rock.  Kelait have carved out a specific kitchen · a specific pot on a specific fire · a specific salt jar next to the pot.\n\nMOTHER KANEL is here.  Three feet three.  Pale-gold skin.  Long dark brown hair in seven braids.  Eyes unusually large even for Kelait.  She is 187 years old.  She has been in the mines for 42 years.\n\nShe does not look up when you enter.  She is stirring the pot."
	},
	{
		"speaker": "MOTHER KANEL",
		"text": "'You have come in.  You have not spoken yet.  You are watching me stir a pot.  You will learn the pot before you learn me.\n\nSit.  The floor is clean · we swept before you came.'"
	},
	{
		"speaker": "· CHOICE · earn her trust ·",
		"type": "choice",
		"choices": [
			{
				"id": "kanel_figure_out",
				"label": "  Watch her cook.  Observe the specific pattern.  Notice when she adds the salt.  ",
				"note": "You figure out the aphorism-as-recipe pattern yourself · Mother Kanel LOVED (high trust) · unlocks all Kelait dialogue trees",
				"sets": {"kanel_disposition_delta": 3, "kanel_puzzle_solved": true}
			},
			{
				"id": "kanel_ask_sara",
				"label": "  Ask Sara Nai · she has read Kelait manuscripts · she can help.  ",
				"note": "Sara helps · medium trust · specific dialogue about her Kelait scholarship · Kanel LIKED",
				"sets": {"kanel_disposition_delta": 1, "kanel_puzzle_helped": true, "sara_nai_disposition_delta": 1}
			},
			{
				"id": "kanel_impatient",
				"label": "  Ask her plainly what she means by the salt.  We do not have time for this.  ",
				"note": "Kanel is not offended but she is not impressed · low trust · some dialogue locked",
				"sets": {"kanel_disposition_delta": -1, "kanel_impatience": true}
			}
		]
	},
	{
		"speaker": "MOTHER KANEL",
		"text": "'You have learned the pot.  We may now speak.\n\nMy people have been in these mines for forty-two years.  The Kel-Rethani say we owe them a debt from a specific war we did not fight in.  They are wrong.  They are also stronger than us.  Both things can be true.\n\nWe have made specific plans.  They involve specific rituals of the older kind.  Sara Nai · Kyrindi scholar · you have read the specific manuscript.  You know what I am not saying.'\n\nSara Nai nods.  Slowly.  She does know."
	},
	{
		"speaker": "· MEETING YR ·",
		"text": "Kanel takes you deeper.  You pass through a specific narrow corridor to the Kelait quarters.  Approximately two hundred Kelait live here.  Children among them.\n\nA specific six-year-old boy watches you from behind a wooden crate.  He is three feet two.  His hair is long and dark brown, unbraided (children do not braid until their tenth year).  His hands are small and clean.  His eyes are enormous.\n\nSara Nai kneels.  She speaks to him in Kelait Common.  The specific words are quiet."
	},
	{
		"speaker": "YR",
		"text": "'You are · you sound · your voice is · like the specific song a Kyrindi merchant sang once when I was very small.  I have not heard that song since.  Do you sing that song?'"
	},
	{
		"speaker": "SARA NAI",
		"text": "She looks at you.  She looks at Kanel.  She looks back at Yr.\n\n'Yes,' she says.  'I know that song.  I will sing it for you when we are outside.  Would that be all right?'\n\nYr nods.  He does not know what OUTSIDE means.  He has never seen the sky.  Mother Kanel has told him about it.  He has believed her but not entirely."
	},
	{
		"speaker": "· DEEP KELAIT CAVE ·",
		"text": "Mother Kanel takes only you, Sara, and Hel Velli deeper.  Past a specific pool of underground water.  Past a specific Kelait sage NPC (Mother Kanel's own teacher, still alive at 200+, whose name she does not say aloud in your hearing).\n\nAt a specific niche in the wall she stops.  She turns to you.\n\nShe speaks."
	},
	{
		"speaker": "MOTHER KANEL",
		"text": "'You will die.  I will die.  Sara Nai will die.  Rafaton will die.  Hel Velli will die.  Rocha will die.  The two moons will die.  The last light will be a specific color none of us have ever seen.\n\nLive now.'"
	},
	{
		"speaker": "· BEAT ·",
		"text": "Nobody speaks for a while."
	},
	{
		"speaker": "· CHOICE · Working V · Mass of the Phoenix ·",
		"type": "choice",
		"choices": [
			{
				"id": "working_v_yes",
				"label": "  Perform Working V.  It costs 1 HP permanently but grants massive ritual damage in the coming confrontation.  ",
				"note": "Hel Velli refuses vocally (specific line).  Rocha (if adjacent) refuses vocally.  Sara Nai stays silent.  Working V completes at -1 permanent HP · sets up the confrontation.",
				"sets": {"working_v_completed": true, "hp_max_delta": -1, "hel_velli_disposition_delta": -1}
			},
			{
				"id": "working_v_no",
				"label": "  Refuse.  Hel Velli said 'please do not' · you heard him.  ",
				"note": "Working V not performed.  Hel Velli +1 disposition.  The confrontation will be harder but the empathy path opens more fully.",
				"sets": {"working_v_completed": false, "hel_velli_disposition_delta": 1}
			}
		]
	},
	{
		"speaker": "· ROCHA ·",
		"text": "In the Kelait quarters, a specific small Parsan-looking cartographer's assistant is helping the children with a specific sketch of the mine layout.  You have not noticed her before.  She has been here the whole chapter.\n\nShe looks up when you approach."
	},
	{
		"speaker": "· CHOICE · Rocha ·",
		"type": "choice",
		"choices": [
			{
				"id": "rocha_direct",
				"label": "  'Are you SURE you're just a cartographer's assistant?'  ",
				"note": "Rocha smiles.  The smile is different from any smile you have seen on Parsa.  She joins the party.  Correction 5 opens later.",
				"sets": {"rocha_recruited": true}
			},
			{
				"id": "rocha_leave",
				"label": "  Let her work.  She looks busy.  ",
				"note": "Rocha stays with the children.  You'll miss the Correction 5 keepsake.  A specific late-game reveal is harder to find.",
				"sets": {"rocha_recruited": false}
			}
		]
	},
	{
		"speaker": "· THAR-KRAI-TAM'S CHAMBER ·",
		"text": "The Kel-Rethani overseer's private chamber.  Seven feet two.  Rust-red skin standard for his tribe.  A specific silvered upper-right blade (family heirloom).  His lower arms are unusually strong from years of specific work.  His face carries a specific tired dignity.\n\nHe sees you.  He does not reach for the blade."
	},
	{
		"speaker": "THAR-KRAI-TAM",
		"text": "'You have come far.  You have earned entry.\n\nI will not ask why.  I will only ask that you leave without disrupting the operation.\n\nMy family depends on this specifically.'\n\nHe names them, unprompted: SORAY, KEV, NAI.  Three children.  Ages twelve, nine, five."
	},
	{
		"speaker": "· CHOICE · confront Thar-Krai-Tam ·",
		"type": "choice",
		"choices": [
			{
				"id": "thar_combat",
				"label": "  Draw your propellant pistol.  This is what has to happen.  ",
				"note": "Combat.  Thar-Krai-Tam falls at critical HP if Working V performed.  His three children are mentioned in a specific Chapter 6 line later.  Kelait freed.",
				"sets": {"thar_krai_tam_outcome": "combat", "kelait_freed": true, "thar_krai_tam_dead": true}
			},
			{
				"id": "thar_empathy",
				"label": "  'You know what you are doing here.  I have seen your face.  You cannot un-know it.  Resign.'  ",
				"note": "Empathy dialogue.  Requires Kanel LIKED or higher.  Thar-Krai-Tam weeps in front of his subordinates.  Resigns.  Helps free the Kelait via a specific side passage.  His eldest daughter Soray will not forgive him.  He accepts it.",
				"sets": {"thar_krai_tam_outcome": "empathy", "kelait_freed": true, "thar_krai_tam_retired": true}
			},
			{
				"id": "thar_walk_away",
				"label": "  Turn around.  This is bigger than you.  Come back another day.  ",
				"note": "Walk away.  Kelait remain enslaved.  You will remember this.  Chapter 6 will remember this.  Yr does not come with you.",
				"sets": {"thar_krai_tam_outcome": "walked_away", "kelait_freed": false, "yr_survived": false}
			}
		]
	},
	{
		"speaker": "· THE ESCAPE ·",
		"text": "The specific escape route Kanel has been planning for years.  Sara Nai leads.  Hel Velli guards the rear.  Rocha, if she is with you, has a specific dev toolkit that opens a specific door that should not have been openable.\n\nYr is at your side.  He looks up when you reach the surface.  His face during that moment is a specific animation the writers noted as 'the most emotional 20 frames of pixel art in the whole game.'\n\nHe says, quietly: 'It is very · very · thank you.  Grandmother said it would be like this.  I did not know it would be like this.'"
	},
	{
		"speaker": "· END CHAPTER 4 ·",
		"text": "A week later, in Talikan, a Delvanni courier finds you at the library.  A folded parchment.  A seal in dark wax · an eight-pointed star.\n\nRafaton requests your presence at the Academy.  For your graduation.\n\nSara Nai reads the seal twice and does not hand the letter back right away.\n\n· CHAPTER 5 · THE ACADEMY ·"
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
	if sfx: sfx.play("mine_drip", 0.5)
	get_tree().create_timer(14.0).timeout.connect(_schedule_ambient)



func boot(state: Dictionary) -> void:
	_run_state = state
	_build_frame()
	_render_current_beat()


func _build_frame() -> void:
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# Basalt-textured horizontal bands
	for y in range(80, 720, 80):
		var band := ColorRect.new()
		band.color = C_STONE
		band.set_anchors_preset(Control.PRESET_TOP_WIDE)
		band.position.y = y
		band.size = Vector2(2000, 40)
		band.color.a = 0.4
		add_child(band)

	# Lantern glow at top-left · specifically
	var lamp := ColorRect.new()
	lamp.color = C_LAMP
	lamp.set_anchors_preset(Control.PRESET_TOP_LEFT)
	lamp.position = Vector2(80, 60)
	lamp.size = Vector2(120, 30)
	lamp.color.a = 0.35
	add_child(lamp)


	# HUD bands
	var hud_top := ColorRect.new()
	hud_top.color = C_GRAY
	hud_top.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	hud_top.offset_top = 0
	hud_top.offset_bottom = 24
	add_child(hud_top)

	var hud_top_text := Label.new()
	hud_top_text.text = "CHAPTER 4 · THE MINES OF DELVAN"
	hud_top_text.set_anchors_preset(Control.PRESET_TOP_LEFT)
	hud_top_text.position = Vector2(12, 6)
	hud_top_text.add_theme_font_size_override("font_size", 14)
	hud_top_text.add_theme_color_override("font_color", C_AMBER)
	add_child(hud_top_text)

	var hud_top_right := Label.new()
	hud_top_right.text = "UNDERGROUND · LANTERN LIT"
	hud_top_right.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	hud_top_right.position = Vector2(-180, 6)
	hud_top_right.add_theme_font_size_override("font_size", 14)
	hud_top_right.add_theme_color_override("font_color", C_LAMP)
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
	hud_bot_text.add_theme_font_size_override("font_size", 14)
	hud_bot_text.add_theme_color_override("font_color", C_GREEN)
	add_child(hud_bot_text)

	# HeroImage · lantern-lit Kelait kitchen · top-right of the mines
	var hero := HeroImage.new()
	if hero.load_from("res://resources/games/vol7/earthman_chronicles/hero_images/mines_lantern.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(220, 124))
		tex_rect.set_anchors_preset(Control.PRESET_TOP_RIGHT)
		tex_rect.position = Vector2(-240, 28)
		tex_rect.size = Vector2(220, 124)
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		add_child(tex_rect)

	# Center Cortex-purple panel
	var panel := ColorRect.new()
	panel.color = C_CORTEX
	panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	panel.offset_left = -400
	panel.offset_right = 400
	panel.offset_top = -240
	panel.offset_bottom = 260
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
	_speaker_lbl.offset_top = -220
	_speaker_lbl.offset_bottom = -200
	_speaker_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_speaker_lbl.add_theme_font_size_override("font_size", 15)
	_speaker_lbl.add_theme_color_override("font_color", C_KELAIT_GOLD)
	add_child(_speaker_lbl)

	_content_lbl = RichTextLabel.new()
	_content_lbl.bbcode_enabled = false
	_content_lbl.fit_content = true
	_content_lbl.set_anchors_preset(Control.PRESET_CENTER)
	_content_lbl.offset_left = -380
	_content_lbl.offset_right = 380
	_content_lbl.offset_top = -190
	_content_lbl.offset_bottom = 120
	_content_lbl.text = String(beat.get("text", ""))
	_content_lbl.add_theme_font_size_override("normal_font_size", 16)
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
	_choices_root.offset_top = 120
	_choices_root.offset_bottom = 260
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
		var need: int = int(choice.get("requires_shenin", 0))
		var have: int = int(_run_state.get("shenin", 0))
		if need > 0 and have < need:
			btn.text = String(choice.get("label", "")) + " · not enough shenin (" + str(have) + "/" + str(need) + ")  "
			btn.disabled = true
		else:
			btn.text = String(choice.get("label", ""))
			btn.pressed.connect(func() -> void: _on_choice_selected(choice))
		btn.add_theme_font_size_override("font_size", 14)
		vh.add_child(btn)

		var note := Label.new()
		note.text = "     " + String(choice.get("note", ""))
		note.add_theme_font_size_override("font_size", 12)
		note.add_theme_color_override("font_color", C_DIM)
		note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		vh.add_child(note)


func _render_advance_button() -> void:
	_choices_root = Control.new()
	_choices_root.set_anchors_preset(Control.PRESET_CENTER)
	_choices_root.offset_left = -80
	_choices_root.offset_right = 80
	_choices_root.offset_top = 180
	_choices_root.offset_bottom = 240
	add_child(_choices_root)

	var btn := Button.new()
	btn.text = "  continue  →  "
	btn.add_theme_font_size_override("font_size", 16)
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
	# Track Working V
	if bool(sets.get("working_v_completed", false)):
		var wc: Array = _run_state.get("workings_completed", [])
		if not wc.has("mass_of_the_phoenix"): wc.append("mass_of_the_phoenix")
		_run_state["workings_completed"] = wc
	# Track Rocha recruitment · adds Correction 5 to eligibility
	if bool(sets.get("rocha_recruited", false)):
		var cf: Array = _run_state.get("corrections_found", [])
		if not cf.has("correction_rochas_signature"): cf.append("correction_rochas_signature")
		_run_state["corrections_found"] = cf
	# Drawing the pistol on Thar-Krai-Tam · the real fight
	if String(sets.get("thar_krai_tam_outcome", "")) == "combat":
		var choices_log_d: Array = _run_state.get("choices_log", [])
		choices_log_d.append({"chapter": 4, "beat": _beat_idx, "choice_id": String(choice.get("id", ""))})
		_run_state["choices_log"] = choices_log_d
		_launch_combat("thar_krai_tam")
		return
	var choices_log: Array = _run_state.get("choices_log", [])
	choices_log.append({"chapter": 4, "beat": _beat_idx, "choice_id": String(choice.get("id", ""))})
	_run_state["choices_log"] = choices_log
	_on_advance()


const COMBAT_SCENE := "res://scenes/games/earthman_chronicles/EarthmanCombat.tscn"
var _combat_overlay: Node = null

func _launch_combat(boss_id: String) -> void:
	_combat_overlay = load(COMBAT_SCENE).instantiate()
	_combat_overlay.combat_complete.connect(_on_combat_complete)
	add_child(_combat_overlay)
	if _combat_overlay.has_method("boot"):
		_combat_overlay.call("boot", {"boss_id": boss_id, "run_state": _run_state})


func _on_combat_complete(boss_id: String, outcome: String) -> void:
	if _combat_overlay != null and is_instance_valid(_combat_overlay):
		_combat_overlay.queue_free()
	_combat_overlay = null
	_run_state["combat_" + boss_id + "_outcome"] = outcome
	if outcome == "defeat":
		# Non-fatal · the story continues, but it remembers
		_run_state["was_dragged_clear"] = true
	_on_advance()


func _on_advance() -> void:
	_beat_idx += 1
	_render_current_beat()


func _end_chapter() -> void:
	# Add Rocha if recruited
	if bool(_run_state.get("rocha_recruited", false)):
		var party: Array = _run_state.get("party_members", ["jack"])
		if not party.has("rocha"):
			party.append("rocha")
		_run_state["party_members"] = party
		var alive: Dictionary = _run_state.get("party_alive", {"jack": true})
		alive["rocha"] = true
		_run_state["party_alive"] = alive
	_run_state["chapter"] = 5

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
