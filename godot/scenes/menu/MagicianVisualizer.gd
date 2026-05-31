extends "res://scenes/menu/TarotVisualizerBase.gd"
## MagicianVisualizer — "Cathedral of Rust and Code".
##
## The Magician card shows Frasier in an abandoned warehouse drawing
## an infinity sigil out of code-stream particles with a soldering
## iron, demons swirling at the edges, a miniature model city he's
## wiring below, and a CRT terminal in the corner.
##
## Thematic widget set:
##   1. CODE-RAIN backdrop overlay — green digital-rain glyphs falling
##      slowly behind the card art (subtle so it doesn't compete)
##   2. INFINITY SIGIL TRACER — a glowing ∞ overlay above Frasier's
##      position pulses on each synth note + slowly auto-rotates;
##      click it to trigger a "sigil close" chord (3 notes)
##   3. CRT TERMINAL panel in lower-right showing live signal:
##      • DEMON.PROC count from puzzle_hooks
##      • IRON.TEMP fluctuating
##      • CODE.STREAM scrolling lorem-ipsum-style fragments
##   4. AMBIENT: warehouse drone loops underneath
##
## Together these are the "Cathedral of Rust and Code" — the chapter's
## title rendered as audio + visual liturgy.

# Code rain state
var _rain_cols: Array = []     # per column: y (head position), speed, glyph_set
var _rain_t: float = 0.0
const RAIN_GLYPH_POOL := "01∞◆▓▒░│║=#%&*+/<>?"

# Sigil tracer state
var sigil_rect: Control
var _sigil_t: float = 0.0
var _sigil_pulse: float = 0.0

# CRT terminal state
var crt_panel: PanelContainer
var crt_log: RichTextLabel
var _crt_t: float = 0.0
var _iron_temp: float = 580.0


func _init() -> void:
    _card_path  = "res://assets/gallery/magician.png"
    _hooks_path = "res://resources/puzzle_hooks/magician.json"
    _ambient_audio_path = "res://assets/audio/bgm/vol5_warehouse_drone.ogg"
    # Cool industrial palette overrides
    C_BG = Color(0.020, 0.025, 0.030)
    C_GOLD = Color(0.45, 0.78, 0.82)
    C_GOLD_HI = Color(0.78, 0.95, 1.0)


# ── THEMATIC WIDGETS ─────────────────────────────────────────────
func _build_thematic_widget() -> void:
    # 1) Code rain — full-screen overlay drawn below the chrome
    var rain := _CodeRain.new()
    rain.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    rain.mouse_filter = Control.MOUSE_FILTER_IGNORE
    rain.z_index = -1
    add_child(rain)
    move_child(rain, 1)   # behind card art but in front of bg color

    # 2) Infinity sigil tracer — clickable, sits roughly over
    # Frasier's hand in the card art
    sigil_rect = _SigilTracer.new()
    sigil_rect.anchor_left = 0.42; sigil_rect.anchor_right = 0.58
    sigil_rect.anchor_top = 0.15;  sigil_rect.anchor_bottom = 0.30
    sigil_rect.mouse_filter = Control.MOUSE_FILTER_STOP
    sigil_rect.gui_input.connect(_on_sigil_input)
    add_child(sigil_rect)

    # 3) CRT terminal panel — lower-left so it doesn't clash with the
    # base class info panel in lower-right
    crt_panel = PanelContainer.new()
    crt_panel.anchor_left = 0.02; crt_panel.anchor_right = 0.35
    crt_panel.anchor_top = 0.72;  crt_panel.anchor_bottom = 0.97
    var ps := StyleBoxFlat.new()
    ps.bg_color = Color(0.0, 0.05, 0.03, 0.92)
    ps.border_color = Color(0.30, 0.95, 0.45, 0.85)
    ps.set_border_width_all(1)
    crt_panel.add_theme_stylebox_override("panel", ps)
    add_child(crt_panel)

    var crt_vbox := VBoxContainer.new()
    crt_vbox.add_theme_constant_override("separation", 2)
    crt_panel.add_child(crt_vbox)

    var crt_hdr := Label.new()
    crt_hdr.text = "● CRT // RUST_CODE.BBS // NODE 1"
    crt_hdr.add_theme_color_override("font_color",
        Color(0.30, 0.95, 0.45))
    crt_hdr.add_theme_font_size_override("font_size", 9)
    crt_vbox.add_child(crt_hdr)

    crt_log = RichTextLabel.new()
    crt_log.bbcode_enabled = true
    crt_log.scroll_following = true
    crt_log.size_flags_vertical = Control.SIZE_EXPAND_FILL
    crt_log.add_theme_font_size_override("normal_font_size", 10)
    crt_log.add_theme_color_override("default_color",
        Color(0.30, 0.95, 0.45))
    crt_vbox.add_child(crt_log)
    _crt_print("[color=#ffd96e]>[/color] iron.warmup()")
    _crt_print("[color=#88c870]  rust = thawing[/color]")
    _crt_print("[color=#88c870]  signal = OK[/color]")


func _crt_print(line: String) -> void:
    if crt_log == null: return
    crt_log.append_text(line + "\n")


