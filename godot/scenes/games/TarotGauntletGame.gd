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


# Outcome capture · the value emitted to game_ended when the player
# dismisses the end screen via _on_leave. Defaults to "leave" with
# no summary if the run was abandoned before win/loss was recorded.
# Set by record_win / record_loss paths so the host scripts get a
# real payload instead of "leave", {}.
var _last_outcome: String = "leave"
var _last_summary: Dictionary = {}

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
var _step_defaults_by_mood: Dictionary = {}  # mood → {step → fallback line}
# Live-queue at ORDER WINDOW: order_item_id → bool (true = pending,
# waiting for bell; false = ready to be picked up). LISTEN spawns
# pending; ADDRESS THE BELL marks oldest pending → ready; PICK UP at
# order_window only takes ready items.
var _order_pending: Dictionary = {}
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
var _sanity: int = 5
var _sanity_max: int = 5
# ── Magician-arcana state ─────────────────────────────────────────
# These mirror the Fool's Inertia + Sanity pattern but with the
# Magician's maker-loop semantics:
#   · _stagnation : rises bad, max kills. The room insisting.
#   · _doubt      : rises bad, max kills. The maker's internal fight.
#   · _inspiration: positive currency. Spent by BURN / BUILD /
#                   TRANSMIT / HUSK; gained from RECORD, NICOLA
#                   WROTE AGAIN, etc.
# Engine reads them defensively — if the scenario's setup doesn't
# declare them, they stay at 0 and never trigger.
var _stagnation: int = 0
var _stagnation_per_turn: int = 1
var _doubt: int = 0
var _doubt_max: int = 7
var _inspiration: int = 0
# Magician-specific tracked state. piece progress per space (each
# inner-cluster station has a hidden "piece" the player advances);
# WIP-model progress for the outer-cluster sandbox arcanas; the
# steamboat as its own track; sealed-arcana set.
var _piece_progress: Dictionary = {}        # space_id → int
var _piece_threshold: int = 3               # default beats per piece
var _pieces_completed: int = 0
var _wip_progress: Dictionary = {}          # wip_id → int (max from location.wip_models)
var _wips_completed_this_run: Dictionary = {}
var _steamboat_progress: int = 0
var _steamboat_threshold: int = 6
# Priestess (II) state — the master reel is Elicia's equivalent of
# the steamboat doom-clock. Each RECORD action ticks the reel by 1;
# at threshold the reel is full (loss in some scenarios, lockout in
# others). Insight is the spendable currency parallel to Frasier's
# Inspiration. Default zero / inert for non-Priestess runs.
var _master_reel: int = 0
var _master_reel_threshold: int = 6
var _insight: int = 0
# Pomegranate Hour episode states (Priestess only). The six episode
# spaces each carry a state on the ladder TITLE_CARD_ONLY → PAPER_ONLY
# → FOOTAGE_ONLY → ASSEMBLY → PICTURE_LOCK_NO_SOUND → LOCKED. Episodes
# can be advanced one state at a time during a run. The count of
# advances is the win-condition counter for require_episodes_advanced_min.
var _episode_states: Dictionary = {}        # space_id → state_id (String)
var _episode_state_ladder: Array = [
	"TITLE_CARD_ONLY", "PAPER_ONLY", "FOOTAGE_ONLY",
	"ASSEMBLY", "PICTURE_LOCK_NO_SOUND", "LOCKED"
]
var _episodes_advanced_this_run: int = 0
# Count of completed sit_with steps with cast/crew (kind == "cast_crew")
# visitors during this run. Required by Pomegranate win conditions to
# distinguish a sit_with with a friend from a lock with a subject of
# the art.
var _cast_crew_sit_with_count: int = 0
# Empress (III) state — Bloom is the POSITIVE doom-clock: rises good,
# opposite of Stagnation. Harvest is the spendable currency (countable
# crops in the pantry). Both default zero/inert for non-empress runs.
var _bloom: int = 0
var _bloom_threshold: int = 6
var _harvest: int = 0
# Emperor (IV) state — Authority is the spendable currency (parallel
# to Inspiration/Insight/Harvest). Ledger is the positive doom-clock,
# rises good — each STAMP/WITNESS enters a ruling. Default zero/inert
# for non-emperor runs.
var _authority: int = 0
var _ledger: int = 0
var _ledger_threshold: int = 6
# Hierophant (V) state — Doctrine is the currency, Signal is the
# positive doom-clock. Same shape as previous arcanas (rises good,
# capped at threshold, optional loss when full).
var _doctrine: int = 0
var _signal: int = 0
var _signal_threshold: int = 6
# Lovers (VI) state — SYNC is the positive doom-clock; VERB is the
# spendable currency. Default zero/inert for non-lovers runs. The
# "partner" is the visitor flagged is_lovers_partner; their position
# (from _visitors_state) drives the partner_at_my_pos predicate.
var _sync: int = 0
var _sync_threshold: int = 6
var _verb: int = 0
var _lovers_partner_id: String = ""
# Chariot (VII) state — MILES is the positive doom-clock (must reach
# threshold to leap at destination); FUEL is the spendable currency.
var _miles: int = 0
var _miles_threshold: int = 6
var _fuel: int = 0
# Patience-freeze counter (THE LONG QUIET ability + freeze_patience
# effect): while > 0, _tick_visitor_patience does nothing on Upkeep.
# Decrements once per turn at Upkeep.
var _patience_frozen_turns: int = 0
# Patched-space pairs — while present, the two named spaces are
# treated as one for visitor proximity / connection (lets a visitor
# in the booth be "addressable" from the lounge). Decay turns at
# Upkeep; entries with turns<=0 are cleaned up.
var _patched_pairs: Array = []   # [{a, b, turns}, ...]
var _sealed_arcanas: Dictionary = {}        # space_id → true while sealed
var _next_gravity_canceled: bool = false
var _active_demons: Dictionary = {}         # demon_id → turns_left
var _player_pos: String = "counter"
var _hand_cards: Array = []     # array of card ids currently in hand
# Per-card stock counts for tableau buys. Each non-starter card
# carries a finite stock that decrements on purchase. When stock
# hits 0 the card disappears from the tableau. Default stock comes
# from the card's `stock` field (JSON), or 2 if unspecified. The
# tile renders the remaining stock so the player always knows.
var _tableau_stock: Dictionary = {}  # cid → int
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
# Per-run achievement tracking — populated as the run progresses,
# read by _evaluate_achievements at win/loss to decide which entries
# in resources/achievements.json have newly fired.
var _cards_played_this_run: Dictionary = {}   # card_id → count
var _claimed_visitors_count: int = 0
var _last_finale_id: String = ""              # populated by _trigger_loss
# Cross-arcana world state — populated at run start from
# resources/world_state.json, filtered to states whose save_key is
# unlocked. Active ambient_lines are merged into the run's pool;
# active gravity_extras are appended to the deck before shuffle.
var _world_state_ambient_lines: Array = []
var _world_state_active_ids: Array = []        # for log + diagnostics
var _lore_tokens_collected: Array = []
var _twelve_years_used: bool = false
var _call_faith_count: int = 0
var _game_over: bool = false

# ── UI refs (built in _build_ui) ─────────────────────────────────────
var _bg: ColorRect = null
var _inv_summary_label: RichTextLabel = null
var _phase_label: Label = null
var _turn_label: Label = null
var _time_label: Label = null
var _inertia_label: Label = null
var _sanity_label: Label = null
var _stagnation_label: Label = null
var _doubt_label: Label = null
var _inspiration_label: Label = null
var _pieces_label: Label = null
var _player_pos_label: Label = null
var _bindle_label: Label = null

# Live BGM mood manipulator — attaches LowPass + Distortion to the
# BGM bus and is fed by _stagnation / _doubt every _render(). Magician
# only; for the Fool the manipulator is created (so the bus is in a
# known state) but stays at neutral (no muffle, no distortion).
const TarotAudioManipulatorScene := preload("res://scenes/games/TarotAudioManipulator.gd")
const CARD_FACE := preload("res://scenes/games/GauntletCardFace.gd")
var _audio_manipulator: Node = null
var _visitors_box: VBoxContainer = null
var _hand_box: HBoxContainer = null
var _tableau_box: HBoxContainer = null
var _tableau_scroll: ScrollContainer = null
var _log: RichTextLabel = null
var _advance_btn: Button = null
var _board_root: Control = null
var _board_content: Control = null
var _board_expand_btn: Button = null
var _board_bg_btn: Button = null
# Default OFF — the painted board art (when present) is loose-fit
# atmospheric texture and tends to compete with the engine-drawn
# markers + labels. Player can toggle it back on via the MAP header.
var _board_bg_visible: bool = false
var _board_fullscreen_exit_btn: Button = null   # viewport-level overlay
# Computed each _render_board: scales markers/meeples/labels to fit
# the actual board content size (normal vs fullscreen).
var _board_ui_scale: float = 1.0
var _board_visitor_stack_offset: float = 14.0
var _board_fullscreen: bool = false
# View mode: "fp" (1st-person at current space, default) or "map"
# (top-down board with all markers + meeples). Fullscreen toggle
# also flips into "map". Hit the same button to return to FP.
var _view_mode: String = "fp"
# Last-rendered stat values, used by _render to flash labels on change
var _last_rendered_time: int = -1
var _last_rendered_inertia: int = -1
var _last_rendered_sanity: int = -1
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
# Per-turn cost bump from Gravity effects (e.g. THE FLUORESCENT TICK).
# Reset at the start of each ACTION phase.
var _this_turn_cost_bump_min: int = 99
var _this_turn_cost_bump_amt: int = 0
# Framework-card buffs that apply to the NEXT framework dice roll:
# FOCUS grants bonus dice, CLOSE CALL grants reroll behavior, both
# consumed by the next _resolve_framework_card call.
var _next_roll_bonus_dice: int = 0
var _next_roll_close_call: String = ""   # "" | "double_take_best" | "extra_die"
# IMPROVISE replays the last-played card. Track its id so the
# IMPROVISE card itself can find it.
var _last_played_cid: String = ""
var _board_meeple: Control = null
var _board_visitor_nodes: Dictionary = {}   # visitor_id → Control (Label or TextureRect)
var _board_space_nodes: Dictionary = {}     # space_id → Label
var _board_marker_pos: Dictionary = {}      # space_id → Vector2 (marker center)
# Threats — spawned by Gravity cards, occupy a space, tick during UPKEEP
# until cleaned. Each entry: {id, def_id, pos}. Rendered as small icons
# right of the marker, same coordinate system as visitor meeples.
var _threats_def: Dictionary = {}           # def_id → def dict
var _threats_active: Array = []             # array of {id, def_id, pos}
var _threats_next_serial: int = 1
var _board_threat_nodes: Dictionary = {}    # threat instance id → Control
# FP-view scan-pan state. Held as members (not lambda captures) so
# we can null/replace cleanly on every render and never invoke a
# tween_callback against a freed bg node.
var _fp_bg: TextureRect = null
var _fp_scan_tween: Tween = null
# ── Lore / atmosphere tracking ────────────────────────────────────
# `_last_logged_pos` tracks the space we last surfaced an arrival
# beat for, so we don't spam the log on rapid renders. `_ambient_
# turn_offset` is randomised at run start so the ambient-pool
# cycle doesn't always fall on the same turns. `_last_steamboat_
# beat` keeps the steamboat ladder lines from re-firing on
# already-logged states.
var _last_logged_pos: String = ""
var _ambient_turn_offset: int = 0
var _last_steamboat_beat: int = -1
var _last_stagnation_tier: int = -1
var _last_doubt_tier: int = -1
# Pending visitor-arrival popups. When a turn brings 2+ visitors at
# once we show them sequentially — each modal's Acknowledge button
# pops the next from the queue.
var _visitor_arrival_queue: Array = []
var _gravity_card_label: RichTextLabel = null
var _end_overlay: Control = null
# Scenario id picked from the gallery, e.g. "the_leap", "lunch_rush",
# "evening_service". Names the setup_<id>.json file the engine
# loads, and optionally a gravity_deck_<id>.json variant.
var _scenario_id: String = "the_leap"
# Reversed mode — set by GalleryOverlay when the player picks the
# REVERSED tile for an arcana (only available after winning all 3
# of that arcana's difficulties). Applied as a stacking modifier on
# top of the underlying hard setup: +2 starting doubt, +2 stagnation,
# -1 starting time, -1 max_turns, tighter visitors_claimed_max.
var _reversed_mode: bool = false
# Escalation: every time the gravity deck recycles, the room
# "learns you." This bumps the per-turn Inertia tick by 1 and is
# announced in the log. THE LEAP rarely sees a reshuffle; longer
# scenarios see one or two.
var _room_attention: int = 0
# Counts deck recycles (incremented in _reshuffle_gravity_discard)
# so the log can name which wave the player is in.
var _gravity_recycle_count: int = 0

const C_BG: Color    = Color(0.045, 0.040, 0.030)
const C_PANEL: Color = Color(0.085, 0.070, 0.050, 1.0)
const C_BORDER: Color = Color(0.70, 0.55, 0.24, 0.45)
const C_TEXT: Color  = Color(0.86, 0.80, 0.66)
const C_DIM: Color   = Color(0.55, 0.50, 0.40)
const C_ACCENT: Color = Color(0.95, 0.78, 0.40)
const C_GOOD: Color  = Color(0.55, 0.95, 0.65)
const C_BAD: Color   = Color(0.95, 0.45, 0.45)

# How many turns a visitor will sit at progress 0 (no GREET yet)
# before they stand up and leave. The room's mood-shaped clock.
# Helpers and Faith are exempt. Per-visitor overrides via the
# `patience` field on the visitor def.
const PATIENCE_BY_MOOD := {
	"jovial":      8,
	"preoccupied": 6,
	"gruff":       5,
	"left_alone":  4,
}


# ── Entry point ──────────────────────────────────────────────────────

func start_scenario(arcana: String = "fool",
					location: String = "dambrosios",
					hand: String = "john_frank",
					scenario_id: String = "the_leap",
					reversed: bool = false) -> void:
	# Hosts have historically passed mixed-convention arcana ids:
	#   · bare         — "fool", "strength", "wheel_of_fortune"
	#   · numbered     — "0_fool", "8_strength"
	#   · roman        — "vi_lovers", "ii_priestess"
	# The data dirs under res://resources/games/ are bare names.
	# Strip any leading "<digits>_" or "<roman>_" so all three
	# conventions resolve to the same dir.
	_arcana_id = _normalize_arcana_id(arcana)
	_location_id = location
	_hand_id = hand
	_scenario_id = scenario_id
	_reversed_mode = reversed


# Strip a leading numeric or Roman-numeral index prefix from an
# arcana id ("0_fool" → "fool", "vi_lovers" → "lovers"). Inputs
# without a prefix pass through unchanged.
static func _normalize_arcana_id(raw: String) -> String:
	if raw == "":
		return raw
	var us: int = raw.find("_")
	if us <= 0:
		return raw
	var prefix: String = raw.substr(0, us)
	# Numeric prefix?
	if prefix.is_valid_int():
		return raw.substr(us + 1)
	# Roman numeral prefix? (lowercase or uppercase letters i v x l)
	var lower: String = prefix.to_lower()
	var is_roman: bool = (lower.length() > 0)
	for ch in lower:
		if ch not in "ivxl":
			is_roman = false
			break
	if is_roman:
		return raw.substr(us + 1)
	return raw


func _ready() -> void:
	add_to_group("ui")   # F4 master-toggle sweep (CLAUDE.md hard rule)
	set_process_unhandled_key_input(true)
	_load_data()
	_build_ui()
	_init_run()
	# Mid-run save state · attempt to resume a save for this exact
	# arcana+scenario. If a save exists, _apply_run_state overrides
	# the freshly-initialized state from _init_run. Audit Tier 2 fix.
	if _try_load_gauntlet_save():
		_log_line("[color=#a8c0a8][i]Resumed save · turn %d.[/i][/color]" % _turn)
	_audio_play_bgm()
	# Spawn the VnPortraitDebugOverlay here too. It's portrait-keyed
	# by default (will show "no portraits active" in gauntlet
	# context) BUT its LOCALE BG-3D + PERSISTENCE sections work
	# generically — letting the user open Shift+F12 and tweak the
	# gauntlet's bg-3D mood/lighting/style without exiting the run.
	# New GAUNTLET CAMERA section (added inside the overlay) targets
	# the current SubViewport's fp_camera so position / rotation /
	# FOV can be dialled live to find the right vantage per space.
	var overlay_script = load("res://scripts/vn/VnPortraitDebugOverlay.gd")
	if overlay_script != null:
		var ov = overlay_script.new()
		ov.name = "VnPortraitDebugOverlay"
		add_child(ov)
	# Attach the BGM mood manipulator. _render() will push live
	# stagnation/doubt values into it on every refresh.
	_audio_manipulator = TarotAudioManipulatorScene.new()
	_audio_manipulator.name = "TarotAudioManipulator"
	add_child(_audio_manipulator)
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
		_log_line("  setup_%s.json: %s" % [_scenario_id, ("OK" if not _setup.is_empty() else "[color=#ff6464]MISSING[/color]")])
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
	_log_line("[color=#7c8398]Phase: %s — click cards to play, then Advance →[/color]" %
		Phase.keys()[_phase])
	_log_line("")
	_render()
	# Pop the FULL LOG modal at game start so the player reads the
	# title + scene + direction hint full-screen before play begins.
	# Deferred so layout completes first.
	call_deferred("_open_pane_modal_by_key", "log")


func _unhandled_key_input(event: InputEvent) -> void:
	# Esc closes the topmost modal layer:
	#   1) drawn-card popup (gravity / item / etc.)
	#   2) pane modal (inventory / log / visitor card / etc.)
	#   3) board fullscreen
	if event is InputEventKey and (event as InputEventKey).pressed:
		var key: InputEventKey = event
		if key.keycode == KEY_ESCAPE:
			var drawn: Node = get_node_or_null("drawn_card_modal")
			if drawn != null and is_instance_valid(drawn):
				drawn.queue_free()
				get_viewport().set_input_as_handled()
				return
			var dim: Node = get_node_or_null("pane_modal_dim")
			if dim != null and is_instance_valid(dim):
				_close_pane_modal(dim as ColorRect)
				get_viewport().set_input_as_handled()
				return
			if _board_fullscreen:
				_toggle_board_fullscreen()
				get_viewport().set_input_as_handled()


# ── Audio ───────────────────────────────────────────────────────────
# Wire into the existing AudioMgr autoload. BGM defaults to the vol5
# ambient drone (the diner being the diner — matches the Fool scene).
# SFX paths are conventions; missing files fall through silently in
# AudioMgr.play_sfx (no exceptions, no spam).

