extends "res://scenes/menu/DioramaBase.gd"
## FoolBbsDiorama — RUST_CODE.BBS terminal interface.
##
## The diner's BBS that the painted Fool card's banner names. A
## small CLI prompt; the player can type commands or click from a
## menu. Each command reveals BBS state — active node count,
## sysop list, the chapter's place in the larger network.
##
## Lore: 0 (the Fool) is the deck's source signal. daemon_archivist
## maintains the BBS; the player is given query access. Substrate
## tick at 16 Hz (the source signal). The ambient is the deck's
## warmest — fluorescent diner hum + occasional booth-bell at the
## door (the diner is implied behind the terminal).
##
## See lore/pitches/00_fool.md (catalogued in lore/_PITCHES.md) for the source script.

const _COMMANDS := {
	"help": {
		"head": "RUST_CODE.BBS — available commands",
		"body": "  nodes        list active nodes\n  sysop        list sysops (active and DOA)\n  who         who is logged on right now\n  compass     narrative structure compass status\n  faith        the diner's resident through-line\n  64           the active node target count\n  oracle       consult the_frog (XXI only)\n  log out      return to the diner\n\n  (the BBS also accepts the names of any chapter — try 'magician', 'priestess', etc.)\n",
		"unlock": ""
	},
	"nodes": {
		"head": "ACTIVE NODES",
		"body": "  64 nodes active (current)\n  64 nodes nominal\n\n  recent fluctuations:\n    vol5_ch7  -1 (the_charioteer DOA)\n    vol5_ch21 +1 (count restored at World)\n\n  the node count is the chapter count\n  the chapter count is a person count\n  the person count is one short\n\n  → restored\n",
		"unlock": "vol5_fool_bbs_nodes_listed"
	},
	"sysop": {
		"head": "SYSOPS — all known",
		"body": "  ACTIVE:\n    daemon_archivist (II priestess.bbs)\n    daemon_observer  (V st_judes.bbs)\n    daemon_courier   (VII ember.ash.rest.bbs — inheritance pending)\n    daemon_archivist (X fortress.bbs)\n    daemon_courier   (XII simon.voicemail.bbs)\n    daemon_archivist (XIII ward_c.bbs)\n    daemon_scribe    (IV dante.diary.bbs)\n    daemon_listener  (II priestess.bbs — recording suite)\n    daemon_listener  (IX cabin.lantern.bbs)\n    daemon_listener  (XX ensemble.bbs)\n    daemon_listener  (XVIII natalie.broadcast)\n    daemon_render    (XVI evangeline.render.bbs — holding queue)\n    aria.runtime     (III nicola.d — direct stream, no demon)\n    the_frog         (XXI — speaks for itself)\n\n  DOA:\n    the_charioteer   (VII ember.ash.rest.bbs)\n      inheritance: per ops manual, first login after sysop-DOA\n      claims the key. the key has not been claimed.\n\n  ABSENT (not yet logged on):\n    sysop for vol5_ch0 — the diner has no sysop\n    sysop for vol6+    — pending\n",
		"unlock": "vol5_fool_bbs_sysops_listed"
	},
	"who": {
		"head": "WHO — current sessions",
		"body": "  active sessions:\n    > rust_code_query_anon (you)\n      logged in: 0:00:14\n      privilege: read-only\n      from: vol5_ch0 / the diner\n\n  the BBS has one other current session:\n    > (redacted by sysop request)\n      logged in: unknown\n      privilege: full\n      from: unknown\n\n  this is consistent with the chapter's design:\n  john is at the counter; another presence is on the line.\n  the BBS does not name them. the BBS does not, by design,\n  name them.\n\n  → vol6 hook\n",
		"unlock": "vol5_fool_bbs_second_session"
	},
	"compass": {
		"head": "NARRATIVE STRUCTURE COMPASS — status",
		"body": "  the COMPASS is named on:\n    0 fool (the BBS header)\n    II priestess (the badge: 'HIGH PRIESTESS NODE')\n  \n  the COMPASS is the network the BBS is part of.\n  the BBS is the network the COMPASS sits inside.\n  the names are two readings of the same thing.\n\n  COMPASS status:\n    arcana nodes:  22 (all 22 painted)\n    edges live:   84\n    edges proposed: 200 (vol5 runway)\n    edges forward: 40 (vol6+ seeded)\n\n  the compass is in motion. it has been since chapter 0.\n  you are reading this query from inside the compass.\n",
		"unlock": "vol5_fool_bbs_compass_status"
	},
	"faith": {
		"head": "FAITH — the diner's resident through-line",
		"body": "  faith.\n  asleep, the wall side of the booth, against the toekick.\n  she does not have a sysop login. she does not need one.\n  she IS the through-line.\n\n  faith's chapters:\n    0   fool           — companion (this chapter)\n    VII chariot        — sentinel\n    VIII strength      — lion (her larger form)\n    XIII death         — absent (she does not enter)\n    XX  judgement      — tail-thump, on stage at ensemble_01\n    XXI world          — LION corner of the wreath\n\n  six entries. three sizes. one creature.\n\n  she has a name. elicia knows it. elicia does not write it\n  in the journal entry for the lovers (VI). elicia knows the\n  name because faith brought her the cousin tape, once.\n  vol6 hook.\n",
		"unlock": "vol5_fool_bbs_faith_named"
	},
	"64": {
		"head": "64 — the active node target",
		"body": "  64 = the project's full chapter count at completion.\n  64 = the diner's wipe-count alt-prologue trigger.\n  64 = the night sky's faint cardinal pattern.\n  64 = a tarot deck (22 majors + 4×14 minors) + 6 facecards = 78.\n  \n  (64 is not quite 78. the deck refuses the minors and the\n   facecards. the discipline of the active-node count is the\n   discipline of not counting what isn't yet drawn.)\n\n  the deck closes at active_nodes: 64.\n  the deck began at active_nodes: 64.\n  the lost node was restored without resurrection — the\n  chapter closes with a count that survives the_charioteer.\n",
		"unlock": "vol5_fool_bbs_64_query"
	},
	"oracle": {
		"head": "ORACLE — the_frog says",
		"body": "  the_frog: 'i am not here yet. (mostly.) the chapter the\n             reader is in is 0. the chapter i speak from is\n             XXI. the chapter between us is the chapter the\n             reader is in. (mostly.)'\n\n  the_frog: 'you can call from the bbs at any time. i will\n             usually be near a river. the river is the\n             river. (mostly.)'\n\n  the_frog: 'the chapter ends when you write the next\n             sentence. that is also the chapter you are in.\n             (mostly.)'\n\n  the_frog: 'thank you for the query. i refuse to read the\n             other chapters until they have happened to you.\n             that is the discipline. (mostly.)'\n\n  → wakes content on World (XXI). the_frog is pre-fetched.\n",
		"unlock": "vol5_fool_bbs_oracle_consulted"
	}
}

