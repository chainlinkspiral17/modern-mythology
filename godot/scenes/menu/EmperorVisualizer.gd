extends "res://scenes/menu/TarotVisualizerBase.gd"
## EmperorVisualizer — sepia monochrome throne.
##
## Dante on the ram-headed throne. Latin motto carved at his feet.
## Two ASCII glyph walls flank him — first-character-per-row spells
## the motto. The floor mirror shows upside-down faces that are not
## quite his — they're the successor.
##
##   • CARD HOTSPOTS — six rects on the painted Emperor card:
##       ANKH      his ankh-sceptre (mid-card)
##       RAM_L     left ram-head (inverted aries glyph)
##       RAM_R     right ram-head (upright aries glyph)
##       GLASS     the bourbon glass (1971)
##       MOTTO     the AVTORITAS POTESTAS IMPERIVM caption
##       MIRROR    the floor reflection — looks back as a stranger
##
##   • BBS CONSOLE — `dante@throne:~$`. Public: ankh / ram / glass /
##     motto / mirror / decode / recall / count / look / listen /
##     clear / exit. Hidden: avtoritas · potestas · imperivm ·
##     bourbon · 1971 · successor · upside_down · aries · horn ·
##     steamboat · empire · smoke · iv · empress · magician ·
##     priestess · fool · hierophant · voltaire · dante · riddle ·
##     inheritance.
##
##   • CROSS-CARD ECHOES — ram-throne pairs with Empress, mirror
##     pairs with Empress dual-POV, steamboat pairs with Magician's
##     model city (Frasier wired it first).

# ── Game state ───────────────────────────────────────────────────
var ankh_touches: int = 0
var ram_l_touched: bool = false
var ram_r_touched: bool = false
var glass_pours: int = 0
var motto_read: bool = false
var mirror_gazes: int = 0     # 0..4 — each gaze reveals more
var wall_l_decoded: bool = false
var wall_r_decoded: bool = false
var hotspots_seen: Dictionary = {}
var commands_run: Dictionary = {}
var memory: PackedStringArray = []
var throne_breath: float = 0.0
var tableau_pulse: float = 0.0

# ── UI refs ──────────────────────────────────────────────────────
var tally_btn: Button
var status_label: Label
var console_input: LineEdit
var console_log: RichTextLabel

# Mirror reveal stages — what the upside-down face shows on each gaze
const MIRROR_STAGES := [
    "the reflection. it is yours. it is not yours.",
    "the eyes are darker. the jaw is softer. the hair is longer.",
    "it is a woman. her hand is on the arm of the throne, not yours.",
    "it is Nicola. she has not arrived. she has already sat there.",
]


func _init() -> void:
    _card_path  = "res://assets/gallery/emperor.png"
    _composition_path = "emperor_card"
    _hooks_path = "res://resources/puzzle_hooks/emperor.json"
    _ambient_audio_path = "res://assets/audio/bgm/vol5_ambient.ogg"
    # Sepia monochrome
    C_BG = Color(0.080, 0.060, 0.040)
    C_GOLD = Color(0.85, 0.65, 0.30)
    C_GOLD_HI = Color(1.0, 0.85, 0.45)
    C_TEXT = Color(0.82, 0.70, 0.50)
    C_TEXT_DIM = Color(0.45, 0.35, 0.22)


func _build_chrome() -> void:
    super()
    _build_bottom_strip()
    _build_card_hotspots()


