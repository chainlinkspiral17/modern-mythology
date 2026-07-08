extends Control
## Pirate Summer · ending screen.
##
## Boots with (host_state).  Reads endings.json.  Picks the correct
## ending by:
##   1. left_camp_early flag → 'left_camp_early'
##   2. All six Wilson clues discovered AND Amelie friendship >= 3
##      OR Wilson-in-party history flag → 'wilson_ashe'
##   3. Highest friendship among per-camper endings (has_ending=true
##      campers · Tessa/Wu Kai/Nika/Elias/Danny) if that friendship
##      is >= 3 → per-camper ending
##   4. Otherwise → 'good_friends' shared ending
##
## Emits:
##   estuary_3_style · finished(canon_vars, lore_tokens)
##   quit_to_shelf   · BACK button
##
## F4-compliant via add_to_group("ui").

signal finished(canon_vars: Dictionary, lore_tokens: Array)
signal quit_to_shelf

const ENDINGS_PATH := "res://resources/games/vol7/pirate_summer/endings.json"

const C_BG     := Color(0.024, 0.020, 0.014, 0.98)
const C_ACCENT := Color(0.78, 0.66, 0.29, 1.00)
const C_TXT    := Color(0.83, 0.79, 0.69, 1.00)
const C_TXT_DIM:= Color(0.50, 0.47, 0.38, 1.00)

const WILSON_CLUES := [
	"wilson_has_anchor_decal",
	"wilson_disappeared_twenty_minutes_tuesday",
	"wilson_ghost_pirate_coordinates_match",
	"wilson_signed_treasure_map_1987",
	"wilson_sings_portuguese_volta_return",
	"wilson_is_the_pirate",
]

var _endings_by_id: Dictionary = {}
var _run_state: Dictionary = {}
var _picked_id: String = ""
var _content_col: VBoxContainer = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	_load_endings()
	_build_ui()


func boot(host_state: Dictionary) -> void:
	_run_state = host_state
	_pick_ending()
	_render()


func _load_endings() -> void:
	if not FileAccess.file_exists(ENDINGS_PATH): return
	var f := FileAccess.open(ENDINGS_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if not (parsed is Dictionary): return
	for e_v in (parsed as Dictionary).get("endings", []):
		var e: Dictionary = e_v
		_endings_by_id[String(e.get("id", ""))] = e


func _pick_ending() -> void:
	# 1. Early exit.
	if bool(_run_state.get("left_camp_early_friday", false)):
		_picked_id = "left_camp_early"
		return
	# 2. Wilson ending · all six clues AND Amelie context.
	# If Sam also carried absolution back from the ghost ship, the
	# full variant fires instead.
	var discovered: Array = _run_state.get("discovered_facts", [])
	var have_all_clues: bool = true
	for c in WILSON_CLUES:
		if not discovered.has(String(c)):
			have_all_clues = false
			break
	var amelie_friend: int = int((_run_state.get("friendship", {}) as Dictionary).get("amelie_rocha", 0))
	if have_all_clues and amelie_friend >= 3:
		if discovered.has("wilson_ancestors_ghost_absolution"):
			_picked_id = "wilson_ashe_full"
		else:
			_picked_id = "wilson_ashe"
		return
	# 3. Highest friendship among per-camper-ending campers.
	var per_camper_ids := ["tessa_ansen", "wu_kai", "nika_voss", "elias_wren", "danny_broz"]
	var best_id := ""
	var best_score: int = 0
	var friendship: Dictionary = _run_state.get("friendship", {})
	for cid in per_camper_ids:
		var score: int = int(friendship.get(cid, 0))
		if score > best_score:
			best_score = score
			best_id = cid
	if best_score >= 3 and best_id != "":
		_picked_id = best_id
		return
	# 4. Shared fallback.
	_picked_id = "good_friends"


func _build_ui() -> void:
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	var top := HBoxContainer.new()
	top.set_anchors_preset(Control.PRESET_TOP_WIDE)
	top.offset_left = 24
	top.offset_right = -24
	top.offset_top = 12
	top.offset_bottom = 40
	top.add_theme_constant_override("separation", 16)
	add_child(top)

	var hdr := Label.new()
	hdr.text = "PIRATE SUMMER · ENDING"
	hdr.add_theme_font_size_override("font_size", 14)
	hdr.add_theme_color_override("font_color", C_ACCENT)
	top.add_child(hdr)

	var sp := Control.new()
	sp.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top.add_child(sp)

	var back := Button.new()
	back.text = "  ✕  back to shelf  "
	back.pressed.connect(func() -> void: quit_to_shelf.emit())
	top.add_child(back)

	# Content column centered.
	var wrap := PanelContainer.new()
	wrap.set_anchors_preset(Control.PRESET_CENTER)
	wrap.custom_minimum_size = Vector2(720, 560)
	wrap.size = wrap.custom_minimum_size
	wrap.position = Vector2(-360, -280 + 24)
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.030, 0.026, 0.020, 1.0)
	sb.border_color = C_ACCENT
	sb.set_border_width_all(1)
	sb.content_margin_left = 22
	sb.content_margin_right = 22
	sb.content_margin_top = 16
	sb.content_margin_bottom = 16
	wrap.add_theme_stylebox_override("panel", sb)
	add_child(wrap)

	_content_col = VBoxContainer.new()
	_content_col.add_theme_constant_override("separation", 8)
	wrap.add_child(_content_col)


