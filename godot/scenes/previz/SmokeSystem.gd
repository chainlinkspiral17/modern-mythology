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
		# SCATTERED across the stage + front (varied X and Z, radiating drift) so
		# the low haze fills a broad field instead of piling into a line/"hotdog"
		spots = [
			[Vector3(stage_x - 3.0, 1.2, -9.0), Vector3(0.5, 0.05, 0.5)],
			[Vector3(stage_x + 2.0, 1.0, -4.0), Vector3(0.7, 0.05, 0.3)],
			[Vector3(stage_x + 8.0, 1.4, -8.0), Vector3(0.9, 0.05, 0.4)],
			[Vector3(stage_x - 1.0, 1.6, 0.0), Vector3(0.6, 0.05, 0.0)],
			[Vector3(stage_x + 10.0, 1.2, 2.0), Vector3(0.9, 0.05, -0.2)],
			[Vector3(stage_x - 3.0, 1.2, 9.0), Vector3(0.5, 0.05, -0.5)],
			[Vector3(stage_x + 2.0, 1.0, 5.0), Vector3(0.7, 0.05, -0.3)],
			[Vector3(stage_x + 8.0, 1.4, 8.0), Vector3(0.9, 0.05, -0.4)],
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
