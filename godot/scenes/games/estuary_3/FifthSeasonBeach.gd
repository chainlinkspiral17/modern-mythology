extends Control
## Act 4 controller · rhythm-drawing on the beach at low tide.
##
## Loads:  res://resources/games/vol7/estuary_3/act4_fifth_season.json
##
## Contract with Estuary3Host:
##   - Host instantiates FifthSeasonBeach, then calls `boot(host_state)`.
##   - When the tide takes the line and Sam signs (or doesn't), the
##     controller emits `act4_finished(canon_vars, line_stats)`.
##   - Host merges canon_vars, appends the line-shape lore token,
##     writes slowsticks_finished += ['estuary_3'], and advances to
##     the ending screen.
##
## Coordinate note · the JSON's authorial description says "Pacific
## at top of frame, dunes at bottom" but the tide_advance_curve
## values run 460→80 (waterline moves UP the frame). To reconcile,
## we render OCEAN AT THE BOTTOM of the frame — pixels below
## waterline_y are water, pixels above are sand. This matches the
## numeric intent of the schedule.
##
## Real-time compression · the design describes ~90 min drawing +
## ~30 min watching. That's a full session. This scaffold
## compresses the tide schedule 30x so a full playthrough runs
## ~4 minutes. `TIDE_TIME_SCALE` controls the compression at
## runtime.
##
## F4-compliant via add_to_group("ui").

signal act4_finished(canon_vars: Dictionary, line_stats: Dictionary)
signal quit_to_shelf

const ACT4_JSON := "res://resources/games/vol7/estuary_3/act4_fifth_season.json"

# Canvas
const CANVAS_W := 2560
const CANVAS_H := 480
const VIEW_W   := 640
const VIEW_H   := 480
const CAM_MARGIN_X := 240      # keep Sam this far from the left of the view

# Rhythm
const BPM := 72.0
const BEATS_PER_BAR := 4
const BAR_SECONDS := (60.0 / BPM) * float(BEATS_PER_BAR)     # ~3.333s
const PRESS_WINDOW_MS := 380.0

# Line advance
const ADVANCE_PX_PER_BAR := 24.0
const HEADING_START_DEG := -90.0                              # up = -y
const HEADING_UP_LEFT_DELTA := -25.0
const HEADING_DOWN_RIGHT_DELTA := 25.0

# Tide compression
const TIDE_TIME_SCALE := 30.0                                 # 30x faster than authored seconds

# Sam
const SAM_START_X := 128.0
const SAM_START_Y := 400.0
const SAM_STICK_LEN := 12.0

# Palette
const C_BG        := Color(0.04, 0.05, 0.06, 1.0)
const C_SAND      := Color(0.88, 0.82, 0.62, 1.0)
const C_WET_SAND  := Color(0.62, 0.58, 0.48, 1.0)
const C_OCEAN     := Color(0.20, 0.28, 0.36, 1.0)
const C_FOAM      := Color(0.72, 0.82, 0.88, 1.0)
const C_LINE      := Color(0.14, 0.18, 0.22, 1.0)
const C_LINE_DIM  := Color(0.36, 0.38, 0.36, 0.55)
const C_SAM       := Color(0.10, 0.08, 0.06, 1.0)
const C_ACCENT    := Color(0.78, 0.66, 0.29, 1.0)
const C_TXT       := Color(0.83, 0.79, 0.69, 1.0)
const C_TXT_DIM   := Color(0.50, 0.47, 0.38, 1.0)
const C_TIDE_POOL := Color(0.48, 0.60, 0.68, 0.55)

# Loaded data
var _def: Dictionary = {}
var _tide_curve: Array = []           # [{real_seconds, waterline_y}, ...]
var _tide_pools: Array = []           # [{pos_xy, radius_px}, ...]
var _creatures_def: Array = []        # authored def rows

# Session state
var _boot_time_ms: int = 0            # baseline for rhythm timing
var _elapsed_real_seconds: float = 0.0
var _bar_index: int = 0
var _sam_pos: Vector2 = Vector2(SAM_START_X, SAM_START_Y)
var _sam_heading_deg: float = HEADING_START_DEG
var _line_points: Array = []          # PackedVector2Array-like Array of Vector2
var _arc_deltas: Array = []           # per-press arc rotation applied
var _tide_pools_crossed: Array = []   # ids of pools the line has entered
var _self_crossings: int = 0
var _witnessed_creatures: Array = []
var _canon_vars: Dictionary = {}
var _finished: bool = false
var _tide_swallow_progress: float = 0.0

