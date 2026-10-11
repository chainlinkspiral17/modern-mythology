class_name MusicDirector
extends Node
## MusicDirector
## ════════════════════════════════════════════════════════════════
## Directs the visual novels' music the way GameEngine directs their
## scenes. GameEngine owns one, calls begin_scene() on every scene load
## and on_node() for every node it dispatches; the director decides
## WHICH track plays and HOW HARD it plays (intensity → the layered
## stems AudioMgr builds from a track's .stems.json).
##
## Single source of truth: res://resources/music/direction.json
## (edit the authored sections; `python3 godot/tools/music_direction.py
## suggest` regenerates the *_auto ones; CI runs `validate`).
##
## TRACK — first rule that names something playable wins:
##   1. scene cue sheet "track" (direction.json "scenes")      → crossfade
##   2. {"t":"music","track":…} / existing {"t":"bgm"} nodes   → as authored
##   3. the scene's focal character's theme (leitmotif): the
##      themed character with the most lines, ≥ 30 % of them  → queued
##   4. the background's locale track ("locales", "locales_auto") → queued
##   5. otherwise AudioMgr's chapter list / queue, as before
##   A track only counts if AudioMgr.can_play(src) — missing catalog
##   audio never silences a scene that already has music.
##
## INTENSITY (0..1) — smoothed (attack / release seconds):
##   authored: cue sheet "intensity", beats ({"at": node | "choice" |
##   "cg" | "interlude" | "end"}), {"t":"music","intensity":…} nodes.
##   An authored value holds until the next authored one ({"auto": true}
##   hands control back to inference).
##   inferred: scene baseline from the whole scene's tension, then per
##   node — tension / calm words, exclamations, clipped lines, think =
##   quieter; choice = anticipation, interlude = breath, cg = lift.
##
## Readout: shown with the VN debug panel (Shift+F12), hidden by F4.
## ════════════════════════════════════════════════════════════════

signal directed(state: Dictionary)

const DIRECTION_PATH := "res://resources/music/direction.json"
const STINGER_DIR := "assets/audio/stingers/"
const FPC_SCRIPT = preload("res://scripts/FirstPersonController.gd")
const DEBUG_OVERLAY_SCRIPT = preload("res://scripts/vn/VnPortraitDebugOverlay.gd")

static var _data: Dictionary = {}
static var _catalog_by_id: Dictionary = {}
static var _loaded := false

var _scene_id := ""
var _vol := 0
var _cue: Dictionary = {}
var _nodes: Array = []
var _baseline := 0.5
var _target := 0.5
var _level := 0.5
var _sent := -1.0
var _pinned := false
var _track_src := ""
var _track_reason := ""
var _int_reason := ""
var _focal := ""
var _scene_has_bgm := false
var _quiet := false          # replaying a save: compute, don't announce
var _readout: Label = null
var _readout_layer: CanvasLayer = null


# ── data ─────────────────────────────────────────────────────────────
static func load_direction() -> void:
	if _loaded:
		return
	_loaded = true
	if FileAccess.file_exists(DIRECTION_PATH):
		var d = JSON.parse_string(FileAccess.get_file_as_string(DIRECTION_PATH))
		if typeof(d) == TYPE_DICTIONARY:
			_data = d
		else:
			push_warning("MusicDirector: direction.json is not valid JSON — directing by inference only")
	for e: Dictionary in SceneDataDB.get_music_catalog():
		_catalog_by_id[str(e.get("id", ""))] = e


static func _section(name: String) -> Dictionary:
	var s = _data.get(name, {})
	return s if typeof(s) == TYPE_DICTIONARY else {}


func _d(key: String, fallback: float) -> float:
	return float(_section("defaults").get(key, fallback))


func _src_of(track_id: String) -> String:
	var e: Dictionary = _catalog_by_id.get(track_id, {})
	return str(e.get("src", ""))


# ── lifecycle ────────────────────────────────────────────────────────
func _ready() -> void:
	load_direction()
	_build_readout()


func begin_scene(scene_id: String, scene_data: Dictionary) -> void:
	load_direction()
	_scene_id = scene_id
	_vol = int(scene_data.get("vol", 0))
	_nodes = scene_data.get("nodes", [])
	var cue = _section("scenes").get(scene_id, {})
	_cue = cue if typeof(cue) == TYPE_DICTIONARY else {}
	_pinned = false
	_scene_has_bgm = _has_bgm_directive()
	_focal = _focal_character()
	_baseline = clampf(_d("base_intensity", 0.5) + _scene_tension() * 0.6, 0.15, 0.9)
	if _cue.has("intensity"):
		_baseline = clampf(float(_cue.intensity), 0.0, 1.0)
		_pinned = true
		_int_reason = "cue sheet"
	else:
		_int_reason = "scene baseline (writing)"
	_target = _baseline
	# track
	if bool(_cue.get("silence", false)):
		_set_silence("cue sheet")
	elif _cue.has("track") and _play_track(str(_cue.track), true, "cue sheet"):
		pass
	elif _scene_has_bgm:
		_track_reason = "scene's bgm / music directives"
	elif _focal != "" and _play_track(_theme_of(_focal), false, "leitmotif · " + _focal):
		pass
	else:
		_track_reason = "chapter / queue"
	_emit()


