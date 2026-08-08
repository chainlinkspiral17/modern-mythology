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
const VN_DIRECTOR_SCRIPT := preload("res://scripts/vn/VnDirector.gd")
const UNLOCK_TOAST_SCRIPT := preload("res://scenes/game/UnlockToast.gd")
const BG_FRAME_SCRIPT     := preload("res://scenes/game/BgFrame.gd")

# Debug: overlay the resolved bg asset path on the bg image so you
# can see which file each scene's bg directive is loading while
# playing. Disable once you're done debugging.
const DEBUG_BG_OVERLAY: bool = false

const CHAPTER_CARD_SCRIPT := preload("res://scenes/game/ChapterCard.gd")

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

# HUD chapter echo memory — untitled scenes inherit the last
# non-empty title seen within the same (vol, chapter) instead of
# degrading the whisper to a bare chapter number.
var _last_chapter_title: String = ""
var _last_title_ch_key:  String = ""

# ── Scene transitions (2026-07 presentation wave) ────────────────
# A fade veil above all UI (z 140) carries scene→scene cuts; a
# ChapterCard (z 150) presents the scene JSON's `title` at every
# (vol, chapter) boundary. `_transition_lock` gates _input so a
# click during a fade can't advance the story underneath.
var _veil: ColorRect = null
var _chapter_card: Control = null
var _transition_lock: bool = false
# ── reading furniture (2026-07 detail pass) ──
var _backlog_overlay: Control = null
# AUTO mode (A key) · hands-free reading: the page turns itself a
# beat after the typewriter rests, scaled to line length. Distinct
# from _auto_timer, which serves voiced-node sync.
var _auto_mode: bool = false
var _auto_read_t: float = 0.0
var _auto_chip: Label = null
# idle cursor · the pointer fades after a few still seconds so it
# never sits in a held frame
var _cursor_idle_t: float = 0.0
var _photo_on: bool = false
var _photo_bars: Array = []          # two ColorRects, built lazily
var _photo_restore: Dictionary = {}  # node path -> was-visible

# The producer keeps the departments on one clock across transitions:
# story dispatch waits for the curtain, audio dips/stops/returns in
# sync with the veil, and a settle beat lands the establishing shot
# before the first line. See scripts/vn/VnProducer.gd.
const VN_PRODUCER_SCRIPT := preload("res://scripts/vn/VnProducer.gd")
var _producer: Node = null

var _bg_solid:       ColorRect   = null
var _bg_composition: Control     = null
var _composition_active: bool    = false
var _substrate:      Control     = null
var _bg:             TextureRect = null
var _bg_frame:       Control     = null
var _dlg_scrim:      Control     = null

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

# ── Scene direction (lore/_VN_DIRECTION_PLAYBOOK.md) ─────────────
# [shot:...] / [panel:...] directives lead narrate/say/think text;
# they're stripped before display and dispatched to the director.
var _director:   Node        = null
var _direct_rx:  RegEx       = RegEx.create_from_string("^\\[(shot|panel|stage|mood|beat):([^\\]\\r\\n]+)\\]\\s*")


