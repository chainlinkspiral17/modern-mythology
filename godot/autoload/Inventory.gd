extends Node
## Inventory — autoload. The player's bag of carryable items found
## across cards.
##
## Items are picked up from hotspots that declare `gives_item: <id>`
## in their puzzle_hooks JSON. A separate hotspot on the same or a
## different card can declare `requires_item: <id>` to become a
## "use this here" target — the cursor flips to USE while carrying
## the matching item, and clicking fires a combined unlock.
##
## State persists to user://progress/inventory.cfg via the SaveSystem
## convention (separate file so SaveSystem's gallery and unlocks files
## stay tidy).

const STORE_PATH := "user://progress/inventory.cfg"
const ITEMS_INDEX_PATH := "res://resources/inventory/_items.json"

signal item_added(id: String)
signal item_removed(id: String)
signal item_used(id: String, target_hotspot_id: String)

var _items: Dictionary = {}    # id -> Dictionary {name, icon, from_card, ts}
var _catalog: Dictionary = {}  # id -> Dictionary {name, icon, blurb, ...}

func _ready() -> void:
	_load_catalog()
	_load_state()

# ── Public API ────────────────────────────────────────────────────

func has(item_id: String) -> bool:
	return _items.has(item_id)

func all() -> Array:
	return _items.keys()

func count() -> int:
	return _items.size()

func describe(item_id: String) -> Dictionary:
	# Merge live + catalog so callers can render full UI without two lookups.
	var d: Dictionary = {}
	if _catalog.has(item_id):
		d.merge(_catalog[item_id])
	if _items.has(item_id):
		d.merge(_items[item_id])
	d["id"] = item_id
	return d

func add(item_id: String, from_card: String = "") -> bool:
	# Returns true only on the first successful add for this id.
	if _items.has(item_id):
		return false
	var entry := {
		"from_card": from_card,
		"ts": Time.get_unix_time_from_system(),
	}
	_items[item_id] = entry
	_save_state()
	item_added.emit(item_id)
	return true

func remove(item_id: String) -> bool:
	if not _items.has(item_id):
		return false
	_items.erase(item_id)
	_save_state()
	item_removed.emit(item_id)
	return true

func mark_used(item_id: String, target_hotspot_id: String,
				consume: bool = false) -> bool:
	if not _items.has(item_id):
		return false
	item_used.emit(item_id, target_hotspot_id)
	if consume:
		remove(item_id)
	return true

# Catalog lookup for UI / inspection.
func catalog_entry(item_id: String) -> Dictionary:
	return _catalog.get(item_id, {})

# ── Persistence ────────────────────────────────────────────────────

func _load_state() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(STORE_PATH) != OK:
		return
	if not cfg.has_section("items"):
		return
	for key in cfg.get_section_keys("items"):
		var val = cfg.get_value("items", key, null)
		if typeof(val) == TYPE_DICTIONARY:
			_items[key] = val
		else:
			_items[key] = {}

func _save_state() -> void:
	DirAccess.make_dir_recursive_absolute("user://progress")
	var cfg := ConfigFile.new()
	for key in _items:
		cfg.set_value("items", key, _items[key])
	cfg.save(STORE_PATH)

# ── Catalog ────────────────────────────────────────────────────────
# Optional shared catalog so item display data (name, blurb, icon
# path) lives in a single resource file rather than scattered across
# every puzzle_hooks JSON. Falls back to id-as-name if the catalog
# is missing or doesn't know an item.

func _load_catalog() -> void:
	if not FileAccess.file_exists(ITEMS_INDEX_PATH):
		return
	var f := FileAccess.open(ITEMS_INDEX_PATH, FileAccess.READ)
	var data: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if typeof(data) != TYPE_DICTIONARY:
		return
	for key in data.keys():
		var v = data[key]
		if typeof(v) == TYPE_DICTIONARY:
			_catalog[key] = v
