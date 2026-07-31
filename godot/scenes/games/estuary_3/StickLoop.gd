class_name StickLoop
## THE LOOP · the shared progression spine every slowstick hangs on.
##
## The catalog's recurring failure is that runs don't feed anything.
## You play, you get an ending, and the next run starts identical.
## Reported as: "slowstick games just far too basic · I want depth of
## play", and then: "need gameplay loops in each individual game, so
## the progression and reward and customization feed back into each
## other."
##
## The contract, identical in every stick:
##
##   EARN   a finished (or abandoned) run banks CREDIT in the stick's
##          own currency — silver, friendship, catch weight, depth.
##   SPEND  credit buys entries from the stick's loadout.json.
##   CARRY  the stick reads its owned loadout AT BOOT and plays
##          differently: different starting resources, different
##          verbs, different routes open.
##   MASTER runs finished raise a mastery number that GATES the
##          later loadout tiers, so the deep options are earned by
##          playing rather than by grinding one cheap loop.
##
## The rule that keeps this from being a numbers treadmill: at least
## one upgrade per tier must grant a FLAG, not a number. Flags open
## verbs and routes ("you can read the weather", "the south road is
## yours"). Numbers alone are not customization.
##
## Data · res://resources/games/vol7/<stick>/loadout.json:
##
##   {
##     "currency": {"id": "silver", "name": "SILVER",
##                  "earn_line": "silver you rode home with"},
##     "upgrades": [
##       {"id": "long_coat", "name": "THE LONG COAT", "cost": 6,
##        "tier": 1, "needs_mastery": 0, "requires": [],
##        "blurb": "the cold stops taking its cut every third hex.",
##        "effects": {"start_grit": 2},
##        "flags": ["ignores_first_cold_bite"]}
##     ]
##   }
##
## Persistence · user://stick_loop.json · static access from any
## scene, including nested console play inside Pirate Summer, where
## no autoload is guaranteed to be in the loop (same reasoning as
## OneironauticsTokens, which this file deliberately mirrors).
##
## Usage from a stick:
##
##   # at boot
##   var grit: int = 6 + StickLoop.effect("sisters_wyrd", "start_grit")
##   if StickLoop.flag("sisters_wyrd", "ignores_first_cold_bite"): ...
##   # at the end of a run
##   StickLoop.finish_run("sisters_wyrd", {"credit": silver_home,
##       "outcome": "rode_home"})

const PATH := "user://stick_loop.json"
const LOADOUT_FMT := "res://resources/games/vol7/%s/loadout.json"


# ─── raw store ───────────────────────────────────────────────────

static func _read() -> Dictionary:
	if not FileAccess.file_exists(PATH):
		return {}
	var f := FileAccess.open(PATH, FileAccess.READ)
	if f == null:
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		var sticks: Variant = (parsed as Dictionary).get("sticks", {})
		if sticks is Dictionary:
			return sticks
	return {}


static func _write(sticks: Dictionary) -> void:
	var dir := DirAccess.open("user://")
	if dir == null:
		return
	var f := FileAccess.open(PATH, FileAccess.WRITE)
	if f == null:
		return
	f.store_string(JSON.stringify({"version": 1, "sticks": sticks}, "  "))
	f.close()


static func _entry(stick_id: String) -> Dictionary:
	var sticks := _read()
	var e: Variant = sticks.get(stick_id, {})
	if e is Dictionary:
		return e
	return {}


static func _put(stick_id: String, e: Dictionary) -> void:
	var sticks := _read()
	sticks[stick_id] = e
	_write(sticks)


# ─── credit · the EARN half ──────────────────────────────────────

static func credit(stick_id: String) -> int:
	return int(_entry(stick_id).get("credit", 0))


static func earn(stick_id: String, amount: int) -> void:
	if amount <= 0:
		return
	var e := _entry(stick_id)
	e["credit"] = int(e.get("credit", 0)) + amount
	e["lifetime"] = int(e.get("lifetime", 0)) + amount
	_put(stick_id, e)


static func lifetime(stick_id: String) -> int:
	return int(_entry(stick_id).get("lifetime", 0))


static func spend(stick_id: String, amount: int) -> bool:
	var e := _entry(stick_id)
	var have: int = int(e.get("credit", 0))
	if amount > have:
		return false
	e["credit"] = have - amount
	_put(stick_id, e)
	return true


# ─── mastery · runs actually finished ────────────────────────────

static func mastery(stick_id: String) -> int:
	return int(_entry(stick_id).get("runs", 0))


## Call this once, at the end of a run. `result` may carry:
##   credit  · int · banked into the stick's pool
##   outcome · String · recorded so the loadout can gate on it
static func finish_run(stick_id: String, result: Dictionary = {}) -> void:
	var e := _entry(stick_id)
	e["runs"] = int(e.get("runs", 0)) + 1
	var gained: int = int(result.get("credit", 0))
	if gained > 0:
		e["credit"] = int(e.get("credit", 0)) + gained
		e["lifetime"] = int(e.get("lifetime", 0)) + gained
	var outcome := String(result.get("outcome", ""))
	if outcome != "":
		var seen: Array = e.get("outcomes", [])
		if not seen.has(outcome):
			seen.append(outcome)
		e["outcomes"] = seen
	_put(stick_id, e)


