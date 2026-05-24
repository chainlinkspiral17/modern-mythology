extends Control
## Character portrait layer — left / center / right slots.
##
## Portrait source preference, per character:
##   1. ASCII composition at  res://resources/substrates/compositions/portrait_<char>.json
##   2. PNG texture at        res://assets/characters/<char>/<char>_<expr>.png
##   3. Animated placeholder silhouette
##
## Lookup keys are lowercased so scene scripts using either "John" or "john"
## resolve to the same files.

const ASCII_COMPOSITION_SCRIPT := preload("res://scenes/game/AsciiComposition.gd")
const PORTRAIT_COMP_ROOT  := "res://resources/substrates/compositions/"
const PORTRAIT_TEX_ROOT   := "res://assets/characters/"

# Expression tint multipliers applied to mono substrate portraits via modulate.
# Mirrors the table in tools/raster_substrate.py.
const EXPR_TINTS := {
	"neutral":   Color(1.00, 1.00, 1.00),
	"happy":     Color(1.00, 0.96, 0.80),
	"excited":   Color(1.00, 0.96, 0.80),
	"pleased":   Color(1.00, 0.96, 0.80),
	"warm":      Color(1.00, 0.96, 0.80),
	"sad":       Color(0.72, 0.82, 1.00),
	"melancholy":Color(0.72, 0.82, 1.00),
	"upset":     Color(0.72, 0.82, 1.00),
	"surprised": Color(1.00, 1.00, 0.78),
	"shocked":   Color(1.00, 1.00, 0.78),
	"wide":      Color(1.00, 1.00, 0.78),
	"angry":     Color(1.00, 0.55, 0.50),
	"furious":   Color(1.00, 0.55, 0.50),
	"frustrated":Color(1.00, 0.55, 0.50),
	"tired":     Color(0.78, 0.82, 0.92),
	"nervous":   Color(0.92, 0.95, 1.00),
	"scared":    Color(0.92, 0.95, 1.00),
	"uneasy":    Color(0.92, 0.95, 1.00),
}

const POSITIONS := {
	"left":   Vector2(160, 55),
	"center": Vector2(480, 55),
	"right":  Vector2(800, 55),
}
const SPRITE_W    := 320.0
const SPRITE_H    := 575.0
const IDLE_AMP    := 5.0
const IDLE_PERIOD := 2.5
const IDLE_PHASE  := {"left": 0.0, "center": 0.85, "right": 1.7}

# slot -> {name, expr, node: Control}
var _slots: Dictionary = {"left": null, "center": null, "right": null}
var _t:     float      = 0.0


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _process(delta: float) -> void:
	_t += delta
	for pos: String in _slots:
		var slot = _slots[pos]
		if slot == null:
			continue
		var node: Control = slot["node"]
		var phase: float  = IDLE_PHASE[pos]
		node.position.y   = POSITIONS[pos].y + sin((_t + phase) * TAU / IDLE_PERIOD) * IDLE_AMP


# ── Public API ────────────────────────────────────────────────────────────────

func show_character(char_name: String, expr: String, pos: String) -> void:
	if not POSITIONS.has(pos):
		pos = "center"
	var slot = _slots[pos]
	if slot != null and slot["name"] != char_name:
		_fade_out_free(slot["node"])
		slot = null
	if slot == null:
		var node := _make_portrait(char_name, expr, pos)
		_slots[pos] = {"name": char_name, "expr": expr, "node": node}
	else:
		_update_expr(slot["node"], char_name, expr)
		slot["expr"] = expr


func update_expression(char_name: String, expr: String) -> void:
	for pos: String in _slots:
		var slot = _slots[pos]
		if slot != null and slot["name"] == char_name:
			_update_expr(slot["node"], char_name, expr)
			slot["expr"] = expr


func hide_at(pos: String) -> void:
	var slot = _slots.get(pos)
	if slot != null:
		_fade_out_free(slot["node"])
		_slots[pos] = null


func hide_all() -> void:
	for pos: String in _slots:
		hide_at(pos)


func activate_speaker(char_name: String) -> void:
	for pos: String in _slots:
		var slot = _slots[pos]
		if slot == null:
			continue
		var is_active: bool = (char_name == "" or slot["name"] == char_name)
		var target: Color   = Color.WHITE if is_active else Color(0.55, 0.55, 0.55, 0.75)
		var tw := (slot["node"] as Control).create_tween()
		tw.tween_property(slot["node"], "modulate", target, 0.2)


