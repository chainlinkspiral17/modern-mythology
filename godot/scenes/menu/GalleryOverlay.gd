extends Control
## Gallery overlay — shows all CG images found in scene data plus any
## ASCII substrate gallery items listed in
## res://resources/substrates/gallery/_index.json.
## Locked tiles for unseen, full-screen viewer on click.

signal closed

const C_GOLD   := Color(0.78, 0.66, 0.29)
const C_BG     := Color(0.024, 0.020, 0.014, 0.97)
const C_BORDER := Color(0.70, 0.55, 0.24, 0.35)
const C_TXT    := Color(0.83, 0.79, 0.69)
const C_DIM    := Color(0.30, 0.28, 0.24, 0.6)
const THUMB_W  := 180
const THUMB_H  := 120

const SUBSTRATE_INDEX := "res://resources/substrates/gallery/_index.json"
const SUBSTRATE_RASTER_SCRIPT := preload("res://scenes/game/AsciiSubstrateRaster.gd")
const COMPOSITION_SCRIPT := preload("res://scenes/game/AsciiComposition.gd")
const DEBUG_OVERLAY_SCRIPT := preload("res://scenes/menu/SubstrateDebugOverlay.gd")
const CARD_INTERACTIVE_SCRIPT := preload("res://scenes/menu/CardInteractiveLayer.gd")
const DISCOVERIES_PANEL_SCRIPT := preload("res://scenes/menu/DiscoveriesPanel.gd")
const FOOL_VISUALIZER_SCRIPT  := preload("res://scenes/menu/FoolVisualizer.gd")
const EMPRESS_VISUALIZER_SCRIPT := preload("res://scenes/menu/EmpressVisualizer.gd")
const MAGICIAN_VISUALIZER_SCRIPT := preload("res://scenes/menu/MagicianVisualizer.gd")
const PRIESTESS_VISUALIZER_SCRIPT := preload("res://scenes/menu/PriestessVisualizer.gd")
const EMPEROR_VISUALIZER_SCRIPT := preload("res://scenes/menu/EmperorVisualizer.gd")
const HIEROPHANT_VISUALIZER_SCRIPT := preload("res://scenes/menu/HierophantVisualizer.gd")
const LOVERS_VISUALIZER_SCRIPT := preload("res://scenes/menu/LoversVisualizer.gd")
const CHARIOT_VISUALIZER_SCRIPT := preload("res://scenes/menu/ChariotVisualizer.gd")
const TAROT_SYNTH_SCRIPT      := preload("res://scenes/menu/TarotSynthOverlay.gd")

# Per-card dedicated visualizers — bypass the generic fullscreen viewer
# when entries here match the item's path. Each visualizer is bespoke
# to its arcana's theme. Start with the Fool's RUST_CODE.BBS terminal.
const DEDICATED_VISUALIZERS := {
	"fool_arcana": "FOOL_VISUALIZER_SCRIPT",
}

# Mirrors MainMenu.VOLUME_META — used to label per-volume gallery sections.
const VOLUME_TITLES: Dictionary = {
	1:  "Modern Mythology",
	2:  "Small Wood Volumes",
	3:  "The Earthman Chronicles",
	4:  "#/Sharp",
	5:  "Major Arcana",
	6:  "Planned Community",
	7:  "Land of Milk & Honey",
	8:  "SCUMM",
	9:  "Por Puesto",
	10: "ROFLcopter",
}


func open() -> void:
	_rebuild()
	visible = true


func _rebuild() -> void:
	for ch in get_children():
		ch.queue_free()

	var backdrop := ColorRect.new()
	backdrop.color = Color(0, 0, 0, 0.7)
	backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(backdrop)

	var card := Panel.new()
	card.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	card.offset_left   = 60
	card.offset_right  = -60
	card.offset_top    = 40
	card.offset_bottom = -40
	var st := StyleBoxFlat.new()
	st.bg_color     = C_BG
	st.border_color = C_BORDER
	st.set_border_width_all(1)
	card.add_theme_stylebox_override("panel", st)
	add_child(card)

	var vbox := VBoxContainer.new()
	vbox.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	vbox.offset_left   = 28
	vbox.offset_right  = -28
	vbox.offset_top    = 20
	vbox.offset_bottom = -20
	vbox.add_theme_constant_override("separation", 12)
	card.add_child(vbox)

	var header_row := HBoxContainer.new()
	vbox.add_child(header_row)
	var title_lbl := Label.new()
	title_lbl.text = "GALLERY"
	_apply_font(title_lbl, SkinDB.F_CINZEL, 13, C_GOLD)
	title_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header_row.add_child(title_lbl)
	var seen_cgs := SaveSystem.get_seen_cgs()
	var all_cgs  := SceneDataDB.get_all_cg_ids()
	var subs     := _load_substrate_index()
	var count_lbl := Label.new()
	count_lbl.text = "%d / %d   +%d ascii" % [seen_cgs.size(), all_cgs.size(), subs.size()]
	_apply_font(count_lbl, SkinDB.F_CINZEL, 10, Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.6))
	count_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	count_lbl.horizontal_alignment  = HORIZONTAL_ALIGNMENT_RIGHT
	header_row.add_child(count_lbl)
	# Discoveries pill — invisible until first cipher reveal, then
	# lights up with a live count. Click to expand a list of finds
	# grouped by card. The "wait, the gallery has a layer" hook.
	var discoveries := Control.new()
	discoveries.set_script(DISCOVERIES_PANEL_SCRIPT)
	header_row.add_child(discoveries)
	var close_btn := Button.new()
	close_btn.text = "✕"
	close_btn.custom_minimum_size = Vector2(32, 32)
	close_btn.pressed.connect(func() -> void: visible = false; closed.emit())
	header_row.add_child(close_btn)

	vbox.add_child(_rule())

	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vbox.add_child(scroll)

	var content := VBoxContainer.new()
	content.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	content.add_theme_constant_override("separation", 14)
	scroll.add_child(content)

	# Gallery games section — surfaces inset playable games whose
	# unlock flags have fired. COMMUNITY PLANNED appears once the
	# reader finishes Summer's Start (Planned Community part 1).
	# Spec: lore/_COMMUNITY_PLANNED_SPEC.md §Unlock condition.
	var cp_unlocked: bool = SaveSystem.is_unlocked("community_planned:reader_finished_summers_start")
	if cp_unlocked:
		content.add_child(_section_label("GALLERY GAMES"))
		var games_flow := HFlowContainer.new()
		games_flow.add_theme_constant_override("h_separation", 12)
		games_flow.add_theme_constant_override("v_separation", 12)
		games_flow.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		games_flow.add_child(_make_community_planned_tile())
		content.add_child(games_flow)
	else:
		# Dev hook: a small toggle to fire the unlock flag without
		# finishing Summer's Start. Removable once the real wire-up
		# from the novel's part-one-end exists. Hidden behind a
		# clearly-labelled dev button so it doesn't masquerade as a
		# real gallery item.
		var dev_row := HBoxContainer.new()
		dev_row.add_theme_constant_override("separation", 8)
		content.add_child(dev_row)
		var dev_btn := Button.new()
		dev_btn.text = "(dev) unlock COMMUNITY PLANNED"
		dev_btn.flat = true
		dev_btn.focus_mode = Control.FOCUS_NONE
		_apply_font(dev_btn, SkinDB.F_CINZEL, 9, Color(0.42, 0.42, 0.42, 0.85))
		dev_btn.pressed.connect(func() -> void:
			SaveSystem.mark_unlocked("community_planned:reader_finished_summers_start")
			_rebuild())
		dev_row.add_child(dev_btn)

	# Substrate (ASCII) section, grouped per-volume.
	# Items without a `volume` (e.g. Player Surfaces) go into a leading
	# "Always Available" bucket. Items with a volume show as a section per
	# volume, headed with the volume title from VOLUME_TITLES.
	if not subs.is_empty():
		content.add_child(_section_label("ASCII SUBSTRATES"))
		var groups: Dictionary = {}  # key: int volume or -1 for "no volume"
		var order: Array = []        # preserve discovery order for unkeyed
		for item_v in subs:
			if typeof(item_v) != TYPE_DICTIONARY:
				continue
			var it: Dictionary = item_v
			var vol: int = int(it.get("volume", -1))
			if not groups.has(vol):
				groups[vol] = []
				order.append(vol)
			(groups[vol] as Array).append(it)

		var ordered_vols: Array = []
		if order.has(-1):
			ordered_vols.append(-1)
		var numbered: Array = []
		for v in order:
			if v != -1:
				numbered.append(v)
		numbered.sort()
		ordered_vols.append_array(numbered)

		for vol_v in ordered_vols:
			var vol: int = int(vol_v)
			var header: String = ""
			if vol == -1:
				header = "ALWAYS AVAILABLE"
			else:
				var title: String = str(VOLUME_TITLES.get(vol, ""))
				header = "VOLUME %d" % vol if title == "" else "VOLUME %d  —  %s" % [vol, title.to_upper()]
			content.add_child(_volume_label(header))
			# Sub-group by `set` field (chapter / arcana / instruments)
			# Sort: Major Arcana first → Chapter 0/I/II/… in numeric/roman
			# order → portraits set bucket → instruments last.
			var by_set: Dictionary = {}
			var set_order: Array = []
			for it_v in groups[vol]:
				var it_d: Dictionary = it_v as Dictionary
				var sset: String = str(it_d.get("set", "—"))
				if not by_set.has(sset):
					by_set[sset] = []
					set_order.append(sset)
				(by_set[sset] as Array).append(it_d)
			set_order.sort_custom(_set_sort_compare)
			for sset in set_order:
				content.add_child(_chapter_label(str(sset)))
				var flow := FlowContainer.new()
				flow.alignment = FlowContainer.ALIGNMENT_BEGIN
				flow.add_theme_constant_override("h_separation", 10)
				flow.add_theme_constant_override("v_separation", 10)
				flow.size_flags_horizontal = Control.SIZE_EXPAND_FILL
				content.add_child(flow)
				for it_v in by_set[sset]:
					flow.add_child(_make_substrate_tile(it_v as Dictionary))

	# CG section
	content.add_child(_section_label("CG IMAGES"))
	if all_cgs.is_empty():
		var empty_lbl := Label.new()
		empty_lbl.text = "No CG images found in scene data."
		_apply_font(empty_lbl, SkinDB.F_IMFELL_R, 14, C_DIM)
		empty_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		content.add_child(empty_lbl)
	else:
		var flow := FlowContainer.new()
		flow.alignment = FlowContainer.ALIGNMENT_BEGIN
		flow.add_theme_constant_override("h_separation", 10)
		flow.add_theme_constant_override("v_separation", 10)
		flow.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		content.add_child(flow)

		for cg_src: String in all_cgs:
			var is_seen: bool = SaveSystem.is_cg_seen(cg_src)
			var tile := _make_tile(cg_src, is_seen)
			flow.add_child(tile)


