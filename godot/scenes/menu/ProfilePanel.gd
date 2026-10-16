extends Control
## ProfilePanel — the one place the whole package's progress is
## visible together. Read-only; no new state. Sections:
##   VOLUMES    · save slots (vol · scene reached) + CGs seen
##   GAUNTLET   · per-arcana W/L aggregated over locations +
##                achievements unlocked count
##   SLOWSTICKS · finished / catalogued
##   TOKENS     · lore tokens held (the cross-game currency)
## Pattern: ScrapbookPanel — static build(parent), fresh each open,
## "ui" group for F4 compliance.

const _ARCANA_ORDER := ["fool", "magician", "priestess", "empress", "emperor",
	"hierophant", "lovers", "chariot", "strength", "hermit", "wheel_of_fortune",
	"justice", "hanged_man", "death", "temperance", "devil", "tower", "star",
	"moon", "sun", "judgement", "world"]
const _STICK_CATALOG_COUNT := 15

const C_BG     := Color(0.024, 0.020, 0.014, 0.97)
const C_ACCENT := Color(0.95, 0.78, 0.40)
const C_TEXT   := Color(0.86, 0.80, 0.66)
const C_DIM    := Color(0.55, 0.51, 0.42)
const C_WIN    := Color(0.55, 0.95, 0.65)
const C_LOSS   := Color(0.95, 0.55, 0.50)


static func build(parent: Node) -> Control:
	var panel := Control.new()
	panel.set_script(load("res://scenes/menu/ProfilePanel.gd"))
	panel.name = "ProfilePanel"
	return panel


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	var bank := get_node_or_null("/root/SFXBank")
	if bank: bank.play("menu_open", 0.7)
	_build()


func _input(event: InputEvent) -> void:
	if event.is_action_pressed("menu_back") or \
			(event is InputEventKey and (event as InputEventKey).keycode == KEY_ESCAPE and event.pressed):
		queue_free()
		get_viewport().set_input_as_handled()


func _build() -> void:
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.78)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.gui_input.connect(func(ev: InputEvent) -> void:
		if ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed:
			queue_free())
	add_child(dim)

	var card := Panel.new()
	card.set_anchors_preset(Control.PRESET_CENTER)
	card.offset_left = -420
	card.offset_right = 420
	card.offset_top = -310
	card.offset_bottom = 310
	var st := StyleBoxFlat.new()
	st.bg_color = C_BG
	st.border_color = Color(C_ACCENT.r, C_ACCENT.g, C_ACCENT.b, 0.45)
	st.set_border_width_all(1)
	st.set_content_margin_all(18)
	card.add_theme_stylebox_override("panel", st)
	add_child(card)

	var vb := VBoxContainer.new()
	vb.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	vb.add_theme_constant_override("separation", 8)
	card.add_child(vb)

	var title := Label.new()
	title.text = "PROFILE · THE WHOLE READING"
	title.add_theme_font_size_override("font_size", 20)
	title.add_theme_color_override("font_color", C_ACCENT)
	vb.add_child(title)

	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	vb.add_child(scroll)
	var col := VBoxContainer.new()
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	col.add_theme_constant_override("separation", 6)
	scroll.add_child(col)

	_section(col, "VOLUMES")
	_build_volumes(col)
	_section(col, "TAROT GAUNTLET")
	_build_gauntlet(col)
	_section(col, "SLOWSTICKS")
	_build_slowsticks(col)
	_section(col, "LORE TOKENS")
	_build_tokens(col)

	var hint := Label.new()
	hint.text = "click outside or ESC to close"
	hint.add_theme_font_size_override("font_size", 12)
	hint.add_theme_color_override("font_color", C_DIM)
	vb.add_child(hint)


func _section(col: VBoxContainer, name_: String) -> void:
	var l := Label.new()
	l.text = name_
	l.add_theme_font_size_override("font_size", 15)
	l.add_theme_color_override("font_color", C_ACCENT)
	col.add_child(l)
	var rule := ColorRect.new()
	rule.color = Color(C_ACCENT.r, C_ACCENT.g, C_ACCENT.b, 0.30)
	rule.custom_minimum_size.y = 1
	col.add_child(rule)


func _row(col: VBoxContainer, text: String, color: Color = C_TEXT, size: int = 13) -> void:
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	col.add_child(l)


