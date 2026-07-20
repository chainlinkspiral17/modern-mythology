extends Node
## Persistent state for the Tarot Gauntlet — cross-run progression,
## unlocks, achievement progress, lore tokens, codex hotspot states.
## Stored in user://gauntlet_state.json so VN save slots are untouched.

const SAVE_PATH := "user://gauntlet_state.json"

# Per-arcana win/loss counts and the specific things that unlock from
# play (item permanents, alt dies, alt hand variants, etc.)
var state: Dictionary = {
	"version": 1,
	"wins_by_arcana_location": {},     # "fool@dambrosios" → int
	"losses_by_arcana_location": {},   # "fool@dambrosios" → int
	"finale_history": [],              # ["wipe_the_same_spot_forever", ...]
	"achievements_unlocked": [],       # ["win_at_dambrosios", ...]
	"items_unlocked": [],              # ["frasier_pen_permanent", ...]
	"contents_seen": [],               # ["contents_pocket_money", ...]
	"lore_tokens_revealed": [],        # ["frasier_seen", ...]
	"codex_hotspots_surfaced": {},     # "fool" → ["fool_steamboat_echo", ...]
	"cp_scenario_unlocks": [],         # ["death:the_quiet_committal", ...] · Community-Planned → Gauntlet crossover
	"current_run": null,               # optional in-progress run snapshot
	"campaign": {                      # THE MAJOR ARCANA · the Fool's Journey
		"cleared": [],                 # arcana ids cleared in the campaign, in order
		"thread": 0,                   # THE QUERENT'S THREAD · carried insight
		"acts_closed": [],             # [1,2,3] as each act finishes
	},
}


func _ready() -> void:
	_load()


func _load() -> void:
	if not FileAccess.file_exists(SAVE_PATH):
		return
	var f := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if f == null:
		return
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	if typeof(parsed) == TYPE_DICTIONARY:
		# Merge into defaults so older saves don't crash on missing keys
		for k in (parsed as Dictionary):
			state[k] = (parsed as Dictionary)[k]


func _save() -> void:
	var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f == null:
		push_error("GauntletState: failed to open " + SAVE_PATH + " for write")
		return
	f.store_string(JSON.stringify(state, "  "))


# ── Mutations ────────────────────────────────────────────────────────

func record_win(arcana: String, location: String, contents: String,
				lore_tokens: Array, finale: String = "") -> void:
	var key := "%s@%s" % [arcana, location]
	state["wins_by_arcana_location"][key] = int(state["wins_by_arcana_location"].get(key, 0)) + 1
	if contents != "" and not (contents in state["contents_seen"]):
		state["contents_seen"].append(contents)
	for tok in lore_tokens:
		if not (tok in state["lore_tokens_revealed"]):
			state["lore_tokens_revealed"].append(tok)
	if finale != "":
		state["finale_history"].append(finale)
	_save()


func record_loss(arcana: String, location: String, finale: String,
				lore_tokens: Array) -> void:
	var key := "%s@%s" % [arcana, location]
	state["losses_by_arcana_location"][key] = int(state["losses_by_arcana_location"].get(key, 0)) + 1
	state["finale_history"].append(finale)
	# Lore tokens carry over even from losses — see §IV.9 post-loss behavior.
	for tok in lore_tokens:
		if not (tok in state["lore_tokens_revealed"]):
			state["lore_tokens_revealed"].append(tok)
	_save()


# ── THE SPREAD · three-card cross-arcana runs ────────────────────────
# Shape: { "cards": [{arcana, setup, title, outcome}], "idx": int,
#          "carry": {sanity, inertia, held_card} }
# Absent key (or null) = no spread in progress.

func get_spread() -> Dictionary:
	var s: Variant = state.get("spread", null)
	return s if s is Dictionary else {}


func set_spread(d: Dictionary) -> void:
	state["spread"] = d
	_save()


func clear_spread() -> void:
	state.erase("spread")
	_save()


func unlock_achievement(id: String) -> bool:
	if id in state["achievements_unlocked"]:
		return false
	state["achievements_unlocked"].append(id)
	_save()
	return true


