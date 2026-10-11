extends Control
## VN TYPE SPECIMEN (2026-10-11): screenshot the real DialogueBox and
## ChoiceMenu over a locale render, per skin, so a typography pass can be
## reviewed as contact sheets instead of guessed at.
##
##   xvfb-run -a -s "-screen 0 1280x720x24" godot --path . \
##     --rendering-driver opengl3 res://tools/VNTypeSpecimen.tscn -- \
##     --skin suburban --bg /abs/render.png --out /abs/out.png [--choice] \
##     [--speaker Sam] [--text "..."]
##
## Keep this a tool: it reads nothing the game does not (SkinDB skins, the
## two scenes), writes one PNG and quits.

const DLG_SCENE := "res://scenes/game/DialogueBox.tscn"
const CH_SCENE  := "res://scenes/game/ChoiceMenu.tscn"

const DEFAULT_TEXT := "The cul-de-sac had the look of a place that had been promised something. Sam counted the mailboxes twice on the walk back from the Kwik Stop, the paper bag of her break going soft against her hip, and the number came out different both times — which was either the heat or the kind of thing that happened on Meadowlark Circle now."


func _parse_args() -> Dictionary:
	var out: Dictionary = {}
	var args: PackedStringArray = OS.get_cmdline_user_args()
	var i: int = 0
	while i < args.size():
		var a: String = args[i]
		if a.begins_with("--"):
			var key: String = a.substr(2)
			if i + 1 < args.size() and not args[i + 1].begins_with("--"):
				out[key] = args[i + 1]
				i += 2
				continue
			out[key] = "1"
		i += 1
	return out


func _ready() -> void:
	var args: Dictionary = _parse_args()
	var skin_name: String = String(args.get("skin", "literary"))
	var bg_path: String = String(args.get("bg", ""))
	var out_path: String = String(args.get("out", "/tmp/vn_specimen.png"))
	var speaker: String = String(args.get("speaker", "Sam"))
	var text: String = String(args.get("text", DEFAULT_TEXT))
	var want_choice: bool = args.has("choice")

	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var bg := TextureRect.new()
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	bg.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	if bg_path != "" and FileAccess.file_exists(bg_path):
		var img: Image = Image.load_from_file(bg_path)
		bg.texture = ImageTexture.create_from_image(img)
	else:
		var solid := ColorRect.new()
		solid.color = Color(0.18, 0.16, 0.14)
		solid.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		add_child(solid)
	add_child(bg)
	# As the engine does: the trip runs on the background texture only and
	# the global screen layer steps aside, so the type stays sharp.
	add_to_group("trip_local")
	var trip: Node = get_node_or_null("/root/TripSync")
	if trip != null and trip.has_method("attach") and bg.texture != null:
		trip.call("attach", bg)

	var skin: Dictionary = SkinDB.skins.get(skin_name, SkinDB.skins["literary"])
	var dlg: Control = (load(DLG_SCENE) as PackedScene).instantiate() as Control
	add_child(dlg)
	dlg.call("setup", skin)
	if speaker == "-":
		dlg.call("show_narrate", text)
	else:
		dlg.call("show_say", speaker, text)
	dlg.call("finish_typing")

	if want_choice:
		dlg.visible = false     # the engine hides the box while a choice is up
		var ch: Control = (load(CH_SCENE) as PackedScene).instantiate() as Control
		ch.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		add_child(ch)
		ch.call("setup", skin)
		ch.call("present", "What does Sam do with the second count?",
			[{"text": "Walk it again, slower, and write the number on the bag."},
			 {"text": "Let it go. The heat makes liars of mailboxes.", "skill": "PATIENCE"},
			 {"text": "Ask Maya whether Meadowlark has always had eleven.", "check": {"skill": "RAPPORT", "diff": 7}}],
			Callable())

	for _i in 6:
		await get_tree().process_frame
	var shot: Image = get_viewport().get_texture().get_image()
	shot.save_png(out_path)
	print("specimen: ", out_path)
	get_tree().quit()
