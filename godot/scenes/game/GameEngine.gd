extends Control
## Core game loop — walks a scene's node array and dispatches to UI components.

signal game_ended

const DIALOGUE_SCENE  := preload("res://scenes/game/DialogueBox.tscn")
const CHOICE_SCENE    := preload("res://scenes/game/ChoiceMenu.tscn")
const CHAR_SCENE      := preload("res://scenes/game/CharLayer.tscn")
const INTERLUDE_SCENE := preload("res://scenes/game/InterludePanel.tscn")
const CG_SCENE        := preload("res://scenes/game/CgPanel.tscn")
const HUD_SCENE       := preload("res://scenes/game/HudBar.tscn")
const IN_GAME_MENU    := preload("res://scenes/game/InGameMenu.tscn")
const SETTINGS_OV     := preload("res://scenes/menu/SettingsOverlay.tscn")
const MUSIC_OV        := preload("res://scenes/menu/MusicPlayerOverlay.tscn")
const SUBSTRATE_SCRIPT   := preload("res://scenes/game/AsciiSubstrate.gd")
const COMPOSITION_SCRIPT := preload("res://scenes/game/AsciiComposition.gd")

var _vol:         int        = 1
var _scene_id:    String     = ""
var _scene_data:  Dictionary = {}
var _node_idx:    int        = 0
var _flags:       Dictionary = {}
var _skills:      Dictionary = {
	"empathy": 0, "logic": 0, "composure": 0, "rhetoric": 0, "signal": 0
}
var _log:         Array      = []
var _skin:        Dictionary = {}
var _active_slot: int        = -1

var _waiting:     bool  = false
var _auto_timer:  float = 0.0
var _paused:      bool  = false

var _bg_solid:       ColorRect   = null
var _bg_composition: Control     = null
var _substrate:      Control     = null
var _bg:             TextureRect = null
var _dlg_scrim:      ColorRect   = null
var _chars:      Control     = null
var _dlg:        Control     = null
var _choices:    Control     = null
var _interlude:  Control     = null
var _cg:         Control     = null
var _hud:        Control     = null
var _ig_menu:    Control     = null
var _settings_ov: Control   = null
var _music_ov:   Control     = null


func _ready() -> void:
	_build_layers()


func _build_layers() -> void:
	_bg_solid = ColorRect.new()
	_bg_solid.color = Color(0.05, 0.04, 0.03)
	_bg_solid.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_bg_solid)

	# Optional layered composition for scene backgrounds (visualizer +
	# image refs + image_frames + border). Sits above the solid bg and
	# below the ASCII piece substrate so a scene can stack both.
	#
	# z_index = -16 keeps the whole sub-tree behind the UI: composition
	# windows use z values up to ~9 internally, and since CanvasItem
	# z_index is additive with the parent, this guarantees the highest
	# bg layer (-16 + 9 = -7) still renders below sibling UI at z=0.
	_bg_composition = Control.new()
	_bg_composition.set_script(COMPOSITION_SCRIPT)
	_bg_composition.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_bg_composition.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_bg_composition.z_index = -16
	add_child(_bg_composition)

	_substrate = Control.new()
	_substrate.set_script(SUBSTRATE_SCRIPT)
	_substrate.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_substrate)

	_bg = TextureRect.new()
	_bg.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_bg)

	_chars = CHAR_SCENE.instantiate()
	_chars.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_chars)

	# Dialogue scrim — gradient panel between chars and dlg so dialogue
	# text always has a high-contrast surface beneath it regardless of
	# how busy the live-ASCII bg gets.
	_dlg_scrim = ColorRect.new()
	_dlg_scrim.color = Color(0.02, 0.02, 0.04, 0.78)
	_dlg_scrim.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_dlg_scrim.offset_top = -260.0
	_dlg_scrim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_dlg_scrim)

	_dlg = DIALOGUE_SCENE.instantiate()
	add_child(_dlg)
	_dlg.visible = false
	# Scrim follows the dialogue's visibility so full-screen CGs and
	# interludes aren't darkened along the bottom.
	_dlg_scrim.visible = false
	_dlg.visibility_changed.connect(func() -> void: _dlg_scrim.visible = _dlg.visible)

	_choices = CHOICE_SCENE.instantiate()
	_choices.anchor_left   = 0.1
	_choices.anchor_right  = 0.9
	_choices.anchor_top    = 0.15
	_choices.anchor_bottom = 0.85
	add_child(_choices)
	_choices.visible = false

	_interlude = INTERLUDE_SCENE.instantiate()
	_interlude.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_interlude)
	_interlude.visible = false

	_cg = CG_SCENE.instantiate()
	_cg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_cg)
	_cg.visible = false

	_hud = HUD_SCENE.instantiate()
	add_child(_hud)
	_hud.connect("menu_pressed", _open_in_game_menu)

	_ig_menu = IN_GAME_MENU.instantiate()
	_ig_menu.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_ig_menu.visible = false
	add_child(_ig_menu)
	_ig_menu.connect("resume_requested",    func() -> void: _resume_from_menu())
	_ig_menu.connect("save_requested",      func(slot: int) -> void: _save_to_slot(slot))
	_ig_menu.connect("main_menu_requested", func() -> void: game_ended.emit())
	_ig_menu.connect("settings_opened",     func() -> void: _open_settings())
	_ig_menu.connect("music_opened",        func() -> void: _open_music())

	_settings_ov = SETTINGS_OV.instantiate()
	_settings_ov.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_settings_ov.visible = false
	add_child(_settings_ov)
	_settings_ov.connect("closed", func() -> void: _settings_ov.visible = false)

	_music_ov = MUSIC_OV.instantiate()
	_music_ov.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_music_ov.visible = false
	add_child(_music_ov)
	_music_ov.connect("closed", func() -> void: _music_ov.visible = false)


