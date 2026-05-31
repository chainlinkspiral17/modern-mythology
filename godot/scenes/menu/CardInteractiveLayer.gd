extends Control
## CardInteractiveLayer — overlays a tarot card composition with
## clickable puzzle-hook hotspots, cipher reveals, cross-reference
## hints, and a "play this card's note" synth trigger.
##
## Designed to be added as a child of the gallery's fullscreen
## viewer (z_index above the composition, below the close hint).
## Hooks data sourced from resources/puzzle_hooks/<id>.json.
##
## When no hook file exists for an asset, the layer renders nothing
## visible — gallery falls back to passive view.

const C_HOTSPOT       := Color(1.0, 0.85, 0.40, 0.0)   # invisible idle
const C_HOTSPOT_HOVER := Color(1.0, 0.85, 0.40, 0.35)
const C_HOTSPOT_RULE  := Color(1.0, 0.85, 0.40, 0.65)
const C_PRIORITY_HI   := Color(1.0, 0.45, 0.35, 0.55)
const C_CIPHER_BG     := Color(0.03, 0.02, 0.04, 0.92)
const C_GOLD          := Color(0.85, 0.63, 0.38)
const C_GOLD_HI       := Color(1.0,  0.85, 0.59)
const C_TEXT          := Color(0.85, 0.72, 0.50)
const C_TEXT_DIM      := Color(0.52, 0.40, 0.22)

const HOOKS_DIR := "res://resources/puzzle_hooks/"

var hooks: Dictionary = {}
var hotspot_btns: Array = []
var cipher_panel: Panel = null
var cross_ref_strip: HBoxContainer = null
var note_btn: Button = null
var asset_id: String = ""        # e.g. "emperor_arcana" or "portrait_dante"

# Audio for "play this card's note" — uses AudioStreamGenerator with
# the same per-arcana timbres as tarot_synth, but inline so this
# layer doesn't depend on the synth overlay being open.
var _gen: AudioStreamGenerator
var _gen_player: AudioStreamPlayer
var _playback: AudioStreamGeneratorPlayback
var _active_notes: Array = []

# 22-arcana timbre map (subset of TarotSynthOverlay's table)
const ARCANA_TIMBRE := {
    "fool":           {"wave":"square",  "freq":110.0, "atk":0.02, "dur":1.0, "rel":0.5},
    "magician":       {"wave":"square",  "freq":138.6, "atk":0.005,"dur":0.5, "rel":0.2},
    "high_priestess": {"wave":"triangle","freq":146.8, "atk":0.04, "dur":1.2, "rel":0.6},
    "empress":        {"wave":"sine",    "freq":174.6, "atk":0.002,"dur":1.6, "rel":0.9},
    "emperor":        {"wave":"sawtooth","freq":196.0, "atk":0.01, "dur":0.9, "rel":0.4},
    "hierophant":     {"wave":"sine",    "freq":207.7, "atk":0.05, "dur":1.0, "rel":0.4},
    "lovers":         {"wave":"sine",    "freq":233.1, "atk":0.003,"dur":1.4, "rel":0.7},
    "chariot":        {"wave":"sawtooth","freq":261.6, "atk":0.01, "dur":0.6, "rel":0.25},
    "strength":       {"wave":"sawtooth","freq":293.7, "atk":0.06, "dur":1.2, "rel":0.4},
    "hermit":         {"wave":"triangle","freq":311.1, "atk":0.08, "dur":1.4, "rel":0.8},
}


func _ready() -> void:
    mouse_filter = Control.MOUSE_FILTER_PASS
    set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    _init_audio()
    set_process_input(true)


## Bind to a specific gallery item. asset = arcana id like "emperor"
## or composition id like "portrait_dante". Tries to resolve the hook
## JSON via several naming conventions.
func bind(item_id: String) -> bool:
    asset_id = item_id
    var hook_path := _resolve_hook_path(item_id)
    if hook_path == "" or not FileAccess.file_exists(hook_path):
        # No hooks for this asset — render nothing (transparent layer)
        return false
    var f := FileAccess.open(hook_path, FileAccess.READ)
    hooks = JSON.parse_string(f.get_as_text())
    f.close()
    _build_overlay()
    return true


