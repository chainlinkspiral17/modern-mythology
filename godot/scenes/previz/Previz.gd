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
# preload the newest helper scripts so we don't depend on the global class
# registry being refreshed (running before a re-import would otherwise fail)
const VOLUME_FOG := preload("res://scenes/previz/VolumeFog.gd")
const FILM_LOOK := preload("res://scenes/previz/FilmLook.gd")
const ASSET_BROWSER := preload("res://scenes/previz/AssetBrowser.gd")

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
var _shots: Array = []
var _shot_idx := -1
var _fullscreen := false
var _timeline: Timeline
var _overlay: RefOverlay
var _tlui: TimelineUI
var _tl_targets := ["camera", "rig"]
var _tl_sel := 0
var _refs: Array = []
var _ref_idx := -1
var _lighting: LightingRig
var _disaster: Disaster
var _film
var _browser
var _volfog
var _lowfog: SmokeSystem
var _volfog_amt := 0.65
var _lowfog_amt := 0.8
var _sky: Sky
var _spectrum                # AudioEffectSpectrumAnalyzerInstance
var _audio_level := 0.0


func _ready() -> void:
	_load_characters()
	_build_environment()
	_build_camera()   # build the camera EARLY so a later error can't blank the view

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

	_lighting = LightingRig.new()
	add_child(_lighting)
	_lighting.build(STAGE_X, _stage_level)

	_volfog = VOLUME_FOG.new()
	add_child(_volfog)
	_volfog.build(STAGE_X)
	_volfog.set_density(_volfog_amt)

	_lowfog = SmokeSystem.new()
	add_child(_lowfog)
	_lowfog.build(STAGE_X, true)
	_lowfog.set_density(_lowfog_amt)

	_disaster = Disaster.new()
	add_child(_disaster)
	_disaster.setup(STAGE_X)

	_make_director()
	_build_timeline()
	_setup_audio_reactor()
	_build_hud()
	apply_mood(STAGE_TO_MOOD[_stage_level])

	_film = FILM_LOOK.new()
	add_child(_film)
	_browser = ASSET_BROWSER.new()
	_browser.target = self
	_browser.spawn_pos = Vector3(STAGE_X - 2.0, 1.5, 0.0)
	add_child(_browser)

	if _cam:
		_cam.make_current()   # ensure the fly camera owns the viewport


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
	_sky = Sky.new()
	_sky_mat = ProceduralSkyMaterial.new()
	_sky.sky_material = _sky_mat
	env.sky = _sky
	# cinematic tonemap — AGX is neutral/filmic and avoids ACES' orange "crush"
	env.tonemap_mode = Environment.TONE_MAPPER_AGX
	env.tonemap_exposure = 1.1
	env.tonemap_white = 1.0
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_energy = 0.25
	# bloom
	env.glow_enabled = true
	env.glow_intensity = 0.5
	env.glow_bloom = 0.15
	# contact shadows / ambient occlusion (Forward+)
	env.ssao_enabled = true
	env.ssao_radius = 1.5
	env.ssao_intensity = 2.0
	# volumetric fog (Forward+) — much denser so haze + beams read clearly
	env.volumetric_fog_enabled = true
	env.volumetric_fog_density = 0.008
	env.volumetric_fog_albedo = Color(0.55, 0.55, 0.6)   # darker fog = won't bloom white, can run denser
	env.volumetric_fog_emission = Color(0.0, 0.0, 0.0)
	env.volumetric_fog_length = 140.0
	env.volumetric_fog_gi_inject = 0.0
	# stylized-realism / 1970s film grade: slight desaturation + gentle contrast
	env.adjustment_enabled = true
	env.adjustment_brightness = 1.0
	env.adjustment_contrast = 1.06
	env.adjustment_saturation = 0.88
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
	# real skybox image for this mood if one was dropped in, else the procedural sky
	var sky_img := _sky_image_for(id)
	if sky_img != "" and _sky:
		var pano := PanoramaSkyMaterial.new()
		pano.panorama = load(sky_img)
		_sky.sky_material = pano
	else:
		if _sky:
			_sky.sky_material = _sky_mat
		_sky_mat.sky_top_color = m["sky_top"]
		_sky_mat.sky_horizon_color = m["sky_horizon"]
		_sky_mat.ground_horizon_color = m["sky_horizon"]
		_sky_mat.ground_bottom_color = m["ground"]
	_env.ambient_light_energy = m["ambient"]
	_env.fog_enabled = true
	_env.fog_light_color = m["fog_color"]
	_env.fog_density = m["fog_density"]
	_env.volumetric_fog_density = m.get("vfog", 0.03)
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
		var z := 0.0 if n == 1 else lerpf(-8.0, 8.0, float(i) / float(n - 1))
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
			var z := lerpf(-24.0, 24.0, float(col) / 8.0)
			_performers.add_child(_person(Color.html(src.get("color", "6a6a72")), Vector3(x, 0.0, z), ""))
			idx += 1


