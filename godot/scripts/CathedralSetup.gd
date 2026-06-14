# CathedralSetup.gd
# ════════════════════════════════════════════════════════════════
# COMMUNITY PLANNED · runtime setup for the Cathedral scene.
#
# Attach to the root Node3D of cathedral.tscn. On _ready():
#   1. Walks every MeshInstance3D descendant and applies the
#      gouraud_lambert.gdshader as material_override so the
#      vertex-baked Gouraud lighting actually shows.
#   2. Generates trimesh static bodies on the architectural
#      meshes (walls, floor, ceiling, etc.) so the player
#      doesn't fall through them.
#   3. Captures the player's capsule collision shape if missing.
#
# This script makes the scene self-setting-up — no manual material
# overrides or per-mesh collision steps needed in the editor.
# ════════════════════════════════════════════════════════════════

extends Node3D

@export var gouraud_shader: Shader = preload("res://assets/shaders/gouraud_lambert.gdshader")
@export var add_colliders: bool = true
@export var brightness: float = 2.0
@export var ambient_floor: float = 0.05
@export var saturation: float = 1.0
# Fall back to StandardMaterial3D + vertex-color-as-albedo if the
# custom shader path isn't working. This sidesteps Godot 4's
# occasional COLOR-passthrough oddities with unshaded shaders.
@export var use_standard_material: bool = true
@export var albedo_brightness: float = 2.2

# Mesh-name substrings that get static-body colliders. Walls + floor
# + ceiling + diorama platforms + workbench + BBS desk. Skip the
# small props (figurines, papers, etc.) — they shouldn't block the
# player.
const COLLIDER_NAME_HINTS: Array[String] = [
	"Floor", "Ceiling", "Wall", "Workbench", "BBS_Desk", "Diorama",
	"FreightDoor", "Partition", "Crate", "Strut",
]


func _ready() -> void:
	var mat: Material = _make_material()

	var meshes := _collect_mesh_instances(self)
	var applied := 0
	var collided := 0
	for mi in meshes:
		mi.material_override = mat
		applied += 1
		if add_colliders and _should_have_collider(mi.name):
			_ensure_static_collider(mi)
			collided += 1

	_ensure_player_capsule()

	var path: String = "standard" if use_standard_material else "gouraud_shader"
	print("[CathedralSetup] applied %s material to %d meshes · added %d colliders" % [path, applied, collided])


func _make_material() -> Material:
	if use_standard_material:
		# StandardMaterial3D with vertex_color_use_as_albedo — proven
		# path through Godot's standard renderer. Works with runtime
		# lighting (so the scene needs a directional/sun light).
		var m := StandardMaterial3D.new()
		m.vertex_color_use_as_albedo = true
		m.albedo_color = Color(albedo_brightness, albedo_brightness, albedo_brightness, 1.0)
		m.roughness = 1.0
		m.metallic = 0.0
		m.cull_mode = BaseMaterial3D.CULL_DISABLED   # see inside the warehouse box
		return m
	# Custom Gouraud shader path (unshaded; vertex bake IS the light)
	var sm := ShaderMaterial.new()
	sm.shader = gouraud_shader
	sm.set_shader_parameter("brightness", brightness)
	sm.set_shader_parameter("ambient_floor", ambient_floor)
	sm.set_shader_parameter("saturation", saturation)
	return sm


func _collect_mesh_instances(node: Node, acc: Array = []) -> Array:
	if node is MeshInstance3D:
		acc.append(node)
	for child in node.get_children():
		_collect_mesh_instances(child, acc)
	return acc


func _should_have_collider(mesh_name: String) -> bool:
	for hint in COLLIDER_NAME_HINTS:
		if hint in mesh_name:
			return true
	return false


func _ensure_static_collider(mi: MeshInstance3D) -> void:
	# If a StaticBody3D sibling already exists, skip
	var parent := mi.get_parent()
	if parent == null:
		return
	for sib in parent.get_children():
		if sib is StaticBody3D and sib.name == mi.name + "_StaticBody":
			return

	# Create a StaticBody3D as a sibling and add a trimesh collision shape
	var body := StaticBody3D.new()
	body.name = mi.name + "_StaticBody"
	parent.add_child(body)
	body.owner = get_tree().edited_scene_root if Engine.is_editor_hint() else null
	# Mirror the mesh's transform onto the static body so the collider lines up
	body.global_transform = mi.global_transform

	var shape := CollisionShape3D.new()
	var concave := mi.mesh.create_trimesh_shape() if mi.mesh != null else null
	if concave != null:
		shape.shape = concave
		body.add_child(shape)
		shape.owner = body.owner


func _ensure_player_capsule() -> void:
	var player := get_node_or_null("Player")
	if player == null:
		return
	var coll := player.get_node_or_null("CollisionShape3D") as CollisionShape3D
	if coll == null:
		coll = CollisionShape3D.new()
		coll.name = "CollisionShape3D"
		player.add_child(coll)
	if coll.shape == null:
		var caps := CapsuleShape3D.new()
		caps.radius = 0.30
		caps.height = 1.70
		coll.shape = caps
		# Place the capsule so its bottom is at the player's feet
		coll.position = Vector3(0, 0.85, 0)
		print("[CathedralSetup] added missing player capsule shape")
