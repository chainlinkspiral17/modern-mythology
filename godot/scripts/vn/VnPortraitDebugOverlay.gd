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
		return
	# Locale MoodCycler keybindings — mirror the walkable-locale FPC
	# F-key map so VN scenes (no FPC in tree) still cycle the bg-3D's
	# shader stack. _locale_mood_action no-ops cleanly if the bg-3D
	# isn't loaded (or the loaded locale has no PostProcess).
	if event.keycode == KEY_F3:
		_locale_mood_action("action_cycle_mood", [1])
		get_viewport().set_input_as_handled(); return
	if event.keycode == KEY_F9:
		_locale_mood_action("action_cycle_blend_mode", [])
		get_viewport().set_input_as_handled(); return
	if event.keycode == KEY_F10:
		_locale_mood_action("action_cycle_blend_amount", [])
		get_viewport().set_input_as_handled(); return
	if event.keycode == KEY_F11:
		_locale_mood_action("action_cycle_lighting", [])
		get_viewport().set_input_as_handled(); return
	# F12 alone — cycle style pack. (Shift+F12 is reserved above for
	# the per-portrait reveal toggle.)
	if event.keycode == KEY_F12 and not event.shift_pressed:
		_locale_mood_action("action_cycle_style_pack", [])
		get_viewport().set_input_as_handled(); return
	# Blend % keys — separate digit + tens dial. Brackets nudge the
	# TENS digit (0-90), minus/equal nudge the ONES digit (0-9), and
	# backslash resets to the locale-preset value.
	if event.keycode == KEY_BRACKETLEFT:
		_locale_mood_action("action_blend_pct_tens", []); _locale_mood_action("action_blend_pct_tens", []); _locale_mood_action("action_blend_pct_tens", []); _locale_mood_action("action_blend_pct_tens", []); _locale_mood_action("action_blend_pct_tens", []); _locale_mood_action("action_blend_pct_tens", []); _locale_mood_action("action_blend_pct_tens", []); _locale_mood_action("action_blend_pct_tens", []); _locale_mood_action("action_blend_pct_tens", [])
		# (10 tens calls = -10 since the action wraps 90→0→10→…; cheaper
		# than adding a new "tens minus" action. Net: rotate one step back.)
		get_viewport().set_input_as_handled(); return
	if event.keycode == KEY_BRACKETRIGHT:
		_locale_mood_action("action_blend_pct_tens", [])
		get_viewport().set_input_as_handled(); return
	if event.keycode == KEY_MINUS:
		for _i in range(9):
			_locale_mood_action("action_blend_pct_ones", [])
		get_viewport().set_input_as_handled(); return
	if event.keycode == KEY_EQUAL:
		_locale_mood_action("action_blend_pct_ones", [])
		get_viewport().set_input_as_handled(); return
	if event.keycode == KEY_BACKSLASH:
		_locale_mood_action("action_blend_pct_reset", [])
		get_viewport().set_input_as_handled(); return


# Mirrors FirstPersonController._apply_hud_visibility — walks the
# tree and hides every HUD-flavored CanvasLayer + every "ui"-group
# member. Lives here so VN scenes work without an FPC in the tree.
func _apply_global_hud_visibility(vis: bool) -> void:
	_walk_hide(get_tree().root, vis)
	for n in get_tree().get_nodes_in_group("ui"):
		if "visible" in n:
			n.visible = vis


# Find the bg-3D's loaded locale MoodCycler (PostProcess CanvasLayer
# script). Background3D exposes get_locale_mood_cycler(); we walk
# the tree to find that node. Returns null cleanly when no bg-3D is
# loaded — every keybinding/button no-ops in that case so the panel
# stays useful in scenes that haven't opted into 3D backgrounds.
func _locale_mood_cycler() -> Node:
	var bg3d: Node = _find_node_named(get_tree().root, "Background3D")
	if bg3d == null:
		return null
	if bg3d.has_method("get_locale_mood_cycler"):
		return bg3d.get_locale_mood_cycler()
	return null


func _find_node_named(node: Node, name: String) -> Node:
	if node.name == name:
		return node
	for child in node.get_children():
		var hit := _find_node_named(child, name)
		if hit != null:
			return hit
	return null


