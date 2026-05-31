extends "res://scenes/menu/TarotVisualizerBase.gd"
## FoolVisualizer — minimal, card-first.
##
## Card art is the dominant visual. UI lives in narrow strips at top
## and bottom only — never over the painted card body.
##
##   Top strip (40px):  title · subtitle · close
##   Bottom strip (60px): status line · wipe-counter button · ambient meter
##
## Hover ANY puzzle-hook hotspot on the card → a soft gold ring fades
## in around it with a one-line caption. Click → cipher panel slides
## up from the bottom, plays the Fool's synth tone, fires the unlock.
##
## Click anywhere else on the card → tiny ripple from cursor + soft
## triangle tone. Lets the player feel the card responds.
##
## Wipe counter is a single button in the bottom strip — click it to
## tick up, with a quick rag-sweep flash. Counter visible. 64 wipes
## unlocks the alt prologue (same hook as before).

var status_strip: HBoxContainer
var status_label: Label
var wipe_btn: Button
var wipe_count: int = 0
var _wipe_pulse: float = 0.0

# Cipher panel that slides in from bottom on hotspot click
var cipher_panel: PanelContainer
var cipher_log: RichTextLabel

# Hotspot hover state
var _hover_btn: Button = null

# Ambient meter
var ambient_meter: ProgressBar
var _ambient_t: float = 0.0


func _init() -> void:
    _card_path  = "res://assets/gallery/fool.png"
    _hooks_path = "res://resources/puzzle_hooks/fool.json"
    _ambient_audio_path = "res://assets/audio/bgm/title_theme.ogg"
    C_BG = Color(0.04, 0.034, 0.020)
    C_GOLD = Color(0.85, 0.66, 0.29)
    C_GOLD_HI = Color(1.0, 0.85, 0.40)


func _build_chrome() -> void:
    # Background fill — black for letterbox if card aspect doesn't fit
    var bg := ColorRect.new()
    bg.color = C_BG
    bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    bg.mouse_filter = Control.MOUSE_FILTER_STOP
    add_child(bg)

    # CARD — full screen, dominant
    if _card_path != "" and ResourceLoader.exists(_card_path):
        card_rect = TextureRect.new()
        card_rect.texture = load(_card_path)
        card_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
        card_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
        card_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
        card_rect.mouse_filter = Control.MOUSE_FILTER_PASS
        card_rect.z_index = 1
        add_child(card_rect)
        # Click-to-feel on card
        card_rect.gui_input.connect(_on_card_click)

    # Hotspot overlay (transparent buttons over puzzle_hooks rects).
    # Base class builds these; we restyle them in _post_build below.
    _build_hotspots()

    # Top strip — 40px tall, opaque-ish gold panel
    var top := PanelContainer.new()
    top.anchor_left = 0; top.anchor_right = 1
    top.anchor_top = 0;  top.anchor_bottom = 0
    top.offset_bottom = 40
    var tps := StyleBoxFlat.new()
    tps.bg_color = Color(0, 0, 0, 0.65)
    tps.border_color = C_GOLD
    tps.border_width_bottom = 1
    top.add_theme_stylebox_override("panel", tps)
    top.z_index = 5
    add_child(top)

    var top_row := HBoxContainer.new()
    top_row.add_theme_constant_override("separation", 12)
    top.add_child(top_row)

    var title := Label.new()
    title.text = "0 · THE FOOL"
    title.add_theme_color_override("font_color", C_GOLD_HI)
    title.add_theme_font_size_override("font_size", 15)
    title.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    top_row.add_child(title)

    var sub := Label.new()
    sub.text = "between acts · D'Ambrosio's · 3:47 AM"
    sub.add_theme_color_override("font_color",
        Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.7))
    sub.add_theme_font_size_override("font_size", 10)
    sub.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    sub.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    top_row.add_child(sub)

    var close := Button.new()
    close.text = "[ × CLOSE ]"
    close.flat = true
    close.add_theme_color_override("font_color", C_GOLD_HI)
    close.pressed.connect(func() -> void: closed.emit())
    top_row.add_child(close)

    # Bottom strip — 60px tall: wipe button + status + ambient meter
    var bot := PanelContainer.new()
    bot.anchor_left = 0; bot.anchor_right = 1
    bot.anchor_top = 1;  bot.anchor_bottom = 1
    bot.offset_top = -60
    var bps := StyleBoxFlat.new()
    bps.bg_color = Color(0, 0, 0, 0.7)
    bps.border_color = C_GOLD
    bps.border_width_top = 1
    bot.add_theme_stylebox_override("panel", bps)
    bot.z_index = 5
    add_child(bot)

    var bot_row := HBoxContainer.new()
    bot_row.add_theme_constant_override("separation", 16)
    bot.add_child(bot_row)

    # Big wipe button — the only persistent interactive UI
    wipe_btn = Button.new()
    wipe_btn.text = "  WIPE THE COUNTER  ( 0 / 64 )"
    wipe_btn.add_theme_color_override("font_color", C_GOLD_HI)
    wipe_btn.add_theme_font_size_override("font_size", 13)
    var wbs := StyleBoxFlat.new()
    wbs.bg_color = Color(C_GOLD.r * 0.3, C_GOLD.g * 0.3, C_GOLD.b * 0.3, 0.6)
    wbs.border_color = C_GOLD
    wbs.set_border_width_all(1)
    wipe_btn.add_theme_stylebox_override("normal", wbs)
    var wbh := wbs.duplicate() as StyleBoxFlat
    wbh.bg_color = Color(C_GOLD.r * 0.55, C_GOLD.g * 0.55, C_GOLD.b * 0.55, 0.7)
    wbh.border_color = C_GOLD_HI
    wipe_btn.add_theme_stylebox_override("hover", wbh)
    wipe_btn.pressed.connect(_do_wipe)
    bot_row.add_child(wipe_btn)

    status_label = Label.new()
    status_label.text = "click a hotspot on the card · or wipe ·"
    status_label.add_theme_color_override("font_color",
        Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.7))
    status_label.add_theme_font_size_override("font_size", 10)
    status_label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    status_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    bot_row.add_child(status_label)

    var amb_lbl := Label.new()
    amb_lbl.text = "♬ amb"
    amb_lbl.add_theme_color_override("font_color",
        Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.5))
    amb_lbl.add_theme_font_size_override("font_size", 9)
    amb_lbl.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    bot_row.add_child(amb_lbl)

    ambient_meter = ProgressBar.new()
    ambient_meter.custom_minimum_size = Vector2(140, 14)
    ambient_meter.max_value = 1.0
    ambient_meter.min_value = 0.0
    ambient_meter.show_percentage = false
    bot_row.add_child(ambient_meter)

    # Cipher panel — hidden until a hotspot is clicked, slides up
    cipher_panel = PanelContainer.new()
    cipher_panel.anchor_left = 0.25; cipher_panel.anchor_right = 0.75
    cipher_panel.anchor_top = 1;     cipher_panel.anchor_bottom = 1
    cipher_panel.offset_top = -180
    cipher_panel.offset_bottom = -70
    var cps := StyleBoxFlat.new()
    cps.bg_color = Color(0.04, 0.02, 0.01, 0.92)
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


