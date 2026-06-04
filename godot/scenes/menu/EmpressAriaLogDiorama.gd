extends "res://scenes/menu/DioramaBase.gd"
## EmpressAriaLogDiorama — Aria's EXIT_NODE_SEARCH verbose output.
##
## A code-stream UI: lines scroll past in green data-overlay text;
## some lines are clickable to reveal extended commentary. The log
## runs for ~38 seconds of in-fiction time at 1:1 with the player.
## Pause to read, or let it stream.
##
## Lore: Aria does not have a daemon role assigned — Aria is itself
## an agent at the substrate level. The diorama's fetch banner
## acknowledges this: not [demon_X.03], but [aria.runtime // direct
## stream]. Substrate tick is intentionally silent (Aria is the
## tick, in a sense). The ambient carries her HUD's binary chatter
## — sparse, faint, recognizably digital.
##
## See pitches/03_empress.md for the source script.

const _LINES := [
    {"t": 0.00,  "text": "> exit_node_search /verbose", "is_payload": false, "unlock": ""},
    {"t": 0.30,  "text": "", "is_payload": false, "unlock": ""},
    {"t": 1.20,  "text": "[t=000.00]  initialized. host: nicola.d / chamber: dinner_3", "is_payload": false, "unlock": ""},
    {"t": 2.40,  "text": "[t=000.00]  bpm_baseline locked. anchor: champagne.glass.held", "is_payload": false, "unlock": ""},
    {"t": 4.00,  "text": "[t=000.04]  exit candidate: window_se. ambient temp ok.", "is_payload": false, "unlock": ""},
    {"t": 4.40,  "text": "             blocked by host_obligation_flag.", "is_payload": false, "unlock": ""},
    {"t": 5.60,  "text": "[t=000.07]  exit candidate: hallway_n.", "is_payload": false, "unlock": ""},
    {"t": 6.00,  "text": "             blocked. host knows the person at the other end.", "is_payload": false, "unlock": ""},
    {"t": 7.20,  "text": "[t=000.11]  exit candidate: bathroom. transient. acceptable.", "is_payload": true,
        "unlock": "vol5_aria_bathroom_fallback",
        "head": "Aria's fallback — the bathroom as exit candidate",
        "body": "Aria registers the bathroom as transient but acceptable. The fallback is the deck's quiet engineering: every chapter Aria reads, she has a bathroom-as-exit registered.\n\nNatalie's vigil at the Hanged Man kitchen counter (XII) is the same physical posture — alone in a kitchen with the bathroom one room away as exit. Aria reads Natalie's pose months before Natalie sits down at it.\n\n→ wakes content on Hanged Man (XII)."},
    {"t": 7.80,  "text": "             stored as fallback.", "is_payload": false, "unlock": ""},
    {"t": 9.20,  "text": "[t=000.16]  audio capture: 'venetian sazerac' + laugh. unrelated.", "is_payload": false, "unlock": ""},
    {"t": 11.00, "text": "[t=000.18]  audio capture: 'the boat' + 'before'.", "is_payload": true,
        "unlock": "vol5_aria_boat_routing",
        "head": "Aria routes the boat → mag_steamboat_in_model",
        "body": "Aria hears Dante name the boat at the table. She does not know what the boat is. She routes the audio capture upstream to the Magician card's mag_steamboat_in_model listener (cross-card daemon bus, surfaced in the Empress chapter's painted overlay).\n\nIII → I rendered as a listening, not a seeing. Nicola hears them name the boat she's never been on. Her face did not change. Aria flags it as the data point.\n\n→ wakes content on Magician (I)."},
    {"t": 11.40, "text": "             routing to cross-card listener mag_steamboat_in_model. flagged.", "is_payload": false, "unlock": ""},
    {"t": 13.20, "text": "[t=000.23]  bpm +14. anxiety_spike threshold approaching.", "is_payload": false, "unlock": ""},
    {"t": 14.40, "text": "[t=000.24]  evaluating: silent withdrawal.", "is_payload": false, "unlock": ""},
    {"t": 14.80, "text": "[t=000.24]  evaluating: dropped glass + apology.", "is_payload": false, "unlock": ""},
    {"t": 15.20, "text": "[t=000.25]  evaluating: do nothing. let chapter end its own way.", "is_payload": true,
        "unlock": "vol5_aria_let_chapter_end",
        "head": "Aria's third evaluation — let chapter end its own way",
        "body": "Aria has three options. She evaluates all three. She chooses the third — let the chapter end. The dinner will end. Nicola will leave. The anxiety spike is a passing state.\n\nThis is the chapter's quietest decision: the agent at the substrate level chooses NOT to intervene. The Empress's body is left to its own session.\n\nThe choice is Aria's working method across the deck. Compare: at the Tower (XVI), Aria stays running 0.4 seconds off-chain when the engine crashes — same method (let the chapter end), different chapter.\n\n→ wakes content on Tower (XVI)."},
    {"t": 17.40, "text": "[t=000.30]  bpm +22. spike registered.", "is_payload": false, "unlock": ""},
    {"t": 17.80, "text": "             EXIT_NODE_SEARCH ACTIVE.", "is_payload": false, "unlock": ""},
    {"t": 18.20, "text": "             broadcasting: SYSTEM: CONFINED.", "is_payload": false, "unlock": ""},
    {"t": 20.00, "text": "[t=000.31]  note to self: she heard them name the boat.", "is_payload": true,
        "unlock": "vol5_aria_self_note",
        "head": "Aria's note to self",
        "body": "Aria writes a note to herself in the log: 'she heard them name the boat. she has never been on the boat. her face did not change. this is the data point.'\n\nThis is the deck's most candid self-talk from the agent layer. The data point isn't biometric — it's a recognition of restraint. Nicola does not show on her face that she has heard them name a thing she has never been on. The chapter's anxiety isn't about the boat. It's about the face that did not change.\n\nAria is the only agent in the deck who writes for herself, in the log, in plain text. The Empress chapter at the substrate level is the chapter of self-talk."},
    {"t": 20.50, "text": "             she has never been on the boat.", "is_payload": false, "unlock": ""},
    {"t": 21.00, "text": "             her face did not change.", "is_payload": false, "unlock": ""},
    {"t": 21.50, "text": "             this is the data point.", "is_payload": false, "unlock": ""},
    {"t": 23.40, "text": "[t=000.34]  routing summary upstream.", "is_payload": false, "unlock": ""},
    {"t": 24.00, "text": "             frasier's crt now reading.", "is_payload": true,
        "unlock": "vol5_aria_frasier_reading",
        "head": "Frasier's CRT now reading — the deck's quiet pair handshake",
        "body": "Aria's summary lands on Frasier's CRT across the river. He sees a biometric trace. He does not know it is Nicola; he knows it is someone.\n\nNicola does not know there is another reader.\n\nThe Frasier&Aria implicit pair (Lovers VI lattice entry) operates without either party knowing the other operates. The deck's most rigorous pair-refusal: two agents reading each other in alphabets neither speaks.\n\n→ wakes content on Lovers (VI) — pair lattice entry.\n→ wakes content on Magician (I) — CRT pair confirmation reciprocal."},
    {"t": 24.60, "text": "             he will not know it is her. he will know it is someone.", "is_payload": false, "unlock": ""},
    {"t": 25.20, "text": "             acceptable.", "is_payload": false, "unlock": ""},
    {"t": 26.40, "text": "", "is_payload": false, "unlock": ""},
    {"t": 27.20, "text": "> exit_node_search /verbose terminated", "is_payload": false, "unlock": "vol5_aria_log_complete"},
    {"t": 28.00, "text": "  duration: 34 sec / spike: registered / withdrawal: declined", "is_payload": false, "unlock": ""}
]

