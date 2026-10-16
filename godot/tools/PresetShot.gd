extends SceneTree
## PRESET SHOT (2026-10-16): one frame per Background3D camera preset, by
## name — for a new set whose presets no chapter on this branch plays yet
## (the vols 1-4 sets: their scenes live on claude/vol1-4-source-text), so
## the contact sheet's manifest does not list them.
##
##   xvfb-run -a godot --path godot --rendering-driver opengl3 \
##     --resolution 1280x720 --script res://tools/PresetShot.gd -- \
##     OUT_DIR preset_a preset_b …
##
## Writes OUT_DIR/<preset>.png through the same Background3D node the VN
## uses (lights, per-preset env, the locale's own post stack, StaticMerge).
## Not HUD: nothing joins "ui"; quits when done.

const BG3D := preload("res://scenes/vn/Background3D.tscn")
const SETTLE_FRAMES := 24

var _out: String = ""
var _presets: Array = []
var _i: int = -1
var _bg: Node = null
var _frames: int = 0


func _initialize() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() < 2:
		push_error("PresetShot: OUT_DIR preset …")
		quit(1)
		return
	_out = args[0]
	DirAccess.make_dir_recursive_absolute(_out)
	for k in range(1, args.size()):
		_presets.append(args[k])
	_bg = BG3D.instantiate()
	root.add_child(_bg)          # its _ready (the SubViewport, the anchor) runs before the first frame


var _started: bool = false


func _next() -> void:
	_i += 1
	if _i >= _presets.size():
		quit(0)
		return
	var ok: bool = bool(_bg.call("load_location", String(_presets[_i])))
	print("[PresetShot] %s %s" % [_presets[_i], "loaded" if ok else "FAILED: " + String(_bg.get("last_load_error"))])
	_frames = 0
	if not ok:
		_next()


func _process(_dt: float) -> bool:
	if not _started:
		_started = true
		_next()
		return false
	if _i < 0 or _i >= _presets.size():
		return false
	_frames += 1
	if _frames == SETTLE_FRAMES:
		var tex: Texture2D = _bg.call("get_viewport_texture")
		var img: Image = tex.get_image() if tex != null else null
		if img != null:
			img.save_png(_out.path_join(String(_presets[_i]) + ".png"))
		_next()
	return false
