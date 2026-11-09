extends Node
## ART CLARITY (2026-11-09). The user: "art is very murky in the current
## scene renderer. Maybe find a way to lessen its effect on imagery."
##
## The generated pictures (HeroArt) are quads in the room, and every pass
## after the render — the locale's PostProcess, the painted watercolour
## pass, the trip — treated them as any wall: washed into 4 px regions,
## inked, hue-drifted. Nothing knew where the pictures were on screen.
##
## This node, inside Background3D's SubViewport, keeps a small second
## camera in step with whichever camera is current. It sees only the
## pictures' white twins (HeroArt.ART_LAYER) on black: the ART MASK. Its
## texture and two strengths are global shader uniforms:
##   art_mask   the mask (white where a picture is on screen)
##   art_keep   how far the passes step back over a picture (0 = not at all)
##   art_focus  0..1, the director's emphasis: the picture fully clear,
##              the room around it softened and darkened (a rack focus)
## The main cameras drop the twins' layer from their cull mask, so the
## twins are never drawn in the picture itself.

const HeroArtScript := preload("res://scripts/vn/HeroArt.gd")
const MASK_DIV: float = 4.0        # the mask renders at a quarter of the view
const KEEP: float = 0.78           # the pictures keep most of their own pixels
const FOCUS_EASE: float = 2.2      # per second, toward the target
const AMBIENT_FOCUS: float = 0.35  # a picture prominent in the frame
const AMBIENT_MIN_H: float = 0.08  # of the frame's height, to count

## The director's request (VnDirector): 1 while it holds on a picture.
static var focus_target: float = 0.0
## How far the passes step back over a picture (KEEP; TripPaintTest's
## --art-keep sets it for an A/B render).
static var keep_level: float = KEEP

var _vp: SubViewport = null
var _cam: Camera3D = null
var _main_vp: SubViewport = null
var _focus: float = 0.0


func setup(main_vp: SubViewport) -> void:
	_main_vp = main_vp
	_vp = SubViewport.new()
	_vp.name = "ArtMaskViewport"
	_vp.transparent_bg = false
	_vp.msaa_3d = Viewport.MSAA_DISABLED
	_vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	_vp.size = Vector2i(320, 180)
	add_child(_vp)
	_cam = Camera3D.new()
	_cam.name = "ArtMaskCamera"
	_cam.cull_mask = HeroArtScript.ART_LAYER
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0, 0, 0, 1)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0, 0, 0, 1)
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	env.glow_enabled = false
	env.fog_enabled = false
	env.volumetric_fog_enabled = false
	_cam.environment = env
	_vp.add_child(_cam)
	_cam.current = true
	RenderingServer.global_shader_parameter_set("art_mask", _vp.get_texture())
	_set_keep(0.0)
	RenderingServer.global_shader_parameter_set("art_focus", 0.0)


func _process(delta: float) -> void:
	if _main_vp == null or _vp == null:
		return
	var want: Vector2i = Vector2i(maxi(16, int(_main_vp.size.x / MASK_DIV)), maxi(16, int(_main_vp.size.y / MASK_DIV)))
	if _vp.size != want:
		_vp.size = want
	var main_cam: Camera3D = _main_vp.get_camera_3d()
	var pictures: bool = not HeroArtScript.placed_art.is_empty()
	if main_cam == null or main_cam == _cam or not pictures:
		_set_keep(0.0)
		_ease_focus(0.0, delta)
		return
	# the twins are the mask's alone
	if main_cam.cull_mask & HeroArtScript.ART_LAYER:
		main_cam.cull_mask = main_cam.cull_mask & ~HeroArtScript.ART_LAYER
	_cam.global_transform = main_cam.global_transform
	_cam.projection = main_cam.projection
	_cam.fov = main_cam.fov
	_cam.size = main_cam.size
	_cam.near = main_cam.near
	_cam.far = main_cam.far
	_cam.keep_aspect = main_cam.keep_aspect
	_cam.h_offset = main_cam.h_offset
	_cam.v_offset = main_cam.v_offset
	_set_keep(keep_level)
	# (2026-11-09) the director's art shots ask for full focus; any frame —
	# a closeup, a wide — where a picture faces the camera near the centre
	# at a readable size gets a gentle one of its own ("the director is not
	# highlighting the art enough in the scenes in close ups")
	var ambient: float = AMBIENT_FOCUS if _art_centered(main_cam) else 0.0
	_ease_focus(maxf(focus_target, ambient), delta)


## A picture faces the camera, its centre in the frame's middle and its
## height at least AMBIENT_MIN_H of the frame.
func _art_centered(cam: Camera3D) -> bool:
	var vsz: Vector2 = Vector2(_main_vp.size)
	if vsz.y <= 0.0:
		return false
	for pv: Variant in HeroArtScript.placements():
		var p: Dictionary = pv
		var quad: Node3D = p.get("quad") as Node3D
		if quad == null:
			continue
		var c: Vector3 = quad.global_position
		if cam.is_position_behind(c):
			continue
		var to_cam: Vector3 = cam.global_position - c
		if quad.global_transform.basis.z.dot(to_cam) <= 0.0:
			continue
		var sp: Vector2 = cam.unproject_position(c) / vsz
		if sp.x < 0.2 or sp.x > 0.8 or sp.y < 0.12 or sp.y > 0.8:
			continue
		var sz: Vector2 = p.get("size", Vector2.ONE)
		var top: Vector2 = cam.unproject_position(c + quad.global_transform.basis.y.normalized() * sz.y * 0.5) / vsz
		var bot: Vector2 = cam.unproject_position(c - quad.global_transform.basis.y.normalized() * sz.y * 0.5) / vsz
		if absf(top.y - bot.y) >= AMBIENT_MIN_H:
			return true
	return false


func _ease_focus(target: float, delta: float) -> void:
	var f: float = move_toward(_focus, clampf(target, 0.0, 1.0), FOCUS_EASE * delta)
	if not is_equal_approx(f, _focus):
		_focus = f
		RenderingServer.global_shader_parameter_set("art_focus", _focus)


var _keep_now: float = -1.0

func _set_keep(v: float) -> void:
	if is_equal_approx(v, _keep_now):
		return
	_keep_now = v
	RenderingServer.global_shader_parameter_set("art_keep", v)


func _exit_tree() -> void:
	# the uniforms are global: off the VN they must read nothing
	RenderingServer.global_shader_parameter_set("art_keep", 0.0)
	RenderingServer.global_shader_parameter_set("art_focus", 0.0)
	focus_target = 0.0
