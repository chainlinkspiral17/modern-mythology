extends Control
## Boot node for the slowstock library flow.
##
## A Control (not a bare Node) so the shelf/host children anchor to
## THIS node's rect — a Node parent breaks the Control anchor chain
## and children size against the whole viewport, which is how the
## shelf ended up painting over the main menu instead of staying
## inside its container.
##
## Launches SlowstockShelf; on `picked(stick_id)` swaps the shelf
## for the Estuary3Host (for estuary_3) or a placeholder-boot
## screen (for authored stubs). On host `quit_to_shelf` or
## `finished` returns to the shelf.
##
## Testable as a top-level scene · double-click SlowstockBoot.tscn
## in the Godot editor to run just the shelf → host loop without
## going through the main menu.

const SHELF_SCENE := "res://scenes/games/estuary_3/SlowstockShelf.tscn"
const HOST_SCENE  := "res://scenes/games/estuary_3/Estuary3Host.tscn"
const PIRATE_HOST_SCENE := "res://scenes/games/pirate_summer/PirateSummerHost.tscn"
const FEY_FAIRE_HOST_SCENE := "res://scenes/games/fey_faire/FeyFaireHost.tscn"
const EARTHMAN_HOST_SCENE  := "res://scenes/games/earthman_chronicles/EarthmanChroniclesHost.tscn"
const SSS_HOST_SCENE := "res://scenes/games/sams_summer_shifts/SamsSummerShiftsHost.tscn"
const E1_HOST_SCENE  := "res://scenes/games/estuary_1/Estuary1Host.tscn"
const NH_HOST_SCENE  := "res://scenes/games/northwind_harbor/NorthwindHarborHost.tscn"
const RMC_HOST_SCENE := "res://scenes/games/riffmaster_melody_club/RiffmasterClubHost.tscn"
const PMG_HOST_SCENE := "res://scenes/games/patient_mister_glass/PatientGlassHost.tscn"
const SG_HOST_SCENE  := "res://scenes/games/sweetgum/SweetgumHost.tscn"
const MW_HOST_SCENE  := "res://scenes/games/mrs_wus_garden/MrsWuHost.tscn"
const E2_HOST_SCENE  := "res://scenes/games/estuary_2/Estuary2Host.tscn"
const HNN_HOST_SCENE := "res://scenes/games/hane_no_niwa/HaneNoNiwaHost.tscn"
const SW_HOST_SCENE  := "res://scenes/games/sisters_wyrd/SistersWyrdHost.tscn"
const KSM_HOST_SCENE := "res://scenes/games/kwik_stop_manager/KwikStopManagerHost.tscn"

var _shelf: Node = null
var _host: Node = null
var _stub_screen: Node = null
var _current_stick_id: String = ""


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_open_shelf()


func _open_shelf() -> void:
	if _host != null:
		_host.queue_free()
		_host = null
	if _stub_screen != null:
		_stub_screen.queue_free()
		_stub_screen = null
	_shelf = load(SHELF_SCENE).instantiate()
	_shelf.picked.connect(_on_picked)
	_shelf.closed.connect(_on_closed)
	add_child(_shelf)


func _open_host_estuary_3(manager_mode: bool = false) -> void:
	if _shelf != null:
		_shelf.queue_free()
		_shelf = null
	_current_stick_id = "estuary_3"
	_host = load(HOST_SCENE).instantiate()
	_host.quit_to_shelf.connect(_open_shelf)
	_host.finished.connect(_on_host_finished)
	add_child(_host)
	# Fresh run for the scaffold; a later commit will surface
	# "continue" vs "new run" on the shelf itself.
	_host.call_deferred("start_new_run", manager_mode)


