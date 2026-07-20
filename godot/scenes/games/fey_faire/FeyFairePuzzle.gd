extends Control
## Fey Faire · booth puzzles · three feys make you earn the approach.
##
## Three of the midway's carnival games are real: you play the fey's
## own game before you may negotiate.  Winning grants gold (booth
## games are a gold source per _FEY_FAIRE_MECHANICS.md), a disposition
## head-start, and a puzzle_solved_<fey> flag that is RETAINED ON
## DEATH ("puzzle progress stays won").  Losing shuts the flap for the
## night, like a failed negotiation — time is the currency.
##
## Three distinct verbs, none of them luck (failure is authored, not
## RNG — the balancing philosophy):
##   cobweb_rhythm · TIMING  · TEST-YOUR-STRENGTH · "swing TRUE" ·
##                   strike while the mallet-marker is in the true
##                   band, three times, band shrinking.
##   puck_shells   · MEMORY  · COIN-IN-A-GLASS · watch three glasses
##                   swap, then name the one with the coin.
##   erlking_wheel · DEDUCE  · WHEEL OF FORTUNE · four clues name one
##                   safe sector of sixteen; the antler takes the rest.
##
## boot({fey_id, fey_name, puzzle}) · emits puzzle_solved / puzzle_
## failed / quit.  F4-compliant via add_to_group("ui").

signal puzzle_solved(fey_id: String)
signal puzzle_failed(fey_id: String)
signal quit

# Rocha palette
const C_BG        := Color(0.157, 0.094, 0.173, 1.0)
const C_PANEL     := Color(0.455, 0.157, 0.282, 1.0)
const C_PANEL_DIM := Color(0.28, 0.10, 0.18, 1.0)
const C_CREAM     := Color(0.957, 0.878, 0.816, 1.0)
const C_ROSE      := Color(0.878, 0.722, 0.753, 1.0)
const C_MAUVE     := Color(0.87, 0.68, 0.76, 1.0)
const C_GOLD      := Color(0.973, 0.784, 0.282, 1.0)
const C_GOLD_DIM  := Color(0.72, 0.52, 0.26, 1.0)
const C_GOOD      := Color(0.62, 0.82, 0.55, 1.0)
const C_BAD       := Color(0.878, 0.361, 0.361, 1.0)
const C_DIM       := Color(0.62, 0.53, 0.47, 1.0)

var _fey_id: String = ""
var _fey_name: String = "they"
var _puzzle: String = ""

# ── Cobweb rhythm (timing) state ──
var _rhythm_active: bool = false
var _marker: float = 0.0
var _marker_dir: float = 1.0
const RHYTHM_SPEED := 0.85          # bar-widths per second
var _rhythm_hits: int = 0
const RHYTHM_TARGET := 3
const RHYTHM_BANDS: Array = [0.16, 0.12, 0.085]   # half-widths, shrinking
var _marker_rect: ColorRect = null
var _band_rect: ColorRect = null
var _rhythm_status: Label = null

# ── Puck shells (memory) state ──
# Fixed swap script (deterministic · authored, not RNG).  Coin starts
# under glass 1.  Each pair swaps those two glasses' contents.
const SHELL_START := 1
const SHELL_SWAPS: Array = [[0, 1], [1, 2], [0, 1], [2, 0], [1, 2]]
var _shell_step: int = 0
var _shell_coin: int = SHELL_START


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")


func boot(state: Dictionary) -> void:
	_fey_id = String(state.get("fey_id", ""))
	_fey_name = String(state.get("fey_name", "they"))
	_puzzle = String(state.get("puzzle", ""))
	_render_intro()


# ── Shared frame ──────────────────────────────────────────────────

func _clear() -> void:
	set_process(false)
	for c in get_children():
		c.queue_free()


func _frame(title: String) -> VBoxContainer:
	_clear()
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	var panel := ColorRect.new()
	panel.color = C_PANEL_DIM
	panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	panel.offset_left = -440
	panel.offset_right = 440
	panel.offset_top = -260
	panel.offset_bottom = 260
	add_child(panel)

	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 32)
	margin.add_theme_constant_override("margin_right", 32)
	margin.add_theme_constant_override("margin_top", 26)
	margin.add_theme_constant_override("margin_bottom", 26)
	panel.add_child(margin)

	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 14)
	margin.add_child(v)

	var hdr := Label.new()
	hdr.text = title
	hdr.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hdr.add_theme_font_size_override("font_size", 22)
	hdr.add_theme_color_override("font_color", C_GOLD)
	v.add_child(hdr)
	return v


