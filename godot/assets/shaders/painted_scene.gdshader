// painted_scene.gdshader
// ════════════════════════════════════════════════════════════════
// THE PAINTED ROOM (2026-10-02). The Deck, after the heroes became
// watercolour and ink: "background clashing with the new art style
// and models. let's bridge the gap." This is the room's half of the
// same language, a FINAL screen-space pass on the VN background's
// SubViewportContainer (Background3D) — it sees the locale exactly as
// its own post stack left it, and repaints it:
//
//   · WASH — Kuwahara flattening (the flat vertex colours become areas
//     of pigment with soft, slightly irregular borders), a value lift
//     toward the PAPER colour (watercolour is translucent), a little
//     less saturation than the CG, pigment pooling where washes meet
//   · INK  — line work along the colour edges (the locale's flat
//     vertex-colour materials give clean object borders), wobbled and
//     broken where the pen lifts; lighter than the heroes' ink, so the
//     figures stay in front
//   · HATCH — one diagonal in the room's shadows
//   · PAPER — granulation and tooth over everything, and the painting
//     fading to bare paper at the frame margins (a vignette of paper,
//     not of black)
//
// Static: no boil (the same Deck asked for less motion). Screen-space
// only, per the project's honest constraint — no per-mesh shaders.
// `paint` = 0 is a pass-through.
// ════════════════════════════════════════════════════════════════
shader_type canvas_item;

// It paints what is ON SCREEN under it: a full-screen ColorRect in a
// CanvasLayer above the locale's own PostProcess (Background3D's
// PaintedPass; the container's own material slot is TripSync's).
// tools/PaintedBgTest stacks it the same way over a sheet frame.
uniform sampler2D screen_tex : hint_screen_texture, filter_linear_mipmap;

uniform float paint        : hint_range(0.0, 1.0) = 1.0;
uniform float wash         : hint_range(0.0, 1.0) = 0.75;
uniform float wash_radius  : hint_range(1.0, 8.0) = 3.5;
uniform float lift         : hint_range(0.0, 1.0) = 0.35;
uniform float sat          : hint_range(0.0, 1.6) = 0.88;
uniform float ink          : hint_range(0.0, 1.0) = 0.55;
uniform float ink_thr      : hint_range(0.02, 1.2) = 0.42;
uniform float hatch        : hint_range(0.0, 1.0) = 0.35;
uniform float grain        : hint_range(0.0, 1.0) = 0.65;
uniform float margin       : hint_range(0.0, 1.0) = 0.45;
uniform float wobble       : hint_range(0.0, 2.0) = 0.25;   // a whisper: more bends banded light into marble (the diner, 2026-10-02)
uniform vec4  paper_color  : source_color = vec4(0.94, 0.91, 0.84, 1.0);
uniform vec4  ink_color    : source_color = vec4(0.16, 0.13, 0.15, 1.0);

float hash21(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

float vnoise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float a = hash21(i);
    float b = hash21(i + vec2(1.0, 0.0));
    float c = hash21(i + vec2(0.0, 1.0));
    float d = hash21(i + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

float fbm(vec2 p) {
    float v = 0.0;
    float amp = 0.5;
    for (int i = 0; i < 4; i++) {
        v += amp * vnoise(p);
        p *= 2.03;
        amp *= 0.5;
    }
    return v;
}

float luma(vec3 c) { return dot(c, vec3(0.299, 0.587, 0.114)); }

vec3 kuwahara(sampler2D tex, vec2 uv, vec2 px, float r) {
    vec3 best = texture(tex, uv).rgb;
    float bestv = 1e9;
    for (int q = 0; q < 4; q++) {
        vec2 dir = vec2((q == 0 || q == 2) ? -1.0 : 1.0, (q < 2) ? -1.0 : 1.0);
        vec3 m = vec3(0.0);
        vec3 sq = vec3(0.0);
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                vec3 t = texture(tex, uv + dir * vec2(float(i), float(j)) * px * r * 0.5).rgb;
                m += t;
                sq += t * t;
            }
        }
        m /= 9.0;
        vec3 v3 = sq / 9.0 - m * m;
        float v = v3.r + v3.g + v3.b;
        if (v < bestv) {
            bestv = v;
            best = m;
        }
    }
    return best;
}

