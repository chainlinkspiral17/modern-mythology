extends Control
## AsciiSubstrateRaster — high-resolution ASCII grid renderer.
##
## Renders the grid once into an internal SubViewport, then displays the
## resulting texture via a stretched TextureRect. This bypasses the live
## BBCode RichTextLabel cost cap (~50k cells) and lets us author huge
## composites that scale/pan/letterbox cleanly to any container.
##
## Use this for gallery items, cinema set-pieces, and zoom-out reveals.
## For in-engine substrates that change with scene flow, use the live
## AsciiSubstrate instead.

const SUBSTRATE_ROOT := "res://resources/substrates/"
const MONO_FONT_PATH := "res://resources/fonts/SpaceMono-Regular.ttf"

@export var font_pixel_size: int = 12

var _bg: ColorRect = null
var _subviewport: SubViewport = null
var _label: RichTextLabel = null
var _texture_rect: TextureRect = null
var _current_path: String = ""

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)

	_bg = ColorRect.new()
	_bg.color = Color(0.020, 0.030, 0.063, 1.0)
	_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_bg)

	# SubViewport hosts the actual BBCode render. Oversized initially;
	# we shrink to fit after the label has a measured size.
	_subviewport = SubViewport.new()
	_subviewport.transparent_bg = true
	_subviewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
	_subviewport.size = Vector2i(64, 64)
	_subviewport.disable_3d = true
	_subviewport.handle_input_locally = false
	add_child(_subviewport)

	_label = RichTextLabel.new()
	_label.bbcode_enabled = true
	_label.fit_content = true
	_label.scroll_active = false
	_label.autowrap_mode = TextServer.AUTOWRAP_OFF
	if ResourceLoader.exists(MONO_FONT_PATH):
		var ff: FontFile = load(MONO_FONT_PATH)
		_label.add_theme_font_override("normal_font",  ff)
		_label.add_theme_font_override("mono_font",    ff)
		_label.add_theme_font_override("bold_font",    ff)
		_label.add_theme_font_override("italics_font", ff)
	_label.add_theme_font_size_override("normal_font_size", font_pixel_size)
	_label.add_theme_font_size_override("mono_font_size",   font_pixel_size)
	_label.add_theme_constant_override("line_separation", 0)
	_subviewport.add_child(_label)

	# TextureRect displays the SubViewport's texture, fit to this Control
	_texture_rect = TextureRect.new()
	_texture_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_texture_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_texture_rect.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
	_texture_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_texture_rect.texture = _subviewport.get_texture()
	add_child(_texture_rect)


# ── Public API ────────────────────────────────────────────────────────────────

func load_substrate(short_path: String) -> void:
	if short_path == "":
		clear_substrate()
		return
	# Prefer the pre-rasterized PNG if one exists. The BBCode path
	# below stalls the main thread on any substrate over ~5k cells
	# (measured 13s for 24k cells on Godot 4.3 headless), so we
	# pre-bake each substrate to a tiny PNG via
	# tools/rasterize_substrates.py and load that instead.
	var png_path: String = SUBSTRATE_ROOT + short_path + ".png"
	if FileAccess.file_exists(png_path):
		var tex: Texture2D = _load_texture(png_path)
		if tex != null:
			_current_path = short_path
			_texture_rect.texture = tex
			# Hide the SubViewport path's texture binding
			_label.text = ""
			return
	var full_path: String = SUBSTRATE_ROOT + short_path + ".json"
	if not FileAccess.file_exists(full_path):
		push_warning("AsciiSubstrateRaster: not found: " + full_path)
		clear_substrate()
		return
	var f := FileAccess.open(full_path, FileAccess.READ)
	if f == null:
		return
	var data: Variant = JSON.parse_string(f.get_as_text())
	if typeof(data) != TYPE_DICTIONARY or not data.has("cells"):
		push_warning("AsciiSubstrateRaster: invalid grid: " + full_path)
		return
	_current_path = short_path
	# Rebind SubViewport-as-texture in case the PNG fast path swapped
	# us out of it previously
	_texture_rect.texture = _subviewport.get_texture()
	_build_bbcode(data)
	# Render in two frames: one for label layout, one for SubViewport pixel readback.
	call_deferred("_finalize_render")


func _load_texture(res_path: String) -> Texture2D:
	if ResourceLoader.exists(res_path):
		var t := ResourceLoader.load(res_path) as Texture2D
		if t != null:
			return t
	# Raw fallback for un-imported PNGs (mosaics ship without .import sidecar)
	var abs_path: String = ProjectSettings.globalize_path(res_path)
	if FileAccess.file_exists(abs_path):
		var img := Image.load_from_file(abs_path)
		if img != null:
			return ImageTexture.create_from_image(img)
	return null


func clear_substrate() -> void:
	_current_path = ""
	_label.text = ""


func current_substrate() -> String:
	return _current_path


# ── Rendering ────────────────────────────────────────────────────────────────

func _build_bbcode(data: Dictionary) -> void:
	var parts := PackedStringArray()
	for row in data.cells:
		for cell in row:
			var c: String = cell.get("c", " ")
			if c == "[":
				c = "[lb]"
			var fg = cell.get("fg")
			var bg = cell.get("bg")
			var open_tags := ""
			var close_tags := ""
			if bg != null:
				open_tags  += "[bgcolor=" + str(bg) + "]"
				close_tags  = "[/bgcolor]" + close_tags
			if fg != null:
				open_tags  += "[color=" + str(fg) + "]"
				close_tags  = "[/color]" + close_tags
			parts.append(open_tags + c + close_tags)
		parts.append("\n")
	_label.text = "".join(parts)


func _finalize_render() -> void:
	await get_tree().process_frame
	# Now the label has a measured size; resize SubViewport to match
	var sz := _label.size
	var w := int(ceil(maxf(sz.x, 32.0)))
	var h := int(ceil(maxf(sz.y, 32.0)))
	_subviewport.size = Vector2i(w, h)
	# Trigger one render
	_subviewport.render_target_update_mode = SubViewport.UPDATE_ONCE
	await get_tree().process_frame
	_subviewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
