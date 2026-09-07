# SpiderdropsMinterFX.gd — score as SPECTACLE (game grammar row 4 · 2026-09-07)
# ════════════════════════════════════════════════════════════════
# The bible's slowstick register is Jeff Minter, "only using current
# hardware" — and the Deck said the neon OVERLAY on a 2D game was
# "ugly and strobey". So the Minter look lives INSIDE the stick: this
# node draws additive light on top of the Spiderdrops web, fed by the
# game's own events.
#
#   burst(pos, col, n, speed)   a drop lands / a thread snaps → a ring
#                               of sparks, additive, drag, no gravity
#   mote(from, col)             every ten points → one mote of light
#                               rises from the hub toward the HUD bar
#                               ("every point is a particle")
#
# Additive blend via CanvasItemMaterial (current hardware, nothing
# faked). Sparks brighten a little with TripSync's beat pulse so the
# storm's light keeps the music's time. Hard cap of MAX_LIVE so the
# Deck never pays for a hundred snaps at once. Nothing here moves the
# frame; nothing strobes — every spark fades, none flashes.
# ════════════════════════════════════════════════════════════════
extends Node2D

const MAX_LIVE: int = 420
const SPARK_LIFE: float = 0.62
const MOTE_LIFE: float = 1.05
const DRAG: float = 3.4

var _sparks: Array[Dictionary] = []   # {pos, vel, t, life, col, size}
var _motes: Array[Dictionary] = []    # {pos, target, t, col}
var _hud_target: Vector2 = Vector2(640.0, 18.0)
var _trip: Node = null


func _ready() -> void:
	var mat: CanvasItemMaterial = CanvasItemMaterial.new()
	mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	material = mat
	z_index = 2
	_trip = get_node_or_null("/root/TripSync")
	set_process(true)


func set_hud_target(p: Vector2) -> void:
	_hud_target = p


func burst(pos: Vector2, col: Color, n: int = 12, speed: float = 110.0, core: bool = false) -> void:
	var budget: int = MAX_LIVE - _sparks.size()
	if budget <= 0:
		return
	n = mini(n, budget)
	for i in range(n):
		var a: float = randf() * TAU
		var sp: float = speed * randf_range(0.55, 1.15)
		# toy-bright: each spark a touch off the base hue
		var c: Color = col
		c.h = fposmod(c.h + randf_range(-0.06, 0.06), 1.0)
		c.s = minf(1.0, c.s * 1.1)
		if core and i < n / 4:
			c = Color(1.0, 1.0, 1.0)
		_sparks.append({
			"pos": pos, "vel": Vector2(cos(a), sin(a)) * sp,
			"t": 0.0, "life": SPARK_LIFE * randf_range(0.7, 1.3),
			"col": c, "size": randf_range(1.6, 3.0),
		})


func mote(from: Vector2, col: Color) -> void:
	if _motes.size() > 60:
		return
	_motes.append({"pos": from + Vector2(randf_range(-6.0, 6.0), randf_range(-4.0, 4.0)),
		"target": _hud_target + Vector2(randf_range(-40.0, 40.0), 0.0), "t": 0.0, "col": col})


func _process(delta: float) -> void:
	var i: int = _sparks.size() - 1
	while i >= 0:
		var s: Dictionary = _sparks[i]
		var t: float = float(s["t"]) + delta
		if t >= float(s["life"]):
			_sparks.remove_at(i)
		else:
			s["t"] = t
			var v: Vector2 = s["vel"]
			v *= maxf(0.0, 1.0 - DRAG * delta)
			s["vel"] = v
			s["pos"] = (s["pos"] as Vector2) + v * delta
		i -= 1
	i = _motes.size() - 1
	while i >= 0:
		var m: Dictionary = _motes[i]
		var t2: float = float(m["t"]) + delta
		if t2 >= MOTE_LIFE:
			_motes.remove_at(i)
		else:
			m["t"] = t2
		i -= 1
	if not _sparks.is_empty() or not _motes.is_empty():
		queue_redraw()


func _draw() -> void:
	var lift: float = 0.0
	if _trip != null:
		lift = 0.25 * float(_trip.get("pulse"))
	for s_v in _sparks:
		var s: Dictionary = s_v
		var k: float = float(s["t"]) / float(s["life"])
		var a: float = (1.0 - k) * (1.0 - k) * (0.85 + lift)
		var c: Color = s["col"]
		c.a = a
		var pos: Vector2 = s["pos"]
		var vel: Vector2 = s["vel"]
		var size: float = float(s["size"]) * (1.0 - k * 0.6)
		draw_circle(pos, size, c)
		# a short tail along the velocity — the light synth's streak
		if vel.length() > 20.0:
			draw_line(pos, pos - vel * 0.035, Color(c.r, c.g, c.b, a * 0.5), maxf(1.0, size * 0.7))
	for m_v in _motes:
		var m: Dictionary = m_v
		var k2: float = float(m["t"]) / MOTE_LIFE
		var e: float = 1.0 - (1.0 - k2) * (1.0 - k2)     # ease out toward the bar
		var from: Vector2 = m["pos"]
		var to: Vector2 = m["target"]
		var p: Vector2 = from.lerp(to, e)
		p.x += sin(k2 * 9.0) * 6.0 * (1.0 - k2)
		var c2: Color = m["col"]
		c2.a = (1.0 - k2 * 0.7) * (0.8 + lift)
		draw_circle(p, 2.4 - k2 * 1.2, c2)
		draw_circle(p, 5.0 - k2 * 2.5, Color(c2.r, c2.g, c2.b, c2.a * 0.18))
