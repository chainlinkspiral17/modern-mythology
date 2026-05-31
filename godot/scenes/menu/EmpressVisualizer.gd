extends "res://scenes/menu/TarotVisualizerBase.gd"
## EmpressVisualizer — split-POV thematic visualizer.
##
## The Empress card visually splits down the centerline:
##   LEFT  = Nicola's sensory POV (burgundy/gold, body-felt)
##   RIGHT = Aria's data overlay POV (emerald, code-stream)
##
## This visualizer's signature: BOTH sides simultaneously visualize
## the same audio signal but in TWO DIFFERENT ways:
##
##   LEFT  side renders a slow-moving WAVEFORM (Nicola's interpretation)
##   RIGHT side renders a fast SPECTRUM / FFT bars (Aria's interpretation)
##
## Same underlying audio (the ambient track or any played note);
## radically different visual abstractions of it. The duality of the
## chapter rendered as audio interpretation duality.

var left_panel: Control
var right_panel: Control
var center_line: ColorRect

# Local color overrides
var C_BURGUNDY  := Color(0.48, 0.12, 0.15)
var C_BURG_HI   := Color(0.80, 0.35, 0.45)
var C_EMERALD   := Color(0.31, 0.63, 0.38)
var C_EM_HI     := Color(0.66, 0.91, 0.61)

# Visualization state — sampled from the audio bus or a running
# AudioEffectSpectrumAnalyzer; here we synthesize the value from
# the active synth notes + ambient gain so it's always lively.
var _vis_t: float = 0.0
var _waveform_buf: PackedFloat32Array = PackedFloat32Array()
const WAVE_LEN := 256
const SPECTRUM_BANDS := 32


func _init() -> void:
    _card_path  = "res://assets/gallery/empress.png"
    _hooks_path = "res://resources/puzzle_hooks/empress.json"
    # No ambient by default — could attach vol5_riverboat_drone.ogg
    # for the chapter's atmospheric track
    _ambient_audio_path = "res://assets/audio/bgm/vol5_riverboat_drone.ogg"
    # Empress palette overrides
    C_BG = Color(0.04, 0.06, 0.04)
    C_GOLD = Color(0.78, 0.66, 0.29)
    C_GOLD_HI = Color(1.0, 0.85, 0.40)
    # Populate waveform buffer
    _waveform_buf.resize(WAVE_LEN)


func _build_thematic_widget() -> void:
    # Left burgundy panel — sensory waveform
    left_panel = Control.new()
    left_panel.anchor_left = 0.02; left_panel.anchor_right = 0.49
    left_panel.anchor_top = 0.72;  left_panel.anchor_bottom = 0.98
    left_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(left_panel)

    var l_bg := ColorRect.new()
    l_bg.color = Color(C_BURGUNDY.r, C_BURGUNDY.g, C_BURGUNDY.b, 0.45)
    l_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    l_bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
    left_panel.add_child(l_bg)

    var l_label := Label.new()
    l_label.text = "  NICOLA · sensory · waveform"
    l_label.add_theme_color_override("font_color", C_BURG_HI)
    l_label.add_theme_font_size_override("font_size", 11)
    l_label.set_anchors_preset(Control.PRESET_TOP_LEFT)
    l_label.offset_top = 4
    left_panel.add_child(l_label)

    var l_wave := _WaveformView.new()
    l_wave.accent = C_BURG_HI
    l_wave.dim = C_BURGUNDY
    l_wave.buf = _waveform_buf
    l_wave.set_anchors_preset(Control.PRESET_FULL_RECT)
    l_wave.offset_top = 22
    l_wave.mouse_filter = Control.MOUSE_FILTER_IGNORE
    l_wave.set_meta("kind", "wave")
    left_panel.add_child(l_wave)
    left_panel.set_meta("view", l_wave)

    # Right emerald panel — data spectrum bars
    right_panel = Control.new()
    right_panel.anchor_left = 0.51; right_panel.anchor_right = 0.98
    right_panel.anchor_top = 0.72;  right_panel.anchor_bottom = 0.98
    right_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(right_panel)

    var r_bg := ColorRect.new()
    r_bg.color = Color(C_EMERALD.r, C_EMERALD.g, C_EMERALD.b, 0.40)
    r_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    r_bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
    right_panel.add_child(r_bg)

    var r_label := Label.new()
    r_label.text = "  ARIA · data · spectrum"
    r_label.add_theme_color_override("font_color", C_EM_HI)
    r_label.add_theme_font_size_override("font_size", 11)
    r_label.set_anchors_preset(Control.PRESET_TOP_LEFT)
    r_label.offset_top = 4
    right_panel.add_child(r_label)

    var r_spec := _SpectrumView.new()
    r_spec.accent = C_EM_HI
    r_spec.dim = C_EMERALD
    r_spec.bands = SPECTRUM_BANDS
    r_spec.set_anchors_preset(Control.PRESET_FULL_RECT)
    r_spec.offset_top = 22
    r_spec.mouse_filter = Control.MOUSE_FILTER_IGNORE
    right_panel.add_child(r_spec)
    right_panel.set_meta("view", r_spec)

    # Centerline divider — the chapter's central conceit visualized
    center_line = ColorRect.new()
    center_line.color = Color(C_GOLD_HI.r, C_GOLD_HI.g, C_GOLD_HI.b, 0.50)
    center_line.anchor_left = 0.495; center_line.anchor_right = 0.505
    center_line.anchor_top = 0.0;    center_line.anchor_bottom = 1.0
    center_line.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(center_line)

    # Help text — what the two sides represent
    var help := Label.new()
    help.text = "[ both sides interpret the same sound · click hotspots on the card to trigger notes ]"
    help.add_theme_color_override("font_color", C_TEXT_DIM)
    help.add_theme_font_size_override("font_size", 9)
    help.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
    help.offset_left = 18; help.offset_bottom = -4
    help.offset_top = -16
    add_child(help)


