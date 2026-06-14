// lens_distort.gdshader
// ════════════════════════════════════════════════════════════════
// Skaterpunk lens / fisheye warp layer. Three effects, all gated
// by `strength`:
//
//   1. Barrel distortion — radial UV warp from the centre. Positive
//      barrel = fisheye (centre stays, edges stretch outward).
//      Negative barrel = pincushion. Vary with TIME for breathing.
//   2. Radial chromatic dispersion — R / B channels sample at
//      slightly different radii, splitting colour at the edges
//      (cheap "real lens" feel).
//   3. Edge darken — soft vignette tied to the same radius so the
//      eye returns to the centre instead of the warped edge.
//
// Place AFTER everything (last post-process before the screen) so
// the warp is the final lens through which the player sees the
// composite. MoodCycler can crank `barrel` over time for the
// breathing-fisheye effect.
// ════════════════════════════════════════════════════════════════
shader_type canvas_item;

uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear;

uniform float strength : hint_range(0.0, 1.0) = 0.0;
uniform float barrel : hint_range(-0.6, 0.6) = 0.30;
uniform float chroma : hint_range(0.0, 0.04) = 0.012;
uniform float edge_darken : hint_range(0.0, 1.0) = 0.40;
uniform float zoom : hint_range(0.5, 1.5) = 1.0;
// zoom compensates for barrel positive (which pushes content out
// past the screen). MoodCycler can swing it for a breathing punch.

void fragment() {
    vec2 uv = SCREEN_UV;
    if (strength < 0.001) {
        COLOR = vec4(texture(SCREEN_TEXTURE, uv).rgb, 1.0);
    } else {
        vec2 centered = uv - vec2(0.5);
        float r = length(centered);
        // Radial warp: barrel * r^2 term gives classic lens curve.
        // Positive barrel pushes outward (fisheye), negative pulls in.
        float warp = 1.0 + barrel * r * r;
        vec2 warped = centered * warp / zoom + vec2(0.5);

        // Radial chromatic dispersion — R samples a bit further out,
        // B a bit further in, G at the warp point.
        float r_off = chroma * r;
        vec2 dir = normalize(centered + vec2(0.0001));
        vec2 uv_r = warped + dir * r_off;
        vec2 uv_g = warped;
        vec2 uv_b = warped - dir * r_off;

        vec3 col;
        col.r = texture(SCREEN_TEXTURE, uv_r).r;
        col.g = texture(SCREEN_TEXTURE, uv_g).g;
        col.b = texture(SCREEN_TEXTURE, uv_b).b;

        // Edge darken — tied to the same radius so the effect
        // builds with the warp.
        float vignette = 1.0 - smoothstep(0.30, 0.85, r) * edge_darken;
        col *= vignette;

        // Crossfade base scene → warped at strength
        vec3 base = texture(SCREEN_TEXTURE, uv).rgb;
        COLOR = vec4(mix(base, col, strength), 1.0);
    }
}
