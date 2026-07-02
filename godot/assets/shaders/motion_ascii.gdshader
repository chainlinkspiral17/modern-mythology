// motion_ascii.gdshader
// ════════════════════════════════════════════════════════════════
// Anime / cartoon motion ASCII layer. Adds speed-line "whoosh"
// glyphs and a streaking motion-trail effect to the post-process
// composite based on the player's screen-space motion vector.
//
//   Speed lines: radial / parallel ASCII strokes that intensify
//   with speed and fade toward the centre of the frame, painted
//   only where the scene is dark enough not to overprint important
//   detail.
//
//   Motion trail: a directional streak — taps the SCREEN_TEXTURE
//   along motion_dir at multiple offsets, max-blends them, gives
//   the cartoon "after-image" smear.
//
// motion_speed (0..1) gates both effects: standing still = both
// off, sprinting = full effect.
//
// motion_dir is the on-screen motion vector (already projected to
// 2D), typically set by MoodCycler reading the player velocity.
// ════════════════════════════════════════════════════════════════
shader_type canvas_item;

uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear;

uniform float strength : hint_range(0.0, 1.0) = 0.0;
uniform float motion_speed : hint_range(0.0, 1.0) = 0.0;
uniform vec2 motion_dir = vec2(1.0, 0.0);
uniform float cell_size : hint_range(4.0, 24.0) = 9.0;
uniform vec4 line_color : source_color = vec4(1.0, 0.98, 0.92, 1.0);
uniform float trail_strength : hint_range(0.0, 1.0) = 0.6;
uniform float line_density   : hint_range(0.0, 1.0) = 0.85;

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

void fragment() {
    vec3 scene = texture(SCREEN_TEXTURE, SCREEN_UV).rgb;
    if (strength < 0.001 || motion_speed < 0.01) {
        COLOR = vec4(scene, 1.0);
    } else {
        vec2 dir = (length(motion_dir) > 0.001) ? normalize(motion_dir) : vec2(1.0, 0.0);
        vec2 perp = vec2(-dir.y, dir.x);

        // ── MOTION TRAIL · directional max-blend smear ──
        vec3 trail = scene;
        float tw = 0.0;
        for (int i = 1; i <= 6; i++) {
            float fi = float(i);
            vec2 off = -dir * fi * 2.2 * SCREEN_PIXEL_SIZE * motion_speed * 9.0;
            vec3 s = texture(SCREEN_TEXTURE, SCREEN_UV + off).rgb;
            // max-blend keeps highlights streaking (anime feel)
            trail = max(trail, s * (1.0 - fi * 0.10));
            tw += 1.0;
        }

        // ── SPEED LINES · per-cell ASCII strokes parallel to motion ──
        vec2 frag = FRAGCOORD.xy;
        vec2 cell_idx = floor(frag / cell_size);
        vec2 local = fract(frag / cell_size);

        // Bias cells toward the SIDES of the frame so the centre stays
        // readable. uv_lateral measures perpendicular distance from
        // the motion axis through the screen centre.
        vec2 centered = SCREEN_UV - vec2(0.5);
        float lateral = abs(dot(centered, perp)) * 2.0;        // 0 centre → ~1 edge
        float edge_bias = smoothstep(0.20, 0.85, lateral);

        // Hash + density decides which cells get a stroke
        float seed = hash21(cell_idx);
        float threshold = 1.0 - line_density * motion_speed * edge_bias;
        float cell_active = step(threshold, seed);

        // Stroke glyph: a thick line parallel to motion direction,
        // running through the cell centre. We project (local - 0.5)
        // onto perp; small projection = on the line.
        vec2 lp = local - vec2(0.5);
        float perp_dist = abs(dot(lp, perp));
        float along = dot(lp, dir);
        float line_mask = step(perp_dist, 0.08) * step(abs(along), 0.40);

        // Twinkle / animate
        float twinkle = 0.6 + 0.4 * sin(TIME * 30.0 + seed * 100.0);
        float line = cell_active * line_mask * twinkle;

        vec3 with_lines = mix(trail, line_color.rgb, line * 0.85);

        // Final: mix the original scene toward the with-trail+lines
        // result based on motion_speed AND the layer's master strength.
        float gate = strength * motion_speed;
        vec3 out_col = mix(scene, with_lines, gate);
        // Trail still fades in even at low motion speed
        out_col = mix(out_col, trail, trail_strength * gate * 0.5);
        COLOR = vec4(out_col, 1.0);
    }
}
