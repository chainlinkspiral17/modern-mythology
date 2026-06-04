extends "res://scenes/menu/DioramaBase.gd"
## HangedManVoicemailsDiorama — Natalie's three outbound voicemails
## to Simon, timestamped to the phone log on the painted card.
##
## Each voicemail is a recording the player can play — text scrolls
## as the audio progresses. Player can replay individual messages,
## or let all three auto-advance.
##
## Lore: daemon_courier.12 fetches in-transit messages (these were
## delivered to Simon's voicemail box — Simon never opened them).
## Substrate tick at 6 Hz (the candle-wax drip rate). The audio
## carries a faint candle-flicker tone (low frequency-modulated
## hum) under the playback.
##
## See pitches/12_hanged_man.md for the source script.

const _MESSAGES := [
    {
        "id": "vm_1_2314",
        "label": "23:14 PT  ·  38 seconds",
        "duration_sec": 38,
        "lines": [
            {"t": 0,  "text": "Hi, it's me. I know you don't want to —"},
            {"t": 4,  "text": "[breath]"},
            {"t": 5,  "text": "I know. Okay. I'm at the apartment. I have the key."},
            {"t": 11, "text": "I am just letting you know I am here. I am not — I won't —"},
            {"t": 16, "text": "I am not opening anything. I am sitting at the counter."},
            {"t": 21, "text": "The candle you bought me is on the counter."},
            {"t": 24, "text": "Did you buy me the candle. I think you did. It is half."},
            {"t": 28, "text": "I'm going to wait until it is the other half and then"},
            {"t": 31, "text": "I'm going to call again. Half a candle is how long I think this is."},
            {"t": 36, "text": "Okay. Bye."}
        ],
        "unlock": "vol5_hanged_vm_1_played"
    },
    {
        "id": "vm_2_0012",
        "label": "00:12 PT  ·  51 seconds",
        "duration_sec": 51,
        "lines": [
            {"t": 0,  "text": "The candle is two-thirds. I lied about half."},
            {"t": 4,  "text": "I lied because half is how long I wished this was."},
            {"t": 8,  "text": "Half a candle is two hours and I have been here three."},
            {"t": 13, "text": "The candle was already half when I sat down because YOU lit it before you left."},
            {"t": 20, "text": "That is a thing you did. You left the candle lit."},
            {"t": 24, "text": "The cards are in front of me. I am not —"},
            {"t": 27, "text": "I will tell you I have not turned any of them."},
            {"t": 31, "text": "I cut the deck. I did the cut you taught me."},
            {"t": 35, "text": "You taught me one cut. The cut is the deck cut once toward the dealer."},
            {"t": 41, "text": "I have done that and I have not turned a card."},
            {"t": 45, "text": "I am waiting for you to tell me to. Call me."},
            {"t": 48, "text": "[breath]"},
            {"t": 49, "text": "Okay. Bye."}
        ],
        "unlock": "vol5_hanged_vm_2_played"
    },
    {
        "id": "vm_3_0058",
        "label": "00:58 PT  ·  17 seconds",
        "duration_sec": 17,
        "lines": [
            {"t": 0,  "text": "Simon."},
            {"t": 2,  "text": "Simon, the candle is gone."},
            {"t": 6,  "text": "I am at the counter."},
            {"t": 9,  "text": "Call me."},
            {"t": 11, "text": "I'm staying."},
            {"t": 14, "text": "Bye."}
        ],
        "unlock": "vol5_hanged_vm_3_played"
    }
]

