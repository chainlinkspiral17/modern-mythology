class_name AssetBrowser
extends CanvasLayer
## In-engine asset previewer: lists the .glb/.gltf in res://assets/models/ and
## drops the chosen one straight into the live previz scene (preview in context),
## so you can place models without editing JSON. toggle() shows/hides it.

var target: Node3D            # where dropped models are parented
var spawn_pos := Vector3.ZERO
var dropped: Array = []
var _list: VBoxContainer


func _ready() -> void:
	layer = 15
	var panel := PanelContainer.new()
	panel.position = Vector2(18.0, 90.0)
	panel.custom_minimum_size = Vector2(300.0, 0.0)
	var vb := VBoxContainer.new()
	panel.add_child(vb)
	var title := Label.new()
	title.text = "ASSET BROWSER — res://assets/models"
	vb.add_child(title)
	var rescan := Button.new()
	rescan.text = "↻ rescan"
	rescan.pressed.connect(refresh)
	vb.add_child(rescan)
	var scroll := ScrollContainer.new()
	scroll.custom_minimum_size = Vector2(0.0, 320.0)
	vb.add_child(scroll)
	_list = VBoxContainer.new()
	_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(_list)
	var clear := Button.new()
	clear.text = "clear dropped"
	clear.pressed.connect(clear_dropped)
	vb.add_child(clear)
	add_child(panel)
	visible = false


func toggle() -> void:
	visible = not visible
	if visible:
		refresh()


func refresh() -> void:
	for c in _list.get_children():
		c.queue_free()
	var da := DirAccess.open("res://assets/models")
	if da == null:
		var l := Label.new()
		l.text = "(no assets/models folder)"
		_list.add_child(l)
		return
	var any := false
	da.list_dir_begin()
	var fn := da.get_next()
	while fn != "":
		if not da.current_is_dir() and fn.get_extension().to_lower() in ["glb", "gltf"]:
			any = true
			var b := Button.new()
			b.text = fn
			b.pressed.connect(_drop.bind("res://assets/models/" + fn))
			_list.add_child(b)
		fn = da.get_next()
	if not any:
		var l := Label.new()
		l.text = "(drop .glb into assets/models)"
		_list.add_child(l)


func _drop(path: String) -> void:
	if target == null or not ResourceLoader.exists(path):
		return
	var res: Resource = load(path)
	if res is PackedScene:
		var inst: Node3D = (res as PackedScene).instantiate()
		inst.position = spawn_pos
		target.add_child(inst)
		dropped.append(inst)


func clear_dropped() -> void:
	for d in dropped:
		if is_instance_valid(d):
			d.queue_free()
	dropped.clear()
