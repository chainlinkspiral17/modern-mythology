extends Control
## AsciiSubstrate — full-viewport ASCII grid that sits at the bottom of the
## GameEngine layer stack. Acts as the "machine substrate" beneath whatever
## richer media (bg textures, character portraits, video) layers above.
##
## Renders the half-block ANSI mosaic by calling `draw_rect` for every cell
## directly inside `_draw()`. NO BBCode parsing, NO RichTextLabel, NO PNG
## file caching. Drawing happens once per substrate load (via `queue_redraw`);
## subsequent frames just re-blit the canvas items.
##
## Grid JSONs live at res://resources/substrates/<short_path>.json and use
## the same {width, height, cells:[[{c,fg,bg}]]} schema as the mosaic tooling.

const SUBSTRATE_ROOT := "res://resources/substrates/"

# Pixel size per cell. 4×8 keeps the rendered grid small and fast.
# CELL_H must be even (half-block ▀ splits in half).
@export var cell_w: int = 4
@export var cell_h: int = 8

var _cells: Array = []
var _bg_color: Color = Color(0.02, 0.025, 0.05, 1.0)
var _current_path: String = ""


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	resized.connect(queue_redraw)


func load_substrate(short_path: String) -> void:
	if short_path == "":
		clear_substrate()
		return
	var full_path: String = SUBSTRATE_ROOT + short_path + ".json"
	if not FileAccess.file_exists(full_path):
		push_warning("AsciiSubstrate: not found: " + full_path)
		clear_substrate()
		return
	var f := FileAccess.open(full_path, FileAccess.READ)
	if f == null:
		return
	var data: Variant = JSON.parse_string(f.get_as_text())
	if typeof(data) != TYPE_DICTIONARY or not (data as Dictionary).has("cells"):
		push_warning("AsciiSubstrate: invalid grid: " + full_path)
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
		# Fill viewport with default bg so the substrate slot isn't black
		# when nothing's loaded
		draw_rect(Rect2(Vector2.ZERO, size), _bg_color)
		return
	var rows: int = _cells.size()
	var cols: int = 0
	for r in _cells:
		var rn: int = (r as Array).size()
		if rn > cols: cols = rn
	# Auto-fit cell pixel size to this Control's current size so the grid
	# always fills the viewport regardless of mosaic resolution
	var fit_cw: float = max(1.0, size.x / float(cols))
	var fit_ch: float = max(1.0, size.y / float(rows))
	var half_h: float = fit_ch * 0.5

	# Solid backdrop fill (catches any cells that don't draw their own bg)
	draw_rect(Rect2(Vector2.ZERO, size), _bg_color)

	for y in range(rows):
		var row: Array = _cells[y]
		var py: float = y * fit_ch
		for x in range(row.size()):
			var cell: Variant = row[x]
			if typeof(cell) != TYPE_DICTIONARY:
				continue
			var c: String = str((cell as Dictionary).get("c", " "))
			var fg_v: Variant = (cell as Dictionary).get("fg")
			var bg_v: Variant = (cell as Dictionary).get("bg")
			var fg: Color = Color(str(fg_v)) if fg_v != null else Color.WHITE
			var bg: Color = Color(str(bg_v)) if bg_v != null else _bg_color
			var px: float = x * fit_cw
			# Half-block characters carry two colors per cell.
			# ▀ U+2580 upper half block: top half FG, bottom half BG
			# ▄ U+2584 lower half block: top half BG, bottom half FG
			# █ U+2588 full block      : whole cell FG
			# " " space                 : whole cell BG
			# anything else             : whole cell FG (glyph approx)
			if c == "▀":
				draw_rect(Rect2(px, py, fit_cw, half_h), fg)
				draw_rect(Rect2(px, py + half_h, fit_cw, fit_ch - half_h), bg)
			elif c == "▄":
				draw_rect(Rect2(px, py, fit_cw, half_h), bg)
				draw_rect(Rect2(px, py + half_h, fit_cw, fit_ch - half_h), fg)
			elif c == " ":
				if bg_v != null:
					draw_rect(Rect2(px, py, fit_cw, fit_ch), bg)
				# else: backdrop already painted
			else:
				draw_rect(Rect2(px, py, fit_cw, fit_ch), fg)
