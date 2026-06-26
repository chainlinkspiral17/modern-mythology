class_name VolumeFog
extends Node3D
## True volumetric smoke that fills the air with FORM — FogVolume boxes whose
## density comes from a 3D noise texture, so it's clumpy/billowing (not flat
## haze), scatters the rig beams, and takes shadow. Slowly drifts. Lives on top
## of the (thin) environment volumetric fog. Requires Forward+ with volumetric
## fog enabled (it is). set_density scales it live.

var vols: Array = []   # [{fv, fm, base, size}]
var density := 0.5


func build(stage_x: float) -> void:
	for c in get_children():
		c.queue_free()
	vols.clear()
	# over the stage (tighter, denser) + a big body of air over the crowd
	_make(Vector3(stage_x - 2.0, 7.0, 0.0), Vector3(46.0, 15.0, 30.0), 0.06)
	_make(Vector3(stage_x + 45.0, 9.0, 0.0), Vector3(95.0, 18.0, 64.0), 0.045)


func _make(pos: Vector3, size: Vector3, freq: float) -> void:
	var fv := FogVolume.new()
	fv.shape = RenderingServer.FOG_VOLUME_SHAPE_BOX
	fv.size = size
	fv.position = pos
	var fm := FogMaterial.new()
	fm.density = 0.4
	fm.albedo = Color(0.65, 0.65, 0.7)   # mid grey so it forms shape without blowing white
	fm.emission = Color(0.0, 0.0, 0.0)
	fm.edge_fade = 0.4
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
	vols.append({ "fv": fv, "fm": fm, "base": pos, "size": size })


func set_density(v: float) -> void:
	density = clampf(v, 0.0, 1.0)
	for x in vols:
		x["fm"].density = density * 0.8


func update(t: float) -> void:
	# slow bounded drift so the clumps roll through the space
	for i in vols.size():
		var x: Dictionary = vols[i]
		var base: Vector3 = x["base"]
		x["fv"].position = base + Vector3(
			sin(t * 0.06 + float(i)) * 4.0,
			sin(t * 0.04 + float(i) * 1.7) * 1.5,
			cos(t * 0.05 + float(i)) * 4.0
		)
