extends Node3D
## Previz sandbox root. Builds the hangar venue, a stage rig, character
## stand-ins and a fly camera entirely in code so the scene runs with no
## imported assets. Phase 1 = blockout + moods + nav + screenshot.
##
## Controls (press ` in-engine for the full grouped cheat-sheet):
##   W A S D / Q E ........ fly (hold Shift = faster)
##   Right mouse (hold) ... look around
##   1 / 2 / 3 ............ stage show: NoNo / One Model Nation / Zonk
##   Z / X / C ............ mood: dusk / night / disaster
##   P .................... save a frame to user://frames/
##   ` (backtick) ......... toggle the on-screen controls cheat-sheet
##   H .................... hide ALL UI (clean render); press again to restore
##   F .................... fullscreen (clean render behind it)

const CHARACTERS_PATH := "res://scenes/previz/data/characters.json"
const STAGE_X := 24.0   # stage at the +X open mouth; crowd gathers outside (further +X)
# ── hand-tunable placement (edit these in the script editor, then re-run) ──
const RIG_LIFT := 5.0        # raise the whole lighting rig up toward the rafters
const STAGE_DECK_Y := 1.5    # top of the performance stage flat; performers stand here
const STAGE_FLAT_X := 30.0   # stage centre X — slide to sit on the hangar's stage
const STAGE_FLAT_Z := 0.0    # stage centre Z — slide to line up under the gray platform
const STAGE_FLAT_SIZE := Vector3(12.0, 1.0, 22.0)  # depth(X) × height × width(Z)
const BACKDROP_H := 11.0      # dark backdrop panel height (floor → ~halfway to rafters)
const PERFORMER_TEST_LIFT := 0.0   # 0 = feet on the deck (was a hover test)
# Angled masking flats around the band (wings/returns) — [dx, dz, width, height,
# yaw°]; dx is relative to the stage centre (negative = upstage, behind the band).
const STAGE_FLATS := [
	[-4.0, -6.5, 12.0, 9.0, -35.0],    # left wing (pulled toward centre, angle swapped)
	[-4.0, 6.5, 12.0, 9.0, 35.0],      # right wing
	[-9.0, -3.5, 9.0, 10.0, -60.0],    # left return
	[-9.0, 3.5, 9.0, 10.0, 60.0],      # right return
]
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
var _hud: Label                 # live status read-out (top-left)
var _hud_panel: PanelContainer
var _help: Label                # keymap cheat-sheet (toggle with `)
var _help_panel: PanelContainer
var _ui_on := true              # master UI visibility (H = clean render)
var _help_shown := false
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
var _tl_targets := ["camera", "rig", "lighting"]
var _tl_sel := 0
var _refs: Array = []
var _ref_idx := -1
var _lighting: LightingRig
var _disaster: Disaster
var _film
var _browser
var _volfog
var _lowfog: SmokeSystem
var _volfog_amt := 0.5   # mid of the (now fully usable) range — natural at boot
var _lowfog_amt := 0.5
var _sky: Sky
var _spectrum                # AudioEffectSpectrumAnalyzerInstance
var _audio_level := 0.0


