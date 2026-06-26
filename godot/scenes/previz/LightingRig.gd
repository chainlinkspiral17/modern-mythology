class_name LightingRig
extends Node3D
## Touring-grade stage lighting that scales HARD with the stage level:
##   1 = intimate (a few movers + wash)   2 = club/theatre   3 = STADIUM package
## Fixture kinds: key, rim, wash, beam (front/mid movers), aerial (sky beams),
## blinder (audience), strobe (upstage wall), floor (up-lights). Movers animate
## in formations off the timeline clock so the rig plays to the music. Only the
## beam/aerial movers feed the volumetric fog (perf); 1 shadow-caster (key).

const LOOKS := ["garage rock", "kraut shafts", "anthem rwb", "key + rim", "warm wash", "cool wash", "colour sweep", "amber theatrical", "magenta / cyan", "rgb tri", "beam fan", "alternating chase", "white out", "strobe", "follow spot", "blackout"]
const FORMATIONS := ["static", "wave", "fan", "circle", "cross", "converge", "chase"]
const SPEEDS := [0.5, 1.0, 2.0]
const ENERGETIC := ["kraut shafts", "anthem rwb", "colour sweep", "amber theatrical", "magenta / cyan", "rgb tri", "beam fan", "alternating chase", "white out", "strobe"]

var fixtures: Array = []   # [{light, z, base, kind}]
var follow: SpotLight3D
var look_idx := 0
var formation_idx := 1
var speed_idx := 1
var strobe := false
var blackout := false
var master := 1.0
var _stage_x := 0.0
var _mover_n := 0