func _open_stub_screen(stick_id: String) -> void:
	# For authored-stub sticks (Estuary 2, Pirate Summer, Mrs Wu's
	# Garden, Kwik Stop Manager, Estuary 1), show a small "authored
	# but not yet playable" acknowledgment screen with a BACK button.
	if _shelf != null:
		_shelf.queue_free()
		_shelf = null
	_stub_screen = Control.new()
	_stub_screen.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_stub_screen.add_to_group("ui")

	var bg := ColorRect.new()
	bg.color = Color(0.024, 0.020, 0.014, 0.97)
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_stub_screen.add_child(bg)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -220
	v.offset_right = 220
	v.offset_top = -80
	v.offset_bottom = 80
	v.add_theme_constant_override("separation", 12)
	_stub_screen.add_child(v)

	var title := Label.new()
	title.text = "%s · AUTHORED · NOT YET PLAYABLE" % stick_id.to_upper().replace("_", " ")
	title.add_theme_font_size_override("font_size", 16)
	title.add_theme_color_override("font_color", Color(0.78, 0.66, 0.29, 1))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(title)

	var body := Label.new()
	body.text = "This stick is on the shelf. Its manifest is authored — cover blurb, back-of-case, prior-owner note. Playable acts are a follow-up commit.\n\nUnlock it, know it exists, come back when it's live."
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.add_theme_font_size_override("font_size", 14)
	body.add_theme_color_override("font_color", Color(0.83, 0.79, 0.69, 1))
	body.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(body)

	var back := Button.new()
	back.text = "  ← back to shelf  "
	back.pressed.connect(_open_shelf)
	v.add_child(back)

	add_child(_stub_screen)


# ─── Signals from children ───────────────────────────────────────

func _on_picked(stick_id: String, manager_mode: bool = false) -> void:
	if stick_id == "estuary_3":
		_open_host_estuary_3(manager_mode)
	elif stick_id == "pirate_summer":
		_open_host_pirate_summer(manager_mode)
	elif stick_id == "fey_faire":
		_open_host_fey_faire()
	elif stick_id == "earthman_chronicles":
		_open_host_earthman_chronicles()
	elif stick_id == "sams_summer_shifts":
		_open_host_sams_summer_shifts()
	elif stick_id == "estuary_1":
		_open_host_estuary_1()
	elif stick_id == "northwind_harbor":
		_open_host_northwind_harbor()
	elif stick_id == "riffmaster_melody_club":
		_open_host_riffmaster()
	elif stick_id == "patient_mister_glass":
		_open_host_patient_glass()
	elif stick_id == "sweetgum":
		_open_host_sweetgum()
	elif stick_id == "mrs_wus_garden":
		_open_host_mrs_wus_garden()
	elif stick_id == "estuary_2":
		_open_host_estuary_2()
	elif stick_id == "hane_no_niwa":
		_open_host_hane_no_niwa()
	elif stick_id == "sisters_wyrd":
		_open_host_sisters_wyrd()
	elif stick_id == "kwik_stop_manager":
		_open_host_kwik_stop_manager()
	elif stick_id == "basilica_of_wires":
		if OneironauticsTokens.has("basilica_cart_acquired"):
			_open_host_basilica()
		else:
			_open_basilica_absence()
	else:
		_open_stub_screen(stick_id)
	# Console boot ritual over any real host (stubs and the empty
	# sleeve set _stub_screen, not _host, so they skip it).
	if _host != null and is_instance_valid(_host):
		_play_boot_sequence(stick_id)


# ── Console boot sequence ────────────────────────────────────────
# The Slowstock is physical hardware in the fiction — booting a
# stick gets the ritual: the console's own wordmark, then the
# studio's title card (from the stick's manifest), then the game.
# Plays as an overlay ON TOP of the freshly-added host (masks the
# host's load-in), fully skippable with a click or key.
const SHELF_SCRIPT := preload("res://scenes/games/estuary_3/SlowstockShelf.gd")


