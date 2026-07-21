extends Control
class_name SpiderdropsWeb
## SPIDERDROPS · the storm · the one live renderer this stick earns.
##
## A Verlet particle web: a hub, eight radial SPOKES, four concentric
## rings, the outer ring pinned as ANCHORS on the storm frame. Rain
## pools into mass, debris blows in on the gusts, threads snap under
## tension. The player is the SPIDER on a node, crawling the web to
## PLUCK water, BRACE nodes against the telegraphed gust, and re-SPIN
## what snaps.
##
## The storm arrives in six escalating GUSTS ("gusts are waves"), each
## telegraphed: a lull, an arrow, then the hit from that direction. The
## run resolves by the SHAPE the web is in when it goes — and the storm
## always, eventually, wins.
##
## Emits (host contract): quit · run_over(result: Dictionary)
## F4-compliant via add_to_group("ui").

signal quit
signal run_over(result: Dictionary)

# ── design-space geometry (canvas_items stretch scales it to the Deck)
const VW := 1280.0
const VH := 720.0
const CENTER := Vector2(640.0, 360.0)

# ── web shape
const SPOKES := 8
const RINGS := 4                      # ring 0 inner .. 3 outer (anchors)
const RING_R := [96.0, 178.0, 262.0, 344.0]

# ── physics
const GRAVITY := 760.0
const DAMP := 0.985
const ITER := 5
const BREAK_RATIO := 1.85             # spiral snaps past rest * this
const SPOKE_TOUGH := 0.55             # spokes get + this tolerance
const BRACE_STIFFEN := 0.85           # braced node's threads get + this
const WATER_MASS := 2.3
const DEBRIS_MASS := 1.4
const DEBRIS_DRAG := 0.9
const SPIDER_MASS := 1.6

# ── water / debris
const WATER_MAX := 3.0
const DROP_ADD := 0.28
const RAIN_BASE := 5.0                # drops/sec at wave 1
const RAIN_PER_WAVE := 2.2
const DEBRIS_MAX := 3.0

# ── storm waves
const WAVE_COUNT := 6
const TELEGRAPH_T := 2.6
const LULL_T := 3.2
const GUST_DIRS := [
	Vector2(1.0, -0.15), Vector2(-1.0, -0.10), Vector2(0.7, 0.25),
	Vector2(-0.8, 0.2), Vector2(1.0, 0.1), Vector2(-1.0, -0.25),
]

# ── resources
const SILK_MAX := 100.0
const SILK_REGEN := 7.0
const SPIN_COST := 22.0
const STAM_MAX := 100.0
const BRACE_DRAIN := 26.0
const STAM_REGEN := 14.0

# ── verb feel
const MOVE_CD := 0.11
const PLUCK_CD := 0.5
const SPIN_CD := 0.35
const PLUCK_SHED := 0.25              # water kept after a pluck
const PLUCK_KICK := 6.0
const SPIN_RANGE := 200.0
const SCORE_RATE := 1.6

# ── palette (PDP toy-bright, storm register)
const C_SKY := Color("2b3a52")
const C_SKY2 := Color("3a4d6b")
const C_BRANCH := Color("241c18")
const C_SILK := Color("e8ecef")
const C_SPIRAL := Color("b9c4cf")
const C_DROP := Color("6fb7e0")
const C_DEBRIS := Color("6b5535")
const C_SPIDER := Color("f2c14e")
const C_SPIDER_DK := Color("9c7a24")
const C_WARN := Color("ff7a5c")
const C_ARROW := Color("f2c14e")

var _nodes: Array = []                # {pos,prev,pin,water,debris,alive,hub,spoke,ring}
var _threads: Array = []              # {a,b,rest,alive,kind}
var _thread_lookup: Dictionary = {}   # "min_max" -> thread index
var _spider: int = 0
var _initial_spiral: int = 0

var _t: float = 0.0
var _running: bool = false
var _resolved: bool = false

var _wave: int = 0
var _phase: String = "lull"           # telegraph | gust | lull
var _phase_t: float = 0.0
var _gust_dir: Vector2 = Vector2.RIGHT
var _gust_strength: float = 0.0
var _wind: Vector2 = Vector2.ZERO
var _waves_survived: int = 0
var _storm_done: bool = false