const _BGM_BY_LOCATION := {
	# Wave-1
	"dambrosios":                 "res://assets/audio/bgm/vol5_ambient.ogg",
	"cathedral":                  "res://assets/audio/bgm/vol5_warehouse_drone.ogg",
	"riverboat":                  "res://assets/audio/bgm/vol5_riverboat_drone.ogg",
	"anya_bungalow":              "res://assets/audio/bgm/vol5_ambient.ogg",
	"roberts_house":              "res://assets/audio/bgm/vol5_ambient.ogg",
	"ember_ash_office":           "res://assets/audio/bgm/vol5_ambient.ogg",
	"lacombe_service_garage":     "res://assets/audio/bgm/vol5_warehouse_drone.ogg",
	"hierophant_circuit":         "res://assets/audio/bgm/vol5_cicadas_dusk.ogg",
	"roadside_chapel":            "res://assets/audio/bgm/vol5_cicadas_dusk.ogg",
	# Wave-2 · reuses the four available Vol5 tracks by tonal fit.
	# Later polish can source per-location tracks; these are honest
	# starting points that beat silence.
	"carnival_lot":               "res://assets/audio/bgm/vol5_cicadas_dusk.ogg",
	"asylum_ward_c":              "res://assets/audio/bgm/vol5_warehouse_drone.ogg",
	"wgur_transmitter_shack":     "res://assets/audio/bgm/vol5_warehouse_drone.ogg",
	"bayou_lighthouse":           "res://assets/audio/bgm/vol5_cicadas_dusk.ogg",
	"courthouse_chamber":         "res://assets/audio/bgm/vol5_warehouse_drone.ogg",
	"mixing_glass":               "res://assets/audio/bgm/vol5_ambient.ogg",
	"le_roulant_casino":          "res://assets/audio/bgm/vol5_ambient.ogg",
	"simon_apartment":            "res://assets/audio/bgm/vol5_ambient.ogg",
	"daigles_roadhouse":          "res://assets/audio/bgm/vol5_ambient.ogg",
	"christian_ice_co":           "res://assets/audio/bgm/vol5_warehouse_drone.ogg",
	"static_drive_in":            "res://assets/audio/bgm/vol5_cicadas_dusk.ogg",
	"solenade_garden":            "res://assets/audio/bgm/vol5_cicadas_dusk.ogg",
	"parish_cemetery":            "res://assets/audio/bgm/vol5_cicadas_dusk.ogg",
	"frog_knows_best":            "res://assets/audio/bgm/vol5_riverboat_drone.ogg",
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

# Preferred SFXBank preset for each _audio_sfx key. If the preset
# is present in SFXBank.PRESET_MAP the bank plays it (overlapping,
# pooled, respects Settings.sfx_vol). Otherwise falls back to the
# _SFX file-path table above via AudioMgr. This lets legacy calls
# like _audio_sfx("card_play") pick up the Wave D authored presets
# without touching every call site.
const _SFX_BANK_KEYS := {
	"card_play":       "card_place",
	"visitor_arrive":  "visitor_arrive",
	"visitor_claimed": "lore_token_reveal",
	"item_pickup":     "pickup",
	"gravity_draw":    "card_flip",
	"win":             "win_chord",
	"loss":            "loss_thud",
	"lore_token":      "lore_token_reveal",
}


func _audio_sfx(key: String) -> void:
	var bank := get_node_or_null("/root/SFXBank")
	if bank and _SFX_BANK_KEYS.has(key):
		var preset: String = String(_SFX_BANK_KEYS[key])
		if bank.has_preset(preset):
			bank.play(preset, 0.75)
			return
	var path: String = _SFX.get(key, "")
	if path == "":
		return
	AudioMgr.play_sfx(path)


# ── Animation + game-feel helpers ────────────────────────────────────
# Small reusable polish primitives so every state change gets visible
# audio + visual feedback. Cheap to call; safe if a target is null.

# Pulse a label's color toward `flash` and back. Used on stat changes
# (time / inertia / sanity) so the player SEES what a card did, not
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

# 1st-person view art for a single space, e.g.
# `assets/gallery/locations/dambrosios_fp_counter.png`. Used by
# `_render_fp` when the player is at that space in normal (non-
# fullscreen) mode. Fullscreen toggles to the top-down map.
func _art_path_fp(space_id: String) -> String:
	return "res://assets/gallery/locations/" + _location_id + "_fp_" + space_id + ".png"

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
	print("[Gauntlet] loading data from %s (scenario %s)" % [arc_root, _scenario_id])
	# Per-scenario setup file: setup_<scenario_id>.json
	_setup           = _load_json(arc_root + "setup_" + _scenario_id + ".json")
	# Per-scenario gravity deck if present, else the default deck.
	# Scenario-specific decks carry their own atmospheric cards
	# (lunch chaos, evening fullness) on top of the shared base.
	var scenario_deck_path: String = arc_root + "gravity_deck_" + _scenario_id + ".json"
	if ResourceLoader.exists(scenario_deck_path):
		_gravity_deck_def = _load_json(scenario_deck_path)
	else:
		_gravity_deck_def = _load_json(arc_root + "gravity_deck.json")
	_finale_def      = _load_json(arc_root + "finale.json")
	_die             = _load_json(arc_root + "die.json")
	# Merge core + arcana-unique action cards into a flat dict by id
	var core_deck := _load_json(FRAMEWORK_CORE)
	var arc_deck  := _load_json(arc_root + "action_cards.json")
	# Player cards are UNIVERSAL by default. They travel with the
	# HAND from location to location. Cards that need specific
	# spaces (CLEAN works anywhere; ADDRESS THE BBS needs the
	# "register") self-gate via their `requires` clause —
	# they're loaded everywhere but only playable where the named
	# space exists.
	#
	# Exception: a card may declare `available_in_locations: [...]`
	# to be loaded ONLY at those locations. Use sparingly — only
	# for cards that genuinely don't translate to other rooms
	# (e.g. a future Hierophant card whose verb is meaningless
	# outside a church). Most cards shouldn't need this.
	for c: Dictionary in core_deck.get("cards", []):
		_action_cards[c["id"]] = c
	for c: Dictionary in arc_deck.get("cards", []):
		var locs: Array = c.get("available_in_locations", [])
		if not locs.is_empty() and not (_location_id in locs):
			continue
		_action_cards[c["id"]] = c
	# Scenario-local action cards: a cameo (or any scenario) can
	# declare unique cards in its setup JSON under `scenario_action_cards`.
	# These ride the same shape as cards in action_cards.json. They are
	# merged AFTER the arcana deck so a scenario card can override a
	# universal card of the same id for this run only.
	for c: Dictionary in _setup.get("scenario_action_cards", []):
		_action_cards[c["id"]] = c
	# Seed the tableau stock counts. Non-starters, non-leap, non-
	# bundle cards get a stock count (from the card's `stock` field
	# or default 2 if unspecified). Each purchase decrements; at 0
	# the card vanishes from the tableau.
	for cid: String in _action_cards.keys():
		var c: Dictionary = _action_cards[cid]
		if c.get("starter", false): continue
		if cid == "leap" or cid == "bundle": continue
		_tableau_stock[cid] = int(c.get("stock", 2))
	# Visitors → id-keyed dict, plus the mood→step fallback table.
	var v_def := _load_json(arc_root + "visitors.json")
	for v: Dictionary in v_def.get("visitors", []):
		_visitors_def[v["id"]] = v
	_step_defaults_by_mood = v_def.get("default_step_lines_by_mood", {})
	# Scenario-local visitors: a cameo can introduce a visitor that
	# only exists when this specific scenario is being played (e.g. a
	# courier who only shows up on the night Antonio comes home).
	# Same schema as the entries in visitors.json.
	for v: Dictionary in _setup.get("scenario_visitors", []):
		_visitors_def[v["id"]] = v
	# Player-as-visitor swap. If the scenario would put the player's
	# arcana character on the board as a visitor (e.g. Frasier hand
	# vs. Frasier walking in for lunch), replace the visitor entry
	# with the matching `*_as_regular` stand-in so the player never
	# meets themselves at the counter.
	_apply_player_visitor_swap()
	# Items + piles
	var i_def := _load_json(arc_root + "items.json")
	_piles_def = i_def.get("piles", {})
	_items_def = i_def.get("items", {})
	# Threats (optional file)
	var t_def := _load_json(arc_root + "threats.json")
	_threats_def = t_def.get("threats", {})
	# Location + hand
	_location = _load_json(DATA_ROOT + "locations/" + _location_id + ".json")
	_hand     = _load_json(DATA_ROOT + "hands/"     + _hand_id     + ".json")
	# Hand fallback: if the host names a hand that has no JSON yet
	# (the new arcana hosts pass placeholders like "frank" / "natalie"
	# / "tbd_devil" that aren't authored yet), fall back to the
	# universal _placeholder.json so the engine has something to
	# read for stats / starting_hand / ultimate.
	if _hand.is_empty():
		_hand = _load_json(DATA_ROOT + "hands/_placeholder.json")
	# Scenario-local map additions: a cameo can unlock spaces/edges
	# that aren't on the host's baseline floor plan (a back stair the
	# guest knows, a courier's side path). Spaces in
	# `scenario_spaces_additions` are appended to _location.spaces;
	# pairs in `scenario_adjacency_additions` are appended to
	# _location.adjacency. Same schema as the entries in the location
	# file.
	var extra_spaces: Array = _setup.get("scenario_spaces_additions", [])
	if not extra_spaces.is_empty():
		var loc_spaces: Array = (_location.get("spaces", []) as Array).duplicate()
		for sp: Dictionary in extra_spaces:
			loc_spaces.append(sp)
		_location["spaces"] = loc_spaces
	var extra_adj: Array = _setup.get("scenario_adjacency_additions", [])
	if not extra_adj.is_empty():
		var loc_adj: Array = (_location.get("adjacency", []) as Array).duplicate()
		for pair: Array in extra_adj:
			loc_adj.append(pair)
		_location["adjacency"] = loc_adj
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

# Build a (vid → swap_target_vid) map for the current hand, then
# rewrite the scenario's visitor lists. A visitor with
# `as_hand_id == _hand_id` is the player walking into their own
# scene; we substitute the matching `swap_target_for_hand` entry.
func _apply_player_visitor_swap() -> void:
	if _setup.is_empty():
		return
	# Resolve the stand-in vid for the current hand, if any.
	var swap_target_vid: String = ""
	for vid in _visitors_def:
		var v: Dictionary = _visitors_def[vid]
		if String(v.get("swap_target_for_hand", "")) == _hand_id:
			swap_target_vid = vid
			break
	if swap_target_vid == "":
		return
	# Build the swap map: any vid whose `as_hand_id` matches my hand.
	var to_swap: Dictionary = {}
	for vid in _visitors_def:
		var v: Dictionary = _visitors_def[vid]
		if String(v.get("as_hand_id", "")) == _hand_id:
			to_swap[vid] = swap_target_vid
	if to_swap.is_empty():
		return
	# Rewrite visitors_present_at_start
	var start_arr: Array = _setup.get("visitors_present_at_start", []).duplicate()
	for i in start_arr.size():
		if to_swap.has(start_arr[i]):
			start_arr[i] = to_swap[start_arr[i]]
	_setup["visitors_present_at_start"] = start_arr
	# Rewrite visitor_schedule entries
	var sched: Array = _setup.get("visitor_schedule", []).duplicate()
	for entry: Dictionary in sched:
		if to_swap.has(entry.get("visitor", "")):
			entry["visitor"] = to_swap[entry["visitor"]]
	_setup["visitor_schedule"] = sched
	print("[Gauntlet] player-as-visitor swap applied: %s" % str(to_swap))


func _init_run() -> void:
	# Reseed the global RNG with a time-based value so the gravity
	# deck (and every other shuffle this run uses) is genuinely
	# random per session. Without this, Godot's default seed at
	# engine start would deterministically reproduce the same draw
	# order across runs from the same launch.
	randomize()
	# Apply the reversed-mode modifier on top of the scenario's
	# starting_state. _reversed_mode is set by start_scenario when
	# the player picked the REVERSED tile for this arcana.
	var start: Dictionary = (_setup.get("starting_state", {}) as Dictionary).duplicate()
	if _reversed_mode:
		start["doubt"]      = int(start.get("doubt", 0)) + 2
		start["stagnation"] = int(start.get("stagnation", 0)) + 2
		start["time"]       = max(2, int(start.get("time", 4)) - 1)
		start["sanity"]     = max(2, int(start.get("sanity", 5)) - 1)
		# Tighter loss-conditions
		var lc: Dictionary = (_setup.get("loss_conditions", {}) as Dictionary).duplicate()
		lc["visitors_claimed_max"] = max(1, int(lc.get("visitors_claimed_max", 3)) - 1)
		_setup["loss_conditions"] = lc
		# Tighter max_turns
		_setup["max_turns"] = max(4, int(_setup.get("max_turns", 8)) - 1)
		_log_line("[color=#c8333c][b]REVERSED.[/b] the room is harder to hold.[/color]")
	_player_pos = start.get("player_pos", "counter")
	_places_visited[_player_pos] = true
	_time       = int(start.get("time", 4))
	_next_time_reset = int(start.get("time_per_turn", _time))
	_inertia    = int(start.get("inertia", 0))
	_sanity     = int(start.get("sanity", start.get("health", 5)))
	_sanity_max = int(start.get("sanity_max", max(_sanity, 5)))
	# Magician-arcana stats (default zero / inert if not declared)
	_stagnation = int(start.get("stagnation", 0))
	_stagnation_per_turn = int(start.get("stagnation_per_turn", 0))
	_doubt = int(start.get("doubt", 0))
	_doubt_max = int(start.get("doubt_max", 7))
	_inspiration = int(start.get("inspiration", 0))
	_piece_threshold = int(start.get("piece_threshold", 3))
	# Seal the arcanas the scenario lists at start. BUILD at the
	# Magician station spends Inspiration to unseal one.
	_sealed_arcanas.clear()
	for sid in _setup.get("sealed_arcanas_at_start", []):
		_sealed_arcanas[String(sid)] = true
	# Per-run achievement trackers — reset on every fresh run.
	_cards_played_this_run.clear()
	_claimed_visitors_count = 0
	_last_finale_id = ""
	# Load cross-arcana world state — sinkhole open, first_septenary
	# completed, candles_lit, etc. Active states append ambient lines
	# to the pool and gravity-extras to the deck.
	_load_world_state()
	# Steamboat threshold + WIP thresholds come from the location def.
	var sb_def: Dictionary = _location.get("steamboat", {})
	_steamboat_threshold = int(sb_def.get("completion_threshold", 6))
	_steamboat_progress = 0
	# Priestess master reel — pulled from location.master_reel.
	# Default 6 if not declared. Starting progress lets a scenario
	# pre-load the reel (e.g. tape_witness starts at 3/6).
	var mr_def: Dictionary = _location.get("master_reel", {})
	_master_reel_threshold = int(mr_def.get("completion_threshold", 6))
	_master_reel = int(start.get("starting_master_reel", 0))
	_insight = int(start.get("insight", 0))
	# Pomegranate Hour episode states. Default per-space from the location
	# JSON (each episode-space carries `episode_state`). The scenario can
	# override with `starting_episode_states: { space_id: STATE_ID }`.
	_episode_states.clear()
	_episodes_advanced_this_run = 0
	_cast_crew_sit_with_count = 0
	for sdef in (_location.get("spaces", []) as Array):
		var sd: Dictionary = sdef as Dictionary
		var st: String = String(sd.get("episode_state", ""))
		if st != "":
			_episode_states[String(sd.get("id", ""))] = st
	var ep_override: Dictionary = start.get("starting_episode_states", {}) as Dictionary
	for k_eo in ep_override.keys():
		_episode_states[String(k_eo)] = String(ep_override[k_eo])
	_patience_frozen_turns = 0
	_patched_pairs.clear()
	# Empress bloom track — pulled from location.bloom_track. Bloom
	# rises GOOD (opposite of stagnation); harvest is the spendable
	# crop currency.
	var bt_def: Dictionary = _location.get("bloom_track", {})
	_bloom_threshold = int(bt_def.get("completion_threshold", 6))
	_bloom = int(start.get("bloom", 0))
	_harvest = int(start.get("harvest", 0))
	# Emperor ledger track — same shape as Bloom but for Dante's office.
	var lt_def: Dictionary = _location.get("ledger_track", {})
	_ledger_threshold = int(lt_def.get("completion_threshold", 6))
	_ledger = int(start.get("ledger", 0))
	_authority = int(start.get("authority", 0))
	# Hierophant signal track — same shape, for the BBS room.
	var sg_def: Dictionary = _location.get("signal_track", {})
	_signal_threshold = int(sg_def.get("completion_threshold", 6))
	_signal = int(start.get("signal", 0))
	_doctrine = int(start.get("doctrine", 0))
	# Lovers sync track — same shape, for the apartment-above-the-diner.
	var sy_def: Dictionary = _location.get("sync_track", {})
	_sync_threshold = int(sy_def.get("completion_threshold", 6))
	_sync = int(start.get("starting_sync", start.get("sync", 0)))
	_verb = int(start.get("verb", 0))
	# Chariot miles track — pulled from location.miles_track.
	var ml_def: Dictionary = _location.get("miles_track", {})
	_miles_threshold = int(ml_def.get("completion_threshold", 6))
	_miles = int(start.get("starting_miles", start.get("miles", 0)))
	_fuel = int(start.get("fuel", 0))
	# Resolve the partner visitor id once (scanned from _visitors_def
	# at run start — the visitor flagged is_lovers_partner: true).
	_lovers_partner_id = ""
	for vid_lp in _visitors_def:
		if bool((_visitors_def[vid_lp] as Dictionary).get("is_lovers_partner", false)):
			_lovers_partner_id = vid_lp
			break
	_piece_progress.clear()
	_wip_progress.clear()
	_pieces_completed = 0
	_next_gravity_canceled = false
	_active_demons.clear()
	# Atmosphere bookkeeping
	_last_logged_pos = ""
	_last_steamboat_beat = -1
	_last_stagnation_tier = -1
	_last_doubt_tier = -1
	_ambient_turn_offset = randi() % 3
	# Apply starting_demons_active if the setup declares any (BLOW
	# OUT THE CANDLES leans on this to start in chaos mode).
	for d_decl in _setup.get("starting_demons_active", []):
		var dd: Dictionary = d_decl
		var did: String = String(dd.get("id", ""))
		var dur: int = int(dd.get("duration_turns", 3))
		if did != "":
			_active_demons[did] = dur
	# Honor starting_steamboat_progress for the hard scenario.
	_steamboat_progress = int(_setup.get("starting_steamboat_progress", _steamboat_progress))
	_hand_cards = (start.get("starting_hand", []) as Array).duplicate()

	# Visitors: the scenario's `visitors_present_at_start` and
	# `visitor_schedule` lists are the source of truth — they let the
	# easy / medium / hard scenarios stagger different visitor counts
	# from a shared visitors.json. Each visitor's intrinsic
	# arrival.kind is treated as a default only; the scenario lists
	# take precedence. Conditional visitors (anya_recording) remain
	# opt-in via their own predicate regardless of scenario.
	var scenario_starters: Array = _setup.get("visitors_present_at_start", [])
	var scenario_schedule: Array = _setup.get("visitor_schedule", [])
	# Place starters
	for vid_v in scenario_starters:
		var vid: String = String(vid_v)
		var v: Dictionary = _visitors_def.get(vid, {})
		if v.is_empty():
			push_warning("Gauntlet: scenario lists unknown visitor in visitors_present_at_start: %s" % vid)
			continue
		var arr: Dictionary = v.get("arrival", {})
		# Resolve starting pos: prefer arrival.pos, fall back to
		# arrival.to (some visitor schemas use "to" rather than "pos"
		# for the starting position).
		var start_pos: String = String(arr.get("pos", arr.get("to", "counter")))
		_visitors_state[vid] = {
			"pos": start_pos,
			"arrived": true,
			"arrived_turn": 1,
			"connected": false,
			"claimed_turn": -1,
			"progress": 0,
		}
	# Queue scheduled visitors. arrival_turn + arrival_space are the
	# canonical scenario field names; fall back to turn + to (the
	# visitor-def shape) so older formats still work.
	for entry_v in scenario_schedule:
		var entry: Dictionary = entry_v
		var vid2: String = String(entry.get("visitor", ""))
		if vid2 == "" or _visitors_state.has(vid2):
			continue
		var v2: Dictionary = _visitors_def.get(vid2, {})
		if v2.is_empty():
			push_warning("Gauntlet: scenario lists unknown visitor in visitor_schedule: %s" % vid2)
			continue
		_visitors_state[vid2] = {
			"pos": "",
			"arrived": false,
			"scheduled_turn": int(entry.get("arrival_turn", entry.get("turn", 99))),
			"arrival_pos": String(entry.get("arrival_space", entry.get("to", "counter"))),
			"connected": false,
			"claimed_turn": -1,
			"progress": 0,
		}
	# Conditional visitors — their arrival is triggered by an in-game
	# event, not by scenario placement. Register them so the trigger
	# can flip them to arrived later, but don't surface them yet.
	for vid in _visitors_def:
		if _visitors_state.has(vid):
			continue
		var vd: Dictionary = _visitors_def[vid]
		var ard: Dictionary = vd.get("arrival", {})
		if ard.get("kind", "") == "conditional":
			_visitors_state[vid] = {
				"pos": "",
				"arrived": false,
				"connected": false,
				"claimed_turn": -1,
				"condition": ard,
				"progress": 0,
			}

	# Item piles: copy the items[] array so we can pop from it.
	# Contents pile (items_contents_pool + draw_one_keep_or_putback)
	# initialises with the full pool shuffled — every search draws
	# the front, player chooses KEEP or PUT BACK, putback shuffles.
	# Items that declare a `scenarios` array on their def are filtered
	# out when the current scenario isn't in the list (e.g. lunch-only
	# jukebox tracks don't appear at 3:47 AM).
	for pid in _piles_def:
		var p_def: Dictionary = _piles_def[pid]
		var raw_items: Array = []
		if p_def.has("items_contents_pool"):
			raw_items = (p_def["items_contents_pool"] as Array).duplicate()
		else:
			raw_items = (p_def.get("items", []) as Array).duplicate()
		var filtered: Array = []
		for iid in raw_items:
			var idef: Dictionary = _items_def.get(String(iid), {})
			var item_scenarios: Array = idef.get("scenarios", [])
			if not item_scenarios.is_empty() and not (_scenario_id in item_scenarios):
				continue
			filtered.append(iid)
		_pile_state[pid] = filtered
		if p_def.has("items_contents_pool"):
			_pile_state[pid].shuffle()

	# Shuffle Gravity deck — Final Girl style:
	# Endgame cards (flagged with endgame:true in the deck JSON)
	# get shuffled SEPARATELY and placed at the BOTTOM of the pile
	# (front of the Array, since pop_back draws). The rest of the
	# deck shuffles normally on top. Guarantees the heaviest
	# threats come late in the run.
	var normal_ids: Array = []
	var endgame_ids: Array = []
	for c: Dictionary in _gravity_deck_def.get("cards", []):
		if c.get("endgame", false):
			endgame_ids.append(c["id"])
		else:
			normal_ids.append(c["id"])
	normal_ids.shuffle()
	endgame_ids.shuffle()
	_gravity_draw_pile = []
	for cid: String in endgame_ids:
		_gravity_draw_pile.append(cid)
	for cid: String in normal_ids:
		_gravity_draw_pile.append(cid)
	print("[Gauntlet] gravity deck shuffled: %d normal + %d endgame (drawn last)" %
		[normal_ids.size(), endgame_ids.size()])


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
	_sanity_label   = _make_track_label("Sanity 5")
	_stagnation_label   = _make_track_label("Stagnation 0")
	_doubt_label        = _make_track_label("Doubt 0")
	_inspiration_label  = _make_track_label("Inspiration 0")
	_pieces_label       = _make_track_label("Pieces 0")
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
	for lbl in [_phase_label, _turn_label, _time_label, _inertia_label, _sanity_label, _stagnation_label, _doubt_label, _inspiration_label, _pieces_label, _player_pos_label, _bindle_label]:
		top_hb.add_child(lbl)
	# Hide the Magician-only labels by default. _render_stats decides
	# which to show based on the loaded scenario.
	_stagnation_label.visible = false
	_doubt_label.visible = false
	_inspiration_label.visible = false
	_pieces_label.visible = false
	# Push the Leave button to the far right of the top bar so it
	# isn't sitting next to MOVE / ADVANCE where it gets misclicked.
	var top_spacer := Control.new()
	top_spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top_hb.add_child(top_spacer)
	var top_leave_btn := Button.new()
	top_leave_btn.text = "← Back to Gallery"
	var leave_room: String = "diner"
	if _arcana_id == "magician":   leave_room = "cathedral"
	if _arcana_id == "priestess":  leave_room = "bungalow"
	if _arcana_id == "empress":    leave_room = "riverboat"
	if _arcana_id == "emperor":    leave_room = "helm"
	if _arcana_id == "hierophant": leave_room = "sunday circuit"
	if _arcana_id == "lovers":     leave_room = "Roberts' house"
	if _arcana_id == "chariot":    leave_room = "hot office"
	top_leave_btn.tooltip_text = "Leave the %s and return to the gallery (this ends the run)." % leave_room
	top_leave_btn.add_theme_font_size_override("font_size", 12)
	top_leave_btn.custom_minimum_size = Vector2(132, 24)
	top_leave_btn.pressed.connect(_on_leave)
	top_hb.add_child(top_leave_btn)

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
	_board_root.offset_bottom = -346
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
	# Lift the header above the content layer so its buttons always
	# win the click test even if content drifts up via clip overflow
	# or z_index changes in fullscreen mode.
	board_header.z_index = 5
	_board_root.add_child(board_header)
	var header_hb := HBoxContainer.new()
	header_hb.add_theme_constant_override("separation", 6)
	header_hb.mouse_filter = Control.MOUSE_FILTER_IGNORE
	board_header.add_child(header_hb)
	var board_title := Label.new()
	board_title.text = "  MAP — " + String(_location.get("title", _location_id))
	board_title.add_theme_color_override("font_color", C_ACCENT)
	board_title.add_theme_font_size_override("font_size", 12)
	board_title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header_hb.add_child(board_title)
	# Background-art toggle — flips the painted board image on/off
	# so the engine-drawn markers + lines + labels read cleanly when
	# the art is misaligned or competing for attention.
	_board_bg_btn = Button.new()
	_board_bg_btn.text = "BG OFF" if not _board_bg_visible else "BG ON"
	_board_bg_btn.tooltip_text = "Toggle the painted board background. Default OFF — turn on if you want the atmospheric texture behind the markers."
	_board_bg_btn.toggle_mode = true
	_board_bg_btn.button_pressed = _board_bg_visible
	_board_bg_btn.add_theme_font_size_override("font_size", 12)
	_board_bg_btn.custom_minimum_size = Vector2(54, 20)
	_board_bg_btn.toggled.connect(func(p: bool) -> void:
		_board_bg_visible = p
		_board_bg_btn.text = "BG ON" if p else "BG OFF"
		# Belt and suspenders: even if the next render misses it,
		# free any lingering bg TextureRect right now.
		if not p:
			for c in _board_content.get_children():
				if c.name == "board_bg":
					c.queue_free()
		_log_line("[color=#7c8398][i]map background %s[/i][/color]" % ("on" if p else "off"))
		_render_board())
	header_hb.add_child(_board_bg_btn)
	# Fullscreen toggle — bulletproofed: z_index so nothing sneaks
	# above it; explicit STOP mouse filter; focus mode that lets
	# Esc / Enter activate it too.
	_board_expand_btn = Button.new()
	_board_expand_btn.text = "⛶"
	_board_expand_btn.tooltip_text = "Open the top-down MAP (fullscreen). 1st-person of the current space is the default normal view."
	_board_expand_btn.add_theme_font_size_override("font_size", 12)
	_board_expand_btn.custom_minimum_size = Vector2(28, 20)
	_board_expand_btn.mouse_filter = Control.MOUSE_FILTER_STOP
	_board_expand_btn.focus_mode = Control.FOCUS_ALL
	_board_expand_btn.z_index = 5
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

	# Bulletproof fullscreen-exit overlay — lives at the top of the
	# whole viewport (not inside _board_root), z=200 so nothing can
	# eat its click. Only visible when fullscreen is on. The in-
	# header ⛶ button still works too; this is a fallback for when
	# layout shifts make that one unreachable.
	_board_fullscreen_exit_btn = Button.new()
	_board_fullscreen_exit_btn.text = "✕  Exit Fullscreen Map  (Esc)"
	_board_fullscreen_exit_btn.add_theme_font_size_override("font_size", 14)
	_board_fullscreen_exit_btn.custom_minimum_size = Vector2(220, 32)
	_board_fullscreen_exit_btn.mouse_filter = Control.MOUSE_FILTER_STOP
	_board_fullscreen_exit_btn.focus_mode = Control.FOCUS_ALL
	_board_fullscreen_exit_btn.z_index = 200
	_board_fullscreen_exit_btn.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	_board_fullscreen_exit_btn.offset_left = -240
	_board_fullscreen_exit_btn.offset_right = -10
	_board_fullscreen_exit_btn.offset_top = 10
	_board_fullscreen_exit_btn.offset_bottom = 42
	_board_fullscreen_exit_btn.visible = false
	_board_fullscreen_exit_btn.pressed.connect(_toggle_board_fullscreen)
	add_child(_board_fullscreen_exit_btn)

	# ── Right column: codex card + gravity card + visitor states + log
	var right := VBoxContainer.new()
	right.set_anchors_preset(Control.PRESET_RIGHT_WIDE)
	right.offset_top = 52
	right.offset_right = -8
	right.offset_left = -432
	right.offset_bottom = -346
	right.add_theme_constant_override("separation", 6)
	add_child(right)

	# Codex card (the gallery image, pinned) — fixed size, NOT expand_fill
	# Right column (top → bottom):
	#   1. VISITORS  — dominant pane, expand_fill, the game IS them
	#   2. GRAVITY   — slim summary bar, click ⛶ for full deck
	#   3. INVENTORY — slim summary bar, click ⛶ for full inventory
	# Slim bars keep the column legible; full detail lives in modals.

	# VISITORS — dominant
	var v_panel := PanelContainer.new()
	v_panel.add_theme_stylebox_override("panel", _make_panel_style())
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

	# GRAVITY — slim summary bar
	var grav_panel := PanelContainer.new()
	grav_panel.add_theme_stylebox_override("panel", _make_panel_style())
	grav_panel.custom_minimum_size = Vector2(420, 56)
	var grav_vb := VBoxContainer.new()
	grav_vb.add_theme_constant_override("separation", 2)
	grav_panel.add_child(grav_vb)
	grav_vb.add_child(_make_pane_header("GRAVITY", "gravity"))
	_gravity_card_label = RichTextLabel.new()
	_gravity_card_label.bbcode_enabled = true
	_gravity_card_label.fit_content = true
	_gravity_card_label.add_theme_color_override("default_color", C_TEXT)
	_gravity_card_label.add_theme_font_size_override("normal_font_size", 12)
	_gravity_card_label.text = "[color=#7c8398]Deck — 12 remaining · click ⛶ for details[/color]"
	grav_vb.add_child(_gravity_card_label)
	right.add_child(grav_panel)

	# INVENTORY / BINDLE — slim summary bar (full list in the ⛶ modal)
	var inv_panel := PanelContainer.new()
	inv_panel.add_theme_stylebox_override("panel", _make_panel_style())
	inv_panel.custom_minimum_size = Vector2(420, 56)
	var inv_vb := VBoxContainer.new()
	inv_vb.add_theme_constant_override("separation", 2)
	inv_panel.add_child(inv_vb)
	inv_vb.add_child(_make_pane_header("INVENTORY / BINDLE", "inventory"))
	_inv_summary_label = RichTextLabel.new()
	_inv_summary_label.bbcode_enabled = true
	_inv_summary_label.fit_content = true
	_inv_summary_label.add_theme_color_override("default_color", C_TEXT)
	_inv_summary_label.add_theme_font_size_override("normal_font_size", 12)
	_inv_summary_label.text = "[color=#7c8398](nothing yet — search a pile)[/color]"
	inv_vb.add_child(_inv_summary_label)
	right.add_child(inv_panel)

	# Log moved OUT of the right column — it now lives in the bottom
	# strip alongside the hand. See bottom panel below.

	# ── Bottom strip: LOG (left, wide) + cards stack (right) ──────
	# Layout request: log on top of the bottom area, hand runs flush
	# into it on the right. So the bottom is one HBox — log fills
	# most of the width, the card stack (tableau row above hand row)
	# sits flush against its right edge.
	var bottom := PanelContainer.new()
	bottom.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	bottom.offset_top = -342
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
	tableau_label.add_theme_font_size_override("font_size", 12)
	tableau_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	tableau_title_hb.add_child(tableau_label)
	_tableau_scroll = ScrollContainer.new()
	_tableau_scroll.custom_minimum_size = Vector2(540, 144)
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
	hand_label.add_theme_font_size_override("font_size", 12)
	hand_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hand_title_hb.add_child(hand_label)
	var move_btn := Button.new()
	move_btn.text = "Move ↪"
	move_btn.add_theme_font_size_override("font_size", 12)
	move_btn.tooltip_text = "Pick an adjacent space to walk to (costs 1 Time, action phase only)."
	move_btn.pressed.connect(_show_move_popup)
	hand_title_hb.add_child(move_btn)
	_advance_btn = Button.new()
	_advance_btn.text = "Advance →"
	_advance_btn.add_theme_font_size_override("font_size", 12)
	_advance_btn.pressed.connect(_on_advance)
	hand_title_hb.add_child(_advance_btn)
	# (Leave moved to the top bar so it isn't adjacent to ADVANCE.)
	var hand_scroll := ScrollContainer.new()
	hand_scroll.custom_minimum_size = Vector2(540, 144)
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
	lbl.add_theme_font_size_override("font_size", 12)
	lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hb.add_child(lbl)
	# Remember the title label so unread badges (e.g. log "(3 new)")
	# can be set later.
	_pane_title_labels[modal_key] = lbl
	var btn := Button.new()
	btn.text = "⛶"
	btn.tooltip_text = "Expand " + title + " (Esc to close)"
	btn.add_theme_font_size_override("font_size", 12)
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
	dim.top_level = true
	dim.position = Vector2.ZERO
	dim.size = get_viewport_rect().size
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
# Generic "card drawn / item taken" popup. Centered, with art on
# the left and title + flavor + body on the right. Click outside,
# Esc, or the Acknowledge button to dismiss. Stacks above the
# pane modal layer (z=110) so it doesn't trample any chooser.

# Visitor arrival popup. Pulls the next vid from
# `_visitor_arrival_queue` and shows a portrait + flavor modal so
# the arrival is visible regardless of what panel the player was
# looking at. Stacks above the gauntlet UI (z=110), dismissible via
# Esc, click-outside, the Acknowledge button, or the Minimize "—"
# button. Minimize closes without chaining; the player can re-click
# the visitor row to view their card. Acknowledge advances to the
# next queued arrival (if any).
func _show_next_visitor_arrival() -> void:
	if _visitor_arrival_queue.is_empty():
		return
	var vid: String = String(_visitor_arrival_queue.pop_front())
	var v: Dictionary = _visitors_def.get(vid, {})
	var st: Dictionary = _visitors_state.get(vid, {})
	var name_s: String = String(v.get("name", vid))
	var pos_s: String = String(st.get("pos", "")).replace("_", " ")
	var hints: Array = v.get("pre_arrival_hints", [])
	var flavor: String = String(hints[hints.size() - 1]) if not hints.is_empty() else "%s walks in." % name_s
	var accent_hex: String = String(v.get("accent", "#c8a268"))
	_log_line("[color=#7c8398][i]» popping arrival modal for %s[/i][/color]" % name_s)
	# Tear down any prior drawn-card popup so this one stacks cleanly.
	var existing: Node = get_node_or_null("drawn_card_modal")
	if existing != null and is_instance_valid(existing):
		existing.queue_free()
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.78)
	# Force the dim to fill the viewport explicitly. Anchors relative
	# to the parent Control had been short-circuiting in some launch
	# paths, leaving the dim sized 0,0 and the modal visible without
	# its darkening backdrop. Top-level + explicit size = bulletproof.
	dim.top_level = true
	dim.position = Vector2.ZERO
	dim.size = get_viewport_rect().size
	dim.mouse_filter = Control.MOUSE_FILTER_STOP
	dim.z_index = 110
	dim.name = "drawn_card_modal"
	dim.modulate = Color(1, 1, 1, 0)
	add_child(dim)
	var fade := create_tween()
	fade.tween_property(dim, "modulate:a", 1.0, 0.14).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	var view: Vector2 = get_viewport_rect().size
	var pop := PanelContainer.new()
	pop.add_theme_stylebox_override("panel", _make_panel_style())
	pop.size = Vector2(min(view.x * 0.66, 820.0), min(view.y * 0.74, 560.0))
	pop.position = (view - pop.size) * 0.5
	pop.mouse_filter = Control.MOUSE_FILTER_STOP
	dim.add_child(pop)
	var root := HBoxContainer.new()
	root.add_theme_constant_override("separation", 16)
	pop.add_child(root)
	# Portrait
	var art_panel := PanelContainer.new()
	art_panel.add_theme_stylebox_override("panel", _make_panel_style())
	art_panel.custom_minimum_size = Vector2(320, 448)
	root.add_child(art_panel)
	var face_tex: Texture2D = _load_texture_silent(_art_path_visitor_face(vid))
	if face_tex:
		var img := TextureRect.new()
		img.texture = face_tex
		img.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		img.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		img.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		img.size_flags_vertical = Control.SIZE_EXPAND_FILL
		art_panel.add_child(img)
	else:
		var ph := Label.new()
		ph.text = "(no portrait art yet)"
		ph.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		ph.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		ph.add_theme_color_override("font_color", Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.40))
		ph.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		ph.size_flags_vertical = Control.SIZE_EXPAND_FILL
		art_panel.add_child(ph)
	# Info column
	var info := VBoxContainer.new()
	info.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	info.size_flags_vertical = Control.SIZE_EXPAND_FILL
	info.add_theme_constant_override("separation", 10)
	root.add_child(info)
	var header_row := HBoxContainer.new()
	info.add_child(header_row)
	var arrived_lbl := Label.new()
	arrived_lbl.text = "✦  arrived"
	arrived_lbl.add_theme_color_override("font_color", Color(0.49, 1.0, 0.69))
	arrived_lbl.add_theme_font_size_override("font_size", 12)
	header_row.add_child(arrived_lbl)
	var min_btn := Button.new()
	min_btn.text = "—"
	min_btn.tooltip_text = "Minimize (the visitor stays on the board; reopen by clicking their row)"
	min_btn.add_theme_font_size_override("font_size", 14)
	min_btn.custom_minimum_size = Vector2(28, 22)
	min_btn.size_flags_horizontal = Control.SIZE_SHRINK_END
	header_row.add_child(min_btn)
	var title_lbl := Label.new()
	title_lbl.text = name_s
	title_lbl.add_theme_color_override("font_color", Color(accent_hex))
	title_lbl.add_theme_font_size_override("font_size", 24)
	title_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	info.add_child(title_lbl)
	var pos_lbl := Label.new()
	pos_lbl.text = "at " + pos_s.to_upper()
	pos_lbl.add_theme_color_override("font_color", Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.6))
	pos_lbl.add_theme_font_size_override("font_size", 12)
	info.add_child(pos_lbl)
	if flavor != "":
		var flavor_rt := RichTextLabel.new()
		flavor_rt.bbcode_enabled = true
		flavor_rt.fit_content = true
		flavor_rt.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		flavor_rt.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		flavor_rt.add_theme_color_override("default_color", Color(0.86, 0.82, 0.74))
		flavor_rt.add_theme_font_size_override("normal_font_size", 13)
		flavor_rt.text = "[i]" + flavor + "[/i]"
		info.add_child(flavor_rt)
	if v.has("mood"):
		var mood_lbl := Label.new()
		mood_lbl.text = "mood: " + String(v.get("mood", ""))
		mood_lbl.add_theme_color_override("font_color", Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.55))
		mood_lbl.add_theme_font_size_override("font_size", 12)
		info.add_child(mood_lbl)
	if v.has("order_item"):
		var hint_rt := RichTextLabel.new()
		hint_rt.bbcode_enabled = true
		hint_rt.fit_content = true
		hint_rt.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		hint_rt.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		hint_rt.add_theme_color_override("default_color", C_TEXT)
		hint_rt.add_theme_font_size_override("normal_font_size", 12)
		hint_rt.text = "[color=#7c8398][i]they'll have something for you when you LISTEN.[/i][/color]"
		info.add_child(hint_rt)
	var spacer := Control.new()
	spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	info.add_child(spacer)
	var ack := Button.new()
	if _visitor_arrival_queue.is_empty():
		ack.text = "Acknowledge  (Esc / click outside)"
	else:
		ack.text = "Next →  (%d more arriving)" % _visitor_arrival_queue.size()
	ack.add_theme_font_size_override("font_size", 12)
	info.add_child(ack)
	# Acknowledge → fade out, then chain to next arrival
	var close_and_chain := func() -> void:
		var t := create_tween()
		t.tween_property(dim, "modulate:a", 0.0, 0.14).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
		t.tween_callback(dim.queue_free)
		t.tween_callback(_show_next_visitor_arrival)
	ack.pressed.connect(close_and_chain)
	# Click on dim (outside the panel) also acknowledges and chains.
	dim.gui_input.connect(func(ev: InputEvent) -> void:
		if ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed:
			close_and_chain.call())
	# Minimize → close WITHOUT chaining; player can re-open via visitor row.
	# Also requeues nothing — the popped vid is just gone; remaining
	# queued arrivals carry on after the next user action that calls
	# _show_next_visitor_arrival (currently only at arrival time).
	min_btn.pressed.connect(func() -> void:
		var t := create_tween()
		t.tween_property(dim, "modulate:a", 0.0, 0.14).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
		t.tween_callback(dim.queue_free))



func _show_drawn_card_popup(art_path: String, title: String, flavor: String, body: String, accent_hex: String) -> void:
	# Tear down any prior drawn-card popup (rapid-fire draws stack
	# cleanly).
	var existing: Node = get_node_or_null("drawn_card_modal")
	if existing != null and is_instance_valid(existing):
		existing.queue_free()
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.75)
	# Top-level + explicit viewport size — anchors-against-parent
	# was sometimes leaving the dim sized 0,0 and the popup floating
	# without its dark backdrop.
	dim.top_level = true
	dim.position = Vector2.ZERO
	dim.size = get_viewport_rect().size
	dim.mouse_filter = Control.MOUSE_FILTER_STOP
	dim.z_index = 110
	dim.name = "drawn_card_modal"
	dim.modulate = Color(1, 1, 1, 0)
	add_child(dim)
	var fade := create_tween()
	fade.tween_property(dim, "modulate:a", 1.0, 0.14).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	var view: Vector2 = get_viewport_rect().size
	var pop := PanelContainer.new()
	pop.add_theme_stylebox_override("panel", _make_panel_style())
	pop.size = Vector2(min(view.x * 0.66, 820.0), min(view.y * 0.74, 560.0))
	pop.position = (view - pop.size) * 0.5
	pop.mouse_filter = Control.MOUSE_FILTER_STOP
	dim.add_child(pop)
	var root := HBoxContainer.new()
	root.add_theme_constant_override("separation", 16)
	pop.add_child(root)
	# Card art
	var art_panel := PanelContainer.new()
	art_panel.add_theme_stylebox_override("panel", _make_panel_style())
	art_panel.custom_minimum_size = Vector2(320, 448)
	root.add_child(art_panel)
	var tex: Texture2D = _load_texture_silent(art_path)
	if tex:
		var img := TextureRect.new()
		img.texture = tex
		img.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		img.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		img.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		img.size_flags_vertical = Control.SIZE_EXPAND_FILL
		art_panel.add_child(img)
	else:
		var ph := Label.new()
		ph.text = "(no art yet)"
		ph.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		ph.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		ph.add_theme_color_override("font_color", Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.40))
		ph.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		ph.size_flags_vertical = Control.SIZE_EXPAND_FILL
		art_panel.add_child(ph)
	# Info column
	var info := VBoxContainer.new()
	info.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	info.size_flags_vertical = Control.SIZE_EXPAND_FILL
	info.add_theme_constant_override("separation", 10)
	root.add_child(info)
	var title_lbl := Label.new()
	title_lbl.text = title
	title_lbl.add_theme_color_override("font_color", Color(accent_hex))
	title_lbl.add_theme_font_size_override("font_size", 22)
	title_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	info.add_child(title_lbl)
	if flavor != "":
		var flavor_rt := RichTextLabel.new()
		flavor_rt.bbcode_enabled = true
		flavor_rt.fit_content = true
		flavor_rt.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		flavor_rt.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		flavor_rt.add_theme_color_override("default_color", Color(0.86, 0.82, 0.74))
		flavor_rt.add_theme_font_size_override("normal_font_size", 13)
		flavor_rt.text = "[i]" + flavor + "[/i]"
		info.add_child(flavor_rt)
	if body != "":
		info.add_child(HSeparator.new())
		var body_rt := RichTextLabel.new()
		body_rt.bbcode_enabled = true
		body_rt.fit_content = true
		body_rt.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		body_rt.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		body_rt.add_theme_color_override("default_color", C_TEXT)
		body_rt.add_theme_font_size_override("normal_font_size", 12)
		body_rt.text = body
		info.add_child(body_rt)
	var spacer := Control.new()
	spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	info.add_child(spacer)
	var ack := Button.new()
	ack.text = "Acknowledge  (Esc / click outside)"
	ack.add_theme_font_size_override("font_size", 12)
	ack.pressed.connect(func() -> void:
		var t := create_tween()
		t.tween_property(dim, "modulate:a", 0.0, 0.14).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
		t.tween_callback(dim.queue_free))
	info.add_child(ack)
	dim.gui_input.connect(func(ev: InputEvent) -> void:
		if ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed:
			ack.emit_signal("pressed"))


func _open_visitor_view(vid: String) -> void:
	# Click-a-portrait card view for a single visitor — big art on
	# the left, name + bio + status + per-step beats on the right.
	var v: Dictionary = _visitors_def.get(vid, {})
	if v.is_empty():
		return
	var st: Dictionary = _visitors_state.get(vid, {})
	# Tear down any existing modal
	var existing: Node = get_node_or_null("pane_modal_dim")
	if existing != null and is_instance_valid(existing):
		existing.queue_free()
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.82)
	# Top-level + explicit viewport size so the dim is guaranteed to
	# cover the gauntlet UI regardless of parent rect.
	dim.top_level = true
	dim.position = Vector2.ZERO
	dim.size = get_viewport_rect().size
	dim.mouse_filter = Control.MOUSE_FILTER_STOP
	dim.z_index = 100
	dim.name = "pane_modal_dim"
	dim.modulate = Color(1, 1, 1, 0)
	dim.gui_input.connect(_on_modal_dim_input.bind(dim))
	add_child(dim)
	var t_fade := create_tween()
	t_fade.tween_property(dim, "modulate:a", 1.0, 0.14).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
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
	# Left: big face portrait
	var art_panel := PanelContainer.new()
	art_panel.add_theme_stylebox_override("panel", _make_panel_style())
	art_panel.custom_minimum_size = Vector2(360, 480)
	root.add_child(art_panel)
	var arrived: bool = st.get("arrived", false)
	var face_tex: Texture2D = _load_texture_silent(_art_path_visitor_face(vid)) if arrived else null
	if face_tex:
		var img := TextureRect.new()
		img.texture = face_tex
		img.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		img.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		img.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		img.size_flags_vertical = Control.SIZE_EXPAND_FILL
		art_panel.add_child(img)
	else:
		var ph := Label.new()
		if not arrived:
			ph.text = "(not yet arrived)"
		else:
			ph.text = "(no portrait art yet)"
		ph.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		ph.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		ph.add_theme_color_override("font_color", Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.4))
		ph.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		ph.size_flags_vertical = Control.SIZE_EXPAND_FILL
		art_panel.add_child(ph)
	# Right: bio + status + per-step beats
	var info := VBoxContainer.new()
	info.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	info.size_flags_vertical = Control.SIZE_EXPAND_FILL
	info.add_theme_constant_override("separation", 10)
	root.add_child(info)
	# Name + mood
	var name_lbl := Label.new()
	name_lbl.text = String(v.get("name", vid)) if arrived else String(v.get("placeholder_name", "someone"))
	name_lbl.add_theme_color_override("font_color", Color(v.get("accent", "#c8a268")))
	name_lbl.add_theme_font_size_override("font_size", 26)
	info.add_child(name_lbl)
	if v.has("mood") and arrived:
		var mood_lbl := Label.new()
		mood_lbl.text = "mood: " + String(v.get("mood", ""))
		mood_lbl.add_theme_color_override("font_color", Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.55))
		mood_lbl.add_theme_font_size_override("font_size", 12)
		info.add_child(mood_lbl)
	# Status line
	var status_rt := RichTextLabel.new()
	status_rt.bbcode_enabled = true
	status_rt.fit_content = true
	status_rt.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	status_rt.add_theme_color_override("default_color", C_TEXT)
	status_rt.add_theme_font_size_override("normal_font_size", 12)
	if st.get("connected", false):
		status_rt.text = "[color=#7cffb0]✓ connected[/color]"
	elif st.get("claimed_turn", -1) >= 0:
		var remaining: int = int(_setup.get("claim_turns_to_consume", 2)) - (_turn - int(st["claimed_turn"]))
		status_rt.text = "[color=#ff8060]✕ claimed — %d turn(s) until consumed[/color]" % max(0, remaining)
	elif arrived:
		var p_now: int = int(st.get("progress", 0))
		var labels: PackedStringArray = ["GREET", "LISTEN", "DELIVER", "SIT WITH"]
		var marks: PackedStringArray = []
		for i in labels.size():
			var prefix: String = "[color=#7cffb0]✓[/color] " if p_now > i else ("[color=#ffd07a]→[/color] " if p_now == i else "[color=#7c8398]·[/color] ")
			marks.append(prefix + labels[i])
		status_rt.text = "at [b]%s[/b]\n[color=#7c8398]Sequence:[/color] %s" % [String(st.get("pos", "?")).replace("_", " "), "  ".join(marks)]
	elif st.has("scheduled_turn"):
		var diff: int = int(st["scheduled_turn"]) - _turn
		status_rt.text = "[color=#7c8398]arrives in ~%d turns[/color]" % max(0, diff)
	info.add_child(status_rt)
	# Lore text (the visitor's defining truth) — shown if connected,
	# else the pre-arrival hint or a "?" line.
	var lore_rt := RichTextLabel.new()
	lore_rt.bbcode_enabled = true
	lore_rt.fit_content = true
	lore_rt.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	lore_rt.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	lore_rt.add_theme_color_override("default_color", Color(0.86, 0.82, 0.74))
	lore_rt.add_theme_font_size_override("normal_font_size", 13)
	if st.get("connected", false) and v.has("lore_text"):
		lore_rt.text = "[i]" + String(v["lore_text"]) + "[/i]"
	elif not arrived and v.has("pre_arrival_hints"):
		var hints: Array = v.get("pre_arrival_hints", [])
		if not hints.is_empty():
			var diff: int = int(st.get("scheduled_turn", 99)) - _turn
			var idx: int = clamp(hints.size() - 1 - max(0, diff), 0, hints.size() - 1)
			lore_rt.text = "[i]" + String(hints[idx]) + "[/i]"
	else:
		lore_rt.text = ""
	if lore_rt.text != "":
		info.add_child(lore_rt)
	info.add_child(HSeparator.new())
	# Per-step beats
	var beats_header := Label.new()
	beats_header.text = "  THE SEQUENCE"
	beats_header.add_theme_color_override("font_color", C_ACCENT)
	beats_header.add_theme_font_size_override("font_size", 12)
	info.add_child(beats_header)
	var steps_dict: Dictionary = v.get("steps", {})
	var verb_labels: Dictionary = v.get("verb_labels", {}) as Dictionary
	var cur_progress: int = int(st.get("progress", 0))
	for step_name in ["greet", "listen", "deliver", "sit_with"]:
		# Pomegranate Hour subjects override the step label
		# (greet → see, listen → voice, deliver → cut, sit_with → lock).
		# The internal step_name stays the same so engine accounting is
		# unaffected; only the displayed label changes.
		var display_label: String = String(verb_labels.get(step_name, step_name))
		# verb_labels may also be keyed by the new verb (e.g. lookup the
		# step's flavor under "lock" instead of "sit_with"). Try that as
		# a fallback when steps_dict doesn't have the standard key.
		var step_line: String = String(steps_dict.get(step_name, ""))
		if step_line == "" and display_label != step_name:
			step_line = String(steps_dict.get(display_label, ""))
		if step_line == "":
			var defaults: Dictionary = _step_defaults_by_mood.get(String(v.get("mood", "preoccupied")), {})
			step_line = String(defaults.get(step_name, ""))
		var step_idx: int = _step_index(step_name)
		var step_done: bool = cur_progress >= step_idx
		var bullet: String = "[color=#7cffb0]✓[/color]" if step_done else "[color=#7c8398]·[/color]"
		var step_rt := RichTextLabel.new()
		step_rt.bbcode_enabled = true
		step_rt.fit_content = true
		step_rt.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		step_rt.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		step_rt.add_theme_color_override("default_color", C_TEXT)
		step_rt.add_theme_font_size_override("normal_font_size", 12)
		# Reveal only what's happened. Completed steps show flavor.
		# Next-up step shows only its label (vague). Steps beyond that
		# are even vaguer — no name, just a placeholder.
		if step_done:
			step_rt.text = "  %s [b]%s[/b]  [color=#7c8398][i]%s[/i][/color]" % [bullet, display_label.to_upper(), step_line]
		elif step_idx == cur_progress + 1:
			step_rt.text = "  %s [color=#c8a268]%s[/color]" % [bullet, display_label.to_upper()]
		else:
			step_rt.text = "  %s [color=#5e5650]· · ·[/color]" % bullet
		info.add_child(step_rt)
	# Order they want — kept hidden until they've actually ordered
	# (LISTEN done, progress >= 2). Until then it reads as "?".
	if arrived and v.has("order_item"):
		info.add_child(HSeparator.new())
		var order_rt := RichTextLabel.new()
		order_rt.bbcode_enabled = true
		order_rt.fit_content = true
		order_rt.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		order_rt.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		order_rt.add_theme_color_override("default_color", C_TEXT)
		order_rt.add_theme_font_size_override("normal_font_size", 12)
		if cur_progress < 2:
			order_rt.text = "[b]ORDER:[/b]  [color=#7c8398][i]they haven't said yet.[/i][/color]"
		else:
			var ord_id: String = String(v["order_item"])
			var ord_item: Dictionary = _items_def.get(ord_id, {})
			if not ord_item.is_empty():
				order_rt.text = "[b]ORDER:[/b]  %s\n[color=#7c8398][i]%s[/i][/color]" % [ord_item.get("title", ord_id), ord_item.get("flavor", "")]
		info.add_child(order_rt)
	# Spacer + close button
	var spacer := Control.new()
	spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	info.add_child(spacer)
	var close := Button.new()
	close.text = "✕  Close  (Esc)"
	close.add_theme_font_size_override("font_size", 13)
	close.custom_minimum_size = Vector2(140, 32)
	close.pressed.connect(_close_pane_modal.bind(dim))
	info.add_child(close)


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
	dim.top_level = true
	dim.position = Vector2.ZERO
	dim.size = get_viewport_rect().size
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
	if art_tex == null:
		art_tex = CARD_FACE.face(cid, _action_cards.get(cid, {}), _arcana_id)
	if art_tex:
		var img := TextureRect.new()
		img.texture = art_tex
		img.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		img.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		img.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		img.size_flags_vertical = Control.SIZE_EXPAND_FILL
		# Procedural faces are chunky pixels — keep them crisp when
		# the view scales them up.
		img.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
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
	l.mouse_filter = Control.MOUSE_FILTER_STOP
	return l


# Inertia mood — based on the setup JSON's inertia_thresholds, which
# is the canonical "what does this level feel like" ladder. Falls
# back to a generic line if no thresholds defined.
func _inertia_mood(level: int) -> String:
	var thresholds: Array = _setup.get("inertia_thresholds", [])
	if thresholds.is_empty():
		return "Inertia %d / 12 — the room's hold on you. 12 = the loop closes." % level
	var matched: Dictionary = {}
	for t: Dictionary in thresholds:
		if int(t.get("level", 0)) <= level:
			matched = t
	var label: String = String(matched.get("label", "")) if not matched.is_empty() else ""
	# Rich tooltip — current label + a sense of the next step
	var out: PackedStringArray = []
	out.append("Inertia %d / 12" % level)
	if label != "":
		out.append("\"" + label + "\"")
	# What's coming
	var next_t: Dictionary = {}
	for t: Dictionary in thresholds:
		if int(t.get("level", 0)) > level:
			next_t = t
			break
	if not next_t.is_empty():
		var diff: int = int(next_t.get("level", 12)) - level
		out.append("In %d more tick%s: %s" % [diff, "" if diff == 1 else "s", String(next_t.get("label", ""))])
	out.append("")
	out.append("Inertia is the room's hold on you. At 12 the loop closes — the 24-hour diner of the soul.")
	return "\n".join(out)


# Sanity mood — invented tier descriptions since the setup JSON
# doesn't enumerate them. Max 5.
func _sanity_mood(h: int) -> String:
	var line: String = ""
	if h >= 5:
		line = "Steady. Cloth in hand, feet on the floor."
	elif h == 4:
		line = "A little thin. The fluorescent above the booth flickers when you do."
	elif h == 3:
		line = "Tired enough you almost don't notice the time."
	elif h == 2:
		line = "Wrong already, like a missed step on a familiar stair."
	elif h == 1:
		line = "A breath from the loop closing. Find somewhere to settle."
	else:
		line = "Gone. Faith hasn't moved."
	return "Sanity %d / %d\n\"%s\"\n\nA Short Rest steadies you. The room — fluorescents, looping clocks, voices you almost recognize — wears it down." % [h, _sanity_max, line]


