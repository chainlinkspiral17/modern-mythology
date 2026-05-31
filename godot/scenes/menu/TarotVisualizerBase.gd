extends Control
## TarotVisualizerBase — scrollable card tableau.
##
## NEW ARCHITECTURE: each card lives at the CENTER of a much larger
## canvas. Around the central painted art, subclasses register
## hand-crafted ASCII tableaux in four cardinal directions that
## extend the card's narrative outward. The player pans the canvas
## (mouse drag / WASD / arrows) to discover what surrounds the
## painted image.
##
##   CANVAS LAYOUT (CANVAS = 3200 × 3200, card at center)
##
##         ┌────────────────────────────────────┐
##         │           NORTH TABLEAU            │  ← sky / dream
##         │           (above card)             │     dimension
##         ├────────────────────────────────────┤
##         │ WEST   │                  │  EAST  │  ← past / future
##         │tableau │   PAINTED CARD   │tableau │
##         │(left)  │     (center)     │(right) │
##         ├────────┴──────────────────┴────────┤
##         │           SOUTH TABLEAU            │  ← underworld /
##         │           (below card)             │     subconscious
##         └────────────────────────────────────┘
##
## Subclasses override _card_path, _hooks_path, _ambient_audio_path,
## and call _add_tableau(direction, art_string, color) inside their
## _build_thematic_widget() override to register each cardinal art.
##
## Chrome (title + close + minimap) lives in fixed-position overlays
## above the pan canvas and doesn't scroll.

signal closed

var _card_path: String = ""
var _composition_path: String = ""   # opt-in: substrate composition id
                                      # under resources/substrates/compositions/.
                                      # When set, supersedes _card_path.
var _substrate_animate: bool = false  # opt-in: glitch+scanline+blink FX
var _substrate_severity: float = 0.15 # base glitch severity (0..1).
                                      # Subclasses can raise per §11 (Tower=hot).
var _face_rect_norm: Rect2 = Rect2(0.30, 0.10, 0.40, 0.35)  # normalized face
                                                            # region for blink
var _hooks_path: String = ""
var _ambient_audio_path: String = ""

const CANVAS_SIZE := 3200.0
const CARD_PIXEL_H := 900.0   # target on-canvas height of the painted card

# Direction enum for _add_tableau
enum Dir { NORTH = 0, SOUTH = 1, EAST = 2, WEST = 3 }

# Shared palette (overrideable)
var C_BG       := Color(0.020, 0.012, 0.018)
var C_INK      := Color(0.06, 0.04, 0.06)
var C_GOLD     := Color(0.85, 0.63, 0.38)
var C_GOLD_HI  := Color(1.0,  0.85, 0.59)
var C_TEXT     := Color(0.85, 0.72, 0.50)
var C_TEXT_DIM := Color(0.52, 0.40, 0.22)

var hooks: Dictionary = {}
var canvas: Control                # the BIG world
var viewport_box: Control          # fixed-size visible area
var card_rect: TextureRect
var hotspot_btns: Array = []
var tableaux: Array = []           # Array of {dir, label}
var minimap: Control
var ambient_player: AudioStreamPlayer

var _pan: Vector2 = Vector2.ZERO   # canvas offset from viewport top-left
var _pan_target: Vector2 = Vector2.ZERO
var _drag_active: bool = false
var _drag_last: Vector2

# Inline synth
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
    # Center after a frame so layout has settled and we have a real
    # size to anchor against. Also wire resized so window changes
    # re-center.
    call_deferred("_center_on_card")
    resized.connect(_center_on_card)
    set_process(true)
    set_process_input(true)


func _load_hooks() -> void:
    if _hooks_path == "" or not FileAccess.file_exists(_hooks_path):
        return
    var f := FileAccess.open(_hooks_path, FileAccess.READ)
    hooks = JSON.parse_string(f.get_as_text())
    f.close()