func _resolve_hook_path(item_id: String) -> String:
    # Direct match: emperor_arcana -> emperor.json
    var candidates := [
        item_id.replace("_arcana", ""),
        item_id,
        item_id.replace("portrait_", ""),
    ]
    for c in candidates:
        var p: String = HOOKS_DIR + str(c) + ".json"
        if FileAccess.file_exists(p):
            return p
    return ""


# ── Audio ────────────────────────────────────────────────────────
func _init_audio() -> void:
    _gen = AudioStreamGenerator.new()
    _gen.mix_rate = 44100
    _gen.buffer_length = 0.05
    _gen_player = AudioStreamPlayer.new()
    _gen_player.bus = "SFX"
    _gen_player.stream = _gen
    add_child(_gen_player)
    _gen_player.play()
    _playback = _gen_player.get_stream_playback()
    set_process(true)


func _process(_delta: float) -> void:
    if _playback == null: return
    var frames := _playback.get_frames_available()
    if frames <= 0: return
    for _i in frames:
        var sum := 0.0
        var rem: Array = []
        for n in _active_notes:
            n.time += 1.0 / 44100.0
            sum += _sample_note(n)
            if n.time < n.dur + n.rel:
                rem.append(n)
        _active_notes = rem
        sum = clamp(sum * 0.3, -0.95, 0.95)
        _playback.push_frame(Vector2(sum, sum))


func _sample_note(n: Dictionary) -> float:
    var env := _adsr(n.time, n.atk, n.dur - n.atk, 0.0, n.rel, n.dur)
    if env <= 0: return 0.0
    var phase = n.freq * n.time * TAU
    var v := 0.0
    match n.wave:
        "sawtooth": v = fmod(phase / TAU, 1.0) * 2.0 - 1.0
        "square":   v = -1.0 if fmod(phase, TAU) < PI else 1.0
        "triangle": v = abs(fmod(phase / TAU, 1.0) - 0.5) * 4.0 - 1.0
        _:          v = sin(phase)
    return v * env


func _adsr(t: float, a: float, d: float, s: float, r: float, dur: float) -> float:
    if t < 0: return 0.0
    if t < a: return t / a
    if t < a + d:
        var dt = (t - a) / d
        return 1.0 - dt * (1.0 - s)
    if t < dur: return s
    if t < dur + r: return s * (1.0 - (t - dur) / r)
    return 0.0


func _trigger_note() -> void:
    var key := asset_id.replace("_arcana", "").replace("portrait_", "")
    var t = ARCANA_TIMBRE.get(key)
    if t == null:
        # default tone
        t = {"wave":"sine","freq":220.0,"atk":0.02,"dur":0.8,"rel":0.3}
    _active_notes.append({
        "time": 0.0, "freq": t.freq, "wave": t.wave,
        "atk": t.atk, "dur": t.dur, "rel": t.rel
    })


