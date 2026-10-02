// portrait_demon_static.gdshader
// ════════════════════════════════════════════════════════════════
// Per-portrait post-process stack. Sits on the SubViewportContainer
// as a material override and samples the viewport texture. SEVEN
// independent effect uniforms (all default-off) so portraits can be
// dialed in ANY combination — not the all-or-nothing demon master
// switch the previous version had:
//
//   1. RGB chromatic aberration  — aberration_str
//   2. Horizontal scanline TEAR  — tear_str
//   3. Static noise overlay      — noise_str
//   4. Signal-drop bands         — dropband_str
//   5. Hue rotation              — hue_shift  (0..1, full wheel)
//   6. Edge vignette             — vignette_str
//   7. Pixelate / down-sample    — pixelate_size (1=off, >1 = step)
//
// `strength` survives as a MASTER multiplier so set_demon_mode(true)
// still works: it pushes strength→1.0 AND defaults the four classic
// demon effects to their canon values. Heroes default strength=0 so
// the master kills everything (pass-through), and the VN debug
// panel can dial in any subset by writing the per-effect uniforms
// directly.
// ════════════════════════════════════════════════════════════════
shader_type canvas_item;

// Master multiplier — at 0 the shader is a pass-through. CharLayer's
// set_demon_mode(true) flips this to 1.0 for demon portraits; the
// VN debug panel can also nudge it for heroes to mix in any of the
// per-effect knobs.
uniform float strength      : hint_range(0.0, 1.0) = 0.0;

// Per-effect strengths — default to a "demon recipe" mix that lights
// up to the v1 look when `strength` is pushed to 1.0. Setting any
// of these to 0 (with strength > 0) lets you isolate single effects.
uniform float aberration_str : hint_range(0.0, 1.0) = 1.0;
uniform float tear_str       : hint_range(0.0, 1.0) = 1.0;
uniform float noise_str      : hint_range(0.0, 1.0) = 1.0;
uniform float dropband_str   : hint_range(0.0, 1.0) = 1.0;

// New independent effects — default OFF so existing portraits keep
// their previous behavior. Debug panel exposes them as per-knob rows.
uniform float hue_shift      : hint_range(0.0, 1.0) = 0.0;
uniform float vignette_str   : hint_range(0.0, 1.0) = 0.0;
uniform float pixelate_size  : hint_range(1.0, 32.0) = 1.0;
uniform float invert_str     : hint_range(0.0, 1.0) = 0.0;
uniform float posterize_lvl  : hint_range(1.0, 32.0) = 32.0;
uniform float bloom_str      : hint_range(0.0, 1.0) = 0.0;
uniform float temp_shift     : hint_range(-1.0, 1.0) = 0.0;
uniform float film_grain_str : hint_range(0.0, 1.0) = 0.0;
uniform float emboss_str     : hint_range(0.0, 1.0) = 0.0;
uniform float duotone_str    : hint_range(0.0, 1.0) = 0.0;
uniform vec4  duotone_a      : source_color = vec4(0.18, 0.08, 0.32, 1.0);
uniform vec4  duotone_b      : source_color = vec4(0.96, 0.62, 0.42, 1.0);
uniform float ascii_str      : hint_range(0.0, 1.0) = 0.0;