func _render_intro() -> void:
	var blurb: String = ""
	var title: String = ""
	match _puzzle:
		"cobweb_rhythm":
			title = "COBWEB · TEST YOUR STRENGTH"
			blurb = "Cobweb hands you the mallet.  'Do not swing hard,' she says.  'Swing TRUE.'  Strike three times, each while the head crosses the true band.  Miss once and the bell stays silent."
		"puck_shells":
			title = "PUCK · COIN IN A GLASS"
			blurb = "Puck sets three glasses on the counter and slides a coin under the middle one.  'Keep your eye on it, then.'  His hands are already moving.  Name the glass at the end."
		"erlking_wheel":
			title = "THE ERLKING · WHEEL OF FORTUNE"
			blurb = "The gaunt man in the grey coat sets his hand to the wheel.  'Name the one sector the antler does not take,' he says, 'and the wheel is yours.  Name wrong and I choose what it costs.'  He tells you four things about it."
		_:
			title = "A GAME"
			blurb = "A booth.  A game.  Play, or walk away."
	var v := _frame(title)

	var body := Label.new()
	body.text = blurb
	body.add_theme_font_size_override("font_size", 15)
	body.add_theme_color_override("font_color", C_CREAM)
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(body)

	var reward := Label.new()
	reward.text = "· win · +3 gold, and they warm to you before you even speak ·\n· lose · the flap shuts until the night turns ·"
	reward.add_theme_font_size_override("font_size", 13)
	reward.add_theme_color_override("font_color", C_DIM)
	v.add_child(reward)

	var play := Button.new()
	play.text = "  · play ·  "
	play.add_theme_font_size_override("font_size", 18)
	play.add_theme_color_override("font_color", C_GOLD)
	play.pressed.connect(_start_puzzle)
	v.add_child(play)

	var leave := Button.new()
	leave.text = "  · not tonight ·  "
	leave.add_theme_font_size_override("font_size", 14)
	leave.pressed.connect(func() -> void: quit.emit())
	v.add_child(leave)


func _start_puzzle() -> void:
	match _puzzle:
		"cobweb_rhythm": _render_rhythm()
		"puck_shells":   _render_shells()
		"erlking_wheel": _render_wheel()
		_:              _win()


# ── COBWEB · rhythm / timing ──────────────────────────────────────

func _render_rhythm() -> void:
	_rhythm_active = true
	_rhythm_hits = 0
	_marker = 0.0
	_marker_dir = 1.0
	var v := _frame("SWING TRUE")

	_rhythm_status = Label.new()
	_rhythm_status.text = "· 0 of %d rung ·" % RHYTHM_TARGET
	_rhythm_status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_rhythm_status.add_theme_font_size_override("font_size", 16)
	_rhythm_status.add_theme_color_override("font_color", C_MAUVE)
	v.add_child(_rhythm_status)

	# The strength-tester track.
	var track := ColorRect.new()
	track.color = C_PANEL
	track.custom_minimum_size = Vector2(760, 60)
	v.add_child(track)

	# The true band (sits at centre; width set per hit).
	_band_rect = ColorRect.new()
	_band_rect.color = Color(C_GOOD.r, C_GOOD.g, C_GOOD.b, 0.4)
	track.add_child(_band_rect)

	# The mallet head marker.
	_marker_rect = ColorRect.new()
	_marker_rect.color = C_GOLD
	_marker_rect.size = Vector2(8, 60)
	track.add_child(_marker_rect)

	var strike := Button.new()
	strike.text = "  · SWING · (space) ·  "
	strike.add_theme_font_size_override("font_size", 18)
	strike.add_theme_color_override("font_color", C_GOLD)
	strike.pressed.connect(_rhythm_strike)
	v.add_child(strike)

	_layout_band()
	set_process(true)


func _band_half() -> float:
	var idx: int = clampi(_rhythm_hits, 0, RHYTHM_BANDS.size() - 1)
	return float(RHYTHM_BANDS[idx])