func _section_label(text: String) -> Label:
	var lbl := Label.new()
	lbl.text = text
	_apply_font(lbl, SkinDB.F_CINZEL, 11, Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.85))
	return lbl


# Try multiple naming conventions to find a card thumbnail image.
# Falls back to raw image read so it works even before Godot has
# .import-ed the assets (running from un-opened source).
func _resolve_thumbnail(item_id: String) -> Texture2D:
	if item_id == "":
		return null
	var candidates: Array = []
	var arcana_base := item_id.replace("_arcana", "")
	candidates.append("res://assets/gallery/%s.png" % arcana_base)
	if item_id.begins_with("portrait_"):
		candidates.append("res://assets/gallery/%s_0.png" % item_id)
	candidates.append("res://assets/gallery/%s.png" % item_id)
	for p in candidates:
		# Try Image.load_from_file FIRST — it accepts any format
		# (auto-detects PNG/JPEG by header bytes), and crucially
		# doesn't push a red error to the Output console when the
		# file is corrupt or a JPEG mislabeled as PNG. ResourceLoader
		# is strict about format vs extension and pushes errors that
		# clutter the log without helping the user.
		var abs_path: String = ProjectSettings.globalize_path(p)
		if FileAccess.file_exists(abs_path):
			var img := Image.load_from_file(abs_path)
			if img != null:
				return ImageTexture.create_from_image(img)
		# ResourceLoader fallback for .import-cached textures (faster
		# than re-decoding from disk if Godot already imported).
		if ResourceLoader.exists(p):
			# Suppress the load-error spam by checking with
			# ResourceLoader.load_threaded_request — no, simpler:
			# just call load() and accept any error noise IF the
			# disk-direct path above already failed.
			var t := load(p)
			if t is Texture2D: return t
	return null


func _chapter_label(text: String) -> Label:
	# Sub-grouping header under a volume (chapter/arcana/instruments)
	var lbl := Label.new()
	lbl.text = "  ▸ " + text
	_apply_font(lbl, SkinDB.F_CINZEL, 9, Color(C_TXT.r, C_TXT.g, C_TXT.b, 0.65))
	return lbl


# Sort sub-groups within a volume header. Major Arcana first, then
# chapters (parse roman numerals or arabic), then portraits, then
# instruments/other. Returns true if a should appear BEFORE b.
func _set_sort_compare(a: String, b: String) -> bool:
	return _set_sort_key(a) < _set_sort_key(b)


func _set_sort_key(s: String) -> int:
	var sl := s.to_lower()
	# Major Arcana / its variants first
	if sl.contains("major arcana") and not sl.contains("playable"):
		return 0
	if sl.contains("major arcana") and sl.contains("playable"):
		return 1
	# Chapter <roman/number> — extract a number for ordering
	if sl.contains("chapter"):
		# Try arabic number first
		var n := 999
		for tok in s.split(" "):
			if tok.is_valid_int():
				n = int(tok); break
		# Roman numeral fallback
		const ROMAN := {"0":0,"i":1,"ii":2,"iii":3,"iv":4,"v":5,"vi":6,
						"vii":7,"viii":8,"ix":9,"x":10,"xi":11,"xii":12,
						"xiii":13,"xiv":14,"xv":15,"xvi":16,"xvii":17,
						"xviii":18,"xix":19,"xx":20,"xxi":21}
		if n == 999:
			for tok in s.split(" "):
				var lt := tok.to_lower().rstrip(",.:")
				if ROMAN.has(lt):
					n = ROMAN[lt]; break
		return 100 + n
	if sl.contains("portrait"):
		return 800
	if sl.contains("instrument"):
		return 900
	return 999


func _volume_label(text: String) -> Label:
	# Subordinate label under the ASCII SUBSTRATES section — dimmer + smaller.
	var lbl := Label.new()
	lbl.text = text
	_apply_font(lbl, SkinDB.F_CINZEL, 10, Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.55))
	return lbl


func _load_substrate_index() -> Array:
	if not FileAccess.file_exists(SUBSTRATE_INDEX):
		return []
	var f := FileAccess.open(SUBSTRATE_INDEX, FileAccess.READ)
	if f == null:
		return []
	var data: Variant = JSON.parse_string(f.get_as_text())
	if typeof(data) != TYPE_DICTIONARY:
		return []
	var dd: Dictionary = data
	if not dd.has("items"):
		return []
	var items_v: Variant = dd["items"]
	if typeof(items_v) != TYPE_ARRAY:
		return []
	return items_v as Array