const _PAYLOADS := {
    "vol5_hanged_vm_1_played": {
        "head": "VM 1 — 23:14 PT  ·  the candle is half",
        "body": "Natalie's first voicemail. 38 seconds. She apologizes (\"I know you don't want to —\"). She names the candle as Simon's gift. She makes a deal with herself: she will call again when the candle's other half is gone.\n\nThe candle was already half when Natalie arrived because Simon left it burning. The deck's deepest quiet cruelty: he prepared the room for her arrival without staying for it. She does not know this yet on VM 1; she will name it on VM 2."
    },
    "vol5_hanged_vm_2_played": {
        "head": "VM 2 — 00:12 PT  ·  'you left the candle lit'",
        "body": "Natalie's second voicemail. 51 seconds, the longest. She corrects her earlier estimate: the candle was half when she sat down, not half because she'd been waiting. She has been waiting three hours, not two.\n\nShe says: 'You left the candle lit.'\n\nShe also surfaces her relationship to the maroon-backed tarot deck. The single cut she has learned — from Simon. 'You taught me one cut.' Natalie's whole tarot education in five words. The Hanged Man chapter is the chapter where she uses what she was taught and doesn't turn a card.\n\n→ wakes content on Moon (XVIII) — her later sigil reading.\n→ wakes content on Death (XIII) — Simon's walkout was 03:55 AMA, four hours after this message.\n→ wakes content on Lovers (VI) — pair lattice entry for Natalie & Simon."
    },
    "vol5_hanged_vm_3_played": {
        "head": "VM 3 — 00:58 PT  ·  17 seconds",
        "body": "Natalie's third voicemail. 17 seconds. The shortest. She says only Simon's name (twice), the candle's state, her location, and the word 'bye.'\n\nThe progression: 38 → 51 → 17. By the third, Natalie has stopped apologizing. She has stopped explaining. She is reporting state.\n\nThe candle is gone. She is staying.\n\nThe Hanged Man's suspension is the suspension that follows the candle's exhaustion. The chapter is the held breath after the last call.\n\n→ wakes content on Moon (XVIII) — the sigils Natalie reads at XVIII are written tonight, between this message and dawn.\n→ wakes content on Hermit (IX) — XII ↔ IX shadow-mirror reciprocal references."
    }
}

# Playback state
var _active_msg: int = -1
var _elapsed: float = 0.0
var _lines_shown: int = 0
var _msg_panel: PanelContainer = null
var _msg_lines_vb: VBoxContainer = null
var _time_label: Label = null


func _init() -> void:
    _diorama_title = "NATALIE'S VOICEMAIL OUTBOX  ·  XII THE HANGED MAN  ·  three messages to Simon"
    _diorama_hint = "click a message to play · text scrolls in time · esc to leave"
    _edge_wash_color = Color(0.40, 0.20, 0.10, 0.04)  # candle amber dimmed


