extends "res://scenes/menu/TarotVisualizerBase.gd"
## ChariotVisualizer — Ember & Ash Restaurant · Two Horses, One Wreck.
##
## VII · POV: Antonio D'Ambrosio. Dante's younger son. The Hierophant's
## phone call was for him — that's why he's reading this from the
## BBS instead of from inside the steel.
##
## The card is a designer's mood-board / autopsy of the night:
## restaurant layout (Scaffolding VIP / Main Floor / Patio /
## Bar Section / Kitchen), liquid menu (Creole Negroni / Venetian
## Sazerac / Chariot's Flame), food menu (Redfish Piccata / Jimmy's
## Sabotage Jambalaya / Tiramisu Southern Comfort), the wrecked SUV
## at the centre, the sphinx-laid dog beside it, and at the bottom-
## right the diagnostic panel — sysop: the_charioteer (D.O.A.).
##
##   • CARD HOTSPOTS — seven rects on the painted Chariot:
##       WRECK     the crashed SUV at the centre
##       DOG       the sphinx-laid dog (Strength/FAITH link)
##       DRINKS    cycle the three signature cocktails
##       ORDER     cycle the three food dishes
##       LAYOUT    cycle the five seating sections
##       STATUS    cycle the five network-ops status lines
##       SCAFFOLD  the industrial framework on the left
##
##   • BBS CONSOLE — `antonio@ember.ash:~$` prompt. Public commands
##     cover all mechanics. Hidden: charioteer · doa · saboteur ·
##     jimmy · quentin · two_horses · one_wreck · negroni · sazerac ·
##     flame · creole · venetian · bayou · redfish · jambalaya ·
##     tiramisu · southern_comfort · dolce · scaffold · vip · bricks ·
##     horse · horses · wreck · ember · ash · network · sysop · cross-
##     character routes.

# ── Game state ───────────────────────────────────────────────────
var wreck_examined: bool = false
var wreck_clicks: int = 0
var dog_pets: int = 0
var drink_idx: int = 0       # 0..3 cycle 3 cocktails + brews list
var order_idx: int = 0       # 0..2 cycle 3 dishes
var layout_idx: int = 0      # 0..4 cycle 5 sections
var status_idx: int = 0      # 0..4 cycle 5 network-ops lines
var scaffold_taps: int = 0   # 0..3 — scaffold check escalation
var hotspots_seen: Dictionary = {}
var commands_run: Dictionary = {}
var memory: PackedStringArray = []
var ember_phase: float = 0.0       # slow card breathing
var tableau_pulse: float = 0.0

# ── UI refs ──────────────────────────────────────────────────────
var tally_btn: Button
var status_label: Label
var console_input: LineEdit
var console_log: RichTextLabel

const DRINKS := [
    "THE CREOLE NEGRONI · NOLA gin · Campari · sweet vermouth · orange bitters.",
    "VENETIAN SAZERAC · rye · Peychaud's · absinthe rinse · Italian amaro twist.",
    "THE CHARIOT'S FLAME · mezcal · chili · lime · flaming garnish · the one he had last.",
    "BAYOU CRAFT BREWS (list) · seasonal · ask the bartender · don't ask Antonio.",
]

const ORDERS := [
    "REDFISH PICCATA · pan-seared redfish · house garnish.",
    "JIMMY'S SABOTAGE JAMBALAYA · saboteur's portion · andouille · chicken · spice-packed.",
    "TIRAMISU 'SOUTHERN COMFORT' · espresso · mascarpone · ladyfingers · SoCo liqueur.",
]

const SECTIONS := [
    "SCAFFOLDING VIP · upper tier · the section that fails.",
    "MAIN FLOOR · ground · 4-tops mostly · the survivors sit here.",
    "PATIO · outdoor · breeze · Patrick sits at the corner four-top.",
    "BAR SECTION · long bar · stools · the charioteer used to lean here.",
    "KITCHEN · staff only · Jimmy plates the jambalaya · also sabotage adjacent.",
]

const STATUS_LINES := [
    "node: ember.ash.rest.bbs",
    "sysop: the_charioteer (D.O.A.)",
    "quentin call complete  ░  06:18 ░  Hierophant booth",
    "jimmy joining unknown  ░  scaffolding crew  ░  not yet on shift",
    "scaffolding check in progress  ░  foreman ETA: too late.",
]

const SCAFFOLD_STAGES := [
    "the scaffolding ladder is fine. it has always been fine.",
    "the second crossbar wobbles when touched. it has always wobbled.",
    "the bolt at the second crossbar is missing. it was missing all night.",
    "the missing bolt is in Jimmy's apron pocket. it has been there since 4 PM.",
]


func _init() -> void:
    _card_path  = "res://assets/gallery/chariot.png"
    _composition_path = "chariot_card"   # mosaic-block centerpiece
    _hooks_path = "res://resources/puzzle_hooks/chariot.json"
    _ambient_audio_path = "res://assets/audio/bgm/vol5_riverboat_drone.ogg"
    # Rust orange + industrial white + diagnostic blue
    C_BG = Color(0.05, 0.04, 0.04)
    C_GOLD = Color(0.95, 0.60, 0.25)
    C_GOLD_HI = Color(1.0, 0.82, 0.40)
    C_TEXT = Color(0.85, 0.78, 0.68)
    C_TEXT_DIM = Color(0.45, 0.38, 0.32)


