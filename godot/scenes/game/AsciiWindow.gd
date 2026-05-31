extends Control
## AsciiWindow — one piece of an AsciiComposition.
##
## Renders ASCII grid JSON(s) into SubViewport(s) and displays via a
## TextureRect. In frame mode each frame is pre-rendered to its own
## SubViewport, so cycling only swaps which texture the TextureRect
## displays — no BBCode re-parsing on swap.
##
## Optional:
##   shadow_color/shadow_offset — duplicate of the content rendered behind
##   the main texture at an offset.
##   frames + frame_duration — cycle pre-rendered frames.

const PIECE_ROOT     := "res://resources/substrates/"
const MONO_FONT_PATH := "res://resources/fonts/SpaceMono-Regular.ttf"

@export var font_pixel_size: int = 12

@export var shadow_color: Color = Color(0, 0, 0, 0)
@export var shadow_offset: Vector2 = Vector2(3, 3)

@export var frames: PackedStringArray = PackedStringArray()
@export var frame_duration: float = 0.6
@export var autoplay: bool = true
@export var loop: bool = true

# Per-frame rendering targets. Single-piece mode uses a single-entry array.
var _subviewports: Array[SubViewport] = []
var _labels: Array[RichTextLabel] = []
var _font_ref: FontFile = null

var _texture_rect: TextureRect = null
var _shadow_rect: TextureRect = null
var _loaded_path: String = ""

var _frame_idx: int = 0
var _frame_timer: float = 0.0
var _playing: bool = false


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	if ResourceLoader.exists(MONO_FONT_PATH):
		_font_ref = load(MONO_FONT_PATH)

	# Build display rects up front; texture pointer is bound when frames load.
	if shadow_color.a > 0.0:
		_shadow_rect = TextureRect.new()
		_shadow_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		_shadow_rect.offset_left   = shadow_offset.x
		_shadow_rect.offset_top    = shadow_offset.y
		_shadow_rect.offset_right  = shadow_offset.x
		_shadow_rect.offset_bottom = shadow_offset.y
		_shadow_rect.stretch_mode  = TextureRect.STRETCH_SCALE
		_shadow_rect.modulate      = shadow_color
		_shadow_rect.mouse_filter  = Control.MOUSE_FILTER_IGNORE
		add_child(_shadow_rect)

	_texture_rect = TextureRect.new()
	_texture_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_texture_rect.stretch_mode = TextureRect.STRETCH_SCALE
	_texture_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_texture_rect)

	if not frames.is_empty():
		_load_frames_internal()


# ── Single-piece loader ───────────────────────────────────────────────────────

func load_piece(short_path: String) -> void:
	if short_path == "":
		return
	# PNG fast path — see AsciiSubstrateRaster.load_substrate for
	# rationale. If a pre-rasterized PNG exists alongside the JSON,
	# load it directly into a TextureRect instead of building BBCode.
	var png_path := "res://resources/substrates/" + short_path + ".png"
	if FileAccess.file_exists(png_path):
		var tex := _load_texture(png_path)
		if tex != null:
			_loaded_path = short_path
			_clear_viewports()
			_make_image_window(tex)
			return
	var data := _read_piece_json(short_path)
	if data.is_empty():
		return
	_loaded_path = short_path
	_clear_viewports()
	_make_viewport_for_data(data)
	call_deferred("_finalize_all")


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


func _make_image_window(tex: Texture2D) -> void:
	# Add a TextureRect as a stand-in for the BBCode SubViewport+Label
	# path. Sized to the texture's native dimensions so AsciiComposition's
	# _fit_canvas() / fit-by-size logic still works.
	var tr := TextureRect.new()
	tr.texture = tex
	tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	tr.stretch_mode = TextureRect.STRETCH_SCALE
	tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var tex_sz := tex.get_size()
	tr.size = tex_sz
	size = tex_sz
	add_child(tr)


# ── Frame cycling ─────────────────────────────────────────────────────────────

func load_frames(frame_paths: PackedStringArray, duration: float = -1.0) -> void:
	frames = frame_paths
	if duration > 0.0:
		frame_duration = duration
	_load_frames_internal()


