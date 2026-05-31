extends "res://scenes/menu/TarotVisualizerBase.gd"
## MagicianVisualizer — minimal, card-first.
##
## Card dominates. Two thin strips at top + bottom for chrome.
## Click on the card → ambient synth pulse. Click puzzle-hook
## hotspots → cipher panel slides up + signature chord.

var status_label: Label
var cipher_panel: PanelContainer
var cipher_log: RichTextLabel
var sigil_t: float = 0.0
var sigil_pulse: float = 0.0


func _init() -> void:
    _card_path  = "res://assets/gallery/magician.png"
    _hooks_path = "res://resources/puzzle_hooks/magician.json"
    _ambient_audio_path = "res://assets/audio/bgm/vol5_warehouse_drone.ogg"
    C_BG = Color(0.020, 0.025, 0.030)
    C_GOLD = Color(0.55, 0.85, 0.88)
    C_GOLD_HI = Color(0.82, 0.98, 1.0)


func _build_chrome() -> void:
    var bg := ColorRect.new()
    bg.color = C_BG
    bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    bg.mouse_filter = Control.MOUSE_FILTER_STOP
    add_child(bg)

    if _card_path != "" and ResourceLoader.exists(_card_path):
        card_rect = TextureRect.new()
        card_rect.texture = load(_card_path)
        card_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
        card_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
        card_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
        card_rect.mouse_filter = Control.MOUSE_FILTER_PASS
        card_rect.z_index = 1
        add_child(card_rect)
        card_rect.gui_input.connect(_on_card_click)

    _build_hotspots()

    var top := _strip_panel(true)
    var top_row := HBoxContainer.new()
    top_row.add_theme_constant_override("separation", 12)
    top.add_child(top_row)
    _hdr_label(top_row, "I · THE MAGICIAN",
               "Cathedral of Rust and Code · vol.5 ch.1")
    var close := Button.new()
    close.text = "[ × CLOSE ]"
    close.flat = true
    close.add_theme_color_override("font_color", C_GOLD_HI)
    close.pressed.connect(func() -> void: closed.emit())
    top_row.add_child(close)

    var bot := _strip_panel(false)
    var bot_row := HBoxContainer.new()
    bot_row.add_theme_constant_override("separation", 16)
    bot.add_child(bot_row)

    var sigil_btn := Button.new()
    sigil_btn.text = "  ∞  TRACE THE SIGIL"
    sigil_btn.add_theme_color_override("font_color", C_GOLD_HI)
    sigil_btn.add_theme_font_size_override("font_size", 13)
    var ss := StyleBoxFlat.new()
    ss.bg_color = Color(C_GOLD.r * 0.3, C_GOLD.g * 0.3, C_GOLD.b * 0.3, 0.6)
    ss.border_color = C_GOLD
    ss.set_border_width_all(1)
    sigil_btn.add_theme_stylebox_override("normal", ss)
    var ssh := ss.duplicate() as StyleBoxFlat
    ssh.bg_color = Color(C_GOLD.r * 0.55, C_GOLD.g * 0.55, C_GOLD.b * 0.55, 0.7)
    ssh.border_color = C_GOLD_HI
    sigil_btn.add_theme_stylebox_override("hover", ssh)
    sigil_btn.pressed.connect(_on_sigil)
    bot_row.add_child(sigil_btn)

    status_label = Label.new()
    status_label.text = "click hotspots on the card · trace the sigil ·"
    status_label.add_theme_color_override("font_color",
        Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.7))
    status_label.add_theme_font_size_override("font_size", 10)
    status_label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    status_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    bot_row.add_child(status_label)

    cipher_panel = PanelContainer.new()
    cipher_panel.anchor_left = 0.25; cipher_panel.anchor_right = 0.75
    cipher_panel.anchor_top = 1; cipher_panel.anchor_bottom = 1
    cipher_panel.offset_top = -180; cipher_panel.offset_bottom = -70
    var cps := StyleBoxFlat.new()
    cps.bg_color = Color(0.0, 0.05, 0.06, 0.92)
    cps.border_color = C_GOLD_HI
    cps.set_border_width_all(1)
    cipher_panel.add_theme_stylebox_override("panel", cps)
    cipher_panel.z_index = 6
    cipher_panel.visible = false
    add_child(cipher_panel)
    cipher_log = RichTextLabel.new()
    cipher_log.bbcode_enabled = true
    cipher_log.fit_content = true
    cipher_log.add_theme_font_size_override("normal_font_size", 11)
    cipher_log.add_theme_color_override("default_color", C_TEXT)
    cipher_panel.add_child(cipher_log)


