extends Control
## Scrapbook view · reads a scrapbook JSON catalog and cross-references
## GauntletState.state.lore_tokens_revealed to render discovered
## entries as text and undiscovered ones as silhouettes.
##
## Contract:
##   - Parent calls `boot(scrapbook_path: String, revealed: Array)`
##     with the resource path and the current set of revealed tokens.
##   - Emits `closed` when the player hits BACK.
##
## Tier chips (colored, small) group entries.  Within a tier,
## discovered entries appear first, undiscovered after · so the
## shape of what's-still-missing is visible at a glance.
##
## F4-compliant via add_to_group("ui").

signal closed

const C_BG      := Color(0.024, 0.020, 0.014, 0.98)
const C_ACCENT  := Color(0.78, 0.66, 0.29, 1.00)
const C_TXT     := Color(0.83, 0.79, 0.69, 1.00)
const C_TXT_DIM := Color(0.44, 0.42, 0.34, 1.00)
const C_QUIET   := Color(0.32, 0.30, 0.24, 1.00)

const _TIER_COLORS := {
	"guests":       Color(0.86, 0.68, 0.32, 1.0),
	"modifiers":    Color(0.62, 0.86, 0.72, 1.0),
	"nights":       Color(0.72, 0.72, 0.94, 1.0),
	"summers":      Color(0.86, 0.86, 0.54, 1.0),
	"endings":      Color(0.94, 0.60, 0.60, 1.0),
	"wilson_clues": Color(0.62, 0.82, 0.96, 1.0),
	"cross_lore":   Color(0.86, 0.72, 0.94, 1.0),
	"world":        Color(0.70, 0.86, 0.60, 1.0),
	"dungeons":     Color(0.72, 0.86, 0.94, 1.0),
	"story_beats":  Color(0.94, 0.80, 0.62, 1.0),
	"completion":   Color(0.78, 0.66, 0.29, 1.0),
}

const _TIER_ORDER := ["endings", "wilson_clues", "dungeons", "story_beats", "summers", "cross_lore", "world", "modifiers", "guests", "nights", "completion"]

var _def: Dictionary = {}
var _revealed: Array = []
var _scroll: ScrollContainer = null
var _content_col: VBoxContainer = null
var _header_lbl: Label = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	_build_ui()


func boot(scrapbook_path: String, revealed: Array) -> void:
	_revealed = revealed.duplicate()
	_def = _load_json(scrapbook_path)
	_render()