# ── camera + nav ────────────────────────────────────────────────────────────────
func _build_camera() -> void:
	_cam = Camera3D.new()
	_cam.fov = 40.0
	_cam.position = Vector3(72.0, 7.0, 0.0)
	add_child(_cam)
	_cam.look_at(Vector3(STAGE_X, 6.0, 0.0), Vector3.UP)
	_cam.current = true
	_yaw = _cam.rotation.y
	_pitch = _cam.rotation.x


func _make_director() -> void:
	_director = CameraDirector.new()
	add_child(_director)


func _setup_audio_reactor() -> void:
	var bus := AudioServer.get_bus_index("Master")
	if bus < 0:
		return
	AudioServer.add_bus_effect(bus, AudioEffectSpectrumAnalyzer.new())
	_spectrum = AudioServer.get_bus_effect_instance(bus, AudioServer.get_bus_effect_count(bus) - 1)


func _build_timeline() -> void:
	_overlay = RefOverlay.new()
	add_child(_overlay)
	_timeline = Timeline.new()
	add_child(_timeline)
	_timeline.setup(_cam, _overlay)
	_timeline.register_target("rig", _stage)   # keyframe the whole lighting/stage rig (e.g. rotate)
	_timeline.set_music_from_paths([
		"res://assets/audio/song.ogg", "res://assets/audio/smoke_it.ogg", "user://song.ogg",
	])
	var layer := CanvasLayer.new()
	layer.layer = 9
	add_child(layer)
	_tlui = TimelineUI.new()
	_tlui.timeline = _timeline
	_tlui.sel_label = _tl_targets[_tl_sel]
	layer.add_child(_tlui)
	_scan_refs()


func _scan_refs() -> void:
	_refs.clear()
	for d in ["user://refs", "res://scenes/previz/refs"]:
		var da := DirAccess.open(d)
		if da == null:
			continue
		da.list_dir_begin()
		var fn := da.get_next()
		while fn != "":
			if not da.current_is_dir() and fn.get_extension().to_lower() in ["png", "jpg", "jpeg", "webp"]:
				_refs.append(d + "/" + fn)
			fn = da.get_next()


func _cycle_ref() -> void:
	if _refs.is_empty():
		_flash("no reference images (drop some in user://refs/)")
		return
	_ref_idx = (_ref_idx + 1) % _refs.size()
	_overlay.load_image(_refs[_ref_idx])
	_flash("ref: %s [%s]" % [_refs[_ref_idx].get_file(), _overlay.place_name()])


func _add_keyframe() -> void:
	var id: String = _tl_targets[_tl_sel]
	if id == "camera":
		_timeline.add_cam_key(_timeline.time, _cam.global_position, _focus_point(), _cam.fov)
	else:
		var node: Node3D = _timeline.targets.get(id)
		if node:
			_timeline.add_obj_key(id, _timeline.time, node.global_position, node.rotation_degrees, node.scale)
	_flash("keyframe @ %.1fs on '%s'" % [_timeline.time, id])


func _timeline_play() -> void:
	if _timeline.playing:
		_timeline.stop()
	else:
		_director_active = false
		_cam.current = true
		_timeline.play()
	_update_hud()


