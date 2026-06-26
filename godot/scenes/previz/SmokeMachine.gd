class_name SmokeMachine
extends GPUParticles3D
## One fog/smoke machine. Soft RADIAL puff texture (not hard quads) so particles
## read as wispy fog, not "glass panes", and stay visible without being heavy.
##   low = false → rising stage SMOKE (drifts up, swirls)
##   low = true  → low-lying stage FOG (hugs the deck, spreads outward, dry-ice)
## Place several (see SmokeSystem). Density is live via amount_ratio.

func setup(pos: Vector3, drift: Vector3, low := false) -> void:
	lifetime = 13.0
	preprocess = 8.0
	randomness = 0.9
	fixed_fps = 24
	position = pos
	visibility_aabb = AABB(Vector3(-60.0, -5.0, -60.0), Vector3(120.0, 60.0, 120.0))

	var pm := ParticleProcessMaterial.new()
	pm.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
	pm.turbulence_enabled = true
	pm.turbulence_noise_scale = 1.8

	var quad := QuadMesh.new()
	var dm := StandardMaterial3D.new()
	dm.albedo_texture = _soft_puff()
	dm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	dm.blend_mode = BaseMaterial3D.BLEND_MODE_MIX
	dm.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	dm.shading_mode = BaseMaterial3D.SHADING_MODE_PER_PIXEL
	dm.cull_mode = BaseMaterial3D.CULL_DISABLED
	# faint self-emission so the haze is visible even before the beams hit it
	dm.emission_enabled = true
	dm.emission = Color(0.45, 0.45, 0.47)   # white self-light so smoke reads white, not a dark veil
	dm.emission_energy_multiplier = 1.4

	if low:
		# ground-hugging fog: a low pool that stays near the deck (doesn't flood the venue)
		amount = 90
		lifetime = 8.0
		pm.emission_sphere_radius = 2.0
		pm.direction = Vector3(drift.x, 0.08, drift.z)
		pm.spread = 38.0
		pm.initial_velocity_min = 0.2
		pm.initial_velocity_max = 0.8
		pm.gravity = Vector3(0.0, -0.05, 0.0)
		pm.scale_min = 2.6
		pm.scale_max = 5.0
		pm.turbulence_noise_strength = 0.5
		pm.color = Color(0.9, 0.91, 0.94, 1.0)
		quad.size = Vector2(6.0, 6.0)
		dm.albedo_color = Color(0.92, 0.93, 0.96, 0.95)
		dm.emission = Color(0.72, 0.72, 0.75)   # bright white deck fog
		dm.emission_energy_multiplier = 1.6
	else:
		# rising smoke: drifts up, swirls
		amount = 96
		pm.emission_sphere_radius = 2.4
		pm.direction = drift
		pm.spread = 55.0
		pm.initial_velocity_min = 0.2
		pm.initial_velocity_max = 0.9
		pm.gravity = Vector3(0.0, 0.12, 0.0)
		pm.scale_min = 2.2
		pm.scale_max = 5.0
		pm.turbulence_noise_strength = 0.7
		pm.color = Color(0.85, 0.85, 0.9, 1.0)
		quad.size = Vector2(6.0, 6.0)
		dm.albedo_color = Color(0.85, 0.85, 0.9, 0.85)

	process_material = pm
	quad.material = dm
	draw_pass_1 = quad
	emitting = true


## 128px soft circle: white centre fading to transparent at the edge.
func _soft_puff() -> GradientTexture2D:
	var grad := Gradient.new()
	grad.set_color(0, Color(1.0, 1.0, 1.0, 1.0))
	grad.set_color(1, Color(1.0, 1.0, 1.0, 0.0))
	var gt := GradientTexture2D.new()
	gt.gradient = grad
	gt.width = 128
	gt.height = 128
	gt.fill = GradientTexture2D.FILL_RADIAL
	gt.fill_from = Vector2(0.5, 0.5)
	gt.fill_to = Vector2(1.0, 0.5)
	return gt


func set_amount(v: float) -> void:
	amount_ratio = clampf(v, 0.0, 1.0)
