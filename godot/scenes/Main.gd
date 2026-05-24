extends Control
## Root scene — menu ↔ game transitions, save/load routing.

const MENU_SCENE   := preload("res://scenes/menu/MainMenu.tscn")
const ENGINE_SCENE := preload("res://scenes/game/GameEngine.tscn")

var _menu:   Control = null
var _engine: Control = null


func _ready() -> void:
	_open_menu()


func _open_menu() -> void:
	_clear_engine()
	if _menu == null:
		_menu = MENU_SCENE.instantiate()
		_menu.connect("play_requested",  _on_play_requested)
		_menu.connect("load_requested",  _on_load_requested)
		add_child(_menu)
	_menu.visible = true


func _on_play_requested(vol: int, scene_id: String, start_node: int) -> void:
	_menu.visible = false
	_start_game(vol, scene_id, -1, start_node)


func _on_load_requested(slot: int) -> void:
	var save_data := SaveSystem.read_save(slot)
	if save_data.is_empty():
		push_error("Main: empty save for slot %d" % slot)
		return
	_menu.visible = false
	_create_engine()
	_engine.call("load_save", save_data)


func _start_game(vol: int, scene_id: String, slot: int, start_node: int = 0) -> void:
	_create_engine()
	_engine.call("start", vol, scene_id, slot, start_node)


func _create_engine() -> void:
	_clear_engine()
	_engine = ENGINE_SCENE.instantiate()
	add_child(_engine)
	_engine.connect("game_ended", _on_game_ended)


func _on_game_ended() -> void:
	_clear_engine()
	_open_menu()


func _clear_engine() -> void:
	if _engine:
		_engine.queue_free()
		_engine = null