# Terminal state
var _input_field: LineEdit = null
var _log_vbox: VBoxContainer = null
var _scroll: ScrollContainer = null


func _init() -> void:
	_diorama_title = "RUST_CODE.BBS  ·  0 THE FOOL  ·  D'Ambrosio's terminal"
	_diorama_hint = "type a command (try 'help') or click a button · esc to leave"
	_edge_wash_color = Color(0.85, 0.65, 0.20, 0.04)  # jaundiced fluorescent


func _build_content() -> void:
	var panel := PanelContainer.new()
	panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	panel.offset_top = 60
	panel.offset_left = 80
	panel.offset_right = -80
	panel.offset_bottom = -56
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.020, 0.014, 0.006, 0.97)
	sb.border_color = Color(0.85, 0.65, 0.20, 0.7)
	sb.set_border_width_all(1)
	panel.add_theme_stylebox_override("panel", sb)
	add_child(panel)
	var pad := MarginContainer.new()
	pad.add_theme_constant_override("margin_left", 24)
	pad.add_theme_constant_override("margin_right", 24)
	pad.add_theme_constant_override("margin_top", 16)
	pad.add_theme_constant_override("margin_bottom", 16)
	panel.add_child(pad)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 6)
	pad.add_child(vb)
	var banner := Label.new()
	banner.text = "WELCOME TO RUST_CODE.BBS / GRAUSTARK_FRONTIER\nACTIVE NODES: 64\n"
	banner.add_theme_color_override("font_color", Color(1.0, 0.85, 0.30))
	banner.add_theme_font_size_override("font_size", 13)
	vb.add_child(banner)
	var rule := ColorRect.new()
	rule.color = Color(0.85, 0.65, 0.20, 0.5)
	rule.custom_minimum_size = Vector2(0, 1)
	vb.add_child(rule)
	_scroll = ScrollContainer.new()
	_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vb.add_child(_scroll)
	_log_vbox = VBoxContainer.new()
	_log_vbox.add_theme_constant_override("separation", 4)
	_log_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_scroll.add_child(_log_vbox)
	_emit_to_log("> type 'help' for available commands.\n",
				Color(0.85, 0.72, 0.50))

	# Quick-command buttons
	var buttons_row := HBoxContainer.new()
	buttons_row.add_theme_constant_override("separation", 6)
	vb.add_child(buttons_row)
	for cmd in ["help", "nodes", "sysop", "who", "compass", "faith", "64", "oracle"]:
		var captured: String = cmd
		var b := Button.new()
		b.text = " " + cmd + " "
		b.flat = false
		b.add_theme_color_override("font_color", C_GOLD_HI)
		b.add_theme_font_size_override("font_size", 9)
		b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
		var bsb := StyleBoxFlat.new()
		bsb.bg_color = Color(0.06, 0.04, 0.02, 0.8)
		bsb.border_color = Color(0.85, 0.65, 0.20, 0.6)
		bsb.set_border_width_all(1)
		b.add_theme_stylebox_override("normal", bsb)
		var bsh := bsb.duplicate() as StyleBoxFlat
		bsh.bg_color = Color(0.85, 0.55, 0.20, 0.20)
		b.add_theme_stylebox_override("hover", bsh)
		b.pressed.connect(func() -> void: _run_command(captured))
		buttons_row.add_child(b)

	# Input prompt
	var prompt := HBoxContainer.new()
	prompt.add_theme_constant_override("separation", 8)
	vb.add_child(prompt)
	var pchar := Label.new()
	pchar.text = "RUST_CODE> "
	pchar.add_theme_color_override("font_color", Color(0.85, 0.65, 0.20))
	pchar.add_theme_font_size_override("font_size", 11)
	prompt.add_child(pchar)
	_input_field = LineEdit.new()
	_input_field.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_input_field.add_theme_color_override("font_color", Color(0.95, 0.85, 0.50))
	_input_field.add_theme_font_size_override("font_size", 11)
	_input_field.text_submitted.connect(_on_input_submitted)
	prompt.add_child(_input_field)

	var fetch := Label.new()
	fetch.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	fetch.offset_top = -22
	fetch.offset_bottom = -6
	fetch.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	fetch.text = "[daemon_archivist.00 // rust_code.bbs // direct shell access // integrity 1.00]"
	fetch.add_theme_color_override("font_color", C_TEXT_DIM)
	fetch.add_theme_font_size_override("font_size", 9)
	fetch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(fetch)