var _silk: float = SILK_MAX
var _stamina: float = STAM_MAX
var _bracing: bool = false
var _brace_node: int = -1

var _move_cd: float = 0.0
var _pluck_cd: float = 0.0
var _spin_cd: float = 0.0
var _rain_accum: float = 0.0
var _score: float = 0.0

# HUD
var _hud_wave: Label = null
var _hud_silk: Label = null
var _hud_stam: Label = null
var _hud_web: Label = null
var _hud_hint: Label = null
var _telegraph: Label = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	_build_hud()


func boot(_state: Dictionary) -> void:
	_build_web()
	_spider = 0
	_running = true
	_resolved = false
	_wave = 1
	_waves_survived = 0
	_storm_done = false
	_silk = SILK_MAX
	_stamina = STAM_MAX
	_begin_wave(1)
	queue_redraw()


# ─── Web construction ────────────────────────────────────────────

func _nidx(s: int, r: int) -> int:
	return 1 + s * RINGS + r


func _build_web() -> void:
	_nodes.clear()
	_threads.clear()
	_thread_lookup.clear()

	# hub
	_nodes.append({
		"pos": CENTER, "prev": CENTER, "pin": false,
		"water": 0.0, "debris": 0.0, "alive": true,
		"hub": true, "spoke": -1, "ring": -1,
	})

	for s in range(SPOKES):
		var ang: float = TAU * float(s) / float(SPOKES) - PI / 2.0
		var dir: Vector2 = Vector2(cos(ang), sin(ang))
		for r in range(RINGS):
			var p: Vector2 = CENTER + dir * RING_R[r]
			var is_anchor: bool = (r == RINGS - 1)
			_nodes.append({
				"pos": p, "prev": p, "pin": is_anchor,
				"water": 0.0, "debris": 0.0, "alive": true,
				"hub": false, "spoke": s, "ring": r,
			})

	# spoke threads: hub -> r0, then r -> r+1 out to the anchor
	for s in range(SPOKES):
		_add_thread(0, _nidx(s, 0), "spoke")
		for r in range(RINGS - 1):
			_add_thread(_nidx(s, r), _nidx(s, r + 1), "spoke")

	# spiral threads: around each ring, s -> s+1
	for r in range(RINGS):
		for s in range(SPOKES):
			_add_thread(_nidx(s, r), _nidx((s + 1) % SPOKES, r), "spiral")

	_initial_spiral = 0
	for t_v in _threads:
		var t: Dictionary = t_v
		if String(t["kind"]) == "spiral":
			_initial_spiral += 1


func _add_thread(a: int, b: int, kind: String) -> void:
	var pa: Vector2 = _nodes[a]["pos"]
	var pb: Vector2 = _nodes[b]["pos"]
	var idx: int = _threads.size()
	_threads.append({
		"a": a, "b": b, "rest": pa.distance_to(pb),
		"alive": true, "kind": kind,
	})
	_thread_lookup[_key(a, b)] = idx


func _key(a: int, b: int) -> String:
	return "%d_%d" % [mini(a, b), maxi(a, b)]


# ─── Storm ───────────────────────────────────────────────────────

func _begin_wave(w: int) -> void:
	_phase = "telegraph"
	_phase_t = 0.0
	var base: Vector2 = GUST_DIRS[(w - 1) % GUST_DIRS.size()]
	_gust_dir = base.normalized().rotated(randf_range(-0.14, 0.14))
	_gust_strength = 400.0 + 120.0 * float(w)


func _gust_len(w: int) -> float:
	return 2.0 + 0.5 * float(w)


func _update_storm(delta: float) -> void:
	_phase_t += delta
	match _phase:
		"telegraph":
			var k: float = clampf(_phase_t / TELEGRAPH_T, 0.0, 1.0)
			_wind = _gust_dir * (_gust_strength * 0.12 * k)
			if _phase_t >= TELEGRAPH_T:
				_phase = "gust"
				_phase_t = 0.0
				_sfx("wind_gust")
		"gust":
			var flutter: float = 1.0 + sin(_t * 9.0) * 0.12
			_wind = _gust_dir * (_gust_strength * flutter)
			if _phase_t >= _gust_len(_wave):
				_phase = "lull"
				_phase_t = 0.0
		"lull":
			_wind = _wind.lerp(Vector2.ZERO, clampf(delta * 3.0, 0.0, 1.0))
			if _phase_t >= LULL_T:
				_waves_survived = _wave
				if _wave >= WAVE_COUNT:
					_storm_done = true
				else:
					_wave += 1
					_begin_wave(_wave)