func build(stage_x: float, level: int) -> void:
	for c in get_children():
		c.queue_free()
	fixtures.clear()
	follow = null
	_stage_x = stage_x
	var ctr := Vector3(stage_x - 2.0, 2.5, 0.0)

	# KEY (shadowed) + cool RIM/back — always
	_fixture(Vector3(stage_x + 10.0, 9.0, -3.0), ctr, Color(1.0, 0.85, 0.65), 26.0, 6.0, "key", true, 0.0)
	_fixture(Vector3(stage_x - 8.0, 8.5, -5.0), ctr, Color(0.55, 0.7, 1.0), 30.0, 5.0, "rim", false, 0.0)
	_fixture(Vector3(stage_x - 8.0, 8.5, 5.0), ctr, Color(0.55, 0.7, 1.0), 30.0, 5.0, "rim", false, 0.0)

	# FRONT TRUSS movers + wash — counts scale with level
	# Two rows of six movers hung off the top of the stage scaffold (truss top
	# y8, about halfway from ground to the y12 roof apex). The bottom row is
	# offset half a column in Z so the rig reads as a ZIG-ZAG. All twelve sweep
	# 180 degrees (pan + tilt) in UNISON off the clock (kind "zigzag").
	var cols := 6
	var zlo := -11.0
	var zhi := 11.0
	var zstep := (zhi - zlo) / float(cols - 1)
	for i in cols:
		var z := zlo + zstep * float(i)
		# Aimed OUT over the audience (+X) at roughly fixture height so the unison
		# tilt sweep rakes from the stage/front rows up to high above the crowd,
		# and the ±90° pan sweeps the full width.
		# top row — mounted on the truss cross
		_fixture(Vector3(stage_x + 1.0, 8.0, z), Vector3(stage_x + 38.0, 6.5, z), Color(0.8, 0.4, 1.0), 9.0, 12.0, "zigzag", false, 4.0)
		# bottom row — hung lower and staggered half a column
		_fixture(Vector3(stage_x + 1.5, 6.5, z + zstep * 0.5), Vector3(stage_x + 38.0, 6.5, z + zstep * 0.5), Color(0.5, 0.6, 1.0), 9.0, 12.0, "zigzag", false, 4.0)
	var wash_n := 4 + level * 2               # 6 / 8 / 10
	for i in wash_n:
		var z := lerpf(-11.0, 11.0, float(i) / float(maxi(wash_n - 1, 1)))
		_fixture(Vector3(stage_x + 2.0, 9.0, z), Vector3(stage_x - 3.0, 1.5, z * 0.4), Color(1.0, 0.8, 0.6), 34.0, 6.0, "wash", false, 0.0)

	if level >= 2:
		# mid-truss movers
		for i in 6:
			var z := lerpf(-10.0, 10.0, float(i) / 5.0)
			_fixture(Vector3(stage_x - 3.0, 9.0, z), Vector3(stage_x - 3.0, 1.0, z), Color(0.4, 0.7, 1.0), 8.0, 12.0, "beam", false, 4.0)
		# audience blinders (face the crowd) + side-boom washes
		for i in 4:
			var z := lerpf(-9.0, 9.0, float(i) / 3.0)
			_fixture(Vector3(stage_x + 3.0, 6.5, z), Vector3(stage_x + 30.0, 4.0, z), Color(1.0, 0.95, 0.85), 45.0, 0.0, "blinder", false, 0.0)
		_fixture(Vector3(stage_x + 1.0, 4.0, -13.0), ctr, Color(0.9, 0.6, 1.0), 36.0, 5.0, "wash", false, 0.0)
		_fixture(Vector3(stage_x + 1.0, 4.0, 13.0), ctr, Color(0.9, 0.6, 1.0), 36.0, 5.0, "wash", false, 0.0)
		# audience-sweep movers — aimed up & out over the crowd so beams rake the
		# air and catch the over-audience fog pockets
		for i in 4:
			var z := lerpf(-8.0, 8.0, float(i) / 3.0)
			_fixture(Vector3(stage_x + 2.0, 9.5, z), Vector3(stage_x + 55.0, 18.0, z * 2.5), Color(0.7, 0.5, 1.0), 8.0, 12.0, "beam", false, 4.5)

	if level >= 3:
		# aerial sky-beams along the back truss (point up + out over the crowd)
		for i in 8:
			var z := lerpf(-11.0, 11.0, float(i) / 7.0)
			var pos := Vector3(stage_x - 6.0, 9.5, z)
			_fixture(pos, pos + Vector3(12.0, 22.0, 0.0), Color(0.5, 0.6, 1.0), 7.0, 14.0, "aerial", false, 5.0)
		# upstage STROBE WALL (faces the audience)
		for i in 6:
			var z := lerpf(-10.0, 10.0, float(i) / 5.0)
			_fixture(Vector3(stage_x - 7.0, 5.0, z), Vector3(stage_x + 20.0, 4.0, z), Color(1.0, 1.0, 1.0), 50.0, 0.0, "strobe", false, 0.0)
		# floor up-lights
		for i in 6:
			var z := lerpf(-9.0, 9.0, float(i) / 5.0)
			_fixture(Vector3(stage_x - 5.0, 0.3, z), Vector3(stage_x - 5.0, 8.0, z), Color(1.0, 0.3, 0.5), 28.0, 6.0, "floor", false, 0.0)
		# side ground-support towers, a stack of movers each
		for side in [-14.0, 14.0]:
			for j in 3:
				var y := 3.0 + float(j) * 2.5
				_fixture(Vector3(stage_x + 2.0, y, side), ctr, Color(0.6, 0.9, 1.0), 8.0, 12.0, "beam", false, 4.0)
		# more audience-sweep movers raking high over the crowd
		for i in 4:
			var z := lerpf(-10.0, 10.0, float(i) / 3.0)
			_fixture(Vector3(stage_x + 1.0, 9.5, z), Vector3(stage_x + 70.0, 20.0, z * 3.0), Color(0.9, 0.5, 0.8), 7.0, 13.0, "beam", false, 5.0)

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

	_mover_n = 0
	for f in fixtures:
		if f["kind"] == "beam" or f["kind"] == "aerial":
			_mover_n += 1