# ── Chrome + canvas ──────────────────────────────────────────────
func _build_chrome() -> void:
    # Solid bg
    var bg := ColorRect.new()
    bg.color = C_BG
    bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    bg.mouse_filter = Control.MOUSE_FILTER_STOP
    add_child(bg)

    # Viewport box — the rectangle that clips the panned canvas.
    # Full screen, clip_contents so the panned canvas doesn't bleed.
    viewport_box = Control.new()
    viewport_box.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    viewport_box.clip_contents = true
    viewport_box.mouse_filter = Control.MOUSE_FILTER_STOP
    add_child(viewport_box)

    # The canvas itself — large Control that holds card + tableaux.
    canvas = Control.new()
    canvas.size = Vector2(CANVAS_SIZE, CANVAS_SIZE)
    canvas.mouse_filter = Control.MOUSE_FILTER_PASS
    viewport_box.add_child(canvas)

    # Card image in the center of the canvas.
    # Use _load_image_with_fallback so the card loads even when the
    # PNG hasn't been .import'd by the editor yet (running from
    # un-imported source).
    var card_tex: Texture2D = _load_image_with_fallback(_card_path)
    if card_tex != null:
        card_rect = TextureRect.new()
        card_rect.texture = card_tex
        card_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
        card_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
        var tex_sz := (card_rect.texture as Texture2D).get_size()
        var card_h := CARD_PIXEL_H
        var card_w := tex_sz.x * (card_h / tex_sz.y)
        card_rect.size = Vector2(card_w, card_h)
        card_rect.position = Vector2(
            (CANVAS_SIZE - card_w) * 0.5,
            (CANVAS_SIZE - card_h) * 0.5
        )
        card_rect.mouse_filter = Control.MOUSE_FILTER_PASS
        canvas.add_child(card_rect)
        # Soft golden frame around the card to lift it from the tableaux
        var frame := ColorRect.new()
        frame.color = Color(C_GOLD_HI.r, C_GOLD_HI.g, C_GOLD_HI.b, 0.0)
        frame.position = card_rect.position - Vector2(6, 6)
        frame.size = card_rect.size + Vector2(12, 12)
        frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
        var fs := StyleBoxFlat.new()
        fs.bg_color = Color(0,0,0,0)
        fs.border_color = C_GOLD
        fs.set_border_width_all(2)
        # Attach via Panel; simpler than draw-loop
        var fp := Panel.new()
        fp.position = card_rect.position - Vector2(6, 6)
        fp.size = card_rect.size + Vector2(12, 12)
        fp.add_theme_stylebox_override("panel", fs)
        fp.mouse_filter = Control.MOUSE_FILTER_IGNORE
        canvas.add_child(fp)

    # Hotspots on the card — same coords as card_rect
    _build_hotspots()

    # Title strip at top — fixed, doesn't scroll
    var top := PanelContainer.new()
    top.anchor_left = 0; top.anchor_right = 1
    top.anchor_top = 0; top.anchor_bottom = 0
    top.offset_bottom = 40
    var tps := StyleBoxFlat.new()
    tps.bg_color = Color(0, 0, 0, 0.70)
    tps.border_color = C_GOLD
    tps.border_width_bottom = 1
    top.add_theme_stylebox_override("panel", tps)
    add_child(top)
    var top_row := HBoxContainer.new()
    top_row.add_theme_constant_override("separation", 12)
    top.add_child(top_row)
    var title_lbl := Label.new()
    title_lbl.text = str(hooks.get("arcana", "ARCANA"))
    title_lbl.add_theme_color_override("font_color", C_GOLD_HI)
    title_lbl.add_theme_font_size_override("font_size", 15)
    title_lbl.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    top_row.add_child(title_lbl)
    var sub_lbl := Label.new()
    sub_lbl.text = str(hooks.get("subtitle", ""))
    sub_lbl.add_theme_color_override("font_color",
        Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.7))
    sub_lbl.add_theme_font_size_override("font_size", 10)
    sub_lbl.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    sub_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    top_row.add_child(sub_lbl)
    var nav_hint := Label.new()
    nav_hint.text = "drag · WASD · home: center"
    nav_hint.add_theme_color_override("font_color", C_TEXT_DIM)
    nav_hint.add_theme_font_size_override("font_size", 9)
    nav_hint.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    top_row.add_child(nav_hint)
    var close := Button.new()
    close.text = "[ × CLOSE ]"
    close.flat = true
    close.add_theme_color_override("font_color", C_GOLD_HI)
    close.pressed.connect(func() -> void: closed.emit())
    top_row.add_child(close)

    # Minimap — small compass-style indicator in bottom-right
    minimap = _Minimap.new()
    minimap.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
    minimap.offset_right = -16; minimap.offset_bottom = -16
    minimap.offset_left = -130; minimap.offset_top = -130
    minimap.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(minimap)


