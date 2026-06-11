extends Control
## Tarot Gauntlet — main controller for one arcana scenario.
## Walks the 5-phase loop: Action → Planning → Shadow → Drift → Upkeep.
## Loads data from godot/resources/games/.

# Inner class — draws faint amber adjacency lines between board nodes.
# Used by _render_board to give the map a visible path structure.
class BoardLinesLayer extends Control:
	var adj_pairs: Array = []  # Array of [Vector2, Vector2]
	func _draw() -> void:
		for p in adj_pairs:
			draw_line(p[0], p[1], Color(0.78, 0.65, 0.42, 0.30), 2.0, true)


signal game_ended(outcome: String, summary: Dictionary)

# ── Data file paths ──────────────────────────────────────────────────
const DATA_ROOT := "res://resources/games/"
const FRAMEWORK_CORE := DATA_ROOT + "framework/action_tableau_core.json"

# Scenario selection — set by start_scenario() before _ready
var _arcana_id: String = "fool"
var _location_id: String = "dambrosios"
var _hand_id: String = "john_frank"

# ── Loaded data ──────────────────────────────────────────────────────
var _setup: Dictionary = {}
var _action_cards: Dictionary = {}       # id → card def (merged Fool + core)
var _gravity_deck_def: Dictionary = {}
var _finale_def: Dictionary = {}
var _visitors_def: Dictionary = {}       # id → visitor def
var _items_def: Dictionary = {}          # id → item def
var _piles_def: Dictionary = {}          # pile_id → {label, items[]}
var _location: Dictionary = {}
var _hand: Dictionary = {}
var _die: Dictionary = {}

# ── Runtime state ────────────────────────────────────────────────────
enum Phase {ACTION, PLANNING, SHADOW, DRIFT, UPKEEP}
var _phase: int = Phase.ACTION
var _turn: int = 1
var _time: int = 6
var _next_time_reset: int = 6   # set by Gravity/Event cards mid-turn
var _inertia: int = 0
var _health: int = 5
var _player_pos: String = "counter"
var _hand_cards: Array = []     # array of card ids currently in hand
var _gravity_draw_pile: Array = []
var _gravity_discard_pile: Array = []
var _gravity_last_drawn: Dictionary = {}
var _visitors_state: Dictionary = {}  # id → {pos, arrived, connected, claimed_turn}
var _pile_state: Dictionary = {}      # pile_id → remaining items
var _inventory: Array = []
var _bindle_assembled: bool = false
var _bell_tones_rung: int = 0
var _counter_haunted: bool = false
var _flags: Dictionary = {}
var _played_this_turn: Array = []
var _connections_made: Array = []
var _lore_tokens_collected: Array = []
var _twelve_years_used: bool = false
var _call_faith_count: int = 0
var _game_over: bool = false

# ── UI refs (built in _build_ui) ─────────────────────────────────────
var _bg: ColorRect = null
var _inv_box: VBoxContainer = null
var _phase_label: Label = null
var _turn_label: Label = null
var _time_label: Label = null
var _inertia_label: Label = null
var _health_label: Label = null
var _player_pos_label: Label = null
var _bindle_label: Label = null
var _visitors_box: VBoxContainer = null
var _hand_box: HBoxContainer = null
var _tableau_box: HBoxContainer = null
var _tableau_scroll: ScrollContainer = null
var _log: RichTextLabel = null
var _advance_btn: Button = null
var _board_root: Control = null
var _board_content: Control = null
var _board_expand_btn: Button = null
var _board_fullscreen: bool = false
# Last-rendered stat values, used by _render to flash labels on change
var _last_rendered_time: int = -1
var _last_rendered_inertia: int = -1
var _last_rendered_health: int = -1
# Every space the player has stood on at least once. Used by composite
# connect_via conditions (e.g. stranger requires stood_on:card_wall).
var _places_visited: Dictionary = {}
# Full log buffer — RichTextLabel.append_text doesn't update .text,
# so .text on the live _log returns nothing useful. We keep our own
# copy so the LOG modal can show the complete history.
var _log_buffer: PackedStringArray = []
# Unread count + per-pane title labels — feeds the "(N new)" badge
# that appears next to the LOG title when the user hasn't opened
# the modal since new lines arrived.
var _log_unread_count: int = 0
var _pane_title_labels: Dictionary = {}   # modal_key → Label
var _board_meeple: Control = null
var _board_visitor_nodes: Dictionary = {}   # visitor_id → Control (Label or TextureRect)
var _board_space_nodes: Dictionary = {}     # space_id → Label
var _gravity_card_label: RichTextLabel = null
var _end_overlay: Control = null

const C_BG: Color    = Color(0.045, 0.040, 0.030)
const C_PANEL: Color = Color(0.085, 0.070, 0.050, 0.92)
const C_BORDER: Color = Color(0.70, 0.55, 0.24, 0.45)
const C_TEXT: Color  = Color(0.86, 0.80, 0.66)
const C_DIM: Color   = Color(0.55, 0.50, 0.40)
const C_ACCENT: Color = Color(0.95, 0.78, 0.40)
const C_GOOD: Color  = Color(0.55, 0.95, 0.65)
const C_BAD: Color   = Color(0.95, 0.45, 0.45)


# ── Entry point ──────────────────────────────────────────────────────

func start_scenario(arcana: String = "fool",
					location: String = "dambrosios",
					hand: String = "john_frank") -> void:
	_arcana_id = arcana
	_location_id = location
	_hand_id = hand


func _ready() -> void:
	set_process_unhandled_key_input(true)
	_load_data()
	_build_ui()
	_init_run()
	_audio_play_bgm()
	# Force an extra board render after layout settles so the map is
	# visible on the very first frame (not just after the user expands
	# or interacts with something).
	call_deferred("_render_board")
	call_deferred("_render")
	# Surface data-load failures in the in-game log so the user doesn't
	# have to dig through Godot's Output panel to see why nothing's
	# happening. If any of these are missing, the run is unplayable.
	if _setup.is_empty() or _action_cards.is_empty() or _location.is_empty():
		_log_line("[color=#ff6464][b]DATA LOAD FAILED[/b][/color]")
		_log_line("Missing data files at: [code]%s[/code]" % DATA_ROOT)
		_log_line("  setup_the_leap.json: %s" % ("OK" if not _setup.is_empty() else "[color=#ff6464]MISSING[/color]"))
		_log_line("  action_cards.json: %s (%d cards merged)" % [
			"OK" if not _action_cards.is_empty() else "[color=#ff6464]MISSING[/color]",
			_action_cards.size()])
		_log_line("  locations/%s.json: %s" % [_location_id,
			"OK" if not _location.is_empty() else "[color=#ff6464]MISSING[/color]"])
		_log_line("[i]Check Godot's Output panel for the full diagnostic.[/i]")
		_log_line("")
	_log_line("[color=#c8a268][b]%s[/b][/color] — %s" %
			  [_setup.get("title", "THE LEAP"), _setup.get("subtitle", "")])
	_log_line("[i]%s[/i]" % _setup.get("epigraph_upright", ""))
	_log_line("")
	# Scene-setting + opening narration straight into the log,
	# right after the title — atmospheric prose first, then a few
	# short lines, then the practical "Hand:" + phase prompt.
	var scene_text: String = String(_setup.get("scene_description", ""))
	if scene_text != "":
		_log_line("[color=#c8a268]%s[/color]" % scene_text)
		_log_line("")
	for line: String in _setup.get("opening_log_lines", []):
		_log_line("[color=#7c8398]" + line + "[/color]")
	# Subtle direction hint — italicised, dimmer
	var hint: String = String(_setup.get("direction_hint", ""))
	if hint != "":
		_log_line("")
		_log_line("[color=#6e6258][i]%s[/i][/color]" % hint)
	_log_line("")
	_log_line("[color=#7c8398]Hand: %s[/color]" % str(_hand_cards))


func _unhandled_key_input(event: InputEvent) -> void:
	# Esc closes any open modal first, then exits fullscreen board.
	if event is InputEventKey and (event as InputEventKey).pressed:
		var key: InputEventKey = event
		if key.keycode == KEY_ESCAPE:
			# Topmost modal first
			var dim: Node = get_node_or_null("pane_modal_dim")
			if dim != null and is_instance_valid(dim):
				_close_pane_modal(dim as ColorRect)
				get_viewport().set_input_as_handled()
				return
			if _board_fullscreen:
				_toggle_board_fullscreen()
				get_viewport().set_input_as_handled()
	_log_line("[color=#7c8398]Phase: %s — click cards to play, then Advance →[/color]" %
		Phase.keys()[_phase])
	_log_line("")
	_render()


# ── Audio ───────────────────────────────────────────────────────────
# Wire into the existing AudioMgr autoload. BGM defaults to the vol5
# ambient drone (the diner being the diner — matches the Fool scene).
# SFX paths are conventions; missing files fall through silently in
# AudioMgr.play_sfx (no exceptions, no spam).

const _BGM_BY_LOCATION := {
	"dambrosios": "res://assets/audio/bgm/vol5_ambient.ogg",
}
const _SFX := {
	"card_play":    "res://assets/audio/sfx/gauntlet_card_play.ogg",
	"dice_roll":    "res://assets/audio/sfx/gauntlet_dice_roll.ogg",
	"bell_tone":    "res://assets/audio/sfx/gauntlet_bell_tone.ogg",
	"gravity_draw": "res://assets/audio/sfx/gauntlet_gravity_draw.ogg",
	"visitor_arrive": "res://assets/audio/sfx/gauntlet_visitor_arrive.ogg",
	"visitor_claimed": "res://assets/audio/sfx/gauntlet_visitor_claimed.ogg",
	"visitor_connect": "res://assets/audio/sfx/gauntlet_visitor_connect.ogg",
	"item_pickup":  "res://assets/audio/sfx/gauntlet_item_pickup.ogg",
	"bundle":       "res://assets/audio/sfx/gauntlet_bundle.ogg",
	"win":          "res://assets/audio/sfx/gauntlet_win.ogg",
	"loss":         "res://assets/audio/sfx/gauntlet_loss.ogg",
	"lore_token":   "res://assets/audio/sfx/gauntlet_lore_token.ogg",
}

func _audio_play_bgm() -> void:
	var bgm: String = _BGM_BY_LOCATION.get(_location_id, "")
	if bgm != "" and Engine.has_singleton("AudioMgr") == false:
		# AudioMgr is an autoload, accessed by name
		pass
	if bgm != "" and Engine.get_main_loop() != null:
		AudioMgr.play_bgm(bgm)

func _audio_sfx(key: String) -> void:
	var path: String = _SFX.get(key, "")
	if path == "":
		return
	AudioMgr.play_sfx(path)


# ── Animation + game-feel helpers ────────────────────────────────────
# Small reusable polish primitives so every state change gets visible
# audio + visual feedback. Cheap to call; safe if a target is null.

# Pulse a label's color toward `flash` and back. Used on stat changes
# (time / inertia / health) so the player SEES what a card did, not
# just reads it in the log.
func _pulse_label(lbl: Label, flash: Color, dur: float = 0.55) -> void:
	if lbl == null:
		return
	# Sample the effective color BEFORE applying the flash override.
	# get_theme_color returns the resolved color (override or theme),
	# avoiding the get_theme_color_override API which doesn't exist in
	# all Godot 4.x versions.
	var original: Color = lbl.get_theme_color("font_color", "Label")
	lbl.add_theme_color_override("font_color", flash)
	var t := create_tween()
	t.tween_property(lbl, "theme_override_colors/font_color", original, dur).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)


# Tween a Control's position. No-op if already at the target.
func _tween_node_to(node: Control, target: Vector2, dur: float = 0.30) -> void:
	if node == null:
		return
	if node.position.distance_to(target) < 0.5:
		node.position = target
		return
	var t := create_tween()
	t.tween_property(node, "position", target, dur).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)


# Brief overlay toast near the top of the screen — fades in then out.
# Used for milestone awards (BUNDLE in hand, LEAP unlocked, visitor
# connected, lore token gained, item picked up).
func _show_toast(text: String, accent_hex: String = "#c8a268") -> void:
	var view: Vector2 = get_viewport_rect().size
	var pop := PanelContainer.new()
	pop.add_theme_stylebox_override("panel", _make_panel_style())
	pop.z_index = 200
	pop.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(pop)
	var rt := RichTextLabel.new()
	rt.bbcode_enabled = true
	rt.fit_content = true
	rt.add_theme_color_override("default_color", Color(0.92, 0.88, 0.78))
	rt.add_theme_font_size_override("normal_font_size", 14)
	rt.text = "[color=%s]✦[/color]  %s" % [accent_hex, text]
	pop.add_child(rt)
	await get_tree().process_frame
	pop.position = Vector2((view.x - pop.size.x) * 0.5, 80.0)
	pop.modulate = Color(1, 1, 1, 0)
	var t := create_tween()
	t.tween_property(pop, "modulate:a", 1.0, 0.18).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	t.tween_interval(2.0)
	t.tween_property(pop, "modulate:a", 0.0, 0.45).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	t.tween_callback(pop.queue_free)


# Brief scale pulse — pump a button up to 1.10x and back. Used on
# card play so the click registers visually.
func _pulse_button(btn: BaseButton) -> void:
	if btn == null:
		return
	btn.pivot_offset = btn.size * 0.5
	var t := create_tween()
	t.tween_property(btn, "scale", Vector2(1.10, 1.10), 0.08).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	t.tween_property(btn, "scale", Vector2(1.0, 1.0), 0.16).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)


# Hover scale — bound to a button's mouse_entered/exited signals so
# hand and tableau cards lift slightly under the cursor.
func _hover_scale(btn: BaseButton, up: bool) -> void:
	if btn == null:
		return
	btn.pivot_offset = btn.size * 0.5
	var t := create_tween()
	t.tween_property(btn, "scale", Vector2(1.06, 1.06) if up else Vector2(1.0, 1.0), 0.10).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)


# ── Art loading helpers ─────────────────────────────────────────────
# All gauntlet art lives under res://assets/gallery/... at the paths
# the gauntlet_studio.html tool writes. _load_texture_silent returns
# null if the file isn't there (so missing art doesn't crash or spam
# red errors — the renderer falls back to text).

func _load_texture_silent(path: String) -> Texture2D:
	if path == "":
		return null
	if not path.begins_with("res://"):
		path = "res://" + path
	if not ResourceLoader.exists(path):
		return null
	var t := ResourceLoader.load(path) as Texture2D
	return t

func _art_path_card(cid: String) -> String:
	# Framework cards (shared across every arcana) live at
	#   assets/gallery/cards/framework_<id>.png
	# Arcana-unique cards at:
	#   assets/gallery/cards/<arcana>_<id>.png
	# Framework cards in _action_cards always have a "double_success"
	# field; arcana cards use the "effects" key instead.
	var card: Dictionary = _action_cards.get(cid, {})
	if card.has("double_success") or card.has("passive_effect"):
		return "res://assets/gallery/cards/framework_" + cid + ".png"
	return "res://assets/gallery/cards/" + _arcana_id + "_" + cid + ".png"

func _art_path_gravity(cid: String) -> String:
	return "res://assets/gallery/cards/" + _arcana_id + "_gravity_" + cid + ".png"

func _art_path_item(item_id: String) -> String:
	return "res://assets/gallery/items/" + _arcana_id + "_" + item_id + ".png"

func _art_path_visitor_face(vid: String) -> String:
	return "res://assets/gallery/" + vid + "_face.png"

func _art_path_board() -> String:
	return "res://assets/gallery/locations/" + _location_id + "_gauntlet_board.png"

func _art_path_meeple(id: String) -> String:
	return "res://assets/gallery/meeples/" + id + ".png"


# ── Data loading ─────────────────────────────────────────────────────

