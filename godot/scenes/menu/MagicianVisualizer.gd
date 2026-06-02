extends "res://scenes/menu/TarotVisualizerBase.gd"
## MagicianVisualizer — Cathedral of Rust and Code.
##
## Frasier in the warehouse-temple, soldering iron drawing the
## infinity sigil over a model-city diorama, flanked by two demons.
## The painted card sits at the center of a 3200×3200 canvas;
## ASCII tableau segments unfold N/S/E/W as the player solders,
## examines the model, banishes demons, reads the CRT, and decodes
## the paint can.
##
## Beyond the tableau, this visualizer carries:
##
##   • BBS CONSOLE in the bottom strip — typed commands trigger
##     reveals. Public: help / solder / model / banish / debug /
##     route / sigil / clear / exit.  Hidden: frasier · temple ·
##     compile · crash · 0x66 · emperor · nicola · priestess · iron ·
##     summon · demons · listen · look · ∞.
##
##   • CARD HOTSPOTS — six rects on the painted Magician card,
##     each fires a distinct mechanic:
##       SOLDER   Frasier's iron (infinity sigil)
##       MODEL    the diorama city he's wiring
##       BANISH_L the warehouse demon to his left
##       BANISH_R the warehouse demon to his right
##       DEBUG    the CRT in the lower-right
##       TAG      the COUNTY ROAD paint can
##
##   • CROSS-CARD ECHOES — solder/banish/debug all mark unlocks
##     that surface in other arcana (Emperor steamboat, Empress
##     biometrics, Priestess infinity).
##
##   • AUDIO-REACTIVE pulse — tableau labels tint along with the
##     BGM spectrum, ripple-phased per segment.

# ── Game state ───────────────────────────────────────────────────
var solder_count: int = 0
var model_count: int = 0
var banish_count: int = 0    # demons banished total (0..2 normally)
var demon_l_banished: bool = false
var demon_r_banished: bool = false
var debug_mode: int = 0      # 0 heartrate · 1 process · 2 forecast
var debug_pulls: int = 0
var tag_stage: int = 0       # 0..3 route fragment depth
var sigil_closed: bool = false
var hotspots_seen: Dictionary = {}
var commands_run: Dictionary = {}
var memory: PackedStringArray = []
var temple_phase: float = 0.0
var tableau_pulse: float = 0.0
var sigil_t: float = 0.0
var sigil_pulse: float = 0.0

# ── UI refs ──────────────────────────────────────────────────────
var tally_btn: Button
var status_label: Label
var console_input: LineEdit
var console_log: RichTextLabel


func _init() -> void:
    _card_path  = "res://assets/gallery/magician.png"
    _composition_path = "magician_card"
    _hooks_path = "res://resources/puzzle_hooks/magician.json"
    _ambient_audio_path = "res://assets/audio/bgm/vol5_warehouse_drone.ogg"
    C_BG = Color(0.020, 0.028, 0.035)
    C_GOLD = Color(0.55, 0.85, 0.88)
    C_GOLD_HI = Color(0.82, 0.98, 1.0)
    C_TEXT = Color(0.55, 0.82, 0.78)
    C_TEXT_DIM = Color(0.22, 0.40, 0.42)


func _build_chrome() -> void:
    super()
    _build_bottom_strip()
    _build_card_hotspots()


