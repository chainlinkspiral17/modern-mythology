extends "res://scenes/menu/TarotVisualizerBase.gd"
## FoolVisualizer — progressive scrollable tableau.
##
## The painted card sits at the center of a 3200×3200 canvas. As
## the player wipes the counter / clicks hotspots / discovers
## ciphers, hand-crafted ASCII tableau segments fade in around the
## card in the four cardinal directions:
##
##   NORTH (sky)        dawn-not-quite-dawn lighting, the awning,
##                      sun-that-sleeps from the oracle text
##   SOUTH (water)      the precipice the Fool will step off of;
##                      surface waves rising with each wipe, depth
##                      revealing below
##   EAST  (journey)    where John could go — road, paw-prints,
##                      bindle, the door labeled II
##   WEST  (left behind) D'Ambrosio's counter, the rag, the customer
##                      who hasn't shown up
##
## Pan with mouse drag or WASD/arrows. HOME re-centers the card.
## Minimap in bottom-right shows where you are in the larger world.

var wipe_count: int = 0
var dog_clicks: int = 0
var oracle_read: bool = false

# Bottom strip controls
var wipe_btn: Button
var status_label: Label


func _init() -> void:
    _card_path  = "res://assets/gallery/fool.png"
    _hooks_path = "res://resources/puzzle_hooks/fool.json"
    _ambient_audio_path = "res://assets/audio/bgm/title_theme.ogg"
    C_BG = Color(0.040, 0.034, 0.020)
    C_GOLD = Color(0.85, 0.66, 0.29)
    C_GOLD_HI = Color(1.0, 0.85, 0.40)


func _build_chrome() -> void:
    super()
    # Bottom strip — wipe counter + status, fixed (doesn't pan)
    var bot := PanelContainer.new()
    bot.anchor_left = 0; bot.anchor_right = 1
    bot.anchor_top = 1;  bot.anchor_bottom = 1
    bot.offset_top = -60
    var bps := StyleBoxFlat.new()
    bps.bg_color = Color(0, 0, 0, 0.7)
    bps.border_color = C_GOLD
    bps.border_width_top = 1
    bot.add_theme_stylebox_override("panel", bps)
    add_child(bot)
    var bot_row := HBoxContainer.new()
    bot_row.add_theme_constant_override("separation", 16)
    bot.add_child(bot_row)

    wipe_btn = Button.new()
    wipe_btn.text = "  WIPE THE COUNTER  ( 0 / 64 )"
    wipe_btn.add_theme_color_override("font_color", C_GOLD_HI)
    wipe_btn.add_theme_font_size_override("font_size", 13)
    var wbs := StyleBoxFlat.new()
    wbs.bg_color = Color(C_GOLD.r * 0.3, C_GOLD.g * 0.3, C_GOLD.b * 0.3, 0.6)
    wbs.border_color = C_GOLD
    wbs.set_border_width_all(1)
    wipe_btn.add_theme_stylebox_override("normal", wbs)
    var wbh := wbs.duplicate() as StyleBoxFlat
    wbh.bg_color = Color(C_GOLD.r * 0.55, C_GOLD.g * 0.55, C_GOLD.b * 0.55, 0.7)
    wbh.border_color = C_GOLD_HI
    wipe_btn.add_theme_stylebox_override("hover", wbh)
    wipe_btn.pressed.connect(_do_wipe)
    bot_row.add_child(wipe_btn)

    status_label = Label.new()
    status_label.text = "drag to pan · wipe to discover · hotspots reveal more"
    status_label.add_theme_color_override("font_color",
        Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.7))
    status_label.add_theme_font_size_override("font_size", 10)
    status_label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    status_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    bot_row.add_child(status_label)