func _load_json(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		push_warning("[SlowstockScrapbook] missing %s" % path)
		return {}
	var f := FileAccess.open(path, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary: return parsed
	return {}


func _build_ui() -> void:
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# Top bar
	var top := HBoxContainer.new()
	top.set_anchors_preset(Control.PRESET_TOP_WIDE)
	top.offset_left = 24
	top.offset_right = -24
	top.offset_top = 12
	top.offset_bottom = 40
	top.add_theme_constant_override("separation", 16)
	add_child(top)

	_header_lbl = Label.new()
	_header_lbl.text = "SCRAPBOOK"
	_header_lbl.add_theme_font_size_override("font_size", 14)
	_header_lbl.add_theme_color_override("font_color", C_ACCENT)
	top.add_child(_header_lbl)

	var sp := Control.new()
	sp.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top.add_child(sp)

	var back := Button.new()
	back.text = "  ← BACK  "
	back.pressed.connect(func() -> void: closed.emit())
	top.add_child(back)

	# Wrap for the entry list (centered, narrow).
	var wrap := PanelContainer.new()
	wrap.set_anchors_preset(Control.PRESET_CENTER)
	wrap.custom_minimum_size = Vector2(760, 560)
	wrap.size = wrap.custom_minimum_size
	wrap.position = Vector2(-380, -280 + 20)
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.030, 0.026, 0.020, 1.0)
	sb.border_color = C_ACCENT
	sb.set_border_width_all(1)
	sb.content_margin_left = 18
	sb.content_margin_right = 18
	sb.content_margin_top = 14
	sb.content_margin_bottom = 14
	wrap.add_theme_stylebox_override("panel", sb)
	add_child(wrap)

	_scroll = ScrollContainer.new()
	_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	wrap.add_child(_scroll)

	_content_col = VBoxContainer.new()
	_content_col.add_theme_constant_override("separation", 4)
	_content_col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_scroll.add_child(_content_col)


func _render() -> void:
	for c in _content_col.get_children():
		c.queue_free()

	if _def.is_empty():
		var oops := Label.new()
		oops.text = "  (no scrapbook found for this stick.)"
		oops.add_theme_color_override("font_color", C_TXT_DIM)
		_content_col.add_child(oops)
		return

	_header_lbl.text = String(_def.get("title", "SCRAPBOOK")).to_upper()

	var entries: Array = _def.get("entries", [])
	# Group by tier.  Preserve insertion order within tier.  Discovered
	# entries render first within their tier.
	var by_tier: Dictionary = {}
	for t in _TIER_ORDER:
		by_tier[t] = []
	for e_var in entries:
		var e: Dictionary = e_var
		var tier := String(e.get("tier", "misc"))
		if not by_tier.has(tier):
			by_tier[tier] = []
		by_tier[tier].append(e)

	# Progress line.
	var total: int = entries.size()
	var found: int = 0
	for e_var in entries:
		if _revealed.has(String((e_var as Dictionary).get("token", ""))):
			found += 1
	var progress := Label.new()
	progress.text = "  %d of %d discovered" % [found, total]
	progress.add_theme_font_size_override("font_size", 11)
	progress.add_theme_color_override("font_color", C_TXT_DIM)
	_content_col.add_child(progress)
	_content_col.add_child(_spacer(8))

	for tier in _TIER_ORDER:
		var group: Array = by_tier.get(tier, [])
		if group.is_empty():
			continue
		_add_tier_header(tier)
		# Discovered first, then silhouettes.
		var found_rows: Array = []
		var missing_rows: Array = []
		for e_var in group:
			var e: Dictionary = e_var
			if _revealed.has(String(e.get("token", ""))):
				found_rows.append(e)
			else:
				missing_rows.append(e)
		for e_var in found_rows:
			_add_entry_row(e_var, true)
		for e_var in missing_rows:
			_add_entry_row(e_var, false)
		_content_col.add_child(_spacer(10))


func _add_tier_header(tier: String) -> void:
	var color: Color = _TIER_COLORS.get(tier, C_ACCENT)
	var wrap := HBoxContainer.new()
	wrap.add_theme_constant_override("separation", 6)
	# Colored chip
	var chip := ColorRect.new()
	chip.color = color
	chip.custom_minimum_size = Vector2(12, 12)
	chip.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	wrap.add_child(chip)
	var lbl := Label.new()
	lbl.text = tier.to_upper()
	lbl.add_theme_font_size_override("font_size", 11)
	lbl.add_theme_color_override("font_color", color)
	wrap.add_child(lbl)
	_content_col.add_child(wrap)


func _add_entry_row(entry: Dictionary, discovered: bool) -> void:
	var row := VBoxContainer.new()
	row.add_theme_constant_override("separation", 1)
	row.size_flags_horizontal = Control.SIZE_EXPAND_FILL

	var title := Label.new()
	if discovered:
		title.text = "  · " + String(entry.get("title", "?"))
		title.add_theme_color_override("font_color", C_TXT)
	else:
		title.text = "  · · · · · · · · · · · · · ·"
		title.add_theme_color_override("font_color", C_QUIET)
	title.add_theme_font_size_override("font_size", 11)
	row.add_child(title)

	if discovered:
		var blurb := RichTextLabel.new()
		blurb.bbcode_enabled = true
		blurb.fit_content = true
		blurb.custom_minimum_size = Vector2(680, 0)
		blurb.add_theme_font_size_override("normal_font_size", 10)
		blurb.add_theme_color_override("default_color", C_TXT_DIM)
		blurb.append_text("      " + String(entry.get("blurb", "")))
		row.add_child(blurb)

	_content_col.add_child(row)


func _spacer(h: int) -> Control:
	var s := Control.new()
	s.custom_minimum_size = Vector2(0, h)
	return s