func _play_boot_sequence(stick_id: String) -> void:
	# Pull title/publisher/year from the stick's manifest.
	var man: Dictionary = {}
	var mpath: String = String(SHELF_SCRIPT.FULL_MANIFESTS.get(stick_id, ""))
	if mpath != "" and FileAccess.file_exists(mpath):
		var mf := FileAccess.open(mpath, FileAccess.READ)
		if mf != null:
			var parsed: Variant = JSON.parse_string(mf.get_as_text())
			if parsed is Dictionary:
				man = parsed
	var shelf_meta: Dictionary = man.get("shelf", {})
	var title: String = String(shelf_meta.get("label_title",
		stick_id.to_upper().replace("_", " ")))
	var publisher: String = String(shelf_meta.get("publisher", ""))
	if publisher == "":
		publisher = "OLAF'S SHELF"
	var year: int = int(shelf_meta.get("release_year", 0))

	var ov := Control.new()
	ov.name = "BootSequence"
	ov.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	ov.mouse_filter = Control.MOUSE_FILTER_STOP
	ov.add_to_group("ui")
	add_child(ov)
	var bg := ColorRect.new()
	bg.color = Color(0.008, 0.009, 0.012, 1.0)
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	ov.add_child(bg)

	# Phase 1 — the console's own screen.
	var p1 := VBoxContainer.new()
	p1.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	p1.custom_minimum_size = Vector2(700, 0)
	p1.offset_left = -350
	p1.offset_right = 350
	p1.alignment = BoxContainer.ALIGNMENT_CENTER
	p1.add_theme_constant_override("separation", 10)
	ov.add_child(p1)
	var mark := Label.new()
	mark.text = "S L O W S T O C K"
	mark.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	mark.add_theme_font_size_override("font_size", 44)
	mark.add_theme_color_override("font_color", Color(0.88, 0.84, 0.74, 1))
	p1.add_child(mark)
	var sysline := Label.new()
	sysline.text = "HOME SYSTEM"
	sysline.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sysline.add_theme_font_size_override("font_size", 14)
	sysline.add_theme_color_override("font_color", Color(0.48, 0.46, 0.40, 1))
	p1.add_child(sysline)
	var reading := Label.new()
	reading.text = "reading stick · %s" % title
	reading.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	reading.add_theme_font_size_override("font_size", 13)
	reading.add_theme_color_override("font_color", Color(0.44, 0.58, 0.44, 1))
	p1.add_child(reading)

	# Phase 2 — the studio's card.
	var p2 := VBoxContainer.new()
	p2.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	p2.custom_minimum_size = Vector2(700, 0)
	p2.offset_left = -350
	p2.offset_right = 350
	p2.alignment = BoxContainer.ALIGNMENT_CENTER
	p2.add_theme_constant_override("separation", 10)
	p2.modulate.a = 0.0
	ov.add_child(p2)
	p2.modulate.a = 0.0
	var pub := Label.new()
	pub.text = publisher.to_upper()
	pub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	pub.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	pub.add_theme_font_size_override("font_size", 34)
	pub.add_theme_color_override("font_color", Color(0.92, 0.88, 0.76, 1))
	p2.add_child(pub)
	if year > 0:
		var yr := Label.new()
		yr.text = "presents  ·  %d" % year
		yr.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		yr.add_theme_font_size_override("font_size", 14)
		yr.add_theme_color_override("font_color", Color(0.50, 0.48, 0.42, 1))
		p2.add_child(yr)

	# Skip on click or key — the tween dies with the overlay.
	ov.gui_input.connect(func(ev: InputEvent) -> void:
		if (ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed) \
				or (ev is InputEventKey and (ev as InputEventKey).pressed):
			ov.queue_free())

	var bank := get_node_or_null("/root/SFXBank")
	if bank: bank.play("cartridge_click", 0.8)

	p1.modulate.a = 0.0
	var tw := ov.create_tween()
	tw.tween_property(p1, "modulate:a", 1.0, 0.30)
	tw.tween_interval(1.1)
	tw.tween_property(p1, "modulate:a", 0.0, 0.22)
	tw.tween_property(p2, "modulate:a", 1.0, 0.30)
	tw.tween_interval(1.3)
	tw.tween_property(ov, "modulate:a", 0.0, 0.35)
	tw.tween_callback(ov.queue_free)


func _open_host_pirate_summer(counselor_mode: bool = false) -> void:
	if _shelf != null:
		_shelf.queue_free()
		_shelf = null
	_current_stick_id = "pirate_summer"
	_host = load(PIRATE_HOST_SCENE).instantiate()
	_host.quit_to_shelf.connect(_open_shelf)
	_host.finished.connect(_on_host_finished)
	# Must land before add_child · _ready picks the save file by mode.
	_host.set("counselor_mode", counselor_mode)
	add_child(_host)


func _open_host_fey_faire() -> void:
	if _shelf != null:
		_shelf.queue_free()
		_shelf = null
	_current_stick_id = "fey_faire"
	_host = load(FEY_FAIRE_HOST_SCENE).instantiate()
	_host.quit_to_shelf.connect(_open_shelf)
	_host.finished.connect(_on_host_finished)
	add_child(_host)


func _open_host_sams_summer_shifts() -> void:
	if _shelf != null:
		_shelf.queue_free()
		_shelf = null
	_current_stick_id = "sams_summer_shifts"
	_host = load(SSS_HOST_SCENE).instantiate()
	_host.quit_to_shelf.connect(_open_shelf)
	_host.finished.connect(_on_host_finished)
	add_child(_host)


