extends Control
class_name HeroParallax
## 2.5D parallax backdrop: stacks HeroImage planes at depth and drifts
## them, so a flat vector backdrop gains layered motion without leaving
## the silkscreen look.
##
## Each plane is an oversized, NEAREST-filtered TextureRect built from a
## HeroImage JSON. A slow idle sway (time sine) plus an optional external
## drive (walk progress, tilt, mouse) offsets each plane by its own
## `parallax` factor — far planes barely move, near planes lead. Near
## planes should carry a TRANSPARENT sky (palette entry "transparent")
## so the planes behind them show through as everything drifts.
##
## It is the PICTURE, not HUD: joins "world_render" (the F4 escape-hatch
## group) so a screenshot keeps the backdrop. Add it low in the tree so
## the stick's UI draws over it, then (optionally) SlowstickLook on top.
##
## Usage (host _ready, behind the UI):
##   var bg := HeroParallax.new()
##   bg.build([
##     {"json": DIR + "the_walk_far.json",  "parallax": 0.25, "sway": 3.0},
##     {"json": DIR + "the_walk_near.json", "parallax": 1.00, "sway": 7.0},
##   ], get_viewport_rect().size)
##   add_child(bg)   # add before the UI layers
##   # per-frame, optionally: bg.set_drive(Vector2(walk01 * 40.0, 0))

const OVERSCAN := 1.14           # planes 14% larger so drift never bares an edge
const SWAY_SPEED := 0.18         # idle sway cycles/sec (slow, ambient)

var _planes: Array = []          # [{rect, parallax, sway, base}]
var _t: float = 0.0
var _drive: Vector2 = Vector2.ZERO


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_to_group("world_render")   # it's the picture; F4 leaves it alone


func build(plane_defs: Array, view_size: Vector2) -> void:
	for c in get_children():
		c.queue_free()
	_planes.clear()
	var over: Vector2 = view_size * OVERSCAN
	var base: Vector2 = -(over - view_size) * 0.5   # centre the overscan
	for def_v in plane_defs:
		var def: Dictionary = def_v
		var hero := HeroImage.new()
		if not hero.load_from(String(def.get("json", ""))):
			continue
		var tr := TextureRect.new()
		tr.texture = hero.texture(Vector2i(int(over.x), int(over.y)))
		tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
		tr.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
		tr.size = over
		tr.position = base
		add_child(tr)
		_planes.append({
			"rect": tr,
			"parallax": float(def.get("parallax", 0.5)),
			"sway": float(def.get("sway", 4.0)),
			"base": base,
		})


## External drive in pixels (e.g. walk progress mapped to a horizontal
## push). Multiplied by each plane's parallax factor. Zero by default.
func set_drive(v: Vector2) -> void:
	_drive = v


func _process(delta: float) -> void:
	if _planes.is_empty():
		return
	_t += delta
	var phase: float = _t * SWAY_SPEED * TAU
	for p_v in _planes:
		var p: Dictionary = p_v
		var sway: Vector2 = Vector2(sin(phase) * p["sway"], cos(phase * 0.6) * p["sway"] * 0.4)
		var off: Vector2 = (sway + _drive) * p["parallax"]
		(p["rect"] as TextureRect).position = (p["base"] as Vector2) + off
