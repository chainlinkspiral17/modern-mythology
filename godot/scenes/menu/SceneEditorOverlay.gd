extends Control
## Scene Editor — browse volumes/scenes, view and edit nodes, playtest.
## Writes edits to user://scenes/ (checked first by SceneDataDB).
## Callback playtest_requested(scene_id, node_idx) to launch from main menu.

signal closed
signal playtest_requested(scene_id: String, node_idx: int)

const C_GOLD   := Color(0.78, 0.66, 0.29)
const C_BG     := Color(0.016, 0.012, 0.008, 0.98)
const C_PANEL  := Color(0.028, 0.022, 0.014, 0.98)
const C_BORDER := Color(0.70, 0.55, 0.24, 0.35)
const C_TXT    := Color(0.83, 0.79, 0.69)
const C_DIM    := Color(0.45, 0.43, 0.36, 0.6)
const C_SEL    := Color(0.78, 0.66, 0.29, 0.12)

const NODE_TYPES := ["narrate", "say", "think", "choice", "show", "hide",
					 "bg", "bgm", "sfx", "flag", "jump", "interlude", "cg", "end"]

var _sel_vol:      int        = -1
var _sel_scene_id: String     = ""
var _sel_node_idx: int        = -1
var _scene_data:   Dictionary = {}
var _dirty:        bool       = false

# UI refs
var _scene_list_vbox: VBoxContainer = null
var _node_list_vbox:  VBoxContainer = null
var _detail_vbox:     VBoxContainer = null
var _status_lbl:      Label         = null


func open() -> void:
	if _scene_list_vbox == null:
		_build()
	_refresh_vol_list()
	visible = true


func _build() -> void:
	var backdrop := ColorRect.new()
	backdrop.color = Color(0, 0, 0, 0.7)
	backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(backdrop)

	var root := Panel.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.offset_left   = 20
	root.offset_right  = -20
	root.offset_top    = 20
	root.offset_bottom = -20
	var st := StyleBoxFlat.new()
	st.bg_color     = C_BG
	st.border_color = C_BORDER
	st.set_border_width_all(1)
	root.add_theme_stylebox_override("panel", st)
	add_child(root)

	var top_bar := HBoxContainer.new()
	top_bar.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	top_bar.offset_left   = 12
	top_bar.offset_right  = -12
	top_bar.offset_top    = 10
	top_bar.offset_bottom = 46
	top_bar.add_theme_constant_override("separation", 12)
	root.add_child(top_bar)

	var title_lbl := Label.new()
	title_lbl.text = "SCENE EDITOR"
	_font(title_lbl, SkinDB.F_CINZEL, 13, C_GOLD)
	title_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top_bar.add_child(title_lbl)

	_status_lbl = Label.new()
	_status_lbl.text = ""
	_font(_status_lbl, SkinDB.F_CINZEL, 10, Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.5))
	_status_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top_bar.add_child(_status_lbl)

	var save_btn := Button.new()
	save_btn.text = "SAVE"
	save_btn.custom_minimum_size = Vector2(70, 30)
	save_btn.pressed.connect(_save_scene)
	top_bar.add_child(save_btn)

	var export_btn := Button.new()
	export_btn.text = "EXPORT TO PROJECT"
	export_btn.custom_minimum_size = Vector2(150, 30)
	export_btn.pressed.connect(_export_scene)
	top_bar.add_child(export_btn)

	var close_btn := Button.new()
	close_btn.text = "✕"
	close_btn.custom_minimum_size = Vector2(32, 30)
	close_btn.pressed.connect(func() -> void: visible = false; closed.emit())
	top_bar.add_child(close_btn)

	# Three-column layout
	var columns := HBoxContainer.new()
	columns.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	columns.offset_top    = 54
	columns.offset_left   = 8
	columns.offset_right  = -8
	columns.offset_bottom = -8
	columns.add_theme_constant_override("separation", 6)
	root.add_child(columns)

	# Column 1: Scene list
	var col1 := _make_column(columns, "SCENES", 260)
	var scroll1 := ScrollContainer.new()
	scroll1.size_flags_vertical = Control.SIZE_EXPAND_FILL
	col1.add_child(scroll1)
	_scene_list_vbox = VBoxContainer.new()
	_scene_list_vbox.add_theme_constant_override("separation", 3)
	_scene_list_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll1.add_child(_scene_list_vbox)

	# Column 2: Node list
	var col2 := _make_column(columns, "NODES", 280)

	# Node toolbar
	var node_toolbar := HBoxContainer.new()
	node_toolbar.add_theme_constant_override("separation", 4)
	col2.add_child(node_toolbar)
	for action: Array in [
		["▲", _move_node_up],
		["▼", _move_node_down],
		["+ ADD", _add_node],
		["✕ DEL", _delete_node],
	]:
		var btn := Button.new()
		btn.text = action[0] as String
		btn.custom_minimum_size.y = 26
		if (action[0] as String).begins_with("+") or (action[0] as String).begins_with("✕"):
			btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		btn.pressed.connect(action[1] as Callable)
		node_toolbar.add_child(btn)

	var scroll2 := ScrollContainer.new()
	scroll2.size_flags_vertical = Control.SIZE_EXPAND_FILL
	col2.add_child(scroll2)
	_node_list_vbox = VBoxContainer.new()
	_node_list_vbox.add_theme_constant_override("separation", 2)
	_node_list_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll2.add_child(_node_list_vbox)

	var play_btn := Button.new()
	play_btn.text = "▶ PLAYTEST FROM HERE"
	play_btn.custom_minimum_size.y = 32
	play_btn.pressed.connect(_playtest)
	col2.add_child(play_btn)

	# Column 3: Node detail editor
	var col3 := _make_column(columns, "NODE DETAIL", 0)
	col3.size_flags_horizontal = Control.SIZE_EXPAND_FILL

	var scroll3 := ScrollContainer.new()
	scroll3.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll3.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	col3.add_child(scroll3)

	_detail_vbox = VBoxContainer.new()
	_detail_vbox.add_theme_constant_override("separation", 8)
	_detail_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll3.add_child(_detail_vbox)


