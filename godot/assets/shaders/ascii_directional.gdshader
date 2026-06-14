// ascii_directional.gdshader  (v2 — frame-sampling rewrite)
// ════════════════════════════════════════════════════════════════
// A TRUE per-cell ASCII renderer that "interprets the frame":
//
// 1. The screen is divided into NxN-pixel cells.
// 2. For each cell, we sample the SCREEN_TEXTURE at the cell's CENTER
//    and at the 4 neighbor cells' centers (one screen-texture lookup
//    per cell, not per pixel).
// 3. We compare this cell's luminance to each neighbor's luminance:
//      · |here - W| , |here - E|  → horizontal brightness change
//      · |here - N| , |here - S|  → vertical brightness change
//    A horizontal brightness gradient means a VERTICAL edge runs
//    through this cell (we'd draw │). A vertical gradient means a
//    HORIZONTAL edge (we'd draw ─). Both gradients means a CORNER
//    or CROSSING (we'd draw ┼). Strong diagonal change means a
//    diagonal stroke (╱ or ╲).
// 4. If no edge is detected, we use the cell's own brightness to
//    pick a FILL CHARACTER from a 4-level density ramp (·  ░  ▒  ▓).
// 5. The character is drawn at the fragment's local position within
//    the cell, with strokes extending to the cell edges so adjacent
//    edge-cells visually connect into continuous lines.
//
// User feedback that drove this rewrite: "I really want the ascii
// look nailed down. I think it's possible." / "Is there a way to
// sample the frame and interpret the edges as ascii?" — yes; the
// previous version did per-pixel Sobel arithmetic INSIDE each cell
// which mixed up scales and lost cell-to-cell coherence. This
// version samples PER CELL.
// ════════════════════════════════════════════════════════════════

shader_type canvas_item;

uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear;

uniform float strength : hint_range(0.0, 1.0) = 0.0;
uniform float cell_size : hint_range(4.0, 32.0) = 10.0;
uniform float edge_threshold : hint_range(0.01, 0.5) = 0.10;
uniform vec4 line_color : source_color = vec4(0.92, 0.20, 0.20, 1.0);
uniform vec4 fill_color : source_color = vec4(0.02, 0.02, 0.03, 1.0);
uniform bool tint_from_scene = false;
uniform float input_scale : hint_range(0.1, 2.0) = 1.0;
// input_scale dims the screen before processing — lithograph-style
// moods set this < 1 so a sunlit scene doesn't read as "everything
// is bright" to the brightness fill ramp.

// ── Mono-with-red mode ─────────────────────────────────────────────
// When enabled, glyphs render in only TWO colours: mono_white for
// normal edges and mono_red for cells where the scene colour is
// red-dominant (the D'Ambrosio's sign text, the booth red, neon
// hotspots). Background stays at fill_color (typically pure black).
// This is the "lithograph ASCII" look — solid black with white edge
// glyphs, halftone density for shadows, red only on tagged items.
uniform bool mono_with_red = false;
uniform vec4 mono_white : source_color = vec4(0.95, 0.92, 0.86, 1.0);
uniform vec4 mono_red   : source_color = vec4(0.98, 0.16, 0.18, 1.0);
uniform float red_threshold : hint_range(0.0, 1.0) = 0.20;

float luma(vec3 c) {
    return dot(c, vec3(0.299, 0.587, 0.114));
}

// Sample the screen at a cell-center coordinate (cell index → UV).
float sample_cell_luma(vec2 cell_idx) {
    vec2 cell_centre_pix = (cell_idx + 0.5) * cell_size;
    vec2 uv = cell_centre_pix * SCREEN_PIXEL_SIZE;
    return luma(texture(SCREEN_TEXTURE, uv).rgb * input_scale);
}

// ── Glyph drawing functions ───────────────────────────────────────
// All glyphs draw their strokes spanning the full cell so adjacent
// edge-cells with the same glyph form continuous lines.

// ─  horizontal full-width
float g_horizontal(vec2 p) {
    return (p.y > 0.42 && p.y < 0.58) ? 1.0 : 0.0;
}

// │  vertical full-height
float g_vertical(vec2 p) {
    return (p.x > 0.42 && p.x < 0.58) ? 1.0 : 0.0;
}

// ┼  cross (both)
float g_cross(vec2 p) {
    return max(g_horizontal(p), g_vertical(p));
}

// ╱  diagonal up-right
float g_diag_ne(vec2 p) {
    float d = abs((1.0 - p.y) - p.x);
    return (d < 0.10) ? 1.0 : 0.0;
}

