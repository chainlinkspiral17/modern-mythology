extends Control
## The cabin's personal slowstock library — shelf UI.
##
## Reads:
##   godot/resources/games/vol7/library/unlock_graph.json
##   godot/resources/games/vol7/library/shelf_layout.json
##   godot/resources/games/vol7/library/stubs/*.json
##   godot/resources/games/vol7/estuary_3/manifest.json
##
## Renders two shelves of cartridge slots per shelf_layout.json.
## Populated slots show the stick's label; empty slots show the
## empty-slot note (Olaf's stack of floppies, Kai's KRZ USB, etc.).
## Locked sticks render dimmer with no boot button. Hovering any
## cartridge surfaces its cover-blurb card in the side panel.
## Clicking a UNLOCKED cartridge emits `picked(stick_id)`.
##
## Persists progress against GauntletState.state.slowsticks_finished
## (a String[] of stick ids). Missing key defaults to []; a save
## from before this commit reads clean.
##
## F4-compliant via add_to_group("ui") on the root Control.

signal picked(stick_id: String)
signal closed

const LIBRARY_ROOT := "res://resources/games/vol7/library/"
const UNLOCK_GRAPH := LIBRARY_ROOT + "unlock_graph.json"
const SHELF_LAYOUT := LIBRARY_ROOT + "shelf_layout.json"
const STUBS_DIR    := LIBRARY_ROOT + "stubs/"
const FULL_MANIFESTS: Dictionary = {
	"estuary_3": "res://resources/games/vol7/estuary_3/manifest.json",
}

const C_BG        := Color(0.024, 0.020, 0.014, 0.97)
const C_SHELF     := Color(0.16, 0.12, 0.08, 1.00)  # dark cedar
const C_SHELF_LIP := Color(0.28, 0.20, 0.14, 1.00)
const C_CART      := Color(0.62, 0.55, 0.42, 1.00)
const C_CART_DIM  := Color(0.24, 0.22, 0.20, 1.00)
const C_LABEL     := Color(0.92, 0.86, 0.72, 1.00)
const C_LABEL_DIM := Color(0.42, 0.40, 0.36, 1.00)
const C_ACCENT    := Color(0.78, 0.66, 0.29, 1.00)
const C_TXT       := Color(0.83, 0.79, 0.69, 1.00)
const C_TXT_DIM   := Color(0.50, 0.47, 0.38, 1.00)
const C_LOCK      := Color(0.30, 0.28, 0.24, 1.00)
const C_BETA      := Color(0.42, 0.36, 0.24, 1.00)  # betamax case

const SLOT_W := 44
const SLOT_H := 128
const SLOT_GAP := 4
const SHELF_LIP_H := 6

# Loaded data
var _unlock_graph: Dictionary = {}
var _shelf_layout: Dictionary = {}
var _manifests: Dictionary = {}     # stick_id → manifest dict
var _finished: Array = []           # from GauntletState

# UI refs
var _card_title:    Label = null
var _card_subtitle: Label = null
var _card_meta:     Label = null
var _card_blurb:    Label = null
var _card_status:   Label = null
var _card_boot_btn: Button = null
var _hovered_id: String = ""


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")   # F4 compliance

	_load_data()
	_build()


func open() -> void:
	# Refresh finished set (in case a stick was just completed
	# and the shelf is being re-opened) and rebuild.
	_refresh_finished()
	visible = true


# ─── Data loading ────────────────────────────────────────────────

func _load_data() -> void:
	_unlock_graph = _load_json(UNLOCK_GRAPH)
	_shelf_layout = _load_json(SHELF_LAYOUT)
	# Load every stub manifest.
	var dir := DirAccess.open(STUBS_DIR)
	if dir != null:
		dir.list_dir_begin()
		var name := dir.get_next()
		while name != "":
			if name.ends_with(".json"):
				var m: Dictionary = _load_json(STUBS_DIR + name)
				var sid: String = String(m.get("id", ""))
				if sid != "":
					_manifests[sid] = m
			name = dir.get_next()
	# Load full manifests (override any stub of the same id).
	for sid in FULL_MANIFESTS.keys():
		var m := _load_json(String(FULL_MANIFESTS[sid]))
		if not m.is_empty():
			_manifests[String(sid)] = m
	_refresh_finished()