func _make_column(parent: HBoxContainer, header: String, min_w: int) -> VBoxContainer:
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 6)
	if min_w > 0:
		col.custom_minimum_size.x = min_w
	var bg := Panel.new()
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var st := StyleBoxFlat.new()
	st.bg_color     = C_PANEL
	st.border_color = C_BORDER
	st.set_border_width_all(1)
	st.content_margin_left   = 8.0
	st.content_margin_right  = 8.0
	st.content_margin_top    = 6.0
	st.content_margin_bottom = 6.0
	bg.add_theme_stylebox_override("panel", st)
	col.add_child(bg)
	var hdr := Label.new()
	hdr.text = header
	_font(hdr, SkinDB.F_CINZEL, 9, Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.6))
	hdr.custom_minimum_size.y = 20
	col.add_child(hdr)
	var rule := ColorRect.new()
	rule.color = C_BORDER
	rule.custom_minimum_size.y = 1
	col.add_child(rule)
	parent.add_child(col)
	return col


func _refresh_vol_list() -> void:
	for ch in _scene_list_vbox.get_children():
		ch.queue_free()

	var vol_meta: Array = [
		[1, "Modern Mythology"],    [2, "Small Wood Volumes"],
		[3, "Earthman Chronicles"], [4, "#/Sharp"],
		[5, "Major Arcana"],        [6, "Planned Community"],
		[7, "Land of Milk & Honey"],
	]
	for vm: Array in vol_meta:
		var vol: int    = vm[0]
		var name: String = vm[1]
		var chapters := SceneDataDB.get_volume_chapters(vol)
		if chapters.is_empty():
			continue
		var vol_btn := Button.new()
		vol_btn.text = "Vol.%d  %s  (%d)" % [vol, name, chapters.size()]
		vol_btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		vol_btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		vol_btn.custom_minimum_size.y = 28
		_style_list_btn(vol_btn, false)
		var v: int = vol
		vol_btn.pressed.connect(func() -> void: _select_vol(v))
		_scene_list_vbox.add_child(vol_btn)

		if _sel_vol == vol:
			var all_scenes := SceneDataDB.get_volume_scenes(vol)
			for scene: Dictionary in all_scenes:
				var sid: String  = scene.get("id", "")
				var stype: String = scene.get("type", "")
				var stitle: String = scene.get("title", sid)
				var s_btn := Button.new()
				s_btn.text = "  · %s  [%s]" % [stitle, stype]
				s_btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
				s_btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
				s_btn.custom_minimum_size.y = 24
				_style_list_btn(s_btn, sid == _sel_scene_id)
				var scene_id: String = sid
				s_btn.pressed.connect(func() -> void: _select_scene(scene_id))
				_scene_list_vbox.add_child(s_btn)