func _fixture(pos: Vector3, aim: Vector3, color: Color, angle: float, energy: float, kind: String, shadow: bool, vol: float) -> void:
	var s := SpotLight3D.new()
	s.position = pos
	s.spot_range = 70.0
	s.spot_angle = angle
	s.light_energy = energy
	s.light_color = color
	# beams/aerials/zig-zag movers scatter hard into the fog as solid shafts
	s.light_volumetric_fog_energy = 12.0 if (kind == "beam" or kind == "aerial" or kind == "zigzag") else vol
	s.shadow_enabled = shadow
	add_child(s)
	s.look_at(aim, _safe_up(aim - pos))
	# visible gear: a dark housing + an emissive lens that glows the live colour
	var holder := Node3D.new()
	holder.position = pos
	add_child(holder)
	holder.look_at(aim, _safe_up(aim - pos))
	# static body/yoke (stays mounted while the head sweeps)
	var house := MeshInstance3D.new()
	var hb := BoxMesh.new()
	hb.size = Vector3(0.5, 0.5, 0.5)
	house.mesh = hb
	var hm := StandardMaterial3D.new()
	hm.albedo_color = Color(0.07, 0.07, 0.08)
	hm.metallic = 0.6
	hm.roughness = 0.4
	house.material_override = hm
	holder.add_child(house)
	# moving HEAD — pivots at the fixture; this is the part that pans/tilts. It
	# carries a dark-metal half-dome reflector CUP whose OPEN MOUTH faces forward,
	# with a bright disc across the mouth as the lit face. -Z is forward.
	var head := Node3D.new()
	holder.add_child(head)
	var cup := MeshInstance3D.new()
	var cm := SphereMesh.new()
	cm.radius = 0.22
	cm.height = 0.44
	cm.is_hemisphere = true
	cm.radial_segments = 20
	cm.rings = 9
	cup.mesh = cm
	cup.position = Vector3(0.0, 0.0, -0.34)
	cup.rotation_degrees = Vector3(90.0, 0.0, 0.0)   # open mouth → -Z (forward), dome → back
	var cupm := StandardMaterial3D.new()
	cupm.albedo_color = Color(0.06, 0.06, 0.07)      # dark metal shell
	cupm.metallic = 0.7
	cupm.roughness = 0.35
	cupm.cull_mode = BaseMaterial3D.CULL_DISABLED    # see the inside of the cup too
	cup.material_override = cupm
	head.add_child(cup)
	var lens := MeshInstance3D.new()
	var disc := CylinderMesh.new()
	disc.top_radius = 0.2
	disc.bottom_radius = 0.2
	disc.height = 0.02
	disc.radial_segments = 20
	lens.mesh = disc
	lens.position = Vector3(0.0, 0.0, -0.35)
	lens.rotation_degrees = Vector3(90.0, 0.0, 0.0)   # disc faces -Z (out the mouth)
	var lm := StandardMaterial3D.new()
	lm.albedo_color = Color(0.02, 0.02, 0.02)
	lm.emission_enabled = true
	lm.emission = color.lerp(Color(1.0, 1.0, 1.0), 0.55)   # bright white face, faint colour halo
	lm.emission_energy_multiplier = 2.0
	lens.material_override = lm
	head.add_child(lens)
	fixtures.append({ "light": s, "z": pos.z, "base": s.rotation, "kind": kind, "lens": lm, "head": head })


## Up-vector that isn't colinear with the aim (floor/aerial fixtures aim near-vertical).
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


func use_look(name: String) -> void:
	var i := LOOKS.find(name)
	if i >= 0:
		look_idx = i


func look_name() -> String:
	return LOOKS[look_idx]


func cycle_formation() -> void:
	formation_idx = (formation_idx + 1) % FORMATIONS.size()


func use_formation(name: String) -> void:
	var i := FORMATIONS.find(name)
	if i >= 0:
		formation_idx = i


func formation_name() -> String:
	return FORMATIONS[formation_idx]


func cycle_speed() -> void:
	speed_idx = (speed_idx + 1) % SPEEDS.size()


func use_speed_idx(i: int) -> void:
	speed_idx = clampi(i, 0, SPEEDS.size() - 1)


func speed_name() -> String:
	return "%.1fx" % SPEEDS[speed_idx]


func _energetic(look: String) -> bool:
	return look in ENERGETIC


