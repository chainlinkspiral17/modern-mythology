extends Node3D
## Previz sandbox root. Builds the hangar venue, a stage rig, character
## stand-ins and a fly camera entirely in code so the scene runs with no
## imported assets. Phase 1 = blockout + moods + nav + screenshot.
##
## Controls:
##   W A S D / Q E ........ fly (hold Shift = faster)
##   Right mouse (hold) ... look around
##   1 / 2 / 3 ............ stage show: NoNo / One Model Nation / Zonk
##   Z / X / C ............ mood: dusk / night / disaster
##   P .................... save a frame to user://frames/
##   H .................... toggle the on-screen help

const CHARACTERS_PATH := "res://scenes/previz/data/characters.json"
const STAGE_X := 24.0   # stage at the +X open mouth; crowd gathers outside (further +X)
const STAGE_TO_BAND := { 1: "Nana Avatar", 2: "One Model Nation", 3: "Zonk" }
const STAGE_TO_MOOD := { 1: "dusk", 2: "dusk", 3: "night" }

var _cam: Camera3D
var _sun: DirectionalLight3D
var _env: Environment
var _sky_mat: ProceduralSkyMaterial
var _stage: Node3D
var _performers: Node3D
var _hud: Label
var _director: CameraDirector

var _stage_level := 1
var _mood := "dusk"
var _yaw := 0.0
var _pitch := 0.0
var _fly_speed := 12.0
var _chars: Array = []
var _pending_move := 0
var _director_active := false


func _ready() -> void:
	_load_characters()
	_build_environment()

	var hangar := Node3D.new()
	hangar.set_script(load("res://scenes/previz/Hangar.gd"))
	add_child(hangar)

	_stage = Node3D.new()
	_stage.set_script(load("res://scenes/previz/StageRig.gd"))
	_stage.position = Vector3(STAGE_X, 1.5, 0.0)
	add_child(_stage)
	_stage.build(_stage_level)

	_performers = Node3D.new()
	add_child(_performers)
	_spawn_crowd()
	_spawn_performers(STAGE_TO_BAND[_stage_level])

	_build_camera()
	_make_director()
	_build_hud()
	apply_mood(STAGE_TO_MOOD[_stage_level])


# ── data ──────────────────────────────────────────────────────────────────────
func _load_characters() -> void:
	if not FileAccess.file_exists(CHARACTERS_PATH):
		push_warning("Previz: characters.json not found")
		return
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(CHARACTERS_PATH))
	if data is Dictionary and data.has("characters"):
		_chars = data["characters"]


# ── environment + sun ──────────────────────────────────────────────────────────
func _build_environment() -> void:
	var we := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_SKY
	var sky := Sky.new()
	_sky_mat = ProceduralSkyMaterial.new()
	sky.sky_material = _sky_mat
	env.sky = sky
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.glow_enabled = true
	we.environment = env
	add_child(we)
	_env = env

	_sun = DirectionalLight3D.new()
	_sun.shadow_enabled = true
	add_child(_sun)


func apply_mood(id: String) -> void:
	_mood = id
	var m := Moods.get_mood(id)
	_sun.rotation_degrees = m["sun_rot"]
	_sun.light_color = m["sun_color"]
	_sun.light_energy = m["sun_energy"]
	_sky_mat.sky_top_color = m["sky_top"]
	_sky_mat.sky_horizon_color = m["sky_horizon"]
	_sky_mat.ground_horizon_color = m["sky_horizon"]
	_sky_mat.ground_bottom_color = m["ground"]
	_env.ambient_light_energy = m["ambient"]
	_env.fog_enabled = true
	_env.fog_light_color = m["fog_color"]
	_env.fog_density = m["fog_density"]
	_env.glow_enabled = m["glow"]
	_update_hud()


# ── characters (capsule stand-ins; swap to res:// .glb via "model") ─────────────
func _person(color: Color, pos: Vector3, model_path: String) -> Node3D:
	if model_path != "" and ResourceLoader.exists(model_path):
		var packed: Resource = load(model_path)
		if packed is PackedScene:
			var inst: Node3D = (packed as PackedScene).instantiate()
			inst.position = pos
			return inst
	var mi := MeshInstance3D.new()
	var cm := CapsuleMesh.new()
	cm.radius = 0.35
	cm.height = 1.8
	mi.mesh = cm
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mi.material_override = mat
	mi.position = pos + Vector3(0.0, 0.9, 0.0)
	return mi


func _spawn_performers(band: String) -> void:
	for c in _performers.get_children():
		if c.has_meta("performer"):
			c.queue_free()
	var roster: Array = []
	for c in _chars:
		if c.get("band", "") == band:
			roster.append(c)
	var n := roster.size()
	for i in n:
		var c: Dictionary = roster[i]
		var z := 0.0 if n == 1 else lerpf(-6.0, 6.0, float(i) / float(n - 1))
		var node := _person(Color.html(c.get("color", "888888")), Vector3(STAGE_X - 2.0, 1.5, z), c.get("model", ""))
		node.set_meta("performer", true)
		_performers.add_child(node)


func _spawn_crowd() -> void:
	var crowd: Array = []
	for c in _chars:
		if c.get("zone", "") == "crowd":
			crowd.append(c)
	# tile the audience area in front of the stage / out toward the bay
	var idx := 0
	for row in 8:
		for col in 9:
			var src: Dictionary = crowd[idx % maxi(crowd.size(), 1)] if crowd.size() > 0 else {"color": "6a6a72"}
			var x := 32.0 + row * 9.0
			var z := lerpf(-18.0, 18.0, float(col) / 8.0)
			_performers.add_child(_person(Color.html(src.get("color", "6a6a72")), Vector3(x, 0.0, z), ""))
			idx += 1


