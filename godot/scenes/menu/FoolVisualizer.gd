extends "res://scenes/menu/TarotVisualizerBase.gd"
## FoolVisualizer — "Between Acts" — water lapping at the cliff's edge.
##
## Per user direction: thematic, animated, game-like. Five layers
## overlay the card art:
##
##   1. WATER LAYER along the bottom — sine waves + foam line glyphs
##      that react to ambient audio + the wipe counter's "splash".
##      The water rises as you wipe → 64 wipes floods the cliff.
##   2. CLIFF EDGE silhouette in foreground bottom-center — broken
##      ASCII line showing the precipice. Cracks expand each wipe.
##   3. DOG that periodically barks (status line + brief pulse) and
##      walks across the bottom, leaving paw-glyph trails.
##   4. SKY GRADIENT overlay across the top — shifts from dawn-blue
##      to "almost-sunrise gold" over a 90s cycle. The chapter's
##      "dawn-not-quite-dawn" lighting cue from the VN DESIGN NOTES
##      hook made literal.
##   5. WIPE COUNTER mini-game widget — counter with a rag-sweep
##      animation across a formica surface. Tap or press 'wipe' in
##      the console to count up. Each wipe = a splash + dog bark
##      chance + water-rise increment. 64 wipes = alt prologue.
##
## All driven by the existing BBS console at the bottom — commands
## still work as before, plus the new widgets respond to in-game
## state.

# Water state
var _water_t: float = 0.0
var _water_phase: float = 0.0
var _water_rise: float = 0.0   # 0..1, grows with wipes
const WATER_LINE_GLYPHS := "≈~_-.`'"

# Cliff state
var _cliff_cracks: int = 0

# Dog state
var _dog_t: float = 0.0
var _dog_walk: float = 0.0     # 0..1 horizontal position
var _dog_barks: int = 0
var _next_bark: float = 6.0

# Wipe counter mini-game
var wipe_count: int = 0
var _wipe_anim_t: float = -1.0  # -1 = no animation, 0..1 = sweeping

# Sky state
var _sky_t: float = 0.0

# BBS console (kept from prior FoolVisualizer)
var console_input: LineEdit
var console_log: RichTextLabel
var counter_label: Label

# Layer refs for redraw
var water_layer: Control
var cliff_layer: Control
var dog_layer: Control
var sky_layer: Control
var wipe_widget: Control


func _init() -> void:
    _card_path  = "res://assets/gallery/fool.png"
    _hooks_path = "res://resources/puzzle_hooks/fool.json"
    # Default ambient: title theme as the "between acts" pause music
    _ambient_audio_path = "res://assets/audio/bgm/title_theme.ogg"
    # Warm jaundiced amber palette per the chapter's color signature
    C_BG = Color(0.040, 0.034, 0.020)
    C_GOLD = Color(0.78, 0.66, 0.29)
    C_GOLD_HI = Color(1.0, 0.85, 0.40)
    C_TEXT = Color(0.85, 0.72, 0.40)


func _build_thematic_widget() -> void:
    # 1) Sky gradient at top — driven by _sky_t
    sky_layer = _SkyGradient.new()
    sky_layer.anchor_left = 0; sky_layer.anchor_right = 1
    sky_layer.anchor_top = 0; sky_layer.anchor_bottom = 0.15
    sky_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(sky_layer)

    # 2) Water layer at bottom
    water_layer = _WaterLayer.new()
    water_layer.anchor_left = 0; water_layer.anchor_right = 1
    water_layer.anchor_top = 0.75; water_layer.anchor_bottom = 0.95
    water_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(water_layer)

    # 3) Cliff edge silhouette
    cliff_layer = _CliffEdge.new()
    cliff_layer.anchor_left = 0.20; cliff_layer.anchor_right = 0.80
    cliff_layer.anchor_top = 0.70; cliff_layer.anchor_bottom = 0.80
    cliff_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(cliff_layer)

    # 4) Dog walking layer
    dog_layer = _DogLayer.new()
    dog_layer.anchor_left = 0; dog_layer.anchor_right = 1
    dog_layer.anchor_top = 0.78; dog_layer.anchor_bottom = 0.86
    dog_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(dog_layer)

    # 5) Wipe counter mini-game widget — interactive
    wipe_widget = _WipeWidget.new()
    wipe_widget.anchor_left = 0.40; wipe_widget.anchor_right = 0.60
    wipe_widget.anchor_top = 0.62; wipe_widget.anchor_bottom = 0.70
    wipe_widget.mouse_filter = Control.MOUSE_FILTER_STOP
    wipe_widget.gui_input.connect(_on_wipe_click)
    add_child(wipe_widget)

    # BBS console at the bottom — kept from previous Fool but
    # smaller now to leave room for the visual layers
    _build_console()