func _build_volumes(col: VBoxContainer) -> void:
	var ss := get_node_or_null("/root/SaveSystem")
	if ss == null:
		_row(col, "  (save system unavailable)", C_DIM)
		return
	var saves: Array = ss.call("list_saves")
	if saves.is_empty():
		_row(col, "  no reading in progress", C_DIM)
	for s_v in saves:
		var s: Dictionary = s_v
		var vol: int = int(s.get("vol", 0))
		var scene: String = String(s.get("scene_id", "?"))
		_row(col, "  slot %s · vol %d · %s" % [str(s.get("slot", "?")), vol, scene])
	var cgs: Dictionary = ss.call("get_seen_cgs")
	_row(col, "  gallery: %d images seen" % cgs.size(), C_DIM)


func _build_gauntlet(col: VBoxContainer) -> void:
	var gs := get_node_or_null("/root/GauntletState")
	var wins_by: Dictionary = {}
	var losses_by: Dictionary = {}
	if gs != null and gs.get("state") is Dictionary:
		var st: Dictionary = gs.get("state")
		wins_by = st.get("wins_by_arcana_location", {})
		losses_by = st.get("losses_by_arcana_location", {})
	# Aggregate "fool@dambrosios" keys down to per-arcana totals.
	var w: Dictionary = {}
	var l: Dictionary = {}
	for k in wins_by:
		var arc := String(k).get_slice("@", 0)
		w[arc] = int(w.get(arc, 0)) + int(wins_by[k])
	for k in losses_by:
		var arc := String(k).get_slice("@", 0)
		l[arc] = int(l.get(arc, 0)) + int(losses_by[k])
	var played := 0
	var line := ""
	var col_count := 0
	for arc in _ARCANA_ORDER:
		var aw: int = int(w.get(arc, 0))
		var al: int = int(l.get(arc, 0))
		if aw + al == 0:
			continue
		played += 1
		line += "  %s %d–%d" % [arc.replace("_", " "), aw, al]
		col_count += 1
		if col_count == 3:
			_row(col, line)
			line = ""
			col_count = 0
	if line != "":
		_row(col, line)
	if played == 0:
		_row(col, "  no cards drawn yet", C_DIM)
	else:
		_row(col, "  arcana played: %d of 22" % played, C_DIM)
	# Achievements: count entries whose unlock_key is marked.
	var ss := get_node_or_null("/root/SaveSystem")
	var unlocked := 0
	var total := 0
	if ss != null and FileAccess.file_exists("res://resources/achievements.json"):
		var f := FileAccess.open("res://resources/achievements.json", FileAccess.READ)
		if f != null:
			var parsed = JSON.parse_string(f.get_as_text())
			if parsed is Dictionary:
				for e_v in (parsed as Dictionary).get("achievements", []):
					var e: Dictionary = e_v
					total += 1
					if ss.call("is_unlocked", String(e.get("unlock_key", ""))):
						unlocked += 1
	_row(col, "  achievements: %d of %d" % [unlocked, total],
			C_WIN if unlocked > 0 else C_DIM)


func _build_slowsticks(col: VBoxContainer) -> void:
	var gs := get_node_or_null("/root/GauntletState")
	var finished: Array = []
	if gs != null and gs.get("state") is Dictionary:
		var st: Dictionary = gs.get("state")
		var sf: Variant = st.get("slowsticks_finished", [])
		if sf is Array:
			finished = sf
	if finished.is_empty():
		_row(col, "  none finished · the shelf is waiting", C_DIM)
	else:
		for sid in finished:
			_row(col, "  ✓ " + String(sid).replace("_", " "), C_WIN)
	_row(col, "  finished: %d of %d catalogued" % [finished.size(), _STICK_CATALOG_COUNT], C_DIM)


func _build_tokens(col: VBoxContainer) -> void:
	var gs := get_node_or_null("/root/GauntletState")
	var tokens: Array = []
	if gs != null and gs.get("state") is Dictionary:
		var st: Dictionary = gs.get("state")
		var lt: Variant = st.get("lore_tokens_revealed", [])
		if lt is Array:
			tokens = lt
	_row(col, "  %d tokens held" % tokens.size(),
			C_TEXT if tokens.size() > 0 else C_DIM)
	_row(col, "  tokens are earned across every game and spent by the" +
			" ones that know how to read them.", C_DIM, 12)