# ── Board rendering ──────────────────────────────────────────────────

func _render_board() -> void:
	# Top of the rendering pipeline. Routes to FP or top-down map
	# depending on _view_mode + fullscreen state. Fullscreen always
	# goes to the top-down map; normal mode prefers FP if art exists,
	# otherwise falls back to the top-down map.
	if _board_content == null:
		return
	# Atmosphere hooks — fire once per actual movement / stat shift.
	_log_arrival_beat_if_changed()
	_log_pressure_tier_crossings()
	if _board_fullscreen or _view_mode == "map":
		_render_topdown_map()
		return
	# FP mode — four-tier fallback:
	#   1. HOST 3D — if the GauntletHost is in the tree (gauntlet
	#      launched from inside its walkable locale), render LIVE
	#      from the host's World3D via a shared-world SubViewport.
	#   2. STANDALONE 3D — gauntlet launched from Gallery / menu
	#      (no host loaded). Load the location's locale .tscn into
	#      the SubViewport's OWN World3D and position a camera per
	#      the embedded SPACE_VANTAGES table below. Same visual
	#      result as the host path — just costs a one-time locale
	#      load on gauntlet start.
	#   3. Painted PNG fallback.
	#   4. Top-down map.
	var host: Node = _find_gauntlet_host()
	if host != null and host.has_method("get_fp_camera_for_space"):
		var cam_spec: Dictionary = host.get_fp_camera_for_space(_player_pos)
		if not cam_spec.is_empty():
			_render_fp_3d(cam_spec, null)
			return
	# Standalone — fetch coords from embedded table, load locale.
	var standalone_spec: Dictionary = _standalone_fp_camera_for_space(_player_pos)
	var standalone_scene: String = _LOCATION_SCENE_PATHS.get(_location_id, "")
	if not standalone_spec.is_empty() and standalone_scene != "" and ResourceLoader.exists(standalone_scene):
		_render_fp_3d(standalone_spec, standalone_scene)
		return
	if ResourceLoader.exists(_art_path_fp(_player_pos)):
		_render_fp()
	else:
		_render_topdown_map()


# Embedded per-location SPACE → (blender_x, blender_y, yaw_deg)
# tables. Mirrors each GauntletHost's SPACE_MAP so the gauntlet can
# render in 3D when launched standalone (no host loaded). When you
# update a host's SPACE_MAP, copy the change here too — single
# source of truth would be nicer but the host has scene-tree
# specifics (player NodePath etc.) that don't make sense in a
# shared resource.
const _LOCATION_SCENE_PATHS := {
	"dambrosios":          "res://scenes/locales/diner.tscn",
	"cathedral":           "res://scenes/locales/cathedral.tscn",       # Magician
	"elicia_bungalow":     "res://scenes/locales/bungalow.tscn",        # Priestess
	"riverboat_interior":  "res://scenes/locales/riverboat_interior.tscn", # Empress / Emperor / Hierophant
	"roberts_house":       "res://scenes/locales/roberts_kitchen.tscn",
	"ember_ash_office":    "res://scenes/locales/houston_office.tscn",
	# 2026-06-21 Major-Arcana sweep — every reversed-card scenario
	# now lands in its own interior.
	"roadside_chapel":         "res://scenes/locales/roadside_chapel.tscn",        # VI Lovers
	"lacombe_service_garage":  "res://scenes/locales/lacombe_service_garage.tscn", # VII Chariot
	"carnival_lot":            "res://scenes/locales/carnival_lot.tscn",           # VIII Strength
	"bayou_lighthouse":        "res://scenes/locales/bayou_lighthouse.tscn",       # IX Hermit
	"le_roulant_casino":       "res://scenes/locales/le_roulant_casino.tscn",      # X Wheel
	"courthouse_chamber":      "res://scenes/locales/courthouse_chamber.tscn",     # XI Justice
	"simon_apartment":         "res://scenes/locales/simon_apartment.tscn",        # XII Hanged Man
	"asylum_ward_c":           "res://scenes/locales/asylum_ward_c.tscn",          # XIII Death
	"mixing_glass":            "res://scenes/locales/mixing_glass.tscn",           # XIV Temperance
	"daigles_roadhouse":       "res://scenes/locales/daigles_roadhouse.tscn",      # XV Devil
	"wgur_transmitter_shack":  "res://scenes/locales/wgur_transmitter_shack.tscn", # XVI Tower
	"christian_ice_co":        "res://scenes/locales/christian_ice_co.tscn",       # XVII Star
	"static_drive_in":         "res://scenes/locales/static_drive_in.tscn",        # XVIII Moon
	"solenade_garden":         "res://scenes/locales/solenade_garden.tscn",        # XIX Sun
	"parish_cemetery":         "res://scenes/locales/parish_cemetery.tscn",        # XX Judgement
	"frog_knows_best":         "res://scenes/locales/frog_knows_best.tscn",        # XXI World
}

const _STANDALONE_SPACE_VANTAGES := {
	"dambrosios": {
		"parking_lot":    [+12.0,  +0.0, 180.0],
		"hostess_stand":  [+7.6,   -0.5, 180.0],
		"back_door":      [-7.5,   -5.5,  90.0],
		"bar":            [-12.0,  +4.5, 270.0],
		"booth_1":        [-7.95,  +3.75, 0.0],
		"kitchen_alcove": [-6.0,   -5.0,  90.0],
		"grill":          [-4.75,  -5.55, 90.0],
		"dish_station":   [+4.0,   -5.55, 90.0],
		"order_window":   [-5.5,   -3.95, 90.0],
		"booth_4":        [-7.95,  +0.75,  0.0],
		"booth_6":        [-7.95,  -2.25,  0.0],
		"counter":        [-0.85,  -4.1, 159.0],   # John behind counter, gaze NE
		                                            # across the dining floor.
		                                            # User-captured 2026-06-21.
		"bar_stools":     [-10.5,  +3.5, 270.0],
		"under_counter":  [+0.0,   -3.5,  90.0],
		"jukebox":        [-10.5,  +5.0,  90.0],
		"bell":           [-4.5,   -3.5,  90.0],
		"pay_phone":      [+2.32,  +7.27, 180.0],
		"cig_machine":    [+2.32,  +7.5,  180.0],
		"register":       [-3.6,   -3.5,  90.0],
		"bathroom":       [+7.0,   -4.7,  90.0],
		"card_wall":      [+0.0,   +8.28, 270.0],
		"river_window":   [-15.0,  +0.0,   0.0],
	},
	# Cathedral (Magician) — mirrors CathedralGauntletHost.SPACE_MAP
	"cathedral": {
		"warehouse_bay":  [+0.0,  +9.0, 270.0],
		"river_window":   [-11.5, +0.0,   0.0],
		"roof_hatch":     [+0.0,  +0.0,  90.0],
		"magician":       [+0.0,  -3.0,  90.0],   # WORKBENCH — scenario start
		"fool":           [-4.0,  +5.5, 270.0],
		"priestess":      [-7.0,  +5.5, 270.0],
		"empress":        [-6.0,  +7.5, 270.0],
		"emperor":        [-3.0,  +7.0, 270.0],
		"hierophant":     [-10.5, +3.0,   0.0],
		"lovers":         [+4.0,  +5.5, 270.0],
		"chariot":        [+5.0,  +2.0, 180.0],
		"strength":       [-4.0,  +4.0,  90.0],
		"hermit":         [+0.6,  -3.4,  90.0],
		"wheel":          [-6.0,  -2.0,  90.0],
		"justice":        [-8.5,  -1.5,   0.0],
		"hanged_man":     [-3.0,  -2.0,  90.0],
		"death":          [-7.5,  -7.0,  90.0],
		"temperance":     [+5.0,  -3.0, 180.0],
		"devil":          [+8.0,  -5.0, 180.0],
		"tower":          [+6.0,  -2.0,  90.0],
	},
	# Elicia's bungalow (Priestess) — mirrors BungalowGauntletHost.SPACE_MAP
	"elicia_bungalow": {
		"living_room":        [-0.5,  +1.6,  90.0],
		"the_studio":         [+2.8,  +2.4, 180.0],
		"the_editing_desk":   [+3.7,  +1.3,  90.0],   # scenario start
		"the_bookshelf":      [+0.6,  +2.6,   0.0],
		"the_kitchen":        [+2.5,  +4.2,  90.0],
		"the_bedroom":        [-3.0,  +4.0,  90.0],
		"the_bathroom":       [-3.4,  +0.8, 180.0],
		"the_storage_closet": [+0.4,  +1.6,  90.0],
		"the_porch":          [+0.0,  -1.2, 270.0],
		"the_back_yard":      [+0.0,  +8.0,  90.0],
		"front_door":         [+0.0,  -0.6,  90.0],
		"back_gate":          [-4.4,  +9.4,  90.0],
		"roof":               [+1.0,  +2.0,  90.0],
	},
	# Riverboat (Empress / Emperor) — mirrors RiverboatGauntletHost.SPACE_MAP.
	# 4-element entries: [x, y, floor_z, yaw]. Three decks.
	"riverboat_interior": {
		# UPPER DECK (Z=3.2)
		"helm":               [+0.0, -2.4,  3.2,  90.0],
		"office_staircase":   [+3.0, -3.0,  3.2, 270.0],
		# MAIN DECK (Z=0.0)
		"maitre_d_stand":     [+0.0, -8.5,  0.0,  90.0],
		"main_dining_room":   [-1.0, -3.0,  0.0,  90.0],
		"private_dining":     [-4.0, +3.0,  0.0,  90.0],
		"table_17":           [-4.5, -0.7,  0.0, 180.0],
		"sammys_bar":         [+3.5,  0.0,  0.0,   0.0],
		"the_pass":           [+1.5, +5.0,  0.0,  90.0],
		"kitchen":            [+0.0, +8.0,  0.0,  90.0],
		"side_door":          [+5.6, -3.0,  0.0,   0.0],
		"gangway":            [+0.0, -11.0, 0.0, 270.0],
		# LOWER DECK (Z=-2.8)
		"back_corridor":      [+0.0, +6.0, -2.8, 270.0],
		"catering_office":    [-4.5, -1.5, -2.8,   0.0],
		"the_card_room":      [-1.0, -1.0, -2.8,  90.0],
		"the_back_room":      [+2.5, -1.0, -2.8,  90.0],
		"staff_locker_room":  [+4.5, -1.0, -2.8,   0.0],
		"staff_exit":         [+5.0, -5.0, -2.8, 270.0],
	},
	# 2026-06-21 — mirrors of the 16 new arcana hosts' SPACE_MAPs.
	# Entries are 3-element [x, y, yaw] (single-floor locales).
	# Authoritative source: scripts/*GauntletHost.gd SPACE_MAP.
	"roadside_chapel": {
		"altar":        [+0.00, +5.80, 270.0],
		"pew_front":    [+0.00, +2.00,  90.0],
		"pew_rear":     [+0.00, +3.80,  90.0],
		"votive_rack":  [+1.40, +5.60, 180.0],
		"statue_niche": [+2.20, +3.40, 180.0],
		"bell_pull":    [-2.10, +0.60,   0.0],
		"narthex":      [+0.00, +0.40,  90.0],
	},
	"le_roulant_casino": {
		"roulette_table": [+0.00, +4.50,  90.0],
		"slot_bank":      [-4.50, +3.20,   0.0],
		"cashier_cage":   [+3.50, +8.50,  90.0],
		"neon_sign":      [+0.00, +3.00,  90.0],
		"plaza_center":   [+0.00, +6.00,  90.0],
		"front_door":     [+0.00, +0.40,  90.0],
	},
	"mixing_glass": {
		"bar_stool_mid": [+1.05, +5.60,   0.0],
		"bar_stool_w":   [-1.05, +5.60, 180.0],
		"backbar":       [+0.00, +8.40, 270.0],
		"booth_1":       [-1.60, +1.20,   0.0],
		"booth_2":       [-1.60, +3.00,   0.0],
		"booth_3":       [-1.60, +4.80,   0.0],
		"booth_4":       [-1.60, +6.60,   0.0],
		"neon_open":     [-1.40, +7.80, 270.0],
		"alley_door":    [+0.00, +0.40,  90.0],
	},
	"daigles_roadhouse": {
		"bar":           [+0.00, +5.40,  90.0],
		"bar_stool":     [+0.00, +5.60, 270.0],
		"pool_table":    [+1.50, +3.20,  90.0],
		"jukebox":       [-4.10, +4.20,   0.0],
		"gator_head":    [+2.30, +6.80,  90.0],
		"schlitz_neon":  [+0.00, +6.80,  90.0],
		"front_door":    [+0.00, +0.40,  90.0],
	},
	"static_drive_in": {
		"counter":        [-1.60, +3.20, 270.0],
		"popcorn":        [+1.00, +3.20, 270.0],
		"soda_fountain":  [-0.80, +3.10, 270.0],
		"candy_case":     [+0.20, +3.20, 270.0],
		"picture_window": [+0.00, +4.60,  90.0],
		"lot_porch":      [+0.00, +0.40,  90.0],
	},
	"lacombe_service_garage": {
		"bay_lift":     [-2.50, +4.50,   0.0],
		"tow_truck":    [+2.50, +4.50, 180.0],
		"pegboard":     [+0.00, +7.80, 270.0],
		"toolbox":      [-1.40, +8.20, 270.0],
		"pump_island":  [+0.00, -1.20,  90.0],
		"vending":      [+4.30, +1.00,   0.0],
	},
	"carnival_lot": {
		"merry_go_round": [+6.00, +0.00,   0.0],
		"big_top":        [-6.00, +0.00,   0.0],
		"ticket_booth":   [+0.00, +7.00, 270.0],
		"lion_cage":      [-1.50, -5.50,  90.0],
		"banner_posts":   [-3.50, -7.00,  90.0],
		"front_gate":     [+0.00, -9.00,  90.0],
	},
	"bayou_lighthouse": {
		"writing_desk":  [+1.60, -0.20, 180.0],
		"bunk":          [+0.00, -1.60,  90.0],
		"spiral_stair":  [-0.60, -0.60,   0.0],
		"n_window":      [+0.00, +2.30,  90.0],
		"lens_hatch":    [+0.00, +0.80,  90.0],
		"door":          [+0.00, -2.30,  90.0],
	},
	"courthouse_chamber": {
		"judge_bench":      [+0.00,  +9.80, 270.0],
		"witness_stand":    [+2.40,  +9.60, 180.0],
		"jury_box":         [-3.70,  +6.00,   0.0],
		"plaintiff_table":  [-1.50,  +5.50,  90.0],
		"defense_table":    [+1.50,  +5.50,  90.0],
		"pew_front":        [+0.00,  +1.50,  90.0],
		"bar_rail":         [+0.00,  +4.20,  90.0],
		"flag_us":          [+3.20, +11.40, 180.0],
		"flag_state":       [-3.20, +11.40,   0.0],
		"rear_door":        [+0.00,  +0.40,  90.0],
	},
	"simon_apartment": {
		"armchair":      [+0.50, +2.40, 180.0],
		"bed":           [+1.40, +5.70, 180.0],
		"kitchenette":   [-1.80, +2.40,   0.0],
		"tv":            [-0.50, +2.20,   0.0],
		"tipped_chair":  [-1.20, +3.20,  90.0],
		"hanging_boot":  [-2.30, +5.50,   0.0],
		"front_window":  [+0.00, +0.80, 270.0],
		"front_door":    [+1.80, +0.40,  90.0],
	},
	"asylum_ward_c": {
		"nurses_station": [+0.00,  +7.00,  90.0],
		"ward_1":         [-2.40,  +1.40,   0.0],
		"ward_2":         [-2.40,  +3.80,   0.0],
		"ward_3":         [-2.40,  +6.20,   0.0],
		"ward_4":         [-2.40,  +8.60,   0.0],
		"ward_5":         [-2.40, +11.00,   0.0],
		"gurney":         [+0.40, +11.00, 180.0],
		"wheelchair":     [-1.20,  +1.50,  90.0],
		"cupola_below":   [+0.00, +13.20,  90.0],
		"corridor_s":     [+0.00,  +0.40,  90.0],
	},
	"wgur_transmitter_shack": {
		"operator_desk": [-0.40, +1.40,  90.0],
		"rack_a":        [-2.20, +1.20,   0.0],
		"rack_b":        [-2.20, +2.00,   0.0],
		"rack_c":        [-2.20, +2.80,   0.0],
		"patch_panel":   [+2.20, +2.20, 180.0],
		"mic_stand":     [-0.70, +1.40,  90.0],
		"n_window":      [+0.00, +3.80,  90.0],
		"door":          [+0.00, +0.40,  90.0],
	},
	"christian_ice_co": {
		"retail_counter":   [+0.00,  +2.40, 270.0],
		"block_freezer":    [+0.00,  +3.80,  90.0],
		"chest_freezer_a": [-3.90,  +4.50,   0.0],
		"chest_freezer_b": [-3.90,  +6.30,   0.0],
		"chest_freezer_c": [-3.90,  +8.10,   0.0],
		"compressor_1":     [+1.80,  +6.50, 180.0],
		"brine_tank":       [+1.80,  +8.50, 180.0],
		"dock_door":        [+0.00, +10.60, 270.0],
		"storefront":       [+0.00,  +0.40,  90.0],
	},
	"solenade_garden": {
		"central_oak":    [+0.00, +0.00,  90.0],
		"sundial":        [+0.00, -3.40,  90.0],
		"bench_n":        [+0.00, +7.40, 270.0],
		"bench_s":        [+0.00, -7.40,  90.0],
		"bench_e":        [+7.40, +0.00, 180.0],
		"bench_w":        [-7.40, +0.00,   0.0],
		"pergola_arch":   [+0.00, +7.80, 270.0],
		"flowerbed_ne":   [+3.00, +3.00,   0.0],
		"flowerbed_nw":   [-3.00, +3.00,   0.0],
		"gate":           [+0.00, -7.80,  90.0],
	},
	"parish_cemetery": {
		"central_mausoleum": [+0.00,  +0.00, 270.0],
		"path_spine_n":      [+0.00,  +5.00, 270.0],
		"path_spine_s":      [+0.00,  -5.00,  90.0],
		"vault_row_w":       [-7.00,  +0.00,   0.0],
		"vault_row_e":       [+7.00,  +0.00, 180.0],
		"vault_row_n":       [+0.00,  +7.00, 270.0],
		"lamp_central":      [+1.20,  +0.00, 180.0],
		"oak_sw":            [-8.50,  -8.00,   0.0],
		"gate":              [+0.00,  -9.00,  90.0],
	},
	"frog_knows_best": {
		"retail_counter": [+0.00, +2.20, 270.0],
		"minnow_tank":    [-1.70, +6.50,  90.0],
		"catfish_tank":   [+0.00, +6.50,  90.0],
		"frog_tank":      [+1.70, +6.50,  90.0],
		"nightcrawler":   [+2.40, +2.20, 180.0],
		"pegboard_w":     [-2.90, +3.50,   0.0],
		"pegboard_e":     [+2.90, +3.50, 180.0],
		"porch":          [+0.00, -1.60,  90.0],
		"front_door":     [+0.00, +0.40,  90.0],
	},
}


func _standalone_fp_camera_for_space(space_id: String) -> Dictionary:
	var loc_table: Dictionary = _STANDALONE_SPACE_VANTAGES.get(_location_id, {})
	var entry: Variant = loc_table.get(space_id, null)
	if entry == null:
		return {}
	var b_x: float = entry[0]
	var b_y: float = entry[1]
	# Riverboat uses 4-element entries (multi-deck): [x, y, floor_z, yaw].
	# Every other location uses 3-element: [x, y, yaw]. Detect by length.
	var floor_z: float = 0.0
	var yaw_deg: float = 0.0
	if entry.size() >= 4:
		floor_z = entry[2]
		yaw_deg = entry[3]
	else:
		yaw_deg = entry[2]
	# Camera yaw = blender_yaw - 90 (Camera3D forward -Z, see
	# DinerGauntletHost.get_fp_camera_for_space for full table).
	var godot_yaw_deg: float = yaw_deg - 90.0
	return {
		"origin":   Vector3(b_x, floor_z + 2.30, -b_y),
		"rotation": Vector3(-0.05, deg_to_rad(godot_yaw_deg), 0.0),
		"fov":      62.0,
	}


# Walks /root looking for a node with a get_fp_camera_for_space
# method (DinerGauntletHost / CathedralGauntletHost / etc.). Returns
# the first match. Cached after first lookup for the gauntlet's
# lifetime.
var _cached_gauntlet_host: Node = null
func _find_gauntlet_host() -> Node:
	if _cached_gauntlet_host != null and is_instance_valid(_cached_gauntlet_host):
		return _cached_gauntlet_host
	_cached_gauntlet_host = _walk_for_host(get_tree().root)
	return _cached_gauntlet_host


func _walk_for_host(node: Node) -> Node:
	if node.has_method("get_fp_camera_for_space"):
		return node
	for child in node.get_children():
		var hit := _walk_for_host(child)
		if hit != null:
			return hit
	return null


# Pre-add cleanup for STANDALONE locale instances. Mirrors what
# Background3D._suppress_interactive_nodes does for VN scenes:
# strip the Player + the HUD CanvasLayer so they don't fight the
# gauntlet for input / overlap our panel. PostProcess stays — we
# WANT the shader treatment on the gauntlet's 3D view.
func _strip_locale_runtime_nodes(root: Node) -> void:
	# Pre-add cleanup. Remove the locale's:
	#   · Player CharacterBody3D — would compete for input
	#   · HUD/Debug CanvasLayers — would draw on top of the gauntlet UI
	# KEEP (with neutering) the locale's PostProcess CanvasLayer
	# (MoodCycler). The MoodCycler controls lights, environment, mood
	# strata, blend modes, and style packs — all of which the user
	# drives via F3/F9/F10/F11/F12 in the debug overlay. Previously
	# we queue_free'd it (because its default 'dambrosios_3am' style
	# pack dimmed every light to near-zero), but that broke the F-key
	# debug controls in the gauntlet. New approach: keep it alive, but
	# clear `default_style_pack` BEFORE its _ready fires so no dimming
	# auto-applies; user starts at the locale's native lighting and
	# can cycle from there. Visibility OFF — the gauntlet's shader
	# stack lives on the SubViewportContainer, not on this canvas
	# layer's screen-space shaders (which break in SubViewports under
	# the Compatibility renderer anyway).
	var to_remove: Array[Node] = []
	for n in _walk_tree(root):
		if n is CharacterBody3D and n.is_in_group("player"):
			to_remove.append(n)
		elif n is CanvasLayer:
			# Is this the locale's MoodCycler? Detected by the
			# `default_style_pack` property the MoodCycler script
			# exports — robust against renames of the CanvasLayer
			# node itself.
			if "default_style_pack" in n:
				n.set("default_style_pack", "")
				(n as CanvasLayer).visible = false
				continue
			to_remove.append(n)
	for n in to_remove:
		var parent: Node = n.get_parent()
		if parent != null:
			parent.remove_child(n)
		n.queue_free()


# Public accessor — the VN debug overlay finds the gauntlet's
# in-SubViewport MoodCycler through this. Returns null if no
# locale is loaded (PNG fallback or top-down map mode).
func get_fp_mood_cycler() -> Node:
	if _cached_fp_vp == null or not is_instance_valid(_cached_fp_vp):
		return null
	return _walk_for_mood_cycler(_cached_fp_vp)


func _walk_for_mood_cycler(node: Node) -> Node:
	if node is CanvasLayer and ("default_style_pack" in node):
		return node
	for child in node.get_children():
		var hit: Node = _walk_for_mood_cycler(child)
		if hit != null:
			return hit
	return null


func _walk_tree(node: Node, out: Array[Node] = []) -> Array[Node]:
	out.append(node)
	for child in node.get_children():
		_walk_tree(child, out)
	return out


func _count_descendants(root: Node) -> int:
	var n: int = 0
	for _c in _walk_tree(root):
		n += 1
	return n


# If the loaded locale instance didn't bring a WorldEnvironment that
# auto-attached to this SubViewport's World3D, install a sane default
# so the gauntlet's standalone-3D view isn't rendering against the
# engine's gray fallback sky.
func _ensure_subviewport_environment(vp: SubViewport, locale_root: Node) -> void:
	# Already a WorldEnvironment in the loaded tree? Trust it.
	for n in _walk_tree(locale_root):
		if n is WorldEnvironment:
			print("[Gauntlet FP] using locale's WorldEnvironment: %s" % n.name)
			return
	# Nothing found — install a default warm-interior env.
	var we := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.04, 0.05, 0.07, 1.0)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.78, 0.74, 0.66, 1.0)
	env.ambient_light_energy = 0.85
	env.fog_enabled = true
	env.fog_light_color = Color(0.62, 0.58, 0.52, 1.0)
	env.fog_light_energy = 0.4
	env.fog_density = 0.004
	we.environment = env
	vp.add_child(we)
	print("[Gauntlet FP] spawned fallback WorldEnvironment in SubViewport")


const _BACKGROUND_3D_SCENE = preload("res://scenes/vn/Background3D.tscn")
const _LOCATION_TO_BG_PRESET := {
	"dambrosios":         "diner_interior",
	"cathedral_of_rust":  "diner_interior",       # TODO add cathedral preset
	"bungalow":           "diner_interior",       # TODO add bungalow preset
	"riverboat_interior": "diner_interior",       # TODO add riverboat preset
}
var _gauntlet_bg3d: Node = null   # cached Background3D instance


# Live-3D FP render. Two modes:
#   · standalone_scene == null → HOST mode. SubViewport with
#     own_world_3d=false, sharing the host locale's World3D.
#   · standalone_scene == "res://…/locale.tscn" → STANDALONE
#     mode. NEW: use Background3D.tscn (proven in VN bg-3D)
#     instead of building a SubViewport from scratch. Only
#     creates the bg3d ONCE per gauntlet session; subsequent
#     space changes just call set_camera_vantage() to retarget.
var _cached_fp_vc: SubViewportContainer = null
var _cached_fp_vp: SubViewport = null
var _cached_fp_cam: Camera3D = null
var _cached_fp_standalone_loaded: bool = false


func _render_fp_3d(cam_spec: Dictionary, standalone_scene) -> void:
	if _board_content == null:
		return
	# Kill any FP-PNG scan tween + clear stale meeple positions
	if _fp_scan_tween != null and _fp_scan_tween.is_valid():
		_fp_scan_tween.kill()
	_fp_scan_tween = null
	_fp_bg = null
	_board_space_nodes.clear()
	_board_marker_pos.clear()

	# Build the SubViewport pipeline ONCE per gauntlet session.
	# Subsequent space changes only retarget the camera — that
	# avoids the locale-reload + LocaleSetup-material-commit race
	# that produced the grey-first-frame (and gray-after-rebuild
	# cascade from the redraw kick).
	if not _is_fp_cache_valid():
		_build_fp_cache(cam_spec, standalone_scene)
	else:
		# Clear stale board contents EXCEPT the cached FP nodes +
		# persistent meeple overlays.
		for c in _board_content.get_children():
			var cnm: String = c.name
			if cnm == "player_meeple" or cnm.begins_with("visitor_") or cnm.begins_with("threat_"):
				continue
			if c == _cached_fp_vc:
				continue
			c.queue_free()

	# Per-space camera retarget — runs regardless of cache hit.
	if _cached_fp_cam != null and is_instance_valid(_cached_fp_cam):
		_cached_fp_cam.position = cam_spec.get("origin", Vector3.ZERO)
		_cached_fp_cam.rotation = cam_spec.get("rotation", Vector3.ZERO)
		_cached_fp_cam.fov = float(cam_spec.get("fov", 62.0))
		_cached_fp_cam.current = true
	# Re-pin persistent meeple overlays above the cached SubViewport
	_restore_persistent_meeples_overlay()
	print("[Gauntlet FP] retargeted → space=%s cam=%s" %
		[_player_pos, cam_spec.get("origin", Vector3.ZERO)])


# Public accessor for the gauntlet FP SubViewportContainer's
# ShaderMaterial. The VN debug overlay's GAUNTLET SHADER section
# writes per-effect uniforms through this. Returns null if the
# cache hasn't been built (e.g. PNG-fallback or top-down map mode).
func get_fp_shader_material() -> ShaderMaterial:
	if _cached_fp_vc == null or not is_instance_valid(_cached_fp_vc):
		return null
	return _cached_fp_vc.material as ShaderMaterial


func _is_fp_cache_valid() -> bool:
	if _cached_fp_vc == null or not is_instance_valid(_cached_fp_vc):
		return false
	if _cached_fp_vp == null or not is_instance_valid(_cached_fp_vp):
		return false
	if _cached_fp_cam == null or not is_instance_valid(_cached_fp_cam):
		return false
	# Container must still be a child of board_content (board may
	# have been wholesale rebuilt by other code paths)
	if _cached_fp_vc.get_parent() != _board_content:
		return false
	return true


func _build_fp_cache(cam_spec: Dictionary, standalone_scene) -> void:
	# Tear down any stale board contents (PNG bg, old map, etc.) but
	# keep persistent meeples.
	for c in _board_content.get_children():
		var cnm: String = c.name
		if cnm == "player_meeple" or cnm.begins_with("visitor_") or cnm.begins_with("threat_"):
			continue
		c.queue_free()
	# Black floor under everything
	var floor_rect := ColorRect.new()
	floor_rect.name = "board_floor"
	floor_rect.color = Color(0, 0, 0, 1)
	floor_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	floor_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_board_content.add_child(floor_rect)
	# SubViewportContainer + SubViewport
	var vc := SubViewportContainer.new()
	vc.name = "fp_3d_container"
	vc.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	vc.stretch = true
	vc.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_board_content.add_child(vc)
	var vp := SubViewport.new()
	vp.name = "fp_viewport"
	vp.own_world_3d = (standalone_scene != null)
	# Fixed 1280×720 internal render size — matches Background3D.tscn
	# exactly (the only proven-working SubViewport pipeline in this
	# project). Letting stretch=true auto-size against the gauntlet
	# panel's potentially-zero-initial layout was producing 0×0
	# SubViewports → no first render, then gray cached texture
	# committed BEFORE the panel laid out. Fixed size dodges that
	# whole race.
	vp.size = Vector2i(1280, 720)
	vp.handle_input_locally = true
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	vc.add_child(vp)
	# stretch_shrink ensures the SubViewport texture scales down to
	# the container size on display — combined with the fixed
	# internal size, we always render at 1280×720 and downscale to
	# whatever the panel ends up being.
	vc.stretch_shrink = 1
	# Standalone mode — load the locale into the SubViewport's own world
	if standalone_scene != null and standalone_scene != "":
		var ps: PackedScene = load(standalone_scene) as PackedScene
		if ps == null:
			push_warning("[Gauntlet FP] Failed to load %s — falling back to top-down map" % standalone_scene)
			vc.queue_free()
			_render_topdown_map()
			return
		var inst: Node = ps.instantiate()
		_strip_locale_runtime_nodes(inst)
		vp.add_child(inst)
		print("[Gauntlet FP] cache built — loaded %s, %d nodes" %
			[standalone_scene, _count_descendants(inst)])
		_ensure_subviewport_environment(vp, inst)
		_cached_fp_standalone_loaded = true
	# Camera
	var cam := Camera3D.new()
	cam.name = "fp_camera"
	cam.position = cam_spec.get("origin", Vector3.ZERO)
	cam.rotation = cam_spec.get("rotation", Vector3.ZERO)
	cam.fov = float(cam_spec.get("fov", 62.0))
	cam.near = 0.05
	cam.far = 200.0
	cam.current = true
	vp.add_child(cam)
	# Cache
	_cached_fp_vc = vc
	_cached_fp_vp = vp
	_cached_fp_cam = cam
	# Post-process shader on the SubViewportContainer. Same pattern
	# as VN portraits: a canvas_item shader sampling TEXTURE (the
	# SubViewport's render target). Lives here instead of as a
	# locale PostProcess CanvasLayer because BackBufferCopy /
	# SCREEN_TEXTURE reads don't work inside SubViewports under the
	# Compatibility renderer. Master strength=0 by default → pure
	# pass-through; the VN debug panel's GAUNTLET SHADER section
	# dials in per-effect strengths.
	var sm := ShaderMaterial.new()
	var shader: Shader = load("res://assets/shaders/portrait_demon_static.gdshader") as Shader
	if shader != null:
		sm.shader = shader
		# Initialise EVERY uniform the debug overlay reads. Without
		# this, get_shader_parameter() returns null for any uniform
		# not explicitly set, and the overlay's `float(...)` calls
		# crash with "Nonexistent 'float' constructor".
		sm.set_shader_parameter("strength", 0.0)
		for u in ["aberration_str", "tear_str", "noise_str",
		          "dropband_str", "hue_shift", "vignette_str",
		          "invert_str", "bloom_str", "film_grain_str",
		          "emboss_str", "duotone_str", "ascii_str"]:
			sm.set_shader_parameter(u, 0.0)
		sm.set_shader_parameter("pixelate_size", 1.0)
		sm.set_shader_parameter("posterize_lvl", 32.0)
		sm.set_shader_parameter("temp_shift", 0.0)
		vc.material = sm
	print("[Gauntlet FP] cache built — vp=%s container=%s" % [vp.size, vc.size])
	# Warm the cache. First render after a cold build is reliably
	# grey (locale _ready cascade still committing materials + light
	# state). User report: "moving had a clear view every single
	# time, initial load always gray." The cache is stable from the
	# FIRST space-change retarget — so we synthesise that retarget
	# now via a Timer (no lambda capture, self-frees on timeout).
	_schedule_fp_warmup(0.30)


# Warmup-retarget the cached camera after a delay. Mimics what a
# space-change retarget does, which empirically lands clean. Timer
# is a child node so its lifetime is tied to the gauntlet.
func _schedule_fp_warmup(delay: float) -> void:
	var t := Timer.new()
	t.one_shot = true
	t.wait_time = delay
	t.autostart = true
	add_child(t)
	t.timeout.connect(_warmup_fp_cam)
	t.timeout.connect(t.queue_free)


func _warmup_fp_cam() -> void:
	if not _is_fp_cache_valid():
		return
	# Empirical: an INITIAL render after cache build is grey, but
	# the FIRST space-change retarget renders clean. The retarget
	# moves the camera position; nothing else changes. So forge a
	# fake "movement" by nudging the camera by 1cm, then back. This
	# mimics what walking to a new space does. Combined with the
	# 300ms delay (post locale _ready settle), the SubViewport
	# wakes up and starts producing the lit texture.
	var cam_spec: Dictionary = {}
	var host: Node = _find_gauntlet_host()
	if host != null and host.has_method("get_fp_camera_for_space"):
		cam_spec = host.get_fp_camera_for_space(_player_pos)
	if cam_spec.is_empty():
		cam_spec = _standalone_fp_camera_for_space(_player_pos)
	if cam_spec.is_empty():
		return
	var target_pos: Vector3 = cam_spec.get("origin", Vector3.ZERO)
	var target_rot: Vector3 = cam_spec.get("rotation", Vector3.ZERO)
	var target_fov: float = float(cam_spec.get("fov", 62.0))
	# Nudge — move 1cm to the side, then back
	_cached_fp_cam.position = target_pos + Vector3(0.01, 0, 0)
	_cached_fp_cam.rotation = target_rot
	_cached_fp_cam.fov = target_fov
	_cached_fp_cam.current = false
	_cached_fp_cam.current = true
	# Defer the actual position restore so the SubViewport has a
	# frame to pick up the change
	_cached_fp_cam.position = target_pos
	_cached_fp_vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	print("[Gauntlet FP] cache warmed — pulsed cam to wake SubViewport")
	# Belt-and-suspenders: a second pulse at +200ms in case the
	# first one was still too early.
	_schedule_fp_warmup_2(0.20)


func _schedule_fp_warmup_2(delay: float) -> void:
	var t := Timer.new()
	t.one_shot = true
	t.wait_time = delay
	t.autostart = true
	add_child(t)
	t.timeout.connect(_pulse_fp_cam_again)
	t.timeout.connect(t.queue_free)


func _pulse_fp_cam_again() -> void:
	if not _is_fp_cache_valid():
		return
	var p: Vector3 = _cached_fp_cam.position
	_cached_fp_cam.position = p + Vector3(0.01, 0, 0)
	_cached_fp_cam.current = false
	_cached_fp_cam.current = true
	_cached_fp_cam.position = p
	print("[Gauntlet FP] second pulse fired")


func _finish_fp_3d_setup(cam: Camera3D, vp: SubViewport) -> void:
	# Single-pass settle. By now (one deferred frame after the
	# SubViewport was built) the container has been laid out, the
	# locale's _ready cascade has run, lights are live, and the
	# WorldEnvironment is attached. Flip the camera current and
	# turn rendering on. No timer chain — that was emitting
	# "Lambda capture freed" errors when _draw_board re-fired
	# before the timer ticked, since the lambda outlived its
	# captured vp.
	if not is_instance_valid(cam) or not is_instance_valid(vp):
		return
	var container := vp.get_parent()
	if container is SubViewportContainer:
		var sz: Vector2 = (container as SubViewportContainer).size
		if sz.x > 0 and sz.y > 0:
			vp.size = Vector2i(int(sz.x), int(sz.y))
	cam.current = true
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	print("[Gauntlet FP] settled — subviewport %s UPDATE_ALWAYS" % vp.size)
	# Re-overlay the persistent meeples last
	_restore_persistent_meeples_overlay()


# After _render_fp_3d / _render_fp swaps the bg, walk the existing
# meeple/visitor/threat nodes and lift them above the new bg so
# the player can still see them. Idempotent — safe to call multiple
# times per render.
func _restore_persistent_meeples_overlay() -> void:
	if _board_content == null:
		return
	for c in _board_content.get_children():
		var cnm: String = c.name
		if cnm == "player_meeple" or cnm.begins_with("visitor_") or cnm.begins_with("threat_"):
			_board_content.move_child(c, -1)