func _accumulate_rain(delta: float) -> void:
	var rate: float = RAIN_BASE + RAIN_PER_WAVE * float(_wave)
	_rain_accum += rate * delta
	while _rain_accum >= 1.0:
		_rain_accum -= 1.0
		var i: int = _rain_target()
		if i >= 0:
			var n: Dictionary = _nodes[i]
			n["water"] = minf(float(n["water"]) + DROP_ADD, WATER_MAX)
	# debris on the gust
	if _phase == "gust" and randf() < 4.0 * delta:
		var j: int = _rain_target()
		if j >= 0:
			var m: Dictionary = _nodes[j]
			m["debris"] = minf(float(m["debris"]) + 1.0, DEBRIS_MAX)


func _rain_target() -> int:
	# a random alive, non-anchor interior node
	for _attempt in range(6):
		var i: int = randi_range(0, _nodes.size() - 1)
		var n: Dictionary = _nodes[i]
		if bool(n["alive"]) and not bool(n["pin"]):
			return i
	return -1


# ─── Verlet ──────────────────────────────────────────────────────

func _mass(i: int) -> float:
	var n: Dictionary = _nodes[i]
	var m: float = 1.0 + float(n["water"]) * WATER_MASS + float(n["debris"]) * DEBRIS_MASS
	if i == _spider:
		m += SPIDER_MASS
	return m


func _inv_mass(i: int) -> float:
	var n: Dictionary = _nodes[i]
	if not bool(n["alive"]) or bool(n["pin"]):
		return 0.0
	if _bracing and i == _brace_node:
		return 0.0
	return 1.0 / _mass(i)


func _integrate(delta: float) -> void:
	var g: Vector2 = Vector2(0.0, GRAVITY)
	for i in range(_nodes.size()):
		var n: Dictionary = _nodes[i]
		if not bool(n["alive"]) or bool(n["pin"]):
			continue
		if _bracing and i == _brace_node:
			continue
		var pos: Vector2 = n["pos"]
		var prev: Vector2 = n["prev"]
		var accel: Vector2 = g + _wind * (1.0 + float(n["debris"]) * DEBRIS_DRAG) / _mass(i)
		var vel: Vector2 = (pos - prev) * DAMP
		n["prev"] = pos
		n["pos"] = pos + vel + accel * delta * delta


func _solve_constraints() -> void:
	for t_v in _threads:
		var t: Dictionary = t_v
		if not bool(t["alive"]):
			continue
		var ia: int = t["a"]
		var ib: int = t["b"]
		var na: Dictionary = _nodes[ia]
		var nb: Dictionary = _nodes[ib]
		if not bool(na["alive"]) or not bool(nb["alive"]):
			continue
		var pa: Vector2 = na["pos"]
		var pb: Vector2 = nb["pos"]
		var d: Vector2 = pb - pa
		var dist: float = d.length()
		if dist < 0.001 or dist <= float(t["rest"]):
			continue   # silk pulls in tension only, never pushes
		var diff: float = (dist - float(t["rest"])) / dist
		var wa: float = _inv_mass(ia)
		var wb: float = _inv_mass(ib)
		var wsum: float = wa + wb
		if wsum <= 0.0:
			continue
		var corr: Vector2 = d * diff
		na["pos"] = pa + corr * (wa / wsum)
		nb["pos"] = pb - corr * (wb / wsum)


func _snap_and_cull() -> void:
	for t_v in _threads:
		var t: Dictionary = t_v
		if not bool(t["alive"]):
			continue
		var ia: int = t["a"]
		var ib: int = t["b"]
		var na: Dictionary = _nodes[ia]
		var nb: Dictionary = _nodes[ib]
		if not bool(na["alive"]) or not bool(nb["alive"]):
			t["alive"] = false
			continue
		var dist: float = (Vector2(nb["pos"]) - Vector2(na["pos"])).length()
		var tol: float = BREAK_RATIO
		if String(t["kind"]) == "spoke":
			tol += SPOKE_TOUGH
		if _bracing and (ia == _brace_node or ib == _brace_node):
			tol += BRACE_STIFFEN
		if dist > float(t["rest"]) * tol:
			t["alive"] = false
			_sfx("thread_snap")
	# cull interior nodes that have lost every thread (they fall away)
	for i in range(1, _nodes.size()):
		var n: Dictionary = _nodes[i]
		if not bool(n["alive"]) or bool(n["pin"]):
			continue
		if not _has_alive_thread(i):
			n["alive"] = false
	# hub orphaned = web collapse
	if not _has_alive_thread(0):
		_nodes[0]["alive"] = false


