extends Control
class_name LongWindFlight
## SPIDERDROPS 2 · the long wind · the balloon-glide core.
##
## Seven legs. Each leg: SETTLE on a branch (silk refills; cast when
## ready), then FLY — balloon on the tailwind across the gap. Hold the
## spider in the WIND BAND (the bright stripe) where the wind carries
## you fastest; drift too low into the churn and the rain drinks your
## silk. Lifting spends silk; the only failure is running dry mid-air,
## which is not really a failure — the wind just takes you (STILL
## FLYING). Cross all seven and you ARRIVE.
##
## The wind that broke the web in game 1 is the wind you ride here.
##
## Emits (host contract): quit · run_over(result: Dictionary)
## F4-compliant via add_to_group("ui").

signal quit
signal run_over(result: Dictionary)

const VW := 1280.0
const VH := 720.0
const SPIDER_X := 320.0

const LEGS := 7
const LEG_DIST := 1600.0

const GRAVITY := 520.0
const LIFT := 980.0
const STEER := 300.0
const V_DAMP := 0.90
const WIND_BASE := 250.0
const WIND_GUST := 560.0
const GUST_PERIOD := 5.0

const BAND_HI := 200.0        # wind band top (screen y)
const BAND_LO := 460.0        # wind band bottom
const CHURN_Y := 600.0        # below this = rain/churn

const SILK_MAX := 100.0
const LIFT_COST := 17.0
const STEER_COST := 5.0
const CHURN_DRAIN := 26.0
const SETTLE_REFILL := 70.0
const SETTLE_MIN := 1.2       # earliest you can cast

const SCORE_RATE := 0.05

# palette (dawn after the storm — the wind is a friend now)
const C_SKY := Color("3a4d6b")
const C_SKY2 := Color("6c7fa0")
const C_BAND := Color("9fd0e8")
const C_CHURN := Color("212c40")
const C_SILK := Color("e8ecef")
const C_DROP := Color("6fb7e0")
const C_BRANCH := Color("241c18")
const C_SPIDER := Color("f2c14e")
const C_SPIDER_DK := Color("9c7a24")
const C_DEBRIS := Color("6b5535")
const C_STAR := Color("f2c14e")

var _leg: int = 1
var _phase: String = "settle"     # settle | fly
var _phase_t: float = 0.0
var _sy: float = 360.0            # spider screen y
var _vy: float = 0.0
var _dist: float = 0.0            # progress along the current leg
var _silk: float = SILK_MAX
var _carry_star: bool = false
var _score: float = 0.0
var _legs_crossed: int = 0
var _t: float = 0.0
var _gust: float = 0.0
var _running: bool = false
var _resolved: bool = false

var _debris: Array = []          # each {x, y, vx}
var _debris_timer: float = 0.0

# HUD
var _hud_leg: Label = null
var _hud_silk: Label = null
var _hud_dist: Label = null
var _hud_hint: Label = null
var _banner: Label = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	_build_hud()


func boot(state: Dictionary) -> void:
	_carry_star = bool(state.get("carry_star", false))
	_silk = SILK_MAX * clampf(float(state.get("silk_frac", 0.7)), 0.1, 1.0)
	_leg = 1
	_legs_crossed = 0
	_score = 0.0
	_start_settle()
	_running = true
	_resolved = false
	queue_redraw()


# ─── phases ──────────────────────────────────────────────────────

func _start_settle() -> void:
	_phase = "settle"
	_phase_t = 0.0
	_sy = (BAND_HI + BAND_LO) * 0.5
	_vy = 0.0
	_dist = 0.0
	_debris.clear()


func _cast() -> void:
	if _phase != "settle" or _phase_t < SETTLE_MIN:
		return
	_phase = "fly"
	_phase_t = 0.0
	_vy = -120.0
	_sfx("silk_cast")


func _land_leg() -> void:
	_legs_crossed += 1
	_score += 250.0
	if _leg >= LEGS:
		_resolve("eaves" if _carry_star else "new_tree")
		return
	_leg += 1
	_sfx("thread_spin")
	_start_settle()


# ─── main loop ───────────────────────────────────────────────────

func _physics_process(delta: float) -> void:
	if not _running:
		return
	_t += delta
	_gust = 0.5 + 0.5 * sin(_t * TAU / GUST_PERIOD)

	if _phase == "settle":
		_silk = minf(SILK_MAX, _silk + SETTLE_REFILL * delta)
		if Input.is_action_pressed("ui_accept") and _phase_t >= SETTLE_MIN:
			_cast()
		_phase_t += delta
	else:
		_fly_step(delta)

	_update_hud()
	queue_redraw()