func _render_topdown_map() -> void:
	if _board_content == null:
		return
	# Coming out of FP mode — kill the scan tween so it doesn't
	# tick against a node we're about to free.
	if _fp_scan_tween != null and _fp_scan_tween.is_valid():
		_fp_scan_tween.kill()
	_fp_scan_tween = null
	_fp_bg = null
	# Coming back from FP mode? Reveal the meeples we hid.
	if _board_meeple != null and is_instance_valid(_board_meeple):
		_board_meeple.visible = true
	for vid in _board_visitor_nodes.keys():
		var vn: Control = _board_visitor_nodes[vid]
		if is_instance_valid(vn):
			vn.visible = true
	for tid in _board_threat_nodes.keys():
		var tn: Control = _board_threat_nodes[tid]
		if is_instance_valid(tn):
			tn.visible = true
	# Static layout (bg, adjacency lines, markers, labels) is torn
	# down every render so highlight/chevron can follow the player.
	# MEEPLES are persistent — recreating them each render produced
	# a visible judder as freshly-spawned nodes snapped from (0,0)
	# to their target. We keep player_meeple + visitor_* across
	# renders and only re-add/remove on actual state changes.
	_board_space_nodes.clear()
	_board_marker_pos.clear()
	for c in _board_content.get_children():
		var cnm: String = c.name
		if cnm == "player_meeple" or cnm.begins_with("visitor_") or cnm.begins_with("threat_"):
			continue
		c.queue_free()
	# Opaque black floor under the board — kills any bleed-through
	# from whatever rendered behind the gauntlet (codex card art,
	# visualizer canvas, etc.). The optional painted bg image is
	# drawn ON TOP of this; engine-drawn markers, labels, meeples,
	# threats all stack above. The floor is named so the cleanup
	# loop above doesn't double-free it across renders.
	var floor_rect := ColorRect.new()
	floor_rect.name = "board_floor"
	floor_rect.color = Color(0, 0, 0, 1)
	floor_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	floor_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_board_content.add_child(floor_rect)
	# Background image layer (rendered first so labels draw on top).
	# If the location-specific board art is missing, fall back to the
	# bare grid we used to render.
	var bg_tex: Texture2D = _load_texture_silent(_art_path_board()) if _board_bg_visible else null
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
		bg.modulate = Color(1, 1, 1, 0.12)
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
	# Margins: ~50px left + ~160px right give the longest label
	# (UNDER COUNTER, JUKEBOX, etc.) room to extend past its marker
	# without clipping the right edge. Bottom margin extra for the
	# meeple stack hanging under the last row.
	var pad_left: float = 50.0
	var pad_right: float = 160.0
	var pad_top: float = 28.0
	var pad_bottom: float = 80.0
	var sx: float = (panel_size.x - pad_left - pad_right) / maxf(1.0, bx_max - bx_min)
	var sy: float = (panel_size.y - pad_top - pad_bottom) / maxf(1.0, by_max - by_min)
	# Meeple / marker / line scale — sized so the board reads at any
	# viewport. Reference size is the fullscreen board (~1200x600);
	# normal-mode board is much smaller, so we scale markers/meeples
	# down proportionally. Clamped so things never get unreadable.
	var ui_scale: float = clamp(min(panel_size.x / 1100.0, panel_size.y / 560.0), 0.50, 1.20)
	var marker_size: float = 12.0 * ui_scale
	var player_meeple_size: float = 28.0 * ui_scale
	var visitor_meeple_size: float = 22.0 * ui_scale
	var meeple_stack_offset: float = 14.0 * ui_scale
	var label_offset: float = 10.0 * ui_scale
	_board_ui_scale = ui_scale
	_board_visitor_stack_offset = meeple_stack_offset
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
		var px: float = (float(xy_p[0]) - bx_min) * sx + pad_left
		var py: float = (float(xy_p[1]) - by_min) * sy + pad_top
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
		marker.custom_minimum_size = Vector2(marker_size, marker_size)
		marker.size = Vector2(marker_size, marker_size)
		marker.position = Vector2(nx - marker_size * 0.5, ny - marker_size * 0.5)
		_board_marker_pos[sid] = Vector2(nx, ny)
		var mst := StyleBoxFlat.new()
		var kind: String = s.get("kind", "named")
		match kind:
			"threshold": mst.bg_color = Color(0.55, 0.95, 0.65, 0.9)
			"search":    mst.bg_color = Color(0.95, 0.78, 0.40, 0.9)
			_:           mst.bg_color = Color(0.82, 0.78, 0.70, 0.8)
		mst.border_color = Color(0, 0, 0, 0.8)
		mst.set_border_width_all(1)
		mst.set_corner_radius_all(marker_size * 0.5)
		marker.add_theme_stylebox_override("panel", mst)
		_board_content.add_child(marker)
		var node := _make_space_label(s)
		node.position = Vector2(nx + label_offset, ny - 8.0 * ui_scale)
		node.name = "space_" + sid
		_board_content.add_child(node)
		_board_space_nodes[sid] = node
	# Player meeple — persistent across renders. Create on first
	# render, resize to current ui_scale otherwise.
	if _board_meeple == null or not is_instance_valid(_board_meeple):
		var player_art: Texture2D = _load_texture_silent(_art_path_meeple("john"))
		if player_art:
			var mp := TextureRect.new()
			mp.texture = player_art
			mp.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
			mp.name = "player_meeple"
			_board_meeple = mp
		else:
			var lbl_m := Label.new()
			lbl_m.text = "★"
			lbl_m.add_theme_color_override("font_color", C_ACCENT)
			lbl_m.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1))
			lbl_m.name = "player_meeple"
			_board_meeple = lbl_m
		_board_meeple.mouse_filter = Control.MOUSE_FILTER_STOP
		# Place it on the marker immediately so the very first frame
		# doesn't show a (0,0) ghost.
		if _board_marker_pos.has(_player_pos):
			var pms: Vector2 = Vector2(player_meeple_size, player_meeple_size)
			_board_meeple.position = _board_marker_pos[_player_pos] - pms * 0.5
		_board_content.add_child(_board_meeple)
	_board_meeple.custom_minimum_size = Vector2(player_meeple_size, player_meeple_size)
	_board_meeple.size = Vector2(player_meeple_size, player_meeple_size)
	if _board_meeple is Label:
		(_board_meeple as Label).add_theme_constant_override("outline_size", int(max(2, 4.0 * ui_scale)))
		(_board_meeple as Label).add_theme_font_size_override("font_size", int(max(11, 18.0 * ui_scale)))
	_board_meeple.tooltip_text = _tooltip_for_player()
	# Visitor meeples — persistent. Drop nodes for visitors who left
	# or haven't arrived; add nodes for newly-arrived visitors.
	var present_vids: Dictionary = {}
	for vid in _visitors_state:
		if _visitors_state[vid].get("arrived", false):
			present_vids[vid] = true
	for vid in _board_visitor_nodes.keys():
		if not present_vids.has(vid):
			var stale: Control = _board_visitor_nodes[vid]
			if is_instance_valid(stale):
				stale.queue_free()
			_board_visitor_nodes.erase(vid)
	for vid in present_vids.keys():
		var vdef: Dictionary = _visitors_def[vid]
		var vnode: Control
		if _board_visitor_nodes.has(vid) and is_instance_valid(_board_visitor_nodes[vid]):
			vnode = _board_visitor_nodes[vid]
		else:
			var vis_art: Texture2D = _load_texture_silent(_art_path_meeple(vid))
			if vis_art:
				var vm := TextureRect.new()
				vm.texture = vis_art
				vm.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
				vnode = vm
			else:
				var dot := Label.new()
				dot.text = "●"
				dot.add_theme_color_override("font_color", Color(vdef.get("accent", "#c8a268")))
				dot.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1))
				vnode = dot
			vnode.name = "visitor_" + vid
			vnode.mouse_filter = Control.MOUSE_FILTER_STOP
			# Spawn at the marker so it doesn't slide from (0,0).
			var vp: String = String(_visitors_state[vid].get("pos", ""))
			if _board_marker_pos.has(vp):
				var vms: Vector2 = Vector2(visitor_meeple_size, visitor_meeple_size)
				vnode.position = _board_marker_pos[vp] - vms * 0.5
			_board_content.add_child(vnode)
			_board_visitor_nodes[vid] = vnode
		vnode.custom_minimum_size = Vector2(visitor_meeple_size, visitor_meeple_size)
		vnode.size = Vector2(visitor_meeple_size, visitor_meeple_size)
		if vnode is Label:
			(vnode as Label).add_theme_constant_override("outline_size", int(max(2, 3.0 * ui_scale)))
			(vnode as Label).add_theme_font_size_override("font_size", int(max(10, 14.0 * ui_scale)))
		vnode.tooltip_text = _tooltip_for_visitor(vid)
	# Threat meeples — persistent like visitors. Drop instances that
	# are no longer active; add ones that are new.
	var active_tids: Dictionary = {}
	for inst: Dictionary in _threats_active:
		active_tids[String(inst.get("id", ""))] = true
	for tid in _board_threat_nodes.keys():
		if not active_tids.has(tid):
			var stale_t: Control = _board_threat_nodes[tid]
			if is_instance_valid(stale_t):
				stale_t.queue_free()
			_board_threat_nodes.erase(tid)
	var threat_meeple_size: float = 18.0 * ui_scale
	for inst: Dictionary in _threats_active:
		var tid: String = String(inst.get("id", ""))
		var tdef: Dictionary = _threats_def.get(inst.get("def_id", ""), {})
		var ticks: int = int(inst.get("ticks_remaining", 0))
		var glyph_text: String = "%s %d" % [String(tdef.get("glyph", "✕")), ticks]
		var tnode: Control
		if _board_threat_nodes.has(tid) and is_instance_valid(_board_threat_nodes[tid]):
			tnode = _board_threat_nodes[tid]
		else:
			var glyph := Label.new()
			glyph.add_theme_color_override("font_color", Color(tdef.get("tint", "#ff8060")))
			glyph.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1))
			tnode = glyph
			tnode.name = "threat_" + tid
			tnode.mouse_filter = Control.MOUSE_FILTER_STOP
			var tp: String = String(inst.get("pos", ""))
			if _board_marker_pos.has(tp):
				var tms: Vector2 = Vector2(threat_meeple_size, threat_meeple_size)
				tnode.position = _board_marker_pos[tp] - tms * 0.5
			_board_content.add_child(tnode)
			_board_threat_nodes[tid] = tnode
		if tnode is Label:
			(tnode as Label).text = glyph_text
			(tnode as Label).add_theme_constant_override("outline_size", int(max(2, 3.0 * ui_scale)))
			(tnode as Label).add_theme_font_size_override("font_size", int(max(11, 16.0 * ui_scale)))
		# Two-glyph cluster needs more horizontal room than a single dot.
		tnode.custom_minimum_size = Vector2(threat_meeple_size * 1.8, threat_meeple_size)
		tnode.size = Vector2(threat_meeple_size * 1.8, threat_meeple_size)
		tnode.tooltip_text = "[%s]\n%s\n\n%d turn(s) until it fades on its own.\n%s" % [
			String(tdef.get("title", "threat")),
			String(tdef.get("flavor", "")),
			ticks,
			_threat_clear_hint(tdef)]
	_position_meeples()


# 1st-person view of the current space. Painted bg fills the panel;
# bottom strip shows a navigation bar listing the adjacent spaces
# (click → walk there); right edge stacks any visitors/threats at
# the player's current space. Player meeple is hidden in this mode
# — the camera IS the player.
func _render_fp() -> void:
	if _board_content == null:
		return
	# Kill the previous FP scan tween + drop our reference to the
	# old bg BEFORE freeing it. Prevents the recursive tween
	# callback from firing against a freed TextureRect.
	if _fp_scan_tween != null and _fp_scan_tween.is_valid():
		_fp_scan_tween.kill()
	_fp_scan_tween = null
	_fp_bg = null
	_board_space_nodes.clear()
	_board_marker_pos.clear()
	for c in _board_content.get_children():
		var cnm: String = c.name
		if cnm == "player_meeple" or cnm.begins_with("visitor_") or cnm.begins_with("threat_"):
			continue
		c.queue_free()
	# Opaque black floor underneath everything else (same role as
	# in _render_topdown_map — kills bleed-through from whatever's
	# behind the gauntlet).
	var floor_rect := ColorRect.new()
	floor_rect.name = "board_floor"
	floor_rect.color = Color(0, 0, 0, 1)
	floor_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	floor_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_board_content.add_child(floor_rect)
	# Background — the painted 1st-person view of this space. We
	# already gated on existence at the caller, so this should load.
	# The bg is rendered slightly oversized (110%) and pinned at top-
	# left so a subtle pan animation has room to "scan" the view
	# without revealing the panel's empty edges.
	var fp_tex: Texture2D = _load_texture_silent(_art_path_fp(_player_pos))
	if fp_tex:
		var bg := TextureRect.new()
		bg.name = "fp_bg"
		bg.texture = fp_tex
		var content_size: Vector2 = _board_content.size
		if content_size.x <= 0:
			content_size = Vector2(700, 480)
		var bg_scale: float = 1.10
		bg.custom_minimum_size = content_size * bg_scale
		bg.size = content_size * bg_scale
		# Start centered (5% slack on each side).
		bg.position = -content_size * (bg_scale - 1.0) * 0.5
		bg.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
		bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_board_content.add_child(bg)
		# Kick off a slow random scan — the painted view drifts in
		# different directions, returns near center, drifts again.
		# _fp_bg is the class member the scan reads (no lambda
		# capture, no freed-reference risk).
		_fp_bg = bg
		_fp_scan_pulse(content_size, bg_scale)
	# Subtle vignette over the bg so the navigation strip + overlays
	# read cleanly against any painting.
	var vignette := ColorRect.new()
	vignette.name = "fp_vignette"
	vignette.color = Color(0, 0, 0, 0.25)
	vignette.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	vignette.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_board_content.add_child(vignette)
	# Top label — what space the player is at, plus its flavor.
	var space_def: Dictionary = _space_def(_player_pos)
	var label_panel := PanelContainer.new()
	label_panel.name = "fp_title_panel"
	label_panel.add_theme_stylebox_override("panel", _make_panel_style())
	label_panel.set_anchors_preset(Control.PRESET_TOP_WIDE)
	label_panel.offset_top = 6
	label_panel.offset_left = 8
	label_panel.offset_right = -8
	label_panel.offset_bottom = 38
	label_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_board_content.add_child(label_panel)
	var label_hb := HBoxContainer.new()
	label_hb.add_theme_constant_override("separation", 10)
	label_hb.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label_panel.add_child(label_hb)
	var at_lbl := Label.new()
	at_lbl.text = "» AT  " + String(space_def.get("label", _player_pos.to_upper()))
	at_lbl.add_theme_color_override("font_color", C_ACCENT)
	at_lbl.add_theme_font_size_override("font_size", 12)
	at_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label_hb.add_child(at_lbl)
	var flavor_s: String = String(space_def.get("flavor", ""))
	if flavor_s != "":
		var flavor_lbl := Label.new()
		flavor_lbl.text = "— " + flavor_s
		flavor_lbl.add_theme_color_override("font_color", Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.7))
		flavor_lbl.add_theme_font_size_override("font_size", 12)
		flavor_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		flavor_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
		label_hb.add_child(flavor_lbl)
	# Right-edge visitors+threats overlay — show who's here with you.
	var here_panel := VBoxContainer.new()
	here_panel.name = "fp_here_panel"
	here_panel.add_theme_constant_override("separation", 4)
	here_panel.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	here_panel.offset_left = -180
	here_panel.offset_right = -10
	here_panel.offset_top = 46
	here_panel.offset_bottom = -100
	here_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_board_content.add_child(here_panel)
	var here_header := Label.new()
	here_header.text = "AT THIS SPACE"
	here_header.add_theme_color_override("font_color", Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.55))
	here_header.add_theme_font_size_override("font_size", 12)
	here_panel.add_child(here_header)
	var any_here: bool = false
	for vid in _visitors_state:
		var v: Dictionary = _visitors_state[vid]
		if not v.get("arrived", false): continue
		if v.get("pos", "") != _player_pos: continue
		any_here = true
		var vdef: Dictionary = _visitors_def.get(vid, {})
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 4)
		row.mouse_filter = Control.MOUSE_FILTER_STOP
		row.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
		row.gui_input.connect(func(ev: InputEvent) -> void:
			if ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed:
				_open_visitor_view(vid))
		var dot := Label.new()
		dot.text = "●"
		dot.add_theme_color_override("font_color", Color(vdef.get("accent", "#c8a268")))
		dot.add_theme_font_size_override("font_size", 14)
		dot.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_child(dot)
		var vlbl := Label.new()
		vlbl.text = String(vdef.get("name", vid))
		vlbl.add_theme_color_override("font_color", C_TEXT)
		vlbl.add_theme_font_size_override("font_size", 12)
		vlbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_child(vlbl)
		here_panel.add_child(row)
	for inst: Dictionary in _threats_active:
		if String(inst.get("pos", "")) != _player_pos: continue
		any_here = true
		var tdef: Dictionary = _threats_def.get(inst.get("def_id", ""), {})
		var trow := HBoxContainer.new()
		trow.add_theme_constant_override("separation", 4)
		trow.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var tglyph := Label.new()
		tglyph.text = String(tdef.get("glyph", "✕"))
		tglyph.add_theme_color_override("font_color", Color(tdef.get("tint", "#ff8060")))
		tglyph.add_theme_font_size_override("font_size", 14)
		trow.add_child(tglyph)
		var ticks: int = int(inst.get("ticks_remaining", 0))
		var tlbl := Label.new()
		tlbl.text = "%s (%d)" % [String(tdef.get("title", "threat")), ticks]
		tlbl.add_theme_color_override("font_color", Color(1.0, 0.50, 0.39))
		tlbl.add_theme_font_size_override("font_size", 12)
		trow.add_child(tlbl)
		here_panel.add_child(trow)
	if not any_here:
		var empty_lbl := Label.new()
		empty_lbl.text = "— nobody here —"
		empty_lbl.add_theme_color_override("font_color", Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.35))
		empty_lbl.add_theme_font_size_override("font_size", 12)
		here_panel.add_child(empty_lbl)
	# Bottom navigation bar — adjacent spaces, click → walk.
	var nav_panel := PanelContainer.new()
	nav_panel.name = "fp_nav_panel"
	nav_panel.add_theme_stylebox_override("panel", _make_panel_style())
	nav_panel.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	nav_panel.offset_top = -68
	nav_panel.offset_left = 8
	nav_panel.offset_right = -8
	nav_panel.offset_bottom = -6
	nav_panel.mouse_filter = Control.MOUSE_FILTER_STOP
	_board_content.add_child(nav_panel)
	var nav_vb := VBoxContainer.new()
	nav_vb.add_theme_constant_override("separation", 2)
	nav_panel.add_child(nav_vb)
	var nav_header := Label.new()
	nav_header.text = "WALK TO  (click an adjacent space)"
	nav_header.add_theme_color_override("font_color", Color(C_ACCENT.r, C_ACCENT.g, C_ACCENT.b, 0.75))
	nav_header.add_theme_font_size_override("font_size", 12)
	nav_vb.add_child(nav_header)
	var nav_hb := HBoxContainer.new()
	nav_hb.add_theme_constant_override("separation", 6)
	nav_vb.add_child(nav_hb)
	var adj_map: Dictionary = _location.get("adjacency", {})
	var adj_list: Array = adj_map.get(_player_pos, [])
	for nbr_id: String in adj_list:
		var nbr_def: Dictionary = _space_def(nbr_id)
		if nbr_def.is_empty(): continue
		# Skip hidden thresholds (precipice_door before reveal)
		if not nbr_def.get("always_visible", true) and nbr_id != "precipice_door":
			continue
		if nbr_id == "precipice_door" and not _flags.get("precipice_revealed", false):
			continue
		var nbr_btn := Button.new()
		nbr_btn.text = String(nbr_def.get("label", nbr_id.to_upper()))
		nbr_btn.add_theme_font_size_override("font_size", 12)
		nbr_btn.tooltip_text = "Walk to %s (1 Time)" % nbr_btn.text
		nbr_btn.custom_minimum_size = Vector2(96, 28)
		nbr_btn.mouse_filter = Control.MOUSE_FILTER_STOP
		# Style threshold spaces in green so they read as "exits".
		var kind_s: String = String(nbr_def.get("kind", "named"))
		if kind_s == "threshold":
			nbr_btn.add_theme_color_override("font_color", C_GOOD)
		elif kind_s == "search":
			nbr_btn.add_theme_color_override("font_color", C_ACCENT)
		nbr_btn.pressed.connect(_on_space_clicked.bind(nbr_id))
		nav_hb.add_child(nbr_btn)
	# Hide the persistent player/visitor/threat meeples in FP mode —
	# the player IS the camera, and the visitor+threat overlay above
	# replaces meeple-at-marker display.
	if _board_meeple != null and is_instance_valid(_board_meeple):
		_board_meeple.visible = false
	for vid in _board_visitor_nodes.keys():
		var vn: Control = _board_visitor_nodes[vid]
		if is_instance_valid(vn):
			vn.visible = false
	for tid in _board_threat_nodes.keys():
		var tn: Control = _board_threat_nodes[tid]
		if is_instance_valid(tn):
			tn.visible = false


# Soft, slow scan-pan of the 1st-person painted view. Reads
# `_fp_bg` (set by _render_fp) instead of capturing a TextureRect
# in a lambda — the previous implementation captured the bg in a
# recursive tween_callback lambda, and when the bg got freed
# (render_fp rebuild, view-mode flip, player movement) Godot
# logged "Lambda capture at index 0 was freed" once per pulse.
# `.bind()` carries only Vector2 + float by value; no node refs.
func _fp_scan_pulse(content_size: Vector2, bg_scale: float) -> void:
	# Kill any in-flight scan tween before starting a new one. A
	# previous render's tween may still be ticking even though we
	# nulled _fp_bg; killing here prevents it from writing into a
	# freed node next frame.
	if _fp_scan_tween != null and _fp_scan_tween.is_valid():
		_fp_scan_tween.kill()
	_fp_scan_tween = null
	if _fp_bg == null or not is_instance_valid(_fp_bg):
		return
	# Slack we can move within without showing empty edges.
	var slack: Vector2 = content_size * (bg_scale - 1.0)
	# Random direction with weighted center returns.
	var dirs: Array = [
		Vector2(-1, 0), Vector2(1, 0), Vector2(0, -1), Vector2(0, 1),
		Vector2(-1, -1), Vector2(1, 1), Vector2(-1, 1), Vector2(1, -1),
		Vector2(0, 0), Vector2(0, 0),
	]
	var dir: Vector2 = dirs[randi() % dirs.size()]
	var mag: float = randf_range(0.40, 1.00)
	var target_offset: Vector2 = Vector2(
		-slack.x * 0.5 + dir.x * slack.x * 0.5 * mag,
		-slack.y * 0.5 + dir.y * slack.y * 0.5 * mag)
	var dur: float = randf_range(4.0, 7.0)
	var hold: float = randf_range(1.5, 3.0)
	_fp_scan_tween = create_tween()
	_fp_scan_tween.tween_property(_fp_bg, "position", target_offset, dur).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	_fp_scan_tween.tween_interval(hold)
	# .bind() — Callable carries content_size + bg_scale by value,
	# no lambda capture. _fp_scan_pulse re-reads _fp_bg from the
	# class member each pulse, so a render swap is observed cleanly.
	_fp_scan_tween.tween_callback(_fp_scan_pulse.bind(content_size, bg_scale))


# Log a small atmospheric beat when the player arrives at a new
# space. The space's def can carry an `arrival_lines` array; we
# pick one at random. Cheap, high-impact for texture — every
# move now reads as a moment in the room.
func _log_arrival_beat_if_changed() -> void:
	if _player_pos == _last_logged_pos:
		return
	_last_logged_pos = _player_pos
	var sd: Dictionary = _space_def(_player_pos)
	var arrivals: Array = sd.get("arrival_lines", [])
	if arrivals.is_empty():
		return
	var line: String = String(arrivals[randi() % arrivals.size()])
	_log_line("[color=#7c8398][i]%s[/i][/color]" % line)


# Steamboat ladder: a unique beat at each completion-progress
# level, fired only once per state crossing. Pulled from the
# location's `steamboat.ladder` array (index 0 = bare hull, last
# = finished). Falls through silently if the location doesn't
# declare a ladder.
func _log_steamboat_beat_if_changed() -> void:
	if _steamboat_progress == _last_steamboat_beat:
		return
	_last_steamboat_beat = _steamboat_progress
	var sb_def: Dictionary = _location.get("steamboat", {})
	var ladder: Array = sb_def.get("ladder", [])
	if _steamboat_progress < 0 or _steamboat_progress >= ladder.size():
		return
	_log_line("[color=#ff8060][i]%s[/i][/color]" % String(ladder[_steamboat_progress]))


# Once-per-N-turns ambient line drawn from the scenario's
# `ambient_pool`. The first run-time offset is randomised so the
# cycle doesn't always land on the same turn numbers.
func _log_ambient_beat_if_due() -> void:
	# Combined pool: base scenario ambient + cross-arcana world-state
	# ambient (sinkhole etc.). Empty merged-pool short-circuits.
	var base_pool: Array = _setup.get("ambient_pool", [])
	var combined_pool: Array = base_pool.duplicate()
	for w in _world_state_ambient_lines:
		combined_pool.append(w)
	if combined_pool.is_empty():
		return
	# Default every 3 turns; setup can override via ambient_every_n.
	var n: int = int(_setup.get("ambient_every_n", 3))
	if n < 1: n = 1
	if ((_turn + _ambient_turn_offset) % n) != 0:
		return
	var line: String = String(combined_pool[randi() % combined_pool.size()])
	_log_line("[color=#7c8398][i]%s[/i][/color]" % line)


# Per-active-demon ambient line, fired once per Upkeep. Reads the
# demon's `ambient_lines` from its action-card def. Lets the
# demons feel like they're actually doing things between plays.
func _log_demon_ambient_beats() -> void:
	if _active_demons.is_empty():
		return
	for did in _active_demons.keys():
		var card_id: String = "demon_" + String(did)
		var cdef: Dictionary = _action_cards.get(card_id, {})
		var lines: Array = cdef.get("ambient_lines", [])
		if lines.is_empty():
			continue
		var line: String = String(lines[randi() % lines.size()])
		_log_line("[color=#c8a268][i]%s[/i][/color]" % line)


# Stagnation / doubt tier crossings — surface the new label as a
# log line when the player's stagnation/doubt enters a new tier.
# Tier definitions live in the setup JSON. Quiet when stats don't
# move; loud when they do.
func _log_pressure_tier_crossings() -> void:
	var st_tiers: Array = _setup.get("stagnation_thresholds", [])
	if not st_tiers.is_empty():
		var cur_tier: int = -1
		for i in st_tiers.size():
			if _stagnation >= int((st_tiers[i] as Dictionary).get("level", 0)):
				cur_tier = i
		if cur_tier != _last_stagnation_tier and cur_tier >= 0:
			_last_stagnation_tier = cur_tier
			var label: String = String((st_tiers[cur_tier] as Dictionary).get("label", ""))
			if label != "":
				_log_line("[color=#ff8060][b]» %s[/b][/color]" % label)
	var d_tiers: Array = _setup.get("doubt_thresholds", [])
	if not d_tiers.is_empty():
		var cur_d: int = -1
		for i in d_tiers.size():
			if _doubt >= int((d_tiers[i] as Dictionary).get("level", 0)):
				cur_d = i
		if cur_d != _last_doubt_tier and cur_d >= 0:
			_last_doubt_tier = cur_d
			var label_d: String = String((d_tiers[cur_d] as Dictionary).get("label", ""))
			if label_d != "":
				_log_line("[color=#ff8060][b]» %s[/b][/color]" % label_d)


func _space_def(sid: String) -> Dictionary:
	# Returns the space definition with hand_overrides applied if the
	# location specifies any for the current _hand_id. This is how
	# guest-lens scenarios work: the same board geometry, different
	# space labels / flavor / arrival_lines depending on who's playing.
	# Example: dantes_office space "desk" labeled "DESK" by default,
	# but "BOSS'S DESK" when _hand_id == "john_frank".
	for s: Dictionary in _location.get("spaces", []):
		if String(s.get("id", "")) == sid:
			var overrides: Dictionary = _location.get("hand_overrides", {}) as Dictionary
			var per_hand: Dictionary = overrides.get(_hand_id, {}) as Dictionary
			var per_space: Dictionary = per_hand.get(sid, {}) as Dictionary
			if per_space.is_empty():
				return s
			var merged: Dictionary = s.duplicate(true)
			for k in per_space.keys():
				merged[k] = per_space[k]
			return merged
	return {}


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
	# Every space gets its full label now — user feedback: "the map
	# also needs more labels for locations." Tier the prominence by
	# relevance: current pos > adjacent > thresholds/search > other.
	if is_here:
		l.text = "» " + label + pile
		col = C_ACCENT
		fs = 12
	elif is_adjacent:
		l.text = label + pile
		col = C_TEXT
		fs = 10
	elif kind == "threshold":
		l.text = label
		col = Color(0.55, 0.95, 0.65, 0.78)
		fs = 9
	elif kind == "search":
		l.text = label + pile
		col = Color(0.95, 0.78, 0.40, 0.78)
		fs = 9
	else:
		# Show the full label too, just dim.
		l.text = label
		col = Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.55)
		fs = 9
	# Scale the chosen font size by the board's UI scale so labels
	# stay readable at any panel size (small in normal view, larger
	# in fullscreen).
	fs = int(max(8, round(fs * _board_ui_scale)))
	l.add_theme_color_override("font_color", col)
	l.add_theme_font_size_override("font_size", fs)
	# Outline + slight shadow so labels read over any painted background.
	l.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	l.add_theme_constant_override("outline_size", int(max(2, 4.0 * _board_ui_scale)))
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
	# the right column + bottom strip) AND switch to the top-down
	# map view. Normal mode is 1st-person of the current space.
	# Click again or hit Esc to restore the FP view in its panel.
	_board_fullscreen = not _board_fullscreen
	_view_mode = "map" if _board_fullscreen else "fp"
	if _board_fullscreen:
		_board_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		_board_root.offset_top = 52
		_board_root.offset_left = 8
		_board_root.offset_right = -8
		_board_root.offset_bottom = -8
		# Hide the in-header expand button while fullscreen — the
		# viewport-level overlay exit button is the working one.
		_board_expand_btn.visible = false
		_board_root.z_index = 10
	else:
		# Restore uses PRESET_FULL_RECT (same as the initial setup) —
		# PRESET_LEFT_WIDE anchors BOTH edges to the parent's LEFT
		# edge and produces a negative-width rect when offset_right
		# is negative, which is what was freezing the board.
		_board_root.set_anchors_preset(Control.PRESET_FULL_RECT)
		_board_root.offset_top = 52
		_board_root.offset_left = 8
		_board_root.offset_bottom = -346
		_board_root.offset_right = -440
		_board_expand_btn.visible = true
		_board_expand_btn.text = "⛶"
		_board_expand_btn.tooltip_text = "Open the top-down MAP (fullscreen). 1st-person of the current space is the default normal view."
		_board_expand_btn.custom_minimum_size = Vector2(28, 20)
		_board_root.z_index = 0
	# Show/hide the viewport-level exit button (the working one)
	if _board_fullscreen_exit_btn != null:
		_board_fullscreen_exit_btn.visible = _board_fullscreen
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
			var prev_pos2: String = _player_pos
			_player_pos = String(keys[idx])
			_places_visited[_player_pos] = true
			_audio_sfx("card_play")
			_log_line("→ %s to [b]%s[/b]" % [reason, _player_pos])
			_faith_follow(prev_pos2)
			_check_composite_connections()
			_check_togo_deliveries()
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
	# Costs 1 Time, no card consumed. Inertia 10+ adds +1 to step
	# onto threshold spaces (the door looks farther).
	var walk_cost: int = 1
	if _inertia >= 10 and _is_threshold(target_pos):
		walk_cost = 2
	if _time < walk_cost:
		_log_line("[i]not enough Time to walk (need %d)[/i]" % walk_cost)
		return
	_time -= walk_cost
	if walk_cost > 1:
		_log_line("[color=#ff8060][i]the door looks farther: walk to %s costs %d[/i][/color]" % [target_pos, walk_cost])
	var prev_pos: String = _player_pos
	_player_pos = target_pos
	_places_visited[_player_pos] = true
	_faith_follow(prev_pos)
	_audio_sfx("card_play")
	_log_line("→ walked to [b]%s[/b]" % target_pos)
	_check_composite_connections()
	_check_togo_deliveries()
	_render()


func _position_meeples() -> void:
	# Meeples should SIT ON their stations, not drift down toward
	# neighboring rows. Player centers on the marker (overlapping
	# the disc); visitors stack TIGHTLY to the right of the marker.
	if _board_meeple and _board_marker_pos.has(_player_pos):
		var mc: Vector2 = _board_marker_pos[_player_pos]
		var mp_size: Vector2 = _board_meeple.size if _board_meeple.size.x > 0 else Vector2(28, 28) * _board_ui_scale
		# Center the player meeple on the marker.
		var target: Vector2 = mc - mp_size * 0.5
		_tween_node_to(_board_meeple, target, 0.32)
	# Visitors: small right-of-marker stack so they cluster with
	# their station instead of drifting down toward the next row.
	var vid_pos_stack: Dictionary = {}
	for vid in _board_visitor_nodes:
		var v: Dictionary = _visitors_state[vid]
		var p: String = v.get("pos", "")
		if _board_marker_pos.has(p):
			var mc2: Vector2 = _board_marker_pos[p]
			var node: Control = _board_visitor_nodes[vid]
			var ns: Vector2 = node.size if node.size.x > 0 else Vector2(22, 22) * _board_ui_scale
			var idx: int = int(vid_pos_stack.get(p, 0))
			vid_pos_stack[p] = idx + 1
			# Right of marker, slightly above center; small per-
			# visitor offset to fan them out without going far.
			var dx: float = (8.0 * _board_ui_scale) + idx * (ns.x * 0.6)
			var dy: float = -ns.y * 0.5
			var vtarget: Vector2 = mc2 + Vector2(dx, dy)
			_tween_node_to(node, vtarget, 0.36)
	# Threats: stack to the LEFT of the marker so they read as the
	# bad twin of the visitor cluster on the right.
	var threat_pos_stack: Dictionary = {}
	for inst: Dictionary in _threats_active:
		var tid: String = String(inst.get("id", ""))
		if not _board_threat_nodes.has(tid):
			continue
		var tpos: String = String(inst.get("pos", ""))
		if not _board_marker_pos.has(tpos):
			continue
		var tnode: Control = _board_threat_nodes[tid]
		var tns: Vector2 = tnode.size if tnode.size.x > 0 else Vector2(18, 18) * _board_ui_scale
		var tidx: int = int(threat_pos_stack.get(tpos, 0))
		threat_pos_stack[tpos] = tidx + 1
		var tdx: float = -(8.0 * _board_ui_scale) - tns.x - tidx * (tns.x * 0.6)
		var tdy: float = -tns.y * 0.5
		var ttarget: Vector2 = _board_marker_pos[tpos] + Vector2(tdx, tdy)
		_tween_node_to(tnode, ttarget, 0.36)


# ── Hand + visitor rendering ─────────────────────────────────────────

