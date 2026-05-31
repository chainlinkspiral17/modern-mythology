extends Control
## FoolVisualizer — dedicated full-screen interactive visualizer for
## the Fool arcana. Built around the Fool's specific RUST_CODE.BBS
## framing: card art occupies the upper viewport, a terminal-style
## BBS console at the bottom accepts commands the player types to
## examine ciphers, walk through the oracle, trigger the synth note,
## reveal cross-references, and burn the counter-wiping easter egg
## (64 wipes → unlock_alt_prologue).
##
## Reuses CardInteractiveLayer's hotspot rendering and synth-note
## trigger on top of the bg art. Adds:
##   • Animated parallax on the fool.png (subtle drift, glitch
##     pulse on the graffiti / steamboat / dog every few seconds)
##   • BBS console — typed input → command parser → response stream
##   • Live cipher reveal log (scrollback as you discover things)
##   • Connection panel (right side) — shows discovered cross-card
##     edges as ASCII-line glyphs
##   • Counter-wipe accumulator (corner gauge)
##
## Pattern is bespoke to the Fool's BBS theme; future per-arcana
## visualizers should each be designed to their card's specific
## metaphor (Magician = warehouse cathedral terminal w/ soldering
## iron mini-game; Empress = split POV toggle; etc).

signal closed

const C_BG          := Color(0.020, 0.012, 0.010)
const C_INK         := Color(0.05, 0.03, 0.04)
const C_GOLD        := Color(0.85, 0.63, 0.38)
const C_GOLD_HI     := Color(1.0,  0.85, 0.59)
const C_AMBER       := Color(0.95, 0.62, 0.18)
const C_GREEN_CRT   := Color(0.30, 0.95, 0.45)
const C_GREEN_DIM   := Color(0.16, 0.50, 0.24)
const C_TEXT        := Color(0.85, 0.72, 0.50)
const C_TEXT_DIM    := Color(0.52, 0.40, 0.22)
const C_RED         := Color(0.85, 0.25, 0.20)

const CARD_PATH := "res://assets/gallery/fool.png"
const HOOKS_PATH := "res://resources/puzzle_hooks/fool.json"

# Inline 22-arcana timbre subset (just need fool here; full table
# lives in CardInteractiveLayer + TarotSynthOverlay)
const FOOL_TIMBRE := {
    "wave": "square", "freq": 110.0,
    "atk": 0.02, "dur": 1.0, "rel": 0.5
}

var hooks: Dictionary = {}
var card_rect: TextureRect
var hotspot_btns: Array = []
var console_input: LineEdit
var console_log: RichTextLabel
var connections_panel: VBoxContainer
var wipe_counter_label: Label
var wipe_count: int = 0

# Audio
var _gen: AudioStreamGenerator
var _gen_player: AudioStreamPlayer
var _playback: AudioStreamGeneratorPlayback
var _active_notes: Array = []

# Animation phase for the glitch pulse on the card
var _glitch_t: float = 0.0


func _ready() -> void:
    set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    mouse_filter = Control.MOUSE_FILTER_STOP
    _load_hooks()
    _init_audio()
    _build_ui()
    set_process(true)
    set_process_input(true)
    _log("[color=#d8a060]RUST_CODE.BBS · GRAUSTARK_FRONTIER · NODE 0[/color]")
    _log("[color=#7a5828]welcome. type [color=#ffd896]help[/color] for commands.[/color]")
    _log("")


func _load_hooks() -> void:
    if not FileAccess.file_exists(HOOKS_PATH): return
    var f := FileAccess.open(HOOKS_PATH, FileAccess.READ)
    hooks = JSON.parse_string(f.get_as_text())
    f.close()


