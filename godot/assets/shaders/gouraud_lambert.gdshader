// gouraud_lambert.gdshader
// ════════════════════════════════════════════════════════════════
// COMMUNITY PLANNED · the Gouraud shader
//
// Reads per-vertex baked lighting from the COLOR_0 attribute (set
// by the Blender build scripts) and outputs it as ALBEDO with the
// unshaded render mode. Real-time lights are ignored by this pass
// — the look IS the bake.
//
// For props that want a runtime light contribution (the workbench
// lamp, the BBS phosphor screen, the river-window directional),
// use the standard Godot StandardMaterial3D on those specific
// faces instead of this shader.
//
// Apply by:
//   1. select the mesh in the scene
//   2. Material Override → New ShaderMaterial → Shader → gouraud_lambert.gdshader
// ════════════════════════════════════════════════════════════════

shader_type spatial;
render_mode unshaded, cull_back, depth_draw_opaque;

uniform float ambient_floor : hint_range(0.0, 0.3) = 0.05;
uniform float saturation : hint_range(0.5, 1.5) = 1.0;

void fragment() {
    vec3 baked = COLOR.rgb;

    // Add a small ambient floor so vertices facing away from all
    // baked lights don't go fully black.
    baked = max(baked, vec3(ambient_floor));

    // Optional saturation push — defaults to 1.0 (no change).
    if (saturation != 1.0) {
        float luma = dot(baked, vec3(0.299, 0.587, 0.114));
        baked = mix(vec3(luma), baked, saturation);
    }

    ALBEDO = baked;
}
