extends Control
## THE MAJOR ARCANA — the Fool's Journey.
##
## Sequences the 22 gauntlet arcana in canonical order (Fool→World)
## as one run: a ladder of cards, each launching the existing
## TarotGauntletGame with its signature scenario, a bookend
## interstitial on return (the Querent's Thread updates, Dean gets his
## beat), and progress persisted in GauntletState.state.campaign.
##
## Rides the gauntlet as a launcher + bookend — no second engine.
## Design: lore/_MAJOR_ARCANA_CAMPAIGN_DESIGN.md
## Pattern: SpreadHost (gauntlet launch + game_ended) + ProfilePanel
## (static build, ui group, Esc to close).

const DATA_PATH := "res://resources/games/campaign/campaign_arcana.json"
const TAROT_GAUNTLET_SCENE := preload("res://scenes/games/TarotGauntletGame.tscn")

const C_BG     := Color(0.024, 0.020, 0.014, 0.98)
const C_ACCENT := Color(0.95, 0.78, 0.40)
const C_TEXT   := Color(0.86, 0.80, 0.66)
const C_DIM    := Color(0.48, 0.45, 0.38)
const C_DONE   := Color(0.62, 0.90, 0.68)
const C_ACTIVE := Color(0.97, 0.86, 0.45)
const C_DEAN   := Color(0.80, 0.55, 0.55)

const ROMAN := ["0","I","II","III","IV","V","VI","VII","VIII","IX","X",
	"XI","XII","XIII","XIV","XV","XVI","XVII","XVIII","XIX","XX","XXI"]

var _arcana: Array = []          # the 22 entries, in order
var _game: Node = null
var _active_entry: Dictionary = {}


static func build(parent: Node) -> Control:
	var panel := Control.new()
	panel.set_script(load("res://scenes/menu/MajorArcanaCampaign.gd"))
	panel.name = "MajorArcanaCampaign"
	return panel


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	var bank := get_node_or_null("/root/SFXBank")
	if bank: bank.play("menu_open", 0.7)
	_load_data()
	_render_ladder()


func _input(event: InputEvent) -> void:
	# Only close from the ladder view; while a gauntlet is live it owns input.
	if _game != null and is_instance_valid(_game):
		return
	if event.is_action_pressed("menu_back") or \
			(event is InputEventKey and (event as InputEventKey).keycode == KEY_ESCAPE and event.pressed):
		queue_free()
		get_viewport().set_input_as_handled()


func _load_data() -> void:
	if not FileAccess.file_exists(DATA_PATH): return
	var f := FileAccess.open(DATA_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		_arcana = (parsed as Dictionary).get("arcana", [])


func _arcana_name(aid: String) -> String:
	var parts := aid.split("_")
	var out: Array = []
	for p in parts:
		if p == "of": out.append("of")
		else: out.append((p as String).capitalize())
	return " ".join(out)


func _active_index() -> int:
	# First arcana not yet cleared, in order. -1 if the run is complete.
	var gs := get_node_or_null("/root/GauntletState")
	for i in range(_arcana.size()):
		var aid := String((_arcana[i] as Dictionary).get("arcana", ""))
		if gs == null or not bool(gs.call("campaign_is_cleared", aid)):
			return i
	return -1


# ── the ladder ────────────────────────────────────────────────────

func _render_ladder() -> void:
	for c in get_children():
		c.queue_free()

	var dim := ColorRect.new()
	dim.color = C_BG
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)

	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 60)
	margin.add_theme_constant_override("margin_right", 60)
	margin.add_theme_constant_override("margin_top", 28)
	margin.add_theme_constant_override("margin_bottom", 24)
	add_child(margin)

	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 8)
	margin.add_child(col)

	var gs := get_node_or_null("/root/GauntletState")
	var thread: int = int(gs.call("campaign_thread")) if gs else 0
	var active := _active_index()

	var header := Label.new()
	header.text = "· THE MAJOR ARCANA · the Fool's Journey ·"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 22)
	header.add_theme_color_override("font_color", C_ACCENT)
	col.add_child(header)

	var status := Label.new()
	var cleared_n := (active if active >= 0 else _arcana.size())
	status.text = "%d of 22 laid down   ·   the Querent's Thread: %d" % [cleared_n, thread]
	status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	status.add_theme_font_size_override("font_size", 13)
	status.add_theme_color_override("font_color", C_DIM)
	col.add_child(status)

	var rule := ColorRect.new()
	rule.color = Color(C_ACCENT.r, C_ACCENT.g, C_ACCENT.b, 0.3)
	rule.custom_minimum_size.y = 1
	col.add_child(rule)

	var scroll := ScrollContainer.new()
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	col.add_child(scroll)
	var ladder := VBoxContainer.new()
	ladder.add_theme_constant_override("separation", 3)
	ladder.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(ladder)

	for i in range(_arcana.size()):
		var e: Dictionary = _arcana[i]
		var aid := String(e.get("arcana", ""))
		var cleared: bool = gs != null and bool(gs.call("campaign_is_cleared", aid))
		var is_active := i == active
		var locked := (not cleared) and (not is_active)

		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 10)
		ladder.add_child(row)

		var num := Label.new()
		num.text = ROMAN[i]
		num.custom_minimum_size.x = 46
		num.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		num.add_theme_font_size_override("font_size", 15)
		num.add_theme_color_override("font_color", C_DONE if cleared else (C_ACTIVE if is_active else C_DIM))
		row.add_child(num)

		var mark := Label.new()
		mark.text = "✓" if cleared else ("▶" if is_active else "·")
		mark.add_theme_font_size_override("font_size", 15)
		mark.add_theme_color_override("font_color", C_DONE if cleared else (C_ACTIVE if is_active else C_DIM))
		row.add_child(mark)

		if is_active:
			var play := Button.new()
			play.text = "  %s  ·  %s  " % [_arcana_name(aid), String(e.get("location", "")).capitalize()]
			play.add_theme_font_size_override("font_size", 16)
			play.add_theme_color_override("font_color", C_ACTIVE)
			var ent := e
			play.pressed.connect(func() -> void: _launch(ent))
			row.add_child(play)
		else:
			var lbl := Label.new()
			lbl.text = "  " + _arcana_name(aid) + ("" if cleared else "  ·  ?")
			lbl.add_theme_font_size_override("font_size", 15)
			lbl.add_theme_color_override("font_color", C_DONE if cleared else C_DIM)
			row.add_child(lbl)

	if active < 0:
		var done := Label.new()
		done.text = "· THE READING IS COMPLETE · Fool to World ·"
		done.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		done.add_theme_font_size_override("font_size", 16)
		done.add_theme_color_override("font_color", C_DONE)
		col.add_child(done)

	var close := Button.new()
	close.text = "  · leave the table ·  "
	close.add_theme_font_size_override("font_size", 14)
	close.pressed.connect(func() -> void: queue_free())
	col.add_child(close)