# UI
var _canvas_holder: Control = null    # parent of camera-panned drawing
var _sand_bg: TextureRect = null
var _line2d: Line2D = null
var _waterline_rect: ColorRect = null
var _ocean_fill: ColorRect = null
var _sam_marker: ColorRect = null
var _tide_pool_layer: Control = null
var _creature_layer: Control = null
var _hud_status: Label = null
var _hud_prompt: Label = null
var _hud_bar_indicator: ColorRect = null
var _next_bar_at_seconds: float = 0.0
var _last_press_delta_ms: float = 0.0


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	_load_def()
	_build_ui()
	set_process(true)
	set_process_input(true)


func boot(host_state: Dictionary) -> void:
	var cv: Variant = host_state.get("canon_vars", {})
	_canon_vars = cv.duplicate(true) if cv is Dictionary else {}
	AudioMgr.play_bgm("res://assets/audio/bgm/e3/act4_beach_loop.wav")
	_reset_run()
	_render_opening_narration()


# ─── Data ────────────────────────────────────────────────────────

func _load_def() -> void:
	if not FileAccess.file_exists(ACT4_JSON):
		push_warning("[FifthSeasonBeach] missing %s" % ACT4_JSON)
		return
	var f := FileAccess.open(ACT4_JSON, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if not (parsed is Dictionary):
		return
	_def = parsed
	_tide_curve = _def.get("tide", {}).get("tide_advance_curve", [])
	_tide_pools = _def.get("tide_pools_on_canvas", [])
	_creatures_def = _def.get("sea_creatures", [])


# ─── Reset / bootstrap ────────────────────────────────────────────

func _reset_run() -> void:
	_elapsed_real_seconds = 0.0
	_bar_index = 0
	_sam_pos = Vector2(SAM_START_X, SAM_START_Y)
	_sam_heading_deg = HEADING_START_DEG
	_line_points.clear()
	_line_points.append(_sam_pos)
	_arc_deltas.clear()
	_tide_pools_crossed.clear()
	_self_crossings = 0
	_witnessed_creatures.clear()
	_finished = false
	_tide_swallow_progress = 0.0
	_next_bar_at_seconds = BAR_SECONDS
	_last_press_delta_ms = 0.0
	_boot_time_ms = Time.get_ticks_msec()


# ─── UI build ────────────────────────────────────────────────────

func _build_ui() -> void:
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# Top status bar
	var top := HBoxContainer.new()
	top.set_anchors_preset(Control.PRESET_TOP_WIDE)
	top.offset_left = 16
	top.offset_right = -16
	top.offset_top = 8
	top.offset_bottom = 32
	top.add_theme_constant_override("separation", 16)
	add_child(top)

	var hdr := Label.new()
	hdr.text = "ACT 4 · THE FIFTH SEASON · 5:14 AM"
	hdr.add_theme_font_size_override("font_size", 12)
	hdr.add_theme_color_override("font_color", C_ACCENT)
	top.add_child(hdr)

	_hud_status = Label.new()
	_hud_status.add_theme_font_size_override("font_size", 11)
	_hud_status.add_theme_color_override("font_color", C_TXT)
	top.add_child(_hud_status)

	var s := Control.new()
	s.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top.add_child(s)

	var quit := Button.new()
	quit.text = "  ✕  BACK  "
	quit.pressed.connect(func() -> void: quit_to_shelf.emit())
	top.add_child(quit)

	# Viewport frame · the canvas is 2560 wide but the view is 640.
	# `_canvas_holder` is a Control that we translate left to
	# implement camera pan on Sam.
	var view_wrap := Panel.new()
	view_wrap.set_anchors_preset(Control.PRESET_CENTER)
	view_wrap.custom_minimum_size = Vector2(VIEW_W, VIEW_H)
	view_wrap.size = view_wrap.custom_minimum_size
	view_wrap.position = Vector2(-VIEW_W / 2, -VIEW_H / 2 + 24)
	view_wrap.clip_contents = true
	var vsb := StyleBoxFlat.new()
	vsb.bg_color = C_BG
	vsb.border_color = C_ACCENT
	vsb.set_border_width_all(1)
	view_wrap.add_theme_stylebox_override("panel", vsb)
	add_child(view_wrap)

	_canvas_holder = Control.new()
	_canvas_holder.custom_minimum_size = Vector2(CANVAS_W, CANVAS_H)
	_canvas_holder.size = Vector2(CANVAS_W, CANVAS_H)
	_canvas_holder.position = Vector2(0, 0)
	_canvas_holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	view_wrap.add_child(_canvas_holder)

	# Sand background (procedural).
	_sand_bg = TextureRect.new()
	_sand_bg.position = Vector2(0, 0)
	_sand_bg.size = Vector2(CANVAS_W, CANVAS_H)
	_sand_bg.texture = _make_sand_texture()
	_canvas_holder.add_child(_sand_bg)

	# Tide-pool layer (below the line so lines cross visibly).
	_tide_pool_layer = Control.new()
	_tide_pool_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_tide_pool_layer.position = Vector2.ZERO
	_tide_pool_layer.size = Vector2(CANVAS_W, CANVAS_H)
	_canvas_holder.add_child(_tide_pool_layer)
	_draw_tide_pools()

	# Ocean fill · a big ColorRect below waterline_y. Height is
	# updated per-frame to match the current waterline.
	_ocean_fill = ColorRect.new()
	_ocean_fill.color = C_OCEAN
	_ocean_fill.position = Vector2(0, 460)
	_ocean_fill.size = Vector2(CANVAS_W, 20)
	_canvas_holder.add_child(_ocean_fill)

	# Waterline foam · thin lighter row at the top of the ocean.
	_waterline_rect = ColorRect.new()
	_waterline_rect.color = C_FOAM
	_waterline_rect.position = Vector2(0, 459)
	_waterline_rect.size = Vector2(CANVAS_W, 1)
	_canvas_holder.add_child(_waterline_rect)

	# The line itself · Line2D grows as the player presses.
	_line2d = Line2D.new()
	_line2d.default_color = C_LINE
	_line2d.width = 3.0
	_line2d.round_precision = 4
	_line2d.begin_cap_mode = Line2D.LINE_CAP_ROUND
	_line2d.end_cap_mode = Line2D.LINE_CAP_ROUND
	_canvas_holder.add_child(_line2d)
	# Prime with the starting point so the first press produces a visible segment.
	_line2d.add_point(_sam_pos)

	# Sam marker · a tiny dark square with a "stick" line off to the
	# side pointing in the heading direction.
	_sam_marker = ColorRect.new()
	_sam_marker.color = C_SAM
	_sam_marker.size = Vector2(4, 4)
	_sam_marker.position = _sam_pos - Vector2(2, 2)
	_canvas_holder.add_child(_sam_marker)

	# Creature layer.
	_creature_layer = Control.new()
	_creature_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_creature_layer.position = Vector2.ZERO
	_creature_layer.size = Vector2(CANVAS_W, CANVAS_H)
	_canvas_holder.add_child(_creature_layer)

	# HUD prompt (bottom center)
	_hud_prompt = Label.new()
	_hud_prompt.text = "SPACE · one press per bar"
	_hud_prompt.add_theme_font_size_override("font_size", 10)
	_hud_prompt.add_theme_color_override("font_color", C_TXT_DIM)
	_hud_prompt.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_hud_prompt.offset_left = 16
	_hud_prompt.offset_right = -16
	_hud_prompt.offset_top = -32
	_hud_prompt.offset_bottom = -12
	_hud_prompt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	add_child(_hud_prompt)

	# Bar-indicator · a thin bar that pulses to the metronome, drawn
	# just above the prompt.
	_hud_bar_indicator = ColorRect.new()
	_hud_bar_indicator.color = C_ACCENT
	_hud_bar_indicator.size = Vector2(120, 2)
	_hud_bar_indicator.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_hud_bar_indicator.position = Vector2(0, 0)
	_hud_bar_indicator.offset_left = 0
	_hud_bar_indicator.offset_right = 0
	_hud_bar_indicator.offset_top = -50
	_hud_bar_indicator.offset_bottom = -48
	add_child(_hud_bar_indicator)


func _make_sand_texture() -> ImageTexture:
	# Deterministic value-noise sand grain across the full canvas.
	# Two-tone: base sand, occasional wet-sand freckle. Runs once
	# at boot.
	var img := Image.create(CANVAS_W, CANVAS_H, false, Image.FORMAT_RGBA8)
	# Fill with base sand.
	img.fill(C_SAND)
	# Cheap deterministic freckle pass · integer hash of (x, y)
	# quantized to 4x4 blocks.
	var block := 4
	for by in range(0, CANVAS_H, block):
		for bx in range(0, CANVAS_W, block):
			var h := (bx * 374761393 + by * 668265263)
			var q := (h ^ (h >> 13)) * 1274126177
			q = q ^ (q >> 16)
			var v := int(q & 0xff)
			# ~8% of blocks: slightly darker (drying wet-sand)
			# ~4%: slightly lighter (dune-blown grain)
			if v < 24:
				var c := Color(C_SAND.r * 0.86, C_SAND.g * 0.86, C_SAND.b * 0.86, 1.0)
				for dy in range(block):
					for dx in range(block):
						if bx + dx < CANVAS_W and by + dy < CANVAS_H:
							img.set_pixel(bx + dx, by + dy, c)
			elif v > 240:
				var c2 := Color(min(1.0, C_SAND.r * 1.10), min(1.0, C_SAND.g * 1.10), min(1.0, C_SAND.b * 1.05), 1.0)
				for dy in range(block):
					for dx in range(block):
						if bx + dx < CANVAS_W and by + dy < CANVAS_H:
							img.set_pixel(bx + dx, by + dy, c2)
	return ImageTexture.create_from_image(img)


func _draw_tide_pools() -> void:
	for tp_var in _tide_pools:
		var tp: Dictionary = tp_var
		var xy: Array = tp.get("pos_xy", [0, 0])
		var r: float = float(tp.get("radius_px", 24))
		var center := Vector2(float(xy[0]), float(xy[1]))
		# Cheap "ellipse" as a Panel with rounded corners.
		var pool := Panel.new()
		var sb := StyleBoxFlat.new()
		sb.bg_color = C_TIDE_POOL
		sb.border_color = Color(C_TIDE_POOL.r * 0.7, C_TIDE_POOL.g * 0.7, C_TIDE_POOL.b * 0.7, 1.0)
		sb.set_border_width_all(1)
		sb.set_corner_radius_all(int(r))
		pool.add_theme_stylebox_override("panel", sb)
		pool.position = center - Vector2(r, r * 0.6)
		pool.size = Vector2(r * 2.0, r * 1.2)
		_tide_pool_layer.add_child(pool)


# ─── Rhythm + input ──────────────────────────────────────────────

func _input(event: InputEvent) -> void:
	if _finished: return
	if event is InputEventKey and event.pressed and not event.echo:
		var k: InputEventKey = event
		if k.keycode == KEY_SPACE or k.keycode == KEY_ENTER:
			_register_press()
			get_viewport().set_input_as_handled()


func _register_press() -> void:
	# Measure the press's offset from the current bar's downbeat.
	# The current bar's beat-1 lives at time (_bar_index * BAR_SECONDS)
	# in elapsed seconds; the NEXT beat-1 lives at (_bar_index + 1) *
	# BAR_SECONDS. Compute delta to whichever is closer.
	var now := _elapsed_real_seconds
	var prev_beat := float(_bar_index) * BAR_SECONDS
	var next_beat := float(_bar_index + 1) * BAR_SECONDS
	var delta_prev := (now - prev_beat) * 1000.0
	var delta_next := (now - next_beat) * 1000.0
	var delta_ms := delta_prev
	# Pick whichever is smaller in absolute value.
	if abs(delta_next) < abs(delta_prev):
		delta_ms = delta_next
	var bank := get_node_or_null("/root/SFXBank")
	if abs(delta_ms) > PRESS_WINDOW_MS:
		# Out of window · rest, no advance. Register the press so we
		# don't double-count.
		_last_press_delta_ms = delta_ms
		if bank: bank.play("press_miss", 0.75)
		return
	_last_press_delta_ms = delta_ms
	if bank: bank.play("press_hit", 0.65)
	if bank: bank.play("stick_scratch", 0.55)
	# Advance the bar counter · a press consumes the current bar.
	# If the press falls on the next bar's early window, treat it
	# as that bar's press.
	if delta_ms >= 0:
		# Pressed after the previous bar's beat 1 · this consumes
		# _bar_index. Ready to advance to bar_index+1.
		_bar_index += 1
	else:
		# Pressed before the next bar's beat 1 · this consumes
		# _bar_index + 1. Skip a bar so we don't double-fire.
		_bar_index += 2
	# Apply direction.
	_apply_press_direction(delta_ms)


func _apply_press_direction(delta_ms: float) -> void:
	# JSON's mapping (ms offset → arc_deg):
	#   -190..-95   → -25   (up_and_left)
	#   -94..-30    →  0    (up)
	#   -29..+29    →  0    (on_beat_curve · advance in current heading)
	#   +30..+94    →  0    (down)
	#   +95..+190   → +25   (down_and_right)
	var arc_deg := 0.0
	if delta_ms <= -95.0:
		arc_deg = HEADING_UP_LEFT_DELTA
	elif delta_ms >= 95.0:
		arc_deg = HEADING_DOWN_RIGHT_DELTA
	_sam_heading_deg += arc_deg
	# Keep heading in [-180, +180] for legibility.
	while _sam_heading_deg > 180.0: _sam_heading_deg -= 360.0
	while _sam_heading_deg < -180.0: _sam_heading_deg += 360.0
	_arc_deltas.append(arc_deg)
	# Advance Sam by ADVANCE_PX_PER_BAR in current heading.
	var rad := deg_to_rad(_sam_heading_deg)
	var new_pos := _sam_pos + Vector2(cos(rad), sin(rad)) * ADVANCE_PX_PER_BAR
	# Clamp inside canvas.
	new_pos.x = clamp(new_pos.x, 0.0, float(CANVAS_W))
	new_pos.y = clamp(new_pos.y, 20.0, 460.0)   # keep off the waterline row
	_line_points.append(new_pos)
	_line2d.add_point(new_pos)
	_maybe_record_self_crossing(_sam_pos, new_pos)
	_maybe_record_tide_pool_cross(new_pos)
	_sam_pos = new_pos
	# Trigger sea creatures based on new shape.
	_evaluate_creatures()


func _maybe_record_self_crossing(a: Vector2, b: Vector2) -> void:
	# Line segment ab against all prior segments.
	if _line_points.size() < 4:
		return
	# The last segment is (a, b). Check against segments 0..n-2.
	for i in range(_line_points.size() - 3):
		var p1: Vector2 = _line_points[i]
		var p2: Vector2 = _line_points[i + 1]
		if _segments_cross(a, b, p1, p2):
			_self_crossings += 1
			return


func _segments_cross(a: Vector2, b: Vector2, c: Vector2, d: Vector2) -> bool:
	# Simple segment intersection · signs of cross products.
	var d1 := _cross_side(a, b, c)
	var d2 := _cross_side(a, b, d)
	var d3 := _cross_side(c, d, a)
	var d4 := _cross_side(c, d, b)
	if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) \
		and ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
		return true
	return false


