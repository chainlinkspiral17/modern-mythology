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

## AsciiComposition script for loading mosaic-block substrate compositions
## as the card centerpiece when _composition_path is set.
const ASCII_COMPOSITION_SCRIPT = preload("res://scenes/game/AsciiComposition.gd")

var hooks: Dictionary = {}
var canvas: Control                # the BIG world
var viewport_box: Control          # fixed-size visible area
var card_rect: Control             # wrapper that hosts either a TextureRect
                                    # (painted PNG) or an AsciiComposition
                                    # (substrate). Layout coords (.position
                                    # / .size) are the same either way so
                                    # subclass hotspots are unaffected.
var card_composition: Node = null  # AsciiComposition instance when used
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

# Cipher reveal panel (lazy-built on first click)
var _cipher_panel: PanelContainer = null
var _cipher_label_head: Label = null
var _cipher_label_text: RichTextLabel = null
var _cipher_label_hint: Label = null
var _cipher_label_unlock: Label = null


func _ready() -> void:
    set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    mouse_filter = Control.MOUSE_FILTER_STOP
    _load_hooks()
    _build_chrome()
    _init_synth()
    _init_ambient()
    _build_thematic_widget()
    # Centering, layout, and live-refresh on cross-card unlocks.
    call_deferred("_center_on_card")
    resized.connect(_center_on_card)
    if not SaveSystem.unlocked_changed.is_connected(_on_unlock_emitted):
        SaveSystem.unlocked_changed.connect(_on_unlock_emitted)
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

    # Card centerpiece — substrate composition takes precedence, falling
    # back to the painted PNG. The wrapper Control's position+size are
    # the layout reference subclass hotspots use, so swapping the inner
    # render path doesn't move any hotspots.
    _build_card_surface()

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


## Build the central card surface. Order of preference:
##   1. _composition_path → mosaic-block substrate composition
##      (renders the painted card as ASCII mosaic + crisp engine-font
##      text overlays per resources/substrates/compositions/<id>.json).
##   2. _card_path → painted PNG.
##   3. Neither → empty wrapper, no centerpiece.
##
## The wrapper Control `card_rect` lives at the canvas center and is
## the reference for subclass hotspots. The inner renderer fills it.
func _build_card_surface() -> void:
    # Decide target wrapper dimensions. For compositions we read the
    # manifest's canvas size; for PNGs we use the texture aspect.
    var card_w: float = 700.0
    var card_h: float = CARD_PIXEL_H
    var composition_canvas: Vector2 = Vector2.ZERO

    if _composition_path != "":
        var comp_full := "res://resources/substrates/compositions/" \
                          + _composition_path + ".json"
        if FileAccess.file_exists(comp_full):
            var f := FileAccess.open(comp_full, FileAccess.READ)
            var data: Variant = JSON.parse_string(f.get_as_text())
            f.close()
            if typeof(data) == TYPE_DICTIONARY and data.has("canvas"):
                var arr = data["canvas"]
                composition_canvas = Vector2(float(arr[0]), float(arr[1]))
                # Card height fixed; width derived from manifest aspect
                card_w = composition_canvas.x * (card_h / composition_canvas.y)
        else:
            push_warning("Visualizer: composition not found: " + comp_full)

    if _composition_path == "" or composition_canvas == Vector2.ZERO:
        var card_tex: Texture2D = _load_image_with_fallback(_card_path)
        if card_tex == null:
            # Nothing to render — leave card_rect as an empty wrapper at
            # canvas center so hotspots fail soft instead of crashing.
            card_rect = Control.new()
            card_rect.size = Vector2(card_w, card_h)
            card_rect.position = Vector2(
                (CANVAS_SIZE - card_w) * 0.5,
                (CANVAS_SIZE - card_h) * 0.5)
            card_rect.mouse_filter = Control.MOUSE_FILTER_PASS
            canvas.add_child(card_rect)
            return
        var tex_sz := card_tex.get_size()
        card_w = tex_sz.x * (card_h / tex_sz.y)

    # Build the wrapper at the canvas center
    card_rect = Control.new()
    card_rect.size = Vector2(card_w, card_h)
    card_rect.position = Vector2(
        (CANVAS_SIZE - card_w) * 0.5,
        (CANVAS_SIZE - card_h) * 0.5)
    card_rect.mouse_filter = Control.MOUSE_FILTER_PASS
    canvas.add_child(card_rect)

    # Fill the wrapper with either composition or texture
    if _composition_path != "" and composition_canvas != Vector2.ZERO:
        var comp := Control.new()
        comp.set_script(ASCII_COMPOSITION_SCRIPT)
        comp.mouse_filter = Control.MOUSE_FILTER_IGNORE
        # Anchor the composition Control to fill the wrapper. Don't use
        # comp.scale here — AsciiComposition has its own _fit_canvas that
        # scales its internal _canvas based on self.size. Setting scale
        # instead would leave self.size at (0,0) and _fit_canvas would
        # bail out early, leaving the mosaic invisible.
        comp.anchor_left = 0; comp.anchor_top = 0
        comp.anchor_right = 1; comp.anchor_bottom = 1
        comp.offset_left = 0; comp.offset_top = 0
        comp.offset_right = 0; comp.offset_bottom = 0
        card_rect.add_child(comp)
        comp.call_deferred("load_composition", _composition_path)
        card_composition = comp
    else:
        var card_tex: Texture2D = _load_image_with_fallback(_card_path)
        if card_tex != null:
            var tr := TextureRect.new()
            tr.texture = card_tex
            tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
            tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
            tr.anchor_right = 1; tr.anchor_bottom = 1
            tr.mouse_filter = Control.MOUSE_FILTER_PASS
            card_rect.add_child(tr)

    # Soft golden frame around the card — applies to both modes
    var frame_panel := Panel.new()
    frame_panel.position = card_rect.position - Vector2(6, 6)
    frame_panel.size = card_rect.size + Vector2(12, 12)
    var fs := StyleBoxFlat.new()
    fs.bg_color = Color(0, 0, 0, 0)
    fs.border_color = C_GOLD
    fs.set_border_width_all(2)
    frame_panel.add_theme_stylebox_override("panel", fs)
    frame_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
    canvas.add_child(frame_panel)