func _ready() -> void:
	_build_layers()
	_producer = VN_PRODUCER_SCRIPT.new()
	add_child(_producer)


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
	_bg.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
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
	_bg_frame.visible = false   # modern-VN: full-bleed bg, no matte bars

	# Scene director — owns shot cuts, letterbox bars and info
	# panels. Bars/panels are Controls in THIS tree (z 95/101), so
	# the F4 CanvasLayer sweep can't hide the picture itself.
	_director = VN_DIRECTOR_SCRIPT.new()
	add_child(_director)
	_director.call("setup", self)

	_chars = CHAR_SCENE.instantiate()
	_chars.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	# Portrait layer sits ABOVE the background but strictly BELOW the
	# dialogue/UI band (UI_Z=100). Must be < UI_Z so activate_speaker's
	# per-portrait z_index bump (active speaker = +1, relative to this
	# base) can never climb over the dialogue text. Still well above the
	# bg composition's internal z (1..9), so those can't escape either.
	_chars.z_index = UI_Z - 40
	add_child(_chars)

	# Dialogue scrim — gradient panel between chars and dlg so dialogue
	# text always has a high-contrast surface beneath it regardless of
	# how busy the live-ASCII bg gets.
	# Bottom-fading gradient scrim (modern-VN clean look): transparent
	# at the top, dark at the bottom — text contrast with no hard box
	# edge. TextureRect over a GradientTexture2D.
	# "Text on top, not on a scrim" (2026-07-12) held the box fully
	# transparent. 2026-07-22 reading-surface draft (user-approved
	# taste pass): a GENTLE gradient returns — still transparent at the
	# top (no box edge, the chrome-less spirit holds), rising to a soft
	# dark at the very bottom so the type sits on a composed surface
	# instead of raw scene. The per-glyph outline still carries
	# legibility; this is atmosphere, not a slab. Revert = bottom
	# alpha back to 0.0 (one number).
	var _scrim_grad := Gradient.new()
	_scrim_grad.set_color(0, Color(0.02, 0.02, 0.04, 0.0))
	_scrim_grad.set_color(1, Color(0.01, 0.01, 0.03, 0.34))
	var _scrim_tex := GradientTexture2D.new()
	_scrim_tex.gradient = _scrim_grad
	_scrim_tex.fill_from = Vector2(0, 0)
	_scrim_tex.fill_to   = Vector2(0, 1)
	_scrim_tex.width  = 8
	_scrim_tex.height = 256
	var _scrim_rect := TextureRect.new()
	_scrim_rect.texture = _scrim_tex
	_scrim_rect.stretch_mode = TextureRect.STRETCH_SCALE
	_scrim_rect.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_scrim_rect.offset_top = -300.0
	_scrim_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_scrim_rect.z_index = UI_Z
	add_child(_scrim_rect)
	_dlg_scrim = _scrim_rect

	_dlg = DIALOGUE_SCENE.instantiate()
	_dlg.z_index = UI_Z
	add_child(_dlg)
	_dlg.visible = false
	# Direct cross-references — DialogueBox needs CharLayer for speaker
	# accents/slots, CharLayer needs DialogueBox for the talk flap.
	# Injecting here kills the per-line find_child tree walks; each
	# component keeps its find_child as a null-member fallback.
	if _dlg.has_method("set_char_layer"):
		_dlg.call("set_char_layer", _chars)
	if _chars.has_method("set_dialogue"):
		_chars.call("set_dialogue", _dlg)
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
	# Above every scene element INCLUDING portrait chrome — modal
	# menus must never have character art floating through them.
	_ig_menu.z_index = UI_Z + 20
	_ig_menu.visible = false
	add_child(_ig_menu)
	_ig_menu.connect("resume_requested",    func() -> void: _resume_from_menu())
	_ig_menu.connect("save_requested",      func(slot: int) -> void: _save_to_slot(slot))
	_ig_menu.connect("main_menu_requested", func() -> void: _exit_to_main_menu())
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
	# Open on black; the first scene arrives through its chapter card
	# (fresh sessions always deserve the plate) or a fade-in.
	_set_veil(1.0)
	_load_scene(scene_id, start_node)
	var sc := SceneDataDB.get_scene(scene_id)
	if start_node == 0 and String(sc.get("title", "")).strip_edges() != "":
		_present_chapter_card(sc)
	else:
		_fade_veil_out(0.6)


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
	# Mid-scene resume: no chapter card, just a quiet fade-in.
	_set_veil(1.0)
	_load_scene(save_data.get("scene", ""), target_idx)
	_fade_veil_out(0.5)


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
	# _run_next bumps _node_idx BEFORE dispatch, so while a line is
	# displayed (_waiting) or a choice is up, _node_idx already points
	# one PAST the node the reader is looking at. Saving that raw value
	# made resume skip the current line — or skip a pending choice
	# entirely when saved from the menu. Save the displayed node's own
	# index; on resume _load_scene re-dispatches exactly that node
	# (safe: the fast-forward pass owns all earlier side effects).
	var idx: int = _node_idx
	if _waiting or (_choices != null and _choices.visible):
		idx = maxi(0, _node_idx - 1)
	SaveSystem.write_save(slot, _vol, _scene_id, idx, _flags, _skills, _log)


func _exit_to_main_menu() -> void:
	# Leaving for the main menu never silently drops progress: write an
	# autosave first — into the active slot when one exists, else the
	# most recently written occupied slot, else slot 1.
	var slot: int = _active_slot
	if slot < 1:
		var best_ts: float = -1.0
		for sd_v in SaveSystem.list_saves():
			var sd: Dictionary = sd_v
			if bool(sd.get("empty", false)):
				continue
			var ts: float = float(sd.get("ts", 0.0))
			if ts > best_ts:
				best_ts = ts
				slot = int(sd.get("slot", -1))
	if slot < 1:
		slot = 1
	_save_to_slot(slot)
	game_ended.emit()


func _open_settings() -> void:
	_settings_ov.call("open")


func _open_music() -> void:
	_music_ov.call("open")


