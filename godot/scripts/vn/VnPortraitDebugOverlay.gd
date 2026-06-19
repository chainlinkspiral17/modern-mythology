extends CanvasLayer
## VnPortraitDebugOverlay
## ════════════════════════════════════════════════════════════════
## Per-portrait debug controls for VN scenes. Shows when the mouse
## is released (Input.MOUSE_MODE_VISIBLE), pinned top-right above
## any VN HUD. Lists every active 3D portrait (Sam, stranger, etc.)
## with controls:
##   · cycle mood through Portrait3D.MOOD_TABLE
##   · toggle demon static shader
##   · live-adjust key / fill / back light colour and energy
##   · reload the GLB (hot-swap after re-export)
##
## Renderable PNG / composition / placeholder portraits are skipped
## — they have no 3D state to tune. CharLayer.get_active_portrait3d_list
## is the single source of truth for what's listed here.
##
## REVEAL POLICY
## The overlay is OPT-IN. Default state on every scene start is
## HIDDEN — debug controls do NOT pop up just because the mouse is
## released. The user toggles them with Shift+F12 (also F4 still
## acts as the master kill switch, hiding HUD globally per
## FirstPersonController.hud_visible). The reveal preference is a
## static var so a single toggle persists across scene loads — once
## you've turned it off it stays off until you choose to bring it
## back, no "every new scene I have to dismiss it again" friction.
##
## F4 INTEGRATION
## F4 is the master "hide all HUD" toggle (FirstPersonController.
## hud_visible static var). The overlay's per-frame visibility check
## ANDs in hud_visible AND _show_pref. The overlay ALSO intercepts
## F4 itself so VN scenes without a walkable FirstPersonController
## in the tree still toggle the HUD — _input fires globally, FPC
## just owns the action method.
## ════════════════════════════════════════════════════════════════

const FPC_SCRIPT = preload("res://scripts/FirstPersonController.gd")

# Persistent "user wants the per-portrait debug panel" preference.
# Static so toggling it once carries across every subsequent scene
# load. Default false — never show without explicit opt-in.
static var _show_pref: bool = false

const MOODS: Array[String] = [
	"neutral", "happy", "sad", "surprised", "angry", "tired", "nervous",
]

var _char_layer: Control = null
var _selected_key: String = ""

# Built once in _ready, contents rebuilt each refresh tick.
var _root_panel: PanelContainer
var _picker_list: VBoxContainer
var _controls_box: VBoxContainer
var _refresh_timer: Timer


func _ready() -> void:
	layer = 120     # above the music-player HUD (110) and the dialog box
	add_to_group("ui")  # F4 sweep hides us with the rest of the HUD
	_char_layer = get_parent() as Control
	_build_ui()
	# Sync to the global HUD-visibility state on spawn. Prevents the
	# panel popping in mid-scene if the user has F4'd the HUD off
	# before this overlay's _ready landed.
	visible = false  # opt-in default — see "REVEAL POLICY" header
	_refresh_timer = Timer.new()
	_refresh_timer.wait_time = 0.5
	_refresh_timer.one_shot = false
	_refresh_timer.timeout.connect(_rebuild_picker)
	add_child(_refresh_timer)
	_refresh_timer.start()
	_rebuild_picker()
	set_process(true)


func _process(_delta: float) -> void:
	# Visible only if THREE conditions all hold:
	#   1. the user opted in via Shift+F12 (_show_pref)
	#   2. F4 hasn't nuked the HUD (FPC_SCRIPT.hud_visible)
	#   3. the mouse is released so clicks can land (MOUSE_MODE_VISIBLE)
	# Any one being false hides the panel. This is what makes the
	# overlay actually obey F4 — without the hud_visible AND, the
	# F4 sweep would set us false and _process would set us true the
	# next frame, fighting the toggle.
	var mouse_free: bool = Input.mouse_mode == Input.MOUSE_MODE_VISIBLE
	visible = _show_pref and FPC_SCRIPT.hud_visible and mouse_free


