// liminal_proximity.gdshader
// ════════════════════════════════════════════════════════════════
// Screen-space cue for "the walls are thin here." Drives off a
// single `strength` uniform that LiminalProximityController.gd
// writes every frame based on the player's distance to the nearest
// liminal-tagged station (per JSON location data).
//
// Three stacked effects, all gated by `strength`:
//
//   1. Radial chromatic aberration — strong at edges, zero at
//      center. Reads as "the picture's fringes are bleeding"
//      rather than "the picture is glitching" (which the demon
//      shader does louder).
//   2. UV wobble — a tiny low-frequency sin-of-sin shimmer that
//      makes the frame feel like it's barely-not-still.
//   3. Tint shift toward `tint_color` — different per subtype:
//        show         → warm sodium (broadcast burnt-in)
//        imagination  → cool desaturated (the unfinished feel)
//        threshold    → deep blue-cyan (the wrong-room cold)
//      LiminalProximityController picks the tint based on the
//      active station's `liminal_type`.
//
// Sits at the END of the post-process stack (after old_film) so
// it modulates everything else (hero/mood treatments are upstream;
// liminal cue overlays).
// ════════════════════════════════════════════════════════════════
shader_type canvas_item;

uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear;

uniform float strength    : hint_range(0.0, 1.0) = 0.0;
uniform float edge_ca     : hint_range(0.0, 0.04) = 0.012;
uniform float wobble_amp  : hint_range(0.0, 0.008) = 0.0018;
uniform float wobble_freq : hint_range(0.1, 6.0) = 0.85;
uniform float tint_amount : hint_range(0.0, 0.6) = 0.18;
uniform vec4  tint_color  : source_color = vec4(0.42, 0.62, 0.78, 1.0);

void fragment() {
    if (strength <= 0.001) {
        COLOR = textureLod(SCREEN_TEXTURE, SCREEN_UV, 0.0);
        return;
    }

    vec2 uv = SCREEN_UV;

    // ── 2. UV wobble (subtle — never more than ~1px on 1280×720)
    float w = sin(TIME * wobble_freq + uv.y * 24.0) *
              cos(TIME * wobble_freq * 0.62 + uv.x * 14.0);
    uv += vec2(w, w * 0.6) * wobble_amp * strength;

    // ── 1. Radial chromatic aberration
    vec2 center = vec2(0.5, 0.5);
    vec2 dir = uv - center;
    float r2 = dot(dir, dir);             // 0 at center, ~0.5 at corners
    float ca = edge_ca * smoothstep(0.04, 0.30, r2) * strength;
    vec3 col;
    col.r = textureLod(SCREEN_TEXTURE, uv + dir * ca,        0.0).r;
    col.g = textureLod(SCREEN_TEXTURE, uv,                   0.0).g;
    col.b = textureLod(SCREEN_TEXTURE, uv - dir * ca,        0.0).b;
    float a = textureLod(SCREEN_TEXTURE, uv, 0.0).a;

    // ── 3. Tint shift — vignette-shaped so edges drift toward
    // tint, center stays mostly itself
    float vignette = smoothstep(0.0, 0.30, r2);
    col = mix(col, tint_color.rgb * dot(col, vec3(0.299, 0.587, 0.114)),
              tint_amount * strength * vignette);

    COLOR = vec4(col, a);
}
