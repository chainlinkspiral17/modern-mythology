extends "res://scenes/menu/DioramaBase.gd"
## EmperorAppointmentDiorama — Dante's leather desk diary.
##
## A page-per-day calendar; the player navigates between days
## via prev/next buttons and clicks time slots to read what's
## written. Wednesday is the diary page the pitch+script
## centred on; the diorama opens there but lets the player
## leaf forward and back through the surrounding week.
##
## Lore: daemon_scribe.04 fetches written documents. Substrate
## tick at 18 Hz (the throne's pulse). The ambient also carries
## a slow leather-creak undertone (~40 Hz beat frequency from
## two close oscillators) — Dante's chair, in the painted scene,
## made audible.
##
## See pitches/04_emperor.md for the source script.

const _DAYS := [
	{
		"label": "MONDAY",
		"n_of_366": 16,
		"slots": [
			{"time": "06:00", "text": "pre-dawn — throne room. brush only. (this is correct.)", "unlock": ""},
			{"time": "09:00", "text": "council — full session (cancelled — q took it)", "unlock": ""},
			{"time": "11:00", "text": "lunch", "unlock": ""},
			{"time": "14:00", "text": "alma (private)", "unlock": "vol5_emp_alma_monday_blocked"},
			{"time": "19:00", "text": "dinner — the house, alone (q cancelled). nicola in town for the council she didn't attend. no contact.", "unlock": "vol5_emp_monday_solo"},
			{"time": "21:30", "text": "boat, alone — don't write what for. (good rule.)", "unlock": ""}
		]
	},
	{
		"label": "TUESDAY",
		"n_of_366": 17,
		"slots": [
			{"time": "07:00", "text": "no schedule. (this is the discipline.)", "unlock": "vol5_emp_tuesday_silence"},
			{"time": "14:00", "text": "alma (private)", "unlock": ""},
			{"time": "19:00", "text": "dinner — light. read. write nothing for the day. (correct.)", "unlock": ""}
		]
	},
	{
		"label": "WEDNESDAY",
		"n_of_366": 18,
		"is_focal": true,
		"slots": [
			{"time": "09:00", "text": "barge — manifest review with quentin (15m)", "unlock": "vol5_emp_wed_quent_barge"},
			{"time": "09:15", "text": "call back — alberto (15m)", "unlock": "vol5_emp_wed_alberto_callback_promise"},
			{"time": "09:30", "text": "walk-through, the boat (45m). NOTES: anchor still fouling. say 'aesthetic' to nicola. it is not aesthetic.", "unlock": "vol5_emp_wed_anchor_lie"},
			{"time": "10:30", "text": "alma (private)", "unlock": "vol5_emp_wed_alma_private"},
			{"time": "12:00", "text": "lunch", "unlock": ""},
			{"time": "14:00", "text": "council — petrotex item — XX'd through. cancelled. quent will take it.", "unlock": "vol5_emp_wed_petrotex_dodge"},
			{"time": "15:00", "text": "council — petrotex item — XX'd through (twice).", "unlock": ""},
			{"time": "16:00", "text": "call back — alberto (15m) — DID NOT CALL. tomorrow.", "unlock": "vol5_emp_wed_alberto_dodged"},
			{"time": "17:00", "text": "walk-through, the office (30m)", "unlock": ""},
			{"time": "17:30", "text": "pour", "unlock": ""},
			{"time": "18:00", "text": "pour", "unlock": ""},
			{"time": "19:00", "text": "dinner, the house, full table. NOTES: tablecloth fleur. nicola not asked. she will know. champagne house pour. she will know that too. let her.", "unlock": "vol5_emp_wed_empress_dinner"},
			{"time": "21:30", "text": "private — the boat, alone (90m). NOTES: don't write what for. (good rule.)", "unlock": "vol5_emp_wed_boat_private"}
		]
	},
	{
		"label": "THURSDAY",
		"n_of_366": 19,
		"slots": [
			{"time": "05:30", "text": "pre-dawn — the throne room. brush only. no light needed.", "unlock": ""},
			{"time": "09:00", "text": "call alberto. (DID NOT call wednesday. correct this.)", "unlock": "vol5_emp_thu_alberto_owed"},
			{"time": "12:00", "text": "alma (private)", "unlock": ""},
			{"time": "16:00", "text": "render farm — evangeline check-in. (quent on this. trust him.)", "unlock": "vol5_emp_thu_render_farm"},
			{"time": "21:30", "text": "boat, alone — what for: thursday. that is enough writing.", "unlock": ""}
		]
	},
	{
		"label": "FRIDAY",
		"n_of_366": 20,
		"slots": [
			{"time": "06:00", "text": "pre-dawn — throne room.", "unlock": ""},
			{"time": "10:00", "text": "render farm follow-up. (quent. quent.)", "unlock": ""},
			{"time": "14:00", "text": "alma (private)", "unlock": ""},
			{"time": "19:00", "text": "dinner — alone. nicola at — (not on this page.)", "unlock": "vol5_emp_fri_nicola_offsite"},
			{"time": "21:30", "text": "boat. moon. (not on this page either.)", "unlock": "vol5_emp_fri_moon_observed"}
		]
	}
]