func _input(event: InputEvent) -> void:
	if not (event is InputEventKey) or not event.pressed or event.echo:
		return
	# Shift+F12 — toggle the per-portrait overlay's reveal pref.
	# Persisted via the static _show_pref so the choice survives
	# scene swaps (no "dismiss it every scene" tax).
	if event.keycode == KEY_F12 and event.shift_pressed:
		_show_pref = not _show_pref
		print("[VnPortraitDebug] reveal pref = %s" % _show_pref)
		get_viewport().set_input_as_handled()
		return
	# F4 — global HUD kill switch. Mirror the FPC binding so VN
	# scenes (which have no walkable FirstPersonController in the
	# tree) still toggle. _apply_hud_visibility walks the tree.
	if event.keycode == KEY_F4:
		FPC_SCRIPT.hud_visible = not FPC_SCRIPT.hud_visible
		_apply_global_hud_visibility(FPC_SCRIPT.hud_visible)
		print("[VnPortraitDebug] F4 → HUD visible = %s" % FPC_SCRIPT.hud_visible)
		get_viewport().set_input_as_handled()


# Mirrors FirstPersonController._apply_hud_visibility — walks the
# tree and hides every HUD-flavored CanvasLayer + every "ui"-group
# member. Lives here so VN scenes work without an FPC in the tree.
func _apply_global_hud_visibility(vis: bool) -> void:
	_walk_hide(get_tree().root, vis)
	for n in get_tree().get_nodes_in_group("ui"):
		if "visible" in n:
			n.visible = vis


func _walk_hide(node: Node, vis: bool) -> void:
	if node is CanvasLayer:
		var nm: String = node.name
		var is_hud: bool = (
			"HUD" in nm or "Hud" in nm or
			"UI" in nm or "Ui" in nm or
			"Debug" in nm or "Menu" in nm or
			node.is_in_group("ui")
		)
		if is_hud:
			(node as CanvasLayer).visible = vis
		return
	for child in node.get_children():
		_walk_hide(child, vis)


# ── UI scaffolding ────────────────────────────────────────────────
func _build_ui() -> void:
	_root_panel = PanelContainer.new()
	_root_panel.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	_root_panel.offset_left = -340.0
	_root_panel.offset_right = -16.0
	_root_panel.offset_top = 16.0
	_root_panel.offset_bottom = 540.0
	add_child(_root_panel)

	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.06, 0.07, 0.10, 0.92)
	sb.border_color = Color(0.78, 0.62, 0.42, 0.65)
	sb.border_width_left = 1
	sb.border_width_top = 1
	sb.border_width_right = 1
	sb.border_width_bottom = 1
	sb.corner_radius_top_left = 4
	sb.corner_radius_top_right = 4
	sb.corner_radius_bottom_left = 4
	sb.corner_radius_bottom_right = 4
	sb.content_margin_left = 10
	sb.content_margin_top = 10
	sb.content_margin_right = 10
	sb.content_margin_bottom = 10
	_root_panel.add_theme_stylebox_override("panel", sb)

	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 8)
	_root_panel.add_child(col)

	var title := Label.new()
	title.text = "VN · 3D PORTRAITS"
	title.add_theme_font_size_override("font_size", 13)
	title.add_theme_color_override("font_color", Color(0.92, 0.78, 0.55, 1.0))
	col.add_child(title)

	var hint := Label.new()
	hint.text = "pick a portrait below to control it"
	hint.add_theme_font_size_override("font_size", 10)
	hint.add_theme_color_override("font_color", Color(0.65, 0.65, 0.72, 1.0))
	col.add_child(hint)

	var sep1 := HSeparator.new()
	col.add_child(sep1)

	_picker_list = VBoxContainer.new()
	_picker_list.add_theme_constant_override("separation", 4)
	col.add_child(_picker_list)

	var sep2 := HSeparator.new()
	col.add_child(sep2)

	_controls_box = VBoxContainer.new()
	_controls_box.add_theme_constant_override("separation", 4)
	col.add_child(_controls_box)


