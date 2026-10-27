# VnDirector.gd
# ════════════════════════════════════════════════════════════════
# The VN's camera direction — a 3D COMIC, not a film. Hard cuts
# between held frames; drift is the marked exception. Grammar and
# authoring rules live in lore/_VN_DIRECTION_PLAYBOOK.md.
#
# Owned by GameEngine. Drives the Background3D SubViewport camera:
#
#   apply_shot("establish")          cut to the locale wide
#   apply_shot("closeup jen")        cut to Marker3D shot_closeup_jen
#   apply_shot("insert register~")   cut to shot_insert_register, drifting
#   apply_panel("receipt_47")        overlay resources/vn/panels/receipt_47.json
#   apply_panel("off")               dismiss the panel
#   release()                        restore establish vantage, bars off
#
# Shots are Marker3D nodes authored IN the locale .tscn, named
# shot_<type>_<id>, group "vn_shot", optional metadata/fov.
# "establish" falls back to the Background3D camera preset when no
# shot_establish marker exists — so every existing locale supports
# [shot:establish] with zero markup. Unknown marker / panel id is a
# silent no-op: a script must never crash the reader.
# ════════════════════════════════════════════════════════════════
extends Node

# Preload-by-path: HeroImage's class_name may miss the first editor
# scan after a pull; the explicit path always resolves.
const HeroImageScript := preload("res://scenes/games/estuary_3/HeroImage.gd")

const PANEL_DIR := "res://resources/vn/panels/"

# Letterbox bars — the comic's panel crop on closeup/insert.
const BAR_HEIGHT := 54.0       # px at 720p reference
const BAR_TWEEN  := 0.12       # fast — a cut, not a curtain

# Drift — slow push-in via FOV tighten, ~2%/sec, floored so a held
# shot never zooms into soup.
const DRIFT_RATE      := 0.02
const DRIFT_MIN_RATIO := 0.86

# Default FOV per shot type when the marker carries no metadata/fov.
const TYPE_FOV := {"closeup": 45.0, "insert": 35.0}
const CLOSEUP_PITCH_MIN := -0.07     # rad: a face frame looks level, a touch down at most
const CLOSEUP_PITCH_MAX := 0.035

# ── Coverage rotation (2026-08-04, "directing the scenes") ──────
# A locale like louisiana_road appears in 37 scenes through ONE
# photograph: every [shot:establish] is the same frame. When a
# locale authors shot_establish_b / _c / _d markers, the director
# picks ONE per chapter (hash of the scene key) — a chapter holds
# its angle consistently, but across the volume the same road is
# seen from different setups. Zero scene-JSON edits; locales opt in
# simply by carrying the extra markers.
var scene_key: String = ""

var _bg3d: Node = null              # Background3D (SubViewportContainer)
# Which side of the room each speaker owns, for as long as this locale
# holds (2026-09-11). A closeup of a person almost never has a marker of
# its own — 561 such cues across 112 presets — so the room's GENERIC pair
# (shot_closeup_person + _b, authored by marker_author --closeup) is the
# face vocabulary. Hashing the character id onto that pair put two
# speakers on the same frame half the time; first-seen order gives them a
# side each and keeps it, which is the film rule, not a coin toss.
var _face_side: Dictionary = {}
var _bar_top: ColorRect = null
var _bar_bottom: ColorRect = null
var _panel_card: Control = null
var _overlay_parent: Control = null

# AN INSERT IS A GLANCE (2026-10-27, the Deck: "that insert never leaves
# the scene once it is shown"). A [shot:insert X] held until the author's
# next cue — ch12's Speak & Spell stayed the whole picture through closing
# the notebook, the drawer, the lights and the deposit slip. It now holds
# its own line and INSERT_HOLD - 1 more, longer while the lines keep naming
# it or an open panel shows the same thing (the notebook while its list is
# read), then the room comes back (consider_line).
const INSERT_HOLD := 3
var _insert_left: int = 0
var _insert_words: PackedStringArray = PackedStringArray()
var _panel_words: PackedStringArray = PackedStringArray()

var _drifting: bool = false
var _drift_floor: float = 50.0

# A [shot:] can land one line after a bg directive whose deferred
# load_location hasn't run yet — park it and retry a few frames.
var _pending_shot: String = ""
var _pending_frames: int = 0
# Who says the line being directed (GameEngine sets it before the line's
# directives; "" for narration). A generic face cue on a speaker's line
# cuts to the speaker's own frame when the room has one (2026-10-27).
var _line_speaker: String = ""
var _pending_speaker: String = ""
const PENDING_MAX_FRAMES := 60

# [stage:] and [mood:] race the deferred locale load the same way —
# park them in order and drain once the locale exists.
var _pending_ops: Array[Dictionary] = []
var _pending_op_frames: int = 0
const PENDING_OP_MAX_FRAMES := 120

