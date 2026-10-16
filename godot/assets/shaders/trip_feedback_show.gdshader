// trip_feedback_show.gdshader · THE TRIP (2026-09-11)
// ════════════════════════════════════════════════════════════════
// The DISPLAY pass for the feedback buffer. One full-rect ColorRect
// sitting directly above the surface the buffer was caught from —
// in the VN, above the background image and below every piece of
// type — drawing the accumulated light back over it.
//
// blend_add, because a light trail is light. The runaway that
// additive blending usually causes is handled INSIDE the shader by a
// soft exponential roll-off (1 − e^(−b·soft)) rather than by a
// clamp: the brightest part of a trail compresses toward 1 and never
// produces the hard clipped edge draft 2 was told about ("add clips;
// screen rolls off"). With the roll-off in the source, the add can
// never contribute more than 1.
//
// The buffer is half resolution and sampled with a linear filter, so
// the trail arrives already soft — which is what a wake should look
// like next to a sharp picture.
// ════════════════════════════════════════════════════════════════
shader_type canvas_item;
render_mode blend_add, unshaded;

uniform sampler2D buf : filter_linear, repeat_disable;
uniform float gain : hint_range(0.0, 4.0) = 1.0;
uniform float soft : hint_range(0.1, 4.0) = 1.35;
// Where the picture under us is already bright, a light trail adds
// nothing and only fogs it (the draft-4 verdict: "whiter or brighter
// scenes are too plain"; light on light is invisible). The trail
// leans on the dark, which is where feedback reads anyway.
uniform float dark_bias : hint_range(0.0, 1.0) = 0.55;
uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear;

void fragment() {
	vec3 b = texture(buf, UV).rgb * gain;
	vec3 t = vec3(1.0) - exp(-b * soft);
	float under = dot(texture(SCREEN_TEXTURE, SCREEN_UV).rgb,
					  vec3(0.299, 0.587, 0.114));
	float k = mix(1.0, 1.0 - smoothstep(0.45, 0.92, under), dark_bias);
	COLOR = vec4(t * k, 1.0);
}