func _build_chrome() -> void:
    super()
    _build_bottom_strip()
    _build_card_hotspots()


func _build_card_hotspots() -> void:
    if card_rect == null: return
    var defs := [
        ["wreck",    Rect2(0.32, 0.32, 0.24, 0.30), "examine the wreck",         _do_wreck],
        ["dog",      Rect2(0.55, 0.50, 0.10, 0.20), "pet the sphinx-laid dog",   _do_dog],
        ["drinks",   Rect2(0.66, 0.06, 0.30, 0.32), "Liquid Gold Dispensary",    _do_drinks],
        ["order",    Rect2(0.08, 0.62, 0.32, 0.28), "order food",                _do_order],
        ["layout",   Rect2(0.66, 0.40, 0.30, 0.28), "study the seating map",     _do_layout],
        ["status",   Rect2(0.66, 0.78, 0.30, 0.18), "read the network status",   _do_status],
        ["scaffold", Rect2(0.02, 0.08, 0.10, 0.55), "check the scaffolding",     _do_scaffold],
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
        sb.bg_color = Color(1.0, 0.55, 0.20, 0.0)
        sb.border_color = Color(1.0, 0.55, 0.20, 0.0)
        sb.set_border_width_all(1)
        btn.add_theme_stylebox_override("normal", sb)
        var bsh := sb.duplicate() as StyleBoxFlat
        bsh.bg_color = Color(1.0, 0.55, 0.20, 0.18)
        bsh.border_color = Color(1.0, 0.82, 0.40, 0.85)
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
    bps.bg_color = Color(0.03, 0.025, 0.025, 0.88)
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
        Color(0.90, 0.78, 0.62))
    vbox.add_child(console_log)

    var inrow := HBoxContainer.new()
    inrow.add_theme_constant_override("separation", 4)
    var prompt := Label.new()
    prompt.text = "antonio@ember.ash:~$ "
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
    tally_btn.text = "  ⚡ wreck ─ · drinks 0/4 · scaffold 0/4 · status 0/5  "
    tally_btn.add_theme_color_override("font_color", C_GOLD_HI)
    tally_btn.add_theme_font_size_override("font_size", 11)
    var wbs := StyleBoxFlat.new()
    wbs.bg_color = Color(C_GOLD.r * 0.2, C_GOLD.g * 0.2, C_GOLD.b * 0.2, 0.55)
    wbs.border_color = C_GOLD
    wbs.set_border_width_all(1)
    tally_btn.add_theme_stylebox_override("normal", wbs)
    var wbh := wbs.duplicate() as StyleBoxFlat
    wbh.bg_color = Color(C_GOLD.r * 0.45, C_GOLD.g * 0.45, C_GOLD.b * 0.45, 0.7)
    wbh.border_color = C_GOLD_HI
    tally_btn.add_theme_stylebox_override("hover", wbh)
    tally_btn.pressed.connect(_do_wreck)
    tally_btn.tooltip_text = "click card regions for distinct mechanics"
    actrow.add_child(tally_btn)

    status_label = Label.new()
    status_label.text = "click the card · wreck · dog · drinks · order · layout · status · scaffold"
    status_label.add_theme_color_override("font_color",
        Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.80))
    status_label.add_theme_font_size_override("font_size", 10)
    status_label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    status_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    actrow.add_child(status_label)

    _log("[color=#ff9650]> VII · THE CHARIOT · vol.5 ch.7 · EMBER & ASH RESTAURANT[/color]")
    _log("[color=#a0664a]> TWO HORSES, ONE WRECK · POV: ANTONIO D'AMBROSIO[/color]")
    _log("[color=#ff9650]> node: ember.ash.rest.bbs · sysop: the_charioteer (D.O.A.)[/color]")
    _log("[color=#a0664a]> the diagnostic surface is yours · type [color=#ffd070]help[/color][/color]")

    console_input.grab_focus()


# ── Tableau registration ─────────────────────────────────────────
func _build_thematic_widget() -> void:
    var c_rust := Color(0.95, 0.58, 0.25, 0.95)
    var c_rust_dim := Color(0.55, 0.32, 0.16, 0.85)
    var c_rust_hot := Color(1.0, 0.78, 0.42, 1.0)
    var c_white := Color(0.92, 0.90, 0.85, 0.95)
    var c_diag := Color(0.55, 0.78, 0.92, 0.95)         # diagnostic blue
    var c_diag_dim := Color(0.28, 0.42, 0.55, 0.85)
    var c_red := Color(0.90, 0.30, 0.30, 0.95)
    var c_smoke := Color(0.55, 0.52, 0.48, 0.85)
    var c_amber := Color(0.95, 0.78, 0.30, 0.95)

    # ────────────────────────────────────────────────────────────
    # NORTH — banner / system overview / above the wreck
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.NORTH, "row": 0, "tint": c_rust,
        "font_size": 13, "requires": null,
        "ascii":
