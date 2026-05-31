extends "res://scenes/menu/TarotVisualizerBase.gd"
## HierophantVisualizer — Sunday Dress, Stiff & Biting.
##
## Maya at St. Jude's Acadian Church, Sunday morning, before the
## 7am mass. Child POV: the world is too large, the system is
## above her, the dress physically bites. The painted card carries
## the inherited form — Petrine keys, triple tiara, the AVDI ET
## TACE banner, the two kneeling acolytes (M and Y), the rose
## window, the carpet with three layered Latin lines.
##
##   • CARD HOTSPOTS — seven rects on the painted Hierophant:
##       DRESS   the dress that bites her back (signature mechanic)
##       KEYS    crossed Petrine keys above the rose window
##       CROWN   the triple papal tiara
##       MAYA    her own kneeling acolyte figure (M)
##       Y       the unnamed companion acolyte (mystery)
##       WINDOW  the 8-segment rose window (red/blue/yellow/green)
##       BANNER  AVDI · ET · TACE (chapter command)
##
##   • BBS CONSOLE — `maya@pew:~$`. Public: help · dress · keys ·
##     crown · maya · y · window · banner · carpet · recall · count ·
##     look · listen · clear · exit. Hidden: avdi · tace · silent ·
##     mass · ecclesia · sanctifica · petrine · tiara · rose ·
##     beatitudes · bite · stiff · sunday · companion · quent · paul ·
##     catechism · acadian · st_jude · itch · scratch · candide ·
##     voltaire · plus cross-character routes.

# ── Game state ───────────────────────────────────────────────────
var dress_touches: int = 0          # the bite count — Maya's body log
var keys_touched: bool = false
var crown_touched: bool = false
var maya_touched: bool = false
var y_touched: int = 0              # 0..3 progressive identity reveal
var window_segments: int = 0        # 0..8 colors collected
var banner_read: bool = false
var carpet_read_stage: int = 0      # 0..3 — three layered latin lines
var hotspots_seen: Dictionary = {}
var commands_run: Dictionary = {}
var memory: PackedStringArray = []
var heat_phase: float = 0.0
var tableau_pulse: float = 0.0

# ── UI refs ──────────────────────────────────────────────────────
var tally_btn: Button
var status_label: Label
var console_input: LineEdit
var console_log: RichTextLabel

# Maya's body-log — the dress bites in different places each time
const DRESS_BITES := [
    "the dress bites her back.",
    "the dress bites her under the arm.",
    "the dress bites where the collar meets the throat.",
    "the dress bites where the elastic is.",
    "the dress bites where the lace meets the skin.",
    "the dress bites because it was made for a different girl.",
    "the dress bites because it remembers the girl it was made for.",
    "the dress bites because the dress is the hierophant.",
]

# Y reveal stages — the unnamed companion's identity surfaces slowly
const Y_REVEALS := [
    "Y is beside her. Y kneels too. Y is also seven.",
    "Y has a different last name. Y's mother is here. Y's mother is praying.",
    "Y is Father Quent's nephew. Y will be a priest, eventually. Y already knows.",
]

# Rose window 8 segments (cycle through them on click)
const WINDOW_COLORS := [
    "RED",     "BLUE",    "YELLOW",  "GREEN",
    "RED",     "BLUE",    "YELLOW",  "GREEN",
]

# Three layered Latin carpet lines (revealed in order)
const CARPET_LINES := [
    "ECCLESIA SEMPER REFORMANDA — always reforming. it never stops.",
    "ANIMA CHRISTI SANCTIFICA ME — sanctify me. she does not know what this means.",
    "DOMINICA MASS · 7 · 9 · 11 — three masses. the chapter is before the seven.",
]


func _init() -> void:
    _card_path  = "res://assets/gallery/hierophant.png"
    _hooks_path = "res://resources/puzzle_hooks/hierophant.json"
    _ambient_audio_path = "res://assets/audio/bgm/vol5_ambient.ogg"
    # Papal red / blue / gold — but seen through a child's hot-skin POV
    C_BG = Color(0.060, 0.040, 0.060)
    C_GOLD = Color(0.95, 0.78, 0.30)
    C_GOLD_HI = Color(1.0, 0.92, 0.50)
    C_TEXT = Color(0.85, 0.78, 0.62)
    C_TEXT_DIM = Color(0.45, 0.40, 0.42)


func _build_chrome() -> void:
    super()
    _build_bottom_strip()
    _build_card_hotspots()


