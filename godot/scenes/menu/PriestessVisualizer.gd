extends "res://scenes/menu/TarotVisualizerBase.gd"
## PriestessVisualizer — Exit Through the Gift Shop.
##
## Elicia in her halftone B&W study. The ONLY card in the deck
## rendered in monochrome — marking her as observer/archivist
## rather than actor. Her tableau reads like an archive: notes,
## tape labels, transcripts, journal annotations.
##
##   • CARD HOTSPOTS — seven rects on the painted Priestess card:
##       TAPES    the Anya VHS stack (upper shelf)
##       JOURNAL  PERSONAL TAROT SYMBOLOGY NOTES on the desk
##       MONITOR  the editing software waveform (left)
##       CAMERA   the camera (upper-mid)
##       COMPASS  the NARRATIVE STRUCTURE COMPASS badge (lower-right)
##       LANTERN  the lantern (upper-center)
##       WINE     the wine bottle (lower-mid, "gas station red")
##
##   • BBS CONSOLE — archive query prompt `archive:~$`. Public:
##       help · tapes · journal · monitor · camera · compass ·
##       lantern · wine · recall · count · look · listen · clear.
##     Hidden: anya · pomegranate · veil · ascendant · structure ·
##       record · transcript · swamp · graustark · moon · elicia ·
##       frasier · dante · nicola · john · 47 · 248 · observe ·
##       witness · silent · vellum.
##
##   • META — the COMPASS badge is the most explicit fourth-wall
##     hook in the deck. Touching it unlocks the structure-overlay.

# ── Game state ───────────────────────────────────────────────────
var tapes_revealed: int = 0    # 0..4 Anya tape labels
var journal_page: int = 0      # 0..N tarot annotations read
var monitor_clip: int = 0      # which clip is loaded
var monitor_pulls: int = 0
var camera_shots: int = 0
var compass_touched: bool = false
var lantern_lit: bool = true
var wine_examined: bool = false
var hotspots_seen: Dictionary = {}
var commands_run: Dictionary = {}
var memory: PackedStringArray = []
var page_pulse: float = 0.0    # subtle paper flicker
var tableau_pulse: float = 0.0

# ── UI refs ──────────────────────────────────────────────────────
var tally_btn: Button
var status_label: Label
var console_input: LineEdit
var console_log: RichTextLabel

# Anya tape inventory revealed progressively
const ANYA_TAPES := [
    "ANYA · 1990.04 · 'first interview'",
    "ANYA · 1991.11 · 'the river footage'",
    "ANYA · 1993.06 · 'silent — audio damaged'",
    "ANYA · 1997.?? · 'the last one she sent'",
]

# Elicia's tarot annotations (revealed by journal hotspot / cmd)
const TAROT_NOTES := [
    "0  THE FOOL — John. Counter-bound. The leap he won't take.",
    "I  THE MAGICIAN — Frasier. He writes what others read.",
    "II THE HIGH PRIESTESS — me. I record what the others write.",
    "III THE EMPRESS — Nicola. The river through the swamp.",
    "IV THE EMPEROR — Dante. Throne of rust and smoke.",
    "V  THE HIEROPHANT — the Acadian. He has not arrived yet.",
    "VI THE LOVERS — uncast. The card stays face-down.",
    "VII THE CHARIOT — the steamboat. Already in the model.",
    "VIII STRENGTH — the dog at D'AMBROSIO'S. Her name is FAITH.",
    "IX THE HERMIT — me, alone. (Different from II. The Priestess",
    "       has visitors. The Hermit doesn't.) ",
    "X  WHEEL OF FORTUNE — the cassette, side B humming.",
    "XI JUSTICE — uncast. I am not the one to draw it.",
    "XII THE HANGED MAN — the bindle on the stick.",
    "XIII DEATH — the COUNTY ROAD sign. The end of the route.",
    "XIV TEMPERANCE — the wine. Gas-station red. Holy enough.",
    "XV THE DEVIL — Frasier's left-hand demon. PID 66.",
    "XVI THE TOWER — Warehouse 47 the night it goes.",
    "XVII THE STAR — Anya. (Forward.)",
    "XVIII THE MOON — between the two pillars: silver and stone.",
    "XIX THE SUN — D'AMBROSIO'S at 6:00 AM. Almost.",
    "XX JUDGEMENT — uncast. The deck refuses.",
    "XXI THE WORLD — the COMPASS badge in my lower-right corner.",
    "                I drew it there. The drawing drew itself.",
]

# Editing-monitor waveform clips Elicia might be reviewing
const MONITOR_CLIPS := [
    "[CLIP_001]  Frasier · 'wakey wakey eggs and bakey'  · 2.1s",
    "[CLIP_002]  John · counter wipe foley · 0.7s loop",
    "[CLIP_003]  Anya · silence (with breath) · 14.2s",
    "[CLIP_004]  Dante · the throne creaks · 1.4s",
    "[CLIP_005]  Nicola · footsteps on cypress board · 8.0s",
    "[CLIP_006]  unknown · the BBS dialup handshake · 11.3s",
    "[CLIP_007]  rain on the warehouse roof · 47.0s loop",
]


