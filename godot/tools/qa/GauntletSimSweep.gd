extends Node
## Headless QA: PLAY Tarot Gauntlet scenarios with a pass-only
## player — call _on_advance() through every phase until the game
## ends (win, loss, or max_turns) or the turn cap trips. Exercises
## setup load, all five phases, shadow/drift/upkeep logic, loss
## triggers, and the finale path on multiple boards, including the
## remapped ones (ember_ash_office, roberts_house).
## Run: godot --headless res://tools/qa/GauntletSimSweep.tscn

const RUNS := [
	{"arcana": "fool", "location": "dambrosios", "hand": "john_frank", "id": "the_leap"},
	{"arcana": "vii_chariot", "location": "ember_ash_office", "hand": "antonio", "id": "two_horses_one_wreck"},
	{"arcana": "vi_lovers", "location": "roberts_house", "hand": "mackenzie", "id": "the_faucet_wins"},
]

func _ready() -> void:
	var failures: int = 0
	for run in RUNS:
		var tag: String = "%s/%s" % [String(run["arcana"]), String(run["id"])]
		print("GSIM-START %s" % tag)
		var ps: PackedScene = load("res://scenes/games/TarotGauntletGame.tscn")
		var g: Node = ps.instantiate()
		g.call("start_scenario", String(run["arcana"]), String(run["location"]),
				String(run["hand"]), String(run["id"]), false, {})
		var ended: Array = [false, "", 0]
		g.connect("game_ended", func(outcome: String, _s: Dictionary) -> void:
			ended[0] = true
			ended[1] = outcome)
		add_child(g)
		for f in range(6):
			await get_tree().process_frame
		var advances: int = 0
		while not ended[0] and advances < 400:
			if bool(g.get("_game_over")):
				break
			g.call("_on_advance")
			advances += 1
			await get_tree().process_frame
			if advances % 25 == 0:
				await get_tree().process_frame
		var turn: int = int(g.get("_turn"))
		if ended[0]:
			print("GSIM-END %s · outcome=%s · turn=%d · advances=%d" % [tag, String(ended[1]), turn, advances])
		elif bool(g.get("_game_over")):
			print("GSIM-END %s · game_over (no signal) · turn=%d · advances=%d" % [tag, turn, advances])
		else:
			print("GSIM-NO-END %s · still running after %d advances (turn %d) — no loss condition fires on a pass-only player?" % [tag, advances, turn])
			failures += 1
		g.queue_free()
		for f in range(3):
			await get_tree().process_frame
	print("QA gauntlet sim done · %d failure(s)" % failures)
	get_tree().quit(1 if failures > 0 else 0)