func _render_hand() -> void:
	for c in _hand_box.get_children():
		c.queue_free()
	for cid in _hand_cards:
		var card: Dictionary = _action_cards.get(cid, {})
		var time_cost: int = int(card.get("time_cost", 1))
		# Card tile = VBox of icon-button on top + autowrap title
		# label below. Title is fully readable; art still pops.
		var tile := VBoxContainer.new()
		tile.add_theme_constant_override("separation", 2)
		var btn := Button.new()
		btn.custom_minimum_size = Vector2(108, 108)
		var playable: bool = _can_play_card(card)
		var is_disabled: bool = (not playable) or (_phase != Phase.ACTION) or _game_over
		# Tooltip leads with a "why not" line when the card is
		# disabled, so the player isn't left guessing.
		var why_blocked: String = ""
		if is_disabled:
			if _phase != Phase.ACTION:
				why_blocked = "(Action phase only — currently %s)" % Phase.keys()[_phase]
			elif _time < time_cost:
				why_blocked = "(needs %d Time; you have %d)" % [time_cost, _time]
			elif not playable:
				why_blocked = "(requirements not met — see effect summary)"
		btn.tooltip_text = "%s — costs %d Time%s\n\n%s\n\n%s\n\n(Click to preview + play.)" % [
			card.get("title", cid), time_cost,
			("\n" + why_blocked) if why_blocked != "" else "",
			String(card.get("flavor", "")),
			_card_summary(card)]
		var art: Texture2D = _load_texture_silent(_art_path_card(cid))
		if art == null:
			# Procedural face until the studio generates real art.
			art = CARD_FACE.face(cid, card, _arcana_id)
		if art:
			btn.icon = art
			btn.expand_icon = true
		btn.disabled = is_disabled
		btn.pressed.connect(func() -> void:
			_pulse_button(btn)
			_open_card_view(cid, "play"))
		btn.mouse_entered.connect(_hover_scale.bind(btn, true))
		btn.mouse_exited.connect(_hover_scale.bind(btn, false))
		tile.add_child(btn)
		var title_lbl := Label.new()
		title_lbl.text = "%s · %dt" % [card.get("title", cid), time_cost]
		title_lbl.add_theme_font_size_override("font_size", 12)
		title_lbl.add_theme_color_override("font_color", C_TEXT)
		title_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		title_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		title_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		title_lbl.custom_minimum_size = Vector2(108, 34)
		title_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
		# Grey title out if card isn't playable
		if not playable or _phase != Phase.ACTION or _game_over:
			title_lbl.add_theme_color_override("font_color", Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.45))
		tile.add_child(title_lbl)
		_hand_box.add_child(tile)


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
		if int(_tableau_stock.get(cid, 0)) <= 0:
			continue   # out of stock — purchased out this run
		buyables.append(cid)
	buyables.sort_custom(func(a: String, b: String) -> bool:
		return int(_action_cards[a].get("time_cost", 1)) < int(_action_cards[b].get("time_cost", 1)))

	for cid: String in buyables:
		var card: Dictionary = _action_cards[cid]
		var time_cost: int = int(card.get("time_cost", 1))
		var price: int = _buy_price(card)
		var tile := VBoxContainer.new()
		tile.add_theme_constant_override("separation", 2)
		var btn := Button.new()
		btn.custom_minimum_size = Vector2(108, 108)
		var can_buy: bool = (_phase == Phase.PLANNING) and (_time >= price) and not _game_over
		var why_blocked: String = ""
		if not can_buy:
			if _phase != Phase.PLANNING:
				why_blocked = "(Planning phase only — currently %s)" % Phase.keys()[_phase]
			elif _time < price:
				why_blocked = "(needs %d Time; you have %d)" % [price, _time]
		btn.tooltip_text = "%s — buy %d Time, play %d Time%s\n\n%s\n\n%s\n\n(Click to preview + buy.)" % [
			card.get("title", cid), price, time_cost,
			("\n" + why_blocked) if why_blocked != "" else "",
			String(card.get("flavor", "")),
			_card_summary(card)]
		var art: Texture2D = _load_texture_silent(_art_path_card(cid))
		if art == null:
			art = CARD_FACE.face(cid, card, _arcana_id)
		if art:
			btn.icon = art
			btn.expand_icon = true
		btn.disabled = not can_buy
		if _phase != Phase.PLANNING:
			btn.modulate = Color(0.7, 0.65, 0.55, 0.7)
		btn.pressed.connect(func() -> void:
			_pulse_button(btn)
			_open_card_view(cid, "buy"))
		btn.mouse_entered.connect(_hover_scale.bind(btn, true))
		btn.mouse_exited.connect(_hover_scale.bind(btn, false))
		tile.add_child(btn)
		var title_lbl := Label.new()
		var stock_n: int = int(_tableau_stock.get(cid, 0))
		var exp_prefix: String = "[exp] " if card.get("experimental", false) else ""
		title_lbl.text = "%s%s · buy %dt · ×%d" % [exp_prefix, card.get("title", cid), price, stock_n]
		title_lbl.add_theme_font_size_override("font_size", 12)
		title_lbl.add_theme_color_override("font_color", C_TEXT)
		title_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		title_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		title_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		title_lbl.custom_minimum_size = Vector2(108, 34)
		title_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
		if not can_buy:
			title_lbl.add_theme_color_override("font_color", Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.45))
		tile.add_child(title_lbl)
		_tableau_box.add_child(tile)


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
	if int(_tableau_stock.get(cid, 0)) <= 0:
		_log_line("[i]no %s left in the tableau[/i]" % card.get("title", cid))
		return
	_time -= price
	_hand_cards.append(cid)
	_tableau_stock[cid] = int(_tableau_stock[cid]) - 1
	_audio_sfx("card_play")
	var remaining: int = int(_tableau_stock[cid])
	if remaining > 0:
		_log_line("[color=#7cffb0]✦ bought [b]%s[/b][/color]  (cost %d, Time %d → %d, %d left in tableau)" %
			[card.get("title", cid), price, _time + price, _time, remaining])
	else:
		_log_line("[color=#7cffb0]✦ bought [b]%s[/b][/color]  (cost %d, Time %d → %d, [i]last copy[/i])" %
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
		"recover_sanity": return "+%d Sanity" % int(e.get("amount", 1))
		"lose_sanity":    return "-%d Sanity" % int(e.get("amount", 1))
		"spawn_threat":
			var tdef_lbl: Dictionary = _threats_def.get(String(e.get("threat_id", "")), {})
			return "Spawn threat: %s" % String(tdef_lbl.get("title", e.get("threat_id", "?")))
		"clear_threats_here": return "Clear any threat at your space"
		"clear_all_threats":  return "Clear EVERY threat on the board"
		"force_connect_visitor_at_my_pos": return "Connect any visitor at your space (bypasses progress + composite paths)"
		"disperse_visitors_here":          return "Push every visitor at your space to a random adjacent space"
		"gain_stagnation": return "+%d Stagnation" % int(e.get("amount", 1))
		"lose_stagnation": return "-%d Stagnation" % int(e.get("amount", 1))
		"gain_doubt":      return "+%d Doubt" % int(e.get("amount", 1))
		"lose_doubt":      return "-%d Doubt" % int(e.get("amount", 1))
		"gain_inspiration":return "+%d Inspiration" % int(e.get("amount", 1))
		"lose_inspiration":return "-%d Inspiration" % int(e.get("amount", 1))
		"spend_inspiration":return "-%d Inspiration (spent)" % int(e.get("amount", 1))
		"advance_piece_at_my_pos": return "Advance the piece at your space by %d" % int(e.get("amount", 1))
		"unfinish_piece":  return "Unfinish a piece by %d" % int(e.get("amount", 1))
		"unfinish_random_piece":          return "A random piece loses 1 progress"
		"unfinish_random_finished_arcana":return "A finished arcana de-finishes"
		"advance_steamboat":              return "Advance the steamboat by %d" % int(e.get("amount", 1))
		"steamboat_threshold_minus":      return "Steamboat completion threshold -%d" % int(e.get("amount", 1))
		"advance_wip":     return "Advance %s WIP by %d" % [String(e.get("wip", "?")), int(e.get("amount", 1))]
		"unlock_one_sealed_arcana":       return "Unlock one sealed arcana"
		"cancel_next_gravity":            return "Cancel the next Gravity card"
		"peek_gravity_top":               return "Peek next %d gravity cards%s" % [int(e.get("n", 3)), (" + rearrange" if e.get("rearrange", false) else "")]
		"set_cross_arcana_flag":          return "Set flag %s in %s" % [String(e.get("key", "?")), String(e.get("target", "?"))]
		"summon_demon":                   return "Summon demon %s for %d turns" % [String(e.get("id", "?")), int(e.get("duration_turns", 3))]
		"lock_threshold_open":            return "Lock %s open for %d turns" % [String(e.get("threshold", "?")), int(e.get("turns", 3))]
		"mark_space":                     return "Mark %s = %s" % [String(e.get("pos", "player_pos")), String(e.get("key", "?"))]
		"consume_inventory_for_contents":return "Consume %d items → contents" % int(e.get("amount", 3))
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
	lines.append("Time %d  ·  Inertia %d  ·  Sanity %d" % [_time, _inertia, _sanity])
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
	if v.has("mood"):
		lines.append("mood: " + String(v.get("mood", "")))
	if st.get("connected", false):
		lines.append("✓ connected")
		if v.has("lore_text"):
			lines.append(String(v.get("lore_text", "")))
	elif st.get("claimed_turn", -1) >= 0:
		var remaining: int = int(_setup.get("claim_turns_to_consume", 2)) - (_turn - int(st["claimed_turn"]))
		lines.append("✕ claimed — %d turn(s) until consumed" % max(0, remaining))
	elif st.get("arrived", false):
		lines.append("at " + String(st.get("pos", "?")).replace("_", " "))
		# Waiter-sequence progress bar
		var p: int = int(st.get("progress", 0))
		var labels: PackedStringArray = ["GREET", "LISTEN", "DELIVER", "SIT WITH"]
		var marks: PackedStringArray = []
		for i in labels.size():
			var prefix: String = "✓ " if p > i else ("→ " if p == i else "  ")
			marks.append(prefix + labels[i])
		lines.append("Sequence: " + "  ".join(marks))
	# Special connect path (composite / card_played_n_times / etc.)
	var cv: Dictionary = v.get("connect_via", {})
	if not cv.is_empty() and not st.get("connected", false):
		lines.append("(or: " + _describe_connect_via_plain(cv) + ")")
	if v.has("tutorial_note"):
		lines.append("[hint] " + String(v.get("tutorial_note", "")))
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
	# Slim summary into the right-column bar. Full detail lives in the
	# ⛶ modal (see _build_inventory_modal_body).
	if _inv_summary_label == null:
		return
	if _bindle_assembled:
		_inv_summary_label.text = "[color=#ffd07a][b]BINDLE assembled[/b][/color] · %d item(s) carried · click ⛶ for details" % _inventory.size()
		return
	var have_stick: bool = _inventory.has("stick")
	var have_cloth: bool = _inventory.has("cloth")
	var have_contents: bool = _has_contents()
	var stick_chip: String = "[color=#7cffb0]✓ stick[/color]" if have_stick else "[color=#7c8398]· stick[/color]"
	var cloth_chip: String = "[color=#7cffb0]✓ cloth[/color]" if have_cloth else "[color=#7c8398]· cloth[/color]"
	var content_chip: String = "[color=#7cffb0]✓ contents[/color]" if have_contents else "[color=#7c8398]· contents[/color]"
	# Count non-bindle items
	var extra_count: int = 0
	for it in _inventory:
		var cat: String = String(_items_def.get(it, {}).get("category", ""))
		if cat != "bindle_component" and cat != "bindle_contents":
			extra_count += 1
	var extras: String = ""
	if extra_count > 0:
		extras = "  ·  [color=#c8a268]%d carried[/color]" % extra_count
	_inv_summary_label.text = "[b]BINDLE:[/b]  %s   %s   %s%s" % [stick_chip, cloth_chip, content_chip, extras]


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

		# Row = the HBoxContainer itself, with mouse_filter STOP so it
		# captures clicks. Children are mouse_filter IGNORE so they
		# don't intercept. (Button-as-wrapper broke layout — Button
		# isn't a Container and the HBox child got 0 size.)
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 6)
		row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.mouse_filter = Control.MOUSE_FILTER_STOP
		row.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
		row.tooltip_text = _tooltip_for_visitor(vid) + "\n\n(Click for full card view.)"
		row.gui_input.connect(func(ev: InputEvent) -> void:
			if ev is InputEventMouseButton:
				var mb := ev as InputEventMouseButton
				if mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT:
					_open_visitor_view(vid))
		if arrived:
			var face: Texture2D = _load_texture_silent(_art_path_visitor_face(vid))
			if face:
				var face_rect := TextureRect.new()
				face_rect.texture = face
				face_rect.custom_minimum_size = Vector2(40, 40)
				face_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
				face_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
				face_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
				row.add_child(face_rect)
			else:
				# Colored dot placeholder so the row reads as portrait-led
				var dot := Label.new()
				dot.text = "●"
				dot.add_theme_color_override("font_color", Color(accent))
				dot.add_theme_font_size_override("font_size", 22)
				dot.mouse_filter = Control.MOUSE_FILTER_IGNORE
				row.add_child(dot)
		var rt := RichTextLabel.new()
		rt.bbcode_enabled = true
		rt.fit_content = true
		rt.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		rt.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		rt.add_theme_color_override("default_color", C_TEXT)
		rt.add_theme_font_size_override("normal_font_size", 12)
		rt.mouse_filter = Control.MOUSE_FILTER_IGNORE
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
			item.add_theme_font_size_override("normal_font_size", 12)
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
	llr.add_theme_font_size_override("normal_font_size", 12)
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
		rt.add_theme_font_size_override("normal_font_size", 12)
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
	var max_turns_ui: int = int(_setup.get("max_turns", 14))
	_turn_label.text  = "Turn %d / %d" % [_turn, max_turns_ui]
	_time_label.text  = "Time %d / %d" % [_time, _next_time_reset]
	_inertia_label.text = "Inertia %d / 12" % _inertia
	_sanity_label.text  = "Sanity %d" % _sanity
	# Major-arcana per-hand stats. Stagnation + Doubt are shared across
	# Magician / Priestess / Empress (all three feel the room sour and
	# the keeper / listener / maker doubt). The third slot is per-arcana:
	#   · Magician — Inspiration
	#   · Priestess — Insight + master Reel readout
	#   · Empress — Harvest + Bloom readout (Bloom is the POSITIVE
	#     doom-clock; Harvest is the spendable currency)
	# Pieces is Magician-only.
	var is_magician: bool = (_arcana_id == "magician")
	var is_priestess: bool = (_arcana_id == "priestess")
	var is_empress: bool = (_arcana_id == "empress")
	var is_emperor: bool = (_arcana_id == "emperor")
	var is_hierophant: bool = (_arcana_id == "hierophant")
	var is_lovers: bool = (_arcana_id == "lovers")
	var is_chariot: bool = (_arcana_id == "chariot")
	var is_major_arcana: bool = is_magician or is_priestess or is_empress or is_emperor or is_hierophant or is_lovers or is_chariot
	if _stagnation_label != null:
		_stagnation_label.visible = is_major_arcana
		if is_major_arcana:
			var s_max: int = int(_setup.get("loss_conditions", {}).get("stagnation_max", 12))
			_stagnation_label.text = "Stagnation %d / %d" % [_stagnation, s_max]
	if _doubt_label != null:
		_doubt_label.visible = is_major_arcana
		if is_major_arcana:
			_doubt_label.text = "Doubt %d / %d" % [_doubt, _doubt_max]
	if _inspiration_label != null:
		_inspiration_label.visible = is_major_arcana
		if is_magician:
			_inspiration_label.text = "Inspiration %d" % _inspiration
		elif is_priestess:
			_inspiration_label.text = "Insight %d  ·  Reel %d / %d" % [_insight, _master_reel, _master_reel_threshold]
		elif is_empress:
			_inspiration_label.text = "Harvest %d  ·  Bloom %d / %d" % [_harvest, _bloom, _bloom_threshold]
		elif is_emperor:
			_inspiration_label.text = "Authority %d  ·  Ledger %d / %d" % [_authority, _ledger, _ledger_threshold]
		elif is_hierophant:
			_inspiration_label.text = "Doctrine %d  ·  Signal %d / %d" % [_doctrine, _signal, _signal_threshold]
		elif is_lovers:
			_inspiration_label.text = "Verb %d  ·  Sync %d / %d" % [_verb, _sync, _sync_threshold]
		elif is_chariot:
			_inspiration_label.text = "Fuel %d  ·  Miles %d / %d" % [_fuel, _miles, _miles_threshold]
	if _pieces_label != null:
		_pieces_label.visible = is_magician
		if is_magician:
			_pieces_label.text = "Pieces %d" % _pieces_completed
	# Inertia + Sanity are Fool-only — hide for the other arcanas.
	if _inertia_label != null and is_major_arcana:
		_inertia_label.visible = false
	if _sanity_label != null and is_major_arcana:
		_sanity_label.visible = false
	# Push current pressure to the BGM audio manipulator — Stagnation
	# muffles the room, Doubt distorts it. Only applies to Magician
	# runs; the Fool's stats don't drive this surface.
	if is_magician and _audio_manipulator != null:
		var s_max_for_audio: float = float(_setup.get("loss_conditions", {}).get("stagnation_max", 12))
		var d_max_for_audio: float = float(_doubt_max)
		_audio_manipulator.update_stagnation(float(_stagnation) / max(1.0, s_max_for_audio))
		_audio_manipulator.update_doubt(float(_doubt) / max(1.0, d_max_for_audio))
	# Evocative tooltips driven by the current value — the player
	# hovers and gets the room's mood at that pressure level.
	_inertia_label.tooltip_text = _inertia_mood(_inertia)
	_sanity_label.tooltip_text = _sanity_mood(_sanity)
	_time_label.tooltip_text = "Time is your action budget for the turn. Unspent Time carries over into the next turn (Final Girl style)."
	_turn_label.tooltip_text = "Each turn cycles ACTION → PLANNING → SHADOW → DRIFT → UPKEEP."
	# Flash labels on change — green for gain, red for loss
	# (Inertia inverted: rising is bad, falling is good)
	if _last_rendered_time != -1 and _time != _last_rendered_time:
		_pulse_label(_time_label, Color(0.49, 1.0, 0.69) if _time > _last_rendered_time else Color(1.0, 0.50, 0.39))
	if _last_rendered_inertia != -1 and _inertia != _last_rendered_inertia:
		_pulse_label(_inertia_label, Color(0.49, 1.0, 0.69) if _inertia < _last_rendered_inertia else Color(1.0, 0.50, 0.39))
	if _last_rendered_sanity != -1 and _sanity != _last_rendered_sanity:
		_pulse_label(_sanity_label, Color(0.49, 1.0, 0.69) if _sanity > _last_rendered_sanity else Color(1.0, 0.50, 0.39))
	_last_rendered_time = _time
	_last_rendered_inertia = _inertia
	_last_rendered_sanity = _sanity
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
	# Defer the scroll-to-bottom one frame so RichTextLabel has
	# laid out the new line and its scroll bar's max_value is up
	# to date. scroll_following = true is meant to do this but
	# doesn't always fire on append_text — force it.
	call_deferred("_scroll_log_to_bottom")
	# Don't count the initial banner/setup lines as unread — only
	# count once the live UI is rendering.
	if _last_rendered_time != -1:
		_log_unread_count += 1
		_update_log_unread_badge()


func _scroll_log_to_bottom() -> void:
	if _log == null:
		return
	var vbar: VScrollBar = _log.get_v_scroll_bar()
	if vbar != null:
		vbar.value = vbar.max_value


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
		"visitor_at_my_pos":
			# True if any arrived, unconnected visitor shares my space
			for vid in _visitors_state:
				var st: Dictionary = _visitors_state[vid]
				if st.get("arrived", false) and not st.get("connected", false) and st.get("pos", "") == _player_pos:
					return true
			return false
		"visitor_at_my_pos_progress_at_least":
			# True if any arrived, unconnected visitor at my space has
			# progress >= n. Used by LISTEN / DELIVER / SIT WITH
			# requirement chain.
			var n: int = int(req.get("n", 1))
			for vid in _visitors_state:
				var st: Dictionary = _visitors_state[vid]
				if (st.get("arrived", false) and not st.get("connected", false)
						and st.get("pos", "") == _player_pos
						and int(st.get("progress", 0)) >= n):
					return true
			return false
		"inventory_has_order_for_visitor_at_my_pos":
			# True if any visitor at my pos has their order_item in
			# my inventory.
			for vid in _visitors_state:
				var st: Dictionary = _visitors_state[vid]
				if not st.get("arrived", false): continue
				if st.get("connected", false): continue
				if st.get("pos", "") != _player_pos: continue
				var ord_id: String = String(_visitors_def.get(vid, {}).get("order_item", ""))
				if ord_id != "" and _inventory.has(ord_id):
					return true
			return false
		"has_inspiration_at_least":
			# Magician — BUILD-style gate. The card is only playable
			# when the player has banked at least N inspiration. The
			# card's effect list typically spends_inspiration N on
			# resolve, so the predicate prevents partial spends.
			return _inspiration >= int(req.get("n", 1))
		"has_insight_at_least":
			# Priestess — TRANSCRIBE-style gate. Mirror of the Magician
			# predicate; uses _insight instead of _inspiration.
			return _insight >= int(req.get("n", 1))
		"has_stagnation_below":
			return _stagnation < int(req.get("n", 12))
		"has_doubt_below":
			return _doubt < int(req.get("n", 7))
		"has_master_reel_below":
			return _master_reel < int(req.get("n", 6))
		"has_bloom_at_least":
			return _bloom >= int(req.get("n", 1))
		"has_harvest_at_least":
			return _harvest >= int(req.get("n", 1))
		"has_authority_at_least":
			return _authority >= int(req.get("n", 1))
		"has_ledger_at_least":
			return _ledger >= int(req.get("n", 1))
		"has_doctrine_at_least":
			return _doctrine >= int(req.get("n", 1))
		"has_signal_at_least":
			return _signal >= int(req.get("n", 1))
		"has_verb_at_least":
			return _verb >= int(req.get("n", 1))
		"has_sync_at_least":
			return _sync >= int(req.get("n", 1))
		"has_fuel_at_least":
			return _fuel >= int(req.get("n", 1))
		"has_miles_at_least":
			return _miles >= int(req.get("n", 1))
		"partner_at_my_pos":
			# Lovers — true if the lovers_partner visitor is at the
			# player's current space. Used by all the duet-style cards.
			if _lovers_partner_id == "":
				return false
			var ps: Dictionary = _visitors_state.get(_lovers_partner_id, {})
			return String(ps.get("pos", "")) == _player_pos
		"visitor_in_bright_space":
			# MOTH-style. True if any arrived, unconnected visitor is
			# at one of the cathedral's "lit" stations. Bright = the
			# inner cluster (warm-lit pieces around the workbench) plus
			# the explicitly-illuminated outer-cluster stations.
			for vid in _visitors_state:
				var st: Dictionary = _visitors_state[vid]
				if not st.get("arrived", false): continue
				if st.get("connected", false): continue
				if _is_bright_space(String(st.get("pos", ""))):
					return true
			return false
	return true


func _step_index(step: String) -> int:
	# Progress encoding: greet=1, listen=2, deliver=3, sit_with=4
	match step:
		"greet":    return 1
		"listen":   return 2
		"deliver":  return 3
		"sit_with": return 4
	return 0


# Per-visitor (or per-mood fallback) flavor when a step lands.
# Visitor JSON's steps[step] takes priority; if missing, fall back
# to default_step_lines_by_mood[mood][step] from the visitors_def
# top-level.
func _log_visitor_step_line(vid: String, step: String) -> void:
	var v: Dictionary = _visitors_def.get(vid, {})
	var name_s: String = String(v.get("name", vid))
	# Pomegranate Hour subjects override the step verb in the UI.
	var verb_labels: Dictionary = v.get("verb_labels", {}) as Dictionary
	var display_step: String = String(verb_labels.get(step, step))
	var line: String = ""
	# Per-visitor line takes priority. Try internal step key first,
	# then the display verb (some JSONs key steps as see/voice/cut/lock).
	var steps_dict: Dictionary = v.get("steps", {})
	if steps_dict.has(step):
		line = String(steps_dict.get(step, ""))
	elif display_step != step and steps_dict.has(display_step):
		line = String(steps_dict.get(display_step, ""))
	if line == "":
		# Fall back to mood-default. _visitors_def is the
		# per-visitor dict; mood defaults are stored as a separate
		# top-level field on the JSON which the engine reads as
		# _step_defaults_by_mood.
		var mood: String = String(v.get("mood", "preoccupied"))
		var defaults: Dictionary = _step_defaults_by_mood.get(mood, {})
		line = String(defaults.get(step, ""))
	# Log a verbed-line header + the flavor underneath
	var verb_label: String = display_step.replace("_", " ").to_upper()
	_log_line("[color=#7cffb0]→ %s[/color] [b]%s[/b]" % [verb_label, name_s])
	if line != "":
		_log_line("[color=#7c8398][i]   %s[/i][/color]" % line)


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


# Pomegranate Hour: the index of an episode state on the six-step
# ladder. Returns -1 for unknown states.
func _episode_state_index(state_id: String) -> int:
	return _episode_state_ladder.find(state_id)


# Pomegranate Hour: advance the named episode-space one state up the
# ladder. Increments the run's episodes_advanced counter for the win
# condition. Returns the new state id (or "" if the space wasn't an
# episode-space, or was already at LOCKED).
func advance_episode(space_id: String) -> String:
	var cur: String = String(_episode_states.get(space_id, ""))
	if cur == "":
		return ""
	var idx: int = _episode_state_index(cur)
	if idx < 0 or idx >= _episode_state_ladder.size() - 1:
		return ""
	var nxt: String = String(_episode_state_ladder[idx + 1])
	_episode_states[space_id] = nxt
	_episodes_advanced_this_run += 1
	return nxt


# Magician / cathedral — the "bright" zone. Inner cluster (warm-lit
# finished pieces around the workbench) plus the explicitly-illuminated
# outer-cluster stations (TOWER neon, STAR lights, SUN, JUDGEMENT
# platform). MOTH demon's mechanics route on this set.
const _CATHEDRAL_BRIGHT_SPACES := [
	"magician",      # workbench lamp
	"fool",
	"priestess",
	"empress",
	"emperor",
	"hierophant",    # inner cluster, warm-lit
	"tower",         # neon
	"star",          # cluster of cold-blue LEDs
	"sun",           # lit pool
	"judgement",     # platform
]
func _is_bright_space(pos: String) -> bool:
	if _arcana_id != "magician":
		return false
	return pos in _CATHEDRAL_BRIGHT_SPACES


# Threshold-locked flag check: lock_threshold_open writes
# `threshold_locked:<id>` = <expiry-turn>. A threshold is "locked open"
# while the current turn <= expiry. Used by both the win-path
# threshold check and the threshold-claim path.
func _is_threshold_locked_open(pos: String) -> bool:
	var key := "threshold_locked:" + pos
	if not _flags.has(key):
		return false
	return _turn <= int(_flags[key])