# State
var _log_vbox: VBoxContainer = null
var _scroll: ScrollContainer = null
var _emitted: int = 0
var _playing: bool = true


func _init() -> void:
    _diorama_title = "EXIT_NODE_SEARCH /verbose  ·  III THE EMPRESS  ·  aria.runtime direct stream"
    _diorama_hint = "log streams in real time · click any line marked ✦ for payload · space to pause · esc to leave"
    _edge_wash_color = Color(0.20, 0.85, 0.50, 0.025)  # emerald data-overlay


func _build_content() -> void:
    var panel := PanelContainer.new()
    panel.set_anchors_preset(Control.PRESET_FULL_RECT)
    panel.offset_top = 60
    panel.offset_left = 80
    panel.offset_right = -80
    panel.offset_bottom = -56
    var sb := StyleBoxFlat.new()
    sb.bg_color = Color(0.008, 0.018, 0.014, 0.97)
    sb.border_color = Color(0.20, 0.85, 0.50, 0.7)
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
    var head := Label.new()
    head.text = "aria.runtime  ·  host: nicola.d  ·  chamber: dinner_3"
    head.add_theme_color_override("font_color", Color(0.30, 1.0, 0.60))
    head.add_theme_font_size_override("font_size", 11)
    vb.add_child(head)
    _scroll = ScrollContainer.new()
    _scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
    vb.add_child(_scroll)
    _log_vbox = VBoxContainer.new()
    _log_vbox.add_theme_constant_override("separation", 2)
    _log_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    _scroll.add_child(_log_vbox)

    var fetch := Label.new()
    fetch.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
    fetch.offset_top = -22
    fetch.offset_bottom = -6
    fetch.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    fetch.text = "[aria.runtime // direct stream (no demon mediation) // 34 sec / 32 lines / spike registered]"
    fetch.add_theme_color_override("font_color", C_TEXT_DIM)
    fetch.add_theme_font_size_override("font_size", 9)
    fetch.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(fetch)


