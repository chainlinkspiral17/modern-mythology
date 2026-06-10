extends "res://scenes/menu/DioramaBase.gd"
## MayaYParkingLotDiorama — Maya & Y (Jimmy) in St. Jude's parking
## lot, the morning of the rite.
##
## Sunday 06:48-06:58 CT. Ten minutes between Father Quent's last
## booth call and the 7 AM mass. Maya is in her Sunday dress; Y is
## in altar-boy whites. They are kneeling-aged. They are also kids.
##
## The conversation is innocuous. The reader knows what each child
## doesn't: Maya will bear the dress all chapter. Y will sabotage
## the scaffolding before Thursday. Antonio is in his car
## heading to Daigle's. Quent has hung up the booth.
##
## Captured by demon_observer.05 (Quent's substrate at St. Jude's
## bbs). The recording is incidental — daemon_observer was
## listening to the vestibule and the kids walked into range.
## Substrate tick at 7 Hz (the rite's tempo). Ambient: parking-
## lot quiet, distant church bell warming up.

const _DIALOGUE := [
    {"t": 0,    "speaker": "system", "text": "[ambient capture — st_judes.bbs / parking lot / 06:48 CT / sunday morning / two children mic-adjacent walking from car to side door]", "is_payload": false, "unlock": ""},
    {"t": 4,    "speaker": "MAYA", "text": "I don't like it when the dress is new.", "is_payload": false, "unlock": ""},
    {"t": 8,    "speaker": "Y", "text": "It's not new. You wore it at Easter.", "is_payload": false, "unlock": ""},
    {"t": 12,   "speaker": "MAYA", "text": "Yes but my mom made it bigger. It bites.", "is_payload": true, "unlock": "vol5_maya_y_dress_bites_origin",
        "head": "06:48:12 — 'it bites'",
        "body": "Maya names the dress for what it does. Her mother made it bigger because Maya grew; the alterations are biting where the new seams sit against the old fabric.\n\nThe painted Hierophant chapter's 'the dress bites her back' is canonical from this two-second exchange in a parking lot. The chapter's body-felt sensation is older than the chapter; Maya has been carrying the bite since her mother's last sewing, which the deck reserves the date of (vol6 hook — likely tied to the Sinkhole, since Maya's mother is also a survivor or close relation).\n\n→ wakes content on Hierophant (V) and the Lovers' implicit pair lattice."},
    {"t": 20,   "speaker": "Y", "text": "My mom said tell her at lunch.", "is_payload": false, "unlock": ""},
    {"t": 24,   "speaker": "MAYA", "text": "She knows. She made it. She made it bite.", "is_payload": false, "unlock": ""},
    {"t": 28,   "speaker": "Y", "text": "Then tell her at lunch.", "is_payload": false, "unlock": ""},
    {"t": 32,   "speaker": "MAYA", "text": "(small breath) Okay.", "is_payload": false, "unlock": ""},
    {"t": 40,   "speaker": "system", "text": "[footsteps. they walk slow. Y kicks a pebble.]", "is_payload": false, "unlock": ""},
    {"t": 56,   "speaker": "Y", "text": "Father Quent was on the phone in the booth again. Before. I saw him.", "is_payload": true, "unlock": "vol5_maya_y_jimmy_saw_quent",
        "head": "06:49:16 — Y saw the booth call",
        "body": "Y was at the church early. He saw Father Quent in the vestibule booth making calls.\n\nY is observant. He is also small. He is the kind of child who sees adults doing important things and files what he sees without yet knowing what filing is for. The Hierophant booth diorama captured the three calls; this exchange captures the witness who saw them being placed.\n\nVol6 forward seed: Y/Jimmy's later sabotage of the Ember & Ash scaffolding may originate in the witness — he may be acting on something he overheard or surmised from Quent's booth. The chapter's chain V → VII → kitchen-saboteur is partly a chain of one child's growing-up between two Sundays."},
    {"t": 66,   "speaker": "MAYA", "text": "He always does that. He doesn't have a phone in the rectory that works.", "is_payload": false, "unlock": ""},
    {"t": 72,   "speaker": "Y", "text": "It works. He doesn't want the housekeeper to hear.", "is_payload": true, "unlock": "vol5_maya_y_quent_avoids_housekeeper",
        "head": "06:49:32 — Y already knows the booth is private",
        "body": "Y already knows why Quent uses the booth — to avoid the housekeeper hearing. Y has watched. Y has inferred.\n\nThe housekeeper is the Carlie thread's implied custodian. Quent's Call 3 ('Bring the car around at six fifty. Don't take Carlie.') is directed at the housekeeper because the housekeeper would otherwise bring Carlie. Y has not yet been told who Carlie is; Y has put together that Quent does not want the housekeeper to know about something.\n\nA seven-year-old can be a witness. Y is the witness Quent does not know he has.\n\n→ vol6 forward seed."},
    {"t": 82,   "speaker": "MAYA", "text": "(small) Oh.", "is_payload": false, "unlock": ""},
    {"t": 86,   "speaker": "Y", "text": "She knows already. The housekeeper. She just doesn't say.", "is_payload": false, "unlock": ""},
    {"t": 92,   "speaker": "MAYA", "text": "Why doesn't she say.", "is_payload": false, "unlock": ""},
    {"t": 96,   "speaker": "Y", "text": "(considers) Because if she said she'd have to do something.", "is_payload": true, "unlock": "vol5_maya_y_not_saying_is_act",
        "head": "06:50:16 — 'if she said she'd have to do something'",
        "body": "Y articulates the deck's working method for adult complicity. The housekeeper does not say because saying would require acting. The not-saying is itself the act.\n\nY is seven or eight. He has watched enough adults stay quiet to recognize the strategy. The deck's institutional vocabulary — Daigle who did not pick up, Dante who did not write, Quent who said but did not say to whom — is the vocabulary Y is learning to speak.\n\nThe sabotage that Y will commit (the Chariot's kitchen, JIMMY'S SABOTAGE JAMBALAYA) may be the act of a child who has decided saying-by-acting is the only registered language. He has seen adults choose silence; he chooses sabotage. Both are choices about what to do with witness.\n\n→ wakes content on Hierophant (V), Chariot (VII), Devil (XV)."},
    {"t": 108,  "speaker": "MAYA", "text": "(quiet) That's not fair.", "is_payload": false, "unlock": ""},
    {"t": 112,  "speaker": "Y", "text": "I know.", "is_payload": false, "unlock": ""},
    {"t": 116,  "speaker": "system", "text": "[they reach the side door. Y stops. Maya looks back at the parking lot.]", "is_payload": false, "unlock": ""},
    {"t": 130,  "speaker": "MAYA", "text": "Y.", "is_payload": false, "unlock": ""},
    {"t": 132,  "speaker": "Y", "text": "Mm.", "is_payload": false, "unlock": ""},
    {"t": 134,  "speaker": "MAYA", "text": "Stay next to me during the kneeling. The dress is worse if I have to hold the kneel by myself.", "is_payload": false, "unlock": ""},
    {"t": 142,  "speaker": "Y", "text": "I will.", "is_payload": false, "unlock": ""},
    {"t": 146,  "speaker": "MAYA", "text": "Even if Father Paul tries to move you.", "is_payload": false, "unlock": ""},
    {"t": 150,  "speaker": "Y", "text": "Even if.", "is_payload": false, "unlock": ""},
    {"t": 154,  "speaker": "system", "text": "[the church bell warms up — a quiet practice strike, then silence. Y holds the side door for Maya. she goes in. he follows.]", "is_payload": true, "unlock": "vol5_maya_y_doorway",
        "head": "06:51:34 — the door",
        "body": "Y holds the door for Maya. Maya goes in first. The deck's youngest characters cross the threshold of the painted Hierophant chapter together; the chapter at V begins where this voice log ends.\n\nThe rite is nine minutes away. Antonio is in his car on the river road, twelve minutes from Daigle's. Quent is in the sacristy preparing. The housekeeper is in the rectory with Carlie. The Sinkhole's anniversary memorial line on the carpet is two months away from being walked over again.\n\nThe deck's youngest voice log is also the deck's quietest chapter-beginning. Two children. Ten minutes. One held door.\n\n→ wakes content on Hierophant (V) — the painted chapter is the chapter immediately after this conversation."},
    {"t": 168,  "speaker": "system", "text": "[ambient capture continues for another 11 minutes — the parking lot fills with arriving congregation. neither child is mic-adjacent again. recording ends at 07:02 when the mass begins.]", "is_payload": false, "unlock": ""}
]