func _has_alive_thread(i: int) -> bool:
	for t_v in _threads:
		var t: Dictionary = t_v
		if not bool(t["alive"]):
			continue
		if int(t["a"]) != i and int(t["b"]) != i:
			continue
		var other: int = int(t["b"]) if int(t["a"]) == i else int(t["a"])
		if bool(_nodes[other]["alive"]):
			return true
	return false


# ─── Spider ──────────────────────────────────────────────────────

func _spider_physics(_delta: float) -> void:
	if not bool(_nodes[_spider]["alive"]):
		if bool(_nodes[0]["alive"]):
			_spider = 0
		# else: hub is gone too; resolve() will catch the loss


func _try_move(dir: Vector2) -> void:
	var want: Vector2 = dir.normalized()
	var best: int = -1
	var best_dot: float = 0.25
	var sp: Vector2 = _nodes[_spider]["pos"]
	for t_v in _threads:
		var t: Dictionary = t_v
		if not bool(t["alive"]):
			continue
		var ia: int = int(t["a"])
		var ib: int = int(t["b"])
		var other: int = -1
		if ia == _spider:
			other = ib
		elif ib == _spider:
			other = ia
		else:
			continue
		if not bool(_nodes[other]["alive"]):
			continue
		var to: Vector2 = (Vector2(_nodes[other]["pos"]) - sp).normalized()
		var dot: float = to.dot(want)
		if dot > best_dot:
			best_dot = dot
			best = other
	if best >= 0:
		_spider = best
		_sfx("spider_step")


func _do_pluck() -> void:
	_shed_node(_spider)
	for t_v in _threads:
		var t: Dictionary = t_v
		if not bool(t["alive"]):
			continue
		var other: int = -1
		if int(t["a"]) == _spider:
			other = int(t["b"])
		elif int(t["b"]) == _spider:
			other = int(t["a"])
		else:
			continue
		if bool(_nodes[other]["alive"]):
			_shed_node(other)
	_sfx("thread_pluck")


func _shed_node(i: int) -> void:
	var n: Dictionary = _nodes[i]
	n["water"] = float(n["water"]) * PLUCK_SHED
	if randf() < 0.6:
		n["debris"] = 0.0
	# a little upward snap (move prev down => velocity up)
	if not bool(n["pin"]):
		var prev: Vector2 = n["prev"]
		n["prev"] = Vector2(prev.x, prev.y + PLUCK_KICK)


func _do_spin() -> bool:
	# revive one snapped thread incident to the spider whose OTHER end
	# is still alive (a strand that popped but still hangs by its nodes)
	for t_v in _threads:
		var t: Dictionary = t_v
		if bool(t["alive"]):
			continue
		var ia: int = int(t["a"])
		var ib: int = int(t["b"])
		if ia != _spider and ib != _spider:
			continue
		var other: int = ib if ia == _spider else ia
		if not bool(_nodes[ia]["alive"]) or not bool(_nodes[ib]["alive"]):
			continue
		if not bool(_nodes[other]["alive"]):
			continue
		t["alive"] = true
		# reset both ends' velocity so the fresh strand does not re-snap
		_nodes[ia]["prev"] = _nodes[ia]["pos"]
		_nodes[ib]["prev"] = _nodes[ib]["pos"]
		_sfx("thread_spin")
		return true
	return false


# ─── Main loop ───────────────────────────────────────────────────

