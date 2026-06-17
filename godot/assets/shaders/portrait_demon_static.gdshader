// portrait_demon_static.gdshader
// ════════════════════════════════════════════════════════════════
// Digital-static / high-energy-chaos overlay for demon portraits.
//
// Sits on the SubViewportContainer as a material override; samples
// the viewport texture and applies four stacked corruptions:
//
//   1. RGB chromatic aberration — channel-split horizontal offset
//      with a time-modulated magnitude (signal-corruption read).
//   2. Horizontal scanline TEAR — at random bands, the row's UV
//      is yanked sideways and the colors wrap. Bands flicker on
//      and off every quantized frame.
//   3. Static noise overlay — TIME-quantized hash noise so the
//      grain reads as TV-snow rather than smooth video noise.
//   4. Signal-drop bands — occasional horizontal stripes go black
//      or oversaturated white, faking a broken sync pulse.
//
// All effects are gated by `strength`. At strength=0 the shader is
// a pass-through (used so the same Portrait3D scene can host both
// hero and demon characters; CharLayer flips the strength when
// loading a demon GLB).
//
// `chaos_rate` controls how fast the corruption mutates — bigger
// = more frantic. Default 18 Hz reads as "broken VHS tape feeding
// the camera live."
// ════════════════════════════════════════════════════════════════
shader_type canvas_item;

uniform float strength    : hint_range(0.0, 1.0) = 1.0;
uniform float chaos_rate  : hint_range(1.0, 60.0) = 18.0;
uniform float aberration  : hint_range(0.0, 0.04) = 0.012;
uniform float tear_amount : hint_range(0.0, 0.20) = 0.06;
uniform float static_amt  : hint_range(0.0, 1.0) = 0.35;
uniform float dropband    : hint_range(0.0, 1.0) = 0.25;
uniform vec4  tint        : source_color = vec4(0.85, 1.00, 0.85, 1.0);

float hash21(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

float hash11(float x) {
    return fract(sin(x * 78.233) * 43758.5453);
}

void fragment() {
    // Pass-through when strength is zero (hero portraits) — Godot
    // forbids `return` inside fragment(), so branch via else instead.
    if (strength <= 0.001) {
        COLOR = texture(TEXTURE, UV);
    } else {
        // Quantize time so corruption STEPS instead of smoothly
        // sliding — reads as discrete frames of a glitching feed,
        // not a soft warble.
        float t_frame = floor(TIME * chaos_rate) / chaos_rate;
        float seed    = t_frame * 11.7;

        vec2 uv = UV;

        // ── 2. Horizontal scanline tear ──────────────────────
        // Pick a small number of rows each frame to yank sideways.
        float row_seed = hash21(vec2(floor(uv.y * 80.0), seed));
        float tear_active = step(0.86, row_seed);   // ~14% of rows tear
        float tear_dir    = (hash11(seed + uv.y * 13.0) - 0.5) * 2.0;
        uv.x += tear_dir * tear_amount * tear_active * strength;

        // ── 1. RGB chromatic aberration ──────────────────────
        // Channel-split with a small time-jittered amount; gives
        // the demon's silhouette a hot-edge fringe.
        float ab = aberration * (0.6 + 0.4 * sin(seed * 6.28)) * strength;
        float r = texture(TEXTURE, vec2(uv.x + ab, uv.y)).r;
        float g = texture(TEXTURE, uv).g;
        float b = texture(TEXTURE, vec2(uv.x - ab, uv.y)).b;
        float a = texture(TEXTURE, uv).a;
        vec3 col = vec3(r, g, b);

        // ── 3. Static noise overlay ──────────────────────────
        // TIME-quantized hash, applied as additive snow. Bright
        // noise ONLY on rows that already have signal (so we
        // don't fill the transparent bg with grain).
        float n = hash21(uv * vec2(640.0, 480.0) + seed);
        col += (n - 0.5) * static_amt * strength * smoothstep(0.02, 0.10, a);

        // ── 4. Signal-drop bands ─────────────────────────────
        // Occasional horizontal strips go to black-white extremes,
        // simulating a broken sync pulse. Triggered per quantized
        // frame on a small set of rows.
        float band_seed   = hash11(floor(uv.y * 18.0) + seed * 3.1);
        float band_active = step(0.93, band_seed) * dropband * strength;
        float band_polarity = step(0.5, hash11(seed));
        col = mix(col, vec3(band_polarity), band_active);

        // Apply demon tint (cool sickly green by default — matches
        // the CHAR_ACCENTS entry for "the_demon")
        col *= mix(vec3(1.0), tint.rgb, strength * 0.4);

        COLOR = vec4(col, a);
    }
}
