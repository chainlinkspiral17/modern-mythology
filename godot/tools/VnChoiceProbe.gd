extends Node
## CHOICE PROBE (2026-11-10): every choice in the game laid out as the game
## lays it, and its options CLICKED. The user: "making choices in the menu
## still breaks the game." The choice column hung from mid-screen downward,
## and the hubs have 7, 10, 13 — one has 31 — options: everything past the
## bottom edge could not be seen or clicked.
##
##   godot --headless --path godot res://tools/VnChoiceProbe.tscn -- [--size 1280x720] [--only vol4_hub]
##
## For every {"t":"choice"} node (all its options, the worst case): the
## column is inside the screen, every option is inside the list's own
## window or can be scrolled into it, and the FIRST and the LAST option take
## a real mouse click. Prints the layout each long list got. Exit 1 on any ✗.

const CHOICE := preload("res://scenes/game/ChoiceMenu.tscn")
var _args: Dictionary = {}
var _bad: int = 0
var _picked: int = -1


func _ready() -> void:
	var ua: PackedStringArray = OS.get_cmdline_user_args()
	for i in ua.size():
		if ua[i].begins_with("--"):
			_args[ua[i].trim_prefix("--")] = ua[i + 1] if i + 1 < ua.size() and not ua[i + 1].begins_with("--") else ""
	_run.call_deferred()


func _flag(what: String) -> void:
	_bad += 1
	print("  ✗ %s" % what)


func _click(at: Vector2) -> void:
	for down: bool in [true, false]:
		var ev := InputEventMouseButton.new()
		ev.button_index = MOUSE_BUTTON_LEFT
		ev.pressed = down
		ev.position = at
		ev.global_position = at
		get_viewport().push_input(ev, true)
		await get_tree().process_frame


func _scene_files() -> Array:
	var out: Array = []
	var root: String = "res://resources/scenes"
	var d := DirAccess.open(root)
	if d == null:
		return out
	for sub in d.get_directories():
		var dd := DirAccess.open(root + "/" + sub)
		if dd == null:
			continue
		for f in dd.get_files():
			if f.ends_with(".json"):
				out.append(root + "/" + sub + "/" + f)
	out.sort()
	return out


func _run() -> void:
	var size_s: String = String(_args.get("size", "1280x720"))
	var wh: PackedStringArray = size_s.split("x")
	get_tree().root.size = Vector2i(int(wh[0]), int(wh[1]))
	for i in 4:
		await get_tree().process_frame
	var screen: Rect2 = Rect2(Vector2.ZERO, get_viewport().get_visible_rect().size)
	print("  canvas %s" % screen.size)
	var only: String = String(_args.get("only", ""))
	var holder := Control.new()
	holder.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	get_tree().root.add_child(holder)
	var menu: Control = CHOICE.instantiate()
	menu.anchor_left = 0.1          # as GameEngine places it
	menu.anchor_right = 0.9
	menu.anchor_top = 0.15
	menu.anchor_bottom = 0.85
	holder.add_child(menu)
	await get_tree().process_frame
	var n_choices: int = 0
	var scrolled: int = 0
	var two_col: int = 0
	for path: String in _scene_files():
		var txt: String = FileAccess.get_file_as_string(path)
		var data_v: Variant = JSON.parse_string(txt)
		if not (data_v is Dictionary):
			continue
		var data: Dictionary = data_v
		var scene_id: String = path.get_file().get_basename()
		if only != "" and scene_id != only:
			continue
		var nodes: Array = data.get("nodes", [])
		for ni in nodes.size():
			if not (nodes[ni] is Dictionary):
				continue
			var n: Dictionary = nodes[ni]
			if String(n.get("t", "")) != "choice":
				continue
			var opts: Array = n.get("opts", [])
			if opts.is_empty():
				continue
			n_choices += 1
			var where: String = "%s:%d (%d options)" % [scene_id, ni, opts.size()]
			menu.call("setup", SkinDB.get_for_vol(int(data.get("vol", 1))))
			_picked = -1
			menu.call("present", String(n.get("prompt", "")), opts,
				func(idx: int) -> void: _picked = idx,
				String(n.get("style", "")), String(n.get("hotspot", "")))
			for i in 4:
				await get_tree().process_frame
			var col: Control = menu.get("_column")
			var grid: Container = menu.get("_vbox")
			var scroll: ScrollContainer = menu.get("_scroll")      # null in the menu as it was before the fix
			var cr: Rect2 = col.get_global_rect()
			if not screen.grow(1.0).encloses(cr):
				_flag("%s: the column %s is not inside the screen %s" % [where, cr, screen])
			var win: Rect2 = scroll.get_global_rect() if scroll != null else screen
			var scrolls: bool = scroll != null and grid.size.y > win.size.y + 1.0
			var cols: int = int(grid.get("columns")) if grid is GridContainer else 1
			if scrolls:
				scrolled += 1
			if cols > 1:
				two_col += 1
			if opts.size() >= 6 or scrolls:
				print("  %s → %d column(s), %s" % [where, cols, "scrolls" if scrolls else "all on screen"])
			for bi in grid.get_child_count():
				var b: Control = grid.get_child(bi) as Control
				if not scrolls and not win.grow(1.0).encloses(b.get_global_rect()):
					_flag("%s: option %d %s is outside the list %s" % [where, bi + 1, b.get_global_rect(), win])
			for target: int in [0, grid.get_child_count() - 1]:
				var btn: Control = grid.get_child(target) as Control
				if scroll != null:
					scroll.ensure_control_visible(btn)
				for i in 3:
					await get_tree().process_frame
				var br: Rect2 = btn.get_global_rect().intersection(win).intersection(screen)
				if br.size.y < 6.0 or br.size.x < 6.0:
					_flag("%s: option %d cannot be brought on screen" % [where, target + 1])
					continue
				_picked = -1
				await _click(br.get_center())
				for i in 2:
					await get_tree().process_frame
				if _picked != target:
					_flag("%s: clicked option %d and got %d" % [where, target + 1, _picked])
	print("[VnChoiceProbe] %d choice(s) · %d in two columns · %d that scroll · %d finding(s)" % [n_choices, two_col, scrolled, _bad])
	get_tree().quit(1 if _bad > 0 else 0)
