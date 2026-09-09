// trip_feedback.gdshader · THE TRIP · the feedback buffer (2026-09-11)
// ════════════════════════════════════════════════════════════════
// The Minter half of the layer, and the one the bible listed as
// missing: "No feedback-trail buffer yet. The Minter register's
// trails are faked by spark halos and the thump; the real thing is a
// SubViewport with a decay quad, driven by the same pulse."
//
// This is the ACCUMULATE pass. It runs inside a half-resolution
// SubViewport that TripSync ping-pongs, and each frame it does two
// things:
//
//   1. RE-PROJECT the previous buffer a hair larger (or smaller, per
//      register) with a slow spin and drift, and decay it. That is
//      the trail — light leaving a wake behind wherever it was.
//   2. SCREEN IN the new light: the bright part of the source, tinted
//      toward the register's palette. Screen, not add, so a static
//      highlight settles instead of running away to white
//      (_SHADER_VISUALS_PLAYBOOK: "add clips; screen rolls off").
//
// WHAT IT NEVER DOES — the motion rule (bible rule 0). The PICTURE
// does not move. The re-projection moves the TRAIL only, it is slow,
// constant, and has no beat in it: `zoom`, `spin` and `drift` are
// per-second rates × delta, computed in TripSync and identical
// whether the music is loud, quiet or absent. The beat is allowed
// exactly one job here, the same one it has everywhere else in THE
// TRIP — it makes light BRIGHTER (`pulse` lifts `gain`), never
// bigger, never faster, never displaced.
//
// The source is a TEXTURE, not the screen: in the VN it is the
// background image itself, so the dialogue box, the portraits and
// every glyph of type are outside the buffer by construction and
// cannot smear. That is the whole reason this is not a screen-space
// pass.
//
// Mesa-safe: two samplers, floats, no loops, no derivatives.
// ════════════════════════════════════════════════════════════════
shader_type canvas_item;
render_mode blend_disabled, unshaded;

uniform sampler2D prev : filter_linear, repeat_disable;   // last frame's buffer
uniform sampler2D src  : filter_linear, repeat_disable;   // what to catch light from

// ── the trail ──
// decay: per-FRAME survival, computed as exp(-dt · rate) in TripSync
// so the wake is the same length at 30 fps and at 90.
uniform float decay : hint_range(0.0, 1.0) = 0.86;
// zoom: per-frame scale of the re-projection. POSITIVE samples the
// previous frame from further in, so the trail expands outward (the
// oil-projector bloom); NEGATIVE pulls it inward (the cabinet sinks).
uniform float zoom = 0.004;
uniform float spin = 0.0;        // radians per frame
uniform float drift_x = 0.0;     // uv per frame
uniform float drift_y = 0.0;
uniform float aspect = 1.7777;

// ── the light that enters ──
uniform float thresh : hint_range(0.0, 1.0) = 0.62;   // luma the picture must clear
uniform float gain : hint_range(0.0, 4.0) = 1.0;      // register × amount × TRAILS
uniform float pulse : hint_range(0.0, 1.0) = 0.0;     // light, never motion
uniform vec3 tint = vec3(1.0, 1.0, 1.0);              // the register's hue
uniform float tint_mix : hint_range(0.0, 1.0) = 0.35;
uniform float edge_amount : hint_range(0.0, 2.0) = 1.0;  // the aura, fed back
uniform vec2 src_px = vec2(0.001, 0.0018);               // one source pixel

float luma3(vec3 c) {
	return dot(c, vec3(0.299, 0.587, 0.114));
}

// The register's LINE light, recomputed here rather than sampled.
// The trip shader draws its aura onto the surface, but the buffer's
// source is that surface's TEXTURE — the picture before the aura is
// laid on it. Finding the silhouettes again (one Sobel, wide, at half
// resolution) is what makes this a feedback of THE LAYER'S OWN LIGHT
// and not merely of bright pixels: the aura is what leaves the wake.
float edge_at(vec2 uv, vec2 px) {
	float l00 = luma3(texture(src, uv + vec2(-px.x, -px.y)).rgb);
	float l10 = luma3(texture(src, uv + vec2( 0.0,  -px.y)).rgb);
	float l20 = luma3(texture(src, uv + vec2( px.x, -px.y)).rgb);
	float l01 = luma3(texture(src, uv + vec2(-px.x,  0.0 )).rgb);
	float l21 = luma3(texture(src, uv + vec2( px.x,  0.0 )).rgb);
	float l02 = luma3(texture(src, uv + vec2(-px.x,  px.y)).rgb);
	float l12 = luma3(texture(src, uv + vec2( 0.0,   px.y)).rgb);
	float l22 = luma3(texture(src, uv + vec2( px.x,  px.y)).rgb);
	float gx = -l00 - 2.0 * l01 - l02 + l20 + 2.0 * l21 + l22;
	float gy = -l00 - 2.0 * l10 - l20 + l02 + 2.0 * l12 + l22;
	return sqrt(gx * gx + gy * gy);
}

void fragment() {
	// ── 1 · the previous frame, re-projected and decayed ──────────
	vec2 c = vec2(0.5);
	vec2 p = (UV - c) * vec2(aspect, 1.0);
	float s = 1.0 - zoom;
	float ca = cos(spin);
	float sa = sin(spin);
	vec2 r = vec2(p.x * ca - p.y * sa, p.x * sa + p.y * ca) * s;
	vec2 puv = r / vec2(aspect, 1.0) + c + vec2(drift_x, drift_y);
	// Clamped rather than wrapped: a wrapped trail draws the top of
	// the frame back in at the bottom, which reads as a glitch, not
	// as light.
	vec3 trail = texture(prev, clamp(puv, vec2(0.002), vec2(0.998))).rgb * decay;

	// ── 2 · the new light ─────────────────────────────────────────
	// (a) the picture's own highlights — a lamp, a window, a sky
	vec3 s_rgb = texture(src, UV).rgb;
	float l = luma3(s_rgb);
	float e = smoothstep(thresh, min(0.995, thresh + 0.32), l);
	vec3 lit = mix(s_rgb, s_rgb * tint * 1.55, tint_mix);
	// (b) the layer's aura — the silhouettes, in the register's hue
	float edge = smoothstep(0.10, 0.40, edge_at(UV, src_px * 2.5));
	vec3 aura = tint * edge * edge_amount * 0.55;
	vec3 beat = vec3(0.72 + 0.88 * pulse);
	vec3 emis = clamp((lit * e + aura) * gain * beat, 0.0, 1.0);

	// screen: 1 − (1−a)(1−b). Bounded, so the buffer cannot run away.
	vec3 outc = 1.0 - (1.0 - clamp(trail, 0.0, 1.0)) * (1.0 - emis);
	COLOR = vec4(outc, 1.0);
}
