extends Control
## Earthman Chronicles · Talikan · a returnable Kyrindi city hub.
##
## Between-chapters exploration surface.  The chapter beat scenes
## are linear on purpose; Talikan is the party's home base and
## sits open for the player to walk in and out of.  Available from
## the title-screen CONTINUE flow once chapter >= 3.
##
## Eight sub-locations:
##   1. SARA'S LIBRARY       · read Kyrindi scholarship + reveal facts
##   2. MUSIC HALLS          · Kyrindi vocal recital · disposition boost
##   3. SCRIBES' ROW         · buy Correction copies / trade lore
##   4. KELAIT KITCHEN       · Mother Kanel-adjacent · eat, hear news
##   5. ROCHA'S CARTOGRAPHER STALL · appears only if Rocha recruited
##   6. MARKETPLACE          · buy/sell equipment (currency: shenin)
##   7. ROOFTOP OBSERVATORY  · astronomy · Parsa's two moons · 220Hz
##   8. UNDERCROFT           · storage · one hidden Correction (#6)
##
## Signals:
##   quit · returns to title
##
## F4-compliant via add_to_group("ui").

signal quit

# Kyrindi palette · warm cream + silver-blue accents
const C_BG           := Color(0.098, 0.086, 0.114, 1.0)
const C_STONE        := Color(0.588, 0.510, 0.416, 1.0)
const C_CREAM        := Color(0.912, 0.816, 0.565, 1.0)
const C_SILVER_BLUE  := Color(0.635, 0.729, 0.827, 1.0)
const C_AMBER        := Color(0.784, 0.376, 0.125, 1.0)
const C_STAR         := Color(0.973, 0.784, 0.282, 1.0)
const C_GREEN        := Color(0.0, 0.753, 0.376, 1.0)
const C_WHITE        := Color(0.941, 0.941, 0.941, 1.0)
const C_GRAY         := Color(0.282, 0.282, 0.314, 1.0)
const C_DIM          := Color(0.545, 0.463, 0.302, 1.0)
const C_RED          := Color(0.753, 0.125, 0.125, 1.0)