func _select_vol(vol: int) -> void:
	_sel_vol = vol
	_sel_scene_id = ""
	_sel_node_idx = -1
	_scene_data   = {}
	_refresh_vol_list()
	_refresh_node_list()
	_refresh_detail()


func _select_scene(scene_id: String) -> void:
	if _dirty:
		_save_scene()
	_sel_scene_id = scene_id
	_sel_node_idx = -1
	_scene_data   = SceneDataDB.get_scene(scene_id).duplicate(true)
	_dirty        = false
	_refresh_vol_list()
	_refresh_node_list()
	_refresh_detail()


func _refresh_node_list() -> void:
	for ch in _node_list_vbox.get_children():
		ch.queue_free()
	if _scene_data.is_empty():
		return
	var nodes: Array = _scene_data.get("nodes", [])
	for i in nodes.size():
		var node: Dictionary = nodes[i]
		var t: String   = node.get("t", "?")
		var preview: String = _node_preview(node)
		var btn := Button.new()
		btn.text = "%3d  [%s]  %s" % [i, t, preview]
		btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		btn.custom_minimum_size.y = 24
		_style_list_btn(btn, i == _sel_node_idx)
		btn.add_theme_font_size_override("font_size", 11)
		var idx: int = i
		btn.pressed.connect(func() -> void: _select_node(idx))
		_node_list_vbox.add_child(btn)


func _sv(n: Dictionary, key: String) -> String:
	var v = n.get(key)
	return v as String if v is String else ""


func _node_preview(node: Dictionary) -> String:
	var t: String = _sv(node, "t")
	match t:
		"narrate":
			var txt: String = _sv(node, "text")
			return txt.substr(0, 40) + ("…" if txt.length() > 40 else "")
		"say", "think":
			return "[%s] %s" % [_sv(node, "char"), _sv(node, "text").substr(0, 30)]
		"show":
			return "%s %s @%s" % [_sv(node, "char"), _sv(node, "expr"), _sv(node, "pos")]
		"bg", "bgm", "sfx", "cg":
			return _sv(node, "src")
		"jump":
			return "→ " + _sv(node, "scene")
		"flag":
			var val = node.get("val")
			return "%s = %s" % [_sv(node, "key"), str(val) if val != null else ""]
		"choice":
			var opts_raw = node.get("opts")
			var opts: Array = opts_raw as Array if opts_raw is Array else []
			return "(%d options)" % opts.size()
		_:
			return ""


func _select_node(idx: int) -> void:
	_sel_node_idx = idx
	_refresh_node_list()
	_refresh_detail()


