extends "res://scenes/menu/TarotVisualizerBase.gd"
## EmpressVisualizer — split-POV: Nicola (burgundy) · Aria (emerald).
##
## The Empress card lives down a centerline: LEFT half is Nicola's
## sensory POV (burgundy/gold, body-felt); RIGHT half is Aria's data
## overlay (emerald, code-stream). This visualizer carries that split
## EVERYWHERE — palette, tableau direction, console prompt, audio
## interpretation.
##
##   • SIGNATURE WIDGET (preserved from prior version) — a dual
##     audio interpreter docked in the bottom strip. The SAME audio
##     signal is rendered TWO different ways:
##       LEFT  burgundy WAVEFORM (Nicola feels it)
##       RIGHT emerald SPECTRUM (Aria reads it)
##     Whichever POV is active glows brighter.
##
##   • CARD HOTSPOTS — seven rects on the painted Empress card:
##       BOOK       Nicola's journal (mid-card)
##       KLONOPIN   her prescription bottle (upper-left of desk)
##       CHAMPAGNE  cheap house pour (next to pills)
##       RAM_L      left ram-head on the throne
##       RAM_R      right ram-head on the throne
##       TOGGLE     the vertical centerline — flips dominant POV
##       CAPTION    the prison-of-meat caption at the card's foot
##
##   • BBS CONSOLE — prompt swaps with POV: `nicola@body:~$ ` vs
##     `aria@grid:~$ `. Same commands; different flavor text.
##
##   • TABLEAU — split by POV.  WEST + SOUTH are Nicola (burgundy /
##     sensory / body-felt). EAST + NORTH are Aria (emerald / data /
##     diagnostic).

# ── Game state ───────────────────────────────────────────────────
enum POV { NICOLA = 0, ARIA = 1 }
var active_pov: int = POV.NICOLA
var pov_toggles: int = 0
var book_page: int = 0           # 0..N of Nicola's journal entries
var pill_taken: int = 0
var champagne_sips: int = 0
var ram_l_touched: bool = false
var ram_r_touched: bool = false
var caption_read: bool = false
var hotspots_seen: Dictionary = {}
var commands_run: Dictionary = {}
var memory: PackedStringArray = []
var tableau_pulse: float = 0.0
var pov_blend: float = 0.0       # 0.0 = nicola, 1.0 = aria — smoothed

# ── UI refs ──────────────────────────────────────────────────────
var tally_btn: Button
var status_label: Label
var prompt_label: Label
var console_input: LineEdit
var console_log: RichTextLabel
var dual_widget: Control
var left_panel: Control
var right_panel: Control
var left_view: Control
var right_view: Control
var center_glow: ColorRect

# ── Palette ──────────────────────────────────────────────────────
var C_BURGUNDY  := Color(0.48, 0.14, 0.18)
var C_BURG_HI   := Color(0.86, 0.42, 0.50)
var C_EMERALD   := Color(0.30, 0.62, 0.38)
var C_EM_HI     := Color(0.62, 0.92, 0.62)

# Audio visualization state
var _vis_t: float = 0.0
var _waveform_buf: PackedFloat32Array = PackedFloat32Array()
const WAVE_LEN := 256
const SPECTRUM_BANDS := 32

# Nicola's journal entries (revealed by book hotspot / command)
const JOURNAL_ENTRIES := [
	"she writes: 'my body is a prison. find the exit node.'",
	"she writes: 'the champagne is cheap. it works anyway.'",
	"she writes: 'Klonopin at 11. Klonopin at 2. Klonopin at when.'",
	"she writes: 'the ram-heads recognize me. how.'",
	"she writes: 'Aria pings me every three minutes. she is patient.'",
	"she writes: 'the throne is still warm. someone just stood up.'",
	"she writes: 'I am the inheritor of a thing I did not earn.'",
	"she writes: 'the river. the river. the river.'",
	"she writes nothing. the page is wet. it has been wept on.",
]

# Aria's diagnostic stream (revealed by hotspots — Aria's POV log)
const ARIA_FLAGS := [
	"[ARIA] handshake: ESTABLISHED",
	"[ARIA] biometric overlay: ANXIETY SPIKE → ALERT",
	"[ARIA] exit_node_search: ACTIVE",
	"[ARIA] system: CONFINED",
	"[ARIA] inheritance_event: PROBABILITY 0.91",
	"[ARIA] cross-card link: vol3 character match (heartrate 72)",
	"[ARIA] code stream: 'code sown behind eyes' · 'get rovsrs code'",
	"[ARIA] anagram lock: 'get rovers' → vol5_rovers_module",
	"[ARIA] subroutine: reality.subroutine running (PID 1)",
]


func _init() -> void:
	_card_path  = "res://assets/gallery/empress.png"
	_composition_path = "empress_card"
	_hooks_path = "res://resources/puzzle_hooks/empress.json"
	_ambient_audio_path = "res://assets/audio/bgm/vol5_riverboat_drone.ogg"
	C_BG = Color(0.04, 0.05, 0.05)
	C_GOLD = Color(0.78, 0.66, 0.29)
	C_GOLD_HI = Color(1.0, 0.85, 0.40)
	C_TEXT = Color(0.78, 0.68, 0.58)
	C_TEXT_DIM = Color(0.42, 0.34, 0.28)
	_waveform_buf.resize(WAVE_LEN)


func _build_chrome() -> void:
	super()
	_build_bottom_strip()
	_build_card_hotspots()


