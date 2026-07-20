extends RefCounted
class_name OneironauticsTokens
## Cross-Oneironautics token store · the connective tissue between
## slowsticks.
##
## Fey Faire, Earthman Chronicles, Pirate Summer, and Estuary 3 all
## EMIT lore tokens when runs finish (endings seen, corrections
## found, feys returned).  This store is the durable place those
## tokens land so OTHER games can consume them:
##
##   · BRING BACK THE LOST (Andrew) rewrites Wilson's dialogue in
##     Pirate Summer
##   · THE CORRECTION puts Rocha's note in Fey Faire's trailer
##     bookcase
##   · the Kelait mourning song's final bar becomes recognizable in
##     Wilson's Portuguese shanty
##
## File-backed at user://oneironautics_tokens.json · no autoload
## registration needed · static access from any scene, including
## nested console play inside Pirate Summer, where GauntletState
## may not be in the loop.
##
## Usage:
##   OneironauticsTokens.add("earthman_correction_ending_seen")
##   if OneironauticsTokens.has("fey_faire_lost_person_returned"): ...

const PATH := "user://oneironautics_tokens.json"


static func all() -> Array:
	if not FileAccess.file_exists(PATH):
		return []
	var f := FileAccess.open(PATH, FileAccess.READ)
	if f == null:
		return []
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		var arr: Variant = (parsed as Dictionary).get("tokens", [])
		if arr is Array:
			return arr
	return []


static func has(token: String) -> bool:
	return all().has(token)


static func add(token: String) -> void:
	if token == "":
		return
	var tokens := all()
	if tokens.has(token):
		return
	tokens.append(token)
	_write(tokens)


static func add_many(new_tokens: Array) -> void:
	var tokens := all()
	var changed := false
	for t in new_tokens:
		var ts := String(t)
		if ts != "" and not tokens.has(ts):
			tokens.append(ts)
			changed = true
	if changed:
		_write(tokens)


static func _write(tokens: Array) -> void:
	var f := FileAccess.open(PATH, FileAccess.WRITE)
	if f == null:
		return
	f.store_string(JSON.stringify({"tokens": tokens}, "  "))
	f.close()


# ─── Cross-stick chronicle reads ─────────────────────────────────
# The token set above holds boolean lore flags. Richer run outcomes
# land in GauntletState.state as `canon_vars` (key → value) and
# `slowsticks_finished` (which sticks are done). These readers
# centralize the /root/GauntletState lookup that consumers would
# otherwise hand-roll, and — like the token store — work from any
# context, including static callers with no scene `self`, via
# Engine.get_main_loop(). GauntletState absent (test scenes, nested
# console play) returns empty/defaults, never crashes.

static func _gauntlet_state() -> Dictionary:
	var ml := Engine.get_main_loop()
	if not (ml is SceneTree):
		return {}
	var root := (ml as SceneTree).root
	if root == null:
		return {}
	var gs := root.get_node_or_null("/root/GauntletState")
	if gs == null:
		return {}
	var st: Variant = gs.get("state")
	return st if st is Dictionary else {}


## Value of a cross-run canon var (e.g. "tideline_report",
## "estuary_3_ending"), or default_value if unset.
static func canon(key: String, default_value: Variant = "") -> Variant:
	var cv: Variant = _gauntlet_state().get("canon_vars", {})
	if cv is Dictionary and (cv as Dictionary).has(key):
		return (cv as Dictionary)[key]
	return default_value


## The list of stick ids the player has finished.
static func finished_sticks() -> Array:
	var arr: Variant = _gauntlet_state().get("slowsticks_finished", [])
	return arr if arr is Array else []


## True if a specific stick has been finished at least once.
static func is_stick_finished(stick_id: String) -> bool:
	return finished_sticks().has(stick_id)


## How many sticks are finished (raw count, includes the remake).
static func finished_count() -> int:
	return finished_sticks().size()
