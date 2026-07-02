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
const UNLOCK_TOAST_SCRIPT := preload("res://scenes/game/UnlockToast.gd")
const BG_FRAME_SCRIPT     := preload("res://scenes/game/BgFrame.gd")

# Debug: overlay the resolved bg asset path on the bg image so you
# can see which file each scene's bg directive is loading while
# playing. Disable once you're done debugging.
const DEBUG_BG_OVERLAY: bool = false

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
var _composition_active: bool    = false
var _substrate:      Control     = null
var _bg:             TextureRect = null
var _bg_frame:       Control     = null
var _dlg_scrim:      ColorRect   = null

# UI nodes pin themselves to this z so composition windows with
# internal z values (1..9) can't escape and cover dialog/portraits.
const UI_Z := 100
var _chars:      Control     = null
var _dlg:        Control     = null
var _choices:    Control     = null
var _interlude:  Control     = null
var _cg:         Control     = null
var _hud:        Control     = null
var _ig_menu:    Control     = null
var _settings_ov: Control   = null
var _music_ov:   Control     = null
var _toast:      Control     = null


func _ready() -> void:
	_build_layers()


func _build_layers() -> void:
	# Bg stack uses natural tree order. UI nodes below are pinned at
	# z_index = UI_Z (100) so the composition's internal z values
	# (visualizer/image/frames/grade at z=1..9) can't escape and
	# cover the dialog box / portraits.
	_bg_solid = ColorRect.new()
	_bg_solid.color = Color(0.05, 0.04, 0.03)
	_bg_solid.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_bg_solid)

	_bg_composition = Control.new()
	_bg_composition.set_script(COMPOSITION_SCRIPT)
	_bg_composition.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_bg_composition.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_bg_composition)

	_substrate = Control.new()
	_substrate.set_script(SUBSTRATE_SCRIPT)
	_substrate.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_substrate)

	_bg = TextureRect.new()
	# Fit (letterbox/pillarbox) instead of cover so the entire source
	# image is visible. Cover-mode was cropping ~22-40px off most
	# sources, plus my prior BG_ZOOM_BASE=1.04 was zooming on top of
	# that crop — combined, large chunks of every bg sat off-screen.
	_bg.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	# Without EXPAND_IGNORE_SIZE, the TextureRect's intrinsic minimum
	# size comes from the texture itself. The vol5 bgs are 2659x1536 —
	# way larger than the 1280x720 viewport — so the rect was forced
	# to texture-native dimensions, blowing past viewport edges and
	# leaving only the center crop visible. This is what made ch3 (and
	# every other plain-bg scene) look "way zoomed in" no matter the
	# stretch_mode. IGNORE_SIZE lets anchors win → rect = viewport →
	# stretch_mode places the whole texture inside the viewport.
	_bg.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_bg)

	# Matte frame above the bg image to cover aspect bars. The live
	# _substrate sits between _bg_solid and _bg, so without this it
	# pokes through the letterbox/pillarbox gaps. Frame paints solid
	# bars over those gaps plus a thin gold rule along the bg edge.
	# Custom Control with _draw — keyed off _bg.texture aspect.
	_bg_frame = Control.new()
	_bg_frame.set_script(BG_FRAME_SCRIPT)
	_bg_frame.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_bg_frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_bg_frame)
	_bg_frame.set("bg_node", _bg)

	_chars = CHAR_SCENE.instantiate()
	_chars.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_chars.z_index = UI_Z
	add_child(_chars)

	# Dialogue scrim — gradient panel between chars and dlg so dialogue
	# text always has a high-contrast surface beneath it regardless of
	# how busy the live-ASCII bg gets.
	_dlg_scrim = ColorRect.new()
	_dlg_scrim.color = Color(0.02, 0.02, 0.04, 0.78)
	_dlg_scrim.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_dlg_scrim.offset_top = -260.0
	_dlg_scrim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_dlg_scrim.z_index = UI_Z
	add_child(_dlg_scrim)

	_dlg = DIALOGUE_SCENE.instantiate()
	_dlg.z_index = UI_Z
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
	_choices.z_index = UI_Z
	add_child(_choices)
	_choices.visible = false

	_interlude = INTERLUDE_SCENE.instantiate()
	_interlude.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_interlude.z_index = UI_Z
	add_child(_interlude)
	_interlude.visible = false

	_cg = CG_SCENE.instantiate()
	_cg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_cg.z_index = UI_Z
	add_child(_cg)
	_cg.visible = false

	_hud = HUD_SCENE.instantiate()
	_hud.z_index = UI_Z
	add_child(_hud)
	_hud.connect("menu_pressed", _open_in_game_menu)

	_ig_menu = IN_GAME_MENU.instantiate()
	_ig_menu.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_ig_menu.z_index = UI_Z
	_ig_menu.visible = false
	add_child(_ig_menu)
	_ig_menu.connect("resume_requested",    func() -> void: _resume_from_menu())
	_ig_menu.connect("save_requested",      func(slot: int) -> void: _save_to_slot(slot))
	_ig_menu.connect("main_menu_requested", func() -> void: game_ended.emit())
	_ig_menu.connect("settings_opened",     func() -> void: _open_settings())
	_ig_menu.connect("music_opened",        func() -> void: _open_music())

	_settings_ov = SETTINGS_OV.instantiate()
	_settings_ov.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_settings_ov.z_index = UI_Z + 1
	_settings_ov.visible = false
	add_child(_settings_ov)
	_settings_ov.connect("closed", func() -> void: _settings_ov.visible = false)

	_music_ov = MUSIC_OV.instantiate()
	_music_ov.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_music_ov.z_index = UI_Z + 1
	_music_ov.visible = false
	add_child(_music_ov)
	_music_ov.connect("closed", func() -> void: _music_ov.visible = false)

	_toast = Control.new()
	_toast.set_script(UNLOCK_TOAST_SCRIPT)
	_toast.z_index = UI_Z + 2
	add_child(_toast)
	AudioMgr.track_unlocked.connect(_on_track_unlocked)


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
	_load_scene(save_data.get("scene", ""), target_idx, true)


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
	# While waiting on input, _node_idx already points one past the
	# line on screen (_run_next pre-increments). Save the displayed
	# line so loading replays it instead of silently skipping it.
	var save_idx: int = _node_idx
	if _waiting and save_idx > 0:
		save_idx -= 1
	SaveSystem.write_save(slot, _vol, _scene_id, save_idx, _flags, _skills, _log)


