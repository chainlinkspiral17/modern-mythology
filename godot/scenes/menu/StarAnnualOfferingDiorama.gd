extends "res://scenes/menu/DioramaBase.gd"
## StarAnnualOfferingDiorama — the un-named figure's annual offering.
##
## Thursday night, hours after the Tower's collapse. The painted XVII
## arrives in the same frame as XVI's smoke; the chapter is the open
## sky that follows. The un-named figure walks to the Graustark
## riverbank she stood on at VIII (lion's jaw) and performs the
## offering she has performed once a year for four years. Two
## vessels: one for the survivors she pulled (+IV), one for the
## people she could not reach (—). The river receives both.
##
## This is the deck's first witness-log diorama: no dialogue, only
## the demon's recorded observations. demon_archivist.17 holds the
## anniversary records — every year a single page filed under
## RECOVERED PERSONS LOG continued, signed with the same dash. The
## archivist watches because the figure stopped filing the reports
## with D'Ambrosio Industrial in the second year; she did not stop
## the ritual.
##
## Frasier (from the still-smoking render farm at the edge of the
## clearing) is the only other witness this Thursday; his presence
## is registered as a faint co-observation tick, not a voice. He
## does not approach. He notices.
##
## Substrate ticks: 8 Hz (Star) + a single river-current hush
## modulated by a low 0.3 Hz pulse (the river's substrate breath).