func _cross_side(a: Vector2, b: Vector2, c: Vector2) -> float:
	return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)


func _maybe_record_tide_pool_cross(pos: Vector2) -> void:
	for i in range(_tide_pools.size()):
		var tp: Dictionary = _tide_pools[i]
		var xy: Array = tp.get("pos_xy", [0, 0])
		var r: float = float(tp.get("radius_px", 24))
		var center := Vector2(float(xy[0]), float(xy[1]))
		if pos.distance_to(center) <= r:
			var pid := "pool_%d" % i
			if not _tide_pools_crossed.has(pid):
				_tide_pools_crossed.append(pid)
				var bank := get_node_or_null("/root/SFXBank")
				if bank: bank.play("tide_pool_splash", 0.7)


# ─── Sea creatures ───────────────────────────────────────────────

func _evaluate_creatures() -> void:
	# Bar-index based arrival thresholds + shape-based preference.
	for c_var in _creatures_def:
		var c: Dictionary = c_var
		var cid: String = String(c.get("id", ""))
		if _witnessed_creatures.has(cid):
			continue
		var min_bars: int = int(c.get("arrives_after_bars_min", 0))
		if _bar_index < min_bars:
			continue
		var prefers: String = String(c.get("prefers", ""))
		if _creature_condition_met(prefers, c):
			_witnessed_creatures.append(cid)
			_render_creature(cid, c)