func _open_settings() -> void:
	_settings_ov.call("open")


func _open_music() -> void:
	_music_ov.call("open")


# ── Scene loading & node dispatch ─────────────────────────────────────────────

func _load_scene(scene_id: String, start_at: int = 0, replay_state: bool = false) -> void:
	_scene_id   = scene_id
	_node_idx   = start_at
	_scene_data = SceneDataDB.get_scene(scene_id)
	if _scene_data.is_empty():
		push_error("GameEngine: scene not found: " + scene_id)
		game_ended.emit()
		return
	# Clear any portraits left over from the previous scene. Scenes
	# don't all bracket their characters with show/hide pairs, so
	# without this a character from the prior scene survives into the
	# next one (e.g. Frasier persisting from vol5_ch0_model_city into
	# vol5_ch1_magician).
	_chars.call("hide_all")
	_auto_load_substrate(scene_id)
	_unlock_gallery_for_scene(scene_id)
	_apply_chapter_music_context(scene_id)
	if replay_state and start_at > 0:
		_replay_state(start_at)
	_run_next()


# Fast-forward scene state when loading a mid-scene save: apply every
# bg / portrait / substrate / flag directive before the target node so
# the player doesn't come back to a black screen with no portraits and
# no music. Text/choice nodes are skipped — only state is replayed.
func _replay_state(upto: int) -> void:
	var nodes: Array = _scene_data.get("nodes", [])
	var last_bgm: String = ""
	for i in range(mini(upto, nodes.size())):
		var n: Dictionary = nodes[i]
		match n.get("t", ""):
			"bg":          _do_bg(n)
			"show":        _do_show(n)
			"hide":        _do_hide(n)
			"substrate":   _do_substrate(n)
			"composition": _do_composition(n)
			# flag/skill are NOT replayed — load_save already restores
			# them from the save payload; replaying would double-apply
			# skill increments.
			"bgm":
				var src: String = _s(n, "src")
				if src != "":
					last_bgm = src
	if last_bgm != "":
		AudioMgr.play_bgm(last_bgm)


# Tell AudioMgr which catalog tracks belong to the current chapter.
func _on_track_unlocked(_src: String, title: String) -> void:
	if _toast != null:
		_toast.call("show_toast", {
			"title":    "Music unlocked",
			"subtitle": title,
		})


