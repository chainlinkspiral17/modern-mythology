## ScreenMgr — every screen shape, from the Deck to a 21:9 ultrawide (2026-11-08).
##
## The game is laid out on a 1280x720 canvas (project.godot, stretch mode
## canvas_items: the UI is re-rasterised at the window's real resolution,
## so text stays sharp at 1440p). How the canvas meets a screen of another
## SHAPE is decided per surface:
##
##   * a surface that has been made WIDE-READY calls request_wide(self):
##     while it is up, the canvas EXPANDS to the screen's shape (720 tall,
##     1720 wide on 21:9; 800 tall on the Deck's 16:10) and the surface
##     uses the extra room itself — the VN spends it on panoramic
##     backgrounds, keeping its text and portraits in the centre band;
##   * every other surface keeps the 16:9 frame, pillarboxed (or
##     letterboxed), exactly as it was designed and tested.
##
## The player can turn the fill off (Settings.wide_screens = "pillarbox").
##
## PIXEL SCALE: the painted / ASCII / dither shaders were tuned with one
## screen pixel per canvas unit (the Deck). At 1440p a "4 px" brush would
## be half as wide. `px_scale` (a global shader uniform, declared in
## project.godot [shader_globals]) is the window's pixels per canvas unit;
## those shaders multiply their pixel lengths by it.
extends Node

signal layout_changed

const DESIGN := Vector2(1280.0, 720.0)

var _last_described: String = ""
var px_scale: float = 1.0


func _ready() -> void:
	get_tree().root.size_changed.connect(_refresh)
	var st: Node = get_node_or_null("/root/Settings")
	if st != null and st.has_signal("settings_changed"):
		st.connect("settings_changed", _on_setting)
	_refresh.call_deferred()


## A surface that lays itself out for any width asks for the full screen.
## (2026-11-09) It is a GROUP now ("wide_ready"), read fresh on every
## refresh: the request was a one-shot list entry dropped the first time the
## surface left the tree, and nothing put it back — a state nobody could see
## from outside. A node in the group that is in the tree fills the screen.
const WIDE_GROUP := "wide_ready"


func request_wide(owner: Node) -> void:
	if owner == null:
		return
	if not owner.is_in_group(WIDE_GROUP):
		owner.add_to_group(WIDE_GROUP)
		owner.tree_entered.connect(_refresh_deferred)
		owner.tree_exited.connect(_refresh_deferred)
	_refresh()


func release_wide(owner: Node) -> void:
	if owner != null and owner.is_in_group(WIDE_GROUP):
		owner.remove_from_group(WIDE_GROUP)
	_refresh()


func _refresh_deferred() -> void:
	if is_inside_tree():
		_refresh.call_deferred()


func _wide_surface_up() -> bool:
	for n: Node in get_tree().get_nodes_in_group(WIDE_GROUP):
		if is_instance_valid(n) and n.is_inside_tree() and not n.is_queued_for_deletion():
			return true
	return false


func _fill_setting() -> bool:
	var st: Node = get_node_or_null("/root/Settings")
	if st != null and "wide_screens" in st:
		return String(st.get("wide_screens")) != "pillarbox"
	return true


## What the screen is doing, in a sentence — shown in Settings under SCREEN
## SIZE and printed to the log on every change, so "it isn't taking" can be
## read off the screen instead of guessed at.
func describe() -> String:
	var root: Window = get_tree().root
	var win: Vector2i = root.size
	var scr: Vector2i = DisplayServer.screen_get_size(DisplayServer.window_get_current_screen())
	var mode: String = "windowed"
	match root.mode:
		Window.MODE_MAXIMIZED: mode = "maximised"
		Window.MODE_FULLSCREEN, Window.MODE_EXCLUSIVE_FULLSCREEN: mode = "fullscreen"
	if root.borderless and win == scr:
		mode = "fullscreen (borderless)"
	if Engine.is_embedded_in_editor():
		mode = "inside the Godot editor's Game tab"
	var shape: String = "16:9"
	if win.y > 0:
		var r: float = float(win.x) / float(win.y)
		if r > 1.9:
			shape = "wide (%.2f:1)" % r
		elif r < 1.7:
			shape = "%.2f:1" % r
	var story: String
	if not _fill_setting():
		story = "the story keeps a 16:9 frame because WIDE SCREENS is on PILLARBOX"
	elif win.y > 0 and float(win.x) / float(win.y) < 1.79:
		story = "the window is 16:9 — nothing wider to fill"
	elif is_wide_active():
		story = "the story fills the width"
	else:
		story = "this page keeps a 16:9 frame; the story fills the width once a chapter is up"
	return "Window %d×%d, %s, on a %d×%d screen · %s. %s." % [win.x, win.y, mode, scr.x, scr.y, shape, story.substr(0, 1).to_upper() + story.substr(1)]


func is_wide_active() -> bool:
	return get_tree().root.content_scale_aspect == Window.CONTENT_SCALE_ASPECT_EXPAND


## The canvas size the current surface lays out in (1280x720 when
## pillarboxed; e.g. 1720x720 on 21:9 when wide).
func canvas_size() -> Vector2:
	return get_tree().root.get_visible_rect().size


## The 16:9 band in the middle of the canvas (canvas units): where the
## text and the portraits stay on any screen.
func center_band() -> Rect2:
	var sz: Vector2 = canvas_size()
	var w: float = minf(sz.x, sz.y * DESIGN.x / DESIGN.y)
	return Rect2(Vector2((sz.x - w) * 0.5, 0.0), Vector2(w, sz.y))


func _wanted_aspect() -> int:
	if _fill_setting() and _wide_surface_up():
		return Window.CONTENT_SCALE_ASPECT_EXPAND
	return Window.CONTENT_SCALE_ASPECT_KEEP


func _refresh() -> void:
	var root: Window = get_tree().root
	var want: int = _wanted_aspect()
	if root.content_scale_aspect != want:
		root.content_scale_aspect = want
	var win: Vector2 = Vector2(root.size)
	var vis: Vector2 = root.get_visible_rect().size
	var k: float = 1.0
	if vis.y > 0.0:
		k = maxf(win.y / vis.y, 1.0)
	if not is_equal_approx(k, px_scale):
		px_scale = k
	RenderingServer.global_shader_parameter_set("px_scale", px_scale)
	var now: String = describe()
	if now != _last_described:
		_last_described = now
		print("[ScreenMgr] ", now)
	layout_changed.emit()


func _on_setting(key: String, _val: Variant) -> void:
	if key == "wide_screens":
		_refresh()