func _locale_mood_action(method: String, args: Array) -> void:
	var mc: Node = _locale_mood_cycler()
	if mc == null or not is_instance_valid(mc):
		return
	if mc.has_method(method):
		mc.callv(method, args)
	# Stamp the resulting state so it survives bg-3D reload (scene
	# advance / locale swap and back). The MoodCycler's update-by-
	# reference style means we just sample the current index values
	# after the action runs.
	var preset_id: String = _current_bg3d_preset()
	if preset_id == "":
		return
	var dbg := get_node_or_null("/root/VnDebugState")
	if dbg == null:
		return
	if "mood_index" in mc:
		dbg.stamp_locale_mood(preset_id, int(mc.mood_index))
	if "lighting_index" in mc:
		dbg.stamp_locale_lighting(preset_id, int(mc.lighting_index))
	if "style_pack_index" in mc:
		dbg.stamp_locale_style_pack(preset_id, int(mc.style_pack_index))
	if "blend_mode" in mc:
		dbg.stamp_locale_blend_mode(preset_id, int(mc.blend_mode))
	if "blend_amt_index" in mc:
		dbg.stamp_locale_blend_amt(preset_id, int(mc.blend_amt_index))


func _current_bg3d_preset() -> String:
	var bg3d: Node = _find_node_named(get_tree().root, "Background3D")
	if bg3d == null or not is_instance_valid(bg3d):
		return ""
	if "_loaded_preset" in bg3d:
		return String(bg3d._loaded_preset)
	return ""


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
	# Locale section is ALWAYS available — works regardless of
	# whether any 3D portrait is on screen. Builds first so it's
	# at the top of the controls scroll when no portrait is up.
	if sel == null:
		_build_locale_section()
		return
	var p3d: Node = sel["portrait3d"]
	if p3d == null or not is_instance_valid(p3d):
		_build_locale_section()
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

	_section_label("PORTRAIT SHADER")

	# 7a. Master strength (gates everything below — at 0 the shader
	# is a pure pass-through, so heroes default to clean rendering).
	var cur_strength: float = 0.0
	var mat: ShaderMaterial = p3d.material as ShaderMaterial
	if mat != null:
		cur_strength = float(mat.get_shader_parameter("strength"))
	_add_pm_row("master strength %.2f" % cur_strength,
		_bump_shader.bind(p3d, "strength", -0.125, 0.0, 1.0, sel),
		_bump_shader.bind(p3d, "strength", +0.125, 0.0, 1.0, sel))

	# 7b. Per-effect knobs — each gated by master * its own strength.
	# Default-on demon recipe (1.0) at master=1 reproduces the v1
	# look; set any to 0 to isolate single effects.
	for fx in [
		["aberration_str", "chromatic"],
		["tear_str",       "scanline tear"],
		["noise_str",      "static noise"],
		["dropband_str",   "drop bands"],
		["hue_shift",      "hue rotate"],
		["vignette_str",   "vignette"],
		["invert_str",     "invert"],
		["bloom_str",      "bloom"],
		["film_grain_str", "film grain"],
		["emboss_str",     "emboss"],
		["duotone_str",    "duotone"],
		["ascii_str",      "ascii overlay"],
	]:
		var u: String = fx[0]
		var nm: String = fx[1]
		var cur: float = 0.0
		if mat != null:
			cur = float(mat.get_shader_parameter(u))
		_add_pm_row("%s %.2f" % [nm, cur],
			_bump_shader.bind(p3d, u, -0.125, 0.0, 1.0, sel),
			_bump_shader.bind(p3d, u, +0.125, 0.0, 1.0, sel))

	# 7c. Pixelate + posterize use non-0..1 ranges
	var pix_cur: float = 1.0
	if mat != null:
		pix_cur = float(mat.get_shader_parameter("pixelate_size"))
	_add_pm_row("pixelate %.0f" % pix_cur,
		_bump_shader.bind(p3d, "pixelate_size", -2.0, 1.0, 32.0, sel),
		_bump_shader.bind(p3d, "pixelate_size", +2.0, 1.0, 32.0, sel))
	var post_cur: float = 32.0
	if mat != null:
		post_cur = float(mat.get_shader_parameter("posterize_lvl"))
	_add_pm_row("posterize %.0f" % post_cur,
		_bump_shader.bind(p3d, "posterize_lvl", -2.0, 2.0, 32.0, sel),
		_bump_shader.bind(p3d, "posterize_lvl", +2.0, 2.0, 32.0, sel))

	# 7d. Temp shift is -1..+1 (cool to warm)
	var temp_cur: float = 0.0
	if mat != null:
		temp_cur = float(mat.get_shader_parameter("temp_shift"))
	_add_pm_row("temp shift %+.2f" % temp_cur,
		_bump_shader.bind(p3d, "temp_shift", -0.10, -1.0, 1.0, sel),
		_bump_shader.bind(p3d, "temp_shift", +0.10, -1.0, 1.0, sel))

	# 7e. Shader presets — one-click recipes that set multiple knobs
	var preset_row1 := HBoxContainer.new()
	preset_row1.add_theme_constant_override("separation", 3)
	_controls_box.add_child(preset_row1)
	for preset_name in ["clean", "vhs", "crt", "vapor"]:
		var b1 := Button.new()
		b1.text = preset_name
		b1.focus_mode = Control.FOCUS_NONE
		b1.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var pn: String = preset_name
		b1.pressed.connect(_apply_shader_preset.bind(p3d, pn, sel))
		preset_row1.add_child(b1)
	var preset_row2 := HBoxContainer.new()
	preset_row2.add_theme_constant_override("separation", 3)
	_controls_box.add_child(preset_row2)
	for preset_name in ["noir", "thermal", "comic", "dream"]:
		var b2 := Button.new()
		b2.text = preset_name
		b2.focus_mode = Control.FOCUS_NONE
		b2.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var pn2: String = preset_name
		b2.pressed.connect(_apply_shader_preset.bind(p3d, pn2, sel))
		preset_row2.add_child(b2)

	_section_label("PORTRAIT BACKDROP")
	# Swaps the fuzzy-static backdrop behind THIS portrait for one
	# of several presets. Acts on CharLayer.set_portrait_backdrop.
	var backdrops := ["static", "void", "warm_glow", "cool_blue",
		"crt_scanlines", "gradient_sunset", "neon_grid"]
	for kind in backdrops:
		var b := Button.new()
		b.text = "backdrop: " + kind
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.focus_mode = Control.FOCUS_NONE
		var bk: String = kind
		b.pressed.connect(_set_backdrop.bind(sel["name"], bk, sel))
		_controls_box.add_child(b)

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

	# Always-visible locale (bg-3D) section — same controls the
	# walkable locale's DebugMenu has, plus blend-tens / blend-ones.
	# Mirrored to F-keys (F3/F9/F10/F11/F12 + [ ] - = \) at the
	# _input level so keyboard works whether or not the panel is up.
	_build_locale_section()

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
	# Stamp mood so the choice survives portrait respawn.
	var p_name: String = ""
	for entry in (_char_layer.get_active_portrait3d_list()
		if _char_layer != null and _char_layer.has_method("get_active_portrait3d_list") else []):
		if entry["portrait3d"] == p3d:
			p_name = String(entry["name"]); break
	if p_name != "":
		var dbg := get_node_or_null("/root/VnDebugState")
		if dbg != null and dbg.has_method("stamp_portrait_mood"):
			dbg.stamp_portrait_mood(p_name, MOODS[idx])
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
	_stamp_light(sel, rest_prop, cur)
	_rebuild_controls(sel)


