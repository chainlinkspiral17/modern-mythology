extends "res://scenes/menu/DioramaBase.gd"
## TowerRenderLogDiorama — RENDER_FARM_LOG_47.txt as live, scrolling
## output that truncates itself.
##
## The 47 failed render jobs as a stack trace. The log writes its
## own abort. The file size increases as the log writes about its
## inability to complete. daemon_render is the failed demon — the
## diorama is the diorama of an unrendered diorama.
##
## Lore: daemon_render's substrate tick is "crash / glitch" — not
## a steady rate but irregular bursts. Each burst is the engine
## attempting and failing.

const _JOB_TEMPLATES := [
	{"id": 1,  "scene": "vol5_ch0_booth6 (FOOL)",
		"reason": "subsystem hierophant.crozier_axis.lock returned UNDEFINED. Subsystem newly undefined (was DEFINED at last commit). fallback: NO FALLBACK CONFIGURED. abort.",
		"unlock": "vol5_tower_job1_origin", "is_root": true},
	{"id": 2,  "scene": "vol5_ch1_warehouse (MAGICIAN)",
		"reason": "ABORTING — predecessor in chain failed.", "unlock": "", "is_root": false},
	{"id": 3,  "scene": "vol5_ch2_giftshop (PRIESTESS)",
		"reason": "ABORTING — predecessor in chain failed.", "unlock": "", "is_root": false},
	{"id": 4,  "scene": "vol5_ch3_empress (EMPRESS)",
		"reason": "ABORTING — predecessor in chain failed. (note: aria_handshake bus reachable; aria continued running off-chain for 0.4 sec then suspended)",
		"unlock": "vol5_tower_aria_off_chain", "is_root": false},
	{"id": 5,  "scene": "vol5_ch4_emperor (EMPEROR)",
		"reason": "ABORTING — predecessor in chain failed.", "unlock": "", "is_root": false},
	{"id": 10, "scene": "vol5_ch9_hermit (HERMIT)",
		"reason": "ABORTING — predecessor in chain failed. (note: tape_io subsystem present; archive intact)",
		"unlock": "", "is_root": false},
	{"id": 46, "scene": "vol5_ch15_daigles (DEVIL)",
		"reason": "ABORTING — predecessor in chain failed.\nREMARK (compiler): scene 15 attempted local restart.\nREMARK (compiler): local restart succeeded for 0.04 sec.\nREMARK (compiler): local restart resumed predecessor lookup.\nREMARK (compiler): predecessor still failed. aborted.",
		"unlock": "vol5_tower_devil_local_restart", "is_root": false},
	{"id": 47, "scene": "vol5_ch16_render_farm (TOWER)",
		"reason": "ABORTING — RECURSION:\n  this job's predecessor was itself.\n  this job is a render of the render of itself.\n  the render farm cannot render its own failure.\nremark (compiler):\n  the engine is trying to render the chapter that is the engine failing. this is a recursive abort. the abort is the chapter.\nstatus: held in queue. job will never resolve.\nstatus: held in queue. job will never resolve.\nstatus: held in queue. job will never resolve.",
		"unlock": "vol5_tower_recursion_seen", "is_root": false}
]

# Log scrolling state
var _log_vbox: VBoxContainer = null
var _scroll: ScrollContainer = null
var _jobs_emitted: int = 0
var _next_emit_at: float = 0.4
var _file_size_label: Label = null


func _init() -> void:
	_diorama_title = "RENDER_FARM_LOG_47.txt  ·  XVI THE TOWER  ·  daemon_render"
	_diorama_hint = "log streams in real time · click any emitted job for details · esc to leave"
	_edge_wash_color = Color(0.95, 0.20, 0.85, 0.03)  # magenta glitch


func _build_content() -> void:
	# The log scroller — fills most of the screen
	var panel := PanelContainer.new()
	panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	panel.offset_top = 60
	panel.offset_left = 40
	panel.offset_right = -40
	panel.offset_bottom = -56
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.012, 0.008, 0.018, 0.96)
	sb.border_color = Color(0.95, 0.20, 0.85, 0.7)
	sb.set_border_width_all(1)
	panel.add_theme_stylebox_override("panel", sb)
	add_child(panel)
	var pad := MarginContainer.new()
	pad.add_theme_constant_override("margin_left", 16)
	pad.add_theme_constant_override("margin_right", 16)
	pad.add_theme_constant_override("margin_top", 12)
	pad.add_theme_constant_override("margin_bottom", 12)
	panel.add_child(pad)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 6)
	pad.add_child(vb)
	var head := Label.new()
	head.text = "node: evangeline.render.queue / commit a8f2c1\njob_count_remaining: 47\nstatus: ABORTING"
	head.add_theme_color_override("font_color", Color(0.95, 0.20, 0.85))
	head.add_theme_font_size_override("font_size", 11)
	vb.add_child(head)
	_file_size_label = Label.new()
	_file_size_label.text = "[file size: 0 bytes]"
	_file_size_label.add_theme_color_override("font_color", C_TEXT_DIM)
	_file_size_label.add_theme_font_size_override("font_size", 9)
	vb.add_child(_file_size_label)
	var rule := ColorRect.new()
	rule.color = Color(0.95, 0.20, 0.85, 0.5)
	rule.custom_minimum_size = Vector2(0, 1)
	vb.add_child(rule)
	_scroll = ScrollContainer.new()
	_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vb.add_child(_scroll)
	_log_vbox = VBoxContainer.new()
	_log_vbox.add_theme_constant_override("separation", 2)
	_log_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_scroll.add_child(_log_vbox)

	var fetch := Label.new()
	fetch.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	fetch.offset_top = -22
	fetch.offset_bottom = -6
	fetch.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	fetch.text = "[demon_render.16 // evangeline.render.bbs // 47 jobs queued // integrity 0.00 (the abort is the chapter)]"
	fetch.add_theme_color_override("font_color", C_TEXT_DIM)
	fetch.add_theme_font_size_override("font_size", 9)
	fetch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(fetch)