# ── UI ───────────────────────────────────────────────────────────
func _build_ui() -> void:
    # Backdrop
    var bg := ColorRect.new()
    bg.color = C_BG
    bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    bg.mouse_filter = Control.MOUSE_FILTER_STOP
    add_child(bg)

    # Card art zone — upper 60% of screen
    var card_zone := Control.new()
    card_zone.anchor_left = 0.02; card_zone.anchor_right = 0.74
    card_zone.anchor_top = 0.03;  card_zone.anchor_bottom = 0.62
    add_child(card_zone)

    card_rect = TextureRect.new()
    card_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    card_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
    card_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
    card_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
    if ResourceLoader.exists(CARD_PATH):
        card_rect.texture = load(CARD_PATH)
    card_zone.add_child(card_rect)

    # Hotspots layer above the card
    _build_hotspots(card_zone)

    # Title strip (above card)
    var title := Label.new()
    title.text = "0 · THE FOOL — between acts"
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

    # Connections panel — right margin
    var conn_zone := PanelContainer.new()
    conn_zone.anchor_left = 0.75; conn_zone.anchor_right = 0.99
    conn_zone.anchor_top = 0.04;  conn_zone.anchor_bottom = 0.62
    var ps := StyleBoxFlat.new()
    ps.bg_color = C_INK
    ps.border_color = C_GOLD
    ps.set_border_width_all(1)
    conn_zone.add_theme_stylebox_override("panel", ps)
    add_child(conn_zone)

    var conn_outer := VBoxContainer.new()
    conn_outer.add_theme_constant_override("separation", 4)
    conn_zone.add_child(conn_outer)

    var conn_hdr := Label.new()
    conn_hdr.text = "↔ RUST_CODE.BBS · CONNECTIONS"
    conn_hdr.add_theme_color_override("font_color", C_GOLD_HI)
    conn_hdr.add_theme_font_size_override("font_size", 10)
    conn_outer.add_child(conn_hdr)
    conn_outer.add_child(_rule())

    var scroll := ScrollContainer.new()
    scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
    conn_outer.add_child(scroll)
    connections_panel = VBoxContainer.new()
    connections_panel.add_theme_constant_override("separation", 6)
    connections_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    scroll.add_child(connections_panel)
    _populate_connections()

    # Wipe counter (corner gauge)
    wipe_counter_label = Label.new()
    wipe_counter_label.text = "wipes: 0/64"
    wipe_counter_label.add_theme_color_override("font_color", C_TEXT_DIM)
    wipe_counter_label.add_theme_font_size_override("font_size", 9)
    wipe_counter_label.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
    wipe_counter_label.offset_left = 18
    wipe_counter_label.offset_bottom = -210
    wipe_counter_label.offset_top = -226
    add_child(wipe_counter_label)

    # Console zone — bottom 35%
    var con_zone := PanelContainer.new()
    con_zone.anchor_left = 0.02; con_zone.anchor_right = 0.99
    con_zone.anchor_top = 0.64;  con_zone.anchor_bottom = 0.98
    var cs := StyleBoxFlat.new()
    cs.bg_color = C_INK
    cs.border_color = C_GREEN_DIM
    cs.set_border_width_all(1)
    con_zone.add_theme_stylebox_override("panel", cs)
    add_child(con_zone)

    var con_box := VBoxContainer.new()
    con_box.add_theme_constant_override("separation", 4)
    con_zone.add_child(con_box)

    var con_hdr := Label.new()
    con_hdr.text = "$ RUST_CODE.BBS · TTY 0 · 3:47 AM ·  type 'help' to list commands"
    con_hdr.add_theme_color_override("font_color", C_GREEN_DIM)
    con_hdr.add_theme_font_size_override("font_size", 9)
    con_box.add_child(con_hdr)

    console_log = RichTextLabel.new()
    console_log.bbcode_enabled = true
    console_log.scroll_following = true
    console_log.size_flags_vertical = Control.SIZE_EXPAND_FILL
    console_log.add_theme_font_size_override("normal_font_size", 11)
    console_log.add_theme_color_override("default_color", C_GREEN_CRT)
    con_box.add_child(console_log)

    var input_row := HBoxContainer.new()
    input_row.add_theme_constant_override("separation", 4)
    var prompt := Label.new()
    prompt.text = "> "
    prompt.add_theme_color_override("font_color", C_AMBER)
    prompt.add_theme_font_size_override("font_size", 12)
    input_row.add_child(prompt)
    console_input = LineEdit.new()
    console_input.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    console_input.add_theme_color_override("font_color", C_GREEN_CRT)
    console_input.add_theme_color_override("caret_color", C_AMBER)
    console_input.text_submitted.connect(_on_command)
    input_row.add_child(console_input)
    con_box.add_child(input_row)
    console_input.grab_focus()


func _rule() -> ColorRect:
    var r := ColorRect.new()
    r.color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.35)
    r.custom_minimum_size.y = 1
    return r


func _build_hotspots(parent: Control) -> void:
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
        parent.add_child(btn)
        hotspot_btns.append(btn)
    parent.resized.connect(_update_hotspot_positions)
    call_deferred("_update_hotspot_positions")


func _update_hotspot_positions() -> void:
    var p := card_rect.size
    for btn in hotspot_btns:
        var rect: Array = btn.get_meta("rect_norm", [0.0, 0.0, 0.1, 0.1])
        btn.position = Vector2(rect[0] * p.x, rect[1] * p.y)
        btn.size = Vector2(rect[2] * p.x, rect[3] * p.y)


