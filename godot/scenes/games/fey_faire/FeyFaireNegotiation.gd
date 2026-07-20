extends Control
## Fey Faire · negotiation scene · data-driven for any fey.
##
## boot(state) requires state to include:
##   fey_id · id of the fey being negotiated with (must exist in
##            feys.json)
##   run_state · full host run state (recruits, keepsakes, quotes,
##               promises, court alignments · used for gating and
##               success rolls)
##
## Renders the fey's manifestation, portrait placeholder, and four
## negotiation branches: OFFER · PROMISE · THREATEN · RECITE.  Each
## opens a specific sub-panel with the fey's own data pulled from
## feys.json.
##
## Emits:
##   negotiation_complete(fey_id, outcome, mutations)
##     outcome · one of "recruited" | "rebuffed" | "hostile"
##     mutations · Dictionary of state changes to merge into
##                 run_state (recruits, court shifts, promises, etc.)
##   quit_to_shelf · escape hatch (BACK)
##
## F4-compliant via add_to_group("ui").

signal negotiation_complete(fey_id: String, outcome: String, mutations: Dictionary)
signal quit_to_shelf

const FEYS_PATH := "res://resources/games/vol7/fey_faire/feys.json"
const QUOTES_PATH := "res://resources/games/vol7/fey_faire/quotes.json"

# Rocha palette
const C_BG        := Color(0.157, 0.094, 0.173, 1.0)
const C_PANEL     := Color(0.455, 0.157, 0.282, 1.0)
const C_PANEL_DIM := Color(0.28, 0.10, 0.18, 1.0)
const C_CREAM     := Color(0.957, 0.878, 0.816, 1.0)
const C_ROSE      := Color(0.878, 0.722, 0.753, 1.0)
const C_MAUVE     := Color(0.87, 0.68, 0.76, 1.0)
const C_GOLD      := Color(0.973, 0.784, 0.282, 1.0)
const C_GOLD_DIM  := Color(0.72, 0.52, 0.26, 1.0)

# Court accent colors
const C_COURT_SEELIE   := Color(0.973, 0.784, 0.282, 1.0)
const C_COURT_UNSEELIE := Color(0.72, 0.52, 0.26, 1.0)
const C_COURT_WILDFEY  := Color(0.62, 0.82, 0.55, 1.0)

var _run_state: Dictionary = {}
var _fey_id: String = ""
var _fey: Dictionary = {}
var _feys_by_id: Dictionary = {}
var _quotes_by_id: Dictionary = {}
var _mutations: Dictionary = {}
var _panel_root: Control = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")


func boot(state: Dictionary) -> void:
	_run_state = state.get("run_state", state)
	_fey_id = String(state.get("fey_id", ""))
	_run_state.erase("_recite_retry_used")   # fresh RECITE retry per encounter
	_load_feys()
	_load_quotes()
	_fey = _feys_by_id.get(_fey_id, {})
	if _fey.is_empty():
		push_warning("[FeyFaireNegotiation] unknown fey_id: " + _fey_id)
		# Fall back to the first fey · scaffold safety
		if not _feys_by_id.is_empty():
			var keys := _feys_by_id.keys()
			_fey_id = String(keys[0])
			_fey = _feys_by_id[_fey_id]
	_build_frame()
	_render_main_view()


