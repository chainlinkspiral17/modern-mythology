extends "res://scenes/menu/DioramaBase.gd"
## DanteQuentBargeDiorama — Dante D'Ambrosio + Father Quent on the
## barge, Wednesday 09:00 CT.
##
## A two-character voice log captured by daemon_observer.04 from
## the barge's docked-mode BBS link (the boat broadcasts when at
## the pier). 45 minutes of recording; the chapter's painted IV
## scene is mid-week. This is the morning Father Quent decides
## about Thursday's scaffolding — the decision he then reverses
## at his Sunday booth (V).
##
## Lore: two demons overlap on this recording. daemon_observer.04
## (Emperor's substrate) captures Dante's side at higher fidelity;
## daemon_observer.05 (Hierophant's substrate) catches Quent's
## responses. The integrity is variable — 0.91 average. Substrate
## ticks at 18 Hz (Dante's pulse) + 7 Hz (Quent's tempo), mixed.
## The ambient also carries river slap against hull, slow.

const _DIALOGUE := [
    {"t": 0,    "speaker": "system", "text": "[barge BBS link active. recording starts at 09:00:00 as instructed. anchor down. coffee on table.]", "is_payload": false, "unlock": ""},
    {"t": 2,    "speaker": "DANTE", "text": "Coffee.", "is_payload": false, "unlock": ""},
    {"t": 4,    "speaker": "QUENT", "text": "Thank you.", "is_payload": false, "unlock": ""},
    {"t": 8,    "speaker": "DANTE", "text": "The manifest is on top. Read it before I sit.", "is_payload": false, "unlock": ""},
    {"t": 16,   "speaker": "QUENT", "text": "(reading) Eighty-two crates. The bourbon is on the down-side of the list.", "is_payload": false, "unlock": ""},
    {"t": 22,   "speaker": "DANTE", "text": "Bourbon is always on the down-side. You like it that way.", "is_payload": false, "unlock": ""},
    {"t": 26,   "speaker": "QUENT", "text": "I like it on a list. The list is what makes it bourbon. Without the list it's just a bottle.", "is_payload": false, "unlock": ""},
    {"t": 34,   "speaker": "DANTE", "text": "(small laugh) Yeah.", "is_payload": false, "unlock": ""},
    {"t": 40,   "speaker": "system", "text": "[15 second pause. anchor chain shifts in the current. Dante sits.]", "is_payload": false, "unlock": ""},
    {"t": 60,   "speaker": "DANTE", "text": "Anchor's fouling.", "is_payload": true, "unlock": "vol5_barge_anchor_fouling",
        "head": "09:01:00 — 'anchor's fouling'",
        "body": "Dante's first direct concern of the morning. The anchor is fouling. The boat is not sitting where it should. Dante notices; Dante does not name what the fouling is from.\n\nDante's appointment book for this day says: 'anchor still fouling. say aesthetic to nicola. it is not aesthetic.' He will lie to Nicola about it at dinner Wednesday night.\n\n→ wakes content on Empress (III)."},
    {"t": 64,   "speaker": "QUENT", "text": "Mm.", "is_payload": false, "unlock": ""},
    {"t": 70,   "speaker": "DANTE", "text": "Have a look later. Bring someone who knows.", "is_payload": false, "unlock": ""},
    {"t": 76,   "speaker": "QUENT", "text": "I'll bring Antonio.", "is_payload": true, "unlock": "vol5_barge_antonio_named",
        "head": "09:01:16 — 'I'll bring Antonio'",
        "body": "Quent names Antonio as the person he'll bring to look at the anchor. Six days from now, Quent will dial Antonio from the St. Jude's vestibule booth and send him to Daigle instead.\n\nThe morning at the barge is the morning Quent has Antonio in mind as the friend-who-can-be-trusted-to-look-at-things. The Chariot's death is the death of that trust — Antonio was the one sent, and the one who didn't come back.\n\n→ wakes content on Chariot (VII), Hierophant (V)."},
    {"t": 81,   "speaker": "DANTE", "text": "Fine. After the eleven mass.", "is_payload": false, "unlock": ""},
    {"t": 86,   "speaker": "QUENT", "text": "After the eleven.", "is_payload": false, "unlock": ""},
    {"t": 90,   "speaker": "system", "text": "[20 seconds of quiet. Dante shuffles papers. Quent reads.]", "is_payload": false, "unlock": ""},
    {"t": 120,  "speaker": "QUENT", "text": "PetroTex item — you have it on the council agenda?", "is_payload": true, "unlock": "vol5_barge_petrotex_mentioned",
        "head": "09:02:00 — Quent raises PetroTex",
        "body": "Quent raises the PetroTex agenda item on Wednesday morning. He has not yet been told he'll be taking the item; Dante decides in the next minute that Quent will.\n\nThe Wheel chapter's Denied Motion and the Justice chapter's shattered scales follow from this 90-second exchange between two friends on a boat. The case is moved from Dante's council to Quent's hands here.\n\n→ wakes content on Wheel (X), Justice (XI)."},
    {"t": 125,  "speaker": "DANTE", "text": "Three sessions, two o'clock and three o'clock. I XX'd it through twice already.", "is_payload": false, "unlock": ""},
    {"t": 134,  "speaker": "QUENT", "text": "You want me to take it.", "is_payload": false, "unlock": ""},
    {"t": 138,  "speaker": "DANTE", "text": "I want you to take it.", "is_payload": false, "unlock": ""},
    {"t": 142,  "speaker": "QUENT", "text": "All right.", "is_payload": false, "unlock": ""},
    {"t": 146,  "speaker": "QUENT", "text": "The Romero file — you have the audit number?", "is_payload": true, "unlock": "vol5_barge_audit_number",
        "head": "09:02:26 — the audit number",
        "body": "Quent asks about an audit number Dante has been telling Alberto to 'wait until it clears.' The audit is the PetroTex date-shift audit — the same audit that clears the wrong way Friday, the same audit that becomes the case's structural lie.\n\nQuent knows about the audit before Sunday morning when he dials Alberto for the third time and says 'the audit's clearing the wrong way. tell him.' The morning at the barge is when Quent learns the case is going to need handling.\n\n→ wakes content on Wheel (X) and Hierophant (V)."},
    {"t": 152,  "speaker": "DANTE", "text": "Alberto has it. I told him wait until it clears.", "is_payload": false, "unlock": ""},
    {"t": 158,  "speaker": "QUENT", "text": "Alberto waits for you.", "is_payload": false, "unlock": ""},
    {"t": 162,  "speaker": "DANTE", "text": "Yes.", "is_payload": false, "unlock": ""},
    {"t": 166,  "speaker": "QUENT", "text": "And you wait for what?", "is_payload": false, "unlock": ""},
    {"t": 174,  "speaker": "DANTE", "text": "(longer pause) For the council to forget the date-shift.", "is_payload": true, "unlock": "vol5_barge_dante_confesses",
        "head": "09:02:54 — Dante's confession",
        "body": "Dante tells Quent, on the boat, what he is waiting for. He is waiting for the council to forget the date-shift in Mrs. Romero's deposition. The chapter Erica Campbell argues at XI Justice is the chapter Dante engineered to be forgotten.\n\nThe boat at 09:02 Wednesday morning is the deck's quietest confession. Quent hears it. Quent files it. Quent will not name it on Sunday's booth call. The institution covers what the throne admits.\n\n→ wakes content on Justice (XI), Wheel (X), Lovers (VI — Nicola&Dante pair lattice gains a new annotation: succession is also coverup)."},
    {"t": 184,  "speaker": "QUENT", "text": "And then?", "is_payload": false, "unlock": ""},
    {"t": 190,  "speaker": "DANTE", "text": "Then it's a different case.", "is_payload": false, "unlock": ""},
    {"t": 196,  "speaker": "QUENT", "text": "Mm.", "is_payload": false, "unlock": ""},
    {"t": 200,  "speaker": "system", "text": "[10 seconds. River slap. Both men breathe out slowly. Quent turns a page.]", "is_payload": false, "unlock": ""},
    {"t": 218,  "speaker": "QUENT", "text": "Thursday's scaffolding.", "is_payload": true, "unlock": "vol5_barge_quent_raises_scaffolding",
        "head": "09:03:38 — Quent raises Thursday's scaffolding",
        "body": "Quent raises the scaffolding decision Wednesday morning. He is preparing to make it. The decision he makes here — leave the scaffolding standing — is the decision he reverses at Sunday's booth. The reversal sends Antonio to Daigle. The reversal kills Antonio.\n\nThe morning on the barge is the morning Quent COULD have decided differently and didn't. The Sunday morning at the booth is the morning he undoes a decision he was at peace with on Wednesday. Two mornings, one decision, two outcomes.\n\n→ wakes content on Devil (XV) and Chariot (VII)."},
    {"t": 222,  "speaker": "DANTE", "text": "Your call.", "is_payload": false, "unlock": ""},
    {"t": 226,  "speaker": "QUENT", "text": "I'm going to leave it up.", "is_payload": false, "unlock": ""},
    {"t": 230,  "speaker": "DANTE", "text": "Mm.", "is_payload": false, "unlock": ""},
    {"t": 236,  "speaker": "QUENT", "text": "Daigle won't like it.", "is_payload": false, "unlock": ""},
    {"t": 240,  "speaker": "DANTE", "text": "Daigle never likes anything you decide.", "is_payload": false, "unlock": ""},
    {"t": 246,  "speaker": "QUENT", "text": "He likes when I decide what he wanted me to decide.", "is_payload": false, "unlock": ""},
    {"t": 252,  "speaker": "DANTE", "text": "(small laugh) Yes.", "is_payload": false, "unlock": ""},
    {"t": 258,  "speaker": "QUENT", "text": "He wants me to take it down.", "is_payload": false, "unlock": ""},
    {"t": 262,  "speaker": "DANTE", "text": "He always wants you to take things down.", "is_payload": false, "unlock": ""},
    {"t": 268,  "speaker": "QUENT", "text": "I'm leaving it up.", "is_payload": false, "unlock": ""},
    {"t": 272,  "speaker": "DANTE", "text": "(noncommittal) Mm.", "is_payload": false, "unlock": ""},
    {"t": 280,  "speaker": "system", "text": "[long silence — 28 seconds. river. coffee. nothing.]", "is_payload": false, "unlock": ""},
    {"t": 320,  "speaker": "QUENT", "text": "How is Alma.", "is_payload": true, "unlock": "vol5_barge_quent_asks_alma",
        "head": "09:05:20 — Quent asks about Alma",
        "body": "Quent asks Dante about Alma by name. The blocked 'alma (private)' slot in Dante's daily calendar has a name; Quent uses it.\n\nDante responds with a single line that the recording captures but does not transcribe (the audio is intentionally indistinct here — daemon_observer respects the privacy that Dante and Quent maintain about Alma between them). Then they move on.\n\nForward seed: Alma is known to Quent. Quent uses her name. Alma will be named in vol6 from whichever direction the deck chooses.\n\n→ vol6 hook."},
    {"t": 326,  "speaker": "DANTE", "text": "[indistinct — single sentence]", "is_payload": false, "unlock": ""},
    {"t": 332,  "speaker": "QUENT", "text": "Mm. Tell her I said.", "is_payload": false, "unlock": ""},
    {"t": 338,  "speaker": "DANTE", "text": "I will.", "is_payload": false, "unlock": ""},
    {"t": 344,  "speaker": "system", "text": "[5 minutes of quiet that the recording dutifully captures. then movement. Quent stands.]", "is_payload": false, "unlock": ""},
    {"t": 640,  "speaker": "QUENT", "text": "I'll come back for the anchor this afternoon.", "is_payload": false, "unlock": ""},
    {"t": 646,  "speaker": "DANTE", "text": "With Antonio.", "is_payload": false, "unlock": ""},
    {"t": 650,  "speaker": "QUENT", "text": "With Antonio.", "is_payload": false, "unlock": ""},
    {"t": 654,  "speaker": "DANTE", "text": "Thank you, Quentin.", "is_payload": false, "unlock": ""},
    {"t": 658,  "speaker": "QUENT", "text": "Thank you, Dante.", "is_payload": false, "unlock": ""},
    {"t": 664,  "speaker": "system", "text": "[Quent walks off. barge BBS link records the walk for 90 more seconds (the manifest is left on the table; Dante does not pick it up). recording ends at 09:12:34, 12 minutes 34 seconds after start, when Dante turns the link off himself.]", "is_payload": true, "unlock": "vol5_barge_recording_ends",
        "head": "09:12:34 — Dante ends the recording",
        "body": "Dante turns the BBS link off himself. The recording ends. daemon_observer.04 has the 12:34 capture. daemon_observer.05 (Quent's substrate) has a parallel capture of the same conversation from a different angle — quent's side of the boat-creak. The two recordings overlap with minor desync.\n\nThe deck has two demons on this conversation because both Dante and Quent are subjects-of-record. The conversation is the deck's most fully witnessed moment outside the ENSEMBLE_01 gathering.\n\nThree decisions were made on the boat this morning:\n  1. Antonio will look at the anchor this afternoon (kept).\n  2. Quent takes the PetroTex item (kept).\n  3. Thursday's scaffolding stays up (REVERSED on Sunday).\n\nThe vol5 spine of consequences pivots on the third decision.\n\n→ wakes content on Hierophant (V), Chariot (VII), Devil (XV), Justice (XI), Wheel (X), Empress (III)."}
]


