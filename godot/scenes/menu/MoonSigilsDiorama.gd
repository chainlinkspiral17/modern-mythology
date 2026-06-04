extends "res://scenes/menu/DioramaBase.gd"
## MoonSigilsDiorama — the 4:3 static field with three sigils
## legible within. Natalie's reading of her own writing.
##
## The Hanged Man (XII) painted the three sigils as unfinished;
## the Moon (XVIII) renders them in static. The diorama renders
## the static as an ASCII field that gradually clarifies the three
## sigils. Click each sigil to read Natalie's gloss + claim.
##
## Lore: daemon_listener.18 surfaces this (Elicia's archive has
## the notebook from XII; the daemon cross-references it against
## the broadcast Natalie is receiving). Substrate tick at 4 Hz
## (the 4:3 static crawl rate).

const _SIGILS := [
    {
        "id": "sigil_1_candle",
        "label": "[1] candle, single wick, flame as open hand",
        "rect": [0.18, 0.34, 0.22, 0.30],
        "ascii": ".·:·.\n. * .\n :|:\n :|:\n .|.\n  |  \n  ·",
        "reading": "\"What burns is what was given to me. The giver is not the flame. The flame is mine. When the wax is gone I am the candle.\"\n\nNatalie's later annotation: simon gave me the candle. the candle is mine. simon is not the flame. simon is the giver. the giver was never the flame.\n\n(it took me four hours at the counter to read this sigil from the page i had drawn. it took me fourteen seconds to read it from the static.)",
        "unlock": "vol5_moon_sigil_1_read"
    },
    {
        "id": "sigil_2_phone",
        "label": "[2] phone receiver off the hook, three rings",
        "rect": [0.42, 0.34, 0.22, 0.30],
        "ascii": "  o\n_,'_\n( ( (\n |  \n .  \n   ",
        "reading": "\"Three calls leave me. The receiver is mine. The not-answered is not me. The not-answered is the receiver on the other end. I am where the calls left from.\"\n\nNatalie's later annotation: the phone log on the painted card was my outbound record. it was not simon's silence. the chapter is not 'simon did not call.' the chapter is 'i made three calls.' that is mine. that is what i did.",
        "unlock": "vol5_moon_sigil_2_read"
    },
    {
        "id": "sigil_3_narwhal",
        "label": "[3] narwhal on keyring + transparent narwhal behind",
        "rect": [0.66, 0.34, 0.22, 0.30],
        "ascii": "    ~o)>\n  ~~~~~\n .o)>\n  ___",
        "reading": "\"The carrier and the carried are the same creature. What you take with you is also watching you. The water you carry is the water you are in.\"\n\nNatalie's later annotation: the apartment key has a narwhal on it. there is another narwhal in the static. they are the same narwhal. the chapter is not 'i lost the dog (faith) and replaced her with a fish' — the chapter is 'what i carry watches me back, and that is also a kind of carrying.'",
        "unlock": "vol5_moon_sigil_3_read"
    }
]

# Static field state
var _static_chars := "·.:·*¦|—_~ "
var _static_label: RichTextLabel = null
var _static_lines: Array = []   # array of arrays of chars
var _next_scramble_at: float = 0.0


func _init() -> void:
    _diorama_title = "SIGILS IN STATIC  ·  XVIII THE MOON  ·  Natalie's reading"
    _diorama_hint = "click a sigil to read Natalie's gloss · esc to leave"
    _edge_wash_color = Color(0.95, 0.95, 0.40, 0.025)


func _build_content() -> void:
    # Static field — a panel filled with shifting characters,
    # with three sigil ASCII insets overlaid.
    var field := PanelContainer.new()
    field.set_anchors_preset(Control.PRESET_CENTER)
    field.offset_left = -520; field.offset_right = 520
    field.offset_top = -260; field.offset_bottom = 220
    var sb := StyleBoxFlat.new()
    sb.bg_color = Color(0.020, 0.020, 0.018, 0.94)
    sb.border_color = Color(0.95, 0.95, 0.40, 0.5)
    sb.set_border_width_all(1)
    field.add_theme_stylebox_override("panel", sb)
    add_child(field)

    _static_label = RichTextLabel.new()
    _static_label.bbcode_enabled = true
    _static_label.fit_content = false
    _static_label.scroll_active = false
    _static_label.add_theme_color_override("default_color",
        Color(C_TEXT_DIM.r, C_TEXT_DIM.g, C_TEXT_DIM.b, 0.7))
    _static_label.add_theme_font_size_override("normal_font_size", 11)
    _static_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
    field.add_child(_static_label)

    # Sigil hotspots — invisible buttons overlaid on the static field
    for s_v in _SIGILS:
        var s: Dictionary = s_v
        var captured := s
        # Each sigil is shown as an ASCII Label on top of the static,
        # then a button is placed over it
        var lbl := Label.new()
        lbl.text = str(s["ascii"])
        lbl.add_theme_color_override("font_color", Color(1.0, 1.0, 0.60))
        lbl.add_theme_font_size_override("font_size", 14)
        lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        var rect: Array = s["rect"]
        lbl.anchor_left = float(rect[0])
        lbl.anchor_top = float(rect[1])
        lbl.anchor_right = float(rect[0]) + float(rect[2])
        lbl.anchor_bottom = float(rect[1]) + float(rect[3])
        lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
        field.add_child(lbl)
        make_hotspot(field, rect, str(s["label"]),
            func() -> void: _show_sigil(captured))

    var fetch := Label.new()
    fetch.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
    fetch.offset_top = -22
    fetch.offset_bottom = -6
    fetch.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    fetch.text = "[demon_listener.18 // natalie.broadcast // 3 sigils legible // integrity 0.99]"
    fetch.add_theme_color_override("font_color", C_TEXT_DIM)
    fetch.add_theme_font_size_override("font_size", 9)
    fetch.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(fetch)


func _show_sigil(s: Dictionary) -> void:
    reveal(str(s["label"]), str(s["reading"]), str(s["unlock"]))


func _on_diorama_tick(_delta: float) -> void:
    if _t >= _next_scramble_at:
        _next_scramble_at = _t + 0.20
        _scramble_static()


func _scramble_static() -> void:
    if _static_label == null or not is_instance_valid(_static_label):
        return
    var rows := 28
    var cols := 100
    var lines := PackedStringArray()
    for r in rows:
        var s := ""
        for c in cols:
            s += _static_chars[randi() % _static_chars.length()]
        lines.append(s)
    _static_label.text = "\n".join(lines)


# ── Ambient: 4 Hz static crawl + low broadcast hum ───────────────

var _tick_phase: float = 0.0


func _ambient_sample(phase: float, step: float) -> Vector2:
    _tick_phase += step * 4.0
    var tick := 0.0
    if fmod(_tick_phase, 1.0) < 0.04:
        tick = -0.03 * (1.0 - fmod(_tick_phase, 1.0) / 0.04)
    # broadcast hum — slowly modulated grey-noise
    var hum := sin(phase * 80.0 * TAU) * 0.012
    var noise := (randf() - 0.5) * 0.020
    var s = tick + hum + noise
    return Vector2(s, s)