func _hdr_label(row: HBoxContainer, title_text: String, sub_text: String) -> void:
    var t := Label.new()
    t.text = title_text
    t.add_theme_color_override("font_color", C_GOLD_HI)
    t.add_theme_font_size_override("font_size", 15)
    t.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    row.add_child(t)
    var s := Label.new()
    s.text = sub_text
    s.add_theme_color_override("font_color",
        Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.7))
    s.add_theme_font_size_override("font_size", 10)
    s.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    s.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    row.add_child(s)


func _strip_panel(top: bool) -> PanelContainer:
    var p := PanelContainer.new()
    p.anchor_left = 0; p.anchor_right = 1
    if top:
        p.anchor_top = 0; p.anchor_bottom = 0
        p.offset_bottom = 40
    else:
        p.anchor_top = 1; p.anchor_bottom = 1
        p.offset_top = -60
    var sb := StyleBoxFlat.new()
    sb.bg_color = Color(0, 0, 0, 0.65)
    sb.border_color = C_GOLD
    if top: sb.border_width_bottom = 1
    else:   sb.border_width_top = 1
    p.add_theme_stylebox_override("panel", sb)
    p.z_index = 5
    add_child(p)
    return p


func _build_thematic_widget() -> void:
    pass


func _on_card_click(event: InputEvent) -> void:
    if event is InputEventMouseButton and event.pressed:
        _active_notes.append({
            "time": 0.0, "freq": 165.0 + randf() * 80,
            "wave": "sawtooth",
            "atk": 0.005, "dur": 0.20, "rel": 0.2,
        })


func _on_sigil() -> void:
    sigil_pulse = 1.0
    # A-C#-E chord, square waves
    for f in [220.0, 277.2, 329.6]:
        _active_notes.append({
            "time": 0.0, "freq": f, "wave": "square",
            "atk": 0.005, "dur": 0.4, "rel": 0.3,
        })
    if status_label != null:
        status_label.text = "∞ closed · chord A C# E"
    SaveSystem.mark_unlocked("vol5_iron_summons_link")


func _on_hotspot(hs: Dictionary) -> void:
    super(hs)
    if cipher_panel == null or cipher_log == null: return
    cipher_log.clear()
    cipher_log.append_text("[color=#a8e8f0]▷ %s[/color]\n" %
        str(hs.get("interact", hs.get("id", ""))))
    var matched: Dictionary = {}
    var hs_id = str(hs.get("id",""))
    for c_v in hooks.get("ciphers", []):
        var c: Dictionary = c_v
        var cid = str(c.get("id",""))
        if cid == hs_id or hs_id.contains(cid) or cid.contains(hs_id):
            matched = c; break
    if not matched.is_empty():
        if matched.has("text"):
            cipher_log.append_text("  %s\n" % str(matched["text"]))
        if matched.has("encoding_hint"):
            cipher_log.append_text(
                "  [color=#3a7878]↳ %s[/color]\n" %
                str(matched["encoding_hint"]))
        if matched.has("reveals"):
            cipher_log.append_text(
                "  [color=#a8e8f0]→ reveals: %s[/color]\n" %
                str(matched["reveals"]))
    cipher_panel.visible = true
    cipher_panel.modulate.a = 0
    var tw := cipher_panel.create_tween()
    tw.tween_property(cipher_panel, "modulate:a", 1.0, 0.25)
    _active_notes.append({
        "time": 0.0, "freq": 220.0, "wave": "sawtooth",
        "atk": 0.005, "dur": 0.5, "rel": 0.5,
    })


func _process(delta: float) -> void:
    super(delta)
    sigil_t += delta
    sigil_pulse = maxf(0.0, sigil_pulse - delta * 1.2)
