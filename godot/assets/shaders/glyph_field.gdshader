// glyph_field.gdshader
// ════════════════════════════════════════════════════════════════
// A drifting ASCII glyph field rendered over the scene. Glyphs
// scroll in multiple directions at different speeds (parallax-
// like) and are alpha-blended with the scene below. Density per
// cell is modulated by the scene's luminance so brighter areas
// get more glyphs (or darker, configurable).
//
// Effect: the substrate hum, manifest as drifting code over the
// world. Distinct from ascii_edges (which paints edges only).
//
// Layer above ascii_edges in the post-process stack.
// ════════════════════════════════════════════════════════════════

shader_type canvas_item;

uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear;

uniform float glyph_alpha : hint_range(0.0, 1.0) = 0.35;
uniform float glyph_cell : hint_range(6.0, 32.0) = 12.0;
uniform vec4 glyph_color : source_color = vec4(0.85, 0.78, 0.55, 1.0);
uniform float scroll_x : hint_range(-2.0, 2.0) = 0.4;
uniform float scroll_y : hint_range(-2.0, 2.0) = -0.15;
uniform float luma_bias : hint_range(-1.0, 1.0) = 0.0;
// luma_bias > 0 means glyphs concentrate in BRIGHT areas
// luma_bias < 0 means glyphs concentrate in DARK areas
// 0 = uniform density

float layer_glyph(vec2 frag_coord, float scale, vec2 scroll, float seed) {
    vec2 scrolled = frag_coord + scroll * TIME * 60.0;
    vec2 cell = floor(scrolled / (glyph_cell * scale));
    vec2 local = fract(scrolled / (glyph_cell * scale));

    float h = fract(sin(dot(cell + vec2(seed), vec2(127.1, 311.7))) * 43758.5);

    if (h < 0.78) return 0.0;   // most cells empty

    float pattern;
    float g = fract(h * 7.0);
    if (g < 0.20) {
        // colon
        float a = step(0.40, local.y) * step(local.y, 0.55) * step(0.42, local.x) * step(local.x, 0.58);
        float b = step(0.65, local.y) * step(local.y, 0.80) * step(0.42, local.x) * step(local.x, 0.58);
        pattern = clamp(a + b, 0.0, 1.0);
    } else if (g < 0.40) {
        // tilde-ish wave
        pattern = step(0.10, sin(local.x * 9.42) * 0.3 + 0.5 - local.y) * step(local.y, 0.7);
    } else if (g < 0.60) {
        // greater-than
        pattern = step(0.85, 1.0 - abs(local.y - mix(0.2, 0.8, local.x)));
    } else if (g < 0.80) {
        // hash mini
        float v = step(0.4, local.x) * step(local.x, 0.6);
        float ho = step(0.4, local.y) * step(local.y, 0.6);
        pattern = clamp(v + ho, 0.0, 1.0);
    } else {
        // square
        pattern = step(0.25, local.x) * step(local.x, 0.75) * step(0.25, local.y) * step(local.y, 0.75);
    }

    return pattern;
}

void fragment() {
    vec3 scene = texture(SCREEN_TEXTURE, SCREEN_UV).rgb;
    float luma = dot(scene, vec3(0.299, 0.587, 0.114));

    // Three layered glyph fields at different scales + scroll
    // speeds for a parallax shimmer
    float g1 = layer_glyph(FRAGCOORD.xy, 1.0,  vec2(scroll_x, scroll_y),         0.0);
    float g2 = layer_glyph(FRAGCOORD.xy, 1.4,  vec2(-scroll_x * 0.6, scroll_y * 0.5), 17.3);
    float g3 = layer_glyph(FRAGCOORD.xy, 0.7,  vec2(scroll_x * 1.4, scroll_y * 1.4), 53.9);

    float glyphs = clamp(g1 + g2 * 0.7 + g3 * 0.5, 0.0, 1.0);

    // Bias glyph density by luma if requested
    float density;
    if (luma_bias > 0.0) {
        density = mix(1.0, luma, luma_bias);
    } else if (luma_bias < 0.0) {
        density = mix(1.0, 1.0 - luma, -luma_bias);
    } else {
        density = 1.0;
    }

    float final_alpha = glyphs * density * glyph_alpha;

    vec3 result = mix(scene, glyph_color.rgb, final_alpha);
    COLOR = vec4(result, 1.0);
}