# ── Scene loading & node dispatch ─────────────────────────────────────────────

func _load_scene(scene_id: String, start_at: int = 0) -> void:
	_scene_id   = scene_id
	# Coverage rotation: the director assigns each chapter its
	# establish angle from this key (see VnDirector._rotation_marker).
	if _director != null:
		_director.set("scene_key", scene_id)
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
	# Persistent chapter echo in the HUD (the plate's quiet twin).
	if _hud != null and _hud.has_method("set_chapter"):
		var ch := str(_scene_data.get("chapter", "")).strip_edges()
		var ttl := String(_scene_data.get("title", "")).strip_edges()
		var ch_key := "%d::%s" % [_vol, ch]
		if ttl != "":
			_last_chapter_title = ttl
			_last_title_ch_key  = ch_key
		elif _last_title_ch_key == ch_key and _last_chapter_title != "":
			# Untitled scene mid-chapter — keep whispering the chapter's
			# last real title instead of degrading to a bare number.
			ttl = _last_chapter_title
		var parts: PackedStringArray = PackedStringArray()
		if ch != "":
			parts.append("CH %s" % ch.to_upper())
		if ttl != "":
			parts.append(ttl)
		_hud.call("set_chapter", ("·  " + "  ·  ".join(parts)) if parts.size() > 0 else "")
	# Resume fast-forward: a mid-scene start (save resume) must not
	# open on a bare stage. Replay the silent side effects of every
	# node before the target — bg / bgm / stage / flags — and re-assert
	# the last mood/shot direction, so the resumed line lands in the
	# world the reader left.
	if start_at > 0:
		_fast_forward_to(start_at)
	# Dispatch through the producer's curtain gate: across a real
	# transition (veil/chapter card up) the first node waits for the
	# reveal + settle beat; mid-story jumps pass straight through.
	if _producer != null:
		_producer.call("when_curtain_up", Callable(self, "_run_next"))
	else:
		_run_next()


# ── Resume fast-forward ──────────────────────────────────────────
# Walk nodes [0..target) applying only silent state, mirroring
# _dispatch's node-type vocabulary: flags and character show/hide in
# order (flags gate later nodes via when_flag / when_not_flag), the
# LAST bg / substrate / composition / bgm each (dispatched in their
# original relative order so composition-suppresses-bg semantics
# hold), and the LAST [mood:...] / [shot:...] directive prefix seen
# in narrate/say/think text. Everything display- or time-shaped —
# text, waits, sfx, choices, interlude, cg, jump, end, videoscene,
# gallery — is skipped. Saved flags stay authoritative: values loaded
# from the save are re-asserted after the replay so a replayed early
# `flag` node can't undo what a later choice set.
func _fast_forward_to(target: int) -> void:
	var nodes: Array = _scene_data.get("nodes", [])
	var authoritative: Dictionary = _flags.duplicate()
	var last_env: Dictionary = {}   # node type -> last node index
	var last_mood: String = ""
	var last_shot: String = ""
	var limit: int = mini(target, nodes.size())
	for i in limit:
		var nv: Variant = nodes[i]
		if not (nv is Dictionary):
			continue
		var n: Dictionary = nv
		# Same conditional gate as _dispatch.
		if n.has("when_flag"):
			var wv: Variant = _flags.get(String(n.get("when_flag")), false)
			var want: bool
			if n.has("is"):
				want = str(wv) == str(n.get("is"))
			elif wv is String:
				want = String(wv) != ""
			else:
				want = bool(wv)
			if not want:
				continue
		if n.has("when_not_flag") and _flags.get(String(n.get("when_not_flag")), false):
			continue
		match n.get("t", ""):
			"show": _do_show(n)
			"hide": _do_hide(n)
			"flag": _do_flag(n)
			"bg", "substrate", "composition", "bgm":
				last_env[String(n.get("t", ""))] = i
			"narrate", "say", "think":
				# Remember only the last mood/shot direction seen.
				var text: String = _s(n, "text")
				if text.begins_with("["):
					while true:
						var m := _direct_rx.search(text)
						if m == null:
							break
						var arg: String = m.get_string(2).strip_edges()
						match m.get_string(1):
							"mood": last_mood = arg
							"shot": last_shot = arg
						text = text.substr(m.get_end(0))
			_:
				pass
	# Environment nodes in original relative order.
	var env_indices: Array = last_env.values()
	env_indices.sort()
	for idx_v in env_indices:
		var n2: Dictionary = nodes[int(idx_v)]
		match n2.get("t", ""):
			"bg":          _do_bg(n2)
			"substrate":   _do_substrate(n2)
			"composition": _do_composition(n2)
			"bgm":         _do_bgm(n2)
	if _director != null:
		if last_shot != "":
			_director.call("apply_shot", last_shot)
		if last_mood != "":
			_director.call("apply_mood", last_mood)
	# Save-file flags win over replayed flag nodes.
	_flags.merge(authoritative, true)


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
	# Conditional nodes · cross-chapter callbacks.  A node carrying
	# when_flag only plays if that flag is set (and, when "is" is
	# present, equals that value); when_not_flag inverts.  Any node
	# type can carry these — a skipped node is silent and free.
	if n.has("when_flag"):
		var wv: Variant = _flags.get(String(n.get("when_flag")), false)
		var want: bool
		if n.has("is"):
			want = str(wv) == str(n.get("is"))
		elif wv is String:
			want = String(wv) != ""
		else:
			want = bool(wv)
		if not want:
			_run_next()
			return
	if n.has("when_not_flag") and _flags.get(String(n.get("when_not_flag")), false):
		_run_next()
		return
	match n.get("t", ""):
		"narrate":    _do_narrate(_directed(n))
		"say":        _do_say(_directed(n))
		"think":      _do_think(_directed(n))
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