func _open_host_estuary_1() -> void:
	if _shelf != null:
		_shelf.queue_free()
		_shelf = null
	_current_stick_id = "estuary_1"
	_host = load(E1_HOST_SCENE).instantiate()
	_host.quit_to_shelf.connect(_open_shelf)
	_host.finished.connect(_on_host_finished)
	add_child(_host)


func _open_host_northwind_harbor() -> void:
	if _shelf != null:
		_shelf.queue_free()
		_shelf = null
	_current_stick_id = "northwind_harbor"
	_host = load(NH_HOST_SCENE).instantiate()
	_host.quit_to_shelf.connect(_open_shelf)
	_host.finished.connect(_on_host_finished)
	add_child(_host)


func _open_host_riffmaster() -> void:
	if _shelf != null:
		_shelf.queue_free()
		_shelf = null
	_current_stick_id = "riffmaster_melody_club"
	_host = load(RMC_HOST_SCENE).instantiate()
	_host.quit_to_shelf.connect(_open_shelf)
	_host.finished.connect(_on_host_finished)
	add_child(_host)


func _open_host_patient_glass() -> void:
	if _shelf != null:
		_shelf.queue_free()
		_shelf = null
	_current_stick_id = "patient_mister_glass"
	_host = load(PMG_HOST_SCENE).instantiate()
	_host.quit_to_shelf.connect(_open_shelf)
	_host.finished.connect(_on_host_finished)
	add_child(_host)


func _open_host_sweetgum() -> void:
	if _shelf != null:
		_shelf.queue_free()
		_shelf = null
	_current_stick_id = "sweetgum"
	_host = load(SG_HOST_SCENE).instantiate()
	_host.quit_to_shelf.connect(_open_shelf)
	_host.finished.connect(_on_host_finished)
	add_child(_host)


func _open_host_mrs_wus_garden() -> void:
	if _shelf != null:
		_shelf.queue_free()
		_shelf = null
	_current_stick_id = "mrs_wus_garden"
	_host = load(MW_HOST_SCENE).instantiate()
	_host.quit_to_shelf.connect(_open_shelf)
	_host.finished.connect(_on_host_finished)
	add_child(_host)


func _open_host_estuary_2() -> void:
	if _shelf != null:
		_shelf.queue_free()
		_shelf = null
	_current_stick_id = "estuary_2"
	_host = load(E2_HOST_SCENE).instantiate()
	_host.quit_to_shelf.connect(_open_shelf)
	_host.finished.connect(_on_host_finished)
	add_child(_host)


func _open_host_hane_no_niwa() -> void:
	if _shelf != null:
		_shelf.queue_free()
		_shelf = null
	_current_stick_id = "hane_no_niwa"
	_host = load(HNN_HOST_SCENE).instantiate()
	_host.quit_to_shelf.connect(_open_shelf)
	_host.finished.connect(_on_host_finished)
	add_child(_host)


const BW_HOST_SCENE := "res://scenes/games/basilica_of_wires/BasilicaHost.tscn"

func _open_host_kwik_stop_manager() -> void:
	if _shelf != null:
		_shelf.queue_free()
		_shelf = null
	_current_stick_id = "kwik_stop_manager"
	_host = load(KSM_HOST_SCENE).instantiate()
	_host.quit_to_shelf.connect(_open_shelf)
	_host.finished.connect(_on_host_finished)
	add_child(_host)


func _open_host_sisters_wyrd() -> void:
	if _shelf != null:
		_shelf.queue_free()
		_shelf = null
	_current_stick_id = "sisters_wyrd"
	_host = load(SW_HOST_SCENE).instantiate()
	_host.quit_to_shelf.connect(_open_shelf)
	_host.finished.connect(_on_host_finished)
	add_child(_host)



func _open_host_basilica() -> void:
	if _shelf != null:
		_shelf.queue_free()
		_shelf = null
	_current_stick_id = "basilica_of_wires"
	_host = load(BW_HOST_SCENE).instantiate()
	_host.quit_to_shelf.connect(_open_shelf)
	_host.finished.connect(_on_host_finished)
	add_child(_host)


