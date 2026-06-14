// ascii_directional.gdshader
// ════════════════════════════════════════════════════════════════
// DIRECTIONAL ASCII renderer. Unlike ascii_render.gdshader which
// picks glyph density purely from luminance (every cell picks a
// glyph independent of its neighbours), this shader uses the LOCAL
// EDGE DIRECTION at each cell to choose which line-drawing
// character to render:
//
//   · horizontal edge   → ─    (mid-cell horizontal stroke)
//   · vertical edge     → │    (mid-cell vertical stroke)
//   · diagonal /        → ╱
//   · diagonal \        → ╲
//   · strong cross      → ┼    (both gradients high)
//   · weak / fill       → · or empty
//
// The visual result: lines in the rendered image trace the geometry's
// silhouettes. Looking at the concept-art reference, this is the
// technique an illustrator was using by hand — horizontal cabin trim
// drawn with horizontal strokes, vertical hull seams with vertical
// strokes, roof slopes with diagonals.
//
// Apply BEFORE ascii_render / demoscene_post so it sees the clean
// scene. strength = 0 passes through, strength = 1 fully directional.
//
// Suggested mood: a new "blueprint" mood (cyan-on-black with this
// directional ASCII) or roll it into substrate for a "world IS
// architecture drawn in code" feel.
// ════════════════════════════════════════════════════════════════

shader_type canvas_item;

uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear;

uniform float strength : hint_range(0.0, 1.0) = 0.0;
uniform float cell_size : hint_range(4.0, 32.0) = 10.0;
uniform float edge_threshold : hint_range(0.01, 0.5) = 0.10;
uniform vec4 line_color : source_color = vec4(0.92, 0.20, 0.20, 1.0);   // line stroke color
uniform vec4 fill_color : source_color = vec4(0.02, 0.02, 0.03, 1.0);   // cell background
uniform bool tint_from_scene = false;   // if true, line takes scene colour

float luma(vec3 c) {
    return dot(c, vec3(0.299, 0.587, 0.114));
}

// Each draw_X function returns 1.0 if (p) is within the character's
// drawn region in cell-local coords (0..1) × (0..1).

// THICKER strokes — the previous values (0.10 width) were too thin to
// read once the post-process scanlines + dither got applied on top.
// Strokes are now 0.14 thick and span 95% of the cell so adjacent
// edge-cells visually connect into continuous lines.

// ─  horizontal bar centred
float draw_horizontal(vec2 p) {
    return (p.y > 0.43 && p.y < 0.57 && p.x > 0.02 && p.x < 0.98) ? 1.0 : 0.0;
}

float draw_horizontal_thick(vec2 p) {
    return (p.y > 0.38 && p.y < 0.62 && p.x > 0.00 && p.x < 1.00) ? 1.0 : 0.0;
}

// │  vertical bar centred
float draw_vertical(vec2 p) {
    return (p.x > 0.43 && p.x < 0.57 && p.y > 0.02 && p.y < 0.98) ? 1.0 : 0.0;
}

float draw_vertical_thick(vec2 p) {
    return (p.x > 0.38 && p.x < 0.62 && p.y > 0.00 && p.y < 1.00) ? 1.0 : 0.0;
}

// ╱  diagonal up-right (bottom-left to top-right)
float draw_diag_ne(vec2 p) {
    float d = abs((1.0 - p.y) - p.x);
    return (d < 0.14 && p.x > 0.00 && p.x < 1.00) ? 1.0 : 0.0;
}

// ╲  diagonal down-right (top-left to bottom-right)
float draw_diag_se(vec2 p) {
    float d = abs(p.x - p.y);
    return (d < 0.14 && p.x > 0.00 && p.x < 1.00) ? 1.0 : 0.0;
}

// ┼  cross — horizontal + vertical
float draw_cross(vec2 p) {
    return max(draw_horizontal(p), draw_vertical(p));
}

// ╳  x-cross — both diagonals
float draw_x(vec2 p) {
    return max(draw_diag_ne(p), draw_diag_se(p));
}

// ·  centre dot
float draw_dot(vec2 p) {
    return (length(p - vec2(0.5)) < 0.10) ? 1.0 : 0.0;
}

