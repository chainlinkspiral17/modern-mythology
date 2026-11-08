// painting_halo.gdshader — a 16:9 painting on a wider screen (2026-11-08).
//
// The user: "keep the side screen real estate mainly for expanding the
// backgrounds to be more panoramic … when the visual novel zooms in on
// static images, maybe employ a blurring feather effect and extend around
// the edges, continuing with the psychedelic theme."
//
// A full-screen rect drawn OVER the painting. It maps every screen point
// into the painting's own UV (img_rect: where the painting is drawn right
// now, after the painting's camera has pushed / panned it), MIRRORS the
// picture past its edges, blurs it wide, and lets the result feather in
// across the painting's border: inside the picture it is transparent, past
// the border it is the picture carried on — soft, dimmed, and drifting in
// the trip's hue (TripSync's hue_base / flow / energy), so the margins read
// as the dream continuing, not as bars.
shader_type canvas_item;

uniform sampler2D painting : filter_linear, repeat_disable;
uniform vec4 img_rect = vec4(0.0, 0.0, 1.0, 1.0);   // the painting on screen: xy, wh in this rect's UV
uniform float feather = 0.12;        // of the screen width: the soft border, half each side of the edge
uniform float blur = 0.035;          // of the painting: the halo's blur radius
uniform float dim = 0.55;            // the halo's brightness against the painting
uniform float hue = 0.0;             // TripSync.hue_base, 0..1
uniform float flow = 0.0;            // TripSync.t_flow (seconds of drift)
uniform float energy = 0.0;          // TripSync.energy, 0..1
uniform float trip = 0.75;           // the player's TRIP amount
uniform float aspect = 2.39;         // this rect's width / height

vec3 hue_shift(vec3 c, float h) {
	const vec3 k = vec3(0.57735);
	float a = h * 6.2831853;
	float ca = cos(a);
	return c * ca + cross(k, c) * sin(a) + k * dot(k, c) * (1.0 - ca);
}

vec2 mirror_uv(vec2 uv) {
	vec2 m = mod(uv, 2.0);
	return mix(m, 2.0 - m, step(1.0, m));
}

void fragment() {
	vec2 rel = (UV - img_rect.xy) / max(img_rect.zw, vec2(1e-4));
	// signed distance to the painting's edge, in screen-width units
	vec2 d2 = max(-rel, rel - 1.0) * img_rect.zw * vec2(1.0, 1.0 / aspect);
	float out_d = max(d2.x, d2.y);                 // > 0 outside, < 0 inside
	float a = smoothstep(-feather * 0.5, feather * 0.5, out_d);
	if (a <= 0.001) {
		discard;
	}
	// the margin breathes: a slow liquid warp that grows with the distance
	// from the picture (the dream loosening the further it goes)
	float far = clamp(out_d * 4.0, 0.0, 1.0) * trip;
	vec2 warp = vec2(sin(rel.y * 6.0 + flow * 0.35), cos(rel.x * 5.0 - flow * 0.28)) * 0.018 * far;
	vec2 base = mirror_uv(rel + warp);
	// a wide blur: two rings of eight taps and the centre
	vec3 acc = texture(painting, base).rgb * 0.2;
	float r1 = blur * (0.6 + far * 0.8);
	float r2 = r1 * 2.2;
	for (int i = 0; i < 8; i++) {
		float ang = float(i) * 0.785398 + 0.39;
		vec2 o = vec2(cos(ang), sin(ang) * aspect * img_rect.z / max(img_rect.w, 1e-4));
		acc += texture(painting, mirror_uv(rel + warp + o * r1)).rgb * 0.06;
		acc += texture(painting, mirror_uv(rel + warp + o * r2)).rgb * 0.04;
	}
	vec3 col = acc;
	// the trip's hue rides the margins: drifting with the music's register
	col = mix(col, hue_shift(col, hue + flow * 0.01 + far * 0.08), 0.55 * trip);
	col *= dim * (1.0 + energy * 0.25 * trip) * mix(1.0, 0.72, far);
	COLOR = vec4(col, a);
}