"""
       ╔═══════════════════════════════════════════════════════╗
       ║   VII · THE CHARIOT · EMBER & ASH RESTAURANT         ║
       ║   ─── TWO HORSES · ONE WRECK ───                     ║
       ║   POV: ANTONIO D'AMBROSIO                            ║
       ╚═══════════════════════════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 1, "tint": c_diag,
        "font_size": 11,
        "requires": null,
        "ascii":
"""
              ┌─── ember.ash.rest.bbs ──────────┐
              │  online                         │
              │  uptime: 14:22:08               │
              │  active threads: 47             │
              │  ─ scaffolding crew on shift ─  │
              │  ─ foreman: dispatched ─        │
              │  ─ ETA: too late ─              │
              └─────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 2, "tint": c_red,
        "font_size": 12,
        "requires": func(): return wreck_clicks >= 1,
        "ascii":
"""
              ╔══════════════════════════════════╗
              ║   ░ TWO HORSES, ONE WRECK ░      ║
              ║                                  ║
              ║   the chariot is supposed to     ║
              ║   show CONTROL of duality.       ║
              ║                                  ║
              ║   here, the duality is the team ║
              ║   that never agreed on the route.║
              ║                                  ║
              ║   half the team is the player.   ║
              ║   half the team is the system.   ║
              ╚══════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 3, "tint": c_amber,
        "font_size": 11,
        "requires": func(): return drink_idx >= 3,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  ░ THE CHARIOT'S FLAME ░         │
              │  the one he had last.            │
              │  mezcal, chili, lime, flame.     │
              │  the flaming garnish was         │
              │  decorative. or warning.         │
              │  ─ both readings on the menu ─   │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 4, "tint": c_diag,
        "font_size": 11,
        "requires": func(): return status_idx >= 5,
        "ascii":
"""
              ╔══════════════════════════════════╗
              ║  ░ ALL STATUS LINES READ ░       ║
              ║                                  ║
              ║  the chapter's diagnostic surface║
              ║  is complete. you have read what ║
              ║  Antonio cannot, because Antonio ║
              ║  is the SYSOP that the panel     ║
              ║  marks D.O.A.                    ║
              ║                                  ║
              ║  the BBS continues without him.  ║
              ╚══════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 5, "tint": c_rust_hot,
        "font_size": 11,
        "requires": func(): return hotspots_seen.size() >= 6,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  ░ EVERY PANEL OBSERVED ░        │
              │  the wreck. the dog. the drinks. │
              │  the dishes. the layout. the     │
              │  status. the scaffold.           │
              │                                  │
              │  Antonio's chapter is a designer │
              │  mood-board because Antonio has  │
              │  stopped narrating. the          │
              │  designer takes over.            │
              └──────────────────────────────────┘
"""
    })

    # ────────────────────────────────────────────────────────────
    # SOUTH — kitchen / food / Jimmy
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.SOUTH, "row": 0, "tint": c_smoke,
        "font_size": 12, "requires": null,
        "ascii":
"""
       ══════════ KITCHEN · staff only ══════════════════════
        ░ slow-cook station ░ flat-top ░ char grill ░       ░
        ░ Jimmy is here ░ Jimmy has been here all afternoon ░
        ░ Jimmy's apron pocket has something heavy in it ░  ░
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 1, "tint": c_rust,
        "font_size": 11,
        "requires": func(): return order_idx >= 1,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  ░ REDFISH PICCATA ░             │
              │  pan-seared · brown butter ·     │
              │  capers · lemon · parsley.       │
              │  the safest dish on the menu.    │
              │  Antonio ordered it.             │
              │  he did not finish it.           │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 2, "tint": c_red,
        "font_size": 11,
        "requires": func(): return order_idx >= 2,
        "ascii":
"""
              ╔══════════════════════════════════╗
              ║  ░ JIMMY'S SABOTAGE JAMBALAYA ░  ║
              ║                                  ║
              ║  saboteur's portion. slow-cooked.║
              ║  andouille · chicken · spice.    ║
              ║                                  ║
              ║  the dish is named for the cook. ║
              ║  the cook is named for the dish. ║
              ║  the cook is also a kneeler at   ║
              ║  St. Jude's. (Hierophant card.)  ║
              ╚══════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 3, "tint": c_amber,
        "font_size": 11,
        "requires": func(): return order_idx >= 3,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  ░ TIRAMISU 'SOUTHERN COMFORT' ░ │
              │  espresso · mascarpone ·         │
              │  ladyfingers · SoCo liqueur.     │
              │  the dolce. the mock comfort.    │
              │  ─ Acadian welcome that bites ─  │
              │  Antonio did not order this.     │
              │  the kitchen sent it anyway.     │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 4, "tint": c_red,
        "font_size": 11,
        "requires": func(): return scaffold_taps >= 3,
        "ascii":
"""
              ╔══════════════════════════════════╗
              ║  ░ THE MISSING BOLT ░            ║
              ║                                  ║
              ║  Jimmy's apron pocket.           ║
              ║  Since 4:00 PM.                  ║
              ║  The second crossbar of          ║
              ║  scaffold ladder C.              ║
              ║                                  ║
              ║  Removed quietly. Not replaced.  ║
              ║  ─ the saboteur sabotages ─      ║
              ╚══════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 5, "tint": c_smoke,
        "font_size": 11,
        "requires": func(): return commands_run.get("jimmy", 0) >= 1,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  JIMMY · last name unconfirmed   │
              │  ─ Hierophant south kneeler ─    │
              │  ─ Ember & Ash line cook ─       │
              │  ─ scaffolding crew (off shift) ─│
              │  ─ saboteur ─                    │
              │  three jobs · one schedule       │
              │  one of them is a cover.         │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 6, "tint": c_diag,
        "font_size": 11,
        "requires": func(): return wreck_clicks >= 4,
        "ascii":