# ── Direction directives ─────────────────────────────────────────
# Strip leading [shot:...] / [panel:...] directives off a text
# node, dispatching each to the director, and return the node with
# the cleaned text. Zero directives → the original node untouched
# (the common path costs one regex miss). The scene-data dict is
# never mutated — SceneDataDB caches it, and a replay must see the
# directives again.
func _directed(n: Dictionary) -> Dictionary:
	var text: String = _s(n, "text")
	if text == "" or not text.begins_with("["):
		return n
	var stripped := text
	while true:
		var m := _direct_rx.search(stripped)
		if m == null:
			break
		var arg := m.get_string(2).strip_edges()
		if _director != null:
			match m.get_string(1):
				"shot":  _director.call("apply_shot", arg)
				"stage": _director.call("apply_stage", arg)
				"mood":  _director.call("apply_mood", arg)
				"beat":  _director.call("apply_beat", arg)
				_:
					_director.call("apply_panel", arg)
					# Paper-slide moment sound: a page turn on open, a
					# soft close on dismiss. Presets ship in SFXBank.
					SFXBank.play("menu_close" if arg == "off" else "page_turn", 0.55)
					if arg != "off":
						SaveSystem.mark_cg_seen("panel:" + arg)
		stripped = stripped.substr(m.get_end(0))
	if stripped == text:
		return n
	var n2 := n.duplicate()
	n2["text"] = stripped
	return n2


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
	var text: String      = _s(n, "text")
	var expr: String      = _s(n, "expr", "neutral")
	_log.append({"role": "say", "char": char_name, "text": text})
	_ensure_portrait(char_name, expr)
	_chars.call("update_expression", char_name.to_lower(), expr)
	AudioMgr.set_sfx_pan(_char_pan(char_name))
	AudioMgr.duck()
	_chars.call("activate_speaker", char_name.to_lower())
	_dlg.visible = true
	_dlg.call("show_say", char_name, text)
	AudioMgr.play_voice(_s(n, "voice"))
	_set_vn_focus(true)
	_wait()


func _do_think(n: Dictionary) -> void:
	var char_name: String = _s(n, "char")
	var expr: String      = _s(n, "expr", "neutral")
	_ensure_portrait(char_name, expr)
	AudioMgr.set_sfx_pan(_char_pan(char_name))
	AudioMgr.duck()
	_chars.call("activate_speaker", char_name.to_lower())
	_dlg.visible = true
	_dlg.call("show_think", char_name, _s(n, "text"))
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
			# An option may set a flag directly · the cheap way for a
			# choice to be remembered without goto-index surgery.
			if opt.has("flag"):
				_flags[String(opt["flag"])] = opt.get("val", true)
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
		_bg_debug_label.add_theme_font_size_override("font_size", 12)
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
	# Per-locale ambient bed: duck the Music Player way down and raise
	# this locale's inverted ambient soundtrack. Independent of whether
	# the GLB is present (below) — the scene IS this locale either way,
	# and a locale with no bed configured is a silent no-op.
	AudioMgr.enter_locale_ambient(preset_id)
	# Locale bust tint — like the ambient bed, the scene IS this locale
	# whether or not the GLB is built, so tint before the GLB check.
	if _chars != null:
		_chars.call("set_locale_tint", preset_id)
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
	if _director != null:
		_director.call("set_bg3d", _bg_3d_node)
		_director.call("on_locale_changed")
	if _chars != null:
		_chars.set("bg_is_3d", true)   # portraits flank, center stays clear
	if _bg_3d_node.has_method("queue_load"):
		_bg_3d_node.call("queue_load", preset_id)
	else:
		_bg_3d_node.call_deferred("load_location", preset_id)