func _load_feys() -> void:
	if not FileAccess.file_exists(FEYS_PATH): return
	var f := FileAccess.open(FEYS_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		var feys_arr: Array = (parsed as Dictionary).get("feys", [])
		for entry_v in feys_arr:
			var entry: Dictionary = entry_v
			_feys_by_id[String(entry.get("id", ""))] = entry


func _load_quotes() -> void:
	if not FileAccess.file_exists(QUOTES_PATH): return
	var f := FileAccess.open(QUOTES_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		var arr: Array = (parsed as Dictionary).get("quotes", [])
		for q_v in arr:
			var q: Dictionary = q_v
			_quotes_by_id[String(q.get("id", ""))] = q


func _build_frame() -> void:
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# Top header: fey name + court
	var court := _fey_str("court", "wildfey")
	var court_color: Color = _court_color(court)

	var header_panel := ColorRect.new()
	header_panel.color = C_PANEL_DIM
	header_panel.set_anchors_preset(Control.PRESET_TOP_WIDE)
	header_panel.offset_top = 20
	header_panel.offset_bottom = 68
	add_child(header_panel)

	var header_label := Label.new()
	header_label.text = "· " + _fey_str("name", "?").to_upper() + " ·  " + court.to_upper() + " ·  TIER " + str(int(_fey.get("tier", 1)))
	header_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header_label.add_theme_font_size_override("font_size", 18)
	header_label.add_theme_color_override("font_color", court_color)
	header_label.set_anchors_preset(Control.PRESET_TOP_WIDE)
	header_label.offset_top = 32
	header_label.offset_bottom = 56
	add_child(header_label)


func _court_color(court: String) -> Color:
	match court:
		"seelie":   return C_COURT_SEELIE
		"unseelie": return C_COURT_UNSEELIE
		"wildfey":  return C_COURT_WILDFEY
		_: return C_GOLD


func _clear_panel() -> void:
	if _panel_root != null and is_instance_valid(_panel_root):
		_panel_root.queue_free()
	_panel_root = null


func _render_main_view() -> void:
	_clear_panel()
	_panel_root = Control.new()
	_panel_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_panel_root.offset_top = 80
	_panel_root.offset_bottom = -20
	_panel_root.offset_left = 40
	_panel_root.offset_right = -40
	add_child(_panel_root)

	# Two-column layout · left panel = manifestation description ·
	# right panel = negotiation options
	var h := HBoxContainer.new()
	h.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	h.add_theme_constant_override("separation", 20)
	_panel_root.add_child(h)

	# LEFT · description
	var left := VBoxContainer.new()
	left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	left.add_theme_constant_override("separation", 8)
	h.add_child(left)

	var manif_panel := ColorRect.new()
	manif_panel.color = C_PANEL
	manif_panel.custom_minimum_size = Vector2(0, 4)
	manif_panel.size_flags_vertical = Control.SIZE_EXPAND_FILL
	left.add_child(manif_panel)

	var left_content := VBoxContainer.new()
	left_content.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	left_content.offset_left = 12
	left_content.offset_right = -12
	left_content.offset_top = 12
	left_content.offset_bottom = -12
	left_content.add_theme_constant_override("separation", 6)
	manif_panel.add_child(left_content)

	# Portrait · procedural from court/tier/id · authored override wins
	var portrait_row := HBoxContainer.new()
	portrait_row.add_theme_constant_override("separation", 10)
	left_content.add_child(portrait_row)

	var portrait_rect := TextureRect.new()
	portrait_rect.texture = FeyPortrait.texture(_fey, Vector2i(96, 120))
	portrait_rect.custom_minimum_size = Vector2(96, 120)
	portrait_rect.stretch_mode = TextureRect.STRETCH_KEEP
	portrait_row.add_child(portrait_rect)

	var portrait_caption := Label.new()
	portrait_caption.text = "· as they choose\n  to be seen ·"
	portrait_caption.add_theme_font_size_override("font_size", 13)
	portrait_caption.add_theme_color_override("font_color", C_GOLD_DIM)
	portrait_row.add_child(portrait_caption)

	var manif_header := Label.new()
	manif_header.text = "MANIFESTATION"
	manif_header.add_theme_font_size_override("font_size", 14)
	manif_header.add_theme_color_override("font_color", C_GOLD_DIM)
	left_content.add_child(manif_header)

	var manif_text := RichTextLabel.new()
	manif_text.bbcode_enabled = false
	manif_text.fit_content = true
	manif_text.text = _fey_str("manifestation", "")
	manif_text.add_theme_font_size_override("normal_font_size", 15)
	manif_text.add_theme_color_override("default_color", C_CREAM)
	manif_text.custom_minimum_size = Vector2(0, 100)
	left_content.add_child(manif_text)

	var sep1 := Control.new()
	sep1.custom_minimum_size = Vector2(0, 6)
	left_content.add_child(sep1)

	var true_form_header := Label.new()
	true_form_header.text = "· if the glamour drops ·"
	true_form_header.add_theme_font_size_override("font_size", 14)
	true_form_header.add_theme_color_override("font_color", C_GOLD_DIM)
	left_content.add_child(true_form_header)

	var true_form_text := RichTextLabel.new()
	true_form_text.bbcode_enabled = false
	true_form_text.fit_content = true
	true_form_text.text = _fey_str("true_form", "")
	true_form_text.add_theme_font_size_override("normal_font_size", 14)
	true_form_text.add_theme_color_override("default_color", C_ROSE)
	true_form_text.custom_minimum_size = Vector2(0, 60)
	left_content.add_child(true_form_text)

	var sep2 := Control.new()
	sep2.custom_minimum_size = Vector2(0, 6)
	left_content.add_child(sep2)

	var desc_header := Label.new()
	desc_header.text = "· disposition ·"
	desc_header.add_theme_font_size_override("font_size", 14)
	desc_header.add_theme_color_override("font_color", C_GOLD_DIM)
	left_content.add_child(desc_header)

	var desc_text := RichTextLabel.new()
	desc_text.bbcode_enabled = false
	desc_text.fit_content = true
	desc_text.text = _fey_str("description", "")
	desc_text.add_theme_font_size_override("normal_font_size", 14)
	desc_text.add_theme_color_override("default_color", C_MAUVE)
	desc_text.custom_minimum_size = Vector2(0, 60)
	left_content.add_child(desc_text)

	# Combat quick-stats footer
	var stats: Dictionary = _fey.get("stats", {})
	var stats_lbl := Label.new()
	stats_lbl.text = "HP %s · SP %s · AP %s · speed %s · charm %s · wit %s · damage · %s · weak · %s" % [
		str(int(stats.get("hp", 0))),
		str(int(stats.get("sp", 0))),
		str(int(stats.get("ap", 0))),
		str(int(stats.get("speed", 0))),
		str(int(stats.get("charm", 0))),
		str(int(stats.get("wit", 0))),
		_fey_str("damage_type", "?"),
		_fey_str("weakness", "?")
	]
	stats_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	stats_lbl.add_theme_font_size_override("font_size", 13)
	stats_lbl.add_theme_color_override("font_color", C_ROSE)
	left_content.add_child(stats_lbl)

	# RIGHT · negotiation branches
	var right := VBoxContainer.new()
	right.custom_minimum_size = Vector2(340, 0)
	right.size_flags_horizontal = Control.SIZE_SHRINK_END
	right.add_theme_constant_override("separation", 10)
	h.add_child(right)

	var right_header := Label.new()
	right_header.text = "· FOUR BRANCHES ·"
	right_header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	right_header.add_theme_font_size_override("font_size", 16)
	right_header.add_theme_color_override("font_color", C_GOLD)
	right.add_child(right_header)

	# Legible tell · what THIS fey actually responds to, read from its
	# court and whether it holds a play. OFFER always recruits but never
	# DELIGHTS — gold is a solvent, not a key. Hitting the real want is
	# what wins full disposition (which the endings gate on). This turns
	# the branch choice from "what can I afford" into "what is this fey."
	# de-domination pass 2026-07.
	var tell := Label.new()
	tell.text = _wants_tell()
	tell.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	tell.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	tell.add_theme_font_size_override("font_size", 13)
	tell.add_theme_color_override("font_color", C_MAUVE)
	right.add_child(tell)

	# Precomputed check · does the player HAVE the specific means
	# to attempt each branch?  Each branch is a different price with
	# a different failure shape · thin-gameplay pass 2026-07.
	var offer_cost := _offer_cost()
	var gold: int = int(_run_state.get("gold", 0))
	var can_offer: bool = gold >= offer_cost
	var outstanding := _outstanding_promises()
	var can_promise: bool = true       # attemptable · they may refuse
	var can_threaten: bool = _player_knows_true_name()
	var mq := _matching_quote()
	var can_recite: bool = not (_run_state.get("unlocked_quotes", []) as Array).is_empty()

	_add_negotiation_button(right, "OFFER",
		"procure " + _fey_str("prize", "their prize") + " · %d gold" % offer_cost
			+ ("" if can_offer else " · you carry %d" % gold),
		can_offer, C_GOLD, _on_offer_pressed)

	_add_negotiation_button(right, "PROMISE",
		_fey_str("request", "")
			+ ("" if outstanding == 0 else " · %d already outstanding" % outstanding),
		can_promise, C_ROSE, _on_promise_pressed)

	_add_negotiation_button(right, "THREATEN",
		"invoke their true name" + (" · tier %d · they will not kneel" % int(_fey.get("tier", 1))
			if int(_fey.get("tier", 1)) >= 3 and can_threaten else ""),
		can_threaten, C_GOLD_DIM, _on_threaten_pressed)

	_add_negotiation_button(right, "RECITE",
		("you hold their line · " + String(mq.get("play", "")) if not mq.is_empty()
			else "quote " + _fey_str("favorite_play", "the right play") + " · you hold no matching line"),
		can_recite, C_MAUVE, _on_recite_pressed)

	var sep3 := Control.new()
	sep3.custom_minimum_size = Vector2(0, 20)
	right.add_child(sep3)

	# Walk away / fight
	var walk := Button.new()
	walk.text = "  walk away  "
	walk.add_theme_font_size_override("font_size", 15)
	walk.pressed.connect(_on_walk_away)
	right.add_child(walk)

	var fight := Button.new()
	fight.text = "  fight instead  "
	fight.add_theme_font_size_override("font_size", 15)
	fight.pressed.connect(_on_fight_pressed)
	right.add_child(fight)

	var back := Button.new()
	back.text = "  ← back to shelf  "
	back.add_theme_font_size_override("font_size", 15)
	back.pressed.connect(_on_back)
	right.add_child(back)


func _add_negotiation_button(parent: Node, action: String, subtitle: String, enabled: bool, color: Color, callback: Callable) -> void:
	var container := VBoxContainer.new()
	container.add_theme_constant_override("separation", 2)
	parent.add_child(container)

	var btn := Button.new()
	btn.text = "  " + action + "  "
	btn.add_theme_font_size_override("font_size", 16)
	btn.add_theme_color_override("font_color", color if enabled else C_PANEL_DIM)
	btn.disabled = not enabled
	btn.pressed.connect(callback)
	container.add_child(btn)

	var subtitle_lbl := Label.new()
	subtitle_lbl.text = "  · " + subtitle + " ·  " + ("" if enabled else "(unavailable)")
	subtitle_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	subtitle_lbl.add_theme_font_size_override("font_size", 13)
	subtitle_lbl.add_theme_color_override("font_color", C_CREAM if enabled else C_PANEL_DIM)
	container.add_child(subtitle_lbl)


func _player_knows_true_name() -> bool:
	# The Host writes known_true_names (Bookstall slim volume, fortune
	# beats, other feys) · this read matched a key nobody wrote and
	# THREATEN was dead code for a whole build.
	var known: Array = _run_state.get("known_true_names", [])
	return known.has(_fey_id)


func _offer_cost() -> int:
	# You procure the fey's exact prize on the midway before the
	# offer · the Faire sells everything, at Faire prices. A seelie
	# in the party haggles it down (Warren boon).
	var cost := 1 + int(_fey.get("tier", 1))
	if _party_has_court("seelie"):
		cost = maxi(1, cost - 1)
	return cost


# ─── Warren party boons ──────────────────────────────────────────

func _party_has_court(court: String) -> bool:
	for fid_v in _run_state.get("recruited_feys", []):
		if String(_feys_by_id.get(String(fid_v), {}).get("court", "")) == court:
			return true
	return false


func _party_has_song() -> bool:
	for fid_v in _run_state.get("recruited_feys", []):
		if String(_feys_by_id.get(String(fid_v), {}).get("damage_type", "")) == "song":
			return true
	return false


func _unseelie_vouch_ready() -> bool:
	# Once per night, an unseelie steps between you and a great one.
	if not _party_has_court("unseelie"):
		return false
	return int(_run_state.get("unseelie_vouch_night", -1)) != int(_run_state.get("night", 1))


func _outstanding_promises() -> int:
	var n := 0
	for p_v in _run_state.get("promises", []):
		var p: Dictionary = p_v
		if not bool(p.get("fulfilled", false)):
			n += 1
	return n


func _matching_quote() -> Dictionary:
	# A quote matches if its play is the fey's favorite, or its
	# affinities name the fey or their court.
	var fav := _fey_str("favorite_play", "")
	var court := _fey_str("court", "")
	for qid_v in _run_state.get("unlocked_quotes", []):
		var q: Dictionary = _quotes_by_id.get(String(qid_v), {})
		if q.is_empty():
			continue
		if fav != "" and String(q.get("play", "")) == fav:
			return q
		var aff: Array = q.get("affinities", [])
		if aff.has(_fey_id) or (court != "" and aff.has(court)):
			return q
	return {}


# ── What this fey actually wants (de-domination) ─────────────────
# Each fey has a single branch that DELIGHTS it — hitting it wins
# full disposition; OFFER (or any mismatch) still recruits but coolly,
# at reduced disposition. OFFER is never a want, so gold stops being a
# universal solvent. The want is DERIVED from data every fey already
# carries (court + whether it holds a play), with a curated override
# hatch for feys whose character reads against the derivation. This
# mirrors the visitor-portrait look table: derive by default, override
# the marquee cases. Endings gate on per-fey disposition, so the
# gradient has teeth.
const _WANTS_OVERRIDE: Dictionary = {
	# id → "RECITE" | "PROMISE" | "THREATEN". Empty by default; the
	# derivation below is characterful because favorite_play already
	# routes the literary feys to RECITE. Add rows only where a fey's
	# character contradicts its court/play.
}


func _fey_wants() -> String:
	if _WANTS_OVERRIDE.has(_fey_id):
		return String(_WANTS_OVERRIDE[_fey_id])
	var fav := _fey_str("favorite_play", "")
	var has_play: bool = fav != "" and fav != "None"
	if has_play:
		return "RECITE"          # the literary ones want their own line
	var tier: int = int(_fey.get("tier", 1))
	if tier >= 3:
		return "PROMISE"         # great ones won't be bought or bossed
	match _fey_str("court", "wildfey"):
		"seelie":   return "PROMISE"   # courtly — a bond binds them
		"unseelie": return "THREATEN"  # they wait to be called by name
		_:          return "PROMISE"   # wildfey take a bargain


func _wants_tell() -> String:
	match _fey_wants():
		"RECITE":
			return "· it holds a play close · win it with the right line, not coin ·"
		"THREATEN":
			return "· it is waiting to be called by its true name ·"
		_:
			return "· it wants a promise it can hold you to, not coin ·"


func _on_offer_pressed() -> void:
	_render_offer_view()


func _on_promise_pressed() -> void:
	_render_promise_view()


func _on_threaten_pressed() -> void:
	_render_threaten_view()


func _on_recite_pressed() -> void:
	_render_recite_view()


func _render_offer_view() -> void:
	var cost := _offer_cost()
	_render_branch_view(
		"OFFER",
		"You spend the evening finding " + _fey_str("prize", "their prize")
			+ " among the stalls · %d gold · and bring it to " % cost
			+ _fey_str("name", "the fey") + ".",
		"the exact prize, exactly procured · the Faire sells everything, at Faire prices",
		func() -> void:
			if int(_run_state.get("gold", 0)) < cost:
				_rebuff("OFFER · your purse came up short at the last stall", {"lock_booth": true})
				return
			_succeed_recruit("OFFER", {"gold_delta": -cost})
	)


func _render_promise_view() -> void:
	var outstanding := _outstanding_promises()
	_render_branch_view(
		"PROMISE",
		"You promise: " + _fey_str("request", "a service"),
		("a fulfilled promise recruits · an unkept one costs you later" if outstanding < 3
			else "you already owe three · fey can read a ledger from across a booth"),
		func() -> void:
			# A fey weighs your record before your words.  Three or
			# more outstanding promises and they refuse outright.
			if _outstanding_promises() >= 3:
				_rebuff("PROMISE · they look at you the way a bank looks at a fourth loan"
					+ " · keep one of the three you owe, then come back",
					{"lock_booth": true})
				return
			_succeed_recruit("PROMISE", {"promise_made": _fey_str("request", "")})
	)


func _render_threaten_view() -> void:
	var tier: int = int(_fey.get("tier", 1))
	_render_branch_view(
		"THREATEN",
		"You speak the true name: '" + _fey_str("true_name", "?") + "'",
		("the fey stiffens.  the name is powerful." if tier < 3
			else "the name is powerful · and so are they.  names start fights at this tier."),
		func() -> void:
			# The great ones (tier 3 · Titania, Oberon, Mab, Hecate...)
			# answer their name with violence · the organic door into
			# combat.  Lesser feys submit, resentful, and the submission
			# is an UNSEELIE act whoever you took.
			if tier >= 3:
				# Warren boon · an unseelie in the party steps between
				# you and the great one, once a night, and it submits
				# instead of fighting.
				if _unseelie_vouch_ready():
					_run_state["unseelie_vouch_night"] = int(_run_state.get("night", 1))
					var sfx2 := get_node_or_null("/root/SFXBank")
					if sfx2: sfx2.play("win_chord", 0.6)
					_render_result_view(
						_fey_str("name", "?") + " · VOUCHED",
						"You speak the name — and one of yours, an unseelie, steps out of your shadow and speaks a name of THEIRS, quietly, first.\n\nThe great one reconsiders the fight it was about to start.  It comes with you instead, on your friend's word, watching that friend the whole way.",
						C_COURT_UNSEELIE,
						func() -> void: _succeed_recruit("THREATEN", {"disposition_delta": -1}, "unseelie")
					)
					return
				var sfx := get_node_or_null("/root/SFXBank")
				if sfx: sfx.play("loss_thud", 0.7)
				_render_result_view(
					_fey_str("name", "?") + " · THE NAME ANSWERS",
					"You speak it.  The booth-shape drops all at once, like scenery.\n\n· they were waiting to be called by name · they have been waiting a long time ·",
					C_COURT_UNSEELIE,
					func() -> void: negotiation_complete.emit(_fey_id, "hostile", {"combat_pending": true})
				)
				return
			_succeed_recruit("THREATEN", {"disposition_delta": -1}, "unseelie")
	)


func _render_recite_view() -> void:
	var mq := _matching_quote()
	_render_branch_view(
		"RECITE",
		("You recite: \"" + String(mq.get("text", "")) + "\"" if not mq.is_empty()
			else "You recite the nearest line you hold, and hope."),
		("the line is theirs · this is the courteous key" if not mq.is_empty()
			else "warning · nothing you hold matches " + _fey_str("favorite_play", "their play") + " · the wrong play offends"),
		func() -> void:
			if not mq.is_empty():
				_succeed_recruit("RECITE")
			elif _party_has_song() and not bool(_run_state.get("_recite_retry_used", false)):
				# Warren boon · a song-fey hums you the scansion · one
				# retry this negotiation instead of the flap closing.
				_run_state["_recite_retry_used"] = true
				var sfx := get_node_or_null("/root/SFXBank")
				if sfx: sfx.play("page_turn", 0.5)
				_render_result_view(
					_fey_str("name", "?") + " · A SECOND TRY",
					"Wrong play — but a song-fey in your party hums, under the flub, the line you SHOULD have brought.  The fey at the booth tilts its head.  You may try RECITE once more, or choose another branch.",
					C_MAUVE,
					func() -> void: _render_main_view()
				)
			else:
				_rebuff("RECITE · you brought the wrong play · they correct your scansion and pull the flap shut",
					{"lock_booth": true, _fey_id + "_disposition_delta": -1})
	)


func _render_branch_view(title: String, prompt: String, note: String, on_confirm: Callable) -> void:
	_clear_panel()
	_panel_root = Control.new()
	_panel_root.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_panel_root.offset_left = -280
	_panel_root.offset_right = 280
	_panel_root.offset_top = -120
	_panel_root.offset_bottom = 120
	add_child(_panel_root)

	var panel_bg := ColorRect.new()
	panel_bg.color = C_PANEL
	panel_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_panel_root.add_child(panel_bg)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.offset_left = 20
	v.offset_right = -20
	v.offset_top = 20
	v.offset_bottom = -20
	v.add_theme_constant_override("separation", 10)
	_panel_root.add_child(v)

	var title_lbl := Label.new()
	title_lbl.text = "· " + title + " ·"
	title_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title_lbl.add_theme_font_size_override("font_size", 18)
	title_lbl.add_theme_color_override("font_color", C_GOLD)
	v.add_child(title_lbl)

	var prompt_lbl := RichTextLabel.new()
	prompt_lbl.bbcode_enabled = false
	prompt_lbl.fit_content = true
	prompt_lbl.text = prompt
	prompt_lbl.add_theme_font_size_override("normal_font_size", 15)
	prompt_lbl.add_theme_color_override("default_color", C_CREAM)
	prompt_lbl.custom_minimum_size = Vector2(0, 40)
	v.add_child(prompt_lbl)

	var note_lbl := Label.new()
	note_lbl.text = "· " + note + " ·"
	note_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	note_lbl.add_theme_font_size_override("font_size", 13)
	note_lbl.add_theme_color_override("font_color", C_ROSE)
	note_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(note_lbl)

	var buttons := HBoxContainer.new()
	buttons.alignment = BoxContainer.ALIGNMENT_CENTER
	buttons.add_theme_constant_override("separation", 12)
	v.add_child(buttons)

	var confirm_btn := Button.new()
	confirm_btn.text = "  confirm  "
	confirm_btn.add_theme_font_size_override("font_size", 15)
	confirm_btn.pressed.connect(on_confirm)
	buttons.add_child(confirm_btn)

	var back_btn := Button.new()
	back_btn.text = "  ← back  "
	back_btn.add_theme_font_size_override("font_size", 15)
	back_btn.pressed.connect(_render_main_view)
	buttons.add_child(back_btn)


func _succeed_recruit(via: String, extra_mutations: Dictionary = {}, court_override: String = "") -> void:
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("win_chord", 0.7)
	# Compute mutations to send back
	var muts := {
		"recruited_fey_id": _fey_id,
		"via": via,
	}
	# Merge extras
	for k in extra_mutations.keys():
		muts[String(k)] = extra_mutations[k]
	# Compute court shift · +2 seelie/unseelie/wildfey based on this
	# fey's court · a THREATEN submission shifts UNSEELIE regardless
	# of whose name was spoken (the act is the court).
	var court := _fey_str("court", "wildfey")
	var court_key := "court_" + (court_override if court_override != "" else court)
	muts[court_key + "_delta"] = 2
	# Named disposition · recruiting a fey means they like you, but HOW
	# MUCH depends on whether you read them right. The branch that
	# matches their want DELIGHTS them (+3); OFFER or any mismatch still
	# recruits, but coolly (+1). Endings gate on titania/oberon/
	# green_man/cricket dispositions, and Helia's tail-flick reads
	# per-fey disposition · so the gradient is felt.
	var delighted: bool = (via == _fey_wants())
	muts[_fey_id + "_disposition_delta"] = 3 if delighted else 1
	# Court cache · the endings count unseelie recruits via this key.
	muts["fey_court_" + _fey_id] = court

	var recruit_line := ("They join your party gladly — you read them true." if delighted
		else ("They join your party, but coolly — bought, not won." if via == "OFFER"
			else "They join your party, but warily — recruited, not won over."))
	_render_result_view(
		_fey_str("name", "?") + " · RECRUITED",
		recruit_line + "  A checkpoint has opened at " + _short_manifestation() + ".",
		C_COURT_SEELIE if court == "seelie" else (C_COURT_UNSEELIE if court == "unseelie" else C_COURT_WILDFEY),
		func() -> void: negotiation_complete.emit(_fey_id, "recruited", muts)
	)


func _rebuff(reason: String, mutations: Dictionary = {}) -> void:
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("pair_cold", 0.6)
	var tail := "\n\nThe flap closes.  This booth will not open again tonight." \
			if bool(mutations.get("lock_booth", false)) \
			else "\n\nThey remain at their booth.  You may try again later."
	_render_result_view(
		_fey_str("name", "?") + " · REBUFFED",
		reason + "." + tail,
		C_ROSE,
		func() -> void: negotiation_complete.emit(_fey_id, "rebuffed", mutations)
	)


func _on_walk_away() -> void:
	negotiation_complete.emit(_fey_id, "walked_away", {})


func _on_fight_pressed() -> void:
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("loss_thud", 0.7)
	_render_result_view(
		_fey_str("name", "?") + " · HOSTILE",
		"You have chosen combat.\n\n· they take a step back · their booth-shape flickers · you see the true form under it · the tent flaps close ·",
		C_COURT_UNSEELIE,
		func() -> void: negotiation_complete.emit(_fey_id, "hostile", {"combat_pending": true})
	)


func _render_result_view(title: String, body: String, tint: Color, on_dismiss: Callable) -> void:
	_clear_panel()
	_panel_root = Control.new()
	_panel_root.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_panel_root.offset_left = -260
	_panel_root.offset_right = 260
	_panel_root.offset_top = -100
	_panel_root.offset_bottom = 100
	add_child(_panel_root)

	var panel_bg := ColorRect.new()
	panel_bg.color = C_PANEL
	panel_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_panel_root.add_child(panel_bg)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.offset_left = 20
	v.offset_right = -20
	v.offset_top = 20
	v.offset_bottom = -20
	v.add_theme_constant_override("separation", 12)
	_panel_root.add_child(v)

	var title_lbl := Label.new()
	title_lbl.text = "· " + title + " ·"
	title_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title_lbl.add_theme_font_size_override("font_size", 18)
	title_lbl.add_theme_color_override("font_color", tint)
	v.add_child(title_lbl)

	var body_lbl := RichTextLabel.new()
	body_lbl.bbcode_enabled = false
	body_lbl.fit_content = true
	body_lbl.text = body
	body_lbl.add_theme_font_size_override("normal_font_size", 15)
	body_lbl.add_theme_color_override("default_color", C_CREAM)
	body_lbl.custom_minimum_size = Vector2(0, 60)
	v.add_child(body_lbl)

	var dismiss_btn := Button.new()
	dismiss_btn.text = "  continue  →  "
	dismiss_btn.add_theme_font_size_override("font_size", 15)
	dismiss_btn.pressed.connect(on_dismiss)
	v.add_child(dismiss_btn)


func _short_manifestation() -> String:
	var m: String = _fey_str("manifestation", "")
	if m == "": return "their booth"
	# First sentence up to the first period.
	var idx: int = m.find(" · ")
	if idx < 0: idx = m.find(".")
	if idx <= 0: return m.substr(0, min(m.length(), 60))
	return m.substr(0, idx)


func _on_back() -> void:
	quit_to_shelf.emit()


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			_on_back()
			get_viewport().set_input_as_handled()


# Null-safe string field read — feys.json carries explicit nulls
# (favorite_play, shakespeare_source), and Dictionary.get() returns
# the stored null instead of the default when the key exists.
# String(null) is an invalid constructor call and crashed the
# negotiation view on any fey without a favorite play.
func _fey_str(key: String, default: String = "") -> String:
	var v = _fey.get(key, default)
	return v if v is String else default
