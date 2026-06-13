// gouraud_lambert.gdshader
// ════════════════════════════════════════════════════════════════
// COMMUNITY PLANNED · the Gouraud shader (vertex-baked lighting)
//
// Reads per-vertex baked lighting from the COLOR_0 attribute (set
// by the Blender build scripts) and outputs it as unshaded ALBEDO.
// Real-time lights are ignored — the look IS the bake.
//
// Apply via:
//   1. select the mesh (or use CathedralSetup.gd to auto-apply)
//   2. Material Override → New ShaderMaterial → load this shader
//
// Tuning uniforms:
//   brightness     · scale the baked color (1.0 = raw bake, 2.0
//                    is the recommended default · the Blender bake
//                    produces values in 0.05-0.25 range, brightness
//                    pushes them to a normal visible range)
//   ambient_floor  · additive small lift so unlit faces still show
//                    some color (NOT a per-channel max — that would
//                    flatten everything to gray)
//   saturation     · optional saturation push (default 1.0)
//
// IMPORTANT: render_mode is cull_disabled because Blender's
// make_box() builds outward-facing normals on closed boxes; from
// inside a closed box, every interior face is back-facing. With
// cull_back the player inside the warehouse sees nothing.
// ════════════════════════════════════════════════════════════════

shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_opaque;

uniform float brightness : hint_range(0.5, 4.0) = 2.0;
uniform float ambient_floor : hint_range(0.0, 0.3) = 0.05;
uniform float saturation : hint_range(0.5, 1.5) = 1.0;

void fragment() {
    vec3 baked = COLOR.rgb;

    // Brightness scale — the Blender bake produces low-intensity
    // values; this lifts them into a visible range while preserving
    // the warm/cool contrast from the bake's per-vertex shading.
    baked *= brightness;

    // Additive ambient floor (NOT max). Preserves color variation
    // while lifting fully-unlit faces off black.
    baked += vec3(ambient_floor);

    // Optional saturation tweak
    if (saturation != 1.0) {
        float luma = dot(baked, vec3(0.299, 0.587, 0.114));
        baked = mix(vec3(luma), baked, saturation);
    }

    ALBEDO = baked;
}
