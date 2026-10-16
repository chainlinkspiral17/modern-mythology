extends Control
class_name SlowstickDiorama
## Shallow 3D diorama for a slowstick: a SubViewport holding a slow-turning
## low-poly, UNTEXTURED hero object under Light3D. Placed behind a stick's
## UI, tinted by the host's SlowstickLook preset, it reads as that studio's
## material — depth without leaving the silkscreen look.
##
## Feeds off the Meshy pipeline: point `glb_path` at a normalized
## assets/3d/... GLB (the untextured T2 hero). With no GLB it builds a
## procedural "resonator" placeholder so the diorama works before any asset
## is generated — the pilot renders today, the real object drops in later.
##
## It is the PICTURE, not HUD: joins "world_render" (F4 leaves it) and its
## container sets `show_behind_parent` so it renders behind a host Control's
## own _draw (e.g. Basilica's wireframe) rather than over it.
##
## Usage — standalone (this file's demo scene auto-builds):
##   attach to a Control; auto_build calls build() in _ready.
## Usage — behind a stick:
##   var d := SlowstickDiorama.new()
##   d.build("res://assets/3d/locales/tuner.glb", Color(0.72,0.80,0.86))
##   add_child(d)   # add before the UI; call move_child(d,0) if needed

@export var auto_build: bool = true
@export var glb_path: String = ""
@export var accent: Color = Color(0.74, 0.80, 0.86)
@export var spin_speed: float = 0.22          # rad/sec, slow

const VP_SIZE := Vector2i(640, 360)

var _vp: SubViewport = null
var _pivot: Node3D = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_to_group("world_render")
	if auto_build:
		build(glb_path, accent)


func build(path: String = "", tint: Color = Color(0.74, 0.80, 0.86)) -> void:
	for c in get_children():
		c.queue_free()

	var cont := SubViewportContainer.new()
	cont.stretch = true
	cont.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	cont.mouse_filter = Control.MOUSE_FILTER_IGNORE
	cont.show_behind_parent = true          # render behind a host's _draw
	add_child(cont)

	_vp = SubViewport.new()
	_vp.size = VP_SIZE
	_vp.transparent_bg = false
	_vp.msaa_3d = Viewport.MSAA_DISABLED    # keep the chunky low-fi edges
	cont.add_child(_vp)

	# Environment — dark void + soft ambient so unlit faces aren't black.
	var we := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.03, 0.035, 0.05)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.42, 0.46, 0.52)
	env.ambient_light_energy = 0.55
	we.environment = env
	_vp.add_child(we)

	# Camera, slightly above, looking at the object's midriff.
	var cam := Camera3D.new()
	cam.position = Vector3(0.0, 1.2, 4.2)
	cam.look_at_from_position(cam.position, Vector3(0.0, 0.55, 0.0), Vector3.UP)
	_vp.add_child(cam)

	# Key + fill (the lighting-playbook three-light spirit, minus the rim).
	var key := DirectionalLight3D.new()
	key.rotation_degrees = Vector3(-42.0, -35.0, 0.0)
	key.light_energy = 1.15
	_vp.add_child(key)
	var fill := DirectionalLight3D.new()
	fill.rotation_degrees = Vector3(-8.0, 140.0, 0.0)
	fill.light_energy = 0.35
	fill.light_color = Color(0.70, 0.78, 0.92)
	_vp.add_child(fill)

	_pivot = Node3D.new()
	_vp.add_child(_pivot)
	_pivot.add_child(_load_or_placeholder(path, tint))


func _load_or_placeholder(path: String, tint: Color) -> Node3D:
	if path != "" and ResourceLoader.exists(path):
		var res: Variant = load(path)
		if res is PackedScene:
			return (res as PackedScene).instantiate()
		push_warning("[SlowstickDiorama] %s is not a PackedScene; using placeholder" % path)
	return _placeholder(tint)


# A procedural "resonator" — stacked torus rings around a core. Untextured,
# one flat material; stands in for a real Meshy hero until one is dropped in.
func _placeholder(tint: Color) -> Node3D:
	var root := Node3D.new()
	var mat := StandardMaterial3D.new()
	mat.albedo_color = tint
	mat.roughness = 0.85
	mat.metallic = 0.0
	for i in range(3):
		var ring := MeshInstance3D.new()
		var tm := TorusMesh.new()
		tm.inner_radius = 0.50 + float(i) * 0.28
		tm.outer_radius = tm.inner_radius + 0.12
		tm.rings = 10
		tm.ring_segments = 16
		ring.mesh = tm
		ring.material_override = mat
		ring.rotation_degrees = Vector3(90.0, 0.0, float(i) * 22.0)
		ring.position = Vector3(0.0, float(i) * 0.18, 0.0)
		root.add_child(ring)
	var core := MeshInstance3D.new()
	var sm := SphereMesh.new()
	sm.radial_segments = 12
	sm.rings = 8
	sm.radius = 0.32
	sm.height = 0.64
	core.mesh = sm
	core.material_override = mat
	core.position = Vector3(0.0, 0.36, 0.0)
	root.add_child(core)
	return root


func set_glb(path: String) -> void:
	build(path, accent)


func _process(delta: float) -> void:
	if _pivot != null:
		_pivot.rotate_y(spin_speed * delta)