func _build_hotspots() -> void:
    # Clear any existing hotspot buttons (live-refresh after a gated_by
    # unlock fires must rebuild from scratch, not stack new buttons on
    # top of stale ones).
    for prev in hotspot_btns:
        if is_instance_valid(prev):
            prev.queue_free()
    hotspot_btns.clear()
    for hs_v in hooks.get("hotspots", []):
        var hs: Dictionary = hs_v
        if card_rect == null: continue
        # Gated hotspots stay dormant until the gating unlock fires.
        # Skip silently — the player will discover they've "woken up"
        # when they return to this card after the cross-card reveal.
        var gate := str(hs.get("gated_by", ""))
        if gate != "" and not SaveSystem.is_unlocked(gate):
            continue
        var btn := Button.new()
        btn.flat = true
        var rect: Array = hs.get("rect", [0.0, 0.0, 0.1, 0.1])
        btn.position = card_rect.position + Vector2(
            rect[0] * card_rect.size.x,
            rect[1] * card_rect.size.y)
        btn.size = Vector2(rect[2] * card_rect.size.x,
                            rect[3] * card_rect.size.y)
        btn.tooltip_text = str(hs.get("interact", hs.get("id", "")))
        btn.mouse_default_cursor_shape = _cursor_for(str(hs.get("cursor", "examine")))
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
        # Hover pulse — soft alpha tween while the cursor is inside.
        # Replays from scratch on each entry so the player gets a fresh
        # heartbeat-style throb rather than a flat tint.
        btn.mouse_entered.connect(func() -> void: _hotspot_pulse_start(btn, bsh))
        btn.mouse_exited.connect(func() -> void: _hotspot_pulse_stop(btn, bsh))
        # Two-step press: reveal cipher (always runs, even if a subclass
        # overrides _on_hotspot without calling super), then run the
        # subclass game-logic via the virtual _on_hotspot hook.
        var on_press := func() -> void:
            _reveal_cipher(captured)
            _on_hotspot(captured)
        btn.pressed.connect(on_press)
        canvas.add_child(btn)
        hotspot_btns.append(btn)


