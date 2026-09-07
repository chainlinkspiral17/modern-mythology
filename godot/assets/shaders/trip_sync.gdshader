// trip_sync.gdshader
// ════════════════════════════════════════════════════════════════
// THE TRIP · the project-wide psychedelic layer (draft 1, 2026-09-07)
//
// "Realism but trippy, running through the game at all times, in
// lines and backgrounds, synced to the music currently playing."
//
// The picture stays the picture — no palette crush, no ASCII, no
// fill. Four things ride on top of it, every one of them scaled by
// the music state that TripSync.gd pushes in each frame:
//
//   LINES        a luma-Sobel finds the geometry edges and lays a
//                rainbow aura along them. Hue runs along the edge
//                (position + noise + beat phase), brightness follows
//                the track's energy, the beat pulse flares the glow.
//   BACKGROUNDS  a domain-warped noise field breathes the flat
//                regions — walls, sky, floor, water — by a few
//                pixels. Suppressed where edge density is high, so
//                geometry outlines and TEXT stay sharp; only the
//                empty stretches undulate. Bass sets the amplitude.
//   CHROMA       the hue of the flat regions drifts in the same
//                noise field (a YIQ rotation, capped ~35°) and the
//                saturation lifts with the mids. Colours breathe;
//                nothing turns a wall green.
//   RIPPLE       each detected beat launches a ring from a drifting
//                centre: a radial displacement wave with a short
//                chromatic split that dies in ~0.6 s.
//
// Two mounting modes, one shader:
//   use_screen = true   full-screen ColorRect in the global layer-60
//                       CanvasLayer (TripSync's own). Reads the
//                       screen after every scene PostProcess stack.
//   use_screen = false  material on a TextureRect / SubViewport-
//                       Container (the VN's backgrounds). Reads
//                       TEXTURE, so the dialogue box above it is
//                       never touched.
//
// Mesa-safe: float uniforms only (no vecN constructor defaults —
// see neon_edge's accent_r/g/b note). ~22 texture taps per fragment.
// amount = 0 is a true identity (per-fragment passthrough).
// ════════════════════════════════════════════════════════════════

shader_type canvas_item;

uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear;
uniform bool use_screen = true;

// ── dials (Settings.trip_amount → amount; the rest are the mix) ──
uniform float amount : hint_range(0.0, 1.0) = 0.6;
uniform float line_amount : hint_range(0.0, 2.0) = 1.0;
uniform float flow_amount : hint_range(0.0, 2.0) = 1.0;
uniform float hue_amount : hint_range(0.0, 2.0) = 1.0;
uniform float ripple_amount : hint_range(0.0, 2.0) = 1.0;

// ── music state · written every frame by TripSync.gd ──
uniform float energy = 0.0;      // 0..1 smoothed overall loudness (auto-gained)
uniform float bass = 0.0;        // 0..1 low band
uniform float mid = 0.0;         // 0..1 mid band
uniform float high = 0.0;        // 0..1 high band
uniform float pulse = 0.0;       // beat envelope, 1 on the hit, exp decay
uniform float ring_t = 10.0;     // seconds since the last beat
uniform float beat_phase = 0.0;  // 0..1 inside the current beat (tempo-locked)
uniform float bar_phase = 0.0;   // 0..1 across four beats
uniform float hue_base = 0.0;    // slow hue rotation, 0..1
uniform float t_flow = 0.0;      // music-paced clock for the flow field
uniform float ring_cx = 0.5;     // ripple centre (uv)
uniform float ring_cy = 0.5;