func _make_community_planned_tile() -> Control:
	# Phosphor-green CRT tile per the spec. The 14.4k connect-tone
	# preview on hover is post-MVP audio work; today the tile is the
	# tile, and the click launches the game.
	var tile := Button.new()
	tile.custom_minimum_size = Vector2(THUMB_W * 2, THUMB_H)
	tile.clip_contents = true
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.02, 0.10, 0.04, 1.0)
	style.border_color = Color(0.32, 0.86, 0.42, 0.65)
	style.set_border_width_all(1)
	style.corner_radius_top_left = 2
	style.corner_radius_top_right = 2
	style.corner_radius_bottom_left = 2
	style.corner_radius_bottom_right = 2
	tile.add_theme_stylebox_override("normal", style)
	var hover_style: StyleBoxFlat = style.duplicate() as StyleBoxFlat
	hover_style.border_color = Color(0.42, 0.96, 0.52, 0.95)
	hover_style.bg_color = Color(0.04, 0.14, 0.06, 1.0)
	tile.add_theme_stylebox_override("hover", hover_style)
	tile.add_theme_stylebox_override("focus", hover_style)
	tile.add_theme_stylebox_override("pressed", hover_style)
	# Centered phosphor-green title.
	var vbox := VBoxContainer.new()
	vbox.anchor_right = 1.0
	vbox.anchor_bottom = 1.0
	vbox.alignment = BoxContainer.ALIGNMENT_CENTER
	tile.add_child(vbox)
	var label := Label.new()
	label.text = "COMMUNITY PLANNED"
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_apply_font(label, SkinDB.F_CINZEL, 14, Color(0.62, 0.96, 0.62, 1))
	vbox.add_child(label)
	var sub := Label.new()
	sub.text = "the summer Frasier holds"
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_apply_font(sub, SkinDB.F_CINZEL, 9, Color(0.42, 0.78, 0.42, 0.85))
	vbox.add_child(sub)
	var dial := Label.new()
	dial.text = "[ 14.4k · CONNECT ]"
	dial.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	dial.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_apply_font(dial, SkinDB.F_CINZEL, 8, Color(0.32, 0.62, 0.32, 0.65))
	vbox.add_child(dial)
	tile.pressed.connect(_launch_community_planned)
	return tile


func _launch_community_planned() -> void:
	var ps: PackedScene = load("res://scenes/games/CommunityPlannedGame.tscn") as PackedScene
	if ps == null:
		push_warning("[GalleryOverlay] Could not load CommunityPlannedGame.tscn")
		return
	var inst := ps.instantiate()
	get_tree().root.add_child(inst)
	visible = false
	closed.emit()


func _make_substrate_tile(item: Dictionary) -> Control:
	var always_unlocked: bool = bool(item.get("always_unlocked", false))
	var is_seen: bool = always_unlocked or SaveSystem.is_cg_seen("substrate:" + str(item.get("id", "")))

	var tile := Button.new()
	tile.custom_minimum_size = Vector2(THUMB_W, THUMB_H)
	tile.clip_contents = true

	var tile_style := StyleBoxFlat.new()
	tile_style.bg_color     = C_DIM if not is_seen else Color(0.04, 0.05, 0.08, 0.9)
	tile_style.border_color = C_BORDER
	tile_style.set_border_width_all(1)
	tile.add_theme_stylebox_override("normal",  tile_style)
	var hover_style: StyleBoxFlat = tile_style.duplicate() as StyleBoxFlat
	hover_style.border_color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.7)
	tile.add_theme_stylebox_override("hover",   hover_style)
	tile.add_theme_stylebox_override("focus",   hover_style)
	tile.add_theme_stylebox_override("pressed", hover_style)

	if is_seen:
		# Card thumbnail — if there's a matching gallery image for the
		# id, use it as the tile background so the gallery actually
		# shows the cards as cards rather than text labels.
		var thumb_tex: Texture2D = _resolve_thumbnail(str(item.get("id","")))
		if thumb_tex != null:
			var thumb := TextureRect.new()
			thumb.texture = thumb_tex
			thumb.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
			thumb.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
			thumb.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
			thumb.modulate = Color(1, 1, 1, 0.92)
			thumb.mouse_filter = Control.MOUSE_FILTER_IGNORE
			tile.add_child(thumb)
			# Dark scrim across the bottom so the title text remains
			# readable against bright card art
			var scrim := ColorRect.new()
			scrim.anchor_top = 0.55
			scrim.anchor_bottom = 1.0
			scrim.anchor_left = 0; scrim.anchor_right = 1
			scrim.color = Color(0, 0, 0, 0.55)
			scrim.mouse_filter = Control.MOUSE_FILTER_IGNORE
			tile.add_child(scrim)

		var v := VBoxContainer.new()
		v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		v.offset_left = 10
		v.offset_right = -10
		v.offset_top = 14
		v.offset_bottom = -10
		v.add_theme_constant_override("separation", 6)
		v.mouse_filter = Control.MOUSE_FILTER_IGNORE
		tile.add_child(v)

		# When there's a thumbnail, push the labels to the bottom so
		# they read over the dark scrim instead of covering the art
		if thumb_tex != null:
			var spacer := Control.new()
			spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
			v.add_child(spacer)

		var kind := Label.new()
		kind.text = "// %s" % str(item.get("type", "ASCII")).to_upper()
		_apply_font(kind, SkinDB.F_CINZEL, 9, Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.55))
		v.add_child(kind)

		var title := Label.new()
		title.text = str(item.get("title", item.get("id", "?")))
		_apply_font(title, SkinDB.F_CINZEL, 14, C_TXT)
		title.autowrap_mode = TextServer.AUTOWRAP_WORD
		v.add_child(title)

		var path: String = str(item.get("path", ""))
		var title_str: String = str(item.get("title", item.get("id", "")))
		var item_kind: String = str(item.get("type", "substrate"))
		tile.pressed.connect(func() -> void: _view_substrate_fullscreen(path, title_str, item_kind))
	else:
		var lock_lbl := Label.new()
		lock_lbl.text = "🔒"
		lock_lbl.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		lock_lbl.add_theme_font_size_override("font_size", 24)
		lock_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		lock_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
		tile.add_child(lock_lbl)
		tile.disabled = true

	return tile


## Spawn a dedicated visualizer over the gallery picker. Hides the
## picker's existing children while the visualizer is open so they
## can't bleed through underneath (z_index doesn't always win against
## sibling Controls inside the same Control parent). Restores them
## when the visualizer emits `closed`.
func _spawn_visualizer(script: Script) -> Control:
	# Record + hide existing children so the visualizer renders alone
	var hidden_siblings: Array = []
	for ch in get_children():
		if ch.visible:
			hidden_siblings.append(ch)
			ch.visible = false
	var v := Control.new()
	v.set_script(script)
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.z_index = 12
	v.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(v)
	v.connect("closed", func() -> void:
		for sib in hidden_siblings:
			if is_instance_valid(sib):
				sib.visible = true
		v.queue_free())
	return v


## When the arcana has a built Tarot Gauntlet scenario, overlay a
## "▷ PLAY" button on top of the visualizer that launches it. Pressing
## the button replaces the visualizer with the gauntlet scene.
const TAROT_GAUNTLET_SCENE := preload("res://scenes/games/TarotGauntletGame.tscn")

func _add_play_button_overlay(parent_visualizer: Control,
							arcana: String, location: String, hand: String) -> void:
	if parent_visualizer == null:
		return
	var btn := Button.new()
	btn.text = "▷ ENTER THE GAUNTLET"
	btn.add_theme_font_size_override("font_size", 14)
	btn.add_theme_color_override("font_color", Color(0.05, 0.05, 0.08))
	var st := StyleBoxFlat.new()
	st.bg_color = Color(0.95, 0.78, 0.40, 0.95)
	st.border_color = Color(0.40, 0.30, 0.10)
	st.set_border_width_all(2)
	st.set_corner_radius_all(4)
	st.content_margin_left = 16
	st.content_margin_right = 16
	st.content_margin_top = 8
	st.content_margin_bottom = 8
	btn.add_theme_stylebox_override("normal", st)
	btn.add_theme_stylebox_override("hover", st)
	btn.add_theme_stylebox_override("pressed", st)
	btn.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	btn.offset_left = -260
	btn.offset_top = -64
	btn.offset_right = -28
	btn.offset_bottom = -28
	btn.z_index = 20
	parent_visualizer.add_child(btn)
	btn.pressed.connect(func() -> void:
		_show_scenario_picker(parent_visualizer, arcana, location, hand))