# Per-region hotspots on the painted Hierophant card.
func _build_card_hotspots() -> void:
    if card_rect == null: return
    var defs := [
        ["dress",  Rect2(0.41, 0.76, 0.18, 0.20), "feel the dress bite",        _do_dress],
        ["keys",   Rect2(0.41, 0.03, 0.18, 0.10), "touch the crossed keys",     _do_keys],
        ["crown",  Rect2(0.45, 0.11, 0.10, 0.10), "touch the triple crown",     _do_crown],
        ["maya",   Rect2(0.30, 0.70, 0.14, 0.20), "be the kneeling Maya",       _do_maya],
        ["y",      Rect2(0.55, 0.70, 0.14, 0.20), "look at the other acolyte",  _do_y],
        ["window", Rect2(0.41, 0.13, 0.18, 0.16), "count the window segments",  _do_window],
        ["banner", Rect2(0.24, 0.01, 0.52, 0.07), "read the AVDI banner",       _do_banner],
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
        sb.bg_color = Color(0.95, 0.30, 0.30, 0.0)
        sb.border_color = Color(0.95, 0.30, 0.30, 0.0)
        sb.set_border_width_all(1)
        btn.add_theme_stylebox_override("normal", sb)
        var bsh := sb.duplicate() as StyleBoxFlat
        bsh.bg_color = Color(0.95, 0.30, 0.30, 0.22)
        bsh.border_color = Color(1.0, 0.92, 0.50, 0.85)
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
    bps.bg_color = Color(0.04, 0.025, 0.04, 0.85)
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
        Color(0.92, 0.80, 0.62))
    vbox.add_child(console_log)

    var inrow := HBoxContainer.new()
    inrow.add_theme_constant_override("separation", 4)
    var prompt := Label.new()
    prompt.text = "maya@pew:~$ "
    prompt.add_theme_color_override("font_color", C_GOLD_HI)
    prompt.add_theme_font_size_override("font_size", 12)
    inrow.add_child(prompt)
    console_input = LineEdit.new()
    console_input.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    console_input.add_theme_color_override("font_color",
        Color(1.0, 0.92, 0.55))
    console_input.text_submitted.connect(_on_command)
    inrow.add_child(console_input)
    vbox.add_child(inrow)

    var actrow := HBoxContainer.new()
    actrow.add_theme_constant_override("separation", 12)
    vbox.add_child(actrow)

    tally_btn = Button.new()
    tally_btn.text = "  ✠ bites 0/8 · window 0/4 · Y 0/3  "
    tally_btn.add_theme_color_override("font_color", C_GOLD_HI)
    tally_btn.add_theme_font_size_override("font_size", 11)
    var wbs := StyleBoxFlat.new()
    wbs.bg_color = Color(C_GOLD.r * 0.18, C_GOLD.g * 0.18, C_GOLD.b * 0.18, 0.55)
    wbs.border_color = C_GOLD
    wbs.set_border_width_all(1)
    tally_btn.add_theme_stylebox_override("normal", wbs)
    var wbh := wbs.duplicate() as StyleBoxFlat
    wbh.bg_color = Color(C_GOLD.r * 0.40, C_GOLD.g * 0.40, C_GOLD.b * 0.40, 0.7)
    wbh.border_color = C_GOLD_HI
    tally_btn.add_theme_stylebox_override("hover", wbh)
    tally_btn.pressed.connect(_do_dress)
    tally_btn.tooltip_text = "click card regions for distinct mechanics"
    actrow.add_child(tally_btn)

    status_label = Label.new()
    status_label.text = "click the card · dress · keys · crown · maya · y · window · banner"
    status_label.add_theme_color_override("font_color",
        Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.80))
    status_label.add_theme_font_size_override("font_size", 10)
    status_label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    status_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    actrow.add_child(status_label)

    _log("[color=#ffd070]> V · THE HIEROPHANT · vol.5 ch.5 · St. Jude's, Sunday[/color]")
    _log("[color=#a87830]> before the 7am mass. parking lot. heat already rising.[/color]")
    _log("[color=#ffd070]> AVDI · ET · TACE[/color]")
    _log("[color=#a87830]>   (hear · and · be silent)[/color]")
    _log("[color=#a87830]> type [color=#ffe896]help[/color] · the dress bites whether you read this or not.[/color]")

    console_input.grab_focus()


# ── Tableau registration ─────────────────────────────────────────
func _build_thematic_widget() -> void:
    var c_gold := C_GOLD_HI
    var c_red := Color(0.85, 0.25, 0.28, 0.95)
    var c_red_dim := Color(0.50, 0.18, 0.20, 0.85)
    var c_blue := Color(0.35, 0.45, 0.85, 0.95)
    var c_blue_dim := Color(0.22, 0.28, 0.50, 0.85)
    var c_cream := Color(0.92, 0.85, 0.68, 0.95)
    var c_stone := Color(0.55, 0.50, 0.48, 0.85)
    var c_child := Color(0.95, 0.75, 0.65, 0.95)   # warm child skin

    # ────────────────────────────────────────────────────────────
    # NORTH — above her / the unreachable system / keys / crown
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.NORTH, "row": 0, "tint": c_gold,
        "font_size": 13, "requires": null,
        "ascii":
"""
       ╔═══════════════════════════════════════════════════╗
       ║   V  ░░  THE HIEROPHANT  ░░  ACADIAN · ST. JUDE'S║
       ╚═══════════════════════════════════════════════════╝
        ─── Sunday Dress, Stiff & Biting ─── parking lot ───
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 1, "tint": c_gold,
        "font_size": 12,
        "requires": null,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │      A V D I  ·  E T  ·  T A C E │
              │      ───────────────────────     │
              │       (hear · and · be silent)   │
              │      ─── carved into the lintel ─│
              │      ─── carved into the carpet ─│
              │      ─── carved into the child ─ │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 2, "tint": c_gold,
        "font_size": 12,
        "requires": func(): return banner_read,
        "ascii":
"""
       ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
     ░▒▒▓▓████  KEYSTONE · HIEROPHANT  ████▓▓▒▒░
       ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
        AVDI  — hear what you are told.
        ET    — and. the conjunction is the bind.
        TACE  — be silent. do not answer back.
        ─── the chapter's command to her ───
        ─── the chapter's command to you ───
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 3, "tint": c_gold,
        "font_size": 11,
        "requires": func(): return keys_touched,
        "ascii":