func _ready() -> void:
	_audit_models()
	_load_characters()
	_build_environment()
	_build_camera()   # build the camera EARLY so a later error can't blank the view

	var hangar := Node3D.new()
	hangar.set_script(load("res://scenes/previz/Hangar.gd"))
	add_child(hangar)

	_stage = Node3D.new()
	_stage.set_script(load("res://scenes/previz/StageRig.gd"))
	_stage.position = Vector3(STAGE_FLAT_X, STAGE_DECK_Y, STAGE_FLAT_Z)
	add_child(_stage)
	_stage.build(_stage_level)

	_build_stage_flat()
	_build_truss()
	_performers = Node3D.new()
	add_child(_performers)
	_spawn_crowd()
	_spawn_performers(STAGE_TO_BAND[_stage_level])

	_lighting = LightingRig.new()
	_lighting.position.y = RIG_LIFT   # raise the whole rig up into the rafters
	add_child(_lighting)
	_lighting.build(STAGE_FLAT_X, _stage_level)   # aim at the actual stage, not the old STAGE_X

	_volfog = VOLUME_FOG.new()
	add_child(_volfog)
	_volfog.build(STAGE_FLAT_X)   # anchor fog/smoke to the actual stage, not the old STAGE_X
	_volfog.set_density(_volfog_amt)

	_lowfog = SmokeSystem.new()
	add_child(_lowfog)
	_lowfog.build(STAGE_FLAT_X, true)
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
## Print what's in assets/models and whether Godot has imported each file, so a
## "not seeing assets" problem shows its cause in the console.
func _audit_models() -> void:
	var dir := DirAccess.open("res://assets/models")
	if dir == null:
		print("[previz] assets/models folder not found")
		return
	var n := 0
	dir.list_dir_begin()
	var fn := dir.get_next()
	while fn != "":
		if not dir.current_is_dir() and fn.get_extension().to_lower() in ["glb", "gltf"]:
			n += 1
			var p := "res://assets/models/" + fn
			print("[previz] model '%s' — imported:%s" % [fn, ResourceLoader.exists(p)])
		fn = dir.get_next()
	if n == 0:
		print("[previz] assets/models has no .glb/.gltf files")


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
	# bake a proper radiance CUBEMAP from whatever sky material is active (used for
	# the skybox itself + image-based reflections/ambient on the models & rig)
	_sky.radiance_size = Sky.RADIANCE_SIZE_256
	_sky.process_mode = Sky.PROCESS_MODE_QUALITY
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
	env.volumetric_fog_density = 0.004   # light ambient haze; beams scatter their own shafts
	env.volumetric_fog_albedo = Color(0.78, 0.78, 0.82)   # brighter so beam shafts read solid
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
		_sky.sky_material = _make_sky_material(sky_img)
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
const CHAR_YAW_DEG := 90.0   # face the audience (+X); was -90 (back turned)

func _person(color: Color, pos: Vector3, model_path: String, model_scale := 1.0) -> Node3D:
	if model_path != "":
		if ResourceLoader.exists(model_path):
			var packed: Resource = load(model_path)
			if packed is PackedScene:
				var inst: Node3D = (packed as PackedScene).instantiate()
				inst.position = pos
				if model_scale != 1.0:
					inst.scale = Vector3.ONE * model_scale
				inst.rotation_degrees = Vector3(0.0, CHAR_YAW_DEG, 0.0)
				inst.set_meta("is_model", true)   # feet get aligned to the surface after add_child
				print("[previz] CHARACTER LOADED '%s' @ %s scale %.2f" % [model_path, pos, model_scale])
				return inst
			else:
				print("[previz] character '%s' is not a PackedScene" % model_path)
		else:
			print("[previz] character model NOT imported: '%s' (run previz-run.sh to import) — using capsule" % model_path)
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


## Lighting truss: four towers rising from the stage deck to a top frame at the
## rig height, with cross-bracing — so the lights read as hung from real rig.
func _build_truss() -> void:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.1, 0.1, 0.12)
	mat.metallic = 0.7
	mat.roughness = 0.4
	var top := RIG_LIFT + 8.5                       # the fixture zone
	var hw := STAGE_FLAT_SIZE.z * 0.5 + 1.0         # half the truss width (Z)
	var xf := STAGE_FLAT_X + STAGE_FLAT_SIZE.x * 0.5 - 0.5   # downstage line
	var xb := STAGE_FLAT_X - STAGE_FLAT_SIZE.x * 0.5 + 0.5   # upstage line
	# four corner towers (deck → top), each with an X cross-brace
	for xx in [xf, xb]:
		for zz in [-hw, hw]:
			var z := STAGE_FLAT_Z + zz
			_beam(Vector3(0.4, top - STAGE_DECK_Y, 0.4), Vector3(xx, (top + STAGE_DECK_Y) * 0.5, z), mat)
			_brace(Vector3(xx, STAGE_DECK_Y, z), Vector3(xx, top, z), 0.18, mat)
	# top frame: downstage + upstage spans (along Z), two side spans (along X)
	_beam(Vector3(0.4, 0.4, hw * 2.0), Vector3(xf, top, STAGE_FLAT_Z), mat)
	_beam(Vector3(0.4, 0.4, hw * 2.0), Vector3(xb, top, STAGE_FLAT_Z), mat)
	_beam(Vector3(xf - xb, 0.4, 0.4), Vector3((xf + xb) * 0.5, top, STAGE_FLAT_Z - hw), mat)
	_beam(Vector3(xf - xb, 0.4, 0.4), Vector3((xf + xb) * 0.5, top, STAGE_FLAT_Z + hw), mat)
	# a centre span + a couple of cross-ties so the lights have a grid to hang on
	_beam(Vector3(xf - xb, 0.35, 0.35), Vector3((xf + xb) * 0.5, top, STAGE_FLAT_Z), mat)
	for zz in [-hw * 0.5, hw * 0.5]:
		_beam(Vector3(xf - xb, 0.3, 0.3), Vector3((xf + xb) * 0.5, top, STAGE_FLAT_Z + zz), mat)


