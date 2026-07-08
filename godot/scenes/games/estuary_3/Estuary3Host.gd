extends Control
## Estuary 3 host · single scene, switches between acts.
##
## Owns the per-run save state (which act, which night, per-night
## register tape, Act 2 canon_vars, Act 3 location visits, Act 4
## line buffer). Instantiates the appropriate act controller as a
## child on transition. Persists to `user://estuary_3.save.json`
## between session boots.
##
## Acts (deferred controllers · scaffolded stubs for this commit):
##   act1_kwik_stop  · KwikStopRoom.gd
##   act2_estuary    · EstuaryPlanner.gd
##   act3_town       · TownWalkabout.gd
##   act4_fifth      · FifthSeasonBeach.gd
##   ending          · Estuary3Ending.gd
##
## Emits `finished(canon_vars, lore_tokens)` when the ending
## resolves. The Vol 7 gallery caller merges those into
## GauntletState.state and returns to the shelf.
##
## F4-compliant via add_to_group("ui") on the root Control.

signal finished(canon_vars: Dictionary, lore_tokens: Array)
signal quit_to_shelf

const SAVE_PATH := "user://estuary_3.save.json"
const RES_ROOT  := "res://resources/games/vol7/estuary_3/"

const ACT_MANIFEST := RES_ROOT + "manifest.json"
const ACT_RESOURCES := {
	"act1_kwik_stop": RES_ROOT + "act1_kwik_stop.json",
	"act2_estuary":   RES_ROOT + "act2_estuary.json",
	"act3_town":      RES_ROOT + "act3_town.json",
	"act4_fifth":     RES_ROOT + "act4_fifth_season.json",
	"ending":         RES_ROOT + "ending.json",
}

# Per-run state.
var _manifest: Dictionary = {}
var _current_act: String = "act1_kwik_stop"
var _run_state: Dictionary = {
	"current_act": "act1_kwik_stop",
	"night_index": 0,                # act1 · 0-11
	"register_tape": [],             # act1 · one entry per served customer
	"canon_vars": {},                # cumulative across acts
	"lore_tokens_pending": [],       # accumulated · flushed on `finished`
	"act2_season_choices": [],       # act2 · four seasons of tide/buffer/species
	"act3_locations_visited": [],    # act3 · location ids
	"act3_clock_minutes": 512,       # act3 · 08:32 → 32 minutes past hour 8
	"act4_line_buffer": [],          # act4 · [(x, y, arc_deg), ...]
}

# Active act controller (deferred · null in this scaffold commit).
var _act_controller: Control = null

# Simple debug/status overlay for this scaffold commit — remove
# once the four act controllers land.
var _debug_label: Label = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	_load_manifest()
	_load_save_if_present()
	_render_debug()


# ─── Session state ───────────────────────────────────────────────

func start_new_run() -> void:
	_run_state = {
		"current_act": "act1_kwik_stop",
		"night_index": 0,
		"register_tape": [],
		"canon_vars": {},
		"lore_tokens_pending": [],
		"act2_season_choices": [],
		"act3_locations_visited": [],
		"act3_clock_minutes": 512,
		"act4_line_buffer": [],
	}
	_current_act = "act1_kwik_stop"
	_save()
	_render_debug()


func resume_from_save() -> bool:
	if not _load_save_if_present():
		return false
	_current_act = String(_run_state.get("current_act", "act1_kwik_stop"))
	_render_debug()
	return true


func advance_to_act(next_act: String) -> void:
	if not ACT_RESOURCES.has(next_act):
		push_warning("[Estuary3Host] unknown act: %s" % next_act)
		return
	_current_act = next_act
	_run_state["current_act"] = next_act
	_save()
	_render_debug()


# ─── I/O ─────────────────────────────────────────────────────────

func _load_manifest() -> void:
	if not FileAccess.file_exists(ACT_MANIFEST):
		push_warning("[Estuary3Host] missing manifest at %s" % ACT_MANIFEST)
		return
	var f := FileAccess.open(ACT_MANIFEST, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		_manifest = parsed


func _load_save_if_present() -> bool:
	if not FileAccess.file_exists(SAVE_PATH):
		return false
	var f := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if f == null:
		return false
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if not (parsed is Dictionary):
		return false
	# Merge defaults so a save from an earlier build doesn't crash
	# on missing keys.
	var d: Dictionary = parsed
	for k in _run_state.keys():
		if not d.has(k):
			d[k] = _run_state[k]
	_run_state = d
	return true


func _save() -> void:
	var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f == null:
		push_warning("[Estuary3Host] failed to open %s for write" % SAVE_PATH)
		return
	f.store_string(JSON.stringify(_run_state, "  "))


# ─── Scaffold-commit debug view ──────────────────────────────────

func _render_debug() -> void:
	if _debug_label == null:
		var bg := ColorRect.new()
		bg.color = Color(0.024, 0.020, 0.014, 0.97)
		bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		add_child(bg)

		_debug_label = Label.new()
		_debug_label.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		_debug_label.offset_left = 32
		_debug_label.offset_right = -32
		_debug_label.offset_top = 32
		_debug_label.offset_bottom = -32
		_debug_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		_debug_label.add_theme_font_size_override("font_size", 12)
		_debug_label.add_theme_color_override("font_color", Color(0.83, 0.79, 0.69, 1))
		add_child(_debug_label)

		# Quit-to-shelf button so we can exit the scaffold view.
		var quit := Button.new()
		quit.text = "  ✕  BACK TO SHELF  "
		quit.set_anchors_preset(Control.PRESET_TOP_RIGHT)
		quit.position = Vector2(-180, 8)
		quit.pressed.connect(func() -> void: quit_to_shelf.emit())
		add_child(quit)

	var shelf: Dictionary = _manifest.get("shelf", {})
	var lines: PackedStringArray = PackedStringArray()
	lines.append("── ESTUARY 3 · %s ──" % String(shelf.get("label_title", "?")))
	lines.append("")
	lines.append(String(shelf.get("cover_blurb", "")))
	lines.append("")
	lines.append("Current act: %s" % _current_act)
	lines.append("Night index (act 1): %d" % int(_run_state.get("night_index", 0)))
	lines.append("Canon vars so far: %s" % JSON.stringify(_run_state.get("canon_vars", {})))
	lines.append("Lore tokens pending: %s" % JSON.stringify(_run_state.get("lore_tokens_pending", [])))
	lines.append("")
	lines.append("── SCAFFOLD NOTE ──")
	lines.append("The four act controllers (KwikStopRoom, EstuaryPlanner,")
	lines.append("TownWalkabout, FifthSeasonBeach) + Estuary3Ending are")
	lines.append("deferred to follow-up commits.  This host is the boot,")
	lines.append("the save-state owner, and the act switcher.  Clicking")
	lines.append("BACK TO SHELF returns you to SlowstockShelf without")
	lines.append("consuming a run.")
	_debug_label.text = "\n".join(Array(lines))