func _load_json(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		push_warning("[SlowstockShelf] missing %s" % path)
		return {}
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	return parsed if parsed is Dictionary else {}


func _refresh_finished() -> void:
	var gs := get_node_or_null("/root/GauntletState")
	if gs == null:
		_finished = []
		return
	var st: Variant = gs.get("state")
	if st is Dictionary:
		var arr: Variant = (st as Dictionary).get("slowsticks_finished", [])
		_finished = arr if arr is Array else []
	else:
		_finished = []


func _is_unlocked(stick_id: String) -> bool:
	# Starts-unlocked set.
	var starts: Array = _unlock_graph.get("starts_unlocked", [])
	if starts.has(stick_id):
		return true
	# Chapter gate.
	var gate: Dictionary = _unlock_graph.get("gated_by_vol7_chapter", {})
	if gate.has(stick_id):
		# TODO · read the current Vol 7 chapter from save state; for
		# now, assume locked to keep the design honest. When save
		# integration lands this reads `saved_vol` + `saved_chapter`
		# from the VN save.
		return false
	# Wave-graph.
	for w_var in _unlock_graph.get("waves", []):
		var w: Dictionary = w_var
		if not (w.get("sticks", []) as Array).has(stick_id):
			continue
		# Threshold: count of finished.
		var min_count: int = int(w.get("unlocked_by_count_of_finished_min", -1))
		if min_count >= 0:
			if _finished.size() >= min_count:
				return true
			continue
		# OR-graph: any of the listed dependencies finished.
		for dep in w.get("unlocked_by_any_of", []):
			if _finished.has(String(dep)):
				return true
	return false


func _is_finished(stick_id: String) -> bool:
	return _finished.has(stick_id)


func _is_fully_playable(stick_id: String) -> bool:
	# A stick with a full manifest (acts field present) is fully
	# playable; stubs are unlockable but boot into an
	# acknowledgment screen.
	var m: Dictionary = _manifests.get(stick_id, {})
	if m.is_empty():
		return false
	return m.has("acts")


# ─── UI build ────────────────────────────────────────────────────

func _build() -> void:
	# Backdrop
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.85)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.gui_input.connect(func(ev: InputEvent) -> void:
		if ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed:
			closed.emit())
	add_child(dim)

	# Two-column layout: shelf on the left, blurb card on the right.
	var root := HBoxContainer.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.add_theme_constant_override("separation", 16)
	root.offset_left = 24
	root.offset_right = -24
	root.offset_top = 24
	root.offset_bottom = -24
	add_child(root)

	# ── Shelf column (left ~65%)
	var shelf_col := VBoxContainer.new()
	shelf_col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	shelf_col.size_flags_stretch_ratio = 1.5
	shelf_col.add_theme_constant_override("separation", 8)
	root.add_child(shelf_col)

	var hdr := Label.new()
	hdr.text = "THE CABIN'S PERSONAL SLOWSTOCK LIBRARY"
	hdr.add_theme_font_size_override("font_size", 14)
	hdr.add_theme_color_override("font_color", C_ACCENT)
	shelf_col.add_child(hdr)

	var sub := Label.new()
	sub.text = String(_shelf_layout.get("shelf", {}).get("location", "west wall, above the record player"))
	sub.add_theme_font_size_override("font_size", 10)
	sub.add_theme_color_override("font_color", C_TXT_DIM)
	shelf_col.add_child(sub)

	# Rule
	var rule := ColorRect.new()
	rule.color = Color(C_ACCENT.r, C_ACCENT.g, C_ACCENT.b, 0.30)
	rule.custom_minimum_size.y = 1
	shelf_col.add_child(rule)

	# Two physical shelves
	var shelf_data: Dictionary = _shelf_layout.get("shelf", {})
	var n_shelves: int = int(shelf_data.get("shelves", 2))
	var slots_per: int = int(shelf_data.get("slots_per_shelf", 16))
	for si in range(n_shelves):
		shelf_col.add_child(_build_shelf(si, slots_per))

	# Progress footer
	var progress := Label.new()
	var total_authored: int = 0
	for m in _manifests.values():
		if (m as Dictionary).get("status", "").begins_with("authored_stub") or (m as Dictionary).has("acts"):
			total_authored += 1
	progress.text = "  %d of %d sticks finished · %d authored on the shelf" % [
		_finished.size(), total_authored, total_authored]
	progress.add_theme_font_size_override("font_size", 10)
	progress.add_theme_color_override("font_color", C_TXT_DIM)
	shelf_col.add_child(progress)

	# ── Blurb card column (right ~35%)
	var card_col := VBoxContainer.new()
	card_col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	card_col.size_flags_stretch_ratio = 1.0
	card_col.add_theme_constant_override("separation", 6)
	root.add_child(card_col)

	_card_title = Label.new()
	_card_title.add_theme_font_size_override("font_size", 16)
	_card_title.add_theme_color_override("font_color", C_ACCENT)
	_card_title.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	card_col.add_child(_card_title)

	_card_subtitle = Label.new()
	_card_subtitle.add_theme_font_size_override("font_size", 11)
	_card_subtitle.add_theme_color_override("font_color", C_TXT)
	_card_subtitle.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	card_col.add_child(_card_subtitle)

	_card_meta = Label.new()
	_card_meta.add_theme_font_size_override("font_size", 9)
	_card_meta.add_theme_color_override("font_color", C_TXT_DIM)
	_card_meta.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	card_col.add_child(_card_meta)

	var card_rule := ColorRect.new()
	card_rule.color = Color(C_ACCENT.r, C_ACCENT.g, C_ACCENT.b, 0.20)
	card_rule.custom_minimum_size.y = 1
	card_col.add_child(card_rule)

	_card_blurb = Label.new()
	_card_blurb.add_theme_font_size_override("font_size", 10)
	_card_blurb.add_theme_color_override("font_color", C_TXT)
	_card_blurb.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_card_blurb.size_flags_vertical = Control.SIZE_EXPAND_FILL
	card_col.add_child(_card_blurb)

	_card_status = Label.new()
	_card_status.add_theme_font_size_override("font_size", 10)
	_card_status.add_theme_color_override("font_color", C_TXT_DIM)
	card_col.add_child(_card_status)

	_card_boot_btn = Button.new()
	_card_boot_btn.text = "  BOOT  "
	_card_boot_btn.disabled = true
	_card_boot_btn.pressed.connect(_on_boot_pressed)
	card_col.add_child(_card_boot_btn)

	# Default card state (nothing hovered)
	_show_card_default()