func _creature_condition_met(prefers: String, c: Dictionary) -> bool:
	match prefers:
		"smooth_lines":
			return _avg_arc_abs() < 8.0
		"lines_that_cross_water":
			return not _tide_pools_crossed.is_empty()
		"lines_that_turn_back_on_themselves":
			return _self_crossings >= 1
		"jagged_lines":
			return _avg_arc_abs() > 18.0
		"always_present":
			return true
		_:
			return false


func _render_creature(cid: String, c: Dictionary) -> void:
	# Small silhouette at an authored position (or near the line's
	# most recent point for otter / crab). This is a placeholder
	# color-only render; SlowstockSprite integration for act4/
	# creature icons is a follow-up.
	var pos: Vector2 = _sam_pos + Vector2(-16, -12)   # default: next to Sam
	# The 2 AM customer on the dune ridge at (2400, 30).
	var authored: Dictionary = c.get("position_relative_to_line", {}) if c.get("position_relative_to_line", null) is Dictionary else {}
	if cid == "the_2am_customer":
		pos = Vector2(2400, 30)
	elif cid == "the_kid_on_the_bike":
		pos = Vector2(128, 20)
	# Creature-specific arrival SFX for the two deferred ones · Wave E.
	var sfx_bank := get_node_or_null("/root/SFXBank")
	if sfx_bank:
		if cid == "the_2am_customer":
			sfx_bank.play("creature_arrival_2am_customer", 0.65)
		elif cid == "the_kid_on_the_bike":
			sfx_bank.play("creature_arrival_kid_on_bike", 0.70)
	var creature_color: Color = _creature_color_for(cid)
	var pnl := ColorRect.new()
	pnl.color = creature_color
	pnl.size = Vector2(6, 6)
	if cid == "great_blue_heron": pnl.size = Vector2(4, 10)
	elif cid == "river_otter":    pnl.size = Vector2(10, 4)
	elif cid == "cutthroat_fry":  pnl.size = Vector2(4, 2)
	elif cid == "great_blue_crab":pnl.size = Vector2(8, 6)
	elif cid == "the_2am_customer": pnl.size = Vector2(6, 12)
	elif cid == "the_kid_on_the_bike": pnl.size = Vector2(8, 8)
	pnl.position = pos - pnl.size / 2
	_creature_layer.add_child(pnl)
	# HUD note.
	_hud_prompt.text = "· %s ·" % String(c.get("label", cid)).to_lower()