func _init() -> void:
    _card_path  = "res://assets/gallery/high_priestess.png"
    _composition_path = "high_priestess_card"
    _hooks_path = "res://resources/puzzle_hooks/high_priestess.json"
    _ambient_audio_path = "res://assets/audio/bgm/vol5_cicadas_dusk.ogg"
    # Halftone B&W palette — the only color in the deck this monochrome
    C_BG = Color(0.060, 0.055, 0.060)
    C_GOLD = Color(0.95, 0.92, 0.85)        # paper cream
    C_GOLD_HI = Color(1.0,  1.0,  0.96)     # pure white
    C_TEXT = Color(0.82, 0.80, 0.74)
    C_TEXT_DIM = Color(0.42, 0.40, 0.36)


func _build_chrome() -> void:
    super()
    _build_bottom_strip()
    _build_card_hotspots()


# Per-region hotspots on the painted Priestess card.
func _build_card_hotspots() -> void:
    if card_rect == null: return
    var defs := [
        ["tapes",   Rect2(0.76, 0.13, 0.14, 0.14), "examine the Anya tapes",       _do_tapes],
        ["journal", Rect2(0.40, 0.78, 0.16, 0.14), "open the symbology notes",     _do_journal],
        ["monitor", Rect2(0.03, 0.38, 0.20, 0.32), "scrub the editing waveform",   _do_monitor],
        ["camera",  Rect2(0.68, 0.26, 0.12, 0.12), "take a snapshot",              _do_camera],
        ["compass", Rect2(0.86, 0.76, 0.12, 0.14), "touch the COMPASS badge",      _do_compass],
        ["lantern", Rect2(0.60, 0.17, 0.10, 0.16), "tend the lantern",             _do_lantern],
        ["wine",    Rect2(0.53, 0.60, 0.07, 0.20), "examine the wine bottle",      _do_wine],
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
        sb.bg_color = Color(1, 1, 0.95, 0.0)
        sb.border_color = Color(1, 1, 0.95, 0.0)
        sb.set_border_width_all(1)
        btn.add_theme_stylebox_override("normal", sb)
        var bsh := sb.duplicate() as StyleBoxFlat
        bsh.bg_color = Color(1, 1, 0.95, 0.18)
        bsh.border_color = Color(1, 1, 0.95, 0.70)
        btn.add_theme_stylebox_override("hover", bsh)
        btn.add_theme_stylebox_override("focus", bsh)
        btn.pressed.connect(d[3])
        canvas.add_child(btn)


func _build_bottom_strip() -> void:
    var bot := PanelContainer.new()
    bot.anchor_left = 0; bot.anchor_right = 1
    bot.anchor_top = 1;  bot.anchor_bottom = 1
    bot.offset_top = -170
    var bps := StyleBoxFlat.new()
    bps.bg_color = Color(0.04, 0.035, 0.04, 0.88)
    bps.border_color = C_GOLD
    bps.border_width_top = 1
    bot.add_theme_stylebox_override("panel", bps)
    add_child(bot)

    var vbox := VBoxContainer.new()
    vbox.add_theme_constant_override("separation", 2)
    bot.add_child(vbox)

    console_log = RichTextLabel.new()
    console_log.bbcode_enabled = true
    console_log.scroll_following = true
    console_log.size_flags_vertical = Control.SIZE_EXPAND_FILL
    console_log.add_theme_font_size_override("normal_font_size", 11)
    console_log.add_theme_color_override("default_color",
        Color(0.82, 0.80, 0.74))
    vbox.add_child(console_log)

    var inrow := HBoxContainer.new()
    inrow.add_theme_constant_override("separation", 4)
    var prompt := Label.new()
    prompt.text = "archive:~$ "
    prompt.add_theme_color_override("font_color", C_GOLD_HI)
    prompt.add_theme_font_size_override("font_size", 12)
    inrow.add_child(prompt)
    console_input = LineEdit.new()
    console_input.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    console_input.add_theme_color_override("font_color",
        Color(0.95, 0.92, 0.85))
    console_input.text_submitted.connect(_on_command)
    inrow.add_child(console_input)
    vbox.add_child(inrow)

    var actrow := HBoxContainer.new()
    actrow.add_theme_constant_override("separation", 12)
    vbox.add_child(actrow)

    tally_btn = Button.new()
    tally_btn.text = "  ░ tapes 0/4 · journal 0/24 · clips 0  "
    tally_btn.add_theme_color_override("font_color", C_GOLD_HI)
    tally_btn.add_theme_font_size_override("font_size", 11)
    var wbs := StyleBoxFlat.new()
    wbs.bg_color = Color(C_GOLD.r * 0.15, C_GOLD.g * 0.15, C_GOLD.b * 0.14, 0.6)
    wbs.border_color = C_GOLD
    wbs.set_border_width_all(1)
    tally_btn.add_theme_stylebox_override("normal", wbs)
    var wbh := wbs.duplicate() as StyleBoxFlat
    wbh.bg_color = Color(C_GOLD.r * 0.35, C_GOLD.g * 0.35, C_GOLD.b * 0.32, 0.75)
    wbh.border_color = C_GOLD_HI
    tally_btn.add_theme_stylebox_override("hover", wbh)
    tally_btn.pressed.connect(_do_tapes)
    tally_btn.tooltip_text = "click card regions for distinct mechanics"
    actrow.add_child(tally_btn)

    status_label = Label.new()
    status_label.text = "click the card · tapes · journal · monitor · camera · compass"
    status_label.add_theme_color_override("font_color",
        Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.80))
    status_label.add_theme_font_size_override("font_size", 10)
    status_label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    status_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    actrow.add_child(status_label)

    _log("[color=#f0eddc]> ARCHIVE / Elicia's study · vol.5 ch.2[/color]")
    _log("[color=#a09a8a]> halftone monochrome. observer mode. recorder running.[/color]")
    _log("[color=#f0eddc]> \"The map was never about finding a destination.[/color]")
    _log("[color=#f0eddc]>  It was about what you became along the way.\"[/color]")
    _log("[color=#a09a8a]> type [color=#ffffff]help[/color] for visible commands. (some are unlisted.)[/color]")

    console_input.grab_focus()