# Payload commentary (mode-b found-doc style) for the most network-
# rich time slots. Keyed by unlock string.
const _PAYLOADS := {
	"vol5_emp_wed_quent_barge": {
		"head": "Wednesday 09:00 — Quentin at the barge",
		"body": "Father Quent (V Hierophant) is at Dante's barge at 09:00 CT Wednesday morning. Two days before he dials Antonio (VII). The two of them walk the boat together; the anchor is fouling; Dante notes it and chooses to lie about it to Nicola (III) at dinner.\n\nIV → V adjacency rendered as a single morning's manifest review. The crozier and the sceptre walk the same deck."
	},
	"vol5_emp_wed_anchor_lie": {
		"head": "Wednesday 09:30 — 'say aesthetic to nicola. it is not aesthetic.'",
		"body": "Dante writes the lie for himself to remember to tell. Nicola will ask about the anchor at dinner. He will say 'aesthetic.' He knows it isn't.\n\nThe Empress chapter's anxiety spike (Aria's ALERT) is partly Aria reading Dante's lie under his bourbon. The HUD overlay's CONFINED status: Nicola is confined inside a dinner where the truth is the table's secret.\n\n→ wakes content on Empress (III)."
	},
	"vol5_emp_wed_alma_private": {
		"head": "Wednesday 10:30 — alma (private)",
		"body": "Blocked. No detail. Recurs in every weekday slot from Monday through Friday. Dante does not write what 'alma' is or who Alma might be. The slot is the deck's deepest withheld appointment.\n\nForward seed for vol6. Alma is the name; the slot is the agreement to keep it private.\n\n→ vol6 hook."
	},
	"vol5_emp_wed_alberto_dodged": {
		"head": "Wednesday 16:00 — 'DID NOT CALL. tomorrow.'",
		"body": "Dante owes Alberto a callback. He doesn't make it. He writes 'tomorrow' and trusts himself to remember; the 22-25 minute callback pattern Alberto's log catalogues doesn't apply when Dante chooses to defer.\n\nThe call Dante didn't make Wednesday is the same call Daigle didn't pick up six days later when Alberto dialled 19 times in 14 minutes. Two refusals to pick up; same caller; one missed.\n\n→ wakes content on Wheel (X) and Devil (XV)."
	},
	"vol5_emp_wed_petrotex_dodge": {
		"head": "Wednesday 14:00 — PetroTex item XX'd through",
		"body": "Dante's council had the PetroTex item on the docket. He XX'd it through. Quent will take it. The agenda Dante dodged on Wednesday is the case Erica argues at Justice (XI) eleven days later.\n\nThe Wheel chapter's Denied Motion is the legal consequence of an item Dante's council declined to discuss.\n\n→ wakes content on Wheel (X), Justice (XI), Hierophant (V)."
	},
	"vol5_emp_wed_empress_dinner": {
		"head": "Wednesday 19:00 — the Empress's dinner",
		"body": "The painted Empress chapter occurs here. Dante's notes confirm: the tablecloth is intentionally fleur — Nicola will read it. The champagne is the house pour — Nicola will read that too. 'Let her.'\n\nDante is having an Empress chapter from the chair, deliberately. The painted scene at III renders Nicola's anxiety as inhabited; the diary line confirms Dante intended it.\n\n→ wakes content on Empress (III)."
	},
	"vol5_emp_wed_boat_private": {
		"head": "Wednesday 21:30 — boat, alone, 90 minutes",
		"body": "Dante's only refusal is to himself. He writes the rule for what not to write. The 21:30 boat slot recurs every day; he never writes its content.\n\nDaigle's morning note at the Devil chapter says 'he wants to talk about the boat.' That conversation happens here — or doesn't, depending on the day. The 90-minute slot has Dante on the boat with someone, or alone, and the diary respects the not-writing.\n\n→ wakes content on Devil (XV)."
	},
	"vol5_emp_fri_moon_observed": {
		"head": "Friday 21:30 — 'moon. (not on this page either.)'",
		"body": "Friday night. Dante observes the moon from his boat. Natalie's Moon chapter (XVIII) is Friday night too; her static-field broadcast goes out at this hour.\n\nDante is the only character whose chapter is rendered concurrently with another character's painted scene. IV ↔ XVIII as observer-and-observed at the same hour, across rooms.\n\n→ wakes content on Moon (XVIII)."
	},
	"vol5_emp_alma_monday_blocked": {
		"head": "Monday 14:00 — alma (private)",
		"body": "Same blocked slot, four days earlier. The pattern: Alma slot recurs daily, mid-afternoon, no detail.\n\nThe daily recurrence is itself the clue — Dante has a standing 14:00 (or 10:30 Wednesday) arrangement with someone named Alma. The deck does not surface her in vol5.\n\n→ vol6 hook."
	},
	"vol5_emp_monday_solo": {
		"head": "Monday 19:00 — 'nicola in town for the council she didn't attend.'",
		"body": "Dante's diary acknowledges Nicola's whereabouts even when they don't meet. She came in for a council session that was cancelled (because Quent took it). Dante was alone Monday night.\n\nThe Empress chapter's anxiety has a four-day setup: Monday's missed council, Tuesday's silence, Wednesday's anchor-lie, Wednesday's dinner. The Wednesday painted scene is the visible tip; the diary surfaces the iceberg.\n\n→ wakes content on Empress (III)."
	},
	"vol5_emp_wed_alberto_callback_promise": {
		"head": "Wednesday 09:15 — 'call back — alberto (15m)'",
		"body": "Promised. Carried to 16:00. Carried to Thursday. The call Dante owes Alberto is the call Alberto is still waiting on weeks later when he dials Daigle 19 times.\n\nThe deck's call-chain has a quiet preface: Dante's wednesday promise to call. The promise is the chain's missing first link.\n\n→ wakes content on Wheel (X)."
	},
	"vol5_emp_thu_alberto_owed": {
		"head": "Thursday morning — 'call alberto. (DID NOT call wednesday. correct this.)'",
		"body": "Dante writes the correction. The correction is in the diary; the call is not in Alberto's log. Dante did not make it Thursday either.\n\nThe diary becomes a catalog of dodged calls. The dodging is the chapter's quiet character work — the Emperor's authority is partly the authority to not pick up.\n\n→ wakes content on Wheel (X), Devil (XV)."
	},
	"vol5_emp_thu_render_farm": {
		"head": "Thursday 16:00 — render farm check-in (Evangeline)",
		"body": "Dante's Thursday afternoon is a check-in on Evangeline's render farm. He delegates to Quent ('trust him'). The render farm at this moment is two days from the crash; the engine is running fine.\n\nDante's vol5 involvement in the Tower's engine is a delegated check-in. He does not personally know what's about to fail.\n\n→ wakes content on Tower (XVI)."
	},
	"vol5_emp_fri_nicola_offsite": {
		"head": "Friday 19:00 — 'nicola at — (not on this page.)'",
		"body": "Dante does not write where Nicola is on Friday night. The deck's withheld is preserved: Friday is Natalie's chapter (XVIII Moon). The Empress and the Moon share a body across chapter mirrors (III ↔ XVIII); Dante's choice not to write may be one of the deck's clues to that.\n\nForward seed for vol6.\n\n→ vol6 hook."
	},
	"vol5_emp_tuesday_silence": {
		"head": "Tuesday — 'no schedule. (this is the discipline.)'",
		"body": "Dante's Tuesday is unwritten. The discipline is the silence; Tuesday is the chapter Frank moderates at Temperance (XIV).\n\nDante and Frank share the discipline of Tuesday-as-silence, in different vocabularies. Two POVs of one weekday.\n\n→ wakes content on Temperance (XIV)."
	}
}