# Playback state
var _playing: bool = true
var _elapsed: float = 0.0
var _lines_shown: int = 0
var _dialogue_vbox: VBoxContainer = null
var _scroll: ScrollContainer = null
var _time_label: Label = null


func _init() -> void:
    _diorama_title = "BARGE — Dante & Quentin  ·  IV+V  ·  Wed 09:00-09:12 CT"
    _diorama_hint = "voice log streams at 4× real-time · click any ✦ line for payload · space to pause · esc"
    _edge_wash_color = Color(0.40, 0.30, 0.20, 0.04)  # sepia barge


func _build_content() -> void:
    var panel := PanelContainer.new()
    panel.set_anchors_preset(Control.PRESET_FULL_RECT)
    panel.offset_top = 60
    panel.offset_left = 80
    panel.offset_right = -80
    panel.offset_bottom = -56
    var sb := StyleBoxFlat.new()
    sb.bg_color = Color(0.024, 0.018, 0.012, 0.97)
    sb.border_color = Color(0.50, 0.35, 0.20, 0.7)
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
    head.text = "BARGE BBS LINK — recording in progress"
    head.add_theme_color_override("font_color", Color(0.85, 0.70, 0.40))
    head.add_theme_font_size_override("font_size", 11)
    head.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    head_row.add_child(head)
    _time_label = Label.new()
    _time_label.text = "00:00 / 12:34"
    _time_label.add_theme_color_override("font_color", C_TEXT_DIM)
    _time_label.add_theme_font_size_override("font_size", 10)
    head_row.add_child(_time_label)
    var rule := ColorRect.new()
    rule.color = Color(0.50, 0.35, 0.20, 0.5)
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
    fetch.text = "[demon_observer.04 + .05 // barge.bbs + st_judes.bbs // 1 conversation, 2 angles // integrity 0.91 (avg)]"
    fetch.add_theme_color_override("font_color", C_TEXT_DIM)
    fetch.add_theme_font_size_override("font_size", 9)
    fetch.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(fetch)