func _load_json(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		push_error("Gauntlet: missing data file: " + path)
		return {}
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("Gauntlet: bad JSON shape in " + path)
		return {}
	return parsed


func _load_data() -> void:
	var arc_root := DATA_ROOT + _arcana_id + "/"
	print("[Gauntlet] loading data from %s" % arc_root)
	_setup           = _load_json(arc_root + "setup_the_leap.json")
	_gravity_deck_def = _load_json(arc_root + "gravity_deck.json")
	_finale_def      = _load_json(arc_root + "finale.json")
	_die             = _load_json(arc_root + "die.json")
	# Merge core + arcana-unique action cards into a flat dict by id
	var core_deck := _load_json(FRAMEWORK_CORE)
	var arc_deck  := _load_json(arc_root + "action_cards.json")
	for c: Dictionary in core_deck.get("cards", []):
		_action_cards[c["id"]] = c
	for c: Dictionary in arc_deck.get("cards", []):
		_action_cards[c["id"]] = c
	# Visitors → id-keyed dict
	var v_def := _load_json(arc_root + "visitors.json")
	for v: Dictionary in v_def.get("visitors", []):
		_visitors_def[v["id"]] = v
	# Items + piles
	var i_def := _load_json(arc_root + "items.json")
	_piles_def = i_def.get("piles", {})
	_items_def = i_def.get("items", {})
	# Location + hand
	_location = _load_json(DATA_ROOT + "locations/" + _location_id + ".json")
	_hand     = _load_json(DATA_ROOT + "hands/"     + _hand_id     + ".json")
	# Diagnostic summary — surfaces in Godot's Output console.
	print("[Gauntlet] loaded:")
	print("    setup: %s starting_hand=%s" % [
		"OK" if not _setup.is_empty() else "MISSING",
		str((_setup.get("starting_state", {}) as Dictionary).get("starting_hand", [])),
	])
	print("    action cards: %d (core+arcana, ids: %s)" %
		[_action_cards.size(), str(_action_cards.keys())])
	print("    gravity cards: %d" % (_gravity_deck_def.get("cards", []) as Array).size())
	print("    visitors: %d" % _visitors_def.size())
	print("    piles: %s" % str(_piles_def.keys()))
	print("    location spaces: %d" % (_location.get("spaces", []) as Array).size())
	print("    hand: %s" % _hand.get("name", "MISSING"))
	print("    die faces: %d" % ((_die.get("die", {}) as Dictionary).get("faces", []) as Array).size())


# ── Run initialization ──────────────────────────────────────────────

func _init_run() -> void:
	var start: Dictionary = _setup.get("starting_state", {})
	_player_pos = start.get("player_pos", "counter")
	_places_visited[_player_pos] = true
	_time       = int(start.get("time", 4))
	_next_time_reset = int(start.get("time_per_turn", _time))
	_inertia    = int(start.get("inertia", 0))
	_health     = int(start.get("health", 5))
	_hand_cards = (start.get("starting_hand", []) as Array).duplicate()

	# Visitors: place those marked on_board_at_start; queue scheduled ones
	for vid in _visitors_def:
		var v: Dictionary = _visitors_def[vid]
		var arr: Dictionary = v.get("arrival", {})
		match arr.get("kind", ""):
			"on_board_at_start":
				_visitors_state[vid] = {
					"pos": arr.get("pos", "counter"),
					"arrived": true,
					"connected": false,
					"claimed_turn": -1,
				}
			"scheduled":
				_visitors_state[vid] = {
					"pos": "",
					"arrived": false,
					"scheduled_turn": int(arr.get("turn", 99)),
					"arrival_pos": arr.get("to", "counter"),
					"connected": false,
					"claimed_turn": -1,
				}
			"conditional":
				_visitors_state[vid] = {
					"pos": "",
					"arrived": false,
					"connected": false,
					"claimed_turn": -1,
					"condition": arr,
				}

	# Item piles: copy the items[] array so we can pop from it
	for pid in _piles_def:
		_pile_state[pid] = (_piles_def[pid].get("items", []) as Array).duplicate()

	# Shuffle Gravity deck
	_gravity_draw_pile = []
	for c: Dictionary in _gravity_deck_def.get("cards", []):
		_gravity_draw_pile.append(c["id"])
	_gravity_draw_pile.shuffle()


# ── UI build ─────────────────────────────────────────────────────────

func _build_ui() -> void:
	_bg = ColorRect.new()
	_bg.color = C_BG
	_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_bg)

	# ── Top tracks bar ───────────────────────────────────────────────
	var top := PanelContainer.new()
	top.set_anchors_preset(Control.PRESET_TOP_WIDE)
	top.offset_top = 6
	top.offset_left = 8
	top.offset_right = -8
	top.offset_bottom = 44
	top.add_theme_stylebox_override("panel", _make_panel_style())
	add_child(top)
	var top_hb := HBoxContainer.new()
	top_hb.add_theme_constant_override("separation", 24)
	top.add_child(top_hb)
	_turn_label     = _make_track_label("Turn 1")
	_time_label     = _make_track_label("Time 6 / 6")
	_inertia_label  = _make_track_label("Inertia 0 / 12")
	_health_label   = _make_track_label("Health 5")
	_phase_label    = _make_track_label("PHASE: ACTION")
	# Click the phase label → open How to Play modal. Tooltip updated
	# every render to describe what to do in the current phase.
	_phase_label.mouse_filter = Control.MOUSE_FILTER_STOP
	_phase_label.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	_phase_label.tooltip_text = _phase_what_now(_phase) + "\n\n(Click for full rules.)"
	_phase_label.gui_input.connect(func(ev: InputEvent) -> void:
		if ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed and (ev as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT:
			_open_pane_modal("How to Play — Phases", _build_phase_help_modal_body))
	_player_pos_label = _make_track_label("at: counter")
	_bindle_label   = _make_track_label("Bindle: —")
	for lbl in [_phase_label, _turn_label, _time_label, _inertia_label, _health_label, _player_pos_label, _bindle_label]:
		top_hb.add_child(lbl)

	# ── Left/center: location board ──────────────────────────────────
	# PRESET_FULL_RECT anchors right edge to parent's right (anchor=1),
	# so offset_right=-440 leaves a 440px gutter for the right column.
	# (Was PRESET_LEFT_WIDE, which anchors BOTH edges to the parent's
	# LEFT edge — offset_right=-440 then put the right edge at x=-440,
	# giving a negative-width rect that rendered as nothing. That's
	# why fullscreen worked (uses FULL_RECT) but normal mode was black.)
	_board_root = Control.new()
	_board_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_board_root.offset_top = 52
	_board_root.offset_left = 8
	_board_root.offset_bottom = -266
	_board_root.offset_right = -440
	# Outer panel + stylebox so the board reads as its own window.
	var board_panel := PanelContainer.new()
	board_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	board_panel.add_theme_stylebox_override("panel", _make_panel_style())
	board_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_board_root.add_child(board_panel)
	add_child(_board_root)
	# Header bar — title + fullscreen toggle. Pinned to the top of
	# the board area so the board has its own visible "window" with
	# a label, like every other panel in the layout.
	var board_header := PanelContainer.new()
	board_header.set_anchors_preset(Control.PRESET_TOP_WIDE)
	board_header.offset_top = 0
	board_header.offset_left = 0
	board_header.offset_right = 0
	board_header.offset_bottom = 26
	board_header.add_theme_stylebox_override("panel", _make_panel_style())
	board_header.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_board_root.add_child(board_header)
	var header_hb := HBoxContainer.new()
	header_hb.add_theme_constant_override("separation", 6)
	board_header.add_child(header_hb)
	var board_title := Label.new()
	board_title.text = "  MAP — " + String(_location.get("title", _location_id))
	board_title.add_theme_color_override("font_color", C_ACCENT)
	board_title.add_theme_font_size_override("font_size", 11)
	board_title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header_hb.add_child(board_title)
	_board_expand_btn = Button.new()
	_board_expand_btn.text = "⛶"
	_board_expand_btn.tooltip_text = "Expand board (fullscreen)"
	_board_expand_btn.add_theme_font_size_override("font_size", 12)
	_board_expand_btn.custom_minimum_size = Vector2(28, 20)
	_board_expand_btn.pressed.connect(_toggle_board_fullscreen)
	header_hb.add_child(_board_expand_btn)
	# Content area BELOW the header — board image, markers, labels,
	# meeples all live here so they don't draw over the title bar.
	# Re-renders on resize so layout-time size is correct (initial
	# _render_board() in _build_ui runs before layout, when size=0).
	_board_content = Control.new()
	_board_content.set_anchors_preset(Control.PRESET_FULL_RECT)
	_board_content.offset_top = 28
	_board_content.offset_left = 4
	_board_content.offset_right = -4
	_board_content.offset_bottom = -4
	_board_content.clip_contents = true
	_board_content.resized.connect(_render_board)
	_board_root.add_child(_board_content)

	# ── Right column: codex card + gravity card + visitor states + log
	var right := VBoxContainer.new()
	right.set_anchors_preset(Control.PRESET_RIGHT_WIDE)
	right.offset_top = 52
	right.offset_right = -8
	right.offset_left = -432
	right.offset_bottom = -266
	right.add_theme_constant_override("separation", 6)
	add_child(right)

	# Codex card (the gallery image, pinned) — fixed size, NOT expand_fill
	# (was eating all the right-column height and squeezing the log to
	# nothing).
	# INVENTORY panel — replaces the old CODEX thumbnail (which was
	# just decorative duplication of the gallery card). Shows what
	# the player has actually picked up, with item art if present
	# and a clear BINDLE assembly indicator at the top.
	var inv_panel := PanelContainer.new()
	inv_panel.add_theme_stylebox_override("panel", _make_panel_style())
	inv_panel.custom_minimum_size = Vector2(420, 170)
	var inv_vb := VBoxContainer.new()
	inv_panel.add_child(inv_vb)
	inv_vb.add_child(_make_pane_header("INVENTORY / BINDLE", "inventory"))
	var inv_scroll := ScrollContainer.new()
	inv_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	inv_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	inv_vb.add_child(inv_scroll)
	_inv_box = VBoxContainer.new()
	_inv_box.add_theme_constant_override("separation", 3)
	_inv_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	inv_scroll.add_child(_inv_box)
	right.add_child(inv_panel)

	# Gravity card display — single thin line. Shows deck size before
	# any draw ("Gravity deck: 12 remaining"), then the drawn card's
	# title + flavor.
	var grav_panel := PanelContainer.new()
	grav_panel.add_theme_stylebox_override("panel", _make_panel_style())
	grav_panel.custom_minimum_size = Vector2(420, 72)
	var grav_vb := VBoxContainer.new()
	grav_panel.add_child(grav_vb)
	grav_vb.add_child(_make_pane_header("GRAVITY", "gravity"))
	_gravity_card_label = RichTextLabel.new()
	_gravity_card_label.bbcode_enabled = true
	_gravity_card_label.fit_content = true
	_gravity_card_label.add_theme_color_override("default_color", C_TEXT)
	_gravity_card_label.text = "[color=#c8a268]Deck[/color] — 12 cards remaining"
	grav_vb.add_child(_gravity_card_label)
	right.add_child(grav_panel)

	# Visitors — gets the freed vertical space from the relocated log
	# Wrapped in a ScrollContainer so multi-line hints can't push the
	# panel taller than its allotted column space.
	var v_panel := PanelContainer.new()
	v_panel.add_theme_stylebox_override("panel", _make_panel_style())
	v_panel.custom_minimum_size = Vector2(420, 120)
	v_panel.size_flags_vertical = Control.SIZE_EXPAND_FILL
	var v_vb := VBoxContainer.new()
	v_panel.add_child(v_vb)
	v_vb.add_child(_make_pane_header("VISITORS", "visitors"))
	var v_scroll := ScrollContainer.new()
	v_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	v_vb.add_child(v_scroll)
	_visitors_box = VBoxContainer.new()
	_visitors_box.add_theme_constant_override("separation", 3)
	_visitors_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	v_scroll.add_child(_visitors_box)
	right.add_child(v_panel)

	# Log moved OUT of the right column — it now lives in the bottom
	# strip alongside the hand. See bottom panel below.

	# ── Bottom strip: LOG (left, wide) + cards stack (right) ──────
	# Layout request: log on top of the bottom area, hand runs flush
	# into it on the right. So the bottom is one HBox — log fills
	# most of the width, the card stack (tableau row above hand row)
	# sits flush against its right edge.
	var bottom := PanelContainer.new()
	bottom.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	bottom.offset_top = -262
	bottom.offset_left = 8
	bottom.offset_right = -8
	bottom.offset_bottom = -6
	bottom.add_theme_stylebox_override("panel", _make_panel_style())
	add_child(bottom)
	var bottom_hb := HBoxContainer.new()
	bottom_hb.add_theme_constant_override("separation", 6)
	bottom.add_child(bottom_hb)

	# Left: log (takes the spare horizontal space)
	var log_vb := VBoxContainer.new()
	log_vb.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	log_vb.size_flags_vertical = Control.SIZE_EXPAND_FILL
	bottom_hb.add_child(log_vb)
	log_vb.add_child(_make_pane_header("LOG", "log"))
	var log_panel := PanelContainer.new()
	log_panel.add_theme_stylebox_override("panel", _make_panel_style())
	log_panel.size_flags_vertical = Control.SIZE_EXPAND_FILL
	log_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_log = RichTextLabel.new()
	_log.bbcode_enabled = true
	_log.scroll_following = true
	_log.add_theme_color_override("default_color", C_TEXT)
	log_panel.add_child(_log)
	log_vb.add_child(log_panel)

	# Right: tableau (top) + hand (bottom), flush against the log
	var cards_vb := VBoxContainer.new()
	cards_vb.add_theme_constant_override("separation", 3)
	cards_vb.custom_minimum_size = Vector2(540, 0)
	cards_vb.size_flags_vertical = Control.SIZE_EXPAND_FILL
	bottom_hb.add_child(cards_vb)

	# Tableau row (shop)
	var tableau_title_hb := HBoxContainer.new()
	cards_vb.add_child(tableau_title_hb)
	var tableau_label := Label.new()
	tableau_label.text = "  TABLEAU  · click to buy in planning"
	tableau_label.add_theme_color_override("font_color", C_ACCENT)
	tableau_label.add_theme_font_size_override("font_size", 10)
	tableau_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	tableau_title_hb.add_child(tableau_label)
	_tableau_scroll = ScrollContainer.new()
	_tableau_scroll.custom_minimum_size = Vector2(540, 104)
	_tableau_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
	_tableau_scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	cards_vb.add_child(_tableau_scroll)
	_tableau_box = HBoxContainer.new()
	_tableau_box.add_theme_constant_override("separation", 4)
	_tableau_scroll.add_child(_tableau_box)

	# Hand row
	var hand_title_hb := HBoxContainer.new()
	cards_vb.add_child(hand_title_hb)
	var hand_label := Label.new()
	hand_label.text = "  HAND"
	hand_label.add_theme_color_override("font_color", C_ACCENT)
	hand_label.add_theme_font_size_override("font_size", 10)
	hand_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hand_title_hb.add_child(hand_label)
	var move_btn := Button.new()
	move_btn.text = "Move ↪"
	move_btn.add_theme_font_size_override("font_size", 11)
	move_btn.tooltip_text = "Pick an adjacent space to walk to (costs 1 Time, action phase only)."
	move_btn.pressed.connect(_show_move_popup)
	hand_title_hb.add_child(move_btn)
	_advance_btn = Button.new()
	_advance_btn.text = "Advance →"
	_advance_btn.add_theme_font_size_override("font_size", 11)
	_advance_btn.pressed.connect(_on_advance)
	hand_title_hb.add_child(_advance_btn)
	var close_btn := Button.new()
	close_btn.text = "Leave"
	close_btn.add_theme_font_size_override("font_size", 11)
	close_btn.pressed.connect(_on_leave)
	hand_title_hb.add_child(close_btn)
	var hand_scroll := ScrollContainer.new()
	hand_scroll.custom_minimum_size = Vector2(540, 104)
	hand_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
	hand_scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	cards_vb.add_child(hand_scroll)
	_hand_box = HBoxContainer.new()
	_hand_box.add_theme_constant_override("separation", 4)
	hand_scroll.add_child(_hand_box)


func _make_panel_style() -> StyleBoxFlat:
	var st := StyleBoxFlat.new()
	st.bg_color = C_PANEL
	st.border_color = C_BORDER
	st.set_border_width_all(1)
	st.set_corner_radius_all(3)
	st.content_margin_left = 8
	st.content_margin_right = 8
	st.content_margin_top = 4
	st.content_margin_bottom = 4
	return st


# Header row with a title label + a small ⛶ expand button. Used at
# the top of every right-column pane so clicking the button opens a
# detailed modal of that pane's contents.
func _make_pane_header(title: String, modal_key: String) -> Control:
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 4)
	var lbl := Label.new()
	lbl.text = "  " + title
	lbl.add_theme_color_override("font_color", C_ACCENT)
	lbl.add_theme_font_size_override("font_size", 11)
	lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hb.add_child(lbl)
	# Remember the title label so unread badges (e.g. log "(3 new)")
	# can be set later.
	_pane_title_labels[modal_key] = lbl
	var btn := Button.new()
	btn.text = "⛶"
	btn.tooltip_text = "Expand " + title + " (Esc to close)"
	btn.add_theme_font_size_override("font_size", 10)
	btn.custom_minimum_size = Vector2(26, 18)
	# bind(modal_key) wraps the String into a Callable arg — avoids any
	# closure-capture weirdness from inline lambdas inside add_child().
	btn.pressed.connect(_open_pane_modal_by_key.bind(modal_key))
	hb.add_child(btn)
	return hb


# Dispatch a pane-expand request to the correct title + body builder.
# Used as the connect target from _make_pane_header so the closure is
# the well-known bind() form, not an inline multi-line lambda.
func _open_pane_modal_by_key(key: String) -> void:
	match key:
		"log":
			_open_pane_modal("Full Log", _build_log_modal_body)
		"inventory":
			_open_pane_modal("Inventory & Bindle", _build_inventory_modal_body)
		"gravity":
			_open_pane_modal("Gravity Deck", _build_gravity_modal_body)
		"visitors":
			_open_pane_modal("Visitors", _build_visitors_modal_body)


# Generic pane modal — dim background, centered panel with a header
# (title + ✕ close) and a scrollable body built by the caller.
# Click outside the panel or the ✕ button to dismiss.
func _close_pane_modal(dim: ColorRect) -> void:
	if dim == null or not is_instance_valid(dim):
		return
	var t := create_tween()
	t.tween_property(dim, "modulate:a", 0.0, 0.14).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	t.tween_callback(dim.queue_free)