# Scenario picker modal — three difficulty options for the Fool's
# D'Ambrosio's location. Each option launches the same engine with
# a different setup file + gravity deck.
const MAGICIAN_SCENARIOS := [
	{
		"id": "sinking_feeling",
		"title": "SINKING FEELING",
		"subtitle": "Easy · 7:14 PM · A Quiet Evening",
		"flavor": "The river is doing what rivers do. Elicia is bringing a tape. John is walking over from the diner. The steamboat on the workbench is a bare hull. Make three pieces, connect with three of the people who show up, and don't finish the steamboat unless you mean to."
	},
	{
		"id": "watch_party",
		"title": "WATCH PARTY",
		"subtitle": "Medium · 9:30 PM · Pomegranate Hour Live, Episode 47",
		"flavor": "Folding chairs out, the show streaming from the cassette deck. A few friends, a few crashers — the critic, the college acquaintance, the superfan. Art-farty, nerdy references, escalating social tension. The Demon arrives at his stool around 10:30. Make five pieces, land three connections with the harder visitors, don't broadcast the steamboat's completion live."
	},
	{
		"id": "blow_out_the_candles",
		"title": "BLOW OUT THE CANDLES",
		"subtitle": "Hard · 11:47 PM · Birthday at the End of the World · Full Moon",
		"flavor": "Maximum capacity. Every chair you own. Elicia's birthday is technically next week but tonight is the night. The demons are wide awake on a full moon. The steamboat is at 4/6 already. The cake is in the dish-station fridge. Get it to the workbench. Light the candles. Don't let the river take the bank before you do."
	}
]


const CHARIOT_SCENARIOS := [
	{
		"id": "hot_office",
		"title": "THE HOT OFFICE",
		"subtitle": "Easy · 11:14 AM · A Difficult Tuesday",
		"flavor": "A Tuesday at Ember & Ash before things get bad. The crew is on the warehouse floor. The cypress beam is up but not, in your professional opinion, straight. Jimmy is on the back stair with two coffees."
	},
	{
		"id": "two_horses_one_wreck",
		"title": "TWO HORSES, ONE WRECK",
		"subtitle": "Medium · 1:47 PM · The Day the Older Man Stood on the Corner",
		"flavor": "1:47 PM. Crew on lunch. The phone has rung four times today. From the leaded window: an older man in a charcoal suit on the corner across the street. Smoking. Watching the warehouse door."
	},
	{
		"id": "option_four",
		"title": "OPTION FOUR",
		"subtitle": "Hard · 4:18 PM · The Day the Wreck Became Visible from the Road",
		"flavor": "4:18 PM. The crew has gone home early. Jimmy is on the back stair with the option-four face. Eleven voicemails today. The sedan is back at the corner. Your thumb has been hovering above DAD."
	}
]

const LOVERS_SCENARIOS := [
	{
		"id": "the_faucet_wins",
		"title": "THE FAUCET WINS",
		"subtitle": "Easy · 8:18 AM · A Saturday Before the Knock",
		"flavor": "Saturday morning. The drip has been going since six. Philip has the wrench. You're back from the garden. The sister is on her way over. Nothing has been delivered to the porch."
	},
	{
		"id": "he_waved",
		"title": "HE WAVED",
		"subtitle": "Medium · 8:45 AM · The Polaroid",
		"flavor": "The boy at the door at 8:47 AM. The station wagon at the curb. An envelope crumpled in the way envelopes are crumpled when a person has held them too tightly. A Polaroid dated June 2009. Houston Street. Your brother walking with his back to the camera."
	},
	{
		"id": "today_the_drip_can_win",
		"title": "TODAY THE DRIP CAN WIN",
		"subtitle": "Hard · 2:14 PM · The Long Hours",
		"flavor": "Afternoon. The Polaroid has been on the table since 8:47 AM. Mrs. Theriot drove away at nine-eleven. Philip is in the back yard with the phone. Today is the day you decide whether you will weave through this."
	}
]

const HIEROPHANT_SCENARIOS := [
	{
		"id": "st_judes_morning",
		"title": "ST JUDE'S MORNING",
		"subtitle": "Easy · 10:42 AM · The Service Has Ended",
		"flavor": "After the service. The heat shimmering off the asphalt like angry ghosts. The Daigle child, seven, in a stiff Sunday dress, the hand of her father in her hand when she takes it. The long black car at the curb. Today's circuit begins."
	},
	{
		"id": "sunday_brunch",
		"title": "SUNDAY BRUNCH",
		"subtitle": "Medium · 11:47 AM · D'Ambrosio's Table 17",
		"flavor": "Gloria refills water two booths down without looking at yours. Hector at the line. The mimosas too sweet. The council men have been at the booth since 11:47. You arrive at 12:02. You like to be the last one to the table."
	},
	{
		"id": "the_bandstand_calls",
		"title": "THE BANDSTAND CALLS",
		"subtitle": "Hard · 3:18 PM · The Second Phone Call of the Hour",
		"flavor": "Three PM. The brunch is over. You are in the back of the long black car. The second phone call of the hour is the call to Antonio in New Orleans. The bandstand is across town. The crow has been watching."
	}
]

const EMPEROR_SCENARIOS := [
	{
		"id": "the_friday_helm",
		"title": "THE FRIDAY HELM",
		"subtitle": "Easy · 8:14 PM · A Normal Friday",
		"flavor": "Friday dinner. Sammy at the well. Hector at the line. Nicola at the stand. Mrs. Karras at her usual table. The bottle in the file cabinet is half-full. The brass clock from your father's office chimes the quarter."
	},
	{
		"id": "times_calling_card",
		"title": "TIME'S CALLING CARD",
		"subtitle": "Medium · 8:48 PM · The Friday Dean Came",
		"flavor": "The canonical ch4 Friday. The night Dean sat at Table 14 for two hours without ordering. The night Sammy came up the office stair three short raps. The night you decided to know."
	},
	{
		"id": "six_weeks_apart",
		"title": "SIX WEEKS APART",
		"subtitle": "Hard · Sunday Brunch · 1st Sunday of an Even Month",
		"flavor": "First Sunday of an even-numbered month. The day you call Antonio. The day Paul holds court at Table 17. The day Alberto, in Houston, decides to be the one who calls first."
	}
]

const EMPRESS_SCENARIOS := [
	{
		"id": "static_bloom",
		"title": "STATIC BLOOM",
		"subtitle": "Easy · 7:42 PM · Friday Dinner",
		"flavor": "Friday dinner. The 7 PM seatings are settling. Table 12 has the imperious wave already rehearsed. Sammy at the well. Hector at the line. You feel the third kick low and insistent during the second water round."
	},
	{
		"id": "when_youre_ready",
		"title": "WHEN YOU'RE READY",
		"subtitle": "Medium · 8:14 PM · The Friday Dean Arrived",
		"flavor": "An out-of-town suit at Table 14. Plain face. Lapels-smoothing gesture. Drinking water. Aria has spoken twice already, both times in the form of a question."
	},
	{
		"id": "the_back_room_calls",
		"title": "THE BACK ROOM CALLS",
		"subtitle": "Hard · 10:42 PM · Dante Sent You Down",
		"flavor": "Dante on the intercom from the helm: Nicola, take this envelope to the catering office. He has not, in three years, sent you to the catering office. The card room is further in. The back room is past the card room."
	}
]

const PRIESTESS_SCENARIOS := [
	{
		"id": "packing",
		"title": "PACKING",
		"subtitle": "Easy · 6:42 PM · Cardboard Boxes, Half-Filled",
		"flavor": "Late afternoon. Cardboard boxes gape along the warped hardwood floor. The mother's teacup is on the kitchen counter. The Anya footage is paused on the laptop. The cult audience has been patient. Mackenzie texts."
	},
	{
		"id": "broken_glass_fractal",
		"title": "BROKEN GLASS FRACTAL",
		"subtitle": "Medium · 8:14 PM · The Mirror Shard, the Choice",
		"flavor": "Dusk into night. You hold the mirror shard between thumb and forefinger. Your reflection fractures into a dozen Elicias, none whole. The Choose-Your-Own-Adventure episode is on the script page on the side table. Three options. The cult audience will not be patient much longer."
	},
	{
		"id": "the_comforting_void",
		"title": "THE COMFORTING VOID",
		"subtitle": "Hard · 11:42 PM · The Storage Closet Door",
		"flavor": "Late. The storage closet door is, this evening, slightly ajar. You did not, this evening, open it. You will, this evening, open it. Pomegranate Hour is in the boxes labeled in your hand from '21."
	}
]