func _beam_colour(look: String, idx: int, z: float, t: float) -> Color:
	match look:
		"garage rock":
			return Color(1.0, 1.0, 1.0)
		"kraut shafts":
			return Color(0.2, 0.45, 1.0)
		"anthem rwb":
			return [Color(1.0, 0.15, 0.15), Color(1.0, 1.0, 1.0), Color(0.2, 0.3, 1.0)][idx % 3]
		"magenta / cyan":
			return Color(1.0, 0.2, 0.7) if idx % 2 == 0 else Color(0.2, 0.9, 1.0)
		"rgb tri":
			return [Color(1.0, 0.2, 0.2), Color(0.2, 1.0, 0.3), Color(0.3, 0.4, 1.0)][idx % 3]
		_:
			return Color.from_hsv(fposmod(t * 0.12 + z * 0.05, 1.0), 0.85, 1.0)


## Geometric descending shafts: tilt down, mirrored pan that snaps on the beat.
func _kraut_shaft(i: int, t: float) -> Vector3:
	var step := float(int(t * 2.0) % 4)
	var mag := lerpf(0.2, 0.9, step / 3.0)
	var sgn := 1.0 if i % 2 == 0 else -1.0
	return Vector3(0.5, mag * sgn, 0.0)


## Whole-bank UNISON sweep for the starting zig-zag rig: pans the full 180°
## (±90° = π/2) left↔right while tilting up↔down, every fixture in lockstep.
func _unison_sweep(t: float) -> Vector3:
	var tt := t * float(SPEEDS[speed_idx])
	var pan := sin(tt * 0.5) * (PI * 0.5)    # ±90° → 180° total, left↔right
	# wide up↔down rake: from down on the stage/front rows up to high above the
	# audience (≈ ±63°), on a slower cycle than the pan
	var tilt := sin(tt * 0.27) * 1.1
	return Vector3(tilt, pan, 0.0)


## Per-mover pan/tilt offset for the current formation (radians, added to base).
func _formation_offset(i: int, n: int, t: float, gain := 1.0) -> Vector3:
	var tt := t * float(SPEEDS[speed_idx])
	var phase := float(i) * (TAU / float(maxi(n, 1)))
	match FORMATIONS[formation_idx]:
		"wave":
			return Vector3(0.0, sin(tt + phase) * 0.6 * gain, 0.0)
		"fan":
			var spread := (float(i) / float(maxi(n - 1, 1)) - 0.5) * 1.4
			return Vector3(0.0, spread * (0.4 + 0.6 * absf(sin(tt))) * gain, 0.0)
		"circle":
			return Vector3(cos(tt + phase) * 0.4 * gain, sin(tt + phase) * 0.6 * gain, 0.0)
		"cross":
			return Vector3(0.0, sin(tt) * (1.0 if i % 2 == 0 else -1.0) * 0.7 * gain, 0.0)
		"converge":
			return Vector3(sin(tt) * 0.2 * gain, sin(tt * 0.7) * 0.3 * gain, 0.0)
		"chase":
			return Vector3(0.0, sin(tt * 1.5 + phase) * 0.7 * gain, 0.0)
		_:
			return Vector3.ZERO


