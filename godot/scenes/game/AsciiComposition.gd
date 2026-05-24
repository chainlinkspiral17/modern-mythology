extends Control
## AsciiComposition — multi-window ASCII layout.
##
## Reads a manifest at res://resources/substrates/compositions/<id>.json:
##   {
##     "canvas": [W, H],          # logical pixel dimensions
##     "windows": [
##       { "path": "pieces/foo", "x": 100, "y": 50, "font_px": 24, "z": 5 }
##     ]
##   }
## Instantiates an AsciiWindow per entry, positions in logical canvas
## space, then scales the whole canvas to fit this Control while
## preserving aspect.

const COMPOSITION_ROOT := "res://resources/substrates/compositions/"
const WINDOW_SCRIPT := preload("res://scenes/game/AsciiWindow.gd")
const VISUALIZER_SCRIPT := preload("res://scenes/game/AsciiVisualizer.gd")

var _canvas: Control = null
var _canvas_size: Vector2 = Vector2(1920, 1080)
var _bg_color_str: String = ""
var _composition_id: String = ""
# Original manifest entries per window, in order. Updated by debug overlay
# so an export reflects current live state.
var _window_manifests: Array = []
var _windows_list: Array = []  # parallel array of Control nodes

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	resized.connect(_fit_canvas)

func load_composition(short_path: String) -> void:
	if short_path == "":
		return
	_composition_id = short_path
	var full := COMPOSITION_ROOT + short_path + ".json"
	if not FileAccess.file_exists(full):
		push_warning("AsciiComposition: not found: " + full)
		return
	var f := FileAccess.open(full, FileAccess.READ)
	if f == null:
		return
	var data: Variant = JSON.parse_string(f.get_as_text())
	if typeof(data) != TYPE_DICTIONARY or not data.has("windows"):
		push_warning("AsciiComposition: invalid manifest: " + full)
		return
	_build(data)


# ── Public API for the debug overlay ──────────────────────────────────────────

func get_windows() -> Array:
	# Returns parallel arrays of (Control, manifest_dict). Caller can mutate
	# control properties live and update the manifest_dict to reflect that
	# for export.
	var out := []
	for i in range(_windows_list.size()):
		out.append({"node": _windows_list[i], "manifest": _window_manifests[i]})
	return out

func composition_id() -> String:
	return _composition_id

func export_manifest() -> Dictionary:
	# Build a fresh manifest dict from current live window state.
	var windows := []
	for i in range(_windows_list.size()):
		var n: Control = _windows_list[i]
		var m: Dictionary = (_window_manifests[i] as Dictionary).duplicate(true)
		m["x"] = int(round(n.position.x))
		m["y"] = int(round(n.position.y))
		m["z"] = n.z_index
		m["alpha"] = snappedf(n.modulate.a, 0.01)
		if "font_pixel_size" in n:
			m["font_px"] = n.font_pixel_size
		var kind: String = str(m.get("kind", "static"))
		if kind == "visualizer":
			m["bar_count"] = n.bar_count
			m["bar_height"] = n.bar_height
			m["bar_gap"] = n.bar_gap
			m["min_freq"] = snappedf(n.min_freq, 1.0)
			m["max_freq"] = snappedf(n.max_freq, 1.0)
			m["magnitude"] = snappedf(n.magnitude_scale, 0.01)
			m["smoothing"] = snappedf(n.smoothing, 0.001)
			m["peak_decay"] = snappedf(n.peak_decay, 0.001)
		windows.append(m)
	return {
		"id": _composition_id,
		"canvas": [int(_canvas_size.x), int(_canvas_size.y)],
		"bg": _bg_color_str,
		"windows": windows,
	}

func _build(data: Dictionary) -> void:
	if _canvas != null:
		_canvas.queue_free()
	_windows_list.clear()
	_window_manifests.clear()

	var canvas_arr = data.get("canvas", [1920, 1080])
	_canvas_size = Vector2(float(canvas_arr[0]), float(canvas_arr[1]))

	_canvas = Control.new()
	_canvas.size = _canvas_size
	_canvas.pivot_offset = Vector2.ZERO
	_canvas.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_canvas)

	var bg_color: Variant = data.get("bg")
	_bg_color_str = str(bg_color) if bg_color != null else ""
	if bg_color != null:
		var rect := ColorRect.new()
		rect.color = Color(_bg_color_str)
		rect.size = _canvas_size
		rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_canvas.add_child(rect)

	for w_data in data.get("windows", []):
		_add_window(w_data)

	await get_tree().process_frame
	_fit_canvas()

