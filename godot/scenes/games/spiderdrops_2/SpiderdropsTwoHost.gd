extends Control
## SPIDERDROPS 2 · THE LONG WIND · run controller · PDP Toys, 1995.
##
## The post-game sequel. The storm is over; the web cannot be held, so
## the spider lets go and travels — ballooning on the gusts that once
## tore the web apart, across the gaps, to a new anchor. The wind that
## destroyed you in the first game carries you in this one.
##
## Carries the first game's ending IN: canon_vars.spiderdrops_result
## sets your starting silk (WHOLE/STAR full, HELD worn, STORM nearly
## empty). Carrying the eight-pointed star (spiderdrops_star) unlocks
## the true ending, UNDER THE EAVES.
##
## Save: user://spiderdrops_2.save.json — best register + run count.
##
## Signals · uniform host contract: quit_to_shelf · finished(...)
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal finished(canon_vars: Dictionary, lore_tokens: Array)

const MANIFEST_PATH := "res://resources/games/vol7/spiderdrops_2/manifest.json"
const SAVE_PATH     := "user://spiderdrops_2.save.json"
const FLIGHT_SCENE  := "res://scenes/games/spiderdrops_2/LongWindFlight.tscn"

# dawn-after-the-storm palette (a tailwind, not a hazard)
const C_SKY    := Color("3a4d6b")
const C_SKY2   := Color("6c7fa0")
const C_SILK   := Color("e8ecef")
const C_DROP   := Color("6fb7e0")
const C_SPIDER := Color("f2c14e")
const C_DARK   := Color("18202e")
const C_TXT    := Color("d8e0e8")

var _manifest: Dictionary = {}
var _run_state: Dictionary = {}
var _title_root: Node = null
var _child_scene: Node = null
var _ending_root: Node = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	SlowstickLook.apply(self, "pdp_toys")
	theme = preload("res://scenes/games/StickTheme.gd").make("pdp_toys")
	_run_state = _fresh_state()
	_load_manifest()
	_load_save_if_present()
	_build_title_screen()


func _fresh_state() -> Dictionary:
	return {
		"runs":           0,
		"best_register":  "",
		"registers_seen": [],
		"canon_vars":     {},
		"lore_tokens_pending": []
	}


