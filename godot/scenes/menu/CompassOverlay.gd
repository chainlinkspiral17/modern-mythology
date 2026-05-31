extends Control
## CompassOverlay — the NARRATIVE STRUCTURE COMPASS / RUST_CODE.BBS.
##
## Cross-volume navigation map. Two display modes:
##   • "full"     — full-screen, used from MainMenu
##   • "top_half" — anchored to the top half of the viewport, used
##                  from the in-game GUI so the dialog box stays
##                  readable below
##
## Layout: vol5 sits at the center as a 22-position major-arcana
## wheel; other volumes orbit as smaller cluster nodes around the
## edges. Click any node → emits scene_selected(scene_id). Closing
## emits closed.
##
## Visual treatment is intentionally placeholder right now — solid
## color discs with labels — pending the user's concept art for the
## final compass rose styling. The data model + interaction layer
## are real; the chrome swaps in later.

signal scene_selected(scene_id: String)
signal closed

const C_BG          := Color(0.02, 0.012, 0.018, 0.94)
const C_INK         := Color(0.06, 0.04, 0.06, 0.85)
const C_RULE        := Color(0.33, 0.20, 0.094)
const C_GOLD        := Color(0.85, 0.63, 0.38)
const C_GOLD_HI     := Color(1.0,  0.85, 0.59)
const C_NODE_LOCK   := Color(0.18, 0.14, 0.12)
const C_NODE_AVAIL  := Color(0.55, 0.38, 0.18)
const C_NODE_VISIT  := Color(0.82, 0.55, 0.22)
const C_NODE_CURR   := Color(1.0,  0.85, 0.40)
const C_EDGE_DIM    := Color(0.30, 0.22, 0.12, 0.55)
const C_EDGE_HOT    := Color(1.0,  0.78, 0.30, 0.85)
const C_TEXT        := Color(0.85, 0.72, 0.50)
const C_TEXT_DIM    := Color(0.52, 0.40, 0.22)

# Two-tier unlock:
#   MainMenu access  — TESTING_ALWAYS_MENU_UNLOCKED is on per user
#                      direction (visible immediately for testing).
#                      Production: gated by "compass:menu_unlocked"
#                      which fires when player solves the unlock
#                      puzzle (priestess badge click / 3x BBS).
#
#   In-game access   — ALWAYS gated by a puzzle solve. The in-game
#                      compass is the AGENT of transition between
#                      chapters / scenes / puzzles / elements —
#                      not a free-toggle overlay. Even in testing
#                      it only opens at transition moments, never
#                      mid-scene.
const TESTING_ALWAYS_MENU_UNLOCKED := true
const COMPASS_MENU_FLAG    := "compass:menu_unlocked"
const COMPASS_INGAME_FLAG  := "compass:ingame_unlocked"

# Major arcana per vol5 chapter (0..21 around the wheel)
const VOL5_ARCANA_ORDER := [
    ["vol5_ch0_booth6",        "0",    "FOOL",         "fool"],
    ["vol5_ch1_magician",      "I",    "MAGICIAN",     "magician"],
    ["vol5_ch2_priestess",     "II",   "PRIESTESS",    "high_priestess"],
    ["vol5_ch3_empress",       "III",  "EMPRESS",      "empress"],
    ["vol5_ch4_emperor",       "IV",   "EMPEROR",      "emperor"],
    ["vol5_ch5_hierophant",    "V",    "HIEROPHANT",   "hierophant"],
    ["vol5_ch6_lovers",        "VI",   "LOVERS",       ""],
    ["vol5_ch7_chariot",       "VII",  "CHARIOT",      ""],
    ["vol5_ch8_strength",      "VIII", "STRENGTH",     ""],
    ["vol5_ch9_hermit",        "IX",   "HERMIT",       ""],
    ["vol5_ch10_wheel",        "X",    "WHEEL",        ""],
    ["vol5_ch11_justice",      "XI",   "JUSTICE",      ""],
    ["vol5_ch12_hanged",       "XII",  "HANGED",       ""],
    ["vol5_ch13_death",        "XIII", "DEATH",        ""],
    ["vol5_ch14_temperance",   "XIV",  "TEMPERANCE",   ""],
    ["vol5_ch15_devil",        "XV",   "DEVIL",        ""],
    ["vol5_ch16_tower",        "XVI",  "TOWER",        ""],
    ["vol5_ch17_star",         "XVII", "STAR",         ""],
    ["vol5_ch18_moon",         "XVIII","MOON",         ""],
    ["vol5_ch19_sun",          "XIX",  "SUN",          ""],
    ["vol5_ch20_judgement",    "XX",   "JUDGEMENT",    ""],
    ["vol5_ch21_world",        "XXI",  "WORLD",        ""],
]

