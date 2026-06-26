class_name FilmLook
extends CanvasLayer
## 1970s cinematic post — a full-screen shader over the 3D: animated film grain,
## vignette, slight chromatic aberration and anamorphic letterbox bars. Sits on a
## low layer so the HUD/timeline (higher layers) stay crisp. Toggle with toggle().
## Builds on the env grade (AGX + desat + bloom) already in the environment.

const SHADER := """
shader_type canvas_item;
uniform sampler2D screen_tex : hint_screen_texture, filter_linear;
uniform float grain = 0.045;
uniform float vignette = 0.55;
uniform float aberration = 1.2;
uniform float bars = 0.07;

float rand(vec2 co){ return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453); }

void fragment(){
	vec2 uv = SCREEN_UV;
	if (uv.y < bars || uv.y > 1.0 - bars) {
		COLOR = vec4(0.0, 0.0, 0.0, 1.0);
	} else {
		vec2 d = uv - vec2(0.5);
		vec2 ab = d * aberration * 0.004;
		vec3 col;
		col.r = texture(screen_tex, uv + ab).r;
		col.g = texture(screen_tex, uv).g;
		col.b = texture(screen_tex, uv - ab).b;
		float g = rand(uv * vec2(1.0 + fract(TIME), 1.3 + fract(TIME * 0.7))) - 0.5;
		col += g * grain;
		float vig = smoothstep(0.9, 0.25, length(d));
		col *= mix(1.0, vig, vignette);
		COLOR = vec4(col, 1.0);
	}
}
"""

var enabled := false   # off by default so a shader/overlay issue can't blank the boot view
var _rect: ColorRect


func _ready() -> void:
	layer = 1
	_rect = ColorRect.new()
	_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var sh := Shader.new()
	sh.code = SHADER
	var mat := ShaderMaterial.new()
	mat.shader = sh
	_rect.material = mat
	add_child(_rect)
	_rect.visible = enabled


func toggle() -> void:
	enabled = not enabled
	_rect.visible = enabled