void fragment() {
    vec2 frag = FRAGCOORD.xy;
    vec2 cell_idx = floor(frag / cell_size);
    vec2 local = fract(frag / cell_size);

    // Sample the centre of THIS cell
    vec2 cell_centre_pix = (cell_idx + 0.5) * cell_size;
    vec2 cell_centre_uv = cell_centre_pix * SCREEN_PIXEL_SIZE;
    vec3 scene = texture(SCREEN_TEXTURE, cell_centre_uv).rgb;
    float l_centre = luma(scene);

    // Sobel using LUMA samples at +/- cell_size in each direction so
    // the edge detection is at the same coarse resolution as the cell
    // grid. This finds GEOMETRY edges, not pixel noise.
    vec2 step = vec2(cell_size, cell_size) * SCREEN_PIXEL_SIZE;
    float l_W = luma(texture(SCREEN_TEXTURE, cell_centre_uv - vec2(step.x, 0)).rgb);
    float l_E = luma(texture(SCREEN_TEXTURE, cell_centre_uv + vec2(step.x, 0)).rgb);
    float l_N = luma(texture(SCREEN_TEXTURE, cell_centre_uv + vec2(0, step.y)).rgb);
    float l_S = luma(texture(SCREEN_TEXTURE, cell_centre_uv - vec2(0, step.y)).rgb);
    float l_NW = luma(texture(SCREEN_TEXTURE, cell_centre_uv + vec2(-step.x, step.y)).rgb);
    float l_NE = luma(texture(SCREEN_TEXTURE, cell_centre_uv + vec2(step.x, step.y)).rgb);
    float l_SW = luma(texture(SCREEN_TEXTURE, cell_centre_uv + vec2(-step.x, -step.y)).rgb);
    float l_SE = luma(texture(SCREEN_TEXTURE, cell_centre_uv + vec2(step.x, -step.y)).rgb);

    // Standard 3x3 Sobel
    float gx = -l_NW - 2.0 * l_W - l_SW + l_NE + 2.0 * l_E + l_SE;
    float gy = -l_NW - 2.0 * l_N - l_NE + l_SW + 2.0 * l_S + l_SE;
    float edge_mag = sqrt(gx * gx + gy * gy);

    // Is this cell on an edge?
    bool is_edge = edge_mag > edge_threshold;

    float mask = 0.0;
    if (is_edge) {
        // Compute angle, quantize into one of 4 cardinal directions
        // (or detect a corner / cross).
        float angle = atan(gy, gx);
        if (angle < 0.0) angle += 3.14159265;       // wrap to [0, π)
        float deg = degrees(angle);
        // Detect a corner: when BOTH |gx| and |gy| are similar magnitudes
        // (both strong), it's not a clean diagonal — it's a corner.
        float ratio = abs(gx) / max(abs(gy), 0.001);
        bool corner_like = (edge_mag > edge_threshold * 2.5) &&
                            (ratio > 0.5 && ratio < 2.0);

        if (corner_like) {
            mask = draw_cross(local);
        } else if (deg < 22.5 || deg > 157.5) {
            // Near horizontal (gradient mostly along X → horizontal edge)
            mask = (edge_mag > edge_threshold * 2.0) ?
                   draw_horizontal_thick(local) : draw_horizontal(local);
        } else if (deg < 67.5) {
            // Diagonal SE → ╱
            mask = draw_diag_ne(local);
        } else if (deg < 112.5) {
            // Near vertical
            mask = (edge_mag > edge_threshold * 2.0) ?
                   draw_vertical_thick(local) : draw_vertical(local);
        } else {
            // Diagonal NE → ╲
            mask = draw_diag_se(local);
        }
    }
    // Non-edge cells stay EMPTY (just fill colour). The previous version
    // drew a dot in every bright cell, which buried the line work in
    // static noise — user feedback caught that the blueprint look
    // didn't read.

    vec3 line = tint_from_scene ? scene * 1.6 : line_color.rgb;
    vec3 ascii_result = mix(fill_color.rgb, line, mask);

    vec3 result = mix(scene, ascii_result, strength);
    COLOR = vec4(result, 1.0);
}
