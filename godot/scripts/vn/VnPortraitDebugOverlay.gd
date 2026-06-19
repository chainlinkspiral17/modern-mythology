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
	# Pinned bottom-LEFT, below the typical portrait zone (mid-screen
	# left/right slots) and above any toast/footer. Narrow enough
	# (~240px) to not crowd the dialog box. Top-right was inside
	# Sam's portrait band — see user note about the panel obscuring
	# the right-slot portrait.
	_root_panel.set_anchors_and_offsets_preset(Control.PRESET_LEFT_WIDE)
	_root_panel.offset_left = 16.0
	_root_panel.offset_right = 296.0
	_root_panel.offset_top = 40.0
	_root_panel.offset_bottom = -16.0
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

	# Wrap controls in a ScrollContainer so the now-expanded panel
	# can list more knobs than fit vertically. size_flags_vertical
	# = SIZE_EXPAND_FILL lets it eat the remaining height of col.
	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	col.add_child(scroll)

	_controls_box = VBoxContainer.new()
	_controls_box.add_theme_constant_override("separation", 4)
	_controls_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(_controls_box)


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

	_section_label("CAMERA")

	# 4. FOV nudger
	var fov_cur: float = 35.0
	if "_rest_cam_fov" in p3d:
		fov_cur = float(p3d._rest_cam_fov)
	_add_pm_row("fov: %.0f°" % fov_cur,
		_bump_fov.bind(p3d, -2.0, sel),
		_bump_fov.bind(p3d, +2.0, sel))

	# 5. Camera pitch / yaw / roll (radians, small steps)
	_add_pm_row("pitch (look up/dn)",
		_bump_cam_rot.bind(p3d, "x", -0.04, sel),
		_bump_cam_rot.bind(p3d, "x", +0.04, sel))
	_add_pm_row("yaw (look L/R)",
		_bump_cam_rot.bind(p3d, "y", -0.04, sel),
		_bump_cam_rot.bind(p3d, "y", +0.04, sel))
	_add_pm_row("roll (tilt)",
		_bump_cam_rot.bind(p3d, "z", -0.04, sel),
		_bump_cam_rot.bind(p3d, "z", +0.04, sel))

	# 6. Camera position offset (frame composition)
	_add_pm_row("dolly X (L/R frame)",
		_bump_cam_pos.bind(p3d, "x", -0.05, sel),
		_bump_cam_pos.bind(p3d, "x", +0.05, sel))
	_add_pm_row("dolly Y (up/dn frame)",
		_bump_cam_pos.bind(p3d, "y", -0.05, sel),
		_bump_cam_pos.bind(p3d, "y", +0.05, sel))
	_add_pm_row("dolly Z (closer/far)",
		_bump_cam_pos.bind(p3d, "z", +0.05, sel),
		_bump_cam_pos.bind(p3d, "z", -0.05, sel))

	_section_label("SHADER (demon static)")

	# 7. Demon-static strength slider (8-step)
	var cur_strength: float = 0.0
	var mat: ShaderMaterial = p3d.material as ShaderMaterial
	if mat != null:
		cur_strength = float(mat.get_shader_parameter("strength"))
	_add_pm_row("static strength %.2f" % cur_strength,
		_bump_shader.bind(p3d, "strength", -0.125, 0.0, 1.0, sel),
		_bump_shader.bind(p3d, "strength", +0.125, 0.0, 1.0, sel))

	_section_label("COLOUR GRADING")

	# 8. Per-portrait Environment adjustments (brightness/contrast/saturation/glow)
	_add_pm_row("brightness",
		_bump_env.bind(p3d, "brightness", -0.10, sel),
		_bump_env.bind(p3d, "brightness", +0.10, sel))
	_add_pm_row("contrast",
		_bump_env.bind(p3d, "contrast", -0.10, sel),
		_bump_env.bind(p3d, "contrast", +0.10, sel))
	_add_pm_row("saturation",
		_bump_env.bind(p3d, "saturation", -0.10, sel),
		_bump_env.bind(p3d, "saturation", +0.10, sel))
	_add_pm_row("glow",
		_bump_env.bind(p3d, "glow", -0.20, sel),
		_bump_env.bind(p3d, "glow", +0.20, sel))

	_section_label("ACTIONS")

	# 9. Reload GLB
	var reload_btn := Button.new()
	reload_btn.text = "reload GLB"
	reload_btn.focus_mode = Control.FOCUS_NONE
	reload_btn.pressed.connect(_reload_glb.bind(p3d, sel["glb_path"]))
	_controls_box.add_child(reload_btn)

	# 10. Reset all to defaults
	var reset_btn := Button.new()
	reset_btn.text = "reset all to defaults"
	reset_btn.focus_mode = Control.FOCUS_NONE
	reset_btn.pressed.connect(_reset_all.bind(p3d, sel))
	_controls_box.add_child(reset_btn)

	# GLB-path readout
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
	# Write to the LIVE light node, not to _rest_*. The active mood
	# may override key_color / fill_color / etc., so a write to the
	# rest value would be masked the next time set_expression runs.
	# Also update _rest_* so the value persists when mood is later
	# re-applied with no override.
	if not is_instance_valid(p3d):
		return
	var live: Node3D = _live_light_node(p3d, light_key)
	if live == null:
		return
	var cur: float = float(live.light_energy)
	cur = clamp(cur + delta, 0.0, 4.0)
	live.light_energy = cur
	var rest_prop: String = "_rest_%s_energy" % light_key
	if rest_prop in p3d:
		p3d.set(rest_prop, cur)
	_rebuild_controls(sel)