# Vol cluster positions (centered on viewport, normalized x/y)
const CLUSTER_POSITIONS := {
    1: Vector2(0.13, 0.18),    # top-left
    2: Vector2(0.85, 0.18),    # top-right
    3: Vector2(0.92, 0.42),    # right
    4: Vector2(0.92, 0.66),    # bottom-right
    5: Vector2(0.50, 0.50),    # CENTER — vol5 wheel
    6: Vector2(0.08, 0.66),    # bottom-left
    7: Vector2(0.08, 0.42),    # left
}

var display_mode: String = "full"
var current_scene_id: String = ""

var _nodes_by_scene: Dictionary = {}    # scene_id -> Dictionary {pos, vol, btn}
var _scenes_per_vol: Dictionary = {}    # vol -> Array[scene_id]
var _close_btn: Button
var _title_label: Label
var _hint_label: Label
var _canvas: Control


func _ready() -> void:
    mouse_filter = Control.MOUSE_FILTER_STOP
    _apply_display_mode()
    _load_scene_index()
    _build_ui()
    set_process_input(true)


func _apply_display_mode() -> void:
    if display_mode == "top_half":
        anchor_left = 0; anchor_right = 1
        anchor_top = 0;  anchor_bottom = 0.5
        offset_left = 0; offset_right = 0
        offset_top = 0;  offset_bottom = 0
    else:
        set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


func _load_scene_index() -> void:
    var path := "res://resources/scenes/index.json"
    if not FileAccess.file_exists(path):
        push_warning("CompassOverlay: scenes/index.json missing")
        return
    var f := FileAccess.open(path, FileAccess.READ)
    var data: Dictionary = JSON.parse_string(f.get_as_text())
    f.close()
    for vol_key in data.keys():
        var vol := int(vol_key)
        _scenes_per_vol[vol] = data[vol_key]


func _build_ui() -> void:
    # Backdrop
    var bg := ColorRect.new()
    bg.color = C_BG
    bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    bg.mouse_filter = Control.MOUSE_FILTER_STOP
    add_child(bg)

    # Header strip
    var header := HBoxContainer.new()
    header.add_theme_constant_override("separation", 12)
    header.offset_left = 14; header.offset_top = 10
    header.offset_right = -14; header.offset_bottom = 36
    header.anchor_right = 1
    add_child(header)

    _title_label = Label.new()
    _title_label.text = "NARRATIVE STRUCTURE COMPASS"
    _title_label.add_theme_color_override("font_color", C_GOLD_HI)
    _title_label.add_theme_font_size_override("font_size", 16)
    header.add_child(_title_label)

    var sub := Label.new()
    sub.text = "RUST_CODE.BBS · ACTIVE NODES: 64"
    sub.add_theme_color_override("font_color", C_TEXT_DIM)
    sub.add_theme_font_size_override("font_size", 11)
    sub.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    header.add_child(sub)

    _hint_label = Label.new()
    _hint_label.text = "[ click node to enter · ESC to close ]"
    _hint_label.add_theme_color_override("font_color", C_TEXT_DIM)
    _hint_label.add_theme_font_size_override("font_size", 10)
    header.add_child(_hint_label)

    _close_btn = Button.new()
    _close_btn.text = "X"
    _close_btn.add_theme_color_override("font_color", C_GOLD_HI)
    _close_btn.custom_minimum_size = Vector2(30, 24)
    _close_btn.pressed.connect(func() -> void: closed.emit())
    header.add_child(_close_btn)

    # Compass canvas — uses _draw for the connecting edges + radial lines
    _canvas = Control.new()
    _canvas.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    _canvas.offset_top = 40
    _canvas.mouse_filter = Control.MOUSE_FILTER_IGNORE
    _canvas.set_script(GDScript.new())
    add_child(_canvas)
    _canvas.draw.connect(_draw_compass)
    _canvas.resized.connect(func() -> void: _canvas.queue_redraw(); _layout_nodes())

    # Build vol5 arcana wheel + other volumes as clusters
    _build_vol5_wheel()
    _build_other_clusters()
    _layout_nodes()


