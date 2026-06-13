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

uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_nearest;

uniform float palette_size : hint_range(2.0, 32.0) = 12.0;
uniform float dither_strength : hint_range(0.0, 1.0) = 0.15;
uniform float scanline_strength : hint_range(0.0, 1.0) = 0.30;
uniform float chromatic_aberration : hint_range(0.0, 0.004) = 0.0015;
uniform float ascii_strength : hint_range(0.0, 1.0) = 0.0;
uniform vec4 ascii_color : source_color = vec4(0.85, 0.78, 0.62, 1.0);
uniform vec4 ascii_bg : source_color = vec4(0.06, 0.04, 0.02, 1.0);

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
