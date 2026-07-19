extends Control
## THE SPREAD — three drawn arcana played in sequence with a small
## carryover. Design: lore/_GAUNTLET_DESIGN_PLAYBOOK.md "THE SPREAD".
##
## Spawned by GalleryOverlay's gallery-games section. Fully
## data-driven: the deal scans res://resources/games/<arcana>/
## setup_*.json, and each setup file carries its own location + hand,
## so scenarios need no changes and new setups join the pool for free.
##
## Carryover between cards (host computes, game clamps):
##   · sanity  — carries down only, floor 2
##   · inertia — half, rounded down, cap 3
##   · one held CORE-deck card picked from the winning hand
## A loss ends the reading. Three wins = A FULL READING.
##
## Spread state persists in GauntletState.state.spread so quitting
## mid-spread resumes. F4-compliant via add_to_group("ui").

signal closed

const TAROT_GAUNTLET_SCENE := preload("res://scenes/games/TarotGauntletGame.tscn")
const GAMES_ROOT := "res://resources/games/"
const CORE_DECK_PATH := "res://resources/games/framework/action_tableau_core.json"
const CARD_ART_DIR := "res://resources/games/gauntlet_cards/"
const NON_ARCANA_DIRS := ["framework", "hands", "locations", "gauntlet_cards",
		"community_planned", "vol7"]

const C_GOLD := Color(0.92, 0.78, 0.40)
const C_BG   := Color(0.024, 0.020, 0.014, 0.97)
const C_TXT  := Color(0.83, 0.79, 0.69)
const C_DIM  := Color(0.50, 0.47, 0.38)
const C_WIN  := Color(0.55, 0.85, 0.55)
const C_LOSS := Color(0.85, 0.45, 0.45)

var _setups_by_arcana: Dictionary = {}   # arcana → Array[{id,title,subtitle,difficulty,location,hand}]
var _core_card_titles: Dictionary = {}   # core card id → title
var _root: Control = null
var _game: Node = null
# DAILY DRAW mode · set by GalleryOverlay before add_child. One
# date-seeded card (same card for everyone on the same day), no
# carryover, no persistence beyond a played-today mark.
var daily_mode: bool = false


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	randomize()
	_scan_setups()
	_load_core_titles()
	if daily_mode:
		_render_daily()
		return
	var spread := GauntletState.get_spread()
	if spread.is_empty():
		_render_draw(_deal())
	else:
		_render_progress()


func _input(event: InputEvent) -> void:
	if not is_visible_in_tree():
		return
	if _game != null and is_instance_valid(_game):
		return   # a scenario is live · it owns input
	if event is InputEventKey and (event as InputEventKey).pressed \
			and (event as InputEventKey).keycode == KEY_ESCAPE:
		get_viewport().set_input_as_handled()
		_close()


func _close() -> void:
	closed.emit()
	queue_free()


# ── Data ─────────────────────────────────────────────────────────

func _scan_setups() -> void:
	_setups_by_arcana.clear()
	var d := DirAccess.open(GAMES_ROOT)
	if d == null:
		return
	d.list_dir_begin()
	var dn := d.get_next()
	while dn != "":
		if d.current_is_dir() and not dn.begins_with("_") and not (dn in NON_ARCANA_DIRS):
			var arc_dir := DirAccess.open(GAMES_ROOT + dn)
			if arc_dir != null:
				var setups: Array = []
				arc_dir.list_dir_begin()
				var fn := arc_dir.get_next()
				while fn != "":
					if fn.begins_with("setup_") and fn.ends_with(".json"):
						var sd := _load_json(GAMES_ROOT + dn + "/" + fn)
						if not sd.is_empty():
							setups.append({
								"id": String(sd.get("id", fn.trim_prefix("setup_").trim_suffix(".json"))),
								"title": String(sd.get("title", "")),
								"subtitle": String(sd.get("subtitle", "")),
								"difficulty": String(sd.get("difficulty", "")),
								"location": String(sd.get("location", "")),
								"hand": String(sd.get("hand", "_placeholder")),
							})
					fn = arc_dir.get_next()
				arc_dir.list_dir_end()
				if not setups.is_empty():
					_setups_by_arcana[dn] = setups
		dn = d.get_next()
	d.list_dir_end()


