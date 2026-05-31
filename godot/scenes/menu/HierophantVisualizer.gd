extends "res://scenes/menu/TarotVisualizerBase.gd"
## HierophantVisualizer — Sweaty Sunday Sermonettes.
##
## REBUILD for the new sketch-diagram art. Setting: St. Jude's
## Acadian Church, Sunday morning, before brunch. The new card is
## a multi-vignette autopsy of inherited authority — Father Quentin
## Paul on the throne flanked by TRADITION and CONFORMITY pillars,
## four kneelers around the Rosh floor symbol, the D'Ambrosio's
## corner booth where Quentin takes BLACK COFFEE NEAT and tells
## Antonio: "Just remember who your friends are."
##
## Significantly different POV from the prior Maya child-experiencer
## card — this is the AUTHORITY's surface, with the child experience
## reduced to one of four multi-witness panels.
##
##   • CARD HOTSPOTS — seven rects on the painted Hierophant:
##       SERMON      Quentin on the throne (center)
##       TRADITION   the left pillar
##       CONFORMITY  the right pillar
##       ROSH        the floor symbol (ritual binding sigil)
##       ACOLYTES    the four kneelers — cycles identity per click
##       BOOTH       the D'Ambrosio's corner-booth panel (Antonio
##                   warning, BLACK COFFEE NEAT, Quentin's spot)
##       WITNESS     the [MULTI-WITNESS POV] panels (right side)
##
##   • BBS CONSOLE — `quentin@stjude:~$` prompt. Public commands cover
##     all mechanics. Hidden lore: rosh · binding · ritual · pillars ·
##     antonio · friends · uncertain · maya · jimmy · john · ribbed ·
##     witness · sweaty · sermonette · acadian · sunday · brunch ·
##     phone · park · church_vibe · courtroom · bones · bleached ·
##     demon · persistent_demon · vignette · four_vignette · voltaire ·
##     candide · cross-character routes.

# ── Game state ───────────────────────────────────────────────────
var sermon_count: int = 0
var tradition_touched: bool = false
var conformity_touched: bool = false
var rosh_invocations: int = 0      # the floor symbol — 0..7 ramp
var acolyte_idx: int = 0           # 0..3 which kneeler identified
var booth_read: bool = false
var witness_idx: int = 0           # 0..3 cycle through 4 vignettes
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

# Four kneelers around the Rosh floor symbol — each is one of the
# named characters being inducted into the system.
const ACOLYTES := [
    "north kneeler · MAYA · seven · the dress still bites · she does not look up",
    "east kneeler · ANTONIO · forty-three · he is here because Quentin said to be",
    "south kneeler · JIMMY · age-uncertain · he came in late · he is sweating",
    "west kneeler · JOHN · timeless · the cook · the wiper · the dog at his side",
]

# Multi-witness POV cycle — each click on the WITNESS panel rotates
# through one of the four vignettes that surround the central scene.
const WITNESSES := [
    "[VIGNETTE 1 · official reception & archive] Press number. Sermon parsed. Theorpter. Trees. Boxed. Selling.",
    "[VIGNETTE 2 · sensory · skin] Heavy suit in Texas heat. Black engraved sweat. Eye lid most. The cologne is cologne.",
    "[VIGNETTE 3 · persistent demon UI] One demon sits in the rafters and tracks who confesses what. The demon is not banished here. The cathedral runs on demon.",
    "[VIGNETTE 4 · D'Ambrosio's corner booth] BLACK COFFEE NEAT. Quentin orders before he arrives. The friends remark is for Antonio. The remark is for the player.",
]

# Rosh invocation reveals — each click on the floor symbol unfolds
# the binding ritual one step further.
const ROSH_REVEALS := [
    "the Rosh sigil glows once. ritual binding initiated.",
    "the four kneelers lean in. their dresses bite. their suits sweat.",
    "the pillars TRADITION and CONFORMITY shake very slightly.",
    "Quentin speaks. you cannot hear what he says. the kneelers can.",
    "the sermon ends. nobody stood up. nobody knelt down. it was already done.",
    "the binding holds. the binding has always held.",
    "the Rosh sigil dims. it does not need to glow to remain bound.",
]


func _init() -> void:
    _card_path  = "res://assets/gallery/hierophant.png"
    # Composition was regenerated from the new Quentin sketch art via
    # img2ansiblocks.py + build_arcana_card.py — safe to wire now.
    _composition_path = "hierophant_card"
    _hooks_path = "res://resources/puzzle_hooks/hierophant.json"
    _ambient_audio_path = "res://assets/audio/bgm/vol5_ambient.ogg"
    # Bleached-bone whites + courtroom blues per the CHURCH_VIBE.EXE
    # annotation on the card.
    C_BG = Color(0.06, 0.07, 0.09)
    C_GOLD = Color(0.92, 0.90, 0.82)        # bleached bone
    C_GOLD_HI = Color(1.0, 0.98, 0.90)       # bone-hi
    C_TEXT = Color(0.78, 0.82, 0.90)         # courtroom blue
    C_TEXT_DIM = Color(0.36, 0.40, 0.50)


func _build_chrome() -> void:
    super()
    _build_bottom_strip()
    _build_card_hotspots()