# Per-region mechanics on the painted Magician.
#   SOLDER   — the soldering iron tracing infinity (mid-upper-right)
#   MODEL    — the model city diorama (lower-mid)
#   BANISH_L — the warehouse demon on the left
#   BANISH_R — the warehouse demon on the right
#   DEBUG    — the CRT readout (lower-right)
#   TAG      — the COUNTY ROAD paint can (lower-left)
func _build_card_hotspots() -> void:
    if card_rect == null: return
    var defs := [
        ["solder",   Rect2(0.52, 0.16, 0.14, 0.22), "trace the infinity sigil", _do_solder],
        ["model",    Rect2(0.30, 0.62, 0.45, 0.30), "examine the model city",   _do_model],
        ["banish_l", Rect2(0.25, 0.42, 0.12, 0.22), "banish the left demon",    _do_banish_l],
        ["banish_r", Rect2(0.80, 0.36, 0.12, 0.22), "banish the right demon",   _do_banish_r],
        ["debug",    Rect2(0.85, 0.80, 0.12, 0.14), "read the CRT",             _do_debug],
        ["tag",      Rect2(0.05, 0.58, 0.13, 0.14), "read the paint can",       _do_tag],
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
        sb.bg_color = Color(0.55, 0.95, 1.0, 0.0)
        sb.border_color = Color(0.55, 0.95, 1.0, 0.0)
        sb.set_border_width_all(1)
        btn.add_theme_stylebox_override("normal", sb)
        var bsh := sb.duplicate() as StyleBoxFlat
        bsh.bg_color = Color(0.55, 0.95, 1.0, 0.20)
        bsh.border_color = Color(0.82, 0.98, 1.0, 0.75)
        btn.add_theme_stylebox_override("hover", bsh)
        btn.add_theme_stylebox_override("focus", bsh)
        btn.pressed.connect(d[3])
        canvas.add_child(btn)


func _build_bottom_strip() -> void:
    var bot := PanelContainer.new()
    bot.anchor_left = 0; bot.anchor_right = 1
    bot.anchor_top = 1;  bot.anchor_bottom = 1
    bot.offset_top = -160
    var bps := StyleBoxFlat.new()
    bps.bg_color = Color(0, 0.02, 0.04, 0.82)
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
        Color(0.35, 0.90, 0.95))
    vbox.add_child(console_log)

    var inrow := HBoxContainer.new()
    inrow.add_theme_constant_override("separation", 4)
    var prompt := Label.new()
    prompt.text = "frasier@cathedral:~$ "
    prompt.add_theme_color_override("font_color", C_GOLD_HI)
    prompt.add_theme_font_size_override("font_size", 12)
    inrow.add_child(prompt)
    console_input = LineEdit.new()
    console_input.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    console_input.add_theme_color_override("font_color",
        Color(0.35, 0.95, 1.0))
    console_input.text_submitted.connect(_on_command)
    inrow.add_child(console_input)
    vbox.add_child(inrow)

    var actrow := HBoxContainer.new()
    actrow.add_theme_constant_override("separation", 12)
    vbox.add_child(actrow)

    tally_btn = Button.new()
    tally_btn.text = "  ∞ solder 0 · model 0 · banish 0/2  "
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
    tally_btn.pressed.connect(_do_solder)
    tally_btn.tooltip_text = "click card regions for distinct mechanics"
    actrow.add_child(tally_btn)

    status_label = Label.new()
    status_label.text = "click the card · solder · model · banish · debug · tag"
    status_label.add_theme_color_override("font_color",
        Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.7))
    status_label.add_theme_font_size_override("font_size", 10)
    status_label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    status_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    actrow.add_child(status_label)

    _log("[color=#88e8f0]> CATHEDRAL OF RUST AND CODE · vol.5 ch.1[/color]")
    _log("[color=#3a7878]> warehouse drone @ -8db · CRT idle · demons: 2[/color]")
    _log("[color=#88e8f0]> wakey wakey, eggs and bakey.[/color]")
    _log("[color=#3a7878]> type [color=#a8e8f0]help[/color] for visible commands. (some are not listed.)[/color]")

    console_input.grab_focus()


# ── Tableau registration ─────────────────────────────────────────
func _build_thematic_widget() -> void:
    var c_cyan := Color(0.45, 0.88, 0.95, 1.0)
    var c_cyan_dim := Color(0.20, 0.45, 0.55, 0.9)
    var c_cyan_hot := Color(0.85, 0.98, 1.0, 1.0)
    var c_emerald := Color(0.30, 0.85, 0.55, 0.9)
    var c_rust := Color(0.78, 0.50, 0.28, 0.9)
    var c_rust_dim := Color(0.42, 0.28, 0.16, 0.85)
    var c_demon := Color(0.85, 0.30, 0.35, 0.9)
    var c_demon_dim := Color(0.50, 0.18, 0.22, 0.85)
    var c_temple := Color(0.65, 0.55, 0.85, 0.85)

    # ────────────────────────────────────────────────────────────
    # NORTH — cathedral roof / data stream above
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.NORTH, "row": 0, "tint": c_cyan_dim,
        "font_size": 13, "requires": null,
        "ascii":
"""
       ╔═════════════════════════════════════════════════╗
       ║   I  ░░  THE MAGICIAN  ░░  CATHEDRAL OF RUST   ║
       ╚═════════════════════════════════════════════════╝
        ─── as above ─── so below ─── as code ─── so flesh ───
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 1, "tint": c_emerald,
        "font_size": 12,
        "requires": func(): return solder_count >= 1,
        "ascii":
"""
       01000110 01010010 01000001 01010011 01001001 01000101 01010010
       ░ green data leaks from the warehouse girders ░
       ░ if you tilt your head, the rust spells words ░
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 2, "tint": c_cyan,
        "font_size": 12,
        "requires": func(): return solder_count >= 4,
        "ascii":
"""
              ╲                              ╱
               ╲      ░▒▓ ∞ ▓▒░             ╱
                ╲     the sigil traced     ╱
                 ╲    four times — closing╱
                  ╲    on itself.        ╱
                   ╲                   ╱
                    ─── as a loop ───
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 3, "tint": c_cyan_hot,
        "font_size": 12,
        "requires": func(): return sigil_closed,
        "ascii":
"""
           ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
         ░▒▒▓▓████  THE SIGIL HAS CLOSED  ████▓▓▒▒░
           ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
                  ┌───────────────────┐
                  │   ▓▓▒▒░ ∞ ░▒▒▓▓   │
                  │   AS ABOVE / BELOW│
                  └───────────────────┘
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 4, "tint": c_emerald,
        "font_size": 11,
        "requires": func(): return commands_run.get("temple", 0) >= 1,
        "ascii":
