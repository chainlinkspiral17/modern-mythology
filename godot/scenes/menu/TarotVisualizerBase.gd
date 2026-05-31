extends Control
## TarotVisualizerBase — shared chrome + plumbing for per-card
## sophisticated visualizers. Each arcana's specific visualizer
## subclasses this and overrides the thematic content.
##
## Provides:
##   • Full-screen card art at z=0 (passed in by subclass via _card_path)
##   • Subtle parallax / breath on the card via _process
##   • Hotspot overlay from puzzle_hooks/<id>.json (clickable rects
##     that fire cipher reveals when clicked)
##   • Inline AudioStreamGenerator for per-card synthesis hooks
##   • Optional ambient audio loop slot for thematic sound (water
##     lapping for Fool, etc) — subclass sets _ambient_audio_path
##   • Standard close button + ESC handling
##
## Subclasses override:
##   _card_path: String           — res:// path to the card image
##   _hooks_path: String          — res:// path to puzzle_hooks JSON
##   _ambient_audio_path: String  — optional thematic audio loop
##   _build_thematic_widget()     — hook to add card-specific content
##                                  on top of the standard chrome

signal closed

# Subclasses override these in their _ready or constructor
var _card_path: String = ""
var _hooks_path: String = ""
var _ambient_audio_path: String = ""

# Shared palette — subclasses may override before _build_chrome
var C_BG       := Color(0.020, 0.012, 0.018)
var C_INK      := Color(0.06, 0.04, 0.06)
var C_GOLD     := Color(0.85, 0.63, 0.38)
var C_GOLD_HI  := Color(1.0,  0.85, 0.59)
var C_TEXT     := Color(0.85, 0.72, 0.50)
var C_TEXT_DIM := Color(0.52, 0.40, 0.22)

# Internals
var hooks: Dictionary = {}
var card_rect: TextureRect
var hotspot_btns: Array = []
var info_panel: PanelContainer
var ambient_player: AudioStreamPlayer

# Live synth
var _gen: AudioStreamGenerator
var _gen_player: AudioStreamPlayer
var _playback: AudioStreamGeneratorPlayback
var _active_notes: Array = []

var _t: float = 0.0


func _ready() -> void:
    set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    mouse_filter = Control.MOUSE_FILTER_STOP
    _load_hooks()
    _build_chrome()
    _init_synth()
    _init_ambient()
    _build_thematic_widget()
    set_process(true)
    set_process_input(true)


func _load_hooks() -> void:
    if _hooks_path == "" or not FileAccess.file_exists(_hooks_path):
        return
    var f := FileAccess.open(_hooks_path, FileAccess.READ)
    hooks = JSON.parse_string(f.get_as_text())
    f.close()


# ── CHROME ───────────────────────────────────────────────────────
func _build_chrome() -> void:
    var bg := ColorRect.new()
    bg.color = C_BG
    bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    bg.mouse_filter = Control.MOUSE_FILTER_STOP
    add_child(bg)

    # Card art full-screen, KEEP_ASPECT_CENTERED so the full card
    # always shows; thematic widgets layer above
    if _card_path != "" and ResourceLoader.exists(_card_path):
        card_rect = TextureRect.new()
        card_rect.texture = load(_card_path)
        card_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
        card_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
        card_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
        card_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
        add_child(card_rect)

    # Title strip
    var title := Label.new()
    title.text = "%s" % str(hooks.get("arcana", ""))
    title.add_theme_color_override("font_color", C_GOLD_HI)
    title.add_theme_font_size_override("font_size", 14)
    title.set_anchors_preset(Control.PRESET_TOP_LEFT)
    title.offset_left = 18; title.offset_top = 6
    add_child(title)

    var close_btn := Button.new()
    close_btn.text = "[ × CLOSE ]"
    close_btn.set_anchors_preset(Control.PRESET_TOP_RIGHT)
    close_btn.offset_right = -18; close_btn.offset_top = 4
    close_btn.offset_left = -120
    close_btn.add_theme_color_override("font_color", C_GOLD_HI)
    close_btn.pressed.connect(func() -> void: closed.emit())
    add_child(close_btn)

    # Info panel — bottom-right, character + subtitle + cipher count
    info_panel = PanelContainer.new()
    info_panel.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
    info_panel.offset_right = -16; info_panel.offset_bottom = -16
    info_panel.offset_left = -300; info_panel.offset_top = -100
    var ps := StyleBoxFlat.new()
    ps.bg_color = Color(C_INK.r, C_INK.g, C_INK.b, 0.85)
    ps.border_color = C_GOLD
    ps.set_border_width_all(1)
    info_panel.add_theme_stylebox_override("panel", ps)
    add_child(info_panel)
    var ib := VBoxContainer.new()
    ib.add_theme_constant_override("separation", 3)
    info_panel.add_child(ib)
    if hooks.has("subtitle"):
        var sub := Label.new()
        sub.text = str(hooks["subtitle"])
        sub.add_theme_color_override("font_color", C_TEXT)
        sub.add_theme_font_size_override("font_size", 10)
        ib.add_child(sub)
    if hooks.has("character"):
        var ch := Label.new()
        ch.text = "POV · " + str(hooks["character"]).to_upper()
        ch.add_theme_color_override("font_color", C_GOLD_HI)
        ch.add_theme_font_size_override("font_size", 9)
        ib.add_child(ch)
    var meta := Label.new()
    var bits := []
    if hooks.has("ciphers"):
        bits.append("ciphers: %d" % (hooks["ciphers"] as Array).size())
    if hooks.has("hotspots"):
        bits.append("hotspots: %d" % (hooks["hotspots"] as Array).size())
    meta.text = " · ".join(bits)
    meta.add_theme_color_override("font_color", C_TEXT_DIM)
    meta.add_theme_font_size_override("font_size", 9)
    ib.add_child(meta)

    # Hotspots — built on top of card art, invisible until hover
    _build_hotspots()


