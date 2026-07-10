extends Control
## ScrapbookPanel — a browser for lore tokens revealed across gauntlet runs.
##
## Walks every res://resources/games/*/setup_*.json plus each arcana's
## visitors.json at open-time to build a token→metadata map. Cross-
## references GauntletState.state["lore_tokens_revealed"] to decide
## which tokens are visible and which are still locked (shown as
## "???" with a count).
##
## Follows the same construction pattern as MainMenu._build_achievements_panel.
## F4-compliant via add_to_group("ui") on the root Control.

const GAMES_ROOT := "res://resources/games/"

const C_GOLD      := Color(0.92, 0.78, 0.40)
const C_GOLD_DIM  := Color(0.70, 0.55, 0.24, 0.45)
const C_BG        := Color(0.024, 0.020, 0.014, 0.97)
const C_TXT       := Color(0.83, 0.79, 0.69)
const C_TXT_DIM   := Color(0.50, 0.47, 0.38)
const C_LOCK      := Color(0.42, 0.38, 0.30)

# Arcana display order (Fool → World) with human names for the header.
# The setup files use these short IDs; visitor.json is under each folder.
const ARCANA_ORDER: Array = [
	["fool",              "0 · THE FOOL"],
	["magician",          "I · THE MAGICIAN"],
	["priestess",         "II · THE HIGH PRIESTESS"],
	["empress",           "III · THE EMPRESS"],
	["emperor",           "IV · THE EMPEROR"],
	["hierophant",        "V · THE HIEROPHANT"],
	["lovers",            "VI · THE LOVERS"],
	["chariot",           "VII · THE CHARIOT"],
	["strength",          "VIII · STRENGTH"],
	["hermit",            "IX · THE HERMIT"],
	["wheel_of_fortune",  "X · THE WHEEL OF FORTUNE"],
	["justice",           "XI · JUSTICE"],
	["hanged_man",        "XII · THE HANGED MAN"],
	["death",             "XIII · DEATH"],
	["temperance",        "XIV · TEMPERANCE"],
	["devil",             "XV · THE DEVIL"],
	["tower",             "XVI · THE TOWER"],
	["star",              "XVII · THE STAR"],
	["moon",              "XVIII · THE MOON"],
	["sun",               "XIX · THE SUN"],
	["judgement",         "XX · JUDGEMENT"],
	["world",             "XXI · THE WORLD"],
]


static func build(parent: Node) -> Control:
	# Called by MainMenu._on_scrapbook. Returns a fresh top-level Control
	# that gets add_child'd to the menu. The caller is responsible for
	# add_child; this method only builds.
	var scrapbook := Control.new()
	scrapbook.set_script(load("res://scenes/menu/ScrapbookPanel.gd"))
	scrapbook.name = "ScrapbookPanel"
	return scrapbook


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")   # F4-compliance
	var bank := get_node_or_null("/root/SFXBank")
	if bank: bank.play("scrapbook_open", 0.75)
	_build()


