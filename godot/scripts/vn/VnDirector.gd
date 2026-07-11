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

var _bg3d: Node = null              # Background3D (SubViewportContainer)
var _bar_top: ColorRect = null
var _bar_bottom: ColorRect = null
var _panel_card: Control = null
var _overlay_parent: Control = null

var _drifting: bool = false
var _drift_floor: float = 50.0

# A [shot:] can land one line after a bg directive whose deferred
# load_location hasn't run yet — park it and retry a few frames.
var _pending_shot: String = ""
var _pending_frames: int = 0
const PENDING_MAX_FRAMES := 60


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
	_drifting = false
	_set_letterbox(false)
	_dismiss_panel()


func release() -> void:
	on_locale_changed()
	if _bg3d != null and is_instance_valid(_bg3d) and _bg3d.has_method("restore_preset_vantage"):
		_bg3d.restore_preset_vantage()


# ── Shots ─────────────────────────────────────────────────────────
func apply_shot(spec: String) -> void:
	_pending_shot = spec.strip_edges()
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

	var marker: Node3D = null
	if _bg3d.has_method("find_shot_marker"):
		marker = _bg3d.find_shot_marker(marker_name)

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
		# Silent no-op for the reader — but say so on the console,
		# else a typo'd shot id is indistinguishable from success.
		print("[VnDirector] shot '%s' → marker %s NOT FOUND · holding frame" % [spec, marker_name])
		return
	_set_letterbox(true)
	_cut_to_marker(marker, shot_type, drift)
	print("[VnDirector] CUT %s → %s%s" % [shot_type, marker_name, " ~drift" if drift else ""])


func _locale_ready() -> bool:
	if _bg3d.has_method("has_locale_loaded"):
		return _bg3d.has_locale_loaded()
	return true


func _cut_to_marker(marker: Node3D, shot_type: String, drift: bool) -> void:
	var cam: Camera3D = _bg3d.get_camera() if _bg3d.has_method("get_camera") else null
	if cam == null:
		return
	cam.global_transform = marker.global_transform
	var fov := float(TYPE_FOV.get(shot_type, 50.0))
	if marker.has_meta("fov"):
		fov = float(marker.get_meta("fov"))
	cam.fov = fov
	cam.make_current()
	_start_drift(drift)


func _start_drift(drift: bool) -> void:
	_drifting = drift
	if drift:
		var cam: Camera3D = _bg3d.get_camera() if _bg3d != null and _bg3d.has_method("get_camera") else null
		if cam != null:
			_drift_floor = cam.fov * DRIFT_MIN_RATIO


func _process(delta: float) -> void:
	if _pending_shot != "":
		_try_apply_shot()
	if not _drifting:
		return
	if _bg3d == null or not is_instance_valid(_bg3d) or not _bg3d.has_method("get_camera"):
		_drifting = false
		return
	var cam: Camera3D = _bg3d.get_camera()
	if cam == null:
		_drifting = false
		return
	cam.fov = maxf(_drift_floor, cam.fov * (1.0 - DRIFT_RATE * delta))


# ── Letterbox ─────────────────────────────────────────────────────
func _set_letterbox(on: bool) -> void:
	if _bar_top == null:
		return
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
		return
	_dismiss_panel()
	var card := _build_panel_card(id)
	if card == null:
		return
	_panel_card = card
	_overlay_parent.add_child(card)


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
	if FileAccess.file_exists(path) and hero.load_from(path):
		var texr := TextureRect.new()
		# Integer-ish upscale of the pixel doc, capped to the upper
		# half of the screen so the dialog box stays clear.
		var scale_i: int = maxi(1, mini(int(900.0 / maxf(1.0, float(hero.w))), int(420.0 / maxf(1.0, float(hero.h)))))
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
	# Center in the upper field (dialog owns the bottom third). A
	# CenterContainer band does the layout math for us.
	var holder := CenterContainer.new()
	holder.set_anchors_preset(Control.PRESET_TOP_WIDE)
	holder.offset_top = 40.0
	holder.offset_bottom = 480.0
	holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	holder.z_index = 101
	holder.add_child(card)
	return holder