func _build_thematic_widget() -> void:
    var c_amber := Color(0.95, 0.74, 0.32, 1.0)
    var c_amber_dim := Color(0.55, 0.40, 0.18, 0.9)
    var c_water := Color(0.45, 0.65, 0.75, 0.9)
    var c_water_dim := Color(0.20, 0.32, 0.42, 0.85)
    var c_ash := Color(0.60, 0.54, 0.40, 0.9)
    var c_door := Color(0.30, 0.85, 0.42, 0.85)

    # ── NORTH — sky tableau ───────────────────────────────────
    # ROW 0: always shown — the awning + lit edge
    _register_segment({
        "dir": Dir.NORTH, "row": 0,
        "tint": c_amber_dim, "font_size": 13,
        "requires": null,
        "ascii":
"""
                       .  .         .       .
                  .      ░░░░░░░░       .  ░░       .
            ░░░░░░  ░░▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░  ▒▒░░░░░░
       ░░▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░
    ─── D'AMBROSIO'S ─── 24 HOURS ─── BREAKFAST SERVED ALL DAY ───
"""
    })
    # ROW 1: revealed after 1 wipe — the sun that sleeps
    _register_segment({
        "dir": Dir.NORTH, "row": 1,
        "tint": c_amber, "font_size": 14,
        "requires": func(): return wipe_count >= 1,
        "ascii":
"""
                          ░░░░
                       ░░░▒▒▒▒░░░             ┐
                     ░▒▒▒▓▓▓▓▓▓▒▒░       the sun
                    ░▒▓▓▓▓██▓██▓▓▒░     outside the
                    ░▒▓▓▓██████▓▓▒░     awnings:
                     ░▒▒▓▓▓▓▓▓▓▒▒░      it sleeps.
                       ░░▒▒▒▒▒░░             ┘
                          ────
"""
    })
    # ROW 2: revealed at 8 wipes — distant constellation
    _register_segment({
        "dir": Dir.NORTH, "row": 2,
        "tint": c_amber_dim, "font_size": 11,
        "requires": func(): return wipe_count >= 8,
        "ascii":
"""
       ✦                                                     ✦
              ·     ✦                            ·
                            ·       ✦                ·
       ·             ✦                                       ✦
                                          ·
            ✦              ─── HE'S JOURNEY ───            ·
                              hasn't started; it's
                              always about to start
       ·                                                     ✦
              ✦                            ·       ✦
"""
    })
    # ROW 3: revealed after reading oracle — the whole sky breaks open
    _register_segment({
        "dir": Dir.NORTH, "row": 3,
        "tint": c_amber, "font_size": 11,
        "requires": func(): return oracle_read,
        "ascii":
"""
                ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
              ░░▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░
            ░░▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░
          ░▒▒▓▓▓▓████████████████████████▓▓▓▓▒▒▒▒░
        ░▒▓▓████████ INFINITE POTENTIAL ████████▓▓▒░
          ░▒▒▓▓▓▓████████████████████████▓▓▓▓▒▒▒▒░
            ░░▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░
              ░░▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░
"""
    })

    # ── SOUTH — water / cliff / underworld ────────────────────
    # ROW 0: always — the precipice line + foam
    _register_segment({
        "dir": Dir.SOUTH, "row": 0,
        "tint": c_water_dim, "font_size": 12,
        "requires": null,
        "ascii":
"""

   ═══════ THE PRECIPICE ═══════════════════════════════════ ════
       │ │ │   │  │     │   │ │   │   │   │ │  │  │  │   │  │
    ≈≈ ~ ≈≈≈≈ ~~ ≈≈≈≈≈≈ ~~~ ≈≈≈ ~~~ ≈≈≈ ~ ≈≈ ~~ ≈ ~~~ ≈≈ ~~~ ≈≈
       ~ ≈≈≈ ~~~ ≈≈ ~~~~~~ ≈≈≈ ~ ≈≈≈ ~~~ ≈≈≈ ~~ ≈≈ ~ ≈≈≈≈ ~ ≈≈
"""
    })
    # ROW 1: water rises with wipes — 4+ shows mid-depth
    _register_segment({
        "dir": Dir.SOUTH, "row": 1,
        "tint": c_water_dim, "font_size": 11,
        "requires": func(): return wipe_count >= 4,
        "ascii":
"""
    ░░▒▒▓▓▓██████████████████████████████████████▓▓▒░
  ░▒▓▓████████████████ THE WATER RISES ███████████████▓▒░
  ░▒▓██████████████████████████████████████████████████▓▒░
    ░▒▓██████████████████████████████████████████████▓▒░
       ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""
    })
    # ROW 2: 16 wipes — drowned city below
    _register_segment({
        "dir": Dir.SOUTH, "row": 2,
        "tint": c_water_dim, "font_size": 11,
        "requires": func(): return wipe_count >= 16,
        "ascii":
"""
        ╔══════════════════════════════════════════════╗
        ║   ░░░░░  GRAUSTARK ░░░░░  SUBMERGED  ░░░░░░  ║
        ╠══════════════════════════════════════════════╣
        ║  ▓▓▓ █ ▓▓  ▓▓▓▓▓  ▓ █▓▓▓  ▓▓▓ █ ▓▓▓ ▓▓▓▓▓ ▓▓ ║
        ║  ▓ █▓▓ ▓▓▓ ▓ ▓ ▓ ▓▓ ▓▓▓ █ ▓▓ ▓▓ █▓▓ ▓ ▓ ▓▓▓ ║
        ║   "the 24-hour diner of the soul"             ║
        ║    " where you never actually leave"          ║
        ╚══════════════════════════════════════════════╝
"""
    })
    # ROW 3: 64 wipes — the bottom
    _register_segment({
        "dir": Dir.SOUTH, "row": 3,
        "tint": c_water, "font_size": 11,
        "requires": func(): return wipe_count >= 64,
        "ascii":
"""
              ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
             ░░ ALT PROLOGUE · KEYSTONE ENGAGED ░░
              ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
                ◆──────────────────────────◆
                    REVERSED · UPRIGHT
                ◆──────────────────────────◆
"""
    })

    # ── EAST — the journey forward ────────────────────────────
    # ROW 0: always — the road
    _register_segment({
        "dir": Dir.EAST, "row": 0,
        "tint": c_ash, "font_size": 11,
        "requires": null,
        "ascii":
"""
              ▓▓
            ▓▓▒▒
          ▓▒▒░░░
        ▒░░░░░    →  →  →
      ░░░░░     ╔═══════╗
    ░░░░       ║   II  ║
   ░░░        ║       ║
   ░          ╚═══════╝
   .          PRECIPICE
   ..            DOOR
   ...
"""
    })
    # ROW 1: paw prints — after dog hotspot click
    _register_segment({
        "dir": Dir.EAST, "row": 1,
        "tint": c_ash, "font_size": 11,
        "requires": func(): return dog_clicks >= 1,
        "ascii":
"""

      ·   ·
        ·       ·   ·         ·       ·
      ·   ·       ·   ·     ·   ·
                        ·       ·       ·
                             ·   ·
              the dog walks
              east as well
"""
    })

    # ── WEST — what's behind / D'Ambrosio's ───────────────────
    # ROW 0: always — the counter
    _register_segment({
        "dir": Dir.WEST, "row": 0,
        "tint": c_ash, "font_size": 11,
        "requires": null,
        "ascii":
"""
              ┌───────────────────────────┐
              │        D'AMBROSIO'S       │
              │      open 24. always.     │
              │ ░░░░░░░░░░░░░░░░░░░░░░░░░ │
              │                           │
              │  ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ │
              │  the COUNTER stretches    │
              │  the COUNTER stretches    │
              │  the COUNTER stretches    │
              └───────────────────────────┘
"""
    })
    # ROW 1: rag on counter — after 1 wipe
    _register_segment({
        "dir": Dir.WEST, "row": 1,
        "tint": c_ash, "font_size": 11,
        "requires": func(): return wipe_count >= 1,
        "ascii":
"""
                   ▒▒▒▒▒▒▒
                 ▒▒░░░░░░░░░▒▒
                ▒▒░░  RAG  ░░▒▒
                 ▒▒░░░░░░░░░▒▒
                   ▒▒▒▒▒▒▒
              wipe. wipe. wipe.
              the formica is the same.
"""
    })


# ── Interactions ────────────────────────────────────────────────
func _do_wipe() -> void:
    wipe_count += 1
    wipe_btn.text = "  WIPE THE COUNTER  ( %d / 64 )" % wipe_count
    _active_notes.append({
        "time": 0.0, "freq": 130.0 + randf() * 30,
        "wave": "triangle", "atk": 0.005, "dur": 0.18, "rel": 0.15,
    })
    SaveSystem.mark_unlocked("lore:counter_wiped_again")
    if wipe_count == 64:
        SaveSystem.mark_unlocked("vol5_alt_prologue_unlocked")
        status_label.text = "64 WIPES — the bottom revealed below."
    elif wipe_count % 8 == 0:
        status_label.text = "wipe %d — the south extends." % wipe_count
    else:
        status_label.text = "(wipe.)"


func _on_hotspot(hs: Dictionary) -> void:
    super(hs)
    var hs_id := str(hs.get("id",""))
    if "dog" in hs_id:
        dog_clicks += 1
        status_label.text = "the dog noticed. paw-prints extend east."
    elif "design_notes" in hs_id or "card_reading" in hs_id \
            or "oracle" in hs_id:
        oracle_read = true
        status_label.text = "oracle read. the sky breaks open above."
    else:
        status_label.text = "[ %s ]" % str(hs.get("interact", hs_id))


func _input(event: InputEvent) -> void:
    super(event)
    if event is InputEventKey and event.pressed and not event.echo:
        match event.keycode:
            KEY_SPACE:
                _do_wipe()
                get_viewport().set_input_as_handled()
            KEY_W:     pan_by(Vector2(0, -80))
            KEY_S:     pan_by(Vector2(0, 80))
            KEY_A:     pan_by(Vector2(-80, 0))
            KEY_D:     pan_by(Vector2(80, 0))
            KEY_UP:    pan_by(Vector2(0, -80))
            KEY_DOWN:  pan_by(Vector2(0, 80))
            KEY_LEFT:  pan_by(Vector2(-80, 0))
            KEY_RIGHT: pan_by(Vector2(80, 0))
