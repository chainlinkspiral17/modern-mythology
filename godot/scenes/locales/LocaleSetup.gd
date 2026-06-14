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

# Thick Italian/French brush-script for D'Ambrosio's signage — fits
# the creole boat-life vibe the reference concept art is pushing.
# Lobster is OFL-licensed; designer Pablo Impallari.
const CURSIVE_FONT: Font = preload("res://resources/fonts/Lobster-Regular.ttf")

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
	var sign_panels_n: Array = []
	var sign_panels_s: Array = []
	var boat_panels: Array = []
	for mi in meshes:
		mi.material_override = mat
		applied += 1
		if add_colliders and _should_have_collider(mi.name):
			_ensure_static_collider(mi)
			collided += 1
		# Collect sign panel meshes so we can attach Label3D text to them
		if "Sign_Panel_N" in mi.name:
			sign_panels_n.append(mi)
		elif "Sign_Panel_S" in mi.name:
			sign_panels_s.append(mi)
		elif "BoatSign_Panel" in mi.name:
			boat_panels.append(mi)
	print("[LocaleSetup · %s] applied material to %d meshes · added %d colliders" % [get_parent().name, applied, collided])
	# Attach real Label3D text to the sign panels.
	#
	# COORDINATE FRAME GOTCHA (cost us two iterations):
	# The Blender build script writes everything Z-up (X east, Y north,
	# Z up). The default glTF export remaps Blender +Y → Godot -Z and
	# Blender +Z → Godot +Y, so by the time the GLB lands in this
	# runtime scene, Godot's world-up is +Y, not +Z.
	#
	# The face_normal and offset vectors below are GODOT WORLD COORDS:
	#   · Sign_Panel_N — Blender +Y face becomes Godot -Z face
	#   · Sign_Panel_S — Blender -Y face becomes Godot +Z face
	#   · BoatSign_Panel — Blender -X face is preserved (-X in Godot)
	#
	# _attach_sign_label uses world_up = (0, 1, 0). When we passed
	# (0, 0, 1) the labels came out rotated 90° around the panel's
	# face axis (text reading vertically along the panel height
	# instead of horizontally along the panel width).
	# pixel_size dialed down for the Lobster cursive — Lobster's
	# strokes are wider per character than the default sans-serif,
	# so the physical font is shrunk to keep text inside the panel
	# boundaries. Pole 6.4 × 2m → 0.008. Boat 7.6 × 2.4m → 0.011.
	for panel in sign_panels_n:
		_attach_sign_label(panel, Vector3(0, 0, -0.10), Vector3(0, 0, -1), 0.008)
	for panel in sign_panels_s:
		_attach_sign_label(panel, Vector3(0, 0,  0.10), Vector3(0, 0,  1), 0.008)
	for panel in boat_panels:
		_attach_sign_label(panel, Vector3(-0.10, 0, 0), Vector3(-1, 0, 0), 0.011)


func _attach_sign_label(panel: MeshInstance3D, world_face_offset: Vector3, face_normal: Vector3, pixel_size: float = 0.010) -> void:
	"""Create a Label3D child of the given panel showing 'D'Ambrosio's'
	at the panel's WORLD center + face offset, oriented so its front
	(+Z) points in face_normal."""
	var label := Label3D.new()
	label.text = "D'Ambrosio's"
	label.font = CURSIVE_FONT
	# Lobster reads ~75% the width of a sans at the same point size,
	# so the font_size bump from 96 → 128 keeps the text filling the
	# panel. Outline thickened too so the cursive strokes survive
	# the lithograph post-process at parking-lot distance.
	label.font_size = 128
	label.outline_size = 10
	label.modulate = Color(0.98, 0.18, 0.20, 1.0)
	label.outline_modulate = Color(0.08, 0.0, 0.0, 1.0)
	label.no_depth_test = false
	label.shaded = false
	label.double_sided = true
	label.alpha_cut = Label3D.ALPHA_CUT_OPAQUE_PREPASS
	label.pixel_size = pixel_size
	panel.add_child(label)
	var panel_centre := panel.global_transform.origin + panel.get_aabb().get_center()
	var pos := panel_centre + world_face_offset
	# Build basis: +Z (label front) → face_normal, +Y (label up) →
	# Godot world +Y (the real up axis at runtime). The degenerate
	# case (face_normal IS straight up/down) shouldn't happen for
	# vertical sign panels but we fall back to +Z to stay safe.
	var fwd: Vector3 = face_normal.normalized()
	var world_up := Vector3(0, 1, 0)
	if abs(fwd.dot(world_up)) > 0.95:
		world_up = Vector3(0, 0, 1)
	var right: Vector3 = world_up.cross(fwd).normalized()
	var up: Vector3 = fwd.cross(right).normalized()
	label.global_transform = Transform3D(Basis(right, up, fwd), pos)
	print("[LocaleSetup] sign label %s @ %s facing %s" % [panel.name, str(pos), str(fwd)])


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