# Per-region hotspots on the new Hierophant sketch card.
# Coordinates are normalized to the painted-card area; the wrapper
# scales them to the actual on-screen card size.
func _build_card_hotspots() -> void:
    if card_rect == null: return
    var defs := [
        ["sermon",     Rect2(0.40, 0.30, 0.20, 0.40), "approach the sermon",       _do_sermon],
        ["tradition",  Rect2(0.32, 0.20, 0.05, 0.55), "TRADITION pillar",          _do_tradition],
        ["conformity", Rect2(0.61, 0.20, 0.05, 0.55), "CONFORMITY pillar",         _do_conformity],
        ["rosh",       Rect2(0.40, 0.70, 0.20, 0.18), "invoke the Rosh sigil",     _do_rosh],
        ["acolytes",   Rect2(0.32, 0.62, 0.34, 0.28), "kneeler ring",              _do_acolytes],
        ["booth",      Rect2(0.04, 0.62, 0.18, 0.24), "D'Ambrosio's corner booth", _do_booth],
        ["witness",    Rect2(0.66, 0.08, 0.30, 0.66), "MULTI-WITNESS POV",         _do_witness],
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
        sb.bg_color = Color(0.85, 0.92, 1.0, 0.0)
        sb.border_color = Color(0.85, 0.92, 1.0, 0.0)
        sb.set_border_width_all(1)
        btn.add_theme_stylebox_override("normal", sb)
        var bsh := sb.duplicate() as StyleBoxFlat
        bsh.bg_color = Color(0.85, 0.92, 1.0, 0.16)
        bsh.border_color = Color(1.0, 0.98, 0.90, 0.80)
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
    bps.bg_color = Color(0.04, 0.05, 0.08, 0.88)
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
        Color(0.85, 0.88, 0.95))
    vbox.add_child(console_log)

    var inrow := HBoxContainer.new()
    inrow.add_theme_constant_override("separation", 4)
    var prompt := Label.new()
    prompt.text = "quentin@stjude:~$ "
    prompt.add_theme_color_override("font_color", C_GOLD_HI)
    prompt.add_theme_font_size_override("font_size", 12)
    inrow.add_child(prompt)
    console_input = LineEdit.new()
    console_input.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    console_input.add_theme_color_override("font_color",
        Color(0.95, 0.95, 0.92))
    console_input.text_submitted.connect(_on_command)
    inrow.add_child(console_input)
    vbox.add_child(inrow)

    var actrow := HBoxContainer.new()
    actrow.add_theme_constant_override("separation", 12)
    vbox.add_child(actrow)

    tally_btn = Button.new()
    tally_btn.text = "  ✠ sermon 0 · rosh 0/7 · witnesses 0/4 · acolytes 0/4  "
    tally_btn.add_theme_color_override("font_color", C_GOLD_HI)
    tally_btn.add_theme_font_size_override("font_size", 11)
    var wbs := StyleBoxFlat.new()
    wbs.bg_color = Color(0.18, 0.20, 0.30, 0.6)
    wbs.border_color = C_GOLD
    wbs.set_border_width_all(1)
    tally_btn.add_theme_stylebox_override("normal", wbs)
    var wbh := wbs.duplicate() as StyleBoxFlat
    wbh.bg_color = Color(0.32, 0.36, 0.50, 0.78)
    wbh.border_color = C_GOLD_HI
    tally_btn.add_theme_stylebox_override("hover", wbh)
    tally_btn.pressed.connect(_do_sermon)
    tally_btn.tooltip_text = "click card regions for distinct mechanics"
    actrow.add_child(tally_btn)

    status_label = Label.new()
    status_label.text = "click the card · sermon · pillars · rosh · acolytes · booth · witness"
    status_label.add_theme_color_override("font_color",
        Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.80))
    status_label.add_theme_font_size_override("font_size", 10)
    status_label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    status_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    actrow.add_child(status_label)

    _log("[color=#e8e0c8]> V · THE HIEROPHANT · vol.5 ch.5 · St. Jude's Acadian Church[/color]")
    _log("[color=#6878a0]> [SYSTEM STATUS: ACADIAN CHURCH / BRUNCH / PHONE / PARK][/color]")
    _log("[color=#e8e0c8]> SWEATY SUNDAY SERMONETTES — already running.[/color]")
    _log("[color=#6878a0]> Quentin says: \"Just remember who your friends are.\"[/color]")
    _log("[color=#6878a0]> type [color=#fffeec]help[/color] · the binding does not require your participation.[/color]")

    console_input.grab_focus()


# ── Tableau registration ─────────────────────────────────────────
func _build_thematic_widget() -> void:
    var c_bone := Color(0.94, 0.90, 0.78, 0.95)
    var c_bone_dim := Color(0.55, 0.52, 0.45, 0.85)
    var c_bone_hot := Color(1.0, 0.98, 0.88, 1.0)
    var c_blue := Color(0.55, 0.65, 0.88, 0.95)
    var c_blue_dim := Color(0.28, 0.34, 0.52, 0.85)
    var c_red := Color(0.85, 0.30, 0.30, 0.92)
    var c_demon := Color(0.50, 0.18, 0.22, 0.85)
    var c_child := Color(0.95, 0.78, 0.70, 0.95)
    var c_pillar := Color(0.72, 0.68, 0.60, 0.90)

    # ────────────────────────────────────────────────────────────
    # NORTH — what hangs above the sermon
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.NORTH, "row": 0, "tint": c_bone,
        "font_size": 13, "requires": null,
        "ascii":