func _load_manifest() -> void:
	if not FileAccess.file_exists(MANIFEST_PATH): return
	var f := FileAccess.open(MANIFEST_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		_manifest = parsed


func _load_save_if_present() -> void:
	if not FileAccess.file_exists(SAVE_PATH): return
	var f := FileAccess.open(SAVE_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		var saved: Dictionary = parsed
		for k in saved.keys():
			_run_state[String(k)] = saved[k]


func _save_state() -> void:
	var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f == null: return
	f.store_string(JSON.stringify(_run_state, "  "))
	f.close()


# ── Carry the first game's ending in ─────────────────────────────
# The register you left the storm with becomes the silk you start the
# journey with. The star is a keepsake that opens the true ending.
func _starting_silk_frac() -> float:
	var reg: String = String(OneironauticsTokens.canon("spiderdrops_result", ""))
	match reg:
		"whole": return 1.0
		"star":  return 1.0
		"held":  return 0.8
		"storm": return 0.4
		_:       return 0.7


func _carry_star() -> bool:
	return OneironauticsTokens.has("spiderdrops_star")


func start_new_run(_manager_mode: bool = false) -> void:
	_open_flight()


func _clear_current_scene() -> void:
	for n in [_title_root, _child_scene, _ending_root]:
		if n != null and is_instance_valid(n):
			n.queue_free()
	_title_root = null
	_child_scene = null
	_ending_root = null


func _play_bgm(path: String) -> void:
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("request_scene_bgm"):
		am.request_scene_bgm(path)


func _sfx(preset: String) -> void:
	var sb := get_node_or_null("/root/SFXBank")
	if sb != null and sb.has_method("play"):
		sb.play(preset)


# ─── Title ───────────────────────────────────────────────────────

func _build_title_screen() -> void:
	_clear_current_scene()

	_title_root = Control.new()
	_title_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_title_root)

	var sky := ColorRect.new()
	sky.color = C_SKY
	sky.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.add_child(sky)

	var band := ColorRect.new()
	band.color = C_SKY2
	band.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	band.offset_top = -300
	_title_root.add_child(band)

	var hero := HeroImage.new()
	if hero.load_from("res://resources/games/vol7/spiderdrops_2/hero_images/title.json"):
		var tr := TextureRect.new()
		tr.texture = hero.texture(Vector2i(1120, 630))
		tr.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		tr.offset_left = -560
		tr.offset_right = 560
		tr.offset_top = -315
		tr.offset_bottom = 315
		tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
		tr.modulate.a = 0.5
		_title_root.add_child(tr)

	preload("res://scenes/games/TitleMotion.gd").attach(_title_root, "pdp_toys")

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -340
	v.offset_right = 340
	v.offset_top = -180
	v.offset_bottom = 250
	v.add_theme_constant_override("separation", 12)
	_title_root.add_child(v)

	var shelf: Dictionary = _manifest.get("shelf", {})

	var title := Label.new()
	title.text = String(shelf.get("label_title", "SPIDERDROPS 2"))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 44)
	title.add_theme_color_override("font_color", C_SPIDER)
	v.add_child(title)

	var subtitle := Label.new()
	subtitle.text = String(shelf.get("label_subtitle", "the long wind"))
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.add_theme_font_size_override("font_size", 15)
	subtitle.add_theme_color_override("font_color", C_SILK)
	v.add_child(subtitle)

	var meta := Label.new()
	meta.text = "PDP Toys · Beaverton, OR · 1995"
	meta.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	meta.add_theme_font_size_override("font_size", 12)
	meta.add_theme_color_override("font_color", C_DROP)
	v.add_child(meta)

	# What you carried in from the storm.
	var reg: String = String(OneironauticsTokens.canon("spiderdrops_result", ""))
	var carry := Label.new()
	carry.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	carry.add_theme_font_size_override("font_size", 12)
	carry.add_theme_color_override("font_color", C_SPIDER if _carry_star() else C_TXT)
	if reg == "":
		carry.text = "· you have not weathered the storm yet · you set out with a traveler's silk ·"
	else:
		var star_line := "  · and the eight-pointed star rides with you" if _carry_star() else ""
		carry.text = "· you left the storm: %s%s ·" % [reg.to_upper(), star_line]
	v.add_child(carry)

	var sep := Control.new()
	sep.custom_minimum_size = Vector2(0, 12)
	v.add_child(sep)

	var play_btn := Button.new()
	play_btn.text = "  CATCH THE WIND  "
	play_btn.add_theme_font_size_override("font_size", 15)
	play_btn.pressed.connect(func() -> void: start_new_run(false))
	v.add_child(play_btn)

	var back_btn := Button.new()
	back_btn.text = "  ← back to shelf  "
	back_btn.add_theme_font_size_override("font_size", 13)
	back_btn.pressed.connect(_on_back_to_shelf)
	v.add_child(back_btn)

	var best: String = String(_run_state.get("best_register", ""))
	var runs: int = int(_run_state.get("runs", 0))
	if runs > 0:
		var status := Label.new()
		status.text = "· journeys: %d · best: %s ·" % [runs, best if best != "" else "—"]
		status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		status.add_theme_font_size_override("font_size", 12)
		status.add_theme_color_override("font_color", C_DROP)
		v.add_child(status)

	var legend := Label.new()
	legend.text = "HOLD accept/A to lift on the wind  ·  ↑↓ steer into the wind band  ·  ←→ lean"
	legend.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	legend.add_theme_font_size_override("font_size", 12)
	legend.add_theme_color_override("font_color", Color(C_SILK.r, C_SILK.g, C_SILK.b, 0.7))
	v.add_child(legend)

	GamepadMgr.focus_first.call_deferred(_title_root)


func _on_back_to_shelf() -> void:
	quit_to_shelf.emit()


# ─── The journey ─────────────────────────────────────────────────

func _open_flight() -> void:
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/spiderdrops_2/long_wind.wav")
	_child_scene = load(FLIGHT_SCENE).instantiate()
	_child_scene.quit.connect(_on_flight_quit)
	_child_scene.run_over.connect(_on_run_over)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", {
			"silk_frac": _starting_silk_frac(),
			"carry_star": _carry_star(),
		})


func _on_flight_quit() -> void:
	_build_title_screen()


func _on_run_over(result: Dictionary) -> void:
	_run_state["runs"] = int(_run_state.get("runs", 0)) + 1
	var register: String = String(result.get("register", "still_flying"))
	var seen: Array = _run_state.get("registers_seen", [])
	if not seen.has(register):
		seen.append(register)
	_run_state["registers_seen"] = seen
	_run_state["best_register"] = _best_of(String(_run_state.get("best_register", "")), register)
	_award_run_tokens(register)
	_save_state()
	_show_ending(result)