func _build() -> void:
	var revealed: Array = _get_revealed_tokens()
	var by_arcana: Dictionary = _index_tokens_by_arcana()
	var cp_unlocks: Array = _get_cp_scenario_unlocks()
	# Cross-arcana index: character-title → [arcana_id, ...]. Any
	# name that surfaces in more than one arcana is a network node
	# in the summer's larger story. Rendered as "→ also in: X, Y"
	# beneath the token body when the token is revealed.
	var title_to_arcana: Dictionary = _index_titles_across_arcana(by_arcana)

	# Backdrop dim
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.78)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.gui_input.connect(func(ev: InputEvent) -> void:
		if ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed:
			queue_free()
	)
	add_child(dim)

	# Card
	var card := Panel.new()
	card.set_anchors_preset(Control.PRESET_CENTER)
	card.offset_left = -400
	card.offset_right = 400
	card.offset_top = -320
	card.offset_bottom = 320
	var st := StyleBoxFlat.new()
	st.bg_color     = C_BG
	st.border_color = C_GOLD_DIM
	st.set_border_width_all(1)
	card.add_theme_stylebox_override("panel", st)
	add_child(card)

	var vb := VBoxContainer.new()
	vb.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	vb.offset_left = 24
	vb.offset_right = -24
	vb.offset_top = 18
	vb.offset_bottom = -18
	vb.add_theme_constant_override("separation", 6)
	card.add_child(vb)

	# Header
	var total_revealed: int = revealed.size()
	var total_authored: int = 0
	for arc_pair: Array in ARCANA_ORDER:
		var arc_id: String = arc_pair[0]
		total_authored += (by_arcana.get(arc_id, []) as Array).size()

	var hdr := HBoxContainer.new()
	vb.add_child(hdr)
	var ttl := Label.new()
	ttl.text = "SCRAPBOOK · %d / %d LORE FOUND" % [total_revealed, total_authored]
	ttl.add_theme_font_size_override("font_size", 13)
	ttl.add_theme_color_override("font_color", C_GOLD)
	ttl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hdr.add_child(ttl)
	var close_btn := Button.new()
	close_btn.text = "✕"
	close_btn.custom_minimum_size = Vector2(28, 28)
	close_btn.pressed.connect(func() -> void: queue_free())
	hdr.add_child(close_btn)

	# Rule
	var rule := ColorRect.new()
	rule.color = Color(C_GOLD_DIM.r, C_GOLD_DIM.g, C_GOLD_DIM.b, 0.25)
	rule.custom_minimum_size.y = 1
	vb.add_child(rule)

	# Scroll list
	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	vb.add_child(scroll)
	var list := VBoxContainer.new()
	list.add_theme_constant_override("separation", 10)
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(list)

	# Per-arcana group
	for arc_pair: Array in ARCANA_ORDER:
		var arc_id: String = arc_pair[0]
		var arc_name: String = arc_pair[1]
		var tokens: Array = by_arcana.get(arc_id, [])
		if tokens.is_empty():
			continue
		var revealed_here: Array = []
		for tk in tokens:
			if String(tk.get("token", "")) in revealed:
				revealed_here.append(tk)

		# Arcana header
		var arc_hdr := HBoxContainer.new()
		var arc_label := Label.new()
		var color := C_GOLD if not revealed_here.is_empty() else C_LOCK
		arc_label.text = arc_name
		arc_label.add_theme_font_size_override("font_size", 12)
		arc_label.add_theme_color_override("font_color", color)
		arc_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		arc_hdr.add_child(arc_label)
		# Count how many of this arcana's scenarios were unlocked via CP
		# (Community-Planned → Gauntlet crossover). Show as "· +N via
		# CP" next to the token count so the two systems visibly link.
		var cp_here: int = 0
		for u in cp_unlocks:
			if String(u).begins_with(arc_id + ":"):
				cp_here += 1
		var count_label := Label.new()
		if cp_here > 0:
			count_label.text = "%d / %d  · +%d via CP" % [revealed_here.size(), tokens.size(), cp_here]
		else:
			count_label.text = "%d / %d" % [revealed_here.size(), tokens.size()]
		count_label.add_theme_font_size_override("font_size", 12)
		count_label.add_theme_color_override("font_color", C_TXT_DIM)
		arc_hdr.add_child(count_label)
		list.add_child(arc_hdr)

		# Token rows
		for tk in tokens:
			var token_id: String = String(tk.get("token", ""))
			var was_revealed: bool = token_id in revealed
			var row := VBoxContainer.new()
			row.add_theme_constant_override("separation", 1)
			var title_lbl := Label.new()
			if was_revealed:
				title_lbl.text = "    ▷ " + String(tk.get("title", token_id))
				title_lbl.add_theme_color_override("font_color", C_TXT)
			else:
				title_lbl.text = "    · ???"
				title_lbl.add_theme_color_override("font_color", C_LOCK)
			title_lbl.add_theme_font_size_override("font_size", 12)
			row.add_child(title_lbl)
			if was_revealed:
				var body_lbl := Label.new()
				body_lbl.text = "        " + String(tk.get("body", ""))
				body_lbl.add_theme_font_size_override("font_size", 12)
				body_lbl.add_theme_color_override("font_color", C_TXT_DIM)
				body_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
				body_lbl.custom_minimum_size.x = 700
				row.add_child(body_lbl)
				# Cross-arcana links: if this character appears in
				# other arcana, list them as a small "also in:" line.
				# The connection is by title (canonical character
				# name) so it survives token id drift across scenarios.
				var title_key: String = String(tk.get("title", ""))
				var other_arcs: Array = title_to_arcana.get(title_key, [])
				if other_arcs.size() > 1:
					var others: Array = []
					for oa in other_arcs:
						if String(oa) == arc_id:
							continue
						others.append(_arcana_short_name(String(oa)))
					if not others.is_empty():
						var link_lbl := Label.new()
						link_lbl.text = "        → also in: " + ", ".join(others)
						link_lbl.add_theme_font_size_override("font_size", 12)
						link_lbl.add_theme_color_override("font_color", C_GOLD_DIM)
						link_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
						link_lbl.custom_minimum_size.x = 700
						row.add_child(link_lbl)
			list.add_child(row)