func _build_hotspots() -> void:
    for hs_v in hooks.get("hotspots", []):
        var hs: Dictionary = hs_v
        if card_rect == null: continue
        var btn := Button.new()
        btn.flat = true
        var rect: Array = hs.get("rect", [0.0, 0.0, 0.1, 0.1])
        btn.position = card_rect.position + Vector2(
            rect[0] * card_rect.size.x,
            rect[1] * card_rect.size.y)
        btn.size = Vector2(rect[2] * card_rect.size.x,
                            rect[3] * card_rect.size.y)
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
        canvas.add_child(btn)
        hotspot_btns.append(btn)


# ── Tableau registration (subclass API) ──────────────────────────
## Register a tableau SEGMENT — a piece of hand-crafted ASCII art
## that appears in a direction once its unlock predicate is true.
##
## Each segment is a Dictionary:
##   {
##     "dir":      Dir.NORTH/SOUTH/EAST/WEST,
##     "row":      0..N — vertical slot from the inside out
##                 (row 0 = closest to card, larger = farther),
##     "ascii":    multi-line string of glyphs,
##     "tint":     Color modulate,
##     "font_size":int (default 13),
##     "requires": predicate fn returning bool — segment shows when
##                 this returns true. Pass null for always-shown.
##     "label":    populated internally (the Label control)
##     "shown":    populated internally (whether revealed yet)
##   }
##
## Multiple segments can share the same dir+row to stack horizontally
## or layer.

var _segments: Array = []   # all registered segment dicts


func _register_segment(seg: Dictionary) -> void:
    seg["label"] = null
    seg["shown"] = false
    _segments.append(seg)


func _check_segment_reveals() -> void:
    for seg in _segments:
        if seg["shown"]:
            continue
        var req = seg.get("requires", null)
        var ready: bool = (req == null) or req.call()
        if ready:
            _materialize_segment(seg)


func _materialize_segment(seg: Dictionary) -> void:
    var lbl := Label.new()
    lbl.text = str(seg.get("ascii", ""))
    lbl.add_theme_color_override("font_color",
        seg.get("tint", C_TEXT))
    lbl.add_theme_font_size_override("font_size",
        int(seg.get("font_size", 13)))
    lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
    lbl.modulate.a = 0.0
    var dir: int = int(seg["dir"])
    var row: int = int(seg.get("row", 0))

    var card_pos: Vector2 = card_rect.position if card_rect != null \
        else Vector2((CANVAS_SIZE - 700) * 0.5,
                     (CANVAS_SIZE - CARD_PIXEL_H) * 0.5)
    var card_sz: Vector2 = card_rect.size if card_rect != null \
        else Vector2(700, CARD_PIXEL_H)
    var gutter := 60.0
    var row_h := 200.0
    var row_w := 360.0

    match dir:
        Dir.NORTH:
            lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
            lbl.size = Vector2(card_sz.x + 600, row_h)
            lbl.position = Vector2(
                card_pos.x - 300,
                card_pos.y - gutter - row_h - (row * (row_h + 20)))
        Dir.SOUTH:
            lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
            lbl.size = Vector2(card_sz.x + 600, row_h)
            lbl.position = Vector2(
                card_pos.x - 300,
                card_pos.y + card_sz.y + gutter + (row * (row_h + 20)))
        Dir.EAST:
            lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
            lbl.size = Vector2(row_w, card_sz.y + 200)
            lbl.position = Vector2(
                card_pos.x + card_sz.x + gutter + (row * (row_w + 20)),
                card_pos.y - 100)
        Dir.WEST:
            lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
            lbl.size = Vector2(row_w, card_sz.y + 200)
            lbl.position = Vector2(
                card_pos.x - gutter - row_w - (row * (row_w + 20)),
                card_pos.y - 100)

    canvas.add_child(lbl)
    var tw := lbl.create_tween()
    tw.tween_property(lbl, "modulate:a", 1.0, 0.6)
    seg["label"] = lbl
    seg["shown"] = true