func _build_console() -> void:
    var con := PanelContainer.new()
    con.anchor_left = 0.02; con.anchor_right = 0.98
    con.anchor_top = 0.86;  con.anchor_bottom = 0.98
    var ps := StyleBoxFlat.new()
    ps.bg_color = Color(0.020, 0.020, 0.012, 0.92)
    ps.border_color = Color(0.30, 0.95, 0.45, 0.65)
    ps.set_border_width_all(1)
    con.add_theme_stylebox_override("panel", ps)
    add_child(con)
    var vb := VBoxContainer.new()
    vb.add_theme_constant_override("separation", 2)
    con.add_child(vb)

    var hdr := Label.new()
    hdr.text = "$ RUST_CODE.BBS · 3:47 AM · type help"
    hdr.add_theme_color_override("font_color", Color(0.16, 0.50, 0.24))
    hdr.add_theme_font_size_override("font_size", 9)
    vb.add_child(hdr)

    console_log = RichTextLabel.new()
    console_log.bbcode_enabled = true
    console_log.scroll_following = true
    console_log.size_flags_vertical = Control.SIZE_EXPAND_FILL
    console_log.add_theme_font_size_override("normal_font_size", 11)
    console_log.add_theme_color_override("default_color",
        Color(0.30, 0.95, 0.45))
    vb.add_child(console_log)

    var input_row := HBoxContainer.new()
    input_row.add_theme_constant_override("separation", 4)
    var prompt := Label.new()
    prompt.text = "> "
    prompt.add_theme_color_override("font_color",
        Color(0.95, 0.62, 0.18))
    prompt.add_theme_font_size_override("font_size", 12)
    input_row.add_child(prompt)
    console_input = LineEdit.new()
    console_input.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    console_input.add_theme_color_override("font_color",
        Color(0.30, 0.95, 0.45))
    console_input.text_submitted.connect(_on_command)
    input_row.add_child(console_input)
    vb.add_child(input_row)
    console_input.grab_focus()

    _log("[color=#d8a060]> welcome between acts. wipe to begin.[/color]")

    # Counter label on top of card
    counter_label = Label.new()
    counter_label.text = "wipes: 0 / 64"
    counter_label.add_theme_color_override("font_color", C_GOLD_HI)
    counter_label.add_theme_font_size_override("font_size", 11)
    counter_label.set_anchors_preset(Control.PRESET_TOP_LEFT)
    counter_label.offset_left = 20; counter_label.offset_top = 32
    add_child(counter_label)


func _log(line: String) -> void:
    if console_log != null:
        console_log.append_text(line + "\n")


# ── Interactions ────────────────────────────────────────────────
func _on_wipe_click(event: InputEvent) -> void:
    if event is InputEventMouseButton and event.pressed:
        _do_wipe()


func _do_wipe() -> void:
    wipe_count += 1
    if counter_label != null:
        counter_label.text = "wipes: %d / 64" % wipe_count
    _water_rise = min(1.0, wipe_count / 64.0)
    _cliff_cracks = wipe_count / 8
    _wipe_anim_t = 0.0     # start sweep animation
    # Synth splash
    _active_notes.append({
        "time": 0.0, "freq": 140.0 + randf() * 40, "wave": "triangle",
        "atk": 0.005, "dur": 0.25, "rel": 0.18,
    })
    # Dog bark chance
    if randf() < 0.15:
        _trigger_dog_bark()
    if wipe_count == 64:
        _log("[color=#ff8050]── 64 WIPES ─ ALT PROLOGUE UNLOCKED ──[/color]")
        SaveSystem.mark_unlocked("vol5_alt_prologue_unlocked")
    elif wipe_count % 8 == 0:
        _log("[color=#7a5828](wipe %d. the formica is the same.)[/color]"
             % wipe_count)
    SaveSystem.mark_unlocked("lore:counter_wiped_again")


