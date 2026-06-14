extends "res://scenes/menu/TarotVisualizerBase.gd"
## FoolVisualizer — deep tableau, console, memory, time-of-day.
##
## The painted card sits at the center of a 3200×3200 canvas.
## ASCII tableau segments unfold in N/S/E/W as the player progresses
## through wipes, hotspot clicks, console commands, and discoveries.
##
## Beyond the tableau, this visualizer carries:
##
##   • BBS CONSOLE in the bottom strip — typed commands trigger
##     reveals. Public commands: help / wipe / bark / oracle / clear.
##     Hidden commands (no help listing): dance · sleep · coffee ·
##     customer · frasier · dream · step · stay · pray · sink · feed ·
##     count · look · listen · memory · recall · 64 · time · fool.
##
##   • COUNTER STATE TRACKER — every interaction logs a "memory"
##     entry. `memory` or `recall` prints the full discovery log.
##
##   • TIME-OF-DAY drift — the chapter is at 3:47 AM. Real wall-clock
##     time pushes the visual mood ever-so-slightly toward dawn via
##     a subtle modulate shift on the painted card.
##
##   • CROSS-CARD ECHOES — clicking certain hotspots fires unlocks
##     that show up in other cards' puzzle states (the meta-system
##     the chapter's BBS header points at).

# ── Game state ───────────────────────────────────────────────────
var wipe_count: int = 0
var pet_count: int = 0
var fall_count: int = 0
var bindle_examined: bool = false
var graffiti_seen: bool = false
var oracle_read: bool = false
var dog_clicks: int = 0     # legacy alias for pet_count
var hotspots_seen: Dictionary = {}     # hs_id -> true
var commands_run: Dictionary = {}      # cmd -> count
var memory: PackedStringArray = []     # discovery log
var time_phase: float = 0.0            # 0=midnight 1=dawn
var tableau_pulse: float = 0.0         # audio-reactive ASCII tint

# Stickers / labels that unlock as you go
var stickers_unlocked: int = 0

# ── UI refs ──────────────────────────────────────────────────────
var wipe_btn: Button
var status_label: Label
var console_input: LineEdit
var console_log: RichTextLabel


func _init() -> void:
	_card_path  = "res://assets/gallery/fool.png"
	_composition_path = "fool_card"   # mosaic-block substrate centerpiece
	_hooks_path = "res://resources/puzzle_hooks/fool.json"
	_ambient_audio_path = "res://assets/audio/bgm/title_theme.ogg"
	C_BG = Color(0.040, 0.034, 0.020)
	C_GOLD = Color(0.85, 0.66, 0.29)
	C_GOLD_HI = Color(1.0, 0.85, 0.40)


func _build_chrome() -> void:
	super()
	_build_bottom_strip()
	_build_card_hotspots()