func _build_vol5_wheel() -> void:
    for i in VOL5_ARCANA_ORDER.size():
        var entry = VOL5_ARCANA_ORDER[i]
        var scene_id = entry[0]
        var roman    = entry[1]
        var name     = entry[2]
        var art      = entry[3]
        var btn := _make_node_button(scene_id, "%s\n%s" % [roman, name],
                                      art != "")
        # store metadata
        _nodes_by_scene[scene_id] = {
            "btn": btn,
            "vol": 5,
            "arcana_idx": i,
            "kind": "vol5_wheel",
            "art_id": art,
        }
        add_child(btn)


func _build_other_clusters() -> void:
    for vol in [1, 2, 3, 4, 6, 7]:
        if not _scenes_per_vol.has(vol): continue
        var scenes: Array = _scenes_per_vol[vol]
        # For each volume, make a single cluster head + show count.
        # Sub-compass per volume is a future pass once each volume's
        # internal structure firms up.
        var head_btn := _make_node_button(
            "_cluster_vol%d" % vol,
            "VOL %d\n%d nodes" % [vol, scenes.size()],
            true)
        _nodes_by_scene["_cluster_vol%d" % vol] = {
            "btn": head_btn,
            "vol": vol,
            "kind": "cluster_head",
            "scenes": scenes,
        }
        add_child(head_btn)


func _make_node_button(scene_id: String, label_text: String,
                        is_available: bool) -> Button:
    var btn := Button.new()
    btn.text = label_text
    btn.custom_minimum_size = Vector2(56, 56)
    btn.add_theme_color_override("font_color", C_GOLD_HI if is_available else C_TEXT_DIM)
    btn.add_theme_font_size_override("font_size", 9)
    btn.disabled = not is_available
    btn.clip_text = true
    # styling
    var sb := StyleBoxFlat.new()
    sb.bg_color = C_NODE_AVAIL if is_available else C_NODE_LOCK
    sb.border_color = C_GOLD if is_available else C_RULE
    sb.set_border_width_all(1)
    sb.corner_radius_top_left = 28
    sb.corner_radius_top_right = 28
    sb.corner_radius_bottom_left = 28
    sb.corner_radius_bottom_right = 28
    btn.add_theme_stylebox_override("normal", sb)
    var hover := sb.duplicate() as StyleBoxFlat
    hover.bg_color = C_NODE_VISIT
    hover.border_color = C_GOLD_HI
    btn.add_theme_stylebox_override("hover", hover)
    btn.add_theme_stylebox_override("focus", hover)
    if is_available:
        var captured_id := scene_id
        btn.pressed.connect(func() -> void: _on_node_pressed(captured_id))
    return btn


func _layout_nodes() -> void:
    var view := _canvas.size
    if view.x <= 0 or view.y <= 0:
        await get_tree().process_frame
        view = _canvas.size
        if view.x <= 0 or view.y <= 0:
            return

    # Center vol5 wheel
    var center := view * 0.5
    var radius := minf(view.x, view.y) * 0.32

    for scene_id in _nodes_by_scene.keys():
        var meta: Dictionary = _nodes_by_scene[scene_id]
        var btn: Button = meta["btn"]
        var node_size := btn.custom_minimum_size
        var pos: Vector2
        if meta["kind"] == "vol5_wheel":
            var i: int = meta["arcana_idx"]
            var theta = -PI/2 + (float(i) / VOL5_ARCANA_ORDER.size()) * TAU
            pos = center + Vector2(cos(theta), sin(theta)) * radius
        else:
            var vol: int = meta["vol"]
            var npos: Vector2 = CLUSTER_POSITIONS.get(vol, Vector2(0.5, 0.5))
            pos = Vector2(npos.x * view.x, npos.y * view.y)
        # center the button on the position
        btn.position = pos - node_size * 0.5

    _canvas.queue_redraw()