func _clear_bg_3d() -> void:
	# Leaving the locale: crossfade the ambient bed back out and let
	# the Music Player return to full volume.
	AudioMgr.exit_locale_ambient()
	if _director != null:
		_director.call("on_locale_changed")
	if _chars != null:
		_chars.set("bg_is_3d", false)
		_chars.call("set_locale_tint", "")
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
		# Scene-driven, non-looping: the VN queue/chapter rotation
		# takes over when the track ends. Respects jukebox mode.
		AudioMgr.request_scene_bgm(src, false)
	else:
		AudioMgr.enqueue_music(src)


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
	_tick_reading_comfort(delta)
	# Voiced/auto-advance timer honors the same modal fences as
	# _tick_reading_comfort — it must not fire through a transition,
	# photo mode, the backlog, a choice, an interlude, or a slowstick
	# overlay. The timer HOLDS while fenced (no decrement) so the
	# advance resumes cleanly when the modal clears.
	if _auto_timer > 0.0 and _can_timed_advance():
		_auto_timer -= delta
		if _auto_timer <= 0.0:
			_auto_timer = 0.0
			if not AudioMgr.is_voice_playing():
				_advance()
	_apply_bg_motion(delta)


func _can_timed_advance() -> bool:
	if _transition_lock or _photo_on or _backlog_overlay != null:
		return false
	if _choices != null and _choices.visible:
		return false
	if _interlude != null and _interlude.visible:
		return false
	return get_tree().get_first_node_in_group("vn_input_blocker") == null


func _toggle_auto_mode() -> void:
	_auto_mode = not _auto_mode
	_auto_read_t = 0.0
	if _auto_chip == null:
		_auto_chip = Label.new()
		_auto_chip.text = "AUTO ▸"
		_auto_chip.add_theme_font_size_override("font_size", 13)
		_auto_chip.add_theme_color_override("font_color", Color(0.82, 0.72, 0.52, 0.9))
		_auto_chip.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.8))
		_auto_chip.add_theme_constant_override("outline_size", 4)
		_auto_chip.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
		_auto_chip.offset_left = -86
		_auto_chip.offset_top = -30
		_auto_chip.z_index = UI_Z + 5
		_auto_chip.add_to_group("ui")
		add_child(_auto_chip)
	_auto_chip.visible = _auto_mode
	var sb := get_node_or_null("/root/SFXBank")
	if sb: sb.play("blip", 0.3)


