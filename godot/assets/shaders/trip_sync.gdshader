// trip_sync.gdshader
// ════════════════════════════════════════════════════════════════
// THE TRIP · the project-wide psychedelic layer (draft 3, 2026-09-07)
//
// "Realism but trippy, running through the game at all times, in
// lines and backgrounds, synced to the music currently playing."
//
// Deck history in one line each: draft 1 "mostly nausea inducing" ·
// draft 2 (still image) "I like it, but it's rough" · draft 2B
// (faint) "lost all the best parts of it." Draft 3 keeps the best
// parts and removes the specific triggers:
//
//   THE LIQUID   the flats drift slowly, like water under glass —
//                a near-CONSTANT amplitude (6 + 6·energy px, smoothed), a
//                field that moves at a fraction of draft 1's rate,
//                NO beat in it (draft 1 pumped it with the bass; that
//                was the sickness). Edges and text never move.
//                mix_motion is the player's dial; 0 = a still image.
//   LINES        a three-scale Sobel finds the silhouettes and lays
//                the register's aura along them; hue runs along the
//                edge, brightness follows energy, the beat lifts it.
//   COLOUR       the flats breathe in hue (a YIQ rotation, capped
//                cap, ±0.55) and saturation with the mids; a wash of the
//                register's palette into the dark flats on the bar.
//   THE BEAT     a ring of light expands from a drifting centre and
//                lights the lines as it passes; the pulse has a
//                45 ms attack. Never a zoom, never a chroma split,
//                never a whole-frame brightness change.
//   SPARKS       (registers that ask) fixed points that fade slowly.
//
// Two mounting modes, one shader:
//   use_screen = true   full-screen ColorRect in the global layer-60
//                       CanvasLayer (TripSync's own).
//   use_screen = false  material on a TextureRect / SubViewport-
//                       Container (the VN's backgrounds); reads
//                       TEXTURE, so the dialogue box is never touched.
//
// Mesa-safe: float uniforms only. 25 texture taps per fragment.
// amount = 0 is a true identity (per-fragment passthrough).
// ════════════════════════════════════════════════════════════════

shader_type canvas_item;

uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear;
uniform bool use_screen = true;

// ── dials (Settings.trip_amount → amount; the rest are the mix) ──
uniform float amount : hint_range(0.0, 1.0) = 0.6;
uniform float line_amount : hint_range(0.0, 2.0) = 1.0;    // aura on the edges
uniform float flow_amount : hint_range(0.0, 2.0) = 1.0;    // colour wash in the flats
uniform float hue_amount : hint_range(0.0, 2.0) = 1.0;     // hue drift + saturation lift
uniform float ripple_amount : hint_range(0.0, 2.0) = 1.0;  // the beat's ring of light