func _beam(size: Vector3, pos: Vector3, mat: StandardMaterial3D) -> void:
	var mi := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = size
	mi.mesh = bm
	mi.material_override = mat
	mi.position = pos
	add_child(mi)


## A thin diagonal cross-brace ("X") between two points (truss detail).
func _brace(a: Vector3, b: Vector3, thick: float, mat: StandardMaterial3D) -> void:
	var mid := (a + b) * 0.5
	var dir := b - a
	var len := dir.length()
	if len < 0.01:
		return
	for s in [1.0, -1.0]:
		var mi := MeshInstance3D.new()
		var bm := BoxMesh.new()
		bm.size = Vector3(thick, len, thick)
		mi.mesh = bm
		mi.material_override = mat
		mi.position = mid
		mi.rotation = Vector3(0.0, 0.0, deg_to_rad(24.0) * s)
		add_child(mi)


## A clean raised performance flat in front of the venue clutter, plus a dark
## backdrop panel behind the band (hides the junk, gives the lights something to
## read against). Both heights are the tunable consts above.
func _build_stage_flat() -> void:
	var deck := MeshInstance3D.new()
	var db := BoxMesh.new()
	db.size = Vector3(STAGE_FLAT_SIZE.x, STAGE_DECK_Y, STAGE_FLAT_SIZE.z)
	deck.mesh = db
	var dm := StandardMaterial3D.new()
	dm.albedo_color = Color(0.07, 0.07, 0.08)
	dm.roughness = 0.7
	deck.material_override = dm
	deck.position = Vector3(STAGE_FLAT_X, STAGE_DECK_Y * 0.5, STAGE_FLAT_Z)   # top at STAGE_DECK_Y, base on the floor
	add_child(deck)
	# dark backdrop, upstage of the band, from the floor up to ~halfway to the rafters
	var back := MeshInstance3D.new()
	var bb := BoxMesh.new()
	bb.size = Vector3(0.4, BACKDROP_H, STAGE_FLAT_SIZE.z + 4.0)
	back.mesh = bb
	var bm := StandardMaterial3D.new()
	bm.albedo_color = Color(0.025, 0.025, 0.03)
	bm.roughness = 0.95
	back.material_override = bm
	back.position = Vector3(STAGE_FLAT_X - STAGE_FLAT_SIZE.x * 0.5 - 0.3, BACKDROP_H * 0.5, STAGE_FLAT_Z)
	add_child(back)
	# angled masking flats (wings/returns) to obscure the rest of the clutter
	for f in STAGE_FLATS:
		_flat(Vector3(STAGE_FLAT_X + f[0], 0.0, STAGE_FLAT_Z + f[1]), Vector2(f[2], f[3]), f[4])


## One angled dark flat standing on the floor (width × height, yawed about Y).
func _flat(pos_floor: Vector3, wh: Vector2, yaw_deg: float) -> void:
	var mi := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = Vector3(0.3, wh.y, wh.x)   # thin in local X; height; width along local Z
	mi.mesh = bm
	var m := StandardMaterial3D.new()
	m.albedo_color = Color(0.035, 0.035, 0.042)
	m.roughness = 0.95
	mi.material_override = m
	mi.position = pos_floor + Vector3(0.0, wh.y * 0.5, 0.0)
	mi.rotation_degrees = Vector3(0.0, yaw_deg, 0.0)
	add_child(mi)


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
		var z := STAGE_FLAT_Z + (0.0 if n == 1 else lerpf(-8.0, 8.0, float(i) / float(n - 1)))
		# stand at the DOWNSTAGE edge of the flat, right in front of the audience
		var px := STAGE_FLAT_X + STAGE_FLAT_SIZE.x * 0.5 - 0.8
		var node := _person(Color.html(c.get("color", "888888")), Vector3(px, STAGE_DECK_Y, z), c.get("model", ""), float(c.get("scale", 1.0)))
		node.set_meta("performer", true)
		_performers.add_child(node)
		if node.has_meta("is_model"):
			# TEST: hover her a few metres above the deck so we can confirm she's
			# there (set PERFORMER_TEST_LIFT back to 0 once placement is verified).
			_place_model(node, STAGE_DECK_Y + PERFORMER_TEST_LIFT)