# Letterbox bookkeeping for beats: _letterbox_on mirrors the bars'
# logical state; _lb_seq bumps on every _set_letterbox so a beat's
# delayed release can tell whether a later shot re-claimed the bars.
var _letterbox_on: bool = false
var _drift_rate: float = DRIFT_RATE
var _lb_seq: int = 0


func setup(overlay_parent: Control) -> void:
	_overlay_parent = overlay_parent
	_bar_top = _make_bar()
	_bar_top.set_anchors_preset(Control.PRESET_TOP_WIDE)
	_bar_bottom = _make_bar()
	_bar_bottom.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	overlay_parent.add_child(_bar_top)
	overlay_parent.add_child(_bar_bottom)


func _make_bar() -> ColorRect:
	var bar := ColorRect.new()
	bar.color = Color(0.0, 0.0, 0.0, 1.0)
	bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	# Above the 3D bg + composition layers, below portraits/dialog
	# (which pin at GameEngine.UI_Z = 100).
	bar.z_index = 95
	bar.custom_minimum_size = Vector2(0, 0)
	bar.visible = false
	return bar


func set_bg3d(bg3d: Node) -> void:
	_bg3d = bg3d


# Called by GameEngine whenever the bg changes (new 3D preset or a
# 2D bg) — a page turn resets the direction state.
func on_locale_changed() -> void:
	_pending_shot = ""
	_pending_ops.clear()
	_drifting = false
	_face_side.clear()
	_set_letterbox(false)
	_dismiss_panel()
	_panel_words = PackedStringArray()
	_insert_left = 0
	# a new room: its pictures are new to the eye
	_art_used.clear()
	_art_return = {}
	_art_cooldown = 0
	_drift_rate = DRIFT_RATE


func release() -> void:
	on_locale_changed()
	if _bg3d != null and is_instance_valid(_bg3d) and _bg3d.has_method("restore_preset_vantage"):
		_bg3d.restore_preset_vantage()


# ── Cast staging + mood ───────────────────────────────────────────
# [stage:john counter_post] → Background3D.stage_character("john",
# "counter_post"); [stage:john off] removes him. [mood:<name>] →
# the locale MoodCycler's style pack / mood by name (lighting +
# post-process as one look). Both park until the locale loads.

func apply_stage(spec: String) -> void:
	_pending_ops.append({"kind": "stage", "arg": spec.strip_edges().to_lower()})
	_pending_op_frames = 0
	_try_apply_ops()


func apply_mood(spec: String) -> void:
	_pending_ops.append({"kind": "mood", "arg": spec.strip_edges().to_lower()})
	_pending_op_frames = 0
	_try_apply_ops()


# ── Beats · [beat:x] · synchronized emphasis in one directive ─────
# The producer discipline at line level: a sting (with its haptic,
# free via SFXBank.RUMBLE_MAP), a camera breath (quick push or pull,
# easing home), and a letterbox pulse fire TOGETHER. Four house
# beats — a small vocabulary on purpose; a beat that appears twice a
# chapter stays an event.
#
#   still · a held hush — letterbox + the gentlest push, no sting
#   hit   · the hard beat — thud sting, sharp push-in
#   chill · the uncanny — cold sting, slow push, longest hold
#   lift  · wonder/relief — warm sting, a pull BACK (fov opens)
const BEATS := {
	"still": {"sting": "",                   "vol": 0.0,  "punch": 0.94, "hold": 1.8},
	"hit":   {"sting": "loss_thud",          "vol": 0.55, "punch": 0.88, "hold": 1.2},
	"chill": {"sting": "tier_crossing_close", "vol": 0.5, "punch": 0.93, "hold": 2.2},
	"lift":  {"sting": "interlude_earned",   "vol": 0.5,  "punch": 1.06, "hold": 1.6},
}


func apply_beat(spec: String) -> void:
	_pending_ops.append({"kind": "beat", "arg": spec.strip_edges().to_lower()})
	_pending_op_frames = 0
	_try_apply_ops()


func _do_beat(beat_name: String) -> bool:
	if not BEATS.has(beat_name):
		return false
	var b: Dictionary = BEATS[beat_name]
	var sting := String(b["sting"])
	if sting != "":
		SFXBank.play(sting, float(b["vol"]))
	var hold := float(b["hold"])
	# Letterbox pulse. If a shot already has the bars in, they stay —
	# the beat only borrows them, tracked by _lb_seq so a shot fired
	# during the hold cancels the stale release.
	var was_on := _letterbox_on
	_set_letterbox(true)
	var my_seq := _lb_seq
	if not was_on:
		var tw2 := create_tween()
		tw2.tween_interval(hold)
		tw2.tween_callback(func() -> void:
			if _lb_seq == my_seq:
				_set_letterbox(false))
	# Camera breath: quick punch (in, or OUT for lift), ease home.
	var cam: Camera3D = _bg3d.get_camera() if _bg3d.has_method("get_camera") else null
	if cam != null:
		_drifting = false
		var fov0 := cam.fov
		var tw := create_tween()
		tw.tween_property(cam, "fov", fov0 * float(b["punch"]), 0.12)\
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
		tw.tween_property(cam, "fov", fov0, maxf(0.4, hold * 0.6))\
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	return true