func _fly_step(delta: float) -> void:
	_phase_t += delta
	# ── vertical ──
	_vy += GRAVITY * delta
	if Input.is_action_pressed("ui_accept") and _silk > 0.0:
		_vy -= LIFT * delta
		_silk -= LIFT_COST * delta
	if Input.is_action_pressed("ui_up"):
		_vy -= STEER * delta
		_silk -= STEER_COST * delta
	if Input.is_action_pressed("ui_down"):
		_vy += STEER * delta
	_vy *= V_DAMP
	_sy += _vy * delta
	_sy = clampf(_sy, 30.0, VH - 24.0)

	# ── the churn drinks silk ──
	if _sy > CHURN_Y:
		_silk -= CHURN_DRAIN * delta
		_vy += 40.0 * delta      # heavier down in the rain

	# ── forward push, scaled by how well you sit in the wind band ──
	var band: float = _band_factor(_sy)
	var wind: float = WIND_BASE + WIND_GUST * _gust
	_dist += wind * band * delta
	_score += wind * band * delta * SCORE_RATE

	_step_debris(delta)

	_silk = maxf(0.0, _silk)
	if _silk <= 0.0:
		_resolve("still_flying")
		return
	if _dist >= LEG_DIST:
		_land_leg()


func _band_factor(y: float) -> float:
	if y >= BAND_HI and y <= BAND_LO:
		return 1.0
	if y < BAND_HI:
		# too high — stalling out of the wind
		return clampf(0.4 + 0.6 * (y / BAND_HI), 0.3, 1.0)
	# below the band, fading toward the churn
	return clampf(1.0 - (y - BAND_LO) / (CHURN_Y - BAND_LO) * 0.85, 0.15, 1.0)


func _step_debris(delta: float) -> void:
	_debris_timer -= delta
	if _debris_timer <= 0.0:
		_debris_timer = randf_range(0.7, 1.6)
		var dy: float = randf_range(80.0, VH - 120.0)
		_debris.append({"x": VW + 20.0, "y": dy, "vx": -randf_range(260.0, 420.0)})
	var keep: Array = []
	for d_v in _debris:
		var d: Dictionary = d_v
		d["x"] = float(d["x"]) + float(d["vx"]) * delta
		if float(d["x"]) < -30.0:
			continue
		# collision with the spider
		if absf(float(d["x"]) - SPIDER_X) < 13.0 and absf(float(d["y"]) - _sy) < 15.0:
			_vy += 220.0
			_silk = maxf(0.0, _silk - 9.0)
			_sfx("thread_snap")
			continue
		keep.append(d)
	_debris = keep


# ─── resolve ─────────────────────────────────────────────────────

func _resolve(register: String) -> void:
	if _resolved:
		return
	_resolved = true
	_running = false
	run_over.emit({
		"register": register,
		"legs_crossed": _legs_crossed,
		"legs_total": LEGS,
		"score": int(_score),
	})


# ─── HUD ─────────────────────────────────────────────────────────

func _build_hud() -> void:
	var bar := HBoxContainer.new()
	bar.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	bar.offset_top = 12
	bar.offset_left = 18
	bar.offset_right = -18
	bar.add_theme_constant_override("separation", 26)
	add_child(bar)
	_hud_leg = _mk(bar, C_SPIDER)
	_hud_dist = _mk(bar, C_SILK)
	_hud_silk = _mk(bar, C_DROP)

	_hud_hint = Label.new()
	_hud_hint.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	_hud_hint.offset_top = -30
	_hud_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_hud_hint.add_theme_font_size_override("font_size", 12)
	_hud_hint.add_theme_color_override("font_color", Color(C_SILK.r, C_SILK.g, C_SILK.b, 0.65))
	_hud_hint.text = "HOLD accept to lift  ·  ↑↓ steer into the bright band  ·  stay out of the rain"
	add_child(_hud_hint)

	_banner = Label.new()
	_banner.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_banner.offset_top = -20
	_banner.offset_left = -300
	_banner.offset_right = 300
	_banner.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_banner.add_theme_font_size_override("font_size", 22)
	_banner.add_theme_color_override("font_color", C_SPIDER)
	add_child(_banner)


func _mk(parent: Node, col: Color) -> Label:
	var l := Label.new()
	l.add_theme_font_size_override("font_size", 14)
	l.add_theme_color_override("font_color", col)
	parent.add_child(l)
	return l