func _layout_band() -> void:
	if _band_rect == null: return
	var track: Control = _band_rect.get_parent()
	var w: float = track.size.x
	if w <= 0.0: w = 760.0
	var half: float = _band_half()
	_band_rect.position = Vector2(w * (0.5 - half), 0)
	_band_rect.size = Vector2(w * (half * 2.0), 60)


func _process(delta: float) -> void:
	if not _rhythm_active or _marker_rect == null:
		return
	_marker += _marker_dir * RHYTHM_SPEED * delta
	if _marker >= 1.0:
		_marker = 1.0
		_marker_dir = -1.0
	elif _marker <= 0.0:
		_marker = 0.0
		_marker_dir = 1.0
	var track: Control = _marker_rect.get_parent()
	var w: float = track.size.x
	if w <= 0.0: w = 760.0
	_marker_rect.position = Vector2(clampf(w * _marker - 4.0, 0.0, w - 8.0), 0)
	_layout_band()


func _rhythm_strike() -> void:
	if not _rhythm_active:
		return
	var half: float = _band_half()
	var sfx := get_node_or_null("/root/SFXBank")
	if absf(_marker - 0.5) <= half:
		_rhythm_hits += 1
		if sfx: sfx.play("unlock_chime", 0.5)
		if _rhythm_hits >= RHYTHM_TARGET:
			_rhythm_active = false
			set_process(false)
			_win()
			return
		if _rhythm_status != null:
			_rhythm_status.text = "· %d of %d rung ·" % [_rhythm_hits, RHYTHM_TARGET]
		_layout_band()
	else:
		_rhythm_active = false
		set_process(false)
		if sfx: sfx.play("loss_thud", 0.6)
		_lose("The head glances off the rail.  The bell does not ring.  'Hard,' Cobweb says, 'not true.'")


# ── PUCK · shell game / memory ────────────────────────────────────

func _render_shells() -> void:
	_shell_step = 0
	_shell_coin = SHELL_START
	_show_shell_step()


func _show_shell_step() -> void:
	var v := _frame("KEEP YOUR EYE ON IT")
	if _shell_step < SHELL_SWAPS.size():
		var pair: Array = SHELL_SWAPS[_shell_step]
		var a: int = int(pair[0])
		var b: int = int(pair[1])
		var line := Label.new()
		line.text = "Puck's hands blur · glass %s and glass %s trade places." % [
			_glass_name(a), _glass_name(b)]
		line.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		line.add_theme_font_size_override("font_size", 17)
		line.add_theme_color_override("font_color", C_CREAM)
		line.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		v.add_child(line)

		var counter := Label.new()
		counter.text = "· swap %d of %d ·" % [_shell_step + 1, SHELL_SWAPS.size()]
		counter.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		counter.add_theme_font_size_override("font_size", 13)
		counter.add_theme_color_override("font_color", C_DIM)
		v.add_child(counter)

		var glasses := Label.new()
		glasses.text = "[ left ]   [ middle ]   [ right ]"
		glasses.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		glasses.add_theme_font_size_override("font_size", 15)
		glasses.add_theme_color_override("font_color", C_GOLD_DIM)
		v.add_child(glasses)

		var nxt := Button.new()
		nxt.text = "  · watch ·  "
		nxt.add_theme_font_size_override("font_size", 16)
		nxt.pressed.connect(_advance_shell)
		v.add_child(nxt)
	else:
		var prompt := Label.new()
		prompt.text = "His hands stop.  'Well?  Which glass holds the coin?'"
		prompt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		prompt.add_theme_font_size_override("font_size", 17)
		prompt.add_theme_color_override("font_color", C_MAUVE)
		prompt.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		v.add_child(prompt)

		var row := HBoxContainer.new()
		row.alignment = BoxContainer.ALIGNMENT_CENTER
		row.add_theme_constant_override("separation", 16)
		v.add_child(row)
		for g in range(3):
			var pick := Button.new()
			pick.text = "  " + _glass_name(g) + "  "
			pick.add_theme_font_size_override("font_size", 17)
			pick.add_theme_color_override("font_color", C_GOLD)
			var gi: int = g
			pick.pressed.connect(func() -> void: _guess_shell(gi))
			row.add_child(pick)


func _advance_shell() -> void:
	var pair: Array = SHELL_SWAPS[_shell_step]
	var a: int = int(pair[0])
	var b: int = int(pair[1])
	if _shell_coin == a:
		_shell_coin = b
	elif _shell_coin == b:
		_shell_coin = a
	_shell_step += 1
	_show_shell_step()


