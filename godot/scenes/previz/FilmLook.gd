class_name FilmLook
extends CanvasLayer
## Full-screen cinematic post over the 3D: film grain, vignette, chromatic
## aberration and anamorphic letterbox, plus a selectable colour GRADE. Sits on a
## low layer so the HUD/timeline stay crisp. cycle() steps: off → each grade → off.
## Builds on the env grade (AGX + desat + bloom) already in the environment.

const GRADES := ["1970s film", "high contrast", "black & white", "bleach bypass", "teal & orange", "film noir"]

const SHADER := """
shader_type canvas_item;
uniform sampler2D screen_tex : hint_screen_texture, filter_linear;
uniform float grain = 0.045;
uniform float vignette = 0.55;
uniform float aberration = 1.2;
uniform float bars = 0.07;
uniform float grade = 0.0;

float rand(vec2 co){ return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453); }

vec3 do_grade(vec3 c, int gd){
	float l = dot(c, vec3(0.299, 0.587, 0.114));
	if (gd == 1) {                              // high-contrast photography
		c = (c - 0.5) * 1.4 + 0.5;
		c = mix(vec3(l), c, 1.18);              // a touch more saturation
	} else if (gd == 2) {                       // black & white
		c = vec3((l - 0.5) * 1.25 + 0.5);
	} else if (gd == 3) {                        // bleach bypass
		vec3 hc = (c - 0.5) * 1.35 + 0.5;
		c = mix(vec3(l), hc, 0.35);             // mostly desaturated + contrasty
		c = mix(c, c * c * (3.0 - 2.0 * c), 0.35);   // S-curve crunch
	} else if (gd == 4) {                        // teal shadows / orange highlights
		vec3 sh = c * vec3(0.82, 1.0, 1.18);
		vec3 hi = c * vec3(1.18, 1.02, 0.78);
		c = mix(sh, hi, smoothstep(0.2, 0.8, l));
		c = (c - 0.5) * 1.12 + 0.5;
	} else if (gd == 5) {                        // film noir (crushed B&W)
		c = vec3(clamp((l - 0.46) * 1.9 + 0.46, 0.0, 1.0));
	}
	return clamp(c, 0.0, 1.0);
}

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
		col = do_grade(col, int(grade + 0.5));
		float g = rand(uv * vec2(1.0 + fract(TIME), 1.3 + fract(TIME * 0.7))) - 0.5;
		col += g * grain;
		float vig = smoothstep(0.9, 0.25, length(d));
		col *= mix(1.0, vig, vignette);
		COLOR = vec4(col, 1.0);
	}
}
"""

var enabled := false   # off by default so a shader/overlay issue can't blank the boot view
var grade := 0
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


## Step: off → 1970s → high contrast → B&W → bleach → teal/orange → noir → off.
## Returns the name of the active look (or "off") for the HUD.
func cycle() -> String:
	if not enabled:
		enabled = true
		grade = 0
	else:
		grade += 1
		if grade >= GRADES.size():
			enabled = false
			grade = 0
	_rect.visible = enabled
	if enabled:
		_rect.material.set_shader_parameter("grade", float(grade))
	return "off" if not enabled else GRADES[grade]


## Kept for callers that just want on/off (cycles into/out of the first grade).
func toggle() -> void:
	if enabled:
		enabled = false
	else:
		enabled = true
		grade = 0
		_rect.material.set_shader_parameter("grade", 0.0)
	_rect.visible = enabled