func _try_apply_ops() -> void:
	if _pending_ops.is_empty():
		return
	if _bg3d == null or not is_instance_valid(_bg3d):
		_pending_ops.clear()
		return
	if not _locale_ready():
		_pending_op_frames += 1
		if _pending_op_frames > PENDING_OP_MAX_FRAMES:
			_pending_ops.clear()
		return
	for op: Dictionary in _pending_ops:
		var arg := String(op.get("arg", ""))
		if op.get("kind") == "beat":
			var bok := _do_beat(arg)
			print("[VnDirector] BEAT → %s%s" % [arg, "" if bok else " · MISS"])
		elif op.get("kind") == "stage":
			var parts := arg.split(" ", false)
			if parts.size() < 2:
				continue
			var ok := false
			if _bg3d.has_method("stage_character"):
				ok = bool(_bg3d.stage_character(String(parts[0]), String(parts[1])))
			print("[VnDirector] STAGE %s → %s%s" % [parts[0], parts[1], "" if ok else " · MISS"])
		else:
			var mc: Node = _bg3d.get_locale_mood_cycler() if _bg3d.has_method("get_locale_mood_cycler") else null
			var ok := false
			if mc != null and mc.has_method("apply_style_or_mood"):
				ok = bool(mc.apply_style_or_mood(arg))
			print("[VnDirector] MOOD → %s%s" % [arg, "" if ok else " · MISS"])
	_pending_ops.clear()


# ── Shots ─────────────────────────────────────────────────────────
func _rotation_marker() -> Node3D:
	if _bg3d == null or not _bg3d.has_method("find_shot_marker"):
		return null
	# Variant 0 is ALWAYS the locale's default view — the authored
	# shot_establish marker if present, else null meaning "the
	# Background3D preset vantage". Alternates extend the deck; they
	# never evict the original framing from rotation.
	var variants: Array = [_bg3d.find_shot_marker("shot_establish")]
	for suffix in ["b", "c", "d", "e"]:
		var m: Node3D = _bg3d.find_shot_marker("shot_establish_" + suffix)
		if m != null:
			variants.append(m)
	if variants.size() <= 1 or scene_key == "":
		return variants[0]
	var idx: int = posmod(scene_key.hash(), variants.size())
	return variants[idx]


func set_line_speaker(char_id: String) -> void:
	# "Mr. Henderson" → mr_henderson, "chief miller" → chief_miller
	var raw: String = char_id.strip_edges().to_lower()
	var out: String = ""
	for i in raw.length():
		var c: String = raw[i]
		if (c >= "a" and c <= "z") or (c >= "0" and c <= "9"):
			out += c
		elif out != "" and not out.ends_with("_"):
			out += "_"
	_line_speaker = out.trim_suffix("_")


func apply_shot(spec: String) -> void:
	_pending_shot = spec.strip_edges()
	_pending_speaker = _line_speaker
	_pending_frames = 0
	_try_apply_shot()


