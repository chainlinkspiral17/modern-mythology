class_name SmokeMachine
extends GPUParticles3D
## Slow drifting stage haze/smoke — big soft billboards that catch the light
## beams. Separate from the WorldEnvironment volumetric fog so there's visible,
## moving smoke even in a static frame. set_haze(0..1) scales the density live.

func setup(stage_x: float, width: float) -> void:
	amount = 90
	lifetime = 10.0
	preprocess = 6.0
	explosiveness = 0.0
	randomness = 0.6
	fixed_fps = 30
	position = Vector3(stage_x + 2.0, 1.0, 0.0)
	visibility_aabb = AABB(Vector3(-40.0, -4.0, -40.0), Vector3(90.0, 50.0, 80.0))

	var pm := ParticleProcessMaterial.new()
	pm.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	pm.emission_box_extents = Vector3(8.0, 1.0, width * 0.5)
	pm.direction = Vector3(0.3, 1.0, 0.0)
	pm.spread = 25.0
	pm.initial_velocity_min = 0.3
	pm.initial_velocity_max = 1.2
	pm.gravity = Vector3(0.15, 0.25, 0.0)
	pm.scale_min = 2.5
	pm.scale_max = 5.5
	pm.color = Color(0.75, 0.75, 0.8, 0.1)
	process_material = pm

	var quad := QuadMesh.new()
	quad.size = Vector2(5.0, 5.0)
	var dm := StandardMaterial3D.new()
	dm.albedo_color = Color(0.8, 0.8, 0.85, 0.09)
	dm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	dm.blend_mode = BaseMaterial3D.BLEND_MODE_MIX
	dm.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	dm.shading_mode = BaseMaterial3D.SHADING_MODE_PER_PIXEL   # catches light/beams
	dm.cull_mode = BaseMaterial3D.CULL_DISABLED
	quad.material = dm
	draw_pass_1 = quad

	emitting = true


func set_haze(v: float) -> void:
	amount_ratio = clampf(v, 0.0, 1.0)