func _refresh_detail() -> void:
	for ch in _detail_vbox.get_children():
		ch.queue_free()
	if _scene_data.is_empty() or _sel_node_idx < 0:
		return
	var nodes: Array = _scene_data.get("nodes", [])
	if _sel_node_idx >= nodes.size():
		return
	var node: Dictionary = nodes[_sel_node_idx].duplicate()

	# Node type selector
	var type_row := HBoxContainer.new()
	type_row.add_theme_constant_override("separation", 8)
	_detail_vbox.add_child(type_row)
	var type_lbl := Label.new()
	type_lbl.text = "TYPE"
	_font(type_lbl, SkinDB.F_CINZEL, 9, Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.6))
	type_lbl.custom_minimum_size.x = 60
	type_row.add_child(type_lbl)
	var type_opt := OptionButton.new()
	for nt: String in NODE_TYPES:
		type_opt.add_item(nt)
	var cur_t: String = _sv(node, "t")
	if cur_t == "":
		cur_t = "narrate"
	var t_idx := NODE_TYPES.find(cur_t)
	if t_idx >= 0:
		type_opt.selected = t_idx
	type_opt.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	type_opt.item_selected.connect(func(i: int) -> void:
		var new_t: String = NODE_TYPES[i]
		(nodes[_sel_node_idx] as Dictionary)["t"] = new_t
		_dirty = true
		_refresh_node_list()
		_refresh_detail()
	)
	type_row.add_child(type_opt)

	# Field editors based on type
	var t: String = _sv(node, "t")
	match t:
		"narrate":
			_detail_vbox.add_child(_text_field("TEXT", node, "text", nodes))
		"say", "think":
			_detail_vbox.add_child(_text_field("CHAR", node, "char", nodes))
			_detail_vbox.add_child(_text_field("EXPR", node, "expr", nodes))
			_detail_vbox.add_child(_text_area("TEXT", node, "text", nodes))
		"show":
			_detail_vbox.add_child(_text_field("CHAR", node, "char", nodes))
			_detail_vbox.add_child(_text_field("EXPR", node, "expr", nodes))
			_detail_vbox.add_child(_text_field("POS",  node, "pos",  nodes))
		"hide":
			_detail_vbox.add_child(_text_field("POS", node, "pos", nodes))
		"bg", "bgm", "sfx":
			_detail_vbox.add_child(_text_field("SRC", node, "src", nodes))
		"cg":
			_detail_vbox.add_child(_text_field("SRC",     node, "src",     nodes))
			_detail_vbox.add_child(_text_field("CAPTION", node, "caption", nodes))
		"jump":
			_detail_vbox.add_child(_text_field("SCENE", node, "scene", nodes))
		"flag":
			_detail_vbox.add_child(_text_field("KEY", node, "key", nodes))
			_detail_vbox.add_child(_text_field("VAL", node, "val", nodes))
		"interlude":
			_detail_vbox.add_child(_text_area("TEXT", node, "text", nodes))
			_detail_vbox.add_child(_text_field("SUB", node, "sub", nodes))
			_detail_vbox.add_child(_text_field("DURATION (ms)", node, "duration", nodes))
		"choice":
			_detail_vbox.add_child(_text_field("PROMPT", node, "prompt", nodes))
			var opts: Array = node.get("opts", [])
			for oi in opts.size():
				_detail_vbox.add_child(_opt_editor(opts, oi, nodes))
			var add_opt_btn := Button.new()
			add_opt_btn.text = "+ ADD OPTION"
			var o: Array = opts
			var nd: Array = nodes
			add_opt_btn.pressed.connect(func() -> void:
				o.append({"text": "New option"})
				_dirty = true
				_refresh_detail()
			)
			_detail_vbox.add_child(add_opt_btn)


func _text_field(label: String, node: Dictionary, key: String, nodes: Array) -> VBoxContainer:
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 4)
	var lbl := Label.new()
	lbl.text = label
	_font(lbl, SkinDB.F_CINZEL, 9, Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.6))
	col.add_child(lbl)
	var line := LineEdit.new()
	line.text = _sv(node, key)
	line.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_style_input(line)
	var k: String = key
	line.text_changed.connect(func(v: String) -> void:
		(nodes[_sel_node_idx] as Dictionary)[k] = v
		_dirty = true
		_status_lbl.text = "● unsaved"
		_status_lbl.add_theme_color_override("font_color", Color(0.9, 0.6, 0.3))
	)
	col.add_child(line)
	return col