const _DIALOGUE := [
    {"t": 0,    "speaker": "system", "text": "[anniversary offering log / graustark bank / late thursday / sky uncovered / observer: demon_archivist.17 / co-observer: frasier (passive, render farm silhouette)]", "is_payload": false, "unlock": ""},
    {"t": 4,    "speaker": "FRAME",  "text": "the clearing — the smoke from the render farm at the eastern edge is still rising. the sky has eight stars visible. the largest is dead-center overhead.", "is_payload": false, "unlock": ""},
    {"t": 14,   "speaker": "OBS",    "text": "she arrives on foot from the north road. she is alone. she carries two clay vessels, one in each hand, the same vessels she carried last year.", "is_payload": true, "unlock": "vol5_star_figure_arrives",
        "head": "she arrives — same vessels, fourth year",
        "body": "The un-named figure of XVII arrives at the Graustark riverbank. demon_archivist.17 confirms by glaze pattern that the two vessels she carries are the same vessels she used in years one, two, and three.\n\nThe vessels are not symbolic. They are the same hand-fired clay she has used four times. She does not buy new ones. She does not refill them between years. She empties them into the river and walks home and puts them back on the shelf.\n\n→ wakes content on Strength (VIII) and Tower (XVI)."},
    {"t": 28,   "speaker": "OBS",    "text": "she sets the vessels on the flat stone at the bank's edge. she does not kneel. she stands the way she stood at VIII — weight even, hands free.", "is_payload": false, "unlock": ""},
    {"t": 42,   "speaker": "FRAME",  "text": "the render farm to the east continues to smoke. a single silhouette at the farm's outer fence has stopped walking. it does not move toward her. it does not move away.", "is_payload": true, "unlock": "vol5_star_frasier_co_witness",
        "head": "Frasier sees her",
        "body": "Frasier, walking the perimeter of the still-smoking render farm at the Tower's aftermath, sees the un-named figure on the riverbank. He stops walking. He does not approach.\n\nFrasier and the un-named figure have not met in any chapter the deck has rendered. They do not meet here. He registers her presence the way a CRT registers a vital sign — a small change in the field, noted without commentary.\n\nThe Magician (I) and Strength (VIII) share the lemniscate as a sigil; the engineer-and-mystic mirror has been quiet through vol5. The Star chapter renders one moment of contact: Frasier sees her perform the offering. He does not record it. demon_archivist.17 does.\n\n→ wakes content on Magician (I) and Tower (XVI)."},
    {"t": 58,   "speaker": "OBS",    "text": "she removes a folded page from her coat. the page is the same form as last year — pre-printed header, fine font, D'AMBROSIO INDUSTRIAL — RECOVERED PERSONS LOG. she stopped filing these in year two. she still writes them.", "is_payload": true, "unlock": "vol5_star_form_continued",
        "head": "the form she stopped filing",
        "body": "She continues to write the recovered-persons log. She stopped submitting them to D'Ambrosio Industrial in year two — after Antonio's first questions about why the rescue list and the official casualty list disagreed.\n\nShe writes them anyway. demon_archivist.17 has the four pages — years one, two, three, and (in twelve minutes) four. The pages are identical in format and divergent only in the count.\n\nThe deck's quietest indictment is here: she does not stop performing the labor; she stops performing the labor to an institution that would use it against the people she labored for. Her continued discipline is the discipline of a witness who has fired her employer.\n\n→ wakes the Nexus thread. Cross-wakes content on Strength (VIII) and Hermit (IX)."},
    {"t": 78,   "speaker": "OBS",    "text": "she reads the page once, silently. she does not move her lips. she folds the page back along its original creases.", "is_payload": false, "unlock": ""},
    {"t": 94,   "speaker": "OBS",    "text": "she lifts the first vessel. the inscription on the inner rim, the +IV mark, faces her. she does not look at it; she knows where it is.", "is_payload": true, "unlock": "vol5_star_pulled_four",
        "head": "+IV — the four she pulled",
        "body": "The first vessel is marked +IV on the inner rim. The four people she pulled from the water at the Sinkhole event. demon_archivist.17 holds the names; the deck does not render them. She knows them; she does not say them; she pours.\n\nThe gesture is precise. She tips the vessel until it empties into the river. She does not rush. She does not say a name as the water leaves. She has decided that the names are not for the air; they are for the water that received the people.\n\n→ wakes the Nexus thread."},
    {"t": 116,  "speaker": "FRAME",  "text": "the river accepts the pour. the surface registers as eight rings — concentric — that move outward and disperse. observer notes: the count of rings matches the count of stars overhead.", "is_payload": true, "unlock": "vol5_star_eight_rings_eight_stars",
        "head": "eight rings, eight stars",
        "body": "demon_archivist.17 records the surface response: the first vessel's pour produces eight concentric rings on the river. The number matches the eight stars visible overhead.\n\nThe Hierophant's eight stained-glass segments (inverted to the sky as the Star's eight) are also the count of the river's reception. Same number, three media: stained glass, sky, river. The chapter's count is constant across registers.\n\nThe largest star, dead-center, is the central ring's source. The figure does not look up. She does not need to.\n\n→ wakes content on Hierophant (V)."},
    {"t": 138,  "speaker": "OBS",    "text": "she sets the first vessel back on the stone. she lifts the second.", "is_payload": false, "unlock": ""},
    {"t": 150,  "speaker": "OBS",    "text": "the inscription on the second vessel's inner rim is a single dash — the same dash she signs her name with. the unreachable.", "is_payload": true, "unlock": "vol5_star_could_not_reach",
        "head": "— the unreachable",
        "body": "The second vessel is marked with a single dash. The people she could not reach at the Sinkhole event. demon_archivist.17 holds an estimate of the count from the cross-referenced casualty rolls; the deck does not render it. She does not write the number on the vessel.\n\nThe dash is the same dash she uses to sign her name on the recovered-persons log. The unreachable receive the same signature she uses for herself. She has decided that her name and their absence are the same shape.\n\n→ wakes the Nexus thread."},
    {"t": 174,  "speaker": "OBS",    "text": "she pours the second vessel. she does not look at the river while she pours. she looks at the eastern edge of the clearing.", "is_payload": true, "unlock": "vol5_star_looks_east",
        "head": "she looks at the smoke",
        "body": "While pouring the second vessel — the unreachable — she looks east. Toward the still-smoking render farm. Toward the silhouette at the fence.\n\ndemon_archivist.17 cannot determine whether she sees Frasier; the distance is sufficient that the silhouette could be any standing object. The observer notes only that her gaze and the line to the farm coincide.\n\nThe gesture is the chapter's quietest interaction: an offering for the unreachable, performed in the direction of the survivor who is the chapter's most visible witness to the collapse. The Star's hope reads here as: the unreachable receive the offering; the visible receive a look.\n\n→ wakes content on Tower (XVI)."},
    {"t": 198,  "speaker": "FRAME",  "text": "the river accepts the second pour. the surface registers as a single long ring that moves downstream and does not disperse. observer notes: this is the second vessel's signature. it is the same response as last year and the year before.", "is_payload": false, "unlock": ""},
    {"t": 218,  "speaker": "OBS",    "text": "she sets the second vessel beside the first. she unfolds the page once more, lays it on the stone, and signs the bottom of it with a small dash made by her thumbnail in pencil.", "is_payload": true, "unlock": "vol5_star_signs_dash",
        "head": "the dash signature",
        "body": "She signs the year's page with the same dash she has used since year one. demon_archivist.17 confirms the dash is identical in length and angle across the four pages; she draws it by muscle memory.\n\nThe dash is the chapter's most repeated character. It appears: as her surname on the recovered-persons log; as her surname on Strength's riverbank reflection (str_rescuer_signature); as the inscription on the second vessel's rim; as her year-mark on the annual page. Four occurrences, one stroke.\n\nThe deck's most consistent typographic motif is also its quietest accusation: the dash is what the chapter renders where a name would otherwise be. She has chosen this. The chapter respects the choice.\n\n→ wakes content across the deck (her appearances)."},
    {"t": 244,  "speaker": "OBS",    "text": "she folds the page and puts it back in her coat. she lifts both vessels — empty now — and turns to leave.", "is_payload": false, "unlock": ""},
    {"t": 258,  "speaker": "FRAME",  "text": "the silhouette at the render farm's fence has not moved. it watches her walk north until the clearing's edge takes her. then it resumes walking the perimeter.", "is_payload": false, "unlock": ""},
    {"t": 274,  "speaker": "OBS",    "text": "she walks the same north road she arrived on. she does not look back. she will not return to this bank for one year.", "is_payload": true, "unlock": "vol5_star_walks_home",
        "head": "she walks home",
        "body": "She walks the north road home. She does not look back at the river. She does not look back at the smoke. She does not look back at the silhouette.\n\nShe will perform this offering once more next year, and once more the year after, and once more the year after that. demon_archivist.17 has standing instructions to maintain the log indefinitely; the figure has not specified an end date. She has not decided whether the discipline ends.\n\nThe Star chapter's hope, rendered: the offering is annual; the offering does not end; the offering is also not a sentence. She gets to walk home.\n\n→ wakes content on Strength (VIII), Hermit (IX), and the Sinkhole Nexus thread across the deck."},
    {"t": 294,  "speaker": "system", "text": "[offering closes 22:51 local. demon_archivist.17 files year four under recovered_persons_log/y04.txt. frasier returns to the inner perimeter of the render farm. the river continues. the sky continues. the eight stars are still eight stars.]", "is_payload": true, "unlock": "vol5_star_offering_logged",
        "head": "year four · filed",
        "body": "demon_archivist.17 files year four of the offering log. The file naming convention is the archivist's: recovered_persons_log/y01.txt, y02.txt, y03.txt, y04.txt. The four files are kept on a substrate partition the archivist does not share with any other demon.\n\nThe Frog's reading on the un-named figure, reserved for XXI: 'she did what she could. she does what she does. she is allowed to walk home.'\n\nThe Star card's hope, completed across registers: hope is what becomes visible when the cover is gone; the cover is the institutional roof, the unprocessed grief, the obligation to be named. She gets the open sky. She gets to walk home. The river takes the rest.\n\n→ wakes content on Strength (VIII), Hermit (IX), Tower (XVI), Magician (I), World (XXI), and the Sinkhole Nexus thread."}
]