func _process(delta: float) -> void:
    super(delta)
    _vis_t += delta
    # Shift waveform buffer, sample current audio signal as the
    # newest entry — here we synthesize from active notes + ambient
    # since AudioServer spectrum sampling requires bus effects setup
    if _waveform_buf.size() > 0:
        var newest := _current_audio_sample()
        for i in range(_waveform_buf.size() - 1):
            _waveform_buf[i] = _waveform_buf[i + 1]
        _waveform_buf[_waveform_buf.size() - 1] = newest
    # Trigger redraws
    if left_panel != null and left_panel.has_meta("view"):
        var v: Control = left_panel.get_meta("view")
        v.queue_redraw()
    if right_panel != null and right_panel.has_meta("view"):
        var v2: Control = right_panel.get_meta("view")
        v2.queue_redraw()


func _current_audio_sample() -> float:
    # Sample the running synth notes for a representative value
    var s := 0.0
    for n in _active_notes:
        s += sin(n.freq * n.time * TAU) * 0.6
    # Ambient breath — even when no notes, the chart moves
    s += sin(_vis_t * 1.7) * 0.15
    s += sin(_vis_t * 5.3) * 0.05
    return clamp(s, -1.0, 1.0)


# ── Nested view classes ─────────────────────────────────────────
class _WaveformView extends Control:
    var accent: Color = Color.WHITE
    var dim: Color = Color(0.3, 0.3, 0.3)
    var buf: PackedFloat32Array
    func _draw() -> void:
        if buf == null or buf.size() < 2: return
        var s := size
        if s.x < 4 or s.y < 4: return
        # Center axis
        draw_line(Vector2(0, s.y * 0.5),
                  Vector2(s.x, s.y * 0.5), dim, 1.0)
        # Waveform
        var n := buf.size()
        var px_per := s.x / float(n - 1)
        var prev := Vector2(0, s.y * 0.5 - buf[0] * s.y * 0.45)
        for i in range(1, n):
            var p := Vector2(i * px_per,
                              s.y * 0.5 - buf[i] * s.y * 0.45)
            draw_line(prev, p, accent, 1.5)
            prev = p

class _SpectrumView extends Control:
    var accent: Color = Color.WHITE
    var dim: Color = Color(0.3, 0.3, 0.3)
    var bands: int = 32
    var _rng := RandomNumberGenerator.new()
    var _levels: PackedFloat32Array = PackedFloat32Array()
    var _falloff: float = 0.06
    var _t: float = 0.0
    func _ready() -> void:
        _levels.resize(bands)
    func _process(d: float) -> void:
        _t += d
        for i in bands:
            var target = (sin(_t * (1.0 + i * 0.13)) * 0.5 + 0.5) \
                          * (0.4 + (_rng.randf() * 0.6))
            target *= 1.0 - (i / float(bands)) * 0.3  # high-freq rolloff
            if target > _levels[i]:
                _levels[i] = target
            else:
                _levels[i] = maxf(_levels[i] - _falloff, target)
    func _draw() -> void:
        var s := size
        if s.x < 4 or s.y < 4: return
        var bw := s.x / float(bands)
        for i in bands:
            var h = _levels[i] * s.y * 0.92
            var x = i * bw
            var col = accent.lerp(dim, 1.0 - _levels[i])
            draw_rect(Rect2(x + 1, s.y - h, bw - 2, h), col, true)
            # peak tip
            draw_rect(Rect2(x + 1, s.y - h - 2, bw - 2, 2),
                      accent, true)