func _stamp_light(sel, prop: String, value) -> void:
	if sel == null:
		return
	var dbg := get_node_or_null("/root/VnDebugState")
	if dbg != null and dbg.has_method("stamp_portrait_light"):
		dbg.stamp_portrait_light(String(sel["name"]), prop, value)


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
	_stamp_light(sel, rest_prop, c)
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


func _build_gauntlet_camera_section() -> void:
	# Find the gauntlet's current FP camera (named "fp_camera"
	# inside the SubViewport). Returns early if not present —
	# this section only shows when the gauntlet is running.
	var fp_cam: Camera3D = _find_node_named_typed(get_tree().root, "fp_camera") as Camera3D
	if fp_cam == null:
		return
	_section_label("GAUNTLET FP CAMERA")
	# Position nudgers (5cm steps)
	for axis in ["x", "y", "z"]:
		var ax: String = axis
		var cur_pos: float = fp_cam.position.x
		if ax == "y": cur_pos = fp_cam.position.y
		elif ax == "z": cur_pos = fp_cam.position.z
		_add_pm_row("pos %s = %+.2f" % [ax.to_upper(), cur_pos],
			_bump_fp_cam_pos.bind(ax, -0.05),
			_bump_fp_cam_pos.bind(ax, +0.05))
	# Rotation nudgers (3° steps, easier to land on canon yaws)
	for axis in ["x", "y", "z"]:
		var ax2: String = axis
		var cur_rot: float = fp_cam.rotation.x
		if ax2 == "y": cur_rot = fp_cam.rotation.y
		elif ax2 == "z": cur_rot = fp_cam.rotation.z
		var label_axis := {"x": "pitch", "y": "yaw", "z": "roll"}[ax2]
		_add_pm_row("%s = %+.1f°" % [label_axis, rad_to_deg(cur_rot)],
			_bump_fp_cam_rot.bind(ax2, deg_to_rad(-3.0)),
			_bump_fp_cam_rot.bind(ax2, deg_to_rad(+3.0)))
	# FOV
	_add_pm_row("FOV = %.0f°" % fp_cam.fov,
		_bump_fp_cam_fov.bind(-2.0),
		_bump_fp_cam_fov.bind(+2.0))
	# Capture-state buttons
	var print_btn := Button.new()
	print_btn.text = "PRINT cam state → console (paste to me)"
	print_btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
	print_btn.focus_mode = Control.FOCUS_NONE
	print_btn.pressed.connect(_print_fp_cam_state)
	_controls_box.add_child(print_btn)
	# Reset to original (re-pull from host's SPACE_MAP)
	var reset_btn := Button.new()
	reset_btn.text = "reset to space default"
	reset_btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
	reset_btn.focus_mode = Control.FOCUS_NONE
	reset_btn.pressed.connect(_reset_fp_cam_to_space_default)
	_controls_box.add_child(reset_btn)


