extends "res://scenes/menu/DioramaBase.gd"
## DeathWardDiorama — Ward C, night-shift handover, 06:00.
##
## Six bed hotspots + one nursing station. Each click reveals the
## night-nurse's note and fires a SaveSystem unlock; three of those
## wake gated hotspots on Hanged Man / Justice / Emperor.
##
## Lore framing: the chapter's documents are being PULLED by the
## demonic substrate (warehouse demons of Magician I; UNCOMFORTABLE
## INSIDE status of Devil XV; demoscene engine of Tower XVI). The
## diorama opens with a faint daemon-fetch banner; the ambient
## carries a subtle digital-substrate tick under the fluorescent
## hum.
##
## See pitches/13_death.md for the source script.

const C_PINK := Color(0.95, 0.62, 0.66)

const _BEDS := [
	{
		"id": "ward_bed_1",
		"label": "[1] Mrs. P, 78",
		"rect": [0.10, 0.30, 0.10, 0.10],
		"report": "stable. slept through. pain 2/10. IV due 07:30.\nfluids ok.",
		"unlocks": "vol5_ward_c_bed1_seen",
	},
	{
		"id": "ward_bed_2",
		"label": "[2] Mr. K, 64",
		"rect": [0.24, 0.30, 0.10, 0.10],
		"report": "restless. paged me at 02:14 and 03:48. complained\nof the lights. the lights were off. i sat with him\nfor the second one. eight minutes. he was looking\nat the ceiling and asking if it was the ceiling. it\nwas the ceiling. he went back to sleep.",
		"unlocks": "vol5_ward_c_bed2_seen",
	},
	{
		"id": "ward_bed_3",
		"label": "[3] VACANT — CASE 1",
		"rect": [0.38, 0.30, 0.10, 0.10],
		"report": "code at 23:47. attending: dr. v. arrived 03:12.\nduration 1h44m. outcome: time of death 01:31.\nfamily notified by phone at 02:08. mother and one\nbrother. no spouse listed. chart is in the bin.\npaperwork on the shelf. the brother is coming this\nmorning. he has been driving since 02:30. don't put\nhim in the family room. the family room is being\nrepainted. use the chaplain's room. the chaplain is\nnot in today.",
		"unlocks": "vol5_ward_c_bed3_seen",
	},
	{
		"id": "ward_bed_4",
		"label": "[4] VACANT — CASE 2",
		"rect": [0.52, 0.30, 0.10, 0.10],
		"report": "NOT a code. Mr. S. discharged himself at 03:55 AMA.\nsigned all the forms. walked out wearing the gown.\nleft the gown on the door at the end of the hall,\nput on his street clothes from the bag, left through\nthe south exit. i did not stop him. i do not think i\nwas supposed to stop him. the night supervisor agreed.\npaperwork is on the shelf. he will be back. he will\nnot be back tonight.\n\nflag his chart for the day team. note: he asked me\nat 03:30 whether the candle had gone out. i do not\nknow what candle he meant. he was lucid. he said it\nlike it was a question i should be able to answer.\ni could not. he discharged himself twenty-five\nminutes later.",
		"unlocks": "vol5_ward_c_simon_walkout_seen",
	},
	{
		"id": "ward_bed_5",
		"label": "[5] Mrs. R, 81",
		"rect": [0.66, 0.30, 0.10, 0.10],
		"report": "comfortable. family stayed until 22:00. they will be\nback at 09. tell them she asked for the radio. give\nher the radio.",
		"unlocks": "vol5_ward_c_marta_present",
	},
	{
		"id": "ward_bed_6",
		"label": "[6] Mr. D, 70",
		"rect": [0.80, 0.50, 0.10, 0.10],
		"report": "vitals attached. nothing changed tonight. nothing\nchanged all week. he is doing what he is doing. he\nknows. don't talk to him about the weather. talk to\nhim about his daughter. she is a dentist in asheville.\nthat is the topic.",
		"unlocks": "vol5_ward_c_dante_present",
	},
	{
		"id": "ward_station",
		"label": "NURSING STATION — full report",
		"rect": [0.32, 0.62, 0.30, 0.10],
		"report": "HANDOVER NOTES:\n\n· the empty beds 3 and 4 are not the same kind of\n  empty. mark it on the assignment board. one bed\n  needs a clean. one bed needs a clean and a strip.\n\n· mrs. r.'s radio.\n\n· the brother in bed 3's chaplain room.\n\n· mr. d., the asheville dentist daughter.\n\n· mr. k., do not turn on the lights, he will notice.\n\ni am off until tuesday. e.s.\n\n[NOTE TO DAY SHIFT, separate page:\n attending physician for last night's code was\n DR. V. — full surname withheld on this form per\n protocol. day team can pull the chart for the\n attending of record. — e.s.]",
		"unlocks": "vol5_ward_c_full_report_read",
	},
]