func _build_thematic_widget() -> void:
    # Subclass hook — no overlays. Card-first.
    pass


func _on_card_click(event: InputEvent) -> void:
    if event is InputEventMouseButton and event.pressed:
        # Soft synth pulse — playful response to clicking the card
        _active_notes.append({
            "time": 0.0, "freq": 220.0 + randf() * 110,
            "wave": "triangle",
            "atk": 0.005, "dur": 0.20, "rel": 0.25,
        })
        _set_status("clicked the card · listen.")


func _do_wipe() -> void:
    wipe_count += 1
    _wipe_pulse = 1.0
    wipe_btn.text = "  WIPE THE COUNTER  ( %d / 64 )" % wipe_count
    _active_notes.append({
        "time": 0.0, "freq": 130.0 + randf() * 30,
        "wave": "triangle",
        "atk": 0.005, "dur": 0.18, "rel": 0.15,
    })
    SaveSystem.mark_unlocked("lore:counter_wiped_again")
    if wipe_count == 64:
        _set_status("64 WIPES — alt prologue unlocked.")
        SaveSystem.mark_unlocked("vol5_alt_prologue_unlocked")
    elif wipe_count % 8 == 0:
        _set_status("wipe %d. the formica is the same." % wipe_count)
    else:
        _set_status("(wipe.)")


func _set_status(s: String) -> void:
    if status_label != null:
        status_label.text = s


# Override the base hotspot click to show a sliding cipher panel
# with the reveal text + play the Fool's note + fire the unlock.
func _on_hotspot(hs: Dictionary) -> void:
    super(hs)
    if cipher_panel == null or cipher_log == null: return
    cipher_log.clear()
    cipher_log.append_text("[color=#ffd896]▷ %s[/color]\n" %
        str(hs.get("interact", hs.get("id", ""))))
    # Find matching cipher
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
        if matched.has("text_lines"):
            for line in matched["text_lines"]:
                cipher_log.append_text("  · %s\n" % str(line))
        if matched.has("encoding_hint"):
            cipher_log.append_text(
                "  [color=#7a5828]↳ %s[/color]\n" %
                str(matched["encoding_hint"]))
        if matched.has("reveals"):
            cipher_log.append_text(
                "  [color=#d8a060]→ reveals: %s[/color]\n" %
                str(matched["reveals"]))
    # Slide it in
    cipher_panel.visible = true
    cipher_panel.modulate.a = 0
    var tw := cipher_panel.create_tween()
    tw.tween_property(cipher_panel, "modulate:a", 1.0, 0.25)
    # Trigger Fool's signature note
    _active_notes.append({
        "time": 0.0, "freq": 165.0, "wave": "triangle",
        "atk": 0.005, "dur": 0.6, "rel": 0.6,
    })


func _process(delta: float) -> void:
    super(delta)
    _wipe_pulse = maxf(0.0, _wipe_pulse - delta * 2.0)
    _ambient_t += delta
    # Ambient meter mirrors note activity
    var amb := 0.0
    for n in _active_notes:
        amb = maxf(amb, 0.3 + 0.7 * (1.0 - n.time / max(0.01, n.dur + n.rel)))
    # Always at least some baseline so the meter isn't dead
    amb = maxf(amb, 0.1 + sin(_ambient_t * 0.6) * 0.05)
    if ambient_meter != null:
        ambient_meter.value = amb
    # Wipe button pulse — flash gold on tick
    if _wipe_pulse > 0 and wipe_btn != null:
        var p = _wipe_pulse
        wipe_btn.modulate = Color(1.0 + p * 0.4,
                                   1.0 + p * 0.4,
                                   1.0 - p * 0.2)
    elif wipe_btn != null:
        wipe_btn.modulate = Color.WHITE


func _input(event: InputEvent) -> void:
    super(event)
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_SPACE:
            _do_wipe()
            get_viewport().set_input_as_handled()