# Cameo tiles per arcana. Each cameo loads the host arcana + host
# location, but overrides the hand to the guest's deck via
# hand_override. Cameos sit below the three core scenarios on the
# picker, separated by a divider label. Empty arrays are fine — the
# divider only renders when there's at least one cameo.
const FOOL_CAMEOS := []
const MAGICIAN_CAMEOS := [
	{
		"id": "cameo_john_at_the_warehouse",
		"hand_override": "fool",
		"difficulty": "easy",
		"title": "JOHN AT THE WAREHOUSE",
		"subtitle": "Cameo · I·Magician · 9:47 PM",
		"flavor": "John walks the river path over from the diner with a folded napkin in his pocket. The Demon is at the workbench. Elicia is filming on the loading dock. Use John's deck inside Frasier's warehouse."
	},
	{
		"id": "cameo_elicia_films_a_scene",
		"hand_override": "elicia",
		"difficulty": "medium",
		"title": "ELICIA FILMS A SCENE",
		"subtitle": "Cameo · I·Magician · 8:14 PM",
		"flavor": "Elicia rigs lights in the south bay. The Demon refuses to be on camera. Frasier won't stop welding. The warehouse becomes a location shoot for Whispers. Use Elicia's deck on Frasier's floor."
	},
	{
		"id": "cameo_antonio_comes_home",
		"hand_override": "antonio",
		"difficulty": "hard",
		"title": "ANTONIO COMES HOME",
		"subtitle": "Cameo · I·Magician · 7:48 PM",
		"flavor": "Antonio at the warehouse door two months before the wreck. The smell is the smell. The model city has an empty platform on the west edge. Use Antonio's silt-of-voicemails deck in the room that taught him ambition."
	}
]
const PRIESTESS_CAMEOS := [
	{
		"id": "cameo_mackenzie_at_the_bungalow",
		"hand_override": "mackenzie",
		"difficulty": "easy",
		"title": "MACKENZIE AT THE BUNGALOW",
		"subtitle": "Cameo · II·Priestess · 7:14 PM",
		"flavor": "Mackenzie brings a 9x13 casserole. The dying basil holds. Elicia is in the studio with the door cracked. Use the Lovers' grounded-warmth deck inside the Priestess's haunted bungalow."
	},
	{
		"id": "cameo_john_before_montreal",
		"hand_override": "john_frank",
		"difficulty": "medium",
		"title": "JOHN BEFORE MONTREAL",
		"subtitle": "Cameo · II·Priestess · 9:14 PM",
		"flavor": "John on the porch with the printed email he's been carrying for seven days. Flight to Montreal at 6:14 AM. Use the Fool's leap deck at the Priestess's threshold."
	},
	{
		"id": "cameo_frasier_fixes_the_kettle",
		"hand_override": "frasier",
		"difficulty": "hard",
		"title": "FRASIER FIXES THE KETTLE",
		"subtitle": "Cameo · II·Priestess · 11:14 PM",
		"flavor": "The back panel off the stove. The toolbox open. The kettle clicks at midnight without being on the burner. The Demon is on the phone. Use the Magician's making deck in the room that does the room thing."
	}
]
const EMPRESS_CAMEOS := [
	{
		"id": "cameo_dean_arrives",
		"hand_override": "dean",
		"difficulty": "easy",
		"title": "DEAN ARRIVES",
		"subtitle": "Cameo · III·Empress · 6:14 PM",
		"flavor": "The out-of-town gentleman walks aboard. He carries no business card, no menu request, and a small note he may, this Friday, leave under a hundred-dollar bill. New hand. Side door. Water glass left full."
	},
	{
		"id": "cameo_frasier_returns_to_the_kitchen",
		"hand_override": "frasier",
		"difficulty": "medium",
		"title": "FRASIER RETURNS TO THE KITCHEN",
		"subtitle": "Cameo · III·Empress · 6:14 PM",
		"flavor": "Frasier walks up the gangway for the first time in five years. He has, tonight, come to eat. Hector has the knife at the pass. Use Frasier's deck on the deck he left."
	},
	{
		"id": "cameo_quentin_at_table_17",
		"hand_override": "quentin_paul",
		"difficulty": "hard",
		"title": "QUENTIN AT TABLE SEVENTEEN",
		"subtitle": "Cameo · III·Empress · 7:48 PM",
		"flavor": "Paul holds court at Table 17 on a Friday Nicola is also working. The aide on his left. The envelope folded in the inside coat pocket. The bandstand payphone is, by 9:14, ringing back."
	}
]
const EMPEROR_CAMEOS := [
	{
		"id": "cameo_sammy_at_the_well",
		"hand_override": "sammy",
		"difficulty": "easy",
		"title": "SAMMY AT THE WELL",
		"subtitle": "Cameo · IV·Emperor · 8:14 PM",
		"flavor": "Sammy works the bar through Friday dinner. The well runs. The pitcher refills. The Hermit's stay-in-place patience inside the Emperor's room. New hand."
	},
	{
		"id": "cameo_antonios_friday_visit",
		"hand_override": "antonio",
		"difficulty": "medium",
		"title": "ANTONIO'S FRIDAY VISIT",
		"subtitle": "Cameo · IV·Emperor · 7:14 PM",
		"flavor": "Antonio's flight from New Orleans landed at four. He came straight to the boat. Sit with Dad at the helm. Take Mom's call from Houston. Leap from the iron stair landing."
	},
	{
		"id": "cameo_paul_at_table_17_sunday",
		"hand_override": "quentin_paul",
		"difficulty": "hard",
		"title": "PAUL AT TABLE SEVENTEEN · SUNDAY",
		"subtitle": "Cameo · IV·Emperor · 12:02 PM",
		"flavor": "The canonical Sunday brunch from Paul's POV. Mimosas too sweet. The council seated. Every doctrine point banked here costs Nicola on her next run."
	}
]
const HIEROPHANT_CAMEOS := [
	{
		"id": "cameo_dante_walks_the_same_circuit",
		"hand_override": "dante",
		"difficulty": "easy",
		"title": "DANTE WALKS THE SAME CIRCUIT",
		"subtitle": "Cameo · V·Hierophant · 2:47 PM",
		"flavor": "Dante drives Paul's Sunday route on a Tuesday. The church empty. The bandstand empty. Father Amato in the side chapel polishing the candleholders. He has known Paul for thirty years and you for thirty-five."
	},
	{
		"id": "cameo_john_at_the_bandstand",
		"hand_override": "john_frank",
		"difficulty": "medium",
		"title": "JOHN AT THE BANDSTAND",
		"subtitle": "Cameo · V·Hierophant · 3:18 PM",
		"flavor": "John walks over from the diner with his notebook. Paul at the microphone. The aide at the riser. Bypass the host. Ask the aide the question Paul's prepared answer doesn't cover."
	},
	{
		"id": "cameo_antonio_confronts_paul",
		"hand_override": "antonio",
		"difficulty": "hard",
		"title": "ANTONIO CONFRONTS PAUL",
		"subtitle": "Cameo · V·Hierophant · 12:42 PM",
		"flavor": "Antonio flew in this morning. The recording app on his phone is on. He came to say no on the record. Walk out mid-sentence with the file."
	}
]
const LOVERS_CAMEOS := [
	{
		"id": "cameo_elicia_at_the_roberts",
		"hand_override": "elicia",
		"difficulty": "easy",
		"title": "ELICIA AT THE ROBERTS",
		"subtitle": "Cameo · VI·Lovers · 4:14 PM",
		"flavor": "Elicia drives over with the Anya footage on a small tape. The Roberts' VCR died in '19. Cue the tape on the couch. Anya on Mackenzie's TV — visible only to Elicia."
	},
	{
		"id": "cameo_john_at_the_roberts",
		"hand_override": "john_frank",
		"difficulty": "medium",
		"title": "JOHN AT THE ROBERTS",
		"subtitle": "Cameo · VI·Lovers · 6:42 PM",
		"flavor": "The night before the Polaroid. John on the back porch with Philip. Leave the napkin on the kitchen counter. The Polaroid reveals at doubt five."
	},
	{
		"id": "cameo_frasier_at_the_roberts",
		"hand_override": "frasier",
		"difficulty": "hard",
		"title": "FRASIER AT THE ROBERTS",
		"subtitle": "Cameo · VI·Lovers · 10:14 AM",
		"flavor": "The day after the Polaroid. Frasier installs the mailbox post. Set / fill / level / step back. The basil in the kitchen window is dying."
	}
]
const CHARIOT_CAMEOS := [
	{
		"id": "cameo_dante_at_ember_and_ash",
		"hand_override": "dante",
		"difficulty": "easy",
		"title": "DANTE AT EMBER & ASH",
		"subtitle": "Cameo · VII·Chariot · 11:14 AM",
		"flavor": "Two months before the wreck. Dante visits Antonio's warehouse for the first time since the expansion. Look at the books. Don't say what you're thinking."
	},
	{
		"id": "cameo_frasier_at_ember_and_ash",
		"hand_override": "frasier",
		"difficulty": "medium",
		"title": "FRASIER AT EMBER & ASH",
		"subtitle": "Cameo · VII·Chariot · 2:18 PM",
		"flavor": "Frasier inspects the cypress beam Antonio asked about last week. Tell him it's fine or tell him it's not. Whichever sentence you choose writes the flag vol5 ch20 reads on the wreck day."
	},
	{
		"id": "cameo_john_at_ember_and_ash",
		"hand_override": "john_frank",
		"difficulty": "hard",
		"title": "JOHN AT EMBER & ASH",
		"subtitle": "Cameo · VII·Chariot · 4:42 PM",
		"flavor": "Antonio called at noon. John in the truck on the way to the warehouse. The host is the visitor here. Pick up the phone three times or let it ring three times. The wreck is at 7:48 regardless."
	}
]