func _build_content() -> void:
    # Phone interface — left side
    var phone := PanelContainer.new()
    phone.set_anchors_preset(Control.PRESET_CENTER_LEFT)
    phone.offset_left = 40
    phone.offset_right = 460
    phone.offset_top = -280
    phone.offset_bottom = 280
    var sb := StyleBoxFlat.new()
    sb.bg_color = Color(0.020, 0.014, 0.012, 0.96)
    sb.border_color = C_GOLD
    sb.set_border_width_all(1)
    sb.corner_radius_top_left = 20
    sb.corner_radius_top_right = 20
    sb.corner_radius_bottom_left = 20
    sb.corner_radius_bottom_right = 20
    phone.add_theme_stylebox_override("panel", sb)
    add_child(phone)
    var m := MarginContainer.new()
    m.add_theme_constant_override("margin_left", 16)
    m.add_theme_constant_override("margin_right", 16)
    m.add_theme_constant_override("margin_top", 18)
    m.add_theme_constant_override("margin_bottom", 18)
    phone.add_child(m)
    var vb := VBoxContainer.new()
    vb.add_theme_constant_override("separation", 10)
    m.add_child(vb)
    var head := Label.new()
    head.text = "OUTBOX — to: simon.j\n(no replies received)"
    head.add_theme_color_override("font_color", C_GOLD_HI)
    head.add_theme_font_size_override("font_size", 11)
    vb.add_child(head)
    var rule := ColorRect.new()
    rule.color = C_GOLD
    rule.custom_minimum_size = Vector2(0, 1)
    vb.add_child(rule)
    for i in _MESSAGES.size():
        var msg: Dictionary = _MESSAGES[i]
        var captured := i
        var btn := Button.new()
        btn.flat = false
        btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
        btn.text = "  ▶ " + str(msg["label"])
        btn.add_theme_color_override("font_color", C_TEXT)
        btn.add_theme_font_size_override("font_size", 10)
        btn.custom_minimum_size = Vector2(0, 40)
        btn.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
        var bsb := StyleBoxFlat.new()
        bsb.bg_color = Color(0.04, 0.04, 0.06, 0.7)
        bsb.border_color = Color(0.40, 0.30, 0.20, 0.5)
        bsb.border_width_left = 2
        btn.add_theme_stylebox_override("normal", bsb)
        var bsh := bsb.duplicate() as StyleBoxFlat
        bsh.bg_color = Color(0.85, 0.55, 0.20, 0.15)
        bsh.border_width_left = 4
        btn.add_theme_stylebox_override("hover", bsh)
        btn.pressed.connect(func() -> void: _play_message(captured))
        vb.add_child(btn)
    var sp := Control.new()
    sp.size_flags_vertical = Control.SIZE_EXPAND_FILL
    vb.add_child(sp)
    var note := Label.new()
    note.text = "the candle was already half when I sat down because YOU lit it before you left"
    note.add_theme_color_override("font_color", C_TEXT_DIM)
    note.add_theme_font_size_override("font_size", 8)
    note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    vb.add_child(note)

    var fetch := Label.new()
    fetch.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
    fetch.offset_top = -22
    fetch.offset_bottom = -6
    fetch.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    fetch.text = "[demon_courier.12 // simon.voicemail.bbs // 3 messages delivered (0 opened by recipient) // integrity 0.99]"
    fetch.add_theme_color_override("font_color", C_TEXT_DIM)
    fetch.add_theme_font_size_override("font_size", 9)
    fetch.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(fetch)


func _play_message(idx: int) -> void:
    _active_msg = idx
    _elapsed = 0.0
    _lines_shown = 0
    _build_msg_panel()


