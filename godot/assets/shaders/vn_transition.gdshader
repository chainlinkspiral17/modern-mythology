shader_type canvas_item;
// VN TRANSITION · the register's dissolve (2026-11-05, pass 298).
// Put on the still of the last frame (GameEngine._transition_play): as
// `progress` runs 0 → 1 the still breaks away along a slow noise field —
// bayou water for the arcana, an oil-projector melt for milk & honey, a
// riso dot screen for the zines — and the edge where it is breaking glows
// in the register's own ink. Nothing moves the new frame underneath; the
// old one simply drains off it. Not a CRT, not a scanline: a dissolve with
// a material to it (the no-retro-cosplay rule, _SLOWSTICK_AESTHETIC_BIBLE).

uniform float progress : hint_range(0.0, 1.0) = 0.0;
uniform vec4 edge_color : source_color = vec4(1.0, 0.72, 0.36, 0.9);
uniform float edge_width = 0.05;      // in noise units: the glowing band
uniform float scale = 3.2;            // the field's size: low = big slow pools
uniform vec2 flow = vec2(0.0, 0.35);  // the field drifts this way as it goes
uniform float halftone = 0.0;         // 1 = the zines' dot screen
uniform float dots = 96.0;            // dot rows across the screen's height

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float vnoise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x),
	           mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
}

float fbm(vec2 p) {
	float v = 0.0;
	float a = 0.5;
	for (int k = 0; k < 4; k++) {
		v += a * vnoise(p);
		p = p * 2.03 + vec2(1.7, 9.2);
		a *= 0.5;
	}
	return v;
}

void fragment() {
	vec4 tex = texture(TEXTURE, UV);
	float aspect = SCREEN_PIXEL_SIZE.y > 0.0 ? SCREEN_PIXEL_SIZE.y / SCREEN_PIXEL_SIZE.x : 1.7778;
	vec2 p = vec2(UV.x * aspect, UV.y) * scale + flow * progress;
	float n = fbm(p);
	if (halftone > 0.5) {
		// a dot screen: each cell's dot shrinks as the threshold passes it
		vec2 g = vec2(UV.x * aspect, UV.y) * dots;
		float d = length(fract(g) - 0.5) * 1.41;
		n = mix(n, 1.0 - d, 0.55);
	}
	// map progress so 0 shows all of the still and 1 none of it
	float t = mix(-edge_width, 1.0 + edge_width, progress);
	float keep = smoothstep(t - edge_width * 0.35, t + edge_width * 0.35, n);
	float band = 1.0 - smoothstep(0.0, edge_width, abs(n - t));
	vec3 rgb = mix(tex.rgb, edge_color.rgb, band * edge_color.a);
	float a = max(keep, band * edge_color.a * (1.0 - progress * 0.5));
	COLOR = vec4(rgb, tex.a * a);
}