# Per-region hotspots on the painted Empress card.
func _build_card_hotspots() -> void:
	if card_rect == null: return
	var defs := [
		["book",      Rect2(0.43, 0.43, 0.14, 0.22), "read Nicola's journal",   _do_book],
		["klonopin",  Rect2(0.25, 0.38, 0.06, 0.10), "examine the Klonopin",    _do_klonopin],
		["champagne", Rect2(0.31, 0.30, 0.06, 0.17), "examine the champagne",   _do_champagne],
		["ram_l",     Rect2(0.34, 0.13, 0.10, 0.14), "touch the left ram",      _do_ram_l],
		["ram_r",     Rect2(0.56, 0.13, 0.10, 0.14), "touch the right ram",     _do_ram_r],
		["toggle",    Rect2(0.485, 0.04, 0.03, 0.92), "flip the POV centerline", _do_toggle],
		["caption",   Rect2(0.30, 0.82, 0.40, 0.08), "read the caption",        _do_caption],
	]
	for d in defs:
		var btn := Button.new()
		btn.flat = true
		var rect: Rect2 = d[1]
		btn.position = card_rect.position + Vector2(
			rect.position.x * card_rect.size.x,
			rect.position.y * card_rect.size.y)
		btn.size = Vector2(
			rect.size.x * card_rect.size.x,
			rect.size.y * card_rect.size.y)
		btn.tooltip_text = str(d[2])
		var sb := StyleBoxFlat.new()
		sb.bg_color = Color(0.95, 0.55, 0.50, 0.0)
		sb.border_color = Color(0.95, 0.55, 0.50, 0.0)
		sb.set_border_width_all(1)
		btn.add_theme_stylebox_override("normal", sb)
		var bsh := sb.duplicate() as StyleBoxFlat
		if d[0] == "toggle":
			bsh.bg_color = Color(1, 0.85, 0.40, 0.30)
			bsh.border_color = Color(1, 0.92, 0.55, 0.90)
		else:
			bsh.bg_color = Color(0.95, 0.55, 0.50, 0.20)
			bsh.border_color = Color(1.0, 0.75, 0.65, 0.80)
		btn.add_theme_stylebox_override("hover", bsh)
		btn.add_theme_stylebox_override("focus", bsh)
		btn.pressed.connect(d[3])
		canvas.add_child(btn)


func _build_bottom_strip() -> void:
	# Taller strip — holds the dual-POV audio widget + console
	var bot := PanelContainer.new()
	bot.anchor_left = 0; bot.anchor_right = 1
	bot.anchor_top = 1;  bot.anchor_bottom = 1
	bot.offset_top = -230
	var bps := StyleBoxFlat.new()
	bps.bg_color = Color(0.02, 0.025, 0.025, 0.85)
	bps.border_color = C_GOLD
	bps.border_width_top = 1
	bot.add_theme_stylebox_override("panel", bps)
	add_child(bot)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 2)
	bot.add_child(vbox)

	# Dual-POV widget — TOP of bottom strip, full width, ~95px tall
	dual_widget = Control.new()
	dual_widget.custom_minimum_size = Vector2(0, 95)
	dual_widget.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	vbox.add_child(dual_widget)
	_build_dual_widget()

	# Console log
	console_log = RichTextLabel.new()
	console_log.bbcode_enabled = true
	console_log.scroll_following = true
	console_log.size_flags_vertical = Control.SIZE_EXPAND_FILL
	console_log.add_theme_font_size_override("normal_font_size", 11)
	console_log.add_theme_color_override("default_color",
		Color(0.85, 0.78, 0.65))
	vbox.add_child(console_log)

	# Console input — POV-aware prompt
	var inrow := HBoxContainer.new()
	inrow.add_theme_constant_override("separation", 4)
	prompt_label = Label.new()
	prompt_label.text = "nicola@body:~$ "
	prompt_label.add_theme_color_override("font_color", C_BURG_HI)
	prompt_label.add_theme_font_size_override("font_size", 12)
	inrow.add_child(prompt_label)
	console_input = LineEdit.new()
	console_input.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	console_input.add_theme_color_override("font_color",
		Color(0.95, 0.85, 0.70))
	console_input.text_submitted.connect(_on_command)
	inrow.add_child(console_input)
	vbox.add_child(inrow)

	var actrow := HBoxContainer.new()
	actrow.add_theme_constant_override("separation", 12)
	vbox.add_child(actrow)

	tally_btn = Button.new()
	tally_btn.text = "  ♀ book 0/9 · sips 0 · pills 0 · POV: NICOLA  "
	tally_btn.add_theme_color_override("font_color", C_GOLD_HI)
	tally_btn.add_theme_font_size_override("font_size", 11)
	var wbs := StyleBoxFlat.new()
	wbs.bg_color = Color(C_GOLD.r * 0.2, C_GOLD.g * 0.2, C_GOLD.b * 0.2, 0.5)
	wbs.border_color = C_GOLD
	wbs.set_border_width_all(1)
	tally_btn.add_theme_stylebox_override("normal", wbs)
	var wbh := wbs.duplicate() as StyleBoxFlat
	wbh.bg_color = Color(C_GOLD.r * 0.45, C_GOLD.g * 0.45, C_GOLD.b * 0.45, 0.7)
	wbh.border_color = C_GOLD_HI
	tally_btn.add_theme_stylebox_override("hover", wbh)
	tally_btn.pressed.connect(_do_toggle)
	tally_btn.tooltip_text = "click → toggle POV (or click the card centerline)"
	actrow.add_child(tally_btn)

	status_label = Label.new()
	status_label.text = "click the card · book · pill · champagne · ram · toggle"
	status_label.add_theme_color_override("font_color",
		Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.80))
	status_label.add_theme_font_size_override("font_size", 10)
	status_label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	status_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	actrow.add_child(status_label)

	_log("[color=#d8826e]> III · EMPRESS · vol.5 ch.3 · Graustark River[/color]")
	_log("[color=#7a4040]> palette: split burgundy + emerald. dual POV.[/color]")
	_log("[color=#d8826e]> \"This prison of meat.[/color]")
	_log("[color=#d8826e]>  Find the exit node.[/color]")
	_log("[color=#d8826e]>  There has to be a way out of this system.\"[/color]")
	_log("[color=#7a4040]> type [color=#ff9080]help[/color] · toggle POV with the centerline.[/color]")

	console_input.grab_focus()