func _try_apply_shot() -> void:
	if _pending_shot == "":
		return
	if _bg3d == null or not is_instance_valid(_bg3d):
		_pending_shot = ""
		return
	var spec := _pending_shot
	var drift := spec.ends_with("~")
	if drift:
		spec = spec.substr(0, spec.length() - 1).strip_edges()
	var parts := spec.split(" ", false)
	if parts.is_empty():
		_pending_shot = ""
		return
	var shot_type := String(parts[0]).to_lower()
	var shot_id := String(parts[1]).to_lower() if parts.size() > 1 else ""
	var marker_name := "shot_" + shot_type + (("_" + shot_id) if shot_id != "" else "")

	# Locale still loading (deferred load_location) → retry next frame.
	if not _locale_ready():
		_pending_frames += 1
		if _pending_frames > PENDING_MAX_FRAMES:
			_pending_shot = ""
		return
	_pending_shot = ""
	_insert_left = INSERT_HOLD if shot_type == "insert" else 0
	_insert_words = _line_words(shot_id.replace("_", " ")) if shot_type == "insert" else PackedStringArray()

	var marker: Node3D = null
	# The generic face pair on a line someone says: the speaker's own frame
	# first, when this room has one in this preset's area.
	if shot_type == "closeup" and (shot_id == "person" or shot_id == "person_b") \
			and _pending_speaker != "" and _bg3d.has_method("find_cast_closeup"):
		var own: Node3D = _bg3d.call("find_cast_closeup", _pending_speaker) as Node3D
		if own != null:
			_set_letterbox(true)
			_cut_to_marker(own, shot_type, drift)
			print("[VnDirector] CUT closeup → %s (the speaker's frame, for %s)%s"
				% [own.name, marker_name, " ~drift" if drift else ""])
			return
	if _bg3d.has_method("find_shot_marker"):
		marker = _bg3d.find_shot_marker(marker_name)

	if shot_type == "establish" and shot_id == "":
		# Coverage rotation: prefer this chapter's assigned variant
		# when the locale authors alternates.
		var rot := _rotation_marker()
		if rot != null:
			marker = rot

	if shot_type == "establish":
		_set_letterbox(false)
		if marker != null:
			_cut_to_marker(marker, shot_type, drift)
			print("[VnDirector] CUT establish → marker%s" % (" ~drift" if drift else ""))
		else:
			if _bg3d.has_method("restore_preset_vantage"):
				_bg3d.restore_preset_vantage()
			_start_drift(drift)
			print("[VnDirector] CUT establish → preset vantage%s" % (" ~drift" if drift else ""))
		return

	# closeup / insert (and any future marker-backed type)
	if marker == null:
		# A WIDE with no marker must never fall into the punch-in —
		# the zoom fallback would cut TIGHTER for a cue that asks
		# for the opposite. The widest framing we always have is the
		# preset vantage.
		if shot_type == "wide":
			if _bg3d.has_method("restore_preset_vantage"):
				_bg3d.restore_preset_vantage()
			_set_letterbox(true)
			_start_drift(drift)
			print("[VnDirector] CUT wide (preset vantage, no %s)%s" % [marker_name, " ~drift" if drift else ""])
			return
		# ── No authored marker for this cue ────────────────────
		# The blind punch-in used to fire here, and it is the reason
		# whole chapters read as "mostly just solid color scenes"
		# (user, 2026-08-12): zooming fov 35 into the middle of the
		# establishing wide fills the frame with whatever flat
		# surface happens to be there. A repo-wide audit found 453
		# such cues across 79 presets.
		#
		# A director without the exact insert shoots a DIFFERENT
		# real detail rather than pushing the lens into a wall. So:
		# borrow a same-type marker from this locale, chosen
		# deterministically from the cue id so the same line always
		# frames the same object (consistency beats variety here).
		var subs: Array = []
		if _bg3d.has_method("shot_markers_of_type"):
			subs = _bg3d.call("shot_markers_of_type", shot_type)
		if subs.is_empty() and shot_type == "closeup" \
				and _bg3d.has_method("shot_markers_of_type"):
			# A closeup of an unstaged THING can borrow an insert.
			subs = _bg3d.call("shot_markers_of_type", "insert")
		if not subs.is_empty():
			var pick: Node3D = null
			if shot_type == "closeup":
				var faces: Array[Node3D] = []
				for s_v in subs:
					var s_n: Node3D = s_v as Node3D
					if s_n != null and String(s_n.name).begins_with("shot_closeup_person"):
						faces.append(s_n)
				if not faces.is_empty():
					faces.sort_custom(_by_name)
					if not _face_side.has(shot_id):
						_face_side[shot_id] = _face_side.size() % faces.size()
					pick = faces[int(_face_side[shot_id])]
			if pick == null:
				pick = subs[abs(shot_id.hash()) % subs.size()] as Node3D
			if pick != null:
				_set_letterbox(true)
				_cut_to_marker(pick, shot_type, drift)
				print("[VnDirector] CUT %s → %s (substitute for %s)%s"
					% [shot_type, pick.name, marker_name,
					   " ~drift" if drift else ""])
				return
		# Nothing authored in this locale at all: hold the wide. An
		# honest establishing frame beats a zoom into a flat wall.
		if _bg3d.has_method("restore_preset_vantage"):
			_bg3d.restore_preset_vantage()
		_start_drift(drift)
		print("[VnDirector] %s has no marker pool → holding the wide (was %s)"
			% [shot_type, marker_name])
		return
	_set_letterbox(true)
	_cut_to_marker(marker, shot_type, drift)
	print("[VnDirector] CUT %s → %s%s" % [shot_type, marker_name, " ~drift" if drift else ""])


func _by_name(a: Node3D, b: Node3D) -> bool:
	return String(a.name) < String(b.name)


func _locale_ready() -> bool:
	if _bg3d.has_method("has_locale_loaded"):
		return _bg3d.has_locale_loaded()
	return true