"""
              ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
              ░ WRECK · RECONSTRUCTION COMPLETE   ░
              ░ ─ scaffold ladder C failed        ░
              ░ ─ Antonio was on the upper tier   ░
              ░ ─ the chariot is the falling      ░
              ░   tier itself, not the SUV in     ░
              ░   the diagram                     ░
              ░ ─ the SUV in the diagram is the   ░
              ░   metaphor the designer chose     ░
              ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""
    })

    # ────────────────────────────────────────────────────────────
    # EAST — Liquid Gold / status / forward
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.EAST, "row": 0, "tint": c_amber,
        "font_size": 11, "requires": null,
        "ascii":
"""

         ┌── LIQUID GOLD DISPENSARY ──────────────┐
         │  three signature cocktails             │
         │  + Bayou craft brew rotation           │
         │  ─ poured by the_charioteer himself ─  │
         │  ─ until 22:18 ─                       │
         │  ─ after that: the second bartender ─  │
         │  ─ name on the schedule: 'pending' ─   │
         └────────────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 1, "tint": c_amber,
        "font_size": 11,
        "requires": func(): return drink_idx >= 1,
        "ascii":
"""

         ┌── THE CREOLE NEGRONI ──────────────────┐
         │  Local NOLA gin.                       │
         │  Campari.                              │
         │  Sweet vermouth.                       │
         │  Orange bitters.                       │
         │  ─ 1:1:1 plus a dash ─                 │
         │  ─ Antonio's grandfather's order ─     │
         └────────────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 2, "tint": c_white,
        "font_size": 11,
        "requires": func(): return drink_idx >= 2,
        "ascii":
"""

         ┌── VENETIAN SAZERAC ────────────────────┐
         │  Rye whiskey.                          │
         │  Peychaud's bitters.                   │
         │  Absinthe rinse.                       │
         │  Italian amaro twist.                  │
         │  ─ family-line cocktail ─              │
         │  ─ Dante's variant of the original ─   │
         │  ─ poured at the Emperor's table too ─ │
         └────────────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 3, "tint": c_diag,
        "font_size": 10,
        "requires": func(): return status_idx >= 1,
        "ascii":
"""

         ┌── STATUS LINE 2 ───────────────────────┐
         │  sysop: the_charioteer (D.O.A.)        │
         │  ─ the BBS still routes mail to him ─  │
         │  ─ the BBS does not know he's gone ─   │
         │  ─ the BBS has 47 active threads ─     │
         │  ─ none of them addressed to a sysop ─ │
         └────────────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 4, "tint": c_diag,
        "font_size": 10,
        "requires": func(): return status_idx >= 2,
        "ascii":
"""

         ┌── STATUS LINE 3 ───────────────────────┐
         │  quentin call complete · 06:18         │
         │  ─ source: Hierophant booth ─          │
         │  ─ subject: 'don't drive tonight' ─    │
         │  ─ Antonio agreed ─                    │
         │  ─ Antonio came in to work the         │
         │    scaffolding shift instead ─         │
         │  ─ the binding bought him here ─       │
         └────────────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 5, "tint": c_red,
        "font_size": 11,
        "requires": func(): return status_idx >= 4,
        "ascii":
"""

         ┌── STATUS LINE 5 ───────────────────────┐
         │  scaffolding check in progress         │
         │  ─ foreman ETA: too late ─             │
         │  ─ ladder C, crossbar 2: bolt missing ─│
         │  ─ recorded by night-camera at 21:54 ─ │
         │  ─ camera footage timestamped wrong ─  │
         │  ─ correction pending ─                │
         └────────────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 6, "tint": c_rust_hot,
        "font_size": 11,
        "requires": func(): return commands_run.get("hierophant", 0) >= 1 or commands_run.get("quentin", 0) >= 1,
        "ascii":
"""

              ┌──────────────────────────────────┐
              │  ░ cross-card · HIEROPHANT ░     │
              │  the call at 06:18 was Quentin's.│
              │  "Just remember who your friends │
              │   are, Antonio." was last week.  │
              │  tonight: "don't drive."         │
              │  Antonio didn't drive.           │
              │  Antonio took the scaffolding    │
              │  shift instead.                  │
              │  the friends remark did its job. │
              └──────────────────────────────────┘
"""
    })

    # ────────────────────────────────────────────────────────────
    # WEST — scaffolding / bricks / past / structure
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.WEST, "row": 0, "tint": c_rust,
        "font_size": 11, "requires": null,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  EMBER & ASH RESTAURANT          │
              │  ─── former: brick warehouse ─── │
              │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
              │  ▓ converted 2019                │
              │  ▓ scaffolding kept exposed      │
              │  ▓ industrial-finish aesthetic   │
              │  ▓ Owner: Antonio D'Ambrosio     │
              │  ▓ Silent partner: Dante         │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 1, "tint": c_rust_dim,
        "font_size": 11,
        "requires": func(): return scaffold_taps >= 1,
        "ascii":
"""
              ┌──── SCAFFOLD STAGE 1 ────────────┐
              │  the ladder is fine.             │
              │  it has always been fine.        │
              │  the inspectors say so.          │
              │  the inspectors said so          │
              │  last quarter and the quarter    │
              │  before. consistency is a kind   │
              │  of truth.                       │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 2, "tint": c_rust,
        "font_size": 11,
        "requires": func(): return scaffold_taps >= 2,
        "ascii":