# Used when the queue empties — it restarts from this chapter's list
# instead of going silent or globbing across volumes.
func _apply_chapter_music_context(scene_id: String) -> void:
	var ch_val = _scene_data.get("chapter", "")
	var ch_id  := scene_id + "::" + str(ch_val)
	var tracks: Array = []
	for entry: Dictionary in SceneDataDB.get_music_catalog():
		var matches := false
		if entry.get("chapter_id", "") == scene_id:
			matches = true
		var chapters_list: Array = entry.get("chapters", [])
		if scene_id in chapters_list:
			matches = true
		if matches:
			tracks.append(entry.get("src", ""))
	AudioMgr.set_chapter(ch_id, tracks)
	# Also unlock any tracks tagged to this scene so the Music
	# Player picks them up as the player progresses, even without
	# a `show` directive naming a tracked character on this page.
	if AudioMgr.has_method("unlock_tracks_for_chapter"):
		AudioMgr.unlock_tracks_for_chapter(ch_id)


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
	# Two parallel conventions, probed in order:
	#
	#   compositions/scene_<id>.json   layered bg (visualizer + image +
	#                                  image_frames + border). If this
	#                                  exists it supersedes the piece —
	#                                  authoring both for the same scene
	#                                  doesn't make sense (substrate
	#                                  would just cover the composition
	#                                  in the z-stack).
	#
	#   scene/<id>.json                single ASCII piece, loaded into
	#                                  _substrate. The legacy /
	#                                  lightweight path; used for scenes
	#                                  without a composition.
	#
	# Explicit {"t":"substrate"} / {"t":"composition"} directives can
	# still swap either mid-scene.
	var comp_short := "scene_" + scene_id
	var comp_path  := "res://resources/substrates/compositions/" + comp_short + ".json"
	var has_comp: bool = FileAccess.file_exists(comp_path)

	if has_comp:
		_bg_composition.call("load_composition", comp_short)
		_composition_active = true
		_substrate.call("clear_substrate")
		return

	_clear_bg_composition()
	_composition_active = false
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
		"skill":      _do_skill(n); _run_next()
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
	_set_vn_focus(false)
	_wait()


func _do_say(n: Dictionary) -> void:
	var char_name: String = _s(n, "char")
	# `char` is the portrait/asset id; `name` (when present) is the
	# display name for the speaker label — e.g. char "tem", name "Tem".
	var display: String   = _s(n, "name", char_name)
	var text: String      = _s(n, "text")
	var expr: String      = _s(n, "expr", "neutral")
	_log.append({"role": "say", "char": display, "text": text})
	_ensure_portrait(char_name, expr)
	_chars.call("update_expression", char_name.to_lower(), expr)
	AudioMgr.set_sfx_pan(_char_pan(char_name))
	AudioMgr.duck()
	_chars.call("activate_speaker", char_name.to_lower())
	_dlg.visible = true
	_dlg.call("show_say", display, text)
	AudioMgr.play_voice(_s(n, "voice"))
	_set_vn_focus(true)
	_wait()


func _do_think(n: Dictionary) -> void:
	var char_name: String = _s(n, "char")
	var display: String   = _s(n, "name", char_name)
	var text: String      = _s(n, "text")
	var expr: String      = _s(n, "expr", "neutral")
	_log.append({"role": "think", "char": display, "text": text})
	_ensure_portrait(char_name, expr)
	AudioMgr.set_sfx_pan(_char_pan(char_name))
	AudioMgr.duck()
	_chars.call("activate_speaker", char_name.to_lower())
	_dlg.visible = true
	_dlg.call("show_think", display, text)
	AudioMgr.play_voice(_s(n, "voice"))
	_set_vn_focus(true)
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
				_resolve_check(opt)
			elif opt.has("scene"):
				_load_scene(opt["scene"])
			elif opt.has("goto"):
				_node_idx = int(opt["goto"])
				_run_next()
			else:
				_run_next()
	)