func _tick_reading_comfort(delta: float) -> void:
	# the pointer fades out of a held frame — but NOT while a modal
	# overlay (cabin TV / slowstock shelf / backlog) is open: those
	# are pointer-driven surfaces, and hiding the cursor there reads
	# as a bug, not reading comfort.
	_cursor_idle_t += delta
	if _cursor_idle_t > 3.5 and not _photo_on \
			and Input.get_mouse_mode() == Input.MOUSE_MODE_VISIBLE \
			and get_tree().get_first_node_in_group("vn_input_blocker") == null:
		Input.set_mouse_mode(Input.MOUSE_MODE_HIDDEN)
	# hands-free page turn: a beat after the typewriter rests,
	# scaled to how much was just read
	if not _auto_mode or _transition_lock or _photo_on \
			or _backlog_overlay != null or _choices.visible \
			or _interlude.visible \
			or get_tree().get_first_node_in_group("vn_input_blocker") != null:
		_auto_read_t = 0.0
		return
	if _dlg == null or not _dlg.visible or bool(_dlg.call("is_typing")):
		_auto_read_t = 0.0
		return
	_auto_read_t += delta
	var chars: int = 0
	var bl: Array = _dlg.get("backlog")
	if not bl.is_empty():
		chars = String((bl[bl.size() - 1] as Dictionary).get("text", "")).length()
	var hold: float = clampf(1.3 + float(chars) * 0.03, 2.2, 7.0)
	if _auto_read_t >= hold:
		_auto_read_t = 0.0
		_advance()


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
		return
	# Cursor wake is not VN chrome — it stays above the modal fence
	# so the pointer still un-hides while a slowstick is open. Wakes
	# on BUTTONS too: clicking without moving (or Deck touchscreen
	# taps, which emit no motion events) must also bring it back.
	if (event is InputEventMouseMotion or event is InputEventMouseButton) \
			and not _photo_on:
		_cursor_idle_t = 0.0
		if Input.get_mouse_mode() == Input.MOUSE_MODE_HIDDEN:
			Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	# Modal fence FIRST — while a full-screen overlay (the cabin TV /
	# slowstock library) owns the keyboard, no VN hotkey (F6/A/H) may
	# toggle chrome underneath. Photo mode keeps its swallow: when
	# photo is itself on, F6 below stays reachable to exit it.
	if not _photo_on and get_tree().get_first_node_in_group("vn_input_blocker") != null:
		return
	# ── PHOTO MODE (F6) · chrome off, bars on, cursor gone. While
	# on, every other input is swallowed so framing a shot can't
	# advance the story. Deliberately not part of the F4 sweep — the
	# bars ARE the picture.
	if event is InputEventKey and event.pressed and not event.echo \
			and (event as InputEventKey).keycode == KEY_F6:
		_toggle_photo_mode()
		get_viewport().set_input_as_handled()
		return
	if _photo_on:
		return
	if event is InputEventKey and event.pressed and not event.echo \
			and (event as InputEventKey).keycode == KEY_A:
		# AUTO toggle is ignored mid-transition and while a choice is
		# up — flipping hands-free mode there could advance past the
		# decision or fight the veil.
		if not _transition_lock and not _choices.visible:
			_toggle_auto_mode()
			get_viewport().set_input_as_handled()
		return
	# ── THE BACKLOG (H or wheel-up) · everything read, re-readable.
	var wheel_up: bool = event is InputEventMouseButton and event.pressed \
			and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_WHEEL_UP
	var h_key: bool = event is InputEventKey and event.pressed and not event.echo \
			and (event as InputEventKey).keycode == KEY_H
	if (wheel_up or h_key) and _backlog_overlay == null and not _transition_lock \
			and not _choices.visible:
		_open_backlog()
		get_viewport().set_input_as_handled()
		return
	# Scene transition in flight — the veil or a chapter card owns the
	# screen. The ChapterCard handles its own advance input; nothing
	# may reach the story underneath.
	if _transition_lock:
		return
	# Modal fence: a full-screen overlay (the cabin TV / slowstock
	# library) is open somewhere above us. _input fires before ANY
	# gui routing, so without this gate every key pressed inside a
	# slowstick also advances the novel underneath.
	if get_tree().get_first_node_in_group("vn_input_blocker") != null:
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
		# A click aimed at an actual button — the HUD MENU, an
		# overlay control — belongs to the GUI. _input runs BEFORE
		# gui routing, so set_input_as_handled() below was eating
		# the press and every Button on the reading screen was
		# mouse-dead (the choice menu only worked because of its
		# explicit gate above).
		if event is InputEventMouseButton and _mouse_over_button():
			return
		get_viewport().set_input_as_handled()
		if _interlude.visible:
			_interlude.call("try_advance")
		else:
			_advance()
	elif event.is_action_pressed("menu_back"):
		get_viewport().set_input_as_handled()
		_open_in_game_menu()


# ─── the backlog overlay ─────────────────────────────────────────