"""
       ╔═══════════════════════════════════════════════════════╗
       ║   V · THE HIEROPHANT · SWEATY SUNDAY SERMONETTES     ║
       ║       [SYSTEM STATUS: CHURCH · BRUNCH · PHONE · PARK] ║
       ╚═══════════════════════════════════════════════════════╝
        ─── inherited authority · running on Sunday at idle ───
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 1, "tint": c_pillar,
        "font_size": 11,
        "requires": null,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │      TRADITION   |   CONFORMITY  │
              │       ▓▓▓▓▓▓▓    |    ▓▓▓▓▓▓▓     │
              │       ▓▓▓▓▓▓▓    |    ▓▓▓▓▓▓▓     │
              │       ▓▓▓▓▓▓▓    |    ▓▓▓▓▓▓▓     │
              │  ─── two pillars · one chair ───  │
              │  ─── the chair holds the man ───  │
              │  ─── the man holds the chair ───  │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 2, "tint": c_blue,
        "font_size": 12,
        "requires": func(): return sermon_count >= 1,
        "ascii":
"""
              ╔══════════════════════════════════════╗
              ║   CHURCH_VIBE.EXE                    ║
              ║   ─ palette: bleached-bone whites ─  ║
              ║   ─ secondary: courtroom blues ─     ║
              ║   ─ font: ringed neat ─              ║
              ║   ─ runtime: Sundays from 6:42 AM ─  ║
              ║   ─ exit code: still pending ─       ║
              ╚══════════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 3, "tint": c_demon,
        "font_size": 11,
        "requires": func(): return commands_run.get("demon", 0) >= 1
                          or commands_run.get("persistent_demon", 0) >= 1,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  [PERSISTENT_DEMON_UI]           │
              │  one demon sits in the rafters.  │
              │  it tracks who confesses what.   │
              │  it is not banished here.        │
              │  the cathedral RUNS on demon.    │
              │  Frasier banished his two.       │
              │  Quentin keeps his.              │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 4, "tint": c_bone_hot,
        "font_size": 11,
        "requires": func(): return rosh_invocations >= 4,
        "ascii":
"""
              ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
            ░░ THE BINDING HOLDS · ROSH @ 4/7  ░░
            ░░ the sigil dimmed once but held.  ░░
            ░░ the four kneelers do not stand.  ░░
            ░░ they would. they don't.          ░░
              ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 5, "tint": c_bone,
        "font_size": 11,
        "requires": func(): return witness_idx >= 3,
        "ascii":
"""
              ╔══════════════════════════════════╗
              ║   VN_DESIGN_NOTES — FOUR        ║
              ║   VIGNETTE STRUCTURE             ║
              ║   ─ vignette 1: reception        ║
              ║   ─ vignette 2: sensory          ║
              ║   ─ vignette 3: persistent_demon ║
              ║   ─ vignette 4: corner booth     ║
              ║   ─ all four observed ─ COMPASS  ║
              ║     V-node marked complete       ║
              ╚══════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 6, "tint": c_bone_hot,
        "font_size": 11,
        "requires": func(): return hotspots_seen.size() >= 6,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  ░ KEYSTONE · HIEROPHANT ░       │
              │  AVDI ET TACE has been inherited │
              │  whole, untranslated, by every   │
              │  card in this deck except one.   │
              │  the exception is THE FOOL.      │
              │  the Fool refuses translation    │
              │  by refusing the language.       │
              └──────────────────────────────────┘
"""
    })

    # ────────────────────────────────────────────────────────────
    # SOUTH — what kneels below / floor / bodies
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.SOUTH, "row": 0, "tint": c_blue_dim,
        "font_size": 12, "requires": null,
        "ascii":
"""
       ════════════ THE FLOOR · St. Jude's ════════════════════
            ░ red runner ░ four kneelers ░ Rosh sigil at        ░
            ░ centre ░ the wood smells of last week's wax ░     ░
            ░ AVDI ET TACE woven into the carpet edges ░        ░
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 1, "tint": c_child,
        "font_size": 11,
        "requires": func(): return acolyte_idx >= 1,
        "ascii":
"""
              ┌────────────────────────────────┐
              │  NORTH kneeler · MAYA · 7      │
              │  ░ the dress still bites       │
              │  ░ she does not look up        │
              │  ░ she has not moved           │
              │  ░ this is her chapter 5       │
              │    from a different angle      │
              └────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 2, "tint": c_bone,
        "font_size": 11,
        "requires": func(): return acolyte_idx >= 2,
        "ascii":
"""
              ┌────────────────────────────────┐
              │  EAST kneeler · ANTONIO · 43   │
              │  ░ he is here because Quentin  │
              │    said to be                  │
              │  ░ his hands are folded wrong  │
              │  ░ he is rehearsing the wreck  │
              │    that is coming in vol7      │
              └────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 3, "tint": c_red,
        "font_size": 11,
        "requires": func(): return acolyte_idx >= 3,
        "ascii":