func _bump_fp_cam_pos(axis: String, delta: float) -> void:
	var cam: Camera3D = _find_node_named_typed(get_tree().root, "fp_camera") as Camera3D
	if cam == null:
		return
	if axis == "x":   cam.position.x += delta
	elif axis == "y": cam.position.y += delta
	elif axis == "z": cam.position.z += delta
	_rebuild_picker()


func _bump_fp_cam_rot(axis: String, delta_rad: float) -> void:
	var cam: Camera3D = _find_node_named_typed(get_tree().root, "fp_camera") as Camera3D
	if cam == null:
		return
	if axis == "x":   cam.rotation.x += delta_rad
	elif axis == "y": cam.rotation.y += delta_rad
	elif axis == "z": cam.rotation.z += delta_rad
	_rebuild_picker()


func _bump_fp_cam_fov(delta: float) -> void:
	var cam: Camera3D = _find_node_named_typed(get_tree().root, "fp_camera") as Camera3D
	if cam == null:
		return
	cam.fov = clamp(cam.fov + delta, 8.0, 110.0)
	_rebuild_picker()


func _print_fp_cam_state() -> void:
	# Dump the current camera state in a format easy to paste back
	# into SPACE_MAP / _STANDALONE_SPACE_VANTAGES.
	var cam: Camera3D = _find_node_named_typed(get_tree().root, "fp_camera") as Camera3D
	if cam == null:
		print("[Gauntlet FP] no camera in tree to capture")
		return
	# Figure out which gauntlet space we're at — TarotGauntletGame
	# exposes _player_pos.
	var gauntlet: Node = _find_gauntlet_node()
	var space_id: String = ""
	if gauntlet != null and "_player_pos" in gauntlet:
		space_id = String(gauntlet._player_pos)
	# Reverse-convert Godot → Blender for SPACE_MAP entry. Camera
	# yaw formula was blender_yaw = godot_yaw + 90.
	var godot_pos: Vector3 = cam.position
	var godot_yaw_deg: float = rad_to_deg(cam.rotation.y)
	var blender_x: float = godot_pos.x
	var blender_y: float = -godot_pos.z
	var blender_yaw_deg: float = godot_yaw_deg + 90.0
	# Normalise yaw to [0, 360)
	while blender_yaw_deg < 0.0:    blender_yaw_deg += 360.0
	while blender_yaw_deg >= 360.0: blender_yaw_deg -= 360.0
	print("")
	print("════════ GAUNTLET CAM STATE CAPTURE ════════")
	print("Space: '%s'" % space_id)
	print("Godot:   pos=%s   rot=%s   fov=%.1f" %
		[cam.position, cam.rotation, cam.fov])
	print("Blender (for SPACE_MAP): [%.2f, %.2f, %.1f]" %
		[blender_x, blender_y, blender_yaw_deg])
	print("Suggested SPACE_MAP line:")
	print('    "%s": [%+.2f, %+.2f, %.1f],' %
		[space_id, blender_x, blender_y, blender_yaw_deg])
	print("════════════════════════════════════════════")