func _open_pane_modal(title: String, body_builder: Callable) -> void:
	# Tear down any existing modal first so stacked opens can't trap input.
	var existing: Node = get_node_or_null("pane_modal_dim")
	if existing != null and is_instance_valid(existing):
		existing.queue_free()
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.75)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_STOP
	dim.z_index = 100
	dim.name = "pane_modal_dim"
	dim.modulate = Color(1, 1, 1, 0)
	dim.gui_input.connect(_on_modal_dim_input.bind(dim))
	add_child(dim)
	var fade_in := create_tween()
	fade_in.tween_property(dim, "modulate:a", 1.0, 0.14).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	var view: Vector2 = get_viewport_rect().size
	var pop := PanelContainer.new()
	pop.add_theme_stylebox_override("panel", _make_panel_style())
	pop.size = Vector2(view.x * 0.72, view.y * 0.72)
	pop.position = (view - pop.size) * 0.5
	pop.mouse_filter = Control.MOUSE_FILTER_STOP
	pop.name = "pane_modal_panel"
	dim.add_child(pop)
	var pop_vb := VBoxContainer.new()
	pop_vb.add_theme_constant_override("separation", 6)
	pop.add_child(pop_vb)
	var header := HBoxContainer.new()
	var title_lbl := Label.new()
	title_lbl.text = "  " + title
	title_lbl.add_theme_color_override("font_color", C_ACCENT)
	title_lbl.add_theme_font_size_override("font_size", 16)
	title_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(title_lbl)
	# Prominent close button — explicit ✕ Close text + ESC hint.
	var close := Button.new()
	close.text = "✕  Close  (Esc)"
	close.add_theme_font_size_override("font_size", 13)
	close.custom_minimum_size = Vector2(140, 28)
	close.pressed.connect(_close_pane_modal.bind(dim))
	header.add_child(close)
	pop_vb.add_child(header)
	pop_vb.add_child(HSeparator.new())
	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	pop_vb.add_child(scroll)
	var body: Control = body_builder.call() as Control
	if body != null:
		body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		scroll.add_child(body)


# Dim background click handler — closes the modal when clicking
# outside the centered panel.
func _on_modal_dim_input(ev: InputEvent, dim: ColorRect) -> void:
	if ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed:
		_close_pane_modal(dim)


# ── Card view modal ─────────────────────────────────────────────────
# Clicking a hand or tableau card opens this fullscreen-ish view:
# big art on the left, title + cost + flavor + effect summary on the
# right, with a prominent action button (▶ Play or ✦ Buy) and Cancel.
# Closes via the button, ✕, Esc, or click outside.
func _open_card_view(cid: String, mode: String) -> void:
	var card: Dictionary = _action_cards.get(cid, {})
	if card.is_empty():
		return
	# Tear down any existing modal so stacked opens can't trap input
	var existing: Node = get_node_or_null("pane_modal_dim")
	if existing != null and is_instance_valid(existing):
		existing.queue_free()
	# Dim background
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.82)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_STOP
	dim.z_index = 100
	dim.name = "pane_modal_dim"
	dim.modulate = Color(1, 1, 1, 0)
	dim.gui_input.connect(_on_modal_dim_input.bind(dim))
	add_child(dim)
	var fade_in := create_tween()
	fade_in.tween_property(dim, "modulate:a", 1.0, 0.14).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)

	# Centered horizontal panel
	var view: Vector2 = get_viewport_rect().size
	var pop := PanelContainer.new()
	pop.add_theme_stylebox_override("panel", _make_panel_style())
	pop.size = Vector2(min(view.x * 0.78, 940.0), min(view.y * 0.82, 640.0))
	pop.position = (view - pop.size) * 0.5
	pop.mouse_filter = Control.MOUSE_FILTER_STOP
	dim.add_child(pop)

	var root := HBoxContainer.new()
	root.add_theme_constant_override("separation", 18)
	pop.add_child(root)

	# Left column: card art panel (5:7 framing)
	var art_panel := PanelContainer.new()
	art_panel.add_theme_stylebox_override("panel", _make_panel_style())
	art_panel.custom_minimum_size = Vector2(380, 532)
	root.add_child(art_panel)
	var art_tex: Texture2D = _load_texture_silent(_art_path_card(cid))
	if art_tex:
		var img := TextureRect.new()
		img.texture = art_tex
		img.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		img.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		img.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		img.size_flags_vertical = Control.SIZE_EXPAND_FILL
		art_panel.add_child(img)
	else:
		var ph := Label.new()
		ph.text = "(no art yet — use the studio to generate)"
		ph.add_theme_color_override("font_color", Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.4))
		ph.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		ph.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		ph.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		art_panel.add_child(ph)

	# Right column: info + action buttons
	var info := VBoxContainer.new()
	info.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	info.size_flags_vertical = Control.SIZE_EXPAND_FILL
	info.add_theme_constant_override("separation", 10)
	root.add_child(info)

	var title := Label.new()
	title.text = card.get("title", cid)
	title.add_theme_color_override("font_color", C_ACCENT)
	title.add_theme_font_size_override("font_size", 26)
	info.add_child(title)

	var cost: int = int(card.get("time_cost", 1))
	var price: int = _buy_price(card) if mode == "buy" else cost
	var cost_line := RichTextLabel.new()
	cost_line.bbcode_enabled = true
	cost_line.fit_content = true
	cost_line.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	cost_line.add_theme_color_override("default_color", C_TEXT)
	cost_line.add_theme_font_size_override("normal_font_size", 13)
	if mode == "buy":
		cost_line.text = "[b]Buy:[/b] %d Time     [b]Plays for:[/b] %d Time" % [price, cost]
	else:
		cost_line.text = "[b]Cost:[/b] %d Time" % cost
	info.add_child(cost_line)

	var flavor_label: String = String(card.get("flavor", ""))
	if flavor_label != "":
		var flavor := RichTextLabel.new()
		flavor.bbcode_enabled = true
		flavor.fit_content = true
		flavor.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		flavor.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		flavor.add_theme_color_override("default_color", Color(0.86, 0.82, 0.74))
		flavor.add_theme_font_size_override("normal_font_size", 13)
		flavor.text = "[i]" + flavor_label + "[/i]"
		info.add_child(flavor)

	info.add_child(HSeparator.new())

	var eff_title := Label.new()
	eff_title.text = "  EFFECT"
	eff_title.add_theme_color_override("font_color", C_ACCENT)
	eff_title.add_theme_font_size_override("font_size", 12)
	info.add_child(eff_title)
	var effects := RichTextLabel.new()
	effects.bbcode_enabled = true
	effects.fit_content = true
	effects.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	effects.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	effects.add_theme_color_override("default_color", C_TEXT)
	effects.add_theme_font_size_override("normal_font_size", 12)
	var summary: String = _card_summary(card)
	if summary == "":
		summary = "(no mechanical effect — flavor-only)"
	effects.text = summary
	info.add_child(effects)

	# Spacer pushes the action row to the bottom
	var spacer := Control.new()
	spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	info.add_child(spacer)

	# Action row
	var actions := HBoxContainer.new()
	actions.add_theme_constant_override("separation", 10)
	info.add_child(actions)
	var cancel := Button.new()
	cancel.text = "✕  Cancel  (Esc)"
	cancel.add_theme_font_size_override("font_size", 13)
	cancel.custom_minimum_size = Vector2(130, 36)
	cancel.pressed.connect(_close_pane_modal.bind(dim))
	actions.add_child(cancel)
	var spacer2 := Control.new()
	spacer2.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	actions.add_child(spacer2)

	var can_act: bool = false
	var act_label: String = ""
	if mode == "play":
		can_act = _can_play_card(card) and (_phase == Phase.ACTION) and (_time >= cost) and not _game_over
		act_label = "▶  Play  (%d Time)" % cost
	else:
		can_act = (_phase == Phase.PLANNING) and (_time >= price) and not _game_over
		act_label = "✦  Buy  (%d Time)" % price
	var act_btn := Button.new()
	act_btn.text = act_label
	act_btn.add_theme_font_size_override("font_size", 14)
	act_btn.custom_minimum_size = Vector2(180, 36)
	act_btn.disabled = not can_act
	# Modal owns the play/buy — close modal first, then resolve the
	# card so the player sees their stat pulses + meeple tween
	# happen in the now-clean main view.
	act_btn.pressed.connect(func() -> void:
		_close_pane_modal(dim)
		if mode == "play":
			_on_play_card(cid)
		else:
			_on_buy_card(cid))
	actions.add_child(act_btn)


func _make_track_label(text: String) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_color_override("font_color", C_TEXT)
	l.add_theme_font_size_override("font_size", 12)
	return l


# ── Board rendering ──────────────────────────────────────────────────

func _render_board() -> void:
	if _board_content == null:
		return
	# Clear — content control owns bg, markers, labels, meeples.
	for c in _board_content.get_children():
		c.queue_free()
	_board_space_nodes.clear()
	_board_visitor_nodes.clear()
	# Background image layer (rendered first so labels draw on top).
	# If the location-specific board art is missing, fall back to the
	# bare grid we used to render.
	var bg_tex: Texture2D = _load_texture_silent(_art_path_board())
	if bg_tex:
		var bg := TextureRect.new()
		bg.name = "board_bg"
		bg.texture = bg_tex
		bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		# STRETCH_SCALE (not KEEP_ASPECT) so the image fills the panel
		# exactly — labels are positioned in the same panel rect, so
		# they only align with the painted stations when the image
		# covers the same rect.
		bg.stretch_mode = TextureRect.STRETCH_SCALE
		# Low alpha — the AI-generated board image's painted stations
		# rarely line up with the JSON's pos_xy coordinates. Treat the
		# image as ATMOSPHERIC TEXTURE / mood, not a literal map. The
		# engine-drawn markers + adjacency lines are the authoritative
		# board.
		bg.modulate = Color(1, 1, 1, 0.20)
		bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_board_content.add_child(bg)
	# Draw spaces as labels positioned per the JSON's pos_xy.
	# Coordinates are in the JSON's coordinate space; we scale to fit
	# the board panel's actual size.
	var spaces: Array = _location.get("spaces", [])
	# Find bounds
	var bx_min := INF
	var bx_max := -INF
	var by_min := INF
	var by_max := -INF
	for s: Dictionary in spaces:
		var xy: Array = s.get("pos_xy", [0, 0])
		bx_min = minf(bx_min, float(xy[0]))
		bx_max = maxf(bx_max, float(xy[0]))
		by_min = minf(by_min, float(xy[1]))
		by_max = maxf(by_max, float(xy[1]))
	var panel_size: Vector2 = _board_content.size
	if panel_size.x <= 0:
		panel_size = Vector2(700, 480)
	var sx: float = (panel_size.x - 80) / maxf(1.0, bx_max - bx_min)
	var sy: float = (panel_size.y - 60) / maxf(1.0, by_max - by_min)
	# Compute every station's screen position upfront so we can draw
	# adjacency lines below them.
	var pos_by_id: Dictionary = {}
	var visible_ids: Dictionary = {}
	for s: Dictionary in spaces:
		var sid_p: String = s.get("id", "")
		if not s.get("always_visible", true) and sid_p != "precipice_door":
			continue
		if sid_p == "precipice_door" and not _flags.get("precipice_revealed", false):
			continue
		var xy_p: Array = s.get("pos_xy", [0, 0])
		var px: float = (float(xy_p[0]) - bx_min) * sx + 40.0
		var py: float = (float(xy_p[1]) - by_min) * sy + 30.0
		pos_by_id[sid_p] = Vector2(px, py)
		visible_ids[sid_p] = true
	# Adjacency lines layer — drawn FIRST so markers + labels sit on top.
	var lines := BoardLinesLayer.new()
	lines.name = "adj_lines"
	lines.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	lines.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var adj_map: Dictionary = _location.get("adjacency", {})
	var seen_edges: Dictionary = {}
	for from_id: String in adj_map.keys():
		if not pos_by_id.has(from_id):
			continue
		for to_id: String in adj_map[from_id]:
			if not pos_by_id.has(to_id):
				continue
			var a: String = from_id
			var b: String = to_id
			if b < a:
				var t: String = a; a = b; b = t
			var key: String = a + "|" + b
			if seen_edges.has(key):
				continue
			seen_edges[key] = true
			lines.adj_pairs.append([pos_by_id[from_id], pos_by_id[to_id]])
	_board_content.add_child(lines)
	for s: Dictionary in spaces:
		var sid: String = s.get("id", "")
		if not visible_ids.has(sid):
			continue
		var nx: float = pos_by_id[sid].x
		var ny: float = pos_by_id[sid].y
		# Node marker: small filled disc/diamond at each station so
		# the board reads as a board even without/with the bg image.
		var marker := Panel.new()
		marker.name = "marker_" + sid
		marker.mouse_filter = Control.MOUSE_FILTER_STOP
		marker.tooltip_text = _tooltip_for_space(s)
		marker.custom_minimum_size = Vector2(12, 12)
		marker.size = Vector2(12, 12)
		marker.position = Vector2(nx - 6, ny - 6)
		var mst := StyleBoxFlat.new()
		var kind: String = s.get("kind", "named")
		match kind:
			"threshold": mst.bg_color = Color(0.55, 0.95, 0.65, 0.9)
			"search":    mst.bg_color = Color(0.95, 0.78, 0.40, 0.9)
			_:           mst.bg_color = Color(0.82, 0.78, 0.70, 0.8)
		mst.border_color = Color(0, 0, 0, 0.8)
		mst.set_border_width_all(1)
		mst.set_corner_radius_all(6)
		marker.add_theme_stylebox_override("panel", mst)
		_board_content.add_child(marker)
		var node := _make_space_label(s)
		node.position = Vector2(nx + 10.0, ny - 8.0)
		node.name = "space_" + sid
		_board_content.add_child(node)
		_board_space_nodes[sid] = node
	# Player meeple — image if present, otherwise styled label.
	var player_art: Texture2D = _load_texture_silent(_art_path_meeple("john"))
	if player_art:
		var mp := TextureRect.new()
		mp.texture = player_art
		mp.custom_minimum_size = Vector2(28, 28)
		mp.size = Vector2(28, 28)
		mp.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		mp.name = "player_meeple"
		_board_meeple = mp
	else:
		var lbl_m := Label.new()
		lbl_m.text = "★"
		lbl_m.add_theme_color_override("font_color", C_ACCENT)
		lbl_m.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1))
		lbl_m.add_theme_constant_override("outline_size", 4)
		lbl_m.add_theme_font_size_override("font_size", 18)
		lbl_m.name = "player_meeple"
		_board_meeple = lbl_m
	_board_meeple.tooltip_text = _tooltip_for_player()
	_board_meeple.mouse_filter = Control.MOUSE_FILTER_STOP
	_board_content.add_child(_board_meeple)
	# Visitor meeples — image if present, otherwise small colored dot.
	for vid in _visitors_state:
		var v: Dictionary = _visitors_state[vid]
		if not v.get("arrived", false):
			continue
		var vdef: Dictionary = _visitors_def[vid]
		var vis_art: Texture2D = _load_texture_silent(_art_path_meeple(vid))
		var vnode: Control
		if vis_art:
			var vm := TextureRect.new()
			vm.texture = vis_art
			vm.custom_minimum_size = Vector2(22, 22)
			vm.size = Vector2(22, 22)
			vm.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
			vnode = vm
		else:
			var dot := Label.new()
			dot.text = "●"
			dot.add_theme_color_override("font_color", Color(vdef.get("accent", "#c8a268")))
			dot.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1))
			dot.add_theme_constant_override("outline_size", 3)
			dot.add_theme_font_size_override("font_size", 14)
			vnode = dot
		vnode.name = "visitor_" + vid
		vnode.tooltip_text = _tooltip_for_visitor(vid)
		vnode.mouse_filter = Control.MOUSE_FILTER_STOP
		_board_content.add_child(vnode)
		_board_visitor_nodes[vid] = vnode
	_position_meeples()


func _make_space_label(s: Dictionary) -> Label:
	# Clickable space label. Click → walk there if adjacent (costs 1 Time).
	# Label visibility is tiered to reduce visual clutter:
	#   · current position: full label, accent color, chevron
	#   · adjacent spaces:  full label, normal color
	#   · search piles:     full label dimmed amber
	#   · thresholds:       full label dimmed green
	#   · other named:      tiny dot only
	var l := Label.new()
	var label: String = s.get("label", s.get("id", ""))
	var sid: String = s.get("id", "")
	var kind: String = s.get("kind", "named")
	var adj: Array = (_location.get("adjacency", {}) as Dictionary).get(_player_pos, [])
	var is_here: bool = (sid == _player_pos)
	var is_adjacent: bool = (sid in adj)
	var pile := ""
	if kind == "search":
		pile = "  [%d]" % _pile_state.get(s.get("search_pile", ""), []).size()
	var col: Color = C_TEXT
	var fs: int = 10
	if is_here:
		l.text = "» " + label + pile
		col = C_ACCENT
		fs = 12
	elif is_adjacent:
		l.text = "· " + label + pile
		col = C_TEXT
		fs = 10
	elif kind == "threshold":
		l.text = label
		col = Color(0.55, 0.95, 0.65, 0.65)
		fs = 9
	elif kind == "search":
		l.text = label + pile
		col = Color(0.95, 0.78, 0.40, 0.65)
		fs = 9
	else:
		# Tiny dot only — keeps the position click-target but removes
		# the label from the visual noise floor.
		l.text = "·"
		col = Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.35)
		fs = 9
	l.add_theme_color_override("font_color", col)
	l.add_theme_font_size_override("font_size", fs)
	# Outline + slight shadow so labels read over any painted background.
	l.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	l.add_theme_constant_override("outline_size", 4)
	l.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.6))
	l.add_theme_constant_override("shadow_offset_x", 1)
	l.add_theme_constant_override("shadow_offset_y", 1)
	l.mouse_filter = Control.MOUSE_FILTER_PASS
	l.tooltip_text = _tooltip_for_space(s)
	# Make it clickable. Adjacent free-move costs 1 Time, no card needed.
	# Spaces farther away still need explicit movement cards (Walk /
	# Sprint / Step Toward / Move Player Toward Threshold).
	l.gui_input.connect(func(ev: InputEvent) -> void:
		if not (ev is InputEventMouseButton):
			return
		var mb := ev as InputEventMouseButton
		if mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT:
			_on_space_clicked(sid))
	return l


