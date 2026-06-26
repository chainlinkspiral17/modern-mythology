class_name LightingRig
extends Node3D
## Cinematic, escalating stage lighting. build(stage_x, level) hangs a fixture
## set that grows with the stage (1 intimate → 3 spectacle). Fixtures are typed:
##   key    — warm, shadow-casting front key on the performers
##   rim    — cool back/rim light for separation
##   wash   — colour washes across the stage
##   beam   — narrow movers that sweep (strong volumetric beams in haze)
##   blinder— audience blinders (face the crowd)
##   floor  — up-lights on the deck
## Looks recolour/animate the groups; a chase engine animates off the timeline
## clock so it plays in time with the music. master dimmer + strobe + blackout.

const LOOKS := ["key + rim", "warm wash", "cool wash", "colour sweep", "beam fan", "alternating chase", "strobe", "follow spot", "blackout"]

var fixtures: Array = []   # [{light, z, base, kind}]
var follow: SpotLight3D
var look_idx := 0
var strobe := false
var blackout := false
var master := 1.0
var _stage_x := 0.0


func build(stage_x: float, level: int) -> void:
	for c in get_children():
		c.queue_free()
	fixtures.clear()
	follow = null
	_stage_x = stage_x
	var ctr := Vector3(stage_x - 2.0, 2.5, 0.0)

	# KEY — warm, shadowed, from front-high (always)
	_fixture(Vector3(stage_x + 10.0, 9.0, -3.0), ctr, Color(1.0, 0.85, 0.65), 26.0, 5.5, "key", true)
	# RIM/back — cool, from upstage (always)
	_fixture(Vector3(stage_x - 8.0, 8.5, -5.0), ctr, Color(0.55, 0.7, 1.0), 30.0, 4.0, "rim", false)
	_fixture(Vector3(stage_x - 8.0, 8.5, 5.0), ctr, Color(0.55, 0.7, 1.0), 30.0, 4.0, "rim", false)
	# front wash row (count grows with level)
	var wash_n := 3 + level * 2
	for i in wash_n:
		var z := lerpf(-9.0, 9.0, float(i) / float(maxi(wash_n - 1, 1)))
		_fixture(Vector3(stage_x + 2.0, 9.0, z), Vector3(stage_x - 3.0, 1.5, z * 0.4), Color(1.0, 0.8, 0.6), 34.0, 4.5, "wash", false)

	if level >= 2:
		# beam movers + audience blinders
		for i in 4:
			var z := lerpf(-8.0, 8.0, float(i) / 3.0)
			_fixture(Vector3(stage_x + 1.0, 9.5, z), Vector3(stage_x - 4.0, 1.0, z), Color(0.8, 0.4, 1.0), 9.0, 9.0, "beam", false)
		_fixture(Vector3(stage_x + 3.0, 6.5, -4.0), Vector3(stage_x + 30.0, 4.0, -4.0), Color(1.0, 0.95, 0.85), 40.0, 0.0, "blinder", false)
		_fixture(Vector3(stage_x + 3.0, 6.5, 4.0), Vector3(stage_x + 30.0, 4.0, 4.0), Color(1.0, 0.95, 0.85), 40.0, 0.0, "blinder", false)

	if level >= 3:
		# overhead beam array + floor up-lights
		for i in 8:
			var z := lerpf(-10.0, 10.0, float(i) / 7.0)
			_fixture(Vector3(stage_x - 3.0, 9.5, z), Vector3(stage_x - 3.0, 1.0, z), Color(0.4, 0.7, 1.0), 7.0, 8.0, "beam", false)
		for i in 5:
			var z := lerpf(-9.0, 9.0, float(i) / 4.0)
			_fixture(Vector3(stage_x - 5.0, 0.3, z), Vector3(stage_x - 5.0, 8.0, z), Color(1.0, 0.3, 0.5), 28.0, 4.0, "floor", false)

	# follow spot — hard pin from front of house (always)
	follow = SpotLight3D.new()
	follow.position = Vector3(stage_x + 34.0, 16.0, 0.0)
	follow.spot_range = 95.0
	follow.spot_angle = 5.0
	follow.light_energy = 9.0
	follow.light_color = Color(1.0, 1.0, 0.96)
	follow.light_volumetric_fog_energy = 2.5
	follow.shadow_enabled = true
	add_child(follow)
	follow.look_at(ctr, _safe_up(ctr - follow.position))


