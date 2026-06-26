class_name VolumeFog
extends Node3D
## Natural volumetric haze that FILLS the stage air. A few large, overlapping
## BOX FogVolumes (not ellipsoids — ellipsoids read as solid "blobs"); their
## shape comes entirely from a fractal 3D-noise density, so it looks wispy and
## clumpy and catches the rig beams. Each layer slowly drifts and spins its
## noise so the haze billows and flows. Forward+ with volumetric fog required.

# [offset-from-stage (x, y, z), box size (full extents), noise-freq, density-mul]
const POCKETS := [
	# broad low body across the stage + front rows
	[Vector3(-2.0, 4.5, 0.0), Vector3(40.0, 10.0, 46.0), 0.055, 1.0],
	# mid-air band through the performance space (catches the front/zigzag beams)
	[Vector3(2.0, 9.5, 0.0), Vector3(36.0, 9.0, 40.0), 0.05, 0.8],
	# up in the rafters (catches the aerial/up beams)
	[Vector3(-2.0, 15.0, 0.0), Vector3(34.0, 9.0, 34.0), 0.042, 0.6],
]

var vols: Array = []   # [{fv, fm, base, mul, ph}]
var density := 0.4


func build(stage_x: float) -> void:
	for c in get_children():
		c.queue_free()
	vols.clear()
	var i := 0
	for p in POCKETS:
		var off: Vector3 = p[0]
		_make(Vector3(stage_x + off.x, off.y, off.z), p[1], p[2], p[3], i)
		i += 1


func _make(pos: Vector3, size: Vector3, freq: float, mul: float, idx: int) -> void:
	var fv := FogVolume.new()
	fv.shape = RenderingServer.FOG_VOLUME_SHAPE_BOX   # noise carves the shape, not the box
	fv.size = size
	fv.position = pos
	var fm := FogMaterial.new()
	fm.density = 0.06 * mul
	fm.albedo = Color(0.85, 0.86, 0.9)
	fm.emission = Color(0.04, 0.04, 0.05)   # faint self-glow so thick patches don't read black
	fm.edge_fade = 0.85                     # soften the box edges so it blends
	# fractal noise → wispy, multi-scale clumps rather than one smooth mass
	var noise := FastNoiseLite.new()
	noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	noise.fractal_type = FastNoiseLite.FRACTAL_FBM
	noise.fractal_octaves = 4
	noise.fractal_gain = 0.55
	noise.frequency = freq
	var tex := NoiseTexture3D.new()
	tex.noise = noise
	tex.width = 56
	tex.height = 40
	tex.depth = 56
	tex.seamless = true
	fm.density_texture = tex
	fv.material = fm
	add_child(fv)
	vols.append({ "fv": fv, "fm": fm, "base": pos, "mul": mul, "ph": float(idx) * 1.7 })


func set_density(v: float) -> void:
	density = clampf(v, 0.0, 1.0)
	# gentle: big box volumes accumulate fast, so keep the ceiling low — 100%
	# is a thick-but-still-wispy haze, not a solid fill.
	for x in vols:
		x["fm"].density = density * 0.04 * float(x["mul"])


func update(t: float) -> void:
	# billow: small drift keeps each layer roughly in place while its noise spins
	# (rotating a box volume spins the internal noise → the clumps roll and flow)
	for i in vols.size():
		var x: Dictionary = vols[i]
		var base: Vector3 = x["base"]
		var ph: float = x["ph"]
		x["fv"].position = base + Vector3(
			sin(t * 0.05 + ph) * 3.0 + sin(t * 0.09 + ph) * 1.0,
			sin(t * 0.04 + ph) * 1.0,
			cos(t * 0.045 + ph) * 3.0 + cos(t * 0.08 + ph) * 1.0
		)
		x["fv"].rotation = Vector3(
			sin(t * 0.02 + ph) * 0.08,
			t * 0.03 + ph,
			cos(t * 0.025 + ph) * 0.06
		)
