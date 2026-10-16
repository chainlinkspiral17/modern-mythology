// portrait_skin.gdshader — the hero portraits' material (2026-10-13).
//
// Meshy's hero textures carry their own painted shading: near-black eye
// sockets, dark lip creases, shadowed jaw lines. Lit again by the portrait
// rig that reads as raccoon eyes and a gash for a mouth (the user: "weird
// ugly visual artifacts that look like misshapen lips or facial features").
// This replaces the GLB's StandardMaterial on portraits only (Portrait3D
// builds it; locales keep the screen-space-only rule):
//   - LIFT: a curve that raises the darkest albedo most and leaves the
//     highlights, so painted shadows open without washing the skin;
//   - the Meshy normal map at a reduced depth (full strength is noise at
//     portrait range); no emission (Meshy's map lights random patches);
//   - a wrap diffuse for a soft terminator, matte, almost no specular.
// Per-character values come from Portrait3D.CHARACTER_SHADING.
shader_type spatial;
render_mode diffuse_lambert_wrap, specular_schlick_ggx, cull_back;

uniform sampler2D albedo_tex : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D normal_tex : hint_normal, filter_linear_mipmap_anisotropic, repeat_enable;
uniform bool has_normal = false;
uniform float normal_depth : hint_range(0.0, 1.0) = 0.35;
uniform float lift : hint_range(0.0, 1.5) = 0.45;        // shadow lift strength
uniform float lift_knee : hint_range(0.1, 0.9) = 0.45;   // above this luminance the lift fades out
uniform float sat : hint_range(0.0, 1.6) = 1.0;
uniform vec4 tint : source_color = vec4(1.0);
uniform float specular_amt : hint_range(0.0, 0.5) = 0.10;

void fragment() {
	vec4 a = texture(albedo_tex, UV);
	vec3 c = a.rgb;
	float lum = dot(c, vec3(0.299, 0.587, 0.114));
	// gamma lift (brightens darks far more than mids), faded out above the knee
	vec3 lifted = pow(max(c, vec3(0.0)), vec3(1.0 / (1.0 + lift)));
	c = mix(lifted, c, smoothstep(lift_knee * 0.5, lift_knee + 0.25, lum));
	float l2 = dot(c, vec3(0.299, 0.587, 0.114));
	c = mix(vec3(l2), c, sat);
	ALBEDO = c * tint.rgb;
	ROUGHNESS = 1.0;
	METALLIC = 0.0;
	SPECULAR = specular_amt;
	if (has_normal) {
		NORMAL_MAP = texture(normal_tex, UV).rgb;
		NORMAL_MAP_DEPTH = normal_depth;
	}
}