# ── Picker ────────────────────────────────────────────────────────
# Rebuilt every refresh tick. Preserves _selected_key across rebuilds
# when the chosen portrait is still active.
func _rebuild_picker() -> void:
	for c in _picker_list.get_children():
		c.queue_free()
	var active: Array = []
	if _char_layer != null and _char_layer.has_method("get_active_portrait3d_list"):
		active = _char_layer.get_active_portrait3d_list()
	if active.is_empty():
		var none := Label.new()
		none.text = "(no 3D portraits active)"
		none.add_theme_font_size_override("font_size", 11)
		none.add_theme_color_override("font_color", Color(0.55, 0.55, 0.62, 1.0))
		_picker_list.add_child(none)
		_selected_key = ""
		_rebuild_controls(null)
		return
	# If selection has fallen off the list, default to the first.
	var still_present: bool = false
	for entry: Dictionary in active:
		if entry["name"] == _selected_key:
			still_present = true
			break
	if not still_present:
		_selected_key = active[0]["name"]
	for entry: Dictionary in active:
		var b := Button.new()
		var marker: String = "●  " if entry["name"] == _selected_key else "○  "
		b.text = "%s%s · %s" % [marker, entry["pos"], entry["name"]]
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.focus_mode = Control.FOCUS_NONE
		var picked_key: String = entry["name"]
		b.pressed.connect(func() -> void:
			_selected_key = picked_key
			_rebuild_picker()
		)
		_picker_list.add_child(b)
	# Re-render controls with the current selection's portrait3d.
	var sel: Dictionary = {}
	for entry: Dictionary in active:
		if entry["name"] == _selected_key:
			sel = entry
			break
	_rebuild_controls(sel if not sel.is_empty() else null)


# ── Controls — keyed to the selected portrait ─────────────────────
func _rebuild_controls(sel) -> void:
	for c in _controls_box.get_children():
		c.queue_free()
	if sel == null:
		return
	var p3d: Node = sel["portrait3d"]
	if p3d == null or not is_instance_valid(p3d):
		return

	# Header — what's selected.
	var head := Label.new()
	head.text = "→ %s (%s)" % [sel["name"], sel["pos"]]
	head.add_theme_font_size_override("font_size", 12)
	head.add_theme_color_override("font_color", Color(1.0, 0.86, 0.62, 1.0))
	_controls_box.add_child(head)

	# 1. Cycle mood
	var current_mood: String = "neutral"
	if "_mood_id" in p3d:
		current_mood = String(p3d._mood_id)
	var mood_row := HBoxContainer.new()
	mood_row.add_theme_constant_override("separation", 4)
	_controls_box.add_child(mood_row)
	var mood_lbl := Label.new()
	mood_lbl.text = "mood: %s" % current_mood
	mood_lbl.add_theme_font_size_override("font_size", 11)
	mood_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	mood_row.add_child(mood_lbl)
	var mood_prev := Button.new()
	mood_prev.text = "←"
	mood_prev.focus_mode = Control.FOCUS_NONE
	mood_prev.custom_minimum_size.x = 28
	mood_prev.pressed.connect(_cycle_mood.bind(p3d, -1))
	mood_row.add_child(mood_prev)
	var mood_next := Button.new()
	mood_next.text = "→"
	mood_next.focus_mode = Control.FOCUS_NONE
	mood_next.custom_minimum_size.x = 28
	mood_next.pressed.connect(_cycle_mood.bind(p3d, +1))
	mood_row.add_child(mood_next)

	# 2. Demon toggle
	var demon_btn := Button.new()
	var demon_on: bool = false
	if "_demon_mode" in p3d:
		demon_on = bool(p3d._demon_mode)
	demon_btn.text = "demon static: %s" % ("ON" if demon_on else "off")
	demon_btn.focus_mode = Control.FOCUS_NONE
	demon_btn.pressed.connect(func() -> void:
		var now_on: bool = bool(p3d._demon_mode) if "_demon_mode" in p3d else false
		if p3d.has_method("set_demon_mode"):
			p3d.set_demon_mode(not now_on)
		_rebuild_controls(sel)
	)
	_controls_box.add_child(demon_btn)

	# 3. Lighting palette — three pairs (key / fill / back) of energy
	#    bumpers + a colour-temp warm/cool cycle. Reads/writes the
	#    portrait's resting palette so mood deltas still compose.
	for light_key in ["key", "fill", "back"]:
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 4)
		_controls_box.add_child(row)
		var lbl := Label.new()
		var rest_e: float = 0.0
		if light_key == "key" and "_rest_key_energy" in p3d:
			rest_e = float(p3d._rest_key_energy)
		elif light_key == "fill" and "_rest_fill_energy" in p3d:
			rest_e = float(p3d._rest_fill_energy)
		elif light_key == "back" and "_rest_back_energy" in p3d:
			rest_e = float(p3d._rest_back_energy)
		lbl.text = "%s   E=%.2f" % [light_key, rest_e]
		lbl.add_theme_font_size_override("font_size", 11)
		lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(lbl)
		var down := Button.new()
		down.text = "−"
		down.focus_mode = Control.FOCUS_NONE
		down.custom_minimum_size.x = 28
		down.pressed.connect(_bump_energy.bind(p3d, light_key, -0.10, sel))
		row.add_child(down)
		var up := Button.new()
		up.text = "+"
		up.focus_mode = Control.FOCUS_NONE
		up.custom_minimum_size.x = 28
		up.pressed.connect(_bump_energy.bind(p3d, light_key, +0.10, sel))
		row.add_child(up)
		var warm := Button.new()
		warm.text = "warm"
		warm.focus_mode = Control.FOCUS_NONE
		warm.pressed.connect(_shift_temp.bind(p3d, light_key, +1, sel))
		row.add_child(warm)
		var cool := Button.new()
		cool.text = "cool"
		cool.focus_mode = Control.FOCUS_NONE
		cool.pressed.connect(_shift_temp.bind(p3d, light_key, -1, sel))
		row.add_child(cool)

	# 4. Reload GLB
	var reload_btn := Button.new()
	reload_btn.text = "reload GLB"
	reload_btn.focus_mode = Control.FOCUS_NONE
	reload_btn.pressed.connect(_reload_glb.bind(p3d, sel["glb_path"]))
	_controls_box.add_child(reload_btn)

	# 5. GLB-path readout
	var path_lbl := Label.new()
	path_lbl.text = sel["glb_path"]
	path_lbl.add_theme_font_size_override("font_size", 9)
	path_lbl.add_theme_color_override("font_color", Color(0.55, 0.55, 0.62, 1.0))
	path_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_controls_box.add_child(path_lbl)