"""
              ┌──── SCAFFOLD STAGE 2 ────────────┐
              │  the second crossbar wobbles.    │
              │  it has always wobbled.          │
              │  the wobble is documented.       │
              │  the wobble is in the work       │
              │  order from March. the work      │
              │  order is closed without action  │
              │  by Antonio in May.              │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 3, "tint": c_red,
        "font_size": 11,
        "requires": func(): return scaffold_taps >= 3,
        "ascii":
"""
              ┌──── SCAFFOLD STAGE 3 ────────────┐
              │  the BOLT at the second crossbar │
              │  is missing.                     │
              │  it was missing all night.       │
              │  it was missing all this week.   │
              │  Antonio walked under it twice   │
              │  on Tuesday.                     │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 4, "tint": c_red,
        "font_size": 11,
        "requires": func(): return commands_run.get("bricks", 0) >= 1,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  ░ BRICKS! ░                     │
              │  the bottom-left annotation.     │
              │  designer mood-board call-out.   │
              │  the bricks are real.            │
              │  the bricks are also a callback  │
              │  to Frasier's warehouse — same   │
              │  industrial lineage, different   │
              │  conversion strategy.            │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 5, "tint": c_diag,
        "font_size": 11,
        "requires": func(): return commands_run.get("frasier", 0) >= 1 or commands_run.get("magician", 0) >= 1,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  ░ cross-card · MAGICIAN ░       │
              │  ember.ash.rest.bbs and          │
              │  rust_code.bbs are on the same   │
              │  long-distance trunk.            │
              │  Frasier could see the wreck     │
              │  on his CRT before the camera    │
              │  footage timestamped wrong.      │
              │  he did not look.                │
              │  he was busy soldering.          │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 6, "tint": c_smoke,
        "font_size": 11,
        "requires": func(): return dog_pets >= 1,
        "ascii":
"""
              ┌──────────────────────────────────┐
              │  ░ the sphinx-laid dog ░         │
              │  not Antonio's.                  │
              │  she came in from the patio at   │
              │  19:30. nobody owns her.         │
              │  she sat down on the diagram     │
              │  exactly where the second sphinx │
              │  should have been.               │
              │  the card was always going to    │
              │  have her. nobody planned it.    │
              └──────────────────────────────────┘
"""
    })


# ── Mechanics ────────────────────────────────────────────────────
func _do_wreck() -> void:
    wreck_clicks += 1
    if not wreck_examined:
        wreck_examined = true
        SaveSystem.mark_unlocked("vol5_chariot_wreck_seen")
    hotspots_seen["wreck"] = true
    _refresh_tally()
    # Low impact + secondary crack
    _active_notes.append({"time":0.0,"freq":62.0,"wave":"sawtooth",
        "atk":0.001,"dur":0.55,"rel":0.55})
    _active_notes.append({"time":0.0,"freq":180.0,"wave":"square",
        "atk":0.005,"dur":0.20,"rel":0.20})
    _memorize("wreck #%d" % wreck_clicks)
    var lines := [
        "the SUV is upside down. the wheels are still turning, faintly.",
        "the windshield is intact. nobody believes this.",
        "the steering wheel has a handprint on it. the print is not Antonio's.",
        "the wreck is a metaphor. the metaphor is a real wreck. both are true.",
        "the reconstruction is complete. it was the scaffold, not the SUV.",
    ]
    var i: int = min(wreck_clicks - 1, lines.size() - 1)
    status_label.text = lines[i]
    _log("[color=#e85040]· wreck %d · %s[/color]" % [wreck_clicks, lines[i]])


func _do_dog() -> void:
    dog_pets += 1
    hotspots_seen["dog"] = true
    _refresh_tally()
    _active_notes.append({"time":0.0,"freq":520.0,"wave":"sine",
        "atk":0.02,"dur":0.20,"rel":0.25})
    _memorize("pet sphinx-dog #%d" % dog_pets)
    var lines := [
        "the dog leans into your hand. she is warm.",
        "the dog does not bark. the dog has not barked all night.",
        "the dog is the second sphinx. you knew this. she knew it first.",
        "the dog is FAITH from D'Ambrosio's. she travels.",
    ]
    var i: int = min(dog_pets - 1, lines.size() - 1)
    status_label.text = lines[i]
    _log("[color=#c8c4b0]· dog · %s[/color]" % lines[i])
    if dog_pets >= 3:
        SaveSystem.mark_unlocked("vol5_chariot_sphinx_link")