func _reset_fp_cam_to_space_default() -> void:
	# Re-trigger a board re-draw which will rebuild the SubViewport
	# from scratch (pulling from SPACE_MAP). Easiest way to undo
	# live camera tweaks per space.
	var gauntlet: Node = _find_gauntlet_node()
	if gauntlet != null and gauntlet.has_method("_render"):
		gauntlet._render()


func _find_gauntlet_node() -> Node:
	# Walk for the gauntlet — distinguished by having _player_pos
	# property AND _board_content. Caching unnecessary since this
	# only fires on debug actions.
	return _walk_for_gauntlet(get_tree().root)


func _walk_for_gauntlet(node: Node) -> Node:
	if "_player_pos" in node and "_board_content" in node:
		return node
	for child in node.get_children():
		var hit := _walk_for_gauntlet(child)
		if hit != null:
			return hit
	return null


func _find_node_named_typed(root: Node, name: String) -> Node:
	if root.name == name:
		return root
	for child in root.get_children():
		var hit := _find_node_named_typed(child, name)
		if hit != null:
			return hit
	return null


func _build_locale_section() -> void:
	_build_gauntlet_camera_section()    # no-op outside gauntlet context
	_section_label("LOCALE BG-3D (F3/F9-F12 + [ ] - = \\)")
	_add_locale_btn("F3  · cycle mood →",        "action_cycle_mood", [1])
	_add_locale_btn("(prev) ← cycle mood",       "action_cycle_mood", [-1])
	_add_locale_btn("F9  · cycle blend mode",    "action_cycle_blend_mode", [])
	_add_locale_btn("F10 · cycle blend amount",  "action_cycle_blend_amount", [])
	_add_locale_btn("]   · blend % +10 (tens)",  "action_blend_pct_tens", [])
	_add_locale_btn("=   · blend % +1 (ones)",   "action_blend_pct_ones", [])
	_add_locale_btn("\\   · blend % reset",      "action_blend_pct_reset", [])
	_add_locale_btn("F11 · cycle lighting",      "action_cycle_lighting", [])
	_add_locale_btn("F12 · cycle style pack",    "action_cycle_style_pack", [])
	_add_locale_btn("F5  · shimmer strobe",      "action_strobe_shimmer", [])
	_add_locale_btn("F6  · rift strobe",         "action_strobe_rift", [])

	_section_label("PERSISTENCE (vol 5-7 wide)")
	var summary := Button.new()
	summary.text = "print state summary → console"
	summary.alignment = HORIZONTAL_ALIGNMENT_LEFT
	summary.focus_mode = Control.FOCUS_NONE
	summary.pressed.connect(func() -> void:
		var dbg := get_node_or_null("/root/VnDebugState")
		if dbg != null and dbg.has_method("print_state_summary"):
			dbg.print_state_summary()
	)
	_controls_box.add_child(summary)
	var wipe := Button.new()
	wipe.text = "wipe ALL overrides (chapters + portraits)"
	wipe.alignment = HORIZONTAL_ALIGNMENT_LEFT
	wipe.focus_mode = Control.FOCUS_NONE
	wipe.pressed.connect(func() -> void:
		var dbg := get_node_or_null("/root/VnDebugState")
		if dbg != null and dbg.has_method("clear_all"):
			dbg.clear_all()
		_rebuild_picker()
	)
	_controls_box.add_child(wipe)


func _add_locale_btn(label: String, method: String, args: Array) -> void:
	var b := Button.new()
	b.text = label
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	b.focus_mode = Control.FOCUS_NONE
	b.pressed.connect(_locale_mood_action.bind(method, args))
	_controls_box.add_child(b)