"""
              ╔══════════════════════════════════╗
              ║    ░  ✠ CROSSED KEYS ✠  ░         ║
              ║                                  ║
              ║    one key for heaven.           ║
              ║    one key for earth.            ║
              ║    crossed at the bow.           ║
              ║    held by no one.               ║
              ║                                  ║
              ║    above the rose window.        ║
              ║    above where she can reach.    ║
              ╚══════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 4, "tint": c_gold,
        "font_size": 11,
        "requires": func(): return crown_touched,
        "ascii":
"""
              ╔══════════════════════════════════╗
              ║      ░  ▓▓▓▓ TIARA ▓▓▓▓  ░       ║
              ║      ░ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ░         ║
              ║      ░░░░░░░░░░░░░░░░░░          ║
              ║      ─── three tiers ───         ║
              ║      ─ TEACHING ─                ║
              ║      ─ GOVERNING ─               ║
              ║      ─ SANCTIFYING ─             ║
              ║      three rings she must pass.  ║
              ╚══════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 5, "tint": c_red,
        "font_size": 11,
        "requires": func(): return window_segments >= 4,
        "ascii":
"""
              ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
            ░░  ROSE WINDOW · 8 segments         ░░
            ░░     R · B · Y · G · R · B · Y · G  ░░
            ░░     red / blue / yellow / green   ░░
            ░░  ─ four colors twice ─            ░░
            ░░  ─ eight beatitudes ─             ░░
            ░░  ─ seven sacraments + baptism ─   ░░
            ░░  ─ Maya counts to four ─          ░░
            ░░  ─ then loses count ─             ░░
              ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 6, "tint": c_gold,
        "font_size": 11,
        "requires": func(): return hotspots_seen.size() >= 6,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  ░ THE CARD IS THE CATECHISM ░   │
              │  every figure points to a rule.  │
              │  every rule points to a figure.  │
              │  Maya is being inducted.         │
              │  the dress is doing the work.    │
              │  the player has been doing it    │
              │  too, by reading this far.       │
              └──────────────────────────────────┘
"""
    })

    # ────────────────────────────────────────────────────────────
    # SOUTH — below / floor / carpet / dress that bites / her body
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.SOUTH, "row": 0, "tint": c_stone,
        "font_size": 12, "requires": null,
        "ascii":
"""
       ════════ THE CARPET · St. Jude's ═════════════════════
        ░ red carpet runner ─ five colors of thread ─        ░
        ░ words woven in, three rows deep:                   ░
        ░   row 1: ECCLESIA SEMPER REFORMANDA                ░
        ░   row 2: ANIMA CHRISTI SANCTIFICA ME               ░
        ░   row 3: DOMINICA MASS  7  9  11                   ░
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 1, "tint": c_child,
        "font_size": 11,
        "requires": func(): return dress_touches >= 1,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  ░ MAYA's body log ░             │
              │  the dress bites her back.       │
              │  the seam is in the wrong place. │
              │  the lace is stiff with starch.  │
              │  her shoulder blades know first. │
              │  her ribs know next.             │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 2, "tint": c_red_dim,
        "font_size": 11,
        "requires": func(): return dress_touches >= 4,
        "ascii":
"""
              ╔══════════════════════════════════╗
              ║   the dress bites ░ four ░ times ║
              ║   ─ each bite a different place ─║
              ║                                  ║
              ║   she does not scratch. she does ║
              ║   not move. she does not speak.  ║
              ║                                  ║
              ║   AVDI ET TACE has been heard.   ║
              ║   AVDI ET TACE has been obeyed.  ║
              ╚══════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 3, "tint": c_red,
        "font_size": 11,
        "requires": func(): return dress_touches >= 8,
        "ascii":
"""
              ╔══════════════════════════════════╗
              ║  ░ THE DRESS IS THE HIEROPHANT ░ ║
              ║                                  ║
              ║  the figure on the card is the   ║
              ║  excuse. the actual hierophant   ║
              ║  is the garment.                 ║
              ║                                  ║
              ║  it bites because that is what   ║
              ║  was inherited. she bleeds a     ║
              ║  little. she will be told it     ║
              ║  was the heat.                   ║
              ╚══════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 4, "tint": c_cream,
        "font_size": 11,
        "requires": func(): return carpet_read_stage >= 1,
        "ascii":
"""
              ┌──── carpet · row 1 ──────────────┐
              │  ECCLESIA SEMPER REFORMANDA      │
              │  ─── always reforming ───        │
              │  the institution is never done.  │
              │  it has been reforming for       │
              │  centuries. it will reform       │
              │  through her too. starting now.  │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 5, "tint": c_blue,
        "font_size": 11,
        "requires": func(): return carpet_read_stage >= 2,
        "ascii":