# Per-region mechanics on the painted Fool: each rect over the card
# triggers a distinct action.
#   WIPE   — John's hand+rag (center-low)
#   PET    — the dog (left of John)
#   FALL   — the bindle bag / journey-stick (upper-left, the leap)
#   READ   — the inner Fool card preview (oracle text)
#   TAG    — the FRANKLY/FOOLISH graffiti (upper-right wall)
func _build_card_hotspots() -> void:
	if card_rect == null: return
	var defs := [
		["wipe",  Rect2(0.40, 0.58, 0.20, 0.16), "wipe the counter",     _do_wipe],
		["pet",   Rect2(0.20, 0.50, 0.16, 0.30), "pet the dog",          _do_pet],
		["fall",  Rect2(0.28, 0.10, 0.12, 0.18), "take the leap",        _do_fall],
		["read",  Rect2(0.03, 0.10, 0.13, 0.40), "read the inner card",  _do_read_oracle],
		["tag",   Rect2(0.72, 0.05, 0.20, 0.10), "examine the graffiti", _do_tag],
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
		sb.bg_color = Color(1, 0.85, 0.40, 0.0)
		sb.border_color = Color(1, 0.85, 0.40, 0.0)
		sb.set_border_width_all(1)
		btn.add_theme_stylebox_override("normal", sb)
		var bsh := sb.duplicate() as StyleBoxFlat
		bsh.bg_color = Color(1, 0.85, 0.40, 0.22)
		bsh.border_color = Color(1, 0.85, 0.40, 0.70)
		btn.add_theme_stylebox_override("hover", bsh)
		btn.add_theme_stylebox_override("focus", bsh)
		btn.pressed.connect(d[3])
		canvas.add_child(btn)


func _build_bottom_strip() -> void:
	# Bottom is taller now — accommodates BBS console + wipe row
	var bot := PanelContainer.new()
	bot.anchor_left = 0; bot.anchor_right = 1
	bot.anchor_top = 1;  bot.anchor_bottom = 1
	bot.offset_top = -160
	var bps := StyleBoxFlat.new()
	bps.bg_color = Color(0, 0, 0, 0.78)
	bps.border_color = C_GOLD
	bps.border_width_top = 1
	bot.add_theme_stylebox_override("panel", bps)
	add_child(bot)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 2)
	bot.add_child(vbox)

	# Console log
	console_log = RichTextLabel.new()
	console_log.bbcode_enabled = true
	console_log.scroll_following = true
	console_log.size_flags_vertical = Control.SIZE_EXPAND_FILL
	console_log.add_theme_font_size_override("normal_font_size", 11)
	console_log.add_theme_color_override("default_color",
		Color(0.30, 0.95, 0.45))
	vbox.add_child(console_log)

	# Console input row
	var inrow := HBoxContainer.new()
	inrow.add_theme_constant_override("separation", 4)
	var prompt := Label.new()
	prompt.text = "> "
	prompt.add_theme_color_override("font_color", Color(0.95, 0.62, 0.18))
	prompt.add_theme_font_size_override("font_size", 12)
	inrow.add_child(prompt)
	console_input = LineEdit.new()
	console_input.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	console_input.add_theme_color_override("font_color",
		Color(0.30, 0.95, 0.45))
	console_input.text_submitted.connect(_on_command)
	inrow.add_child(console_input)
	vbox.add_child(inrow)

	# Bottom action row — big wipe button + status + counters
	var actrow := HBoxContainer.new()
	actrow.add_theme_constant_override("separation", 12)
	vbox.add_child(actrow)

	# Compact multi-mechanic tally — wipe is one of several actions
	# now, so the giant WIPE button is replaced by a single small
	# readout that updates per-mechanic.
	wipe_btn = Button.new()
	wipe_btn.text = "  ░ wipe 0 · pet 0 · fall 0 ░  "
	wipe_btn.add_theme_color_override("font_color", C_GOLD_HI)
	wipe_btn.add_theme_font_size_override("font_size", 11)
	var wbs := StyleBoxFlat.new()
	wbs.bg_color = Color(C_GOLD.r * 0.25, C_GOLD.g * 0.25, C_GOLD.b * 0.25, 0.5)
	wbs.border_color = C_GOLD
	wbs.set_border_width_all(1)
	wipe_btn.add_theme_stylebox_override("normal", wbs)
	var wbh := wbs.duplicate() as StyleBoxFlat
	wbh.bg_color = Color(C_GOLD.r * 0.5, C_GOLD.g * 0.5, C_GOLD.b * 0.5, 0.7)
	wbh.border_color = C_GOLD_HI
	wipe_btn.add_theme_stylebox_override("hover", wbh)
	wipe_btn.pressed.connect(_do_wipe)
	wipe_btn.tooltip_text = "click the card regions for distinct actions"
	actrow.add_child(wipe_btn)

	status_label = Label.new()
	status_label.text = "click the card · wipe · pet · fall · read · tag"
	status_label.add_theme_color_override("font_color",
		Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.7))
	status_label.add_theme_font_size_override("font_size", 10)
	status_label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	status_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	actrow.add_child(status_label)

	_log("[color=#d8a060]> 3:47 AM · D'AMBROSIO'S · between acts.[/color]")
	_log("[color=#7a5828]> type [color=#ffd896]help[/color] for visible commands.[/color]")
	_log("[color=#3a2614]> (some commands are not listed.)[/color]")

	console_input.grab_focus()