func _build_msg_panel() -> void:
    if _msg_panel != null and is_instance_valid(_msg_panel):
        _msg_panel.queue_free()
    var msg: Dictionary = _MESSAGES[_active_msg]
    _msg_panel = PanelContainer.new()
    _msg_panel.set_anchors_preset(Control.PRESET_CENTER_RIGHT)
    _msg_panel.offset_left = -540
    _msg_panel.offset_right = -40
    _msg_panel.offset_top = -280
    _msg_panel.offset_bottom = 280
    var sb := StyleBoxFlat.new()
    sb.bg_color = Color(0.024, 0.020, 0.018, 0.96)
    sb.border_color = C_GOLD_HI
    sb.set_border_width_all(1)
    _msg_panel.add_theme_stylebox_override("panel", sb)
    add_child(_msg_panel)
    var m := MarginContainer.new()
    m.add_theme_constant_override("margin_left", 16)
    m.add_theme_constant_override("margin_right", 16)
    m.add_theme_constant_override("margin_top", 14)
    m.add_theme_constant_override("margin_bottom", 14)
    _msg_panel.add_child(m)
    var vb := VBoxContainer.new()
    vb.add_theme_constant_override("separation", 8)
    m.add_child(vb)
    var head := Label.new()
    head.text = "▷ " + str(msg["label"])
    head.add_theme_color_override("font_color", C_GOLD_HI)
    head.add_theme_font_size_override("font_size", 11)
    vb.add_child(head)
    _time_label = Label.new()
    _time_label.text = "00:00 / %02d:%02d" % [int(msg["duration_sec"]) / 60, int(msg["duration_sec"]) % 60]
    _time_label.add_theme_color_override("font_color", C_TEXT_DIM)
    _time_label.add_theme_font_size_override("font_size", 9)
    vb.add_child(_time_label)
    var rule := ColorRect.new()
    rule.color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.4)
    rule.custom_minimum_size = Vector2(0, 1)
    vb.add_child(rule)
    var scroll := ScrollContainer.new()
    scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
    vb.add_child(scroll)
    _msg_lines_vb = VBoxContainer.new()
    _msg_lines_vb.add_theme_constant_override("separation", 6)
    _msg_lines_vb.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    scroll.add_child(_msg_lines_vb)
    var payload_btn := Button.new()
    payload_btn.text = "[ ✦ surface payload ]"
    payload_btn.flat = true
    payload_btn.alignment = HORIZONTAL_ALIGNMENT_RIGHT
    payload_btn.add_theme_color_override("font_color", C_GOLD)
    payload_btn.name = "payload_btn"
    payload_btn.visible = false
    var captured_unlock := str(msg["unlock"])
    payload_btn.pressed.connect(func() -> void:
        var p: Dictionary = _PAYLOADS.get(captured_unlock, {})
        if not p.is_empty():
            reveal(str(p.get("head", "")), str(p.get("body", "")), captured_unlock))
    vb.add_child(payload_btn)
    var dismiss := Button.new()
    dismiss.text = "[ × hang up ]"
    dismiss.flat = true
    dismiss.alignment = HORIZONTAL_ALIGNMENT_RIGHT
    dismiss.add_theme_color_override("font_color", C_TEXT_DIM)
    dismiss.pressed.connect(func() -> void:
        _active_msg = -1
        if is_instance_valid(_msg_panel):
            _msg_panel.queue_free())
    vb.add_child(dismiss)


func _on_diorama_tick(delta: float) -> void:
    if _active_msg < 0:
        return
    _elapsed += delta * 4.0   # 4× pacing
    var msg: Dictionary = _MESSAGES[_active_msg]
    var lines: Array = msg["lines"]
    while _lines_shown < lines.size() and float(lines[_lines_shown]["t"]) <= _elapsed:
        var line: Dictionary = lines[_lines_shown]
        if _msg_lines_vb != null and is_instance_valid(_msg_lines_vb):
            var lb := Label.new()
            lb.text = str(line["text"])
            lb.add_theme_color_override("font_color", C_TEXT)
            lb.add_theme_font_size_override("font_size", 11)
            lb.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
            lb.custom_minimum_size.x = 440
            _msg_lines_vb.add_child(lb)
        _lines_shown += 1
    if _time_label != null and is_instance_valid(_time_label):
        var dur := int(msg["duration_sec"])
        _time_label.text = "%02d:%02d / %02d:%02d" % [int(_elapsed) / 60, int(_elapsed) % 60, dur / 60, dur % 60]
    if _lines_shown >= lines.size() and _msg_panel != null:
        var pb: Variant = _msg_panel.find_child("payload_btn", true, false)
        if pb != null:
            pb.visible = true


# ── Ambient: 6 Hz candle drip + flicker tone ─────────────────────

var _tick_phase: float = 0.0
var _flicker_phase: float = 0.0


func _ambient_sample(_phase: float, step: float) -> Vector2:
    _tick_phase += step * 6.0
    var tick := 0.0
    if fmod(_tick_phase, 1.0) < 0.03:
        tick = -0.04 * (1.0 - fmod(_tick_phase, 1.0) / 0.03)
    # Slow flicker tone — 220 Hz amplitude-modulated at 1.3 Hz
    _flicker_phase += step
    var mod := 0.5 + 0.5 * sin(_flicker_phase * 1.3 * TAU)
    var flicker := sin(_flicker_phase * 220.0 * TAU) * 0.014 * mod
    var noise := (randf() - 0.5) * 0.010
    var s = tick + flicker + noise
    return Vector2(s, s)