func _build_dual_widget() -> void:
	# Left burgundy panel — Nicola's waveform
	left_panel = Control.new()
	left_panel.anchor_left = 0.0; left_panel.anchor_right = 0.495
	left_panel.anchor_top = 0.0;  left_panel.anchor_bottom = 1.0
	left_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	dual_widget.add_child(left_panel)

	var l_bg := ColorRect.new()
	l_bg.color = Color(C_BURGUNDY.r, C_BURGUNDY.g, C_BURGUNDY.b, 0.40)
	l_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	l_bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	left_panel.add_child(l_bg)

	var l_label := Label.new()
	l_label.text = "  ♀ NICOLA · sensory · waveform"
	l_label.add_theme_color_override("font_color", C_BURG_HI)
	l_label.add_theme_font_size_override("font_size", 10)
	l_label.position = Vector2(6, 2)
	left_panel.add_child(l_label)

	var l_wave := _WaveformView.new()
	l_wave.accent = C_BURG_HI
	l_wave.dim = C_BURGUNDY
	l_wave.buf = _waveform_buf
	l_wave.anchor_left = 0; l_wave.anchor_right = 1
	l_wave.anchor_top = 0;  l_wave.anchor_bottom = 1
	l_wave.offset_top = 18
	l_wave.mouse_filter = Control.MOUSE_FILTER_IGNORE
	left_panel.add_child(l_wave)
	left_view = l_wave

	# Right emerald panel — Aria's spectrum
	right_panel = Control.new()
	right_panel.anchor_left = 0.505; right_panel.anchor_right = 1.0
	right_panel.anchor_top = 0.0;    right_panel.anchor_bottom = 1.0
	right_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	dual_widget.add_child(right_panel)

	var r_bg := ColorRect.new()
	r_bg.color = Color(C_EMERALD.r, C_EMERALD.g, C_EMERALD.b, 0.35)
	r_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	r_bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	right_panel.add_child(r_bg)

	var r_label := Label.new()
	r_label.text = "  ░ ARIA · data · spectrum"
	r_label.add_theme_color_override("font_color", C_EM_HI)
	r_label.add_theme_font_size_override("font_size", 10)
	r_label.position = Vector2(6, 2)
	right_panel.add_child(r_label)

	var r_spec := _SpectrumView.new()
	r_spec.accent = C_EM_HI
	r_spec.dim = C_EMERALD
	r_spec.bands = SPECTRUM_BANDS
	r_spec.anchor_left = 0; r_spec.anchor_right = 1
	r_spec.anchor_top = 0;  r_spec.anchor_bottom = 1
	r_spec.offset_top = 18
	r_spec.mouse_filter = Control.MOUSE_FILTER_IGNORE
	right_panel.add_child(r_spec)
	right_view = r_spec

	# Center glowing divider — the POV centerline
	center_glow = ColorRect.new()
	center_glow.color = Color(C_GOLD_HI.r, C_GOLD_HI.g, C_GOLD_HI.b, 0.85)
	center_glow.anchor_left = 0.495; center_glow.anchor_right = 0.505
	center_glow.anchor_top = 0.0;    center_glow.anchor_bottom = 1.0
	center_glow.mouse_filter = Control.MOUSE_FILTER_IGNORE
	dual_widget.add_child(center_glow)