# Marker-free comic punch-in: a tighter FOV on the establish
# vantage's axis, derived from the PRESET (not the live camera) so
# repeated shots never compound.
#
# RETIRED as a fallback 2026-08-12 — kept because it is the correct
# behavior for a locale that WANTS a lens-only push (a future
# `[shot:push]` cue), but a missing marker no longer routes here:
# zooming into the middle of a wide was manufacturing the flat
# single-color frames the user reported. See apply_shot().
func _punch_in(shot_type: String, drift: bool) -> bool:
	if not _bg3d.has_method("get_preset_vantage") or not _bg3d.has_method("get_camera"):
		return false
	var v: Dictionary = _bg3d.get_preset_vantage()
	if v.is_empty():
		return false
	var cam: Camera3D = _bg3d.get_camera()
	if cam == null:
		return false
	var rot: Vector3 = v["rotation"]
	# ZOOM, don't dolly. The old fallback moved the camera 1.2-1.8m
	# forward along the view — with no collision data that landed
	# INSIDE shelving in tight interiors (a screen-filling product
	# box where a scene should be). A lens push can never enter
	# geometry; locales that want true dollied framings author
	# closeup/insert markers.
	cam.position = v["origin"] as Vector3
	cam.rotation = rot
	cam.fov = 30.0 if shot_type == "closeup" else 24.0
	cam.make_current()
	_set_letterbox(true)
	_start_drift(drift)
	return true


func _cut_to_marker(marker: Node3D, shot_type: String, drift: bool) -> void:
	var cam: Camera3D = _bg3d.get_camera() if _bg3d.has_method("get_camera") else null
	if cam == null:
		return
	cam.global_transform = marker.global_transform
	if shot_type == "closeup":
		# EYE LEVEL (2026-10-27, the Deck: "the camera being below their
		# sightlines is also weird, it should be eye-level, looking them in
		# the face"): 153 of 449 face frames were authored 15° down at a
		# seated spot, so the floor climbed the frame behind a level face.
		# A face frame keeps its place and its yaw and looks level.
		var e: Vector3 = marker.global_transform.basis.get_euler()
		e.x = clampf(e.x, CLOSEUP_PITCH_MIN, CLOSEUP_PITCH_MAX)
		cam.global_transform = Transform3D(Basis.from_euler(e), marker.global_position)
	var fov := float(TYPE_FOV.get(shot_type, 50.0))
	if marker.has_meta("fov"):
		fov = float(marker.get_meta("fov"))
	cam.fov = fov
	cam.make_current()
	_start_drift(drift)


func _start_drift(drift: bool) -> void:
	_drifting = drift
	_drift_rate = DRIFT_RATE
	if drift:
		var cam: Camera3D = _bg3d.get_camera() if _bg3d != null and _bg3d.has_method("get_camera") else null
		if cam != null:
			_drift_floor = cam.fov * DRIFT_MIN_RATIO


func _process(delta: float) -> void:
	if _pending_shot != "":
		_try_apply_shot()
	if not _pending_ops.is_empty():
		_try_apply_ops()
	if not _drifting:
		return
	if _bg3d == null or not is_instance_valid(_bg3d) or not _bg3d.has_method("get_camera"):
		_drifting = false
		return
	var cam: Camera3D = _bg3d.get_camera()
	if cam == null:
		_drifting = false
		return
	cam.fov = maxf(_drift_floor, cam.fov * (1.0 - _drift_rate * delta))


# ── Letterbox ─────────────────────────────────────────────────────
func _set_letterbox(on: bool) -> void:
	if _bar_top == null:
		return
	_letterbox_on = on
	_lb_seq += 1
	var h := BAR_HEIGHT if on else 0.0
	_bar_top.visible = true
	_bar_bottom.visible = true
	var tw := create_tween().set_parallel(true)
	tw.tween_property(_bar_top, "offset_bottom", h, BAR_TWEEN)
	tw.tween_property(_bar_bottom, "offset_top", -h, BAR_TWEEN)
	if not on:
		tw.chain().tween_callback(func() -> void:
			_bar_top.visible = false
			_bar_bottom.visible = false)


# ── Panels ────────────────────────────────────────────────────────
func apply_panel(id: String) -> void:
	id = id.strip_edges().to_lower()
	if id == "off" or id == "":
		_dismiss_panel()
		_panel_words = PackedStringArray()
		return
	_panel_words = _line_words(id.replace("_", " "))
	_dismiss_panel()
	# (2026-10-27, the Deck: "are we still using these old temp inserts and
	# not the new generated art from the hero tool?") a panel whose subject
	# has a hero-tool picture installed in the set (vol6_rick_notebook →
	# cosmic_comics_interior_rick_notebook.png on the desk) is not drawn: the
	# [shot:insert …] on the same line shows the real picture in the room.
	if _hero_art_for_panel(id) != "":
		return
	var card := _build_panel_card(id)
	if card == null:
		return
	_panel_card = card
	_overlay_parent.add_child(card)


const HERO_ART_DIR := "res://assets/art/hero/"
var _hero_art_files: PackedStringArray = PackedStringArray()