# Scene data puts pass/fail as siblings of `check` on the option
# (e.g. {"check": {"skill": "logic", "diff": 9}, "pass": 11, "fail": 8});
# older/hand-authored data may nest them inside `check`. Accept both.
func _resolve_check(opt: Dictionary) -> void:
	var check: Dictionary = opt.get("check", {})
	var skill: String = check.get("skill", "")
	var diff:  int    = int(check.get("diff", 0))
	var pass_idx: int = int(opt.get("pass", check.get("pass", _node_idx)))
	var fail_idx: int = int(opt.get("fail", check.get("fail", _node_idx)))
	_node_idx = pass_idx if int(_skills.get(skill, 0)) >= diff else fail_idx
	_run_next()


func _do_show(n: Dictionary) -> void:
	var char_name: String = n.get("char", "")
	_chars.call("show_character",
		char_name.to_lower(),
		n.get("expr", "neutral"),
		n.get("pos",  "center"),
		n.get("facing", "")
	)
	# Use the CharLayer slug fn so "The Demon"/"oil exec"/etc collapse
	# the same way they do for portrait lookups + accents.
	var char_key: String = _chars.call("char_key", char_name)
	AudioMgr.unlock_tracks_for_character(char_key)


func _do_hide(n: Dictionary) -> void:
	var pos: String = n.get("pos", "")
	if pos == "":
		_chars.call("hide_all")
	else:
		_chars.call("hide_at", pos)


# Persistent label in the top-right corner of the viewport showing
# the bg asset path the engine is currently loading. Created lazily
# on first call, then just updated with new text.
var _bg_debug_label: Label = null

func _set_bg_debug_label(src: String) -> void:
	if _bg_debug_label == null:
		_bg_debug_label = Label.new()
		_bg_debug_label.add_theme_font_size_override("font_size", 10)
		_bg_debug_label.add_theme_color_override("font_color", Color(0.95, 0.85, 0.55))
		_bg_debug_label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
		_bg_debug_label.add_theme_constant_override("outline_size", 3)
		_bg_debug_label.set_anchors_preset(Control.PRESET_TOP_RIGHT)
		_bg_debug_label.offset_left  = -560.0
		_bg_debug_label.offset_top   = 6.0
		_bg_debug_label.offset_right = -8.0
		_bg_debug_label.offset_bottom = 22.0
		_bg_debug_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		_bg_debug_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_bg_debug_label.z_index = UI_Z + 3
		add_child(_bg_debug_label)
	_bg_debug_label.text = "bg: " + src


const BACKGROUND_3D_SCENE := preload("res://scenes/vn/Background3D.tscn")
var _bg_3d_node: SubViewportContainer = null


func _do_bg(n: Dictionary) -> void:
	var src: String = _s(n, "src")
	if src == "":
		_bg.texture = null
		_clear_bg_3d()
		print("[GameEngine] BG  (cleared)")
		return
	# 3D-scene background — src looks like "3d:<preset_id>" e.g.
	# "3d:diner_interior" or "3d:riverfront_exterior". The preset
	# IDs are defined in scripts/vn/Background3D.gd CAMERA_PRESETS.
	# A SubViewport renders the location with an establishing-shot
	# camera; the resulting ViewportTexture replaces the static PNG.
	if src.begins_with("3d:"):
		var preset_id: String = src.substr(3)
		_apply_bg_3d(preset_id)
		print("[GameEngine] BG  3d:%s  via SubViewport" % preset_id)
		return
	# Static / PNG paths beyond this point — clear any prior 3D
	# viewport so we don't keep rendering a heavy world off-screen.
	_clear_bg_3d()
	# Composition supersedes bg PNG. When a scene_<id>.json composition
	# is loaded, it already contains the bg image as a window (alongside
	# ASCII flicker, dust motes, color grade) and the redundant bg PNG
	# plus BgFrame matte completely cover those layers — collapsing the
	# composed look back to a plain PNG. Skip the bg paint so the
	# composition stays visible. Scenes without a composition still
	# render via _bg as before.
	if _composition_active:
		_bg.texture = null
		if _bg_frame != null:
			_bg_frame.queue_redraw()
		print("[GameEngine] BG  %s  → suppressed (composition active)" % src)
		return
	var path := "res://" + src
	var via: String = "missing"
	if ResourceLoader.exists(path):
		_bg.texture = ResourceLoader.load(path) as Texture2D
		via = "ResourceLoader"
	else:
		# Pre-check disk presence before Image.load_from_file so a
		# missing PNG (e.g. vol6_kwik_stop.jpg on a fresh checkout
		# without the bg asset) doesn't error-spam the debugger.
		var disk_path := ProjectSettings.globalize_path(path)
		if FileAccess.file_exists(path) or FileAccess.file_exists(disk_path):
			var img := Image.load_from_file(disk_path)
			_bg.texture = ImageTexture.create_from_image(img) if img else null
			via = "Image.load_from_file" if img else "FAILED — image load returned null"
		else:
			_bg.texture = null
			via = "skipped — file not on disk"
	if _bg.texture != null:
		var sz := _bg.texture.get_size()
		print("[GameEngine] BG  %s  via %s  [%dx%d]" %
			[src, via, int(sz.x), int(sz.y)])
	else:
		print("[GameEngine] BG  %s  via %s  ← scene references this but it doesn't exist" %
			[src, via])
	# Randomize the pan phase per bg so different scenes don't all
	# reveal the same edge first — feels less mechanical.
	_bg_pan_phase = randf() * BG_PAN_PERIOD
	if _bg_frame != null:
		_bg_frame.queue_redraw()
	# Debug overlay — small label in the top-right corner of the
	# bg showing the asset path. Toggle via DEBUG_BG_OVERLAY below.
	if DEBUG_BG_OVERLAY:
		_set_bg_debug_label(src)