// ╲  diagonal down-right
float g_diag_se(vec2 p) {
    float d = abs(p.x - p.y);
    return (d < 0.10) ? 1.0 : 0.0;
}

// ╳  X (both diagonals)
float g_x(vec2 p) {
    return max(g_diag_ne(p), g_diag_se(p));
}

// ┌ ┐ └ ┘ — corner glyphs for cells where the edge bends
// ┌ top-left corner: vertical from middle down + horizontal from middle right
float g_corner_tl(vec2 p) {
    float v = (p.x > 0.42 && p.x < 0.58 && p.y > 0.42) ? 1.0 : 0.0;
    float h = (p.y > 0.42 && p.y < 0.58 && p.x > 0.42) ? 1.0 : 0.0;
    return max(v, h);
}

// ┐ top-right
float g_corner_tr(vec2 p) {
    float v = (p.x > 0.42 && p.x < 0.58 && p.y > 0.42) ? 1.0 : 0.0;
    float h = (p.y > 0.42 && p.y < 0.58 && p.x < 0.58) ? 1.0 : 0.0;
    return max(v, h);
}

// └ bottom-left
float g_corner_bl(vec2 p) {
    float v = (p.x > 0.42 && p.x < 0.58 && p.y < 0.58) ? 1.0 : 0.0;
    float h = (p.y > 0.42 && p.y < 0.58 && p.x > 0.42) ? 1.0 : 0.0;
    return max(v, h);
}

// ┘ bottom-right
float g_corner_br(vec2 p) {
    float v = (p.x > 0.42 && p.x < 0.58 && p.y < 0.58) ? 1.0 : 0.0;
    float h = (p.y > 0.42 && p.y < 0.58 && p.x < 0.58) ? 1.0 : 0.0;
    return max(v, h);
}

// Density fill characters for non-edge cells
// ·  single dot
float g_dot(vec2 p) {
    return (length(p - vec2(0.5)) < 0.10) ? 1.0 : 0.0;
}

// ░  light shade — sparse dot grid
float g_light(vec2 p) {
    vec2 q = fract(p * 3.0);
    return (length(q - vec2(0.5)) < 0.18) ? 1.0 : 0.0;
}

// ▒  medium shade — denser dot grid
float g_medium(vec2 p) {
    vec2 q = fract(p * 4.0);
    return (length(q - vec2(0.5)) < 0.28) ? 1.0 : 0.0;
}

// ▓  dark shade — almost full
float g_dark(vec2 p) {
    vec2 q = fract(p * 5.0);
    return (length(q - vec2(0.5)) < 0.38) ? 1.0 : 0.0;
}