func get_pos_for_char(char_name: String) -> String:
	for pos: String in _slots:
		var slot = _slots[pos]
		if slot != null and slot["name"] == char_name:
			return pos
	return "center"


# ── Portrait construction ─────────────────────────────────────────────────────

func _make_portrait(char_name: String, expr: String, pos: String) -> Control:
	var wrapper := Control.new()
	wrapper.custom_minimum_size = Vector2(SPRITE_W, SPRITE_H)
	wrapper.size                = Vector2(SPRITE_W, SPRITE_H)
	wrapper.position            = POSITIONS[pos]
	wrapper.modulate.a          = 0.0

	var key := char_name.to_lower()
	var comp_path := PORTRAIT_COMP_ROOT + "portrait_" + key + ".json"
	var tex_path  := "%s%s/%s_%s.png" % [PORTRAIT_TEX_ROOT, key, key, expr]

	if FileAccess.file_exists(comp_path):
		var comp := Control.new()
		comp.set_script(ASCII_COMPOSITION_SCRIPT)
		comp.size = Vector2(SPRITE_W, SPRITE_H)
		comp.custom_minimum_size = Vector2(SPRITE_W, SPRITE_H)
		wrapper.add_child(comp)
		comp.call_deferred("load_composition", "portrait_" + key)
		wrapper.set_meta("kind", "composition")
		wrapper.set_meta("comp", comp)
		_apply_substrate_tint(wrapper, expr)
	elif ResourceLoader.exists(tex_path):
		var tr := TextureRect.new()
		tr.texture               = ResourceLoader.load(tex_path) as Texture2D
		tr.stretch_mode          = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		tr.custom_minimum_size   = Vector2(SPRITE_W, SPRITE_H)
		wrapper.add_child(tr)
		wrapper.set_meta("kind", "texture")
	else:
		wrapper.add_child(_make_placeholder(char_name, expr))
		wrapper.set_meta("kind", "placeholder")

	add_child(wrapper)
	var tw := wrapper.create_tween()
	tw.tween_property(wrapper, "modulate:a", 1.0, 0.3)
	return wrapper


func _update_expr(wrapper: Control, char_name: String, expr: String) -> void:
	var kind: String = wrapper.get_meta("kind", "placeholder")
	var key := char_name.to_lower()
	if kind == "composition":
		_apply_substrate_tint(wrapper, expr)
	elif kind == "texture":
		var tr := wrapper.get_child(0) as TextureRect
		var path := "%s%s/%s_%s.png" % [PORTRAIT_TEX_ROOT, key, key, expr]
		if ResourceLoader.exists(path):
			tr.texture = ResourceLoader.load(path) as Texture2D
	else:
		var ph: Control = wrapper.get_child(0)
		if ph.has_meta("expr_lbl"):
			(ph.get_meta("expr_lbl") as Label).text = "[ %s ]" % expr
		if ph.has_meta("border"):
			_apply_expr_tint(ph.get_meta("border") as Panel, _char_color(char_name), expr)


# ── Substrate (ASCII composition) portrait tint ───────────────────────────────

func _apply_substrate_tint(wrapper: Control, expr: String) -> void:
	# Tint the composition child rather than the wrapper so the speaker-active
	# fade (which writes wrapper.modulate) composes cleanly with the expression.
	var comp: Control = wrapper.get_meta("comp", null) as Control
	if comp == null:
		return
	comp.modulate = EXPR_TINTS.get(expr, EXPR_TINTS["neutral"])


func _fade_out_free(node: Control) -> void:
	var tw := node.create_tween()
	tw.tween_property(node, "modulate:a", 0.0, 0.25)
	tw.tween_callback(node.queue_free)


# ── Placeholder portrait ──────────────────────────────────────────────────────