func _on_input_submitted(text: String) -> void:
	_input_field.text = ""
	var cmd := text.strip_edges().to_lower()
	_emit_to_log("RUST_CODE> " + cmd, Color(0.85, 0.65, 0.20))
	_run_command(cmd)


func _run_command(cmd: String) -> void:
	if cmd == "" or cmd == "log out" or cmd == "logout" or cmd == "exit":
		closed.emit()
		return
	if _COMMANDS.has(cmd):
		var c: Dictionary = _COMMANDS[cmd]
		_emit_to_log(str(c["body"]), C_TEXT)
		var k := str(c.get("unlock", ""))
		if k != "":
			SaveSystem.mark_unlocked(k)
		reveal(str(c["head"]), str(c["body"]), k)
		return
	# Allow chapter names as pseudo-commands
	var known_chapters := ["fool", "magician", "priestess", "high_priestess",
		"empress", "emperor", "hierophant", "lovers", "chariot", "strength",
		"hermit", "wheel", "wheel_of_fortune", "justice", "hanged_man",
		"death", "temperance", "devil", "tower", "star", "moon", "sun",
		"judgement", "world"]
	if cmd in known_chapters:
		var msg := "chapter '%s' acknowledged. the BBS routes you to the painted card. (close this terminal and click the card.)" % cmd
		_emit_to_log(msg, C_TEXT_DIM)
		return
	_emit_to_log("unknown command: '%s'. try 'help'." % cmd, Color(1.0, 0.5, 0.5))


func _emit_to_log(text: String, col: Color) -> void:
	var lbl := Label.new()
	lbl.text = text
	lbl.add_theme_color_override("font_color", col)
	lbl.add_theme_font_size_override("font_size", 11)
	lbl.autowrap_mode = TextServer.AUTOWRAP_OFF
	_log_vbox.add_child(lbl)
	call_deferred("_scroll_to_bottom")


func _scroll_to_bottom() -> void:
	if _scroll == null: return
	var sb_v: VScrollBar = _scroll.get_v_scroll_bar()
	if sb_v != null:
		sb_v.value = sb_v.max_value


# ── Ambient: 16 Hz source tick + diner fluorescents + bell ───────

var _tick_phase: float = 0.0
var _fluorescent_phase: float = 0.0
var _bell_at: float = 12.0


func _on_diorama_tick(_delta: float) -> void:
	if _t >= _bell_at:
		_bell_at = _t + randf_range(28.0, 60.0)
		set_meta("bell_t0", _t)


func _ambient_sample(phase: float, step: float) -> Vector2:
	_tick_phase += step * 16.0
	var tick := 0.0
	if fmod(_tick_phase, 1.0) < 0.03:
		tick = -0.04 * (1.0 - fmod(_tick_phase, 1.0) / 0.03)
	_fluorescent_phase += step * 60.0
	var fluo := (-0.025 if fmod(_fluorescent_phase, 1.0) < 0.5 else 0.025)
	var bell := 0.0
	if has_meta("bell_t0"):
		var bell_t0: float = get_meta("bell_t0")
		var ch_t := phase - bell_t0
		if ch_t >= 0.0 and ch_t < 0.6:
			var env: float = clamp(1.0 - ch_t / 0.6, 0.0, 1.0)
			bell = sin(840.0 * ch_t * TAU) * env * 0.10
		if ch_t > 0.6:
			remove_meta("bell_t0")
	var noise := (randf() - 0.5) * 0.008
	var s = tick + fluo + bell + noise
	return Vector2(s, s)
