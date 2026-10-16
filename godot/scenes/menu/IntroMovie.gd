extends Control
## IntroMovie — the temporary opening: title, credits, the opening
## movie (2026-10-01). The user: "make the temp starting title/credits/
## opening movie that goes to main menu on click or finish and also play
## on the pause/menu screen in the background. It will eventually be
## replaced by a much more involved system involving unlocked assets and
## the media player."
##
## Plays INTRO_VIDEO full screen with sound; any click, key or pad
## button (after a short grace so the launch click does not skip it), or
## the video's end, emits `finished`. No file on disk → finishes at once,
## so a checkout without the video boots straight to the menu.
##
## The video is a Theora .ogv (Godot's only native video codec), made
## from the source .mp4 by godot/tools/install_intro_video.sh. It is
## loaded from its FILE, not as an imported resource, so it plays the
## moment it lands on disk. It lives on Google Drive, not in git.

signal finished

const INTRO_VIDEO := "res://assets/video/intro/modernmythology1.ogv"
const SKIP_GRACE_S := 0.4

var _player: VideoStreamPlayer = null
var _t: float = 0.0
var _done: bool = false


## The intro's stream, or null when the file is not on this machine.
## Shared with the pause menu's background loop.
static func make_stream() -> VideoStream:
	var abs_path: String = ProjectSettings.globalize_path(INTRO_VIDEO)
	if not FileAccess.file_exists(abs_path):
		return null
	var st := VideoStreamTheora.new()
	st.file = abs_path
	return st


static func available() -> bool:
	return FileAccess.file_exists(ProjectSettings.globalize_path(INTRO_VIDEO))


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	var bg := ColorRect.new()
	bg.color = Color.BLACK
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)
	var st: VideoStream = make_stream()
	if st == null:
		_finish.call_deferred()
		return
	_player = VideoStreamPlayer.new()
	_player.stream = st
	_player.expand = true
	_player.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_player.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_player)
	_player.finished.connect(_finish)
	_player.play()
	var hint := Label.new()
	hint.text = "click or press any button to skip"
	hint.add_theme_font_size_override("font_size", 12)
	hint.add_theme_color_override("font_color", Color(1, 1, 1, 0.35))
	hint.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_RIGHT)
	hint.offset_left = -260
	hint.offset_top = -28
	hint.offset_right = -14
	hint.offset_bottom = -8
	hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	add_child(hint)


func _process(delta: float) -> void:
	_t += delta


func _input(event: InputEvent) -> void:
	if _done or _t < SKIP_GRACE_S:
		return
	var skip: bool = false
	if event is InputEventKey and (event as InputEventKey).pressed and not (event as InputEventKey).echo:
		skip = true
	elif event is InputEventMouseButton and (event as InputEventMouseButton).pressed:
		skip = true
	elif event is InputEventJoypadButton and (event as InputEventJoypadButton).pressed:
		skip = true
	if skip:
		get_viewport().set_input_as_handled()
		_finish()


func _finish() -> void:
	if _done:
		return
	_done = true
	if _player != null:
		_player.stop()
	finished.emit()