# State
var _day_idx: int = 2   # opens at Wednesday (the focal page)
var _day_panel: PanelContainer = null
var _slots_vbox: VBoxContainer = null


func _init() -> void:
	_diorama_title = "DANTE'S APPOINTMENT BOOK  ·  IV THE EMPEROR  ·  page 18 of 366"
	_diorama_hint = "click a time slot for the day's notes · prev / next to leaf · esc to leave"
	_edge_wash_color = Color(0.40, 0.30, 0.20, 0.04)  # sepia leather


func _build_content() -> void:
	_build_day_panel()
	# Navigation buttons — bottom strip
	var nav := HBoxContainer.new()
	nav.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	nav.offset_left = 60
	nav.offset_right = -60
	nav.offset_top = -56
	nav.offset_bottom = -22
	nav.add_theme_constant_override("separation", 16)
	add_child(nav)
	var prev_btn := Button.new()
	prev_btn.text = "[ ← previous day ]"
	prev_btn.flat = true
	prev_btn.add_theme_color_override("font_color", C_GOLD)
	prev_btn.pressed.connect(func() -> void: _change_day(-1))
	nav.add_child(prev_btn)
	var sp := Control.new()
	sp.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	nav.add_child(sp)
	var next_btn := Button.new()
	next_btn.text = "[ next day → ]"
	next_btn.flat = true
	next_btn.add_theme_color_override("font_color", C_GOLD)
	next_btn.pressed.connect(func() -> void: _change_day(1))
	nav.add_child(next_btn)

	var fetch := Label.new()
	fetch.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	fetch.offset_top = -16
	fetch.offset_bottom = -4
	fetch.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	fetch.text = "[demon_scribe.04 // dante.diary.bbs // 5 days fetched (mon-fri) // integrity 0.93 (alma redacted by subject)]"
	fetch.add_theme_color_override("font_color", C_TEXT_DIM)
	fetch.add_theme_font_size_override("font_size", 12)
	fetch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(fetch)


