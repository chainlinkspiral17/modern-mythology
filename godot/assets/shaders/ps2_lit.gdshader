// ps2_lit.gdshader
// ════════════════════════════════════════════════════════════════
// Spatial shader for the locales. Vertex-snap in screen space
// (the PlayStation 2's signature polygon wobble — the GS only had
// 24-bit fixed-point screen coordinates with no subpixel precision)
// plus vertex-color albedo + per-vertex Gouraud shading from the
// scene's real Light3D nodes.
//
// Apply as material_override on every MeshInstance3D in a locale.
// LocaleSetup.gd does that automatically when use_palette_shader
// is enabled and palette_shader is set to this resource.
//
// Knobs:
//   ps2_grid       · the effective horizontal resolution to snap
//                    to. Lower = more visible wobble. 256 is harsh
//                    PS2-Lite (Silent Hill 1 vibe), 480 is closer
//                    to PS2 native, 800+ is barely noticeable.
//   wobble_amount  · how much of the snap actually applies. 0 = no
//                    snapping (smooth modern), 1 = full PS2.
//   albedo_boost   · multiplier on the vertex colour. The locales
//                    bake flat material colours into vertex colour;
//                    use this to brighten/darken the whole locale
//                    without re-baking the GLB.
// ════════════════════════════════════════════════════════════════

shader_type spatial;
render_mode cull_back, diffuse_lambert_wrap, vertex_lighting, depth_draw_opaque;

uniform float ps2_grid : hint_range(64.0, 1024.0) = 320.0;
uniform float wobble_amount : hint_range(0.0, 1.0) = 1.0;
uniform float albedo_boost : hint_range(0.1, 3.0) = 1.15;

void vertex() {
    // Project to clip space, then snap NDC.xy to a low-res grid.
    // This recreates the PS2's lack of subpixel precision: as the
    // camera moves a half-pixel, the projected vertex hops to the
    // next snap-step, producing the famous PS2 polygon shimmer.
    vec4 clip = PROJECTION_MATRIX * MODELVIEW_MATRIX * vec4(VERTEX, 1.0);
    float grid = max(ps2_grid, 1.0);

    vec2 ndc = clip.xy / clip.w;
    vec2 snapped = floor(ndc * grid * 0.5) / (grid * 0.5);
    vec2 final_ndc = mix(ndc, snapped, wobble_amount);
    clip.xy = final_ndc * clip.w;

    POSITION = clip;
}

void fragment() {
    ALBEDO = COLOR.rgb * albedo_boost;
    ROUGHNESS = 0.95;
    METALLIC = 0.0;
    SPECULAR = 0.05;
}