func _shift_temp(p3d: Node, light_key: String, warm_dir: int, sel) -> void:
	# Warm / cool dial — nudges the RGB toward sodium-orange or
	# moonlight-blue while preserving brightness. Writes to the LIVE
	# light node first (visible immediately) and also stamps the
	# rest-state value so subsequent set_expression() calls keep it.
	if not is_instance_valid(p3d):
		return
	var live: Node3D = _live_light_node(p3d, light_key)
	if live == null:
		return
	var c: Color = live.light_color
	var step: float = 0.08
	if warm_dir > 0:
		c.r = clamp(c.r + step, 0.0, 1.0)
		c.b = clamp(c.b - step * 0.7, 0.0, 1.0)
	else:
		c.r = clamp(c.r - step * 0.7, 0.0, 1.0)
		c.b = clamp(c.b + step, 0.0, 1.0)
	live.light_color = c
	var rest_prop: String = "_rest_%s_color" % light_key
	if rest_prop in p3d:
		p3d.set(rest_prop, c)
	_rebuild_controls(sel)


# Portrait3D exposes the lights via @onready _key / _fill / _back.
# Walk to those node properties rather than the rest snapshots.
func _live_light_node(p3d: Node, light_key: String) -> Node3D:
	if not is_instance_valid(p3d):
		return null
	var prop: String = "_%s" % light_key
	if not (prop in p3d):
		return null
	var n = p3d.get(prop)
	return n as Node3D


func _section_label(text: String) -> void:
	var sep := HSeparator.new()
	_controls_box.add_child(sep)
	var lbl := Label.new()
	lbl.text = text
	lbl.add_theme_font_size_override("font_size", 10)
	lbl.add_theme_color_override("font_color", Color(0.92, 0.78, 0.55, 0.85))
	_controls_box.add_child(lbl)


func _add_pm_row(label_text: String, on_minus: Callable, on_plus: Callable) -> void:
	# Reusable "label + − + +" row for any numeric control. Saves
	# ~25 lines of boilerplate per knob.
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 4)
	_controls_box.add_child(row)
	var lbl := Label.new()
	lbl.text = label_text
	lbl.add_theme_font_size_override("font_size", 11)
	lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(lbl)
	var down := Button.new()
	down.text = "−"
	down.focus_mode = Control.FOCUS_NONE
	down.custom_minimum_size.x = 28
	down.pressed.connect(on_minus)
	row.add_child(down)
	var up := Button.new()
	up.text = "+"
	up.focus_mode = Control.FOCUS_NONE
	up.custom_minimum_size.x = 28
	up.pressed.connect(on_plus)
	row.add_child(up)


func _bump_fov(p3d: Node, delta: float, sel) -> void:
	if not is_instance_valid(p3d) or not ("_camera" in p3d):
		return
	var cam = p3d.get("_camera")
	if cam == null or not is_instance_valid(cam):
		return
	var cur: float = float(cam.fov)
	cur = clamp(cur + delta, 8.0, 100.0)
	cam.fov = cur
	if "_rest_cam_fov" in p3d:
		p3d.set("_rest_cam_fov", cur)
	_rebuild_controls(sel)