"""
            ╔══════════════════════════════════════╗
            ║   ░▒▓ THE WAREHOUSE IS A TEMPLE ▓▒░  ║
            ║   ░  with rust for stained glass  ░  ║
            ║   ░  with girders for vaulting    ░  ║
            ║   ░  with sodium lights for      ░   ║
            ║   ░  candles. nothing is sacred,  ░  ║
            ║   ░  therefore everything is.    ░   ║
            ╚══════════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 5, "tint": c_temple,
        "font_size": 11,
        "requires": func(): return hotspots_seen.size() >= 5,
        "ascii":
"""
          ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
        ░▒▒▓▓ THE FOUR ELEMENTS ON FRASIER'S BENCH ▓▓▒▒░
          ▒ ⚒ WAND  : the soldering iron        ▒
          ▒ ⚔ SWORD : the wire cutters          ▒
          ▒ ◯ COIN  : the steel washer          ▒
          ▒ ☼ CUP   : the rusted coffee mug     ▒
          ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""
    })
    _register_segment({"dir": Dir.NORTH, "row": 6, "tint": c_cyan_hot,
        "font_size": 12,
        "requires": func(): return solder_count >= 16,
        "ascii":
"""
              ╔═══════════════════════════════╗
              ║  ░▒▓█ ASCENDING NODE █▓▒░    ║
              ║  the sigil has been traced   ║
              ║  sixteen times. the air      ║
              ║  smells like ozone. the dog  ║
              ║  at D'AMBROSIO'S sits up.    ║
              ║  Nicola pauses mid-stride.   ║
              ╚═══════════════════════════════╝
"""
    })

    # ────────────────────────────────────────────────────────────
    # SOUTH — basement / model city / what's below
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.SOUTH, "row": 0, "tint": c_rust,
        "font_size": 12, "requires": null,
        "ascii":
"""
       ═════════ THE MODEL CITY ═════════════════════════
        ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓
        ░ wires soldered to the floor of the diner ░
        ░ tiny LEDs where the streetlights will be ░
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 1, "tint": c_rust_dim,
        "font_size": 11,
        "requires": func(): return model_count >= 1,
        "ascii":
"""
              ┌────────────────────────────────────┐
              │  ░ GRAUSTARK ░  predictive layout  │
              │  ▓  ▓  ▓  ▓     before construction │
              │  ▓ THE COUNTER ▓                   │
              │  ▓  ▓  ▓  ▓                        │
              └────────────────────────────────────┘
                  built tonight · risen in years
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 2, "tint": c_demon_dim,
        "font_size": 11,
        "requires": func(): return model_count >= 3,
        "ascii":
"""
              ╔══════════════════════════════════╗
              ║  ░  a tiny RED STEAMBOAT  ░      ║
              ║  ░  pinned to the model's edge   ║
              ║  ░  this is the boat from        ║
              ║  ░  the EMPEROR card. Frasier    ║
              ║  ░  has not met Dante yet.       ║
              ║  ░  the model knew first.        ║
              ╚══════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 3, "tint": c_rust,
        "font_size": 11,
        "requires": func(): return model_count >= 6,
        "ascii":
"""
              ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
              ░  the streets of GRAUSTARK arranged ░
              ░  in the same pattern as            ░
              ░  Frasier's circuit boards.         ░
              ░  topology is destiny.              ░
              ░  conductance is fate.              ░
              ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 4, "tint": c_emerald,
        "font_size": 10,
        "requires": func(): return commands_run.get("compile", 0) >= 1,
        "ascii":
"""
       $ gcc -O2 -DREALITY cathedral.c -lvoid
       cathedral.c: In function 'manifest':
       cathedral.c:47:2: warning: dimension cast may collide with timeline
          47 |   commit_to_reality(model, year=1997);
             |   ^~~~~~~~~~~~~~~~~
       cathedral.c:91:7: note: 'commit_to_reality' is irreversible
       /tmp/ccmagic.o:(.text+0x66): undefined reference to 'mercy'
       collect2: error: ld returned 1 exit status
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 5, "tint": c_demon,
        "font_size": 11,
        "requires": func(): return commands_run.get("crash", 0) >= 1,
        "ascii":
"""
              ▒░▒░▒░ REALITY SUBROUTINE GLITCH ░▒░▒░▒
              ░ frame 0114: the model city flickers ░
              ░ frame 0115: a girl walks past the   ░
              ░             warehouse who isn't     ░
              ░             born yet                ░
              ░ frame 0116: rollback failed         ░
              ░ frame 0117: rollback failed         ░
              ░ frame 0118: rollback accepted       ░
              ░ frame 0119: she was always there    ░
