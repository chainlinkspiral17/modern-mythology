class_name Timeline
extends Node
## Central sequencer for the previz. A single playhead drives:
##   • a CAMERA track   — keyframes of {pos, look-at target, fov}
##   • OBJECT tracks     — transform keyframes for any registered Node3D
##   • AUDIO cues        — one-shot SFX fired when the playhead crosses them
##   • REF-IMAGE cues    — show a reference image (placement) at a time
## When a music stream is loaded it becomes the master clock, so every track
## "plays along with the music". Save/load to JSON. Lighting/fog/debris cues
## (next phases) hang off this same clock.

var time := 0.0
var duration := 20.0
var playing := false

var cam: Camera3D
var overlay: RefOverlay
var targets := {}            # id -> Node3D

var cam_keys: Array = []     # [{t,pos,target,fov}]
var obj_tracks := {}         # id -> [{t,pos,rot,scale}]
var audio_cues: Array = []   # [{t,path}]
var ref_cues: Array = []     # [{t,path,place}]
var light_cues: Array = []   # [{t,data}] — rig state snapshot, latest-wins

var _light_sink := Callable() # Previz callable that applies a light-cue data dict
var _last_light_t := -1.0     # t of the last-applied light cue (avoid re-applying)

var _music: AudioStreamPlayer
var _sfx: AudioStreamPlayer
var _last_time := 0.0


func setup(camera: Camera3D, ref_overlay: RefOverlay) -> void:
	cam = camera
	overlay = ref_overlay
	_sfx = AudioStreamPlayer.new()
	add_child(_sfx)


func register_target(id: String, node: Node3D) -> void:
	targets[id] = node


func has_music() -> bool:
	return _music != null and _music.stream != null


func music_playing() -> bool:
	return _music != null and _music.playing


func set_music_from_paths(paths: Array) -> bool:
	for p in paths:
		var stream := _load_stream(p)
		if stream:
			if _music == null:
				_music = AudioStreamPlayer.new()
				add_child(_music)
			_music.stream = stream
			return true
	return false


func _load_stream(path: String) -> AudioStream:
	if path != "" and ResourceLoader.exists(path):
		var r: Resource = load(path)
		if r is AudioStream:
			return r
	return null


# ── editing ─────────────────────────────────────────────────────────────────
func add_cam_key(t: float, pos: Vector3, target: Vector3, fov: float) -> void:
	cam_keys.append({ "t": t, "pos": pos, "target": target, "fov": fov })
	cam_keys.sort_custom(func(a, b): return a["t"] < b["t"])
	_recalc()


func add_obj_key(id: String, t: float, pos: Vector3, rot: Vector3, scale: Vector3) -> void:
	if not obj_tracks.has(id):
		obj_tracks[id] = []
	obj_tracks[id].append({ "t": t, "pos": pos, "rot": rot, "scale": scale })
	obj_tracks[id].sort_custom(func(a, b): return a["t"] < b["t"])
	_recalc()


func add_audio_cue(t: float, path: String) -> void:
	audio_cues.append({ "t": t, "path": path })
	audio_cues.sort_custom(func(a, b): return a["t"] < b["t"])
	_recalc()


func add_ref_cue(t: float, path: String, place: int) -> void:
	ref_cues.append({ "t": t, "path": path, "place": place })
	ref_cues.sort_custom(func(a, b): return a["t"] < b["t"])
	_recalc()


func set_light_sink(c: Callable) -> void:
	_light_sink = c


## Snapshot of the lighting rig state at time t. `data` is a flat dict of
## JSON-safe primitives (look/formation names, indices, bools, fog floats).
func add_light_cue(t: float, data: Dictionary) -> void:
	# replace an existing cue at (nearly) the same time rather than stacking
	for c in light_cues:
		if absf(float(c["t"]) - t) < 0.05:
			c["data"] = data
			_last_light_t = -1.0
			return
	light_cues.append({ "t": t, "data": data })
	light_cues.sort_custom(func(a, b): return a["t"] < b["t"])
	_last_light_t = -1.0   # force re-apply on next sample
	_recalc()


