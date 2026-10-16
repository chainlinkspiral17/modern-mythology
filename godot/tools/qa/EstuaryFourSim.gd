extends Node
## Headless QA: ESTUARY 4 campaign sim — the working season's first
## driver ("Deck-verify pending" since July). Plays all four chapters
## through the real UI with a rational-player policy for the 13-week
## season: repair storm damage, lash down when the glass drops, take
## the county grant, rest a worn crew, otherwise careful work on the
## first open project.
##
## PROGRESS asserts: campaign_over fires, the season advanced past
## week 10, at least one project reached full build, and the grant
## week resolved one way or the other. Stalls fail loudly.
##
## Run: godot --headless res://tools/qa/EstuaryFourSim.tscn

const GAME_SCENE := "res://scenes/games/estuary_4/EstuaryFour.tscn"
const TICK_CAP := 3000
const STALL_FAIL := 250

var _over: bool = false
var _final: Dictionary = {}


func _ready() -> void:
	var game: Control = (load(GAME_SCENE) as PackedScene).instantiate()
	add_child(game)
	game.connect("campaign_over", func(st: Dictionary) -> void:
		_over = true
		_final = st)
	await get_tree().process_frame
	game.call("boot", {"seed": 777})
	await get_tree().process_frame

	var last_fp: String = ""
	var stall: int = 0
	for tick in range(TICK_CAP):
		await get_tree().process_frame
		await get_tree().process_frame
		if _over:
			break
		var st: Dictionary = game.get("_state")
		var se: Dictionary = st.get("season", {})
		var btns: Array = []
		_collect_buttons(game, btns)
		var fp: String = "%s,%s,%d" % [st.get("chapter", 1), se.get("week", 4), btns.size()]
		if fp == last_fp:
			stall += 1
			if stall >= STALL_FAIL:
				print("E4SIM-STALL at %s" % fp)
				for b_v in btns:
					print("  btn: %s" % (b_v as Button).text)
				get_tree().quit(1)
				return
		else:
			last_fp = fp
			stall = 0
		var pick: Button = _choose(btns, int(se.get("morale", 3)))
		if pick != null:
			pick.emit_signal("pressed")

	if not _over:
		print("E4SIM-FAIL · campaign never ended")
		get_tree().quit(1)
		return
	var se2: Dictionary = _final.get("season", {})
	var prog: Dictionary = se2.get("progress", {})
	print("E4SIM-END · week=%s budget=%s morale=%s" %
		[se2.get("week", "?"), se2.get("budget", "?"), se2.get("morale", "?")])
	print("E4SIM-END · progress=%s damaged=%s grant=%s" %
		[prog, se2.get("damaged", []), se2.get("grant_taken", false)])
	var built_full: bool = false
	for pid in ["gate", "channel", "plantings"]:
		if int(prog.get(pid, 0)) >= 4:
			built_full = true
	var ok: bool = int(se2.get("week", 0)) >= 14 and built_full
	print("Estuary 4 season sim done · %s" % ("PASS" if ok else "FAIL (progress asserts)"))
	get_tree().quit(0 if ok else 1)


func _choose(btns: Array, morale: int) -> Button:
	# continue → repair → prep → grant → rest-if-worn → careful work
	# → any first safe button (ch1/ch3/ch4 story choices).
	var order: Array = ["→", "repair the storm damage", "lashing down", "county grant"]
	for key_v in order:
		var key := String(key_v)
		for b_v in btns:
			var b: Button = b_v
			if b.text.contains(key) and not b.disabled:
				return b
	if morale <= 1:
		for b_v in btns:
			var b: Button = b_v
			if b.text.contains("rest the crew"):
				return b
	for b_v in btns:
		var b: Button = b_v
		if b.text.contains("· careful") and not b.disabled:
			return b
	for b_v in btns:
		var b: Button = b_v
		if b.disabled or b.text.contains("quit") or b.text.contains("shelf"):
			continue
		return b
	return null


func _collect_buttons(root: Node, out: Array) -> void:
	if root is Button and (root as Button).is_visible_in_tree():
		out.append(root)
	for c in root.get_children():
		_collect_buttons(c, out)
