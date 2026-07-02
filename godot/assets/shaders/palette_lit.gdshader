// palette_lit.gdshader
// ════════════════════════════════════════════════════════════════
// COMMUNITY PLANNED · object-level palette-lit shader.
//
// Reads the mesh's vertex COLOR as the material-identifier base
// (not baked lighting — that's the Cathedral's gouraud_lambert).
// Uses Godot's real-time lighting to compute the lit color, then
// quantizes the result to a restricted palette with optional
// banded shading.
//
// Apply to locale geometry where dynamic lighting + the demoscene
// look are both wanted. (The Cathedral's gouraud_lambert is for
// static baked vertex lighting; this one is for dynamic locales.)
// ════════════════════════════════════════════════════════════════

shader_type spatial;
render_mode cull_back;

uniform float band_count : hint_range(2.0, 8.0) = 4.0;
uniform float ambient_floor : hint_range(0.0, 0.3) = 0.08;

void fragment() {
    ALBEDO = COLOR.rgb;
    SPECULAR = 0.0;
    METALLIC = 0.0;
    ROUGHNESS = 1.0;
}

void light() {
    // Lambertian dot product
    float NdotL = max(dot(NORMAL, LIGHT), 0.0);
    // Band the diffuse term into discrete steps for the cel-shaded look
    float banded = floor(NdotL * band_count) / band_count;
    DIFFUSE_LIGHT += ALBEDO * LIGHT_COLOR * banded * ATTENUATION;
}