func _recalc() -> void:
	var mx := 5.0
	for k in cam_keys:
		mx = maxf(mx, k["t"])
	for id in obj_tracks:
		for k in obj_tracks[id]:
			mx = maxf(mx, k["t"])
	for c in audio_cues:
		mx = maxf(mx, c["t"])
	for c in ref_cues:
		mx = maxf(mx, c["t"])
	for c in light_cues:
		mx = maxf(mx, c["t"])
	if has_music() and _music.stream.get_length() > 0.0:
		mx = maxf(mx, _music.stream.get_length())
	duration = mx + 2.0


# ── transport ────────────────────────────────────────────────────────────────
func play() -> void:
	playing = true
	_last_time = time
	if has_music():
		_music.play(time)


func stop() -> void:
	playing = false
	if has_music():
		_music.stop()


func seek(dt: float) -> void:
	time = clampf(time + dt, 0.0, duration)
	_last_time = time
	if playing and has_music():
		_music.seek(time)
	apply(time)


func _process(delta: float) -> void:
	if not playing:
		return
	if has_music() and _music.playing:
		time = _music.get_playback_position()
	else:
		time += delta
	if time >= duration:
		time = duration
		stop()
	apply(time)
	_fire_cues(_last_time, time)
	_last_time = time


# ── playback ─────────────────────────────────────────────────────────────────
func apply(t: float) -> void:
	if cam and not cam_keys.is_empty():
		var c := _sample_cam(t)
		cam.global_position = c["pos"]
		cam.fov = c["fov"]
		var tgt: Vector3 = c["target"]
		if cam.global_position.distance_to(tgt) > 0.01:
			cam.look_at(tgt, Vector3.UP)
	for id in obj_tracks:
		var node: Node3D = targets.get(id)
		var keys: Array = obj_tracks[id]
		if node == null or keys.is_empty():
			continue
		var s := _sample_obj(keys, t)
		node.global_position = s["pos"]
		node.rotation_degrees = s["rot"]
		node.scale = s["scale"]
	if overlay and not ref_cues.is_empty():
		var rc := _latest_ref(t)
		if rc.is_empty():
			overlay.set_place(RefOverlay.Place.HIDDEN)
		else:
			if overlay.current_path != rc["path"]:
				overlay.load_image(rc["path"])
			overlay.set_place(rc["place"])
	if _light_sink.is_valid() and not light_cues.is_empty():
		var lc := _latest_light(t)
		# only fire when the governing cue changes (cheap, and scrub-safe)
		if not lc.is_empty() and float(lc["t"]) != _last_light_t:
			_last_light_t = float(lc["t"])
			_light_sink.call(lc["data"])


func _fire_cues(t0: float, t1: float) -> void:
	if t1 <= t0:
		return
	for c in audio_cues:
		var ct: float = c["t"]
		if ct > t0 and ct <= t1:
			var stream := _load_stream(c["path"])
			if stream:
				_sfx.stream = stream
				_sfx.play()


func _latest_ref(t: float) -> Dictionary:
	var found := {}
	for c in ref_cues:
		if c["t"] <= t:
			found = c
		else:
			break
	return found


func _latest_light(t: float) -> Dictionary:
	var found := {}
	for c in light_cues:
		if c["t"] <= t:
			found = c
		else:
			break
	return found


# ── interpolation ─────────────────────────────────────────────────────────────
func _seg(keys: Array, t: float) -> Dictionary:
	# returns {a, b, u} for the segment containing t, or {a} as a clamp
	if t <= float(keys[0]["t"]):
		return { "a": keys[0], "b": keys[0], "u": 0.0 }
	var last: Dictionary = keys[keys.size() - 1]
	if t >= float(last["t"]):
		return { "a": last, "b": last, "u": 0.0 }
	for i in range(keys.size() - 1):
		var a: Dictionary = keys[i]
		var b: Dictionary = keys[i + 1]
		if t >= float(a["t"]) and t <= float(b["t"]):
			var span: float = maxf(0.0001, float(b["t"]) - float(a["t"]))
			return { "a": a, "b": b, "u": smoothstep(0.0, 1.0, (t - float(a["t"])) / span) }
	return { "a": last, "b": last, "u": 0.0 }