## World-space combined AABB of all meshes under a node (zero-size if none).
func _world_aabb(node: Node3D) -> AABB:
	var out := AABB()
	var first := true
	for mi in node.find_children("*", "MeshInstance3D", true, false):
		var b: AABB = (mi as MeshInstance3D).global_transform * (mi as MeshInstance3D).get_aabb()
		if first:
			out = b
			first = false
		else:
			out = out.merge(b)
	return out


## Auto-scale a character to ~human height if its native size is wildly off, then
## stand its feet on surface_y. Prints what it measured (so "no character" is
## diagnosable: tiny/huge size, or zero-size = no meshes found).
func _place_model(node: Node3D, surface_y: float) -> void:
	var a := _world_aabb(node)
	if a.size == Vector3.ZERO:
		print("[previz] PLACE: '%s' has NO MeshInstance3D meshes (can't see it)" % node.name)
		return
	var h := a.size.y
	if h > 0.001 and (h < 0.8 or h > 3.0):     # not a sensible human height → rescale
		node.scale *= (1.8 / h)
		a = _world_aabb(node)
	node.global_position.y += surface_y - a.position.y   # feet on the surface
	print("[previz] PLACE '%s': size=%s feet@%.2f pos=%s" % [node.name, a.size, surface_y, node.global_position])


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
			var x := STAGE_FLAT_X + 8.0 + row * 9.0   # crowd starts just in front of the stage
			var z := STAGE_FLAT_Z + lerpf(-24.0, 24.0, float(col) / 8.0)
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
	_timeline.set_light_sink(_apply_light_cue) # keyframe the LX rig state (look/fog/etc.)
	# any track dropped in assets/audio/previz/ (or user://) becomes the master
	# clock; the rig reacts to it live and light cues override on top.
	var music := _scan_audio()
	music.append_array(["res://assets/audio/previz/song.ogg", "user://song.ogg"])
	_timeline.set_music_from_paths(music)
	var layer := CanvasLayer.new()
	layer.layer = 9
	add_child(layer)
	_tlui = TimelineUI.new()
	_tlui.timeline = _timeline
	_tlui.sel_label = _tl_targets[_tl_sel]
	layer.add_child(_tlui)
	_scan_refs()
	# restore a saved timeline if there is one; otherwise seed the set-change cues
	if not _timeline.load_json("user://timeline.json"):
		_seed_default_cues()


## Program the three set changes as light cues at the storyboard timings so the
## show plays itself when a track is loaded (until the user saves their own).
func _seed_default_cues() -> void:
	_timeline.add_light_cue(0.0, {
		"stage": 1, "look": "garage rock", "formation": "wave", "speed": 1,
		"gobo": "open", "gel": "open", "mix": false, "master": 1.0,
	})
	_timeline.add_light_cue(50.0, {
		"stage": 2, "look": "kraut shafts", "formation": "cross", "speed": 1,
		"gobo": "stripes", "gel": "deep blue", "mix": false, "master": 1.0,
	})
	_timeline.add_light_cue(135.0, {
		"stage": 3, "look": "anthem rwb", "formation": "fan", "speed": 1,
		"gobo": "open", "gel": "open", "mix": true, "master": 1.0,
	})


