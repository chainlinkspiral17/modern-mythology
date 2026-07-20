extends RefCounted
class_name AlmanacState
## THE ONEIRONAUT'S ALMANAC · state reader.
##
## Thin, READ-ONLY layer over the stores the four pillars already
## write — OneironauticsTokens (flat cross-pillar token set) and
## GauntletState (arcana wins / canon vars). Aggregates them into the
## Almanac's chapters and evaluates the additive cross-pillar unlock
## rules. Never migrates a save, never gates base content.
##
## Design: lore/_ONEIRONAUTS_ALMANAC_DESIGN.md
##
## Static, like OneironauticsTokens — no autoload registration needed.
## GauntletState (a real autoload) is reached through the main loop.

const ENTRIES_PATH := "res://resources/almanac/almanac.json"
const UNLOCKS_PATH  := "res://resources/almanac/almanac_unlocks.json"
const TOKENS := preload("res://scenes/games/estuary_3/OneironauticsTokens.gd")


static func _gauntlet() -> Node:
	var ml := Engine.get_main_loop()
	if ml is SceneTree:
		return (ml as SceneTree).root.get_node_or_null("/root/GauntletState")
	return null


# ── predicate evaluation ──────────────────────────────────────────
# Predicate shapes (all optional, composable):
#   {"token": "x"}              · OneironauticsTokens.has("x")
#   {"token_prefix": "x_"}      · any held token starts with "x_"
#   {"arcana_won": "fool"}      · GauntletState says that arcana is done
#   {"all_arcana": true}        · every one of the 22 is done
#   {"canon": "k", "eq": "v"}   · GauntletState canon var k == v (v
#                                 optional → just "k is set & truthy")
#   {"any": [pred,...]}         · at least one holds
#   {"all": [pred,...]}         · every one holds
static func predicate_met(pred: Dictionary) -> bool:
	if pred.has("any"):
		for p in pred["any"]:
			if predicate_met(p): return true
		return false
	if pred.has("all"):
		for p in pred["all"]:
			if not predicate_met(p): return false
		return true
	if pred.has("token"):
		return TOKENS.has(String(pred["token"]))
	if pred.has("token_prefix"):
		var pre := String(pred["token_prefix"])
		for t in TOKENS.all():
			if String(t).begins_with(pre): return true
		return false
	if pred.has("arcana_won"):
		var g := _gauntlet()
		if g == null: return false
		if g.has_method("is_arcana_completed"):
			return bool(g.call("is_arcana_completed", String(pred["arcana_won"])))
		return false
	if pred.has("all_arcana"):
		var g2 := _gauntlet()
		if g2 == null or not g2.has_method("is_arcana_completed"):
			return false
		for a in ARCANA:
			if not bool(g2.call("is_arcana_completed", a)): return false
		return true
	if pred.has("canon"):
		var g3 := _gauntlet()
		if g3 == null: return false
		var cv: Dictionary = {}
		if "state" in g3:
			cv = (g3.get("state") as Dictionary).get("canon_vars", {})
		var key := String(pred["canon"])
		if not cv.has(key): return false
		if pred.has("eq"):
			return String(cv[key]) == String(pred["eq"])
		return bool(cv[key])
	return false


const ARCANA := ["fool", "magician", "priestess", "empress", "emperor",
	"hierophant", "lovers", "chariot", "strength", "hermit",
	"wheel_of_fortune", "justice", "hanged_man", "death", "temperance",
	"devil", "tower", "star", "moon", "sun", "judgement", "world"]


# ── entries ───────────────────────────────────────────────────────

static func load_entries() -> Array:
	if not FileAccess.file_exists(ENTRIES_PATH):
		return []
	var f := FileAccess.open(ENTRIES_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		return (parsed as Dictionary).get("entries", [])
	return []


static func entry_is_lit(entry: Dictionary) -> bool:
	var req: Array = entry.get("requires", [])
	for pred in req:
		if not predicate_met(pred): return false
	return not req.is_empty() or bool(entry.get("always", false))


static func chapters() -> Array:
	# Distinct chapter ids in authored order.
	var out: Array = []
	for e in load_entries():
		var c := String((e as Dictionary).get("chapter", ""))
		if c != "" and not out.has(c): out.append(c)
	return out


static func chapter_progress(chapter: String, entries: Array = []) -> Vector2i:
	# Returns (lit, total) for one chapter.
	var es: Array = entries if not entries.is_empty() else load_entries()
	var lit := 0
	var total := 0
	for e_v in es:
		var e: Dictionary = e_v
		if String(e.get("chapter", "")) != chapter: continue
		total += 1
		if entry_is_lit(e): lit += 1
	return Vector2i(lit, total)


# ── cross-pillar unlocks ──────────────────────────────────────────
# almanac_unlocks.json · rules of {when: [pred...], grant_token: "x"}.
# Additive only: fires a token the entries (and any pillar) can honor.
# Idempotent — a rule whose token is already held is skipped. Returns
# the list of tokens newly granted this pass.
static func evaluate_unlocks() -> Array:
	if not FileAccess.file_exists(UNLOCKS_PATH):
		return []
	var f := FileAccess.open(UNLOCKS_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if not (parsed is Dictionary):
		return []
	var granted: Array = []
	for rule_v in (parsed as Dictionary).get("rules", []):
		var rule: Dictionary = rule_v
		var tok := String(rule.get("grant_token", ""))
		if tok == "" or TOKENS.has(tok):
			continue
		var when: Array = rule.get("when", [])
		var ok := not when.is_empty()
		for pred in when:
			if not predicate_met(pred):
				ok = false
				break
		if ok:
			TOKENS.add(tok)
			granted.append(tok)
	return granted