# Per-region hotspots on the painted Emperor card.
func _build_card_hotspots() -> void:
    if card_rect == null: return
    var defs := [
        ["ankh",   Rect2(0.39, 0.38, 0.08, 0.22), "touch the ankh",         _do_ankh],
        ["ram_l",  Rect2(0.37, 0.20, 0.09, 0.12), "touch the left ram",     _do_ram_l],
        ["ram_r",  Rect2(0.54, 0.20, 0.09, 0.12), "touch the right ram",    _do_ram_r],
        ["glass",  Rect2(0.28, 0.53, 0.08, 0.12), "examine the bourbon",    _do_glass],
        ["motto",  Rect2(0.20, 0.92, 0.60, 0.06), "read the motto",         _do_motto],
        ["mirror", Rect2(0.30, 0.84, 0.40, 0.08), "gaze into the mirror",   _do_mirror],
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
        sb.bg_color = Color(1, 0.80, 0.40, 0.0)
        sb.border_color = Color(1, 0.80, 0.40, 0.0)
        sb.set_border_width_all(1)
        btn.add_theme_stylebox_override("normal", sb)
        var bsh := sb.duplicate() as StyleBoxFlat
        bsh.bg_color = Color(1, 0.80, 0.40, 0.22)
        bsh.border_color = Color(1, 0.92, 0.55, 0.85)
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
    bps.bg_color = Color(0.04, 0.030, 0.020, 0.85)
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
        Color(0.88, 0.74, 0.52))
    vbox.add_child(console_log)

    var inrow := HBoxContainer.new()
    inrow.add_theme_constant_override("separation", 4)
    var prompt := Label.new()
    prompt.text = "dante@throne:~$ "
    prompt.add_theme_color_override("font_color", C_GOLD_HI)
    prompt.add_theme_font_size_override("font_size", 12)
    inrow.add_child(prompt)
    console_input = LineEdit.new()
    console_input.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    console_input.add_theme_color_override("font_color",
        Color(1.0, 0.85, 0.55))
    console_input.text_submitted.connect(_on_command)
    inrow.add_child(console_input)
    vbox.add_child(inrow)

    var actrow := HBoxContainer.new()
    actrow.add_theme_constant_override("separation", 12)
    vbox.add_child(actrow)

    tally_btn = Button.new()
    tally_btn.text = "  ☥ ankh 0 · rams 0/2 · pours 0 · mirror 0/4  "
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
    tally_btn.pressed.connect(_do_ankh)
    tally_btn.tooltip_text = "click card regions for distinct mechanics"
    actrow.add_child(tally_btn)

    status_label = Label.new()
    status_label.text = "click the card · ankh · ram · glass · motto · mirror"
    status_label.add_theme_color_override("font_color",
        Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.80))
    status_label.add_theme_font_size_override("font_size", 10)
    status_label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    status_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    actrow.add_child(status_label)

    _log("[color=#ffb060]> IV · THE EMPEROR · vol.5 ch.4 · throne of rust and smoke[/color]")
    _log("[color=#a87040]> sepia monochrome. motto carved. mirror below.[/color]")
    _log("[color=#ffb060]> AVTORITAS  POTESTAS  IMPERIVM[/color]")
    _log("[color=#a87040]> type [color=#ffd896]help[/color] · the throne accepts no decoration.[/color]")

    console_input.grab_focus()


# ── Tableau registration ─────────────────────────────────────────
func _build_thematic_widget() -> void:
    var c_sepia := Color(0.85, 0.65, 0.30, 0.95)
    var c_sepia_dim := Color(0.45, 0.32, 0.18, 0.85)
    var c_sepia_hot := Color(1.0, 0.85, 0.45, 1.0)
    var c_parch := Color(0.82, 0.70, 0.50, 0.95)
    var c_smoke := Color(0.55, 0.50, 0.45, 0.85)
    var c_blood := Color(0.78, 0.30, 0.22, 0.95)
    var c_rust := Color(0.62, 0.38, 0.22, 0.90)

    # ────────────────────────────────────────────────────────────
    # NORTH — above the throne / authority / sky / motto carved
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.NORTH, "row": 0, "tint": c_sepia_dim,
        "font_size": 13, "requires": null,
        "ascii":
"""
       ╔═══════════════════════════════════════════════════╗
       ║   IV  ░░  THE EMPEROR  ░░  THRONE OF RUST AND    ║
       ║       ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  SMOKE       ║
       ╚═══════════════════════════════════════════════════╝
        ─── as the throne ─── so the man ─── so the empire ───
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 1, "tint": c_sepia,
        "font_size": 12,
        "requires": null,
        "ascii":
"""
              ┌────────────────────────────┐
              │      A V T O R I T A S     │
              │      P O T E S T A S       │
              │      I M P E R I V M       │
              │  ── carved at his feet ──  │
              │  ── carved into his back ──│
              │  ── carved into the air ──│
              └────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 2, "tint": c_sepia_hot,
        "font_size": 12,
        "requires": func(): return motto_read,
        "ascii":
"""
       ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
     ░▒▒▓▓████  KEYSTONE · EMPEROR  ████▓▓▒▒░
       ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
        AVTORITAS — what is given to a man
        POTESTAS  — what he takes for himself
        IMPERIVM  — what survives him.
        ─── all three. the third is the one he fears. ───
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 3, "tint": c_sepia,
        "font_size": 11,
        "requires": func(): return ankh_touches >= 4,
        "ascii":
"""
              ╔══════════════════════════════════╗
              ║       ░  ☥ ANKH  ░               ║
              ║  the ankh is the only soft thing ║
              ║  he holds. life. living thing.   ║
              ║  he holds it like a man holds    ║
              ║  a fish he has not killed yet.   ║
              ╚══════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 4, "tint": c_sepia_hot,
        "font_size": 11,
        "requires": func(): return ram_l_touched and ram_r_touched,
        "ascii":