const FOOL_SCENARIOS := [
	{
		"id": "the_leap",
		"title": "THE LEAP",
		"subtitle": "Easy · 3:47 AM · Between Acts",
		"flavor": "The off-shift. The diner is almost empty. The room presses on you because nothing else is. Assemble the bindle, gather three visitors, and walk to a threshold."
	},
	{
		"id": "lunch_rush",
		"title": "THE RUSH",
		"subtitle": "Medium · 12:18 PM · Lunch Service",
		"flavor": "Sunlit room, full booths, tickets ahead of you. Bus kid and line cook on the board to keep pace. Win by serving four orders, connecting three visitors, and reaching the parking lot."
	},
	{
		"id": "evening_service",
		"title": "FULL HOUSE",
		"subtitle": "Hard · 8:42 PM · Evening Service",
		"flavor": "Bar open. Every booth seated. The kitchen calling, the bar roaring, the jukebox skipping. Serve six orders and connect four visitors before the room takes you."
	}
]


func _show_scenario_picker(visualizer: Control, arcana: String, location: String, hand: String) -> void:
	if visualizer == null:
		return
	# Tear down any existing picker first
	var existing: Node = visualizer.get_node_or_null("scenario_picker")
	if existing != null and is_instance_valid(existing):
		existing.queue_free()
	var dim := ColorRect.new()
	dim.name = "scenario_picker"
	dim.color = Color(0, 0, 0, 0.86)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_STOP
	dim.z_index = 30
	visualizer.add_child(dim)
	var panel := PanelContainer.new()
	var ps := StyleBoxFlat.new()
	ps.bg_color = Color(0.08, 0.07, 0.05, 1.0)
	ps.border_color = C_GOLD
	ps.set_border_width_all(1)
	ps.set_corner_radius_all(3)
	ps.content_margin_left = 24
	ps.content_margin_right = 24
	ps.content_margin_top = 20
	ps.content_margin_bottom = 20
	panel.add_theme_stylebox_override("panel", ps)
	panel.set_anchors_preset(Control.PRESET_CENTER)
	panel.offset_left = -360
	panel.offset_right = 360
	panel.offset_top = -260
	panel.offset_bottom = 260
	dim.add_child(panel)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 14)
	panel.add_child(vb)
	# Header — arcana-aware
	var arcana_title: String = "ENTER THE GAUNTLET · D'AMBROSIO'S"
	var arcana_sub:   String = "John Frank · Pick a shift"
	var scenarios:    Array  = FOOL_SCENARIOS
	var cameos:       Array  = FOOL_CAMEOS
	if arcana == "magician":
		arcana_title = "ENTER THE GAUNTLET · THE CATHEDRAL"
		arcana_sub   = "Frasier Temple · Pick an evening"
		scenarios    = MAGICIAN_SCENARIOS
		cameos       = MAGICIAN_CAMEOS
	elif arcana == "priestess" or arcana == "ii_priestess":
		arcana_title = "ENTER THE GAUNTLET · ELICIA'S BOOTH"
		arcana_sub   = "Elicia Temple · Pick a session"
		scenarios    = PRIESTESS_SCENARIOS
		cameos       = PRIESTESS_CAMEOS
	elif arcana == "empress" or arcana == "iii_empress":
		arcana_title = "ENTER THE GAUNTLET · THE RIVERBOAT"
		arcana_sub   = "Nicola · Pick a meal"
		scenarios    = EMPRESS_SCENARIOS
		cameos       = EMPRESS_CAMEOS
	elif arcana == "emperor" or arcana == "iv_emperor":
		arcana_title = "ENTER THE GAUNTLET · DANTE'S OFFICE"
		arcana_sub   = "Dante · Pick a session"
		scenarios    = EMPEROR_SCENARIOS
		cameos       = EMPEROR_CAMEOS
	elif arcana == "hierophant" or arcana == "v_hierophant":
		arcana_title = "ENTER THE GAUNTLET · EMBER.ASH.REST.BBS"
		arcana_sub   = "Sysop · Pick a session"
		scenarios    = HIEROPHANT_SCENARIOS
		cameos       = HIEROPHANT_CAMEOS
	elif arcana == "lovers" or arcana == "vi_lovers":
		arcana_title = "ENTER THE GAUNTLET · THE APARTMENT"
		arcana_sub   = "Sasha & Reed · Pick a time"
		scenarios    = LOVERS_SCENARIOS
		cameos       = LOVERS_CAMEOS
	elif arcana == "chariot" or arcana == "vii_chariot":
		arcana_title = "ENTER THE GAUNTLET · THE MIDNIGHT BUS"
		arcana_sub   = "Cora · Pick a run"
		scenarios    = CHARIOT_SCENARIOS
		cameos       = CHARIOT_CAMEOS
	var title := Label.new()
	title.text = arcana_title
	title.add_theme_font_size_override("font_size", 14)
	title.add_theme_color_override("font_color", C_GOLD)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vb.add_child(title)
	var sub := Label.new()
	sub.text = arcana_sub
	sub.add_theme_font_size_override("font_size", 10)
	sub.add_theme_color_override("font_color", Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.55))
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vb.add_child(sub)
	# Build the scenarios list — base + an optional REVERSED tile
	# (unlocked once the player has won all 3 of this arcana's
	# difficulties via the *_complete achievement).
	var tiles_to_show: Array = scenarios.duplicate()
	if SaveSystem.is_unlocked("unlocked:reversed:" + arcana):
		# The REVERSED tile uses the hard scenario as its base
		# (typically index 2) and the engine applies the reversed
		# modifier on top.
		var hard_id: String = "the_leap"
		if scenarios.size() >= 3:
			hard_id = String((scenarios[scenarios.size() - 1] as Dictionary).get("id", hard_id))
		tiles_to_show.append({
			"id": hard_id,
			"reversed": true,
			"title": "REVERSED · " + arcana.to_upper(),
			"subtitle": "Unlocked · The room turned around.",
			"flavor": "The arcana reversed. Doubt starts +2. Stagnation starts +2. One less Time, one less Sanity, one less turn, one fewer claim before you lose. The room is harder to hold. Everything that was inevitable is still inevitable, just sooner."
		})
	# Cameos: tag a divider sentinel and append. The render loop
	# checks for "divider" and emits a section label instead of a
	# tile.
	if not cameos.is_empty():
		tiles_to_show.append({ "divider": "CAMEOS · OTHER PLAYERS IN THIS ROOM" })
		for c: Dictionary in cameos:
			tiles_to_show.append(c)
	# Scenario tiles
	for scn: Dictionary in tiles_to_show:
		if scn.has("divider"):
			var div := Label.new()
			div.text = String(scn["divider"])
			div.add_theme_font_size_override("font_size", 10)
			div.add_theme_color_override("font_color", Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.40))
			div.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			vb.add_child(div)
			continue
		var tile_panel := PanelContainer.new()
		var ts := StyleBoxFlat.new()
		ts.bg_color = Color(0.05, 0.045, 0.03, 1.0)
		ts.border_color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.35)
		ts.set_border_width_all(1)
		ts.set_corner_radius_all(3)
		ts.content_margin_left = 14
		ts.content_margin_right = 14
		ts.content_margin_top = 10
		ts.content_margin_bottom = 10
		tile_panel.add_theme_stylebox_override("panel", ts)
		tile_panel.mouse_filter = Control.MOUSE_FILTER_STOP
		tile_panel.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
		vb.add_child(tile_panel)
		var tile_vb := VBoxContainer.new()
		tile_vb.add_theme_constant_override("separation", 4)
		tile_panel.add_child(tile_vb)
		# Title row: difficulty chip + scenario title, side by side.
		# The chip reads the scenario's "difficulty" key, falling
		# back to parsing the leading token of the subtitle so older
		# tile definitions still light up.
		var title_row := HBoxContainer.new()
		title_row.add_theme_constant_override("separation", 8)
		tile_vb.add_child(title_row)
		var diff_str: String = _scenario_difficulty(scn)
		if diff_str != "":
			var chip := Label.new()
			chip.text = diff_str.to_upper()
			chip.add_theme_font_size_override("font_size", 9)
			chip.add_theme_color_override("font_color", Color(0.05, 0.045, 0.03, 1.0))
			var cs := StyleBoxFlat.new()
			cs.bg_color = _difficulty_color(diff_str)
			cs.set_corner_radius_all(3)
			cs.content_margin_left = 6
			cs.content_margin_right = 6
			cs.content_margin_top = 2
			cs.content_margin_bottom = 2
			chip.add_theme_stylebox_override("normal", cs)
			chip.size_flags_vertical = Control.SIZE_SHRINK_CENTER
			title_row.add_child(chip)
		var t_title := Label.new()
		t_title.text = String(scn.get("title", ""))
		t_title.add_theme_font_size_override("font_size", 15)
		t_title.add_theme_color_override("font_color", C_GOLD)
		t_title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		title_row.add_child(t_title)
		var t_sub := Label.new()
		t_sub.text = String(scn.get("subtitle", ""))
		t_sub.add_theme_font_size_override("font_size", 10)
		t_sub.add_theme_color_override("font_color", Color(C_TXT.r, C_TXT.g, C_TXT.b, 0.65))
		tile_vb.add_child(t_sub)
		var t_flavor := Label.new()
		t_flavor.text = String(scn.get("flavor", ""))
		t_flavor.add_theme_font_size_override("font_size", 11)
		t_flavor.add_theme_color_override("font_color", C_TXT)
		t_flavor.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		t_flavor.custom_minimum_size = Vector2(600, 0)
		tile_vb.add_child(t_flavor)
		var scenario_id: String = String(scn.get("id", "the_leap"))
		var is_reversed: bool = bool(scn.get("reversed", false))
		# Cameo tiles override the hand to the guest's deck while
		# keeping the host's arcana and location.
		var hand_to_use: String = String(scn.get("hand_override", hand))
		tile_panel.gui_input.connect(func(ev: InputEvent) -> void:
			if ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed and (ev as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT:
				dim.queue_free()
				_launch_gauntlet(visualizer, arcana, location, hand_to_use, scenario_id, is_reversed))
	# Back to gallery — dismiss the picker and return to the
	# arcana's visualizer behind it.
	var cancel := Button.new()
	cancel.text = "← Back to Gallery"
	cancel.add_theme_font_size_override("font_size", 11)
	cancel.custom_minimum_size = Vector2(160, 28)
	cancel.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	cancel.pressed.connect(dim.queue_free)
	vb.add_child(cancel)


# Read a scenario tile's difficulty as a normalized string
# ("easy", "medium", "hard", or "reversed"). Honors an explicit
# "difficulty" key on the dict; otherwise sniffs the leading token of
# "subtitle" so legacy tiles whose subtitle is "Easy · ..." still
# light up. Returns "" if nothing matches.
func _scenario_difficulty(scn: Dictionary) -> String:
	if bool(scn.get("reversed", false)):
		return "reversed"
	var explicit: String = String(scn.get("difficulty", "")).to_lower().strip_edges()
	if explicit in ["easy", "medium", "hard"]:
		return explicit
	var sub: String = String(scn.get("subtitle", "")).to_lower()
	if sub.begins_with("easy"):   return "easy"
	if sub.begins_with("medium"): return "medium"
	if sub.begins_with("hard"):   return "hard"
	# Cameos prefix with "CAMEO · ..."; parse the difficulty out of
	# the dict explicitly only — cameos should set "difficulty".
	return ""


func _difficulty_color(diff: String) -> Color:
	match diff:
		"easy":     return Color(0.55, 0.78, 0.45, 1.0)  # green
		"medium":   return Color(0.85, 0.70, 0.30, 1.0)  # amber
		"hard":     return Color(0.85, 0.35, 0.30, 1.0)  # red
		"reversed": return Color(0.65, 0.40, 0.85, 1.0)  # violet
		_:          return Color(0.6, 0.6, 0.6, 1.0)


func _launch_gauntlet(visualizer: Control, arcana: String, location: String, hand: String, scenario_id: String = "the_leap", reversed: bool = false) -> void:
	# Capture the visualizer's spawn script so we can re-open it
	# when the gauntlet ends. We fully queue_free the visualizer
	# instead of relying on `visible = false`: the visualizer's
	# painted canvas extends beyond the viewport and was bleeding
	# through the gauntlet's panels in some configurations.
	var visualizer_script: Script = null
	if visualizer:
		visualizer_script = visualizer.get_script() as Script
		visualizer.queue_free()
	var game := TAROT_GAUNTLET_SCENE.instantiate()
	game.start_scenario(arcana, location, hand, scenario_id, reversed)
	game.z_index = 30
	add_child(game)
	game.connect("game_ended", func(_outcome: String, _summary: Dictionary) -> void:
		game.queue_free()
		# Re-open the same visualizer the player launched from so
		# they're back where they were, not at the top-level picker.
		if visualizer_script != null:
			var v2 := _spawn_visualizer(visualizer_script)
			_add_play_button_overlay(v2, arcana, location, hand))


func _view_substrate_fullscreen(short_path: String, title: String, kind: String = "substrate") -> void:
	# Dedicated visualizer route — bespoke per-arcana experience.
	# Matches by path first (specific to a card), then by kind
	# (handles new entry types like "overlay" / "playable").
	if short_path == "fool_arcana":
		var v := _spawn_visualizer(FOOL_VISUALIZER_SCRIPT)
		_add_play_button_overlay(v, "fool", "dambrosios", "john_frank")
		return
	# Empress rebuilt around Nicola at D'Ambrosio's (vol5 ch3 canon).
	if short_path == "empress_arcana":
		var ve := _spawn_visualizer(EMPRESS_VISUALIZER_SCRIPT)
		_add_play_button_overlay(ve, "empress", "riverboat_interior", "nicola")
		return
	if short_path == "magician_arcana":
		var vm := _spawn_visualizer(MAGICIAN_VISUALIZER_SCRIPT)
		_add_play_button_overlay(vm, "magician", "cathedral", "frasier")
		return
	# Priestess rebuilt around Elicia's bungalow (vol5 ch2 canon).
	if short_path == "high_priestess_arcana":
		var vp := _spawn_visualizer(PRIESTESS_VISUALIZER_SCRIPT)
		_add_play_button_overlay(vp, "priestess", "elicia_bungalow", "elicia")
		return
	# Emperor rebuilt around Dante at the riverboat helm (vol5 ch4 canon).
	if short_path == "emperor_arcana":
		var vem := _spawn_visualizer(EMPEROR_VISUALIZER_SCRIPT)
		_add_play_button_overlay(vem, "emperor", "riverboat_interior", "dante")
		return
	# Hierophant rebuilt around Quentin Paul's Sunday circuit (vol5 ch5 canon).
	if short_path == "hierophant_arcana":
		var vh := _spawn_visualizer(HIEROPHANT_VISUALIZER_SCRIPT)
		_add_play_button_overlay(vh, "hierophant", "the_hierophant_circuit", "quentin_paul")
		return
	# Lovers rebuilt around the Roberts on cursed ground (vol5 ch6 Lovers canon).
	if short_path == "lovers_arcana":
		var vlv := _spawn_visualizer(LOVERS_VISUALIZER_SCRIPT)
		_add_play_button_overlay(vlv, "lovers", "roberts_house", "mackenzie")
		return
	# Chariot rebuilt around Antonio at Ember & Ash (vol5 ch7 Chariot canon).
	if short_path == "chariot_arcana":
		var vch := _spawn_visualizer(CHARIOT_VISUALIZER_SCRIPT)
		_add_play_button_overlay(vch, "chariot", "ember_ash_office", "antonio")
		return
	# Tarot Synth — type:"overlay" entry in the gallery index, opens
	# the playable instrument as a fullscreen overlay
	if kind == "overlay" or short_path == "TarotSynthOverlay":
		var ts := Control.new()
		ts.set_script(TAROT_SYNTH_SCRIPT)
		ts.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		ts.z_index = 12
		ts.mouse_filter = Control.MOUSE_FILTER_STOP
		add_child(ts)
		ts.connect("closed", func() -> void: ts.queue_free())
		return

	var viewer := ColorRect.new()
	viewer.color = Color(0, 0, 0, 0.96)
	viewer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	viewer.z_index = 10
	viewer.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(viewer)

	var sub := Control.new()
	if kind == "composition":
		sub.set_script(COMPOSITION_SCRIPT)
	else:
		sub.set_script(SUBSTRATE_RASTER_SCRIPT)
	sub.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	sub.mouse_filter = Control.MOUSE_FILTER_IGNORE
	viewer.add_child(sub)
	if kind == "composition":
		sub.call_deferred("load_composition", short_path)
	else:
		sub.call_deferred("load_substrate", short_path)

	# Debug overlay — composition-only. Hidden by default; toggled via DEBUG btn.
	var debug_overlay: Control = null
	if kind == "composition":
		debug_overlay = Control.new()
		debug_overlay.set_script(DEBUG_OVERLAY_SCRIPT)
		debug_overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		debug_overlay.visible = false
		debug_overlay.z_index = 20
		viewer.add_child(debug_overlay)

		var debug_btn := Button.new()
		debug_btn.text = "DEBUG"
		debug_btn.custom_minimum_size = Vector2(80, 28)
		debug_btn.set_anchors_preset(Control.PRESET_TOP_LEFT)
		debug_btn.offset_left = 16
		debug_btn.offset_top  = 16
		debug_btn.offset_right = 96
		debug_btn.offset_bottom = 44
		debug_btn.z_index = 21
		debug_btn.pressed.connect(func() -> void:
			if not debug_overlay.visible:
				debug_overlay.call("bind", sub)
				debug_overlay.visible = true
			else:
				debug_overlay.visible = false)
		viewer.add_child(debug_btn)

	# Interactive layer — adds clickable hotspots + cipher reveals +
	# per-card synth note trigger if a puzzle_hooks entry exists for
	# this asset id. Sits above the composition, below the close hint.
	# Resolves both arcana ids and portrait ids via the layer's bind().
	var card_interactive := Control.new()
	card_interactive.set_script(CARD_INTERACTIVE_SCRIPT)
	card_interactive.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	card_interactive.z_index = 15
	card_interactive.mouse_filter = Control.MOUSE_FILTER_PASS
	viewer.add_child(card_interactive)
	# Defer bind so _ready has fired and audio is initialized
	card_interactive.call_deferred("bind", short_path)

	var close_lbl := Label.new()
	close_lbl.text = "CLICK TO CLOSE — %s" % title
	close_lbl.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	close_lbl.offset_right  = -16
	close_lbl.offset_bottom = -16
	close_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	close_lbl.vertical_alignment   = VERTICAL_ALIGNMENT_BOTTOM
	_apply_font(close_lbl, SkinDB.F_CINZEL, 9, Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.5))
	close_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	viewer.add_child(close_lbl)

	viewer.gui_input.connect(func(ev: InputEvent) -> void:
		if ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed:
			viewer.queue_free()
	)


