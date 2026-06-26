class_name VolumeFog
extends Node3D
## Volumetric smoke in POCKETS — several small ellipsoid FogVolumes scattered
## around the stage and venue air (with gaps between), each with a 3D-noise
## density so it's clumpy and catches the rig beams in patches rather than a
## uniform blanket. Low densities so you see through to the stage. Requires
## Forward+ with volumetric fog enabled. Each pocket drifts on its own phase.

# [offset-from-stage (x rel, y, z), size (radii), noise-freq, density-mul]
const POCKETS := [
	# low, around the stage
	[Vector3(-3.0, 3.5, -8.0), Vector3(11.0, 6.0, 9.0), 0.08, 1.2],
	[Vector3(-5.0, 5.5, 7.0), Vector3(10.0, 7.0, 9.0), 0.07, 1.1],
	[Vector3(2.0, 4.0, 0.0), Vector3(9.0, 5.0, 8.0), 0.09, 1.2],
	# up in the rafters over the stage (catches the aerial beams)
	[Vector3(0.0, 13.0, 0.0), Vector3(22.0, 6.0, 16.0), 0.05, 0.9],
	# out over the audience, low + high (catches the audience-aimed beams)
	[Vector3(24.0, 5.0, -15.0), Vector3(15.0, 8.0, 13.0), 0.05, 0.8],
	[Vector3(42.0, 6.5, 12.0), Vector3(17.0, 9.0, 15.0), 0.045, 0.7],
	[Vector3(62.0, 7.5, -7.0), Vector3(19.0, 10.0, 16.0), 0.04, 0.6],
	[Vector3(38.0, 15.0, 0.0), Vector3(34.0, 8.0, 42.0), 0.035, 0.55],
]

var vols: Array = []   # [{fv, fm, base, mul}]
var density := 0.4


func build(stage_x: float) -> void:
	for c in get_children():
		c.queue_free()
	vols.clear()
	for p in POCKETS:
		var off: Vector3 = p[0]
		_make(Vector3(stage_x + off.x, off.y, off.z), p[1], p[2], p[3])


func _make(pos: Vector3, size: Vector3, freq: float, mul: float) -> void:
	var fv := FogVolume.new()
	fv.shape = RenderingServer.FOG_VOLUME_SHAPE_ELLIPSOID   # soft blobby pocket
	fv.size = size
	fv.position = pos
	var fm := FogMaterial.new()
	fm.density = 0.1 * mul
	fm.albedo = Color(0.82, 0.82, 0.85)   # whiter pockets
	fm.emission = Color(0.0, 0.0, 0.0)
	fm.edge_fade = 0.6
	var noise := FastNoiseLite.new()
	noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	noise.frequency = freq
	var tex := NoiseTexture3D.new()
	tex.noise = noise
	tex.width = 40
	tex.height = 24
	tex.depth = 40
	tex.seamless = true
	fm.density_texture = tex
	fv.material = fm
	add_child(fv)
	vols.append({ "fv": fv, "fm": fm, "base": pos, "mul": mul })


func set_density(v: float) -> void:
	density = clampf(v, 0.0, 1.0)
	for x in vols:
		x["fm"].density = density * 0.9 * float(x["mul"])


func update(t: float) -> void:
	# slow flowing billow: translate the pocket AND rotate it — rotating the
	# volume spins its internal noise, so the clumps roll/swirl (not just slide)
	for i in vols.size():
		var x: Dictionary = vols[i]
		var base: Vector3 = x["base"]
		var ph := float(i) * 1.3
		x["fv"].position = base + Vector3(
			sin(t * 0.06 + ph) * 4.0 + sin(t * 0.11 + ph) * 1.5,
			sin(t * 0.045 + ph) * 1.5,
			cos(t * 0.05 + ph) * 4.0 + cos(t * 0.09 + ph) * 1.5
		)
		x["fv"].rotation = Vector3(
			sin(t * 0.03 + ph) * 0.2,
			t * 0.05 + ph,
			cos(t * 0.035 + ph) * 0.15
		)
