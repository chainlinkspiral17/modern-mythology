extends Control
class_name TitleMotion
## Title screens that breathe · see lore/_MENU_MOTION_PLAYBOOK.md.
##
## A motion layer a host drops over its title art: drifting motes,
## a shimmer pass crossing the frame, optional practical-light
## flicker points. Living pixel art, not UI tweens — everything
## draws snapped to a coarse pixel grid so motion lands on the art's
## own resolution. Budget rule: 2-3 effects per screen; restraint
## IS the studio character (ranch flickers, homebrew only blinks).
##
## Usage (preload by path — new class_names miss the first editor
## scan after a pull):
##   const TITLE_MOTION := preload("res://scenes/games/TitleMotion.gd")
##   TITLE_MOTION.attach(_title_root, "rocha_faire")
## Optional practicals:
##   var m := TITLE_MOTION.attach(_title_root, "sagebrush")
##   m.flicker_points = [Vector2(400, 300), ...]
##
## The layer ignores the mouse and sits wherever it is added in the
## child order — attach it right after the title art, before the
## button column, so effects pass over the picture and under the UI.

# Per-studio motion character. mote_px = the coarse grid the motes
# snap to (match the title art's upscale factor, roughly).
const PRESETS: Dictionary = {
	"rocha_faire": {   # pollen over the faire, warm shimmer
		"motes": 26, "mote_color": Color(0.95, 0.88, 0.62, 0.55),
		"drift": Vector2(9, -4), "mote_px": 4,
		"shimmer_color": Color(1.0, 0.95, 0.85, 0.07), "shimmer_period": 9.0},
	"sagebrush": {     # dust on the wind, heat-pale shimmer
		"motes": 30, "mote_color": Color(0.86, 0.72, 0.52, 0.45),
		"drift": Vector2(16, -1), "mote_px": 4,
		"shimmer_color": Color(1.0, 0.9, 0.75, 0.05), "shimmer_period": 12.0},
	"astro_cortex": {  # star drift, instrument-cool shimmer
		"motes": 18, "mote_color": Color(0.78, 0.82, 0.92, 0.5),
		"drift": Vector2(-3, 2), "mote_px": 3,
		"shimmer_color": Color(0.8, 0.9, 1.0, 0.05), "shimmer_period": 11.0},
	"oneironautics": { # fireflies over the water
		"motes": 14, "mote_color": Color(0.98, 0.92, 0.55, 0.6),
		"drift": Vector2(4, -6), "mote_px": 4,
		"shimmer_color": Color(0, 0, 0, 0), "shimmer_period": 9.0},
	"ranch": {         # commercial restraint · flicker only
		"motes": 0, "mote_color": Color(0, 0, 0, 0),
		"drift": Vector2.ZERO, "mote_px": 4,
		"shimmer_color": Color(0, 0, 0, 0), "shimmer_period": 9.0},
	"homebrew": {      # one blinking cursor (host places it)
		"motes": 0, "mote_color": Color(0, 0, 0, 0),
		"drift": Vector2.ZERO, "mote_px": 4,
		"shimmer_color": Color(0, 0, 0, 0), "shimmer_period": 9.0},
	"shelf": {         # cabin grain drifting in lamplight
		"motes": 20, "mote_color": Color(0.9, 0.8, 0.6, 0.30),
		"drift": Vector2(3, -5), "mote_px": 4,
		"shimmer_color": Color(1.0, 0.9, 0.7, 0.04), "shimmer_period": 14.0},
}

var preset_name: String = "shelf"
var flicker_points: Array = []          # Vector2s · practicals that breathe
var flicker_color: Color = Color(0.98, 0.85, 0.5, 0.8)

var _cfg: Dictionary = {}
var _t: float = 0.0
var _motes: Array = []                  # {p: Vector2, spd: float, ph: float}


static func attach(root: Control, preset: String) -> Control:
	var script: GDScript = load("res://scenes/games/TitleMotion.gd")
	var m: Control = script.new()
	m.set("preset_name", preset)
	m.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	m.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(m)
	return m


func _ready() -> void:
	_cfg = PRESETS.get(preset_name, PRESETS["shelf"])
	var n: int = _cfg["motes"]
	for i in range(n):
		_motes.append({
			"p": Vector2(_h01(i, 1) * 1280.0, _h01(1, i) * 720.0),
			"spd": 0.6 + _h01(i, 7) * 0.9,
			"ph": _h01(i, 13) * TAU,
		})


func _process(delta: float) -> void:
	if not is_visible_in_tree():
		return
	_t += delta
	queue_redraw()


func _draw() -> void:
	var sz := size
	if sz.x < 2.0 or sz.y < 2.0:
		return
	var grid: float = float(_cfg.get("mote_px", 4))
	var drift: Vector2 = _cfg["drift"]
	var mote_col: Color = _cfg["mote_color"]
	# motes — drifting, twinkling, wrapped, snapped to the grid
	for m_v in _motes:
		var m: Dictionary = m_v
		var base: Vector2 = m["p"]
		var spd: float = m["spd"]
		var pos := Vector2(
			fposmod(base.x + drift.x * _t * spd * 4.0, sz.x),
			fposmod(base.y + drift.y * _t * spd * 4.0, sz.y))
		pos = (pos / grid).floor() * grid
		var c := mote_col
		c.a = mote_col.a * (0.45 + 0.55 * absf(sin(_t * 1.7 + float(m["ph"]))))
		draw_rect(Rect2(pos, Vector2(grid, grid)), c)
	# shimmer — a slanted light band crossing every period
	var sh_col: Color = _cfg["shimmer_color"]
	if sh_col.a > 0.0:
		var period: float = _cfg["shimmer_period"]
		var travel: float = fposmod(_t, period) / period
		var band_x: float = travel * (sz.x + 400.0) - 200.0
		var w := 90.0
		var pts := PackedVector2Array([
			Vector2(band_x, 0), Vector2(band_x + w, 0),
			Vector2(band_x + w - 120.0, sz.y), Vector2(band_x - 120.0, sz.y)])
		draw_colored_polygon(pts, sh_col)
	# practicals — flicker points the host placed over its own art
	for fp_v in flicker_points:
		var fp: Vector2 = fp_v
		var fc := flicker_color
		fc.a = flicker_color.a * (0.55 + 0.45 * _h01(int(_t * 9.0), int(fp.x)))
		var snapped_fp := (fp / grid).floor() * grid
		draw_rect(Rect2(snapped_fp, Vector2(grid, grid)), fc)


func _h01(x: int, y: int) -> float:
	var n: int = x * 374761393 + y * 668265263 + 12345
	n = (n ^ (n >> 13)) * 1274126177
	return float((n ^ (n >> 16)) & 0xFFFF) / 65536.0
