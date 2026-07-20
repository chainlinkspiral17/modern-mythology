extends Control
## THE ONEIRONAUT'S ALMANAC — the cross-pillar compendium.
##
## One place that remembers everything you've dreamed across the four
## pillars (VN / gauntlet / Community Planned / slowsticks), plus the
## THREADS that run between them. Read-only over OneironauticsTokens +
## GauntletState via AlmanacState; entries light when their predicates
## are met. Evaluates the additive cross-pillar unlock rules on open.
##
## Design: lore/_ONEIRONAUTS_ALMANAC_DESIGN.md
## Pattern: ProfilePanel — static build(parent), fresh each open,
## "ui" group for F4 compliance, Esc/menu_back to close.

const C_BG     := Color(0.024, 0.020, 0.014, 0.97)
const C_ACCENT := Color(0.95, 0.78, 0.40)
const C_TEXT   := Color(0.86, 0.80, 0.66)
const C_DIM    := Color(0.48, 0.45, 0.38)
const C_LIT    := Color(0.62, 0.90, 0.68)
const C_THREAD := Color(0.80, 0.66, 0.92)

const CHAPTER_TITLES := {
	"the_reading":  "THE READING",
	"the_gauntlet": "THE GAUNTLET",
	"the_county":   "THE COUNTY",
	"the_shelf":    "THE SHELF",
	"threads":      "THREADS",
}

var _entries: Array = []
var _chapters: Array = []
var _sel: String = ""
var _right: VBoxContainer = null


static func build(parent: Node) -> Control:
	var panel := Control.new()
	panel.set_script(load("res://scenes/menu/Almanac.gd"))
	panel.name = "Almanac"
	return panel


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	var bank := get_node_or_null("/root/SFXBank")
	if bank: bank.play("menu_open", 0.7)
	# Light up any cross-pillar unlocks earned since last look.
	AlmanacState.evaluate_unlocks()
	_entries = AlmanacState.load_entries()
	_chapters = AlmanacState.chapters()
	if not _chapters.is_empty():
		_sel = String(_chapters[0])
	_build()


func _input(event: InputEvent) -> void:
	if event.is_action_pressed("menu_back") or \
			(event is InputEventKey and (event as InputEventKey).keycode == KEY_ESCAPE and event.pressed):
		queue_free()
		get_viewport().set_input_as_handled()


func _build() -> void:
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.80)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.gui_input.connect(func(ev: InputEvent) -> void:
		if ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed:
			queue_free())
	add_child(dim)

	var card := Panel.new()
	card.set_anchors_preset(Control.PRESET_CENTER)
	card.offset_left = -460
	card.offset_right = 460
	card.offset_top = -300
	card.offset_bottom = 300
	add_child(card)

	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 26)
	margin.add_theme_constant_override("margin_right", 26)
	margin.add_theme_constant_override("margin_top", 20)
	margin.add_theme_constant_override("margin_bottom", 20)
	card.add_child(margin)

	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 10)
	margin.add_child(col)

	var header := Label.new()
	header.text = "· THE ONEIRONAUT'S ALMANAC ·"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 22)
	header.add_theme_color_override("font_color", C_ACCENT)
	col.add_child(header)

	var sub := Label.new()
	var lit_all := 0
	for e in _entries:
		if AlmanacState.entry_is_lit(e): lit_all += 1
	sub.text = "%d of %d pages have filled in · the walls here are thin" % [lit_all, _entries.size()]
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub.add_theme_font_size_override("font_size", 12)
	sub.add_theme_color_override("font_color", C_DIM)
	col.add_child(sub)

	var rule := ColorRect.new()
	rule.color = Color(C_ACCENT.r, C_ACCENT.g, C_ACCENT.b, 0.3)
	rule.custom_minimum_size.y = 1
	col.add_child(rule)

	var body := HBoxContainer.new()
	body.add_theme_constant_override("separation", 16)
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	col.add_child(body)

	# ── left · chapter list ──
	var chapters_col := VBoxContainer.new()
	chapters_col.add_theme_constant_override("separation", 4)
	chapters_col.custom_minimum_size.x = 250
	body.add_child(chapters_col)
	for c_v in _chapters:
		var c := String(c_v)
		var prog: Vector2i = AlmanacState.chapter_progress(c, _entries)
		var b := Button.new()
		b.text = "  %s  ·  %d/%d  " % [CHAPTER_TITLES.get(c, c.to_upper()), prog.x, prog.y]
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.add_theme_font_size_override("font_size", 15)
		b.add_theme_color_override("font_color", C_ACCENT if c == _sel else C_TEXT)
		var cid := c
		b.pressed.connect(func() -> void: _select(cid))
		chapters_col.add_child(b)

	# ── right · entries of the selected chapter ──
	var scroll := ScrollContainer.new()
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.add_child(scroll)
	_right = VBoxContainer.new()
	_right.add_theme_constant_override("separation", 10)
	_right.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(_right)
	_render_entries()

	var close := Button.new()
	close.text = "  · close ·  "
	close.add_theme_font_size_override("font_size", 14)
	close.pressed.connect(func() -> void: queue_free())
	col.add_child(close)


func _select(chapter: String) -> void:
	if chapter == _sel: return
	_sel = chapter
	# Rebuild the whole card (cheap) so chapter-button highlight updates too.
	for c in get_children():
		c.queue_free()
	_build()


func _render_entries() -> void:
	if _right == null: return
	for c in _right.get_children():
		c.queue_free()
	var is_threads := _sel == "threads"
	for e_v in _entries:
		var e: Dictionary = e_v
		if String(e.get("chapter", "")) != _sel: continue
		var lit := AlmanacState.entry_is_lit(e)
		var row := VBoxContainer.new()
		row.add_theme_constant_override("separation", 1)
		_right.add_child(row)
		var title := Label.new()
		title.text = ("✦ " if lit else "· ") + String(e.get("title", "?"))
		title.add_theme_font_size_override("font_size", 15)
		if lit:
			title.add_theme_color_override("font_color", C_THREAD if is_threads else C_LIT)
		else:
			title.add_theme_color_override("font_color", C_DIM)
		row.add_child(title)
		var blurb := Label.new()
		blurb.text = "    " + (String(e.get("blurb", "")) if lit else "— not yet dreamed —")
		blurb.add_theme_font_size_override("font_size", 12)
		blurb.add_theme_color_override("font_color", C_TEXT if lit else C_DIM)
		blurb.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		row.add_child(blurb)