func _show_move_popup() -> void:
	# Move chooser — shows the adjacent spaces so the player doesn't
	# have to know they can also click space labels on the board.
	if _phase != Phase.ACTION:
		_log_line("[i](Move only works during the Action phase.)[/i]")
		return
	if _game_over:
		return
	if _time < 1:
		_log_line("[i]not enough Time to walk[/i]")
		return
	var adj: Array = (_location.get("adjacency", {}) as Dictionary).get(_player_pos, [])
	if adj.is_empty():
		_log_line("[i]nowhere adjacent[/i]")
		return
	var popup := PopupMenu.new()
	popup.add_theme_font_size_override("font_size", 12)
	# Label by space id → printable label
	var space_label_by_id: Dictionary = {}
	for s: Dictionary in (_location.get("spaces", []) as Array):
		space_label_by_id[s.get("id", "")] = s.get("label", s.get("id", ""))
	var visible_targets: Array = []
	for nbr: String in adj:
		# Hidden threshold can't be walked into until revealed
		if nbr == "precipice_door" and not _flags.get("precipice_revealed", false):
			continue
		var pretty: String = String(space_label_by_id.get(nbr, nbr))
		popup.add_item("→ " + pretty + "   [1 Time]")
		visible_targets.append(nbr)
	if visible_targets.is_empty():
		_log_line("[i]no walkable adjacency from %s[/i]" % _player_pos)
		popup.queue_free()
		return
	add_child(popup)
	popup.id_pressed.connect(func(idx: int) -> void:
		if idx >= 0 and idx < visible_targets.size():
			_on_space_clicked(String(visible_targets[idx]))
		popup.queue_free())
	popup.close_requested.connect(func() -> void: popup.queue_free())
	popup.position = Vector2i(int(get_viewport().get_mouse_position().x),
		int(get_viewport().get_mouse_position().y))
	popup.popup()


func _toggle_board_fullscreen() -> void:
	# Expand the board to fill the whole game viewport (covering
	# the right column + bottom strip). Click again or hit Esc to
	# restore the normal three-column layout.
	_board_fullscreen = not _board_fullscreen
	if _board_fullscreen:
		_board_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		_board_root.offset_top = 52
		_board_root.offset_left = 8
		_board_root.offset_right = -8
		_board_root.offset_bottom = -8
		_board_expand_btn.text = "✕  Exit Fullscreen"
		_board_expand_btn.tooltip_text = "Restore normal layout (Esc)"
		_board_expand_btn.custom_minimum_size = Vector2(140, 22)
		_board_root.z_index = 10
	else:
		# Restore uses PRESET_FULL_RECT (same as the initial setup) —
		# PRESET_LEFT_WIDE anchors BOTH edges to the parent's LEFT
		# edge and produces a negative-width rect when offset_right
		# is negative, which is what was freezing the board.
		_board_root.set_anchors_preset(Control.PRESET_FULL_RECT)
		_board_root.offset_top = 52
		_board_root.offset_left = 8
		_board_root.offset_bottom = -266
		_board_root.offset_right = -440
		_board_expand_btn.text = "⛶"
		_board_expand_btn.tooltip_text = "Expand board (fullscreen)"
		_board_expand_btn.custom_minimum_size = Vector2(28, 20)
		_board_root.z_index = 0
	_render_board()


func _prompt_pick_destination(max_hops: int, reason: String) -> void:
	# Card-driven movement: BFS from the current position within
	# max_hops, then a PopupMenu of every reachable destination.
	# Replaces the old "auto-route to nearest threshold" behavior —
	# the player chooses where they go, every time.
	if _game_over or max_hops <= 0:
		return
	var adj_map: Dictionary = _location.get("adjacency", {})
	var dist: Dictionary = {_player_pos: 0}
	var queue: Array = [_player_pos]
	while not queue.is_empty():
		var cur: String = queue.pop_front()
		var d: int = int(dist[cur])
		if d >= max_hops:
			continue
		for nbr: String in adj_map.get(cur, []):
			if dist.has(nbr):
				continue
			if nbr == "precipice_door" and not _flags.get("precipice_revealed", false):
				continue
			dist[nbr] = d + 1
			queue.append(nbr)
	dist.erase(_player_pos)
	if dist.is_empty():
		_log_line("[i]nowhere to step from %s[/i]" % _player_pos)
		return
	var popup := PopupMenu.new()
	popup.add_theme_font_size_override("font_size", 12)
	var space_label_by_id: Dictionary = {}
	for s: Dictionary in (_location.get("spaces", []) as Array):
		space_label_by_id[s.get("id", "")] = s.get("label", s.get("id", ""))
	var keys: Array = dist.keys()
	keys.sort_custom(func(a: String, b: String) -> bool: return int(dist[a]) < int(dist[b]))
	for tid: String in keys:
		var hops: int = int(dist[tid])
		var label_s: String = String(space_label_by_id.get(tid, tid))
		var suffix: String = "" if hops == 1 else "s"
		popup.add_item("→ %s   (%d hop%s)" % [label_s, hops, suffix])
	add_child(popup)
	popup.id_pressed.connect(func(idx: int) -> void:
		if idx >= 0 and idx < keys.size():
			_player_pos = String(keys[idx])
			_places_visited[_player_pos] = true
			_audio_sfx("card_play")
			_log_line("→ %s to [b]%s[/b]" % [reason, _player_pos])
			_check_composite_connections()
			_render()
		popup.queue_free())
	popup.close_requested.connect(func() -> void: popup.queue_free())
	popup.position = Vector2i(int(get_viewport().get_mouse_position().x),
		int(get_viewport().get_mouse_position().y))
	popup.popup()


func _on_space_clicked(target_pos: String) -> void:
	if _game_over or _phase != Phase.ACTION:
		_log_line("[i](can't move outside the action phase)[/i]")
		return
	if target_pos == _player_pos:
		_log_line("[i]you're already at %s[/i]" % target_pos)
		return
	# Must be adjacent
	var adj: Array = (_location.get("adjacency", {}) as Dictionary).get(_player_pos, [])
	if not (target_pos in adj):
		_log_line("[i]%s isn't adjacent to %s — play Walk / Sprint to move farther[/i]" %
			[target_pos, _player_pos])
		return
	# Hidden threshold can't be clicked
	if target_pos == "precipice_door" and not _flags.get("precipice_revealed", false):
		_log_line("[i]you don't see a way through there yet[/i]")
		return
	# Costs 1 Time, no card consumed (free walk to adjacent).
	if _time < 1:
		_log_line("[i]not enough Time to walk[/i]")
		return
	_time -= 1
	_player_pos = target_pos
	_places_visited[_player_pos] = true
	_audio_sfx("card_play")
	_log_line("→ walked to [b]%s[/b]" % target_pos)
	_check_composite_connections()
	_render()


func _position_meeples() -> void:
	# Player at current pos — tween between rounds, don't teleport.
	if _board_meeple and _board_space_nodes.has(_player_pos):
		var anchor: Label = _board_space_nodes[_player_pos]
		var target: Vector2 = anchor.position + Vector2(0, 18)
		_tween_node_to(_board_meeple, target, 0.32)
	# Visitors at their positions — tween too
	var vid_pos_stack: Dictionary = {}   # pos → stack offset count
	for vid in _board_visitor_nodes:
		var v: Dictionary = _visitors_state[vid]
		var p: String = v.get("pos", "")
		if _board_space_nodes.has(p):
			var anchor2: Label = _board_space_nodes[p]
			var idx: int = int(vid_pos_stack.get(p, 0))
			vid_pos_stack[p] = idx + 1
			var vtarget: Vector2 = anchor2.position + Vector2(0, 36 + idx * 14)
			_tween_node_to(_board_visitor_nodes[vid], vtarget, 0.36)


# ── Hand + visitor rendering ─────────────────────────────────────────

func _render_hand() -> void:
	for c in _hand_box.get_children():
		c.queue_free()
	for cid in _hand_cards:
		var card: Dictionary = _action_cards.get(cid, {})
		var btn := Button.new()
		var time_cost: int = int(card.get("time_cost", 1))
		# Compact label — title plus cost. Art fills the rest of the
		# tile so the hand reads as cards, not a button row.
		btn.text = "%s · %dt" % [card.get("title", cid), time_cost]
		btn.add_theme_font_size_override("font_size", 10)
		btn.custom_minimum_size = Vector2(96, 96)
		btn.clip_text = true
		btn.tooltip_text = "%s — costs %d Time\n\n%s\n\n%s\n\n(Click to preview + play.)" % [
			card.get("title", cid), time_cost,
			String(card.get("flavor", "")),
			_card_summary(card)]
		var art: Texture2D = _load_texture_silent(_art_path_card(cid))
		if art:
			btn.icon = art
			btn.expand_icon = true
			btn.vertical_icon_alignment = VERTICAL_ALIGNMENT_TOP
		var playable: bool = _can_play_card(card)
		btn.disabled = (not playable) or (_phase != Phase.ACTION) or _game_over
		# Click opens the card-view modal, NOT immediate play. Play
		# happens from the modal's ▶ Play button after the user has
		# read the full card.
		btn.pressed.connect(func() -> void:
			_pulse_button(btn)
			_open_card_view(cid, "play"))
		btn.mouse_entered.connect(_hover_scale.bind(btn, true))
		btn.mouse_exited.connect(_hover_scale.bind(btn, false))
		_hand_box.add_child(btn)


# Tableau: every non-starter card in the action tableau, available for
# purchase during the Planning phase. Sorted by time cost so the cheap
# cards lead. Always visible (so the player can see what's in the shop
# from any phase), only buyable during PLANNING when the player has
# enough Time.
func _render_tableau() -> void:
	if _tableau_box == null:
		return
	for c in _tableau_box.get_children():
		c.queue_free()
	# Build list of buyable cards: anything in _action_cards that isn't
	# a starter AND isn't LEAP (LEAP doesn't get purchased — it's a
	# special card that becomes playable when conditions are met; it
	# gets added to hand automatically once BUNDLE is assembled).
	var buyables: Array = []
	for cid: String in _action_cards.keys():
		var card: Dictionary = _action_cards[cid]
		if card.get("starter", false):
			continue
		if cid == "leap" or cid == "bundle":
			continue   # milestone awards, not purchases
		buyables.append(cid)
	buyables.sort_custom(func(a: String, b: String) -> bool:
		return int(_action_cards[a].get("time_cost", 1)) < int(_action_cards[b].get("time_cost", 1)))

	for cid: String in buyables:
		var card: Dictionary = _action_cards[cid]
		var time_cost: int = int(card.get("time_cost", 1))
		var price: int = _buy_price(card)
		var btn := Button.new()
		btn.text = "%s · buy %dt" % [card.get("title", cid), price]
		btn.add_theme_font_size_override("font_size", 10)
		btn.custom_minimum_size = Vector2(96, 96)
		btn.clip_text = true
		btn.tooltip_text = "%s — buy %d Time, play %d Time\n\n%s\n\n%s\n\n(Click to preview + buy.)" % [
			card.get("title", cid), price, time_cost,
			String(card.get("flavor", "")),
			_card_summary(card)]
		var art: Texture2D = _load_texture_silent(_art_path_card(cid))
		if art:
			btn.icon = art
			btn.expand_icon = true
			btn.vertical_icon_alignment = VERTICAL_ALIGNMENT_TOP
		# Buyable during PLANNING + Time ≥ price
		var can_buy: bool = (_phase == Phase.PLANNING) and (_time >= price) and not _game_over
		btn.disabled = not can_buy
		# Dim style outside planning so it reads as preview, not shop
		if _phase != Phase.PLANNING:
			btn.modulate = Color(0.7, 0.65, 0.55, 0.7)
		# Click opens the card-view modal with a ✦ Buy button.
		btn.pressed.connect(func() -> void:
			_pulse_button(btn)
			_open_card_view(cid, "buy"))
		btn.mouse_entered.connect(_hover_scale.bind(btn, true))
		btn.mouse_exited.connect(_hover_scale.bind(btn, false))
		_tableau_box.add_child(btn)


const BUY_PRICE_MARKUP: int = 0   # Tableau buy = card's time_cost + this

func _buy_price(card: Dictionary) -> int:
	return int(card.get("time_cost", 1)) + BUY_PRICE_MARKUP


func _on_buy_card(cid: String) -> void:
	if _phase != Phase.PLANNING or _game_over:
		return
	var card: Dictionary = _action_cards.get(cid, {})
	var price: int = _buy_price(card)
	if _time < price:
		_log_line("[i]not enough Time to buy %s (need %d, have %d)[/i]" %
			[card.get("title", cid), price, _time])
		return
	_time -= price
	_hand_cards.append(cid)
	_audio_sfx("card_play")
	_log_line("[color=#7cffb0]✦ bought [b]%s[/b][/color]  (cost %d, Time %d → %d)" %
		[card.get("title", cid), price, _time + price, _time])
	_render()


func _card_summary(card: Dictionary) -> String:
	var out: PackedStringArray = []
	# Framework cards: triple-outcome dice card
	if card.has("double_success"):
		out.append("Roll the Threshold dice:")
		out.append("  ★★  " + str(card.get("double_success", "")))
		out.append("  ★   " + str(card.get("single_success", "")))
		out.append("  ✕   " + str(card.get("failure", "")))
	# Passive (e.g. SPEND IT)
	if card.has("passive_effect"):
		out.append(str(card.get("passive_effect", "")))
	# Requires
	var reqs: Array = card.get("requires", [])
	if not reqs.is_empty():
		var req_lines: PackedStringArray = []
		for r: Dictionary in reqs:
			req_lines.append(_describe_requirement(r))
		out.append("Requires: " + ", ".join(req_lines))
	# Effects (arcana cards)
	var effs: Array = card.get("effects", [])
	if not effs.is_empty():
		out.append("Effect:")
		for e: Dictionary in effs:
			out.append("  · " + _describe_effect(e))
	return "\n".join(out)


# Convert one requirement dict into a one-line English phrase.
func _describe_requirement(r: Dictionary) -> String:
	match String(r.get("kind", "")):
		"at_pos":          return "you at %s" % String(r.get("pos", "?")).to_upper()
		"at_threshold":    return "you at a THRESHOLD"
		"inventory_has":   return "carry %s" % String(r.get("item", "?")).to_upper()
		"inventory_has_contents": return "carry any CONTENTS"
		"item_at_pos":     return "an item is here"
		"win_conditions_met": return "win conditions met"
	return String(r.get("kind", "?"))


