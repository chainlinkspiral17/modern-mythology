class_name VolumeFog
extends Node3D
## True volumetric smoke that fills the air with FORM — FogVolume boxes whose
## density comes from a 3D noise texture, so it's clumpy/billowing (not flat
## haze), scatters the rig beams and takes shadow. Densities are kept low so you
## can see THROUGH it (the camera often sits inside a volume); crank with F1/F2.
## Requires Forward+ with volumetric fog enabled. Slowly drifts.

var vols: Array = []   # [{fv, fm, base, mul}]
var density := 0.2


func build(stage_x: float) -> void:
	for c in get_children():
		c.queue_free()
	vols.clear()
	# dense-ish over the stage (the visual focus); thinner over the crowd air so
	# the camera isn't buried in soup
	_make(Vector3(stage_x - 2.0, 7.0, 0.0), Vector3(46.0, 15.0, 30.0), 0.06, 1.0)
	_make(Vector3(stage_x + 45.0, 9.0, 0.0), Vector3(95.0, 18.0, 64.0), 0.045, 0.45)


func _make(pos: Vector3, size: Vector3, freq: float, mul: float) -> void:
	var fv := FogVolume.new()
	fv.shape = RenderingServer.FOG_VOLUME_SHAPE_BOX
	fv.size = size
	fv.position = pos
	var fm := FogMaterial.new()
	fm.density = 0.06 * mul
	fm.albedo = Color(0.65, 0.65, 0.7)   # mid grey: forms shape without blowing white
	fm.emission = Color(0.0, 0.0, 0.0)
	fm.edge_fade = 0.5
	var noise := FastNoiseLite.new()
	noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	noise.frequency = freq
	var tex := NoiseTexture3D.new()
	tex.noise = noise
	tex.width = 48
	tex.height = 24
	tex.depth = 48
	tex.seamless = true
	fm.density_texture = tex
	fv.material = fm
	add_child(fv)
	vols.append({ "fv": fv, "fm": fm, "base": pos, "mul": mul })


func set_density(v: float) -> void:
	density = clampf(v, 0.0, 1.0)
	for x in vols:
		x["fm"].density = density * 0.3 * float(x["mul"])   # low so it reads as haze, not soup


func update(t: float) -> void:
	for i in vols.size():
		var x: Dictionary = vols[i]
		var base: Vector3 = x["base"]
		x["fv"].position = base + Vector3(
			sin(t * 0.06 + float(i)) * 4.0,
			sin(t * 0.04 + float(i) * 1.7) * 1.5,
			cos(t * 0.05 + float(i)) * 4.0
		)