func _guess_shell(g: int) -> void:
	var sfx := get_node_or_null("/root/SFXBank")
	if g == _shell_coin:
		if sfx: sfx.play("unlock_chime", 0.5)
		_win()
	else:
		if sfx: sfx.play("loss_thud", 0.6)
		_lose("Puck lifts the glass you named.  Nothing.  He lifts the true one · the coin, of course, and his grin.  'Next time, friend.'")


func _glass_name(g: int) -> String:
	match g:
		0: return "left"
		1: return "middle"
		2: return "right"
	return "?"


# ── ERLKING · the wheel / deduction ───────────────────────────────
# Four clues resolve to exactly one sector of sixteen.  Even · not a
# power of two · digit-sum in {3,6,9} · under ten → 6.
const WHEEL_ANSWER := 6

func _render_wheel() -> void:
	var v := _frame("NAME THE SAFE SECTOR")

	var clues := Label.new()
	clues.text = "The Erlking speaks, watching you the whole time:\n\n  · 'It is EVEN.  The odd sectors are for odd folk.'\n  · 'It is NOT one of my own numbers · not two, four, eight, or the child's sixteen.'\n  · 'Add its figures: they make three, or six, or nine · the old courtesy.'\n  · 'And it is LESS THAN TEN.  You would not reach the far rim.'"
	clues.add_theme_font_size_override("font_size", 15)
	clues.add_theme_color_override("font_color", C_CREAM)
	clues.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(clues)

	var grid := GridContainer.new()
	grid.columns = 8
	grid.add_theme_constant_override("h_separation", 6)
	grid.add_theme_constant_override("v_separation", 6)
	v.add_child(grid)
	for n in range(1, 17):
		var b := Button.new()
		b.text = "16·CHILD" if n == 16 else str(n)
		b.add_theme_font_size_override("font_size", 13)
		b.custom_minimum_size = Vector2(84, 34)
		if n == 16:
			b.add_theme_color_override("font_color", C_BAD)
		var ni: int = n
		b.pressed.connect(func() -> void: _guess_wheel(ni))
		grid.add_child(b)


func _guess_wheel(n: int) -> void:
	var sfx := get_node_or_null("/root/SFXBank")
	if n == WHEEL_ANSWER:
		if sfx: sfx.play("unlock_chime", 0.5)
		_win()
	elif n == 16:
		if sfx: sfx.play("loss_thud", 0.7)
		_lose("You point at the sixteenth sector before you can stop your hand.  The Erlking smiles for the first time.  'The CHILD.  As you like.'  The flap falls shut · and something colder than a lost game follows you out.")
	else:
		if sfx: sfx.play("loss_thud", 0.6)
		_lose("The wheel comes to rest one sector off.  'The antler takes that one,' the Erlking says, almost kindly.  'Come back when you have thought it through.'")


# ── Outcomes ──────────────────────────────────────────────────────

func _win() -> void:
	var v := _frame("· THE BELL RINGS ·")
	var body := Label.new()
	body.text = "You won " + _fey_name + "'s game.  Three gold, and a look you did not expect · they were not sure you could.  Now you may approach the booth on your own terms."
	body.add_theme_font_size_override("font_size", 16)
	body.add_theme_color_override("font_color", C_GOOD)
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(body)
	var go := Button.new()
	go.text = "  · approach the booth ·  "
	go.add_theme_font_size_override("font_size", 18)
	go.add_theme_color_override("font_color", C_GOLD)
	go.pressed.connect(func() -> void: puzzle_solved.emit(_fey_id))
	v.add_child(go)


func _lose(reason: String) -> void:
	var v := _frame("· YOU LOSE THE GAME ·")
	var body := Label.new()
	body.text = reason
	body.add_theme_font_size_override("font_size", 16)
	body.add_theme_color_override("font_color", C_BAD)
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(body)
	var go := Button.new()
	go.text = "  · step away ·  "
	go.add_theme_font_size_override("font_size", 16)
	go.pressed.connect(func() -> void: puzzle_failed.emit(_fey_id))
	v.add_child(go)


func _input(event: InputEvent) -> void:
	if _rhythm_active and event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_SPACE:
			_rhythm_strike()
			get_viewport().set_input_as_handled()
