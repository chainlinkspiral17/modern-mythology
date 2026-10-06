# RoadScroller.gd
# ════════════════════════════════════════════════════════════════
# A car that is DRIVING, in a scene where nothing can move the car
# (2026-10-05, Miriam's Subaru — "moving west on a two-lane road
# through cane fields"). The wagon stays put; the passing world
# moves: every part whose name starts with one of `prefixes` slides
# toward the camera at `speed_mps` and wraps round the span, each
# part on its own, so the cane rows, the poles and the delineators
# keep streaming past the windows.
#
# It runs only while the active camera is INSIDE the car (within
# `inside_radius` of the scene origin) — when the director cuts to a
# marker elsewhere on the set (the county-line station), the world
# holds still. The car faces Godot -Z (Blender +Y), so the world
# moves toward +Z.
# ════════════════════════════════════════════════════════════════
extends Node

@export var interior_path: NodePath = NodePath("../Interior")
@export var speed_mps: float = 24.0
@export var span_min: float = -440.0
@export var span_max: float = 440.0
@export var inside_radius: float = 6.0
@export var prefixes: PackedStringArray = PackedStringArray(["Cane_", "Pole_", "Road_Delineator_"])
@export var skip_prefixes: PackedStringArray = PackedStringArray(["Pole_Wire_"])

var _parts: Array[Node3D] = []
var _centers: PackedFloat32Array = PackedFloat32Array()   # each part's own centre z (its origin is the scene's)


func _ready() -> void:
	call_deferred("_collect")


func _collect() -> void:
	_parts.clear()
	_centers.clear()
	var root: Node = get_node_or_null(interior_path)
	if root == null:
		return
	for n in root.find_children("*", "Node3D", true, false):
		var n3: Node3D = n as Node3D
		if n3 == null:
			continue
		var nm: String = String(n3.name)
		if _matches(nm, skip_prefixes) or not _matches(nm, prefixes):
			continue
		var c: float = 0.0
		var mi: MeshInstance3D = n3 as MeshInstance3D
		if mi != null:
			c = mi.get_aabb().get_center().z
		_parts.append(n3)
		_centers.append(c + n3.position.z)


func _matches(nm: String, list: PackedStringArray) -> bool:
	for p in list:
		if nm.begins_with(p):
			return true
	return false


func _process(delta: float) -> void:
	if _parts.is_empty():
		return
	var cam: Camera3D = get_viewport().get_camera_3d()
	if cam == null or cam.global_position.length() > inside_radius:
		return
	var step: float = speed_mps * delta
	var span: float = span_max - span_min
	for i in range(_parts.size()):
		var part: Node3D = _parts[i]
		var p: Vector3 = part.position
		p.z += step
		if _centers[i] + p.z > span_max:
			p.z -= span
		part.position = p