# ── Data ──────────────────────────────────────────────────────────

func _get_revealed_tokens() -> Array:
	# GauntletState is an autoload if the game has been run at least once.
	# If it's not present (running scrapbook from a fresh build), degrade
	# to "nothing revealed" cleanly.
	var gs: Node = get_node_or_null("/root/GauntletState")
	if gs == null:
		return []
	var st: Dictionary = gs.get("state") if gs.get("state") is Dictionary else {}
	return st.get("lore_tokens_revealed", [])


func _get_cp_scenario_unlocks() -> Array:
	# Community-Planned → Gauntlet crossover: scenarios unlocked via CP
	# stage-choice effects. Format: ["<arcana>:<scenario_id>", ...].
	var gs: Node = get_node_or_null("/root/GauntletState")
	if gs == null:
		return []
	var st: Dictionary = gs.get("state") if gs.get("state") is Dictionary else {}
	return st.get("cp_scenario_unlocks", [])


# Walks res://resources/games/<arcana>/{setup_*.json, visitors.json}
# and returns a Dictionary keyed by arcana_id → Array of token entries.
# Each entry: {token, title, body, source} where title is the visitor
# name (or threshold flavor first line) and body is the lore_text
# (truncated to ~180 chars for the panel).
func _index_tokens_by_arcana() -> Dictionary:
	var out: Dictionary = {}
	var dir := DirAccess.open(GAMES_ROOT)
	if dir == null:
		return out
	dir.list_dir_begin()
	var entry: String = dir.get_next()
	while entry != "":
		if dir.current_is_dir() and entry != "." and entry != "..":
			var tokens: Array = _index_arcana(entry)
			if not tokens.is_empty():
				out[entry] = tokens
		entry = dir.get_next()
	return out


func _index_arcana(arc_id: String) -> Array:
	var out: Array = []
	var seen_tokens: Dictionary = {}
	var arc_dir_path := GAMES_ROOT + arc_id + "/"
	var arc_dir := DirAccess.open(arc_dir_path)
	if arc_dir == null:
		return out
	arc_dir.list_dir_begin()
	var fname: String = arc_dir.get_next()
	while fname != "":
		if fname.begins_with("setup_") and fname.ends_with(".json"):
			_extract_tokens_from_setup(arc_dir_path + fname, out, seen_tokens)
		fname = arc_dir.get_next()
	# Also pull tokens defined on the canonical visitors.json.
	_extract_tokens_from_visitors_file(arc_dir_path + "visitors.json", out, seen_tokens)
	return out