# ── 3D-scene background pipeline ─────────────────────────────────
func _apply_bg_3d(preset_id: String) -> void:
	if _bg_3d_node == null or not is_instance_valid(_bg_3d_node):
		_bg_3d_node = BACKGROUND_3D_SCENE.instantiate()
		# Insert ABOVE the bg TextureRect but BELOW the dust-motes /
		# composition overlay layers. add_sibling drops it next to
		# _bg in the tree; layer-z ordering is by child order so it
		# paints after _bg, hiding the PNG behind it.
		_bg.add_sibling(_bg_3d_node)
		_bg_3d_node.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		_bg_3d_node.mouse_filter = Control.MOUSE_FILTER_IGNORE
	# Pre-check the locale GLB existence BEFORE clearing the PNG bg.
	# Locale .glb files are build artifacts (not committed) so a
	# fresh checkout that hasn't run the Blender builders yet would
	# end up with a black bg if we cleared and then load failed.
	# Keep the PNG visible until we know the 3D bg can render.
	var presets: Dictionary = _bg_3d_node.CAMERA_PRESETS
	var spec: Dictionary = presets.get(preset_id, {})
	var req_glb: String = spec.get("requires_glb", "")
	if req_glb != "" and not FileAccess.file_exists(req_glb):
		push_warning("[GameEngine] 3D bg '%s' needs %s — build it with `cd godot/tools/blender && ./run_cathedral.sh build_<name>.py`. Keeping PNG bg." % [preset_id, req_glb])
		_bg_3d_node.visible = false
		return
	# Clear the PNG bg so we're definitely showing the 3D viewport
	_bg.texture = null
	_bg_3d_node.visible = true
	# Force _bg_3d_node to render ON TOP of everything in the
	# parent's children list (later siblings = later draw order
	# for Controls). The substrate, composition, _bg TextureRect
	# are all siblings; without this, anything created after our
	# initial add_sibling() can end up painting over the 3D bg.
	var parent := _bg_3d_node.get_parent()
	if parent != null:
		parent.move_child(_bg_3d_node, parent.get_child_count() - 1)
	# Hide the auto-loaded substrate + composition. The composition's
	# "image" windows (e.g. vol5_dambrosios_exterior.png at z=3 in
	# scene_vol5_ch0_booth6) would otherwise paint a full-screen 2D
	# PNG ON TOP of the 3D viewport — exactly the bug we saw where
	# the 3D bg was visibly swaying behind a static 2D image.
	if _bg_composition != null:
		_bg_composition.visible = false
	if _substrate != null:
		_substrate.visible = false
	# CG layer (cutscene full-screen graphic) — usually hidden, but
	# ensure it's down so nothing left over from a previous scene
	# bleeds through.
	if _cg != null:
		_cg.visible = false
	print("[GameEngine]   ↳ hid composition+substrate+cg, moved 3d viewport to front sibling")
	_bg_3d_node.call_deferred("load_location", preset_id)