"""
    })
    _register_segment({"dir": Dir.SOUTH, "row": 6, "tint": c_rust,
        "font_size": 11,
        "requires": func(): return tag_stage >= 3,
        "ascii":
"""
              ╔══════════════════════════════════╗
              ║  COUNTY ROAD ░░░░░░░░░░░░░░░░    ║
              ║  full label:                     ║
              ║  ▓ COUNTY ROAD 17               ║
              ║  ▓ to ROCK ISLAND ░ to NAUVOO   ║
              ║  ▓ to the warehouse Nicola      ║
              ║  ▓ will pass on foot in ch.3    ║
              ╚══════════════════════════════════╝
"""
    })

    # ────────────────────────────────────────────────────────────
    # EAST — forward / the empire he's modeling
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.EAST, "row": 0, "tint": c_rust,
        "font_size": 11, "requires": null,
        "ascii":
"""
                  ░░
                ░░▒▒░░
              ░▒▒▓▓▓▓▒▒░   →   →   →
            ░▒▓██▓██▓▒░    THE EMPIRE
          ░▒▓████████▒░    HE HASN'T
        ░▒▓████████████▒░  MET YET
       ▒▓██████████████▓▒
       ▒▒░░░░░░░░░░░░░░▒▒
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 1, "tint": c_emerald,
        "font_size": 11,
        "requires": func(): return debug_pulls >= 1,
        "ascii":
"""

         ┌─── CRT readout ───────────────────────┐
         │  ♥  72 bpm  ░ steady              ░  │
         │  ░  whose? not Frasier's.            │
         │  ░  not anyone in the warehouse.     │
         │  ░  remote bio-monitor.              │
         │  ░  someone in Vol 3. someone wet.   │
         └────────────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 2, "tint": c_cyan,
        "font_size": 11,
        "requires": func(): return debug_pulls >= 2,
        "ascii":
"""

         ┌─── CRT readout · mode 2 ──────────────┐
         │  process list:                        │
         │  PID 1   reality.subroutine    R     │
         │  PID 47  cathedral.daemon      S     │
         │  PID 66  demon.left            Z     │
         │  PID 67  demon.right           Z     │
         │  PID 248 nicola.precognition   ?     │
         │  PID ??? frasier.self          ?     │
         └────────────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 3, "tint": c_cyan_hot,
        "font_size": 11,
        "requires": func(): return debug_pulls >= 3,
        "ascii":
"""

         ┌─── CRT readout · forecast ────────────┐
         │  T+0:00:00  ch.1  HERE                │
         │  T+0:14:22  ch.2  Anya / silence      │
         │  T+0:38:09  ch.3  Nicola arrives      │
         │  T+1:02:55  ch.4  Dante. throne.      │
         │  T+1:47:00  ch.5  the cathedral       │
         │              collapses or holds —     │
         │              uncertain.               │
         └────────────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 4, "tint": c_demon,
        "font_size": 11,
        "requires": func(): return banish_count >= 1,
        "ascii":
"""

              ░▒░ one demon banished. ░▒░
                  the warehouse smells
                  one part less of brimstone.
                  the other watches.
                  the other waits.
                  ─── 1 / 2 ───
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 5, "tint": c_emerald,
        "font_size": 11,
        "requires": func(): return banish_count >= 2,
        "ascii":
"""

              ╔══════════════════════════════════╗
              ║   ░ BOTH DEMONS BANISHED ░       ║
              ║                                  ║
              ║   the cathedral is clean.        ║
              ║   the air goes flat.             ║
              ║                                  ║
              ║   Frasier puts the iron down.    ║
              ║   he looks at the empty corner.  ║
              ║   he says: "huh."                ║
              ║                                  ║
              ║   ░ vol5_demon_summon_count=0 ░  ║
              ╚══════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.EAST, "row": 6, "tint": c_cyan_hot,
        "font_size": 11,
        "requires": func(): return commands_run.get("emperor", 0) >= 1,
        "ascii":
"""

              ┌──────────────────────────────────┐
              │  the steamboat in the model:     │
              │  it's the same boat.             │
              │  Dante hasn't seen it yet.       │
              │  Dante will never know           │
              │  Frasier wired it first.         │
              │  the magician sees forward.      │
              │  the emperor catches up.         │
              └──────────────────────────────────┘
