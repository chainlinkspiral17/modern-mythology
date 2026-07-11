extends Control
## Pirate Summer · run controller.
##
## Boots the CampOverworld with a starting zone/spawn from the
## manifest, forwards `quit_to_shelf` and `finished` up to
## SlowstockBoot in the same shape Estuary3Host uses.
##
## Persists run state to `user://pirate_summer.save.json`.
## Wave B state is minimal (zone, spawn, day_index).  Later
## waves grow it: party roster, friendship meters, duffel
## contents, discovered clues, stat spikes, journal entries.
##
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal finished(canon_vars: Dictionary, lore_tokens: Array)

const MANIFEST_PATH := "res://resources/games/vol7/pirate_summer/manifest.json"
const SAVE_PATH     := "user://pirate_summer.save.json"

var _manifest: Dictionary = {}
var _run_state: Dictionary = {
	"zone":       "cabin_sturgeon",
	"spawn":      "start",
	"day_index":  0,          # 0=Sunday, 1=Monday, ... 6=Saturday
	"time_index": 0,          # 0=wake · 1=breakfast · ... · 9=lights_out
	"party":      [],         # ["wu_kai", ...] · Sam always implicit
	"friendship": {},         # camper_id → int 0..5
	"canon_vars": {},
	"lore_tokens_pending": [],
	"duffel":     [],         # inventory slots (deferred)
	"stats":      {"body": 2, "heart": 2, "mind": 2, "luck": 2, "sneak": 2, "knack": 2},
	"fatigue":    0,
	"hunger":     0,
	"discovered_facts": [],
	"used_chatter_ids": [],
}

var _overworld: Node = null


func _play_bgm(path: String) -> void:
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("play_bgm"):
		am.play_bgm(path)


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	SlowstickLook.apply(self, "oneironautics")
	# Studio control chrome (mirrors the look preset) — cascades
	# to every child scene; see StickTheme.gd.
	theme = preload("res://scenes/games/StickTheme.gd").make("oneironautics")
	_load_manifest()
	_load_save_if_present()
	_build_title_screen()


