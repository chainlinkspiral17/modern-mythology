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

// Density knobs per layer
uniform float galaxy_strength : hint_range(0.0, 1.0) = 0.6;
uniform float star_strength   : hint_range(0.0, 1.0) = 0.85;
uniform float chip_strength   : hint_range(0.0, 1.0) = 0.45;

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

// 4-point star glyph: + shape (vertical + horizontal stroke)
float g_star4(vec2 p) {
    float vbar = (abs(p.x - 0.5) < 0.08 && abs(p.y - 0.5) < 0.35) ? 1.0 : 0.0;
    float hbar = (abs(p.y - 0.5) < 0.08 && abs(p.x - 0.5) < 0.35) ? 1.0 : 0.0;
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

void fragment() {
    vec2 frag = FRAGCOORD.xy;
    vec2 cell_idx = floor(frag / cell_size);
    vec2 local = fract(frag / cell_size);

    // Pre-fetch scene at THIS pixel for the sky mask
    vec3 scene_now = texture(SCREEN_TEXTURE, SCREEN_UV).rgb;
    float scene_max = max(scene_now.r, max(scene_now.g, scene_now.b));
    float sky_mask = 1.0 - smoothstep(sky_thresh * 0.5, sky_thresh, scene_max);

    if (sky_mask <= 0.001) {
        // Not sky — pass scene through unchanged
        COLOR = vec4(scene_now, 1.0);
        return;
    }

    float t = TIME * time_scale;
    vec3 paint = vec3(0.0);
    float total_mask = 0.0;

    // ── LAYER 1: slow galaxy spiral ──────────────────────────────
    // Centre the galaxy in the upper-right of the canvas. Polar coord
    // with arms cos(theta * arms + r * pitch - t). Slow rotation.
    {
        vec2 normalised = (cell_idx * cell_size) * vec2(1.0 / 1280.0, 1.0 / 720.0);
        vec2 g_uv = normalised - vec2(0.75, 0.20);
        g_uv.x *= 1.6;
        float r = length(g_uv) * 4.0;
        float theta = atan(g_uv.y, g_uv.x);
        float arm = cos(theta * 2.0 + r * 3.0 - t * 0.25);
        float arm_mask = smoothstep(0.55, 0.85, arm);
        float core_mask = 1.0 - smoothstep(0.0, 0.25, r);
        float spiral_falloff = 1.0 - smoothstep(0.0, 1.0, r);
        float galaxy_val = max(arm_mask * spiral_falloff, core_mask) * galaxy_strength;
        if (galaxy_val > 0.10) {
            float glyph = core_mask > 0.5 ? g_asterisk(local) : g_dot(local, 0.10);
            paint = max(paint, galaxy_col.rgb * galaxy_val * glyph);
            total_mask = max(total_mask, galaxy_val * glyph);
        }
    }

    // ── LAYER 2: random twinkling stars ──────────────────────────
    // Hash by cell index → ~2 % of cells are stars. Each has a phase
    // offset, twinkles over time. Skip cells already painted by galaxy.
    {
        float seed = hash21(cell_idx);
        if (seed > 0.978) {
            float phase = hash11(seed * 100.0) * 6.2831;
            float twinkle = 0.5 + 0.5 * sin(t * 1.4 + phase);
            float val = twinkle * star_strength;
            // Pick glyph from a 2nd hash — dot vs 4-point star
            float glyph_pick = hash11(seed * 31.7);
            float glyph = (glyph_pick > 0.65) ? g_star4(local) : g_dot(local, 0.12);
            paint = max(paint, star_white.rgb * val * glyph);
            total_mask = max(total_mask, val * glyph);
        }
    }

    // ── LAYER 3: fungal microchip ────────────────────────────────
    // Drifting hex-ish grid of cyan dots with organic branching
    // connections. Grid is the "microchip"; branches grow between
    // adjacent nodes — "fungal." Drifts slowly across the sky.
    {
        vec2 chip_offset = vec2(t * 0.30, t * 0.18);
        vec2 chip_uv = cell_idx * 0.18 + chip_offset;
        float node = hash21(floor(chip_uv));
        float branch_a = hash11(node * 11.0);
        // Sparse node grid
        float node_val = 0.0;
        if (node > 0.62) {
            node_val = (node - 0.62) * 2.6 * chip_strength;
        }
        // Organic branches: a 2-d sine pattern at lower freq
        float branch = sin(chip_uv.x * 4.0 + t * 0.7) * sin(chip_uv.y * 3.0 - t * 0.5);
        float branch_val = smoothstep(0.86, 0.96, branch) * chip_strength * 0.7;
        float chip_val = max(node_val, branch_val);
        if (chip_val > 0.08) {
            float glyph_pick = hash11(node * 17.3);
            float glyph = glyph_pick > 0.5 ? g_dot(local, 0.08) : g_star4(local);
            paint = max(paint, chip_col.rgb * chip_val * glyph);
            total_mask = max(total_mask, chip_val * glyph);
        }
    }

    // Composite over the dark sky scene, gated by sky_mask × strength
    float final_mask = clamp(total_mask * sky_mask * strength, 0.0, 1.0);
    vec3 result = mix(scene_now, paint, final_mask);
    COLOR = vec4(result, 1.0);
}
