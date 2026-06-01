extends Control
## AsciiSubstrate — full-viewport ASCII grid that sits at the bottom of the
## GameEngine layer stack. Acts as the "machine substrate" beneath whatever
## richer media (bg textures, character portraits, video) layers above.
##
## Public API:
##   load_substrate("vol5/diner_predawn")   load grid by short path
##   clear_substrate()                      empty the grid
##
## Grid JSONs live at res://resources/substrates/<short_path>.json and use
## the same {width, height, cells:[[{c,fg,bg}]]} schema as tools/img2ascii.py.

const SUBSTRATE_ROOT := "res://resources/substrates/"
const MONO_FONT_PATH := "res://resources/fonts/SpaceMono-Regular.ttf"

@export var font_pixel_size: int = 14
@export var idle_modulate: Color = Color(0.85, 0.85, 0.9, 1.0)

var _bg:    ColorRect     = null
var _label: RichTextLabel = null
var _current_path: String = ""

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)

	_bg = ColorRect.new()
	_bg.color = Color(0.027, 0.035, 0.071, 1.0)
	_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_bg)

	_label = RichTextLabel.new()
	_label.bbcode_enabled = true
	_label.fit_content = true
	_label.scroll_active = false
	_label.autowrap_mode = TextServer.AUTOWRAP_OFF
	_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_label.set_anchors_preset(Control.PRESET_CENTER)
	_label.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_label.grow_vertical   = Control.GROW_DIRECTION_BOTH
	_label.modulate = idle_modulate

	if ResourceLoader.exists(MONO_FONT_PATH):
		var ff: FontFile = load(MONO_FONT_PATH)
		_label.add_theme_font_override("normal_font", ff)
		_label.add_theme_font_override("mono_font",   ff)
		_label.add_theme_font_override("bold_font",   ff)
		_label.add_theme_font_override("italics_font", ff)
	_label.add_theme_font_size_override("normal_font_size", font_pixel_size)
	_label.add_theme_font_size_override("mono_font_size",   font_pixel_size)
	_label.add_theme_constant_override("line_separation", 0)
	add_child(_label)


# ── Public API ────────────────────────────────────────────────────────────────

func load_substrate(short_path: String) -> void:
	if short_path == "":
		clear_substrate()
		return
	# PNG fast path — see AsciiSubstrateRaster.load_substrate.
	# RichTextLabel BBCode parsing stalls the main thread on any
	# substrate over ~5k cells; pre-rasterized PNGs load in ms.
	var png_path: String = SUBSTRATE_ROOT + short_path + ".png"
	if FileAccess.file_exists(png_path):
		var tex: Texture2D = _load_texture(png_path)
		if tex != null:
			_current_path = short_path
			_swap_to_texture(tex)
			return
	var full_path: String = SUBSTRATE_ROOT + short_path + ".json"
	if not FileAccess.file_exists(full_path):
		push_warning("AsciiSubstrate: not found: " + full_path)
		clear_substrate()
		return
	var f := FileAccess.open(full_path, FileAccess.READ)
	if f == null:
		push_warning("AsciiSubstrate: could not open: " + full_path)
		return
	var data: Variant = JSON.parse_string(f.get_as_text())
	if typeof(data) != TYPE_DICTIONARY or not data.has("cells"):
		push_warning("AsciiSubstrate: invalid grid: " + full_path)
		return
	_current_path = short_path
	_swap_to_label()
	_render(data)


func _load_texture(res_path: String) -> Texture2D:
	if ResourceLoader.exists(res_path):
		var t := ResourceLoader.load(res_path) as Texture2D
		if t != null:
			return t
	var abs_path: String = ProjectSettings.globalize_path(res_path)
	if FileAccess.file_exists(abs_path):
		var img := Image.load_from_file(abs_path)
		if img != null:
			return ImageTexture.create_from_image(img)
	return null


var _png_rect: TextureRect = null

func _swap_to_texture(tex: Texture2D) -> void:
	if _label != null:
		_label.text = ""
		_label.visible = false
	if _png_rect == null:
		_png_rect = TextureRect.new()
		_png_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		_png_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		_png_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		_png_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(_png_rect)
	_png_rect.texture = tex
	_png_rect.visible = true


func _swap_to_label() -> void:
	if _png_rect != null:
		_png_rect.visible = false
		_png_rect.texture = null
	if _label != null:
		_label.visible = true


func clear_substrate() -> void:
	_current_path = ""
	if _label != null:
		_label.text = ""
	if _png_rect != null:
		_png_rect.visible = false
		_png_rect.texture = null


func current_substrate() -> String:
	return _current_path


# ── Render ────────────────────────────────────────────────────────────────────

func _render(data: Dictionary) -> void:
	# BBCode string assembly — much faster than push_color/pop per cell for
	# a few thousand cells.
	var parts := PackedStringArray()
	for row in data.cells:
		for cell in row:
			var c: String = cell.get("c", " ")
			# Escape any literal '[' so BBCode doesn't choke.
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