## Convenience: legacy single-call API for static, always-shown
## tableaux. Subclasses can use _register_segment for richer setup.
func _add_tableau(dir: int, ascii_art: String, tint: Color,
                  font_size: int = 13) -> void:
    _register_segment({
        "dir": dir, "row": 0,
        "ascii": ascii_art, "tint": tint,
        "font_size": font_size,
        "requires": null,
    })


# ── Camera ───────────────────────────────────────────────────────
func _center_on_card() -> void:
    # Use viewport rect — `size` may be (0,0) at _ready before layout
    # has settled, which would land the card in the top-left corner.
    var vp := get_viewport()
    var view_sz: Vector2 = (vp.get_visible_rect().size
                            if vp != null else size)
    if view_sz.x <= 0 or view_sz.y <= 0:
        view_sz = size
    if view_sz.x <= 0 or view_sz.y <= 0:
        view_sz = Vector2(1280, 720)
    var card_center := Vector2(CANVAS_SIZE * 0.5, CANVAS_SIZE * 0.5)
    if card_rect != null:
        card_center = card_rect.position + card_rect.size * 0.5
    _pan_target = card_center - view_sz * 0.5
    _pan = _pan_target
    _apply_pan()


func _apply_pan() -> void:
    canvas.position = -_pan
    if minimap != null:
        minimap.set_meta("pan", _pan)
        minimap.set_meta("view", size)
        minimap.queue_redraw()


## Helpers for subclasses to pan without touching private members
## directly (Godot 4.6 stricter inherited-member access).
func pan_by(delta_vec: Vector2) -> void:
    _pan_target += delta_vec


func recenter() -> void:
    _center_on_card()


## Load a Texture2D resilient to un-imported assets. Tries Godot's
## ResourceLoader first (which requires a .import sidecar), then
## falls back to raw Image.load_from_file from the on-disk path.
## Verbose print on failure paths so the user can see WHY the card
## isn't appearing.
static func _load_image_with_fallback(res_path: String) -> Texture2D:
    if res_path == "":
        push_warning("Visualizer: empty card path")
        return null
    print("[Visualizer] trying to load: ", res_path)
    if ResourceLoader.exists(res_path):
        var t := load(res_path)
        if t is Texture2D:
            print("[Visualizer] ✓ loaded via ResourceLoader")
            return t
        else:
            print("[Visualizer] ResourceLoader returned non-Texture2D: ", t)
    else:
        print("[Visualizer] ResourceLoader.exists() → false (no .import sidecar)")
    # Fallback: read the raw file from disk
    var abs_path: String = ProjectSettings.globalize_path(res_path)
    print("[Visualizer] fallback: trying raw read at ", abs_path)
    if FileAccess.file_exists(abs_path):
        var img := Image.load_from_file(abs_path)
        if img != null:
            print("[Visualizer] ✓ loaded via raw Image.load_from_file (",
                  img.get_size(), ")")
            return ImageTexture.create_from_image(img)
        else:
            push_warning("Visualizer: Image.load_from_file returned null for "
                          + abs_path)
    else:
        push_warning("Visualizer: file does NOT exist on disk: " + abs_path)
    return null


# ── SYNTH (kept same as before) ──────────────────────────────────
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