# ── Public API ────────────────────────────────────────────────────────────────

func start(vol: int, scene_id: String = "", slot: int = -1, start_node: int = 0) -> void:
	_vol         = vol
	_active_slot = slot
	_apply_skin(vol)
	if scene_id == "":
		var chapters := SceneDataDB.get_volume_chapters(vol)
		if chapters.is_empty():
			push_error("GameEngine: no chapters for vol %d" % vol)
			return
		scene_id = chapters[0].get("id", "")
	_load_scene(scene_id, start_node)


func load_save(save_data: Dictionary) -> void:
	_active_slot = int(save_data.get("slot", -1))
	_vol         = int(save_data.get("vol", 1))
	_flags       = save_data.get("flags",  {})
	var saved_skills = save_data.get("skills", {})
	if saved_skills is Dictionary:
		for k in (saved_skills as Dictionary):
			_skills[k] = int((saved_skills as Dictionary)[k])
	_log = save_data.get("log", [])
	_apply_skin(_vol)
	# Load scene data without auto-running, then jump to saved node index
	var target_idx: int = int(save_data.get("nodeIndex", 0))
	_load_scene(save_data.get("scene", ""), target_idx)


# ── Skin ──────────────────────────────────────────────────────────────────────

func _apply_skin(vol: int) -> void:
	_skin = SkinDB.get_for_vol(vol)
	_bg_solid.color = _skin.get("scene_bg", Color(0.05, 0.04, 0.03))
	_dlg.offset_top = -_skin.get("dlg_min_h", 210.0)
	_dlg.call("setup", _skin)
	_choices.call("setup", _skin)
	_hud.call("setup", _skin, vol, _skills, func() -> void: _open_in_game_menu())


# ── In-game overlays ──────────────────────────────────────────────────────────

func _open_in_game_menu() -> void:
	_paused = true
	_ig_menu.call("open", _active_slot)


func _resume_from_menu() -> void:
	_paused = false
	_ig_menu.visible = false


func _save_to_slot(slot: int) -> void:
	if slot < 1:
		return
	_active_slot = slot
	SaveSystem.write_save(slot, _vol, _scene_id, _node_idx, _flags, _skills, _log)


func _open_settings() -> void:
	_settings_ov.call("open")


func _open_music() -> void:
	_music_ov.call("open")