## Map a JSON `cursor` string to a Godot cursor shape. Unknown values
## fall back to the magnifier (examine) — most hotspots want it.
func _cursor_for(kind: String) -> int:
    match kind:
        "take":     return Control.CURSOR_POINTING_HAND
        "use":      return Control.CURSOR_DRAG
        "closer":   return Control.CURSOR_CROSS
        "navigate": return Control.CURSOR_ARROW
        "exit":     return Control.CURSOR_FORBIDDEN
        _:          return Control.CURSOR_HELP


# ── Hotspot hover pulse ───────────────────────────────────────────
# Per-button tween that lives on the StyleBoxFlat's bg_color alpha.
# We hold the tween on a meta so mouse_exited can stop it cleanly.

func _hotspot_pulse_start(btn: Button, sbox: StyleBoxFlat) -> void:
    var prior = btn.get_meta("pulse_tw", null)
    if prior != null and is_instance_valid(prior):
        prior.kill()
    var sb := sbox.duplicate() as StyleBoxFlat
    btn.add_theme_stylebox_override("hover", sb)
    var apply_alpha := func(a: float) -> void:
        sb.bg_color = Color(1, 0.85, 0.40, a)
        sb.border_color = Color(1, 0.85, 0.40, clamp(a * 2.6, 0.0, 1.0))
    var tw := create_tween().set_loops()
    tw.tween_method(apply_alpha, 0.18, 0.55, 0.8)
    tw.tween_method(apply_alpha, 0.55, 0.18, 0.8)
    btn.set_meta("pulse_tw", tw)

func _hotspot_pulse_stop(btn: Button, _sbox: StyleBoxFlat) -> void:
    var prior = btn.get_meta("pulse_tw", null)
    if prior != null and is_instance_valid(prior):
        prior.kill()
        btn.remove_meta("pulse_tw")


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


# ── Cipher reveal panel ──────────────────────────────────────────
# Find the cipher matching this hotspot (by id, then by anchor
# proximity), render its text + encoding_hint into the floating
# panel, and mark its reveal flag. Always-fire — bypasses the
# subclass _on_hotspot override.

func _reveal_cipher(hs: Dictionary) -> void:
    var matched := _match_cipher_for(hs)
    if matched.is_empty():
        # Hotspot has no cipher (rare — e.g. pure game-action ones).
        # Surface a thin placeholder so the click still feels alive.
        _ensure_cipher_panel()
        _cipher_label_head.text = "▷ " + str(hs.get("interact", hs.get("id", "")))
        _cipher_label_text.text = ""
        _cipher_label_hint.text = ""
        _cipher_label_unlock.text = ""
        _show_cipher_panel()
        return
    _ensure_cipher_panel()
    _cipher_label_head.text = "▷ " + str(hs.get("interact", hs.get("id", "")))
    var body := str(matched.get("text", ""))
    if matched.has("text_lines"):
        var lines := PackedStringArray()
        for line_v in matched["text_lines"]:
            lines.append(str(line_v))
        if body != "":
            body += "\n"
        body += "\n".join(lines)
    _cipher_label_text.text = body
    _cipher_label_hint.text = str(matched.get("encoding_hint", ""))
    var reveals_key := str(matched.get("reveals", ""))
    if reveals_key != "":
        SaveSystem.mark_unlocked(reveals_key)
        _cipher_label_unlock.text = "→ " + reveals_key
    else:
        _cipher_label_unlock.text = ""
    _show_cipher_panel()