func _fixture(pos: Vector3, aim: Vector3, color: Color, angle: float, energy: float, kind: String, shadow: bool) -> void:
	var s := SpotLight3D.new()
	s.position = pos
	s.spot_range = 60.0
	s.spot_angle = angle
	s.light_energy = energy
	s.light_color = color
	s.light_volumetric_fog_energy = 3.5 if kind == "beam" else 1.5
	s.shadow_enabled = shadow
	add_child(s)
	s.look_at(aim, _safe_up(aim - pos))
	fixtures.append({ "light": s, "z": pos.z, "base": s.rotation, "kind": kind })


## Pick an up-vector that isn't colinear with the aim direction (floor/overhead
## fixtures aim straight up/down, which would warn with the default UP).
static func _safe_up(dir: Vector3) -> Vector3:
	if dir.length() < 0.001 or absf(dir.normalized().dot(Vector3.UP)) > 0.999:
		return Vector3(0.0, 0.0, 1.0)
	return Vector3.UP


func set_follow_target(p: Vector3) -> void:
	if follow:
		follow.look_at(p, _safe_up(p - follow.global_position))


func set_master(v: float) -> void:
	master = clampf(v, 0.0, 1.5)


func cycle_look() -> void:
	look_idx = (look_idx + 1) % LOOKS.size()


func look_name() -> String:
	return LOOKS[look_idx]


func update(t: float) -> void:
	var look := look_name()
	var dark := blackout or look == "blackout"
	var strobe_on := fposmod(t * 12.0, 1.0) < 0.5
	for f in fixtures:
		var s: SpotLight3D = f["light"]
		var kind: String = f["kind"]
		var z: float = f["z"]
		var base: Vector3 = f["base"]
		if dark:
			s.visible = false
			continue
		s.visible = true
		var col: Color = s.light_color
		var e := 0.0
		var rot := base
		match kind:
			"key":
				col = Color(1.0, 0.84, 0.64)
				e = 5.5 if look != "follow spot" else 1.5
			"rim":
				col = Color(0.55, 0.7, 1.0)
				e = 4.0
			"wash":
				col = _wash_colour(look, z, t)
				e = 4.5
				if look == "alternating chase":
					e = 7.0 if (int(floor(t * 4.0)) + int(z)) % 2 == 0 else 0.4
				elif look == "follow spot":
					e = 1.0
			"beam":
				col = Color.from_hsv(fposmod(t * 0.12 + z * 0.05, 1.0), 0.85, 1.0)
				e = 9.0 if (look == "beam fan" or look == "colour sweep") else 2.5
				rot = base + Vector3(sin(t * 1.1 + z * 0.2) * 0.25, sin(t * 1.7 + z * 0.3) * 0.7, 0.0)
			"blinder":
				e = 14.0 if (strobe and strobe_on) else (3.0 if look == "beam fan" else 0.0)
				col = Color(1.0, 0.96, 0.88)
			"floor":
				col = Color.from_hsv(fposmod(0.5 - t * 0.06 + z * 0.04, 1.0), 0.75, 1.0)
				e = 4.0
		if look == "strobe":
			col = Color(1.0, 1.0, 1.0)
			e = 16.0 if strobe_on else 0.0
			rot = base
		elif strobe and not strobe_on:
			e = 0.0
		s.light_color = col
		s.light_energy = e * master
		s.rotation = rot
	if follow:
		follow.visible = (look == "follow spot") and not dark
		follow.light_energy = 10.0 * master


func _wash_colour(look: String, z: float, t: float) -> Color:
	match look:
		"cool wash":
			return Color(0.5, 0.65, 1.0)
		"colour sweep":
			return Color.from_hsv(fposmod(t * 0.08 + z * 0.03, 1.0), 0.7, 1.0)
		_:
			return Color(1.0, 0.78, 0.55)
