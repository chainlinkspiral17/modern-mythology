extends Control
## Fey Faire · The Trailer · Prospero's Airstream · scaffold pass.
##
## The player's persistent home base.  Six fixtures are
## interactable and open sub-panels:
##   · KEEPSAKE BOOKCASE · 20 active slots + footlocker overflow ·
##     shows collected keepsakes from keepsakes.json with lore +
##     effect · scaffolded read-only for this pass (swap-active
##     UI is a follow-up commit)
##   · COTS · party roster · lists recruited feys · dismiss/invite
##     stubs
##   · WRITING DESK · compendium · met/recruited/hostile feys
##     from feys.json · grouped by court
##   · MEMORY MIRRORS · six mirrors matching the boot questionnaire
##     · cracked when memory lost
##   · HEARTH · HP restore stub (no HP tracking in scaffold)
##   · HELIA THE CAT · per-fey disposition indicator (tail flick
##     description per recruited fey)
##
## Signals:
##   quit · returns to Gate
##
## F4-compliant via add_to_group("ui").

signal quit
signal enter_mirror(mirror_id: String)
signal request_save

const FEYS_PATH      := "res://resources/games/vol7/fey_faire/feys.json"
const KEEPSAKES_PATH := "res://resources/games/vol7/fey_faire/keepsakes.json"
const ERRANDS_PATH   := "res://resources/games/vol7/fey_faire/errands.json"

var _errands: Array = []

# Trailer palette · warmer, more mundane than the Faire
const C_BG        := Color(0.145, 0.098, 0.075, 1.0)   # inside-a-trailer dark
const C_WOOD      := Color(0.451, 0.294, 0.180, 1.0)   # Craftsman wood
const C_WOOD_HI   := Color(0.671, 0.443, 0.263, 1.0)
const C_CREAM     := Color(0.957, 0.878, 0.816, 1.0)
const C_ROSE      := Color(0.878, 0.722, 0.753, 1.0)
const C_GOLD      := Color(0.973, 0.784, 0.282, 1.0)
const C_GOLD_DIM  := Color(0.72, 0.52, 0.26, 1.0)
const C_LAMP      := Color(0.973, 0.816, 0.518, 1.0)   # warm lamplight
const C_MEMORY    := Color(0.62, 0.55, 0.72, 1.0)      # memory-mirror silvery
const C_CRACKED   := Color(0.42, 0.30, 0.30, 1.0)      # cracked mirror
const C_RECRUITED := Color(0.62, 0.82, 0.55, 1.0)      # warren need met · green

var _run_state: Dictionary = {}
var _feys_by_id: Dictionary = {}
var _keepsakes_by_id: Dictionary = {}
var _panel_root: Control = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")


func boot(state: Dictionary) -> void:
	_run_state = state
	_load_data()
	_build_frame()
	_render_main_view()


func _load_data() -> void:
	if FileAccess.file_exists(FEYS_PATH):
		var f := FileAccess.open(FEYS_PATH, FileAccess.READ)
		var parsed: Variant = JSON.parse_string(f.get_as_text())
		f.close()
		if parsed is Dictionary:
			for entry_v in (parsed as Dictionary).get("feys", []):
				var entry: Dictionary = entry_v
				_feys_by_id[String(entry.get("id", ""))] = entry
	if FileAccess.file_exists(KEEPSAKES_PATH):
		var f2 := FileAccess.open(KEEPSAKES_PATH, FileAccess.READ)
		var parsed2: Variant = JSON.parse_string(f2.get_as_text())
		f2.close()
		if parsed2 is Dictionary:
			for entry_v in (parsed2 as Dictionary).get("keepsakes", []):
				var entry: Dictionary = entry_v
				_keepsakes_by_id[String(entry.get("id", ""))] = entry
	if FileAccess.file_exists(ERRANDS_PATH):
		var f3 := FileAccess.open(ERRANDS_PATH, FileAccess.READ)
		var parsed3: Variant = JSON.parse_string(f3.get_as_text())
		f3.close()
		if parsed3 is Dictionary:
			_errands = (parsed3 as Dictionary).get("errands", [])


func _build_frame() -> void:
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# Wood-plank floor · horizontal bands
	for y in range(360, 720, 24):
		var plank := ColorRect.new()
		plank.color = C_WOOD if (y / 24) % 2 == 0 else C_WOOD_HI
		plank.set_anchors_preset(Control.PRESET_TOP_WIDE)
		plank.position.y = y
		plank.size = Vector2(2000, 12)
		add_child(plank)

	# Warm lamp glow at center-top · Prospero's bare bulb
	var lamp := ColorRect.new()
	lamp.color = C_LAMP
	lamp.set_anchors_preset(Control.PRESET_TOP_LEFT)
	lamp.position = Vector2(0, 0)
	lamp.size = Vector2(2000, 60)
	# Simulate glow via a specific alpha
	lamp.color.a = 0.25
	add_child(lamp)

	# Header
	var header := Label.new()
	header.text = "· THE TRAILER · PROSPERO'S AIRSTREAM ·"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 18)
	header.add_theme_color_override("font_color", C_LAMP)
	header.set_anchors_preset(Control.PRESET_TOP_WIDE)
	header.offset_top = 20
	header.offset_bottom = 48
	add_child(header)


func _clear_panel() -> void:
	if _panel_root != null and is_instance_valid(_panel_root):
		_panel_root.queue_free()
	_panel_root = null