func _emit_next_job() -> void:
	if _jobs_emitted >= _JOB_TEMPLATES.size():
		# All visible jobs emitted; final lines (the self-truncating
		# tail). Repeat once.
		if not has_meta("tail_emitted"):
			set_meta("tail_emitted", true)
			_emit_log_line("[end of log. log truncated. log truncates itself.]",
							Color(1, 0.4, 0.4, 0.9), false)
			_emit_log_line("[file size: increasing.]",
							Color(C_TEXT_DIM.r, C_TEXT_DIM.g, C_TEXT_DIM.b, 1.0), false)
		return
	var job: Dictionary = _JOB_TEMPLATES[_jobs_emitted]
	_jobs_emitted += 1
	var head_line := "[job %03d / DEMOSCENE_VIBE.EXE / SCENE: %s]" % [int(job["id"]), str(job["scene"])]
	_emit_log_line(head_line, Color(0.95, 0.20, 0.85, 0.95), true, job)
	_emit_log_line("  init                                             ok",
					C_TEXT_DIM, false)
	_emit_log_line("  load_assets                                      ok",
					C_TEXT_DIM, false)
	if job.get("is_root", false):
		_emit_log_line("  particle_sync attempt                            ok",
						C_TEXT_DIM, false)
		_emit_log_line("  particle_sync verify                             FAIL",
						Color(1, 0.4, 0.4, 0.9), false)
	var reason_lines := str(job["reason"]).split("\n")
	for line in reason_lines:
		_emit_log_line("  " + line, C_TEXT, false)
	_emit_log_line("", C_TEXT, false)


func _emit_log_line(text: String, col: Color, clickable: bool,
					 job: Dictionary = {}) -> void:
	if not clickable:
		var lbl := Label.new()
		lbl.text = text
		lbl.add_theme_color_override("font_color", col)
		lbl.add_theme_font_size_override("font_size", 10)
		lbl.autowrap_mode = TextServer.AUTOWRAP_OFF
		_log_vbox.add_child(lbl)
	else:
		var captured := job
		var btn := Button.new()
		btn.flat = false
		btn.text = text
		btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		btn.add_theme_color_override("font_color", col)
		btn.add_theme_font_size_override("font_size", 10)
		btn.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
		var bsb := StyleBoxFlat.new()
		bsb.bg_color = Color(0, 0, 0, 0.2)
		btn.add_theme_stylebox_override("normal", bsb)
		var bsh := bsb.duplicate() as StyleBoxFlat
		bsh.bg_color = Color(0.95, 0.20, 0.85, 0.15)
		btn.add_theme_stylebox_override("hover", bsh)
		btn.pressed.connect(func() -> void: _show_job_payload(captured))
		_log_vbox.add_child(btn)

	if _file_size_label != null:
		var sz := _file_size_label.text.replace("[file size: ", "").replace(" bytes]", "")
		var n := int(sz)
		n += text.length() + 1
		_file_size_label.text = "[file size: %d bytes]" % n

	call_deferred("_scroll_to_bottom")


func _scroll_to_bottom() -> void:
	var sb: VScrollBar = _scroll.get_v_scroll_bar() if _scroll != null else null
	if sb != null:
		sb.value = sb.max_value


func _show_job_payload(job: Dictionary) -> void:
	var head := "Job %03d  ·  %s" % [int(job["id"]), str(job["scene"])]
	var body := str(job["reason"])
	var key := str(job.get("unlock", ""))
	reveal(head, body, key)


func _on_diorama_tick(_delta: float) -> void:
	if _t >= _next_emit_at:
		_emit_next_job()
		_next_emit_at = _t + 0.6


# ── Ambient: irregular glitch bursts ─────────────────────────────

func _ambient_sample(phase: float, step: float) -> Vector2:
	var bursts := 0.0
	# Random burst rate — every 0.5 to 1.5 sec
	if int(phase * 2.0) != int((phase - step) * 2.0):
		if randf() < 0.4:
			bursts = (randf() - 0.5) * 0.32
	var glitch := 0.0
	if randf() < 0.02:
		glitch = sin(phase * 1480.0 * TAU) * 0.06
	var noise := (randf() - 0.5) * 0.018
	var s = bursts + glitch + noise
	return Vector2(s, s)