func _physics_process(delta: float) -> void:
	if not _running:
		return
	_t += delta
	_move_cd = maxf(0.0, _move_cd - delta)
	_pluck_cd = maxf(0.0, _pluck_cd - delta)
	_spin_cd = maxf(0.0, _spin_cd - delta)

	_read_held_input(delta)
	_update_storm(delta)
	_accumulate_rain(delta)

	_integrate(delta)
	for _i in range(ITER):
		_solve_constraints()
	_snap_and_cull()
	_spider_physics(delta)

	# resources
	var regen_mul: float = 2.0 if _phase == "lull" else 1.0
	_silk = minf(SILK_MAX, _silk + SILK_REGEN * regen_mul * delta)
	if not _bracing:
		_stamina = minf(STAM_MAX, _stamina + STAM_REGEN * regen_mul * delta)

	# score for every strand you keep up, every second
	_score += SCORE_RATE * float(_alive_spiral() + _spokes_intact() * 3) * delta

	_update_hud()
	queue_redraw()

	if not _resolved:
		if not bool(_nodes[0]["alive"]) or _spokes_intact() <= 2:
			_resolve()
		elif _storm_done:
			_resolve()


func _read_held_input(delta: float) -> void:
	# movement (discrete hops along threads)
	if _move_cd <= 0.0:
		var dir: Vector2 = Vector2.ZERO
		if Input.is_action_pressed("ui_right"): dir.x += 1.0
		if Input.is_action_pressed("ui_left"): dir.x -= 1.0
		if Input.is_action_pressed("ui_down"): dir.y += 1.0
		if Input.is_action_pressed("ui_up"): dir.y -= 1.0
		if dir != Vector2.ZERO:
			_try_move(dir)
			_move_cd = MOVE_CD
	# brace (hold) — the DEFEND analog; pins the current node + stiffens
	var want_brace: bool = Input.is_key_pressed(KEY_SHIFT) and _stamina > 0.0
	_bracing = want_brace
	_brace_node = _spider if _bracing else -1
	if _bracing:
		_stamina = maxf(0.0, _stamina - BRACE_DRAIN * delta)


# ─── Resolve ─────────────────────────────────────────────────────

func _alive_spiral() -> int:
	var c: int = 0
	for t_v in _threads:
		var t: Dictionary = t_v
		if bool(t["alive"]) and String(t["kind"]) == "spiral":
			c += 1
	return c


func _thread_alive_between(a: int, b: int) -> bool:
	var idx: int = int(_thread_lookup.get(_key(a, b), -1))
	if idx < 0:
		return false
	return bool(_threads[idx]["alive"])


func _spoke_chain_alive(s: int) -> bool:
	if not _thread_alive_between(0, _nidx(s, 0)):
		return false
	for r in range(RINGS - 1):
		if not _thread_alive_between(_nidx(s, r), _nidx(s, r + 1)):
			return false
	return true


func _spokes_intact() -> int:
	var c: int = 0
	for s in range(SPOKES):
		if _spoke_chain_alive(s):
			c += 1
	return c


func _resolve() -> void:
	_resolved = true
	_running = false
	var spokes: int = _spokes_intact()
	var frac: float = float(_alive_spiral()) / float(maxi(1, _initial_spiral))
	var reg: String = "storm"
	if not bool(_nodes[0]["alive"]) or spokes <= 2:
		reg = "storm"
	elif spokes >= 7 and frac <= 0.20:
		reg = "star"
	elif spokes >= 7 and frac >= 0.60:
		reg = "whole"
	else:
		reg = "held"
	run_over.emit({
		"register": reg,
		"waves_survived": _waves_survived,
		"spokes_alive": spokes,
		"spiral_frac": frac,
		"score": int(_score),
	})


# ─── HUD ─────────────────────────────────────────────────────────

func _build_hud() -> void:
	var bar := HBoxContainer.new()
	bar.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	bar.offset_top = -40
	bar.offset_left = 18
	bar.offset_right = -18
	bar.add_theme_constant_override("separation", 26)
	add_child(bar)

	_hud_wave = _mk_label(bar, C_ARROW)
	_hud_web = _mk_label(bar, C_SILK)
	_hud_silk = _mk_label(bar, C_SILK)
	_hud_stam = _mk_label(bar, C_DROP)

	_hud_hint = Label.new()
	_hud_hint.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	_hud_hint.offset_top = -62
	_hud_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_hud_hint.add_theme_font_size_override("font_size", 12)
	_hud_hint.add_theme_color_override("font_color", Color(C_SILK.r, C_SILK.g, C_SILK.b, 0.6))
	_hud_hint.text = "MOVE arrows  ·  PLUCK space  ·  BRACE hold shift  ·  SPIN s"
	add_child(_hud_hint)

	_telegraph = Label.new()
	_telegraph.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	_telegraph.offset_top = 44
	_telegraph.offset_left = -300
	_telegraph.offset_right = 300
	_telegraph.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_telegraph.add_theme_font_size_override("font_size", 22)
	_telegraph.add_theme_color_override("font_color", C_ARROW)
	_telegraph.visible = false
	add_child(_telegraph)


