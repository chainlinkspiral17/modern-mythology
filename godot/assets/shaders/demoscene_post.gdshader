// demoscene_post.gdshader
// ════════════════════════════════════════════════════════════════
// COMMUNITY PLANNED · the substrate / demoscene post-process pass.
//
// Apply as a ShaderMaterial on a full-screen ColorRect inside a
// CanvasLayer over the 3D viewport. Reads SCREEN_TEXTURE and
// transforms it into the ASCII / dither / scanline register vol 5
// has always reached for.
//
// Tunable uniforms (per-mood, set from LightController.gd):
//
//   palette_size       · how many colors to quantize to (default 12)
//   dither_strength    · 0..1, how strong the bayer matrix is
//   scanline_strength  · 0..1
//   chromatic_aberration · 0..0.004
//   ascii_strength     · 0..1, 0 = no ASCII overlay, 1 = full
//   phosphor_decay     · NOT IMPLEMENTED here; needs viewport history
//
// Mood preset suggestions (set in LightController):
//   lunch       → palette 16, dither 0.0, scanline 0.0, ascii 0.0
//   dusk        → palette 12, dither 0.15, scanline 0.3, ascii 0.0
//   3:47_am     → palette 10, dither 0.25, scanline 0.5, ascii 0.3
//   precipice   → palette  6, dither 0.45, scanline 0.7, ascii 0.6
//   substrate   → palette  4, dither 0.60, scanline 0.8, ascii 1.0
// ════════════════════════════════════════════════════════════════

shader_type canvas_item;

// filter_linear so the post-process samples smoothly when the
// 1280×720 canvas is stretched to a larger window. filter_nearest
// here makes the entire scene look pixelated/blocky on any window
// scaled above the project's viewport size — every other shader in
// the chain uses filter_linear; this one matches now.
uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear;

uniform float palette_size : hint_range(2.0, 32.0) = 12.0;
uniform float dither_strength : hint_range(0.0, 1.0) = 0.15;
uniform float scanline_strength : hint_range(0.0, 1.0) = 0.30;
uniform float chromatic_aberration : hint_range(0.0, 0.004) = 0.0015;
uniform float ascii_strength : hint_range(0.0, 1.0) = 0.0;
uniform vec4 ascii_color : source_color = vec4(0.85, 0.78, 0.62, 1.0);
uniform vec4 ascii_bg : source_color = vec4(0.06, 0.04, 0.02, 1.0);

// ── per-studio render language (slowsticks; SlowstickLook presets) ──
// 0 none · 1 gouache wash · 2 silkscreen halftone · 3 ink bleed ·
// 4 field-guide grain. Defaults to 0 so CP / gauntlet (which never set
// it) render exactly as before. Each mode is a subtle house STYLE, not a
// filter — kept gentle per the aesthetic bible.
uniform int look_mode = 0;
uniform vec4 paper_tint : source_color = vec4(0.90, 0.86, 0.74, 1.0);
uniform float grain_amount : hint_range(0.0, 1.0) = 0.5;
uniform float ink_amount : hint_range(0.0, 1.0) = 0.6;