# Convert one effect dict into a one-line English phrase. Keeps card
# tooltips legible instead of dumping raw {kind: foo, ...} syntax.
func _describe_effect(e: Dictionary) -> String:
	var kind: String = String(e.get("kind", ""))
	match kind:
		"gain_time":      return "+%d Time" % int(e.get("amount", 1))
		"lose_time":      return "-%d Time" % int(e.get("amount", 1))
		"gain_inertia":   return "+%d Inertia" % int(e.get("amount", 1))
		"lose_inertia":   return "-%d Inertia" % int(e.get("amount", 1))
		"recover_health": return "+%d Health" % int(e.get("amount", 1))
		"log":            return String(e.get("text", ""))
		"if_at":
			var then_e: Array = e.get("then", [])
			var sub: PackedStringArray = []
			for se: Dictionary in then_e:
				sub.append(_describe_effect(se))
			return "if you're at %s: %s" % [String(e.get("pos", "?")).to_upper(), " · ".join(sub)]
		"else":           return "otherwise no effect"
		"move_visitor":   return "%s moves to %s" % [String(e.get("visitor", "?")), String(e.get("to", "?"))]
		"ring_bell_tone": return "ring the BELL"
		"if_both_tones_rung":
			var then_e2: Array = e.get("then", [])
			var sub2: PackedStringArray = []
			for se: Dictionary in then_e2:
				sub2.append(_describe_effect(se))
			return "if both bell tones rung: %s" % " · ".join(sub2)
		"advance_next_visitor_arrival": return "next visitor arrives %d turn(s) sooner" % int(e.get("by", 1))
		"advance_visitor_arrival": return "%s arrives %d turn(s) sooner" % [String(e.get("visitor", "?")), int(e.get("by", 1))]
		"increment_meta":   return "track meta:%s" % String(e.get("key", ""))
		"if_meta_at_least":
			var then_e3: Array = e.get("then", [])
			var sub3: PackedStringArray = []
			for se: Dictionary in then_e3:
				sub3.append(_describe_effect(se))
			return "after %d %s: %s" % [int(e.get("value", 0)), String(e.get("key", "")), " · ".join(sub3)]
		"end_action_phase": return "ends your action phase"
		"if_visitor_adjacent":
			var then_e4: Array = e.get("then", [])
			var sub4: PackedStringArray = []
			for se: Dictionary in then_e4:
				sub4.append(_describe_effect(se))
			return "if %s is here: %s" % [String(e.get("visitor", "?")).to_upper(), " · ".join(sub4)]
		"if_visitor_present":
			var then_e5: Array = e.get("then", [])
			var sub5: PackedStringArray = []
			for se: Dictionary in then_e5:
				sub5.append(_describe_effect(se))
			return "if %s has arrived: %s" % [String(e.get("visitor", "?")).to_upper(), " · ".join(sub5)]
		"if_at_pos_and_visitor_arrived_this_turn":
			return "if you're at %s when %s arrives: connect" % [String(e.get("pos", "?")).to_upper(), String(e.get("visitor", "?")).to_upper()]
		"mark_connection": return "connect with %s" % String(e.get("visitor", "?")).to_upper()
		"connect_visitor_at_my_pos": return "connect with any visitor on your space"
		"move_player_toward_threshold": return "pick a destination up to %d hop(s) away" % int(e.get("spaces", 1))
		"take_item_at_pos": return "pick up the top item here"
		"assemble_bindle": return "assemble the BUNDLE"
		"if_contents_is":
			var then_e6: Array = e.get("then", [])
			var sub6: PackedStringArray = []
			for se: Dictionary in then_e6:
				sub6.append(_describe_effect(se))
			return "if your contents is %s: %s" % [String(e.get("contents", "?")), " · ".join(sub6)]
		"auto_connect_visitor": return "auto-connect %s" % String(e.get("visitor", "?")).to_upper()
		"trigger_win":     return "trigger the LEAP win"
		"set_next_time_reset": return "next Time reset = %d" % int(e.get("value", 6))
		"if_played_this_turn":
			return "if you played %s this turn..." % String(e.get("card", "?")).to_upper()
		"discard_hand":    return "discard %d card(s)" % int(e.get("amount", 1))
		"reveal_lore_token": return "lore token: %s" % String(e.get("token", "?"))
		"play_jukebox_track": return "play %s" % String(e.get("label", "track"))
		"advance_stranger_connection": return "advance Stranger connection"
	# Default: humanise the kind (snake_case → space-case)
	return kind.replace("_", " ")


# ── Tooltip builders for board nodes ────────────────────────────────

func _tooltip_for_space(s: Dictionary) -> String:
	var sid: String = s.get("id", "")
	var label: String = s.get("label", sid)
	var kind: String = s.get("kind", "named")
	var lines: PackedStringArray = []
	lines.append(label + ("  (you are here)" if sid == _player_pos else ""))
	match kind:
		"threshold": lines.append("Threshold — LEAP candidate when conditions are met.")
		"search":    lines.append("Search pile — play SEARCH or PICK UP here.")
		_:           pass
	if s.has("flavor"):
		lines.append(String(s.get("flavor", "")))
	# Pile count only — keep contents secret so search is a discovery
	# beat, not a spoiler in a tooltip.
	var pile_id: String = s.get("search_pile", "")
	if pile_id != "":
		var pile: Array = _pile_state.get(pile_id, [])
		if pile.is_empty():
			lines.append("Pile: (empty)")
		else:
			lines.append("Pile: %d item(s) — search to reveal" % pile.size())
	# What's here
	var here_visitors: PackedStringArray = []
	for vid in _visitors_state:
		var vst: Dictionary = _visitors_state[vid]
		if vst.get("arrived", false) and vst.get("pos", "") == sid:
			here_visitors.append(String(_visitors_def.get(vid, {}).get("name", vid)))
	if not here_visitors.is_empty():
		lines.append("Here: " + ", ".join(here_visitors))
	# Adjacency
	var adj: Array = (_location.get("adjacency", {}) as Dictionary).get(sid, [])
	if not adj.is_empty():
		var adj_names: PackedStringArray = []
		for nbr: String in adj:
			if nbr == "precipice_door" and not _flags.get("precipice_revealed", false):
				continue
			adj_names.append(nbr.replace("_", " "))
		lines.append("Connects to: " + ", ".join(adj_names))
	return "\n".join(lines)


func _tooltip_for_player() -> String:
	var lines: PackedStringArray = []
	lines.append("★ John Frank")
	lines.append("At: " + _player_pos.replace("_", " "))
	lines.append("Time %d  ·  Inertia %d  ·  Health %d" % [_time, _inertia, _health])
	if _bindle_assembled:
		lines.append("Bindle: assembled — LEAP at a threshold")
	else:
		var s_part: String = "stick" if _inventory.has("stick") else "(stick)"
		var c_part: String = "cloth" if _inventory.has("cloth") else "(cloth)"
		var k_part: String = "contents" if _has_contents() else "(contents)"
		lines.append("Bindle: " + s_part + " · " + c_part + " · " + k_part)
	return "\n".join(lines)


func _tooltip_for_visitor(vid: String) -> String:
	var v: Dictionary = _visitors_def.get(vid, {})
	var st: Dictionary = _visitors_state.get(vid, {})
	var lines: PackedStringArray = []
	lines.append("● " + String(v.get("name", vid)))
	if st.get("connected", false):
		lines.append("✓ connected")
		if v.has("lore_text"):
			lines.append(String(v.get("lore_text", "")))
	elif st.get("claimed_turn", -1) >= 0:
		var remaining: int = int(_setup.get("claim_turns_to_consume", 2)) - (_turn - int(st["claimed_turn"]))
		lines.append("✕ claimed — %d turn(s) until consumed" % max(0, remaining))
	elif st.get("arrived", false):
		lines.append("at " + String(st.get("pos", "?")).replace("_", " "))
	# Connect requirement
	var cv: Dictionary = v.get("connect_via", {})
	if not cv.is_empty() and not st.get("connected", false):
		lines.append("Connect: " + _describe_connect_via_plain(cv))
	return "\n".join(lines)


# Tooltip-safe (no BBCode) version of _describe_connect_via.
func _describe_connect_via_plain(cv: Dictionary) -> String:
	match String(cv.get("kind", "")):
		"card_at_pos_with_visitor_adjacent":
			return "play %s at %s while they're at %s" % [
				String(cv.get("card", "?")).to_upper(),
				String(cv.get("player_pos", "?")).to_upper(),
				String(cv.get("visitor_pos", "?")).to_upper()]
		"card_at_pos":
			return "play %s at %s" % [
				String(cv.get("card", "?")).to_upper(),
				String(cv.get("player_pos", "?")).to_upper()]
		"card_at_pos_on_arrival_turn":
			return "play %s at %s on the turn they arrive" % [
				String(cv.get("card", "?")).to_upper(),
				String(cv.get("player_pos", "?")).to_upper()]
		"card_played_n_times":
			return "play %s %d times" % [
				String(cv.get("card", "?")).to_upper(), int(cv.get("times", 1))]
		"composite":
			var parts: PackedStringArray = []
			for sub: Dictionary in cv.get("all_of", []):
				parts.append(_describe_connect_via_plain(sub))
			return "; ".join(parts)
		"took_item":
			return "pick up %s" % String(cv.get("item", "?")).to_upper()
		"stood_on":
			return "stand at %s" % String(cv.get("pos", "?")).to_upper()
		"auto_on_bundle_with_contents":
			return "auto when you BUNDLE with %s" % String(cv.get("contents", "?"))
	return str(cv)


func _render_inventory() -> void:
	if _inv_box == null:
		return
	for c in _inv_box.get_children():
		c.queue_free()
	# Bindle assembly status line first
	var status := RichTextLabel.new()
	status.bbcode_enabled = true
	status.fit_content = true
	status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	status.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	status.add_theme_color_override("default_color", C_TEXT)
	status.add_theme_font_size_override("normal_font_size", 10)
	if _bindle_assembled:
		status.text = "[color=#ffd07a][b]BINDLE assembled[/b][/color] — play LEAP at a threshold."
	else:
		var have_stick: bool = _inventory.has("stick")
		var have_cloth: bool = _inventory.has("cloth")
		var have_contents: bool = _has_contents()
		status.text = "BINDLE: %s · %s · %s" % [
			"[color=#7cffb0]stick[/color]" if have_stick else "[color=#7c8398]stick[/color]",
			"[color=#7cffb0]cloth[/color]" if have_cloth else "[color=#7c8398]cloth[/color]",
			"[color=#7cffb0]contents[/color]" if have_contents else "[color=#7c8398]contents[/color]",
		]
	_inv_box.add_child(status)
	# Empty-state hint
	if _inventory.is_empty():
		var empty := Label.new()
		empty.text = "  (nothing yet — Search at a pile space)"
		empty.add_theme_font_size_override("font_size", 9)
		empty.add_theme_color_override("font_color", Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.5))
		_inv_box.add_child(empty)
		return
	# Item rows
	for item_id: String in _inventory:
		var item: Dictionary = _items_def.get(item_id, {})
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 4)
		row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var art: Texture2D = _load_texture_silent(_art_path_item(item_id))
		if art:
			var ico := TextureRect.new()
			ico.texture = art
			ico.custom_minimum_size = Vector2(24, 24)
			ico.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
			ico.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
			row.add_child(ico)
		var lbl := RichTextLabel.new()
		lbl.bbcode_enabled = true
		lbl.fit_content = true
		lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		lbl.add_theme_color_override("default_color", C_TEXT)
		lbl.add_theme_font_size_override("normal_font_size", 10)
		var cat: String = item.get("category", "")
		var tag: String = ""
		match cat:
			"bindle_component": tag = "[color=#c8a268][b]B[/b][/color] "
			"bindle_contents":  tag = "[color=#ffd07a][b]C[/b][/color] "
			"consumable":       tag = "[color=#7cffb0][b]u[/b][/color] "
			"passive":          tag = "[color=#9bc3ff][b]p[/b][/color] "
			_:                  tag = ""
		lbl.text = "%s%s" % [tag, item.get("title", item_id)]
		row.add_child(lbl)
		_inv_box.add_child(row)


func _render_visitors() -> void:
	for c in _visitors_box.get_children():
		c.queue_free()
	for vid in _visitors_def:
		var v: Dictionary = _visitors_def[vid]
		var st: Dictionary = _visitors_state.get(vid, {})
		# Fully-hidden visitors (e.g. conditional Anya before her trigger)
		# don't even occupy a slot in the list.
		if v.get("hidden_until_arrived", false) and not st.get("arrived", false):
			continue
		var arrived: bool = st.get("arrived", false)
		var name_s: String = v.get("name", vid) if arrived else String(v.get("placeholder_name", "someone"))
		var accent: String = v.get("accent", "#c8a268") if arrived else "#6e6258"
		var status: String = ""
		var hint_line: String = ""

		if st.get("connected", false):
			status = " [color=#7cffb0]✓ connected[/color]"
		elif st.get("claimed_turn", -1) >= 0:
			var remaining: int = int(_setup.get("claim_turns_to_consume", 2)) - (_turn - int(st["claimed_turn"]))
			status = " [color=#ff8060]✕ claimed (%d turns left)[/color]" % remaining
		elif arrived:
			status = " [color=#c8a268]· at %s[/color]" % st.get("pos", "?")
		elif st.has("scheduled_turn"):
			var diff: int = int(st["scheduled_turn"]) - _turn
			# Escalating hint: index by proximity to arrival (last hint = arriving now)
			var hints: Array = v.get("pre_arrival_hints", [])
			if not hints.is_empty():
				var idx: int = clamp(hints.size() - 1 - max(0, diff), 0, hints.size() - 1)
				hint_line = String(hints[idx])
			if diff <= 0:
				status = " [color=#7c8398]· any moment[/color]"
			else:
				status = " [color=#7c8398]· ~%dt[/color]" % diff
		else:
			# Dormant unscheduled (e.g. conditional w/o hidden flag): show nothing
			# rather than leak that they exist
			continue

		# Row: optional face image + text label
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 4)
		row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		if arrived:
			var face: Texture2D = _load_texture_silent(_art_path_visitor_face(vid))
			if face:
				var face_rect := TextureRect.new()
				face_rect.texture = face
				face_rect.custom_minimum_size = Vector2(28, 28)
				face_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
				face_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
				row.add_child(face_rect)
		var rt := RichTextLabel.new()
		rt.bbcode_enabled = true
		rt.fit_content = true
		rt.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		rt.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		rt.add_theme_color_override("default_color", C_TEXT)
		rt.add_theme_font_size_override("normal_font_size", 9)
		if hint_line != "" and not arrived:
			rt.text = "[color=%s]●[/color] [i]%s[/i]%s\n[color=#7c8398][i]   %s[/i][/color]" % [accent, name_s, status, hint_line]
		else:
			rt.text = "[color=%s]●[/color] %s%s" % [accent, name_s, status]
		row.add_child(rt)
		_visitors_box.add_child(row)


# ── Pane modal body builders ────────────────────────────────────────

# Short one-line hint for the phase, used in the phase-label tooltip
# so the player always knows what to do at the current beat without
# opening the full rules modal.
func _phase_what_now(p: int) -> String:
	match p:
		Phase.ACTION:
			return "ACTION — click cards in your HAND to play them, or click MOVE ↪ / a space label to walk. Click Advance → when done."
		Phase.PLANNING:
			return "PLANNING — buy non-starter cards from the TABLEAU (cost = card's Time). Unspent Time will carry into next turn. Click Advance →."
		Phase.SHADOW:
			return "SHADOW — the room takes its turn. A Gravity card flips and resolves. You don't make decisions here, just click Advance →."
		Phase.DRIFT:
			return "DRIFT — unclaimed visitors drift toward attractor spots. Click Advance →."
		Phase.UPKEEP:
			return "UPKEEP — cleanup. Inertia ticks if the room's hold is rising. Click Advance → to start the next turn."
	return ""


# Full How-to-Play modal body — every phase explained, plus a quick
# legend for connections, bindle, and the LEAP win.
func _build_phase_help_modal_body() -> Control:
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 14)
	var intro := RichTextLabel.new()
	intro.bbcode_enabled = true
	intro.fit_content = true
	intro.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	intro.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	intro.add_theme_color_override("default_color", C_TEXT)
	intro.add_theme_font_size_override("normal_font_size", 13)
	intro.text = "[i]Each turn cycles through five phases. The phase label at the top of the screen tells you which one you're in. Click [b]Advance →[/b] to leave the current phase.[/i]"
	vb.add_child(intro)

	var phases: Array = [
		{
			"name": "ACTION",
			"goal": "Play cards from your HAND, walk the diner, connect with visitors.",
			"do": [
				"Click a HAND card to play it (costs the card's Time).",
				"Frame-cards (WALK / SPRINT / FOCUS / SEARCH / SHORT REST / LONG REST / DISTRACTION / GUARD / CLOSE CALL / SPEND IT / IMPROVISE) roll the Threshold dice; the outcome determines what they do.",
				"Click the [b]MOVE ↪[/b] button (or any adjacent space marker on the board) to walk 1 hop for 1 Time, no card needed.",
				"Pick up an item with PICK UP at a search-pile space.",
				"Phase ends when you click [b]Advance →[/b] (some cards end it automatically — e.g. SIT WITH).",
			],
		},
		{
			"name": "PLANNING",
			"goal": "Buy new cards. Reset Time.",
			"do": [
				"The TABLEAU row above the HAND shows non-starter cards available for purchase. Click a tableau card to buy it — costs the card's Time.",
				"Time refreshes — unspent Time carries over and adds to the base (6 per turn). End with 2 unspent → next turn starts with 8.",
				"Played starter cards (e.g. WIPE COUNTER, SHORT REST, ADDRESS THE BELL) return to your hand for free.",
				"BUNDLE auto-enters your hand when you have stick + cloth + a contents item. LEAP auto-enters once BUNDLE is played.",
			],
		},
		{
			"name": "SHADOW",
			"goal": "The room takes its turn.",
			"do": [
				"A Gravity card flips and resolves automatically. The card's effect happens to you — usually an Inertia tick, a claim on a visitor, or a forced choice.",
				"GUARD cards played earlier in the turn absorb the next Inertia tick.",
				"DISTRACTION cards played earlier can cancel the top Gravity card.",
				"Just click Advance → when you've read the card.",
			],
		},
		{
			"name": "DRIFT",
			"goal": "Visitors drift toward attractor spaces.",
			"do": [
				"Lingering, unconnected visitors drift toward the HOSTESS STAND, the BAR, or BOOTH 4 (the drift attractors).",
				"This phase is currently mostly flavor — full drift logic is coming. Click Advance →.",
			],
		},
		{
			"name": "UPKEEP",
			"goal": "Cleanup. Inertia tick. Visitor consumption.",
			"do": [
				"Inertia rises by 1 per turn baseline. Some Gravity effects make it rise faster.",
				"Claimed patrons who weren't helped in time tick toward consumption.",
				"At Inertia 7+ the deck thickens. At Inertia 12 you've lost — the 24-hour diner of the soul.",
				"Click Advance → and the next ACTION turn begins.",
			],
		},
	]
	for ph: Dictionary in phases:
		var section := PanelContainer.new()
		section.add_theme_stylebox_override("panel", _make_panel_style())
		var inner := VBoxContainer.new()
		inner.add_theme_constant_override("separation", 4)
		section.add_child(inner)
		var hdr := RichTextLabel.new()
		hdr.bbcode_enabled = true
		hdr.fit_content = true
		hdr.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		hdr.add_theme_color_override("default_color", C_TEXT)
		hdr.add_theme_font_size_override("normal_font_size", 14)
		hdr.text = "[color=#c8a268][b]%s[/b][/color]  —  [i]%s[/i]" % [ph["name"], ph["goal"]]
		inner.add_child(hdr)
		for line: String in ph.get("do", []):
			var item := RichTextLabel.new()
			item.bbcode_enabled = true
			item.fit_content = true
			item.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			item.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			item.add_theme_color_override("default_color", C_TEXT)
			item.add_theme_font_size_override("normal_font_size", 11)
			item.text = "  · " + line
			inner.add_child(item)
		vb.add_child(section)

	# Win / loss legend
	var legend := PanelContainer.new()
	legend.add_theme_stylebox_override("panel", _make_panel_style())
	var lvb := VBoxContainer.new()
	lvb.add_theme_constant_override("separation", 4)
	legend.add_child(lvb)
	var lhdr := Label.new()
	lhdr.text = "  WIN / LOSS"
	lhdr.add_theme_color_override("font_color", C_ACCENT)
	lhdr.add_theme_font_size_override("font_size", 13)
	lvb.add_child(lhdr)
	var llr := RichTextLabel.new()
	llr.bbcode_enabled = true
	llr.fit_content = true
	llr.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	llr.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	llr.add_theme_color_override("default_color", C_TEXT)
	llr.add_theme_font_size_override("normal_font_size", 11)
	llr.text = "[b]WIN:[/b] assemble the BUNDLE (stick + cloth + a contents item), connect with at least 3 visitors, keep Faith adjacent, and play LEAP at an open threshold while Inertia is under 7.\n\n[b]LOSS:[/b] Inertia reaches 12 (the 24-hour diner of the soul) [i]or[/i] 3 visitors stay claimed and get consumed."
	lvb.add_child(llr)
	vb.add_child(legend)
	return vb


