// ascii_edges.gdshader
// ════════════════════════════════════════════════════════════════
// Edge detection + ASCII characters along detected edges. Reads
// the rendered scene's depth buffer to find geometric edges, then
// outputs procedural ASCII-glyph patterns IN those edge regions
// while passing the scene through unmodified elsewhere.
//
// Effect: low-poly geometry gets a thick painted outline that
// LOOKS like it's made of code. The substrate's "the chassis
// breathes" rendering.
//
// Apply on a CanvasLayer's ColorRect above the geometry layer.
// ════════════════════════════════════════════════════════════════

shader_type canvas_item;

uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear;
uniform sampler2D DEPTH_TEXTURE : hint_depth_texture, filter_nearest;

uniform float edge_strength : hint_range(0.0, 1.0) = 0.8;
uniform float edge_threshold : hint_range(0.0001, 0.01) = 0.0015;
uniform vec4 edge_color : source_color = vec4(0.92, 0.78, 0.45, 1.0);
uniform vec4 edge_bg_color : source_color = vec4(0.05, 0.04, 0.02, 1.0);
uniform float glyph_cell_size : hint_range(4.0, 32.0) = 10.0;
uniform float scroll_speed : hint_range(0.0, 4.0) = 1.2;

// Sample depth, linearize. In Godot 4 the depth buffer is non-
// linear (closer to 1.0 = near camera, 0.0 = far). We sample
// neighbors and use the contrast as an edge signal.
float sample_depth(vec2 uv) {
    return texture(DEPTH_TEXTURE, uv).r;
}

// Procedural ASCII-like glyph density per cell, scrolling over time.
// Returns 0..1 fill intensity.
float scroll_glyph(vec2 frag_coord, float t) {
    // Shift the cells horizontally over time so the glyphs "flow"
    vec2 scrolled = frag_coord + vec2(t * 80.0, 0.0);
    vec2 cell = floor(scrolled / glyph_cell_size);
    vec2 local = fract(scrolled / glyph_cell_size);

    // Hash the cell index for pseudo-random glyph choice
    float h = fract(sin(dot(cell, vec2(127.1, 311.7))) * 43758.5);

    // Build a procedural pattern per cell — different cells render
    // different "glyphs" via different pixel-pattern formulas.
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
    vec2 px = SCREEN_PIXEL_SIZE;

    // Edge detection: sample center + four neighbors, sum the
    // absolute differences. High contrast = edge.
    float d0 = sample_depth(uv);
    float d1 = sample_depth(uv + vec2(px.x * 1.5, 0.0));
    float d2 = sample_depth(uv + vec2(0.0, px.y * 1.5));
    float d3 = sample_depth(uv + vec2(-px.x * 1.5, 0.0));
    float d4 = sample_depth(uv + vec2(0.0, -px.y * 1.5));

    // Robert's cross + Laplacian-ish — sensitive to both edges
    // and small-detail changes.
    float edge = abs(d1 - d3) + abs(d2 - d4) + 2.0 * abs(d0 - (d1 + d2 + d3 + d4) * 0.25);
    float edge_mask = smoothstep(edge_threshold, edge_threshold * 4.0, edge);

    // The scrolling ASCII pattern, only painted into edge regions
    float glyph = scroll_glyph(FRAGCOORD.xy, TIME * scroll_speed);

    // Pass-through scene color where there's no edge
    vec3 scene = texture(SCREEN_TEXTURE, uv).rgb;

    // In edge regions, blend toward the glyph-textured edge color
    vec3 edge_painted = mix(edge_bg_color.rgb, edge_color.rgb, glyph);
    vec3 result = mix(scene, edge_painted, edge_mask * edge_strength);

    COLOR = vec4(result, 1.0);
}
