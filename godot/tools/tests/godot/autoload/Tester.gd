extends Node
# Drives the REAL AudioMgr.gd (copied in by godot_audiomgr.test.js) against fixture audio:
# .wav sibling fallback, stems manifest → AudioStreamSynchronized, intensity layers, fallback to the mix.
var cap: AudioEffectCapture
var out := {}

func _ready() -> void:
	await get_tree().process_frame
	var bus := AudioServer.get_bus_index("BGM")
	cap = AudioEffectCapture.new()
	AudioServer.add_bus_effect(bus, cap)
	# 1. a catalog .ogg path with only a .wav beside it
	var s: AudioStream = AudioMgr._load_audio("assets/audio/bgm/plain.ogg")
	out["wav_fallback"] = s.get_class() if s else "null"
	# 2. stems
	AudioMgr.play_bgm("assets/audio/bgm/layered.ogg")
	await get_tree().create_timer(1.0).timeout
	out["stream"] = AudioMgr._bgm.stream.get_class()
	out["layers"] = AudioMgr.get_music_layers().size()
	out["length"] = snappedf(AudioMgr.get_stream_length(), 0.1)
	out["rms_full"] = await measure()
	AudioMgr.set_music_intensity(0.0, 0.1)
	await get_tree().create_timer(0.4).timeout
	out["rms_low"] = await measure()
	out["gains_low"] = AudioMgr.get_music_layers().map(func(l): return l.gain)
	AudioMgr.set_music_intensity(1.0, 0.1)
	await get_tree().create_timer(0.4).timeout
	out["rms_back"] = await measure()
	# 3. a manifest naming a missing stem plays the mix instead
	AudioMgr.play_bgm("assets/audio/bgm/broken.ogg")
	await get_tree().create_timer(1.5).timeout
	out["broken_stream"] = AudioMgr._bgm.stream.get_class() if AudioMgr._bgm.stream else "null"
	print("RESULT " + JSON.stringify(out))
	get_tree().quit()

func measure() -> float:
	cap.clear_buffer()
	await get_tree().create_timer(0.6).timeout
	var fr := cap.get_buffer(cap.get_frames_available())
	var s := 0.0
	for v in fr:
		s += v.x * v.x + v.y * v.y
	return snappedf(sqrt(s / maxf(1.0, 2.0 * fr.size())), 0.0001)