func _load_frames_internal() -> void:
	_clear_viewports()
	for p in frames:
		var data := _read_piece_json(str(p))
		if data.is_empty():
			continue
		_make_viewport_for_data(data)
	call_deferred("_finalize_all")
	_playing = autoplay and _subviewports.size() > 1
	_frame_timer = 0.0


func _process(delta: float) -> void:
	if not _playing or _subviewports.size() <= 1:
		return
	_frame_timer += delta
	if _frame_timer >= frame_duration:
		_frame_timer = 0.0
		var next := _frame_idx + 1
		if next >= _subviewports.size():
			if loop:
				next = 0
			else:
				_playing = false
				return
		_set_active_frame(next)


# ── Internal: SubViewport per-frame plumbing ──────────────────────────────────

func _clear_viewports() -> void:
	for sv in _subviewports:
		if is_instance_valid(sv):
			sv.queue_free()
	_subviewports.clear()
	_labels.clear()
	_frame_idx = 0


func _make_viewport_for_data(data: Dictionary) -> void:
	var sv := SubViewport.new()
	sv.transparent_bg = true
	sv.disable_3d = true
	sv.handle_input_locally = false
	sv.render_target_update_mode = SubViewport.UPDATE_DISABLED
	sv.size = Vector2i(64, 64)
	add_child(sv)

	var lbl := RichTextLabel.new()
	lbl.bbcode_enabled = true
	lbl.fit_content = true
	lbl.scroll_active = false
	lbl.autowrap_mode = TextServer.AUTOWRAP_OFF
	if _font_ref != null:
		lbl.add_theme_font_override("normal_font",  _font_ref)
		lbl.add_theme_font_override("mono_font",    _font_ref)
		lbl.add_theme_font_override("bold_font",    _font_ref)
		lbl.add_theme_font_override("italics_font", _font_ref)
	lbl.add_theme_font_size_override("normal_font_size", font_pixel_size)
	lbl.add_theme_font_size_override("mono_font_size",   font_pixel_size)
	lbl.add_theme_constant_override("line_separation", 0)
	sv.add_child(lbl)

	_build_bbcode_on(lbl, data)
	_subviewports.append(sv)
	_labels.append(lbl)


func _finalize_all() -> void:
	if _subviewports.is_empty():
		return
	await get_tree().process_frame
	for i in range(_subviewports.size()):
		var sv := _subviewports[i]
		var lbl := _labels[i]
		var sz := lbl.size
		var w := int(ceil(maxf(sz.x, 8.0)))
		var h := int(ceil(maxf(sz.y, 8.0)))
		sv.size = Vector2i(w, h)
		sv.render_target_update_mode = SubViewport.UPDATE_ONCE
	# Auto-size this Control to the first frame's rendered dimensions
	var first_sz := _labels[0].size
	size = Vector2(maxf(first_sz.x, 8.0), maxf(first_sz.y, 8.0))
	_set_active_frame(0)
	await get_tree().process_frame
	for sv in _subviewports:
		sv.render_target_update_mode = SubViewport.UPDATE_DISABLED


func _set_active_frame(idx: int) -> void:
	if idx < 0 or idx >= _subviewports.size():
		return
	_frame_idx = idx
	var tex := _subviewports[idx].get_texture()
	if _texture_rect != null:
		_texture_rect.texture = tex
	if _shadow_rect != null:
		_shadow_rect.texture = tex


# ── Internal: JSON I/O + BBCode build ─────────────────────────────────────────

func _read_piece_json(short_path: String) -> Dictionary:
	if short_path == "":
		return {}
	var full := PIECE_ROOT + short_path + ".json"
	if not FileAccess.file_exists(full):
		push_warning("AsciiWindow: piece not found: " + full)
		return {}
	var f := FileAccess.open(full, FileAccess.READ)
	if f == null:
		return {}
	var data: Variant = JSON.parse_string(f.get_as_text())
	if typeof(data) != TYPE_DICTIONARY or not (data as Dictionary).has("cells"):
		return {}
	return data as Dictionary


func _build_bbcode_on(lbl: RichTextLabel, data: Dictionary) -> void:
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
	lbl.text = "".join(parts)