## The installed hero-art picture standing for panel `id` ("" when none):
## the id without its volume prefix is the picture's tail
## (vol6_rick_notebook → *_rick_notebook.png).
func _hero_art_for_panel(id: String) -> String:
	var key: String = id
	var rx := RegEx.create_from_string("^vol\\d+_")
	key = rx.sub(key, "", false)
	if key.length() < 4:
		return ""
	if _hero_art_files.is_empty():
		var d: DirAccess = DirAccess.open(HERO_ART_DIR)
		if d == null:
			return ""
		_hero_art_files = d.get_files()
	for f0: String in _hero_art_files:
		# an exported build lists the imported copies (x.png.import / .remap)
		var f: String = f0.trim_suffix(".import").trim_suffix(".remap")
		var base: String = f.get_basename()
		if (f.ends_with(".png") or f.ends_with(".jpg")) and (base == key or base.ends_with("_" + key)):
			return HERO_ART_DIR + f
	return ""


func _dismiss_panel() -> void:
	if _panel_card != null and is_instance_valid(_panel_card):
		_panel_card.queue_free()
	_panel_card = null


func _build_panel_card(id: String) -> Control:
	var card := PanelContainer.new()
	var st := StyleBoxFlat.new()
	st.bg_color = Color(0.055, 0.05, 0.045, 0.97)
	st.border_color = Color(0.83, 0.79, 0.69, 0.9)
	st.set_border_width_all(2)
	st.content_margin_left = 10
	st.content_margin_right = 10
	st.content_margin_top = 10
	st.content_margin_bottom = 10
	card.add_theme_stylebox_override("panel", st)
	card.mouse_filter = Control.MOUSE_FILTER_IGNORE

	var path := PANEL_DIR + id + ".json"
	var hero = HeroImageScript.new()
	var content: Control = null
	# (2026-10-27) the hero tool's picture of the panel's thing (roster
	# scene2d `panel_<id>`, installed at assets/cg/panel_<id>.jpg) replaces
	# the old pixel document when it is there
	var pic_path: String = "res://assets/cg/panel_%s.jpg" % id
	if ResourceLoader.exists(pic_path):
		var tex: Texture2D = load(pic_path) as Texture2D
		var pr := TextureRect.new()
		pr.texture = tex
		pr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		pr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		var aspect: float = float(tex.get_width()) / maxf(1.0, float(tex.get_height())) if tex != null else 1.33
		pr.custom_minimum_size = Vector2(minf(560.0, 320.0 * aspect), minf(320.0, 560.0 / maxf(aspect, 0.01)))
		content = pr
	elif FileAccess.file_exists(path) and hero.load_from(path):
		var texr := TextureRect.new()
		# Integer-ish upscale of the pixel doc. Height cap 300 keeps
		# the card INSIDE the upper field — the dialogue text zone
		# starts around y≈390 (box is ~46% of a 720 viewport) and the
		# old 420 cap was landing the card right on top of the prose.
		var scale_i: int = maxi(1, mini(int(700.0 / maxf(1.0, float(hero.w))), int(300.0 / maxf(1.0, float(hero.h)))))
		var target := Vector2i(hero.w * scale_i, hero.h * scale_i)
		texr.texture = hero.texture(target)
		texr.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		texr.custom_minimum_size = Vector2(target)
		texr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		content = texr
	else:
		# Fallback discipline: bordered text card with the id, so a
		# missing panel asset reads as a note, not a crash.
		var lbl := Label.new()
		lbl.text = id.replace("_", " ").to_upper()
		lbl.add_theme_font_size_override("font_size", 20)
		lbl.add_theme_color_override("font_color", Color(0.83, 0.79, 0.69))
		lbl.custom_minimum_size = Vector2(360, 80)
		lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		content = lbl
	card.add_child(content)
	# Center in the upper field — and STAY there. The dialogue text
	# zone begins ≈y390 (the box is ~46% of a 720 viewport), so the
	# band ends at 370. And the card sits BELOW the dialogue z
	# (UI_Z=100): if they ever do touch, the prose reads over the
	# image, never the reverse (user report 2026-07: "image over
	# text" — the old band reached 480 at z 101).
	var holder := CenterContainer.new()
	holder.set_anchors_preset(Control.PRESET_TOP_WIDE)
	holder.offset_top = 36.0
	holder.offset_bottom = 370.0
	holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	holder.z_index = 99
	holder.add_child(card)
	# Arrive like a document laid on the table, not a popup.
	card.modulate.a = 0.0
	var tw := card.create_tween()
	tw.tween_property(card, "modulate:a", 1.0, 0.25)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	return holder


