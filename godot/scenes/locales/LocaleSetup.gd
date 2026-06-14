# LocaleSetup.gd
# ════════════════════════════════════════════════════════════════
# COMMUNITY PLANNED · runtime setup for the vol5 chapter locales.
#
# Attach to the Geometry node inside a locale scene (sibling of
# LightSetups and PostProcess). On _ready() it:
#
#   1. Walks every MeshInstance3D and applies a StandardMaterial3D
#      that reads vertex COLOR as albedo and is lit by the scene's
#      real-time Light3D nodes. (Unlike the Cathedral's gouraud
#      bake — locales use dynamic lighting per mood.)
#
#   2. Identifies architectural meshes by name substring (Floor /
#      Ceiling / Wall / Counter / Booth / Bar / Kitchen / Hall /
#      Card / Door / Porch / Stool / etc.) and creates a
#      StaticBody3D + trimesh collision sibling for each so the
#      player can walk on the floor and bump into walls.
#
# Drop-in for every locale scene. Compatible with LightController
# on the root for mood switching.
# ════════════════════════════════════════════════════════════════

extends Node3D

@export var use_palette_shader: bool = false
@export var palette_shader: Shader = null
@export var add_colliders: bool = true
@export var albedo_brightness: float = 1.0
@export var ps2_grid: float = 640.0
@export var wobble_amount: float = 0.0

# Mesh names that should get collision. Locale-broad — covers
# walls, floors, counters, large furniture. Skip small props.
const COLLIDER_NAME_HINTS: Array[String] = [
    "Floor", "Ceiling", "Wall", "Counter", "Booth", "Bar", "Kitchen",
    "Hall", "CardWall", "Door", "Porch", "Stool", "Pole", "Partition",
    "Crate", "Shelf", "Loom", "Tower",
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
    print("[LocaleSetup · %s] applied material to %d meshes · added %d colliders" % [get_parent().name, applied, collided])


func _make_material() -> Material:
    if use_palette_shader and palette_shader != null:
        var sm := ShaderMaterial.new()
        sm.shader = palette_shader
        sm.set_shader_parameter("ps2_grid", ps2_grid)
        sm.set_shader_parameter("wobble_amount", wobble_amount)
        sm.set_shader_parameter("albedo_boost", albedo_brightness)
        return sm
    # Fallback: standard material that uses vertex color as albedo
    var m := StandardMaterial3D.new()
    m.vertex_color_use_as_albedo = true
    m.albedo_color = Color(albedo_brightness, albedo_brightness, albedo_brightness, 1.0)
    m.roughness = 1.0
    m.metallic = 0.0
    return m


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
    var parent := mi.get_parent()
    if parent == null:
        return
    var sibling_name := mi.name + "_StaticBody"
    for sib in parent.get_children():
        if sib.name == sibling_name:
            return
    var body := StaticBody3D.new()
    body.name = sibling_name
    parent.add_child(body)
    body.global_transform = mi.global_transform
    var shape := CollisionShape3D.new()
    if mi.mesh != null:
        var concave := mi.mesh.create_trimesh_shape()
        if concave != null:
            shape.shape = concave
            body.add_child(shape)
