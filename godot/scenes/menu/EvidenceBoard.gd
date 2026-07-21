extends Control
## THE EVIDENCE BOARD — the interactive cross-stick meta-mystery.
##
## Each slowstick hides one secret that fires a token when found. Here
## the collector PINS two discovered secrets; if they form an authored
## connection, a THREAD assembles — the resonance is named, never
## resolved. This is the deduction VERB the meta-layer lacked: the
## automatic almanac_unlocks rules assemble threads passively on
## Almanac-open, but the board makes you do the connecting yourself,
## the way Patient Mister Glass makes you pin two answers into a
## finding.
##
## Read-only over OneironauticsTokens; revealed connections persist via
## their `fires` token and light a THREADS entry in the Almanac.
##
## Data:    godot/resources/almanac/evidence_board.json
## Pattern: Almanac.gd — static build(parent), fresh each open, "ui"
##          group for F4, Esc/menu_back to close.

const DATA_PATH := "res://resources/almanac/evidence_board.json"

const C_BG     := Color(0.024, 0.020, 0.014, 0.97)
const C_ACCENT := Color(0.95, 0.78, 0.40)
const C_TEXT   := Color(0.86, 0.80, 0.66)
const C_DIM    := Color(0.48, 0.45, 0.38)
const C_LIT    := Color(0.62, 0.90, 0.68)
const C_THREAD := Color(0.80, 0.66, 0.92)
const C_PIN    := Color(0.95, 0.62, 0.42)

var _secrets: Array = []
var _connections: Array = []
var _pinned: Array = []      # token strings, max 2
var _note: String = ""


static func build(_parent: Node) -> Control:
	var panel := Control.new()
	panel.set_script(load("res://scenes/menu/EvidenceBoard.gd"))
	panel.name = "EvidenceBoard"
	return panel


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	var bank := get_node_or_null("/root/SFXBank")
	if bank: bank.play("menu_open", 0.7)
	_load_data()
	_build()


func _load_data() -> void:
	if not FileAccess.file_exists(DATA_PATH):
		return
	var f := FileAccess.open(DATA_PATH, FileAccess.READ)
	if f == null:
		return
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		_secrets = (parsed as Dictionary).get("secrets", [])
		_connections = (parsed as Dictionary).get("connections", [])


func _input(event: InputEvent) -> void:
	if event.is_action_pressed("menu_back") or \
			(event is InputEventKey and (event as InputEventKey).keycode == KEY_ESCAPE and event.pressed):
		queue_free()
		get_viewport().set_input_as_handled()


# ── data helpers ─────────────────────────────────────────────────

func _found(token: String) -> bool:
	return OneironauticsTokens.has(token)


func _found_secrets() -> Array:
	var out: Array = []
	for s_v in _secrets:
		var s: Dictionary = s_v
		if _found(String(s.get("token", ""))):
			out.append(s)
	return out


func _is_revealed(conn: Dictionary) -> bool:
	return OneironauticsTokens.has(String(conn.get("fires", "")))


func _revealed_count() -> int:
	var n := 0
	for c_v in _connections:
		if _is_revealed(c_v):
			n += 1
	return n


func _match_connection(a: String, b: String) -> Dictionary:
	for c_v in _connections:
		var c: Dictionary = c_v
		var pair: Array = c.get("pair", [])
		if pair.size() == 2 and pair.has(a) and pair.has(b):
			return c
	return {}


# ── interaction ──────────────────────────────────────────────────

func _toggle_pin(token: String) -> void:
	if _pinned.has(token):
		_pinned.erase(token)
	elif _pinned.size() < 2:
		_pinned.append(token)
	else:
		_note = "you can hold two clues against each other at a time. unpin one first."
		var bank := get_node_or_null("/root/SFXBank")
		if bank: bank.play("pair_cold", 0.5)
		_rebuild()
		return
	_note = ""
	_rebuild()


func _connect() -> void:
	if _pinned.size() != 2:
		return
	var conn := _match_connection(String(_pinned[0]), String(_pinned[1]))
	var bank := get_node_or_null("/root/SFXBank")
	if conn.is_empty():
		_note = "these two do not answer each other. not yet."
		if bank: bank.play("pair_cold", 0.55)
	elif _is_revealed(conn):
		_note = "already assembled. the thread is on the board."
		if bank: bank.play("page_turn", 0.5)
	else:
		OneironauticsTokens.add(String(conn.get("fires", "")))
		_note = "· a thread assembles ·"
		if bank: bank.play("win_chord", 0.7)
		_pinned.clear()
	_rebuild()


func _rebuild() -> void:
	for c in get_children():
		c.queue_free()
	_build()