static func outcomes(stick_id: String) -> Array:
	var arr: Variant = _entry(stick_id).get("outcomes", [])
	return arr if arr is Array else []


# ─── the loadout · the SPEND half ────────────────────────────────

static func loadout(stick_id: String) -> Dictionary:
	var path: String = LOADOUT_FMT % stick_id
	if not FileAccess.file_exists(path):
		return {}
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	return parsed if parsed is Dictionary else {}


static func has_loadout(stick_id: String) -> bool:
	return FileAccess.file_exists(LOADOUT_FMT % stick_id)


static func owned(stick_id: String) -> Array:
	var arr: Variant = _entry(stick_id).get("owned", [])
	return arr if arr is Array else []


static func owns(stick_id: String, upgrade_id: String) -> bool:
	return owned(stick_id).has(upgrade_id)


static func _upgrade_def(stick_id: String, upgrade_id: String) -> Dictionary:
	for u_v in loadout(stick_id).get("upgrades", []):
		var u: Dictionary = u_v
		if String(u.get("id", "")) == upgrade_id:
			return u
	return {}


## Why an upgrade can't be bought yet, or "" when it can.
static func blocked_reason(stick_id: String, upgrade_id: String) -> String:
	var u := _upgrade_def(stick_id, upgrade_id)
	if u.is_empty():
		return "no such thing"
	if owns(stick_id, upgrade_id):
		return "already yours"
	var need_m: int = int(u.get("needs_mastery", 0))
	if mastery(stick_id) < need_m:
		return "finish %d run%s first" % [need_m, "" if need_m == 1 else "s"]
	for r_v in u.get("requires", []):
		var r := String(r_v)
		if not owns(stick_id, r):
			var rd := _upgrade_def(stick_id, r)
			return "needs %s" % String(rd.get("name", r))
	var cost: int = int(u.get("cost", 0))
	if credit(stick_id) < cost:
		return "costs %d · you have %d" % [cost, credit(stick_id)]
	return ""


static func buy(stick_id: String, upgrade_id: String) -> bool:
	if blocked_reason(stick_id, upgrade_id) != "":
		return false
	var u := _upgrade_def(stick_id, upgrade_id)
	if not spend(stick_id, int(u.get("cost", 0))):
		return false
	var e := _entry(stick_id)
	var have: Array = e.get("owned", [])
	have.append(upgrade_id)
	e["owned"] = have
	_put(stick_id, e)
	return true


# ─── the CARRY half · what a stick reads at boot ─────────────────

## Summed numeric effect of every owned upgrade. Absent → 0.
static func effect(stick_id: String, key: String) -> int:
	var total := 0
	var have := owned(stick_id)
	for u_v in loadout(stick_id).get("upgrades", []):
		var u: Dictionary = u_v
		if not have.has(String(u.get("id", ""))):
			continue
		var eff: Dictionary = u.get("effects", {})
		if eff.has(key):
			total += int(eff[key])
	return total


## True when any owned upgrade grants this capability flag.
static func flag(stick_id: String, key: String) -> bool:
	var have := owned(stick_id)
	for u_v in loadout(stick_id).get("upgrades", []):
		var u: Dictionary = u_v
		if not have.has(String(u.get("id", ""))):
			continue
		for f_v in u.get("flags", []):
			if String(f_v) == key:
				return true
	return false


## Every upgrade with its live purchase state, for the OUTFIT screen.
## Each row: id, name, cost, tier, blurb, owned, buyable, reason.
static func catalog(stick_id: String) -> Array:
	var rows: Array = []
	for u_v in loadout(stick_id).get("upgrades", []):
		var u: Dictionary = u_v
		var uid := String(u.get("id", ""))
		var why := blocked_reason(stick_id, uid)
		rows.append({
			"id": uid,
			"name": String(u.get("name", uid)),
			"cost": int(u.get("cost", 0)),
			"tier": int(u.get("tier", 1)),
			"blurb": String(u.get("blurb", "")),
			"owned": owns(stick_id, uid),
			"buyable": why == "",
			"reason": why,
		})
	return rows


static func currency_name(stick_id: String) -> String:
	var c: Dictionary = loadout(stick_id).get("currency", {})
	return String(c.get("name", "CREDIT"))


static func earn_line(stick_id: String) -> String:
	var c: Dictionary = loadout(stick_id).get("currency", {})
	return String(c.get("earn_line", ""))


## Debug / new-game-plus reset for one stick.
static func forget(stick_id: String) -> void:
	var sticks := _read()
	sticks.erase(stick_id)
	_write(sticks)