func _build_shelf(shelf_index: int, slots_per: int) -> Control:
	var wrap := VBoxContainer.new()
	wrap.add_theme_constant_override("separation", 0)

	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", SLOT_GAP)
	row.custom_minimum_size = Vector2((SLOT_W + SLOT_GAP) * slots_per, SLOT_H)
	wrap.add_child(row)

	# Build slot lookup for this shelf.
	var slot_entry := {}     # slot_index → entry dict
	var slot_empty := {}
	for e_var in _shelf_layout.get("entries", []):
		var e: Dictionary = e_var
		if int(e.get("shelf", 0)) == shelf_index:
			slot_entry[int(e.get("slot", 0))] = e
	for e_var in _shelf_layout.get("empty_slots", []):
		var e: Dictionary = e_var
		if int(e.get("shelf", 0)) == shelf_index:
			slot_empty[int(e.get("slot", 0))] = e

	for slot in range(slots_per):
		var cart: Control = null
		if slot_entry.has(slot):
			cart = _make_cartridge_slot(slot_entry[slot])
		elif slot_empty.has(slot):
			cart = _make_empty_slot(slot_empty[slot])
		else:
			cart = _make_empty_slot({"note": ""})
		row.add_child(cart)

	# Shelf lip below the row.
	var lip := ColorRect.new()
	lip.color = C_SHELF_LIP
	lip.custom_minimum_size = Vector2(0, SHELF_LIP_H)
	wrap.add_child(lip)

	return wrap