# ── Tableau registration ─────────────────────────────────────────
func _build_thematic_widget() -> void:
    var c_paper := Color(0.92, 0.90, 0.82, 1.0)
    var c_paper_dim := Color(0.55, 0.52, 0.46, 0.9)
    var c_ink := Color(0.96, 0.94, 0.88, 1.0)
    var c_grey := Color(0.70, 0.68, 0.62, 0.9)
    var c_grey_dim := Color(0.40, 0.38, 0.34, 0.85)
    var c_pom := Color(0.78, 0.32, 0.32, 0.95)   # pomegranate red — only color
    var c_meta := Color(0.85, 0.82, 0.74, 1.0)

    # ────────────────────────────────────────────────────────────
    # NORTH — shelves above / Anya tapes / occult titles / pillars
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.NORTH, "row": 0, "tint": c_paper_dim,
        "font_size": 13, "requires": null,
        "ascii":
"""
       ╔═══════════════════════════════════════════════════╗
       ║   II  ░░  THE HIGH PRIESTESS  ░░  ARCHIVE NODE   ║
       ╚═══════════════════════════════════════════════════╝
        ─── between two pillars: silver and stone ─── she sits ───
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 1, "tint": c_paper,
        "font_size": 12,
        "requires": null,
        "ascii":
"""
              ┌─────────────────────────────────────┐
              │  the SHELF                          │
              │  ▓ MYSTERY CULT TEXTS (19th C.)    │
              │  ▓ OCCULT SYMBOLOGY of the          │
              │    ASCENDANT                        │
              │  ▓ FIELD NOTES vol. 1-7             │
              │  ▓ a stack of VHS tapes →           │
              └─────────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 2, "tint": c_paper,
        "font_size": 11,
        "requires": func(): return tapes_revealed >= 1,
        "ascii":
"""
              ╔═══════════════════════════════════════╗
              ║  ▓ ANYA · TAPE 1 — first interview    ║
              ║       date: 1990.04                   ║
              ║       label in her own handwriting    ║
              ║       a name on a shelf is a person   ║
              ║       you have not met yet.           ║
              ╚═══════════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 3, "tint": c_paper,
        "font_size": 11,
        "requires": func(): return tapes_revealed >= 2,
        "ascii":
"""
              ╔═══════════════════════════════════════╗
              ║  ▓ ANYA · TAPE 2 — the river footage  ║
              ║       date: 1991.11                   ║
              ║       she filmed at the cypress dock  ║
              ║       Graustark, before the empire    ║
              ║       was built around her.           ║
              ╚═══════════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 4, "tint": c_grey_dim,
        "font_size": 11,
        "requires": func(): return tapes_revealed >= 3,
        "ascii":
"""
              ╔═══════════════════════════════════════╗
              ║  ▓ ANYA · TAPE 3 — SILENT             ║
              ║       date: 1993.06                   ║
              ║       audio damaged — visual intact   ║
              ║       her mouth moves                 ║
              ║       a transcript may not be possible║
              ║       (we have only her face.)        ║
              ╚═══════════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 5, "tint": c_ink,
        "font_size": 11,
        "requires": func(): return tapes_revealed >= 4,
        "ascii":
"""
              ╔═══════════════════════════════════════╗
              ║  ▓ ANYA · TAPE 4 — the last           ║
              ║       date: 1997.??                   ║
              ║       arrived by mail, no return.     ║
              ║       I have not played it.           ║
              ║       I do not know that I will.      ║
              ║       ─ Elicia ─                      ║
              ╚═══════════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 6, "tint": c_grey,
        "font_size": 11,
        "requires": func(): return commands_run.get("moon", 0) >= 1,
        "ascii":
"""
              ╲                                     ╱
               ╲     ◐  ◑   the pillars frame    ╱
                ╲    the space between them     ╱
                 ╲   ─── B ─── J ───           ╱
                  ╲  silver pillar · stone    ╱
                   ╲ pillar · she's the gap ╱
                    ───  between them.  ───
"""
    })

    # ────────────────────────────────────────────────────────────
    # SOUTH — desk surface / journal / pomegranate / wine
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.SOUTH, "row": 0, "tint": c_paper,
        "font_size": 12, "requires": null,
        "ascii":
"""
       ════════════════ THE DESK ═════════════════════════════
         ░ a journal · a wine bottle · a stack of polaroids ░
         ░ a fountain pen · a closed lacquer box · a key ░░
         ░ the COMPASS badge embossed in the lower-right ░░
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 1, "tint": c_pom,
        "font_size": 12,
        "requires": null,
        "ascii":
"""
                       ▒▒▓▓▓▓▒▒
                     ▒▓▓██████▓▓▒
                    ▓██▓▓▓██▓▓▓▓██▓
                    ██▓▓████████▓▓██   POMEGRANATE
                    ▓██▓▓▓██▓▓▓▓██▓     sigil — closed
                     ▒▓▓██████▓▓▒       leather journal
                       ▒▒▓▓▓▓▒▒          beside the notes
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 2, "tint": c_paper,
        "font_size": 11,
        "requires": func(): return journal_page >= 1,
        "ascii":