func _populate_connections() -> void:
    var xref: Dictionary = hooks.get("cross_references", {})
    for k in xref.keys():
        var row := Label.new()
        row.text = "▸ %s\n   %s" % [k, str(xref[k])]
        row.add_theme_color_override("font_color", C_TEXT)
        row.add_theme_font_size_override("font_size", 9)
        row.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
        connections_panel.add_child(row)


# ── Command parser ───────────────────────────────────────────────
func _on_command(text: String) -> void:
    var line := text.strip_edges().to_lower()
    console_input.text = ""
    _log("[color=#e89c30]> %s[/color]" % text)
    if line == "":
        return
    var parts := line.split(" ", false)
    var cmd := parts[0]
    var arg := " ".join(parts.slice(1)) if parts.size() > 1 else ""

    match cmd:
        "help", "?", "commands":
            _cmd_help()
        "ls", "list":
            _cmd_list(arg)
        "examine", "look", "x":
            _cmd_examine(arg)
        "read":
            _cmd_read(arg)
        "play", "note":
            _cmd_play()
        "wipe":
            _cmd_wipe()
        "connect":
            _cmd_connect(arg)
        "oracle":
            _cmd_oracle()
        "exit", "quit", "close":
            closed.emit()
        "clear", "cls":
            console_log.clear()
        _:
            _log("[color=#7a5828]? unknown command. type [color=#ffd896]help[/color][/color]")


func _cmd_help() -> void:
    _log("[color=#d8a060]commands:[/color]")
    _log("  [color=#ffd896]help[/color]              — this list")
    _log("  [color=#ffd896]ls ciphers[/color]        — list discoverable ciphers")
    _log("  [color=#ffd896]ls hotspots[/color]       — list interactable rects")
    _log("  [color=#ffd896]ls connections[/color]    — list cross-card edges")
    _log("  [color=#ffd896]examine <thing>[/color]   — inspect ciphers + hotspots by id or keyword")
    _log("  [color=#ffd896]read oracle[/color]       — print the Fool's oracle text")
    _log("  [color=#ffd896]play[/color] / [color=#ffd896]note[/color]       — trigger the Fool's synth note")
    _log("  [color=#ffd896]wipe[/color]              — wipe the counter (×64 = ?)")
    _log("  [color=#ffd896]connect <card>[/color]    — show cross-references to <card>")
    _log("  [color=#ffd896]exit[/color]              — close visualizer")


func _cmd_list(arg: String) -> void:
    if arg in ["ciphers", "cipher", "c"]:
        for c_v in hooks.get("ciphers", []):
            var c: Dictionary = c_v
            var prio = "  " if str(c.get("priority","")) == "" else "★ "
            _log("[color=#d8a060]%s%s[/color]  [color=#7a5828]· %s[/color]" % [
                prio, c.get("id",""), c.get("kind","")
            ])
    elif arg in ["hotspots", "hotspot", "h"]:
        for h_v in hooks.get("hotspots", []):
            var h: Dictionary = h_v
            _log("[color=#d8a060]%s[/color]  [color=#7a5828]→ %s[/color]" % [
                h.get("id",""), h.get("unlocks","")
            ])
    elif arg in ["connections", "connection", "x", "xrefs"]:
        var xref: Dictionary = hooks.get("cross_references", {})
        for k in xref.keys():
            _log("[color=#d8a060]%s[/color]  [color=#7a5828]→ %s[/color]" % [k, xref[k]])
    else:
        _log("[color=#7a5828]ls what? try: ciphers · hotspots · connections[/color]")


func _cmd_examine(arg: String) -> void:
    if arg == "":
        _log("[color=#7a5828]examine what? (try: bindle / dog / graffiti / counter / inner_card / design_notes)[/color]")
        return
    # try matching by id or keyword in any cipher's text
    var matched: Dictionary = {}
    for c_v in hooks.get("ciphers", []):
        var c: Dictionary = c_v
        var hay = (str(c.get("id","")) + " " + str(c.get("text","")) + " " +
                   str(c.get("text_lines",[]))).to_lower()
        if arg in hay:
            matched = c; break
    if matched.is_empty():
        for h_v in hooks.get("hotspots", []):
            var h: Dictionary = h_v
            if arg in str(h.get("id","")).to_lower():
                _on_hotspot(h); return
        _log("[color=#7a5828]? nothing here named '%s'[/color]" % arg)
        return
    _print_cipher(matched)
    if matched.has("reveals"):
        SaveSystem.mark_unlocked(str(matched["reveals"]))


func _cmd_read(arg: String) -> void:
    if arg == "" or arg in ["oracle", "card"]:
        _cmd_oracle()
    else:
        _cmd_examine(arg)