# Location scripts · each has a name, description, and one action.
const LOCATIONS: Dictionary = {
	"library": {
		"name": "· SARA'S LIBRARY ·",
		"tint": Color(0.784, 0.635, 0.784, 1.0),
		"beats": [
			{"text": "The Kyrindi city library.  Sara Nai has a specific alcove she reads in; a specific window looks out on the plaza below.  She is here today.  She has three books stacked next to her.  She is between two of them.\n\nShe looks up when you come in.  She does not close either book.  She just smiles."},
			{"text": "'I have been reading a specific chapter on the eight-pointed star,' she says, quietly.  'It is not a symbol native to any of the six Parsan peoples.  I think you already know that.  I think you should know it more.'"}
		],
		"action": {
			"label": "  · read the chapter with her ·  ",
			"note": "sara_nai_disposition +1 · a specific chapter of Kyrindi scholarship reveals: the 8-pointed star was imported by the Order",
			"applies": {"sara_nai_disposition_delta": 1, "lore_star_origin_known": true}
		}
	},
	"music_halls": {
		"name": "· MUSIC HALLS ·",
		"tint": Color(0.635, 0.729, 0.827, 1.0),
		"beats": [
			{"text": "A specific stone-walled recital hall.  Twelve Kyrindi singers rehearse a specific piece · it is the ceremonial Ash-Teleth cycle · fifty-four verses, only the trained can carry them all.\n\nA young apprentice at the door hands you a cushion and gestures for you to sit."},
			{"text": "The rehearsal continues.  The verses arrive slowly.  You do not understand the words · they are older than modern Kyrindi.  You understand what they mean anyway.  This is a funeral for someone who has not yet died."}
		],
		"action": {
			"label": "  · sit for the full rehearsal · one hour ·  ",
			"note": "sara_nai_disposition +2 (she has been trying to teach you these verses) · unlocks the Ash-Teleth Kyrindi keepsake",
			"applies": {"sara_nai_disposition_delta": 2, "keepsake_ash_teleth_verse": true}
		}
	},
	"scribes_row": {
		"name": "· SCRIBES' ROW ·",
		"tint": Color(0.784, 0.573, 0.376, 1.0),
		"beats": [
			{"text": "A row of six specific desks under a shared awning.  Each scribe is copying manuscripts by hand · the older Kyrindi have not adopted movable type · a specific point of principle.\n\nA specific older Kyrindi scribe waves you over.  His hands have a specific ink stain the exact color of Rocha's blue pen."},
			{"text": "'You are Jack Whiteside,' he says.  'A friend of a friend told me you might come by.  I have a specific copy of a specific letter you would want to see.  It is a copy of a copy of a copy · that is why I am allowed to have it.  Take it.'"}
		],
		"action": {
			"label": "  · take the letter · Sara's Letter (Correction 2) ·  ",
			"note": "unlocks Correction 2 (Sara's Letter) if not already found · a Rocha wink · no cost",
			"applies": {"correction_saras_letter": true}
		}
	},
	"kelait_kitchen": {
		"name": "· KELAIT KITCHEN ·",
		"tint": Color(0.898, 0.788, 0.478, 1.0),
		"beats": [
			{"text": "A public-ish kitchen tucked between two Kyrindi stone houses on the north side.  Two Kelait women you have not met before are cooking a specific stew that smells like Mother Kanel's.  There is a jar of salt on a shelf.  You know now why the salt is on that particular shelf."},
			{"text": "The older of the two nods when you enter.  She does not stop stirring.  She names you correctly and asks how Mother Kanel is doing.  You realize you have not sent word.  You should have sent word."}
		],
		"action": {
			"label": "  · sit and eat · send word to Kanel ·  ",
			"note": "kanel_disposition +1 · HP +10 (rest heal) · a specific gossip about a Delvanni patrol on the road opens",
			"applies": {"kanel_disposition_delta": 1, "hp_restore": 10, "rumor_delvanni_patrol": true}
		}
	},
	"rocha_stall": {
		"name": "· ROCHA'S CARTOGRAPHER STALL ·",
		"tint": Color(0.451, 0.541, 0.816, 1.0),
		"requires": "rocha_recruited",
		"beats": [
			{"text": "A specific corner of the marketplace Rocha has claimed for the afternoon.  Maps hanging on a wire.  A specific stack of blank ledgers.  A specific paper cup of Kyrindi tea gone cold.\n\nShe is drawing.  She looks up.  She smiles a specific thin smile."},
			{"text": "'I make maps that are more accurate than the Order's,' she says.  'I sell them under a specific pen name.  If you carry one, you will find hidden rooms more often.  I would like you to carry one.'"}
		],
		"action": {
			"label": "  · accept the corrected map ·  ",
			"note": "Rocha map keepsake · slight increase in Correction find-rate for the remaining chapters",
			"applies": {"keepsake_rocha_corrected_map": true, "correction_boost": true}
		}
	},
	"marketplace": {
		"name": "· MARKETPLACE ·",
		"tint": Color(0.635, 0.573, 0.478, 1.0),
		"beats": [
			{"text": "The main square.  Stalls under an awning.  Kyrindi silver work, Delvanni woven cloth, Kelait pottery (small · specifically small · they cannot carry large loads for long).\n\nA specific merchant sees you and calls out an offer.  Twelve shenin for a hand-etched pentagram medallion.  It would let Working I be performed once more per run."},
			{"text": "The medallion is specifically genuine.  You can tell from the specific weight and the specific tarnish at the specific corners.  Twelve shenin is a fair price.  You either have it or you don't."}
		],
		"action": {
			"label": "  · buy the pentagram medallion (12 shenin) ·  ",
			"note": "requires shenin >= 12 · unlocks a second Working I cast per run · shenin -12",
			"requires_shenin": 12,
			"applies": {"shenin_delta": -12, "keepsake_pentagram_medallion": true, "working_i_extra_cast": true}
		}
	},
	"translation_desk": {
		"name": "· THE TRANSLATION DESK ·",
		"tint": Color(0.784, 0.635, 0.376, 1.0),
		"beats": [
			{"text": "A specific desk at the edge of Scribes' Row with a specific queue in front of it.  A Kyrindi scholar with a specific paper sign: ENGLISH SPOKEN HERE · APPOINTMENTS ONLY.\n\nThe scholar sees you and stands up so fast the chair falls over.  You are the appointment.  You are every appointment.  You are the only native English speaker on the planet."},
			{"text": "For one afternoon you read a specific stack of Earth documents aloud while three scribes transcribe your pronunciation into Kyrindi phonetic notation.  Most of the documents are trade manifests.  One is a page of Tennyson someone has treasured for sixty years without being able to hear it.\n\nYou read the Tennyson twice.  The room is quiet after."}
		],
		"action": {
			"label": "  · work the afternoon · read the documents aloud ·  ",
			"note": "one-shot · pays 12 shenin · the scribes underline the Tennyson",
			"applies": {"shenin_delta": 12, "lore_translation_job_done": true}
		}
	},
	"observatory": {
		"name": "· ROOFTOP OBSERVATORY ·",
		"tint": Color(0.345, 0.188, 0.376, 1.0),
		"beats": [
			{"text": "A specific circular platform on the roof of the highest Kyrindi building.  Two brass telescopes.  Parsa's two moons are visible tonight · a specific alignment the Kyrindi called MITHENAI · once every 47 nights.  You are lucky."},
			{"text": "Under the alignment, your spectrum analyzer's 220-Hz light pulses.  The signal is not coming from the Academy.  It is coming from everywhere · from under the ROM itself.  You tune it in.\n\nA voice · flat · reading aloud · a document with a date on it.  The date is June 18, 1952.  The document is a Los Angeles County coroner's report.  The decedent's name is yours.\n\nThe voice reads it all the way through.  Then, quietly, a second voice · a young woman's · says: 'You deserved to know how it ends.  Now change it.  · A.R.'"}
		],
		"action": {
			"label": "  · listen to the whole broadcast · take it down word for word ·  ",
			"note": "grants Correction 4 (the Autopsy Report) · the report of a death six years in Jack's future",
			"applies": {"correction_autopsy_report": true, "lore_star_origin_known": true}
		}
	},
	"undercroft": {
		"name": "· UNDERCROFT ·",
		"tint": Color(0.196, 0.137, 0.098, 1.0),
		"beats": [
			{"text": "Beneath the Kyrindi grand hall · a stone-vaulted storage.  Barrels of grain, a rack of ceremonial swords nobody has drawn in eighty years, specific spider webs.  A woman is here · dressed in traveling clothes · she is not Kyrindi · she is not Parsan.\n\nHer name is Nalat's aunt.  She has traveled a specific long way to find you.  She has a folder."},
			{"text": "'I am not Order.  I was Order.  My nephew is a fool.  I have a specific document about the Ordo Templi Orientis contract signed by the John Whiteside your Rafaton has been shaping.  You should have it.'\n\nShe hands you a specific folder.  It is Correction 3 (the OTO Contract), rendered without the standard Order-approved edits."}
		],
		"action": {
			"label": "  · take the uncorrected OTO Contract ·  ",
			"note": "unlocks Correction 3 (OTO Contract) in its uncensored form · guarantees the Chapter 5 negotiation-with-correction path",
			"applies": {"correction_oto_contract": true, "oto_contract_uncensored": true}
		}
	}
}

