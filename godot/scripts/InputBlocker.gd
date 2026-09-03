extends Control
class_name InputBlocker
## Modal input fence. Used as the container for full-screen
## overlays (the cabin TV) so nothing underneath can be driven
## while the overlay is open:
##
##  · Children (the overlay's own UI) get first chance at every
##    event — within a subtree, unhandled input visits children
##    before the parent — and whatever they leave unconsumed is
##    swallowed HERE instead of reaching the menu / VN below.
##  · Joins the "vn_input_blocker" group; handlers that listen at
##    _input level (which fires before ANY gui or unhandled
##    routing — GameEngine's advance key does) check the group
##    and stand down while a fence exists.
##  · Releases GUI focus on entry so a previously-focused menu
##    button can't keep receiving Enter/arrow presses directly.


func _ready() -> void:
	add_to_group("vn_input_blocker")
	if get_viewport() != null:
		get_viewport().gui_release_focus()


func _unhandled_input(event: InputEvent) -> void:
	# Joypad events are NOT swallowed (2026-09-03): GamepadMgr is an
	# autoload, and autoloads receive unhandled input LAST (Godot walks
	# the group from the deepest node back to the root's first child).
	# This fence sits under every slowstick, so it ate B/X/Y/LB/RB
	# before the pad layer could translate them into ESC/E/J/Tab/I —
	# on the Deck, Pirate Summer's day modal (B to begin) could never
	# be dismissed and Sam never moved. The pad layer synthesizes the
	# KEY event, which comes back through here as a key and IS fenced
	# from the menu underneath, so nothing leaks.
	if event is InputEventJoypadButton or event is InputEventJoypadMotion:
		return
	get_viewport().set_input_as_handled()


func _unhandled_key_input(_event: InputEvent) -> void:
	get_viewport().set_input_as_handled()
