extends "res://scenes/menu/TarotVisualizerBase.gd"
## LoversVisualizer — The Card Stays Face-Down.
##
## VI · the only major arcana whose centerpiece is its OWN ABSENCE.
## The card sits face-down on the canvas, ornate back pattern shown.
## Every hotspot is a hand reaching toward the card; the card never
## flips. The deepest reveal — the truth of the chapter — comes via
## the WAIT mechanic: nothing changes, the card remains face-down,
## that IS the answer.
##
## Already seeded in the deck:
##   Priestess journal: "VI THE LOVERS — uncast. The card stays face-down."
##   Emperor mirror:    succession reveal stops at INHERITANCE, declines romance.
##
## The chapter's geography is the GRAUSTARK RIVER — running between two
## banks where the lovers stand. Nobody crosses on this card. That
## crossing is what would flip the card. It never happens.
##
##   • CARD HOTSPOTS — six rects on the face-down card:
##       FLIP       attempt to turn the card (5 attempts then it bonds shut)
##       PAIRS      reveal the 6 implicit pairs across the deck
##       WAIT       pass a moment; the most truthful interaction
##       LISTEN     hear distant voices from other cards
##       MIRROR     the would-be Lovers' would-be mirror
##       GRAUSTARK  the river between them
##
##   • BBCS CONSOLE — `face_down:~$`. Hidden lore: lovers · refuse ·
##     uncast · justice · judgement · psyche · eros · river · anya ·
##     aria · succession · friends · plus cross-character routes.

# ── Game state ───────────────────────────────────────────────────
var flip_attempts: int = 0      # 0..5 — the card never actually flips
var pair_idx: int = 0           # 0..6 cycle through implicit pairs
var waits: int = 0
var listens: int = 0
var mirror_gazed: bool = false
var graustark_seen: bool = false
var hotspots_seen: Dictionary = {}
var commands_run: Dictionary = {}
var memory: PackedStringArray = []
var card_phase: float = 0.0
var tableau_pulse: float = 0.0
var bond_locked: bool = false   # after 5 flip attempts, the back-pattern bonds

# ── UI refs ──────────────────────────────────────────────────────
var tally_btn: Button
var status_label: Label
var console_input: LineEdit
var console_log: RichTextLabel

# Six implicit pairs across the deck, revealed via PAIRS hotspot
const PAIRS := [
	"FRASIER & ARIA · cathedral signal · data overlay · the magician hears the empress",
	"QUENTIN & ANTONIO · the friends remark · the bought time · the binding holds",
	"JOHN & FAITH · the cook and the dog · the only pair that never separated",
	"ANYA & ELICIA · across the tape · across the year · one records · one was recorded",
	"NICOLA & DANTE · succession not romance · the chair passes through the chair",
	"MAYA & Y · too young to be lovers · already shaped into the form of pairs",
]

# Flip attempts — each one fails differently
const FLIP_RESPONSES := [
	"the card resists slightly. the ornate back stays facing you.",
	"the card moves a millimetre. settles back. the pattern realigns.",
	"the card refuses. the refusal is patient, not angry.",
	"the card is heavier than it looks. heavier each attempt.",
	"the card has bonded to the table. you've used all five attempts.",
]

# Listen — what you hear from other cards when you press an ear
const LISTEN_FRAGMENTS := [
	"from the WAREHOUSE: a soldering iron, a sigil being traced.",
	"from D'AMBROSIO'S: a counter being wiped. a dog breathing.",
	"from ST. JUDE'S: a kneeler shifting. a coffee cup placed.",
	"from EMBER & ASH: a scaffold creaks. a bolt drops.",
	"from the EMPRESS' ROOM: a champagne glass tilts. an Aria packet pings.",
	"from the THRONE: a mirror, looking up.",
	"from the ARCHIVE: a cassette spool turns. tape 4 still unplayed.",
]

# Mirror — three stages of self-recognition
const MIRROR_STAGES := [
	"two figures, one looking at the other. neither moves.",
	"two figures, both looking at the mirror between them.",
	"two figures. the mirror is the river. nobody crosses.",
]


func _init() -> void:
	_card_path  = "res://assets/gallery/lovers_back.png"
	_composition_path = ""
	_hooks_path = "res://resources/puzzle_hooks/lovers.json"
	_ambient_audio_path = "res://assets/audio/bgm/vol5_riverboat_drone.ogg"
	# Tarnished gold + deep purple — the back pattern's palette
	C_BG = Color(0.060, 0.040, 0.080)
	C_GOLD = Color(0.78, 0.65, 0.42)
	C_GOLD_HI = Color(1.0, 0.85, 0.55)
	C_TEXT = Color(0.72, 0.68, 0.78)
	C_TEXT_DIM = Color(0.42, 0.32, 0.48)


func _build_chrome() -> void:
	super()
	_build_bottom_strip()
	_build_card_hotspots()