"""
              ┌────────────────────────────────────────┐
              │  PERSONAL TAROT SYMBOLOGY NOTES        │
              │  ─── volume i ───                      │
              │                                        │
              │  0  THE FOOL — John. Counter-bound.    │
              │      The leap he won't take.           │
              │                                        │
              │  the others are below the fold.        │
              └────────────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 3, "tint": c_paper,
        "font_size": 10,
        "requires": func(): return journal_page >= 8,
        "ascii":
"""
              ┌────────────────────────────────────────┐
              │  ─── continued ───                     │
              │  I-VIII annotated. her handwriting is  │
              │  small and ruthless.  she has crossed  │
              │  out 'STRENGTH' three times before     │
              │  settling on the dog's name: FAITH.    │
              │  the dog is the symbol. the symbol is  │
              │  the dog. a tautology she likes.       │
              └────────────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 4, "tint": c_ink,
        "font_size": 10,
        "requires": func(): return journal_page >= 22,
        "ascii":
"""
              ┌─────────────────────────────────────────┐
              │  ─── final entries ───                  │
              │  XXI THE WORLD — the COMPASS badge in   │
              │       my lower-right corner.            │
              │       I drew it there.                  │
              │       The drawing drew itself.          │
              │                                         │
              │  she stops writing on the page after.   │
              │  the rest is blank or torn.             │
              └─────────────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 5, "tint": c_pom,
        "font_size": 11,
        "requires": func(): return wine_examined,
        "ascii":
"""
              ╔═════════════════════════════════════╗
              ║   the wine bottle                   ║
              ║   ▒░  GAS STATION RED  ░▒           ║
              ║   ▒░  Acadian Vineyard '94   ░▒     ║
              ║   ▒░  uncorked. half-poured.  ░▒    ║
              ║   ▒░  she drinks it like coffee. ░▒ ║
              ║   ▒░  it is holy enough.    ░▒      ║
              ╚═════════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 6, "tint": c_grey,
        "font_size": 11,
        "requires": func(): return camera_shots >= 3,
        "ascii":
"""
              ┌────────────────────────────────────┐
              │  POLAROIDS · three new ones        │
              │  [▦] the shelf · with tapes        │
              │  [▦] the window · cypress visible  │
              │  [▦] her own hand · on the journal │
              │  she archives herself archiving.   │
              └────────────────────────────────────┘
"""
    })

    # ────────────────────────────────────────────────────────────
    # EAST — through the window / Graustark / forward
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.EAST, "row": 0, "tint": c_grey,
        "font_size": 11, "requires": null,
        "ascii":
"""
              ┌─── window ────────────────┐
              │ ░░▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒░░    │
              │ ▒▓▓ cypress · cypress ▓▓▒ │
              │ ▒▓▓ swamp · spanish   ▓▓▒ │
              │ ▒▓▓ moss · ░ moss    ▓▓▒ │
              │ ▓▓▓▓ rotting boards  ▓▓▓▓ │
              │ ─── GRAUSTARK ──────────  │
              └─────────────────────────── ┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 1, "tint": c_meta,
        "font_size": 11,
        "requires": func(): return compass_touched,
        "ascii":
"""

         ╔════════════════════════════════════════╗
         ║   ░▒▓ NARRATIVE STRUCTURE COMPASS ▓▒░  ║
         ║          (HIGH PRIESTESS Node)         ║
         ╠════════════════════════════════════════╣
         ║      N · upcoming                      ║
         ║      ┐                                 ║
         ║   W ─┼─ E    you are here:             ║
         ║      ┘       II · PRIESTESS · ch.2     ║
         ║      S · past                          ║
         ║                                        ║
         ║   ░ neighboring nodes ░                ║
         ║      N: III EMPRESS (Nicola, ch.3)     ║
         ║      W: I  MAGICIAN (Frasier, ch.1)    ║
         ║      E: V  HIEROPHANT (Acadian, ch.5)  ║
         ║      S: 0  FOOL      (John, ch.0)      ║
         ╚════════════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 2, "tint": c_ink,
        "font_size": 10,
        "requires": func(): return compass_touched,
        "ascii":
"""

         ┌── COMPASS metadata ────────────────────┐
         │  this badge is a fourth-wall element.  │
         │  Elicia drew it on her own card.       │
         │  the card knows it is a card.          │
         │  the player who reads this knows too.  │
         │  ─ the deck reads itself ─             │
         └────────────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 3, "tint": c_paper,
        "font_size": 10,
        "requires": func(): return monitor_pulls >= 1,
        "ascii":
"""

         ┌── EDITING TIMELINE ────────────────────┐
         │ ▓▓░▒░▒▓▓▓▓▒░▒░▒▓▓▒░▒░▒▓▓▒░▒░▒▓▓▓▒░░  │
         │ ░░░ waveform scrubbing                │
         │ ░░░ click MONITOR again to advance    │
         │ ░░░ each clip is real project audio    │
         └────────────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 4, "tint": c_grey,
        "font_size": 11,
        "requires": func(): return monitor_pulls >= 4,
        "ascii":