func _add_window(w: Dictionary) -> void:
	var kind := str(w.get("kind", "static"))

	# Image kind: raw PNG/JPG texture, not ASCII. Useful as a deep
	# background under semi-transparent ASCII layers.
	if kind == "image":
		_add_image_window(w)
		return

	# image_frames: cycle a list of PNG textures at a fixed interval.
	# All frames must be the same size; placed and scaled like the
	# single-image kind. Used for pre-rasterized ASCII flicker, where
	# we want exact pixel alignment with other image layers without
	# paying the SubViewport cost of live ASCII cycling.
	if kind == "image_frames":
		_add_image_frames_window(w)
		return

	var win := Control.new()
	if kind == "visualizer":
		win.set_script(VISUALIZER_SCRIPT)
	else:
		win.set_script(WINDOW_SCRIPT)
	win.position = Vector2(float(w.get("x", 0)), float(w.get("y", 0)))
	if w.has("font_px"):
		win.font_pixel_size = int(w["font_px"])
	if w.has("z"):
		win.z_index = int(w["z"])
	win.mouse_filter = Control.MOUSE_FILTER_IGNORE

	# Visualizer-specific config
	if kind == "visualizer":
		if w.has("bar_count"):    win.bar_count        = int(w["bar_count"])
		if w.has("bar_height"):   win.bar_height       = int(w["bar_height"])
		if w.has("bar_gap"):      win.bar_gap          = int(w["bar_gap"])
		if w.has("min_freq"):     win.min_freq         = float(w["min_freq"])
		if w.has("max_freq"):     win.max_freq         = float(w["max_freq"])
		if w.has("magnitude"):    win.magnitude_scale  = float(w["magnitude"])
		if w.has("smoothing"):    win.smoothing        = float(w["smoothing"])
		if w.has("peak_decay"):   win.peak_decay       = float(w["peak_decay"])
		if w.has("peak_hold"):    win.peak_hold        = bool(w["peak_hold"])
		if w.has("wave_smooth_passes"): win.wave_smooth_passes = int(w["wave_smooth_passes"])
		if w.has("update_hz"):    win.update_hz        = float(w["update_hz"])
		if w.has("col_lo"):       win.col_lo           = Color(str(w["col_lo"]))
		if w.has("col_mid"):      win.col_mid          = Color(str(w["col_mid"]))
		if w.has("col_hi"):       win.col_hi           = Color(str(w["col_hi"]))
		if w.has("col_peak"):     win.col_peak         = Color(str(w["col_peak"]))
		if w.has("col_dim"):      win.col_dim          = Color(str(w["col_dim"]))
		if w.has("col_peak_tip"): win.col_peak_tip     = Color(str(w["col_peak_tip"]))

	# Generic visual modifiers
	if w.has("modulate"):
		win.modulate = Color(str(w["modulate"]))
	if w.has("alpha"):
		var a: float = float(w["alpha"])
		var m: Color = win.modulate
		win.modulate = Color(m.r, m.g, m.b, a)

	# Static-window-specific options
	if kind != "visualizer":
		if w.has("shadow_color"):
			win.shadow_color = Color(str(w["shadow_color"]))
		if w.has("shadow_offset"):
			var so = w["shadow_offset"]
			if so is Array and so.size() >= 2:
				win.shadow_offset = Vector2(float(so[0]), float(so[1]))
		if w.has("frames"):
			var fr_v = w["frames"]
			if fr_v is Array:
				var fr := PackedStringArray()
				for item in fr_v:
					fr.append(str(item))
				win.frames = fr
		if w.has("frame_duration"):
			win.frame_duration = float(w["frame_duration"])

	_canvas.add_child(win)
	_windows_list.append(win)
	_window_manifests.append(w.duplicate(true))

	if kind != "visualizer" and not w.has("frames"):
		var path: String = str(w.get("path", ""))
		win.call_deferred("load_piece", path)

func _parse_stretch(v: Variant) -> int:
	# Manifest accepts: "scale" (default, fills w×h, may distort),
	# "cover" (keep aspect, crop), "fit" (keep aspect, letterbox),
	# "keep_centered" (no stretch, center within box).
	match str(v):
		"cover":         return TextureRect.STRETCH_KEEP_ASPECT_COVERED
		"fit":           return TextureRect.STRETCH_KEEP_ASPECT
		"keep_centered": return TextureRect.STRETCH_KEEP_CENTERED
		_:               return TextureRect.STRETCH_SCALE


func _fit_canvas() -> void:
	if _canvas == null or _canvas_size.x <= 0 or _canvas_size.y <= 0:
		return
	var viewer := size
	if viewer.x <= 0 or viewer.y <= 0:
		return
	var s := minf(viewer.x / _canvas_size.x, viewer.y / _canvas_size.y)
	_canvas.scale = Vector2(s, s)
	_canvas.position = (viewer - _canvas_size * s) * 0.5