# ════════════════════════════════════════════════════════════════
# THE ART IN THE ROOM (2026-10-14). The user: "the visual novel
# director needs to feature it but subtly. Building out quiet moments
# of stillness using the game mechanics would be preferable."
#
# Every picture HeroArt laid in the room (HeroArt.placements()) can be
# shot without a marker: the camera stands off the picture's face at the
# distance that fills ART_FILL of the frame, a few degrees off square
# (a photograph of a thing, not a scan), and drifts in slowly.
#
#   · NOTICING — a narration line with no [shot:] of its own that NAMES
#     a picture in the room by its object word ("the calendar", "the
#     photograph", "the mural") holds on that picture for the line, then
#     the next line returns the frame it left. Once per picture per room
#     visit; ART_COOLDOWN lines between; never on dialogue. Subtle by
#     construction: the prose already pointed there.
#   · STILLNESS — the player's own quiet moment (GameEngine: J / pad Y):
#     enter_stillness() frames the room's close-up pieces (`inspect`)
#     one at a time, nearest first; step_stillness(±1) browses;
#     exit_stillness() returns the frame. The text, the HUD and the music
#     are GameEngine's and AudioMgr's.
# ════════════════════════════════════════════════════════════════
const HeroArtScript := preload("res://scripts/vn/HeroArt.gd")
const ART_FOV := 30.0
const ART_FILL := 0.64            # of the frame's height (or width, whichever binds)
# With the text up (a noticing shot), the dialogue box owns the lower ~44 %
# of the screen: the picture is framed smaller and its centre sits at
# ART_TEXT_CENTER of the screen's height from the top, clear of the box.
const ART_FILL_TEXT := 0.40
const ART_TEXT_CENTER := 0.33
const ART_MIN_DIST := 0.30
const ART_MAX_DIST := 3.2
const ART_YAW := 0.10             # rad off square, toward the room's side
const ART_PITCH := -0.04          # rad: a touch from above, as eyes meet a wall
const ART_DRIFT := 0.008          # slower than a cue's drift: the stillness push
const ART_COOLDOWN := 6
var _art_used: Dictionary = {}
var _art_return: Dictionary = {}  # the frame an art shot left, to return to
var _art_cooldown: int = 0
var _still_list: Array = []
var _still_i: int = 0
var _still_return: Dictionary = {}  # the exact frame stillness was entered from


## Where the camera stands to frame picture `p` (a HeroArt placement).
func _art_pose(p: Dictionary, cam: Camera3D, with_text: bool = false) -> Transform3D:
	var quad: MeshInstance3D = p["quad"]
	var xf: Transform3D = quad.global_transform
	var center: Vector3 = xf.origin
	var normal: Vector3 = xf.basis.z.normalized()
	var size: Vector2 = p.get("size", Vector2.ONE)
	var aspect: float = 16.0 / 9.0
	var vp: Viewport = cam.get_viewport()
	if vp != null and vp.get_visible_rect().size.y > 0.0:
		aspect = vp.get_visible_rect().size.x / vp.get_visible_rect().size.y
	var half_v: float = tan(deg_to_rad(ART_FOV) * 0.5)
	var fill: float = ART_FILL_TEXT if with_text else ART_FILL
	var dist_h: float = (size.y / fill) * 0.5 / half_v
	var dist_w: float = (size.x / fill) * 0.5 / (half_v * aspect)
	var dist: float = clampf(maxf(dist_h, dist_w), ART_MIN_DIST, ART_MAX_DIST)
	# off square toward where the room's camera already is (its side of the
	# picture), a touch from above
	var side: float = 1.0
	var right: Vector3 = Vector3.UP.cross(normal).normalized()
	if right.length() < 0.5:
		right = Vector3.RIGHT
	if (cam.global_position - center).dot(right) < 0.0:
		side = -1.0
	var dir: Vector3 = normal.rotated(Vector3.UP, ART_YAW * side)
	dir = dir.rotated(right, ART_PITCH)
	var eye: Vector3 = center + dir.normalized() * dist
	var up: Vector3 = Vector3.UP if absf(normal.dot(Vector3.UP)) < 0.95 else Vector3.FORWARD
	var target: Vector3 = center
	if with_text:
		# aim below the picture so it rides high in the frame, over the box
		var frame_h: float = 2.0 * dist * half_v
		var wall_up: Vector3 = (up - normal * up.dot(normal)).normalized()
		target = center - wall_up * frame_h * (0.5 - ART_TEXT_CENTER)
	return Transform3D(Basis.looking_at(target - eye, up), eye)


func _art_cam() -> Camera3D:
	if _bg3d == null or not is_instance_valid(_bg3d) or not _bg3d.has_method("get_camera"):
		return null
	return _bg3d.get_camera()


func _save_frame(cam: Camera3D) -> Dictionary:
	return {"xf": cam.global_transform, "fov": cam.fov, "lb": _letterbox_on,
		"drift": _drifting, "rate": _drift_rate}


func _restore_frame(saved: Dictionary) -> void:
	var cam: Camera3D = _art_cam()
	if cam == null or saved.is_empty():
		return
	cam.global_transform = saved["xf"]
	cam.fov = float(saved["fov"])
	_set_letterbox(bool(saved["lb"]))
	_drifting = bool(saved["drift"])
	_drift_rate = float(saved["rate"])


