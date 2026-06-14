// starscape.gdshader
// ════════════════════════════════════════════════════════════════
// Animated ASCII sky pattern — three layers drifting at different
// speeds over the dark sky pixels of the post-process stack.
//
//   Layer 1 (slow):   spiral-galaxy arms rotating around a point
//   Layer 2 (medium): random twinkling pinpoint stars
//   Layer 3 (faster): fungal-microchip — grid dots + organic branches
//
// Each layer paints into ASCII cells; combined via max() then
// gated by a sky mask (only paints over near-black scene pixels)
// so the boat, ground, and lit elements stay clean.
//
// Insert into the post-process stack AFTER the linework / ASCII
// passes (it samples their output to find the dark sky), but BEFORE
// the demoscene palette quantize (so the palette can still smooth
// any banding the star colours introduce).
// ════════════════════════════════════════════════════════════════

shader_type canvas_item;

uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear;

uniform float strength : hint_range(0.0, 1.0) = 0.0;
uniform float cell_size : hint_range(4.0, 24.0) = 10.0;
uniform float time_scale : hint_range(0.0, 2.0) = 0.40;
// Sky-detection threshold: pixel max-channel < sky_thresh → eligible
// for starscape. Higher value = more permissive (more area gets
// stars). For the linework moods with pure-black fill, 0.10 works.
uniform float sky_thresh : hint_range(0.0, 1.0) = 0.10;

uniform vec4 star_white : source_color = vec4(0.95, 0.92, 0.88, 1.0);
uniform vec4 galaxy_col : source_color = vec4(0.78, 0.85, 1.0, 1.0);
uniform vec4 chip_col   : source_color = vec4(0.55, 0.88, 0.95, 1.0);
uniform vec4 cloud_edge_col  : source_color = vec4(0.55, 0.62, 0.78, 1.0);
uniform vec4 cloud_core_col  : source_color = vec4(0.88, 0.92, 0.98, 1.0);

// Density knobs per layer
uniform float galaxy_strength : hint_range(0.0, 1.0) = 0.6;
uniform float star_strength   : hint_range(0.0, 1.0) = 0.85;
uniform float chip_strength   : hint_range(0.0, 1.0) = 0.45;
uniform float cloud_strength  : hint_range(0.0, 1.0) = 0.0;
uniform float cloud_scale     : hint_range(0.001, 0.05) = 0.012;
uniform float cloud_floor     : hint_range(0.0, 1.0) = 0.55;

float hash11(float p) {
    p = fract(p * 0.1031);
    p *= p + 33.33;
    p *= p + p;
    return fract(p);
}