func _text_area(label: String, node: Dictionary, key: String, nodes: Array) -> VBoxContainer:
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 4)
	var lbl := Label.new()
	lbl.text = label
	_font(lbl, SkinDB.F_CINZEL, 9, Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.6))
	col.add_child(lbl)
	var ta := TextEdit.new()
	ta.text = _sv(node, key)
	ta.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	ta.custom_minimum_size.y = 80
	ta.wrap_mode = TextEdit.LINE_WRAPPING_BOUNDARY
	var k: String = key
	ta.text_changed.connect(func() -> void:
		(nodes[_sel_node_idx] as Dictionary)[k] = ta.text
		_dirty = true
		_status_lbl.text = "● unsaved"
		_status_lbl.add_theme_color_override("font_color", Color(0.9, 0.6, 0.3))
	)
	col.add_child(ta)
	return col


func _opt_editor(opts: Array, oi: int, _nodes: Array) -> VBoxContainer:
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 4)
	var hdr_row := HBoxContainer.new()
	var hdr_lbl := Label.new()
	hdr_lbl.text = "OPTION %d" % (oi + 1)
	_font(hdr_lbl, SkinDB.F_CINZEL, 9, Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.5))
	hdr_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hdr_row.add_child(hdr_lbl)
	var del_btn := Button.new()
	del_btn.text = "✕"
	del_btn.custom_minimum_size = Vector2(24, 20)
	del_btn.add_theme_color_override("font_color", Color(0.8, 0.3, 0.3))
	var o: Array = opts
	var i: int = oi
	del_btn.pressed.connect(func() -> void:
		o.remove_at(i)
		_dirty = true
		_refresh_detail()
	)
	hdr_row.add_child(del_btn)
	col.add_child(hdr_row)
	for field_key: String in ["text", "scene", "goto"]:
		var opt: Dictionary = opts[oi]
		if field_key == "text" or opt.has(field_key):
			var row := HBoxContainer.new()
			row.add_theme_constant_override("separation", 6)
			var fl := Label.new()
			fl.text = field_key.to_upper()
			_font(fl, SkinDB.F_CINZEL, 8, C_DIM)
			fl.custom_minimum_size.x = 44
			row.add_child(fl)
			var le := LineEdit.new()
			le.text = _sv(opt, field_key)
			le.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			_style_input(le)
			var fk: String = field_key
			var oo: Array  = opts
			var ii: int    = oi
			le.text_changed.connect(func(v: String) -> void:
				(oo[ii] as Dictionary)[fk] = v
				_dirty = true
				_status_lbl.text = "● unsaved"
				_status_lbl.add_theme_color_override("font_color", Color(0.9, 0.6, 0.3))
			)
			row.add_child(le)
			col.add_child(row)
	return col


func _move_node_up() -> void:
	if _sel_node_idx <= 0 or _scene_data.is_empty():
		return
	var nodes: Array = _scene_data.get("nodes", [])
	var tmp: Dictionary = nodes[_sel_node_idx]
	nodes[_sel_node_idx]     = nodes[_sel_node_idx - 1]
	nodes[_sel_node_idx - 1] = tmp
	_sel_node_idx -= 1
	_dirty = true
	_refresh_node_list()


func _move_node_down() -> void:
	if _scene_data.is_empty():
		return
	var nodes: Array = _scene_data.get("nodes", [])
	if _sel_node_idx < 0 or _sel_node_idx >= nodes.size() - 1:
		return
	var tmp: Dictionary = nodes[_sel_node_idx]
	nodes[_sel_node_idx]     = nodes[_sel_node_idx + 1]
	nodes[_sel_node_idx + 1] = tmp
	_sel_node_idx += 1
	_dirty = true
	_refresh_node_list()


func _add_node() -> void:
	if _scene_data.is_empty():
		return
	var nodes: Array = _scene_data.get("nodes", [])
	var insert_at: int = _sel_node_idx + 1 if _sel_node_idx >= 0 else nodes.size()
	nodes.insert(insert_at, {"t": "narrate", "text": ""})
	_sel_node_idx = insert_at
	_dirty = true
	_refresh_node_list()
	_refresh_detail()


