// painted_scene.gdshader
// ════════════════════════════════════════════════════════════════
// THE PAINTED ROOM — draft 4, a real watercolour (2026-10-02). The
// Deck on draft 3: "better, but it doesn't look like watercolor at
// all." Drafts 1-3 softened the render and inked its outlines; this
// one paints it, with the watercolour model in watercolor.gdshaderinc:
// wash regions, feathered borders, pigment that pools and settles,
// darker rims where a wash dries, the paper left bare in the lights,
// a pencil under it all. The scene keeps its VALUES (re-keyed to the
// source, highlights over a knee compressed, a dark room never
// brightened) — drafts 1-2 taught that lifting a night scene to cream
// paper is mud.
//
// A FINAL screen-space pass on the VN background (a CanvasLayer in
// Background3D's SubViewport above the locale's own stack; the trip
// rides above this, inked). Static: nothing boils. `paint` 0 = off.
// ════════════════════════════════════════════════════════════════
shader_type canvas_item;

#include "res://assets/shaders/watercolor.gdshaderinc"

uniform sampler2D screen_tex : hint_screen_texture, filter_linear_mipmap;

uniform float paint        : hint_range(0.0, 1.0) = 1.0;
uniform float wash         : hint_range(0.0, 1.0) = 0.85;   // how far the render flattens into wash regions
uniform float wash_radius  : hint_range(1.0, 12.0) = 4.0;   // px: the brush's width (6 ate the riverboat's rails)
uniform float bleed        : hint_range(0.0, 2.0) = 0.8;    // feathering where washes meet
uniform float blotch       : hint_range(0.0, 1.0) = 0.25;   // pigment density, brush-load scale
uniform float grain        : hint_range(0.0, 1.0) = 0.55;   // granulation, paper-tooth scale
uniform float edge_dark    : hint_range(0.0, 2.0) = 0.8;    // pigment pooling at wash rims
uniform float dry          : hint_range(0.0, 1.0) = 0.6;    // the lights left as bare paper
uniform float paper        : hint_range(0.0, 1.0) = 0.75;   // the sheet's tooth over everything
uniform float layers       : hint_range(2.0, 9.0) = 5.0;    // washes come in LAYERS: a gradient is 2-3 washes, not a ramp
uniform float layering     : hint_range(0.0, 1.0) = 0.4;    // how far a smooth gradient becomes stepped washes
uniform float sat          : hint_range(0.0, 1.6) = 1.05;
uniform float pencil       : hint_range(0.0, 1.0) = 0.35;   // the drawing under the paint
uniform float pencil_thr   : hint_range(0.02, 1.2) = 0.40;
uniform float margin       : hint_range(0.0, 1.0) = 0.18;
uniform float wobble       : hint_range(0.0, 2.0) = 0.25;
uniform vec4  paper_color  : source_color = vec4(0.94, 0.91, 0.84, 1.0);
// values: re-keyed to the source, highlights over the knee compressed,
// a downward-only exposure (a room brighter than target_key comes down
// to it; a dark room is never brightened)
uniform float value_keep   : hint_range(0.0, 1.0) = 0.80;
uniform float knee         : hint_range(0.3, 1.0) = 0.66;
uniform float knee_squash  : hint_range(0.0, 1.0) = 0.60;
uniform float target_key   : hint_range(0.1, 0.9) = 0.46;
uniform float expose       : hint_range(0.0, 1.0) = 1.0;
// THE PAPER MOVES WITH THE PICTURE (the Deck, 2026-10-02: "the same
// repeating watercolor wash texture stays static in background, which
// makes it super noticeable"). Screen-space noise sits still while a
// camera track slides the room under it. Background3D pushes the view's
// yaw/pitch as a UV shift every frame, so the blotches, tooth and
// wobble travel with what they are painted on.
uniform vec2 noise_shift = vec2(0.0, 0.0);