func _build_log_modal_body() -> Control:
	# Full log — read from _log_buffer (RichTextLabel.append_text
	# doesn't update its .text property, so we keep our own copy).
	var rt := RichTextLabel.new()
	rt.bbcode_enabled = true
	rt.fit_content = true
	rt.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	rt.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	rt.add_theme_color_override("default_color", C_TEXT)
	rt.add_theme_font_size_override("normal_font_size", 12)
	rt.scroll_following = true
	rt.text = "\n".join(_log_buffer)
	# Opening the modal counts as catching up.
	_log_unread_count = 0
	_update_log_unread_badge()
	return rt


func _build_inventory_modal_body() -> Control:
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 8)
	# Bindle status header
	var status := RichTextLabel.new()
	status.bbcode_enabled = true
	status.fit_content = true
	status.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	status.add_theme_color_override("default_color", C_TEXT)
	status.add_theme_font_size_override("normal_font_size", 14)
	if _bindle_assembled:
		status.text = "[color=#ffd07a][b]BINDLE assembled.[/b][/color] Play LEAP at any open threshold to win."
	else:
		var s_part: String = "[color=#7cffb0]stick[/color]" if _inventory.has("stick") else "[color=#7c8398]stick[/color]"
		var c_part: String = "[color=#7cffb0]cloth[/color]" if _inventory.has("cloth") else "[color=#7c8398]cloth[/color]"
		var k_part: String = "[color=#7cffb0]contents[/color]" if _has_contents() else "[color=#7c8398]contents[/color]"
		status.text = "[b]Bindle:[/b]  %s  ·  %s  ·  %s" % [s_part, c_part, k_part]
	vb.add_child(status)
	vb.add_child(HSeparator.new())
	if _inventory.is_empty():
		var empty := Label.new()
		empty.text = "  Nothing in inventory yet. Search at a pile space (REGISTER, BOOTH 6, JUKEBOX, CARD WALL, UNDER COUNTER, PAY PHONE, KITCHEN ALCOVE)."
		empty.add_theme_color_override("font_color", Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.7))
		empty.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		empty.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		vb.add_child(empty)
		return vb
	# Per-item rows
	for item_id: String in _inventory:
		var item: Dictionary = _items_def.get(item_id, {})
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 10)
		row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var art: Texture2D = _load_texture_silent(_art_path_item(item_id))
		if art:
			var ico := TextureRect.new()
			ico.texture = art
			ico.custom_minimum_size = Vector2(64, 64)
			ico.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
			ico.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
			row.add_child(ico)
		var text := RichTextLabel.new()
		text.bbcode_enabled = true
		text.fit_content = true
		text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		text.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		text.add_theme_color_override("default_color", C_TEXT)
		text.add_theme_font_size_override("normal_font_size", 12)
		var cat: String = item.get("category", "")
		var cat_label: String = ""
		match cat:
			"bindle_component": cat_label = "[color=#c8a268]bindle component[/color]"
			"bindle_contents":  cat_label = "[color=#ffd07a]bindle contents[/color]"
			"consumable":       cat_label = "[color=#7cffb0]consumable[/color]"
			"passive":          cat_label = "[color=#9bc3ff]passive[/color]"
			"jukebox_track":    cat_label = "[color=#c8a268]jukebox track[/color]"
			_:                  cat_label = "[color=#7c8398]item[/color]"
		text.text = "[b]%s[/b]   %s\n[i]%s[/i]" % [
			item.get("title", item_id), cat_label, item.get("flavor", "")]
		row.add_child(text)
		vb.add_child(row)
	return vb


func _build_visitors_modal_body() -> Control:
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 12)
	for vid in _visitors_def:
		var v: Dictionary = _visitors_def[vid]
		var st: Dictionary = _visitors_state.get(vid, {})
		var arrived: bool = st.get("arrived", false)
		# Hidden conditional visitors stay hidden in the modal too
		if v.get("hidden_until_arrived", false) and not arrived:
			continue
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 10)
		row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var face: Texture2D = _load_texture_silent(_art_path_visitor_face(vid)) if arrived else null
		if face:
			var ico := TextureRect.new()
			ico.texture = face
			ico.custom_minimum_size = Vector2(72, 72)
			ico.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
			ico.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
			row.add_child(ico)
		var text := RichTextLabel.new()
		text.bbcode_enabled = true
		text.fit_content = true
		text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		text.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		text.add_theme_color_override("default_color", C_TEXT)
		text.add_theme_font_size_override("normal_font_size", 12)
		var name_s: String = v.get("name", vid) if arrived else String(v.get("placeholder_name", "someone"))
		var accent: String = v.get("accent", "#c8a268") if arrived else "#6e6258"
		var lines: PackedStringArray = []
		lines.append("[color=%s][b]%s[/b][/color]" % [accent, name_s])
		if st.get("connected", false):
			lines.append("[color=#7cffb0]✓ connected[/color]  —  " + String(v.get("lore_text", "")))
		elif st.get("claimed_turn", -1) >= 0:
			var remaining: int = int(_setup.get("claim_turns_to_consume", 2)) - (_turn - int(st["claimed_turn"]))
			lines.append("[color=#ff8060]✕ claimed — %d turns until they're consumed[/color]" % remaining)
		elif arrived:
			lines.append("at [b]%s[/b]" % st.get("pos", "?"))
		elif st.has("scheduled_turn"):
			var diff: int = int(st["scheduled_turn"]) - _turn
			var hints: Array = v.get("pre_arrival_hints", [])
			if not hints.is_empty():
				var idx: int = clamp(hints.size() - 1 - max(0, diff), 0, hints.size() - 1)
				lines.append("[i]%s[/i]" % String(hints[idx]))
			lines.append("[color=#7c8398]· arriving in ~%d turns[/color]" % max(0, diff))
		# Connect requirement
		var cv: Dictionary = v.get("connect_via", {})
		if not cv.is_empty() and not st.get("connected", false):
			lines.append("[color=#c8a268]Connect:[/color] %s" % _describe_connect_via(cv))
		text.text = "\n".join(lines)
		row.add_child(text)
		vb.add_child(row)
	return vb


func _describe_connect_via(cv: Dictionary) -> String:
	match cv.get("kind", ""):
		"card_at_pos_with_visitor_adjacent":
			return "play [b]%s[/b] at [b]%s[/b] while they're at [b]%s[/b]" % [
				String(cv.get("card", "?")).to_upper(),
				String(cv.get("player_pos", "?")).to_upper(),
				String(cv.get("visitor_pos", "?")).to_upper()]
		"card_at_pos":
			return "play [b]%s[/b] at [b]%s[/b]" % [
				String(cv.get("card", "?")).to_upper(),
				String(cv.get("player_pos", "?")).to_upper()]
		"card_at_pos_on_arrival_turn":
			return "play [b]%s[/b] at [b]%s[/b] on the turn they arrive" % [
				String(cv.get("card", "?")).to_upper(),
				String(cv.get("player_pos", "?")).to_upper()]
		"card_played_n_times":
			return "play [b]%s[/b] %d times" % [
				String(cv.get("card", "?")).to_upper(), int(cv.get("times", 1))]
		"composite":
			var parts: PackedStringArray = []
			for sub: Dictionary in cv.get("all_of", []):
				parts.append("· " + _describe_connect_via(sub))
			return "\n   " + "\n   ".join(parts)
		"took_item":
			return "pick up [b]%s[/b]" % String(cv.get("item", "?")).to_upper()
		"stood_on":
			return "stand at [b]%s[/b]" % String(cv.get("pos", "?")).to_upper()
		"auto_on_bundle_with_contents":
			return "auto-connect when you BUNDLE with [b]%s[/b]" % String(cv.get("contents", "?"))
	return str(cv)


func _build_gravity_modal_body() -> Control:
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 8)
	var header := RichTextLabel.new()
	header.bbcode_enabled = true
	header.fit_content = true
	header.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_theme_color_override("default_color", C_TEXT)
	header.add_theme_font_size_override("normal_font_size", 14)
	header.text = "[color=#c8a268][b]Gravity deck[/b][/color]  ·  %d cards remaining" % _gravity_draw_pile.size()
	vb.add_child(header)
	vb.add_child(HSeparator.new())
	# Cards still in the deck — shown FACE DOWN (don't spoil), just by count
	# per title? No — spec wants full content. We'll show titles + flavor
	# since the player has the right to read every card in the deck.
	var by_id: Dictionary = {}
	for c: Dictionary in _gravity_deck_def.get("cards", []):
		by_id[c.get("id", "")] = c
	for cid: String in _gravity_draw_pile:
		var c: Dictionary = by_id.get(cid, {})
		var rt := RichTextLabel.new()
		rt.bbcode_enabled = true
		rt.fit_content = true
		rt.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		rt.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		rt.add_theme_color_override("default_color", C_TEXT)
		rt.add_theme_font_size_override("normal_font_size", 11)
		rt.text = "[b]%s[/b]\n[color=#7c8398][i]%s[/i][/color]" % [c.get("title", cid), c.get("flavor", "")]
		vb.add_child(rt)
	return vb


# ── Render-all ───────────────────────────────────────────────────────

func _render() -> void:
	if _game_over:
		return
	# Auto-grant milestone cards into hand — these are awards, not
	# purchases, so they shouldn't sit in the tableau shop for the
	# user to figure out they need to buy. Granted the moment the
	# trigger condition fires.
	if _has_all_bindle_components() and not _bindle_assembled and not ("bundle" in _hand_cards):
		_hand_cards.append("bundle")
		_log_line("[color=#ffd07a][b]BUNDLE in hand[/b] — all three components collected.[/color]")
		_show_toast("[b]BUNDLE[/b] is in your hand — assemble it.", "#ffd07a")
	if _bindle_assembled and not ("leap" in _hand_cards):
		_hand_cards.append("leap")
		_log_line("[color=#ffd07a][b]LEAP in hand[/b] — bindle assembled.[/color]")
		_show_toast("[b]LEAP[/b] unlocked — play it at any open threshold.", "#ffd07a")
	_phase_label.text = "PHASE: " + Phase.keys()[_phase]
	_phase_label.tooltip_text = _phase_what_now(_phase) + "\n\n(Click for full rules.)"
	_turn_label.text  = "Turn %d" % _turn
	_time_label.text  = "Time %d / %d" % [_time, _next_time_reset]
	_inertia_label.text = "Inertia %d / 12" % _inertia
	_health_label.text  = "Health %d" % _health
	# Flash labels on change — green for gain, red for loss
	# (Inertia inverted: rising is bad, falling is good)
	if _last_rendered_time != -1 and _time != _last_rendered_time:
		_pulse_label(_time_label, Color(0.49, 1.0, 0.69) if _time > _last_rendered_time else Color(1.0, 0.50, 0.39))
	if _last_rendered_inertia != -1 and _inertia != _last_rendered_inertia:
		_pulse_label(_inertia_label, Color(0.49, 1.0, 0.69) if _inertia < _last_rendered_inertia else Color(1.0, 0.50, 0.39))
	if _last_rendered_health != -1 and _health != _last_rendered_health:
		_pulse_label(_health_label, Color(0.49, 1.0, 0.69) if _health > _last_rendered_health else Color(1.0, 0.50, 0.39))
	_last_rendered_time = _time
	_last_rendered_inertia = _inertia
	_last_rendered_health = _health
	_player_pos_label.text = "at: " + _player_pos
	_bindle_label.text = "Bindle: " + _bindle_display()
	# Rebuild the board so the » chevron + highlight color follow
	# the player to their new space. Cheap (~20 labels).
	_render_board()
	_position_meeples()
	_render_hand()
	_render_tableau()
	_render_visitors()
	_render_inventory()
	_update_advance_label()


func _bindle_display() -> String:
	if _bindle_assembled:
		return "★ ASSEMBLED ★"
	var parts: PackedStringArray = []
	if _inventory.has("stick"):  parts.append("stick")
	if _inventory.has("cloth"):  parts.append("cloth")
	var has_contents := false
	for it in _inventory:
		if String(it).begins_with("contents_"):
			has_contents = true
			parts.append("contents")
			break
	if parts.is_empty():
		return "—"
	return ", ".join(parts)


func _update_advance_label() -> void:
	match _phase:
		Phase.ACTION:   _advance_btn.text  = "End Action →"
		Phase.PLANNING: _advance_btn.text  = "End Planning →"
		Phase.SHADOW:   _advance_btn.text  = "End Shadow →"
		Phase.DRIFT:    _advance_btn.text  = "End Drift →"
		Phase.UPKEEP:   _advance_btn.text  = "Next Turn →"


# ── Logging ──────────────────────────────────────────────────────────

func _log_line(s: String) -> void:
	_log_buffer.append(s)
	if _log == null:
		print("[Gauntlet] " + s)
		return
	_log.append_text(s + "\n")
	# Don't count the initial banner/setup lines as unread — only
	# count once the live UI is rendering.
	if _last_rendered_time != -1:
		_log_unread_count += 1
		_update_log_unread_badge()


func _update_log_unread_badge() -> void:
	var lbl: Label = _pane_title_labels.get("log") as Label
	if lbl == null:
		return
	if _log_unread_count > 0:
		lbl.text = "  LOG  · %d new" % _log_unread_count
		lbl.add_theme_color_override("font_color", Color(1.0, 0.82, 0.42))
	else:
		lbl.text = "  LOG"
		lbl.add_theme_color_override("font_color", C_ACCENT)


# ── Card playability + play ─────────────────────────────────────────

func _can_play_card(card: Dictionary) -> bool:
	var cost: int = int(card.get("time_cost", 1))
	if _time < cost:
		return false
	# Check requires[]
	for req: Dictionary in card.get("requires", []):
		if not _check_requirement(req):
			return false
	# Special: LEAP only when conditions met
	if card.get("id", "") == "leap":
		return _win_conditions_met()
	# BUNDLE only with stick + cloth + contents
	if card.get("id", "") == "bundle":
		return (_inventory.has("stick") and _inventory.has("cloth")
				and _has_contents() and not _bindle_assembled)
	return true


func _check_requirement(req: Dictionary) -> bool:
	match req.get("kind", ""):
		"at_pos":
			return _player_pos == req.get("pos", "")
		"inventory_has":
			return _inventory.has(req.get("item", ""))
		"inventory_has_contents":
			return _has_contents()
		"item_at_pos":
			var pile_id := _pile_at_pos(_player_pos)
			return pile_id != "" and not _pile_state.get(pile_id, []).is_empty()
		"at_threshold":
			return _is_threshold(_player_pos)
		"win_conditions_met":
			return _win_conditions_met()
	return true


func _has_contents() -> bool:
	for it in _inventory:
		if String(it).begins_with("contents_"):
			return true
	return false


func _has_all_bindle_components() -> bool:
	return _inventory.has("stick") and _inventory.has("cloth") and _has_contents()


func _pile_at_pos(pos: String) -> String:
	for s: Dictionary in _location.get("spaces", []):
		if s.get("id", "") == pos:
			return s.get("search_pile", "")
	return ""


func _is_threshold(pos: String) -> bool:
	for s: Dictionary in _location.get("spaces", []):
		if s.get("id", "") == pos and s.get("kind", "") == "threshold":
			return true
	return false


