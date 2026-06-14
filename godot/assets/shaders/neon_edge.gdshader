// neon_edge.gdshader
// ════════════════════════════════════════════════════════════════
// Synthwave / chillwave outline shader. Runs a luminance Sobel on
// the screen colour to find visible silhouettes, paints those edges
// in a hot neon accent (pink / cyan / yellow / white — your call via
// edge_color), and fills the NON-edge pixels with a vertical gradient
// (dusk magenta at the bottom blending to deep purple at the top, or
// any other pair of colours via fill_low / fill_high).
//
// Apply on a CanvasLayer ColorRect early in the post-process stack
// (sees the clean 3D scene before the ASCII or demoscene passes).
// strength = 0 passes the scene through; strength = 1 fully stylizes.
//
// Mood examples (set via MoodCycler):
//   chillwave   · edge = hot pink, fill = magenta → purple gradient
//   noir        · edge = white,    fill = solid black
//   sunset      · edge = warm yellow, fill = orange → purple
//   ice         · edge = pale cyan,  fill = navy → near-black
// ════════════════════════════════════════════════════════════════

shader_type canvas_item;

uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear;

uniform float strength : hint_range(0.0, 1.0) = 0.0;
uniform float edge_threshold : hint_range(0.001, 0.5) = 0.10;
uniform float edge_thickness : hint_range(0.5, 4.0) = 1.5;
uniform vec4 edge_color : source_color = vec4(1.0, 0.22, 0.78, 1.0);  // hot pink
uniform vec4 fill_low  : source_color = vec4(0.42, 0.12, 0.50, 1.0);  // dusk magenta
uniform vec4 fill_high : source_color = vec4(0.10, 0.05, 0.25, 1.0);  // deep purple
uniform float fill_gradient : hint_range(0.0, 1.0) = 1.0;
// fill_gradient = 0  → flat (just fill_low used everywhere)
// fill_gradient = 1  → full vertical gradient from fill_low (bottom)
//                      to fill_high (top)
uniform float edge_glow : hint_range(0.0, 1.0) = 0.4;
// edge_glow controls how much edge brightness bleeds into adjacent
// fill area (a cheap fake bloom).
uniform float scene_blend : hint_range(0.0, 1.0) = 0.0;
// scene_blend = 0 → fill is purely the gradient (full stylization)
// scene_blend = 1 → fill uses the underlying scene colour
// In between, warm lamp glows and other accent colours bleed through
// the gradient — important for the chillwave look to keep warm
// yellows readable on a black background.

uniform float bleed_lo : hint_range(0.0, 1.0) = 0.78;
uniform float bleed_hi : hint_range(0.0, 1.0) = 0.96;
// bleed_lo/hi = scene-brightness smoothstep range for the bleed.
// Default (0.78, 0.96) lets bright lamp glows through; raise to
// (0.92, 0.99) to be stricter.

uniform bool sat_bleed = false;
uniform float sat_lo : hint_range(0.0, 1.0) = 0.40;
uniform float sat_hi : hint_range(0.0, 1.0) = 0.60;
uniform bool red_only = false;
// sat_bleed = true → AND a saturation gate on top of the brightness
// gate. Useful as a generic discriminator.
//
// red_only = true → REPLACES the saturation gate with a strict
// red-dominance test: red_dom = R - max(G, B). Sign red gives
// 0.78; sodium-lit warm cars give 0.34; warm walls give ~0.05.
// Only "true red emission" passes — perfect for the lithograph
// look where the reference shows ONLY the sign letters (and the
// red-tinted lit windows) in colour, never warm-lit surfaces.

float luma(vec3 c) {
    return dot(c, vec3(0.299, 0.587, 0.114));
}