# Shader-recipe presets — one-click "looks" that set several
# uniforms at once. All other uniforms are zeroed so previewing
# a preset starts from a clean slate. The user can then tweak
# the individual rows for fine-grain.
const _PRESETS := {
	"clean": {
		"strength": 0.0,
	},
	"vhs": {  # VHS tape — chromatic + tear + drop bands, no bloom
		"strength": 1.0,
		"aberration_str": 0.9, "tear_str": 0.7, "noise_str": 0.5,
		"dropband_str": 0.5, "vignette_str": 0.30,
	},
	"crt": {  # CRT monitor — scanlines + slight chromatic + vignette
		"strength": 1.0,
		"aberration_str": 0.4, "tear_str": 0.0, "noise_str": 0.18,
		"dropband_str": 0.0, "vignette_str": 0.60, "bloom_str": 0.30,
	},
	"vapor": {  # Vaporwave — hue + duotone + pixelate
		"strength": 1.0,
		"hue_shift": 0.20, "duotone_str": 0.6,
		"duotone_a": Color(0.32, 0.18, 0.62, 1.0),
		"duotone_b": Color(0.96, 0.52, 0.84, 1.0),
		"pixelate_size": 4.0, "bloom_str": 0.40,
	},
	"noir": {  # Film noir — desat + high contrast + grain + vignette
		"strength": 1.0,
		"duotone_str": 0.85,
		"duotone_a": Color(0.04, 0.04, 0.06, 1.0),
		"duotone_b": Color(0.94, 0.92, 0.88, 1.0),
		"film_grain_str": 0.30, "vignette_str": 0.65,
	},
	"thermal": {  # Heat-map look — duotone red→yellow
		"strength": 1.0,
		"duotone_str": 0.95,
		"duotone_a": Color(0.10, 0.04, 0.18, 1.0),
		"duotone_b": Color(0.98, 0.74, 0.18, 1.0),
		"posterize_lvl": 8.0,
	},
	"comic": {  # Comic-book — heavy emboss + posterize
		"strength": 1.0,
		"emboss_str": 0.65, "posterize_lvl": 4.0, "vignette_str": 0.40,
	},
	"dream": {  # Soft ethereal — bloom + cool temp + slight invert
		"strength": 1.0,
		"bloom_str": 0.70, "temp_shift": -0.30,
		"vignette_str": 0.35, "film_grain_str": 0.10,
	},
}

# Every numeric uniform we need to clear when switching presets so a
# leftover value from a previous preset doesn't leak.
const _SHADER_UNIFORMS_NUMERIC := [
	"aberration_str", "tear_str", "noise_str", "dropband_str",
	"hue_shift", "vignette_str", "invert_str", "bloom_str",
	"temp_shift", "film_grain_str", "emboss_str", "duotone_str",
	"ascii_str",
]


func _apply_shader_preset(p3d: Node, preset_name: String, sel) -> void:
	if not is_instance_valid(p3d):
		return
	var mat: ShaderMaterial = p3d.material as ShaderMaterial
	if mat == null:
		return
	# Reset the per-effect knobs first
	for u in _SHADER_UNIFORMS_NUMERIC:
		mat.set_shader_parameter(u, 0.0)
	mat.set_shader_parameter("pixelate_size", 1.0)
	mat.set_shader_parameter("posterize_lvl", 32.0)
	# Apply preset overrides
	var recipe: Dictionary = _PRESETS.get(preset_name, {})
	for k in recipe:
		mat.set_shader_parameter(k, recipe[k])
	print("[VnPortraitDebug] shader preset %s applied" % preset_name)
	_rebuild_controls(sel)


func _set_backdrop(char_key: String, kind: String, sel) -> void:
	if _char_layer == null or not is_instance_valid(_char_layer):
		return
	if _char_layer.has_method("set_portrait_backdrop"):
		_char_layer.set_portrait_backdrop(char_key, kind)
	# Persist so the kind survives portrait respawn.
	var dbg := get_node_or_null("/root/VnDebugState")
	if dbg != null and dbg.has_method("stamp_portrait_backdrop"):
		dbg.stamp_portrait_backdrop(char_key, kind)
	_rebuild_controls(sel)


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
	# Stamp into VnDebugState so the value survives a portrait
	# respawn (next dialog beat re-instantiating this character).
	if sel != null:
		_stamp_shader(sel, param, cur)
	_rebuild_controls(sel)


func _stamp_shader(sel, uniform: String, value) -> void:
	if sel == null:
		return
	var dbg := get_node_or_null("/root/VnDebugState")
	if dbg != null and dbg.has_method("stamp_portrait_shader"):
		dbg.stamp_portrait_shader(String(sel["name"]), uniform, value)


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
	# Stamp at the END (after we know the final value) — see below.
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
	# Stamp into VnDebugState so the value survives respawn.
	if sel != null:
		var dbg := get_node_or_null("/root/VnDebugState")
		if dbg != null and dbg.has_method("stamp_portrait_env"):
			var final_v: float = 0.0
			match knob:
				"brightness": final_v = env.adjustment_brightness
				"contrast":   final_v = env.adjustment_contrast
				"saturation": final_v = env.adjustment_saturation
				"glow":       final_v = env.glow_intensity
			dbg.stamp_portrait_env(String(sel["name"]), knob, final_v)
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