"""

         ┌── CLIPS REVIEWED ──────────────────────┐
         │  she has scrubbed through at least     │
         │  four. the editing software is open    │
         │  to a session named:                   │
         │  ▓ vol5_ch2_archive.aup3               │
         │  ▓ last saved: 04:11                   │
         │  ▓ unsaved changes: yes.               │
         └────────────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 5, "tint": c_pom,
        "font_size": 11,
        "requires": func(): return commands_run.get("anya", 0) >= 1,
        "ascii":
"""

              ╔══════════════════════════════════╗
              ║   ░ ANYA · forward seeding ░     ║
              ║                                  ║
              ║   she does not appear in prose   ║
              ║   yet. her name appears here.    ║
              ║                                  ║
              ║   the tapes are a promise.       ║
              ║   the tapes are a warning.       ║
              ║   the player who clicks them     ║
              ║   has been told. the player who  ║
              ║   meets her later will recognize.║
              ╚══════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 6, "tint": c_meta,
        "font_size": 11,
        "requires": func(): return hotspots_seen.size() >= 6,
        "ascii":
"""

              ┌─────────────────────────────────┐
              │  ░░ you have touched everything ░│
              │  ░░ on her desk except the      ░│
              │  ░░ lacquer box, which is       ░│
              │  ░░ outside the painted frame.  ░│
              │  ░░ the lacquer box is in vol6. ░│
              │  ░░ Elicia notes this.          ░│
              └─────────────────────────────────┘
"""
    })

    # ────────────────────────────────────────────────────────────
    # WEST — tape transcripts / archive log / past
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.WEST, "row": 0, "tint": c_paper,
        "font_size": 11, "requires": null,
        "ascii":
"""
              ┌──────────────────────────────┐
              │  ARCHIVE LOG                 │
              │  ─── est. 1989 ─── ongoing  │
              │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
              │ ▓ 1989 first cassette        │
              │ ▓ 1991 first interview saved │
              │ ▓ 1993 first silent tape     │
              │ ▓ 1995 archive moves house   │
              │ ▓ 1997 — now —               │
              └──────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 1, "tint": c_paper_dim,
        "font_size": 11,
        "requires": func(): return monitor_pulls >= 1,
        "ascii":
"""
              ┌────────────────────────────────┐
              │  [CLIP_001] Frasier · 2.1s     │
              │  ─── transcript ───            │
              │  "wakey wakey, eggs and bakey. │
              │   reality subroutine glitching"│
              │  ─── flagged ───               │
              │  for cross-ref with magician   │
              │  card. matches his ambient.    │
              └────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 2, "tint": c_paper_dim,
        "font_size": 10,
        "requires": func(): return monitor_pulls >= 3,
        "ascii":
"""
              ┌────────────────────────────────┐
              │  [CLIP_003] Anya · 14.2s       │
              │  ─── transcript ───            │
              │  (silence)                     │
              │  (breath)                      │
              │  (silence)                     │
              │  (breath)                      │
              │  (a name half-said, cut)       │
              │  ─── unfileable ───            │
              └────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 3, "tint": c_grey_dim,
        "font_size": 11,
        "requires": func(): return commands_run.get("transcript", 0) >= 1,
        "ascii":
"""
              ╔═══════════════════════════════════╗
              ║  TRANSCRIPTION ETHIC              ║
              ║  ░ I write what was said.         ║
              ║  ░ I write what was not said.     ║
              ║  ░ I do not write what should     ║
              ║    have been said.                ║
              ║  ░ that is a different ethic.     ║
              ║  ░ that is not my ethic.          ║
              ╚═══════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 4, "tint": c_grey,
        "font_size": 11,
        "requires": func(): return commands_run.get("ascendant", 0) >= 1,
        "ascii":
"""
              ┌─────────────────────────────────┐
              │  ░ OCCULT SYMBOLOGY of the      │
              │    ASCENDANT — opened to p.247  │
              │                                 │
              │  "the ascendant is not a person │
              │   it is the axis where the      │
              │   horizon meets the sign rising │
              │   at the moment of asking."     │
              │                                 │
              │  she has underlined ASKING.     │
              └─────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 5, "tint": c_pom,
        "font_size": 11,
        "requires": func(): return commands_run.get("veil", 0) >= 1,
        "ascii":
"""
              ┌─────────────────────────────────┐
              │  ░ THE VEIL BEHIND HER ░        │
              │  is patterned with pomegranates │
              │  it hides:                      │
              │    ▓ a river                    │
              │    ▓ a door                     │
              │    ▓ a name                     │
              │  she has not lifted it.         │
              │  she does not need to.          │
              └─────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 6, "tint": c_meta,
        "font_size": 10,
        "requires": func(): return lantern_lit == false,
        "ascii":
