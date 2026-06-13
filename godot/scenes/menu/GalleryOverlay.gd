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
		"id": "green_phosphor",
		"title": "GREEN PHOSPHOR",
		"subtitle": "Easy · 8:42 PM · Tuesday Night",
		"flavor": "The regular caller is dialed in. The kid with questions is walking up the alley. The modems are at standby. The kettle is thinking about boiling."
	},
	{
		"id": "the_long_signal",
		"title": "THE LONG SIGNAL",
		"subtitle": "Medium · 11:14 PM · Late Wednesday",
		"flavor": "Anya is at the floppy wall. The ham band is open. The regular caller has been idle for two minutes. Sysop has THE LONG SIGNAL in his hand because tonight is the night to use it."
	},
	{
		"id": "broadcast_night",
		"title": "BROADCAST NIGHT",
		"subtitle": "Hard · 3:14 AM · Off-the-Books",
		"flavor": "3:14 AM. The BBS is between conversations. The ham voice is on the band. The lurker has logged in at this hour for the third night in a row."
	}
]

const EMPEROR_SCENARIOS := [
	{
		"id": "docket",
		"title": "DOCKET",
		"subtitle": "Easy · 9:14 AM · Tuesday",
		"flavor": "Tuesday morning docket. The clerk has the cabinet open. The petitioner is in the anteroom. The bell has rung twice. Hear four matters, stamp three rulings, send people away with what they came for."
	},
	{
		"id": "first_session",
		"title": "FIRST SESSION",
		"subtitle": "Medium · 7:48 AM · Monday Open",
		"flavor": "Pre-clerk Monday. Someone slept in their car waiting for you to open. The radiator is cold. The first ruling of the week is the heaviest."
	},
	{
		"id": "appeal",
		"title": "APPEAL",
		"subtitle": "Hard · 4:32 PM · The Late Afternoon",
		"flavor": "An appellate hearing on a case from six months ago. The appellant has been here for an hour already. The widow is in the anteroom. Volumes 9 and 10 of the river-code are missing. The clerk is tired."
	}
]

const EMPRESS_SCENARIOS := [
	{
		"id": "static_bloom",
		"title": "STATIC BLOOM",
		"subtitle": "Easy · 7:42 PM · Friday Dinner",
		"flavor": "Friday dinner. The first arrivals are already at the long table. The neighbor has been here since two. The upper deck is in mid-season. Feed the table; let the boat be the boat."
	},
	{
		"id": "harvest_dinner",
		"title": "HARVEST DINNER",
		"subtitle": "Medium · 6:18 PM · Late Autumn",
		"flavor": "The last full dinner of the season. Frasier comes over from the cathedral. The upper deck has one last yield in it. Make a full table with what the garden has left."
	},
	{
		"id": "ice_in_the_river",
		"title": "ICE IN THE RIVER",
		"subtitle": "Hard · 11:14 PM · Late February",
		"flavor": "The river has ice in it for the first time in a decade. A drifter is at the gangway who wasn't on the list. The river widow is in the lounge already. The radio is on in the wheelhouse without Nicola turning it on."
	}
]