# Per-region hotspots on the face-down card.
func _build_card_hotspots() -> void:
	if card_rect == null: return
	var defs := [
		["flip",      Rect2(0.30, 0.20, 0.40, 0.60), "attempt to flip the card",   _do_flip],
		["pairs",     Rect2(0.05, 0.78, 0.40, 0.18), "cycle implicit pairs",       _do_pairs],
		["wait",      Rect2(0.65, 0.04, 0.25, 0.10), "wait",                       _do_wait],
		["listen",    Rect2(0.04, 0.04, 0.22, 0.12), "listen to other cards",      _do_listen],
		["mirror",    Rect2(0.74, 0.42, 0.18, 0.30), "look in the mirror",         _do_mirror],
		["graustark", Rect2(0.10, 0.42, 0.18, 0.30), "see the river between them", _do_graustark],
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
		sb.bg_color = Color(0.85, 0.75, 0.55, 0.0)
		sb.border_color = Color(0.85, 0.75, 0.55, 0.0)
		sb.set_border_width_all(1)
		btn.add_theme_stylebox_override("normal", sb)
		var bsh := sb.duplicate() as StyleBoxFlat
		bsh.bg_color = Color(0.85, 0.75, 0.55, 0.18)
		bsh.border_color = Color(1.0, 0.85, 0.55, 0.75)
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
	bps.bg_color = Color(0.03, 0.020, 0.045, 0.88)
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
	console_log.add_theme_font_size_override("normal_font_size", 12)
	console_log.add_theme_color_override("default_color",
		Color(0.82, 0.78, 0.88))
	vbox.add_child(console_log)

	var inrow := HBoxContainer.new()
	inrow.add_theme_constant_override("separation", 4)
	var prompt := Label.new()
	prompt.text = "face_down:~$ "
	prompt.add_theme_color_override("font_color", C_GOLD_HI)
	prompt.add_theme_font_size_override("font_size", 12)
	inrow.add_child(prompt)
	console_input = LineEdit.new()
	console_input.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	console_input.add_theme_color_override("font_color",
		Color(0.95, 0.85, 0.65))
	console_input.text_submitted.connect(_on_command)
	inrow.add_child(console_input)
	vbox.add_child(inrow)

	var actrow := HBoxContainer.new()
	actrow.add_theme_constant_override("separation", 12)
	vbox.add_child(actrow)

	tally_btn = Button.new()
	tally_btn.text = "  ⚭ flip 0/5 · pairs 0/6 · waits 0  "
	tally_btn.add_theme_color_override("font_color", C_GOLD_HI)
	tally_btn.add_theme_font_size_override("font_size", 12)
	var wbs := StyleBoxFlat.new()
	wbs.bg_color = Color(C_GOLD.r * 0.18, C_GOLD.g * 0.18, C_GOLD.b * 0.20, 0.55)
	wbs.border_color = C_GOLD
	wbs.set_border_width_all(1)
	tally_btn.add_theme_stylebox_override("normal", wbs)
	var wbh := wbs.duplicate() as StyleBoxFlat
	wbh.bg_color = Color(C_GOLD.r * 0.40, C_GOLD.g * 0.40, C_GOLD.b * 0.40, 0.7)
	wbh.border_color = C_GOLD_HI
	tally_btn.add_theme_stylebox_override("hover", wbh)
	tally_btn.pressed.connect(_do_wait)
	tally_btn.tooltip_text = "click card regions for distinct mechanics"
	actrow.add_child(tally_btn)

	status_label = Label.new()
	status_label.text = "the card is face-down · flip · pairs · wait · listen · mirror · graustark"
	status_label.add_theme_color_override("font_color",
		Color(C_TEXT.r, C_TEXT.g, C_TEXT.b, 0.80))
	status_label.add_theme_font_size_override("font_size", 12)
	status_label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	status_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	actrow.add_child(status_label)

	_log("[color=#ffd896]> VI · THE LOVERS · vol.5 ch.6 · the card stays face-down[/color]")
	_log("[color=#a0789a]> Graustark river between two banks · nobody crosses[/color]")
	_log("[color=#ffd896]> the deck declines to deal this one face-up[/color]")
	_log("[color=#a0789a]> type [color=#ffd896]help[/color] · the most truthful action is [color=#ffd896]wait[/color][/color]")

	console_input.grab_focus()


# ── Tableau registration ─────────────────────────────────────────
func _build_thematic_widget() -> void:
	var c_gold := C_GOLD_HI
	var c_gold_dim := Color(0.48, 0.40, 0.26, 0.90)
	var c_purple := Color(0.55, 0.40, 0.75, 0.92)
	var c_purple_dim := Color(0.32, 0.22, 0.45, 0.85)
	var c_river := Color(0.40, 0.55, 0.72, 0.90)
	var c_river_deep := Color(0.18, 0.30, 0.42, 0.90)
	var c_text := Color(0.82, 0.78, 0.88, 0.92)

	# ────────────────────────────────────────────────────────────
	# NORTH — what would be above the card if it were drawn
	# ────────────────────────────────────────────────────────────
	_register_segment({"dir": Dir.NORTH, "row": 0, "tint": c_gold_dim,
		"font_size": 13, "requires": null,
		"ascii":
"""
	╔═══════════════════════════════════════════════════╗
	║   VI · THE LOVERS · the card stays face-down     ║
	╚═══════════════════════════════════════════════════╝
		─── the angel would bless · would, would, would ───
"""
	})
	_register_segment({"dir": Dir.NORTH, "row": 1, "tint": c_gold_dim,
		"font_size": 11,
		"requires": null,
		"ascii":
"""
			┌──────────────────────────────────┐
			│  WHAT WOULD BE THERE             │
			│  if this card were dealt face-up:│
			│ ░ an angel above ░               │
			│ ░ two figures below ░            │
			│ ░ apples, snakes, a garden ░     │
			│ ░ a choice ░ a binding ░         │
			│  ─── instead: an ornate back ─── │
			└──────────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.NORTH, "row": 2, "tint": c_purple,
		"font_size": 11,
		"requires": func(): return flip_attempts >= 1,
		"ascii":
"""
			╔══════════════════════════════════╗
			║  THE FIRST ATTEMPT               ║
			║  the corner of the card lifts.   ║
			║  not enough to see what's under. ║
			║  the corner falls back.          ║
			║  the ornate pattern reasserts.   ║
			╚══════════════════════════════════╝
"""
	})
	_register_segment({"dir": Dir.NORTH, "row": 3, "tint": c_gold,
		"font_size": 11,
		"requires": func(): return bond_locked,
		"ascii":
"""
			╔══════════════════════════════════╗
			║  ░ THE CARD HAS BONDED ░         ║
			║                                  ║
			║  five attempts. the card is now  ║
			║  part of the table. you will not ║
			║  flip it. nobody will.           ║
			║                                  ║
			║  this is the keystone of the     ║
			║  chapter. the refusal is the     ║
			║  reading.                        ║
			╚══════════════════════════════════╝
"""
	})
	_register_segment({"dir": Dir.NORTH, "row": 4, "tint": c_purple,
		"font_size": 11,
		"requires": func(): return commands_run.get("uncast", 0) >= 1 or commands_run.get("refuse", 0) >= 1,
		"ascii":
"""
			┌──────────────────────────────────┐
			│  ░ THE UNCAST REGISTER ░         │
			│  three majors stay face-down     │
			│  across the deck:                │
			│                                  │
			│  VI    THE LOVERS    — refused   │
			│  XI    JUSTICE        — refused  │
			│  XX    JUDGEMENT      — refused  │
			│                                  │
			│  the pattern: cards demanding    │
			│  RESOLUTION are the ones kept    │
			│  open.                           │
			└──────────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.NORTH, "row": 5, "tint": c_gold_dim,
		"font_size": 11,
		"requires": func(): return waits >= 3,
		"ascii":
"""
			░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
			░  three waits in.                  ░
			░  the card has not moved.          ░
			░  the river continues to run.      ░
			░  the chapter is asking nothing    ░
			░  of you. you are doing it well.   ░
			░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""
	})
	_register_segment({"dir": Dir.NORTH, "row": 6, "tint": c_gold,
		"font_size": 11,
		"requires": func(): return waits >= 7,
		"ascii":
"""
			╔══════════════════════════════════╗
			║  ░ SEVEN WAITS ░                 ║
			║                                  ║
			║  this is the truest reading the  ║
			║  card offers. you have waited    ║
			║  longer than the chapter.        ║
			║                                  ║
			║  it cannot make you the kind of  ║
			║  reader the deck wanted; you     ║
			║  have already become a different ║
			║  kind.                           ║
			╚══════════════════════════════════╝
"""
	})

	# ────────────────────────────────────────────────────────────
	# SOUTH — the river / the refusal mechanism / what's below
	# ────────────────────────────────────────────────────────────
	_register_segment({"dir": Dir.SOUTH, "row": 0, "tint": c_river,
		"font_size": 12, "requires": null,
		"ascii":
"""
	════════════ THE GRAUSTARK RIVER ════════════════════
		░ ≈≈≈ ≈≈ ≈ ≈≈≈ ≈≈ ≈ ≈≈≈ ≈≈ ≈ ≈≈≈ ≈≈ ≈ ≈≈≈ ≈≈ ≈ ░
		░     between two banks. nobody on this card        ░
		░     crosses. that crossing is what would flip it. ░
"""
	})
	_register_segment({"dir": Dir.SOUTH, "row": 1, "tint": c_river,
		"font_size": 11,
		"requires": func(): return graustark_seen,
		"ascii":
"""
			╔══════════════════════════════════╗
			║  ░ THE RIVER · KEYSTONE ░        ║
			║                                  ║
			║  every other card is on one bank ║
			║  or the other. the Lovers stand  ║
			║  on opposite sides.              ║
			║                                  ║
			║  the river is the geography of   ║
			║  every refusal in the deck.      ║
			║                                  ║
			║  ░ vol5_graustark_keystone ░     ║
			╚══════════════════════════════════╝
"""
	})
	_register_segment({"dir": Dir.SOUTH, "row": 2, "tint": c_river_deep,
		"font_size": 11,
		"requires": func(): return pair_idx >= 1,
		"ascii":
"""
			┌─── pair · FRASIER & ARIA ────────┐
			│  the cathedral signal · the data │
			│  overlay · the magician hears    │
			│  the empress · neither says her  │
			│  name aloud · the warehouse roof │
			│  is on his bank · her cypress    │
			│  window is on hers · the trunk   │
			│  carries packets both directions │
			└──────────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.SOUTH, "row": 3, "tint": c_river_deep,
		"font_size": 11,
		"requires": func(): return pair_idx >= 2,
		"ascii":
"""
			┌─── pair · QUENTIN & ANTONIO ─────┐
			│  the friends remark · the bought │
			│  time · the binding holds · they │
			│  are not lovers in any reading   │
			│  · they are lovers in EVERY      │
			│  reading the chapter declines to │
			│  render · the booth and the      │
			│  phone are the same room         │
			└──────────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.SOUTH, "row": 4, "tint": c_river_deep,
		"font_size": 11,
		"requires": func(): return pair_idx >= 4,
		"ascii":
"""
			┌─── pair · ANYA & ELICIA ─────────┐
			│  across the tape · across the    │
			│  year · one records · one was    │
			│  recorded · tape four arrived    │
			│  by mail · the player who clicks │
			│  it has been told something the  │
			│  characters won't say to each    │
			│  other                           │
			└──────────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.SOUTH, "row": 5, "tint": c_river_deep,
		"font_size": 11,
		"requires": func(): return pair_idx >= 6,
		"ascii":
"""
			╔══════════════════════════════════╗
			║  ░ ALL SIX PAIRS NAMED ░         ║
			║                                  ║
			║  the lattice is complete. every  ║
			║  pair the chapter declines to    ║
			║  consummate is now in the log.   ║
			║                                  ║
			║  the card is still face-down.    ║
			║                                  ║
			║  that is the answer.             ║
			╚══════════════════════════════════╝
"""
	})
	_register_segment({"dir": Dir.SOUTH, "row": 6, "tint": c_river_deep,
		"font_size": 11,
		"requires": func(): return mirror_gazed,
		"ascii":
"""
			┌──────────────────────────────────┐
			│  ░ THE MIRROR ░                  │
			│  two figures, both looking at    │
			│  the mirror between them.        │
			│  the mirror is the river.        │
			│  nobody crosses.                 │
			│                                  │
			│  the mirror at the Emperor's     │
			│  feet showed the SUCCESSOR.      │
			│  the mirror on this card shows   │
			│  the SEPARATION.                 │
			└──────────────────────────────────┘
"""
	})

	# ────────────────────────────────────────────────────────────
	# EAST — forward / the wedding never reached / forward refusal
	# ────────────────────────────────────────────────────────────
	_register_segment({"dir": Dir.EAST, "row": 0, "tint": c_purple,
		"font_size": 11, "requires": null,
		"ascii":
"""

		┌── THE RENDEZVOUS NEVER KEPT ───────────┐
		│  every implicit pair has a meeting     │
		│  point the chapter declines to render: │
		│                                        │
		│    Frasier × Aria   the BBS handshake  │
		│    Quentin × Antonio the booth          │
		│    John × Faith     the counter         │
		│    Anya × Elicia    the cassette        │
		│    Nicola × Dante   the throne          │
		│    Maya × Y         the kneel           │
		└────────────────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.EAST, "row": 1, "tint": c_purple,
		"font_size": 11,
		"requires": func(): return listens >= 1,
		"ascii":
"""

			┌──────────────────────────────────┐
			│  ░ LISTENING · 1 ░               │
			│  from the WAREHOUSE              │
			│  a soldering iron, a sigil       │
			│  being traced. the magician card │
			│  audible through the river.      │
			└──────────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.EAST, "row": 2, "tint": c_purple,
		"font_size": 11,
		"requires": func(): return listens >= 4,
		"ascii":
"""

			┌──────────────────────────────────┐
			│  ░ LISTENING · 4 ░               │
			│  EMBER & ASH                     │
			│  the scaffold creaks. a bolt     │
			│  drops. Antonio is on this card  │
			│  by VII; he is not on THIS card  │
			│  at all. only audible from it.   │
			└──────────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.EAST, "row": 3, "tint": c_purple,
		"font_size": 11,
		"requires": func(): return listens >= 7,
		"ascii":
"""

			╔══════════════════════════════════╗
			║  ░ ALL SEVEN VOICES HEARD ░      ║
			║                                  ║
			║  each other card audible through ║
			║  the river. the Lovers card is   ║
			║  the chamber of the deck: every  ║
			║  sound reverberates here, none   ║
			║  originate here.                 ║
			╚══════════════════════════════════╝
"""
	})
	_register_segment({"dir": Dir.EAST, "row": 4, "tint": c_gold_dim,
		"font_size": 11,
		"requires": func(): return commands_run.get("psyche", 0) >= 1 or commands_run.get("eros", 0) >= 1,
		"ascii":
"""

			┌──────────────────────────────────┐
			│  ░ THE ORIGINAL LOVERS ░         │
			│  Psyche & Eros · the lamp · the  │
			│  oil drop · the recognition · the│
			│  separation · the river of the   │
			│  underworld · the long wait      │
			│  · this card is THAT story       │
			│  · told without telling          │
			└──────────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.EAST, "row": 5, "tint": c_gold,
		"font_size": 11,
		"requires": func(): return bond_locked and waits >= 5,
		"ascii":
"""

			╔══════════════════════════════════╗
			║  ░ THE RIGHT WAY TO READ THIS ░  ║
			║                                  ║
			║  you stopped trying to flip it.  ║
			║  you waited five times after.    ║
			║                                  ║
			║  the card knows you are reading  ║
			║  it correctly. it remains where  ║
			║  it remains.                     ║
			╚══════════════════════════════════╝
"""
	})

	# ────────────────────────────────────────────────────────────
	# WEST — past / why this card is refused / lineage of refusal
	# ────────────────────────────────────────────────────────────
	_register_segment({"dir": Dir.WEST, "row": 0, "tint": c_purple,
		"font_size": 11, "requires": null,
		"ascii":
"""
			┌──────────────────────────────────┐
			│  CARDS THAT REFUSE               │
			│  ─── across this deck ───        │
			│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
			│  ▓ VI  THE LOVERS   — face-down │
			│  ▓ XI  JUSTICE       — face-down│
			│  ▓ XX  JUDGEMENT     — face-down│
			│  ─── three of twenty-two ───    │
			│  ─── the chapter's quietest    ─│
			│      argument                    │
			└──────────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.WEST, "row": 1, "tint": c_gold_dim,
		"font_size": 11,
		"requires": func(): return commands_run.get("priestess", 0) >= 1 or commands_run.get("elicia", 0) >= 1,
		"ascii":
"""
			┌──────────────────────────────────┐
			│  ░ cross-card · PRIESTESS ░       │
			│  Elicia's tarot journal, entry   │
			│  VI: "THE LOVERS — uncast.       │
			│   The card stays face-down."     │
			│  she annotated this BEFORE the   │
			│  chapter even ran. she knew.     │
			└──────────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.WEST, "row": 2, "tint": c_gold,
		"font_size": 11,
		"requires": func(): return commands_run.get("emperor", 0) >= 1 or commands_run.get("dante", 0) >= 1,
		"ascii":
"""
			┌──────────────────────────────────┐
			│  ░ cross-card · EMPEROR ░        │
			│  the mirror at his feet showed   │
			│  the successor — Nicola — and    │
			│  STOPPED there. INHERITANCE, not │
			│  romance.                        │
			│  that mirror's last frame is     │
			│  this card's first frame. it     │
			│  declines to continue.           │
			└──────────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.WEST, "row": 3, "tint": c_purple_dim,
		"font_size": 11,
		"requires": func(): return commands_run.get("anya", 0) >= 1,
		"ascii":
"""
			┌──────────────────────────────────┐
			│  ░ ANYA ░                        │
			│  tape 4 arrived by mail. Elicia  │
			│  has not played it. the most     │
			│  honest reading of THIS chapter  │
			│  is to leave it unplayed.        │
			│  every Lovers card is a tape    │
			│  not played.                     │
			└──────────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.WEST, "row": 4, "tint": c_purple,
		"font_size": 11,
		"requires": func(): return commands_run.get("succession", 0) >= 1 or commands_run.get("friends", 0) >= 1,
		"ascii":
"""
			┌──────────────────────────────────┐
			│  ░ FORMS OF NOT-LOVE ░           │
			│  succession  — the throne passes │
			│  friends     — Quentin's remark  │
			│  binding     — the Rosh ritual   │
			│  inheritance — the rams          │
			│  ─ all four are the card's      ─│
			│  ─ ghost-readings. none of them ─│
			│  ─ are the card.                ─│
			└──────────────────────────────────┘
"""
	})
	_register_segment({"dir": Dir.WEST, "row": 5, "tint": c_gold,
		"font_size": 11,
		"requires": func(): return graustark_seen and listens >= 1 and pair_idx >= 1 and mirror_gazed,
		"ascii":
"""
			╔══════════════════════════════════╗
			║  ░ THE CHAPTER'S ARGUMENT ░       ║
			║                                  ║
			║  not every card needs to flip.   ║
			║  not every story needs the kiss. ║
			║  not every river needs a bridge. ║
			║                                  ║
			║  some readings hold by withheld. ║
			║  this is one.                    ║
			╚══════════════════════════════════╝
"""
	})


# ── Mechanics ────────────────────────────────────────────────────
func _do_flip() -> void:
	if bond_locked:
		status_label.text = "the card has bonded. you've used all five attempts."
		return
	flip_attempts += 1
	hotspots_seen["flip"] = true
	_refresh_tally()
	_active_notes.append({"time":0.0,"freq":174.6,"wave":"sine",
		"atk":0.04,"dur":0.30,"rel":0.40})
	var i: int = min(flip_attempts - 1, FLIP_RESPONSES.size() - 1)
	status_label.text = FLIP_RESPONSES[i]
	_memorize("flip #%d" % flip_attempts)
	_log("[color=#a878d0]· flip %d/5 · %s[/color]" % [flip_attempts, status_label.text])
	if flip_attempts >= 5:
		bond_locked = true
		_log("[color=#ffd896]· ░ THE CARD HAS BONDED ─ the refusal IS the reading.[/color]")
		SaveSystem.mark_unlocked("vol5_lovers_card_bonded")


func _do_pairs() -> void:
	if pair_idx >= PAIRS.size():
		status_label.text = "all six pairs in the log. none confirmed. that's the form."
		return
	pair_idx += 1
	hotspots_seen["pairs"] = true
	_refresh_tally()
	_active_notes.append({"time":0.0,"freq":293.7,"wave":"triangle",
		"atk":0.02,"dur":0.22,"rel":0.25})
	var line: String = PAIRS[pair_idx - 1]
	_memorize("pair · " + line)
	status_label.text = line
	_log("[color=#a878d0]· pair %d/6 · %s[/color]" % [pair_idx, line])
	if pair_idx == PAIRS.size():
		_log("[color=#ffd896]· ░ all six pairs named · the lattice is the answer.[/color]")
		SaveSystem.mark_unlocked("vol5_pair_lattice_seen")


func _do_wait() -> void:
	waits += 1
	hotspots_seen["wait"] = true
	_refresh_tally()
	# Very soft sustained tone — the wait note
	_active_notes.append({"time":0.0,"freq":110.0,"wave":"sine",
		"atk":0.08,"dur":0.60,"rel":0.80})
	_memorize("wait #%d" % waits)
	var lines := [
		"you wait. the card is face-down.",
		"you wait again. the card is face-down.",
		"you wait. the river is still running.",
		"you wait. somewhere a tape is not being played.",
		"you wait. somewhere a friend is being warned.",
		"you wait. the deck is grateful.",
		"you wait. the card has finished waiting for you.",
	]
	var i: int = min(waits - 1, lines.size() - 1)
	status_label.text = lines[i]
	_log("[color=#d8c878]· wait %d · %s[/color]" % [waits, lines[i]])
	if waits == 1:
		SaveSystem.mark_unlocked("vol5_lovers_waited")
	if waits == 7:
		_log("[color=#ffd896]· ░ SEVEN WAITS · the truest reading the card offers.[/color]")
		SaveSystem.mark_unlocked("vol5_lovers_seven_waits")


func _do_listen() -> void:
	if listens >= LISTEN_FRAGMENTS.size():
		status_label.text = "all seven voices heard. the card itself stays silent."
		return
	listens += 1
	hotspots_seen["listen"] = true
	_refresh_tally()
	_active_notes.append({"time":0.0,"freq":392.0,"wave":"sine",
		"atk":0.04,"dur":0.25,"rel":0.30})
	var line: String = LISTEN_FRAGMENTS[listens - 1]
	_memorize("listen · " + line)
	status_label.text = line
	_log("[color=#a878d0]· listen %d/7 · %s[/color]" % [listens, line])
	if listens == LISTEN_FRAGMENTS.size():
		_log("[color=#ffd896]· ░ chamber of the deck · every sound resonates here.[/color]")
		SaveSystem.mark_unlocked("vol5_lovers_listened")


func _do_mirror() -> void:
	if mirror_gazed:
		status_label.text = "the mirror has shown what it shows."
		return
	mirror_gazed = true
	hotspots_seen["mirror"] = true
	_refresh_tally()
	_active_notes.append({"time":0.0,"freq":220.0,"wave":"sine",
		"atk":0.04,"dur":0.35,"rel":0.45})
	var line: String = MIRROR_STAGES[MIRROR_STAGES.size() - 1]
	_memorize("mirror · " + line)
	status_label.text = line
	_log("[color=#88a8c8]· mirror · %s[/color]" % line)
	SaveSystem.mark_unlocked("vol5_lovers_mirror")


func _do_graustark() -> void:
	graustark_seen = true
	hotspots_seen["graustark"] = true
	_refresh_tally()
	_active_notes.append({"time":0.0,"freq":146.8,"wave":"sawtooth",
		"atk":0.04,"dur":0.35,"rel":0.45})
	_memorize("graustark river observed")
	status_label.text = "the river runs between them. nobody crosses on this card."
	_log("[color=#88a8c8]· ≈≈ THE GRAUSTARK RIVER ≈≈ · keystone of the chapter.[/color]")
	SaveSystem.mark_unlocked("vol5_graustark_keystone")


func _on_hotspot(hs: Dictionary) -> void:
	super(hs)
	var hs_id := str(hs.get("id",""))
	hotspots_seen[hs_id] = true
	_memorize("hotspot: " + hs_id)
	match hs_id:
		"lov_flip":      _do_flip()
		"lov_pairs":     _do_pairs()
		"lov_wait":      _do_wait()
		"lov_listen":    _do_listen()
		"lov_mirror":    _do_mirror()
		"lov_graustark": _do_graustark()
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
		"flip", "turn":
			_do_flip()
		"pairs", "pair":
			_do_pairs()
		"wait":
			_do_wait()
		"listen":
			_do_listen()
		"mirror":
			_do_mirror()
		"graustark", "river":
			_do_graustark()
		"recall", "memory":
			_cmd_memory()
		"count", "counts":
			_cmd_count()
		"look":
			_cmd_look()
		"clear", "cls":
			console_log.clear()
		"exit", "quit", "close":
			closed.emit()
		# Hidden — uncast siblings
		"uncast", "refuse", "refused":
			_log("[color=#a878d0]  three majors stay face-down: VI · XI · XX[/color]")
			_log("[color=#7068a0]  romance · justice · final judgement — all kept open.[/color]")
		"justice":
			_log("[color=#a878d0]  XI · JUSTICE · the card the Priestess wrote 'I am not the one to draw it'.[/color]")
		"judgement":
			_log("[color=#a878d0]  XX · JUDGEMENT · the card the Priestess wrote 'the deck refuses'.[/color]")
		# Hidden — original lovers
		"psyche":
			_log("[color=#d8b878]  the lamp · the oil drop · the recognition.[/color]")
		"eros":
			_log("[color=#d8b878]  she could not look at him · she looked anyway · he left.[/color]")
		# Hidden — implicit pairs by name
		"frasier", "magician":
			_log("[color=#88c8d0]  pair: FRASIER & ARIA · the trunk carries packets both directions.[/color]")
		"aria":
			_log("[color=#88c8d0]  pair: ARIA & FRASIER · neither says the other's name aloud.[/color]")
		"quentin":
			_log("[color=#a87830]  pair: QUENTIN & ANTONIO · the booth and the phone are the same room.[/color]")
		"antonio":
			_log("[color=#a87830]  pair: ANTONIO & QUENTIN · the friends remark · the bought time.[/color]")
		"john", "fool":
			_log("[color=#c89868]  pair: JOHN & FAITH · the cook and the dog · the only pair that never separated.[/color]")
		"faith":
			_log("[color=#c89868]  the dog at his side. she travels between cards. she stays at his side.[/color]")
		"anya":
			_log("[color=#a09a8a]  pair: ANYA & ELICIA · across the tape · across the year.[/color]")
		"elicia", "priestess":
			_log("[color=#a09a8a]  pair: ELICIA & ANYA · one records · one was recorded.[/color]")
		"nicola", "empress":
			_log("[color=#c8807a]  pair: NICOLA & DANTE · succession not romance.[/color]")
		"dante", "emperor":
			_log("[color=#c89060]  pair: DANTE & NICOLA · the chair passes through the chair.[/color]")
		"maya":
			_log("[color=#e8c4b0]  pair: MAYA & Y · too young to be lovers · already shaped into the form of pairs.[/color]")
		"y":
			_log("[color=#e8c4b0]  pair: Y & MAYA · the other kneeler · Father Quent's nephew · already knows.[/color]")
		"hierophant":
			_log("[color=#fffeec]  the binding card · the chapter Quentin runs · related, not lovers.[/color]")
		"chariot":
			_log("[color=#ff9650]  Antonio's card. Quentin's call was for him. crossings refused on both ends.[/color]")
		# Hidden — keystones
		"succession":
			_log("[color=#c89060]  the form of not-love that lets the chapter declare a winner.[/color]")
		"friends":
			_log("[color=#a87830]  the form of not-love that bought Antonio onto the scaffold.[/color]")
		"binding":
			_log("[color=#fffeec]  the form of not-love that holds four kneelers around a sigil.[/color]")
		"inheritance":
			_log("[color=#c89060]  the form of not-love the rams certify.[/color]")
		"lovers":
			_log("[color=#ffd896]  the form of love the chapter declines to certify.[/color]")
		"keystone":
			_log("[color=#ffd896]  the refusal is the reading. wait is the answer.[/color]")
		"bridge":
			_log("[color=#88a8c8]  there is no bridge on this card. that is the card.[/color]")
		_:
			if line == "tip":
				_log("[color=#a878d0]  the card declines to be tipped.[/color]")
			elif line == "rust_code.bbs":
				_log("[color=#88c8d0]  ember.ash.rest.bbs ↔ rust_code.bbs · sister trunks · same river.[/color]")
			else:
				_log("[color=#7068a0]? unknown. try: help · wait · pairs[/color]")


func _cmd_help() -> void:
	_log("[color=#ffd896]commands (visible):[/color]")
	_log("  [color=#ffd896]flip[/color]       — attempt to turn the card (5 attempts, then it bonds)")
	_log("  [color=#ffd896]pairs[/color]      — cycle implicit pairs across the deck (6)")
	_log("  [color=#ffd896]wait[/color]       — pass a moment (the most truthful action)")
	_log("  [color=#ffd896]listen[/color]     — hear distant voices from other cards (7)")
	_log("  [color=#ffd896]mirror[/color]     — what the Lovers' mirror shows")
	_log("  [color=#ffd896]graustark[/color]  — the river between the banks")
	_log("  [color=#ffd896]recall[/color]     — discovery log")
	_log("  [color=#ffd896]count[/color]      — tallies")
	_log("  [color=#ffd896]look · clear · exit[/color]")
	_log("[color=#7068a0](some commands are unlisted. the deck keeps its silences.)[/color]")


func _cmd_memory() -> void:
	_log("[color=#ffd896]── memory · %d entries ──[/color]" % memory.size())
	var shown := 0
	for entry in memory:
		if shown >= 20:
			_log("[color=#7068a0]  ... (%d more)[/color]" %
				(memory.size() - shown))
			break
		_log("  [color=#c8b8d0]· %s[/color]" % entry)
		shown += 1


func _cmd_count() -> void:
	_log("[color=#ffd896]── tallies ────────────────[/color]")
	_log("  flip attempts: [color=#a878d0]%d / 5  %s[/color]" % [
		flip_attempts, "(bonded)" if bond_locked else ""])
	_log("  pairs named:   [color=#a878d0]%d / 6[/color]" % pair_idx)
	_log("  waits:         [color=#d8c878]%d[/color]" % waits)
	_log("  listens:       [color=#a878d0]%d / 7[/color]" % listens)
	_log("  mirror:        [color=#88a8c8]%s[/color]" %
		("gazed" if mirror_gazed else "untouched"))
	_log("  graustark:     [color=#88a8c8]%s[/color]" %
		("seen" if graustark_seen else "unseen"))
	_log("  hotspots:      [color=#ffd896]%d[/color]" % hotspots_seen.size())
	_log("  commands run:  [color=#ffd896]%d[/color]" % commands_run.size())


func _cmd_look() -> void:
	_log("[color=#c8b8d0]· the card sits face-down on the table[/color]")
	_log("[color=#c8b8d0]· ornate back pattern · tarnished gold on deep purple[/color]")
	_log("[color=#c8b8d0]· the table sits beside the Graustark river[/color]")
	_log("[color=#c8b8d0]· on the far bank: a figure standing[/color]")
	_log("[color=#c8b8d0]· on this bank: a figure standing[/color]")
	_log("[color=#7068a0]· the river runs between · nobody is crossing[/color]")


func _refresh_tally() -> void:
	if tally_btn != null:
		tally_btn.text = "  ⚭ flip %d/5 · pairs %d/6 · waits %d  " % [
			flip_attempts, pair_idx, waits]


func _memorize(entry: String) -> void:
	memory.append(entry)
	if memory.size() > 200:
		memory.remove_at(0)


func _log(line: String) -> void:
	if console_log != null:
		console_log.append_text(line + "\n")


# ── Process / slow card breath / audio-reactive pulse ────────────
func _process(delta: float) -> void:
	super(delta)
	card_phase = fmod(card_phase + delta * 0.35, TAU)
	if card_rect != null:
		# Very slow gold breath; bond_locked makes it freeze
		var b: float = 1.0
		if not bond_locked:
			b = 1.0 + sin(card_phase) * 0.015
		card_rect.modulate = Color(b * 0.98, b * 0.94, b * 1.00)
	tableau_pulse += delta
	var amp: float = 0.0
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("get_bgm_magnitude"):
		amp = clamp(float(am.call("get_bgm_magnitude", 80.0, 3200.0)) * 10.0,
					0.0, 1.0)
	var base_amp = 0.06 + amp * 0.22
	var idx := 0
	for seg in _segments:
		if not seg.get("shown", false): continue
		var lbl: Label = seg.get("label")
		if lbl == null: continue
		var phase = tableau_pulse * 1.3 + idx * 0.50
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
			_do_wait()
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