"""
              ┌────────────────────────────────┐
              │  SOUTH kneeler · JIMMY · ?     │
              │  ░ age-uncertain · came late   │
              │  ░ he is sweating              │
              │  ░ his hands are not folded    │
              │  ░ the saboteur kneels too     │
              │  ░ but reserves the right to   │
              │    sabotage the kneeling       │
              └────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 4, "tint": c_bone_dim,
        "font_size": 11,
        "requires": func(): return acolyte_idx >= 4,
        "ascii":
"""
              ┌────────────────────────────────┐
              │  WEST kneeler · JOHN · timeless│
              │  ░ the cook · the wiper        │
              │  ░ the dog at his side         │
              │  ░ the only one who could      │
              │    have refused. who chose     │
              │    not to. who chose to wipe   │
              │    the counter on this side    │
              │    of the door instead.        │
              └────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 5, "tint": c_bone_hot,
        "font_size": 11,
        "requires": func(): return rosh_invocations >= 7,
        "ascii":
"""
              ╔══════════════════════════════════╗
              ║  ░ ROSH FULLY INVOKED ░          ║
              ║                                  ║
              ║  the sigil dims. the binding     ║
              ║  holds. the four do not stand.   ║
              ║                                  ║
              ║  the binding was never sealed    ║
              ║  by the ritual. the binding was  ║
              ║  the showing-up.                 ║
              ╚══════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 6, "tint": c_red,
        "font_size": 11,
        "requires": func(): return booth_read,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  D'AMBROSIO'S corner booth       │
              │  ░ BLACK COFFEE NEAT             │
              │  ░ ordered before he arrives     │
              │  ░ the waitress writes 'Quentin' │
              │    without asking the name       │
              │  ░ the booth is reserved by      │
              │    long-standing fact            │
              └──────────────────────────────────┘
              ░ "Just remember who your friends ░
              ░ are, Antonio. In these          ░
              ░ uncertain times."               ░
"""
    })

    # ────────────────────────────────────────────────────────────
    # EAST — multi-witness POV / forward
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.EAST, "row": 0, "tint": c_blue,
        "font_size": 11, "requires": null,
        "ascii":
"""

         ┌── [MULTI-WITNESS POV] · OFFICIAL ──────┐
         │  press number                          │
         │  sermon parsed                         │
         │  Theorpter · trees · boxed             │
         │  selling smelock                       │
         │  ─ archive accepts ─                   │
         └────────────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 1, "tint": c_blue,
        "font_size": 11,
        "requires": func(): return witness_idx >= 1,
        "ascii":
"""

         ┌── [MULTI-WITNESS POV] · SENSORY ───────┐
         │  Heavy suit in Texas heat.             │
         │  Black engraved sweat. Saliva-soaked   │
         │  collar. Eye lid most. The cologne is  │
         │  cologne and nothing else.             │
         │  ─ body receives ─                     │
         └────────────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 2, "tint": c_demon,
        "font_size": 11,
        "requires": func(): return witness_idx >= 2,
        "ascii":
"""

         ┌── [MULTI-WITNESS POV] · DEMON ─────────┐
         │  one demon in the rafters tracks       │
         │  every confession by name.             │
         │  the cathedral RUNS on the demon.      │
         │  Frasier banished both his demons.     │
         │  Quentin keeps his. it knows the cost. │
         │  ─ ledger accumulates ─                │
         └────────────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 3, "tint": c_red,
        "font_size": 11,
        "requires": func(): return witness_idx >= 3,
        "ascii":
"""

         ┌── [MULTI-WITNESS POV] · BOOTH ─────────┐
         │  BLACK COFFEE NEAT — ordered ahead.    │
         │  "Just remember who your friends are." │
         │  the line is for ANTONIO.              │
         │  the line is also for the player.      │
         │  Antonio kneels. the line lands.       │
         │  ─ binding sealed ─                    │
         └────────────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 4, "tint": c_bone_hot,
        "font_size": 11,
        "requires": func(): return commands_run.get("emperor", 0) >= 1
                          or commands_run.get("dante", 0) >= 1,
        "ascii":
"""

              ┌──────────────────────────────────┐
              │  ░ cross-card · EMPEROR ░        │
              │  the Acadian vineyard is Dante's │
              │  on paper. Quentin's uncle runs  │
              │  it. Quentin says the 9am wine.  │
              │  Dante signs the lease.          │
              │  Quentin pours the lease.        │
              │  the wine is the same wine.      │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 5, "tint": c_red,
        "font_size": 11,
        "requires": func(): return commands_run.get("antonio", 0) >= 1
                          or commands_run.get("chariot", 0) >= 1,
        "ascii":
"""

              ┌──────────────────────────────────┐
              │  ░ cross-card · CHARIOT ░        │
              │  Antonio is Chariot's POV.       │
              │  the wreck is ahead of him.      │
              │  Quentin made the phone call     │
              │  that left him here this morning │
              │  instead of behind that wheel.   │
              │  the binding bought time.        │
              │  the binding costs.              │
              └──────────────────────────────────┘