func _build_day_panel() -> void:
	if _day_panel != null and is_instance_valid(_day_panel):
		_day_panel.queue_free()
	var day: Dictionary = _DAYS[_day_idx]
	_day_panel = PanelContainer.new()
	_day_panel.set_anchors_preset(Control.PRESET_CENTER)
	_day_panel.offset_left = -480
	_day_panel.offset_right = 480
	_day_panel.offset_top = -260
	_day_panel.offset_bottom = 240
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.10, 0.07, 0.04, 0.96)
	sb.border_color = Color(0.50, 0.35, 0.20)
	sb.set_border_width_all(2)
	_day_panel.add_theme_stylebox_override("panel", sb)
	add_child(_day_panel)
	var m := MarginContainer.new()
	m.add_theme_constant_override("margin_left", 24)
	m.add_theme_constant_override("margin_right", 24)
	m.add_theme_constant_override("margin_top", 18)
	m.add_theme_constant_override("margin_bottom", 18)
	_day_panel.add_child(m)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 8)
	m.add_child(vb)
	var head := Label.new()
	head.text = "%s                                                  [PAGE %d of 366]" % [str(day["label"]), int(day["n_of_366"])]
	head.add_theme_color_override("font_color", Color(0.85, 0.70, 0.40))
	head.add_theme_font_size_override("font_size", 13)
	vb.add_child(head)
	var rule := ColorRect.new()
	rule.color = Color(0.50, 0.35, 0.20)
	rule.custom_minimum_size = Vector2(0, 1)
	vb.add_child(rule)
	if bool(day.get("is_focal", false)):
		var foc := Label.new()
		foc.text = "(the chapter's focal page)"
		foc.add_theme_color_override("font_color", C_TEXT_DIM)
		foc.add_theme_font_size_override("font_size", 12)
		vb.add_child(foc)
	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vb.add_child(scroll)
	_slots_vbox = VBoxContainer.new()
	_slots_vbox.add_theme_constant_override("separation", 4)
	_slots_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(_slots_vbox)
	for slot_v in day["slots"]:
		var slot: Dictionary = slot_v
		var captured := slot
		var btn := Button.new()
		btn.flat = false
		btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		btn.text = "  %s    %s" % [str(slot["time"]), str(slot["text"])]
		btn.add_theme_color_override("font_color", Color(0.85, 0.72, 0.50))
		btn.add_theme_font_size_override("font_size", 12)
		btn.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
		var rsb := StyleBoxFlat.new()
		rsb.bg_color = Color(0.06, 0.04, 0.02, 0.7)
		rsb.border_color = Color(0.50, 0.35, 0.20, 0.5)
		rsb.border_width_bottom = 1
		btn.add_theme_stylebox_override("normal", rsb)
		var rsh := rsb.duplicate() as StyleBoxFlat
		rsh.bg_color = Color(0.85, 0.55, 0.20, 0.15)
		btn.add_theme_stylebox_override("hover", rsh)
		btn.pressed.connect(func() -> void: _on_slot_pressed(captured))
		_slots_vbox.add_child(btn)