func _creature_color_for(cid: String) -> Color:
	match cid:
		"great_blue_heron":     return Color(0.42, 0.48, 0.52)
		"cutthroat_fry":        return Color(0.88, 0.92, 0.94)
		"river_otter":          return Color(0.36, 0.24, 0.16)
		"great_blue_crab":      return Color(0.72, 0.24, 0.28)
		"the_2am_customer":     return Color(0.28, 0.30, 0.34)
		"the_kid_on_the_bike":  return Color(0.20, 0.32, 0.48)
		_:                      return Color(0.5, 0.5, 0.5)


# ─── Frame ───────────────────────────────────────────────────────

func _process(dt: float) -> void:
	if _finished: return
	_elapsed_real_seconds += dt
	_advance_tide()
	_update_camera()
	_update_hud()
	_update_metronome()
	# End trigger · when the compressed tide has climbed past the
	# drawing's minimum y (i.e. water is over most of the line),
	# transition to signing.
	if _line_points.size() > 1 and _waterline_y() < _line_min_y() + 8:
		_end_run(false)
	# Or if the player walks off the east edge of the canvas.
	if _sam_pos.x >= float(CANVAS_W) - 12.0:
		_end_run(false)


func _advance_tide() -> void:
	if _tide_curve.is_empty(): return
	var t_scaled := _elapsed_real_seconds * TIDE_TIME_SCALE
	# Find the two curve points bracketing t_scaled.
	var lo := _tide_curve[0]
	var hi := _tide_curve[_tide_curve.size() - 1]
	for i in range(_tide_curve.size() - 1):
		if float(_tide_curve[i]["real_seconds"]) <= t_scaled and \
		   float(_tide_curve[i + 1]["real_seconds"]) >= t_scaled:
			lo = _tide_curve[i]
			hi = _tide_curve[i + 1]
			break
	var span := max(0.001, float(hi["real_seconds"]) - float(lo["real_seconds"]))
	var frac := clamp((t_scaled - float(lo["real_seconds"])) / span, 0.0, 1.0)
	var wy := lerp(float(lo["waterline_y"]), float(hi["waterline_y"]), frac)
	# Draw water below waterline_y (ocean fill), foam AT waterline_y.
	_waterline_rect.position = Vector2(0, wy)
	_ocean_fill.position = Vector2(0, wy + 1)
	_ocean_fill.size = Vector2(CANVAS_W, max(0.0, float(CANVAS_H) - wy - 1))
	# Line segments below waterline dim slightly to suggest swallow.
	if _line2d != null and _line_points.size() > 1:
		# Cheap: fade the whole line proportional to how much is
		# below water. A full pass would rebuild the line with
		# per-point colors, but Line2D uses default_color; we tint
		# the whole thing modulated by swallow_frac.
		var below_count := 0
		for p in _line_points:
			if (p as Vector2).y >= wy: below_count += 1
		var swallow := float(below_count) / float(_line_points.size())
		_tide_swallow_progress = swallow
		_line2d.modulate = Color(1, 1, 1, lerp(1.0, 0.28, swallow))