"""
    })

    # ────────────────────────────────────────────────────────────
    # WEST — past / what the warehouse was / Voltaire / tapes
    # ────────────────────────────────────────────────────────────
    _register_segment({"dir": Dir.WEST, "row": 0, "tint": c_rust,
        "font_size": 11, "requires": null,
        "ascii":
"""
              ┌──────────────────────────┐
              │  WAREHOUSE 47            │
              │  former tenants:         │
              │ ░░░░░░░░░░░░░░░░░░░░░░░░ │
              │ ▓ 1971 furniture importer│
              │ ▓ 1979 vending repair    │
              │ ▓ 1984 vacant            │
              │ ▓ 1991 vacant            │
              │ ▓ 1995 — FRASIER         │
              └──────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 1, "tint": c_rust_dim,
        "font_size": 11,
        "requires": func(): return solder_count >= 1,
        "ascii":
"""
                ░░░░░░░░░░░░░░░░░░░░░░░░░░░
              ░░  cassette tape on the desk ░░
              ░░  side A: VOLTAIRE — CANDIDE ░░
              ░░  side B: blank but humming  ░░
              ░░  Frasier hasn't pressed play ░░
              ░░  in nine months. it still    ░░
              ░░  hums.                       ░░
                ░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 2, "tint": c_rust,
        "font_size": 11,
        "requires": func(): return tag_stage >= 1,
        "ascii":
"""

              ┌──────────────────────────┐
              │  paint can stencil:      │
              │  ░░ COUNTY ROAD ░░ ░░    │
              │  half scraped off        │
              │  the rest is below       │
              │  the rust line.          │
              └──────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 3, "tint": c_demon_dim,
        "font_size": 10,
        "requires": func(): return commands_run.get("demon", 0) >= 1,
        "ascii":
"""
              ╔══════════════════════════════════════╗
              ║   demon inventory                    ║
              ╠══════════════════════════════════════╣
              ║   LEFT:  scavenger of forgotten APIs ║
              ║          speaks in deprecated calls  ║
              ║          hungers for null pointers   ║
              ╠══════════════════════════════════════╣
              ║   RIGHT: aggregator of doomed builds ║
              ║          carries every crash report  ║
              ║          smells faintly of segfault  ║
              ╚══════════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 4, "tint": c_temple,
        "font_size": 11,
        "requires": func(): return commands_run.get("priestess", 0) >= 1,
        "ascii":
"""

              ┌──────────────────────────────────┐
              │  ▒░▒ THE PRIESTESS' SHELF ▒░▒    │
              │  among her books the infinity    │
              │  glyph appears bound in vellum   │
              │  ─ same glyph Frasier traces ─   │
              │  she READS it. he WRITES it.     │
              │  one card watches the other.     │
              └──────────────────────────────────┘
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 5, "tint": c_rust,
        "font_size": 11,
        "requires": func(): return solder_count >= 8,
        "ascii":
"""

              ╔══════════════════════════════════╗
              ║  the floor under the workbench   ║
              ║  is scorched in a ring.          ║
              ║  the ring is exactly the         ║
              ║  diameter of a man kneeling.     ║
              ║  Frasier doesn't kneel.          ║
              ║  but someone once did.           ║
              ╚══════════════════════════════════╝
"""
    })
    _register_segment({"dir": Dir.WEST, "row": 6, "tint": c_cyan,
        "font_size": 11,
        "requires": func(): return commands_run.get("nicola", 0) >= 1,
        "ascii":
"""

              ┌─────────────────────────────────┐
              │  ▒░▒ EMPRESS · NICOLA ▒░▒       │
              │  her data is green. his is cyan.│
              │  the colors mix in the air      │
              │  over the warehouse roof        │
              │  ─ teal ─                       │
              │  the EMS biometric stream he's  │
              │  watching belongs to her ride.  │
              └─────────────────────────────────┘
"""
    })


# ── Mechanics ────────────────────────────────────────────────────
func _do_solder() -> void:
    solder_count += 1
    sigil_pulse = 1.0
    _refresh_tally()
    _active_notes.append({"time":0.0,"freq":660.0 + randf() * 80.0,
        "wave":"square","atk":0.001,"dur":0.10,"rel":0.15})
    _memorize("solder #%d" % solder_count)
    var milestones := {
        1:  "first stroke. the air ionizes.",
        4:  "four strokes. the sigil closes.",
        8:  "eight. the workbench floor warms.",
        16: "sixteen. ascending node — the warehouse exhales.",
        32: "thirty-two. you hear the dog bark from elsewhere.",
    }
    if solder_count == 4:
        sigil_closed = true
        SaveSystem.mark_unlocked("vol5_magician_ascending_node")
    if solder_count == 16:
        SaveSystem.mark_unlocked("vol5_magician_ascending_node_full")
    if milestones.has(solder_count):
        var m: String = milestones[solder_count]
        status_label.text = m
        _log("[color=#a8e8f0]· %s[/color]" % m)
    else:
        status_label.text = "(solder %d.)" % solder_count