float hash21(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

// Centred dot glyph
float g_dot(vec2 p, float r) {
    return step(distance(p, vec2(0.5)), r);
}

// 4-point star glyph: + shape (vertical + horizontal stroke).
// Bumped thicker (0.08 → 0.12 stroke half-width) and longer
// (0.35 → 0.42 stroke length) so stars read at typical render
// distance — "starscape still vague" feedback.
float g_star4(vec2 p) {
    float vbar = (abs(p.x - 0.5) < 0.12 && abs(p.y - 0.5) < 0.42) ? 1.0 : 0.0;
    float hbar = (abs(p.y - 0.5) < 0.12 && abs(p.x - 0.5) < 0.42) ? 1.0 : 0.0;
    return max(vbar, hbar);
}

// Asterisk / 8-point — used for galaxy core
float g_asterisk(vec2 p) {
    float plus = g_star4(p);
    float dnw = abs((p.x - 0.5) - (p.y - 0.5)) < 0.08 ? 1.0 : 0.0;
    float dne = abs((p.x - 0.5) + (p.y - 0.5)) < 0.08 ? 1.0 : 0.0;
    float d_mask = (distance(p, vec2(0.5)) < 0.35) ? 1.0 : 0.0;
    return max(plus, max(dnw, dne) * d_mask);
}

// ── Cloud-density glyphs (mimic ░ ▒ ▓) ───────────────────────────
// Light hatch — sparse diagonal lines
float g_light_hatch(vec2 p) {
    float d1 = abs((p.x + p.y) - 0.5);
    float d2 = abs((p.x + p.y) - 1.0);
    return ((d1 < 0.06) || (d2 < 0.06)) ? 1.0 : 0.0;
}
// Medium hatch — denser cross-hatch
float g_medium_hatch(vec2 p) {
    float d1 = abs((p.x + p.y) - 0.5);
    float d2 = abs((p.x + p.y) - 1.0);
    float d3 = abs((p.x - p.y) - 0.0);
    float d4 = abs((p.x - p.y) + 0.5);
    return ((d1 < 0.06) || (d2 < 0.06) || (d3 < 0.06) || (d4 < 0.06)) ? 1.0 : 0.0;
}
// Solid glyph — nearly-filled cell minus 1-pixel margin
float g_solid(vec2 p) {
    return (p.x > 0.10 && p.x < 0.90 && p.y > 0.10 && p.y < 0.90) ? 1.0 : 0.0;
}

// Value-noise primitive — 2D bilinear hash interpolation
float noise2d(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);   // smooth
    float a = hash21(i);
    float b = hash21(i + vec2(1.0, 0.0));
    float c = hash21(i + vec2(0.0, 1.0));
    float d = hash21(i + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

// 3-octave fBM — large complex cloud shapes
float fbm3(vec2 p) {
    float v = 0.0;
    v += 0.500 * noise2d(p);
    v += 0.250 * noise2d(p * 2.07);
    v += 0.125 * noise2d(p * 4.13);
    return v / 0.875;
}

void fragment() {
    vec2 frag = FRAGCOORD.xy;
    vec2 cell_idx = floor(frag / cell_size);
    vec2 local = fract(frag / cell_size);

    // Pre-fetch scene at THIS pixel for the sky mask
    vec3 scene_now = texture(SCREEN_TEXTURE, SCREEN_UV).rgb;
    float scene_max = max(scene_now.r, max(scene_now.g, scene_now.b));
    float sky_mask = 1.0 - smoothstep(sky_thresh * 0.5, sky_thresh, scene_max);

    float t = TIME * time_scale;
    vec3 paint = vec3(0.0);
    float total_mask = 0.0;

    // sky_active gates ALL layer computation — if we're not on a sky
    // pixel, sky_active = 0 and paint stays zero. We can't early-return
    // from a canvas_item fragment() (Godot rejects it), so we compute
    // every layer unconditionally and multiply by sky_active at the end.
    float sky_active = step(0.001, sky_mask);

    // ── LAYER 1: slow galaxy spiral ──────────────────────────────
    // Centred upper-middle of the canvas (was upper-right) so the
    // galaxy is unmistakable when the player looks up. Bigger
    // overall (r scaled 4.0 → 2.8) so the arms reach further. Arm
    // pattern unchanged — cos(theta·2 + r·3 − t·0.25).
    {
        vec2 normalised = (cell_idx * cell_size) * vec2(1.0 / 1280.0, 1.0 / 720.0);
        vec2 g_uv = normalised - vec2(0.50, 0.25);
        g_uv.x *= 1.6;
        float r = length(g_uv) * 2.8;
        float theta = atan(g_uv.y, g_uv.x);
        float arm = cos(theta * 2.0 + r * 3.0 - t * 0.25);
        float arm_mask = smoothstep(0.40, 0.80, arm);
        float core_mask = 1.0 - smoothstep(0.0, 0.30, r);
        float spiral_falloff = 1.0 - smoothstep(0.0, 1.1, r);
        float galaxy_val = max(arm_mask * spiral_falloff, core_mask) * galaxy_strength;
        float glyph = core_mask > 0.5 ? g_asterisk(local) : g_dot(local, 0.12);
        float layer = galaxy_val * glyph;
        paint = max(paint, galaxy_col.rgb * layer);
        total_mask = max(total_mask, layer);
    }

    // ── LAYER 2: random twinkling stars ──────────────────────────
    {
        float seed = hash21(cell_idx);
        float star_active = step(0.978, seed);
        float phase = hash11(seed * 100.0) * 6.2831;
        float twinkle = 0.5 + 0.5 * sin(t * 1.4 + phase);
        float val = twinkle * star_strength * star_active;
        float glyph_pick = hash11(seed * 31.7);
        float glyph = (glyph_pick > 0.65) ? g_star4(local) : g_dot(local, 0.12);
        float layer = val * glyph;
        paint = max(paint, star_white.rgb * layer);
        total_mask = max(total_mask, layer);
    }

    // ── LAYER 4: ASCII clouds — large diffuse penetration ───────
    // 3-octave fBM produces large complex cloud shapes. The
    // (density - floor) subtraction means most sky is CLEAR — only
    // the peaks of the noise field are clouds. Density is mapped to
    // 4 glyph levels so cloud EDGES read as sparse dots (light
    // penetration through diffuse edges) and CORES go dense. Drifts
    // slowly horizontally — long, lazy weather.
    {
        vec2 cell_pix = cell_idx * cell_size;
        vec2 cloud_uv = cell_pix * cloud_scale + vec2(t * 0.025, t * 0.008);
        float n = fbm3(cloud_uv);
        float density = clamp((n - cloud_floor) * 2.4, 0.0, 1.0);
        float density_val = density * cloud_strength;
        // Multi-density glyph pick — diffuse edges to dense cores
        float glyph = 0.0;
        if (density < 0.18) {
            glyph = 0.0;
        } else if (density < 0.38) {
            glyph = g_dot(local, 0.10);          // edge dust
        } else if (density < 0.60) {
            glyph = g_light_hatch(local);
        } else if (density < 0.80) {
            glyph = g_medium_hatch(local);
        } else {
            glyph = g_solid(local);
        }
        vec3 cloud_color = mix(cloud_edge_col.rgb, cloud_core_col.rgb, density);
        float layer = density_val * glyph;
        paint = max(paint, cloud_color * layer);
        total_mask = max(total_mask, layer);
    }

    // ── LAYER 3: fungal microchip ────────────────────────────────
    // Larger-scale (cell_idx * 0.18 → * 0.12) so the chip pattern
    // reads as a distinct organic-circuit field instead of fine
    // noise. Node threshold raised so denser nodes appear.
    {
        vec2 chip_offset = vec2(t * 0.30, t * 0.18);
        vec2 chip_uv = cell_idx * 0.12 + chip_offset;
        float node = hash21(floor(chip_uv));
        float node_val = max(0.0, (node - 0.55) * 2.2) * chip_strength;
        float branch = sin(chip_uv.x * 4.0 + t * 0.7) * sin(chip_uv.y * 3.0 - t * 0.5);
        float branch_val = smoothstep(0.80, 0.95, branch) * chip_strength * 0.85;
        float chip_val = max(node_val, branch_val);
        float glyph_pick = hash11(node * 17.3);
        float glyph = glyph_pick > 0.5 ? g_dot(local, 0.10) : g_star4(local);
        float layer = chip_val * glyph;
        paint = max(paint, chip_col.rgb * layer);
        total_mask = max(total_mask, layer);
    }

    // Composite as ADDITIVE on top of the dark sky so the stars POP
    // bright against the near-black fill. Brightness multiplier 1.6
    // → 2.6 to push the layers HARD against the pure-black field —
    // "starscape still vague" was the feedback; this should make
    // the galaxy + chip patterns unmistakable.
    float final_mask = clamp(total_mask * sky_mask * sky_active * strength, 0.0, 1.0);
    vec3 result = scene_now + paint * final_mask * 2.6;
    COLOR = vec4(result, 1.0);
}
