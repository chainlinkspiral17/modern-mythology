extends Node
# Drives the REAL scripts/vn/MusicDirector.gd (copied in by godot_director.test.js) through
# fixture scenes and prints what it decided. The node asserts on the JSON.
var out := {}

func scene(id: String, vol: int, nodes: Array) -> Dictionary:
	return {"id": id, "vol": vol, "nodes": nodes}

func _ready() -> void:
	await get_tree().process_frame
	var md := MusicDirector.new()
	add_child(md)
	await get_tree().process_frame
	# 1. inference: tense vs calm writing, then choice / interlude / cg
	var tense := scene("t_tense", 1, [
		{"t": "say", "char": "Nobody", "text": "Run! NOW! There's blood on the door!"},
		{"t": "narrate", "text": "Sirens. The knife is still in his hand. Panic."}])
	var calm := scene("t_calm", 1, [
		{"t": "narrate", "text": "Quiet rain on the window. Warm tea, slow morning."},
		{"t": "say", "char": "Nobody", "text": "Breathe. It's Sunday. We're safe…"}])
	md.begin_scene("t_tense", tense); md.on_node(0, tense.nodes[0]); md.on_node(1, tense.nodes[1])
	out["tense"] = md.state()
	md.begin_scene("t_calm", calm); md.on_node(0, calm.nodes[0]); md.on_node(1, calm.nodes[1])
	out["calm"] = md.state()
	md.on_node(2, {"t": "choice", "opts": []}); out["choice"] = md.state().target
	md.on_node(3, {"t": "interlude", "text": "Later"}); out["interlude"] = md.state().target
	md.on_node(4, {"t": "cg", "src": "x.png"}); out["cg"] = md.state().target
	# 2. authored cue sheet pins intensity; a beat moves it; {"auto": true} hands back
	var cued := scene("t_cued", 1, [
		{"t": "narrate", "text": "Blood. Run. Fire!"}, {"t": "narrate", "text": "a"}, {"t": "narrate", "text": "Quiet tea."}])
	md.begin_scene("t_cued", cued)
	out["cued_start"] = md.state()
	md.on_node(0, cued.nodes[0]); out["cued_pinned"] = md.state().target
	md.on_node(1, cued.nodes[1]); out["cued_beat"] = md.state().target
	md.on_node(2, cued.nodes[2]); out["cued_auto"] = md.state()
	# 3. leitmotif: Sharp carries the scene → his theme (on disk) starts
	var sharp := scene("t_sharp", 1, [
		{"t": "say", "char": "Sharp", "text": "Basement's open."}, {"t": "say", "char": "Sharp", "text": "Bring the amp."},
		{"t": "say", "char": "Faust", "text": "Fine."}])
	md.begin_scene("t_sharp", sharp)
	out["sharp"] = md.state()
	# 4. locale: no focal theme, no bgm → the bg's locale track (queued; plays if nothing is)
	AudioMgr.stop_bgm(); await get_tree().create_timer(1.0).timeout
	var club := scene("t_club", 1, [{"t": "bg", "src": "assets/backgrounds/vol1_club_dance.jpg"}, {"t": "narrate", "text": "Bass through the floor."}])
	md.begin_scene("t_club", club); md.on_node(0, club.nodes[0])
	out["club"] = md.state()
	await get_tree().create_timer(1.2).timeout
	out["club_playing"] = AudioMgr.get_current_track()
	# 5. silence node
	md.on_node(1, {"t": "music", "silence": true}); out["silence"] = md.state().track_reason
	# 6. smoothing reaches AudioMgr
	md.begin_scene("t_tense", tense); md.on_node(0, tense.nodes[0])
	await get_tree().create_timer(3.0).timeout
	out["sent"] = snappedf(AudioMgr.get_music_intensity(), 0.01)
	out["target_now"] = md.state().target
	# 7. replay to a node index rebuilds the target without side effects
	md.begin_scene("t_cued", cued); md.replay(2)
	out["replay"] = md.state().target
	print("RESULT " + JSON.stringify(out))
	get_tree().quit()