"""
              ╔══════════════════════════════════╗
              ║   ░ BOTH RAMS BOUND ░            ║
              ║                                  ║
              ║   left horn:  inverted aries    ║
              ║                (the past empire)│
              ║   right horn: upright aries     ║
              ║                (the next empire)│
              ║                                  ║
              ║   the orientation flips between ║
              ║   his lifetime and her arrival. ║
              ╚══════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 5, "tint": c_sepia,
        "font_size": 11,
        "requires": func(): return commands_run.get("empire", 0) >= 1,
        "ascii":
"""
              ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
            ░░  THE EMPIRE — D'AMBROSIO HOLDINGS  ░░
            ░░  ▓ the diner                       ░░
            ░░  ▓ the warehouse strip             ░░
            ░░  ▓ the riverboat                   ░░
            ░░  ▓ County Road 17 (rights-of-way)  ░░
            ░░  ▓ the vineyard (silent partner)   ░░
              ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 6, "tint": c_sepia_hot,
        "font_size": 11,
        "requires": func(): return hotspots_seen.size() >= 6,
        "ascii":
"""
              ╔════════════════════════════════════╗
              ║  ░ EVERY HOTSPOT TOUCHED ░         ║
              ║  the throne records who sat in it. ║
              ║  the throne records who knelt.     ║
              ║  the throne records who stood up   ║
              ║  without permission.               ║
              ║                                    ║
              ║  it is also a chair. mostly.       ║
              ╚════════════════════════════════════╝
"""
    })

    # ────────────────────────────────────────────────────────────
    # SOUTH — below / mirror / successor face / floor
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.SOUTH, "row": 0, "tint": c_smoke,
        "font_size": 12, "requires": null,
        "ascii":
"""
       ════════ THE MIRROR FLOOR ═════════════════════════
                            ▒▒
                          ▒░░░░▒
                         ▒░░░░░░▒    a face below.
                          ▒░░░░▒       upside-down.
                            ▒▒          waiting.
        ─── you are above ─── the face is below ───
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 1, "tint": c_parch,
        "font_size": 11,
        "requires": func(): return mirror_gazes >= 1,
        "ascii":
"""
              ┌─── mirror gaze · 1 ─────────────┐
              │  the reflection.                │
              │  it is yours.                   │
              │  it is not yours.               │
              │  the eyes do not match.         │
              └─────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 2, "tint": c_smoke,
        "font_size": 11,
        "requires": func(): return mirror_gazes >= 2,
        "ascii":
"""
              ┌─── mirror gaze · 2 ─────────────┐
              │  the eyes are darker.           │
              │  the jaw is softer.             │
              │  the hair is longer.            │
              │  the angle is wrong for         │
              │  a reflection of you.           │
              └─────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 3, "tint": c_blood,
        "font_size": 11,
        "requires": func(): return mirror_gazes >= 3,
        "ascii":
"""
              ┌─── mirror gaze · 3 ─────────────┐
              │  it is a woman.                 │
              │  her hand is on the arm of      │
              │  the throne — not yours.        │
              │  the bourbon glass on her side  │
              │  is empty. yours is half full.  │
              └─────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 4, "tint": c_blood,
        "font_size": 11,
        "requires": func(): return mirror_gazes >= 4,
        "ascii":
"""
              ╔══════════════════════════════════╗
              ║   ░ THE SUCCESSOR IS NAMED ░     ║
              ║                                  ║
              ║   it is Nicola.                  ║
              ║                                  ║
              ║   she has not arrived.           ║
              ║   she has already sat there.     ║
              ║                                  ║
              ║   ░ vol5_dual_pov_node = TRUE ░  ║
              ╚══════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 5, "tint": c_rust,
        "font_size": 11,
        "requires": func(): return glass_pours >= 1,
        "ascii":
"""
              ┌──── BOURBON · 1971 ──────────────┐
              │  the bottle is older than him.   │
              │  the seal was broken in '71.     │
              │  the year the diner opened.      │
              │  the year his father died.       │
              │  the year he learned to sign     │
              │  AVTORITAS in a steady hand.     │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 6, "tint": c_smoke,
        "font_size": 10,
        "requires": func(): return commands_run.get("smoke", 0) >= 1,
        "ascii":
"""
              ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
              ░  smoke rises from the throne legs ░
              ░  the cushion is scorched in a ring ░
              ░  the same ring is in Frasier's     ░
              ░  warehouse, under the workbench.   ░
              ░  the same diameter. the same man.  ░
              ░  ─ a knelt man, once.              ░
              ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""
    })

    # ────────────────────────────────────────────────────────────
    # EAST — forward / what the empire becomes / wall RIGHT riddle
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.EAST, "row": 0, "tint": c_sepia,
        "font_size": 11, "requires": null,
        "ascii":
"""

         ┌─── ASCII WALL · RIGHT ──────────────┐
         │  I·──────────────────────────·n     │
         │  M·─ first-character-per-row ─·d    │
         │  P·──── decode each row ─────·d     │
         │  E·─── against the LEFT wall ─·t    │
         │  R·──────────────────────────·a     │
         │  I·──── they mirror at the ──·k     │
         │  V·──── 13th character: an  ─·s     │
         │  M·──── invisible glyph ─────·t     │
         └─────────────────────────────────────┘
         (first letters reading down: IMPERIVM)
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 1, "tint": c_sepia_hot,
        "font_size": 11,
        "requires": func(): return wall_r_decoded,
        "ascii":