func _make_tile(src: String, is_seen: bool) -> Control:
	var tile := Button.new()
	tile.custom_minimum_size = Vector2(THUMB_W, THUMB_H)
	tile.clip_contents = true

	var tile_style := StyleBoxFlat.new()
	tile_style.bg_color     = C_DIM if not is_seen else Color(0, 0, 0, 0.2)
	tile_style.border_color = C_BORDER
	tile_style.set_border_width_all(1)
	tile.add_theme_stylebox_override("normal",  tile_style)
	var hover_style: StyleBoxFlat = tile_style.duplicate() as StyleBoxFlat
	hover_style.border_color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.7)
	tile.add_theme_stylebox_override("hover",   hover_style)
	tile.add_theme_stylebox_override("focus",   hover_style)
	tile.add_theme_stylebox_override("pressed", hover_style)

	if is_seen:
		var img_path := "res://" + src
		if ResourceLoader.exists(img_path):
			var tex := ResourceLoader.load(img_path) as Texture2D
			if tex:
				var img_rect := TextureRect.new()
				img_rect.texture      = tex
				img_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
				img_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
				img_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
				tile.add_child(img_rect)
	else:
		var lock_lbl := Label.new()
		lock_lbl.text = "🔒"
		lock_lbl.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		lock_lbl.add_theme_font_size_override("font_size", 24)
		lock_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		lock_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
		tile.add_child(lock_lbl)

	if is_seen:
		var s: String = src
		tile.pressed.connect(func() -> void: _view_fullscreen(s))
	else:
		tile.disabled = true

	return tile


