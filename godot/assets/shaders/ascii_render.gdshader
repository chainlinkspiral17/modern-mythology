// ascii_render.gdshader
// ════════════════════════════════════════════════════════════════
// A TRUE ASCII renderer. The screen is divided into character cells,
// each cell is replaced by an ASCII glyph chosen by the cell's average
// luminance. The scene literally renders as printed code.
//
// Distinct from ascii_edges (edge-only) and glyph_field (drifting
// overlay) — this is "the scene IS the code," every cell on the
// screen becomes a character, with denser characters representing
// brighter source pixels and empty space representing darkness.
//
// Apply on a CanvasLayer's ColorRect, FIRST in the post-process
// stack (above geometry, before palette quantization). At strength
// 1.0 the entire screen renders as ASCII; lower values let the
// underlying scene bleed through, useful for crossfading the look.
//
// Knobs:
//   cell_size      · pixel dimension of each character cell
//   strength       · 0..1 blend between raw scene and ASCII render
//   fg_color       · the character foreground (the "ink")
//   bg_color       · what fills the cell behind the character
//   tint_from_scene· if true, characters take on the underlying
//                    scene colour instead of fg_color (much more
//                    legible, recommended)
//   gamma          · contrast curve for the luma → character ramp
// ════════════════════════════════════════════════════════════════

shader_type canvas_item;

uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear;

uniform float cell_size : hint_range(4.0, 32.0) = 10.0;
uniform float strength : hint_range(0.0, 1.0) = 1.0;
uniform vec4 fg_color : source_color = vec4(0.92, 0.82, 0.55, 1.0);
uniform vec4 bg_color : source_color = vec4(0.04, 0.03, 0.02, 1.0);
uniform bool tint_from_scene = true;
uniform float gamma : hint_range(0.2, 3.0) = 0.85;

// Returns 1.0 if pixel `p` (local cell coords in [0,1]^2) is part of
// glyph index `idx`. The glyph ramp progresses from sparse to dense.
//   0  · space (empty)
//   1  · single dot ·
//   2  · colon  :
//   3  · dash   -
//   4  · plus   +
//   5  · equals =
//   6  · star   *
//   7  · hash   #
//   8  · percent %
//   9  · solid block ▓
float glyph(int idx, vec2 p) {
    if (idx <= 0) return 0.0;

    if (idx == 1) {
        // single dot near baseline
        return (length(p - vec2(0.50, 0.62)) < 0.07) ? 1.0 : 0.0;
    }
    if (idx == 2) {
        // colon — two stacked dots
        float a = (length(p - vec2(0.50, 0.32)) < 0.075) ? 1.0 : 0.0;
        float b = (length(p - vec2(0.50, 0.66)) < 0.075) ? 1.0 : 0.0;
        return max(a, b);
    }
    if (idx == 3) {
        // dash — short horizontal bar at mid-height
        return (p.y > 0.46 && p.y < 0.54 && p.x > 0.22 && p.x < 0.78) ? 1.0 : 0.0;
    }
    if (idx == 4) {
        // plus
        float h = (p.y > 0.44 && p.y < 0.56 && p.x > 0.22 && p.x < 0.78) ? 1.0 : 0.0;
        float v = (p.x > 0.44 && p.x < 0.56 && p.y > 0.22 && p.y < 0.78) ? 1.0 : 0.0;
        return max(h, v);
    }
    if (idx == 5) {
        // equals — two horizontal bars
        float a = (p.y > 0.34 && p.y < 0.42 && p.x > 0.22 && p.x < 0.78) ? 1.0 : 0.0;
        float b = (p.y > 0.58 && p.y < 0.66 && p.x > 0.22 && p.x < 0.78) ? 1.0 : 0.0;
        return max(a, b);
    }
    if (idx == 6) {
        // star — central cross + diagonals
        float h = (p.y > 0.46 && p.y < 0.54 && p.x > 0.22 && p.x < 0.78) ? 1.0 : 0.0;
        float v = (p.x > 0.46 && p.x < 0.54 && p.y > 0.22 && p.y < 0.78) ? 1.0 : 0.0;
        float d1 = (abs(p.x + p.y - 1.0) < 0.06 && p.x > 0.22 && p.x < 0.78) ? 1.0 : 0.0;
        float d2 = (abs(p.x - p.y) < 0.06 && p.x > 0.22 && p.x < 0.78) ? 1.0 : 0.0;
        return max(max(h, v), max(d1, d2));
    }
    if (idx == 7) {
        // hash — two verticals + two horizontals inside a box
        float in_box = (p.x > 0.18 && p.x < 0.82 && p.y > 0.18 && p.y < 0.82) ? 1.0 : 0.0;
        float v1 = (p.x > 0.32 && p.x < 0.40) ? 1.0 : 0.0;
        float v2 = (p.x > 0.60 && p.x < 0.68) ? 1.0 : 0.0;
        float h1 = (p.y > 0.32 && p.y < 0.40) ? 1.0 : 0.0;
        float h2 = (p.y > 0.60 && p.y < 0.68) ? 1.0 : 0.0;
        return in_box * max(max(v1, v2), max(h1, h2));
    }
    if (idx == 8) {
        // percent — diagonal slash + two small open circles
        float slash = (abs(p.x + p.y - 1.0) < 0.07 && p.x > 0.20 && p.x < 0.80) ? 1.0 : 0.0;
        float d_tl = (length(p - vec2(0.30, 0.30)) > 0.07 &&
                       length(p - vec2(0.30, 0.30)) < 0.13) ? 1.0 : 0.0;
        float d_br = (length(p - vec2(0.70, 0.70)) > 0.07 &&
                       length(p - vec2(0.70, 0.70)) < 0.13) ? 1.0 : 0.0;
        return max(slash, max(d_tl, d_br));
    }
    // 9 — solid block (densest)
    return (p.x > 0.12 && p.x < 0.88 && p.y > 0.10 && p.y < 0.90) ? 1.0 : 0.0;
}

void fragment() {
    vec2 frag = FRAGCOORD.xy;
    vec2 cell_idx = floor(frag / cell_size);
    vec2 local = fract(frag / cell_size);

    // Sample the scene at the centre of THIS cell, not at the fragment
    // — so every fragment inside a cell sees the same source pixel.
    vec2 cell_center_pix = (cell_idx + 0.5) * cell_size;
    vec2 cell_center_uv = cell_center_pix * SCREEN_PIXEL_SIZE;
    vec3 scene = texture(SCREEN_TEXTURE, cell_center_uv).rgb;
    float luma = dot(scene, vec3(0.299, 0.587, 0.114));

    // Luma → character index (0 = space, 9 = solid block). A slight
    // gamma curve biases the ramp so the picture has plenty of mid-
    // density characters (more legible than mostly-space or mostly-
    // dense).
    float ramp = pow(clamp(luma, 0.0, 1.0), gamma);
    int idx = int(clamp(ramp * 9.0 + 0.5, 0.0, 9.0));
    float mask = glyph(idx, local);

    // Foreground: either the configured ink colour, or the scene's
    // own colour brightened so the character shape reads.
    vec3 fg = tint_from_scene ? scene * 1.6 + 0.05 : fg_color.rgb;
    vec3 ascii_pixel = mix(bg_color.rgb, fg, mask);

    // Crossfade between the raw scene and the ASCII render
    vec3 result = mix(scene, ascii_pixel, strength);
    COLOR = vec4(result, 1.0);
}