## Show tracks to drive the music-reactive rig: anything in assets/audio/previz/
## or user://. Sorted so a numbered prefix (01_, 02_) sets the order.
func _scan_audio() -> Array:
	var found: Array = []
	for d in ["res://assets/audio/previz", "user://"]:
		var da := DirAccess.open(d)
		if da == null:
			continue
		da.list_dir_begin()
		var fn := da.get_next()
		while fn != "":
			if not da.current_is_dir() and fn.get_extension().to_lower() in ["ogg", "wav", "mp3"]:
				found.append(d.path_join(fn))
			fn = da.get_next()
	found.sort()
	return found


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
	elif id == "lighting":
		_timeline.add_light_cue(_timeline.time, _capture_light_state())
		_flash("LX cue @ %.1fs (%s)" % [_timeline.time, _lighting.look_name()])
		return
	else:
		var node: Node3D = _timeline.targets.get(id)
		if node:
			_timeline.add_obj_key(id, _timeline.time, node.global_position, node.rotation_degrees, node.scale)
	_flash("keyframe @ %.1fs on '%s'" % [_timeline.time, id])


## Snapshot the whole lighting/fog rig as a JSON-safe dict for a timeline cue.
func _capture_light_state() -> Dictionary:
	return {
		"look": _lighting.look_name(),
		"formation": _lighting.formation_name(),
		"speed": _lighting.speed_idx,
		"strobe": _lighting.strobe,
		"blackout": _lighting.blackout,
		"master": _lighting.master,
		"gobo": _lighting.gobo_name(),
		"gel": _lighting.gel_name(),
		"mix": _lighting.filter_mix,
		"stage": _stage_level,
		"fog": (_env.volumetric_fog_density if _env else 0.03),
		"volfog": _volfog_amt,
		"lowfog": _lowfog_amt,
	}


## Apply a captured light-cue dict (fired by the Timeline as the playhead crosses).
func _apply_light_cue(d: Dictionary) -> void:
	# stage level first (it rebuilds the rig + forces a look) so the cue's own
	# look/formation below win; only rebuild when the level actually changes.
	var lvl := int(d.get("stage", _stage_level))
	if lvl != _stage_level:
		_set_stage(lvl)
	if d.has("look"):
		_lighting.use_look(String(d["look"]))
	if d.has("formation"):
		_lighting.use_formation(String(d["formation"]))
	if d.has("speed"):
		_lighting.use_speed_idx(int(d["speed"]))
	if d.has("mix"):
		_lighting.filter_mix = bool(d["mix"])
	if d.has("gel"):
		_lighting.use_gel(String(d["gel"]))
	if d.has("gobo"):
		_lighting.use_gobo(String(d["gobo"]))   # also re-applies projectors
	_lighting.strobe = bool(d.get("strobe", _lighting.strobe))
	_lighting.blackout = bool(d.get("blackout", _lighting.blackout))
	_lighting.set_master(float(d.get("master", _lighting.master)))
	if _env and d.has("fog"):
		_env.volumetric_fog_density = clampf(float(d["fog"]), 0.0, 0.15)
	if d.has("volfog"):
		_volfog_amt = clampf(float(d["volfog"]), 0.0, 1.0)
		if _volfog:
			_volfog.set_density(_volfog_amt)
	if d.has("lowfog"):
		_lowfog_amt = clampf(float(d["lowfog"]), 0.0, 1.0)
		if _lowfog:
			_lowfog.set_density(_lowfog_amt)
	_update_hud()


func _timeline_play() -> void:
	if _timeline.playing:
		_timeline.stop()
	else:
		_director_active = false
		_cam.current = true
		_timeline.play()
	_update_hud()


## Force all UI overlays on/off (used by capture to grab clean frames).
func _set_chrome(v: bool) -> void:
	if _hud_panel:
		_hud_panel.visible = v
	if _help_panel:
		_help_panel.visible = v and _help_shown
	if _tlui:
		_tlui.visible = v


## Restore overlays to their intended state (master UI toggle + help toggle).
func _apply_chrome() -> void:
	_set_chrome(_ui_on)


## Keywords that map a sky image filename to a mood (robust to arbitrary names).
const SKY_KEYWORDS := {
	"dusk": ["dusk", "dawn", "evening", "sunset", "golden", "day", "afternoon"],
	"night": ["night", "dark", "star", "moon", "overcast", "cloud", "midnight"],
	"disaster": ["disaster", "dust", "storm", "smoke", "chaos", "apocalyp"],
}