"""
    })

    # ────────────────────────────────────────────────────────────
    # WEST — past / Acadian inheritance / books / cards
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.WEST, "row": 0, "tint": c_bone,
        "font_size": 11, "requires": null,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  ST. JUDE's ACADIAN CHURCH       │
              │  ─── parish est. 1898 ───        │
              │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
              │  ▓ Father Paul (pastor)          │
              │  ▓ Father Quentin (deacon)       │
              │  ▓ Acadian Vineyard donates wine │
              │  ▓ carpet replaced 1976          │
              │  ▓ next replacement: never       │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 1, "tint": c_pillar,
        "font_size": 11,
        "requires": func(): return tradition_touched,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  ░ PILLAR · TRADITION ░           │
              │  what came before is the chair.  │
              │  the chair does not change.      │
              │  the man on the chair changes.   │
              │  the chair forgets him within    │
              │  a generation. the chair         │
              │  remains.                        │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 2, "tint": c_pillar,
        "font_size": 11,
        "requires": func(): return conformity_touched,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  ░ PILLAR · CONFORMITY ░          │
              │  the same shape every Sunday.    │
              │  the kneelers shaped by the      │
              │  shape they kneel into.          │
              │  the door open from one side.    │
              │  the door not noticed by those   │
              │  shaped to face the throne.      │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 3, "tint": c_blue,
        "font_size": 11,
        "requires": func(): return commands_run.get("voltaire", 0) >= 1
                          or commands_run.get("candide", 0) >= 1,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  ░ VOLTAIRE · banned shelf ░     │
              │  CANDIDE is on the parish's      │
              │  banned-book closet list.        │
              │  three doors from where Maya     │
              │  kneels. Quentin signed the      │
              │  list. Father Paul did not.      │
              │  the list disagrees with         │
              │  itself, quietly.                │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 4, "tint": c_bone_dim,
        "font_size": 11,
        "requires": func(): return commands_run.get("priestess", 0) >= 1
                          or commands_run.get("elicia", 0) >= 1,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  ░ cross-card · PRIESTESS ░       │
              │  Elicia has a tape of this       │
              │  sermon. Quentin did not consent │
              │  to be recorded. she did not     │
              │  ask. her ethic permits this.    │
              │  she would tell you so.          │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 5, "tint": c_blue,
        "font_size": 11,
        "requires": func(): return commands_run.get("frasier", 0) >= 1
                          or commands_run.get("magician", 0) >= 1,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  ░ cross-card · MAGICIAN ░        │
              │  Frasier's warehouse is a temple │
              │  with rust for stained glass.    │
              │  this temple has stained glass   │
              │  with rust for rust.             │
              │  one chose to build his temple.  │
              │  the other inherited his to run. │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 6, "tint": c_red,
        "font_size": 11,
        "requires": func(): return booth_read and witness_idx >= 3,
        "ascii":
"""
              ╔══════════════════════════════════╗
              ║  ░ THE FRIENDS REMARK ░          ║
              ║                                  ║
              ║  Antonio hears it inside the     ║
              ║  sermon. it reads as benediction.║
              ║                                  ║
              ║  the player hears it outside.    ║
              ║  it reads as threat.             ║
              ║                                  ║
              ║  both readings are correct.      ║
              ║  the line is doing both jobs.    ║
              ╚══════════════════════════════════╝