// ── register · the per-pillar look (TripSync.REGISTERS, lerped) ──
//   palette_mode  0 rainbow (base) · 1 swamp phosphor (vol 5, MAJOR
//                 ARCANA: bayou greens + sodium amber on the kick) ·
//                 2 zine duotone (vol 6, PLANNED COMMUNITY: riso pink
//                 + teal, hard-edged, photocopy grain) · 3 liquid light
//                 (vol 7, LAND OF MILK AND HONEY: oil-projector amber /
//                 violet / rose, wall-of-sound dense) · 4 neon vector
//                 (slowsticks: Minter — pure additive rainbow, white
//                 cores, spark storms, the screen thumps on the kick)
//   spark_amount  additive beat-flashing point field (Minter storms /
//                 the sci-fi starfield)
//   grain_amount  photocopy grain (zine)
//   flicker_amount cabinet power dip on the kick (arcade)
//   thump_amount  radial zoom pulse on the beat (Minter)
uniform int palette_mode = 0;
uniform float spark_amount : hint_range(0.0, 2.0) = 0.0;
uniform float grain_amount : hint_range(0.0, 2.0) = 0.0;
uniform float flicker_amount : hint_range(0.0, 2.0) = 0.0;
uniform float thump_amount : hint_range(0.0, 2.0) = 0.0;

// Vertex colour (modulate) carried across: in fragment(), COLOR
// already has TEXTURE folded in, so multiplying by it would apply
// the texture twice in texture mode.
varying vec4 v_mod;

void vertex() {
    v_mod = COLOR;
}

float luma(vec3 c) {
    return dot(c, vec3(0.299, 0.587, 0.114));
}

float hash21(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

float vnoise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    float a = hash21(i);
    float b = hash21(i + vec2(1.0, 0.0));
    float c = hash21(i + vec2(0.0, 1.0));
    float d = hash21(i + vec2(1.0, 1.0));
    return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}

float fbm(vec2 p) {
    float v = 0.0;
    float a = 0.5;
    for (int k = 0; k < 3; k++) {
        v += a * vnoise(p);
        p = p * 2.03 + vec2(17.1, 9.3);
        a *= 0.5;
    }
    return v;
}

vec3 hsv2rgb(vec3 c) {
    vec3 p = abs(fract(c.xxx + vec3(0.0, 2.0 / 3.0, 1.0 / 3.0)) * 6.0 - 3.0);
    return c.z * mix(vec3(1.0), clamp(p - 1.0, 0.0, 1.0), c.y);
}

// The aura colour for a running hue, per register.
vec3 aura_color(float hue, float kick) {
    if (palette_mode == 1) {
        // swamp phosphor: green → cyan water, sodium amber bleeding in on the kick
        vec3 swamp = hsv2rgb(vec3(0.24 + 0.30 * fract(hue), 0.80, 1.0));
        return mix(swamp, vec3(1.0, 0.62, 0.15), kick * 0.55);
    } else if (palette_mode == 2) {
        // zine duotone: two risograph inks, hard-edged — no gradient between them
        float ink = step(0.5, fract(hue * 2.0));
        return mix(vec3(1.0, 0.25, 0.62), vec3(0.05, 0.75, 0.70), ink);
    } else if (palette_mode == 3) {
        // liquid light: an oil projector — amber, rose, violet, the odd cold blue
        float w = fract(hue);
        vec3 c = mix(vec3(1.0, 0.58, 0.16), vec3(0.95, 0.25, 0.45), smoothstep(0.0, 0.35, w));
        c = mix(c, vec3(0.55, 0.22, 0.95), smoothstep(0.35, 0.70, w));
        c = mix(c, vec3(0.20, 0.55, 1.0), smoothstep(0.70, 0.88, w));
        return mix(c, vec3(1.0, 0.58, 0.16), smoothstep(0.88, 1.0, w));
    } else if (palette_mode == 4) {
        // neon vector: saturated rainbow with a white core when the kick lands
        return mix(hsv2rgb(vec3(hue, 1.0, 1.0)), vec3(1.0), kick * 0.35);
    }
    return hsv2rgb(vec3(hue, 0.88, 1.0));
}

vec3 tap(sampler2D scr, sampler2D tex, vec2 uv) {
    if (use_screen) {
        return texture(scr, uv).rgb;
    }
    return texture(tex, uv).rgb;
}