func _load_core_titles() -> void:
	var cd := _load_json(CORE_DECK_PATH)
	for c_v in cd.get("cards", []):
		var c: Dictionary = c_v
		_core_card_titles[String(c.get("id", ""))] = String(c.get("title", c.get("id", "")))


func _load_json(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {}
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	return parsed if parsed is Dictionary else {}


func _deal() -> Array:
	# Three DISTINCT arcana, one random setup each.
	var arcs: Array = _setups_by_arcana.keys()
	arcs.shuffle()
	var cards: Array = []
	for i in range(mini(3, arcs.size())):
		var arc: String = String(arcs[i])
		var setups: Array = _setups_by_arcana[arc]
		var pick: Dictionary = setups[randi() % setups.size()]
		cards.append({
			"arcana": arc,
			"setup": String(pick["id"]),
			"title": String(pick["title"]),
			"difficulty": String(pick["difficulty"]),
			"location": String(pick["location"]),
			"hand": String(pick["hand"]),
			"outcome": "",
			"ending": "",
		})
	return cards


# ── DAILY DRAW ───────────────────────────────────────────────────

static func daily_key() -> String:
	var d := Time.get_date_dict_from_system()
	return "%04d%02d%02d" % [int(d["year"]), int(d["month"]), int(d["day"])]


func _daily_pick() -> Dictionary:
	# Deterministic per calendar day · sorted keys so DirAccess
	# listing order can't shift the draw between machines.
	var rng := RandomNumberGenerator.new()
	rng.seed = int(daily_key())
	var arcs: Array = _setups_by_arcana.keys()
	arcs.sort()
	if arcs.is_empty():
		return {}
	var arc: String = String(arcs[rng.randi() % arcs.size()])
	var setups: Array = (_setups_by_arcana[arc] as Array).duplicate()
	setups.sort_custom(func(a, b) -> bool: return String(a["id"]) < String(b["id"]))
	var pick: Dictionary = setups[rng.randi() % setups.size()]
	return {
		"arcana": arc,
		"setup": String(pick["id"]),
		"title": String(pick["title"]),
		"difficulty": String(pick["difficulty"]),
		"location": String(pick["location"]),
		"hand": String(pick["hand"]),
		"outcome": "",
		"ending": "",
	}


func _render_daily(after_outcome: String = "") -> void:
	var cd := _daily_pick()
	if cd.is_empty():
		_close()
		return
	var v := _build_frame("· THE DAILY DRAW ·")
	var sub := Label.new()
	sub.text = "one card, same card, everyone, today"
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub.add_theme_font_size_override("font_size", 13)
	sub.add_theme_color_override("font_color", C_DIM)
	v.add_child(sub)
	_card_row(v, [cd], 0)
	var played_key: String = "daily:" + daily_key()
	var played: bool = SaveSystem.is_unlocked(played_key)
	if after_outcome != "" or played:
		var res := Label.new()
		if after_outcome == "won":
			res.text = "· today's card fell your way ·"
			res.add_theme_color_override("font_color", C_WIN)
		elif after_outcome == "lost":
			res.text = "· today's card reversed on you · tomorrow deals fresh ·"
			res.add_theme_color_override("font_color", C_LOSS)
		else:
			res.text = "· played today · replays welcome, the mark is already made ·"
			res.add_theme_color_override("font_color", C_DIM)
		res.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		res.add_theme_font_size_override("font_size", 13)
		v.add_child(res)
	var actions := HBoxContainer.new()
	actions.alignment = BoxContainer.ALIGNMENT_CENTER
	actions.add_theme_constant_override("separation", 16)
	v.add_child(actions)
	_button(actions, "  PLAY TODAY'S CARD  ", _launch_daily)
	_button(actions, "  ← back  ", _close, 13)
	GamepadMgr.focus_first.call_deferred(_root)


func _launch_daily() -> void:
	var cd := _daily_pick()
	if cd.is_empty():
		return
	_clear_root()
	_game = TAROT_GAUNTLET_SCENE.instantiate()
	_game.call("start_scenario", String(cd["arcana"]), String(cd["location"]),
			String(cd["hand"]), String(cd["setup"]))
	_game.set("z_index", 30)
	add_child(_game)
	_game.connect("game_ended", _on_daily_ended)


func _on_daily_ended(outcome: String, _summary: Dictionary) -> void:
	if _game != null and is_instance_valid(_game):
		_game.queue_free()
	_game = null
	if outcome == "won" or outcome == "lost":
		SaveSystem.mark_unlocked("daily:" + daily_key())
	_render_daily(outcome)


func _card_art(arcana: String, size: Vector2i) -> Texture2D:
	var hero := HeroImage.new()
	if not hero.load_from(CARD_ART_DIR + arcana + ".json"):
		return null
	return hero.texture(size)


# ── Views ────────────────────────────────────────────────────────

func _clear_root() -> void:
	if _root != null and is_instance_valid(_root):
		_root.queue_free()
	_root = null


func _build_frame(title_text: String) -> VBoxContainer:
	_clear_root()
	_root = Control.new()
	_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_root)
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_root.add_child(bg)
	var v := VBoxContainer.new()
	v.set_anchors_preset(Control.PRESET_CENTER)
	v.offset_left = -430
	v.offset_right = 430
	v.offset_top = -330
	v.offset_bottom = 330
	v.add_theme_constant_override("separation", 12)
	_root.add_child(v)
	var hdr := Label.new()
	hdr.text = title_text
	hdr.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hdr.add_theme_font_size_override("font_size", 20)
	hdr.add_theme_color_override("font_color", C_GOLD)
	v.add_child(hdr)
	return v