func update(t: float, level := 0.0, active := false) -> void:
	var look := look_name()
	var dark := blackout or look == "blackout"
	var hot := _energetic(look)
	# audio-reactive: pump/flash to the music when it's playing, else a gentle pulse
	var beat := level if active else (0.5 + 0.5 * sin(t * 3.0))
	var pump := 0.55 + 0.9 * beat
	# strobe ONLY when explicitly armed (key 5) or the dedicated strobe look —
	# never automatically in an energetic set. Flashes on the beat, tamed rate.
	var strobe_armed := strobe or look == "strobe"
	var strobe_hit := (level > 0.5) if active else (fposmod(t * 5.0, 1.0) < 0.15)
	# garage rock: occasional red flash (on a strong beat, or rarely on the timer)
	var garage_hit := (level > 0.6) if active else (fposmod(t * 0.8, 1.0) < 0.06)
	var mi := 0
	for f in fixtures:
		var s: SpotLight3D = f["light"]
		var kind: String = f["kind"]
		var z: float = f["z"]
		var base: Vector3 = f["base"]
		var lens: StandardMaterial3D = f["lens"]
		var head: Node3D = f["head"]
		if dark:
			s.visible = false
			lens.emission = Color(0.0, 0.0, 0.0)
			continue
		s.visible = true
		var col: Color = s.light_color
		var e := 0.0
		var rot := base
		match kind:
			"key":
				col = Color(1.0, 0.84, 0.64)
				e = 6.0 if look != "follow spot" else 1.5
			"rim":
				col = Color(0.55, 0.7, 1.0)
				e = 5.0
			"wash":
				col = _wash_colour(look, z, t)
				e = 6.0 * (pump if hot else 1.0)
				if look == "alternating chase":
					e = 8.0 if (int(floor(t * 4.0)) + int(z)) % 2 == 0 else 0.5
				elif look == "follow spot":
					e = 1.2
			"zigzag":
				# starting-rig front array: the whole bank sweeps 180 in UNISON
				col = _beam_colour(look, mi, z, t)
				e = (12.0 * pump) if hot else 4.0
				rot = base + _unison_sweep(t)
				mi += 1
			"beam":
				col = _beam_colour(look, mi, z, t)
				e = (12.0 * pump) if hot else 2.5
				if look == "kraut shafts":
					rot = base + _kraut_shaft(mi, t)
				else:
					rot = base + _formation_offset(mi, maxi(_mover_n, 1), t)
				mi += 1
			"aerial":
				col = _beam_colour(look, mi, z, t)
				e = (14.0 * pump) if hot else 3.0
				rot = base + _formation_offset(mi, maxi(_mover_n, 1), t, 1.6)
				mi += 1
			"blinder":
				if look == "garage rock":
					col = Color(1.0, 0.12, 0.12)   # red flashes
					e = 13.0 if garage_hit else 0.0
				else:
					col = Color(1.0, 0.96, 0.88)
					e = 14.0 if (strobe_armed and strobe_hit) else 0.0
			"strobe":
				col = Color(1.0, 1.0, 1.0)
				e = 14.0 if (strobe_armed and strobe_hit) else 0.0
			"floor":
				col = Color.from_hsv(fposmod(0.5 - t * 0.06 + z * 0.04, 1.0), 0.75, 1.0)
				e = 6.0
		# the dedicated strobe LOOK flashes the whole rig (still only on the hit)
		if look == "strobe" and kind != "strobe" and kind != "blinder":
			col = Color(1.0, 1.0, 1.0)
			e = 12.0 if strobe_hit else 0.0
			rot = base
		s.light_color = col
		s.light_energy = e * master
		s.rotation = rot
		head.rotation = rot - base   # the head pans/tilts; the body stays mounted
		# bright white face with a faint colour halo; HDR multiplier blooms the
		# core white as the fixture gets hot
		lens.emission = col.lerp(Color(1.0, 1.0, 1.0), 0.55)
		lens.emission_energy_multiplier = clampf(e * master * 0.5, 0.0, 8.0)
	if follow:
		follow.visible = (look == "follow spot") and not dark
		follow.light_energy = 10.0 * master


func _wash_colour(look: String, z: float, t: float) -> Color:
	match look:
		"garage rock":
			return Color(1.0, 1.0, 1.0)
		"kraut shafts":
			return Color(0.15, 0.35, 1.0) if int(absf(z)) % 2 == 0 else Color(0.1, 0.7, 1.0)
		"anthem rwb":
			return [Color(1.0, 0.15, 0.15), Color(1.0, 1.0, 1.0), Color(0.2, 0.3, 1.0)][int(absf(z)) % 3]
		"cool wash":
			return Color(0.5, 0.65, 1.0)
		"colour sweep":
			return Color.from_hsv(fposmod(t * 0.08 + z * 0.03, 1.0), 0.7, 1.0)
		"amber theatrical":
			return Color(1.0, 0.7, 0.35)
		"magenta / cyan":
			return Color(1.0, 0.2, 0.7) if int(absf(z)) % 2 == 0 else Color(0.2, 0.9, 1.0)
		"rgb tri":
			var c := [Color(1.0, 0.2, 0.2), Color(0.2, 1.0, 0.3), Color(0.3, 0.4, 1.0)]
			return c[int(absf(z)) % 3]
		"white out":
			return Color(1.0, 1.0, 1.0)
		_:
			return Color(1.0, 0.78, 0.55)