"""

              ╔══════════════════════════════════╗
              ║  ░ RIGHT WALL DECODED ░          ║
              ║  IMPERIVM — what survives him.   ║
              ║  the empire after the emperor.   ║
              ║  ─ vol5_keystone_emperor_part_3 ─║
              ╚══════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 2, "tint": c_sepia,
        "font_size": 11,
        "requires": func(): return commands_run.get("steamboat", 0) >= 1
                          or commands_run.get("magician", 0) >= 1,
        "ascii":
"""

              ┌──────────────────────────────────┐
              │  ░ cross-card · MAGICIAN ░       │
              │  the red steamboat in Frasier's  │
              │  model is this boat. mine.       │
              │  he wired it before I bought it. │
              │  the magician sees forward.      │
              │  the emperor catches up.         │
              │  ─ I caught up ─                 │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 3, "tint": c_blood,
        "font_size": 11,
        "requires": func(): return commands_run.get("empress", 0) >= 1
                          or commands_run.get("nicola", 0) >= 1,
        "ascii":
"""

              ┌──────────────────────────────────┐
              │  ░ cross-card · EMPRESS ░        │
              │  the ram-throne in her card.     │
              │  it is the SAME throne.          │
              │  she touches the rams.           │
              │  I have not introduced her.      │
              │  she does not need me to.        │
              │  the throne signed for itself.   │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 4, "tint": c_sepia_hot,
        "font_size": 11,
        "requires": func(): return commands_run.get("hierophant", 0) >= 1
                          or commands_run.get("acadian", 0) >= 1,
        "ascii":
"""

              ┌──────────────────────────────────┐
              │  ░ cross-card · HIEROPHANT ░     │
              │  the vineyard is mine on paper.  │
              │  the Acadian runs it.            │
              │  he calls it his.                │
              │  he is correct.                  │
              │  ─ ownership is a notary fiction ─│
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 5, "tint": c_smoke,
        "font_size": 10,
        "requires": func(): return mirror_gazes >= 4 and
                                  ram_l_touched and ram_r_touched,
        "ascii":
"""

              ╔═══════════════════════════════════╗
              ║   ░ SUCCESSION INSTRUMENT ░       ║
              ║                                   ║
              ║   the rams: inheritance signed.   ║
              ║   the mirror: inheritor named.    ║
              ║   the motto: inheritance lasting. ║
              ║                                   ║
              ║   the chair is hers when she      ║
              ║   sits in it. not before.         ║
              ║   she has, however, already sat.  ║
              ╚═══════════════════════════════════╝
"""
    })

    # ────────────────────────────────────────────────────────────
    # WEST — past / how he came to the throne / wall LEFT
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.WEST, "row": 0, "tint": c_sepia,
        "font_size": 11, "requires": null,
        "ascii":
"""
         ┌─── ASCII WALL · LEFT ───────────────┐
         │  A·─────── the bourbon ─────────·g  │
         │  V·──── the broken seal ───────·a   │
         │  T·──── the father's hand ─────·s   │
         │  O·──── the steady signature ──·k   │
         │  R·──── 1971 — the diner opens ·s   │
         │  I·──── the warehouse purchase ·v   │
         │  T·──── the steamboat acquired ·l   │
         │  A·──── the ram-throne carved ─·a   │
         │  S·──── the motto commissioned ·g   │
         └─────────────────────────────────────┘
         (first letters reading down: AVTORITAS)
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 1, "tint": c_sepia_hot,
        "font_size": 11,
        "requires": func(): return wall_l_decoded,
        "ascii":
"""
              ╔══════════════════════════════════╗
              ║  ░ LEFT WALL DECODED ░           ║
              ║  AVTORITAS — what is given.      ║
              ║  the empire he was handed.       ║
              ║  ─ vol5_keystone_emperor_part_2 ─║
              ╚══════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 2, "tint": c_rust,
        "font_size": 11,
        "requires": func(): return commands_run.get("dante", 0) >= 1,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  DANTE D'AMBROSIO                │
              │  ─── born 1953 ─── still here ── │
              │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
              │  ▓ inherited the diner '71       │
              │  ▓ inherited the river '78       │
              │  ▓ inherited the warehouse '84   │
              │  ▓ inherited his father's smell  │
              │    of bourbon and bay rum '71    │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 3, "tint": c_blood,
        "font_size": 11,
        "requires": func(): return commands_run.get("1971", 0) >= 1
                          or commands_run.get("bourbon", 0) >= 1,
        "ascii":