# ── Scene loading & node dispatch ─────────────────────────────────────────────

func _load_scene(scene_id: String, start_at: int = 0) -> void:
	_scene_id   = scene_id
	_node_idx   = start_at
	_scene_data = SceneDataDB.get_scene(scene_id)
	if _scene_data.is_empty():
		push_error("GameEngine: scene not found: " + scene_id)
		game_ended.emit()
		return
	_auto_load_substrate(scene_id)
	_unlock_gallery_for_scene(scene_id)
	_run_next()


const _SUBSTRATE_INDEX_PATH := "res://resources/substrates/gallery/_index.json"

func _unlock_gallery_for_scene(scene_id: String) -> void:
	# Mark any gallery items whose unlock_pattern matches this scene as seen.
	# Pattern is a glob (String.match) — e.g. "vol5_ch0_*".
	if not FileAccess.file_exists(_SUBSTRATE_INDEX_PATH):
		return
	var f := FileAccess.open(_SUBSTRATE_INDEX_PATH, FileAccess.READ)
	if f == null:
		return
	var data: Variant = JSON.parse_string(f.get_as_text())
	if typeof(data) != TYPE_DICTIONARY:
		return
	var items_v: Variant = (data as Dictionary).get("items", [])
	if typeof(items_v) != TYPE_ARRAY:
		return
	for item_v in items_v:
		if typeof(item_v) != TYPE_DICTIONARY:
			continue
		var item: Dictionary = item_v
		var pattern: String = str(item.get("unlock_pattern", ""))
		if pattern == "":
			continue
		if scene_id.match(pattern):
			SaveSystem.mark_cg_seen("substrate:" + str(item.get("id", "")))


func _auto_load_substrate(scene_id: String) -> void:
	# Two parallel conventions, both probed on every scene load:
	#
	#   compositions/scene_<id>.json   layered bg (visualizer + image +
	#                                  image_frames + border) — loaded
	#                                  into _bg_composition.
	#   scene/<id>.json                single ASCII piece — loaded into
	#                                  _substrate (legacy / lightweight).
	#
	# Either, both, or neither may exist. Both render together when
	# both are present, in z order: _bg_composition under _substrate.
	# Explicit {"t":"substrate"} / {"t":"composition"} directives can
	# override mid-scene.
	var comp_short := "scene_" + scene_id
	var comp_path  := "res://resources/substrates/compositions/" + comp_short + ".json"
	if FileAccess.file_exists(comp_path):
		_bg_composition.call("load_composition", comp_short)
	else:
		_clear_bg_composition()

	var piece_short := "scene/" + scene_id
	var piece_path  := "res://resources/substrates/" + piece_short + ".json"
	if FileAccess.file_exists(piece_path):
		_substrate.call("load_substrate", piece_short)
	else:
		_substrate.call("clear_substrate")


func _clear_bg_composition() -> void:
	# AsciiComposition rebuilds its canvas on every load; clear by
	# wiping its children to leave _bg_composition empty + transparent.
	for ch in _bg_composition.get_children():
		ch.queue_free()


func _run_next() -> void:
	var nodes: Array = _scene_data.get("nodes", [])
	if _node_idx >= nodes.size():
		_end_scene()
		return
	var node: Dictionary = nodes[_node_idx]
	_node_idx += 1
	_dispatch(node)


func _dispatch(n: Dictionary) -> void:
	match n.get("t", ""):
		"narrate":    _do_narrate(n)
		"say":        _do_say(n)
		"think":      _do_think(n)
		"choice":     _do_choice(n)
		"show":       _do_show(n); _run_next()
		"hide":       _do_hide(n); _run_next()
		"bg":         _do_bg(n);   _run_next()
		"substrate":  _do_substrate(n); _run_next()
		"composition": _do_composition(n); _run_next()
		"bgm":        _do_bgm(n);  _run_next()
		"sfx":        _do_sfx(n);  _run_next()
		"flag":       _do_flag(n); _run_next()
		"jump":       _do_jump(n)
		"end":        _end_scene()
		"interlude":  _do_interlude(n)
		"cg":         _do_cg(n)
		"videoscene": _do_videoscene(n)
		"gallery":    _run_next()
		_:
			push_warning("GameEngine: unknown node type '%s'" % n.get("t", ""))
			_run_next()