# Playback state
var _playing: bool = true
var _elapsed: float = 0.0
var _lines_shown: int = 0
var _dialogue_vbox: VBoxContainer = null
var _scroll: ScrollContainer = null
var _time_label: Label = null


func _init() -> void:
    _diorama_title = "ANNUAL OFFERING  ·  XVII  ·  the un-named figure at the river  ·  year four"
    _diorama_hint = "witness log streams at 6× real-time · click ✦ moments · space to pause · esc"
    _edge_wash_color = Color(0.15, 0.25, 0.35, 0.04)


func _build_content() -> void:
    var panel := PanelContainer.new()
    panel.set_anchors_preset(Control.PRESET_FULL_RECT)
    panel.offset_top = 60
    panel.offset_left = 80
    panel.offset_right = -80
    panel.offset_bottom = -56
    var sb := StyleBoxFlat.new()
    sb.bg_color = Color(0.018, 0.022, 0.028, 0.97)
    sb.border_color = Color(0.45, 0.55, 0.75, 0.7)
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
    head.text = "GRAUSTARK BANK  ·  Thursday  ·  22:42 local  ·  sky uncovered after XVI"
    head.add_theme_color_override("font_color", Color(0.70, 0.78, 0.88))
    head.add_theme_font_size_override("font_size", 11)
    head.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    head_row.add_child(head)
    _time_label = Label.new()
    _time_label.text = "00:00 / 04:54"
    _time_label.add_theme_color_override("font_color", C_TEXT_DIM)
    _time_label.add_theme_font_size_override("font_size", 10)
    head_row.add_child(_time_label)
    var rule := ColorRect.new()
    rule.color = Color(0.45, 0.55, 0.75, 0.5)
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
    fetch.text = "[demon_archivist.17 // 4:54 witness log // co-observer: frasier (passive) // integrity 0.99 // filed: recovered_persons_log/y04.txt]"
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
        _time_label.text = "%02d:%02d / 04:54" % [int(_elapsed) / 60, int(_elapsed) % 60]


func _emit_line(line: Dictionary) -> void:
    var sp := str(line["speaker"])
    var text := str(line["text"])
    var is_payload := bool(line.get("is_payload", false))
    var col := C_TEXT
    var prefix := ""
    match sp:
        "OBS":
            col = Color(0.70, 0.78, 0.88)
            prefix = "OBS:   "
        "FRAME":
            col = Color(0.60, 0.65, 0.75)
            prefix = "FRAME: "
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


# ── Ambient: 8 Hz Star tick + low river breath (0.3 Hz modulation) ──

var _tick_phase: float = 0.0
var _breath_phase: float = 0.0


func _on_diorama_tick_audio() -> void:
    pass


func _ambient_sample(phase: float, step: float) -> Vector2:
    _tick_phase += step * 8.0
    var tick := 0.0
    if fmod(_tick_phase, 1.0) < 0.025:
        tick = -0.020 * (1.0 - fmod(_tick_phase, 1.0) / 0.025)
    _breath_phase += step * 0.3
    var breath := sin(_breath_phase * TAU) * 0.5 + 0.5  # 0..1
    var hush := (randf() - 0.5) * 0.012 * (0.4 + 0.6 * breath)
    var s = tick + hush
    return Vector2(s, s)


func _input(event: InputEvent) -> void:
    super(event)
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_SPACE:
            _playing = not _playing
            get_viewport().set_input_as_handled()