"""
              ╔══════════════════════════════════╗
              ║  1971 — the year                 ║
              ║                                  ║
              ║  · the diner opens               ║
              ║  · the father dies               ║
              ║  · the bourbon seal breaks       ║
              ║  · he signs his first AVTORITAS  ║
              ║  · in a hand that does not shake ║
              ║                                  ║
              ║  he was eighteen.                ║
              ╚══════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 4, "tint": c_sepia,
        "font_size": 11,
        "requires": func(): return commands_run.get("voltaire", 0) >= 1,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  ░ VOLTAIRE — on his desk too ░  │
              │  CANDIDE — a different printing  │
              │  than Frasier's. an older one.   │
              │  marginalia in his father's hand.│
              │  the underlined sentence reads:  │
              │  \"il faut cultiver notre jardin\"│
              │   (he has not.)                  │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 5, "tint": c_parch,
        "font_size": 11,
        "requires": func(): return commands_run.get("priestess", 0) >= 1
                          or commands_run.get("elicia", 0) >= 1,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  ░ cross-card · PRIESTESS ░       │
              │  Elicia has no tape of him.       │
              │  the throne reflects nothing      │
              │  back at her recorder.            │
              │  this is not refusal. this is     │
              │  the throne's nature: it does     │
              │  not let itself be recorded.      │
              └───────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 6, "tint": c_sepia_dim,
        "font_size": 11,
        "requires": func(): return commands_run.get("john", 0) >= 1
                          or commands_run.get("fool", 0) >= 1,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  ░ cross-card · FOOL ░           │
              │  John wipes the counter he sold  │
              │  me. he does not know he sold    │
              │  it. the diner was already mine  │
              │  before he hired on.             │
              │  the fool builds the empire.     │
              │  the emperor signs for it.       │
              └──────────────────────────────────┘
"""
    })


# ── Mechanics ────────────────────────────────────────────────────
func _do_ankh() -> void:
    ankh_touches += 1
    hotspots_seen["emp_ankh"] = true
    _refresh_tally()
    # Ankh = soft tone — sustained sine
    _active_notes.append({"time":0.0,"freq":146.8,"wave":"sine",
        "atk":0.04,"dur":0.45,"rel":0.60})
    _memorize("ankh #%d" % ankh_touches)
    var lines := ["the ankh is warm.",
        "the ankh hums against his palm.",
        "the ankh remembers being held.",
        "the ankh: ☥ — the only soft thing he holds.",
        "the ankh agrees with him. once. tonight."]
    var i: int = min(ankh_touches - 1, lines.size() - 1)
    status_label.text = lines[i]
    _log("[color=#ffd896]· ☥ %s[/color]" % lines[i])
    if ankh_touches == 1:
        SaveSystem.mark_unlocked("music:vol5_emperor_theme")


func _do_ram_l() -> void:
    if not ram_l_touched:
        ram_l_touched = true
        hotspots_seen["emp_ram_left"] = true
        _refresh_tally()
        _memorize("ram left touched (inverted aries)")
        status_label.text = "left horn — inverted aries. the past empire."
        _log("[color=#c89060]· left ram acknowledged ─ inverted aries.[/color]")
        SaveSystem.mark_unlocked("lore:aries_left_horn")
    _ram_chord()
    if ram_l_touched and ram_r_touched:
        _log("[color=#ffb060]· ░░ BOTH rams ─ inheritance carved both ways.[/color]")
        SaveSystem.mark_unlocked("vol5_aries_inheritance_emperor")


func _do_ram_r() -> void:
    if not ram_r_touched:
        ram_r_touched = true
        hotspots_seen["emp_ram_right"] = true
        _refresh_tally()
        _memorize("ram right touched (upright aries)")
        status_label.text = "right horn — upright aries. the next empire."
        _log("[color=#c89060]· right ram acknowledged ─ upright aries.[/color]")
        SaveSystem.mark_unlocked("lore:aries_right_horn")
    _ram_chord()
    if ram_l_touched and ram_r_touched:
        _log("[color=#ffb060]· ░░ BOTH rams ─ inheritance carved both ways.[/color]")
        SaveSystem.mark_unlocked("vol5_aries_inheritance_emperor")


func _ram_chord() -> void:
    # E minor open — imperial heavy
    for f in [82.4, 164.8, 246.9]:
        _active_notes.append({"time":0.0,"freq":f,"wave":"sawtooth",
            "atk":0.01,"dur":0.45,"rel":0.55})


func _do_glass() -> void:
    glass_pours += 1
    hotspots_seen["emp_glass"] = true
    _refresh_tally()
    _active_notes.append({"time":0.0,"freq":175.0,"wave":"triangle",
        "atk":0.005,"dur":0.20,"rel":0.30})
    _memorize("bourbon #%d" % glass_pours)
    var lines := ["1971. the seal broke that year.",
        "second pour. steady hand.",
        "third pour. the year of the diner.",
        "fourth. the bottle is older than him.",
        "fifth. the bottle empties when he does."]
    var i: int = min(glass_pours - 1, lines.size() - 1)
    status_label.text = lines[i]
    _log("[color=#c8704a]· bourbon · %s[/color]" % lines[i])
    SaveSystem.mark_unlocked("lore:bourbon_1971")