// ── THE HERO LOOK (2026-10-01) ─────────────────────────────────
// The Deck: "the models look kinda lame without post-processing and
// effects and mood direction." Every locale renders through its own
// post stack inside its viewport (ascii_render → demoscene_post: neon
// edges, fringe, grade); the 3D heroes were laid over it as clean CG.
// `look` (0..1) runs a hero grade when the demon master is off:
// lens fringe toward the frame edges, contrast / saturation /
// temperature, highlight bloom, moving grain, an inner + outer RIM
// glow on the silhouette in the room's key colour (the locale's neon
// edges, echoed), a figure vignette and a soft fade at the base.
// Portrait3D drives every knob from the room's light and the mood.
uniform float look           : hint_range(0.0, 1.0) = 0.0;
uniform float look_aberr     : hint_range(0.0, 2.0) = 0.35;
uniform float look_contrast  : hint_range(0.5, 1.6) = 1.06;
uniform float look_sat       : hint_range(0.0, 1.6) = 1.0;
uniform float look_temp      : hint_range(-1.0, 1.0) = 0.0;
uniform float look_bloom     : hint_range(0.0, 1.5) = 0.25;
uniform float look_grain     : hint_range(0.0, 1.0) = 0.35;
uniform float look_rim       : hint_range(0.0, 1.5) = 0.55;
uniform vec4  look_rim_color : source_color = vec4(0.70, 0.85, 1.0, 1.0);
uniform vec4  look_shadow    : source_color = vec4(0.10, 0.09, 0.14, 1.0);
uniform float look_vignette  : hint_range(0.0, 1.0) = 0.20;
uniform float look_fade      : hint_range(0.0, 1.0) = 0.6;
// ── THE PAINTED HERO (2026-10-02) ────────────────────────────────
// The Deck: "less plastic, more cartoon sketch, with watercolor vibe."
// On top of the grade: Kuwahara-flattened WASHES (shading becomes
// areas of pigment, the CG gradients and the plastic sheen go), soft
// cel BANDS, pigment pooling at the wash edges, paper GRANULATION,
// broken hand-drawn INK lines (luminance + silhouette edges, wobbled,
// gapped by noise), cross-HATCHING in the shadows, and a ragged
// BLEED of the silhouette into the room. All static: nothing boils.
uniform float look_wash      : hint_range(0.0, 1.0) = 0.8;
uniform float look_cel       : hint_range(0.0, 1.0) = 0.5;
uniform float look_bands     : hint_range(2.0, 8.0) = 4.0;
uniform float look_matte     : hint_range(0.0, 1.0) = 0.8;
uniform float look_ink       : hint_range(0.0, 1.0) = 0.8;
uniform float look_ink_thr   : hint_range(0.02, 0.6) = 0.14;
uniform float look_hatch     : hint_range(0.0, 1.0) = 0.5;
uniform float look_paper     : hint_range(0.0, 1.0) = 0.7;
uniform float look_bleed     : hint_range(0.0, 1.0) = 0.6;
uniform float look_wobble    : hint_range(0.0, 2.0) = 1.0;

uniform float chaos_rate  : hint_range(1.0, 60.0) = 18.0;
uniform float aberration  : hint_range(0.0, 0.04) = 0.012;
uniform float tear_amount : hint_range(0.0, 0.20) = 0.06;
uniform float static_amt  : hint_range(0.0, 1.0) = 0.35;
uniform float dropband    : hint_range(0.0, 1.0) = 0.25;
uniform vec4  tint        : source_color = vec4(0.85, 1.00, 0.85, 1.0);

float hash21(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

float hash11(float x) {
    return fract(sin(x * 78.233) * 43758.5453);
}

// RGB↔HSV helpers for the hue_shift knob.
vec3 rgb2hsv(vec3 c) {
    vec4 K = vec4(0.0, -1.0/3.0, 2.0/3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)),
                d / (q.x + e), q.x);
}

vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0/3.0, 1.0/3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

float luma(vec3 c) { return dot(c, vec3(0.299, 0.587, 0.114)); }

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

// Kuwahara: the flattest of four quadrants wins — painterly areas with
// crisp borders between them (alpha-weighted: the empty background
// does not bleed black into the figure)
vec3 kuwahara(sampler2D tex, vec2 uv, vec2 px, float r) {
    vec3 best = texture(tex, uv).rgb;
    float bestv = 1e9;
    for (int q = 0; q < 4; q++) {
        vec2 dir = vec2((q == 0 || q == 2) ? -1.0 : 1.0, (q < 2) ? -1.0 : 1.0);
        vec3 m = vec3(0.0);
        vec3 sq = vec3(0.0);
        float w = 0.0;
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                vec4 t = texture(tex, uv + dir * vec2(float(i), float(j)) * px * r * 0.5);
                m += t.rgb * t.a;
                sq += t.rgb * t.rgb * t.a;
                w += t.a;
            }
        }
        if (w > 0.01) {
            m /= w;
            vec3 var3 = sq / w - m * m;
            float v = var3.r + var3.g + var3.b;
            if (v < bestv) {
                bestv = v;
                best = m;
            }
        }
    }
    return best;
}