## Find a sky image for a mood: exact <id>.<ext> first, else any file in
## res://assets/sky/ whose name contains a keyword for that mood.
func _sky_image_for(id: String) -> String:
	for ext in ["hdr", "exr", "png", "jpg", "jpeg", "webp"]:
		var p := "res://assets/sky/%s.%s" % [id, ext]
		if ResourceLoader.exists(p):
			print("[previz] sky '%s' → %s (exact)" % [id, p])
			return p
	var keys: Array = SKY_KEYWORDS.get(id, [id])
	var dir := DirAccess.open("res://assets/sky")
	if dir:
		dir.list_dir_begin()
		var fn := dir.get_next()
		while fn != "":
			if not dir.current_is_dir() and fn.get_extension().to_lower() in ["hdr", "exr", "png", "jpg", "jpeg", "webp"]:
				var low := fn.to_lower()
				for k in keys:
					if low.find(k) != -1:
						var p := "res://assets/sky/" + fn
						if ResourceLoader.exists(p):
							print("[previz] sky '%s' → %s (keyword '%s')" % [id, p, k])
							return p
			fn = dir.get_next()
	print("[previz] sky '%s' → none in assets/sky — using procedural sky" % id)
	return ""


## Build a sky material from an image: a Cubemap → cube sky shader; otherwise an
## equirectangular panorama (Godot bakes it into the radiance cubemap).
func _make_sky_material(path: String) -> Material:
	var res: Resource = load(path)
	if res is Cubemap:
		var sh := Shader.new()
		sh.code = "shader_type sky;\nuniform samplerCube tex : source_color;\nvoid sky() {\n\tCOLOR = texture(tex, EYEDIR).rgb;\n}\n"
		var sm := ShaderMaterial.new()
		sm.shader = sh
		sm.set_shader_parameter("tex", res)
		print("[previz] sky material: cubemap %s" % path)
		return sm
	var pano := PanoramaSkyMaterial.new()
	pano.panorama = res
	if res is Texture2D:
		var w := (res as Texture2D).get_width()
		var h := (res as Texture2D).get_height()
		var ratio := float(w) / float(maxi(h, 1))
		print("[previz] sky panorama %s — %dx%d (ratio %.2f)" % [path, w, h, ratio])
		if absf(ratio - 2.0) > 0.4:
			print("[previz]   ⚠ not ~2:1 — this looks like a CUBEMAP/non-equirect image; it will map wrong as a panorama")
	return pano


func _fog_adjust(dir: float) -> void:
	if _env == null:
		return
	# general (ambient) fog reads best at a FRACTION of a percent, so step it in
	# fine 0.03% increments and cap low — beam shafts get their punch from the
	# fixtures' volumetric scatter, not from a thick ambient haze.
	var cur := _env.volumetric_fog_density + dir * 0.0003
	cur = clampf(cur, 0.0, 0.012)
	_env.volumetric_fog_density = cur
	_flash("general fog %.2f%%" % (cur * 100.0))


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


## Clean full-screen capture view: native-res fullscreen, all UI hidden behind it.
func _toggle_fullscreen() -> void:
	_fullscreen = not _fullscreen
	DisplayServer.window_set_mode(
		DisplayServer.WINDOW_MODE_FULLSCREEN if _fullscreen else DisplayServer.WINDOW_MODE_WINDOWED
	)
	_ui_on = not _fullscreen   # clean render in fullscreen; UI back when windowed
	_apply_chrome()


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
			KEY_H:
				_ui_on = not _ui_on   # master: clean render with all UI hidden
				_apply_chrome()
				_flash("UI %s" % ("on" if _ui_on else "off — clean render"))
			KEY_QUOTELEFT:
				_help_shown = not _help_shown
				if _help_panel:
					_help_panel.visible = _ui_on and _help_shown
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
				_fog_adjust(-1.0)
			KEY_8:
				_fog_adjust(1.0)
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
			KEY_F9:
				_lighting.cycle_gobo()
				_flash("gobo: %s" % _lighting.gobo_name())
			KEY_F10:
				_lighting.toggle_filter_mix()
				_flash("filter mix %s" % ("ON" if _lighting.filter_mix else "off"))
			KEY_F11:
				_lighting.cycle_gel()
				_flash("gel: %s" % _lighting.gel_name())
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
		_lighting.build(STAGE_FLAT_X, level)
		_lighting.use_look(["garage rock", "kraut shafts", "anthem rwb"][clampi(level - 1, 0, 2)])


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
	_apply_chrome()
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
	_apply_chrome()
	_flash("saved %s" % path)