func _win_conditions_met() -> bool:
	if not _bindle_assembled:
		return false
	if _connections_made.size() < int(_setup.get("win_conditions", {}).get("require_visitors_connected_min", 3)):
		return false
	if _inertia >= int(_setup.get("win_conditions", {}).get("require_inertia_below", 7)):
		return false
	# Faith adjacent
	var faith_state: Dictionary = _visitors_state.get("faith", {})
	if not (faith_state.get("arrived", false) and faith_state.get("pos", "") == _player_pos):
		return false
	# Threshold space
	if not _is_threshold(_player_pos):
		return false
	return true


func _on_play_card(cid: String) -> void:
	if _game_over or _phase != Phase.ACTION:
		return
	var card: Dictionary = _action_cards.get(cid, {})
	if not _can_play_card(card):
		_log_line("[i]can't play %s now[/i]" % card.get("title", cid))
		return
	var cost: int = int(card.get("time_cost", 1))
	_time -= cost
	_played_this_turn.append(cid)
	_audio_sfx("card_play")
	_log_line("→ played [b]%s[/b]" % card.get("title", cid))
	# Resolve effects
	_resolve_effects(card.get("effects", []))
	# Framework cards: either a dice-roll outcome (double_success
	# present) or a passive (passive_effect present, e.g. SPEND IT).
	if card.has("double_success"):
		_resolve_framework_card(card)
	elif card.has("passive_effect"):
		_apply_framework_card_mechanic(card.get("id", ""), "passive")
	# Remove from hand (except for starter Zero Cost — they refresh next planning)
	_hand_cards.erase(cid)
	if _is_starter(cid):
		# Zero Cost starters refresh: rebuy automatically next planning
		# (For now just re-add)
		pass
	_render()
	_check_game_end()


func _is_starter(cid: String) -> bool:
	return _action_cards.get(cid, {}).get("starter", false)


func _resolve_effects(effects: Array) -> void:
	for e in effects:
		_resolve_effect(e)


func _resolve_effect(e: Dictionary) -> void:
	var kind: String = e.get("kind", "")
	match kind:
		"gain_time":
			_time += int(e.get("amount", 0))
			_next_time_reset += int(e.get("amount", 0))
		"lose_time":
			_time = max(0, _time - int(e.get("amount", 0)))
		"gain_inertia":
			# GUARD flag (set by a successful Guard card) absorbs the
			# next Gravity-card Inertia tick.
			if _flags.get("guard_ignore_next_gravity_inertia", false):
				_flags["guard_ignore_next_gravity_inertia"] = false
				_log_line("[color=#7cffb0]GUARD absorbed +%d Inertia.[/color]" % e.get("amount", 0))
			else:
				_inertia = min(12, _inertia + int(e.get("amount", 0)))
				_log_line("[color=#ff8060]+%d Inertia[/color] → %d" % [e.get("amount", 0), _inertia])
		"lose_inertia":
			_inertia = max(0, _inertia - int(e.get("amount", 0)))
			_log_line("[color=#7cffb0]-%d Inertia[/color] → %d" % [e.get("amount", 0), _inertia])
		"recover_health":
			_health = min(5, _health + int(e.get("amount", 0)))
		"log":
			_log_line("[i]%s[/i]" % e.get("text", ""))
		"if_at":
			if _player_pos == e.get("pos", ""):
				_resolve_effects(e.get("then", []))
			else:
				_resolve_effects(e.get("else", []))
		"else":
			pass    # handled by sibling if_at
		"move_visitor":
			var vid: String = e.get("visitor", "")
			var to: String = e.get("to", "")
			if to == "player_pos":
				to = _player_pos
			_visitors_state[vid]["pos"] = to
			_log_line("[i]%s moves to %s[/i]" % [_visitors_def.get(vid, {}).get("name", vid), to])
		"ring_bell_tone":
			_bell_tones_rung = min(2, _bell_tones_rung + 1)
			_log_line("[i]bell tone %d/2[/i]" % _bell_tones_rung)
		"if_both_tones_rung":
			if _bell_tones_rung >= 2:
				_resolve_effects(e.get("then", []))
		"advance_next_visitor_arrival":
			_advance_next_visitor(int(e.get("by", 1)))
		"advance_visitor_arrival":
			var v: String = e.get("visitor", "")
			if _visitors_state.has(v) and _visitors_state[v].has("scheduled_turn"):
				if e.get("only_if_not_arrived", false) and _visitors_state[v].get("arrived", false):
					return
				_visitors_state[v]["scheduled_turn"] = max(_turn, int(_visitors_state[v]["scheduled_turn"]) - int(e.get("by", 1)))
		"increment_meta":
			var key: String = e.get("key", "")
			if key == "call_faith_count":
				_call_faith_count += 1
		"if_meta_at_least":
			if e.get("key", "") == "call_faith_count" and _call_faith_count >= int(e.get("value", 0)):
				_resolve_effects(e.get("then", []))
		"end_action_phase":
			_phase = Phase.PLANNING
			_log_line("[i]action phase ends.[/i]")
		"if_visitor_adjacent":
			var vid2: String = e.get("visitor", "")
			var vst: Dictionary = _visitors_state.get(vid2, {})
			if (vst.get("arrived", false) and vst.get("pos", "") == _player_pos
				and _player_pos == e.get("and_player_at", _player_pos)):
				_resolve_effects(e.get("then", []))
		"if_visitor_present":
			var vid3: String = e.get("visitor", "")
			var vst3: Dictionary = _visitors_state.get(vid3, {})
			if vst3.get("arrived", false):
				_resolve_effects(e.get("then", []))
			else:
				_resolve_effects(e.get("else", []))
		"if_at_pos_and_visitor_arrived_this_turn":
			var v2: String = e.get("visitor", "")
			var vst2: Dictionary = _visitors_state.get(v2, {})
			var arrived_this_turn: bool = (vst2.has("scheduled_turn") and int(vst2.get("scheduled_turn", 99)) == _turn)
			if _player_pos == e.get("pos", "") and arrived_this_turn:
				_resolve_effects(e.get("then", []))
		"mark_connection":
			_connect_visitor(e.get("visitor", ""))
		"move_player_toward_threshold":
			# Was: auto-route to nearest threshold. Now: prompt the
			# player for their destination (within N hops).
			_prompt_pick_destination(int(e.get("spaces", 1)), "stepped")
		"take_item_at_pos":
			_take_top_item_at_pos()
		"assemble_bindle":
			_bindle_assembled = true
			_audio_sfx("bundle")
			_log_line("[color=#ffd07a][b]BUNDLE assembled.[/b][/color]")
			_show_toast("[b]BUNDLE ASSEMBLED[/b] — find a threshold and LEAP.", "#ffd07a")
		"if_contents_is":
			if _inventory.has(e.get("contents", "")):
				_resolve_effects(e.get("then", []))
		"auto_connect_visitor":
			_connect_visitor(e.get("visitor", ""))
		"trigger_win":
			_trigger_win(e.get("from_threshold", _player_pos))
		"set_next_time_reset":
			_next_time_reset = int(e.get("value", 6))
		"if_played_this_turn":
			if e.get("card", "") in _played_this_turn:
				_resolve_effects(e.get("then", []))
			else:
				_resolve_effects(e.get("else", []))
		"discard_hand":
			_prompt_discard_cards(int(e.get("amount", 0)))
		"reveal_lore_token":
			_collect_lore_token(e.get("token", ""))
		"if_visitor_not_connected":
			if not (_visitors_state.get(e.get("visitor", ""), {}).get("connected", false)):
				_resolve_effects(e.get("then", []))
		"if_arcana_completed":
			if GauntletState.is_arcana_completed(e.get("arcana", "")):
				_resolve_effects(e.get("then", []))
		"reveal_threshold":
			_flags["precipice_revealed"] = true
		"set_flag":
			_flags[e.get("key", "")] = e.get("value", true)
		"choose":
			# Take first option for now (full UI later). Logs both.
			var opts: Array = e.get("options", [])
			if not opts.is_empty():
				_log_line("[i]choose: %s[/i]" % opts[0].get("label", ""))
				_resolve_effects(opts[0].get("effects", []))
		"play_jukebox_track":
			var bgm_path: String = e.get("bgm", "")
			var label: String = e.get("label", "track")
			if bgm_path != "":
				AudioMgr.play_bgm(bgm_path)
				_log_line("[color=#c8a268]♪ jukebox · now playing [b]%s[/b][/color]" % label)
		"advance_stranger_connection":
			# Hook for the cloth's on_pickup. The actual connection
			# fires from _check_composite_connections — this is just
			# a (now-implemented) no-op so the warning stops firing.
			pass
		"connect_visitor_at_my_pos":
			# Used by SIT WITH — connect any arrived, unconnected
			# visitor at the player's current position.
			for vid_p in _visitors_state:
				var vst_p: Dictionary = _visitors_state[vid_p]
				if vst_p.get("arrived", false) and not vst_p.get("connected", false) and vst_p.get("pos", "") == _player_pos:
					_connect_visitor(vid_p)
					break
		_:
			_log_line("[i](unhandled effect: %s)[/i]" % kind)


# Composite connect_via evaluation — runs after every move + item
# pickup. For visitors with kind:"composite", checks every sub-cond
# in all_of[] and auto-connects when all are met. The stranger's
# rule is: took_item(cloth) AND stood_on(card_wall).
func _check_composite_connections() -> void:
	for vid in _visitors_def:
		var v: Dictionary = _visitors_def[vid]
		var st: Dictionary = _visitors_state.get(vid, {})
		if st.get("connected", false):
			continue
		# Hidden-until-trigger visitors don't connect via composite
		if v.get("hidden_until_arrived", false) and not st.get("arrived", false):
			continue
		var cv: Dictionary = v.get("connect_via", {})
		if String(cv.get("kind", "")) != "composite":
			continue
		var all_met: bool = true
		for sub: Dictionary in cv.get("all_of", []):
			if not _check_connect_subcondition(sub):
				all_met = false
				break
		if all_met:
			_connect_visitor(vid)


func _check_connect_subcondition(sub: Dictionary) -> bool:
	match String(sub.get("kind", "")):
		"took_item":
			return _inventory.has(sub.get("item", ""))
		"stood_on":
			return _places_visited.has(String(sub.get("pos", "")))
		"at_pos":
			return _player_pos == String(sub.get("pos", ""))
	return false


# ── Discard chooser ─────────────────────────────────────────────────
# Used by the "discard_hand" effect (e.g. Gravity's "Choose: Discard
# 2 Action cards"). Pops a modal letting the player CHOOSE which
# cards to lose instead of silently popping from the back.
func _prompt_discard_cards(amount: int) -> void:
	if amount <= 0 or _hand_cards.is_empty():
		return
	# Tear down any existing modal
	var existing: Node = get_node_or_null("pane_modal_dim")
	if existing != null and is_instance_valid(existing):
		existing.queue_free()
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.80)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_STOP
	dim.z_index = 100
	dim.name = "pane_modal_dim"
	add_child(dim)
	var view: Vector2 = get_viewport_rect().size
	var pop := PanelContainer.new()
	pop.add_theme_stylebox_override("panel", _make_panel_style())
	pop.size = Vector2(min(view.x * 0.70, 720.0), min(view.y * 0.72, 540.0))
	pop.position = (view - pop.size) * 0.5
	pop.mouse_filter = Control.MOUSE_FILTER_STOP
	dim.add_child(pop)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 8)
	pop.add_child(vb)
	var title := Label.new()
	title.text = "  Discard %d card%s from your hand" % [amount, "" if amount == 1 else "s"]
	title.add_theme_color_override("font_color", C_ACCENT)
	title.add_theme_font_size_override("font_size", 16)
	vb.add_child(title)
	var hint := RichTextLabel.new()
	hint.bbcode_enabled = true
	hint.fit_content = true
	hint.add_theme_color_override("default_color", C_TEXT)
	hint.add_theme_font_size_override("normal_font_size", 11)
	hint.text = "[i]Click cards to select. Click [b]Discard[/b] when you've picked %d.[/i]" % amount
	vb.add_child(hint)
	vb.add_child(HSeparator.new())
	var cards_box := HBoxContainer.new()
	cards_box.add_theme_constant_override("separation", 6)
	vb.add_child(cards_box)
	var selected_indices: Array = []   # indices into _hand_cards
	var confirm_btn := Button.new()
	confirm_btn.text = "Discard (0 / %d)" % amount
	confirm_btn.add_theme_font_size_override("font_size", 13)
	confirm_btn.disabled = true
	for i in _hand_cards.size():
		var cid: String = _hand_cards[i]
		var card: Dictionary = _action_cards.get(cid, {})
		var btn := Button.new()
		btn.text = card.get("title", cid)
		btn.add_theme_font_size_override("font_size", 11)
		btn.custom_minimum_size = Vector2(108, 80)
		btn.tooltip_text = String(card.get("flavor", ""))
		btn.toggle_mode = true
		var art: Texture2D = _load_texture_silent(_art_path_card(cid))
		if art:
			btn.icon = art
			btn.expand_icon = true
			btn.vertical_icon_alignment = VERTICAL_ALIGNMENT_TOP
		var idx: int = i
		btn.toggled.connect(func(pressed: bool) -> void:
			if pressed:
				if selected_indices.size() >= amount:
					btn.button_pressed = false
					return
				selected_indices.append(idx)
			else:
				selected_indices.erase(idx)
			confirm_btn.text = "Discard (%d / %d)" % [selected_indices.size(), amount]
			confirm_btn.disabled = selected_indices.size() != amount)
		cards_box.add_child(btn)
	vb.add_child(HSeparator.new())
	var actions := HBoxContainer.new()
	actions.add_theme_constant_override("separation", 8)
	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	actions.add_child(spacer)
	confirm_btn.pressed.connect(func() -> void:
		# Remove the selected indices in descending order so earlier
		# indices stay valid
		var to_remove: Array = selected_indices.duplicate()
		to_remove.sort()
		to_remove.reverse()
		for i_v: int in to_remove:
			if i_v >= 0 and i_v < _hand_cards.size():
				_log_line("[color=#ff8060]discarded:[/color] %s" % _action_cards.get(_hand_cards[i_v], {}).get("title", _hand_cards[i_v]))
				_hand_cards.remove_at(i_v)
		_close_pane_modal(dim)
		_render())
	actions.add_child(confirm_btn)
	vb.add_child(actions)


# ── Helpers used by effects ─────────────────────────────────────────

func _connect_visitor(vid: String) -> void:
	if vid == "" or not _visitors_state.has(vid):
		return
	if _visitors_state[vid].get("connected", false):
		return
	_visitors_state[vid]["connected"] = true
	_visitors_state[vid]["claimed_turn"] = -1
	_connections_made.append(vid)
	_audio_sfx("visitor_connect")
	var v: Dictionary = _visitors_def[vid]
	_log_line("[color=#7cffb0]✓ connected with %s[/color]" % v.get("name", vid))
	_show_toast("Connected with [b]%s[/b]" % v.get("name", vid), "#7cffb0")
	if v.has("lore_token"):
		_collect_lore_token(v["lore_token"])


func _collect_lore_token(token: String) -> void:
	if token == "" or token in _lore_tokens_collected:
		return
	_lore_tokens_collected.append(token)
	_log_line("[color=#ffd07a]✦ lore token: %s[/color]" % token)
	_audio_sfx("lore_token")
	_show_toast("Lore token gained — [b]%s[/b]" % token.replace("_", " "), "#ffd07a")


func _take_top_item_at_pos() -> void:
	var pile_id := _pile_at_pos(_player_pos)
	if pile_id == "" or _pile_state.get(pile_id, []).is_empty():
		_log_line("[i]nothing to take here[/i]")
		return
	var item_id: String = _pile_state[pile_id].pop_front()
	var items_dict := _items_def
	var item: Dictionary = items_dict.get(item_id, {})
	# Reusable pile items (e.g. jukebox tracks): trigger their on-use
	# effects immediately and cycle the entry to the bottom of the pile
	# instead of putting them into inventory.
	if item.get("reusable", false):
		_audio_sfx("item_pickup")
		_log_line("[color=#c8a268]selected: %s[/color]" % item.get("title", item_id))
		if item.has("effects_on_use"):
			_resolve_effects(item["effects_on_use"])
		_pile_state[pile_id].append(item_id)
		return
	_inventory.append(item_id)
	_audio_sfx("item_pickup")
	_log_line("[color=#c8a268]picked up: %s[/color]" % item.get("title", item_id))
	var cat: String = item.get("category", "")
	if cat == "bindle_component" or cat == "bindle_contents":
		_show_toast("Picked up [b]%s[/b]" % item.get("title", item_id), "#c8a268")
	# on_pickup hooks
	if item.has("on_pickup"):
		_resolve_effects(item["on_pickup"])
	# Composite connection conditions sometimes depend on items
	_check_composite_connections()
	# Lose inertia per Bindle component
	if item.get("category", "") == "bindle_component" or item.get("category", "") == "bindle_contents":
		_inertia = max(0, _inertia - 1)