func _waterline_y() -> float:
	return _waterline_rect.position.y if _waterline_rect else 460.0


func _line_min_y() -> float:
	var m := 480.0
	for p in _line_points:
		var y := (p as Vector2).y
		if y < m: m = y
	return m


func _update_camera() -> void:
	# Sam-follows. Position the canvas_holder so Sam sits at
	# CAM_MARGIN_X from the left of the view.
	var target_x := clamp(_sam_pos.x - float(CAM_MARGIN_X), 0.0, float(CANVAS_W - VIEW_W))
	# Smooth toward target.
	_canvas_holder.position.x = lerp(_canvas_holder.position.x, -target_x, 0.15)
	# Move Sam marker.
	_sam_marker.position = _sam_pos - Vector2(2, 2)


func _update_hud() -> void:
	if _hud_status == null: return
	var hh := 5
	var mm := 14 + int(_elapsed_real_seconds * TIDE_TIME_SCALE / 60.0)
	while mm >= 60:
		hh += 1
		mm -= 60
	_hud_status.text = "  clock %02d:%02d  ·  bar %d  ·  |arc| %.1f°  ·  crossings %d  ·  pools %d  ·  creatures %d" % [
		hh, mm, _bar_index, _avg_arc_abs(), _self_crossings, _tide_pools_crossed.size(), _witnessed_creatures.size()]


