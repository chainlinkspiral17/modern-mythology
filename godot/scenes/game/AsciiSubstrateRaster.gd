extends Control
## AsciiSubstrateRaster — ASCII grid renderer using direct canvas drawing.
##
## Reads the mosaic JSON, then renders every cell as two filled rectangles
## (top half FG, bottom half BG — the half-block ▀ convention) directly via
## `_draw`. No BBCode parser, no RichTextLabel, no baked-PNG companion.
##
## Use this for gallery items and any zoom-out reveal of a mosaic. For
## in-engine substrates that swap with scene flow use AsciiSubstrate.

const SUBSTRATE_ROOT := "res://resources/substrates/"

var _cells: Array = []
var _bg_color: Color = Color(0.02, 0.03, 0.06, 1.0)
var _current_path: String = ""

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	resized.connect(queue_redraw)


# ── Public API ───────────────────────────────────────────────────────────────

func load_substrate(short_path: String) -> void:
	if short_path == "":
		clear_substrate()
		return
	var full_path: String = SUBSTRATE_ROOT + short_path + ".json"
	if not FileAccess.file_exists(full_path):
		push_warning("AsciiSubstrateRaster: not found: " + full_path)
		clear_substrate()
		return
	var f := FileAccess.open(full_path, FileAccess.READ)
	if f == null: return
	var data: Variant = JSON.parse_string(f.get_as_text())
	if typeof(data) != TYPE_DICTIONARY or not (data as Dictionary).has("cells"):
		push_warning("AsciiSubstrateRaster: invalid grid: " + full_path)
		return
	_current_path = short_path
	_cells = (data as Dictionary).get("cells", [])
	if (data as Dictionary).has("bg"):
		_bg_color = Color(str(data["bg"]))
	queue_redraw()


func clear_substrate() -> void:
	_current_path = ""
	_cells = []
	queue_redraw()


func current_substrate() -> String:
	return _current_path


# ── Rendering ────────────────────────────────────────────────────────────────

func _draw() -> void:
	if _cells.is_empty():
		draw_rect(Rect2(Vector2.ZERO, size), _bg_color)
		return
	var rows: int = _cells.size()
	var cols: int = 0
	for r in _cells:
		var rn: int = (r as Array).size()
		if rn > cols: cols = rn
	# Letterbox-fit the grid to this Control's size so the rendered image
	# preserves aspect.
	var grid_aspect: float = float(cols) / float(rows) * 0.5  # half-block tall
	var view_aspect: float = size.x / size.y
	var draw_w: float
	var draw_h: float
	if view_aspect > grid_aspect:
		draw_h = size.y
		draw_w = draw_h * grid_aspect
	else:
		draw_w = size.x
		draw_h = draw_w / grid_aspect
	var off_x: float = (size.x - draw_w) * 0.5
	var off_y: float = (size.y - draw_h) * 0.5
	var fit_cw: float = draw_w / float(cols)
	var fit_ch: float = draw_h / float(rows)
	var half_h: float = fit_ch * 0.5

	draw_rect(Rect2(Vector2.ZERO, size), _bg_color)

	for y in range(rows):
		var row: Array = _cells[y]
		var py: float = off_y + y * fit_ch
		for x in range(row.size()):
			var cell: Variant = row[x]
			if typeof(cell) != TYPE_DICTIONARY: continue
			var c: String = str((cell as Dictionary).get("c", " "))
			var fg_v: Variant = (cell as Dictionary).get("fg")
			var bg_v: Variant = (cell as Dictionary).get("bg")
			var fg: Color = Color(str(fg_v)) if fg_v != null else Color.WHITE
			var bg: Color = Color(str(bg_v)) if bg_v != null else _bg_color
			var px: float = off_x + x * fit_cw
			if c == "▀":
				draw_rect(Rect2(px, py, fit_cw, half_h), fg)
				draw_rect(Rect2(px, py + half_h, fit_cw, fit_ch - half_h), bg)
			elif c == "▄":
				draw_rect(Rect2(px, py, fit_cw, half_h), bg)
				draw_rect(Rect2(px, py + half_h, fit_cw, fit_ch - half_h), fg)
			elif c == " ":
				if bg_v != null:
					draw_rect(Rect2(px, py, fit_cw, fit_ch), bg)
			else:
				draw_rect(Rect2(px, py, fit_cw, fit_ch), fg)