# ── layout ───────────────────────────────────────────────────────

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
	card.offset_left = -470
	card.offset_right = 470
	card.offset_top = -310
	card.offset_bottom = 310
	add_child(card)

	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 26)
	margin.add_theme_constant_override("margin_right", 26)
	margin.add_theme_constant_override("margin_top", 20)
	margin.add_theme_constant_override("margin_bottom", 20)
	card.add_child(margin)

	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 8)
	margin.add_child(col)

	var header := Label.new()
	header.text = "· THE EVIDENCE BOARD ·"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 22)
	header.add_theme_color_override("font_color", C_ACCENT)
	col.add_child(header)

	var sub := Label.new()
	sub.text = "%d of %d secrets found · %d of %d threads assembled · pin two, and see if they answer each other" % [
		_found_secrets().size(), _secrets.size(), _revealed_count(), _connections.size()]
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

	# ── left · discovered secrets (pinnable) ──
	var left_scroll := ScrollContainer.new()
	left_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	left_scroll.custom_minimum_size.x = 400
	left_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.add_child(left_scroll)
	var left := VBoxContainer.new()
	left.add_theme_constant_override("separation", 6)
	left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	left_scroll.add_child(left)

	var found := _found_secrets()
	if found.is_empty():
		var none := Label.new()
		none.text = "no secrets found yet. every stick keeps one. go and stay too long in one."
		none.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		none.add_theme_font_size_override("font_size", 13)
		none.add_theme_color_override("font_color", C_DIM)
		left.add_child(none)
	for s_v in found:
		var s: Dictionary = s_v
		var tok := String(s.get("token", ""))
		var pinned: bool = _pinned.has(tok)
		var b := Button.new()
		b.text = "%s %s · %s" % ["[◆]" if pinned else "[ ]", String(s.get("label", "?")), String(s.get("stick", ""))]
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.add_theme_font_size_override("font_size", 14)
		b.add_theme_color_override("font_color", C_PIN if pinned else C_TEXT)
		var t := tok
		b.pressed.connect(func() -> void: _toggle_pin(t))
		left.add_child(b)
		var note := Label.new()
		note.text = "     " + String(s.get("note", ""))
		note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		note.add_theme_font_size_override("font_size", 11)
		note.add_theme_color_override("font_color", C_DIM)
		left.add_child(note)

	# secrets still out in the sticks — count only, no spoilers
	var still_out: int = _secrets.size() - found.size()
	if still_out > 0:
		var locked := Label.new()
		locked.text = "· %d more secret%s still in the sticks ·" % [still_out, "" if still_out == 1 else "s"]
		locked.add_theme_font_size_override("font_size", 11)
		locked.add_theme_color_override("font_color", C_DIM)
		left.add_child(locked)

	# ── right · assembled threads ──
	var right_scroll := ScrollContainer.new()
	right_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	right_scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	right_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.add_child(right_scroll)
	var right := VBoxContainer.new()
	right.add_theme_constant_override("separation", 12)
	right.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	right_scroll.add_child(right)

	var any_revealed := false
	for c_v in _connections:
		var c: Dictionary = c_v
		if not _is_revealed(c):
			continue
		any_revealed = true
		var trow := VBoxContainer.new()
		trow.add_theme_constant_override("separation", 2)
		right.add_child(trow)
		var ttl := Label.new()
		ttl.text = "✦ " + String(c.get("title", "?"))
		ttl.add_theme_font_size_override("font_size", 15)
		ttl.add_theme_color_override("font_color", C_THREAD)
		trow.add_child(ttl)
		var txt := Label.new()
		txt.text = String(c.get("text", ""))
		txt.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		txt.add_theme_font_size_override("font_size", 12)
		txt.add_theme_color_override("font_color", C_TEXT)
		trow.add_child(txt)
	if not any_revealed:
		var yet := Label.new()
		yet.text = "no threads assembled yet. two clues that share a year, a shape, a hand, a note — hold them together."
		yet.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		yet.add_theme_font_size_override("font_size", 12)
		yet.add_theme_color_override("font_color", C_DIM)
		right.add_child(yet)

	# ── connect bar ──
	var rule2 := ColorRect.new()
	rule2.color = Color(C_ACCENT.r, C_ACCENT.g, C_ACCENT.b, 0.3)
	rule2.custom_minimum_size.y = 1
	col.add_child(rule2)

	var bar := HBoxContainer.new()
	bar.add_theme_constant_override("separation", 12)
	col.add_child(bar)

	var pinned_lbl := Label.new()
	pinned_lbl.text = "pinned · %d of 2" % _pinned.size()
	pinned_lbl.add_theme_font_size_override("font_size", 13)
	pinned_lbl.add_theme_color_override("font_color", C_PIN if _pinned.size() == 2 else C_DIM)
	bar.add_child(pinned_lbl)

	var connect_btn := Button.new()
	connect_btn.text = "  · hold them against each other ·  "
	connect_btn.add_theme_font_size_override("font_size", 14)
	connect_btn.disabled = _pinned.size() != 2
	connect_btn.pressed.connect(_connect)
	bar.add_child(connect_btn)

	if _note != "":
		var msg := Label.new()
		msg.text = _note
		msg.add_theme_font_size_override("font_size", 12)
		msg.add_theme_color_override("font_color", C_LIT if _note.begins_with("·") else C_DIM)
		bar.add_child(msg)

	var close := Button.new()
	close.text = "  · close ·  "
	close.add_theme_font_size_override("font_size", 14)
	close.pressed.connect(func() -> void: queue_free())
	col.add_child(close)

	GamepadMgr.focus_first.call_deferred(self)
