extends Control
## BgFrame — paints a matte over the aspect bars of the centered bg
## image and draws a thin gold rule along the image edge.
##
## The bg uses STRETCH_KEEP_ASPECT_CENTERED so the source is fully
## visible with letterbox/pillarbox where viewport aspect doesn't
## match. Without this frame, the live ASCII _substrate sits in
## those gaps. Frame computes the source's fitted rect, paints the
## four bar regions with the matte color, and outlines the image
## edge with a 1px gold rule for a "framed picture" feel.

const C_MATTE   := Color(0.039, 0.031, 0.020)        # near-black, matches scene_bg
const C_RULE    := Color(0.70, 0.55, 0.24, 0.55)     # muted gold
const RULE_W    := 1.0

var bg_node: TextureRect = null


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	resized.connect(queue_redraw)


func _process(_delta: float) -> void:
	# Bg image breathes via zoom — keeps the rule hugging the edge.
	# Negligible work: 4 rect fills + 1 outline.
	queue_redraw()


func _draw() -> void:
	if bg_node == null or bg_node.texture == null:
		return
	var tex_sz := bg_node.texture.get_size()
	if tex_sz.x <= 0.0 or tex_sz.y <= 0.0:
		return
	var view := size
	# Fit (KEEP_ASPECT_CENTERED) — scale to whichever dim is smaller.
	var s := minf(view.x / tex_sz.x, view.y / tex_sz.y)
	# Account for the live zoom breath / sway applied to bg_node.
	var node_scale: float = bg_node.scale.x
	var draw_sz := tex_sz * s * node_scale
	var origin := (view - draw_sz) * 0.5 + bg_node.position

	# Paint matte over the four bar regions. We paint the full view
	# minus the image rect by drawing four rectangles; simpler than
	# computing a hole-shape.
	#  ┌─────────────┐
	#  │     top     │
	#  ├──┬───────┬──┤
	#  │L │  bg   │ R│
	#  ├──┴───────┴──┤
	#  │   bottom    │
	#  └─────────────┘
	var l := origin.x
	var t := origin.y
	var r := origin.x + draw_sz.x
	var b := origin.y + draw_sz.y
	if t > 0.0:
		draw_rect(Rect2(0.0, 0.0, view.x, t), C_MATTE, true)
	if b < view.y:
		draw_rect(Rect2(0.0, b, view.x, view.y - b), C_MATTE, true)
	if l > 0.0:
		draw_rect(Rect2(0.0, t, l, b - t), C_MATTE, true)
	if r < view.x:
		draw_rect(Rect2(r, t, view.x - r, b - t), C_MATTE, true)

	# Thin gold rule along the image edge.
	draw_rect(Rect2(l, t, r - l, b - t), C_RULE, false, RULE_W)
