"""_props/make_locale_tscn.py — generator for full-feature-parity
locale .tscn files.

Per `_VOL5_LOCALES_MANIFEST.md`'s hard rule, every locale must
include all 8 elements (WorldEnvironment + three-light foundation
+ GLB + PostProcess+MoodCycler+9-shader stack + LiminalProximity
+ PDPRiffmaster + HUD+DebugMenu). Hand-writing each one is ~260
lines of mechanical boilerplate. This generator takes a config
dict and renders the canonical .tscn.

Usage from a build / one-shot script:

    from _props.make_locale_tscn import write_locale_tscn
    write_locale_tscn({
        "out_path": "godot/scenes/locales/foo.tscn",
        "uid": "uid://foo_id",
        "root_node": "Foo",
        "glb": "res://assets/3d/locales/foo.glb",
        "env": { ... },              # bg / amb / fog / glow knobs
        "shader": { ... },           # warm / bg / neon_edge / neon_lo / neon_hi / lim_tint
        "lights": [ (name, type, xform, color, energy), ... ],
        "mood_strata": [...],
    })

All paths are resolved by the CALLER — generator only writes the
content. Lights with type 'OmniLight3D' get a default omni_range
of 4.0 (override per-locale if needed).
"""

TEMPLATE = '''[gd_scene load_steps=24 format=3 uid="{uid}"]

[ext_resource type="PackedScene" path="{glb}" id="1_glb"]
[ext_resource type="Script" path="res://scripts/DebugHUD.gd" id="3_hud"]
[ext_resource type="Shader" path="res://assets/shaders/demoscene_post.gdshader" id="4_post"]
[ext_resource type="Script" path="res://scripts/MoodCycler.gd" id="5_mood"]
[ext_resource type="Shader" path="res://assets/shaders/ascii_render.gdshader" id="6_ascii"]
[ext_resource type="Shader" path="res://assets/shaders/neon_edge.gdshader" id="7_neon"]
[ext_resource type="Shader" path="res://assets/shaders/ascii_directional.gdshader" id="8_dir"]
[ext_resource type="Shader" path="res://assets/shaders/starscape.gdshader" id="9_star"]
[ext_resource type="Shader" path="res://assets/shaders/motion_ascii.gdshader" id="10_motion"]
[ext_resource type="Shader" path="res://assets/shaders/gauss_blur.gdshader" id="11_blur"]
[ext_resource type="Shader" path="res://assets/shaders/old_film.gdshader" id="12_oldfilm"]
[ext_resource type="Script" path="res://scripts/PDPRiffmaster.gd" id="13_riff"]
[ext_resource type="Script" path="res://scripts/DebugMenu.gd" id="14_dbgm"]
[ext_resource type="Shader" path="res://assets/shaders/liminal_proximity.gdshader" id="15_lim"]
[ext_resource type="Script" path="res://scripts/LiminalProximityController.gd" id="16_limc"]

[sub_resource type="ShaderMaterial" id="Mat_Post"]
shader = ExtResource("4_post")
shader_parameter/palette_size = 14.0
shader_parameter/dither_strength = 0.10
shader_parameter/scanline_strength = 0.18
shader_parameter/chromatic_aberration = 0.0008
shader_parameter/ascii_strength = 0.0
shader_parameter/ascii_color = {warm}
shader_parameter/ascii_bg = {shader_bg}

[sub_resource type="ShaderMaterial" id="Mat_Ascii"]
shader = ExtResource("6_ascii")
shader_parameter/cell_size = 10.0
shader_parameter/strength = 0.0
shader_parameter/fg_color = {warm}
shader_parameter/bg_color = {shader_bg}
shader_parameter/tint_from_scene = true
shader_parameter/gamma = 0.85

[sub_resource type="ShaderMaterial" id="Mat_Neon"]
shader = ExtResource("7_neon")
shader_parameter/strength = 0.0
shader_parameter/edge_threshold = 0.10
shader_parameter/edge_thickness = 1.6
shader_parameter/edge_color = {neon_edge}
shader_parameter/fill_low = {neon_lo}
shader_parameter/fill_high = {neon_hi}
shader_parameter/fill_gradient = 1.0
shader_parameter/edge_glow = 0.4
shader_parameter/scene_blend = 0.0
shader_parameter/bleed_lo = 0.78
shader_parameter/bleed_hi = 0.96
shader_parameter/sat_bleed = false
shader_parameter/sat_lo = 0.40
shader_parameter/sat_hi = 0.60
shader_parameter/red_only = false
shader_parameter/accent_r = 1.0
shader_parameter/accent_g = 0.0
shader_parameter/accent_b = 0.0
shader_parameter/blend_mode = 0

[sub_resource type="ShaderMaterial" id="Mat_DirAscii"]
shader = ExtResource("8_dir")
shader_parameter/strength = 0.0
shader_parameter/cell_size = 10.0
shader_parameter/edge_threshold = 0.10
shader_parameter/line_color = {neon_edge}
shader_parameter/fill_color = Color(0.02, 0.02, 0.03, 1)
shader_parameter/tint_from_scene = false
shader_parameter/input_scale = 1.0
shader_parameter/mono_with_red = false
shader_parameter/mono_white = {warm}
shader_parameter/mono_red = {neon_edge}
shader_parameter/red_threshold = 0.20

[sub_resource type="ShaderMaterial" id="Mat_Starscape"]
shader = ExtResource("9_star")
shader_parameter/strength = 0.0
shader_parameter/cell_size = 10.0
shader_parameter/time_scale = 0.40
shader_parameter/sky_thresh = 0.10
shader_parameter/star_white = {warm}
shader_parameter/galaxy_col = Color(0.78, 0.82, 0.95, 1)
shader_parameter/chip_col = Color(0.62, 0.78, 0.88, 1)
shader_parameter/galaxy_strength = 0.6
shader_parameter/star_strength = 0.85
shader_parameter/chip_strength = 0.45
shader_parameter/cloud_edge_col = Color(0.62, 0.70, 0.82, 1)
shader_parameter/cloud_core_col = Color(0.85, 0.88, 0.95, 1)
shader_parameter/cloud_strength = 0.0
shader_parameter/cloud_scale = 0.012
shader_parameter/cloud_floor = 0.55
shader_parameter/force_full = false

[sub_resource type="ShaderMaterial" id="Mat_Motion"]
shader = ExtResource("10_motion")
shader_parameter/strength = 0.0
shader_parameter/motion_speed = 0.0
shader_parameter/motion_dir = Vector2(1, 0)
shader_parameter/cell_size = 9.0
shader_parameter/line_color = {warm}
shader_parameter/trail_strength = 0.6
shader_parameter/line_density = 0.85

[sub_resource type="ShaderMaterial" id="Mat_Blur"]
shader = ExtResource("11_blur")
shader_parameter/strength = 0.0
shader_parameter/blur_mode = 0
shader_parameter/radius = 4.0
shader_parameter/motion_dir = Vector2(1, 0)

[sub_resource type="ShaderMaterial" id="Mat_OldFilm"]
shader = ExtResource("12_oldfilm")
shader_parameter/strength = 0.0
shader_parameter/sim_fps = 18.0
shader_parameter/tint_color = {warm}
shader_parameter/tint_amount = 0.55
shader_parameter/grain_strength = 0.18
shader_parameter/flicker_strength = 0.20
shader_parameter/vignette_strength = 0.55
shader_parameter/scratch_strength = 0.10
shader_parameter/judder_strength = 0.0

[sub_resource type="ShaderMaterial" id="Mat_Liminal"]
shader = ExtResource("15_lim")
shader_parameter/strength = 0.0
shader_parameter/edge_ca = 0.012
shader_parameter/wobble_amp = 0.0018
shader_parameter/wobble_freq = 0.85
shader_parameter/tint_amount = 0.18
shader_parameter/tint_color = {lim_tint}

[sub_resource type="Environment" id="Env_Locale"]
background_mode = 1
background_color = {env_bg}
ambient_light_source = 2
ambient_light_color = {env_amb}
ambient_light_energy = {env_amb_e}
fog_enabled = true
fog_light_color = {env_fog}
fog_light_energy = {env_fog_e}
fog_density = {env_fog_d}
adjustment_enabled = true
adjustment_brightness = {env_bright}
adjustment_contrast = {env_cont}
adjustment_saturation = {env_sat}
glow_enabled = true
glow_intensity = {env_glow_i}
glow_bloom = {env_glow_b}
glow_blend_mode = 1
glow_hdr_threshold = 0.95
glow_hdr_scale = 2.4

[node name="{root_node}" type="Node3D"]

[node name="WorldEnvironment" type="WorldEnvironment" parent="."]
environment = SubResource("Env_Locale")

{lights_block}

[node name="Interior" parent="." instance=ExtResource("1_glb")]

[node name="PostProcess" type="CanvasLayer" parent="."]
layer = 50
script = ExtResource("5_mood")
mood_strata = Array[String]({mood_strata})
default_style_pack = ""

[node name="NeonQuad" type="ColorRect" parent="PostProcess"]
material = SubResource("Mat_Neon")
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
mouse_filter = 2

[node name="BB_Before_DirAsciiQuad" type="BackBufferCopy" parent="PostProcess"]
copy_mode = 2

[node name="DirAsciiQuad" type="ColorRect" parent="PostProcess"]
material = SubResource("Mat_DirAscii")
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
mouse_filter = 2

[node name="BB_Before_AsciiQuad" type="BackBufferCopy" parent="PostProcess"]
copy_mode = 2

[node name="AsciiQuad" type="ColorRect" parent="PostProcess"]
material = SubResource("Mat_Ascii")
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
mouse_filter = 2

[node name="BB_Before_StarscapeQuad" type="BackBufferCopy" parent="PostProcess"]
copy_mode = 2

[node name="StarscapeQuad" type="ColorRect" parent="PostProcess"]
material = SubResource("Mat_Starscape")
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
mouse_filter = 2

[node name="BB_Before_MotionQuad" type="BackBufferCopy" parent="PostProcess"]
copy_mode = 2

[node name="MotionQuad" type="ColorRect" parent="PostProcess"]
material = SubResource("Mat_Motion")
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
mouse_filter = 2

[node name="BB_Before_BlurQuad" type="BackBufferCopy" parent="PostProcess"]
copy_mode = 2

[node name="BlurQuad" type="ColorRect" parent="PostProcess"]
material = SubResource("Mat_Blur")
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
mouse_filter = 2

[node name="BB_Before_Quad" type="BackBufferCopy" parent="PostProcess"]
copy_mode = 2

[node name="Quad" type="ColorRect" parent="PostProcess"]
material = SubResource("Mat_Post")
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
mouse_filter = 2

[node name="BB_Before_OldFilmQuad" type="BackBufferCopy" parent="PostProcess"]
copy_mode = 2

[node name="OldFilmQuad" type="ColorRect" parent="PostProcess"]
material = SubResource("Mat_OldFilm")
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
mouse_filter = 2

[node name="BB_Before_LiminalQuad" type="BackBufferCopy" parent="PostProcess"]
copy_mode = 2

[node name="LiminalQuad" type="ColorRect" parent="PostProcess"]
material = SubResource("Mat_Liminal")
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
mouse_filter = 2

[node name="LiminalProximityController" type="Node3D" parent="."]
script = ExtResource("16_limc")
post_process_path = NodePath("../PostProcess")
location_json = ""

[node name="PDPRiffmaster" type="Node" parent="."]
script = ExtResource("13_riff")

[node name="HUD" type="CanvasLayer" parent="." groups=["ui"]]
layer = 100

[node name="DebugLabel" type="Label" parent="HUD"]
offset_left = 16.0
offset_top = 16.0
offset_right = 600.0
offset_bottom = 200.0
script = ExtResource("3_hud")

[node name="DebugMenu" type="VBoxContainer" parent="HUD"]
offset_left = 16.0
offset_top = 360.0
offset_right = 520.0
offset_bottom = 980.0
script = ExtResource("14_dbgm")
'''