func on_node(idx: int, n: Dictionary) -> void:
	var t: String = str(n.get("t", ""))
	# authored beats for this node (by index, or by kind)
	for b in _cue.get("beats", []):
		if typeof(b) != TYPE_DICTIONARY:
			continue
		var at = b.get("at")
		if (typeof(at) == TYPE_INT or typeof(at) == TYPE_FLOAT) and int(at) == idx:
			apply(b, "beat @%d" % idx)
		elif typeof(at) == TYPE_STRING and at == t:
			apply(b, "beat @" + t)
	match t:
		"music":
			apply(n, "music node")
		"bg":
			if not _cue.has("track") and not _scene_has_bgm:
				var lt := _locale_track(str(n.get("src", "")))
				if lt != "" and _track_reason.begins_with("chapter"):
					_play_track(lt, false, "locale · " + str(n.get("src", "")))
		"choice":
			_infer(_d("choice_intensity", 0.85), "choice — anticipation", true)
		"interlude":
			_infer(_d("interlude_intensity", 0.2), "interlude — breath", false)
		"cg":
			_infer(_d("cg_intensity", 0.9), "cg — reveal", true)
		"narrate", "say", "think":
			var s := _text_score(str(n.get("text", "")))
			if t == "think":
				s += _d("think_offset", -0.1)
			_infer(clampf(_baseline + s, 0.05, 1.0), "writing (%+.2f)" % s, false)
		"end":
			if bool(_section("defaults").get("end_of_volume_release", true)):
				_infer(_baseline * 0.6, "scene end — release", false)
	_emit()


# Fast-forward for a mid-scene save load: rebuild the intensity state.
func replay(upto: int) -> void:
	_quiet = true
	for i in range(mini(upto, _nodes.size())):
		var n: Dictionary = _nodes[i]
		if str(n.get("t", "")) in ["narrate", "say", "think", "music", "choice"]:
			on_node(i, n)
	_quiet = false
	_level = _target
	_send(true)
	# a locale / leitmotif track chosen while replaying hasn't been started yet
	if _track_src != "" and not AudioMgr.is_playing():
		AudioMgr.play_bgm(_track_src)


# Apply an authored directive: {track, intensity, stinger, silence, fade, hard, auto}
func apply(d: Dictionary, why: String) -> void:
	var num := func(v) -> bool: return typeof(v) == TYPE_INT or typeof(v) == TYPE_FLOAT
	var fade := float(d.fade) if num.call(d.get("fade")) else 2.0
	if bool(d.get("silence", false)):
		_set_silence(why)
		return
	if typeof(d.get("track")) == TYPE_STRING and str(d.track) != "":
		_play_track(str(d.track), bool(d.get("hard", true)), why)
	if num.call(d.get("intensity")):
		_target = clampf(float(d.intensity), 0.0, 1.0)
		_pinned = true
		_int_reason = why
		if fade <= 0.05:
			_level = _target
	if bool(d.get("auto", false)):
		_pinned = false
		_int_reason = why + " → inference"
	if d.has("stinger"):
		var path := STINGER_DIR + str(d.stinger) + ".ogg"
		if AudioMgr.can_play(path):
			AudioMgr.play_sfx(path)


# ── decisions ────────────────────────────────────────────────────────
func _infer(v: float, why: String, peak: bool) -> void:
	if _pinned:
		return
	_target = maxf(_target, v) if peak else v
	_int_reason = why


func _play_track(track_id: String, hard: bool, why: String) -> bool:
	var src := _src_of(track_id) if not track_id.contains("/") else track_id
	if src == "" or not AudioMgr.can_play(src):
		return false
	_track_src = src
	_track_reason = why
	if _quiet or src == AudioMgr.get_current_track():
		return true
	if hard or not AudioMgr.is_playing():
		AudioMgr.play_bgm(src)
	else:
		AudioMgr.enqueue_music(src)
	return true


func _set_silence(why: String) -> void:
	_track_src = ""
	_track_reason = "silence · " + why
	if not _quiet:
		AudioMgr.stop_bgm()


func _has_bgm_directive() -> bool:
	for n in _nodes:
		var t := str(n.get("t", ""))
		if t == "bgm" or (t == "music" and n.has("track")):
			return true
	return false


func _theme_of(char_key: String) -> String:
	for sec in ["characters", "characters_auto"]:
		var m = _section(sec).get(char_key)
		if typeof(m) == TYPE_DICTIONARY:
			if not bool(m.get("leitmotif", true)):
				return ""
			return str(m.get("theme", ""))
	return ""