func unlock_item(id: String) -> bool:
	if id in state["items_unlocked"]:
		return false
	state["items_unlocked"].append(id)
	_save()
	return true


func record_cp_scenario_unlock(arcana: String, scenario_id: String) -> bool:
	# Community Planned → Gauntlet crossover. Called by the CP effect
	# interpreter's `unlock_gauntlet_scenario` handler when a stage
	# choice grants access to a specific Gauntlet scenario. Returns
	# true if newly recorded, false if already present.
	var key := "%s:%s" % [arcana, scenario_id]
	var arr: Array = state.get("cp_scenario_unlocks", [])
	if key in arr:
		return false
	arr.append(key)
	state["cp_scenario_unlocks"] = arr
	_save()
	return true


func cp_scenario_is_unlocked(arcana: String, scenario_id: String) -> bool:
	var key := "%s:%s" % [arcana, scenario_id]
	return key in state.get("cp_scenario_unlocks", [])


# ── Queries ──────────────────────────────────────────────────────────

func wins_at(arcana: String, location: String) -> int:
	return int(state["wins_by_arcana_location"].get("%s@%s" % [arcana, location], 0))


func total_wins(arcana: String) -> int:
	var total := 0
	for k in state["wins_by_arcana_location"]:
		if k.begins_with(arcana + "@"):
			total += int(state["wins_by_arcana_location"][k])
	return total


func is_arcana_completed(arcana: String) -> bool:
	return total_wins(arcana) > 0


func has_achievement(id: String) -> bool:
	return id in state["achievements_unlocked"]


func has_item_unlock(id: String) -> bool:
	return id in state["items_unlocked"]


# ── THE MAJOR ARCANA campaign ────────────────────────────────────────
# The Fool's Journey · a carried run over the 22. Additive over the
# existing per-arcana win records; the campaign is a framing layer.

func _campaign() -> Dictionary:
	# Older saves merged before this block existed won't have it.
	if not state.has("campaign") or not (state["campaign"] is Dictionary):
		state["campaign"] = {"cleared": [], "thread": 0, "acts_closed": []}
	var c: Dictionary = state["campaign"]
	if not c.has("cleared"):     c["cleared"] = []
	if not c.has("thread"):      c["thread"] = 0
	if not c.has("acts_closed"): c["acts_closed"] = []
	return c


func campaign_cleared() -> Array:
	return _campaign()["cleared"]


func campaign_is_cleared(arcana: String) -> bool:
	return arcana in _campaign()["cleared"]


func campaign_thread() -> int:
	return int(_campaign()["thread"])


func campaign_clear(arcana: String, thread_gain: int) -> bool:
	# Records a campaign win. Returns true if this arcana was newly
	# cleared (so the caller fires tokens / awards once). Idempotent.
	var c := _campaign()
	if arcana in c["cleared"]:
		return false
	(c["cleared"] as Array).append(arcana)
	c["thread"] = int(c["thread"]) + maxi(0, thread_gain)
	_save()
	return true


func campaign_spend_thread(cost: int) -> bool:
	var c := _campaign()
	if int(c["thread"]) < cost:
		return false
	c["thread"] = int(c["thread"]) - cost
	_save()
	return true


func campaign_close_act(n: int) -> bool:
	var c := _campaign()
	if n in c["acts_closed"]:
		return false
	(c["acts_closed"] as Array).append(n)
	_save()
	return true


func campaign_act_closed(n: int) -> bool:
	return n in _campaign()["acts_closed"]


func reset_all() -> void:
	state = {
		"version": 1,
		"wins_by_arcana_location": {},
		"losses_by_arcana_location": {},
		"finale_history": [],
		"achievements_unlocked": [],
		"items_unlocked": [],
		"contents_seen": [],
		"lore_tokens_revealed": [],
		"codex_hotspots_surfaced": {},
		"current_run": null,
		"campaign": {"cleared": [], "thread": 0, "acts_closed": []},
	}
	_save()