def col(rgb):
    return "Color({:.2f}, {:.2f}, {:.2f}, {})".format(*rgb)


def write_locale_tscn(cfg):
    lights = []
    for (nm, t, xform, c, energy) in cfg["lights"]:
        s = (f'[node name="{nm}" type="{t}" parent="."]\n'
             f'transform = {xform}\n'
             f'light_color = {c}\n'
             f'light_energy = {energy}\n'
             f'shadow_enabled = false')
        if t == "OmniLight3D":
            s += "\nomni_range = 4.0"
        lights.append(s)
    sh = cfg["shader"]
    env = cfg["env"]
    content = TEMPLATE.format(
        uid=cfg["uid"],
        root_node=cfg["root_node"],
        glb=cfg["glb"],
        warm=col(sh["warm"]),
        shader_bg=col(sh["bg"]),
        neon_edge=col(sh["neon_edge"]),
        neon_lo=col(sh["neon_lo"]),
        neon_hi=col(sh["neon_hi"]),
        lim_tint=col(sh["lim_tint"]),
        env_bg=col(env["bg"]),
        env_amb=col(env["amb"]),
        env_amb_e=env["amb_e"],
        env_fog=col(env["fog"]),
        env_fog_e=env["fog_e"],
        env_fog_d=env["fog_d"],
        env_bright=env.get("bright", 1.0),
        env_cont=env.get("cont", 1.04),
        env_sat=env.get("sat", 0.94),
        env_glow_i=env.get("glow_i", 0.70),
        env_glow_b=env.get("glow_b", 0.12),
        lights_block="\n\n".join(lights),
        mood_strata=str(cfg["mood_strata"]),
    )
    with open(cfg["out_path"], "w") as f:
        f.write(content)
    return cfg["out_path"]