func _do_drinks() -> void:
    if drink_idx >= DRINKS.size():
        status_label.text = "all four pours catalogued."
        return
    drink_idx += 1
    hotspots_seen["drinks"] = true
    _refresh_tally()
    _active_notes.append({"time":0.0,"freq":392.0,"wave":"triangle",
        "atk":0.01,"dur":0.20,"rel":0.30})
    var line: String = DRINKS[drink_idx - 1]
    _memorize("drink · " + line)
    status_label.text = line
    _log("[color=#ffd070]· pour %d/4 · %s[/color]" % [drink_idx, line])
    if drink_idx == DRINKS.size():
        SaveSystem.mark_unlocked("vol5_chariot_drinks_menu")


func _do_order() -> void:
    if order_idx >= ORDERS.size():
        status_label.text = "the kitchen has nothing else to send."
        return
    order_idx += 1
    hotspots_seen["order"] = true
    _refresh_tally()
    _active_notes.append({"time":0.0,"freq":220.0,"wave":"triangle",
        "atk":0.01,"dur":0.22,"rel":0.25})
    var line: String = ORDERS[order_idx - 1]
    _memorize("order · " + line)
    status_label.text = line
    _log("[color=#c89060]· order %d/3 · %s[/color]" % [order_idx, line])
    if order_idx == ORDERS.size():
        SaveSystem.mark_unlocked("vol5_chariot_food_menu")


func _do_layout() -> void:
    if layout_idx >= SECTIONS.size():
        status_label.text = "all five sections studied."
        return
    layout_idx += 1
    hotspots_seen["layout"] = true
    _refresh_tally()
    _active_notes.append({"time":0.0,"freq":330.0,"wave":"sine",
        "atk":0.01,"dur":0.18,"rel":0.20})
    var line: String = SECTIONS[layout_idx - 1]
    _memorize("section · " + line)
    status_label.text = line
    _log("[color=#88a8c0]· section %d/5 · %s[/color]" % [layout_idx, line])
    if layout_idx == SECTIONS.size():
        SaveSystem.mark_unlocked("vol5_chariot_layout_seen")


func _do_status() -> void:
    if status_idx >= STATUS_LINES.size():
        status_label.text = "all five status lines read."
        return
    status_idx += 1
    hotspots_seen["status"] = true
    _refresh_tally()
    _active_notes.append({"time":0.0,"freq":880.0,"wave":"square",
        "atk":0.001,"dur":0.04,"rel":0.06})
    var line: String = STATUS_LINES[status_idx - 1]
    _memorize("status · " + line)
    status_label.text = line
    _log("[color=#88c8d8]· status %d/5 · %s[/color]" % [status_idx, line])
    if status_idx == STATUS_LINES.size():
        SaveSystem.mark_unlocked("vol5_chariot_diagnostic")


func _do_scaffold() -> void:
    if scaffold_taps >= SCAFFOLD_STAGES.size():
        status_label.text = "scaffold check complete · ladder C condemned."
        return
    scaffold_taps += 1
    hotspots_seen["scaffold"] = true
    _refresh_tally()
    _active_notes.append({"time":0.0,"freq":110.0,"wave":"sawtooth",
        "atk":0.005,"dur":0.25,"rel":0.30})
    var line: String = SCAFFOLD_STAGES[scaffold_taps - 1]
    _memorize("scaffold #%d · %s" % [scaffold_taps, line])
    status_label.text = line
    _log("[color=#e85040]· scaffold %d/4 · %s[/color]" % [scaffold_taps, line])
    if scaffold_taps == SCAFFOLD_STAGES.size():
        _log("[color=#ff9650]· ░ THE MISSING BOLT IS IN JIMMY'S APRON POCKET.[/color]")
        SaveSystem.mark_unlocked("vol5_chariot_scaffold_check")
        SaveSystem.mark_unlocked("vol5_jimmy_sabotage_revealed")