func _update_metronome() -> void:
	# Pulse the bar indicator's alpha with bar phase.
	var phase := fmod(_elapsed_real_seconds, BAR_SECONDS) / BAR_SECONDS
	# Bright at beat 1, decays over the bar.
	var alpha := max(0.15, 1.0 - phase * 0.85)
	_hud_bar_indicator.color = Color(C_ACCENT.r, C_ACCENT.g, C_ACCENT.b, alpha)


# ─── End of run · shape analysis + ending pick ────────────────────

func _end_run(quit: bool) -> void:
	if _finished: return
	_finished = true
	set_process(false)
	# Compute line stats.
	var stats := _compute_line_stats()
	# Select the ending.
	var ending := _pick_ending(stats)
	stats["ending_id"] = String(ending.get("id", "fallback"))
	stats["ending_narration"] = String(ending.get("trigger_narration", ""))
	stats["signing_action"] = String(ending.get("signing_action", ""))
	stats["final_line_before_credits"] = String(ending.get("final_line_before_credits", ""))
	# Extract canon_vars / lore_token from the ending's gauntlet_state.
	var gs: Dictionary = ending.get("gauntlet_state", {})
	var cv: Dictionary = gs.get("canon_var", {})
	for k in cv.keys():
		_canon_vars[String(k)] = cv[k]
	stats["lore_token"] = String(gs.get("lore_token", ""))
	# Show the end screen.
	_render_end_screen(stats)


func _compute_line_stats() -> Dictionary:
	var total_length := 0.0
	for i in range(_line_points.size() - 1):
		total_length += (_line_points[i + 1] as Vector2).distance_to(_line_points[i] as Vector2)
	var stats := {
		"average_arc_deg_absolute_value": _avg_arc_abs(),
		"count_of_self_crossings":         _self_crossings,
		"total_length_pixels":              total_length,
		"count_of_tide_pools_crossed":      _tide_pools_crossed.size(),
		"any_stroke_west_of_starting_position": _any_stroke_west_of(SAM_START_X),
		"any_stroke_east_of_2000px_x":     _any_stroke_east_of(2000.0),
		"creatures_witnessed":              _witnessed_creatures.duplicate(),
	}
	return stats


func _avg_arc_abs() -> float:
	if _arc_deltas.is_empty():
		return 0.0
	var total := 0.0
	for a in _arc_deltas:
		total += abs(float(a))
	return total / float(_arc_deltas.size())


func _any_stroke_west_of(x: float) -> bool:
	for p in _line_points:
		if (p as Vector2).x < x: return true
	return false


func _any_stroke_east_of(x: float) -> bool:
	for p in _line_points:
		if (p as Vector2).x > x: return true
	return false


func _pick_ending(stats: Dictionary) -> Dictionary:
	# The JSON authors five endings with conditions. We evaluate the
	# first four by matching the literal condition strings; if none
	# hits, the fallback ending fires.
	var endings: Array = _def.get("endings", [])
	var avg_arc := float(stats["average_arc_deg_absolute_value"])
	var crossings := int(stats["count_of_self_crossings"])
	var total_len := float(stats["total_length_pixels"])
	for e_var in endings:
		var e: Dictionary = e_var
		var eid := String(e.get("id", ""))
		match eid:
			"the_line_was_smooth":
				if avg_arc < 8.0 and crossings == 0 and total_len >= 400.0:
					return e
			"the_line_was_jagged":
				if avg_arc > 18.0 or crossings >= 3:
					return e
			"the_line_turned_back_on_itself":
				if crossings >= 1 and crossings < 3 and avg_arc >= 8.0 and avg_arc <= 18.0:
					return e
			"the_line_was_unfinished":
				if total_len < 400.0:
					return e
			"fallback":
				continue   # fall through to end
	# If nothing matched above, use the authored fallback if any.
	for e_var in endings:
		var e: Dictionary = e_var
		if String(e.get("id", "")) == "fallback":
			return e
	return {}


