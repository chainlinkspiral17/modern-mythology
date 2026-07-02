class_name VolumeFog
extends Node3D
## Natural volumetric haze that FILLS the stage air. A few large, overlapping
## BOX FogVolumes (not ellipsoids — ellipsoids read as solid "blobs"); their
## shape comes entirely from a fractal 3D-noise density, so it looks wispy and
## clumpy and catches the rig beams. Each layer slowly drifts and spins its
## noise so the haze billows and flows. Forward+ with volumetric fog required.

# [offset-from-stage (x, y, z), box size (full extents), noise-freq, density-mul]
# Broad thin layers FILL the air; smaller high-mul pockets add THICKER patches at
# varied spots/heights so the haze naturally differs in density across the space.
const POCKETS := [
	# ── broad, thin fill (the base haze) ──
	[Vector3(-2.0, 4.5, 0.0), Vector3(42.0, 10.0, 48.0), 0.05, 0.7],   # low body
	[Vector3(2.0, 9.5, 0.0), Vector3(38.0, 9.0, 42.0), 0.045, 0.55],  # mid band
	[Vector3(-2.0, 15.0, 0.0), Vector3(36.0, 9.0, 36.0), 0.04, 0.45], # rafters
	# ── localized THICKER pockets (uneven pooling, different in each space) ──
	[Vector3(-6.0, 3.0, -13.0), Vector3(15.0, 7.0, 15.0), 0.09, 1.5],  # stage-left low clump
	[Vector3(-3.0, 6.5, 13.0), Vector3(14.0, 8.0, 14.0), 0.08, 1.3],   # stage-right mid clump
	[Vector3(6.0, 2.5, 3.0), Vector3(13.0, 5.0, 13.0), 0.1, 1.6],      # downstage thick low patch
	[Vector3(-10.0, 11.0, -4.0), Vector3(12.0, 7.0, 12.0), 0.07, 1.1], # upstage high wisp
	[Vector3(8.0, 8.0, -8.0), Vector3(11.0, 7.0, 11.0), 0.085, 1.2],   # downstage-left mid clump
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
	# big box volumes accumulate fast — keep the ceiling low so the WHOLE slider
	# is usable: 100% is a thick-but-wispy haze, not a solid fill.
	for x in vols:
		x["fm"].density = density * 0.004 * float(x["mul"])


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