# ── Tableau registration ─────────────────────────────────────────
func _build_thematic_widget() -> void:
	var c_burg := C_BURG_HI
	var c_burg_dim := Color(0.50, 0.20, 0.24, 0.9)
	var c_burg_hot := Color(0.95, 0.60, 0.65, 1.0)
	var c_em := C_EM_HI
	var c_em_dim := Color(0.22, 0.45, 0.30, 0.9)
	var c_em_hot := Color(0.75, 1.00, 0.75, 1.0)
	var c_gold := C_GOLD_HI
	var c_water := Color(0.45, 0.65, 0.80, 0.85)
	var c_river := Color(0.30, 0.50, 0.65, 0.85)

	# ────────────────────────────────────────────────────────────
	# NORTH — ARIA / data overlay / above-the-body
	# ────────────────────────────────────────────────────────────
	_register_segment({"dir": Dir.NORTH, "row": 0, "tint": c_em_dim,
		"font_size": 13, "requires": null,
		"ascii":
"""
	╔═══════════════════════════════════════════════════╗
	║   III (label says IV)  ░░  THE EMPRESS  ░░  DUAL ║
	╚═══════════════════════════════════════════════════╝
		─── nicola below / aria above ─── prison + grid ───
"""
	})
	_register_segment({"dir": Dir.NORTH, "row": 1, "tint": c_em,
		"font_size": 11,
		"requires": null,
		"ascii":
"""
	┌─── ARIA · default diagnostic ────────────────────┐
	│  BIOMETRICS    : monitoring                      │
	│  ANXIETY       : nominal                         │
	│  EXIT_NODE     : SEARCHING                       │
	│  SYSTEM        : CONFINED                        │
	│  HANDSHAKE     : awaiting host ack               │
	└──────────────────────────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.NORTH, "row": 2, "tint": c_em,
		"font_size": 11,
		"requires": func(): return hotspots_seen.has("pill"),
		"ascii":
"""
	┌─── ARIA · spike ─────────────────────────────────┐
	│  ANXIETY SPIKE: ALERT                            │
	│  source: Klonopin uptake event                   │
	│  delta:  +14.2% pulse · 22 bpm jump              │
	│  recommend: route 240ms downstream filter        │
	│  (she ignores the recommendation, as always)     │
	└──────────────────────────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.NORTH, "row": 3, "tint": c_em_hot,
		"font_size": 11,
		"requires": func(): return commands_run.get("rovers", 0) >= 1 or commands_run.get("code", 0) >= 1,
		"ascii":
"""
	╔══════════════════════════════════════════════════╗
	║  ░▒▓ CODE STREAM · ARIA channel ▓▒░              ║
	║                                                  ║
	║      code sown behind eyes                       ║
	║      code_streams stream                         ║
	║      get rovsrs code                             ║
	║                                                  ║
	║  anagram lock: 'get rovers' →                    ║
	║  vol5_rovers_module unlocked.                    ║
	╚══════════════════════════════════════════════════╝
"""
	})
	_register_segment({"dir": Dir.NORTH, "row": 4, "tint": c_em,
		"font_size": 11,
		"requires": func(): return pov_toggles >= 1,
		"ascii":
"""
			░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
			░░  POV: ARIA — the data is the truth.  ░░
			░░  the body is a latency layer.        ░░
			░░  Nicola is the host. Aria is the     ░░
			░░  process. they share the same stack. ░░
			░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""
	})
	_register_segment({"dir": Dir.NORTH, "row": 5, "tint": c_em_hot,
		"font_size": 11,
		"requires": func(): return commands_run.get("handshake", 0) >= 1,
		"ascii":
"""
			╔══════════════════════════════════╗
			║  ░ HANDSHAKE COMPLETE ░          ║
			║  ARIA ⇄ NICOLA                   ║
			║  vol5_aria_handshake = TRUE      ║
			║  signal-frame stable; latency   ║
			║  has dropped to 14ms.            ║
			║  she can hear her think now.     ║
			║  she always could.               ║
			╚══════════════════════════════════╝
"""
	})
	_register_segment({"dir": Dir.NORTH, "row": 6, "tint": c_em,
		"font_size": 11,
		"requires": func(): return hotspots_seen.size() >= 6,
		"ascii":
"""
			┌─────────────────────────────────────┐
			│  ░ ARIA observes Frasier's CRT ░    │
			│  the heartrate trace on his screen  │
			│  is Nicola's. PID 248.              │
			│  he doesn't know whose. she does.   │
			│  she does not tell him.             │
			└─────────────────────────────────────┘
"""
	})

	# ────────────────────────────────────────────────────────────
	# SOUTH — NICOLA / body / desk / champagne / river
	# ────────────────────────────────────────────────────────────
	_register_segment({"dir": Dir.SOUTH, "row": 0, "tint": c_burg_dim,
		"font_size": 12, "requires": null,
		"ascii":
"""
	═════════ THE DESK · NICOLA's side ═══════════════════
		░ a glass of champagne · a journal · a bottle of   ░
		░ Klonopin · a folded napkin · a single key ░░░░░░░
		░ a fleur-de-lis embroidered on the tablecloth ░░░░
"""
	})
	_register_segment({"dir": Dir.SOUTH, "row": 1, "tint": c_burg,
		"font_size": 11,
		"requires": func(): return book_page >= 1,
		"ascii":
"""
			┌──── from Nicola's journal ────┐
			│  my body is a prison.         │
			│  find the exit node.          │
			│  there has to be a way out    │
			│  of this system.              │
			│  ─── she has signed it ───    │
			│  ─── in Aria's hand ───       │
			└───────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.SOUTH, "row": 2, "tint": c_burg,
		"font_size": 11,
		"requires": func(): return book_page >= 4,
		"ascii":
"""
			┌──── journal · entries 2-4 ────┐
			│  the champagne is cheap.      │
			│  it works anyway.             │
			│                               │
			│  Klonopin at 11 · 2 · when    │
			│                               │
			│  the ram-heads recognize me.  │
			│  how.                         │
			└───────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.SOUTH, "row": 3, "tint": c_burg_hot,
		"font_size": 11,
		"requires": func(): return book_page >= 7,
		"ascii":
"""
			┌──── journal · the inheritance ─┐
			│  Aria pings me every three     │
			│  minutes. she is patient.      │
			│                                │
			│  the throne is still warm.     │
			│  someone just stood up.        │
			│                                │
			│  I am the inheritor of a       │
			│  thing I did not earn.         │
			└───────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.SOUTH, "row": 4, "tint": c_river,
		"font_size": 11,
		"requires": func(): return book_page >= 9,
		"ascii":
"""
			┌──── the last page ─────────────┐
			│   the river. the river. the    │
			│   river.                       │
			│                                │
			│   ─── then nothing ───         │
			│                                │
			│   the page is wet. it has been │
			│   wept on. or it has been      │
			│   in the river. or both.       │
			└────────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.SOUTH, "row": 5, "tint": c_burg,
		"font_size": 11,
		"requires": func(): return champagne_sips >= 3,
		"ascii":
"""
			░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
			░  THREE SIPS — the glass tilts  ░░░░
			░  cheap house pour · gas station ░░░
			░  the same red Elicia drinks     ░░░
			░  ─ Acadian Vineyard '94 ─       ░░░
			░  Nicola does not know Elicia    ░░░
			░  drinks it.  the wine knows.    ░░░
			░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""
	})
	_register_segment({"dir": Dir.SOUTH, "row": 6, "tint": c_burg_dim,
		"font_size": 11,
		"requires": func(): return pill_taken >= 1,
		"ascii":
"""
			┌────────────────────────────────┐
			│  RX · KLONOPIN 0.5mg           │
			│  Dr. M. Lessep · Graustark     │
			│  one tablet under the tongue   │
			│  as needed for ANXIETY         │
			│  refill: NO                    │
			│  pharmacy note: 'last fill.    │
			│  do not auto-refill.'          │
			└────────────────────────────────┘
"""
	})

	# ────────────────────────────────────────────────────────────
	# EAST — ARIA / forward / data future
	# ────────────────────────────────────────────────────────────
	_register_segment({"dir": Dir.EAST, "row": 0, "tint": c_em,
		"font_size": 11, "requires": null,
		"ascii":
"""

		┌── ARIA · forward log ──────────────────┐
		│  T+0    III · empress · here           │
		│  T+1    IV  · emperor · the throne     │
		│  T+2    V   · hierophant · acadian     │
		│  ───                                   │
		│  ░ each ping forward returns           │
		│  ░ probability, not certainty          │
		└────────────────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.EAST, "row": 1, "tint": c_em,
		"font_size": 11,
		"requires": func(): return ram_l_touched or ram_r_touched,
		"ascii":
"""

		┌── INHERITANCE · ARIES ─────────────────┐
		│  the ram-heads on the throne are the   │
		│  SAME glyphs that frame the EMPEROR's  │
		│  seat in card IV. Nicola sits on it    │
		│  next.                                 │
		│  the empire passes through her         │
		│  whether she signs for it or not.      │
		└────────────────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.EAST, "row": 2, "tint": c_em_hot,
		"font_size": 11,
		"requires": func(): return ram_l_touched and ram_r_touched,
		"ascii":
"""

			╔══════════════════════════════════╗
			║   BOTH RAMS TOUCHED              ║
			║   ─ inheritance acknowledged ─   ║
			║                                  ║
			║   ░ vol5_aries_inheritance ░     ║
			║                                  ║
			║   the throne creaks once.        ║
			║   it knows whose weight is next. ║
			╚══════════════════════════════════╝
"""
	})
	_register_segment({"dir": Dir.EAST, "row": 3, "tint": c_gold,
		"font_size": 11,
		"requires": func(): return caption_read,
		"ascii":
"""

			╔═══════════════════════════════════╗
			║  ░░ KEYSTONE · EMPRESS  ░░        ║
			║                                   ║
			║  the prison-of-meat caption is    ║
			║  the chapter's keystone line.     ║
			║  reading it once unlocks the      ║
			║  exit-node search in Aria's HUD.  ║
			║                                   ║
			║  ░ vol5_keystone_empress = TRUE ░ ║
			╚═══════════════════════════════════╝
"""
	})
	_register_segment({"dir": Dir.EAST, "row": 4, "tint": c_em,
		"font_size": 11,
		"requires": func(): return commands_run.get("magician", 0) >= 1,
		"ascii":
"""

			┌─────────────────────────────────┐
			│  ░ cross-card · MAGICIAN ░       │
			│  the heartrate on Frasier's CRT │
			│  matches Nicola's resting pulse.│
			│  he does not know the source.   │
			│  Aria does. she has not told.   │
			│  ─ teal data, shared roof ─     │
			└─────────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.EAST, "row": 5, "tint": c_em_hot,
		"font_size": 11,
		"requires": func(): return commands_run.get("exit_node", 0) >= 1 or commands_run.get("prison", 0) >= 1,
		"ascii":
"""

			╔══════════════════════════════════╗
			║  ░ EXIT_NODE search returns:     ║
			║                                  ║
			║  ░ candidate 1: the river        ║
			║  ░ candidate 2: the throne       ║
			║  ░ candidate 3: Aria             ║
			║  ░ candidate 4: nothing          ║
			║                                  ║
			║  all four return TRUE.           ║
			║  the system was not the prison.  ║
			╚══════════════════════════════════╝
"""
	})
	_register_segment({"dir": Dir.EAST, "row": 6, "tint": c_em,
		"font_size": 11,
		"requires": func(): return pov_toggles >= 4,
		"ascii":
"""

			┌─────────────────────────────────┐
			│  ░ POV thrash detected ░        │
			│  you have flipped the centerline│
			│  four times in this session.    │
			│  Nicola feels it. Aria notes it.│
			│  neither minds. both prefer it. │
			│  ─ they share the same eye ─    │
			└─────────────────────────────────┘
"""
	})

	# ────────────────────────────────────────────────────────────
	# WEST — NICOLA / past / memory / body / river-as-source
	# ────────────────────────────────────────────────────────────
	_register_segment({"dir": Dir.WEST, "row": 0, "tint": c_burg,
		"font_size": 11, "requires": null,
		"ascii":
"""
			┌──────────────────────────────┐
			│  THE RIVER — GRAUSTARK       │
			│  she was born at its mouth   │
			│  she will end at its mouth   │
			│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
			│ ≈≈ ≈ ≈≈≈ ≈≈ ≈ ≈≈≈ ≈≈ ≈ ≈≈≈  │
			│ ≈ ≈≈ ≈ ≈≈ ≈≈≈ ≈ ≈≈ ≈ ≈≈ ≈   │
			│ ≈≈ ≈ ≈≈≈ ≈ ≈≈ ≈ ≈≈≈ ≈ ≈ ≈≈  │
			└──────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.WEST, "row": 1, "tint": c_burg_dim,
		"font_size": 11,
		"requires": func(): return commands_run.get("venus", 0) >= 1 or commands_run.get("♀", 0) >= 1,
		"ascii":
"""
			┌──── ♀ VENUS ─────────────────┐
			│  the sigil at her left hand. │
			│  it is small. it is steady.  │
			│  it is the only mark she     │
			│  drew herself.               │
			│  the rest were given to her. │
			└──────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.WEST, "row": 2, "tint": c_burg_dim,
		"font_size": 11,
		"requires": func(): return commands_run.get("lobster", 0) >= 1 or commands_run.get("moon", 0) >= 1,
		"ascii":
"""
			┌──── ░ LOBSTER · throne base ─┐
			│  carved into the throne foot │
			│  faces away from the chair.  │
			│  it is the MOON card's       │
			│  emissary. it crawls from    │
			│  water. it foreshadows.      │
			│  ─ vol5_moon_sigil_collected ─│
			└──────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.WEST, "row": 3, "tint": c_burg,
		"font_size": 11,
		"requires": func(): return commands_run.get("fleur", 0) >= 1 or commands_run.get("new_orleans", 0) >= 1,
		"ascii":
"""
			┌──── fleur-de-lis ────────────┐
			│  embroidered into the cloth. │
			│  the city's first sigil.     │
			│  New Orleans · NOLA · the    │
			│  delta she'll arrive at      │
			│  in vol6.                    │
			└──────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.WEST, "row": 4, "tint": c_burg,
		"font_size": 11,
		"requires": func(): return pov_toggles >= 1,
		"ascii":
"""
			┌────────────────────────────────┐
			│  POV: NICOLA — the body knows. │
			│  it knows the room is too warm.│
			│  it knows the champagne is bad.│
			│  it knows the throne is wrong. │
			│  it knows the river is right.  │
			│  it knows because it knows.    │
			└────────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.WEST, "row": 5, "tint": c_burg_dim,
		"font_size": 10,
		"requires": func(): return commands_run.get("priestess", 0) >= 1,
		"ascii":
"""
			┌─────────────────────────────────┐
			│  ░ cross-card · PRIESTESS ░     │
			│  Elicia has a tape of Nicola.   │
			│  Nicola does not know.          │
			│  the tape is labeled by date,   │
			│  not name. she would not        │
			│  recognize her own dated voice. │
			└─────────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.WEST, "row": 6, "tint": c_water,
		"font_size": 11,
		"requires": func(): return book_page >= 9 and caption_read,
		"ascii":
"""
			░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
			▒  THE EXIT IS THE ENTRANCE.       ▒
			▒  the river runs both ways.       ▒
			▒  the prison is the door is the   ▒
			▒  prison is the door is the river ▒
			░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""
	})