# Playback state
var _playing: bool = true
var _elapsed: float = 0.0
var _lines_shown: int = 0
var _dialogue_vbox: VBoxContainer = null
var _scroll: ScrollContainer = null
var _time_label: Label = null


func _init() -> void:
    _diorama_title = "MAYA & Y  ·  V (parking lot)  ·  06:48-06:51 CT  ·  9 min before mass"
    _diorama_hint = "voice log streams at 6× real-time · click ✦ lines · space to pause · esc"
    _edge_wash_color = Color(0.45, 0.40, 0.50, 0.04)


func _build_content() -> void:
    var panel := PanelContainer.new()
    panel.set_anchors_preset(Control.PRESET_FULL_RECT)
    panel.offset_top = 60
    panel.offset_left = 80
    panel.offset_right = -80
    panel.offset_bottom = -56
    var sb := StyleBoxFlat.new()
    sb.bg_color = Color(0.022, 0.020, 0.028, 0.97)
    sb.border_color = Color(0.55, 0.50, 0.65, 0.7)
    sb.set_border_width_all(1)
    panel.add_theme_stylebox_override("panel", sb)
    add_child(panel)
    var pad := MarginContainer.new()
    pad.add_theme_constant_override("margin_left", 24)
    pad.add_theme_constant_override("margin_right", 24)
    pad.add_theme_constant_override("margin_top", 16)
    pad.add_theme_constant_override("margin_bottom", 16)
    panel.add_child(pad)
    var vb := VBoxContainer.new()
    vb.add_theme_constant_override("separation", 6)
    pad.add_child(vb)
    var head_row := HBoxContainer.new()
    head_row.add_theme_constant_override("separation", 16)
    vb.add_child(head_row)
    var head := Label.new()
    head.text = "ST_JUDES.BBS  ·  parking lot ambient capture  ·  06:48 CT"
    head.add_theme_color_override("font_color", Color(0.75, 0.70, 0.80))
    head.add_theme_font_size_override("font_size", 11)
    head.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    head_row.add_child(head)
    _time_label = Label.new()
    _time_label.text = "00:00 / 02:48"
    _time_label.add_theme_color_override("font_color", C_TEXT_DIM)
    _time_label.add_theme_font_size_override("font_size", 10)
    head_row.add_child(_time_label)
    var rule := ColorRect.new()
    rule.color = Color(0.55, 0.50, 0.65, 0.5)
    rule.custom_minimum_size = Vector2(0, 1)
    vb.add_child(rule)
    _scroll = ScrollContainer.new()
    _scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
    vb.add_child(_scroll)
    _dialogue_vbox = VBoxContainer.new()
    _dialogue_vbox.add_theme_constant_override("separation", 5)
    _dialogue_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    _scroll.add_child(_dialogue_vbox)
    var fetch := Label.new()
    fetch.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
    fetch.offset_top = -22
    fetch.offset_bottom = -6
    fetch.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    fetch.text = "[demon_observer.05 // st_judes.bbs (parking lot ambient — children mic-adjacent for 2:48 of 14:00 capture) // integrity 0.95]"
    fetch.add_theme_color_override("font_color", C_TEXT_DIM)
    fetch.add_theme_font_size_override("font_size", 9)
    fetch.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(fetch)