func _mk_label(parent: Node, col: Color) -> Label:
	var l := Label.new()
	l.add_theme_font_size_override("font_size", 14)
	l.add_theme_color_override("font_color", col)
	parent.add_child(l)
	return l


func _update_hud() -> void:
	if _hud_wave == null:
		return
	_hud_wave.text = "GUST %d / %d" % [_wave, WAVE_COUNT]
	_hud_web.text = "web %d/8 · %d%%" % [_spokes_intact(), int(round(float(_alive_spiral()) / float(maxi(1, _initial_spiral)) * 100.0))]
	_hud_silk.text = "silk %d" % int(_silk)
	_hud_stam.text = "brace %d" % int(_stamina)
	if _phase == "telegraph":
		var arrow: String = _dir_arrow(_gust_dir)
		_telegraph.text = "GUST %d INCOMING  %s" % [_wave, arrow]
		_telegraph.visible = true
	else:
		_telegraph.visible = false


func _dir_arrow(v: Vector2) -> String:
	if absf(v.x) >= absf(v.y):
		return "→→→" if v.x >= 0.0 else "←←←"
	return "↓↓↓" if v.y >= 0.0 else "↑↑↑"


# ─── Draw ────────────────────────────────────────────────────────

func _draw() -> void:
	var vp: Vector2 = Vector2(VW, VH)
	# storm sky
	draw_rect(Rect2(Vector2.ZERO, vp), C_SKY)
	draw_rect(Rect2(Vector2(0.0, VH * 0.5), Vector2(VW, VH * 0.5)), C_SKY2)
	_draw_rain(vp)
	_draw_branches()
	_draw_threads()
	_draw_nodes()
	_draw_spider()
	if _phase == "telegraph":
		_draw_gust_arrow()


func _draw_rain(vp: Vector2) -> void:
	var slant: Vector2 = Vector2(_wind.x * 0.02, 1.0).normalized()
	var speed: float = 620.0 + float(_wave) * 40.0
	var col: Color = Color(C_DROP.r, C_DROP.g, C_DROP.b, 0.30)
	for i in range(110):
		var px: float = float((i * 137) % int(vp.x))
		var base_y: float = float((i * 89) % int(vp.y))
		var y: float = fmod(base_y + _t * speed, vp.y)
		var p: Vector2 = Vector2(px + slant.x * 46.0 * (y / vp.y), y)
		draw_line(p, p + slant * 14.0, col, 1.0)


func _draw_branches() -> void:
	# a suggestion of the frame the anchors hang from
	for s in range(SPOKES):
		var a: int = _nidx(s, RINGS - 1)
		var ap: Vector2 = _nodes[a]["pos"]
		var out: Vector2 = (ap - CENTER).normalized()
		draw_line(ap, ap + out * 120.0, C_BRANCH, 6.0)
		draw_circle(ap, 5.0, C_BRANCH)


func _draw_threads() -> void:
	for t_v in _threads:
		var t: Dictionary = t_v
		if not bool(t["alive"]):
			continue
		var na: Dictionary = _nodes[int(t["a"])]
		var nb: Dictionary = _nodes[int(t["b"])]
		if not bool(na["alive"]) or not bool(nb["alive"]):
			continue
		var pa: Vector2 = na["pos"]
		var pb: Vector2 = nb["pos"]
		var dist: float = pa.distance_to(pb)
		var strain: float = dist / maxf(1.0, float(t["rest"]))
		var is_spoke: bool = String(t["kind"]) == "spoke"
		var base: Color = C_SILK if is_spoke else C_SPIRAL
		# water on the two nodes tints the strand bluer + heavier
		var wet: float = clampf((float(na["water"]) + float(nb["water"])) / (WATER_MAX * 2.0), 0.0, 1.0)
		var col: Color = base.lerp(C_DROP, wet * 0.7)
		if strain > 1.4:
			col = col.lerp(C_WARN, clampf((strain - 1.4) / 0.6, 0.0, 1.0))
		var w: float = (2.4 if is_spoke else 1.4) + wet * 1.6
		draw_line(pa, pb, col, w)


