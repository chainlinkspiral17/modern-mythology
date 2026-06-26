class_name SmokeMachine
extends GPUParticles3D
## One stage fog/smoke machine: many small, soft, turbulent billboards that read
## as drifting haze (not giant panes) and catch the light beams. Place several of
## these (see SmokeSystem) like real foggers. set density live via amount_ratio.

func setup(pos: Vector3, drift: Vector3) -> void:
	amount = 48
	lifetime = 12.0
	preprocess = 8.0
	randomness = 0.85
	fixed_fps = 24
	position = pos
	visibility_aabb = AABB(Vector3(-50.0, -5.0, -50.0), Vector3(100.0, 60.0, 100.0))

	var pm := ParticleProcessMaterial.new()
	pm.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
	pm.emission_sphere_radius = 1.5
	pm.direction = drift
	pm.spread = 45.0
	pm.initial_velocity_min = 0.2
	pm.initial_velocity_max = 0.9
	pm.gravity = Vector3(0.0, 0.12, 0.0)
	pm.scale_min = 0.9
	pm.scale_max = 2.2
	pm.turbulence_enabled = true
	pm.turbulence_noise_strength = 0.5
	pm.turbulence_noise_scale = 1.8
	pm.color = Color(0.8, 0.8, 0.85, 0.05)
	process_material = pm

	var quad := QuadMesh.new()
	quad.size = Vector2(2.2, 2.2)
	var dm := StandardMaterial3D.new()
	dm.albedo_color = Color(0.82, 0.82, 0.86, 0.05)   # low alpha → soft, layered
	dm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	dm.blend_mode = BaseMaterial3D.BLEND_MODE_MIX
	dm.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	dm.shading_mode = BaseMaterial3D.SHADING_MODE_PER_PIXEL   # tinted by the beams
	dm.cull_mode = BaseMaterial3D.CULL_DISABLED
	quad.material = dm
	draw_pass_1 = quad

	emitting = true


func set_amount(v: float) -> void:
	amount_ratio = clampf(v, 0.0, 1.0)
