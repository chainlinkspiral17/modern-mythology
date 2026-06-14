extends "res://scenes/menu/DioramaBase.gd"
## MagicianModelCityDiorama — Frasier's predictive scale model.
##
## A top-down view of the model city Frasier is wiring at the
## Cathedral of Rust and Code. Each element is clickable; on
## click, the diorama surfaces Frasier's notes on what the
## element predicts.
##
## Lore: daemon_scribe.01 fetches Frasier's annotations. Substrate
## tick at 24 Hz (the inscription rate — fast, methodical). The
## ambient carries a soldering-iron hum (a fundamental + harmonic
## ~440 Hz, very faint) and an occasional code-stream particle
## sound (high-frequency tick at random intervals).
##
## See lore/pitches/01_magician.md (catalogued in lore/_PITCHES.md) for the source script.

const _MODEL_ELEMENTS := [
	{
		"id": "steamboat",
		"label": "[ steamboat ]  (vol5_ch4 — emperor)",
		"rect": [0.42, 0.62, 0.16, 0.10],
		"head": "the red steamboat — Dante's barge before he owns it",
		"body": "Frasier wired this in three months before Dante closed the deal. The painted Emperor card (IV) shows the same boat carved into the throne. The model predicts; the throne realizes.\n\nFrasier doesn't know Dante. The prediction is structural — the city WILL have a barge on this river, by this owner, at this scale. The empire arrives at the model before it arrives at the city.\n\n→ wakes content on Emperor (IV)."
	},
	{
		"id": "warehouse_47",
		"label": "[ warehouse 47 ]  (vol5_ch10 — wheel)",
		"rect": [0.18, 0.42, 0.14, 0.10],
		"head": "warehouse 47 — Erica's law firm at scale",
		"body": "Frasier built warehouse 47 to test the GLASS WALLS variable. He did not know it would become a law firm. He calls it 'the fortress' in his notes — Erica's WALLS SLIGHTLY TRANSPARENT status line surfaces here as a load-bearing prediction.\n\nThe walls being transparent is engineered; Frasier proved at scale that the architecture would not be opaque. The chapter at X is the case prep that the model knew would happen.\n\n→ wakes content on Wheel (X)."
	},
	{
		"id": "st_judes_miniature",
		"label": "[ st. jude's miniature ]  (vol5_ch5 — hierophant)",
		"rect": [0.62, 0.20, 0.10, 0.12],
		"head": "st. jude's — the church Frasier renders with extra fidelity",
		"body": "The St. Jude's miniature is the only church Frasier built. He gave it disproportionate detail: rose window, vestibule booth, kneeler positions, the carpet's three Latin lines. He has not been to the actual church.\n\nThe miniature includes a booth with a tiny phone receiver. Father Quent's call chain originates from a phone the model already had.\n\n→ wakes content on Hierophant (V)."
	},
	{
		"id": "ember_ash",
		"label": "[ ember & ash ]  (vol5_ch7 — chariot)",
		"rect": [0.30, 0.74, 0.14, 0.12],
		"head": "ember & ash — the scaffolding visible from this angle",
		"body": "Frasier modeled the restaurant with the SCAFFOLDING VIP section as a single welded support beam. The beam is visibly listing in the model. He noticed; he did not call.\n\nThe Chariot's wreck happens because the scaffolding fails; the model showed the failure six months in advance. Frasier's notes for ember & ash read: 'beam tolerance, calculate. do later.' He didn't.\n\n→ wakes content on Chariot (VII)."
	},
	{
		"id": "daigles_pier",
		"label": "[ daigle's pier ]  (vol5_ch15 — devil)",
		"rect": [0.74, 0.74, 0.14, 0.14],
		"head": "daigle's — pier and dim bulb",
		"body": "Daigle's bar sits on the Gulf at this position. Frasier wired the amber bulb at the wrong wattage on purpose, to test the heat profile. The wrong-wattage bulb in the model city is the wrong-wattage bulb at the actual bar.\n\nThe Devil chapter's UNCOMFORTABLE INSIDE arises from Frasier's deliberate experiment, scaled up. The architecture of bondage is engineered; the model proved at small scale what the chapter renders at full.\n\n→ wakes content on Devil (XV) and Tower (XVI) — the bulb that finally cooks the line."
	},
	{
		"id": "render_farm_site",
		"label": "[ render farm site ]  (vol5_ch16 — tower)",
		"rect": [0.86, 0.40, 0.10, 0.16],
		"head": "render farm site — empty platform in the model",
		"body": "Frasier marked the site for the render farm but never built it in the model. He calls this the 'recursion problem' in his notes: the engine that would render the model city includes the model city. He could not nest it without infinite recursion.\n\nEvangeline solves the recursion by attempting it. Job 47 in RENDER_FARM_LOG_47 is the recursive abort Frasier predicted by NOT building.\n\n→ wakes content on Tower (XVI)."
	},
	{
		"id": "empress_chamber",
		"label": "[ d'ambrosio house chamber ]  (vol5_ch3 — empress)",
		"rect": [0.50, 0.36, 0.12, 0.12],
		"head": "the dinner chamber — wired with Aria's HUD echo",
		"body": "Frasier built the d'ambrosio house with the dinner chamber slightly raised. He wired a CRT in the model that mirrors his actual CRT — they're the same channel. The model's CRT reads aria.runtime; the real CRT reads aria.runtime. Two CRTs, one signal.\n\nThe Empress chapter's Aria HUD overlay is the channel Frasier wired into the model to prove the handshake was possible. The handshake is the chapter.\n\n→ wakes content on Empress (III) and Magician's existing CRT hotspot."
	},
	{
		"id": "anya_block",
		"label": "[ anya's block ]  (vol6 — forward seed)",
		"rect": [0.04, 0.16, 0.10, 0.10],
		"head": "anya's block — unwired",
		"body": "A residential block Frasier roughed in but never wired. Notes: 'pending. anya signal expected vol6. leave plumbing for the tape line.'\n\nFrasier knows Anya is coming. He has not yet inscribed her chapter. The block sits in the model as reserved infrastructure.\n\n→ vol6 forward seed."
	},
	{
		"id": "infinity_above",
		"label": "[ infinity sigil — overhead ]  (vol5_ch1 → vol5_ch8)",
		"rect": [0.46, 0.04, 0.16, 0.08],
		"head": "the infinity sigil — Frasier traces it above the model",
		"body": "The lemniscate floats above the model as code-stream particles. Frasier traces it with his soldering iron during the painted Magician chapter; the trace inscribes the glyph for the Priestess to archive (II), the Strength figure to wear (VIII), and Frank to read in dust (XIX).\n\nThe glyph is the deck's longest reach across one symbol. Four cards, one curve.\n\n→ wakes content on Priestess (II), Strength (VIII), Sun (XIX)."
	}
]