func _on_diorama_tick(delta: float) -> void:
    if _playing:
        _elapsed += delta * 6.0
    while _lines_shown < _DIALOGUE.size() and float(_DIALOGUE[_lines_shown]["t"]) <= _elapsed:
        _emit_line(_DIALOGUE[_lines_shown])
        _lines_shown += 1
    if _time_label != null and is_instance_valid(_time_label):
        _time_label.text = "%02d:%02d / 02:48" % [int(_elapsed) / 60, int(_elapsed) % 60]


func _emit_line(line: Dictionary) -> void:
    var sp := str(line["speaker"])
    var text := str(line["text"])
    var is_payload := bool(line.get("is_payload", false))
    var col := C_TEXT
    var prefix := ""
    match sp:
        "MAYA":
            col = Color(0.90, 0.70, 0.75)
            prefix = "MAYA: "
        "Y":
            col = Color(0.65, 0.80, 0.75)
            prefix = "Y:    "
        "system":
            col = C_TEXT_DIM
    if not is_payload:
        var lbl := Label.new()
        lbl.text = prefix + text
        lbl.add_theme_color_override("font_color", col)
        lbl.add_theme_font_size_override("font_size", 10)
        lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
        _dialogue_vbox.add_child(lbl)
    else:
        var captured := line
        var btn := Button.new()
        btn.flat = false
        btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
        btn.text = "  ✦  " + prefix + text
        btn.add_theme_color_override("font_color", col)
        btn.add_theme_font_size_override("font_size", 10)
        btn.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
        var bsb := StyleBoxFlat.new()
        bsb.bg_color = Color(col.r * 0.3, col.g * 0.3, col.b * 0.3, 0.4)
        bsb.border_color = Color(col.r, col.g, col.b, 0.6)
        bsb.border_width_left = 2
        btn.add_theme_stylebox_override("normal", bsb)
        var bsh := bsb.duplicate() as StyleBoxFlat
        bsh.bg_color = Color(col.r, col.g, col.b, 0.18)
        bsh.border_width_left = 4
        btn.add_theme_stylebox_override("hover", bsh)
        btn.pressed.connect(func() -> void:
            reveal(str(captured.get("head", "")), str(captured.get("body", "")),
                    str(captured.get("unlock", ""))))
        _dialogue_vbox.add_child(btn)
    call_deferred("_scroll_to_bottom")