func _build_hotspots() -> void:
    for hs_v in hooks.get("hotspots", []):
        var hs: Dictionary = hs_v
        var btn := Button.new()
        btn.flat = true
        btn.set_meta("rect_norm", hs.get("rect", [0.0, 0.0, 0.1, 0.1]))
        btn.set_meta("hs", hs)
        btn.tooltip_text = str(hs.get("interact", hs.get("id", "")))
        var sb := StyleBoxFlat.new()
        sb.bg_color = Color(1, 0.85, 0.40, 0.0)
        sb.border_color = Color(1, 0.85, 0.40, 0.0)
        sb.set_border_width_all(1)
        btn.add_theme_stylebox_override("normal", sb)
        var bsh := sb.duplicate() as StyleBoxFlat
        bsh.bg_color = Color(1, 0.85, 0.40, 0.30)
        bsh.border_color = Color(1, 0.85, 0.40, 0.85)
        btn.add_theme_stylebox_override("hover", bsh)
        btn.add_theme_stylebox_override("focus", bsh)
        var captured := hs
        btn.pressed.connect(func() -> void: _on_hotspot(captured))
        add_child(btn)
        hotspot_btns.append(btn)
    resized.connect(_update_hotspot_positions)
    call_deferred("_update_hotspot_positions")


func _update_hotspot_positions() -> void:
    if card_rect == null: return
    # Compute the actual rect of the card art inside the screen
    # (since KEEP_ASPECT_CENTERED letterboxes/pillarboxes it)
    var tex := card_rect.texture
    if tex == null: return
    var tsize := tex.get_size()
    var view := size
    var s := minf(view.x / tsize.x, view.y / tsize.y)
    var draw := tsize * s
    var origin := (view - draw) * 0.5
    for btn in hotspot_btns:
        var rect: Array = btn.get_meta("rect_norm", [0.0,0.0,0.1,0.1])
        btn.position = origin + Vector2(rect[0] * draw.x, rect[1] * draw.y)
        btn.size = Vector2(rect[2] * draw.x, rect[3] * draw.y)


func _on_hotspot(hs: Dictionary) -> void:
    _trigger_synth_pulse()
    if hs.has("unlocks"):
        SaveSystem.mark_unlocked(str(hs["unlocks"]))


# ── SYNTH ────────────────────────────────────────────────────────
func _init_synth() -> void:
    _gen = AudioStreamGenerator.new()
    _gen.mix_rate = 44100
    _gen.buffer_length = 0.05
    _gen_player = AudioStreamPlayer.new()
    _gen_player.bus = "SFX"
    _gen_player.stream = _gen
    add_child(_gen_player)
    _gen_player.play()
    _playback = _gen_player.get_stream_playback()


func _trigger_synth_pulse() -> void:
    _active_notes.append({
        "time": 0.0, "freq": 220.0, "wave": "sine",
        "atk": 0.02, "dur": 0.6, "rel": 0.4,
    })


# ── AMBIENT ──────────────────────────────────────────────────────
func _init_ambient() -> void:
    if _ambient_audio_path == "": return
    if not ResourceLoader.exists(_ambient_audio_path): return
    ambient_player = AudioStreamPlayer.new()
    ambient_player.bus = "BGM"
    ambient_player.stream = load(_ambient_audio_path)
    ambient_player.volume_db = -8.0
    add_child(ambient_player)
    ambient_player.play()


# ── THEMATIC WIDGET (override in subclass) ───────────────────────
func _build_thematic_widget() -> void:
    pass


# ── _process / audio pump / parallax breath ──────────────────────
func _process(delta: float) -> void:
    _t += delta
    # Card breath / parallax — subtle
    if card_rect != null:
        card_rect.pivot_offset = card_rect.size * 0.5
        card_rect.scale = Vector2(1.0 + sin(_t * 0.4) * 0.005,
                                  1.0 + sin(_t * 0.4) * 0.005)
        card_rect.position.x = sin(_t * 0.25) * 3.0

    # Synth pump
    if _playback != null:
        var frames := _playback.get_frames_available()
        if frames > 0:
            for _i in frames:
                var sum := 0.0
                var rem: Array = []
                for n in _active_notes:
                    n.time += 1.0 / 44100.0
                    sum += _sample(n)
                    if n.time < n.dur + n.rel:
                        rem.append(n)
                _active_notes = rem
                sum = clamp(sum * 0.3, -0.95, 0.95)
                _playback.push_frame(Vector2(sum, sum))


func _sample(n: Dictionary) -> float:
    var env := _adsr(n.time, n.atk, n.dur - n.atk, 0.0, n.rel, n.dur)
    if env <= 0: return 0.0
    var phase = n.freq * n.time * TAU
    var v := 0.0
    match n.wave:
        "square":   v = -1.0 if fmod(phase, TAU) < PI else 1.0
        "sawtooth": v = fmod(phase / TAU, 1.0) * 2.0 - 1.0
        "triangle": v = abs(fmod(phase / TAU, 1.0) - 0.5) * 4.0 - 1.0
        _:          v = sin(phase)
    return v * env


func _adsr(t, a, d, s, r, dur) -> float:
    if t < 0: return 0.0
    if t < a: return t / a
    if t < a + d:
        var dt = (t - a) / d
        return 1.0 - dt * (1.0 - s)
    if t < dur: return s
    if t < dur + r: return s * (1.0 - (t - dur) / r)
    return 0.0


func _input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_ESCAPE:
            closed.emit()
            get_viewport().set_input_as_handled()
