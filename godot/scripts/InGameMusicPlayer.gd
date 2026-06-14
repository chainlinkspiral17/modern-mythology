# InGameMusicPlayer.gd · AUTOLOAD
# ════════════════════════════════════════════════════════════════
# Scans user://music/ for .ogg / .mp3 files at startup, plays them
# through the Master bus. The MoodCycler's _audio_level reads Master
# peak, so playing tracks automatically drives the visualizer with
# zero extra wiring.
#
#   user-data path on Steam Deck:
#     ~/.local/share/godot/app_userdata/Modern Mythology (Copy)/music/
#   Drop .ogg or .mp3 files in there before launching the game.
#
# Controls:
#   F7  · previous track
#   F8  · next track
#   (auto-advances on track end)
#
# Self-contained HUD label sits at the bottom-left so it doesn't
# fight the scene's existing HUD elements.
# ════════════════════════════════════════════════════════════════
extends Node

const MUSIC_DIR: String = "user://music/"

var _tracks: Array = []      # [{name: String, stream: AudioStream}, ...]
var _index: int = 0
var _player: AudioStreamPlayer
var _hud_label: Label
var _hud_layer: CanvasLayer


func _ready() -> void:
    _ensure_music_dir()
    _scan_tracks()
    _spawn_player()
    _spawn_hud()
    if not _tracks.is_empty():
        _play(_index)
    else:
        _hud_label.text = "TRACK · drop .ogg/.mp3 into %s (no tracks found)" % MUSIC_DIR
        print("[InGameMusic] no tracks in %s" % MUSIC_DIR)


func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_F7:
            _step(-1)
        elif event.keycode == KEY_F8:
            _step(1)


# ── Setup helpers ────────────────────────────────────────────────
func _ensure_music_dir() -> void:
    # DirAccess for user:// paths — Godot resolves to app data dir.
    if not DirAccess.dir_exists_absolute(MUSIC_DIR):
        DirAccess.make_dir_recursive_absolute(MUSIC_DIR)
        # Leave a stub README so the user discovers what goes here.
        var readme: FileAccess = FileAccess.open(MUSIC_DIR + "README.txt", FileAccess.WRITE)
        if readme:
            readme.store_string(
                "Drop .ogg or .mp3 files in this directory.\n" +
                "They will autoplay at startup.\n" +
                "F7 / F8 prev / next track.\n"
            )
            readme.close()


func _scan_tracks() -> void:
    var dir: DirAccess = DirAccess.open(MUSIC_DIR)
    if dir == null:
        return
    dir.list_dir_begin()
    var file_name: String = dir.get_next()
    while file_name != "":
        if not dir.current_is_dir():
            var lower: String = file_name.to_lower()
            var path: String = MUSIC_DIR + file_name
            var stream: AudioStream = null
            if lower.ends_with(".ogg") or lower.ends_with(".oga"):
                stream = AudioStreamOggVorbis.load_from_file(path)
            elif lower.ends_with(".mp3"):
                var bytes: PackedByteArray = FileAccess.get_file_as_bytes(path)
                if bytes.size() > 0:
                    var mp3: AudioStreamMP3 = AudioStreamMP3.new()
                    mp3.data = bytes
                    stream = mp3
            if stream != null:
                _tracks.append({"name": file_name, "stream": stream})
        file_name = dir.get_next()
    dir.list_dir_end()
    _tracks.sort_custom(func(a, b): return a["name"] < b["name"])
    print("[InGameMusic] found %d track(s) in %s" % [_tracks.size(), MUSIC_DIR])


func _spawn_player() -> void:
    _player = AudioStreamPlayer.new()
    _player.bus = "Master"
    _player.volume_db = 0.0
    _player.finished.connect(_on_track_finished)
    add_child(_player)


func _spawn_hud() -> void:
    _hud_layer = CanvasLayer.new()
    _hud_layer.layer = 110     # above scene HUD (which is at 100)
    add_child(_hud_layer)
    _hud_label = Label.new()
    _hud_label.offset_left = 16.0
    _hud_label.offset_top = 660.0
    _hud_label.offset_right = 1100.0
    _hud_label.offset_bottom = 700.0
    _hud_label.add_theme_font_size_override("font_size", 16)
    _hud_label.add_theme_color_override("font_color", Color(0.65, 0.92, 1.0, 1.0))
    _hud_label.add_theme_color_override("font_outline_color", Color.BLACK)
    _hud_label.add_theme_constant_override("outline_size", 3)
    _hud_layer.add_child(_hud_label)


# ── Playback control ─────────────────────────────────────────────
func _step(delta: int) -> void:
    if _tracks.is_empty():
        return
    var n: int = _tracks.size()
    _index = ((_index + delta) % n + n) % n
    _play(_index)


func _play(idx: int) -> void:
    var t: Dictionary = _tracks[idx]
    _player.stream = t["stream"]
    _player.play()
    _hud_label.text = "TRACK %d/%d · %s   [F7 prev · F8 next]" % [
        idx + 1, _tracks.size(), t["name"]
    ]
    print("[InGameMusic] ▶ %s" % t["name"])


func _on_track_finished() -> void:
    _step(1)


# Public API for other scripts / debug menu
func next_track() -> void:
    _step(1)


func prev_track() -> void:
    _step(-1)
