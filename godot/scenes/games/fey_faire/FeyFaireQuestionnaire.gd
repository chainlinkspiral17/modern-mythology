extends Control
## Fey Faire · boot questionnaire · walks the player through the
## 11 questions defined in questionnaire.json.  Handles three
## question types: short_text (one-line entry), long_text (multi-
## line entry), single_choice (button list).  Each answer is stored
## by its schema-defined `storage` key.
##
## Skipping (Space) uses the question's `backfill` value.
##
## When complete, emits `finished(answers: Dictionary)` with all
## stored answers keyed by their `storage` id.  Host routes to Gate.
##
## Rocha's cream + old rose + mauve palette matches the title.
## F4-compliant via add_to_group("ui").

signal finished(answers: Dictionary)
signal cancelled

const QUESTIONNAIRE_PATH := "res://resources/games/vol7/fey_faire/questionnaire.json"

# Palette · matches Rocha's cart title card
const C_BG        := Color(0.157, 0.094, 0.173, 1.0)
const C_PANEL     := Color(0.455, 0.157, 0.282, 1.0)
const C_CREAM     := Color(0.957, 0.878, 0.816, 1.0)
const C_ROSE      := Color(0.878, 0.722, 0.753, 1.0)
const C_MAUVE     := Color(0.87, 0.68, 0.76, 1.0)
const C_GOLD      := Color(0.973, 0.784, 0.282, 1.0)
const C_GOLD_DIM  := Color(0.72, 0.52, 0.26, 1.0)

var _questions: Array = []
var _current_idx: int = 0
var _answers: Dictionary = {}

# Live UI refs · rebuilt per question
var _prompt_lbl: Label = null
var _hint_lbl:   Label = null
var _input_root: Control = null
var _short_input: LineEdit = null
var _long_input:  TextEdit  = null
var _progress_lbl: Label = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	_load_questionnaire()
	_build_frame()
	_render_current_question()


func _load_questionnaire() -> void:
	if not FileAccess.file_exists(QUESTIONNAIRE_PATH):
		push_warning("[FeyFaireQuestionnaire] missing %s" % QUESTIONNAIRE_PATH)
		_questions = []
		return
	var f := FileAccess.open(QUESTIONNAIRE_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		_questions = (parsed as Dictionary).get("questions", [])


func _build_frame() -> void:
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# Cream + old rose horizontal bands · match the title card
	var band_cream := ColorRect.new()
	band_cream.color = C_CREAM
	band_cream.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	band_cream.offset_top = 0
	band_cream.offset_bottom = 60
	add_child(band_cream)

	var band_rose := ColorRect.new()
	band_rose.color = C_ROSE
	band_rose.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	band_rose.offset_top = -60
	band_rose.offset_bottom = 0
	add_child(band_rose)

	# Header
	var header := Label.new()
	header.text = "· THE FEY FAIRE · A CIRCUIT OF QUESTIONS ·"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 16)
	header.add_theme_color_override("font_color", C_PANEL)
	header.set_anchors_preset(Control.PRESET_TOP_WIDE)
	header.offset_top = 20
	header.offset_bottom = 44
	add_child(header)

	# Progress line
	_progress_lbl = Label.new()
	_progress_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_progress_lbl.add_theme_font_size_override("font_size", 14)
	_progress_lbl.add_theme_color_override("font_color", C_GOLD_DIM)
	_progress_lbl.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_progress_lbl.offset_top = -40
	_progress_lbl.offset_bottom = -20
	add_child(_progress_lbl)


func _clear_input_root() -> void:
	if _input_root != null and is_instance_valid(_input_root):
		_input_root.queue_free()
	_input_root = null
	_short_input = null
	_long_input = null