vec4 paint_from(sampler2D TEX, vec2 uv0, vec2 px) {
    if (paint <= 0.001) {
        return texture(TEX, uv0);
    } else {
        vec2 P = uv0 / px;
        // the brush wanders: a static warp of where pigment and pen land
        vec2 wob = (vec2(vnoise(uv0 * vec2(24.0, 18.0)), vnoise(uv0 * vec2(21.0, 26.0) + 5.7)) - 0.5)
                   * px * 4.0 * wobble * paint;
        vec2 uv = uv0 + wob;
        vec3 src = texture(TEX, uv).rgb;
        // WASH
        vec3 flat_c = kuwahara(TEX, uv, px, wash_radius);
        vec3 col = mix(src, flat_c, wash * paint);
        float l = luma(col);
        col = mix(vec3(l), col, mix(1.0, sat, paint));
        // translucent: values lift toward the paper, not toward white
        col = mix(col, paper_color.rgb - (paper_color.rgb - col) * 0.80, lift * paint);
        // pigment pools where washes meet
        vec3 wide = vec3(0.0);
        for (int i = 0; i < 8; i++) {
            float ang = float(i) * 0.785398 + 0.39;
            wide += texture(TEX, uv + vec2(cos(ang), sin(ang)) * px * 9.0).rgb;
        }
        wide /= 8.0;
        float pool = smoothstep(0.10, 0.45, length(flat_c - wide));   // only real colour borders pool
        col *= 1.0 - pool * 0.22 * wash * paint;
        // INK along the colour edges
        float e;
        {
            // edges read over a 2.5 px reach, in COLOUR not brightness
            // (a red chair on a grey floor is one brightness): the locales'
            // own post bands gradients into rings, and a fine brightness
            // test inked every ring (the diner's ceiling, 2026-10-02)
            vec2 o = px * 2.5;
            vec3 tl = texture(TEX, uv + vec2(-o.x, -o.y)).rgb;
            vec3 tc = texture(TEX, uv + vec2(0.0, -o.y)).rgb;
            vec3 tr = texture(TEX, uv + vec2(o.x, -o.y)).rgb;
            vec3 ml = texture(TEX, uv + vec2(-o.x, 0.0)).rgb;
            vec3 mr = texture(TEX, uv + vec2(o.x, 0.0)).rgb;
            vec3 bl = texture(TEX, uv + vec2(-o.x, o.y)).rgb;
            vec3 bc = texture(TEX, uv + vec2(0.0, o.y)).rgb;
            vec3 br = texture(TEX, uv + vec2(o.x, o.y)).rgb;
            vec3 gx = -tl - 2.0 * ml - bl + tr + 2.0 * mr + br;
            vec3 gy = -tl - 2.0 * tc - tr + bl + 2.0 * bc + br;
            e = sqrt(dot(gx, gx) + dot(gy, gy)) * 0.6;
        }
        float line = smoothstep(ink_thr, ink_thr + 0.25, e);
        line *= mix(1.0, 0.30 + 0.9 * smoothstep(0.25, 0.65, vnoise(P * 0.05)), 0.85);   // the pen lifts
        col = mix(col, ink_color.rgb, clamp(line, 0.0, 1.0) * ink * paint);
        // HATCH in the shadows
        float sh = luma(col);
        float h1 = smoothstep(0.82, 0.97, abs(fract((P.x + P.y) / 8.0) - 0.5) * 2.0);
        float shadow = 1.0 - smoothstep(0.18, 0.38, sh);
        col = mix(col, ink_color.rgb, h1 * shadow * smoothstep(0.3, 0.6, vnoise(P * 0.025 + 3.0)) * 0.45 * hatch * paint);
        // PAPER: granulation, tooth, and the darks never quite black
        float gran = fbm(uv0 * vec2(90.0, 52.0) + 1.3);
        float tooth = fbm(uv0 * vec2(300.0, 170.0));
        col *= 1.0 - (gran - 0.5) * 0.26 * grain * paint;
        col *= mix(1.0, 0.94 + 0.10 * tooth, grain * paint);
        float dk = 1.0 - smoothstep(0.04, 0.22, luma(col));
        col += dk * (0.06 + (gran - 0.5) * 0.12) * grain * paint;
        // the painting thins to bare paper at the margins, raggedly
        vec2 c = uv0 - vec2(0.5);
        float m = smoothstep(0.30, 0.62, length(c * vec2(0.92, 1.25)) + (gran - 0.5) * 0.10);
        col = mix(col, paper_color.rgb, m * margin * paint);
        return vec4(clamp(col, 0.0, 1.0), 1.0);
    }
}

void fragment() {
    COLOR = paint_from(screen_tex, SCREEN_UV, SCREEN_PIXEL_SIZE);
}