// Sobel edge magnitude at a given sample distance.
float sobel(sampler2D scr, sampler2D tex, vec2 uv, vec2 px) {
    float l00 = luma(tap(scr, tex, uv + vec2(-px.x, -px.y)));
    float l10 = luma(tap(scr, tex, uv + vec2( 0.0,  -px.y)));
    float l20 = luma(tap(scr, tex, uv + vec2( px.x, -px.y)));
    float l01 = luma(tap(scr, tex, uv + vec2(-px.x,  0.0 )));
    float l21 = luma(tap(scr, tex, uv + vec2( px.x,  0.0 )));
    float l02 = luma(tap(scr, tex, uv + vec2(-px.x,  px.y)));
    float l12 = luma(tap(scr, tex, uv + vec2( 0.0,   px.y)));
    float l22 = luma(tap(scr, tex, uv + vec2( px.x,  px.y)));
    float gx = -l00 - 2.0 * l01 - l02 + l20 + 2.0 * l21 + l22;
    float gy = -l00 - 2.0 * l10 - l20 + l02 + 2.0 * l12 + l22;
    return sqrt(gx * gx + gy * gy);
}

void fragment() {
    vec2 uv = use_screen ? SCREEN_UV : UV;
    vec2 px = use_screen ? SCREEN_PIXEL_SIZE : TEXTURE_PIXEL_SIZE;
    float src_a = use_screen ? 1.0 : texture(TEXTURE, UV).a;

    // Identity path — never stamp anything when the dial is off.
    if (amount < 0.001) {
        COLOR = vec4(tap(SCREEN_TEXTURE, TEXTURE, uv), src_a) * v_mod;
    } else {
        // Minter thump: the whole picture breathes in on the kick.
        uv = vec2(0.5) + (uv - vec2(0.5)) * (1.0 - thump_amount * amount * 0.018 * pulse);
        float aspect = px.y / px.x;             // width / height
        vec2 q = uv * vec2(aspect, 1.0);        // aspect-true coords, height = 1

        // ── edges: thin (the line) and wide (the density mask) ──
        float edge = sobel(SCREEN_TEXTURE, TEXTURE, uv, px * 1.25);
        float edge_wide = sobel(SCREEN_TEXTURE, TEXTURE, uv, px * 3.5);
        float line = smoothstep(0.06, 0.30, edge);
        float glow = smoothstep(0.03, 0.22, edge_wide);
        float density = clamp(glow * 1.4 + line, 0.0, 1.0);   // 1 = busy, keep still
        float open = 1.0 - density;                            // 1 = flat region

        // ── flow field · domain-warped fbm, paced by the music clock ──
        float tf = t_flow;
        vec2 n1 = vec2(
            fbm(q * 2.2 + vec2(tf * 0.11, -tf * 0.07)),
            fbm(q * 2.2 + vec2(5.2 - tf * 0.09, tf * 0.13)));
        vec2 warp = n1 - vec2(0.5);
        float n2 = fbm(q * 3.1 + warp * 1.5 + vec2(tf * 0.05, -tf * 0.04));

        float breath = 0.55 + 0.45 * sin(bar_phase * 6.28318);
        float flow_px = (7.0 + 22.0 * bass) * breath * flow_amount * amount;
        vec2 disp = warp * px.y * flow_px * open;

        // ── beat ripple · a ring from a drifting centre ──
        vec2 c = vec2(ring_cx * aspect, ring_cy);
        vec2 to_c = q - c;
        float r = length(to_c) + 0.0001;
        vec2 dir = to_c / r;
        float ring_r = ring_t * 1.15;
        float band = exp(-pow((r - ring_r) * 7.0, 2.0));
        float wave = sin((r - ring_r) * 42.0) * band * exp(-ring_t * 1.7);
        disp += dir * wave * px.y * 16.0 * ripple_amount * amount * (1.0 - density * 0.5);

        // ── sample the breathing picture with a beat-sized chroma split ──
        float ca = (0.00035 + 0.0022 * pulse) * amount * hue_amount;
        vec2 suv = uv + disp;
        vec3 col;
        col.r = tap(SCREEN_TEXTURE, TEXTURE, suv + dir * ca).r;
        col.g = tap(SCREEN_TEXTURE, TEXTURE, suv).g;
        col.b = tap(SCREEN_TEXTURE, TEXTURE, suv - dir * ca).b;

        // ── chroma drift · rotate IQ by a noise angle, lift saturation on the mids ──
        float y = dot(col, vec3(0.299, 0.587, 0.114));
        float i = dot(col, vec3(0.596, -0.274, -0.322));
        float qq = dot(col, vec3(0.211, -0.523, 0.312));
        float ang = (n2 - 0.5) * 1.25 * (0.35 + 0.65 * energy)
                  + sin(bar_phase * 6.28318 + q.x * 2.0) * 0.14 * energy;
        ang *= hue_amount * amount * (1.0 - density * 0.6);
        ang = clamp(ang, -0.62, 0.62);
        float sat = 1.0 + 0.40 * mid * hue_amount * amount;
        float ci = cos(ang);
        float si = sin(ang);
        float i2 = (i * ci - qq * si) * sat;
        float q2 = (i * si + qq * ci) * sat;
        col = vec3(
            y + 0.956 * i2 + 0.621 * q2,
            y - 0.272 * i2 - 0.647 * q2,
            y - 1.106 * i2 + 1.703 * q2);

        // ── rainbow aura on the lines · hue runs along the edge, shimmer travels ──
        float hue = fract(hue_base + q.x * 0.16 + q.y * 0.11 + n1.x * 0.35 + beat_phase * 0.08);
        vec3 rainbow = aura_color(hue, pulse);
        float travel = 0.62 + 0.38 * sin(dot(q, vec2(38.0, 27.0)) - tf * 3.4 + beat_phase * 6.28318);
        float aura = line_amount * amount * (0.28 + 0.62 * energy + 0.55 * pulse);
        col += rainbow * (line * travel * 0.80 + glow * (0.22 + 0.45 * pulse) * 0.35) * aura;

        // ── a faint complementary wash into the dark flats on the bar breath ──
        vec3 wash = aura_color(hue_base + 0.5 + n2 * 0.2, 0.0);
        col += wash * (1.0 - y) * open * 0.07 * energy * breath * flow_amount * amount;

        // ── sparks · a point field that flashes on the beat and rides the flow ──
        if (spark_amount > 0.001) {
            vec2 sq = q + warp * 0.05 * bass;
            vec2 cell = floor(sq * 44.0);
            float h = hash21(cell);
            vec2 jit = vec2(hash21(cell + vec2(7.0, 3.0)), hash21(cell + vec2(13.0, 5.0))) - vec2(0.5);
            vec2 pt = (cell + vec2(0.5) + jit * 0.8) / 44.0;
            float d = length(sq - pt);
            float gate = 0.90 - 0.08 * energy - 0.22 * pulse;
            float twinkle = step(gate, fract(h * 7.0 + t_flow * (0.20 + 0.6 * h) + beat_phase * step(0.5, h)));
            float dot_i = smoothstep(0.0055 + 0.004 * pulse, 0.0, d);
            float halo = smoothstep(0.03, 0.0, d) * 0.25 * pulse;
            vec3 spark_col = aura_color(h + hue_base, pulse);
            col += spark_col * (dot_i + halo) * twinkle * spark_amount * amount * (0.5 + 0.5 * energy + 0.7 * pulse);
        }

        // ── photocopy grain (zine) ──
        if (grain_amount > 0.001) {
            float g = hash21(uv / px + vec2(fract(t_flow * 7.0) * 91.0, 0.0)) - 0.5;
            col += vec3(g) * 0.14 * grain_amount * amount;
        }

        // ── cabinet power dip on the kick (arcade) ──
        if (flicker_amount > 0.001) {
            col *= 1.0 - flicker_amount * amount * 0.10 * pulse * (0.5 + 0.5 * sin(t_flow * 55.0));
        }

        COLOR = vec4(clamp(col, 0.0, 1.0), src_a) * v_mod;
    }
}