func _match_cipher_for(hs: Dictionary) -> Dictionary:
    var hs_id := str(hs.get("id", ""))
    var ciphers := hooks.get("ciphers", []) as Array
    # Exact ID match first.
    for c_v in ciphers:
        var c: Dictionary = c_v
        var c_id := str(c.get("id", ""))
        if c_id == "": continue
        if c_id == hs_id or hs_id.begins_with(c_id) or c_id.begins_with(hs_id):
            return c
    # Otherwise nearest-anchor in normalized space.
    if ciphers.is_empty(): return {}
    var rect: Array = hs.get("rect", [0,0,0,0])
    var cx: float = float(rect[0]) + float(rect[2]) * 0.5
    var cy: float = float(rect[1]) + float(rect[3]) * 0.5
    var best: Dictionary = {}
    var best_d: float = INF
    for c_v in ciphers:
        var c: Dictionary = c_v
        var a = c.get("anchor_norm", null)
        if typeof(a) != TYPE_ARRAY or a.size() < 2: continue
        # cross_card_link ciphers can have a list-of-points anchor;
        # average them.
        var ax: float = 0.0
        var ay: float = 0.0
        if typeof(a[0]) == TYPE_ARRAY:
            for pt in a:
                ax += float(pt[0]); ay += float(pt[1])
            ax /= a.size(); ay /= a.size()
        else:
            ax = float(a[0]); ay = float(a[1])
        var d: float = abs(ax - cx) + abs(ay - cy)
        if d < best_d:
            best_d = d; best = c
    return best


func _ensure_cipher_panel() -> void:
    if _cipher_panel != null and is_instance_valid(_cipher_panel):
        return
    _cipher_panel = PanelContainer.new()
    _cipher_panel.set_anchors_preset(Control.PRESET_TOP_RIGHT)
    _cipher_panel.offset_right = -18
    _cipher_panel.offset_top = 56
    _cipher_panel.offset_left = -380
    _cipher_panel.custom_minimum_size = Vector2(360, 0)
    _cipher_panel.mouse_filter = Control.MOUSE_FILTER_STOP
    var sb := StyleBoxFlat.new()
    sb.bg_color = Color(0.03, 0.02, 0.04, 0.92)
    sb.border_color = C_GOLD_HI
    sb.set_border_width_all(1)
    _cipher_panel.add_theme_stylebox_override("panel", sb)
    add_child(_cipher_panel)
    var vb := VBoxContainer.new()
    vb.add_theme_constant_override("separation", 6)
    _cipher_panel.add_child(vb)
    _cipher_label_head = Label.new()
    _cipher_label_head.add_theme_color_override("font_color", C_GOLD_HI)
    _cipher_label_head.add_theme_font_size_override("font_size", 11)
    vb.add_child(_cipher_label_head)
    _cipher_label_text = RichTextLabel.new()
    _cipher_label_text.fit_content = true
    _cipher_label_text.bbcode_enabled = false
    _cipher_label_text.add_theme_color_override("default_color", C_TEXT)
    _cipher_label_text.add_theme_font_size_override("normal_font_size", 10)
    _cipher_label_text.custom_minimum_size = Vector2(340, 0)
    vb.add_child(_cipher_label_text)
    _cipher_label_hint = Label.new()
    _cipher_label_hint.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    _cipher_label_hint.custom_minimum_size.x = 340
    _cipher_label_hint.add_theme_color_override("font_color", C_TEXT_DIM)
    _cipher_label_hint.add_theme_font_size_override("font_size", 9)
    vb.add_child(_cipher_label_hint)
    _cipher_label_unlock = Label.new()
    _cipher_label_unlock.add_theme_color_override("font_color", C_GOLD)
    _cipher_label_unlock.add_theme_font_size_override("font_size", 9)
    vb.add_child(_cipher_label_unlock)
    var dismiss := Button.new()
    dismiss.text = "[ × ]"
    dismiss.flat = true
    dismiss.alignment = HORIZONTAL_ALIGNMENT_RIGHT
    dismiss.add_theme_color_override("font_color", C_GOLD)
    dismiss.pressed.connect(func() -> void: _cipher_panel.visible = false)
    vb.add_child(dismiss)
    _cipher_panel.visible = false


func _show_cipher_panel() -> void:
    _cipher_panel.visible = true
    _cipher_panel.modulate.a = 0.0
    var tw := create_tween()
    tw.tween_property(_cipher_panel, "modulate:a", 1.0, 0.25)


# Live-refresh hotspots when a cross-card unlock fires. This is what
# makes the "wait, did something new appear here?" moment work — the
# player marks a Fool cipher, switches to Magician, and the gated
# hotspot is already lit by the time the visualizer rebuilds.
func _on_unlock_emitted(_key: String) -> void:
    if card_rect == null: return
    _build_hotspots()


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