func _bump_cam_rot(p3d: Node, axis: String, delta: float, sel) -> void:
	if not is_instance_valid(p3d) or not ("_camera" in p3d):
		return
	var cam = p3d.get("_camera")
	if cam == null or not is_instance_valid(cam):
		return
	var r: Vector3 = cam.rotation
	if axis == "x":
		r.x = clamp(r.x + delta, -1.5, 1.5)
	elif axis == "y":
		r.y = clamp(r.y + delta, -1.5, 1.5)
	elif axis == "z":
		r.z = clamp(r.z + delta, -1.5, 1.5)
	cam.rotation = r
	_rebuild_controls(sel)


func _bump_cam_pos(p3d: Node, axis: String, delta: float, sel) -> void:
	if not is_instance_valid(p3d) or not ("_camera" in p3d):
		return
	var cam = p3d.get("_camera")
	if cam == null or not is_instance_valid(cam):
		return
	var pos: Vector3 = cam.position
	if axis == "x":
		pos.x = clamp(pos.x + delta, -3.0, 3.0)
	elif axis == "y":
		pos.y = clamp(pos.y + delta, -3.0, 3.0)
	elif axis == "z":
		pos.z = clamp(pos.z + delta, -10.0, 10.0)
	cam.position = pos
	if "_rest_cam_pos" in p3d:
		p3d.set("_rest_cam_pos", pos)
	_rebuild_controls(sel)


func _bump_shader(p3d: Node, param: String, delta: float, lo: float, hi: float, sel) -> void:
	if not is_instance_valid(p3d):
		return
	var mat: ShaderMaterial = p3d.material as ShaderMaterial
	if mat == null:
		return
	var cur: float = float(mat.get_shader_parameter(param))
	cur = clamp(cur + delta, lo, hi)
	mat.set_shader_parameter(param, cur)
	_rebuild_controls(sel)


# Per-portrait WorldEnvironment adjustments. Looks up the SubViewport's
# WorldEnvironment (if any) and tweaks brightness / contrast / saturation /
# glow_intensity. Creates an Environment if none exists so live grading
# can start from a clean slate.
func _bump_env(p3d: Node, knob: String, delta: float, sel) -> void:
	if not is_instance_valid(p3d):
		return
	var vp = p3d.get_node_or_null("SubViewport")
	if vp == null:
		return
	# Find or create a WorldEnvironment in the SubViewport.
	var we: WorldEnvironment = null
	for child in vp.get_children():
		if child is WorldEnvironment:
			we = child
			break
	if we == null:
		we = WorldEnvironment.new()
		we.environment = Environment.new()
		we.environment.background_mode = Environment.BG_COLOR
		we.environment.background_color = Color(0, 0, 0, 0)
		we.environment.adjustment_enabled = true
		vp.add_child(we)
	var env: Environment = we.environment
	if env == null:
		env = Environment.new()
		we.environment = env
	env.adjustment_enabled = true
	if knob == "brightness":
		env.adjustment_brightness = clamp(env.adjustment_brightness + delta, 0.1, 3.0)
	elif knob == "contrast":
		env.adjustment_contrast = clamp(env.adjustment_contrast + delta, 0.1, 3.0)
	elif knob == "saturation":
		env.adjustment_saturation = clamp(env.adjustment_saturation + delta, 0.0, 3.0)
	elif knob == "glow":
		env.glow_enabled = true
		env.glow_intensity = clamp(env.glow_intensity + delta, 0.0, 4.0)
	_rebuild_controls(sel)


func _reset_all(p3d: Node, sel) -> void:
	# Soft-reset: re-load the GLB (which re-applies character lighting
	# from CHARACTER_LIGHTING) AND clear any per-portrait Environment
	# adjustments + shader strength. Mood resets to neutral.
	if not is_instance_valid(p3d):
		return
	if p3d.has_method("set_demon_mode"):
		p3d.set_demon_mode(false)
	if p3d.has_method("set_expression"):
		p3d.set_expression("neutral")
	var mat: ShaderMaterial = p3d.material as ShaderMaterial
	if mat != null:
		mat.set_shader_parameter("strength", 0.0)
	# Clear the WorldEnvironment we may have spawned for live grading.
	var vp = p3d.get_node_or_null("SubViewport")
	if vp != null:
		for child in vp.get_children():
			if child is WorldEnvironment and child.name == "":
				child.queue_free()
	# Reload the GLB to re-stamp character lighting.
	if sel != null and sel.has("glb_path"):
		_reload_glb(p3d, sel["glb_path"])
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