func _clear_bg_3d() -> void:
	if _bg_3d_node != null and is_instance_valid(_bg_3d_node):
		_bg_3d_node.visible = false
	# Restore the 2D substrate + composition layers for any next
	# non-3D bg directive (or for the auto-loaded substrate on the
	# next scene that doesn't use a 3D bg).
	if _bg_composition != null:
		_bg_composition.visible = true
	if _substrate != null:
		_substrate.visible = true


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
		_composition_active = false
	else:
		_bg_composition.call("load_composition", src)
		_composition_active = true
		# Stale bg PNG would now sit on top of the new composition and
		# cover it; clear so the composition is what shows.
		_bg.texture = null
		if _bg_frame != null:
			_bg_frame.queue_redraw()


func _do_bgm(n: Dictionary) -> void:
	# By default, scene-data `bgm` directives ENQUEUE the track —
	# the queue picks it up when the current track finishes (or
	# immediately if nothing is playing). That keeps transitions
	# soft: a player walking from one scene into another doesn't
	# hear an instant cut. Set `"hard": true` on the directive for
	# moments that NEED a hard swap (win/loss stings, dramatic
	# reveals).
	var src: String = _s(n, "src")
	if src == "":
		return
	if bool(n.get("hard", false)):
		AudioMgr.play_bgm(src)
	else:
		AudioMgr.enqueue_music(src)


func _do_sfx(n: Dictionary) -> void:
	AudioMgr.play_sfx(_s(n, "src"))


func _do_flag(n: Dictionary) -> void:
	_flags[n.get("key", "")] = n.get("val", true)


# {"t": "skill", "key": "logic", "val": 1}          → logic += 1
# {"t": "skill", "key": "logic", "val": 3, "set": true} → logic = 3
# Without this node type skills stay at 0 forever and every choice
# check fails, so the whole stat system was decorative.
func _do_skill(n: Dictionary) -> void:
	var key: String = str(n.get("key", ""))
	if key == "":
		return
	var val: int = int(n.get("val", 1))
	if bool(n.get("set", false)):
		_skills[key] = val
	else:
		_skills[key] = int(_skills.get(key, 0)) + val
	if _hud != null and _hud.has_method("update_skills"):
		_hud.update_skills(_skills)


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
	_apply_bg_motion(delta)


# Background idle motion. Bg now displays in fit-mode (whole image
# visible with thin aspect bars), so the previous Ken-Burns pan +
# 1.04 base zoom — which assumed cover-mode with crop margin to pan
# across — would just slide the image past the visible area
# exposing the solid color underneath. Keeping:
#  • Riverboat sway:  small wobble + micro-rotation for life.
#  • Zoom breath:     very subtle ±0.4% breathing so the frame
#                     doesn't feel locked. Stays well within where
#                     letterbox bars would notice.
# No translation pan — that pushed image past its own edges.
var _sway_t:       float = 0.0
var _bg_pan_t:     float = 0.0
var _bg_pan_phase: float = 0.0
const SWAY_PERIOD   := 5.4
const SWAY_X_AMP    := 4.0
const SWAY_Y_AMP    := 2.0
const SWAY_ROT      := 0.004
const BG_PAN_PERIOD := 25.0
const BG_ZOOM_BASE  := 1.0
const BG_ZOOM_AMP   := 0.004

func _apply_bg_motion(delta: float) -> void:
	_sway_t   += delta
	_bg_pan_t += delta
	var t: float = (_bg_pan_t + _bg_pan_phase) * TAU / BG_PAN_PERIOD
	var pan_scale := BG_ZOOM_BASE + sin(t * 0.4) * BG_ZOOM_AMP

	var sway_phase: float = _sway_t * TAU / SWAY_PERIOD
	var sway_pos := Vector2(sin(sway_phase) * SWAY_X_AMP, cos(sway_phase * 0.7) * SWAY_Y_AMP)
	var sway_rot := sin(sway_phase) * SWAY_ROT

	var total_scale := Vector2(pan_scale, pan_scale)

	if _bg != null and _bg.texture != null:
		_bg.pivot_offset = _bg.size * 0.5
		_bg.position     = sway_pos
		_bg.scale        = total_scale
		_bg.rotation     = sway_rot

	if _bg_composition != null and _bg_composition.get_child_count() > 0:
		_bg_composition.pivot_offset = _bg_composition.size * 0.5
		_bg_composition.position     = sway_pos
		_bg_composition.scale        = total_scale
		_bg_composition.rotation     = sway_rot