func _card_row(v: VBoxContainer, cards: Array, idx_current: int) -> void:
	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", 26)
	v.add_child(row)
	for i in range(cards.size()):
		var cd: Dictionary = cards[i]
		var col := VBoxContainer.new()
		col.add_theme_constant_override("separation", 4)
		row.add_child(col)
		var art := TextureRect.new()
		art.texture = _card_art(String(cd["arcana"]), Vector2i(220, 340))
		art.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		art.custom_minimum_size = Vector2(220, 340)
		art.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		var oc: String = String(cd.get("outcome", ""))
		if oc == "" and i != idx_current:
			art.modulate = Color(0.45, 0.45, 0.45, 1.0)
		elif oc == "lost":
			art.modulate = Color(0.55, 0.30, 0.30, 1.0)
		col.add_child(art)
		var name_lbl := Label.new()
		name_lbl.text = String(cd["arcana"]).replace("_", " ").to_upper()
		name_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		name_lbl.add_theme_font_size_override("font_size", 13)
		name_lbl.add_theme_color_override("font_color", C_GOLD if i == idx_current and oc == "" else C_TXT)
		col.add_child(name_lbl)
		var setup_lbl := Label.new()
		setup_lbl.text = String(cd["title"])
		setup_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		setup_lbl.add_theme_font_size_override("font_size", 12)
		setup_lbl.add_theme_color_override("font_color", C_DIM)
		col.add_child(setup_lbl)
		var st := Label.new()
		if oc == "won":
			st.text = "· cleared ·"
			st.add_theme_color_override("font_color", C_WIN)
		elif oc == "lost":
			st.text = "· reversed ·"
			st.add_theme_color_override("font_color", C_LOSS)
		elif i == idx_current:
			st.text = "· current ·"
			st.add_theme_color_override("font_color", C_GOLD)
		else:
			st.text = "· waiting ·"
			st.add_theme_color_override("font_color", C_DIM)
		st.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		st.add_theme_font_size_override("font_size", 12)
		col.add_child(st)


func _button(v: Container, text: String, cb: Callable, font_size: int = 15) -> Button:
	var b := Button.new()
	b.text = text
	b.add_theme_font_size_override("font_size", font_size)
	b.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	b.pressed.connect(cb)
	v.add_child(b)
	return b