func _change_day(delta: int) -> void:
	_day_idx = clamp(_day_idx + delta, 0, _DAYS.size() - 1)
	_build_day_panel()


func _on_slot_pressed(slot: Dictionary) -> void:
	var unlock_key := str(slot.get("unlock", ""))
	if unlock_key != "" and _PAYLOADS.has(unlock_key):
		var payload: Dictionary = _PAYLOADS[unlock_key]
		reveal(str(payload.get("head", slot.get("time", ""))),
				str(payload.get("body", "")), unlock_key)
	else:
		var head: String = str(slot.get("time", "")) + "  ·  " + str(_DAYS[_day_idx]["label"])
		var body: String = str(slot.get("text", ""))
		reveal(head, body, unlock_key)


# ── Ambient: 18 Hz throne tick + 40 Hz leather creak ─────────────

var _tick_phase: float = 0.0
var _leather_phase_a: float = 0.0
var _leather_phase_b: float = 0.0


func _ambient_sample(_phase: float, step: float) -> Vector2:
	_tick_phase += step * 18.0
	var tick := 0.0
	if fmod(_tick_phase, 1.0) < 0.03:
		tick = -0.04 * (1.0 - fmod(_tick_phase, 1.0) / 0.03)
	# Leather creak — two close oscillators beating at ~40 Hz
	_leather_phase_a += step * 39.5
	_leather_phase_b += step * 40.5
	var creak := sin(_leather_phase_a * TAU) * 0.012 + sin(_leather_phase_b * TAU) * 0.012
	var noise := (randf() - 0.5) * 0.010
	var s = tick + creak + noise
	return Vector2(s, s)