func _make_placeholder(char_name: String, expr: String) -> Control:
	var col := _char_color(char_name)
	var ph  := Control.new()
	ph.custom_minimum_size = Vector2(SPRITE_W, SPRITE_H)

	# Background fill
	var bg := Panel.new()
	bg.size = Vector2(SPRITE_W, SPRITE_H)
	var bg_st := StyleBoxFlat.new()
	bg_st.bg_color = Color(col.r * 0.10, col.g * 0.10, col.b * 0.10, 0.92)
	bg_st.border_color = Color(col.r, col.g, col.b, 0.0)
	bg_st.set_border_width_all(0)
	bg.add_theme_stylebox_override("panel", bg_st)
	ph.add_child(bg)

	# Colored border panel (expression-tinted)
	var border := Panel.new()
	border.size = Vector2(SPRITE_W, SPRITE_H)
	_apply_expr_tint(border, col, expr)
	ph.add_child(border)
	ph.set_meta("border", border)

	# Head oval
	var hw := 96.0
	var hh := 118.0
	var head := Panel.new()
	head.position           = Vector2((SPRITE_W - hw) * 0.5, 74.0)
	head.custom_minimum_size = Vector2(hw, hh)
	var h_st := StyleBoxFlat.new()
	h_st.bg_color = Color(col.r * 0.42, col.g * 0.42, col.b * 0.42, 0.95)
	var r := int(hw * 0.5)
	h_st.corner_radius_top_left     = r
	h_st.corner_radius_top_right    = r
	h_st.corner_radius_bottom_left  = r
	h_st.corner_radius_bottom_right = r
	head.add_theme_stylebox_override("panel", h_st)
	ph.add_child(head)

	# Body shape
	var bw := 164.0
	var body := Panel.new()
	body.position            = Vector2((SPRITE_W - bw) * 0.5, 214.0)
	body.custom_minimum_size = Vector2(bw, 234.0)
	var b_st := StyleBoxFlat.new()
	b_st.bg_color = Color(col.r * 0.30, col.g * 0.30, col.b * 0.30, 0.90)
	b_st.corner_radius_top_left  = 20
	b_st.corner_radius_top_right = 20
	body.add_theme_stylebox_override("panel", b_st)
	ph.add_child(body)

	# Name label
	var name_lbl := Label.new()
	name_lbl.text                = char_name.capitalize()
	name_lbl.position            = Vector2(0.0, SPRITE_H - 90.0)
	name_lbl.size                = Vector2(SPRITE_W, 32.0)
	name_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	name_lbl.add_theme_color_override("font_color", col)
	name_lbl.add_theme_font_size_override("font_size", 15)
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		name_lbl.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
	ph.add_child(name_lbl)

	# Expression label
	var expr_lbl := Label.new()
	expr_lbl.text                = "[ %s ]" % expr
	expr_lbl.position            = Vector2(0.0, SPRITE_H - 54.0)
	expr_lbl.size                = Vector2(SPRITE_W, 22.0)
	expr_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	expr_lbl.add_theme_color_override("font_color", Color(col.r, col.g, col.b, 0.5))
	expr_lbl.add_theme_font_size_override("font_size", 10)
	ph.add_child(expr_lbl)
	ph.set_meta("expr_lbl", expr_lbl)

	return ph


func _apply_expr_tint(border: Panel, base: Color, expr: String) -> void:
	var c := base
	match expr:
		"happy", "excited", "pleased", "warm":
			c = Color(minf(base.r + 0.12, 1.0), base.g, base.b * 0.75)
		"sad", "melancholy", "upset", "tired":
			c = Color(base.r * 0.65, base.g * 0.75, minf(base.b + 0.18, 1.0))
		"angry", "furious", "frustrated":
			c = Color(minf(base.r + 0.35, 1.0), base.g * 0.45, base.b * 0.45)
		"surprised", "shocked", "wide":
			c = Color(minf(base.r + 0.15, 1.0), minf(base.g + 0.15, 1.0), base.b * 0.6)
		"nervous", "scared", "uneasy":
			c = Color(minf(base.r + 0.08, 1.0), base.g * 0.9, minf(base.b + 0.08, 1.0))
	var st := StyleBoxFlat.new()
	st.bg_color = Color(0, 0, 0, 0)
	st.border_color = Color(c.r, c.g, c.b, 0.45)
	st.set_border_width_all(1)
	border.add_theme_stylebox_override("panel", st)


func _char_color(name: String) -> Color:
	var h := (name.hash() % 360 + 360) % 360
	return Color.from_hsv(h / 360.0, 0.52, 0.84)