func _do_model() -> void:
    model_count += 1
    hotspots_seen["mag_model_city"] = true
    _refresh_tally()
    _active_notes.append({"time":0.0,"freq":175.0,"wave":"triangle",
        "atk":0.005,"dur":0.20,"rel":0.20})
    _memorize("model #%d" % model_count)
    var lines := ["a wire snaps into place.",
        "the diner foundation appears.",
        "a tiny RED STEAMBOAT pinned at the edge.",
        "the streets of GRAUSTARK reveal a circuit.",
        "the model knows what hasn't happened yet.",
        "the model is the city. the city is the model."]
    var i: int = min(model_count - 1, lines.size() - 1)
    status_label.text = lines[i]
    _log("[color=#c89868]· model %d. %s[/color]" % [model_count, lines[i]])
    if model_count == 3:
        SaveSystem.mark_unlocked("vol5_magician_emperor_link")
    if model_count == 6:
        SaveSystem.mark_unlocked("lore:graustark_overlay_map")


func _do_banish_l() -> void:
    if demon_l_banished:
        status_label.text = "left demon is already gone. only smoke."
        _log("[color=#c84030]· left demon already banished.[/color]")
        return
    demon_l_banished = true
    banish_count += 1
    hotspots_seen["mag_demon_left"] = true
    _refresh_tally()
    _banish_chord()
    _memorize("banish left")
    status_label.text = "LEFT demon banished. one to go."
    _log("[color=#e84055]· LEFT demon — scavenger of deprecated APIs — banished.[/color]")
    SaveSystem.mark_unlocked("lore:demon_left_inventory")
    SaveSystem.mark_unlocked("vol5_demon_summon_count")


func _do_banish_r() -> void:
    if demon_r_banished:
        status_label.text = "right demon is already gone. the corner is quiet."
        _log("[color=#c84030]· right demon already banished.[/color]")
        return
    demon_r_banished = true
    banish_count += 1
    hotspots_seen["mag_demon_right"] = true
    _refresh_tally()
    _banish_chord()
    _memorize("banish right")
    status_label.text = "RIGHT demon banished. cathedral runs clean."
    _log("[color=#e84055]· RIGHT demon — aggregator of doomed builds — banished.[/color]")
    SaveSystem.mark_unlocked("lore:demon_right_inventory")
    if banish_count == 2:
        _log("[color=#a8e8f0]· both demons cleared. air pressure drops.[/color]")
        SaveSystem.mark_unlocked("vol5_magician_demons_clear")


func _banish_chord() -> void:
    # A-C#-E triad over a sub-bass thump
    for f in [110.0, 220.0, 277.2, 329.6]:
        _active_notes.append({"time":0.0,"freq":f,"wave":"square",
            "atk":0.005,"dur":0.45,"rel":0.4})


func _do_debug() -> void:
    debug_pulls += 1
    debug_mode = (debug_mode + 1) % 3
    hotspots_seen["mag_crt_readout"] = true
    _refresh_tally()
    _active_notes.append({"time":0.0,"freq":920.0,"wave":"square",
        "atk":0.001,"dur":0.04,"rel":0.06})
    _memorize("debug · mode %d" % debug_mode)
    var modes := ["♥ heartrate (72 bpm)", "process list (47/66/67)",
                  "forecast (T+1:47 cathedral)"]
    status_label.text = "CRT → " + modes[debug_mode]
    _log("[color=#88e8f0]· CRT mode %d · %s[/color]" % [debug_mode, modes[debug_mode]])
    SaveSystem.mark_unlocked("vol5_diagnostic_grid")


func _do_tag() -> void:
    tag_stage = min(tag_stage + 1, 3)
    hotspots_seen["mag_paint_can"] = true
    _refresh_tally()
    _active_notes.append({"time":0.0,"freq":300.0,"wave":"sawtooth",
        "atk":0.001,"dur":0.12,"rel":0.15})
    _memorize("tag stage %d" % tag_stage)
    var stages := ["paint can stencil: ░░ COUNTY ROAD ░░ ░░ (half scraped)",
                   "more visible: COUNTY ROAD 17",
                   "rust line scrubbed: ROCK ISLAND · NAUVOO",
                   "full route: the road Nicola walks in ch.3."]
    status_label.text = stages[tag_stage]
    _log("[color=#c89868]· paint · %s[/color]" % stages[tag_stage])
    if tag_stage >= 3:
        SaveSystem.mark_unlocked("vol5_county_road_clue")


func _on_hotspot(hs: Dictionary) -> void:
    super(hs)
    var hs_id := str(hs.get("id",""))
    hotspots_seen[hs_id] = true
    _memorize("hotspot: " + hs_id)
    match hs_id:
        "mag_soldering_iron":   _do_solder()
        "mag_model_city":       _do_model()
        "mag_steamboat":
            status_label.text = "the steamboat — Dante's, in miniature."
            SaveSystem.mark_unlocked("vol5_magician_emperor_link")
        "mag_demon_left":       _do_banish_l()
        "mag_demon_right":      _do_banish_r()
        _:
            status_label.text = "[ %s ]" % str(hs.get("interact", hs_id))