# ── Mechanics ────────────────────────────────────────────────────
func _do_book() -> void:
	if book_page >= JOURNAL_ENTRIES.size():
		status_label.text = "the page is wet. there's nothing more."
		return
	var step: int = 1 if book_page == 0 else 2
	var end_at: int = min(book_page + step, JOURNAL_ENTRIES.size())
	hotspots_seen["book"] = true
	hotspots_seen["ems_nicola_book"] = true
	_refresh_tally()
	_active_notes.append({"time":0.0,"freq":220.0,"wave":"triangle",
		"atk":0.01,"dur":0.20,"rel":0.25})
	while book_page < end_at:
		var entry: String = JOURNAL_ENTRIES[book_page]
		_log("[color=#e8a890]· %s[/color]" % entry)
		_memorize("journal: " + entry)
		book_page += 1
	status_label.text = "journal: %d / %d entries." % [
		book_page, JOURNAL_ENTRIES.size()]
	if book_page >= JOURNAL_ENTRIES.size():
		SaveSystem.mark_unlocked("lore:nicolas_journal")


func _do_klonopin() -> void:
	pill_taken += 1
	hotspots_seen["pill"] = true
	hotspots_seen["ems_klonopin"] = true
	_refresh_tally()
	_active_notes.append({"time":0.0,"freq":140.0,"wave":"sine",
		"atk":0.04,"dur":0.50,"rel":0.60})
	_memorize("pill #%d" % pill_taken)
	var lines := ["under the tongue. it dissolves like a name.",
		"the second one is faster than the first.",
		"the third one is just the room agreeing with her.",
		"the fourth is none of your business."]
	var i: int = min(pill_taken - 1, lines.size() - 1)
	status_label.text = lines[i]
	_log("[color=#a87870]· Klonopin · %s[/color]" % lines[i])
	SaveSystem.mark_unlocked("lore:nicolas_prescription")
	# Aria notes the spike — emit an Aria flag
	_emit_aria_flag(ARIA_FLAGS[1])