func _move_player_toward_nearest_threshold(spaces: int) -> void:
	# Simple BFS: find shortest path to nearest threshold, take first step.
	var adj: Dictionary = _location.get("adjacency", {})
	# Find threshold ids
	var thresholds: Array = []
	for s: Dictionary in _location.get("spaces", []):
		if s.get("kind", "") == "threshold":
			var tid: String = s.get("id", "")
			# Skip hidden thresholds
			if tid == "precipice_door" and not _flags.get("precipice_revealed", false):
				continue
			thresholds.append(tid)
	if thresholds.is_empty():
		return
	# BFS from player_pos
	var queue: Array = [_player_pos]
	var prev: Dictionary = {_player_pos: ""}
	while not queue.is_empty():
		var cur: String = queue.pop_front()
		if cur in thresholds:
			# Walk back to find first step
			var path: Array = []
			var n: String = cur
			while n != "":
				path.append(n)
				n = prev.get(n, "")
			path.reverse()
			# path[0] is player_pos; advance up to `spaces` steps
			var step: int = min(spaces, path.size() - 1)
			if step > 0:
				_player_pos = path[step]
				_log_line("[i]stepped toward → %s[/i]" % _player_pos)
			return
		for nbr: String in adj.get(cur, []):
			if not prev.has(nbr):
				prev[nbr] = cur
				queue.append(nbr)


func _advance_next_visitor(by: int) -> void:
	# Find earliest unarrived scheduled visitor, drop arrival turn
	var earliest_vid := ""
	var earliest_turn: int = 99
	for vid in _visitors_state:
		var st: Dictionary = _visitors_state[vid]
		if not st.get("arrived", false) and st.has("scheduled_turn"):
			if int(st["scheduled_turn"]) < earliest_turn:
				earliest_turn = int(st["scheduled_turn"])
				earliest_vid = vid
	if earliest_vid != "":
		_visitors_state[earliest_vid]["scheduled_turn"] = max(_turn, earliest_turn - by)


# ── Framework card resolution (Threshold Roll) ──────────────────────

func _resolve_framework_card(card: Dictionary) -> void:
	# Roll Threshold dice. Number of dice = base + modifiers.
	# Base: 2. Modifier: lower inertia → more dice (low inertia is good).
	var n_dice: int = 2
	if _inertia >= 7:
		n_dice = max(1, n_dice - 1)
	var roll := _roll_arcana_dice(n_dice)
	var result: String = roll["result"]
	var line: String = roll["line"]
	_log_line("[i]threshold roll: %s → %s[/i]" % [line, result])
	# Apply outcome — log flavor AND apply mechanical effect.
	match result:
		"ss":
			_log_line("★★ " + card.get("double_success", ""))
		"s":
			_log_line("★  " + card.get("single_success", ""))
		"fail":
			_log_line("✕  " + card.get("failure", ""))
	_apply_framework_card_mechanic(card.get("id", ""), result)


# Maps framework-card id × result into actual state changes. Was
# missing in the first cut — framework cards logged flavor but
# didn't move/heal/search. User noticed: "the player should be
# able to play the cards they chose in the order they wanted, right,
# it seems to do it automatically?" → because nothing visibly
# happened from a click, the player couldn't tell their action
# landed.
func _apply_framework_card_mechanic(cid: String, result: String) -> void:
	match cid:
		"walk":
			match result:
				"ss":   _prompt_pick_destination(2, "walked")
				"s":    _prompt_pick_destination(1, "walked")
				"fail":
					_prompt_pick_destination(1, "stumbled toward")
					_time = max(0, _time - 1)
		"sprint":
			match result:
				"ss":   _prompt_pick_destination(3, "sprinted")
				"s":
					_prompt_pick_destination(2, "sprinted")
					_time = max(0, _time - 1)
				"fail":
					_prompt_pick_destination(1, "sprinted poorly")
					_time = max(0, _time - 2)
		"search":
			# At a search space, take the top item.
			var pile_id := _pile_at_pos(_player_pos)
			if pile_id == "":
				_log_line("[i]no search pile at %s[/i]" % _player_pos)
				return
			match result:
				"ss":   _take_top_item_at_pos(); _take_top_item_at_pos()  # peek+take
				"s":    _take_top_item_at_pos()
				"fail": pass
		"short_rest":
			match result:
				"ss":   _health = min(5, _health + 2)
				"s":    _health = min(5, _health + 1)
				"fail": pass
		"long_rest":
			match result:
				"ss":   _health = min(5, _health + 3)
				"s":    _health = min(5, _health + 2)
				"fail":
					_health = min(5, _health + 1)
					_time = max(0, _time - 1)
		"focus":
			# Successful FOCUS lowers Inertia by 1 (sharpens you against
			# the room). Failure no-ops.
			if result == "ss":
				_inertia = max(0, _inertia - 2)
			elif result == "s":
				_inertia = max(0, _inertia - 1)
		"distraction":
			match result:
				"ss":
					_pop_top_gravity_card()
					_prompt_pick_destination(1, "moved")
				"s":
					_pop_top_gravity_card()
				"fail":
					_inertia = min(12, _inertia + 1)
		"guard":
			# Sets a flag that next Gravity-card Inertia tick is ignored.
			if result == "ss" or result == "s":
				_flags["guard_ignore_next_gravity_inertia"] = true
				if result == "ss":
					_prompt_pick_destination(1, "moved on guard")
		"close_call":
			# Reroll — for now, no-op past the dice roll itself. (A real
			# reroll requires tracking the last-rolled card; future pass.)
			pass
		"spend_it":
			_time += 1
			_log_line("[color=#7cffb0]✦ SPEND IT: +1 Time[/color]  (Time → %d)" % _time)
		"improvise":
			# Replays the last-played card's mechanic. Currently no-op
			# until we track last-played card state.
			pass


func _pop_top_gravity_card() -> void:
	if _gravity_draw_pile.is_empty():
		return
	var cid: String = _gravity_draw_pile.pop_back()
	_gravity_discard_pile.append(cid)
	_log_line("[i]cancelled next Gravity card: %s[/i]" % cid)


func _roll_arcana_dice(n: int) -> Dictionary:
	# Pull faces from _die
	var faces: Array = _die.get("die", {}).get("faces", [])
	if faces.is_empty():
		return {"result": "fail", "line": "(no die data)"}
	var n_ss := 0
	var n_s := 0
	var n_fail := 0
	var parts: PackedStringArray = []
	for i in n:
		var face: Dictionary = faces[randi() % faces.size()]
		var r: String = face.get("result", "fail")
		# Wild face — DOG counts as ★ if faith adjacent
		if r == "wild":
			var faith_st: Dictionary = _visitors_state.get("faith", {})
			if faith_st.get("pos", "") == _player_pos:
				r = "s"
			else:
				r = "fail"
		parts.append(String(face.get("symbol", "?")))
		match r:
			"ss": n_ss += 1
			"s":  n_s  += 1
			_:    n_fail += 1
	var result: String = "fail"
	if n_ss > 0:
		result = "ss"
	elif n_s > 0:
		result = "s"
	return {"result": result, "line": " ".join(parts)}


# ── Phase advance + Shadow/Drift/Upkeep ─────────────────────────────

func _on_advance() -> void:
	if _game_over:
		return
	match _phase:
		Phase.ACTION:
			_phase = Phase.PLANNING
			_phase_planning()
		Phase.PLANNING:
			_phase = Phase.SHADOW
			_phase_shadow()
		Phase.SHADOW:
			_phase = Phase.DRIFT
			_phase_drift()
		Phase.DRIFT:
			_phase = Phase.UPKEEP
			_phase_upkeep()
		Phase.UPKEEP:
			_phase = Phase.ACTION
			_phase_action()
	_render()


func _phase_action() -> void:
	# Start of new turn — increment, reset played-this-turn
	_turn += 1
	_played_this_turn.clear()
	# Default inertia tick (gravity of the room)
	_inertia = min(12, _inertia + 1)
	_log_line("\n[color=#c8a268][b]── turn %d ──[/b][/color]" % _turn)
	# Visitor arrivals scheduled for this turn
	for vid in _visitors_state:
		var st: Dictionary = _visitors_state[vid]
		if not st.get("arrived", false) and st.has("scheduled_turn"):
			if int(st["scheduled_turn"]) <= _turn:
				st["arrived"] = true
				st["pos"] = st.get("arrival_pos", "counter")
				var name_s: String = _visitors_def.get(vid, {}).get("name", vid)
				_log_line("[i]→ %s arrives at %s[/i]" % [name_s, st["pos"]])


func _phase_planning() -> void:
	# Free reset of starters back into hand if they were played
	for cid: String in _action_cards.keys():
		var card: Dictionary = _action_cards[cid]
		if card.get("starter", false) and not (cid in _hand_cards):
			_hand_cards.append(cid)
	# Final Girl economy: leftover Time CARRIES OVER and adds on top
	# of the per-turn base. So ending with 2 unspent → next turn starts
	# with 6 + 2 = 8. Encourages efficient turns without punishing big
	# saves for a planned splurge.
	var carry: int = _time
	_time = carry + _next_time_reset
	_next_time_reset = int((_setup.get("starting_state", {}) as Dictionary).get("time_per_turn", 6))
	# If the Bindle has been assembled but LEAP isn't in hand yet,
	# add it now. (LEAP is awarded by BUNDLE, never purchased.)
	if _bindle_assembled and not ("leap" in _hand_cards):
		_hand_cards.append("leap")
		_log_line("[color=#ffd07a][b]LEAP added to your hand.[/b][/color]")
	if carry > 0:
		_log_line("[color=#c8a268][i]planning. Time = %d carried + %d base = %d.[/i][/color]" %
			[carry, _next_time_reset, _time])
	else:
		_log_line("[color=#c8a268][i]planning. Time reset to %d. Click TABLEAU cards (above hand) to buy.[/i][/color]" % _time)


func _phase_shadow() -> void:
	if _gravity_draw_pile.is_empty():
		_log_line("[i]gravity deck empty[/i]")
		return
	var cid: String = _gravity_draw_pile.pop_back()
	_gravity_discard_pile.append(cid)
	_audio_sfx("gravity_draw")
	var card: Dictionary = _find_gravity_card(cid)
	_gravity_last_drawn = card
	_log_line("[color=#ff8060][b]GRAVITY:[/b] %s[/color]" % card.get("title", cid))
	_log_line("[i]%s[/i]" % card.get("flavor", ""))
	_gravity_card_label.text = "[color=#c8a268]GRAVITY[/color]\n[b]%s[/b]\n[i]%s[/i]" % [card.get("title", cid), card.get("flavor","")]
	_show_toast("Gravity: [b]%s[/b]" % card.get("title", cid), "#ff8060")
	_resolve_effects(card.get("effects", []))
	# Inertia ≥ 7: extra draw per the inertia thresholds spec
	if _inertia >= 7 and not _gravity_draw_pile.is_empty():
		var cid2: String = _gravity_draw_pile.pop_back()
		_gravity_discard_pile.append(cid2)
		var card2: Dictionary = _find_gravity_card(cid2)
		_log_line("[color=#ff8060][b]GRAVITY (bonus):[/b] %s[/color]" % card2.get("title", cid2))
		_resolve_effects(card2.get("effects", []))


func _find_gravity_card(cid: String) -> Dictionary:
	for c: Dictionary in _gravity_deck_def.get("cards", []):
		if c.get("id", "") == cid:
			return c
	return {}


func _phase_drift() -> void:
	# Inertia thresholds: place CLAIM markers
	if _inertia >= 8:
		_place_claim_marker(false)
	if _inertia >= 10:
		_place_claim_marker(true)
	# Claim countdowns: consume visitors at countdown end
	var max_turns := int(_setup.get("claim_turns_to_consume", 2))
	for vid in _visitors_state:
		var st: Dictionary = _visitors_state[vid]
		var claim: int = int(st.get("claimed_turn", -1))
		if claim >= 0 and not st.get("connected", false):
			if (_turn - claim) >= max_turns:
				st["arrived"] = false
				st["pos"] = ""
				st["consumed"] = true
				_log_line("[color=#ff6060]✕ %s consumed by the room.[/color]" % _visitors_def.get(vid, {}).get("name", vid))
	# Counter-haunted flag: standing on COUNTER adds +1 Inertia
	if _counter_haunted and _player_pos == "counter":
		_inertia = min(12, _inertia + 1)
		_log_line("[color=#ff8060]+1 Inertia (counter is calling)[/color]")


func _place_claim_marker(skip_first: bool) -> void:
	# Closest unconnected, unclaimed visitor on the board
	var candidates: Array = []
	for vid in _visitors_state:
		var st: Dictionary = _visitors_state[vid]
		if (st.get("arrived", false) and not st.get("connected", false)
			and int(st.get("claimed_turn", -1)) < 0):
			candidates.append(vid)
	if candidates.is_empty():
		return
	# Just pick first for now (could measure adjacency-distance later)
	var pick_idx := 0
	if skip_first and candidates.size() > 1:
		pick_idx = 1
	var vid: String = candidates[pick_idx]
	_visitors_state[vid]["claimed_turn"] = _turn
	_log_line("[color=#ff8060]CLAIM marker on %s[/color]" % _visitors_def.get(vid, {}).get("name", vid))


func _phase_upkeep() -> void:
	# Faith adjacent → −1 Inertia
	var faith_st: Dictionary = _visitors_state.get("faith", {})
	if faith_st.get("arrived", false) and faith_st.get("pos", "") == _player_pos:
		_inertia = max(0, _inertia - 1)
		_log_line("[color=#7cffb0]Faith steady · -1 Inertia[/color]")
	# Precipice door reveal check
	var present := 0
	for vid in _visitors_state:
		if _visitors_state[vid].get("arrived", false):
			present += 1
	if present >= 4 and not _flags.get("precipice_revealed", false):
		_flags["precipice_revealed"] = true
		_log_line("[color=#7cffb0]✦ the Precipice Door is now visible.[/color]")
	_check_game_end()


# ── End conditions ──────────────────────────────────────────────────

func _check_game_end() -> void:
	if _game_over:
		return
	# Inertia 12
	if _inertia >= 12:
		_trigger_loss("inertia_12")
		return
	# Three Visitors claimed
	var consumed := 0
	for vid in _visitors_state:
		if _visitors_state[vid].get("consumed", false):
			consumed += 1
	if consumed >= 3:
		_trigger_loss("visitors_claimed_3")
		return


func _trigger_win(threshold: String) -> void:
	_game_over = true
	_audio_sfx("win")
	# Find threshold's ending lore token
	var ending_token := ""
	for t: Dictionary in _setup.get("thresholds", []):
		if t.get("id", "") == threshold:
			ending_token = t.get("ending_lore_token", "")
	if ending_token != "":
		_collect_lore_token(ending_token)
	# Persist
	var contents := ""
	for it in _inventory:
		if String(it).begins_with("contents_"):
			contents = it
			break
	GauntletState.record_win(_arcana_id, _location_id, contents, _lore_tokens_collected, "")
	_show_end_screen(true, "★ THE LEAP",
		"From the %s — '%s'\n\nThe leap rendered.\n%d Lore Tokens collected." %
		[threshold, ending_token, _lore_tokens_collected.size()])
	game_ended.emit("win", {
		"threshold": threshold,
		"contents": contents,
		"lore_tokens": _lore_tokens_collected,
	})


func _trigger_loss(reason: String) -> void:
	_game_over = true
	_audio_sfx("loss")
	# Pick a Finale for the reason
	var finale_id := ""
	var finale_title := ""
	var finale_flavor := ""
	var candidates: Array = []
	for f: Dictionary in _finale_def.get("finales", []):
		if f.get("triggered_by", "") == reason:
			candidates.append(f)
	if candidates.is_empty() and not _finale_def.get("finales", []).is_empty():
		candidates = _finale_def["finales"]
	if not candidates.is_empty():
		var f: Dictionary = candidates[randi() % candidates.size()]
		finale_id = f.get("id", "")
		finale_title = f.get("title", "")
		finale_flavor = f.get("flavor", "")
	GauntletState.record_loss(_arcana_id, _location_id, finale_id, _lore_tokens_collected)
	_show_end_screen(false, "REVERSED · " + finale_title, finale_flavor)
	game_ended.emit("loss", {
		"reason": reason,
		"finale": finale_id,
		"lore_tokens": _lore_tokens_collected,
	})


func _show_end_screen(won: bool, title: String, body: String) -> void:
	if _end_overlay != null:
		_end_overlay.queue_free()
	_end_overlay = Control.new()
	_end_overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_end_overlay.z_index = 200
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.78)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_STOP
	_end_overlay.add_child(dim)
	var panel := PanelContainer.new()
	panel.set_anchors_preset(Control.PRESET_CENTER)
	panel.offset_left = -360
	panel.offset_right = 360
	panel.offset_top = -160
	panel.offset_bottom = 160
	panel.add_theme_stylebox_override("panel", _make_panel_style())
	_end_overlay.add_child(panel)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 14)
	panel.add_child(vb)
	var t := Label.new()
	t.text = title
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	t.add_theme_color_override("font_color", C_GOOD if won else C_BAD)
	t.add_theme_font_size_override("font_size", 22)
	vb.add_child(t)
	var b := RichTextLabel.new()
	b.bbcode_enabled = true
	b.fit_content = true
	b.size_flags_vertical = Control.SIZE_EXPAND_FILL
	b.text = "[i]%s[/i]\n\nLore Tokens: %s" % [body, ", ".join(_lore_tokens_collected)]
	b.add_theme_color_override("default_color", C_TEXT)
	vb.add_child(b)
	var btn := Button.new()
	btn.text = "Leave"
	btn.pressed.connect(_on_leave)
	vb.add_child(btn)
	add_child(_end_overlay)


func _on_leave() -> void:
	game_ended.emit("leave", {})
	queue_free()