"""
    })


# ── Mechanics ────────────────────────────────────────────────────
func _do_sermon() -> void:
    sermon_count += 1
    hotspots_seen["sermon"] = true
    _refresh_tally()
    # Quentin's voice = mid-range sustained tone
    _active_notes.append({"time":0.0,"freq":196.0,"wave":"sine",
        "atk":0.04,"dur":0.45,"rel":0.55})
    _memorize("sermon #%d" % sermon_count)
    var lines := [
        "Quentin clears his throat. the kneelers do not move.",
        "Quentin speaks. it is in Latin. it does not need to be heard.",
        "Quentin pauses. the pause does the work the words can't.",
        "Quentin smiles slightly. somebody in the back coughs anyway.",
        "Quentin says 'AVDI ET TACE.' Maya hears SCRATCH again. she does not.",
        "Quentin says 'BLESSED ARE WE.' the demon in the rafters takes a note.",
    ]
    var i: int = min(sermon_count - 1, lines.size() - 1)
    status_label.text = lines[i]
    _log("[color=#fffeec]· sermon %d · %s[/color]" % [sermon_count, lines[i]])
    if sermon_count == 1:
        SaveSystem.mark_unlocked("vol5_sermon_attended")


func _do_tradition() -> void:
    if not tradition_touched:
        tradition_touched = true
        hotspots_seen["tradition"] = true
        _refresh_tally()
        _memorize("TRADITION touched")
        status_label.text = "TRADITION — the chair, not the man."
        _log("[color=#c8c4b0]· ▓ TRADITION pillar touched · the chair, not the man.[/color]")
        SaveSystem.mark_unlocked("vol5_pillar_tradition")
    _active_notes.append({"time":0.0,"freq":146.8,"wave":"sawtooth",
        "atk":0.03,"dur":0.35,"rel":0.40})
    if tradition_touched and conformity_touched:
        _log("[color=#fffeec]· ░░ BOTH PILLARS — the throne is bound.[/color]")
        SaveSystem.mark_unlocked("vol5_hierophant_throne_bound")


func _do_conformity() -> void:
    if not conformity_touched:
        conformity_touched = true
        hotspots_seen["conformity"] = true
        _refresh_tally()
        _memorize("CONFORMITY touched")
        status_label.text = "CONFORMITY — the shape they kneel into."
        _log("[color=#c8c4b0]· ▓ CONFORMITY pillar touched · the shape they kneel into.[/color]")
        SaveSystem.mark_unlocked("vol5_pillar_conformity")
    _active_notes.append({"time":0.0,"freq":164.8,"wave":"sawtooth",
        "atk":0.03,"dur":0.35,"rel":0.40})
    if tradition_touched and conformity_touched:
        _log("[color=#fffeec]· ░░ BOTH PILLARS — the throne is bound.[/color]")
        SaveSystem.mark_unlocked("vol5_hierophant_throne_bound")


func _do_rosh() -> void:
    if rosh_invocations >= ROSH_REVEALS.size():
        status_label.text = "the Rosh sigil has shown what it shows."
        return
    rosh_invocations += 1
    hotspots_seen["rosh"] = true
    _refresh_tally()
    # Low sub-bass + sustained mid — ritual chord
    _active_notes.append({"time":0.0,"freq":98.0,"wave":"sawtooth",
        "atk":0.04,"dur":0.55,"rel":0.60})
    _active_notes.append({"time":0.0,"freq":196.0,"wave":"sine",
        "atk":0.04,"dur":0.50,"rel":0.55})
    var line: String = ROSH_REVEALS[rosh_invocations - 1]
    _memorize("Rosh #%d · %s" % [rosh_invocations, line])
    status_label.text = line
    _log("[color=#a8b8d8]· ✠ rosh %d/7 · %s[/color]" % [rosh_invocations, line])
    if rosh_invocations >= ROSH_REVEALS.size():
        SaveSystem.mark_unlocked("vol5_rosh_binding_complete")


func _do_acolytes() -> void:
    if acolyte_idx >= ACOLYTES.size():
        status_label.text = "all four kneelers identified."
        return
    acolyte_idx += 1
    hotspots_seen["acolytes"] = true
    _refresh_tally()
    _active_notes.append({"time":0.0,"freq":293.7,"wave":"triangle",
        "atk":0.02,"dur":0.20,"rel":0.25})
    var line: String = ACOLYTES[acolyte_idx - 1]
    _memorize("acolyte · " + line)
    status_label.text = line
    _log("[color=#e8d0c0]· kneeler %d/4 · %s[/color]" % [acolyte_idx, line])
    if acolyte_idx == ACOLYTES.size():
        _log("[color=#fffeec]· ░ all four kneelers named — the ring is complete.[/color]")
        SaveSystem.mark_unlocked("vol5_acolyte_ring_complete")


func _do_booth() -> void:
    if not booth_read:
        booth_read = true
        hotspots_seen["booth"] = true
        _refresh_tally()
        _memorize("D'Ambrosio's corner booth · BLACK COFFEE NEAT")
        status_label.text = "BLACK COFFEE NEAT · Quentin's spot · the line lands on Antonio."
        _log("[color=#e85060]· ☕ D'Ambrosio's booth · BLACK COFFEE NEAT · Quentin's spot.[/color]")
        _log("[color=#c84050]·   \"Just remember who your friends are, Antonio. In these[/color]")
        _log("[color=#c84050]·    uncertain times.\"[/color]")
        SaveSystem.mark_unlocked("vol5_booth_warning")
    # Coffee cup tap
    _active_notes.append({"time":0.0,"freq":640.0,"wave":"square",
        "atk":0.001,"dur":0.05,"rel":0.06})


func _do_witness() -> void:
    if witness_idx >= WITNESSES.size():
        status_label.text = "all four witnesses seen."
        return
    witness_idx += 1
    hotspots_seen["witness"] = true
    _refresh_tally()
    _active_notes.append({"time":0.0,"freq":440.0 + witness_idx * 30,
        "wave":"sine","atk":0.02,"dur":0.18,"rel":0.20})
    var line: String = WITNESSES[witness_idx - 1]
    _memorize("witness " + str(witness_idx) + " · " + line)
    status_label.text = "witness %d/4 → next vignette." % witness_idx
    _log("[color=#a8b8d8]· %s[/color]" % line)
    if witness_idx == WITNESSES.size():
        _log("[color=#fffeec]· ░ all four vignettes observed — COMPASS V-node ready.[/color]")
        SaveSystem.mark_unlocked("vol5_hierophant_four_vignettes")


func _on_hotspot(hs: Dictionary) -> void:
    super(hs)
    var hs_id := str(hs.get("id",""))
    hotspots_seen[hs_id] = true
    _memorize("hotspot: " + hs_id)
    status_label.text = "[ %s ]" % str(hs.get("interact", hs_id))


# ── Console commands ─────────────────────────────────────────────
func _on_command(text: String) -> void:
    var line := text.strip_edges().to_lower()
    console_input.text = ""
    if line == "":
        return
    _log("[color=#fffeec]> %s[/color]" % text)
    commands_run[line] = int(commands_run.get(line, 0)) + 1
    _memorize("typed: " + line)
    var parts := line.split(" ", false)
    var cmd := parts[0]

    match cmd:
        # Public
        "help", "?":
            _cmd_help()
        "sermon", "preach":
            _do_sermon()
        "tradition":
            _do_tradition()
        "conformity":
            _do_conformity()
        "pillars":
            if not tradition_touched: _do_tradition()
            if not conformity_touched: _do_conformity()
        "rosh", "binding", "invoke":
            _do_rosh()
        "acolytes", "kneelers", "kneeler", "ring":
            _do_acolytes()
        "booth", "coffee", "neat":
            _do_booth()
        "witness", "vignette", "witnesses":
            _do_witness()
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
        # Hidden — system
        "sweaty", "sermonette", "sermonettes":
            _log("[color=#e8e0c8]  sweaty sunday sermonette · 7:00 AM · doors open ↓[/color]")
        "acadian", "st_jude", "stjude", "church":
            _log("[color=#a8b8d8]  St. Jude's Acadian Church · est. 1898.[/color]")
        "brunch":
            _log("[color=#a8b8d8]  status: BRUNCH — Quentin will be in his booth by 9.[/color]")
        "phone":
            _log("[color=#a8b8d8]  status: PHONE — the call to Antonio was placed 06:18.[/color]")
        "park":
            _log("[color=#a8b8d8]  status: PARK — the lot fills first. the lot empties last.[/color]")
        "system_status":
            _log("[color=#a8b8d8]  CHURCH · BRUNCH · PHONE · PARK — all four active.[/color]")
        "church_vibe", "vibe":
            _log("[color=#fffeec]  CHURCH_VIBE.EXE · bleached-bone whites · courtroom blues[/color]")
        "bones", "bleached", "white":
            _log("[color=#fffeec]  the cathedral wears bleached bone. it's a colour, not a metaphor. mostly.[/color]")
        "blue", "courtroom":
            _log("[color=#a8b8d8]  the blue is from photo references of municipal courtrooms.[/color]")
        # Hidden — ritual
        "ritual":
            _do_rosh()
        "demon", "persistent_demon":
            _log("[color=#a85050]  one demon · rafters · ledger of every confession.[/color]")
            _log("[color=#7a3838]  Frasier banished his two. Quentin keeps his one.[/color]")
        "vignette", "four_vignette", "vignettes":
            _do_witness()
        # Hidden — people
        "quentin":
            _log("[color=#fffeec]  Father Quentin Paul · 34 · Acadian · wears the heat as vestment.[/color]")
            _log("[color=#c8c4b0]  has not banished his demon. is not interested in banishing it.[/color]")
        "paul":
            _log("[color=#c8c4b0]  Father Paul · 58 · pastor · believes in patience.[/color]")
            _log("[color=#a89c80]  did not sign the banned-book list.[/color]")
        "antonio":
            _log("[color=#e85060]  Antonio D'Ambrosio · 43 · Dante's nephew · Chariot POV.[/color]")
            _log("[color=#c84050]  the friends remark lands on him. it lands on you too.[/color]")
        "friends":
            _log("[color=#e85060]  \"Just remember who your friends are, Antonio.[/color]")
            _log("[color=#c84050]   In these uncertain times.\"[/color]")
            _log("[color=#7a3030]  the line does two jobs simultaneously.[/color]")
        "uncertain":
            _log("[color=#c84050]  uncertain times — manufactured uncertainty, in this case.[/color]")
        "maya":
            _log("[color=#e8c4b0]  Maya · 7 · north kneeler · the dress still bites.[/color]")
            _log("[color=#a89080]  her chapter from a different angle.[/color]")
        "jimmy":
            _log("[color=#a85050]  Jimmy · south kneeler · saboteur · sweating.[/color]")
            _log("[color=#7a3030]  reserves the right to sabotage the kneeling.[/color]")
        "john":
            _log("[color=#c8a878]  John · west kneeler · cook · wiper · dog at his side.[/color]")
            _log("[color=#7a6850]  the only one who could have refused. chose to wipe the counter instead.[/color]")
        # Hidden — cross-card
        "magician", "frasier":
            _log("[color=#88c8d0]  Frasier · rust-temple builder · two demons banished.[/color]")
        "emperor", "dante":
            _log("[color=#c89060]  Dante · the vineyard is his on paper. Quentin's uncle runs it.[/color]")
        "empress", "nicola":
            _log("[color=#c8807a]  Nicola · she passes the parking lot in Vol6, alone.[/color]")
        "priestess", "elicia":
            _log("[color=#a09a8a]  Elicia · tape of this sermon · Quentin did not consent.[/color]")
        "fool":
            _log("[color=#c89868]  the Fool refuses the language. the only card that can.[/color]")
        "chariot":
            _log("[color=#e8d070]  Antonio's card. the wreck. the phone call bought time.[/color]")
        # Hidden — books
        "voltaire", "candide":
            _log("[color=#a8b8d8]  CANDIDE · on the parish banned-book list.[/color]")
            _log("[color=#586878]  three doors from where Maya kneels.[/color]")
        # Hidden — sensory
        "texas", "heat":
            _log("[color=#c8a878]  the suit is wool blend. the suit was a mistake.[/color]")
        "ribbed", "engraved":
            _log("[color=#c8a878]  black engraved sweat — the salt outlines his collar.[/color]")
        _:
            if line == "tip":
                _log("[color=#586878]  the collection plate is on its way.[/color]")
            elif line == "rust_code.bbs":
                _log("[color=#a85050]  blocked at the parish firewall.[/color]")
            else:
                _log("[color=#586878]? unknown. try: help · pillars · rosh[/color]")


func _cmd_help() -> void:
    _log("[color=#fffeec]commands (visible):[/color]")
    _log("  [color=#fffeec]sermon[/color]     — Quentin speaks")
    _log("  [color=#fffeec]tradition[/color]  — left pillar")
    _log("  [color=#fffeec]conformity[/color] — right pillar")
    _log("  [color=#fffeec]pillars[/color]    — touch both")
    _log("  [color=#fffeec]rosh[/color]       — invoke the floor sigil (7 stages)")
    _log("  [color=#fffeec]acolytes[/color]   — identify the four kneelers")
    _log("  [color=#fffeec]booth[/color]      — D'Ambrosio's corner booth · Quentin's spot")
    _log("  [color=#fffeec]witness[/color]    — cycle multi-witness vignettes (4)")
    _log("  [color=#fffeec]recall[/color]     — discovery log")
    _log("  [color=#fffeec]count[/color]      — tallies")
    _log("  [color=#fffeec]look · listen · clear · exit[/color]")
    _log("[color=#586878](some commands are unlisted. the parish keeps its books.)[/color]")


func _cmd_memory() -> void:
    _log("[color=#fffeec]── memory · %d entries ──[/color]" % memory.size())
    var shown := 0
    for entry in memory:
        if shown >= 20:
            _log("[color=#586878]  ... (%d more)[/color]" %
                 (memory.size() - shown))
            break
        _log("  [color=#c8c4b0]· %s[/color]" % entry)
        shown += 1


func _cmd_count() -> void:
    _log("[color=#fffeec]── tallies ────────────────[/color]")
    _log("  sermon:      [color=#fffeec]%d[/color]" % sermon_count)
    _log("  pillars:     [color=#c8c4b0]%s · %s[/color]" % [
         "T✓" if tradition_touched else "T─",
         "C✓" if conformity_touched else "C─"])
    _log("  rosh:        [color=#a8b8d8]%d / 7 invocations[/color]" % rosh_invocations)
    _log("  acolytes:    [color=#e8d0c0]%d / 4 named[/color]" % acolyte_idx)
    _log("  booth:       [color=#e85060]%s[/color]" %
         ("read" if booth_read else "unread"))
    _log("  witnesses:   [color=#a8b8d8]%d / 4 vignettes[/color]" % witness_idx)
    _log("  hotspots:    [color=#fffeec]%d[/color]" % hotspots_seen.size())
    _log("  commands run:[color=#fffeec] %d[/color]" % commands_run.size())


func _cmd_look() -> void:
    _log("[color=#c8c4b0]· St. Jude's interior. Sunday. 6:42 AM.[/color]")
    _log("[color=#c8c4b0]· Quentin on the throne. heavy suit. unmoved.[/color]")
    _log("[color=#c8c4b0]· TRADITION pillar left · CONFORMITY pillar right.[/color]")
    _log("[color=#c8c4b0]· four kneelers around the Rosh floor symbol.[/color]")
    _log("[color=#586878]· corner booth visible from the lectern. coffee already ordered.[/color]")
    _log("[color=#586878]· four multi-witness panels along the right wall.[/color]")
    _log("[color=#586878]· one demon in the rafters. tracking. not banished.[/color]")


func _cmd_listen() -> void:
    _log("[color=#c8c4b0]· Father Paul rehearsing the kyrie under his breath.[/color]")
    _log("[color=#c8c4b0]· cicadas just starting outside. it is going to be hot.[/color]")
    _log("[color=#586878]· the demon making a sound that is not quite a sound.[/color]")
    _log("[color=#586878]· coffee, somewhere. pouring.[/color]")
    _log("[color=#586878]· Quentin's voice. low. ahead of the room.[/color]")


func _refresh_tally() -> void:
    if tally_btn != null:
        var p := (1 if tradition_touched else 0) + (1 if conformity_touched else 0)
        tally_btn.text = "  ✠ sermon %d · pillars %d/2 · rosh %d/7 · witnesses %d/4 · acolytes %d/4  " % [
            sermon_count, p, rosh_invocations, witness_idx, acolyte_idx]


func _memorize(entry: String) -> void:
    memory.append(entry)
    if memory.size() > 200:
        memory.remove_at(0)


func _log(line: String) -> void:
    if console_log != null:
        console_log.append_text(line + "\n")


# ── Process / heat / audio-reactive ASCII pulse ──────────────────
func _process(delta: float) -> void:
    super(delta)
    heat_phase = fmod(heat_phase + delta * 0.7, TAU)
    if card_rect != null:
        var shim := 1.0 + sin(heat_phase) * 0.020
        # Red bias grows with rosh invocations — the binding flushes in
        var red_bias := rosh_invocations * 0.010
        card_rect.modulate = Color(
            1.0 * shim + red_bias,
            0.97 * shim,
            0.95 * shim - red_bias * 0.4)
    tableau_pulse += delta
    var amp: float = 0.0
    var am := get_node_or_null("/root/AudioMgr")
    if am != null and am.has_method("get_bgm_magnitude"):
        amp = clamp(float(am.call("get_bgm_magnitude", 80.0, 3200.0)) * 10.0,
                     0.0, 1.0)
    var base_amp = 0.07 + amp * 0.28
    var idx := 0
    for seg in _segments:
        if not seg.get("shown", false): continue
        var lbl: Label = seg.get("label")
        if lbl == null: continue
        var phase = tableau_pulse * 1.6 + idx * 0.43
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
            _do_sermon()
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
