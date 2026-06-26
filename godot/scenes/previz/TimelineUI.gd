class_name TimelineUI
extends Control
## A drawn timeline strip across the bottom of the screen: one row per track
## (camera, each object track, audio, ref), keyframe ticks positioned by time,
## a moving playhead, and a transport readout. Read-only view for now; editing
## is via keys in Previz.gd (click-to-seek/scrub comes with the technician
## console phase).

var timeline: Timeline
var sel_label := ""


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_layout()


func _layout() -> void:
	var vp := get_viewport().get_visible_rect().size
	position = Vector2(0.0, vp.y - 132.0)
	size = Vector2(vp.x, 132.0)


func _process(_delta: float) -> void:
	queue_redraw()


func _draw() -> void:
	if timeline == null:
		return
	_layout()
	var w := size.x
	var h := size.y
	var font := ThemeDB.fallback_font
	draw_rect(Rect2(0.0, 0.0, w, h), Color(0.0, 0.0, 0.0, 0.55))

	var pad := 96.0
	var tw := w - pad - 18.0
	var dur := maxf(timeline.duration, 1.0)

	var rows: Array = []
	rows.append(["CAMERA", _times(timeline.cam_keys)])
	for id in timeline.obj_tracks:
		rows.append([str(id).to_upper(), _times(timeline.obj_tracks[id])])
	rows.append(["AUDIO", _times(timeline.audio_cues)])
	rows.append(["REF", _times(timeline.ref_cues)])

	var top := 24.0
	var rh := (h - top - 8.0) / float(maxi(rows.size(), 1))
	for i in rows.size():
		var y := top + float(i) * rh
		var cy := y + rh * 0.5
		draw_string(font, Vector2(8.0, cy + 4.0), rows[i][0], HORIZONTAL_ALIGNMENT_LEFT, 84, 12, Color(0.8, 0.75, 0.6))
		draw_line(Vector2(pad, cy), Vector2(pad + tw, cy), Color(1.0, 1.0, 1.0, 0.12), 1.0)
		for tt in rows[i][1]:
			var x := pad + (float(tt) / dur) * tw
			draw_circle(Vector2(x, cy), 3.5, Color(0.9, 0.72, 0.32))

	var px := pad + (timeline.time / dur) * tw
	draw_line(Vector2(px, top - 6.0), Vector2(px, h - 6.0), Color(1.0, 0.8, 0.3), 2.0)

	var head := "t %.1f / %.1f s   %s   target: %s" % [
		timeline.time, dur, ("PLAY" if timeline.playing else "STOP"), sel_label
	]
	draw_string(font, Vector2(8.0, 16.0), head, HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color(1.0, 0.9, 0.7))


func _times(arr: Array) -> Array:
	var out: Array = []
	for k in arr:
		out.append(float(k["t"]))
	return out