func _set_chrome(v: bool) -> void:
	if _hud:
		_hud.visible = v
	if _tlui:
		_tlui.visible = v


func _sky_image_for(id: String) -> String:
	for ext in ["hdr", "exr", "png", "jpg", "jpeg"]:
		var p := "res://assets/sky/%s.%s" % [id, ext]
		if ResourceLoader.exists(p):
			return p
	return ""


func _fog_adjust(d: float) -> void:
	if _env == null:
		return
	_env.volumetric_fog_density = clampf(_env.volumetric_fog_density + d, 0.0, 0.15)
	_flash("fog %.4f" % _env.volumetric_fog_density)


func _volfog_adjust(d: float) -> void:
	_volfog_amt = clampf(_volfog_amt + d, 0.0, 1.0)
	if _volfog:
		_volfog.set_density(_volfog_amt)
	_flash("volume smoke %d%%" % int(_volfog_amt * 100.0))


func _lowfog_adjust(d: float) -> void:
	_lowfog_amt = clampf(_lowfog_amt + d, 0.0, 1.0)
	if _lowfog:
		_lowfog.set_density(_lowfog_amt)
	_flash("stage fog %d%%" % int(_lowfog_amt * 100.0))


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


## Clean full-screen capture view: native-res fullscreen with the HUD hidden.
func _toggle_fullscreen() -> void:
	_fullscreen = not _fullscreen
	DisplayServer.window_set_mode(
		DisplayServer.WINDOW_MODE_FULLSCREEN if _fullscreen else DisplayServer.WINDOW_MODE_WINDOWED
	)
	_set_chrome(not _fullscreen)


func _process(delta: float) -> void:
	if _cam == null:
		return
	var lt: float = _timeline.time if (_timeline and _timeline.playing) else float(Time.get_ticks_msec()) / 1000.0
	var active: bool = _timeline != null and _timeline.music_playing()
	if _spectrum:
		var mag: float = _spectrum.get_magnitude_for_frequency_range(40.0, 280.0).length()
		_audio_level = lerpf(_audio_level, clampf(mag * 14.0, 0.0, 1.0), 0.35)
	if not active:
		_audio_level = lerpf(_audio_level, 0.0, 0.2)
	if _lighting:
		_lighting.update(lt, _audio_level, active)
	if _volfog:
		_volfog.update(lt)
	if _timeline and _timeline.playing and not _timeline.cam_keys.is_empty():
		return   # the timeline is driving the camera
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
			KEY_I:
				_import_storyboard()
			KEY_N:
				_goto_shot(_shot_idx + 1)
			KEY_B:
				_goto_shot(_shot_idx - 1)
			KEY_R:
				_batch_render()
			KEY_F:
				_toggle_fullscreen()
			KEY_T:
				_timeline_play()
			KEY_Y:
				_timeline.stop()
				_timeline.time = 0.0
				_timeline.apply(0.0)
				_update_hud()
			KEY_SEMICOLON:
				_timeline.seek(-0.5)
			KEY_APOSTROPHE:
				_timeline.seek(0.5)
			KEY_O:
				_tl_sel = (_tl_sel + 1) % _tl_targets.size()
				_tlui.sel_label = _tl_targets[_tl_sel]
				_update_hud()
			KEY_J:
				_add_keyframe()
			KEY_G:
				_overlay.cycle_place()
				_update_hud()
			KEY_L:
				_cycle_ref()
			KEY_U:
				if _overlay.current_path != "":
					_timeline.add_ref_cue(_timeline.time, _overlay.current_path, _overlay.place)
					_flash("ref cue @ %.1fs (%s)" % [_timeline.time, _overlay.place_name()])
				else:
					_flash("load a reference image first ([L])")
			KEY_SLASH:
				_timeline.save_json("user://timeline.json")
				_flash("saved timeline -> user://timeline.json")
			KEY_4:
				_lighting.cycle_look()
				_flash("LX look: %s" % _lighting.look_name())
			KEY_5:
				_lighting.strobe = not _lighting.strobe
				_flash("strobe %s" % ("ON" if _lighting.strobe else "off"))
			KEY_6:
				_lighting.blackout = not _lighting.blackout
				_flash("blackout %s" % ("ON" if _lighting.blackout else "off"))
			KEY_7:
				_fog_adjust(-0.003)
			KEY_8:
				_fog_adjust(0.003)
			KEY_F1:
				_volfog_adjust(-0.05)
			KEY_F2:
				_volfog_adjust(0.05)
			KEY_F3:
				_lowfog_adjust(-0.05)
			KEY_F4:
				_lowfog_adjust(0.05)
			KEY_F5:
				_lighting.cycle_formation()
				_flash("formation: %s" % _lighting.formation_name())
			KEY_F6:
				_lighting.cycle_speed()
				_flash("mover speed: %s" % _lighting.speed_name())
			KEY_F7:
				_film.toggle()
				_flash("film look %s" % ("on" if _film.enabled else "off"))
			KEY_F8:
				_browser.toggle()
			KEY_MINUS:
				_lighting.set_master(_lighting.master - 0.1)
				_flash("dimmer %d%%" % int(_lighting.master * 100.0))
			KEY_EQUAL:
				_lighting.set_master(_lighting.master + 0.1)
				_flash("dimmer %d%%" % int(_lighting.master * 100.0))
			KEY_9:
				if not _performers.get_children().is_empty():
					_lighting.set_follow_target(_performers.get_child(0).global_position)
					_flash("follow spot -> performer")
			KEY_V:
				_disaster.trigger()
				apply_mood("disaster")
				_flash("HELICOPTER — debris incoming")
			KEY_0:
				_disaster.reset()
				_flash("disaster reset")