# True iff the VnPortraitDebugOverlay is currently on-screen.
# Used by _input to skip VN advance while the user is interacting
# with the debug panel. Walks the CharLayer's children since the
# overlay attaches itself there in CharLayer._ready.
func _vn_debug_overlay_visible() -> bool:
	if _chars == null or not is_instance_valid(_chars):
		return false
	var overlay: Node = _chars.get_node_or_null("VnPortraitDebugOverlay")
	if overlay == null or not is_instance_valid(overlay):
		return false
	return bool(overlay.visible)


func _input(event: InputEvent) -> void:
	if _paused:
		# Esc closes the pause menu again (only when no sub-overlay is
		# open on top of it — those own their close behavior).
		if event.is_action_pressed("menu_back") \
				and _ig_menu.visible \
				and not _settings_ov.visible and not _music_ov.visible:
			get_viewport().set_input_as_handled()
			_resume_from_menu()
		return
	# Don't process advance/menu_back while the choice menu is up.
	# Otherwise the same mouse-click that picks an option also fires
	# advance: ChoiceMenu's button consumes the click first, runs the
	# callback (which sets _waiting=true on the next dialogue node),
	# then our _input handler runs _advance() on the same event,
	# advancing one node past the choice and skipping content.
	if _choices.visible:
		return
	# Debug-overlay gate. _input runs BEFORE the GUI chain — without
	# this gate, clicking a debug-panel button would (a) hit the
	# button AND (b) also fire _advance() here, and set_input_as_handled
	# would stop the Button from receiving the press. Only skip when
	# a debug overlay is ACTUALLY visible (Shift+F12 opt-in), so
	# normal VN scenes — where the mouse is visible by default but
	# no debug panel is up — still click-to-advance as expected.
	if event is InputEventMouseButton:
		if _vn_debug_overlay_visible():
			return
	if event.is_action_pressed("advance"):
		if _choices != null and _choices.visible:
			return
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
		# Re-arm the auto-advance timer: when auto mode fired while the
		# line was still typing, leaving the timer at 0 stalled auto
		# mode on that line forever.
		var ms: int = Settings.auto_advance_ms
		if ms > 0:
			_auto_timer = ms / 1000.0
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
	var next := SceneDataDB.get_next_scene_id(_scene_id)
	if next == "":
		# Only hard-stop music when the run actually ends. Chained
		# scenes keep their queue/crossfade continuity — stopping here
		# hard-cut the BGM at every chapter boundary.
		AudioMgr.stop_bgm()
	if next != "":
		var next_scene := SceneDataDB.get_scene(next)
		var next_vol: int = int(next_scene.get("vol", _vol))
		if next_vol != _vol:
			_vol = next_vol
			_apply_skin(_vol)
		_load_scene(next)
	else:
		_set_vn_focus(false)
		game_ended.emit()


# ── Auto-portrait fallback ──────────────────────────────────────
# Many scenes (100+ across the project) have characters that
# speak via say / think but were never explicitly `show`n. Under
# the old logic those characters were invisible — activate_speaker
# only modifies existing portraits. This helper catches the
# pattern: if the character isn't currently shown, auto-spawn a
# portrait at the first empty slot (center → right → left). The
# authorial intent for POV characters is "visible + idle while
# they witness," so default expression is "neutral" — callers
# pass through whatever expr the say/think directive carries.
func _ensure_portrait(char_name: String, expr: String) -> void:
	if char_name == null or char_name.strip_edges() == "":
		return
	if _chars == null or not is_instance_valid(_chars):
		return
	if _chars.has_method("has_character") and _chars.has_character(char_name):
		return
	var pos: String = "center"
	if _chars.has_method("first_empty_slot"):
		pos = _chars.first_empty_slot()
	if _chars.has_method("show_character"):
		_chars.show_character(char_name, expr, pos)


# ── VN focus mode hook ──────────────────────────────────────────
# When a character is speaking (say / think), the locale's
# MoodCycler softens noise-y shader params (scanline, aberration,
# ASCII strength, oldfilm grain + judder) so dialogue text reads.
# narrate (no character) and scene end release the focus.
#
# Silently no-ops if the scene doesn't have a PostProcess /
# MoodCycler (e.g. a pure VN-only scene with no postprocess stack).
func _set_vn_focus(active: bool) -> void:
	var scene := get_tree().current_scene
	if scene == null:
		return
	var post := scene.get_node_or_null("PostProcess")
	if post != null and post.has_method("vn_focus_dialogue"):
		post.vn_focus_dialogue(active)