func _render() -> void:
	if _content_col == null: return
	for c in _content_col.get_children():
		c.queue_free()
	var e: Dictionary = _endings_by_id.get(_picked_id, {})
	if e.is_empty():
		var oops := Label.new()
		oops.text = "  (no ending data)"
		oops.add_theme_color_override("font_color", C_TXT_DIM)
		_content_col.add_child(oops)
		return

	var hdr := Label.new()
	hdr.text = "· %s ·" % String(e.get("label", _picked_id)).to_upper()
	hdr.add_theme_font_size_override("font_size", 13)
	hdr.add_theme_color_override("font_color", C_ACCENT)
	hdr.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_content_col.add_child(hdr)

	var scroll := ScrollContainer.new()
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_content_col.add_child(scroll)

	var body := RichTextLabel.new()
	body.bbcode_enabled = true
	body.fit_content = true
	body.custom_minimum_size = Vector2(660, 400)
	body.add_theme_color_override("default_color", C_TXT)
	body.add_theme_font_size_override("normal_font_size", 11)
	body.append_text(String(e.get("epilogue", "...")))
	scroll.add_child(body)

	var actions := HBoxContainer.new()
	actions.alignment = BoxContainer.ALIGNMENT_END
	_content_col.add_child(actions)

	var next := Button.new()
	next.text = "  →  back to the shelf  "
	next.pressed.connect(_finish_and_return)
	actions.add_child(next)


func _finish_and_return() -> void:
	var e: Dictionary = _endings_by_id.get(_picked_id, {})
	var canon_vars: Dictionary = _run_state.get("canon_vars", {})
	var cv_add: Dictionary = e.get("canon_var", {})
	for k in cv_add.keys():
		canon_vars[String(k)] = cv_add[k]
	var lore_tokens: Array = _run_state.get("lore_tokens_pending", []).duplicate()
	var lt := String(e.get("lore_token", ""))
	if lt != "" and not lore_tokens.has(lt):
		lore_tokens.append(lt)
	# Always append the top-level completion tokens.
	for t in ["pirate_summer_finished", "camp_sweetgum_visited"]:
		if not lore_tokens.has(t):
			lore_tokens.append(t)
	# Wilson-ending variants both drop the recognition token.
	if (_picked_id == "wilson_ashe" or _picked_id == "wilson_ashe_full") \
		and not lore_tokens.has("wilson_ashe_recognized"):
		lore_tokens.append("wilson_ashe_recognized")
	finished.emit(canon_vars, lore_tokens)