func _delete_node() -> void:
	if _scene_data.is_empty() or _sel_node_idx < 0:
		return
	var nodes: Array = _scene_data.get("nodes", [])
	if _sel_node_idx >= nodes.size():
		return
	nodes.remove_at(_sel_node_idx)
	_sel_node_idx = mini(_sel_node_idx, nodes.size() - 1)
	_dirty = true
	_refresh_node_list()
	_refresh_detail()


func _save_scene() -> void:
	if _scene_data.is_empty() or _sel_scene_id == "":
		return
	if SceneDataDB.save_scene_override(_sel_scene_id, _scene_data):
		_dirty = false
		_status_lbl.text = "Saved"
		_status_lbl.add_theme_color_override("font_color", Color(0.5, 0.8, 0.4))
	else:
		_status_lbl.text = "Save failed!"
		_status_lbl.add_theme_color_override("font_color", Color(0.9, 0.3, 0.3))


func _export_scene() -> void:
	if _scene_data.is_empty() or _sel_scene_id == "":
		return
	if _dirty:
		_save_scene()
	if SceneDataDB.export_scene_to_project(_sel_scene_id, _scene_data):
		_status_lbl.text = "Exported to project"
		_status_lbl.add_theme_color_override("font_color", Color(0.4, 0.7, 1.0))
	else:
		_status_lbl.text = "Export failed! (editor build only)"
		_status_lbl.add_theme_color_override("font_color", Color(0.9, 0.3, 0.3))


func _playtest() -> void:
	if _sel_scene_id == "":
		return
	var idx: int = maxi(0, _sel_node_idx)
	playtest_requested.emit(_sel_scene_id, idx)
	visible = false
	closed.emit()


func _style_list_btn(btn: Button, selected: bool) -> void:
	var st := StyleBoxFlat.new()
	st.bg_color     = C_SEL if selected else Color(0, 0, 0, 0)
	st.border_color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.5) if selected else Color(0, 0, 0, 0)
	st.set_border_width_all(1 if selected else 0)
	st.content_margin_left   = 6.0
	st.content_margin_right  = 6.0
	st.content_margin_top    = 2.0
	st.content_margin_bottom = 2.0
	btn.add_theme_stylebox_override("normal",  st)
	var hover := st.duplicate() as StyleBoxFlat
	hover.bg_color     = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.08)
	hover.border_color = C_BORDER
	hover.set_border_width_all(1)
	btn.add_theme_stylebox_override("hover",   hover)
	btn.add_theme_stylebox_override("focus",   hover)
	btn.add_theme_stylebox_override("pressed", hover)
	btn.add_theme_color_override("font_color",       C_GOLD if selected else C_TXT)
	btn.add_theme_color_override("font_hover_color", C_GOLD)
	btn.add_theme_font_size_override("font_size", 11)
	if ResourceLoader.exists(SkinDB.F_IMFELL_R):
		btn.add_theme_font_override("font", load(SkinDB.F_IMFELL_R) as Font)


func _style_input(node: Control) -> void:
	var st := StyleBoxFlat.new()
	st.bg_color     = Color(0, 0, 0, 0.4)
	st.border_color = C_BORDER
	st.set_border_width_all(1)
	st.content_margin_left   = 8.0
	st.content_margin_right  = 8.0
	st.content_margin_top    = 6.0
	st.content_margin_bottom = 6.0
	node.add_theme_stylebox_override("normal", st)
	node.add_theme_stylebox_override("focus",  st)
	node.add_theme_color_override("font_color",            C_TXT)
	node.add_theme_color_override("font_placeholder_color", C_DIM)
	node.add_theme_font_size_override("font_size", 12)
	if ResourceLoader.exists(SkinDB.F_IMFELL_R):
		node.add_theme_font_override("font", load(SkinDB.F_IMFELL_R) as Font)


func _font(node: Label, path: String, size: int, col: Color) -> void:
	if ResourceLoader.exists(path):
		node.add_theme_font_override("font", load(path) as Font)
	node.add_theme_font_size_override("font_size", size)
	node.add_theme_color_override("font_color", col)