void fragment() {
    vec2 uv = SCREEN_UV;
    vec2 px = SCREEN_PIXEL_SIZE * edge_thickness;

    // 3x3 luminance Sobel
    float l00 = luma(texture(SCREEN_TEXTURE, uv + vec2(-px.x, -px.y)).rgb);
    float l10 = luma(texture(SCREEN_TEXTURE, uv + vec2( 0.0,  -px.y)).rgb);
    float l20 = luma(texture(SCREEN_TEXTURE, uv + vec2( px.x, -px.y)).rgb);
    float l01 = luma(texture(SCREEN_TEXTURE, uv + vec2(-px.x,  0.0 )).rgb);
    float l21 = luma(texture(SCREEN_TEXTURE, uv + vec2( px.x,  0.0 )).rgb);
    float l02 = luma(texture(SCREEN_TEXTURE, uv + vec2(-px.x,  px.y)).rgb);
    float l12 = luma(texture(SCREEN_TEXTURE, uv + vec2( 0.0,   px.y)).rgb);
    float l22 = luma(texture(SCREEN_TEXTURE, uv + vec2( px.x,  px.y)).rgb);

    float gx = -l00 - 2.0 * l01 - l02 + l20 + 2.0 * l21 + l22;
    float gy = -l00 - 2.0 * l10 - l20 + l02 + 2.0 * l12 + l22;
    float edge = sqrt(gx * gx + gy * gy);

    float edge_mask = smoothstep(edge_threshold, edge_threshold * 3.0, edge);

    // Vertical gradient fill (uv.y is 0 at top, 1 at bottom for canvas)
    float gy_t = mix(0.5, smoothstep(0.0, 1.0, uv.y), fill_gradient);
    vec3 fill = mix(fill_high.rgb, fill_low.rgb, gy_t);

    // Only the BRIGHTEST pixels (lit windows, lamp glow, neon itself)
    // get their warm scene colour to bleed through. The threshold is
    // tight so a bright daytime scene doesn't tint the entire fill —
    // most of the screen stays in the dark gradient. This keeps the
    // pure-black-background look the concept art is going for.
    vec3 scene_now = texture(SCREEN_TEXTURE, uv).rgb;
    float scene_max = max(scene_now.r, max(scene_now.g, scene_now.b));
    float brightness_mask = smoothstep(bleed_lo, bleed_hi, scene_max);
    float bleed_mask = brightness_mask;
    if (red_only) {
        // Strict red-dominance discriminator. Sodium-lit warm cars
        // (red_dom ~0.34) get rejected even though they're saturated
        // and bright; only the sign letters and red-glow windows pass.
        float red_dom = scene_now.r - max(scene_now.g, scene_now.b);
        bleed_mask *= smoothstep(sat_lo, sat_hi, red_dom);
    } else if (sat_bleed) {
        // Generic saturation gate (less strict than red_only).
        float scene_min = min(scene_now.r, min(scene_now.g, scene_now.b));
        float saturation = scene_max > 0.001 ? (scene_max - scene_min) / scene_max : 0.0;
        bleed_mask *= smoothstep(sat_lo, sat_hi, saturation);
    }
    fill = mix(fill, scene_now * 1.8, scene_blend * bleed_mask);

    // Cheap bloom: sample a wider edge mask for the glow halo
    vec2 gpx = SCREEN_PIXEL_SIZE * (edge_thickness + 3.0);
    float l00g = luma(texture(SCREEN_TEXTURE, uv + vec2(-gpx.x, -gpx.y)).rgb);
    float l20g = luma(texture(SCREEN_TEXTURE, uv + vec2( gpx.x, -gpx.y)).rgb);
    float l02g = luma(texture(SCREEN_TEXTURE, uv + vec2(-gpx.x,  gpx.y)).rgb);
    float l22g = luma(texture(SCREEN_TEXTURE, uv + vec2( gpx.x,  gpx.y)).rgb);
    float l01g = luma(texture(SCREEN_TEXTURE, uv + vec2(-gpx.x,  0.0  )).rgb);
    float l21g = luma(texture(SCREEN_TEXTURE, uv + vec2( gpx.x,  0.0  )).rgb);
    float l10g = luma(texture(SCREEN_TEXTURE, uv + vec2( 0.0,   -gpx.y)).rgb);
    float l12g = luma(texture(SCREEN_TEXTURE, uv + vec2( 0.0,    gpx.y)).rgb);
    float gxg = -l00g - 2.0 * l01g - l02g + l20g + 2.0 * l21g + l22g;
    float gyg = -l00g - 2.0 * l10g - l20g + l02g + 2.0 * l12g + l22g;
    float edge_wide = sqrt(gxg * gxg + gyg * gyg);
    float glow_mask = smoothstep(edge_threshold * 0.5, edge_threshold * 2.5, edge_wide);

    // Stylized output: gradient fill + edge bloom + crisp edge line
    vec3 stylized = fill;
    stylized = mix(stylized, edge_color.rgb, glow_mask * edge_glow);
    stylized = mix(stylized, edge_color.rgb, edge_mask);

    vec3 scene = texture(SCREEN_TEXTURE, uv).rgb;
    vec3 result = mix(scene, stylized, strength);
    COLOR = vec4(result, 1.0);
}
