extends Control
## SPIDERDROPS · run controller · PDP Toys, Beaverton OR, 1993.
##
## A real-time physics arcade toy: keep the orb-weaver's web up through
## a six-gust thunderstorm. Marketed as a high-score toy; the design
## never lets you beat the storm — the run resolves by the SHAPE the
## web is in when it goes (the Tideline-register pattern). When only
## the eight radial spokes survive, the web is the Order's
## eight-pointed star, uncommented.
##
## Save file: user://spiderdrops.save.json — best register + run count
## only; the storm is one sitting, no mid-run save (the Sweetgum shape).
##
## Signals · uniform slowstock host contract:
##   quit_to_shelf · caller (SlowstockBoot) reopens the shelf
##   finished(canon_vars, lore_tokens)
##
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal finished(canon_vars: Dictionary, lore_tokens: Array)

const MANIFEST_PATH := "res://resources/games/vol7/spiderdrops/manifest.json"
const SAVE_PATH     := "user://spiderdrops.save.json"
const WEB_SCENE     := "res://scenes/games/spiderdrops/SpiderdropsWeb.tscn"

# PDP toy-bright palette · storm register
const C_SKY    := Color("2b3a52")   # storm slate-blue
const C_SKY2   := Color("47597a")   # lighter band
const C_SILK   := Color("e8ecef")   # web silk
const C_DROP   := Color("6fb7e0")   # rain / water
const C_SPIDER := Color("f2c14e")   # PDP toy-yellow spider
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


func start_new_run(_manager_mode: bool = false) -> void:
	_open_storm()


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


# ─── Title screen ────────────────────────────────────────────────

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
	band.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	band.offset_top = 120
	band.offset_bottom = 300
	_title_root.add_child(band)

	# A hint of the web itself as title art.
	var hero := HeroImage.new()
	if hero.load_from("res://resources/games/vol7/spiderdrops/hero_images/title.json"):
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
	v.offset_left = -320
	v.offset_right = 320
	v.offset_top = -180
	v.offset_bottom = 240
	v.add_theme_constant_override("separation", 12)
	_title_root.add_child(v)

	var shelf: Dictionary = _manifest.get("shelf", {})

	var title := Label.new()
	title.text = String(shelf.get("label_title", "SPIDERDROPS"))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 46)
	title.add_theme_color_override("font_color", C_SPIDER)
	v.add_child(title)

	var subtitle := Label.new()
	subtitle.text = String(shelf.get("label_subtitle", "keep the web up"))
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.add_theme_font_size_override("font_size", 15)
	subtitle.add_theme_color_override("font_color", C_SILK)
	v.add_child(subtitle)

	var meta := Label.new()
	meta.text = "PDP Toys · Beaverton, OR · 1993"
	meta.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	meta.add_theme_font_size_override("font_size", 12)
	meta.add_theme_color_override("font_color", C_DROP)
	v.add_child(meta)

	var sep := Control.new()
	sep.custom_minimum_size = Vector2(0, 14)
	v.add_child(sep)

	var play_btn := Button.new()
	play_btn.text = "  WEATHER THE STORM  "
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
		status.text = "· storms weathered: %d · best: %s ·" % [runs, best if best != "" else "—"]
		status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		status.add_theme_font_size_override("font_size", 12)
		status.add_theme_color_override("font_color", C_DROP)
		v.add_child(status)

	# Verb legend — a toy needs its controls on the box.
	var legend := Label.new()
	legend.text = "MOVE arrows/stick  ·  PLUCK space/A  ·  BRACE hold shift/RT  ·  SPIN s/X"
	legend.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	legend.add_theme_font_size_override("font_size", 12)
	legend.add_theme_color_override("font_color", Color(C_SILK.r, C_SILK.g, C_SILK.b, 0.7))
	v.add_child(legend)

	GamepadMgr.focus_first.call_deferred(_title_root)


func _on_back_to_shelf() -> void:
	quit_to_shelf.emit()


# ─── The storm ───────────────────────────────────────────────────

func _open_storm() -> void:
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/spiderdrops/storm.wav")
	_child_scene = load(WEB_SCENE).instantiate()
	_child_scene.quit.connect(_on_storm_quit)
	_child_scene.run_over.connect(_on_run_over)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_storm_quit() -> void:
	_build_title_screen()