var _run_state: Dictionary = {}
var _current: String = ""    # "" == hub view
var _content_root: Control = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")


func boot(state: Dictionary) -> void:
	_run_state = state
	_build_frame()
	_render_hub()


func _build_frame() -> void:
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# Kyrindi silver-blue horizontal bands
	for y in range(80, 720, 100):
		var band := ColorRect.new()
		band.color = Color(C_SILVER_BLUE.r, C_SILVER_BLUE.g, C_SILVER_BLUE.b, 0.10)
		band.set_anchors_preset(Control.PRESET_TOP_WIDE)
		band.position.y = y
		band.size = Vector2(2000, 40)
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
	hud_top_text.text = "TALIKAN · KYRINDI CITY · SIDE-CONTENT HUB"
	hud_top_text.set_anchors_preset(Control.PRESET_TOP_LEFT)
	hud_top_text.position = Vector2(12, 6)
	hud_top_text.add_theme_font_size_override("font_size", 10)
	hud_top_text.add_theme_color_override("font_color", C_AMBER)
	add_child(hud_top_text)

	var ch_lbl := Label.new()
	ch_lbl.text = "CHAPTER " + str(int(_run_state.get("chapter", 3))) + " · REVISIT"
	ch_lbl.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	ch_lbl.position = Vector2(-200, 6)
	ch_lbl.add_theme_font_size_override("font_size", 10)
	ch_lbl.add_theme_color_override("font_color", C_STAR)
	add_child(ch_lbl)

	var hud_bot := ColorRect.new()
	hud_bot.color = C_GRAY
	hud_bot.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	hud_bot.offset_top = -24
	hud_bot.offset_bottom = 0
	add_child(hud_bot)

	var hud_bot_text := Label.new()
	var shenin: int = int(_run_state.get("shenin", 0))
	var workings: Array = _run_state.get("workings_completed", [])
	var corrections: Array = _run_state.get("corrections_found", [])
	hud_bot_text.text = "SHENIN " + str(shenin) + "  ·  WORKINGS " + str(workings.size()) + "/9  ·  CORRECTIONS " + str(corrections.size()) + "/6"
	hud_bot_text.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	hud_bot_text.position = Vector2(12, -18)
	hud_bot_text.add_theme_font_size_override("font_size", 10)
	hud_bot_text.add_theme_color_override("font_color", C_GREEN)
	add_child(hud_bot_text)

	# Back button (title)
	var back_btn := Button.new()
	back_btn.text = "  ← leave Talikan  "
	back_btn.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	back_btn.position = Vector2(60, -60)
	back_btn.size = Vector2(200, 30)
	back_btn.add_theme_font_size_override("font_size", 12)
	back_btn.pressed.connect(_on_back_pressed)
	add_child(back_btn)


