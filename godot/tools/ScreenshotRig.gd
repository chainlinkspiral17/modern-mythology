extends Node
## Screenshot rig · captures every slowstick scene in action.
##
## Run on a machine with a display (the Steam Deck):
##
##   cd /home/deck/Downloads/modern-mythology/godot
##   godot --path . res://tools/ScreenshotRig.tscn
##
## Cycles through each scene, boots it with a representative
## mid-run state, waits a few frames for layout + HeroImages, grabs
## the viewport, and saves PNGs to user://screenshots/ (shown in
## the console as an absolute path at the end).  Quits when done.

const SHOTS := [
	# [label, scene path, boot payload or null (hosts boot themselves)]
	["ff_title",        "res://scenes/games/fey_faire/FeyFaireHost.tscn", null],
	["ff_midway",       "res://scenes/games/fey_faire/FeyFaireMidway.tscn",
		{"night": 3, "gold": 8, "recruited_feys": ["ondine", "boggart"], "shows_attended": [1, 2], "questionnaire": {"player_name": "Robin"}}],
	["ff_negotiation",  "res://scenes/games/fey_faire/FeyFaireNegotiation.tscn",
		{"fey_id": "titania", "run_state": {"night": 4, "unlocked_quotes": ["midsummer_shadows"], "questionnaire": {"player_name": "Robin"}}}],
	["ff_combat",       "res://scenes/games/fey_faire/FeyFaireCombat.tscn",
		{"fey_id": "erlking", "run_state": {"night": 4, "unlocked_quotes": ["macbeth_thumbs"], "questionnaire": {"player_name": "Robin"}}}],
	["ff_trailer",      "res://scenes/games/fey_faire/FeyFaireTrailer.tscn",
		{"night": 3, "recruited_feys": ["ondine", "puck", "moth"], "keepsakes": ["playbill_midsummer"],
		 "promises": [{"fey_id": "ondine", "promise": "PROMISE to visit a beach within the next year", "fulfilled": false}],
		 "questionnaire": {"player_name": "Robin", "bedroom_description": "a bed under a map of tides", "favorite_song": "one I hum wrong on purpose"}}],
	["ff_fortune",      "res://scenes/games/fey_faire/FeyFaireFortune.tscn",
		{"run_state": {"questionnaire": {"player_name": "Robin", "favorite_song": "one I hum wrong on purpose", "lost_person_name": "Andrew"}}}],
	["ff_big_top",      "res://scenes/games/fey_faire/FeyFaireBigTop.tscn", {"night": 4}],
	["em_title",        "res://scenes/games/earthman_chronicles/EarthmanChroniclesHost.tscn", null],
	["em_ch2",          "res://scenes/games/earthman_chronicles/EarthmanChapter2Approach.tscn",
		{"chapter": 2, "class_focus": "synthesis", "party_members": ["jack"]}],
	["em_ch4",          "res://scenes/games/earthman_chronicles/EarthmanChapter4Mines.tscn",
		{"chapter": 4, "shenin": 36, "party_members": ["jack", "hel_velli", "sara_nai"]}],
	["em_combat",       "res://scenes/games/earthman_chronicles/EarthmanCombat.tscn",
		{"boss_id": "nalat", "run_state": {"hp_max": 100, "workings_completed": ["star_ruby", "bornless_one", "hymn_of_pan"], "party_members": ["jack", "hel_velli", "sara_nai", "rocha"]}}],
	["em_talikan",      "res://scenes/games/earthman_chronicles/EarthmanTalikanHub.tscn",
		{"chapter": 4, "shenin": 36, "party_members": ["jack", "hel_velli", "sara_nai", "rocha"], "rocha_recruited": true, "workings_completed": ["star_ruby"], "corrections_found": ["correction_oto_contract"]}],
	["em_codex",        "res://scenes/games/earthman_chronicles/EarthmanCodex.tscn",
		{"chapter": 5, "workings_completed": ["star_ruby", "bornless_one"], "corrections_found": ["correction_oto_contract", "correction_rochas_signature"], "party_members": ["jack", "hel_velli", "sara_nai", "rocha"], "rocha_recruited": true}],
	["sss_title",       "res://scenes/games/sams_summer_shifts/SamsSummerShiftsHost.tscn", null],
	["sss_week6",       "res://scenes/games/sams_summer_shifts/SummerLoop.tscn",
		{"week": 6, "till": 5, "regulars": 5, "nerve": 4, "choices_log": [], "endings_seen": []}],
	["ps_camp",         "res://scenes/games/pirate_summer/PirateSummerHost.tscn", null],
]

var _idx := 0
var _current: Node = null


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute("user://screenshots")
	_next()


func _next() -> void:
	if _current != null and is_instance_valid(_current):
		_current.queue_free()
		_current = null
	if _idx >= SHOTS.size():
		print("=== screenshots saved to: ", ProjectSettings.globalize_path("user://screenshots"))
		get_tree().quit()
		return
	var shot: Array = SHOTS[_idx]
	var label: String = String(shot[0])
	print("capturing ", label, " ...")
	_current = load(String(shot[1])).instantiate()
	add_child(_current)
	if shot[2] != null and _current.has_method("boot"):
		_current.call("boot", shot[2])
	# Give layout, HeroImages, and first paints time to settle.
	for i in range(12):
		await get_tree().process_frame
	var img: Image = get_viewport().get_texture().get_image()
	img.save_png("user://screenshots/" + label + ".png")
	_idx += 1
	_next()