func _draw_compass() -> void:
    var view := _canvas.size
    var center := view * 0.5
    var radius := minf(view.x, view.y) * 0.32

    # outer rule ring
    _canvas.draw_arc(center, radius + 12, 0, TAU, 96, C_GOLD, 1.0, true)
    _canvas.draw_arc(center, radius - 16, 0, TAU, 96, C_EDGE_DIM, 1.0, true)
    # cardinal tick marks (N E S W)
    for tick in 4:
        var theta = -PI/2 + tick * PI/2
        var inner = center + Vector2(cos(theta), sin(theta)) * (radius - 22)
        var outer = center + Vector2(cos(theta), sin(theta)) * (radius + 18)
        _canvas.draw_line(inner, outer, C_GOLD, 1.0)

    # radial spokes to vol5 nodes
    for i in VOL5_ARCANA_ORDER.size():
        var theta = -PI/2 + (float(i) / VOL5_ARCANA_ORDER.size()) * TAU
        var inner = center + Vector2(cos(theta), sin(theta)) * (radius - 14)
        var outer = center + Vector2(cos(theta), sin(theta)) * radius
        _canvas.draw_line(inner, outer, C_EDGE_DIM, 1.0)

    # cluster-to-center threads (cross-volume connective tissue —
    # placeholder: dim line from each cluster head into the wheel)
    for vol in [1, 2, 3, 4, 6, 7]:
        var key := "_cluster_vol%d" % vol
        if not _nodes_by_scene.has(key): continue
        var btn: Button = _nodes_by_scene[key]["btn"]
        var cluster_pos := btn.position + btn.custom_minimum_size * 0.5
        # draw dotted line via dashed segments
        var to_center = center - cluster_pos
        var steps = int(to_center.length() / 14.0)
        for s in steps:
            if s % 2 == 0:
                var a = cluster_pos + to_center * (float(s) / steps)
                var b = cluster_pos + to_center * (float(s + 1) / steps)
                _canvas.draw_line(a, b, C_EDGE_DIM, 1.0)

    # center mark — the compass rose origin
    _canvas.draw_circle(center, 4, C_GOLD_HI)
    _canvas.draw_arc(center, 8, 0, TAU, 24, C_GOLD, 1.0, true)


func _on_node_pressed(scene_id: String) -> void:
    if scene_id.begins_with("_cluster_vol"):
        # placeholder — future: zoom into the volume sub-compass
        var vol = int(scene_id.replace("_cluster_vol", ""))
        _title_label.text = "VOL %d — sub-compass TODO" % vol
        return
    scene_selected.emit(scene_id)


func _input(event: InputEvent) -> void:
    if not visible: return
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_ESCAPE:
            closed.emit()
            get_viewport().set_input_as_handled()


# ── Public API ────────────────────────────────────────────────────
func open(mode: String = "full", at_scene: String = "") -> void:
    display_mode = mode
    current_scene_id = at_scene
    _apply_display_mode()
    visible = true
    if _canvas != null:
        await get_tree().process_frame
        _layout_nodes()


func close() -> void:
    visible = false


## Visible in MainMenu (test mode flips this on; production requires
## the unlock puzzle).
static func is_menu_unlocked() -> bool:
    if TESTING_ALWAYS_MENU_UNLOCKED: return true
    return SaveSystem.is_unlocked(COMPASS_MENU_FLAG)


## Available as the in-game navigation agent. Strictly puzzle-gated;
## no test override. The caller is ALSO responsible for only invoking
## this at valid transition points (scene end / chapter end / puzzle
## complete / element finished) — the compass is the transition agent
## itself, not a free-toggle pause overlay.
static func is_ingame_unlocked() -> bool:
    return SaveSystem.is_unlocked(COMPASS_INGAME_FLAG)


## Call once when the player solves the in-game unlock puzzle.
static func unlock_for_ingame() -> void:
    SaveSystem.mark_unlocked(COMPASS_INGAME_FLAG)
    SaveSystem.mark_unlocked(COMPASS_MENU_FLAG)


## Valid transition contexts — call sites pass one of these when
## opening the compass in-game so we can audit/log invalid invokes.
enum InGameContext {
    SCENE_END,
    CHAPTER_END,
    PUZZLE_SOLVED,
    ELEMENT_COMPLETED,
}