func _sample_cam(t: float) -> Dictionary:
	var s := _seg(cam_keys, t)
	var a: Dictionary = s["a"]
	var b: Dictionary = s["b"]
	var u: float = s["u"]
	return {
		"pos": (a["pos"] as Vector3).lerp(b["pos"], u),
		"target": (a["target"] as Vector3).lerp(b["target"], u),
		"fov": lerpf(float(a["fov"]), float(b["fov"]), u),
	}


func _sample_obj(keys: Array, t: float) -> Dictionary:
	var s := _seg(keys, t)
	var a: Dictionary = s["a"]
	var b: Dictionary = s["b"]
	var u: float = s["u"]
	return {
		"pos": (a["pos"] as Vector3).lerp(b["pos"], u),
		"rot": (a["rot"] as Vector3).lerp(b["rot"], u),
		"scale": (a["scale"] as Vector3).lerp(b["scale"], u),
	}


# ── persistence ───────────────────────────────────────────────────────────────
func _v(v: Vector3) -> Array:
	return [v.x, v.y, v.z]


func _a2v(a) -> Vector3:
	if a is Array and a.size() >= 3:
		return Vector3(float(a[0]), float(a[1]), float(a[2]))
	return Vector3.ZERO


## Restore a saved timeline (camera/object/audio/ref/light tracks). Returns true
## if a file was read. Defensive — skips malformed entries rather than crashing.
func load_json(path: String) -> bool:
	if not FileAccess.file_exists(path):
		return false
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not (data is Dictionary):
		return false
	cam_keys.clear()
	obj_tracks.clear()
	audio_cues.clear()
	ref_cues.clear()
	light_cues.clear()
	for k in data.get("camera", []):
		cam_keys.append({ "t": float(k.get("t", 0.0)), "pos": _a2v(k.get("pos")), "target": _a2v(k.get("target")), "fov": float(k.get("fov", 50.0)) })
	for id in data.get("objects", {}):
		var arr: Array = []
		for k in data["objects"][id]:
			arr.append({ "t": float(k.get("t", 0.0)), "pos": _a2v(k.get("pos")), "rot": _a2v(k.get("rot")), "scale": _a2v(k.get("scale")) })
		obj_tracks[id] = arr
	for c in data.get("audio_cues", []):
		audio_cues.append({ "t": float(c.get("t", 0.0)), "path": String(c.get("path", "")) })
	for c in data.get("ref_cues", []):
		ref_cues.append({ "t": float(c.get("t", 0.0)), "path": String(c.get("path", "")), "place": int(c.get("place", 0)) })
	for c in data.get("light_cues", []):
		light_cues.append({ "t": float(c.get("t", 0.0)), "data": c.get("data", {}) })
	cam_keys.sort_custom(func(a, b): return a["t"] < b["t"])
	audio_cues.sort_custom(func(a, b): return a["t"] < b["t"])
	ref_cues.sort_custom(func(a, b): return a["t"] < b["t"])
	light_cues.sort_custom(func(a, b): return a["t"] < b["t"])
	_last_light_t = -1.0
	_recalc()
	return true


func save_json(path: String) -> void:
	var cam_out: Array = []
	for k in cam_keys:
		cam_out.append({ "t": k["t"], "pos": _v(k["pos"]), "target": _v(k["target"]), "fov": k["fov"] })
	var obj_out := {}
	for id in obj_tracks:
		var arr: Array = []
		for k in obj_tracks[id]:
			arr.append({ "t": k["t"], "pos": _v(k["pos"]), "rot": _v(k["rot"]), "scale": _v(k["scale"]) })
		obj_out[id] = arr
	var data := {
		"duration": duration,
		"camera": cam_out,
		"objects": obj_out,
		"audio_cues": audio_cues,
		"ref_cues": ref_cues,
		"light_cues": light_cues,
	}
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(data, "\t"))
		f.close()
