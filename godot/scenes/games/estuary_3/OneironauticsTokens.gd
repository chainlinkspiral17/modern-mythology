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