func _trigger_dog_bark() -> void:
    _dog_barks += 1
    _log("[color=#ffd896]  ◐ dog barks once.[/color]")
    # Quick yip — short square pulse
    _active_notes.append({
        "time": 0.0, "freq": 480.0, "wave": "square",
        "atk": 0.001, "dur": 0.05, "rel": 0.08,
    })
    _next_bark = _dog_t + 6.0 + randf() * 8.0


func _on_command(text: String) -> void:
    var line := text.strip_edges().to_lower()
    console_input.text = ""
    _log("[color=#e89c30]> %s[/color]" % text)
    if line == "":
        return
    match line.split(" ")[0]:
        "help", "?":
            _log("[color=#d8a060]  wipe · bark · oracle · clear · exit[/color]")
        "wipe":
            _do_wipe()
        "bark":
            _trigger_dog_bark()
        "oracle":
            for c_v in hooks.get("ciphers", []):
                if str(c_v.get("kind","")) == "inline_oracle":
                    for ln in c_v.get("text_lines", []):
                        _log("[color=#c8a878]%s[/color]" % ln)
                    break
        "clear":
            console_log.clear()
        "exit", "quit":
            closed.emit()
        _:
            _log("[color=#7a5828]? unknown. try: help[/color]")


# ── _process — drive all the layered animations ────────────────
func _process(delta: float) -> void:
    super(delta)
    _water_t += delta
    _water_phase += delta * (0.7 + _water_rise * 0.6)
    _dog_t += delta
    _dog_walk = fmod(_dog_t * 0.05, 1.0)
    _sky_t += delta
    if _wipe_anim_t >= 0:
        _wipe_anim_t += delta * 4.0
        if _wipe_anim_t > 1.0:
            _wipe_anim_t = -1.0

    # Layer redraws
    if water_layer != null:
        water_layer.set_meta("phase", _water_phase)
        water_layer.set_meta("rise", _water_rise)
        water_layer.queue_redraw()
    if cliff_layer != null:
        cliff_layer.set_meta("cracks", _cliff_cracks)
        cliff_layer.queue_redraw()
    if dog_layer != null:
        dog_layer.set_meta("walk", _dog_walk)
        dog_layer.set_meta("barking", _dog_t < _next_bark - 5.5)
        dog_layer.queue_redraw()
    if sky_layer != null:
        sky_layer.set_meta("t", _sky_t)
        sky_layer.queue_redraw()
    if wipe_widget != null:
        wipe_widget.set_meta("anim", _wipe_anim_t)
        wipe_widget.set_meta("count", wipe_count)
        wipe_widget.queue_redraw()

    # Auto bark
    if _dog_t > _next_bark:
        _trigger_dog_bark()


# ── Nested view classes ─────────────────────────────────────────
class _WaterLayer extends Control:
    func _draw() -> void:
        var s := size
        if s.x < 4 or s.y < 4: return
        var phase: float = get_meta("phase", 0.0)
        var rise: float = get_meta("rise", 0.0)
        var water_top = s.y * (1.0 - rise * 0.5) - 8
        # Multi-band water
        for band in 6:
            var by = water_top + band * 4
            if by > s.y: break
            var alpha = 0.18 + band * 0.10
            var col := Color(0.25, 0.45, 0.55, alpha)
            for x in range(0, int(s.x), 6):
                var wy = by + sin((x * 0.04) + phase + band * 0.3) * (2 + band)
                draw_rect(Rect2(x, wy, 5, 3), col, true)
        # Foam line glyphs on top wave
        var font := ThemeDB.fallback_font
        var glyphs := "≈~_-.`'"
        for x in range(0, int(s.x), 14):
            var fy = water_top + sin((x * 0.04) + phase) * 4 - 4
            var g := glyphs[(x + int(phase * 14)) % glyphs.length()]
            draw_string(font, Vector2(x, fy), g,
                        HORIZONTAL_ALIGNMENT_LEFT, -1, 12,
                        Color(0.85, 0.95, 1.0, 0.55))