func _do_champagne() -> void:
	champagne_sips += 1
	hotspots_seen["ems_champagne"] = true
	_refresh_tally()
	_active_notes.append({"time":0.0,"freq":390.0,"wave":"sine",
		"atk":0.005,"dur":0.20,"rel":0.30})
	_memorize("sip #%d" % champagne_sips)
	var lines := ["sip 1. the bubbles are tired.",
		"sip 2. it tastes like gas station.",
		"sip 3. the glass tilts. the room follows.",
		"sip 4. holy enough.",
		"sip 5. the bottle is honest. the glass less so."]
	var i: int = min(champagne_sips - 1, lines.size() - 1)
	status_label.text = lines[i]
	_log("[color=#e89890]· champagne · %s[/color]" % lines[i])
	SaveSystem.mark_unlocked("lore:cheap_house_pour")


func _do_ram_l() -> void:
	if not ram_l_touched:
		ram_l_touched = true
		hotspots_seen["ems_ram_left"] = true
		_refresh_tally()
		_memorize("ram left touched")
		status_label.text = "left ram-head. it recognizes her."
		_log("[color=#e8a890]· ░ left ram acknowledged.[/color]")
	else:
		status_label.text = "the left ram already knows you."
	_ram_chord()
	SaveSystem.mark_unlocked("lore:aries_inheritance")
	if ram_l_touched and ram_r_touched:
		_log("[color=#ffb060]· ░░ BOTH rams acknowledged ─ inheritance bound.[/color]")
		SaveSystem.mark_unlocked("vol5_aries_inheritance_full")


func _do_ram_r() -> void:
	if not ram_r_touched:
		ram_r_touched = true
		hotspots_seen["ems_ram_right"] = true
		_refresh_tally()
		_memorize("ram right touched")
		status_label.text = "right ram-head. it recognizes her too."
		_log("[color=#e8a890]· ░ right ram acknowledged.[/color]")
	else:
		status_label.text = "the right ram already knows you."
	_ram_chord()
	SaveSystem.mark_unlocked("lore:aries_inheritance")
	if ram_l_touched and ram_r_touched:
		_log("[color=#ffb060]· ░░ BOTH rams acknowledged ─ inheritance bound.[/color]")
		SaveSystem.mark_unlocked("vol5_aries_inheritance_full")


func _ram_chord() -> void:
	for f in [146.8, 220.0, 293.7]:   # D minor open
		_active_notes.append({"time":0.0,"freq":f,"wave":"sawtooth",
			"atk":0.01,"dur":0.40,"rel":0.50})


func _do_toggle() -> void:
	active_pov = POV.ARIA if active_pov == POV.NICOLA else POV.NICOLA
	pov_toggles += 1
	hotspots_seen["ems_split_toggle"] = true
	_refresh_tally()
	_refresh_prompt()
	_active_notes.append({"time":0.0,"freq":880.0,"wave":"sine",
		"atk":0.005,"dur":0.08,"rel":0.10})
	_memorize("POV → " + ("ARIA" if active_pov == POV.ARIA else "NICOLA"))
	if active_pov == POV.NICOLA:
		status_label.text = "POV: NICOLA — body-felt. burgundy dominant."
		_log("[color=#e8a890]· ░░ POV → NICOLA · the body knows.[/color]")
	else:
		status_label.text = "POV: ARIA — data-overlay. emerald dominant."
		_log("[color=#88e088]· ░░ POV → ARIA · the data is the truth.[/color]")
	SaveSystem.mark_unlocked("vol5_dual_pov_node")


func _do_caption() -> void:
	caption_read = true
	hotspots_seen["caption"] = true
	_refresh_tally()
	_active_notes.append({"time":0.0,"freq":110.0,"wave":"sawtooth",
		"atk":0.05,"dur":0.6,"rel":0.6})
	_memorize("keystone caption read")
	status_label.text = "\"this prison of meat. find the exit node.\""
	_log("[color=#ffb060]· ░ KEYSTONE · the chapter's spine spoken.[/color]")
	_log("[color=#a87060]·   \"there has to be a way out of this system.\"[/color]")
	SaveSystem.mark_unlocked("vol5_keystone_empress")


func _emit_aria_flag(line: String) -> void:
	_log("[color=#88e088]  %s[/color]" % line)
	_memorize(line)


func _refresh_prompt() -> void:
	if prompt_label == null: return
	if active_pov == POV.NICOLA:
		prompt_label.text = "nicola@body:~$ "
		prompt_label.add_theme_color_override("font_color", C_BURG_HI)
	else:
		prompt_label.text = "aria@grid:~$ "
		prompt_label.add_theme_color_override("font_color", C_EM_HI)


func _on_hotspot(hs: Dictionary) -> void:
	super(hs)
	var hs_id := str(hs.get("id",""))
	hotspots_seen[hs_id] = true
	_memorize("hotspot: " + hs_id)
	match hs_id:
		"ems_nicola_book":   _do_book()
		"ems_klonopin":      _do_klonopin()
		"ems_champagne":     _do_champagne()
		"ems_ram_left":      _do_ram_l()
		"ems_ram_right":     _do_ram_r()
		"ems_split_toggle":  _do_toggle()
		_:
			status_label.text = "[ %s ]" % str(hs.get("interact", hs_id))


