extends Control
## Tarot Gauntlet — main controller for one arcana scenario.
## Walks the 5-phase loop: Action → Planning → Shadow → Drift → Upkeep.
## Loads data from godot/resources/games/.

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
var _codex: TextureRect = null
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
var _board_meeple: Label = null
var _board_visitor_nodes: Dictionary = {}   # visitor_id → Label
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
	_load_data()
	_build_ui()
	_init_run()
	_audio_play_bgm()
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
	_log_line("[color=#7c8398]Hand: %s[/color]" % _hand_cards)
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
	return "res://assets/gallery/cards/" + _arcana_id + "_" + cid + ".png"

func _art_path_gravity(cid: String) -> String:
	return "res://assets/gallery/cards/" + _arcana_id + "_gravity_" + cid + ".png"

func _art_path_item(item_id: String) -> String:
	return "res://assets/gallery/items/" + _arcana_id + "_" + item_id + ".png"

func _art_path_visitor_face(vid: String) -> String:
	return "res://assets/gallery/" + vid + "_face.png"

func _art_path_board() -> String:
	return "res://assets/gallery/locations/" + _location_id + "_gauntlet_board.png"


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
	_time       = int(start.get("time", 6))
	_next_time_reset = _time
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
	_player_pos_label = _make_track_label("at: counter")
	_bindle_label   = _make_track_label("Bindle: —")
	for lbl in [_phase_label, _turn_label, _time_label, _inertia_label, _health_label, _player_pos_label, _bindle_label]:
		top_hb.add_child(lbl)

	# ── Left/center: location board ──────────────────────────────────
	_board_root = Control.new()
	_board_root.set_anchors_preset(Control.PRESET_LEFT_WIDE)
	_board_root.offset_top = 52
	_board_root.offset_left = 8
	_board_root.offset_bottom = -214
	_board_root.offset_right = -440
	var board_panel := PanelContainer.new()
	board_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	board_panel.add_theme_stylebox_override("panel", _make_panel_style())
	_board_root.add_child(board_panel)
	add_child(_board_root)
	_render_board()

	# ── Right column: codex card + gravity card + visitor states + log
	var right := VBoxContainer.new()
	right.set_anchors_preset(Control.PRESET_RIGHT_WIDE)
	right.offset_top = 52
	right.offset_right = -8
	right.offset_left = -432
	right.offset_bottom = -214
	right.add_theme_constant_override("separation", 6)
	add_child(right)

	# Codex card (the gallery image, pinned) — fixed size, NOT expand_fill
	# (was eating all the right-column height and squeezing the log to
	# nothing).
	var codex_panel := PanelContainer.new()
	codex_panel.add_theme_stylebox_override("panel", _make_panel_style())
	codex_panel.custom_minimum_size = Vector2(420, 180)
	var codex_vb := VBoxContainer.new()
	codex_panel.add_child(codex_vb)
	var codex_title := Label.new()
	codex_title.text = "  CODEX"
	codex_title.add_theme_color_override("font_color", C_ACCENT)
	codex_title.add_theme_font_size_override("font_size", 11)
	codex_vb.add_child(codex_title)
	_codex = TextureRect.new()
	_codex.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_codex.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_codex.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_codex.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var codex_path: String = _location.get("bg_codex_card", "res://assets/gallery/fool.png")
	if not codex_path.begins_with("res://"):
		codex_path = "res://" + codex_path
	if ResourceLoader.exists(codex_path):
		_codex.texture = ResourceLoader.load(codex_path) as Texture2D
	codex_vb.add_child(_codex)
	right.add_child(codex_panel)

	# Gravity card display — single thin line. Shows deck size before
	# any draw ("Gravity deck: 12 remaining"), then the drawn card's
	# title + flavor.
	var grav_panel := PanelContainer.new()
	grav_panel.add_theme_stylebox_override("panel", _make_panel_style())
	grav_panel.custom_minimum_size = Vector2(420, 56)
	_gravity_card_label = RichTextLabel.new()
	_gravity_card_label.bbcode_enabled = true
	_gravity_card_label.fit_content = true
	_gravity_card_label.add_theme_color_override("default_color", C_TEXT)
	_gravity_card_label.text = "[color=#c8a268]GRAVITY DECK[/color] — 12 cards remaining"
	grav_panel.add_child(_gravity_card_label)
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
	var v_title := Label.new()
	v_title.text = "  VISITORS"
	v_title.add_theme_color_override("font_color", C_ACCENT)
	v_title.add_theme_font_size_override("font_size", 11)
	v_vb.add_child(v_title)
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
	bottom.offset_top = -210
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
	var log_title := Label.new()
	log_title.text = "  LOG"
	log_title.add_theme_color_override("font_color", C_ACCENT)
	log_title.add_theme_font_size_override("font_size", 10)
	log_vb.add_child(log_title)
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
	_tableau_scroll.custom_minimum_size = Vector2(540, 60)
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
	hand_scroll.custom_minimum_size = Vector2(540, 60)
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