func _on_diorama_tick(delta: float) -> void:
    if _playing:
        _elapsed += delta * 4.0   # 4x pacing — 12:34 in-fiction = ~3:08 real
    while _lines_shown < _DIALOGUE.size() and float(_DIALOGUE[_lines_shown]["t"]) <= _elapsed:
        _emit_line(_DIALOGUE[_lines_shown])
        _lines_shown += 1
    if _time_label != null and is_instance_valid(_time_label):
        var total := 754  # 12:34
        _time_label.text = "%02d:%02d / 12:34" % [int(_elapsed) / 60, int(_elapsed) % 60]


func _emit_line(line: Dictionary) -> void:
    var sp := str(line["speaker"])
    var text := str(line["text"])
    var is_payload := bool(line.get("is_payload", false))
    var col := C_TEXT
    var prefix := ""
    match sp:
        "DANTE":
            col = Color(0.85, 0.65, 0.30)
            prefix = "DANTE: "
        "QUENT":
            col = Color(0.50, 0.60, 0.85)
            prefix = "QUENT: "
        "system":
            col = C_TEXT_DIM
            prefix = ""
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


# ── Ambient: mixed 18 Hz + 7 Hz ticks (two demons) + river slap ──

var _tick_d_phase: float = 0.0
var _tick_q_phase: float = 0.0
var _river_phase: float = 0.0


func _ambient_sample(_phase: float, step: float) -> Vector2:
    _tick_d_phase += step * 18.0
    var tick_d := 0.0
    if fmod(_tick_d_phase, 1.0) < 0.025:
        tick_d = -0.025 * (1.0 - fmod(_tick_d_phase, 1.0) / 0.025)
    _tick_q_phase += step * 7.0
    var tick_q := 0.0
    if fmod(_tick_q_phase, 1.0) < 0.04:
        tick_q = -0.025 * (1.0 - fmod(_tick_q_phase, 1.0) / 0.04)
    # River slap — very slow modulated noise burst
    _river_phase += step
    var river := (randf() - 0.5) * 0.02 * (0.5 + 0.5 * sin(_river_phase * 0.3 * TAU))
    var s = tick_d + tick_q + river
    return Vector2(s, s)


func _input(event: InputEvent) -> void:
    super(event)
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_SPACE:
            _playing = not _playing
            get_viewport().set_input_as_handled()