func _make_cartridge_slot(entry: Dictionary) -> Control:
	var sid: String = String(entry.get("stick", ""))
	var manifest: Dictionary = _manifests.get(sid, {})
	var shelf: Dictionary = manifest.get("shelf", {})
	var case: String = String(entry.get("case", "cartridge_sleeve"))
	var unlocked: bool = _is_unlocked(sid)
	var finished: bool = _is_finished(sid)

	var panel := Panel.new()
	panel.custom_minimum_size = Vector2(SLOT_W, SLOT_H)
	var sb := StyleBoxFlat.new()
	sb.bg_color = C_BETA if case == "betamax_case" else (C_CART if unlocked else C_CART_DIM)
	sb.border_color = C_ACCENT if finished else Color(sb.bg_color.r * 0.7, sb.bg_color.g * 0.7, sb.bg_color.b * 0.7, 1.0)
	sb.set_border_width_all(1)
	sb.set_corner_radius_all(2)
	panel.add_theme_stylebox_override("panel", sb)

	# The label is a rotated Label on the "spine" of the cartridge —
	# faux vertical text, chunky. Uses the sticker's label_title with
	# a fallback for stub-only rows.
	var lbl := Label.new()
	lbl.text = String(shelf.get("label_title", sid.to_upper()))
	lbl.add_theme_font_size_override("font_size", 9)
	lbl.add_theme_color_override("font_color", C_LABEL if unlocked else C_LABEL_DIM)
	lbl.rotation = -PI / 2.0
	lbl.set_anchors_preset(Control.PRESET_CENTER)
	lbl.pivot_offset = Vector2(0, 0)
	lbl.position = Vector2(SLOT_W / 2 - 4, SLOT_H - 8)
	lbl.size = Vector2(SLOT_H - 16, 12)
	panel.add_child(lbl)

	# Tiny status glyph at the bottom.
	var glyph := Label.new()
	if finished:
		glyph.text = "✓"
		glyph.add_theme_color_override("font_color", C_ACCENT)
	elif unlocked:
		glyph.text = "◆"
		glyph.add_theme_color_override("font_color", C_LABEL)
	else:
		glyph.text = "·"
		glyph.add_theme_color_override("font_color", C_LOCK)
	glyph.add_theme_font_size_override("font_size", 10)
	glyph.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	glyph.position = Vector2(4, SLOT_H - 14)
	panel.add_child(glyph)

	# Interaction. Use a MouseArea via mouse_entered/exited on the panel.
	panel.mouse_filter = Control.MOUSE_FILTER_STOP
	panel.mouse_entered.connect(func() -> void: _on_cart_hover(sid))
	panel.mouse_exited.connect(func() -> void: _on_cart_unhover(sid))
	panel.gui_input.connect(func(ev: InputEvent) -> void:
		if ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed:
			if unlocked:
				picked.emit(sid))

	return panel


func _make_empty_slot(entry: Dictionary) -> Control:
	var panel := Panel.new()
	panel.custom_minimum_size = Vector2(SLOT_W, SLOT_H)
	var sb := StyleBoxFlat.new()
	sb.bg_color = C_SHELF                        # blend into shelf
	sb.border_color = Color(C_SHELF.r + 0.03, C_SHELF.g + 0.03, C_SHELF.b + 0.03, 1.0)
	sb.set_border_width_all(1)
	panel.add_theme_stylebox_override("panel", sb)

	var note: String = String(entry.get("note", ""))
	if note != "" and note != "Empty.":
		# Non-trivial empty slot (KRZ USB, Betamax tape, etc.) —
		# make it hoverable with the note as the blurb.
		panel.mouse_filter = Control.MOUSE_FILTER_STOP
		panel.mouse_entered.connect(func() -> void: _show_card_empty_note(note))
		panel.mouse_exited.connect(func() -> void: _show_card_default())
		# Tiny dot to signal "this is something."
		var dot := Label.new()
		dot.text = "·"
		dot.add_theme_color_override("font_color", C_TXT_DIM)
		dot.add_theme_font_size_override("font_size", 10)
		dot.set_anchors_preset(Control.PRESET_CENTER)
		dot.position = Vector2(SLOT_W / 2 - 3, SLOT_H / 2 - 6)
		panel.add_child(dot)
	return panel