# ── Node handlers ─────────────────────────────────────────────────────────────

# Safe string getter: returns default when value is null or not a String.
func _s(n: Dictionary, key: String, default: String = "") -> String:
	var v = n.get(key)
	return v as String if v is String else default


func _do_narrate(n: Dictionary) -> void:
	var text: String = _s(n, "text")
	_log.append({"role": "narrate", "text": text})
	AudioMgr.set_sfx_pan(0.0)
	AudioMgr.duck()
	_chars.call("activate_speaker", "")
	_dlg.visible = true
	_dlg.call("show_narrate", text)
	AudioMgr.play_voice(_s(n, "voice"))
	_wait()


func _do_say(n: Dictionary) -> void:
	var char_name: String = _s(n, "char")
	var text: String      = _s(n, "text")
	var expr: String      = _s(n, "expr", "neutral")
	_log.append({"role": "say", "char": char_name, "text": text})
	_chars.call("update_expression", char_name.to_lower(), expr)
	AudioMgr.set_sfx_pan(_char_pan(char_name))
	AudioMgr.duck()
	_chars.call("activate_speaker", char_name.to_lower())
	_dlg.visible = true
	_dlg.call("show_say", char_name, text)
	AudioMgr.play_voice(_s(n, "voice"))
	_wait()


func _do_think(n: Dictionary) -> void:
	var char_name: String = _s(n, "char")
	AudioMgr.set_sfx_pan(_char_pan(char_name))
	AudioMgr.duck()
	_chars.call("activate_speaker", char_name.to_lower())
	_dlg.visible = true
	_dlg.call("show_think", char_name, _s(n, "text"))
	AudioMgr.play_voice(_s(n, "voice"))
	_wait()


func _char_pan(char_name: String) -> float:
	var pos: String = _chars.call("get_pos_for_char", char_name.to_lower())
	match pos:
		"left":  return -0.3
		"right": return  0.3
	return 0.0


func _do_choice(n: Dictionary) -> void:
	_dlg.visible = false
	AudioMgr.stop_voice()
	AudioMgr.unduck()
	var opts: Array = n.get("opts", [])
	_choices.visible = true
	_choices.call("present", n.get("prompt", ""), opts,
		func(idx: int) -> void:
			_choices.visible = false
			_dlg.visible = true
			var opt: Dictionary = opts[idx]
			if opt.has("check"):
				_resolve_check(opt["check"])
			elif opt.has("scene"):
				_load_scene(opt["scene"])
			elif opt.has("goto"):
				_node_idx = int(opt["goto"])
				_run_next()
			else:
				_run_next()
	)


func _resolve_check(check: Dictionary) -> void:
	var skill: String = check.get("skill", "")
	var diff:  int    = int(check.get("diff", 0))
	var pass_idx: int = int(check.get("pass", _node_idx))
	var fail_idx: int = int(check.get("fail", _node_idx))
	_node_idx = pass_idx if int(_skills.get(skill, 0)) >= diff else fail_idx
	_run_next()


func _do_show(n: Dictionary) -> void:
	_chars.call("show_character",
		n.get("char", "").to_lower(),
		n.get("expr", "neutral"),
		n.get("pos",  "center")
	)


func _do_hide(n: Dictionary) -> void:
	var pos: String = n.get("pos", "")
	if pos == "":
		_chars.call("hide_all")
	else:
		_chars.call("hide_at", pos)


func _do_bg(n: Dictionary) -> void:
	var src: String = _s(n, "src")
	if src == "":
		_bg.texture = null
		return
	var path := "res://" + src
	if ResourceLoader.exists(path):
		_bg.texture = ResourceLoader.load(path) as Texture2D
	else:
		_bg.texture = null


func _do_substrate(n: Dictionary) -> void:
	var src: String = _s(n, "src")
	_substrate.call("load_substrate", src)