func _win_conditions_met() -> bool:
	var wc: Dictionary = _setup.get("win_conditions", {})
	# ── Magician schema ─────────────────────────────────────────
	# Detect Magician runs by arcana id; the predicate set is
	# different from the Fool's (no bindle, no Faith-adjacent).
	if _arcana_id == "magician":
		var need_pieces: int = int(wc.get("require_pieces_completed_min", 0))
		if _pieces_completed < need_pieces:
			return false
		var need_connect: int = int(wc.get("require_visitors_connected_min", 0))
		if _connections_made.size() < need_connect:
			return false
		var need_hard: int = int(wc.get("require_hard_mood_connections_min", 0))
		if need_hard > 0:
			var hard_count: int = 0
			for cvid in _connections_made:
				var cv_def: Dictionary = _visitors_def.get(String(cvid), {})
				var mood: String = String(cv_def.get("mood", ""))
				if mood == "gruff" or mood == "preoccupied" or mood == "left_alone":
					hard_count += 1
			if hard_count < need_hard:
				return false
		if _doubt >= int(wc.get("require_doubt_below", 99)):
			return false
		if _stagnation >= int(wc.get("require_stagnation_below", 99)):
			return false
		if bool(wc.get("require_steamboat_unfinished", false)):
			if _steamboat_progress >= _steamboat_threshold:
				return false
		if bool(wc.get("require_cake_lit", false)):
			if not _flags.get("cake_lit", false):
				return false
		if bool(wc.get("require_threshold_space", true)) and not _is_threshold(_player_pos):
			return false
		return true
	# ── Chariot schema ──────────────────────────────────────────
	if _arcana_id == "chariot":
		var ch_need_connect: int = int(wc.get("require_visitors_connected_min", 3))
		if _connections_made.size() < ch_need_connect:
			return false
		var ch_need_hard: int = int(wc.get("require_hard_mood_connections_min", 0))
		if ch_need_hard > 0:
			var ch_hard_count: int = 0
			for chcvid in _connections_made:
				var chcv_def: Dictionary = _visitors_def.get(String(chcvid), {})
				var chmood: String = String(chcv_def.get("mood", ""))
				if chmood == "intense" or chmood == "lonely" or chmood == "preoccupied":
					ch_hard_count += 1
			if ch_hard_count < ch_need_hard:
				return false
		if _doubt >= int(wc.get("require_doubt_below", 99)):
			return false
		if _stagnation >= int(wc.get("require_stagnation_below", 99)):
			return false
		if _miles < int(wc.get("require_miles_at_least", 0)):
			return false
		if bool(wc.get("require_threshold_space", true)) and not _is_threshold(_player_pos):
			return false
		return true
	# ── Lovers schema ───────────────────────────────────────────
	if _arcana_id == "lovers":
		var lv_need_connect: int = int(wc.get("require_visitors_connected_min", 3))
		if _connections_made.size() < lv_need_connect:
			return false
		var lv_need_hard: int = int(wc.get("require_hard_mood_connections_min", 0))
		if lv_need_hard > 0:
			var lv_hard_count: int = 0
			for lvcvid in _connections_made:
				var lvcv_def: Dictionary = _visitors_def.get(String(lvcvid), {})
				var lvmood: String = String(lvcv_def.get("mood", ""))
				if lvmood == "intense" or lvmood == "lonely" or lvmood == "preoccupied":
					lv_hard_count += 1
			if lv_hard_count < lv_need_hard:
				return false
		if _doubt >= int(wc.get("require_doubt_below", 99)):
			return false
		if _stagnation >= int(wc.get("require_stagnation_below", 99)):
			return false
		if _sync < int(wc.get("require_sync_at_least", 0)):
			return false
		# Lovers' signature: the partner must be at the player's space
		# at the moment of LEAP. If they are, set the lovers_synced_leap
		# flag for the achievement evaluator.
		if bool(wc.get("require_partner_at_my_pos_at_leap", false)):
			if _lovers_partner_id == "":
				return false
			var lp_pst: Dictionary = _visitors_state.get(_lovers_partner_id, {})
			if String(lp_pst.get("pos", "")) != _player_pos:
				return false
			_flags["lovers_synced_leap"] = true
		if bool(wc.get("require_threshold_space", true)) and not _is_threshold(_player_pos):
			return false
		return true
	# ── Hierophant schema ───────────────────────────────────────
	if _arcana_id == "hierophant":
		var h_need_connect: int = int(wc.get("require_visitors_connected_min", 3))
		if _connections_made.size() < h_need_connect:
			return false
		var h_need_hard: int = int(wc.get("require_hard_mood_connections_min", 0))
		if h_need_hard > 0:
			var h_hard_count: int = 0
			for hcvid in _connections_made:
				var hcv_def: Dictionary = _visitors_def.get(String(hcvid), {})
				var hmood: String = String(hcv_def.get("mood", ""))
				if hmood == "intense" or hmood == "lonely" or hmood == "preoccupied":
					h_hard_count += 1
			if h_hard_count < h_need_hard:
				return false
		if _doubt >= int(wc.get("require_doubt_below", 99)):
			return false
		if _stagnation >= int(wc.get("require_stagnation_below", 99)):
			return false
		if _signal < int(wc.get("require_signal_at_least", 0)):
			return false
		if bool(wc.get("require_threshold_space", true)) and not _is_threshold(_player_pos):
			return false
		return true
	# ── Emperor schema ──────────────────────────────────────────
	if _arcana_id == "emperor":
		var em_need_connect: int = int(wc.get("require_visitors_connected_min", 3))
		if _connections_made.size() < em_need_connect:
			return false
		var em_need_hard: int = int(wc.get("require_hard_mood_connections_min", 0))
		if em_need_hard > 0:
			var em_hard_count: int = 0
			for emcvid in _connections_made:
				var emcv_def: Dictionary = _visitors_def.get(String(emcvid), {})
				var emmood: String = String(emcv_def.get("mood", ""))
				if emmood == "intense" or emmood == "lonely" or emmood == "preoccupied":
					em_hard_count += 1
			if em_hard_count < em_need_hard:
				return false
		if _doubt >= int(wc.get("require_doubt_below", 99)):
			return false
		if _stagnation >= int(wc.get("require_stagnation_below", 99)):
			return false
		if _ledger < int(wc.get("require_ledger_at_least", 0)):
			return false
		if bool(wc.get("require_threshold_space", true)) and not _is_threshold(_player_pos):
			return false
		return true
	# ── Empress schema ──────────────────────────────────────────
	if _arcana_id == "empress":
		var e_need_connect: int = int(wc.get("require_visitors_connected_min", 3))
		if _connections_made.size() < e_need_connect:
			return false
		var e_need_hard: int = int(wc.get("require_hard_mood_connections_min", 0))
		if e_need_hard > 0:
			var e_hard_count: int = 0
			for ecvid in _connections_made:
				var ecv_def: Dictionary = _visitors_def.get(String(ecvid), {})
				var emood: String = String(ecv_def.get("mood", ""))
				if emood == "preoccupied" or emood == "lonely" or emood == "left_alone":
					e_hard_count += 1
			if e_hard_count < e_need_hard:
				return false
		if _doubt >= int(wc.get("require_doubt_below", 99)):
			return false
		if _stagnation >= int(wc.get("require_stagnation_below", 99)):
			return false
		if _bloom < int(wc.get("require_bloom_at_least", 0)):
			return false
		if bool(wc.get("require_threshold_space", true)) and not _is_threshold(_player_pos):
			return false
		return true
	# ── Priestess schema ────────────────────────────────────────
	if _arcana_id == "priestess":
		var p_need_connect: int = int(wc.get("require_visitors_connected_min", 3))
		if _connections_made.size() < p_need_connect:
			return false
		var p_need_hard: int = int(wc.get("require_hard_mood_connections_min", 0))
		if p_need_hard > 0:
			var p_hard_count: int = 0
			for pcvid in _connections_made:
				var pcv_def: Dictionary = _visitors_def.get(String(pcvid), {})
				var pmood: String = String(pcv_def.get("mood", ""))
				if pmood == "intense" or pmood == "lonely" or pmood == "preoccupied":
					p_hard_count += 1
			if p_hard_count < p_need_hard:
				return false
		if _doubt >= int(wc.get("require_doubt_below", 99)):
			return false
		if _stagnation >= int(wc.get("require_stagnation_below", 99)):
			return false
		if _master_reel >= int(wc.get("require_master_reel_below", _master_reel_threshold + 1)):
			return false
		# Pomegranate Hour: episodes advanced this run.
		var need_advances: int = int(wc.get("require_episodes_advanced_min", 0))
		if need_advances > 0 and _episodes_advanced_this_run < need_advances:
			return false
		# Pomegranate Hour: a specific episode must have advanced past
		# its starting state. "require_episode_locked" is a slight
		# misnomer — it means "this episode-space must have been
		# advanced at least once tonight," which is the win for The
		# Conversation (Ep. 17 moves from TITLE_CARD_ONLY to
		# FOOTAGE_ONLY).
		var locked_space: String = String(wc.get("require_episode_locked", ""))
		if locked_space != "":
			var cur_state: String = String(_episode_states.get(locked_space, ""))
			var start_state: String = ""
			for sdef_chk in (_location.get("spaces", []) as Array):
				if String((sdef_chk as Dictionary).get("id", "")) == locked_space:
					start_state = String((sdef_chk as Dictionary).get("episode_state", ""))
					break
			# overlay scenario starting override if present
			var ep_ov: Dictionary = (_setup.get("starting_state", {}) as Dictionary).get("starting_episode_states", {}) as Dictionary
			if ep_ov.has(locked_space):
				start_state = String(ep_ov[locked_space])
			if _episode_state_index(cur_state) <= _episode_state_index(start_state):
				return false
		# Pomegranate Hour: cast/crew sit_with completions.
		var need_cc_sit: int = int(wc.get("require_cast_crew_sit_with_min", 0))
		if need_cc_sit > 0 and _cast_crew_sit_with_count < need_cc_sit:
			return false
		if bool(wc.get("require_threshold_space", true)) and not _is_threshold(_player_pos):
			return false
		return true
	# ── Fool schema (default) ───────────────────────────────────
	if not _bindle_assembled:
		return false
	if _connections_made.size() < int(wc.get("require_visitors_connected_min", 3)):
		return false
	if _inertia >= int(wc.get("require_inertia_below", 7)):
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
	# Achievement bookkeeping — count cards played per run.
	_cards_played_this_run[cid] = int(_cards_played_this_run.get(cid, 0)) + 1
	var base_cost: int = int(card.get("time_cost", 1))
	var cost: int = base_cost
	# Gravity-imposed cost bump (e.g. THE FLUORESCENT TICK)
	if _this_turn_cost_bump_amt > 0 and base_cost >= _this_turn_cost_bump_min:
		cost += _this_turn_cost_bump_amt
		_log_line("[color=#ff8060][i]the tick: +%d to %s[/i][/color]" % [_this_turn_cost_bump_amt, card.get("title", cid)])
	# Inertia 11+: every Action card costs +1 Time (the counter
	# knows your name — even small gestures get sticky)
	if _inertia >= 11:
		cost += 1
		_log_line("[color=#ff8060][i]the counter knows: +1 Time on %s[/i][/color]" % card.get("title", cid))
	if _time < cost:
		_log_line("[i]not enough Time to play %s (need %d, have %d)[/i]" % [card.get("title", cid), cost, _time])
		return
	_time -= cost
	_played_this_turn.append(cid)
	# Track for IMPROVISE replay — but don't overwrite when IMPROVISE
	# itself is the card being played (it should reference the
	# previous play, not itself).
	if cid != "improvise":
		_last_played_cid = cid
	_audio_sfx("card_play")
	# Log the play with the card's flavor underneath — gives every
	# action its quiet sentence in the log instead of bare verbs.
	_log_line("[color=#c8a268]→ played[/color] [b]%s[/b]  [color=#7c8398](-%d Time)[/color]" %
		[card.get("title", cid), cost])
	var card_flavor: String = String(card.get("flavor", ""))
	if card_flavor != "":
		_log_line("[color=#7c8398][i]   %s[/i][/color]" % card_flavor)
	# Resolve effects
	_resolve_effects(card.get("effects", []))
	# Threat-clearing: any card whose id is named in an active threat's
	# `cleared_by.card` clears that threat when played at the threat's
	# space. CLEAN at the bathroom mops the bathroom; CLEAN at the
	# river window wipes the miasma off the glass.
	_clear_threats_at(_player_pos, cid)
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
			# In-turn modifier only — Time refreshes next turn and
			# leftover never carries, so gain_time doesn't push the
			# next-turn baseline upward.
			_time += int(e.get("amount", 0))
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
		"recover_sanity":
			var rec_amt: int = int(e.get("amount", 0))
			_sanity = min(_sanity_max, _sanity + rec_amt)
			if rec_amt > 0:
				_log_line("[color=#7cffb0]+%d Sanity[/color] → %d" % [rec_amt, _sanity])
		"lose_sanity":
			# Mental-threat mechanic. The room thins you out — voices
			# you almost remember, lights that tick when you breathe,
			# clocks that won't move. At 0, the loop closes.
			var amt: int = int(e.get("amount", 1))
			_sanity = max(0, _sanity - amt)
			_log_line("[color=#ff8060]-%d Sanity[/color] → %d" % [amt, _sanity])
			if _sanity == 0:
				_log_line("[color=#ff5040][b]The fluorescent goes solid. The counter is colder than the cloth. You don't quite remember what you came in here for.[/b][/color]")
				_trigger_loss("sanity_zero")
		"spawn_threat":
			_spawn_threat(String(e.get("threat_id", "")), String(e.get("pos", "")))
		"clear_threats_here":
			_clear_threats_at(_player_pos, String(e.get("card", "")))
		"clear_all_threats":
			if _threats_active.is_empty():
				_log_line("[i]nothing to clear — the room is, for now, settled.[/i]")
			else:
				var n: int = _threats_active.size()
				for inst: Dictionary in _threats_active:
					var tdef: Dictionary = _threats_def.get(inst.get("def_id", ""), {})
					_log_line("[color=#7cffb0]✓ cleared:[/color] [b]%s[/b]" % String(tdef.get("title", "threat")))
				_threats_active = []
				_show_toast("Cleared %d threats" % n, "#7cffb0")
		"force_connect_visitor_at_my_pos":
			var any_connected: bool = false
			for vid_fp in _visitors_state:
				var vst_fp: Dictionary = _visitors_state[vid_fp]
				if not vst_fp.get("arrived", false): continue
				if vst_fp.get("connected", false): continue
				if vst_fp.get("pos", "") != _player_pos: continue
				_connect_visitor(vid_fp)
				any_connected = true
				break
			if not any_connected:
				_log_line("[i]nobody here to connect with.[/i]")
		"disperse_visitors_here":
			# Push every non-helper, non-Faith visitor at the player's
			# pos to a random adjacent space. Useful at lunch/evening
			# rush when the counter clogs and you need to clear a path
			# (e.g. via the COMING THROUGH card).
			var adj_d: Array = _location.get("adjacency", {}).get(_player_pos, [])
			if adj_d.is_empty():
				_log_line("[i]nowhere for them to drift to from here.[/i]")
			else:
				var any_moved: bool = false
				for vid_d in _visitors_state:
					var vst_d: Dictionary = _visitors_state[vid_d]
					if not vst_d.get("arrived", false): continue
					if vst_d.get("pos", "") != _player_pos: continue
					if vid_d == "faith": continue
					var vdef_d: Dictionary = _visitors_def.get(vid_d, {})
					if vdef_d.get("helper", false): continue
					if vst_d.get("connected", false): continue
					var dest: String = String(adj_d[randi() % adj_d.size()])
					vst_d["pos"] = dest
					any_moved = true
					_log_line("[color=#c8a268][i]» %s steps aside toward %s[/i][/color]" %
						[vdef_d.get("name", vid_d), dest.replace("_", " ").to_upper()])
				if not any_moved:
					_log_line("[i]nobody here to disperse.[/i]")
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
			# Real chooser modal — used by Gravity cards like
			# THE COUNTER WANTS WIPING (discard 2 cards OR +2 Inertia).
			_prompt_choose(e.get("options", []))
		"play_jukebox_track":
			# Jukebox plays the track once at full BGM volume; when the
			# track ends, AudioMgr snaps back to the diner ambient. The
			# track also unlocks in the Music Player overlay (its
			# catalog entry uses unlock.type:"heard" and play_bgm marks
			# heard automatically; we also flag the explicit unlock key
			# so MusicPlayerOverlay shows the new-unlock indicator).
			var bgm_path: String = e.get("bgm", "")
			var label: String = e.get("label", "track")
			var catalog_id: String = e.get("catalog_id", "")
			if bgm_path != "":
				var resume_src: String = _BGM_BY_LOCATION.get(_location_id, "")
				AudioMgr.play_oneshot_bgm(bgm_path, resume_src)
				_log_line("[color=#c8a268]♪ jukebox · now playing [b]%s[/b][/color]" % label)
				if catalog_id != "":
					if SaveSystem.mark_unlocked("music:" + catalog_id):
						AudioMgr.track_unlocked.emit(bgm_path, label)
						_show_toast("Music unlocked: [b]%s[/b]" % label, "#c8a268")
		"advance_stranger_connection":
			# Hook for the cloth's on_pickup. The actual connection
			# fires from _check_composite_connections — this is just
			# a (now-implemented) no-op so the warning stops firing.
			pass
		"this_turn_time_cost_modifier":
			# THE FLUORESCENT TICK gravity: bump the cost of expensive
			# cards by N for the rest of this turn. Recorded in
			# _this_turn_cost_bump and consumed by _on_play_card.
			_this_turn_cost_bump_min = int(e.get("min_cost_for_bump", 2))
			_this_turn_cost_bump_amt = int(e.get("bump", 1))
			_log_line("[color=#ff8060][i]Expensive cards cost +%d Time this turn (the tick keeps time wrong).[/i][/color]" % _this_turn_cost_bump_amt)
		"connect_visitor_at_my_pos":
			# Used by SIT WITH. Visitors with a special connect_via
			# (composite / card_played_n_times / auto_on_bundle_with_contents)
			# have their own path — sitting with them logs the
			# moment but doesn't artificially close the connection.
			# Waiter visitors (no special connect_via) connect only
			# after GREET → LISTEN → DELIVER (progress >= 3).
			for vid_p in _visitors_state:
				var vst_p: Dictionary = _visitors_state[vid_p]
				if not vst_p.get("arrived", false): continue
				if vst_p.get("connected", false): continue
				if vst_p.get("pos", "") != _player_pos: continue
				var vdef_p: Dictionary = _visitors_def.get(vid_p, {})
				var cv_p: Dictionary = vdef_p.get("connect_via", {})
				if not cv_p.is_empty():
					_log_line("[i]you sit. they don't lift their eyes.[/i]")
					continue
				var prog_p: int = int(vst_p.get("progress", 0))
				if prog_p < 3:
					_log_line("[i]they're not ready to be sat with yet.[/i]")
					continue
				_connect_visitor(vid_p)
				break
		"place_pending_order_for_visitor":
			# LISTEN follow-on. Find the visitor at the player's pos
			# whose progress was just bumped, look up their
			# order_item, spawn it as pending in the order_window
			# pile. Skip if they already have a pending order.
			for vid_o in _visitors_state:
				var vst_o: Dictionary = _visitors_state[vid_o]
				if not vst_o.get("arrived", false): continue
				if vst_o.get("connected", false): continue
				if vst_o.get("pos", "") != _player_pos: continue
				var vdef_o: Dictionary = _visitors_def.get(vid_o, {})
				var order_id: String = String(vdef_o.get("order_item", ""))
				if order_id == "": continue
				var pile: Array = _pile_state.get("order_window", [])
				if order_id in pile:
					# Already queued — don't double up
					continue
				pile.append(order_id)
				_pile_state["order_window"] = pile
				_order_pending[order_id] = true
				_log_line("[color=#c8a268][i]   The order goes up on the wheel.[/i][/color]")
				# Spawn an attached TO-GO order if this visitor declares one
				var togo_id: String = String(vdef_o.get("spawns_togo_on_listen", ""))
				if togo_id != "":
					if not (togo_id in pile):
						pile.append(togo_id)
						_pile_state["order_window"] = pile
						_order_pending[togo_id] = true
						var togo_def: Dictionary = _items_def.get(togo_id, {})
						var togo_title: String = String(togo_def.get("title", togo_id))
						var togo_pos: String = String(togo_def.get("deliver_to_pos", "?")).replace("_", " ").to_upper()
						_log_line("[color=#c8a268][i]   A TO-GO ticket prints itself: %s, for %s.[/i][/color]" % [togo_title, togo_pos])
				break
		"consume_order_for_visitor_at_my_pos":
			# DELIVER follow-on. The visitor's order_item is consumed
			# from inventory, and the delivered-order count ticks up
			# so the lunch/evening win conditions can see it.
			for vid_c in _visitors_state:
				var vst_c: Dictionary = _visitors_state[vid_c]
				if not vst_c.get("arrived", false): continue
				if vst_c.get("connected", false): continue
				if vst_c.get("pos", "") != _player_pos: continue
				var ord_id2: String = String(_visitors_def.get(vid_c, {}).get("order_item", ""))
				if ord_id2 != "" and _inventory.has(ord_id2):
					_inventory.erase(ord_id2)
					var ititle2: String = String(_items_def.get(ord_id2, {}).get("title", ord_id2))
					_log_line("[color=#7c8398][i]   You set the %s down. They take it.[/i][/color]" % ititle2)
					_flags["orders_delivered"] = int(_flags.get("orders_delivered", 0)) + 1
					break
		"ready_oldest_order":
			# ADDRESS THE BELL follow-on. First pending order in the
			# pile becomes ready.
			var pile2: Array = _pile_state.get("order_window", [])
			for iid: String in pile2:
				if _order_pending.get(iid, false):
					_order_pending[iid] = false
					var ititle: String = String(_items_def.get(iid, {}).get("title", iid))
					_log_line("[color=#c8a268][i]   The bell. \"%s\" — ready.[/i][/color]" % ititle)
					_show_toast("Order ready: [b]%s[/b]" % ititle, "#c8a268")
					break
		"advance_visitor_step":
			# GREET / LISTEN / DELIVER / SIT WITH all funnel through
			# here. The card's effect names which step it is; we find
			# the highest-progress unconnected visitor at the player's
			# space and bump their progress one. Then log the per-
			# visitor flavor line for that step (falling back to a
			# mood-default if no per-visitor line is set).
			var step_name: String = String(e.get("step", ""))
			var target_vid: String = ""
			var best_progress: int = -1
			for vid_s in _visitors_state:
				var vst_s: Dictionary = _visitors_state[vid_s]
				if not vst_s.get("arrived", false): continue
				if vst_s.get("connected", false): continue
				if vst_s.get("pos", "") != _player_pos: continue
				var p: int = int(vst_s.get("progress", 0))
				if p > best_progress:
					best_progress = p
					target_vid = vid_s
			if target_vid == "":
				_log_line("[i]nobody here to %s[/i]" % step_name)
				return
			# Only advance progress if this is the *next* step for
			# them. SIT WITH on a visitor still at 0 (the stranger,
			# composite path) logs the moment but doesn't bump them
			# to step 4. Out-of-order or repeat plays log the flavor
			# line but leave progress alone.
			var step_idx: int = _step_index(step_name)
			var cur_prog: int = int(_visitors_state[target_vid].get("progress", 0))
			var advanced: bool = false
			if step_idx > 0 and step_idx == cur_prog + 1:
				_visitors_state[target_vid]["progress"] = step_idx
				advanced = true
			_log_visitor_step_line(target_vid, step_name)
			if advanced:
				_inertia = max(0, _inertia - 1)

		# ── Magician-arcana effects ──────────────────────────────
		"gain_stagnation":
			var sa: int = int(e.get("amount", 1))
			_stagnation += sa
			_log_line("[color=#ff8060]+%d Stagnation[/color] → %d" % [sa, _stagnation])
		"lose_stagnation":
			_stagnation = max(0, _stagnation - int(e.get("amount", 1)))
			_log_line("[color=#7cffb0]-%d Stagnation[/color] → %d" % [int(e.get("amount", 1)), _stagnation])
		"gain_doubt":
			var da: int = int(e.get("amount", 1))
			_doubt = min(_doubt_max, _doubt + da)
			_log_line("[color=#ff8060]+%d Doubt[/color] → %d / %d" % [da, _doubt, _doubt_max])
			if _doubt >= _doubt_max:
				_log_line("[color=#ff5040][b]Doubt at max — the maker breaks.[/b][/color]")
				_trigger_loss("doubt_max")
		"lose_doubt":
			_doubt = max(0, _doubt - int(e.get("amount", 1)))
		"gain_inspiration":
			_inspiration += int(e.get("amount", 1))
			_log_line("[color=#7cffb0]+%d Inspiration[/color] → %d" % [int(e.get("amount", 1)), _inspiration])
		"lose_inspiration":
			_inspiration = max(0, _inspiration - int(e.get("amount", 1)))
		"spend_inspiration":
			_inspiration = max(0, _inspiration - int(e.get("amount", 1)))
			_log_line("[color=#c8a268][i]-%d Inspiration spent → %d[/i][/color]" % [int(e.get("amount", 1)), _inspiration])

		"advance_piece_at_my_pos":
			var amt: int = int(e.get("amount", 1))
			var cur: int = int(_piece_progress.get(_player_pos, 0))
			cur += amt
			_piece_progress[_player_pos] = cur
			_log_line("[color=#c8a268]piece at %s · %d / %d[/color]" % [_player_pos.to_upper(), cur, _piece_threshold])
			if cur >= _piece_threshold:
				_piece_progress[_player_pos] = _piece_threshold
				_pieces_completed += 1
				_log_line("[color=#7cffb0]✦ piece completed at %s. (%d total)[/color]" % [_player_pos.to_upper(), _pieces_completed])
				_show_toast("Piece completed at %s" % _player_pos.to_upper(), "#7cffb0")
		"unfinish_piece":
			var u_amt: int = int(e.get("amount", 1))
			var target_pos: String = _player_pos
			# If player_choice, just pick the highest-progress non-completed piece (simple default)
			if e.get("player_choice", false):
				var best_pos: String = ""
				var best_n: int = -1
				for pos in _piece_progress:
					var n: int = int(_piece_progress[pos])
					if n > best_n and n < _piece_threshold:
						best_n = n
						best_pos = pos
				if best_pos != "":
					target_pos = best_pos
			if _piece_progress.has(target_pos):
				_piece_progress[target_pos] = max(0, int(_piece_progress[target_pos]) - u_amt)
				_log_line("[color=#ff8060]piece at %s lost %d progress.[/color]" % [target_pos.to_upper(), u_amt])
		"unfinish_random_piece", "unfinish_random_finished_arcana":
			# Find a random in-progress piece and dock it 1.
			var candidates: Array = []
			for pos in _piece_progress:
				var n2: int = int(_piece_progress[pos])
				if n2 > 0:
					candidates.append(pos)
			if not candidates.is_empty():
				var pick: String = candidates[randi() % candidates.size()]
				_piece_progress[pick] = max(0, int(_piece_progress[pick]) - 1)
				_log_line("[color=#ff8060]something came undone at %s.[/color]" % pick.to_upper())

		"advance_steamboat":
			var sb_amt: int = int(e.get("amount", 1))
			_steamboat_progress += sb_amt
			_log_line("[color=#ff8060]steamboat · %d / %d[/color]" % [_steamboat_progress, _steamboat_threshold])
			_log_steamboat_beat_if_changed()
			if _steamboat_progress >= _steamboat_threshold:
				_log_line("[color=#ff5040][b]The steamboat is finished. The sinkhole opens.[/b][/color]")
				_flags["steamboat_finished"] = true
				var lc: Dictionary = _setup.get("loss_conditions", {})
				# Three loss-flavors a scenario can declare:
				#   · steamboat_finished_on_easy:false  — SINKING FEELING
				#   · steamboat_finished_before_end:true — WATCH PARTY
				#   · steamboat_finished_before_cake:true — BLOW OUT
				#     (further conditional on the cake being lit)
				var sb_loss: bool = false
				if lc.get("steamboat_finished_on_easy", true) == false: sb_loss = true
				if lc.get("steamboat_finished_before_end", false): sb_loss = true
				if lc.get("steamboat_finished_before_cake", false) and not _flags.get("cake_lit", false): sb_loss = true
				if sb_loss:
					_trigger_loss("steamboat_finished")
				else:
					# The campaign win-trigger when the scenario allows
					# finishing — only happens for cases that don't
					# punish completion (currently none in the trio,
					# but reserved for future arcs).
					_trigger_win("steamboat_finished")
		"steamboat_threshold_minus":
			_steamboat_threshold = max(1, _steamboat_threshold - int(e.get("amount", 1)))
			_log_line("[color=#ff8060]steamboat threshold → %d[/color]" % _steamboat_threshold)

		"advance_wip":
			var wid: String = String(e.get("wip", ""))
			var wamt: int = int(e.get("amount", 1))
			var wp: int = int(_wip_progress.get(wid, 0))
			wp += wamt
			_wip_progress[wid] = wp
			var wip_defs: Dictionary = _location.get("wip_models", {})
			var threshold: int = int(wip_defs.get(wid, {}).get("completion_threshold", 4))
			if wp >= threshold and not _wips_completed_this_run.get(wid, false):
				_wips_completed_this_run[wid] = true
				var codex_key: String = String(wip_defs.get(wid, {}).get("codex_key", ""))
				if codex_key != "":
					var was_new: bool = SaveSystem.mark_unlocked("codex:" + codex_key)
					if was_new:
						_log_line("[color=#7cffb0]✦ WIP completed: %s (codex annotation unlocked).[/color]" % wid)
						_show_toast("Frasier built it: %s" % wid, "#7cffb0")
				_log_line("[color=#c8a268]WIP %s reached completion.[/color]" % wid)

		"unlock_one_sealed_arcana":
			# Pick the highest-priority sealed (first in the dict order)
			# and unseal it. The player will see the door open.
			var keys: Array = _sealed_arcanas.keys()
			if keys.is_empty():
				_log_line("[i]every door in here is already open.[/i]")
			else:
				var pick_k: String = String(keys[0])
				_sealed_arcanas.erase(pick_k)
				_log_line("[color=#7cffb0]✦ unsealed: %s[/color]" % pick_k.to_upper())
				_show_toast("Door opens: %s" % pick_k.to_upper(), "#7cffb0")

		"cancel_next_gravity":
			_next_gravity_canceled = true
			_log_line("[color=#7cffb0]the next Gravity card is canceled.[/color]")

		"peek_gravity_top":
			var pn: int = int(e.get("n", 3))
			var lines: PackedStringArray = ["[color=#c8a268][b]Peeking next %d Gravity:[/b][/color]" % pn]
			for i in min(pn, _gravity_draw_pile.size()):
				var cid_p: String = _gravity_draw_pile[_gravity_draw_pile.size() - 1 - i]
				var card_p: Dictionary = _find_gravity_card(cid_p)
				lines.append("  %d · %s" % [i + 1, card_p.get("title", cid_p)])
			_log_line("\n".join(lines))

		"set_cross_arcana_flag":
			var target: String = String(e.get("target", ""))
			var key_s: String = String(e.get("key", ""))
			if target != "" and key_s != "":
				SaveSystem.mark_unlocked("cross:%s:%s" % [target, key_s])
				_log_line("[color=#c8a268][i]transmission sent to %s · flag %s[/i][/color]" % [target, key_s])

		"summon_demon":
			var did: String = String(e.get("id", ""))
			var dur: int = int(e.get("duration_turns", 3))
			if did != "":
				_active_demons[did] = dur
				_log_line("[color=#c8a268]✦ demon %s summoned for %d turns.[/color]" % [did.to_upper(), dur])

		"summon_random_demon":
			# Pull a random demon from the eight-demon Magician roster
			# that ISN'T already active. Falls back to extending a
			# random active one if all eight are already summoned.
			var roster: Array = ["vagrant","cicada","moth","steamboat","weir","filly","starling","husk"]
			var dur2: int = int(e.get("duration_turns", 4))
			var available: Array = []
			for d_id in roster:
				if not _active_demons.has(d_id): available.append(d_id)
			if available.is_empty():
				# Pick any active one and add to its duration
				if not _active_demons.is_empty():
					var picked: String = _active_demons.keys()[randi() % _active_demons.size()]
					_active_demons[picked] = int(_active_demons[picked]) + dur2
					_log_line("[color=#c8a268]✦ all demons already here · %s gains %d turns.[/color]" % [picked.to_upper(), dur2])
			else:
				var did_pick: String = available[randi() % available.size()]
				_active_demons[did_pick] = dur2
				_log_line("[color=#c8a268]✦ a new demon wakes · %s for %d turns.[/color]" % [did_pick.to_upper(), dur2])

		"all_active_demons_gain_duration":
			# Moon-rises card / similar — every currently-active demon
			# gets N more turns of stay. Empty-set falls through silently.
			var add: int = int(e.get("amount", 2))
			if _active_demons.is_empty():
				_log_line("[i]the moon rises · no demons are listening yet.[/i]")
			else:
				for did_k in _active_demons.keys():
					_active_demons[did_k] = int(_active_demons[did_k]) + add
				_log_line("[color=#c8a268]✦ the moon rises · %d demons gain %d turns each.[/color]" % [_active_demons.size(), add])

		"lock_threshold_open":
			# Locks a named threshold open for N turns. Tracked in
			# _flags as "threshold_locked:<id>" with the turn-count
			# expiry; the threshold-render code checks this flag and
			# treats the threshold as open + non-claimable while set.
			var tid: String = String(e.get("threshold", ""))
			var turns: int = int(e.get("turns", 3))
			if tid != "":
				_flags["threshold_locked:" + tid] = _turn + turns
				_log_line("[color=#7cffb0]threshold %s locked open for %d turns.[/color]" %
					[tid.to_upper(), turns])

		"tick_master_reel":
			# Priestess — advance the master reel by N. At threshold
			# the reel is full and tape-based actions become inert.
			var amt_mr: int = int(e.get("amount", 1))
			_master_reel = min(_master_reel_threshold, _master_reel + amt_mr)
			_log_line("[color=#a99070]·[/color] master reel ticks · %d / %d" %
				[_master_reel, _master_reel_threshold])
			if _master_reel >= _master_reel_threshold:
				# Loss check delegated to the scenario's loss_conditions
				# (master_reel_full_before_end). The render layer will
				# also pick up the threshold state via _master_reel.
				if bool(_setup.get("loss_conditions", {}).get("master_reel_full_before_end", false)):
					_trigger_loss("master_reel_full")

		"untick_master_reel":
			# SHELVE — move a finished tape onto the wall, freeing
			# reel space. Doesn't go below 0.
			var amt_um: int = int(e.get("amount", 1))
			_master_reel = max(0, _master_reel - amt_um)
			_log_line("[color=#7cffb0]·[/color] tape filed · master reel %d / %d" %
				[_master_reel, _master_reel_threshold])

		"gain_insight":
			var ig: int = int(e.get("amount", 1))
			_insight += ig
			_log_line("[color=#a8e89c]+%d Insight[/color] → %d" % [ig, _insight])

		"spend_insight":
			var is_amt: int = int(e.get("amount", 1))
			_insight = max(0, _insight - is_amt)
			_log_line("[color=#a99070]-%d Insight[/color] → %d" % [is_amt, _insight])

		"tick_bloom":
			# Empress — Bloom rises (good). Caps at threshold.
			var b_amt: int = int(e.get("amount", 1))
			_bloom = min(_bloom_threshold, _bloom + b_amt)
			_log_line("[color=#7cffb0]+%d Bloom[/color] → %d / %d" %
				[b_amt, _bloom, _bloom_threshold])

		"spend_bloom":
			var bs: int = int(e.get("amount", 1))
			_bloom = max(0, _bloom - bs)
			_log_line("[color=#a99070]-%d Bloom[/color] → %d / %d" %
				[bs, _bloom, _bloom_threshold])

		"gain_harvest":
			var hg: int = int(e.get("amount", 1))
			_harvest += hg
			_log_line("[color=#88b87a]+%d Harvest[/color] → %d" % [hg, _harvest])

		"spend_harvest":
			var hs: int = int(e.get("amount", 1))
			_harvest = max(0, _harvest - hs)
			_log_line("[color=#a99070]-%d Harvest[/color] → %d" % [hs, _harvest])

		"gain_authority":
			var ag: int = int(e.get("amount", 1))
			_authority += ag
			_log_line("[color=#d8a060]+%d Authority[/color] → %d" % [ag, _authority])

		"spend_authority":
			var as_amt: int = int(e.get("amount", 1))
			_authority = max(0, _authority - as_amt)
			_log_line("[color=#a99070]-%d Authority[/color] → %d" % [as_amt, _authority])

		"tick_ledger":
			var lg: int = int(e.get("amount", 1))
			_ledger = min(_ledger_threshold, _ledger + lg)
			_log_line("[color=#d8a060]·[/color] ledger ticks · %d / %d" %
				[_ledger, _ledger_threshold])
			if _ledger >= _ledger_threshold:
				if bool(_setup.get("loss_conditions", {}).get("ledger_full_before_end", false)):
					_trigger_loss("ledger_full")

		"gain_doctrine":
			var dg: int = int(e.get("amount", 1))
			_doctrine += dg
			_log_line("[color=#a8e89c]+%d Doctrine[/color] → %d" % [dg, _doctrine])

		"spend_doctrine":
			var ds: int = int(e.get("amount", 1))
			_doctrine = max(0, _doctrine - ds)
			_log_line("[color=#a99070]-%d Doctrine[/color] → %d" % [ds, _doctrine])

		"tick_signal":
			var sg: int = int(e.get("amount", 1))
			_signal = min(_signal_threshold, _signal + sg)
			_log_line("[color=#a8e89c]·[/color] signal ticks · %d / %d" %
				[_signal, _signal_threshold])
			if _signal >= _signal_threshold:
				if bool(_setup.get("loss_conditions", {}).get("signal_full_before_end", false)):
					_trigger_loss("signal_full")

		"gain_verb":
			var vg: int = int(e.get("amount", 1))
			_verb += vg
			_log_line("[color=#d8a060]+%d Verb[/color] → %d" % [vg, _verb])

		"spend_verb":
			var vs: int = int(e.get("amount", 1))
			_verb = max(0, _verb - vs)
			_log_line("[color=#a99070]-%d Verb[/color] → %d" % [vs, _verb])

		"tick_sync_if_partner_here":
			# Lovers — SYNC ticks only when the partner is at the
			# player's space. If they're not, the card's flavor still
			# log-lines but SYNC doesn't move.
			var sy_amt: int = int(e.get("amount", 1))
			if _lovers_partner_id != "":
				var pst: Dictionary = _visitors_state.get(_lovers_partner_id, {})
				if String(pst.get("pos", "")) == _player_pos:
					_sync = min(_sync_threshold, _sync + sy_amt)
					_log_line("[color=#a8e89c]·[/color] sync ticks · %d / %d" %
						[_sync, _sync_threshold])
				else:
					_log_line("[i]reed is in the other corner. sync holds.[/i]")

		"tick_miles":
			# Chariot — drive forward (or backward, if amount < 0).
			# Capped at threshold and never goes below 0.
			var mi: int = int(e.get("amount", 1))
			_miles = clamp(_miles + mi, 0, _miles_threshold)
			_log_line("[color=#a8e89c]·[/color] miles %s · %d / %d" %
				["forward" if mi >= 0 else "back", _miles, _miles_threshold])

		"gain_fuel":
			var fg: int = int(e.get("amount", 1))
			_fuel += fg
			_log_line("[color=#88b87a]+%d Fuel[/color] → %d" % [fg, _fuel])

		"spend_fuel":
			var fs: int = int(e.get("amount", 1))
			_fuel = max(0, _fuel - fs)
			_log_line("[color=#a99070]-%d Fuel[/color] → %d" % [fs, _fuel])

		"move_partner_random":
			# Move the lovers partner to a random non-threshold space,
			# different from their current. Gravity-driven.
			if _lovers_partner_id == "":
				return
			var pst2: Dictionary = _visitors_state.get(_lovers_partner_id, {})
			var here: String = String(pst2.get("pos", ""))
			var candidates: Array = []
			for s: Dictionary in _location.get("spaces", []):
				if s.get("kind", "") == "threshold": continue
				var sid_c: String = String(s.get("id", ""))
				if sid_c != "" and sid_c != here:
					candidates.append(sid_c)
			if candidates.is_empty():
				return
			var next_pos: String = String(candidates[randi() % candidates.size()])
			pst2["pos"] = next_pos
			_log_line("[i]reed crosses to %s.[/i]" % next_pos.replace("_", " "))

		"freeze_patience":
			# THE LONG QUIET — patience does not tick for N turns. The
			# upkeep ticker checks _patience_frozen_turns and skips
			# the tick when set; the counter decrements at upkeep.
			var ft: int = int(e.get("turns", 1))
			_patience_frozen_turns = max(_patience_frozen_turns, ft)
			_log_line("[color=#a8e89c]✦ the long quiet · patience holds for %d turn%s.[/color]" %
				[ft, "" if ft == 1 else "s"])

		"advance_visitor_schedule":
			# CALL IN — pull the next scheduled visitor in early. Picks
			# the unarrived visitor with the lowest scheduled_turn and
			# brings them in this turn.
			var picked_v: String = ""
			var best_turn: int = 99
			for vid_sc in _visitors_state:
				var st_sc: Dictionary = _visitors_state[vid_sc]
				if st_sc.get("arrived", false): continue
				if not st_sc.has("scheduled_turn"): continue
				var sched: int = int(st_sc.get("scheduled_turn", 99))
				if sched < best_turn:
					best_turn = sched
					picked_v = vid_sc
			if picked_v != "":
				var st_p: Dictionary = _visitors_state[picked_v]
				st_p["arrived"] = true
				st_p["arrived_turn"] = _turn
				st_p["pos"] = String(st_p.get("arrival_pos", "lounge"))
				var vn: String = String(_visitors_def.get(picked_v, {}).get("name", picked_v))
				_log_line("[color=#a99070]✦ %s arrives early.[/color]" % vn)
			else:
				_log_line("[i]nobody else booked tonight.[/i]")

		"patch_two_spaces":
			# PATCH — two named spaces are treated as one for visitor
			# proximity for N turns. While a patch is active, a
			# visitor in space A can be addressed from space B (and
			# vice versa). Per-card "a" and "b" name the pair.
			var pa: String = String(e.get("a", ""))
			var pb: String = String(e.get("b", ""))
			var pt: int = int(e.get("turns", 1))
			if pa != "" and pb != "":
				_patched_pairs.append({"a": pa, "b": pb, "turns": pt})
				_log_line("[color=#a8e89c]✦ patched %s ↔ %s for %d turn%s.[/color]" %
					[pa.to_upper(), pb.to_upper(), pt, "" if pt == 1 else "s"])

		"force_connect_visitor_in_bright_space":
			# MOTH demon — picks the first arrived/unconnected visitor
			# at a bright space and force-connects them. Skips the
			# greet/listen/deliver/sit_with sequence; useful when
			# you're out of time but need the visitor counted.
			var picked_vid: String = ""
			for vid_m in _visitors_state:
				var st_m: Dictionary = _visitors_state[vid_m]
				if not st_m.get("arrived", false): continue
				if st_m.get("connected", false): continue
				if _is_bright_space(String(st_m.get("pos", ""))):
					picked_vid = vid_m
					break
			if picked_vid == "":
				_log_line("[i]moth circles a darker piece. no bright-space visitor to claim.[/i]")
			else:
				var vst_m: Dictionary = _visitors_state[picked_vid]
				vst_m["connected"] = true
				vst_m["progress"] = 4
				vst_m["forced_by"] = "moth"
				var v_name: String = String(_visitors_def.get(picked_vid, {}).get("name", picked_vid))
				_log_line("[color=#c8a268]✦ moth claims %s for you. they leave with the light.[/color]" % v_name)
				_show_toast("Moth-claimed: %s" % v_name, "#c8a268")

		"buy_random_tableau":
			# "Someone bought the file" — a gravity-driven shopper
			# decrements one random tableau card's stock by 1. If a
			# card was already at 0 it's skipped; if none have stock
			# remaining the log notes the empty shelves.
			var with_stock: Array = []
			for cid_t in _tableau_stock.keys():
				if int(_tableau_stock[cid_t]) > 0:
					with_stock.append(cid_t)
			if with_stock.is_empty():
				_log_line("[i]somebody came in to buy. the shelves are bare.[/i]")
			else:
				var bought: String = String(with_stock[randi() % with_stock.size()])
				_tableau_stock[bought] = int(_tableau_stock[bought]) - 1
				var c_title: String = String(_action_cards.get(bought, {}).get("title", bought))
				_log_line("[color=#7c8398][i]somebody bought %s before you could.[/i][/color]" % c_title.to_upper())

		"mark_space":
			# Lightweight space-key marker for RECORD-style mechanics.
			_flags["space_marker:%s" % _player_pos] = String(e.get("key", "marked"))

		"consume_inventory_for_contents":
			# COLLAGE — consume N items from inventory, produce one
			# generic contents item that counts toward the Bindle.
			var n_needed: int = int(e.get("amount", 3))
			if _inventory.size() < n_needed:
				_log_line("[i]not enough pieces to collage yet.[/i]")
			else:
				for i in n_needed:
					_inventory.pop_back()
				_inventory.append("contents_collage")
				_log_line("[color=#7cffb0]✦ collage piece assembled.[/color]")
		"light_the_candles":
			# BLOW OUT THE CANDLES win path. Sets the cake_lit flag,
			# bumps Inspiration, drops Stagnation + Doubt. Should be
			# played at the MAGICIAN workbench.
			if _player_pos != "magician":
				_log_line("[i]the cake is at the workbench. light them there.[/i]")
			elif _flags.get("cake_lit", false):
				_log_line("[i]the candles are already lit. let them burn down.[/i]")
			else:
				_flags["cake_lit"] = true
				_inspiration += 3
				_stagnation = max(0, _stagnation - 2)
				_doubt = max(0, _doubt - 1)
				_log_line("[color=#ffd07a][b]✦ the candles are lit.[/b][/color]")
				_log_line("[color=#7c8398][i]everyone in the room turns. someone starts the song. someone takes a photo. for thirty seconds you are inside the moment instead of beside it.[/i][/color]")
				_show_toast("Candles lit · +3 Inspiration", "#ffd07a")
				# Milestone — unlocks the candles_lit BGM stinger,
				# the Full Moon music-player skin, and the Steamboat
				# Wheel visualizer. Fires once per save.
				if SaveSystem.mark_unlocked("milestone:candles_lit"):
					_log_line("[color=#a99060][i]a new track is in the music player.[/i][/color]")

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
func _prompt_contents_pick(pile_id: String) -> void:
	# REGISTER pile semantics: draw the top item (already shuffled),
	# show the player what it is + its flavor, offer KEEP or PUT BACK.
	# Put-back shuffles the pile so the next draw is uncertain.
	# This is the meaningful per-run choice — which contents you carry
	# defines the ending.
	var pile: Array = _pile_state.get(pile_id, [])
	if pile.is_empty():
		_log_line("[i]the register drawer is empty.[/i]")
		return
	var iid: String = String(pile[0])
	var item: Dictionary = _items_def.get(iid, {})
	var existing: Node = get_node_or_null("pane_modal_dim")
	if existing != null and is_instance_valid(existing):
		existing.queue_free()
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.82)
	dim.top_level = true
	dim.position = Vector2.ZERO
	dim.size = get_viewport_rect().size
	dim.mouse_filter = Control.MOUSE_FILTER_STOP
	dim.z_index = 100
	dim.name = "pane_modal_dim"
	add_child(dim)
	var view: Vector2 = get_viewport_rect().size
	var pop := PanelContainer.new()
	pop.add_theme_stylebox_override("panel", _make_panel_style())
	pop.size = Vector2(min(view.x * 0.72, 760.0), min(view.y * 0.72, 540.0))
	pop.position = (view - pop.size) * 0.5
	pop.mouse_filter = Control.MOUSE_FILTER_STOP
	dim.add_child(pop)
	var root := HBoxContainer.new()
	root.add_theme_constant_override("separation", 16)
	pop.add_child(root)
	# Art on the left
	var art_panel := PanelContainer.new()
	art_panel.add_theme_stylebox_override("panel", _make_panel_style())
	art_panel.custom_minimum_size = Vector2(260, 360)
	root.add_child(art_panel)
	var art_tex: Texture2D = _load_texture_silent(_art_path_item(iid))
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
		ph.text = "(no art yet)"
		ph.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		ph.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		ph.add_theme_color_override("font_color", Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.4))
		ph.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		ph.size_flags_vertical = Control.SIZE_EXPAND_FILL
		art_panel.add_child(ph)
	# Text on the right
	var info := VBoxContainer.new()
	info.add_theme_constant_override("separation", 10)
	info.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	root.add_child(info)
	var head := Label.new()
	head.text = "  The register drawer."
	head.add_theme_color_override("font_color", C_ACCENT)
	head.add_theme_font_size_override("font_size", 12)
	info.add_child(head)
	var title := Label.new()
	title.text = item.get("title", iid)
	title.add_theme_color_override("font_color", C_ACCENT)
	title.add_theme_font_size_override("font_size", 20)
	title.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	info.add_child(title)
	var flavor := RichTextLabel.new()
	flavor.bbcode_enabled = true
	flavor.fit_content = true
	flavor.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	flavor.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	flavor.add_theme_color_override("default_color", C_TEXT)
	flavor.add_theme_font_size_override("normal_font_size", 12)
	flavor.text = "[i]" + String(item.get("flavor", "")) + "[/i]"
	info.add_child(flavor)
	var hint := RichTextLabel.new()
	hint.bbcode_enabled = true
	hint.fit_content = true
	hint.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	hint.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hint.add_theme_color_override("default_color", Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.7))
	hint.add_theme_font_size_override("normal_font_size", 12)
	hint.text = "[i]This is the contents of your bindle. KEEP it and the LEAP carries it — your ending will be shaped by what you carried. PUT BACK shuffles the drawer; next search draws something else.[/i]"
	info.add_child(hint)
	var spacer := Control.new()
	spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	info.add_child(spacer)
	var actions := HBoxContainer.new()
	actions.add_theme_constant_override("separation", 10)
	info.add_child(actions)
	var putback := Button.new()
	putback.text = "Put it back"
	putback.add_theme_font_size_override("font_size", 13)
	putback.custom_minimum_size = Vector2(140, 36)
	putback.pressed.connect(func() -> void:
		pile.shuffle()
		_log_line("[i]you slide it back, slide the drawer back in. The register isn't done with you.[/i]")
		_close_pane_modal(dim))
	actions.add_child(putback)
	var spacer2 := Control.new()
	spacer2.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	actions.add_child(spacer2)
	var keep := Button.new()
	keep.text = "✦  Keep it  (+1 to bindle)"
	keep.add_theme_font_size_override("font_size", 14)
	keep.custom_minimum_size = Vector2(180, 36)
	keep.pressed.connect(func() -> void:
		pile.pop_front()
		_inventory.append(iid)
		_audio_sfx("item_pickup")
		_log_line("[color=#c8a268]✦ kept:[/color] [b]%s[/b]" % item.get("title", iid))
		var pf2: String = String(item.get("flavor", ""))
		if pf2 != "":
			_log_line("[color=#7c8398][i]   %s[/i][/color]" % pf2)
		_show_toast("Bindle contents: [b]%s[/b]" % item.get("title", iid), "#c8a268")
		_inertia = max(0, _inertia - 1)
		# Side effects from the contents (e.g. cassette spawns Anya)
		if item.has("side_effects"):
			_resolve_effects(item["side_effects"])
		_check_composite_connections()
		_close_pane_modal(dim)
		_render())
	actions.add_child(keep)