func _extract_tokens_from_setup(path: String, out: Array, seen: Dictionary) -> void:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if not (parsed is Dictionary):
		return
	var setup: Dictionary = parsed
	# scenario_visitors[] entries
	for v_var in setup.get("scenario_visitors", []):
		var v: Dictionary = v_var
		_add_token(out, seen,
			String(v.get("lore_token", "")),
			String(v.get("name", "")),
			String(v.get("lore_text", "")))
	# thresholds[] entries (each has ending_lore_token + flavor)
	for t_var in setup.get("thresholds", []):
		var t: Dictionary = t_var
		_add_token(out, seen,
			String(t.get("ending_lore_token", "")),
			String(t.get("label", "")),
			String(t.get("flavor", "")))


func _extract_tokens_from_visitors_file(path: String, out: Array, seen: Dictionary) -> void:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if not (parsed is Dictionary):
		return
	var d: Dictionary = parsed
	for v_var in d.get("visitors", []):
		var v: Dictionary = v_var
		_add_token(out, seen,
			String(v.get("lore_token", "")),
			String(v.get("name", "")),
			String(v.get("lore_text", "")))
	for v_var in d.get("passive_witnesses", []):
		var v: Dictionary = v_var
		_add_token(out, seen,
			String(v.get("lore_token", "")),
			String(v.get("name", "")),
			String(v.get("lore_text", "")))


# Walks the arcana→tokens map and returns a Dictionary of
# title → [arcana_id, ...]. A title that appears in more than one
# arcana is a cross-mode character: e.g. "The Lacombe Sisters"
# might surface in Empress, Death, and Hermit. Used to render the
# "→ also in:" line under each revealed token.
#
# Also scans every OTHER arcana's token bodies for mentions of
# this title as a substring · a character that appears in one
# arcana as the visitor and shows up in another arcana's threshold
# flavor is still a cross-connection, even if they don't have a
# token of their own there. Case-insensitive substring match with
# a minimum length so common words don't false-positive.
func _index_titles_across_arcana(by_arcana: Dictionary) -> Dictionary:
	var out: Dictionary = {}
	# First pass · direct title matches.
	for arc_id in by_arcana.keys():
		var tokens: Array = by_arcana[arc_id]
		for tk_var in tokens:
			var tk: Dictionary = tk_var
			var title: String = String(tk.get("title", ""))
			if title == "":
				continue
			var arr: Array = out.get(title, [])
			if not arr.has(String(arc_id)):
				arr.append(String(arc_id))
				out[title] = arr
	# Second pass · body scan. For each unique title, see whether
	# any OTHER arcana's token bodies mention it as a substring.
	# Skip titles under 5 characters to avoid matching "The" and
	# other common prefixes.
	for title in out.keys():
		var t: String = String(title)
		if t.length() < 5:
			continue
		var t_lower: String = t.to_lower()
		for arc_id in by_arcana.keys():
			var arcs: Array = out[title]
			if arcs.has(String(arc_id)):
				continue
			for tk_var in by_arcana[arc_id]:
				var tk: Dictionary = tk_var
				var body: String = String(tk.get("body", "")).to_lower()
				if body.find(t_lower) >= 0:
					arcs.append(String(arc_id))
					out[title] = arcs
					break
	return out


# Short display name for an arcana in the "→ also in:" line. Full
# roman-numeral names would wrap and dominate the row; this trims
# to just the card's name (e.g. "III · THE EMPRESS" → "empress").
func _arcana_short_name(arc_id: String) -> String:
	for pair in ARCANA_ORDER:
		if String(pair[0]) == arc_id:
			var full: String = String(pair[1])
			var tail: String = full.substr(full.find("·") + 1).strip_edges().to_lower()
			return tail.trim_prefix("the ")
	return arc_id


func _add_token(out: Array, seen: Dictionary, token: String, title: String, body: String) -> void:
	if token == "" or seen.has(token):
		return
	seen[token] = true
	# Truncate body to keep the panel scannable.
	var body_short := body
	if body_short.length() > 220:
		body_short = body_short.substr(0, 217) + "…"
	out.append({
		"token": token,
		"title": title,
		"body":  body_short,
	})