func _load_save_if_present() -> void:
	if not FileAccess.file_exists(SAVE_PATH): return
	var f := FileAccess.open(SAVE_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		var saved: Dictionary = parsed
		# Merge saved fields over the default run state so a stale save
		# missing a newly-added field doesn't nuke the default.
		for k in saved.keys():
			_run_state[String(k)] = saved[k]


func start_new_run(_unused: bool = false) -> void:
	# Match Estuary3Host's start_new_run(manager_mode) signature so
	# SlowstockBoot can call it uniformly. `manager_mode` is ignored
	# here · Counselor Mode is Pirate Summer's analog and ships in
	# Wave O.
	if _title_root != null and is_instance_valid(_title_root):
		_title_root.queue_free()
		_title_root = null
	_run_state = {
		"zone":       String(_manifest.get("start_zone", "cabin_sturgeon")),
		"spawn":      String(_manifest.get("start_spawn", "start")),
		"day_index":  0,
		"time_index": 0,
		"party":      [],
		"friendship": {},
		"canon_vars": {},
		"lore_tokens_pending": [],
		"duffel":     [],
		"stats":      {"body": 2, "heart": 2, "mind": 2, "luck": 2, "sneak": 2, "knack": 2},
		"fatigue":    0,
		"hunger":     0,
		"discovered_facts": [],
		"used_chatter_ids": [],
	}
	_save()
	if _overworld != null and is_instance_valid(_overworld):
		_overworld.queue_free()
		_overworld = null
	_boot_overworld()


func _load_manifest() -> void:
	if not FileAccess.file_exists(MANIFEST_PATH):
		push_warning("[PirateSummerHost] missing %s" % MANIFEST_PATH)
		return
	var f := FileAccess.open(MANIFEST_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		_manifest = parsed
		# Seed initial run state from manifest defaults on cold boot.
		if String(_run_state.get("zone", "")) == "cabin_sturgeon":
			_run_state["zone"]  = String(_manifest.get("start_zone", "cabin_sturgeon"))
			_run_state["spawn"] = String(_manifest.get("start_spawn", "start"))


# ─── Title · ease in, establish the summer ──────────────────────

var _title_root: Control = null


func _build_title_screen() -> void:
	if _title_root != null and is_instance_valid(_title_root):
		_title_root.queue_free()
	_title_root = Control.new()
	_title_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_title_root)

	var bg := ColorRect.new()
	bg.color = Color(0.055, 0.075, 0.09, 1.0)
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.add_child(bg)

	# The first campfire night — the summer's front cover.
	var hero := HeroImage.new()
	if hero.load_from("res://resources/games/vol7/pirate_summer/sprites/scenes/moment_first_campfire_night.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(800, 450))
		tex_rect.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		tex_rect.offset_left = -400
		tex_rect.offset_right = 400
		tex_rect.offset_top = -310
		tex_rect.offset_bottom = 140
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		_title_root.add_child(tex_rect)

	# Fireflies over the water (menu motion playbook).
	preload("res://scenes/games/TitleMotion.gd").attach(_title_root, "oneironautics")

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -360
	v.offset_right = 360
	v.offset_top = 130
	v.offset_bottom = 360
	v.add_theme_constant_override("separation", 10)
	_title_root.add_child(v)

	var title := Label.new()
	title.text = "PIRATE SUMMER"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 36)
	title.add_theme_color_override("font_color", Color(0.95, 0.9, 0.78, 1.0))
	v.add_child(title)

	var premise := Label.new()
	premise.text = "June 1988 · Camp Sweetgum, one week · you are Sam, eleven years old.\nMake friends. Follow what the counselors won't say. Dig where the map says dig."
	premise.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	premise.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	premise.add_theme_font_size_override("font_size", 14)
	premise.add_theme_color_override("font_color", Color(0.62, 0.72, 0.68, 1.0))
	v.add_child(premise)

	var start_btn := Button.new()
	start_btn.text = "  BEGIN THE WEEK  " if int(_run_state.get("day_index", 0)) == 0 else "  BACK TO CAMP  "
	start_btn.add_theme_font_size_override("font_size", 14)
	start_btn.pressed.connect(func() -> void:
		if _title_root != null and is_instance_valid(_title_root):
			_title_root.queue_free()
			_title_root = null
		_boot_overworld())
	v.add_child(start_btn)

	var back_btn := Button.new()
	back_btn.text = "  ← back to shelf  "
	back_btn.flat = true
	back_btn.add_theme_font_size_override("font_size", 13)
	back_btn.pressed.connect(func() -> void: quit_to_shelf.emit())
	v.add_child(back_btn)


func _boot_overworld() -> void:
	var scene: PackedScene = load("res://scenes/games/pirate_summer/CampOverworld.tscn")
	if scene == null:
		push_warning("[PirateSummerHost] CampOverworld.tscn failed to load")
		return
	_overworld = scene.instantiate()
	add_child(_overworld)
	if _overworld.has_signal("quit_to_shelf"):
		_overworld.quit_to_shelf.connect(func() -> void: quit_to_shelf.emit())
	if _overworld.has_signal("zone_changed"):
		_overworld.zone_changed.connect(_on_zone_changed)
	if _overworld.has_signal("run_finished"):
		_overworld.run_finished.connect(_on_run_finished)
	if _overworld.has_signal("party_changed"):
		_overworld.party_changed.connect(_on_party_changed)
	if _overworld.has_signal("day_advanced"):
		_overworld.day_advanced.connect(_on_day_advanced)
	if _overworld.has_signal("facts_discovered"):
		_overworld.facts_discovered.connect(_on_facts_discovered)
	if _overworld.has_signal("time_advanced"):
		_overworld.time_advanced.connect(_on_time_advanced)
	_overworld.call_deferred("boot", _run_state)


func _on_zone_changed(zone_id: String, spawn_id: String) -> void:
	_run_state["zone"] = zone_id
	_run_state["spawn"] = spawn_id
	_save()


func _on_party_changed(party: Array, friendship: Dictionary) -> void:
	_run_state["party"] = party
	_run_state["friendship"] = friendship
	_save()


func _on_day_advanced(day_index: int) -> void:
	_run_state["day_index"] = day_index
	_save()


func _on_facts_discovered(discovered: Array) -> void:
	_run_state["discovered_facts"] = discovered
	_save()


func _on_time_advanced(day_index: int, time_index: int) -> void:
	_run_state["day_index"] = day_index
	_run_state["time_index"] = time_index
	_save()


func _on_run_finished(_canon_vars: Dictionary, _lore_tokens: Array) -> void:
	# Camp week done · tear down the overworld and mount the ending
	# scene.  The ending reads _run_state and picks the right epilogue.
	_open_ending_scene()


func _open_ending_scene() -> void:
	if _overworld != null and is_instance_valid(_overworld):
		_overworld.queue_free()
		_overworld = null
	var scene: PackedScene = load("res://scenes/games/pirate_summer/PirateSummerEnding.tscn")
	if scene == null:
		push_warning("[PirateSummerHost] PirateSummerEnding.tscn failed to load")
		return
	var ending := scene.instantiate()
	add_child(ending)
	if ending.has_signal("quit_to_shelf"):
		ending.quit_to_shelf.connect(func() -> void: quit_to_shelf.emit())
	if ending.has_signal("finished"):
		ending.finished.connect(_on_ending_finished)
	ending.call_deferred("boot", _run_state)


func _on_ending_finished(canon_vars: Dictionary, lore_tokens: Array) -> void:
	var cv: Dictionary = _run_state.get("canon_vars", {})
	for k in canon_vars.keys():
		cv[String(k)] = canon_vars[k]
	_run_state["canon_vars"] = cv
	var pending: Array = _run_state.get("lore_tokens_pending", [])
	for t in lore_tokens:
		var s := String(t)
		if not pending.has(s):
			pending.append(s)
	_run_state["lore_tokens_pending"] = pending
	_save()
	finished.emit(cv, pending)


func _save() -> void:
	var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f == null:
		return
	f.store_string(JSON.stringify(_run_state, "\t"))
	f.close()