func _make_track_label(text: String) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_color_override("font_color", C_TEXT)
	l.add_theme_font_size_override("font_size", 12)
	return l


# ── Board rendering ──────────────────────────────────────────────────

func _render_board() -> void:
	# Clear
	for c in _board_root.get_children():
		if c.name.begins_with("space_") or c.name.begins_with("visitor_") or c.name == "player_meeple" or c.name == "board_bg":
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
		bg.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		bg.modulate = Color(1, 1, 1, 0.55)
		bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_board_root.add_child(bg)
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
	var panel_size: Vector2 = _board_root.size
	if panel_size.x <= 0:
		panel_size = Vector2(700, 480)
	var sx: float = (panel_size.x - 80) / maxf(1.0, bx_max - bx_min)
	var sy: float = (panel_size.y - 60) / maxf(1.0, by_max - by_min)
	for s: Dictionary in spaces:
		var sid: String = s.get("id", "")
		if not s.get("always_visible", true) and sid != "precipice_door":
			continue
		# Hide Precipice Door if not yet revealed
		if sid == "precipice_door" and not _flags.get("precipice_revealed", false):
			continue
		var xy2: Array = s.get("pos_xy", [0, 0])
		var nx: float = (float(xy2[0]) - bx_min) * sx + 40.0
		var ny: float = (float(xy2[1]) - by_min) * sy + 30.0
		var node := _make_space_label(s)
		node.position = Vector2(nx - 60.0, ny - 14.0)
		node.name = "space_" + sid
		_board_root.add_child(node)
		_board_space_nodes[sid] = node
	# Player meeple
	_board_meeple = Label.new()
	_board_meeple.text = "★ John"
	_board_meeple.add_theme_color_override("font_color", C_ACCENT)
	_board_meeple.add_theme_font_size_override("font_size", 14)
	_board_meeple.name = "player_meeple"
	_board_root.add_child(_board_meeple)
	# Visitor meeples
	for vid in _visitors_state:
		var v: Dictionary = _visitors_state[vid]
		if v.get("arrived", false):
			var vdef: Dictionary = _visitors_def[vid]
			var lbl := Label.new()
			lbl.text = "● " + vdef.get("name", vid)
			lbl.add_theme_color_override("font_color", Color(vdef.get("accent", "#c8a268")))
			lbl.add_theme_font_size_override("font_size", 11)
			lbl.name = "visitor_" + vid
			_board_root.add_child(lbl)
			_board_visitor_nodes[vid] = lbl
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
	l.mouse_filter = Control.MOUSE_FILTER_PASS
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
			_audio_sfx("card_play")
			_log_line("→ %s to [b]%s[/b]" % [reason, _player_pos])
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
	_audio_sfx("card_play")
	_log_line("→ walked to [b]%s[/b]" % target_pos)
	_render()


func _position_meeples() -> void:
	# Player at current pos
	if _board_meeple and _board_space_nodes.has(_player_pos):
		var anchor: Label = _board_space_nodes[_player_pos]
		_board_meeple.position = anchor.position + Vector2(0, 18)
	# Visitors at their positions
	var vid_pos_stack: Dictionary = {}   # pos → stack offset count
	for vid in _board_visitor_nodes:
		var v: Dictionary = _visitors_state[vid]
		var p: String = v.get("pos", "")
		if _board_space_nodes.has(p):
			var anchor2: Label = _board_space_nodes[p]
			var idx: int = int(vid_pos_stack.get(p, 0))
			vid_pos_stack[p] = idx + 1
			_board_visitor_nodes[vid].position = anchor2.position + Vector2(0, 36 + idx * 14)


# ── Hand + visitor rendering ─────────────────────────────────────────