func _do_composition(n: Dictionary) -> void:
	# Explicit override during a scene — load a background composition
	# into _bg_composition. src is the short path relative to
	# resources/substrates/compositions/ (without the .json suffix).
	var src: String = _s(n, "src")
	if src == "":
		_clear_bg_composition()
	else:
		_bg_composition.call("load_composition", src)


func _do_bgm(n: Dictionary) -> void:
	AudioMgr.play_bgm(_s(n, "src"))


func _do_sfx(n: Dictionary) -> void:
	AudioMgr.play_sfx(_s(n, "src"))


func _do_flag(n: Dictionary) -> void:
	_flags[n.get("key", "")] = n.get("val", true)


func _do_jump(n: Dictionary) -> void:
	var target: String = _s(n, "scene")
	if target != "":
		_load_scene(target)
	else:
		_end_scene()


func _do_interlude(n: Dictionary) -> void:
	_dlg.visible = false
	AudioMgr.unduck()
	_interlude.visible = true
	_interlude.call("present",
		n.get("text", ""),
		n.get("sub", ""),
		int(n.get("duration", 0)),
		func() -> void:
			_interlude.visible = false
			_dlg.visible = true
			_run_next()
	)


func _do_cg(n: Dictionary) -> void:
	var src: String = _s(n, "src")
	SaveSystem.mark_cg_seen(src)
	_dlg.visible = false
	AudioMgr.unduck()
	_cg.visible = true
	_cg.call("present",
		src,
		n.get("caption", ""),
		func() -> void:
			_cg.visible = false
			_dlg.visible = true
			_run_next()
	)


func _do_videoscene(_n: Dictionary) -> void:
	_run_next()


# ── Advance / input ───────────────────────────────────────────────────────────

func _wait() -> void:
	_waiting = true
	var ms: int = Settings.auto_advance_ms
	_auto_timer = ms / 1000.0 if ms > 0 else 0.0


func _process(delta: float) -> void:
	if _paused:
		return
	if _auto_timer > 0.0:
		_auto_timer -= delta
		if _auto_timer <= 0.0:
			_auto_timer = 0.0
			if not AudioMgr.is_voice_playing():
				_advance()
	_apply_bg_sway(delta)


# Subtle riverboat list — slow sinusoidal translate + tiny rotation on the
# bg composition. Affects scene backgrounds only; portraits and dialog
# stay fixed.
var _sway_t: float = 0.0
const SWAY_PERIOD := 5.4   # seconds per cycle
const SWAY_X_AMP  := 6.0   # logical px
const SWAY_Y_AMP  := 3.0
const SWAY_ROT    := 0.006 # radians (~0.34°)

func _apply_bg_sway(delta: float) -> void:
	if _bg_composition == null or _bg_composition.get_child_count() == 0:
		return
	_sway_t += delta
	var phase: float = _sway_t * TAU / SWAY_PERIOD
	_bg_composition.position = Vector2(sin(phase) * SWAY_X_AMP, cos(phase * 0.7) * SWAY_Y_AMP)
	_bg_composition.pivot_offset = _bg_composition.size * 0.5
	_bg_composition.rotation = sin(phase) * SWAY_ROT


func _input(event: InputEvent) -> void:
	if _paused:
		return
	if event.is_action_pressed("advance"):
		get_viewport().set_input_as_handled()
		if _interlude.visible:
			_interlude.call("try_advance")
		else:
			_advance()
	elif event.is_action_pressed("menu_back"):
		get_viewport().set_input_as_handled()
		_open_in_game_menu()


func _advance() -> void:
	if not _waiting:
		return
	if _dlg.visible and _dlg.call("is_typing"):
		_dlg.call("finish_typing")
		return
	AudioMgr.stop_voice()
	_waiting    = false
	_auto_timer = 0.0
	_run_next()


# ── End ───────────────────────────────────────────────────────────────────────

func _end_scene() -> void:
	_dlg.visible = false
	AudioMgr.stop_voice()
	AudioMgr.unduck()
	AudioMgr.stop_bgm()
	game_ended.emit()