const PRIESTESS_SCENARIOS := [
	{
		"id": "cicada_session",
		"title": "CICADA SESSION",
		"subtitle": "Easy · 9:18 PM · Late Summer",
		"flavor": "Three appointments tonight, all small. The returner is in the lounge already. The cicadas are doing the part of the work the room can't do. Elicia gets to be the listener instead of the engineer for a change. The reel is fresh."
	},
	{
		"id": "long_quiet",
		"title": "THE LONG QUIET",
		"subtitle": "Medium · 11:02 PM · Confessional Hour",
		"flavor": "Late session. The kind of visitor who walks in because they had nowhere else to say it. The pre-funeral son. The apologist. Elicia's ability is exactly the right shape for this hour. Don't let the reel fill before the apology lands."
	},
	{
		"id": "tape_witness",
		"title": "TAPE WITNESS",
		"subtitle": "Hard · 2:14 AM · The Truth-Teller's Hour",
		"flavor": "Off-the-books. The truth-teller is in the booth already. The cathedral is dark on the other side. Two more visitors coming. The reel is half-full of the take Elicia made before you got there. Get the truth on tape without breaking the listener."
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
	if arcana == "magician":
		arcana_title = "ENTER THE GAUNTLET · THE CATHEDRAL"
		arcana_sub   = "Frasier Temple · Pick an evening"
		scenarios    = MAGICIAN_SCENARIOS
	elif arcana == "priestess" or arcana == "ii_priestess":
		arcana_title = "ENTER THE GAUNTLET · ELICIA'S BOOTH"
		arcana_sub   = "Elicia Temple · Pick a session"
		scenarios    = PRIESTESS_SCENARIOS
	elif arcana == "empress" or arcana == "iii_empress":
		arcana_title = "ENTER THE GAUNTLET · THE RIVERBOAT"
		arcana_sub   = "Nicola · Pick a meal"
		scenarios    = EMPRESS_SCENARIOS
	elif arcana == "emperor" or arcana == "iv_emperor":
		arcana_title = "ENTER THE GAUNTLET · DANTE'S OFFICE"
		arcana_sub   = "Dante · Pick a session"
		scenarios    = EMPEROR_SCENARIOS
	elif arcana == "hierophant" or arcana == "v_hierophant":
		arcana_title = "ENTER THE GAUNTLET · EMBER.ASH.REST.BBS"
		arcana_sub   = "Sysop · Pick a session"
		scenarios    = HIEROPHANT_SCENARIOS
	elif arcana == "lovers" or arcana == "vi_lovers":
		arcana_title = "ENTER THE GAUNTLET · THE APARTMENT"
		arcana_sub   = "Sasha & Reed · Pick a time"
		scenarios    = LOVERS_SCENARIOS
	elif arcana == "chariot" or arcana == "vii_chariot":
		arcana_title = "ENTER THE GAUNTLET · THE MIDNIGHT BUS"
		arcana_sub   = "Cora · Pick a run"
		scenarios    = CHARIOT_SCENARIOS
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
	# Scenario tiles
	for scn: Dictionary in tiles_to_show:
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
		var t_title := Label.new()
		t_title.text = String(scn.get("title", ""))
		t_title.add_theme_font_size_override("font_size", 15)
		t_title.add_theme_color_override("font_color", C_GOLD)
		tile_vb.add_child(t_title)
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
		tile_panel.gui_input.connect(func(ev: InputEvent) -> void:
			if ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed and (ev as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT:
				dim.queue_free()
				_launch_gauntlet(visualizer, arcana, location, hand, scenario_id, is_reversed))
	# Back to gallery — dismiss the picker and return to the
	# arcana's visualizer behind it.
	var cancel := Button.new()
	cancel.text = "← Back to Gallery"
	cancel.add_theme_font_size_override("font_size", 11)
	cancel.custom_minimum_size = Vector2(160, 28)
	cancel.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	cancel.pressed.connect(dim.queue_free)
	vb.add_child(cancel)


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
	if short_path == "empress_arcana":
		var ve := _spawn_visualizer(EMPRESS_VISUALIZER_SCRIPT)
		_add_play_button_overlay(ve, "empress", "riverboat_interior", "nicola")
		return
	if short_path == "magician_arcana":
		var vm := _spawn_visualizer(MAGICIAN_VISUALIZER_SCRIPT)
		_add_play_button_overlay(vm, "magician", "cathedral", "frasier")
		return
	if short_path == "high_priestess_arcana":
		var vp := _spawn_visualizer(PRIESTESS_VISUALIZER_SCRIPT)
		# Priestess scenario play button removed in canon-alignment surgery
		# — Whispers from the Liminal rebuild pending. Visualizer still renders.
		return
	if short_path == "emperor_arcana":
		var vem := _spawn_visualizer(EMPEROR_VISUALIZER_SCRIPT)
		_add_play_button_overlay(vem, "emperor", "dantes_office", "dante")
		return
	# Hierophant play button removed in canon-alignment surgery — Q. Paul
	# rebuild pending. Visualizer still renders the arcana card.
	if short_path == "hierophant_arcana":
		_spawn_visualizer(HIEROPHANT_VISUALIZER_SCRIPT)
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


func _apply_font(node: Label, path: String, size: int, col: Color) -> void:
	if ResourceLoader.exists(path):
		node.add_theme_font_override("font", load(path) as Font)
	node.add_theme_font_size_override("font_size", size)
	node.add_theme_color_override("font_color", col)