func _build_stage(level: int) -> void:
	_stage_level = level
	_stage.build(level)
	_spawn_performers(STAGE_TO_BAND[level])
	if _lighting:
		_lighting.build(STAGE_X, level)
		_lighting.use_look(["key + rim", "colour sweep", "beam fan"][clampi(level - 1, 0, 2)])


func _set_stage(level: int) -> void:
	_build_stage(level)
	apply_mood(STAGE_TO_MOOD[level])


# ── storyboard import → one camera/stage/mood per shot ──────────────────────
func _import_storyboard() -> void:
	var paths := ["user://storyboard.json", "res://scenes/previz/data/storyboard.json"]
	var doc := {}
	for p in paths:
		if FileAccess.file_exists(p):
			doc = StoryboardIO.load_doc(p)
			if not doc.is_empty():
				break
	if doc.is_empty():
		_flash("no storyboard.json (drop the tool's JSON export in user:// or scenes/previz/data/)")
		return
	_shots = StoryboardIO.map_shots(doc, STAGE_X)
	_director.clear()
	for sh in _shots:
		var fr: Dictionary = sh["framing"]
		_director.add_camera(sh["title"], fr["pos"], fr["target"], fr["fov"], sh["move"], sh["duration"])
	_shot_idx = 0
	_goto_shot(0)
	_flash("imported %d shots — [N]/[B] step, [R] render all" % _shots.size())


func _goto_shot(i: int) -> void:
	if _shots.is_empty():
		return
	_shot_idx = clampi(i, 0, _shots.size() - 1)
	var sh: Dictionary = _shots[_shot_idx]
	_build_stage(sh["level"])
	apply_mood(sh["mood"])
	_director.select(_shot_idx)
	_director_active = true
	_director.make_current()
	_update_hud()