# ── Actions ───────────────────────────────────────────────────────
func _cycle_mood(p3d: Node, delta: int) -> void:
	if not is_instance_valid(p3d):
		return
	var cur: String = "neutral"
	if "_mood_id" in p3d:
		cur = String(p3d._mood_id)
	var idx: int = MOODS.find(cur)
	if idx < 0:
		idx = 0
	idx = (idx + delta + MOODS.size()) % MOODS.size()
	if p3d.has_method("set_expression"):
		p3d.set_expression(MOODS[idx])
	_rebuild_picker()


func _bump_energy(p3d: Node, light_key: String, delta: float, sel) -> void:
	if not is_instance_valid(p3d):
		return
	var prop: String = "_rest_%s_energy" % light_key
	if not (prop in p3d):
		return
	var cur: float = float(p3d.get(prop))
	cur = clamp(cur + delta, 0.0, 4.0)
	p3d.set(prop, cur)
	# Re-apply mood so the rest value lands on the live light node.
	if p3d.has_method("set_expression") and "_mood_id" in p3d:
		p3d.set_expression(String(p3d._mood_id))
	_rebuild_controls(sel)


func _shift_temp(p3d: Node, light_key: String, warm_dir: int, sel) -> void:
	# Warm / cool dial — nudges the RGB toward sodium-orange or
	# moonlight-blue while preserving brightness. Useful to taste-
	# test character lighting palettes without editing code.
	if not is_instance_valid(p3d):
		return
	var prop: String = "_rest_%s_color" % light_key
	if not (prop in p3d):
		return
	var c: Color = p3d.get(prop)
	var step: float = 0.06
	if warm_dir > 0:
		c.r = clamp(c.r + step, 0.0, 1.0)
		c.b = clamp(c.b - step, 0.0, 1.0)
	else:
		c.r = clamp(c.r - step, 0.0, 1.0)
		c.b = clamp(c.b + step, 0.0, 1.0)
	p3d.set(prop, c)
	if p3d.has_method("set_expression") and "_mood_id" in p3d:
		p3d.set_expression(String(p3d._mood_id))
	_rebuild_controls(sel)


func _reload_glb(p3d: Node, glb_path: String) -> void:
	if not is_instance_valid(p3d) or glb_path == "":
		return
	# Force a fresh load by clearing the cached path FIRST — otherwise
	# Portrait3D.load_character sees same-glb-as-before and no-ops.
	if "_loaded_glb_path" in p3d:
		p3d._loaded_glb_path = ""
	var cur_expr: String = ""
	if "_mood_id" in p3d:
		cur_expr = String(p3d._mood_id)
	if p3d.has_method("load_character"):
		p3d.load_character(glb_path, cur_expr)
	print("[VnPortraitDebug] reloaded GLB %s" % glb_path)
