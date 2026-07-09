extends Control
## Fey Faire · run controller · scaffold pass.
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
## Persists run state to `user://fey_faire.save.json` when the
## eventual chapter authoring lands.  For the scaffold, no save
## happens because there's no state.
##
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal finished(canon_vars: Dictionary, lore_tokens: Array)

const MANIFEST_PATH := "res://resources/games/vol7/fey_faire/manifest.json"
const SAVE_PATH     := "user://fey_faire.save.json"

# Rocha's title-card palette · cream + old rose + mauve + gold
const C_BG        := Color(0.157, 0.094, 0.173, 1.0)   # black-plum #28182c
const C_CREAM     := Color(0.957, 0.878, 0.816, 1.0)   # #f4e0d0
const C_ROSE      := Color(0.878, 0.722, 0.753, 1.0)   # #e0b8c0
const C_MAUVE     := Color(0.784, 0.557, 0.643, 1.0)   # #c88ea4
const C_DEEP      := Color(0.455, 0.157, 0.282, 1.0)   # #743c60 · dark plum
const C_GOLD      := Color(0.973, 0.784, 0.282, 1.0)   # #f8c848
const C_GOLD_DIM  := Color(0.541, 0.361, 0.157, 1.0)   # #8a5c30

var _manifest: Dictionary = {}


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	_load_manifest()
	_build_title_screen()


func _load_manifest() -> void:
	if not FileAccess.file_exists(MANIFEST_PATH):
		push_warning("[FeyFaireHost] missing manifest %s" % MANIFEST_PATH)
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

	# Cream + old rose horizontal bands · match the cart title card
	var band_cream := ColorRect.new()
	band_cream.color = C_CREAM
	band_cream.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	band_cream.offset_top = 0
	band_cream.offset_bottom = 200
	add_child(band_cream)

	var band_rose := ColorRect.new()
	band_rose.color = C_ROSE
	band_rose.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	band_rose.offset_top = 200
	band_rose.offset_bottom = 380
	add_child(band_rose)

	# Mauve tent-stripe hint · vertical bands · specific spacing
	for x in range(80, 1200, 100):
		var stripe := ColorRect.new()
		stripe.color = C_MAUVE
		stripe.set_anchors_preset(Control.PRESET_TOP_LEFT)
		stripe.position = Vector2(x, 60)
		stripe.size = Vector2(8, 320)
		add_child(stripe)

	# Center-panel dark plum
	var center_panel := ColorRect.new()
	center_panel.color = C_DEEP
	center_panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	center_panel.offset_left = -320
	center_panel.offset_right = 320
	center_panel.offset_top = -80
	center_panel.offset_bottom = 260
	add_child(center_panel)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -300
	v.offset_right = 300
	v.offset_top = -60
	v.offset_bottom = 240
	v.add_theme_constant_override("separation", 14)
	add_child(v)

	var shelf: Dictionary = _manifest.get("shelf", {})

	var title := Label.new()
	title.text = String(shelf.get("label_title", "FEY FAIRE"))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 28)
	title.add_theme_color_override("font_color", C_GOLD)
	v.add_child(title)

	var subtitle := Label.new()
	subtitle.text = String(shelf.get("label_subtitle", ""))
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.add_theme_font_size_override("font_size", 12)
	subtitle.add_theme_color_override("font_color", C_CREAM)
	v.add_child(subtitle)

	var meta := Label.new()
	meta.text = "%s · %s · %s" % [
		String(shelf.get("publisher", "")),
		String(shelf.get("publisher_locale", "")),
		int(shelf.get("release_year", 0))
	]
	meta.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	meta.add_theme_font_size_override("font_size", 10)
	meta.add_theme_color_override("font_color", C_ROSE)
	v.add_child(meta)

	var sep := Control.new()
	sep.custom_minimum_size = Vector2(0, 16)
	v.add_child(sep)

	var blurb := RichTextLabel.new()
	blurb.bbcode_enabled = false
	blurb.fit_content = true
	blurb.custom_minimum_size = Vector2(560, 80)
	blurb.text = String(shelf.get("cover_blurb", ""))
	blurb.add_theme_font_size_override("normal_font_size", 10)
	blurb.add_theme_color_override("default_color", C_CREAM)
	v.add_child(blurb)

	var sep2 := Control.new()
	sep2.custom_minimum_size = Vector2(0, 12)
	v.add_child(sep2)

	var status_label := Label.new()
	status_label.text = "· content authored · playable acts pending ·"
	status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	status_label.add_theme_font_size_override("font_size", 10)
	status_label.add_theme_color_override("font_color", C_GOLD_DIM)
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