"""
              ┌──── carpet · row 2 ──────────────┐
              │  ANIMA CHRISTI SANCTIFICA ME     │
              │  ─── sanctify me ───             │
              │  she does not know what          │
              │  SANCTIFICA means.               │
              │  she repeats it under her breath │
              │  because it sounds like SCRATCH. │
              │  she would scratch if she could. │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 6, "tint": c_gold,
        "font_size": 11,
        "requires": func(): return carpet_read_stage >= 3,
        "ascii":
"""
              ┌──── carpet · row 3 ──────────────┐
              │  DOMINICA MASS  7  9  11         │
              │  ─── the schedule ───            │
              │  this chapter is before the 7.   │
              │  the heat is already up. the     │
              │  doors are open for the carpet   │
              │  to air. she counts to seven on  │
              │  the carpet rows. she gets there.│
              └──────────────────────────────────┘
"""
    })

    # ────────────────────────────────────────────────────────────
    # EAST — forward / who she'll be / catechism / Y identity
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.EAST, "row": 0, "tint": c_gold,
        "font_size": 11, "requires": null,
        "ascii":
"""

         ┌── CATECHISM · pending ─────────────────┐
         │  age 7   first communion               │
         │  age 12  confirmation                  │
         │  age 14  she stops attending           │
         │  age 19  she comes back, briefly       │
         │  age 31  she has not been back since   │
         │                                        │
         │  ─ the schedule does not know this yet ─│
         └────────────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 1, "tint": c_cream,
        "font_size": 11,
        "requires": func(): return y_touched >= 1,
        "ascii":
"""

              ┌────────────────────────────────┐
              │  Y · the other acolyte         │
              │  ░ Y is beside her             │
              │  ░ Y kneels too                │
              │  ░ Y is also seven             │
              │  ░ Y has not said anything     │
              │    today. AVDI ET TACE applies │
              │    to Y just the same.         │
              └────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 2, "tint": c_cream,
        "font_size": 11,
        "requires": func(): return y_touched >= 2,
        "ascii":
"""

              ┌────────────────────────────────┐
              │  Y · more visible              │
              │  ░ Y has a different last name │
              │  ░ Y's mother is in the back   │
              │  ░ Y's mother is praying with  │
              │    her eyes open               │
              │  ░ Y's mother is from out of   │
              │    town. she is here for this. │
              └────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 3, "tint": c_gold,
        "font_size": 11,
        "requires": func(): return y_touched >= 3,
        "ascii":
"""

              ╔════════════════════════════════╗
              ║   Y · identified               ║
              ║                                ║
              ║   Y is Father Quent's nephew.  ║
              ║   Y will be a priest, in time. ║
              ║   Y already knows.             ║
              ║                                ║
              ║   Maya does not know what      ║
              ║   ALREADY KNOWS means.         ║
              ║                                ║
              ║   ░ vol5_y_identified = TRUE ░ ║
              ╚════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 4, "tint": c_blue,
        "font_size": 11,
        "requires": func(): return commands_run.get("priestess", 0) >= 1
                          or commands_run.get("elicia", 0) >= 1,
        "ascii":
"""

              ┌──────────────────────────────────┐
              │  ░ cross-card · PRIESTESS ░      │
              │  Elicia is the adult observer.   │
              │  Maya is the child experiencer.  │
              │  one records. one is being       │
              │  recorded INTO.                  │
              │  they are the same shape from    │
              │  different angles in time.       │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 5, "tint": c_red,
        "font_size": 11,
        "requires": func(): return commands_run.get("emperor", 0) >= 1
                          or commands_run.get("dante", 0) >= 1,
        "ascii":
"""

              ┌──────────────────────────────────┐
              │  ░ cross-card · EMPEROR ░        │
              │  the vineyard belongs to Dante.  │
              │  the Acadian (Father Quent's     │
              │  uncle) runs it on his behalf.   │
              │  the wine for the 9am mass:      │
              │  Acadian Vineyard '94.           │
              │  GAS STATION RED on the table.   │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 6, "tint": c_gold,
        "font_size": 11,
        "requires": func(): return banner_read and dress_touches >= 4,
        "ascii":
"""

              ╔══════════════════════════════════╗
              ║  ░ HIEROPHANT FULL RECEIVED ░    ║
              ║                                  ║
              ║  ▓ AVDI ET TACE banner read.     ║
              ║  ▓ Dress has bitten four times.  ║
              ║  ▓ Maya has not spoken.          ║
              ║  ▓ Maya has not moved.           ║
              ║                                  ║
              ║  she is now a member.            ║
              ║  the system has installed itself.║
              ╚══════════════════════════════════╝