# ── Overlay build ────────────────────────────────────────────────
func _build_overlay() -> void:
    # clear any prior children
    for c in get_children():
        if c != _gen_player:
            c.queue_free()
    hotspot_btns.clear()

    # Top-right info corner: title + "play note" button + cross-ref strip
    var hud := VBoxContainer.new()
    hud.set_anchors_preset(Control.PRESET_TOP_RIGHT)
    hud.offset_right = -20
    hud.offset_top = 60
    hud.add_theme_constant_override("separation", 6)
    add_child(hud)

    var info := PanelContainer.new()
    var ps := StyleBoxFlat.new()
    ps.bg_color = C_CIPHER_BG
    ps.border_color = C_GOLD
    ps.set_border_width_all(1)
    info.add_theme_stylebox_override("panel", ps)
    hud.add_child(info)

    var info_box := VBoxContainer.new()
    info_box.add_theme_constant_override("separation", 4)
    info.add_child(info_box)

    var title := Label.new()
    title.text = "[ %s ]" % str(hooks.get("arcana", asset_id)).to_upper()
    title.add_theme_color_override("font_color", C_GOLD_HI)
    title.add_theme_font_size_override("font_size", 12)
    info_box.add_child(title)

    if hooks.has("subtitle"):
        var sub := Label.new()
        sub.text = str(hooks.get("subtitle", ""))
        sub.add_theme_color_override("font_color", C_TEXT)
        sub.add_theme_font_size_override("font_size", 9)
        info_box.add_child(sub)

    var meta_lbl := Label.new()
    var meta_bits := []
    if hooks.has("character"):
        meta_bits.append("char: " + str(hooks["character"]))
    if hooks.has("palette"):
        meta_bits.append("palette: " + str(hooks["palette"]))
    if hooks.has("ciphers"):
        meta_bits.append("ciphers: %d" % (hooks["ciphers"] as Array).size())
    if hooks.has("hotspots"):
        meta_bits.append("hotspots: %d" % (hooks["hotspots"] as Array).size())
    meta_lbl.text = " · ".join(meta_bits)
    meta_lbl.add_theme_color_override("font_color", C_TEXT_DIM)
    meta_lbl.add_theme_font_size_override("font_size", 9)
    info_box.add_child(meta_lbl)

    note_btn = Button.new()
    note_btn.text = "♪ PLAY NOTE"
    note_btn.add_theme_color_override("font_color", C_GOLD_HI)
    note_btn.pressed.connect(_trigger_note)
    info_box.add_child(note_btn)

    # Cross-reference strip — small text links to connected cards
    if hooks.has("cross_references") and typeof(hooks["cross_references"]) == TYPE_DICTIONARY:
        var xref_lbl := Label.new()
        xref_lbl.text = "↔ connects:"
        xref_lbl.add_theme_color_override("font_color", C_TEXT_DIM)
        xref_lbl.add_theme_font_size_override("font_size", 9)
        info_box.add_child(xref_lbl)
        var xref: Dictionary = hooks["cross_references"]
        for k in xref.keys():
            var refrow := Label.new()
            refrow.text = "  • %s: %s" % [k, str(xref[k])]
            refrow.add_theme_color_override("font_color", C_TEXT)
            refrow.add_theme_font_size_override("font_size", 9)
            refrow.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
            refrow.custom_minimum_size.x = 280
            info_box.add_child(refrow)

    # Cipher panel — populated on hotspot click (initially empty)
    cipher_panel = Panel.new()
    cipher_panel.custom_minimum_size = Vector2(340, 100)
    var cs := StyleBoxFlat.new()
    cs.bg_color = C_CIPHER_BG
    cs.border_color = C_GOLD_HI
    cs.set_border_width_all(1)
    cipher_panel.add_theme_stylebox_override("panel", cs)
    cipher_panel.visible = false
    hud.add_child(cipher_panel)

    # Hotspots — draw as invisible buttons over their normalized rects
    for hs_v in hooks.get("hotspots", []):
        var hs: Dictionary = hs_v
        var btn := Button.new()
        btn.flat = true
        # convert normalized rect [x, y, w, h] to actual position later
        # via _update_hotspot_positions on resize
        btn.set_meta("rect_norm", hs.get("rect", [0.0, 0.0, 0.1, 0.1]))
        btn.set_meta("hotspot_data", hs)
        btn.tooltip_text = str(hs.get("interact", hs.get("id", "")))
        # invisible by default, light highlight on hover
        var bs := StyleBoxFlat.new()
        bs.bg_color = C_HOTSPOT
        bs.border_color = Color(C_HOTSPOT_RULE.r, C_HOTSPOT_RULE.g,
                                 C_HOTSPOT_RULE.b, 0.0)
        bs.set_border_width_all(1)
        btn.add_theme_stylebox_override("normal", bs)
        var bsh := bs.duplicate() as StyleBoxFlat
        bsh.bg_color = C_HOTSPOT_HOVER
        bsh.border_color = C_HOTSPOT_RULE
        btn.add_theme_stylebox_override("hover", bsh)
        btn.add_theme_stylebox_override("focus", bsh)
        var captured := hs
        btn.pressed.connect(func() -> void: _show_cipher_for_hotspot(captured))
        add_child(btn)
        hotspot_btns.append(btn)

    resized.connect(_update_hotspot_positions)
    _update_hotspot_positions()


func _update_hotspot_positions() -> void:
    var view := size
    for btn in hotspot_btns:
        var rect: Array = btn.get_meta("rect_norm", [0.0, 0.0, 0.1, 0.1])
        var x = rect[0] * view.x
        var y = rect[1] * view.y
        var w = rect[2] * view.x
        var h = rect[3] * view.y
        btn.position = Vector2(x, y)
        btn.size = Vector2(w, h)