func _open_backlog() -> void:
	var entries: Array = _dlg.get("backlog") if _dlg != null else []
	_backlog_overlay = Control.new()
	_backlog_overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_backlog_overlay.z_index = UI_Z + 55
	_backlog_overlay.mouse_filter = Control.MOUSE_FILTER_STOP
	_backlog_overlay.add_to_group("ui")
	_backlog_overlay.add_to_group("vn_input_blocker")
	add_child(_backlog_overlay)

	var dim := ColorRect.new()
	dim.color = Color(0.01, 0.01, 0.02, 0.88)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_backlog_overlay.add_child(dim)

	var col := VBoxContainer.new()
	col.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	col.offset_left = -420
	col.offset_right = 420
	col.offset_top = -300
	col.offset_bottom = 300
	col.add_theme_constant_override("separation", 8)
	_backlog_overlay.add_child(col)

	var hdr := Label.new()
	hdr.text = "· the story so far · H or ESC returns ·"
	hdr.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hdr.add_theme_font_size_override("font_size", 13)
	hdr.add_theme_color_override("font_color", Color(0.62, 0.58, 0.50))
	col.add_child(hdr)

	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	col.add_child(scroll)

	var body := RichTextLabel.new()
	body.bbcode_enabled = true
	body.fit_content = true
	body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body.custom_minimum_size = Vector2(820, 0)
	body.add_theme_font_size_override("normal_font_size", 15)
	body.add_theme_color_override("default_color", Color(0.88, 0.86, 0.82))
	body.mouse_filter = Control.MOUSE_FILTER_IGNORE
	scroll.add_child(body)

	var lines := PackedStringArray()
	for e_v in entries:
		var e: Dictionary = e_v
		var nm := String(e.get("name", ""))
		var txt := String(e.get("text", ""))
		if bool(e.get("think", false)):
			txt = "[i]" + txt + "[/i]"
		if nm == "":
			lines.append("[color=#a8a49a]" + txt + "[/color]")
		else:
			var accent := Color(0.82, 0.72, 0.52)
			if _chars != null and _chars.has_method("accent_for"):
				var av: Variant = _chars.call("accent_for", nm)
				if av is Color:
					accent = av
			lines.append("[color=%s][b]%s[/b][/color] · %s" % [accent.to_html(false), nm, txt])
	body.text = "\n\n".join(lines) if not lines.is_empty() else "[i]nothing read yet — the book is still open to its first page.[/i]"

	# open at the freshest line, not the top of the session
	scroll.set_deferred("scroll_vertical", 999999)

	_backlog_overlay.gui_input.connect(func(ev: InputEvent) -> void:
		var close := false
		if ev is InputEventKey and ev.pressed:
			var k := (ev as InputEventKey).keycode
			close = k == KEY_ESCAPE or k == KEY_H
		elif ev is InputEventMouseButton and ev.pressed \
				and (ev as InputEventMouseButton).button_index == MOUSE_BUTTON_WHEEL_DOWN \
				and scroll.scroll_vertical >= int(scroll.get_v_scroll_bar().max_value - scroll.size.y) - 4:
			close = true   # wheel past the freshest line rolls back to the story
		if close:
			_close_backlog()
			get_viewport().set_input_as_handled())
	# keys land on the overlay
	_backlog_overlay.focus_mode = Control.FOCUS_ALL
	_backlog_overlay.grab_focus.call_deferred()


func _close_backlog() -> void:
	if _backlog_overlay != null and is_instance_valid(_backlog_overlay):
		_backlog_overlay.queue_free()
	_backlog_overlay = null


# ─── photo mode ──────────────────────────────────────────────────

func _toggle_photo_mode() -> void:
	_photo_on = not _photo_on
	if _photo_bars.is_empty():
		for top in [true, false]:
			var bar := ColorRect.new()
			bar.color = Color.BLACK
			bar.z_index = UI_Z + 60
			bar.set_anchors_preset(Control.PRESET_TOP_WIDE if top else Control.PRESET_BOTTOM_WIDE)
			bar.offset_bottom = 54 if top else 0
			bar.offset_top = 0 if top else -54
			bar.visible = false
			bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
			add_child(bar)
			_photo_bars.append(bar)
	if _photo_on:
		# Entering the frame: the backlog is chrome too — drop it.
		_close_backlog()
		_photo_restore = {}
		for n in [_dlg, _hud, _choices, _auto_chip]:
			if n != null and is_instance_valid(n):
				_photo_restore[n.get_instance_id()] = n.visible
				n.visible = false
		for b in _photo_bars:
			(b as ColorRect).visible = true
		Input.set_mouse_mode(Input.MOUSE_MODE_HIDDEN)
	else:
		for n2 in [_dlg, _hud, _choices, _auto_chip]:
			if n2 != null and is_instance_valid(n2) and _photo_restore.has(n2.get_instance_id()):
				n2.visible = bool(_photo_restore[n2.get_instance_id()])
		for b2 in _photo_bars:
			(b2 as ColorRect).visible = false
		Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)


# True when the mouse is over a Button (or inside one — icon /
# label children resolve up the chain). Those clicks are the GUI's.
func _mouse_over_button() -> bool:
	var hov: Control = get_viewport().gui_get_hovered_control()
	var n: Node = hov
	while n != null:
		if n is BaseButton:
			return true
		n = n.get_parent()
	return false


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

const VN_ARCANA_MAP := "res://resources/almanac/vn_arcana_map.json"

func _record_vn_reading(scene_id: String) -> void:
	# VN <-> Gauntlet binding (conservative). Finishing a Vol-5 arcana
	# chapter fires vn_read_<arcana>, which lights the Almanac's THE
	# READING chapter and marks the arcana on the Major Arcana ladder.
	# Legible only — reading never grants a gauntlet advantage.
	if not FileAccess.file_exists(VN_ARCANA_MAP):
		return
	var f := FileAccess.open(VN_ARCANA_MAP, FileAccess.READ)
	if f == null:
		return
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if not (parsed is Dictionary):
		return
	var m: Dictionary = (parsed as Dictionary).get("scene_to_arcana", {})
	var arc := String(m.get(scene_id, ""))
	if arc != "":
		OneironauticsTokens.add("vn_read_" + arc)