# ── camera + nav ────────────────────────────────────────────────────────────────
func _build_camera() -> void:
	_cam = Camera3D.new()
	_cam.fov = 42.0
	_cam.position = Vector3(70.0, 9.0, 0.0)
	add_child(_cam)
	_cam.look_at(Vector3(STAGE_X, 5.0, 0.0), Vector3.UP)
	_cam.current = true
	_yaw = _cam.rotation.y
	_pitch = _cam.rotation.x


func _make_director() -> void:
	_director = CameraDirector.new()
	add_child(_director)


func _focus_point() -> Vector3:
	var fwd := -_cam.global_transform.basis.z
	var d := maxf(8.0, _cam.global_position.distance_to(Vector3(STAGE_X, 4.0, 0.0)))
	return _cam.global_position + fwd * d


func _toggle_view() -> void:
	_director_active = not _director_active
	if _director_active and _director.count() > 0:
		_director.make_current()
	else:
		_director_active = false
		_cam.current = true
	_update_hud()


func _process(delta: float) -> void:
	if _cam == null:
		return
	var dir := Vector3.ZERO
	if Input.is_key_pressed(KEY_W): dir.z -= 1.0
	if Input.is_key_pressed(KEY_S): dir.z += 1.0
	if Input.is_key_pressed(KEY_A): dir.x -= 1.0
	if Input.is_key_pressed(KEY_D): dir.x += 1.0
	var v := _cam.global_transform.basis * dir
	if Input.is_key_pressed(KEY_Q): v.y -= 1.0
	if Input.is_key_pressed(KEY_E): v.y += 1.0
	if v.length() > 0.0:
		var spd := _fly_speed * (3.0 if Input.is_key_pressed(KEY_SHIFT) else 1.0)
		_cam.global_position += v.normalized() * spd * delta


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT):
		_yaw -= event.relative.x * 0.005
		_pitch = clampf(_pitch - event.relative.y * 0.005, -1.4, 1.4)
		_cam.rotation = Vector3(_pitch, _yaw, 0.0)
	elif event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_1: _set_stage(1)
			KEY_2: _set_stage(2)
			KEY_3: _set_stage(3)
			KEY_Z: apply_mood("dusk")
			KEY_X: apply_mood("night")
			KEY_C: apply_mood("disaster")
			KEY_P: _screenshot()
			KEY_H: _hud.visible = not _hud.visible
			KEY_M:
				_pending_move = (_pending_move + 1) % CameraDirector.MOVES.size()
				_update_hud()
			KEY_K:
				_director.add_camera("Cam %d" % (_director.count() + 1), _cam.global_position, _focus_point(), _cam.fov, CameraDirector.MOVES[_pending_move])
				_flash("added Cam %d — %s" % [_director.count(), CameraDirector.MOVES[_pending_move]])
			KEY_TAB:
				_toggle_view()
			KEY_SPACE:
				if _director.playing: _director.stop()
				else: _director.play()
			KEY_BRACKETLEFT:
				_director.scrub(-0.25)
			KEY_BRACKETRIGHT:
				_director.scrub(0.25)
			KEY_COMMA:
				_director.select(_director.active - 1)
				if _director_active: _director.make_current()
				_update_hud()
			KEY_PERIOD:
				_director.select(_director.active + 1)
				if _director_active: _director.make_current()
				_update_hud()
			KEY_BACKSLASH:
				_director.save_json("user://previz_cameras.json")
				_flash("saved cameras -> user://previz_cameras.json")


func _set_stage(level: int) -> void:
	_stage_level = level
	_stage.build(level)
	_spawn_performers(STAGE_TO_BAND[level])
	apply_mood(STAGE_TO_MOOD[level])


# ── frame export ──────────────────────────────────────────────────────────────
func _screenshot() -> void:
	var dir := "user://frames"
	if not DirAccess.dir_exists_absolute(dir):
		DirAccess.make_dir_recursive_absolute(dir)
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	var stamp := Time.get_datetime_string_from_system().replace(":", "-")
	var path := "%s/previz_%s.png" % [dir, stamp]
	img.save_png(path)
	_flash("saved %s" % path)


# ── HUD ───────────────────────────────────────────────────────────────────────
func _build_hud() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	_hud = Label.new()
	_hud.position = Vector2(14.0, 12.0)
	_hud.add_theme_font_size_override("font_size", 15)
	layer.add_child(_hud)
	_update_hud()


func _update_hud() -> void:
	if _hud == null:
		return
	var band: String = STAGE_TO_BAND.get(_stage_level, "?")
	var mood: Dictionary = Moods.get_mood(_mood)
	var cam_line := "cameras: none   [K] add from current view"
	if _director and _director.count() > 0:
		var info := _director.active_info()
		cam_line = "CAM %d/%d  %s%s   view: %s" % [
			_director.active + 1, _director.count(), info.get("move", "?"),
			(" [playing]" if _director.playing else ""),
			("director" if _director_active else "fly"),
		]
	_hud.text = "STAGE %d — %s\nMOOD — %s\n%s\nnext move [M]: %s\n\n[1/2/3] stage  [Z/X/C] mood  [WASD/QE] fly  [RMB] look\n[K] add cam  [M] move  [Tab] fly/cam  [Space] play  [ [ / ] ] scrub  [,/.] cam  [\\] save  [P] frame  [H] hide" % [
		_stage_level, band, mood.get("label", _mood), cam_line, CameraDirector.MOVES[_pending_move]
	]


func _flash(msg: String) -> void:
	if _hud:
		_hud.text = msg