func _do_motto() -> void:
    motto_read = true
    hotspots_seen["motto"] = true
    _refresh_tally()
    # Deep tonic chord
    for f in [82.4, 110.0, 164.8, 220.0]:
        _active_notes.append({"time":0.0,"freq":f,"wave":"sawtooth",
            "atk":0.05,"dur":0.7,"rel":0.7})
    _memorize("motto read")
    status_label.text = "AVTORITAS · POTESTAS · IMPERIVM."
    _log("[color=#ffd896]· ░ KEYSTONE ─ AVTORITAS · POTESTAS · IMPERIVM[/color]")
    _log("[color=#a87040]·   given / taken / surviving.[/color]")
    SaveSystem.mark_unlocked("vol5_keystone_emperor")


func _do_mirror() -> void:
    if mirror_gazes >= MIRROR_STAGES.size():
        status_label.text = "the mirror has shown what it shows. no more."
        return
    mirror_gazes += 1
    hotspots_seen["mirror"] = true
    _refresh_tally()
    # Inverted minor — descending
    _active_notes.append({"time":0.0,"freq":110.0,"wave":"sine",
        "atk":0.02,"dur":0.35,"rel":0.40})
    _active_notes.append({"time":0.0,"freq":92.5,"wave":"sine",
        "atk":0.04,"dur":0.40,"rel":0.50})
    _memorize("mirror gaze #%d" % mirror_gazes)
    var line: String = MIRROR_STAGES[mirror_gazes - 1]
    status_label.text = line
    _log("[color=#c89868]· mirror · %s[/color]" % line)
    if mirror_gazes >= MIRROR_STAGES.size():
        _log("[color=#c84030]· ░░ SUCCESSOR NAMED · Nicola has already sat.[/color]")
        SaveSystem.mark_unlocked("vol5_dual_pov_node")
        SaveSystem.mark_unlocked("vol5_emperor_succession_seen")


func _on_hotspot(hs: Dictionary) -> void:
    super(hs)
    var hs_id := str(hs.get("id",""))
    hotspots_seen[hs_id] = true
    _memorize("hotspot: " + hs_id)
    match hs_id:
        "emp_ankh":      _do_ankh()
        "emp_ram_left":  _do_ram_l()
        "emp_ram_right": _do_ram_r()
        "emp_glass":     _do_glass()
        _:
            status_label.text = "[ %s ]" % str(hs.get("interact", hs_id))