void fragment() {
    // Master gate — strength=0 → pure pass-through.
    if (strength <= 0.001 && look <= 0.001) {
        COLOR = texture(TEXTURE, UV);
    } else if (strength <= 0.001) {
        vec2 px = TEXTURE_PIXEL_SIZE;
        vec2 c = UV - vec2(0.5);
        vec2 P = UV / px;                                   // pixel coords
        // the hand's wobble: a static warp of where the brush and pen land
        vec2 wob = (vec2(vnoise(UV * vec2(38.0, 42.0)), vnoise(UV * vec2(41.0, 37.0) + 7.3)) - 0.5)
                   * px * 3.0 * look_wobble * look;
        vec2 uv = UV + wob;
        vec4 base = texture(TEXTURE, uv);
        float a = base.a;
        // silhouette ring (alpha around this pixel, 4 px)
        float amax = 0.0;
        float amin = 1.0;
        for (int i = 0; i < 8; i++) {
            float ang = float(i) * 0.785398;
            float sa = texture(TEXTURE, uv + vec2(cos(ang), sin(ang)) * px * 4.0).a;
            amax = max(amax, sa);
            amin = min(amin, sa);
        }
        // WASH: flatten the CG shading into areas of pigment
        vec3 flat_c = kuwahara(TEXTURE, uv, px, mix(1.5, 5.0, look_wash));
        vec3 col = mix(base.rgb, flat_c, look_wash * look);
        // de-plastic: the specular sheen folds back into the local colour
        float lum = luma(col);
        float tamed = lum - max(lum - 0.60, 0.0) * 0.75;
        col *= mix(1.0, tamed / max(lum, 1e-3), look_matte * look);
        // soft cel bands
        lum = luma(col);
        float bl = lum * look_bands;
        float q = (floor(bl) + smoothstep(0.30, 0.70, fract(bl))) / look_bands;
        col *= mix(1.0, q / max(lum, 1e-3), look_cel * look);
        // grade: temperature, saturation, contrast, shadows into the room
        col.r += look_temp * 0.10 * look;
        col.b -= look_temp * 0.10 * look;
        lum = luma(col);
        col = mix(vec3(lum), col, mix(1.0, look_sat, look));
        col = (col - 0.5) * mix(1.0, look_contrast, look) + 0.5;
        col = mix(col, col * 0.6 + look_shadow.rgb * 0.4, (1.0 - smoothstep(0.0, 0.35, lum)) * 0.5 * look);
        // watercolour is translucent: values lift toward the paper
        col = mix(col, vec3(1.0) - (vec3(1.0) - col) * 0.88, look_wash * 0.35 * look);
        // pigment pools where washes meet (flat vs a wider average)
        vec3 wide = vec3(0.0);
        float ww = 0.0;
        for (int i = 0; i < 8; i++) {
            float ang = float(i) * 0.785398 + 0.39;
            vec4 t = texture(TEXTURE, uv + vec2(cos(ang), sin(ang)) * px * 7.0);
            wide += t.rgb * t.a;
            ww += t.a;
        }
        wide /= max(ww, 1e-3);
        float pool = clamp(length(flat_c - wide) * 2.2, 0.0, 1.0);
        col *= 1.0 - pool * 0.30 * look_wash * look;
        // granulation: pigment settles in the paper's tooth
        float gran = fbm(UV * vec2(70.0, 74.0) + 3.1);
        float paper = fbm(UV * vec2(210.0, 220.0));
        col *= 1.0 - (gran - 0.5) * 0.30 * look_paper * look;
        col *= mix(1.0, 0.93 + 0.12 * paper, look_paper * look);
        // watercolour has no true black: the deepest washes stay pigment,
        // and the paper's tooth shows through them (hair was a flat blob)
        float dk = 1.0 - smoothstep(0.04, 0.24, luma(col));
        col += dk * (0.07 + (gran - 0.5) * 0.16 + paper * 0.05) * look_paper * look;
        // INK: luminance + silhouette edges, wobbled and broken
        float e = 0.0;
        {
            vec2 o = px * 1.4;
            float tl = luma(texture(TEXTURE, uv + vec2(-o.x, -o.y)).rgb);
            float tc = luma(texture(TEXTURE, uv + vec2(0.0, -o.y)).rgb);
            float tr = luma(texture(TEXTURE, uv + vec2(o.x, -o.y)).rgb);
            float ml = luma(texture(TEXTURE, uv + vec2(-o.x, 0.0)).rgb);
            float mr = luma(texture(TEXTURE, uv + vec2(o.x, 0.0)).rgb);
            float bl2 = luma(texture(TEXTURE, uv + vec2(-o.x, o.y)).rgb);
            float bc = luma(texture(TEXTURE, uv + vec2(0.0, o.y)).rgb);
            float br = luma(texture(TEXTURE, uv + vec2(o.x, o.y)).rgb);
            float gx = -tl - 2.0 * ml - bl2 + tr + 2.0 * mr + br;
            float gy = -tl - 2.0 * tc - tr + bl2 + 2.0 * bc + br;
            e = sqrt(gx * gx + gy * gy);
        }
        float line = smoothstep(look_ink_thr, look_ink_thr + 0.18, e);
        line = max(line, smoothstep(0.15, 0.6, amax - amin) * 0.9);   // the outline
        line *= mix(1.0, 0.35 + 0.9 * smoothstep(0.25, 0.65, vnoise(P * 0.07)), 0.8);   // the pen lifts
        vec3 ink = look_shadow.rgb * 0.55 + vec3(0.03, 0.025, 0.04);
        col = mix(col, ink, clamp(line, 0.0, 1.0) * look_ink * look);
        // HATCHING in the shadows: two diagonals, the second only in the deepest
        float sh = luma(col);
        float h1 = smoothstep(0.80, 0.97, abs(fract((P.x + P.y) / 7.0) - 0.5) * 2.0);
        float h2 = smoothstep(0.80, 0.97, abs(fract((P.x - P.y) / 7.0) - 0.5) * 2.0);
        float shadow1 = 1.0 - smoothstep(0.20, 0.40, sh);
        float shadow2 = 1.0 - smoothstep(0.10, 0.24, sh);
        float hatch = max(h1 * shadow1, h2 * shadow2) * smoothstep(0.3, 0.6, vnoise(P * 0.03 + 11.0));
        col = mix(col, ink, hatch * 0.55 * look_hatch * look);
        // rim: the edge of the figure catches the room's key (softer now)
        float inner = clamp(a - amin, 0.0, 1.0);
        col = mix(col, col + look_rim_color.rgb * 0.6, inner * look_rim * 0.6 * look);
        col *= 1.0 - smoothstep(0.35, 0.85, length(c * vec2(1.0, 0.8))) * look_vignette * look;
        // grain, static (no boil)
        float g = hash21(floor(P)) - 0.5;
        col += g * 0.06 * look_grain * look;
        // BLEED: the silhouette goes ragged and the wash runs past it
        float edge = clamp((1.0 - amin) * amax, 0.0, 1.0);
        float rag = (gran - 0.5) * 1.2 * look_bleed * look * edge;
        float outa = clamp(a + rag, 0.0, 1.0);
        float run = clamp(amax - a, 0.0, 1.0) * look_bleed * look * smoothstep(0.45, 0.75, gran) * 0.55;
        vec3 runc = mix(flat_c, vec3(1.0), 0.35);
        vec3 outc = mix(runc, col, step(0.001, a) * clamp(a / max(outa, 1e-3), 0.0, 1.0));
        outa = max(outa, run);
        outa *= 1.0 - smoothstep(0.80, 1.0, UV.y) * look_fade * look;
        COLOR = vec4(clamp(outc, 0.0, 1.0), outa);
    } else {
        float t_frame = floor(TIME * chaos_rate) / chaos_rate;
        float seed    = t_frame * 11.7;

        vec2 uv = UV;

        // ── 7. Pixelate (snap UV to a grid) ──────────────────
        if (pixelate_size > 1.5) {
            float ps = pixelate_size;
            uv = floor(uv * ps) / ps + (0.5 / ps);
        }

        // ── 2. Horizontal scanline tear ──────────────────────
        float row_seed = hash21(vec2(floor(uv.y * 80.0), seed));
        float tear_active = step(0.86, row_seed);
        float tear_dir    = (hash11(seed + uv.y * 13.0) - 0.5) * 2.0;
        uv.x += tear_dir * tear_amount * tear_active * strength * tear_str;

        // ── 1. RGB chromatic aberration ──────────────────────
        float ab = aberration * (0.6 + 0.4 * sin(seed * 6.28)) * strength * aberration_str;
        float r = texture(TEXTURE, vec2(uv.x + ab, uv.y)).r;
        float g = texture(TEXTURE, uv).g;
        float b = texture(TEXTURE, vec2(uv.x - ab, uv.y)).b;
        float a = texture(TEXTURE, uv).a;
        vec3 col = vec3(r, g, b);

        // ── 5. Hue rotation (gated by strength * hue_shift) ──
        if (hue_shift > 0.001) {
            vec3 hsv = rgb2hsv(col);
            hsv.x = fract(hsv.x + hue_shift * strength);
            col = hsv2rgb(hsv);
        }

        // ── 9. Posterize (banded quantization, color-bleed look) ─
        if (posterize_lvl < 31.5) {
            col = floor(col * posterize_lvl) / posterize_lvl;
        }

        // ── 3. Static noise overlay ──────────────────────────
        float n = hash21(uv * vec2(640.0, 480.0) + seed);
        col += (n - 0.5) * static_amt * strength * noise_str * smoothstep(0.02, 0.10, a);

        // ── 4. Signal-drop bands ─────────────────────────────
        float band_seed   = hash11(floor(uv.y * 18.0) + seed * 3.1);
        float band_active = step(0.93, band_seed) * dropband * strength * dropband_str;
        float band_polarity = step(0.5, hash11(seed));
        col = mix(col, vec3(band_polarity), band_active);

        // ── 8. Invert ───────────────────────────────────────
        if (invert_str > 0.001) {
            col = mix(col, 1.0 - col, invert_str * strength);
        }

        // ── 6. Edge vignette ────────────────────────────────
        if (vignette_str > 0.001) {
            vec2 q = UV - vec2(0.5);
            float v = smoothstep(0.30, 0.78, length(q));
            col = mix(col, col * (1.0 - v), vignette_str * strength);
        }

        // ── 10. Bloom approximation (sample neighbours + add) ─
        if (bloom_str > 0.001) {
            vec2 off = vec2(0.004, 0.0);
            vec3 bloom = texture(TEXTURE, uv + off).rgb;
            bloom += texture(TEXTURE, uv - off).rgb;
            bloom += texture(TEXTURE, uv + off.yx).rgb;
            bloom += texture(TEXTURE, uv - off.yx).rgb;
            bloom *= 0.25;
            // Only the bright parts add — threshold at 0.55
            vec3 hi = max(bloom - vec3(0.55), vec3(0.0)) * 2.0;
            col += hi * bloom_str * strength;
        }

        // ── 11. Colour temperature shift (warm/cool) ─────────
        if (abs(temp_shift) > 0.001) {
            float t = temp_shift * strength;
            col.r = clamp(col.r + t * 0.20, 0.0, 1.0);
            col.b = clamp(col.b - t * 0.20, 0.0, 1.0);
        }

        // ── 12. Film grain (Perlin-ish per-pixel) ────────────
        if (film_grain_str > 0.001) {
            float g = hash21(uv * vec2(1920.0, 1080.0) + vec2(seed * 7.0));
            col += (g - 0.5) * 0.18 * film_grain_str * strength;
        }

        // ── 13. Emboss (Sobel-lite) ──────────────────────────
        if (emboss_str > 0.001) {
            vec2 e = vec2(1.0 / 720.0, 0.0);
            vec3 nx = texture(TEXTURE, uv + e).rgb - texture(TEXTURE, uv - e).rgb;
            vec3 ny = texture(TEXTURE, uv + e.yx).rgb - texture(TEXTURE, uv - e.yx).rgb;
            float edge = length(nx) + length(ny);
            col = mix(col, vec3(0.5) + vec3(edge * 2.0), emboss_str * strength);
        }

        // ── 14. Duotone (luminance → 2-colour gradient) ──────
        if (duotone_str > 0.001) {
            float lum = dot(col, vec3(0.299, 0.587, 0.114));
            vec3 dt = mix(duotone_a.rgb, duotone_b.rgb, lum);
            col = mix(col, dt, duotone_str * strength);
        }

        // ── 15. ASCII overlay (cheap — quantize + cell-noise) ─
        if (ascii_str > 0.001) {
            vec2 cell = floor(uv * vec2(80.0, 45.0));
            float ch = hash21(cell);
            float ck = step(0.5, ch);
            // Multiply against luminance so the "characters" sit
            // where the figure already has brightness
            float lum2 = dot(col, vec3(0.299, 0.587, 0.114));
            col = mix(col, vec3(ck * lum2), ascii_str * strength);
        }

        // Demon tint — only when chromatic/noise effects are strong
        // (preserves the canon sickly-green when running demon recipe;
        // dims the tint when only specific effects are active so a
        // pure hue-shift portrait isn't also green).
        float demon_weight = max(aberration_str, noise_str) * strength * 0.4;
        col *= mix(vec3(1.0), tint.rgb, demon_weight);

        COLOR = vec4(col, a);
    }
}