func _render_main_view() -> void:
	_clear_panel()
	_panel_root = Control.new()
	_panel_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_panel_root.offset_top = 60
	_panel_root.offset_bottom = -20
	_panel_root.offset_left = 40
	_panel_root.offset_right = -40
	add_child(_panel_root)

	# HeroImage · trailer interior · top-right corner
	var hero := HeroImage.new()
	if hero.load_from("res://resources/games/vol7/fey_faire/hero_images/trailer_interior.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(220, 124))
		tex_rect.set_anchors_preset(Control.PRESET_TOP_RIGHT)
		tex_rect.position = Vector2(-240, 4)
		tex_rect.size = Vector2(220, 124)
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		_panel_root.add_child(tex_rect)

	# 3x2 fixture grid
	var grid := GridContainer.new()
	grid.columns = 3
	grid.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	grid.add_theme_constant_override("h_separation", 16)
	grid.add_theme_constant_override("v_separation", 16)
	_panel_root.add_child(grid)

	_add_fixture_button(grid, "KEEPSAKE BOOKCASE",
		"twenty active slots · footlocker overflow",
		_active_keepsake_count_string(),
		_render_bookcase_view)

	_add_fixture_button(grid, "COTS · PARTY ROSTER",
		"recruited feys · and what each grants the party",
		_party_summary_string(),
		_render_cots_view)

	_add_fixture_button(grid, "THE WARREN · ERRANDS",
		"feys beyond the fence · your party vouches you in",
		_warren_summary_string(),
		_render_warren_view)

	_add_fixture_button(grid, "WRITING DESK · COMPENDIUM",
		"met · recruited · defeated · dismissed",
		_compendium_summary_string(),
		_render_compendium_view)

	_add_fixture_button(grid, "MEMORY MIRRORS",
		"six · one per boot question · crack on death",
		_memory_summary_string(),
		_render_memory_view)

	_add_fixture_button(grid, "HEARTH",
		"kitchen · restore HP without advancing the night",
		"pending · no HP tracking yet",
		null)

	_add_fixture_button(grid, "HELIA · THE CAT",
		"Prospero's cat · shows how each recruited fey feels",
		_helia_summary_string(),
		_render_helia_view)

	# NG+ · after three summers, the owner of the Airstream wakes.
	var lifetime_seen: Array = _run_state.get("endings_seen", [])
	if lifetime_seen.size() >= 3:
		var talked: bool = bool(_run_state.get("prospero_woke", false))
		_add_fixture_button(grid, "PROSPERO",
			"the bed at the back · he is sitting up · he is looking at you",
			"awake" if not talked else "asleep again · he said what he had",
			_render_prospero_view if not talked else null)

	# Back button
	var back := Button.new()
	back.text = "  ← back to the Gate  "
	back.add_theme_font_size_override("font_size", 15)
	back.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	back.offset_top = -40
	back.offset_bottom = -8
	back.pressed.connect(_on_back)
	_panel_root.add_child(back)


func _add_fixture_button(parent: Node, title: String, subtitle: String, status: String, callback: Variant) -> void:
	var cell := ColorRect.new()
	cell.color = C_WOOD
	cell.custom_minimum_size = Vector2(320, 120)
	parent.add_child(cell)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.offset_left = 12
	v.offset_right = -12
	v.offset_top = 10
	v.offset_bottom = -10
	v.add_theme_constant_override("separation", 4)
	cell.add_child(v)

	var title_lbl := Label.new()
	title_lbl.text = title
	title_lbl.add_theme_font_size_override("font_size", 16)
	title_lbl.add_theme_color_override("font_color", C_LAMP)
	v.add_child(title_lbl)

	var subtitle_lbl := Label.new()
	subtitle_lbl.text = "· " + subtitle
	subtitle_lbl.add_theme_font_size_override("font_size", 13)
	subtitle_lbl.add_theme_color_override("font_color", C_GOLD_DIM)
	v.add_child(subtitle_lbl)

	var status_lbl := Label.new()
	status_lbl.text = status
	status_lbl.add_theme_font_size_override("font_size", 14)
	status_lbl.add_theme_color_override("font_color", C_CREAM)
	status_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(status_lbl)

	var btn := Button.new()
	btn.text = "  open  " if callback != null else "  pending  "
	btn.add_theme_font_size_override("font_size", 14)
	btn.disabled = (callback == null)
	if callback != null:
		btn.pressed.connect(callback)
	v.add_child(btn)


func _active_keepsake_count_string() -> String:
	var kp: Array = _run_state.get("keepsakes", [])
	return "%d keepsake%s · 20 slots" % [kp.size(), "" if kp.size() == 1 else "s"]


func _party_summary_string() -> String:
	var recruited: Array = _run_state.get("recruited_feys", [])
	if recruited.is_empty(): return "· no recruits yet ·"
	var names: Array = []
	for id in recruited:
		var fey: Dictionary = _feys_by_id.get(String(id), {})
		if not fey.is_empty():
			names.append(String(fey.get("name", id)))
	return "recruited · " + ", ".join(names)


func _compendium_summary_string() -> String:
	var met: Array = _run_state.get("met_feys", [])
	var recruited: Array = _run_state.get("recruited_feys", [])
	var total: int = _feys_by_id.size()
	return "%d recruited · %d encountered · %d unmet" % [recruited.size(), met.size(), max(0, total - recruited.size() - met.size())]


func _memory_summary_string() -> String:
	var lost: int = int(_run_state.get("memories_lost", 0))
	return "%d of 6 memories intact" % [6 - lost]


func _helia_summary_string() -> String:
	var recruited: Array = _run_state.get("recruited_feys", [])
	if recruited.is_empty(): return "· no recruits to indicate ·"
	return "%d fey%s to observe" % [recruited.size(), "" if recruited.size() == 1 else "s"]


# ── Bookcase view ─────────────────────────────────────────────
func _render_bookcase_view() -> void:
	_render_sub_view("KEEPSAKE BOOKCASE", func(v: VBoxContainer) -> void:
		# Cross-Oneironautics · Rocha's note lands here permanently
		# after THE CORRECTION is seen in Earthman Chronicles.
		if OneironauticsTokens.has("rocha_note_permanently_unlocked_in_fey_faire_trailer"):
			var rocha_hdr := Label.new()
			rocha_hdr.text = "✦ A HANDWRITTEN NOTE · blue pen · not from this game"
			rocha_hdr.add_theme_font_size_override("font_size", 15)
			rocha_hdr.add_theme_color_override("font_color", C_GOLD)
			v.add_child(rocha_hdr)
			var rocha_body := Label.new()
			rocha_body.text = "    It is tucked between two books that do not touch it.  Two words: 'for jack'.  The handwriting leans slightly right.  Nobody in Fey Faire wrote this.  Helia sleeps next to it every night."
			rocha_body.add_theme_font_size_override("font_size", 13)
			rocha_body.add_theme_color_override("font_color", C_ROSE)
			rocha_body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			v.add_child(rocha_body)
			var sep_r := Control.new()
			sep_r.custom_minimum_size = Vector2(0, 8)
			v.add_child(sep_r)
		var kp: Array = _run_state.get("keepsakes", [])
		if kp.is_empty():
			var empty := Label.new()
			empty.text = "· the bookcase is empty ·"
			empty.add_theme_color_override("font_color", C_GOLD_DIM)
			empty.add_theme_font_size_override("font_size", 15)
			v.add_child(empty)
			var hint := Label.new()
			hint.text = "keepsakes are earned by choosing them at boot, gifted by feys, or found across the Faire."
			hint.add_theme_color_override("font_color", C_CREAM)
			hint.add_theme_font_size_override("font_size", 14)
			hint.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			v.add_child(hint)
			return
		for kp_id in kp:
			var entry: Dictionary = _keepsakes_by_id.get(String(kp_id), {})
			if entry.is_empty(): continue
			_add_keepsake_row(v, entry))


func _add_keepsake_row(parent: Node, entry: Dictionary) -> void:
	var row := ColorRect.new()
	row.color = C_WOOD_HI
	row.custom_minimum_size = Vector2(0, 80)
	parent.add_child(row)

	var vh := VBoxContainer.new()
	vh.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	vh.offset_left = 10
	vh.offset_right = -10
	vh.offset_top = 6
	vh.offset_bottom = -6
	vh.add_theme_constant_override("separation", 2)
	row.add_child(vh)

	var name_lbl := Label.new()
	name_lbl.text = String(entry.get("name", ""))
	name_lbl.add_theme_font_size_override("font_size", 15)
	name_lbl.add_theme_color_override("font_color", C_LAMP)
	vh.add_child(name_lbl)

	var lore_lbl := RichTextLabel.new()
	lore_lbl.bbcode_enabled = false
	lore_lbl.fit_content = true
	lore_lbl.text = String(entry.get("lore", ""))
	lore_lbl.add_theme_font_size_override("normal_font_size", 13)
	lore_lbl.add_theme_color_override("default_color", C_CREAM)
	vh.add_child(lore_lbl)

	var effect_lbl := Label.new()
	effect_lbl.text = "· " + String(entry.get("effect", "no effect authored"))
	effect_lbl.add_theme_font_size_override("font_size", 13)
	effect_lbl.add_theme_color_override("font_color", C_ROSE)
	effect_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	vh.add_child(effect_lbl)


# ── Cots view ─────────────────────────────────────────────────
# Standing in words, not numbers — the Courts do not keep score in
# a way they'd admit to.
func _standing_word(n: int) -> String:
	if n >= 8: return "beloved"
	if n >= 5: return "known"
	if n >= 2: return "noticed"
	if n >= 1: return "glimpsed"
	return "unmet"


func _render_cots_view() -> void:
	_render_sub_view("COTS · PARTY ROSTER", func(v: VBoxContainer) -> void:
		# Court standing — the three Courts' opinion of you, surfaced
		# where the party lives. The counters have always been kept
		# (combat and negotiation both feed them); now they're read.
		var se: int = int(_run_state.get("court_seelie", 0))
		var un: int = int(_run_state.get("court_unseelie", 0))
		var wf: int = int(_run_state.get("court_wildfey", 0))
		var standing := Label.new()
		standing.text = "STANDING · seelie %s · unseelie %s · wildfey %s" % [
			_standing_word(se), _standing_word(un), _standing_word(wf)]
		standing.add_theme_font_size_override("font_size", 13)
		standing.add_theme_color_override("font_color", C_CREAM.darkened(0.2))
		v.add_child(standing)
		var rule := ColorRect.new()
		rule.color = Color(C_LAMP.r, C_LAMP.g, C_LAMP.b, 0.25)
		rule.custom_minimum_size.y = 1
		v.add_child(rule)

		# BOONS · what the roster GRANTS · reasons to hold each fey.
		_add_boons_readout(v)
		var rule2 := ColorRect.new()
		rule2.color = Color(C_LAMP.r, C_LAMP.g, C_LAMP.b, 0.25)
		rule2.custom_minimum_size.y = 1
		v.add_child(rule2)

		var protagonist := Label.new()
		var player_name: String = String(_run_state.get("questionnaire", {}).get("player_name", "you"))
		protagonist.text = "COT 1 · " + player_name + " · always here"
		protagonist.add_theme_font_size_override("font_size", 15)
		protagonist.add_theme_color_override("font_color", C_LAMP)
		v.add_child(protagonist)

		var recruited: Array = _run_state.get("recruited_feys", [])
		var slot_idx: int = 2
		for id in recruited:
			if slot_idx > 4:
				break
			var fey_id: String = String(id)
			var fey: Dictionary = _feys_by_id.get(fey_id, {})
			if fey.is_empty(): continue
			var cot := Label.new()
			cot.text = "COT " + str(slot_idx) + " · " + String(fey.get("name", fey_id)) + " · " + String(fey.get("court", "?"))
			cot.add_theme_font_size_override("font_size", 15)
			cot.add_theme_color_override("font_color", C_CREAM)
			v.add_child(cot)

			# Solo line for this fey
			var solo: String = _solo_line(fey_id)
			if solo != "":
				var solo_lbl := Label.new()
				solo_lbl.text = "    " + solo
				solo_lbl.add_theme_font_size_override("font_size", 13)
				solo_lbl.add_theme_color_override("font_color", C_ROSE)
				solo_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
				v.add_child(solo_lbl)

			# Paired line if the NEXT recruited fey (adjacent cot) is present
			var next_idx: int = recruited.find(fey_id) + 1
			if next_idx < recruited.size():
				var other_id: String = String(recruited[next_idx])
				var pair: String = _pair_line(fey_id, other_id)
				if pair != "":
					var pair_lbl := Label.new()
					pair_lbl.text = "    ↳ " + pair
					pair_lbl.add_theme_font_size_override("font_size", 13)
					pair_lbl.add_theme_color_override("font_color", C_GOLD_DIM)
					pair_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
					v.add_child(pair_lbl)

			slot_idx += 1
		while slot_idx <= 4:
			var empty := Label.new()
			empty.text = "COT " + str(slot_idx) + " · empty"
			empty.add_theme_font_size_override("font_size", 15)
			empty.add_theme_color_override("font_color", C_GOLD_DIM)
			v.add_child(empty)
			slot_idx += 1

		if recruited.size() > 4:
			var overflow := Label.new()
			overflow.text = "\n· " + str(recruited.size() - 3) + " more feys are on a specific rotating cot-share arrangement they worked out among themselves ·"
			overflow.add_theme_font_size_override("font_size", 13)
			overflow.add_theme_color_override("font_color", C_ROSE)
			overflow.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			v.add_child(overflow))


# Per-fey solo lines · what they say when they're the only one speaking.
# Draws lightly on the fey's specific-ness · Ondine talks about the counter,
# Puck about his tricks, Boggart about lost things, etc.
func _solo_line(fey_id: String) -> String:
	match fey_id:
		"ondine":                return "'The rings do not matter.  I have said this before.  I will say it again.  Sit.'"
		"cricket_the_cricket":   return "'I have been at that counter for a very long time.  It is nice to sit in a chair for once.'"
		"boggart":               return "'Lost-and-found is not a metaphor.  I DO find things.  I have found your keys in a way you would not have.'"
		"nixie":                 return "'The fountain-jump is boring.  There are three specific coins nobody has thrown back.  I want them.'"
		"puck":                  return "'A prank should feel like a hug that got the timing slightly wrong.  I keep telling this to the newer feys.  They do not listen.'"
		"green_man":             return "'The cotton candy is not really cotton candy.  You already knew that.'"
		"hob_of_the_hedgerow":   return "'The kernel that is the color of blood is dye from a specific brand of cherry filling.  I put it there.  It is a signature.'"
		"pooka":                 return "'The rabbit costume is not a costume.  Please stop asking.'"
		"moth":
			# Hane no Niwa cross-token · the gold feather · a garden
			# across the sea knows the same trade.
			if OneironauticsTokens.has("hnn_gold_feather"):
				return "'I would like to edit one specific detail in your memory of tonight.  You will not notice.  You may thank me later.  There is a garden across the sea that does this with letters instead.  Slower.  Kinder, possibly.  We do not discuss it.'"
			return "'I would like to edit one specific detail in your memory of tonight.  You will not notice.  You may thank me later.'"
		"baobhan_sith":          return "'The kiss cost you a specific dollar.  I have made a specific mental note.  Tomorrow I will spend it on nothing.'"
		"erlking":               return "'I have been running the wheel for four hundred years.  Nobody has landed on Sector 16.  This is because I do not allow it.'"
		"cluricaune":            return "'I am specifically drunk.  I have been drunk since 1691.  The rabbits watch me.  I am fine.'"
		"cu_sith":               return ("'*silence · a specific stare · the green fur ripples · the stare continues*'")
		"herne_the_hunter":      return "'The stag was me.  The man is me.  I have been both.  Both is easier.'"
		"morgan_le_fey":         return "'The cards told me you would end up here.  I told the cards to shut up.  They shut up.  Now we are here.'"
		"leanan_sidhe":          return "'I have been humming your song under my breath since the road here.  You have not asked why.  Ask.'"
		"sycorax":               return "'The mark on my forearm is a specific mark for a specific thing.  I would put it on you but you are not ready.  I will know when you are.'"
		"caliban":               return "'The cage is a specific comfort.  Do not free me.  I know that is a specific hard sentence to hear.  I will explain if you sit for the specific length of time.'"
		"jenny_greenteeth":      return "'The pond has three specific children in it who have been there a specific long time.  They are happy.  I check.'"
		"weird_sister_first":    return "'The other two are inside the cauldron right now.  It works.  Do not ask.'"
		"hamlets_ghost":         return "'The whole play is one specific line long, if you cut everything else.  I will tell you the line when it is dark.'"
		"kitsune":               return "'Nine tails today.  Three tails on Night 1.  The math is real.  You should be worried.'"
		"merrow":                return "'The tank is not for me.  It is for the tourists.  I could leave.  I will not.  Yet.'"
		"dryad":                 return "'I have been in the moss grove for four hundred years.  You are the first person to walk in without stepping on the moss.  Thank you.'"
		"titania":               return "'The seventh night of every specific run I write a new play for you.  I have already started this one.  It is longer than the last.'"
		"oberon":                return "'You have not seen the whole court yet.  The whole court is watching you.  Neither of these facts is a threat.'"
		"selkie":                return "'The coat is where I said it was.  I have not gone home in nine years.  I will not go home this year either.  I am tired of the sea.'"
		"kelpie":                return "'The radio is playing your song.  It has been playing your song since I met you.  This is not romantic.  This is a specific warning.'"
		"nuckelavee":            return "'*a specific silence · the horse-part shifts · the rider-part shifts · the eye-contact does not break*'"
		"redcap":                return "'The cap is dyed with a specific dye I get from a specific supplier.  I would not tell you what.  I would not tell you why.'"
		"sluagh":                return "'We are the ones who never got in.  We do not want in.  We are watching from a specific distance.  We are not enemies of yours.'"
		"leprechaun":            return "'The pot of gold is a specific rumor I have never denied.  I do not have a pot of gold.  I have a specific specific pension.'"
	return "'*asleep · a specific breath · a small twitch of a specific hand*'"


# Paired lines · what two adjacent-cot feys say to each other.
func _pair_line(a: String, b: String) -> String:
	# Try (a,b) and (b,a)
	var key1: String = a + "|" + b
	var key2: String = b + "|" + a
	var pairs: Dictionary = {
		"ondine|cricket_the_cricket":     "Ondine to Cricket: 'The tickets are getting more selective.  Or the tourists are getting less specific.  Either way.'",
		"cricket_the_cricket|ondine":     "Cricket to Ondine: 'They ARE getting more specific.  I've been paying attention.'",
		"boggart|puck":                   "Boggart to Puck: 'The pranks and the lost-and-found are the same job in different hats.'  Puck: 'They are.'",
		"puck|moth":                      "Puck to Moth: 'You edit them awake.  I edit them dreaming.  We should divide the calendar.'  Moth: 'We already have.'",
		"moth|baobhan_sith":              "Moth to Baobhan: 'You take a dollar per kiss.  I take a memory per edit.  We are two different economies.'  Baobhan: 'Yours is better.'",
		"green_man|dryad":                "Green Man to Dryad: 'How's the moss.'  Dryad: 'The moss is well.'",
		"green_man|herne_the_hunter":     "Green Man to Herne: 'The stag was you.'  Herne: 'It was.'",
		"morgan_le_fey|leanan_sidhe":     "Morgan to Leanan: 'You have been humming their song under your breath since the road here.'  Leanan: 'I have.  I always do.'",
		"caliban|sycorax":                "Caliban to Sycorax: 'Mother.'  Sycorax: 'Son.'  · both are looking away for the specific same reason ·",
		"oberon|titania":                 "Oberon to Titania: 'The play is longer this year.'  Titania: 'It always is.  It always will be.  This is the point.'",
		"kitsune|pooka":                  "Kitsune to Pooka: 'The rabbit costume is not a costume.'  Pooka: 'You know I know you know.'",
		"jenny_greenteeth|kelpie":        "Jenny to the Kelpie: 'How's the pond.'  Kelpie: 'Wet.'",
		"weird_sister_first|hamlets_ghost": "Weird Sister to Hamlet's Ghost: 'You have been rehearsing for four hundred years.'  Ghost: 'I have.'",
		"cluricaune|leprechaun":          "Cluricaune to Leprechaun: 'The pension is going to run out.'  Leprechaun: 'It is not.  We have negotiated.  Do not tell.'",
		"erlking|nuckelavee":             "Erlking to Nuckelavee: '*a specific look*'  Nuckelavee: '*the exact same look, returned*'",
		"cu_sith|hob_of_the_hedgerow":    "Cu Sìth to the Hob: '*a specific tail-thump*'  Hob: 'I heard you.'"
	}
	if pairs.has(key1):
		return String(pairs[key1])
	if pairs.has(key2):
		return String(pairs[key2])
	return ""


# ── Compendium view ───────────────────────────────────────────
func _render_compendium_view() -> void:
	_render_sub_view("WRITING DESK · COMPENDIUM", func(v: VBoxContainer) -> void:
		# Ondine's ledger · every promise made this run, and its state.
		var promises: Array = _run_state.get("promises", [])
		if not promises.is_empty():
			var ledger_hdr := Label.new()
			ledger_hdr.text = "· ONDINE'S LEDGER · " + str(promises.size()) + " promise(s) on record ·"
			ledger_hdr.add_theme_font_size_override("font_size", 15)
			ledger_hdr.add_theme_color_override("font_color", C_GOLD)
			v.add_child(ledger_hdr)
			for pr_v in promises:
				var pr: Dictionary = pr_v
				var mark: String = "·"
				if bool(pr.get("resolved", false)):
					mark = "✓" if bool(pr.get("fulfilled", false)) else "○"
				var line := Label.new()
				line.text = "  " + mark + " " + String(pr.get("fey_id", "?")).capitalize() + " · " + String(pr.get("promise", ""))
				line.add_theme_font_size_override("font_size", 13)
				line.add_theme_color_override("font_color", C_CREAM if not bool(pr.get("resolved", false)) else (C_GOLD if bool(pr.get("fulfilled", false)) else C_GOLD_DIM))
				line.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
				v.add_child(line)
			var ledger_note := Label.new()
			ledger_note.text = "  · the ledger is read back on the last night · promises bind you, not your character ·"
			ledger_note.add_theme_font_size_override("font_size", 12)
			ledger_note.add_theme_color_override("font_color", C_GOLD_DIM)
			v.add_child(ledger_note)
			var sep_l := Control.new()
			sep_l.custom_minimum_size = Vector2(0, 10)
			v.add_child(sep_l)
		var recruited: Array = _run_state.get("recruited_feys", [])
		var met: Array = _run_state.get("met_feys", [])

		var by_court := {"seelie": [], "unseelie": [], "wildfey": []}
		for id in _feys_by_id.keys():
			var f: Dictionary = _feys_by_id[String(id)]
			var court: String = String(f.get("court", "wildfey"))
			if not by_court.has(court): continue
			var status: String = "unmet"
			if recruited.has(String(id)): status = "RECRUITED"
			elif met.has(String(id)): status = "met"
			by_court[court].append({"id": String(id), "name": String(f.get("name", id)), "tier": int(f.get("tier", 1)), "status": status})

		for court in ["seelie", "unseelie", "wildfey"]:
			var header := Label.new()
			header.text = "· " + court.to_upper() + " · " + str(by_court[court].size()) + " feys ·"
			header.add_theme_font_size_override("font_size", 16)
			header.add_theme_color_override("font_color", C_LAMP)
			v.add_child(header)
			for f_v in by_court[court]:
				var f: Dictionary = f_v
				var line := Label.new()
				var status_marker: String = "  "
				if f["status"] == "RECRUITED": status_marker = "✓ "
				elif f["status"] == "met": status_marker = "· "
				else: status_marker = "  "
				line.text = "     " + status_marker + "T" + str(f["tier"]) + " · " + f["name"]
				line.add_theme_font_size_override("font_size", 14)
				var col: Color = C_LAMP if f["status"] == "RECRUITED" else (C_CREAM if f["status"] == "met" else C_GOLD_DIM)
				line.add_theme_color_override("font_color", col)
				v.add_child(line)
			var sep := Control.new()
			sep.custom_minimum_size = Vector2(0, 8)
			v.add_child(sep))


# ── Memory mirror view ────────────────────────────────────────
func _render_memory_view() -> void:
	_render_sub_view("MEMORY MIRRORS · six on the wall", func(v: VBoxContainer) -> void:
		var q: Dictionary = _run_state.get("questionnaire", {})
		var lost: int = int(_run_state.get("memories_lost", 0))
		# Fourth column · the blurred paraphrase shown once the mirror
		# cracks (a death spends memories in this exact order; kept in
		# lockstep with FeyFaireHost.MEMORY_SLOTS).
		var slot_map: Array = [
			["bedroom_description", "your bedroom",           "mirror_1_rose_garden", "... a room you used to fall asleep in?  The light came from one side ..."],
			["favorite_song",       "the song you played",    "mirror_2_storm_coast", "... a song you used to hum.  You cannot find the tune now ..."],
			["favorite_meal",       "the meal you enjoyed",   "mirror_3_court_beneath", "... something you ate that you were glad to be eating ..."],
			["holiday",             "the holiday that matters", "mirror_4_the_green", "... a day that came once a year and meant something.  Which day? ..."],
			["parent_argument",     "the argument with a parent", "mirror_5_undertide", "... a voice you raised, or one raised at you.  You cannot hear the words ..."],
			["first_kiss",          "the first kiss",         "mirror_6_dream", "... someone leaned in, once.  You have lost their face ..."],
		]
		var completed: Array = _run_state.get("mirrors_completed", [])
		for i in range(slot_map.size()):
			var key: String = slot_map[i][0]
			var label: String = slot_map[i][1]
			var mirror_id: String = slot_map[i][2]
			var value: String = String(q.get(key, ""))
			var cracked: bool = i < lost
			var done: bool = completed.has(mirror_id)
			var row := ColorRect.new()
			row.color = C_CRACKED if cracked else C_MEMORY
			row.custom_minimum_size = Vector2(0, 76)
			v.add_child(row)
			var vh := VBoxContainer.new()
			vh.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
			vh.offset_left = 10
			vh.offset_right = -10
			vh.offset_top = 4
			vh.offset_bottom = -4
			vh.add_theme_constant_override("separation", 2)
			row.add_child(vh)
			var hdr := Label.new()
			var status: String = ""
			if cracked: status = " · CRACKED"
			elif done:  status = " · WALKED"
			hdr.text = "MIRROR " + str(i + 1) + " · " + label + status
			hdr.add_theme_font_size_override("font_size", 14)
			hdr.add_theme_color_override("font_color", C_BG)
			vh.add_child(hdr)
			var body := Label.new()
			var blur: String = slot_map[i][3] if slot_map[i].size() > 3 else "· ... a specific memory that used to be here ..."
			body.text = value if not cracked else blur
			body.add_theme_font_size_override("font_size", 13)
			body.add_theme_color_override("font_color", C_BG)
			body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			vh.add_child(body)
			if not cracked:
				var enter_btn := Button.new()
				enter_btn.text = "  · step through this mirror ·  " if not done else "  · step through again ·  "
				enter_btn.add_theme_font_size_override("font_size", 14)
				var mid: String = mirror_id
				enter_btn.pressed.connect(func() -> void: enter_mirror.emit(mid))
				vh.add_child(enter_btn))


# ── Prospero wakes · NG+ · one conversation ───────────────────
func _render_prospero_view() -> void:
	_render_sub_view("PROSPERO · AWAKE", func(v: VBoxContainer) -> void:
		var seen: Array = _run_state.get("endings_seen", [])
		var body := RichTextLabel.new()
		body.bbcode_enabled = false
		body.fit_content = true
		body.text = "He is old the way the carousel tune is old.  He pats the blanket for Helia, who is already there.\n\n'Three summers.  Most take one and keep it.  You keep coming back through, wearing new faces, carrying the same pocket.  I ran this Faire for a hundred years before I lay down, and I only ever saw a handful like you.\n\nI am not going to tell you what the Faire is.  You would forget it at the Gate like everyone does.  I will tell you what I know that survives the Gate: the Faire keeps every stub.  Cricket showed you.  The stubs are why the endings you have seen · " + str(seen.size()) + " of them now · lean against each other like books.\n\nHere.  A word.  Not my name · you could not carry my name.  A word to spend.  All three courts honor it once.  Spend it on a night when the choice in front of you is between two things you want.'\n\nHe lies back down.  Helia does not move.  The trailer is quiet in the specific way it was before, except now you know he is only sleeping."
		body.add_theme_font_size_override("normal_font_size", 16)
		body.add_theme_color_override("default_color", C_CREAM)
		body.custom_minimum_size = Vector2(0, 300)
		v.add_child(body)

		var take_btn := Button.new()
		take_btn.text = "  · take the word ·  "
		take_btn.add_theme_font_size_override("font_size", 16)
		take_btn.add_theme_color_override("font_color", C_GOLD)
		take_btn.pressed.connect(func() -> void:
			_run_state["prospero_woke"] = true
			var kp: Array = _run_state.get("keepsakes", [])
			if not kp.has("prosperos_word"):
				kp.append("prosperos_word")
			_run_state["keepsakes"] = kp
			_run_state["court_seelie"] = int(_run_state.get("court_seelie", 0)) + 1
			_run_state["court_unseelie"] = int(_run_state.get("court_unseelie", 0)) + 1
			_run_state["court_wildfey"] = int(_run_state.get("court_wildfey", 0)) + 1
			var sfx := get_node_or_null("/root/SFXBank")
			if sfx: sfx.play("unlock_chime", 0.7)
			_render_main_view()
		)
		v.add_child(take_btn))


# ── Helia view · disposition indicator ────────────────────────
func _render_helia_view() -> void:
	_render_sub_view("HELIA · THE CAT", func(v: VBoxContainer) -> void:
		var recruited: Array = _run_state.get("recruited_feys", [])
		var intro := Label.new()
		intro.text = "Prospero's cat.  She never lets herself be petted.\n\nHer tail-flick indicates how each recruited fey feels about you:"
		intro.add_theme_font_size_override("font_size", 14)
		intro.add_theme_color_override("font_color", C_CREAM)
		intro.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		v.add_child(intro)

		var sep := Control.new()
		sep.custom_minimum_size = Vector2(0, 12)
		v.add_child(sep)

		if recruited.is_empty():
			var empty := Label.new()
			empty.text = "· no recruits to indicate ·  Helia is asleep on the writing desk ·"
			empty.add_theme_font_size_override("font_size", 14)
			empty.add_theme_color_override("font_color", C_GOLD_DIM)
			v.add_child(empty)
			return

		for id in recruited:
			var fey: Dictionary = _feys_by_id.get(String(id), {})
			if fey.is_empty(): continue
			var disp: int = int(_run_state.get(String(id) + "_disposition", 0))
			var flick: String = _tail_flick_for(disp)
			var row := Label.new()
			row.text = "· " + String(fey.get("name", id)) + " · " + flick
			row.add_theme_font_size_override("font_size", 15)
			row.add_theme_color_override("font_color", _tail_flick_color(disp))
			v.add_child(row))


func _tail_flick_for(disp: int) -> String:
	if disp >= 4:  return "tail slow left-to-right · fey LOVED"
	elif disp >= 1:return "tail still · fey LIKED"
	elif disp >= -1:return "tail still · fey NEUTRAL"
	elif disp >= -3:return "tail twitching · fey WARY"
	else:          return "cat hisses · fey HATED"


func _tail_flick_color(disp: int) -> Color:
	if disp >= 4:  return C_LAMP
	elif disp >= 1:return C_CREAM
	elif disp >= -1:return C_GOLD_DIM
	elif disp >= -3:return C_ROSE
	else:          return Color(0.75, 0.25, 0.25, 1.0)


# ── Sub-view frame helper ─────────────────────────────────────
# ─── BOONS · what the roster grants · reasons to hold each fey ───

func _add_boons_readout(v: VBoxContainer) -> void:
	var hdr := Label.new()
	hdr.text = "BOONS · what your party grants:"
	hdr.add_theme_font_size_override("font_size", 13)
	hdr.add_theme_color_override("font_color", C_LAMP)
	v.add_child(hdr)
	var courts := _party_courts()
	var types := _party_damage_types()
	var boons: Array = []
	if courts.has("seelie"):
		boons.append("· a seelie in the party haggles the stalls · OFFER costs 1 less gold")
	if courts.has("unseelie"):
		boons.append("· an unseelie vouches · once a night a named great one submits instead of fighting")
	if courts.has("wildfey"):
		boons.append("· a wildfey knows the ways · once a night one closed flap opens anyway")
	if types.has("song"):
		boons.append("· a song-fey hums you the scansion · one failed RECITE may be re-tried")
	var covered: Array = []
	for t in ["iron", "salt", "flame", "song", "bone", "word"]:
		if types.has(t):
			covered.append(t)
	if not covered.is_empty():
		boons.append("· combat SECOND can strike: " + ", ".join(covered))
	if boons.is_empty():
		boons.append("· no boons yet · recruit feys and the party starts doing things for you")
	for b in boons:
		var lbl := Label.new()
		lbl.text = String(b)
		lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		lbl.add_theme_font_size_override("font_size", 12)
		lbl.add_theme_color_override("font_color", C_RECRUITED if not String(b).begins_with("· no boons") else C_GOLD_DIM)
		v.add_child(lbl)


# ─── THE WARREN · errands · a purpose for all 101 feys ───────────

func _party_courts() -> Dictionary:
	var out := {}
	for fid_v in _run_state.get("recruited_feys", []):
		var f: Dictionary = _feys_by_id.get(String(fid_v), {})
		out[String(f.get("court", ""))] = true
	return out


func _party_damage_types() -> Dictionary:
	var out := {}
	for fid_v in _run_state.get("recruited_feys", []):
		var f: Dictionary = _feys_by_id.get(String(fid_v), {})
		out[String(f.get("damage_type", ""))] = true
	return out


func _errand_available(e: Dictionary) -> bool:
	# The target isn't recruited yet, and the party holds one of the
	# target's own kind (giver_court) to vouch it out.
	var recruited: Array = _run_state.get("recruited_feys", [])
	if recruited.has(String(e.get("target", ""))):
		return false
	return _party_courts().has(String(e.get("giver_court", "")))


func _errand_need_met(e: Dictionary) -> bool:
	var need: Dictionary = e.get("needs", {})
	if need.has("damage_type"):
		return _party_damage_types().has(String(need["damage_type"]))
	if need.has("court_not"):
		# Any party fey of a DIFFERENT court than the forbidden one.
		for c in _party_courts().keys():
			if String(c) != String(need["court_not"]) and String(c) != "":
				return true
		return false
	return true


func _qualifying_fey(e: Dictionary) -> String:
	# The party fey who satisfies the need · the one "sent."
	var need: Dictionary = e.get("needs", {})
	for fid_v in _run_state.get("recruited_feys", []):
		var f: Dictionary = _feys_by_id.get(String(fid_v), {})
		if need.has("damage_type") and String(f.get("damage_type", "")) == String(need["damage_type"]):
			return String(fid_v)
		if need.has("court_not") and String(f.get("court", "")) != String(need["court_not"]):
			return String(fid_v)
	return ""


func _warren_summary_string() -> String:
	var recruited: Array = _run_state.get("recruited_feys", [])
	var total := _errands.size()
	var done := 0
	var avail := 0
	for e_v in _errands:
		var e: Dictionary = e_v
		if recruited.has(String(e.get("target", ""))):
			done += 1
		elif _errand_available(e):
			avail += 1
	return "%d of %d reached · %d ready to run" % [done, total, avail]


func _render_warren_view() -> void:
	_render_sub_view("THE WARREN · errands beyond the fence", func(v: VBoxContainer) -> void:
		var note := Label.new()
		note.text = "Feys out past the string-lights. One of your own vouches you in; to walk to a fey you bring the thing it respects. Reaching one recruits it — and it vouches for the next."
		note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		note.add_theme_font_size_override("font_size", 13)
		note.add_theme_color_override("font_color", C_GOLD_DIM)
		v.add_child(note)
		var recruited: Array = _run_state.get("recruited_feys", [])
		var any_shown := false
		for e_v in _errands:
			var e: Dictionary = e_v
			var tid := String(e.get("target", ""))
			if recruited.has(tid):
				continue          # already brought in
			if not _errand_available(e):
				continue          # no voucher of that court in the party yet
			any_shown = true
			_add_errand_row(v, e)
		if not any_shown:
			var empty := Label.new()
			var all_done := true
			for e2_v in _errands:
				if not recruited.has(String((e2_v as Dictionary).get("target", ""))):
					all_done = false
					break
			empty.text = "The warren is empty. Every fey beyond the fence has come in." if all_done \
				else "No errands yet. Recruit a fey on the midway first — its kind will vouch the next one out."
			empty.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			empty.add_theme_font_size_override("font_size", 14)
			empty.add_theme_color_override("font_color", C_CREAM)
			v.add_child(empty)
	)


func _add_errand_row(parent: Node, e: Dictionary) -> void:
	var tid := String(e.get("target", ""))
	var fey: Dictionary = _feys_by_id.get(tid, {})
	var cell := ColorRect.new()
	cell.color = C_WOOD_HI
	cell.custom_minimum_size = Vector2(0, 96)
	parent.add_child(cell)
	var col := VBoxContainer.new()
	col.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	col.offset_left = 10
	col.offset_right = -10
	col.offset_top = 6
	col.offset_bottom = -6
	col.add_theme_constant_override("separation", 2)
	cell.add_child(col)
	var name_lbl := Label.new()
	name_lbl.text = "· %s · %s · tier %d" % [String(fey.get("name", tid)),
		String(fey.get("court", "?")), int(fey.get("tier", 1))]
	name_lbl.add_theme_font_size_override("font_size", 15)
	name_lbl.add_theme_color_override("font_color", C_LAMP)
	col.add_child(name_lbl)
	var hook_lbl := Label.new()
	# The card is composed from the target's OWN manifestation + the
	# authored hook. Short manifestation (first clause).
	var manif := String(fey.get("manifestation", ""))
	var idx := manif.find("  ")
	if idx < 0:
		idx = manif.find(".")
	var manif_short := manif.substr(0, idx) if idx > 0 else manif.substr(0, min(70, manif.length()))
	hook_lbl.text = "%s  (%s)" % [String(e.get("hook", "")), manif_short]
	hook_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	hook_lbl.add_theme_font_size_override("font_size", 12)
	hook_lbl.add_theme_color_override("font_color", C_CREAM)
	col.add_child(hook_lbl)
	var need_row := HBoxContainer.new()
	need_row.add_theme_constant_override("separation", 10)
	col.add_child(need_row)
	var met := _errand_need_met(e)
	var need_lbl := Label.new()
	need_lbl.text = "· %s" % String(e.get("needs_line", "bring the right kin"))
	need_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	need_lbl.add_theme_font_size_override("font_size", 12)
	need_lbl.add_theme_color_override("font_color", C_RECRUITED if met else C_GOLD_DIM)
	need_row.add_child(need_lbl)
	var run_btn := Button.new()
	run_btn.text = "  send %s  " % String(_feys_by_id.get(_qualifying_fey(e), {}).get("name", "them")) if met else "  can't yet  "
	run_btn.add_theme_font_size_override("font_size", 12)
	run_btn.disabled = not met
	if met:
		run_btn.pressed.connect(_run_errand.bind(e))
	need_row.add_child(run_btn)


func _run_errand(e: Dictionary) -> void:
	var tid := String(e.get("target", ""))
	var fey: Dictionary = _feys_by_id.get(tid, {})
	var sent := _qualifying_fey(e)
	var sent_name := String(_feys_by_id.get(sent, {}).get("name", "your ally"))
	# Recruit the target · same mutation shape as a booth recruit.
	var recruited: Array = _run_state.get("recruited_feys", [])
	if not recruited.has(tid):
		recruited.append(tid)
	_run_state["recruited_feys"] = recruited
	var court := String(fey.get("court", "wildfey"))
	var court_key := "court_" + court
	_run_state[court_key] = int(_run_state.get(court_key, 0)) + 2
	_run_state[tid + "_disposition"] = int(_run_state.get(tid + "_disposition", 0)) + 2
	_run_state["fey_court_" + tid] = court
	var met: Array = _run_state.get("met_feys", [])
	if not met.has(tid):
		met.append(tid)
	_run_state["met_feys"] = met
	# Milestone tokens.
	OneironauticsTokens.add("fey_faire_errand_first")
	_check_warren_milestones()
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("win_chord", 0.6)
	request_save.emit()
	# Confirm screen · the fey's own request lands as the promise made.
	_render_sub_view("· %s comes in ·" % String(fey.get("name", tid)), func(v: VBoxContainer) -> void:
		var body := Label.new()
		body.text = "%s walked you out past the fence and vouched. %s asks one thing, the way its kind does:\n\n\"%s\"\n\nYou said yes. %s joins the party." % [
			sent_name, String(fey.get("name", tid)),
			String(fey.get("request", "nothing you can't give")),
			String(fey.get("name", tid))]
		body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		body.add_theme_font_size_override("font_size", 14)
		body.add_theme_color_override("font_color", C_CREAM)
		v.add_child(body)
		# The request becomes a promise on Ondine's ledger, honestly.
		var promises: Array = _run_state.get("promises", [])
		promises.append({"fey_id": tid, "promise": String(fey.get("request", "")), "resolved": false})
		_run_state["promises"] = promises
		var back := Button.new()
		back.text = "  · back to the warren ·  "
		back.add_theme_font_size_override("font_size", 14)
		back.pressed.connect(_render_warren_view)
		v.add_child(back)
	)


func _check_warren_milestones() -> void:
	var recruited: Array = _run_state.get("recruited_feys", [])
	# Per-court emptied.
	for court in ["seelie", "unseelie", "wildfey"]:
		var court_targets := 0
		var court_done := 0
		for e_v in _errands:
			var e: Dictionary = e_v
			if String(e.get("giver_court", "")) == court:
				court_targets += 1
				if recruited.has(String(e.get("target", ""))):
					court_done += 1
		if court_targets > 0 and court_done == court_targets:
			OneironauticsTokens.add("fey_faire_warren_court_" + court)
	# All errands done.
	var all_done := true
	for e2_v in _errands:
		if not recruited.has(String((e2_v as Dictionary).get("target", ""))):
			all_done = false
			break
	if all_done:
		OneironauticsTokens.add("fey_faire_warren_emptied")


func _render_sub_view(title: String, populator: Callable) -> void:
	_clear_panel()
	_panel_root = Control.new()
	_panel_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_panel_root.offset_top = 60
	_panel_root.offset_bottom = -20
	_panel_root.offset_left = 60
	_panel_root.offset_right = -60
	add_child(_panel_root)

	var bg := ColorRect.new()
	bg.color = C_WOOD
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_panel_root.add_child(bg)

	var header_row := HBoxContainer.new()
	header_row.set_anchors_preset(Control.PRESET_TOP_WIDE)
	header_row.offset_left = 12
	header_row.offset_right = -12
	header_row.offset_top = 8
	header_row.offset_bottom = 32
	_panel_root.add_child(header_row)

	var title_lbl := Label.new()
	title_lbl.text = "· " + title + " ·"
	title_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	title_lbl.add_theme_font_size_override("font_size", 17)
	title_lbl.add_theme_color_override("font_color", C_LAMP)
	header_row.add_child(title_lbl)

	var back_btn := Button.new()
	back_btn.text = "  ← back to trailer  "
	back_btn.add_theme_font_size_override("font_size", 14)
	back_btn.pressed.connect(_render_main_view)
	header_row.add_child(back_btn)

	var scroll := ScrollContainer.new()
	scroll.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scroll.offset_top = 40
	scroll.offset_bottom = -12
	scroll.offset_left = 12
	scroll.offset_right = -12
	_panel_root.add_child(scroll)

	var v := VBoxContainer.new()
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	v.add_theme_constant_override("separation", 6)
	scroll.add_child(v)

	populator.call(v)


func _on_back() -> void:
	quit.emit()


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			_on_back()
			get_viewport().set_input_as_handled()