# ── Console commands ─────────────────────────────────────────────
func _on_command(text: String) -> void:
    var line := text.strip_edges().to_lower()
    console_input.text = ""
    if line == "":
        return
    _log("[color=#ffd896]> %s[/color]" % text)
    commands_run[line] = int(commands_run.get(line, 0)) + 1
    _memorize("typed: " + line)
    var parts := line.split(" ", false)
    var cmd := parts[0]

    match cmd:
        # Public
        "help", "?":
            _cmd_help()
        "ankh":
            _do_ankh()
        "ram":
            _cmd_ram()
        "glass", "bourbon", "drink":
            _do_glass()
        "motto", "keystone":
            _do_motto()
        "mirror", "gaze":
            _do_mirror()
        "decode", "walls", "wall":
            _cmd_decode()
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
        # Hidden lore — motto components
        "avtoritas", "authority":
            _log("[color=#ffd896]  AVTORITAS — what is given to a man.[/color]")
            _log("[color=#a87040]  the empire he was handed in 1971.[/color]")
        "potestas", "power":
            _log("[color=#ffd896]  POTESTAS — what he takes for himself.[/color]")
            _log("[color=#a87040]  the warehouse, the river, the road.[/color]")
        "imperivm", "imperium", "empire":
            _log("[color=#ffd896]  IMPERIVM — what survives him.[/color]")
            _log("[color=#a87040]  the only verb in the motto that is not his.[/color]")
        # Hidden — succession
        "successor", "successors":
            _log("[color=#c84030]  the mirror knows her name. it spelled it down.[/color]")
        "upside_down", "inverted":
            _log("[color=#c84030]  the reflections do not match the chair.[/color]")
            _log("[color=#7a3030]  this is not refusal. this is recognition.[/color]")
        "aries", "horn":
            _log("[color=#c89060]  left horn inverted. right horn upright.[/color]")
            _log("[color=#a87040]  the orientation flips when the chair changes.[/color]")
        "inheritance":
            if not ram_l_touched: _do_ram_l()
            if not ram_r_touched: _do_ram_r()
        # Cross-references
        "steamboat":
            _log("[color=#ffd896]  the red boat in Frasier's model is mine.[/color]")
            _log("[color=#a87040]  he wired it before I bought it.[/color]")
        "magician", "frasier":
            _log("[color=#88c8d0]  Frasier · the magician sees forward.[/color]")
            _log("[color=#a87040]  I catch up.[/color]")
        "empress", "nicola":
            _log("[color=#c8807a]  Nicola · she sits in the chair when I am not in it.[/color]")
            _log("[color=#a87040]  the chair does not mind. I am learning not to.[/color]")
        "priestess", "elicia":
            _log("[color=#a09a8a]  Elicia has no tape of me.[/color]")
            _log("[color=#7a7468]  the throne does not let itself be recorded.[/color]")
        "fool", "john":
            _log("[color=#c89868]  John wipes the counter he sold me.[/color]")
            _log("[color=#a87040]  he does not know he sold it.[/color]")
        "hierophant", "acadian":
            _log("[color=#a878d0]  the Acadian runs my vineyard.[/color]")
            _log("[color=#a87040]  he calls it his. he is correct.[/color]")
        # Self
        "dante":
            _log("[color=#ffd896]  he does not stand up when his name is called.[/color]")
            _log("[color=#a87040]  the throne stands up first. always has.[/color]")
        "1971":
            _log("[color=#c84030]  the year of the seal break.[/color]")
            _log("[color=#7a3030]  the year of the diner opening.[/color]")
            _log("[color=#7a3030]  the year his father stopped.[/color]")
        "smoke":
            _log("[color=#888078]  the ring under the cushion is scorched.[/color]")
            _log("[color=#5a5450]  same diameter as the warehouse ring.[/color]")
        "rust":
            _log("[color=#c8704a]  the throne wears rust the way other men wear suits.[/color]")
        "voltaire", "candide":
            _log("[color=#c89868]  his father's copy. underlined: 'cultivate the garden.'[/color]")
            _log("[color=#7a7468]  he has not.[/color]")
        "riddle":
            _log("[color=#ffd896]  LEFT wall first chars: AVTORITAS.[/color]")
            _log("[color=#ffd896]  RIGHT wall first chars: IMPERIVM.[/color]")
            _log("[color=#a87040]  POTESTAS is between them — in the chair.[/color]")
            wall_l_decoded = true
            wall_r_decoded = true
            SaveSystem.mark_unlocked("vol5_keystone_emperor_part_2")
            SaveSystem.mark_unlocked("vol5_keystone_emperor_part_3")
        "throne":
            _log("[color=#c8704a]  it is also a chair. mostly.[/color]")
        "iv", "four":
            _log("[color=#ffd896]  IV — the number Nicola already inherited.[/color]")
            _log("[color=#a87040]  her card was mislabeled IV. it was correct.[/color]")
        _:
            if line == "tip":
                _log("[color=#a87040]  no tip jar. emperors take.[/color]")
            elif line == "rust_code.bbs":
                _log("[color=#ffd896]  the BBS belongs to me on paper.[/color]")
                _log("[color=#a87040]  on practice it belongs to Frasier.[/color]")
            else:
                _log("[color=#5a3018]? unknown. try: help · decode · motto[/color]")


func _cmd_help() -> void:
    _log("[color=#ffd896]commands (visible):[/color]")
    _log("  [color=#ffd896]ankh[/color]       — touch the sceptre")
    _log("  [color=#ffd896]ram[/color]        — touch both ram-heads")
    _log("  [color=#ffd896]glass[/color]      — pour the bourbon")
    _log("  [color=#ffd896]motto[/color]      — read the keystone")
    _log("  [color=#ffd896]mirror[/color]     — gaze into the floor")
    _log("  [color=#ffd896]decode[/color]     — decode the ASCII walls")
    _log("  [color=#ffd896]recall[/color]     — discovery log")
    _log("  [color=#ffd896]count[/color]      — tallies")
    _log("  [color=#ffd896]look · listen · clear · exit[/color]")
    _log("[color=#a87040](some commands are unlisted. the throne keeps counsel.)[/color]")


func _cmd_ram() -> void:
    if not ram_l_touched: _do_ram_l()
    if not ram_r_touched: _do_ram_r()


func _cmd_decode() -> void:
    if wall_l_decoded and wall_r_decoded:
        _log("[color=#a87040]  the walls are already decoded. AVTORITAS · IMPERIVM.[/color]")
        return
    wall_l_decoded = true
    wall_r_decoded = true
    _log("[color=#ffd896]  ░ DECODING ─ first-character-per-row ─[/color]")
    _log("[color=#ffd896]  LEFT wall:  A V T O R I T A S → AVTORITAS[/color]")
    _log("[color=#ffd896]  RIGHT wall: I M P E R I V M → IMPERIVM[/color]")
    _log("[color=#a87040]  the keystone POTESTAS is between them. in the chair.[/color]")
    _memorize("walls decoded")
    SaveSystem.mark_unlocked("vol5_keystone_emperor_part_2")
    SaveSystem.mark_unlocked("vol5_keystone_emperor_part_3")