# ── HUD ───────────────────────────────────────────────────────────────────────
func _build_hud() -> void:
	var layer := CanvasLayer.new()
	layer.layer = 20   # above the film-look post (layer 1) so the HUD stays crisp
	add_child(layer)
	# live status — top-left
	_hud_panel = _ui_panel()
	_hud_panel.position = Vector2(14.0, 12.0)
	layer.add_child(_hud_panel)
	_hud = _hud_panel.get_child(0)
	# keymap cheat-sheet — bottom-left, hidden until `
	_help_panel = _ui_panel()
	_help_panel.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	_help_panel.position = Vector2(14.0, -10.0)
	_help_panel.grow_vertical = Control.GROW_DIRECTION_BEGIN
	_help_panel.visible = false
	layer.add_child(_help_panel)
	_help = _help_panel.get_child(0)
	_help.add_theme_font_size_override("font_size", 13)
	_help.text = _help_text()
	_update_hud()


## A dark, rounded, padded panel wrapping a single Label (returned as child 0).
func _ui_panel() -> PanelContainer:
	var pc := PanelContainer.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.03, 0.03, 0.045, 0.66)
	sb.set_corner_radius_all(6)
	sb.set_content_margin_all(11)
	sb.border_color = Color(0.8, 0.66, 0.3, 0.22)
	sb.set_border_width_all(1)
	pc.add_theme_stylebox_override("panel", sb)
	var lbl := Label.new()
	lbl.add_theme_font_size_override("font_size", 14)
	lbl.add_theme_color_override("font_color", Color(0.86, 0.83, 0.74))
	pc.add_child(lbl)
	return pc


## Static keymap, grouped by area for readability (toggle with `).
func _help_text() -> String:
	return "\n".join([
		"NAV    [WASD] move   [Q/E] down/up   [RMB] look   [-/=] dimmer",
		"STAGE  [1/2/3] set    [Z/X/C] mood",
		"CAMERA [K] add cam  [M] move type  [Tab] fly/director  [,/.] prev/next cam  [\\] save dir",
		"TIME   [T] play  [Y] rewind  [;/'] scrub  [O] track  [J] keyframe",
		"REF    [G] place  [L] image  [U] cue        STORYBOARD [I] import  [N/B] step",
		"LX     [4] look  [5] strobe  [6] blackout  [7/8] fog  [F5] formation  [F6] speed  [9] follow",
		"FILTER [F9] gobo (shape)  [F10] mix  [F11] gel (colour)",
		"FOG    [F1/F2] volume smoke   [F3/F4] stage fog",
		"FX     [V] helicopter+debris   [0] reset",
		"VIEW   [F] fullscreen   [H] hide all UI   [P] screenshot   [R] render shots   [F7] film  [F8] assets",
	])


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
		var filt := "%s/%s%s" % [_lighting.gobo_name(), _lighting.gel_name(), (" mix" if _lighting.filter_mix else "")]
		lx_line = "\nLX    %s · %s@%s · dim %d%%%s%s\nFILT  %s\nFOG   general %.2f%% · smoke %d%% · stage %d%%" % [
			_lighting.look_name(), _lighting.formation_name(), _lighting.speed_name(),
			int(_lighting.master * 100.0),
			("  STROBE" if _lighting.strobe else ""), ("  BLACKOUT" if _lighting.blackout else ""),
			filt,
			(_env.volumetric_fog_density * 100.0 if _env else 0.0), int(_volfog_amt * 100.0), int(_lowfog_amt * 100.0),
		]
	var cp := _cam.global_position if _cam else Vector3.ZERO
	_hud.text = "STAGE %d — %s   ·   %s\nCAM   %s%s%s%s\nmove [M]: %s   cam@(%.0f, %.0f, %.0f)   press ` for controls" % [
		_stage_level, band, mood.get("label", _mood),
		cam_line, shot_line, tl_line, lx_line, CameraDirector.MOVES[_pending_move],
		cp.x, cp.y, cp.z
	]


func _flash(msg: String) -> void:
	if _hud:
		_hud.text = msg