## Cut to picture `p`, drifting slowly in. `with_text`: the dialogue box
## is up (a noticing shot) — frame the picture high and clear of it.
func cut_to_art(p: Dictionary, with_text: bool = false) -> bool:
	var cam: Camera3D = _art_cam()
	if cam == null:
		return false
	cam.global_transform = _art_pose(p, cam, with_text)
	cam.fov = ART_FOV
	cam.make_current()
	_set_letterbox(true)
	_drifting = true
	_drift_rate = ART_DRIFT
	_drift_floor = ART_FOV * DRIFT_MIN_RATIO
	return true


static func _line_words(text: String) -> PackedStringArray:
	var out := PackedStringArray()
	var clean: String = text.to_lower()
	for ch: String in [",", ".", ";", ":", "!", "?", "\"", "'s", "—", "(", ")", "[", "]"]:
		clean = clean.replace(ch, " ")
	for w: String in clean.split(" ", false):
		var ww: String = w.strip_edges()
		if ww.ends_with("s") and not ww.ends_with("ss"):
			ww = ww.substr(0, ww.length() - 1)
		if ww != "":
			out.append(ww)
	return out


## Every text line passes here before it shows (GameEngine). `cued`: the
## line carried its own [shot:] (the author's frame wins).
func consider_line(text: String, kind: String, cued: bool) -> void:
	if _insert_left > 0 and not cued:
		_hold_or_leave_insert(text)
	if not _art_return.is_empty():
		if not cued:
			_restore_frame(_art_return)
		_art_return = {}
	if _art_cooldown > 0:
		_art_cooldown -= 1
	if cued or kind != "narrate" or _art_cooldown > 0 or not _still_list.is_empty():
		return
	var words: PackedStringArray = _line_words(text)
	if words.is_empty():
		return
	var best: Dictionary = {}
	for pv: Variant in HeroArtScript.placements():
		var p: Dictionary = pv
		var slug: String = String(p.get("slug", ""))
		if _art_used.has(slug):
			continue
		var pw: PackedStringArray = p.get("words", PackedStringArray())
		var hit: bool = false
		for w: String in pw:
			if w in words:
				hit = true
				break
		if not hit:
			continue
		if best.is_empty() or (bool(p.get("inspect", false)) and not bool(best.get("inspect", false))):
			best = p
	if best.is_empty():
		return
	var cam: Camera3D = _art_cam()
	if cam == null:
		return
	_art_return = _save_frame(cam)
	if cut_to_art(best, true):
		_art_used[String(best["slug"])] = true
		_art_cooldown = ART_COOLDOWN
		print("[VnDirector] NOTICE → %s (the line names it)" % best["slug"])
	else:
		_art_return = {}


## One more line on an insert: kept while the line names its subject or an
## open panel shows it, else counted down; at zero the room's wide returns.
func _hold_or_leave_insert(text: String) -> void:
	var named: bool = false
	for w: String in _line_words(text):
		if w in _insert_words:
			named = true
			break
	if not named:
		for w: String in _panel_words:
			if w in _insert_words:
				named = true
				break
	if named:
		_insert_left = INSERT_HOLD
		return
	_insert_left -= 1
	if _insert_left <= 0:
		apply_shot("establish")
		print("[VnDirector] the insert has had its look → the room")


## The room's close-up pieces, nearest the current camera first.
func stillness_pieces() -> Array:
	var out: Array = []
	for pv: Variant in HeroArtScript.placements():
		var p: Dictionary = pv
		if bool(p.get("inspect", false)):
			out.append(p)
	var cam: Camera3D = _art_cam()
	if cam != null and out.size() > 1:
		var from: Vector3 = cam.global_position
		out.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
			return (a["quad"] as Node3D).global_position.distance_squared_to(from) \
				< (b["quad"] as Node3D).global_position.distance_squared_to(from))
	return out


func stillness_available() -> bool:
	return not stillness_pieces().is_empty()


## Enter the player's quiet moment; returns the first piece ({} = none).
func enter_stillness() -> Dictionary:
	var cam: Camera3D = _art_cam()
	if cam == null:
		return {}
	_still_list = stillness_pieces()
	if _still_list.is_empty():
		return {}
	_still_return = _save_frame(cam)
	_still_i = 0
	cut_to_art(_still_list[0])
	return _still_list[0]


func step_stillness(dir: int) -> Dictionary:
	if _still_list.is_empty():
		return {}
	_still_i = posmod(_still_i + dir, _still_list.size())
	cut_to_art(_still_list[_still_i])
	return _still_list[_still_i]


func stillness_count() -> int:
	return _still_list.size()


func stillness_index() -> int:
	return _still_i


## Back to exactly the frame the player left (a noticing shot stays a
## noticing shot; the next line still returns from it as usual).
func exit_stillness() -> void:
	_still_list = []
	_restore_frame(_still_return)
	_still_return = {}