func _scroll_to_bottom() -> void:
    if _scroll == null: return
    var sb_v: VScrollBar = _scroll.get_v_scroll_bar()
    if sb_v != null:
        sb_v.value = sb_v.max_value


# ── Ambient: 7 Hz observer tick + distant bell + footsteps ───────

var _tick_phase: float = 0.0
var _next_bell_at: float = 30.0


func _ambient_sample(phase: float, step: float) -> Vector2:
    _tick_phase += step * 7.0
    var tick := 0.0
    if fmod(_tick_phase, 1.0) < 0.04:
        tick = -0.025 * (1.0 - fmod(_tick_phase, 1.0) / 0.04)
    var bell := 0.0
    if has_meta("bell_t0"):
        var bt: float = phase - get_meta("bell_t0")
        if bt >= 0.0 and bt < 1.2:
            var env: float = clamp(1.0 - bt / 1.2, 0.0, 1.0)
            bell = sin(220.0 * bt * TAU) * env * 0.04 + sin(440.0 * bt * TAU) * env * 0.02
        if bt > 1.2:
            remove_meta("bell_t0")
    if _t >= _next_bell_at:
        set_meta("bell_t0", phase)
        _next_bell_at = _t + randf_range(45.0, 80.0)
    var noise := (randf() - 0.5) * 0.010
    var s = tick + bell + noise
    return Vector2(s, s)


func _input(event: InputEvent) -> void:
    super(event)
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_SPACE:
            _playing = not _playing
            get_viewport().set_input_as_handled()