func _open_basilica_absence() -> void:
	# The catalog's one hole · Olaf's hand-labeled empty sleeve.
	# In 2048 Tem finds one at auction for more than the cabin is
	# worth · whether to buy it is a Vol 7 present-day beat, and
	# it lives HERE, outside the game.
	if _shelf != null:
		_shelf.queue_free()
		_shelf = null
	_stub_screen = Control.new()
	_stub_screen.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_stub_screen.add_to_group("ui")

	var bg := ColorRect.new()
	bg.color = Color(0, 0, 0, 1)
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_stub_screen.add_child(bg)

	var hero := HeroImage.new()
	if hero.load_from("res://resources/games/vol7/basilica_of_wires/hero_images/empty_sleeve.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(640, 360))
		tex_rect.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		tex_rect.offset_left = -320
		tex_rect.offset_right = 320
		tex_rect.offset_top = -290
		tex_rect.offset_bottom = 70
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		_stub_screen.add_child(tex_rect)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -320
	v.offset_right = 320
	v.offset_top = 90
	v.offset_bottom = 330
	v.add_theme_constant_override("separation", 12)
	_stub_screen.add_child(v)

	var body := Label.new()
	body.text = "The sleeve is empty. It has been empty for thirty years. Olaf kept it where the cart would go, so the shelf would know what it was missing."
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	body.add_theme_font_size_override("font_size", 14)
	body.add_theme_color_override("font_color", Color(0.91, 0.96, 0.97))
	v.add_child(body)

	# The auction beat unlocks once Tem knows Astro-Cortex from the
	# inside · Earthman Chronicles finished.
	var em_finished := false
	var gs := get_node_or_null("/root/GauntletState")
	if gs != null:
		var st: Variant = gs.get("state")
		if st is Dictionary:
			em_finished = ((st as Dictionary).get("slowsticks_finished", []) as Array).has("earthman_chronicles")
	if em_finished:
		var auction := Label.new()
		auction.text = "· 2048 · one has surfaced at auction. It costs more than the cabin is worth."
		auction.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		auction.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		auction.add_theme_font_size_override("font_size", 13)
		auction.add_theme_color_override("font_color", Color(0.91, 0.66, 0.19))
		v.add_child(auction)

		var buy := Button.new()
		buy.text = "  · buy it anyway ·  "
		buy.add_theme_font_size_override("font_size", 14)
		buy.pressed.connect(func() -> void:
			OneironauticsTokens.add("basilica_cart_acquired")
			var bank := get_node_or_null("/root/SFXBank")
			if bank: bank.play("cartridge_click", 0.8)
			if _stub_screen != null:
				_stub_screen.queue_free()
				_stub_screen = null
			_open_host_basilica())
		v.add_child(buy)

	var back := Button.new()
	back.text = "  ← back to shelf  "
	back.add_theme_font_size_override("font_size", 13)
	back.pressed.connect(_open_shelf)
	v.add_child(back)

	add_child(_stub_screen)


func _open_host_earthman_chronicles() -> void:
	if _shelf != null:
		_shelf.queue_free()
		_shelf = null
	_current_stick_id = "earthman_chronicles"
	_host = load(EARTHMAN_HOST_SCENE).instantiate()
	_host.quit_to_shelf.connect(_open_shelf)
	_host.finished.connect(_on_host_finished)
	add_child(_host)


func _on_closed() -> void:
	# From the shelf's dim-click or Escape. If our parent is
	# something other than the SceneTree root (e.g. we're mounted
	# under MainMenu as an overlay), free ourselves so the parent
	# regains focus. Otherwise re-open the shelf · the standalone
	# SlowstockBoot flow has no other place to return to.
	if get_parent() != null and get_parent() != get_tree().root:
		queue_free()
	else:
		_open_shelf()


func _on_host_finished(canon_vars: Dictionary, lore_tokens: Array) -> void:
	# Durable cross-game store · consumed by other slowsticks
	OneironauticsTokens.add_many(lore_tokens)
	# Merge into GauntletState if it's present (the autoload might
	# not be registered in every test-scene setup).
	var gs := get_node_or_null("/root/GauntletState")
	if gs != null:
		var st: Variant = gs.get("state")
		if st is Dictionary:
			var d: Dictionary = st
			var cv: Dictionary = d.get("canon_vars", {})
			for k in canon_vars.keys():
				cv[String(k)] = canon_vars[k]
			d["canon_vars"] = cv
			var lt: Array = d.get("lore_tokens_revealed", [])
			for t in lore_tokens:
				if not lt.has(String(t)):
					lt.append(String(t))
			d["lore_tokens_revealed"] = lt
			var sf: Array = d.get("slowsticks_finished", [])
			var stick_id: String = _current_stick_id if _current_stick_id != "" else "estuary_3"
			if not sf.has(stick_id):
				sf.append(stick_id)
			d["slowsticks_finished"] = sf
			if gs.has_method("_save"):
				gs.call("_save")
	_open_shelf()

