extends Node
## Headless QA: instantiate every slowstick HOST scene (plus the
## strategic games) for two frames each, catching runtime errors
## that only fire on _ready. Errors print to the log; the summary
## line reports per-host status.
## Run: godot --headless res://tools/qa/HostBootSweep.tscn

const HOSTS := {
	"slowstock_boot":  "res://scenes/games/estuary_3/SlowstockBoot.tscn",
	"community_planned": "res://scenes/games/CommunityPlannedGame.tscn",
	"tarot_gauntlet":  "res://scenes/games/TarotGauntletGame.tscn",
	"estuary_3_host":  "res://scenes/games/estuary_3/Estuary3Host.tscn",
	"estuary_4_host":  "res://scenes/games/estuary_4/EstuaryFourHost.tscn",
	"northwind_host":  "res://scenes/games/northwind_harbor/NorthwindHarborHost.tscn",
	"salmonberry_host": "res://scenes/games/salmonberry/SalmonberryHost.tscn",
}

func _ready() -> void:
	var failures: int = 0
	for key in HOSTS:
		var path: String = String(HOSTS[key])
		if not ResourceLoader.exists(path):
			print("HOST-MISSING %s → %s" % [key, path])
			failures += 1
			continue
		print("HOST-BOOT %s" % key)
		var ps: PackedScene = load(path)
		if ps == null:
			print("HOST-LOAD-FAIL %s" % key)
			failures += 1
			continue
		var inst: Node = ps.instantiate()
		if inst == null:
			print("HOST-INST-FAIL %s" % key)
			failures += 1
			continue
		add_child(inst)
		await get_tree().process_frame
		await get_tree().process_frame
		inst.queue_free()
		await get_tree().process_frame
		print("HOST-OK %s" % key)
	print("QA host sweep done · %d hard failure(s)" % failures)
	get_tree().quit(1 if failures > 0 else 0)