// ── the player's MIX (Settings.trip_flow / lines / colour / beat) ──
// Four dials multiplied into the register so the balance can be
// found on the Deck. mix_motion is the ONE dial that moves pixels:
// the slow liquid drift in the flats (draft 3). 0 = a still image.
uniform float mix_motion : hint_range(0.0, 1.0) = 1.0;
uniform float mix_lines : hint_range(0.0, 1.0) = 1.0;
uniform float mix_colour : hint_range(0.0, 1.0) = 1.0;
uniform float mix_beat : hint_range(0.0, 1.0) = 1.0;

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
//                 cores, spark storms)
//   spark_amount  additive beat-flashing point field (Minter storms /
//                 the sci-fi starfield) — fixed points, never travelling
//   grain_amount  photocopy grain (zine), static per eighth-second
//   (draft 1's flicker_amount and thump_amount are GONE — see MOTION RULE)
uniform int palette_mode = 0;
uniform float spark_amount : hint_range(0.0, 2.0) = 0.0;
uniform float grain_amount : hint_range(0.0, 2.0) = 0.0;

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
        float aspect = px.y / px.x;             // width / height
        vec2 q = uv * vec2(aspect, 1.0);        // aspect-true coords, height = 1

        // ── edges · three scales averaged into one SOFT mask (draft 2:
        //    the picture under us is already dithered and quantized by
        //    demoscene_post, so a single-scale Sobel reads the dither as
        //    a thousand tiny edges — speckle. Averaging 1.5 / 2.5 / 4 px
        //    and raising the floor leaves only real silhouettes, with an
        //    anti-aliased falloff instead of a hard 1 px rainbow.)
        float e1 = sobel(SCREEN_TEXTURE, TEXTURE, uv, px * 1.5);
        float e2 = sobel(SCREEN_TEXTURE, TEXTURE, uv, px * 2.5);
        float e3 = sobel(SCREEN_TEXTURE, TEXTURE, uv, px * 4.0);
        float edge = (e1 * 0.5 + e2 * 0.3 + e3 * 0.2);
        float line = smoothstep(0.12, 0.42, edge);            // the silhouette itself
        float glow = smoothstep(0.05, 0.30, e3);              // its soft halo
        float density = clamp(glow * 1.2 + line, 0.0, 1.0);   // 1 = busy, keep still
        float open = 1.0 - density;                            // 1 = flat region

        // ── colour field · slow fbm, paced by the music clock. It only
        //    ever drives COLOUR; it never displaces a pixel (draft 2).
        float tf = t_flow;
        vec2 n1 = vec2(
            fbm(q * 1.6 + vec2(tf * 0.05, -tf * 0.035)),
            fbm(q * 1.6 + vec2(5.2 - tf * 0.045, tf * 0.06)));
        float n2 = fbm(q * 2.3 + (n1 - vec2(0.5)) * 1.2 + vec2(tf * 0.025, -tf * 0.02));
        float breath = 0.70 + 0.30 * sin(bar_phase * 6.28318);

        // ── the liquid · a slow, CONSTANT drift of the flats (draft 3).
        //    Draft 1 pumped this with the bass (7 + 22·bass px, breathing
        //    on the bar) and it was the nausea. What stays: an amplitude
        //    that barely changes (4 + 3·energy px, smoothed), a field
        //    that drifts at a fraction of the old rate, no beat in it
        //    at all, and only where the picture is open — edges and
        //    text never move. mix_motion is the player's dial; 0 = still.
        float flow_px = (6.0 + 6.0 * energy) * (0.90 + 0.10 * sin(bar_phase * 6.28318))
                      * flow_amount * mix_motion * amount;
        vec2 disp = (n1 - vec2(0.5)) * px.y * flow_px * open;
        vec3 col = tap(SCREEN_TEXTURE, TEXTURE, uv + disp);

        // ── chroma drift · a small, slow IQ rotation in the flats, lifted by the mids ──
        float y = dot(col, vec3(0.299, 0.587, 0.114));
        float i = dot(col, vec3(0.596, -0.274, -0.322));
        float qq = dot(col, vec3(0.211, -0.523, 0.312));
        float ang = (n2 - 0.5) * 1.05 * (0.40 + 0.60 * energy);
        ang *= hue_amount * mix_colour * amount * (1.0 - density * 0.6);
        ang = clamp(ang, -0.55, 0.55);
        float sat = 1.0 + 0.36 * mid * hue_amount * mix_colour * amount;
        float ci = cos(ang);
        float si = sin(ang);
        float i2 = (i * ci - qq * si) * sat;
        float q2 = (i * si + qq * ci) * sat;
        col = vec3(
            y + 0.956 * i2 + 0.621 * q2,
            y - 0.272 * i2 - 0.647 * q2,
            y - 1.106 * i2 + 1.703 * q2);

        // ── the beat as a ring of LIGHT · lights the lines as it passes, moves nothing ──
        vec2 c = vec2(ring_cx * aspect, ring_cy);
        float r = length(q - c);
        float ring_r = ring_t * 0.9;
        float ring = exp(-pow((r - ring_r) * 4.5, 2.0)) * exp(-ring_t * 1.4) * ripple_amount * mix_beat;
        float kick = pulse * mix_beat;

        // ── aura on the lines · hue runs along the edge, a slow shimmer.
        //    SCREEN-blended, not added: highlights roll off instead of
        //    clipping to white (draft 2 · "rough").
        float hue = fract(hue_base + q.x * 0.08 + q.y * 0.06 + n1.x * 0.30 + beat_phase * 0.04);
        vec3 rainbow = aura_color(hue, kick * 0.7);
        float travel = 0.78 + 0.22 * sin(dot(q, vec2(22.0, 15.0)) - tf * 1.6 + beat_phase * 3.14159 * mix_beat);
        float aura = line_amount * mix_lines * amount * (0.30 + 0.62 * energy + 0.45 * kick + 0.9 * ring);
        vec3 aura_rgb = rainbow * (line * travel * 0.80 + glow * (0.24 + 0.40 * kick + 0.5 * ring) * 0.40) * aura;
        col = 1.0 - (1.0 - col) * (1.0 - clamp(aura_rgb, 0.0, 1.0));

        // ── a faint wash into the dark flats · the flats breathe in colour, not in place ──
        vec3 wash = aura_color(hue_base + 0.5 + n2 * 0.2, 0.0);
        vec3 wash_rgb = wash * (1.0 - y) * open * 0.11 * (0.4 + 0.6 * energy) * breath * flow_amount * mix_colour * amount;
        col = 1.0 - (1.0 - col) * (1.0 - clamp(wash_rgb, 0.0, 1.0));

        // ── sparks · fixed points that flash on the beat (they never travel) ──
        if (spark_amount > 0.001) {
            vec2 cell = floor(q * 44.0);
            float h = hash21(cell);
            vec2 jit = vec2(hash21(cell + vec2(7.0, 3.0)), hash21(cell + vec2(13.0, 5.0))) - vec2(0.5);
            vec2 pt = (cell + vec2(0.5) + jit * 0.8) / 44.0;
            float d = length(q - pt);
            // a slow sine fade per point — never a flash (draft 2B: "strobey")
            float fade = 0.5 + 0.5 * sin(t_flow * (1.2 + 2.4 * h) + h * 40.0 + beat_phase * 6.28318 * step(0.7, h) * mix_beat);
            float twinkle = fade * fade * fade * step(0.45, hash21(cell + vec2(3.0, 11.0)));
            float dot_i = smoothstep(0.0075, 0.0, d) * 0.7;
            float halo = smoothstep(0.035, 0.0, d) * 0.15 * kick;
            vec3 spark_col = aura_color(h + hue_base, kick * 0.6);
            vec3 spark_rgb = spark_col * (dot_i + halo) * twinkle * spark_amount * amount * (0.5 + 0.5 * energy + 0.35 * kick);
            col = 1.0 - (1.0 - col) * (1.0 - clamp(spark_rgb, 0.0, 1.0));
        }

        // ── photocopy grain (zine) · static per eighth-second, low ──
        if (grain_amount > 0.001) {
            float g = hash21(uv / px + vec2(floor(t_flow * 8.0) * 91.0, 0.0)) - 0.5;
            col += vec3(g) * 0.05 * grain_amount * amount;
        }

        COLOR = vec4(clamp(col, 0.0, 1.0), src_a) * v_mod;
    }
}