# ── Console commands ─────────────────────────────────────────────
func _on_command(text: String) -> void:
    var line := text.strip_edges().to_lower()
    console_input.text = ""
    if line == "":
        return
    _log("[color=#88e8f0]> %s[/color]" % text)
    commands_run[line] = int(commands_run.get(line, 0)) + 1
    _memorize("typed: " + line)
    var parts := line.split(" ", false)
    var cmd := parts[0]

    match cmd:
        # Public
        "help", "?":
            _cmd_help()
        "solder", "iron":
            _do_solder()
        "model", "diorama":
            _do_model()
        "banish":
            _cmd_banish_all()
        "debug", "crt":
            _do_debug()
        "route", "paint":
            _do_tag()
        "sigil", "∞":
            _cmd_sigil()
        "memory", "recall":
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
            _log("[color=#88e8f0]  ≈≈ Graustark · the warehouse roof sees the river through the smog.[/color]")
            _log("[color=#3a7878]  industrial Acadian-adjacent · the sigil resonates over water.[/color]")
        "exit", "quit", "close":
            closed.emit()
        # Hidden lore
        "frasier":
            _log("[color=#a8e8f0]  wakey wakey, eggs and bakey.[/color]")
            _log("[color=#3a7878]  reality subroutine glitching.[/color]")
        "temple":
            _log("[color=#a878d0]  the warehouse is a temple.[/color]")
            _log("[color=#3a3858]  rust for stained glass. girders for vaulting.[/color]")
        "compile":
            _log("[color=#88c878]  $ gcc -O2 -DREALITY cathedral.c -lvoid[/color]")
            _log("[color=#88c878]  undefined reference to 'mercy'.[/color]")
        "crash":
            _log("[color=#e85540]  ▒░▒ REALITY SUBROUTINE GLITCH ░▒░[/color]")
            _log("[color=#7a4040]  frame rollback failed. she was always there.[/color]")
        "0x66":
            _log("[color=#a8e8f0]  0x66 = 102 decimal = 'f' = frasier.[/color]")
            _log("[color=#3a7878]  also: PID of demon.left in the process list.[/color]")
        "emperor":
            _log("[color=#88e8f0]  the steamboat in the model is Dante's.[/color]")
            _log("[color=#3a7878]  the magician sees forward.[/color]")
        "nicola":
            _log("[color=#88c878]  her data is green. yours is cyan. mix = teal.[/color]")
        "priestess":
            _log("[color=#a878d0]  the infinity glyph lives in her books too.[/color]")
        "demon", "demons":
            _log("[color=#c84030]  LEFT: scavenger of deprecated APIs.[/color]")
            _log("[color=#c84030]  RIGHT: aggregator of doomed builds.[/color]")
        "summon":
            _log("[color=#7a3030]  the cathedral is not for summoning.[/color]")
            _log("[color=#3a2020]  it is for letting go.[/color]")
        "voltaire":
            _log("[color=#c89868]  side A unread. side B humming. nine months.[/color]")
        "candide":
            _log("[color=#c89868]  the best of all possible warehouses.[/color]")
        "anya":
            _log("[color=#a878d0]  her name appears later. write it down.[/color]")
        _:
            if line == "tip":
                _log("[color=#3a7878]  no tip jar. magicians don't tip.[/color]")
            elif line == "rust_code.bbs":
                _log("[color=#a8e8f0]  the BBS recognizes the cathedral.[/color]")
            else:
                _log("[color=#3a2614]? unknown. try: help · memory · sigil[/color]")


func _cmd_help() -> void:
    _log("[color=#88e8f0]commands (visible):[/color]")
    _log("  [color=#a8e8f0]solder[/color]     — trace the infinity sigil")
    _log("  [color=#a8e8f0]model[/color]      — examine the diorama")
    _log("  [color=#a8e8f0]banish[/color]     — clear both demons")
    _log("  [color=#a8e8f0]debug[/color]      — cycle the CRT")
    _log("  [color=#a8e8f0]route[/color]      — read the paint can")
    _log("  [color=#a8e8f0]sigil[/color]      — the infinity, contemplated")
    _log("  [color=#a8e8f0]memory[/color]     — discovery log")
    _log("  [color=#a8e8f0]count[/color]      — tallies")
    _log("  [color=#a8e8f0]look[/color]       — examine the cathedral")
    _log("  [color=#a8e8f0]listen[/color]     — what's the drone saying")
    _log("  [color=#a8e8f0]clear · exit[/color]")
    _log("[color=#3a7878](some commands are unlisted. the BBS keeps secrets.)[/color]")


func _cmd_sigil() -> void:
    sigil_pulse = 1.0
    _banish_chord()
    _log("[color=#a8e8f0]    ░▒▓ ∞ ▓▒░[/color]")
    _log("[color=#3a7878]    A · C# · E — the magician's chord.[/color]")
    SaveSystem.mark_unlocked("vol5_iron_summons_link")


