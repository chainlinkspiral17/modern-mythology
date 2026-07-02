// gauss_blur.gdshader
// ════════════════════════════════════════════════════════════════
// One-pass tunable blur for the cinematic-condition presets:
//   blur_mode = 0 → Gaussian (omnidirectional)        — "blur"
//   blur_mode = 1 → directional (vector-based)        — "motion"
//   blur_mode = 2 → radial (from screen centre out)   — DOF haze
//
// 9-tap kernel per mode. Cheap. Placed in the post-process stack
// AFTER the starscape and BEFORE the demoscene palette quantize so
// the blur is applied to the stylised composite, then the palette
// is applied to the blurred result.
// ════════════════════════════════════════════════════════════════
shader_type canvas_item;

uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear;

uniform float strength : hint_range(0.0, 1.0) = 0.0;
uniform int blur_mode : hint_range(0, 2) = 0;
uniform float radius : hint_range(0.0, 16.0) = 4.0;
uniform vec2 motion_dir = vec2(1.0, 0.0);   // unit-ish direction for blur_mode=1

float gauss_weight(float x) {
    return exp(-0.5 * x * x);
}

void fragment() {
    vec3 scene = texture(SCREEN_TEXTURE, SCREEN_UV).rgb;
    if (strength < 0.001 || radius < 0.001) {
        COLOR = vec4(scene, 1.0);
    } else {
        vec3 acc = vec3(0.0);
        float wsum = 0.0;
        // 9 taps along chosen direction(s)
        for (int i = -4; i <= 4; i++) {
            float fi = float(i);
            float w = gauss_weight(fi * 0.5);
            vec2 offset;
            if (blur_mode == 1) {
                // Directional / motion
                offset = motion_dir * fi * radius * SCREEN_PIXEL_SIZE;
            } else if (blur_mode == 2) {
                // Radial — direction is from screen centre outward
                vec2 dir = normalize(SCREEN_UV - vec2(0.5)) * fi * radius * SCREEN_PIXEL_SIZE.x;
                offset = dir;
            } else {
                // Gaussian — combine N along axis-aligned dirs for cheap box-ish gauss
                float ang = fi * 0.78539816;   // π/4 increments around the circle
                offset = vec2(cos(ang), sin(ang)) * radius * SCREEN_PIXEL_SIZE;
            }
            acc += texture(SCREEN_TEXTURE, SCREEN_UV + offset).rgb * w;
            wsum += w;
        }
        vec3 blurred = acc / max(wsum, 0.0001);
        COLOR = vec4(mix(scene, blurred, strength), 1.0);
    }
}