const ASCII_MODEL := """\

				   FRASIER'S MODEL CITY — top view
				   (3.6 m × 3.0 m at the cathedral workshop)

   ╭─────────────────────────────────────────────────────────╮
   │                                                         │
   │ [anya?]                  [ ∞ overhead ]                 │
   │                                                         │
   │                                                         │
   │       [warehouse 47]      [empress chamber]             │
   │       (Erica's firm)      (d'ambrosio house)            │
   │                                                         │
   │                                                         │
   │                                          [render farm]  │
   │                                          (Evangeline)    │
   │                                                         │
   │             [steamboat]                                 │
   │             (Dante's barge)                             │
   │                                                         │
   │                                                         │
   │ [ember & ash]                          [daigle's pier]  │
   │ (the scaffolding)                      (the amber bulb) │
   │                                                         │
   ╰─────────────────────────────────────────────────────────╯
										  [st. jude's]
										  (forward east)
"""


func _init() -> void:
	_diorama_title = "MODEL CITY  ·  I THE MAGICIAN  ·  Frasier's prediction at scale"
	_diorama_hint = "click any element for Frasier's notes · esc to leave"
	_edge_wash_color = Color(0.40, 0.60, 0.50, 0.04)  # dark teal industrial


func _build_content() -> void:
	var panel := PanelContainer.new()
	panel.set_anchors_preset(Control.PRESET_CENTER)
	panel.offset_left = -540; panel.offset_right = 540
	panel.offset_top = -300; panel.offset_bottom = 280
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.014, 0.020, 0.024, 0.96)
	sb.border_color = Color(0.40, 0.70, 0.65, 0.7)
	sb.set_border_width_all(1)
	panel.add_theme_stylebox_override("panel", sb)
	add_child(panel)
	var lbl := Label.new()
	lbl.text = ASCII_MODEL
	lbl.add_theme_color_override("font_color", Color(0.70, 0.85, 0.80))
	lbl.add_theme_font_size_override("font_size", 11)
	lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	panel.add_child(lbl)
	for el_v in _MODEL_ELEMENTS:
		var el: Dictionary = el_v
		var captured := el
		make_hotspot(panel, el["rect"], str(el["label"]),
			func() -> void: reveal(str(captured["head"]), str(captured["body"]),
									"vol5_magician_model_" + str(captured["id"])))

	var fetch := Label.new()
	fetch.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	fetch.offset_top = -22
	fetch.offset_bottom = -6
	fetch.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	fetch.text = "[demon_scribe.01 // cathedral.workshop.bbs // 9 elements indexed (1 unwired) // integrity 0.97]"
	fetch.add_theme_color_override("font_color", C_TEXT_DIM)
	fetch.add_theme_font_size_override("font_size", 9)
	fetch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(fetch)


# ── Ambient: 24 Hz inscription tick + soldering iron hum ─────────

var _tick_phase: float = 0.0
var _solder_phase: float = 0.0
var _next_particle_at: float = 1.2


func _on_diorama_tick(_delta: float) -> void:
	if _t >= _next_particle_at:
		set_meta("particle_t0", _t)
		_next_particle_at = _t + randf_range(2.0, 5.0)


func _ambient_sample(phase: float, step: float) -> Vector2:
	_tick_phase += step * 24.0
	var tick := 0.0
	if fmod(_tick_phase, 1.0) < 0.03:
		tick = -0.04 * (1.0 - fmod(_tick_phase, 1.0) / 0.03)
	_solder_phase += step * 440.0
	var solder := sin(_solder_phase * TAU) * 0.012
	var harmonic := sin(_solder_phase * 0.5 * TAU) * 0.008
	var particle := 0.0
	if has_meta("particle_t0"):
		var p_t0: float = get_meta("particle_t0")
		var ch_t := phase - p_t0
		if ch_t >= 0.0 and ch_t < 0.08:
			particle = sin(ch_t * 2400.0 * TAU) * 0.04 * (1.0 - ch_t / 0.08)
		if ch_t > 0.08:
			remove_meta("particle_t0")
	var noise := (randf() - 0.5) * 0.006
	var s = tick + solder + harmonic + particle + noise
	return Vector2(s, s)