func _cmd_memory() -> void:
    _log("[color=#ffd896]── memory · %d entries ──[/color]" % memory.size())
    var shown := 0
    for entry in memory:
        if shown >= 20:
            _log("[color=#a87040]  ... (%d more)[/color]" %
                 (memory.size() - shown))
            break
        _log("  [color=#c89868]· %s[/color]" % entry)
        shown += 1


func _cmd_count() -> void:
    _log("[color=#ffd896]── tallies ────────────────[/color]")
    _log("  ankh:        [color=#ffd896]%d[/color]" % ankh_touches)
    _log("  rams:        [color=#c89060]%s · %s[/color]" % [
         "L✓" if ram_l_touched else "L─",
         "R✓" if ram_r_touched else "R─"])
    _log("  bourbon:     [color=#c8704a]%d pours[/color]" % glass_pours)
    _log("  motto:       [color=#ffd896]%s[/color]" %
         ("read" if motto_read else "unread"))
    _log("  mirror:      [color=#c84030]%d / %d gazes[/color]" %
         [mirror_gazes, MIRROR_STAGES.size()])
    _log("  walls:       [color=#a87040]%s · %s[/color]" % [
         "L✓" if wall_l_decoded else "L─",
         "R✓" if wall_r_decoded else "R─"])
    _log("  hotspots:    [color=#ffd896]%d[/color]" % hotspots_seen.size())
    _log("  commands run:[color=#ffd896] %d[/color]" % commands_run.size())


func _cmd_look() -> void:
    _log("[color=#c89868]· the throne: ram-headed, rusted, warm.[/color]")
    _log("[color=#c89868]· the ankh in his right hand.[/color]")
    _log("[color=#c89868]· the bourbon glass beside him, half-poured.[/color]")
    _log("[color=#c89868]· the motto at his feet: AVTORITAS · POTESTAS · IMPERIVM.[/color]")
    _log("[color=#a87040]· the floor mirror — the face below is yours and not yours.[/color]")
    _log("[color=#a87040]· two ASCII walls flanking him. they read down, not across.[/color]")


func _cmd_listen() -> void:
    _log("[color=#c89868]· the throne creaks. it has weight in it.[/color]")
    _log("[color=#c89868]· the bourbon, a glass placed without care.[/color]")
    _log("[color=#c89868]· the ankh hums. very low.[/color]")
    _log("[color=#a87040]· something below the floor. a chair, scraping.[/color]")
    _log("[color=#a87040]· a woman, not quite standing up yet.[/color]")


func _refresh_tally() -> void:
    if tally_btn != null:
        tally_btn.text = "  ☥ ankh %d · rams %d/2 · pours %d · mirror %d/4  " % [
            ankh_touches,
            (1 if ram_l_touched else 0) + (1 if ram_r_touched else 0),
            glass_pours,
            mirror_gazes]


func _memorize(entry: String) -> void:
    memory.append(entry)
    if memory.size() > 200:
        memory.remove_at(0)


func _log(line: String) -> void:
    if console_log != null:
        console_log.append_text(line + "\n")


# ── Process / throne breath / audio-reactive ASCII pulse ─────────
func _process(delta: float) -> void:
    super(delta)
    # Slow, heavy throne breath
    throne_breath = fmod(throne_breath + delta / 11.0, TAU)
    if card_rect != null:
        var b := 0.5 + sin(throne_breath) * 0.5
        # Warm sepia, with a hint of red when mirror has revealed
        var red_bias := mirror_gazes * 0.025
        card_rect.modulate = Color(
            1.0 + b * 0.04 + red_bias,
            0.97 + b * 0.02,
            0.92 - b * 0.02)
    # Audio-reactive ASCII pulse
    tableau_pulse += delta
    var amp: float = 0.0
    var am := get_node_or_null("/root/AudioMgr")
    if am != null and am.has_method("get_bgm_magnitude"):
        amp = clamp(float(am.call("get_bgm_magnitude", 80.0, 3200.0)) * 10.0,
                     0.0, 1.0)
    # Slower, heavier pulse than the other cards — imperial pace
    var base_amp = 0.08 + amp * 0.30
    var idx := 0
    for seg in _segments:
        if not seg.get("shown", false): continue
        var lbl: Label = seg.get("label")
        if lbl == null: continue
        var phase = tableau_pulse * 1.6 + idx * 0.42
        var pulse_val = sin(phase) * 0.5 + 0.5
        var tint: Color = seg.get("tint", C_TEXT)
        var lifted := tint.lerp(C_GOLD_HI, pulse_val * base_amp)
        lifted.a = tint.a * (0.88 + pulse_val * base_amp * 0.25)
        lbl.modulate = lifted
        idx += 1


func _input(event: InputEvent) -> void:
    super(event)
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_SPACE and not console_input.has_focus():
            _do_ankh()
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
