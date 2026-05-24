extends Control
## AsciiVisualizer — fast, fluid BGM-reactive ASCII window (60 fps).
##
## Renders cells via direct Font.draw_string() calls in _draw() — bypasses
## RichTextLabel + BBCode parsing + SubViewport pipeline entirely. That's
## the only way to hold solid 60 fps at hundreds of cells per frame.
##
## Each column = one log-spaced frequency bucket from AudioMgr's BGM
## spectrum analyzer. Cells fill bottom-up with sub-cell precision via
## ▁▂▃▄▅▆▇█. Column-body density chars (": + * # ▒ ▓ █") give the
## particle-stream feel.

const MONO_FONT_PATH := "res://resources/fonts/SpaceMono-Regular.ttf"

@export var font_pixel_size: int = 14
@export var bar_count:  int = 24
@export var bar_height: int = 14
@export var bar_gap:    int = 0
@export var min_freq:   float = 40.0
@export var max_freq:   float = 14000.0
@export var magnitude_scale: float = 8.0
@export var smoothing: float = 0.15
@export var update_hz: float = 60.0

@export var peak_hold: bool = true
@export var peak_decay: float = 0.97

# Wave-style smoothing across adjacent bars (1D box blur, N passes).
# 0 = jagged bars, 2-3 = soft wave that ripples like water.
@export var wave_smooth_passes: int = 0

@export var col_lo:        Color = Color("#2a4060")
@export var col_mid:       Color = Color("#4a8aaa")
@export var col_hi:        Color = Color("#9bc3ff")
@export var col_peak:      Color = Color("#ffd17a")
@export var col_peak_tip:  Color = Color("#ffffff")
@export var col_dim:       Color = Color("#1a1c20")

const _FILL_CHARS := [" ", "▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
const _DENSITY_CHARS := [":", "+", "*", "#", "▒", "▓", "█"]

var _font: Font = null
var _cell_w: float = 0.0
var _cell_h: float = 0.0
var _font_ascent: float = 0.0
var _bars: Array[float] = []
var _peaks: Array[float] = []
var _accum: float = 0.0


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	if ResourceLoader.exists(MONO_FONT_PATH):
		_font = load(MONO_FONT_PATH)
	_recalc_metrics()
	_resize_buffers()
	_apply_size()


func _recalc_metrics() -> void:
	if _font != null:
		var s := _font.get_string_size("█", HORIZONTAL_ALIGNMENT_LEFT, -1.0, font_pixel_size)
		_cell_w = s.x
		_cell_h = float(font_pixel_size)
		_font_ascent = _font.get_ascent(font_pixel_size)
	else:
		_cell_w = float(font_pixel_size) * 0.6
		_cell_h = float(font_pixel_size)
		_font_ascent = float(font_pixel_size) * 0.85


func _resize_buffers() -> void:
	var old_size := _bars.size()
	_bars.resize(bar_count)
	_peaks.resize(bar_count)
	for i in range(old_size, bar_count):
		_bars[i] = 0.0
		_peaks[i] = 0.0


func _apply_size() -> void:
	var w := float(bar_count) * (_cell_w + float(bar_gap) * _cell_w) - float(bar_gap) * _cell_w
	var h := float(bar_height) * _cell_h
	size = Vector2(w, h)


func _process(delta: float) -> void:
	_accum += delta
	if _accum >= 1.0 / update_hz:
		_accum = 0.0
		_update_bars()
		queue_redraw()


func _update_bars() -> void:
	if _bars.size() != bar_count:
		_resize_buffers()
		_apply_size()
	var lo_log := log(min_freq) / log(10.0)
	var hi_log := log(max_freq) / log(10.0)
	var am := get_node_or_null("/root/AudioMgr")
	for i in range(bar_count):
		var f_lo := pow(10.0, lo_log + (hi_log - lo_log) * (float(i) / bar_count))
		var f_hi := pow(10.0, lo_log + (hi_log - lo_log) * (float(i + 1) / bar_count))
		var mag: float = 0.0
		if am != null and am.has_method("get_bgm_magnitude"):
			mag = float(am.call("get_bgm_magnitude", f_lo, f_hi))
		var target: float = clampf(mag * magnitude_scale, 0.0, 1.0)
		_bars[i] = lerpf(target, _bars[i], smoothing)
		if peak_hold:
			_peaks[i] = maxf(_peaks[i] * peak_decay, _bars[i])
	# Optional spatial smoothing across adjacent bars — gives a wave look.
	for _pass in range(wave_smooth_passes):
		var prev: float = _bars[0]
		for i in range(1, bar_count - 1):
			var curr: float = _bars[i]
			_bars[i] = (prev + curr + _bars[i + 1]) / 3.0
			prev = curr


func _color_for_depth(depth: float) -> Color:
	if depth < 0.18:
		return col_peak
	elif depth < 0.42:
		return col_hi
	elif depth < 0.70:
		return col_mid
	return col_lo


func _column_char(depth_from_top_norm: float) -> String:
	var idx: int = clampi(int(round(depth_from_top_norm * float(_DENSITY_CHARS.size() - 1))), 0, _DENSITY_CHARS.size() - 1)
	return _DENSITY_CHARS[idx]


func _draw() -> void:
	if _font == null:
		return
	if _cell_w <= 0.0 or _cell_h <= 0.0:
		_recalc_metrics()
	# If the user retuned dimensions live, re-apply size before drawing
	var ci := get_canvas_item()
	var col_stride := _cell_w + float(bar_gap) * _cell_w
	for row_i in range(bar_height):
		var depth: float = float(row_i) / maxf(1.0, float(bar_height))
		var col: Color = _color_for_depth(depth)
		var y_baseline: float = float(row_i) * _cell_h + _font_ascent
		for bar_i in range(bar_count):
			var bar_norm: float = _bars[bar_i]
			var bar_px: float = bar_norm * float(bar_height)
			var dist_from_bottom: int = bar_height - row_i
			var full_count: int = int(floor(bar_px))
			var frac: float = bar_px - float(full_count)
			var peak_row: int = bar_height - int(round(_peaks[bar_i] * bar_height))
			var is_peak: bool = peak_hold and row_i == peak_row and _peaks[bar_i] > 0.02

			var ch: String = ""
			var draw_col: Color = col
			if dist_from_bottom <= full_count:
				var bar_depth_from_top: float = 1.0 - float(dist_from_bottom - 1) / maxf(1.0, float(full_count))
				ch = _column_char(bar_depth_from_top)
			elif dist_from_bottom == full_count + 1 and frac > 0.0:
				var frac_idx: int = clampi(int(round(frac * 8.0)), 1, 8)
				ch = str(_FILL_CHARS[frac_idx])
			elif is_peak:
				ch = "▔"
				draw_col = col_peak_tip
			else:
				ch = "·"
				draw_col = col_dim

			var pos := Vector2(float(bar_i) * col_stride, y_baseline)
			_font.draw_string(ci, pos, ch, HORIZONTAL_ALIGNMENT_LEFT, -1.0, font_pixel_size, draw_col)