func _prompt_search_choice(pile_id: String, peek: int) -> void:
	# SEARCH ★★ — peek the top `peek` items in the pile, let the
	# player pick one. Un-chosen items stay in their original
	# positions in the pile (so the next search finds them).
	var pile: Array = _pile_state.get(pile_id, [])
	if pile.is_empty():
		_log_line("[i]nothing to look at[/i]")
		return
	# If fewer items than `peek`, just take the top.
	if pile.size() < 2:
		_take_top_item_at_pos()
		return
	var peek_n: int = min(peek, pile.size())
	var top_ids: Array = []
	for i in peek_n:
		top_ids.append(pile[i])
	var existing: Node = get_node_or_null("pane_modal_dim")
	if existing != null and is_instance_valid(existing):
		existing.queue_free()
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.80)
	dim.top_level = true
	dim.position = Vector2.ZERO
	dim.size = get_viewport_rect().size
	dim.mouse_filter = Control.MOUSE_FILTER_STOP
	dim.z_index = 100
	dim.name = "pane_modal_dim"
	add_child(dim)
	var view: Vector2 = get_viewport_rect().size
	var pop := PanelContainer.new()
	pop.add_theme_stylebox_override("panel", _make_panel_style())
	pop.size = Vector2(min(view.x * 0.62, 640.0), min(view.y * 0.62, 460.0))
	pop.position = (view - pop.size) * 0.5
	pop.mouse_filter = Control.MOUSE_FILTER_STOP
	dim.add_child(pop)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 10)
	pop.add_child(vb)
	var title := Label.new()
	title.text = "  ★★  Search — Look at top %d, take 1" % peek_n
	title.add_theme_color_override("font_color", C_ACCENT)
	title.add_theme_font_size_override("font_size", 16)
	vb.add_child(title)
	var hint := Label.new()
	hint.text = "  Whichever you don't take stays in the pile for next time."
	hint.add_theme_color_override("font_color", Color(0.85, 0.83, 0.78, 0.7))
	hint.add_theme_font_size_override("font_size", 12)
	vb.add_child(hint)
	vb.add_child(HSeparator.new())
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	vb.add_child(row)
	for i in top_ids.size():
		var iid: String = String(top_ids[i])
		var item: Dictionary = _items_def.get(iid, {})
		var tile := VBoxContainer.new()
		tile.add_theme_constant_override("separation", 4)
		var btn := Button.new()
		btn.custom_minimum_size = Vector2(140, 140)
		var art: Texture2D = _load_texture_silent(_art_path_item(iid))
		if art:
			btn.icon = art
			btn.expand_icon = true
		btn.tooltip_text = "%s\n\n%s" % [item.get("title", iid), String(item.get("flavor", ""))]
		var idx: int = i
		btn.pressed.connect(func() -> void:
			# Remove the chosen index from the pile, add to inventory
			pile.remove_at(idx)
			_inventory.append(iid)
			_audio_sfx("item_pickup")
			_log_line("[color=#c8a268]✦ took:[/color] [b]%s[/b]" % item.get("title", iid))
			var fl: String = String(item.get("flavor", ""))
			if fl != "":
				_log_line("[color=#7c8398][i]   %s[/i][/color]" % fl)
			# on_pickup hooks + bindle toast + composite check
			var cat: String = item.get("category", "")
			if cat == "bindle_component" or cat == "bindle_contents":
				_show_toast("Picked up [b]%s[/b]" % item.get("title", iid), "#c8a268")
			if item.has("on_pickup"):
				_resolve_effects(item["on_pickup"])
			if cat == "bindle_component" or cat == "bindle_contents":
				_inertia = max(0, _inertia - 1)
			_check_composite_connections()
			_close_pane_modal(dim)
			_render())
		tile.add_child(btn)
		var lbl := Label.new()
		lbl.text = String(item.get("title", iid))
		lbl.add_theme_font_size_override("font_size", 12)
		lbl.add_theme_color_override("font_color", C_TEXT)
		lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		lbl.custom_minimum_size = Vector2(140, 30)
		tile.add_child(lbl)
		row.add_child(tile)


func _prompt_choose(options: Array) -> void:
	# Used by Gravity-card "choose" effects. Pops a modal with one
	# button per option; click an option to resolve its effects.
	if options.is_empty():
		return
	var existing: Node = get_node_or_null("pane_modal_dim")
	if existing != null and is_instance_valid(existing):
		existing.queue_free()
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.80)
	dim.top_level = true
	dim.position = Vector2.ZERO
	dim.size = get_viewport_rect().size
	dim.mouse_filter = Control.MOUSE_FILTER_STOP
	dim.z_index = 100
	dim.name = "pane_modal_dim"
	add_child(dim)
	var view: Vector2 = get_viewport_rect().size
	var pop := PanelContainer.new()
	pop.add_theme_stylebox_override("panel", _make_panel_style())
	pop.size = Vector2(min(view.x * 0.55, 540.0), min(view.y * 0.55, 360.0))
	pop.position = (view - pop.size) * 0.5
	pop.mouse_filter = Control.MOUSE_FILTER_STOP
	dim.add_child(pop)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 12)
	pop.add_child(vb)
	var title := Label.new()
	title.text = "  Choose one"
	title.add_theme_color_override("font_color", C_ACCENT)
	title.add_theme_font_size_override("font_size", 18)
	vb.add_child(title)
	var hint := Label.new()
	hint.text = "  The room is asking. There's no opt-out."
	hint.add_theme_color_override("font_color", Color(0.85, 0.83, 0.78, 0.7))
	hint.add_theme_font_size_override("font_size", 12)
	vb.add_child(hint)
	vb.add_child(HSeparator.new())
	for opt: Dictionary in options:
		var btn := Button.new()
		btn.text = String(opt.get("label", "(option)"))
		btn.add_theme_font_size_override("font_size", 13)
		btn.custom_minimum_size = Vector2(0, 40)
		var opt_effects: Array = opt.get("effects", [])
		btn.pressed.connect(func() -> void:
			_log_line("[color=#c8a268]→ chose:[/color] %s" % opt.get("label", ""))
			_close_pane_modal(dim)
			_resolve_effects(opt_effects)
			_render())
		vb.add_child(btn)


func _prompt_discard_cards(amount: int) -> void:
	if amount <= 0 or _hand_cards.is_empty():
		return
	# Auto-resolve if the hand is too small to choose from: discard
	# everything that's available. No modal, just a log line — the
	# player has no agency in that situation anyway.
	if _hand_cards.size() <= amount:
		var n_discarded: int = _hand_cards.size()
		var titles: PackedStringArray = []
		for cid: String in _hand_cards:
			titles.append(String(_action_cards.get(cid, {}).get("title", cid)))
		_log_line("[color=#ff8060]discarded all %d:[/color] %s" % [n_discarded, ", ".join(titles)])
		_hand_cards.clear()
		_render()
		return
	# Tear down any existing modal
	var existing: Node = get_node_or_null("pane_modal_dim")
	if existing != null and is_instance_valid(existing):
		existing.queue_free()
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.80)
	dim.top_level = true
	dim.position = Vector2.ZERO
	dim.size = get_viewport_rect().size
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
	hint.add_theme_font_size_override("normal_font_size", 12)
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
		btn.add_theme_font_size_override("font_size", 12)
		btn.custom_minimum_size = Vector2(108, 80)
		btn.tooltip_text = String(card.get("flavor", ""))
		btn.toggle_mode = true
		var art: Texture2D = _load_texture_silent(_art_path_card(cid))
		if art == null:
			art = CARD_FACE.face(cid, card, _arcana_id)
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

func _threat_clear_hint(tdef: Dictionary) -> String:
	var cb: Dictionary = tdef.get("cleared_by", {})
	var card: String = String(cb.get("card", ""))
	if card == "":
		return "(no clear path)"
	var card_def: Dictionary = _action_cards.get(card, {})
	var ctitle: String = String(card_def.get("title", card.to_upper()))
	var radius: int = int(cb.get("clear_radius", 0))
	if radius > 0:
		return "Clear by playing %s here or on an adjacent space." % ctitle
	return "Clear by playing %s here." % ctitle


func _spawn_threat(def_id: String, pos_override: String = "") -> void:
	if def_id == "" or not _threats_def.has(def_id):
		return
	var tdef: Dictionary = _threats_def[def_id]
	# Resolve position: explicit override > spawn_at_visitor > default_pos
	var pos: String = pos_override
	if pos == "":
		var src_vid: String = String(tdef.get("spawn_at_visitor", ""))
		if src_vid != "" and _visitors_state.has(src_vid) and _visitors_state[src_vid].get("arrived", false):
			pos = String(_visitors_state[src_vid].get("pos", ""))
	if pos == "":
		pos = String(tdef.get("default_pos", ""))
	if pos == "":
		return
	# One-per-(def_id, pos): the room doesn't stack identical messes.
	# If the same threat would respawn on the same space, refresh its
	# countdown instead of stacking a second copy.
	for existing: Dictionary in _threats_active:
		if existing.get("def_id", "") == def_id and existing.get("pos", "") == pos:
			existing["ticks_remaining"] = int(tdef.get("max_ticks", 99))
			_log_line("[color=#ff8060][i]· the %s lingers on (%d turns).[/i][/color]" %
				[String(tdef.get("title", def_id)).to_lower(), int(existing["ticks_remaining"])])
			return
	var tid: String = "t%d" % _threats_next_serial
	_threats_next_serial += 1
	var ticks: int = int(tdef.get("max_ticks", 99))
	_threats_active.append({"id": tid, "def_id": def_id, "pos": pos, "ticks_remaining": ticks})
	var spawn_msg: String = String(tdef.get("spawn_message", ""))
	if spawn_msg != "":
		_log_line("[color=#ff8060]✕ %s[/color] [color=#7c8398][i]%s · %d turns until it fades on its own[/i][/color]" %
			[String(tdef.get("title", def_id)), spawn_msg, ticks])
	else:
		_log_line("[color=#ff8060]✕ %s[/color] [color=#7c8398][i](%d turns)[/i][/color]" %
			[String(tdef.get("title", def_id)), ticks])
	_show_toast("Threat · [b]%s[/b]" % String(tdef.get("title", def_id)), "#ff8060")


func _clear_threats_at(pos: String, card_id: String) -> bool:
	# Returns true if at least one threat was cleared. The threat's
	# `cleared_by.card` must match `card_id`, and `pos` must be at
	# (or within `clear_radius` of) the threat's space.
	if pos == "":
		return false
	var cleared_any: bool = false
	var remaining: Array = []
	for inst: Dictionary in _threats_active:
		var tdef: Dictionary = _threats_def.get(inst.get("def_id", ""), {})
		var cb: Dictionary = tdef.get("cleared_by", {})
		var need_card: String = String(cb.get("card", ""))
		if need_card != "" and need_card != card_id:
			remaining.append(inst)
			continue
		var radius: int = int(cb.get("clear_radius", 0))
		var tpos: String = String(inst.get("pos", ""))
		if not _within_radius(pos, tpos, radius):
			remaining.append(inst)
			continue
		# Cleared.
		var msg: String = String(tdef.get("cleared_message", ""))
		if msg != "":
			_log_line("[color=#7cffb0]✓ cleared:[/color] [b]%s[/b]  [color=#7c8398][i]%s[/i][/color]" %
				[String(tdef.get("title", "threat")), msg])
		else:
			_log_line("[color=#7cffb0]✓ cleared:[/color] [b]%s[/b]" % String(tdef.get("title", "threat")))
		cleared_any = true
	_threats_active = remaining
	return cleared_any


# True if `from` is `target` or within `radius` adjacency hops of it
# (radius 0 = exact match, radius 1 = adjacent).
func _within_radius(from: String, target: String, radius: int) -> bool:
	if from == target:
		return true
	if radius <= 0:
		return false
	var adj_map: Dictionary = _location.get("adjacency", {})
	var visited: Dictionary = {from: true}
	var frontier: Array = [from]
	for _hop in range(radius):
		var next_frontier: Array = []
		for s: String in frontier:
			for nbr: String in adj_map.get(s, []):
				if nbr == target:
					return true
				if not visited.has(nbr):
					visited[nbr] = true
					next_frontier.append(nbr)
		frontier = next_frontier
	return false


# Ongoing per-Upkeep tick — every active threat applies its
# `ongoing_per_upkeep` effects, then decrements its countdown.
# When the countdown hits 0 the threat expires harmlessly.
func _tick_threats_upkeep() -> void:
	if _threats_active.is_empty():
		return
	var survivors: Array = []
	for inst: Dictionary in _threats_active:
		var tdef: Dictionary = _threats_def.get(inst.get("def_id", ""), {})
		var fx: Array = tdef.get("ongoing_per_upkeep", [])
		if not fx.is_empty():
			_log_line("[color=#ff8060][i]· %s — %s[/i][/color]" %
				[String(tdef.get("title", "threat")).to_lower(), String(tdef.get("flavor", ""))])
			_resolve_effects(fx)
		# Decrement countdown
		var tr: int = int(inst.get("ticks_remaining", 99))
		tr -= 1
		if tr <= 0:
			var em: String = String(tdef.get("expired_message", ""))
			if em != "":
				_log_line("[color=#c8a268]· %s fades.[/color] [color=#7c8398][i]%s[/i][/color]" %
					[String(tdef.get("title", "threat")), em])
			else:
				_log_line("[color=#c8a268]· %s fades.[/color]" % String(tdef.get("title", "threat")))
		else:
			inst["ticks_remaining"] = tr
			survivors.append(inst)
	_threats_active = survivors


# Faith's mess follows her — if she's moved, the wet patch went with
# her. Called from _check_composite_connections and movement code.
func _update_following_threats() -> void:
	for inst: Dictionary in _threats_active:
		var tdef: Dictionary = _threats_def.get(inst.get("def_id", ""), {})
		var follow: String = String(tdef.get("follow_visitor", ""))
		if follow == "" or not _visitors_state.has(follow):
			continue
		var new_pos: String = String(_visitors_state[follow].get("pos", ""))
		if new_pos != "" and new_pos != inst.get("pos", ""):
			inst["pos"] = new_pos


func _connect_visitor(vid: String) -> void:
	if vid == "" or not _visitors_state.has(vid):
		return
	if _visitors_state[vid].get("connected", false):
		return
	# Conditional visitors (hidden_until_arrived = true) materialise
	# at the player's current space when they connect — e.g. Anya
	# appears next to John when BUNDLE assembles with cassette spine.
	var v_def: Dictionary = _visitors_def.get(vid, {})
	if v_def.get("hidden_until_arrived", false) and not _visitors_state[vid].get("arrived", false):
		_visitors_state[vid]["arrived"] = true
		_visitors_state[vid]["pos"] = _player_pos
	_visitors_state[vid]["connected"] = true
	_visitors_state[vid]["claimed_turn"] = -1
	_connections_made.append(vid)
	# Pomegranate Hour: a connection at the sit_with step with a cast/
	# crew visitor counts toward the cast_crew_sit_with win counter.
	# Subjects-of-the-art (kind: "subject") do NOT count — they
	# fulfill a different win condition (episodes advanced).
	var v_kind: String = String(v_def.get("kind", ""))
	if v_kind == "cast_crew":
		_cast_crew_sit_with_count += 1
	elif v_kind == "subject":
		# Subjects' final lock step advances their bound episode-space
		# up one state on the ladder. The episode advances because the
		# subject was witnessed all the way through.
		var bound: String = String(v_def.get("bound_to_episode", ""))
		if bound != "":
			var new_state: String = advance_episode(bound)
			if new_state != "":
				_log_line("[color=#c8a268][i]Episode advances — %s is now %s.[/i][/color]" % [bound, new_state])
	_audio_sfx("visitor_connect")
	var v: Dictionary = _visitors_def[vid]
	var name_s: String = v.get("name", vid)
	# Headline
	_log_line("")
	_log_line("[color=#7cffb0]✓  You connect with %s.[/color]" % name_s)
	# Lore beat — the visitor's defining truth
	if v.has("lore_text"):
		_log_line("[color=#c8a268][i]%s[/i][/color]" % v["lore_text"])
	# Per-visitor narrative follow-up — the small moment between you
	# and them that the connection actually IS, not just its result.
	var beat: String = _connection_beat(vid)
	if beat != "":
		_log_line("[color=#7c8398]%s[/color]" % beat)
	# Progress note
	var total: int = _connections_made.size()
	var needed: int = int((_setup.get("win_conditions", {}) as Dictionary).get("require_visitors_connected_min", 3))
	_log_line("[color=#7c8398][i]Connections: %d / %d toward the leap.[/i][/color]" % [total, needed])
	_log_line("")
	_show_toast("Connected with [b]%s[/b]" % name_s, "#7cffb0")
	if v.has("lore_token"):
		_collect_lore_token(v["lore_token"])


# Per-visitor narrative beat that fires on connection. Each one is
# the quiet seconds AFTER the connect — what the room does, what
# they say, what John notices. Keep these to one or two sentences
# so the log doesn't bog down.
func _connection_beat(vid: String) -> String:
	match vid:
		"frasier":
			return "Frasier sets his notebook on the counter and turns it toward you. The handwriting is yours, except where it isn't. He nods, like you've finally caught up to him."
		"stranger":
			return "The Booth-Six Stranger lowers the glowing page and holds it open with one finger. Whatever you're supposed to read is there, in your hand, in 1987, in their hand, now."
		"faith":
			return "Faith presses the length of her body against your shin and stays there. Whatever you do next, she's coming."
		"dawn_cook":
			return "The Dawn Cook ties on the apron you've been wearing for eleven years. They don't look at you. You don't have to look at them. The counter is taken care of."
		"bbs_caller":
			return "The terminal scrolls a clean line of green text:  WE SEE YOU. RETURN AT YOUR DISCRETION.  The cursor blinks twice and waits."
		"anya_recording":
			return "The cassette spins one full reel. A woman's voice you almost remember says your name, dated the year before you started here."
	return ""


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
	# Contents pile (REGISTER) — draw-one-keep-or-putback. Don't
	# auto-take; show a chooser so the player commits or shuffles.
	var p_def: Dictionary = _piles_def.get(pile_id, {})
	if p_def.get("draw_one_keep_or_putback", false):
		_prompt_contents_pick(pile_id)
		return
	# Order window — only ready orders are pickable. Pending orders
	# (just spawned, bell not yet rung) stay in the pile, dim.
	var item_id: String = ""
	if pile_id == "order_window":
		for iid: String in _pile_state[pile_id]:
			if not _order_pending.get(iid, false):
				item_id = iid
				break
		if item_id == "":
			_log_line("[i]the orders here are still pending — the cook hasn't rung the bell yet.[/i]")
			return
		_pile_state[pile_id].erase(item_id)
		_order_pending.erase(item_id)
	else:
		item_id = _pile_state[pile_id].pop_front()
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
	_log_line("[color=#c8a268]✦ picked up:[/color] [b]%s[/b]" % item.get("title", item_id))
	var pf: String = String(item.get("flavor", ""))
	if pf != "":
		_log_line("[color=#7c8398][i]   %s[/i][/color]" % pf)
	var cat: String = item.get("category", "")
	if cat == "bindle_component" or cat == "bindle_contents":
		_show_toast("Picked up [b]%s[/b]" % item.get("title", item_id), "#c8a268")
	# Big art popup — feels like drawing a card in a board game. Shows
	# the item's full title, flavor, and category. Click outside / Esc
	# to dismiss.
	var item_body: String = ""
	if cat != "":
		var cat_label: String = ""
		match cat:
			"bindle_component": cat_label = "Bindle component"
			"bindle_contents":  cat_label = "Bindle contents"
			"consumable":       cat_label = "Consumable"
			"passive":          cat_label = "Passive"
			"order":            cat_label = "Order ticket"
			"order_togo":       cat_label = "TO-GO order"
			"jukebox_track":    cat_label = "Jukebox B-side"
			_:                  cat_label = cat
		item_body = "[b]%s[/b]" % cat_label
	_show_drawn_card_popup(_art_path_item(item_id), item.get("title", item_id), pf, item_body, "#c8a268")
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
	# FOCUS buff (consumed)
	if _next_roll_bonus_dice > 0:
		n_dice += _next_roll_bonus_dice
		_log_line("[color=#7cffb0][i]focus: +%d dice[/i][/color]" % _next_roll_bonus_dice)
		_next_roll_bonus_dice = 0
	# CLOSE CALL buff (consumed)
	var roll: Dictionary = {}
	var cc_mode: String = _next_roll_close_call
	_next_roll_close_call = ""
	if cc_mode == "extra_die":
		n_dice += 1
		_log_line("[color=#7cffb0][i]close call: +1 die[/i][/color]")
	if cc_mode == "double_take_best":
		var r_a: Dictionary = _roll_arcana_dice(n_dice)
		var r_b: Dictionary = _roll_arcana_dice(n_dice)
		# Take whichever result is higher (ss > s > fail)
		var rank := {"ss": 2, "s": 1, "fail": 0}
		if int(rank.get(r_a["result"], 0)) >= int(rank.get(r_b["result"], 0)):
			roll = r_a
		else:
			roll = r_b
		_log_line("[color=#7cffb0][i]close call: rolled twice, took best[/i][/color]")
	else:
		roll = _roll_arcana_dice(n_dice)
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
				"ss":
					# "Look at top 2, take 1." Peek both, player
					# chooses; the un-chosen one stays on top of the
					# pile for the next search.
					_prompt_search_choice(pile_id, 2)
				"s":
					_take_top_item_at_pos()
				"fail":
					_log_line("[i]nothing useful in reach.[/i]")
		"short_rest":
			match result:
				"ss":   _sanity = min(_sanity_max, _sanity + 2)
				"s":    _sanity = min(_sanity_max, _sanity + 1)
				"fail": pass
		"long_rest":
			match result:
				"ss":   _sanity = min(_sanity_max, _sanity + 3)
				"s":    _sanity = min(_sanity_max, _sanity + 2)
				"fail":
					_sanity = min(_sanity_max, _sanity + 1)
					_time = max(0, _time - 1)
		"focus":
			# Bonus dice on the NEXT framework card's roll, plus a Time
			# bump on ★★. Reduces Threshold roll cost = makes the next
			# roll more reliable (more dice = better odds of success).
			match result:
				"ss":
					_next_roll_bonus_dice = 2
					_time += 1
					_log_line("[color=#7cffb0]✦ FOCUS: +2 dice on next roll, +1 Time[/color]")
				"s":
					_next_roll_bonus_dice = 1
					_log_line("[color=#7cffb0]✦ FOCUS: +1 die on next roll[/color]")
				"fail":
					pass
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
			# CLOSE CALL ★★: next framework card rolls twice, takes
			# the better result. ★: next framework card gets +1 die.
			# ✕: no effect. (Buff state consumed in _resolve_framework_card.)
			match result:
				"ss":
					_next_roll_close_call = "double_take_best"
					_log_line("[color=#7cffb0]✦ CLOSE CALL: next roll will double + take best[/color]")
				"s":
					_next_roll_close_call = "extra_die"
					_log_line("[color=#7cffb0]✦ CLOSE CALL: next roll gets +1 die[/color]")
				"fail":
					pass
		"spend_it":
			_time += 1
			_log_line("[color=#7cffb0]✦ SPEND IT: +1 Time[/color]  (Time → %d)" % _time)
		"improvise":
			# IMPROVISE ★★: replay the last-played card's effects.
			# ★: replay only its mechanical outcome at this roll.
			# ✕: +1 Inertia (the room notices you're spinning).
			if _last_played_cid == "":
				_log_line("[i]nothing to improvise — no card played yet this turn[/i]")
			else:
				var last_card: Dictionary = _action_cards.get(_last_played_cid, {})
				var lname: String = last_card.get("title", _last_played_cid)
				match result:
					"ss":
						_log_line("[color=#7cffb0]✦ IMPROVISE: replaying [b]%s[/b][/color]" % lname)
						_resolve_effects(last_card.get("effects", []))
						# Framework re-resolve too (skips re-rolling
						# infinitely by short-circuiting the improvise
						# itself: only replay if last wasn't improvise)
						if _last_played_cid != "improvise" and last_card.has("double_success"):
							_apply_framework_card_mechanic(_last_played_cid, "s")
					"s":
						_log_line("[color=#7cffb0]✦ IMPROVISE: shadow of [b]%s[/b][/color]" % lname)
						if last_card.has("double_success"):
							_apply_framework_card_mechanic(_last_played_cid, "s")
					"fail":
						_inertia = min(12, _inertia + 1)


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
	# Autosave at the END of each phase before transitioning. The
	# save then captures the state the player would resume into
	# (i.e., the start of the next phase). Cheap — single small JSON
	# blob.
	_write_gauntlet_save()
	match _phase:
		Phase.ACTION:
			_phase = Phase.PLANNING
			_show_phase_banner("PLANNING — buy cards · Time refreshes")
			_phase_planning()
		Phase.PLANNING:
			_phase = Phase.SHADOW
			_show_phase_banner("SHADOW — the room takes its turn")
			_phase_shadow()
		Phase.SHADOW:
			_phase = Phase.DRIFT
			_show_phase_banner("DRIFT — visitors drift toward attractors")
			_phase_drift()
		Phase.DRIFT:
			_phase = Phase.UPKEEP
			_show_phase_banner("UPKEEP — cleanup")
			_phase_upkeep()
		Phase.UPKEEP:
			_phase = Phase.ACTION
			_show_phase_banner("──  TURN %d  ── ACTION" % (_turn + 1))
			_phase_action()
	_render()


# Phase transition banner — slides in from the top center, fades out
# after 1.4s. Gives the player a clear "we just moved phases" beat
# without forcing them to read the small phase label.
func _show_phase_banner(text: String) -> void:
	var view: Vector2 = get_viewport_rect().size
	var pop := PanelContainer.new()
	pop.add_theme_stylebox_override("panel", _make_panel_style())
	pop.z_index = 90   # below modals (100) but above everything else
	pop.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(pop)
	var lbl := Label.new()
	lbl.text = "  " + text + "  "
	lbl.add_theme_color_override("font_color", C_ACCENT)
	lbl.add_theme_font_size_override("font_size", 16)
	pop.add_child(lbl)
	await get_tree().process_frame
	pop.position = Vector2((view.x - pop.size.x) * 0.5, 50.0)
	pop.modulate = Color(1, 1, 1, 0)
	var t := create_tween()
	t.tween_property(pop, "modulate:a", 1.0, 0.16).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	t.tween_interval(1.2)
	t.tween_property(pop, "modulate:a", 0.0, 0.35).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	t.tween_callback(pop.queue_free)


func _phase_action() -> void:
	# Start of new turn — increment, reset played-this-turn
	_turn += 1
	_played_this_turn.clear()
	# Reset per-turn Gravity modifiers + framework-card buffs
	_this_turn_cost_bump_min = 99
	_this_turn_cost_bump_amt = 0
	_next_roll_bonus_dice = 0
	_next_roll_close_call = ""
	_last_played_cid = ""
	# Per-scenario baseline inertia tick (per-turn). Default 1.
	# Setup JSON's starting_state.inertia_per_turn overrides.
	# _room_attention adds an extra +1 per gravity-deck recycle.
	var tick: int = int((_setup.get("starting_state", {}) as Dictionary).get("inertia_per_turn", 1))
	tick += _room_attention
	if tick > 0:
		_inertia = min(12, _inertia + tick)
	# Magician arcana: stagnation ticks per turn the same way
	# inertia does. Triggers loss at stagnation_max (default 12).
	if _stagnation_per_turn > 0:
		_stagnation += _stagnation_per_turn
		var s_max: int = int(_setup.get("loss_conditions", {}).get("stagnation_max", 12))
		if _stagnation >= s_max:
			_log_line("[color=#ff5040][b]Stagnation at max. The maker forgets the make.[/b][/color]")
			_trigger_loss("stagnation_max")
			return
	# Active demons tick down their durations.
	for did in _active_demons.keys():
		var left: int = int(_active_demons[did]) - 1
		if left <= 0:
			_active_demons.erase(did)
		else:
			_active_demons[did] = left
	# Patience freeze counter ticks down by 1 each upkeep.
	if _patience_frozen_turns > 0:
		_patience_frozen_turns -= 1
	# Patched-space pairs tick down + expire.
	var still_patched: Array = []
	for p in _patched_pairs:
		var pd: Dictionary = p
		var left_t: int = int(pd.get("turns", 0)) - 1
		if left_t > 0:
			pd["turns"] = left_t
			still_patched.append(pd)
		else:
			_log_line("[i]· patch %s ↔ %s released.[/i]" %
				[String(pd.get("a","?")).to_upper(), String(pd.get("b","?")).to_upper()])
	_patched_pairs = still_patched
	# BLOW OUT — the river-takes-the-bank loss trigger. Scenario
	# declares `river_takes_the_bank_after_turn: N`. From turn N+1
	# onward, if the cake hasn't been lit, the river caves the
	# bank and the run ends.
	var river_trigger: int = int(_setup.get("loss_conditions", {}).get("river_takes_the_bank_after_turn", 0))
	if river_trigger > 0 and _turn > river_trigger and not _flags.get("cake_lit", false):
		_log_line("\n[color=#ff5040][b]The river takes the bank.[/b][/color]")
		_log_line("[color=#7c8398][i]a sound like a building giving up. you don't get the candles lit. the room ends with the water in it.[/i][/color]")
		_trigger_loss("river_takes_the_bank")
		return
	# Time-of-day deadline. Each scenario's setup may declare
	# `max_turns`; on turn N+1 the shift ends and the engine forces
	# a win-check. THE LEAP: 14 turns by default. RUSH: 10. EVENING: 12.
	var max_turns: int = int(_setup.get("max_turns", 14))
	if _turn > max_turns:
		_log_line("\n[color=#ff8060][b]── the shift is over ──[/b][/color]")
		_force_end_of_shift_check()
		return
	_log_line("\n[color=#c8a268][b]── turn %d / %d ──[/b][/color]" % [_turn, max_turns])
	# Visitor arrivals scheduled for this turn
	var arrivals_this_turn: Array = []
	for vid in _visitors_state:
		var st: Dictionary = _visitors_state[vid]
		if not st.get("arrived", false) and st.has("scheduled_turn"):
			if int(st["scheduled_turn"]) <= _turn:
				st["arrived"] = true
				st["arrived_turn"] = _turn
				st["pos"] = st.get("arrival_pos", "counter")
				var name_s: String = _visitors_def.get(vid, {}).get("name", vid)
				_log_line("[i]→ %s arrives at %s[/i]" % [name_s, st["pos"]])
				arrivals_this_turn.append(vid)
	# Pop a modal for each arrival so the player sees their face. The
	# popup is z=110 (above the gauntlet UI), dismissible via the
	# Acknowledge button, Esc, or clicking outside. If multiple
	# visitors arrive in the same turn, queue them so each shows in
	# turn — _show_visitor_arrival_popup tears down its predecessor.
	for vid in arrivals_this_turn:
		_visitor_arrival_queue.append(vid)
	call_deferred("_show_next_visitor_arrival")


# TO-GO auto-deliver — when the player walks to the order's
# deliver_to_pos with the order in inventory, the order fires its
# reward and is consumed. Called from _on_space_clicked and
# _prompt_pick_destination after the position updates.
func _check_togo_deliveries() -> void:
	if _inventory.is_empty():
		return
	for iid: String in _inventory.duplicate():
		var idef: Dictionary = _items_def.get(iid, {})
		var to_pos: String = String(idef.get("deliver_to_pos", ""))
		if to_pos == "":
			continue
		if to_pos != _player_pos:
			continue
		var ititle: String = String(idef.get("title", iid))
		_inventory.erase(iid)
		_audio_sfx("item_pickup")
		_log_line("[color=#7cffb0]✦ delivered:[/color] [b]%s[/b]" % ititle)
		_log_line("[color=#7c8398][i]   A figure steps out of an idling truck and takes the paper bag. They tip their hat. The truck pulls away.[/i][/color]")
		var reward: Dictionary = idef.get("deliver_reward", {})
		if reward.has("gain_time"):
			_time += int(reward["gain_time"])
		if reward.has("lose_inertia"):
			_inertia = max(0, _inertia - int(reward["lose_inertia"]))
		if reward.has("lore_token"):
			_collect_lore_token(String(reward["lore_token"]))
		# Counts toward the lunch/evening "orders delivered" win
		# threshold, same as a dine-in deliver.
		_flags["orders_delivered"] = int(_flags.get("orders_delivered", 0)) + 1
		_show_toast("Delivered [b]%s[/b]" % ititle, "#7cffb0")


func _phase_planning() -> void:
	# Free reset of starters back into hand if they were played
	for cid: String in _action_cards.keys():
		var card: Dictionary = _action_cards[cid]
		if card.get("starter", false) and not (cid in _hand_cards):
			_hand_cards.append(cid)
	# THE LEAP economy: time REFRESHES each turn — leftover Time
	# does not carry. The tightness is the point; the 24-hour diner
	# of the soul doesn't bank minutes for you. Modifiers and
	# special effects can still set _next_time_reset for a specific
	# turn (e.g. THE CLOCK HOLDS → 5).
	_time = _next_time_reset
	_next_time_reset = int((_setup.get("starting_state", {}) as Dictionary).get("time_per_turn", 6))
	# If the Bindle has been assembled but LEAP isn't in hand yet,
	# add it now. (LEAP is awarded by BUNDLE, never purchased.)
	if _bindle_assembled and not ("leap" in _hand_cards):
		_hand_cards.append("leap")
		_log_line("[color=#ffd07a][b]LEAP added to your hand.[/b][/color]")
	_log_line("[color=#c8a268][i]planning. Time refreshed to %d. Click TABLEAU cards (above hand) to buy.[/i][/color]" % _time)


func _phase_shadow() -> void:
	var cid: String = _draw_gravity_card()
	if cid == "":
		_log_line("[i]gravity deck empty — the room has run out of new ways to press on you.[/i]")
		return
	# Magician's BURN card sets _next_gravity_canceled; consume it
	# here so the card is drawn (discarded) but resolves no effects.
	if _next_gravity_canceled:
		_next_gravity_canceled = false
		var card_c: Dictionary = _find_gravity_card(cid)
		_log_line("[color=#7cffb0]✓ canceled by BURN:[/color] [b]%s[/b]" % card_c.get("title", cid))
		return
	_audio_sfx("gravity_draw")
	var card: Dictionary = _find_gravity_card(cid)
	_gravity_last_drawn = card
	_log_line("[color=#ff8060][b]GRAVITY:[/b] %s[/color]" % card.get("title", cid))
	_log_line("[i]%s[/i]" % card.get("flavor", ""))
	_gravity_card_label.text = "[color=#c8a268]GRAVITY[/color]\n[b]%s[/b]\n[i]%s[/i]" % [card.get("title", cid), card.get("flavor","")]
	# Big art popup — gives the destiny card cinematic weight before
	# its effects resolve onto the player.
	var grav_body: String = ""
	var g_effs: Array = card.get("effects", [])
	if not g_effs.is_empty():
		var lines: PackedStringArray = ["[b]The room does:[/b]"]
		for e: Dictionary in g_effs:
			lines.append("  · " + _describe_effect(e))
		grav_body = "\n".join(lines)
	_show_drawn_card_popup(_art_path_gravity(cid), card.get("title", cid), card.get("flavor", ""), grav_body, "#ff8060")
	_resolve_effects(card.get("effects", []))
	# Inertia ≥ 7: extra draw per the inertia thresholds spec
	if _inertia >= 7:
		var cid2: String = _draw_gravity_card()
		if cid2 != "":
			var card2: Dictionary = _find_gravity_card(cid2)
			_log_line("[color=#ff8060][b]GRAVITY (bonus):[/b] %s[/color]" % card2.get("title", cid2))
			_resolve_effects(card2.get("effects", []))


# Pull one Gravity card. Cycles through draw → discard. When the
# draw pile empties, anything in the discard whose effect is still
# in play (active threat, set flag, revealed threshold, collected
# lore token) is EXHAUSTED — held out of the reshuffle so the room
# doesn't get to throw the same hook at you twice. The held cards
# remain in the discard and re-evaluate every reshuffle, so once
# you clear a threat the card returns to the rotation.
func _draw_gravity_card() -> String:
	if _gravity_draw_pile.is_empty():
		_reshuffle_gravity_discard()
	if _gravity_draw_pile.is_empty():
		return ""
	var cid: String = _gravity_draw_pile.pop_back()
	_gravity_discard_pile.append(cid)
	return cid


func _reshuffle_gravity_discard() -> void:
	if _gravity_discard_pile.is_empty():
		return
	var returning: Array = []
	var staying_out: Array = []
	for cid: String in _gravity_discard_pile:
		if _gravity_card_effect_in_play(cid):
			staying_out.append(cid)
		else:
			returning.append(cid)
	_gravity_discard_pile = staying_out
	if returning.is_empty():
		return
	# Endgame-flagged cards reshuffle to the BOTTOM (same rule as the
	# initial deck build) so they keep their late-game role.
	var endgame_ids: Array = []
	var normal_ids: Array = []
	for cid: String in returning:
		var c: Dictionary = _find_gravity_card(cid)
		if c.get("endgame", false):
			endgame_ids.append(cid)
		else:
			normal_ids.append(cid)
	normal_ids.shuffle()
	endgame_ids.shuffle()
	_gravity_draw_pile = []
	for cid: String in endgame_ids:
		_gravity_draw_pile.append(cid)
	for cid: String in normal_ids:
		_gravity_draw_pile.append(cid)
	if staying_out.is_empty():
		_log_line("[color=#c8a268][i]· the deck reshuffles. %d cards back into the room's hand.[/i][/color]" % returning.size())
	else:
		_log_line("[color=#c8a268][i]· the deck reshuffles. %d return; %d still in play and stay out.[/i][/color]" %
			[returning.size(), staying_out.size()])
	# Escalation: the room has now seen John for one full cycle. It's
	# paying more attention. Each recycle adds 1 to the per-turn
	# Inertia tick, telegraphed as "the room learns you."
	_gravity_recycle_count += 1
	_room_attention += 1
	_log_line("[color=#ff8060][b]» the room learns you ·[/b][/color] [color=#ff8060]+1 Inertia/turn[/color] [color=#7c8398](attention = %d)[/color]" % _room_attention)
	_show_toast("The room is paying more attention", "#ff8060")


# Does this Gravity card have an effect that's still active right
# now? Used by the reshuffle to decide what stays exhausted.
func _gravity_card_effect_in_play(cid: String) -> bool:
	var card: Dictionary = _find_gravity_card(cid)
	for e: Dictionary in card.get("effects", []):
		if _gravity_effect_in_play(e):
			return true
	return false