func _render_draw(cards: Array) -> void:
	var v := _build_frame("· THE SPREAD ·")
	if cards.size() < 3:
		var err := Label.new()
		err.text = "the deck is missing · no arcana setups found on disk"
		err.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		err.add_theme_font_size_override("font_size", 13)
		err.add_theme_color_override("font_color", C_LOSS)
		v.add_child(err)
		_button(v, "  ← back  ", _close, 13)
		return
	var sub := Label.new()
	sub.text = "three cards, one sitting · what you lose in one room you carry into the next"
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub.add_theme_font_size_override("font_size", 13)
	sub.add_theme_color_override("font_color", C_DIM)
	v.add_child(sub)
	_card_row(v, cards, 0)
	var actions := HBoxContainer.new()
	actions.alignment = BoxContainer.ALIGNMENT_CENTER
	actions.add_theme_constant_override("separation", 16)
	v.add_child(actions)
	_button(actions, "  REDRAW  ", func() -> void: _render_draw(_deal()))
	_button(actions, "  BEGIN THE READING  ", func() -> void:
		GauntletState.set_spread({"cards": cards, "idx": 0, "carry": {}})
		var sfx := get_node_or_null("/root/SFXBank")
		if sfx: sfx.play("card_place", 0.7)
		_launch_current())
	_button(actions, "  ← back  ", _close, 13)
	GamepadMgr.focus_first.call_deferred(_root)


func _render_progress() -> void:
	var spread := GauntletState.get_spread()
	var cards: Array = spread.get("cards", [])
	var idx: int = int(spread.get("idx", 0))
	var v := _build_frame("· THE SPREAD · card %d of 3 ·" % (idx + 1))
	_card_row(v, cards, idx)
	var carry: Dictionary = spread.get("carry", {})
	if not carry.is_empty():
		var carry_lbl := Label.new()
		var held: String = String(carry.get("held_card", ""))
		carry_lbl.text = "carrying in · sanity %d · inertia %d%s" % [
			int(carry.get("sanity", 5)), int(carry.get("inertia", 0)),
			(" · " + String(_core_card_titles.get(held, held))) if held != "" else ""]
		carry_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		carry_lbl.add_theme_font_size_override("font_size", 13)
		carry_lbl.add_theme_color_override("font_color", C_GOLD)
		v.add_child(carry_lbl)
	var actions := HBoxContainer.new()
	actions.alignment = BoxContainer.ALIGNMENT_CENTER
	actions.add_theme_constant_override("separation", 16)
	v.add_child(actions)
	_button(actions, "  DEAL THE NEXT CARD  " if idx > 0 else "  TURN THE FIRST CARD  ", _launch_current)
	_button(actions, "  abandon the reading  ", _abandon, 12)
	_button(actions, "  ← back  ", _close, 13)
	GamepadMgr.focus_first.call_deferred(_root)


func _abandon() -> void:
	GauntletState.clear_spread()
	_render_draw(_deal())


func _launch_current() -> void:
	var spread := GauntletState.get_spread()
	var cards: Array = spread.get("cards", [])
	var idx: int = int(spread.get("idx", 0))
	if idx >= cards.size():
		return
	var cd: Dictionary = cards[idx]
	_clear_root()
	_game = TAROT_GAUNTLET_SCENE.instantiate()
	_game.set("spread_carry", (spread.get("carry", {}) as Dictionary).duplicate())
	_game.call("start_scenario", String(cd["arcana"]), String(cd["location"]),
			String(cd["hand"]), String(cd["setup"]))
	_game.set("z_index", 30)
	add_child(_game)
	_game.connect("game_ended", _on_game_ended)


func _on_game_ended(outcome: String, summary: Dictionary) -> void:
	if _game != null and is_instance_valid(_game):
		_game.queue_free()
	_game = null
	if outcome == "leave":
		# Walked out mid-scenario · the card is still face-down and
		# the gauntlet's own mid-run save will resume it.
		_render_progress()
		return
	var spread := GauntletState.get_spread()
	var cards: Array = spread.get("cards", [])
	var idx: int = int(spread.get("idx", 0))
	if idx >= cards.size():
		_render_draw(_deal())
		return
	var cd: Dictionary = cards[idx]
	cd["outcome"] = "won" if outcome == "won" else "lost"
	cd["ending"] = String(summary.get("ending_token", summary.get("finale_title", "")))
	cards[idx] = cd
	spread["cards"] = cards
	if outcome != "won":
		GauntletState.clear_spread()
		_render_reading_over(cards, false)
		return
	if idx >= 2:
		GauntletState.clear_spread()
		SaveSystem.mark_unlocked("achievement:spread_full_reading")
		var sfx := get_node_or_null("/root/SFXBank")
		if sfx: sfx.play("unlock_chime", 0.8)
		_render_reading_over(cards, true)
		return
	GauntletState.set_spread(spread)
	_render_interstitial(spread, summary)


