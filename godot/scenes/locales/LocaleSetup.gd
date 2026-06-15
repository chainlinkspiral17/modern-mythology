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
	# Commercial cluster — fuel pumps, canopy columns, plate-glass
	# storefront frames, building posts/foundations, cooler doors,
	# parking-lot curb stops.
	"Post", "Pump", "Pylon", "Slab", "Mullion", "CanopyCol",
	"Foundation", "Cooler", "Aisle", "Xerox", "CurbStop",
	"Register", "FlagPole_Base", "PylonPole", "Plinth", "Plaza",
	# Outdoor locales — heightmap terrain meshes
	"Terrain", "Ground", "Lawn",
]


func _ready() -> void:
	var mat: Material = _make_material()
	var meshes := _collect_mesh_instances(self)
	var applied := 0
	var collided := 0
	var sign_panels_n: Array = []
	var sign_panels_s: Array = []
	var boat_panels: Array = []
	var ot_plaque_panels: Array = []
	var ot_park_sign_panels: Array = []
	var kwik_stop_signs: Array = []
	var nexcorp_signs: Array = []
	var nexcorp_pylon_signs: Array = []
	var flag_plaque_panels: Array = []
	var cosmic_comics_signs: Array = []
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
		elif "OT_Plaque" in mi.name:
			ot_plaque_panels.append(mi)
		elif "OTPark_SignLetters" in mi.name:
			ot_park_sign_panels.append(mi)
		elif "OTPark_ArchInscription" in mi.name:
			ot_park_sign_panels.append(mi)
		elif "KwikStop_SignPanel" in mi.name:
			kwik_stop_signs.append(mi)
		elif "NexCorpGG_SignPanel" in mi.name:
			nexcorp_signs.append(mi)
		elif "NexCorpGG_PylonSign" in mi.name:
			nexcorp_pylon_signs.append(mi)
		elif "OTPark_FlagPlaque" in mi.name:
			flag_plaque_panels.append(mi)
		elif "CosmicComics_SignPanel" in mi.name:
			cosmic_comics_signs.append(mi)
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
	# OT statue brass plaque — faces SOUTH (Blender -Y → Godot +Z)
	# Text: "OLIVER TREE · 1993-2026" in cream serif on brass.
	# Plaque text: pixel_size 0.004 → 0.006 (text was too small to
	# render at the previous size — Label3D dropped below the
	# pixel-per-glyph threshold). Offset 0.025 → 0.05 so the text
	# sits clearly in front of the plaque face, not z-fighting.
	for panel in ot_plaque_panels:
		_attach_text_label(panel,
						Vector3(0, 0, 0.05),
						Vector3(0, 0, 1),
						"OLIVER TREE\n1993 – 2026",
						0.006,
						Color(0.94, 0.88, 0.72, 1.0),
						Color(0.12, 0.08, 0.04, 1.0))
	# Park entry sign — same treatment.
	for panel in ot_park_sign_panels:
		_attach_text_label(panel,
						Vector3(0, 0, 0.05),
						Vector3(0, 0, 1),
						"The Oliver Tree\nMemorial Park",
						0.007,
						Color(0.32, 0.22, 0.16, 1.0),
						Color(0.86, 0.82, 0.70, 1.0))
	# Convenience-store roof signs — face SOUTH (Blender -Y →
	# Godot +Z). Kwik Stop in cream on red, NexCorp Gas & Go in
	# white on blue.
	for panel in kwik_stop_signs:
		_attach_text_label(panel,
						Vector3(0, 0, 0.10),
						Vector3(0, 0, 1),
						"KWIK STOP",
						0.018,
						Color(0.98, 0.95, 0.86, 1.0),
						Color(0.40, 0.05, 0.05, 1.0))
	for panel in nexcorp_signs:
		_attach_text_label(panel,
						Vector3(0, 0, 0.10),
						Vector3(0, 0, 1),
						"NexCorp\nGas & Go",
						0.013,
						Color(0.98, 0.98, 0.96, 1.0),
						Color(0.08, 0.12, 0.22, 1.0))
	for panel in cosmic_comics_signs:
		_attach_text_label(panel,
						Vector3(0, 0, 0.10),
						Vector3(0, 0, 1),
						"COSMIC\nCOMICS",
						0.015,
						Color(0.95, 0.85, 0.30, 1.0),
						Color(0.10, 0.02, 0.10, 1.0))
	for panel in nexcorp_pylon_signs:
		_attach_text_label(panel,
						Vector3(0, 0, 0.12),
						Vector3(0, 0, 1),
						"NEXCORP",
						0.014,
						Color(0.98, 0.98, 0.96, 1.0),
						Color(0.08, 0.12, 0.22, 1.0))
	# Flag pole base plaque — explains the half-mast position in
	# memory of Oliver Tree. Plaque is south-facing: Blender -Y
	# face → Godot +Z face after glTF axis swap.
	for panel in flag_plaque_panels:
		_attach_text_label(panel,
						Vector3(0, 0, 0.03),
						Vector3(0, 0, 1),
						"AT HALF-MAST\nIN MEMORY OF\nOLIVER TREE",
						0.002,
						Color(0.95, 0.88, 0.72, 1.0),
						Color(0.10, 0.06, 0.02, 1.0))


func _attach_text_label(panel: MeshInstance3D, world_face_offset: Vector3,
						face_normal: Vector3, text: String,
						pixel_size: float = 0.010,
						text_color: Color = Color(0.94, 0.88, 0.72, 1.0),
						outline_color: Color = Color(0.12, 0.08, 0.04, 1.0)) -> void:
	"""Generic text-attached-to-panel helper. Same orientation logic
	as _attach_sign_label but with configurable text + colours.
	Used by the OT plaque + park sign + any other Label3D panel
	that doesn't want the cursive D'Ambrosio's defaults."""
	var label := Label3D.new()
	label.text = text
	label.font_size = 64
	label.outline_size = 6
	label.modulate = text_color
	label.outline_modulate = outline_color
	label.no_depth_test = false
	label.shaded = false
	label.double_sided = true
	label.alpha_cut = Label3D.ALPHA_CUT_OPAQUE_PREPASS
	label.pixel_size = pixel_size
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	panel.add_child(label)
	var panel_centre := panel.global_transform.origin + panel.get_aabb().get_center()
	var pos := panel_centre + world_face_offset
	var fwd: Vector3 = face_normal.normalized()
	var world_up := Vector3(0, 1, 0)
	if abs(fwd.dot(world_up)) > 0.95:
		world_up = Vector3(0, 0, 1)
	var right: Vector3 = world_up.cross(fwd).normalized()
	var up: Vector3 = fwd.cross(right).normalized()
	label.global_transform = Transform3D(Basis(right, up, fwd), pos)


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
