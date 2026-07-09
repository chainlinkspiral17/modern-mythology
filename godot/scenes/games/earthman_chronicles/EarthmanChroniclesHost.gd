extends Control
## The Earthman Chronicles · run controller · scaffold pass.
##
## Boots to a title card that reads the manifest and renders the
## cart's title + subtitle + shelf metadata.  ENTER starts a
## (deferred) new run · currently just displays a "content
## authored · playable acts pending" acknowledgment screen.
## BACK returns to the shelf.
##
## Follows Pirate Summer / Estuary 3 host pattern:
##   - signal quit_to_shelf · caller (SlowstockBoot) reopens shelf
##   - signal finished(canon_vars, lore_tokens) · caller merges
##     into GauntletState + reopens shelf
##
## Persists run state to `user://earthman_chronicles.save.json`
## when the eventual chapter authoring lands.  For the scaffold,
## no save happens because there's no state.
##
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal finished(canon_vars: Dictionary, lore_tokens: Array)

const MANIFEST_PATH := "res://resources/games/vol7/earthman_chronicles/manifest.json"
const SAVE_PATH     := "user://earthman_chronicles.save.json"

# Astro-Cortex Amiga/DOS palette · deep purple + amber + arcade green
const C_BG           := Color(0.094, 0.094, 0.157, 1.0)   # #181828 deep purple
const C_CORTEX       := Color(0.345, 0.188, 0.376, 1.0)   # #583060 Cortex-purple
const C_AMBER        := Color(0.784, 0.376, 0.125, 1.0)   # #c86020 Amiga amber
const C_GREEN        := Color(0.0, 0.753, 0.376, 1.0)     # #00c060 arcade green (correction terminal)
const C_RED          := Color(0.753, 0.125, 0.125, 1.0)   # #c02020 warning red (220-Hz moments)
const C_CREAM        := Color(0.912, 0.816, 0.565, 1.0)   # #e8d090 warm terminal cream
const C_WHITE        := Color(0.941, 0.941, 0.941, 1.0)   # #f0f0f0
const C_GRAY         := Color(0.282, 0.282, 0.314, 1.0)   # #484850 Krexal industrial gray

var _manifest: Dictionary = {}


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	_load_manifest()
	_build_title_screen()


func _load_manifest() -> void:
	if not FileAccess.file_exists(MANIFEST_PATH):
		push_warning("[EarthmanChroniclesHost] missing manifest %s" % MANIFEST_PATH)
		return
	var f := FileAccess.open(MANIFEST_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		_manifest = parsed


# start_new_run signature matches Estuary3Host / PirateSummerHost so
# SlowstockBoot can call it uniformly.  For the scaffold pass this
# just re-mounts the title (there is no run to start yet).
func start_new_run(_manager_mode: bool = false) -> void:
	pass


func _build_title_screen() -> void:
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# CRT scanline hint · simulate horizontal bands
	for y in range(0, 720, 2):
		var scanline := ColorRect.new()
		scanline.color = Color(0.0, 0.0, 0.0, 0.15)
		scanline.set_anchors_preset(Control.PRESET_TOP_WIDE)
		scanline.position.y = y
		scanline.size = Vector2(2000, 1)
		add_child(scanline)

	# Top HUD band · Astro-Cortex terminal-style
	var hud_top := ColorRect.new()
	hud_top.color = C_GRAY
	hud_top.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	hud_top.offset_top = 0
	hud_top.offset_bottom = 24
	add_child(hud_top)

	var hud_top_text := Label.new()
	hud_top_text.text = "ASTRO-CORTEX SOFTWARE · CULVER CITY CA · REV 2"
	hud_top_text.set_anchors_preset(Control.PRESET_TOP_LEFT)
	hud_top_text.position = Vector2(12, 6)
	hud_top_text.add_theme_font_size_override("font_size", 10)
	hud_top_text.add_theme_color_override("font_color", C_AMBER)
	add_child(hud_top_text)

	var hud_top_right := Label.new()
	hud_top_right.text = "MARCH 1985"
	hud_top_right.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	hud_top_right.position = Vector2(-140, 6)
	hud_top_right.add_theme_font_size_override("font_size", 10)
	hud_top_right.add_theme_color_override("font_color", C_AMBER)
	add_child(hud_top_right)

	# Center title panel
	var center_panel := ColorRect.new()
	center_panel.color = C_CORTEX
	center_panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	center_panel.offset_left = -340
	center_panel.offset_right = 340
	center_panel.offset_top = -100
	center_panel.offset_bottom = 260
	add_child(center_panel)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -320
	v.offset_right = 320
	v.offset_top = -80
	v.offset_bottom = 240
	v.add_theme_constant_override("separation", 14)
	add_child(v)

	var shelf: Dictionary = _manifest.get("shelf", {})

	var title := Label.new()
	title.text = String(shelf.get("label_title", "THE EARTHMAN CHRONICLES"))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 26)
	title.add_theme_color_override("font_color", C_AMBER)
	v.add_child(title)

	var subtitle := Label.new()
	subtitle.text = String(shelf.get("label_subtitle", ""))
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.add_theme_font_size_override("font_size", 12)
	subtitle.add_theme_color_override("font_color", C_CREAM)
	v.add_child(subtitle)

	var meta := Label.new()
	meta.text = "%s · %s · %d" % [
		String(shelf.get("publisher", "")),
		String(shelf.get("publisher_locale", "")),
		int(shelf.get("release_year", 0))
	]
	meta.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	meta.add_theme_font_size_override("font_size", 10)
	meta.add_theme_color_override("font_color", C_WHITE)
	v.add_child(meta)

	var sep := Control.new()
	sep.custom_minimum_size = Vector2(0, 16)
	v.add_child(sep)

	var blurb := RichTextLabel.new()
	blurb.bbcode_enabled = false
	blurb.fit_content = true
	blurb.custom_minimum_size = Vector2(600, 100)
	blurb.text = String(shelf.get("cover_blurb", ""))
	blurb.add_theme_font_size_override("normal_font_size", 10)
	blurb.add_theme_color_override("default_color", C_WHITE)
	v.add_child(blurb)

	var sep2 := Control.new()
	sep2.custom_minimum_size = Vector2(0, 12)
	v.add_child(sep2)

	# A specific 220-Hz reference · warning red · a tell
	var hidden_status := Label.new()
	hidden_status.text = "· A LOST WORK · ADAPTED · MARCH 1985 ·"
	hidden_status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hidden_status.add_theme_font_size_override("font_size", 10)
	hidden_status.add_theme_color_override("font_color", C_RED)
	v.add_child(hidden_status)

	var status_label := Label.new()
	status_label.text = "· content authored · playable acts pending ·"
	status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	status_label.add_theme_font_size_override("font_size", 10)
	status_label.add_theme_color_override("font_color", C_GREEN)
	v.add_child(status_label)

	var buttons := HBoxContainer.new()
	buttons.alignment = BoxContainer.ALIGNMENT_CENTER
	buttons.add_theme_constant_override("separation", 16)
	v.add_child(buttons)

	var back_btn := Button.new()
	back_btn.text = "  ← back to shelf  "
	back_btn.pressed.connect(_on_back_pressed)
	buttons.add_child(back_btn)


func _on_back_pressed() -> void:
	quit_to_shelf.emit()


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			_on_back_pressed()
			get_viewport().set_input_as_handled()
