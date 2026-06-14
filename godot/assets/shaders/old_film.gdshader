// old_film.gdshader
// ════════════════════════════════════════════════════════════════
// Silent-era cinema layer. Six stacked effects, all gated by
// `strength`:
//
//   1. Desaturate to luminance
//   2. Sepia / warm-paper tint (toggle: tint_color)
//   3. Frame-flicker — quantize TIME to a frames-per-second rate
//      and use that quantized value for brightness modulation
//      AND grain pattern, so the picture appears to step at the
//      simulated rate (without the actual renderer dropping fps).
//   4. Film grain — TIME-quantized noise overlay
//   5. Dust / scratches — sparse vertical noise lines
//   6. Vignette — radial darkening at edges
//
// `sim_fps` controls the apparent rate (minimum 12 to avoid the
// "seizure" zone but still feel cranked). At 60 Hz real refresh,
// sim_fps = 12 means each "film frame" is held for ~5 real frames.
// ════════════════════════════════════════════════════════════════
shader_type canvas_item;

uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear;

uniform float strength : hint_range(0.0, 1.0) = 0.0;
uniform float sim_fps  : hint_range(12.0, 60.0) = 18.0;
uniform vec4  tint_color : source_color = vec4(0.96, 0.90, 0.74, 1.0);
uniform float tint_amount : hint_range(0.0, 1.0) = 0.55;
uniform float grain_strength : hint_range(0.0, 1.0) = 0.18;
uniform float flicker_strength : hint_range(0.0, 1.0) = 0.20;
uniform float vignette_strength : hint_range(0.0, 1.0) = 0.55;
uniform float scratch_strength : hint_range(0.0, 1.0) = 0.10;
uniform float judder_strength : hint_range(0.0, 0.04) = 0.0;
// judder_strength = per-frame UV offset amplitude. At 0.003 the
// picture wobbles by ~3 px on a 1280×720 frame each new simulated
// frame — hand-cranked-camera shake. Bigger = more drunken cinema.

float hash21(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

void fragment() {
    vec2 uv = SCREEN_UV;
    if (strength < 0.001) {
        COLOR = vec4(texture(SCREEN_TEXTURE, uv).rgb, 1.0);
    } else {
        // ── Quantized frame time. floor(TIME * sim_fps) ticks once
        // per simulated film frame. Used both for grain seed and
        // flicker brightness so they advance together.
        float frame_t = floor(TIME * sim_fps);

        // ── Camera judder. Per-quantized-frame UV offset — picture
        // wobbles like a hand-cranked camera that isn't quite
        // mechanically smooth. Two-axis hash so it doesn't run on
        // rails.
        vec2 judder = vec2(0.0);
        if (judder_strength > 0.0001) {
            float jx = hash21(vec2(frame_t,        17.0)) - 0.5;
            float jy = hash21(vec2(frame_t * 1.7, 31.0)) - 0.5;
            judder = vec2(jx, jy) * judder_strength;
        }
        vec3 scene = texture(SCREEN_TEXTURE, uv + judder).rgb;

        // ── 1. Desaturate
        float luma = dot(scene, vec3(0.299, 0.587, 0.114));
        vec3 bw = vec3(luma);

        // ── 2. Sepia tint — mix BW toward warm paper colour
        vec3 tinted = mix(bw, bw * tint_color.rgb * 1.15, tint_amount);

        // ── 3. Frame flicker: per-frame brightness wobble. Use
        // hash of the quantized frame index as the wobble seed so
        // consecutive frames have different brightnesses.
        float flick = hash21(vec2(frame_t, 0.0));
        float flick_mul = 1.0 - flicker_strength * 0.5 + flick * flicker_strength;
        tinted *= flick_mul;

        // ── 4. Film grain — per-pixel hash seeded by frame index.
        // Stays consistent within a frame, swaps each new "tick".
        float grain = hash21(uv * 1024.0 + vec2(frame_t * 7.3, frame_t * 3.7));
        tinted += (grain - 0.5) * grain_strength;

        // ── 5. Scratches — sparse vertical streaks at random x
        // positions that hold for a frame, jitter at frame swap.
        float scratch_seed = hash21(vec2(frame_t * 13.7, 0.0));
        if (scratch_seed > 0.92) {
            float scratch_x = hash21(vec2(frame_t * 23.1, 0.0));
            if (abs(uv.x - scratch_x) < 0.002) {
                tinted += vec3(scratch_strength * 0.95);
            }
        }

        // ── 6. Vignette — radial darkening
        float r = distance(uv, vec2(0.5));
        float v = 1.0 - smoothstep(0.45, 0.85, r) * vignette_strength;
        tinted *= v;

        vec3 result = mix(scene, tinted, strength);
        COLOR = vec4(result, 1.0);
    }
}