func _add_image_window(w: Dictionary) -> void:
	var path: String = str(w.get("path", ""))
	if path == "":
		return
	var full := "res://" + path if not path.begins_with("res://") else path
	if not ResourceLoader.exists(full):
		push_warning("AsciiComposition: image not found: " + full)
		return
	var tex: Texture2D = ResourceLoader.load(full) as Texture2D
	if tex == null:
		return
	var win := TextureRect.new()
	win.texture = tex
	win.stretch_mode = _parse_stretch(w.get("stretch", "scale"))
	win.position = Vector2(float(w.get("x", 0)), float(w.get("y", 0)))
	var win_w: float = float(w.get("w", _canvas_size.x))
	var win_h: float = float(w.get("h", _canvas_size.y))
	win.size = Vector2(win_w, win_h)
	if w.has("z"):
		win.z_index = int(w["z"])
	win.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if w.has("modulate"):
		win.modulate = Color(str(w["modulate"]))
	if w.has("alpha"):
		var a: float = float(w["alpha"])
		var m: Color = win.modulate
		win.modulate = Color(m.r, m.g, m.b, a)
	_canvas.add_child(win)
	_windows_list.append(win)
	_window_manifests.append(w.duplicate(true))


func _add_image_frames_window(w: Dictionary) -> void:
	var frames_v: Variant = w.get("frames", [])
	if typeof(frames_v) != TYPE_ARRAY or (frames_v as Array).is_empty():
		return
	var textures: Array[Texture2D] = []
	for p_v in frames_v:
		var p: String = str(p_v)
		var full := "res://" + p if not p.begins_with("res://") else p
		if not ResourceLoader.exists(full):
			push_warning("AsciiComposition: image_frames missing: " + full)
			continue
		var t := ResourceLoader.load(full) as Texture2D
		if t != null:
			textures.append(t)
	if textures.is_empty():
		return

	var win := TextureRect.new()
	win.texture = textures[0]
	win.stretch_mode = _parse_stretch(w.get("stretch", "scale"))
	win.position = Vector2(float(w.get("x", 0)), float(w.get("y", 0)))
	win.size = Vector2(float(w.get("w", _canvas_size.x)), float(w.get("h", _canvas_size.y)))
	if w.has("z"):
		win.z_index = int(w["z"])
	win.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if w.has("modulate"):
		win.modulate = Color(str(w["modulate"]))
	if w.has("alpha"):
		var a: float = float(w["alpha"])
		var m: Color = win.modulate
		win.modulate = Color(m.r, m.g, m.b, a)
	_canvas.add_child(win)
	_windows_list.append(win)
	_window_manifests.append(w.duplicate(true))

	# Drive frame cycling from a self-contained Timer so each window
	# advances independently without a _process loop on the composition.
	var dur: float = float(w.get("frame_duration", 0.5))
	if textures.size() > 1 and dur > 0.0:
		var timer := Timer.new()
		timer.wait_time = dur
		timer.one_shot  = false
		timer.autostart = true
		win.add_child(timer)
		var idx_ref := [0]
		timer.timeout.connect(func() -> void:
			idx_ref[0] = (idx_ref[0] + 1) % textures.size()
			win.texture = textures[idx_ref[0]]
		)

	# Audio-reactive alpha: when present, win.modulate.a oscillates
	# around base_alpha by ±magnitude × bus magnitude in [freq_lo, freq_hi].
	# Use a tiny inline ticker rather than another _process on the canvas.
	if w.has("audio_reactive"):
		_attach_audio_reactive_alpha(win, w["audio_reactive"])


func _attach_audio_reactive_alpha(win: TextureRect, cfg_v: Variant) -> void:
	if typeof(cfg_v) != TYPE_DICTIONARY:
		return
	var cfg: Dictionary = cfg_v
	var freq_lo: float    = float(cfg.get("freq_lo", 30.0))
	var freq_hi: float    = float(cfg.get("freq_hi", 200.0))
	var base_alpha: float = float(cfg.get("base_alpha", win.modulate.a))
	var magnitude: float  = float(cfg.get("magnitude", 6.0))
	var smoothing: float  = clampf(float(cfg.get("smoothing", 0.18)), 0.0, 0.95)
	var min_alpha: float  = float(cfg.get("min_alpha", 0.05))
	var max_alpha: float  = float(cfg.get("max_alpha", 1.0))
	var hz: float         = maxf(15.0, float(cfg.get("update_hz", 30.0)))

	var ticker := Timer.new()
	ticker.wait_time = 1.0 / hz
	ticker.one_shot  = false
	ticker.autostart = true
	win.add_child(ticker)

	var smoothed_ref := [0.0]
	ticker.timeout.connect(func() -> void:
		var am := get_node_or_null("/root/AudioMgr")
		if am == null or not am.has_method("get_bgm_magnitude"):
			return
		var mag: float = clampf(float(am.call("get_bgm_magnitude", freq_lo, freq_hi)) * magnitude, 0.0, 1.0)
		smoothed_ref[0] = lerpf(mag, smoothed_ref[0], smoothing)
		var a: float = clampf(base_alpha + smoothed_ref[0] * (max_alpha - base_alpha), min_alpha, max_alpha)
		var m: Color = win.modulate
		win.modulate = Color(m.r, m.g, m.b, a)
	)