func _on_hotspot(hs: Dictionary) -> void:
    super(hs)
    var hs_id := str(hs.get("id",""))
    hotspots_seen[hs_id] = true
    _memorize("hotspot: " + hs_id)
    match hs_id:
        "cha_wreck_hotspot":     _do_wreck()
        "cha_dog_hotspot":       _do_dog()
        "cha_drinks_hotspot":    _do_drinks()
        "cha_food_hotspot":      _do_order()
        "cha_layout_hotspot":    _do_layout()
        "cha_status_hotspot":    _do_status()
        "cha_scaffold_hotspot":  _do_scaffold()
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
        "wreck", "examine":
            _do_wreck()
        "dog", "pet", "sphinx":
            _do_dog()
        "drinks", "drink", "pour":
            _do_drinks()
        "order", "food", "menu":
            _do_order()
        "layout", "seating", "sections":
            _do_layout()
        "status", "ops", "network":
            _do_status()
        "scaffold", "scaffolding", "check":
            _do_scaffold()
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
        "graustark", "river", "delta":
            _log("[color=#ff9650]  ≈≈ Graustark · Ember & Ash sits inland · the river runs behind.[/color]")
            _log("[color=#a0664a]  the wreck didn't reach the river · just the scaffold.[/color]")
        "exit", "quit", "close":
            closed.emit()
        # Hidden — diagnostic
        "charioteer", "sysop":
            _log("[color=#ff9650]  the_charioteer is Antonio's BBS handle.[/color]")
            _log("[color=#a0664a]  the BBS marks him D.O.A. the BBS still routes his mail.[/color]")
        "doa":
            _log("[color=#e85040]  dead on arrival · sysop process not responding.[/color]")
            _log("[color=#7a3030]  47 threads continue without him.[/color]")
        "two_horses", "horses", "horse":
            _log("[color=#ff9650]  the chariot's two horses · classic duality · here: collapsed.[/color]")
        "one_wreck", "wreck_metaphor":
            _log("[color=#e85040]  the wreck is the team that never agreed on the route.[/color]")
        "ember", "ash":
            _log("[color=#ff9650]  EMBER & ASH · former brick warehouse · industrial finish.[/color]")
        "bbs", "ember.ash.rest.bbs":
            _log("[color=#88c8d8]  node: ember.ash.rest.bbs · 47 active threads.[/color]")
        # Hidden — saboteur
        "jimmy":
            _log("[color=#a85050]  Jimmy · saboteur · Hierophant kneeler · Ember & Ash line cook.[/color]")
            _log("[color=#7a3030]  three jobs, one schedule, one is a cover.[/color]")
        "saboteur", "sabotage":
            _log("[color=#e85040]  the bolt at scaffold ladder C, crossbar 2.[/color]")
            _log("[color=#7a3030]  in Jimmy's apron pocket since 4 PM.[/color]")
        # Hidden — drinks deep
        "creole", "creole_negroni":
            _log("[color=#ffd070]  THE CREOLE NEGRONI · NOLA gin · Campari · sweet vermouth.[/color]")
        "venetian", "sazerac", "peychaud":
            _log("[color=#fffaf0]  VENETIAN SAZERAC · rye · Peychaud's · absinthe · amaro.[/color]")
            _log("[color=#a89c80]  Dante's variant. the family-line cocktail.[/color]")
        "flame", "chariots_flame", "chili", "mezcal":
            _log("[color=#ff8048]  THE CHARIOT'S FLAME · mezcal · chili · lime · flaming garnish.[/color]")
            _log("[color=#a04030]  the one he had last.[/color]")
        "bayou", "brew", "craft":
            _log("[color=#88a868]  BAYOU CRAFT BREWS · ask the bartender · don't ask Antonio.[/color]")
        "nola":
            _log("[color=#ffd070]  New Orleans / Lousiana · Acadian-adjacent · fleur-de-lis.[/color]")
        # Hidden — dishes
        "redfish", "piccata":
            _log("[color=#c89060]  REDFISH PICCATA · the safest dish · he didn't finish it.[/color]")
        "jambalaya":
            _log("[color=#c84030]  JIMMY'S SABOTAGE JAMBALAYA · saboteur's portion.[/color]")
        "tiramisu":
            _log("[color=#c8a060]  TIRAMISU 'SOUTHERN COMFORT' · mock Acadian welcome.[/color]")
        "southern_comfort", "soco":
            _log("[color=#c89060]  SoCo liqueur · the Acadian welcome that bites.[/color]")
        "dolce":
            _log("[color=#c8a060]  dolce · sweet · the kitchen sent it anyway.[/color]")
        # Hidden — structure
        "scaffold_vip", "vip":
            _log("[color=#a85050]  SCAFFOLDING VIP · upper tier · the section that fails.[/color]")
        "bricks":
            _log("[color=#a86040]  BRICKS! · designer's mood-board call-out · industrial lineage.[/color]")
        "patio", "patrick":
            _log("[color=#88a868]  Patio · Patrick at the corner four-top · he survives.[/color]")
        "kitchen":
            _log("[color=#c84030]  Kitchen · staff only · Jimmy plates · also sabotage adjacent.[/color]")
        # Hidden — cross-character
        "antonio":
            _log("[color=#e85040]  Antonio D'Ambrosio · 34 · Dante's younger son · sysop · D.O.A.[/color]")
            _log("[color=#7a3030]  the chapter's POV character. also the chapter's target.[/color]")
        "dante", "emperor":
            _log("[color=#c89060]  Dante · silent partner of Ember & Ash · Antonio's uncle.[/color]")
            _log("[color=#a86040]  the family-line Sazerac is poured at his table too.[/color]")
        "quentin", "hierophant":
            _log("[color=#fffeec]  Quentin · the 06:18 call · 'don't drive tonight.'[/color]")
            _log("[color=#a89c80]  the binding bought Antonio onto the scaffolding shift.[/color]")
        "magician", "frasier":
            _log("[color=#88c8d0]  Frasier · same long-distance trunk · saw it · didn't look.[/color]")
        "fool", "john":
            _log("[color=#c89868]  John · D'Ambrosio's counter · timeless · the dog travels.[/color]")
        "empress", "nicola":
            _log("[color=#c8807a]  Nicola · she passes the lot on foot the morning after.[/color]")
        "priestess", "elicia":
            _log("[color=#a09a8a]  Elicia · she has the camera footage timestamped wrong.[/color]")
        "faith":
            _log("[color=#c89868]  the dog's name. she travels between cards.[/color]")
        _:
            if line == "tip":
                _log("[color=#7a3030]  charioteer doesn't tip. charioteer is D.O.A.[/color]")
            elif line == "rust_code.bbs":
                _log("[color=#88c8d8]  rust_code.bbs ↔ ember.ash.rest.bbs · same trunk · sister networks.[/color]")
            else:
                _log("[color=#7a3030]? unknown. try: help · status · scaffold[/color]")


