class_name SmokeSystem
extends Node3D
## A bank of fog/smoke machines around the stage. build(stage_x, low):
##   low = false → rising SMOKE from 5 points (downstage L/R, upstage L/R, centre)
##   low = true  → low stage FOG from 6 points along the deck front (dry-ice pool)
## One density control scales them all. Lit by the rig (per-pixel particles) so
## the beams carve through the haze.

var machines: Array = []
var _low := false


func build(stage_x: float, low := false) -> void:
	for c in get_children():
		c.queue_free()
	machines.clear()
	_low = low
	var spots: Array
	if low:
		# emit from the LIP of the stage and roll outward over the front rows
		spots = [
			[Vector3(stage_x + 5.0, 1.4, -10.0), Vector3(0.8, -0.1, 0.2)],
			[Vector3(stage_x + 5.0, 1.4, -6.0), Vector3(0.9, -0.1, 0.1)],
			[Vector3(stage_x + 5.0, 1.4, -2.0), Vector3(0.9, -0.1, 0.0)],
			[Vector3(stage_x + 5.0, 1.4, 2.0), Vector3(0.9, -0.1, 0.0)],
			[Vector3(stage_x + 5.0, 1.4, 6.0), Vector3(0.9, -0.1, -0.1)],
			[Vector3(stage_x + 5.0, 1.4, 10.0), Vector3(0.8, -0.1, -0.2)],
		]
	else:
		spots = [
			[Vector3(stage_x + 3.0, 1.0, -10.0), Vector3(-0.2, 1.0, 0.3)],
			[Vector3(stage_x + 3.0, 1.0, 10.0), Vector3(-0.2, 1.0, -0.3)],
			[Vector3(stage_x - 5.0, 1.0, -8.0), Vector3(0.3, 1.0, 0.2)],
			[Vector3(stage_x - 5.0, 1.0, 8.0), Vector3(0.3, 1.0, -0.2)],
			[Vector3(stage_x - 1.0, 1.0, 0.0), Vector3(0.1, 1.0, 0.0)],
		]
	for s in spots:
		var m := SmokeMachine.new()
		add_child(m)
		m.setup(s[0], s[1], low)
		machines.append(m)


func set_density(v: float) -> void:
	for m in machines:
		m.set_emit_ratio(v)