func _cmd_oracle() -> void:
    var oracle = null
    for c_v in hooks.get("ciphers", []):
        var c: Dictionary = c_v
        if str(c.get("kind","")) == "inline_oracle":
            oracle = c; break
    if oracle == null:
        _log("[color=#7a5828]no oracle text found in hooks[/color]")
        return
    _log("[color=#d8a060]── THE FOOL ──────────────────────[/color]")
    for line in oracle.get("text_lines", []):
        _log("[color=#c8a878]%s[/color]" % line)
    _log("")
    SaveSystem.mark_unlocked("lore:fool_oracle_read")


func _cmd_play() -> void:
    _trigger_note()
    _log("[color=#30ee50]♪ pulse_soft @ 110.0 Hz — 1.0s release[/color]")


func _cmd_wipe() -> void:
    wipe_count += 1
    wipe_counter_label.text = "wipes: %d/64" % wipe_count
    SaveSystem.mark_unlocked("lore:counter_wiped_again")
    if wipe_count == 64:
        _log("[color=#ff8050]── 64 WIPES ─ ALT PROLOGUE UNLOCKED ──[/color]")
        SaveSystem.mark_unlocked("vol5_alt_prologue_unlocked")
    elif wipe_count % 8 == 0:
        _log("[color=#7a5828](wipe %d. the formica is the same.)[/color]" % wipe_count)
    else:
        _log("[color=#3a2614](wipe.)[/color]")


func _cmd_connect(arg: String) -> void:
    var xref: Dictionary = hooks.get("cross_references", {})
    if arg == "":
        for k in xref.keys():
            _log("[color=#d8a060]↔ %s[/color]  [color=#c8a878]· %s[/color]" % [k, xref[k]])
        return
    for k in xref.keys():
        if arg in k.to_lower() or arg in str(xref[k]).to_lower():
            _log("[color=#d8a060]▶ %s[/color]" % k)
            _log("[color=#c8a878]  %s[/color]" % xref[k])
            return
    _log("[color=#7a5828]? no connection to '%s' from here[/color]" % arg)


func _on_hotspot(hs: Dictionary) -> void:
    var hs_id = str(hs.get("id",""))
    var matched: Dictionary = {}
    for c_v in hooks.get("ciphers", []):
        var c: Dictionary = c_v
        var cid = str(c.get("id",""))
        if cid == hs_id or hs_id.contains(cid) or cid.contains(hs_id):
            matched = c; break
    _log("[color=#d8a060]▷ %s[/color]" % hs.get("interact", hs_id))
    if not matched.is_empty():
        _print_cipher(matched)
        if matched.has("reveals"):
            SaveSystem.mark_unlocked(str(matched["reveals"]))
    if hs.has("unlocks"):
        SaveSystem.mark_unlocked(str(hs["unlocks"]))
        _log("[color=#7a5828]  → unlocked: %s[/color]" % hs["unlocks"])
    # Special: counter hotspot increments wipe count
    if hs_id == "fool_counter":
        _cmd_wipe()
    _trigger_note()


func _print_cipher(c: Dictionary) -> void:
    if c.has("text"):
        _log("  [color=#c8a878]%s[/color]" % c["text"])
    if c.has("text_lines"):
        for line in c["text_lines"]:
            _log("  [color=#c8a878]│ %s[/color]" % line)
    if c.has("encoding_hint"):
        _log("  [color=#7a5828]↳ %s[/color]" % c["encoding_hint"])
    if c.has("reveals"):
        _log("  [color=#d8a060]→ reveals: %s[/color]" % c["reveals"])


func _log(line: String) -> void:
    console_log.append_text(line + "\n")


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


func _trigger_note() -> void:
    _active_notes.append({
        "time": 0.0,
        "freq": FOOL_TIMBRE.freq,
        "wave": FOOL_TIMBRE.wave,
        "atk": FOOL_TIMBRE.atk,
        "dur": FOOL_TIMBRE.dur,
        "rel": FOOL_TIMBRE.rel,
    })


func _process(delta: float) -> void:
    # Audio pump
    if _playback != null:
        var frames := _playback.get_frames_available()
        if frames > 0:
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

    # Subtle card breathing (modulate alpha + position slightly)
    _glitch_t += delta
    if card_rect != null:
        var pulse = 0.95 + sin(_glitch_t * 0.6) * 0.05
        card_rect.modulate.a = pulse
        card_rect.position.x = sin(_glitch_t * 0.4) * 2.0


func _sample_note(n: Dictionary) -> float:
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
    if not visible: return
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_ESCAPE:
            closed.emit()
            get_viewport().set_input_as_handled()


# Public open/close
func open() -> void:
    visible = true
    if console_input != null: console_input.grab_focus()


func close() -> void:
    visible = false