float hash12(vec2 p) {
    return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

// Bayer 4×4 ordered dither matrix
const float bayer4[16] = float[](
     0.0,  8.0,  2.0, 10.0,
    12.0,  4.0, 14.0,  6.0,
     3.0, 11.0,  1.0,  9.0,
    15.0,  7.0, 13.0,  5.0
);

float bayer_at(vec2 pixel) {
    int x = int(mod(pixel.x, 4.0));
    int y = int(mod(pixel.y, 4.0));
    return bayer4[y * 4 + x] / 16.0 - 0.5;
}

// 8-character ASCII ramp from light to dark
// (rendered as procedural patterns rather than text glyphs — gives the same density gradient)
float ascii_ramp(float luma, vec2 cell) {
    // Cells are 8×8 pixels. Within each cell, we draw a procedural
    // pattern whose density matches the input luma.
    vec2 c = floor(cell * 8.0) / 8.0;
    float l = luma;
    // Density buckets — each step picks a different fill pattern.
    float fill = 0.0;
    if (l < 0.06) {
        fill = 0.0;                            // space
    } else if (l < 0.20) {
        fill = step(0.88, fract(c.x + c.y));   // sparse dots
    } else if (l < 0.36) {
        fill = step(0.76, fract(c.x * 2.0 + c.y));  // ":"
    } else if (l < 0.52) {
        fill = step(0.62, fract(c.x + c.y * 2.0));  // "-"
    } else if (l < 0.68) {
        fill = step(0.48, fract(c.x * 3.0 - c.y));  // "+"
    } else if (l < 0.82) {
        fill = step(0.32, fract(c.x + c.y));        // "*"
    } else if (l < 0.94) {
        fill = step(0.16, fract(c.x * 2.0 + c.y));  // "#"
    } else {
        fill = 1.0;                            // "@"
    }
    return fill;
}

void fragment() {
    vec2 uv = SCREEN_UV;
    vec2 pixel_coord = FRAGCOORD.xy;

    // ── chromatic aberration ──
    vec3 col;
    col.r = texture(SCREEN_TEXTURE, uv + vec2(chromatic_aberration, 0.0)).r;
    col.g = texture(SCREEN_TEXTURE, uv).g;
    col.b = texture(SCREEN_TEXTURE, uv - vec2(chromatic_aberration, 0.0)).b;

    // ── ordered dither ──
    float d = bayer_at(pixel_coord) * dither_strength;
    col += vec3(d) * 0.06;

    // ── palette quantization ──
    col = floor(col * palette_size) / palette_size;

    // ── per-studio render language ──
    if (look_mode == 1) {
        // gouache wash · paper tooth + gentle value compression toward stock
        float g = (hash12(pixel_coord) - 0.5) * 0.05 * grain_amount;
        col += vec3(g);
        col = mix(col, col * 0.85 + paper_tint.rgb * 0.15, 0.22);
    } else if (look_mode == 2) {
        // silkscreen halftone · posterized inks broken up by the bayer dot
        float luma2 = dot(col, vec3(0.299, 0.587, 0.114));
        float ink = step(bayer_at(pixel_coord) + 0.5, luma2);
        vec3 q = floor(col * 4.0) / 4.0;
        col = mix(q, col, 0.35);
        col *= mix(0.90, 1.0, ink);
    } else if (look_mode == 3) {
        // ink bleed · darken where luminance edges are strong (line pooling)
        float o = 0.0016;
        float lc = dot(texture(SCREEN_TEXTURE, uv).rgb, vec3(0.333));
        float lx = dot(texture(SCREEN_TEXTURE, uv + vec2(o, 0.0)).rgb, vec3(0.333));
        float ly = dot(texture(SCREEN_TEXTURE, uv + vec2(0.0, o)).rgb, vec3(0.333));
        float edge = clamp((abs(lc - lx) + abs(lc - ly)) * 6.0 * ink_amount, 0.0, 0.5);
        col *= (1.0 - edge);
    } else if (look_mode == 4) {
        // field-guide grain · fine warm speckle, near-nothing
        float g2 = (hash12(pixel_coord) - 0.5) * 0.06 * grain_amount;
        col += vec3(g2) + paper_tint.rgb * 0.02;
    }

    // ── scanlines ──
    float scanline = 1.0 - (sin(pixel_coord.y * 3.14159) * 0.5 + 0.5) * scanline_strength * 0.4;
    col *= scanline;

    // ── ASCII overlay (luminance-driven density) ──
    if (ascii_strength > 0.001) {
        float luma = dot(col, vec3(0.299, 0.587, 0.114));
        float a = ascii_ramp(luma, uv);
        vec3 ascii_col = mix(ascii_bg.rgb, ascii_color.rgb, a);
        col = mix(col, ascii_col, ascii_strength);
    }

    COLOR = vec4(col, 1.0);
}