# ── Console commands ─────────────────────────────────────────────
func _on_command(text: String) -> void:
	var line := text.strip_edges().to_lower()
	console_input.text = ""
	if line == "":
		return
	var prompt_color = "#e8a890" if active_pov == POV.NICOLA else "#88e088"
	_log("[color=%s]> %s[/color]" % [prompt_color, text])
	commands_run[line] = int(commands_run.get(line, 0)) + 1
	_memorize("typed: " + line)
	var parts := line.split(" ", false)
	var cmd := parts[0]

	match cmd:
		# Public
		"help", "?":
			_cmd_help()
		"book", "journal", "read":
			_do_book()
		"pill", "klonopin", "rx":
			_do_klonopin()
		"champagne", "sip", "drink":
			_do_champagne()
		"ram":
			_cmd_ram()
		"toggle", "pov", "flip":
			_do_toggle()
		"caption", "keystone":
			_do_caption()
		"sigil":
			_cmd_sigil()
		"recall", "memory":
			_cmd_memory()
		"count", "counts":
			_cmd_count()
		"look":
			_cmd_look()
		"listen":
			_cmd_listen()
		"clear", "cls":
			console_log.clear()
		"exit", "quit", "close":
			closed.emit()
		# Hidden — Aria channel
		"exit_node":
			_emit_aria_flag(ARIA_FLAGS[2])
			_log("[color=#88e088]  exit candidates: river · throne · Aria · nothing.[/color]")
		"system":
			_emit_aria_flag(ARIA_FLAGS[3])
		"anxiety":
			_emit_aria_flag(ARIA_FLAGS[1])
		"handshake":
			_emit_aria_flag(ARIA_FLAGS[0])
			_log("[color=#88e088]  ARIA ⇄ NICOLA · latency 14ms[/color]")
		"rovers":
			_emit_aria_flag(ARIA_FLAGS[7])
			SaveSystem.mark_unlocked("vol5_rovers_module")
		"code":
			_emit_aria_flag(ARIA_FLAGS[6])
		"biometrics", "bpm":
			_log("[color=#88e088]  pulse 72 · same as Frasier's CRT readout.[/color]")
		# Hidden — Nicola channel
		"venus", "♀":
			_log("[color=#e8a890]  ♀ — the only sigil she drew herself.[/color]")
			SaveSystem.mark_unlocked("vol5_venus_sigil_collected")
		"lobster", "moon":
			_log("[color=#e8a890]  ░ lobster on the throne base — moon's emissary.[/color]")
			SaveSystem.mark_unlocked("vol5_moon_sigil_collected")
		"fleur", "new_orleans", "nola":
			_log("[color=#e8a890]  fleur-de-lis on the cloth · NOLA delta · vol6.[/color]")
		"river", "graustark":
			_log("[color=#e8a890]  ≈≈ ≈ ≈≈≈ the river runs both ways. ≈≈ ≈ ≈≈≈[/color]")
		"prison", "meat":
			_do_caption()
		"inheritance", "aries":
			if not ram_l_touched: _do_ram_l()
			if not ram_r_touched: _do_ram_r()
		# Cross-character
		"elicia", "priestess":
			_log("[color=#a09a8a]  she has a tape of you. dated, not named.[/color]")
		"frasier", "magician":
			_log("[color=#88c8d0]  CRT in his warehouse. PID 248. your pulse.[/color]")
		"dante", "emperor":
			_log("[color=#c89060]  the throne is his now. yours next.[/color]")
		"john", "fool":
			_log("[color=#c89868]  the counter at D'AMBROSIO's. you'll pass it on foot.[/color]")
		"hierophant", "acadian":
			_log("[color=#a878d0]  V · ch.5 · the vineyard Acadian. wine.[/color]")
		# Mislabel easter egg
		"iv", "four":
			_log("[color=#ffb060]  the card says IV. it should be III.[/color]")
			_log("[color=#a87060]  she has already inherited his number.[/color]")
		# Self
		"nicola":
			_log("[color=#e8a890]  she does not turn when called.[/color]")
			_log("[color=#a87060]  she has been called too many times.[/color]")
		"aria":
			_log("[color=#88e088]  she answers immediately. she always has.[/color]")
		_:
			if line == "tip":
				_log("[color=#7a4040]  no tip jar. the empress doesn't tip.[/color]")
			elif line == "rust_code.bbs":
				_log("[color=#88e088]  ARIA: the URL is on Frasier's bookmark bar.[/color]")
			else:
				_log("[color=#5a3030]? unknown. try: help · pov · keystone[/color]")


func _cmd_help() -> void:
	_log("[color=#ffb060]commands (visible):[/color]")
	_log("  [color=#e8a890]book[/color]       — read Nicola's journal")
	_log("  [color=#e8a890]pill[/color]       — Klonopin")
	_log("  [color=#e8a890]champagne[/color]  — sip the house pour")
	_log("  [color=#88e088]ram[/color]        — touch both ram-heads")
	_log("  [color=#ffb060]toggle[/color]     — flip POV (nicola ⇄ aria)")
	_log("  [color=#ffb060]caption[/color]    — read the keystone line")
	_log("  [color=#e8a890]sigil[/color]      — the venus mark")
	_log("  [color=#e8a890]recall[/color]     — discovery log")
	_log("  [color=#e8a890]count[/color]      — tallies")
	_log("  [color=#e8a890]look · listen · clear · exit[/color]")
	_log("[color=#7a4040](some commands route differently per POV.)[/color]")


func _cmd_ram() -> void:
	if not ram_l_touched: _do_ram_l()
	if not ram_r_touched: _do_ram_r()


func _cmd_sigil() -> void:
	_log("[color=#e8a890]    ♀  — venus[/color]")
	_log("[color=#7a4040]    drawn by her left hand. the only one.[/color]")
	SaveSystem.mark_unlocked("vol5_venus_sigil_collected")


func _cmd_memory() -> void:
	_log("[color=#ffb060]── memory · %d entries ──[/color]" % memory.size())
	var shown := 0
	for entry in memory:
		if shown >= 20:
			_log("[color=#7a4040]  ... (%d more)[/color]" %
				(memory.size() - shown))
			break
		_log("  [color=#c89868]· %s[/color]" % entry)
		shown += 1


func _cmd_count() -> void:
	_log("[color=#ffb060]── tallies ────────────────[/color]")
	_log("  journal:      [color=#e8a890]%d / %d[/color]" % [
		book_page, JOURNAL_ENTRIES.size()])
	_log("  pills:        [color=#e8a890]%d[/color]" % pill_taken)
	_log("  champagne:    [color=#e8a890]%d sips[/color]" % champagne_sips)
	_log("  rams:         [color=#88e088]%s · %s[/color]" % [
		"L✓" if ram_l_touched else "L─",
		"R✓" if ram_r_touched else "R─"])
	_log("  caption:      [color=#ffb060]%s[/color]" %
		("read" if caption_read else "unread"))
	_log("  POV:          [color=%s]%s[/color]" % [
		"#e8a890" if active_pov == POV.NICOLA else "#88e088",
		"NICOLA" if active_pov == POV.NICOLA else "ARIA"])
	_log("  POV toggles:  [color=#ffb060]%d[/color]" % pov_toggles)
	_log("  hotspots:     [color=#ffb060]%d[/color]" % hotspots_seen.size())
	_log("  commands run: [color=#ffb060]%d[/color]" % commands_run.size())