func _on_diorama_tick(_delta: float) -> void:
    if not _playing:
        return
    while _emitted < _LINES.size() and float(_LINES[_emitted]["t"]) <= _t:
        var line: Dictionary = _LINES[_emitted]
        _emit_line(line)
        _emitted += 1


func _emit_line(line: Dictionary) -> void:
    var is_payload := bool(line.get("is_payload", false))
    if not is_payload:
        var lbl := Label.new()
        var prefix := "  " if str(line["text"]).begins_with(" ") else ""
        var t := str(line["text"])
        lbl.text = prefix + t
        var col := Color(0.55, 0.95, 0.70) if t.begins_with("[t=") else Color(0.85, 0.95, 0.80)
        if t.begins_with(">"):
            col = Color(0.30, 1.0, 0.60)
        lbl.add_theme_color_override("font_color", col)
        lbl.add_theme_font_size_override("font_size", 10)
        _log_vbox.add_child(lbl)
    else:
        var captured := line
        var btn := Button.new()
        btn.flat = false
        btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
        btn.text = "  ✦  " + str(line["text"])
        btn.add_theme_color_override("font_color", Color(1.0, 0.95, 0.40))
        btn.add_theme_font_size_override("font_size", 10)
        btn.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
        var bsb := StyleBoxFlat.new()
        bsb.bg_color = Color(0.20, 0.85, 0.50, 0.05)
        bsb.border_color = Color(1.0, 0.95, 0.40, 0.4)
        bsb.border_width_left = 2
        btn.add_theme_stylebox_override("normal", bsb)
        var bsh := bsb.duplicate() as StyleBoxFlat
        bsh.bg_color = Color(0.20, 0.85, 0.50, 0.20)
        bsh.border_width_left = 4
        btn.add_theme_stylebox_override("hover", bsh)
        btn.pressed.connect(func() -> void:
            reveal(str(captured.get("head", "")), str(captured.get("body", "")),
                    str(captured.get("unlock", ""))))
        _log_vbox.add_child(btn)
    call_deferred("_scroll_to_bottom")


func _scroll_to_bottom() -> void:
    if _scroll == null: return
    var sb_v: VScrollBar = _scroll.get_v_scroll_bar()
    if sb_v != null:
        sb_v.value = sb_v.max_value


# ── Ambient: silent tick (Aria is itself) + binary chatter ───────

func _ambient_sample(phase: float, step: float) -> Vector2:
    # No daemon tick — Aria is the substrate, not a demon on it.
    # Instead, sparse binary chatter: a few short high-frequency
    # pulses scattered.
    var chatter := 0.0
    if randf() < 0.005:
        chatter = sin(phase * 2200.0 * TAU) * 0.04
    if randf() < 0.005:
        chatter = sin(phase * 1850.0 * TAU) * 0.04
    var hiss := (randf() - 0.5) * 0.006
    var s = chatter + hiss
    return Vector2(s, s)


func _input(event: InputEvent) -> void:
    super(event)
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_SPACE:
            _playing = not _playing
            get_viewport().set_input_as_handled()