func _cmd_help() -> void:
    _log("[color=#ffd070]commands (visible):[/color]")
    _log("  [color=#ffd070]wreck[/color]      — examine the centerpiece")
    _log("  [color=#ffd070]dog[/color]        — pet the sphinx-laid dog")
    _log("  [color=#ffd070]drinks[/color]     — Liquid Gold Dispensary (4 pours)")
    _log("  [color=#ffd070]order[/color]      — kitchen menu (3 dishes)")
    _log("  [color=#ffd070]layout[/color]     — seating sections (5)")
    _log("  [color=#ffd070]status[/color]     — network ops (5 lines)")
    _log("  [color=#ffd070]scaffold[/color]   — check ladder C (4 stages)")
    _log("  [color=#ffd070]recall[/color]     — discovery log")
    _log("  [color=#ffd070]count[/color]      — tallies")
    _log("  [color=#ffd070]look · listen · clear · exit[/color]")
    _log("[color=#7a3030](some commands are unlisted. the BBS still routes mail.)[/color]")


func _cmd_memory() -> void:
    _log("[color=#ffd070]── memory · %d entries ──[/color]" % memory.size())
    var shown := 0
    for entry in memory:
        if shown >= 20:
            _log("[color=#7a3030]  ... (%d more)[/color]" %
                 (memory.size() - shown))
            break
        _log("  [color=#c89060]· %s[/color]" % entry)
        shown += 1


func _cmd_count() -> void:
    _log("[color=#ffd070]── tallies ────────────────[/color]")
    _log("  wreck:     [color=#e85040]%s · %d clicks[/color]" % [
         "examined" if wreck_examined else "untouched", wreck_clicks])
    _log("  dog pets:  [color=#c8c4b0]%d[/color]" % dog_pets)
    _log("  drinks:    [color=#ffd070]%d / 4[/color]" % drink_idx)
    _log("  orders:    [color=#c89060]%d / 3[/color]" % order_idx)
    _log("  sections:  [color=#88a8c0]%d / 5[/color]" % layout_idx)
    _log("  status:    [color=#88c8d8]%d / 5[/color]" % status_idx)
    _log("  scaffold:  [color=#e85040]%d / 4[/color]" % scaffold_taps)
    _log("  hotspots:  [color=#ffd070]%d[/color]" % hotspots_seen.size())
    _log("  cmds run:  [color=#ffd070]%d[/color]" % commands_run.size())


func _cmd_look() -> void:
    _log("[color=#c89060]· EMBER & ASH at midnight. converted brick warehouse.[/color]")
    _log("[color=#c89060]· wrecked SUV at centre · the chariot, in metaphor and in fact.[/color]")
    _log("[color=#c89060]· sphinx-laid dog · sentinel · half of the absent duality.[/color]")
    _log("[color=#c89060]· LIQUID GOLD DISPENSARY · three cocktails · brews list.[/color]")
    _log("[color=#c89060]· kitchen sending dishes · saboteur plating.[/color]")
    _log("[color=#7a3030]· STATUS panel runs in the corner · diagnostic surface.[/color]")
    _log("[color=#7a3030]· scaffolding to the left · ladder C visible from here.[/color]")


func _cmd_listen() -> void:
    _log("[color=#c89060]· hum of the kitchen exhaust.[/color]")
    _log("[color=#c89060]· cooler ticking in the bar section.[/color]")
    _log("[color=#c89060]· dog's slow breathing.[/color]")
    _log("[color=#7a3030]· scaffolding · faintly · the wobble.[/color]")
    _log("[color=#7a3030]· no Antonio. anywhere.[/color]")


func _refresh_tally() -> void:
    if tally_btn != null:
        tally_btn.text = "  ⚡ wreck %s · drinks %d/4 · status %d/5 · scaffold %d/4  " % [
            ("✓" if wreck_examined else "─"),
            drink_idx, status_idx, scaffold_taps]


func _memorize(entry: String) -> void:
    memory.append(entry)
    if memory.size() > 200:
        memory.remove_at(0)


func _log(line: String) -> void:
    if console_log != null:
        console_log.append_text(line + "\n")


# ── Process / ember breath / audio-reactive ASCII pulse ──────────
func _process(delta: float) -> void:
    super(delta)
    ember_phase = fmod(ember_phase + delta * 0.9, TAU)
    if card_rect != null:
        # Slow ember breathing on the card; red bias grows with wreck clicks
        var br := 1.0 + sin(ember_phase) * 0.025
        var red := wreck_clicks * 0.014
        card_rect.modulate = Color(
            1.0 * br + red,
            0.94 * br,
            0.88 * br - red * 0.5)
    tableau_pulse += delta
    var amp: float = 0.0
    var am := get_node_or_null("/root/AudioMgr")
    if am != null and am.has_method("get_bgm_magnitude"):
        amp = clamp(float(am.call("get_bgm_magnitude", 80.0, 3200.0)) * 10.0,
                     0.0, 1.0)
    var base_amp = 0.08 + amp * 0.32
    var idx := 0
    for seg in _segments:
        if not seg.get("shown", false): continue
        var lbl: Label = seg.get("label")
        if lbl == null: continue
        var phase = tableau_pulse * 1.7 + idx * 0.42
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
            _do_status()
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