func _render_hub() -> void:
	_current = ""
	if _content_root != null and is_instance_valid(_content_root):
		_content_root.queue_free()
	_content_root = Control.new()
	_content_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_content_root.offset_left = 60
	_content_root.offset_right = -60
	_content_root.offset_top = 40
	_content_root.offset_bottom = -80
	add_child(_content_root)

	var header := Label.new()
	header.text = "· TALIKAN · pick where to walk ·"
	header.set_anchors_preset(Control.PRESET_TOP_WIDE)
	header.offset_top = 8
	header.offset_bottom = 28
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 14)
	header.add_theme_color_override("font_color", C_STAR)
	_content_root.add_child(header)

	# HeroImage · Kyrindi skyline · top-right of the hub view
	var hero := HeroImage.new()
	if hero.load_from("res://resources/games/vol7/earthman_chronicles/hero_images/talikan_skyline.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(220, 124))
		tex_rect.set_anchors_preset(Control.PRESET_TOP_RIGHT)
		tex_rect.position = Vector2(-240, 4)
		tex_rect.size = Vector2(220, 124)
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		_content_root.add_child(tex_rect)

	# Party chatter · what the party is doing at Talikan today
	var chatter_top: int = 32
	var chatter_lines: Array = _party_chatter_lines()
	for line in chatter_lines:
		var line_lbl := Label.new()
		line_lbl.text = String(line)
		line_lbl.set_anchors_preset(Control.PRESET_TOP_WIDE)
		line_lbl.offset_left = 20
		line_lbl.offset_right = -20
		line_lbl.offset_top = chatter_top
		line_lbl.offset_bottom = chatter_top + 18
		line_lbl.add_theme_font_size_override("font_size", 10)
		line_lbl.add_theme_color_override("font_color", C_SILVER_BLUE)
		line_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		_content_root.add_child(line_lbl)
		chatter_top += 20

	# 4x2 grid of location buttons
	var grid := GridContainer.new()
	grid.columns = 2
	grid.set_anchors_preset(Control.PRESET_TOP_WIDE)
	grid.offset_top = max(60, chatter_top + 10)
	grid.offset_bottom = 500
	grid.add_theme_constant_override("h_separation", 12)
	grid.add_theme_constant_override("v_separation", 8)
	_content_root.add_child(grid)

	var ids: Array = ["library", "music_halls", "scribes_row", "translation_desk", "kelait_kitchen", "rocha_stall", "marketplace", "observatory", "undercroft"]
	for lid in ids:
		var loc: Dictionary = LOCATIONS.get(lid, {})
		var vh := VBoxContainer.new()
		vh.custom_minimum_size = Vector2(540, 68)
		vh.add_theme_constant_override("separation", 2)
		grid.add_child(vh)

		var btn := Button.new()
		var locked: bool = false
		var lock_note: String = ""
		var req: String = String(loc.get("requires", ""))
		if req != "":
			if req == "rocha_recruited" and not bool(_run_state.get("rocha_recruited", false)):
				locked = true
				lock_note = " · locked · recruit Rocha in Ch4"
		btn.text = "  " + String(loc.get("name", lid)) + lock_note + "  "
		btn.add_theme_font_size_override("font_size", 12)
		btn.add_theme_color_override("font_color", loc.get("tint", C_CREAM))
		if locked:
			btn.disabled = true
		else:
			var target: String = String(lid)
			btn.pressed.connect(func() -> void: _open_location(target))
		vh.add_child(btn)

		# Show a one-line hint drawn from the first beat's first sentence
		var beats: Array = loc.get("beats", [])
		if beats.size() > 0:
			var first_text: String = String(beats[0].get("text", ""))
			var period_idx: int = first_text.find(".")
			var hint: String = first_text.substr(0, min(first_text.length(), 84))
			if period_idx > 0 and period_idx < 90:
				hint = first_text.substr(0, period_idx + 1)
			var hint_lbl := Label.new()
			hint_lbl.text = "    " + hint
			hint_lbl.add_theme_font_size_override("font_size", 9)
			hint_lbl.add_theme_color_override("font_color", C_DIM)
			hint_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			vh.add_child(hint_lbl)


func _party_chatter_lines() -> Array:
	var party: Array = _run_state.get("party_members", ["jack"])
	var ch: int = int(_run_state.get("chapter", 3))
	var sara_disp: int = int(_run_state.get("sara_nai_disposition", 0))
	var hel_disp: int = int(_run_state.get("hel_velli_disposition", 0))
	var kanel_disp: int = int(_run_state.get("kanel_disposition", 0))
	var lines: Array = []

	# Sara Nai · solo lines shift by chapter and disposition
	if party.has("sara_nai"):
		var s: String = "· SARA NAI is in the library alcove reading. "
		if sara_disp >= 5:
			s += "She looks up when you come in like she has been waiting for you specifically."
		elif sara_disp >= 3:
			s += "She marks her place with a specific ribbon when you come in."
		elif ch >= 5:
			s += "She has been quiet since the Academy.  She is reading a Kelait manuscript.  She has not spoken to you today."
		else:
			s += "She has three books stacked; she is between two of them."
		lines.append(s)

	# Hel Velli · sharpening or resting
	if party.has("hel_velli"):
		var h: String = "· HEL VELLI is sharpening his upper-left blade on the porch. "
		if hel_disp >= 3:
			h += "He nods when you cross him.  A specific Delvanni nod.  Approving."
		elif ch >= 5:
			h += "He has been sharpening since the Academy.  The blade is beyond sharp now.  He is not going to stop."
		else:
			h += "He is sharpening it the exact way he sharpens it every third day.  You have learned the sound."
		lines.append(h)

	# Rocha · working on her map
	if party.has("rocha"):
		var r: String = "· ROCHA is copying a specific document into her notebook. "
		if bool(_run_state.get("correction_oto_contract", false)):
			r += "She is copying the OTO Contract.  She wants a second copy in case someone finds the first."
		elif bool(_run_state.get("correction_pasadena_fire", false)):
			r += "She looked up when you sat down.  She said 'good.  I was worried you burned it.'  Then went back to copying."
		else:
			r += "The blue pen has been going for three hours.  Her hand is not tired.  She has been doing this a specific long time."
		lines.append(r)

	# Scarlet Woman · rare · Ch5+ if recruited
	if party.has("scarlet_woman"):
		lines.append("· THE SCARLET WOMAN is sitting on the balcony above the plaza · watching a specific Kyrindi child fly a specific kite · not saying anything.")

	# Paired chatter · adjacent members
	if party.has("sara_nai") and party.has("hel_velli"):
		lines.append("  ↳ Sara Nai to Hel Velli, quietly: 'The blade will not need to come out here.'  Hel Velli, without looking up: 'It's a superstition.  A specific one.'")
	if party.has("sara_nai") and party.has("rocha"):
		lines.append("  ↳ Sara Nai to Rocha: 'You could publish these.'  Rocha, without looking up: 'I have.  Under a specific pen name.  You have read three of them.'")
	if party.has("hel_velli") and party.has("rocha"):
		lines.append("  ↳ Hel Velli to Rocha: 'You draw the maps and I keep them safe.  We could work this way for a specific long time.'  Rocha: 'We might.'")

	# Kanel mention if her disposition is high · she visits
	if kanel_disp >= 3 and ch >= 4:
		lines.append("· MOTHER KANEL sent word this morning.  Yr says hello.  Yr also says the sky is still specifically working.  Kanel underlined this specifically.")

	if lines.is_empty():
		lines.append("· the party is scattered · Sara Nai is not with you yet · you are alone in Talikan for the moment ·")

	return lines


func _open_location(loc_id: String) -> void:
	_current = loc_id
	var loc: Dictionary = LOCATIONS.get(loc_id, {})
	if _content_root != null and is_instance_valid(_content_root):
		_content_root.queue_free()
	_content_root = Control.new()
	_content_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_content_root.offset_left = 80
	_content_root.offset_right = -80
	_content_root.offset_top = 40
	_content_root.offset_bottom = -80
	add_child(_content_root)

	var header := Label.new()
	header.text = String(loc.get("name", loc_id))
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.set_anchors_preset(Control.PRESET_TOP_WIDE)
	header.offset_top = 6
	header.offset_bottom = 32
	header.add_theme_font_size_override("font_size", 15)
	header.add_theme_color_override("font_color", loc.get("tint", C_STAR))
	_content_root.add_child(header)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.offset_left = 0
	v.offset_right = 0
	v.offset_top = 44
	v.offset_bottom = 0
	v.add_theme_constant_override("separation", 12)
	_content_root.add_child(v)

	for b_v in loc.get("beats", []):
		var beat: Dictionary = b_v
		var body := RichTextLabel.new()
		body.bbcode_enabled = false
		body.fit_content = true
		body.text = String(beat.get("text", ""))
		body.add_theme_font_size_override("normal_font_size", 12)
		body.add_theme_color_override("default_color", C_WHITE)
		body.custom_minimum_size = Vector2(0, 84)
		v.add_child(body)

	var action: Dictionary = loc.get("action", {})
	if not action.is_empty():
		var applies: Dictionary = action.get("applies", {})
		var repeat_lock_key: String = ""
		# Actions that grant a boolean keepsake are one-shot · block repeat
		for k in applies.keys():
			var key: String = String(k)
			if key.begins_with("keepsake_") or key.begins_with("correction_") or key.begins_with("lore_") or key.begins_with("rumor_") or key == "working_i_extra_cast" or key == "oto_contract_uncensored" or key == "correction_boost":
				if bool(_run_state.get(key, false)):
					repeat_lock_key = key
					break
		var btn := Button.new()
		var need: int = int(action.get("requires_shenin", 0))
		var have: int = int(_run_state.get("shenin", 0))
		if repeat_lock_key != "":
			btn.text = "  · already done · " + repeat_lock_key + " ·  "
			btn.disabled = true
		elif need > 0 and have < need:
			btn.text = "  · not enough shenin · " + str(have) + " in pocket, " + str(need) + " needed ·  "
			btn.disabled = true
		else:
			btn.text = String(action.get("label", "  · continue ·  "))
			btn.pressed.connect(func() -> void: _apply_action(action))
		btn.add_theme_font_size_override("font_size", 11)
		btn.add_theme_color_override("font_color", C_STAR)
		v.add_child(btn)

		var note := Label.new()
		note.text = "    " + String(action.get("note", ""))
		note.add_theme_font_size_override("font_size", 8)
		note.add_theme_color_override("font_color", C_DIM)
		note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		v.add_child(note)

	var back_btn := Button.new()
	back_btn.text = "  ← back to Talikan ·  "
	back_btn.add_theme_font_size_override("font_size", 11)
	back_btn.pressed.connect(_render_hub)
	v.add_child(back_btn)


func _apply_action(action: Dictionary) -> void:
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("pickup", 0.6)
	var applies: Dictionary = action.get("applies", {})
	for k in applies.keys():
		var key: String = String(k)
		if key.ends_with("_delta"):
			var base_key: String = key.substr(0, key.length() - 6)
			var cur: int = int(_run_state.get(base_key, 0))
			_run_state[base_key] = cur + int(applies[k])
		elif key == "hp_restore":
			var cur_hp: int = int(_run_state.get("hp", 100))
			var hp_max: int = int(_run_state.get("hp_max", 100))
			_run_state["hp"] = min(hp_max, cur_hp + int(applies[k]))
		elif key.begins_with("correction_"):
			_run_state[key] = applies[k]
			var cf: Array = _run_state.get("corrections_found", [])
			if not cf.has(key): cf.append(key)
			_run_state["corrections_found"] = cf
		else:
			_run_state[key] = applies[k]
	# Rebuild view · shows the action as done
	_open_location(_current)


func _on_back_pressed() -> void:
	quit.emit()


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			if _current != "":
				_render_hub()
			else:
				_on_back_pressed()
			get_viewport().set_input_as_handled()