func _on_hotspot(hs: Dictionary) -> void:
    _trigger_synth_pulse()
    if hs.has("unlocks"):
        SaveSystem.mark_unlocked(str(hs["unlocks"]))


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


# ── THEMATIC (override in subclass) ──────────────────────────────
func _build_thematic_widget() -> void:
    pass


# ── _process — pan smoothing + audio pump ────────────────────────
func _process(delta: float) -> void:
    _t += delta
    # Smooth pan toward target
    _pan = _pan.lerp(_pan_target, clamp(delta * 6.0, 0, 1))
    _apply_pan()
    # Check unlock-gated tableau segments
    _check_segment_reveals()
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


# ── Input — pan controls ─────────────────────────────────────────
func _input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo:
        match event.keycode:
            KEY_ESCAPE:
                closed.emit()
                get_viewport().set_input_as_handled()
            KEY_HOME:
                _center_on_card()
                get_viewport().set_input_as_handled()


func _gui_input(event: InputEvent) -> void:
    if event is InputEventMouseButton:
        var mb := event as InputEventMouseButton
        if mb.button_index == MOUSE_BUTTON_LEFT:
            _drag_active = mb.pressed
            _drag_last = mb.position
        elif mb.button_index == MOUSE_BUTTON_WHEEL_UP and mb.pressed:
            _pan_target.y -= 80
        elif mb.button_index == MOUSE_BUTTON_WHEEL_DOWN and mb.pressed:
            _pan_target.y += 80
    elif event is InputEventMouseMotion and _drag_active:
        var mm := event as InputEventMouseMotion
        var d := mm.position - _drag_last
        _drag_last = mm.position
        _pan_target -= d
        _pan = _pan_target   # snap during drag, smooth on release


# ── Minimap inner class ──────────────────────────────────────────
class _Minimap extends Control:
    func _draw() -> void:
        var pan: Vector2 = get_meta("pan", Vector2.ZERO)
        var view: Vector2 = get_meta("view", Vector2(800, 600))
        var s := size
        var bg := Color(0, 0, 0, 0.7)
        draw_rect(Rect2(0, 0, s.x, s.y), bg, true)
        draw_rect(Rect2(0, 0, s.x, s.y),
                   Color(0.85, 0.66, 0.29, 0.7), false, 1)
        # World rect
        var w_scale: float = (s.x - 8) / 3200.0
        # Card position (center of 3200x3200)
        var cx := 4 + 3200 * 0.5 * w_scale
        var cy := 4 + 3200 * 0.5 * w_scale
        var card_w := 700 * w_scale
        var card_h := 900 * w_scale
        draw_rect(Rect2(cx - card_w * 0.5, cy - card_h * 0.5,
                         card_w, card_h),
                   Color(1.0, 0.85, 0.40, 0.8), false, 1)
        # Viewport rect
        var vx = 4 + pan.x * w_scale
        var vy = 4 + pan.y * w_scale
        var vw = view.x * w_scale
        var vh = view.y * w_scale
        draw_rect(Rect2(vx, vy, vw, vh),
                   Color(1.0, 0.95, 0.60, 0.9), false, 1)
        # Cardinal labels
        var font := ThemeDB.fallback_font
        draw_string(font, Vector2(s.x*0.5 - 5, 12), "N",
                    HORIZONTAL_ALIGNMENT_LEFT, -1, 9,
                    Color(0.85, 0.66, 0.29, 0.8))
        draw_string(font, Vector2(s.x*0.5 - 5, s.y - 4), "S",
                    HORIZONTAL_ALIGNMENT_LEFT, -1, 9,
                    Color(0.85, 0.66, 0.29, 0.8))
        draw_string(font, Vector2(4, s.y*0.5 + 4), "W",
                    HORIZONTAL_ALIGNMENT_LEFT, -1, 9,
                    Color(0.85, 0.66, 0.29, 0.8))
        draw_string(font, Vector2(s.x - 10, s.y*0.5 + 4), "E",
                    HORIZONTAL_ALIGNMENT_LEFT, -1, 9,
                    Color(0.85, 0.66, 0.29, 0.8))