func _render_current_question() -> void:
	_clear_input_root()
	if _questions.is_empty() or _current_idx >= _questions.size():
		_complete()
		return
	var q: Dictionary = _questions[_current_idx]

	_input_root = Control.new()
	_input_root.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_input_root.offset_left = -340
	_input_root.offset_right = 340
	_input_root.offset_top = -200
	_input_root.offset_bottom = 200
	add_child(_input_root)

	# Center panel background
	var panel := ColorRect.new()
	panel.color = C_PANEL
	panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_input_root.add_child(panel)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.offset_left = 24
	v.offset_right = -24
	v.offset_top = 20
	v.offset_bottom = -20
	v.add_theme_constant_override("separation", 12)
	_input_root.add_child(v)

	# Prompt
	_prompt_lbl = Label.new()
	_prompt_lbl.text = String(q.get("prompt", ""))
	_prompt_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_prompt_lbl.add_theme_font_size_override("font_size", 18)
	_prompt_lbl.add_theme_color_override("font_color", C_GOLD)
	v.add_child(_prompt_lbl)

	# Hint · storage key + skip note
	_hint_lbl = Label.new()
	_hint_lbl.text = "(space to skip · your skip fills in an authored default)"
	_hint_lbl.add_theme_font_size_override("font_size", 13)
	_hint_lbl.add_theme_color_override("font_color", C_ROSE)
	v.add_child(_hint_lbl)

	# Input field(s) per type
	var atype := String(q.get("answer_type", "short_text"))
	match atype:
		"short_text":
			_short_input = LineEdit.new()
			_short_input.placeholder_text = "..."
			_short_input.max_length = int(q.get("max_length", 40))
			_short_input.add_theme_font_size_override("font_size", 16)
			_short_input.custom_minimum_size = Vector2(0, 28)
			v.add_child(_short_input)
			_short_input.grab_focus.call_deferred()
		"long_text":
			_long_input = TextEdit.new()
			_long_input.placeholder_text = "..."
			_long_input.wrap_mode = TextEdit.LINE_WRAPPING_BOUNDARY
			_long_input.add_theme_font_size_override("font_size", 16)
			_long_input.custom_minimum_size = Vector2(0, 96)
			v.add_child(_long_input)
			_long_input.grab_focus.call_deferred()
		"single_choice":
			var options: Array = q.get("options", [])
			for opt_v in options:
				var opt: Dictionary = opt_v
				# Respect gate_shown if present (a specific option-availability flag)
				var gate_shown: Variant = opt.get("gate_shown", null)
				if gate_shown != null:
					# Trivial gate: if the gate mentions a storage key we
					# haven't answered yet, hide this option.  A real
					# implementation would parse the boolean.  For now
					# we're permissive and show every option.
					pass
				var btn := Button.new()
				btn.text = "  " + String(opt.get("label", opt.get("id", "?"))) + "  "
				btn.add_theme_font_size_override("font_size", 16)
				btn.pressed.connect(func() -> void: _submit_answer(String(opt.get("id", ""))))
				v.add_child(btn)

	# Buttons row
	var buttons := HBoxContainer.new()
	buttons.alignment = BoxContainer.ALIGNMENT_CENTER
	buttons.add_theme_constant_override("separation", 16)
	v.add_child(buttons)

	if atype != "single_choice":
		var submit_btn := Button.new()
		submit_btn.text = "  next →  "
		submit_btn.pressed.connect(_on_submit_pressed)
		buttons.add_child(submit_btn)

	var skip_btn := Button.new()
	skip_btn.text = "  skip  "
	skip_btn.pressed.connect(_on_skip_pressed)
	buttons.add_child(skip_btn)

	var quit_btn := Button.new()
	quit_btn.text = "  ← back  "
	quit_btn.pressed.connect(_on_back_pressed)
	buttons.add_child(quit_btn)

	# Update progress
	_progress_lbl.text = "question %d of %d" % [_current_idx + 1, _questions.size()]


func _on_submit_pressed() -> void:
	var q: Dictionary = _questions[_current_idx]
	var atype := String(q.get("answer_type", "short_text"))
	var value: String = ""
	if atype == "short_text" and _short_input != null:
		value = _short_input.text
	elif atype == "long_text" and _long_input != null:
		value = _long_input.text
	if value.strip_edges() == "":
		# Empty submit falls back to skip
		_on_skip_pressed()
		return
	_submit_answer(value)


func _on_skip_pressed() -> void:
	var q: Dictionary = _questions[_current_idx]
	var backfill: String = String(q.get("backfill", ""))
	_submit_answer(backfill)


func _submit_answer(value: String) -> void:
	var q: Dictionary = _questions[_current_idx]
	var key := String(q.get("storage", ""))
	if key != "":
		_answers[key] = value
	_current_idx += 1
	_render_current_question()


func _on_back_pressed() -> void:
	cancelled.emit()


func _complete() -> void:
	# Boot inventory item option-specific · grants a starter keepsake
	var boot_item := String(_answers.get("boot_inventory_item", ""))
	if boot_item != "":
		var q: Dictionary = {}
		for entry_v in _questions:
			var entry: Dictionary = entry_v
			if String(entry.get("id", "")) == "q_boot_inventory_item":
				q = entry
				break
		if not q.is_empty():
			for opt_v in q.get("options", []):
				var opt: Dictionary = opt_v
				if String(opt.get("id", "")) == boot_item:
					_answers["_granted_keepsake"] = String(opt.get("grants_keepsake", ""))
					break
	finished.emit(_answers)


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			_on_back_pressed()
			get_viewport().set_input_as_handled()
			return
		# Enter submits · but only if a text input is focused AND
		# the input is short_text (long_text uses Enter for newlines)
		if kev.keycode == KEY_ENTER or kev.keycode == KEY_KP_ENTER:
			if _short_input != null and _short_input.has_focus():
				_on_submit_pressed()
				get_viewport().set_input_as_handled()