"""
    })

    # ────────────────────────────────────────────────────────────
    # WEST — past / Acadian inheritance / parents / heat
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.WEST, "row": 0, "tint": c_cream,
        "font_size": 11, "requires": null,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  ST. JUDE's ACADIAN CHURCH       │
              │  ─── parish est. 1898 ───        │
              │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
              │  ▓ Father Paul (pastor)          │
              │  ▓ Father Quent (deacon, Acadian)│
              │  ▓ Acadian Vineyard donates wine │
              │  ▓ carpet replaced 1976          │
              │  ▓ next replacement: never       │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 1, "tint": c_child,
        "font_size": 11,
        "requires": null,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  MAYA · age 7 · Sunday morning   │
              │  ─── before the 7am mass ───     │
              │ ░ the dress was her cousin's.    │
              │ ░ the cousin was a year older.   │
              │ ░ the cousin grew faster than    │
              │   anyone expected.               │
              │ ░ Maya was told it would fit.    │
              │ ░ Maya was told incorrectly.     │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 2, "tint": c_cream,
        "font_size": 11,
        "requires": func(): return commands_run.get("quent", 0) >= 1
                          or commands_run.get("paul", 0) >= 1
                          or commands_run.get("father", 0) >= 1,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  FATHER PAUL · 58 · pastor       │
              │  ─ believes in process ─         │
              │  ─ believes in patience ─        │
              │  ─ does not believe in the heat ─│
              │                                  │
              │  FATHER QUENT · 34 · Acadian     │
              │  ─ believes in form ─            │
              │  ─ believes in inheritance ─     │
              │  ─ wears the heat as a vestment ─│
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 3, "tint": c_blue,
        "font_size": 11,
        "requires": func(): return commands_run.get("petrine", 0) >= 1
                          or commands_run.get("peter", 0) >= 1,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  PETRINE KEYS                    │
              │  ░ one to bind, one to loose     │
              │  ░ given to Peter on the rock    │
              │  ░ passed hand to hand for       │
              │    two thousand years            │
              │  ░ Maya knows none of this.      │
              │  ░ Maya knows the keys are above │
              │    her head and unreachable.     │
              │  ░ that is enough.               │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 4, "tint": c_stone,
        "font_size": 11,
        "requires": func(): return commands_run.get("heat", 0) >= 1
                          or commands_run.get("sunday", 0) >= 1,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  HEAT · the Acadian summer       │
              │  ░ already at 6:42 AM            │
              │  ░ the doors are open            │
              │  ░ the cicadas have not          │
              │    started yet. they will.       │
              │  ░ the dress is wool blend.      │
              │  ░ she was told it would breathe │
              │  ░ wool does not.                │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 5, "tint": c_red_dim,
        "font_size": 10,
        "requires": func(): return commands_run.get("voltaire", 0) >= 1
                          or commands_run.get("candide", 0) >= 1,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  ░ VOLTAIRE elsewhere ░          │
              │  Frasier has the cassette.       │
              │  Dante's father underlined the   │
              │  garden line.                    │
              │  here, in the parish, Voltaire   │
              │  is the name on a banned list    │
              │  in the church library closet,   │
              │  three doors from where she      │
              │  kneels.                         │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 6, "tint": c_red,
        "font_size": 11,
        "requires": func(): return dress_touches >= 8 and banner_read,
        "ascii":
"""
              ╔══════════════════════════════════╗
              ║  ░ THE INHERITANCE COMPLETE ░    ║
              ║                                  ║
              ║  it is not the keys. it is not   ║
              ║  the crown. it is not the        ║
              ║  banner. it is not the carpet.   ║
              ║                                  ║
              ║  it is the dress.                ║
              ║                                  ║
              ║  ─ the system installs from      ║
              ║    the skin inward. ─            ║
              ╚══════════════════════════════════╝