func _view_fullscreen(src: String) -> void:
	var viewer := ColorRect.new()
	viewer.color = Color(0, 0, 0, 0.92)
	viewer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	viewer.z_index = 10
	add_child(viewer)

	var path := "res://" + src
	if ResourceLoader.exists(path):
		var tex := ResourceLoader.load(path) as Texture2D
		if tex:
			var img := TextureRect.new()
			img.texture      = tex
			img.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
			img.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
			img.mouse_filter = Control.MOUSE_FILTER_IGNORE
			viewer.add_child(img)

	var close_lbl := Label.new()
	close_lbl.text = "CLICK TO CLOSE"
	close_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	close_lbl.vertical_alignment   = VERTICAL_ALIGNMENT_BOTTOM
	close_lbl.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	close_lbl.offset_right  = -16
	close_lbl.offset_bottom = -16
	_apply_font(close_lbl, SkinDB.F_CINZEL, 9, Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.5))
	close_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	viewer.add_child(close_lbl)

	viewer.gui_input.connect(func(ev: InputEvent) -> void:
		if ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed:
			viewer.queue_free()
	)


func _rule() -> ColorRect:
	var r := ColorRect.new()
	r.color = C_BORDER
	r.custom_minimum_size.y = 1
	return r


func _apply_font(node: Control, path: String, size: int, col: Color) -> void:
	if ResourceLoader.exists(path):
		node.add_theme_font_override("font", load(path) as Font)
	node.add_theme_font_size_override("font_size", size)
	node.add_theme_color_override("font_color", col)
