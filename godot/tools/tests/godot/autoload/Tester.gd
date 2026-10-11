extends Node
# Drives the REAL AudioMgr.gd (copied in by godot_audiomgr.test.js) against fixture audio:
# .wav sibling fallback, stems manifest → AudioStreamSynchronized, intensity layers, fallback to the mix,
# Ogg temps (<base>.temp.ogg + .stems/*.ogg) with the manifest's loop / loop_offset, real audio winning.
var cap: AudioEffectCapture
var out := {}
var finished := 0

func _ready() -> void:
	await get_tree().process_frame
	var bus := AudioServer.get_bus_index("BGM")
	cap = AudioEffectCapture.new()
	cap.buffer_length = 4.0
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
	# 4. Ogg temps: found after the real src and the .wav, exact length, loop from the manifest
	out["tmp_can_play"] = AudioMgr.can_play("assets/audio/bgm/tmp_loop.ogg")
	var t: AudioStream = AudioMgr._load_audio("assets/audio/bgm/tmp_loop.ogg")
	out["tmp_class"] = t.get_class() if t else "null"
	if t is AudioStreamOggVorbis:
		out["tmp_loop"] = t.loop
		out["tmp_offset_frame"] = int(t.loop_offset * 44100.0)
		out["tmp_frames"] = int(round(t.get_length() * 44100.0))
	var r: AudioStream = AudioMgr._load_audio("assets/audio/raw/rawtmp.ogg")
	out["raw_class"] = r.get_class() if r else "null"
	if r is AudioStreamOggVorbis:
		out["raw_loop"] = r.loop
		out["raw_frames"] = int(round(r.get_length() * 44100.0))
	# 5. it loops in game: capture several loop points (1.5 s file, loop 0.5 → 1.5)
	AudioMgr._bgm.finished.connect(_on_finished)
	AudioMgr.play_bgm("assets/audio/bgm/tmp_loop.ogg")
	await get_tree().create_timer(1.6).timeout
	cap.clear_buffer()
	finished = 0
	await get_tree().create_timer(3.2).timeout
	seam(cap.get_buffer(cap.get_frames_available()), 882.0)
	out["seam_finished"] = finished
	# 6. Ogg stems
	AudioMgr.play_bgm("assets/audio/bgm/oggstems.ogg")
	await get_tree().create_timer(1.5).timeout
	var st = AudioMgr._bgm.stream
	out["ostems_class"] = st.get_class() if st else "null"
	out["ostems_layers"] = AudioMgr.get_music_layers().size()
	if st is AudioStreamSynchronized:
		out["ostems_sub"] = st.get_sync_stream(0).get_class()
		out["ostems_sub_loop"] = range(st.stream_count).map(func(i): return st.get_sync_stream(i).loop)
	AudioMgr.set_music_intensity(0.0, 0.1)
	await get_tree().create_timer(0.4).timeout
	out["ostems_gains_low"] = AudioMgr.get_music_layers().map(func(l): return l.gain)
	AudioMgr.set_music_intensity(1.0, 0.1)
	# 7. real audio wins
	AudioMgr.play_bgm("assets/audio/bgm/realwin.ogg")
	await get_tree().create_timer(1.5).timeout
	var rs = AudioMgr._bgm.stream
	out["real_class"] = rs.get_class() if rs else "null"
	out["real_len"] = snappedf(rs.get_length(), 0.01) if rs else 0.0
	out["real_loop"] = rs.loop if rs is AudioStreamOggVorbis else null
	var b: AudioStream = AudioMgr._load_audio("assets/audio/bgm/both.ogg")
	out["both_class"] = b.get_class() if b else "null"
	print("RESULT " + JSON.stringify(out))
	get_tree().quit()

func _on_finished() -> void:
	finished += 1


# a looping sine through the bus: the second-order predictor residual x[n] - 2cos(w)x[n-1] + x[n-2] is ~0 for a
# clean sine and jumps at a restart, a gap or a seam
func seam(fr: PackedVector2Array, freq: float) -> void:
	var c2 := 2.0 * cos(2.0 * PI * freq / AudioServer.get_mix_rate())
	var worst := 0.0
	var quiet := 0
	var sum := 0.0
	for i in range(2, fr.size()):
		var e := absf(fr[i].x - c2 * fr[i - 1].x + fr[i - 2].x)
		worst = maxf(worst, e)
		sum += e
		if absf(fr[i].x) < 0.0005 and absf(fr[i - 1].x) < 0.0005 and absf(fr[i - 2].x) < 0.0005:
			quiet += 1
	out["seam_frames"] = fr.size()
	out["seam_worst"] = snappedf(worst, 0.00001)
	out["seam_typical"] = snappedf(sum / maxf(1.0, fr.size() - 2.0), 0.000001)
	out["seam_quiet"] = quiet


func measure() -> float:
	cap.clear_buffer()
	await get_tree().create_timer(0.6).timeout
	var fr := cap.get_buffer(cap.get_frames_available())
	var s := 0.0
	for v in fr:
		s += v.x * v.x + v.y * v.y
	return snappedf(sqrt(s / maxf(1.0, 2.0 * fr.size())), 0.0001)