func _render_end_screen(stats: Dictionary) -> void:
	# Fade out the canvas holder and print the end narration.
	_canvas_holder.modulate = Color(1, 1, 1, 0.45)
	var overlay := Panel.new()
	overlay.set_anchors_preset(Control.PRESET_CENTER)
	overlay.custom_minimum_size = Vector2(560, 320)
	overlay.size = overlay.custom_minimum_size
	overlay.position = Vector2(-280, -160)
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.024, 0.020, 0.014, 0.94)
	sb.border_color = C_ACCENT
	sb.set_border_width_all(1)
	overlay.add_theme_stylebox_override("panel", sb)
	add_child(overlay)

	var col := VBoxContainer.new()
	col.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	col.offset_left = 16
	col.offset_right = -16
	col.offset_top = 16
	col.offset_bottom = -16
	col.add_theme_constant_override("separation", 6)
	overlay.add_child(col)

	var hdr := Label.new()
	hdr.text = "· 7:14 AM ·"
	hdr.add_theme_font_size_override("font_size", 12)
	hdr.add_theme_color_override("font_color", C_ACCENT)
	col.add_child(hdr)

	var body := RichTextLabel.new()
	body.bbcode_enabled = true
	body.fit_content = true
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.add_theme_color_override("default_color", C_TXT)
	body.add_theme_font_size_override("normal_font_size", 11)
	body.append_text("[i]%s[/i]\n\n" % String(stats.get("ending_narration", "")))
	body.append_text("[color=#c8a842]%s[/color]\n\n" % String(stats.get("signing_action", "")))
	body.append_text("[b]%s[/b]" % String(stats.get("final_line_before_credits", "")))
	col.add_child(body)

	var actions := HBoxContainer.new()
	actions.alignment = BoxContainer.ALIGNMENT_END
	col.add_child(actions)

	var next := Button.new()
	next.text = "  →  THE ENDING QUESTION  "
	next.pressed.connect(func() -> void:
		# Append the lore token to canon_vars for the host to write.
		var lore: String = String(stats.get("lore_token", ""))
		var pending: Array = _canon_vars.get("_lore_tokens_pending", [])
		if lore != "" and not pending.has(lore):
			pending.append(lore)
			_canon_vars["_lore_tokens_pending"] = pending
		act4_finished.emit(_canon_vars, stats))
	actions.add_child(next)


# ─── Opening narration overlay ────────────────────────────────────

func _render_opening_narration() -> void:
	var overlay := Panel.new()
	overlay.set_anchors_preset(Control.PRESET_CENTER)
	overlay.custom_minimum_size = Vector2(560, 260)
	overlay.size = overlay.custom_minimum_size
	overlay.position = Vector2(-280, -130)
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.024, 0.020, 0.014, 0.94)
	sb.border_color = C_ACCENT
	sb.set_border_width_all(1)
	overlay.add_theme_stylebox_override("panel", sb)
	add_child(overlay)

	var col := VBoxContainer.new()
	col.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	col.offset_left = 16
	col.offset_right = -16
	col.offset_top = 16
	col.offset_bottom = -16
	col.add_theme_constant_override("separation", 6)
	overlay.add_child(col)

	var hdr := Label.new()
	hdr.text = "· 5:14 AM · TUESDAY AFTER LABOR DAY ·"
	hdr.add_theme_font_size_override("font_size", 12)
	hdr.add_theme_color_override("font_color", C_ACCENT)
	col.add_child(hdr)

	var body := RichTextLabel.new()
	body.bbcode_enabled = true
	body.fit_content = true
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.add_theme_color_override("default_color", C_TXT)
	body.add_theme_font_size_override("normal_font_size", 10)
	var opening: Array = _def.get("opening_narration", [])
	for line in opening:
		body.append_text("[i]%s[/i]\n\n" % String(line))
	col.add_child(body)

	var actions := HBoxContainer.new()
	actions.alignment = BoxContainer.ALIGNMENT_END
	col.add_child(actions)

	var begin := Button.new()
	begin.text = "  pick up the stick  "
	begin.pressed.connect(func() -> void:
		overlay.queue_free()
		# Reset the elapsed-time origin so bar 0 starts now.
		_reset_run())
	actions.add_child(begin)