# ─── Card panel ──────────────────────────────────────────────────

func _on_cart_hover(stick_id: String) -> void:
	_hovered_id = stick_id
	var manifest: Dictionary = _manifests.get(stick_id, {})
	var shelf: Dictionary = manifest.get("shelf", {})
	var unlocked: bool = _is_unlocked(stick_id)
	var finished: bool = _is_finished(stick_id)

	_card_title.text = String(shelf.get("label_title", stick_id.to_upper()))
	_card_subtitle.text = String(shelf.get("label_subtitle", ""))

	var meta_parts: PackedStringArray = PackedStringArray()
	if shelf.has("publisher"):
		meta_parts.append(String(shelf["publisher"]))
	if shelf.has("release_year"):
		meta_parts.append(str(int(shelf["release_year"])))
	if shelf.has("hardware"):
		meta_parts.append(String(shelf["hardware"]))
	if shelf.has("genre_stamp"):
		meta_parts.append(String(shelf["genre_stamp"]))
	_card_meta.text = "  ·  ".join(meta_parts)

	var blurb := String(shelf.get("cover_blurb", ""))
	var prior := String(shelf.get("prior_owner_note", shelf.get("prior_owner", "")))
	if prior != "":
		blurb += "\n\n" + prior
	_card_blurb.text = blurb

	if not unlocked:
		_card_status.text = "  LOCKED · finish another stick to unlock"
		_card_status.add_theme_color_override("font_color", C_LOCK)
		_card_boot_btn.disabled = true
		_card_boot_btn.text = "  LOCKED  "
	elif finished:
		_card_status.text = "  FINISHED · replay available"
		_card_status.add_theme_color_override("font_color", C_ACCENT)
		_card_boot_btn.disabled = false
		_card_boot_btn.text = "  REPLAY  "
	elif not _is_fully_playable(stick_id):
		_card_status.text = "  UNLOCKED · not yet fully implemented"
		_card_status.add_theme_color_override("font_color", C_TXT_DIM)
		_card_boot_btn.disabled = false
		_card_boot_btn.text = "  PEEK  "
	else:
		_card_status.text = "  UNLOCKED · ready to boot"
		_card_status.add_theme_color_override("font_color", C_LABEL)
		_card_boot_btn.disabled = false
		_card_boot_btn.text = "  BOOT  "


func _on_cart_unhover(stick_id: String) -> void:
	if _hovered_id == stick_id:
		_show_card_default()


func _show_card_default() -> void:
	_hovered_id = ""
	_card_title.text = "· hover a cartridge"
	_card_subtitle.text = ""
	_card_meta.text = ""
	_card_blurb.text = "The shelf is Olaf's. He built the cabin with Eddvard in '79. Most of these sticks were his. A few Tem added. The empty slots are his too — the shelf was never full."
	_card_status.text = ""
	_card_boot_btn.disabled = true
	_card_boot_btn.text = "  BOOT  "


func _show_card_empty_note(note: String) -> void:
	_hovered_id = ""
	_card_title.text = "· not a slowstick"
	_card_subtitle.text = ""
	_card_meta.text = ""
	_card_blurb.text = note
	_card_status.text = ""
	_card_boot_btn.disabled = true
	_card_boot_btn.text = "  —  "


func _on_boot_pressed() -> void:
	if _hovered_id != "" and _is_unlocked(_hovered_id):
		picked.emit(_hovered_id)


func _input(event: InputEvent) -> void:
	if event.is_action_pressed("menu_back") or (event is InputEventKey and (event as InputEventKey).keycode == KEY_ESCAPE and event.pressed):
		closed.emit()
		get_viewport().set_input_as_handled()
