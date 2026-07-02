class_name CameraDirector
extends Node3D
## Multiple named cameras, each with a keyframed move on its own time axis.
## Keyframes are generated from storyboard-style move presets (the same
## vocabulary as the HTML Storyboard tool), then sampled/interpolated
## (position + look-at target + fov) for smooth playback and scrubbing.
## Phase 3 (storyboard import) reuses add_camera() to build a camera per shot.

const MOVES := [
	"Static locked-off", "Slow push in", "Slow pull out",
	"Crane up over crowd", "Crane down to stage",
	"Lateral dolly left", "Lateral dolly right",
	"Orbit around performer", "Whip pan", "Handheld drift",
	"Rise to reveal bay doors", "Boom down through haze",
]

var cams: Array = []   # each: { name, move, duration, keys:[{t,pos,target,fov}] }
var active := -1
var time := 0.0
var playing := false
var cam: Camera3D


func _ready() -> void:
	cam = Camera3D.new()
	add_child(cam)


func count() -> int:
	return cams.size()


func active_info() -> Dictionary:
	if active < 0 or active >= cams.size():
		return {}
	return cams[active]


## Create a camera whose keyframed move starts from the given pose.
func add_camera(cam_name: String, pos: Vector3, target: Vector3, fov: float, move: String, duration := 6.0) -> int:
	cams.append({
		"name": cam_name, "move": move, "duration": duration,
		"keys": _gen_keys(move, pos, target, fov, duration),
	})
	active = cams.size() - 1
	time = 0.0
	_apply(active, 0.0)
	return active


func select(i: int) -> void:
	if cams.is_empty():
		return
	active = wrapi(i, 0, cams.size())
	time = 0.0
	_apply(active, 0.0)


func play() -> void:
	if active >= 0:
		playing = true


func stop() -> void:
	playing = false


func clear() -> void:
	cams.clear()
	active = -1
	time = 0.0
	playing = false


func make_current() -> void:
	if active >= 0:
		cam.current = true


func scrub(dt: float) -> void:
	if active < 0:
		return
	time = clampf(time + dt, 0.0, float(cams[active]["duration"]))
	_apply(active, time)


func _process(delta: float) -> void:
	if playing and active >= 0:
		time += delta
		if time > float(cams[active]["duration"]):
			time = 0.0   # loop for preview
		_apply(active, time)


func _apply(i: int, t: float) -> void:
	var s := sample(cams[i], t)
	cam.global_position = s["pos"]
	cam.fov = s["fov"]
	var tgt: Vector3 = s["target"]
	if cam.global_position.distance_to(tgt) > 0.01:
		cam.look_at(tgt, Vector3.UP)


## Interpolate pos/target/fov at time t (smoothstep eased between keys).
func sample(setup: Dictionary, t: float) -> Dictionary:
	var keys: Array = setup["keys"]
	if keys.is_empty():
		return { "pos": Vector3.ZERO, "target": Vector3.FORWARD, "fov": 45.0 }
	if t <= float(keys[0]["t"]):
		return _key_state(keys[0])
	var last: Dictionary = keys[keys.size() - 1]
	if t >= float(last["t"]):
		return _key_state(last)
	for i in range(keys.size() - 1):
		var a: Dictionary = keys[i]
		var b: Dictionary = keys[i + 1]
		if t >= float(a["t"]) and t <= float(b["t"]):
			var span: float = maxf(0.0001, float(b["t"]) - float(a["t"]))
			var u := smoothstep(0.0, 1.0, (t - float(a["t"])) / span)
			return {
				"pos": (a["pos"] as Vector3).lerp(b["pos"], u),
				"target": (a["target"] as Vector3).lerp(b["target"], u),
				"fov": lerpf(float(a["fov"]), float(b["fov"]), u),
			}
	return _key_state(last)


func _key_state(k: Dictionary) -> Dictionary:
	return { "pos": k["pos"], "target": k["target"], "fov": k["fov"] }


# ── move presets → keyframes ────────────────────────────────────────────────
func _k(t: float, p: Vector3, tg: Vector3, f: float) -> Dictionary:
	return { "t": t, "pos": p, "target": tg, "fov": f }


func _gen_keys(move: String, p: Vector3, t: Vector3, f: float, d: float) -> Array:
	var to_target := t - p
	var dist := to_target.length()
	var fwd := to_target.normalized() if dist > 0.001 else Vector3(0, 0, -1)
	var right := fwd.cross(Vector3.UP).normalized()
	var up := Vector3.UP
	match move:
		"Slow push in":
			return [_k(0.0, p, t, f), _k(d, p + fwd * dist * 0.35, t, f)]
		"Slow pull out":
			return [_k(0.0, p, t, f), _k(d, p - fwd * dist * 0.4, t, f)]
		"Crane up over crowd":
			return [_k(0.0, p, t, f), _k(d, p + up * 8.0, t, f)]
		"Crane down to stage":
			return [_k(0.0, p, t, f), _k(d, p - up * 6.0, t, f)]
		"Lateral dolly left":
			return [_k(0.0, p, t, f), _k(d, p - right * 10.0, t - right * 10.0, f)]
		"Lateral dolly right":
			return [_k(0.0, p, t, f), _k(d, p + right * 10.0, t + right * 10.0, f)]
		"Orbit around performer":
			var keys: Array = []
			var steps := 6
			var total := deg_to_rad(70.0)
			for i in steps + 1:
				var ang := total * (float(i) / float(steps))
				var off := (p - t).rotated(Vector3.UP, ang)
				keys.append(_k(d * float(i) / float(steps), t + off, t, f))
			return keys
		"Whip pan":
			return [_k(0.0, p, t, f), _k(d * 0.6, p, t, f), _k(d, p, t + right * 40.0, f)]
		"Handheld drift":
			return [_k(0.0, p, t, f), _k(d * 0.5, p + right * 0.4 + up * 0.3, t, f), _k(d, p - right * 0.3 + up * 0.2, t, f)]
		"Rise to reveal bay doors":
			return [_k(0.0, p, t, f), _k(d, p + up * 5.0, Vector3(60.0, t.y, t.z), f)]
		"Boom down through haze":
			return [_k(0.0, p + up * 6.0, t, f), _k(d, p, t, f)]
		_:
			return [_k(0.0, p, t, f)]


# ── persistence ─────────────────────────────────────────────────────────────
func _v(v: Vector3) -> Array:
	return [v.x, v.y, v.z]


func save_json(path: String) -> void:
	var out: Array = []
	for c in cams:
		var keys: Array = []
		for k in c["keys"]:
			keys.append({ "t": k["t"], "pos": _v(k["pos"]), "target": _v(k["target"]), "fov": k["fov"] })
		out.append({ "name": c["name"], "move": c["move"], "duration": c["duration"], "keys": keys })
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify({ "cameras": out }, "\t"))
		f.close()
