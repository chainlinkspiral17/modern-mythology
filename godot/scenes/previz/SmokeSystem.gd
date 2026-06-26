class_name SmokeSystem
extends Node3D
## Several fog/smoke machines placed around the stage (downstage L/R, upstage L/R,
## centre), so the haze billows from multiple sources like real foggers. One
## density control scales them all.

var machines: Array = []


func build(stage_x: float) -> void:
	for c in get_children():
		c.queue_free()
	machines.clear()
	var spots := [
		[Vector3(stage_x + 3.0, 0.4, -10.0), Vector3(-0.2, 1.0, 0.3)],   # downstage L
		[Vector3(stage_x + 3.0, 0.4, 10.0), Vector3(-0.2, 1.0, -0.3)],   # downstage R
		[Vector3(stage_x - 5.0, 0.4, -8.0), Vector3(0.3, 1.0, 0.2)],     # upstage L
		[Vector3(stage_x - 5.0, 0.4, 8.0), Vector3(0.3, 1.0, -0.2)],     # upstage R
		[Vector3(stage_x - 1.0, 0.4, 0.0), Vector3(0.1, 1.0, 0.0)],      # centre
	]
	for s in spots:
		var m := SmokeMachine.new()
		add_child(m)
		m.setup(s[0], s[1])
		machines.append(m)


func set_density(v: float) -> void:
	for m in machines:
		m.set_amount(v)