func _draw_nodes() -> void:
	for i in range(_nodes.size()):
		var n: Dictionary = _nodes[i]
		if not bool(n["alive"]):
			continue
		var p: Vector2 = n["pos"]
		var water: float = float(n["water"])
		if water > 0.05:
			var rad: float = 2.0 + water * 3.2
			draw_circle(p + Vector2(0.0, rad * 0.5), rad, C_DROP)
			draw_circle(p + Vector2(-rad * 0.3, rad * 0.2), rad * 0.35, Color(1, 1, 1, 0.5))
		if float(n["debris"]) > 0.05:
			draw_rect(Rect2(p - Vector2(3.0, 2.0), Vector2(6.0, 4.0)), C_DEBRIS)


func _draw_spider() -> void:
	if not bool(_nodes[_spider]["alive"]):
		return
	var p: Vector2 = _nodes[_spider]["pos"]
	if _bracing:
		draw_arc(p, 15.0, 0.0, TAU, 20, Color(C_SPIDER.r, C_SPIDER.g, C_SPIDER.b, 0.5), 2.0)
	# eight legs, reaching toward connected neighbors where possible
	var reached: Array = []
	for t_v in _threads:
		var t: Dictionary = t_v
		if not bool(t["alive"]):
			continue
		var other: int = -1
		if int(t["a"]) == _spider:
			other = int(t["b"])
		elif int(t["b"]) == _spider:
			other = int(t["a"])
		else:
			continue
		if bool(_nodes[other]["alive"]):
			var d: Vector2 = (Vector2(_nodes[other]["pos"]) - p).normalized()
			reached.append(d)
	for li in range(8):
		var dir: Vector2
		if li < reached.size():
			dir = reached[li]
		else:
			var a: float = TAU * float(li) / 8.0
			dir = Vector2(cos(a), sin(a))
		var knee: Vector2 = p + dir * 7.0 + Vector2(0.0, -3.0)
		var foot: Vector2 = p + dir * 13.0
		draw_line(p, knee, C_SPIDER_DK, 1.6)
		draw_line(knee, foot, C_SPIDER_DK, 1.6)
	draw_circle(p + Vector2(0.0, 3.0), 6.0, C_SPIDER)      # abdomen
	draw_circle(p, 4.0, C_SPIDER_DK)                        # cephalothorax


func _draw_gust_arrow() -> void:
	var c: Vector2 = CENTER + Vector2(0.0, -230.0)
	var d: Vector2 = _gust_dir.normalized()
	var tail: Vector2 = c - d * 70.0
	var head: Vector2 = c + d * 70.0
	var perp: Vector2 = Vector2(-d.y, d.x)
	var pulse: float = 0.5 + 0.5 * sin(_t * 6.0)
	var col: Color = Color(C_ARROW.r, C_ARROW.g, C_ARROW.b, 0.4 + 0.4 * pulse)
	draw_line(tail, head, col, 5.0)
	draw_line(head, head - d * 22.0 + perp * 14.0, col, 5.0)
	draw_line(head, head - d * 22.0 - perp * 14.0, col, 5.0)


# ─── Input (discrete verbs) ──────────────────────────────────────

func _input(event: InputEvent) -> void:
	if not _running:
		return
	if event.is_action_pressed("ui_cancel"):
		_running = false
		quit.emit()
		get_viewport().set_input_as_handled()
		return
	if event.is_action_pressed("ui_accept"):
		if _pluck_cd <= 0.0:
			_do_pluck()
			_pluck_cd = PLUCK_CD
		get_viewport().set_input_as_handled()
		return
	if event is InputEventKey and event.pressed and not event.echo:
		var kev: InputEventKey = event
		if kev.keycode == KEY_S:
			if _spin_cd <= 0.0 and _silk >= SPIN_COST:
				if _do_spin():
					_silk -= SPIN_COST
				_spin_cd = SPIN_CD
			get_viewport().set_input_as_handled()


func _sfx(preset: String) -> void:
	var sb := get_node_or_null("/root/SFXBank")
	if sb != null and sb.has_method("play"):
		sb.play(preset)