func _render_interstitial(spread: Dictionary, summary: Dictionary) -> void:
	var cards: Array = spread.get("cards", [])
	var idx: int = int(spread.get("idx", 0))
	var v := _build_frame("· CARD %d CLEARED ·" % (idx + 1))
	_card_row(v, cards, idx)
	var final_sanity: int = int(summary.get("final_sanity", 5))
	var final_inertia: int = int(summary.get("final_inertia", 0))
	var carry_inertia: int = clampi(final_inertia / 2, 0, 3)
	var carry_lbl := Label.new()
	carry_lbl.text = "you leave with · sanity %d · inertia %d (carries as %d)" % [
			final_sanity, final_inertia, carry_inertia]
	carry_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	carry_lbl.add_theme_font_size_override("font_size", 14)
	carry_lbl.add_theme_color_override("font_color", C_TXT)
	v.add_child(carry_lbl)
	# Held card · core-deck cards only survive the arcana change.
	var holdables: Array = []
	for cid_v in summary.get("final_hand", []):
		var cid: String = String(cid_v)
		if _core_card_titles.has(cid) and not (cid in holdables):
			holdables.append(cid)
	var hold_lbl := Label.new()
	hold_lbl.text = "hold one card for the next room:" if not holdables.is_empty() \
			else "nothing in this hand travels · arcana cards stay with their rooms"
	hold_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hold_lbl.add_theme_font_size_override("font_size", 13)
	hold_lbl.add_theme_color_override("font_color", C_DIM)
	v.add_child(hold_lbl)
	var pick_row := HBoxContainer.new()
	pick_row.alignment = BoxContainer.ALIGNMENT_CENTER
	pick_row.add_theme_constant_override("separation", 10)
	v.add_child(pick_row)
	for cid_v in holdables:
		var cid: String = String(cid_v)
		_button(pick_row, "  %s  " % String(_core_card_titles.get(cid, cid)),
				func() -> void: _commit_carry(final_sanity, carry_inertia, cid), 13)
	_button(pick_row, "  hold nothing  ",
			func() -> void: _commit_carry(final_sanity, carry_inertia, ""), 13)
	GamepadMgr.focus_first.call_deferred(_root)


func _commit_carry(sanity: int, inertia: int, held: String) -> void:
	var spread := GauntletState.get_spread()
	var carry: Dictionary = {"sanity": sanity, "inertia": inertia}
	if held != "":
		carry["held_card"] = held
	spread["carry"] = carry
	spread["idx"] = int(spread.get("idx", 0)) + 1
	GauntletState.set_spread(spread)
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("card_flip", 0.6)
	_render_progress()


func _render_reading_over(cards: Array, full_reading: bool) -> void:
	var v := _build_frame("· A FULL READING ·" if full_reading else "· THE READING ENDS EARLY ·")
	_card_row(v, cards, -1)
	var lines: Array = []
	for cd_v in cards:
		var cd: Dictionary = cd_v
		var oc: String = String(cd.get("outcome", ""))
		if oc == "":
			lines.append("%s · never turned" % String(cd["arcana"]).replace("_", " "))
		else:
			var ending: String = String(cd.get("ending", ""))
			lines.append("%s · %s%s" % [String(cd["arcana"]).replace("_", " "),
					"cleared" if oc == "won" else "reversed",
					(" · " + ending.replace("_", " ")) if ending != "" else ""])
	var body := Label.new()
	body.text = "\n".join(lines)
	body.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	body.add_theme_font_size_override("font_size", 13)
	body.add_theme_color_override("font_color", C_TXT)
	v.add_child(body)
	if full_reading:
		var ach := Label.new()
		ach.text = "✦ achievement · A FULL READING"
		ach.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		ach.add_theme_font_size_override("font_size", 14)
		ach.add_theme_color_override("font_color", C_GOLD)
		v.add_child(ach)
	var actions := HBoxContainer.new()
	actions.alignment = BoxContainer.ALIGNMENT_CENTER
	actions.add_theme_constant_override("separation", 16)
	v.add_child(actions)
	_button(actions, "  DRAW AGAIN  ", func() -> void: _render_draw(_deal()))
	_button(actions, "  ← back to gallery  ", _close, 13)
	GamepadMgr.focus_first.call_deferred(_root)