void fragment() {
    vec2 frag = FRAGCOORD.xy;
    vec2 cell_idx = floor(frag / cell_size);
    vec2 local = fract(frag / cell_size);

    // ── MULTI-SCALE FRAME SAMPLING ─────────────────────────────────
    // Each cell looks at THREE concentric rings of neighbors:
    //   Ring 1 (immediate): N/S/E/W + 4 diagonals → fine-grain edges
    //                       and corner detection
    //   Ring 2 (2 cells away): big silhouette detection — catches the
    //                       outline of large objects that a 1-cell
    //                       Sobel under-detects
    //   Plus this cell's own brightness for the density fill.
    // 13 texture taps per cell, all in screen-space. The "multi-pass"
    // effect the user asked for (edges-then-density-then-far) is
    // achieved by combining all three signals into one glyph choice.
    float l_here = sample_cell_luma(cell_idx);
    float l_W    = sample_cell_luma(cell_idx + vec2(-1.0,  0.0));
    float l_E    = sample_cell_luma(cell_idx + vec2(+1.0,  0.0));
    float l_N    = sample_cell_luma(cell_idx + vec2( 0.0, -1.0));
    float l_S    = sample_cell_luma(cell_idx + vec2( 0.0, +1.0));
    float l_NW   = sample_cell_luma(cell_idx + vec2(-1.0, -1.0));
    float l_NE   = sample_cell_luma(cell_idx + vec2(+1.0, -1.0));
    float l_SW   = sample_cell_luma(cell_idx + vec2(-1.0, +1.0));
    float l_SE   = sample_cell_luma(cell_idx + vec2(+1.0, +1.0));
    // Far ring — 2 cells away. Used to detect long-baseline edges
    // (the silhouette of a whole boat hull, the edge of a roofline)
    // that small-baseline edge detection might miss because adjacent
    // cells share a similar shaded value.
    float l_W2 = sample_cell_luma(cell_idx + vec2(-2.0,  0.0));
    float l_E2 = sample_cell_luma(cell_idx + vec2(+2.0,  0.0));
    float l_N2 = sample_cell_luma(cell_idx + vec2( 0.0, -2.0));
    float l_S2 = sample_cell_luma(cell_idx + vec2( 0.0, +2.0));

    // Brightness gradients at fine + coarse scales
    float dH  = max(abs(l_here - l_W),  abs(l_here - l_E));
    float dV  = max(abs(l_here - l_N),  abs(l_here - l_S));
    // Diagonal gradients (for ╱ ╲)
    float dNW_SE = abs(l_NW - l_SE);
    float dNE_SW = abs(l_NE - l_SW);
    // Coarse-scale gradient (2-cell baseline). Even when fine edge
    // doesn't trip, the coarse edge catches large silhouettes.
    float dH2 = max(abs(l_here - l_W2), abs(l_here - l_E2));
    float dV2 = max(abs(l_here - l_N2), abs(l_here - l_S2));

    float fine_edge   = max(dH, dV);
    float diag_edge   = max(dNW_SE, dNE_SW);
    float coarse_edge = max(dH2, dV2);

    bool is_fine_edge   = fine_edge   > edge_threshold;
    bool is_diag_edge   = diag_edge   > edge_threshold * 1.4;
    // Coarse threshold tightened (was 1.8×) so faint long-baseline
    // shading drift doesn't sprinkle dots across surfaces that should
    // read as solid black.
    bool is_coarse_edge = coarse_edge > edge_threshold * 2.5 && !is_fine_edge;

    float mask = 0.0;

    if (is_fine_edge) {
        bool strong_h = dH > edge_threshold;
        bool strong_v = dV > edge_threshold;

        if (strong_h && strong_v) {
            float h_dir = l_E - l_W;
            float v_dir = l_S - l_N;
            if (h_dir > 0.0 && v_dir > 0.0)      mask = g_corner_tl(local);
            else if (h_dir < 0.0 && v_dir > 0.0) mask = g_corner_tr(local);
            else if (h_dir > 0.0 && v_dir < 0.0) mask = g_corner_bl(local);
            else                                  mask = g_corner_br(local);
        } else if (strong_h) {
            mask = g_vertical(local);
        } else {
            mask = g_horizontal(local);
        }
    } else if (is_diag_edge) {
        // Diagonal silhouette — pick ╱ or ╲ from which diagonal is steeper
        if (dNW_SE > dNE_SW) {
            mask = g_diag_se(local);
        } else {
            mask = g_diag_ne(local);
        }
    } else if (is_coarse_edge) {
        // Faint long-baseline silhouette — sparse dot rather than a
        // bold stroke. This gives "outline of distant geometry" feel
        // without overwhelming the picture with thick lines.
        mask = g_dot(local);
    } else {
        // ── BRIGHTNESS DENSITY FILL ─────────────────────────────────
        // Reference target is mostly PURE BLACK with halftone density
        // only on the brightest surfaces. Earlier ramp started at
        // l=0.02 which flooded the scene; raised the empty cutoff to
        // 0.15 so dim ambient-lit areas read as solid black through
        // the lithograph shader.
        if (l_here < 0.15) {
            mask = 0.0;
        } else if (l_here < 0.30) {
            mask = g_dot(local);
        } else if (l_here < 0.50) {
            mask = g_light(local);
        } else if (l_here < 0.70) {
            mask = g_medium(local);
        } else if (l_here < 0.85) {
            mask = g_dark(local);
        } else {
            mask = max(g_medium(local), g_dark(local));
        }
    }

    vec3 cell_scene_col = texture(SCREEN_TEXTURE,
        (cell_idx + 0.5) * cell_size * SCREEN_PIXEL_SIZE).rgb;
    vec3 line;
    if (mono_with_red) {
        // red dominance = how much the red channel exceeds max(g,b).
        // Items tagged with red (sign text, booths) clear the threshold;
        // warm-yellow lights stay near 0 and pick the white glyph.
        float red_dom = cell_scene_col.r - max(cell_scene_col.g, cell_scene_col.b);
        line = (red_dom > red_threshold) ? mono_red.rgb : mono_white.rgb;
    } else if (tint_from_scene) {
        line = cell_scene_col * 1.6;
    } else {
        line = line_color.rgb;
    }
    vec3 ascii_result = mix(fill_color.rgb, line, mask);

    vec3 scene = texture(SCREEN_TEXTURE, frag * SCREEN_PIXEL_SIZE).rgb;
    vec3 result = mix(scene, ascii_result, strength);
    COLOR = vec4(result, 1.0);
}