func _end_scene() -> void:
	_record_vn_reading(_scene_id)
	_dlg.visible = false
	AudioMgr.stop_voice()
	var next := SceneDataDB.get_next_scene_id(_scene_id)
	if next == "":
		AudioMgr.unduck()
		AudioMgr.stop_scene_bgm()
		if _director != null:
			_director.call("release")
		_set_vn_focus(false)
		game_ended.emit()
		return
	# Producer sequencing: the music dips WITH the fade-out; the bed
	# stops and the camera releases only at full black. (Before this,
	# BGM hard-cut and the camera snapped while the scene was still
	# on screen.)
	if _producer != null:
		_producer.call("scene_out_begin")
	# Capture the boundary BEFORE _load_scene replaces _scene_data.
	var prev_ch := str(_scene_data.get("chapter", ""))
	var prev_vol := _vol
	var next_scene := SceneDataDB.get_scene(next)
	var next_vol: int = int(next_scene.get("vol", _vol))
	if next_vol != _vol:
		_vol = next_vol
		_apply_skin(_vol)
	var chapter_break: bool = next_vol != prev_vol \
		or str(next_scene.get("chapter", "")) != prev_ch
	var titled: bool = String(next_scene.get("title", "")).strip_edges() != ""
	# Fade to black, build the next scene under the veil, then either
	# present the chapter plate (boundary) or fade back in (same-frame
	# cuts are gone — every scene change breathes).
	await _fade_veil_in(0.3)
	if _producer != null:
		_producer.call("scene_out_black")
	if _director != null:
		_director.call("release")
	_load_scene(next)
	if chapter_break and titled:
		_present_chapter_card(next_scene)
	else:
		_fade_veil_out(0.45)


# ── Transition machinery ────────────────────────────────────────

func _ensure_veil() -> void:
	if _veil != null and is_instance_valid(_veil):
		return
	_veil = ColorRect.new()
	_veil.color = Color(0.01, 0.008, 0.005, 0.0)
	_veil.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_veil.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_veil.z_index = UI_Z + 40
	add_child(_veil)


func _set_veil(alpha: float) -> void:
	_ensure_veil()
	_veil.color.a = alpha
	_transition_lock = alpha > 0.0
	if _transition_lock and _producer != null:
		_producer.call("hold_curtain")


func _fade_veil_in(dur: float) -> void:
	# to black
	_ensure_veil()
	_transition_lock = true
	if _producer != null:
		_producer.call("hold_curtain")
	var tw := create_tween()
	tw.tween_property(_veil, "color:a", 1.0, dur)
	await tw.finished


func _fade_veil_out(dur: float) -> void:
	# reveal; the music returns with the light, the input lock lifts
	# when fully clear, and the producer raises the curtain (settle
	# beat, then the held first node runs).
	_ensure_veil()
	_transition_lock = true
	if _producer != null:
		_producer.call("reveal_begin")
	var tw := create_tween()
	tw.tween_property(_veil, "color:a", 0.0, dur)
	tw.tween_callback(func() -> void:
		_transition_lock = false
		if _producer != null:
			_producer.call("curtain_up"))


func _present_chapter_card(scene: Dictionary) -> void:
	_transition_lock = true
	if _chapter_card != null and is_instance_valid(_chapter_card):
		_chapter_card.queue_free()
	_chapter_card = CHAPTER_CARD_SCRIPT.new()
	_chapter_card.z_index = UI_Z + 50
	add_child(_chapter_card)
	var ch := str(scene.get("chapter", "")).strip_edges()
	_chapter_card.call("set_plate", _vol, scene.get("chapter", 0))
	var kicker := "VOLUME %d" % _vol
	if ch != "":
		kicker += "   ·   CHAPTER %s" % ch.to_upper()
	_chapter_card.call("present", kicker, String(scene.get("title", "")),
		func() -> void:
			if _chapter_card != null and is_instance_valid(_chapter_card):
				_chapter_card.queue_free()
			_chapter_card = null
			_transition_lock = false
			# The plate sat in hush; music and the first line arrive
			# together as it clears.
			if _producer != null:
				_producer.call("reveal_begin")
				_producer.call("curtain_up"))
	# The card is opaque — drop the veil behind it so the world is
	# already revealed when the card fades itself out.
	if _veil != null and is_instance_valid(_veil):
		_veil.color.a = 0.0


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