# ── launch + return ───────────────────────────────────────────────

func _setup_hand(aid: String, scenario: String) -> String:
	var p := "res://resources/games/%s/setup_%s.json" % [aid, scenario]
	if not FileAccess.file_exists(p): return "john_frank"
	var f := FileAccess.open(p, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		return String((parsed as Dictionary).get("hand", "john_frank"))
	return "john_frank"


func _launch(entry: Dictionary) -> void:
	_active_entry = entry
	for c in get_children():
		c.queue_free()
	var aid := String(entry.get("arcana", ""))
	var loc := String(entry.get("location", ""))
	var scn := String(entry.get("scenario", ""))
	_game = TAROT_GAUNTLET_SCENE.instantiate()
	_game.call("start_scenario", aid, loc, _setup_hand(aid, scn), scn, false)
	_game.set("z_index", 30)
	add_child(_game)
	_game.connect("game_ended", _on_gauntlet_ended)


func _on_gauntlet_ended(outcome: String, _summary: Dictionary) -> void:
	if _game != null and is_instance_valid(_game):
		_game.queue_free()
	_game = null
	var won := outcome == "won"
	if won:
		var aid := String(_active_entry.get("arcana", ""))
		var award := int(_active_entry.get("thread_award", 1))
		var gs := get_node_or_null("/root/GauntletState")
		var newly := gs != null and bool(gs.call("campaign_clear", aid, award))
		if newly:
			OneironauticsTokens.add("campaign_arcana_%s_cleared" % aid)
			_maybe_close_act(int(_active_entry.get("act", 0)))
			_maybe_complete()
	_render_bookend(won)


func _maybe_close_act(act: int) -> void:
	if act <= 0: return
	var gs := get_node_or_null("/root/GauntletState")
	if gs == null: return
	# All arcana of this act cleared?
	for e_v in _arcana:
		var e: Dictionary = e_v
		if int(e.get("act", 0)) != act: continue
		if not bool(gs.call("campaign_is_cleared", String(e.get("arcana", "")))):
			return
	if bool(gs.call("campaign_close_act", act)):
		OneironauticsTokens.add("campaign_act_%d_closed" % act)


func _maybe_complete() -> void:
	var gs := get_node_or_null("/root/GauntletState")
	if gs == null: return
	for e_v in _arcana:
		if not bool(gs.call("campaign_is_cleared", String((e_v as Dictionary).get("arcana", "")))):
			return
	OneironauticsTokens.add("campaign_major_arcana_complete")


func _render_bookend(won: bool) -> void:
	for c in get_children():
		c.queue_free()
	var dim := ColorRect.new()
	dim.color = C_BG
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)

	var panel := Panel.new()
	panel.set_anchors_preset(Control.PRESET_CENTER)
	panel.offset_left = -430
	panel.offset_right = 430
	panel.offset_top = -220
	panel.offset_bottom = 220
	add_child(panel)
	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 30)
	margin.add_theme_constant_override("margin_right", 30)
	margin.add_theme_constant_override("margin_top", 26)
	margin.add_theme_constant_override("margin_bottom", 26)
	panel.add_child(margin)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 14)
	margin.add_child(v)

	var aid := String(_active_entry.get("arcana", ""))
	var hdr := Label.new()
	hdr.text = ("· %s · the card turns ·" % _arcana_name(aid)) if won else ("· %s · the card resists ·" % _arcana_name(aid))
	hdr.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hdr.add_theme_font_size_override("font_size", 20)
	hdr.add_theme_color_override("font_color", C_DONE if won else C_DEAN)
	v.add_child(hdr)

	if won:
		var gs := get_node_or_null("/root/GauntletState")
		var thread: int = int(gs.call("campaign_thread")) if gs else 0
		var tl := Label.new()
		tl.text = "The Querent's Thread lengthens.  ( now %d )" % thread
		tl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		tl.add_theme_font_size_override("font_size", 13)
		tl.add_theme_color_override("font_color", C_ACCENT)
		v.add_child(tl)

	var beat := Label.new()
	beat.text = String(_active_entry.get("dean_beat", "")) if won else "You do not advance. He waits. He is patient the way weather is patient — try the card again when you are ready."
	beat.add_theme_font_size_override("font_size", 15)
	beat.add_theme_color_override("font_color", C_TEXT)
	beat.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(beat)

	var cont := Button.new()
	cont.text = "  · continue the reading ·  "
	cont.add_theme_font_size_override("font_size", 16)
	cont.add_theme_color_override("font_color", C_ACCENT)
	cont.pressed.connect(func() -> void: _render_ladder())
	v.add_child(cont)