# Register rank: eaves (true) > new_tree > still_flying.
func _register_rank(reg: String) -> int:
	match reg:
		"eaves":        return 3
		"new_tree":     return 2
		"still_flying": return 1
		_:              return 0


func _best_of(a: String, b: String) -> String:
	return a if _register_rank(a) >= _register_rank(b) else b


func _award_run_tokens(register: String) -> void:
	var tokens: Array = _run_state.get("lore_tokens_pending", [])
	if not tokens.has("spiderdrops_2_finished"):
		tokens.append("spiderdrops_2_finished")
	if register == "new_tree" or register == "eaves":
		if not tokens.has("spiderdrops_2_arrived"):
			tokens.append("spiderdrops_2_arrived")
	if register == "eaves" and not tokens.has("spiderdrops_the_eaves"):
		tokens.append("spiderdrops_the_eaves")
	_run_state["lore_tokens_pending"] = tokens
	OneironauticsTokens.add_many(tokens)


# ─── Ending register screen ──────────────────────────────────────

const REGISTER_TITLE := {
	"new_tree":     "A NEW TREE",
	"still_flying": "STILL FLYING",
	"eaves":        "UNDER THE EAVES",
}
const REGISTER_LINE := {
	"new_tree":     "The wind sets you down on a branch you have never seen, in a place the storm never reached. You have silk enough. You begin again. You can always begin again.",
	"still_flying": "The last of the silk pays out and you stop steering. The wind has you now, and it is going somewhere you were not, and that turns out to be all right. You are not lost. You are only still flying.",
	"eaves":        "The long wind carries you in under a low roof, out of the weather at last — the corner of a cabin by the water. Something is already here: the shape you carried, the eight points, waiting where the wall meets the wall. You are home, in a house that is not yours, and no one will ever tell you whose.",
}


func _show_ending(result: Dictionary) -> void:
	_clear_current_scene()
	_sfx("page_turn")
	var register: String = String(result.get("register", "still_flying"))

	_ending_root = Control.new()
	_ending_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_ending_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_ending_root)

	var bg := ColorRect.new()
	bg.color = C_DARK if register == "eaves" else C_SKY
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_ending_root.add_child(bg)

	var hero := HeroImage.new()
	if hero.load_from("res://resources/games/vol7/spiderdrops_2/hero_images/ending_%s.json" % register):
		var tr := TextureRect.new()
		tr.texture = hero.texture(Vector2i(1120, 630))
		tr.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
		tr.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
		tr.modulate.a = 0.45
		_ending_root.add_child(tr)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -380
	v.offset_right = 380
	v.offset_top = -190
	v.offset_bottom = 230
	v.add_theme_constant_override("separation", 16)
	_ending_root.add_child(v)

	var title := Label.new()
	title.text = String(REGISTER_TITLE.get(register, "STILL FLYING"))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 34)
	title.add_theme_color_override("font_color", C_SPIDER)
	v.add_child(title)

	var line := Label.new()
	line.text = String(REGISTER_LINE.get(register, ""))
	line.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	line.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	line.add_theme_font_size_override("font_size", 15)
	line.add_theme_color_override("font_color", C_TXT)
	v.add_child(line)

	var score := Label.new()
	score.text = "legs crossed: %d of %d  ·  score %d" % [
		int(result.get("legs_crossed", 0)),
		int(result.get("legs_total", 7)),
		int(result.get("score", 0)),
	]
	score.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	score.add_theme_font_size_override("font_size", 13)
	score.add_theme_color_override("font_color", C_DROP)
	v.add_child(score)

	var sep := Control.new()
	sep.custom_minimum_size = Vector2(0, 8)
	v.add_child(sep)

	var again := Button.new()
	again.text = "  set out again  "
	again.add_theme_font_size_override("font_size", 14)
	again.pressed.connect(_open_flight)
	v.add_child(again)

	var done := Button.new()
	done.text = "  put the cart back  "
	done.add_theme_font_size_override("font_size", 14)
	done.pressed.connect(_put_the_cart_back)
	v.add_child(done)

	GamepadMgr.focus_first.call_deferred(_ending_root)


func _put_the_cart_back() -> void:
	var canon: Dictionary = _run_state.get("canon_vars", {})
	canon["spiderdrops_2_result"] = String(_run_state.get("best_register", "still_flying"))
	_run_state["canon_vars"] = canon
	_save_state()
	var tokens: Array = _run_state.get("lore_tokens_pending", [])
	finished.emit(canon, tokens)


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			if _title_root != null and _child_scene == null and _ending_root == null:
				_on_back_to_shelf()
				get_viewport().set_input_as_handled()