# The themed character who carries the scene: most say/think lines, ≥ 30 %.
func _focal_character() -> String:
	if not bool(_section("defaults").get("leitmotifs", true)):
		return ""
	var counts := {}
	var total := 0
	for n in _nodes:
		if str(n.get("t", "")) in ["say", "think"] and n.get("char") is String:
			var k := _char_key(str(n.char))
			counts[k] = int(counts.get(k, 0)) + 1
			total += 1
	var best := ""
	var best_n := 0
	for k in counts:
		if counts[k] > best_n and _theme_of(k) != "":
			best = k
			best_n = counts[k]
	return best if total > 0 and float(best_n) / float(total) >= 0.3 else ""


# same slug as CharLayer.char_key — the catalog's "chars" tags use it
static func _char_key(name: String) -> String:
	return name.strip_edges().to_lower().replace(" ", "_")


func _locale_track(bg_src: String) -> String:
	for sec in ["locales", "locales_auto"]:
		var m = _section(sec).get(bg_src)
		if typeof(m) == TYPE_STRING:
			return m
		if typeof(m) == TYPE_DICTIONARY and m.has(str(_vol)):
			return str(m[str(_vol)])
	return ""


# Tension of a line, −0.5 … +0.5: lexicon words, exclamations, clipped / shouted lines.
func _text_score(text: String) -> float:
	if text == "":
		return 0.0
	var low := text.to_lower()
	var lex := _section("lexicon")
	var step := _d("word_step", 0.12)
	var s := 0.0
	var words := {}
	for w in low.split(" ", false):
		words[w.strip_edges().trim_suffix(".").trim_suffix(",").trim_suffix("!").trim_suffix("?").trim_suffix("—")] = true
	for w in lex.get("tension", []):
		if (" " in w and low.contains(w)) or words.has(w):
			s += step
	for w in lex.get("calm", []):
		if (" " in w and low.contains(w)) or words.has(w):
			s -= step * 0.75
	s += 0.06 * mini(3, text.count("!"))
	if text.length() < 28 and (text.ends_with("!") or text.ends_with("?") or text.ends_with("—")):
		s += 0.05
	var caps := 0
	for w in text.split(" ", false):
		if w.length() >= 3 and w == w.to_upper() and w != w.to_lower():
			caps += 1
	s += 0.04 * mini(3, caps)
	if text.contains("…") or text.contains("..."):
		s -= 0.03
	return clampf(s, -0.5, 0.5)


func _scene_tension() -> float:
	var total := 0.0
	var n := 0
	for node in _nodes:
		if str(node.get("t", "")) in ["narrate", "say", "think"]:
			total += _text_score(str(node.get("text", "")))
			n += 1
	return total / float(n) if n > 0 else 0.0


# ── output ───────────────────────────────────────────────────────────
func _process(delta: float) -> void:
	var tau := _d("attack_sec", 2.5) if _target > _level else _d("release_sec", 8.0)
	_level = move_toward(_level, _target, delta / maxf(0.05, tau))
	_send(false)
	_update_readout()


func _send(force: bool) -> void:
	if force or absf(_level - _sent) >= 0.02:
		_sent = _level
		AudioMgr.set_music_intensity(_level, 0.4)


func state() -> Dictionary:
	return {
		"scene": _scene_id, "track": _track_src, "track_reason": _track_reason,
		"intensity": snappedf(_level, 0.01), "target": snappedf(_target, 0.01),
		"intensity_reason": _int_reason, "baseline": snappedf(_baseline, 0.01),
		"pinned": _pinned, "focal": _focal,
	}


func _emit() -> void:
	if not _quiet:
		directed.emit(state())


# ── readout (with the VN debug panel; F4 hides it) ──────────────────
func _build_readout() -> void:
	_readout_layer = CanvasLayer.new()
	_readout_layer.layer = 121
	_readout_layer.add_to_group("ui")
	_readout_layer.visible = FPC_SCRIPT.hud_visible
	add_child(_readout_layer)
	_readout = Label.new()
	_readout.add_theme_font_size_override("font_size", 11)
	_readout.add_theme_color_override("font_color", Color(0.95, 0.85, 0.55))
	_readout.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	_readout.add_theme_constant_override("outline_size", 3)
	_readout.position = Vector2(8, 6)
	_readout.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_readout_layer.add_child(_readout)


func _update_readout() -> void:
	if _readout_layer == null:
		return
	var show := FPC_SCRIPT.hud_visible and DEBUG_OVERLAY_SCRIPT._show_pref
	_readout_layer.visible = show
	if not show:
		return
	var tr := _track_src.get_file() if _track_src != "" else "—"
	_readout.text = "♪ %s  (%s)\n◢ intensity %.2f → %.2f  (%s)%s" % [
		tr, _track_reason, _level, _target, _int_reason, "  · pinned" if _pinned else ""]
