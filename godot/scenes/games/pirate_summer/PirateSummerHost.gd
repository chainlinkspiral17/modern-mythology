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
	"party":      [],         # ["wu_kai", ...] · Sam always implicit
	"friendship": {},         # camper_id → int 0..5
	"canon_vars": {},
	"lore_tokens_pending": [],
	"duffel":     [],         # inventory slots (deferred)
	"stats":      {"body": 2, "heart": 2, "mind": 2, "luck": 2, "sneak": 2, "knack": 2},
	"fatigue":    0,
	"hunger":     0,
}

var _overworld: Node = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	_load_manifest()
	_boot_overworld()


func start_new_run(_unused: bool = false) -> void:
	# Match Estuary3Host's start_new_run(manager_mode) signature so
	# SlowstockBoot can call it uniformly. `manager_mode` is ignored
	# here · Counselor Mode is Pirate Summer's analog and ships in
	# Wave O.
	_run_state = {
		"zone":       String(_manifest.get("start_zone", "cabin_sturgeon")),
		"spawn":      String(_manifest.get("start_spawn", "start")),
		"day_index":  0,
		"party":      [],
		"friendship": {},
		"canon_vars": {},
		"lore_tokens_pending": [],
		"duffel":     [],
		"stats":      {"body": 2, "heart": 2, "mind": 2, "luck": 2, "sneak": 2, "knack": 2},
		"fatigue":    0,
		"hunger":     0,
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
	_overworld.call_deferred("boot", _run_state)


func _on_zone_changed(zone_id: String, spawn_id: String) -> void:
	_run_state["zone"] = zone_id
	_run_state["spawn"] = spawn_id
	_save()


func _on_run_finished(canon_vars: Dictionary, lore_tokens: Array) -> void:
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
