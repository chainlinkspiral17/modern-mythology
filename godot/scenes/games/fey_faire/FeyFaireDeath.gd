extends Control
## Fey Faire · death interstitial · the checkpoint economy made legible.
##
## Shown by FeyFaireHost when combat ends with player_hp <= 0.  The
## Host has already resolved the costs (a specific memory cracked,
## half the purse spilled, the most-recent keepsake dropped) and the
## respawn cell (the deepest checkpoint a recruit/vanquish opened).
## This scene NAMES each of those losses so death teaches its lesson
## instead of silently rewinding — see _FEY_FAIRE_MECHANICS.md
## "Death and checkpoints."
##
## boot(report) keys:
##   fey_name, manifestation, memory_label, memory_blur,
##   gold_before, gold_after, item_lost, wake_name,
##   memories_left (int), is_final (bool)
##
## Emits `revive` when the player chooses to wake.  On a normal death
## the Host reopens the midway at the checkpoint cell; when is_final
## (all six memories gone) the Host routes to the YOU FORGET WHY YOU
## CAME ending instead — the button text changes to say so.
##
## F4-compliant via add_to_group("ui").

signal revive

# Rocha palette · dimmed · this is the tent going dark
const C_BG        := Color(0.086, 0.055, 0.106, 1.0)
const C_PANEL     := Color(0.20, 0.11, 0.17, 1.0)
const C_CREAM     := Color(0.957, 0.878, 0.816, 1.0)
const C_ROSE      := Color(0.878, 0.722, 0.753, 1.0)
const C_MAUVE     := Color(0.87, 0.68, 0.76, 1.0)
const C_GOLD      := Color(0.973, 0.784, 0.282, 1.0)
const C_GOLD_DIM  := Color(0.72, 0.52, 0.26, 1.0)
const C_DIM       := Color(0.62, 0.53, 0.47, 1.0)
const C_CRACK     := Color(0.66, 0.42, 0.42, 1.0)

var _report: Dictionary = {}


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")


func boot(report: Dictionary) -> void:
	_report = report
	_render()


func _render() -> void:
	for c in get_children():
		c.queue_free()

	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("loss_thud", 0.7)

	var panel := ColorRect.new()
	panel.color = C_PANEL
	panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	panel.offset_left = -430
	panel.offset_right = 430
	panel.offset_top = -250
	panel.offset_bottom = 250
	add_child(panel)

	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 30)
	margin.add_theme_constant_override("margin_right", 30)
	margin.add_theme_constant_override("margin_top", 24)
	margin.add_theme_constant_override("margin_bottom", 24)
	panel.add_child(margin)

	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 12)
	margin.add_child(v)

	var is_final: bool = bool(_report.get("is_final", false))

	var header := Label.new()
	header.text = "· YOU FALL ·" if not is_final else "· YOU FALL · AND CANNOT RISE ·"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 26)
	header.add_theme_color_override("font_color", C_GOLD)
	v.add_child(header)

	var fey_name: String = String(_report.get("fey_name", "they"))
	var manifestation: String = String(_report.get("manifestation", "the tent"))
	var lede := Label.new()
	lede.text = "The tent fades.  " + fey_name + " does not follow you down.  You are on your back at " + manifestation + ", and the Faire is taking its price."
	lede.add_theme_font_size_override("font_size", 15)
	lede.add_theme_color_override("font_color", C_CREAM)
	lede.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(lede)

	var rule := ColorRect.new()
	rule.color = Color(C_MAUVE.r, C_MAUVE.g, C_MAUVE.b, 0.3)
	rule.custom_minimum_size.y = 1
	v.add_child(rule)

	# ── THE PRICE ──────────────────────────────────────────────
	# A memory, always.  This is the one that stings.
	var mem_label: String = String(_report.get("memory_label", "a memory"))
	var mem_blur: String = String(_report.get("memory_blur", "... something that used to be here ..."))
	_add_loss(v, "A MEMORY CRACKS · " + mem_label, mem_blur, C_CRACK)

	# Half the purse.
	var gb: int = int(_report.get("gold_before", 0))
	var ga: int = int(_report.get("gold_after", 0))
	if gb != ga:
		_add_loss(v, "THE PURSE SPILLS",
			"gold " + str(gb) + " → " + str(ga) + " · half of it rolls under the boards and is gone",
			C_GOLD_DIM)

	# The most-recent keepsake, if any.
	var item_lost: String = String(_report.get("item_lost", ""))
	if item_lost != "":
		_add_loss(v, "SOMETHING FALLS FROM YOUR POCKET",
			item_lost + " · you do not find it when you wake",
			C_GOLD_DIM)

	var rule2 := ColorRect.new()
	rule2.color = Color(C_MAUVE.r, C_MAUVE.g, C_MAUVE.b, 0.3)
	rule2.custom_minimum_size.y = 1
	v.add_child(rule2)

	# ── WHAT SURVIVES · the lesson: recruits remember you ──────
	var kept := Label.new()
	kept.text = "Your party remembers you.  Your promises, your quotes, your standing with the Courts — all kept.  The dead do not take those."
	kept.add_theme_font_size_override("font_size", 13)
	kept.add_theme_color_override("font_color", C_ROSE)
	kept.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(kept)

	var mem_left: int = int(_report.get("memories_left", 0))
	var counter := Label.new()
	counter.text = "· memories intact · " + str(mem_left) + " of 6 ·"
	counter.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	counter.add_theme_font_size_override("font_size", 13)
	counter.add_theme_color_override("font_color", C_DIM)
	v.add_child(counter)

	# ── WAKE ───────────────────────────────────────────────────
	if is_final:
		var final_lbl := Label.new()
		final_lbl.text = "That was the last one.  You sit up, and you do not know what you came here to do, or that you came here at all."
		final_lbl.add_theme_font_size_override("font_size", 14)
		final_lbl.add_theme_color_override("font_color", C_CRACK)
		final_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		v.add_child(final_lbl)
	else:
		var wake_name: String = String(_report.get("wake_name", "the Gate"))
		var wake_lbl := Label.new()
		wake_lbl.text = "You wake at " + wake_name + " · the deepest place the Faire will let you begin again."
		wake_lbl.add_theme_font_size_override("font_size", 14)
		wake_lbl.add_theme_color_override("font_color", C_MAUVE)
		wake_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		v.add_child(wake_lbl)

	var btn := Button.new()
	btn.text = "  · sit down in the empty lot ·  " if is_final else "  · wake ·  "
	btn.add_theme_font_size_override("font_size", 18)
	btn.add_theme_color_override("font_color", C_GOLD if not is_final else C_CRACK)
	btn.pressed.connect(func() -> void: revive.emit())
	v.add_child(btn)


func _add_loss(parent: Node, title: String, body: String, tint: Color) -> void:
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 1)
	parent.add_child(box)
	var t := Label.new()
	t.text = title
	t.add_theme_font_size_override("font_size", 15)
	t.add_theme_color_override("font_color", tint)
	box.add_child(t)
	var b := Label.new()
	b.text = "    " + body
	b.add_theme_font_size_override("font_size", 13)
	b.add_theme_color_override("font_color", C_CREAM)
	b.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	box.add_child(b)
