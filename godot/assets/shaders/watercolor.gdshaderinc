// watercolor.gdshaderinc
// ════════════════════════════════════════════════════════════════
// THE WATERCOLOUR MODEL (2026-10-02), shared by the painted room
// (painted_scene.gdshader) and the painted hero (portrait_demon_
// static.gdshader's `look` path). The Deck on draft 3: "it doesn't
// look like watercolor at all" — a softened render with outlines is
// not a painting. What reads as watercolour (Bousseau et al. 2006,
// and any wet sheet of Arches):
//
//   ABSTRACTION  colour flattens into WASH regions (Kuwahara, 4×4 taps
//                per quadrant — big enough to make regions, not blur)
//   BLEEDING     where two washes meet, the border feathers: the lookup
//                is displaced by low-frequency noise at the edges
//   PIGMENT      density varies inside a wash — blotches at the scale
//                of a brush load, granulation at the paper's tooth:
//                c' = c · (1 − (1 − c)(d − 1)), d around 1
//   EDGE DARKENING the strongest cue: pigment pools at the rim of a
//                wash as it dries, so every region has a darker edge
//   DRY PAPER    the highlights are the paper left unpainted, broken
//                by the tooth (dry-brush), not white paint
//   PAPER        the sheet's texture over everything, lightly
//
// Lines, if any, are a pencil under the paint: thin, broken, in a
// darkened local colour — never a heavy ink outline.
// ════════════════════════════════════════════════════════════════

float wc_hash21(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

float wc_vnoise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float a = wc_hash21(i);
    float b = wc_hash21(i + vec2(1.0, 0.0));
    float c = wc_hash21(i + vec2(0.0, 1.0));
    float d = wc_hash21(i + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

float wc_fbm(vec2 p) {
    float v = 0.0;
    float amp = 0.5;
    for (int i = 0; i < 4; i++) {
        v += amp * wc_vnoise(p);
        p *= 2.03;
        amp *= 0.5;
    }
    return v;
}

float wc_luma(vec3 c) { return dot(c, vec3(0.299, 0.587, 0.114)); }

// Bousseau's pigment density: d > 1 pools pigment (darker, more
// saturated), d < 1 thins it toward the paper.
vec3 wc_pigment(vec3 c, float d) {
    return clamp(c * (1.0 - (1.0 - c) * (d - 1.0)), 0.0, 1.0);
}

// Kuwahara abstraction: four 4×4 quadrants of reach r (px), the flattest
// wins — painterly regions with crisp borders. Alpha-weighted, so a
// transparent surround (the hero's) does not bleed black in.
vec4 wc_kuwahara(sampler2D tex, vec2 uv, vec2 px, float r) {
    vec3 best = texture(tex, uv).rgb;
    float best_a = texture(tex, uv).a;
    float bestv = 1e9;
    for (int q = 0; q < 4; q++) {
        vec2 dir = vec2((q == 0 || q == 2) ? -1.0 : 1.0, (q < 2) ? -1.0 : 1.0);
        vec3 m = vec3(0.0);
        vec3 sq = vec3(0.0);
        float w = 0.0;
        float aw = 0.0;
        for (int i = 0; i < 4; i++) {
            for (int j = 0; j < 4; j++) {
                vec4 t = texture(tex, uv + dir * vec2(float(i), float(j)) * px * r / 3.0);
                m += t.rgb * t.a;
                sq += t.rgb * t.rgb * t.a;
                w += t.a;
                aw += 1.0;
            }
        }
        if (w > 0.01) {
            m /= w;
            vec3 v3 = sq / w - m * m;
            float v = v3.r + v3.g + v3.b;
            if (v < bestv) {
                bestv = v;
                best = m;
                best_a = w / aw;
            }
        }
    }
    return vec4(best, best_a);
}

// Colour-edge strength (Sobel over a reach of `o` px) — red on grey is
// one brightness, so brightness alone misses the room's borders.
float wc_edge(sampler2D tex, vec2 uv, vec2 o) {
    vec3 tl = texture(tex, uv + vec2(-o.x, -o.y)).rgb;
    vec3 tc = texture(tex, uv + vec2(0.0, -o.y)).rgb;
    vec3 tr = texture(tex, uv + vec2(o.x, -o.y)).rgb;
    vec3 ml = texture(tex, uv + vec2(-o.x, 0.0)).rgb;
    vec3 mr = texture(tex, uv + vec2(o.x, 0.0)).rgb;
    vec3 bl = texture(tex, uv + vec2(-o.x, o.y)).rgb;
    vec3 bc = texture(tex, uv + vec2(0.0, o.y)).rgb;
    vec3 br = texture(tex, uv + vec2(o.x, o.y)).rgb;
    vec3 gx = -tl - 2.0 * ml - bl + tr + 2.0 * mr + br;
    vec3 gy = -tl - 2.0 * tc - tr + bl + 2.0 * bc + br;
    return sqrt(dot(gx, gx) + dot(gy, gy)) * 0.6;
}

// The mean colour in a ring of 8 taps at reach `r` px.
vec3 wc_ring(sampler2D tex, vec2 uv, vec2 px, float r) {
    vec3 s = vec3(0.0);
    for (int i = 0; i < 8; i++) {
        float ang = float(i) * 0.785398 + 0.39;
        s += texture(tex, uv + vec2(cos(ang), sin(ang)) * px * r).rgb;
    }
    return s / 8.0;
}
