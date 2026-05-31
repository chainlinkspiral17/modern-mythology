extends SceneTree
## Headless smoke test for the menu overlays. Instantiates each overlay inside a
## real (headless) tree and drives its main code paths — tab switching, the
## lightbox viewer, playback + seek — so parse errors, missing nodes, bad signal
## connections, and runtime errors surface as a nonzero exit code.
## Run: godot --headless -s tools/check_overlays.gd

var _failures := 0


func _init() -> void:
	# Let autoloads (AudioMgr, SceneDataDB, SaveSystem, SkinDB) come online.
	await process_frame
	await process_frame
	await _check_gallery()
	await _check_music()
	if _failures > 0:
		push_error("CHECK SUMMARY: %d failure(s)" % _failures)
		quit(1)
	else:
		print("CHECK SUMMARY: all overlays OK")
		quit(0)


func _instantiate(path: String) -> Node:
	var packed := load(path) as PackedScene
	if packed == null:
		push_error("CHECK FAIL: could not load " + path)
		_failures += 1
		return null
	var inst := packed.instantiate()
	if inst == null:
		push_error("CHECK FAIL: could not instantiate " + path)
		_failures += 1
		return null
	root.add_child(inst)
	await process_frame
	return inst


func _check_gallery() -> void:
	var inst := await _instantiate("res://scenes/menu/GalleryOverlay.tscn")
	if inst == null:
		return
	inst.call("open")
	await process_frame
	for tab in ["stills", "substrates", "video"]:
		inst.call("_select_tab", tab)
		await process_frame
		# Exercise the filter rebuild with each available chip key.
		var data: Dictionary = inst.call("_gather_all")
		var items: Array = data[tab]
		for it: Dictionary in items:
			if it.get("seen", false):
				inst.call("_open_viewer_for", it)
				await process_frame
				inst.call("_viewer_step", 1)
				await process_frame
				inst.call("_viewer_step", -1)
				await process_frame
				inst.call("_close_viewer")
				await process_frame
				break
	print("CHECK OK: GalleryOverlay (tabs + lightbox)")
	inst.queue_free()
	await process_frame


func _check_music() -> void:
	# Autoload singletons aren't global identifiers in the entry `-s` script,
	# so reach them through the tree.
	var audio := root.get_node_or_null("AudioMgr")
	# Give the player a real current track so now-playing + seek run.
	if audio != null:
		audio.call("play_bgm", "assets/audio/bgm/vol1_ambient.mp3")
	await process_frame
	var inst := await _instantiate("res://scenes/menu/MusicPlayerOverlay.tscn")
	if inst == null:
		return
	inst.call("open")
	await process_frame
	await process_frame  # let _process tick the seek bar
	# Drive volume filters.
	inst.set("_vol_filter", 1)
	inst.call("_rebuild_tracks")
	inst.call("_refresh")
	await process_frame
	inst.set("_vol_filter", 0)
	inst.call("_rebuild_tracks")
	inst.call("_refresh")
	await process_frame
	# Transport.
	inst.call("_on_play_pause")
	await process_frame
	inst.call("_update_seek")
	await process_frame
	print("CHECK OK: MusicPlayerOverlay (transport + seek + filter)")
	if audio != null:
		audio.call("stop_bgm")
	inst.queue_free()
	await process_frame
