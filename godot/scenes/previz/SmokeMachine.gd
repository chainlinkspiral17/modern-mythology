class_name SmokeMachine
extends GPUParticles3D
## One fog/smoke machine. Soft RADIAL puff texture (not hard quads) so particles
## read as wispy fog, not "glass panes", and stay visible without being heavy.
##   low = false → rising stage SMOKE (drifts up, swirls)
##   low = true  → low-lying stage FOG (hugs the deck, spreads outward, dry-ice)
## Place several (see SmokeSystem). Density is live via amount_ratio.

func setup(pos: Vector3, drift: Vector3, low := false) -> void:
	lifetime = 14.0
	preprocess = 12.0
	randomness = 0.45            # less lifetime jitter → no random pop in/out
	fixed_fps = 30
	position = pos
	visibility_aabb = AABB(Vector3(-60.0, -5.0, -60.0), Vector3(120.0, 60.0, 120.0))

	var pm := ParticleProcessMaterial.new()
	pm.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
	pm.turbulence_enabled = true
	pm.turbulence_noise_scale = 0.9   # broad, slow swirls (not tight chunks)
	# real fog/smoke behaviour: each puff fades IN, lingers, fades OUT (no pop)
	# and GROWS as it ages, so overlapping puffs merge into a continuous volume
	pm.color_ramp = _alpha_ramp()
	pm.scale_curve = _grow_curve()
	pm.damping_min = 0.2
	pm.damping_max = 0.6              # drag → it slows and hangs in the air, lingering

	var quad := QuadMesh.new()
	var dm := StandardMaterial3D.new()
	dm.albedo_texture = _soft_puff()
	dm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	dm.blend_mode = BaseMaterial3D.BLEND_MODE_MIX
	dm.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	dm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED   # always white — never darkens in shadow
	dm.cull_mode = BaseMaterial3D.CULL_DISABLED
	dm.emission_enabled = false

	if low:
		# REAL low fog (dry-ice/CO2): a slow, dense, ground-hugging blanket that
		# spills off the lip and rolls outward, lingering low. Many big, soft,
		# low-opacity puffs overlap into one continuous bank.
		amount = 220
		lifetime = 18.0
		pm.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
		pm.emission_box_extents = Vector3(3.5, 0.4, 4.0)   # born along the lip, not a point
		pm.direction = drift                  # outward off the lip
		pm.spread = 35.0
		pm.flatness = 0.85                     # keeps motion horizontal → hugs the deck
		pm.initial_velocity_min = 0.2
		pm.initial_velocity_max = 0.8          # creeps slowly so it lingers
		pm.gravity = Vector3(0.0, -0.05, 0.0)  # sinks and pools low
		pm.scale_min = 4.5
		pm.scale_max = 8.0                      # big overlapping puffs blend together
		pm.turbulence_noise_strength = 0.6
		quad.size = Vector2(9.0, 9.0)
		dm.albedo_color = Color(0.95, 0.95, 0.97, 0.22)  # low alpha → reads as a soft bank, not hard discs
	else:
		# REAL stage smoke (hazer/fogger plume): a soft column that rises slowly,
		# expands and swirls, thinning as it climbs into the rig.
		amount = 150
		lifetime = 16.0
		pm.emission_sphere_radius = 1.6
		pm.direction = drift
		pm.spread = 40.0
		pm.initial_velocity_min = 0.15
		pm.initial_velocity_max = 0.7
		pm.gravity = Vector3(0.0, 0.18, 0.0)   # buoyant — drifts up
		pm.scale_min = 3.0
		pm.scale_max = 6.5
		pm.turbulence_noise_strength = 0.85
		quad.size = Vector2(7.5, 7.5)
		dm.albedo_color = Color(0.9, 0.9, 0.93, 0.26)

	process_material = pm
	quad.material = dm
	draw_pass_1 = quad
	emitting = true


## 128px soft circle: gentle gaussian-ish falloff (very feathered edge) so puffs
## blend instead of reading as hard-edged discs.
func _soft_puff() -> GradientTexture2D:
	var grad := Gradient.new()
	grad.set_color(0, Color(1.0, 1.0, 1.0, 1.0))
	grad.set_color(1, Color(1.0, 1.0, 1.0, 0.0))
	grad.add_point(0.35, Color(1.0, 1.0, 1.0, 0.55))
	grad.add_point(0.7, Color(1.0, 1.0, 1.0, 0.12))   # long soft tail → feathered
	var gt := GradientTexture2D.new()
	gt.gradient = grad
	gt.width = 128
	gt.height = 128
	gt.fill = GradientTexture2D.FILL_RADIAL
	gt.fill_from = Vector2(0.5, 0.5)
	gt.fill_to = Vector2(1.0, 0.5)
	return gt


## Alpha over a particle's lifetime: fade IN, hold, fade OUT — no pop in/out.
func _alpha_ramp() -> GradientTexture1D:
	var g := Gradient.new()
	g.set_color(0, Color(1.0, 1.0, 1.0, 0.0))   # born invisible
	g.set_color(1, Color(1.0, 1.0, 1.0, 0.0))   # dies invisible
	g.add_point(0.2, Color(1.0, 1.0, 1.0, 1.0))
	g.add_point(0.6, Color(1.0, 1.0, 1.0, 1.0))
	var t := GradientTexture1D.new()
	t.gradient = g
	return t


## Scale over lifetime: start smaller, grow as it ages so puffs expand and merge.
func _grow_curve() -> CurveTexture:
	var c := Curve.new()
	c.add_point(Vector2(0.0, 0.45))
	c.add_point(Vector2(1.0, 1.0))
	var t := CurveTexture.new()
	t.curve = c
	return t


# NOTE: don't name this set_amount — that overrides GPUParticles3D's native
# set_amount(int) and fails to compile. set_emit_ratio drives amount_ratio.
func set_emit_ratio(v: float) -> void:
	amount_ratio = clampf(v, 0.0, 1.0)
