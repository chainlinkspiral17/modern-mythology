// ascii_edges.gdshader
// ════════════════════════════════════════════════════════════════
// Edge detection + ASCII characters along detected edges. Runs a
// luminance Sobel on the screen colour to find visible silhouettes
// and contrast boundaries, then paints procedural ASCII-glyph
// patterns IN those edge regions while passing the scene through
// unmodified elsewhere.
//
// Originally used DEPTH_TEXTURE, but Godot 4's canvas_item shaders
// can't reliably bind the 3D depth buffer when stacked behind
// other CanvasLayer post-processes — the depth read came back
// uniform and the edges looked like a flat overlay. Luma Sobel on
// SCREEN_TEXTURE works regardless of layer order and actually
// tracks the geometry the player sees.
//
// Effect: low-poly geometry gets a thick painted outline that
// LOOKS like it's made of code. The substrate's "the chassis
// breathes" rendering.
//
// Apply on a CanvasLayer's ColorRect above the geometry layer.
// ════════════════════════════════════════════════════════════════

shader_type canvas_item;

uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear;

uniform float edge_strength : hint_range(0.0, 1.0) = 0.8;
uniform float edge_threshold : hint_range(0.001, 0.5) = 0.08;
uniform float edge_softness : hint_range(1.0, 8.0) = 3.0;
uniform vec4 edge_color : source_color = vec4(0.92, 0.78, 0.45, 1.0);
uniform vec4 edge_bg_color : source_color = vec4(0.05, 0.04, 0.02, 1.0);
uniform float glyph_cell_size : hint_range(4.0, 32.0) = 10.0;
uniform float scroll_speed : hint_range(0.0, 4.0) = 1.2;
uniform float edge_thickness : hint_range(0.5, 3.0) = 1.5;

float luma(vec3 c) {
    return dot(c, vec3(0.299, 0.587, 0.114));
}

// Procedural ASCII-like glyph density per cell, scrolling over time.
// Returns 0..1 fill intensity.
float scroll_glyph(vec2 frag_coord, float t) {
    vec2 scrolled = frag_coord + vec2(t * 80.0, 0.0);
    vec2 cell = floor(scrolled / glyph_cell_size);
    vec2 local = fract(scrolled / glyph_cell_size);

    float h = fract(sin(dot(cell, vec2(127.1, 311.7))) * 43758.5);

    float pattern;
    if (h < 0.10) {
        // sparse dot
        pattern = step(0.6, length(local - vec2(0.5)));
        pattern = 1.0 - pattern;
    } else if (h < 0.25) {
        // diagonal slash "/"
        pattern = step(0.85, 1.0 - abs(local.x + local.y - 1.0));
    } else if (h < 0.40) {
        // backslash "\"
        pattern = step(0.85, 1.0 - abs(local.x - local.y));
    } else if (h < 0.55) {
        // plus "+"
        float v1 = step(0.4, local.x) * step(local.x, 0.6);
        float v2 = step(0.4, local.y) * step(local.y, 0.6);
        pattern = clamp(v1 + v2, 0.0, 1.0);
    } else if (h < 0.70) {
        // horizontal dash "-"
        pattern = step(0.4, local.y) * step(local.y, 0.6);
    } else if (h < 0.85) {
        // pipe "|"
        pattern = step(0.4, local.x) * step(local.x, 0.6);
    } else if (h < 0.95) {
        // pound "#"
        float v1 = step(0.3, local.x) * step(local.x, 0.45);
        float v2 = step(0.6, local.x) * step(local.x, 0.75);
        float h1 = step(0.3, local.y) * step(local.y, 0.45);
        float h2 = step(0.6, local.y) * step(local.y, 0.75);
        pattern = clamp(v1 + v2 + h1 + h2, 0.0, 1.0);
    } else {
        // dense block
        pattern = 1.0;
    }
    return pattern;
}

void fragment() {
    vec2 uv = SCREEN_UV;
    vec2 px = SCREEN_PIXEL_SIZE * edge_thickness;

    // 3x3 luminance Sobel on the screen colour
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

    float edge_mask = smoothstep(edge_threshold, edge_threshold * edge_softness, edge);

    // Scrolling ASCII pattern, painted IN edge regions only
    float glyph = scroll_glyph(FRAGCOORD.xy, TIME * scroll_speed);

    vec3 scene = texture(SCREEN_TEXTURE, uv).rgb;
    vec3 edge_painted = mix(edge_bg_color.rgb, edge_color.rgb, glyph);
    vec3 result = mix(scene, edge_painted, edge_mask * edge_strength);

    COLOR = vec4(result, 1.0);
}