func _on_run_over(result: Dictionary) -> void:
	_run_state["runs"] = int(_run_state.get("runs", 0)) + 1
	var register: String = String(result.get("register", "storm"))
	var seen: Array = _run_state.get("registers_seen", [])
	if not seen.has(register):
		seen.append(register)
	_run_state["registers_seen"] = seen
	# Best = the least-lost register reached (rank order below).
	_run_state["best_register"] = _best_of(String(_run_state.get("best_register", "")), register)
	# Fire this run's tokens durably now — every storm counts, whether or
	# not the player ends the session (puts the cart back) after it.
	_award_run_tokens(register)
	_save_state()
	_show_ending(result)


# Register rank: whole > held > star > storm. Best keeps the highest.
func _register_rank(reg: String) -> int:
	match reg:
		"whole": return 4
		"held":  return 3
		"star":  return 2
		"storm": return 1
		_:       return 0


func _best_of(a: String, b: String) -> String:
	return a if _register_rank(a) >= _register_rank(b) else b


# ─── Ending screen · the register, not a trophy ──────────────────

const REGISTER_TITLE := {
	"whole": "THE WEB HELD",
	"held":  "HELD",
	"star":  "THE EIGHT-POINTED STAR",
	"storm": "THE STORM",
}
const REGISTER_LINE := {
	"whole": "Morning. The web is beaded with light and every strand is where you left it. You kept it whole.",
	"held":  "Morning. The web sags and gaps where the storm got through, but it is standing, and so are you.",
	"star":  "Morning. The soft spiral is gone — all of it. Only the eight spokes remain, and together they make a shape you did not draw. It was always going to be this shape.",
	"storm": "The web came down. It was always going to come down. The storm does not know you were there. You stayed as long as you could.",
}


func _show_ending(result: Dictionary) -> void:
	_clear_current_scene()
	_sfx("page_turn")
	var register: String = String(result.get("register", "storm"))

	_ending_root = Control.new()
	_ending_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_ending_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_ending_root)

	var bg := ColorRect.new()
	bg.color = C_DARK if register == "storm" else C_SKY
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_ending_root.add_child(bg)

	# The register's own picture, held subtle behind the text.
	var hero := HeroImage.new()
	if hero.load_from("res://resources/games/vol7/spiderdrops/hero_images/ending_%s.json" % register):
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
	v.offset_left = -360
	v.offset_right = 360
	v.offset_top = -180
	v.offset_bottom = 220
	v.add_theme_constant_override("separation", 16)
	_ending_root.add_child(v)

	var title := Label.new()
	title.text = String(REGISTER_TITLE.get(register, "THE STORM"))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 34)
	title.add_theme_color_override("font_color", C_SPIDER if register != "storm" else C_SILK)
	v.add_child(title)

	var line := Label.new()
	line.text = String(REGISTER_LINE.get(register, ""))
	line.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	line.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	line.add_theme_font_size_override("font_size", 15)
	line.add_theme_color_override("font_color", C_TXT)
	v.add_child(line)

	var score := Label.new()
	score.text = "held for %d gusts  ·  %d of 8 spokes  ·  %d%% of the web  ·  score %d" % [
		int(result.get("waves_survived", 0)),
		int(result.get("spokes_alive", 0)),
		int(round(float(result.get("spiral_frac", 0.0)) * 100.0)),
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
	again.text = "  another storm  "
	again.add_theme_font_size_override("font_size", 14)
	again.pressed.connect(_open_storm)
	v.add_child(again)

	var done := Button.new()
	done.text = "  put the cart back  "
	done.add_theme_font_size_override("font_size", 14)
	done.pressed.connect(_put_the_cart_back)
	v.add_child(done)

	GamepadMgr.focus_first.call_deferred(_ending_root)


# Fire the completion + register tokens for one storm. Idempotent
# (OneironauticsTokens.add no-ops on repeat); called after every run so
# every storm's register is recorded even across "another storm" loops.
func _award_run_tokens(register: String) -> void:
	var tokens: Array = _run_state.get("lore_tokens_pending", [])
	if not tokens.has("spiderdrops_finished"):
		tokens.append("spiderdrops_finished")
	var reg_token := ""
	match register:
		"whole": reg_token = "spiderdrops_whole"
		"star":  reg_token = "spiderdrops_star"
		"storm": reg_token = "spiderdrops_storm"
	if reg_token != "" and not tokens.has(reg_token):
		tokens.append(reg_token)
	_run_state["lore_tokens_pending"] = tokens
	OneironauticsTokens.add_many(tokens)


func _put_the_cart_back() -> void:
	# End the session: emit finished so SlowstockBoot marks the stick
	# read, advances the collector spine, and merges canon into
	# GauntletState. Carries the BEST register reached this session.
	var canon: Dictionary = _run_state.get("canon_vars", {})
	canon["spiderdrops_result"] = String(_run_state.get("best_register", "storm"))
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