class _CliffEdge extends Control:
    func _draw() -> void:
        var s := size
        if s.x < 4 or s.y < 4: return
        var cracks: int = get_meta("cracks", 0)
        var font := ThemeDB.fallback_font
        # Jagged top edge
        var edge_pts := PackedVector2Array()
        for x in range(0, int(s.x) + 1, 8):
            var jag = sin(x * 0.4) * 3 + (1 if (x / 8) % 3 == 0 else 0)
            edge_pts.append(Vector2(x, jag + 2))
        for i in range(1, edge_pts.size()):
            draw_line(edge_pts[i-1], edge_pts[i],
                      Color(0.40, 0.30, 0.18), 2)
        # Cracks expand as wipes accumulate
        for n in cracks:
            var cx = (n * 53) % int(s.x)
            var cy = 4 + (n * 11) % int(s.y - 4)
            draw_line(Vector2(cx, cy), Vector2(cx + 6, cy + 8),
                      Color(0.20, 0.15, 0.08, 0.8), 1)


class _DogLayer extends Control:
    func _draw() -> void:
        var s := size
        if s.x < 4 or s.y < 4: return
        var walk: float = get_meta("walk", 0.0)
        var barking: bool = get_meta("barking", false)
        var dx = walk * s.x
        var font := ThemeDB.fallback_font
        var glyph := "ʕ•ᴥ•ʔ" if barking else "ʕ◕ᴥ◕ʔ"
        draw_string(font, Vector2(dx, s.y - 4), glyph,
                    HORIZONTAL_ALIGNMENT_LEFT, -1, 16,
                    Color(0.85, 0.70, 0.40, 0.85))
        # Paw trail
        for i in 8:
            var tx = dx - (i + 1) * 16
            if tx < 0: break
            var alpha = 0.3 * (1.0 - i / 8.0)
            draw_string(font, Vector2(tx, s.y - 2), "·",
                        HORIZONTAL_ALIGNMENT_LEFT, -1, 12,
                        Color(0.85, 0.70, 0.40, alpha))


class _SkyGradient extends Control:
    func _draw() -> void:
        var s := size
        if s.x < 4 or s.y < 4: return
        var t: float = get_meta("t", 0.0)
        # Slow 90s cycle: dawn-blue → almost-sunrise gold
        var phase = (sin(t * TAU / 90.0) + 1.0) * 0.5
        var c_top := Color(0.05, 0.05, 0.12).lerp(
            Color(0.45, 0.30, 0.18), phase)
        var c_bot := Color(0.12, 0.10, 0.18).lerp(
            Color(0.85, 0.55, 0.20), phase)
        for y in range(0, int(s.y), 2):
            var lt = y / s.y
            var col = c_top.lerp(c_bot, lt)
            col.a = 0.45 * (1.0 - lt)
            draw_rect(Rect2(0, y, s.x, 2), col, true)


class _WipeWidget extends Control:
    func _draw() -> void:
        var s := size
        if s.x < 8 or s.y < 8: return
        var anim: float = get_meta("anim", -1.0)
        var count: int = get_meta("count", 0)
        # Formica counter surface — speckled rect
        var formica := Color(0.55, 0.50, 0.35, 0.55)
        draw_rect(Rect2(0, 0, s.x, s.y), formica, true)
        draw_rect(Rect2(0, 0, s.x, s.y),
                  Color(1, 0.85, 0.40, 0.55), false, 1)
        # Speckle
        for i in 24:
            var px = (i * 17) % int(s.x)
            var py = (i * 31) % int(s.y)
            draw_rect(Rect2(px, py, 2, 2),
                      Color(0.7, 0.6, 0.45, 0.4), true)
        # Wipe-sweep animation
        if anim >= 0:
            var sweep_x = anim * s.x
            for dx in 14:
                var alpha = 0.7 * (1.0 - dx / 14.0)
                draw_rect(Rect2(sweep_x - dx * 2, 0, 2, s.y),
                          Color(0.95, 0.95, 0.95, alpha), true)
        # Label
        var font := ThemeDB.fallback_font
        draw_string(font, Vector2(8, s.y * 0.65),
                    "TAP TO WIPE",
                    HORIZONTAL_ALIGNMENT_LEFT, -1, 10,
                    Color(0.20, 0.18, 0.10, 0.85))


func _input(event: InputEvent) -> void:
    super(event)
    # Spacebar = wipe shortcut (when console isn't focused)
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_SPACE and not console_input.has_focus():
            _do_wipe()
            get_viewport().set_input_as_handled()