# ── Sigil interaction ────────────────────────────────────────────
func _on_sigil_input(event: InputEvent) -> void:
    if event is InputEventMouseButton and event.pressed:
        # Trigger 3-note "sigil close" chord
        var triad := [220.0, 277.2, 329.6]
        for f in triad:
            _active_notes.append({
                "time": 0.0, "freq": f, "wave": "square",
                "atk": 0.005, "dur": 0.4, "rel": 0.3,
            })
        _crt_print("[color=#ffd96e]>[/color] sigil.close()")
        _crt_print("[color=#88c870]  chord = A C# E[/color]")
        _sigil_pulse = 1.0
        if hooks.has("hotspots"):
            for h_v in hooks["hotspots"]:
                if str(h_v.get("id","")) == "mag_soldering_iron":
                    SaveSystem.mark_unlocked(str(h_v.get("unlocks","")))


# ── _process — drive thematic animations ─────────────────────────
func _process(delta: float) -> void:
    super(delta)
    _sigil_t += delta
    _crt_t += delta
    if sigil_rect != null:
        sigil_rect.queue_redraw()
    _sigil_pulse = maxf(0.0, _sigil_pulse - delta * 1.2)
    # Iron temp oscillation + occasional log line
    _iron_temp += (sin(_crt_t * 1.5) * 8.0 - 4.0) * delta
    if _crt_t > 2.4:
        _crt_t = 0.0
        var demon_count := 0
        if hooks.has("ciphers"):
            for c_v in hooks["ciphers"]:
                if str(c_v.get("kind","")) == "presence_count":
                    demon_count = 2
                    break
        var pool := [
            "[color=#3a5028]  ...[/color]",
            "[color=#88c870]  iron.temp = %d°C[/color]" % int(_iron_temp),
            "[color=#88c870]  demon.proc = %d[/color]" % demon_count,
            "[color=#88c870]  stream = active[/color]",
            "[color=#ffd96e]  ∞ = stable[/color]",
            "[color=#88c870]  model_city.ping → riverboat[/color]",
        ]
        _crt_print(pool[randi() % pool.size()])


# ── Nested view classes ─────────────────────────────────────────
class _CodeRain extends Control:
    var t: float = 0.0
    var cols: Array = []
    var initialized: bool = false

    func _process(d: float) -> void:
        t += d
        if not initialized:
            var n := int(size.x / 14.0)
            cols.resize(n)
            for i in n:
                cols[i] = {
                    "head": randf() * size.y,
                    "speed": 40.0 + randf() * 80.0,
                    "len": 8 + (randi() % 16),
                }
            initialized = true
        for c in cols:
            c["head"] += c["speed"] * d
            if c["head"] > size.y + 200:
                c["head"] = -randf() * 200
        queue_redraw()

    func _draw() -> void:
        if not initialized: return
        var font := ThemeDB.fallback_font
        var pool := "01∞◆▓▒░│║=#%&*+/<>?"
        for i in cols.size():
            var c = cols[i]
            var x = i * 14
            var head_y: float = c["head"]
            var length: int = c["len"]
            for k in length:
                var y = head_y - k * 14
                if y < -14 or y > size.y + 14: continue
                var alpha = max(0.0, (1.0 - float(k) / length) * 0.5)
                if k == 0:
                    alpha = 0.85
                var glyph := pool[randi() % pool.length()]
                draw_string(font, Vector2(x, y),
                            glyph, HORIZONTAL_ALIGNMENT_LEFT, -1, 11,
                            Color(0.30, 0.95, 0.45, alpha))


class _SigilTracer extends Control:
    var t: float = 0.0
    var pulse: float = 0.0

    func _process(d: float) -> void:
        t += d

    func _draw() -> void:
        var s := size
        if s.x < 10 or s.y < 10: return
        var cx = s.x * 0.5
        var cy = s.y * 0.5
        var rx = s.x * 0.42
        var ry = s.y * 0.35
        # Lemniscate of Bernoulli (figure-8)
        var pts := PackedVector2Array()
        var samples := 64
        for i in samples + 1:
            var theta = i / float(samples) * TAU + t * 0.4
            var denom = 1.0 + sin(theta) * sin(theta)
            var x = cx + rx * cos(theta) / denom
            var y = cy + ry * sin(theta) * cos(theta) / denom
            pts.append(Vector2(x, y))
        var col := Color(0.78, 0.95, 1.0, 0.85)
        var dim := Color(0.30, 0.55, 0.70, 0.55)
        for i in range(1, pts.size()):
            draw_line(pts[i-1], pts[i], col, 1.5)
        # Pulse glow ring on the lemniscate's center
        if pulse > 0.0:
            draw_arc(Vector2(cx, cy), 8 + pulse * 18, 0, TAU, 32,
                      Color(1, 0.95, 0.7, pulse), 2.0)
        # Subtle outer halo
        draw_arc(Vector2(cx, cy), max(rx, ry) + 4, 0, TAU, 48,
                  Color(0.3, 0.7, 0.85, 0.20), 1.0)