vec4 paint_from(sampler2D TEX, vec2 uv0, vec2 px) {
    if (paint <= 0.001) {
        return texture(TEX, uv0);
    }
    vec2 un = uv0 - noise_shift;        // noise coordinates: anchored to the view
    vec2 P = un / px;
    // the hand wanders a little: a static warp of where the brush lands
    vec2 wob = (vec2(wc_vnoise(un * vec2(24.0, 18.0)), wc_vnoise(un * vec2(21.0, 26.0) + 5.7)) - 0.5)
               * px * 4.0 * wobble * paint;
    vec2 uv = uv0 + wob;
    vec3 src = texture(TEX, uv).rgb;
    vec3 wide = wc_ring(TEX, uv, px, 9.0);
    float local = wc_luma(wide);
    // colour edges, read relative to the local light (night edges are small)
    float e = wc_edge(TEX, uv, px * 2.5) * 0.55 / (0.12 + local);

    // ── BLEED: at a border the lookup wanders along low-frequency noise,
    //    so two washes feather into each other instead of meeting at a line
    float border = smoothstep(0.08, 0.5, e);
    vec2 drift = (vec2(wc_fbm(un * vec2(60.0, 34.0)), wc_fbm(un * vec2(53.0, 41.0) + 9.0)) - 0.5)
                 * px * 12.0 * bleed * border * paint;
    // ── WASH: the render flattens into regions of pigment
    vec3 flat_c = wc_kuwahara(TEX, uv + drift, px, wash_radius).rgb;
    vec3 col = mix(src, flat_c, wash * paint);
    float l = wc_luma(col);
    col = mix(vec3(l), col, mix(1.0, sat, paint));
    float g_blotch = wc_fbm(un * vec2(13.0, 7.5) + 1.3);
    float g_tooth = wc_fbm(un * vec2(95.0, 54.0) + 2.0);

    // ── LAYERS: a painter lays a gradient as two or three washes, each
    //    with its own irregular border — the value steps, the threshold
    //    wandering with the brush load, and the hue rides along
    //    — only where there IS a gradient: on a flat dark wall the steps
    //    wandered into a map of blobs (the warehouse, 2026-10-02)
    float lv = max(wc_luma(col), 1e-3);
    float graded = smoothstep(0.015, 0.09, abs(lv - local));
    float stepped = (floor(lv * layers + (g_blotch - 0.5) * 0.5) + 0.5) / layers;
    float lv2 = mix(lv, stepped, layering * graded * paint);
    col *= lv2 / lv;
    float layer_edge = smoothstep(0.0, 0.08, fwidth(stepped)) * layering * graded;

    // ── PIGMENT: density varies inside a wash — blotches the size of a
    //    brush load, granulation at the paper's tooth
    float dens = 1.0 + (g_blotch - 0.5) * 1.3 * blotch * paint + (g_tooth - 0.5) * 0.6 * grain * paint;
    col = wc_pigment(col, dens);
    // ── EDGE DARKENING: pigment pools at the rim of every wash as it dries —
    //    at the colour borders and at the layer borders alike
    float rim = max(smoothstep(0.06, 0.45, e), layer_edge * 0.8) * (0.7 + 0.6 * g_tooth);
    col = wc_pigment(col, 1.0 + 0.6 * rim * edge_dark * paint);
    // ── DRY PAPER: the lights are the sheet left unpainted, broken by the tooth
    float hi = smoothstep(0.72, 0.95, wc_luma(src));
    float dry_mask = hi * smoothstep(0.30, 0.70, g_tooth) * dry * paint;
    col = mix(col, paper_color.rgb, dry_mask);
    // ── PAPER: the sheet's texture over everything; the darks never quite black
    float mottle = wc_fbm(un * vec2(5.0, 3.0) + 7.0);
    col *= mix(1.0, (0.90 + 0.18 * g_tooth) * (0.96 + 0.08 * mottle), paper * paint);
    float dk = 1.0 - smoothstep(0.04, 0.22, wc_luma(col));
    col += dk * (0.02 + (g_tooth - 0.5) * 0.06) * paper * paint;
    // ── PENCIL under the paint: thin, broken, in a darkened local colour
    float line = smoothstep(pencil_thr, pencil_thr + 0.3, e);
    line *= 0.35 + 0.9 * smoothstep(0.30, 0.65, wc_vnoise(P * 0.06));     // the pencil lifts
    vec3 graphite = mix(col * 0.55, vec3(0.22, 0.20, 0.24), 0.5);
    col = mix(col, graphite, clamp(line, 0.0, 1.0) * pencil * paint);

    // ── VALUES: the frame's mean (a 6×5 grid; the back buffer has no mips),
    //    a downward-only exposure, re-key to the source, a highlight knee
    float mean = 0.0;
    for (int gx2 = 0; gx2 < 6; gx2++) {
        for (int gy2 = 0; gy2 < 5; gy2++) {
            vec2 g = vec2((float(gx2) + 0.5) / 6.0, (float(gy2) + 0.5) / 5.0);
            mean += wc_luma(texture(TEX, g).rgb);
        }
    }
    mean /= 30.0;
    float ex = mix(1.0, min(1.0, target_key / max(mean, 1e-3)), expose * paint);
    float tl = wc_luma(src) * ex;
    tl = tl - max(tl - knee, 0.0) * knee_squash;
    // a watercolour sits a little lighter than its subject: the paper shows
    tl = mix(tl, tl * 0.82 + 0.18 * wc_luma(paper_color.rgb), 0.5 * paint);
    float cl = max(wc_luma(col), 1e-3);
    col *= mix(1.0, clamp(tl / cl, 0.4, 1.6), value_keep * paint);
    // ── MARGINS: the painting thins to paper at the local value
    vec2 c = uv0 - vec2(0.5);
    float m = smoothstep(0.32, 0.64, length(c * vec2(0.92, 1.25)) + (g_blotch - 0.5) * 0.10);
    vec3 mt = paper_color.rgb * clamp(local * 1.1, 0.05, 0.95);
    col = mix(col, mt, m * margin * paint);
    return vec4(clamp(col, 0.0, 1.0), 1.0);
}

void fragment() {
    COLOR = paint_from(screen_tex, SCREEN_UV, SCREEN_PIXEL_SIZE);
}