func _update_hud() -> void:
	if _hud_leg == null:
		return
	_hud_leg.text = "LEG %d / %d" % [_leg, LEGS]
	_hud_dist.text = "%d%%" % int(clampf(_dist / LEG_DIST, 0.0, 1.0) * 100.0)
	_hud_silk.text = "silk %d" % int(_silk)
	if _phase == "settle":
		if _phase_t >= SETTLE_MIN:
			_banner.text = "leg %d · CAST (accept) to catch the wind" % _leg
		else:
			_banner.text = "resting · leg %d of %d" % [_leg, LEGS]
	elif _gust > 0.72:
		_banner.text = "GUST — ride it"
	else:
		_banner.text = ""


# ─── draw ────────────────────────────────────────────────────────

func _draw() -> void:
	# dawn sky
	draw_rect(Rect2(Vector2.ZERO, Vector2(VW, VH)), C_SKY)
	draw_rect(Rect2(Vector2(0.0, VH * 0.5), Vector2(VW, VH * 0.5)), C_SKY2)
	# the wind band — brighter where the gust is stronger
	var band_a: float = 0.10 + 0.16 * _gust
	draw_rect(Rect2(Vector2(0.0, BAND_HI), Vector2(VW, BAND_LO - BAND_HI)),
		Color(C_BAND.r, C_BAND.g, C_BAND.b, band_a))
	# the churn
	draw_rect(Rect2(Vector2(0.0, CHURN_Y), Vector2(VW, VH - CHURN_Y)), C_CHURN)
	_draw_rain()
	_draw_debris()
	if _phase == "fly":
		_draw_progress_branch()
	_draw_spider()


func _draw_rain() -> void:
	var slant: Vector2 = Vector2(0.5 + _gust * 0.5, 1.0).normalized()
	var speed: float = 500.0 + 300.0 * _gust
	var col: Color = Color(C_DROP.r, C_DROP.g, C_DROP.b, 0.22)
	for i in range(90):
		var px: float = float((i * 137) % int(VW))
		var base_y: float = float((i * 83) % int(VH))
		var y: float = fmod(base_y + _t * speed, VH)
		var p: Vector2 = Vector2(fmod(px + _t * 80.0, VW), y)
		draw_line(p, p + slant * 12.0, col, 1.0)


func _draw_debris() -> void:
	for d_v in _debris:
		var d: Dictionary = d_v
		draw_rect(Rect2(Vector2(float(d["x"]) - 4.0, float(d["y"]) - 3.0), Vector2(8.0, 6.0)), C_DEBRIS)


func _draw_progress_branch() -> void:
	# the far branch slides in from the right as the leg nears its end
	var p: float = clampf(_dist / LEG_DIST, 0.0, 1.0)
	if p < 0.72:
		return
	var slide: float = (1.0 - (p - 0.72) / 0.28)
	var bx: float = VW - 60.0 + slide * 220.0
	draw_line(Vector2(bx, (BAND_HI + BAND_LO) * 0.5), Vector2(VW + 60.0, (BAND_HI + BAND_LO) * 0.5 - 30.0), C_BRANCH, 8.0)
	draw_circle(Vector2(bx, (BAND_HI + BAND_LO) * 0.5), 5.0, C_BRANCH)


func _draw_spider() -> void:
	var p: Vector2 = Vector2(SPIDER_X, _sy)
	# the ballooning silk streamer, up into the wind
	if _phase == "fly":
		var prev: Vector2 = p
		for k in range(1, 9):
			var t: float = float(k)
			var sp: Vector2 = Vector2(
				p.x - t * 9.0 + sin(_t * 6.0 + t) * 4.0,
				p.y - t * 11.0)
			draw_line(prev, sp, Color(C_SILK.r, C_SILK.g, C_SILK.b, 0.5), 1.0)
			prev = sp
	# eight legs
	for li in range(8):
		var a: float = TAU * float(li) / 8.0
		var knee: Vector2 = p + Vector2(cos(a), sin(a)) * 7.0 + Vector2(0.0, -2.0)
		var foot: Vector2 = p + Vector2(cos(a), sin(a)) * 12.0
		draw_line(p, knee, C_SPIDER_DK, 1.6)
		draw_line(knee, foot, C_SPIDER_DK, 1.6)
	draw_circle(p + Vector2(0.0, 3.0), 6.0, C_SPIDER)
	draw_circle(p, 4.0, C_SPIDER_DK)
	if _carry_star:
		# the keepsake, a small eight-point glint on the abdomen
		draw_circle(p + Vector2(0.0, 3.0), 2.0, C_STAR)


# ─── input ───────────────────────────────────────────────────────

func _input(event: InputEvent) -> void:
	if not _running:
		return
	if event.is_action_pressed("ui_cancel"):
		_running = false
		quit.emit()
		get_viewport().set_input_as_handled()


func _sfx(preset: String) -> void:
	var sb := get_node_or_null("/root/SFXBank")
	if sb != null and sb.has_method("play"):
		sb.play(preset)