"""
              ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
              ░░  the lantern is out.            ░░
              ░░  the page is darker.            ░░
              ░░  she works by the monitor's     ░░
              ░░  glow now. the waveform lights  ░░
              ░░  her face cold blue.            ░░
              ░░  (light it again to read on.)   ░░
              ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""
    })


# ── Mechanics ────────────────────────────────────────────────────
func _do_tapes() -> void:
    tapes_revealed = min(tapes_revealed + 1, ANYA_TAPES.size())
    hotspots_seen["pri_anya_tapes_hotspot"] = true
    _refresh_tally()
    _active_notes.append({"time":0.0,"freq":520.0,"wave":"sine",
        "atk":0.02,"dur":0.20,"rel":0.30})
    _memorize("tape #%d revealed" % tapes_revealed)
    var label: String = ANYA_TAPES[tapes_revealed - 1]
    status_label.text = "tape revealed: " + label
    _log("[color=#f0eddc]· %s[/color]" % label)
    if tapes_revealed == 1:
        SaveSystem.mark_unlocked("vol5_anya_introduced")
    if tapes_revealed == ANYA_TAPES.size():
        _log("[color=#a09a8a]· all four Anya tapes catalogued.[/color]")


func _do_journal() -> void:
    if journal_page >= TAROT_NOTES.size():
        status_label.text = "the journal is complete. the rest is blank."
        return
    var page_step: int = 1 if journal_page == 0 else 3
    var end_at: int = min(journal_page + page_step, TAROT_NOTES.size())
    hotspots_seen["pri_journal_hotspot"] = true
    _refresh_tally()
    _active_notes.append({"time":0.0,"freq":260.0,"wave":"triangle",
        "atk":0.01,"dur":0.18,"rel":0.20})
    while journal_page < end_at:
        _log("[color=#e8e2cc]  %s[/color]" % TAROT_NOTES[journal_page])
        _memorize("journal: " + TAROT_NOTES[journal_page])
        journal_page += 1
    status_label.text = "journal: %d / %d entries read." % [
        journal_page, TAROT_NOTES.size()]
    if journal_page >= TAROT_NOTES.size():
        SaveSystem.mark_unlocked("lore:elicia_tarot_journal")


func _do_monitor() -> void:
    monitor_pulls += 1
    monitor_clip = (monitor_clip + 1) % MONITOR_CLIPS.size()
    hotspots_seen["pri_editing_monitor_hotspot"] = true
    _refresh_tally()
    _active_notes.append({"time":0.0,"freq":380.0,"wave":"sawtooth",
        "atk":0.001,"dur":0.10,"rel":0.10})
    _memorize("scrubbed: clip %d" % monitor_clip)
    status_label.text = MONITOR_CLIPS[monitor_clip]
    _log("[color=#c0baa6]· %s[/color]" % MONITOR_CLIPS[monitor_clip])
    SaveSystem.mark_unlocked("vol5_priestess_editing_clip")


func _do_camera() -> void:
    camera_shots += 1
    hotspots_seen["pri_camera_hotspot"] = true
    _refresh_tally()
    # Camera shutter — high snap + low click
    _active_notes.append({"time":0.0,"freq":1800.0,"wave":"square",
        "atk":0.001,"dur":0.02,"rel":0.02})
    _active_notes.append({"time":0.0,"freq":140.0,"wave":"triangle",
        "atk":0.001,"dur":0.06,"rel":0.08})
    _memorize("polaroid #%d" % camera_shots)
    var subjects := ["the shelf", "the window", "her own hand",
        "the journal", "the wine bottle", "the lantern",
        "the COMPASS badge", "the door (out of frame)"]
    var s: String = subjects[(camera_shots - 1) % subjects.size()]
    status_label.text = "polaroid #%d : %s" % [camera_shots, s]
    _log("[color=#f0eddc]· [▦] polaroid #%d — %s[/color]" %
         [camera_shots, s])
    SaveSystem.mark_unlocked("vol5_priestess_camera")


func _do_compass() -> void:
    compass_touched = true
    hotspots_seen["pri_compass_badge_hotspot"] = true
    _refresh_tally()
    # Soft chime — open fifths
    for f in [330.0, 495.0, 660.0]:
        _active_notes.append({"time":0.0,"freq":f,"wave":"sine",
            "atk":0.05,"dur":0.5,"rel":0.6})
    _memorize("COMPASS badge touched (fourth wall opened)")
    status_label.text = "NARRATIVE STRUCTURE COMPASS — node II revealed east."
    _log("[color=#f0eddc]· ░▒▓ COMPASS touched ▓▒░ ─ structure unfolds east.[/color]")
    _log("[color=#a09a8a]· she drew it on her own card. the card knows.[/color]")
    SaveSystem.mark_unlocked("vol5_meta_compass_unlocked")


func _do_lantern() -> void:
    lantern_lit = not lantern_lit
    hotspots_seen["pri_lantern_hotspot"] = true
    _refresh_tally()
    _active_notes.append({"time":0.0,"freq":110.0,"wave":"triangle",
        "atk":0.05,"dur":0.30,"rel":0.40})
    _memorize("lantern " + ("lit" if lantern_lit else "out"))
    if lantern_lit:
        status_label.text = "lantern lit. the page is warm again."
        _log("[color=#f0eddc]· lantern lit. page warm.[/color]")
    else:
        status_label.text = "lantern out. she works by monitor-glow."
        _log("[color=#7a7468]· lantern out. monitor-glow takes over.[/color]")
    SaveSystem.mark_unlocked("vol5_priestess_lantern")


func _do_wine() -> void:
    wine_examined = true
    hotspots_seen["pri_wine_hotspot"] = true
    _refresh_tally()
    _active_notes.append({"time":0.0,"freq":196.0,"wave":"sine",
        "atk":0.03,"dur":0.30,"rel":0.40})
    _memorize("wine examined")
    status_label.text = "GAS STATION RED — Acadian Vineyard '94."
    _log("[color=#c84848]· wine: GAS STATION RED. she drinks it like coffee.[/color]")
    SaveSystem.mark_unlocked("lore:gas_station_red")


func _on_hotspot(hs: Dictionary) -> void:
    super(hs)
    var hs_id := str(hs.get("id",""))
    hotspots_seen[hs_id] = true
    _memorize("hotspot: " + hs_id)
    match hs_id:
        "pri_anya_tapes_hotspot":      _do_tapes()
        "pri_compass_badge_hotspot":   _do_compass()
        "pri_journal_hotspot":         _do_journal()
        "pri_camera_hotspot":          _do_camera()
        "pri_lantern_hotspot":         _do_lantern()
        "pri_wine_hotspot":            _do_wine()
        "pri_editing_monitor_hotspot": _do_monitor()
        _:
            status_label.text = "[ %s ]" % str(hs.get("interact", hs_id))


# ── Console commands ─────────────────────────────────────────────
func _on_command(text: String) -> void:
    var line := text.strip_edges().to_lower()
    console_input.text = ""
    if line == "":
        return
    _log("[color=#f0eddc]> %s[/color]" % text)
    commands_run[line] = int(commands_run.get(line, 0)) + 1
    _memorize("typed: " + line)
    var parts := line.split(" ", false)
    var cmd := parts[0]

    match cmd:
        # Public
        "help", "?":
            _cmd_help()
        "tapes", "anya_tapes":
            _do_tapes()
        "journal", "notes":
            _do_journal()
        "monitor", "scrub":
            _do_monitor()
        "camera", "snap":
            _do_camera()
        "compass", "structure":
            _do_compass()
        "lantern", "light":
            _do_lantern()
        "wine":
            _do_wine()
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
        # Hidden lore
        "anya":
            _cmd_anya()
        "pomegranate":
            _log("[color=#c84848]  ░▒▓ POMEGRANATE — Persephone's seed.[/color]")
            _log("[color=#7a4848]  six seeds. six months below. six months above.[/color]")
        "veil":
            _log("[color=#f0eddc]  the veil is pomegranate-patterned.[/color]")
            _log("[color=#a09a8a]  it hides: a river, a door, a name.[/color]")
        "ascendant":
            _log("[color=#f0eddc]  book p.247 — the ascendant is the axis of asking.[/color]")
        "record", "observe", "witness":
            _log("[color=#f0eddc]  recorder is running. it has always been running.[/color]")
        "transcript":
            _log("[color=#a09a8a]  ethic: I write what was said.[/color]")
            _log("[color=#a09a8a]         I write what was not said.[/color]")
            _log("[color=#7a7468]         I do not write what should have been said.[/color]")
        "swamp", "graustark":
            _log("[color=#a09a8a]  cypress · spanish moss · rotting boards.[/color]")
            _log("[color=#7a7468]  the river is below. always below.[/color]")
        "moon":
            _log("[color=#f0eddc]  between two pillars: silver and stone.[/color]")
            _log("[color=#a09a8a]  she is the gap between them.[/color]")
        "elicia":
            _log("[color=#f0eddc]  she does not answer to her name in the room.[/color]")
            _log("[color=#a09a8a]  she answers to it on tape, later, when she plays it back.[/color]")
        "frasier":
            _log("[color=#a09a8a]  clip_001 is his. she has not deleted it.[/color]")
        "dante":
            _log("[color=#a09a8a]  emperor card. she does not have a tape of him yet.[/color]")
        "nicola":
            _log("[color=#a09a8a]  empress card. ch.3 — Elicia notes the EMS biometric overlap.[/color]")
        "john":
            _log("[color=#a09a8a]  fool card. she has a polaroid of the counter, no John.[/color]")
        "hierophant", "acadian":
            _log("[color=#a09a8a]  ch.5. she has not met him. she has tape of his voice.[/color]")
        "47":
            _log("[color=#a09a8a]  warehouse 47. she rents the room next door.[/color]")
        "248":
            _log("[color=#a09a8a]  PID 248 in Frasier's CRT: nicola.precognition.[/color]")
            _log("[color=#7a7468]  she has noticed this.[/color]")
        "silent":
            _log("[color=#7a7468]  tape 3 is silent. it is the loudest one.[/color]")
        "vellum":
            _log("[color=#a09a8a]  the infinity glyph in her books is bound in vellum.[/color]")
            _log("[color=#7a7468]  same glyph Frasier solders. one reads. one writes.[/color]")
        _:
            if line == "tip":
                _log("[color=#a09a8a]  no tip jar. she's not in service.[/color]")
            elif line == "rust_code.bbs":
                _log("[color=#f0eddc]  she has the URL written in her notes.[/color]")
                _log("[color=#a09a8a]  she has not dialed in. yet.[/color]")
            else:
                _log("[color=#7a7468]? unknown. try: help · memory · anya[/color]")


func _cmd_help() -> void:
    _log("[color=#f0eddc]commands (visible):[/color]")
    _log("  [color=#ffffff]tapes[/color]      — examine the Anya tape stack")
    _log("  [color=#ffffff]journal[/color]    — open the tarot symbology notes")
    _log("  [color=#ffffff]monitor[/color]    — scrub the editing waveform")
    _log("  [color=#ffffff]camera[/color]     — take a polaroid")
    _log("  [color=#ffffff]compass[/color]    — touch the COMPASS badge (meta)")
    _log("  [color=#ffffff]lantern[/color]    — light or extinguish")
    _log("  [color=#ffffff]wine[/color]       — examine the bottle")
    _log("  [color=#ffffff]recall[/color]     — discovery log")
    _log("  [color=#ffffff]count[/color]      — tallies")
    _log("  [color=#ffffff]look[/color]       — examine the study")
    _log("  [color=#ffffff]listen[/color]     — what the cicadas say")
    _log("  [color=#ffffff]clear · exit[/color]")
    _log("[color=#7a7468](some commands are unlisted. she keeps secrets.)[/color]")


func _cmd_anya() -> void:
    _log("[color=#f0eddc]── ANYA · tape inventory ──[/color]")
    if tapes_revealed == 0:
        _log("[color=#7a7468]  no tapes catalogued. click the shelf.[/color]")
        return
    for i in range(tapes_revealed):
        _log("  [color=#e8e2cc]▓ %s[/color]" % ANYA_TAPES[i])
    if tapes_revealed < ANYA_TAPES.size():
        _log("[color=#7a7468]  (%d more on the shelf — keep clicking)[/color]"
             % (ANYA_TAPES.size() - tapes_revealed))


func _cmd_memory() -> void:
    _log("[color=#f0eddc]── archive log · %d entries ──[/color]" % memory.size())
    var shown := 0
    for entry in memory:
        if shown >= 20:
            _log("[color=#7a7468]  ... (%d more)[/color]" %
                 (memory.size() - shown))
            break
        _log("  [color=#c0baa6]· %s[/color]" % entry)
        shown += 1


func _cmd_count() -> void:
    _log("[color=#f0eddc]── tallies ────────────────[/color]")
    _log("  Anya tapes:   [color=#ffffff]%d / %d[/color]" % [
         tapes_revealed, ANYA_TAPES.size()])
    _log("  journal:      [color=#ffffff]%d / %d entries[/color]" % [
         journal_page, TAROT_NOTES.size()])
    _log("  clips scrubbed:[color=#ffffff] %d (current %d)[/color]" % [
         monitor_pulls, monitor_clip])
    _log("  polaroids:    [color=#ffffff]%d[/color]" % camera_shots)
    _log("  compass:      [color=#ffffff]%s[/color]" %
         ("touched" if compass_touched else "untouched"))
    _log("  lantern:      [color=#ffffff]%s[/color]" %
         ("lit" if lantern_lit else "out"))
    _log("  wine:         [color=#ffffff]%s[/color]" %
         ("examined" if wine_examined else "sealed"))
    _log("  hotspots:     [color=#ffffff]%d[/color]" % hotspots_seen.size())
    _log("  commands run: [color=#ffffff]%d[/color]" % commands_run.size())


func _cmd_look() -> void:
    _log("[color=#c0baa6]· halftone room. B&W. cicadas outside.[/color]")
    _log("[color=#c0baa6]· shelf above: books, tapes labeled ANYA.[/color]")
    _log("[color=#c0baa6]· desk: journal, pomegranate sigil, wine, polaroids.[/color]")
    _log("[color=#c0baa6]· left: editing monitor with a waveform.[/color]")
    _log("[color=#c0baa6]· camera in front of her. lantern above.[/color]")
    _log("[color=#7a7468]· window: cypress swamp. Graustark.[/color]")
    _log("[color=#7a7468]· lower right: a circular badge: COMPASS.[/color]")


func _cmd_listen() -> void:
    _log("[color=#c0baa6]· cicadas. dusk-pitched.[/color]")
    _log("[color=#c0baa6]· lantern fuel, hissing.[/color]")
    _log("[color=#c0baa6]· monitor fan, whispering.[/color]")
    _log("[color=#7a7468]· the swamp, swallowing every other sound.[/color]")
    _log("[color=#7a7468]· her own pen scratching. occasionally.[/color]")


func _refresh_tally() -> void:
    if tally_btn != null:
        tally_btn.text = "  ░ tapes %d/%d · journal %d/%d · clips %d  " % [
            tapes_revealed, ANYA_TAPES.size(),
            journal_page, TAROT_NOTES.size(),
            monitor_pulls]


func _memorize(entry: String) -> void:
    memory.append(entry)
    if memory.size() > 200:
        memory.remove_at(0)


func _log(line: String) -> void:
    if console_log != null:
        console_log.append_text(line + "\n")


# ── Process / page-flicker / audio-reactive ASCII pulse ──────────
func _process(delta: float) -> void:
    super(delta)
    page_pulse = fmod(page_pulse + delta * 0.6, TAU)
    # Lantern affects whole-card brightness; subtle paper-flicker on top
    if card_rect != null:
        var lantern_b := 1.0 if lantern_lit else 0.62
        var flicker := 1.0 + sin(page_pulse) * 0.015
        var b := lantern_b * flicker
        card_rect.modulate = Color(b, b, b * 0.985)
    # Audio-reactive ASCII pulse
    tableau_pulse += delta
    var amp: float = 0.0
    var am := get_node_or_null("/root/AudioMgr")
    if am != null and am.has_method("get_bgm_magnitude"):
        amp = clamp(float(am.call("get_bgm_magnitude", 80.0, 3200.0)) * 10.0,
                     0.0, 1.0)
    # Quieter pulse than Magician/Fool — she's contemplative
    var base_amp = 0.06 + amp * 0.25
    var idx := 0
    for seg in _segments:
        if not seg.get("shown", false): continue
        var lbl: Label = seg.get("label")
        if lbl == null: continue
        var phase = tableau_pulse * 1.4 + idx * 0.45
        var pulse_val = sin(phase) * 0.5 + 0.5
        var tint: Color = seg.get("tint", C_TEXT)
        var lifted := tint.lerp(C_GOLD_HI, pulse_val * base_amp)
        lifted.a = tint.a * (0.90 + pulse_val * base_amp * 0.20)
        lbl.modulate = lifted
        idx += 1


func _input(event: InputEvent) -> void:
    super(event)
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_SPACE and not console_input.has_focus():
            _do_journal()
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