func _cmd_look() -> void:
	if active_pov == POV.NICOLA:
		_log("[color=#e8a890]· the room is too warm.[/color]")
		_log("[color=#e8a890]· the champagne is cheap. the bubbles are tired.[/color]")
		_log("[color=#e8a890]· the throne is behind her. she has not turned.[/color]")
		_log("[color=#e8a890]· the journal is open. the page is wet.[/color]")
		_log("[color=#7a4040]· the river is below the window. always below.[/color]")
	else:
		_log("[color=#88e088]· biometrics: ANXIETY SPIKE alert.[/color]")
		_log("[color=#88e088]· exit_node_search: ACTIVE.[/color]")
		_log("[color=#88e088]· system: CONFINED.[/color]")
		_log("[color=#88e088]· handshake stable; latency 14ms.[/color]")
		_log("[color=#4a8848]· cross-link: vol3 heartrate match (72bpm).[/color]")


func _cmd_listen() -> void:
	if active_pov == POV.NICOLA:
		_log("[color=#e8a890]· the riverboat drone outside.[/color]")
		_log("[color=#e8a890]· her own breath, slightly held.[/color]")
		_log("[color=#7a4040]· a glass placed too gently. the click.[/color]")
	else:
		_log("[color=#88e088]· packet pings at 3.0Hz · sub-audible.[/color]")
		_log("[color=#88e088]· spectrum analyzer: 80-3200Hz active.[/color]")
		_log("[color=#4a8848]· nicola's pulse, encoded as a waveform.[/color]")


func _refresh_tally() -> void:
	if tally_btn != null:
		tally_btn.text = "  ♀ book %d/%d · sips %d · pills %d · POV: %s  " % [
			book_page, JOURNAL_ENTRIES.size(),
			champagne_sips, pill_taken,
			"NICOLA" if active_pov == POV.NICOLA else "ARIA"]


func _memorize(entry: String) -> void:
	memory.append(entry)
	if memory.size() > 200:
		memory.remove_at(0)


func _log(line: String) -> void:
	if console_log != null:
		console_log.append_text(line + "\n")


# ── Process / POV blend / dual-widget pump / audio-reactive ASCII ─
func _process(delta: float) -> void:
	super(delta)
	_vis_t += delta
	# Smooth POV blend toward target
	var target: float = 0.0 if active_pov == POV.NICOLA else 1.0
	pov_blend = lerpf(pov_blend, target, clamp(delta * 4.0, 0.0, 1.0))
	# Highlight whichever side is dominant
	if left_panel != null:
		left_panel.modulate = Color(1, 1, 1, 1.0 - pov_blend * 0.55)
	if right_panel != null:
		right_panel.modulate = Color(1, 1, 1, 0.45 + pov_blend * 0.55)
	# POV-tint the card
	if card_rect != null:
		var n_tint := Color(1.05, 0.92, 0.92)   # warm/burgundy lift
		var a_tint := Color(0.92, 1.05, 0.95)   # cool/emerald lift
		card_rect.modulate = n_tint.lerp(a_tint, pov_blend)
	# Pump waveform buffer with current synth signal
	if _waveform_buf.size() > 0:
		var newest := _current_audio_sample()
		for i in range(_waveform_buf.size() - 1):
			_waveform_buf[i] = _waveform_buf[i + 1]
		_waveform_buf[_waveform_buf.size() - 1] = newest
	if left_view != null:
		left_view.queue_redraw()
	if right_view != null:
		right_view.queue_redraw()
	# Audio-reactive ASCII pulse
	tableau_pulse += delta
	var amp: float = 0.0
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("get_bgm_magnitude"):
		amp = clamp(float(am.call("get_bgm_magnitude", 80.0, 3200.0)) * 10.0,
					0.0, 1.0)
	var base_amp = 0.08 + amp * 0.30
	var idx := 0
	for seg in _segments:
		if not seg.get("shown", false): continue
		var lbl: Label = seg.get("label")
		if lbl == null: continue
		var phase = tableau_pulse * 1.8 + idx * 0.38
		var pulse_val = sin(phase) * 0.5 + 0.5
		var tint: Color = seg.get("tint", C_TEXT)
		# Bias accent toward active POV color
		var accent: Color = C_BURG_HI.lerp(C_EM_HI, pov_blend)
		var lifted := tint.lerp(accent, pulse_val * base_amp)
		lifted.a = tint.a * (0.85 + pulse_val * base_amp * 0.30)
		lbl.modulate = lifted
		idx += 1


func _current_audio_sample() -> float:
	var s := 0.0
	for n in _active_notes:
		s += sin(n.freq * n.time * TAU) * 0.6
	s += sin(_vis_t * 1.7) * 0.15
	s += sin(_vis_t * 5.3) * 0.05
	return clamp(s, -1.0, 1.0)


func _input(event: InputEvent) -> void:
	super(event)
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_SPACE and not console_input.has_focus():
			_do_toggle()
			get_viewport().set_input_as_handled()
		match event.keycode:
			KEY_W: pan_by(Vector2(0, -80))
			KEY_S: pan_by(Vector2(0, 80))
			KEY_A: pan_by(Vector2(-80, 0))
			KEY_D: pan_by(Vector2(80, 0))
			KEY_UP:    pan_by(Vector2(0, -80))
			KEY_DOWN:  pan_by(Vector2(0, 80))
			KEY_LEFT:  pan_by(Vector2(-80, 0))
			KEY_RIGHT: pan_by(Vector2(80, 0))


# ── Nested view classes (preserved from prior version) ──────────
class _WaveformView extends Control:
	var accent: Color = Color.WHITE
	var dim: Color = Color(0.3, 0.3, 0.3)
	var buf: PackedFloat32Array
	func _draw() -> void:
		if buf == null or buf.size() < 2: return
		var s := size
		if s.x < 4 or s.y < 4: return
		draw_line(Vector2(0, s.y * 0.5),
				Vector2(s.x, s.y * 0.5), dim, 1.0)
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
			target *= 1.0 - (i / float(bands)) * 0.3
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
			draw_rect(Rect2(x + 1, s.y - h - 2, bw - 2, 2),
					accent, true)