func _gravity_effect_in_play(e: Dictionary) -> bool:
	match String(e.get("kind", "")):
		"spawn_threat":
			var tid: String = String(e.get("threat_id", ""))
			for inst: Dictionary in _threats_active:
				if String(inst.get("def_id", "")) == tid:
					return true
			return false
		"set_flag":
			# Truthy-evaluating flag value. Most set_flag effects flip a
			# bool to true and never flip it back; this also treats any
			# non-empty string as "still in play."
			var k: String = String(e.get("key", ""))
			var cur = _flags.get(k, null)
			if cur == null: return false
			if cur is bool: return cur
			if cur is int: return cur != 0
			if cur is String: return cur != ""
			return true
		"reveal_threshold":
			# Once revealed it stays revealed — the door doesn't un-
			# appear. Card is exhausted for the rest of the game.
			return _flags.get(String(e.get("threshold", "")) + "_revealed", false) \
				or _flags.get("precipice_revealed", false)
		"reveal_lore_token":
			var tok: String = String(e.get("token", ""))
			return tok in _lore_tokens_collected
		_:
			return false


func _find_gravity_card(cid: String) -> Dictionary:
	for c: Dictionary in _gravity_deck_def.get("cards", []):
		if c.get("id", "") == cid:
			return c
	return {}


func _phase_drift() -> void:
	# Visitors who aren't connected and aren't claimed drift one hop
	# toward the location's drift_attractors. BFS finds the next hop
	# along the shortest path; tie-breaks pick the FIRST attractor
	# listed (primary > secondary > tertiary).
	_run_drift()
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
				var nm: String = _visitors_def.get(vid, {}).get("name", vid)
				_log_line("")
				_log_line("[color=#ff6060]✕ %s consumed by the room.[/color]" % nm)
				_log_line("[color=#7c8398][i]   The booth empties. The chair settles. Like nobody was ever sitting in it.[/i][/color]")
				_show_toast("[b]%s[/b] consumed by the room" % nm, "#ff6060")
	# Counter-haunted flag: standing on COUNTER adds +1 Inertia
	if _counter_haunted and _player_pos == "counter":
		_inertia = min(12, _inertia + 1)
		_log_line("[color=#ff8060]+1 Inertia (counter is calling)[/color]")


# Faith follow — if she was at the player's previous space (or has
# been connected), she walks to the player's new space too. Keeps
# the LEAP win condition (Faith adjacent) realistic without forcing
# you to re-call her every turn.
func _faith_follow(prev_pos: String) -> void:
	var st: Dictionary = _visitors_state.get("faith", {})
	if not st.get("arrived", false):
		return
	# Only follow if she was at the prev pos OR has been connected
	# (after that, she's yours)
	if String(st.get("pos", "")) != prev_pos and not st.get("connected", false):
		return
	st["pos"] = _player_pos
	_log_line("[color=#7c8398][i]   Faith follows.[/i][/color]")


# Drift mechanic — every unconnected, unclaimed visitor moves one
# hop closer to a drift attractor space. Faith doesn't drift (she
# stays with John once called). Once a visitor reaches an attractor,
# they wait there until claimed or connected. Adds atmosphere AND
# pressure: visitors you ignored start leaving the spaces where you
# could connect with them.
func _run_drift() -> void:
	var attractors_def: Dictionary = _location.get("drift_attractors", {})
	if attractors_def.is_empty():
		return
	var attractor_priorities: PackedStringArray = []
	for key in ["primary", "secondary", "tertiary"]:
		var aid: String = String(attractors_def.get(key, ""))
		if aid != "":
			attractor_priorities.append(aid)
	if attractor_priorities.is_empty():
		return
	var adj_map: Dictionary = _location.get("adjacency", {})
	var any_moved: bool = false
	for vid in _visitors_state:
		var st: Dictionary = _visitors_state[vid]
		if vid == "faith":
			continue   # Faith follows John, not the room
		if not st.get("arrived", false):
			continue
		if st.get("connected", false):
			continue
		if int(st.get("claimed_turn", -1)) >= 0:
			continue
		# Engaged (player has already greeted / listened / delivered)
		# visitors don't drift — they wait for you to come back.
		if int(st.get("progress", 0)) > 0:
			continue
		var cur: String = String(st.get("pos", ""))
		if cur == "":
			continue
		# Already at an attractor — they wait
		if cur in attractor_priorities:
			continue
		# BFS toward the highest-priority attractor, take the first hop
		var next_hop: String = _bfs_next_hop(cur, attractor_priorities, adj_map)
		if next_hop == "" or next_hop == cur:
			continue
		st["pos"] = next_hop
		var nm: String = _visitors_def.get(vid, {}).get("name", vid)
		_log_line("[color=#7c8398][i]· %s drifts toward %s.[/i][/color]" % [nm, next_hop.replace("_", " ")])
		any_moved = true
	if any_moved:
		_render()


# BFS from `start`, return the first hop along the shortest path
# toward ANY of the target ids. Empty string if no path or already
# at a target.
func _bfs_next_hop(start: String, targets: PackedStringArray, adj_map: Dictionary) -> String:
	if start in targets:
		return ""
	var prev: Dictionary = {start: ""}
	var queue: Array = [start]
	var found: String = ""
	while not queue.is_empty():
		var cur: String = queue.pop_front()
		if cur in targets:
			found = cur
			break
		for nbr: String in adj_map.get(cur, []):
			if prev.has(nbr):
				continue
			if nbr == "precipice_door" and not _flags.get("precipice_revealed", false):
				continue
			prev[nbr] = cur
			queue.append(nbr)
	if found == "":
		return ""
	# Walk back to find the first hop
	var node: String = found
	while String(prev.get(node, "")) != start:
		node = prev[node]
		if node == "":
			return ""
	return node


func _place_claim_marker(skip_first: bool) -> void:
	# Closest unconnected, unclaimed visitor on the board. Helpers
	# (bus kid, line cook) are exempt — they're staff, not patrons.
	var candidates: Array = []
	for vid in _visitors_state:
		var st: Dictionary = _visitors_state[vid]
		var vdef: Dictionary = _visitors_def.get(vid, {})
		if vdef.get("helper", false): continue
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
	# Order window: how many pending orders ripen per Upkeep depends
	# on whether the LINE COOK helper is on the board. Without him,
	# the cook is John's responsibility — one bell per Upkeep. With
	# him, every pending order ripens (he's on the line cooking AND
	# ringing). Lunch + Evening scenarios put him on the grill at
	# start, so the bell keeps up with the room.
	var pile_ow: Array = _pile_state.get("order_window", [])
	var cook_st: Dictionary = _visitors_state.get("line_cook", {})
	var cook_present: bool = cook_st.get("arrived", false)
	var rang_one: bool = false
	for iid: String in pile_ow:
		if not _order_pending.get(iid, false):
			continue
		_order_pending[iid] = false
		var ititle_ow: String = String(_items_def.get(iid, {}).get("title", iid))
		if cook_present:
			_log_line("[color=#c8a268][i]   Bell. The line cook calls back: %s up.[/i][/color]" % ititle_ow)
		else:
			_log_line("[color=#c8a268][i]   Bell. The cook's pass-the-window ring. %s ready.[/i][/color]" % ititle_ow)
		_show_toast("Bell · [b]%s[/b] ready" % ititle_ow, "#c8a268")
		rang_one = true
		if not cook_present:
			break
	# Bus Kid helper: if on the board, decrement the countdown of
	# threats at adjacent spaces by 1 extra tick (or clear them if
	# already at 1). Caps at one threat cleared per Upkeep so it
	# doesn't trivialize a busy room.
	var kid_st: Dictionary = _visitors_state.get("bus_kid", {})
	if kid_st.get("arrived", false) and not _threats_active.is_empty():
		var kid_pos: String = String(kid_st.get("pos", ""))
		var adj_kid: Array = _location.get("adjacency", {}).get(kid_pos, [])
		adj_kid = adj_kid.duplicate()
		adj_kid.append(kid_pos)
		var helped: bool = false
		for inst: Dictionary in _threats_active:
			if helped: break
			var tpos: String = String(inst.get("pos", ""))
			if not (tpos in adj_kid): continue
			var tr: int = int(inst.get("ticks_remaining", 0))
			inst["ticks_remaining"] = max(0, tr - 1)
			var tdef_h: Dictionary = _threats_def.get(inst.get("def_id", ""), {})
			_log_line("[color=#7cffb0][i]   The bus kid catches the %s. (-1 tick)[/i][/color]" %
				String(tdef_h.get("title", "threat")).to_lower())
			helped = true
	# Faith adjacent → −1 Inertia
	var faith_st: Dictionary = _visitors_state.get("faith", {})
	if faith_st.get("arrived", false) and faith_st.get("pos", "") == _player_pos:
		_inertia = max(0, _inertia - 1)
		_log_line("[color=#7cffb0]Faith steady · -1 Inertia[/color]")
	# Threat pieces tick during UPKEEP.
	_tick_threats_upkeep()
	# Atmosphere — one ambient pool beat (every N turns), one log
	# per active demon. Quiet on turns with no demons + nothing
	# due in the pool.
	_log_ambient_beat_if_due()
	_log_demon_ambient_beats()
	# Mood-gated visitor patience. A visitor still at progress 0
	# (never greeted) for `patience` turns since arrival stands up
	# and leaves — counts as a self-claim. Helpers, Faith, and the
	# stranger (whose connect path is composite) are exempt.
	_tick_visitor_patience()
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

func _tick_visitor_patience() -> void:
	# THE LONG QUIET / freeze_patience — skip the whole tick while
	# the freeze counter is positive. Counter is decremented in the
	# upkeep step that calls us.
	if _patience_frozen_turns > 0:
		_log_line("[color=#a8e89c][i]the long quiet holds. nobody is checking the time.[/i][/color]")
		return
	# Each Upkeep: for any visitor who's arrived, unconnected, not
	# already claimed, has helper:false, has no special connect_via,
	# and is still at progress 0 — count turns since arrival. If we
	# hit their patience limit they stand up and leave (self-claim).
	for vid in _visitors_state:
		var st: Dictionary = _visitors_state[vid]
		if not st.get("arrived", false): continue
		if st.get("connected", false): continue
		if int(st.get("claimed_turn", -1)) >= 0: continue
		if int(st.get("progress", 0)) > 0: continue
		var vdef: Dictionary = _visitors_def.get(vid, {})
		if vdef.get("helper", false): continue
		if vid == "faith": continue
		# Visitors with a composite/auto connect path don't need
		# the waiter sequence at all — they wait on their own
		# rules and shouldn't time out on patience.
		var cv: Dictionary = vdef.get("connect_via", {})
		if not cv.is_empty(): continue
		var patience: int = int(vdef.get("patience",
			PATIENCE_BY_MOOD.get(String(vdef.get("mood", "preoccupied")), 6)))
		# The Twins (and any future paired visitors with
		# `shared_patience: true`) effectively double their patience —
		# they're two figures with one timer, so they wait longer
		# before "standing up" together. Matches the design intent
		# of the visitors.json entry.
		if bool(vdef.get("shared_patience", false)):
			patience = patience * 2
		var arrived_turn: int = int(st.get("arrived_turn", 1))
		var elapsed: int = _turn - arrived_turn
		var remaining: int = patience - elapsed
		# Telegraph at 2 turns out and 1 turn out so the player
		# can triage.
		if remaining == 2:
			_log_line("[color=#ff8060][i]· %s is checking the time.[/i][/color]" %
				_visitors_def.get(vid, {}).get("name", vid))
		elif remaining == 1:
			_log_line("[color=#ff8060][i]· %s is gathering their things.[/i][/color]" %
				_visitors_def.get(vid, {}).get("name", vid))
		elif remaining <= 0:
			st["claimed_turn"] = _turn
			st["walked_off"] = true
			_claimed_visitors_count += 1
			_log_line("[color=#ff5040][b]✕ %s walks out without being greeted.[/b][/color]" %
				_visitors_def.get(vid, {}).get("name", vid))
			_show_toast("%s walked out" % _visitors_def.get(vid, {}).get("name", vid), "#ff5040")


# Force a win-check at end of shift (time-of-day deadline). If the
# scenario's win conditions are met right now, trigger the win. If
# not, trigger a loss with reason "shift_over".
func _force_end_of_shift_check() -> void:
	if _game_over:
		return
	# Reuse the same predicate the LEAP card uses but without
	# requiring a threshold. Different scenarios have different
	# win shapes, so check by scenario.
	var wc: Dictionary = _setup.get("win_conditions", {})
	var connected_count: int = _connections_made.size()
	var need_connected: int = int(wc.get("require_visitors_connected_min", 3))
	# Orders served (lunch/evening only)
	var orders_served: int = int(_flags.get("orders_delivered", 0))
	var need_orders: int = int(wc.get("require_orders_delivered_min", 0))
	# Inertia ceiling
	var max_inertia: int = int(wc.get("require_inertia_below", 99))
	var meets: bool = (connected_count >= need_connected
		and orders_served >= need_orders
		and _inertia < max_inertia)
	if meets:
		_log_line("[color=#7cffb0][b]· you made it to closing. The shift holds.[/b][/color]")
		_trigger_win("shift_end")
	else:
		_log_line("[color=#ff5040][b]· the shift ends with you behind.[/b][/color]")
		_trigger_loss("shift_over")


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


# ── World-state loader ───────────────────────────────────────────
# Reads res://resources/world_state.json on _init_run and filters to
# states whose save_key is unlocked. Active states append ambient
# lines into _world_state_ambient_lines (read by the ambient beat)
# and append gravity_extras to _gravity_deck_def["cards"] BEFORE
# the deck is shuffled.
const _WORLD_STATE_PATH := "res://resources/world_state.json"
func _load_world_state() -> void:
	_world_state_ambient_lines.clear()
	_world_state_active_ids.clear()
	if not FileAccess.file_exists(_WORLD_STATE_PATH):
		return
	var f := FileAccess.open(_WORLD_STATE_PATH, FileAccess.READ)
	if f == null:
		return
	var parsed = JSON.parse_string(f.get_as_text())
	if not (parsed is Dictionary):
		return
	var states: Array = (parsed as Dictionary).get("states", [])
	var extras_appended: int = 0
	for s_v in states:
		var s: Dictionary = s_v
		var key: String = String(s.get("save_key", ""))
		if key == "" or not SaveSystem.is_unlocked(key):
			continue
		_world_state_active_ids.append(String(s.get("id", "")))
		# Ambient lines
		for ln_v in s.get("ambient_lines", []):
			_world_state_ambient_lines.append(String(ln_v))
		# Gravity extras — append to the active deck's cards array.
		# Each entry needs an id, title, flavor, effects — same shape
		# as a normal gravity card. The card is treated as non-
		# endgame (no `endgame` flag).
		var gex: Array = s.get("gravity_extras", [])
		if not gex.is_empty():
			var current_cards: Array = _gravity_deck_def.get("cards", [])
			for ge_v in gex:
				current_cards.append(ge_v)
				extras_appended += 1
			_gravity_deck_def["cards"] = current_cards
	if not _world_state_active_ids.is_empty():
		print("[Gauntlet] world state active: %s (+%d gravity extras)" %
			[", ".join(_world_state_active_ids), extras_appended])


# ── Achievement evaluator ────────────────────────────────────────
# Reads res://resources/achievements.json on every win/loss and
# evaluates each entry's trigger against the current run state.
# Newly-satisfied achievements fire SaveSystem.mark_unlocked() and any
# declared reward (also a mark_unlocked). Idempotent — already-unlocked
# entries skip silently.
const _ACHIEVEMENTS_PATH := "res://resources/achievements.json"
var _achievements_cache: Array = []
func _load_achievements_if_needed() -> void:
	if not _achievements_cache.is_empty():
		return
	if not FileAccess.file_exists(_ACHIEVEMENTS_PATH):
		return
	var f := FileAccess.open(_ACHIEVEMENTS_PATH, FileAccess.READ)
	if f == null:
		return
	var parsed = JSON.parse_string(f.get_as_text())
	if parsed is Dictionary:
		_achievements_cache = (parsed as Dictionary).get("achievements", [])

func _evaluate_achievements(outcome: String, finale_id: String) -> void:
	_load_achievements_if_needed()
	if _achievements_cache.is_empty():
		return
	for entry_v in _achievements_cache:
		var entry: Dictionary = entry_v
		var unlock_key: String = String(entry.get("unlock_key", ""))
		if unlock_key == "":
			continue
		if SaveSystem.is_unlocked(unlock_key):
			continue
		var trigger: Dictionary = entry.get("trigger", {})
		if not _achievement_trigger_fires(trigger, outcome, finale_id):
			continue
		# Newly satisfied — mark + reward + log.
		SaveSystem.mark_unlocked(unlock_key)
		var reward: Dictionary = entry.get("reward", {})
		if reward.get("kind", "") == "unlock":
			SaveSystem.mark_unlocked(String(reward.get("key", "")))
		var t_title: String = String(entry.get("title", entry.get("id", "?")))
		_log_line("[color=#ffd896][b]✦ achievement: %s[/b][/color]" % t_title)
		_show_toast("✦ %s" % t_title, "#ffd896")

func _achievement_trigger_fires(trigger: Dictionary, outcome: String, finale_id: String) -> bool:
	var kind: String = String(trigger.get("kind", ""))
	match kind:
		"any_win":
			return outcome == "win"
		"any_loss":
			return outcome == "loss"
		"all_scenarios":
			# Every scenario in the list must be marked
			# unlocked:scenario:<arcana>:<id>.
			var arc: String = String(trigger.get("arcana", ""))
			var scs: Array = trigger.get("scenarios", [])
			# The CURRENT win counts even before SaveSystem fully
			# flushes — so we check arcana+scenario_id against the
			# run we just finished too.
			for sid_v in scs:
				var sid: String = String(sid_v)
				var key: String = "unlocked:scenario:%s:%s" % [arc, sid]
				if outcome == "win" and arc == _arcana_id and sid == _scenario_id:
					continue
				if not SaveSystem.is_unlocked(key):
					return false
			return true
		"any_win_per_arcana":
			var arcs: Array = trigger.get("arcanas", [])
			var min_count: int = int(trigger.get("min", arcs.size()))
			var hit: int = 0
			for arc_v in arcs:
				var ak: String = "milestone:gauntlet_win:" + String(arc_v)
				if SaveSystem.is_unlocked(ak):
					hit += 1
				elif outcome == "win" and String(arc_v) == _arcana_id:
					hit += 1
			return hit >= min_count
		"win_with_metric":
			if outcome != "win":
				return false
			var metric: String = String(trigger.get("metric", ""))
			var op: String = String(trigger.get("op", "=="))
			var target: int = int(trigger.get("value", 0))
			var measured: int = _achievement_metric(metric)
			return _achievement_compare(measured, op, target)
		"loss_with_finale_id":
			return outcome == "loss" and finale_id == String(trigger.get("finale_id", ""))
		"flag_during_run":
			var flag_key: String = String(trigger.get("flag", ""))
			# Support "lore_token:foo" — fires when token foo was
			# collected during this run.
			if flag_key.begins_with("lore_token:"):
				var tok: String = flag_key.substr("lore_token:".length())
				return tok in _lore_tokens_collected
			return bool(_flags.get(flag_key, false))
		"card_played_during_run":
			return int(_cards_played_this_run.get(String(trigger.get("card", "")), 0)) > 0
		"lovers_synced_leap":
			return outcome == "win" and _arcana_id == "lovers" and bool(_flags.get("lovers_synced_leap", false))
	return false

func _achievement_metric(metric: String) -> int:
	match metric:
		"doubt": return _doubt
		"stagnation": return _stagnation
		"visitors_claimed": return _claimed_visitors_count
		"active_demons": return _active_demons.size()
		"connections": return _connections_made.size()
		"episodes_advanced": return _episodes_advanced_this_run
		"cast_crew_sit_with": return _cast_crew_sit_with_count
		"master_reel": return _master_reel
		"sync": return _sync
		"miles": return _miles
		"bloom": return _bloom
		"ledger": return _ledger
		"signal": return _signal
		"insight": return _insight
		"harvest": return _harvest
		"authority": return _authority
		"doctrine": return _doctrine
		"verb": return _verb
		"fuel": return _fuel
	return 0

func _achievement_compare(a: int, op: String, b: int) -> bool:
	match op:
		"==": return a == b
		"!=": return a != b
		"<":  return a <  b
		"<=": return a <= b
		">":  return a >  b
		">=": return a >= b
	return false


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
	# Milestones — gauntlet_win unlocks the Cathedral of Rust skin
	# + Cathedral Drift visualizer + "The Leap (won)" BGM. Per-arcana
	# variant lets later content gate on a specific arcana win.
	SaveSystem.mark_unlocked("milestone:gauntlet_win")
	SaveSystem.mark_unlocked("milestone:gauntlet_win:" + _arcana_id)
	SaveSystem.mark_unlocked("unlocked:scenario:%s:%s" % [_arcana_id, _scenario_id])
	if _bindle_assembled:
		SaveSystem.mark_unlocked("milestone:bindle_assembled")
	# Evaluate achievements before the end-screen so newly-fired ones
	# can surface in the run summary.
	_evaluate_achievements("win", "")
	# Persist
	var contents := ""
	for it in _inventory:
		if String(it).begins_with("contents_"):
			contents = it
			break
	GauntletState.record_win(_arcana_id, _location_id, contents, _lore_tokens_collected, "")
	# Clear the mid-run save now that the scenario is complete —
	# next start of this arcana+scenario opens fresh.
	_clear_gauntlet_save()
	# Capture for game_ended emit on leave. Threshold + finale-token
	# data goes into the summary so the host can log / route on it.
	_last_outcome = "won"
	_last_summary = {
		"arcana": _arcana_id,
		"location": _location_id,
		"scenario": _scenario_id,
		"threshold": threshold,
		"contents": contents,
		"lore_tokens": _lore_tokens_collected,
		"ending_token": ending_token,
	}
	# CG image path per threshold
	var cg_path: String = _win_cg_path(threshold)
	# Threshold-specific narrative
	var narrative: String = _win_narrative(threshold, ending_token, contents)
	_show_end_screen(true, "★  THE LEAP", narrative, cg_path)
	# game_ended fires from _on_leave when the player dismisses the
	# screen — emitting it now would tear the overlay down with the
	# scene before they see the ending.


func _win_cg_path(threshold: String) -> String:
	match threshold:
		"parking_lot":   return "res://assets/cg/fool_leap_parking_lot.png"
		"river_window":  return "res://assets/cg/fool_leap_river_window.png"
		"precipice_door": return "res://assets/cg/fool_leap_precipice_door.png"
	return ""


func _win_narrative(threshold: String, ending_token: String, contents: String) -> String:
	var head: String = ""
	# 1. Fool has hand-authored per-threshold prose (was here before
	#    every arcana had win screens).
	match threshold:
		"parking_lot":
			head = "You step off the curb into the parking lot. The fluorescents dim behind you. The sodium light ahead is mundane, ordinary, awake. Whatever Graustark is, you're walking into it now."
		"river_window":
			head = "The window unlatches like it was always going to. You climb over the sill and the river receives you — its current is a substrate you've felt under everything but never named. You leap into the dark water and the dark water knows your name."
		"precipice_door":
			head = "The door you couldn't see all night is open. The room beyond is lit warm — tape reels turning, a woman at the far end, waiting. Elicia has been recording you since before you started here. You step through, and the door closes softly behind you."
	# 2. If no Fool-authored head, fall through to threshold-declared
	#    narrative fields on the setup file. Threshold entries can carry
	#    an optional `win_narrative` (full paragraph) or `flavor` (the
	#    exit-moment description that every threshold already has). We
	#    prefer win_narrative when present since it can be tuned for the
	#    winning-tone specifically.
	if head == "":
		for t in _setup.get("thresholds", []):
			var t_d: Dictionary = t
			if String(t_d.get("id", "")) != threshold:
				continue
			var wn: String = String(t_d.get("win_narrative", ""))
			var fl: String = String(t_d.get("flavor", ""))
			if wn != "":
				head = wn
			elif fl != "":
				head = fl
			break
	# 3. If threshold is unknown (edge case · scenario-additions space
	#    that isn't in the setup's thresholds list), synthesize from the
	#    ending_lore_token so we never render an empty win screen.
	if head == "" and ending_token != "":
		head = "You crossed the threshold. What waits on the other side is · in the parish's shorthand · %s." % ending_token.replace("_", " ")
	var contents_line: String = ""
	if contents != "":
		var c_item: Dictionary = _items_def.get(contents, {})
		var c_token: String = String(c_item.get("ending_lore_token", ""))
		contents_line = "\n\nYou carry %s with you — %s." % [
			c_item.get("title", contents),
			c_token.replace("_", " ") if c_token != "" else "the smallest weight that's still yours"]
	var lore_line: String = ""
	if not _lore_tokens_collected.is_empty():
		lore_line = "\n\nLore tokens collected:\n  · " + "\n  · ".join(_lore_tokens_collected)
	return head + contents_line + lore_line


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
	_last_finale_id = finale_id
	# Evaluate achievements that fire on loss (sinkhole opens etc.).
	_evaluate_achievements("loss", finale_id)
	# Milestones — gauntlet_loss unlocks the 24-Hour Diner skin + the
	# Reversed BGM track. Per-arcana variant tracks which arcana you
	# lost on. Magician finales each have their own stinger key the
	# music catalog references, so unlock that too.
	SaveSystem.mark_unlocked("milestone:gauntlet_loss")
	SaveSystem.mark_unlocked("milestone:gauntlet_loss:" + _arcana_id)
	if _arcana_id == "magician" and finale_id != "":
		# Map finale-id → the catalog's stinger key. Finale ids come
		# from magician/finale.json; keys here mirror the catalog
		# entries added in the music-slot-definitions pass.
		var stinger_key: String = ""
		match finale_id:
			"the_maker_forgets_the_make": stinger_key = "milestone:magician_finale:maker_forgets"
			"the_maker_breaks":            stinger_key = "milestone:magician_finale:maker_breaks"
			"the_steamboat_sails":         stinger_key = "milestone:magician_finale:steamboat_sails"
			"the_river_takes_the_bank":    stinger_key = "milestone:magician_finale:river_takes_bank"
			"the_room_walked_out":         stinger_key = "milestone:magician_finale:room_walked_out"
			"shift_ends_behind":           stinger_key = "milestone:magician_finale:shift_ends"
			"inertia_max":                 stinger_key = "milestone:magician_finale:inertia_fallback"
		if stinger_key != "":
			SaveSystem.mark_unlocked(stinger_key)
	if _arcana_id == "priestess" and finale_id != "":
		# Priestess finale-id → milestone:priestess_finale:<key>. The
		# music catalog slots can adopt these keys when the priestess
		# finale stingers are added in a future music-slot pass.
		var p_key: String = ""
		match finale_id:
			"the_reel_ran_out":              p_key = "milestone:priestess_finale:reel_ran_out"
			"the_listener_breaks":           p_key = "milestone:priestess_finale:listener_breaks"
			"the_session_ends_empty":        p_key = "milestone:priestess_finale:session_empty"
			"they_walked_out_mid_sentence":  p_key = "milestone:priestess_finale:walked_out"
			"the_cicadas_stopped":           p_key = "milestone:priestess_finale:cicadas_stopped"
			"session_over_unfinished":       p_key = "milestone:priestess_finale:shift_ends"
		if p_key != "":
			SaveSystem.mark_unlocked(p_key)
	GauntletState.record_loss(_arcana_id, _location_id, finale_id, _lore_tokens_collected)
	_clear_gauntlet_save()
	_last_outcome = "lost"
	_last_summary = {
		"arcana": _arcana_id,
		"location": _location_id,
		"scenario": _scenario_id,
		"finale_id": finale_id,
		"finale_title": finale_title,
		"lore_tokens": _lore_tokens_collected,
	}
	var cg_path: String = _loss_cg_path(finale_id)
	_show_end_screen(false, "REVERSED · " + finale_title, finale_flavor, cg_path)
	# game_ended fires when the player dismisses the end screen via
	# _on_leave — emitting it here would tear the scene down and the
	# player would never see the finale.


func _loss_cg_path(finale_id: String) -> String:
	match finale_id:
		"wipe_the_same_spot_forever":         return "res://assets/cg/fool_finale_wipe_forever.png"
		"twenty_four_hour_diner_of_the_soul": return "res://assets/cg/fool_finale_24_hour_diner.png"
		"the_empty_room":                     return "res://assets/cg/fool_finale_empty_room.png"
		"the_room_listens_back":              return "res://assets/cg/fool_finale_room_listens.png"
		"the_three_forty_seven_minute":       return "res://assets/cg/fool_finale_three_forty_seven.png"
	return ""


func _show_end_screen(won: bool, title: String, body: String, cg_path: String = "") -> void:
	if _end_overlay != null:
		_end_overlay.queue_free()
	_end_overlay = Control.new()
	_end_overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_end_overlay.z_index = 200
	# Heavy dim — cinematic.
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.92)
	dim.top_level = true
	dim.position = Vector2.ZERO
	dim.size = get_viewport_rect().size
	dim.mouse_filter = Control.MOUSE_FILTER_STOP
	_end_overlay.add_child(dim)
	# Centered ~80% cinematic panel, large image + text below.
	var view: Vector2 = get_viewport_rect().size
	var panel := PanelContainer.new()
	panel.add_theme_stylebox_override("panel", _make_panel_style())
	panel.size = Vector2(min(view.x * 0.84, 980.0), min(view.y * 0.88, 680.0))
	panel.position = (view - panel.size) * 0.5
	_end_overlay.add_child(panel)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 12)
	panel.add_child(vb)
	# CG image at the top (or a placeholder bar if missing) — gives
	# the finale weight even before art is generated.
	var cg_tex: Texture2D = _load_texture_silent(cg_path) if cg_path != "" else null
	var cg_panel := PanelContainer.new()
	cg_panel.add_theme_stylebox_override("panel", _make_panel_style())
	cg_panel.custom_minimum_size = Vector2(0, 340)
	cg_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	vb.add_child(cg_panel)
	if cg_tex:
		var img := TextureRect.new()
		img.texture = cg_tex
		img.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		img.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		img.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		img.size_flags_vertical = Control.SIZE_EXPAND_FILL
		cg_panel.add_child(img)
	else:
		var ph := Label.new()
		ph.text = "(finale CG art not yet generated)\nGenerate it in gauntlet_studio.html at\n  %s" % cg_path
		ph.add_theme_color_override("font_color", Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.40))
		ph.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		ph.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		ph.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		ph.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		cg_panel.add_child(ph)
	# Title — large, color-coded
	var t := Label.new()
	t.text = title
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	t.add_theme_color_override("font_color", C_GOOD if won else C_BAD)
	t.add_theme_font_size_override("font_size", 26)
	vb.add_child(t)
	# Narrative + lore tokens, scrollable so long endings fit
	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	vb.add_child(scroll)
	var b := RichTextLabel.new()
	b.bbcode_enabled = true
	b.fit_content = true
	b.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	b.text = "[i]%s[/i]" % body
	b.add_theme_color_override("default_color", C_TEXT)
	b.add_theme_font_size_override("normal_font_size", 13)
	scroll.add_child(b)
	# Buttons
	var actions := HBoxContainer.new()
	actions.add_theme_constant_override("separation", 10)
	vb.add_child(actions)
	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	actions.add_child(spacer)
	var btn := Button.new()
	btn.text = "Leave the Diner"
	btn.add_theme_font_size_override("font_size", 14)
	btn.custom_minimum_size = Vector2(180, 36)
	btn.pressed.connect(_on_leave)
	actions.add_child(btn)
	add_child(_end_overlay)
	# Fade-in for cinematic feel
	_end_overlay.modulate = Color(1, 1, 1, 0)
	var t_in := create_tween()
	t_in.tween_property(_end_overlay, "modulate:a", 1.0, 0.5).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)


func _on_leave() -> void:
	# Snap the BGM bus back to neutral so the menu / next scene
	# doesn't inherit a muffled / distorted room.
	if _audio_manipulator != null and is_instance_valid(_audio_manipulator):
		_audio_manipulator.reset()
	# Quiesce the FP SubViewport BEFORE this tree is freed. Freeing a
	# live own-world SubViewport (the ~3k-node locale, UPDATE_ALWAYS)
	# in the same frame it renders has crashed the Compatibility
	# renderer on the Deck when leaving a gauntlet.
	if _cached_fp_vp != null and is_instance_valid(_cached_fp_vp):
		_cached_fp_vp.render_target_update_mode = SubViewport.UPDATE_DISABLED
	if _cached_fp_vc != null and is_instance_valid(_cached_fp_vc):
		_cached_fp_vc.visible = false
	visible = false
	# Emit the real outcome captured at win/loss time. If the player
	# left before either fired, defaults are "leave" / {}.
	game_ended.emit(_last_outcome, _last_summary)
	queue_free()


# ── Mid-run save state ──────────────────────────────────────────
# Tier 2 audit gap: the gauntlet had zero save state; mid-run quit
# lost everything. Now: autosave on phase transition; resume on
# next start_scenario for the same arcana+scenario. The save lives
# at user://saves/gauntlet/<arcana>_<scenario>.json and stores
# enough state that the player can pick up where they left off.
# Complex sub-state (visitor positions, tableau stock, gravity
# deck order) is included; design data (cards / setups / decks)
# is reloaded from JSON on resume.
const GAUNTLET_SAVE_DIR := "user://saves/gauntlet/"


func _gauntlet_save_path() -> String:
	return GAUNTLET_SAVE_DIR + ("%s_%s.json" % [_arcana_id, _scenario_id])


func _collect_run_state() -> Dictionary:
	return {
		"save_version":      1,
		"arcana":             _arcana_id,
		"scenario":           _scenario_id,
		"location":           _location_id,
		"hand_setup":         _hand_id,
		"reversed":           _reversed_mode,
		"phase":              int(_phase),
		"turn":               _turn,
		"time":               _time,
		"next_time_reset":    _next_time_reset,
		"inertia":            _inertia,
		"sanity":             _sanity,
		"sanity_max":         _sanity_max,
		"stagnation":         _stagnation,
		"doubt":              _doubt,
		"player_pos":         _player_pos,
		"places_visited":     _places_visited,
		"hand_cards":         _hand_cards,
		"tableau_stock":      _tableau_stock,
		"inventory":          _inventory,
		"visitors_state":     _visitors_state,
		"gravity_draw_pile":  _gravity_draw_pile,
		"gravity_discard":    _gravity_discard_pile,
		"gravity_last":       _gravity_last_drawn,
		"gravity_recycles":   _gravity_recycle_count,
		"lore_tokens":        _lore_tokens_collected,
	}


func _apply_run_state(d: Dictionary) -> void:
	# Restore the run from a save dict. Called after _init_run() so
	# we overwrite the freshly-initialized state with the saved one.
	# Type-cast carefully — JSON.parse turns ints into floats, so we
	# coerce everywhere.
	_phase            = int(d.get("phase", Phase.ACTION))
	_turn             = int(d.get("turn", 1))
	_time             = int(d.get("time", 4))
	_next_time_reset  = int(d.get("next_time_reset", _time))
	_inertia          = int(d.get("inertia", 0))
	_sanity           = int(d.get("sanity", 5))
	_sanity_max       = int(d.get("sanity_max", 5))
	_stagnation       = int(d.get("stagnation", 0))
	_doubt            = int(d.get("doubt", 0))
	_player_pos       = String(d.get("player_pos", "counter"))
	_places_visited   = d.get("places_visited", {})
	_hand_cards       = d.get("hand_cards", [])
	_tableau_stock    = d.get("tableau_stock", {})
	_inventory        = d.get("inventory", [])
	_visitors_state   = d.get("visitors_state", {})
	_gravity_draw_pile    = d.get("gravity_draw_pile", [])
	_gravity_discard_pile = d.get("gravity_discard", [])
	_gravity_last_drawn   = d.get("gravity_last", {})
	_gravity_recycle_count = int(d.get("gravity_recycles", 0))
	_lore_tokens_collected = d.get("lore_tokens", [])


func _write_gauntlet_save() -> void:
	# Only save if a real run is in progress.
	if _game_over:
		return
	if _arcana_id == "" or _scenario_id == "":
		return
	DirAccess.make_dir_recursive_absolute(GAUNTLET_SAVE_DIR)
	var f := FileAccess.open(_gauntlet_save_path(), FileAccess.WRITE)
	if f == null:
		push_warning("[Gauntlet] could not write save to %s" % _gauntlet_save_path())
		return
	f.store_string(JSON.stringify(_collect_run_state(), "  "))


const GAUNTLET_SAVE_VERSION := 1


func _try_load_gauntlet_save() -> bool:
	# Returns true if a save existed for this arcana+scenario AND
	# was loaded successfully. Caller (_ready) should skip the
	# fresh-state intro log lines when this returns true.
	var path: String = _gauntlet_save_path()
	if not FileAccess.file_exists(path):
		return false
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return false
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	if typeof(parsed) != TYPE_DICTIONARY:
		return false
	var d: Dictionary = parsed
	# Sanity check — refuse to load a save that doesn't match this
	# arcana + scenario (shouldn't happen since the path is keyed
	# by them, but a manual file copy could trip it).
	if String(d.get("arcana", "")) != _arcana_id or String(d.get("scenario", "")) != _scenario_id:
		return false
	# Version gate. Currently v1. When a breaking change lands, add
	# an explicit migration branch here and bump GAUNTLET_SAVE_VERSION.
	# For now: refuse to load future-version saves rather than crash
	# on missing fields we can't infer.
	var save_v: int = int(d.get("save_version", 1))
	if save_v > GAUNTLET_SAVE_VERSION:
		push_warning("[Gauntlet] save v%d newer than engine v%d for %s/%s — refusing to load" %
			[save_v, GAUNTLET_SAVE_VERSION, _arcana_id, _scenario_id])
		return false
	# Older versions load through as-is · the _apply_run_state uses
	# .get(field, default) throughout so any newly-added field is
	# populated with a sensible default when it's missing from an
	# older save. This is additive-forward-compat by construction.
	_apply_run_state(d)
	return true


func _clear_gauntlet_save() -> void:
	# Called on win/loss to remove the save so the next start of
	# the same scenario gets a fresh run. Also called by the player
	# from any "restart this scenario" affordance the UI exposes.
	var path: String = _gauntlet_save_path()
	if FileAccess.file_exists(path):
		DirAccess.remove_absolute(path)
