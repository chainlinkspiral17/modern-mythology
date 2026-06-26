class_name StoryboardIO
extends RefCounted
## Bridges the HTML Storyboard Pipeline tool and the previz scene.
##
## IMPORT: reads a Storyboard JSON export (the `doc` object: sets + segments)
## and maps each shot to a previz state — stage level (by set order), lighting
## mood (by time-of-day / kind), camera move (shared vocabulary) and a default
## framing derived from the shot type.
##
## EXPORT: writes per-shot camera/light data + rendered frame paths back out as
## user://storyboard_previz.json, to fold into the storyboard tool as start
## frames + camera notes.

static func load_doc(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {}
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	return data if data is Dictionary else {}


## doc -> ordered Array of shot dicts: { title, band, level, mood, move,
## duration, framing:{pos,target,fov}, shot_type, lip }
static func map_shots(doc: Dictionary, stage_x: float) -> Array:
	var sets: Array = doc.get("sets", [])
	var level_by_set := {}
	var band_by_set := {}
	for i in sets.size():
		var s: Dictionary = sets[i]
		level_by_set[s.get("id", "")] = clampi(i + 1, 1, 3)
		band_by_set[s.get("id", "")] = s.get("band", "")
	var default_clip: float = float(doc.get("settings", {}).get("clipSec", 8))
	var out: Array = []
	for seg in doc.get("segments", []):
		var sid: String = seg.get("setId", "")
		var level: int = level_by_set.get(sid, 1)
		var move: String = seg.get("camera", "Static locked-off")
		if not (move in CameraDirector.MOVES):
			move = "Static locked-off"
		var dur: float = float(seg.get("durationSec", 0))
		if dur <= 0.0:
			dur = default_clip
		out.append({
			"title": seg.get("title", seg.get("shotType", "shot")),
			"band": band_by_set.get(sid, ""),
			"level": level,
			"mood": _mood_for(str(seg.get("timeOfDay", "")), str(seg.get("kind", "")), level),
			"move": move,
			"duration": dur,
			"framing": _framing(str(seg.get("shotType", "")), stage_x),
			"shot_type": seg.get("shotType", ""),
			"lip": seg.get("lipSync", false),
		})
	return out


static func _mood_for(tod: String, kind: String, level: int) -> String:
	var t := tod.to_lower()
	if t.find("night") >= 0:
		return "night"
	if t.find("dusk") >= 0:
		return "dusk"
	if kind == "sfx":
		return "disaster"
	return "night" if level >= 3 else "dusk"


## Default camera framing for a shot type, in world space near the stage mouth.
static func _framing(shot_type: String, sx: float) -> Dictionary:
	match shot_type:
		"Close — performer":
			return { "pos": Vector3(sx + 8.0, 3.5, 1.5), "target": Vector3(sx - 1.0, 3.2, 0.0), "fov": 30.0 }
		"Medium — band":
			return { "pos": Vector3(sx + 12.0, 4.0, 3.0), "target": Vector3(sx - 1.0, 3.0, 0.0), "fov": 38.0 }
		"Insert / detail":
			return { "pos": Vector3(sx + 5.0, 2.5, 1.0), "target": Vector3(sx - 1.0, 2.5, 0.0), "fov": 24.0 }
		"Stage wide":
			return { "pos": Vector3(sx + 22.0, 7.0, 0.0), "target": Vector3(sx - 1.0, 4.0, 0.0), "fov": 46.0 }
		"Establishing wide":
			return { "pos": Vector3(sx + 70.0, 12.0, 8.0), "target": Vector3(sx, 7.0, 0.0), "fov": 50.0 }
		"Crowd wide":
			return { "pos": Vector3(sx + 4.0, 6.0, 0.0), "target": Vector3(sx + 50.0, 3.0, 0.0), "fov": 55.0 }
		"POV crowd":
			return { "pos": Vector3(sx + 45.0, 2.0, 0.0), "target": Vector3(sx - 1.0, 5.0, 0.0), "fov": 34.0 }
		"Overhead":
			return { "pos": Vector3(sx + 15.0, 30.0, 0.0), "target": Vector3(sx, 2.0, 0.0), "fov": 50.0 }
		"Crane up", "Crane down":
			return { "pos": Vector3(sx + 20.0, 9.0, 0.0), "target": Vector3(sx - 1.0, 4.0, 0.0), "fov": 42.0 }
		"Tracking":
			return { "pos": Vector3(sx + 12.0, 4.0, 6.0), "target": Vector3(sx - 1.0, 3.0, 0.0), "fov": 40.0 }
		"Silhouette":
			return { "pos": Vector3(sx + 18.0, 5.0, 0.0), "target": Vector3(sx - 1.0, 4.0, 0.0), "fov": 45.0 }
		_:
			return { "pos": Vector3(sx + 22.0, 7.0, 0.0), "target": Vector3(sx - 1.0, 4.0, 0.0), "fov": 45.0 }


static func export_previz(shots: Array, cam_states: Array, path: String) -> void:
	var out: Array = []
	for i in shots.size():
		var sh: Dictionary = shots[i]
		out.append({
			"index": i,
			"title": sh["title"],
			"band": sh["band"],
			"stage_level": sh["level"],
			"mood": sh["mood"],
			"move": sh["move"],
			"duration": sh["duration"],
			"shot_type": sh["shot_type"],
			"camera": cam_states[i] if i < cam_states.size() else {},
		})
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify({ "previz_shots": out }, "\t"))
		f.close()
