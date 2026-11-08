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

var _wide_owners: Array[Node] = []
var px_scale: float = 1.0


func _ready() -> void:
	get_tree().root.size_changed.connect(_refresh)
	var st: Node = get_node_or_null("/root/Settings")
	if st != null and st.has_signal("settings_changed"):
		st.connect("settings_changed", _on_setting)
	_refresh.call_deferred()


## A surface that lays itself out for any width asks for the full screen;
## it is released automatically when it leaves the tree.
func request_wide(owner: Node) -> void:
	if owner == null or _wide_owners.has(owner):
		return
	_wide_owners.append(owner)
	owner.tree_exiting.connect(release_wide.bind(owner), CONNECT_ONE_SHOT)
	_refresh()


func release_wide(owner: Node) -> void:
	_wide_owners.erase(owner)
	_refresh()


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
	_wide_owners = _wide_owners.filter(func(n: Node) -> bool: return is_instance_valid(n))
	var fill: bool = true
	var st: Node = get_node_or_null("/root/Settings")
	if st != null and "wide_screens" in st:
		fill = String(st.get("wide_screens")) != "pillarbox"
	if fill and not _wide_owners.is_empty():
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
	layout_changed.emit()


func _on_setting(key: String, _val: Variant) -> void:
	if key == "wide_screens":
		_refresh()
