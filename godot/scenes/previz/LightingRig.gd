class_name LightingRig
extends Node3D
## A late-70s / early-80s stage lighting rig: a row of colored wash/PAR fixtures
## plus a follow spot, hung on the truss and visible as volumetric beams in the
## haze (Forward+). A small chase engine animates colour / pan / intensity as a
## function of time, so when it's driven by the timeline clock it "plays along
## with the music". Drive it by calling update(t) every frame.

const LOOKS := ["warm wash", "cool wash", "color sweep", "alternating chase", "strobe", "follow spot", "blackout"]

var fixtures: Array = []   # [{light, z, base}]
var follow: SpotLight3D
var look_idx := 0
var strobe := false
var blackout := false
var _follow_target := Vector3.ZERO


func build(stage_x: float) -> void:
	for c in get_children():
		c.queue_free()
	fixtures.clear()
	_follow_target = Vector3(stage_x - 2.0, 4.0, 0.0)
	var n := 8
	var truss_y := 10.0
	for i in n:
		var z := lerpf(-9.0, 9.0, float(i) / float(n - 1))
		var s := SpotLight3D.new()
		s.position = Vector3(stage_x + 1.5, truss_y, z)
		s.spot_range = 50.0
		s.spot_angle = 12.0
		s.light_energy = 6.0
		s.light_color = Color(1.0, 0.8, 0.6)
		s.light_volumetric_fog_energy = 2.5
		s.shadow_enabled = false
		add_child(s)
		s.look_at(Vector3(stage_x - 3.0, 1.5, z * 0.4), Vector3.UP)
		fixtures.append({ "light": s, "z": z, "base": s.rotation })
	# follow spot — a hard pin from front-of-house
	follow = SpotLight3D.new()
	follow.position = Vector3(stage_x + 32.0, 15.0, 0.0)
	follow.spot_range = 90.0
	follow.spot_angle = 6.0
	follow.light_energy = 9.0
	follow.light_color = Color(1.0, 1.0, 0.95)
	follow.light_volumetric_fog_energy = 2.0
	follow.shadow_enabled = false
	add_child(follow)
	follow.look_at(_follow_target, Vector3.UP)


func set_follow_target(p: Vector3) -> void:
	_follow_target = p
	if follow:
		follow.look_at(p, Vector3.UP)


func cycle_look() -> void:
	look_idx = (look_idx + 1) % LOOKS.size()


func look_name() -> String:
	return LOOKS[look_idx]


func update(t: float) -> void:
	var look := look_name()
	var dark := blackout or look == "blackout"
	for i in fixtures.size():
		var f: Dictionary = fixtures[i]
		var s: SpotLight3D = f["light"]
		var z: float = f["z"]
		var base: Vector3 = f["base"]
		s.visible = not dark
		if dark:
			continue
		match look:
			"cool wash":
				s.light_color = Color(0.5, 0.65, 1.0)
				s.light_energy = 5.0
				s.rotation = base
			"color sweep":
				s.light_color = Color.from_hsv(fposmod(t * 0.08 + z * 0.03, 1.0), 0.75, 1.0)
				s.light_energy = 7.0
				s.rotation = base + Vector3(0.0, sin(t * 1.2 + z * 0.2) * 0.5, 0.0)
			"alternating chase":
				var on := (int(floor(t * 4.0)) + i) % 2 == 0
				s.light_energy = 9.0 if on else 0.4
				s.light_color = Color(1.0, 0.3, 0.3) if (i % 2 == 0) else Color(0.3, 0.5, 1.0)
				s.rotation = base
			"strobe":
				s.light_color = Color(1.0, 1.0, 1.0)
				s.light_energy = 16.0 if fposmod(t * 12.0, 1.0) < 0.5 else 0.0
				s.rotation = base
			"follow spot":
				s.light_color = Color(0.85, 0.8, 0.75)
				s.light_energy = 1.8
				s.rotation = base
			_:  # warm wash
				s.light_color = Color(1.0, 0.78, 0.55)
				s.light_energy = 6.0
				s.rotation = base
		# global strobe overlay (independent of the strobe look)
		if strobe and look != "strobe" and fposmod(t * 12.0, 1.0) >= 0.5:
			s.light_energy = 0.0
	if follow:
		follow.visible = (look == "follow spot") and not dark