const ASCII_LAYOUT := """\

					WARD C  ·  NIGHT SHIFT  ·  06:00 SIGN-OFF

   ╭─────────────────────────────────────────────────────────────────╮
   │                                                                 │
   │                                                                 │
   │   ┌─[1]─┐   ┌─[2]─┐   ┌─[3]─┐   ┌─[4]─┐   ┌─[5]─┐               │
   │   │Mrs.P│   │Mr.K │   │EMPTY│   │EMPTY│   │Mrs.R│               │
   │   │ 78  │   │ 64  │   │     │   │     │   │ 81  │               │
   │   └──┬──┘   └──┬──┘   └──┬──┘   └──┬──┘   └──┬──┘               │
   │      │         │         ·         ·         │                  │
   │      ·         ·                             ·                  │
   │                                                                 │
   │           ─────  NURSING STATION  ─────                         │
   │             [click for full report]                             │
   │                                                                 │
   │                                                                 │
   │                                                ┌─[6]─┐          │
   │                                                │Mr.D │          │
   │                                                │ 70  │          │
   │                                                └──┬──┘          │
   │                                                   ·             │
   │                                                                 │
   │   east window:                                                  │
   │      pink dusk leaking through the blinds                       │
   │                                                                 │
   ╰─────────────────────────────────────────────────────────────────╯

					e.s.  //  r.n.  //  bed 4-9 night shift
								off until tuesday
"""

# Ambient state — fluorescent hum + IV pings + faint daemon tick
var _amb_phase: float = 0.0
var _ping_active: Array = []
var _next_ping_at: float = 2.0


func _init() -> void:
	_diorama_title = "WARD C  ·  XIII THE DEATH  ·  night-shift handover"
	_diorama_hint = "click a bed or the station · esc to leave"
	_edge_wash_color = Color(C_PINK.r, C_PINK.g, C_PINK.b, 0.04)


func _build_content() -> void:
	var diorama := PanelContainer.new()
	diorama.set_anchors_preset(Control.PRESET_CENTER)
	diorama.offset_left = -540; diorama.offset_right = 540
	diorama.offset_top = -340; diorama.offset_bottom = 340
	diorama.mouse_filter = Control.MOUSE_FILTER_PASS
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.012, 0.008, 0.014, 0.94)
	sb.border_color = C_GOLD
	sb.set_border_width_all(1)
	diorama.add_theme_stylebox_override("panel", sb)
	add_child(diorama)

	var label := Label.new()
	label.text = ASCII_LAYOUT
	label.add_theme_color_override("font_color", C_TEXT)
	label.add_theme_font_size_override("font_size", 12)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	diorama.add_child(label)

	for bed_v in _BEDS:
		var bed: Dictionary = bed_v
		var captured := bed
		make_hotspot(diorama, bed["rect"], str(bed["label"]),
			func() -> void: _on_bed(captured))

	# Daemon-fetch banner — small footer below the diorama,
	# acknowledges the document is being pulled from the demonic
	# substrate rather than naturally surfacing.
	var fetch := Label.new()
	fetch.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	fetch.offset_top = -28
	fetch.offset_bottom = -10
	fetch.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	fetch.text = "[demon_archivist.13 // ward_c.bbs // 7 records recovered // integrity 0.97]"
	fetch.add_theme_color_override("font_color", C_TEXT_DIM)
	fetch.add_theme_font_size_override("font_size", 12)
	fetch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(fetch)


func _on_bed(bed: Dictionary) -> void:
	reveal(str(bed["label"]), str(bed["report"]), str(bed.get("unlocks", "")))


# ── Ambient: 60 Hz buzz + IV pings + faint daemon tick ────────────
# The daemon tick (a very low 12 Hz click train) is the lore beat:
# the demonic substrate that pulled these records is audible at the
# threshold of perception. Each diorama's ambient carries a similar
# substrate signature so the player learns to hear it.

func _ambient_sample(phase: float, step: float) -> Vector2:
	_amb_phase += step
	var buzz := -0.04 if fmod(phase * 60.0, 1.0) < 0.5 else 0.04
	var noise := (randf() - 0.5) * 0.012
	var daemon_tick := 0.0
	var tick_phase := fmod(phase * 12.0, 1.0)
	if tick_phase < 0.02:
		daemon_tick = -0.06 * (1.0 - tick_phase / 0.02)
	var ping_sum := 0.0
	var rem: Array = []
	for p in _ping_active:
		p.time += step
		if p.time < p.dur:
			var env: float = clamp(1.0 - p.time / p.dur, 0.0, 1.0)
			ping_sum += sin(p.freq * p.time * TAU) * env * 0.18
			rem.append(p)
	_ping_active = rem
	var s = buzz + noise + ping_sum + daemon_tick
	return Vector2(s, s)


func _on_diorama_tick(_delta: float) -> void:
	if _t >= _next_ping_at:
		_ping_active.append({
			"time": 0.0,
			"freq": 800.0 + randf_range(-30.0, 30.0),
			"dur": 0.10 + randf_range(0.0, 0.06),
		})
		_next_ping_at = _t + randf_range(3.0, 7.0)