func _render_hand() -> void:
	for c in _hand_box.get_children():
		c.queue_free()
	for cid in _hand_cards:
		var card: Dictionary = _action_cards.get(cid, {})
		var btn := Button.new()
		var time_cost: int = int(card.get("time_cost", 1))
		btn.text = "%s\n[%d]" % [card.get("title", cid), time_cost]
		btn.add_theme_font_size_override("font_size", 9)
		btn.custom_minimum_size = Vector2(84, 50)
		btn.clip_text = true
		btn.tooltip_text = String(card.get("flavor", "")) + "\n\n" + _card_summary(card)
		var art: Texture2D = _load_texture_silent(_art_path_card(cid))
		if art:
			btn.icon = art
			btn.expand_icon = true
			btn.vertical_icon_alignment = VERTICAL_ALIGNMENT_TOP
		var playable: bool = _can_play_card(card)
		btn.disabled = (not playable) or (_phase != Phase.ACTION) or _game_over
		btn.pressed.connect(_on_play_card.bind(cid))
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
		var btn := Button.new()
		btn.text = "%s\n[%d]" % [card.get("title", cid), time_cost]
		btn.add_theme_font_size_override("font_size", 9)
		btn.custom_minimum_size = Vector2(84, 50)
		btn.clip_text = true
		btn.tooltip_text = String(card.get("flavor", "")) + "\n\n" + _card_summary(card)
		var art: Texture2D = _load_texture_silent(_art_path_card(cid))
		if art:
			btn.icon = art
			btn.expand_icon = true
			btn.vertical_icon_alignment = VERTICAL_ALIGNMENT_TOP
		# Buyable during PLANNING + Time ≥ cost
		var can_buy: bool = (_phase == Phase.PLANNING) and (_time >= time_cost) and not _game_over
		btn.disabled = not can_buy
		# Dim style outside planning so it reads as preview, not shop
		if _phase != Phase.PLANNING:
			btn.modulate = Color(0.7, 0.65, 0.55, 0.7)
		btn.pressed.connect(_on_buy_card.bind(cid))
		_tableau_box.add_child(btn)


func _on_buy_card(cid: String) -> void:
	if _phase != Phase.PLANNING or _game_over:
		return
	var card: Dictionary = _action_cards.get(cid, {})
	var time_cost: int = int(card.get("time_cost", 1))
	if _time < time_cost:
		_log_line("[i]not enough Time to buy %s (need %d, have %d)[/i]" %
			[card.get("title", cid), time_cost, _time])
		return
	_time -= time_cost
	_hand_cards.append(cid)
	_audio_sfx("card_play")
	_log_line("[color=#7cffb0]✦ bought [b]%s[/b][/color]  (Time %d → %d)" %
		[card.get("title", cid), _time + time_cost, _time])
	_render()


func _card_summary(card: Dictionary) -> String:
	# For framework cards (with ★★/★/✕ lines)
	if card.has("double_success"):
		return "★★ %s\n★ %s\n✕ %s" % [
			card.get("double_success",""),
			card.get("single_success",""),
			card.get("failure",""),
		]
	# For arcana cards with effect lists, summarize key effects
	var lines: PackedStringArray = []
	for e: Dictionary in card.get("effects", []):
		lines.append("· " + str(e))
	return "\n".join(lines)


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
	if _bindle_assembled and not ("leap" in _hand_cards):
		_hand_cards.append("leap")
		_log_line("[color=#ffd07a][b]LEAP in hand[/b] — bindle assembled.[/color]")
	_phase_label.text = "PHASE: " + Phase.keys()[_phase]
	_turn_label.text  = "Turn %d" % _turn
	_time_label.text  = "Time %d / %d" % [_time, _next_time_reset]
	_inertia_label.text = "Inertia %d / 12" % _inertia
	_health_label.text  = "Health %d" % _health
	_player_pos_label.text = "at: " + _player_pos
	_bindle_label.text = "Bindle: " + _bindle_display()
	# Rebuild the board so the » chevron + highlight color follow
	# the player to their new space. Cheap (~20 labels).
	_render_board()
	_position_meeples()
	_render_hand()
	_render_tableau()
	_render_visitors()
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
	if _log == null:
		print("[Gauntlet] " + s)
		return
	_log.append_text(s + "\n")


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
	# Tableau cards (framework core): do a Threshold Roll
	if card.has("double_success"):
		_resolve_framework_card(card)
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
			var n: int = int(e.get("amount", 0))
			while n > 0 and not _hand_cards.is_empty():
				_hand_cards.pop_back()
				n -= 1
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
		_:
			_log_line("[i](unhandled effect: %s)[/i]" % kind)


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
	if v.has("lore_token"):
		_collect_lore_token(v["lore_token"])


func _collect_lore_token(token: String) -> void:
	if token == "" or token in _lore_tokens_collected:
		return
	_lore_tokens_collected.append(token)
	_log_line("[color=#ffd07a]✦ lore token: %s[/color]" % token)


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
	# on_pickup hooks
	if item.has("on_pickup"):
		_resolve_effects(item["on_pickup"])
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
	_time = _next_time_reset
	_next_time_reset = 6
	# If the Bindle has been assembled but LEAP isn't in hand yet,
	# add it now. (LEAP is awarded by BUNDLE, never purchased.)
	if _bindle_assembled and not ("leap" in _hand_cards):
		_hand_cards.append("leap")
		_log_line("[color=#ffd07a][b]LEAP added to your hand.[/b][/color]")
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