# ── Tableau registration ─────────────────────────────────────────
func _build_thematic_widget() -> void:
	var c_amber := Color(0.95, 0.74, 0.32, 1.0)
	var c_amber_dim := Color(0.55, 0.40, 0.18, 0.9)
	var c_amber_hot := Color(1.00, 0.92, 0.50, 1.0)
	var c_water := Color(0.45, 0.65, 0.75, 0.9)
	var c_water_dim := Color(0.20, 0.32, 0.42, 0.85)
	var c_water_deep := Color(0.10, 0.20, 0.30, 0.9)
	var c_ash := Color(0.60, 0.54, 0.40, 0.9)
	var c_ash_dim := Color(0.35, 0.30, 0.20, 0.85)
	var c_door := Color(0.30, 0.85, 0.42, 0.85)
	var c_red := Color(0.85, 0.35, 0.30, 0.9)
	var c_dream := Color(0.65, 0.45, 0.85, 0.85)

	# ────────────────────────────────────────────────────────────
	# NORTH — sky / dream / above
	# ────────────────────────────────────────────────────────────
	_register_segment({"dir": Dir.NORTH, "row": 0, "tint": c_amber_dim,
		"font_size": 13, "requires": null,
		"ascii":
"""
				 .       .   .    ░░░░░░░░       .       .
			░░░░░░  ░░▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░  ▒▒░░░░░░
	   ░░▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░
   ─── D'AMBROSIO'S ─── 24 HOURS ─── BREAKFAST ALWAYS ───
"""
	})
	_register_segment({"dir": Dir.NORTH, "row": 1, "tint": c_amber,
		"font_size": 14,
		"requires": func(): return wipe_count >= 1,
		"ascii":
"""
					   ░░░░
					░░▒▒▒▒░░             ┐ the sun
				  ░▒▒▓▓▓▓▓▓▒▒░     outside the awnings:
				 ░▒▓▓▓██▓██▓▒░         it sleeps.
				  ░▒▒▓▓▓▓▓▓▓▒░             ┘
					   ────
"""
	})
	_register_segment({"dir": Dir.NORTH, "row": 2, "tint": c_amber_dim,
		"font_size": 11,
		"requires": func(): return wipe_count >= 8,
		"ascii":
"""
	✦                    ·     ✦              ·              ✦
			·    ─── HE'S JOURNEY HASN'T STARTED ───      ·
					   it's always about to.
	·                                                          ✦
"""
	})
	_register_segment({"dir": Dir.NORTH, "row": 3, "tint": c_amber_hot,
		"font_size": 11,
		"requires": func(): return oracle_read,
		"ascii":
"""
		░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
	  ░░▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░
	░░▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░
  ░▒▒▓▓████████ INFINITE  POTENTIAL ████████▓▓▒▒░
	░░▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░
		░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""
	})
	# NEW NORTH 4: dog moon
	_register_segment({"dir": Dir.NORTH, "row": 4, "tint": c_dream,
		"font_size": 11,
		"requires": func(): return dog_clicks >= 3,
		"ascii":
"""
			╔══════════════════════════════════╗
			║       ▒▒▒▒                       ║
			║     ▒▒░░░░▒▒    the dog          ║
			║    ▒░░░░░░░░▒    knows the moon  ║
			║     ▒▒░░░░▒▒     by its smell.   ║
			║       ▒▒▒▒                       ║
			╚══════════════════════════════════╝
"""
	})
	# NEW NORTH 5: type 'dream'
	_register_segment({"dir": Dir.NORTH, "row": 5, "tint": c_dream,
		"font_size": 11,
		"requires": func(): return commands_run.get("dream", 0) >= 1,
		"ascii":
"""
			░▒░▒░ THE DREAM LAYER ░▒░▒░
			  ▒░░  Frasier walks in     ░▒
			░░░░░░  before he walks in. ░░░░░
			  ▒░░░ the bell rings ░░░▒
				  ░░ before. ░░
"""
	})
	# NEW NORTH 6: graffiti tag
	_register_segment({"dir": Dir.NORTH, "row": 6, "tint": c_red,
		"font_size": 12,
		"requires": func(): return wipe_count >= 32,
		"ascii":
"""
			  ╔═══════════════════════════╗
			  ║  ░▒▓█  FRANKLY  █▓▒░       ║
			  ║       ░▒▓█  FOOLISH  █▓▒░ ║
			  ║   ─ author signature ─    ║
			  ╚═══════════════════════════╝
"""
	})
	# NEW NORTH 7: all hotspots seen
	_register_segment({"dir": Dir.NORTH, "row": 7, "tint": c_amber_hot,
		"font_size": 12,
		"requires": func(): return hotspots_seen.size() >= 6,
		"ascii":
"""
			░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
		  ░▒▒▓▓████ THE SUN FINALLY RISES ████▓▓▒▒░
			░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
			  the day that doesn't end
			  because it never quite began
"""
	})

	# ────────────────────────────────────────────────────────────
	# SOUTH — water / underworld
	# ────────────────────────────────────────────────────────────
	_register_segment({"dir": Dir.SOUTH, "row": 0, "tint": c_water_dim,
		"font_size": 12, "requires": null,
		"ascii":
"""

   ════════ THE PRECIPICE ═════════════════════════════════
	   │ │ │   │  │     │   │ │   │   │   │ │  │  │  │   │
	≈≈ ~ ≈≈≈≈ ~~ ≈≈≈≈≈≈ ~~~ ≈≈≈ ~~~ ≈≈≈ ~ ≈≈ ~~ ≈ ~~~ ≈≈
	   ~ ≈≈≈ ~~~ ≈≈ ~~~~~~ ≈≈≈ ~ ≈≈≈ ~~~ ≈≈≈ ~~ ≈≈ ~ ≈≈≈≈
"""
	})
	_register_segment({"dir": Dir.SOUTH, "row": 1, "tint": c_water_dim,
		"font_size": 11,
		"requires": func(): return wipe_count >= 4,
		"ascii":
"""
	░░▒▒▓▓████████████████████████████████████████▓▓▒░
  ░▒▓▓████████████ THE WATER RISES ████████████████▓▒░
  ░▒▓██████████████████████████████████████████████▓▒░
	░▒▓██████████████████████████████████████████▓▒░
	   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""
	})
	_register_segment({"dir": Dir.SOUTH, "row": 2, "tint": c_water_dim,
		"font_size": 11,
		"requires": func(): return wipe_count >= 16,
		"ascii":
"""
		╔══════════════════════════════════════════╗
		║   ░░░░░  GRAUSTARK ░░░░░  SUBMERGED  ░░  ║
		╠══════════════════════════════════════════╣
		║  ▓▓▓ █ ▓▓ ▓▓▓▓▓ ▓ █▓▓▓ ▓▓▓ █ ▓▓▓ ▓▓▓▓▓ ║
		║  ▓ █▓▓ ▓▓▓ ▓ ▓ ▓ ▓▓ ▓▓▓ █ ▓▓ ▓▓ █▓▓ ▓ ▓ ║
		║   "the 24-hour diner of the soul"        ║
		║    "where you never actually leave"      ║
		╚══════════════════════════════════════════╝
"""
	})
	_register_segment({"dir": Dir.SOUTH, "row": 3, "tint": c_water,
		"font_size": 11,
		"requires": func(): return wipe_count >= 64,
		"ascii":
"""
			  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
			 ░░ ALT PROLOGUE · KEYSTONE ENGAGED ░░
			  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
				◆──────────────────────────◆
					REVERSED · UPRIGHT
				◆──────────────────────────◆
"""
	})
	# NEW SOUTH 4: type 'sink'
	_register_segment({"dir": Dir.SOUTH, "row": 4, "tint": c_water_deep,
		"font_size": 10,
		"requires": func(): return commands_run.get("sink", 0) >= 1,
		"ascii":
"""
		  ▒▓▓▓▓▓▓▓ UNDERWATER D'AMBROSIO'S ▓▓▓▓▓▓▓▒
		▓▓▓ the bell rings · no one sits ▓▓▓
	  ▓▓▓▓ the coffee pot drowns · slowly ▓▓▓▓
		▓▓▓ the dog's bowl floats up · empty ▓▓▓
		  ▒▓▓▓▓ John wipes ░ wipes ░ wipes ▓▓▓▓▒
"""
	})
	# NEW SOUTH 5: bindle click
	_register_segment({"dir": Dir.SOUTH, "row": 5, "tint": c_ash_dim,
		"font_size": 11,
		"requires": func(): return hotspots_seen.has("fool_bindle"),
		"ascii":
"""
					   ▒▒▓▒▒
					  ▒░▒░░░▒
					 ▒░ ▒░░░░▒        the bindle
					 ▒░░░░░░░░▒       drifts out to sea
					  ▒░▒░░░▒          containing:
					   ▒▒░▒▒          nothing
									   and everything
"""
	})
	# NEW SOUTH 6: type 'fool' (self-aware moment)
	_register_segment({"dir": Dir.SOUTH, "row": 6, "tint": c_amber,
		"font_size": 11,
		"requires": func(): return commands_run.get("fool", 0) >= 1,
		"ascii":
"""
			  ╔══════════════════════════════════╗
			  ║   "fool" — a command typed by   ║
			  ║         someone who knew this    ║
			  ║         was a card to be read   ║
			  ║         not a place to live in  ║
			  ║                                  ║
			  ║       you stepped THROUGH        ║
			  ║       (the fool's leap)          ║
			  ╚══════════════════════════════════╝
"""
	})
	# NEW SOUTH 7: 100 wipes — beyond
	_register_segment({"dir": Dir.SOUTH, "row": 7, "tint": c_dream,
		"font_size": 11,
		"requires": func(): return wipe_count >= 100,
		"ascii":
"""
	   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
	 ░░▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░
	   100 WIPES — THE FOOL SURFACES IN ANOTHER LIFE
	   another counter ░ another rag ░ another dog
	 ░░▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░
	   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""
	})

	# ────────────────────────────────────────────────────────────
	# EAST — journey forward
	# ────────────────────────────────────────────────────────────
	_register_segment({"dir": Dir.EAST, "row": 0, "tint": c_ash,
		"font_size": 11, "requires": null,
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
	_register_segment({"dir": Dir.EAST, "row": 1, "tint": c_ash,
		"font_size": 11,
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
	# NEW EAST 2: wipe ≥ 8 — human footprints
	_register_segment({"dir": Dir.EAST, "row": 2, "tint": c_ash,
		"font_size": 11,
		"requires": func(): return wipe_count >= 8,
		"ascii":
"""

	  ▐█▌                                       ▐█▌
		▐█▌                                   ▐█▌
		  ▐█▌   the apron is heavy           ▐█▌
			▐█▌  but the door is open      ▐█▌
			  ▐█▌                        ▐█▌
				─── eight steps so far ───
"""
	})
	# NEW EAST 3: 5 dog clicks
	_register_segment({"dir": Dir.EAST, "row": 3, "tint": c_ash,
		"font_size": 11,
		"requires": func(): return dog_clicks >= 5,
		"ascii":
"""
			  ┌─────────────────────────────┐
			  │  the dog leads now.         │
			  │  ▒▒▓▓ noses east ▓▓▒▒       │
			  │  ▒▒▓▓ tail forward ▓▓▒▒    │
			  │  ▒▒▓▓ knows the route ▓▓▒▒ │
			  │  ▒▒▓▓ better than you ▓▓▒▒ │
			  └─────────────────────────────┘
"""
	})
	# NEW EAST 4: type 'step'
	_register_segment({"dir": Dir.EAST, "row": 4, "tint": c_door,
		"font_size": 12,
		"requires": func(): return commands_run.get("step", 0) >= 1,
		"ascii":
"""

	   ╔═══════════════════════════════════════╗
	   ║                                       ║
	   ║      ─→  THE DOOR  →   →   →  →       ║
	   ║                                       ║
	   ║       you typed STEP.                ║
	   ║       the door swings.                ║
	   ║                                       ║
	   ╚═══════════════════════════════════════╝
				╲    OPENING    ╱
				 ╲             ╱
				  ╲   ▓▓▓▓▓   ╱
				   ╲ ░▒▓█▓▒░ ╱
					▓▓▓▓▓▓▓▓
"""
	})
	# NEW EAST 5: 32 wipes — far diner appears
	_register_segment({"dir": Dir.EAST, "row": 5, "tint": c_ash_dim,
		"font_size": 10,
		"requires": func(): return wipe_count >= 32,
		"ascii":
"""

							  ░░
							░░░░░░
						  ▒▒▓▓▓▓▒▒
						▒▒▓████▓▒▒
					   ▒▒▓██████▓▒▒
					  ▒▒▒▒▒▒▒▒▒▒▒▒▒
					  ─── another diner ───
					   ─── due east ───
					   ─── 24 hours ───
					   ─── same menu ───
"""
	})
	# NEW EAST 6: all hotspots — journey resumes
	_register_segment({"dir": Dir.EAST, "row": 6, "tint": c_amber_hot,
		"font_size": 11,
		"requires": func(): return hotspots_seen.size() >= 8,
		"ascii":
"""

			  ╔════════════════════════════════╗
			  ║   ░ THE JOURNEY RESUMES ░       ║
			  ║                                ║
			  ║   ➜ bindle on stick             ║
			  ║   ➜ dog at heel                 ║
			  ║   ➜ rag in apron pocket         ║
			  ║   ➜ counter still wet           ║
			  ║                                ║
			  ║   step where the path appears   ║
			  ║   the path appears when you do  ║
			  ╚════════════════════════════════╝
"""
	})

	# ────────────────────────────────────────────────────────────
	# WEST — past / what's behind
	# ────────────────────────────────────────────────────────────
	_register_segment({"dir": Dir.WEST, "row": 0, "tint": c_ash,
		"font_size": 11, "requires": null,
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
	_register_segment({"dir": Dir.WEST, "row": 1, "tint": c_ash,
		"font_size": 11,
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
	# NEW WEST 2: type 'customer'
	_register_segment({"dir": Dir.WEST, "row": 2, "tint": c_ash_dim,
		"font_size": 10,
		"requires": func(): return commands_run.get("customer", 0) >= 1,
		"ascii":
"""

				░░░░░░░░░░░░░░░░░░░░░░░░░░
			  ░░ stool 4 is occupied        ░░
			  ░░ by nobody you can see       ░░
			  ░░ they always order:          ░░
			  ░░   ▓ coffee, black           ░░
			  ░░   ▓ no toast                ░░
			  ░░   ▓ a quiet booth in 1971   ░░
				░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""
	})
	# NEW WEST 3: 16 wipes — ledger
	_register_segment({"dir": Dir.WEST, "row": 3, "tint": c_ash,
		"font_size": 10,
		"requires": func(): return wipe_count >= 16,
		"ascii":
"""

	   ╔══════════════════════════════════════╗
	   ║      LEDGER OF NAMES                ║
	   ║      every customer he served:      ║
	   ╠══════════════════════════════════════╣
	   ║  ░ Frasier T. ░ Marie ░ Hal ░ Curtis ║
	   ║  ░ Joan ░ Pete ░ a man in a coat ░  ║
	   ║  ░ the girl who never ordered ░     ║
	   ║  ░ 14 others he forgot the names of ║
	   ║  ░ 1 he refuses to forget           ║
	   ╚══════════════════════════════════════╝
"""
	})
	# NEW WEST 4: 3 dog clicks — bowl
	_register_segment({"dir": Dir.WEST, "row": 4, "tint": c_ash,
		"font_size": 11,
		"requires": func(): return dog_clicks >= 3,
		"ascii":
"""

				  ╭──────────╮
				  │░░░░░░░░░░│
				  │░  DOG   ░│
				  │░░░░░░░░░░│
				  ╰──────────╯
			  empty.  it has been
			  empty since closing time.
			  closing time was eleven years ago.
"""
	})
	# NEW WEST 5: graffiti hotspot
	_register_segment({"dir": Dir.WEST, "row": 5, "tint": c_red,
		"font_size": 12,
		"requires": func(): return hotspots_seen.has("fool_graffiti"),
		"ascii":
"""
				╔══════════════════════════╗
				║   ░░▒▒▓▓  F R A N K L Y  ║
				║   ▓▓▒▒░░  FRANKLY  ░░▒▒▓▓║
				║   ─ the author signs ─   ║
				║   ─ on the brick wall ─  ║
				║   ─ visible from booth 6 ─║
				╚══════════════════════════╝
"""
	})
	# NEW WEST 6: 64 wipes — same forever
	_register_segment({"dir": Dir.WEST, "row": 6, "tint": c_amber,
		"font_size": 11,
		"requires": func(): return wipe_count >= 64,
		"ascii":
"""
	   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
	   ▒  the counter ░ the rag ░ the formica ▒
	   ▒  the same ░ the same ░ the same      ▒
	   ▒  ░ even the customers are the same   ▒
	   ▒  ░ even the customers are no one    ▒
	   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""
	})

	# ────────────────────────────────────────────────────────────
	# PET milestones — tableau grows around the dog
	# ────────────────────────────────────────────────────────────
	_register_segment({"dir": Dir.WEST, "row": 7, "tint": c_amber,
		"font_size": 11,
		"requires": func(): return pet_count >= 5,
		"ascii":
"""
				╭──────────────────────╮
				│   ░▒▓ THE DOG ▓▒░    │
				│  she's leaned in     │
				│  ▒░ five times now ░▒│
				│  her name is on the  │
				│  tip of his tongue.  │
				╰──────────────────────╯
"""
	})
	_register_segment({"dir": Dir.NORTH, "row": 8, "tint": c_dream,
		"font_size": 11,
		"requires": func(): return pet_count >= 10,
		"ascii":
"""
			  ▒▒▒▒                       ▒▒▒▒
			▒▒░░░░▒▒        ten          ▒▒░░░░▒▒
		   ▒░░░░░░░░▒    ▒  pets later   ▒░░░░░░░░▒
			▒▒░░░░▒▒    ▒    he calls   ▒▒░░░░▒▒
			  ▒▒▒▒      ▒    her FAITH.   ▒▒▒▒
						▒
"""
	})

	# ────────────────────────────────────────────────────────────
	# FALL milestones — the leap proper
	# ────────────────────────────────────────────────────────────
	_register_segment({"dir": Dir.SOUTH, "row": 8, "tint": c_dream,
		"font_size": 11,
		"requires": func(): return fall_count >= 1,
		"ascii":
"""
						╱
					   ╱
					  ╱     one foot off
					 ╱     the other still
					╱      wiping. always
				   ╱       still wiping.
				  ╱
"""
	})
	_register_segment({"dir": Dir.SOUTH, "row": 9, "tint": c_red,
		"font_size": 11,
		"requires": func(): return fall_count >= 3,
		"ascii":
"""
			  ╔══════════════════════════════════╗
			  ║   ░▒▓ THE LEAP ▓▒░               ║
			  ║  the diner shrinks behind you    ║
			  ║  the dog watches calmly          ║
			  ║  she does not bark               ║
			  ║  she knows you'll come back      ║
			  ║  she knows you'll fall again     ║
			  ╚══════════════════════════════════╝
"""
	})
	_register_segment({"dir": Dir.EAST, "row": 7, "tint": c_amber_hot,
		"font_size": 11,
		"requires": func(): return fall_count >= 5,
		"ascii":
"""
			  the moon falls sideways.
			  you fall the same way.
				  ◐ ◑ ◐ ◑ ◐ ◑
			  landing was always optional.
			  ─── five leaps in ───
			  ─── infinity to go ───
"""
	})

	# ────────────────────────────────────────────────────────────
	# TAG / graffiti — author signature thread
	# ────────────────────────────────────────────────────────────
	_register_segment({"dir": Dir.EAST, "row": 8, "tint": c_red,
		"font_size": 11,
		"requires": func(): return graffiti_seen,
		"ascii":
"""
			  ▒▓█  FRANKLY · FOOLISH  █▓▒
			  the author admits
			  to having signed
			  the dream they wrote
			  ─── the diner is a card ───
			  ─── you are reading it ───
"""
	})


# ── Mechanics ────────────────────────────────────────────────────
func _do_pet() -> void:
	pet_count += 1
	dog_clicks = pet_count   # keep tableau predicates working
	_refresh_tally()
	_active_notes.append({"time":0.0,"freq":420.0,"wave":"square",
		"atk":0.001,"dur":0.06,"rel":0.10})
	_memorize("pet #%d" % pet_count)
	status_label.text = ["the dog leans into your hand.",
		"the dog wags. tail tracks east.",
		"the dog yips once, quietly.",
		"the dog rests her head on your shoe.",
		"the dog knows your weight by name."][pet_count % 5]
	_log("[color=#ffd896]· pet #%d.  %s[/color]" % [pet_count, status_label.text])


func _do_fall() -> void:
	fall_count += 1
	_refresh_tally()
	_active_notes.append({"time":0.0,"freq":80.0,"wave":"sawtooth",
		"atk":0.001,"dur":0.45,"rel":0.6})
	_memorize("fall #%d" % fall_count)
	var lines := ["one foot off. the other still wiping.",
		"two feet off. the dog watches calmly.",
		"no feet. the diner shrinks behind.",
		"you don't land. you don't have to.",
		"you fall the way the moon falls — sideways."]
	status_label.text = lines[min(fall_count - 1, lines.size() - 1)]
	_log("[color=#a878e0]· fall #%d.  %s[/color]" % [fall_count, status_label.text])
	SaveSystem.mark_unlocked("vol5_fool_leap_%d" % fall_count)


func _do_read_oracle() -> void:
	oracle_read = true
	_cmd_oracle()


func _do_tag() -> void:
	graffiti_seen = true
	hotspots_seen["fool_graffiti"] = true
	_memorize("tag examined")
	status_label.text = "FRANKLY · FOOLISH — the author signs."
	_log("[color=#e85530]· author signature on the brick wall.[/color]")
	SaveSystem.mark_unlocked("vol5_graffiti_signature_seen")


# ── Wipe ─────────────────────────────────────────────────────────
func _do_wipe() -> void:
	wipe_count += 1
	_refresh_tally()
	_active_notes.append({
		"time": 0.0, "freq": 130.0 + randf() * 30,
		"wave": "triangle", "atk": 0.005, "dur": 0.18, "rel": 0.15,
	})
	SaveSystem.mark_unlocked("lore:counter_wiped_again")
	_memorize("wipe #%d" % wipe_count)
	var milestones := {
		1:  "the rag appears.",
		4:  "the water begins rising.",
		8:  "constellation surfaces.",
		16: "ledger of names opens.",
		32: "a graffiti tag.  another diner appears east.",
		64: "64 WIPES — alt prologue unlocked. same forever.",
		100:"the fool surfaces in another life.",
	}
	if milestones.has(wipe_count):
		var m: String = milestones[wipe_count]
		status_label.text = m
		_log("[color=#ffd896]· %s[/color]" % m)
	else:
		status_label.text = "(wipe %d.)" % wipe_count
	if wipe_count == 64:
		SaveSystem.mark_unlocked("vol5_alt_prologue_unlocked")


func _on_hotspot(hs: Dictionary) -> void:
	super(hs)
	var hs_id := str(hs.get("id",""))
	hotspots_seen[hs_id] = true
	_memorize("hotspot: " + hs_id)
	if "dog" in hs_id:
		dog_clicks += 1
		status_label.text = "the dog noticed. east extends."
	elif "design_notes" in hs_id or "card_reading" in hs_id \
			or "oracle" in hs_id:
		oracle_read = true
		status_label.text = "oracle read. the sky breaks open."
	elif "bindle" in hs_id:
		status_label.text = "bindle examined. it drifts south."
	elif "graffiti" in hs_id:
		status_label.text = "FRANKLY tag — author signature."
	else:
		status_label.text = "[ %s ]" % str(hs.get("interact", hs_id))


# ── Console commands ─────────────────────────────────────────────
func _on_command(text: String) -> void:
	var line := text.strip_edges().to_lower()
	console_input.text = ""
	if line == "":
		return
	_log("[color=#e89c30]> %s[/color]" % text)
	commands_run[line] = int(commands_run.get(line, 0)) + 1
	_memorize("typed: " + line)
	var parts := line.split(" ", false)
	var cmd := parts[0]
	var rest := " ".join(parts.slice(1)) if parts.size() > 1 else ""

	match cmd:
		# Public
		"help", "?":
			_cmd_help()
		"wipe":
			_do_wipe()
		"pet":
			_do_pet()
		"fall", "leap", "jump":
			_do_fall()
		"tag", "graffiti":
			_do_tag()
		"bark":
			_trigger_dog_bark()
		"oracle":
			_cmd_oracle()
		"clear", "cls":
			console_log.clear()
		"graustark", "river", "delta":
			_log("[color=#c89868]  ≈≈ Graustark · the cliff is over the river · the leap is into it.[/color]")
			_log("[color=#a87858]  county road 17 follows the river east · the dog knows the route.[/color]")
		"exit", "quit", "close":
			closed.emit()
		# Memory / state
		"memory", "recall":
			_cmd_memory()
		"count", "counts":
			_cmd_count()
		"time":
			_cmd_time()
		# Hidden lore commands
		"dance":
			_log("[color=#ffd896]  the dog spins twice. nobody else sees.[/color]")
			_trigger_dog_bark()
		"sleep":
			_log("[color=#7a5828]  john nods off briefly. dream layer activates above.[/color]")
			commands_run["dream"] = int(commands_run.get("dream", 0)) + 1
		"coffee":
			_log("[color=#c8a878]  the pot's been on since closing.[/color]")
			_log("[color=#7a5828]  it tastes like 1971.[/color]")
		"customer":
			_log("[color=#c8a878]  stool 4. nobody you can see. coffee, black.[/color]")
		"frasier":
			_log("[color=#ffd896]  the bell rings.  someone walks in.[/color]")
			_log("[color=#7a5828]  the first choice. it doesn't matter.[/color]")
		"dream":
			_log("[color=#a878e0]  ▒░▒░ the dream layer opens above ░▒░▒[/color]")
		"step":
			_log("[color=#88c870]  ─→ the door swings. the precipice waits.[/color]")
		"stay":
			_log("[color=#7a5828]  the counter accepts. the formica is the same.[/color]")
		"pray":
			_log("[color=#c8a878]  there is no chapel. there is the counter.[/color]")
			_log("[color=#7a5828]  the counter is the chapel.[/color]")
		"sink":
			_log("[color=#3050aa]  the diner submerges. you can still wipe.[/color]")
		"feed":
			_log("[color=#c8a878]  the dog's bowl has been empty since closing.[/color]")
		"look":
			_cmd_look()
		"listen":
			_cmd_listen()
		"fool":
			_log("[color=#ffd896]  you typed FOOL. that means you read the card.[/color]")
			_log("[color=#7a5828]  the leap is yours.[/color]")
		"64":
			_log("[color=#ffd896]  64 is the count when the cliff floods.[/color]")
			_log("[color=#7a5828]  the count is also: ACTIVE NODES per the BBS header.[/color]")
		_:
			# Tiny easter eggs by exact line
			if line == "tip":
				_log("[color=#c8a878]  no tip jar. nobody tips a fool.[/color]")
			elif line == "rust_code.bbs":
				_log("[color=#7a5828]  you remembered the URL.[/color]")
				_log("[color=#ffd896]  the system remembers you back.[/color]")
			else:
				_log("[color=#3a2614]? unknown. try: help · memory · listen[/color]")


func _cmd_help() -> void:
	_log("[color=#d8a060]commands (visible):[/color]")
	_log("  [color=#ffd896]wipe[/color]       — wipe the counter")
	_log("  [color=#ffd896]pet[/color]        — pet the dog")
	_log("  [color=#ffd896]fall[/color]       — take the leap")
	_log("  [color=#ffd896]tag[/color]        — examine the graffiti")
	_log("  [color=#ffd896]bark[/color]       — the dog speaks")
	_log("  [color=#ffd896]oracle[/color]     — read the card")
	_log("  [color=#ffd896]memory[/color]     — what you've discovered")
	_log("  [color=#ffd896]count[/color]      — tallies")
	_log("  [color=#ffd896]time[/color]       — what time is it really")
	_log("  [color=#ffd896]look[/color]       — examine the scene")
	_log("  [color=#ffd896]listen[/color]     — what do you hear")
	_log("  [color=#ffd896]clear[/color]      — clear the console")
	_log("  [color=#ffd896]exit[/color]       — close")
	_log("[color=#7a5828](some commands are unlisted. the BBS keeps secrets.)[/color]")


func _cmd_oracle() -> void:
	var oracle = null
	for c_v in hooks.get("ciphers", []):
		var c: Dictionary = c_v
		if str(c.get("kind","")) == "inline_oracle":
			oracle = c; break
	if oracle == null:
		_log("[color=#7a5828]no oracle text found.[/color]")
		return
	_log("[color=#d8a060]── THE FOOL ──────────────────────[/color]")
	for line in oracle.get("text_lines", []):
		_log("[color=#c8a878]%s[/color]" % line)
	_log("")
	oracle_read = true
	SaveSystem.mark_unlocked("lore:fool_oracle_read")


func _cmd_memory() -> void:
	_log("[color=#d8a060]── memory · %d entries ─────[/color]" % memory.size())
	var shown := 0
	for entry in memory:
		if shown >= 20:
			_log("[color=#7a5828]  ... (%d more)[/color]" %
				 (memory.size() - shown))
			break
		_log("  [color=#c8a878]· %s[/color]" % entry)
		shown += 1


func _cmd_count() -> void:
	_log("[color=#d8a060]── tallies ─────────────────[/color]")
	_log("  wipes:        [color=#ffd896]%d / 64[/color]" % wipe_count)
	_log("  dog clicks:   [color=#ffd896]%d[/color]" % dog_clicks)
	_log("  hotspots:     [color=#ffd896]%d[/color]" %
		 hotspots_seen.size())
	_log("  oracle:       [color=#ffd896]%s[/color]" %
		 ("read" if oracle_read else "unread"))
	_log("  commands run: [color=#ffd896]%d[/color]" %
		 commands_run.size())


func _cmd_time() -> void:
	_log("[color=#d8a060]· chapter time: 3:47 AM[/color]")
	_log("[color=#c8a878]· dawn drift:   %d%%[/color]" %
		 int(time_phase * 100))
	_log("[color=#7a5828]· the dawn never quite comes.[/color]")


func _cmd_look() -> void:
	_log("[color=#c8a878]· counter ░ formica ░ rag in apron pocket[/color]")
	_log("[color=#c8a878]· the dog. her name is somewhere in the prose.[/color]")
	_log("[color=#c8a878]· a bindle on a stick. why is it there.[/color]")
	_log("[color=#c8a878]· the door labeled II. it waits.[/color]")
	_log("[color=#7a5828]· something on the brick wall. graffiti.[/color]")


func _cmd_listen() -> void:
	_log("[color=#c8a878]· fluorescent hum. always.[/color]")
	_log("[color=#c8a878]· the coffee pot, gurgling.[/color]")
	_log("[color=#c8a878]· the rag, dragging.[/color]")
	_log("[color=#7a5828]· something else. not quite a bell.[/color]")


func _trigger_dog_bark() -> void:
	_log("[color=#ffd896]  ◐ the dog barks once.[/color]")
	_active_notes.append({
		"time": 0.0, "freq": 480.0, "wave": "square",
		"atk": 0.001, "dur": 0.05, "rel": 0.08,
	})


func _memorize(entry: String) -> void:
	memory.append(entry)
	if memory.size() > 200:
		memory.remove_at(0)


func _refresh_tally() -> void:
	if wipe_btn != null:
		wipe_btn.text = "  ░ wipe %d · pet %d · fall %d ░  " % [
			wipe_count, pet_count, fall_count]


func _log(line: String) -> void:
	if console_log != null:
		console_log.append_text(line + "\n")


# ── Process / time drift / audio-reactive ASCII pulse ──────────
func _process(delta: float) -> void:
	super(delta)
	# Time-of-day drift
	time_phase = fmod(time_phase + delta / 600.0, 1.0)
	if card_rect != null:
		var dawn := 0.5 + sin(time_phase * TAU) * 0.5
		card_rect.modulate = Color(1.0 + dawn * 0.05,
									1.0 + dawn * 0.03,
									0.97 - dawn * 0.02)
	# Audio-reactive pulse running THROUGH the ASCII tableau.
	# Sample BGM magnitude (falls back to constant if no analyzer).
	# Each visible tableau segment gets its modulate alpha+tint
	# modulated by a sine wave offset by segment index — produces a
	# ripple that flows across the cardinal directions as the music
	# plays.
	tableau_pulse += delta
	var amp: float = 0.0
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("get_bgm_magnitude"):
		amp = clamp(float(am.call("get_bgm_magnitude", 80.0, 3200.0)) * 10.0,
					 0.0, 1.0)
	# Baseline so it ripples even without audio
	var base_amp = 0.10 + amp * 0.40
	var idx := 0
	for seg in _segments:
		if not seg.get("shown", false): continue
		var lbl: Label = seg.get("label")
		if lbl == null: continue
		var phase = tableau_pulse * 2.4 + idx * 0.35
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
			_do_wipe()
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