func _cmd_banish_all() -> void:
    if not demon_l_banished:
        _do_banish_l()
    if not demon_r_banished:
        _do_banish_r()


func _cmd_memory() -> void:
    _log("[color=#88e8f0]── memory · %d entries ─────[/color]" % memory.size())
    var shown := 0
    for entry in memory:
        if shown >= 20:
            _log("[color=#3a7878]  ... (%d more)[/color]" %
                 (memory.size() - shown))
            break
        _log("  [color=#c8e8f0]· %s[/color]" % entry)
        shown += 1


func _cmd_count() -> void:
    _log("[color=#88e8f0]── tallies ─────────────────[/color]")
    _log("  solders:      [color=#a8e8f0]%d[/color]" % solder_count)
    _log("  model edits:  [color=#a8e8f0]%d[/color]" % model_count)
    _log("  demons:       [color=#a8e8f0]%d / 2 banished[/color]" % banish_count)
    _log("  CRT pulls:    [color=#a8e8f0]%d (mode %d)[/color]" %
         [debug_pulls, debug_mode])
    _log("  paint stage:  [color=#a8e8f0]%d / 3[/color]" % tag_stage)
    _log("  hotspots:     [color=#a8e8f0]%d[/color]" % hotspots_seen.size())
    _log("  commands run: [color=#a8e8f0]%d[/color]" % commands_run.size())


func _cmd_look() -> void:
    _log("[color=#c8e8f0]· rust girders ░ sodium light ░ warehouse 47[/color]")
    _log("[color=#c8e8f0]· soldering iron in his hand. infinity tracing.[/color]")
    _log("[color=#c8e8f0]· model city on the floor. red steamboat pinned.[/color]")
    _log("[color=#c8e8f0]· CRT in the corner. heartrate trace.[/color]")
    _log("[color=#3a7878]· two demons. one each side. they're waiting.[/color]")
    _log("[color=#3a7878]· paint can: COUNTY ROAD ░░ (partial).[/color]")


func _cmd_listen() -> void:
    _log("[color=#c8e8f0]· warehouse drone. -8db. continuous.[/color]")
    _log("[color=#c8e8f0]· soldering iron, hissing on flux.[/color]")
    _log("[color=#c8e8f0]· CRT fan, slightly off-balance.[/color]")
    _log("[color=#3a7878]· cassette in the deck, humming on blank side B.[/color]")
    _log("[color=#3a7878]· something else. underneath. ozone, maybe.[/color]")


func _refresh_tally() -> void:
    if tally_btn != null:
        tally_btn.text = "  ∞ solder %d · model %d · banish %d/2  " % [
            solder_count, model_count, banish_count]


func _memorize(entry: String) -> void:
    memory.append(entry)
    if memory.size() > 200:
        memory.remove_at(0)


func _log(line: String) -> void:
    if console_log != null:
        console_log.append_text(line + "\n")


# ── Process / temple drift / audio-reactive ASCII pulse ──────────
func _process(delta: float) -> void:
    super(delta)
    sigil_t += delta
    sigil_pulse = maxf(0.0, sigil_pulse - delta * 1.2)
    # Slow temple breath on the card
    temple_phase = fmod(temple_phase + delta / 8.0, TAU)
    if card_rect != null:
        var breath := 0.5 + sin(temple_phase) * 0.5
        var sigil_boost := sigil_pulse * 0.15
        card_rect.modulate = Color(
            0.95 + breath * 0.05 + sigil_boost,
            0.97 + breath * 0.03 + sigil_boost,
            1.0 + sigil_boost)
    # Audio-reactive ASCII pulse
    tableau_pulse += delta
    var amp: float = 0.0
    var am := get_node_or_null("/root/AudioMgr")
    if am != null and am.has_method("get_bgm_magnitude"):
        amp = clamp(float(am.call("get_bgm_magnitude", 80.0, 3200.0)) * 10.0,
                     0.0, 1.0)
    var base_amp = 0.10 + amp * 0.40 + sigil_pulse * 0.25
    var idx := 0
    for seg in _segments:
        if not seg.get("shown", false): continue
        var lbl: Label = seg.get("label")
        if lbl == null: continue
        var phase = tableau_pulse * 2.0 + idx * 0.40
        var pulse_val = sin(phase) * 0.5 + 0.5
        var tint: Color = seg.get("tint", C_TEXT)
        var lifted := tint.lerp(C_GOLD_HI, pulse_val * base_amp)
        lifted.a = tint.a * (0.85 + pulse_val * base_amp * 0.30)
        lbl.modulate = lifted
        idx += 1


func _input(event: InputEvent) -> void:
    super(event)
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_SPACE and not console_input.has_focus():
            _do_solder()
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