"""
    })


# ── Mechanics ────────────────────────────────────────────────────
func _do_dress() -> void:
    dress_touches += 1
    hotspots_seen["hie_dress"] = true
    _refresh_tally()
    # A small sharp pinch — short high square
    _active_notes.append({"time":0.0,"freq":1100.0,"wave":"square",
        "atk":0.001,"dur":0.04,"rel":0.05})
    _active_notes.append({"time":0.0,"freq":220.0,"wave":"triangle",
        "atk":0.005,"dur":0.10,"rel":0.10})
    var line: String = DRESS_BITES[min(dress_touches - 1,
                                        DRESS_BITES.size() - 1)]
    _memorize("dress: " + line)
    status_label.text = line
    _log("[color=#e85060]· %s[/color]" % line)
    SaveSystem.mark_unlocked("vol5_dress_bites_seen")
    if dress_touches == 8:
        _log("[color=#ffd070]· ░░ THE DRESS IS THE HIEROPHANT ─ system installed.[/color]")
        SaveSystem.mark_unlocked("vol5_dress_is_hierophant")


func _do_keys() -> void:
    if not keys_touched:
        keys_touched = true
        hotspots_seen["hie_keys"] = true
        _refresh_tally()
        _memorize("crossed keys touched")
        status_label.text = "✠ one for heaven · one for earth · crossed."
        _log("[color=#ffd070]· ✠ crossed keys — Petrine, unreachable.[/color]")
        SaveSystem.mark_unlocked("vol5_keys_seen")
    _active_notes.append({"time":0.0,"freq":523.0,"wave":"sine",
        "atk":0.03,"dur":0.35,"rel":0.45})


func _do_crown() -> void:
    if not crown_touched:
        crown_touched = true
        hotspots_seen["hie_crown"] = true
        _refresh_tally()
        _memorize("triple crown touched")
        status_label.text = "▓▓▓ tiara — teaching · governing · sanctifying."
        _log("[color=#ffd070]· ▓▓▓ triple crown — three rings to pass.[/color]")
        SaveSystem.mark_unlocked("vol5_tiara_seen")
    # Three ascending tones
    _active_notes.append({"time":0.0,"freq":261.6,"wave":"sine",
        "atk":0.02,"dur":0.20,"rel":0.20})
    _active_notes.append({"time":0.0,"freq":329.6,"wave":"sine",
        "atk":0.02,"dur":0.20,"rel":0.20})
    _active_notes.append({"time":0.0,"freq":392.0,"wave":"sine",
        "atk":0.02,"dur":0.25,"rel":0.30})


func _do_maya() -> void:
    if not maya_touched:
        maya_touched = true
        hotspots_seen["hie_acolyte_maya"] = true
        _refresh_tally()
        _memorize("maya acolyte selected")
        status_label.text = "Maya · 7 · kneeling · dress biting · silent."
        _log("[color=#f8b8a0]· M · Maya · the acolyte on the left.[/color]")
    # Make the dress bite too — she IS the dress's host
    _do_dress()


func _do_y() -> void:
    if y_touched >= Y_REVEALS.size():
        status_label.text = "Y is identified. nothing more is offered."
        return
    y_touched += 1
    hotspots_seen["hie_acolyte_y"] = true
    _refresh_tally()
    _active_notes.append({"time":0.0,"freq":392.0,"wave":"triangle",
        "atk":0.02,"dur":0.18,"rel":0.20})
    var line: String = Y_REVEALS[y_touched - 1]
    _memorize("Y: " + line)
    status_label.text = line
    _log("[color=#f8e0b0]· Y · %s[/color]" % line)
    if y_touched >= Y_REVEALS.size():
        SaveSystem.mark_unlocked("vol5_y_identified")


func _do_window() -> void:
    window_segments += 1
    hotspots_seen["hie_rose_window"] = true
    _refresh_tally()
    var idx: int = (window_segments - 1) % WINDOW_COLORS.size()
    var color_name: String = WINDOW_COLORS[idx]
    _memorize("window segment %d : %s" % [window_segments, color_name])
    # Pitch by color
    var freqs := {"RED": 261.6, "BLUE": 329.6,
                  "YELLOW": 392.0, "GREEN": 440.0}
    var freq: float = float(freqs.get(color_name, 261.6))
    _active_notes.append({"time":0.0,"freq":freq,"wave":"sine",
        "atk":0.02,"dur":0.25,"rel":0.25})
    status_label.text = "rose window: segment %d · %s." % [
        window_segments, color_name]
    _log("[color=#a0b0e8]· ░ rose window segment %d : %s[/color]" %
         [window_segments, color_name])
    if window_segments == 8:
        _log("[color=#ffd070]· ░░ all 8 segments counted — 4 colors, twice.[/color]")
        SaveSystem.mark_unlocked("vol5_glass_colors_seen")


func _do_banner() -> void:
    banner_read = true
    hotspots_seen["hie_banner"] = true
    _refresh_tally()
    # The keystone chord — slow imperial fifth
    for f in [196.0, 293.7, 392.0]:
        _active_notes.append({"time":0.0,"freq":f,"wave":"sine",
            "atk":0.05,"dur":0.55,"rel":0.55})
    _memorize("AVDI ET TACE read")
    status_label.text = "AVDI · ET · TACE — hear, and be silent."
    _log("[color=#ffd070]· ░ KEYSTONE ─ AVDI · ET · TACE[/color]")
    _log("[color=#a87830]·   the chapter's command, to her and to you.[/color]")
    SaveSystem.mark_unlocked("vol5_audi_et_tace_known")


func _do_carpet() -> void:
    if carpet_read_stage >= CARPET_LINES.size():
        status_label.text = "the carpet has been read down through to the schedule."
        return
    carpet_read_stage += 1
    _refresh_tally()
    _active_notes.append({"time":0.0,"freq":175.0,"wave":"triangle",
        "atk":0.02,"dur":0.20,"rel":0.25})
    var line: String = CARPET_LINES[carpet_read_stage - 1]
    _memorize("carpet: " + line)
    status_label.text = line
    _log("[color=#e8d8a8]· carpet row %d · %s[/color]" %
         [carpet_read_stage, line])
    if carpet_read_stage >= CARPET_LINES.size():
        SaveSystem.mark_unlocked("vol5_carpet_read")


func _on_hotspot(hs: Dictionary) -> void:
    super(hs)
    var hs_id := str(hs.get("id",""))
    hotspots_seen[hs_id] = true
    _memorize("hotspot: " + hs_id)
    match hs_id:
        "hie_dress":         _do_dress()
        "hie_keys":          _do_keys()
        "hie_crown":         _do_crown()
        "hie_acolyte_maya":  _do_maya()
        "hie_acolyte_y":     _do_y()
        "hie_rose_window":   _do_window()
        "hie_banner":        _do_banner()
        _:
            status_label.text = "[ %s ]" % str(hs.get("interact", hs_id))


# ── Console commands ─────────────────────────────────────────────
func _on_command(text: String) -> void:
    var line := text.strip_edges().to_lower()
    console_input.text = ""
    if line == "":
        return
    _log("[color=#ffd070]> %s[/color]" % text)
    commands_run[line] = int(commands_run.get(line, 0)) + 1
    _memorize("typed: " + line)
    var parts := line.split(" ", false)
    var cmd := parts[0]

    match cmd:
        # Public
        "help", "?":
            _cmd_help()
        "dress", "bite":
            _do_dress()
        "keys":
            _do_keys()
        "crown", "tiara":
            _do_crown()
        "maya":
            _do_maya()
        "y":
            _do_y()
        "window", "rose":
            _do_window()
        "banner", "motto":
            _do_banner()
        "carpet":
            _do_carpet()
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
        # Hidden — motto components
        "avdi", "audi", "hear":
            _log("[color=#ffd070]  AVDI — hear what you are told.[/color]")
            _log("[color=#a87830]  she does. she has no choice.[/color]")
        "tace", "silent":
            _log("[color=#ffd070]  TACE — be silent. do not answer back.[/color]")
            _log("[color=#a87830]  she is. she has not been given language for the bite.[/color]")
        "et", "and":
            _log("[color=#a87830]  ET — the conjunction is the bind.[/color]")
        # Hidden — symbology
        "petrine", "peter":
            _log("[color=#a0b0e8]  Peter's keys: bind and loose.[/color]")
            _log("[color=#a87830]  unreachable above the rose window.[/color]")
        "rose", "glass":
            _log("[color=#a0b0e8]  8 segments · 4 colors · she counts to four.[/color]")
        "beatitudes", "eight":
            _log("[color=#a0b0e8]  eight blessings. eight segments. same count.[/color]")
        "sacraments", "seven":
            _log("[color=#a0b0e8]  seven sacraments plus baptism = 8.[/color]")
            _log("[color=#a87830]  the window has chosen its math.[/color]")
        "ecclesia", "reformanda":
            _log("[color=#ffd070]  ECCLESIA SEMPER REFORMANDA — always reforming.[/color]")
            if carpet_read_stage < 1: _do_carpet()
        "sanctifica", "anima", "christi":
            _log("[color=#a0b0e8]  ANIMA CHRISTI SANCTIFICA ME — sanctify me.[/color]")
            _log("[color=#a87830]  she hears SCRATCH. she would.[/color]")
            if carpet_read_stage < 2:
                while carpet_read_stage < 2: _do_carpet()
        "mass", "schedule":
            _log("[color=#ffd070]  DOMINICA MASS · 7 · 9 · 11[/color]")
            _log("[color=#a87830]  this chapter is before the 7. heat already up.[/color]")
            if carpet_read_stage < 3:
                while carpet_read_stage < 3: _do_carpet()
        # Hidden — body
        "itch", "scratch":
            _log("[color=#e85060]  she does not scratch. AVDI ET TACE applies.[/color]")
        "bite", "stiff":
            _do_dress()
        "sunday":
            _log("[color=#a87830]  Sunday at 6:42 AM. wool blend dress. cicadas pending.[/color]")
        "heat":
            _log("[color=#a87830]  Acadian summer. doors open for carpet airing.[/color]")
        # Hidden — people
        "companion", "acolyte":
            _do_y()
        "quent", "father_quent":
            _log("[color=#e8d8a8]  Father Quent · 34 · Acadian · wears the heat as a vestment.[/color]")
        "paul", "father_paul":
            _log("[color=#e8d8a8]  Father Paul · 58 · pastor · believes in patience.[/color]")
        "father":
            _log("[color=#e8d8a8]  two fathers. one believes in process, one in form.[/color]")
        "catechism":
            _log("[color=#ffd070]  age 7 · 12 · then she stops at 14.[/color]")
        # Hidden — places
        "acadian", "st_jude", "stjude":
            _log("[color=#e8d8a8]  St. Jude's Acadian Church · parish est. 1898.[/color]")
        # Cross-character
        "elicia", "priestess":
            _log("[color=#a09a8a]  Elicia is the adult-observer. Maya is the child-experiencer.[/color]")
            _log("[color=#7a7468]  same shape, different angle in time.[/color]")
        "frasier", "magician":
            _log("[color=#88c8d0]  Frasier's cathedral runs on rust. yours runs on incense.[/color]")
        "dante", "emperor":
            _log("[color=#c89060]  the vineyard is his. Quent's uncle runs it.[/color]")
            _log("[color=#a87040]  the 9am wine is Acadian '94. GAS STATION RED.[/color]")
        "nicola", "empress":
            _log("[color=#c8807a]  Nicola passes the parking lot in Vol6, alone.[/color]")
        "john", "fool":
            _log("[color=#c89868]  John never enters a church. the counter is his chapel.[/color]")
        "voltaire", "candide":
            _log("[color=#e85060]  on the banned list in the church library closet.[/color]")
            _log("[color=#a87830]  three doors from where she kneels.[/color]")
        _:
            if line == "tip":
                _log("[color=#a87830]  no tip. the collection plate comes later.[/color]")
            elif line == "rust_code.bbs":
                _log("[color=#e85060]  blocked at the parish firewall.[/color]")
            else:
                _log("[color=#5a3040]? unknown. try: help · banner · dress[/color]")


func _cmd_help() -> void:
    _log("[color=#ffd070]commands (visible):[/color]")
    _log("  [color=#ffe896]dress[/color]      — feel the dress bite")
    _log("  [color=#ffe896]keys[/color]       — touch the crossed keys")
    _log("  [color=#ffe896]crown[/color]      — touch the triple tiara")
    _log("  [color=#ffe896]maya[/color]       — be the kneeling acolyte")
    _log("  [color=#ffe896]y[/color]          — look at the other acolyte (3 reveals)")
    _log("  [color=#ffe896]window[/color]     — count rose-window segments")
    _log("  [color=#ffe896]banner[/color]     — read AVDI ET TACE (keystone)")
    _log("  [color=#ffe896]carpet[/color]     — read the three Latin rows")
    _log("  [color=#ffe896]recall[/color]     — discovery log")
    _log("  [color=#ffe896]count[/color]      — tallies")
    _log("  [color=#ffe896]look · listen · clear · exit[/color]")
    _log("[color=#a87830](some commands are unlisted. the parish keeps secrets.)[/color]")


func _cmd_memory() -> void:
    _log("[color=#ffd070]── memory · %d entries ──[/color]" % memory.size())
    var shown := 0
    for entry in memory:
        if shown >= 20:
            _log("[color=#a87830]  ... (%d more)[/color]" %
                 (memory.size() - shown))
            break
        _log("  [color=#e8d8a8]· %s[/color]" % entry)
        shown += 1


func _cmd_count() -> void:
    _log("[color=#ffd070]── tallies ────────────────[/color]")
    _log("  dress bites: [color=#e85060]%d / 8[/color]" % dress_touches)
    _log("  keys:        [color=#ffe896]%s[/color]" %
         ("touched" if keys_touched else "untouched"))
    _log("  crown:       [color=#ffe896]%s[/color]" %
         ("touched" if crown_touched else "untouched"))
    _log("  maya:        [color=#ffe896]%s[/color]" %
         ("acolyte" if maya_touched else "not yet"))
    _log("  Y:           [color=#e8d8a8]%d / %d reveals[/color]" %
         [y_touched, Y_REVEALS.size()])
    _log("  window:      [color=#a0b0e8]%d / 8 segments[/color]" % window_segments)
    _log("  banner:      [color=#ffd070]%s[/color]" %
         ("read" if banner_read else "unread"))
    _log("  carpet:      [color=#e8d8a8]%d / 3 rows[/color]" % carpet_read_stage)
    _log("  hotspots:    [color=#ffd070]%d[/color]" % hotspots_seen.size())
    _log("  commands run:[color=#ffd070] %d[/color]" % commands_run.size())


func _cmd_look() -> void:
    _log("[color=#e8d8a8]· St. Jude's parking lot. sun already up.[/color]")
    _log("[color=#e8d8a8]· crossed keys above the rose window.[/color]")
    _log("[color=#e8d8a8]· triple tiara on the figure between her and the keys.[/color]")
    _log("[color=#e8d8a8]· two kneelers: M (her) and Y (the other).[/color]")
    _log("[color=#e8d8a8]· carpet underfoot. three latin rows woven in.[/color]")
    _log("[color=#a87830]· AVDI ET TACE banner across the lintel.[/color]")
    _log("[color=#e85060]· the dress. always the dress.[/color]")


func _cmd_listen() -> void:
    _log("[color=#e8d8a8]· no cicadas yet. they will start at 7.[/color]")
    _log("[color=#e8d8a8]· Father Paul rehearsing the kyrie under his breath.[/color]")
    _log("[color=#e8d8a8]· car doors closing. the parishioners arriving.[/color]")
    _log("[color=#a87830]· the carpet absorbing every footstep.[/color]")
    _log("[color=#a87830]· her own breath, slightly held against the wool.[/color]")


func _refresh_tally() -> void:
    if tally_btn != null:
        tally_btn.text = "  ✠ bites %d/8 · window %d/8 · Y %d/%d  " % [
            dress_touches, window_segments,
            y_touched, Y_REVEALS.size()]


func _memorize(entry: String) -> void:
    memory.append(entry)
    if memory.size() > 200:
        memory.remove_at(0)


func _log(line: String) -> void:
    if console_log != null:
        console_log.append_text(line + "\n")


# ── Process / heat shimmer / audio-reactive ASCII pulse ──────────
func _process(delta: float) -> void:
    super(delta)
    heat_phase = fmod(heat_phase + delta * 0.8, TAU)
    if card_rect != null:
        # Heat shimmer + slight red bias proportional to dress_touches
        var shim := 1.0 + sin(heat_phase) * 0.018
        var red_bias := dress_touches * 0.012
        card_rect.modulate = Color(
            1.0 * shim + red_bias,
            0.96 * shim,
            0.92 * shim - red_bias * 0.5)
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
        var phase = tableau_pulse * 1.7 + idx * 0.41
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
            _do_dress()
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
