extends Control
## DeathWardDiorama — fullscreen overlay rendering Ward C as an
## interactive ASCII layout. Spawned from the Death (XIII) card's
## entry hotspot.
##
## The diorama is the playable form of the night-nurse's 06:00
## handover report from the XIII pitch+script. Six bed hotspots
## + one nursing station. Each bed click reveals the nurse's
## note for that bed and fires a SaveSystem unlock — three of
## those unlocks gate dormant hotspots on partner cards
## (Hanged Man / Justice / Emperor) so the diorama lights up the
## network as the player explores it.
##
## Procedural ambient audio: a 60 Hz fluorescent hum + occasional
## IV-machine pings at randomised intervals. No external assets.

signal closed

const C_BG := Color(0.020, 0.012, 0.018, 0.96)
const C_INK := Color(0.06, 0.04, 0.06)
const C_GOLD := Color(0.85, 0.66, 0.29)
const C_GOLD_HI := Color(1.0, 0.85, 0.40)
const C_TEXT := Color(0.85, 0.72, 0.50)
const C_TEXT_DIM := Color(0.52, 0.40, 0.22)
const C_AMBER := Color(1.0, 0.78, 0.40)
const C_PINK := Color(0.95, 0.62, 0.66)  # dusk-pink east light

# The six beds + nursing station — see _BEDS const below for the
# data table. Hotspot positions are in normalized 0..1 coords
# over the diorama panel, plotted to match the ASCII layout's
# visual bed positions.
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
        "unlocks": "vol5_ward_c_simon_walkout_seen",  # → Hanged Man
    },
    {
        "id": "ward_bed_5",
        "label": "[5] Mrs. R, 81",
        "rect": [0.66, 0.30, 0.10, 0.10],
        "report": "comfortable. family stayed until 22:00. they will be\nback at 09. tell them she asked for the radio. give\nher the radio.",
        "unlocks": "vol5_ward_c_marta_present",  # → Justice
    },
    {
        "id": "ward_bed_6",
        "label": "[6] Mr. D, 70",
        "rect": [0.80, 0.50, 0.10, 0.10],
        "report": "vitals attached. nothing changed tonight. nothing\nchanged all week. he is doing what he is doing. he\nknows. don't talk to him about the weather. talk to\nhim about his daughter. she is a dentist in asheville.\nthat is the topic.",
        "unlocks": "vol5_ward_c_dante_present",  # → Emperor
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

var _bed_hotspots: Array = []
var _report_panel: PanelContainer = null
var _report_text: RichTextLabel = null
var _report_head: Label = null

# Procedural ambient — 60 Hz buzz + occasional IV ping
var _amb_gen: AudioStreamGenerator
var _amb_player: AudioStreamPlayer
var _amb_playback: AudioStreamGeneratorPlayback
var _amb_phase: float = 0.0
var _ping_active: Array = []   # Array of {time:float, freq:float, dur:float, env_t0:float}
var _next_ping_at: float = 2.0
var _t: float = 0.0


func _ready() -> void:
    set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    mouse_filter = Control.MOUSE_FILTER_STOP
    _build_chrome()
    _init_ambient()
    set_process(true)
    set_process_input(true)


func _build_chrome() -> void:
    # Solid backdrop
    var bg := ColorRect.new()
    bg.color = C_BG
    bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    bg.mouse_filter = Control.MOUSE_FILTER_STOP
    add_child(bg)

    # Subtle east-window pink wash on the right third of the screen
    var wash := ColorRect.new()
    wash.color = Color(C_PINK.r, C_PINK.g, C_PINK.b, 0.05)
    wash.set_anchors_preset(Control.PRESET_RIGHT_WIDE)
    wash.offset_left = -360
    wash.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(wash)

    # ASCII diorama panel — centered, fixed proportions
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

    var diorama_label := Label.new()
    diorama_label.text = ASCII_LAYOUT
    diorama_label.add_theme_color_override("font_color", C_TEXT)
    diorama_label.add_theme_font_size_override("font_size", 12)
    diorama_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
    diorama_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
    diorama.add_child(diorama_label)

    # Bed + station hotspot buttons overlaid on the diorama
    for bed in _BEDS:
        var btn := Button.new()
        btn.flat = true
        btn.tooltip_text = str(bed["label"])
        var rect: Array = bed["rect"]
        # Diorama is 1080 × 680 (offsets above). Normalized rects map
        # directly to that interior surface, anchored to diorama center.
        btn.anchor_left = rect[0]; btn.anchor_top = rect[1]
        btn.anchor_right = rect[0] + rect[2]
        btn.anchor_bottom = rect[1] + rect[3]
        btn.mouse_default_cursor_shape = Control.CURSOR_HELP
        var bsb := StyleBoxFlat.new()
        bsb.bg_color = Color(1, 0.85, 0.40, 0.0)
        bsb.border_color = Color(1, 0.85, 0.40, 0.0)
        bsb.set_border_width_all(1)
        btn.add_theme_stylebox_override("normal", bsb)
        var bsh := bsb.duplicate() as StyleBoxFlat
        bsh.bg_color = Color(1, 0.85, 0.40, 0.30)
        bsh.border_color = Color(1, 0.85, 0.40, 0.85)
        btn.add_theme_stylebox_override("hover", bsh)
        btn.add_theme_stylebox_override("focus", bsh)
        var captured := bed
        btn.pressed.connect(func() -> void: _on_bed_pressed(captured))
        diorama.add_child(btn)
        _bed_hotspots.append(btn)

    # Title strip — fixed at top, doesn't move
    var top := PanelContainer.new()
    top.set_anchors_preset(Control.PRESET_TOP_WIDE)
    top.offset_bottom = 40
    var tps := StyleBoxFlat.new()
    tps.bg_color = Color(0, 0, 0, 0.78)
    tps.border_color = C_GOLD
    tps.border_width_bottom = 1
    top.add_theme_stylebox_override("panel", tps)
    add_child(top)
    var top_row := HBoxContainer.new()
    top_row.add_theme_constant_override("separation", 12)
    top.add_child(top_row)
    var pad := Control.new()
    pad.custom_minimum_size = Vector2(14, 0)
    top_row.add_child(pad)
    var title := Label.new()
    title.text = "WARD C  ·  XIII THE DEATH  ·  night-shift handover"
    title.add_theme_color_override("font_color", C_GOLD_HI)
    title.add_theme_font_size_override("font_size", 13)
    title.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    top_row.add_child(title)
    var sp := Control.new()
    sp.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    top_row.add_child(sp)
    var hint := Label.new()
    hint.text = "click a bed or the station · esc to leave"
    hint.add_theme_color_override("font_color", C_TEXT_DIM)
    hint.add_theme_font_size_override("font_size", 9)
    hint.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    top_row.add_child(hint)
    var close := Button.new()
    close.text = "[ × CLOSE ]"
    close.flat = true
    close.add_theme_color_override("font_color", C_GOLD_HI)
    close.pressed.connect(func() -> void: closed.emit())
    top_row.add_child(close)


# ── Report reveal panel ───────────────────────────────────────────

func _on_bed_pressed(bed: Dictionary) -> void:
    _ensure_report_panel()
    _report_head.text = "▷ " + str(bed["label"])
    _report_text.text = str(bed["report"])
    var key := str(bed.get("unlocks", ""))
    if key != "":
        SaveSystem.mark_unlocked(key)
    _report_panel.visible = true
    _report_panel.modulate.a = 0.0
    var tw := create_tween()
    tw.tween_property(_report_panel, "modulate:a", 1.0, 0.22)


func _ensure_report_panel() -> void:
    if _report_panel != null and is_instance_valid(_report_panel):
        return
    _report_panel = PanelContainer.new()
    _report_panel.set_anchors_preset(Control.PRESET_RIGHT_WIDE)
    _report_panel.offset_left = -380
    _report_panel.offset_right = -18
    _report_panel.offset_top = 56
    _report_panel.offset_bottom = -18
    _report_panel.mouse_filter = Control.MOUSE_FILTER_STOP
    _report_panel.z_index = 12
    var sb := StyleBoxFlat.new()
    sb.bg_color = Color(0.03, 0.02, 0.04, 0.96)
    sb.border_color = C_GOLD_HI
    sb.set_border_width_all(1)
    _report_panel.add_theme_stylebox_override("panel", sb)
    add_child(_report_panel)
    var m := MarginContainer.new()
    m.add_theme_constant_override("margin_left", 12)
    m.add_theme_constant_override("margin_right", 12)
    m.add_theme_constant_override("margin_top", 10)
    m.add_theme_constant_override("margin_bottom", 10)
    _report_panel.add_child(m)
    var vb := VBoxContainer.new()
    vb.add_theme_constant_override("separation", 6)
    m.add_child(vb)
    _report_head = Label.new()
    _report_head.add_theme_color_override("font_color", C_GOLD_HI)
    _report_head.add_theme_font_size_override("font_size", 11)
    vb.add_child(_report_head)
    _report_text = RichTextLabel.new()
    _report_text.fit_content = true
    _report_text.bbcode_enabled = false
    _report_text.add_theme_color_override("default_color", C_TEXT)
    _report_text.add_theme_font_size_override("normal_font_size", 10)
    _report_text.size_flags_vertical = Control.SIZE_EXPAND_FILL
    vb.add_child(_report_text)
    var dismiss := Button.new()
    dismiss.text = "[ × dismiss ]"
    dismiss.flat = true
    dismiss.alignment = HORIZONTAL_ALIGNMENT_RIGHT
    dismiss.add_theme_color_override("font_color", C_GOLD)
    dismiss.pressed.connect(func() -> void: _report_panel.visible = false)
    vb.add_child(dismiss)
    _report_panel.visible = false


# ── Procedural ambient audio ──────────────────────────────────────
# Layered: a low fluorescent buzz (60 Hz square wave at very low gain)
# + occasional IV-machine pings (800 Hz sine, 0.08 s with brief
# decay envelope, fired every 3-7 seconds).

func _init_ambient() -> void:
    _amb_gen = AudioStreamGenerator.new()
    _amb_gen.mix_rate = 44100
    _amb_gen.buffer_length = 0.05
    _amb_player = AudioStreamPlayer.new()
    _amb_player.bus = "BGM"
    _amb_player.stream = _amb_gen
    _amb_player.volume_db = -16.0
    add_child(_amb_player)
    _amb_player.play()
    _amb_playback = _amb_player.get_stream_playback()


func _process(delta: float) -> void:
    _t += delta
    if _amb_playback == null:
        return
    var frames := _amb_playback.get_frames_available()
    if frames <= 0:
        return
    var step := 1.0 / 44100.0
    for _i in frames:
        # 60 Hz fluorescent buzz — soft square wave + small noise.
        _amb_phase += step
        var buzz := -0.04 if fmod(_amb_phase * 60.0, 1.0) < 0.5 else 0.04
        var noise := (randf() - 0.5) * 0.012
        # IV pings — sample any active ones.
        var ping_sum := 0.0
        var rem: Array = []
        for p in _ping_active:
            p.time += step
            if p.time < p.dur:
                # 800 Hz sine, quick decay envelope.
                var env := clamp(1.0 - p.time / p.dur, 0.0, 1.0)
                ping_sum += sin(p.freq * p.time * TAU) * env * 0.18
                rem.append(p)
        _ping_active = rem
        var sample = clamp(buzz + noise + ping_sum, -0.95, 0.95)
        _amb_playback.push_frame(Vector2(sample, sample))
    # Schedule next ping
    if _t >= _next_ping_at:
        _ping_active.append({
            "time": 0.0,
            "freq": 800.0 + randf_range(-30.0, 30.0),
            "dur": 0.10 + randf_range(0.0, 0.06),
        })
        _next_ping_at = _t + randf_range(3.0, 7.0)


# ── Input ─────────────────────────────────────────────────────────

func _input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_ESCAPE:
            closed.emit()
            get_viewport().set_input_as_handled()