func _batch_render() -> void:
	if _shots.is_empty():
		_flash("import a storyboard first ([I])")
		return
	var dir := "user://frames"
	if not DirAccess.dir_exists_absolute(dir):
		DirAccess.make_dir_recursive_absolute(dir)
	_set_chrome(false)   # clean frames
	var states: Array = []
	for i in _shots.size():
		var sh: Dictionary = _shots[i]
		_build_stage(sh["level"])
		apply_mood(sh["mood"])
		_director.select(i)
		_director.make_current()
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		img.save_png("%s/shot_%02d.png" % [dir, i + 1])
		var s := _director.sample(_director.cams[i], 0.0)
		var p: Vector3 = s["pos"]
		var t: Vector3 = s["target"]
		states.append({ "pos": [p.x, p.y, p.z], "target": [t.x, t.y, t.z], "fov": s["fov"], "frame": "shot_%02d.png" % (i + 1) })
	StoryboardIO.export_previz(_shots, states, "user://storyboard_previz.json")
	_set_chrome(not _fullscreen)
	_flash("rendered %d frames + storyboard_previz.json" % _shots.size())


# ── frame export ──────────────────────────────────────────────────────────────
func _screenshot() -> void:
	var dir := "user://frames"
	if not DirAccess.dir_exists_absolute(dir):
		DirAccess.make_dir_recursive_absolute(dir)
	_set_chrome(false)   # keep HUD + timeline strip out of the capture
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	var stamp := Time.get_datetime_string_from_system().replace(":", "-")
	var path := "%s/previz_%s.png" % [dir, stamp]
	img.save_png(path)
	_set_chrome(not _fullscreen)
	_flash("saved %s" % path)


# ── HUD ───────────────────────────────────────────────────────────────────────
func _build_hud() -> void:
	var layer := CanvasLayer.new()
	layer.layer = 20   # above the film-look post (layer 1) so the HUD stays crisp
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
	var shot_line := ""
	if not _shots.is_empty():
		var sh: Dictionary = _shots[clampi(_shot_idx, 0, _shots.size() - 1)]
		shot_line = "\nSHOT %d/%d — %s  (%s · %s)" % [_shot_idx + 1, _shots.size(), sh["title"], sh["shot_type"], sh["move"]]
	var tl_line := ""
	if _timeline:
		tl_line = "\nTIMELINE  t %.1f/%.1f  %s  target[O]: %s  ref[G]: %s%s" % [
			_timeline.time, _timeline.duration, ("PLAY" if _timeline.playing else "STOP"),
			_tl_targets[_tl_sel], (_overlay.place_name() if _overlay else "-"),
			("  (music)" if _timeline.has_music() else ""),
		]
	var lx_line := ""
	if _lighting:
		lx_line = "\nLX  look[4]:%s  form[F5]:%s@%s  strobe[5]:%s  blackout[6]:%s  dim[-/=]:%d%%\nFX  fog[7/8]:%.3f  volsmoke[F1/F2]:%d%%  stagefog[F3/F4]:%d%%  follow[9]" % [
			_lighting.look_name(), _lighting.formation_name(), _lighting.speed_name(),
			("on" if _lighting.strobe else "-"), ("on" if _lighting.blackout else "-"),
			int(_lighting.master * 100.0),
			(_env.volumetric_fog_density if _env else 0.0), int(_volfog_amt * 100.0), int(_lowfog_amt * 100.0),
		]
	_hud.text = "STAGE %d — %s\nMOOD — %s\n%s%s%s%s\nnext move [M]: %s\n\n[1/2/3] stage  [Z/X/C] mood  [WASD/QE] fly  [RMB] look\n[K] add cam  [M] move  [Tab] fly/cam  [Space] play  [ [ / ] ] scrub  [,/.] cam  [\\] save\n[I] import storyboard  [N/B] step  [R] render all  [F7] film  [F8] assets  [F] fullscreen  [P] frame  [H] hide\nTIMELINE: [T] play  [Y] rewind  [;/'] scrub  [O] target  [J] keyframe  [G] ref place  [L] ref img  [U] ref cue  [/] save\nLX: [4] look  [5] strobe  [6] blackout  [7/8] fog  [9] follow->performer   FX: [V] helicopter+debris  [0] reset" % [
		_stage_level, band, mood.get("label", _mood), cam_line, shot_line, tl_line, lx_line, CameraDirector.MOVES[_pending_move]
	]


func _flash(msg: String) -> void:
	if _hud:
		_hud.text = msg