func _show_cipher_for_hotspot(hs: Dictionary) -> void:
    var hs_id: String = str(hs.get("id", ""))
    # find matching cipher in hooks.ciphers if any
    var matched: Dictionary = {}
    for c_v in hooks.get("ciphers", []):
        var c: Dictionary = c_v
        var c_id: String = str(c.get("id", ""))
        # match by id prefix or interact tag
        if c_id == hs_id or hs_id.begins_with(c_id) or c_id.begins_with(hs_id):
            matched = c; break
    if matched.is_empty() and hooks.get("ciphers", []).size() > 0:
        # fall back to: cipher whose anchor_norm is nearest the hotspot center
        var rect: Array = hs.get("rect", [0,0,0,0])
        var hs_cx = rect[0] + rect[2] / 2.0
        var hs_cy = rect[1] + rect[3] / 2.0
        var best = null
        var best_d = INF
        for c_v in hooks["ciphers"]:
            var c: Dictionary = c_v
            var a = c.get("anchor_norm", [0.5, 0.5])
            if typeof(a) != TYPE_ARRAY or a.size() < 2: continue
            var d = abs(a[0] - hs_cx) + abs(a[1] - hs_cy)
            if d < best_d: best_d = d; best = c
        if best != null: matched = best

    _render_cipher_panel(hs, matched)
    _trigger_note()


func _render_cipher_panel(hs: Dictionary, cipher: Dictionary) -> void:
    for c in cipher_panel.get_children(): c.queue_free()
    var vbox := VBoxContainer.new()
    vbox.add_theme_constant_override("separation", 3)
    vbox.offset_left = 8; vbox.offset_top = 6
    vbox.offset_right = -8; vbox.offset_bottom = -6
    vbox.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    vbox.offset_left = 8; vbox.offset_top = 6
    vbox.offset_right = -8; vbox.offset_bottom = -6
    cipher_panel.add_child(vbox)

    var head := Label.new()
    head.text = "▷ " + str(hs.get("interact", hs.get("id", "")))
    head.add_theme_color_override("font_color", C_GOLD_HI)
    head.add_theme_font_size_override("font_size", 10)
    vbox.add_child(head)

    if cipher.has("text"):
        var t := Label.new()
        t.text = str(cipher["text"])
        t.add_theme_color_override("font_color", C_TEXT)
        t.add_theme_font_size_override("font_size", 9)
        t.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
        t.custom_minimum_size.x = 320
        vbox.add_child(t)
    if cipher.has("text_lines"):
        for line in cipher["text_lines"]:
            var l := Label.new()
            l.text = "  " + str(line)
            l.add_theme_color_override("font_color", C_TEXT)
            l.add_theme_font_size_override("font_size", 9)
            vbox.add_child(l)
    if cipher.has("encoding_hint"):
        var eh := Label.new()
        eh.text = "↳ " + str(cipher["encoding_hint"])
        eh.add_theme_color_override("font_color", C_TEXT_DIM)
        eh.add_theme_font_size_override("font_size", 8)
        eh.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
        eh.custom_minimum_size.x = 320
        vbox.add_child(eh)
    if cipher.has("reveals"):
        var r := Label.new()
        r.text = "→ unlocks: " + str(cipher["reveals"])
        r.add_theme_color_override("font_color", C_GOLD)
        r.add_theme_font_size_override("font_size", 9)
        vbox.add_child(r)
        # actually flip the unlock flag
        SaveSystem.mark_unlocked(str(cipher["reveals"]))
    if hs.has("unlocks"):
        SaveSystem.mark_unlocked(str(hs["unlocks"]))

    cipher_panel.custom_minimum_size = Vector2(340, 0)
    cipher_panel.visible = true


func _input(event: InputEvent) -> void:
    if not visible: return
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_H:
            # toggle all hotspot visibility (debug)
            for btn in hotspot_btns:
                var sb := (btn.get_theme_stylebox("normal") as StyleBoxFlat)
                if sb:
                    sb.border_color.a = 0.0 if sb.border_color.a > 0 else 0.8
                    btn.add_theme_stylebox_override("normal", sb)
            get_viewport().set_input_as_handled()
